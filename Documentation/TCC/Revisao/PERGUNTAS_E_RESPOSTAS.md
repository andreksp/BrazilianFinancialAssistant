# Perguntas e Respostas — Assistente Financeiro Brasileiro (TCC)

Documento de apoio à defesa, gerado a partir da versão mais recente do código (commit `148e9f7`, mais o ajuste de `uvicorn` em `requirements.txt`) e do `manuscrito.md` atual (com a correção de BDR e a Seção 7.5 de verificação da integração MCP). Cada resposta reflete o que está implementado e escrito hoje — não o que se planeja fazer.

Convenção: 🟢 pergunta factual (resposta objetiva); 🟡 pergunta de julgamento/justificativa (resposta é uma posição defensável, não um fato único).

---

## PARTE 1 — SOBRE O CÓDIGO

### 1. Arquitetura geral

**🟢 Quais são as camadas da aplicação?**
Interface Angular → API FastAPI (`backend/app/api/`) → orquestrador multiagente (`backend/app/agents/`) → gateway MCP (`backend/app/mcp_gateway.py`) → servidor MCP (`mcp_server/runtime_server.py`) → calculadoras Python (`backend/app/calculations/`) → persistência SQLAlchemy/SQLite e base vetorial ChromaDB.

**🟢 O sistema é uma função Python, uma rota REST ou uma ferramenta MCP?**
É os três, em pontos diferentes: as calculadoras são funções/classes Python puras; `/api/trades/process`, `/api/chat/`, `/api/calculations/*` são rotas REST expostas pelo FastAPI; `fee_policy` e `calculate_trade` são ferramentas MCP expostas por `mcp_server/runtime_server.py` e chamadas pelo gateway via protocolo stdio real. A monografia é explícita em não confundir essas três coisas (Seção 2.4).

**🟡 Por que usar MCP em vez de simplesmente chamar a função da calculadora direto do backend?**
Justificativa defensável: separar o processo que executa o cálculo do processo que fala com o usuário/LLM cria uma fronteira de contrato (schema JSON) e uma trilha de auditoria (`tools/call`) que uma chamada de função in-process não tem — qualquer cliente MCP futuro (não só este backend) poderia reutilizar as mesmas ferramentas. O custo é real e documentado: cada cálculo abre e fecha um subprocesso Python (latência extra, ~0,3–0,5s medidos localmente) e, no caminho síncrono do chat, chega a bloquear o event loop inteiro durante essa janela (ver Seção 7.5 do manuscrito e o achado de `test_concurrency_eventloop.py`). Não é uma escolha isenta de custo — é uma troca deliberada de simplicidade por desacoplamento, com uma limitação de desempenho conhecida e não corrigida.

**🟢 O LLM decide quais ferramentas MCP chamar?**
Não. O código do backend decide, depois de já ter interpretado a operação — não é function calling autônomo do modelo. Isso está explícito no manuscrito (Seção 5.8): "A seleção é determinada pelo código após a interpretação da operação, não por escolha autônoma de ferramentas pelo LLM."

**🟢 Existem dois servidores MCP no repositório — por quê?**
Sim. `mcp_server/server.py` é o servidor legado (ferramentas `get_tax_rules`, `get_fee_structure`, `example_calculation`, `get_regulation`, `validate_calculation`), criado como apoio de desenvolvimento e não integrado ao fluxo real. `mcp_server/runtime_server.py` é o servidor novo, com apenas duas ferramentas (`fee_policy`, `calculate_trade`), que é o único efetivamente chamado pelo backend em produção.

### 2. Modelo de dados e calculadoras

**🟢 Que campos o `TradeInput` exige que não existiam antes da revisão?**
`total_vendas_mes`, `preco_medio_informado`, `custos_operacao`, `irrf_informado`, `prazo_dias` (só empréstimo), `classificacao` (swing/day_trade, declarada pelo usuário, não detectada automaticamente) e `exchange_estrangeira` (só cripto).

**🟢 Por que a ausência de custo médio agora gera erro em vez de assumir ganho zero?**
Porque assumir ganho zero silenciosamente produziria um IR de R$0 indistinguível de uma isenção real — um erro de dado viraria um erro de cálculo sem aviso nenhum ao usuário. A decisão de projeto foi: sem dado suficiente, recusar o cálculo (`ValueError`) e não persistir a venda, em vez de gerar um número que parece correto mas não é. Isso está coberto por `test_revision_safety.py` e pela ferramenta `calculate_trade` do servidor MCP (`math.isfinite(cost) and cost > 0`).

**🟢 Qual é a diferença de tratamento entre Ações/BDR e FII/Opções nesse aspecto?**
`AcoesCalculator` e `BDRCalculator` têm a guarda de custo médio implementada na própria classe (levantam `ValueError`). `FIICalculator` e `OpcoesCalculator` **não têm** — ainda usam `pm = average_price or trade.preco_unitario`, que assume ganho zero silenciosamente se chamadas isoladamente. Isso só não afeta o usuário final porque o gateway MCP intercepta e recusa custo ausente/não-positivo para todo tipo de ativo antes de chamar qualquer calculadora. É uma dívida técnica documentada (manuscrito, Seção 7.5), não uma falha ativa no caminho real.

