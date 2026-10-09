> Archived research: see the repository `research/ARCHIVE.md` for current credential/setup instructions. Original local env files are not included.

# Uncomparable research harness

Read [the findings](UNCOMPARABLE_FINDINGS.md) first. This folder is separate from the completed Civilizr neighborhood experiments. Python standard library only; no install step, application, database or external service beyond Qloo.

## Reproduce offline

From this directory, with Python 3.10+:

```powershell
python analyze.py
python -m unittest test_analysis.py
```

On macOS, use `python3` instead of `python`:

```powershell
python3 analyze.py
```

Outputs are in `tables/`: request audit, all returned entities/tags, explicit candidate missingness, property data, coverage, A/B/C comparisons, similarity matrix and stability checks. Blank matrix entries mean unavailable, not zero similarity. Flat vectors have undefined rank correlation. Top-five overlap includes all candidates tied at the cutoff; flat vectors are excluded.

## Re-run live requests deliberately

`experiment.py` reuses `../qloo.py` unchanged. It reads `QLOO_API_KEY` and `QLOO_BASE_URL` from the process environment, falling back to the ignored `../civilizr-research.env`. The supplied key works on `https://hackathon.api.qloo.com`. No key is stored in plans or logged. Do not paste keys into chat or commit env files.

```powershell
python experiment.py 08_fixed --budget 14
```

Successful responses resume locally without fresh requests. Failed requests may be tried again on rerun, so inspect the request audit first. For a deliberate uncached run use `--out-name new_name`; this consumes new requests. Exact parameters and selection history are in `plans/01_smoke.json` through `plans/10_panel_audit.json`. The aggregate 85-attempt ceiling includes past attempts in this folder; this experiment used 79. It is intentionally not a polling system. A changed plan or base host requires a new run directory. All requests are sequential, with no automatic retries and a 20-second timeout; budgets count HTTP attempts.

`preregistration.json` records pre-API plan/property/A/B hashes; the runner refuses changes to those frozen files. Later identity/source checks are in `lead_checks.json`, not retroactively added to B. `inputs.json` records accepted IDs and proxy roles; `proxy_addendum.json` adds Ray's author record. `panels.json` freezes the outcome-selected candidates before comparative scoring.

`runs/<stage>/` stores raw response JSON, exact URLs and parameters, UTC times, statuses, response hashes and run manifests. `sources/` stores source/documentation snapshots, including failed retrievals; consult source URLs and status rather than treating every saved HTML page as verified content. Both folders are ignored by Git and remain available locally. The property JSON contains independent primary-source citations; Qloo output stays separate.

The analysis verifies raw response hashes. The report's narrative judgments and accepted identity mappings are researcher-authored, not automated facts. This is a disposable feasibility experiment, not a production client or a statistically validated model.
