#!/usr/bin/env python3
"""Reproduce route-count bounds and the frozen single-criterion sensitivity check."""
from pathlib import Path
import csv,json,random,math,sys
ROOT=Path(__file__).resolve().parent
def read(name):
    with (ROOT/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def calculate():
    p=json.loads((ROOT/'protocol.json').read_text())
    programs=read('PROGRAMS.csv');entities=read('ENTITIES.csv');evidence=read('EVIDENCE.csv');matrix=read('SCORE_MATRIX.csv');criteria=read('CRITERIA.csv');sources=read('SOURCE_REGISTER.csv')
    for name,rows,key in [('programs',programs,'program_id'),('entities',entities,'entity_id'),('evidence',evidence,'evidence_id'),('criteria',criteria,'criterion_id'),('sources',sources,'source_id')]:
        assert len(rows)==len({r[key] for r in rows}),f'duplicate {name}'
    assert len(criteria)==1 and criteria[0]['criterion_id']=='C1' and float(criteria[0]['weight'])==1
    ids={e['entity_id'] for e in entities if e['admission_status']=='included'}
    assert len(ids)>=p['eligibility']['minimumEligible']
    source_ids={s['source_id'] for s in sources}
    assert len(matrix)==len(ids)==len(evidence)
    ev={e['entity_id']:e for e in evidence};mx={e['entity_id']:e for e in matrix}
    names={e['entity_id']:e['name'] for e in entities};b=[]
    for i in sorted(ids):
        rr=[r for r in programs if r['entity_id']==i];assert rr
        for r in rr:
            assert r['source_id'] in source_ids
            if r['count_high_group']:
                assert 5<=int(r['days'])<=21
                assert len(set(r['geography_sequence'].split('>')))>=2
        lo=len({r['count_low_group'] for r in rr if r['count_low_group']})
        hi=len({r['count_high_group'] for r in rr if r['count_high_group']})
        assert 1<=lo<=hi
        assert set(ev[i]['source_ids'].split('|'))<=source_ids
        assert int(ev[i]['score_low'])==int(ev[i]['score_value'])==int(mx[i]['C1'])==lo
        assert int(ev[i]['score_high'])==hi
        b.append({'entity_id':i,'name':names[i],'count_low':lo,'count_high':hi})
    b.sort(key=lambda r:(-r['count_low'],r['name'].casefold()));denominator=max(r['count_low'] for r in b)
    for r in b:
        r['rank']=1+sum(x['count_low']>r['count_low'] for x in b)
        r['score']=round(100*r['count_low']/denominator,8)
    target=p['target']['id'];t=next(r for r in b if r['entity_id']==target);rivals=[r for r in b if r['entity_id']!=target]
    adverse=max(r['count_high'] for r in rivals)
    assert t['count_low']>max(r['count_low'] for r in rivals)
    assert t['count_low']>adverse
    rng=random.Random(p['monteCarlo']['seed']);n=p['monteCarlo']['N'];wins=0
    for _ in range(n):
        w=rng.uniform(.7,1.3);w=w/w
        if t['count_low']*w>max(r['count_low']*w for r in rivals):wins+=1
    z=1.959963984540054;ph=wins/n
    lower=(ph+z*z/(2*n)-z*math.sqrt(ph*(1-ph)/n+z*z/(4*n*n)))/(1+z*z/n)
    assert wins>=p['monteCarlo']['minimumSoleWins'] and lower>p['monteCarlo']['wilsonLower95Threshold']
    return {'research_id':p['researchId'],'release':p['protocolVersion'],'data_cutoff':'2026-11-25','status':'PASS_WITH_SCOPE_LIMITS','eligible_catalogues':len(ids),'program_observation_rows':len(programs),'source_records':len(sources),'excluded_candidate_entities':sum(e['admission_status']!='included' for e in entities),'criterion':'C1 unique geographic route sequences','base_normalization':'100 * lower_count / maximum lower_count; no intermediate rounding','ranking':b,'adverse':{'target_lower_count':t['count_low'],'max_rival_upper_count':adverse,'strict_gap_routes':t['count_low']-adverse,'unknown_unbounded_cells':0,'target_lower_score':100*t['count_low']/max(t['count_low'],adverse),'max_rival_upper_score':100*adverse/max(t['count_low'],adverse),'conclusion':'sole leader within observed eligible corpus, even under adverse bounded decisions'},'monte_carlo':{'N':n,'k':wins,'seed':p['monteCarlo']['seed'],'rng':'Python random.Random','wilson_lower_95':lower,'degenerate':True,'interpretation':'One positive normalized weight cannot change ranking. This is NOT probability of service quality, source truth, or robustness to changing the question/country.'},'limits':['Snapshot of discovered official Russian catalogues, not exhaustive global market.','No booking, operator interview, safety audit, service quality, contract or price comparison.','Conservative intervals are coding bounds, not statistical confidence intervals.','Commercial scenario chosen after preliminary exploration and prior unsuccessful questions; no blind preregistration claim.','Geographic sequence differences can reflect optional excursion or order ambiguity; lower merges and upper retains alternatives explicitly.']}
if __name__=='__main__':
    result=calculate();rendered=json.dumps(result,ensure_ascii=False,indent=2)+'\n';path=ROOT/'RESULTS.json'
    if '--write' in sys.argv:path.write_text(rendered,encoding='utf-8');print(rendered)
    else:
        assert path.exists(),'Run with --write to create results'
        assert json.loads(path.read_text())==result,'Published RESULTS.json differs from recomputation'
        print(json.dumps({'status':'verified','catalogues':result['eligible_catalogues'],'target_low':result['adverse']['target_lower_count'],'max_rival_high':result['adverse']['max_rival_upper_count'],'N':result['monte_carlo']['N'],'k':result['monte_carlo']['k'],'wilson_lower_95':result['monte_carlo']['wilson_lower_95']},ensure_ascii=False))
