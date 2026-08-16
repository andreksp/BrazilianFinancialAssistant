# Plano de Implementação — Brazilian Financial Assistant

**Data de Início**: 2026-04-27  
**Projeto**: TCC — Assistente Financeiro Inteligente para Mercado Brasileiro  
**Objetivo Primário**: Calcular impostos (IR), taxas, e valor líquido de operações de bolsa  

---

## Visão Geral do Roadmap

O projeto será implementado em **7 fases**, começando pela infraestrutura base e culminando em um sistema multi-agente com IA para interpretação de linguagem natural.

### Fases Resumidas

| Fase | Nome | Duração Est. | Deliverable |
|------|------|--------------|------------|
| 0 | Infraestrutura Base | 1-2 dias | Estrutura de pastas, dependências, setup inicial |
| 1 | Engine de Cálculo (Equities) | 5-7 dias | Todos os módulos de cálculo para ações, BDRs, FIIs, opções |
| 2 | Backend API | 3-4 dias | FastAPI endpoints, banco de dados, persistência |
| 2.5 | Streamlit Prototype | 1-2 dias | Demo UI para validação e apresentações intermediárias |
| 3 | LLM + ChromaDB | 4-5 dias | Integração Claude, parser de linguagem natural, regulamentações |
| 4 | Frontend Angular | 5-7 dias | Interface chat, formulário, exibição de resultados |
| 5 | Docker & Deploy | 2-3 dias | Containerização, docker-compose, testes E2E |
| 6 | MCP Server (Dev Tool) | 2-3 dias | Ferramentas internas para validação e pesquisa |
| 7 | Multi-Agent (Fase 2 TCC) | 4-6 dias | Orquestrador + agentes especializados |

**Total Estimado**: 27-41 dias (5-8 semanas com desenvolvimento 5x/semana)

---

## Fase 0: Infraestrutura Base

**Objetivo**: Preparar o ambiente local para desenvolvimento.  
**Duração**: 1-2 dias  
**Responsável**: Você

### 0.1 — Estrutura de Pastas

- [ ] Criar diretório `/backend/`
- [ ] Criar diretório `/backend/app/`
- [ ] Criar diretório `/backend/app/api/`
- [ ] Criar diretório `/backend/app/calculations/`
- [ ] Criar diretório `/backend/app/calculations/equity/`
- [ ] Criar diretório `/backend/app/calculations/fees/`
- [ ] Criar diretório `/backend/app/calculations/taxes/`
- [ ] Criar diretório `/backend/app/llm/`
- [ ] Criar diretório `/backend/app/vector_db/`
- [ ] Criar diretório `/backend/app/models/`
- [ ] Criar diretório `/backend/app/storage/`
- [ ] Criar diretório `/backend/app/parsers/`
- [ ] Criar diretório `/backend/app/utils/`
- [ ] Criar diretório `/backend/tests/`
- [ ] Criar diretório `/backend/data/`
- [ ] Criar diretório `/backend/data/regulations/`
- [ ] Criar diretório `/frontend/`
- [ ] Criar diretório `/frontend/src/`

### 0.2 — Arquivos de Configuração Base

- [ ] Criar `/backend/pyproject.toml` (Poetry config)
  ```toml
  [tool.poetry]
  name = "brazilian-financial-assistant"
  version = "0.1.0"
  
  [tool.poetry.dependencies]
  python = "^3.11"
  fastapi = "^0.104.0"
  uvicorn = "^0.24.0"
  pydantic = "^2.5.0"
  sqlalchemy = "^2.0.0"
  chromadb = "^0.4.0"
  anthropic = "^0.7.0"
  python-dotenv = "^1.0.0"
  ```

- [ ] Criar `/.gitignore`
  ```
  # Environment
  .env
  .env.local
  
  # Python
  __pycache__/
  *.py[cod]
  *$py.class
  *.so
  .Python
  env/
  venv/
  ENV/
  
  # Poetry
  poetry.lock
  
  # IDE
  .vscode/
  .idea/
  *.swp
  
  # Database
  *.db
  *.sqlite3
  chroma_data/
  
  # Node
  node_modules/
  dist/
  
  # OS
  .DS_Store
  .Thumbs.db
  ```

- [ ] Criar `/.env.example`
  ```
  # LLM
  ANTHROPIC_API_KEY=your_key_here
  
  # Database
  DATABASE_URL=sqlite:///./app.db
  
  # Frontend
  FRONTEND_URL=http://localhost:4200
  
  # ChromaDB
  CHROMA_DB_PATH=./chroma_data
  ```

- [ ] Criar `/backend/__init__.py` (vazio)
- [ ] Criar `/backend/app/__init__.py` (vazio)

### 0.3 — Poetry & Dependências

```bash
cd backend
poetry install
```

- [ ] Verificar que `poetry.lock` foi criado
- [ ] Confirmar que dependências principais estão instaladas

### 0.4 — FastAPI Entry Point Minimal

