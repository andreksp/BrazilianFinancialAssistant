"""Inserção pontual aprovada em limitações e trabalhos futuros."""
from pathlib import Path
from datetime import datetime
from shutil import copy2
from docx import Document

ROOT = Path(__file__).resolve().parent
word = ROOT / 'Entrega_Final/Monografia_Revisada_para_Orientador.docx'
template = ROOT / 'modelo/modelo_sincronizado.docx'
md = ROOT / 'manuscrito.md'
changes = [
    ('A cobertura operacional também é parcial:',
     'A cobertura de derivativos é parcial. No segmento de contratos futuros, o protótipo contempla apenas os minicontratos de índice e de dólar (WIN e WDO). Além desses contratos, contempla o tratamento simplificado de opções apresentado neste trabalho. A diversidade de especificações contratuais, formas de liquidação e eventos operacionais limita a generalização dos cálculos para outros produtos.'),
    ('No plano de integração,',
     'Como trabalho futuro, propõe-se ampliar gradualmente a cobertura de derivativos, incluindo outros contratos futuros e modalidades ainda não contempladas. Essa expansão deverá considerar as particularidades de cada produto e ser acompanhada de revisão das regras, implementação de cálculos específicos e testes com cenários representativos, preferencialmente validados por especialistas.'),
]
docs = [Document(word), Document(template)]
def texts(d):
    return [p.text for p in d.paragraphs if p.text.strip() and not p.style.name.lower().startswith('toc') and not p._p.xpath('.//w:fldChar|.//w:fldSimple')]
assert texts(docs[0]) == texts(docs[1]), 'Word e modelo divergentes; revisar antes de editar.'
for d in docs:
    for anchor, content in changes:
        assert content not in texts(d), 'Trecho já inserido.'
        assert sum(p.text.startswith(anchor) for p in d.paragraphs) == 1
backup = ROOT / 'backups' / ('antes_escopo_derivativos_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
for p in (word, word.with_suffix('.pdf'), template, md):
    copy2(p, backup / p.name)
for path, d in zip((word, template), docs):
    protected = [p._p.xml for p in d.paragraphs[:84]]
    before = texts(d)
    for anchor, content in changes:
        p = next(p for p in d.paragraphs if p.text.startswith(anchor))
        p.insert_paragraph_before(content, 'TCC Corpo')
    assert [p._p.xml for p in d.paragraphs[:84]] == protected
    assert [t for t in texts(d) if t not in [c for _, c in changes]] == before
    assert len(d.inline_shapes) == 14 and len(d.tables) == 4
    d.save(path)
blocks = ['<!-- Fonte editorial única. Preserve IDs; capas, tabelas e figuras são mantidas no modelo. -->']
for i, p in enumerate(docs[1].paragraphs):
    if not p.text.strip() or p._p.xpath('.//w:fldChar|.//w:fldSimple|.//w:drawing') or p.style.name.lower().startswith('toc'):
        continue
    prefix = '# ' if p.style.name in ('TCC Capitulo', 'TCC Preliminar') else '## ' if p.style.name == 'TCC Secao' else ''
    blocks.append(f'<!-- p:{i} -->\n{prefix}{p.text}')
md.write_text('\n\n'.join(blocks) + '\n', encoding='utf8')
print('Backup:', backup)
print('Dois parágrafos inseridos; conteúdo anterior preservado.')
