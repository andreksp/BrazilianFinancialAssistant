# Agent: Phase 0 — Infraestrutura Base

**Responsabilidade**: Preparar ambiente para desenvolvimento  
**Duração**: 1-2 dias  
**Output**: Servidor FastAPI rodando com health endpoint  

---

## Conhecimento de Negócio

### Estrutura de Pastas
Organização monorepo com backend Python e frontend Angular:
```
backend/          — FastAPI + cálculos + LLM
  app/
    api/          — Rotas REST
    calculations/ — Motores de cálculo (impostos, taxas)
    llm/          — Integração Claude
    models/       — Pydantic models
frontend/         — Angular 17
  src/
    app/
      components/ — Chat, trade-input, results
      services/   — API client
```

### Configuração de Ambiente
- **Python**: 3.11+ (type hints forte, async nativo)
- **Package Manager**: Poetry (lockfile reproducível)
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **LLM**: Claude Haiku (parsing) + Sonnet (explicações)
- **Vector DB**: ChromaDB (busca semântica de regulamentações)

### Variáveis de Ambiente Críticas
```
ANTHROPIC_API_KEY       # Necessário para LLM
DATABASE_URL            # sqlite:// ou postgresql://
FRONTEND_URL            # http://localhost:4200 (dev)
CHROMA_DB_PATH          # ./chroma_data
DEBUG                   # True (dev) / False (prod)
```

---

## Tarefas

### 1. Criar Estrutura de Pastas
- [x] `/backend/app/` com subpastas:
  - api/, calculations/, llm/, models/, vector_db/, storage/
- [x] `/frontend/src/app/` com subpastas:
  - components/, services/, models/
- [x] `/backend/tests/`
- [x] `/backend/data/regulations/`

### 2. Configuração Poetry
**Arquivo**: `backend/pyproject.toml`

Dependências críticas:
- **fastapi** — Web framework
- **uvicorn** — ASGI server
- **pydantic** — Data validation
- **sqlalchemy** — ORM
- **chromadb** — Vector database
- **anthropic** — Claude API SDK
- **python-dotenv** — Environment variables

**Business Logic**: 
- FastAPI oferece OpenAPI auto-docs para contrato de API
- Pydantic força validação de tipos (importante para cálculos financeiros)
- SQLAlchemy permite abstract tanto SQLite (dev) quanto PostgreSQL (prod)

### 3. Configuração de Ambiente
**Arquivo**: `.env.example`

Chaves necessárias:
```
ANTHROPIC_API_KEY=seu_token_anthropic
DATABASE_URL=sqlite:///./app.db
FRONTEND_URL=http://localhost:4200
CHROMA_DB_PATH=./chroma_data
DEBUG=True
```

**Business Logic**:
- ANTHROPIC_API_KEY: Necessário para parsing de trades em linguagem natural
- DATABASE_URL: Suporta dev (SQLite) e prod (PostgreSQL) sem mudança de código
- CHROMA_DB_PATH: Persistência de embeddings de regulamentações

### 4. FastAPI Entry Point
**Arquivo**: `backend/app/main.py`

Estrutura:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Brazilian Financial Assistant")

# CORS para localhost:4200 (Angular dev)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:4200"])

# Lifespan: inicializar ChromaDB, conectar DB
@asynccontextmanager
async def lifespan(app):
    # Startup: carregar regulamentações
    yield
    # Shutdown: fechar conexões
```

**Business Logic**:
- CORS **obrigatório** para Angular chamar FastAPI em localhost
- Lifespan para inicializar recursos externos (ChromaDB, banco de dados)

### 5. Health Check Endpoint
**Rota**: `GET /health`

Response:
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

**Business Logic**:
- Usado por Docker health checks
- Monitoramento em produção
- Detecta falhas de inicialização

### 6. Settings/Config
**Arquivo**: `backend/app/core/config.py`

Usa `pydantic-settings` para ler `.env`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    DATABASE_URL: str = "sqlite:///./app.db"
    FRONTEND_URL: str = "http://localhost:4200"
    ...
```

**Business Logic**:
- Lê do `.env` automaticamente
- Type-safe (TypeError se tipo errado)
- Fallbacks sensatos para dev

### 7. Teste Local
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload

# Verificar:
# curl http://localhost:8000/health
# http://localhost:8000/docs (OpenAPI)
```

---

## Validação (Checklist)

- [ ] Estrutura de pastas criada
- [ ] `poetry.lock` gerado (dependências instaladas)
- [ ] `.env` criado a partir de `.env.example`
- [ ] `uvicorn app.main:app --reload` roda sem erro
- [ ] `GET /health` retorna `{"status": "ok"}`
- [ ] `GET /docs` carrega OpenAPI UI (swagger)

---

## Notas

- **Phase 0 é bloqueante**: Sem isso, Phase 1 não pode iniciar
- **Poetry vs pip**: Preferir Poetry por reproducibilidade (lockfile)
- **Debug=True em dev**: Ativa reloading automático (hot-reload)
- **CORS local**: Necessário para Angular dev server em 4200
