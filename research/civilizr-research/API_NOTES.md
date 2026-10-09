# Qloo API notes

Reviewed 2026-10-07 using Qloo's official [documentation repository](https://github.com/qloo/docs-public).
The live docs site was unavailable to the web reader. Local source copies and
SHA-256 hashes are recorded in `docs/sources.json`; copies are in ignored `docs/snapshots/`.
Only Qloo supplies experimental data. Documentation examples are not observations.

| Need | Endpoint and parameters | Interpretation / caveat |
|---|---|---|
| Locality lookup | `GET /search`, `query`, `types=urn:entity:locality`, `take`, `page`; optional `filter.location=latitude,longitude`, `filter.radius` in miles | Inspect returned ID, disambiguation, ancestors, location and boundaries. Fuzzy matches are unsafe without review. |
| Location-based preferences | `GET /v2/insights`, `filter.type`, `signal.location=<locality UUID or WKT>`; alternative `signal.location.query` | Location influences affinity. Use identical result domains for comparisons. |
| Local business inventory | Same route, `filter.type=urn:entity:place`, `filter.location`, `filter.location.radius=0`, optional `filter.tags` | Filters output POIs. Different nearby businesses do not independently establish audience taste. |
| Taste/category affinity | Same route, `filter.type=urn:tag`, `signal.location`, `filter.parents.types` and/or `filter.tag.types`; `filter.results.tags` for a fixed list | Use actual returned taxonomy IDs. Preserve missing/unscored results. |
| Entity affinity | Same route, `filter.type=urn:entity:brand` or `urn:entity:destination`, `signal.location`; optionally `filter.results.entities` for fixed candidates | Do not constrain destinations to Orlando if studying travel preferences. |
| Taxonomy discovery | `GET /v2/tags/types`, `filter.parents.types`; `GET /v2/tags`, `filter.query`, `filter.tag.types`, `take<=50`, `page` | Paginate where needed; this experiment records the finite pages searched. |
| Explanation | Insights `feature.explainability=true` | Returns per-result and aggregate input-entity contributions. May return `query.explainability.warning`. It is not causal evidence or a promised explanation of geographic inference. |
| Heatmap | Insights `filter.type=urn:heatmap`, `filter.location` or `.query`, plus `signal.interests.tags` or `.entities` | Returns geographic cells with affinity, affinity_rank and popularity. Compare one signal over one shared extent. No UI needed. |
| Boundary heatmap | `output.heatmap.boundary` | Docs describe geohashes (default), city and neighborhood output, but do not give a rigorous enum here. Default-grid probe first; test `neighborhood` separately. |
| Category trends | `GET /trends/category`, `type=urn:entity:brand`, `page`, `take` | Prose limits support to brands, with movies/TV beta; the enum is broader. No documented location parameter. |
| Entity trends | `GET /trends/entity`, `entity_id`, `start_date`, `end_date`, `page`, `take` | Entity-level time series, not demonstrated neighborhood-specific change. |
| V2 trends | `GET /v2/trending`, `signal.interests.entities`, `filter.type`, `filter.start_date`, `filter.end_date`, `take<=50` | All four main parameters required by prose. Example curl omits required inputs. Probe separately. |
| Group comparison | `GET /v2/analysis/compare`, `a.signal.interests.entities`, `b.signal.interests.entities` | Compares selected entity groups; selection of local venues can manufacture an apparent contrast. Not a direct neighborhood panel. |

Authentication: `X-Api-Key` header. The supplied key was rejected by `api.qloo.com`
and accepted by `hackathon.api.qloo.com`; this is an observed host restriction,
not a network failure. Keep host configuration explicit. [Authentication reference](https://github.com/qloo/docs-public/blob/main/reference/api-onboarding.md).

## Geographic and score semantics

Insights WKT uses **longitude latitude**, unlike Search's **latitude,longitude**.
`filter.location.radius` uses meters and defaults to fuzzy expansion when omitted;
zero requests strict locality boundaries. `signal.location.radius` only applies
to POINT inputs and is ignored for locality IDs/polygons. It overrides adaptive
density selection, so it belongs in a sensitivity test. [Insights parameter reference](https://github.com/qloo/docs-public/blob/main/reference/insights-api-deep-dive.md),
[Search reference](https://github.com/qloo/docs-public/blob/main/reference/get-search.md).

Qloo describes adaptive geohash resolution and inference even where direct signal
is sparse. A returned result does not establish a well-sampled neighborhood.
Location-linked interactions may include visitors; these are not verified resident
survey responses. [Location methodology](https://github.com/qloo/docs-public/blob/main/docs/insights-with-location.md).

Affinity is normalized per query; keep native values and compare rankings with
matched output domains. The prose uses a 0–100 presentation, while this account's
responses use 0–1 values. Do not infer growth from small affinity differences.
Popularity is a percentile, not spending, foot traffic, population, or a count.
[Score interpretation](https://github.com/qloo/docs-public/blob/main/docs/interpreting-affinity-scores.md),
[heatmap metrics](https://github.com/qloo/docs-public/blob/main/docs/heatmaps.md).

## Documentation inconsistencies worth testing

- The entity-type guide omits some location signals shown in the location guide;
  it also marks entity interests required for destinations. Location-only requests
  are capability probes until verified. [Entity-type guide](https://github.com/qloo/docs-public/blob/main/reference/available-parameters-by-entity-type.md),
  [location use case](https://github.com/qloo/docs-public/blob/main/reference/insights-with-location-use-case.md).
- Tag output is documented in the [taste guide](https://github.com/qloo/docs-public/blob/main/reference/taste-analysis.md)
  even though the deep-dive enum omits `urn:tag`. Some lookup enums list audiences
  where the description also permits entity parents. Trust successful observed
  behavior only for the tested host and parameters.
- Actual locality metadata uses `query.localities.signal` in the first smoke
  response, while prose describes `query.locality.signal`. Preserve the whole object.
- The repository's `openapi-schema.json` is an OpenAPI document validation schema,
  not a usable Qloo endpoint specification (it contains `$defs`, not actual API paths).
  Do not generate a client from it.

Further references: [tags](https://github.com/qloo/docs-public/blob/main/reference/get-tags.md),
[tag types](https://github.com/qloo/docs-public/blob/main/reference/get-tag-types.md),
[heatmap request](https://github.com/qloo/docs-public/blob/main/reference/heatmaps-use-case.md),
[category trends](https://github.com/qloo/docs-public/blob/main/reference/get-trends-category.md),
[entity trends](https://github.com/qloo/docs-public/blob/main/reference/get-trends-entity.md),
[v2 trending](https://github.com/qloo/docs-public/blob/main/reference/get-trending.md),
[analysis compare](https://github.com/qloo/docs-public/blob/main/reference/analysis-compare.md).
