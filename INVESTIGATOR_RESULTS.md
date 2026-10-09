# Taste Investigator: implementation and evidence

The app now has a real NVIDIA-driven action loop over Qloo evidence. It is playable locally with the existing Qloo key and the supplied NVIDIA key; no OpenAI key, new dependencies or deployment are required. This is a prototype of adaptive play, not evidence that the agent predicts taste better than a fixed shortlist.

Archived JSON filenames below refer to `research/investigator/runs/`; selected screenshots are in `docs/verification/`. New comparison runs still write to ignored `test-results/`.

## What makes the decisions

`investigator.py` owns one persistent state per round: original typed interests, scored candidates, shown predictions, explicit feedback, domain-fit hypotheses with low/medium confidence, unavailable categories, influence results, budgets and public action receipts. The model receives that state and selects one schema-validated action. Invalid IDs, repeats, unobserved hypothesis citations, ineligible queries and premature verdicts are rejected.

The six actions are QUERY_QLOO, TEST_PREDICTION, INVESTIGATE_CONTRADICTION, CHANGE_DOMAIN, ANALYZE_INFLUENCE and DELIVER_VERDICT. Query and domain-change actions fetch actual new Qloo evidence; prediction actions must name an unseen scored candidate. A confirmed query adds up to two explicitly liked predictions to the original typed signals. Rejection never invents a negative Qloo signal, and unfamiliarity never becomes dislike. Sparse, flat or unsupported discovery results are recorded and excluded.

Qloo contributes entity resolution, typed tag/audience support, scored affinity candidates and fixed-panel input-removal evidence. The model contributes selection of tools, candidate, next domain, hypotheses and short observations based on the feedback history. Code retains authority over metrics, validation, allowed tools, request destinations, budgets and final verdict categories. All model prose is escaped before display. No arbitrary execution or URLs are available to the model.

The original two-domain leave-one-out analysis remains tied to the **original** selections and frozen panels. Later liked predictions never alter that calculation. Audience removal still measures changing cohort context, not the personal importance of a hobby. Accuracy is confirmed / (confirmed + rejected), with unfamiliar answers excluded and fewer than three familiar answers flagged as insufficient evidence.

Bounds: five questions, ten model calls, at most three model steps per turn, three discovery queries and 32 logical Qloo requests per investigation. Existing global Qloo cache and request caps remain. Model requests have a 30-second timeout, no automatic retries and a 150-call default process cap. Failures switch to a visibly labeled fixed-Qloo continuation. A failed final observation uses deterministic closing copy and is separately traced. Fallback runs are never counted as successful live-agent demonstrations.

## NVIDIA feasibility

Authenticated structured tool calls worked with `nvidia/nemotron-3-super-120b-a12b`, the selected default. The key is read on the Python server from environment / ignored `.env`; it never reaches the browser. There is no paid-provider fallback.

