"""Offline descriptive summaries of actual saved runs; no API calls."""
import csv
import json
from pathlib import Path
import statistics
import qloo

ROOT = Path(__file__).resolve().parent
EXPERIMENT_RUNS = ("01-smoke", "02-host-probe", "03-discovery", "04-pilot",
                   "05-culture-pilot", "06-expansion", "07-culture-remaining",
                   "08-diagnostics", "09-sensitivity")


def complete20(obs):
    rows = obs["rows"][:20]
    return (len(rows) == 20 and len({r["id"] for r in rows if r["id"]}) == 20
            and all(qloo.number(r["affinity"]) for r in rows))


def main():
    observations = []
    attempt_counts = {}
    all_specs = []
    # Freeze this experiment's inputs; a future rerun must not silently add samples.
    for directory in (ROOT / "runs" / name for name in EXPERIMENT_RUNS):
        manifest_file = directory / "manifest.json"
        if not manifest_file.exists():
            continue
        manifest = qloo.read_json(manifest_file)
        if manifest.get("offline_analysis_only"):
            continue
        log = directory / "requests.jsonl"
        if log.exists():
            for line in log.read_text(encoding="utf-8").splitlines():
                code = str(json.loads(line).get("http_status"))
                attempt_counts[code] = attempt_counts.get(code, 0) + 1
        for spec in manifest["identity"]["plan"]["requests"]:
            meta_path = directory / (spec["id"] + ".meta.json")
            if not meta_path.exists():
                continue
            meta = qloo.read_json(meta_path)
            payload = qloo.read_json(directory / meta["raw_file"]) if meta.get("ok") else {}
            rows = qloo.normalized(payload)
            obs = {"spec": spec, "rows": rows, "source": str(directory.relative_to(ROOT) / meta.get("raw_file", "")),
                   "http_status": meta.get("http_status"), "ok": meta.get("ok"), "payload": payload}
            all_specs.append(obs)
            if spec.get("kind") == "profile" and meta.get("ok"):
                observations.append(obs)
    output = ROOT / "reports"
    output.mkdir(exist_ok=True)
    main_obs = [o for o in observations if o["spec"].get("role") in ("target", "control")
                and o["spec"]["dimension"] != "brands_point"]
    by_dim = {}
    for obs in main_obs:
        by_dim.setdefault(obs["spec"]["dimension"], []).append(obs)
    metrics, top, heatmaps = [], [], []
    for dim, group in by_dim.items():
        sims = []
        controls, targets = [], []
        for a in group:
            for b in group:
                if a["spec"]["id"] >= b["spec"]["id"]:
                    continue
                if not (complete20(a) and complete20(b)):
                    continue
                ia, ib = [r["id"] for r in a["rows"][:20]], [r["id"] for r in b["rows"][:20]]
                jac, cos = qloo.similarities(ia, ib)
                sims.append(jac)
                roles = {a["spec"]["role"], b["spec"]["role"]}
                if roles == {"target", "control"}:
                    controls.append(jac)
                if roles == {"target"}:
                    targets.append(jac)
        metrics.append({"dimension": dim, "areas": len(group),
                        "complete_top20_areas": sum(complete20(o) for o in group),
                        "target_control_pairs": len(controls),
                        "rows_min": min(len(o["rows"]) for o in group),
                        "rows_max": max(len(o["rows"]) for o in group),
                        "median_target_control_jaccard20": statistics.median(controls) if controls else None,
                        "median_target_target_jaccard20": statistics.median(targets) if targets else None,
                        "min_pair_jaccard20": min(sims) if sims else None,
                        "max_pair_jaccard20": max(sims) if sims else None})
        for obs in group:
            top.append({"area": obs["spec"]["area"], "dimension": dim,
                        "returned": len(obs["rows"]), "top5": " | ".join(r["name"] for r in obs["rows"][:5]),
                        "source": obs["source"]})
        # Readable matrix of six resolved areas, blank for incomplete top-20 lists.
        labels = [o["spec"]["area"] for o in group]
        matrix = []
        for a in group:
            row = {"area": a["spec"]["area"]}
            for b in group:
                sufficient = complete20(a) and complete20(b)
                row[b["spec"]["area"]] = qloo.similarities(
                    [r["id"] for r in a["rows"][:20]], [r["id"] for r in b["rows"][:20]])[0] if sufficient else None
            matrix.append(row)
        qloo.write_csv(output / f"{dim}_jaccard20.csv", matrix, ["area"] + labels)
    for obs in all_specs:
        if obs["spec"].get("kind") == "heatmap" and obs["ok"]:
            rows = obs["rows"]
            heatmaps.append({"dimension": obs["spec"]["dimension"], "cells": len(rows),
                             "unique_affinity_values": len({r["affinity"] for r in rows}),
                             "unique_geohash_lengths": sorted({len(r["geohash"]) for r in rows}),
                             "zero_popularity_cells": sum(r["popularity"] == 0 for r in rows),
                             "source": obs["source"]})
    sensitivity = []
    for name in ("Winter Park", "College Park", "Mills 50 point proxy"):
        point = [o for o in observations if o["spec"]["dimension"] == "brands_point" and o["spec"]["area"] == name]
        if len(point) == 2:
            jac, cos = qloo.similarities(*[[r["id"] for r in o["rows"][:20]] for o in point])
            sensitivity.append({"area": name, "comparison": "500m_vs_1000m_point", "jaccard20": jac, "rank_cosine20": cos})
        polygon = next((o for o in main_obs if o["spec"]["dimension"] == "brands" and o["spec"]["area"] == name), None)
        if polygon:
            for p in point:
                jac, cos = qloo.similarities([r["id"] for r in polygon["rows"][:20]], [r["id"] for r in p["rows"][:20]])
                sensitivity.append({"area": name, "comparison": f"polygon_vs_{p['spec']['params']['signal.location.radius']}m_point",
                                    "jaccard20": jac, "rank_cosine20": cos})
    qloo.write_csv(output / "dimension_summary.csv", metrics)
    qloo.write_csv(output / "neighborhood_top5.csv", top)
    qloo.write_csv(output / "heatmap_coverage.csv", heatmaps)
    qloo.write_csv(output / "geometry_sensitivity.csv", sensitivity)
    result = {"attempt_counts": attempt_counts, "total_attempts": sum(attempt_counts.values()),
              "dimensions": metrics, "heatmaps": heatmaps, "sensitivity": sensitivity}
    qloo.save_json(output / "summary.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
