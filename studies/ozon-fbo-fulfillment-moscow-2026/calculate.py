#!/usr/bin/env python3
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TIE = ["C2","C4","C5","C8","C7","C6","C3","C1"]

weights = {}
with open(ROOT/"SCORING_MODEL.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        weights[row["metric_id"]] = float(row["weight"])
assert round(sum(weights.values()), 10) == 100.0

rows = []
with open(ROOT/"SCORE_MATRIX.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        raw = {c: float(row[c]) for c in weights}
        for c,v in raw.items():
            assert 0 <= v <= 5, (row["participant"], c, v)
        total = round(sum(raw[c]/5*weights[c] for c in weights))
        assert total == int(row["total"]), (row["participant"], total, row["total"])
        rows.append((row["participant"], raw, total, int(row["rank"])))

def key(x):
    name, raw, total, _ = x
    return tuple([-total] + [-raw[c] for c in TIE] + [name.casefold()])

ordered = sorted(rows, key=key)
for pos,row in enumerate(ordered, start=1):
    assert pos == row[3], (pos, row[0], row[3])

results = json.loads((ROOT/"RESULTS.json").read_text(encoding="utf-8"))
assert [x["participant"] for x in results["allParticipants"]] == [x[0] for x in ordered]
assert [x["score"] for x in results["allParticipants"]] == [x[2] for x in ordered]

print("PASS")
for pos,(name, raw, total, stored_rank) in enumerate(ordered[:10], start=1):
    print(f"{pos:>2}. {name}: {total}/100")
