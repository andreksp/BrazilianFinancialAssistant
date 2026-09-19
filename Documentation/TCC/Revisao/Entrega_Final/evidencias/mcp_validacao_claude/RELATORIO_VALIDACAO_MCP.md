# Relatório de Verificação Independente — Integração MCP

Sessão: 2026-09-16/17. Projeto: `D:\Projects\BrazilianFinancialAssistant`. Executor: Claude Code, seguindo `PROMPT_CLAUDE_TESTES.md`.

Ambiente: venv isolado criado do zero (`backend/venv_mcp_test`), Python 3.11.9, Windows. Nenhum commit foi feito. Nenhuma chamada paga a LLM foi realizada até este ponto do relatório (item 6 pendente de autorização — ver final).

---

## 1. Instalação e suíte de testes — **PASS, com ressalva real**

- **Achado**: `backend/requirements.txt` não é instalável do zero. `mcp==1.28.0` exige `uvicorn>=0.31.1`, mas o arquivo fixa `uvicorn[standard]==0.24.0`. `pip install -r requirements.txt` falha com `ResolutionImpossible` num ambiente limpo. A evidência anterior de "100 passed" (`pytest_mcp.txt`, gerada antes desta sessão) só foi possível porque reaproveitou um ambiente que já tinha uvicorn mais novo instalado — **não foi reproduzida a partir de uma instalação limpa do arquivo publicado**.
- Instalando com `uvicorn[standard]>=0.31.1` (única mudança), o restante resolve sem conflitos (`pip check` limpo). Versões resultantes: uvicorn 0.53.0, fastapi 0.141.1, pydantic 2.13.5, anthropic 1.6.0, chromadb 0.5.3, mcp 1.28.0.
- Suíte completa reexecutada nesse venv limpo: **100 passed, 2 warnings, 19.87s** (comando: `python -m pytest tests/ -v`; log completo em `pytest_full_venv_isolado.txt`; `pip freeze` em `pip_freeze_venv_mcp_test.txt`).
- **Não corrigi `requirements.txt`** nesta sessão — é uma decisão de packaging que cabe ao autor (ex.: subir o piso de `uvicorn` ou remover o pin exato). Reportando apenas.

## 2. Protocolo MCP real — **PASS**

Script: `verify_protocol.py` → evidência bruta em `protocol_evidence.json`.

- **Subprocesso real confirmado**: durante a sessão MCP, dois processos `python.exe` filhos foram detectados via `psutil` (um com o caminho do venv, outro com o caminho do Python base do sistema — ambos executando `mcp_server/runtime_server.py`; a duplicidade é uma observação de comportamento do Windows/anyio ao spawnar o processo via `sys.executable` dentro de um venv, não investigada a fundo por não ser o foco do pedido) + 1 `conhost.exe` (console host do Windows). Todos encerrados corretamente após o fechamento da sessão — **nenhum órfão remanescente**.
- **Handshake real registrado**: `initialize` (protocolVersion=`2025-11-25`, serverInfo=`Financial calculations runtime`/`1.28.0`), `tools/list` (2 ferramentas: `fee_policy`, `calculate_trade`, com schemas completos), `tools/call` para ambas as ferramentas com payloads reais (`fee_policy` retornou `live_tariffs: false` e o aviso de estimativa legada; `calculate_trade` para FII retornou `ir_devido: 20.0`, batendo com o gabarito 20% sobre ganho de R$100).
- **Caminho web não chama calculadoras diretamente** (verificado por inspeção estática, não execução): em `app/api/trades.py`, os imports de classes de calculadora (`AcoesCalculator` etc.) só alimentam um dicionário `_CALCULATORS` usado exclusivamente para validar se `tipo_ativo` é suportado (`_CALCULATORS.get(trade.tipo_ativo) is None` → HTTP 400); a linha que executa o cálculo é sempre `await calculate_via_mcp_async(...)`. Em `app/agents/base_agent.py`, `_process()` chama `calculate_via_mcp(...)` diretamente; o método abstrato `get_calculator()`, implementado em cada agente especialista (`acoes_agent.py` etc., que instanciam `AcoesCalculator()` etc. em nível de classe), **não é mais invocado em lugar nenhum do fluxo real** — é código morto remanescente da versão pré-MCP, mantido apenas para satisfazer o contrato abstrato de `BaseAgent`.

