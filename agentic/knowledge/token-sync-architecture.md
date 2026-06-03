# Token Sync Architecture

Tài liệu này giải thích cơ chế đồng bộ design token giữa **Figma → Repo → Webflow**
và những điều kiện bắt buộc để pipeline MAS hoạt động deterministic.

---

## Nguyên tắc cốt lõi

> **Class definition = immutable. Token value = payload duy nhất cần sync.**

```
class text-weight-bold  →  var --font-weight--bold  →  value (project A: 700, project B: 900)
       (không đổi)               (key cố định)              (thay đổi theo dự án/thiết kế)
```

`text-weight-bold` không bao giờ đổi tên hay nghĩa.
Cái thay đổi là **giá trị của variable** đứng sau nó.
LLM không đoán "bold là bao nhiêu" — nó đọc value từ token catalog.

---

## Kiến trúc 3-way ledger

```
┌─────────────────┐      read       ┌──────────────────┐      push       ┌─────────────────┐
│  Figma Project  │ ─────────────►  │   Repo Library   │ ─────────────►  │ Webflow Project │
│  (design SoT)   │                 │ (git-versioned)  │                 │ (build target)  │
│                 │                 │                  │                 │                 │
│ Variables panel │                 │ libraries/       │                 │ Variables panel │
│ - Base tokens   │ ◄─── drift? ──► │ {site_id}/       │ ◄─── drift? ──► │ - same tokens   │
│ - Theme aliases │                 │ library.json     │                 │ - applied live  │
└─────────────────┘                 │ token-map.json   │                 └─────────────────┘
                                    │ changelog.json   │
                                    └──────────────────┘
```

**Figma** = nơi designer định nghĩa token value.
**Repo** = ledger trung gian, git-versioned, là nguồn sự thật cho agent build.
**Webflow** = đích build, nhận value từ repo qua `variable_tool`.

Mỗi lần sync tạo 1 entry trong `changelog.json` — đây là audit trail.

---

## Token là "hợp đồng" giữa designer và LLM

| | Figma | Repo | Webflow |
|---|---|---|---|
| **Key (cố định)** | `Font Weight/bold` | `figma-token-map.json` mapping | `--font-weight--bold` |
| **Value (sync được)** | 700 | `client-first-library.json` | variable value |

Designer đổi `Font Weight/bold` từ 700 → 900 ở Figma
→ `update_library_from_figma.py` cập nhật repo
→ `sync_library_to_webflow.py` push lên Webflow variable
→ **class `text-weight-bold` không cần đổi một chữ.**

---

## Điều kiện sống còn: designer BẮT BUỘC dùng Figma Variables

Đây là điều kiện kỹ thuật, không phải khuyến nghị.

| Designer làm | Kết quả pipeline |
|---|---|
| Dùng Variable cho color, spacing, typography | Token có thể sync → LLM deterministic |
| Hardcode raw value (vd: `font-weight: 700` trực tiếp) | Không có token để sync → LLM phải đoán → vỡ |

**Pre-flight gate** tại bước ingest:
- Phát hiện Figma node có raw value không backed-by-variable
- Flag: `untokenized_property` → chặn pipeline hoặc yêu cầu designer fix trước
- Không có cách tự động giải quyết case này — chỉ có kỷ luật đầu vào

---

## Vị trí trong pipeline MAS

```
Step 1  sync-library     ← TOKEN SYNC (đây)
          │ Figma vars → repo → Webflow vars + drift gate + untokenized gate
          │
Step 2  sync-components  ← component structure map (de_component_tool)
          │
Step 3  read + html      ← read-figma-data.md → archive/deprecated-workflows/write-html-contract.webflow-first.md
          │
Step 4  split sections   ← section boundary detection
          │
Step 5  subagents build  ← parallel-section-build (apply-only)
```

Step 1 là nền. Nếu token-layer chuẩn, steps 3–5 hoàn toàn deterministic.

---

## Scripts hiện có

| Script | Việc làm |
|---|---|
| `scripts/update_library_from_figma.py` | Figma MCP → repo library (step: Figma→Repo) |
| `scripts/sync_library_to_webflow.py` | Repo → Webflow variable_tool (step: Repo→Webflow) |
| `tools/library_resolver.py` | Load/register/scaffold library dir, update last-synced |
| `scripts/gates/validate_project_library.py` | Gate: validate library JSON, class←→token coverage |

**Còn thiếu (v0.7.0 candidates):**
- `scripts/detect_token_drift.py` — so sánh 3-way (Figma ↔ repo ↔ Webflow), tạo reconciliation report
- `scripts/gates/validate_tokens_in_figma.py` — gate phát hiện untokenized property trong raw Figma data

---

## Hướng dẫn ngắn cho từng bên

### Designer (Figma side)
- **Luôn dùng Variables** cho mọi color, spacing, typography, border — kể cả prototype
- Đặt tên variable theo pattern đã có: `Font Weight/bold`, `Spacing/medium`, `Colors/Theme/Text Color/primary`
- Không apply raw hex hoặc raw number trực tiếp lên element nếu nó sẽ xuất hiện trong component build
- Nếu muốn thêm token mới → thêm vào Figma Variable collection trước, đặt tên rõ ràng, rồi báo operator sync

### Operator / Developer (repo side)
1. Sau khi designer update token ở Figma → chạy `update_library_from_figma.py` để pull về repo
2. Review `changelog.json` diff — confirm intentional changes
3. Chạy `validate_project_library.py` để đảm bảo không có class mồ côi
4. Chạy `sync_library_to_webflow.py` để push lên Webflow variable
5. Commit repo

### LLM / Agent (build side)
- Trước khi viết HTML contract → đọc `knowledge-base/libraries/{site_id}/client-first-library.json`
- Mọi color đều phải trace về token class (`text-color-primary`) — không hardcode hex
- Mọi spacing đều pick token (`margin-medium`, `gap-large`) — không compute px/16
- Nếu Figma node có raw value không có token → `flag: untokenized` trong design analysis, STOP

---

## Source files tham khảo

| File | Nội dung |
|---|---|
| `knowledge-base/client-first-class-map.json` | Global utility class catalog (v0.5.0, synced từ CF V2.2) |
| `knowledge-base/libraries/{site_id}/client-first-library.json` | Per-project variable-backed class values |
| `knowledge-base/libraries/{site_id}/figma-token-map.json` | Figma variable path → CF class + cssName |
| `agentic/specs/figma-to-client-first-mapping.md` | Quy tắc map Figma node → CF class (Sections A–G) |
| `agentic/prompts/read-figma-data.md` | Pre-analysis prompt, bao gồm color token catalog validation |
| `agentic/prompts/generate-cf-library.md` | LLM prompt tạo/update library từ Figma MCP |
