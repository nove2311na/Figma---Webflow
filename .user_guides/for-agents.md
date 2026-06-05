# Hướng dẫn cho AI Agent / LLM

Bạn là AI agent đang thực thi task trong repo này.
Đọc file này trước khi làm bất cứ điều gì.

---

## Repo này làm gì?

Pipeline **Figma → Webflow** tự động theo chuẩn Finsweet Client-First V2.
- Bạn đọc Figma data → phân tích → viết HTML contract → build Webflow (native element ops)
- Không bao giờ dùng `whtml_builder`. HTML là intermediate contract, không phải push payload.
- Mọi Webflow write cần approval từ user trước khi thực thi.

---

## Pre-flight: đọc những file này TRƯỚC KHI bắt đầu bất kỳ task nào

```
1. agentic/memory/README.md                    ← trạng thái session trước & invariants
2. agentic/policies/validation-gates.md        ← SOP phase & validation gates
3. workspace/meta.json                         ← project + site ID
4. workspace/state.json                        ← pipeline đang ở đâu
5. agentic/knowledge/libraries/{site_id}/      ← token library của project
6. agentic/knowledge/client-first-class-map.json  ← global CF class catalog
```

Không đọc pre-flight → không bắt đầu task.

---

## Vai trò agents và khi nào dùng

| Agent | Trigger |
|---|---|
| `@pm` | User request mới, orchestration, approval gate, session handoff |
| `@client-first-architect` | Phase 1: viết blueprint + HTML contract + QA loop |
| `@figma-webflow-operator` | Phase 2A: extract Figma, create classes, create section containers |
| `@section-builder` | Phase 2B: build 1 section (apply-only, KHÔNG tạo class) |
| `@qa-gatekeeper` | Phase 3: QA, gate checks, readiness report |
| `@workspace-steward` | Archive, restore, validate workspace integrity |

---

## Quy trình chuẩn (SOP)

```
Phase 0  Intake     → PM đọc request, load context, check state
Phase 1  Blueprint  → Architect đọc Figma → design analysis → HTML contract → blueprint → STOP for user approval
Phase 2A Setup      → Operator tạo classes trên Webflow + tạo section containers → ghi parent_element_id
Phase 2B Build      → Section-builder subagents build song song (apply-only)
Phase 3  QA         → Architect QA vs Figma + blueprint → APPROVED hoặc FIX loop
Phase 4  Handoff    → PM update session-handoff.md, báo cáo evidence
```

Hard stops bắt buộc:
- Sau Phase 1: PHẢI dừng, trình blueprint, chờ user approve
- Trước mọi Webflow write: confirm site_id + page_id với user

---

## HTML Contract — quy tắc quan trọng nhất

> HTML contract = naming authority. Class names được quyết định một lần, serially, bởi architect.
> Subagents chỉ APPLY classes đã có — không bao giờ tạo class mới.

Khi viết HTML contract:
1. Đọc `.claude/skills/figma-to-html-architect/SKILL.md` → tạo design analysis JSON trước
2. Mọi class phải trace về: CF library class HOẶC entry trong `new_classes` với Case 1-5

---

## Client-First V2.2 — những điều hay bị nhầm

| Sai | Đúng |
|---|---|
| "CF không có layout utility, mọi flex/grid = custom class" | CF V2.2 CÓ: `flex-horizontal`, `flex-vertical`, `gap-*`, `grid-N-col`, `grid-autofit-*` |
| "Tính rem = px/16" | Dùng token-snap: pick token gần nhất (`Spacing/medium = 2rem`), apply utility class |
| "Case 4 = cần custom class cho mọi breakpoint" | Variable modes tự handle spacing/type responsive. Case 4 chỉ cho structural reflow |
| `aspect-ratio-portrait = 3/4` | Thực tế = **2/3**. `landscape = 3/2`. Tất cả có `object-fit:cover` |
| `text-size-huge` tồn tại | Không tồn tại. Scale: tiny/small/regular/medium/large |
| `is-brand`, `is-outline` là CF combos | CF V2.2 chỉ có `is-secondary` và `is-text` cho button |

---

## Forbidden actions (không bao giờ được làm)

- `whtml_builder` — FORBIDDEN
- Edit `agentic/knowledge/client-first/INDEX.yaml`
- Edit `.claude/skills/_shared/scripts/validate_css_contract.py`
- Edit `agentic/schemas/library/client-first-library.schema.json`
- Edit bất kỳ file nào trong `workspace/` trừ khi được authorize rõ ràng
- Tạo class mới trong Webflow khi đang ở role `section-builder` (apply-only)
- Push/publish lên Webflow chưa có approval
- Hardcode hex color — luôn dùng library token class
- Commit file `.env` hay secret

---

## Khi gặp ambiguity hoặc missing data

Thứ tự xử lý:
1. Kiểm tra `workspace/error-logs.json` xem đã có error chưa
2. Kiểm tra `agentic/rules/retry-policy.yaml` — có retry được không?
3. Nếu vẫn blocked → STOP, escalate lên PM, log blocker vào `error-logs.json`
4. Không tự đoán khi bị thiếu Figma data, thiếu page ID, thiếu token

---

## Token là hợp đồng — không đoán

```
Figma variable "Font Weight/bold"  →  CF class text-weight-bold  →  Webflow var --font-weight--bold
```

Nếu Figma node có raw value không backed-by-variable → ghi `untokenized: true` trong design analysis → STOP → báo PM.

Không tự assign class cho raw value.

---

## Evidence trước báo cáo

Không báo cáo "xong" khi chưa có evidence:
- Phase 1: blueprint JSON tồn tại trong `workspace/blueprints/`
- Phase 2A: `parent_element_id` đã ghi vào `workspace/state.json`
- Phase 2B: action log tồn tại trong `workspace/sections/[id]_action_log.json`
- Phase 3: QA report với verdict APPROVED tồn tại
- Mọi phase: gates pass trước khi report done

---

## Files quan trọng nhất để làm việc

| Mục đích | File |
|---|---|
| CF class catalog | `agentic/knowledge/client-first-class-map.json` |
| Project token library | `agentic/knowledge/libraries/{site_id}/client-first-library.json` |
| Token → Figma map | `agentic/knowledge/libraries/{site_id}/figma-token-map.json` |
| Figma analysis prompt | `.claude/skills/figma-to-html-architect/SKILL.md` |
| Figma→CF mapping rules | `agentic/specs/contracts/figma-to-client-first-mapping.md` |
| Token sync architecture | `agentic/knowledge/token-sync-architecture.md` |
| Approval gate rules | `agentic/policies/approval-gates.md` |
| MCP capabilities | `agentic/rules/webflow-mcp.rules.yaml` |
