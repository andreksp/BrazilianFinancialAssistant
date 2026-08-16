# Brazilian Financial Assistant - System Architecture

## 1. High-Level System Architecture

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor':'#2c3e50', 'primaryBorderColor':'#3498db', 'lineColor':'#3498db', 'secondaryColor':'#34495e', 'tertiaryColor':'#95a5a6'}}}%%

graph TB
    User["👤 User<br/>(Browser)"]
    
    subgraph Frontend["🎨 Frontend Layer"]
        Chat["💬 Chat Interface<br/>Natural Language"]
        Form["📋 Trade Form<br/>Structured Input"]
        Results["📊 Results Display<br/>Calculations"]
    end
    
    subgraph Backend["⚙️ Backend Layer"]
        API["🛣️ API Router<br/>FastAPI"]
        
        LLM["🤖 Claude API<br/>Haiku | Sonnet | Opus"]
        Parser["Parse &<br/>Extract"]
        
        AcoesCalc["Ações<br/>Calculator"]
        FeeCalc["B3 Fee<br/>Calculator"]
        TaxEngine["Tax<br/>Engine"]
        
        DB["💾 Database<br/>SQLite/PostgreSQL"]
    end
    
    subgraph Data["📚 Data Layer"]
        ChromaDB["🔍 ChromaDB<br/>Regulations & Rules"]
    end
    
    subgraph External["☁️ External APIs"]
        ClaudeAPI["Anthropic<br/>Claude API"]
    end
    
    User -->|HTTP/JSON| Frontend
    Chat -->|POST /api/chat| API
    Form -->|POST /api/trades| API
    
    API -->|route| LLM
    API -->|route| AcoesCalc
    
    LLM -.->|semantic search| ChromaDB
    Parser -.->|query context| ChromaDB
    
    AcoesCalc -->|calculate| Results
    TaxEngine -->|aggregate| Results
    FeeCalc -->|breakdown| Results
    
    AcoesCalc -.->|read portfolio| DB
    TaxEngine -.->|persist| DB
    
    LLM -->|API calls| ClaudeAPI
    Results -->|HTTP/JSON| User
    
    style User fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#ecf0f1
    style Frontend fill:#27ae60,stroke:#1e8449,stroke-width:2px,color:#ecf0f1
    style Backend fill:#8e44ad,stroke:#6c3483,stroke-width:2px,color:#ecf0f1
    style Data fill:#e67e22,stroke:#ca6f1e,stroke-width:2px,color:#ecf0f1
    style External fill:#c0392b,stroke:#a93226,stroke-width:2px,color:#ecf0f1
    
    style Chat fill:#16a085,stroke:#117a65,stroke-width:1px,color:#ecf0f1
    style Form fill:#16a085,stroke:#117a65,stroke-width:1px,color:#ecf0f1
    style Results fill:#16a085,stroke:#117a65,stroke-width:1px,color:#ecf0f1
    
    style API fill:#5b7c99,stroke:#3d5a80,stroke-width:1px,color:#ecf0f1
    style LLM fill:#5b7c99,stroke:#3d5a80,stroke-width:1px,color:#ecf0f1
    style Parser fill:#5b7c99,stroke:#3d5a80,stroke-width:1px,color:#ecf0f1
    
    style AcoesCalc fill:#7d3c98,stroke:#5b2c78,stroke-width:1px,color:#ecf0f1
    style FeeCalc fill:#7d3c98,stroke:#5b2c78,stroke-width:1px,color:#ecf0f1
    style TaxEngine fill:#7d3c98,stroke:#5b2c78,stroke-width:1px,color:#ecf0f1
    style DB fill:#7d3c98,stroke:#5b2c78,stroke-width:1px,color:#ecf0f1
    
    style ChromaDB fill:#d68910,stroke:#b06e0f,stroke-width:1px,color:#ecf0f1
    style ClaudeAPI fill:#922b21,stroke:#78281f,stroke-width:1px,color:#ecf0f1
