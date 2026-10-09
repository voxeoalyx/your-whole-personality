# Civilizr Experiment 2: STOP / RETHINK

**Recommendation for the October 30 hackathon: move on from this Civilizr hypothesis.
The evidence does not justify building a cultural real-estate leading indicator,
and the cross-city matching test does not yet justify that pivot either.**

Qloo returned stable, geographically differentiated outputs, but we did not establish
an information advantage. Fixed panels exposed missing coverage; the most broadly
usable domain was weak and sensitive to which categories were included. A 200 m
College Park center shift exceeded the median between-neighborhood food difference. Cross-city
matches were largely generic. The independent venue baseline was too sparse at
the two original controls to resolve incremental information convincingly.

This is a negative feasibility decision for the **tested method and account**, not
proof that all Qloo applications or alternative taxonomies are unhelpful. No economic
outcome, cultural maturity, temporal lead, or predictive value has been demonstrated.

## What ran

On 2026-10-07, **80 new Qloo HTTP attempts all returned 200**, including empty and
incomplete results. We used nine Orlando proxies, three Atlanta proxies, fixed
47-brand and 28-tag requests, geometry perturbations, candidate subsets and four
requests repeated without the local cache. One free Overpass request supplied an
independent snapshot of actual mapped venues. No UI, paid data, added Python packages,
database or product was built. Experiment 1 files and responses remain intact.

The [plan](EXPERIMENT_2_PLAN.md) was saved before the new Qloo calls; its SHA-256 is
recorded in run manifests. [Protocol departures](experiment2/DEVIATIONS.md) are explicit.
Raw results, omissions, request parameters, timestamps and code hashes are in
`experiment2/runs/`; the [run guide](experiment2/README.md) explains offline analysis
and deliberate future repeats. Fourteen offline tests passed, including missingness,
ties, geometry, inventory distance, baseline fitting and the existing request safeguards.

## Comparable geography, with qualified neighborhood labels

Every primary unit is a 1,000 m, 32-vertex polygon of approximately **3.121 km²**.
Mills 50 and Thornton Park use official City district address coordinates; six
original areas use reviewed Qloo locality coordinates. City District uses a labeled
downtown point proxy after both CBD lookups failed. Atlanta uses centroids of official
City polygons. We retained boundary references and the original Atlanta geometry,
but did not equate differently sized administrative areas.

City District and Thornton Park were chosen by a fixed hash from the remaining
City Main Streets list before new profiles, not because of expected results. That
frame still favors commercial districts and is not a random metropolitan sample.
Proxy labels, water/residential coverage and overlapping units limit interpretation.
[Coordinates, areas and sources](experiment2/GEOGRAPHY.md),
[machine-readable geography](experiment2/geographies.csv).

## Fixed panels substantially weaken the original contrast

Candidates are actual Qloo IDs. The brand panel combines 24 brands drawn by hash
from the audited Experiment 1 pool with all 25 eligible brands from a location-free
high-popularity lookup, with two overlapping IDs. Teams, universities, hospitals,
attractions and conservatively identified regional brands were removed **before**
new geographic scoring. Rifle Paper Co., Publix and Tijuana Flats are among the
exclusions. The independent and pooled brand subsets are sensitivity checks, not
two independent cultural domains. [Full candidate audit](experiment2/candidate_audit.csv).

Primary dissimilarity is `(1 - Spearman rank correlation) / 2` on the same complete
panel, with average ranks for ties. Missing scores are not zeros. Native affinities
are retained, but never treated as absolute cross-location demand measurements.

| Frozen panel | Candidates | Complete Orlando profiles | Median between-area dissimilarity | Assessment |
|---|---:|---:|---:|---|
| Brands, full | 47 | 5/9 | 0.0458 | Coverage fails; median below the 0.05 screen |
| Brands, independent subset | 25 | 5/9 | 0.0204 | Mostly similar rankings; not another domain |
| Brands, pooled subset | 24 | 8/9 | 0.0622 | Strongest selected-panel contrast, but Pine Hills still incomplete |
| Food/dining/coffee | 12 | 9/9 | 0.0437 | Coverage passes; differentiation and candidate-stability screens fail |
| Arts/culture | 8 | 0/9 | Not computed | Children's museum tag absent; do not substitute a post-selected panel |
| Wellness/fitness | 8 | 0/9 | Not computed | Martial arts school and physical fitness program tags absent |

Medians use only valid pairs: 10 full-brand pairs, 28 pooled-brand pairs and 36 food
pairs. They must not be compared as though all panels used the same neighborhoods.
The coverage gate required at least eight complete Orlando profiles and all three
primary sensitivity areas. Only food passed that gate; **zero domains passed the
full prespecified screen**. The 0.05 threshold is a pragmatic planning rule, not a
scientific discontinuity; candidate instability and coverage matter more than food's
small numerical miss. [Coverage](experiment2/reports/coverage.csv),
[domain summary](experiment2/reports/domain_summary.csv).

