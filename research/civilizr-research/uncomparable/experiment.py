"""Small Qloo experiment wrapper; stdlib only. Plans are immutable JSON files."""
import argparse
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import qloo

qloo.ENDPOINTS.update({"/v2/audiences", "/v2/audiences/types"})


def records(payload):
    result = payload.get("results", {})
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        for key in ("entities", "tags", "audiences", "audience_types", "types"):
            if isinstance(result.get(key), list):
                return result[key]
    return []


def run(stage, budget, out_name=None):
    plan = qloo.read_json(ROOT / "plans" / (stage + ".json"))
    out = ROOT / "runs" / (out_name or stage)
    attempts = sum(len(p.read_text(encoding="utf-8").splitlines())
                   for p in (ROOT / "runs").glob("*/requests.jsonl"))
    pending = 0
    for spec in plan["requests"]:
        meta = out / (spec["id"] + ".meta.json")
        if not meta.exists() or not qloo.read_json(meta).get("ok"):
            pending += 1
    if attempts + min(budget, pending) > 85:
        raise ValueError("Experiment-wide 85-attempt ceiling would be exceeded")
    frozen = ["UNCOMPARABLE_EXPERIMENT_PLAN.md", "properties.json", "baseline_ab.json", "experiment.py"]
    state = {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in frozen}
    lock = ROOT / "preregistration.json"
    if not lock.exists():
        qloo.save_json(lock, {"frozen_at": qloo.now(), "sha256": state})
    else:
        saved = qloo.read_json(lock)["sha256"]
        for name in frozen[:3]:
            if saved[name] != state[name]:
                raise ValueError("Frozen pre-API material changed: " + name)
    out.mkdir(parents=True, exist_ok=True)
    qloo.save_json(out / "wrapper.json", {"at": qloo.now(), "sha256": state})
    return qloo.run(plan, out, qloo.load_env(ROOT.parent / "civilizr-research.env"),
                    budget=budget, retries=0, timeout=20, delay=0.3)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage")
    p.add_argument("--budget", required=True, type=int)
    p.add_argument("--out-name")
    args = p.parse_args()
    if not 1 <= args.budget <= 85:
        p.error("budget must be 1..85")
    sys.exit(run(args.stage, args.budget, args.out_name))
