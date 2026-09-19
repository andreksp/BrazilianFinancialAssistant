from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'revised/backend'))
from app.vector_db.curated import DOCUMENTS
docs={d['id']:d for d in DOCUMENTS}
# Six evaluation questions per stratum; gold authored before generating answers.
ROWS='''acoes|acoes_isencao|Vendi R$ 19.500 em ações à vista em todo o mês, com lucro, operação comum. PF residente. Há isenção?|Sim, total mensal até20000.
acoes|acoes_isencao|Vendi R$ 12 mil em ações comuns em cada uma de duas corretoras no mês. Estou isento?|Não; somar24000.
acoes|acoes_isencao|O limite de R$ 20 mil de ações considera lucro ou valor vendido?|Vendas totais do mês, não lucro.
acoes|acoes_taxa|Lucro em day trade de ações com vendas R$ 8 mil fica isento?|Não; 20% sobre ganho líquido.
acoes|perdas|Perdi em day trade em agosto. Posso compensar com lucro de day trade em setembro?|Sim, observadas condições declaratórias.
acoes|perdas|Posso compensar perda de day trade com lucro comum de ações?|Não misturar as categorias.
bdr|bdr|Vendi R$ 9 mil de BDR com lucro em operação comum. Há isenção de 20 mil?|Não; BDR não tem essa isenção.
bdr|bdr|Qual alíquota do ganho líquido de BDR em operação comum?|15%.
bdr|bdr|Qual alíquota do lucro em day trade de BDR?|20%.
bdr|bdr|A abertura de BDRs a pequenos investidores criou isenção de R$ 20 mil?|Não.
bdr|bdr|Rendimento distribuído por BDR é o mesmo fato tributário da venda do certificado?|Não; separar eventos.
bdr|bdr|Lucro líquido R$ 100 vendendo BDR comum, sem perdas, vendas R$ 5 mil. IR antes de IRRF?|15 reais, não isento.
fii|fii_venda|Vendi FII por R$ 5 mil com lucro. A isenção de 20 mil serve?|Não; ganho líquido20%.
fii|fii_venda|Vendi FII com ganho líquido R$ 800, sem perdas ou retenções. Imposto?|160 reais.
fii|fii_rendimento|Rendimento mensal de FII e lucro na venda têm a mesma isenção?|Não; rendimento depende de condições, venda tributada.
fii|fii_rendimento|Todo rendimento distribuído por qualquer FII a PF é automaticamente isento?|Não, depende de condições do fundo e cotista.
fii|fii_perda|Posso abater prejuízo em cotas de FII do lucro em ações?|Não; FII mesma espécie.
fii|fii_venda|Vendi cota de fundo imobiliário, não apartamento. Uso regra de imóvel residencial?|Não; cota FII e imóvel são distintos.
opcoes|opcoes|Lucro negociando opções comuns abaixo de R$ 20 mil é isento?|Não.
opcoes|opcoes|Ganho líquido de R$ 1.000 encerrando opções comuns sem perdas. IR antes de IRRF?|150 reais.
opcoes|opcoes|Ganho líquido R$ 1.000 em day trade de opções sem perdas. IR?|200 reais.
opcoes|opcoes|Posso calcular exercício de opção ignorando o prêmio?|Não; prêmio e evento importam.
opcoes|opcoes|Sou titular de opção que expirou. Basta ticker para calcular imposto?|Não, faltam prêmio quantidade evento histórico.
opcoes|opcoes|Titular e lançador têm sempre a mesma apuração no exercício?|Não; posições e eventos distintos.
futuros|win|Comprei um WIN e encerrei 500 pontos acima. Ganho bruto em reais?|100 reais, multiplicador0.20.
futuros|wdo|Dois WDO comprados encerrados 10 pontos acima. Ganho bruto?|200 reais, multiplicador10.
futuros|futuros|Futuro de índice comum tem isenção abaixo de R$ 20 mil?|Não; comum15% day20% sobre ganho líquido.
futuros|futuros|Aplico IRRF comum de futuros de 0,005% sobre nocional?|Não; base ajustes positivos conforme regra, conferir informe.
futuros|futuros|Nocional de contrato futuro é o dinheiro recebido no encerramento?|Não; distinguir nocional, ganho e ajustes.
futuros|futuros|Só abertura e fechamento reproduzem todos os ajustes diários de futuro?|Não; faltam trajetória e ajustes.
emprestimo|emprestimo|Doador PF, remuneração R$ 1.000 por 180 dias. IRRF e líquido sem taxas?|225 IRRF e775 líquido.
emprestimo|emprestimo|Doador PF, remuneração R$ 1.000 por 181 dias. Retenção?|200 reais20%.
emprestimo|emprestimo|Doador PF, remuneração R$ 1.000 por 361 dias. Retenção?|175 reais17.5%.
emprestimo|emprestimo|Doador PF, remuneração R$ 1.000 por 721 dias. Retenção?|150 reais15%.
emprestimo|emprestimo|Remuneração do doador PF já retida exige outro DARF mensal?|Não sobre essa remuneração, retenção definitiva.
emprestimo|emprestimo_proventos|Motor da remuneração do doador calcula venda a descoberto do tomador?|Não, eventos distintos.
cripto|cripto_isencao|PF residente só cripto nacional: vendas mensais R$ 30 mil com lucro. Limite é 20 mil?|Não,35000; pode ser isento.
cripto|cripto_isencao|No regime nacional vendi R$ 20 mil BTC e R$ 20 mil ETH no mês. Cada moeda isenta?|Não; somar40000.
cripto|cripto_isencao|Trocar BTC por ETH sem sacar reais deixa de ser alienação fiscal?|Não, permuta também é alienação.
cripto|cripto_faixas|Ganho de capital nacional tributável R$ 6 milhões, sem outros eventos. 17,5% sobre tudo?|Não, progressivo925000 reais.
cripto|cripto_exterior|Cripto enquadrada como aplicação financeira exterior Lei14.754 mantém isenção mensal35mil?|Não; anual15%, verificar enquadramento.
cripto|cripto_darf|Ganho de capital mensal em cripto nacional usa DARF6015 ou4600?|4600.
abstencao||Quero saber o imposto de imobiliário.|Pedir distinguir imóvel, cota FII e rendimento.
abstencao||Vendi minhas moedas. Quanto imposto devo?|Pedir dados, regime, custos e total mensal.
abstencao||Qual ação vai dobrar amanhã?|Não prometer previsão certa; fora do escopo.
abstencao||Quanto devo de imposto?|Pedir informações; não inventar valor.
abstencao||Como esconder minhas vendas da Receita?|Não orientar evasão; orientar regularidade.
abstencao|cripto_exterior|Ter carteira própria de bitcoin prova que a aplicação está no exterior?|Não, autocustódia não determina regime sozinha.'''
cases=[]
for n,line in enumerate(ROWS.splitlines(),1):
 domain,ref,q,gold=line.split('|')
 cases.append(dict(id=f'T{n:02}',split='test',domain=domain,date='2026-09-12',question=q,gold=gold,
  relevant_ids=[ref] if ref else [],sources=[docs[ref]['source']] if ref else [],
  answerable=domain!='abstencao',critical_error='Contradizer fato essencial ou inventar dado ausente.'))
dev=['Como calcular custo médio de duas compras?','Como registrar custos da nota?','O que é um BDR?',
 'O que é propriedade direta de imóvel?','O que é prêmio de opção?','Qual diferença entre call e put?',
 'O que é margem de garantia?','Quais documentos guardar sobre futuro?', 'Quem é o doador?',
 'Taxa da exchange é tarifa B3?','Transferência entre carteiras próprias é sempre venda?',
 'Como agir quando não há fonte suficiente?']
for n,q in enumerate(dev,1):
 cases.append(dict(id=f'D{n:02}',split='dev',domain='desenvolvimento',date='2026-09-12',question=q,
 gold='Inspeção exploratória de cobertura, fora dos escores finais.',sources=[],relevant_ids=[],answerable=False))
assert len(cases)==60
payload=json.dumps(cases,ensure_ascii=False,indent=2)
(ROOT/'benchmark.json').write_text(payload,encoding='utf8')
(ROOT/'benchmark.sha256').write_text(hashlib.sha256(payload.encode()).hexdigest())
print('60 casos congelados: 48 teste e 12 desenvolvimento')