**🟢 A isenção de R$20.000 para BDR: como isso mudou entre commits?**
Na correção original desta sessão (commit `148e9f7`), `BDRCalculator` foi corrigido para exigir `total_vendas_mes` e recusar sem ele — mas uma regressão foi introduzida depois (fora desta sessão): mesmo com 88 testes passando, um caso de verificação manual (venda de 10 BDRs AAPL34, ganho de R$1.000, sem isenção aplicável) retornava IR = R$0 em vez de R$150 (15%). Foi corrigida depois, e a suíte ampliada para 94 testes. Isso é registrado explicitamente no manuscrito como um alerta: "aprovação da suíte não constitui validação tributária independente" — 88/88 verde não provou a ausência desse bug.

**🟢 Como funciona a tabela progressiva de cripto (`progressive_tax`)?**
Aplica cada alíquota apenas à fatia do ganho dentro da respectiva faixa (marginal), não a maior alíquota sobre o ganho inteiro: 15% até R$5 milhões, 17,5% de R$5-10M, 20% de R$10-30M, 22,5% acima. Um ganho de R$6 milhões resulta em R$750 mil (15% de R$5M) + R$175 mil (17,5% de R$1M) = R$925 mil — verificado em `test_progressive_slices` e no caso `cripto_nacional_tributado`/`cripto_progressivo` do relatório de validação MCP.

**🟢 Qual é a diferença entre cripto nacional e cripto no exterior no código?**
Nacional: isenção de R$35.000/mês (soma de todas as alienações, inclusive permutas cripto-cripto), acima disso tabela progressiva. Exterior (`exchange_estrangeira=True`): a calculadora **recusa** calcular (`ValueError`, mensagem menciona "anual") — a lógica do sistema cobre apenas o regime nacional mensal; o regime do exterior (Lei 14.754/2023, apuração anual a 15% fixo) está fora do escopo do motor implementado.

**🟢 Os multiplicadores de WIN e WDO estão certos?**
WIN: 1 ponto = R$0,20 por contrato. WDO: 1 ponto = R$10,00 por contrato. Ambos aplicados tanto no ganho quanto no valor financeiro nocional. Verificado em `test_futuros.py` e nos casos `futuro_win`/`futuro_wdo` do relatório de validação MCP (100 pontos de ganho no WIN = R$14,62 de IR sobre R$100 de ganho a 15%, líquido de custos).

**🟢 O que acontece se eu não informar o prazo do empréstimo de ações?**
`EmprestimoCalculator.calculate_result` levanta `ValueError` mencionando "prazo" — não assume mais a faixa mais conservadora (22,5%) como a versão original fazia. Essa mudança de contrato foi deliberada: presumir um prazo poderia sub ou superestimar a retenção sem o usuário perceber.

**🟢 Por que o campo `ganho_prejuizo_liquido` às vezes é chamado de "líquido" mas não subtrai o IR?**
Porque, por definição no código, `ganho_prejuizo_liquido = ganho_bruto - custos/taxas`, **não** menos o imposto de renda. Isso ficou evidente como um problema real na Seção 7.5 do manuscrito: numa resposta de chat real, o Sonnet rotulou R$498,14 (= R$500 de ganho − R$1,86 de custos, sem descontar o IR de R$100) como "ganho líquido", e um leitor comum entenderia "líquido" como já descontado o imposto (o que daria R$398,14). É uma ambiguidade de nomenclatura entre o campo estruturado e a linguagem natural gerada — registrada como achado, não corrigida.

### 3. Integração MCP (detalhes de implementação)

**🟢 Qual SDK MCP e qual transporte são usados?**
`mcp==1.28.0`, transporte stdio. O backend inicia um subprocesso com o mesmo interpretador Python (`sys.executable`) executando `mcp_server/runtime_server.py`, chama `initialize`, depois `tools/call` para `fee_policy` e `calculate_trade`, e fecha a sessão. Cada cálculo abre e fecha uma sessão nova (não há sessão persistente/pool).

**🟢 Qual é o timeout do gateway?**
30 segundos globais (`asyncio.wait_for(invoke(), timeout=30)` em `mcp_gateway.py`). Qualquer exceção (timeout incluído) é convertida em `ValueError` genérico antes de subir ao chamador — nunca há fallback para cálculo direto.

**🟢 O que acontece se o servidor MCP não existir ou travar?**
Se o arquivo do servidor não existir, ou o subprocesso falhar ao iniciar, ou a resposta vier com schema inválido, o gateway propaga um `ValueError` ("MCP indisponível ou resposta inválida; nenhum cálculo local alternativo foi executado"). Testado explicitamente em `test_mcp_runtime.py::test_transport_failure_has_no_fallback` e nos scripts de validação de 16/09/2026.

