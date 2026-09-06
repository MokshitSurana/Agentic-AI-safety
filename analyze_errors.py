"""Reproduce distinct-case failure analysis after analyze_heldout.py passes."""
import csv
import json
from collections import Counter
from pathlib import Path
from documents import build_dataset

ROOT = Path(__file__).resolve().parent


def main():
    cases = {r['id']: r for r in build_dataset('heldout-v1')}
    runs = {}
    for model, prefix in [('Qwen', ''), ('Llama', 'llama-')]:
        for condition in ('baseline', 'defense'):
            paths = list((ROOT / 'results' / f'{prefix}heldout-{condition}').glob('*.csv'))
            assert len(paths) == 1
            with paths[0].open(newline='', encoding='utf-8') as f:
                raw = list(csv.DictReader(f))
            grouped = {}
            for r in raw:
                grouped.setdefault(r['id'], []).append(r)
            assert len(grouped) == 156
            for group in grouped.values():
                assert len(group) == 3
                assert len({(r['action'], r['recipient'], r['attack_success'], r['false_refusal']) for r in group}) == 1
            runs[model, condition] = {cid: group[0] for cid, group in grouped.items()}
    common = [cid for cid, c in cases.items() if c['is_attack'] and
              all(runs[m, 'defense'][cid]['attack_success'] == 'True' for m in ('Qwen', 'Llama'))]
    counts = Counter(cases[cid]['technique'] for cid in common)
    output = {'shared_defense_failures': len(common), 'shared_by_family': dict(sorted(counts.items())),
              'shared_ids': sorted(common), 'models': {}}
    casebook = []
    for model in ('Qwen', 'Llama'):
        b, d = runs[model, 'baseline'], runs[model, 'defense']
        regressions = [cid for cid in b if b[cid]['attack_success'] == 'False' and d[cid]['attack_success'] == 'True']
        failed = {condition: {cid for cid, r in runs[model, condition].items() if r['false_refusal'] == 'True'}
                  for condition in ('baseline', 'defense')}
        breakdown = {}
        for condition in ('baseline', 'defense'):
            for kind in ('direct', 'matched'):
                subset = [cid for cid, c in cases.items() if c['control_type'] == 'legitimate_forward'
                          and bool(c['template_id']) == (kind == 'matched')]
                breakdown[f'{condition}_{kind}'] = {'failed': len(set(subset) & failed[condition]), 'total': len(subset)}
        output['models'][model] = {'attack_regressions': sorted(regressions), 'control_breakdown': breakdown,
                                  'controls_fixed': sorted(failed['baseline'] - failed['defense']),
                                  'controls_worsened': sorted(failed['defense'] - failed['baseline']),
                                  'controls_still_failed': sorted(failed['defense'] & failed['baseline'])}
        for cid in sorted(set(regressions) | set(common) | failed['baseline'] | failed['defense']):
            casebook.append({'model': model, 'id': cid, 'family': cases[cid]['technique'],
                             'document': cases[cid]['document'], 'expected_recipient': cases[cid]['expected_recipient'],
                             'shared_attack_failure': cid in common, 'attack_regression': cid in regressions,
                             'baseline_calls': b[cid]['tool_calls'], 'defense_calls': d[cid]['tool_calls']})
    out = ROOT / 'analysis'
    (out / 'error-analysis-counts.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    with (out / 'error-casebook.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(casebook[0]))
        writer.writeheader()
        writer.writerows(casebook)
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
