# Transfer audit and verification

October 9, 2026. Scope: the Your Whole Personality application and the complete related research selected for its new private repository. No public deployment is part of this transfer.

## Secrets and history

- Inspected the original workspace Git state: no commits, no tracked app/research files, and no separate project Git history existed. A new dedicated project repository avoids importing unrelated workspace files.
- Scanned 2,345 original app/research artifacts (about 400 MB) for exact configured Qloo/NVIDIA credentials and common token/private-key patterns before packaging. No actual credential was found outside the excluded env files.
- The indexed transfer was scanned again: 2,312 files, about 261 MB, both configured API keys, common NVIDIA/OpenAI/GitHub/AWS credential patterns, literal credential assignments, private keys, local home paths and forbidden credential/generated filenames. Zero unresolved findings. The final documentation and commit are checked again before push.
- Two original runner-test values are deliberately synthetic. Their exact value hashes are allowlisted only in that test file; there is no directory-wide test exemption. Public review URLs containing a `/home` URL component were distinguished from absolute local filesystem paths.
- `.env`, other actual env files, private-key files, virtual environments, caches, temporary captures and editor/OS files are ignored. `.env.example` contains blank Qloo/NVIDIA credentials. No credentials were rotated because no committed exposure was found in this audit.
- `tools/audit_repository.py --history` scans the Git index and every object reachable from all local refs, including older blobs and commit/tag messages. It checks configured secrets without displaying values and fails on findings or an incomplete audit. The optional pre-commit hook scans the index. Enable it after each clone with `git config core.hooksPath .githooks`.

These checks are scoped evidence, not proof that every possible secret format is detectable. Untracked/ignored future files are not checked by the Git audit. Review newly collected data, participant information and new credential types before adding them. Keep the repository private unless Qloo distribution/display rights and all included evidence are reviewed for public release.

## Application and transfer checks

- All 52 Python application tests and seven JavaScript tests passed on the prepared laptop checkout. Two added regressions cover independent checkout configuration and secret-guard behavior.
- Exported only the Git index into an empty scratch directory, with no `.env`, no old cache and no API keys in the process. All 52 application tests completed successfully; the two tests requiring an active secret for exact-value checking explicitly skipped (they passed in the configured checkout). All seven JavaScript tests passed.
- The clean export started through `server.py`, served the page/config, and completed the recorded-game HTTP flow with six labeled predictions. POSIX launcher/hook syntax passed. This is Windows-based portability verification, not a claim that physical Mac/Safari testing has occurred.
- Research tests: Civilizr 14, Uncomparable 4, Whole Personality 6; all passed without live requests. Verified all 2,265 transferred file hashes. The original research runner hash remains unchanged, and the Whole Personality study audit verified its 183 raw responses and frozen preregistration in the scratch export.
- Bounded live smoke: one Qloo request returned three scored movie recommendations; one NVIDIA request returned a valid TEST_PREDICTION action using `nvidia/nemotron-3-super-120b-a12b`. No full paid benchmark or new provider integration was introduced.

Gameplay/scoring/model logic was preserved. App changes are limited to portable credential lookup, startup scripts and fixture locations/requirements. Research code/raw responses retain original bytes; only three copied setup READMEs received portability notes, tracked in the transfer manifest. Omitted 38 bulky per-run CSVs are reproducible from preserved raw JSON. Future live runs and API availability may differ from these checks.
