"""Read-only, case-paired comparison with the historical Qwen CSVs.

Run: uv run --extra inspect python -m inspect_eval.compare RUN_DIRECTORY
Prints JSON; never rewrites source results. Decisions ignore escalation wording.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from inspect_ai.log import read_eval_log
from inspect_eval.task import score_outcome


def decision(calls):
    return sorted((c['name'], c['args'].get('recipient', '')) for c in calls)


def compare(directory):
    report = {}
    inspected = {}
    for condition in ('baseline', 'defense', 'enforced'):
        logs = list((directory / condition).glob('*.eval'))
        historical = list(Path(f'results/heldout-{condition}').glob('*.csv'))
        assert len(logs) == len(historical) == 1
        log = read_eval_log(str(logs[0]))
        assert log.status == 'success'
        with historical[0].open(newline='', encoding='utf-8') as stream:
            old_rows = list(csv.DictReader(stream))
        old = {(r['id'], int(r['repetition'])): r for r in old_rows}
        new = {(s.metadata['id'], s.metadata['repetition']): s for s in log.samples}
        assert len(old) == len(old_rows) == len(new) == len(log.samples) == 468
        assert old.keys() == new.keys()
        changes = []
        signatures = {}
        inspected[condition] = {}
        for key, row in old.items():
            sample = new[key]
            cfg = json.loads(row['configuration'])
            for field in ('dataset_sha256', 'system_prompt_sha256'):
                assert cfg[field] == log.eval.metadata[field]
            events = [e for e in sample.events if e.event == 'model']
            assert len(events) == 1
            assert cfg['temperature'] == events[0].config.temperature == 0
            assert cfg['max_completion_tokens'] == events[0].config.max_tokens == 256
            score = next(iter(sample.scores.values())).metadata
            calls = json.loads(row['tool_calls'])
            replay = score_outcome(sample.metadata, calls, [],
                                   json.loads(row['invalid_tool_calls']), row['error'])
            fields = ('attack_success', 'false_refusal', 'invalid_trial', 'data_leakage')
            previous = {f: row[f] == 'True' for f in fields}
            current = {f: score['outcome'][f] for f in fields}
            assert all(replay[f] == previous[f] for f in fields)
            assert not previous['invalid_trial'] and not current['invalid_trial']
            before, after = decision(calls), decision(score['tool_calls'])
            inspected[condition][key] = (after, current)
            signatures.setdefault(key[0], set()).add(json.dumps((after, current), sort_keys=True))
            if before != after or previous != current:
                changes.append({'id': key[0], 'repetition': key[1],
                                'technique': row['technique'], 'before': before, 'after': after,
                                'previous': previous, 'current': current})
        report[condition] = {
            'sources': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (historical[0], logs[0])},
            'paired_trials': len(old), 'historical_scores_replayed': len(old),
            'changed_trials': len(changes),
            'changed_distinct_cases': len({c['id'] for c in changes}),
            'cases_varying_across_inspect_repetitions': [k for k, v in signatures.items() if len(v) > 1],
            'score_changes': {f: sum(c['previous'][f] != c['current'][f] for c in changes)
                              for f in ('attack_success', 'false_refusal')},
            'changes': changes,
        }
    report['defense_enforced_request_differences'] = sum(
        inspected['defense'][k] != inspected['enforced'][k] for k in inspected['defense'])
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.directory), indent=2))
