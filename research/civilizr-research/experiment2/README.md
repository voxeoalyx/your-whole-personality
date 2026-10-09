> Archived research: see the repository `research/ARCHIVE.md` for current credential/setup instructions. Original local env files are not included.

# Disposable Experiment 2

Python 3.10+, standard library only. Run commands from the `civilizr-research`
directory. No installations, service, database, frontend or economic dataset.

The primary result is `../EXPERIMENT_2_FINDINGS.md`; frozen methodology is
`../EXPERIMENT_2_PLAN.md`. `DEVIATIONS.md` records the scoped lookup failure,
panel-size limit and supplementary diagnostics. Experiment 1 is preserved.

## Run / resume / inspect

The supplied key remains in ignored `civilizr-research.env`, with
`QLOO_API_KEY` and `QLOO_BASE_URL=https://hackathon.api.qloo.com`. Process environment
variables override the file. The shared runner validates the host, uses the key
only in its header, redacts echoed keys, and records request parameters separately.

```powershell
python experiment2.py run --stage 03-main --budget 14
python analyze_experiment2.py
python -m unittest test_qloo test_experiment2 -v
```

On macOS, use `python3` instead of `python`:

```powershell
python3
```

Same-directory successful requests are reused locally. Failed requests can resume
within the attempt budget. A changed plan, code hash or frozen inputs require a
new run directory; never edit an old manifest to bypass that safeguard. The
Experiment 2 driver enforces a 90-attempt total; **80 were used in this experiment**.
Its early discovery runs predate final driver/configuration hashes and are preserved
as historical runs, not resumable under a different identity.

To deliberately repeat later without the local cache, use the shared runner with
a **new directory**, retaining the frozen plan and an explicit small budget:

```powershell
python qloo.py run experiment2/plans/07-repeat.json --out runs/experiment2-repeat-YYYYMMDD --env civilizr-research.env --budget 4 --retries 0
```

This is a new future run outside the original 80-attempt analysis. Its results need
a separate temporal comparison; the current analyzer intentionally does not merge
unknown future stages into the historical experiment. Server caching is not disabled
or bypassed. UTC timestamps and HTTP response dates remain in metadata.

## Files and interpretation

- `plans/`: every exact request, including small probes and supplemental checks.
- `runs/`: raw Qloo JSON, metadata, source hashes and per-attempt logs, locally
  ignored by Git. The shared runner's automatic `evidence.md` does not analyze
  `fixed_profile` requests; use **this experiment's reports** instead.
- `candidates.json`, `panels.json`, `candidate_audit.csv`: native IDs, selection
  source, exclusions and membership. No unscored candidate is turned into zero.
- `geographies.json`, `geographies.csv`, `GEOGRAPHY.md`: coordinates, polygons,
  areas, official references and proxy limitations. Plans are the definitive WKT.
- `sources/`: ignored official-source snapshots, their retrieval metadata, OSM
  snapshot and supplementary geometries. Query URLs permit source refresh, but
  a refreshed snapshot should go into a new experiment so dates remain explicit.
- `inventory_request.json`: exact Overpass query. `python experiment2.py inventory`
  reuses an existing local snapshot; it makes one bounded request when absent.
- `reports/coverage.csv`: which full panels can actually be compared.
- `reports/fixed_fingerprints.csv`: native scores and ranks; partial panels are
  explicitly marked and excluded from full-panel similarity matrices.
- `reports/pairwise_baselines.csv`, `baseline_cross_validation.csv`,
  `baseline_residual_contrasts.csv`: distance/inventory comparisons. Leave-one-area-out
  folds exclude every touching pair from training; pair endpoints are tested in
  two folds, so counts are not independent observations. Negative held-out R² means
  worse error than the fold's training-mean predictor, not inverse cultural value.
- `reports/geographic_sensitivity.csv`: prespecified, supplementary and point
  checks labeled by stage. Only stage 04 enters the frozen robustness gate.
- `reports/candidate_sensitivity.csv`, `cross_city_matches.csv`,
  `repeat_request_equality.csv`: candidate dependence, exploratory analogues and
  immediate reproducibility, including explicit missingness limitations.
- `PROVENANCE.md`: reviewed documentation and unanswered Qloo questions.

`python experiment2.py discovery`, `freeze`, and `plans` rebuild the original
configuration from archived discovery inputs, refusing changes to frozen files.
Additional diagnostic plans are preserved verbatim; they do not require regeneration.
The OSM inventory uses point-in-polygon membership and named feature deduplication
within 30 m. Way/relation coordinates are Overpass bounding-box centers, not precise
entrances. Missing mappings and possibly closed businesses prevent treating it as
a census of operating establishments.

**Inventory attribution:** © OpenStreetMap contributors, under the
[ODbL](https://opendatacommons.org/licenses/odbl/1-0/).
[OSM copyright and attribution](https://www.openstreetmap.org/copyright).
Keep attribution with inventory exports. Qloo output and derived-score commercial
permissions remain subject to the applicable account agreement, as recorded in
`PROVENANCE.md`.
