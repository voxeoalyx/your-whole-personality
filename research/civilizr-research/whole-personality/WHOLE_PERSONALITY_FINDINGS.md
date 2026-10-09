# Whole Personality: findings

2026-10-08 · Qloo experiment 3 · **Recommendation: NARROW — consumer-first validation.**

Qloo exhibits real, repeatable sensitivity to mixed interests. It has not demonstrated human personality measurement, incremental usefulness over an LLM, or better partnership decisions. A small game mechanic is worth testing with people; a commercial intelligence product is not justified yet. No product was built.

## What was actually tested

The frozen plan and LLM-only baseline preceded live recommendation collection. The early combination gate passed before the expanded matrix. We made **183 HTTP requests**, all returning HTTP 200, below the 185-attempt ceiling. Search resolved 19 reviewed entities; 18 worked as individual interest signals on both output panels. Twelve three-interest profiles were attempted; **10 were faithful and usable**. Five brands each received two proposed partners, with both singletons and both combinations measured. Full leave-one-out analysis covered six profiles.

The Frank Herbert Dune book resolved in search but generated a `not_found` input warning in Insights. Alone, it returned 45 brand and 19 TV candidates without scores. In mixed profiles, Qloo scored the candidates using the remaining interests. Therefore p11/p12 are failed three-interest tests, not successful book profiles. They remain visible and are excluded from valid narrative comparisons. HTTP success and complete output scores did not imply complete input support.

The main panel contains 45 brands from the earlier Civilizr experiment, after excluding input brands. The 19-title TV panel comes from the original two profiles' recommendations: **it favors detecting that original contrast**. A secondary panel contains 50 of 52 eligible pilot brands, selected deterministically by sorted UUID, with only two brands overlapping the primary panel. It is another outcome-selected sensitivity check, not independent validation. These panels are small measurement instruments, not comprehensive cultural maps.

Rank distance is **D = (1 − Spearman rho) / 2**: zero means identical rankings, one means reversed rankings. It uses ties correctly and is undefined for incomplete or flat scores. Scores remain query-normalized; no affinity is interpreted as a probability. Top-five overlap includes ties. All thresholds below are descriptive screens, not significance tests.

## 1. Can one interest hijack a modeled cultural identity?

**Sometimes it disproportionately changes the measured rankings; usually there is no robust single winner.** Identity Dominance is the mean rank distance between the full profile and each leave-one-out profile across brands and television. It is Qloo sensitivity, never a percentage of someone's personality.

Only **one of six** tested contexts passed the frozen dominance screen: a winner above 0.10, more than twice the runner-up, winning on both disjoint candidate halves. That was The Joe Rogan Experience in Radiohead + Blue Bottle + Rogan: ID **0.295**, versus Blue Bottle **0.142** and Radiohead **0.058**.

Rogan also wins after replacing the brand panel, but its greater-than-two ratio does not survive that change. The secondary calculation reuses the same TV panel, so this is partial robustness. In Taylor Swift + Starbucks + Rogan, the same podcast's ID is only **0.045**, about 6.6 times smaller. A universal “Rogan dominates everyone” claim fails.

## 2. Which entities produce the strongest effects, and why?

Rogan's podcast in the original context produces the largest measured leave-one-out effect. Severance is next among the principal original-profile inputs (ID **0.155**), with Radiohead at **0.124**. These effects are driven mainly by TV reordering. Their exact causal mechanism is unknown; the selected TV candidates contrast the original recommendations sharply.

The same entity changes substantially across contexts, ruling out fixed popularity or entity type as a sufficient explanation. Radiohead has higher supplied popularity than the Rogan podcast but a smaller effect in p02. An alternative podcast, Huberman Lab, also causes a large original-profile TV shift. Complete scores make missing candidates an unlikely explanation for these particular contrasts. However, this small purposive sample cannot isolate effects of popularity, category, training coverage or strength of an individual signal. It does not contain controlled niche-versus-mainstream matches.

Qloo's brand explainability shares in the original triples are roughly 0.30–0.36 per input, despite unequal leave-one-out distances. Native contributions and ranking sensitivity answer different questions; neither measures human influence. Candidate halves disagree on the winning input in three other contexts, and the secondary brand panel changes three full-panel winners. A product should sometimes report “no clear winner.”

## 3. Does Qloo meaningfully combine multiple interests?

**Yes, as an API behavior.** The pilot combinations differed from every singleton on both panels. In the partnership study, **17 of 20 domain comparisons** were at least D=0.03 away from both brand and partner alone. None passed the strict partner-substitution warning; Apple + Severance on TV was borderline, only D=0.0202 from Severance alone, just outside the 0.02 cutoff. Threshold precision should not hide that resemblance.

The combinations are generally close to the simple equal-rank average of their singletons: median D **0.016** across the 20 comparisons. This supports blending and weakens a claim that the combinations expose unique emergent audiences or partnership synergy. It does not identify Qloo's internal algorithm.

Four uncached local repeats, two input-order reversals and four actual half-panel reissues all preserved ranks exactly: rho **1.000**. These are same-session checks on the original cases, not independent replications of every partnership or proof of historical stability. Server caching remains possible. Discrete swaps do not establish a continuous tipping point; no verified per-interest dose control was used.

## 4. Is the personality flip in the data or the narrative?

**A substantial TV-ranking flip is in the data. The specific personality story is unverified.** Both Joe Rogan the person and The Joe Rogan Experience the podcast were tested separately; they were not silently treated as one entity.

