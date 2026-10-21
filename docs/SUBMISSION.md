# Your Whole Personality — Devpost materials

Status: prepared copy, not submitted. No public demo or source URL is claimed yet.

## Tagline

You contain multitudes. The algorithm disagrees. A Qloo-powered taste investigation that lets you challenge its assumptions.

## Inspiration

Recommendation systems compress people into patterns. We wanted to turn that uncomfortable feeling into something playful and inspectable: give an algorithm a few things you love, let it make a case, and push back. The joke is about algorithmic overconfidence; it is not a personality diagnosis.

## What it does

Your Whole Personality is a four-act browser experience. Choose three to five interests; react to cross-category predictions; inspect how removing one interest changes a fixed recommendation shortlist; and receive a shareable verdict. A bounded NVIDIA Taste Investigator uses structured actions and prior reactions to choose its next Qloo-backed question. Players can inspect public decision summaries and evidence receipts.

Three recorded example profiles preserve the four-act game when live providers are unavailable. They contain saved Qloo responses, are labeled throughout the experience and exports, and do not claim to predict a player's own selections. Recorded mode does not run the adaptive live investigator. If only NVIDIA fails during a live round, the application visibly continues with fixed Qloo predictions. If Qloo fails, the player can explicitly choose a recorded profile rather than receiving invented recommendations.

## How we built it

Python serves a vanilla HTML/CSS/JavaScript interface. The server calls Qloo search, insight, tag and hobby-audience endpoints, with typed signals and output categories held out from the inputs. NVIDIA's hosted model selects from a bounded action schema; code validates its actions and restricts predictions to returned Qloo evidence. Metrics and verdict categories are deterministic. Leave-one-out comparisons rescore the same candidate panels, keeping ranking sensitivity separate from player-confirmed predictability.

For judge hosting, the repository includes a Docker image, a Render Blueprint, persistent provider request ceilings, visitor quotas, bounded HTTP connections, a health endpoint, and stateless recorded rounds. Credentials remain server-side. Deployment is single-instance; these controls bound this hackathon demo, not an enterprise service.

## Challenges and what we learned

Searchable interests are not always useful scoring inputs. Some activity tags returned flat rankings; the app refuses unsupported records instead of substituting a broader interest. Cultural affinities are not probabilities or percentages of a person's identity. A missing or flat comparison produces insufficient evidence rather than a dramatic verdict.

Controlled investigator tests demonstrated feedback-dependent control flow, but did not establish a relevance or engagement advantage over fixed Qloo recommendations. Some paths were movie-heavy. The experiment has no validated personality score and no completed real-player study. Fixed-panel comparisons are outcome-selected model sensitivity, not causal influence on a human.

## Accomplishments

A complete four-act game, a feedback-responsive investigator with constrained evidence, inspectable counterfactual comparisons, three reproducible recorded examples, and PNG/text/JSON exports. The app runs without external Python or npm packages. Offline tests cover metrics, typed signals, provider failures, feedback idempotency, recorded labeling, request boundaries, and spend controls.

## What's next

Observe consenting players, measure latency/fallback and useful adaptation, diversify prediction domains, and improve real-device accessibility and sharing. We have deliberately prioritized a reliable judge experience over another feature.

## Built with

Qloo Taste AI; NVIDIA hosted inference / Nemotron; Python; JavaScript; HTML; CSS; SQLite; Docker. Add Render only after deployment succeeds.

## Testing instructions for judges

1. Open the functional HTTPS demo URL supplied in the submission. No account or payment is required.
2. Choose **Play a recorded round**, then select an example profile. Answer the six guesses, inspect **Try without**, and reveal/export the verdict. This route uses saved Qloo evidence and no live provider calls.
3. For the live agent, choose three to five supported interests or a starter mix, then begin. Respond to up to five predictions and expand **Inspect the investigator** to see its actions. Live picks/reactions are sent to the disclosed providers.
4. If the live request allowance is busy/exhausted or a provider is unavailable, use the recorded route. Recorded examples remain accessible independently of live-job capacity. A model-only failure is labeled fixed-Qloo fallback.
5. Influence means ranking sensitivity on a selected shortlist, not a claim about personality or causality. Unfamiliar guesses do not count as wrong.

## Links to fill only after verification

- Functional demo: PENDING verified HTTPS deployment.
- Public source: PENDING reviewed clean repository publication, MIT detection, and anonymous clone/test.
- Optional demo video: PENDING actual screen recording/upload. See DEMO_SCRIPT.md.

## Rules verified October 21, 2026

Official source: https://qloo.devpost.com/rules . Deadline October 30, 2026, 11:45 p.m. Eastern. Working Qloo-integrated agentic application; functional demo link; public repository with detectable open-source license and necessary assets/instructions; English text description; authorized third-party use. Make the application freely accessible to judges until November 16, 2026, 11:45 p.m. Eastern. The reviewed rules do not specify a mandatory video duration; do not import the older Qloo LLM hackathon's three-minute rule. Confirm any additional fields in the authenticated submission form.

The original single commit is dated October 9, within the submission period beginning September 30. Do not claim a separate influencer/brand-matching product: this submission describes the implemented taste game.

## Finish sequence around the Meta overlap

- First: confirm provider data/display and post-event key access through judging; connect Render; review this pull request.
- Then: deploy a single paid instance with persistent disk, verify live and recorded paths, and publish the approved clean source snapshot. Avoid a framework rewrite or new feature work during the Meta overlap.
- Next: record a short actual walkthrough and enter this copy/verified links in Devpost. Aim to finish October 28; use October 29–30 for corrections and availability checks. No schedule or reminder is implied.
- Finally: verify submitted status and anonymous access to source/demo; retain hosting and credentials through November 16. Do not shut the service down at the submission deadline.
