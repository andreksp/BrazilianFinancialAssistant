"""Registra a limitação de consulta de posição e simulação conversacional."""
from pathlib import Path
from datetime import datetime
from shutil import copy2
from docx import Document

root = Path(__file__).resolve().parent
word = root / 'Entrega_Final/Monografia_Revisada_para_Orientador.docx'
template = root / 'modelo/modelo_sincronizado.docx'
md = root / 'manuscrito.md'
text = ('A consulta à carteira pelo chat também é limitada. A ferramenta de consulta ao custo médio '
        'fica disponível somente após a extração de uma operação com dados suficientes; não há '
        'ferramenta para recuperar o saldo de um ativo a partir de perguntas como “se eu vender meu '
        'saldo de PETR4, quanto pagarei de imposto?”. Assim, mesmo com compras persistidas, a pergunta '
        'pode receber uma resposta geral sem consulta à posição do usuário. O fluxo não mantém uma '
        'simulação em andamento para solicitar e incorporar os dados faltantes, como preço e data '
        'de venda. Além disso, não há separação explícita entre simulação e registro: uma venda '
        'extraída e calculada com sucesso é persistida pelo agente. Portanto, o chat não deve ser '
        'tratado como simulador de carteira sem efeitos sobre os registros. Essas restrições decorrem '
        'da implementação do fluxo, e não do protocolo MCP.')
docs = [Document(word), Document(template)]
anchor = 'A desatualização de fontes, a interpretação incorreta de dados'
for d in docs:
    assert not any(p.text == text for p in d.paragraphs)
    assert sum(p.text.startswith(anchor) for p in d.paragraphs) == 1
backup = root / 'backups' / ('antes_limitacao_carteira_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
for file in (word, word.with_suffix('.pdf'), template, md):
    copy2(file, backup / file.name)
for file, d in zip((word, template), docs):
    original = [p._p.xml for p in d.paragraphs]
    p = next(p for p in d.paragraphs if p.text.startswith(anchor))
    p.insert_paragraph_before(text, 'TCC Corpo')
    assert [p._p.xml for p in d.paragraphs if p.text != text] == original
    d.save(file)
blocks = ['<!-- Fonte editorial única. Preserve IDs; capas, tabelas e figuras são mantidas no modelo. -->']
for i, p in enumerate(docs[1].paragraphs):
    if not p.text.strip() or p._p.xpath('.//w:fldChar|.//w:fldSimple|.//w:drawing') or p.style.name.lower().startswith('toc'):
        continue
    prefix = '# ' if p.style.name in ('TCC Capitulo', 'TCC Preliminar') else '## ' if p.style.name == 'TCC Secao' else ''
    blocks.append(f'<!-- p:{i} -->\n{prefix}{p.text}')
md.write_text('\n\n'.join(blocks) + '\n', encoding='utf8')
print(backup)