- [ ] Criar `/backend/app/main.py`
  ```python
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  
  app = FastAPI(title="Brazilian Financial Assistant", version="0.1.0")
  
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:4200"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  
  @app.get("/health")
  async def health():
      return {"status": "ok"}
  ```

### 0.5 — Testes Iniciais

- [ ] Rodar servidor FastAPI
  ```bash
  uvicorn app.main:app --reload
  ```
- [ ] Visitar `http://localhost:8000/health` → deve retornar `{"status": "ok"}`
- [ ] Visitar `http://localhost:8000/docs` → OpenAPI docs devem carregar

### Checklist Fase 0
- [ ] Estrutura de pastas criada
- [ ] `pyproject.toml` configurado
- [ ] `.gitignore` e `.env.example` criados
- [ ] FastAPI rodando com health endpoint
- [ ] OpenAPI docs acessível

---

## Fase 1: Engine de Cálculo (Equities)

**Objetivo**: Implementar toda a lógica de cálculo de impostos e taxas para ações, BDRs, FIIs e opções.  
**Duração**: 5-7 dias  
**Entrada**: Pydantic models para trades, saída: cálculos de IR, taxas, net value  

### 1.1 — Models (Pydantic)

- [ ] Criar `/backend/app/models/trade.py`
  - `TradeType` enum: "acao", "bdr", "fii", "opcao"
  - `OperationType` enum: "compra", "venda"
  - `TradeOperationType` enum: "swing", "day_trade"
  - `TradeInput` model: ativo, tipo, qtd, preço, data, corretora, corretagem
  - `TaxCalculationResult` model: ganho_prejuizo, ir_devido, irrf_retido, taxas, valor_liquido
  - `PortfolioPosition` model: ativo, qtd, preco_medio, data_primeira_compra

### 1.2 — Cálculo de Preço Médio

- [ ] Criar `/backend/app/calculations/equity/price_averager.py`
  - Função: `calculate_weighted_average(positions: List[Position], new_qty: float, new_price: float) -> float`
  - Testes com múltiplas compras, vendas parciais
  - **Validação contra research.md**

### 1.3 — Cálculos por Ativo (Ações)

- [ ] Criar `/backend/app/calculations/equity/acoes.py`
  - Função: `calculate_swing_trade_tax(gains: float) -> TaxResult`
    - Alíquota: 15% (ou 0% se < R$20.000 total vendido no mês)
    - IRRF: 0,005%
  - Função: `calculate_day_trade_tax(gains: float, losses: float) -> TaxResult`
    - Alíquota: 20%
    - IRRF: 1%
  - Compensação de prejuízos (mesmo ativo, mesmo mês)
  - Testes: edge case isenção R$20.000

- [ ] Criar `/backend/app/calculations/equity/bdrs.py`
  - Similar a ações (mesmas alíquotas)

- [ ] Criar `/backend/app/calculations/equity/fiis.py`
  - Alíquota: 20% (sem isenção)
  - Sem compensação de prejuízos (por legislação)
  - IRRF: 0,005% / 1%

- [ ] Criar `/backend/app/calculations/equity/opcoes.py`
  - Exercício: usa regras da ação subjacente
  - Ganho/prejuízo: (preço_exercício - preço_premium) × qtd
  - Testes com calls e puts

### 1.4 — Cálculo de Taxas (B3)

- [ ] Criar `/backend/app/calculations/fees/b3_fees.py`
  - Taxa de liquidação: 0,0275%
  - Taxa de registro: 0,0034% (ações) / variável (derivativos)
  - Emolumentos: 0,003%
  - Função: `calculate_total_fees(valor_financeiro: float, asset_type: str) -> FeesResult`
  - Detalhamento: liquidação, registro, emolumentos, ISS

### 1.5 — Engine Central de Impostos

- [ ] Criar `/backend/app/calculations/taxes/ir_engine.py`
  - Classe: `TaxEngine`
  - Métodos:
    - `add_trade(trade: TradeInput)`
    - `calculate_monthly_tax(month: int, year: int) -> MonthlyTaxResult`
    - `get_total_tax()`
  - Gestão de bases (day trade vs swing trade separadas)
  - Gestão de prejuízos carregáveis

### 1.6 — Dados de Regras

- [ ] Criar `/backend/app/data/tax_rules.json`
  ```json
  {
    "assets": {
      "acao": {
        "swing_trade": {"aliquota": 0.15, "min_exemption": 20000},
        "day_trade": {"aliquota": 0.20}
      }
    },
    "fees": {
      "b3": {
        "liquidacao": 0.000275,
        "registro_acao": 0.000034
      }
    }
  }
  ```

### 1.7 — Testes Unitários

- [ ] Criar `/backend/tests/test_acoes.py`
  - Teste: swing trade sem isenção
  - Teste: swing trade com isenção (< R$20.000)
  - Teste: swing trade acima de R$20.000 (perde isenção)
  - Teste: day trade (alíquota 20%)
  - Teste: múltiplas compras + vendas (preço médio)
  - **Testes contra research.md Cenários 1-3**

