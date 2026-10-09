# Taste Investigator implementation plan

Keep the existing picker, typed Qloo signals, four-act visual design, deterministic verdicts, share/export and fixed-panel leave-one-out calculation. Experiment 3 supports context-dependent recommendation sensitivity, not a personality measurement or demonstrated superiority over an LLM.

1. Verify NVIDIA's hosted free development endpoint with a small structured function call. Keep credentials in the ignored app `.env`, server-side only. No Sites migration or deployment is part of this change.
2. Add a bounded investigator with persistent per-round state: original interests, scored candidates, presented predictions, feedback, competing hypotheses, uncertainty, domain coverage and budgets. NVIDIA selects structured actions; application code validates and executes them. Every prediction must reference a returned Qloo candidate. Feedback must reach subsequent decisions.
3. Reuse the original two fixed panels and input-removal calculation independently of adaptive predictions. Extra discovery may change questions, but never the baseline sensitivity experiment. Audience removal remains removal of cohort context.
4. Replace the fixed live prediction queue with approximately five adaptive questions. Keep recorded rounds and provide a clearly labeled fixed-Qloo fallback on model failure. Add an optional concise trace, not model reasoning. Update privacy, share labels and session exports.
5. Add focused tests for action validation, state isolation, duplicate/stale feedback, errors, sparse evidence, budgets and scoring. Run controlled same-input positive/negative paths with the real model and verify complete browser/mobile flows.
6. Add a three-mode evaluation harness with a shared frozen candidate panel: LLM-only (names/types, no Qloo scores), fixed Qloo, and agentic Qloo. Record controlled scenarios honestly; do not treat scripted feedback as human relevance evidence. Document candidate-selection bias and a blinded human evaluation protocol.

Use Python's standard library and the existing vanilla frontend. Keep prior research unchanged. Live provider validation is distinct from fixture tests; report any unavailable acceptance checks.
