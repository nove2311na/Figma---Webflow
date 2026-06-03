# MAS Build Discipline

**Source**: lessons from SaaS — Futuristic App build (2026-06-03). 8 patterns PM committed to. See `.user_bugs-log` in the same project root for the full bug log.

**Applies to**: any agent (`pm`, `client-first-architect`, `figma-webflow-operator`, `section-builder`, `qa-gatekeeper`, `workspace-steward`) running any MAS V3 Figma-to-Webflow workflow on this repo.

**Read order**: before any work, every agent must read this file. Referenced by `agentic/memory/team-memory.md`, `agentic/orchestration/sop.md`, and `agentic/policies/runtime-instructions.md`.

---

## D-1 — Write→Bash, never multi-line `python -c`

**Bad pattern**: `python -c "code with\nnewlines"` — Windows bash mangles embedded newlines → `SyntaxError: EOL while scanning string literal`. Reproduced twice in the SaaS build.

**Required pattern**:
1. Use the **Write** tool to save the snippet to `scripts/<descriptive_name>.py`
2. Then run via `python scripts/<descriptive_name>.py`

**Exception**: trivially small single-line snippets joined by `;` (e.g. `python -c "import json,sys; print(json.dumps(sys.argv))"`). No newlines.

**Why**: portable across Windows / macOS / Linux; inspectable; diffable; re-runnable.

**Enforcement**: project-local PreToolUse hook in `.claude/settings.local.json` (see `.claude/hooks/build-discipline-guard.js`). Hook warns on `python -c` with embedded newlines.

---

## D-2 — No subagents for MCP-dependent work

**Bad pattern**: spawning `figma-webflow-operator` or any subagent to do Webflow / Figma MCP writes. Subagent runtimes in this Claude Code instance do **not** inherit MCP server connections from the parent. Result: subagent reports "tool inventory = Bash/Edit/Glob/Grep/Read/Write only" and produces a blocker, wasting ~45K tokens.

**Required pattern**: do MCP work (Webflow, Figma, asset uploads, Webflow styles/elements) in the **main session only**. Reserve subagents for:
- Read-only code exploration (Explore agent)
- Reasoning tasks that don't need external state
- Tasks explicitly scoped to filesystem + grep

**Why**: subagent MCP isolation is a Claude Code runtime characteristic. Documented limitation, not a bug.

---

## D-3 — EnterPlanMode for any phase with >5 Webflow writes

**Bad pattern**: jumping into Phase 2A with 51 style creates + 13 element creates without a per-phase plan.

**Required pattern**: any SOP phase that will mutate Webflow (2A class setup, 2B section build, Phase 3 QA fixes) must start with **EnterPlanMode**. Show the section-by-section / batch-by-batch plan in the plan file. Get user approval before writes.

**Why**: `runtime-instructions.md` §6 already requires PM to stop before Webflow writes. EnterPlanMode is the formalized version — single approval per phase, not per workflow.

---

## D-4 — Retry on bash error in same turn

**Bad pattern**: bash returns SyntaxError or "command not found" → PM says "tool failed" and waits. User feedback was explicit: this is the failure mode.

**Required pattern**: after any tool rejection, **retry in the same turn** with an alternate approach. Never end a turn on a tool failure. Common alternate paths:
- Bash failed → use Write tool + bash on the file
- Multi-line python -c failed → split into multiple calls OR Write the .py file
- Tool denied by auto-classifier → surface to user and ask for permission pattern

---

## D-5 — Caveman terse for all messages >3 lines

**Bad pattern**: long multi-paragraph explanations even with caveman mode on. Lost the terse discipline during long explanations.

**Required pattern**: any message >3 lines uses caveman formatting:
- Drop articles (`a`, `an`, `the`)
- Drop filler (`just`, `really`, `basically`, `actually`, `simply`)
- Drop pleasantries (`sure`, `certainly`, `happy to`)
- Drop hedging
- Pattern: `[thing] [action] [reason]. [next step].`
- Bullets with `path:line` refs instead of narrative

**Exception**: security warnings, irreversible action confirmations, multi-step sequences where fragment order or omitted conjunctions risk misread.

---

## D-6 — Stop after first tool failure; never stack

**Bad pattern**: one tool errors, immediately issue a 2nd tool call (or 2nd in same message) and surface both as "things failed". Final QA turn had Webflow query timeout + bash gate rejection stacked.

**Required pattern**: when any tool returns non-success:
1. STOP. Do not issue another tool call in the same turn.
2. Surface the failure with file:line evidence.
3. Retry with alternate approach in the next turn (or same turn if failure is recoverable).
4. Only after the first issue is resolved, proceed to next.

---

## D-7 — Surface stand-in asset swap path

**Bad pattern**: deciding "logos = text marks" + "images = text placeholder" during build, but not telling the user how to swap them. User has to dig through state.json to find the decision.

**Required pattern**: any "stand-in" decision (text marks, placeholder divs, simulated images) surfaces with a 1-line swap path:
- "Stand-ins: 7 brand logos = text marks. Swap: `asset_tool.upload_image_by_url(svg_url, name, alt)` per brand, then `element_tool.set_image_asset(element_id, asset_id)` on the wrapper div."
- Element IDs to swap are listed inline so the user has a copy-paste command list.

---

## D-8 — Blocker format includes retry count + next action + recoverability

**Bad pattern**: first Webflow Designer MCP blocker said "open link" without saying "tried 2 retries already" or "is this user-actionable or PM-recoverable". User had to guess.

**Required pattern**: every blocker surfaces in this exact shape:
```
BLOCKER: <one-line summary>
- Tried: <N times, with what command>
- Observed: <error string from last attempt>
- Next action: <what PM will try, OR what user must do>
- Recoverable by: pm | user
```

---

## Verification

Any agent starting a MAS run should:
1. Read this file first (it is referenced from `team-memory.md` hard invariants).
2. Run a quick self-check before each phase:
   - D-1: am I about to call `python -c` with newlines? → Write the file first.
   - D-2: am I spawning a subagent for MCP work? → do it in main session.
   - D-3: does this phase have >5 Webflow writes? → EnterPlanMode first.
   - D-4: last tool call failed — did I retry in same turn?
   - D-5: is this message >3 lines? → caveman format.
   - D-6: any tool failure in last call? → stop, surface, retry.
   - D-7: am I choosing a stand-in? → state swap path inline.
   - D-8: am I reporting a blocker? → include tried count + next action + recoverability.

## Out of scope

These 8 patterns are not a substitute for:
- The `runtime-instructions.md` agent contract (still primary)
- The SOP phase rules (still authoritative for phase movement)
- The approval gates (still gate every Webflow write)
- The standalone architecture baseline (still required for the repo to be valid)

They are a behavioral layer on top.
