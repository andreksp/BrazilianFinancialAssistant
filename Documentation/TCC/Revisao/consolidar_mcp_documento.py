from pathlib import Path
from copy import deepcopy
from datetime import datetime
import shutil, json
from docx import Document
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

R=Path(__file__).resolve().parent
B=R/'backups'/('antes_mcp_unico_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
B.mkdir(parents=True)
for name in ['modelo/modelo_sincronizado.docx','Entrega_Final/Monografia_Revisada_para_Orientador.docx','Entrega_Final/Monografia_Revisada_para_Orientador.pdf','manuscrito.md','figures/arquitetura_mcp.png','figures/arquitetura_mcp.svg']:
    shutil.copy2(R/name,B/Path(name).name)
d=Document(R/'modelo/modelo_sincronizado.docx')
protected=[p._p.xml for p in d.paragraphs[:70]]
for p in d.paragraphs:
    new=p.text.replace('mcp_server/runtime_server.py','mcp_server/server.py').replace(' O servidor legado de apoio ao desenvolvimento permanece separado e não integra esse caminho.','')
    if new.startswith('Dois servidores têm papéis distintos.'):
        new='O servidor MCP, implementado em mcp_server/server.py, expõe as ferramentas fee_policy e calculate_trade para execução pelo backend. A primeira informa a política de custos; a segunda valida as entradas e reutiliza a calculadora correspondente ao ativo. Não há acesso ao banco operacional nem chamada a LLM nesse servidor. A configuração MCP do projeto e o gateway do backend utilizam esse mesmo ponto de entrada.'
    if new!=p.text:
        props=deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
        p.clear();r=p.add_run(new)
        if props is not None:r._r.insert(0,props)
source=Path(r'C:\Users\andre\tcc_revisao\mcp_work\update_document.py').read_text(encoding='utf8')
diagram=source.split('# Diagram is generated from code, with vector source retained as SVG.\n')[1].split('shape=d.inline_shapes')[0]
diagram=diagram.replace('ax.set_ylim(0,6)','ax.set_ylim(-.15,6)').replace('Servidor MCP runtime','Servidor MCP').replace(r'\nMCP legado: fora deste fluxo.','')
exec(diagram)
shape=d.inline_shapes[1];rel=shape._inline.graphic.graphicData.pic.blipFill.blip.embed
d.part.related_parts[rel]._blob=picture.read_bytes()
assert protected==[p._p.xml for p in d.paragraphs[:70]]
d.save(R/'modelo/modelo_sincronizado.docx')
blocks=['<!-- Fonte editorial única. Preserve IDs; capas, tabelas e figuras são mantidas no modelo. -->']
for i,p in enumerate(d.paragraphs):
    if not p.text.strip() or p._p.xpath('.//w:fldChar|.//w:fldSimple|.//w:drawing') or p.style.name.lower().startswith('toc'):continue
    prefix='# ' if p.style.name in ('TCC Capitulo','TCC Preliminar') else '## ' if p.style.name=='TCC Secao' else ''
    blocks.append(f'<!-- p:{i} -->\n{prefix}{p.text}')
(R/'manuscrito.md').write_text('\n\n'.join(blocks)+'\n',encoding='utf8')
print('Documento e diagrama consolidados. Backup:',B)
