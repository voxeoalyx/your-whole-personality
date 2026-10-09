# Whole Personality research harness

Disposable Qloo experiment, separate from Civilizr and Uncomparable. Python standard library only. Start with `WHOLE_PERSONALITY_FINDINGS.md`; the recommendation is **NARROW**.

## Read the results

- `WHOLE_PERSONALITY_EXPERIMENT_PLAN.md`, `NARRATIVE_PROTOCOL.md`, `llm_baseline.json`: frozen before API recommendations; hashes in `preregistration.json`.
- `seeds.json`, `profile_design.json`, `panels.json`, `configurations.json`: reviewed entities and exact experimental fixtures.
- `plans/*.json`: exact endpoint and query parameters; `profile_refs.json` and `secondary_refs.json` identify deduplicated requests.
- `runs/`: local raw response bytes, response hashes, metadata, UTC timestamps, manifests and request-attempt logs. Git ignored.
- `tables/`: UTF-8 CSV with BOM for spreadsheet readers. Missing scores remain blank. `faithful_inputs` distinguishes ignored inputs from complete output panels; blank means that comparison was not run.
- `BRAND_PARTNERSHIPS.md`: all five brands, both combinations and singleton controls.
- `LLM_VS_QLOO.md`, `qloo_narratives.json`: narrative comparison and grounded drafts.
- `evaluation/BLINDED_PACKET.md`, `feedback.csv`: six cases for later human evaluation. Keep `evaluation/answer_key.json` away from evaluators. No feedback is filled in.
- `PRODUCT_AND_COMMERCIAL.md`, `API_NOTES.md`, `DEVIATIONS.md`: proposed validation, rights questions and limitations.

## Reproduce offline

From this directory, using an available Python 3 interpreter:

```powershell
python analyze.py
python narratives.py
python -m unittest test_metrics.py
python audit.py
```

The offline workflow makes no API calls. It rebuilds tables and the comparison packet, verifies response and preregistration hashes, and checks metric behavior. Existing human `feedback.csv` is preserved. Narrative drafts and the LLM-only baseline are saved artifacts; offline analysis does not call a language model or claim to reproduce its prose generation. `audit.py` scans artifacts for the active key without displaying it; this check is explicitly skipped if no key is configured. Python 3.9+ is required.

## Requests, credentials and resuming

The wrapper imports the existing `../qloo.py` without modifying it. It reads `QLOO_API_KEY` and optional `QLOO_BASE_URL` from the process environment, falling back to the existing ignored `../civilizr-research.env`. Process values take precedence. Do not put credentials in request plans. The default API origin is the existing harness configuration; manifests preserve the actual origin used by this run.

The six stages used 19 + 12 + 18 + 94 + 27 + 13 = **183 attempts**. The matrix stage was resumed once after a smaller initial budget. Successful requests are cached locally, requests execute sequentially, timeout is 20 seconds, retries are disabled, and the experiment-wide ceiling is 185 attempts including failures.

To resume an interrupted stage, use the existing stage name and a deliberate request budget, for example:

```powershell
python experiment.py 04_matrix --budget 8
```

Completed requests are reused; this command makes no new calls against the completed archive. `01_lookup`, `02_pilot`, `03_gate`, `04_matrix`, `05_secondary`, `06_checks` are the exact stage names. `python gate.py` verifies the pilot decision from saved responses. Stage execution does not automatically dispatch later stages. The original gate was explicitly checked before the matrix.

Do not delete the archive to obtain a new sample. The 185-attempt limit belongs to this completed experiment, leaving only two attempts. A new date-separated study needs a separately frozen protocol, budget and archive. Replaying identical parameters later may return changed server data; only the saved-response analysis is exactly reproducible here.

No UI, dependency installation, product database, deployment, external messages or API key commits are part of this research.
