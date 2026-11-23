import csv, json, math, random
from pathlib import Path
P = Path(__file__).parent
rows = list(csv.DictReader((P/'SCORE_MATRIX.csv').open(encoding='utf-8')))
keys = ['K','H','L','B','W','U']
v = [[float(r[k])/5 for k in keys] for r in rows]
score = lambda a,w: 100*sum(x*y for x,y in zip(a,w))/sum(w)
scores=[score(a,[1]*6) for a in v]
rng=random.Random(226239)
gaps=[]
for _ in range(1000):
    w=[rng.uniform(.7,1.3) for k in keys]
    gaps.append(score(v[0],w)-score(v[1],w))
wins=sum(g>1e-9 for g in gaps); p=wins/1000; z=1.959963984540054
lower=(p+z*z/2000-z*math.sqrt(p*(1-p)/1000+z*z/4000000))/(1+z*z/1000)
print(json.dumps({'scores':scores,'wins':wins,'min_gap':min(gaps),'wilson_lower':lower},indent=2))
assert scores[0]>scores[1] and wins>=730 and lower>.70