| Single-interest replacement | Brand D | TV D | Interpretation within these panels |
|---|---:|---:|---|
| Severance → Rogan podcast; Radiohead + Blue Bottle fixed | 0.085 | 0.861 | Large TV reversal; smaller brand shift |
| Severance → Joe Rogan person; same base | 0.092 | 0.820 | Similar broad result with exact named person |
| Severance → Huberman Lab; same base | 0.055 | 0.723 | Not unique to Rogan |
| Friends → Rogan podcast; Taylor + Starbucks fixed | 0.033 | 0.123 | Much weaker context |
| Elden Ring → Animal Crossing; Metallica + Nike fixed | 0.007 | 0.030 | Little overall movement |
| Blue Bottle → Monster; Patagonia + Lululemon fixed | 0.112 | 0.035 | Brand change, little TV movement |

Unrestricted original TV leads move from **Black Mirror, Devs, Electric Dreams** to **Comedians in Cars Getting Coffee, Lady Dynamite, Adam Ruins Everything** with the podcast. Unrestricted brand leaders still overlap substantially around Patagonia, REI and Huckberry. The secondary brand distance for the original podcast replacement is 0.139, versus 0.085 on the primary panel. The large effect is not uniformly cross-domain.

The returned tags mix place attributes, dishes, media motifs and genres. Examples include “Identifies as women-owned,” “Os A Moelle,” “Cinematically Raw” and “Spacecraft,” often tied at affinity 1. They are not direct labels for a person's identity. We could not reproduce or validate the demo's eco-conscious/body-positive versus motorsports/battle-royale story. A documented audience input is not a posterior audience classification.

Fixed-format LLM narratives name only returned recommendations. Three valid swaps are large data/large named-content change; two are middle/large; one is small/middle. There are **zero small/large and zero large/small** examples under the frozen thresholds. In the brand-heavy swap, the top-five TV set stays identical while one of the three displayed TV names changes: a concrete presentation cutoff effect. This constrained audit cannot establish whether the proprietary demo exaggerates changes. See the complete narrative comparison and cutoff-gap table.

## 5. Can a brand make a better positioning or partnership decision?

**It can form more specific hypotheses; better decisions remain unproven.** All five comparisons were completed:

| Brand | Proposed partners | D between combinations: brands / TV |
|---|---|---:|
| Blue Bottle | Radiohead / Metallica | 0.103 / 0.495 |
| Nike | Elden Ring / Animal Crossing | 0.012 / 0.044 |
| Apple Inc. | Severance / Friends | 0.016 / 0.207 |
| Lululemon | Huberman Lab / Rogan podcast | 0.057 / 0.048 |
| Patagonia | Björk / Taylor Swift | 0.067 / 0.402 |

For example, Lululemon + Huberman surfaces Whole Foods, West Elm and Alex and Ani; Lululemon + Rogan surfaces ESPN, Whole Foods and Alex and Ani. That gives a strategist a concrete media or creative hypothesis to test. It does not estimate audience reach, exclusivity, brand safety, purchase intent, sales or brand lift. Nike's alternatives barely separate on the brand panel, making that comparison weak with this instrument. Apple–Severance is an existing association sanity check, not an undiscovered partnership opportunity.

The frozen LLM-only baseline often supplies plausible alternatives too. No independent human ratings were collected, and the LLM had an unrestricted candidate universe while Qloo was panel-constrained. Consequently there is **no measured incremental utility over the LLM baseline**. A blinded six-case packet and separate answer key are ready; no evaluator responses were fabricated.

## 6. What would make this defensible beyond Qloo?

A repeatable decision workflow, consented feedback on actual interests, held-out preference outcomes and evidence that recommendations improve a real task could become differentiated assets. The leave-one-out formula, the raw API rankings and a colorful narrative are readily reproducible. Qloo already demonstrates mixed-interest inference and markets creative/media/partnership planning, so wrapping its output is weak differentiation. These are vendor offerings, not independently verified performance claims. [Qloo capabilities](https://www.qloo.com/capabilities), [marketing use case](https://www.qloo.com/use-cases/plan-marketing-and-media-campaigns).

Commercial rights and ownership of derived/feedback data are unresolved; a working key establishes neither. Contract findings, proposed buyers and validation requirements are in PRODUCT_AND_COMMERCIAL.md. Public launch or a paid intelligence offering would require resolving those rights.

## 7. Is there a compelling, investable hackathon product?

**A testable hackathon mechanic, yes; an investable business case, not yet.** The supported concept is “Which interest moves this recommendation mix most?” with visible evidence, swaps, and an honest no-clear-winner state. Its entertainment and sharing value still require human testing. Cultural White Space is least supported: affinity does not show competitor absence, market demand or an unoccupied opportunity.

Next, use the blinded packet as an exploratory screen, then recruit volunteers with their own interests and withheld likes. Compare Qloo and an LLM with equivalent candidate access and identical wording; freeze the next protocol before collection. Measure relevance, useful novelty, enjoyment and actual voluntary sharing, using people as the unit of analysis. Repeat independent brand/TV panels on another day and include unsupported-input cases. For a commercial branch, ask strategists to make a concrete shortlist before and after seeing the evidence, then test their resulting hypotheses externally. Do not treat more API calls as a substitute for validation.

GO is blocked by the absence of independent added-utility evidence. STOP would overstate this run: the measurable mixing and context-dependent sensitivity are real. NARROW preserves the consumer experiment while withholding claims of decision intelligence.

## Evidence map

All files are in this experiment's directory. `tables/swaps.csv`, `dominance.csv`, `partnerships.csv`, `coverage.csv`, `checks.csv` and `narrative_changes.csv` contain the reported quantities; `profile_refs.json` maps logical cases to exact raw requests. `runs/` stores response bytes, hashes, timestamps and request parameters. `API_NOTES.md` lists official documentation and observed limitations; `DEVIATIONS.md` records scope clarifications. Six metric tests, raw-response hashes, preregistration hashes and the narrative evidence audit were checked locally.
