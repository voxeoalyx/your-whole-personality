# Civilizr: Qloo experiment 1 findings

**2026-10-07 — Continue research; do not build Civilizr yet.** Qloo returned
distinct, immediately reproducible cultural profiles for six resolved areas.
That supports a small second experiment, but does **not** establish cultural
maturity, cultural change, or a leading indicator of housing-market outcomes.
Geographic definition and uneven coverage are substantial unresolved confounds.

The run made **95 HTTP attempts: 87 returned 200**, including some empty or unscored
results. It used only Qloo, no economic data, with no composite score or UI.
All requests, failures and raw responses are saved under `runs/`; the method was
specified in [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md) before implementation.

## What Qloo distinguished

Winter Park, College Park, Audubon Park, Baldwin Park, Pine Hills and Azalea Park
resolved to distinct Qloo locality polygons. Pine Hills and Azalea Park were
tentative contrast controls, not ground-truth labels of economic or cultural status.
Winter Park and the controls have different administrative scales from the Orlando
neighborhoods; this is not an equal-area comparison.

The following are **recommendations associated with each location signal**, not
claims that every named business is physically inside that area:

| Area | Illustrative observed results | Limitation |
|---|---|---|
| Winter Park | Rifle Paper Co. ranked #3 among brands; The Ravenous Pig #1 for dining; Barnie's #1 for coffee | Whole-locality and center-point brands differed substantially |
| College Park | Rifle Paper Co. #4; Infusion Tea #1 dining | Brand list close to Winter Park and Baldwin Park |
| Audubon Park | Rifle Paper Co. #3; The Guesthouse #1 dining | Only 4 coffee, 0 fitness and 8 bar results; generic tags included Church and Place |
| Baldwin Park | Rifle Paper Co. #6; Seito Sushi Baldwin Park #1 dining | Shared 18/20 brands with College Park |
| Pine Hills | Johnny Dang & Co. #3, Sniper Gang Apparel #4; Chili's #1 dining | Differences can reflect geography or model coverage, not maturity |
| Azalea Park | Full Sail University #4; Dave & Buster's Orlando #1 dining | Tourism and regional associations feature prominently |
| Mills 50 | No valid locality match. A separate point proxy near a Qloo-listed business returned brands led by Orlando City SC and Universal Orlando Resort | This is not a verified Mills 50 neighborhood fingerprint |

Evidence: [per-area top results and raw-file references](reports/neighborhood_top5.csv),
[reviewed localities](localities.json), [all scored results](runs/11-final/results.csv).
Three locality searches failed to identify Mills 50: a qualified query returned
Orlando, and scoped `Mills 50` / `Mills50` queries returned empty lists. A place lookup
found businesses, allowing a separately labeled 500/1,000 m proxy around a Qloo
coordinate on Colonial Drive. No Orlando-wide fallback was accepted as Mills 50.

## Which dimensions worked

All place-category queries used the **same 20 km candidate region** centered on
Qloo's Orlando coordinate, changing only the input location. This avoids comparing
disjoint inventories, but proximity and spatial modeling can still explain differences.
Categories came from actual Qloo taxonomy responses. Museums, fitness centers and
bars are narrow proxies for arts, wellness and nightlife, respectively.

| Dimension | Complete top-20 areas / 6 | Median target–control Jaccard at 20 | Assessment |
|---|---:|---:|---|
| Brands | 6 | 0.18 | Clearest non-venue contrast; includes teams, colleges and health systems, not just retail |
| Food/dining | 6 | 0.11 | Strong venue differentiation; substantial proximity confound |
| Coffee/cafes | 5 | 0.21 | Potentially useful, but Audubon coverage fails |
| Broad place tags | 6 | 0.38 | Different but often generic, mixed namespaces, difficult to interpret |
| Bars | 5 | 0.33 | Some contrast, overlap with dining; Audubon incomplete |
| Destinations | 6 | 0.78 | Weak separation; dominated by shared Florida destinations |
| Fitness centers | 0 | — | 0–13 results per area; inadequate for a six-area top-20 comparison |
| Museums | 0 | — | 6–9 results; narrow, largely shared venue pool |

Jaccard is intersection/union: lower values mean less list overlap, **not higher
cultural maturity**. Medians use eight target–control pairs, or six where Audubon
is incomplete. No significance or population inference is claimed. Full values:
[dimension summary](reports/dimension_summary.csv).

Winter Park's uncached, same-session repeats were identical for brands, place tags
and destinations. Winter Park versus Pine Hills shared **4/20 brands**, **11/20
place tags**, but **19/20 destinations**. These complementary outputs passed the
initial coverage/repeat screening gates; they are not statistically independent
samples, and an immediate repeat may reflect server caching or a stable snapshot.

