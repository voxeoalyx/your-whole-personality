# Activity signals investigation

## Plan (before live probes)

1. Resolve Pilates, running, yoga, weightlifting and architecture using `/v2/tags` and `/v2/audiences` on the configured hackathon origin. Inspect actual names, IDs and taxonomy; never synthesize IDs or silently broaden a concept.
2. Combine each plausible exact representation with Radiohead and Blue Bottle Coffee. Discover and score fixed 20-item TV/movie panels, compare against entities alone, and inspect warnings, finite affinities, rank distances and top-three changes. Score additional representations when taxonomy has materially different meanings.
3. Run the existing full leave-one-out procedure on viable mixed profiles, including a profile with entities, a tag and a hobby audience. Keep the same panels and scoring thresholds. Separately describe audience removal as removing cohort context; native family weights are not equal measures of personal importance.
4. Extend the existing picker only after evidence supports it. Keep typed IDs, clear labels, explicit unsupported feedback and existing 3–5 picks/six guesses/remix mechanics. Limit audience lookup to voluntary hobbies; do not infer demographic membership.
5. Test routing, ignored signals, missing/flat scores, mixed removals, baseline compatibility, HTTP input validation, and the browser picker/game flow.

Raw responses and exact request parameters are kept locally in versioned `research/prototype/activity-signals/`. No credentials are recorded. Results below will distinguish scored model sensitivity from validated human relevance.

