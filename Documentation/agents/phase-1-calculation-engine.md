# Agent: Phase 1 — Engine de Cálculo (Equities)

**Responsabilidade**: Implementar lógica de cálculo para Ações, BDRs, FIIs e Opções  
**Duração**: 5-7 dias  
**Input**: Dados de operações (trade details)  
**Output**: Resultado completo com IR, taxas, IRRF, valor líquido  

---

## Conhecimento de Negócio — Regras Fiscais Brasileiras

### Alíquotas de IR por Ativo

| Ativo | Swing Trade | Day Trade | Isenção |
|-------|-------------|-----------|---------|
| **Ações** | 15% | 20% | R$20k/mês |
| **BDR** | 15% | 20% | R$20k/mês |
| **FII** | 20% | 20% | Não |
| **Opções** | 15%/20% | 15%/20% | Idem ação subjacente |

**Critical Rule**: Isenção R$20.000 aplica ao **total vendido no mês**, não por ativo individual.
- Se total vendido = R$23.000 → **perde isenção completamente** (não é proporcional)
- Afeta todos os trades do mês (não retroativo)

### IRRF (Imposto Retido na Fonte)
- **Swing**: 0,005% (dedo-duro) sobre valor financeiro
- **Day Trade**: 1% sobre valor financeiro
- Retido automaticamente pela corretora
- Abatido como crédito no IR a pagar (DARF)

### Preço Médio (Weighted Moving Average)

**Fórmula**:
```
PM = (Qtd_anterior × PM_anterior + Qtd_nova × Preço_novo) / (Qtd_anterior + Qtd_nova)
```

**Regras Críticas**:
- Vendas **NÃO** alteram o preço médio (apenas reduzem quantidade)
- Quando quantidade chega a zero → PM reseta
- Essencial para cálculo correto de ganho/prejuízo
- Aplicado **por ativo** (cada PETR4 tem seu PM)

### Exemplo de Cálculo de Preço Médio

```
Data 1: Compra 100 PETR4 @ R$25
  PM = 25.00, Qtd = 100

Data 2: Compra 50 PETR4 @ R$24
  PM = (100×25 + 50×24) / 150 = 24.67, Qtd = 150

Data 3: Venda 80 PETR4 @ R$26
  Ganho = (26 - 24.67) × 80 = R$106.40
  Qtd remanescente = 70, PM continua 24.67 ← CRÍTICO!
```

### Compensação de Prejuízos

| Base | Pode compensar? | Exemplo |
|------|-----------------|---------|
| Prejuízo DT compensa Ganho DT (mesmo ativo, mesmo mês) | ✅ Sim | Prejuízo -R$500 + Ganho +R$800 = +R$300 (IR sobre 300) |
| Prejuízo DT compensa Ganho ST | ❌ Não | Bases separadas |
| Prejuízo ST compensa Ganho ST (ativos diferentes) | ✅ Sim | Prejuízo VALE em ST + Ganho PETR em ST = compensação |
| Prejuízo ST carrega para mês seguinte | ✅ Sim | Acumula até compensação futura |

**Business Logic**: Day Trade e Swing Trade são **bases tributárias completamente separadas**.

### Taxas B3

Sobre cada operação:
- **Taxa de Liquidação**: 0,0275% (B3)
- **Taxa de Registro**: 0,0034% (ações) ou variável (derivativos)
- **Emolumentos**: 0,003% (receita do mercado)
- **Corretagem**: Variável por corretora (0,01% ~ 0,10%)
- **ISS**: 5% sobre corretagem (imposto municipal)

**Exemplo**:
```
Venda de 100 ações @ R$25 = R$2.500

Taxa Liquidação: 2500 × 0,000275 = R$0,69
Taxa Registro:   2500 × 0,000034 = R$0,09
Emolumentos:     2500 × 0,00003  = R$0,08
Corretagem:      2500 × 0,001    = R$2,50 (0,1%)
ISS:             2,50 × 0,05     = R$0,13
TOTAL FEES:                       ≈ R$3,49
```

### DARF (Imposto a Pagar)

- **Código**: 6015 (Pessoa Física - Ganho operações bolsa)
- **Vencimento**: Último dia útil do mês seguinte ao fato gerador
- **Exemplo**: Operações em março → DARF vence em 30 de abril
- **Mínimo**: R$10,00 (valores menores acumulam para próximo mês)
- **Cálculo**: IR Devido - IRRF Retido = Valor a Pagar

