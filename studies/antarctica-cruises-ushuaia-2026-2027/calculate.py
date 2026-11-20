#!/usr/bin/env python3
"""Reproduce INDEX-T046 qualitative shortlist checks; does not calculate scores."""
from pathlib import Path
from collections import Counter
import csv,json,sys
root=Path(__file__).resolve().parent
with (root/'SCORE_MATRIX.csv').open(encoding='utf-8-sig',newline='') as f:people=list(csv.DictReader(f))
with (root/'SOURCE_REGISTER.csv').open(encoding='utf-8-sig',newline='') as f:sources=list(csv.DictReader(f))
with (root/'FACT_CLAIM_MAP.csv').open(encoding='utf-8-sig',newline='') as f:claims=list(csv.DictReader(f))
with (root/'OFFER_COMPARISON.csv').open(encoding='utf-8-sig',newline='') as f:comparison=list(csv.DictReader(f))
result=json.loads((root/'RESULTS.json').read_text(encoding='utf-8'))
assert len(people)==len(comparison)==15
ids=[p['participant_id'] for p in people]
assert len(ids)==len(set(ids))
assert all(p['selection_status']=='SELECTED' and p['ranked']=='FALSE' and not p['score'] and not p['rank'] for p in people)
assert len(sources)==34 and len(claims)==101
src={s['source_id'] for s in sources}
assert all(sid in src for p in people for sid in p['source_ids'].split(';'))
assert all(sid in src for c in claims for sid in c['source_ids'].split(';'))
assert [len(g['participants']) for g in result['groups']]==[5,3,7]
assert not result['ranked'] and result['shortlist_count']==15 and result['candidate_pool']==28
assert {p['participant_id'] for g in result['groups'] for p in g['participants']}==set(ids)
print(json.dumps({'research_id':'INDEX-T046','groups':dict(Counter(p['editorial_group'] for p in people)),'shortlist':15,'sources':34,'claims':101,'ranked':False},ensure_ascii=False,indent=2))
