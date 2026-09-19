"""Build reviewed Word from manuscrito.md; no new model calls or evidence.
Preserve paragraph IDs. For structural changes update the template and ID map.
"""
from pathlib import Path
from copy import deepcopy
from datetime import datetime
import json, re, shutil
from docx import Document
from docx.shared import Pt

ROOT = Path(__file__).resolve().parent
config = json.loads((ROOT/'correcao_20260913/sync_config.json').read_text(encoding='utf8'))
doc = Document(ROOT/config['template'])
source = (ROOT/'manuscrito.md').read_text(encoding='utf8')
chunks = re.split(r'<!-- p:(\d+) -->\s*\n',source)
seen = set()
for pos in range(1,len(chunks),2):
    idx = int(chunks[pos])
    if idx in seen: raise ValueError(f'Duplicate paragraph ID: {idx}')
    seen.add(idx)
    text = re.sub(r'^#{1,2} ', '', chunks[pos+1].strip())
    p = doc.paragraphs[idx]
    if text == p.text: continue
    rp = deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
    notes = [deepcopy(run._r) for run in p.runs if run._r.xpath('.//w:footnoteReference')]
    p.clear()
    run = p.add_run(text)
    if rp is not None: run._r.insert(0,rp)
    for note in notes: p._p.append(note)
# The TOC end-field paragraph must not create a blank page before Chapter 1.
for p in doc.paragraphs:
    if not p.text.strip() and p._p.xpath('.//w:fldChar'):
        p.paragraph_format.space_before=Pt(0)
        p.paragraph_format.space_after=Pt(0)
        p.paragraph_format.line_spacing=Pt(1)
        for run in p.runs: run.font.size=Pt(1)
target=ROOT/config['output']
if target.exists():
    backup=ROOT/'backups'/('antes_gerar_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    backup.mkdir()
    shutil.copy2(target,backup/target.name)
assert len(doc.inline_shapes)==10 and len(doc.tables)==4
doc.save(target)
print(f'Atualizado: {target}; {len(seen)} paragrafos; 10 imagens; 4 tabelas.')
print('Atualize o sumario e o PDF no Word apos alterar o texto.')
