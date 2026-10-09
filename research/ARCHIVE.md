# Research archive

This directory makes the checkout self-contained. It preserves the earlier Civilizr neighborhood experiments (including negative findings), Uncomparable feasibility study, Whole Personality study, activity-signal probes and investigator comparisons. No credentials or real participant dataset are included.

- `civilizr-research/`: original code, preregistration, plans, documentation snapshots, raw JSON responses, manifests, attempt logs, reports and compact tables from the complete earlier research tree.
- `prototype/verification/`: raw responses and hashes behind all three playable recordings.
- `prototype/activity-signals/`: complete activity lookup/coverage probes and six mixed-signal games, including flat/unsupported cases.
- `investigator/runs/`: all saved JSON comparison/browser runs, including failures, not just successful examples.
- `../docs/verification/`: selected share-card/mobile screenshots.
- `TRANSFER_MANIFEST.json`: relative paths, byte counts and SHA-256 hashes of retained evidence and omitted reproducible exports. Documentation portability edits are separately identified.

Earlier READMEs describe runs as local/Git-ignored and mention a preexisting env file. Those are historical workflow descriptions: these curated response archives are now intentionally versioned in a private repository, and that env file is deliberately excluded. The live application reads only the root `.env` or process environment. Frozen research runners can receive `QLOO_API_KEY`/`QLOO_BASE_URL` via environment, or an explicitly selected ignored local env file; never put credentials into plans. Do not rerun completed experiments merely to validate the transfer.

## Reproduce offline

From the repository root:

```sh
python3 -m unittest discover -s research/civilizr-research -p 'test_*.py' -v
python3 -m unittest discover -s research/civilizr-research/uncomparable -p 'test_*.py' -v
python3 -m unittest discover -s research/civilizr-research/whole-personality -p 'test_*.py' -v
python3 research/civilizr-research/whole-personality/audit.py
python3 tools/verify_archive.py
```

The Whole Personality audit verifies 183 raw responses and preregistration; it updates its derived audit table. Its own exact-key scan is skipped without the legacy env file; the repository audit covers archived content using root `.env` independently. Run analysis in a scratch copy if you want the versioned historical derived tables untouched. Follow each study's README for its analysis entry point and original budget/protocol.

Only bulky per-run `results.csv` exports were omitted (38 files, about 139 MB). Original JSON responses and compact published tables remain. Regenerate a particular run's CSV without API calls:

```sh
python3 research/civilizr-research/qloo.py analyze research/civilizr-research/PATH/TO/RUN
```

Use the run-directory paths listed in `TRANSFER_MANIFEST.json`; replace `PATH/TO/RUN` with one of them relative to `civilizr-research`. Regenerated per-run `results.csv` remains ignored. Other derived outputs may change: inspect `git diff`. Live API calls can change over time; saved-response analysis is the reproducible evidence here.

Research files have Git text conversion disabled to preserve source/response hashes on Windows and Mac. Original `qloo.py` SHA-256: `88926b5ff19d9578b0be91249bce28af4fa4ad08289956bda59ef7d9d0db267e`. The original laptop research directory was not modified.