Pine Hills received 40/47 brands; College Park and Mills 50 received 46/47, and
Azalea Park 45/47. Samsung was missing in all four; Pine Hills also lacked six other
brands. Explicit missing-only requests returned empty lists. The API's fixed-output
filter restricts candidates but did not produce a fully scored matrix here.
The arts/wellness failures apply to these specific frozen tags, not every possible
arts/wellness taxonomy. Keeping the failed panels visible avoids cherry-picking.

There are descriptive differences. Food's strongest pair, College Park–Pine Hills,
had dissimilarity **0.140** (rho 0.720), while the median pair had rho **0.913**.
Coffee shop ranked first in Winter Park, College Park, Audubon Park and Baldwin Park;
hamburger restaurant ranked first in Pine Hills. Yet seven areas shared the same
three top categories—coffee shop, Mexican and bakery—in different orders. This is
limited categorical differentiation, not evidence of cultural advancement.
[Full fixed fingerprints](experiment2/reports/fixed_fingerprints.csv),
[food similarity matrix](experiment2/reports/food_spearman_matrix.csv).

## Robustness: favorable geometry checks, unfavorable candidate checks

- Winter Park, Mills 50 and Pine Hills retained exactly the same returned scores
  under 800/1,000/1,200 m polygons and 200 m east shifts. Their valid full panels
  therefore have zero measured within-area rank distance. Incomplete panels remain
  incomplete; equality of partial outputs does not repair coverage.
- The supplementary six-area shifts found an important exception: **College Park's
  food dissimilarity changed by 0.0559**, greater than the overall median between-area
  difference of 0.0437 and equal to its nearest other-area difference. Its pooled
  brand distance changed 0.0157. The other five supplementary areas were stable
  on valid panels. Thus primary-test stability does not generalize to every center.
  This new observation does not retroactively alter the primary gate calculations.
- Same-center POINT + explicit 1,000 m radius diagnostics also matched their polygon
  outputs. Atlanta's 200 m shifts were stable. This supports **local output stability**,
  but cannot distinguish fine spatial resolution from aggregation, smoothing or
  server caching. It does not erase Experiment 1's whole-locality versus small-area
  differences. [Sensitivity table](experiment2/reports/geographic_sensitivity.csv).
- All four immediate repeat requests returned identical result objects, including
  the same omissions. No historical stability claim is possible.
  [Repeat equality](experiment2/reports/repeat_request_equality.csv).
- Food's two deterministic six-category halves produced pair-distance ordering
  correlations of **0.544 and 0.661** against the full panel, both below the planned
  0.70 warning threshold. Actual reduced-panel reissues preserved rankings of the
  retained items: the warning concerns which attributes define similarity, not
  demonstrated nondeterminism in Qloo's scoring.
- Rank-based versus standardized-score-based pair ordering agreed only **0.670**
  for food and **0.273** for the full brand panel. The independent brand subset was
  especially metric-sensitive (0.042). Pooled versus independent brand distance
  orderings agreed 0.721 on their ten common complete pairs, but their typical
  differentiation and coverage differed. These similarities are method-dependent.
  [Candidate checks](experiment2/reports/candidate_sensitivity.csv).

## The baseline challenge remains unresolved

**A: geographic distance.** Pairwise geographic versus Qloo dissimilarity correlation
was **0.236 for food** and **0.539 for full brands** (only five complete areas).
Distance alone is not a strong account of the observed food ranking variation.
That finding is not evidence that the remaining variation is useful culture.

**B: actual venue inventory.** OSM supplied 4,806 raw features in the requested
extent. We classified relevant actual mapped venues, applied the same polygons,
and deduplicated same-name/category features within 30 m. We did not use Qloo
recommendations as inventory. Counts are:

| Proxy | Mapped venues after deduplication |
|---|---:|
| Winter Park | 50 |
| College Park | 18 |
| Audubon Park | 17 |
| Baldwin Park | 10 |
| Pine Hills | 1 |
| Azalea Park | 0 |
| Mills 50 | 104 |
| Thornton Park | 106 |
| City District | 126 |

