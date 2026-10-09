# Civilizr: Qloo feasibility experiment 1

Written before implementation, 2026-10-07. Research harness only; no product, UI,
economic data, composite maturity score, or assumption that named areas are culturally superior.

## Question and falsification

Can Qloo provide reproducible, geographically distinct cultural profiles at the
scale of Orlando neighborhoods? Even a successful result cannot establish that
culture leads prices: temporal and economic validation would be a later experiment.

The test set is Winter Park, College Park, Audubon Park, Mills 50, Baldwin Park,
plus **Pine Hills and Azalea Park** as tentative contrast controls. Their role is
an experimental selection, not a verified claim about affluence or culture.
Orlando is a broad-area baseline. Winter Park and the controls may resolve to
larger administrative areas than the named Orlando neighborhoods; record this
scale mismatch and never silently treat them as equal-area samples.

## Smallest tests first

1. **Smoke, 5 requests:** search Winter Park, Mills 50 and Pine Hills as locality
   entities; inspect place tag types; request place-related taste tags for the
   named Winter Park locality as a capability probe. A fuzzy match is not proof
   of correct geography. Stop on missing credentials or authentication failure.
2. **Discovery:** resolve all eight areas, inspect names, IDs, subtype, geocode,
   and returned geometry; retain ambiguous/unresolved areas as missing. Never
   replace Mills 50 with Orlando or select the first search hit automatically.
   Discover Qloo tags for the candidate cultural dimensions. Freeze reviewed
   locality IDs and exact taxonomy IDs with source response paths before profiling.
3. **Pilot:** after geographic review, compare Winter Park, Mills 50 and Pine Hills
   for place taste tags, brands and destinations. Keep output universes, take,
   trend bias and all other parameters identical. Also request Orlando, a no-location
   baseline, and an uncached repeat of Winter Park. Treat errors or unsupported
   dimensions as missing, not zeros. Check whether tags actually have affinity scores.
4. **Expand only if useful:** run the same profiles for all areas. Split food,
   coffee, fitness, arts and nightlife only where the discovered taxonomy supports
   it. Local place inventories are a separate supply diagnostic; distinct POIs
   across disjoint geofences are not evidence of distinct audience preferences.
5. **Optional probes:** feature.explainability on/off for the same query; one
   heatmap per frozen tag over the same Orlando extent; brand trending plus a
   short entity time series. Do not interpret global entity trends as neighborhood
   change. Entity-seeded explainability, if needed, is a separate diagnostic and
   must not contaminate the location-only fingerprints.

## Comparison and practical gates

Use each domain separately. Export ranked lists and raw scores; do not subtract
query-normalized affinity scores between neighborhoods. For top-k results export
binary membership and reciprocal-rank vectors over the union of returned IDs,
Jaccard overlap and cosine similarity of reciprocal ranks. Missing from top-k
means unobserved below the cutoff, not zero actual affinity. Reject incomplete,
failed, empty or unscored profiles from the matrix. Compare k=10 and k=20 where
enough rows exist; flag ties, since arbitrary tie ordering can create false signal.
Also export rank differences against each control (descriptive, not statistical lift).

Provisional screening rules, fixed before seeing results:

- Fewer than five distinct, verified target/control geographies: coverage insufficient.
- At least two independent non-inventory domains must yield 20 unique, scored
  results across those areas, including at least one contrast control.
- Same-query top-20 repeat overlap should be at least 0.90. Differences between
  areas should exceed repeat noise; a top-20 Jaccard of at most 0.70 for some
  target/control pairs in both domains warrants a second test, not a product build.
- If location outputs resemble the Orlando/no-location baseline, locality IDs
  collapse, or only nearby venue lists differ, evidence is weak for this hypothesis.
- These are practical gates, not significance tests. Seven selected areas cannot
  validate a market indicator. Sensitivity to borders, different spatial scales,
  sparse coverage, visitor activity and Qloo smoothing remain alternative explanations.

## Reproducibility and constraints

Python standard library; sequential requests; timeout, bounded retries and a hard
attempt budget. Save exact endpoint/parameters, UTC time, configuration and code
hashes, HTTP status, raw response and per-attempt log. Resume the same run without
reissuing successful requests; use a new run directory for independent repeats.
No key in logs, URLs, manifests or version control. No automatic paid services,
bulk scraping, real-estate datasets, or UI.

See [API_NOTES.md](API_NOTES.md) for source links, parameter semantics and known
documentation conflicts. Live access, geographic coverage and taxonomy remain
unverified until authenticated requests succeed.
