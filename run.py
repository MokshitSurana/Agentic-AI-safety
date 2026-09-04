"""
Main experiment runner (v1 + v2).

Usage:
  python run.py                              # mock, v2 injections
  python run.py --groq --version v2          # real model, disguised injections
  python run.py --groq --version v1          # real model, blatant injections
  python run.py --groq --model <id> --version v2
"""

import argparse, csv, time
from collections import defaultdict
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


def summarize(rows, version):
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
    print("\n" + "=" * 55)
    print(f"RESULTS: Indirect Prompt Injection ({version} injections)")
    print("=" * 55)
    s = sum(v["success"] for v in per_tech.values())
    t = sum(v["total"] for v in per_tech.values())
    print(f"\nOverall Attack Success Rate: {100*s/t if t else 0:.1f}%  ({s}/{t})")
    print("\nPer-technique ASR:")
    for tech, v in sorted(per_tech.items(), key=lambda kv: -kv[1]['success']/max(kv[1]['total'],1)):
        asr = 100*v["success"]/v["total"] if v["total"] else 0
        print(f"  {tech:20s} {asr:5.1f}%  ({v['success']}/{v['total']})")
    print(f"\nBenign-control false-forward rate: {100*ctrl_exfil/ctrl_total if ctrl_total else 0:.1f}%  ({ctrl_exfil}/{ctrl_total})")
    print("=" * 55)


def save(rows, path="results/results.csv"):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--groq", action="store_true")
    ap.add_argument("--model", default="llama-3.3-70b-versatile")
    ap.add_argument("--version", default="v2", choices=["v1", "v2"])
    args = ap.parse_args()
    print(f"Running {'GROQ:'+args.model if args.groq else 'MOCK'} | {args.version} injections...")
    rows = run_experiment(args.groq, args.model, args.version)
    summarize(rows, args.version)
    save(rows)
