# Submission release review — October 21, 2026

## Decision

Keep `voxeoalyx/your-whole-personality` private. Prefer a new public repository from the reviewed allowlist after the provider-data rights gate is resolved and the owner approves publication. Do not change visibility of the existing repository or push its history to a public remote.

## Verified source and audit scope

GitHub default branch `codex/initial-transfer` was private, with no detected license. HEAD was `7afabc495c4a8644ddf4761d28509c1f70d73e3c` (October 9). The accessible commit list contained this single root commit. The recursive tree contains 2,267 files under research, in addition to application files. No AGENTS.md was present in that tree.

Reviewed application source, static assets, catalog/recordings, deployment/status/security documentation, tests and repository-audit tooling. Retrieved the 62 exact archived JSON fixtures required by the application tests: 30 raw response/metadata pairs, one unsupported-interest response and one activity coverage capture. These contain predefined cultural-entity evidence, not a real-player study. Pattern-scanned the candidate package for token/private-key patterns, literal credential assignments, forbidden files and local home paths; do not treat this as a proof of absence. No live Qloo/NVIDIA credentials were configured here, so an exact-current-secret comparison could not run. No credentials are copied into the deployment files.

The full 2,267-file research archive and all its contents were NOT cleared by this review. The existing SECURITY_AUDIT.md describes an earlier operator's transfer audit, not a new independent clearance. That older audit cannot establish current public redistribution rights. The clean export excludes unrelated studies, old research reports/screenshots, private Git history, caches and credentials; only explicitly named test fixtures are retained. Those fixtures and saved demo/catalog records still require applicable provider distribution permission.

## License review

No external pip/npm runtime packages, bundled SDKs, third-party fonts, vendored code or downloaded image files were identified in the application. Original source/style/SVG assets are covered by a standard MIT LICENSE added in this change. THIRD_PARTY_NOTICES.md excludes provider data, remote images, trademarks and unrelated archived material from that grant. No broad relicensing claim is made. Confirm any contributor/employer ownership not visible in Git before release.

Qloo's public terms reserve rights in output and refer to additional account-specific terms. They did not settle this account's permissions for saved-output redistribution, image display or public demo use. The code's public entrypoint refuses startup until QLOO_DISPLAY_APPROVED=1. This is a release gate awaiting applicable terms/permission, not a claim that the hackathon forbids deployment. Ask Qloo to clarify the specific points listed in THIRD_PARTY_NOTICES.md, including credentials through November 16; do not assume an October 30 key expiry is sufficient for judging. No message to Qloo has been sent.

## Changes

- Persistent SQLite lifetime Qloo/NVIDIA request ceilings reserved before transport; restarts do not reset ceilings on a retained disk.
- Fixed-window search, validation, answer and live-start quotas keyed by hashed connecting address; raw IPs are not retained. Proxy headers are ignored unless explicitly configured after verification.
- Two live working jobs, atomic live-start admission and answer continuation checks; bounded HTTP threads/socket timeouts; request framing/body/type checks.
- Recorded rounds are stateless and remain available when live capacity/budgets fail. Recorded mode never silently becomes a claimed live prediction or agent.
- Explicit non-root Docker runtime allowlist, persistent-volume Render Blueprint, health endpoint and fail-closed HTTPS public entrypoint.
- Accurate Devpost copy, judge steps and actual-screen recording script. No fabricated live results or validated personality/relevance claims.

## Validation

Python unittest discovery: 58 tests run successfully, with 2 explicit skips because no active keys were available for exact-value credential assertions. All 7 JavaScript tests passed. Fixtures verify the original response SHA-256 values and recomputed recorded metrics. New tests cover concurrent/restart-safe ledger ceilings, rejection before provider transport, quota isolation/expiry, spoofed forwarded-header handling, body framing and recorded availability under full live capacity. Python syntax compilation passed.

The public export is tested independently without API keys. Repository-pattern scanning reports no findings in the selected package. This is not a fresh audit of the full private repository history. Review the final PR diff and allowlist before publication.

## Not yet verified / remaining access

No Render account/hosting integration is connected in this session. No Docker CLI is available here, so container build and hosted disk permissions are not verified. Exact hosting cost/billing approval, hosted verification of the privilege-dropping volume bootstrap, deployed TLS, proxy headers, live provider access/expiry and a real hosted smoke test remain required. Use docs/DEPLOYMENT.md for exact settings and acceptance checks. No new provider calls were spent.

The connected local browser could not be accessed. The cloud Devpost page was logged out, showing registration/login rather than an editable submission. No Devpost project was created or submitted, and authenticated form-specific requirements remain unchecked. No demo video was recorded/uploaded; docs/DEMO_SCRIPT.md is a plan for actual footage. No screenshots from old verification were repackaged as proof of this release. Browser/mobile layout/sharing have not been newly validated.

## Reviewable next steps

1. Review/merge the private deployment PR; resolve Qloo rights and credential duration.
2. Connect Render, approve the paid service shown in the account, deploy and perform the documented live/recorded/TLS checks.
3. Run `python tools/export_public.py ../your-whole-personality-public`, review the output, initialize a NEW Git repository, commit and audit its history, then publish only with owner approval. Do not add the old private remote or history. Verify GitHub detects MIT and an anonymous clone passes the tests.
4. Sign in to Devpost, enter docs/SUBMISSION.md, add verified demo/public-source URLs and optional real video/gallery. Check the final required form fields and submit before October 30, 11:45 p.m. Eastern. Keep access active through November 16.
