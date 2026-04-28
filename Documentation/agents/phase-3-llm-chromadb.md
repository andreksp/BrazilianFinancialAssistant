# Agent: Phase 3 — LLM + ChromaDB Integration

**Responsabilidade**: Integrar Claude API para parsing natural language, ChromaDB para RAG  
**Duração**: 4-5 dias  
**Input**: Phase 2 (API endpoints)  
**Output**: Chat endpoint funcional com IA  

---

## Conhecimento de Negócio

### Multimodal LLM Strategy

**Problem**: Usuário entra "Vendi 100 ações da PETR4 por R$25,50 em 15/03/2025"  
Precisa virar estruturado: `TradeInput(ativo="PETR4", quantidade=100, ...)`

**Solution**: Duas chamadas LLM otimizadas por custo-benefício:

#### Stage 1: Parse com Claude Haiku (Rápido, Barato)
- **Model**: `claude-haiku-4-5-20251001`
- **Task**: Extrair dados estruturados do texto
- **Latency**: ~500ms
- **Cost**: ~$0,001 por request
- **Prompt**: "Extraia os dados do trade para JSON"

#### Stage 2: Explain com Claude Sonnet (Qualidade)
- **Model**: `claude-sonnet-4-6-20250514`
- **Task**: Explicar resultado em português
- **Latency**: ~2-3s
- **Cost**: ~$0,01 por request
- **Prompt**: "Explique este cálculo de imposto em português"

**MVP**: Usar **apenas Haiku** no início (menos custo). Upgrade para Sonnet se qualidade insuficiente.

### ChromaDB for Regulatory Context (RAG)

**Problem**: LLM não tem contexto sobre regras IR brasileiras  
Pode gerar explicações incorretas ou alucinações

**Solution**: Retrieval-Augmented Generation (RAG)
1. Carregar regulamentações de `/backend/data/regulations/` em ChromaDB
2. User pergunta → buscar contexto relevante em ChromaDB
3. Passar contexto + pergunta para Claude
4. Claude responde com base em contexto real

**Exemplo**:
```
User: "Qual é a alíquota de IR para operação com ações?"
→ ChromaDB busca "aliquota ações"
→ Recupera: "Swing trade: 15%, Day trade: 20%"
→ Claude: "Para operações com ações... (resposta baseada em ChromaDB)"
```

### Prompt Engineering (PT-BR)

Prompts bem estruturados são críticos para qualidade. Incluem:
1. **Role**: "Você é um assistente financeiro..."
2. **Context**: Regras IR, taxas B3, DARF
3. **Instructions**: "Responda em português, formato JSON..."
4. **Examples**: Exemplos de input/output esperado

---

## Architecture: Chat Flow

```
User Message (PT-BR)
    ↓
Claude Haiku: Parse trade
    ├── Input: "Vendi 100 PETR4 por R$25,50..."
    └── Output: TradeInput JSON
    ↓
Validate Trade ← (Pydantic)
    ↓
TaxEngine.calculate()
    ↓
ChromaDB: Search relevant regulations
    ├── Query: "operação ações 15% 20%"
    └── Results: Top 3 relevant regulations
    ↓
Claude Sonnet: Explain result + regulations
    ├── Input: Calculation result + ChromaDB context
    └── Output: Explanation in Portuguese
    ↓
Response to User
```

---

## Tarefas de Implementação

### 1. Anthropic SDK Client
**Arquivo**: `backend/app/llm/claude_client.py`

```python
from anthropic import Anthropic
from app.core.config import settings

class ClaudeClient:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model_parser = settings.LLM_MODEL_PARSER
        self.model_explainer = settings.LLM_MODEL_EXPLAINER
    
    def parse_trade(self, user_message: str) -> Optional[TradeInput]:
        """
        Parse natural language to structured TradeInput.
        
        Example:
            Input: "Vendi 100 ações PETR4 a R$25,50 em 15/03/2025"
            Output: TradeInput(ativo="PETR4", quantidade=100, ...)
        """
        system_prompt = """Você é um assistente que extrai dados de operações de bolsa.
        
Extraia do texto do usuário:
- ativo (ticker, ex: PETR4)
- quantidade
- preço
- data
- tipo_operacao (compra ou venda)
- tipo_ativo (acao, bdr, fii, opcao)

Responda APENAS em JSON válido:
{
  "ativo": "PETR4",
  "tipo_ativo": "acao",
  "tipo_operacao": "venda",
  "quantidade": 100,
  "preco_unitario": 25.50,
  "data_operacao": "2025-03-15"
}

Se não conseguir extrair, responda:
{"erro": "Não consegui entender o trade"}
"""
        
        message = self.client.messages.create(
            model=self.model_parser,
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        # Parse response
        response_text = message.content[0].text
        
        try:
            data = json.loads(response_text)
            if "erro" in data:
                return None
            return TradeInput(**data)
        except (json.JSONDecodeError, ValidationError):
            return None
    
    def explain_calculation(
        self, 
        result: TaxCalculationResult,
        context: str = ""
    ) -> str:
        """
        Explain calculation result in Portuguese.
        
        Uses Claude Sonnet for better reasoning.
        """
        system_prompt = """Você é um assessor financeiro que explica resultados de cálculos.

Baseado no resultado fornecido:
- Ganho/prejuízo
- Imposto de renda
- Taxas
- Valor líquido

Explique em português de forma clara e didática.
Sempre cite valores em R$ com formatação correta (vírgula decimal).
Seja conciso (máximo 3 linhas).
"""
        
        user_message = f"""
Operação: {result.ativo}
Ganho/Prejuízo: R$ {result.ganho_prejuizo_bruto:,.2f}
IR Devido: R$ {result.ir_devido:,.2f}
IRRF Retido: R$ {result.irrf_retido:,.2f}
Valor Líquido: R$ {result.valor_liquido:,.2f}

{context}

Explique este resultado para o usuário.
"""
        
        message = self.client.messages.create(
            model=self.model_explainer,
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        return message.content[0].text
```

