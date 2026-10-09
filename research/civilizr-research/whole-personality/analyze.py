"""Offline analysis, preserving missingness and separating proxies from evidence."""
from collections import Counter
import hashlib
from statistics import mean
from metrics import ROOT, qloo, items, scores, compare, equal_rank_mix, invalid_inputs


def main():
    out = ROOT / "tables"
    out.mkdir(exist_ok=True)
    data, specs, audit, result_rows, missing = {}, {}, [], [], []
    for mp in sorted((ROOT / "runs").glob("*/manifest.json")):
        for spec in qloo.read_json(mp)["identity"]["plan"]["requests"]:
            ref = mp.parent.name + "/" + spec["id"]
            meta_path = mp.parent / (spec["id"] + ".meta.json")
            if not meta_path.exists():
                continue
            meta = qloo.read_json(meta_path)
            raw = mp.parent / meta["raw_file"]
            assert hashlib.sha256(raw.read_bytes()).hexdigest() == meta["response_sha256"], ref
            payload = qloo.read_json(raw)
            data[ref], specs[ref] = payload, spec
            sc = scores(payload)
            audit.append({"request":ref, "status":meta["http_status"], "returned":len(items(payload)), "scored":len(sc),
                          "distinct_scores":len(set(sc.values())), "params":qloo.canonical(spec["params"]),
                          "warnings":qloo.canonical(payload.get("warnings", [])), "errors":qloo.canonical(payload.get("errors", []))})
            for rank, x in enumerate(items(payload), 1):
                result_rows.append({"request":ref,"rank":rank,"id":x.get("entity_id",x.get("id")),"name":x.get("name"),
                                    "type":qloo.canonical(x.get("types",x.get("type"))),"affinity":x.get("query",{}).get("affinity"),
                                    "popularity":x.get("popularity"),"explainability":qloo.canonical(x.get("query",{}).get("explainability"))})
            present={x.get("entity_id",x.get("id")) for x in items(payload)}
            for entity in spec["params"].get("filter.results.entities", []):
                missing.append({"request":ref,"id":entity,"state":"scored" if entity in sc else "returned_unscored" if entity in present else "missing", "affinity":sc.get(entity)})
    refs = qloo.read_json(ROOT / "profile_refs.json")
    sec = qloo.read_json(ROOT / "secondary_refs.json")
    panels = qloo.read_json(ROOT / "panels.json")
    ids = {"brand":[x["id"] for x in panels["primary_brand"]], "tv_show":[x["id"] for x in panels["tv_show"]], "secondary":[x["id"] for x in panels["secondary_brand"]]}
    design = qloo.read_json(ROOT / "profile_design.json")
    configs = qloo.read_json(ROOT / "configurations.json")
    seeds = qloo.read_json(ROOT / "seeds.json")["seeds"]
    def payload(key, domain):
        ref = sec.get(key) if domain == "secondary" else refs.get(key,{}).get(domain)
        return data.get(ref,{})
    def cmp(a,b,d,subset=None):
        return compare(scores(payload(a,d)),scores(payload(b,d)),ids[d] if subset is None else subset)
    def top(k,d,n=3):
        return [x["name"] for x in items(payload(k,d))[:n]]
    coverage, evidence = [], []
    for p in design["profiles"]:
        k = p["id"]
        record = {"id":k,"interests":[seeds[s]["name"] for s in configs[k]],"brands":[],"tv":[],"refs":refs[k]}
        for d in ["brand","tv_show"]:
            sc=scores(payload(k,d))
            native={t.get("name") for x in items(payload(k,d))[:10] for t in (x.get("tags") or []) if "genre" in t.get("type","")}
            coverage.append({"profile":k,"domain":d,"requested":len(ids[d]),"scored":len(sc),"complete":set(ids[d])<=sc.keys(),"faithful_inputs":not invalid_inputs(payload(k,d)),"unsupported_inputs":" | ".join(invalid_inputs(payload(k,d))),
                             "nonflat":len(set(sc.values()))>1,"top10_native_genre_count":len(native),"top10_native_genres":" | ".join(sorted(x for x in native if x)),"top5":" | ".join(top(k,d,5))})
            record["brands" if d=="brand" else "tv"]=top(k,d)
        record["faithful_inputs"]=all(not invalid_inputs(payload(k,d)) for d in ["brand","tv_show"])
        evidence.append(record)
    swaps=[]
    for a,b in design["swap_pairs"] + [["p01","demo_person"],["p02","demo_person"]]:
        for d in ["brand","tv_show","secondary"]:
            pa,pb=payload(a,d),payload(b,d)
            swaps.append({"a":a,"b":b,"domain":d,"faithful_inputs":not (invalid_inputs(pa)+invalid_inputs(pb)) if pa and pb else None,**cmp(a,b,d)})
    dominance=[]
    for p in design["loo_profiles"]:
        for e in configs[p]:
            ablated="loo_"+p+"__"+e
            row={"profile":p,"removed":e,"type":seeds[e]["type"],"popularity":seeds[e].get("popularity")}
            for panel_mode in ["full","half0","half1","secondary"]:
                ds=[]
                for d in ["brand","tv_show"]:
                    actual="secondary" if panel_mode=="secondary" and d=="brand" else d
                    chosen=ids[actual]
                    if panel_mode in ("half0","half1"):
                        chosen=chosen[int(panel_mode[-1])::2]
                    m=cmp(p,ablated,actual,chosen)
                    row[panel_mode+"_"+d]=m["distance"]
                    ds.append(m["distance"])
                row["id_"+panel_mode]=mean(ds) if all(x is not None for x in ds) else None
            contributions=payload(p,"brand").get("query",{}).get("explainability",{}).get("signal.interests.entities",{}).get("effect_on_all_recs",[])
            row["brand_explainability_share"]=next((x.get("avg_score") for x in contributions if x.get("entity_id")==seeds[e]["id"]),None)
            dominance.append(row)
    winners=[]
    for p in design["loo_profiles"]:
        rs=[r for r in dominance if r["profile"]==p]
        w={"profile":p}
        for mode in ["full","half0","half1","secondary"]:
            valid=[r for r in rs if r["id_"+mode] is not None]
            ordered=sorted(valid,key=lambda r:r["id_"+mode],reverse=True)
            w[mode+"_winner"]=ordered[0]["removed"] if len(ordered)==len(rs) else None
            if mode=="full" and len(ordered)==len(rs):
                w["largest_id"],w["next_id"]=ordered[0]["id_full"],ordered[1]["id_full"]
        w["dominance_flag"]=(w.get("largest_id",0)>0.10 and w.get("largest_id",0)>2*w.get("next_id",0)
                             and w["full_winner"]==w["half0_winner"]==w["half1_winner"])
        winners.append(w)
    partnerships=[]
    detail=["# Brand partnership comparisons", "", "All outputs are modeled associations, not interventions or predicted campaign effects. A/B/C/D refer to brand alone, brand+partner, brand+alternative and partner alone. Candidate panels are identical within each domain. Low distance to D warns that B may primarily reproduce the partner.", ""]
    for case in design["brands"]:
        brand=case["brand"]
        detail += ["## "+seeds[brand]["name"], ""]
        for partner in case["partners"]:
            combo="brand_"+brand+"__"+partner
            alternative=next(x for x in case["partners"] if x!=partner)
            for d in ["brand","tv_show"]:
                a="single_"+brand; b="single_"+partner
                db,dp=cmp(combo,a,d),cmp(combo,b,d)
                mix=equal_rank_mix(scores(payload(a,d)),scores(payload(b,d)),ids[d])
                row={"brand":brand,"partner":partner,"alternative":alternative,"domain":d,
                     "distance_to_brand":db["distance"],"distance_to_partner":dp["distance"],
                     "brand_partner_distance":cmp(a,b,d)["distance"],
                     "distance_to_alternative_combo":cmp(combo,"brand_"+brand+"__"+alternative,d)["distance"],
                     "distance_to_equal_rank_mix":compare(scores(payload(combo,d)),mix,ids[d])["distance"],
                     "top_brand_alone":" | ".join(top(a,d)),"top_combo":" | ".join(top(combo,d)),"top_partner_alone":" | ".join(top(b,d))}
                row["partner_substitution_flag"]=dp["distance"] is not None and db["distance"] is not None and dp["distance"]<=.02 and db["distance"]>=.10
                row["distinct_from_both"]=dp["distance"] is not None and db["distance"] is not None and min(dp["distance"],db["distance"])>=.03
                for half in [0,1]:
                    chosen=ids[d][half::2]
                    x,y=cmp(combo,a,d,chosen),cmp(combo,b,d,chosen)
                    row["half"+str(half)+"_to_brand"],row["half"+str(half)+"_to_partner"]=x["distance"],y["distance"]
                partnerships.append(row)
                detail += [f"**Partner: {seeds[partner]['name']} — {d}.**", "", "A: "+row["top_brand_alone"]+". B: "+row["top_combo"]+". D: "+row["top_partner_alone"]+".", "",
                           f"D(B,A)={row['distance_to_brand']:.3f}; D(B,D)={row['distance_to_partner']:.3f}; D(B,C)={row['distance_to_alternative_combo']:.3f}; D(B,equal-rank mix)={row['distance_to_equal_rank_mix']:.3f}.", ""]
    checks=[]
    for ref,spec in specs.items():
        if spec.get("compare_to"):
            checks.append({"request":ref,"kind":spec.get("check"),**compare(scores(data[ref]),scores(data[spec["compare_to"]]),spec["params"]["filter.results.entities"])})
    for name,rows in [("requests",audit),("results",result_rows),("candidate_scores",missing),("coverage",coverage),("swaps",swaps),("dominance",dominance),("dominance_winners",winners),("partnerships",partnerships),("checks",checks)]:
        if rows:
            qloo.write_csv(out / (name+".csv"),rows)
    qloo.save_json(ROOT / "narrative_evidence.json",evidence)
    (ROOT / "BRAND_PARTNERSHIPS.md").write_text("\n".join(detail),encoding="utf-8")
    seed_coverage=[]
    for key,seed in seeds.items():
        row={"seed":key,"name":seed["name"],"type":seed["type"],"popularity":seed.get("popularity")}
        for d in ["brand","tv_show"]:
            p=payload("single_"+key,d)
            row[d+"_unsupported"]=bool(invalid_inputs(p))
            row[d+"_scored"]=len(scores(p))
        seed_coverage.append(row)
    qloo.write_csv(out/"seed_coverage.csv",seed_coverage)
    summary={"requests":len(audit),"statuses":dict(Counter(r["status"] for r in audit)),"candidate_missing":sum(x["state"]=="missing" for x in missing),"candidate_unscored":sum(x["state"]=="returned_unscored" for x in missing),"faithful_profile_domains":sum(x["faithful_inputs"] for x in coverage),
             "profile_domain_complete":sum(x["complete"] for x in coverage),"profile_domain_total":len(coverage),"winners":winners,
             "partnership_domain_comparisons":len(partnerships),"partner_substitution_flags":sum(x["partner_substitution_flag"] for x in partnerships),
             "distinct_from_both":sum(x["distinct_from_both"] for x in partnerships),"checks":checks}
    qloo.save_json(out / "summary.json",summary)
    print(qloo.canonical(summary))


if __name__=="__main__":
    main()