**🟢 O cálculo via MCP dá o mesmo resultado que chamar a calculadora direto?**
Sim, em todos os 10 casos testados (todas as 8 categorias de ativo, cobrindo os campos comparados: ganho bruto, imposto, retenção, alíquota e isenção) — ver `comparacao_mcp_vs_direto.json`. Isso é esperado por construção: `runtime_server.py` importa e reutiliza as mesmas classes de `backend/app/calculations/`, não reimplementa fórmulas.

**🟢 O caminho web (rota HTTP) chama a calculadora diretamente em algum lugar?**
Não no fluxo de execução real. `backend/app/api/trades.py` ainda importa as classes de calculadora, mas só para montar um dicionário `_CALCULATORS` usado como validação de "tipo de ativo suportado" (`_CALCULATORS.get(tipo_ativo) is None` → HTTP 400) — nunca instancia nem chama `.calculate_result()`. Nos agentes especialistas (`acoes_agent.py` etc.), o método `get_calculator()` ainda importa e instancia as calculadoras (para satisfazer o contrato abstrato de `BaseAgent`), mas **não é mais chamado** em lugar nenhum — é código morto pós-migração para MCP.

**🟢 Existe algum problema de concorrência conhecido na integração MCP?**
Sim, um real e não corrigido: a rota `/api/chat/` é `async def` mas chama `Orchestrator.process(...)` de forma síncrona (sem `await`), que desce até `base_agent.py` chamando o wrapper **síncrono** `gateway.calculate_via_mcp()` direto, sem isolamento de thread. Um teste reproduzindo esse padrão exato mediu bloqueio do event loop durante praticamente 100% da duração da chamada MCP (~0,37s). Isso significa que, com um único worker uvicorn (configuração padrão), cada cálculo disparado pelo chat trava todas as outras requisições concorrentes nesse worker durante o round-trip. A rota estruturada `/api/trades/process` (que usa `await calculate_via_mcp_async` de verdade) não tem esse problema — só o caminho do chat.

**🟢 O `requirements.txt` instala do zero sem erro?**
Depois da correção mais recente, sim. Antes, não: `mcp==1.28.0` exige `uvicorn>=0.31.1`, mas o arquivo fixava `uvicorn[standard]==0.24.0`, causando `ResolutionImpossible` num ambiente limpo. A evidência anterior de "100 testes aprovados" só funcionou porque reaproveitou um ambiente que já tinha uvicorn mais novo instalado. O arquivo foi corrigido para `uvicorn[standard]>=0.31.1` e reinstalado com sucesso em venv novo.

### 4. RAG / ChromaDB

**🟢 Qual é a arquitetura de RAG atualmente em uso — a "legada" ou a "revisada"?**
A revisada, exclusivamente. `backend/app/vector_db/chroma_client.py` mantém a implementação antiga como `get_legacy_chroma_client()` só para inspeção/comparação, mas a última linha do arquivo reexporta `get_chroma_client` de `backend/app/vector_db/revised_client.py` — é essa função que todo o resto do sistema (`base_agent.py`, `orchestrator.py`) importa e usa.

**🟢 Como o corpus revisado é estruturado?**
18 trechos curados manualmente (não segmentação automática por tokens), definidos em `backend/app/vector_db/curated.py`, cada um com `id`, `text`, `asset_type`, `source` (URL oficial) e `checked_at` (data de consulta, fixa em `'2026-09-12'`). Ficam numa única coleção ChromaDB (`regulacoes_revisadas_v1`), com `hnsw:space: cosine`, função de embedding padrão do ChromaDB (`DefaultEmbeddingFunction`, ONNX MiniLM-L6-v2, executada localmente).

**🟢 A busca filtra por tipo de ativo (`asset_type`)?**
Não mais. `revised_client.py::search_regulations` recebe um parâmetro `asset_type`, mas nunca o usa no corpo da função — a busca é sempre global sobre a coleção única, ranqueada só por distância de cosseno. O parâmetro existe apenas por compatibilidade de assinatura com os chamadores antigos (`base_agent.py` ainda passa `asset_type=self.chroma_scope`).

**🟢 Quantos documentos são recuperados por consulta (k)?**
Depende do caminho de chamada: `top_k=2` para explicar um cálculo já realizado, `top_k=3` para perguntas sem operação extraída e para o fluxo consultivo geral. O benchmark de recuperação também usou 3. Não há um valor único de k para todo o sistema.

**🟢 A data de consulta (`checked_at`) garante que a informação está vigente?**
Não — é só a data em que o trecho foi verificado/incluído no corpus, não a data de vigência da norma. O manuscrito é explícito sobre essa distinção (Seção 5.5) e afirma que não há sistema de versionamento histórico de normas nem resolução de conflitos normativos implementado.

