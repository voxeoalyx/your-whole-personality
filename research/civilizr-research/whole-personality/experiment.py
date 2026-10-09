"""Independent, disposable Whole Personality Qloo runner; stdlib only."""
import argparse
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import qloo
qloo.ENDPOINTS.update({"/v2/audiences", "/v2/audiences/types"})


def items(payload):
    r = payload.get("results", {})
    if isinstance(r, list):
        return r
    return next((r[k] for k in ("entities", "tags", "audiences", "types") if isinstance(r.get(k), list)), []) if isinstance(r, dict) else []


def run(stage, budget, out_name=None):
    plan = qloo.read_json(ROOT / "plans" / (stage + ".json"))
    out = ROOT / "runs" / (out_name or stage)
    used = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in (ROOT / "runs").glob("*/requests.jsonl"))
    pending = sum(not (out / (s["id"] + ".meta.json")).exists() or not qloo.read_json(out / (s["id"] + ".meta.json")).get("ok") for s in plan["requests"])
    if used + min(budget, pending) > 185:
        raise ValueError("Experiment-wide 185-attempt ceiling would be exceeded")
    frozen = ["WHOLE_PERSONALITY_EXPERIMENT_PLAN.md", "NARRATIVE_PROTOCOL.md", "llm_baseline.json"]
    state = {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in frozen}
    lock = ROOT / "preregistration.json"
    if lock.exists():
        if qloo.read_json(lock)["sha256"] != state:
            raise ValueError("Frozen plan or LLM baseline changed")
    else:
        qloo.save_json(lock, {"at": qloo.now(), "sha256": state})
    out.mkdir(parents=True, exist_ok=True)
    qloo.save_json(out / "wrapper.json", {"at": qloo.now(), "sha256": state, "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    return qloo.run(plan, out, qloo.load_env(ROOT.parent / "civilizr-research.env"), budget, 0, 20, 0.3)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage")
    p.add_argument("--budget", type=int, required=True)
    p.add_argument("--out-name")
    args = p.parse_args()
    if not 1 <= args.budget <= 185:
        p.error("budget must be 1..185")
    sys.exit(run(args.stage, args.budget, args.out_name))
