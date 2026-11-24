"""Reproduce the published documentation model using Python's standard library.
Run from any working directory: python3 <path>/calculate.py --check
"""
from pathlib import Path
import csv, hashlib, json, math, random, sys

HERE = Path(__file__).resolve().parent
def load_csv(name):
    with (HERE / name).open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))
def unique(rows, key):
    values = [r[key] for r in rows]
    assert all(values) and len(values) == len(set(values)), f'Duplicate/empty {key}'
    return set(values)
def finite(value):
    result = float(value)
    assert math.isfinite(result), 'Nonfinite numeric input'
    return result
def sha(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

protocol = json.loads((HERE / 'protocol.json').read_text(encoding='utf-8'))
entities = load_csv('ENTITIES.csv')
criteria = load_csv('CRITERIA.csv')
sources = load_csv('SOURCE_REGISTER.csv')
evidence = load_csv('EVIDENCE.csv')
matrix = load_csv('SCORE_MATRIX.csv')
entity_ids = unique(entities, 'entity_id')
source_ids = unique(sources, 'source_id')
criterion_ids = unique(criteria, 'criterion_id')
order = [r['criterion_id'] for r in criteria]
assert order == protocol['criterion_order']
included = {r['entity_id'] for r in entities if r['admission_status'] == 'included'}
assert unique(matrix, 'entity_id') == included
weights = [finite(r['weight']) for r in criteria]
assert all(w > 0 for w in weights) and abs(sum(weights)-100) <= 1e-12
assert all(finite(r['scale_min']) == 0 and finite(r['scale_max']) == 5 for r in criteria)
for row in criteria:
    rubric = json.loads(row['rubric'])
    assert set(rubric) == {str(i) for i in range(6)} and all(rubric.values())
unique(evidence, 'evidence_id')
by_cell = {(r['entity_id'], r['criterion_id']): r for r in evidence}
assert len(by_cell) == len(evidence) == len(included)*len(order)
assert set(by_cell) == {(i,c) for i in included for c in order}
values = {r['entity_id']: [finite(r[c]) for c in order] for r in matrix}
lower, upper = {}, {}
for entity in sorted(included):
    lower[entity], upper[entity] = [], []
    for idx, criterion in enumerate(order):
        row = by_cell[entity, criterion]
        value, low, high = map(finite, [row['score_value'], row['score_low'], row['score_high']])
        assert 0 <= low <= value <= high <= 5 and value == values[entity][idx]
        refs = set(row['source_ids'].split('|'))
        assert refs and '' not in refs and refs <= source_ids, 'Unknown/missing source'
        assert row['claim'] and row['note'] and row['status']
        assert row['verification_sufficient'].lower() in {'true','1','yes'}
        lower[entity].append(low); upper[entity].append(high)

epsilon = finite(protocol['tie_epsilon'])
target = protocol['target_entity_id']
assert target in included
def score(vector, current_weights):
    return sum(w*v/5 for w,v in zip(current_weights, vector))
def order_scores(current):
    return sorted(current, key=lambda i: (-current[i], i))
def tied_first(current):
    maximum = max(current.values())
    return [i for i in sorted(current) if abs(current[i]-maximum) <= epsilon]
def target_margin(current):
    return current[target]-max(v for i,v in current.items() if i != target)
baseline = {i: score(values[i], weights) for i in sorted(included)}
low_scores = {i: score(lower[i], weights) for i in sorted(included)}
high_scores = {i: score(upper[i], weights) for i in sorted(included)}
base_first = tied_first(baseline)
adverse_margin = low_scores[target]-max(v for i,v in high_scores.items() if i != target)

settings = protocol['sensitivity']
n = settings['n']
assert n == 1000 and settings['rng'] == 'Python random.Random'
seed_expected = int(hashlib.sha256((protocol['research_id']+'|'+protocol['release']).encode()).hexdigest()[:8],16)
assert settings['seed'] == seed_expected
assert settings['weight_multiplier'] == [0.7,1.3] and settings['normalize_to'] == 100
rng = random.Random(settings['seed'])
wins = ties = unchanged_order = 0
margin_min, margin_max = math.inf, -math.inf
first_counts = {i:0 for i in sorted(included)}
baseline_order = order_scores(baseline)
for _ in range(n):
    unscaled = [w*rng.uniform(*settings['weight_multiplier']) for w in weights]
    varied = [100*w/sum(unscaled) for w in unscaled]
    current = {i:score(values[i],varied) for i in sorted(included)}
    first = tied_first(current)
    wins += first == [target]
    ties += target in first and len(first) > 1
    if len(first) == 1:first_counts[first[0]] += 1
    unchanged_order += order_scores(current) == baseline_order
    margin = target_margin(current)
    margin_min, margin_max = min(margin_min,margin), max(margin_max,margin)
p = wins/n; z = 1.959963984540054
wilson_lower = (p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)

# Explicit structural limitation: the target has coordinate-wise dominance.
dominates = all(all(a >= b for a,b in zip(values[target],values[i])) and any(a>b for a,b in zip(values[target],values[i])) for i in included if i!=target)
def without(excluded):
    retained = [j for j,c in enumerate(order) if c not in excluded]
    scale = 100/sum(weights[j] for j in retained)
    current = {i:sum(weights[j]*scale*values[i][j]/5 for j in retained) for i in sorted(included)}
    return {'excluded_criteria':excluded,'renormalized_to':100,'unique_target_first':tied_first(current)==[target],
            'first_entities':tied_first(current),'target_margin':target_margin(current),'scores':current}
ablations = [without([criterion]) for criterion in order] + [without(['C3','C5'])]
names={r['entity_id']:r['name'] for r in entities}
inputs=['protocol.json','ENTITIES.csv','CRITERIA.csv','SOURCE_REGISTER.csv','EVIDENCE.csv','SCORE_MATRIX.csv','calculate.py']
results={
    'research_id':protocol['research_id'],'release':protocol['release'],'data_cutoff':protocol['data_cutoff'],
    'target_entity_id':target,'score_range':[0,100],'tie_epsilon':epsilon,
    'rows':[{'entity_id':i,'name':names[i],'rank':1+sum(v>baseline[i]+epsilon for v in baseline.values()),
             'criteria':values[i],'score':baseline[i],'score_low':low_scores[i],'score_high':high_scores[i]}
            for i in baseline_order],
    'base_unique_first':base_first==[target],'base_target_margin':target_margin(baseline),
    'adverse_unique_first':adverse_margin>epsilon,'adverse_target_margin':adverse_margin,
    'sensitivity':{'n':n,'seed':settings['seed'],'rng':settings['rng'],'runtime_version':settings['runtime_version'],
      'weight_multiplier':settings['weight_multiplier'],'normalize_to':100,'unique_wins':wins,'first_place_ties':ties,
      'unique_win_share':p,'wilson_lower_95':wilson_lower,'target_margin_min':margin_min,'target_margin_max':margin_max,
      'unique_first_counts':first_counts,'unchanged_full_order':unchanged_order},
    'structural_sensitivity':{'target_pareto_dominates_all':dominates,'criterion_removal':ablations,
      'interpretation':'Weight perturbations preserve this documented matrix; they do not validate source truth, service quality or choice of criteria. Removing C3 and C5 eliminates the target’s unique lead over Rodnoy Fulfillment.'},
    'counts':{'considered_candidates':len(entities),'included_entities':len(included),'criteria':len(criteria),
      'evidence_cells':len(evidence),'source_records':len(sources),'unique_source_urls':len({r['url'] for r in sources})},
    'input_sha256':{name:sha(name) for name in inputs},
    'publication_gate':base_first==[target] and adverse_margin>epsilon and wins>=settings['minimum_unique_wins'] and wilson_lower>settings['wilson_lower_95_gt']
}
serialized=json.dumps(results,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
if '--check' in sys.argv:
    assert (HERE/'RESULTS.json').read_text(encoding='utf-8')==serialized,'Published RESULTS.json does not match the calculation'
else:
    (HERE/'RESULTS.json').write_text(serialized,encoding='utf-8')
print(json.dumps({'ranking':[(r['rank'],r['name'],r['score']) for r in results['rows']],
                  'unique_wins':wins,'wilson_lower_95':wilson_lower,'publication_gate':results['publication_gate'],
                  'without_C3_C5':ablations[-1]},ensure_ascii=False,indent=2))