## 3. Comparação MCP vs. cálculo direto, por tipo de ativo — **PASS (10/10)**

Script: `compare_mcp_vs_direct.py` → evidência em `comparacao_mcp_vs_direto.json`.

10 casos cobrindo ações (com e sem isenção), BDR, FII, opções, futuro WIN, futuro WDO, empréstimo de ações (300 dias), cripto nacional (tributado e isento) — todos com custos, custo médio, total mensal, prazo ou retenções conforme exigido por cada tipo. Em todos os 10: **resultado via MCP == resultado via import direto da calculadora**, e ambos batem com o valor esperado pela regra tributária documentada (base legal citada por caso no JSON).

**Ressalva sobre os gabaritos**: os valores esperados foram derivados das regras já documentadas no `manuscrito.md`/`research.md` do próprio projeto (verificadas contra fontes oficiais em sessão anterior de revisão da monografia, registrada em `Documentation/TCC/Revisao/`). Esta execução **não é uma nova consulta independente a fontes oficiais** — reutiliza o levantamento já feito, checando apenas que a implementação corrente ainda produz esses valores.

**Achado à parte (não é bug de MCP, é dívida técnica pré-existente)**: `OpcoesCalculator` e `FIICalculator` não fazem parte da migração de segurança aplicada a `AcoesCalculator`/`BDRCalculator`/`FuturosCalculator`/`CriptomoedaCalculator` (ver `test_revision_safety.py` — não há testes equivalentes para opções/FII). Concretamente:
  - Ambas ainda usam o padrão antigo `pm = average_price or trade.preco_unitario`, que silenciosamente assume ganho zero se `average_price` vier `None`, em vez de recusar o cálculo com `ValueError` como as demais.
  - `OpcoesCalculator` tem no docstring "Isenção: R$20.000/mês aplica (rastreada em nível de portfólio)", mas o código nunca implementa isso — `isenção_aplicada = False` é fixo, sem checagem de `total_vendas_mes`. Ou o comentário está desatualizado, ou a isenção deveria ter sido implementada e não foi.
  - **Por que isso não quebrou nos testes**: o gateway MCP (`runtime_server.py::calculate_trade`) intercepta e rejeita `average_price`/`preco_medio_informado` ausente ou não-positivo para todo tipo de ativo (exceto empréstimo), então a lacuna do calculador em si fica mascarada enquanto todo tráfego passar pelo MCP. Se algum código futuro chamar `OpcoesCalculator`/`FIICalculator` diretamente (como os testes unitários já fazem, deliberadamente, para testar a calculadora isolada), a lacuna se manifesta.

## 4. Testes de falha — **PASS (todas as recusas ocorreram sem fallback direto e sem venda gravada)**

Scripts: `test_failures_http.py` (camada HTTP real, TestClient) e `test_nan_inf_timeout_cancel.py` (gateway/protocolo).

