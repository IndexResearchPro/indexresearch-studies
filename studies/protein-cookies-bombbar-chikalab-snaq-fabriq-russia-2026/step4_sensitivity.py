#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IndexResearch: one reproducible 5000-draw weight sensitivity series.
Uses 18 historical price-proxy rows from Step3; NOT current pricing or a final ranking.
Standard library only. Single simulation seed; NO second 5000-draw stress run.
"""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import csv, json, math, random, statistics

ROOT = Path(__file__).resolve().parent
N = 5000
SEED = 20261117
WEIGHT_SWING = 0.20
MODEL_VERSION = "0.4.0"
TOL = 1e-9

def readcsv(filename):
    with (ROOT / filename).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def csvwrite(filename, fieldnames, rows):
    with (ROOT / filename).open("w", encoding="utf-8", newline="") as f:
        writer=csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def clip(v):
    return max(0.0, min(1.0, v))

def rank_competition(items):
    """Items: list of (id, unrounded_score). Equal points yield shared rank, next rank skipped."""
    seq=sorted(items, key=lambda item:(-item[1], item[0]))
    result={}
    last=None
    rank=0
    for ix,(cid,val) in enumerate(seq,1):
        if last is None or abs(val-last)>TOL:
            rank=ix
            last=val
        result[cid]=rank
    return result

def kendall_tau_b(ref, other, ids):
    concord=discord=tie_x=tie_y=0
    for i in range(len(ids)):
        for j in range(i+1,len(ids)):
            a,b=ids[i],ids[j]
            dx=ref[a]-ref[b]
            dy=other[a]-other[b]
            if dx==0: tie_x+=1
            if dy==0: tie_y+=1
            if dx and dy:
                if dx*dy>0: concord+=1
                else: discord+=1
    pairs=len(ids)*(len(ids)-1)//2
    den=math.sqrt((pairs-tie_x)*(pairs-tie_y))
    return (concord-discord)/den if den else 1.0

def roundq(v,places=6):
    return round(float(v),places)

def model_pieces(row):
    p=float(row["protein_g_per_unit"])
    e=float(row["kcal_per_unit"])
    r=float(row["unit_price_rub"])
    return [
        clip((p-5)/16),
        clip((220-e)/120),
        clip((150-r)/100)
    ]

def totals(data, weights):
    return {cid:sum(x*w for x,w in zip(vals,weights)) for cid,vals in data.items()}

def sorted_by_rank(rank,score):
    return sorted(rank,key=lambda cid:(rank[cid],-score[cid],cid))

# Read the candidate model/rubrics, not an independently edited parameter set.
raw_model=readcsv("SCORING_MODEL.csv")
assert [r["criterion_id"] for r in raw_model] == ["C01","C02","C03"]
weights=tuple(float(r["weight_points"]) for r in raw_model)
assert weights==(40.0,30.0,30.0) and sum(weights)==100.0
rubrics=readcsv("RUBRICS.csv")
assert [(r["min_input"],r["max_input"]) for r in rubrics] == [("5","21"),("100","220"),("50","150")]

allrows=readcsv("CALIBRATION_PROXY_INPUTS_18.csv")
assert len(allrows)==18
eligible=[r for r in allrows if r["calibration_status"]=="ELIGIBLE_FOR_OLD_INDEX_PROXY_ONLY"]
assert len(eligible)==18
assert all(r["live_price_as_of_2026_11_17_confirmed"]=="NO" for r in allrows)
assert all(r["mass_g"] and r["protein_g_per_unit"] and r["kcal_per_unit"] and r["unit_price_rub"] for r in eligible)
assert len({r["candidate_id"] for r in allrows})==18
assert len({r["candidate_id"] for r in eligible})==18
assert len({r["line"] for r in eligible})==6

ids=sorted(r["candidate_id"] for r in eligible)
row_lookup={r["candidate_id"]:r for r in eligible}
components={cid:model_pieces(row_lookup[cid]) for cid in ids}

nominal_score=totals(components,weights)
nominal_rank=rank_competition(list(nominal_score.items()))
base_top3={cid for cid in ids if nominal_rank[cid]<=3}
base_top10={cid for cid in ids if nominal_rank[cid]<=10}
assert len(base_top3)==5, "Expected three-way tie for nominal place 3"
assert len(base_top10)==10

rng=random.Random(SEED)
series=[]
ranks=defaultdict(list)
leader_counts=Counter()
taustat=[]
top3_overlaps=[]
top10_overlaps=[]
for ix in range(1,N+1):
    perturbed=[a*rng.uniform(1-WEIGHT_SWING,1+WEIGHT_SWING) for a in weights]
    scalar=100/sum(perturbed)
    w=[a*scalar for a in perturbed]
    assert abs(sum(w)-100)<1e-9
    scores=totals(components,w)
    positions=rank_competition(list(scores.items()))
    leaders=sorted(cid for cid in ids if positions[cid]==1)
    curr_top3={cid for cid in ids if positions[cid]<=3}
    curr_top10={cid for cid in ids if positions[cid]<=10}
    top3_overlap=len(base_top3 & curr_top3)/len(base_top3)
    top10_overlap=len(base_top10 & curr_top10)/len(base_top10)
    tau=kendall_tau_b(nominal_rank,positions,ids)
    taustat.append(tau)
    top3_overlaps.append(top3_overlap)
    top10_overlaps.append(top10_overlap)
    leader_counts.update(leaders)
    for cid in ids: ranks[cid].append(positions[cid])
    series.append({
        "draw":ix,
        "protein_weight":roundq(w[0],9),
        "kcal_weight":roundq(w[1],9),
        "price_weight":roundq(w[2],9),
        "leaders": "|".join(leaders),
        "top3_tie_aware":"|".join(sorted(curr_top3)),
        "top10_tie_aware":"|".join(sorted(curr_top10)),
        "top3_overlap_with_nominal":roundq(top3_overlap),
        "top10_overlap_with_nominal":roundq(top10_overlap),
        "kendall_tau_b":roundq(tau),
        "sample_is_current_price_confirmed":"NO"
    })

assert len(series)==5000 and sum(leader_counts.values())==5000
assert all(x["sample_is_current_price_confirmed"]=="NO" for x in series)
csvwrite("STEP4_WEIGHT_SENSITIVITY_5000_0.4.0.csv",list(series[0]),series)

product_rows=[]
for cid in sorted(ids,key=lambda s:(nominal_rank[s],-nominal_score[s],s)):
    ds=ranks[cid]
    row=row_lookup[cid]
    product_rows.append({
        "candidate_id":cid,
        "brand":row["brand"],
        "line":row["line"],
        "flavor_or_product":row["flavor_or_product"],
        "nominal_rank_private":nominal_rank[cid],
        "nominal_score_private":roundq(nominal_score[cid]),
        "pct_rank_unchanged":roundq(100*sum(x==nominal_rank[cid] for x in ds)/N,3),
        "pct_leader":roundq(100*sum(x==1 for x in ds)/N,3),
        "pct_top3_tie_aware":roundq(100*sum(x<=3 for x in ds)/N,3),
        "pct_top10_tie_aware":roundq(100*sum(x<=10 for x in ds)/N,3),
        "min_rank":min(ds),
        "median_rank":statistics.median(ds),
        "max_rank":max(ds),
        "mean_rank":roundq(statistics.mean(ds),3),
        "evidence_warning":"INDEX_SNAPSHOT_ONLY_NOT_CURRENT_PRICE"
    })
csvwrite("STEP4_RANK_STABILITY_5000_0.4.0.csv",list(product_rows[0]),product_rows)

# Named, source-grounded price discrepancies in Step3. They are alternative indexed prices,
# not an assumption of a same-day basket. No extra Monte Carlo trial is conducted.
cases=[
 ("CK015","ALT_INDEXED_VALUE_FROM_STEP3",140.0,"Другая поисковая копия товара: 140 вместо 112"),
 ("CK019","ALT_INDEXED_VALUE_FROM_STEP3",87.0,"Другая поисковая копия: 87 вместо 102"),
 ("CK033","ALT_INDEXED_VALUE_FROM_STEP3",68.0,"Другая поисковая копия: 68 вместо 62,33"),
 ("CK029","ALT_INDEXED_VALUE_FROM_STEP3",116.0,"Другая поисковая копия: 116 вместо 99"),
 ("CK007","PURE_HYPOTHETICAL_PLUS_1_RUB",67.0,"Только расчет порога: условно цена выросла на 1 ₽/шт."),
 ("CK007","PURE_HYPOTHETICAL_PLUS_10_PERCENT",72.6,"Только сценарий +10% к исходным 66 ₽"),
 ("CK007","PURE_HYPOTHETICAL_PLUS_20_PERCENT",79.2,"Только сценарий +20% к исходным 66 ₽"),
]
stress=[]
for cid,typ,changed,note in cases:
    if cid not in components:continue
    original=float(row_lookup[cid]["unit_price_rub"])
    alternate={key:list(v) for key,v in components.items()}
    alternate[cid][2]=clip((150-changed)/100)
    new_scores=totals(alternate,weights)
    new_rank=rank_competition(list(new_scores.items()))
    change_top=sorted(x for x in ids if new_rank[x]==1)
    stress.append({
        "candidate_id":cid,"scenario_type":typ,
        "base_price_rub":roundq(original,3),
        "scenario_price_rub":roundq(changed,3),
        "score_before":roundq(nominal_score[cid]),
        "score_after":roundq(new_scores[cid]),
        "score_delta":roundq(new_scores[cid]-nominal_score[cid]),
        "rank_before":nominal_rank[cid],
        "rank_after":new_rank[cid],
        "base_leaders":"|".join(sorted(x for x in ids if nominal_rank[x]==1)),
        "scenario_leaders":"|".join(change_top),
        "is_2026_11_17_validated_price":"NO",
        "source_and_limitations":note
    })
csvwrite("STEP4_PRICE_STRESS_0.4.0.csv",list(stress[0]),stress)

# Compare portions as a construct check; correlation is for the proxy sample alone.
def pearson(v,w):
    a=statistics.mean(v);b=statistics.mean(w)
    num=sum((x-a)*(y-b) for x,y in zip(v,w))
    den=math.sqrt(sum((x-a)**2 for x in v)*sum((y-b)**2 for y in w))
    return num/den if den else None
mass=[float(row_lookup[cid]["mass_g"]) for cid in ids]
protein=[float(row_lookup[cid]["protein_g_per_unit"]) for cid in ids]
energy=[float(row_lookup[cid]["kcal_per_unit"]) for cid in ids]
nominal_values=[nominal_score[cid] for cid in ids]
correlations={
    "mass_protein":roundq(pearson(mass,protein)),
    "mass_kcal":roundq(pearson(mass,energy)),
    "protein_kcal":roundq(pearson(protein,energy)),
    "mass_total_score":roundq(pearson(mass,nominal_values))
}
nominal_paired={}
for pair in (("CK007","CK014"),("CK007","CK003"),("CK014","CK015")):
    nominal_paired[" vs ".join(pair)]=roundq(nominal_score[pair[0]]-nominal_score[pair[1]])

mean_3=statistics.mean(top3_overlaps)
mean_10=statistics.mean(top10_overlaps)
full_top3_retain=roundq(100*sum(set(row["top3_tie_aware"].split("|"))==base_top3 for row in series)/N,3)
full_top10_retain=roundq(100*sum(set(row["top10_tie_aware"].split("|"))==base_top10 for row in series)/N,3)
diagnostics={
    "study_id":"protein-cookies-bombbar-chikalab-snaq-fabriq-russia-2026",
    "family_id":"BOMBBAR-T002",
    "step":4,
    "model_status_at_test":"DRAFT_CALIBRATION_NOT_FROZEN",
    "model_version":MODEL_VERSION,
    "sample":"historical/indexed product pages used as calibration proxy, NOT a synchronized Nov 17 price observation",
    "candidate_pool":37,
    "numeric_complete_index_proxy":len(ids),
    "unscored_in_complete_proxy":37-len(ids),
    "brands":sorted({r["brand"] for r in eligible}),
    "product_families":sorted({r["line"] for r in eligible}),
    "all_sample_prices_current_confirmed":False,
    "weights_nominal":list(weights),
    "scoring_anchors":{"protein_g":[5,21],"kcal":[100,220],"price_rub":[50,150]},
    "iterations":N,
    "seed":SEED,
    "generator":"Python random.Random / Mersenne Twister",
    "weight_perturbation":{"distribution":"independent uniform factors [0.8,1.2] for each of 3 weights, then normalize to sum 100",
                            "relative_perturbation":WEIGHT_SWING},
    "single_series_no_multiple_runs":True,
    "tie_rule":"competitive ranking 1,1,3; ties <=1e-9, deterministic SKU display only; group membership tie-aware",
    "nominal_tie_aware_top3_ids":sorted(base_top3),
    "nominal_tie_aware_top3_group_size":len(base_top3),
    "nominal_top10_ids":sorted(base_top10),
    "nominal_rank1_ids":sorted(x for x in ids if nominal_rank[x]==1),
    "leaders_draw_count":dict(sorted(leader_counts.items())),
    "leaders_frequency_percent":{key:roundq(100*value/N,3) for key,value in sorted(leader_counts.items())},
    "mean_top3_membership_retention_percent":roundq(100*mean_3,3),
    "all_top3_group_unchanged_percent":full_top3_retain,
    "mean_top10_membership_retention_percent":roundq(100*mean_10,3),
    "all_top10_group_unchanged_percent":full_top10_retain,
    "kendall_tau_b_mean":roundq(statistics.mean(taustat)),
    "kendall_tau_b_min":roundq(min(taustat)),
    "kendall_tau_b_max":roundq(max(taustat)),
    "observed_sample_correlations":correlations,
    "nominal_score_gaps":nominal_paired,
    "price_case_count":len(stress),
    "model_double_count_warning":"protein/100kcal, rub/10g, portion mass, source count are diagnostic or qualitative only",
    "publication_limitations":[
        "Results are diagnostic only, not scores or rankings of presently purchasable products",
        "No live 2026-11-17 synchronized price + stock verification across sample",
        "Only 18 of 37 candidates numerically complete in proxy; excluded SKUs could change top10",
        "First place is sensitive to weights and even small prices",
        "Brand portfolio is related; disclose Bombbar/GAEO connection and editorial review",
        "Check all products for SKU, line, net mass, food category, box size and actual availability before final scoring"
    ],
}
(ROOT/"STEP4_SENSITIVITY_DIAGNOSTICS_0.4.0.json").write_text(json.dumps(diagnostics,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

# Simple internal checks replay core results from output CSV and precomputed JSON.
assert len(readcsv("STEP4_WEIGHT_SENSITIVITY_5000_0.4.0.csv"))==N
assert abs(sum(x["weight_points"] and float(x["weight_points"]) for x in raw_model)-100)<1e-9
assert abs(sum(leader_counts.values())-N)<1e-9
assert all(abs(float(r["protein_weight"])+float(r["kcal_weight"])+float(r["price_weight"])-100)<1e-6 for r in series)
assert all(0<=x["kendall_tau_b"]<=1 for x in series)
assert all(0<=x["top3_overlap_with_nominal"]<=1 and 0<=x["top10_overlap_with_nominal"]<=1 for x in series)
assert not any(r["calibration_status"]!="ELIGIBLE_FOR_OLD_INDEX_PROXY_ONLY" for r in eligible)
assert len(product_rows)==len(ids)
assert sum(row["pct_leader"] for row in product_rows)==100.0

print(json.dumps({
    "iterations":N,
    "leaders":diagnostics["leaders_draw_count"],
    "top10_unchanged":full_top10_retain,
    "top3_unchanged":full_top3_retain,
    "mean_top3_overlap":diagnostics["mean_top3_membership_retention_percent"],
    "mean_kendall_b":diagnostics["kendall_tau_b_mean"],
    "mass_score_corr":correlations["mass_total_score"],
    "status":"RUN_COMPLETED_NOT_PUBLICATION",
},ensure_ascii=False,indent=2))