---

## Arquitetura de Cálculo

### Fluxo Principal

```
TradeInput (ativo, qtd, preço, data, etc)
    ↓
TaxEngine.add_trade()
    ↓
Seleciona Calculadora (AcoesCalculator, FIICalculator, etc)
    ↓
Calculator.calculate_result()
    ├── Calcula ganho/prejuízo (price - average_price) × qty
    ├── Determina tipo: swing vs day_trade
    ├── Aplica alíquota (15% ou 20%)
    ├── Aplica isenção (se elegível)
    ├── Calcula taxas B3
    ├── Calcula IRRF
    └── Retorna TaxCalculationResult
    ↓
TaxEngine armazena resultado e atualiza portfólio
    ↓
API retorna para frontend
```

### Classes Principais

#### BaseCalculator (Abstract)
Interface base para todas as calculadoras de ativo:
- `calculate_gain_loss()` — (preço_venda - PM) × quantidade
- `get_tax_rate()` — 15% ou 20%
- `get_irrf_rate()` — 0,005% ou 1%
- `calculate_result()` — Implementação completa

#### AcoesCalculator (implements BaseCalculator)
Cálculos específicos para Ações:
- Alíquota: 15% (swing) ou 20% (day)
- Isenção: R$20.000/mês
- IRRF: 0,005% (swing) ou 1% (day)
- Classificação: `is_day_trade()` método

#### TaxEngine
Orquestrador central:
- Mantém portfólio de posições (preço médio por ativo)
- Agrega resultados por mês/ano
- Calcula compensação de prejuízos
- Gera MonthlyTaxSummary (para DARF)
- Exporta relatórios

---

## Tarefas de Implementação

### 1. Pydantic Models
**Arquivo**: `backend/app/models/trade.py`

```python
class TradeInput(BaseModel):
    ativo: str                      # "PETR4"
    tipo_ativo: AssetType           # "acao", "bdr", "fii", "opcao"
    tipo_operacao: OperationType    # "compra", "venda"
    quantidade: float
    preco_unitario: float
    data_operacao: date
    corretora: Optional[str]
    corretagem_percentual: float    # 0.001 = 0,1%
    corretagem_fixa: float          # R$ fixo

class TaxCalculationResult(BaseModel):
    valor_financeiro: float
    ganho_prejuizo_bruto: float
    taxas_totais: FeesBreakdown
    aliquota_aplicada: float        # 0.15 ou 0.20
    ir_devido: float
    irrf_retido: float
    ganho_prejuizo_liquido: float
    valor_liquido: float
    tipo_operacao_classificacao: TradeOperationType
```

**Business Logic**:
- Decimal precision para valores (evitar erros float: 0.1 + 0.2 ≠ 0.3)
- Validação de limites (quantidade > 0, preço > 0)

### 2. Base Calculator
**Arquivo**: `backend/app/calculations/base.py`

```python
from abc import ABC, abstractmethod

class BaseCalculator(ABC):
    @abstractmethod
    def calculate_gain_loss(self, qty, purchase_price, sale_price) -> float:
        pass
    
    @abstractmethod
    def get_tax_rate(self, is_day_trade: bool) -> float:
        pass
    
    @abstractmethod
    def calculate_result(self, trade: TradeInput, average_price: float) -> TaxCalculationResult:
        pass
```

### 3. Ações Calculator
**Arquivo**: `backend/app/calculations/equity/acoes.py`

```python
class AcoesCalculator(BaseCalculator):
    SWING_RATE = 0.15
    DAY_RATE = 0.20
    EXEMPTION_LIMIT = 20000.0
    SWING_IRRF = 0.00005
    DAY_IRRF = 0.01
    
    def calculate_result(self, trade, average_price):
        # 1. Classificar: day_trade ou swing
        is_day = self.is_day_trade(trade)
        
        # 2. Calcular ganho/prejuízo
        ganho = (trade.preco_unitario - average_price) * trade.quantidade
        
        # 3. Determinar alíquota
        if is_day:
            aliquota = 0.20
        elif trade.valor_financeiro < 20000:
            aliquota = 0.0  # Isenção
        else:
            aliquota = 0.15
        
        # 4. Calcular IR
        ir = max(0, ganho) * aliquota
        
        # 5. Calcular IRRF
        irrf = trade.valor_financeiro * (self.DAY_IRRF if is_day else self.SWING_IRRF)
        
        # 6. Calcular taxas B3
        fees = calculate_b3_fees(trade)
        
        return TaxCalculationResult(...)
```

