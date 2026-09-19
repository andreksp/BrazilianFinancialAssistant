"""Independent source-derived regression scenarios; no API use."""
from pathlib import Path
import sys,subprocess,json
ROOT=Path(__file__).parent
if len(sys.argv)==1:
 for v in ['baseline','revised']:subprocess.run([sys.executable,__file__,v],check=True)
else:
 v=sys.argv[1];sys.path.insert(0,str(ROOT/v/'backend'))
 from app.models.trade import TradeInput
 from app.calculations.equity.acoes import AcoesCalculator
 from app.calculations.crypto.criptomoedas import CriptomoedaCalculator
 from app.calculations.derivatives.futuros import FuturosCalculator
 from app.calculations.lending.emprestimo import EmprestimoCalculator
 cases=[]
 def add(name,cls,asset,ticker,qty,price,pm,expected,**extra):
  cases.append((name,cls,dict(ativo=ticker,tipo_ativo=asset,tipo_operacao='venda',quantidade=qty,
    preco_unitario=price,data_operacao='2026-09-01',custos_operacao=0,irrf_informado=0,**extra),pm,expected))
 add('acao_limite',AcoesCalculator,'acao','PETR4',100,200,100,{'ir_devido':0},total_vendas_mes=20000)
 add('acao_acima_limite',AcoesCalculator,'acao','PETR4',100,200,100,{'ir_devido':1500},total_vendas_mes=20001)
 add('acao_daytrade',AcoesCalculator,'acao','PETR4',100,200,100,{'ir_devido':2000},classificacao='day_trade')
 add('cripto_limite',CriptomoedaCalculator,'cripto','BTC',0.1,350000,300000,{'ir_devido':0},total_vendas_mes=35000)
 add('cripto_agregacao',CriptomoedaCalculator,'cripto','BTC',0.1,350000,300000,{'ir_devido':750},total_vendas_mes=40000)
 add('cripto_progressivo',CriptomoedaCalculator,'cripto','BTC',100,70000,10000,{'ir_devido':925000},total_vendas_mes=7000000)
 add('WIN_multiplicador',FuturosCalculator,'futuro_indice','WINV26',1,130500,130000,{'ganho_prejuizo_bruto':100,'ir_devido':15})
 add('WDO_multiplicador',FuturosCalculator,'futuro_dolar','WDOU26',2,5510,5500,{'ganho_prejuizo_bruto':200,'ir_devido':30})
 for days,tax in [(180,225),(181,200),(361,175),(721,150)]:
  add('doador_'+str(days),EmprestimoCalculator,'emprestimo_acoes','PETR4',100,10,None,{'irrf_retido':tax,'ir_devido':0},prazo_dias=days)
 records=[]
 for name,cls,data,pm,expected in cases:
  try:
   r=cls().calculate_result(TradeInput(**data),average_price=pm).model_dump(mode='json')
   ok=all(abs(r[k]-value)<=0.01 for k,value in expected.items())
   records.append(dict(id=name,inputs=data,average_price=pm,expected=expected,actual=r,passed=ok))
  except Exception as e: records.append(dict(id=name,inputs=data,expected=expected,error=str(e),passed=False))
 (ROOT/(v+'_calculator_checks.json')).write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
 print(v,sum(r['passed'] for r in records),'/',len(records),flush=True)