```

---

## 2. Chat Workflow (Natural Language Processing)

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    actor User
    participant Frontend
    participant Backend as Backend<br/>FastAPI
    participant Claude as Claude API
    participant ChromaDB
    participant Calculator
    participant Database as SQLite

    User->>Frontend: Type: "Vendi 100 PETR4<br/>por R$25,50"
    Frontend->>Backend: POST /api/chat/message
    
    activate Backend
    Backend->>Claude: 1. Extract trade from message
    activate Claude
    Claude-->>Backend: {ativo: PETR4,<br/>qty: 100,<br/>price: 25.50}
    deactivate Claude
    
    Backend->>ChromaDB: 2. Search tax rules<br/>"ações venda IR"
    activate ChromaDB
    ChromaDB-->>Backend: "15% swing trade,<br/>R$20k exemption"
    deactivate ChromaDB
    
    Backend->>Database: 3. Get average price<br/>for PETR4
    activate Database
    Database-->>Backend: PM = R$25.00
    deactivate Database
    
    Backend->>Calculator: 4. Calculate taxes
    activate Calculator
    Calculator-->>Backend: {ganho: 50.00,<br/>ir: 7.50,<br/>liquido: 2540.35}
    deactivate Calculator
    
    Backend->>Claude: 5. Explain results
    activate Claude
    Claude-->>Backend: "Você vendeu 100 ações<br/>com lucro de R$50.00...<br/>IR de R$7.50..."
    deactivate Claude
    
    Backend->>Database: 6. Save to history
    activate Database
    Database-->>Backend: Saved ✓
    deactivate Database
    
    Backend-->>Frontend: ChatResponse JSON
    deactivate Backend
    
    Frontend->>User: Display explanation<br/>+ calculation breakdown
```

---

## 3. Structured Trade Processing Workflow

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    actor User
    participant Frontend
    participant Backend as Backend<br/>FastAPI
    participant Database as SQLite
    participant Calculator
    participant Storage as Response

    User->>Frontend: Fill trade form +<br/>Submit
    Frontend->>Backend: POST /api/trades/process<br/>(TradeInput JSON)
    
    activate Backend
    Backend->>Database: Get portfolio<br/>position for PETR4
    activate Database
    Database-->>Backend: {qty: 100,<br/>avg_price: 25.00}
    deactivate Database
    
    Backend->>Calculator: calculate_result(<br/>trade, pm=25.00)
    activate Calculator
    
    Note over Calculator: 1. ganho = (25.50 - 25.00) * 100<br/>= R$50.00
    Note over Calculator: 2. taxas = B3 fees (0.87)<br/>+ Corretagem + ISS
    Note over Calculator: 3. ir = 50 * 0.15 = R$7.50<br/>(swing trade)
    Note over Calculator: 4. irrf = 2550 * 0.005% = R$1.28
    Note over Calculator: 5. liquido = 2550 - 0.87<br/>- 7.50 - 1.28
    
    Calculator-->>Backend: TaxCalculationResult
    deactivate Calculator
    
    Backend->>Database: Save trade & result
    activate Database
    Database-->>Backend: Saved with ID
    deactivate Database
    
    Backend-->>Storage: Return results
    deactivate Backend
    
    Storage-->>Frontend: TaxCalculationResult JSON
    Frontend->>User: Display breakdown:<br/>Gain, Taxes, Fees, Net Value
```

---

## 4. Data Flow: ChromaDB + LLM Integration

```mermaid
graph LR
    subgraph User["User Query"]
        Q["'What's the tax<br/>on stock sales?'"]
    end
    
    subgraph LLM_Processing["LLM Processing"]
        Haiku["Claude Haiku<br/>(Fast)"]
        Sonnet["Claude Sonnet<br/>(Balanced)"]
    end
    
    subgraph Knowledge["Knowledge Base"]
        ChromaDB_Collection["ChromaDB<br/>Regulatory Data"]
        Rules["📄 IR Rules<br/>📊 B3 Fees<br/>📋 Regulations"]
    end
    
    subgraph Response["Response Generation"]
        Answer["'IR on stocks is 15%<br/>swing, 20% day trade.<br/>Monthly exemption...'"]
    end
    
    Q -->|"identify intent:<br/>which regulations?"| Haiku
    Haiku -->|"semantic search<br/>for 'ações imposto renda'"| ChromaDB_Collection
    ChromaDB_Collection -->|"return relevant<br/>regulations"| Rules
    Rules -->|"provide context"| Sonnet
    Sonnet -->|"generate response<br/>in Portuguese"| Answer
    
    style User fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#ecf0f1
    style LLM_Processing fill:#8e44ad,stroke:#6c3483,stroke-width:2px,color:#ecf0f1
    style Knowledge fill:#e67e22,stroke:#ca6f1e,stroke-width:2px,color:#ecf0f1
    style Response fill:#27ae60,stroke:#1e8449,stroke-width:2px,color:#ecf0f1
