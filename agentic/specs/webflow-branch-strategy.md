# Webflow Branch Strategy Specification

This spec outlines branching, preflight, concurrency, and retry policies for safe, audit-logged Webflow operations.

## Branching & Authorization Rules

1. **Branch-First Deployments**: All mutations must run on a temporary site branch, not directly on the main/production site setup.
2. **Preflight Check**: A preflight smoke call must verify tool visibility and branch accessibility before executing the build plan.
3. **Execution Serialisation**: To avoid database lockups and API rate limits, all Webflow write processes must execute strictly serialized (one operation at a time).
4. **Audit Logging**: Write operations must output transactional entries to a local audit log (`write-audit-log.jsonl`), detailing each action's payload, response, and observation.
5. **No Auto-Publish**: Auto-publish is strictly forbidden from the compiler pipeline. Publishing is manually triggered or gated separately.
