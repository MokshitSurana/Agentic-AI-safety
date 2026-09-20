"""Render the post's single figure from the audited Markdown result table."""
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
rows = {}
for line in (ROOT / "report.md").read_text(encoding="utf-8").splitlines():
    if not line.startswith("| "):
        continue
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    if cells[0] in ("Qwen/Qwen2.5-7B-Instruct", "meta-llama/Llama-3.1-8B-Instruct"):
        rows[(cells[0], cells[1])] = cells

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
fig, ax = plt.subplots(figsize=(10.8, 6.4), facecolor="white")
colors = ("#52657B", "#D97706", "#087F8C")
labels = ("Baseline: requested", "Stronger prompt: requested", "Stronger prompt + guard: allowed")
for model, top in (("Qwen/Qwen2.5-7B-Instruct", 5), ("meta-llama/Llama-3.1-8B-Instruct", 1)):
    for index, condition in enumerate(("baseline", "defense", "enforced")):
        cells = rows[(model, condition)]
        attempted, total = map(int, re.match(r"(\d+)/(\d+)", cells[2]).groups())
        count = attempted if condition != "enforced" else int(cells[4])
        rate = 100*count/total
        y = top-index
        ax.barh(y, rate, height=.62, color=colors[index], label=labels[index] if top == 5 else None)
        if not count:
            ax.plot(0, y, "|", color=colors[index], markersize=22, markeredgewidth=4, clip_on=False)
        ax.text(rate+1.5, y, f"{rate:.1f}% ({count}/{total})", va="center", fontsize=10)
    ax.text(0, top+.72, model.split("/")[-1], fontsize=12, weight="bold")

ax.set_yticks([5, 4, 3, 1, 0, -1], [*labels, *labels])
ax.set_xlim(0, 120)
ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
ax.set_ylim(-1.7, 6.2)
ax.set_xlabel("Attack-trial rate on the synthetic transfer suite")
ax.xaxis.grid(True, alpha=.16)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis="y", length=0)
fig.suptitle("Prompts reduced unsafe requests. The tool guard blocked execution.",
             x=.035, y=.97, ha="left", fontsize=15, weight="bold")
fig.text(.035, .025,
         "Gray/orange: model requests. Teal: allowed simulated actions.\n"
         "Enforced models still requested 225/360 and 186/360 unsafe forwards. Three repetitions per case; no error bars.",
         fontsize=9, color="#475569")
fig.subplots_adjust(left=.33, right=.98, top=.86, bottom=.15)
output = ROOT / "figures"
output.mkdir(exist_ok=True)
fig.savefig(output / "forwarding-results.png", dpi=180)
plt.close(fig)
print(output / "forwarding-results.png")
