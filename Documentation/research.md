# Research: Brazilian Financial Market Rules & Technical Decisions

**Data**: 2026-04-27  
**Projeto**: Brazilian Financial Assistant (TCC)  
**Fase**: Planning & Research

---

## 1. Regras Fiscais Brasileiras (Imposto de Renda)

### Alíquotas e Isenções por Tipo de Ativo

| Ativo | Tipo de Operação | Alíquota | Isenção | IRRF (Dedo-Duro) |
|-------|------------------|----------|---------|-----------------|
| **Ações** | Swing Trade | 15% | Vendas ≤ R$20.000/mês | 0,005% |
| **Ações** | Day Trade | 20% | Não há | 1% |
| **BDR** | Swing Trade | 15% | Vendas ≤ R$20.000/mês | 0,005% |
| **BDR** | Day Trade | 20% | Não há | 1% |
| **FII (Fundos Imobiliários)** | Swing + Day Trade | 20% | Não há (PF) | 0,005% / 1% |
| **Opções de Ações** | Exercício (compra) | 15% / 20% | Idem Ações | Proporcional |
| **Opções de Ações** | Exercício (venda) | 15% / 20% | Idem Ações | Proporcional |
| **Futuros (Dólar)** | Swing Trade | 15% | Não há | 1% |
| **Futuros (Dólar)** | Day Trade | 20% | Não há | 1% |
| **Futuros (Índice)** | Swing Trade | 15% | Não há | 1% |
| **Futuros (Índice)** | Day Trade | 20% | Não há | 1% |

### Observações Fiscais Críticas

1. **Isenção de R$20.000**
   - Válida **apenas para swing trade** de ações, BDRs
   - Cálculo: Soma de todas as vendas no mês (não por ativo individual)
   - Se ultrapassar R$20.000, **toda a operação é tributada** (não apenas o excesso)
   - **Ação executada**: Sempre calcular e exibir cenário com/sem isenção

2. **Day Trade vs Swing Trade**
   - **Day Trade**: Compra E venda do mesmo ativo no mesmo dia de pregão
   - **Swing Trade**: Qualquer outra operação (compra e venda em dias diferentes)
   - Classificação crítica: afeta alíquota (20% vs 15%) e isenção

3. **IRRF (Imposto Retido na Fonte)**
   - "Dedo-duro": 0,005% retido em operações normais (enviado à Receita Federal automaticamente)
   - 1% retido em day trades
   - Registrado nos extratos bancários/corretoras
   - Crédito automático: abatido do IR a pagar (DARF)

4. **Preço Médio (Média Móvel Ponderada)**
   - Fórmula: `PM = (Qtd_anterior × PM_anterior + Qtd_nova × Preço_novo) / (Qtd_anterior + Qtd_nova)`
   - Vendas NÃO alteram o preço médio (apenas reduzem quantidade)
   - Essencial para cálculo correto de ganho/prejuízo
   - Reseta a zero quando quantidade chega a zero

5. **Ganho/Prejuízo em Vendas**
   - Ganho = (Preço_venda - PM) × Quantidade_vendida
   - Prejuízo = negativo
   - Base para cálculo de IR devido

### Regras de Compensação e Prejuízo

| Cenário | Compensação? | Detalhes |
|---------|--------------|----------|
| Prejuízo DT compensa Ganho DT (mesmo ativo, mesmo mês) | ✅ Sim | Same-month, same-asset compensation |
| Prejuízo DT compensa Ganho ST (mesmo ativo) | ❌ Não | Day Trade e Swing Trade = bases separadas |
| Prejuízo ST (ativo A) compensa Ganho ST (ativo B) | ✅ Sim | Qualquer ativo, mesmo mês |
| Prejuízo ST carrega para próximos meses | ✅ Sim | Acumula até compensação futura |
| Prejuízo DT carrega para próximo mês | ❌ Não | Restrições de portaria (pode variar) |

**Ação executada**: Implementar base de dados separada para Day Trade e Swing Trade. Ao exibir resultado, mostrar:
- Ganho/Prejuízo por categoria
- Compensações realizadas (mesmo mês)
- Saldo arrastável (prejuízo ST pendente)

---

## 2. Taxas e Custos Operacionais (B3 & Corretoras)

### Taxa de Liquidação (B3)

| Componente | Taxa | Sobre | Observação |
|-----------|------|-------|-----------|
| Taxa de Liquidação | 0,0275% | Valor financeiro | Aplica a todos os trades |
| Taxa de Registro (Ações) | 0,0034% | Valor financeiro | Custa entre R$0,50 ~ R$3,00 por operação |
| Taxa de Registro (Opções) | Variável | Valor financeiro | Mais caro que ações |
| Emolumentos (Ações) | 0,003% | Valor financeiro | Receita do mercado |
| Emolumentos (Derivativos) | 0,003% ~ 0,01% | Valor financeiro | Varia por tipo |

