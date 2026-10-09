# Verification log

2026-10-08. These are engineering checks, not evidence of human entertainment or preference accuracy.

| Check | Evidence / result |
|---|---|
| Three distinct live interest combinations | `record_demos.py --live` completed 30 Qloo calls: Radiohead/Blue Bottle/Severance; Taylor Swift/Starbucks/Friends; Metallica/Nike/Elden Ring. All have six predictions and complete two-domain ablations. |
| Recommendation provenance | Python test checks names, UUIDs and affinities against saved raw response bytes and response hashes in `research/prototype/verification/`. Fixture sensitivity recomputes exactly. |
| Local live browser flow | Overthinker round completed from starter selection through all guesses, removal preview and verdict. Guesses included Moon and Control, from unsupplied categories. |
| Five-interest boundary | A custom live round with Spirited Away, Radiohead, Blue Bottle, Taylor Swift and The Joe Rogan Experience produced six guesses and all five ablations. A sixth selection was refused; replacement through “Make a swap” worked. |
| Service failure | A separate server with a zero-call budget produced the correct error and allowed an explicitly labeled recorded round. Fixed a progress message accidentally overwriting the error text. |
| Three browser game loops | Overthinker live, comfort recorded, side quest recorded completed all four acts. Recorded modes stayed visibly labeled. |
| Unfamiliarity | Three yes, one no, two unknown produced 75% from 3/4 familiar guesses. Six unknown produced an insufficient-evidence verdict with no accuracy percentage. Six no produced 0/6 and statistical inconvenience. |
| Unsupported input | Live book search resolved Dune (1965, Frank Herbert); keyboard selection returned a clear rejection without adding or substituting an interest. |
| Missing/flat data | Tests with omitted candidates and flat scores return undefined distances and no winner. Incomplete baseline stops the round; incomplete ablations permit guesses but withhold an influential-interest claim and comparison. |
| Mobile | Browser tested at 390×844 and 320×740. Fixed the narrow progress strip; no horizontal overflow at either width. Fixed heading spacing, counter wrapping and excessive guess-header height.  |
| Startup | The supplied PowerShell start script launched the local server on a temporary test port; the normal server is left running on 8765. |
| Desktop | Browser tested at 1280×900; verdict layout has no horizontal overflow. Selected historical screenshots are preserved in `docs/verification/`. |
| Keyboard | Search ArrowDown + Enter selected the exact Dune record; Enter started a live round. Native buttons, select, focus outlines, skip link and dialog use standard keyboard controls. Full assistive-technology audit remains pending. |
| Sharing | 1080×1350 PNG generated, previewed and extracted from its visible image for visual inspection. Recorded label and separate measurements included. In-app automatic download event did not complete; added explicit PNG link and image-save fallback. Clipboard permission failed; selectable summary fallback was displayed. Direct automatic downloads/native sharing in other browsers remain unverified. |
| Secrets / HTTP | Exact active-key scan of client/data/tests passed. HTTP tests reject secret/source paths, unknown inputs, hostile Host/Origin and check config contains no credential. No key was copied into app files. |
| Automated tests | 16 Python tests and 7 JavaScript tests passed. Pure verdict tests enumerate all yes/no/unknown distributions; a synthetic valid sensitivity winner exercises the positive hijack branch. |
| Research preservation | Application is a sibling directory. Existing `civilizr-research/qloo.py` hash remains `88926b5ff19d9578b0be91249bce28af4fa4ad08289956bda59ef7d9d0db267e`. Prior experiments were not edited. |

No participant ratings were stored. Test answers were deliberate verification inputs, not the developer's actual tastes. No claims about share conversion, real-world accuracy, licensing approval, public availability or production security follow from these checks.
# Activity picker extension — October 8, 2026

- 31 Python tests and 7 JavaScript tests pass. Original entity-only fixtures recompute identically. New tests cover correct URN routing, all-family ignored-input warnings, mixed leave-one-out removals on identical panels, real flat Pilates/weightlifting captures, alternate panels for tied top results, explicit hobby-only search, partial endpoint errors, and typed validation through the actual local HTTP boundary.
- Six complete live research games cover Running/Yoga/Architecture audiences, Architecture books/Yoga music tags, and a five-pick mix containing entities, a tag and two audiences. Full evidence and limits: [ACTIVITY_SIGNALS.md](ACTIVITY_SIGNALS.md).
- An additional live browser round combined Running's audience, Radiohead, Blue Bottle and Architecture's book tag. All six guesses, audience removal, verdict and remix worked. Two test confirmations, two rejections and two unfamiliar answers produced 2/4 = 50%. The ranking winner retained the explicit “Books genre tag” label. The exported 1080×1350 PNG was inspected without overlaps (`docs/verification/activity-share-card.png`). These are synthetic test reactions, not preference-validation data.
- The picker visibly distinguishes audiences, tags and incidental entity titles. A known-unsupported search displays its limitation instead of selecting broader wellness. No new package dependency, storage or feedback transmission was added.
- Final server browser check: selecting Pilates studio by keyboard was refused after the coverage check, leaving zero picks and an explicit no-substitution explanation. At a 320-pixel viewport, document width was 305 pixels (scrollbar allowance), with no horizontal overflow. Restaurant/hotel tag variants have distinct type labels. The original research harness file remained unchanged.
