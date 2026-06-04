# Session Handoff

## Current Phase

`ready_for_execution`

## Current Objective

No active objective set yet.

## Last Verified State

- **Webflow page**: N/A
- **Sections**: N/A
- **Classes**: N/A

## Confirmed Targets

- Figma frame: N/A
- Webflow site: N/A
- Project slug: N/A
- Target page: N/A

## Known Gaps

No known gaps.

## 8 Workflow Patterns

1. **Write→Bash pattern**: no multi-line `python -c` (Windows shell mangles newlines). Save `.py` then run.
2. **No subagents for MCP work**: subagent runtimes in this Claude Code instance do not inherit MCP. Do MCP work in main session.
3. **EnterPlanMode for >5 Webflow writes**: one approval per phase, not per workflow.
4. **Retry on bash error in same turn**: never end a turn on a failure.
5. **Caveman terse >3 lines**: bullet list with `path:line` refs.
6. **Stop after first failure**: never stack two tool calls when the first errored.
7. **Surface stand-in swap path**: 1 line per decision.
8. **Blocker format**: "tried: N times" + "next action" + "user vs PM-recoverable".

## Files of Record

No active files of record.

## Date

2026-06-04
