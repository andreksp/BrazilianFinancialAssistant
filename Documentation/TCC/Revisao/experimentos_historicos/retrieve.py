from pathlib import Path
import os,sys,json,subprocess,hashlib,time
ROOT=Path(__file__).parent
if len(sys.argv)==1:
 for version in ['baseline','revised']:
  subprocess.run([sys.executable,__file__,version],check=True)
else:
 version=sys.argv[1]
 os.environ['CHROMA_DB_PATH']=str(ROOT/(version+'_chroma'))
 os.environ['DATABASE_URL']='sqlite:///'+str(ROOT/(version+'_test.db')).replace('\\','/')
 sys.path.insert(0,str(ROOT/version/'backend'))
 from app.vector_db.chroma_client import get_chroma_client
 c=get_chroma_client(); c.load_initial_regulations()
 rows=[]
 for case in json.loads((ROOT/'benchmark.json').read_text(encoding='utf8')):
  t=time.perf_counter()
  if version=='revised': evidence=c.search_evidence(case['question'])
  else:
   scope={'acoes':'acoes','bdr':'acoes','opcoes':'acoes','cripto':'cripto'}.get(case['domain'],'geral')
   texts=c.search_regulations(case['question'],asset_type=scope,top_k=3)
   evidence=[dict(id=hashlib.sha256(s.encode()).hexdigest()[:16],text=s,metadata={},distance=None) for s in texts]
  rows.append(dict(case_id=case['id'],evidence=evidence,seconds=time.perf_counter()-t))
 (ROOT/(version+'_retrieval.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
 print(version,len(rows),'queries saved',flush=True)