**Business Logic**:
- Prompts em português para melhor parsing
- JSON output para fácil parsing
- Fallback se JSON inválido

### 2. ChromaDB Client
**Arquivo**: `backend/app/vector_db/chroma_client.py`

```python
import chromadb
from app.core.config import settings

class ChromaDBClient:
    def __init__(self):
        """Initialize ChromaDB with persistent storage."""
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        
        # Create collections per asset type
        self.collection_geral = self.client.get_or_create_collection(
            name="regulacoes_geral",
            metadata={"description": "IR, DARF, taxas gerais"}
        )
        
        self.collection_acoes = self.client.get_or_create_collection(
            name="regulacoes_acoes",
            metadata={"description": "Regras específicas para ações"}
        )
        
        self.collection_derivativos = self.client.get_or_create_collection(
            name="regulacoes_derivativos",
            metadata={"description": "Regras para futuros, índices, etc"}
        )
    
    def add_regulation(
        self,
        title: str,
        content: str,
        asset_type: str = "geral",
        source: str = ""
    ):
        """Add regulation to ChromaDB."""
        if asset_type == "acoes":
            collection = self.collection_acoes
        elif asset_type == "derivativos":
            collection = self.collection_derivativos
        else:
            collection = self.collection_geral
        
        # Generate unique ID
        doc_id = f"{asset_type}_{hash(title) % 10000}"
        
        collection.add(
            documents=[content],
            metadatas=[{"title": title, "source": source}],
            ids=[doc_id],
        )
        
        logger.info(f"Added: {title}")
    
    def search_regulations(
        self,
        query: str,
        asset_type: str = "geral",
        top_k: int = 3
    ) -> str:
        """
        Search and return regulations as formatted text.
        
        Returns concatenated text for LLM context.
        """
        if asset_type == "acoes":
            collection = self.collection_acoes
        elif asset_type == "derivativos":
            collection = self.collection_derivativos
        else:
            collection = self.collection_geral
        
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        if not results or not results["documents"]:
            return ""
        
        # Format for LLM context
        context_lines = []
        for i, doc in enumerate(results["documents"][0], 1):
            metadata = results["metadatas"][0][i-1] if results["metadatas"] else {}
            title = metadata.get("title", "")
            context_lines.append(f"{i}. {title}:\n{doc}")
        
        return "\n\n".join(context_lines)
    
    def load_initial_regulations(self):
        """Load regulations from /backend/data/regulations/ on startup."""
        import os
        data_dir = "/app/backend/data/regulations" if os.path.exists("/app") else "./backend/data/regulations"
        
        if not os.path.exists(data_dir):
            logger.warning(f"Regulations directory not found: {data_dir}")
            return
        
        for filename in os.listdir(data_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(data_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Determine asset type from filename
                if "acao" in filename.lower():
                    asset_type = "acoes"
                elif "derivat" in filename.lower():
                    asset_type = "derivativos"
                else:
                    asset_type = "geral"
                
                self.add_regulation(
                    title=filename.replace(".txt", ""),
                    content=content,
                    asset_type=asset_type,
                    source=filename
                )
        
        logger.info("Regulations loaded into ChromaDB")
```

### 3. Chat Endpoint with LLM
**Arquivo**: `backend/app/api/chat.py`

```python
from app.llm.claude_client import get_claude_client
from app.vector_db.chroma_client import get_chroma_client

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat endpoint with LLM.
    
    Flow:
    1. Parse trade with Claude Haiku
    2. Validate trade
    3. Calculate with TaxEngine
    4. Get context from ChromaDB
    5. Explain with Claude Sonnet
    6. Save to ChatHistory
    """
    try:
        claude = get_claude_client()
        chroma = get_chroma_client()
        
        # Step 1: Parse
        trade = claude.parse_trade(request.message)
        
        if not trade:
            return ChatResponse(
                response="Desculpe, não consegui entender o trade. Use o formulário de entrada estruturada.",
                confidence=0.0
            )
        
        # Step 2: Validate & Calculate
        calculator = AcoesCalculator()  # TODO: Route to correct calculator
        result = calculator.calculate_result(trade)
        
        # Step 3: Get context
        context = chroma.search_regulations(
            f"{trade.tipo_ativo} {result.aliquota_aplicada * 100}%",
            asset_type="acoes" if trade.tipo_ativo == "acao" else "geral"
        )
        
        # Step 4: Explain
        explanation = claude.explain_calculation(result, context)
        
        # Step 5: Save to chat history (optional)
        # chat_history = ChatHistoryModel(...)
        # db.add(chat_history)
        # db.commit()
        
        return ChatResponse(
            response=explanation,
            trade_extracted=trade,
            calculation_result=result,
            confidence=0.95  # Parse foi bem-sucedido
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return ChatResponse(
            response="Erro ao processar sua mensagem.",
            confidence=0.0
        )
```