| Cenário | Resultado |
|---|---|
| Custo médio ausente | HTTP 400; nenhuma venda gravada no histórico (verificado consultando `/api/trades/history` depois) |
| Total mensal ausente (ações) | HTTP 400 |
| Prazo ausente (empréstimo) | HTTP 400 |
| Tipo de ativo inválido | HTTP 422 (Pydantic, antes de chegar à lógica de negócio) |
| Quantidade negativa | HTTP 422 |
| NaN em `preco_medio_informado` | Rejeitado no próprio modelo `TradeInput` (`Field(ge=0)`; NaN nunca satisfaz `>=`) — nem chega ao gateway MCP |
| Infinito em `preco_medio_informado` | Passa a validação do Pydantic, mas é rejeitado pelo `runtime_server.py` (`math.isfinite`) com `ValueError` |
| Ferramenta MCP ausente | `tools/call` para nome inexistente retorna `isError=True`, "Unknown tool" — sem exceção não tratada |
| Resposta inválida de servidor MCP (forjado) | `TaxCalculationResult.model_validate()` falha com `ValidationError` (14 campos faltantes), convertida em `ValueError` genérico pelo gateway |
| Timeout | Servidor MCP forjado (sleep 120s) forçado com teto externo de 5s (não os 30s internos, para não esperar); `asyncio.TimeoutError` propagado corretamente. **O teto interno real de 30s do gateway não foi esperado até estourar** (economia de tempo); a lógica de conversão de exceção em `ValueError` é agnóstica ao tipo de exceção, então o comportamento no timeout de 30s é inferido do código, não observado diretamente nesta sessão. |
| Cancelamento (task.cancel()) | `CancelledError` propagada corretamente, sem exceção não tratada nem subprocesso órfão |
| **Batch parcial** | Lote com 1 compra + 1 venda inválida (sem total mensal) + 1 venda válida (FII) → resultado: 1 item retornado (a venda de FII). A compra não retorna resultado por design; a venda inválida é descartada silenciosamente (log de warning), **sem interromper o processamento das demais entradas do lote e sem reverter nada que já foi salvo antes dela**. |

Nenhum caso caiu em fallback de cálculo direto (a inspeção de `mcp_gateway.py` mostra que toda falha vira `ValueError`, nunca uma chamada alternativa à calculadora local).

## 5. Concorrência e comportamento no event loop — **PASS parcial / achado real de arquitetura**

Script: `test_concurrency_eventloop.py` → evidência em `resultados_concorrencia_eventloop.json`.

- **8 chamadas assíncronas concorrentes** (`calculate_via_mcp_async`, caminho real da rota `POST /api/trades/process`): 8/8 sucesso, resultados corretamente isolados por chamada (nenhuma mistura de dados entre chamadas concorrentes), 0.54s no total para as 8, nenhum processo órfão após a rajada.
  - *(Nota: a primeira execução deste teste reportou falsamente 1/8 de sucesso — investigado e confirmado como defeito no fixture do teste, não no sistema: o `total_vendas_mes` estava fixo enquanto o `preco_unitario` variava por chamada, violando a própria regra de negócio para 7 das 8 chamadas. Corrigido e reexecutado.)*
- **Achado real — bloqueio do event loop no caminho do chat**: `app/api/chat.py::send_message` é `async def` e chama `Orchestrator.process(...)` de forma síncrona (sem `await`), que por sua vez desce até `base_agent.py` chamando `gateway.calculate_via_mcp(...)` — o wrapper **síncrono** — diretamente, sem `run_in_executor` nem qualquer outro isolamento de thread. Teste reproduzindo esse padrão exato (heartbeat concorrente no mesmo loop, tique a cada 50ms): durante a chamada MCP (~0,37s), o heartbeat parou de tiquetar quase completamente (maior intervalo entre tiques ≈ 0,40s, ou seja, praticamente a duração inteira da chamada). **Isso significa que, em produção com um único worker uvicorn (padrão), cada mensagem de chat que dispare um cálculo MCP bloqueia TODAS as outras requisições concorrentes nesse worker pela duração do round-trip MCP** (spawn de subprocesso Python + protocolo stdio, tipicamente 0,3–0,5s nesta máquina, podendo ser maior sob carga ou em disco mais lento). O próprio código já reconhece isso parcialmente (`mcp_gateway.py`: "O gateway síncrono é compatibilidade do agente e não comprova escalabilidade") — este teste fornece a prova empírica direta do mecanismo e da magnitude.
  - Isso **não afeta a rota estruturada** (`/api/trades/process`), que usa `await calculate_via_mcp_async` de verdade e não bloqueia o loop (confirmado no primeiro subteste).

## 6. Execução real da aplicação (formulário e chat) — **PASS (via API real; sem navegador)**

