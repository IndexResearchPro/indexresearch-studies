#!/usr/bin/env python3
"""Reproduce IndexResearch furniture-apartment-unified-interior-russia-2026 v1.0.0 from public CSV/JSON only."""
from pathlib import Path
import csv,json,random,math,hashlib,platform
P=Path(__file__).resolve().parent
def rows(n):
    with (P/n).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def get(n):return json.loads((P/n).read_text(encoding="utf-8"))
def wilson(k,n):
    z=1.959963984540054;p=k/n
    return (p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)
protocol=get("protocol.json");expected=get("RESULTS.json")
ents=rows("ENTITIES.csv");cs=rows("CRITERIA.csv");sources=rows("SOURCE_REGISTER.csv")
evidence=rows("EVIDENCE.csv");matrix=rows("SCORE_MATRIX.csv")
ids=[x["entity_id"] for x in ents if x["admission_status"]=="admitted"]
cid=[c["criterion_id"] for c in cs]
assert len(ids)==len(set(ids))==10
assert len(matrix)==len(ids) and set(ids)=={m["entity_id"] for m in matrix}
assert len(set(s["source_id"] for s in sources))==len(sources)
assert len(cs)==6 and sum(float(c["weight"]) for c in cs)==100
assert len(evidence)==len(ids)*len(cs)
ev={(e["entity_id"],e["criterion_id"]):e for e in evidence}
assert len(ev)==len(evidence)
source_ids={s["source_id"] for s in sources}
for m in matrix:
    for c in cid:
        v=float(m[c]);assert 0<=v<=5
        x=ev[(m["entity_id"],c)]
        assert abs(float(x["score_value"])-v)<1e-9
        assert 0<=float(x["score_low"])<=v<=float(x["score_high"])<=5
        assert set(x["source_ids"].split("|")) <= source_ids
weights=[float(c["weight"]) for c in cs]
def score(m,ws):
    return sum(ws[j]*float(m[cid[j]])/5 for j in range(len(cs)))
baseline={m["entity_id"]:score(m,weights) for m in matrix}
rank=sorted(baseline,key=lambda x:(-baseline[x],x))
for a,b in zip(rank,expected["ranking"]):
    assert a==b["entity_id"] and abs(baseline[a]-b["score"])<1e-9
assert rank[0]==protocol["target_entity_id"] and baseline[rank[0]]>baseline[rank[1]]
seed=int(hashlib.sha256(f"{slug}|{ver}".encode()).hexdigest()[:8],16)
assert seed==protocol["sensitivity"]["seed"]
rng=random.Random(seed);wins=ties=0;mingap=100
for _ in range(1000):
    pert=[w*rng.uniform(0.7,1.3) for w in weights]
    norm=[100*w/sum(pert) for w in pert]
    actual={m["entity_id"]:score(m,norm) for m in matrix}
    high=max(actual.values())
    leaders=[e for e,s in actual.items() if abs(s-high)<=1e-9]
    wins+=leaders==[protocol["target_entity_id"]]
    ties+=len(leaders)>1
    mingap=min(mingap,actual[rank[0]]-max(s for e,s in actual.items() if e!=rank[0]))
lower=wilson(wins,1000)
s=expected["stability"]
assert wins==s["target_unique_wins"] and ties==s["top_ties"]
assert abs(mingap-s["min_target_margin"])<1e-8
assert abs(lower-s["wilson_lower_95"])<1e-10
assert wins>=730 and lower>0.70
manifest={}
for line in (P/"manifest.sha256").read_text(encoding="utf-8").splitlines():
    if not line.strip():continue
    sha,fn=line.split("  ",1)
    assert hashlib.sha256((P/fn).read_bytes()).hexdigest()==sha,(fn,"sha256 mismatch")
    manifest[fn]=sha
assert set(manifest)==set(f.name for f in P.iterdir() if f.is_file())-{"manifest.sha256"}
print(json.dumps({"status":"PASS","leader":rank[0],"score":baseline[rank[0]],"second_score":baseline[rank[1]],"wins":wins,"wilson":lower,"min_gap":mingap,"python":platform.python_version()},ensure_ascii=False))
