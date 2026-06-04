# Guides — Onboarding cho mọi bên liên quan

Folder này dành cho **bất kỳ ai** lần đầu tiếp cận repo này.
Đọc file phù hợp với vai trò của bạn — không cần đọc toàn bộ repo.

## Repo này làm gì?

Chuyển đổi **Figma design → Webflow page** tự động bằng AI agent,
tuân thủ chuẩn **Finsweet Client-First V2** — chuẩn CSS/naming phổ biến nhất cho Webflow.

```
Figma design
    ↓  (AI đọc, phân tích, map token)
HTML contract  ←  naming authority (tên class quyết định ở đây, 1 lần, không race condition)
    ↓  (AI build song song từng section)
Webflow live page
```

## Đọc file nào?

| Bạn là | File cần đọc |
|---|---|
| **Designer** — làm việc trên Figma | [`for-designers.md`](./for-designers.md) |
| **Developer / Operator** — chạy pipeline, quản lý repo | [`for-developers.md`](./for-developers.md) |
| **LLM / AI Agent** — thực thi task trong repo này | [`for-agents.md`](./for-agents.md) |

## Setup môi trường

| Việc | File |
|---|---|
| Cài Webflow + Figma MCP cho 1 repo (Claude Code) — gồm audit trạng thái repo này, fast-path lặp lại cho repo khác, troubleshooting, caveats | [`setup-mcp-webflow-figma.md`](./setup-mcp-webflow-figma.md) |

## Sơ đồ hệ sinh thái

```
FIGMA (design source)
  └── Variables (token) ──────────────────────────────────┐
  └── Components / Frames                                 │
                                                          ▼
REPO (trung gian, git-versioned)                    TOKEN SYNC
  ├── knowledge-base/       ← CF class catalog       (scripts/)
  │   └── libraries/{id}/  ← per-project token library
  ├── workspace/            ← live project state (rawdata, blueprints)
  ├── agentic/              ← agent rules, prompts, specs, schemas
  └── scripts/gates/        ← quality gates (CI-like checks)
                                                          │
WEBFLOW (build target)                                    │
  └── Variables panel  ◄─────────────────────────────────┘
  └── Pages / Elements ← agent build (apply-only, MCP-352)
```

## Kiến trúc tài liệu

| Thư mục | Nội dung |
|---|---|
| `guides/` | Onboarding cho người đọc (bạn đang ở đây) |
| `agentic/knowledge/` | Kiến thức kỹ thuật nền: token sync, CF library, Webflow MCP |
| `agentic/specs/` | Spec chi tiết: mapping rules, schemas, QA contract |
| `.claude/skills/figma-to-webflow-orchestrator/SKILL.md` | Prompt guide cho LLM: phân tích Figma, viết HTML contract |
| `.claude/skills/figma-to-webflow-orchestrator/SKILL.md` | SOP, phase state machine, handoff contracts |
| `.claude/agents/` | Định nghĩa vai trò từng AI agent |
| `.claude/skills/` | Workflow skills: blueprint, build, QA, parallel sections |