### 4. BDR, FII, Opções Calculators
**Pattern**: Copiar AcoesCalculator e ajustar apenas:
- **BDR**: Mesmas regras que Ações (15% swing, 20% day, isenção R$20k)
- **FII**: 20% fixo (sem isenção, sem compensação)
- **Opções**: Baseado na ação subjacente

### 5. B3 Fees
**Arquivo**: `backend/app/calculations/fees/b3_fees.py`

```python
def calculate_b3_fees(valor_financeiro, asset_type, trade) -> FeesBreakdown:
    taxa_liquidacao = valor_financeiro * 0.000275
    taxa_registro = valor_financeiro * 0.000034  # ações
    emolumentos = valor_financeiro * 0.00003
    corretagem = valor_financeiro * trade.corretagem_percentual + trade.corretagem_fixa
    iss = corretagem * 0.05
    
    return FeesBreakdown(
        taxa_liquidacao=taxa_liquidacao,
        taxa_registro=taxa_registro,
        emolumentos=emolumentos,
        corretagem=corretagem,
        iss_sobre_corretagem=iss,
    )
```

### 6. Tax Engine
**Arquivo**: `backend/app/calculations/taxes/ir_engine.py`

```python
class TaxEngine:
    def __init__(self):
        self.positions = {}  # {ativo: PortfolioPosition}
        self.monthly_results = {}  # {(mes, ano): [TaxCalculationResult]}
    
    def add_trade(self, trade, result):
        self._update_position(trade)  # Atualizar preço médio
        self._store_result(trade, result)
    
    def _update_position(self, trade):
        # Implementar weighted average formula
        # Só executa se trade.tipo_operacao == "compra"
        
    def get_monthly_summary(self, mes, ano) -> MonthlyTaxSummary:
        # Agregar resultados do mês
        # Separar swing vs day trade
        # Aplicar compensação de prejuízos
        # Calcular DARF vencimento
```

### 7. Testes Unitários
**Arquivo**: `backend/tests/test_acoes.py`

Cenários críticos (de research.md):

```python
def test_swing_trade_with_exemption():
    """R$20k exemption apply corretamente"""
    
def test_day_trade_no_exemption():
    """Day trade é sempre 20%, sem isenção"""
    
def test_loss_not_taxed():
    """Prejuízo resulta em IR = 0"""
    
def test_weighted_average_price():
    """Múltiplas compras atualizam PM corretamente"""
    
def test_irrf_calculation():
    """0,005% (swing) vs 1% (day) retido"""
```

---

## Validação (Checklist)

- [ ] Models Pydantic criados com validações
- [ ] BaseCalculator e AcoesCalculator implementados
- [ ] Cálculo de preço médio funcionando (teste com múltiplas compras)
- [ ] Isenção R$20.000 aplicada corretamente
- [ ] BDR, FII, Opções calculators implementados
- [ ] Taxas B3 detalhadas
- [ ] TaxEngine agregando resultados mensais
- [ ] Testes unitários: 90%+ cobertura
- [ ] Validação com dados reais (C6, XP, etc)

---

## Decisões de Design

### Por que não usar float?
Python floats têm erro de arredondamento:
```python
0.1 + 0.2  # 0.30000000000000004 (float)
```

**Solution**: Usar `Decimal` para valores monetários.

### Por que separar Day Trade e Swing Trade?
Bases tributárias completamente diferentes:
- Alíquota diferente
- Isenção só em swing
- Compensação de prejuízo restrita
- IRRF diferente

Misturar causaria bugs sérios.

### Por que weighted average por ativo?
Regra fiscal: PM é específico por ativo. Não há "PM global" de todas as ações.

---

## Notas

- **Phase 1 é crítica**: Cálculos incorretos = imposto errado
- **Testes com dados reais**: Validar contra C6, XP, Clear
- **Documentação de regulamentações**: Incluir referências Receita Federal
- **Precisão é prioridade 1**: Melhor lento e certo do que rápido e errado
