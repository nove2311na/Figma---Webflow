"""Workspace site registry for Webflow-driven migrations.

Pure logic module. Callers (orchestrator, CLI) feed in the site data dict
(typically obtained from the Webflow MCP `data_sites_tool` / `get_site` call)
and the module bootstraps/refreshes the workspace directory + registry file.
No direct MCP calls happen inside this module.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOG = logging.getLogger("site_registry")

REGISTRY_FILENAME = "registry.json"
SITE_INFO_FILENAME = "webflow-site-info.json"
REGISTRY_VERSION = "1.0.0"

SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9._-]+")


def safe_dir_name(value: str) -> str:
    """Collapse any unsafe char to `-`; collapse runs of `-`."""
    cleaned = SAFE_NAME_RE.sub("-", value).strip("-")
    return cleaned or "unnamed-site"


@dataclass
class SiteInfo:
    site_id: str
    short_name: str
    display_name: str
    workspace_dir: str
    last_connected: str
    figma_file_key: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_webflow_site(cls, site: dict[str, Any], workspace_dir: Path) -> "SiteInfo":
        site_id = site.get("id") or site.get("siteId")
        short_name = site.get("shortName") or safe_dir_name(site_id or "site")
        display_name = site.get("displayName") or short_name
        if not site_id:
            raise ValueError("Webflow site dict missing required 'id' field")
        return cls(
            site_id=site_id,
            short_name=short_name,
            display_name=display_name,
            workspace_dir=str(workspace_dir),
            last_connected=datetime.now(timezone.utc).isoformat(),
            raw=site,
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


def _read_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": REGISTRY_VERSION, "sites": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Registry corrupted at {path}: {exc}") from exc


def _write_registry(path: Path, registry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def bootstrap_workspace(
    site: dict[str, Any],
    *,
    repo_root: Path,
    registry_path: Path | None = None,
    force_refresh: bool = False,
) -> SiteInfo:
    """Register a Webflow site and create its workspace directory.

    Idempotent: if `shortName` is already in the registry, the existing
    workspace_dir is reused and only `webflow-site-info.json` is refreshed
    (unless `force_refresh=False` to skip the refresh).
    """
    if registry_path is None:
        registry_path = repo_root / "workspace" / "_webflow-sites" / REGISTRY_FILENAME

    registry = _read_registry(registry_path)
    sites: dict[str, Any] = registry.setdefault("sites", {})

    short_name = site.get("shortName") or safe_dir_name(site.get("id") or "site")
    workspace_dir = repo_root / "workspace" / short_name
    site_info = SiteInfo.from_webflow_site(site, workspace_dir)

    if short_name in sites and not force_refresh:
        LOG.info("site %s already registered; refreshing webflow-site-info.json only", short_name)
    else:
        workspace_dir.mkdir(parents=True, exist_ok=True)
        (workspace_dir / "design-system").mkdir(parents=True, exist_ok=True)
        (workspace_dir / "design-system" / "validations").mkdir(parents=True, exist_ok=True)
        (workspace_dir / "figma").mkdir(parents=True, exist_ok=True)
        (workspace_dir / "html").mkdir(parents=True, exist_ok=True)
        (workspace_dir / "preview").mkdir(parents=True, exist_ok=True)
        LOG.info("created workspace dir %s", workspace_dir)

    sites[short_name] = site_info.to_dict()
    _write_registry(registry_path, registry)

    info_path = workspace_dir / SITE_INFO_FILENAME
    info_path.write_text(
        json.dumps(site_info.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    LOG.info("wrote %s", info_path)
    return site_info


def list_known_sites(repo_root: Path) -> list[SiteInfo]:
    """Return all sites previously registered (in shortName order)."""
    registry_path = repo_root / "workspace" / "_webflow-sites" / REGISTRY_FILENAME
    if not registry_path.exists():
        return []
    registry = _read_registry(registry_path)
    out: list[SiteInfo] = []
    for short_name in sorted(registry.get("sites", {})):
        raw = registry["sites"][short_name]
        out.append(
            SiteInfo(
                site_id=raw["site_id"],
                short_name=raw["short_name"],
                display_name=raw["display_name"],
                workspace_dir=raw["workspace_dir"],
                last_connected=raw["last_connected"],
                figma_file_key=raw.get("figma_file_key"),
                raw=raw.get("raw", {}),
            )
        )
    return out


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    repo_root = Path(__file__).resolve().parents[4]
    print(json.dumps([s.to_dict() for s in list_known_sites(repo_root)], indent=2))
