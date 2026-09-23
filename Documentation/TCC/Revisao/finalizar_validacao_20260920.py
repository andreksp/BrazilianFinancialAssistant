"""Align historical scope references after adding Section 7.6."""
from pathlib import Path
from copy import deepcopy
from docx import Document

r = Path(__file__).resolve().parent
path = r / 'modelo/modelo_sincronizado.docx'
d = Document(path)
changes = {
    'não foram produzidas novas capturas nem alegada uma revalidação visual de ponta a ponta nesta edição.':
    'naquela etapa, não houve nova revalidação visual de ponta a ponta. As capturas posteriores estão na Seção 7.6.',
    'As capturas reais já estão incorporadas à Seção 7.4, incluindo resultados e recusas observados no navegador.':
    'As capturas reais estão nas Seções 7.4 e 7.6, com resultados e recusas observados no navegador.',
    'A revisão editorial atualiza o sumário e preserva os resultados históricos; não elimina as limitações de validação e de cobertura do protótipo.':
    'A verificação posterior de 146 testes, os ensaios com modelos reais e os defeitos de interface são discutidos na Seção 7.6. O sumário foi atualizado; os resultados históricos foram preservados.',
}
md = (r / 'manuscrito.md').read_text(encoding='utf8')
for old, new in changes.items():
    found = [p for p in d.paragraphs if old in p.text]
    assert len(found) == 1 and md.count(old) == 1
    p = found[0]
    text = p.text.replace(old, new)
    props = deepcopy(p.runs[0]._r.rPr) if p.runs[0]._r.rPr is not None else None
    p.clear()
    run = p.add_run(text)
    if props is not None:
        run._r.insert(0, props)
    md = md.replace(old, new)
d.save(path)
(r / 'manuscrito.md').write_text(md, encoding='utf8')
