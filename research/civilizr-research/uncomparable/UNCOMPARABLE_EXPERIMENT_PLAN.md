# Uncomparable: feasibility experiment 1

Frozen before the first Uncomparable API request, 2026-10-07. No product or UI.

## Question and controls

Does Qloo add useful information to a capable LLM given verified property provenance? A cultural association is not a buyer, purchase intention, willingness to pay, or a transaction premium.

Seven properties: Jacobs I, Fallingwater, Farnsworth House, Eames House, Gamble House, Frederick Douglass's Cedar Hill, and the McKinley Project in Garland. These cover two Wright houses, other modernists, Arts and Crafts, historical significance, and a contemporary suburban control. The control is a DOE energy award case study, not a representative random home. Museum/tourist coverage and famous-author coverage are possible confounds. There is no hierarchy of cultural worth.

## Frozen comparison

`properties.json` holds source-backed facts and uncertainty separately from Qloo. `baseline_ab.json` freezes A (ordinary attributes) and B (provenance plus an LLM's interpretation and predicted cultural leads), before viewing API recommendations. C will use exactly these facts plus observed Qloo results. Predicted leads are hypotheses, not historical claims. Obvious author/brand associations do not count as discoveries.

The same assistant prepares and evaluates the descriptions. This is a structured, unblinded feasibility comparison, not an independent blind trial. A future blinded user trial is necessary before claiming incremental consumer utility.

## Small, adaptive protocol

1. Read official Qloo docs. Search actual houses, authors, styles, design brands and audience taxonomy. Record returned type, geographic identity, missing and ambiguous matches; do not accept names alone. Initial four-query smoke test precedes expansion.
2. Freeze accepted IDs before main profiles. Prefer direct house entities; author or style proxies are explicitly different inputs. Do not silently substitute a museum for an architect. Query unrestricted design-brand recommendations first, plus selected books, destinations and places. Use `bias.trends=off` and explainability where supported.
3. Freeze a shared, small brand candidate panel from the union of initial brand results. This is an exploratory outcome-selected panel, not an independent confirmation. Exclude unrelated entities only using recorded domain reasons, not favorable scores. Preserve every missing/unscored candidate. Compare ranks only on complete panels; paired overlap is explicitly partial.
4. Compare traditions using rank correlation and top-five overlap. Repeat an identical request uncached, halve the fixed candidate panel, and compare a house with a related author/style input. Keep same-author houses separate; identical proxy input cannot differentiate them.
5. Probe audience lookup and audience-as-input recommendations if relevant IDs exist. Never invert audience-to-entity affinity into an estimate of buyers. Check at most a few potentially useful, non-obvious leads against independent primary sources. Corroborating thematic relevance does not validate Qloo's underlying audience measurement.

Target roughly 60 HTTP calls, hard ceiling 85 including bounded retries. Sequential requests, 20-second timeout, explicit budgets, local raw JSON and exact request manifests. Stop expanding a failed domain. No dependency installation. Reuse the existing stdlib runner without editing it.

## Decision criteria

GO requires faithful usable representation for at least five of seven properties across at least three traditions, repeatable profiles, and at least two useful, non-obvious leads beyond B across two traditions. Leads must have independent thematic corroboration and survive a relevant perturbation. Rank differences alone do not pass.

NARROW requires a specific supported discovery/matching use, with missing coverage and confounds visible. STOP if faithful inputs are sparse, generic recommendations dominate, or B explains property distinctions just as well. Fixed-panel completeness is mandatory for any full-vector claim. An identical-repeat Spearman correlation below 0.95 or half-panel correlation below 0.8 flags fragility; these are screening rules, not statistical significance. No valuation claim is possible here.

Record limitations and unperformed tests. An honest null result is a successful experiment. No further datasets, application, or scheduled monitoring in this task.
