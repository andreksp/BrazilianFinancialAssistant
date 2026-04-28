# Agent: Phase 2 — Backend API (FastAPI)

**Responsabilidade**: Expor Engine de Cálculo via REST API, integrar banco de dados  
**Duração**: 3-4 dias  
**Input**: Phase 1 (TaxEngine + Calculators)  
**Output**: API endpoints funcional + database persistence  

---

## Conhecimento de Negócio

### API Contract (FastAPI ↔ Frontend Angular)

A API é o "contrato" entre backend e frontend. Mudanças precisam ser coordenadas.

#### Endpoint 1: POST /api/trades/process

**Request**:
```json
{
  "ativo": "PETR4",
  "tipo_ativo": "acao",
  "tipo_operacao": "venda",
  "quantidade": 100,
  "preco_unitario": 25.50,
  "data_operacao": "2025-03-15",
  "corretora": "C6",
  "corretagem_percentual": 0.001,
  "corretagem_fixa": 0
}
```

**Response** (200 OK):
```json
{
  "ativo": "PETR4",
  "tipo_ativo": "acao",
  "quantidade": 100,
  "preco_unitario": 25.50,
  "data_operacao": "2025-03-15",
  "valor_financeiro": 2550.00,
  "ganho_prejuizo_bruto": 50.00,
  "taxas_totais": {
    "taxa_liquidacao": 0.70,
    "taxa_registro": 0.09,
    "emolumentos": 0.08,
    "corretagem": 2.55,
    "iss_sobre_corretagem": 0.13
  },
  "aliquota_aplicada": 0.15,
  "ir_devido": 7.50,
  "irrf_retido": 0.13,
  "isenção_aplicada": false,
  "ganho_prejuizo_liquido": 46.55,
  "valor_liquido": 2539.32,
  "tipo_operacao_classificacao": "swing",
  "mensagem": "Operação swing trade de PETR4: R$ 50,00 - IR devido: R$ 7,50"
}
```

**Business Logic**:
- Campo `valor_liquido`: Quanto o usuário recebe/paga após tudo
- Campo `mensagem`: Resumo amigável para o usuário
- `tipo_operacao_classificacao`: Inferido (não vem do usuário)

#### Endpoint 2: GET /api/calculations/summary

**Request**:
```
GET /api/calculations/summary?month=3&year=2025&user_id=user123
```

**Response** (200 OK):
```json
{
  "mes": 3,
  "ano": 2025,
  "ganho_swing_trade": 5000.00,
  "prejuizo_swing_trade": 1000.00,
  "ganho_day_trade": 1500.00,
  "prejuizo_day_trade": 200.00,
  "ir_swing_trade": 600.00,
  "ir_day_trade": 260.00,
  "irrf_retido_total": 850.00,
  "ir_total_devido": 860.00,
  "darf_vencimento": "2025-04-30"
}
```

**Business Logic**:
- Agregação de todas as operações do mês
- Separação de swing vs day trade
- Aplicação de compensação de prejuízos
- Cálculo de DARF (vencimento = último dia útil mês seguinte)

#### Endpoint 3: GET /api/calculations/darf

**Request**:
```
GET /api/calculations/darf?month=3&year=2025
```

**Response**:
```json
{
  "codigo_darf": "6015",
  "descricao": "Ganho operações bolsa - Pessoa Física",
  "mes": 3,
  "ano": 2025,
  "ir_devido": 860.00,
  "irrf_retido": 850.00,
  "valor_a_pagar": 10.00,
  "vencimento": "2025-04-30",
  "minimo_para_pagar": 10.00,
  "alerta": "Valor abaixo do mínimo (R$10) - acumular para próximo mês"
}
```

**Business Logic**:
- DARF é o comprovante de imposto a pagar
- Código 6015 = ganho em operações de bolsa (PF)
- `valor_a_pagar` = IR devido - IRRF retido
- Se < R$10, acumula (não precisa pagar agora)

---

## Database Schema

### Tabela: trades

```sql
CREATE TABLE trades (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    ativo VARCHAR(20) NOT NULL,
    tipo_ativo VARCHAR(20) NOT NULL,  -- acao, bdr, fii, opcao
    tipo_operacao VARCHAR(20) NOT NULL,  -- compra, venda
    quantidade DECIMAL(15, 2) NOT NULL,
    preco_unitario DECIMAL(15, 2) NOT NULL,
    data_operacao DATE NOT NULL,
    corretora VARCHAR(100),
    corretagem_percentual DECIMAL(5, 4),
    corretagem_fixa DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_trades_user_date ON trades(user_id, data_operacao);
```

