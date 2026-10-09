# API coverage and observed limitations

Reviewed 2026-10-08 using Qloo's official public documentation. Source snapshots and SHA-256 records are local in `sources/docs_manifest.json`. They are documentation evidence, not API response data.

| Need | Endpoint / parameters used | Observed result |
|---|---|---|
| Resolve an intended entity | `GET /search`: `query`, `types`, `take=5` | 19 names reviewed against type/description/ID; search alone did not establish interest support |
| Combine interests | `GET /v2/insights`: `signal.interests.entities`, `filter.type` | Multiple artists, brands, TV titles, podcasts, a person and games worked; selected Dune book did not |
| Hold outputs constant | `filter.results.entities`, `take` matching panel size | 45-brand, 19-TV and secondary 50-brand panels; candidate rows returned but sometimes unscored |
| Explain returned associations | `feature.explainability=true` | Per-interest explanations available; contribution shares differ from ablation sensitivity |
| Reduce trend confounding | `bias.trends=off` throughout | Trends intentionally excluded; no historical changes or trend index measured |
| Native tag outputs | `filter.type=urn:tag`, `take=20` | Three original cases succeeded but heterogeneous namespaces and saturation made personality interpretation unsound |
| Audience inference | No reverse-audience query issued | Reviewed documentation exposes audience signals as inputs; no supported posterior identity classifier established |

The Insights documentation describes entity signals, output filters and explanation fields. Its contribution values are query-specific; low contributions can be omitted. Neither absence of an explanation nor its normalized share is a psychological influence estimate. Global interest weight is not evidence of per-entity weighting. [Insights deep dive](https://docs.qloo.com/reference/insights-api-deep-dive), [parameters by output type](https://docs.qloo.com/reference/available-parameters-by-entity-type).

Affinity values are normalized within a query. We compare ranks on identical panels, retain the original numbers and avoid cross-query probability interpretations. Finite nonconstant scores and faithful input support are separate checks. No geography, audience, popularity threshold or trend bias was added to the profiles. [Interpreting affinity](https://docs.qloo.com/docs/interpreting-affinity-scores), [search documentation](https://docs.qloo.com/reference/get-search).

The exact original names are in `seeds.json`: Severance is the 2022 series, Friends the 1994 series, Dune the Frank Herbert book, Apple the company brand, Animal Crossing: New Horizons the 2020 game. Joe Rogan the person and The Joe Rogan Experience podcast have separate UUIDs and results. The podcast is the frozen p02/p06 input; an extra person case addresses the literal demo wording. No other substitutions were made.

The Dune UUID returned an Insights `not_found` warning. Its singleton produced 64 unscored candidate rows across two domains. Its two mixed profiles produced complete scores while omitting Dune. This limitation applies to that record and account on this date; it does not establish that all books are unsupported. No output candidate was entirely absent, and no network or HTTP failure occurred in the 183 attempts. An HTTP-200 response can still be unsuitable for the intended experiment.

Brand/popularity fields, native genres, explanations and warnings are retained in raw JSON; compact exports include input support and native top-ten genre counts. Returned tags include content motifs and place attributes, not homogeneous audience traits. This experiment does not support converting such tags into demographics, politics, health, body image or psychology.

Known limits: purposive entities; 10 valid profiles; only six full ablations; two main output domains; selection-biased TV panel; secondary panel selected from pilot results; short top-three narratives; no per-seed dose test; no date-separated replication; no real campaign outcomes or participant feedback. We do not infer exact demo settings, unpublished API behavior or rights from possession of a working key.