```

---

## 5. Component Interaction Diagram

```mermaid
graph TB
    subgraph Core["Core Calculation"]
        AcoesCalc["AcoesCalculator<br/>─────<br/>get_tax_rate()<br/>get_irrf_rate()<br/>calculate_gain_loss()<br/>calculate_result()"]
        
        FeeCalc["B3FeeCalculator<br/>─────<br/>liquidação: 0.0275%<br/>registro: 0.0034%<br/>emolumentos: 0.003%<br/>corretagem: variable<br/>iss: 5%"]
        
        TaxEngine["TaxEngine<br/>─────<br/>track positions<br/>calculate PM<br/>monthly summaries<br/>loss tracking"]
    end
    
    subgraph Context["Context & Intelligence"]
        ChromaDB["ChromaDB<br/>─────<br/>Tax rules<br/>Fee structures<br/>Examples<br/>Documentation"]
        
        Claude["Claude API<br/>─────<br/>Haiku: Parse<br/>Sonnet: Explain<br/>Opus: Complex"]
    end
    
    subgraph Persistence["Data Storage"]
        DB["Database<br/>─────<br/>Trades<br/>Portfolio<br/>History<br/>Calculations"]
    end
    
    AcoesCalc -->|calculate gain/loss| TaxEngine
    FeeCalc -->|calculate fees| AcoesCalc
    TaxEngine -->|lookup position| DB
    TaxEngine -->|save result| DB
    Claude -->|query for context| ChromaDB
    Claude -->|get average price| DB
    
    style Core fill:#8e44ad,stroke:#6c3483,stroke-width:2px,color:#ecf0f1
    style Context fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#ecf0f1
    style Persistence fill:#e67e22,stroke:#ca6f1e,stroke-width:2px,color:#ecf0f1
    
    style AcoesCalc fill:#7d3c98,stroke:#5b2c78,stroke-width:1px,color:#ecf0f1
    style FeeCalc fill:#7d3c98,stroke:#5b2c78,stroke-width:1px,color:#ecf0f1
    style TaxEngine fill:#7d3c98,stroke:#5b2c78,stroke-width:1px,color:#ecf0f1
    style ChromaDB fill:#d68910,stroke:#b06e0f,stroke-width:1px,color:#ecf0f1
    style Claude fill:#5dade2,stroke:#2874a6,stroke-width:1px,color:#ecf0f1
    style DB fill:#d68910,stroke:#b06e0f,stroke-width:1px,color:#ecf0f1
