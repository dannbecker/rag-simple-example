import json
import os
from typing import List, Dict, Any
from datetime import datetime
import pickle
from config import FAISS_INDEX_DIR, CHAT_HISTORY_DIR

def clean_text_data(text):
    """Limpa o texto removendo caracteres nulos e normalizando encoding"""
    if text is not None:
        return text.replace('\x00', '').encode('utf-8').decode('utf-8')
    return text

def save_faiss_index(index, filename: str):
    """Salva um índice FAISS no disco"""
    filepath = os.path.join(FAISS_INDEX_DIR, f"{filename}.pkl")
    with open(filepath, 'wb') as f:
        pickle.dump(index, f)

def load_faiss_index(filename: str):
    """Carrega um índice FAISS do disco"""
    filepath = os.path.join(FAISS_INDEX_DIR, f"{filename}.pkl")
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    return None

def save_chat_history(chat_id: str, user_message: str, ai_response: str):
    """Salva o histórico de chat em arquivo JSON local"""
    chat_file = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
    
    # Carregar histórico existente ou criar novo
    if os.path.exists(chat_file):
        with open(chat_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
    
    # Adicionar nova mensagem
    history.append({
        "user": user_message,
        "ai": ai_response,
        "timestamp": datetime.now().isoformat()
    })
    
    # Salvar histórico atualizado
    with open(chat_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_chat_history(chat_id: str) -> List[Dict[str, Any]]:
    """Carrega o histórico de chat de um arquivo JSON local"""
    chat_file = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
    
    if os.path.exists(chat_file):
        with open(chat_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_all_chat_ids() -> List[str]:
    """Retorna todos os IDs de chat disponíveis"""
    chat_ids = []
    for filename in os.listdir(CHAT_HISTORY_DIR):
        if filename.endswith('.json'):
            chat_id = filename.replace('.json', '')
            chat_ids.append(chat_id)
    return chat_ids

def clear_chat_history(chat_id: str) -> bool:
    """Remove o histórico de chat de um chat específico"""
    chat_file = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
    if os.path.exists(chat_file):
        os.remove(chat_file)
        return True
    return False

def get_document_names_from_faiss() -> List[str]:
    """Retorna os nomes dos documentos armazenados no FAISS"""
    # Esta função será implementada no main.py onde temos acesso ao índice FAISS
    pass