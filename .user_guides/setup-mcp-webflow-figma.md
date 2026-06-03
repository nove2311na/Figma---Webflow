# Setup MCP — Webflow + Figma cho Claude Code

Hướng dẫn cài 2 MCP server (Webflow + Figma) cho 1 repo. Local-only, không global. Tested trên Windows 11 + Git Bash + Node v22.20 + Claude Code v2.1.161 + custom `ANTHROPIC_BASE_URL` proxy.

> Đọc nhanh: nếu bạn chỉ muốn lặp lại setup cho repo khác → nhảy thẳng [Section B](#b--cài-cho-repo-mới-fast-path).

---

## A — Trạng thái hiện tại của repo này (audit)

Repo `MAS-Figma-Webflow-khang` đã setup xong 2 MCP server. Tóm tắt:

### MCP server đang dùng

| Tên | Transport | Endpoint | Mục đích |
|---|---|---|---|
| `webflow` | HTTP (streamable) | `https://mcp.webflow.com/mcp` | Đọc/sửa Webflow sites, collections, pages |
| `figma-desktop` | HTTP | `http://127.0.0.1:3845/mcp` | Đọc Figma design từ desktop Dev Mode |

### Scope đang dùng

Cả 2 scope đều có entry (vì quá trình setup chạy fallback):

| Scope | Nơi lưu | Share với team | Trạng thái |
|---|---|---|---|
| **Project** | `<repo>/.mcp.json` | Có (commit git) | Active |
| **Local** | `~/.claude.json` → `projects[<repo-path>].mcpServers` | Không | Active (precedence cao hơn) |

> ⚠️ Có duplicate warning khi chạy `claude mcp list`. Không ảnh hưởng chức năng. Muốn dọn → xóa scope nào không cần (xem [Section D](#d--troubleshooting)).

### File đã touch (audit trail)

| File | Action | Note |
|---|---|---|
| `<repo>/.mcp.json` | Created | Project-scope config, commit được vào git |
| `~/.claude.json` | Modified (jq patch x2) | Set `enabledMcpjsonServers` + `hasTrustDialogAccepted` + `enableAllProjectMcpServers` cho 2 path variants (Windows `\\` + Unix `/`) |
| `~/.claude.json` | Modified (`claude mcp add --scope local`) | Local-scope entries cho cả webflow + figma-desktop |
| `~/.claude.json.bak.20260603_123037` | Created | Backup pre-jq (62.4K). Giữ để rollback nếu cần |

---

## B — Cài cho repo mới (fast path)

**Time**: ~5 phút. **Prereq**: Node ≥ 22.3, Figma desktop app, account Webflow.

### Bước 1 — Mở Figma desktop + bật Dev Mode MCP

1. Mở **Figma desktop app** (không phải browser)
2. Mở 1 file Design bất kỳ
3. Click canvas trống (deselect tất cả)
4. Toolbar trên cùng → toggle **Dev Mode** (icon `</>`)
5. Right sidebar → bật **MCP server**
6. Đợi message: "server is enabled and running"

> Giữ Figma desktop chạy suốt phiên làm việc. Tắt Figma = MCP figma-desktop chết.

### Bước 2 — Add 2 MCP server (từ root repo)

```bash
cd /path/to/your/new/repo

# Webflow — HTTP streamable (OAuth handled per-user)
# Endpoint: /mcp (KHÔNG dùng /sse — đã deprecated, trả 400)
claude mcp add --scope local --transport http webflow https://mcp.webflow.com/mcp

# Figma — direct HTTP đến desktop MCP server
claude mcp add --scope local --transport http figma-desktop http://127.0.0.1:3845/mcp
```

`--scope local` = lưu vào `~/.claude.json` cho repo hiện tại, KHÔNG global, KHÔNG cần trust prompt.

> ⚠️ **Đừng dùng SSE endpoint cũ** `https://mcp.webflow.com/sse`. Webflow đã chuyển sang HTTP streamable transport. Endpoint mới = `/mcp`. GitHub README của `webflow/mcp-server` chưa update — ignore. Doc chính thức ở [developers.webflow.com/mcp/installing/claude-code](https://developers.webflow.com/mcp/installing/claude-code).

### Bước 3 — Verify

```bash
claude mcp list
```

Mong đợi:
```
webflow:       https://mcp.webflow.com/mcp (HTTP) - ! Needs authentication
figma-desktop: http://127.0.0.1:3845/mcp (HTTP) - ✓ Connected
```

Nếu thấy như trên → setup đúng. `webflow` cần OAuth ở Bước 5.

### Bước 4 — Restart Claude Code

Nếu đang có session mở → `/exit`. Sau đó mở lại:
```bash
claude
```

> **Bắt buộc restart**. Session đang chạy không pickup MCP mới add.

### Bước 5 — Trigger Webflow OAuth

Trong session mới, gõ:
```
/mcp
```

UI hiện list MCP. Chọn `webflow` → action authenticate → browser tự mở trang Webflow OAuth → click **Authorize** → chọn sites cần grant access.

Token cache vào `~/.mcp-auth` (per-user, không vào repo).

Verify lại:
```bash
claude mcp list
```
`webflow` phải thành ✓ Connected.

### Bước 6 — Smoke test

Trong session:
```
list my Webflow sites
get current Figma selection
```

Cả 2 phải trả về data thật, không "tool not found".

---

## C — Optional: thêm `.mcp.json` để share với team

Bước B chỉ setup local. File config nằm trong `~/.claude.json` không vào git → teammate khác máy không có. Nếu muốn share:

### Tạo `.mcp.json` ở root repo

```json
{
  "mcpServers": {
    "webflow": {
      "type": "http",
      "url": "https://mcp.webflow.com/mcp"
    },
    "figma-desktop": {
      "type": "http",
      "url": "http://127.0.0.1:3845/mcp"
    }
  }
}
```

Commit file này. Teammate clone repo → `.mcp.json` tự được detect.

### Teammate phía mình cần làm

1. Mở Claude Code trong repo → có thể hiện **trust dialog** hỏi approve `.mcp.json`. Gõ `y`.
2. Nếu trust dialog KHÔNG hiện (xem [caveat về proxy](#e--known-caveats)) → fallback:
   ```bash
   claude mcp reset-project-choices
   claude   # relaunch → dialog hiện lại
   ```
3. Nếu vẫn không hiện → patch tay `~/.claude.json` (xem [Section D](#d--troubleshooting), mục "Trust prompt không hiện").

### Lưu ý duplicate

Nếu vừa có `.mcp.json` (project) vừa có entry trong `~/.claude.json` (local) cho cùng server → `claude mcp list` báo duplicate warning. Per docs, local thắng project. Muốn dọn → giữ 1 scope.

---

## D — Troubleshooting

### `/mcp` panel không hiện server vừa add

**Reason**: session đang chạy được launch trước khi add MCP.
**Fix**: `/exit` → `claude` lại.

### Trust prompt cho `.mcp.json` không hiện ở startup

**Reason**: `~/.claude.json` cache state `hasTrustDialogAccepted` đã true (từ session trước) hoặc bị block bởi custom proxy.

**Fix 1 — Reset (khuyến nghị thử trước)**:
```bash
claude mcp reset-project-choices
claude   # next launch sẽ re-prompt
```

**Fix 2 — Patch tay `~/.claude.json` qua jq**:

```bash
# Backup trước
cp ~/.claude.json ~/.claude.json.bak.$(date +%Y%m%d_%H%M%S)

# Patch — thay 2 path variant cho đúng repo của bạn
jq --arg p1 'C:\path\to\your\repo' \
   --arg p2 'C:/path/to/your/repo' \
   '.projects[$p1].enabledMcpjsonServers = ["webflow","figma-desktop"]
  | .projects[$p2].enabledMcpjsonServers = ["webflow","figma-desktop"]
  | .projects[$p1].hasTrustDialogAccepted = true
  | .projects[$p2].hasTrustDialogAccepted = true
  | .projects[$p1].enableAllProjectMcpServers = true
  | .projects[$p2].enableAllProjectMcpServers = true' \
   ~/.claude.json > ~/.claude.json.tmp && mv ~/.claude.json.tmp ~/.claude.json
```

> Note: Windows path trong Git Bash có thể tồn tại 2 variant (`\\` và `/`). Phải patch cả 2.

### `webflow` show `! Needs authentication` mãi

**Reason**: chưa hoàn tất OAuth flow.
**Fix**: trong session Claude Code → `/mcp` → chọn webflow → authenticate → browser. Nếu browser không tự mở → copy URL từ terminal paste tay.

### `webflow` báo `SSE error: Non-200 status code (400)` khi authenticate

**Reason**: dùng endpoint SSE cũ `https://mcp.webflow.com/sse` (đã deprecated). Webflow đã chuyển sang HTTP streamable.
**Fix**: remove + re-add với endpoint HTTP mới:
```bash
claude mcp remove webflow -s local
claude mcp remove webflow -s project   # nếu có
claude mcp add --scope local --transport http webflow https://mcp.webflow.com/mcp
```
Restart Claude → `/mcp` → webflow → authenticate lại.

### `webflow` OAuth loop / token corrupt

```bash
rm -rf ~/.mcp-auth
```
Restart Claude → re-auth.

### `figma-desktop` show `✘ failed` hoặc `Connection refused`

**Checklist**:
1. Figma desktop có đang mở không? (browser KHÔNG work)
2. Đã toggle Dev Mode chưa?
3. Right sidebar có bật MCP server chưa?
4. Có thấy message "server is enabled and running" chưa?
5. Test trực tiếp:
   ```bash
   curl -s http://127.0.0.1:3845/mcp -X POST -H "Content-Type: application/json" -d '{}' | head -5
   ```
   Nếu connection refused → Figma chưa expose port. Bật lại MCP toggle.

### Duplicate scope warning

`claude mcp list` báo:
```
Warning: Server "webflow" is defined in multiple scopes...
```

**Fix**: chọn 1 scope, remove cái còn lại:
```bash
# Giữ local, xóa project
claude mcp remove webflow -s project
claude mcp remove figma-desktop -s project

# HOẶC giữ project, xóa local
claude mcp remove webflow -s local
claude mcp remove figma-desktop -s local
```

### Node version lỗi với `mcp-remote`

Webflow MCP cần Node ≥ 22.3. Check:
```bash
node --version
```
Nếu thấp hơn → upgrade Node.

---

## E — Known caveats

### Custom `ANTHROPIC_BASE_URL` proxy

Nếu `.claude/settings.local.json` (hoặc env) set `ANTHROPIC_BASE_URL` về 3rd-party proxy (vd `api.minimax.io`):
- Trust dialog cho `.mcp.json` có thể KHÔNG hiện ở startup
- Tool Search bị disable mặc định (per docs)
- Claude.ai connectors không load
- **Workaround**: dùng local scope thay project scope (đã apply trong setup này). Nếu cần project scope → patch tay qua jq.

### Google Drive path với space

Path có "My Drive" (Google Drive sync) tạo 2 entry trong `~/.claude.json`:
- `G:\\My Drive\\...` (Windows backslash)
- `G:/My Drive/...` (Unix forward slash từ Git Bash)

Khi patch JSON → phải set field cho cả 2 entry. Lệnh jq trong [Section D](#d--troubleshooting) đã include 2 path variants.

### Local scope ≠ team-shared

Local scope (`~/.claude.json`) chỉ ở máy bạn. Teammate khác máy clone repo về KHÔNG có. Muốn share → dùng project scope (`.mcp.json`) ở [Section C](#c--optional-thêm-mcpjson-để-share-với-team).

### Mỗi project lưu OAuth token riêng theo endpoint

Per docs: "OAuth tokens are stored per endpoint". Nếu cùng `webflow` server đăng ký 2 endpoint khác nhau (vd SSE direct vs qua mcp-remote) → 2 OAuth token riêng. Tốn thời gian auth 2 lần.

---

## F — Tham khảo

- [Claude Code MCP docs](https://code.claude.com/docs/en/mcp)
- [Webflow MCP — Claude Code install (chính thức, dùng endpoint mới `/mcp`)](https://developers.webflow.com/mcp/installing/claude-code)
- [Webflow MCP overview](https://developers.webflow.com/mcp/reference/overview)
- [Webflow MCP server GitHub (README cũ, vẫn show endpoint `/sse` — ignore)](https://github.com/webflow/mcp-server)
- [Figma + Claude Code MCP setup](https://help.figma.com/hc/en-us/articles/39888612464151-Claude-Code-and-Figma-Set-up-the-MCP-server)
