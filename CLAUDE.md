# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Brazilian Financial Assistant** is a capstone project (TCC) building an intelligent chatbot/assistant for the Brazilian financial market. The core functionality calculates taxes, fees, net values, and provides financial insights when users input their trades executed in Brazil.

Users input their trades and the assistant processes them to compute:
- Taxes (IR - Imposto de Renda)
- Transaction fees and costs
- Net value calculations
- Financial summaries and insights

### Development Phases

**Phase 1: Equity Products**
- Ações (Stocks)
- BDRs (Brazilian Depositary Receipts)
- Fundos Imobiliários (Real Estate Investment Trusts)
- Opções de Ações (Stock Options)

**Phase 2: Derivatives**
- Futuros de Dólar (USD Futures)
- Futuros de Índice (Index Futures)
- Futuros de Criptomoedas (Crypto Futures)
- Other derivatives

**Phase 3: Advanced Products**
- Empréstimo de Ações (Stock Lending)

## Technology Stack

**Backend**
- **Language**: Python 3.10+
- **API Framework**: FastAPI
- **LLM Integration**: OpenAI API, Claude API, or local models
- **Vector Database**: ChromaDB (for document/regulation embeddings and retrieval)
- **Database**: SQLite or PostgreSQL (user trade history, calculations, chat history)
- **Financial Calculations Engine**: Custom Python modules for tax/fee calculations

**Frontend**
- **Framework**: Angular (TypeScript)
- **UI Components**: Material Design or similar
- **HTTP Client**: Angular HttpClient for API communication

**Data Sources**
- Brazilian tax regulations (IR rules, fee structures)
- B3 (Bolsa de Valores) documentation
- Market data APIs (price feeds, derivatives data)

**Deployment & DevOps**
- **Containerization**: Docker
- **Orchestration**: Docker Compose (for local dev and production)
- **Cloud Deployment**: Azure Container Instances or AWS ECS (temporary for capstone presentation)
- **Package Managers**: 
  - Backend: Poetry or pip with requirements.txt
  - Frontend: npm or yarn

**Custom MCP (Model Context Protocol)**
- Internal MCP server to assist development with financial calculations and tax rules
- Provides context and tools for Claude Code during implementation

## Project Structure (Expected)

```
.
├── backend/                          # Python backend
│   ├── app/
│   │   ├── api/                    # FastAPI routes/endpoints
│   │   │   ├── chat.py            # Chat endpoint
│   │   │   ├── trades.py          # Trade input/processing
│   │   │   └── calculations.py    # Calculation endpoints
│   │   ├── calculations/          # Financial calculation engines
│   │   │   ├── taxes/            # Tax calculations (IR rules)
│   │   │   ├── fees/             # Transaction fees & costs
│   │   │   ├── equity/           # Ações, BDRs, Fundos Imob, Opções
│   │   │   ├── derivatives/      # Futuros, Derivativos
│   │   │   └── lending/          # Empréstimo de Ações
│   │   ├── llm/                    # LLM integration & prompts
│   │   ├── vector_db/              # ChromaDB integration
│   │   ├── models/                 # Database/Pydantic models
│   │   ├── storage/                # Database/persistence layer
│   │   ├── parsers/                # Parse user input (trade details)
│   │   └── utils/                  # Utilities
│   ├── data/                        # Financial rules, regulations, reference data
│   ├── tests/                       # Test suite
│   ├── main.py                      # FastAPI app entry point
│   ├── requirements.txt             # Dependencies
│   ├── Dockerfile                   # Backend container
│   └── pyproject.toml              # Poetry config (optional)
│
├── frontend/                         # Angular frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/        # UI components
│   │   │   │   ├── chat/         # Chat interface component
│   │   │   │   ├── trade-input/  # Trade input form
│   │   │   │   └── results/      # Results display
│   │   │   ├── services/         # HTTP services (API calls)
│   │   │   │   └── api.service.ts
│   │   │   ├── models/           # TypeScript interfaces
│   │   │   └── app.component.ts
│   │   ├── assets/               # Images, icons
│   │   ├── environments/         # Environment configs
│   │   └── main.ts
│   ├── angular.json
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile                # Frontend container
│   └── nginx.conf               # Nginx config (for production)
│
├── docker-compose.yml             # Orchestrate backend + frontend
├── .dockerignore
├── .gitignore
└── README.md
```

## Common Development Commands

### Backend (Python/FastAPI)

```bash
# Install dependencies
cd backend
pip install -r requirements.txt
# or with Poetry
poetry install

# Run tests
pytest tests/
pytest tests/test_module.py::test_function  # Single test

# Format and lint
black app/
flake8 app/
isort app/

# Run development server
python -m uvicorn app.main:app --reload

# Or run from backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Angular)

```bash
# Install dependencies
cd frontend
npm install

# Run development server
ng serve
# or
npm start

