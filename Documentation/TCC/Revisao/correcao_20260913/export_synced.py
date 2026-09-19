"""Fallback renderer: installed Microsoft Word -> PDF -> page PNGs."""
from pathlib import Path
import json
import fitz
import win32com.client

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Entrega_Final'
file = OUT / 'Monografia_Revisada_para_Orientador.docx'
pdf = file.with_suffix('.pdf')
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
doc = None
try:
    doc = word.Documents.Open(str(file), ReadOnly=False, AddToRecentFiles=False)
    for note in doc.Footnotes:
        note.Reference.Font.Superscript = True
        note.Range.Font.Name = 'Times New Roman'
        note.Range.Font.Size = 10
        note.Range.ParagraphFormat.FirstLineIndent = 0
        note.Range.ParagraphFormat.SpaceAfter = 0
        note.Range.ParagraphFormat.LineSpacingRule = 0
        url = 'https://www.gov.br/investidor/pt-br/educacional/publicacoes-educacionais/livros-cvm/'
        link_range = note.Range.Duplicate
        if link_range.Find.Execute(FindText=url):
            if link_range.Hyperlinks.Count == 0:
                doc.Hyperlinks.Add(Anchor=link_range, Address=url)
    doc.Fields.Update()
    for toc in doc.TablesOfContents:
        toc.Update()
    doc.Repaginate()
    for toc in doc.TablesOfContents:
        toc.UpdatePageNumbers()
    doc.Save()
    doc.ExportAsFixedFormat(str(pdf), 17)
    print('Exported Word PDF:', pdf, flush=True)
finally:
    if doc is not None:
        doc.Close(False)
    word.Quit()

pages = Path(__file__).parent / 'pages_sincronizadas'
pages.mkdir(exist_ok=True)
report = []
with fitz.open(pdf) as d:
    for i, page in enumerate(d, 1):
        page.get_pixmap(matrix=fitz.Matrix(1.5,1.5), alpha=False).save(str(pages / f'page-{i:02}.png'))
        report.append({'page':i, 'text_start':page.get_text()[:160], 'text_length':len(page.get_text())})
print('Pages:', len(report))
(Path(__file__).parent / 'pages_sincronizadas.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
