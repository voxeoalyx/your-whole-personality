# Sites migration verification

October 28, 2026. The local migration described below was subsequently deployed **owner-private** after separate authorization. See [hosted verification](HOSTED_VERIFICATION.md) for release identity, the native-Request compatibility repair, API checks and deferred browser checks. No public-repository or license change occurred. Local-only findings below are historical evidence.

## Implementation

The supported application lives in `sites/`, based on the installed official Sites Vinext starter. `.openai/hosting.json` declares `d1: "DB"` and no R2 binding. The Sites Vite integration and connector-context wrapper are retained. Source has no project ID until registration is authorized. `dist/server` and `dist/client` are generated locally; no Python, research archive, `.env`, keys or development database is packaged as a public asset.

The HTTP contract and original frontend are preserved, including recorded play, the NVIDIA investigator, Act III/IV influence findings, self-report opt-in, research JSON and share exports. Typed validation now supports a `pending` checkpoint, handled by the frontend. It still performs the original singleton and alternate-panel tests; unsupported signals are not silently substituted.

Python's threading and process memory are replaced by D1-backed JSON checkpoints and atomic SQL leases/counters. Each poll awaits at most one provider operation, saves state, and returns. It can continue from another isolate without a live Python process or a long detached background promise. Queries chosen by the investigator are saved as pending actions and executed on a later poll. A 30-second lease prevents competing round writers; two global operation leases bound provider work. Stale lease owners cannot overwrite newer results. Answer retries remain idempotent.

## Scoring and behavioral parity

- Original `game.py`, `signals.py`, `scoring.py`, `investigator.py` and `static/logic.js` remained byte-for-byte unchanged during migration. They remain the Python/reference implementation and frontend oracle.
- The JavaScript strict scorer was compared with Python over **all nine archived profiles plus 100 generated tied, missing, flat and reversed-panel cases**. Scores agree within 1e-12 numerical tolerance, with matching winner, completeness, domain, half-panel and row-order results. The strict thresholds remain `value > .10`, more than twice the runner-up, and the same winner on both halves.
- Checkpointed game construction for all nine profiles reproduces original full/removal panels and Python strict scores after serializing/reloading state at every step. Typed labels and signal-family parameters are preserved.
- The existing `logic.js` file is copied unchanged to the Site. Predictability, unfamiliar denominators, player-facing influence categories, changed-recommendation examples and share-card qualifications retain their original implementation.
- Model instructions and structured-action schema were transferred from the existing Python source. The five-question, ten-call, three-discovery and three-step bounds remain; evidence-backed candidate/hypothesis validation, explicit-like query composition and fixed/closing-only fallback distinctions are tested.

This establishes implementation parity for the tested evidence, not model determinism, recommendation superiority, identity measurement or partnership outcomes.

## Local automated verification

- 64 original Python application/security/HTTP tests passed.
- 57 existing JavaScript tests passed.
- 21 new Sites tests passed, including real SQLite migration SQL, cross-instance budgets, leases, stale-owner rejection, separate session caps, expiry/cleanup, malformed/foreign-origin requests, secret/reasoning exclusions, redirect rejection, complete API fixture rounds and scoring parity.
- All 24 archived research tests passed; all 2,265 archived file hashes verified.
- Production build and TypeScript check passed. Wrangler generated runtime binding types from the built configuration.
- The locked dependency audit reports **zero vulnerabilities** as checked October 28. The supplied starter initially had advisories; affected direct/transitive packages were patched, and unused starter UI dependencies/components were removed. Overrides narrowly patch `fflate` and the migration tool's `esbuild`; schema generation still succeeds. No forced downgrade was used.

The framework emits non-fatal source-map/dynamic-import and future config-loader notices. These do not prevent the build or current type check; they are not evidence that hosted execution has been tested.

## Built-Worker browser verification

