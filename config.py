"""
Configurações da aplicação RAG com FAISS local
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações da API
API_TITLE = "Document Search API"
API_DESCRIPTION = "API para carregar e pesquisar documentos usando embeddings de IA generativa com FAISS local."
API_VERSION = "0.1.0"

# Configurações do Google AI
GOOGLE_EMBEDDING_MODEL = "models/embedding-001"

def get_google_api_key():
    """Obtém a chave da API do Google das variáveis de ambiente"""
    return os.getenv("GOOGLE_API_KEY")

# Configurações de diretórios
DATA_DIR = "data"
FAISS_INDEX_DIR = os.path.join(DATA_DIR, "faiss_indexes")
CHAT_HISTORY_DIR = os.path.join(DATA_DIR, "chat_history")

# Configurações do FAISS
FAISS_COLLECTIONS = {
    "documents": "my_docs",
    "chat_history": "chat_history"
}

# Configurações de busca
DEFAULT_SEARCH_K = 10
CHAT_HISTORY_SEARCH_K = 3

# Configurações de CORS
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# Validação de configuração
def validate_config():
    """Valida se todas as configurações necessárias estão presentes"""
    if not get_google_api_key():
        raise ValueError(
            "GOOGLE_API_KEY não encontrado. "
            "Configure a variável GOOGLE_API_KEY no arquivo .env"
        )
    
    # Criar diretórios se não existirem
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
    
    return True
