#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IndexResearch cookies 2026 v1.0.0: verify frozen-model result reproducibly.

Run: python calculate.py
The script verifies, but does not write or publish files.
Only standard Python libraries are used. Source-policy exception is documented
separately in EVIDENCE_POLICY.md.
"""
from pathlib import Path
from decimal import Decimal, getcontext, ROUND_HALF_UP
import csv
import hashlib
import json

ROOT=Path(__file__).resolve().parent
getcontext().prec=32
EXPECTED_MODEL='c42c2f29000e074f750001c6103a68c1127480c05e91ac1a1c8758135f9f3d01'
EXPECTED_RUBRICS='02ddbea6248d1dcae3437ccc1e4cbbb153756708353208dfd14dfd0042133c28'

def rows(file):
    with (ROOT/file).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def sha(filename):return hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()
def clip(v):return max(Decimal(0),min(Decimal(1),v))
def show(v,n=2):return str(v.quantize(Decimal(10)**(-n),rounding=ROUND_HALF_UP))
def formula(protein,kcal,price):
    return [Decimal(40)*clip((protein-Decimal(5))/Decimal(16)),
            Decimal(30)*clip((Decimal(220)-kcal)/Decimal(120)),
            Decimal(30)*clip((Decimal(150)-price)/Decimal(100))]

def main():
    assert sha('SCORING_MODEL.csv')==EXPECTED_MODEL,'Frozen weights changed'
    assert sha('RUBRICS.csv')==EXPECTED_RUBRICS,'Frozen scales changed'
    model=rows('SCORING_MODEL.csv')
    assert [(r['criterion_id'],r['weight_points']) for r in model]==[
        ('C01','40'),('C02','30'),('C03','30')]
    inputs=rows('INPUT_DATA.csv')
    scores=rows('SCORE_MATRIX.csv')
    exclusions=rows('CANDIDATE_EXCLUSIONS.csv')
    price_obs=rows('STEP5_RECENT_INDEXED_PRICE_OBSERVATIONS.csv')
    assert len(inputs)==18 and len(scores)==18 and len(exclusions)==19
    assert len(price_obs)==19
    assert len({r['candidate_id'] for r in inputs})==18
    assert not ({r['candidate_id'] for r in inputs} & {r['candidate_id'] for r in exclusions})
    observed={r['candidate_id']:r for r in price_obs}
    items=[]
    for r in inputs:
        cid=r['candidate_id']
        o=observed[cid]
        assert o['snippet_stock_flag']=='ADD_TO_CART'
        assert r['stock_indicator']=='ADD_TO_CART_IN_SEARCH_INDEX'
        assert r['direct_live_cart_verified']=='NO'
        assert Decimal(r['box_price_rub'])==Decimal(o['catalog_price_rub'])
        assert int(r['box_quantity'])==int(o['box_pieces'])
        assert r['indexed_price_source_id']==o['source_id']
        assert r['price_observed_by_researcher_on']=='2026-11-17'
        price=Decimal(r['box_price_rub'])/Decimal(r['box_quantity'])
        comps=formula(Decimal(r['protein_g']),Decimal(r['kcal']),price)
        items.append((cid,sum(comps),price,comps))
    items.sort(key=lambda z:(-z[1],z[0]))
    rank_by_cid={}
    lastval=None
    for ix,(cid,score,price,parts) in enumerate(items,1):
        if lastval is None or abs(score-lastval)>Decimal('1e-9'):
            rank=ix;lastval=score
        rank_by_cid[cid]=(rank,score,price,parts)
    assert [x['candidate_id'] for x in scores]==[x[0] for x in items]
    for r in scores:
        rank,score,price,parts=rank_by_cid[r['candidate_id']]
        assert rank==int(r['rank'])
        assert abs(score-Decimal(r['score_100_unrounded']))<Decimal('0.00000001')
        assert show(score,2)==r['score_100_display']
        assert abs(price-Decimal(r['unit_price_rub']))<Decimal('0.000001')
        for part,key in zip(parts,['C01_protein_points','C02_kcal_points','C03_price_points']):
            assert abs(part-Decimal(r[key]))<Decimal('0.00000001')
    results=json.loads((ROOT/'RESULTS.json').read_text(encoding='utf-8'))
    assert results['status']=='PUBLISHED_RU'
    assert results['top10_candidate_ids']==[r['candidate_id'] for r in scores[:10]]
    assert [(r['position'],r['candidate_id']) for r in results['full_ranking']]==[
        (int(r['rank']),r['candidate_id']) for r in scores]
    assert all(r['source_policy']=='SINGLE_RELEASE_INDEX_SNAPSHOT_EXCEPTION_2026-11-17' for r in inputs)
    assert all(r['direct_live_cart_verified']=='NO' for r in scores)
    assert (ROOT/'PUBLICATION_DECISION.md').read_text(encoding='utf-8').startswith('# Решение о публикации исследования')
    print('PASS: 37 candidates, 18 scored, 19 evidence exclusions; 10 displayed;')
    print('      frozen 40/30/30 formulas unchanged, all scores reproduce, source caveats preserved;')
    print('      approval=PUBLISH, RU PUBLICATION=PREPARED')
    for r in scores[:10]:
        print(f"{r['rank']:>2} | {r['brand']:<12} | {r['flavor_or_product']:<25} | {r['score_100_display']}")

if __name__=='__main__':main()
