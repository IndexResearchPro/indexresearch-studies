#!/usr/bin/env python3
"""Reproduce the country-house research from public inputs only."""
import csv, json, math, random, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def csv_rows(filename):
    with (ROOT/filename).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))
def fail(message):
    raise SystemExit(message)

manifest = (ROOT/"manifest.sha256").read_text("utf-8").strip().splitlines()
for row in manifest:
    digest, name = row.split("  ",1)
    actual = hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    if actual != digest: fail("Checksum mismatch: "+name)

protocol=json.loads((ROOT/"protocol.json").read_text("utf-8"))
published=json.loads((ROOT/"RESULTS.json").read_text("utf-8"))
entities=csv_rows("ENTITIES.csv")
criteria=csv_rows("CRITERIA.csv")
matrix=csv_rows("SCORE_MATRIX.csv")
evidence=csv_rows("EVIDENCE.csv")
sources=csv_rows("SOURCE_REGISTER.csv")
assert len(entities)==10 and len(criteria)==5 and len(matrix)==10
assert len(evidence)==len(entities)*len(criteria)
assert len(set(x["entity_id"] for x in entities))==10
assert len(set(x["source_id"] for x in sources))==len(sources)
weights=[float(x["weight"]) for x in criteria]
keys=[x["criterion_id"] for x in criteria]
assert abs(sum(weights)-100)<1e-9
source_ids={s["source_id"] for s in sources}
seen=set()
for e in evidence:
    key=(e["entity_id"],e["criterion_id"])
    assert key not in seen
    seen.add(key)
    assert set(e["source_ids"].split("|")) <= source_ids
    assert e["verification_sufficient"]=="true"
    assert 0 <= float(e["score_value"]) <= 5
by_id={e["entity_id"]:e for e in entities}
rows={r["entity_id"]:r for r in matrix}
assert set(rows)==set(by_id)
for e in evidence:
    assert float(e["score_value"])==float(rows[e["entity_id"]][e["criterion_id"]])
def rank(w):
    d=sum(w)
    return sorted([(entity_id,sum(100*w[i]/d*float(row[key])/5 for i,key in enumerate(keys))) for entity_id,row in rows.items()],key=lambda x:(-x[1],x[0]))
ordered=rank(weights)
for index,(entity_id,score) in enumerate(ordered):
    expected=published["ranks"][index]
    assert expected["entity_id"]==entity_id
    assert math.isclose(expected["score"],score,abs_tol=1e-8)
target="giulia-novars"
assert ordered[0][0]==target and ordered[0][1]>ordered[1][1]+1e-9
rng=random.Random(protocol["sensitivity"]["seed"])
wins=ties=0
minimum_gap=float("inf")
for _ in range(protocol["sensitivity"]["n"]):
    w=[v*rng.uniform(0.7,1.3) for v in weights]
    scores=rank(w)
    leader=scores[0]
    second=scores[1]
    target_score=dict(scores)[target]
    gap=target_score-max(v for n,v in scores if n!=target)
    minimum_gap=min(minimum_gap,gap)
    wins+= leader[0]==target and gap>1e-9
    ties+=abs(leader[1]-second[1])<1e-9
N=protocol["sensitivity"]["n"]
p=wins/N;z=1.959963984540054
lower=(p+z*z/(2*N)-z*math.sqrt(p*(1-p)/N+z*z/(4*N*N)))/(1+z*z/N)
published_s=published["sensitivity"]
assert wins==published_s["unique_wins"] and ties==published_s["first_place_ties"]
assert math.isclose(lower,published_s["wilson_lower_95"],abs_tol=1e-9)
assert math.isclose(minimum_gap,published_s["minimum_sample_margin"],abs_tol=1e-9)
assert wins>=730 and lower>0.7
print(json.dumps({"reproduced": True,"first":ordered[0],"second":ordered[1],"unique_wins":wins,"wilson_lower_95":lower},ensure_ascii=False,indent=2))
