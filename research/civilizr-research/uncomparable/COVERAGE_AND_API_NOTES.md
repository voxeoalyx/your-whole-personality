# Coverage and API notes

Observed on `hackathon.api.qloo.com`, 2026-10-07. Findings apply to this account, host, finite queries and date; they do not establish absence from every Qloo product. Official documentation reviewed before the main tests: the existing [API notes](../API_NOTES.md), Qloo's [entity-type guide](https://github.com/qloo/docs-public/blob/main/reference/available-parameters-by-entity-type.md), [score guide](https://github.com/qloo/docs-public/blob/main/docs/interpreting-affinity-scores.md), [taste guide](https://github.com/qloo/docs-public/blob/main/reference/taste-analysis.md), [audiences guide](https://github.com/qloo/docs-public/blob/main/docs/audiences.md), [audience lookup](https://github.com/qloo/docs-public/blob/main/reference/get-audiences.md), and [audience types](https://github.com/qloo/docs-public/blob/main/reference/get-audience-types.md). Additional current documentation snapshots and retrieval hashes are under `sources/`.

## Native capabilities and observed limitations

| Capability | Request | Observed result |
|---|---|---|
| Entity resolution | `/search`, `query`, `types`, `take` | Authors, persons, brands, books and places resolve, but fuzzy results include homonyms and unrelated places. Inspect type, address and description. Search success does not imply Insights support. |
| Architects/designers | Same search; disambiguate `urn:entity:person` and `urn:entity:author` | Wright and Ray Eames have author records that work as interests. Mies and Charles Eames person records resolve but fail as interests. Charles Sumner Greene resolves after rejecting other Charles Greenes; its affinity was not tested. |
| Styles | `/v2/tags?filter.query=...&take=50` | Actual `urn:tag:decor:qloo:` IDs include `usonian`, `bauhaus`, `international_style`, `mid_century_modern`, `craftsman`, `victorian`, `sustainable_architecture`. Four tested styles are flat; mid-century varies but gives weakly interpretable brands. Bauhaus and Victorian were lookup-only. Cedar Hill was not assigned a Victorian style. |
| Design/home brands | `/v2/insights`, `filter.type=urn:entity:brand`, `filter.tags=urn:tag:industry:qloo:home_goods` | Native tag found on Herman Miller. Includes furniture, appliances and smart-home brands; it is not a pure furniture taxonomy. Farnsworth returns KNOLL, Arper and Eames Office. A later Stickley brand lookup returned no results. |
| Cross-domain relations | Insights, `signal.interests.entities` or `.tags`; `filter.type` = brand, book, place, destination, movie | Four property-associated inputs yield varied brand scores. Place recommendations have plausible discovery leads; destinations are strongly regional. Books/movies did not demonstrate architectural specificity. This experiment did not exhaust every output domain for every house. |
| Fixed candidates | `filter.results.entities`, explicit UUID list, `take` equal to list length | All 24 brands scored for four working house inputs and both author proxies. All 15 places scored for three house inputs and Ray author. No missing brand score was filled with zero. |
| Explainability | `feature.explainability=true` | Working single-entity queries assign contribution 1 to the sole seed. This attributes the input; it does not explain a cultural mechanism, provide population counts, confidence intervals, or evidence of residential demand. Style/audience probes warn that explainability could not be calculated. |
| Audiences | `/v2/audiences`, `filter.parents.types=urn:audience:hobbies_and_interests`, `take=50`; then Insights `signal.demographics.audiences=<native URN>` | 42 hobby audiences returned, including Architecture, Photography and Home Organization. All three fixed six-place tests return only five: Jacobs is missing. Three returned places have the same 0.7649962878 score across all three audiences. Complete audience fingerprints are not established. |
| Buyer/valuation evidence | No suitable documented capability established in this review | Curated positive-interest signals do not identify house buyers, purchase intent, budgets, willingness to pay, scarcity, condition, legal provenance or transaction premiums. We did not solicit demographic profiling. |

`bias.trends=off` is fixed for all Insights requests. Popularity is retained where returned, but is not an inventory count, buyer count or premium. No trend/time-series claim is made: these are same-session snapshots. Affinity values are preserved natively and ranks are compared within matched panels, not interpreted as probabilities or absolute strength across queries.

## Property coverage

| Property | Resolution | Affinity support | Consequence |
|---|---|---|---|
| Jacobs I | Correct Madison house, rank 9 in a 10-result lookup | HTTP 400, invalid interest | Cannot profile this house directly. Usonian proxy is flat. |
| Fallingwater | Correct Mill Run house found after expanding to 100 results | HTTP 400 for brands and books | Cannot compare the two Wright houses directly. Shared Wright author input would make them identical by construction. |
| Farnsworth | Correct Plano house | Working | Museum/visitor/place signal; not documented resident taste. |
| Eames | Eames Foundation at house address | Working institution proxy | [Official contact page](https://eamesfoundation.org/about/contact/) verifies the address; institution and house desirability remain different constructs. |
| Gamble | Correct Pasadena house | Working | Does not isolate craft from tourism, geography or other cultural associations. |
| Cedar Hill | Frederick Douglass National Historic Site | Working | Does not isolate architecture from the person's historical significance. |
| McKinley | No faithful match in the recorded ten-result search | No direct test possible | Sustainable Architecture proxy is flat. Do not interpret missingness as lack of culture. |

Six of seven have an identifiable place/institution record; **only four of seven have a usable property-associated affinity input, including the Eames institution proxy**. The predeclared five-of-seven threshold was not met.

Machine-readable decisions: `coverage.json`, `tables/coverage.csv`. Full IDs: `inputs.json`, `proxy_addendum.json`. Every attempted lookup, not just accepted matches, is in `tables/results.csv`; request parameters and errors are in `tables/requests.csv`. Search expansion, tag synonyms, homonyms, and missing IDs remain in raw responses.

## Missingness and silent flatness

There were 79 HTTP attempts: 74 HTTP 200 and five HTTP 400. No transport retry was needed or attempted. Four style inputs each scored all 24 brand candidates identically at 0.7649962877984056, with the same unrelated unrestricted recommendations. Their rank correlation is **undefined**, not 1; returned list order is not a cultural ranking. This behaves like an uninformative fallback, but the API did not disclose the internal cause.

Across all fixed-panel requests there are 389 requested candidate occurrences: 386 returned with scores and three missing (Jacobs once per audience). Scored-but-flat values remain flagged as uninformative; nominal completeness does not make them useful. Missing/unscored/HTTP failure/flat score are distinct conditions. `tables/candidate_scores.csv` preserves each candidate occurrence.

The 24-brand panel is a union of two modernist-seeded home-goods lists. This is a biased exploratory candidate selection, especially for Gamble and Cedar Hill, not a validated architecture ontology. Halving it checks sensitivity within that selection, not robustness to every candidate universe. The post-hoc Stickley lookup tests an obvious omission named in baseline B; it returned no brand, and did not change the panel. The 15-place panel similarly uses the union of three discovered top-five lists. No holdout property set or longitudinal stability was tested.
