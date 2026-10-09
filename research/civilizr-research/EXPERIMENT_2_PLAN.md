# Experiment 2: does the cultural signal survive controls?

Frozen before new Qloo requests on 2026-10-07. Experiment 1 remains untouched.
This is a feasibility screen, with no UI, economic data, maturity score, or claim
that cultural differences predict housing outcomes.

## Design and stopping rules

1. First probe fixed-candidate scoring on Winter Park and Pine Hills. Require
   the requested IDs, numeric affinities, no duplicates, and no unexpected IDs.
   An omitted candidate is missing, never zero. If a domain cannot return a
   complete panel, retain its coverage table but exclude it from comparisons.
   Allow at most two documented parameter repairs, then stop that route.
2. Use the original seven Orlando areas plus **City District and Thornton Park**.
   The additions are the first two SHA-256 hashes of `civilizr-exp2:<name>` over
   the nine remaining districts on the City's Main Streets list. The sampling
   frame and hashes will be saved; selection uses no Qloo result or stereotype.
3. Primary geography: equal-radius 1,000 m, 32-vertex regular polygons centered
   on reviewed Qloo locality coordinates (original areas) or official City
   district anchors (Mills 50 and additions). These are explicitly **central-area
   proxies**, not whole neighborhoods. Save authoritative boundary references
   where available; do not digitize PDF borders by guesswork. Prefer official
   digital polygons for reference/supplementary checks if readily obtainable.
   Equal-area proxies are necessary because cities, districts and neighborhoods
   have different administrative scales. Save actual geometry, area, center,
   coordinate source, and limitations. Water, borders and overlapping proxies
   are not independent resident populations.
4. Sensitivity: Winter Park, Mills 50 and Pine Hills each get 800 m, 1,200 m and
   a 200 m eastward center shift with radius held at 1,000 m. Quantify changes
   against every area's nearest and median between-area differences.
5. Fixed brands/lifestyle panel: audit the pooled Experiment 1 brand union,
   excluding local teams, academic/health institutions, attractions and obvious
   regional brands; record every exclusion. Add an independent, location-free
   high-popularity brand lookup panel if the API supports it. Freeze candidates
   before main profiles. Report independent and pooled subsets separately.
6. Fixed native tag panel: food/dining/coffee, arts/culture/entertainment and
   wellness/fitness, selected from actual taxonomy without new neighborhood
   affinities. Aim for 8-16 non-geographic tags per domain; avoid synonym aliases.
   Broad genres are imperfect proxies; do not call them independent cultural
   dimensions if the observed data do not support that interpretation.
7. Use identical location-only Insights requests with trend bias off and an
   explicit fixed output list. No interest seeds. Tags can share one request
   to conserve budget; analyze within each domain separately. Save all values.
8. Budget: sequential, resumable, standard-library Python; at most **90 new
   Qloo HTTP attempts** including lookup, repairs and repeats. Expect 60-75.
   Stop on authentication/rate-limit or persistent connection failures; preserve
   partial evidence rather than enlarging the experiment to find a positive.

## Measures fixed in advance

- Primary profile similarity: Spearman correlation over the **same full panel**,
  using average ranks for score ties. Dissimilarity = (1 - rho) / 2. All-tied
  vectors are uninformative, not a perfect match. No absolute affinity subtraction
  across locations: Qloo normalizes by query.
- Secondary: Pearson correlation of within-profile centered scores (equivalent
  to cosine after centering/scaling), explicitly a normalization-sensitive check.
  Compare neighborhood-pair distance orderings between rank and score methods.
- Adequate domain: at least 8 candidates, complete finite scores in at least
  8/9 Orlando proxies, at least 5 distinct score levels per profile, and full
  profiles in all three sensitivity neighborhoods. Coverage is model output
  coverage, not observation counts or evidence of representative sampling.
- Reproducibility: reissue selected Winter Park/Pine Hills requests into a fresh
  run directory. Require rho >= .95. This bypasses the local cache, not any
  server cache; same-session reproducibility is not historical stability.
- Geographic robustness: median within-neighborhood dissimilarity <= 1/3 of
  median between-neighborhood dissimilarity, with worst perturbations and nearest
  neighbors also reported. Meaningful differentiation requires median between
  dissimilarity >= .05. These are pragmatic screens, not significance tests.
- Candidate sensitivity: independent versus pooled brand panels, deterministic
  alternating-ID halves within tags, and selected reduced-panel reissues.
  Report pairwise-distance Spearman agreement; < .70 is a material warning.
  Do not remove poorly performing candidates after seeing results.

## Baseline challenge

**A: geography.** Haversine centroid distance and overlap flags, compared with
Qloo dissimilarities using pairwise Spearman correlations and near/far examples.

**B: inventory.** Obtain one modest OpenStreetMap Overpass snapshot of real POIs
covering the Orlando proxies, using amenity/shop/leisure/tourism tags. Apply the
same polygons locally, export individual source IDs and category counts. Deduplicate
same-name/category representations within 30 m. Export raw and deduplicated counts;
do not fill unmapped businesses or present OSM as a complete business register.
Use category proportions and Hellinger distance; report total counts separately.
Flag fewer than 10 mapped POIs and sparse domains. If retrieval/quality is inadequate,
mark this baseline unavailable or provisional; never substitute Qloo recommendations.

**C: Qloo.** Compare dissimilarity with A and B. Fit simple descriptive linear
models using standardized log(1 + distance km), inventory Hellinger distance and
absolute log count difference. Evaluate by leaving an entire neighborhood out
(all touching pairs excluded from fitting), against a training-mean baseline.
Compare geography only, inventory only and both; clamp no predictions. Report
held-out error, not population p-values from dependent pairs. Residuals are
unexplained variation, **not demonstrated cultural information or predictive value**.
Inspect the largest residual contrasts and whether they survive perturbations.
No external truth about culture is available in this experiment; lack of fit
alone cannot satisfy the information-advantage claim.

## Cross-city secondary probe

Use three Atlanta central-area proxies: Midtown, Inman Park and West End, anchored
to official City neighborhood polygons if accessible, otherwise reviewed Qloo
locality lookups. Selected for a small range of urban contexts before results,
not expected Orlando analogues. Use identical radius and fixed nonlocal panels.
Apply a 200 m east shift to each; test candidate subsets and each domain separately.
Report nearest and runner-up margins, shared rank attributes, local-identifier
exclusions and comparison with the generic mean Orlando fingerprint. A nearest
match among three candidates is not validation; no forced one-to-one matching.

## Predetermined decision

- **GO** requires useful repeatable differentiation beyond both baselines in at
  least two adequately covered domains, with boundary variation materially smaller
  than meaningful between-area differences. This includes evidence that residual
  differences represent useful culture, not merely numerical model residuals.
  Missing/unreliable inventory or absent independent validation prevents a strong GO.
- **NARROW** if robust evidence is limited to particular domains/applications;
  cross-city matching is only a candidate direction if matches survive geometry,
  panel choice and comparison with generic profiles, with a validation plan.
- **STOP / RETHINK** if differences are dominated by geometry, boundaries, local
  identifiers, sparse scoring or candidate instability. Report disconfirming evidence
  with the same prominence as favorable results.

Document all departures and why; do not silently relax gates. Review Qloo spatial
construction, resolution, freshness, observation counts, history, score semantics
and relevant API terms. Record unanswered technical/licensing questions; do not
infer undocumented guarantees or contact Qloo on the user's behalf.
