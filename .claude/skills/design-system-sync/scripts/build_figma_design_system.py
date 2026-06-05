#!/usr/bin/env python3
"""Build figma-design-system.json from a saved Figma MCP payload."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCRIPT_DIR = Path(__file__).resolve().parent
SHARED_DIR = SCRIPT_DIR.parents[1] / "_shared" / "scripts"
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from repo_root import find_repo_root, resolve_repo_path  # noqa: E402
from contract_paths import (  # noqa: E402
    figma_contract_paths,
    figma_mcp_input_schema_path,
    figma_template_path,
    workspace_design_system_dir,
)

REPO_ROOT = find_repo_root(Path(__file__))


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Error: file not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON at {path}: {exc}")
        sys.exit(1)


def first_present(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return None


def normalize_name(name: str) -> str:
    return " / ".join(part.strip() for part in str(name).replace("\\", "/").split("/") if part.strip())


def walk_dicts(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        found.append(value)
        for child in value.values():
            found.extend(walk_dicts(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(walk_dicts(child))
    return found


def format_schema_path(error_path: Any) -> str:
    parts = [str(part) for part in error_path]
    return "$" if not parts else "$." + ".".join(parts)


def validate_input_payload(payload: dict[str, Any], schema_path: Path) -> list[dict[str, str]]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    return [
        {
            "path": format_schema_path(error.path),
            "message": error.message,
        }
        for error in errors
    ]


def entry_name(entry: dict[str, Any], fallback: str | None = None) -> str | None:
    raw = first_present(entry, ("name", "displayName", "variableName", "styleName", "figmaStyleName"))
    if raw is None:
        raw = fallback
    if raw is None:
        return None
    return normalize_name(str(raw))


def entry_id(entry: dict[str, Any]) -> Any:
    return first_present(entry, ("figmaId", "id", "key", "node_id", "nodeId", "styleId", "variableId"))


def entry_modes(entry: dict[str, Any]) -> dict[str, Any] | None:
    raw = first_present(entry, ("modes", "valuesByMode", "values_by_mode", "modeValues"))
    if isinstance(raw, dict):
        return raw
    return None


def entry_value(entry: dict[str, Any]) -> Any:
    value = first_present(entry, ("value", "resolvedValue", "resolved_value"))
    if value is not None:
        return value
    modes = entry_modes(entry)
    if modes:
        return next(iter(modes.values()))
    return None


def collect_named_entries(payload: Any, top_level_keys: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}

    def add(candidate: Any, fallback: str | None = None) -> None:
        if not isinstance(candidate, dict):
            return
        name = entry_name(candidate, fallback)
        if name:
            entries.setdefault(name, candidate)

    if isinstance(payload, dict):
        for key in top_level_keys:
            section = payload.get(key)
            if isinstance(section, dict):
                for item_key, item in section.items():
                    add(item, item_key)
            elif isinstance(section, list):
                for item in section:
                    add(item)

    for item in walk_dicts(payload):
        add(item)

    return entries


def overlay_variable(template_entry: dict[str, Any], figma_entry: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(template_entry)
    value = entry_value(figma_entry)
    modes = entry_modes(figma_entry)
    figma_id = entry_id(figma_entry)

    if figma_id is not None:
        out["figmaId"] = figma_id
    if value is not None:
        out["value"] = value
        out["resolvedValue"] = first_present(figma_entry, ("resolvedValue", "resolved_value")) or value
    if modes is not None:
        out["modes"] = modes

    for src, dst in (
        ("type", "type"),
        ("unit", "unit"),
        ("mode", "mode"),
        ("collection", "collection"),
        ("aliasOf", "aliasOf"),
        ("description", "description"),
    ):
        if src in figma_entry and figma_entry[src] is not None:
            out[dst] = figma_entry[src]

    return out


def overlay_style(template_entry: dict[str, Any], figma_entry: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(template_entry)
    figma_id = entry_id(figma_entry)
    if figma_id is not None:
        out["figmaId"] = figma_id

    properties = first_present(figma_entry, ("properties", "style", "typeStyle", "textStyle"))
    if isinstance(properties, dict):
        out["properties"] = properties

    for src, dst in (
        ("type", "type"),
        ("mode", "mode"),
        ("category", "category"),
        ("description", "description"),
    ):
        if src in figma_entry and figma_entry[src] is not None:
            out[dst] = figma_entry[src]

    return out


def template_id_remaining(entry: dict[str, Any]) -> bool:
    figma_id = str(entry.get("figmaId", ""))
    return ":tpl-" in figma_id or "VariableID:tpl-" in figma_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Build figma-design-system.json from a saved Figma MCP payload")
    parser.add_argument("--workspace", required=True, help="Workspace name")
    parser.add_argument("--input", required=True, help="Path to the saved Figma MCP JSON payload")
    parser.add_argument("--output", help="Path to write figma-design-system.json")
    parser.add_argument("--template", help="Path to figma-design-system-contract.json")
    parser.add_argument("--input-schema", help="Path to figma-mcp-variable-defs.schema.json")
    parser.add_argument("--report", help="Path to write build-figma-design-system-report.json")
    parser.add_argument("--allow-partial", action="store_true", help="Write output even when some template keys are missing")
    args = parser.parse_args()

    input_path = resolve_repo_path(REPO_ROOT, args.input)
    template_path = resolve_repo_path(REPO_ROOT, args.template) if args.template else figma_template_path(REPO_ROOT)
    input_schema_path = resolve_repo_path(REPO_ROOT, args.input_schema) if args.input_schema else figma_mcp_input_schema_path(REPO_ROOT)
    output_path, _ = figma_contract_paths(REPO_ROOT, args.workspace)
    if args.output:
        output_path = resolve_repo_path(REPO_ROOT, args.output)
    report_path = (
        resolve_repo_path(REPO_ROOT, args.report)
        if args.report
        else workspace_design_system_dir(REPO_ROOT, args.workspace) / "validations" / "build-figma-design-system-report.json"
    )

    assert input_path is not None and template_path is not None and input_schema_path is not None and output_path is not None and report_path is not None

    payload = load_json(input_path)
    template = load_json(template_path)

    input_schema_errors = validate_input_payload(payload, input_schema_path)
    if input_schema_errors:
        report = {
            "status": "failed",
            "input": str(input_path),
            "inputSchema": str(input_schema_path),
            "template": str(template_path),
            "output": str(output_path),
            "summary": {
                "inputSchemaErrors": len(input_schema_errors),
                "templateVariables": len(template.get("variables", {})),
                "templateStyles": len(template.get("styles", {})),
            },
            "inputSchemaErrors": input_schema_errors,
            "missingVariables": [],
            "missingStyles": [],
            "templateIdsRemaining": [],
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Figma MCP input schema validation: FAILED")
        print(f"Report: {report_path}")
        print("Normalize the Figma MCP response to figma-mcp-variable-defs.schema.json before building.")
        sys.exit(1)

    result = copy.deepcopy(template)

    raw_variables = collect_named_entries(payload, ("variables", "variableDefinitions", "variableCollections"))
    raw_styles = collect_named_entries(payload, ("styles", "textStyles", "paintStyles", "effectStyles", "gridStyles"))

    missing_variables: list[str] = []
    missing_styles: list[str] = []
    updated_variables: list[str] = []
    updated_styles: list[str] = []

    for name, template_entry in template.get("variables", {}).items():
        key = normalize_name(name)
        raw = raw_variables.get(key)
        if raw is None:
            missing_variables.append(name)
            continue
        result["variables"][name] = overlay_variable(template_entry, raw)
        updated_variables.append(name)

    for name, template_entry in template.get("styles", {}).items():
        key = normalize_name(name)
        raw = raw_styles.get(key)
        if raw is None:
            missing_styles.append(name)
            continue
        result["styles"][name] = overlay_style(template_entry, raw)
        updated_styles.append(name)

    result.setdefault("meta", {})
    result["meta"]["source"] = "figma"
    result["meta"]["extractedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    result["meta"]["extractedBy"] = "figma-dev-mode-mcp"

    template_ids_remaining = [
        f"variables.{name}"
        for name, entry in result.get("variables", {}).items()
        if template_id_remaining(entry)
    ] + [
        f"styles.{name}"
        for name, entry in result.get("styles", {}).items()
        if template_id_remaining(entry)
    ]

    report = {
        "status": "passed",
        "input": str(input_path),
        "inputSchema": str(input_schema_path),
        "template": str(template_path),
        "output": str(output_path),
        "summary": {
            "templateVariables": len(template.get("variables", {})),
            "templateStyles": len(template.get("styles", {})),
            "inputSchemaErrors": 0,
            "rawVariablesDiscovered": len(raw_variables),
            "rawStylesDiscovered": len(raw_styles),
            "updatedVariables": len(updated_variables),
            "updatedStyles": len(updated_styles),
            "missingVariables": len(missing_variables),
            "missingStyles": len(missing_styles),
            "templateIdsRemaining": len(template_ids_remaining),
        },
        "missingVariables": missing_variables,
        "missingStyles": missing_styles,
        "templateIdsRemaining": template_ids_remaining,
    }

    if missing_variables or missing_styles or template_ids_remaining:
        report["status"] = "failed"

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    should_write = report["status"] == "passed" or args.allow_partial
    if should_write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Figma design-system build status: {report['status'].upper()}")
    print(f"Report: {report_path}")
    if should_write:
        print(f"Output: {output_path}")
    if report["status"] != "passed":
        print("Figma payload is not template-complete. Fix the Figma file or MCP payload before mapping.")
        sys.exit(1)


if __name__ == "__main__":
    main()