```

---

## 6. Complete Request Flow: End-to-End

```mermaid
graph TD
    Start["User Action<br/>Chat OR Form"] -->|Chat| ChatPath["POST /api/chat/message"]
    Start -->|Form| FormPath["POST /api/trades/process"]
    
    ChatPath --> Parse["Claude Haiku<br/>Parse trade<br/>Extract fields"]
    Parse --> ChromaQuery["Query ChromaDB<br/>Get tax rules<br/>& regulations"]
    ChromaQuery --> Validate["Validate<br/>extracted trade"]
    
    FormPath --> DirectCalc["Directly go to<br/>calculation"]
    
    Validate --> GetPortfolio["Look up<br/>average price<br/>in database"]
    DirectCalc --> GetPortfolio
    
    GetPortfolio --> Calculate["Run Calculations<br/>─────<br/>AcoesCalculator<br/>B3FeeCalculator<br/>TaxEngine"]
    
    Calculate --> Result["Generate<br/>TaxCalculationResult"]
    
    Result --> Explain["Claude Sonnet<br/>Explain in<br/>Portuguese"]
    
    Explain --> SaveDB["Save to<br/>Database"]
    
    SaveDB --> Response["Return JSON<br/>Response"]
    
    Response --> Frontend["Frontend<br/>Display<br/>Results"]
    
    Frontend --> User["👤 User"]
    
    style Start fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#ecf0f1
    style ChatPath fill:#8e44ad,stroke:#6c3483,stroke-width:1px,color:#ecf0f1
    style FormPath fill:#8e44ad,stroke:#6c3483,stroke-width:1px,color:#ecf0f1
    style Parse fill:#9b59b6,stroke:#6c3483,stroke-width:1px,color:#ecf0f1
    style ChromaQuery fill:#d68910,stroke:#b06e0f,stroke-width:1px,color:#ecf0f1
    style Validate fill:#27ae60,stroke:#1e8449,stroke-width:1px,color:#ecf0f1
    style DirectCalc fill:#27ae60,stroke:#1e8449,stroke-width:1px,color:#ecf0f1
    style GetPortfolio fill:#e67e22,stroke:#ca6f1e,stroke-width:1px,color:#ecf0f1
    style Calculate fill:#16a085,stroke:#117a65,stroke-width:1px,color:#ecf0f1
    style Result fill:#5dade2,stroke:#2874a6,stroke-width:1px,color:#ecf0f1
    style Explain fill:#9b59b6,stroke:#6c3483,stroke-width:1px,color:#ecf0f1
    style SaveDB fill:#e67e22,stroke:#ca6f1e,stroke-width:1px,color:#ecf0f1
    style Response fill:#27ae60,stroke:#1e8449,stroke-width:1px,color:#ecf0f1
    style Frontend fill:#3498db,stroke:#2980b9,stroke-width:1px,color:#ecf0f1
    style User fill:#2ecc71,stroke:#27ae60,stroke-width:2px,color:#ecf0f1
```

---

## 7. Technology Stack & Deployment

```mermaid
graph TB
    subgraph Client["Client Layer"]
        Browser["🌐 Web Browser"]
        Angular["Angular 17<br/>TypeScript<br/>Material UI"]
    end
    
    subgraph Server["Server Layer"]
        FastAPI["FastAPI<br/>Python 3.10+"]
        Python["Python Modules<br/>Calculations<br/>LLM Integration<br/>Storage"]
    end
    
    subgraph External["External Services"]
        Claude["☁️ Anthropic<br/>Claude API"]
        Chroma["☁️ ChromaDB<br/>Vector Storage"]
    end
    
    subgraph Local["Local Storage"]
        SQLite["SQLite<br/>Development<br/>OR<br/>PostgreSQL<br/>Production"]
    end
    
    subgraph Deployment["Deployment"]
        Docker["🐳 Docker<br/>Backend Container<br/>Frontend Container"]
        Compose["Docker Compose<br/>Local Dev<br/>Production"]
    end
    
    Browser -->|HTTP| Angular
    Angular -->|REST/JSON| FastAPI
    FastAPI -->|Python Modules| Python
    Python -->|API Call| Claude
    Python -->|Semantic Search| Chroma
    Python -->|SQL| SQLite
    FastAPI -->|Build| Docker
    Docker -->|Orchestrate| Compose
    
    style Client fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#ecf0f1
    style Server fill:#27ae60,stroke:#1e8449,stroke-width:2px,color:#ecf0f1
    style External fill:#e67e22,stroke:#ca6f1e,stroke-width:2px,color:#ecf0f1
    style Local fill:#8e44ad,stroke:#6c3483,stroke-width:2px,color:#ecf0f1
    style Deployment fill:#16a085,stroke:#117a65,stroke-width:2px,color:#ecf0f1
    
    style Browser fill:#5dade2,stroke:#2874a6,stroke-width:1px,color:#ecf0f1
    style Angular fill:#5dade2,stroke:#2874a6,stroke-width:1px,color:#ecf0f1
    style FastAPI fill:#58d68d,stroke:#2d7659,stroke-width:1px,color:#ecf0f1
    style Python fill:#58d68d,stroke:#2d7659,stroke-width:1px,color:#ecf0f1
    style Claude fill:#d68910,stroke:#b06e0f,stroke-width:1px,color:#ecf0f1
    style Chroma fill:#d68910,stroke:#b06e0f,stroke-width:1px,color:#ecf0f1
    style SQLite fill:#9b59b6,stroke:#6c3483,stroke-width:1px,color:#ecf0f1
    style Docker fill:#1abc9c,stroke:#117a65,stroke-width:1px,color:#ecf0f1
    style Compose fill:#1abc9c,stroke:#117a65,stroke-width:1px,color:#ecf0f1