**Business Logic**:
- `tipo_operacao`: Compra atualiza preço médio, venda gera IR
- `data_operacao`: Agrupa por mês para resumo mensal
- Salva ANTES do cálculo (para auditoria)

### Tabela: calculations

```sql
CREATE TABLE calculations (
    id UUID PRIMARY KEY,
    trade_id UUID NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    ganho_prejuizo_bruto DECIMAL(15, 2) NOT NULL,
    aliquota_aplicada DECIMAL(5, 4),
    ir_devido DECIMAL(15, 2),
    irrf_retido DECIMAL(15, 2),
    valor_liquido DECIMAL(15, 2),
    tipo_operacao_classificacao VARCHAR(20),  -- swing, day_trade
    created_at TIMESTAMP,
    
    FOREIGN KEY (trade_id) REFERENCES trades(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Business Logic**:
- Resultado do cálculo (imutável, auditável)
- Separação trade (input) vs calculation (output)

### Tabela: monthly_summaries

```sql
CREATE TABLE monthly_summaries (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    mes INT NOT NULL,
    ano INT NOT NULL,
    ganho_swing DECIMAL(15, 2) DEFAULT 0,
    prejuizo_swing DECIMAL(15, 2) DEFAULT 0,
    ganho_day DECIMAL(15, 2) DEFAULT 0,
    prejuizo_day DECIMAL(15, 2) DEFAULT 0,
    ir_total_devido DECIMAL(15, 2),
    irrf_retido DECIMAL(15, 2),
    darf_vencimento DATE,
    created_at TIMESTAMP,
    
    UNIQUE(user_id, mes, ano)
);
```

**Business Logic**:
- Cache de agregação (evita recalcular todo mês)
- `darf_vencimento` = último dia útil do mês seguinte

### Tabela: users (básico para MVP)

```sql
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Business Logic**:
- Suporte multi-usuário desde o início
- Isolamento de dados por `user_id`

---

## Tarefas de Implementação

### 1. SQLAlchemy Models
**Arquivo**: `backend/app/storage/models.py`

```python
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class TradeModel(Base):
    __tablename__ = "trades"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    ativo = Column(String(20), nullable=False)
    tipo_ativo = Column(String(20), nullable=False)
    tipo_operacao = Column(String(20), nullable=False)
    quantidade = Column(Numeric(15, 2), nullable=False)
    preco_unitario = Column(Numeric(15, 2), nullable=False)
    data_operacao = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_trades_user_date', 'user_id', 'data_operacao'),
    )

class CalculationModel(Base):
    __tablename__ = "calculations"
    id = Column(String, primary_key=True)
    trade_id = Column(String, ForeignKey("trades.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    ganho_prejuizo_bruto = Column(Numeric(15, 2), nullable=False)
    ir_devido = Column(Numeric(15, 2))
    irrf_retido = Column(Numeric(15, 2))
    valor_liquido = Column(Numeric(15, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Business Logic**:
- SQLAlchemy permite abstract DB (SQLite dev, PostgreSQL prod)
- Índices em `user_id, data_operacao` para queries rápidas
- Numeric type para evitar erros float

### 2. Database Connection
**Arquivo**: `backend/app/storage/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Business Logic**:
- `get_db()` é dependency injection para FastAPI
- SQLite single-thread → `check_same_thread=False`
- PostgreSQL não precisa

### 3. API Endpoint: Process Trade
**Arquivo**: `backend/app/api/trades.py`

```python
@router.post("/process", response_model=TaxCalculationResult)
async def process_trade(
    trade: TradeInput,
    db: Session = Depends(get_db),
    user_id: str = "user123"  # TODO: Get from auth
):
    """Process a trade and calculate taxes."""
    
    # 1. Buscar preço médio do portfólio (se venda)
    average_price = None
    if trade.tipo_operacao == OperationType.VENDA:
        # Buscar última compra não liquidada
        last_buy = db.query(TradeModel).filter(
            TradeModel.user_id == user_id,
            TradeModel.ativo == trade.ativo,
            TradeModel.tipo_operacao == OperationType.COMPRA
        ).order_by(TradeModel.data_operacao.desc()).first()
        
        if last_buy:
            average_price = float(last_buy.preco_unitario)
    
    # 2. Selecionar calculadora
    if trade.tipo_ativo == AssetType.ACAO:
        calculator = AcoesCalculator()
    elif trade.tipo_ativo == AssetType.BDR:
        calculator = BDRCalculator()
    # ... etc
    
    # 3. Calcular
    result = calculator.calculate_result(trade, average_price)
    
    # 4. Salvar trade em DB
    trade_model = TradeModel(
        id=str(uuid4()),
        user_id=user_id,
        ativo=trade.ativo,
        tipo_ativo=trade.tipo_ativo,
        tipo_operacao=trade.tipo_operacao,
        quantidade=trade.quantidade,
        preco_unitario=trade.preco_unitario,
        data_operacao=trade.data_operacao,
    )
    db.add(trade_model)
    
    # 5. Salvar cálculo
    calc_model = CalculationModel(
        id=str(uuid4()),
        trade_id=trade_model.id,
        user_id=user_id,
        ganho_prejuizo_bruto=result.ganho_prejuizo_bruto,
        ir_devido=result.ir_devido,
        irrf_retido=result.irrf_retido,
        valor_liquido=result.valor_liquido,
    )
    db.add(calc_model)
    db.commit()
    
    return result
```

