"""Evaluate the recorded pilot before authorizing the larger matrix."""
from metrics import ROOT, qloo, load, scores, compare

refs = qloo.read_json(ROOT / "profile_refs.json")
panels = qloo.read_json(ROOT / "panels.json")
rows = []
for a,b in [("p01","p02"),("p01","demo_person"),("p01","single_radiohead"),
            ("p01","single_blue_bottle"),("p01","single_severance"),
            ("p02","single_radiohead"),("p02","single_blue_bottle"),("p02","single_rogan")]:
    for d,p in [("brand","primary_brand"),("tv_show","tv_show")]:
        rows.append({"a":a,"b":b,"domain":d, **compare(scores(load(refs[a][d])), scores(load(refs[b][d])), [x["id"] for x in panels[p]])})
mix_rows = [r for r in rows if r["a"] == "p01" and r["b"].startswith("single_")]
passes = any(all(r["distance"] is not None and r["distance"] > 0.02 for r in mix_rows if r["domain"] == domain) for domain in ["brand","tv_show"])
result = {"at":qloo.now(), "continue_matrix":passes, "rule":"At least one domain has complete nonflat original mixture distinguishable from every singleton by D > 0.02", "comparisons":rows}
qloo.save_json(ROOT / "pilot_gate.json", result)
print(qloo.canonical(result))