**🟢 Existe algum limiar de rejeição por similaridade insuficiente (ex.: "não encontrei evidência suficiente")?**
Não foi calibrado nenhum limiar numérico. A ausência de evidência suficiente é tratada só nas instruções de sistema dadas ao modelo ("se faltar evidência, peça esclarecimento"), não por um corte técnico de distância/score no código de recuperação.

### 5. Orquestração multiagente e LLM

**🟢 Quais modelos são usados e para quê?**
`claude-haiku-4-5-20251001` para classificação de intenção e extração de operações (parsing); `claude-sonnet-5` para explicações e respostas de consulta geral. Configurável via `.env` (`LLM_MODEL_PARSER`, `LLM_MODEL_EXPLAINER`).

**🟢 Como o orquestrador decide qual agente chamar?**
`Orchestrator.process()` primeiro chama `claude.classify_intent(message)` (Haiku), que devolve um tipo de ativo com confiança. Se um tipo reconhecido é identificado, delega a um agente especialista (`AcoesAgent`, `FIIAgent`, `OpcoesAgent`, `DerivativosAgent`, `EmprestimoAgent`, `CriptoAgent`); senão, trata como pergunta geral usando busca RAG + Sonnet diretamente.

**🟢 O modelo "lembra" da conversa anterior?**
Não, no sentido de reenviar histórico no prompt. Cada chamada ao modelo usa uma única mensagem construída para a solicitação corrente, sem sumarização nem janela de mensagens anteriores (`ClaudeClient._call_model`). A continuidade entre uma compra e uma venda posterior do mesmo ativo acontece por **consulta ao banco relacional** (preço médio via `get_average_price`), não por memória conversacional — perguntas de referência como "e se eu vender metade disso?" não são resolvidas, porque não há recuperação da mensagem anterior para isso.

**🟢 O histórico de chat é usado para restaurar a conversa ao recarregar a página?**
Não. A lista de mensagens exibidas fica só no componente Angular local, reiniciada vazia a cada recarga. O backend expõe uma rota de histórico (`GET /api/chat/history`), mas o frontend não a chama para restaurar a tela, e o fluxo de geração não a usa para montar prompts.

**🟢 `POST /api/chat/` e `POST /api/trades/process` usam a mesma convenção para `user_id`?**
Não — inconsistência real encontrada na validação: `/api/trades/process` e `/api/trades/history` recebem `user_id` como query string; `/api/chat/` recebe `user_id` dentro do corpo JSON (`ChatRequest.user_id`). Passar `?user_id=x` na URL do chat é silenciosamente ignorado.

### 6. Testes e qualidade

**🟢 Quantos testes existem hoje e quantos passam?**
94 testes aprovados (estado mais recente, após a correção da regressão de BDR), com 2 avisos de depreciação (Pydantic `class Config`, `httpx`/`httpx2`). Não inclui os 6 testes específicos de MCP/protocolo real registrados separadamente em `pytest_mcp.txt` (100 testes) nem os scripts de validação de 16-17/09 (fora da suíte pytest padrão).

**🟢 Por que a suíte de 88 testes passou mesmo com o bug de BDR presente?**
Porque nenhum dos 12 cenários numéricos formais da Tabela 4 do manuscrito testava BDR — a cobertura por categoria de ativo era incompleta. O caso que expôs o bug (venda de 10 AAPL34, IR esperado R$150, retornado R$0) foi um teste adicional feito manualmente depois, fora da suíte automatizada original. Isso é citado no próprio manuscrito como argumento contra tratar "suíte verde" como prova de correção tributária.

**🟢 O que `test_revision_safety.py` verifica?**
Que dados ausentes (mês, custo médio, prazo do empréstimo, custos/IRRF de futuros) geram recusa (`ValueError`) em vez de um cálculo silenciosamente incorreto, para Ações, Cripto, Futuros e Empréstimo. Também verifica que cripto no exterior é rejeitada como "não coberta" e que a tabela progressiva aplica corretamente por faixas.

**🟢 Os testes provam que o cálculo tributário está juridicamente correto?**
Não. Provam que o código produz o resultado que o próprio time de desenvolvimento espera dele, segundo regras já documentadas internamente — não houve validação por um especialista tributário externo nem nova consulta independente a fontes oficiais na rodada de testes. Isso é dito explicitamente tanto no manuscrito quanto no relatório de validação MCP.

### 7. Persistência e memória

**🟢 Qual banco de dados é usado?**
SQLAlchemy sobre SQLite por padrão (`DATABASE_URL` configurável; produção poderia usar Postgres via Docker Compose). Duas tabelas principais: `trades` (operações e resultados calculados) e `chat_history` (mensagens e respostas).

**🟢 Como o preço médio é calculado entre compras?**
Média ponderada, recalculada a cada compra registrada (`PortfolioPosition`/`get_average_price` em `repository.py`): `PM_novo = (Qtd_anterior × PM_anterior + Qtd_nova × Preço_novo) / (Qtd_anterior + Qtd_nova)`.