## Simple neighborhood similarity

Brand top-20 Jaccard, using six verified locality inputs:

| | Winter Park | College Park | Audubon Park | Baldwin Park | Pine Hills | Azalea Park |
|---|---:|---:|---:|---:|---:|---:|
| Winter Park | 1.00 | 0.74 | 0.48 | 0.74 | 0.11 | 0.29 |
| College Park | 0.74 | 1.00 | 0.54 | 0.82 | 0.11 | 0.29 |
| Audubon Park | 0.48 | 0.54 | 1.00 | 0.54 | 0.11 | 0.25 |
| Baldwin Park | 0.74 | 0.82 | 0.54 | 1.00 | 0.11 | 0.29 |
| Pine Hills | 0.11 | 0.11 | 0.11 | 0.11 | 1.00 | 0.21 |
| Azalea Park | 0.29 | 0.29 | 0.25 | 0.29 | 0.21 | 1.00 |

Source: [brand matrix](reports/brands_jaccard20.csv). Separate domain matrices,
reciprocal-rank cosine at k=10/20, sparse fingerprints and control rank contrasts
are saved in [combined evidence](runs/11-final/evidence.md). Absent top-k IDs are
censored observations, not zero affinity. Score ties make rank cosine less reliable.

**Geographic robustness is not established.** Winter Park's polygon versus its
Qloo center-point shared just **9/20 brands** (Jaccard 0.29); College Park shared
13/20 (0.48). Changing a whole locality to a small central area changes the sampled
geography, so this is not an API inconsistency—but it matters for any neighborhood
label. The Mills 50 proxy shared 17/20 across 500 and 1,000 m, without verifying
the district boundary. [Geometry sensitivity](reports/geometry_sensitivity.csv).

## API limitations actually encountered

- The supplied key works on `hackathon.api.qloo.com`; production returned 401.
- Geography-only explainability returned no explanation metadata. Adding two
  interest entities produced contribution metadata, which explains those inputs,
  not the origin or reliability of the geographic signal.
- `/trends/category` and `/trends/entity` returned 404 on this host. `/v2/trending`
  returned an empty Rifle Paper Co. series for 2026-09-09 through 2026-10-07.
  This is inconclusive about other entities/dates or production access. No useful
  neighborhood trend was obtained. Returned `audience_growth=0` is not evidence
  that a neighborhood has stopped growing.
- Default heatmaps worked for all five place categories: 1,150–1,522 cells, all
  six-character geohashes. Raw cells and affinity/popularity values are exported.
  Locality output required an undocumented-in-the-prose enum correction to
  `urn:entity:locality`, then returned 500 twice. No neighborhood aggregation was
  inferred from the grid. Some cells had zero popularity alongside high affinity.
- The no-location tag request returned unscored taxonomy; bare brand/destination
  requests returned 400. Orlando destination insights returned 200 with no entities.
  A usable universal no-location preference baseline was not obtained.
- Affinities are query-normalized and commonly near 1; popularity is a percentile,
  not spend or growth. Responses inspected did not provide usable neighborhood
  observation counts, confidence intervals or freshness sufficient to assess coverage.

Source requests: [diagnostics](plans/diagnostics.json), [sensitivity](plans/sensitivity.json),
[API documentation and caveats](API_NOTES.md), [heatmap coverage](reports/heatmap_coverage.csv).

## Decision and experiment 2

**Qloo did not fail the basic “can it produce different profiles?” test. It has
not passed the more demanding “useful cultural leading indicator” test.** Close
neighborhoods can look similar; sparse responses and boundary choices can drive
apparent differences. Nothing here establishes that one taste profile is more
mature, more desirable, or ahead of housing fundamentals.

Experiment 2 should remain Qloo-only initially: freeze comparable spatial units
(including a defensible Mills 50 boundary), test modest boundary/center shifts,
and compare a fixed union of brand/tag candidates using `filter.results.entities`
and `filter.results.tags`. Include nearby areas not chosen for a presumed contrast,
repeat on separate dates, and test whether separation survives excluding obvious
local teams/institutions and accounting for distance to recommended venues. Ask
Qloo about coverage, freshness, effective spatial resolution and historical access.

Proceed to economic data only if between-area differences consistently exceed
within-area boundary/time sensitivity in at least two usable domains. A later
out-of-time housing test must compare predictive value against simple geography,
amenity and prior-price baselines. Otherwise stop or narrow the hypothesis.