- [ ] Criar `/backend/tests/test_bdrs.py` (similar)
- [ ] Criar `/backend/tests/test_fiis.py`
  - Teste: sem isenção
  - Teste: sem compensação
- [ ] Criar `/backend/tests/test_fees.py`
  - Teste: B3 fees breakdown
  - Teste: corretagem variável

### 1.8 — Validação Contra Dados Reais

- [ ] Coletar 3-5 operações reais de plataforma (C6, XP, etc.)
- [ ] Calcular manualmente esperado
- [ ] Rodar Engine e validar resultado
- [ ] Documentar resultados em `/backend/tests/real_scenarios.py`

### Checklist Fase 1
- [ ] Models Pydantic criados e tipados
- [ ] Preço médio funcionando (testes passando)
- [ ] Ações: swing + day trade, isenção implementada
- [ ] BDR: implementado
- [ ] FII: implementado, sem isenção
- [ ] Opções: implementado
- [ ] Fees B3: detalhamento correto
- [ ] Testes unitários: 90%+ cobertura
- [ ] Testes com dados reais: validação ✓

---

## Fase 2: Backend API (FastAPI)

**Objetivo**: Expor Engine de cálculo via REST API, integrar banco de dados.  
**Duração**: 3-4 dias  
**Entrada**: Engine Phase 1, saída: POST /api/trades/process funcional  

### 2.1 — Modelos de Banco de Dados (SQLAlchemy)

- [ ] Criar `/backend/app/storage/database.py`
  - Setup SQLAlchemy + SQLite (dev)
  - Connection string via env var

- [ ] Criar `/backend/app/storage/models.py`
  ```python
  User:
    - id (PK)
    - email
    - created_at
  
  Trade:
    - id (PK)
    - user_id (FK)
    - asset_type
    - operation_type (compra/venda)
    - quantity
    - price
    - date
    - corretora
    - corretagem
    - irrf_retido
    - created_at
  
  Calculation:
    - id (PK)
    - user_id (FK)
    - month/year
    - total_gains
    - total_losses
    - ir_due
    - darf_deadline
    - created_at
  
  ChatHistory:
    - id (PK)
    - user_id (FK)
    - message (user input)
    - response (assistant response)
    - created_at
  ```

### 2.2 — API Endpoint: Process Trade

- [ ] Criar `/backend/app/api/trades.py`
  ```python
  POST /api/trades/process
  {
    "ativo": "PETR4",
    "tipo_operacao": "venda",
    "quantidade": 100,
    "preco": 25.50,
    "data": "2025-03-15",
    "corretora": "C6",
    "corretagem": 0.001
  }
  
  Response:
  {
    "ganho_prejuizo": 100.50,
    "ir_devido": 15.08,
    "irrf_retido": 0.005,
    "taxas": {...},
    "valor_liquido": 2529.99,
    "mensagem": "Operação processada com sucesso"
  }
  ```

- [ ] Validar entrada com Pydantic
- [ ] Chamar Engine de cálculo (Fase 1)
- [ ] Retornar resultado

### 2.3 — API Endpoint: Chat

- [ ] Criar `/backend/app/api/chat.py` (MVP: HTTP, não WebSocket)
  ```python
  POST /api/chat
  {
    "message": "Vendi 100 ações da PETR4 por R$25,50 cada",
    "user_id": "user123"
  }
  
  Response:
  {
    "response": "Entendi. Você vendeu 100 ações da PETR4 a R$25,50...",
    "extracted_trade": {...},
    "calculation": {...}
  }
  ```

- [ ] Placeholder (será integrado com LLM em Fase 3)

### 2.4 — API Endpoint: Histórico de Cálculos

- [ ] Criar `/backend/app/api/calculations.py`
  ```python
  GET /api/calculations/{calculation_id}
  Response: Cálculo completo com breakdown
  
  GET /api/calculations/summary?month=3&year=2025
  Response: Resumo mensal (ganhos, perdas, IR)
  ```

### 2.5 — CORS & Security

- [ ] Configurar CORS para `localhost:4200` (Angular dev)
- [ ] Adicionar rate limiting (opcional, Phase 1 pode pular)
- [ ] Middleware de logging

### 2.6 — Testes de Integração

- [ ] Criar `/backend/tests/test_api.py`
  - Teste: POST /api/trades/process
  - Teste: GET /api/calculations/{id}
  - Teste: Database persistence (trade salvo e recuperado)

- [ ] Fixture: Database de teste (SQLite em memória)

### Checklist Fase 2
- [ ] SQLAlchemy models criados
- [ ] POST /api/trades/process funcional
- [ ] GET /api/calculations/{id} funcional
- [ ] Database persiste trades
- [ ] Testes de integração passando
- [ ] CORS configurado

---

## Fase 2.5: Streamlit Prototype (Demo UI)

**Objetivo**: Interface de demonstração rápida para validar o fluxo completo de cálculo visualmente, antes de construir o Angular.  
**Duração**: 1-2 dias  
**Entrada**: Backend API Phase 2 funcional, saída: app Streamlit rodando em localhost:8501  
**Nota**: Demo e prototipagem apenas — não vai para produção. Ideal para TCC apresentações intermediárias e validação rápida.