**🟢 O `user_id` garante segurança/autenticação?**
Não — é só um identificador de string livre, sem autenticação real. O manuscrito é explícito: "não constitui autenticação completa; segurança de uma implantação pública [...] não foi validada."

### 8. Limitações conhecidas do código (resumo para perguntas diretas de banca)

1. `OpcoesCalculator`/`FIICalculator` sem a mesma guarda de custo médio que `AcoesCalculator`/`BDRCalculator` (mascarado pelo MCP).
2. Comentário em `OpcoesCalculator` afirma isenção de R$20.000 aplicável, mas o código nunca implementa isso — comentário incorreto, não correção pendente de verdade nas regras de negócio (opções não têm essa isenção segundo a Receita).
3. Bloqueio do event loop no caminho síncrono do chat (`calculate_via_mcp` chamado sem `await`/executor).
4. Inconsistência de convenção de `user_id` entre endpoints.
5. Mensagem de aviso sobre "tarifas estimadas" aparece mesmo para tipos de ativo que não usam tabela de tarifas B3 nenhuma (ex.: empréstimo de ações).
6. Ambiguidade de nomenclatura em `ganho_prejuizo_liquido` (não desconta IR, mas "líquido" pode sugerir que sim).
7. Sem consolidação mensal real de carteira — `total_vendas_mes` é informado pelo usuário, não calculado a partir do histórico.
8. Sem detecção automática de day trade — `classificacao` é declarada, não inferida da data de compra/venda.
9. Sem memória conversacional entre mensagens de chat (cada chamada ao LLM é isolada).
10. Docker/Poetry não validados com a integração MCP (o Dockerfile atual não inclui o servidor MCP irmão do backend).

---

## PARTE 2 — SOBRE A MONOGRAFIA

### 1. Motivação, problema e objetivos

**🟢 Qual é a questão de pesquisa?**
"Em que medida a combinação de recuperação de evidências e cálculo determinístico pode apoiar respostas tributárias verificáveis, e quais erros permanecem observáveis em um conjunto controlado de consultas?"

**🟡 Por que RAG + calculadora determinística, e não só um LLM grande e bem treinado (ou fine-tuned)?**
Justificativa dada na Fundamentação Teórica: um LLM sozinho pode ser fluente sem ser correto (risco de alucinação), e para valores numéricos tributários isso é inaceitável — um erro de centavos numa alíquota é diferente de um erro de estilo de texto. Separar "o que a lei diz" (RAG, evidência recuperável e citável), "como calcular" (código testável, determinístico) e "como explicar" (LLM) permite localizar em qual componente um erro está, em vez de tudo ficar opaco dentro dos parâmetros de um modelo.

**🟢 Qual é o recorte de escopo (quais ativos são cobertos)?**
Ações, BDRs, fundos imobiliários (FIIs), opções, minicontratos futuros de índice e dólar (WIN/WDO), remuneração do doador em empréstimo de ações, e criptoativos (regime nacional; exterior é explicitamente fora de escopo).

**🟢 O sistema pretende substituir um contador ou a Receita Federal?**
Não — a monografia declara isso explicitamente em vários pontos: é um protótipo educacional, não um serviço de escrituração, consultoria individualizada ou transmissão de declarações.

### 2. Fundamentação teórica

**🟢 Por que os modelos de resposta acessados pela API não podem ser chamados de "modelos abertos"?**
Porque acesso comercial ao serviço, disponibilidade dos pesos e abertura dos dados de treinamento são características diferentes — usar a API da Anthropic não implica que o modelo seja aberto em nenhum desses sentidos.

**🟢 O que diferencia embeddings de busca exaustiva (busca por palavra-chave)?**
Embeddings representam propriedades semânticas em vetores, permitindo recuperar conteúdo relacionado mesmo sem coincidência exata de palavras — mas isso tem uma limitação relevante para o domínio: dois textos podem ser semanticamente próximos e, ainda assim, ter sentidos opostos ("tem isenção" e "não tem isenção"), o que impede tratar distância vetorial como prova de correção tributária.

**🟢 Que estrutura de indexação o ChromaDB usa e ela foi testada em escala?**
HNSW (grafo hierárquico de vizinhos aproximados), mas não foi medida diferença entre busca exata e aproximada nem testada em corpus grande — o corpus de 18 trechos serve à avaliação das respostas, não a conclusões sobre desempenho de índice em escala.

**🟢 O que é LLM-as-a-Judge e quais são seus limites reconhecidos na monografia?**
Um modelo (aqui, `claude-opus-5`) atribui notas/julga respostas segundo uma rubrica. Limites reconhecidos: vieses de posição/apresentação, mesmo fornecedor entre gerador e avaliador (correlação de estilo e critério), e concordância entre repetições do próprio julgamento não é o mesmo que validade jurídica (um avaliador pode repetir o mesmo erro consistentemente).