**Limitação de acesso**: a integração de navegador (Claude in Chrome) usada em sessão anterior desta mesma revisão havia se desconectado quando cheguei a este item, e não foi possível reconectá-la nesta execução. Por isso, **não há capturas de tela da interface Angular** nesta rodada. Em vez disso, autorizado pelo autor (chat completo, com custo real), rodei o backend de verdade (mesma stack, `venv_mcp_test`, banco SQLite e Chroma temporários e isolados, chave real da Anthropic) e exercitei a API estruturada (equivalente funcional ao formulário) e o chat completo via requisições HTTP reais — não são respostas do executor de benchmark reaproveitadas, nem mocks.

Backend real, porta 127.0.0.1:8020, log completo em `server_real_20260916.log`.

**Formulário (API estruturada, sem custo de LLM)** — `formulario_real/`:
| Cenário | IR devido | Observação |
|---|---|---|
| Ações — isento (total mês R$3.000) | R$0,00 | `isenção_aplicada: true` |
| Ações — tributado (total mês R$25.000) | R$74,85 | 15% sobre R$500 de ganho, líquido de taxas |
| FII — venda de cotas | R$20,00 | 20% sobre R$100, sem isenção |
| Cripto nacional (acima de R$35.000/mês) | R$750,00 | 15% sobre R$5.000 |
| Futuro WIN | R$14,62 | multiplicador R$0,20/ponto aplicado (100 pontos × R$0,20 × 1 contrato = R$20 nocional, R$100 de ganho após multiplicador de índice) |
| Futuro WDO | R$29,54 | multiplicador R$10,00/ponto aplicado |
| Empréstimo de ações — doador (300 dias) | R$0,00 (IRRF R$24,00) | tabela regressiva 20%, tributação exclusiva na fonte |

Todos os 7 confirmados no log do servidor como tendo passado pelo gateway MCP real (`MCP tools=fee_policy,calculate_trade transport=stdio status=ok asset_type=...`), não por cálculo direto.

**Chat completo (3 mensagens reais, autorizadas — custo real incorrido)** — `chat_real/`:
1. **Pergunta geral** ("Qual a diferença de tributação entre venda de ações e venda de cotas de FII?") → resposta correta do agente consultivo, distinguindo ganho de capital (20% FII, sempre) de rendimento distribuído (isento sob condições da Lei 11.033/2004), e citando a regra de compensação de prejuízos por espécie de fundo.
2. **Compra via linguagem natural** ("Comprei 50 cotas do HGLG11 a 100 reais hoje") → extração correta da operação (`tipo_operacao: compra`, `quantidade: 50`, `preco_unitario: 100.0`), confirmação registrada, preço médio atualizado no banco.
3. **Venda via linguagem natural** ("Vendi as 50 cotas do HGLG11 a 110 reais hoje") → pipeline completo exercitado de ponta a ponta: Haiku classifica intenção (`fii`, confiança 0,98) → Haiku extrai a operação → backend recupera o preço médio real da compra anterior (R$100, gravada na mensagem 2) → gateway MCP calcula (`ir_devido: 100.0`, 20% sobre R$500 de ganho) → Sonnet gera explicação em português citando corretamente a ausência de isenção para FII e a diferença entre ganho de capital e rendimento distribuído.

**Achado adicional (inconsistência de API, não é bug do MCP)**: `POST /api/chat/` lê `user_id` do **corpo** da requisição (`ChatRequest.user_id`), enquanto `/api/trades/process` e `/api/trades/history` leem da **query string**. Ao testar manualmente com `?user_id=chat_demo` na query (convenção usada pelos outros endpoints), o parâmetro foi silenciosamente ignorado e todas as mensagens de chat foram gravadas sob `user_id="default"`. Sem impacto nesta execução (banco temporário e descartável), mas é uma inconsistência real de contrato de API entre endpoints do mesmo backend.

