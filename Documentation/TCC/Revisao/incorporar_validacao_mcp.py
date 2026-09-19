"""Incorpora evidências já existentes; não executa testes nem chamadas de IA."""
from pathlib import Path
from datetime import datetime
from copy import deepcopy
import json, re, shutil
from docx import Document

R = Path(__file__).resolve().parent
E = R/'Entrega_Final/evidencias/mcp_validacao_claude'
cfg = json.loads((R/'correcao_20260913/sync_config.json').read_text(encoding='utf8'))
d = Document(R/cfg['template'])
assert not any(p.text.startswith('7.5 Verificação complementar') for p in d.paragraphs), 'Já incorporado'
cases = json.loads((E/'comparacao_mcp_vs_direto.json').read_text(encoding='utf8'))
assert len(cases)==10 and all(x['mcp_matches_direct'] and x['expected_ok'] for x in cases)
con = json.loads((E/'resultados_concorrencia_eventloop.json').read_text(encoding='utf8'))
assert con['async_concurrent']['n_ok']==8
assert '100 passed' in (E/'pytest_full_venv_isolado.txt').read_text(encoding='utf8')
assert len(list((E/'formulario_real').glob('*.json')))==7
assert len(list((E/'chat_real').glob('*.json')))==3
protected = [p._p.xml for p in d.paragraphs[:70]]
B = R/'backups'/('antes_evidencias_claude_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
B.mkdir(parents=True)
for name in [cfg['template'],cfg['output'],'manuscrito.md','Entrega_Final/Monografia_Revisada_para_Orientador.pdf']:
    shutil.copy2(R/name,B/Path(name).name)

def replace(prefix, text):
    found=[p for p in d.paragraphs if p.text.startswith(prefix)]
    assert len(found)==1,(prefix,len(found))
    p=found[0]
    rp=deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
    p.clear();run=p.add_run(text)
    if rp is not None:run._r.insert(0,rp)

for p in d.paragraphs:
    if p.text.startswith('Os resultados são organizados'):
        replace('Os resultados são organizados',p.text.replace('Os benchmarks e as capturas apresentados neste capítulo antecedem','Os benchmarks e as capturas das Seções 7.1 a 7.4 antecedem')+' A Seção 7.5 apresenta uma verificação complementar da integração MCP, com registros próprios e sem alterar o benchmark histórico.')
        break
replace('Outras evoluções incluem validar o fluxo MCP completo', 'Outras evoluções incluem corrigir e revalidar o bloqueio do event loop no chat, tornar reproduzível a instalação das dependências publicadas e uniformizar a semântica dos campos de resultado. A verificação complementar da Seção 7.5 demonstrou o fluxo MCP com modelos de linguagem pela API, mas não substitui testes com navegador, avaliações de usuários ou estudo de carga. Permanecem necessários o teste do timeout interno, a validação de Docker e Poetry e o versionamento de tarifas com fontes e vigência. Cada mudança deve ser acompanhada de novos testes e revisão especializada, preservando as evidências anteriores.')
anchor=next(p for p in d.paragraphs if p.text=='8 CONCLUSÃO')
body_style=next(p.style for p in d.paragraphs if p.text.startswith('Os resultados são organizados'))
heading_style=next(p.style for p in d.paragraphs if p.text.startswith('7.4 Demonstração'))
anchor.insert_paragraph_before('7.5 Verificação complementar da integração MCP',style=heading_style)
paragraphs=[
'Após a integração, foi realizada uma rodada adicional por Claude Code, com artefatos registrados na sessão de 16–17 de setembro de 2026. A análise a seguir confronta o relatório com os arquivos JSON e logs preservados em Entrega_Final/evidencias/mcp_validacao_claude. Trata-se de verificação assistida por IA e revisão documental das evidências, não de auditoria tributária independente. Não foram reexecutados o benchmark histórico nem o julgamento LLM-as-a-Judge; os resultados desta rodada não alteram seus denominadores.',
'A reprodução em ambiente virtual isolado, com Python 3.11.9 no Windows, revelou incompatibilidade no arquivo de dependências: o SDK MCP 1.28.0 requer uvicorn a partir de 0.31.1, enquanto requirements.txt fixa 0.24.0. Segundo o registro de instalação, a resolução só foi concluída após flexibilizar essa restrição no ambiente de teste. Nesse ambiente, o log pytest_full_venv_isolado.txt registra 100 testes aprovados, dois avisos e 19,87 segundos. Assim, a aprovação da suíte não comprova a instalação limpa do arquivo publicado; a execução anterior havia utilizado um ambiente já existente. Nenhuma correção de código é atribuída a esta rodada.',
'O arquivo protocol_evidence.json registra inicialização da sessão, listagem e chamadas das ferramentas fee_policy e calculate_trade por stdio, com subprocessos reais. Em comparacao_mcp_vs_direto.json, dez casos abrangem as oito categorias de ativos implementadas. Nos campos efetivamente comparados — ganho bruto, imposto, retenção, alíquota e isenção — houve concordância entre MCP e execução direta em todos os casos. Os gabaritos reutilizam regras do levantamento anterior, sem nova consulta independente a fontes oficiais. A comparação verifica a preservação dos resultados selecionados pelo transporte, não a igualdade de todos os campos nem a correção integral das calculadoras.',
'Os registros de falha documentam recusas por dados obrigatórios ausentes, entradas inválidas, servidor ausente e resposta incompatível com o esquema. No caso de custo médio ausente, a consulta posterior ao histórico retornou vazia. O teste HTTP de NaN foi interrompido pelo serializador; outro teste verificou sua rejeição diretamente no modelo de entrada. O cancelamento e um limite externo de cinco segundos foram exercitados, mas o timeout interno de trinta segundos não foi observado até expirar. O lote parcial retornou apenas a venda válida, sem apresentar ao cliente um resultado individual para a venda rejeitada. Esses testes possuem escopos diferentes e não devem ser condensados em uma taxa única de sucesso.',
'No teste assíncrono, oito chamadas concorrentes ao gateway foram concluídas com resultados isolados em 0,545 segundo para o conjunto, sem processos órfãos detectados após a rajada. Esse tempo não é a latência individual de cada requisição. Já a reprodução do padrão síncrono utilizado pelo chat apresentou chamada de 0,368 segundo e intervalo máximo de 0,400 segundo entre sinais periódicos de atividade do event loop. O resultado evidencia bloqueio durante a chamada nesse teste local. A execução do mesmo wrapper em uma thread separada apresentou intervalo máximo de 0,063 segundo, constituindo um controle experimental, não uma correção aplicada. Não foi realizado estudo de carga do serviço completo.',
'A execução do backend real produziu sete respostas da API estruturada e três respostas de chat, com registros HTTP e chamadas MCP no log server_real_20260916.log. Os casos estruturados incluíram ações, FII, criptoativos, futuros WIN e WDO e remuneração de empréstimo de ações. No chat, foram enviadas uma pergunta geral, uma compra de cinquenta cotas de HGLG11 a R$ 100 e uma venda dessas cotas a R$ 110. A venda recuperou o custo da compra registrada e retornou ganho bruto de R$ 500 e imposto de R$ 100. Há, portanto, evidência de encadeamento entre interpretação, persistência, cálculo MCP e explicação. Não há novas capturas de tela: chamadas HTTP não validam a interação ou a apresentação no navegador.',
'A inspeção de chat_real/03_venda_fii.json, entretanto, impede classificar a resposta como integralmente correta. A explicação apresenta ganho de R$ 500, imposto de R$ 100 e custos de R$ 1,86, mas denomina R$ 498,14 como ganho líquido. Pelas próprias parcelas exibidas, subtrair imposto e custos produziria R$ 398,14. O valor de R$ 498,14 corresponde ao resultado antes do imposto, refletindo a ambiguidade do campo ganho_prejuizo_liquido, cujo valor estruturado é 498,1355. Além disso, o texto salvo termina incompleto. A causa dessa interrupção não é demonstrada pelo arquivo. O caso comprova a execução do fluxo e simultaneamente uma inconsistência entre rótulo, composição aritmética e explicação; não representa uma nova medida de acurácia do chat.',
'A política retornada declara live_tariffs=false e ausência de vigência validada. Permanecem estimativas legadas quando não há custos informados, sem comprovação de tarifas atuais. A inspeção registrada também aponta fallback inseguro nas calculadoras isoladas de FII e opções, interceptado pelo servidor MCP no fluxo testado, e um comentário sobre isenção em opções incompatível com o comportamento do código. Esse comentário não é adotado como fundamento tributário. Outras limitações incluem convenções diferentes para user_id entre endpoints e advertência genérica sobre tarifas mesmo para ativos que não usam essa tabela. O custo das chamadas de IA desta rodada não foi medido em tokens; a estimativa informal do executor não é incorporada como resultado financeiro medido.'
]
for text in paragraphs:anchor.insert_paragraph_before(text,style=body_style)
assert protected==[p._p.xml for p in d.paragraphs[:70]], 'Preliminares alteradas'
d.save(R/cfg['template'])
blocks=['<!-- Fonte editorial única. Preserve IDs; capas, tabelas e figuras são mantidas no modelo. -->']
for i,p in enumerate(d.paragraphs):
    if not p.text.strip() or p._p.xpath('.//w:fldChar|.//w:fldSimple|.//w:drawing') or p.style.name.lower().startswith('toc'):continue
    prefix='# ' if p.style.name in ('TCC Capitulo','TCC Preliminar') else '## ' if p.style.name=='TCC Secao' else ''
    blocks.append(f'<!-- p:{i} -->\n{prefix}{p.text}')
(R/'manuscrito.md').write_text('\n\n'.join(blocks)+'\n',encoding='utf8')
print('Fontes atualizadas; backup:',B)
