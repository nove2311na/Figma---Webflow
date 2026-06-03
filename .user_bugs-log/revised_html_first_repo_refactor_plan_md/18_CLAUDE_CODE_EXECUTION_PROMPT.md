# 18 — Claude Code Execution Prompt

Use this prompt to ask Claude Code to implement the revised refactor.

```text
You are refactoring this repository into an HTML-first Figma-to-Webflow compiler framework with a Python MVP runner.

Hard constraints:
- The uploaded Client-First CSS is the binding source of truth for variables/classes.
- Final HTML cannot use a class unless it exists in the generated Client-First Library Contract, Webflow native class index, or approved structural conventions.
- Do not build directly from raw Figma to Webflow.
- Do not use whtml_builder.
- Do not paste raw HTML into Webflow.
- Do not perform any Webflow writes during this refactor.
- Strict mode: missing token/class/style/component = blocker.
- Research examples are conceptual unless classes are proven by CSS contract.

Implement one big update but follow these internal stages:

1. Archive old run-specific and Webflow-first files.
2. Add revised folder structure.
3. Add specs/rules/schemas for HTML-first compiler.
4. Add Client-First CSS contract generator.
5. Add Figma extraction contract and schema.
6. Add design-system sync strict mode.
7. Add component registry and signature matcher.
8. Add Figma normalization layer.
9. Add Semantic IR, tag resolver, class resolver.
10. Add HTML blueprint renderer and QA gates.
11. Add asset/alt manifest.
12. Add chunk slicer and golden fixtures.
13. Add Webflow native build plan compiler with branch/audit/retry policy.
14. Update README, CLAUDE.md, workflow map, SOP, prompts, policies, evals.
15. Update quality gate profile `html-first`.

Acceptance:
- No active command references archived scripts.
- CSS contract is generated from source CSS.
- Unknown class in final HTML fails.
- Strict mode does not propose/create new classes.
- HTML output has no inline style or hardcoded hex.
- Every section/component has data markers.
- Asset/alt policy catches missing alt.
- Native build plan generation does not execute writes.
- README and CLAUDE.md state HTML-first workflow.
- whtml_builder remains forbidden.
- No Webflow writes are performed.

Report progress using:
Stage:
Done:
Evidence:
Blockers:
Next:
```
