#!/usr/bin/env python3
import csv,json,hashlib,math,platform,random
from pathlib import Path
P=Path(__file__).resolve().parent
read=lambda name:list(csv.DictReader((P/name).open(encoding='utf8',newline='')))
p=json.loads((P/'protocol.json').read_text(encoding='utf8')); c=read('CRITERIA.csv'); e=read('EVIDENCE.csv'); sources=read('SOURCE_REGISTER.csv'); ent=read('ENTITIES.csv'); matrix=read('SCORE_MATRIX.csv')
ids=[x['criterion_id'] for x in c];assert ids==p['criterion_order'] and len(ids)==len(set(ids));w=[float(x['weight']) for x in c];assert sum(w)==100 and all(x>0 for x in w)
assert len({x['source_id'] for x in sources})==len(sources);src={x['source_id'] for x in sources};assert len({x['entity_id'] for x in ent})==len(ent);ad={x['entity_id'] for x in ent if x['admission_status']=='admitted'}
assert len(ad)>=10 and len({x['entity_id'] for x in matrix})==len(matrix)==len(ad) and {x['entity_id'] for x in matrix}==ad
rows={x['entity_id']:[float(x[k]) for k in ids] for x in matrix};assert all(math.isfinite(v) and 0<=v<=5 for r in rows.values() for v in r)
check={};lo={};hi={}
for x in e:
 k=x['entity_id'],x['criterion_id'];assert k not in check and k[0] in ad and k[1] in ids;assert x['source_ids'] and set(x['source_ids'].split('|'))<=src
 val=float(x['score_value']); l=float(x['score_low']); h=float(x['score_high']);assert 0<=l<=val<=h<=5 and all(map(math.isfinite,(val,l,h)))
 if x['status'] in ('interval','unavailable'): assert val==l
 else:
  raw=x['raw_value'];assert raw;assert x['verification_sufficient']=='true';assert l==h==val
  if k[1]=='provenance': n=int(raw); calc=2.5*min(n,2)
  else:
   bits=raw.split('|');assert len(bits)==(4 if k[1]=='input' else 5) and all(b in ('0','1') for b in bits);calc=sum(a*b for a,b in zip(map(int,bits),[2,1,1,1] if k[1]=='input' else [1]*5))
  assert val==calc and (val==0 or x['claim'])
 assert val==rows[k[0]][ids.index(k[1])];check[k]=val;lo[k]=l;hi[k]=h
assert set(check)=={(a,b) for a in ad for b in ids};assert len({x['evidence_id'] for x in e})==len(e)
def scores(weights,rs):return {k:sum(a*b/5 for a,b in zip(weights,r)) for k,r in rs.items()}
base=scores(w,rows);order=sorted(base,key=lambda k:(-base[k],k));eps=p['tie_epsilon'];target=p['target'];rank=0;prev=None;ranking=[]
for i,k in enumerate(order,1):
 if prev is None or abs(base[k]-prev)>eps:rank=i
 ranking.append({'id':k,'rank':rank,'score':round(base[k],10),'levels':rows[k]});prev=base[k]
margin=base[target]-max(v for k,v in base.items() if k!=target)
adverse=scores(w,{k:[(lo if k==target else hi)[k,cid] for cid in ids] for k in rows});adverse_margin=adverse[target]-max(v for k,v in adverse.items() if k!=target)
s=p['sensitivity'];seed=int(hashlib.sha256((p['research_id']+'|'+p['release']).encode()).hexdigest()[:8],16);assert s['seed']==seed;rng=random.Random(seed);wins=ties=0;margins=[];n=s['n'];assert n==1000
for i in range(n):
 q=[a*rng.uniform(*s['range']) for a in w];q=[100*a/sum(q) for a in q];a=scores(q,rows);m=a[target]-max(v for k,v in a.items() if k!=target);margins.append(m);wins+=m>eps;ties+=abs(m)<=eps
z=1.959963984540054;f=wins/n;lower=(f+z*z/(2*n)-z*math.sqrt(f*(1-f)/n+z*z/(4*n*n)))/(1+z*z/n)
out={'research_id':p['research_id'],'release':p['release'],'ranking':ranking,'base_margin':margin,'adverse_margin':adverse_margin,'sensitivity':{'n':n,'seed':seed,'range':s['range'],'algorithm':'Python random.Random / uniform normalized weights','python_version':platform.python_version(),'unique_wins':wins,'top_ties':ties,'win_share':f,'wilson_lower_95':lower,'min_margin':min(margins),'numeric_gate_pass':margin>eps and adverse_margin>eps and wins>=s['min_wins'] and lower>s['wilson_lower_gt']},'input_hashes':{k:hashlib.sha256((P/k).read_bytes()).hexdigest() for k in ['protocol.json','CRITERIA.csv','ENTITIES.csv','SOURCE_REGISTER.csv','EVIDENCE.csv','SCORE_MATRIX.csv','calculate.py']}}
if __name__=='__main__':
 print(json.dumps(out,ensure_ascii=False,indent=2));
 if '--write' in __import__('sys').argv:(P/'RESULTS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 else:
  saved=json.loads((P/'RESULTS.json').read_text(encoding='utf8')); assert saved['ranking']==out['ranking'] and saved['input_hashes']==out['input_hashes'] and saved['base_margin']==out['base_margin'] and saved['adverse_margin']==out['adverse_margin']; assert all(saved['sensitivity'][k]==out['sensitivity'][k] for k in ['n','seed','unique_wins','top_ties','win_share','numeric_gate_pass']); assert abs(saved['sensitivity']['min_margin']-out['sensitivity']['min_margin'])<1e-9 and abs(saved['sensitivity']['wilson_lower_95']-out['sensitivity']['wilson_lower_95'])<1e-9
