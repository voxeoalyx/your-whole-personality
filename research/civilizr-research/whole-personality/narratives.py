"""Offline narrative audit and blinded human packet. Does not rate its own outputs."""
from collections import Counter
import csv
import hashlib
from statistics import mean, median
from metrics import ROOT, qloo, items, load, scores, compare


def read_csv(name):
    with (ROOT / "tables" / (name + ".csv")).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def bucket(value, low, high):
    return "small" if value <= low else "large" if value >= high else "middle"


def names(record):
    return {domain + ":" + x.casefold() for domain in ["brands", "tv"] for x in record[domain]}


def normalized_summary(record):
    return (", ".join(record["brands"]) + " are three brand suggestions for this combination. "
            "For television, consider " + ", ".join(record["tv"]) +
            "; treat these suggestions as possibilities to explore, not conclusions about a person's character or preferences.")


def main():
    evidence = {x["id"]: x for x in qloo.read_json(ROOT / "narrative_evidence.json")}
    grounded = {x["id"]: x for x in qloo.read_json(ROOT / "qloo_narratives.json")}
    baseline = {x["id"]: x for x in qloo.read_json(ROOT / "llm_baseline.json")["profiles"]}
    panels = qloo.read_json(ROOT / "panels.json")
    swaps = read_csv("swaps")
    audit, gaps, comparisons = [], [], []
    for pid, record in grounded.items():
        assert record["brands"] == evidence[pid]["brands"] and record["tv"] == evidence[pid]["tv"]
        assert record["faithful_inputs"] == evidence[pid]["faithful_inputs"]
        for method, r in [("Qloo-grounded",record),("LLM-only",baseline[pid])]:
            wc=len(r["summary"].split())
            assert 30 <= wc <= 55, (pid,method,wc)
            audit.append({"profile":pid,"method":method,"words":wc,
                          "eligible_comparison":record["faithful_inputs"],
                          "names_match_top3_evidence":True if method=="Qloo-grounded" else "not_applicable",
                          "independent_quality_rating":"not_collected"})
        comparisons.append({"profile":pid,"interests":" | ".join(record["interests"]),
                            "faithful_inputs":record["faithful_inputs"],
                            "qloo_brands":" | ".join(record["brands"]),"llm_brands":" | ".join(baseline[pid]["brands"]),
                            "qloo_tv":" | ".join(record["tv"]),"llm_tv":" | ".join(baseline[pid]["tv"]),
                            "literal_name_overlap":len(names(record)&names(baseline[pid]))})
        for d in ["brand","tv_show"]:
            raw=load(record["refs"][d]); xs=items(raw)
            assert len(xs)>=4
            third,fourth=xs[2],xs[3]
            gaps.append({"profile":pid,"domain":d,"request":record["refs"][d],
                         "faithful_inputs":record["faithful_inputs"],
                         "rank3":third["name"],"rank4":fourth["name"],
                         "score_gap_3_to_4_within_query":third["query"]["affinity"]-fourth["query"]["affinity"]})
    changes=[]
    for a,b in qloo.read_json(ROOT / "profile_design.json")["swap_pairs"]:
        if not (grounded[a]["faithful_inputs"] and grounded[b]["faithful_inputs"]):
            continue
        ms=[float(x["distance"]) for x in swaps if x["a"]==a and x["b"]==b and x["domain"] in ["brand","tv_show"]]
        assert len(ms)==2
        x,y=names(grounded[a]),names(grounded[b]); change=1-len(x&y)/len(x|y)
        bx,by=names(baseline[a]),names(baseline[b])
        changes.append({"a":a,"b":b,"mean_data_distance":mean(ms),"data_bucket":bucket(mean(ms),.05,.15),
                        "qloo_named_content_distance":change,"narrative_bucket":bucket(change,1/3,2/3),
                        "llm_named_content_distance":1-len(bx&by)/len(bx|by)})
    for name,rows in [("narrative_audit",audit),("narrative_cutoff_gaps",gaps),("llm_vs_qloo",comparisons),("narrative_changes",changes)]:
        qloo.write_csv(ROOT / "tables" / (name+".csv"),rows)
    counts=Counter(x["data_bucket"]+"_data/"+x["narrative_bucket"]+"_narrative" for x in changes)
    part=read_csv("partnerships")
    summary={"faithful_comparisons":len(changes),"quadrants":{a+"_data/"+b+"_narrative":counts[a+"_data/"+b+"_narrative"] for a in ["small","middle","large"] for b in ["small","middle","large"]},
             "partnership_median_distance_to_equal_rank_mix":median(float(x["distance_to_equal_rank_mix"]) for x in part),
             "independent_human_ratings":0}
    qloo.save_json(ROOT / "tables" / "narrative_summary.json",summary)
    lines=["# LLM versus Qloo: evidence, not a quality contest", "",
           "The LLM-only suggestions were frozen before this run's Qloo recommendations. Both outputs are from one assistant drafting pass under the fixed protocol. No human ratings have been collected. Literal overlap is not accuracy, and novel names are not proof of useful novelty.", "",
           "This is not a fair predictive benchmark yet: Qloo selects from 45 brands and 19 TV titles; the LLM can name anything, including an input brand. The TV panel was selected from the original Qloo contrasts. The original demo description was already known to the LLM author. A second study must equalize candidate access or compare unrestricted recommendations from both methods, using held-out people and interests.", "",
           "## All profiles", "", "| Profile | Qloo brands / TV | LLM-only brands / TV | Eligible? |", "|---|---|---|---|"]
    for r in comparisons:
        lines.append("| "+r["profile"]+" | "+r["qloo_brands"].replace(" | ",", ")+" / "+r["qloo_tv"].replace(" | ",", ")+" | "+r["llm_brands"].replace(" | ",", ")+" / "+r["llm_tv"].replace(" | ",", ")+" | "+("Yes" if r["faithful_inputs"] else "No: Dune ignored")+" |")
    lines += ["", "## Change in the evidence versus change in the description", "",
              "Named-content distance is Jaccard distance between the six named suggestions. It is not a semantic or psychological measure. Data distance is the mean of two fixed-panel rank distances. Thresholds were frozen in NARRATIVE_PROTOCOL.md.", "",
              "| Swap | Mean data D | Named-content distance | Category |", "|---|---:|---:|---|"]
    for r in changes:
        lines.append(f"| {r['a']} to {r['b']} | {r['mean_data_distance']:.3f} | {r['qloo_named_content_distance']:.3f} | {r['data_bucket']} data / {r['narrative_bucket']} narrative |")
    lines += ["", "The original replacement and the other two original-profile variants are large/large. The mainstream and brand-heavy swaps are middle/large. The gaming swap is small/middle. There are zero small/large and zero large/small examples under the frozen cutoffs; those quadrants cannot be populated honestly.", "",
              "The brand-heavy pair retains the identical top-five TV set but changes one of the three TV names in the summary. This is a visible compression effect from showing three names. Rank-3/rank-4 native score gaps are in tables/narrative_cutoff_gaps.csv; these are within-query diagnostics, not calibrated uncertainty or comparable probabilities.", "",
              "The constrained narratives contain only returned recommendation names and tentative exploration language. This prevents most personality overclaiming by design; it does not test an unrestricted storyteller or recreate Qloo's demo prompt. No stochastic narrative repeats were run. Potentially counterintuitive outputs, such as fashion brands from the Monster substitution and PlayStation from a Nintendo-game input, are data leads requiring user judgment, not evidence that the person's identity changed.", "",
              "## Independent checks and pending validation", "",
              "Qloo's unrestricted Severance-alone output ranks Apple Inc. second. [Apple's official Severance page](https://www.apple.com/tv-pr/originals/severance/) confirms the association. Both the Joe Rogan person and podcast singleton outputs rank Onnit first; [Onnit's Joe Rogan publication](https://onnit.s3.amazonaws.com/digital-downloads/ebooks/Joe%20Rogan%20-%20The%20Facts%20of%20Life.pdf) independently documents that association. These are two post-hoc relationship sanity checks, not held-out consumer predictions. The frozen LLM-only original Rogan case also suggests Onnit, so that observation supplies no evidence of Qloo's superiority. Neither check establishes relevance to a person with the mixed interests.", "",
              "Give evaluation/BLINDED_PACKET.md to evaluators without evaluation/answer_key.json or these results. The packet standardizes wording, randomizes option labels deterministically and leaves all ratings blank. It tests hypothetical-profile coherence and potential usefulness; it cannot establish personal prediction accuracy unless the evaluator actually has those interests. Run a separate matched-input test with real volunteers before a product decision."]
    (ROOT / "LLM_VS_QLOO.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    make_packet(grounded,baseline)
    print(qloo.canonical(summary))


def make_packet(grounded,baseline):
    out=ROOT / "evaluation"; out.mkdir(exist_ok=True)
    seed="whole-personality-blind-v1-2026-10-08"
    chosen=["p01","p02","p04","p05","p07","p09"]
    chosen.sort(key=lambda p:hashlib.sha256((seed+"/order/"+p).encode()).hexdigest())
    packet=["# Cultural suggestions: evaluation packet", "",
            "Six hypothetical interest combinations follow. For each, compare A and B without looking up how they were produced. Both use the same wording. Score suggestions, not writing style. Do not assume these interests describe you or imply a person's demographics, politics, health or personality.", "",
            "Use an anonymous evaluator ID. Complete feedback.csv with one row per case and option. Relevance, useful specificity, novelty, entertainment and willingness to share: 1 (low) to 5 (high), blank if unable to judge. List any unsupported claims, counterintuitive suggestions and reasons. Mark a single preferred option per case: A, B, equal, or neither. Familiarity with the input interests: none/some/all. Do not reward unfamiliar suggestions just for being surprising.", "",
            "For an exploratory self-check, you may add explicit like/dislike/unknown reactions to each named suggestion in the notes, clearly labeled as your own tastes. These are not proof about a hypothetical audience. Please do not consult the answer key until all ratings are saved.", ""]
    key=[]; rows=[]
    for i,pid in enumerate(chosen,1):
        case=f"case_{i:02}"
        methods=[("Qloo-grounded",grounded[pid]),("LLM-only",baseline[pid])]
        if int(hashlib.sha256((seed+"/option/"+pid).encode()).hexdigest(),16)%2:
            methods.reverse()
        packet += ["## "+case, "", "Interests: "+", ".join(grounded[pid]["interests"])+".", ""]
        for label,(method,record) in zip(["A","B"],methods):
            packet += ["**Option "+label+".** "+normalized_summary(record), ""]
            key.append({"case":case,"option":label,"profile":pid,"method":method})
            rows.append({"evaluator_id":"","case":case,"option":label,"input_familiarity":"","relevance_1_5":"",
                         "useful_specificity_1_5":"","novelty_1_5":"","entertainment_1_5":"","willingness_to_share_1_5":"",
                         "unsupported_claims":"","counterintuitive_suggestions":"","preferred_option_A_B_equal_neither":"","reason_or_personal_reactions":""})
    (out / "BLINDED_PACKET.md").write_text("\n".join(packet)+"\n",encoding="utf-8")
    # Keep human feedback immutable on subsequent analysis runs.
    feedback=out / "feedback.csv"
    if not feedback.exists():
        qloo.write_csv(feedback,rows)
    qloo.save_json(out / "answer_key.json",{"withhold_from_evaluators":True,"shuffle_seed":seed,"assignments":key})


if __name__=="__main__":
    main()
