"""Alinha a monografia ao código de 03/10/2026 e cria o Apêndice B.

1. Atualiza trechos que contradiziam o código (identificador do usuário, confirmação
   de gravação, separação entre simulação e registro, consulta à carteira, venda de
   ações acima de R$ 20 mil, IRRF não informado em futuros).
2. Retira do corpo do texto caminhos de arquivo, nomes de classe e de função e nomes
   de arquivos de evidência, substituindo-os por descrição ou por referência ao
   Apêndice B. Mantém nomes que são o próprio objeto da discussão (ferramentas MCP,
   blocos tool_use/tool_result, o campo ganho_prejuizo_liquido) e transcrições literais.
3. Cria o Apêndice B, já citado no texto mas inexistente no documento.

Edita os dois .docx (entrega e modelo), confere que nenhum outro parágrafo mudou e
regenera manuscrito.md a partir do modelo, como os scripts anteriores.
"""
from pathlib import Path
from datetime import datetime
from shutil import copy2
from docx import Document

ROOT = Path(__file__).resolve().parent
WORD = ROOT / 'Entrega_Final/Monografia_Revisada_para_Orientador.docx'
TEMPLATE = ROOT / 'modelo/modelo_sincronizado.docx'
MD = ROOT / 'manuscrito.md'

# (trecho atual, novo trecho). Cada trecho atual deve ocorrer exatamente uma vez.
REPLACEMENTS = [
    # 5.2 Interface web
    ('O serviço ApiService centraliza as chamadas HTTP',
     'Um serviço único do frontend centraliza as chamadas HTTP'),
    ('No fluxo estruturado, processTrade envia os dados a POST /api/trades/process e recebe '
     'TaxCalculationResult. No fluxo conversacional, sendChat utiliza POST /api/chat/ e recebe '
     'ChatResponse, que pode conter',
     'No fluxo estruturado, o formulário envia os dados à rota de processamento de operações e '
     'recebe o resultado do cálculo. No fluxo conversacional, o chat envia a mensagem à rota de '
     'chat e recebe uma resposta que pode conter'),
    ('A implementação pode ser localizada em frontend/src/app/components e no serviço '
     'services/api.service.ts.',
     'A localização dos componentes no código consta no Apêndice B, item B.1.'),
    # 5.3 / 5.4
    ('O modelo TradeInput valida', 'O modelo de dados da operação valida'),
    ('A orquestração está implementada em classes Python, em app/agents, e utiliza o cliente do '
     'SDK da Anthropic em app/llm/claude_client.py. Orchestrator.process solicita',
     'A orquestração está implementada em classes Python e utiliza o cliente do SDK da '
     'Anthropic. O orquestrador solicita'),
    ('o agente inicia o ciclo de ferramentas em app/agents/tool_chat.py.',
     'o agente inicia o ciclo de ferramentas.'),
    ('com tool_choice configurado como auto. Solicitações tool_use são respondidas com blocos '
     'tool_result,',
     'com a escolha de ferramentas deixada ao modelo (tool_choice configurado como auto). As '
     'solicitações de ferramenta, em blocos tool_use, são respondidas com blocos tool_result,'),
    ('Nos agentes, uma compra extraída pode ser registrada com uma confirmação; uma venda exige',
     'Nos agentes, uma operação extraída é registrada somente quando a mensagem a afirma como '
     'realizada, como em “comprei” ou “vendi”; nos demais casos, a resposta é apresentada como '
     'simulação. Uma venda exige'),
    (' Esse encadeamento está em BaseAgent.process e BaseAgent._process.', ''),
    ('(top_k=2)', '(k = 2)'),
    ('(top_k=3)', '(k = 3)'),
    # 5.5 Base vetorial
    ('ChromaDB 0.5.3, PersistentClient e a função padrão ONNXMiniLM_L6_V2, associada a '
     'all-MiniLM-L6-v2.',
     'ChromaDB 0.5.3, com cliente persistente em disco e a função padrão de embeddings associada '
     'ao modelo all-MiniLM-L6-v2.'),
    ('O cliente revisado define a coleção regulacoes_revisadas_v1 e o parâmetro hnsw:space como '
     'cosine.',
     'O cliente revisado utiliza uma coleção única e distância de cosseno no índice.'),
    ('solicita n_results=min(k, quantidade_de_documentos), sem implementar',
     'solicita o menor valor entre k e o número de documentos da coleção, sem implementar'),
    ('Suas fontes estão identificadas em app/vector_db/curated.py: orientações',
     'Suas fontes estão identificadas no próprio corpus (Apêndice B, item B.3): orientações'),
    ('Cada registro reúne id, text, source, asset_type e checked_at.',
     'Cada registro reúne identificador, texto, fonte, tipo de ativo e data de verificação.'),
    ('load_initial_regulations insere os registros com upsert; search_evidence devolve '
     'identificador, texto, metadados e distância; search_regulations formata o contexto com '
     'origem e data. O filtro asset_type não restringe',
     'A carga inicial insere os registros sem duplicá-los; a busca devolve identificador, texto, '
     'metadados e distância, e a formatação do contexto acrescenta origem e data. O filtro por '
     'tipo de ativo não restringe'),
    # 5.6 Calculadoras
    ('Para ações, a isenção depende de total mensal informado; para criptoativos nacionais, deixa '
     'de ser decidida pelo valor de uma venda isolada.',
     'Para ações, a isenção depende de total mensal informado; uma venda isolada acima de '
     'R$ 20.000 em operação comum, porém, já afasta a isenção e é calculada sem esse total, que '
     'não é presumido. O resultado é apresentado como estimativa da operação, antes de '
     'compensações e créditos de IRRF. Para criptoativos nacionais, a isenção deixa de ser '
     'decidida pelo valor de uma venda isolada.'),
    ('e o nocional deixa de ser apresentado como recebimento líquido do encerramento.',
     'e o nocional deixa de ser apresentado como recebimento líquido do encerramento. A falta de '
     'IRRF informado não impede a simulação: o campo é exibido como “não informado”, e não como '
     'zero, e nenhum crédito de retenção é considerado.'),
    ('As calculadoras são classes Python em backend/app/calculations. O servidor '
     'mcp_server/server.py importa',
     'As calculadoras são classes Python. O servidor MCP importa'),
    ('As rotas POST /api/trades/process e POST /api/trades/batch utilizam '
     'backend/app/mcp_gateway.py; o chat utiliza o cliente MCP do ciclo em '
     'backend/app/agents/tool_chat.py. O chat registra a venda somente após resultado validado e '
     'finalização normal da explicação. Compras são registradas sem cálculo.',
     'As rotas de processamento individual e em lote do formulário utilizam um gateway MCP; o '
     'chat utiliza o cliente MCP do ciclo de ferramentas (Apêndice B, item B.4). O chat registra '
     'a venda somente quando a mensagem a afirma como realizada, após resultado validado e '
     'finalização normal da explicação. Compras afirmadas são registradas sem cálculo.'),
    # 5.7 Persistência
    ('por meio de get_average_price, em backend/app/storage/repository.py.',
     'por meio da consulta de preço médio da camada de persistência.'),
    ('inicializada vazia quando ele é recriado, inclusive após recarregar a página. Essa '
     'reinicialização visual não exclui os registros do banco.',
     'inicializada vazia quando ele é recriado, inclusive após recarregar a página. O botão '
     'Limpar produz o mesmo efeito. Essa reinicialização visual não exclui os registros do banco.'),
    ('vinculados ao user_id, sem', 'vinculados ao identificador do usuário, sem'),
    # 5.8 MCP e instruções
    ('O servidor MCP, implementado em mcp_server/server.py, expõe', 'O servidor MCP expõe'),
    ('estão registradas em experiment.py.',
     'estão registradas no código do experimento (Apêndice B, item B.6).'),
    # 6.4 / 6.5
    ('judge.py reúne', 'o script de julgamento reúne'),
    ('Os testes estão em backend/tests do projeto consolidado; o executor dos 12 cenários está em '
     'experimentos_historicos/calculator_checks.py. Os arquivos benchmark.json, '
     'baseline_retrieval.json, revised_retrieval.json, api_results e results_per_case.csv '
     'permitem rastrear a avaliação textual. Os comandos de reprodução e o inventário do pacote '
     'são apresentados no Apêndice B.',
     'Os testes automatizados, o executor dos 12 cenários e os arquivos que permitem rastrear a '
     'avaliação textual — benchmark, recuperações das duas configurações, respostas da API e '
     'resultados por caso — estão relacionados no Apêndice B, item B.6. Os comandos de '
     'reprodução constam no item B.13.'),
    ('a existência do tratamento compartilhado em calculate_b3_fees não permite',
     'a existência do cálculo compartilhado de taxas da B3 não permite'),
    # 7.3
    ('Os registros pytest_corrigido.txt, calculadoras_12_reexecutadas.json e '
     'bdr_regressao_corrigida.json documentam a verificação posterior.',
     'Os registros da verificação posterior estão relacionados no Apêndice B, item B.7.'),
    ('O registro está em evidencias/mcp_integracao_20260916/pytest_mcp.txt.',
     'O registro consta no Apêndice B, item B.8.'),
    # 7.5
    ('preservados em Entrega_Final/evidencias/mcp_validacao_claude.',
     'preservados no pacote de evidências (Apêndice B, item B.9).'),
    ('enquanto requirements.txt fixa 0.24.0.', 'enquanto o arquivo de dependências fixava 0.24.0.'),
    ('o log pytest_full_venv_isolado.txt registra', 'o registro da suíte indica'),
    ('O arquivo protocol_evidence.json registra', 'O registro do protocolo documenta'),
    ('Em comparacao_mcp_vs_direto.json, dez casos', 'Na comparação entre MCP e execução direta, dez casos'),
    ('no log server_real_20260916.log.', 'no log do servidor.'),
    ('A inspeção de chat_real/03_venda_fii.json, entretanto,',
     'A inspeção do registro da venda de FII pelo chat, entretanto,'),
    ('declara live_tariffs=false e ausência', 'declara não usar tarifas em tempo real e ausência'),
    ('convenções diferentes para user_id entre endpoints',
     'convenções diferentes para o identificador do usuário entre rotas'),
    ('O registro está em evidencias/tool_use_20260920/pytest.txt.',
     'O registro consta no Apêndice B, item B.10.'),
    # 7.6
    ('sete capturas de interface em evidencias/tool_use_validacao_claude.',
     'sete capturas de interface (Apêndice B, item B.11).'),
    ('O log pytest_suite_limpa.txt contém', 'O registro da instalação limpa contém'),
    (', conforme evidencias/revisao_adendo_tool_use_20260920/pytest.txt.',
     ' (Apêndice B, item B.12).'),
    ('A interface revelou dois defeitos ainda não corrigidos nesta versão. O chat grava sob '
     'user123, enquanto histórico, resumo e DARF consultam o usuário padrão quando o '
     'identificador não é enviado. Assim, uma venda calculada pode coexistir com histórico vazio '
     'e DARF zerado (Figura 13). Em outro caso, a resposta declarou que não havia gravado a '
     'venda, embora o executor tenha confirmado sua persistência (Figura 14). O usuário pode '
     'reenviar a operação e duplicá-la.',
     'A interface revelou dois defeitos na sessão de 20 de setembro. O chat gravava sob user123, '
     'enquanto histórico, resumo e DARF consultavam o usuário padrão quando o identificador não '
     'era enviado. Assim, uma venda calculada podia coexistir com histórico vazio e DARF zerado '
     '(Figura 13). Em outro caso, a resposta declarou que não havia gravado a venda, embora o '
     'executor tenha confirmado sua persistência (Figura 14), o que poderia levar o usuário a '
     'reenviar e duplicar a operação. O primeiro defeito foi corrigido: o identificador passou a '
     'ter origem única no serviço do frontend e a acompanhar todas as chamadas, com um teste que '
     'grava por um caminho e consulta por outro. No segundo, a confirmação de gravação passou a '
     'ser emitida pelo backend, que acrescenta ao início da resposta a indicação de registro, em '
     'vez de deixá-la a cargo do modelo. A instrução do prompt de sistema não foi alterada, e o '
     'texto gerado ainda pode divergir dessa indicação.'),
    ('O relatório vincula o resultado à divergência de user_id entre gravação e consulta;',
     'O relatório vincula o resultado à divergência do identificador do usuário entre gravação e '
     'consulta;'),
    ('A captura não comprova, sozinha, o estado do banco.',
     'A captura não comprova, sozinha, o estado do banco. O comportamento registrado é anterior à '
     'confirmação de gravação emitida pelo backend.'),
    # 8 Limitações e trabalhos futuros
    ('Na Seção 7.6, a interface apresentou divergência de usuário entre gravação e consulta e uma '
     'explicação incompatível com a persistência da venda. Esses achados impedem tratar o '
     'histórico e o DARF exibidos como integralmente confiáveis.',
     'Na Seção 7.6, a interface apresentou divergência de usuário entre gravação e consulta, '
     'posteriormente corrigida, e uma explicação incompatível com a persistência da venda, '
     'mitigada pela confirmação emitida pelo backend. Ainda assim, o histórico e o DARF exibidos '
     'não substituem a apuração mensal, pois não consolidam operações de outras corretoras nem '
     'compensações de prejuízos.'),
    ('A consulta à carteira pelo chat também é limitada. A ferramenta de consulta ao custo médio '
     'fica disponível somente após a extração de uma operação com dados suficientes; não há '
     'ferramenta para recuperar o saldo de um ativo a partir de perguntas como “se eu vender meu '
     'saldo de PETR4, quanto pagarei de imposto?”. Assim, mesmo com compras persistidas, a '
     'pergunta pode receber uma resposta geral sem consulta à posição do usuário. O fluxo não '
     'mantém uma simulação em andamento para solicitar e incorporar os dados faltantes, como '
     'preço e data de venda. Além disso, não há separação explícita entre simulação e registro: '
     'uma venda extraída e calculada com sucesso é persistida pelo agente. Portanto, o chat não '
     'deve ser tratado como simulador de carteira sem efeitos sobre os registros.',
     'A consulta à carteira pelo chat também é limitada. Perguntas que nomeiam um único ativo e '
     'mencionam preço médio, custo médio, histórico, carteira ou saldo são respondidas por '
     'consulta somente leitura ao banco, que devolve o preço médio registrado sem calcular imposto '
     'nem registrar operação. A consulta não informa a quantidade em carteira, e mensagens com '
     'mais de um ativo não seguem esse caminho. O fluxo não mantém uma simulação em andamento '
     'para solicitar e incorporar os dados faltantes, como preço e data de venda; o usuário é '
     'orientado a reenviar a mensagem completa. A gravação passou a depender de formulação '
     'afirmativa, como “comprei”, “vendi” ou “registre”: hipóteses, simulações, negações e datas '
     'futuras são tratadas como simulação, e a resposta informa que nenhuma operação foi '
     'registrada. Como essa separação se baseia em padrões de texto, mensagens ambíguas tendem a '
     'ser tratadas como simulação.'),
    ('Como continuidade, priorizam-se a unificação da identificação do usuário entre chat, '
     'histórico e resumo mensal, a confirmação de gravação pelo backend e a prevenção de '
     'registros duplicados.',
     'Como continuidade, priorizam-se a prevenção de registros duplicados, a revisão da instrução '
     'do prompt sobre o estado de gravação e a consulta da quantidade em carteira pelo chat.'),
]

