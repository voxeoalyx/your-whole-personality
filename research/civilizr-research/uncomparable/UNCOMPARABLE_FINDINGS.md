# Uncomparable — experiment 1 findings

**Recommendation: NARROW to curated architectural discovery. Do not build the proposed distinctive-property matching or intelligence product for October 30 on this evidence.** Qloo produces some repeatable, defensible discovery leads for supported house museums. It does not yet demonstrate better property understanding than verified provenance plus an LLM. The original broad hypothesis did not pass.

This was a seven-property, 79-request feasibility test on October 7, 2026. The plan, source-backed property facts and A/B baseline were frozen and hashed before the first request. Raw responses, errors, exact parameters and CSVs are saved locally. No application was built; earlier Civilizr experiments were preserved.

## What worked, and what failed

Only **four of seven properties** supplied a working property-associated interest signal: Farnsworth, Gamble, Cedar Hill and the Eames Foundation at the house address. Jacobs I and Fallingwater both resolve in search but fail as Insights interests. McKinley, the qualified suburban control, did not resolve in the finite lookup. Neither a faithful two-Wright-house comparison nor a meaningful ordinary-home contrast is possible. A shared Wright author input cannot solve that problem.

Native style labels exist, but Usonian, International Style, Craftsman and Sustainable Architecture produced the same flat 0.7649962878 scores and unrelated brands. Their presence in the taxonomy is not evidence of usable style intelligence. Mid-century Modern produced varying scores, led by Whittaker's Chocolate Lovers and Maggie Marilyn; this was not a convincing architectural explanation. Mies and Charles Eames person records resolve but fail as affinity inputs. Wright and Ray Eames author records work, yet both favor technology brands in unrestricted output.

The strongest useful domain was **cultural places and galleries**. Home-goods brands were interpretable for Farnsworth, but largely familiar: KNOLL, Arper, Eames Office, Moooi and B&B Italia led. The Eames house-associated input favored Hem, Fritz Hansen, Eames Office, VITRA and KNOLL on the fixed panel. These describe contemporary design adjacency, not the specific qualities of a house. Books and the one film probe were not convincingly architectural; destinations mostly reproduced regional travel context. Gamble's unrestricted brands favored Bring A Trailer, Ford Bronco and Canoo. An attractive story about collecting would be speculation.

## Is differentiation real and stable?

All 24 fixed brand candidates scored for each working house input. Spearman rank correlations are below. Blanks for Jacobs, Fallingwater and McKinley remain missing in the full CSV, not zero.

| | Farnsworth | Eames Foundation | Gamble | Cedar Hill |
|---|---:|---:|---:|---:|
| Farnsworth | 1.00 | 0.83 | 0.74 | −0.29 |
| Eames Foundation | 0.83 | 1.00 | 0.76 | −0.30 |
| Gamble | 0.74 | 0.76 | 1.00 | −0.05 |
| Cedar Hill | −0.29 | −0.30 | −0.05 | 1.00 |

There are real differences in returned rankings. They are not evidence that the API understands the intended architectural distinctions. The panel was selected from Wright/Farnsworth home-goods recommendations and favors modernist candidates; Gamble resembles both modernist houses on that panel. Cedar Hill's separation can reflect historical association rather than architecture. The control needed to distinguish these explanations is unavailable.

Both uncached Eames repeat requests were exact rank repeats: **rho = 1.00** for 24 brands and 15 places. The Eames/Farnsworth half-brand panels and Eames half-place panel also preserved all shared ranks, **rho = 1.00**. These are within-session checks, not temporal validation.

Input identity mattered much more: Eames Foundation versus Ray Eames author gave **rho = −0.665** for brands and **0.454** for places. Their top-five brand sets did not overlap. Wright author versus Ray author gave **rho = 0.954**. Thus reproducibility is good for a fixed input, but replacing a house with its designer is not a reliable representation strategy. Single-seed explainability simply gave that seed contribution 1; it did not explain these discrepancies.

## Does C beat provenance plus an LLM?

`COMPARATIVE_RESULTS.md` and `tables/comparisons.csv` retain all seven A/B/C comparisons. A contains ordinary attributes; B interprets the same verified facts with historical context; C adds observed API outputs. No unsupported Qloo metadata was promoted into verified property facts.

B already distinguishes Jacobs's affordable domestic experiment from Fallingwater's landscape retreat, Farnsworth's structural reduction from the Eameses' industrial components and personal collections, Gamble's integrated craft, and Cedar Hill's historical significance. C cannot reproduce several of those contrasts because its direct inputs or style proxies fail. There was no convincing improvement in architectural explanation, preservation assessment, scarcity or property-specific desirability.

