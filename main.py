from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import tempfile
import time
import os
from utils import (
    clean_text_data, save_faiss_index, load_faiss_index, 
    save_chat_history, get_chat_history, get_all_chat_ids, 
    clear_chat_history
)
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import create_retrieval_chain
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from ia import llm_google
from config import (
    API_TITLE, API_DESCRIPTION, API_VERSION, get_google_api_key,
    GOOGLE_EMBEDDING_MODEL, CORS_ORIGINS, CORS_CREDENTIALS,
    CORS_METHODS, CORS_HEADERS, DEFAULT_SEARCH_K, CHAT_HISTORY_SEARCH_K,
    validate_config
)
import uvicorn

# Validar configuração
validate_config()

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

if not get_google_api_key():
    raise HTTPException(status_code=500, detail="Google API key não encontrado. Configure a variável GOOGLE_API_KEY.")

embeddings = GoogleGenerativeAIEmbeddings(model=GOOGLE_EMBEDDING_MODEL)

# Carregar ou criar índices FAISS locais
def get_or_create_faiss_index(collection_name: str):
    """Carrega um índice FAISS existente ou cria um novo"""
    index = load_faiss_index(collection_name)
    if index is None:
        # Criar novo índice vazio
        index = FAISS.from_texts(["placeholder"], embeddings, metadatas=[{"placeholder": True}])
        # Remover o placeholder
        index.delete([index.index_to_docstore_id[0]])
        save_faiss_index(index, collection_name)
    return index

# Inicializar índices FAISS
db = get_or_create_faiss_index("my_docs")
chat_history_db = get_or_create_faiss_index("chat_history")

class QueryRequest(BaseModel):
    query: str
    chat_id: str

