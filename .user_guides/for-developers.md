# Hướng dẫn cho Developer / Operator

Bạn là người **vận hành pipeline**, chạy scripts, quản lý repo, và là cầu nối giữa Designer và AI.

---

## Tổng quan công việc của bạn

```
Designer update Figma  →  bạn sync token  →  bạn kick off build  →  AI build Webflow
                          (scripts/)          (Claude Code)          (agents)
```

Bạn không viết HTML hay CSS. Bạn:
1. Kiểm soát chất lượng đầu vào (Figma file đúng chuẩn chưa?)
2. Đồng bộ token library từ Figma → repo → Webflow
3. Khởi tạo workspace và kick off pipeline
4. Phê duyệt blueprint trước khi AI build lên Webflow (bắt buộc)
5. Chạy gates để verify output

---

## Khởi tạo project mới

```cmd
python scripts\init_workspace.py --project "Tên Dự Án" --figma "https://figma.com/design/..." --webflow-site-id "site_abc123"
```

Lệnh này:
- Tạo `workspace/meta.json` với project info
- Scaffold `knowledge-base/libraries/{site_id}/`
- Register project vào `knowledge-base/libraries/registry.json`

---

## Sync token library (sau khi Designer update Figma)

```cmd
python scripts\update_library_from_figma.py  # in hướng dẫn Figma MCP → repo
python scripts\gates\validate_project_library.py --site-id <id> --target .
python scripts\sync_library_to_webflow.py     # in payloads Webflow MCP
```

Sau khi sync → commit repo để có audit trail.

---

## Kick off build (Claude Code)

```
@pm build trang home cho dự án [tên], Figma: [link], Webflow site: [site_id]
```

PM agent sẽ orchestrate toàn bộ. Bạn chỉ cần:
- Chờ agent dừng ở **Blueprint approval gate**
- Review blueprint (`workspace/blueprints/*.json`) — class names, HTML structure, new classes
- Approve: "approved" → agent tiếp tục build lên Webflow

---

## Gates — chạy bất kỳ lúc nào

```cmd
python scripts\gates\validate_agentic_structure.py --target .   # 39/39 paths phải pass
python scripts\gates\run_quality_gate.py --target .              # full suite
python scripts\gates\scan_secrets.py --target .                  # không có secret trong repo
python scripts\gates\validate_build_contract.py --site-id <id>  # blueprint hợp lệ
```

Gate fail → đừng build. Fix trước.

---

## Files bạn cần biết

| File | Việc |
|---|---|
| `workspace/meta.json` | Project metadata (site_id, figma file_id) |
| `workspace/state.json` | Trạng thái hiện tại của pipeline |
| `workspace/blueprints/` | Blueprint JSON (class names, HTML contract) |
| `workspace/rawdata/` | Figma raw data đã extract |
| `workspace/error-logs.json` | Lỗi từ agent |
| `knowledge-base/libraries/{site_id}/` | Token library của project |
| `knowledge-base/libraries/{site_id}/changelog.json` | Audit trail mỗi lần sync token |

---

## Approval gates — KHÔNG được bỏ qua

Pipeline MAS có 2 hard stops yêu cầu bạn approve:

1. **Trước Phase 1 → Phase 2**: Xem xét và approve blueprint trước khi AI build lên Webflow
2. **Trước publish**: PM sẽ hỏi confirm trước khi publish site

Không approve = không build. Đây là cơ chế safety.

---

## Khi Designer thêm token mới

1. Designer báo: "Tôi thêm token `Spacing/brand-gap = 2.5rem`"
2. Bạn chạy sync pipeline (xem mục "Sync token library" ở trên)
3. Verify trong `changelog.json` có entry mới
4. Verify trong Webflow Designer có variable mới
5. Báo Designer OK rồi design tiếp

---

## Xử lý "untokenized property" (Designer quên dùng variable)

Agent sẽ báo: `flag: untokenized` trong design analysis.
Ý nghĩa: Figma node có raw value không backed-by-variable.

Việc của bạn:
1. Báo Designer fix (apply variable đúng cho node đó)
2. HOẶC quyết định tạo custom class (nếu value đó intentionally one-off)
3. Không cho agent tiếp tục cho đến khi quyết định xong

---

## Không được làm gì

- Không chỉnh sửa `knowledge-base/client-first-theory.md` (sacred)
- Không chỉnh sửa `scripts/gates/validate_client_first_library.py` (sacred)
- Không commit file `.env` hay secret
- Không push Webflow live khi chưa approve blueprint
- Không xóa `workspace/` khi đang có build đang chạy

---

## Kiến trúc tóm tắt để debug

Khi có lỗi, kiểm tra theo thứ tự:

```
1. workspace/error-logs.json          → lỗi gì?
2. workspace/state.json               → pipeline đang ở phase nào?
3. .claude/skills/_shared/scripts/run_quality_gate.py  → gate nào fail?
4. knowledge-base/libraries/{id}/     → library đúng không?
5. .claude/skills/figma-to-webflow-orchestrator/SKILL.mdsop.md       → SOP phase yêu cầu gì?
```