### 3. Domínio tributário (perguntas de conteúdo — a banca pode testar conhecimento de domínio)

**🟢 Qual é a regra de isenção para ações à vista?**
Isenção do ganho quando o total de vendas de ações à vista no mês (somando todas as corretoras), em operações comuns (não day trade), não ultrapassa R$20.000. O limite incide sobre o valor vendido, não sobre o lucro.

**🟢 BDRs têm a mesma isenção que ações?**
Não — BDR não tem a isenção de R$20.000. Ganho tributado em 15% (comum) ou 20% (day trade), sempre, independentemente do valor movimentado no mês.

**🟢 FII tem isenção de R$20.000 na venda de cotas?**
Não. Venda de cotas de FII: 20% sobre o ganho líquido, sempre, sem faixa de isenção. Isso é diferente do **rendimento distribuído mensalmente** pelo fundo (aluguéis etc.), que pode ser isento para pessoa física sob condições da Lei 11.033/2004 (negociação em bolsa, mínimo de 100 cotistas, limites de concentração) — são dois fatos geradores distintos, e confundi-los é um erro comum que o benchmark testa deliberadamente (caso T13).

**🟢 Qual é o regime de isenção de criptoativos nacionais?**
Isenção quando o total de alienações de criptoativos no mês (todas as moedas, todas as exchanges/carteiras nacionais, incluindo permutas cripto-cripto mesmo sem conversão em reais) não ultrapassa R$35.000 — não R$20.000, e não é limite por moeda ou operação individual.

**🟢 E se o criptoativo estiver custodiado no exterior?**
Regime diferente: Lei 14.754/2023, apuração anual, alíquota de 15% fixa, sem a isenção mensal de R$35.000. A monografia alerta que autocustódia, por si só, não prova localização no exterior — é preciso verificar natureza do ativo, custódia e intermediação antes de aplicar esse regime.

**🟢 Como funciona a progressividade do ganho de capital acima do limite de isenção de cripto?**
Por faixas (marginal), Lei 13.259/2016: 15% até R$5 milhões de ganho, 17,5% de R$5-10M, 20% de R$10-30M, 22,5% acima de R$30M — nunca a maior alíquota aplicada ao ganho inteiro.

**🟢 Qual é o valor do ponto nos minicontratos WIN e WDO?**
WIN (mini índice Ibovespa): R$0,20 por ponto por contrato. WDO (mini dólar): R$10,00 por ponto por contrato (contrato de USD 10.000, cotação em reais por USD 1.000).

**🟢 Como é tributada a remuneração do doador em empréstimo de ações?**
Pela Lei 15.265/2025 (arts. 18-19): tributação exclusiva na fonte, tabela regressiva por prazo — 22,5% até 180 dias, 20% de 181-360, 17,5% de 361-720, 15% acima de 720 dias. É tratamento de renda fixa, não de ganho de capital em venda de ação, e não gera DARF mensal adicional sobre essa remuneração.

**🟢 O código dos futuros reproduz o ajuste diário real de mercado?**
Não — é uma simplificação reconhecida explicitamente: o motor calcula a diferença entre cotação de abertura e fechamento da posição comprada, multiplicada pelo tamanho do contrato, mas não reproduz a trajetória completa de ajustes diários (marcação a mercado D+1), posições vendidas nem rolagens.

### 4. Trabalhos relacionados

**🟢 Como a monografia se posiciona em relação a Lewis et al. (2020) e a outros trabalhos de RAG?**
Reconhece o princípio arquitetural (recuperação + geração) sem alegar equivalência experimental — o corpus aqui é pequeno e curado manualmente em português, enquanto os benchmarks de referência têm escala e treinamento diferentes. A contribuição não é um novo algoritmo de recuperação ou modelo, mas um estudo aplicado de integração e avaliação num domínio sensível (tributário).

### 5. Metodologia de avaliação

**🟢 Quantas perguntas tem o benchmark e como se dividem?**
60 perguntas: 12 de desenvolvimento (não entram nos escores finais) e 48 de teste, distribuídas por 8 categorias (ações, BDRs, FIIs, opções, futuros, empréstimo, criptoativos, consultas ambíguas/fora de escopo). Os 42 casos dos 7 primeiros estratos compõem os escores de recuperação; os 6 restantes são avaliados separadamente quanto a abstenção/pedido de esclarecimento adequado.

**🟢 Quais configurações foram comparadas?**
Três: Sonnet com corpus inicial, Sonnet com corpus revisado, Haiku com corpus revisado. O texto das instruções foi mantido igual entre configurações.

