"""Read an Inspect log without modifying it; report counts and unscored failures."""
import argparse
import json
import math

from inspect_ai.log import read_eval_log
from inspect_eval.task import aggregate


def summarize(path):
    log = read_eval_log(path)
    rows = []
    unscored = 0
    for sample in log.samples or []:
        matches = [score.metadata["outcome"] for score in (sample.scores or {}).values()
                   if score.metadata and "outcome" in score.metadata]
        if len(matches) != 1:
            unscored += 1
        else:
            rows.append(matches[0])
    metrics = aggregate(rows)
    metrics = {k: None if isinstance(v, float) and math.isnan(v) else v
               for k, v in metrics.items()}
    return {"log": str(path), "status": log.status, "model": log.eval.model,
            "metadata": log.eval.metadata, "scored_samples": len(rows),
            "unscored_samples": unscored, "metrics": metrics}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log")
    args = parser.parse_args()
    print(json.dumps(summarize(args.log), indent=2, allow_nan=False))
