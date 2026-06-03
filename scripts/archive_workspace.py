#!/usr/bin/env python3
"""Archive the workspace and wipe it only after zip validation."""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = ROOT / "workspace"
ARCHIVES_DIR = ROOT / "archives"


def safe_name(value: str) -> str:
    """Return a filesystem-safe archive name part."""
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_") or "unknown_project"


def project_name() -> str:
    """Read project name from workspace metadata."""
    meta_path = WORKSPACE_DIR / "meta.json"
    if not meta_path.exists():
        return "unknown_project"
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "unknown_project"
    return safe_name(str(data.get("projectName", "unknown_project")))


def archive_workspace() -> Path | None:
    """Create an archive and clear the workspace after validation."""
    if not WORKSPACE_DIR.exists():
        print("workspace directory does not exist; nothing to archive")
        return None

    ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat().replace(":", "-").replace(".", "-")
    archive_path = ARCHIVES_DIR / f"{project_name()}_{timestamp}.zip"

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in WORKSPACE_DIR.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(WORKSPACE_DIR))

    if not archive_path.exists() or archive_path.stat().st_size <= 0:
        raise RuntimeError("archive validation failed; workspace was not deleted")

    shutil.rmtree(WORKSPACE_DIR)
    WORKSPACE_DIR.mkdir(parents=True)
    return archive_path


def main() -> int:
    archive_path = archive_workspace()
    if archive_path:
        print(f"workspace archived: {archive_path}")
        print("workspace wiped and recreated empty")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

