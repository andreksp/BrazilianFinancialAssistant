"""Versioned experimental corpus. Summaries, not verbatim legal text."""
DATE = '2026-09-12'
SOURCES = {
 'isencoes':'https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/bolsa-de-valores-1/isencoes',
 'in1585':'https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494',
 'fii':'https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/fundos-de-investimento-no-brasil',
 'perdas':'https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/bolsa-de-valores-1/compensacoes',
 'cripto':'https://normas.receita.fazenda.gov.br/sijut2consulta/anexoOutros.action?idArquivoBinario=64040',
 'capital':'https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/lei/l13259.htm',
 'exterior':'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14754.htm',
 'emprestimo':'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15265.htm',
 'wdo':'https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/moedas/futuro-mini-de-taxa-de-cambio-de-reais-por-dolar-comercial.htm',
 'win':'https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/futuro-mini-de-ibovespa.htm',
 'bdr':'https://borainvestir.b3.com.br/noticias/imposto-de-renda/renda-variavel-imposto-de-renda/como-declarar-bdrs-no-imposto-de-renda-2026-veja-guia-completo-para-nao-cometer-erros/',
 'l11033':'https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l11033.htm',
 'b3':'https://www.b3.com.br/pt_br/produtos-e-servicos/emprestimo-de-ativos/informacoes.htm',
}
# Each chunk keeps a complete rule and its qualification together.
ROWS = [
 ('acoes_isencao','acoes','isencoes','Ações à vista: para pessoa física residente, ganhos em operações comuns podem ser isentos quando o total das vendas de ações no mês, somadas as corretoras, não ultrapassa R$ 20.000. O limite incide sobre vendas, não sobre lucro. Não se aplica a day trade, opções, FII, ETF ou BDR.'),
 ('acoes_taxa','acoes','l11033','Ações em bolsa: operações comuns tributáveis têm alíquota de 15%; day trade, 20% sobre ganhos líquidos. Não se aplica limite de isenção ao day trade. IRRF é antecipação e não substitui automaticamente a apuração mensal.'),
 ('perdas','geral','perdas','Prejuízos em day trade podem ser compensados com ganhos em day trade no mês ou em períodos posteriores, observadas as obrigações declaratórias. Não se misturam com ganhos de operações comuns. Compensação não significa restituição automática.'),
 ('bdr','acoes','bdr','BDR não possui a isenção de vendas de R$ 20 mil das ações à vista. Ganho líquido em operação comum: 15%; day trade: 20%. O limite de vendas não transforma lucro de BDR em isento. Rendimentos distribuídos por BDR não devem ser confundidos com ganho na venda do certificado.'),
 ('fii_venda','geral','fii','Venda de cotas de fundo imobiliário (FII): ganho líquido sujeito a 20%. Não há isenção pela venda abaixo de R$ 20 mil. Venda de cota, rendimento distribuído pelo fundo e venda direta de imóvel são fatos distintos.'),
 ('fii_rendimento','geral','l11033','Rendimentos distribuídos por FII a pessoa física podem ser isentos quando cumpridas as condições do art. 3º da Lei 11.033, incluindo negociação admitida em bolsa ou balcão organizado, mínimo de 100 cotistas e restrições de participação e concentração. Não se presume isenção de todo fundo ou cotista. Isso não isenta lucro na venda de cotas.'),
 ('fii_perda','geral','in1585','Prejuízos na alienação de cotas de FII somente se compensam com ganhos de alienação de cotas de fundos da mesma espécie. Não compensar indiscriminadamente com lucro em ações. O cálculo exige custos, ganhos e perdas da categoria.'),
 ('opcoes','acoes','in1585','Opções em bolsa: apuração depende de negociação, exercício ou expiração e da posição titular ou lançador. Não basta tratar toda operação como venda de ação. Operações comuns: 15%; day trade: 20%. Não existe isenção de R$ 20 mil para ganho com opções. O prêmio integra a apuração conforme o evento.'),
 ('futuros','geral','in1585','Futuros: operações comuns 15%, day trade 20%, sem isenção de R$ 20 mil. Apuração envolve ajustes e despesas; valor nocional não é lucro nem caixa recebido. IRRF comum de 0,005% usa soma algébrica positiva dos ajustes diários no encerramento; retenção efetiva deve ser conferida no informe. Não aplicar sobre nocional.'),
 ('wdo','geral','wdo','Minicontrato futuro de dólar WDO: tamanho USD 10.000 e cotação em reais por USD 1.000. Uma variação de um ponto corresponde a R$ 10 por contrato. Para posição comprada: diferença de cotações × 10 × contratos; invertida para posição vendida. Isso não substitui os ajustes diários.'),
 ('win','geral','win','Minicontrato futuro de Ibovespa WIN: cada ponto equivale a R$ 0,20 por contrato. Variação de 500 pontos em um contrato comprado equivale a R$ 100 antes de custos. Não confundir pontos com reais, nem nocional com ganho.'),
 ('emprestimo','geral','emprestimo','Empréstimo de ativos no País: Lei 15.265/2025, arts. 18 e 19. Remuneração do emprestador residente pessoa física é tributada exclusivamente na fonte pelas regras de renda fixa: 22,5% até 180 dias; 20% de 181 a 360; 17,5% de 361 a 720; 15% acima de 720. Não é venda isenta de ação e não gera DARF mensal adicional sobre essa remuneração. Prazo e rendimento bruto são necessários.'),
 ('emprestimo_proventos','geral','emprestimo','Empréstimo transfere titularidade com obrigação de devolução. Remuneração contratual e reembolso de proventos são eventos diferentes. Arts. 20 e seguintes da Lei 15.265/2025 disciplinam reembolsos. O cálculo da remuneração do doador não cobre venda a descoberto, custos e tributação do tomador.'),
 ('cripto_isencao','cripto','cripto','Regime de ganho de capital de criptoativos nacionais: somar todas as alienações de criptoativos no mês. Até R$ 35.000 pode haver isenção; não são R$ 20.000 e não é limite por moeda ou operação. Permuta entre criptomoedas também configura alienação mesmo sem conversão em reais. Não concluir sobre o exterior sem enquadramento específico.'),
 ('cripto_faixas','cripto','capital','Ganho de capital tributável: aplicar progressivamente 15% à parcela até R$ 5 milhões, 17,5% à parcela entre R$ 5 e 10 milhões, 20% de R$ 10 a 30 milhões e 22,5% ao excedente. Não aplicar a maior alíquota ao ganho inteiro. Um ganho de R$ 6 milhões, sem outras condições, corresponde a R$ 925 mil de imposto.'),
 ('cripto_exterior','cripto','exterior','Aplicações financeiras no exterior, enquadradas na Lei 14.754/2023, possuem apuração anual a 15%, sem a isenção mensal de R$ 35 mil. Para criptoativos, verificar natureza do ativo, custódia/intermediação e regulamentação. Autocustódia não prova, por si só, localização no exterior. Não generalizar de uma exchange para toda cripto.'),
 ('cripto_darf','cripto','cripto','No regime de ganho de capital mensal aplicável a criptoativos, o recolhimento utiliza DARF 4600 até o último dia útil do mês seguinte. Não usar automaticamente 6015, próprio de ganhos líquidos em bolsa. Obrigação de informar operações é diferente de obrigação de pagar imposto.'),
 ('b3_papel','geral','b3','A B3 fornece infraestrutura para registro e liquidação de empréstimos de ativos e atua como contraparte central. Sua tarifa de serviço não é o imposto de renda: a legislação tributária e a Receita Federal regem o tributo. Custos da corretora também são distintos.'),
]
DOCUMENTS = [dict(id=i, asset_type=a, source=SOURCES[s], checked_at=DATE, text=t) for i,a,s,t in ROWS]
