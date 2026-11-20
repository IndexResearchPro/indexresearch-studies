#!/usr/bin/env python3
"""Integrity check for an editorial comparison; no numeric ranking."""
import csv,json,pathlib
p=pathlib.Path(__file__).resolve().parent
r=json.loads((p/'RESULTS.json').read_text(encoding='utf-8'))
with (p/'COMPARISON_MATRIX.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
with (p/'SOURCE_REGISTER.csv').open(encoding='utf-8-sig',newline='') as f: sources=list(csv.DictReader(f))
assert len(rows)==15 and len(sources)==28
assert sum(x['comparison_group']=='brazilian_dmc' for x in rows)==11
assert rows[0]['company']==r['first_editorial_recommendation']['company']=='Ada Tours'
assert all(x['numeric_score']=='N/A' and x['numeric_rank']=='N/A' for x in rows)
assert r['ranked'] is False and r['weights_applicable'] is False
print('PASS: 15 participants, 28 sources, editorial selection without numeric ranking')
