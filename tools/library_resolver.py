"""Registry-based resolver for multi-project Client-First libraries."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LIBRARIES_DIR = "knowledge-base/libraries"
REGISTRY_FILENAME = "registry.json"
LIBRARY_FILENAME = "client-first-library.json"
TOKEN_MAP_FILENAME = "figma-token-map.json"
CHANGELOG_FILENAME = "changelog.json"


def _registry_path(target: Path) -> Path:
    return target / LIBRARIES_DIR / REGISTRY_FILENAME


def _library_dir(target: Path, site_id: str) -> Path:
    return target / LIBRARIES_DIR / site_id


def load_registry(target: Path) -> dict[str, Any]:
    """Load registry.json; return empty registry if missing."""
    path = _registry_path(target)
    if not path.exists():
        return {"version": "1.0", "projects": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_registry(target: Path, registry: dict[str, Any]) -> None:
    path = _registry_path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")


def resolve_library(target: Path, site_id: str) -> Path:
    """Return path to client-first-library.json for site_id.

    Raises FileNotFoundError when the project is not registered.
    """
    registry = load_registry(target)
    for project in registry.get("projects", []):
        if project.get("webflow_site_id") == site_id:
            lib_path = target / project["library_path"]
            return lib_path
    raise FileNotFoundError(f"site_id '{site_id}' not found in registry")


def load_library(target: Path, site_id: str) -> dict[str, Any]:
    """Load client-first-library.json for site_id."""
    lib_path = resolve_library(target, site_id)
    return json.loads(lib_path.read_text(encoding="utf-8"))


def register_project(target: Path, meta: dict[str, Any]) -> None:
    """Upsert a project entry into registry.json.

    meta must contain: webflow_site_id, figma_file_id, name.
    Optional: library_path (auto-derived if absent).
    """
    site_id: str = meta["webflow_site_id"]
    library_path = meta.get(
        "library_path",
        f"{LIBRARIES_DIR}/{site_id}/{LIBRARY_FILENAME}",
    )
    entry = {
        "id": site_id,
        "name": meta.get("name", site_id),
        "webflow_site_id": site_id,
        "figma_file_id": meta.get("figma_file_id", ""),
        "library_path": library_path,
        "last_synced": meta.get("last_synced", None),
    }
    registry = load_registry(target)
    existing_ids = [p["webflow_site_id"] for p in registry["projects"]]
    if site_id in existing_ids:
        registry["projects"] = [
            entry if p["webflow_site_id"] == site_id else p
            for p in registry["projects"]
        ]
    else:
        registry["projects"].append(entry)
    _save_registry(target, registry)


def scaffold_library_dir(target: Path, site_id: str, figma_file_id: str = "") -> list[str]:
    """Create per-project library directory and seed files if missing.

    Returns list of action strings describing what was created or kept.
    """
    lib_dir = _library_dir(target, site_id)
    lib_dir.mkdir(parents=True, exist_ok=True)
    actions: list[str] = [f"library dir ready: {LIBRARIES_DIR}/{site_id}/"]

    shell_library: dict[str, Any] = {
        "project_id": site_id,
        "webflow_site_id": site_id,
        "figma_file_id": figma_file_id,
        "version": "0.1.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "classes": {},
    }
    shell_token_map: dict[str, Any] = {
        "figma_file_id": figma_file_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "naming_convention": {
            "pattern": "{cf_category}-{semantic_name}",
            "categories": [
                "text-color",
                "background-color",
                "border-color",
                "spacing",
                "font-size",
                "font-weight",
                "border-radius",
                "opacity",
            ],
        },
        "mappings": {},
    }

    for filename, payload in [
        (LIBRARY_FILENAME, shell_library),
        (TOKEN_MAP_FILENAME, shell_token_map),
        (CHANGELOG_FILENAME, []),
    ]:
        file_path = lib_dir / filename
        if file_path.exists():
            actions.append(f"kept {LIBRARIES_DIR}/{site_id}/{filename}")
        else:
            file_path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            actions.append(f"created {LIBRARIES_DIR}/{site_id}/{filename}")

    return actions


def update_last_synced(target: Path, site_id: str) -> None:
    """Stamp last_synced timestamp for site_id in registry."""
    registry = load_registry(target)
    for project in registry["projects"]:
        if project["webflow_site_id"] == site_id:
            project["last_synced"] = datetime.now(timezone.utc).isoformat()
            break
    _save_registry(target, registry)


if __name__ == "__main__":
    # Smoke test: load registry from current dir
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    reg = load_registry(root)
    print(f"registry loaded — {len(reg.get('projects', []))} project(s)")
    for p in reg.get("projects", []):
        print(f"  {p['webflow_site_id']} → {p['library_path']}")
