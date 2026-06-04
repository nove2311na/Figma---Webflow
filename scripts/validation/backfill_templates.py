#!/usr/bin/env python3
"""Backfill figmaId + namespace + modes into the LLM-fillable exemplar templates.

Phase 6 of the skill-overhaul plan. After variable-entry.schema.json was tightened
to require figmaId + namespace + modes, the existing 148 variable entries + 19
style entries in the templates no longer conform. This script:

1. Reads each template (figma + webflow).
2. For each variable entry, derives:
   - figmaId: deterministic from name hash. Pattern: VariableID:<uuid>:<index>.
   - namespace: derived from existing collection field if present, else 'other'.
   - modes: wrapped from existing `mode` (singular) into { mode: value }.
3. For each style entry, derives figmaId the same way.
4. Adds 8 NEW example entries (one per Webflow CSS namespace from the user's CSS)
   showing the full figmaId + modes + aliasOf pattern in production shape.
5. Writes the result back to the same file.

Run:
    python scripts/validation/backfill_templates.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import OrderedDict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE_FIGMA = REPO_ROOT / ".claude/skills/design-system-sync/template/figma-design-system-contract.json"
TEMPLATE_WEBFLOW = REPO_ROOT / ".claude/skills/design-system-sync/template/webflow-design-system-contract.json"

# Collection name (from Figma) -> Webflow CSS namespace
COLLECTION_TO_NAMESPACE = {
    "Layout": "_layout",
    "Typography": "_typography",
    "Sizes": "_sizes",
    "Colors": "_neutral",
    "Brand": "_brand",
    "Theme": "_theme",
    "Focus": "_focus",
    "Font Weight": "_font-weight",
    "Borders": "_sizes",
    "Spacing": "_layout",
    "Gaps": "_layout",
}


def derive_figma_id(name: str, idx: int) -> str:
    """Deterministic figmaId from name. Templates use a tpl: prefix so production
    code can detect template entries and replace with real ids on extraction."""
    h = hashlib.sha256(name.encode("utf-8")).hexdigest()
    uuid = f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
    return f"VariableID:tpl-{uuid}:{idx}"


def derive_namespace(entry: dict) -> str:
    collection = entry.get("collection") or ""
    if collection in COLLECTION_TO_NAMESPACE:
        return COLLECTION_TO_NAMESPACE[collection]
    name = entry.get("name", "")
    name_lower = name.lower()
    if "spacing" in name_lower or "gap" in name_lower or "section" in name_lower or "grid" in name_lower:
        return "_layout"
    if "font-size" in name_lower or "line-height" in name_lower or "letter-spacing" in name_lower or "h1" in name_lower or "h2" in name_lower or "h3" in name_lower or "h4" in name_lower or "h5" in name_lower or "h6" in name_lower or "body" in name_lower:
        return "_typography"
    if "container" in name_lower or "max-width" in name_lower or "border" in name_lower or "size" in name_lower:
        return "_sizes"
    if "color" in name_lower or "background" in name_lower:
        return "_theme"
    if "focus" in name_lower:
        return "_focus"
    if "weight" in name_lower:
        return "_font-weight"
    return "other"


def derive_modes(entry: dict) -> dict:
    """Wrap existing `mode` (singular) into modes object. Default to {'default': <value>}."""
    mode = entry.get("mode", "default")
    value = entry.get("value", "")
    if isinstance(value, (int, float)):
        value_str = str(value)
    elif value is None:
        value_str = ""
    else:
        value_str = str(value)
    if mode not in ("default", "dark", "light", "high-contrast"):
        mode = "default"
    return OrderedDict([(mode, value_str)])


def backfill_variable_entry(entry: dict, name: str, idx: int) -> dict:
    """Add figmaId + namespace + modes to an existing variable entry, preserving all other fields."""
    new_entry = OrderedDict()
    for k, v in entry.items():
        new_entry[k] = v
    new_entry["name"] = name
    new_entry["figmaId"] = derive_figma_id(name, idx)
    if "namespace" not in new_entry:
        new_entry["namespace"] = derive_namespace(new_entry)
    if "modes" not in new_entry:
        new_entry["modes"] = derive_modes(new_entry)
    else:
        new_entry["modes"] = OrderedDict(new_entry["modes"])
    if "editableInFigma" not in new_entry:
        new_entry["editableInFigma"] = True
    if "projectExtension" not in new_entry:
        new_entry["projectExtension"] = False
    return new_entry


def add_namespace_examples(variables: dict, is_webflow: bool = False) -> dict:
    """Add 8 NEW example entries (one per Webflow namespace from the user's CSS)."""
    examples = OrderedDict()
    base_id = 9000

    def make_entry(name, idx, vtype, namespace, value, modes, unit=None, alias_of=None, collection=""):
        e = OrderedDict([
            ("name", name),
            ("figmaId", f"VariableID:example-{name.replace('---','-').replace('--','-')}:{idx}"),
            ("type", vtype),
            ("namespace", namespace),
            ("value", value),
            ("modes", OrderedDict(modes)),
            ("unit", unit),
            ("source", OrderedDict([("selector", ":root"), ("property", f"--{name}"), ("collection", collection)])),
            ("editableInFigma", True),
            ("projectExtension", False),
        ])
        if alias_of:
            e["aliasOf"] = alias_of
        if is_webflow:
            e["figmaName"] = name
            e["webflowName"] = name
            e["updatePolicy"] = "create"
        return e

    examples["_theme---text-color--primary"] = make_entry(
        "_theme---text-color--primary", base_id, "alias", "_theme", "var(--neutral--black)",
        [("default", "var(--neutral--black)"), ("dark", "var(--neutral--white)")],
        alias_of="VariableID:example-neutral-black:9100", collection="Theme")

    examples["_typography---h1--h1-font-size"] = make_entry(
        "_typography---h1--h1-font-size", base_id+1, "font-size", "_typography", 4,
        [("default", "4rem")], unit="rem", collection="Typography")

    examples["_sizes---container--large"] = make_entry(
        "_sizes---container--large", base_id+2, "size", "_sizes", 80,
        [("default", "80rem")], unit="rem", collection="Sizes")

    examples["_layout---spacing--medium"] = make_entry(
        "_layout---spacing--medium", base_id+3, "spacing", "_layout", 2,
        [("default", "2rem")], unit="rem", collection="Layout")

    examples["_focus--width"] = make_entry(
        "_focus--width", base_id+4, "size", "_focus", 0.125,
        [("default", ".125rem")], unit="rem", collection="Focus")

    examples["_brand--blue"] = make_entry(
        "_brand--blue", base_id+5, "color", "_brand", "#2d62ff",
        [("default", "#2d62ff"), ("dark", "#d9e5ff")], collection="Brand")

    examples["_neutral--black"] = make_entry(
        "_neutral--black", base_id+6, "color", "_neutral", "#000",
        [("default", "#000"), ("dark", "#fff")], collection="Colors")

    examples["_font-weight--bold"] = make_entry(
        "_font-weight--bold", base_id+7, "font-weight", "_font-weight", 700,
        [("default", "700")], collection="Font Weight")

    variables.update(examples)
    return variables


def backfill_template(path: Path, is_webflow: bool) -> tuple[int, int]:
    print(f"Reading {path.name}...")
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=OrderedDict)

    variables = data.get("variables", OrderedDict())
    styles = data.get("styles", OrderedDict())

    var_count_before = len(variables)
    style_count_before = len(styles)

    new_variables = OrderedDict()
    for idx, (name, entry) in enumerate(variables.items(), 1):
        new_variables[name] = backfill_variable_entry(entry, name, idx)

    new_styles = OrderedDict()
    for idx, (name, entry) in enumerate(styles.items(), 1):
        new_entry = OrderedDict()
        for k, v in entry.items():
            new_entry[k] = v
        new_entry["name"] = name
        new_entry["figmaId"] = derive_figma_id(name, idx)
        if "webflowClassName" not in new_entry and is_webflow:
            new_entry["webflowClassName"] = name
        elif "figmaStyleName" not in new_entry and not is_webflow:
            new_entry["figmaStyleName"] = name
        if "category" not in new_entry:
            if "h1" in name.lower() or "heading" in name.lower():
                new_entry["category"] = "heading"
            elif "text" in name.lower():
                new_entry["category"] = "text"
            else:
                new_entry["category"] = "custom"
        new_styles[name] = new_entry

    new_variables = add_namespace_examples(new_variables, is_webflow=is_webflow)

    if is_webflow:
        new_variables = OrderedDict()
        with open(path) as f:
            data_orig = json.load(f, object_pairs_hook=OrderedDict)
        orig_variables = data_orig.get("variables", OrderedDict())
        for idx, (name, entry) in enumerate(orig_variables.items(), 1):
            new_variables[name] = backfill_variable_entry(entry, name, idx)
        new_variables = add_namespace_examples(new_variables, is_webflow=is_webflow)
        data["variables"] = new_variables
        for k, v in new_styles.items():
            new_styles[k]["webflowClassName"] = new_styles[k].get("webflowClassName", k)
        data["styles"] = new_styles
    else:
        data["variables"] = new_variables
        data["styles"] = new_styles

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return var_count_before + 8, style_count_before


def main() -> int:
    for path, is_webflow in [(TEMPLATE_FIGMA, False), (TEMPLATE_WEBFLOW, True)]:
        if not path.exists():
            print(f"SKIP: {path} not found")
            continue
        vars_after, styles_after = backfill_template(path, is_webflow)
        print(f"  {path.name}: variables +8 examples, styles unchanged. Total variables={vars_after}, styles={styles_after}")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
