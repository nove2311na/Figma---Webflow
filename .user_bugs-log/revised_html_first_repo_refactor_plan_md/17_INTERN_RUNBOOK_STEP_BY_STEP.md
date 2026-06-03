# 17 — Intern Runbook: Step-by-Step

## 0. Safety

Do not:
- use Webflow write tools;
- publish;
- use `whtml_builder`;
- invent classes;
- modify Figma automatically.

## 1. Create branch

```bash
git checkout -b refactor/html-first-compiler-revised
```

## 2. Read first

```text
README.md
CLAUDE.md
agentic/orchestration/workflow-map.md
agentic/orchestration/sop.md
knowledge-base/client-first-class-map.json
```

## 3. Execute tasks in order

### Task A — Archive cleanup
Follow `02_PHASE_0_ARCHIVE_CLEANUP_STABILIZATION.md`.

### Task B — Structure/contracts
Follow `03_PHASE_1_REPO_STRUCTURE_CONTRACTS.md`.

### Task C — CSS Library Contract
Follow `04_PHASE_2_CLIENT_FIRST_LIBRARY_CONTRACT.md`.

Run:

```bash
python scripts/index_css_library.py
python scripts/gates/validate_css_contract.py
```

### Task D — Figma Extraction Contract
Follow `05_PHASE_3_FIGMA_MCP_EXTRACTION_CONTRACT.md`.

### Task E — Design-System Sync
Follow `06_PHASE_4_DESIGN_SYSTEM_SYNC_STRICT_MODE.md`.

### Task F — Component Registry + Signatures
Follow `07_PHASE_5_COMPONENT_REGISTRY_SIGNATURE_SYNC.md`.

### Task G — Figma Normalizer
Follow `08_PHASE_6_FIGMA_NORMALIZATION_MESSY_RECOVERY.md`.

### Task H — Semantic IR + Resolver
Follow `09_PHASE_7_SEMANTIC_IR_TAG_CLASS_RESOLUTION.md`.

### Task I — HTML Blueprint + QA
Follow `10_PHASE_8_HTML_BLUEPRINT_RENDER_QA.md`.

### Task J — Asset/Alt
Follow `11_PHASE_9_ASSET_ALT_POLICY_MANIFEST.md`.

### Task K — Chunks + Fixtures
Follow `12_PHASE_10_CHUNK_SLICING_GOLDEN_FIXTURES.md`.

### Task L — Webflow Native Plan
Follow `13_PHASE_11_WEBFLOW_NATIVE_OPS_BRANCH_AUDIT.md`.

### Task M — Docs/Prompts
Follow `14_PHASE_12_RUNTIME_DOCS_PROMPTS_UPDATE.md`.

### Task N — Gates/Evals
Follow `15_PHASE_13_GATES_EVALS_ACCEPTANCE.md`.

## 4. Progress report format

```text
Stage:
Done:
Evidence:
Blockers:
Next:
```

## 5. Blocker format

```text
BLOCKER
What failed:
Tried:
Evidence:
Why it matters:
Need decision:
```

## 6. Final PR summary

```text
Summary:
- Converted repo plan/docs/contracts toward HTML-first compiler.
- Added CSS contract layer.
- Added Figma extraction/normalization contracts.
- Added component signature matching.
- Added HTML QA, asset, chunk, native plan gates.

No Webflow writes were performed.

Validation:
- ...
```
