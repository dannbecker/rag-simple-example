# RAG Simple Example com FAISS Local

Este é um exemplo simples de implementação RAG (Retrieval-Augmented Generation) usando FAISS local para armazenamento de vetores e arquivos JSON locais para histórico de chat.

## Características

- **FAISS Local**: Armazenamento de vetores local usando FAISS para busca de similaridade
- **Histórico Local**: Armazenamento de histórico de chat em arquivos JSON locais
- **API FastAPI**: Interface REST para upload e consulta de documentos
- **Google Gemini**: Integração com embeddings e LLM do Google
- **Processamento PDF**: Suporte para carregamento e processamento de documentos PDF

## Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd rag-simple-example
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
# Crie um arquivo .env com:
GOOGLE_API_KEY=sua_chave_api_google_aqui
```

## Uso

1. Inicie o servidor:
```bash
uvicorn main:app --reload
```

2. Acesse a documentação da API:
```
http://localhost:8000/
```

## Endpoints

- `POST /upload` - Upload de documentos PDF
- `POST /query` - Consulta de documentos
- `GET /history/{chat_id}` - Histórico de chat
- `GET /all_chat_ids` - Lista todos os IDs de chat
- `DELETE /history/{chat_id}` - Limpa histórico de chat
- `GET /documents` - Lista todos os documentos
- `DELETE /documents/{file_name}` - Remove documento

## Estrutura de Dados

Os dados são armazenados localmente na pasta `data/`:
- `data/faiss_indexes/` - Índices FAISS para documentos e histórico
- `data/chat_history/` - Arquivos JSON com histórico de chat

## Vantagens do FAISS Local

- **Sem dependências externas**: Não requer banco de dados PostgreSQL
- **Performance**: Busca de similaridade rápida e eficiente
- **Portabilidade**: Fácil de mover entre ambientes
- **Simplicidade**: Configuração mínima necessária

## Limitações

- **Persistência**: Dados são armazenados localmente (não compartilhados entre instâncias)
- **Escalabilidade**: Limitado ao armazenamento local
- **Backup**: Requer backup manual dos dados

## Tecnologias Utilizadas

- FastAPI
- FAISS (Facebook AI Similarity Search)
- LangChain
- Google Gemini AI
- PyPDF2