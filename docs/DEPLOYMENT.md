# One-instance HTTPS judge deployment

No public deployment has been performed or verified. Recommended host: a Render Docker web service, paid Starter plan, one instance with a 1 GB persistent disk. Render supports Docker, managed HTTPS and health checks; persistent disks require a paid service. Confirm the price shown in your account before provisioning. This preserves the existing Python application; GitHub Pages cannot run its backend.

## Required before public launch

1. Confirm your Qloo account/event terms permit public demo display, saved-response source distribution, caching, exports and images, and that the credential remains usable through November 16, 2026. See THIRD_PARTY_NOTICES.md. Set `QLOO_DISPLAY_APPROVED=1` only after resolving this. The public entrypoint refuses to start otherwise.
2. Connect Render to the existing private repo and select the reviewed deployment branch, or use the approved clean public repo. Do not publish the old archive as a shortcut. The Docker build explicitly excludes research, tests, docs, Git history and .env files.
3. Create a Blueprint from `render.yaml`. It uses Docker, one Starter instance, `/healthz`, and a persistent disk at `/state`. Automatic deployment is off so the judging version stays stable. A private source repo is fine for hosting but does not satisfy the public-source submission requirement.
4. In service environment settings, privately set `QLOO_API_KEY` and optional `NVIDIA_API_KEY`. Never paste credentials into chat, source, a URL, a screenshot, or Devpost. If NVIDIA is absent, live rounds use labeled fixed Qloo. The public app still requires rights confirmation for recorded data.
5. Keep `BUDGET_DB=/state/budget.sqlite3`. The container bootstrap initializes `/state` ownership/mode, clears supplementary groups and drops permanently to UID/GID 10001 before executing the application. No application requests run as root. Check startup logs and actual mounted-volume persistence before judging.
6. Render supplies `RENDER_EXTERNAL_URL`; alternatively set `PUBLIC_ORIGIN` to the exact final HTTPS origin, without a trailing slash. Custom domains require this explicit origin. `PORT` defaults to 10000. TLS terminates at Render; the backend is accessible only through its trusted proxy. Do not directly expose the backend port.

The Docker command is `python container_entrypoint.py`; its brief volume initialization execs `python serve_public.py` as the unprivileged app user. On a non-container host, arrange writable volume ownership and run `python serve_public.py` directly as an unprivileged user. There is no pip/npm install or build step. Equivalent container deployment:

```sh
docker build -t your-whole-personality .
# Create a durable volume and make its mount writable by uid 10001.
# Supply secrets through your host's secret manager or a private env file outside the image.
# Configure HTTPS and the exact PUBLIC_ORIGIN; expose only the reverse proxy.
```

## Protections and budget settings

`QLOO_TOTAL_LIMIT=1000` and `NVIDIA_TOTAL_LIMIT=500` are conservative lifetime request ceilings stored in SQLite. Reservations happen before provider requests, including failed attempts. Do not delete/reset the database on redeploy. These are request limits, not dollar caps: set them to your actual remaining account allowance and use provider-side billing controls too. Per-process `QLOO_CALL_LIMIT`/`NVIDIA_CALL_LIMIT` are additional ceilings; the Blueprint sets matching values. Reaching any ceiling leaves recorded examples available.

There are at most two working live rounds, 24 live jobs and 32 HTTP connections. Body length is at most 8192 bytes; ambiguous framing and non-JSON POSTs are rejected. Socket operations time out after 10 seconds. Provider timeouts remain 15 seconds Qloo / 30 seconds NVIDIA, without automatic retries. Search is limited to 20 requests/minute, validation to 30/minute, answers to 30/minute, and valid live-round starts to 3/hour per connecting address. Request limits are fixed windows in bounded memory and reset on restart. They are best-effort anonymous abuse controls, not authenticated per-person identity.

By default forwarded IP headers are ignored. Behind a proxy all visitors may share that proxy's allowance; this is safe but may limit judge live access. Only after validating Render's real header chain and inability to bypass its edge, set `TRUST_PROXY=render` to use the rightmost appended X-Forwarded-For address. Verify spoofed leftmost values cannot change the effective visitor. Do not enable this on an arbitrary/directly accessible server. Recorded mode has no API quota and does not allocate job state, so shared-address limits do not block it.

Provider budgets persist across restarts; sessions and visitor counters do not. The app remains a bounded standard-library hackathon service behind managed HTTPS, not a general production platform. Do not scale beyond one instance. The host must also enforce edge traffic/connection protections; the app cannot absorb denial-of-service traffic. Jobs expire after 30 minutes once bounded work completes. No raw IPs, user payloads, API keys or reactions are written to the budget database. HTTP access logs are suppressed by the app; review the host's own logging separately.

## Acceptance before using the URL in Devpost

- Confirm build and startup, durable volume ownership, a valid TLS certificate and no redirect/login/payment wall.
- GET `/healthz`, `/`, `/api/config`; config must expose capability flags, never credentials.
- Run all three recorded examples through guesses, comparison, verdict and exports from an anonymous browser, desktop and phone. They must remain labeled recorded at every stage. Artwork failure must not block play.
- Set a tiny test provider ceiling on a separate test volume; exhaust it, restart, and confirm the ceiling remains exhausted while recorded mode works. Never consume the judging budget merely to test limits.
- Confirm malicious Host/Origin, oversized body, spoofed forwarding headers and excessive search requests are rejected before upstream spend.
- With real server-side secrets, complete one bounded live round and inspect its trace. Test model unavailability and Qloo unavailability; neither may fabricate successful live output. Verify the explicit recorded escape route.
- Leave the service, disk and provider access active through November 16, 2026, 11:45 p.m. Eastern. Stop automatic redeploys. Capture the deployed commit and verified source/demo URLs in the submission.

Official hosting references: https://render.com/docs/web-services , https://render.com/docs/docker , https://render.com/docs/disks , https://render.com/docs/health-checks , https://render.com/docs/blueprint-spec . Docker build, hosted TLS, actual proxy headers, provider availability and physical-mobile sharing remain unverified in this workspace.
