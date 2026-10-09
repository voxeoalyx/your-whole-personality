"""Verify this archived study and scan its artifacts for the active key, without API calls."""
from collections import Counter
from datetime import datetime
import hashlib
from urllib.parse import urlsplit, parse_qs
from metrics import ROOT, qloo, items, invalid_inputs


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    frozen=qloo.read_json(ROOT / "preregistration.json")
    for name,expected in frozen["sha256"].items():
        assert digest(ROOT / name)==expected, "Frozen file changed: "+name
    shared=digest(ROOT.parent / "qloo.py")
    assert shared=="88926b5ff19d9578b0be91249bce28af4fa4ad08289956bda59ef7d9d0db267e", "Shared runner changed"
    attempts=0; raw_count=0; endpoints=Counter(); stamps=[]
    for manifest_path in sorted((ROOT / "runs").glob("*/manifest.json")):
        folder=manifest_path.parent
        manifest=qloo.read_json(manifest_path)
        plan=qloo.read_json(ROOT / "plans" / (folder.name+".json"))
        assert manifest["identity"]["plan"]==plan, "Plan differs from execution manifest"
        wrapper=qloo.read_json(folder / "wrapper.json")
        assert wrapper["sha256"]==frozen["sha256"], "Run used changed methodology"
        assert wrapper["runner_sha256"]==digest(ROOT / "experiment.py"), "Wrapper changed after execution"
        attempts+=len((folder / "requests.jsonl").read_text(encoding="utf-8").splitlines())
        for spec in plan["requests"]:
            meta=qloo.read_json(folder / (spec["id"]+".meta.json"))
            raw=folder / meta["raw_file"]
            assert raw.resolve().is_relative_to(folder.resolve())
            assert digest(raw)==meta["response_sha256"], "Response hash mismatch"
            assert meta["spec"]==spec and meta["params"]==qloo.wire_params(spec["params"])
            assert {k:v[0] for k,v in parse_qs(urlsplit(meta["url"]).query).items()}==meta["params"]
            assert meta["ok"] and meta["http_status"]==200 and meta["attempt_no"]==1
            stamps.append(datetime.fromisoformat(meta["at"]))
            endpoints[spec["endpoint"]]+=1
            raw_count+=1
    assert attempts==raw_count==183 and attempts<=185
    assert datetime.fromisoformat(frozen["at"])<=min(stamps)
    for record in qloo.read_json(ROOT / "sources/docs_manifest.json"):
        assert record["status"]=="fulfilled"
        source=record["value"]
        source_path="__".join(urlsplit(source["url"]).path.split("/")[-2:])
        assert digest(ROOT / "sources" / source_path)==source["sha256"]
    evidence=qloo.read_json(ROOT / "narrative_evidence.json")
    assert sum(x["faithful_inputs"] for x in evidence)==10
    narratives={x["id"]:x for x in qloo.read_json(ROOT / "qloo_narratives.json")}
    for row in evidence:
        for domain,field in [("brand","brands"),("tv_show","tv")]:
            stage,ident=row["refs"][domain].split("/")
            folder=ROOT / "runs" / stage
            meta=qloo.read_json(folder / (ident+".meta.json"))
            payload=qloo.read_json(folder / meta["raw_file"])
            assert row[field]==[x["name"] for x in items(payload)[:3]]==narratives[row["id"]][field]
            assert row["faithful_inputs"]==(not invalid_inputs(payload))
    active_key=qloo.load_env(ROOT.parent / "civilizr-research.env").get("QLOO_API_KEY","")
    scanned=0
    if active_key:
        secret=active_key.encode()
        for file in ROOT.rglob("*"):
            if file.is_file() and "__pycache__" not in file.parts:
                if secret in file.read_bytes():
                    raise RuntimeError("Credential found in experiment artifact; contents withheld: "+str(file.relative_to(ROOT)))
                scanned+=1
    result={"at":qloo.now(),"passed":True,"attempts":attempts,"raw_responses_verified":raw_count,
            "endpoints":dict(endpoints),"first_request_at":min(stamps).isoformat(),"last_request_at":max(stamps).isoformat(),
            "preregistration_verified":True,"shared_runner_sha256":shared,"narratives_trace_to_raw":True,
            "active_key_artifact_scan":"passed" if active_key else "skipped_no_active_key", "files_scanned":scanned}
    qloo.save_json(ROOT / "tables/audit.json",result)
    print(qloo.canonical(result))


if __name__=="__main__":
    main()
