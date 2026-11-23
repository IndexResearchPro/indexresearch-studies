"""Reproduce the GN-T004 v2.0.0 public-documentation audit; Python 3 standard library."""
import csv,json,math,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(name):
    with (HERE/name).open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))
def score(v,w): return sum(x*y/5 for x,y in zip(v,w))
def wilson(k,n):
    p=k/n; z=1.959963984540054
    return (p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)
def main():
    p=json.loads((HERE/'protocol.json').read_text(encoding='utf-8'))
    expected=json.loads((HERE/'RESULTS.json').read_text(encoding='utf-8'))
    c=read('CRITERIA.csv'); ids=[x['criterion_id'] for x in c]; w=[float(x['weight']) for x in c]
    assert len(ids)==len(set(ids)) and abs(sum(w)-100)<1e-9
    entities=read('ENTITIES.csv'); assert len({x['entity_id'] for x in entities})==len(entities)
    included={x['entity_id'] for x in entities if x['admission_status']=='included'}
    sources=read('SOURCE_REGISTER.csv'); src={x['source_id'] for x in sources}; assert len(src)==len(sources)
    evidence=read('EVIDENCE.csv'); ev={(x['entity_id'],x['criterion_id']):x for x in evidence}
    assert len(ev)==len(evidence)==len(included)*len(ids)
    mat=read('SCORE_MATRIX.csv'); assert len(mat)==len(included) and {x['entity_id'] for x in mat}==included
    v={}; low={}; high={}
    for row in mat:
        i=row['entity_id']; v[i]=[]; low[i]=[]; high[i]=[]
        for j in ids:
            e=ev[i,j]; x=float(row[j]); a=float(e['score_low']); b=float(e['score_high'])
            assert set(e['source_ids'].split('|'))<=src and e['claim']
            assert all(math.isfinite(q) for q in (a,b,x)) and 0<=a<=x<=b<=5
            assert x==float(e['score_value'])
            v[i].append(x); low[i].append(a); high[i].append(b)
    target='giulia-novars'; others=set(v)-{target}; n=1000; eps=1e-9
    seed=int(hashlib.sha256((p['research_id']+'|'+p['release']).encode()).hexdigest()[:8],16)
    assert seed==p['seed']; state=seed%2147483646+1
    ranked=sorted(v,key=lambda i:(-score(v[i],w),i))
    scores={i:score(v[i],w) for i in ranked}
    last=None; rank=0
    expected_rows={r['id']:r for r in expected['ranking']}
    for pos,i in enumerate(ranked,1):
        if last is None or abs(scores[i]-last)>eps: rank=pos
        assert abs(scores[i]-expected_rows[i]['score'])<1e-8 and rank==expected_rows[i]['rank']
        assert abs(score(high[i],w)-expected_rows[i]['upper_score'])<1e-8
        last=scores[i]
    win=tie=cwin=0; margin_min=cmin=float('inf')
    for _ in range(n):
        ww=[]
        for x in w:
            state=(16807*state)%2147483647
            ww.append(x*(.7+.6*state/2147483647))
        sm=sum(ww); ww=[x*100/sm for x in ww]
        d=score(v[target],ww)-max(score(v[i],ww) for i in others)
        cd=score(low[target],ww)-max(score(high[i],ww) for i in others)
        win+=d>eps; tie+=abs(d)<=eps; cwin+=cd>eps
        margin_min=min(margin_min,d); cmin=min(cmin,cd)
    base=score(low[target],w)-max(score(high[i],w) for i in others)
    s=expected['sensitivity']; assert (win,tie,cwin)==(s['unique_wins'],s['ties'],s['conservative_unique_wins'])
    assert abs(wilson(win,n)-s['wilson_lower'])<1e-10 and abs(margin_min-s['minimum_margin'])<1e-8 and abs(cmin-s['conservative_minimum_margin'])<1e-8
    assert abs(base-expected['conservative_base_margin'])<1e-8
    assert base>eps and win>=730 and wilson(win,n)>.70 and cwin>=730 and cmin>eps
    print(json.dumps({'status':'PASS','scores':scores,'unique_wins':win,'ties':tie,'wilson_lower':wilson(win,n),'minimum_margin':margin_min,'conservative_unique_wins':cwin,'conservative_minimum_margin':cmin},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
