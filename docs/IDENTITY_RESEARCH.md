# Identity Reality Check: research protocol v1

Implemented October 25, 2026. This iteration makes the hypothesis testable; it provides no human evidence yet.

## Three separate constructs

Cultural influence is sensitivity of Qloo's fixed shortlist rankings to removing an input. Identity attachment is the player's self-report. Identity transfer is the untested proposition that an association can strengthen attachment to another brand. These are not combined into a score. Neither ranking sensitivity nor prediction confirmation is a percentage of identity.

The optional interaction follows Act IV. Players can choose several original typed inputs, none, decline, or add one short unsupported self-report. Input type and taxonomy remain explicit: an audience signal supplies cohort context, a tag supplies category context, and an entity identifies a cultural item. No unsupported text is resolved, substituted, or sent to either API. The earlier lack of exact Pilates/weightlifting activity coverage is preserved; running/yoga/architecture coverage does not license substitutions.

The deterministic reveal uses the existing descriptive Act III classification, without changing its strict threshold or the agent. A qualified largest leader may agree with one selected interest without earning dominance. Multiple self-reported interests or distributed model influence yield shared control; the record also retains overlap IDs, since shared control does not necessarily mean agreement. None is an explicit answer. Skip and decline yield null classification. Missing/partial comparisons yield insufficient evidence for an overall identity comparison, even when a scoped domain finding remains available in Act III. Zero ranking movement is a measured distributed outcome, not missing data. Generated humor targets model limitations, not the player's psychology.

## Storage and privacy decision

The actual host is a local Python single-process server with temporary jobs/cache, no research database, authentication or deletion service. Disk is technically available, but writing public profiles to it would require a protection/retention system this experiment does not have. We chose voluntary reviewed exports. No new ingestion API, cookies, telemetry, localStorage, accounts or external analytics.

Identity answers remain in tab memory until cleared, a new round or reload. Separate unchecked permissions control (a) including identity in a card/copied text and (b) preparing research JSON. Editing a submitted answer revokes both; revoking sharing clears generated share previews. The original session export excludes the new identity response; original gameplay/export needs neither permission. Research preview is discarded on revocation; downloaded copies cannot be remotely deleted. Recipients of separately shared files must state their own purpose, retention and deletion contact before collection. The app promises no recipient retention duration or nonexistent deletion mechanism. A future pilot should specify a responsible contact and 90-day raw-data deletion before recruiting; that is a proposal, not an implemented service.

Consent prepares a local file, not automatic enrollment or transmission. A random UUID identifies a round's exports without an account or backend job token; repeated previews reuse it. Interest combinations and free text can be identifying: records are pseudonymous, not guaranteed anonymous. Do not publish raw records; screen voluntary text for personal information before analysis. UI requests interest-only text, max 80 characters; control/bidi characters are stripped and HTML escaped. This cannot guarantee players will never enter sensitive information. Decline is always available.

## Versioned schema and analysis rules

[JSON Schema](research-record.schema.json) is generated from `static/research-schema.js`; a regression test prevents drift. Runtime validation checks closed object allowlists, consent, enums, IDs, numeric values, answer consistency and recomputed denominators before allowing download. Changes to semantics require an experiment/schema version change. No whole game, model response, hidden reasoning, API keys, request headers or conversations enter the research record.

Fields: schema/experiment/consent/scoring/influence versions; record UUID; explicit consent scope/time; live versus recorded source and evidence date; model provider/name/fallback; input IDs/types/taxonomy/support; shown prediction IDs/domains/order/reactions and whether already an original input; removal means/domain distances/half checks and strict winner; identity status, selected IDs, separate unsupported text; comparison and overlap IDs; prediction denominators. Missing numeric comparisons are null, never zero-filled. Qloo's internal model version is not exposed: API version and evidence date are provenance, not a vendor-model fingerprint.

Analysis specification:

| Question | Eligible denominator / measure |
| --- | --- |
| Strongest model influence matches identity | Consenting live records with answered identity, complete overall comparison and a unique dominant/largest leader. Report matches/eligible, split strict vs qualified. None is eligible non-match; multiple selections can contain a match via overlap IDs. Report shared and insufficient strata separately. |
| Interest categories associated with attachment | Within consenting live answered records: selected identity inputs / originally offered inputs per type; cluster by round and report opportunity counts. Unsupported text has no inferred Qloo category. No population inference from convenience samples. |
| Vocabulary gaps | Answered live records containing unsupported text / all answered live identity records. Also report count of text responses. This is a reported coverage gap, not independently verified absence from Qloo. |
| Predictability vs attachment | Complete familiar-response denominators, with at least three familiar guesses; compare attachment to the modeled leader or selection count, not invented attachment intensity. Report sample sizes and uncertainty; no intensity scale exists here. |
| High model influence necessarily identity-defining? | For each input with finite measurements and answered identity, compare removal distance with selection indicator. Cluster by round, stratify entity/tag/audience and output domain; avoid treating inputs as independent people. |
| Agreement by signal type | Same unique-leader eligible set, stratified by leader type, with numerator, denominator, missing/partial counts. |
| Correct previously unreported predictions | For live non-fallback agent rounds: confirmed predictions outside original inputs / familiar predictions outside original inputs. Unfamiliar and unanswered counts reported separately. Sequence supports early/late descriptive comparisons; adaptation makes these non-independent. IDs absent from inputs do not prove a preference was unknown in the wider world. |

Keep recorded example rounds separate from personal profiles and real-agent rounds separate from fallback. Retain null/skipped/declined separately from none. Report all exclusions and source/version counts before rates. Deduplicate record IDs; this prevents duplicate file imports, not repeat players. No stable user tracking means repeat-player independence cannot be established. Export-only records cannot estimate overall game completion, consent or skip rates: use separately consented moderated observation for those denominators.

The reveal is shown before self-report and can anchor answers. This version measures post-reveal agreement, not an independent psychological criterion. A later preregistered study should randomize question timing (before/after reveal), retain unchanged wording, and compare against repeated self-reports and observable behavior. Do not add those changes silently to this experiment.

## Agent and Qloo contribution

NVIDIA still chooses validated actions from accumulated feedback and scored candidate evidence. Rejected/unfamiliar answers do not become positive Qloo inputs. Qloo supplies typed cross-domain recommendations, fixed-panel scores and removal evidence. Removing Qloo would remove those grounded candidate constraints and influence comparisons; an LLM's prose alone cannot reproduce those receipts. The new reveal uses deterministic copy and no additional inference calls. The public investigator trace retains strict dominance and provider/action evidence; private reasoning is excluded. No superiority over an independently evaluated LLM-only baseline has been demonstrated.