### 4. Prompts Module
**Arquivo**: `backend/app/llm/prompts.py`

Centralize todos os prompts para fácil manutenção:

```python
SYSTEM_PROMPT_PARSER = """
Você é um assistente que extrai dados de operações de bolsa brasileira.

Extraia do texto:
- ativo (ticker em maiúsculas)
- quantidade
- preço
- data (se fornecida)
- tipo_operacao (compra ou venda)
- tipo_ativo (acao, bdr, fii, opcao)

Responda APENAS em JSON válido, sem explicações.
"""

SYSTEM_PROMPT_EXPLAINER = """
Você é um assessor financeiro que explica cálculos de IR de forma clara.

Baseado nos dados fornecidos:
- Explique o ganho/prejuízo
- Cite a alíquota de imposto e por quê
- Mostre o valor de IR a pagar
- Mencione taxas operacionais
- Finalize com o valor líquido

Responda em português do Brasil.
Use formato claro, com números em R$ (vírgula decimal).
Seja conciso (máximo 3-4 frases).
"""
```

---

## Regulatory Documents

### Estrutura de `/backend/data/regulations/`

Criar arquivos TXT com regulamentações:

#### `ir_acoes.txt`
```
Alíquota de Imposto de Renda para Ações

SWING TRADE (compra e venda em dias diferentes):
- Alíquota: 15%
- Isenção: Vendas mensais até R$20.000
- IRRF: 0,005% (dedo-duro)

DAY TRADE (compra e venda no mesmo dia):
- Alíquota: 20% (sem isenção)
- IRRF: 1%

Referência: Receita Federal - Ganho Capital
```

#### `darf_guide.txt`
```
DARF - Darf de Imposto de Renda Retido na Fonte

Código: 6015 (Pessoa Física - Ganho operações bolsa)
Vencimento: Último dia útil do mês seguinte
Mínimo: R$10,00 (valores menores acumulam)
```

#### `b3_fees.txt`
```
Tabela de Taxas - B3

Taxa de Liquidação: 0,0275% sobre valor financeiro
Taxa de Registro: 0,0034% (ações)
Emolumentos: 0,003%
ISS: 5% sobre corretagem (imposto municipal)
```

---

## Testes

### Test 1: Parse Trade

```python
def test_parse_trade():
    claude = ClaudeClient()
    result = claude.parse_trade("Vendi 100 ações PETR4 por R$25,50 em 15/03/2025")
    
    assert result is not None
    assert result.ativo == "PETR4"
    assert result.quantidade == 100
    assert result.tipo_operacao == "venda"
```

### Test 2: ChromaDB Search

```python
def test_chroma_search():
    chroma = ChromaDBClient()
    chroma.load_initial_regulations()
    
    context = chroma.search_regulations("aliquota ações", asset_type="acoes")
    assert "15%" in context
    assert "20%" in context
```

### Test 3: Chat Endpoint

```python
def test_chat_endpoint(client):
    response = client.post("/api/chat/message", json={
        "message": "Vendi 100 PETR4 a R$25,50"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["trade_extracted"] is not None
    assert data["calculation_result"] is not None
    assert data["response"]  # Explanation in PT-BR
```

---

## Prompt Caching (Optional Optimization)

Para reduzir custos (~90%) com regulamentações estáticas:

```python
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1000,
    system=[
        {
            "type": "text",
            "text": "Você é um assessor financeiro..."
        },
        {
            "type": "text",
            "text": f"Regulamentações:\n{all_regulations}",
            "cache_control": {"type": "ephemeral"}  # Cache para 5 min
        }
    ],
    messages=[{"role": "user", "content": user_message}]
)
```

---

## Validação (Checklist)

- [ ] Anthropic SDK integrado
- [ ] Claude Haiku parsing trades corretamente
- [ ] Claude Sonnet explicando resultados em PT-BR
- [ ] ChromaDB armazenando regulamentações
- [ ] Busca semântica funcionando
- [ ] POST /api/chat/message end-to-end
- [ ] Testes unitários + integração
- [ ] Prompt caching (opcional, otimização)

---

## Notas

- **LLM não é perfeito**: Fallback para formulário estruturado
- **Confidence score**: Indicar ao usuário se o parsing foi seguro (>0.9)
- **Custo**: Haiku ~100x mais barato que Sonnet, usar para parsing
- **Latência**: 500ms Haiku + 2s Sonnet = 2.5s total (aceitável)
- **Regulamentações**: Manter em `/backend/data/` e versionadas em git
