# Retry and Stop Conditions

| Workflow | Retry Limit | Stop Conditions |
|---|---:|---|
| workspace init | 1 | workspace exists and required files exist, or script failure. |
| archive workspace | 1 | archive missing/empty, explicit user cancellation, or successful wipe. |
| restore workspace | 1 | workspace non-empty, archive missing, or successful restore. |
| Figma extraction | 2 | raw/content files created, Figma auth failure, missing URL/node. |
| blueprint creation | 2 | blueprint ready for approval, missing raw data, unresolved design ambiguity. |
| Webflow build | 3 | MCP-352 verification boundary, tool failure, target mismatch, QA needed. |
| class + container setup (Phase 2A) | 1 | all classes created and registered + containers created, or tool failure (deterministic, no backoff). |
| section build per subagent (Phase 2B) | 3 | section subtree matches contract, MCP-352 boundary, missing class blocker, or tool failure. |
| parallel QA aggregation | 2 | all section logs reconciled vs blueprint, or a section needs a fix loop. |
| QA loop | 5 | `[APPROVED]`, repeated same blocker, missing Webflow evidence. |

If the same blocker repeats three times, PM records it in `agentic/memory/session-handoff.md` and asks for the missing external state or decision.
