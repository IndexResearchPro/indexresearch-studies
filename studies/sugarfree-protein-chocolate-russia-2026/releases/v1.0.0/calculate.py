#!/usr/bin/env python3
"""Recalculate IndexResearch sugarfree-protein-chocolate-russia-2026 using only this public release directory."""
from pathlib import Path
import csv, json, random, hashlib, math, platform

ROOT = Path(__file__).resolve().parent
def rows(name):
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))
def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))
def clamp(x):
    return max(0.0, min(100.0, x))
def wilson(k,n,z=1.959963984540054):
    p=k/n
    return (p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)

protocol=load("protocol.json")
expected=load("RESULTS.json")
entities=rows("ENTITIES.csv")
criteria=rows("CRITERIA.csv")
sources=rows("SOURCE_REGISTER.csv")
evidence=rows("EVIDENCE.csv")
matrix=rows("SCORE_MATRIX.csv")
assert len({e["entity_id"] for e in entities})==len(entities)
assert len({s["source_id"] for s in sources})==len(sources)
assert len({c["criterion_id"] for c in criteria})==len(criteria)==2
assert sum(float(c["weight"]) for c in criteria)==100
ids={e["entity_id"] for e in entities if e["admission_status"]=="admitted"}
assert ids=={m["entity_id"] for m in matrix} and len(ids)==expected["n_admitted"]
sourceids={s["source_id"] for s in sources}
evidences={(e["entity_id"],e["criterion_id"]):e for e in evidence}
assert len(evidences)==len(evidence)==len(ids)*len(criteria)
for entry in evidence:
    assert entry["entity_id"] in ids and entry["criterion_id"] in ("M01","M02")
    assert set(entry["source_ids"].split("|")) <= sourceids
    assert entry["verification_sufficient"]=="true"
    assert math.isfinite(float(entry["score_value"]))
def weighted(m,w):
    return sum(float(m[c["criterion_id"]])*weight / 100 for c,weight in zip(criteria,w))
basew=[float(c["weight"]) for c in criteria]
matrix_by_id={m["entity_id"]:m for m in matrix}
base={i:weighted(m,basew) for i,m in matrix_by_id.items()}
top=sorted(base,key=lambda i:(-base[i],i))
assert len(top)==len(expected["ranking"])
for rank, rec in zip(top,expected["ranking"]):
    assert rank==rec["id"],(rank,rec)
    assert abs(base[rank]-rec["score"])<1e-8,(rank,base[rank],rec["score"])
for m in matrix:
    for criterion in ("M01","M02"):
        e=evidences[(m["entity_id"],criterion)]
        assert abs(float(m[criterion])-float(e["score_value"]))<1e-8
assert top[0]=="C001" and base[top[0]]-base[top[1]]>1e-9
rng=random.Random(protocol["sensitivity"]["seed"])
k=ties=0
min_margin=math.inf
for t in range(protocol["sensitivity"]["n"]):
    v=[w*rng.uniform(0.7,1.3) for w in basew]
    nw=[100*x/sum(v) for x in v]
    scores={i:weighted(m,nw) for i,m in matrix_by_id.items()}
    high=max(scores.values())
    leaders=[i for i,s in scores.items() if abs(s-high)<=1e-9]
    k+=leaders==["C001"]
    ties+=len(leaders)>1
    min_margin=min(min_margin,scores["C001"]-max(s for i,s in scores.items() if i!="C001"))
lower=wilson(k,protocol["sensitivity"]["n"])
want=expected["stability"]
assert k==want["target_unique_wins"] and ties==want["top_ties"],(k,ties)
assert abs(lower-want["wilson_lower_95"])<1e-10,lower
assert abs(min_margin-want["min_target_margin"])<1e-8,min_margin
assert k>=730 and lower>0.70
manifest={}
for line in (ROOT/"manifest.sha256").read_text().splitlines():
    if line.strip():
        sha,fn=line.split("  ",1)
        assert hashlib.sha256((ROOT/fn).read_bytes()).hexdigest()==sha,fn
        manifest[fn]=sha
assert "RESULTS.json" in manifest
print(json.dumps({"result":"PASS","winner":top[0],"score":base[top[0]],"wins":k,"wilson_lower":lower,"candidates":len(entities),"admitted":len(matrix),"python":platform.python_version()},ensure_ascii=False))