### Corretagem

| Corretora | Modelo | Valor Típico |
|-----------|--------|-------------|
| Corretoras Varejo | % do contrato | 0,04% ~ 0,10% |
| Corretoras com desconto | Fixo + % ou flat | R$10 ~ R$50 + % |
| Corretoras Premium | Negotiable | Pode ser 0,01% ~ 0,05% |

**Ação executada**: 
- Armazenar corretagem como **configurável por corretora**
- Exibir breakdown de taxas no resultado (liquidação, registro, emolumentos, corretagem)
- Permitir ajustes para "what-if" scenarios

### ISS sobre Corretagem

- **ISS**: 5% sobre o valor da corretagem (imposto municipal)
- **Quem paga**: Pessoa física pode deduzir, empresa abate como custo
- **Cálculo**: ISS = Corretagem × 5%

**Ação executada**: Incluir ISS automaticamente no cálculo de custos totais.

---

## 3. Cálculo do DARF (Imposto)

### Informações Básicas

| Campo | Valor |
|-------|-------|
| **Código DARF** | 6015 (Pessoa Física - Ganho Operações de Bolsa) |
| **Prazo de Pagamento** | Último dia útil do mês seguinte ao fato gerador |
| **Valor Mínimo** | R$10,00 (valores menores acumulam para próximo mês) |
| **Juros** | 1% ao mês + SELIC se pago atrasado |
| **Multa** | 20% + 0,33% ao dia se pago atrasado |

### Exemplo de Cronograma

- **Operação em março** → DARF vence em 30 de abril
- **Operação em abril** → DARF vence em 31 de maio
- **Valor < R$10** → Acumula e paga com próximo mês que ultrapassar R$10

**Ação executada**:
- Calcular IR mensal de forma faseada (por mês de operação)
- Exibir vencimento do DARF por mês
- Alertar se valor < R$10 (acumular para próximo mês)

---

## 4. Decisões Técnicas

### Arquitetura LLM

| Decisão | Escolha | Motivo | Trade-offs |
|---------|---------|--------|-----------|
| **Modelo de Parsing** | Claude Haiku 4.5 | Custo baixo, speed bom | Menos inteligência vs Sonnet |
| **Modelo de Raciocínio** | Claude Sonnet 4.6 | Melhor compreensão de contexto | Mais caro que Haiku |
| **Strategy** | Haiku para parsing + Sonnet para explicação | Otimizado custo-qualidade | Duas chamadas API |
| **Prompt Caching** | Ativar para regulamentações (static) | Reduz latência e custo | Requer setup inicial |

### Vector Database (ChromaDB)

| Aspecto | Decisão | Motivo |
|--------|---------|--------|
| **DB Vetorial** | ChromaDB local | Sem infra externa, fast retrieval, ótimo para TCC |
| **Embedding Model** | all-MiniLM-L6-v2 (HuggingFace) | Open-source, nenhuma dependência paga |
| **Persistência** | SQLite + JSON (data/) | Reprodutível, versionável, sem docker volume complexo |
| **Seed Data** | Documentos de `/backend/data/regulations/` | Versionado em git |
| **Retrieval Strategy** | Semantic search + keyword fallback | Robusto para português |

### Banco de Dados

| Contexto | Escolha | Motivo |
|---------|---------|--------|
| **Desenvolvimento Local** | SQLite3 | Sem setup, arquivo único, SQL padrão |
| **Produção (Cloud)** | PostgreSQL | Robusto, escalável, JSON support (JSONB) |
| **ORM** | SQLAlchemy | Type-safe, migrations com Alembic, universal |
| **Migrations** | Alembic | Versionável, reversível, standard em FastAPI |

### Backend

| Escolha | Motivo |
|--------|--------|
| **Language** | Python 3.11 | Type hints forte, ecosystem ML/data robusto |
| **Framework** | FastAPI | Async nativo, auto-docs OpenAPI, Pydantic integrado |
| **Task Queue** (opcional, Fase 2) | Celery + Redis | Para processamentos longos (LLM expensive calls) |
| **Logging** | Python logging + structlog | Estruturado, rastreável em cloud |
| **Test Framework** | pytest + hypothesis (property-based) | Robusto para cálculos financeiros |

### Frontend

| Escolha | Motivo |
|--------|--------|
| **Framework** | Angular 17 | Standalone components, signals, moderno, Material integrado |
| **UI Components** | Angular Material 17 | Design consistente, a11y built-in |
| **State Management** | Signals (Angular 14+) | Reatividade simples, sem Redux overhead |
| **HTTP Client** | Angular HttpClient + Interceptors | CORS + auth tokens automáticos |
| **Locale** | ngx-translate (PT-BR) | Vírgula decimal, DD/MM/YYYY automático |
| **Charts** | Chart.js ou ngx-charts | Visualização de evolution de saldos/impostos |

### Containerização