These are selected mapped categories, not verified totals of operating businesses.
The control counts may reflect residential center placement, mapping omissions or
both; they cannot establish an absence of commerce. We have no efficient independent
completeness audit. Way/relation bounding-box centers and category mapping add error.
Qloo's FAQ also cites OSM as a supplementary source, so independent retrieval does
not guarantee independent upstream data.
[Venue counts](experiment2/reports/inventory_counts.csv),
[individual source-linked venues](experiment2/reports/inventory_venues.csv).
Inventory data: **© OpenStreetMap contributors**, [ODbL](https://www.openstreetmap.org/copyright).

**C: fixed Qloo fingerprints against both baselines.** Inventory-composition distance
had correlation **0.165** with food dissimilarity over nonempty inventories. Small
linear baseline models were evaluated by withholding every pair touching one
neighborhood, avoiding the obvious pair leakage from a random row split.

| Food comparison scope | Areas / pairs | Geography held-out R² | Inventory held-out R² | Both held-out R² |
|---|---:|---:|---:|---:|
| All available for each model | 9/36 geography; 8/28 others | 0.033 | 0.029 | -0.081 |
| Same seven proxies with >=10 mapped venues | 7/21 | 0.006 | -0.414 | -0.409 |

R² here measures error reduction against each fold's training-mean Qloo-distance
predictor. Negative values mean worse prediction, not an inverse cultural signal.
These are tiny-sample diagnostics with dependent pairs; no population significance
test is claimed. The predictors include geographic log distance, venue-category
Hellinger distance and log count difference. There is no trained cultural scoring model.
[Baseline comparisons](experiment2/reports/baseline_cross_validation.csv).

The largest positive food residuals in the seven-area comparison involved College
Park versus City District, Thornton Park and Mills 50: observed dissimilarities
0.105, 0.101 and 0.084 versus mean held-out predictions 0.034, 0.035 and 0.031.
College Park's supplementary center shift changed its food profile by 0.0559,
so these residual contrasts are not secure evidence of a neighborhood-level trait.
Candidate dependence and unvalidated cultural meaning also remain. Low baseline explanatory power can reflect
bad inventory measurement, nonlinear relationships or Qloo noise. **Residuals are
not an information advantage.** We lack an external outcome or blinded cultural
judgment showing that these residuals are useful.
[Residual contrasts](experiment2/reports/baseline_residual_contrasts.csv).

## Cross-city analogues: technically possible, not validated or distinctive

Three Atlanta proxies were fixed in advance: Midtown, Inman Park and West End.
The same nonlocal candidates and equal-area geometry were used. Food was complete
for all three; West End lacked one full-panel brand, leaving only two full-brand
comparators. No local team or institution was reintroduced to manufacture matches.

**All nine Orlando food profiles selected Midtown**, with rho 0.797–0.986. The
leave-one-area-out mean Orlando fingerprint also selected Midtown every time.
Shared leading attributes were usually bakery, coffee shop and Mexican. Runner-up
distance margins were only 0.0035–0.0245.

The matches survived both Orlando and Atlanta 200 m shifts, but **every Orlando
food profile switched to Inman Park under one deterministic half-panel**; the other
half selected Midtown. That is strong evidence of generic, candidate-dependent
matching in this test, rather than nine independently meaningful analogues.

Brands offer some differentiated descriptive matches: Audubon Park and Baldwin Park
chose Inman Park on the full panel, while Winter Park and the downtown proxies chose
Midtown. But the pooled brand subset chose Inman Park for all eight eligible Orlando
areas, matching its generic-profile choice; the independent subset changed Baldwin's
match to Midtown. Missing West End/full-panel coverage further limits competition.
No outside judgments validated these pairings.
[All matches and sensitivity](experiment2/reports/cross_city_matches.csv).

## Provenance and remaining limitations

Official documentation supports adaptive geohash inference, mixed interaction and
metadata sources, and query-normalized scores. It does not establish effective
resolution, resident representation, local data vintage or usable historical
neighborhood panels for these requests. New responses contain an undocumented
`query.geospatial.panel_size` field; values reach billions and must not be labeled
unique people, confidence or effective sample sizes without a definition.

The [provenance review and technical questions](experiment2/PROVENANCE.md) cover
that field, missing-candidate semantics, identical small-boundary outputs, proximity
contribution, freshness, historical access, explainability and commercial derived-data
rights. Account-specific caching, attribution and public score-display permissions
remain unconfirmed. No Qloo team messages were sent, and nothing was published.

## Decision against the frozen gates

| Outcome | Evidence |
|---|---|
| GO | **Fails.** No two adequately covered domains pass differentiation and robustness screens; incremental usefulness beyond both baselines is not demonstrated. |
| NARROW | **Not supported yet.** Stable food rankings are technically usable, but matching is generic and candidate-dependent; selected brand contrasts lack broad complete coverage and validation. |
| STOP / RETHINK | **Best fit.** Sparse fixed scoring, weak/generic differentiation, candidate dependence and the College Park center sensitivity undermine the method. Stability elsewhere and exact repeats are favorable but insufficient. |

For October 30, allocate effort to another hypothesis. Do not add housing data or
build a Civilizr interface on top of these results. Do not sell the Atlanta nearest
matches as validated neighborhood analogues.

If Qloo can first explain the missingness and effective spatial footprint, a small
follow-up worth considering would use a location-independent panel they confirm can
be fully scored, independently audited venue inventories, and blinded held-out
neighborhood judgments. Fix the success metric before those judgments and require
Qloo to beat geography and inventory on new neighborhoods. That would test actual
incremental usefulness; another attractive similarity matrix would not.