**Business Logic**:
- Buscar preço médio do banco antes de calcular
- Salvar trade (input) e calculation (resultado) separados
- Auditoria: qualquer erro futura pode investigar trade original

### 4. API Endpoint: Monthly Summary
**Arquivo**: `backend/app/api/calculations.py`

```python
@router.get("/summary", response_model=MonthlyTaxSummary)
async def get_monthly_summary(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    user_id: str = "user123"
):
    """Get monthly tax summary."""
    
    # 1. Buscar todas as calculações do mês
    calculations = db.query(CalculationModel).join(TradeModel).filter(
        TradeModel.user_id == user_id,
        extract('month', TradeModel.data_operacao) == month,
        extract('year', TradeModel.data_operacao) == year,
    ).all()
    
    # 2. Agregar por tipo
    ganho_swing = sum(
        c.ganho_prejuizo_bruto 
        for c in calculations 
        if c.ganho_prejuizo_bruto > 0 and c.tipo_operacao_classificacao == "swing"
    )
    
    # ... similar para day trade, prejuízos
    
    # 3. Calcular IR total
    ir_total = ganho_swing * 0.15 + ganho_day * 0.20  # Simplificado
    
    # 4. Aplicar compensação de prejuízos
    # prejuizo_swing compensa ganho_swing
    
    # 5. Gerar DARF vencimento
    darf_date = self._calculate_darf_deadline(month, year)
    
    return MonthlyTaxSummary(
        mes=month,
        ano=year,
        ganho_swing_trade=ganho_swing,
        ir_total_devido=ir_total,
        darf_vencimento=darf_date,
    )
```

### 5. CORS Configuration
**Em**: `backend/app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # http://localhost:4200
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Business Logic**:
- Angular em localhost:4200 precisa chamar FastAPI em localhost:8000
- CORS permite cross-origin requests
- Necessário em dev, pode restringir em prod

### 6. Alembic Migrations (opcional Phase 1)
```bash
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

---

## Testes de Integração

### Test 1: POST /api/trades/process

```python
def test_process_trade(client, db):
    trade = TradeInput(
        ativo="PETR4",
        tipo_ativo="acao",
        tipo_operacao="venda",
        quantidade=100,
        preco_unitario=25.50,
        data_operacao=date(2025, 3, 15),
    )
    
    response = client.post("/api/trades/process", json=trade.model_dump())
    
    assert response.status_code == 200
    assert response.json()["valor_liquido"] > 0
    
    # Verificar que trade foi salvo
    trades = db.query(TradeModel).all()
    assert len(trades) == 1
```

### Test 2: Database Persistence

```python
def test_trade_persists_in_database(client, db):
    # Inserir trade
    client.post("/api/trades/process", json=trade_data)
    
    # Recuperar do banco
    trades = db.query(TradeModel).all()
    assert len(trades) == 1
    
    # Fazer novo request - preço médio deve vir do banco
    response = client.post("/api/trades/process", json=another_trade)
    # Verificar que usou PM do banco
```

---

## Validação (Checklist)

- [ ] SQLAlchemy models criados
- [ ] Database connection working (SQLite ou PostgreSQL)
- [ ] POST /api/trades/process salva em DB
- [ ] Preço médio recuperado do banco (para vendas)
- [ ] GET /api/calculations/summary agrega corretamente
- [ ] DARF vencimento calculado
- [ ] CORS configurado para Angular
- [ ] Testes de integração passando

---

## Notas

- **Database é crítica**: Sem persistência, qualquer restart perde dados
- **Índices importantes**: Queries por user_id e data_operacao são frequentes
- **Auth**: MVP usa user_id mockado, Phase 3 adiciona autenticação real
- **Migrations**: Usar Alembic para versionamento de schema (importante prod)
