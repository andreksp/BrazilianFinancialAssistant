Projeto principal: D:\Projects\BrazilianFinancialAssistant.
Documentação: esta pasta.
Fonte: manuscrito.md; modelo: modelo/modelo_sincronizado.docx.
Gerar: python build_revision.py; depois python correcao_20260913/export_synced.py.
Integração MCP local implementada em 16/09/2026. Benchmark e capturas históricos não foram reexecutados.
Ver PROMPT_CLAUDE_TESTES.md para validação independente e evidências de navegador.

Limite de implantação: a integração foi validada em Python local com backend/requirements.txt. Docker e Poetry não foram validados; o Dockerfile atual não inclui o servidor MCP irmão do backend. Não tratar o deploy em contêiner como pronto. Validar/adaptar empacotamento antes de usar Docker.
