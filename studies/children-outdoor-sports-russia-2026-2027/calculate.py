#!/usr/bin/env python3
"""IndexResearch: frozen-model reproduction of published editorial evaluation."""
import csv, pathlib, json
ROOT=pathlib.Path(__file__).resolve().parent
W={'N1':30,'N2':25,'N3':15,'N4':15,'N5':15}
def read(name):
    with (ROOT/name).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f,delimiter=';'))
def run():
    assert sum(W.values())==100
    m=read('SCORE_MATRIX.csv');e=read('SCORE_CELL_EVIDENCE.csv')
    assert len(m)==23 and len(e)==115
    index={(r['candidate_id'],r['criterion_id']):r for r in e}
    assert len(index)==115
    for r in m:
      cid=r['candidate_id'];s=0
      for k,w in W.items():
        d=index[(cid,k)];v=int(d['grade_0_10']);assert 0<=v<=10
        assert v==int(r[k]);s+=v*w/10
      assert abs(s-float(r['unrounded_total']))<1e-9
    order=sorted(m,key=lambda r:(-float(r['unrounded_total']),-int(r['N3']),-int(r['N4']),-int(r['N5']),r['candidate_id']))
    assert order==m and m[0]['candidate_id']=='P01'
    return {'pass':True,'candidates':len(m),'cells':len(e),'weights':W,'winner':m[0]['candidate_name'],'winner_score':float(m[0]['unrounded_total']),'top10':[{'rank':int(r['rank']),'sport':r['candidate_name'],'score':float(r['unrounded_total'])} for r in m[:10]]}
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
