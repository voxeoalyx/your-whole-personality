# Release preparation — October 21, 2026

Deployment branch adds durable provider ceilings, visitor quotas, bounded HTTP connections, atomic admission, stateless recorded rounds, Docker/Render configuration, MIT source license with third-party exclusions, a clean-export allowlist, and Devpost materials. No public deployment, public source publication or Devpost submission is claimed. See docs/RELEASE_AUDIT.md and docs/DEPLOYMENT.md for current scope and blockers.

The transfer notes below describe the earlier October 9 baseline.

# Project status

Transfer baseline: October 9, 2026. A working local prototype, with all earlier research retained. No public deployment or real-player study has been completed.

## Working

- Four-act taste game; three to five typed picks (entities, supported cultural tags, explicit hobby audiences), Qloo-backed cross-domain predictions, fixed-panel leave-one-out comparisons and deterministic verdicts.
- Persistent NVIDIA Taste Investigator: six bounded structured actions, feedback-dependent queries/choices, five live questions, public evidence trace, visibly labeled fixed-Qloo fallback. No OpenAI key required.
- Three offline recorded example profiles, six guesses each; PNG preview/export, copyable verdict and JSON session backup.
- Server-only Qloo/NVIDIA keys, request budgets, timeouts, origin/host checks, in-memory expiry; no external packages, database or build step.

## Architecture

`server.py` serves the API/static assets and owns jobs. `qloo_client.py` handles Qloo requests/cache; `signals.py` handles entity/tag/audience semantics. `game.py` constructs frozen panels; `scoring.py` calculates ranking sensitivity. `model_client.py` calls NVIDIA; `investigator.py` validates actions and manages adaptive state. `static/` is vanilla JS/CSS/HTML; `data/` contains catalog and recordings. `tests/` covers offline Python/HTTP and JavaScript logic. `research/` preserves Civilizr, Uncomparable, Whole Personality, activity and investigator experiments. Keys come only from process variables or this checkout's ignored `.env`.

## Known issues and evidence limits

- Live provider latency/availability varies. Model repetition/schema failures can trigger fallback; a deterministic final observation is sometimes necessary.
- Controlled tests show modest feedback branching, often movie-heavy. There is no demonstrated relevance or engagement advantage over fixed Qloo, and no validated personality score.
- Pilates/weightlifting tags returned flat results; no silent broader-wellness substitution. Hobby audiences measure cohort context, not the importance of a favorite. Books have coverage limitations.
- Original Civilizr studies did not establish a reliable neighborhood cultural leading indicator; read their negative findings before reusing that hypothesis.
- Native mobile sharing/download/clipboard behavior and full accessibility remain unverified. Remote artwork can fail.
- In-memory stdlib backend, no authentication or multi-instance coordination; deployment requires HTTPS proxy, quotas and rights review.

## Recommended next steps

1. Follow [MAC_SETUP.md](MAC_SETUP.md); restore keys privately and rerun offline tests/audit, then a small live round.
2. Observe consenting players with the documented A/B/C protocol; measure useful adaptation, latency, fallback and share intent rather than scripted accuracy.
3. Repeat counterfactual feedback tests and diversify held-out domains; keep scoring/panels honest and unsupported interests explicit.
4. Resolve data/display rights, public abuse limits and real-device sharing before deployment. Avoid a backend rewrite until that need is established.

Transfer validation and secret-audit scope are recorded in [SECURITY_AUDIT.md](SECURITY_AUDIT.md). Historical browser evidence is in [VERIFICATION.md](VERIFICATION.md) and [INVESTIGATOR_RESULTS.md](INVESTIGATOR_RESULTS.md).
