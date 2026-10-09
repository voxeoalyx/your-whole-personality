"""Offline exports and conservative, tie-aware comparisons. No network access."""
import hashlib
import math
from statistics import mean
from experiment import ROOT, qloo, records


def ranks(values):
    ordered = sorted(enumerate(values), key=lambda x: x[1])
    result = [0.0] * len(values)
    start = 0
    while start < len(ordered):
        end = start + 1
        while end < len(ordered) and ordered[end][1] == ordered[start][1]:
            end += 1
        for i, _ in ordered[start:end]:
            result[i] = (start + 1 + end) / 2
        start = end
    return result


def spearman(a, b):
    if len(a) != len(b) or len(a) < 2:
        return None
    x, y = ranks(a), ranks(b)
    mx, my = mean(x), mean(y)
    numerator = sum((u - mx) * (v - my) for u, v in zip(x, y))
    denominator = math.sqrt(sum((v - mx) ** 2 for v in x) * sum((v - my) ** 2 for v in y))
    return numerator / denominator if denominator else None


def scores(payload):
    return {x.get("entity_id", x.get("id")): x["query"]["affinity"]
            for x in records(payload)
            if isinstance(x.get("query", {}).get("affinity"), (int, float))
            and math.isfinite(x["query"]["affinity"])}


def compare(a, b, expected):
    expected = set(expected)
    common = expected & a.keys() & b.keys()
    result = {"expected": len(expected), "paired": len(common), "complete": common == expected,
              "spearman": None, "top5_jaccard": None}
    if common != expected or len(common) < 2:
        return result
    ids = sorted(expected)
    result["spearman"] = spearman([a[i] for i in ids], [b[i] for i in ids])
    if result["spearman"] is not None:
        def top(values):
            threshold = sorted((values[i] for i in ids), reverse=True)[min(5, len(ids)) - 1]
            return {i for i in ids if values[i] >= threshold}
        x, y = top(a), top(b)
        result["top5_jaccard"] = len(x & y) / len(x | y)
    return result


