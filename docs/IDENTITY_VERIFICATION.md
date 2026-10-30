# Identity extension verification — October 25, 2026

## Automated checks

- 54 application Python tests pass, including agent action validation, feedback isolation, transport/fallback, typed signals, scoring and HTTP boundaries. New HTTP test verifies both added modules are served and research POSTs return 404 without adding jobs, with consent true or false.
- 56 JavaScript tests pass (36 existing + 20 identity/research tests). Covers single/multiple/none/decline/skip, unsupported text, agreement/disagreement/shared/insufficient, partial evidence, consent default, allowlisted exports, schema drift/validation, unfamiliar denominator, share opt-in/revocation and canvas bounds.
- Archived suites: 14 runner/experiment tests, 6 Whole Personality metric tests, 4 uncomparable analysis tests pass. Logged mock 401/timeouts are intentional test cases.
- Archive integrity: 2,265 files verified unchanged. Indexed repository secret audit: 2,315 files, zero findings. New/modified working files: 18 scanned separately with the same secret rules; zero findings.

## Browser checks

Completed recorded overthinker rounds through all four acts, on desktop and at a requested 390 × 844 mobile viewport (document content width 375px). Measured scrollWidth equals clientWidth: no horizontal overflow. Visually inspected the mobile optional form/reveal and PNG dialog. This is viewport testing in the desktop browser, not physical iOS/Android verification.

Original verdict and PNG were available before any identity answer or consent. The 5 familiar confirmations / 1 unfamiliar scripted round preserved THE ALGORITHM HAS SEEN YOUR TYPE BEFORE. The exported original image omitted identity content. Added unsupported “Pilates” remained explicitly self-report-only; it was absent from copied text until separate sharing permission. Enabling sharing added it to the on-page card and generated 1080 × 1350 PNG with all labels visible. Canvas grows for longer text (unit-tested).

Research preview required unchecked-by-default consent and displayed the exact versioned JSON. Download completed to a local JSON file; clearing consent removed the preview. Declining identity removed previous selections/text and displayed NO ANSWER REQUIRED. Multi-selection rendered actual named interests and shared control. None was accepted without requiring another answer. New-round navigation worked. Test responses are scripted, not human preference observations.

A separate live Qloo/NVIDIA regression completed five predictions with `nvidia/nemotron-3.5-super-vl-120b-a12b`, six model calls and no fixed-prediction fallback. Scripted answers: Moon rejected; Children of Men unfamiliar; Gattaca, Primer and Ex Machina confirmed. The investigator referenced earlier feedback in its subsequent decisions. The final prose call used the existing `closing_fallback` path, so the deterministic closing line/verdict completed the round; this was not a completely fallback-free model run. Strict sensitivity remained complete with no winner, domain-specific leaders, and 3/4 familiar predictions confirmed. The optional identity check worked on that live result. The original session JSON downloaded and parsed with five predictions and no identity field. Research JSON downloaded and parsed with explicit consent and unsupported text marked unscored. No identity answers are sent to either provider. No production deployment or automatic research collection was performed.

## What this establishes

The extension can elicit a distinct self-report without changing game scoring or requiring research participation. It creates an inspectable, consent-gated file rather than a silent dataset. It does not establish that real users enjoy the interaction, finish it in 15–30 seconds, voluntarily share, provide stable identity answers, or become more loyal to a brand. Those are next experiments, with denominators and anchoring concerns in IDENTITY_RESEARCH.md.
