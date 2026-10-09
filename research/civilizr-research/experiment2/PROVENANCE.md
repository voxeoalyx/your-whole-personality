# Provenance, spatial interpretation, and questions for Qloo

Reviewed 2026-10-07. These questions have **not** been sent to anyone.

## What the official documentation establishes

Qloo describes first-party and anonymized second/third-party interactions,
transactions, streams, views, ratings and follows, plus metadata and API learning
rights. This is a modeled association system, not a neighborhood resident survey.
[Data foundation](https://github.com/qloo/docs-public/blob/main/docs/data-foundation.md).
Its pipeline combines co-occurrence learning, content attributes and geospatial
analysis. The description mentions sampling thresholds and normalization without
publishing neighborhood-specific thresholds or validation errors.
[Processing methodology](https://github.com/qloo/docs-public/blob/main/docs/processing-methodology.md).

Location-linked interactions are mapped to geohash tiles, with resolution adapted
to signal density. The documented smallest example is about 118 m wide; it is
**not** a guaranteed effective resolution for these Orlando queries. Repeated
interactions can increase weight; a visitor interaction need not identify a resident.
[Location methodology](https://github.com/qloo/docs-public/blob/main/docs/insights-with-location.md).

The FAQ describes category-dependent daily, weekly and monthly updates, but does
not supply a locality-level data cutoff, lookback window or vintage. It also names
OpenStreetMap as a supplementary source: our independently retrieved OSM baseline
is therefore not guaranteed independent of Qloo's underlying entity metadata.
[FAQ](https://github.com/qloo/docs-public/blob/main/docs/faqs.md).

Scores are contextual and normalized per query. Rank comparison over a fixed
panel respects relative ordering; neither ranks nor standardized score correlations
recover absolute demand, spending, growth or population prevalence.
[Score interpretation](https://github.com/qloo/docs-public/blob/main/docs/interpreting-affinity-scores.md).

The fixed-output filters restrict candidate IDs but the documentation does not
promise that all requested IDs receive scores. WKT uses longitude then latitude.
Explicit point radii override dynamic density discovery; radii are ignored for
polygon/locality signals. The output-place filter's fuzzy-radius behavior must not
be confused with the input location signal.
[Parameter reference](https://github.com/qloo/docs-public/blob/main/reference/insights-api-deep-dive.md).

## New observations, not undocumented guarantees

This host returned `query.geospatial.panel_size.context` and `.target` on the
fixed-panel requests. The common context value was 72,776,032,816; Orlando target
values ranged from 5,015,328 to 2,088,652,243. They are saved in
`reports/request_diagnostics.csv`. We did not find a definition in the reviewed
official references/search. They must **not** be presented as unique people,
effective sample size, confidence, or population counts.

The primary three areas' modest polygon changes preserved returned scores, as did
their same-center POINT + 1,000 m diagnostics. The additional College Park eastward
shift changed food and pooled-brand rankings. Stable outputs elsewhere are compatible with geographic aggregation,
smoothing, caching or other implementation choices; it does not establish which
mechanism operates or prove sub-neighborhood resolution. Missing candidates remain
missing when specifically requested. No freshness field, confidence interval,
effective independent sample size or neighborhood historical series was established.
Experiment 1's inaccessible/empty trend probes remain the only historical-access
evidence; they were not repeated here.

## Technical questions that would change the decision

1. For the saved request hashes, what does each `panel_size` field count? Is it
   weighted events, inferred mass, a pooled panel, or something else? What is the
   effective independent observation count and uncertainty by candidate/location?
2. Which geohash levels and aggregation footprint were used for each WKT polygon?
   Why do 800/1,000/1,200 m polygons, 200 m center shifts and explicit-radius points
   return exactly identical scores? Can the effective footprint be returned?
3. What fraction of location affinity comes from proximity/venue supply, visitor
   behavior, resident behavior, content similarity and inferred geographic smoothing?
   Is a proximity-neutral or residence-linked output available?
4. Why is Samsung unscored in College Park, Mills 50 and West End while other
   brands score, and why are three valid taxonomy IDs omitted everywhere in this
   panel? Are aliases, confidence cutoffs or candidate eligibility responsible?
   Is there an endpoint that scores an entire fixed panel with missingness reasons?
5. What are each locality's last observation date, lookback window, update cadence,
   model version and revision policy? Are historical **as-of** geographic profiles
   available without future-data leakage, and on the hackathon account?
6. Is there a documented calibrated quantity comparable across locations or time?
   What neighborhood-scale held-out evaluation exists against inventory/proximity
   baselines? Can location-only explainability expose geographic contributions?

## Usage and derived-data restrictions to resolve before a product

The public [Qloo Terms of Use](https://www.qloo.com/legal/terms), labeled December 19,
2024, cover APIs and output, allow a superseding signed agreement, and refer to
additional client-specific terms. They reserve Qloo IP rights and restrict resale,
redistribution, sublicensing and certain derivative uses. These public terms alone
do not establish this account's permitted retention period, public score display,
commercial derived-index rights or attribution requirements. Obtain the applicable
hackathon/client agreement and written clarification of those uses before a public
or commercial product. This is an unresolved permission scope, not a claim that
the authorized local research is forbidden. TasteDive-specific terms were not
assumed to govern this Insights account.

Ask specifically about local raw-response retention, reproducible research archives,
sharing derived rank/similarity tables, commercial neighborhood scores, hackathon
demo display, attribution, and deletion obligations. No deployment or publication
was performed.

OSM-derived inventory: **© OpenStreetMap contributors**, available under the
[Open Database License](https://opendatacommons.org/licenses/odbl/1-0/).
[Attribution and license guidance](https://www.openstreetmap.org/copyright).
The local inventory includes source feature URLs; keep this attribution with exports.

## Archived source material

`sources/docs_manifest.json` records official Qloo document URLs, retrieval UTC
times and SHA-256 hashes. `sources/initial_manifest.json` covers City listing pages
and the Atlanta layer metadata; `sources/atlanta_neighborhoods.meta.json` preserves
the exact GeoJSON query. `inventory_request.json` and the OSM response metadata
record the independent inventory query and snapshot date. Experiment 1's source
archive provides the full location/parameter references. No source documentation
example has been counted as an experimental observation.