EV = 'Documentation/TCC/Revisao/Entrega_Final/evidencias'
HIST = 'Documentation/TCC/Revisao/experimentos_historicos'
APPENDIX_TITLE = 'APÊNDICE B – LOCALIZAÇÃO DO CÓDIGO E DAS EVIDÊNCIAS'
APPENDIX_BODY = [
    'Este apêndice relaciona os componentes de código e os registros de evidência citados nos '
    'Capítulos 5 a 7, para que cada afirmação possa ser conferida no pacote entregue. Os caminhos '
    'são relativos à raiz do projeto.',
    'B.1 Interface web: frontend/src/app/components; serviço de chamadas HTTP em '
    'frontend/src/app/services/api.service.ts.',
    'B.2 Orquestração e ciclo de ferramentas: backend/app/agents, incluindo tool_chat.py (ciclo de '
    'ferramentas) e chat_policy.py (separação entre simulação e registro); cliente do SDK em '
    'backend/app/llm/claude_client.py.',
    'B.3 Corpus curado e fontes dos trechos: backend/app/vector_db/curated.py.',
    'B.4 Calculadoras e MCP: backend/app/calculations; servidor MCP em mcp_server/server.py; '
    'gateway MCP do formulário em backend/app/mcp_gateway.py.',
    'B.5 Persistência e consulta de preço médio: backend/app/storage/repository.py.',
    f'B.6 Testes e experimento histórico: backend/tests e frontend/tests; em {HIST}: '
    'calculator_checks.py (12 cenários), experiment.py (instruções e execução), judge.py '
    '(julgamento), benchmark.json, baseline_retrieval.json, revised_retrieval.json, api_results e '
    'results_per_case.csv.',
    f'B.7 Verificação posterior das calculadoras (Seção 7.3): {EV}/correcao_posterior, com '
    'pytest_corrigido.txt, calculadoras_12_reexecutadas.json e bdr_regressao_corrigida.json.',
    f'B.8 Integração MCP de 16 set. 2026: {EV}/mcp_integracao_20260916/pytest_mcp.txt.',
    f'B.9 Verificação complementar da integração MCP, 16–17 set. 2026 (Seção 7.5): '
    f'{EV}/mcp_validacao_claude, com pytest_full_venv_isolado.txt, protocol_evidence.json, '
    'comparacao_mcp_vs_direto.json, server_real_20260916.log e chat_real/03_venda_fii.json.',
    f'B.10 Primeira verificação do ciclo de ferramentas, 20 set. 2026: '
    f'{EV}/tool_use_20260920/pytest.txt.',
    f'B.11 Validação do ciclo de ferramentas e da interface, 20 set. 2026 (Seção 7.6): '
    f'{EV}/tool_use_validacao_claude, com o relatório RELATORIO_TOOL_USE.md, '
    'pytest_suite_limpa.txt, os resultados em JSON e as capturas em capturas_interface.',
    f'B.12 Suíte ampliada após as correções: {EV}/revisao_adendo_tool_use_20260920/pytest.txt.',
    'B.13 Reprodução: a suíte do backend é executada em backend com python -m pytest tests/ -q, '
    'definindo DATABASE_URL para um arquivo SQLite temporário e ANTHROPIC_API_KEY vazia, sem '
    'chamadas a modelos. A regressão do frontend é executada em frontend com node '
    'tests/history-regression.cjs. A aplicação local é iniciada com python -m uvicorn '
    'app.main:app --port 8000, em backend, e npm start, em frontend, com acesso em '
    'http://localhost:4200. A reexecução do benchmark histórico implica novas chamadas pagas aos '
    'modelos e não integra esta entrega.',
]
NEXT_HEADING = 'ANEXO A – DECLARAÇÃO DE USO DE IA'


