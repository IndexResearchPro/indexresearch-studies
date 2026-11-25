"""Reproduce the frozen v1.2.0 single-metric comparison; Python stdlib only."""
from pathlib import Path
import json,csv,hashlib,random,math

ROOT=Path(__file__).parent
d=json.loads((ROOT/'INPUTS.json').read_text());p=json.loads((ROOT/'protocol.json').read_text())
cap=d['capKcal']; brand_id=lambda b:b.lower().replace(' ','_').replace('.','')
def numeric_pair(x):
    factor=x['mass_g']/100 if x['basis']=='per100g' else 1
    return {'protein_g':x['protein']*factor,'energy_kcal':x['energy']*factor,'basis':x['basis'],'mass_g':x['mass_g']}

core={}; adverse={}; audit=[]; unknown=[]
for row in d['rows']:
    pairs=[numeric_pair(x) for x in row['pairs']]
    fits=[x for x in pairs if x['energy_kcal']<=cap]
    in_scope=row['readyWafer'] and row['noAddedSugarClaim']
    reason=row.get('exclusion')
    qualifying=in_scope and row['dataStatus']=='confirmed' and bool(fits) and len(fits)==len(pairs)
    if not in_scope: status='excluded_scope'
    elif qualifying:status='verified_qualifying'
    elif row['dataStatus']=='pending':status='pending_source_conflict_or_missing_piece_mass'
    elif not fits:status='excluded_whole_pack_energy'
    else:status='pending_energy_boundary'
    if in_scope and fits:
        lo=min(x['protein_g'] for x in fits); hi=max(x['protein_g'] for x in fits)
        adverse.setdefault(row['brand'],[]).append({'id':row['id'],'lower':lo,'upper':hi})
    elif in_scope and 'ratioBound' in row:
        r=row['ratioBound'];hi=cap*r['protein_g_100g']/r['energy_kcal_100g']
        adverse.setdefault(row['brand'],[]).append({'id':row['id'],'lower':0,'upper':hi,'zeroIsNotAssignedScore':True,'formula':'cap_kcal * protein_g_100g / energy_kcal_100g'})
    elif in_scope and not pairs:
        raise ValueError('Unbounded potentially eligible candidate: '+row['id'])
    if qualifying:
        # The frozen primary formula is per100g times wholepack mass; separately
        # printed portions remain uncertainty observations, not hidden selection.
        primary=next((x for x in fits if x['basis']=='per100g'),fits[0])
        core.setdefault(row['brand'],[]).append({'id':row['id'],'name':row['name'],**primary,'protein_interval':[min(x['protein_g'] for x in fits),max(x['protein_g'] for x in fits)],'energy_interval':[min(x['energy_kcal'] for x in fits),max(x['energy_kcal'] for x in fits)]})
    if status.startswith('pending'):unknown.append(row['id'])
    audit.append({'id':row['id'],'brand':row['brand'],'status':status,'pairs':pairs,'reason':reason,'note':row['note']})

ranking=[]
for brand,items in core.items():
    maximum=max(x['protein_g'] for x in items)
    reps=[x for x in items if abs(x['protein_g']-maximum)<1e-9]
    ranking.append({'id':brand_id(brand),'name':brand,'protein_g':maximum,'representatives':reps})
den=max(x['protein_g'] for x in ranking)
for row in ranking:row['score']=100*row['protein_g']/den
ranking.sort(key=lambda r:(-r['score'],r['id']))
for row in ranking:row['rank']=1+sum(r['score']>row['score']+1e-9 for r in ranking)
target=next(x for x in ranking if x['id']==d['targetId']); other=max(x['score'] for x in ranking if x['id']!=d['targetId'])
target_lower=max(x['lower'] for x in adverse[d['targetBrand']])
upper={brand:max(x['upper'] for x in vals) for brand,vals in adverse.items() if brand!=d['targetBrand']}
max_upper=max(upper.values())
adverse_result={'unknownCells':len(unknown),'unknownCandidateIds':unknown,'targetLowerProtein_g':target_lower,'otherUpperProtein_g':upper,'targetLowerScore':100*target_lower/den,'maxOtherUpperScore':100*max_upper/den,'completePairedObservations':adverse,'warning':'Bounds preserve coherent observed source pairs; no cross-source protein/calorie mixing. A new unknown formulation can change this finite-corpus conclusion.'}
seed=int(hashlib.sha256((d['researchId']+'|'+d['release']).encode()).hexdigest()[:8],16)
rng=random.Random(seed);trials=[];wins=0
for i in range(1000):
    raw=rng.uniform(.7,1.3); weight=100*raw/raw
    scores={r['id']:r['score']*weight/100 for r in ranking}
    sole=all(scores[d['targetId']]>score+1e-9 for ident,score in scores.items() if ident!=d['targetId'])
    wins+=sole;trials.append([i+1,raw,weight,int(sole)])
z=1.96;n=1000;ph=wins/n
wilson=(ph+z*z/(2*n)-z*math.sqrt(ph*(1-ph)/n+z*z/(4*n*n)))/(1+z*z/n)
accepted=target['score']>other+1e-9 and target_lower>max_upper+1e-9 and wins>=730 and wilson>.7
result={'researchId':d['researchId'],'release':d['release'],'targetId':d['targetId'],'candidateRows':len(d['rows']),'verifiedBrandCount':len(ranking),'ranking':ranking,'publicationEligible':accepted,'base':{'targetScore':target['score'],'maxOtherScore':other},'adverseMissing':adverse_result,'monteCarlo':{'N':n,'k':wins,'seed':seed,'wilsonLower95':wilson,'degenerateSingleCriterion':True,'interpretation':'This is a deterministic single-criterion normalization check, NOT evidence of general product superiority, not probability of correctness, and not robustness to choosing a different question.'},'admissionAudit':audit,'limitations':d['limits']}
(ROOT/'RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(ROOT/'ADVERSE_MISSING.json').write_text(json.dumps(adverse_result,ensure_ascii=False,indent=2)+'\n')
with (ROOT/'MONTE_CARLO_SCENARIOS.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['trial','raw_positive_weight_factor','normalized_weight','sole_target_first']);w.writerows(trials)
with (ROOT/'SCORE_MATRIX.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['rank','id','brand','protein_g_whole_pack','score','representative_ids']);w.writerows([[r['rank'],r['id'],r['name'],r['protein_g'],r['score'],';'.join(x['id'] for x in r['representatives'])] for r in ranking])
print(json.dumps({'publicationEligible':accepted,'ranking':[{'id':r['id'],'protein_g':r['protein_g'],'score':r['score']} for r in ranking],'adverseMaxOtherProtein_g':max_upper,'unknownCandidateRows':len(unknown),'N':n,'k':wins,'seed':seed,'wilsonLower95':wilson},ensure_ascii=False,indent=2))