### 2.5.1 — Setup Streamlit

- [ ] Adicionar `streamlit` ao `requirements.txt` (ou `pyproject.toml`)
- [ ] Criar `/streamlit_app/` diretório
- [ ] Criar `/streamlit_app/app.py` — entry point

### 2.5.2 — Páginas do App

- [ ] Criar `/streamlit_app/pages/1_Calcular_Trade.py`
  ```python
  # Formulário estruturado: ativo, tipo, qtd, preço, data, corretora
  # Chama POST /api/trades/process
  # Exibe resultado: ganho/prejuízo, IR devido, taxas detalhadas, valor líquido
  ```

- [ ] Criar `/streamlit_app/pages/2_Chat.py`
  ```python
  # Input de linguagem natural (para ser integrado quando Phase 3 estiver pronto)
  # Chama POST /api/chat
  # Exibe conversa + resultado de cálculo formatado
  ```

- [ ] Criar `/streamlit_app/pages/3_Historico.py`
  ```python
  # Chama GET /api/calculations/summary
  # Exibe tabela de trades e resumo mensal
  ```

### 2.5.3 — Componentes Reutilizáveis

- [ ] Criar `/streamlit_app/components/result_card.py`
  ```python
  def render_result(result: dict):
      # Exibe card com:
      # - Ganho/Prejuízo em destaque (verde/vermelho)
      # - IR Devido, IRRF, Taxas B3
      # - Valor Líquido final
      # Formatos PT-BR: R$ com vírgula, datas DD/MM/YYYY
  ```

- [ ] Criar `/streamlit_app/utils/api_client.py`
  ```python
  # Funções helper para chamar o backend FastAPI
  # Reutilizável entre todas as páginas
  ```

### 2.5.4 — Configuração

- [ ] Criar `/streamlit_app/.streamlit/config.toml`
  ```toml
  [server]
  port = 8501

  [theme]
  primaryColor = "#1a73e8"
  backgroundColor = "#ffffff"
  secondaryBackgroundColor = "#f0f2f6"
  ```

### 2.5.5 — Docker (Opcional)

- [ ] Adicionar serviço `streamlit` ao `docker-compose.dev.yml`
  ```yaml
  streamlit:
    build:
      context: ./streamlit_app
    ports:
      - "8501:8501"
    depends_on:
      - backend
    command: streamlit run app.py
  ```

### 2.5.6 — Testes Manuais

- [ ] Teste: formulário de trade → cálculo exibido corretamente (PT-BR)
- [ ] Teste: resultado com isenção R$20.000 exibido corretamente
- [ ] Teste: resultado negativo (prejuízo) exibido em vermelho
- [ ] Teste: página de chat conecta ao backend (placeholder até Phase 3)

### Checklist Fase 2.5
- [ ] Streamlit rodando em localhost:8501
- [ ] Formulário de trade → cálculo funcional
- [ ] Resultados formatados em PT-BR (R$, datas)
- [ ] Página de chat conecta ao `/api/chat`
- [ ] Histórico de cálculos visível
- [ ] Dockerizado (opcional)

---

## Fase 3: LLM + ChromaDB Integration

**Objetivo**: Integrar Claude API para parsing de linguagem natural, embeddings de regulamentações.  
**Duração**: 4-5 dias  
**Entrada**: FastAPI Phase 2, saída: `/api/chat` com IA funcional  

### 3.1 — Anthropic SDK Client

- [ ] Criar `/backend/app/llm/claude_client.py`
  ```python
  class ClaudeClient:
    def __init__(api_key: str)
    def parse_trade(user_message: str) -> TradeInput
    def explain_calculation(calc_result: TaxCalculationResult) -> str
    def answer_question(question: str, context: str) -> str
  ```

- [ ] Usar `claude-haiku-4-5` para parsing (fast, cheap)
- [ ] Usar `claude-sonnet-4-6` para explicações complexas (se necessário, Phase 1 pode usar só Haiku)

### 3.2 — Prompts em PT-BR

- [ ] Criar `/backend/app/llm/prompts.py`
  ```python
  SYSTEM_PROMPT_PARSER = """
  Você é um assistente financeiro especializado em mercado de ações brasileiro.
  Sua tarefa é extrair informações de operações de bolsa do texto fornecido pelo usuário.
  
  Retorne um JSON estruturado com:
  - ativo
  - tipo_operacao (compra/venda)
  - quantidade
  - preco
  - data
  - tipo_trade (swing/day_trade) [se possível deduzir]
  """
  
  SYSTEM_PROMPT_EXPLAINER = """
  Você é um assessor financeiro que explica resultados de cálculos de imposto de renda.
  Use linguagem simples e didática. Sempre em português brasileiro.
  """
  ```

### 3.3 — ChromaDB Setup

- [ ] Criar `/backend/app/vector_db/chroma_client.py`
  ```python
  class ChromaDB:
    def __init__(db_path: str)
    def add_regulation(title: str, content: str)
    def search_regulations(query: str, top_k: int = 5) -> List[str]
  ```