def set_text(paragraph, text):
    runs = paragraph.runs
    runs[0].text = text
    for run in runs[1:]:
        run._r.getparent().remove(run._r)


def apply(doc):
    """Substitui os trechos e insere o apêndice; confere que nada mais mudou."""
    before = [p._p.xml for p in doc.paragraphs]
    paragraphs = doc.paragraphs
    touched = set()
    for old, new in REPLACEMENTS:
        hits = [i for i, p in enumerate(paragraphs) if old in p.text]
        assert len(hits) == 1, (len(hits), old[:70])
        p = paragraphs[hits[0]]
        assert p.text.count(old) == 1, old[:70]
        set_text(p, p.text.replace(old, new))
        touched.add(hits[0])
    mid = [p._p.xml for p in doc.paragraphs]
    assert len(mid) == len(before)
    assert all(mid[i] == before[i] for i in range(len(before)) if i not in touched),         'parágrafo não previsto foi alterado'
    assert not any(p.text.strip() == APPENDIX_TITLE for p in doc.paragraphs)
    anchors = [i for i, p in enumerate(doc.paragraphs) if p.text.strip() == NEXT_HEADING]
    assert len(anchors) == 1 and doc.paragraphs[anchors[0]].style.name == 'TCC Capitulo'
    k = anchors[0]
    anchor = doc.paragraphs[k]
    anchor.insert_paragraph_before(APPENDIX_TITLE, 'TCC Capitulo')
    for t in APPENDIX_BODY:
        anchor.insert_paragraph_before(t, 'TCC Corpo')
    after = [p._p.xml for p in doc.paragraphs]
    n = 1 + len(APPENDIX_BODY)
    assert after[:k] + after[k + n:] == mid, 'inserção alterou outro parágrafo'
    return len(touched)


docs = [Document(WORD), Document(TEMPLATE)]
assert [p.text for p in docs[0].paragraphs] == [p.text for p in docs[1].paragraphs]

backup = ROOT / 'backups' / ('antes_consistencia_codigo_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
for file in (WORD, WORD.with_suffix('.pdf'), TEMPLATE, MD):
    copy2(file, backup / file.name)

for file, doc in zip((WORD, TEMPLATE), docs):
    changed = apply(doc)
    doc.save(file)
    print(file.name, 'parágrafos alterados:', changed)

blocks = ['<!-- Fonte editorial única. Preserve IDs; capas, tabelas e figuras são mantidas no modelo. -->']
for i, p in enumerate(docs[1].paragraphs):
    if not p.text.strip() or p._p.xpath('.//w:fldChar|.//w:fldSimple|.//w:drawing') or p.style.name.lower().startswith('toc'):
        continue
    prefix = '# ' if p.style.name in ('TCC Capitulo', 'TCC Preliminar') else '## ' if p.style.name == 'TCC Secao' else ''
    blocks.append(f'<!-- p:{i} -->\n{prefix}{p.text}')
MD.write_text('\n\n'.join(blocks) + '\n', encoding='utf8')
print(backup)
