#!/usr/bin/env python3
"""Reproduce the finite-corpus disclosure study using only this release.

Run from any directory. --write materializes deterministic derived files;
without it, every derived file is compared byte-for-byte with a fresh run.
No network, API, private repository or third-party library is used.
"""
from __future__ import annotations
import csv, hashlib, io, json, math, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parent
EPSILON = 1e-9
PROTOCOL_BLOB = "a16879667d4e6e3ab4b23820e422da9c67a93a67"

def canonical(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"

def csv_text(fields, rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()

def main():
    raw = (ROOT / "protocol.json").read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert git_blob == PROTOCOL_BLOB, "Frozen protocol bytes changed"
    protocol = json.loads(raw)
    input_data = json.loads((ROOT / "observations.json").read_text())
    criteria = protocol["criteria"]
    corpus = protocol["corpus"]["cases"]
    observations = input_data["cases"]
    criteria_ids = [x["id"] for x in criteria]
    weights = [x["weight"] for x in criteria]
    assert len(criteria_ids) == len(set(criteria_ids)) == 5
    assert weights == [20] * 5 and sum(weights) == 100
    assert all(len(c["items"]) == 5 for c in criteria)
    ids = [c["case_id"] for c in corpus]
    assert len(ids) == len(set(ids)) == 13
    assert {c["case_id"] for c in observations} == set(ids)
    assert len(observations) == 13
    obs = {c["case_id"]: c for c in observations}
    sources, evidence, atomic, matrix, entities, numeric = [], [], [], [], [], []
    unknown_count = 0
    for index, case in enumerate(corpus, 1):
        o = obs[case["case_id"]]
        assert len(o["bits"]) == len(o["notes"]) == 5
        assert all(len(b) == 5 and set(b) <= set("01?") for b in o["bits"])
        assert o["ref"] and o["range"] and all(o["notes"])
        source_id = f"S{index:03d}"
        sources.append(dict(source_id=source_id, url=case["url"], title=case["brand"], publisher=case["agency"], checked_at=input_data["recorded_at"], source_date="Publication date not consistently stated; project dates are not assumed to be publication dates", source_type="primary self-authored agency case", access_status="readable case text; images excluded", locator=o["range"], retrieval_ref=o["ref"]))
        entities.append(dict(entity_id=case["case_id"], name=case["agency"] + " / " + case["brand"], unit="one frozen case page", admission_status="included", inclusion_reason="Explicitly frozen finite corpus, not a market sample", exclusion_reason=""))
        low, high = [], []
        row = {"entity_id": case["case_id"]}
        for c, bits, note in zip(criteria, o["bits"], o["notes"]):
            lo = bits.count("1")
            hi = lo + bits.count("?")
            low.append(lo)
            high.append(hi)
            row[c["id"]] = lo
            assert 0 <= lo <= hi <= 5
            unknown_count += bits.count("?")
            evidence.append(dict(evidence_id=case["case_id"] + "_" + c["id"], entity_id=case["case_id"], criterion_id=c["id"], claim=note, source_ids=source_id, status="partial_unknown" if hi != lo else "observed_disclosure", raw_value=bits, score_value=lo, score_low=lo, score_high=hi, verification_sufficient="yes_for_textual_disclosure_only", note="1=explicit; 0=not found in the complete readable case text; ?=interpretive uncertainty. Does not measure actual capability. Locator: " + o["range"]))
            for (item_id, definition), bit in zip(c["items"], bits):
                atomic.append(dict(entity_id=case["case_id"], criterion_id=c["id"], item_id=item_id, status={"1":"explicit","0":"not_found_in_readable_case","?":"unknown"}[bit], score_low=int(bit == "1"), score_high=int(bit != "0"), source_id=source_id, evidence_id=case["case_id"] + "_" + c["id"], locator=o["range"]))
        matrix.append(row)
        numeric.append(dict(case_id=case["case_id"], agency=case["agency"], brand=case["brand"], low=low, high=high))
    assert len(evidence) == 65 and len(atomic) == 325 and unknown_count == 6
    assert sum(e["score_low"] != e["score_high"] for e in evidence) == 5
    assert len({(e["entity_id"],e["criterion_id"]) for e in evidence}) == 65
    assert all(e["source_ids"] in {s["source_id"] for s in sources} for e in evidence)
    assert all(e["score_value"] == next(r[e["criterion_id"]] for r in matrix if r["entity_id"] == e["entity_id"]) for e in evidence)
    for index, outside in enumerate(protocol["corpus"]["outside_candidates"],1):
        entities.append(dict(entity_id=f"OUTSIDE_{index}", name=outside["agency"], unit="agency candidate outside this fixed case corpus", admission_status="outside_fixed_corpus", inclusion_reason="", exclusion_reason=outside["reason"]))
    agencies = sorted({c["agency"] for c in numeric})
    assert len(agencies) == 7 and "Heads" in agencies

    def score(values, w):
        s = sum(a * b / 5 for a, b in zip(values, w))
        assert math.isfinite(s)
        return s

    def agency_scores(w, bound):
        values = {}
        for agency in agencies:
            options = [(score(c[bound], w), c["case_id"]) for c in numeric if c["agency"] == agency]
            options.sort(key=lambda p: (-p[0], p[1]))
            values[agency] = options[0]
        return values

    base = agency_scores(weights, "low")
    upper = agency_scores(weights, "high")
    target = protocol["target"]
    base_margin = base[target][0] - max(v[0] for a,v in base.items() if a != target)
    adverse_margin = base[target][0] - max(v[0] for a,v in upper.items() if a != target)
    seed_text = protocol["stability"]["seed_text"]
    seed_hex = hashlib.sha256(seed_text.encode()).hexdigest()
    seed = int(seed_hex[:16],16)
    rng = random.Random(seed)
    trials = []
    wins = 0
    minimum_margin = float("inf")
    for trial_id in range(1,1001):
        raw_weights = [w * rng.uniform(0.7,1.3) for w in weights]
        w = [100 * x / sum(raw_weights) for x in raw_weights]
        lower_trial = agency_scores(w,"low")
        upper_trial = agency_scores(w,"high")
        rival, rival_row = max(((a,v) for a,v in upper_trial.items() if a != target), key=lambda pair: pair[1][0])
        margin = lower_trial[target][0] - rival_row[0]
        unique = margin > EPSILON
        wins += unique
        minimum_margin = min(minimum_margin,margin)
        trials.append(dict(trial=trial_id, **{cid:format(x,".15g") for cid,x in zip(criteria_ids,w)}, target_lower=format(lower_trial[target][0],".15g"), rival_upper=format(rival_row[0],".15g"), rival=rival, target_case=lower_trial[target][1], rival_case=rival_row[1], margin=format(margin,".15g"), unique_win=int(unique)))
    z = 1.959963984540054
    p = wins / 1000
    wilson = (p + z*z/2000 - z*math.sqrt(p*(1-p)/1000+z*z/(4*1000*1000))) / (1+z*z/1000)
    ranked = []
    for agency in sorted(agencies,key=lambda a:(-base[a][0],a)):
        entity_id = "clever-branding" if agency == "Clёver Branding" else agency.lower()
        ranked.append(dict(entity_id=entity_id,agency=agency,rank=1+sum(v[0] > base[agency][0]+EPSILON for v in base.values()),score=base[agency][0],score_low=base[agency][0],score_high=upper[agency][0],best_base_case=base[agency][1],best_upper_case=upper[agency][1],case_count=sum(c["agency"]==agency for c in numeric)))
    case_results = [dict(case_id=c["case_id"],agency=c["agency"],brand=c["brand"],criteria_low=c["low"],criteria_high=c["high"],score=score(c["low"],weights),score_low=score(c["low"],weights),score_high=score(c["high"],weights)) for c in numeric]
    case_results.sort(key=lambda c:(-c["score"],c["case_id"]))
    for c in case_results:
        c["rank"] = 1+sum(other["score"] > c["score"]+EPSILON for other in case_results)
    accepted = base_margin > EPSILON and adverse_margin > EPSILON and wins >=730 and wilson > 0.7
    result = dict(research_id=protocol["research_id"],version=protocol["version"],protocol_sha256=hashlib.sha256(raw).hexdigest(),protocol_git_blob=git_blob,scope="13 fixed readable case pages, seven agencies, textual disclosure only",target=target,criteria_order=criteria_ids,weights=weights,aggregation="best whole case per agency; reselected in each trial; no cross-case cell mixing",tie_epsilon=EPSILON,missing_policy="lower bound for all; target lower versus each rival upper",unknown_atomic_items=unknown_count,base_unique_first=base_margin>EPSILON,adverse_unique_first=adverse_margin>EPSILON,base_margin=base_margin,adverse_margin=adverse_margin,agencies=ranked,cases=case_results,stability=dict(N=1000,k=wins,unique_win_rate=p,wilson_lower_95=wilson,seed=seed,seed_text=seed_text,seed_sha256=seed_hex,rng="Python random.Random",multiplier=[0.7,1.3],normalize_to=100,minimum_adverse_margin=minimum_margin),calculation_status="ACCEPTED_FINITE_CORPUS_CALCULATION" if accepted else "NOT_ACCEPTED",public_release_status="not_asserted_by_calculator",limitations=["No independent second coder.","Agency-authored text, not verified commercial effectiveness.","Purposive finite corpus selected after exploratory reading.","Unequal number of case pages per agency; best-case result is an opportunity measure within this corpus only.","Images and unlisted pages are not measured.","A zero is missing textual explanation, not missing agency capability.","Lower positions with overlapping intervals are not a definitive quality ordering."])
    outputs = {
        "ENTITIES.csv":csv_text(["entity_id","name","unit","admission_status","inclusion_reason","exclusion_reason"],entities),
        "CRITERIA.csv":csv_text(["criterion_id","name","weight","scale_min","scale_max","rubric","question_link"],[dict(criterion_id=c["id"],name=c["label"],weight=c["weight"],scale_min=0,scale_max=5,rubric=" | ".join(i+": "+d for i,d in c["items"]),question_link=protocol["question"]) for c in criteria]),
        "SOURCE_REGISTER.csv":csv_text(list(sources[0]),sources),
        "EVIDENCE.csv":csv_text(list(evidence[0]),evidence),
        "OBSERVATIONS.csv":csv_text(list(atomic[0]),atomic),
        "SCORE_MATRIX.csv":csv_text(["entity_id"]+criteria_ids,matrix),
        "RESULTS.json":canonical(result),
        "TRIALS.csv":csv_text(list(trials[0]),trials),
        "AGENCY_RESULTS.csv":csv_text(list(ranked[0]),ranked),
        "AGENCY_SCORE_MATRIX.csv":csv_text(["entity_id","agency","best_base_case"]+criteria_ids,[dict(entity_id=a["entity_id"],agency=a["agency"],best_base_case=a["best_base_case"],**{cid:value for cid,value in zip(criteria_ids,next(c["low"] for c in numeric if c["case_id"]==a["best_base_case"]))}) for a in ranked]),
    }
    write = "--write" in sys.argv
    for name,text in outputs.items():
        path=ROOT/name
        data=text.encode("utf-8")
        if write:
            path.write_bytes(data)
        else:
            assert path.read_bytes() == data, "Reproduction mismatch: "+name
    print(canonical({"status":result["calculation_status"],"mode":"write" if write else "verified_exact_reproduction","agencies":ranked,"base_margin":base_margin,"adverse_margin":adverse_margin,"stability":result["stability"],"unknown_atomic_items":unknown_count,"derived_files":len(outputs)}))

if __name__ == "__main__":
    main()