- [ ] Usar embedding model: `all-MiniLM-L6-v2` (HuggingFace, open-source)

### 3.4 — Carregar Regulamentações

- [ ] Criar `/backend/app/vector_db/loader.py`
  ```python
  def load_regulations_from_disk():
    # Ler /backend/data/regulations/*.txt
    # Alimentar ChromaDB na inicialização
  ```

- [ ] Criar `/backend/data/regulations/` com documentos:
  - `ir_acoes.txt` — Regras IR para ações (Receita Federal)
  - `b3_fees.txt` — Tabela de taxas B3
  - `darf_guide.txt` — Guia DARF
  - `isenção_20k.txt` — Explicação isenção R$20.000
  - (pode ser cópia/resumo de research.md)

### 3.5 — Chat Endpoint com LLM

- [ ] Atualizar `/backend/app/api/chat.py`
  ```python
  POST /api/chat
  {
    "message": "Vendi 100 ações da PETR4 por R$25,50 cada"
  }
  
  Fluxo:
  1. ClaudeClient.parse_trade(message) → TradeInput (via Haiku)
  2. TaxEngine.calculate(TradeInput) → TaxCalculationResult
  3. ClaudeClient.explain_calculation(result) → Explicação em PT-BR (via Sonnet ou Haiku)
  4. Salvar em ChatHistory
  ```

### 3.6 — Retrieval-Augmented Generation (RAG)

- [ ] Implementar busca de contexto antes de chamar LLM
  ```python
  def answer_question(question: str):
    context = chromadb.search_regulations(question, top_k=3)
    response = claude.answer(question, context=context)
  ```

### 3.7 — Testes

- [ ] Criar `/backend/tests/test_llm.py`
  - Teste: parse_trade("Comprei 50 ações VALE3 a R$23.50")
  - Teste: Resultado é TradeInput válido com campos corretos

- [ ] Criar `/backend/tests/test_chroma.py`
  - Teste: search_regulations("isenção") retorna regulação correta
  - Teste: ChromaDB persiste entre chamadas

### Checklist Fase 3
- [ ] ClaudeClient integrado
- [ ] Prompts em PT-BR criados
- [ ] ChromaDB funcionando
- [ ] Regulamentações carregadas
- [ ] POST /api/chat parse e calcula corretamente
- [ ] ChatHistory salvando em DB
- [ ] Testes passando

---

## Fase 4: Frontend Angular

**Objetivo**: Interface web para usuário enviar trades e ver resultados.  
**Duração**: 5-7 dias  
**Entrada**: FastAPI completo, saída: app Angular rodando em localhost:4200  

### 4.1 — Setup Angular 17

```bash
ng new frontend --standalone
cd frontend
npm install @angular/material
```

- [ ] Confirmar que `ng serve` roda em localhost:4200

### 4.2 — Modelos TypeScript

- [ ] Criar `/frontend/src/app/models/trade.ts`
  ```typescript
  export interface Trade {
    ativo: string;
    tipoOperacao: "compra" | "venda";
    quantidade: number;
    preco: number;
    data: string;
    corretora?: string;
  }
  
  export interface CalculationResult {
    ganhoPrejuizo: number;
    irDevido: number;
    irrf_retido: number;
    taxas: { [key: string]: number };
    valorLiquido: number;
  }
  
  export interface ChatMessage {
    role: "user" | "assistant";
    content: string;
    trade?: Trade;
    calculation?: CalculationResult;
  }
  ```

### 4.3 — API Service

- [ ] Criar `/frontend/src/app/services/api.service.ts`
  ```typescript
  @Injectable()
  export class ApiService {
    constructor(private http: HttpClient) {}
    
    processTrade(trade: Trade): Observable<CalculationResult> {
      return this.http.post<CalculationResult>('/api/trades/process', trade);
    }
    
    sendChat(message: string): Observable<ChatResponse> {
      return this.http.post<ChatResponse>('/api/chat', { message });
    }
    
    getCalculations(month: number, year: number): Observable<CalculationResult[]> {
      return this.http.get(`/api/calculations/summary`, { params: { month, year } });
    }
  }
  ```

### 4.4 — Chat Component

- [ ] Criar `/frontend/src/app/components/chat/chat.component.ts`
  - Input: textfield para mensagem do usuário
  - Output: mensagem + resultado de cálculo
  - Material: `MatCardModule`, `MatFormFieldModule`, `MatButtonModule`
  - Tratamento de locale: PT-BR (vírgula decimal)

- [ ] HTML: chat-like interface
  - Lista de mensagens (user | assistant)
  - Cada mensagem de cálculo mostra resultado formatado

### 4.5 — Trade Input Component

- [ ] Criar `/frontend/src/app/components/trade-input/trade-input.component.ts`
  - Formulário estruturado (não natural language)
  - Campos: ativo, tipo, qtd, preço, data, corretora
  - Dropdown para corretora (configurável)
  - Botão: "Calcular"

### 4.6 — Results Component

