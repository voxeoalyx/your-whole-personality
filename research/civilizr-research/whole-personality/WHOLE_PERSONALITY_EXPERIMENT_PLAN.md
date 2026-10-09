# Whole Personality — experiment 3

2026-10-08. Independent research in `whole-personality/`; preserve Civilizr and Uncomparable. No product, UI, deployment, outreach, or paid dependencies.

## Hypothesis and scope

Does changing one interest reproducibly change Qloo's modeled preferences? Does combining a brand with a proposed cultural partner add information beyond that partner alone? These are tests of a recommender, not human psychology or campaign outcomes. The user's demo description is an observation to investigate, not a ground-truth personality label. The demo's prompt, model, settings and exact entity choices are unknown.

Read prior findings and current official API documentation first. Verify every seed by ID, type and metadata. If Joe Rogan's person record fails, test a separately labeled Joe Rogan Experience podcast proxy; never silently substitute them. Record any other substitutions before scoring.

## Stages and early gate

1. Resolve seeds; freeze exact IDs and input profiles. Freeze LLM-only predictions before reading new recommendations. The author already knows the user's reported demo labels, so the original case is not a blind baseline.
2. Pilot Radiohead + Blue Bottle + Severance versus the Joe Rogan replacement; include every single seed and the unchanged two-interest base. Test brands and television. Stop the full matrix if supported combinations are uniformly flat, unusable, or reproduce one single seed without meaningful change in both domains. A pilot may reveal a failed measurement choice; report that separately from product failure.
3. If the gate passes, test 12 profiles organized into one-interest-swap pairs/variants: original four variants, mainstream, mixed entertainment/gaming, brand-heavy, and niche/book combinations. They are hypothetical research fixtures, not labeled populations. Up to five brands get brand alone, two proposed partners, each combined profile, and both partners alone.
4. Full leave-one-out tests on the original pair, mainstream pair and brand-heavy pair (six profiles); the other profiles get swap tests only. This bounds requests while testing context dependence. Explicitly report the reduced leave-one-out coverage.
5. Same-session uncached repeats, input-order reversal, two disjoint candidate halves, and a few actual half-panel reissues. Inspect both score completeness and rank stability. Test native scored tags and audience outputs only if documented; an audience-as-input query is not an inverse audience estimate. Explainability contributions are diagnostics, not psychological influence.

Target about 150–170 new requests, hard ceiling 185 including failures. Reuse the stdlib GET runner, sequential requests, explicit stage budgets, no automatic retries, 20-second timeouts. Cache/resume successful local requests. Stop failed branches instead of expanding indefinitely.

## Candidate selection and metrics

Brand primary panel: reuse the 47 previously audited nonlocal brands from Civilizr experiment 2, selected before these taste profiles. Keep its coverage problems visible. A television panel is the deterministic union of up to ten results for each original triple, frozen before the full matrix; this is outcome-selected and may favor the original contrast. Exclude every seed of the same output type from all profiles' candidate panels to prevent own-interest exclusion from manufacturing missingness. Keep a secondary brand panel from the original pilot recommendations, if substantially different; use it as a candidate-selection sensitivity check, not independent evidence. Maximum 50 candidates per query.

For each complete, nonconstant panel, compute tie-aware Spearman rho and **rank distance D = (1 − rho) / 2**. Top-five Jaccard uses all candidates tied at the cutoff; flat vectors are undefined. Missing results are never zero; full-panel metrics are NA if incomplete. Report matched complete subsets only as explicitly partial exploratory analyses. Keep native query-normalized scores, but do not interpret cross-query score differences as probabilities or demand changes.

**Identity Dominance ID(P,e)** = mean of D(full profile, profile without e) across the two fully observed, nonflat domains. Report per-domain values and number of available domains; do not silently average one domain into a two-domain index. A dominance *flag* requires the largest leave-one-out distance to exceed 0.10 and twice the next-largest, with the same winner in both disjoint candidate halves. This is a transparent sensitivity screen, not a percent of a person's personality. Rank displacement and changes in the mix of returned native categories are auxiliary diagnostics, not a psychological-diversity score.

For combinations report distance to brand alone, partner alone, and a simple equal-weight average of their percentile ranks. Near-partner behavior (D <= 0.02) despite a large distance from the brand (D >= 0.10) is a warning that a partnership simulation may just substitute the partner. A combination separated from both singletons by D >= 0.03 is evidence of distinct model behavior, not evidence of a new real audience. Thresholds are pragmatic screens, not significance tests.

Check popularity metadata, input type, missingness, singleton similarity and explainability alongside dominance. The small, purposive set cannot identify causal effects of popularity/type. GET's global interests weight is not a documented per-seed dose control; absent a verified per-seed API mechanism, discrete swaps/additions cannot establish continuous dose-response or a tipping point.

## Narrative and external validation

Two layers remain separate. Quantitative outputs are generated offline from stored responses. Narrative uses the fixed prompt in `NARRATIVE_PROTOCOL.md`, short descriptions, returned evidence only, and no inferred demographic, political, psychological or lifestyle traits. Store exact evidence and narratives. LLM-only uses the identical interest names, same output length and format, without Qloo evidence. The same assistant drafts both; do not use its own ratings as sole proof of quality.

Compare narrative named recommendations/topic emphasis with the underlying top-five changes. Audit every factual phrase against supplied evidence. Classify large/small data versus large/small narrative changes using declared thresholds; do not force all four quadrants to exist. Narrative-sensitive wording cannot turn a small rank change into a personality flip. No proprietary demo replication is claimed.

Use a few independently documented cultural relationships as limited sanity checks, not ground-truth consumer demand or proof of superiority. Prepare a shuffled, unlabeled packet and separate answer key for later human evaluation. Do not send it to anyone. Include useful specificity, novelty, relevance, unsupported claims and pair preference questions. The absence of independent human feedback caps claims of entertainment, market value and incremental utility.

## Decision criteria

GO requires reproducible, interpretable mixed-input effects in both domains across multiple contexts, some meaningful combination beyond either singleton, adequate coverage, and independent evidence of added utility over the LLM-only baseline. NARROW fits stable model sensitivity or amusing failures with unproven commercial utility; propose a consumer-first validation. STOP fits generic, unstable or unsupported results, or no credible benefit over ordinary LLM inference.

Require same-session repeat rho >= 0.95; flag input-order changes above D=0.02 and candidate-half disagreement on the dominance winner. Require at least 10/12 profiles complete in a primary domain before claiming broad panel coverage. If the primary panel fails, keep that failure and label any replacement secondary; never retroactively change the gate. Historical stability, human accuracy, prediction of sales/brand lift, and investability cannot be established by this run alone.

Review Qloo's current marketer offerings and public license terms. Commercial permission depends on the user's actual agreement; a working hackathon key is not proof of redistribution, derived-data, public display or commercial rights. Record unresolved contract questions without contacting Qloo. Identify the workflow, feedback and outcome data a competitor with the same API would lack; do not invent market size, pricing or an investment case.
