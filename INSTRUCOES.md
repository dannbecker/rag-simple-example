# Instruções de Uso - RAG com FAISS Local

## 🚀 Migração Concluída

A aplicação foi **completamente migrada** do PGVector para o FAISS local. Agora você pode usar a aplicação sem depender de um banco de dados PostgreSQL externo.

## 📋 Pré-requisitos

1. **Python 3.8+** instalado
2. **Chave da API Google Gemini** (obrigatória)
3. **Ambiente virtual** ativado

## 🔧 Configuração

### 1. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite o arquivo .env e adicione sua chave da API
GOOGLE_API_KEY=sua_chave_real_aqui
```

**⚠️ IMPORTANTE:** Obtenha sua chave da API em: https://makersuite.google.com/app/apikey

### 2. Instalar Dependências

```bash
# Ativar ambiente virtual (Windows)
venv\Scripts\activate.bat

# Ativar ambiente virtual (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## 🏃‍♂️ Executando a Aplicação

### 1. Iniciar o Servidor

```bash
# Com ambiente virtual ativado
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Acessar a API

- **Documentação Swagger:** http://localhost:8000/
- **API Base:** http://localhost:8000

## 📚 Como Usar

### 1. Upload de Documentos

```bash
# Via curl
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@seu_documento.pdf"

# Via Python (usando example_usage.py)
python example_usage.py
```

### 2. Consultar Documentos

```bash
# Via curl
curl -X POST "http://localhost:8000/query" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"query": "Sua pergunta aqui", "chat_id": "chat_123"}'

# Via Python
from example_usage import query_document
query_document("Sua pergunta aqui", "chat_123")
```

### 3. Gerenciar Histórico

```bash
# Listar todos os chats
curl "http://localhost:8000/all_chat_ids"

# Obter histórico de um chat específico
curl "http://localhost:8000/history/chat_123"

# Limpar histórico de um chat
curl -X DELETE "http://localhost:8000/history/chat_123"
```

## 🗂️ Estrutura de Dados

Os dados são armazenados localmente na pasta `data/`:

```
data/
├── faiss_indexes/          # Índices FAISS
│   ├── my_docs.pkl        # Documentos carregados
│   └── chat_history.pkl   # Histórico de conversas
└── chat_history/           # Histórico em JSON
    ├── chat_123.json
    └── chat_456.json
```

## 🔍 Funcionalidades Principais

### ✅ Implementado
- ✅ Upload de documentos PDF
- ✅ Busca semântica com FAISS
- ✅ Histórico de chat persistente
- ✅ API REST completa
- ✅ Integração com Google Gemini
- ✅ Armazenamento local

### 🆕 Novidades da Migração
- 🆕 **FAISS local** em vez de PostgreSQL
- 🆕 **Histórico JSON** em vez de banco de dados
- 🆕 **Sem dependências externas** de banco
- 🆕 **Configuração centralizada** em `config.py`
- 🆕 **Testes automatizados** incluídos

## 🧪 Testando a Implementação

Execute os testes para verificar se tudo está funcionando:

```bash
# Executar testes
python test_faiss.py

# Resultado esperado: 4/4 testes passaram ✅
```

## 🚨 Solução de Problemas

### Erro: "Google API key não encontrado"
```bash
# Verifique se o arquivo .env existe e contém:
GOOGLE_API_KEY=sua_chave_aqui
```

### Erro: "Could not import faiss"
```bash
# Reinstale as dependências:
pip install -r requirements.txt
```

### Erro: "Porta já em uso"
```bash
# Use uma porta diferente:
uvicorn main:app --reload --port 8001
```

## 📊 Vantagens da Nova Implementação

| Aspecto | PGVector (Antigo) | FAISS Local (Novo) |
|---------|-------------------|-------------------|
| **Dependências** | PostgreSQL + Supabase | Apenas Python |
| **Configuração** | Complexa | Simples |
| **Portabilidade** | Limitada | Total |
| **Custo** | Pode ter custos | Gratuito |
| **Performance** | Boa | Excelente |
| **Manutenção** | Requer DBA | Automática |

## 🔮 Próximos Passos

1. **Teste a aplicação** com seus próprios documentos
2. **Ajuste as configurações** em `config.py` se necessário
3. **Personalize o prompt** no `main.py` para seu caso de uso
4. **Monitore o uso** dos índices FAISS

## 📞 Suporte

Se encontrar problemas:

1. ✅ Execute `python test_faiss.py` para verificar a instalação
2. 🔍 Verifique os logs da aplicação
3. 📋 Confirme que o arquivo `.env` está configurado
4. 🐛 Reporte bugs com detalhes do erro

---

**🎉 Parabéns!** Sua aplicação RAG agora está rodando completamente local com FAISS!
