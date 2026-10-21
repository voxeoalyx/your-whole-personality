# Your Whole Personality

**You contain multitudes. The algorithm disagrees.**

A four-act taste investigation: select 3–5 interests, challenge Qloo-backed predictions, inspect how each interest changes a fixed recommendation shortlist, and export a verdict. NVIDIA's bounded Taste Investigator chooses structured actions based on your reactions. The model cannot invent candidates or compute personality metrics.

## Run locally

Python 3.10+ and a browser; no pip/npm runtime dependencies:

```sh
cp .env.example .env
# Add server-only QLOO_API_KEY and optional NVIDIA_API_KEY privately.
python server.py
```

Open http://127.0.0.1:8765 . Three recorded example profiles work without keys. They are saved Qloo results, explicitly labeled as borrowed profiles; recorded mode does not run the adaptive investigator. They remain playable when live quotas or provider access fail. If NVIDIA alone fails, live play continues with visibly labeled fixed Qloo predictions. If Qloo fails, choose a recorded round explicitly.

The default model is `nvidia/nemotron-3-super-120b-a12b`. Credentials are read from process variables or an ignored local `.env`, never the browser. Do not share keys in chat, code, URLs, screenshots or submission materials.

## HTTPS judging deployment

No public deployment is claimed yet. Use the Dockerfile and Render Blueprint, one paid instance with a persistent budget disk, and the fail-closed `serve_public.py` entrypoint. Read [deployment instructions](docs/DEPLOYMENT.md) for exact settings, rights confirmation, quotas, acceptance checks and known limits. Keep judge access active through November 16, 2026. Public source publication requires a separate reviewed snapshot; do not publish the existing private research archive.

The app enforces server-side request ceilings, visitor quotas, atomic live-job admission, bounded HTTP connections, input/origin checks, provider timeouts and no automatic retries. Recorded rounds are stateless and independent of live-job capacity. Durable budgets require the mounted SQLite file. Visitor counters and live sessions remain in memory; this is a single-instance hackathon deployment.

## Evidence and limitations

Qloo supports typed entities, cultural tags and explicit hobby audiences. Unsupported/flat records are refused without broader substitutions. Predictions use held-out output categories. Public investigator summaries show actions and evidence, not hidden model reasoning.

“Try without” compares fixed candidate panels with one input removed. Influence is mean `(1 − Spearman rank correlation) / 2` across two complete, nonflat output domains. A clear winner must exceed 0.10, more than twice the runner-up, and win on both disjoint panel halves. This is outcome-selected model ranking sensitivity, not human causality or statistical significance.

Predictability is confirmed guesses divided by confirmed plus rejected guesses. Unfamiliar guesses are excluded; fewer than three familiar guesses is insufficient evidence. Metrics are kept separate. There is no validated personality score. Controlled tests demonstrate modest feedback branching, sometimes movie-heavy; no real-player study or relevance/engagement advantage over fixed Qloo has been established. Native mobile sharing/accessibility remain incompletely verified.

## Privacy

Live searches/picks go to Qloo. Live evidence, picks and explicit reactions go to NVIDIA for inference; explicitly liked predictions may become later Qloo signals. Reactions/session state stay in server memory; rounds expire after 30 minutes after bounded work completes, and search caches after two hours. Provider retention follows provider terms. Recorded reactions stay in the browser tab. No accounts, analytics, localStorage or cookies are used. User-triggered JSON exports contain selections, reactions and evidence; share deliberately. Remote artwork may contact its provider. App access logs omit interests; hosting logs are separate. The spend database stores only counters; anonymous quota identifiers stay briefly in memory.

## Validate

```sh
python -m unittest discover -s tests -v
node --test tests/logic.test.js
python tools/audit_repository.py --history
```

Node is only needed for JavaScript tests. The selected raw fixtures let tests verify recorded-response hashes and provenance without credentials. Qloo output in fixtures is separately governed by provider terms.

## License and submission

Original application source is [MIT licensed](LICENSE). Provider output, remote images, marks and archived third-party material are not relicensed: see [third-party notices](THIRD_PARTY_NOTICES.md). Public distribution of saved provider data still needs applicable permission.

[Devpost copy and judge instructions](docs/SUBMISSION.md), [demo recording script](docs/DEMO_SCRIPT.md), and [release audit](docs/RELEASE_AUDIT.md) describe the implemented project and remaining release gates. The public-export tool uses an explicit file allowlist and creates a fresh directory without private Git history or unrelated research; it never publishes anything.