def main():
    out = ROOT / "tables"
    out.mkdir(exist_ok=True)
    requests, rows, candidates, payloads, specifications = [], [], [], {}, {}
    for manifest_path in sorted((ROOT / "runs").glob("*/manifest.json")):
        folder = manifest_path.parent
        manifest = qloo.read_json(manifest_path)
        for spec in manifest["identity"]["plan"]["requests"]:
            key = folder.name + "/" + spec["id"]
            meta_path = folder / (spec["id"] + ".meta.json")
            meta = qloo.read_json(meta_path) if meta_path.exists() else {}
            payload = qloo.read_json(folder / meta["raw_file"]) if meta.get("raw_file") else {}
            if meta.get("raw_file"):
                assert hashlib.sha256((folder / meta["raw_file"]).read_bytes()).hexdigest() == meta["response_sha256"], key
            payloads[key], specifications[key] = payload, spec
            found = records(payload)
            scored = scores(payload)
            requests.append({"request": key, "endpoint": spec["endpoint"], "http_status": meta.get("http_status"),
                             "ok": meta.get("ok", False), "returned": len(found), "scored": len(scored),
                             "unique_scores": len(set(scored.values())), "warnings": qloo.canonical(payload.get("warnings", [])),
                             "errors": qloo.canonical(payload.get("errors", [])), "params": qloo.canonical(spec["params"]),
                             "raw": str((folder / meta["raw_file"]).relative_to(ROOT)) if meta.get("raw_file") else ""})
            for rank, item in enumerate(found, 1):
                rows.append({"request": key, "rank_as_returned": rank, "id": item.get("entity_id", item.get("id")),
                             "native_id": item.get("id"), "name": item.get("name"), "type": qloo.canonical(item.get("types", item.get("type"))),
                             "affinity": item.get("query", {}).get("affinity"), "popularity": item.get("popularity"),
                             "address": item.get("properties", {}).get("address"),
                             "explainability": qloo.canonical(item.get("query", {}).get("explainability")),
                             "tag_count": len(item.get("tags") or [])})
            expected = spec["params"].get("filter.results.entities", [])
            if isinstance(expected, str):
                expected = expected.split(",")
            present = {x.get("entity_id", x.get("id")): x for x in found}
            for candidate in expected:
                candidates.append({"request": key, "id": candidate, "name": present.get(candidate, {}).get("name"),
                                   "state": "scored" if candidate in scored else "returned_unscored" if candidate in present else "missing",
                                   "affinity": scored.get(candidate), "http_status": meta.get("http_status")})
            assert set(present).issuperset(scored), key
    qloo.write_csv(out / "requests.csv", requests)
    qloo.write_csv(out / "results.csv", rows)
    qloo.write_csv(out / "candidate_scores.csv", candidates)
    panels = qloo.read_json(ROOT / "panels.json")
    matrix = []
    houses = [x["id"] for x in qloo.read_json(ROOT / "properties.json")]
    brand_ids = [x["id"] for x in panels["brands"]]
    for a in houses:
        for b in houses:
            matrix.append({"a": a, "b": b, **compare(scores(payloads.get("08_fixed/" + a + "_fixed", {})),
                                                  scores(payloads.get("08_fixed/" + b + "_fixed", {})), brand_ids)})
    qloo.write_csv(out / "property_similarity.csv", matrix)
    checks = [("eames_repeat", "eames_fixed", "repeat"), ("eames_half", "eames_fixed", "candidate_half"),
              ("farnsworth_half", "farnsworth_fixed", "candidate_half"),
              ("eames_places_repeat", "eames_places_fixed", "repeat"),
              ("eames_places_half", "eames_places_fixed", "candidate_half")]
    stability = []
    for new, old, kind in checks:
        current = "09_checks/" + new
        ids = specifications[current]["params"]["filter.results.entities"]
        stability.append({"test": new, "kind": kind, **compare(scores(payloads[current]), scores(payloads["08_fixed/" + old]), ids)})
    for a, b, panel_name in [("eames_fixed", "ray_fixed", "brands"), ("eames_places_fixed", "ray_places_fixed", "places"),
                              ("wright_fixed", "ray_fixed", "brands")]:
        stability.append({"test": a + "__" + b, "kind": "related_input" if a.startswith("eames") else "different_author",
                          **compare(scores(payloads["08_fixed/" + a]), scores(payloads["08_fixed/" + b]),
                                    [x["id"] for x in panels[panel_name]])})
    qloo.write_csv(out / "stability.csv", stability)
    wide = []
    for a in houses:
        row = {"property": a}
        row.update({r["b"]: r["spearman"] for r in matrix if r["a"] == a})
        wide.append(row)
    qloo.write_csv(out / "similarity_matrix.csv", wide)
    props = qloo.read_json(ROOT / "properties.json")
    qloo.write_csv(out / "properties.csv", [{**p, "sources": " | ".join(p["sources"])} for p in props])
    qloo.write_csv(out / "coverage.csv", qloo.read_json(ROOT / "coverage.json"))
    baseline = {x["id"]: x for x in qloo.read_json(ROOT / "baseline_ab.json")}
    assessments = {x["id"]: x for x in qloo.read_json(ROOT / "assessments.json")}
    comparisons = []
    markdown = ["# A/B/C comparison", "",
                "A and B were frozen before Qloo requests. Every method uses the same property fact record in `properties.json`. "
                "B's predicted cultural leads are hypotheses, not documented relationships. C adds Qloo observations; it does not turn them into property facts. "
                "Assessment is unblinded and provisional. Search expansion and supplementary lead validation occurred after the baseline freeze.", ""]
    for p in props:
        a, b = assessments[p["id"]], baseline[p["id"]]
        comparisons.append({"property": p["name"], "A": b["A"], "B": b["B"], "C": a["C"],
                            "incremental_value": a["increment"], "evidence_requests": " | ".join(a["evidence"])})
        markdown += ["## " + p["name"], "", "**A — conventional facts.** " + b["A"], "",
                     "**B — provenance plus LLM.** " + b["B"], "", "**C — same facts plus Qloo.** " + a["C"], "",
                     "**Increment over B.** " + a["increment"], "",
                     "Source facts: " + "; ".join("[primary source](" + s + ")" for s in p["sources"]) + ".", "",
                     "Qloo evidence: " + ", ".join("`" + s + "`" for s in a["evidence"]) + ".", ""]
    qloo.write_csv(out / "comparisons.csv", comparisons)
    (ROOT / "COMPARATIVE_RESULTS.md").write_text("\n".join(markdown), encoding="utf-8")
    summary = {"requests": len(requests), "http_200": sum(x["http_status"] == 200 for x in requests),
               "http_400": sum(x["http_status"] == 400 for x in requests), "stability": stability,
               "candidate_states": {s: sum(x["state"] == s for x in candidates) for s in ["scored", "returned_unscored", "missing"]}}
    qloo.save_json(out / "summary.json", summary)
    print(qloo.canonical(summary))


if __name__ == "__main__":
    main()
