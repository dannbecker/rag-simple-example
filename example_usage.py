#!/usr/bin/env python3
"""
Exemplo de uso da API RAG com FAISS local
"""

import requests
import json
import uuid

# Configuração da API
API_BASE_URL = "http://localhost:8000"

def upload_document(file_path: str):
    """Upload de um documento PDF"""
    print(f"📤 Fazendo upload do documento: {file_path}")
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
    
    if response.status_code == 200:
        print("✅ Documento carregado com sucesso!")
        return response.json()
    else:
        print(f"❌ Erro no upload: {response.text}")
        return None

def query_document(query: str, chat_id: str):
    """Consulta de documentos"""
    print(f"🔍 Fazendo consulta: {query}")
    
    data = {
        "query": query,
        "chat_id": chat_id
    }
    
    response = requests.post(f"{API_BASE_URL}/query", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"🤖 Resposta da IA: {result['answer']}")
        return result
    else:
        print(f"❌ Erro na consulta: {response.text}")
        return None

def get_chat_history(chat_id: str):
    """Obtém o histórico de chat"""
    print(f"📚 Obtendo histórico do chat: {chat_id}")
    
    response = requests.get(f"{API_BASE_URL}/history/{chat_id}")
    
    if response.status_code == 200:
        history = response.json()
        print(f"📖 Histórico encontrado: {len(history['history'])} mensagens")
        return history
    else:
        print(f"❌ Erro ao obter histórico: {response.text}")
        return None

def list_documents():
    """Lista todos os documentos"""
    print("📋 Listando documentos disponíveis")
    
    response = requests.get(f"{API_BASE_URL}/documents")
    
    if response.status_code == 200:
        documents = response.json()
        print(f"📄 Documentos encontrados: {documents['file_names']}")
        return documents
    else:
        print(f"❌ Erro ao listar documentos: {response.text}")
        return None

def main():
    """Função principal de exemplo"""
    print("🚀 Exemplo de uso da API RAG com FAISS Local")
    print("=" * 50)
    
    # Gerar um ID único para o chat
    chat_id = str(uuid.uuid4())
    print(f"🆔 ID do chat: {chat_id}")
    
    # Listar documentos existentes
    list_documents()
    
    # Exemplo de consulta (sem upload prévio)
    print("\n" + "=" * 50)
    print("💬 Exemplo de consulta:")
    
    query = "O que é oftalmologia?"
    query_document(query, chat_id)
    
    # Obter histórico do chat
    print("\n" + "=" * 50)
    print("📚 Histórico do chat:")
    get_chat_history(chat_id)
    
    print("\n" + "=" * 50)
    print("✨ Exemplo concluído!")
    print("\nPara fazer upload de documentos, use:")
    print("upload_document('caminho/para/seu/arquivo.pdf')")
    print("\nPara consultas específicas, use:")
    print("query_document('sua pergunta aqui', chat_id)")

if __name__ == "__main__":
    main()
