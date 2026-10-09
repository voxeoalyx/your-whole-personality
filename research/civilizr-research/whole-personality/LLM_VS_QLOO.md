# LLM versus Qloo: evidence, not a quality contest

The LLM-only suggestions were frozen before this run's Qloo recommendations. Both outputs are from one assistant drafting pass under the fixed protocol. No human ratings have been collected. Literal overlap is not accuracy, and novel names are not proof of useful novelty.

This is not a fair predictive benchmark yet: Qloo selects from 45 brands and 19 TV titles; the LLM can name anything, including an input brand. The TV panel was selected from the original Qloo contrasts. The original demo description was already known to the LLM author. A second study must equalize candidate access or compare unrestricted recommendations from both methods, using held-out people and interests.

## All profiles

| Profile | Qloo brands / TV | LLM-only brands / TV | Eligible? |
|---|---|---|---|
| p01 | Vice, Whole Foods Market, The New York Times / Black Mirror, Devs, Electric Dreams | Aesop, MUJI, Patagonia / Black Mirror, Mr. Robot, Dark | Yes |
| p02 | Vice, Whole Foods Market, National Audubon Society / Comedians in Cars Getting Coffee, Lady Dynamite, Adam Ruins Everything | Onnit, Monster Energy, Under Armour / The Last Dance, Formula 1: Drive to Survive, Mindhunter | Yes |
| p03 | Vice, Whole Foods Market, National Audubon Society / Comedians in Cars Getting Coffee, Adam Ruins Everything, UnREAL | Garmin, Lululemon, Patagonia / Limitless with Chris Hemsworth, The Mind, Explained, Abstract: The Art of Design | Yes |
| p04 | Kate Spade New York, Victoria's Secret, Chanel / UnREAL, My Mister, High Maintenance | Aesop, Uniqlo, Converse / Only Murders in the Building, The Bear, Fleabag | Yes |
| p05 | Victoria's Secret, Calvin Klein, Forever 21 / UnREAL, My Mister, Forever | Target, Nike, Starbucks / New Girl, How I Met Your Mother, The Good Place | Yes |
| p06 | Victoria's Secret, Vans, Instagram / UnREAL, Search Party, Lady Dynamite | Nike, Monster Energy, Garmin / The Last Dance, Ted Lasso, Formula 1: Drive to Survive | Yes |
| p07 | Playstation, Air Jordan Product Line, Mercedes-benz / Rake, Baskets, High Maintenance | Razer, Vans, Monster Energy / The Witcher, Arcane, The Last of Us | Yes |
| p08 | Playstation, Youtube, Air Jordan Product Line / Rake, Comedians in Cars Getting Coffee, Baskets | Nintendo, Uniqlo, Vans / Adventure Time, The Good Place, Avatar: The Last Airbender | Yes |
| p09 | Whole Foods Market, West Elm, Kate Spade New York / Old Enough!, Adam Ruins Everything, UnREAL | REI, Allbirds, Garmin / Our Planet, Abstract: The Art of Design, Chef’s Table | Yes |
| p10 | Vans, Victoria's Secret, Alex and Ani / Old Enough!, Adam Ruins Everything, Comedians in Cars Getting Coffee | The North Face, GoPro, Vans / Formula 1: Drive to Survive, The Last Dance, Top Gear | Yes |
| p11 | Gucci, Louis Vuitton, Christian Dior / Devs, Humans, Silo | MUJI, Aesop, Camper / Dark, Twin Peaks, Black Mirror | No: Dune ignored |
| p12 | Louis Vuitton, Gucci, Calvin Klein / Black Mirror, Humans, Electric Dreams | MUJI, Uniqlo, Converse / The Good Place, Pushing Daisies, Fleabag | No: Dune ignored |

## Change in the evidence versus change in the description

Named-content distance is Jaccard distance between the six named suggestions. It is not a semantic or psychological measure. Data distance is the mean of two fixed-panel rank distances. Thresholds were frozen in NARRATIVE_PROTOCOL.md.

| Swap | Mean data D | Named-content distance | Category |
|---|---:|---:|---|
| p01 to p02 | 0.473 | 0.800 | large data / large narrative |
| p01 to p03 | 0.389 | 0.800 | large data / large narrative |
| p01 to p04 | 0.283 | 1.000 | large data / large narrative |
| p05 to p06 | 0.078 | 0.800 | middle data / large narrative |
| p07 to p08 | 0.018 | 0.500 | small data / middle narrative |
| p09 to p10 | 0.074 | 0.800 | middle data / large narrative |

The original replacement and the other two original-profile variants are large/large. The mainstream and brand-heavy swaps are middle/large. The gaming swap is small/middle. There are zero small/large and zero large/small examples under the frozen cutoffs; those quadrants cannot be populated honestly.

The brand-heavy pair retains the identical top-five TV set but changes one of the three TV names in the summary. This is a visible compression effect from showing three names. Rank-3/rank-4 native score gaps are in tables/narrative_cutoff_gaps.csv; these are within-query diagnostics, not calibrated uncertainty or comparable probabilities.

The constrained narratives contain only returned recommendation names and tentative exploration language. This prevents most personality overclaiming by design; it does not test an unrestricted storyteller or recreate Qloo's demo prompt. No stochastic narrative repeats were run. Potentially counterintuitive outputs, such as fashion brands from the Monster substitution and PlayStation from a Nintendo-game input, are data leads requiring user judgment, not evidence that the person's identity changed.

## Independent checks and pending validation

Qloo's unrestricted Severance-alone output ranks Apple Inc. second. [Apple's official Severance page](https://www.apple.com/tv-pr/originals/severance/) confirms the association. Both the Joe Rogan person and podcast singleton outputs rank Onnit first; [Onnit's Joe Rogan publication](https://onnit.s3.amazonaws.com/digital-downloads/ebooks/Joe%20Rogan%20-%20The%20Facts%20of%20Life.pdf) independently documents that association. These are two post-hoc relationship sanity checks, not held-out consumer predictions. The frozen LLM-only original Rogan case also suggests Onnit, so that observation supplies no evidence of Qloo's superiority. Neither check establishes relevance to a person with the mixed interests.

Give evaluation/BLINDED_PACKET.md to evaluators without evaluation/answer_key.json or these results. The packet standardizes wording, randomizes option labels deterministically and leaves all ratings blank. It tests hypothetical-profile coherence and potential usefulness; it cannot establish personal prediction accuracy unless the evaluator actually has those interests. Run a separate matched-input test with real volunteers before a product decision.
