"""Copy pod results into a fresh staging directory; never overwrite local results."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
POD = "thesis-clinical-nlp"
REMOTE = "/workspace/agent-analysis/results"


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stage = ROOT / ".pod-sync" / stamp
    stage.mkdir(parents=True, exist_ok=False)
    base = ["kubectl", "-n", "uic-cs-parde"]
    # Runtime logs may change while the service is alive; back them up, but
    # exclude them from immutable experiment checksums and public commits.
    code = (
        "import pathlib,hashlib,json; p=pathlib.Path('/workspace/agent-analysis/results'); "
        "print(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() "
        "for f in p.rglob('*') if f.is_file() and 'server-logs' not in f.relative_to(p).parts}))"
    )
    output = subprocess.check_output(base + ["exec", POD, "--",
        "/workspace/.venvs/agent-analysis-py311/bin/python", "-c", code], text=True)
    expected = json.loads(output)
    # kubectl treats a Windows drive colon as a remote specification.
    destination = (stage / "results").relative_to(ROOT).as_posix()
    subprocess.run(base + ["cp", f"{POD}:{REMOTE}", destination], cwd=ROOT, check=True)
    copied, same, conflicts = [], [], []
    for name, sha in expected.items():
        source = (stage / "results" / name).resolve()
        target = (ROOT / "results" / name).resolve()
        if not source.is_relative_to(stage.resolve()) or not target.is_relative_to((ROOT / "results").resolve()):
            raise ValueError("Invalid result path")
        if hashlib.sha256(source.read_bytes()).hexdigest() != sha:
            raise ValueError(f"Remote result changed or copy mismatch: {name}")
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() == sha:
                same.append(name)
            else:
                conflicts.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as handle:
                handle.write(source.read_bytes())
            if hashlib.sha256(target.read_bytes()).hexdigest() != sha:
                raise ValueError(f"Local verification failed: {name}")
            copied.append(name)
    report = {"timestamp_utc": stamp, "remote": REMOTE, "pod": POD,
              "verified_remote_files": len(expected), "copied": copied, "already_identical": same,
              "conflicts_preserved_in_staging": conflicts,
              "local_staging": str(stage), "sha256": expected,
              "note": "Server runtime logs copied only into staging and excluded from immutable checks."}
    path = ROOT / "analysis" / f"pod-sync-{stamp}.json"
    with path.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps({"verified": len(expected), "copied": len(copied), "already_identical": len(same),
                      "conflicts": conflicts, "report": str(path), "new_files": copied}, indent=2))


if __name__ == "__main__":
    main()