# Run tests
ng test
# or
npm test

# Build for production
ng build --configuration production
```

### Docker & Docker Compose

```bash
# Build and run entire stack
docker-compose up --build

# Run with hot reload (for development)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Build individual containers
docker build -t brazilian-financial-backend ./backend
docker build -t brazilian-financial-frontend ./frontend

# Stop all containers
docker-compose down
```

## Key Architectural Considerations

1. **Monorepo Structure**: Single repository with backend + frontend + Docker config. Simplifies:
   - Deployment (single docker-compose orchestrates both services)
   - Versioning (frontend and backend versions together)
   - Development workflow (clone once, run together)

2. **API Contract (FastAPI ↔ Angular)**:
   - Backend exposes REST/WebSocket endpoints for:
     - Chat messages (POST /api/chat)
     - Trade processing (POST /api/trades/process)
     - Calculation results (GET /api/calculations/{id})
   - Frontend sends structured data; backend returns JSON responses with calculations and explanations
   - Use FastAPI auto-generated OpenAPI docs for type safety

3. **ChromaDB Integration**:
   - Store embeddings of Brazilian financial regulations, tax rules, B3 documentation
   - On startup, load regulatory documents into ChromaDB
   - When processing trades, retrieve relevant regulations/rules via semantic search
   - Pass retrieved context to LLM for more accurate calculations and explanations
   - Example: User mentions "ação" → ChromaDB retrieves relevant IR rules → LLM uses this context

4. **Modular Calculation Engine**: Separate calculation logic by asset class (equities, derivatives, lending). Each module handles:
   - Trade input parsing and validation
   - Tax calculations based on current Brazilian tax law (IR rates, exemptions)
   - Fee/cost calculations (brokerage fees, B3 fees, etc.)
   - Net value computations

5. **Tax Rules Engine**: Encode Brazilian tax regulations:
   - IR rules for different asset types (aliquotas, isenções)
   - Darf (tax payment) calculations
   - Monthly/annual tax compliance requirements
   - Specific rules for derivatives, lending, etc.

6. **Trade Data Model**: Design flexible models to capture:
   - Asset type and quantity
   - Entry/exit prices and dates
   - Associated fees and costs
   - Tax treatment and exemptions

7. **LLM as Chat Interface**: Use LLM to:
   - Parse natural language trade descriptions from users (via Angular chat)
   - Clarify ambiguous inputs
   - Explain calculation results in Portuguese
   - Provide financial insights and recommendations

8. **Accuracy & Compliance**: Financial calculations must be precise and comply with B3 and Brazilian tax authority (Receita Federal) rules. Validate all calculations against authoritative sources.

9. **Phased Development**: Build Phase 1 (equities) with full tax/fee accuracy before expanding to derivatives and lending products.

## Development Notes

- **Portuguese Language**: All user interactions, calculations, and outputs in Brazilian Portuguese. Handle date formats (DD/MM/YYYY), number formats (using comma for decimals).

- **Brazilian Tax Accuracy**: This is critical. Reference:
  - Receita Federal guidelines for IR on financial operations
  - B3 official documentation for fees and trading rules
  - Current tax rates and exemption thresholds (they change yearly)
  
- **Phase 1 Priority**: Get equity product calculations (Ações, BDRs, Fundos Imob, Opções) completely accurate before advancing. Test against real scenarios.

- **Testing Strategy**:
  - Unit tests for each calculation module (isolated tax/fee logic)
  - Integration tests with real trade scenarios
  - Validation against known results from financial platforms (C6, Clear, XP, etc.)
  - E2E tests for chat flow (Angular + FastAPI)
  
- **Secrets Management**: Store API keys (OpenAI/Claude) in `.env` files, never in version control. Use environment variables in Docker.

- **Performance**: Calculations should be instant; prioritize accuracy over fancy LLM features.

- **Frontend-Backend Communication**:
  - Use JSON for all API requests/responses
  - Define clear request/response schemas using Pydantic (backend) and TypeScript interfaces (frontend)
  - CORS must be configured in FastAPI to allow requests from Angular dev server
  
- **Docker Development**:
  - Use docker-compose for local development
  - Mount volumes for hot-reload during development (source code changes without rebuilding)
  - Separate docker-compose.yml (production) from docker-compose.dev.yml (development with hot-reload)
  - Each service (backend, frontend) runs in separate containers
  
- **ChromaDB Data**:
  - Populate ChromaDB with regulatory documents during app startup
  - Store ChromaDB data in a persistent volume (docker volume)
  - Include sample regulations in `/backend/data/` directory for initial seeding

- **Internal MCP Server (Development Tool)**:
  - Implement as separate Python service using MCP SDK
  - Does NOT ship with the application (local development only)
  - Register in `claude.ai/code` settings via MCP configuration
  - Tools return structured data: rules, examples, validation results, documentation
  - Example: `get_tax_rules("acao")` returns IR rules specific to stock trades
  
- **MCP Integration with Claude Code**:
  - Configure MCP in `.claude/settings.json` or via claude.ai/code UI
  - Claude automatically calls MCP tools when developing tax/fee calculation modules
  - Useful for: verifying calculation logic, researching rules, getting worked examples, validating against regulations
  - MCP data comes from `/backend/data/` directory (regulations, rules, examples)

## Implementation Roadmap

**Phase 1: Equity Products (Ações, BDRs, Fundos Imobiliários, Opções)**
1. Set up Python project structure and dependencies
2. Build trade data models
3. Implement IR tax calculations for equity operations
4. Implement fee/cost calculations (B3, brokerage)
5. Create calculation engine for net values
6. Build basic chatbot interface with LLM
7. Thorough testing against real-world scenarios

**Phase 2: Derivatives (Futuros, etc.)**
1. Extend models for derivative trades
2. Implement tax calculations for futures
3. Handle margin and daily settlement (D+1) specifics
4. Add to chatbot

**Phase 3: Stock Lending**
1. Model stock lending operations
2. Implement associated tax rules
3. Integrate into full system

## Multi-Agent Architecture

The assistant uses a **Multi-Agent RAG** pattern where an orchestrator routes each user trade to a specialized agent:

```
User inputs trade
       ↓
  Orchestrator Agent (LLM)
  identifies asset type
  /        |         \
