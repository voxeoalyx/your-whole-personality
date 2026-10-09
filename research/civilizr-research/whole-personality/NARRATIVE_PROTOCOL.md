# Fixed narrative protocol

The assistant in this research chat is the LLM. One structured drafting pass per condition; no separate paid model, hidden chain of thought, fine-tuning or independent model judge. Input labels are visible to the drafter, so this is not blind generation. Later evaluators receive randomized labels. Original-demo baseline is additionally exposed to the user's description; report that contamination.

## LLM-only prompt

Given ONLY these named cultural interests, propose three brands and three television titles someone exploring this combination might investigate. Add a two-sentence cultural recommendation summary of 30–55 words. Use tentative language. Do not describe the person's demographics, politics, psychology, health, values, lifestyle, or purchase intent. Cultural associations are hypotheses, not facts about an individual. Return interest list, six named suggestions and summary. Do not use Qloo outputs, scores or commentary.

## Qloo-grounded prompt

Given ONLY the supplied returned recommendation names, native categories, ranks and coverage notes, select three brands and three television titles from the highest-ranked available evidence. Add a two-sentence cultural recommendation summary of 30–55 words. Do not add any entity absent from the evidence. Describe the recommendation mix rather than the person. Do not infer demographics, politics, psychology, health, values, lifestyle or purchase intent. Explicitly qualify missing or flat domains. Return evidence request IDs, six named suggestions and summary. Do not reproduce the user's demo labels unless the supplied evidence directly measures them.

For both conditions, use the same two-sentence structure: one sentence naming the brand suggestions; one naming television suggestions. Avoid decorative personality adjectives. Brand/product and genre labels may be used only when supplied in the relevant evidence. This deliberately constrained narrative tests whether a useful evidence-grounded mechanic remains without speculative storytelling.

## Audit, not self-certification

Record all 12 LLM baselines before live recommendations. If a seed needs substitution, the original baseline remains visible and is marked mismatched; do not silently rewrite it. Keep a separate substitution addendum if needed before the expanded matrix.

For each Qloo narrative audit every named recommendation against the supplied profile response; preserve its rank. Narrative change = Jaccard distance of the six named suggestions (a proxy for content change, not sentiment/meaning). Small = <= 1/3; large = >= 2/3; middle remains middle. Data change uses mean two-domain D where complete: small <= 0.05, large >= 0.15. Report empty quadrant counts rather than invent examples. Also inspect whether own-domain missingness or a tiny gap near rank 3 causes an apparent narrative jump.

These thresholds and constrained summaries do not reveal how Qloo's proprietary demo writes its narrative. No claim of stochastic narrative stability is possible from one drafting pass. Prepare a small randomized packet with a separate key, equal-format descriptions and explicit unanswered human ratings. No assistant ratings count as independent consumer validation.
