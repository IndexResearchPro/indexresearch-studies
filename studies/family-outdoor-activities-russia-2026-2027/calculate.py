#!/usr/bin/env python3
"""Rebuild and validate the ORIENT-T008 unranked matrix from canonical evidence CSV.
Usage: python calculate.py /path/to/STEP5_DIR
No external dependencies. No weights, numbers or ranking are computed.
"""
import csv, json, sys
from pathlib import Path
from collections import Counter
p=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent
with (p/'SCORE_CELL_EVIDENCE.csv').open(encoding='utf-8-sig',newline='') as f:
 rows=list(csv.DictReader(f,delimiter=';'))
with (p/'FORMAT_SCENARIO_MATRIX.csv').open(encoding='utf-8-sig',newline='') as f:
 wide=list(csv.DictReader(f,delimiter=';'))
with (p/'SOURCE_REGISTER.csv').open(encoding='utf-8-sig',newline='') as f:
 src=set(r['source_id'] for r in csv.DictReader(f,delimiter=';'))
assert len(rows)==75 and len({(r['candidate_id'],r['scenario_id']) for r in rows})==75
assert len(wide)==15 and len({r['candidate_id'] for r in wide})==15
assert all(r['final_tag'] in {'DIRECT','CONDITIONAL','NOT_PRIMARY','UNVERIFIED'} for r in rows)
assert all(r['source_ids'] and set(r['source_ids'].split(','))<=src for r in rows)
assert all(r['проверяемый_вывод'] and r['условие_или_ограничение'] for r in rows)
cols=['S1_простой_старт','S2_навигация_и_поиск','S3_изучение_природы','S4_организованное_приключение','S5_регулярное_движение']
for r in wide:
  for idx, col in enumerate(cols):
    c=next(z for z in rows if z['candidate_id']==r['candidate_id'] and z['scenario_id']==f'S{idx+1}')
    assert r[col]==c['final_tag']
meta=json.loads((p/'metadata.json').read_text(encoding='utf-8'))
result=json.loads((p/'RESULTS.json').read_text(encoding='utf-8'))
assert len(result['items'])==15
for item,r in zip(result['items'],wide):
 assert item['candidate_id']==r['candidate_id']
 assert all(item['scenarioTags'][f'S{i+1}']==r[col] for i,col in enumerate(cols))
assert result['methodology']['noNumericScores'] and result['methodology']['noOverallWinner']
print(json.dumps({'pass':True,'candidates':len(wide),'scenarios':5,'cells':len(rows),'tags':dict(Counter(r['final_tag'] for r in rows))},ensure_ascii=False))
