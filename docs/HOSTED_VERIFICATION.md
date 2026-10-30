# Private Sites deployment verification

October 30 release pass: the complete source/license preparation and hosted browser checks are recorded in [release verification](RELEASE_VERIFICATION.md). This includes the NVIDIA availability diagnosis, validated Lightning replacement, actual clipboard/consent checks and the remaining native-download limitation. Earlier entries below are dated historical evidence.

October 29 allowance update: owner-private version 6 is deployed from source `1aa16651b560931b508de2609e87a3d5d5665625`, saved version `appgprj_6ae282792070819194927c121754dcbf~appgver_08220865ab288191955238acd514a53f`, deployment `appgdep_6ae3db5eed788191af88bccbe65741c9`, runtime revision 2. The original October 28 verification below remains a dated record.

- Hosted and default Qloo budget: **500 calls per UTC date**. NVIDIA configuration was preserved. Provider counters were not reset; caching, minute/cost limits, two-operation leases and recorded behavior are unchanged.
- New live rounds: **10 per visitor per UTC date**, atomically enforced in D1. Existing answers, sensitivity work/polls and recorded rounds do not consume this allowance. Trusted Sites identity is preferred for daily salted visitor hashes, with the existing native-edge fallback for anonymous visitors. Salts now expire at UTC midnight, aligning visitor identity and daily admission windows. No raw identity/address is stored.
- **24 Sites tests**, TypeScript and production build passed. A complete live fixture continued through five answers and sensitivity after exhausting new-round admission; concurrency and separate visitor/day boundaries were also tested.
- Hosted configuration and recorded round creation/retrieval passed using private service access, with zero provider calls. The ten-round boundary was covered against real SQLite migrations; no ten unused live jobs were created in production merely to exhaust a counter.
- Unshill received the separately authorized 500/day budget and ten new reports/day as well. Both Sites retain owner-only access and unchanged GitHub visibility. These settings do not grant provider entitlements; public access and the existing release gates below still need separate resolution.

October 28, 2026. **READY for owner-only evaluation. Public submission remains NOT READY.** No public access, GitHub visibility change, license change or Devpost submission was performed. Owner-browser checks were deferred at the user's request after ChatGPT sign-in required a password.

## Release identity

| Item | Verified value |
| --- | --- |
| Private URL | https://your-whole-personality.a-lyx.chatgpt.site |
| Site | `appgprj_6ae282792070819194927c121754dcbf` |
| Final source commit | `b1d0828ec87c253d9b2aa49da8222acc82082bb7` |
| Saved version | `appgprj_6ae282792070819194927c121754dcbf~appgver_684a85e60c048191bb7ef91acfd2d1ed` |
| Deployment | `appgdep_6ae284d845bc8191aabec398b2b6ec52` — succeeded |
| Runtime environment revision | 1; six server settings stored as secrets |
| Audience | Custom policy containing only the owner; zero editors, groups or external visitors |
| Original GitHub repository | `voxeoalyx/your-whole-personality` — **PRIVATE**, confirmed with GitHub CLI |

The supported Sites source is a separate Git checkout at `sites/`, synchronized through the official Sites source helper. The parent GitHub checkout's existing uncommitted work was not committed or pushed by this deployment. Do not accidentally add the nested checkout as a GitHub submodule; synchronize future source changes deliberately.

## VERIFIED

| Check/component | Evidence | Result |
| --- | --- | --- |
| Private access | Policy rechecked after final deployment. Anonymous browser showed “Log in to access”; unauthenticated HTTP page/API/assets were denied (401/403). | PASS. Service checks used the supported private header only for this Site. |
| Database | Native overview returned `DB` and tables `records`, `leases`, `counters`. | PASS. Sites applied the generated migration. |
| Secrets/configuration | Hosted `/api/config` returned 200 with live/investigator presence flags. Keys were absent. Actual Qloo/NVIDIA calls succeeded. | PASS. Six runtime settings are server secrets. |
| Typed search/validation | Running returned its exact hobby-audience URN, then `pending`, then `valid: true` after both domain checks. | PASS. No silent substitution. |
| Full live API round | Radiohead / Blue Bottle Coffee / Severance; five answers, all removals and two 20-item panels completed. Five accepted NVIDIA prediction actions, six model calls, ten logical game Qloo requests, zero optional discovery queries. | PASS with closing-only fallback below. |
| Recorded API | Comfort Zone creation returned 202 and retrieval returned six predictions with `source: recorded`. | PASS. Browser-local answer/result interaction was not retested in the hosted browser. |
| Answer integrity | Repeated first answer returned `duplicate: true`; invalid sequence returned 400. | PASS. Five distinct answers remained. |
| Concurrent reads/durability | Two simultaneous final GETs returned identical state. Full live and recorded states survived an actual private redeployment; live JSON matched exactly. | PASS. Physical cross-isolate routing was not proven. |
| Provider accounting | After redeployment D1 retained 13 Qloo and six NVIDIA calls: game plus search/validation. | PASS. Daily ceilings are 180 Qloo / 150 NVIDIA, not deliberately exhausted. |
| Rate limiting | Controlled concurrent burst of 32 invalid recorded starts produced 28 validation errors and four 429s; earlier requests used the other allowance. 429 included `Retry-After: 60`. | PASS. No upstream calls; not a load benchmark. |
| Validation/origins | Malformed JSON, 8,193-byte body, short/long searches, unknown/unverified interests and bad recorded IDs returned 400. Foreign Origin/cross-site metadata returned 403. Missing round returned 404. | PASS. Missing-round check is not timed expiry evidence. |
| Source/research isolation | `.env` and server module paths returned 404; `/api/research` returned 404. Exact configured-key checks covered all fetched responses and 233 tracked-source/built files with zero matches. | PASS. No automatic research upload was introduced. |
| Headers/assets | Document/API: no-store, restrictive CSP, nosniff, no-referrer. Root JS/CSS assets returned 200 with correct MIME types. | PASS with static-header difference below. |
| Automated verification | Build, TypeScript and all **22 Sites tests** passed, including strict scoring parity over nine archived profiles plus 100 generated cases. Dependency audit: zero reported vulnerabilities. | PASS. Prior migration also passed 64 Python, 57 frontend and 24 research tests; unchanged suites were not rerun this turn. |
| Scoring | `sites/public/logic.js` remains byte-identical to `static/logic.js`; strict parity tests passed again. | PASS. No thresholds, affinities, denominators or outcome rules changed. |

