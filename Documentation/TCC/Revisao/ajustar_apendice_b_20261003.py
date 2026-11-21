from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

NEW = [
    'Este apêndice relaciona os componentes de código e os registros de evidência citados nos Capítulos 5 a 7, para que cada afirmação possa ser conferida no pacote entregue. Os caminhos de código são relativos à raiz do projeto. Os registros de evidência (B.7 a B.12) estão na pasta Documentation/TCC/Revisao/Entrega_Final/evidencias, e os arquivos do experimento histórico, na pasta Documentation/TCC/Revisao/experimentos_historicos.',
    'B.1 Interface web: frontend/src/app/components; serviço de chamadas HTTP em frontend/src/app/services/api.service.ts.',
    'B.2 Orquestração e ciclo de ferramentas: backend/app/agents, incluindo tool_chat.py (ciclo de ferramentas) e chat_policy.py (separação entre simulação e registro); cliente do SDK em backend/app/llm/claude_client.py.',
    'B.3 Corpus curado e fontes dos trechos: backend/app/vector_db/curated.py.',
    'B.4 Calculadoras e MCP: backend/app/calculations; servidor MCP em mcp_server/server.py; gateway MCP do formulário em backend/app/mcp_gateway.py.',
    'B.5 Persistência e consulta de preço médio: backend/app/storage/repository.py.',
    'B.6 Testes e experimento histórico: backend/tests e frontend/tests; na pasta do experimento, calculator_checks.py (12 cenários), experiment.py (instruções e execução), judge.py (julgamento), benchmark.json, baseline_retrieval.json, revised_retrieval.json, api_results e results_per_case.csv.',
    'B.7 Verificação posterior das calculadoras (Seção 7.3): correcao_posterior, com pytest_corrigido.txt, calculadoras_12_reexecutadas.json e bdr_regressao_corrigida.json.',
    'B.8 Integração MCP de 16 set. 2026: mcp_integracao_20260916/pytest_mcp.txt.',
    'B.9 Verificação complementar da integração MCP, 16–17 set. 2026 (Seção 7.5): mcp_validacao_claude, com pytest_full_venv_isolado.txt, protocol_evidence.json, comparacao_mcp_vs_direto.json, server_real_20260916.log e chat_real/03_venda_fii.json.',
    'B.10 Primeira verificação do ciclo de ferramentas, 20 set. 2026: tool_use_20260920/pytest.txt.',
    'B.11 Validação do ciclo de ferramentas e da interface, 20 set. 2026 (Seção 7.6): tool_use_validacao_claude, com o relatório RELATORIO_TOOL_USE.md, pytest_suite_limpa.txt, os resultados em JSON e as capturas em capturas_interface.',
    'B.12 Suíte ampliada após as correções: revisao_adendo_tool_use_20260920/pytest.txt.',
]
R = 'D:/Projects/BrazilianFinancialAssistant/Documentation/TCC/Revisao/'
for f in ['Entrega_Final/Monografia_Revisada_para_Orientador.docx', 'modelo/modelo_sincronizado.docx']:
    d = Document(R + f)
    P = d.paragraphs
    ks = [i for i, p in enumerate(P) if p.style.name == 'TCC Capitulo' and p.text.startswith('APÊNDICE B –')]
    assert len(ks) == 1
    k = ks[0]
    body = P[k + 1:k + 15]
    assert body[0].text.startswith('Este apêndice') and body[13].text.startswith('B.13')
    assert P[k + 15].text.startswith('ANEXO A')
    for p, t in zip(body[:13], NEW):
        p.runs[0].text = t
        for r in p.runs[1:]:
            r._r.getparent().remove(r._r)
    for p in body:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    d.save(R + f)
    print(f, 'ok')

d = Document(R + 'modelo/modelo_sincronizado.docx')
blocks = ['<!-- Fonte editorial única. Preserve IDs; capas, tabelas e figuras são mantidas no modelo. -->']
for i, p in enumerate(d.paragraphs):
    if not p.text.strip() or p._p.xpath('.//w:fldChar|.//w:fldSimple|.//w:drawing') or p.style.name.lower().startswith('toc'):
        continue
    pre = '# ' if p.style.name in ('TCC Capitulo', 'TCC Preliminar') else '## ' if p.style.name == 'TCC Secao' else ''
    blocks.append(f'<!-- p:{i} -->\n{pre}{p.text}')
open(R + 'manuscrito.md', 'w', encoding='utf8').write('\n\n'.join(blocks) + '\n')
print('md regenerado')
