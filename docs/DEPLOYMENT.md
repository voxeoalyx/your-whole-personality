# Deployment of the existing Python prototype

No deployment has been performed. GitHub stores source; GitHub Pages cannot execute this Python backend. ChatGPT Sites did not provide native model inference in the earlier investigation, and this app has not been adapted to its Worker runtime.

Use a Python-capable host with an HTTPS reverse proxy. Deploy the root Python files plus `static/` and `data/`; no pip or npm build/install is required. Research and tests can stay in Git without being included in a runtime image. Configure `QLOO_API_KEY`, `NVIDIA_API_KEY`, `QLOO_BASE_URL`, `QLOO_CALL_LIMIT`, `NVIDIA_MODEL` and `NVIDIA_CALL_LIMIT` through the host's secret/environment settings. Never upload a local `.env` as a public asset.

Start with Python 3.10+:

```sh
python3 server.py --host 0.0.0.0 --port 8765 --public-origin https://your-actual-host.example
```

Replace the example origin with the exact real HTTPS origin, without a trailing slash/path, and choose the port required by your host. The proxy must preserve that Host header, terminate TLS, and enforce body-size, request-timeout, rate and concurrency limits. Expose only the proxy. Smoke-check `/`, `/api/config`, and a recorded round before spending live requests. Config exposes capability flags, not keys. One small live round verifies the provider credentials and current availability.

This is a bounded development/hackathon prototype, not a production-hardened server. Run one process/instance: jobs, investigator state, cache and budgets are in memory. Restarts lose sessions and reset budgets; multiple instances would not share them. Two active rounds are allowed, but there is no user authentication or per-user quota. Add abuse controls and review the stdlib server before opening it broadly. Provider free development access is not an unlimited public-service allowance.

Confirm Qloo's applicable display/caching/distribution rights and image requirements before public use. Keep provider privacy disclosure visible. Test real Safari/mobile sharing and failure paths; automatic downloads/clipboard delivery remain unverified on those devices. Use [INVESTIGATOR_RESULTS.md](../INVESTIGATOR_RESULTS.md) for the current evidence and human-evaluation limitations.