The production artifact ran on `http://127.0.0.1:8787/` through the local workerd/D1 emulator and the JavaScript-only launcher, using the existing keys through server process environment. A live Running hobby lookup also passed both singleton validation domains through the pending-validation flow and was added with its explicit hobby-audience label.

No service keys were written into source, client assets or local credential files. Exact-key scanning of all built files found no credential matches; direct `.env` and server-module HTTP requests returned 404. The root response retained no-store, CSP, no-referrer and nosniff headers.

A live Overthinker round completed with scripted feedback: Moon rejected; Children of Men unfamiliar; Gattaca, Primer and Ex Machina confirmed. Five accepted NVIDIA prediction decisions referenced prior answers; there were six model calls, ten logical Qloo requests and no prediction-stage fallback. The final prose call used the existing closing-only fallback and the normal result/card visibly said **FIXED CLOSING**. This was not a fallback-free model benchmark. It produced **3/4 familiar confirmed, one unfamiliar, five shown (75%)**.

Act III/IV retained Blue Bottle Coffee as the movie leader and Severance as the game/average leader, without manufacturing strict dominance. Removing Severance showed Lost in Translation #11→#1 and Moon #1→#7, with Control #1→#19 in games. The original session JSON parsed correctly, with five predictions, correct denominator and closing-fallback metadata, and no optional identity field. The PNG preview rendered at 1080×1350. At requested 390px and 320px widths the document measured 375px and 305px after scrollbars, with no horizontal overflow. These are desktop browser viewport checks, not physical-device certification or proof of native downloads.

A recorded Comfort Zone round completed all six questions and reached the final share card, preserving example-profile labeling and shared-influence qualifications. Three yes/three unfamiliar produced 3/3 familiar confirmed. A recorded round also remained retrievable after stopping and restarting the actual built Worker against the same local D1 storage. The final artifact served static modules with no-store and nosniff headers. The browser error/warning log was empty when checked. Tests are scripted QA, not participant taste or engagement measurements.

## Runtime-specific corrections and operational differences

Workers rejects Fetch's `redirect: "error"` mode before sending a request. Both provider adapters now use `manual` and reject non-success responses, including redirects, without forwarding keys. This was discovered in emulator testing and covered by regression tests. [Cloudflare Request documentation](https://developers.cloudflare.com/workers/runtime-apis/request/).

The initial checkpoint implementation exposed a full fixed shortlist just before investigator initialization. The API now keeps that preparation state private until the investigator exists, so the first live screen correctly has five agent-selected questions. A fixture assertion prevents this regression.

NVIDIA transport timeout is 15 seconds instead of the reference's 30, fitting within the browser's existing 20-second request deadline; Qloo remains 15 seconds. Timeout/failure results are explicitly labeled. Provider budgets are shared D1 daily ceilings by UTC date (default 180 Qloo, 150 NVIDIA), not Python process-lifetime limits. Restarting an isolate cannot reset them. Visitor/request budgets and pending work are also shared. Unknown visitor metadata falls into a restrictive shared bucket; verify actual Sites edge metadata before public use.

Temporary game state expires 30 minutes after creation, including working rounds, and becomes inaccessible immediately at expiry. Provider caches and search/validation records expire after two hours; expired records are physically deleted by subsequent API cleanup. D1 storage survives process restarts; platform backup/log retention is separate. No optional identity answer or research JSON is sent to the backend. The Site-specific privacy text describes these changes.

## Remaining hosted checks

A live Sites deployment is still required to confirm platform forwarding/origin behavior, anonymous access, binding provisioning, hosted D1 migrations, production secret injection, actual runtime/quotas, CSP/embedding, cache behavior, real mobile downloads/clipboard and hosting backup/log retention. The local source/build is not a public URL. Provider public-use/data rights, repository publication/license and hackathon submission remain separate decisions. Do not infer authorization or readiness for those steps from this local migration.

See `sites/README.md` for reproducible local setup and commands. Only the D1 local emulator was migrated; no remote schema or resource was changed.
