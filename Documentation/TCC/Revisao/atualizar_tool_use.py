from pathlib import Path
from copy import deepcopy
from datetime import datetime
import shutil,re
from docx import Document
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

R=Path(__file__).resolve().parent
B=R/'backups'/('antes_tool_use_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
B.mkdir(parents=True)
for name in ['modelo/modelo_sincronizado.docx','Entrega_Final/Monografia_Revisada_para_Orientador.docx','Entrega_Final/Monografia_Revisada_para_Orientador.pdf','manuscrito.md','figures/arquitetura_mcp.png','figures/arquitetura_mcp.svg']:
    shutil.copy2(R/name,B/Path(name).name)
d=Document(R/'modelo/modelo_sincronizado.docx')
protected=[p._p.xml for p in d.paragraphs[:70]]
changes={
'Na Figura 2 é apresentada a arquitetura após':'Na Figura 2 é apresentada a arquitetura com seleção de ferramentas pelo LLM no chat, implementada em 20 de setembro de 2026. Após classificação e extração da operação, o modelo solicita ferramentas e o backend valida e executa as chamadas. As ferramentas MCP reutilizam as calculadoras; o resultado retorna ao modelo para explicação. No formulário, a sequência de chamadas permanece determinada pelo backend. Compras e perguntas sem operação mantêm seus fluxos anteriores, sem acionar esse ciclo de cálculo.',
'A orquestração está implementada':'A orquestração está implementada em classes Python, em app/agents, e utiliza o cliente do SDK da Anthropic em app/llm/claude_client.py. Orchestrator.process solicita classificação da intenção e extração da operação antes de delegar ao agente especializado. Para vendas ou remuneração extraídas, o agente inicia o ciclo de ferramentas em app/agents/tool_chat.py. O modelo explicador recebe os dados da operação, o contexto documental e as ferramentas disponíveis, com tool_choice configurado como auto. Solicitações tool_use são respondidas com blocos tool_result, até a explicação final ou um limite de execução. Perguntas sem operação não entram nesse ciclo.',
'As calculadoras são classes Python em':'As calculadoras são classes Python em backend/app/calculations. O servidor mcp_server/server.py importa e reutiliza essas classes, sem reproduzir suas fórmulas. As rotas POST /api/trades/process e POST /api/trades/batch utilizam backend/app/mcp_gateway.py; o chat utiliza o cliente MCP do ciclo em backend/app/agents/tool_chat.py. O chat registra a venda somente após resultado validado e finalização normal da explicação. Compras são registradas sem cálculo. Falhas MCP não são substituídas por execução direta das calculadoras.',
'Quanto à memória do agente,':'Quanto à memória do agente, o protótipo distingue o histórico conversacional dos dados estruturados das operações. Mensagens e respostas são persistidas por usuário, mas não são reinseridas nos prompts de solicitações subsequentes. Não há sumarização nem janela de conversas anteriores. Classificação, extração e perguntas documentais utilizam chamadas independentes. No ciclo de ferramentas de uma venda, as mensagens do modelo e os resultados tool_result são mantidos apenas durante a solicitação corrente, permitindo que a explicação considere os retornos das ferramentas. Esse contexto temporário não constitui memória conversacional entre mensagens do usuário.',
'A integração utiliza o SDK Python MCP':'A integração utiliza o SDK Python MCP 1.28.0 e transporte stdio. Um subprocesso local executa o servidor, sem expor serviço HTTP MCP. No formulário, o gateway determina a sequência e mantém seu limite global de trinta segundos. No chat, o cliente inicializa uma sessão, confere a disponibilidade de fee_policy e calculate_trade e oferece ao LLM versões dessas ferramentas vinculadas à operação corrente. O backend injeta os argumentos completos ao chamar o MCP; o modelo não pode substituir usuário, ativo ou valores financeiros nessa etapa. A consulta consultar_preco_medio é uma ferramenta local de leitura no backend, não uma terceira ferramenta publicada pelo servidor MCP.',
'A ferramenta fee_policy não realiza':'A ferramenta fee_policy não realiza consulta tarifária em tempo real: declara a origem interna da política e a ausência de vigência validada. O host exige sua consulta antes do cálculo e, quando necessário, a consulta do custo médio. O ciclo permite até seis rodadas do modelo e oito solicitações de ferramentas; chamadas repetidas concluídas reutilizam o resultado da solicitação corrente. Chamadas ao modelo têm timeout de trinta segundos sem repetição automática; a sessão MCP tem timeout de leitura de vinte segundos. Nomes ou argumentos não autorizados são recusados. Resposta truncada, ausência de cálculo validado e esgotamento dos limites impedem o registro da venda. A seleção pelo LLM é, portanto, delimitada por controles do backend e não equivale a autonomia irrestrita.',
'Outras evoluções incluem corrigir e revalidar':'Outras evoluções incluem validar a seleção de ferramentas com modelos reais e navegador, medir concorrência no serviço completo, tornar reproduzível a instalação das dependências publicadas e uniformizar a semântica dos resultados. A rota de chat foi convertida para execução síncrona em threadpool do framework, retirando o processamento bloqueante do corpo de uma rota assíncrona; essa alteração ainda exige medição de carga e latência. A execução real da Seção 7.5 antecede o ciclo de ferramentas de 20 de setembro e não demonstra suas escolhas pelo modelo. Também permanecem a validação de Docker e Poetry e o versionamento de tarifas com fontes e vigência.'
}
for prefix,new in changes.items():
    found=[p for p in d.paragraphs if p.text.startswith(prefix)]
    assert len(found)==1,(prefix,len(found))
    p=found[0];props=deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
    p.clear();run=p.add_run(new)
    if props is not None:run._r.insert(0,props)
log=Path(r'C:\Users\andre\tcc_revisao\mcp_work\pytest_mcp.txt').read_text(encoding='utf8')
count=re.search(r'(\d+) passed, 2 warnings',log).group(1)
anchor=next(p for p in d.paragraphs if p.text=='8 CONCLUSÃO' and p.runs)
reference=next(p for p in d.paragraphs if p.text.startswith('Após a integração, foi realizada'))
text=f'Em 20 de setembro de 2026, foi implementado o ciclo de seleção de ferramentas pelo modelo no chat. A verificação local posterior registrou {count} testes aprovados e dois avisos, em ambiente já instalado, com banco temporário e sem chamadas pagas de IA. Os testes adicionais empregaram respostas programadas do modelo e incluíram comunicação com servidor MCP real, bloqueio de argumentos indevidos, limites, resposta truncada, identificação da operação e ausência de gravação em falhas. O registro está em evidencias/tool_use_20260920/pytest.txt. Esses testes verificam o código que processa tool_use e tool_result, mas não comprovam a qualidade das escolhas de um modelo real. Não foram produzidos novos resultados de benchmark nem novas capturas de navegador para essa implementação.'
p=anchor.insert_paragraph_before(text,style=reference.style)
if reference._p.pPr is not None:p._p.insert(0,deepcopy(reference._p.pPr))
if reference.runs[0]._r.rPr is not None:p.runs[0]._r.insert(0,deepcopy(reference.runs[0]._r.rPr))

source=Path(r'C:\Users\andre\tcc_revisao\mcp_work\update_document.py').read_text(encoding='utf8')
diagram=source.split('# Diagram is generated from code, with vector source retained as SVG.\n')[1].split('shape=d.inline_shapes')[0]
diagram=diagram.replace('ax.set_ylim(0,6)','ax.set_ylim(-.15,6)').replace('Servidor MCP runtime','Servidor MCP').replace(r'\nMCP legado: fora deste fluxo.','')
diagram=diagram.replace(r'LLM\nInterpreta e explica',r'LLM\nSeleciona ferramentas\nno chat e explica')
diagram=diagram.replace(r'Gateway MCP\nDecisão no backend',r'Cliente MCP\nChat: ciclo tool_use\nFormulário: sequência fixa')
diagram=diagram.replace(r'SQLite\nOperações e histórico',r'SQLite\nCusto médio e histórico')
exec(diagram)
shape=d.inline_shapes[1];rel=shape._inline.graphic.graphicData.pic.blipFill.blip.embed
d.part.related_parts[rel]._blob=picture.read_bytes()
shape._inline.docPr.set('descr','LLM seleciona ferramentas no chat; backend valida chamadas MCP e consulta local de custo médio; formulário usa sequência fixa.')
assert protected==[p._p.xml for p in d.paragraphs[:70]]
d.save(R/'modelo/modelo_sincronizado.docx')
blocks=['<!-- Fonte editorial única. Preserve IDs; capas, tabelas e figuras são mantidas no modelo. -->']
for i,p in enumerate(d.paragraphs):
    if not p.text.strip() or p._p.xpath('.//w:fldChar|.//w:fldSimple|.//w:drawing') or p.style.name.lower().startswith('toc'):continue
    prefix='# ' if p.style.name in ('TCC Capitulo','TCC Preliminar') else '## ' if p.style.name=='TCC Secao' else ''
    blocks.append(f'<!-- p:{i} -->\n{prefix}{p.text}')
(R/'manuscrito.md').write_text('\n\n'.join(blocks)+'\n',encoding='utf8')
out=R/'Entrega_Final/evidencias/tool_use_20260920';out.mkdir(parents=True,exist_ok=True)
(out/'pytest.txt').write_text(log,encoding='utf8')
print('Fontes e diagrama atualizados. Testes:',count,'Backup:',B)