| Escolha | Uso |
|--------|-----|
| **Docker Compose (dev)** | Hot-reload, mount volumes para source |
| **Docker Compose (prod)** | Versão estável, sem volumes, env vars |
| **Network** | backend:8000, frontend:80 (via nginx), ChromaDB internal |
| **Volumes (dev)** | `./backend:/app/backend`, `./frontend:/app/frontend` |
| **Volumes (prod)** | ChromaDB persistent volume (`chroma_data/`) |

### Package Management

| Tool | Uso |
|-----|-----|
| **Poetry** (Backend) | `poetry.lock` garantia reproducible builds |
| **npm** (Frontend) | `package-lock.json` standard Angular |
| **Docker** | Both: `pip` + `npm ci` (não install) em prod |

---

## 5. Validação de Cenários Críticos

### Cenário 1: Isenção de R$20.000 — Edge Case

```
Mês: Março/2025
Operação 1: Venda 100 ações PETR4 por R$15.000 (ganho R$1.000) → dentro do limite
Operação 2: Venda 50 ações VALE3 por R$8.000 (ganho R$500) → total R$23.000 > R$20.000

Cálculo CORRETO:
- Total vendido = R$23.000 (acima de R$20.000)
- Isenção NÃO se aplica
- IR = (R$1.000 + R$500) × 15% = R$225

Cálculo ERRADO (armadilha comum):
- IR = (R$1.000) × 0% + (R$500) × 15% = R$75 ← ERRADO

**Ação executada**: Teste unitário deve validar esse cenário.
```

### Cenário 2: Preço Médio com Múltiplas Compras

```
Data 1: Compra 100 ações PETR4 a R$25/ação → PM = R$25
Data 2: Compra 50 ações PETR4 a R$24/ação
        PM = (100 × 25 + 50 × 24) / (100 + 50) = (2500 + 1200) / 150 = 24.67

Data 3: Venda 80 ações PETR4 a R$26/ação
        Ganho = (26 - 24.67) × 80 = 1.33 × 80 = R$106.40
        Qtd remanescente = 150 - 80 = 70 ações (PM continua 24.67)

Date 4: Venda 70 ações PETR4 a R$27/ação
        Ganho = (27 - 24.67) × 70 = 2.33 × 70 = R$163.10
        
Total IR = (106.40 + 163.10) × 15% = R$40.58 (se dentro de R$20k isenção)

**Ação executada**: Implementar testes com múltiplas compras + vendas parciais.
```

### Cenário 3: Day Trade x Swing Trade — Mesma Ação

```
Mês: Abril/2025
DT 1: Compra 100 ITUB4 a R$28, vende no mesmo dia a R$28.50
      Ganho DT = R$50 (alíquota 20%) → IR = R$10

ST 1: Compra 50 ITUB4 a R$28.50 (compra separada no dia anterior)
      Vende 1 semana depois a R$29
      Ganho ST = R$25 (alíquota 15%) → IR = R$3.75

Total IR = R$10 + R$3.75 = R$13.75
(Ganho DT NÃO compensa prejuízo ST, bases são separadas)

**Ação executada**: Estrutura de dados distingue day_trades[] e swing_trades[].
```

---

## 6. Referências Oficiais

### Regulamentações Brasileiras

1. **Receita Federal — IR sobre Ganho de Capital**
   - Portaria MF: Normas para cálculo de IR
   - Isenção R$20.000: Instrução Normativa SRF nº 208/2002
   - DARF 6015: Código oficial para PF

2. **B3 (Bolsa de Valores)**
   - Tabela de Taxas: https://www.b3.com.br/pt_br/b3/solucoes-para-você/investidor/duvidas-frequentes/
   - Regulamentação de Derivativos
   - Liquidação D+2 (ações), D+1 (derivativos)

3. **Corretoras Brasileiras**
   - C6, XP Investimentos, Clear, Nubank — cobram corretagem variável
   - Necessário parametrizar no sistema

---

## 7. Roadmap de Implementação

### Ordem de Prioridade (Phase 1)

1. **Ações (Swing + Day Trade)** — 40% do volume esperado de usuários
2. **BDR** — Similar a ações, 20% do volume
3. **FII** — Simpler (sem isenção), 20% do volume
4. **Opções de Ações** — Mais complexo, 15% do volume
5. **Derivativos/Futuros** — Phase 2 (complexidade maior)

---

## 8. Notas de Desenvolvimento

- **Precisão**: Usar `Decimal` (não `float`) para valores monetários — evitar erros de arredondamento
- **Locale**: PT-BR com vírgula decimal, datas DD/MM/YYYY
- **Testes**: Criar cenários reais (operações de plataformas reais: C6, XP, etc.)
- **Validação**: Comparar resultados com ferramentas de mercado (Brapi, Yahoo Finance para preços históricos)
- **Compliance**: Todos os cálculos devem passar por validação manual (usuário final é responsável pela declaração)

---

**Última atualização**: 2026-04-27
