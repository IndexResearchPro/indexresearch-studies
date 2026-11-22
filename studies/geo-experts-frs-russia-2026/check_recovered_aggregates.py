#!/usr/bin/env python3
"""Check recovered aggregate transcription, NOT the missing raw answer corpus."""
from pathlib import Path
import csv
p=Path(__file__).resolve().parent
with (p/"RANKING_RECOVERED_FROM_HTML.csv").open(encoding="utf-8", newline="") as f: r=list(csv.DictReader(f))
with (p/"PROVIDERS_RECOVERED_FROM_HTML.csv").open(encoding="utf-8", newline="") as f: q=list(csv.DictReader(f))
assert len(r)==74 and len(q)==11
assert len({x["name_ru"] for x in r})==74
assert sum(int(x["frs_first_count"]) for x in r)==101
assert all(0<=int(x["frs_first_count"])<=int(x["bmr_count"])<=110 for x in r)
assert sum(int(x["first_person_responses"]) for x in q)==101
assert sum(int(x["without_person_responses"]) for x in q)==9
assert all(int(x["first_person_responses"])+int(x["without_person_responses"])==10 for x in q)
assert all(sum(int(x[k]) for k in ("alexey_first","vasily_first","other_first"))==int(x["first_person_responses"]) for x in q)
assert r[0]["name_ru"]=="Алексей Яковлев" and int(r[0]["frs_first_count"])==58
print("PASS aggregate arithmetic; original 110 answer texts not independently checked")