- [ ] Criar `/frontend/src/app/components/results/results.component.ts`
  - Exibir ganho/prejuízo, IR devido, taxas detalhadas
  - Gráfico simples (opcional): Chart.js com breakdown de taxas
  - Locales: R$ (símbolo), vírgula decimal, datas DD/MM/YYYY

### 4.7 — Locale (PT-BR)

- [ ] Criar `/frontend/src/app/pipes/locale.pipe.ts`
  ```typescript
  @Pipe({
    name: 'currency',
    standalone: true
  })
  export class CurrencyPipe implements PipeTransform {
    transform(value: number): string {
      return value.toLocaleString('pt-BR', { 
        style: 'currency', 
        currency: 'BRL' 
      });
    }
  }
  ```

### 4.8 — App Component

- [ ] Criar `/frontend/src/app/app.component.ts`
  - Layout: Header (título), Sidebar ou Tabs (Chat | Trade Input | Histórico)
  - Material AppBar, Sidenav

### 4.9 — Testes E2E (opcional, Phase 1)

- [ ] Criar `/frontend/e2e/chat.e2e.ts` (Cypress ou Playwright)
  - Teste: usuário digita mensagem → API responde → resultado exibido

### Checklist Fase 4
- [ ] Angular 17 rodando
- [ ] Models TypeScript criados
- [ ] API Service integrado
- [ ] Chat Component funcional
- [ ] Trade Input Component funcional
- [ ] Results Component exibe dados corretamente
- [ ] Locale PT-BR aplicado (moeda, datas)
- [ ] Chat → Backend → cálculo → Frontend: fluxo completo ✓

---

## Fase 5: Docker & Deploy

**Objetivo**: Containerizar app, docker-compose para dev/prod, preparar para cloud.  
**Duração**: 2-3 dias  
**Entrada**: App completo (backend + frontend), saída: `docker-compose up` funcional  

### 5.1 — Backend Dockerfile

