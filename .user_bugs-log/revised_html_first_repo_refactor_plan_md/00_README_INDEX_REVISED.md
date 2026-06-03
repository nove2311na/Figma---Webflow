# Revised HTML-first Figma → Webflow Repo Refactor Plan — Index

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## 1. Mục tiêu bản plan revised

Bản plan này thay thế/upgrade bộ plan trước bằng các phát hiện từ research:

- CSS thật của FS Client-First phải được parse thành **Library Contract** bắt buộc.
- Figma MCP extraction phải tách thành phase riêng, tạo **Figma Node Bundle** ổn định.
- Figma messy phải qua **Normalizer** trước Semantic IR.
- Component phải có **Registry + Signature Matcher**, không chỉ match theo tên.
- HTML phải pass local gates trước khi slice chunk và compile Webflow native plan.
- Webflow write phải branch-first, audit-logged, approval-gated, serialized by default.

## 2. Target pipeline

```text
Figma MCP + Client-First/Webflow CSS
→ Client-First Library Contract
→ Figma Extraction Bundle
→ Design-System Sync
→ Component Registry + Signature Sync
→ Figma Normalized Tree
→ Semantic IR
→ Tag Resolver
→ Class Resolver
→ HTML Blueprint
→ Local HTML + QA
→ Asset/Alt Manifest
→ Section Chunks
→ Golden Fixtures / Benchmarks
→ Webflow Native Build Plan
→ Approval
→ Webflow Branch Native Ops
→ Webflow QA + Audit
```

## 3. Phase files

| Phase | File | Mục tiêu |
|---|---|---|
| 0 | `02_PHASE_0_ARCHIVE_CLEANUP_STABILIZATION.md` | Move file thừa/sai phase sang archive, sửa reference để repo không gãy. |
| 1 | `03_PHASE_1_REPO_STRUCTURE_CONTRACTS.md` | Tạo specs/rules/schemas/workspace mới. |
| 2 | `04_PHASE_2_CLIENT_FIRST_LIBRARY_CONTRACT.md` | Parse CSS thật thành contract bắt buộc. |
| 3 | `05_PHASE_3_FIGMA_MCP_EXTRACTION_CONTRACT.md` | Chuẩn hóa Figma MCP extraction thành node bundle. |
| 4 | `06_PHASE_4_DESIGN_SYSTEM_SYNC_STRICT_MODE.md` | So Figma variable/style với CSS contract. |
| 5 | `07_PHASE_5_COMPONENT_REGISTRY_SIGNATURE_SYNC.md` | Registry + signature matching cho component. |
| 6 | `08_PHASE_6_FIGMA_NORMALIZATION_MESSY_RECOVERY.md` | Normalize Figma messy trước Semantic IR. |
| 7 | `09_PHASE_7_SEMANTIC_IR_TAG_CLASS_RESOLUTION.md` | Semantic IR, tag resolver, class resolver strict mode. |
| 8 | `10_PHASE_8_HTML_BLUEPRINT_RENDER_QA.md` | HTML Blueprint → local HTML → QA gates. |
| 9 | `11_PHASE_9_ASSET_ALT_POLICY_MANIFEST.md` | Asset manifest + alt policy. |
| 10 | `12_PHASE_10_CHUNK_SLICING_GOLDEN_FIXTURES.md` | Chunk slicing + fixtures/benchmarks. |
| 11 | `13_PHASE_11_WEBFLOW_NATIVE_OPS_BRANCH_AUDIT.md` | Native build plan + branch/audit/retry. |
| 12 | `14_PHASE_12_RUNTIME_DOCS_PROMPTS_UPDATE.md` | Update README/CLAUDE/SOP/prompts. |
| 13 | `15_PHASE_13_GATES_EVALS_ACCEPTANCE.md` | Gates/evals/final acceptance. |

Extra:
- `01_DECISION_SUMMARY_FROM_RESEARCH.md`
- `16_FILE_MOVE_AND_REFERENCE_STABILIZATION_MATRIX.md`
- `17_INTERN_RUNBOOK_STEP_BY_STEP.md`
- `18_CLAUDE_CODE_EXECUTION_PROMPT.md`

## 4. Non-negotiable rules

1. Không build trực tiếp từ raw Figma lên Webflow.
2. Không dùng `whtml_builder`.
3. Không inline style.
4. Không hardcode hex/px nếu class/token đã tồn tại.
5. Không dùng class research/example nếu chưa có trong `client-first-library-contract.json`.
6. Missing class/token/style/component trong strict mode = blocker.
7. Mọi section/component cần `data-section`, `data-component`, `data-figma-node`.
8. Webflow write chỉ sau approved local HTML + approved native build plan.
9. Webflow write mặc định serialized, branch-first, audit logged.
10. Publish không thuộc import pipeline.

## 5. Definition of Done

Repo revised đạt khi tạo/validate được:

```text
knowledge-base/generated/client-first-library-contract.json
knowledge-base/generated/css-variable-index.json
knowledge-base/generated/css-class-index.json
knowledge-base/generated/css-selector-index.json
knowledge-base/generated/css-property-value-index.json
knowledge-base/generated/css-breakpoint-index.json
knowledge-base/generated/webflow-native-class-index.json

workspace/figma/figma.node-bundle.json
workspace/figma/figma.normalized-tree.json
workspace/reports/design-system-sync-report.json
workspace/reports/component-sync-report.json
workspace/reports/component-match-report.json
workspace/semantic/figma.semantic-tree.json
workspace/html/page.blueprint.json
workspace/html/page.html
workspace/html/asset-manifest.json
workspace/html/chunks/section-manifest.json
workspace/webflow-native/native-build-plan.json
workspace/webflow-native/write-audit-log.jsonl
```
