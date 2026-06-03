---
name: reflection-review
description: Review MAS Figma-to-Webflow blueprints, Webflow action logs, QA reports, and handoffs with a bounded reflection loop. Use when Claude Code needs to critique an artifact, score it against evidence, require revisions, or decide whether a MAS phase can advance.
---

# Reflection Review

## Use When

- A blueprint, Webflow action log, QA report, or handoff needs critique before phase closure.
- The PM needs an evidence-backed pass, revise, or block decision.
- A Webflow mutation log must be checked for ReAct fields.

## Workflow

1. Read `agentic/orchestration/reflection-loop.md`.
2. Read the target artifact and any cited workspace evidence.
3. Score the artifact with `agentic/evals/reflection-rubric.md`.
4. Write or request a `reflection_review` entry in `workspace/state.json`.
5. Return one verdict: `pass`, `revise`, or `block`.

## Validation

- Pass only when the score is at least 4.6 and no hard failure exists.
- Revise when evidence is present but the score is between 4.0 and 4.59.
- Block when approval, ReAct trace, Webflow evidence, or artifact ownership is missing.
- Never approve a phase transition; route the decision back to `pm`.

## Bundled Resources

- `references/review-card.md` contains the compact scoring card.
- `scripts/check_react_entries.py` checks a `workspace/state.json` file for Webflow ReAct entries.
- `assets/review-card-template.md` is a reusable reflection note template.

