"""Documenta a memória implementada, sem alterar código ou resultados."""
from pathlib import Path
from datetime import datetime
from copy import deepcopy
import json, shutil
from docx import Document

R=Path(__file__).resolve().parent
cfg=json.loads((R/'correcao_20260913/sync_config.json').read_text(encoding='utf8'))
d=Document(R/cfg['template'])
assert not any(p.text.startswith('Quanto à memória do agente,') for p in d.paragraphs), 'Texto já incorporado'
B=R/'backups'/('antes_memoria_agente_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
B.mkdir(parents=True)
for file in [cfg['template'],cfg['output'],'manuscrito.md','Entrega_Final/Monografia_Revisada_para_Orientador.pdf']:
    shutil.copy2(R/file,B/Path(file).name)
protected=[p._p.xml for p in d.paragraphs[:70]]
reference=next(p for p in d.paragraphs if p.text.startswith('A persistência operacional utiliza'))
anchor=d.paragraphs[d.paragraphs.index(reference)+1] if False else None
idx=next(i for i,p in enumerate(d.paragraphs) if p.text.startswith('A persistência operacional utiliza'))
anchor=d.paragraphs[idx+1]
texts=[
'Quanto à memória do agente, o protótipo distingue o histórico conversacional dos dados estruturados das operações. As mensagens e respostas são persistidas no banco relacional, associadas ao identificador do usuário, mas não são reinseridas nos prompts das chamadas subsequentes. Não são empregados mecanismos de sumarização nem janelas de mensagens anteriores. Cada chamada ao modelo utiliza uma única mensagem construída para a solicitação corrente, acompanhada das instruções de sistema e, quando pertinente, de trechos recuperados da base documental ou de resultados de cálculo. Esse comportamento está implementado no método ClaudeClient._call_model, em backend/app/llm/claude_client.py.',
'A continuidade entre operações é obtida pela consulta aos registros financeiros persistidos, e não pela recuperação textual das conversas. Ao processar uma venda, o agente pode consultar o preço médio calculado a partir das operações anteriores do mesmo usuário e ativo, por meio de get_average_price, em backend/app/storage/repository.py. Assim, utilizar uma compra registrada em uma interação anterior não significa que o modelo recebeu ou recordou o diálogo correspondente. A recuperação documental no ChromaDB fornece contexto regulatório, não memória das mensagens do usuário.',
'Na interface atual, as mensagens exibidas são mantidas em uma lista local do componente de chat, inicializada vazia quando ele é recriado, inclusive após recarregar a página. Essa reinicialização visual não exclui os registros do banco. O backend oferece consulta ao histórico por usuário, mas o componente não a utiliza para restaurar automaticamente a conversa, e o fluxo de geração não a utiliza para compor prompts. Não há identificação explícita de sessões de conversa separadas: os registros são vinculados ao user_id, sem um identificador próprio de cada novo chat.'
]
for text in texts:
    p=anchor.insert_paragraph_before(text,style=reference.style)
    if p._p.pPr is not None:p._p.remove(p._p.pPr)
    if reference._p.pPr is not None:p._p.insert(0,deepcopy(reference._p.pPr))
    if reference.runs and reference.runs[0]._r.rPr is not None:p.runs[0]._r.insert(0,deepcopy(reference.runs[0]._r.rPr))
p=next(p for p in d.paragraphs if p.text.startswith('A cobertura operacional também é parcial'))
r=p.add_run(' A ausência de memória conversacional também limita perguntas de continuidade, como “e se eu vender metade disso?”, pois não há recuperação explícita da mensagem anterior para resolver a referência. O histórico persistido permite consulta aos registros, mas não equivale a suporte a diálogos contextualizados entre múltiplos turnos.')
if p.runs[0]._r.rPr is not None:r._r.insert(0,deepcopy(p.runs[0]._r.rPr))
assert protected==[p._p.xml for p in d.paragraphs[:70]]
d.save(R/cfg['template'])
blocks=['<!-- Fonte editorial única. Preserve IDs; capas, tabelas e figuras são mantidas no modelo. -->']
for i,p in enumerate(d.paragraphs):
    if not p.text.strip() or p._p.xpath('.//w:fldChar|.//w:fldSimple|.//w:drawing') or p.style.name.lower().startswith('toc'):continue
    prefix='# ' if p.style.name in ('TCC Capitulo','TCC Preliminar') else '## ' if p.style.name=='TCC Secao' else ''
    blocks.append(f'<!-- p:{i} -->\n{prefix}{p.text}')
(R/'manuscrito.md').write_text('\n\n'.join(blocks)+'\n',encoding='utf8')
print('Seções 5.7 e 8.2 atualizadas. Backup:',B)