NVIDIA advertises [free development endpoints](https://docs.api.nvidia.com/nim/docs/run-anywhere). [Nemotron Super's official page](https://build.nvidia.com/nvidia/nemotron-3-super-120b-a12b) identifies the hosted model. Availability and limits are service/account dependent; this is not an unlimited public-production entitlement. We did not inspect the user's account balance or promise a particular quota.

Capability failures matter: Kimi K2.6 was listed in the model catalog but returned HTTP 404 for inference with this key; Kimi K3 exceeded the 30-second game timeout in both probes. Nemotron Lightning completed some runs but was overly repetitive and timed out in other paths. These attempts remain in `research/investigator/runs/`; successful examples were not substituted for failed attempts in their original files.

The preceding Sites investigation found no native inference capability in the documentation/runtime examined. Hosting this Python app as a Site would require backend adaptation and would not automatically supply model inference. That rewrite and deployment were not performed.

## Controlled comparison

`compare_investigators.py` uses one saved real-Qloo pool for all modes, five questions and the same scripted feedback scenarios. Mode A sees names/types only; B uses the fixed sequence; C sees Qloo scores and input-removal evidence. Stable ID ordering prevents the model from receiving Qloo rank through candidate position. For this inexpensive offline-Qloo test, no mode can fetch new candidates. `--forced-prefix 2` gives every mode the same first two items (Moon and Control), isolating subsequent choices.

The final Super run in `research/investigator/runs/final-three-mode-comparison.json`, after tightening action validation, produced:

| Mode | First two answers | Subsequent predictions | Model time for remainder |
| --- | --- | --- | --- |
| A: titles only | yes, yes | Primer; Ex Machina; Gattaca | 14.86 s |
| A: titles only | no, no | Primer; Ex Machina; Gattaca | 12.67 s |
| B: fixed Qloo | yes, yes | Children of Men; The Outer Worlds; Gattaca | no model |
| B: fixed Qloo | no, no | Children of Men; The Outer Worlds; Gattaca | no model |
| C: Qloo + model | yes, yes | Primer; Ex Machina; Gattaca | 16.44 s |
| C: Qloo + model | no, no | Gattaca; Primer; Children of Men | 14.69 s |

All six completed without a fixed fallback. **Adaptation is modest:** C changed both order and one of the three subsequent titles, but all later selections were movies. A did not change selected items in this pair. An earlier run (`neutral-order-comparison.json`) changed C's fourth/fifth selections but not its immediate third guess. These few runs cannot separate feedback effects from model sampling variability, establish robust adaptation, or prove that Qloo improves relevance. The seed pool is already Qloo-selected even in A, so A is a within-pool ablation, not a completely independent no-Qloo recommender. The protocol below includes a stronger independent baseline.

Earlier Lightning tests made the same initial subsequent choices after likes and dislikes; unfamiliar/contradictory runs hit fallback. Those negative findings motivated model and input-order changes; they are not evidence of success. Scripted yes/no rates are imposed by the test, **not measured recommendation accuracy**. No human results are claimed.

## Verification and interpretation

Automated tests exercise positive/negative feedback plumbing, unfamiliarity, contradictions, unsupported signals, sparse/flat/failed Qloo discovery, missing/failed model responses, invalid actions, question/call exhaustion, typed query composition, duplicate answers and fixed-panel preservation. Transport tests verify structured function handling and exclusion of private reasoning. These tests use explicit fixtures, not fake live LLM evidence.

Fifty Python tests and seven JavaScript tests pass. Browser and edge-case live results are recorded below. The existing recorded mode remains an offline six-question example-profile game; it is never presented as an adaptive session.

The first Super unfamiliar and contradiction probes also exposed invalid hypothesis references / repeat selections and correctly entered fixed fallback (`edge-feedback-comparison.json`). Listing permitted IDs in the schema and returning the rejected public action allowed the contradiction rerun to complete: Moon, Control, Primer, Gattaca, Children of Men; two yes, two no, one unfamiliar; 2/4 familiar confirmed, 12.48 seconds for the controlled remainder (`constrained-edge-feedback.json`).

The unfamiliar-only path still tried to assert a promising preference without familiar feedback. The final schema/instruction explicitly requests no preference hypotheses until a familiar answer exists. Its subsequent live run completed all five unknown answers, kept accuracy undefined with denominator zero, and did not use fixed fallback (`no-familiar-feedback.json`, 11.70 seconds for the remainder). Validation also rejects a promising hypothesis supported only by unfamiliar answers. Earlier failures remain saved.

One complete positive browser round used Moon, Primer, Upstream Color, Children of Men and Her, then showed 5/5 familiar confirmed and no supported ranking winner. It used nine model calls including rejected actions; the final model observation failed validation and the UI used its honest deterministic closing line. The full positive trace is saved as `browser-positive-trace.json`. This is a scripted browser check, not a participant's taste data.

The corrected mobile browser path presented the same Moon and Primer first; rejecting both led to Ex Machina, versus Upstream Color after two yeses in the earlier browser run. It then presented Gattaca and Children of Men. Responses no/no/unknown/yes/no produced exactly **1/4 familiar confirmed, 1 unfamiliar, 5 shown (25%)**, with no supported ranking winner. This round stayed agentic for all predictions, used seven model calls and a deterministic closing fallback. Its validated session export is `browser-mixed-session.json`. The earlier browser start that fell back is separately preserved as `browser-initial-fallback.json`; browser runs straddled schema fixes, so the same-code controlled comparison above is the cleaner branching check.

Mobile checks at requested 390px and 320px viewports had no horizontal overflow (content widths 375px and 305px after scrollbars). The existing mobile CSS hid observations; the focused fix makes agent observations visible. `mobile-investigator.png` shows the changed third guess and all response controls. `mobile-verdict.png` captures the complete narrow result. This is browser viewport testing, not a physical-phone study.

The PNG preview generated a visually checked 1080×1350 card with investigator labeling and separate measurements (`investigator-share-card.png`). The in-app browser did not expose a session-file download event, so the export now also offers a copyable JSON backup, parsed and checked in the browser. Clipboard delivery also could not be confirmed; copy now immediately exposes selectable text and uses a bounded clipboard attempt. A complete offline round verified that backup is visible and preserves the recorded-example label. These limitations are not counted as successful native downloads/clipboard delivery. Native sharing on phones remains untested. Browser error logs were empty at the end, and the temporary viewport override was reset.

## Small human evaluation

Recruit 9–12 consenting participants for exploratory testing. Collect three to five explicit interests; avoid collecting demographics. Randomize/counterbalance A/B/C order and keep layout, question budget and response controls the same. Warn participants that this is a tiny taste game, not a personality assessment. Do not silently collect their sessions.

For the within-pool test, use the same neutral-order candidates in A/C and the documented fixed ordering in B. Keep rejected/unknown semantics identical. Avoid showing the same item repeatedly across modes; record exposure and either use separate matched pools or separate participants per condition. Separately test a true no-Qloo baseline where the LLM proposes candidates and a neutral catalog verifies identity: report catalog/support differences instead of pretending the candidate sets are identical.

Collect familiar-item confirmation with its denominator, unfamiliar fraction, perceived novelty (1–5), enjoyment (1–5), perceived learning from feedback (1–5), completion time, dropouts, fallback frequency and voluntary share intent. Ask one open question: “Which answer changed what the investigator did?” Inspect traces against that account. Report participant-level results and uncertainty; do not pool repeated answers as independent people or claim significance from a handful of sessions. Do not interpret scripted benchmark rates as human relevance.

Decision gate: only strengthen the hackathon claim if participants notice useful feedback-driven changes and C improves something worth its latency over B. If not, keep the simpler fixed experience and report that the agent added narration and cost without demonstrated value. Next technical work should emphasize repeated counterfactual runs and genuinely different held-out domains, not more elaborate personality scores.
