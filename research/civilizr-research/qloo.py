"""Disposable Qloo research runner. Python 3.10+; standard library only."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

ROOT = Path(__file__).resolve().parent
ALLOWED_HOSTS = {"api.qloo.com", "staging.api.qloo.com", "hackathon.api.qloo.com"}
ENDPOINTS = {"/search", "/entities", "/v2/insights", "/v2/tags",
             "/v2/tags/types", "/trends/category", "/trends/entity",
             "/v2/trending", "/v2/analysis/compare"}


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_env(path):
    """Small dotenv subset; no interpolation/execution; process environment wins."""
    values = {}
    if path and Path(path).exists():
        for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                raise ValueError("Invalid .env line: expected NAME=value (content withheld)")
            name, value = line.split("=", 1)
            value = value.strip()
            if value.startswith(('"', "'")):
                quote = value[0]
                end = value.find(quote, 1)
                if end < 0 or (value[end + 1:].strip() and not value[end + 1:].strip().startswith("#")):
                    raise ValueError("Invalid quoted .env value (content withheld)")
                value = value[1:end]
            else:
                value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
            values[name.strip()] = value
    return {name: os.environ.get(name) or values.get(name, "")
            for name in ("QLOO_API_KEY", "QLOO_BASE_URL")}


def base_url(value):
    value = (value or "https://api.qloo.com").rstrip("/")
    parts = urlsplit(value)
    if (parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS
            or parts.path or parts.query or parts.fragment or parts.username
            or parts.password or parts.port not in (None, 443)):
        raise ValueError("QLOO_BASE_URL must be an HTTPS Qloo API host, with no path")
    return value


def wire_params(params):
    def scalar(v):
        return str(v).lower() if isinstance(v, bool) else str(v)
    return {k: ",".join(map(scalar, v)) if isinstance(v, list) else scalar(v)
            for k, v in sorted(params.items())}


def validate_plan(plan, key=""):
    if not isinstance(plan.get("requests"), list) or not plan["requests"]:
        raise ValueError("Plan must have a nonempty requests list")
    ids = set()
    for spec in plan["requests"]:
        name = spec.get("id", "")
        if not re.fullmatch(r"[a-z0-9_-]+", name) or name in ids:
            raise ValueError("Request IDs must be unique lowercase filenames")
        ids.add(name)
        if spec.get("endpoint") not in ENDPOINTS:
            raise ValueError("Endpoint is not an approved read-only Qloo route")
        if not isinstance(spec.get("params"), dict):
            raise ValueError("Each request needs params")
        for p, v in spec["params"].items():
            if re.search(r"key|token|authorization|secret", p, re.I):
                raise ValueError("Credentials must not appear in request parameters")
            vals = v if isinstance(v, list) else [v]
            if any(not isinstance(x, (str, int, float, bool)) for x in vals):
                raise ValueError("GET params must be scalar values or scalar lists")
    if key and key in canonical(plan):
        raise ValueError("Credential found in plan; refusing to save it")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward credentials to a redirect destination.


def transport(url, key, timeout):
    req = Request(url, headers={"X-Api-Key": key, "Accept": "application/json",
                                "User-Agent": "civilizr-disposable-research/0.1"})
    try:
        response = build_opener(NoRedirect()).open(req, timeout=timeout)
    except HTTPError as exc:
        response = exc
    with response:
        body = response.read(8 * 1024 * 1024 + 1)
        if len(body) > 8 * 1024 * 1024:
            raise ValueError("Response exceeds 8 MiB cap; reduce query scope")
        # Whitelist only operational headers; never log request headers.
        headers = {k: response.headers[k] for k in
                   ("Date", "Retry-After", "Content-Type", "X-Request-Id")
                   if response.headers.get(k)}
        return response.status, headers, body


def run(plan, out, env, budget=5, retries=1, timeout=20, delay=0.3,
        request_fn=transport):
    key = env.get("QLOO_API_KEY", "").strip()
    validate_plan(plan, key)
    base = base_url(env.get("QLOO_BASE_URL"))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    identity = {"base_url": base, "plan": plan,
                "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    manifest_path = out / "manifest.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        if manifest["identity"] != identity:
            raise ValueError("Run identity changed; use a new output directory")
    else:
        save_json(manifest_path, {"created_at": now(), "identity": identity})
    invocation = {"at": now(), "attempt_budget": budget, "retries": retries,
                  "timeout_seconds": timeout, "delay_seconds": delay,
                  "key_present": bool(key)}
    with (out / "invocations.jsonl").open("a", encoding="utf-8") as f:
        f.write(canonical(invocation) + "\n")
    if not key:
        save_json(out / "status.json", {"at": now(), "state": "blocked_missing_key",
                                       "network_attempts_this_invocation": 0})
        print("No QLOO_API_KEY. Saved plan; made zero API requests.")
        analyze(out)
        return 2
    attempts = 0
    halt = False
    for spec in plan["requests"]:
        meta_path = out / (spec["id"] + ".meta.json")
        previous = read_json(meta_path) if meta_path.exists() else {}
        if previous.get("ok") and (out / previous["raw_file"]).exists():
            continue
        if attempts >= budget or halt:
            break
        params = wire_params(spec["params"])
        url = base + spec["endpoint"] + "?" + urlencode(params)
        for retry in range(retries + 1):
            if attempts >= budget:
                break
            attempts += 1
            attempt_no = previous.get("attempt_no", 0) + 1
            meta = {"spec": spec, "url": url, "method": "GET", "params": params,
                    "request_sha256": digest({"base": base, "endpoint": spec["endpoint"], "params": params}),
                    "at": now(), "attempt_no": attempt_no, "ok": False}
            start = time.monotonic()
            status, headers, raw = None, {}, b""
            try:
                status, headers, raw = request_fn(url, key, timeout)
                # Exceptional server echoes of credentials are redacted before persistence.
                safe_text = raw.decode("utf-8", errors="replace").replace(key, "[REDACTED]")
                meta["credential_redacted"] = safe_text != raw.decode("utf-8", errors="replace")
                try:
                    payload = json.loads(safe_text)
                    meta["ok"] = (200 <= status < 300 and isinstance(payload, dict)
                                  and payload.get("success") is not False
                                  and not payload.get("error") and not payload.get("errors"))
                    filename = f"{spec['id']}.a{attempt_no}.json"
                except json.JSONDecodeError:
                    filename = f"{spec['id']}.a{attempt_no}.txt"
                    meta["error"] = "non_json_response"
                (out / filename).write_text(safe_text, encoding="utf-8")
                meta["raw_file"] = filename
                meta["response_sha256"] = hashlib.sha256(safe_text.encode()).hexdigest()
            except (URLError, OSError, TimeoutError, ValueError) as exc:
                meta["error"] = type(exc).__name__
            meta.update({"http_status": status, "response_headers": headers,
                         "elapsed_seconds": round(time.monotonic() - start, 3)})
            # Redact in metadata too, in case a server header reflects credentials.
            meta = json.loads(canonical(meta).replace(key, "[REDACTED]"))
            save_json(meta_path, meta)
            with (out / "requests.jsonl").open("a", encoding="utf-8") as f:
                f.write(canonical(meta) + "\n")
            print(f"{spec['id']}: HTTP {status or 'network error'}; {'ok' if meta['ok'] else 'failed'}")
            previous = meta
            if status in (401, 403):
                halt = True
                break
            if meta["ok"] or (status is not None and status != 429 and status < 500):
                break
            if retry < retries and attempts < budget:
                retry_after = headers.get("Retry-After", "0")
                try:
                    wait = float(retry_after)
                except ValueError:
                    wait = 0
                if wait > 30:
                    halt = True  # Resume later instead of ignoring long server cooldowns.
                    break
                time.sleep(max(2 ** retry, wait))
        if not halt:
            time.sleep(delay)
    complete = all((out / (s["id"] + ".meta.json")).exists()
                   and read_json(out / (s["id"] + ".meta.json")).get("ok")
                   for s in plan["requests"])
    save_json(out / "status.json", {"at": now(), "state": "complete" if complete else "partial",
                                   "network_attempts_this_invocation": attempts})
    analyze(out)
    return 0 if complete else 1


def at(obj, *keys):
    for key in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def first(*values):
    return next((v for v in values if v is not None), None)


def number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def result_rows(payload):
    result = payload.get("results", payload.get("data", {}))
    if isinstance(result, list):
        return "results", result
    if isinstance(result, dict):
        for key in ("entities", "tags", "heatmap", "tag_types", "types", "trends", "trending"):
            if isinstance(result.get(key), list):
                return key, result[key]
    return "unknown", []


def normalized(payload):
    kind, rows = result_rows(payload)
    output = []
    for rank, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            continue
        location = first(row.get("location"), at(row, "properties", "location"), {})
        query = row.get("query") or {}
        output.append({
            "rank": rank, "result_kind": kind,
            "id": first(row.get("entity_id"), row.get("tag_id"), row.get("id"),
                        row.get("tag_value"), at(location, "geohash"), row.get("type") if kind == "tag_types" else ""),
            "name": row.get("name", ""), "subtype": first(row.get("subtype"), row.get("type"), row.get("types")),
            "affinity": first(query.get("affinity"), row.get("affinity")),
            "affinity_rank": first(query.get("affinity_rank"), row.get("affinity_rank")),
            "popularity": first(query.get("popularity"), row.get("popularity"), at(row, "properties", "popularity")),
            "tag_affinity": query.get("tag_affinity"),
            "tag_affinity_rank": query.get("tag_affinity_rank"),
            "trend": first(query.get("trend"), row.get("trend"), row.get("trends")),
            "measurements_json": canonical(query.get("measurements")),
            "latitude": first(at(location, "latitude"), at(location, "lat")),
            "longitude": first(at(location, "longitude"), at(location, "lon")),
            "geohash": at(location, "geohash"),
            "disambiguation": row.get("disambiguation", ""),
            "geocode_json": canonical(at(row, "properties", "geocode")),
            "tags_json": canonical(first(row.get("tags"), at(row, "properties", "tags"))),
            "explainability_json": canonical(query.get("explainability")),
        })
    return output


def write_csv(path, rows, fields=None):
    fields = fields or list(dict.fromkeys(k for row in rows for k in row))
    with Path(path).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            # Prevent spreadsheet formula execution from API-sourced text.
            safe = {k: ("'" + v if isinstance(v, str) and v.startswith(("=", "+", "-", "@")) else v)
                    for k, v in row.items()}
            writer.writerow(safe)


def similarities(a, b):
    if not a or not b:
        return None, None
    sa, sb = set(a), set(b)
    jaccard = len(sa & sb) / len(sa | sb)
    va, vb = {x: 1 / (i + 1) for i, x in enumerate(a)}, {x: 1 / (i + 1) for i, x in enumerate(b)}
    cosine = sum(va[x] * vb[x] for x in sa & sb) / math.sqrt(
        sum(x*x for x in va.values()) * sum(x*x for x in vb.values()))
    return jaccard, cosine


def profile_signature(spec):
    # Compare only identical request definitions apart from the tested geography.
    params = dict(spec["params"])
    params.pop("signal.location", None)
    return digest({"endpoint": spec["endpoint"], "params": wire_params(params)})[:12]


def analyze(out):
    out = Path(out)
    plan = read_json(out / "manifest.json")["identity"]["plan"]
    tables, coverage, query_info, profiles = [], [], [], []
    for spec in plan["requests"]:
        file = out / (spec["id"] + ".meta.json")
        meta = read_json(file) if file.exists() else {}
        payload = read_json(out / meta["raw_file"]) if meta.get("ok") else {}
        rows = normalized(payload)
        context = {"request_id": spec["id"], "area": spec.get("area", ""),
                   "dimension": spec.get("dimension", ""), "kind": spec.get("kind", ""),
                   "raw_file": meta.get("raw_file", "")}
        tables.extend({**context, **r} for r in rows)
        coverage.append({**context, "status": "ok" if meta.get("ok") else "failed" if meta else "not_run",
                         "http_status": meta.get("http_status"), "rows": len(rows),
                         "scored_rows": sum(number(r["affinity"]) for r in rows),
                         "unique_ids": len({r["id"] for r in rows if r["id"]}),
                         "query_json": canonical(payload.get("query", {}))})
        query_info.append({**context, "query": payload.get("query", {}),
                           "warnings": first(payload.get("warnings"), payload.get("warning"))})
        if spec.get("kind") == "profile" and meta.get("ok") and spec.get("geography_verified"):
            profiles.append((spec, rows))
    write_csv(out / "results.csv", tables, list(tables[0]) if tables else ["request_id", "area", "dimension", "id", "name", "affinity"])
    write_csv(out / "coverage.csv", coverage)
    save_json(out / "query_metadata.json", query_info)
    pairs, vectors, differences = [], [], []
    for k in (10, 20):
        eligible = []
        for spec, rows in profiles:
            subset = rows[:k]
            ids = [r["id"] for r in subset]
            # Sparse/unscored rows cannot masquerade as a complete taste vector.
            if (len(subset) < k or len(set(ids)) != k or not all(ids)
                    or not all(number(r["affinity"]) for r in subset)):
                continue
            tied = len({r["affinity"] for r in subset}) < k
            eligible.append((spec, subset, ids, tied))
            for r in subset:
                vectors.append({"request_id": spec["id"], "area": spec["area"],
                                "dimension": spec["dimension"], "k": k, "id": r["id"],
                                "name": r["name"], "membership": 1,
                                "reciprocal_rank": 1 / r["rank"], "ties_present": tied})
        for a, ra, ia, ta in eligible:
            for b, rb, ib, tb in eligible:
                if a["dimension"] != b["dimension"] or profile_signature(a) != profile_signature(b):
                    continue
                jac, cos = similarities(ia, ib)
                pairs.append({"dimension": a["dimension"], "signature": profile_signature(a), "k": k,
                              "a": a["id"], "b": b["id"], "area_a": a["area"], "area_b": b["area"],
                              "jaccard": jac, "rank_cosine": cos, "ties_present": ta or tb})
                if b.get("role") == "control" and a.get("role") == "target":
                    ar, br = {r["id"]: r for r in ra}, {r["id"]: r for r in rb}
                    for item in sorted(set(ia) | set(ib)):
                        x, y = ar.get(item), br.get(item)
                        differences.append({"dimension": a["dimension"], "k": k, "area": a["area"],
                                            "control": b["area"], "id": item, "name": (x or y)["name"],
                                            "area_rank": x["rank"] if x else None,
                                            "control_rank": y["rank"] if y else None,
                                            "control_minus_area_rank": y["rank"]-x["rank"] if x and y else None,
                                            "observation": "both" if x and y else "area_top_k_only" if x else "control_top_k_only"})
        for dim, sig in sorted({(r["dimension"], r["signature"]) for r in pairs if r["k"] == k}):
            group = [r for r in pairs if r["dimension"] == dim and r["signature"] == sig and r["k"] == k]
            labels = list(dict.fromkeys(r["a"] for r in group))
            for metric in ("jaccard", "rank_cosine"):
                values = {(r["a"], r["b"]): r[metric] for r in group}
                matrix = [{"request_id": a, **{b: values.get((a, b)) for b in labels}} for a in labels]
                write_csv(out / f"matrix_{dim}_{sig}_k{k}_{metric}.csv", matrix)
    write_csv(out / "similarity_pairs.csv", pairs, list(pairs[0]) if pairs else ["dimension", "k", "a", "b", "jaccard", "rank_cosine"])
    write_csv(out / "fingerprints.csv", vectors, list(vectors[0]) if vectors else ["request_id", "dimension", "k", "id", "reciprocal_rank"])
    write_csv(out / "control_rank_differences.csv", differences, list(differences[0]) if differences else ["dimension", "area", "control", "id", "area_rank", "control_rank"])
    ok = sum(r["status"] == "ok" for r in coverage)
    report = ["# Run evidence", "", f"Successful requests: {ok}/{len(coverage)}.",
              "", "| Request | Status | Rows | Scored |", "|---|---|---:|---:|"]
    report += [f"| {r['request_id']} | {r['status']} | {r['rows']} | {r['scored_rows']} |" for r in coverage]
    report += ["", "Matrices use complete, scored, reviewed location profiles only.",
               "Missing from top-k is censoring, not zero affinity. Rank ties can distort rank cosine.",
               "No cultural maturity, economic maturity, statistical lift or leading-indicator claim is inferred."]
    if not pairs:
        report.append("No eligible profile pairs; no empirical similarity matrix can be computed.")
    (out / "evidence.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def combine(inputs, out):
    """Offline analysis view; references original raw files, never copies observations."""
    out = Path(out).resolve()
    if out.exists():
        raise ValueError("Combined output must be a new directory")
    out.mkdir(parents=True)
    requests, sources = [], []
    for i, directory in enumerate(inputs):
        directory = Path(directory).resolve()
        manifest = read_json(directory / "manifest.json")
        sources.append({"run": str(directory), "manifest_sha256": digest(manifest)})
        for spec in manifest["identity"]["plan"]["requests"]:
            renamed = dict(spec, id=f"r{i+1}_{spec['id']}")
            requests.append(renamed)
            source_meta = directory / (spec["id"] + ".meta.json")
            if source_meta.exists():
                meta = read_json(source_meta)
                meta.update({"spec": renamed, "source_meta": str(source_meta)})
                if "raw_file" in meta:
                    meta["raw_file"] = os.path.relpath(directory / meta["raw_file"], out)
                save_json(out / (renamed["id"] + ".meta.json"), meta)
    save_json(out / "manifest.json", {"created_at": now(), "offline_analysis_only": True,
                                      "sources": sources, "identity": {"plan": {"requests": requests}}})
    analyze(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    execute = sub.add_parser("run")
    execute.add_argument("plan", type=Path)
    execute.add_argument("--out", type=Path, required=True)
    execute.add_argument("--env", type=Path, default=ROOT / ".env")
    execute.add_argument("--budget", type=int, default=5, help="Maximum HTTP attempts, including retries")
    execute.add_argument("--retries", type=int, default=1)
    execute.add_argument("--timeout", type=float, default=20)
    execute.add_argument("--delay", type=float, default=0.3)
    execute.add_argument("--dry-run", action="store_true")
    analysis = sub.add_parser("analyze")
    analysis.add_argument("out", type=Path)
    merged = sub.add_parser("combine")
    merged.add_argument("inputs", nargs="+", type=Path)
    merged.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "combine":
        combine(args.inputs, args.out)
        return 0
    if args.command == "analyze":
        analyze(args.out)
        return 0
    if args.budget < 1 or not 0 <= args.retries <= 3 or args.timeout <= 0 or args.delay < 0:
        parser.error("budget/timeout must be positive, delay nonnegative, retries between 0 and 3")
    env = load_env(args.env)
    plan = read_json(args.plan)
    validate_plan(plan, env["QLOO_API_KEY"])
    if args.dry_run:
        print(json.dumps({"base_url": base_url(env["QLOO_BASE_URL"]), "plan": plan}, indent=2))
        return 0
    return run(plan, args.out, env, args.budget, args.retries, args.timeout, args.delay)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as exc:
        # Credential-bearing dotenv values are never included in these messages.
        print(f"Stopped: {exc}", file=sys.stderr)
        sys.exit(2)
