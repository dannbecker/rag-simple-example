#!/usr/bin/env python3
"""
Teste simples da implementação FAISS local
"""

import os
import sys
import tempfile

def test_imports():
    """Testa se todas as importações estão funcionando"""
    try:
        from config import validate_config
        from utils import clean_text_data, save_faiss_index, load_faiss_index
        from langchain_community.vectorstores import FAISS
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        print("✅ Todas as importações estão funcionando")
        return True
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False

def test_config():
    """Testa a configuração"""
    try:
        from config import validate_config
        # Simular ambiente sem API key para testar validação
        original_key = os.environ.get('GOOGLE_API_KEY')
        os.environ.pop('GOOGLE_API_KEY', None)
        
        try:
            validate_config()
            print("❌ Validação deveria ter falhado sem API key")
            return False
        except ValueError:
            print("✅ Validação de configuração funcionando")
        
        # Restaurar API key para outros testes
        if original_key:
            os.environ['GOOGLE_API_KEY'] = original_key
        else:
            os.environ['GOOGLE_API_KEY'] = 'test_key'
        return True
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def test_utils():
    """Testa as funções utilitárias"""
    try:
        from utils import clean_text_data
        
        # Teste de limpeza de texto
        test_text = "Texto com\x00caracteres nulos"
        cleaned = clean_text_data(test_text)
        if "\x00" not in cleaned:
            print("✅ Função clean_text_data funcionando")
        else:
            print("❌ Função clean_text_data não funcionou corretamente")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Erro nas funções utilitárias: {e}")
        return False

def test_faiss_basic():
    """Testa funcionalidade básica do FAISS"""
    try:
        from langchain_community.vectorstores import FAISS
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        
        # Criar embeddings mock para teste
        class MockEmbeddings:
            def embed_query(self, text):
                return [0.1, 0.2, 0.3]  # Vetor mock
            def embed_documents(self, texts):
                return [[0.1, 0.2, 0.3] for _ in texts]
        
        mock_embeddings = MockEmbeddings()
        
        # Teste básico do FAISS
        texts = ["Teste documento 1", "Teste documento 2"]
        metadatas = [{"id": 1}, {"id": 2}]
        
        faiss_index = FAISS.from_texts(texts, mock_embeddings, metadatas=metadatas)
        
        if hasattr(faiss_index, 'index') and faiss_index.index.ntotal > 0:
            print("✅ FAISS básico funcionando")
            return True
        else:
            print("❌ FAISS básico não funcionou")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste FAISS: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 Iniciando testes da implementação FAISS")
    print("=" * 50)
    
    tests = [
        ("Importações", test_imports),
        ("Configuração", test_config),
        ("Funções Utilitárias", test_utils),
        ("FAISS Básico", test_faiss_basic),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testando: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ Teste {test_name} falhou")
        except Exception as e:
            print(f"❌ Teste {test_name} falhou com exceção: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! A implementação FAISS está funcionando.")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
