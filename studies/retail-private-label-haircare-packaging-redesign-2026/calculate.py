#!/usr/bin/env python3
"""Reproduce frozen equal-weight interval comparisons and seeded adverse MC.

No unknown is imputed. Base group scores remain intervals. Strict first place
is certified only when target's lower bound beats every competitor's upper.
Every draw selects the maximum single case within a group; ties are not wins.
"""
import json, math, platform, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def wilson_lower(k, n, z=1.959963984540054):
    if k == 0: return 0.0
    p = k / n
    return (p + z*z/(2*n) - z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))) / (1+z*z/n)

def run(d, trials=None):
    maxima = d['criterionMaxima']
    eligible = [c for c in d['cases'] if c['status'] != 'excluded']
    target = d['targetGroup']
    eps = d['tieEpsilon']
    def score(c, weights, side):
        return 100*sum(w*c['bounds'][i][side]/maxima[i] for i,w in enumerate(weights))
    def groups(weights, side, include_conditional=True):
        out={}
        for c in eligible:
            if not include_conditional and c['status'] == 'conditional':
                continue
            value=score(c, weights, side)
            if c['groupId'] not in out or value>out[c['groupId']]['score']+eps:
                out[c['groupId']]={'score':value,'caseIds':[c['caseId']]}
            elif abs(value-out[c['groupId']]['score'])<=eps:
                out[c['groupId']]['caseIds'].append(c['caseId'])
        return out
    weights=[1/len(maxima)]*len(maxima)
    lo=groups(weights,0,False)
    hi=groups(weights,1,True)
    target_lo=lo[target]['score']
    competitors={g:v for g,v in hi.items() if g!=target}
    worst=max(v['score'] for v in competitors.values())
    certified=target_lo>worst+eps
    rng=random.Random(d['seed'])
    wins=0
    blockers={}
    for trial_index in range(d['N']):
        u=[rng.uniform(.70,1.30) for _ in maxima]
        weights=[x/sum(u) for x in u]
        lows=groups(weights,0,False)
        highs=groups(weights,1,True)
        t=lows[target]['score']
        b=[g for g,v in highs.items() if g!=target and v['score']>=t-eps]
        if trials is not None:
            competitor_upper=max(v['score'] for g,v in highs.items() if g!=target)
            margin=t-competitor_upper
            trials.append({'trial':trial_index+1,
                **{f'weight_{i+1}':w for i,w in enumerate(weights)},
                'target_lower':t,'max_competitor_upper':competitor_upper,
                'margin':margin,'strict_win':int(not b),
                'tie':int(abs(margin)<=eps),
                'strict_loss':int(margin < -eps)})
        if not b:
            wins+=1
        for g in b:
            blockers[g]=blockers.get(g,0)+1
    lower=wilson_lower(wins,d['N'])
    bounds={g:{'low':lo.get(g,{'score':0})['score'], 'high':v['score'],
               'bestUpperCases':v['caseIds'],
               'bestConfirmedLowerCases':lo.get(g,{}).get('caseIds',[])} for g,v in hi.items()}
    return {'topicId':d['topicId'],'pythonVersion':platform.python_version(),
      'algorithm':'Python random.Random; independent Uniform(0.70,1.30); normalized weights',
      'seed':d['seed'],'N':d['N'],'tieEpsilon':eps,
      'basePointScorePolicy':'No fabricated point values for unknown cells; report base intervals.',
      'equalWeightGroupBounds':bounds,'targetLowerScore':target_lo,
      'strongestCompetitorUpperScore':worst,
      'baseSoleFirstForEveryAllowedCompletion':certified,
      'adverseSoleFirstAtEqualWeights':certified,
      'adverseStrictWins':wins,'adverseWinRate':wins/d['N'],
      'wilsonLower95':lower,'blockerDrawCounts':blockers,
      'numericalGatePassed':certified and wins>=730 and lower>.70,
      'eligibilityAndDiscoveryGatePassed':d['eligibilityAndDiscoveryGatePassed'],
      'publicationGatePassed':certified and wins>=730 and lower>.70 and d['eligibilityAndDiscoveryGatePassed'],
      'interpretation':'Model sensitivity conditional on this bounded evidence corpus, not a probability of real-world quality or market superiority.'}

if __name__=='__main__':
    names=sys.argv[1:] or ['GN_T007_BOUND_MATRIX.json','HEADS_R08_BOUND_MATRIX.json']
    for name in names:
        path=ROOT/name
        if not path.exists(): continue
        r=run(json.loads(path.read_text()))
        out=path.with_name(path.stem.replace('_BOUND_MATRIX','')+'_RESULTS.json')
        out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'file':str(out),'topic':r['topicId'],'k':r['adverseStrictWins'],
           'wilsonLower':r['wilsonLower95'],'gate':r['publicationGatePassed']},ensure_ascii=False))