```

---

## 8. Phase Rollout

```mermaid
timeline
    title Project Development Phases
    
    section Phase 1 (MVP - Now)
        Single trade calculation ✅
        Ações + BDR support ✅
        Tax logic (15%, 20%) ✅
        Fee calculations ✅
        Basic API endpoints ✅
        
    section Phase 2 (Next)
        Database integration 📅
        Chat with Claude 📅
        ChromaDB seeding 📅
        Monthly summaries 📅
        Frontend polish 📅
        
    section Phase 3 (Future)
        Multi-agent system 🔮
        Derivatives support 🔮
        Stock lending 🔮
        Real-time prices 🔮
        Tax optimization 🔮
```

---

## 9. API Endpoint Overview

```mermaid
graph TB
    API["🛣️ FastAPI<br/>Base: /api"]
    
    API --> Trades["📊 /trades"]
    API --> Chat["💬 /chat"]
    API --> Calc["🧮 /calculations"]
    
    Trades --> T1["POST /process<br/>✅ Working<br/>Calculate single trade"]
    Trades --> T2["POST /batch<br/>⚠️ Incomplete<br/>Process multiple trades"]
    Trades --> T3["GET /history<br/>❌ Needs DB<br/>User trade history"]
    
    Chat --> C1["POST /message<br/>⚠️ Placeholder<br/>Chat with LLM"]
    Chat --> C2["GET /history<br/>❌ Needs DB<br/>Chat history"]
    
    Calc --> Ca1["GET /summary<br/>❌ Needs DB<br/>Monthly totals"]
    Calc --> Ca2["GET /darf<br/>⚠️ Placeholder<br/>Tax due info"]
    
    style T1 fill:#27ae60,stroke:#1e8449,stroke-width:1px,color:#ecf0f1
    style T2 fill:#f39c12,stroke:#d68910,stroke-width:1px,color:#ecf0f1
    style T3 fill:#c0392b,stroke:#922b21,stroke-width:1px,color:#ecf0f1
    style C1 fill:#f39c12,stroke:#d68910,stroke-width:1px,color:#ecf0f1
    style C2 fill:#c0392b,stroke:#922b21,stroke-width:1px,color:#ecf0f1
    style Ca1 fill:#c0392b,stroke:#922b21,stroke-width:1px,color:#ecf0f1
    style Ca2 fill:#f39c12,stroke:#d68910,stroke-width:1px,color:#ecf0f1
```

---

## Key Architectural Principles

| Principle | Implementation |
|-----------|-----------------|
| **Separation of Concerns** | API layer → Calculation layer → Storage layer |
| **LLM as Intelligence** | Haiku (parse), Sonnet (explain), Opus (complex tasks) |
| **Context-Aware** | ChromaDB provides regulatory context to LLM |
| **Type Safety** | Pydantic models for all request/response validation |
| **Modular Calculators** | Each asset type has dedicated calculator (extensible) |
| **Persistent Storage** | Database tracks portfolio for accurate average prices |
| **Stateless API** | Each request is independent; state in database |

---

## Security & Data Protection

```mermaid
graph LR
    User["👤 User"]
    
    Frontend["Frontend<br/>(HTTPS)"]
    
    Backend["Backend<br/>(Validated Input)"]
    
    Secrets[".env<br/>(Never in Git)"]
    
    Database["Database<br/>(SQL Injection<br/>Protection)"]
    
    LLM["LLM<br/>(API Key<br/>from Secrets)"]
    
    User -->|HTTPS| Frontend
    Frontend -->|Validated JSON| Backend
    Backend -->|Secure| Secrets
    Backend -->|Parameterized SQL| Database
    Secrets -->|API Key| LLM
    
    style User fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#ecf0f1
    style Frontend fill:#27ae60,stroke:#1e8449,stroke-width:2px,color:#ecf0f1
    style Backend fill:#8e44ad,stroke:#6c3483,stroke-width:2px,color:#ecf0f1
    style Secrets fill:#c0392b,stroke:#922b21,stroke-width:2px,color:#ecf0f1
    style Database fill:#e67e22,stroke:#ca6f1e,stroke-width:2px,color:#ecf0f1
    style LLM fill:#16a085,stroke:#117a65,stroke-width:2px,color:#ecf0f1
```

