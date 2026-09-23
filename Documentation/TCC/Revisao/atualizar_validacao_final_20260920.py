"""Integrate verified tool-use evidence without rewriting historical experiments."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime
import shutil
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

R = Path(__file__).resolve().parent
backup = R / 'backups' / ('antes_validacao_final_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
for name in ['modelo/modelo_sincronizado.docx', 'manuscrito.md',
             'Entrega_Final/Monografia_Revisada_para_Orientador.docx',
             'Entrega_Final/Monografia_Revisada_para_Orientador.pdf']:
    shutil.copy2(R / name, backup / Path(name).name)
d = Document(R / 'modelo/modelo_sincronizado.docx')
assert not any(p.text.startswith('7.6 Validação do ciclo') for p in d.paragraphs), 'Already applied'
protected = [p._p.xml for p in d.paragraphs[:84]]

def replace(prefix, text):
    matches = [p for p in d.paragraphs if p.text.startswith(prefix)]
    assert len(matches) == 1, (prefix, len(matches))
    p = matches[0]
    props = deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
    p.clear()
    run = p.add_run(text)
    if props is not None:
        run._r.insert(0, props)

replace('Em 20 de setembro de 2026, foi implementado',
        'Em 20 de setembro de 2026, foi implementado o ciclo de seleção de ferramentas pelo modelo no chat. A primeira verificação local registrou 120 testes aprovados e dois avisos, em ambiente já instalado, com banco temporário e respostas programadas do modelo. O registro está em evidencias/tool_use_20260920/pytest.txt. Esses testes verificaram o processamento de tool_use e tool_result, sem demonstrar escolhas de um modelo real. A validação posterior, com modelos reais, correções e navegador, é apresentada na Seção 7.6, sem substituir os resultados históricos desta seção.')
replace('Outras evoluções incluem validar a seleção',
        'A validação de 20 de setembro demonstrou seleção de ferramentas por modelo real, execução no navegador e instalação limpa em ambiente virtual, além de um ensaio local de concorrência com respostas simuladas. Como continuidade, priorizam-se a unificação da identificação do usuário entre chat, histórico e resumo mensal, a confirmação de gravação pelo backend e a prevenção de registros duplicados. Também são necessários testes repetidos de extração de campos, reexecução do benchmark para a arquitetura atual, estudo de carga com modelos reais, validação de Docker e Poetry e versionamento de tarifas com fontes e vigência.')
replace('A cobertura operacional também é parcial:',
        'A cobertura operacional também é parcial: persistem simplificações de consolidação mensal, custo médio, tarifas legadas e classificação de eventos. A simulação de futuros não reproduz toda a trajetória de ajustes diários, posições vendidas ou rolagens, e o empréstimo compartilha campos com operações de compra e venda. Na Seção 7.6, a interface apresentou divergência de usuário entre gravação e consulta e uma explicação incompatível com a persistência da venda. Esses achados impedem tratar o histórico e o DARF exibidos como integralmente confiáveis. O identificador de usuário não constitui autenticação completa. A ausência de memória conversacional limita perguntas de continuidade, como “e se eu vender metade disso?”; registros persistidos não equivalem a contexto recuperado entre mensagens. Segurança pública e adequação à apuração fiscal autônoma não foram validadas.')

anchor = next(p for p in d.paragraphs if p.text == '8 CONCLUSÃO')

def add(text, style='TCC Corpo', new_page=False):
    p = anchor.insert_paragraph_before(text, style)
    if new_page:
        p.paragraph_format.page_break_before = True
    return p

add('7.6 Validação do ciclo de ferramentas e da interface', 'TCC Secao', True)
paragraphs = [
    'A rodada de 20 de setembro de 2026 avaliou a arquitetura com seleção de ferramentas pelo LLM. Foram confrontados o relatório de Claude Code, os arquivos JSON, os logs e sete capturas de interface em evidencias/tool_use_validacao_claude. As etapas envolveram inspeção de código, respostas programadas, modelos reais e navegador. São demonstrações com dados sintéticos e verificação de software assistida por IA, não auditoria tributária independente nem reexecução do benchmark ou do LLM-as-a-Judge.',
    'A instalação em novo ambiente virtual foi concluída após a atualização da restrição de uvicorn; o registro de dependências não indicou conflitos. O log pytest_suite_limpa.txt contém 120 testes aprovados, dois avisos e 18,56 segundos. Após as correções, a suíte local ampliada registrou 146 aprovações e dois avisos em 15,78 segundos, conforme evidencias/revisao_adendo_tool_use_20260920/pytest.txt. Este último resultado pertence a um ambiente já instalado: não deve ser confundido com a instalação limpa da primeira rodada.',
    'Foram corrigidas a tributação do ganho bruto em FII e opções, a ausência de guarda de custo médio nas chamadas diretas e a perda de mensagens de validação em exceções agrupadas. Também foi removido um ramo inalcançável de cripto no exterior, mantendo a recusa desse regime. Uma consulta de custo médio vazia passou a informar o dado ausente, mesmo quando o modelo encerra sem solicitar cálculo. Nenhuma dessas alterações transforma estimativas legadas de custos em tarifas oficiais atualizadas.',
    'Os testes adversariais reexecutados registraram doze casos aprovados e uma observação entre treze casos, sem falhas; quatro casos adicionais verificaram ferramenta desconhecida, identificador repetido e limites de chamadas e rodadas. O ensaio de concorrência, com serviço e MCP reais, mas respostas de modelo simuladas, registrou intervalo máximo de 0,075 segundo entre sinais de atividade em repouso e 0,076 segundo durante um ou três chats. Três chats levaram 4,492 segundos no conjunto, contra 4,43 segundos para um chat. Não houve falha dos sinais monitorados. O resultado é restrito à pequena carga local, sem demonstrar capacidade de produção.',
    'Sete cenários com modelo real abrangeram pergunta geral, compra, FII com compra anterior, FII com custo informado e recusas por custo médio, total mensal ou prazo ausentes. Na venda com compra anterior, o modelo solicitou consulta do custo médio; com custo informado, dispensou essa ferramenta. Os registros tool_use e tool_result documentam a seleção no ciclo. Após as correções numéricas, o JSON registrou uma compra e duas vendas, com IR de R$ 99,63 para HGLG11 e R$ 19,93 para KNRI11. As recusas não geraram vendas.',
    'As três recusas foram reexecutadas com modelo real após o último ajuste de validação, sem registros de venda. Na pergunta sobre ações, o extrator não preservou o custo médio informado e a recusa ocorreu por esse dado ausente, não pelo total mensal. Pelo navegador, a mesma categoria de cenário alcançou a recusa por total mensal. A divergência indica necessidade de testar repetibilidade da extração; não foi estimada sua frequência. Os JSONs registram custos estimados de US$ 0,1349 na segunda rodada completa e US$ 0,0678 no reteste das recusas, sem conciliação de fatura nem inclusão de todas as chamadas de navegador.',
    'Os sete cenários foram também exercitados no navegador, em sessões com banco temporário, segundo o relatório e as capturas. As Figuras 11 e 12 mostram o imposto corrigido e a mensagem de custo ausente. As capturas adicionais registram recusa por total mensal, recusa por prazo e resposta consultiva sem cartão de cálculo. Essas evidências complementam os testes programados, mas não constituem avaliação de usabilidade nem taxa estatística de acerto.',
    'A interface revelou dois defeitos ainda não corrigidos nesta versão. O chat grava sob user123, enquanto histórico, resumo e DARF consultam o usuário padrão quando o identificador não é enviado. Assim, uma venda calculada pode coexistir com histórico vazio e DARF zerado (Figura 13). Em outro caso, a resposta declarou que não havia gravado a venda, embora o executor tenha confirmado sua persistência (Figura 14). O usuário pode reenviar a operação e duplicá-la. A interpretação dos resultados deve, portanto, separar cálculo, explicação, persistência e apresentação, sem concluir que o fluxo fiscal completo está validado.',
]
for text in paragraphs:
    add(text)

captures = R / 'Entrega_Final/evidencias/tool_use_validacao_claude/capturas_interface'
figures = [
    (11, 'Venda de FII no chat após a correção da base de cálculo', '01_venda_fii_ir_corrigido_99_63.jpg',
     'A tela mostra ganho bruto de R$ 500,00, IR de R$ 99,63 e valor líquido de R$ 5.398,23. São saídas observadas, não validação integral da apuração mensal.'),
    (12, 'Recusa específica quando o custo médio não está disponível', '02_recusa_mensagem_especifica.jpg',
     'Para XPML11, a resposta pede o custo médio e o reenvio dos dados completos da venda, informa a ausência de contexto entre mensagens e declara que não houve registro.'),
    (13, 'Histórico vazio e DARF zerado apesar da venda registrada', '03_historico_vazio_bug_user_id.jpg',
     'A tela de setembro de 2026 informa ausência de vendas e valor a pagar de R$ 0,00. O relatório vincula o resultado à divergência de user_id entre gravação e consulta; não se trata de isenção demonstrada.'),
    (14, 'Cálculo corrigido acompanhado de afirmação indevida sobre gravação', '04_fii_custo_informado_ir_19_93.jpg',
     'O cartão de KNRI11 mostra IR de R$ 19,93. Acima, a resposta afirma “Não gravei esta venda”, em desacordo com a persistência relatada pelo executor. A captura não comprova, sozinha, o estado do banco.'),
]
for number, title, filename, reading in figures:
    p = add(f'Figura {number} – {title}', 'TCC Legenda', number in (11, 13))
    p.paragraph_format.keep_with_next = True
    p = add('', 'Normal')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    shape = p.add_run().add_picture(str(captures / filename), width=Cm(15.8))
    shape._inline.docPr.set('descr', title)
    p = add('Fonte: captura da interface Angular, sessão de 20 set. 2026, dados sintéticos. ' + reading, 'TCC Referencia')
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.keep_with_next = False
    p.paragraph_format.space_after = Pt(12)
    for run in p.runs:
        run.font.size = Pt(10)

assert protected == [p._p.xml for p in d.paragraphs[:84]], 'Cover or approved abstracts changed'
assert len(d.inline_shapes) == 14 and len(d.tables) == 4
d.save(R / 'modelo/modelo_sincronizado.docx')
blocks = ['<!-- Fonte editorial única. Preserve IDs; capas, tabelas e figuras são mantidas no modelo. -->']
for i, p in enumerate(d.paragraphs):
    if not p.text.strip() or p._p.xpath('.//w:fldChar|.//w:fldSimple|.//w:drawing') or p.style.name.lower().startswith('toc'):
        continue
    prefix = '# ' if p.style.name in ('TCC Capitulo', 'TCC Preliminar') else '## ' if p.style.name == 'TCC Secao' else ''
    blocks.append(f'<!-- p:{i} -->\n{prefix}{p.text}')
(R / 'manuscrito.md').write_text('\n\n'.join(blocks) + '\n', encoding='utf8')
print('Updated sources; backup:', backup)