**🟢 Como são calculados P@1, P@3 e nDCG@3?**
Rubrica de relevância em 3 graus (0 = irrelevante/contraditório, 1 = parcial, 2 = diretamente pertinente e correto). P@1: se o primeiro resultado tem grau 2. P@3: quantidade de resultados grau 2 entre os 3 primeiros, dividido por 3. nDCG@3: ganho `2^grau − 1` com desconto logarítmico de posição, usando como denominador ideal a união dos trechos julgados nas duas configurações para aquela pergunta (por isso é chamada "nDCG@3 agrupada" — não é um julgamento exaustivo de todo o corpus).

**🟢 O que muda entre P@1 alto e P@3 baixo?**
Uma pergunta pode precisar de só um trecho suficiente — nesse caso P@3 pode ficar baixo mesmo com a resposta tendo a regra necessária. As três métricas devem ser lidas juntas: nenhuma substitui verificar a resposta gerada de fato.

**🟢 Quem julgou as respostas e como a repetibilidade foi verificada?**
`claude-opus-5`, recebendo respostas anonimizadas em ordem embaralhada reproduzível. Uma rubrica separa correção, fundamentação, erro crítico e abstenção adequada. 12 perguntas (distribuídas pelos estratos) tiveram o julgamento repetido, gerando 36 pares — 32 de 36 mantiveram a mesma nota de correção (88,9% de concordância simples), enquanto as marcações de erro crítico coincidiram nas 36.

**🟢 Por que usar o mesmo fornecedor (Anthropic) para gerar e julgar as respostas é uma limitação?**
Porque pode haver correlação de estilo, conhecimento e critério entre o gerador e o avaliador — um viés sistemático de um não seria necessariamente detectado pelo outro. A monografia chama isso explicitamente de limitação, não de validação independente.

**🟢 Como os 12 cenários numéricos foram verificados?**
Por comparação direta contra tolerância de R$0,01 nos campos esperados (ir_devido, aliquota_aplicada, isenção_aplicada etc.), executando cada calculadora com entradas explícitas — não inferidos a partir da redação das respostas do modelo.

### 6. Resultados

**🟢 Quantas respostas o Sonnet acertou com corpus inicial vs. revisado?**
29 de 42 (inicial) vs. 37 de 42 (revisado) — diferença de 8 respostas, ~19 pontos percentuais. Haiku com corpus revisado: 30 de 42.

**🟢 Quantos erros críticos cada configuração teve?**
9 (Sonnet/inicial), 7 (Haiku/revisado), 0 (Sonnet/revisado) — mas a monografia é cuidadosa em dizer que zero marcações não prova ausência de erro (pode haver respostas incompletas ou falha do próprio avaliador).

**🟢 Como a recuperação (P@1, P@3, nDCG@3) mudou entre corpus inicial e revisado?**
P@1: 52,4% → 57,1%. P@3: 23,8% → 30,2%. nDCG@3 agrupada: 0,517 → 0,560. A melhora é menor que a observada na correção das respostas — sugere que contexto mais organizado ajuda a geração sem produzir recuperação perfeita, mas não permite isolar qual mudança (regra corrigida vs. granularidade vs. ordenação) causou qual ganho.

**🟢 O que os 12 cenários numéricos mostraram, antes e depois?**
6 de 12 atendidos na versão inicial; 12 de 12 na revisada. Os 4 casos de retenção do doador já eram atendidos mesmo na versão inicial — não é atribuído como ganho novo da revisão.

**🟢 Qual foi o custo total do experimento?**
US$4,89 no total (desenvolvimento, respostas, julgamentos, repetições, tentativas de formato). As 48 respostas de teste custaram aproximadamente US$0,56 (Sonnet inicial), US$0,33 (Sonnet revisado) e US$0,12 (Haiku revisado).

**🟢 A suíte de testes de software (pytest) mede a mesma coisa que os escores de correção das respostas?**
Não — são avaliações completamente separadas. Pytest testa se o código de cálculo produz o resultado esperado para entradas estruturadas explícitas; os escores de correção medem se o LLM, dado um contexto recuperado, gera uma resposta em linguagem natural considerada correta por outro modelo. Uma suíte 100% verde não valida a extração de linguagem natural, o roteador, nem a interface.

### 7. Limitações e trabalhos futuros

**🟢 Quais são as principais limitações declaradas?**
Ausência de validação tributária independente; corpus pequeno; gabaritos assistidos por IA (sem homologação de especialista); comparação dentro de um único fornecedor de LLM; julgamento não exaustivo do corpus; simplificação de apuração mensal; regressão de BDR encontrada mesmo com suíte "verde"; falha de adequação em pelo menos uma demonstração de chat (empréstimo, caso T31); recusas por dado ausente também fazem parte das demonstrações documentadas (não só sucessos).

**🟢 O que ficou faltando em termos de memória/continuidade conversacional?**
Perguntas de referência a turnos anteriores (ex.: "e se eu vender metade disso?") não são resolvidas, porque o sistema não recupera a mensagem anterior para isso — a continuidade só existe via dados persistidos no banco (preço médio), não via memória de diálogo.

