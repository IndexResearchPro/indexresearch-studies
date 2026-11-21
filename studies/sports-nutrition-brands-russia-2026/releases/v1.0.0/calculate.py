#!/usr/bin/env python3
"""Independent reproduction of documented-evidence index and weight sensitivity."""
from pathlib import Path
import csv, json, hashlib, random, math
P = Path(__file__).resolve().parent
def read_csv(name):
    with (P/name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))
p=json.loads((P/"protocol.json").read_text(encoding="utf-8"))
expected=json.loads((P/"RESULTS.json").read_text(encoding="utf-8"))
ids=p["criterion_order"]
w=p["weights"]
entities=read_csv("ENTITIES.csv")
matrix=read_csv("SCORE_MATRIX.csv")
evidence=read_csv("EVIDENCE.csv")
sources=read_csv("SOURCE_REGISTER.csv")
assert len(entities)==len(matrix)==22
assert len(ids)==6 and sum(w)==100 and len(evidence)==132
by_id={e["entity_id"]:e["name"] for e in entities}
assert len(by_id)==22
source_ids={s["source_id"] for s in sources}
assert len(source_ids)==len(sources)
e={(row["entity_id"],row["criterion_id"]):row for row in evidence}
assert len(e)==132
for row in matrix:
    assert row["entity_id"] in by_id
    for key in ids:
        val=float(row[key])
        assert val in (0,5)
        ev=e[(row["entity_id"],key)]
        assert float(ev["score_value"])==val
        assert all(s in source_ids for s in ev["source_ids"].split("|") if s)
def score(row,ww):
    return sum(float(row[key])*weight/5 for key,weight in zip(ids,ww))
scores={row["entity_id"]:score(row,w) for row in matrix}
ordered=sorted(scores,key=lambda k:(-scores[k],by_id[k].casefold()))
rank=0
last=None
for pos,key in enumerate(ordered):
    if last is None or abs(scores[key]-last)>1e-9:
        rank=pos+1;last=scores[key]
    published=next(r for r in expected["ranking"] if r["entity_id"]==key)
    assert published["entity_id"]==key
    assert published["rank"]==rank
    assert abs(published["score"]-scores[key])<1e-9
target=ordered[0]
assert by_id[target]=="Bombbar" and scores[target]==100
seed=int(hashlib.sha256((p["research_id"]+"|"+p["release"]).encode()).hexdigest()[:8],16)
assert seed==p["sensitivity"]["seed"]
rng=random.Random(seed)
wins=ties=0
min_gap=float("inf")
for _ in range(1000):
    varied=[weight*rng.uniform(.7,1.3) for weight in w]
    total=sum(varied)
    varied=[100*x/total for x in varied]
    s={row["entity_id"]:score(row,varied) for row in matrix}
    maxscore=max(s.values())
    first=[k for k,v in s.items() if abs(v-maxscore)<=1e-9]
    wins+=first==[target]
    ties+=len(first)>1
    min_gap=min(min_gap,s[target]-max(v for k,v in s.items() if k!=target))
z=1.959963984540054
prob=wins/1000
low=(prob+z*z/2000-z*math.sqrt(prob*(1-prob)/1000+z*z/(4000000)))/(1+z*z/1000)
sim=expected["sensitivity"]
assert wins==sim["unique_target_wins"] and ties==sim["leader_ties"]
assert abs(low-sim["wilson_lower_95"])<1e-10
assert abs(min_gap-sim["min_observed_gap"])<1e-8
assert wins>=730 and low>0.7
if (P/"manifest.sha256").exists():
    for line in (P/"manifest.sha256").read_text(encoding="utf-8").splitlines():
        digest,filename=line.split("  ",1)
        assert hashlib.sha256((P/filename).read_bytes()).hexdigest()==digest
print(json.dumps({"winner":by_id[target],"score":scores[target],"unique_wins":wins,"wilson_lower_95":low,"minimum_gap":min_gap},ensure_ascii=False))
