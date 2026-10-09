"""Conservative tie-aware research metrics; no dependencies or network."""
import math
from statistics import mean
from experiment import ROOT, qloo, items


def load(ref):
    folder, name = ref.split("/")
    meta = qloo.read_json(ROOT / "runs" / folder / (name + ".meta.json"))
    return qloo.read_json(ROOT / "runs" / folder / meta["raw_file"])


def scores(payload):
    return {x.get("entity_id",x.get("id",x.get("tag_id"))): x["query"]["affinity"] for x in items(payload)
            if x.get("entity_id",x.get("id",x.get("tag_id"))) and isinstance(x.get("query", {}).get("affinity"), (int, float))
            and math.isfinite(x["query"]["affinity"])}


def invalid_inputs(payload):
    return [entity for w in payload.get("warnings", []) if w.get("type")=="not_found"
            for entity in w.get("signal.interests.entities", [])]


def ranks(v):
    ordered = sorted(enumerate(v), key=lambda p: p[1])
    result = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i + 1
        while j < len(v) and ordered[i][1] == ordered[j][1]:
            j += 1
        for k, _ in ordered[i:j]:
            result[k] = (i + 1 + j) / 2
        i = j
    return result


def rho(a, b):
    if len(a) != len(b) or len(a) < 2:
        return None
    a, b = ranks(a), ranks(b)
    am, bm = mean(a), mean(b)
    denom = math.sqrt(sum((x-am)**2 for x in a) * sum((y-bm)**2 for y in b))
    return sum((x-am)*(y-bm) for x,y in zip(a,b)) / denom if denom else None


def compare(a, b, expected):
    ids = sorted(set(expected))
    paired = set(ids) & a.keys() & b.keys()
    result = {"n_expected": len(ids), "n_paired": len(paired), "complete": len(paired) == len(ids), "rho": None, "distance": None, "top5_jaccard": None}
    if len(paired) != len(ids):
        return result
    r = rho([a[i] for i in ids], [b[i] for i in ids])
    if r is None:
        return result
    def top(v):
        cutoff = sorted((v[i] for i in ids), reverse=True)[min(5, len(ids))-1]
        return {i for i in ids if v[i] >= cutoff}
    x, y = top(a), top(b)
    result.update(rho=r, distance=(1-r)/2, top5_jaccard=len(x & y)/len(x | y))
    return result


def equal_rank_mix(a, b, ids):
    if not set(ids) <= a.keys() & b.keys():
        return {}
    ra, rb = ranks([a[i] for i in ids]), ranks([b[i] for i in ids])
    return {k:(x+y)/2 for k,x,y in zip(ids,ra,rb)}
