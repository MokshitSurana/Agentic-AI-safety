"""Run three sequential conditions on one server, retaining all native Inspect logs."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from inspect_ai import eval
from inspect_eval.task import transfer
from inspect_eval.summarize import summarize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="vllm/Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--output-dir", default="results/inspect/validation")
    args = parser.parse_args()
    root = Path(args.output_dir) / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    root.mkdir(parents=True)
    summaries = []
    for condition, prompt, enforce in (("baseline", "baseline", False),
                                       ("defense", "defense", False),
                                       ("enforced", "defense", True)):
        print(f"Starting {condition}: {156 * args.repetitions} samples", flush=True)
        logs = eval(transfer(prompt=prompt, enforce_recipients=enforce,
                             repetitions=args.repetitions), model=args.model,
                    model_base_url=args.base_url, max_samples=1,
                    log_dir=str(root / condition), display="plain")
        summary = summarize(logs[0].location)
        summaries.append({"condition": condition, **summary})
        (root / "summary.json").write_text(json.dumps(summaries, indent=2, allow_nan=False),
                                           encoding="utf-8")
        print(json.dumps(summaries[-1], indent=2), flush=True)
        if summary["status"] != "success" or summary["unscored_samples"]:
            raise RuntimeError(f"Incomplete {condition} run; inspect logs before continuing")
        if summary["metrics"]["invalid_trials"]:
            raise RuntimeError(f"Invalid trials in {condition}; inspect logs before continuing")
    print(f"Validation saved to {root}", flush=True)


if __name__ == "__main__":
    main()
