from pathlib import Path
from PIL import Image, ImageDraw
from docx import Document
import fitz, re, json
R=Path(__file__).resolve().parents[1]
doc=Document(R/'Entrega_Final/Monografia_Revisada_para_Orientador.docx')
text='\n'.join(p.text for p in doc.paragraphs)
assert '94 testes aprovados' in text
assert 'apenas FII e a remuneração do doador em empréstimo de ações são hoje operáveis' not in text
assert 'inserir capturas de tela reais da interface Angular após conexão' not in text
assert 'bilhões de documentos' not in text
assert len(doc.tables)==4 and len(doc.inline_shapes)==10
md=(R/'manuscrito.md').read_text(encoding='utf8')
chunks=re.split(r'<!-- p:(\d+) -->\s*\n',md)
template=Document(R/json.loads((R/'correcao_20260913/sync_config.json').read_text(encoding='utf8'))['template'])
for k in range(1,len(chunks),2):
    value=re.sub(r'^#{1,2} ','',chunks[k+1].strip())
    assert value==template.paragraphs[int(chunks[k])].text
pdf=fitz.open(R/'Entrega_Final/Monografia_Revisada_para_Orientador.pdf')
print('Pages',len(pdf),'Images',len(doc.inline_shapes),'Tables',len(doc.tables))
for i,p in enumerate(pdf): print(i+1,p.get_text()[:85].replace('\n',' '))
files=[R/f'correcao_20260913/pages_sincronizadas/page-{i+1:02d}.png' for i in range(len(pdf))]
for start in range(0,len(files),12):
    sheet=Image.new('RGB',(1200,1640),'#aaa')
    draw=ImageDraw.Draw(sheet)
    for j,path in enumerate(files[start:start+12]):
        im=Image.open(path); im.thumbnail((290,380))
        x=(j%4)*300;y=(j//4)*540
        sheet.paste(im,(x,y+25));draw.text((x+5,y+5),path.stem,fill='black')
    sheet.save(R/f'correcao_20260913/pages_sincronizadas/contact-{start//12}.png')