References inspected October 8, 2026: [Tags search](https://raw.githubusercontent.com/qloo/docs-public/main/reference/get-tags.md), [Find audiences](https://raw.githubusercontent.com/qloo/docs-public/main/reference/get-audiences.md), [audience semantics](https://raw.githubusercontent.com/qloo/docs-public/main/docs/audiences.md), [Insights parameters](https://raw.githubusercontent.com/qloo/docs-public/main/reference/insights-api-deep-dive.md).

## Findings

**Extend the picker, with explicit meanings and coverage checks.** Running, yoga and architecture have usable hobby audiences on `https://hackathon.api.qloo.com`. Architecture and yoga also have usable content tags. Pilates and weightlifting did not produce useful activity-specific recommendation signals in these tests. A successful HTTP response and a decimal affinity are not enough.

Baseline: Radiohead + Blue Bottle Coffee. Two independently fixed 20-entity panels were discovered from that entity-only baseline, then held constant for every added signal. All 12 tested representations returned 20 scored items in both TV and movies, without not-found warnings. The table reports `(1 - Spearman rho) / 2` against the entity-only baseline, not accuracy or personal importance.

| Interest / exact representation | TV distance | Movie distance | Finding |
| --- | ---: | ---: | --- |
| Pilates studio: place genre or category tag | 0.000 | 0.000 | Flat singleton signals; unusable here |
| Pilates: occupation tag | 0.000 | 0.000 | Flat, and an occupation is not an activity preference |
| Running: podcast genre tag | 0.000 | 0.000 | Flat singleton signals in four tested output domains |
| Running: hobby audience | 0.173 | 0.151 | Scored, changes rankings and top three |
| Yoga: music genre tag | 0.000 | 0.000 | Nonflat standalone results; a different mixed shortlist shows influence |
| Yoga: hobby audience | 0.359 | 0.132 | Scored, changes rankings and top three |
| Weightlifting area: place genre or category tag | 0.000 | 0.000 | Flat singleton signals; unusable here |
| Weightlifting: occupation tag | 0.000 | 0.000 | Flat; not a hobby representation |
| Architecture: book genre tag | 0.043 | 0.117 | Scored, changes rankings and top three |
| Architecture: hobby audience | 0.246 | 0.135 | Scored, changes rankings and top three |

Examples on those fixed panels: Running moved **UnREAL** into TV's top three, with affinity **0.953918**, and **Lady Bird** to first among movies (**0.921975**). The Yoga audience put **Tomorrow with You** first in TV (**0.949598**). The Architecture book tag put **Marriage Story** first among movies (**0.874672**); the Architecture audience instead put **Lady Bird** first (**0.937979**). These are model outputs, not evidence that runners or yoga practitioners actually like those titles. Some associations are surprising, and no participant relevance ratings were collected.

Standalone tag probes, including useful tags, lacked explainability. The warning alone therefore does not establish failure; flat scores on multiple panels and unchanged mixed rankings are the stronger evidence. These experiments support conditional recommendation signals, not explanations of why people like the results.

### What exactly failed for Pilates and weightlifting?

`/v2/audiences?filter.query=pilates` and the weightlifting equivalent returned empty audience lists. A complete 42-item hobby-audience listing also had neither; searches for fitness, weight, strength and bodybuilding found no audiences. A separate “weight lifting” spelling did not reveal an exact activity audience.

Pilates resolved to `urn:tag:genre:place:pilates_studio`, `urn:tag:category:place:pilates_studio`, and `urn:tag:occupation:wikidata:pilates`. Weightlifting resolved to the corresponding `weightlifting_area` place genre/category tags and `urn:tag:occupation:wikidata:weightlifting`. Each of those six tags produced **20 identical affinities of 0.7649962877984056** in each of TV, movies, brands and games. Their standalone responses warned “Could not calculate explainability.” Combined with the entity baseline they changed the score scale but not any rank; several unrelated flat tags yielded identical score vectors. That is not a useful specific activity signal. There was no authentication or endpoint-access failure.

Other nearby-location, restaurant/hotel and instructor variants are not validated as representations of doing the activity. The picker excludes occupation and nearby-attraction taxonomy, shows place categories as place categories, and checks any selected tag before accepting it. It never chooses a substitute.

**A legitimate broader option exists, with a different meaning:** `urn:tag:genre:media:fitness` (Fitness; books/podcasts genre) and `urn:tag:genre:media:health_fitness` (Health & Fitness; podcasts genre). These describe content preferences, not Pilates or weightlifting participation. Fitness had weak movement on the fixed baseline (TV 0.008, movies 0.000). Health & Fitness moved rankings more (TV 0.044, movies 0.299). Its first 20 standalone results were tied, but a separate Radiohead-derived fixed panel exposed nonflat standalone scores in both domains. Therefore the validator checks a second panel before rejecting tied top results. Neither broader tag is automatically added for Pilates. Exercise's games-genre tag did not help on these panels.

### Exact usable IDs and semantics

- Running: `urn:audience:hobbies_and_interests:running`
- Yoga: `urn:audience:hobbies_and_interests:yoga`; separately `urn:tag:genre:music:yoga` means yoga music.
- Architecture: `urn:audience:hobbies_and_interests:architecture`; separately `urn:tag:genre:media:architecture` means architecture books.

Audience **URN IDs**, not their companion `entity_id` UUIDs, go to `signal.demographics.audiences`. Tags go to `signal.interests.tags`; entities retain `signal.interests.entities`. The audience search's `filter.query` and hobby parent restriction were verified live. Audience normalization also checks the returned type locally. Other demographic audience classes are not offered.

No custom weights were tuned. Qloo exposes separate family weights, so deleting a cohort signal is not semantically equivalent to deleting a named favorite. Audiences influence scores through aggregate group tastes; selecting one is voluntary context, not a claim that we inferred someone's demographics. A rank distance remains mathematically comparable as response sensitivity at these settings, but cannot establish equal personal importance, causality, or psychological traits.

## Game mechanics check

Six complete live games used the existing discovery → fixed full panel → each-input removal procedure: each of the three audiences separately, each of the two usable tags separately, and a five-input mix with both entities, Architecture's book tag, Running and Yoga audiences. All produced six finite scored guesses, two complete panels and every removal. The five-input result had mean distances **0.556** for the architecture tag, **0.282** for Running's cohort, **0.200** for Yoga's cohort, **0.177** for Radiohead and **0.105** for Blue Bottle. It correctly named **no clear winner** because the leader was not more than twice the runner-up. The yoga-music mix identified Radiohead under the unchanged rule.

The original rank formula and winner thresholds are unchanged. Each removal now deletes exactly one typed input from its proper family and retains all other families and candidate IDs. Empty families are omitted. Tags exclude their documented parent entity categories from output selection; an audience has no entity output category. Missing or flat comparisons still cannot support a winner. Original entity-only recordings still recompute identically.

**Panel dependence is material.** Architecture's tag moved the common entity-only panels by a mean 0.080, versus 0.502 on its own mixed-profile panels. Yoga's music tag had zero rank movement on the common panels but 0.225 on its mixed-profile panels. Those are different conditional measurements, not contradictory estimates of a universal effect. Do not compare scores from different games as calibrated influence. None of these tests validate human relevance.

## Focused implementation

- Search now combines entities, tags and explicit hobby audiences, with separate category filters and exact-name hobby matches ahead of incidental titles. Distinct types retain distinct IDs and labels, including in selected chips, removal results and exported session data.
- A tag/audience must provide nonflat scored recommendations in two output domains. Tied top results get one alternative fixed-panel check. Actual round domains are checked again, using the existing memory cache. Ignored-signal warnings are checked for all three families; entity results cannot mask a rejected tag.
- Pilates/weightlifting searches explain the known limitation. Partial endpoint failure is visible while successful sources remain usable. No new dependencies, account storage or feedback upload.
- Search needs up to three calls; context validation normally adds two singleton calls per tag/audience, plus up to four calls if an alternate panel is needed. These are cached; all share the original timeouts and process budget. Conservative validation can reject sparse signals that work only in narrower contexts.

## Reproduce and evidence

From this app directory, run `python probe_activities.py --live --phase lookup`, then phases `compare`, `coverage`, `mechanics`, and optionally `broader`. Research requests reuse saved raw bytes only when their SHA-256 matches the metadata; live application requests never load this disk cache. Remove or relocate only this investigation's cache if intentionally collecting a new snapshot.

The primary investigation captured **169 successful requests** locally (150 Insights, 8 tag lookups, 11 audience lookups), including supplemental spelling/broader-category checks. One connection failure was resumed from cache. Additional browser validation requests use the ordinary application memory cache and are not archived as research.

- `research/prototype/activity-signals/raw/`: original responses plus exact parameters, request hashes, response hashes and timestamps.
- `comparison.json`, `coverage.json`, `broader.json`: the measurements above.
- `game_1.json` through `game_6.json`, `mechanics.json`: full example-game outputs and removals.
- `health_fitness_validation.json`: successful alternative-panel validation for the broader content tag.

These captures concern predefined public example interests, not player reactions. Future taxonomy/model changes, other entity mixtures and independently chosen panels may change the outcomes.