The best added discovery lead was **Eames Foundation → Friedman Benda**, rank 2 among unrestricted cultural places. It remained rank 2 on the 15-place panel, the eight-place subset and the Ray-author panel. The gallery's [2018 exhibition record](https://www.friedmanbenda.com/exhibitions/inside-the-walls-architects-design-curated-by-mark-mcdonald/) includes Charles and Ray Eames and their ESU furniture. This is a defensible architecture-to-collectible-design connection, absent from our frozen B. It suggests a useful next cultural stop or reading lead. It does not validate the affinity score or imply a market of Eames-house buyers.

Farnsworth → Wrightwood 659, rank 5, was another plausible discovery lead: the venue [describes its architecture and socially engaged art program and Tadao Ando building](https://wrightwood659.org/about/). Geographic proximity remains a major alternative explanation; this lead did not receive the same related-input validation as Friedman Benda.

Neither lead proves information unavailable to a capable LLM with better retrieval. The same assistant authored and assessed the comparisons; they were not independently blind. A name absent from one short baseline is a candidate benefit, not proof of model superiority. We found one particularly defensible, perturbation-resistant lead, not the predeclared two across two traditions. The coverage gate also failed. **GO is not justified.** NARROW is justified only by this specific discovery capability, with utility still unvalidated.

## The buyer connection

Architecture, Photography and Home Organization audiences exist. Each audience-to-six-place request returned five places, omitting Jacobs. Eames and Gamble varied; Farnsworth, Fallingwater and Cedar Hill all received the same flat value across the three audiences. Explainability was unavailable. This is insufficient for a complete audience profile or architectural preference comparison.

An audience-conditioned recommendation is not the inverse probability that a visitor belongs to an audience. Neither direction measures residential preference, ability to transact, purchase intent, willingness to pay or an actual price premium. No buyer demographics, demand estimates or premiums were inferred.

## Product decision for October 30

| Direction | Verdict | Practical interpretation |
|---|---|---|
| Discover | **NARROW** | A curated set of supported architectural sites could offer source-backed significance plus a few clearly labeled cultural discoveries. This could be shareable as an editorial experience. Incremental user value from Qloo remains to be tested. |
| Match | **STOP on present evidence** | Property coverage, style signals and audience direction are insufficient for matching homes with buyers. A future user-declared cultural-interest-to-museum recommender is a different, narrower hypothesis. |
| Intelligence | **STOP on present evidence** | Professional provenance research is useful, but Qloo has not shown reliable incremental property intelligence. No condition, scarcity, transaction or premium evidence was established. |

The most interesting tradition was California modernism through the Eames house-associated institution; Farnsworth gave the clearest expected design-brand relationships. Friedman Benda was the most surprising defensible lead. The missing capabilities are consistent search-to-affinity support, reliable architectural style signals, faithful residential-property representation, explanatory evidence and a validated buyer connection.

There is a plausible *commercial hypothesis* around editorial architecture/travel discovery or museum content, not demonstrated willingness to pay. For a hackathon, I would pursue only a small curated Discover concept after the next quick test passes. If the objective must remain unusual-home matching, positioning or valuation, abandon that scope for October 30 rather than disguise a museum recommender as real-estate intelligence.

## Next experiment — small and decisive

Use 8–12 independently selected, supported sites, including another Arts and Crafts house and less famous architecture. Give a provenance-plus-LLM baseline and a Qloo-assisted method equal source access, candidate budgets and description lengths. Present shuffled, unlabeled pairs to a few architecture-interested people. Count useful, independently verified discoveries, preference and wasted/irrelevant leads; ask which places they would actually explore. Include a strong LLM-plus-web-retrieval baseline so Qloo is not rewarded for fixing weak research.

Predeclare a simple requirement: Qloo must produce a repeatable improvement in useful discoveries across multiple traditions, with acceptable coverage and no more unsupported claims. This study alone does not set a statistically powered threshold. Do not add real-estate datasets, a frontend or buyer claims before that incremental benefit is demonstrated.

See [coverage and API limitations](COVERAGE_AND_API_NOTES.md), [frozen plan](UNCOMPARABLE_EXPERIMENT_PLAN.md), and [reproduction instructions](README.md). Four offline math tests passed; all raw response hashes and frozen baseline hashes were checked.