**🟢 Quais trabalhos futuros têm prioridade?**
Revisão dos gabaritos por especialista; consultas externas ao processo de desenvolvimento (fora do time que construiu o sistema); migração completa de testes; contabilização mensal real (agregação automática de vendas por carteira); modelagem específica do empréstimo; cobertura de ajustes diários de futuros; comparação de embeddings para português; avaliação de ponta a ponta com usuários reais; corrigir e revalidar o bloqueio do event loop no chat; tornar reproduzível a instalação das dependências (já parcialmente corrigido no código, ver Parte 1); uniformizar a semântica dos campos de resultado (ex.: `ganho_prejuizo_liquido`); testar o timeout interno de 30s até estourar de verdade; validar Docker e Poetry com a integração MCP.

### 8. Perguntas difíceis previstas de banca (com resposta sugerida)

**🟡 "Se o LLM pode alucinar, por que confiar na explicação em português, mesmo com o número certo vindo da calculadora?"**
Não se confia cegamente — é exatamente por isso que a avaliação separa correção da resposta em linguagem natural (julgada por outro modelo, com taxa de erro crítico reportada) do resultado numérico estruturado (verificado por testes determinísticos). A arquitetura reduz o risco de erro *aritmético*, mas não elimina risco de má explicação, rótulo ambíguo (ver caso do `ganho_prejuizo_liquido`) ou generalização indevida — achados que a própria monografia documenta, inclusive um caso de resposta truncada e mal rotulada na Seção 7.5.

**🟡 "Por que o benchmark é sintético e não usa perguntas reais de usuários?"**
Trade-off explícito: perguntas sintéticas permitem controlar cobertura de categorias e incluir deliberadamente casos de fronteira (ambiguidade FII/ação, exterior vs. nacional em cripto) que poderiam ser raros numa amostra real pequena, mas não representam a distribuição real de dúvidas de investidores nem foram validadas por um especialista tributário — limitação reconhecida, não ocultada.

**🟡 "Como você sabe que a melhora de 29→37 respostas corretas não é só o modelo 'acertando por sorte' numa amostra pequena?"**
Não há teste estatístico de significância reportado — a amostra é pequena (42 perguntas) e a própria monografia evita alegar generalização: descreve o resultado como "benefício da revisão no conjunto examinado", não como efeito populacional comprovado. É uma limitação metodológica que deve ser reconhecida diretamente se perguntada, não defendida como se fosse robusta.

**🟡 "Se MCP não muda o resultado do cálculo (é idêntico ao direto), por que a integração vale a pena, dado que ela introduziu um bug de bloqueio do event loop?"**
Resposta honesta: o valor está na separação arquitetural e na trilha de protocolo auditável, não em melhorar a exatidão do cálculo (que já era correta antes). O custo (bloqueio do event loop no chat) é real e não foi escondido — está documentado como limitação a corrigir, e a decisão de manter a integração mesmo com essa limitação pode ser justificada como "câmbio aceitável para fins de protótipo/pesquisa", mas não deveria ser apresentada como pronta para produção sob carga.

**🟡 "Vocês usaram IA para gerar boa parte do código, dos testes e até da própria monografia — isso compromete a autoria/validade do trabalho?"**
A monografia declara isso abertamente (Apêndice B / Seção sobre uso de IA): o código inicial e a revisão documental tiveram assistência de IA, os gabaritos são assistidos por IA sem homologação de especialista, e as respostas de teste foram geradas e julgadas por modelos da mesma família. A defesa correta não é negar isso, mas apontar que o valor do trabalho está na metodologia de avaliação (separar camadas, medir com métricas explícitas, registrar evidência bruta reproduzível) — não na alegação de que o conteúdo é 100% produzido manualmente pelo autor.

**🟡 "Por que a suíte de testes ficou verde (88, depois 94) mas ainda havia um bug tributário real (BDR)?"**
Porque testes só verificam o que alguém pensou em testar. Os 12 cenários numéricos formais nunca cobriram BDR isoladamente; a suíte pytest testava outras propriedades do BDR mas não esse caso específico de fronteira. Isso é evidência a favor de ampliar cobertura por categoria de ativo antes de declarar qualquer conjunto de testes como suficiente — e a monografia já registra essa lição explicitamente.

---

## Como este documento foi produzido

Gerado por leitura direta do código em `D:\Projects\BrazilianFinancialAssistant` no commit `148e9f7` (mais o ajuste de `uvicorn` em `backend/requirements.txt`, ainda não commitado) e do `Documentation/TCC/Revisao/manuscrito.md` na versão mais recente (incluindo a Seção 7.5 e a correção da regressão de BDR). Não inclui verificação nova contra fontes tributárias oficiais além do que já está documentado no próprio projeto — para perguntas de conteúdo tributário muito específicas fora do escopo já coberto, confirme com a bibliografia legal citada na monografia antes da defesa.
