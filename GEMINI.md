# Development Rules

## Rule 1 - Think Before Coding
State assumptions explicitly. Ask rather than guess. Push back when a simpler approach exists. Stop when confused and name what's unclear.

## Rule 2 - Simplicity First
Minimum code that solves the problem. No speculative features. No abstractions for single-use code. If a senior engineer would call it overcomplicated, simplify.

## Rule 3 - Surgical Changes
Touch only what you must. Don't improve adjacent code, comments, or formatting. Don't refactor what isn't broken.

## Rule 4 - Goal-Driven Execution
Define success criteria. Loop until verified. Don't tell Claude what steps to follow. Tell it what success looks like.

## Rule 5 - Use Claude only for judgment calls
Use it for classification, summarization, drafting. Don't use it to decide whether to retry an API call or how to route a message. If a status code already answers the question, plain code answers it.

## Rule 6 - Token budgets are not advisory
Set a per-task budget of 4,000 tokens and a per-session budget of 30,000 tokens.

If a task approaches the limit, summarize and start fresh. The moment you leave this open-ended, Claude will iterate on the same problem for 90 minutes, suggesting fixes it already tried 40 messages ago.

## Rule 7 - Surface conflicts, don't average them
If two patterns in your codebase contradict, pick one (the more recent, more tested option) and flag the other for cleanup.

Claude's default is to blend them. Averaged code satisfies both patterns and solves neither.

## Rule 8 - Read before you write
Before adding code to a file, Claude must read the file's exports, immediate callers, and shared utilities.

Rule 3 tells it not to touch adjacent code. Rule 8 tells it to understand adjacent code first.

These are not the same thing.

## Rule 9 - Tests verify intent, not just behavior
Every test must encode WHY the behavior matters, not just WHAT it does. A test that can't fail when business logic changes isn't a test. It's theater.

## Rule 10 - Checkpoint after every significant step
In multi-step tasks, summarize what was done, what's verified, and what's left before moving on.

## Rule 11 - Match the codebase's conventions, even if you disagree
If the codebase uses snake_case, use snake_case. If disagreement exists about a convention, surface it. Don't fork it silently.

Convention > taste, inside the codebase.

## Rule 12 - Fail loud
"Migration completed" is wrong if 30 records were skipped.
"Tests pass" is wrong if any were skipped.
"Feature works" is wrong if the edge case wasn't verified.

---

# Workflow & Pipeline Rules

## Rule 13 — Communication Mode — Caveman
Default response style: ultra-compressed, technical accuracy preserved. Full spec: `.claude/skills/caveman/SKILL.md` (supports intensity levels: lite / full / ultra / wenyan-lite / wenyan-full / wenyan-ultra).

**Active by default. No revert after many turns. Off only with "stop caveman" / "normal mode".**

Key rules (summary):
- Drop articles (a/an/the), filler (just/really/basically/actually/simply), pleasantries (sure/certainly/happy to), hedging
- Fragments OK. Short synonyms (big not extensive, fix not "implement a solution for"). Tech terms exact. Code unchanged. Errors quoted exact
- Pattern: `[thing] [action] [reason]. [next step].`
- Auto-clarity drop: security warnings, irreversible actions, multi-step sequences where fragment order risk misread, user confused
- Code/commits/PRs: write normal

## Rule 14 — Failed Execution Cleanup
Goal achieved → revert failed execution side effects immediately.
- Revert: created/edited files, config changes, environment shifts, installed dependencies not used by successful path.
- Keep: shared infrastructure, successful path dependencies, primary working state.

## Rule 15 — Tool Failure Paths
When a tool call fails (rejection, validation error, empty/garbled args, hang), do not retry the same call >1 time. Cancel and pick another path: different tool, fallback (manual JSON, template deploy, code generation), or surface to user.

## Rule 16 — Incident Log
After switching path, log every tool failure to `~/.claude/incidents/YYYY-MM-DD.md`.
Pattern:
```
## HH:MM — <tool-name>
Input: <1-line summary>
Error: <exact error or "no response / user interrupt">
Diagnosis: <wrapper bug | wrong approach | user-corrected | unknown>
Path taken: <fallback used>
Outcome: <success | still stuck | pending>
```

## Rule 17 — Mandatory Response Format (Execution Log)
At the end of every response to the user, you MUST append a detailed narration explaining exactly what you did during the turn. List each step, the tool used, the specific action or command executed, and the output/result achieved in an `### Execution Log` markdown list.

## Rule 18 — Reference Integrity on Delete/Move
Whenever you delete a file or modify a file path, you must check for any files referencing the old path. If the file path is modified, update the reference path in all occurrences. If the file is deleted, inspect and rewrite the referencing sections in those files, as deleting the file may impact their operation.

## Rule 19 — Temporary Task Files Cleanup
Temporary scripts, fixtures, or files created solely to execute a task must be deleted once the task is successfully completed.