**Custo real incorrido**: não medido em tokens por esta execução (o app não loga uso de tokens, diferente do harness do benchmark histórico que gerava `api_ledger.jsonl`). Estimativa por analogia às chamadas já registradas em sessões anteriores desta revisão (mesmos modelos, Haiku classify + parse + Sonnet explain/answer): da ordem de US$0,01–0,03 no total para as 3 mensagens.

## 7. Custos e política de tarifas — **PASS**

- Confirmado empiricamente: quando `custos_operacao` é informado (ex.: `5.0`), o resultado usa exatamente esse valor em `taxas_totais.total`, sem qualquer aviso de estimativa.
- Quando `custos_operacao` é omitido, o resultado usa a estimativa legada de tarifas B3 parametrizadas (`taxas_totais.total` calculado por `b3_fees.py`) **e** a mensagem final inclui, textualmente, o aviso: "Custos informados são preferidos. Eventuais tarifas parametrizadas são estimativas legadas, sem vigência validada; não constituem tabela atual da B3."
- `fee_policy` sempre retorna `live_tariffs: false` e `effective_date: null` — nunca finge ter uma tarifa vigente validada.

---

## Resumo executivo

| Item do prompt | Status |
|---|---|
| 1. Instalação + suíte completa | **PASS**, com achado real (requirements.txt não instala do zero sem ajuste de uvicorn) |
| 2. Protocolo real (initialize/tools/list/tools/call) + prova de subprocesso + caminho web sem chamada direta | **PASS** |
| 3. Comparação MCP vs. direto, todos os tipos de ativo | **PASS (10/10)**, com achado de dívida técnica pré-existente (Opções/FII não migrados para o padrão seguro) |
| 4. Testes de falha (10 cenários) | **PASS** em todos, com uma ressalva de escopo (timeout interno de 30s não observado até o fim, só inferido) |
| 5. Concorrência e event loop | **PASS** na rota assíncrona; **achado real** de bloqueio do event loop no caminho síncrono do chat |
| 6. Execução real com navegador/chat | **PASS via API real** (formulário + chat completo, autorizado, custo real incorrido ~centavos). Navegador indisponível nesta sessão — sem capturas de tela da interface Angular. |
| 7. Política de custos/tarifas | **PASS** |

## Achados menores adicionais

- A mensagem de aviso "Custos informados são preferidos. Eventuais tarifas parametrizadas são estimativas legadas..." é anexada de forma genérica sempre que `custos_operacao` não é informado, **mesmo para tipos de ativo que não usam a tabela de tarifas B3 de forma alguma** (ex.: `EmprestimoCalculator`, que tem `taxas_totais.total == 0` fixo). Não é um erro de cálculo, mas o texto do aviso não se aplica literalmente a esse caso.
- `POST /api/chat/` lê `user_id` do corpo da requisição; `/api/trades/process` e `/api/trades/history` leem da query string — inconsistência de convenção entre endpoints do mesmo backend (ver Seção 6).
- Foi criado um ambiente virtual `backend/venv_mcp_test/` para esta verificação. Está listado como não rastreado pelo git (`.gitignore` só cobre o diretório literal `venv/`, não `venv_mcp_test/`) — não foi commitado, mas fica pendente de limpeza ou de um ajuste no `.gitignore` se o autor quiser evitar que apareça em `git status`.

## Limitações desta verificação

- Não reexecutei o benchmark histórico de 60 perguntas nem os julgamentos LLM-as-a-Judge — fora de escopo deste prompt, e isso não deve ser confundido com uma nova rodada de avaliação de qualidade de resposta.
- Os gabaritos tributários usados na Seção 3 vêm do levantamento já feito na revisão anterior da monografia, não de uma nova consulta a fontes oficiais nesta sessão.
- O teste de timeout usa um teto externo de 5s por economia de tempo, não os 30s reais internos do gateway.
- Docker/Poetry não foram tocados nem validados nesta sessão (fora de escopo, conforme o próprio prompt already avisa).
- Nenhuma correção de código foi aplicada nesta sessão — apenas verificação e registro de achados, conforme pedido ("Registre limitações e bugs encontrados antes de propor correções").
