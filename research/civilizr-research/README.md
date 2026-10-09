> Archived research: see the repository `research/ARCHIVE.md` for current credential/setup instructions. Original local env files are not included.

# Civilizr: disposable Qloo research

Start with [Experiment 2 findings](EXPERIMENT_2_FINDINGS.md): the controlled follow-up
recommends **STOP / RETHINK**. Its [run guide](experiment2/README.md) covers fixed panels,
geographic sensitivity and the independent venue baseline. Original
[Experiment 1 findings](FINDINGS.md) and all raw work are preserved.
Python 3.10+; **no pip packages, server, database or UI**.

## What is here

- [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md): plan and screening gates written before implementation.
- [API_NOTES.md](API_NOTES.md): current official endpoints, semantics, links and documentation gaps.
- `qloo.py`: sequential request runner, raw capture, CSV export and rank comparisons.
- `plans/*.json`: exact request definitions, including failures and sensitivity probes.
- `localities.json` / `taxonomy.json`: reviewed Qloo IDs and their source responses.
- `runs/01-*` through `runs/09-*`: original local observations, request logs and parameters.
- `runs/11-final`: offline analysis view referencing original raw files.
- `reports/`: compact matrices, per-area top results, coverage and geometry sensitivity.
- `summarize.py`: regenerates descriptive tables for the frozen nine original runs.
- `test_qloo.py`: offline tests using synthetic fixtures only, never research observations.

## Credentials

Set `QLOO_API_KEY` in the process environment, or copy `.env.example` to `.env` and
edit locally. An environment value takes precedence over a file value. The supplied
credential is already in **`civilizr-research.env`**, with the confirmed host
`https://hackathon.api.qloo.com`; use `--env civilizr-research.env` for this file.
The production host rejected this particular key. The runner does not automatically
switch hosts. All `*.env`, `.env*` secrets, raw runs and doc snapshots are ignored
by Git. No key is stored in source, URLs, manifests or logs.

## Smallest fresh live test

Run from this folder in PowerShell:

```powershell
python qloo.py run plans/smoke.json --env civilizr-research.env --out runs/fresh-smoke --budget 5 --retries 0
```

Use your installed Python 3.10+ interpreter (`python3` on macOS, or `python` in the activated virtual environment). No packages are required. Do not rerun all stages before inspecting the small test.

```powershell
python qloo.py run plans/pilot.json --env civilizr-research.env --out runs/fresh-pilot --budget 6 --retries 1
# Repeat exactly the same command to resume the remaining requests.
python qloo.py analyze runs/fresh-pilot
python -m unittest -v
python summarize.py
```

A budget counts **HTTP attempts including retries**, not only successful queries.
Defaults: 5 attempts, 20-second timeout, one retry, 0.3-second pacing. Requests are
sequential. 401/403 stops the run; 400/404 is retained without automatic retry.
429/5xx/network errors have bounded retry/backoff; long Retry-After stops for later
resumption. Nonzero exit codes mean partial/failing runs (1) or setup/missing key (2).
Missing credentials create a manifest/status with zero HTTP attempts.

Successful files are reused only within the same output directory. Use a **new
directory for an independent repeat**. Changed request plans, host or runner source
hash require a new directory; the original observations remain intact. Resume is
not a fresh measurement. The final runner has improved CSV parsing compared with
the earliest saved source hashes; analyze those old runs offline or start a fresh
run rather than trying to append to them.

Each raw response is `request_id.aN.json` (unexpected non-JSON bodies are `.txt`).
Each `.meta.json` records exact URL, parameters, response file/hash, status and UTC
time. `requests.jsonl` preserves all attempts; `invocations.jsonl` records timeout,
budget and retry settings. Secret echoes, if any, are redacted and flagged. No raw
body or credential-bearing request headers are printed to the terminal.

## Read the outputs correctly

`coverage.csv` distinguishes not-run, failed, empty and scored results. `results.csv`
includes IDs, native affinity/popularity, tags, coordinates and explanation fields;
`query_metadata.json` preserves query-level metadata and warnings. The full response
is authoritative if the normalizer does not recognize a future response shape.

`fingerprints.csv` is a sparse union-of-IDs vector: membership and 1/rank for returned
top-k items. An omitted item means **not observed in top-k**, not zero true affinity.
`matrix_*` and `similarity_pairs.csv` provide Jaccard and reciprocal-rank cosine at
k=10 and k=20. Comparisons require matching endpoint/parameters except location,
reviewed geography, k unique IDs and k numeric affinity values. Ties are flagged;
prefer Jaccard when arbitrary tie order affects cosine. Inventory/proxy/seeded
diagnostics are not folded into one maturity score. `control_rank_differences.csv`
reports observed ranks and missing-top-k flags; it does not estimate statistical lift.

Raw affinity scores are query-normalized. Do not compare absolute score differences
across geographies, treat API popularity as local spending, or treat global trends as
neighborhood growth. Sports teams, universities and health systems are also Qloo
brands; the brand domain is broader than retail.

## Frozen stages

| Plan | Requests | Purpose |
|---|---:|---|
| smoke | 5 | Authentication, locality resolution, first tag capability |
| discovery | 11 | Remaining locality searches; five native taxonomy searches; tag-type page 2 |
| pilot | 18 | Three resolved areas, Orlando/no-location baselines, uncached Winter Park repeats |
| culture-pilot | 10 | Five place categories for Winter Park and Pine Hills in a shared 20 km candidate area |
| expansion | 9 | Remaining three resolved areas: tags, brands, destinations |
| culture-remaining | 20 | Same five place categories for the remaining four resolved areas |
| diagnostics | 13 | Mills 50 aliases/places, explainability, three trend routes, six heatmap probes |
| sensitivity | 7 | Three Qloo-derived centers at 500/1,000 m for brands; corrected locality heatmap |

These are historical plans, not a command to rerun everything. Original attempts:
95 including the rejected production-host call and one retry of a server error.
The exploratory Mills 50 point proxy is explicitly separate from the six verified
locality profiles; it is not an official neighborhood polygon.
