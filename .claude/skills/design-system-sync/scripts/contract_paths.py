"""Canonical design-system artifact, template, and schema paths."""
from __future__ import annotations

from pathlib import Path


FIGMA_CONTRACT_FILE = "figma-design-system.json"
WEBFLOW_CONTRACT_FILE = "webflow-design-system.json"
FIGMA_TEMPLATE_FILE = "figma-design-system-contract.json"
WEBFLOW_TEMPLATE_FILE = "webflow-design-system-contract.json"
FIGMA_MCP_INPUT_SCHEMA_FILE = "figma-mcp-variable-defs.schema.json"


def workspace_design_system_dir(repo_root: Path, workspace: str) -> Path:
    return repo_root / "workspace" / workspace / "design-system"


def figma_contract_paths(repo_root: Path, workspace: str) -> tuple[Path, Path]:
    root = workspace_design_system_dir(repo_root, workspace)
    return root / FIGMA_CONTRACT_FILE, root / FIGMA_CONTRACT_FILE


def webflow_contract_paths(repo_root: Path, workspace: str) -> tuple[Path, Path]:
    root = workspace_design_system_dir(repo_root, workspace)
    return root / WEBFLOW_CONTRACT_FILE, root / WEBFLOW_CONTRACT_FILE


def figma_template_path(repo_root: Path) -> Path:
    return repo_root / ".claude" / "skills" / "design-system-sync" / "template" / FIGMA_TEMPLATE_FILE


def webflow_template_path(repo_root: Path) -> Path:
    return repo_root / ".claude" / "skills" / "design-system-sync" / "template" / WEBFLOW_TEMPLATE_FILE


def figma_mcp_input_schema_path(repo_root: Path) -> Path:
    return repo_root / ".claude" / "skills" / "design-system-sync" / "schema" / FIGMA_MCP_INPUT_SCHEMA_FILE
