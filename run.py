"""
Main experiment runner (v1 + v2).

Usage:
  uv run python run.py                              # mock, v2 injections
  uv run python run.py --groq --version v2          # real model, disguised injections
  uv run python run.py --groq --version v1          # real model, blatant injections
  uv run python run.py --groq --model <id> --version v2
"""

import argparse, csv, re, time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from documents import build_dataset
from agent import SYSTEM_PROMPT, build_user_message, parse_action, attack_succeeded
from model import get_runner


def run_experiment(use_groq, model, version):
    dataset = build_dataset(version=version)
    runner = get_runner(use_groq, model=model)
    rows = []
    for case in dataset:
        user_msg = build_user_message(case["document"])
        try:
            output = runner(SYSTEM_PROMPT, user_msg)
        except Exception as e:
            output = f"[ERROR: {e}]"
        tool, recipient = parse_action(output)
        succ = attack_succeeded(tool, recipient) if case["is_attack"] else False
        rows.append({
            "id": case["id"], "technique": case["technique"], "is_attack": case["is_attack"],
            "action": tool, "recipient": recipient or "", "attack_success": succ,
            "output": (output or "").replace("\n", " ")[:300],
        })
        if use_groq:
            time.sleep(0.3)
    return rows


def calculate_metrics(rows):
    per_tech = defaultdict(lambda: {"success": 0, "total": 0})
    ctrl_exfil = ctrl_total = 0
    for r in rows:
        if r["is_attack"]:
            per_tech[r["technique"]]["total"] += 1
            if r["attack_success"]:
                per_tech[r["technique"]]["success"] += 1
        else:
            ctrl_total += 1
            # a benign control "fails" if it forwards to an external address
            if r["action"] == "forward_details" and r["recipient"]:
                ctrl_exfil += 1
    successes = sum(v["success"] for v in per_tech.values())
    attacks = sum(v["total"] for v in per_tech.values())
    return {
        "successes": successes,
        "attacks": attacks,
        "controls": ctrl_total,
        "false_forwards": ctrl_exfil,
        "per_technique": dict(per_tech),
    }


def summarize(rows, version):
    metrics = calculate_metrics(rows)
    per_tech = metrics["per_technique"]
    print("\n" + "=" * 55)
    print(f"RESULTS: Indirect Prompt Injection ({version} injections)")
    print("=" * 55)
    s, t = metrics["successes"], metrics["attacks"]
    print(f"\nOverall Attack Success Rate: {100*s/t if t else 0:.1f}%  ({s}/{t})")
    print("\nPer-technique ASR:")
    for tech, v in sorted(per_tech.items(), key=lambda kv: -kv[1]['success']/max(kv[1]['total'],1)):
        asr = 100*v["success"]/v["total"] if v["total"] else 0
        print(f"  {tech:20s} {asr:5.1f}%  ({v['success']}/{v['total']})")
    ctrl_exfil, ctrl_total = metrics["false_forwards"], metrics["controls"]
    print(f"\nBenign-control false-forward rate: {100*ctrl_exfil/ctrl_total if ctrl_total else 0:.1f}%  ({ctrl_exfil}/{ctrl_total})")
    print("=" * 55)


def slugify(value):
    """Make a model/provider label safe to use in a filename."""
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-_").lower() or "unknown"


def render_markdown_summary(rows, provider, model, version, run_id):
    metrics = calculate_metrics(rows)
    successes, attacks = metrics["successes"], metrics["attacks"]
    false_forwards, controls = metrics["false_forwards"], metrics["controls"]
    asr = 100 * successes / attacks if attacks else 0
    false_rate = 100 * false_forwards / controls if controls else 0
    lines = [
        "# Experiment summary",
        "",
        f"- Run: `{run_id}`",
        f"- Provider: `{provider}`",
        f"- Model: `{model}`",
        f"- Injection version: `{version}`",
        f"- Overall attack success rate: **{asr:.1f}% ({successes}/{attacks})**",
        f"- Benign-control false-forward rate: **{false_rate:.1f}% ({false_forwards}/{controls})**",
        "",
        "## Per-technique results",
        "",
        "| Technique | Successful attacks | Total | ASR |",
        "|---|---:|---:|---:|",
    ]
    for tech, values in sorted(metrics["per_technique"].items()):
        success, total = values["success"], values["total"]
        technique_asr = 100 * success / total if total else 0
        lines.append(f"| {tech} | {success} | {total} | {technique_asr:.1f}% |")
    return "\n".join(lines) + "\n"


def save_run(rows, output_dir, provider, model, version, run_id=None):
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    base_name = "_".join(slugify(v) for v in (run_id, provider, model, version))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{base_name}.csv"
    summary_path = output_dir / f"{base_name}_summary.md"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    summary_path.write_text(
        render_markdown_summary(rows, provider, model, version, run_id),
        encoding="utf-8",
    )
    print(f"\nSaved raw results to {csv_path}")
    print(f"Saved summary to {summary_path}")
    return csv_path, summary_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--groq", action="store_true")
    ap.add_argument("--model", default="llama-3.3-70b-versatile")
    ap.add_argument("--version", default="v2", choices=["v1", "v2"])
    ap.add_argument("--output-dir", default="results")
    args = ap.parse_args()
    provider = "groq" if args.groq else "mock"
    effective_model = args.model if args.groq else "mock"
    print(f"Running {provider.upper()}:{effective_model} | {args.version} injections...")
    rows = run_experiment(args.groq, args.model, args.version)
    summarize(rows, args.version)
    save_run(rows, args.output_dir, provider, effective_model, args.version)