Agent    Agent      Agent
Ações  Derivativos   BDR/FII
  \        |         /
   Consolidated result
       (taxes, fees, net value)
```

**Orchestrator**: Receives user input, classifies the asset type, and delegates to the appropriate specialist agent.

**Specialist Agents**: Each agent has:
- ChromaDB context scoped to its asset type (IR rules, B3 fees, regulations)
- Calculation modules specific to its domain
- Awareness of its own tax rules and exemptions

**Implementation Strategy**:
- **Phase 1**: Single LLM + direct calculation modules (no multi-agent yet — avoid complexity early)
- **Phase 2**: Introduce orchestrator + Ações/Derivativos agents (natural split point when Derivatives adds complexity)
- **Phase 3**: Add Lending agent, orchestrator handles all three

**Academic Value**: Multi-Agent RAG is a strong differentiator for the capstone presentation — demonstrates both AI architecture and domain specialization.

## Custom MCP (Internal Development Tool)

A custom MCP server will be created as an **internal development tool** to assist Claude Code while building this project:

**Purpose**: Provide Claude with context and tools during implementation:
- Brazilian financial market regulations and tax rules (Receita Federal, B3)
- Reference implementations and validation logic
- Trade calculation algorithms and examples
- Documentation on financial products (Ações, Derivativos, etc.)

**Implementation**:
- MCP server (stdio transport) with tools for:
  - `get_tax_rules(asset_type)` - Retrieve applicable IR rules for a specific asset type
  - `get_fee_structure()` - Return current B3 and brokerage fee structures
  - `validate_calculation(type, params, result)` - Validate calculation logic against rules
  - `get_regulation(keyword)` - Search relevant Brazilian financial regulations
  - `example_calculation(asset_type)` - Return worked example calculations
- Runs locally during development (not part of the deployed application)

**Use Cases**:
- While implementing tax calculations: Claude queries `get_tax_rules()` to verify logic
- When coding fee calculations: Claude validates against `validate_calculation()`
- Debugging trade processing: Claude references `example_calculation()` to ensure correctness
- Researching regulations: Claude uses `get_regulation()` for documentation

**Benefits**:
- Reduces context window needed (Claude doesn't need to remember all tax rules)
- Ensures implementation aligns with actual Brazilian regulations
- Speeds up development through guided examples
- Acts as a "domain expert consultant" during coding

## Cloud Deployment (TCC Presentation)

For the capstone presentation, the application will be temporarily deployed to cloud infrastructure with the internal MCP:

**Options**:
- **Azure**: Azure Container Instances + Azure Database for PostgreSQL
- **AWS**: AWS ECS + RDS for PostgreSQL + CloudFront (CDN)

**Deployment Steps**:
1. Push Docker images to container registry (Azure ACR / AWS ECR)
2. Configure cloud database and secrets management
3. Deploy docker-compose stack (Azure) or use ECS task definitions (AWS)
4. Set up domain/DNS for presentation access
5. Configure monitoring and logging

**Cleanup**:
- Delete resources after presentation to avoid unnecessary costs
- Keep deployment configuration in version control for future use

**Environment-Specific Config**:
- Use environment variables for cloud endpoints
- Separate docker-compose files for local dev vs cloud deployment
- Store secrets in cloud provider's secrets management (Azure Key Vault / AWS Secrets Manager)

**Note**: The internal MCP (development tool) is NOT deployed to the cloud. It's only used locally during development with Claude Code.
