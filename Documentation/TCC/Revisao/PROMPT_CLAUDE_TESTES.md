# Verificação independente da integração MCP

Trabalhe em D:\Projects\BrazilianFinancialAssistant. A documentação principal está em Documentation/TCC/Revisao. Não use C:\Users\andre\tcc_revisao\revised como projeto principal.

Objetivo: testar e documentar a integração MCP de execução, sem confundir resultados novos com o benchmark histórico. Leia o git diff e preserve alterações existentes. Não faça commits, publique código, apague dados ou exponha .env/chaves. Peça autorização antes de chamadas pagas a LLMs e informe o custo previsto. Use banco SQLite e pasta Chroma temporários; não use o banco operacional.

Implementação a verificar:
- backend/app/mcp_gateway.py abre sessão MCP real via stdio, inicializa e chama fee_policy e calculate_trade.
- mcp_server/server.py reutiliza as calculadoras Python; não duplica fórmulas nem persiste operações.
- base_agent.py e rotas /api/trades/process e /api/trades/batch usam o gateway. Compras continuam no backend; perguntas sem operação usam RAG/LLM sem cálculo MCP.
- mcp_server/server.py é o servidor legado de apoio ao desenvolvimento, não o servidor runtime.
- Dependência: mcp==1.28.0, API v1. Não atualizar silenciosamente para v2.

Execute:
1. Instale dependências em ambiente virtual e rode backend/tests, incluindo test_mcp_runtime.py. Registre comando, versões, data, stdout, stderr e duração. A execução local anterior teve 100 testes aprovados; isso não garante sua execução.
2. Confira no protocolo initialize, tools/list e tools/call. Prove que houve subprocesso MCP e que as calculadoras não foram chamadas diretamente pelo caminho web. Não considere mocks como evidência do protocolo real.
3. Compare saídas MCP e diretas para ações, BDR, FII, opções, futuros de índice/dólar, empréstimo e cripto. Use custos, custo médio, total mensal, prazo e retenções necessários. Avalie gabaritos com fontes oficiais; não trate concordância com o código como validade tributária independente.
4. Teste falhas: custo ausente, total mensal ausente, prazo ausente, campos inválidos, NaN/infinito, servidor ausente, resposta inválida, ferramenta ausente, timeout e cancelamento. Verifique ausência de venda gravada em falha e inexistência de fallback direto. Registre eventual processamento parcial em batch.
5. Teste concorrência e Windows/uvicorn: início e encerramento dos processos stdio, latência, ausência de processos órfãos e bloqueio do event loop. O gateway síncrono é compatibilidade do agente e não comprova escalabilidade.
6. Rode a aplicação e capture evidências reais de formulário e chat. Para o chat completo, confirme antes orçamento e disponibilidade do modelo. Use exclusivamente dados sintéticos e não exponha chaves, nomes de clientes ou contas.
7. Confirme que custos informados são respeitados e que estimativas legadas não são apresentadas como tarifas atuais. fee_policy não consulta a B3 em tempo real e não possui vigência validada. Não inventar data de vigência ou fonte de tarifa.

Entregue evidências em Documentation/TCC/Revisao/Entrega_Final/evidencias/mcp_validacao_claude, com relatório PASS/FAIL/BLOQUEADO, logs, casos, gabaritos e capturas. Separe testes unitários, protocolo real, API e navegador/LLM. Registre limitações e bugs encontrados antes de propor correções.

Não sobrescreva experimentos_historicos, resultados do benchmark, capturas antigas nem o resumo aprovado. Não diga que as métricas históricas avaliaram MCP. Se corrigir código, explique o motivo e repita os testes afetados. Só atualize os resultados da monografia após revisar as evidências com o autor; ao editar Word, sincronize manuscrito.md e modelo/modelo_sincronizado.docx, regenere PDF e confira capas, sumário, figuras e paginação.

Limite de implantação: a integração foi validada em Python local com backend/requirements.txt. Docker e Poetry não foram validados; o Dockerfile atual não inclui o servidor MCP irmão do backend. Não tratar o deploy em contêiner como pronto. Validar/adaptar empacotamento antes de usar Docker.