### Actual game and agent attribution

Scripted QA answers were Moon **no**, Children of Men **unfamiliar**, Gattaca **yes**, Primer **no**, Ex Machina **yes**: **2/4 familiar confirmed, one unfamiliar, five shown (50%)**. These are test answers, not participant research or the owner's preferences.

All five accepted prediction actions came from `nvidia/nemotron-3.5-super-vl-120b-a12b`; later receipts contained earlier feedback. Accepted model calls took 1.636–3.082 seconds, excluding Qloo/polling/answers. Maximum observed game poll was 4.020 seconds, below the browser's 20-second request deadline; this is not an end-to-end benchmark.

The final prose call used **closing fallback**: `closing_fallback: true`, `fallback_reason: null`. Earlier AI decisions remain valid. The delivered frontend contains its existing FIXED CLOSING labeling; hosted visual rendering was not checked after sign-in was deferred. This was not a fallback-free agent run and did not demonstrate optional query tools or superiority over an LLM-only recommender.

Strict dominance remained null. Applying the existing player-facing result function to the hosted response correctly produced **DIFFERENT CATEGORY LEADERS**: Blue Bottle Coffee for movies; Severance for games/largest average, qualified with “No clear overall dominance.” Removing Radiohead moved Children of Men #2→#16; removing Severance moved Lost in Translation #11→#1 and Control #1→#19. These are fixed-panel ranking changes, not shares of personality or causal identity attachment.

## Hosted issues found and repaired

**High, resolved — `sites/worker/index.ts`, `lib/api.mjs`:** initial hosted API requests returned 400 during quota initialization. Production exception evidence located `Reflect.get` in Vinext's request proxy calling the native `Request.cf` getter with an incompatible receiver. D1 schema and salt insertion had succeeded. APIs now retain the native Worker Request within the existing connector context, preserving trusted edge metadata. Infrastructure quota failures return 503 instead of blaming input. A new test checks native metadata, separate hashed visitor budgets and absence of raw addresses in stored counters. The hosted round then succeeded. [Cloudflare receiver-error documentation](https://developers.cloudflare.com/workers/observability/errors/#illegal-invocation-errors).

**Medium, disclosure corrected — `sites/assets/index.html`, `public/app.js`:** hosting logs contain request URLs, connection metadata and headers. Search terms in URLs can therefore appear in logs. The notice now says this and distinguishes private ChatGPT sign-in from a game account database. The game does not persist the supplied account details in its round records. Hosting retention remains unknown; application TTLs do not govern those logs/backups.

## IMPORTANT / UNKNOWN before public release

| Finding/component | Evidence and severity | Smallest next step |
| --- | --- | --- |
| Owner-browser workflow | **Medium / UNKNOWN.** Account selection initially errored, then requested a password. User chose API-only completion. The final return to the retained browser successfully rendered the live landing page; no game was started there. | Complete the full hosted live/recorded UI, Act III/IV, privacy consent, images, dialogs and recovery checks. Access controls need not change. |
| Exports, mobile, accessibility, embed | **Medium / UNKNOWN.** Hosted PNG/JSON downloads, clipboard, viewport/keyboard/VoiceOver and physical-device sharing were not completed. Local migration checks remain the available evidence. `frame-ancestors 'none'` remains. | Test the authenticated hosted browser and intended embed surface; change CSP only for a supported, demonstrated need. |
| Static response headers | **Low.** Sites serves JS/CSS with `public, max-age=0, must-revalidate`; authored `_headers` did not give those responses document/API no-store/nosniff headers. MIME types and private gating were correct; static assets contain no credentials/session data. | Confirm supported Sites asset-header controls before claiming uniform header behavior. Preserve document/API protections. |
| Expiry/outages/capacity | **Medium / partly UNKNOWN.** Real SQL fixtures cover expiry, leases, caps, malformed provider responses, timeouts, budgets and fallback. Hosted checks did not wait 30 minutes or deliberately break/exhaust providers. | Bounded staging failure/expiry checks; avoid spending real quotas just to demonstrate a stop. |
| Hosting retention | **Medium / UNKNOWN.** Logging is confirmed; retention, backup deletion and operator access were not established by tools. | Obtain applicable Sites retention information and align release disclosure. |
| Public submission | **BLOCKER for submission, intentionally unchanged.** Site/GitHub remain private; license, provider public-use rights and public judge access remain unresolved in the original audit. | Resolve separately with owner before public launch; do not change visibility automatically. |

Final deployment returned success. A bounded recent Worker error-log query after repair returned no error events; indexing can lag, so successful HTTP checks are the direct functionality evidence. Only predefined public interests/scripted answers were used. No keys or service credentials were written into source, reports or test artifacts.
