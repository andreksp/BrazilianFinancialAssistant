"""Aggregate automatic scores without selecting favorable cases."""
from pathlib import Path
import json,math,statistics,csv
ROOT=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
cases=[c for c in read(ROOT/'benchmark.json') if c['split']=='test']
retrieval={v:{r['case_id']:r['evidence'] for r in read(ROOT/(v+'_retrieval.json'))} for v in ['baseline','revised']}
rows=[]; repeats=[]
for c in cases:
 s=read(ROOT/'api_results'/(c['id']+'_judge_scores.json'))
 grades={t['id']:t['relevancia'] for t in s['trechos']}
 ideal=sorted(grades.values(),reverse=True)[:3]
 idcg=sum((2**g-1)/math.log2(i+2) for i,g in enumerate(ideal))
 for r in s['respostas']:
  config=r['configuration'];version=config.split('_')[0]
  g=[grades[e['id']] for e in retrieval[version][c['id']]]
  dcg=sum((2**x-1)/math.log2(i+2) for i,x in enumerate(g))
  a=read(ROOT/'api_results'/f"{c['id']}_{config}.json")
  rows.append(dict(case_id=c['id'],domain=c['domain'],configuration=config,answerable=c['answerable'],
   p1=int(bool(g) and g[0]==2),p3=sum(x==2 for x in g)/3,
   ndcg3_pooled=dcg/idcg if idcg else 0,correct=int(r['correcao']==2 and not r['erro_critico']),
   correctness_grade=r['correcao'],grounding_grade=r['fundamentacao'],critical_error=r['erro_critico'],
   abstention_appropriate=r['abstencao_adequada'],seconds=a['seconds'],usd=a['usd']))
 repeat_path=ROOT/'api_results'/(c['id']+'_judge_repeat_scores.json')
 if repeat_path.exists():
  ss=read(repeat_path);rr={r['configuration']:r for r in ss['respostas']}
  for r in s['respostas']:
   repeats.append(dict(case_id=c['id'],configuration=r['configuration'],
    same_grade=r['correcao']==rr[r['configuration']]['correcao'],
    same_critical=r['erro_critico']==rr[r['configuration']]['erro_critico']))
summary={}
for config in sorted({r['configuration'] for r in rows}):
 allrows=[r for r in rows if r['configuration']==config]
 factual=[r for r in allrows if r['answerable']]
 abst=[r for r in allrows if not r['answerable']]
 summary[config]=dict(n=len(allrows),n_factual=len(factual),
  correct_factual=sum(r['correct'] for r in factual),correct_all=sum(r['correct'] for r in allrows),
  critical_errors=sum(r['critical_error'] for r in allrows),
  p1=statistics.mean(r['p1'] for r in factual),p3=statistics.mean(r['p3'] for r in factual),
  ndcg3_pooled=statistics.mean(r['ndcg3_pooled'] for r in factual),
  abstention_appropriate=sum(r['abstention_appropriate'] for r in abst),n_abstention=len(abst),
  median_seconds=statistics.median(r['seconds'] for r in allrows),usd=sum(r['usd'] for r in allrows))
result=dict(configurations=summary,judge_repeat=dict(n=len(repeats),
  same_grade=sum(r['same_grade'] for r in repeats),same_critical=sum(r['same_critical'] for r in repeats)),
 total_api_usd=sum(json.loads(s)['usd'] for s in (ROOT/'api_ledger.jsonl').read_text().splitlines()),
 caveats=['Automatic, AI-authored gold; not independent expert validation.',
 'nDCG denominator uses judged union of retrieved chunks, not exhaustive corpus judgments.',
 'Only 42 answerable questions enter retrieval averages; 6 clarification/out-of-scope cases separate.',
 'Corpus curation, chunking, ranking and context length changed together; no isolated causal attribution.',
 'Domain scope for baseline provided by benchmark; routing and extraction not measured.',
 'Model families are all Anthropic; same-family judge may have correlated bias.'])
(ROOT/'results_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
with (ROOT/'results_per_case.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps(result,ensure_ascii=False,indent=2))