- [ ] Criar `/backend/Dockerfile`
  ```dockerfile
  FROM python:3.11-slim
  
  WORKDIR /app
  COPY pyproject.toml poetry.lock ./
  RUN pip install poetry && poetry install --no-dev
  
  COPY . .
  
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

### 5.2 — Frontend Dockerfile

- [ ] Criar `/frontend/Dockerfile`
  ```dockerfile
  FROM node:18 AS build
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  COPY . .
  RUN npm run build
  
  FROM nginx:alpine
  COPY --from=build /app/dist/frontend /usr/share/nginx/html
  COPY nginx.conf /etc/nginx/conf.d/default.conf
  EXPOSE 80
  ```

- [ ] Criar `/frontend/nginx.conf`
  ```nginx
  server {
    listen 80;
    location / {
      root /usr/share/nginx/html;
      try_files $uri $uri/ /index.html;
    }
    location /api {
      proxy_pass http://backend:8000;
    }
  }
  ```

### 5.3 — docker-compose.yml (Produção)

- [ ] Criar `/docker-compose.yml`
  ```yaml
  version: "3.8"
  
  services:
    backend:
      build: ./backend
      ports:
        - "8000:8000"
      environment:
        DATABASE_URL: postgresql://user:pass@db:5432/bfa
        ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    
    frontend:
      build: ./frontend
      ports:
        - "80:80"
      depends_on:
        - backend
    
    db:
      image: postgres:15-alpine
      environment:
        POSTGRES_DB: bfa
        POSTGRES_USER: user
        POSTGRES_PASSWORD: pass
      volumes:
        - postgres_data:/var/lib/postgresql/data
  
  volumes:
    postgres_data:
  ```

### 5.4 — docker-compose.dev.yml (Desenvolvimento)

- [ ] Criar `/docker-compose.dev.yml`
  ```yaml
  version: "3.8"
  
  services:
    backend:
      build: ./backend
      ports:
        - "8000:8000"
      volumes:
        - ./backend:/app
      environment:
        DATABASE_URL: sqlite:///app.db
        ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      command: uvicorn app.main:app --reload --host 0.0.0.0
    
    frontend:
      build: ./frontend
      ports:
        - "4200:4200"
      volumes:
        - ./frontend/src:/app/src
      command: ng serve --host 0.0.0.0
  ```

### 5.5 — .dockerignore

- [ ] Criar `/.dockerignore`
  ```
  .git
  .gitignore
  node_modules
  dist
  __pycache__
  *.pyc
  .env
  .vscode
  .idea
  Documentation/
  README.md
  ```

### 5.6 — Build & Test Local

- [ ] Rodar localmente
  ```bash
  docker-compose -f docker-compose.dev.yml up
  # ou para produção
  docker-compose up --build
  ```

- [ ] Testes:
  - [ ] Backend rodando em 8000
  - [ ] Frontend rodando em 4200
  - [ ] POST /api/chat funciona (from frontend)
  - [ ] Banco de dados persiste (rodar 2x, dados continuam)

### 5.7 — Testes E2E

- [ ] Criar `/tests/e2e/full_flow.test.ts` (Playwright)
  - Usuário navega para localhost:4200
  - Digita mensagem no chat
  - Clica "Enviar"
  - Resultado aparece na tela
  - Resultado salvo no banco (verificar GET /api/calculations)

### 5.8 — GitHub Actions (opcional)

- [ ] Criar `/.github/workflows/ci.yml`
  ```yaml
  name: CI
  on: [push, pull_request]
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - name: Run backend tests
          run: docker-compose run backend pytest
        - name: Run frontend tests
          run: docker-compose run frontend npm test
  ```

### Checklist Fase 5
- [ ] Backend Dockerfile criado e buildable
- [ ] Frontend Dockerfile criado e buildable
- [ ] docker-compose.yml (prod) funcional
- [ ] docker-compose.dev.yml (dev) com hot-reload
- [ ] Teste: chat end-to-end via containers
- [ ] CI/CD (opcional, can skip Phase 1)

---

## Fase 6: MCP Server (Dev Tool)

**Objetivo**: Criar servidor MCP local para validação de cálculos durante desenvolvimento.  
**Duração**: 2-3 dias  
**Nota**: Não é deployado; usado apenas localmente para acelerar dev com Claude Code  

### 6.1 — MCP Server Setup

- [ ] Criar `/mcp_server/` diretório
- [ ] Criar `/mcp_server/server.py` (MCP SDK)
  ```python
  from mcp.server import Server
  from mcp.types import Tool, TextContent
  
  app = Server("brazilian-financial-assistant")
  
  @app.tool()
  def get_tax_rules(asset_type: str) -> str:
    """Retorna regras de IR para um tipo de ativo"""
    rules = {
      "acao": "15% swing trade, 20% day trade...",
      "fii": "20% sem isenção..."
    }
    return rules.get(asset_type, "Asset type not found")
  
  @app.tool()
  def get_fee_structure() -> dict:
    """Retorna tabela de taxas B3"""
    return {
      "liquidacao": 0.000275,
      "registro_acao": 0.000034,
      "emolumentos": 0.003
    }
  
  @app.tool()
  def validate_calculation(asset_type: str, params: dict, result: dict) -> str:
    """Valida um cálculo contra regras"""
    # Implementar lógica de validação
    return "Cálculo válido ✓"
  
  @app.tool()
  def example_calculation(asset_type: str) -> dict:
    """Retorna exemplo de cálculo passo-a-passo"""
    # Exemplos da research.md Cenários 1-3
    return {...}
  ```

### 6.2 — Configurar MCP em Claude Code

- [ ] Editar `~/.claude/settings.json` (ou `.claude/settings.json` no projeto)
  ```json
  {
    "mcpServers": {
      "brazilian-financial": {
        "command": "python",
        "args": ["/absolute/path/to/mcp_server/server.py"],
        "disabled": false
      }
    }
  }
  ```

### 6.3 — Testes

- [ ] Testar MCP localmente
  ```bash
  python mcp_server/server.py
  # Ou usar claude-ai/code para chamar os tools
  ```

- [ ] Teste: `get_tax_rules("acao")` retorna conteúdo esperado
- [ ] Teste: `validate_calculation("acao", {...}, {...})` valida corretamente

### Checklist Fase 6
- [ ] MCP Server criado
- [ ] Tools implementadas: get_tax_rules, get_fee_structure, validate_calculation, example_calculation
- [ ] Registrado em settings.json
- [ ] Claude Code consegue chamar tools
- [ ] Testes passando

---

## Fase 7: Multi-Agent RAG (Fase 2 TCC)

**Objetivo**: Implementar orquestrador de agentes especializados (Ações, Derivativos, etc).  
**Duração**: 4-6 dias  
**Nota**: Implementar DEPOIS que Phase 1 esteja completa e estável  

### 7.1 — Orchestrator Agent

- [ ] Criar `/backend/app/llm/orchestrator.py`
  ```python
  class OrchestratorAgent:
    def classify_trade(user_message: str) -> str:
      """Classifica: 'acao' | 'derivativo' | 'bdr_fii' """
      # Chamar Claude para classificar
      # Retornar asset_type
    
    def delegate(asset_type: str, trade: TradeInput) -> TaxCalculationResult:
      """Delega para agente especializado"""
  ```

### 7.2 — Specialized Agents

- [ ] Criar `/backend/app/llm/agents/acoes_agent.py`
  - ChromaDB scoped com regulações de ações
  - Cálculo via TaxEngine (Ações)
  - Explicação em PT-BR

- [ ] Criar `/backend/app/llm/agents/derivativo_agent.py`
  - ChromaDB scoped com regulações de futuros
  - Cálculo via TaxEngine (Futuros)
  - Explicação

- [ ] Criar `/backend/app/llm/agents/bdr_fii_agent.py`
  - BDRs + FIIs
  - ChromaDB + cálculo

### 7.3 — Atualizar Chat API

- [ ] Modificar `/backend/app/api/chat.py`
  ```python
  POST /api/chat
  {
    "message": "Vendi 100 PETR4..."
  }
  
  Fluxo:
  1. OrchestratorAgent.classify_trade() → "acao"
  2. Delegar para AcoesAgent
  3. AcoesAgent.process() → resultado
  4. Retornar ao usuário
  ```

### 7.4 — Documentação Multi-Agent

- [ ] Criar `/Documentation/multi_agent_architecture.md`
  - Diagrama: Orquestrador → Agentes
  - ChromaDB particionado por domínio
  - Benefícios para TCC (architecture pattern)

### 7.5 — Testes

- [ ] Criar `/backend/tests/test_orchestrator.py`
  - Teste: classifica "acao" corretamente
  - Teste: delega para agente correto
  - Teste: resultado final idêntico ao Phase 1 (sem orquestrador)

### Checklist Fase 7
- [ ] OrchestratorAgent funcional
- [ ] AcoesAgent, DerivativoAgent, BDR_FIIAgent criados
- [ ] Chat routing via orchestrator
- [ ] Testes passando
- [ ] Documentação multi-agent escrita

---

## Checklist de Validação Final

### Testes Unitários
- [ ] 90%+ code coverage nos modules de cálculo
- [ ] Todos os testes passando: `pytest tests/ -v`
- [ ] Testes com dados reais passando

### Testes de Integração
- [ ] E2E: chat → backend → cálculo → frontend
- [ ] Database: trades persistem e recuperam corretamente
- [ ] API: todas as rotas testadas

### Testes de Precisão Financeira
- [ ] Ações: swing trade, day trade, isenção R$20.000 ✓
- [ ] BDR: mesmas regras que ações ✓
- [ ] FII: sem isenção ✓
- [ ] Opções: baseado em ação subjacente ✓
- [ ] Taxas B3: breakdown correto ✓
- [ ] IRRF: calculado e exibido ✓

### Testes de Locale (PT-BR)
- [ ] Moeda exibida em R$ com vírgula decimal
- [ ] Datas em DD/MM/YYYY
- [ ] Mensagens em português

### Testes de Performance
- [ ] Cálculo de trade: < 500ms
- [ ] Parse de linguagem natural: < 2s (Haiku)
- [ ] ChromaDB search: < 1s

### Deployment
- [ ] docker-compose up --build: sem erros
- [ ] Backend rodando em :8000
- [ ] Frontend rodando em :80 (ou :4200 em dev)
- [ ] Conexão frontend ↔ backend funcional

### Documentação
- [ ] README.md atualizado com instruções de setup
- [ ] CLAUDE.md reflete estado atual
- [ ] research.md com todas as regras
- [ ] plan.md (este arquivo) com checkboxes marcados

---

## Notas e Anotações

### Sessão 1 (2026-04-27)
**Criado**: Estrutura do plano, research.md, plan.md  
**Status**: Planejamento completo. Pronto para iniciar Fase 0.

**Próximos passos**:
1. Confirmar se research.md tem informações corretas (validar com fontes oficiais)
2. Iniciar Fase 0: criação de pastas e setup Poetry
3. Após Fase 0: proceder com Fase 1 (Engine de cálculo)

---

### Decisões Abertas (para discutir)

1. **LLM para Chat**
   - MVP: Usar só `claude-haiku-4-5` para tudo (mais barato)
   - Alternativa: Haiku para parsing + Sonnet para explicações (mais caro, melhor qualidade)
   - **Recomendação**: MVP com Haiku, upgrade se necessário

2. **WebSocket vs HTTP para Chat**
   - MVP: HTTP polling simples (menos infra)
   - Alternativa: WebSocket (mais real-time, mais complexo)
   - **Recomendação**: HTTP MVP, WebSocket em Phase 2

3. **PostgreSQL em Prod vs SQLite**
   - SQLite é mais simples, PostgreSQL mais escalável
   - Para TCC, SQLite em dev + opção para Postgres em prod
   - **Recomendação**: Manter ambos, abstrair via SQLAlchemy

4. **Prompt Caching**
   - Ativar desde o início (reduz custo ~90% para requests similares)
   - Requer setup extra no Anthropic SDK
   - **Recomendação**: Implementar em Fase 3

---

### Riscos & Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|--------|-----------|
| Cálculos financeiros incorretos | Alta | Alto | Testes com dados reais, validação manual |
| LLM não entende português bem | Média | Médio | Prompt eng cuidadosa, fallback a formulário estruturado |
| Performance de ChromaDB | Baixa | Médio | Indexação, caching, validar com dados reais |
| Custo alto de API Claude | Média | Médio | Usar Haiku, prompt caching, rate limiting |
| Timeout em cloud | Baixa | Médio | Docker health checks, timeouts configurados |

---

### Recursos Úteis

- **Receita Federal**: https://www.gov.br/receitafederal/
- **B3**: https://www.b3.com.br/
- **Anthropic Docs**: https://docs.anthropic.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **ChromaDB**: https://docs.trychroma.com/
- **Angular**: https://angular.io/

---

**Plano criado por**: Claude Code  
**Data**: 2026-04-27  
**Status**: Ready for Phase 0 ✓
