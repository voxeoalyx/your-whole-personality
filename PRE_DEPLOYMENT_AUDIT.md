# Pre-deployment and hackathon-readiness audit

**October 30 release pass:** see [release verification](docs/RELEASE_VERIFICATION.md) for completed source/license preparation, hosted browser checks and a validated free-model configuration repair. These supersede the earlier pending-browser/license findings; native download delivery and provider/hosting policy confirmations retain the stated limits. Public access and Devpost submission have not been performed.

**Private hosting follow-up (October 28):** subsequently authorized code fixes and runtime migration are now deployed owner-private. Hosted API checks passed after a native-Request compatibility repair. See [hosted verification](docs/HOSTED_VERIFICATION.md) for exact release details, evidence and remaining checks. Owner-browser testing was deferred by the user. GitHub and the Site remain private. The original public-release findings and decision below are historical; public submission remains blocked by the unresolved publication/rights/license and verification items.

**Audited October 28, 2026. Recommendation: NOT READY for public deployment or submission in its current state.** The local game works; publication, hosting, abuse protection, provider permissions, and fallback attribution need specific work. No application code, configuration, repository visibility, or deployment was changed during this audit.

Scope: Your Whole Personality only, targeting the user-confirmed [Qloo Agentic Hackathon](https://qloo.devpost.com/). No requirements from another project/event were applied. Examined the working tree on `codex/initial-transfer`, HEAD `63a274730f485e3c4a4ecd2cb962af86d4ccb349`, including the uncommitted Identity Reality Check changes. The unrelated untracked `unshill/` directory was excluded. This report is the audit's only repository addition.

## Follow-up: authorized code fixes, October 28

The findings below preserve the original audit evidence. A subsequent authorized implementation addressed B2 for the existing **single-process** runtime, B5, I1 and I2, plus the browser timeout/recovery and work-deadline portions of I3. No deployment, repository publication or provider contractual action occurred. Scoring, game construction and influence logic were unchanged byte-for-byte relative to the start of that implementation.

- Added atomic live admission, two reserved background-work slots shared by starts/answers, separate recorded-example capacity, and 429 Retry-After responses. Rejected busy answers consume no feedback. Added per-connection route limits, a renewable conservative visitor cost budget and a global request ceiling. Provider lifetime ceilings remain. Salted address hashes/counters are bounded, expire and are periodically cleaned; untrusted forwarding headers are ignored. Distributed/proxy-aware enforcement remains a deployment requirement.
- Final-call failure or model-call exhaustion now produces explicit closing-only metadata and labels in Act III/IV, the card, copied verdict, PNG and research export. Earlier AI decisions retain attribution. Research v1 accepts its new optional closing flag without rejecting older records.
- Aligned `.env.example` and the server model default with the verified Nemotron 3.5 identifier. Updated setup/deployment notes and privacy disclosure, including search terms, retention exceptions, temporary quota counters and provider-policy links.
- Browser API waits are bounded at 20 seconds. Polling/answer failures offer an idempotent retry. Loading states explain abandonment; background tasks have cooperative 180-second deadlines at provider boundaries. Running requests are not forcibly killed; production request/concurrency limits are still required.

Verification: **64 Python application/security tests and 57 JavaScript tests passed**; all 24 archived research tests passed again. A localhost fixture browser round deliberately failed its final model call: the banner, fixed-closing paragraph, card label, copied verdict and PNG preview displayed the correct provenance, with no console errors. This fixture is not a new live-provider benchmark. The final scan of 28 changed application/release files found no matches. The broader reachable-history guard reported one machine-home-path finding in an unrelated Unshill audit document; it reported no credential-pattern matches. That unrelated history was not modified. Remaining release blockers: B1 (Sites migration/public URL), B3 (publication/license/release), B4 (permissions), and deployment-specific distributed controls/verification. Overall release recommendation remains **NOT READY** pending those items.

## Follow-up: local Sites migration

A subsequent authorized migration now exists under `sites/`, using the supported Vinext/Cloudflare Workers starter and D1 binding. See `docs/SITES_MIGRATION.md` for parity checks, local Worker verification and remaining hosted-only checks. B1's Python-runtime incompatibility has been addressed in source; its public-URL and hosted-validation requirements remain open. This original audit is retained as historical evidence. No Site registration, deployment, public-repository change or license selection has occurred. Public release remains blocked by the outstanding publication/permissions and hosted-verification requirements.

## BLOCKERS — must fix before public deployment

### B1. This repository is not a deployable Sites application

- **Severity:** High — runtime incompatibility; no verified public demo.
- **Affected:** `server.py`, `qloo_client.py`, `model_client.py`, `investigator.py`, `game.py`, `signals.py`, `scoring.py`; absent Sites build/hosting manifest.
- **Evidence:** The app uses Python's `ThreadingHTTPServer`, a thread pool, process-local dictionaries/locks, and filesystem reads. Sites' installed documentation specifies a Cloudflare Workers server runtime, 128 MB per isolate and HTTP external connections. Its default server starter is Vinext; its explicit Worker ESM starter exports `fetch(request, env, ctx)`. No supported upload-and-run path for this Python server was documented. A static upload cannot implement the five existing API routes. The owned-Sites inventory returned no matching Your Whole Personality deployment; repository documentation supplies only localhost and example host URLs.
- **Smallest fix:** Preserve the UI, scoring formulas and API contract, but adapt the backend to the documented Sites runtime, including `/api/config`, `/api/search`, `/api/validate`, `/api/game[/id]` and `/api/answer`. Replace Python background threads and per-process sessions with bounded request/job handling and shared expiring state; preserve idempotent answers. Package only runtime assets, not the research archive or `.env`. Validate locally, then smoke-test an authorized public deployment. This is a required migration, not a file-copy deployment.
- **Alternative if the deadline rules out that migration:** A separately authorized Python-capable host could preserve more code, with a production serving boundary and shared abuse controls. Do not expose the present development server directly: [Python's documentation explicitly cautions against production use of `http.server`](https://docs.python.org/3/library/http.server.html).

### B2. Anonymous users can exhaust service capacity and provider budgets

- **Severity:** High — inexpensive denial of service and API-quota abuse.
- **Affected:** `server.py:119` (`origin_ok`), `server.py:140` search routing, `server.py:161` POST handling and session admission; `qloo_client.py:66`; `model_client.py:25`.
- **Evidence:** Valid Host with no Origin is accepted, as needed by normal clients, so origin checks do not stop bots. Search/validation have no visitor rate limits. Qloo's 180-call and NVIDIA's 150-call defaults are shared process-lifetime caps, not renewable per-user quotas or cross-instance controls. A normal three-interest round uses ten Qloo requests before optional discovery/search. An isolated fixture probe, with upstream calls forbidden, accepted **24 recorded rounds and returned 429 on request 25**. Those records occupy the same table as live rounds for 30 minutes. Session-cap checks and insertion occur in separate lock sections; answer work also bypasses the initial working-round gate. Two worker threads do not bound HTTP threads or the work queue.
- **Smallest fix:** Apply server-side rate limits to every costly route, an atomic shared budget/admission check, bounded queued work, and a deliberate replenishment/expiry policy that keeps judging available. Prevent recorded rounds from consuming the whole live-session allowance. Return useful retry guidance. Origin protection and hard provider spend ceilings should remain. Do not solve this merely by increasing limits.

### B3. Required public source/demo deliverables are missing

- **Severity:** High — submission eligibility.
- **Affected:** GitHub repository settings, root license file, release commit, README/demo URL.
- **Evidence:** Read-only GitHub CLI inspection returned **PRIVATE** and `licenseInfo: null`. No tracked license file was found. Eighteen changed/new release files, including identity functionality/tests/docs, are not in HEAD. No functioning externally published URL was supplied or discovered.
- **Smallest fix:** After rights/security review and separate authorization, choose an appropriate open-source license, commit the reviewed release files explicitly, push, publish the repository, and supply the working hosted URL. Do not accidentally stage `unshill/`. A successful local round is not the required public demo. See the submission checklist below.

### B4. Public-use and redistribution permissions remain unverified

- **Severity:** High — resolve authorization before public service/repository release.
- **Affected:** NVIDIA hosted inference; Qloo outputs in `data/` and `research/`; artwork URLs; license/attribution documentation.
- **Evidence:** No account-specific public-use authorization was established. NVIDIA's published API trial terms restrict unsubscribed access to internal testing/evaluation and exclude production; an existing working/free key does not establish public-demo rights. Confirm whether a hackathon exception or subscription applies. [NVIDIA API Trial Terms, §§1.2–1.4](https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf).
- **Smallest fix:** Confirm the applicable NVIDIA entitlement and Qloo hackathon agreement for public visitors, output display, caching and redistribution of archived responses/artwork. Record required notices and distinguish application-code licensing from third-party data rights. Qloo's public terms defer to applicable negotiated/additional agreements and reserve rights in outputs and marks; they do not establish that this entire research archive can be relicensed. Also resolve the applicable age restrictions before unrestricted play. [Qloo terms, introduction and §§2, 8](https://www.qloo.com/legal/terms).

### B5. Failed final model reasoning is not visibly labeled as fallback

- **Severity:** High — misleading provenance in the core judged experience.
- **Affected:** `investigator.py:284–300`, `static/app.js:19,29,138`, `static/research-schema.js` / research model metadata.
- **Evidence:** Both an isolated failure probe and today's full live round ended with `closing_fallback`, while `fallback_reason` remained null and mode remained `agentic_qloo`. Act IV displayed the canned line “The evidence is in. My confidence has been appropriately reduced.” under the investigator presentation; the card still said `QLOO + NVIDIA · INVESTIGATOR`. The public trace discloses the failure, but the normal player view does not. Prediction-stage fallback is labeled correctly.
- **Smallest fix:** Expose a closing-only fallback status, label the closing sentence as fixed copy, and preserve that distinction in relevant export metadata. Retain credit for earlier real AI decisions. Add a regression for final-call failure; do not mark the entire round fabricated or hide its earlier valid decisions.

## IMPORTANT — should fix before submission

### I1. Setup does not reproduce the currently working model configuration

- **Severity:** Medium — avoidable fresh-clone/deployment failure.
- **Affected:** `.env.example:8`, `model_client.py:9`, `MAC_SETUP.md`, older `INVESTIGATOR_RESULTS.md` model instructions.
- **Evidence:** Defaults name `nvidia/nemotron-3-super-120b-a12b`; the local environment and today's successful prediction calls use `nvidia/nemotron-3.5-super-vl-120b-a12b`. The old default was not live-retested here; its current availability is unknown. Copying the example and filling only keys does not recreate the audited configuration.
- **Smallest fix:** Document/set the verified model identifier consistently, keep it configurable, and smoke-test the exact release environment. Do not promise perpetual free availability.

### I2. Privacy copy needs a few precise corrections and hosting-specific details

- **Severity:** Medium — incomplete disclosure, not evidence of undisclosed research uploads.
- **Affected:** `static/index.html:17`, `static/app.js:45–52`, `qloo_client.py:98–105`, `server.py:209–224`.
- **Evidence:** Typing at least two characters sends the raw search term to Qloo after a 320 ms debounce, before starting a round. In-memory request audit entries retain search parameters, not just hashes. The notice describes interests/reactions but does not clearly explain search-as-you-type. Its 30-minute session statement omits the exemption for working jobs; cache cleanup can wait for the provider lock. There is no immediate server-session deletion endpoint. Provider policies are mentioned without links. Future Sites/proxy logs are not covered by the local no-access-logging implementation.
- **Smallest fix:** Say when search terms leave the browser; describe local retention as scheduled expiry with in-flight exceptions; make clear that reload/clearing identity does not delete a live server round or provider copies. Link the applicable provider policies and disclose actual host logs after deployment. Do not imply that app TTLs govern provider retention. Qloo's public input-signal terms include continuing use rights and no obligation to delete; confirm the applicable agreement. [Qloo terms, §9](https://www.qloo.com/legal/terms).

### I3. Waiting and cancellation are weak under slow or interrupted networks

- **Severity:** Medium — stalled play and wasted quota.
- **Affected:** `static/app.js:30,65–94`; serialized requests in `qloo_client.py:72`; `server.py` worker lifecycle.
- **Evidence:** Provider socket timeouts are bounded (Qloo 15 seconds, NVIDIA 30), but browser fetch/polling has no overall deadline. Loading advertises 15–45 seconds; multiple serialized calls and action-repair attempts can exceed it. The between-answer screen has no recovery control. “Back to my picks” stops client progress but does not cancel server work. A transient polling failure drops the user into the error screen rather than resuming the current round. Successful model decisions in today's trace took 1.886–2.941 seconds each; that excludes rejected calls, failed closing, Qloo latency and user time, and is not an end-to-end performance benchmark.
- **Smallest fix:** Bound browser waits, offer a safe retry of the same job/idempotent answer, and label abandoning a round accurately. Add a total job deadline to release capacity. Verify timeout/recovery on the hosted build without loosening scoring or inventing results.

### I4. Submission claims must match the modest agent evidence

- **Severity:** Medium — judging credibility.
- **Affected:** Submission description, `INVESTIGATOR_RESULTS.md`, demo rehearsal.
- **Evidence:** Real model actions are executed, but today's run selected five movies, used zero discovery queries, needed two rejected-action repairs and used a fixed closing. It does not demonstrate cross-domain exploration or prove that feedback caused a different item than a counterfactual run. Existing paired live recordings show modest changed choices, with acknowledged sampling and baseline limitations.
- **Smallest fix:** Rehearse the exact released model/profile and show its public action receipts. Describe verified adaptive selection and its limits; do not promise every available tool is used every round. No new agent feature is needed for an honest submission.

## POLISH — optional improvements

| Finding | Component/evidence | Severity | Smallest recommended fix |
| --- | --- | --- | --- |
| Hosting-specific error copy | `static/app.js:30` tells a visitor to restart “the local server” after malformed/non-JSON responses. | Low | Use hosted-service recovery language in the public build. |
| Audit accessibility beyond viewport fit | Keyboard handlers, labels, skip link, focus management and reduced-motion CSS exist; no full screen-reader/contrast/touch-target audit was performed. | Low | Run a short keyboard and VoiceOver pass on the hosted release; fix demonstrated failures only. |
| Generated PNG has substantial unused space | Both tested previews rendered at 1080×1350 with all influence qualifications intact. | Low | Leave as-is for deadline; optional spacing adjustment later. |
| Test warnings | Python 3.14 emits positional `re.split` deprecation warnings; a mocked HTTPError emits a resource warning. All tests pass. | Low | Clean these narrowly after release-critical fixes; neither currently blocks play. |

## VERIFIED — actually tested and confirmed

### Automated checks and security boundaries

| Check run on the audited working tree | Result / scope |
| --- | --- |
| `.venv/bin/python -m unittest discover -s tests -v` | **54 passed.** Initial sandbox run could not bind localhost; the authorized loopback rerun passed, including all HTTP tests. |
| `npm test` | **56 passed**, including each influence outcome, Act IV/share qualifications, optional identity and consent/export schema checks. |
| Archived research suites | **24 passed:** 14 root research, 6 Whole Personality metrics, 4 Uncomparable analysis. Offline fixtures, not new participant research. |
| `python tools/audit_repository.py --history` | **0 findings:** 2,315 indexed files; 2,569 index/history objects; 271,214,141 bytes; two configured secrets checked without printing them. |
| Separate changed/untracked release-file scan | **18 files, 0 findings**, using the same patterns and exact configured-secret checks; excluded unrelated `unshill/`. |
| `python tools/verify_archive.py` | **2,265 archived files passed** integrity checks. |
| Isolated session-capacity/expiry probe | 24 demo admissions, then 429; no upstream calls. All ready records were removed after simulated >30-minute expiry. |
| Isolated final-model failure probe | Reproduced B5: `closing_fallback`, null fallback reason, `agentic_qloo`. |

Pattern scans cannot prove absence of every secret. History scope is all reachable **local** refs, not deleted/unreachable objects, remote-only refs, external logs or provider accounts. Git hooks are configured as `.githooks`; no secret was printed or rotated.

The runtime imports Python standard-library modules only. `npm ls --all --json` has no dependency tree; the virtual environment contains only pip. There is no third-party production package set for npm/pip vulnerability auditing, and no CDN JavaScript was found. Tested versions: Python **3.14.8**, Node **24.22.1**. This is an inventory result, not a CVE-free attestation of Python, Node, the OS or a future Sites starter. Audit newly introduced migration dependencies and the actual hosting runtime before release.

Confirmed safeguards: static-file allowlist blocks `.env`/source/traversal requests; `/api/config` contains presence flags rather than keys; exact allowed HTTPS provider destinations and disabled redirects prevent arbitrary API proxying; body-size/interest/type/feedback validation and duplicate-answer handling are tested. Model actions cannot execute arbitrary code, choose arbitrary URLs or invent candidate IDs. HTML output is escaped; private reasoning fields are discarded. Responses use no-store, nosniff and a restrictive CSP. These are useful controls, but do not fix B2.

### Full player workflows

- **Live anonymous round:** Radiohead / Blue Bottle Coffee / Severance; scripted responses: Moon **no**, Primer **unknown**, Children of Men **yes**, Gattaca **no**, Ex Machina **yes**. Both APIs worked with the existing keys. Trace: eight NVIDIA calls, five accepted prediction decisions, two invalid-action repairs, one closing fallback; ten logical Qloo requests, zero optional discovery queries. Correct result: **2/4 familiar confirmed, one unfamiliar, five shown, 50%**. This is test feedback, not the user's preferences or measured recommendation quality.
- **Act III → Act IV:** Blue Bottle Coffee led movie influence; Severance led games and the overall average; no strict dominant winner was manufactured. Removing Severance moved Lost in Translation from #11 to #1 and Moon from #1 to #7 on the fixed movie panel; Control moved #1 to #19 in games. Final card retained names, domain distinctions and non-dominance qualifications.
- **Recorded round:** Completed all six Comfort Zone predictions, exercised a different removal, and reached the final card. Example-profile/source labeling remained visible. Three yes / three unfamiliar produced 3/3 familiar confirmed, with the denominator displayed; no live agent was claimed.
- **Privacy/export UX:** Optional identity selection worked. Identity sharing was unchecked by default; copied text omitted it. Research review was disabled before consent, produced parseable allowlisted JSON after consent, and cleared when consent was revoked. Both live and recorded PNG previews rendered; live image dimensions were 1080×1350. Selectable copy fallback worked. Native clipboard delivery, file downloads and physical-phone sharing are not inferred from preview success.
- **Responsive checks:** Live guessing/results at requested 390px and 320px widths had document widths of 375px and 305px after scrollbars, with no horizontal overflow. Controls remained exposed in the accessibility tree. Browser console error/warning log was empty when checked. This is desktop-browser viewport testing, not physical iOS/Android certification.
- **Search/keyboard:** A live Pilates search displayed the exact-signal limitation and distinguished incidental music/place records instead of silently substituting Fitness. Arrow Down focused a result; Escape dismissed results and returned focus to the search input.

### Data handling actually implemented

| Data | Destination/storage | Consent and deletion behavior |
| --- | --- | --- |
| Search text, selected typed interests, scored candidates | Qloo; bounded server cache/request audit. Selected interests/evidence also enter NVIDIA model context. | Search occurs while typing; see I2. Server cache/audit cleanup targets two hours. Provider retention is separate. |
| Live yes/no/unknown answers and public action trace | Server job/investigator memory; NVIDIA. Up to two explicit yes predictions may become additional Qloo inputs. | No accounts or persistent player database. Idle/completed state expires after 30 minutes from creation; working exception applies. Restart loses state. UUID round token is a bearer capability: anyone possessing it can retrieve/answer that round. |
| Recorded answers and optional identity/free text | Browser module state. No localStorage, sessionStorage, research ingestion endpoint or automatic research upload found. | Reload/new round clears tab state; identity has clear/decline controls. Live server state expires independently. |
| Session JSON, research JSON, copied verdict and PNG | User-initiated local export; downloaded/shared copies persist outside the app. | Separate identity-share opt-in and research-review consent. Research records are pseudonymous, not guaranteed anonymous. Recipient deletion requires a separate agreement, as disclosed. |
| Artwork requests | HTTPS URLs returned by Qloo; browser communicates with image hosts. | No-referrer is set. Image hosts still receive ordinary network request information. The privacy notice mentions external image loading. |

The local HTTP handler suppresses access logs. Normal server operation does not persist raw live responses (`record_dir` is unset). Archived fixtures are deliberately versioned research data; their public distribution is a separate B4 question.

### Agentic behavior and Qloo differentiation

`investigator.py` sends evidence plus accumulated feedback to NVIDIA, validates the returned structured action, and executes its selected candidate/tool. It supports `TEST_PREDICTION`, `INVESTIGATE_CONTRADICTION`, `QUERY_QLOO`, `CHANGE_DOMAIN`, `ANALYZE_INFLUENCE` and `DELIVER_VERDICT`, constrained by five questions, ten model calls, three discovery queries and three model steps per advance. Scoring and final category logic remain deterministic. Therefore the implementation is more than a narration wrapper; availability of actions does not prove that a given model will use them well.

**What a judge can observe:** enter explicit picks, reject a prediction, then open “Inspect the investigator.” The subsequent public receipt contains the prior feedback and the model's accepted action/candidate; the next displayed title is that candidate. Today's order differs from the fixed alternating movie/game sequence. The archived positive/negative pair in `INVESTIGATOR_RESULTS.md` additionally changes later order and one title after common initial questions. Fixture tests prove feedback plumbing; those archived live pairs provide limited behavioral evidence, not robust causal validation. No hidden chain-of-thought is exposed or needed.

**What Qloo supplies:** entity/tag/audience resolution and support checks; cross-category candidate discovery and affinities; fixed-panel full-profile/removal responses used for rank-distance, stability checks and changed-recommendation receipts. Without live Qloo, new personalized profiles, rescoring and evidence-grounded influence comparisons are unavailable. Recorded mode still works because it contains earlier Qloo outputs. Without NVIDIA, fixed-Qloo play remains possible with correct labeling. The optional identity answer is self-report, not a Qloo output.

**Not demonstrated:** superiority to an independent LLM-only recommender, real-person recommendation accuracy, viral sharing, customer retention, willingness to pay, or partnership ROI. The existing names-only comparison still uses a Qloo-selected candidate pool; scripted reactions are not relevance measurements. The brand-partnership premise remains research/prototype work, not a validated commercial recommendation engine. Preserve these distinctions in submission copy.

### Submission checklist for this event

The [current event page](https://qloo.devpost.com/) gives **October 30, 2026, 11:45 pm EDT** as the deadline. It requires a functional externally published demo, public source, open-source license and feature description; **demo videos are explicitly not required**. Its public-demo requirement is stricter than the rules' generic private-login testing wording, so submit an anonymously accessible published app.

The [official rules](https://qloo.devpost.com/rules) require Qloo plus an agentic tool/framework/integration; functional source/assets/setup instructions; a detectable license; English materials; authorized third-party integrations; and judging access through the judging period. Existing projects must explain significant in-period updates. Multiple submissions must be substantially different. Registration, participant eligibility and final Devpost submission were not inspected. The rules' existing-project clause contains a garbled phrase; explain the dated changes and clarify with the organizer if eligibility is uncertain. Keep the release available through November 5; confirm the exact shutdown date because the published schedule and rules disagree about judging end time.

README and Mac setup instructions exist and describe the local app, privacy limits and research caveats. Missing release tasks: B1–B4, the exact deployed model configuration, a final feature/Qloo/agent description and a short testing path. A video is optional; do not spend deadline time creating one instead of making the app accessible.

## UNKNOWN — requires live Sites deployment or external confirmation

The following are deliberately unverified, not assumed compatible:

| Component | Documentation/tool evidence | Required validation / smallest next step |
| --- | --- | --- |
| Build/runtime | Installed **Sites 1.1.2** skill: `SKILL.md` runtime constraints; `templates/worker-esm-starter/README.md`. Worker starter copies only its JS server and manifest. | Produce/validate a supported artifact; check static assets, MIME types, routing and production errors. No Python execution support established. |
| Secrets and provider egress | `references/identity-and-secrets.md` and native Sites environment-variable tools support server runtime secrets. HTTP external connections are documented. | Configure keys server-side after authorization; verify Qloo/NVIDIA account access, regional restrictions, quotas and timeout behavior from the deployed runtime. No secrets were fetched through Sites tools in this audit. |
| State and work lifetime | `references/storage.md` documents D1 structured storage and R2 files via hosting bindings. | Test cross-request/cross-isolate session continuity, atomic answer/budget operations, TTL cleanup and job completion after the initiating request ends. Global dictionaries and Python threads cannot be assumed to survive there. No research database is needed merely to host the current optional export. |
| Public anonymous access | Sites identity reference permits public requests without identity headers. Read-only `sites_list_sites` returned 15 owned sites, none matching this app. | Confirm anonymous access to the actual published URL, not just an owner preview. Do not require ChatGPT sign-in for the public judge flow. |
| CSP, embedding and images | Current CSP has `frame-ancestors 'none'`; remote HTTPS images and data/blob images are allowed. | Verify Sites preview/embed requirements and final headers; keep protection as restrictive as compatible. Test image-host failures. |
| Export, privacy and real mobile | Canvas export uses text, not cross-origin image pixels; client previews work locally. | Verify clipboard permissions, PNG/JSON downloads, dialog behavior and native Safari/Android sharing in the hosted context. Check actual hosting logs/retention before finalizing privacy text. |
| Platform dependencies and capacity | Current app has no third-party runtime packages; the migration may introduce them. | Audit the resulting locked dependency tree, supported runtime and concurrent visitor behavior. Current process budgets are not hosted capacity evidence. |
| Provider/publication rights and submission account | Public policies checked; account-specific permissions and Devpost form were not available in scope. | Resolve B4 and verify registration/final submission separately. No visibility or contractual action was taken. |

Sites compatibility conclusions come from the installed official Sites skill/reference files and read-only native tooling, not an assumption that all Cloudflare capabilities are exposed by Sites. No Site was created, configured or deployed.

## Release decision

**NOT READY.** The tested local game is functional, but the current source cannot simply be uploaded to Sites, public-source/demo requirements are unmet, and anonymous abuse and final-fallback attribution need fixes. Resolve B1–B5, align the model/privacy/setup details, then rerun this release's tests and a public anonymous end-to-end smoke check. Preserve the current scoring and UI scope; no redesign or new feature work is needed to address these findings.
