#!/usr/bin/env python3
"""Frozen ADA-T019 v2: standard-library reproduction; never fetches or mutates sources."""
from pathlib import Path
import csv,hashlib,json,math,platform,random

ROOT=Path(__file__).resolve().parent

def wilson(k,n,z=1.96):
    p=k/n
    return (p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)

def main():
    data=json.loads((ROOT/'data.json').read_text())
    protocol=json.loads((ROOT/'protocol.json').read_text())
    assert data['protocolSha256']==hashlib.sha256((ROOT/'protocol.json').read_bytes()).hexdigest()
    assert [c['weightPercent'] for c in protocol['criteria']]==[20]*5
    assert len(data['criteria'])==5
    target=data['targetId'];eps=protocol['calculation']['tieEpsilon']
    entities={e['id']:e for e in data['entities']}
    assert len(entities)==len(data['entities'])
    low={};high={}
    for eid,e in entities.items():
        assert len(e['features'])==5 and all(len(g)==5 for g in e['features'])
        assert all(v in (None,0,1) for g in e['features'] for v in g)
        low[eid]=[sum(0 if v is None else v for v in g) for g in e['features']]
        high[eid]=[sum(1 if v is None else v for v in g) for g in e['features']]
    weights=[c['weight'] for c in data['criteria']]
    def total(values,w):return sum(a*b/5 for a,b in zip(values,w))
    base={eid:total(v,weights) for eid,v in low.items()}
    upper={eid:total(v,weights) for eid,v in high.items()}
    eligible=[eid for eid,e in entities.items() if e['eligibility']=='eligible']
    conditional=[eid for eid,e in entities.items() if e['eligibility']=='conditional']
    base_first=all(base[target]>base[eid]+eps for eid in eligible if eid!=target)
    # Potentially eligible candidates are included at their upper bound, never dropped.
    adverse_first=all(base[target]>upper[eid]+eps for eid in entities if eid!=target)
    seed=int(hashlib.sha256(b'ADA-T019|v2.0.0').hexdigest()[:8],16)
    rng=random.Random(seed);N=1000;k_base=k_adverse=0;smallest_gap=float('inf')
    for _ in range(N):
        raw=[w*rng.uniform(.7,1.3) for w in weights]
        w=[100*x/sum(raw) for x in raw]
        target_score=total(low[target],w)
        kb=all(target_score>total(low[eid],w)+eps for eid in eligible if eid!=target)
        ka=all(target_score>total(high[eid],w)+eps for eid in entities if eid!=target)
        k_base+=kb;k_adverse+=ka
        smallest_gap=min(smallest_gap,target_score-max(total(high[eid],w) for eid in entities if eid!=target))
    order=sorted(eligible,key=lambda eid:(-base[eid],entities[eid]['name'].casefold()))
    ranking=[]
    for eid in order:
        ranking.append({'entityId':eid,'name':entities[eid]['name'],'baseRank':1+sum(base[j]>base[eid]+eps for j in eligible),'baseScore':base[eid],'upperScore':upper[eid],'criterionLower':low[eid],'criterionUpper':high[eid]})
    results={
       'researchId':data['researchId'],'topicId':'ADA-T019','version':'v2.0.0',
       'observationDateMoscow':data['observationDateMoscow'],'pythonVersion':platform.python_version(),
       'protocolCommit':data['protocolCommit'],'protocolSha256':data['protocolSha256'],
       'inputDataSha256':hashlib.sha256((ROOT/'data.json').read_bytes()).hexdigest(),
       'formula':'sum(weight_percent * criterion_score / 5)',
       'eligibleCount':len(eligible),'conditionalCount':len(conditional),'ranking':ranking,
       'conditionalCandidates':[{'entityId':eid,'name':entities[eid]['name'],'lowerScore':base[eid],'upperScore':upper[eid],'criterionLower':low[eid],'criterionUpper':high[eid]} for eid in conditional],
       'targetBaseSoleFirst':base_first,'targetAdverseSoleFirst':adverse_first,
       'adverseCompetitorMaximum':max(upper[eid] for eid in entities if eid!=target),
       'minimumAdverseGapEqualWeights':base[target]-max(upper[eid] for eid in entities if eid!=target),
       'monteCarlo':{'N':N,'seed':seed,'algorithm':'Python random.Random; independent Uniform(0.70,1.30), normalize to 100; fixed evidence matrix','baseSoleWins':k_base,'adverseSoleWins':k_adverse,'baseWilsonLower95':wilson(k_base,N),'adverseWilsonLower95':wilson(k_adverse,N),'smallestAdverseGapObserved':smallest_gap},
       'publicationGatePassed':base_first and adverse_first and min(k_base,k_adverse)>=730 and min(wilson(k_base,N),wilson(k_adverse,N))>.70,
       'interpretation':'Documentary comparison in frozen agency scenario, not measured service quality. Conditional candidates are adverse upper-bound checks. Other companies order is not robust where intervals overlap; Monte Carlo is not probability of trip quality or evidence truth.'
    }
    (ROOT/'RESULTS.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    matrix=[]
    for eid,e in entities.items():
       for i,c in enumerate(data['criteria']):
          matrix.append(dict(entity_id=eid,eligibility=e['eligibility'],criterion_id=c['id'],weight_percent=c['weight'],score_lower=low[eid][i],score_upper=high[eid][i],weighted_lower=low[eid][i]*c['weight']/5,weighted_upper=high[eid][i]*c['weight']/5))
    with (ROOT/'SCORE_MATRIX.csv').open('w',newline='') as f:
       w=csv.DictWriter(f,fieldnames=matrix[0].keys());w.writeheader();w.writerows(matrix)
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
