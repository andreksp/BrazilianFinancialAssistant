from pathlib import Path
from copy import deepcopy
from docx import Document
R=Path(__file__).resolve().parent
p=R/'modelo/modelo_sincronizado.docx'
d=Document(p)
src=next(p for p in d.paragraphs if p.text.startswith('7.4 Demonstração') and p.runs and not p.style.name.lower().startswith('toc'))
dst=next(p for p in d.paragraphs if p.text.startswith('7.5 Verificação'))
dst.style=src.style
if dst._p.pPr is not None:dst._p.remove(dst._p.pPr)
if src._p.pPr is not None:dst._p.insert(0,deepcopy(src._p.pPr))
if src.runs[0]._r.rPr is not None:
    dst.runs[0]._r.insert(0,deepcopy(src.runs[0]._r.rPr))
d.save(p)
print('Formatação do título alinhada às demais seções.')
