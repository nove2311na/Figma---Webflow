# 02 — Phase 0: Archive Cleanup & System Stabilization

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## 1. Bối cảnh

Repo hiện có artifact/script của run cũ và workflow cũ. Nếu để trong core, intern/Claude Code dễ chạy nhầm pipeline cũ.

Mục tiêu phase này:
- Move file thừa/sai phase vào `archive/`;
- Không xoá;
- Sửa mọi reference active;
- Đảm bảo không command nào còn gọi script cũ.

## 2. Tạo archive structure

Create:

```text
archive/
  README.md
  MIGRATION_LOG.md
  runs/
    saas-futuristic-app/
      final-report.md
      scripts/
  site-libraries/
  deprecated-workflows/
  old-blueprint-flow/
```

`archive/README.md`:

```md
# Archive

Historical artifacts and deprecated workflows.
Files here are not active runtime instructions.
Do not import archived scripts from active code.
Do not use archived Webflow site/page IDs as defaults.
```

`archive/MIGRATION_LOG.md`:

```md
# Migration Log

## YYYY-MM-DD — HTML-first refactor
Moved run-specific artifacts and deprecated Webflow-first workflow files out of active runtime.
```

## 3. Move files

| Current path | New path | Action after move |
|---|---|---|
| `agentic/memory/final-report-saas-futuristic-app.md` | `archive/runs/saas-futuristic-app/final-report.md` | Update docs reference to archive path only. |
| `scripts/phase2a_reconcile_library.py` | `archive/runs/saas-futuristic-app/scripts/phase2a_reconcile_library.py` | Replace with `scripts/index_css_library.py`. |
| `scripts/phase2b_synthesize_logs.py` | `archive/runs/saas-futuristic-app/scripts/phase2b_synthesize_logs.py` | Remove from active workflow. |
| `scripts/phase3_fix_library.py` | `archive/runs/saas-futuristic-app/scripts/phase3_fix_library.py` | Replace with strict missing report/manual library update. |
| `scripts/phase3_fix_tokenmap.py` | `archive/runs/saas-futuristic-app/scripts/phase3_fix_tokenmap.py` | Replace with `validate_design_system_sync.py`. |
| `scripts/run_all_gates.py` | `archive/runs/saas-futuristic-app/scripts/run_all_gates.py` | Replace with `run_quality_gate.py --profile html-first`. |
| `knowledge-base/libraries/6920a7d45c61690dd10ac690/` | `archive/site-libraries/6920a7d45c61690dd10ac690/` | Remove hardcoded active references. |
| `knowledge-base/libraries/6a1fa213c04827556dcac7b5/` | `archive/site-libraries/6a1fa213c04827556dcac7b5/` | Remove hardcoded active references. |
| `agentic/prompts/write-html-contract.md` | `archive/deprecated-workflows/write-html-contract.webflow-first.md` | Replace with split prompts in later phases. |

## 4. Search references after move

Run:

```bash
grep -R "final-report-saas-futuristic-app" -n . --exclude-dir=.git --exclude-dir=archive
grep -R "phase2a_reconcile_library" -n . --exclude-dir=.git --exclude-dir=archive
grep -R "phase2b_synthesize_logs" -n . --exclude-dir=.git --exclude-dir=archive
grep -R "phase3_fix_library" -n . --exclude-dir=.git --exclude-dir=archive
grep -R "phase3_fix_tokenmap" -n . --exclude-dir=.git --exclude-dir=archive
grep -R "run_all_gates" -n . --exclude-dir=.git --exclude-dir=archive
grep -R "6920a7d45c61690dd10ac690" -n . --exclude-dir=.git --exclude-dir=archive
grep -R "6a1fa213c04827556dcac7b5" -n . --exclude-dir=.git --exclude-dir=archive
grep -R "write-html-contract" -n . --exclude-dir=.git --exclude-dir=archive
```

Expected:
- no active command references old scripts;
- old Webflow IDs only appear in archive or docs explaining historical examples.

## 5. Do not move yet

Keep active:

```text
agentic/evals/
agentic/memory/session-handoff.md
agentic/memory/team-memory.md
knowledge-base/client-first-class-map.json
knowledge-base/client-first-theory.md
scripts/archive_workspace.py
scripts/init_workspace.py
scripts/restore_workspace.py
scripts/gates/scan_secrets.py
scripts/gates/validate_relative_paths.py
tools/library_resolver.py
tools/utils.py
```

Reason:
- These are still useful after update.
- `client-first-class-map.json` becomes curated interpretation layer, not source of truth.
- Evals will be updated, not archived.

## 6. Create gate

Create:

```text
scripts/gates/validate_archive_cleanup.py
```

Checks:
```text
[ ] archive/README.md exists.
[ ] archive/MIGRATION_LOG.md exists.
[ ] old paths no longer exist.
[ ] moved files exist under archive.
[ ] active repo no longer references old script names.
[ ] active repo no longer references old site IDs except archive.
[ ] README/CLAUDE no longer instruct old blueprint-first commands.
```

## 7. Done checklist

```text
[ ] Archive folders created.
[ ] Old run files moved.
[ ] Old scripts moved.
[ ] Old site libraries moved.
[ ] Old broad prompt archived.
[ ] Active references updated.
[ ] validate_archive_cleanup.py passes.
```