@app.post("/upload",
          summary="Carregar um documento para a base de dados do FAISS local",
          description="Carregar um documento para a base de dados do FAISS local para ser pesquisado posteriormente.",
          response_description="Mensagem indicando sucesso ou falha."
          )
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Somente arquivos PDF são permitidos.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(await file.read())
            tmp_file_path = tmp_file.name

        loader = PyPDFLoader(tmp_file_path)
        pages = loader.load_and_split()
        os.remove(tmp_file_path)

        if not pages:
            raise HTTPException(status_code=400, detail="O documento está vazio. Tente novamente com outro arquivo.")

        documents = [
            Document(
                page_content=clean_text_data(page.page_content),
                metadata={
                    "page_number": idx + 1,
                    "file_name": file.filename
                }
            )
            for idx, page in enumerate(pages)
        ]

        # Adicionar documentos ao índice FAISS
        db.add_documents(documents)
        
        # Salvar índice atualizado
        save_faiss_index(db, "my_docs")

        return {"message": "Documento carregado com sucesso com metadados."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {str(e)}")

@app.post("/query")
async def query_document(request: QueryRequest):
    start_time = time.time()

    try:
        # Realizar busca de similaridade
        results = db.similarity_search_with_score(request.query, k=DEFAULT_SEARCH_K)

        files = [result[0].metadata["file_name"] for result in results]
        pages = [result[0].metadata["page_number"] for result in results]
        vectors = [result[1] for result in results]

        print(f"Documentos: {files} - Páginas: {pages}")
        print(f"Vetores das respostas mais próximas: {vectors}")
        if results:
            print(f"Documentos próximos: {results[0][0].page_content}")

        context = ""
        for doc, score in results:
            context += f"Arquivo: {doc.metadata['file_name']}\nPágina: {doc.metadata['page_number']}\nTexto: {doc.page_content}\n\n"

        # Buscar histórico de chat usando FAISS
        history = ""
        if chat_history_db.index.ntotal > 0:  # Verificar se o índice não está vazio
            conversation_history = chat_history_db.similarity_search_with_score(
                request.query, k=CHAT_HISTORY_SEARCH_K
            )
            for history_doc, score in conversation_history:
                if "user" in history_doc.metadata and "ai" in history_doc.metadata:
                    history += f"Usuário: {history_doc.metadata['user']}\nIA: {history_doc.metadata['ai']}\n\n"

        template = """
            Você é um assistente cordial e especializado em contratos.

            Sua tarefa é usar:
            - Um parágrafo de contexto ({context}) com informações relevantes sobre contratos
            - A pergunta feita pelo usuário ({input})
            - O histórico da conversa anterior ({history})

            Instruções:

            1. Leia com atenção o contexto ({context}) e identifique as informações mais úteis sobre o contrato.

            2. Verifique o histórico ({history}) para encontrar algo que complemente a resposta.

            3. Elabore uma resposta clara, objetiva e educada. Seja direto e vá ao ponto, sem rodeios desnecessários.

            4. **Só cumprimente o usuário (ex: "Olá", "Oi", "Bom dia") se ele iniciar a pergunta com esse tipo de saudação.** Caso contrário, não cumprimente — apenas responda de forma direta e respeitosa.

            5. Se não for possível responder com as informações disponíveis, diga isso de forma educada, explicando que os dados não estão disponíveis ou que precisa de mais detalhes.

            Atenção:
            - Use apenas o conteúdo do contexto e histórico.
            - Não invente informações.
            - Nunca utilize conhecimento externo.

            Agora, responda à pergunta com base apenas no que foi fornecido.
        """

        prompt = PromptTemplate.from_template(template)

        combine_docs_chain = create_stuff_documents_chain(llm_google(), prompt)
        retriever = db.as_retriever(
            search_kwargs={"k": DEFAULT_SEARCH_K}
        )
        retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

        response = retrieval_chain.invoke({"input": request.query, "context": context, "history": history})
        print(f"Resposta: {response['answer']}")

        # Salvar histórico de chat localmente
        save_chat_history(request.chat_id, request.query, response['answer'])
        
        # Também adicionar ao índice FAISS para busca semântica
        chat_history_doc = Document(
            page_content=f"Usuário: {request.query}\nIA: {response['answer']}",
            metadata={"chat_id": request.chat_id, "user": request.query, "ai": response['answer'], "timestamp": datetime.now().isoformat()}
        )
        chat_history_db.add_documents([chat_history_doc])
        save_faiss_index(chat_history_db, "chat_history")

        print(f"Tempo: {time.time() - start_time} segundos")
        return {"answer": response['answer']}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@app.get("/history/{chat_id}")
async def get_chat_history_endpoint(chat_id: str):
    try:
        history = get_chat_history(chat_id)
        history_sorted = sorted(history, key=lambda x: x["timestamp"])
        return {"history": history_sorted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@app.get("/all_chat_ids")
def list_all_chats():
    try:
        chat_ids = get_all_chat_ids()
        return {"chat_ids": chat_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@app.delete("/history/{chat_id}")
async def clear_chat_history_endpoint(chat_id: str):
    try:
        # Limpar histórico local
        clear_chat_history(chat_id)
        
        # Recriar índice FAISS sem o histórico deste chat
        # Esta é uma implementação simplificada - em produção você pode querer uma abordagem mais sofisticada
        new_chat_history_db = get_or_create_faiss_index("chat_history")
        save_faiss_index(new_chat_history_db, "chat_history")
        
        return {"message": f"Histórico do chat {chat_id} limpo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@app.get("/documents")
async def list_all_document_names():
    try:
        # Buscar todos os documentos no índice FAISS
        results = db.similarity_search_with_score("contrato", k=1000)
        file_names = sorted({doc.metadata["file_name"] for doc, score in results})
        return {"file_names": file_names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@app.delete("/documents/{file_name}")
async def delete_document(file_name: str):
    try:
        # Buscar documentos com o nome do arquivo
        results = db.similarity_search_with_score(file_name, k=1000)
        documents_to_delete = [doc for doc, score in results if doc.metadata["file_name"] == file_name]
        
        if documents_to_delete:
            # Recriar índice sem os documentos deletados
            remaining_docs = [doc for doc, score in results if doc.metadata["file_name"] != file_name]
            
            if remaining_docs:
                new_db = FAISS.from_documents(remaining_docs, embeddings)
            else:
                new_db = get_or_create_faiss_index("my_docs")
            
            save_faiss_index(new_db, "my_docs")
            # Atualizar a referência global
            globals()['db'] = new_db
            
        return {"message": f"Arquivo {file_name} deletado."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
