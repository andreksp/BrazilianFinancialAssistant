# Validação da seleção de ferramentas pelo LLM

Trabalhe em D:\Projects\BrazilianFinancialAssistant. Não altere monografia,
manuscrito, resultados históricos nem código sem aprovação. Não faça commits.

A implementação de 20/09/2026 muda SOMENTE vendas/remuneração extraídas no chat:
Haiku classifica/extrai; Sonnet recebe ferramentas e usa tool_choice=auto.
backend/app/agents/tool_chat.py mantém um ciclo limitado, até 6 rodadas/8 chamadas.
fee_policy e calculate_trade usam MCP real em mcp_server/server.py.
consultar_preco_medio é ferramenta LOCAL, somente leitura, vinculada ao usuário
e ativo pelo backend; NÃO é uma terceira ferramenta publicada no servidor MCP.
Os argumentos das ferramentas apresentadas ao modelo são vazios: o host injeta
a operação validada. O modelo decide ferramentas, não altera fatos financeiros.
Compras e perguntas sem operação mantêm o fluxo anterior; formulário usa gateway.

Execute a suíte em banco temporário. Não toque no banco operacional. Registre
versões, instalação, comandos e logs. Os testes anteriores não comprovam instalação
limpa; existe conflito conhecido uvicorn/MCP no requirements publicado.

Peça autorização e orçamento ANTES de chamadas pagas. Se autorizado, teste via
API e navegador quando disponível: FII com custo informado, FII com compra prévia,
FII sem custo, ações sem total mensal, empréstimo sem prazo, pergunta geral e compra.
Capture blocos tool_use/tool_result, stop_reason e uso de tokens sem expor chaves.
Comprove que a seleção veio do modelo real, não de roteiro simulado nem do gateway
do formulário. Observe logs chat_tool origin=llm e chamadas reais MCP.

Teste tentativas de passar user_id/ativo/custo nas ferramentas, ferramenta desconhecida,
repetição, limite de rodadas, servidor ausente e resposta truncada. Venda só deve
ser gravada uma vez após resultado validado E finalização normal da explicação.
Verifique concorrência real: a rota de chat agora é def e executada em threadpool,
mas ainda é necessário medir heartbeat/latência no serviço completo.

Confira a explicação numericamente, inclusive ganho antes/depois de imposto;
a observação semântica no prompt NÃO é prova de correção ou de ausência de alucinação.
Verifique a ausência de memória entre mensagens e a preservação de tool_result
somente dentro da solicitação atual. Não trate o user_id atual como autenticação forte.

Salve os artefatos em Entrega_Final/evidencias/tool_use_validacao_claude.
Separe implementação, teste com modelo simulado, teste com modelo real e navegador.
Não transfira as métricas históricas para esta arquitetura. Reporte bugs sem ocultá-los.
