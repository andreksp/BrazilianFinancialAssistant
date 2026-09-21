# Escopo da verificação de 20/09/2026

120 testes aprovados, dois avisos. Ambiente Python já instalado, banco SQLite e
Chroma temporários, ANTHROPIC_API_KEY vazia. Não é prova de instalação limpa.
Comando executado: python -m pytest backend/tests -q -p no:cacheprovider
(caminho absoluto dos testes; diretório de trabalho temporário e PYTHONPATH=backend).

O servidor MCP foi exercitado de verdade pelo teste test_real_mcp_with_scripted_llm.
As respostas do modelo foram simuladas: não houve nova chamada paga, navegador,
benchmark, medição de custo ou prova da qualidade de decisão de um LLM real.
Os testes estão em backend/tests/test_llm_tool_chat.py.

Históricos anteriores permanecem preservados. Falhas conhecidas nas calculadoras,
empacotamento e autenticação não foram resolvidas por esta mudança de seleção.

Referência de protocolo da API consultada:
https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls
