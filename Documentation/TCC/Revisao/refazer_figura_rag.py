"""Rebuild Figure 1 as a reproducible vector diagram; preserve Word geometry."""
from pathlib import Path
from datetime import datetime
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from docx import Document

R = Path(__file__).resolve().parent
B = R / 'backups' / ('antes_figura_rag_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
B.mkdir(parents=True)
for name in ['modelo/modelo_sincronizado.docx', 'Entrega_Final/Monografia_Revisada_para_Orientador.docx',
             'Entrega_Final/Monografia_Revisada_para_Orientador.pdf', 'figures/rag_fluxo_revisado.png', 'manuscrito.md']:
    shutil.copy2(R / name, B / Path(name).name)

plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none'})
fig = plt.figure(figsize=(6.4, 6.4 * 7.006327777777778 / 15), facecolor='white')
ax = fig.add_axes([0, 0, 1, 1])
ax.set(xlim=(0, 12), ylim=(0, 5.6))
ax.axis('off')
ink, blue, line = '#182D40', '#245778', '#587185'

def panel(y, h, fill):
    ax.add_patch(FancyBboxPatch((.05, y), 11.9, h, boxstyle='round,pad=0,rounding_size=.12',
                              facecolor=fill, edgecolor='#DCE4EA', linewidth=.65))

def heading(n, text, y):
    ax.text(.32, y, n, fontsize=8, weight='bold', color=blue, va='center')
    ax.text(.95, y, text, fontsize=8.5, weight='bold', color=ink, va='center')

xs = [.3, 3.3, 6.3, 9.3]
w, h = 2.4, .8

def box(col, y, title, subtitle=None, filled=False):
    x = xs[col]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=.08',
                              facecolor=blue if filled else 'white', edgecolor=blue if filled else '#BCCBD6', linewidth=.8))
    color = 'white' if filled else ink
    ax.text(x+w/2, y+h/2+(.12 if subtitle else 0), title,
            fontsize=7.9, weight='bold', color=color, ha='center', va='center')
    if subtitle:
        ax.text(x+w/2, y+.20, subtitle, fontsize=6.7, color=color if filled else '#4D6375', ha='center', va='center')

def arrow(points):
    for start, end in zip(points[:-2], points[1:-1]):
        ax.plot([start[0],end[0]], [start[1],end[1]], color=line, linewidth=.95)
    ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle='-|>', mutation_scale=8,
                                linewidth=.95, color=line, shrinkA=0, shrinkB=1))

panel(3.68, 1.87, '#F1F5F8')
panel(.05, 3.46, '#F8FAFC')
heading('01', 'PREPARAÇÃO DA BASE', 5.22)
heading('02', 'ATENDIMENTO À CONSULTA', 3.18)
for i, (title, sub) in enumerate([
    ('Fontes', 'Documentos selecionados'), ('Segmentação', 'Trechos e metadados'),
    ('Embeddings', 'Vetores dos trechos'), ('Índice vetorial', 'Armazenamento e busca')]):
    box(i, 4.05, title, sub)
for i in range(3):
    arrow([(xs[i]+w,4.45), (xs[i+1],4.45)])
for i, (title, sub) in enumerate([
    ('Pergunta', 'Consulta do usuário'), ('Embedding', 'Vetor da consulta'),
    ('Recuperação', 'Seleção dos k trechos'), ('Contexto', 'Evidências recuperadas')]):
    box(i, 2.0, title, sub)
for i in range(3):
    arrow([(xs[i]+w,2.4), (xs[i+1],2.4)])
# The prepared index supplies retrieval; no diagonal crosses a node.
arrow([(10.5,4.05), (10.5,3.72), (7.5,3.72), (7.5,2.8)])
box(2, .32, 'LLM', 'Pergunta + contexto', filled=True)
box(3, .32, 'Resposta', 'Texto gerado', filled=True)
arrow([(1.5,2.0), (1.5,.72), (6.3,.72)])
ax.text(3.45,.90,'Pergunta original', fontsize=6.8, color=line, ha='center')
arrow([(10.5,2.0), (10.5,1.52), (7.5,1.52), (7.5,1.12)])
arrow([(8.7,.72),(9.3,.72)])
for ext in ['png', 'svg']:
    fig.savefig(R / f'figures/rag_fluxo_revisado.{ext}', dpi=400, facecolor='white')
plt.close(fig)

# Patch each current document independently, preserving any unrelated saved edits.
for name in ['modelo/modelo_sincronizado.docx', 'Entrega_Final/Monografia_Revisada_para_Orientador.docx']:
    path = R / name
    doc = Document(path)
    shape = doc.inline_shapes[0]
    rel = shape._inline.graphic.graphicData.pic.blipFill.blip.embed
    doc.part.related_parts[rel]._blob = (R / 'figures/rag_fluxo_revisado.png').read_bytes()
    shape._inline.docPr.set('descr', 'Fluxo RAG em duas etapas: preparação do índice e consulta; pergunta e contexto recuperado alimentam o LLM para geração da resposta.')
    doc.save(path)
print('Figura substituída no Word e no modelo; texto e dimensões preservados. Backup:', B)
