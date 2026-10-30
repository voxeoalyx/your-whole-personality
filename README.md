# Your Whole Personality

The application now has an owner-private [ChatGPT Sites deployment](https://your-whole-personality.a-lyx.chatgpt.site), using the [Vinext/Workers/D1 runtime](sites/README.md) in `sites/`. See [release verification](docs/RELEASE_VERIFICATION.md) for source preparation, hosted browser/consent/export checks and remaining limitations. The Python setup below remains the reference implementation and scoring oracle. No public deployment has been performed; GitHub remains private.

**You contain multitudes. The algorithm disagrees.**

A playable four-act taste test with a persistent Taste Investigator. The supported hosted runtime is Vinext/Cloudflare Workers with D1, serving the existing HTML/CSS/JavaScript game. Live investigation uses Qloo and NVIDIA; recorded rounds need neither API. A buildless Python standard-library server is retained as the reference implementation.

## Run the supported Sites runtime

Tested with Node 24, npm and Python 3.10+. Python is needed only for reference/parity tests, not the deployed Worker. From a fresh clone:

```sh
git clone https://github.com/voxeoalyx/your-whole-personality.git
cd your-whole-personality
python3 -m venv .venv
cp .env.example .env
chmod 600 .env
# Edit .env locally with authorized Qloo and NVIDIA keys, or omit them for recorded play.
cd sites
npm ci
npm run build
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0000_sudden_sheva_callister.sql
npm start -- --port 8787
```

Open **http://127.0.0.1:8787/**. Apply the migration only once per new local database. See [Sites setup](sites/README.md) for development, tests and hosted binding/secrets configuration. Secrets stay server-side; no account is needed for local recorded play. The private hosted preview uses ChatGPT sign-in.

## Run the Python reference

Python 3.10+ and a browser are sufficient; there are no pip or npm dependencies. Git is needed to clone, and Node 18+ is needed only for JavaScript tests. See [MAC_SETUP.md](MAC_SETUP.md) for exact fresh-Mac commands and authentication.

```sh
git clone https://github.com/voxeoalyx/your-whole-personality.git
cd your-whole-personality
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
chmod 600 .env
# Edit .env locally with your own Qloo and NVIDIA credentials.
python server.py
```

Open **http://127.0.0.1:8765**. Keep the terminal running; Ctrl+C stops the server. On subsequent starts, `sh start.sh` uses this checkout's virtual environment when present. On Windows, run `py -3 -m venv .venv`, copy `.env.example` to `.env`, edit it locally, then run `.\start.ps1`. Neither launcher depends on a bundled laptop runtime. Use `python server.py --port 8766` if the port is occupied.

The default binds to loopback and rejects other hosts/origins. Nothing has been publicly deployed. An explicit external bind and HTTPS origin are available behind a reverse proxy; see [deployment instructions](docs/DEPLOYMENT.md).

Live play reads `QLOO_API_KEY` from this checkout's `.env` or the process environment; process values take precedence. No sibling folder is required. The default host is `https://hackathon.api.qloo.com`. Add `NVIDIA_API_KEY` for the investigator; no OpenAI key is needed. Each line must be `NAME=value`, without quotes around the entire assignment. Keys never enter client responses, HTML or JavaScript. All actual env files are ignored by Git; `.env.example` contains blank credential fields.

The release default model is `nvidia/nemotron-3.5-lightning-30b-a3b`. `QLOO_CALL_LIMIT=180` and `NVIDIA_CALL_LIMIT=150` bound new upstream requests per process; restarting resets these development budgets. Availability and limits depend on provider/account access. A missing, timed-out or rejected model request switches to a labeled fixed-Qloo fallback, with no paid-provider fallback.

**No keys or unreliable internet?** Choose "Play a recorded round." Three installed example profiles contain actual Qloo responses collected on October 8, 2026. They need neither API nor local credentials and remain labeled on every act/export. Remote artwork may fail offline; text remains playable. They are example profiles, not predictions about your own picks.

Enable the optional local secret-check hook with `git config core.hooksPath .githooks`. Run `python tools/audit_repository.py --history` before pushing. Read [SECURITY_AUDIT.md](SECURITY_AUDIT.md) for scope and limitations.

## What works

1. Choose three to five interests. Search across named entities, cultural tags and explicit hobby audiences. Types and descriptions distinguish a book/movie from a category or a group: Yoga music is separate from the Yoga hobby audience. Search results are validated before selection. Unsupported or uninformative records are refused without substitution, including the Dune book and the tested Pilates/weightlifting place tags.
2. Answer up to five live investigator predictions with “Nailed it,” “Absolutely not” or “Haven't tried it.” NVIDIA selects structured actions and Qloo-backed candidates using prior answers. It can query another held-out category, incorporate explicitly liked predictions into a new query, inspect influence, or end early with a supported reason. Live answers are final because subsequent decisions depend on them; start a new round to change the path. Recorded rounds retain the original six guesses and previous-answer control.
3. Inspect leave-one-out ranking changes. Act III distinguishes strict dominance, the largest measured influence without dominance, shared/category-specific influence, and insufficient evidence. “Try without” names titles entering/leaving the top three and their before/after ranks, with both lists available to inspect. No additional API call is needed. “Make a swap” starts a fresh round; reactions are not carried between profiles.
4. Reveal a deterministic, evidence-grounded verdict. Predictability and ranking influence stay separate. Act IV, copied text and the PNG carry the same named Act III influences and qualifications. Preview/export a 1080px-wide PNG (normally 1350px tall; long receipts grow to preserve names and evidence limits), copy the verdict or explicitly download your session as JSON. There is no pretend public share link.

The model chooses actions and short observations; code validates every action and computes all metrics and verdict categories. Guesses must be unseen, scored entities returned by Qloo. The joke targets algorithmic overconfidence. “Inspect the investigator” opens public decision summaries and evidence receipts; it does not expose private model reasoning. See [INVESTIGATOR_RESULTS.md](INVESTIGATOR_RESULTS.md) for the architecture, controlled results, limitations and human evaluation protocol.

## Integration and scoring

The focused activity extension is documented in [ACTIVITY_SIGNALS.md](ACTIVITY_SIGNALS.md), with exact IDs, live measurements, failures and reproducible probes. Running, Yoga and Architecture audiences work; Architecture books and Yoga music work as distinct tag interests. Pilates itself did not yield useful scored variation. Fitness/Health & Fitness are broader content preferences that must be chosen explicitly.

`qloo_client.py` supports `GET /search`, `/v2/tags`, `/v2/audiences` and `/v2/insights`. `signals.py` routes typed selections to `signal.interests.entities`, `signal.interests.tags` or `signal.demographics.audiences`; it never puts an audience UUID into the entity signal. Hobby audiences are the only audience class offered. Insights retains `bias.trends=off`, `feature.explainability=true`, and fixed `filter.results.entities` panels. Redirects are refused so credentials cannot be forwarded. Tag/audience coverage requires nonflat scores in two output domains; tied top results get a separate fixed-panel check. Every round rechecks its actual output domains and every response checks ignored-input warnings across all three signal families. HTTP 200 plus entity-driven scores does not prove that an added tag works.

`game.py` chooses two output categories absent from the inputs. It discovers up to 20 candidates per category, then scores the same panel for the full profile and each removal. For three inputs, this is typically **10 upstream requests**: two discovery requests, two full-panel checks, six removals. Five inputs require 14, plus any uncached search or validation calls. Guesses become playable while ablations finish. Requests are serialized upstream, bounded by 15-second timeouts and a default 180-call process budget; no automatic retries. Equivalent requests share an in-memory cache for up to two hours. Starting another round with the same interests usually reuses those responses.

`scoring.py` uses mean ranks for ties. Per-domain distance is `(1 − Spearman rho) / 2`; the displayed influence uses the mean across **both** complete, nonflat domains. A winner must exceed 0.10, exceed twice the next-largest value, and remain the winner on both disjoint halves of the panels. If any necessary comparison is missing or flat, there is no supported winner. The halves check candidate sensitivity, not statistical significance.

Act III's descriptive reveal is separate from that strict metric and the Act IV verdict scoring. Its named influences also appear in Act IV and every share format, with category labels and qualifications rather than a generic non-winner message. The original result, domain values and halves remain in “Inspect the investigator,” including recorded rounds. Missing comparisons are scoped, never zero-filled; tied recommendation ranks are displayed as ranges. See [ACT_III_FINDINGS.md](ACT_III_FINDINGS.md) for the investigation and nine-profile before/after distribution. Reproduce it offline with `node tools/analyze_influence.mjs`.

These panels are selected from the full profile's results, so they are outcome-selected and may affect sensitivity. They are not the exact panels used in Experiment 3, and its numerical effects are not hardcoded into the game. The prototype generalizes the research calculation to other output domains; it does not claim that movie/game results independently validate the original brand/TV findings. Native affinity values are never treated as probabilities or shares of human personality.

Mixed profiles keep the same removal formula and thresholds. Each ablation removes one selected record from its own signal family; empty families are omitted, other signals and candidate panels remain fixed. Tags also hold out their documented parent entity categories. Audience removal measures the effect of cohort context at Qloo's default weights, not the importance of a personal favorite. The game explains this and keeps typed labels in sensitivity results. Search now uses up to three calls, and each context signal normally adds two cached coverage probes; a tied probe can add a reference-panel discovery and rescore per domain. All requests share the existing call budget.

Predictability is `confirmed / (confirmed + rejected)`. Unfamiliar guesses are excluded. With fewer than three familiar guesses, the verdict says insufficient evidence even if the raw displayed fraction is high. Otherwise a supported ranking winner can trigger the hijack verdict; without one, ≥75% confirmation gives the legible verdict, ≤25% gives statistical inconvenience, and the middle gives multitudes. The two measurements are never averaged into a personality score.

Official references: [Qloo Search](https://raw.githubusercontent.com/qloo/docs-public/main/reference/get-search.md), [Insights reference](https://raw.githubusercontent.com/qloo/docs-public/main/reference/insights-api-deep-dive.md). Prior research is archived in `research/civilizr-research/whole-personality/`; see [research/ARCHIVE.md](research/ARCHIVE.md) for provenance and offline reproduction.

## Privacy and data

Live search and selected interests go to Qloo. Live selections, candidate evidence, explicit reactions and concise hypothesis state go to NVIDIA for inference. Explicitly liked predictions may be added to later Qloo queries; rejected and unfamiliar predictions are never sent as positive signals. In the Sites runtime, live reactions are POSTed to the server and saved in temporary D1 round state. Rounds expire 30 minutes after creation, including working rounds; caches/search records expire after two hours. Expired rows are inaccessible and are physically removed by the next API cleanup. The Python reference instead uses process memory and an in-flight expiry exception. Reloading the tab abandons its UI but does not instantly erase the server job. Provider retention is governed by those services, not the local expiry. Recorded-round reactions stay in the tab. The game has no analytics, account database or localStorage. Private Sites access uses platform authentication/cookies and supplies basic account details, which the game does not store in round records. Hosting logs include request URLs, headers and connection metadata: search text in URLs may appear in those logs. Hosting backup/log retention and provider retention are separate from app expiry and remain unverified.

The optional session JSON contains typed selections, exact signal parameters, shown predictions/reactions, separate metrics, source/timestamp and the investigator trace including Qloo request receipts. It excludes credentials and private reasoning. It is written only when the player chooses to download it. No consented research dataset is silently accumulated. Development probes use predefined public example interests and scripted responses, never real-player reactions.

## Tests and verification

```sh
python -m unittest discover -s tests -v
node --test tests/*.test.js
```

The Python reference requires no third-party Python packages. The hosted runtime uses the locked npm dependencies in `sites/`; Node is required for its build and tests. Python tests cover the original scoring and typed signals plus bounded actions, feedback isolation, duplicate submissions, discovery failures, schema validation, transport failures, fallback and credential exclusion. JavaScript tests cover unfamiliarity, sample sizes, Act IV verdict branches, recorded-mode share labeling, all Act III outcomes, partial evidence and tied-rank recommendation changes. Fixture-model tests verify plumbing; only separately labeled live NVIDIA runs provide evidence about model behavior.

Run the controlled comparison without spending Qloo requests:

```sh
python compare_investigators.py --live-model --modes A B C --scenarios positive negative unfamiliar contradiction --forced-prefix 2
```

This uses the same saved, real Qloo candidate pool for all modes. A sees titles/types without scores or rank order; B is fixed Qloo; C sees scored Qloo evidence. A's candidate pool is still Qloo-derived, so this is not a fully independent no-Qloo baseline. Scripted reactions test control flow, not recommendation relevance. The command saves raw traces in ignored `test-results/`. Omit `--forced-prefix 2` for unconstrained full rounds; use `--modes B` without `--live-model` for an offline baseline.

See `VERIFICATION.md` for browser checks and their limits. Live collection of three fixture combinations used 30 calls. A separate live UI round also completed. The archived recordings can be regenerated intentionally with `python record_demos.py --live`, but existing recordings are reused; do not remove them merely to repeat testing. Original response bytes and hashes are versioned in `research/prototype/verification/`. New probe outputs remain in ignored `.cache/` and `test-results/` until deliberately reviewed for archiving.

## Known limits

- Local prototype, not production hosting. Process budget and in-memory limits are not multi-user abuse protection. Two active rounds are allowed; backing out stops the UI but an already-started round may finish its bounded requests.
- Search coverage is not Insights support. Categories can produce incomplete or uninformative panels. Book support is especially unproven here; nothing is silently replaced. The two available held-out categories depend on the mix; large requests can be slow on weak internet.
- No scientific claim about identity, human preferences, campaign results or model calibration. Five judgments are a tiny sample. All three recorded starter profiles currently have no robust single winner; the game does not manufacture one for a better reveal. The positive winner branch is covered by controlled scoring/verdict tests.
- Model-selected panels and top-three summaries can amplify changes. The ranking thresholds are inherited screening rules, not validated psychometrics. No historical stability or independent user-validation claim is made.
- Image URLs are supplied by Qloo and may fail or change. PNGs use type and color instead of remote artwork, avoiding tainted canvases and dependence on those assets.
- Browser clipboard/download restrictions vary. The in-app browser used for testing required selectable text and PNG preview fallbacks. Automatic file delivery and native sharing on Safari/iOS/Android remain unverified. There are no public result URLs.
- No real participant engagement study has been run. The 2–4-minute target, humor, voluntary sharing and advantage over a simpler taste quiz remain hypotheses.

## Before public hackathon submission

The supported Sites backend now runs on Vinext/Workers/D1; the root Python backend remains the reference implementation. Hosting in ChatGPT does not remove the NVIDIA requirement. Private deployment does not satisfy public demo/source requirements or establish provider public-use rights. The Python proxy instructions below apply only to the reference server.

For a small Python-capable HTTPS host, keep the app's `static/` and `data/demos.json` with the Python files, set both keys using the host's secret manager, and run behind its reverse proxy:

```sh
python server.py --host 0.0.0.0 --port 8765 --public-origin https://your-actual-host.example
```

Replace the example with the exact real origin. The proxy must preserve that Host header, terminate HTTPS, limit body size/timeouts and apply request/concurrency quotas; expose only the proxy publicly. The built-in stdlib HTTP server and in-memory budgets are suitable for a bounded prototype, not production hardening. Restarts lose sessions/cache. No accounts or paid infrastructure were added. A free NVIDIA development endpoint is not a promise of unrestricted public-production capacity.

Confirm the applicable Qloo agreement permits public use, output display/caching and the intended distribution; the existing research did not establish these rights. Review image usage and attribution requirements. Then host behind a production server with HTTPS, server-managed secrets, origin policy, per-user/global quotas, rate limiting, bounded concurrency and clear privacy disclosure. Recheck the actual hackathon's current rules. Complete mobile browser, accessibility and failure-path testing, and obtain feedback from actual players. Do not expose this development server directly.

The three highest-impact next improvements are: (1) observe real players completing and voluntarily sharing a round; (2) improve entity coverage and test influence stability on independent candidate panels; (3) ship a rights-cleared HTTPS version with robust mobile sharing and API-budget controls. Public share links, if later justified, should be opt-in and store only the card content the player approves.

## Optional Identity Reality Check

After Act IV, optionally choose one or several original typed interests, none, decline, or a short unsupported interest. The reveal compares Qloo model sensitivity with self-reported attachment; identity transfer remains untested. Original verdicts, the investigator and scoring are unchanged, including “THE ALGORITHM HAS SEEN YOUR TYPE BEFORE.”

Identity answers stay in tab memory and are never sent to Qloo/NVIDIA or the server. A separate unchecked permission includes them in copied text and PNG. Another unchecked consent enables a validated research JSON preview/download; nothing is uploaded. No storage service is required. Delete downloaded copies locally; separately shared files require a recipient's retention/deletion agreement. The original session JSON excludes these optional identity answers. See [research/privacy protocol](docs/IDENTITY_RESEARCH.md), [schema](docs/research-record.schema.json), [commercial pilot and opportunity assessment](docs/COMMERCIAL_VALIDATION.md), and [verification](docs/IDENTITY_VERIFICATION.md).

### Release audit fixes (October 28, 2026)

Local request/visitor quotas now renew, with bounded worker admission, separate recorded/live capacity and retained hard provider call ceilings. See [deployment limits](docs/DEPLOYMENT.md) for exact limits and proxy/multiple-instance restrictions. Final-model failure is labeled as fixed closing copy on the result, copied verdict, PNG and research metadata while preserving earlier AI decisions. Default model configuration matches the verified Nemotron 3.5 endpoint. Privacy text covers search-as-you-type, temporary abuse counters, in-flight retention exceptions and provider policies. Browser requests are bounded and failed polling/answers can retry the same round. These fixes do not constitute deployment readiness or provider authorization.

## License and release scope

Original application code and documentation use the [MIT license](LICENSE). See [third-party notices](THIRD_PARTY_NOTICES.md) for retained component licenses and the separate status of Qloo data, remote artwork, archived captures and provider terms. Licensing the application does not relicense third-party data. The hosted preview is intended for hackathon judging; no automatic shutdown or provider migration is configured.
