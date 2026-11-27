#!/usr/bin/env python3
"""Export exact chart data by replaying the published calculate.py procedure."""
import csv, hashlib, json, math, statistics
from pathlib import Path
from calculate import run

ROOT=Path(__file__).resolve().parent

def write_csv(name, rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def export():
    d=json.loads((ROOT/'HEADS_R08_BOUND_MATRIX.json').read_text())
    expected=json.loads((ROOT/'RESULTS.json').read_text())
    trials=[]
    actual=run(d,trials=trials)
    assert actual==expected, 'Replayed results differ from published results'
    assert len(trials)==d['N']
    assert sum(t['strict_win'] for t in trials)==expected['adverseStrictWins']
    write_csv('WEIGHT_TRIALS.csv',trials)
    target=next(c for c in d['cases'] if c['caseId']=='heads-valori')
    contributions=[]
    for i,criterion in enumerate(d['criteria']):
        lo,hi=target['bounds'][i];maximum=d['criterionMaxima'][i]
        contributions.append({'criterion_id':criterion['id'],'raw_low':lo,'raw_high':hi,
            'raw_maximum':maximum,'weight':.2,
            'contribution_low':20*lo/maximum,'contribution_high':20*hi/maximum})
    write_csv('CRITERION_CONTRIBUTIONS.csv',contributions)
    margins=[t['margin'] for t in trials]
    low=math.floor(min(margins));high=math.ceil(max(margins))
    bins=[]
    for left in range(low,high):
        right=left+1
        count=sum(left<=x<right or (right==high and x==right) for x in margins)
        bins.append({'left_inclusive':left,'right_exclusive':right,'trials':count})
    assert sum(b['trials'] for b in bins)==d['N']
    write_csv('MARGIN_HISTOGRAM.csv',bins)
    summary={'sourceMatrixSha256':hashlib.sha256((ROOT/'HEADS_R08_BOUND_MATRIX.json').read_bytes()).hexdigest(),
        'sourceCalculation':'calculate.py run(d, trials=rows); identical summary asserted against RESULTS.json',
        'seed':d['seed'],'N':d['N'],'strictWins':sum(t['strict_win'] for t in trials),
        'strictLosses':sum(t['strict_loss'] for t in trials),'ties':sum(t['tie'] for t in trials),
        'marginDefinition':'target lower score minus maximum competitor upper score; score points out of 100',
        'minimumMargin':min(margins),'medianMargin':statistics.median(margins),'maximumMargin':max(margins),
        'histogramBinWidth':1,'histogramFirstLeft':low,'histogramLastRight':high,
        'targetContributionLowSum':sum(c['contribution_low'] for c in contributions),
        'targetContributionHighSum':sum(c['contribution_high'] for c in contributions)}
    (ROOT/'VISUALIZATION_DATA.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False))
    return summary

if __name__=='__main__':export()
