#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
import jsonschema

# Make the shared module importable when this script is run from any cwd.
_SKILLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(_SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILLS_DIR))
_SHARED_SCRIPTS_DIR = _SKILLS_DIR / "_shared" / "scripts"
if str(_SHARED_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_SCRIPTS_DIR))
from _shared.scripts.repo_root import find_repo_root, resolve_repo_path  # noqa: E402
from _shared.selector_guards import is_native_selector, is_html_tag_selector  # noqa: E402
from contract_paths import figma_contract_paths, webflow_template_path, workspace_design_system_dir  # noqa: E402

REPO_ROOT = find_repo_root()

def load_required_items(guide_path: Path) -> tuple[set, set]:
    if not guide_path.exists():
        print(f"Error: Guide file not found at {guide_path}")
        sys.exit(1)
    content = guide_path.read_text(encoding="utf-8")
    required_vars = set()
    required_styles = set()
    mode = None
    import re
    for line in content.splitlines():
        line = line.strip()
        if "1. Required Variables" in line:
            mode = "vars"
        elif "2. Required Text Styles" in line:
            mode = "styles"
        elif line.startswith("- `") and mode:
            match = re.search(r"`([^`]+)`", line)
            if match:
                name = match.group(1)
                if mode == "vars": required_vars.add(name)
                elif mode == "styles": required_styles.add(name)
    return required_vars, required_styles

def check_for_placeholders(data, path=""):
    placeholders = []
    if isinstance(data, dict):
        for k, v in data.items():
            current_path = f"{path}.{k}" if path else k
            placeholders.extend(check_for_placeholders(v, current_path))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            current_path = f"{path}[{idx}]"
            placeholders.extend(check_for_placeholders(item, current_path))
    elif isinstance(data, str) and "[VALUE]" in data:
        placeholders.append(path)
    return placeholders

def main():
    parser = argparse.ArgumentParser(description="Validate Figma JSON contract")
    parser.add_argument("--workspace", required=True, help="Workspace name")
    parser.add_argument("--guide", default=".claude/skills/design-system-sync/references/figma-webflow-mapping.md")
    parser.add_argument("--schema", default=".claude/skills/design-system-sync/schema/figma-design-system-contract.schema.json")
    parser.add_argument("--webflow-template", help="Path to webflow-design-system-contract.json")
    parser.add_argument("--mapping", help="Path to figma-webflow-mapping.md")
    args = parser.parse_args()

    contract_path, _ = figma_contract_paths(REPO_ROOT, args.workspace)
    val_dir = workspace_design_system_dir(REPO_ROOT, args.workspace) / "validations"
    val_dir.mkdir(parents=True, exist_ok=True)
    report_json_path = val_dir / "validation_report.json"
    report_txt_path = val_dir / "validation_report.txt"

    guide_path = resolve_repo_path(REPO_ROOT, args.guide)
    schema_path = resolve_repo_path(REPO_ROOT, args.schema)
    
    template_path = resolve_repo_path(REPO_ROOT, args.webflow_template) if args.webflow_template else webflow_template_path(REPO_ROOT)
    mapping_path = resolve_repo_path(REPO_ROOT, args.mapping) if args.mapping else REPO_ROOT / ".claude/skills/design-system-sync/references/figma-webflow-mapping.md"
    assert guide_path is not None and schema_path is not None and template_path is not None and mapping_path is not None
    
    report = {
        "status": "failed",
        "errors": [],
        "warnings": [],
        "summary": {
            "schemaValidation": "not_run",
            "missingRequiredVariables": 0,
            "missingRequiredStyles": 0,
            "placeholdersFound": 0,
            "templateViolations": 0
        }
    }

    if not contract_path.exists():
        msg = f"Validation FAILED: Contract file not found at {contract_path}"
        print(msg)
        report["errors"].append(msg)
        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        report_txt_path.write_text(msg, encoding="utf-8")
        sys.exit(1)

    # 1. Parse JSON
    try:
        data = json.loads(contract_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        msg = f"Validation FAILED: Contract file is not valid JSON. Detail: {e}"
        print(msg)
        report["errors"].append(msg)
        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        report_txt_path.write_text(msg, encoding="utf-8")
        sys.exit(1)

    # 2. Validate against JSON Schema
    schema_ok = True
    if schema_path.exists():
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            from jsonschema import Draft202012Validator
            from _shared.scripts.validate_artifacts import load_registry
            registry = load_registry()
            validator = Draft202012Validator(schema, registry=registry)
            validator.validate(instance=data)
            report["summary"]["schemaValidation"] = "passed"
        except jsonschema.ValidationError as e:
            schema_ok = False
            msg = f"Schema Validation FAILED at '{'.'.join(str(p) for p in e.path)}': {e.message}"
            report["errors"].append(msg)
            report["summary"]["schemaValidation"] = "failed"
        except Exception as e:
            schema_ok = False
            msg = f"Schema loading/validation error: {e}"
            report["errors"].append(msg)
            report["summary"]["schemaValidation"] = "error"
    else:
        report["warnings"].append(f"Schema file not found at {schema_path}. Skipping schema validation.")
        report["summary"]["schemaValidation"] = "skipped"

    # 3. Check for Required Items in Guide
    req_vars, req_styles = load_required_items(guide_path)
    ext_vars = set(data.get("variables", {}).keys())
    ext_styles = set(data.get("styles", {}).keys())

    missing_vars = req_vars - ext_vars
    missing_styles = req_styles - ext_styles
    report["summary"]["missingRequiredVariables"] = len(missing_vars)
    report["summary"]["missingRequiredStyles"] = len(missing_styles)

    for v in sorted(missing_vars):
        report["errors"].append(f"Missing required Figma variable: '{v}'")
    for s in sorted(missing_styles):
        report["errors"].append(f"Missing required Figma style: '{s}'")

    # 4. Check for Placeholders [VALUE]
    placeholders = check_for_placeholders(data)
    report["summary"]["placeholdersFound"] = len(placeholders)
    for p in placeholders:
        report["errors"].append(f"Placeholder '[VALUE]' found at: '{p}'")

    # 5. Check mapping targets against the Webflow template if template and mapping exist
    template_ok = True
    if mapping_path.exists() and template_path.exists():
        try:
            # Parse mapping
            import re
            mapping_content = mapping_path.read_text(encoding="utf-8")
            var_map = {}
            style_map = {}
            mode = None
            for line in mapping_content.splitlines():
                line = line.strip()
                if "## Variable Mapping" in line:
                    mode = "vars"
                    continue
                elif "## Class Mapping" in line:
                    mode = "styles"
                    continue
                if line.startswith("|") and ("Figma Variable" not in line) and ("Figma Style" not in line) and not re.match(r"^[|:\-\s]+$", line):
                    parts = [p.strip() for p in line.split("|")[1:-1]]
                    if len(parts) >= 2:
                        f_name = parts[0]
                        w_name = parts[1]
                        if f_name.startswith("`") and f_name.endswith("`"): f_name = f_name[1:-1].strip()
                        if w_name.startswith("`") and w_name.endswith("`"): w_name = w_name[1:-1].strip()
                        if f_name and w_name:
                            if mode == "vars": var_map[f_name] = w_name
                            elif mode == "styles": style_map[f_name] = w_name

            # Load Webflow template
            template_data = json.loads(template_path.read_text(encoding="utf-8"))
            excluded_data = template_data.get("excluded", {})
            webflow_native = set(excluded_data.get("webflowNativeSelectors", []))
            native_elements = set(excluded_data.get("nativeElementSelectors", []))
            unsupported = set(excluded_data.get("unsupportedSelectors", []))

            # Validate mappings
            violations = 0
            for f_var, w_var in var_map.items():
                # Variables are prefixed with --, we check their names
                if is_native_selector(w_var, webflow_native) or w_var.startswith("--w-") or w_var.startswith("--wf-"):
                    report["errors"].append(f"Template Violation: Figma variable '{f_var}' maps to Webflow native variable '{w_var}'.")
                    violations += 1
                if is_html_tag_selector(w_var, native_elements):
                    report["errors"].append(f"Template Violation: Figma variable '{f_var}' maps to HTML native tag variable '{w_var}'.")
                    violations += 1

            for f_style, w_class in style_map.items():
                if is_native_selector(w_class, webflow_native):
                    report["errors"].append(f"Template Violation: Figma style '{f_style}' maps to Webflow native selector '{w_class}'.")
                    violations += 1
                if is_html_tag_selector(w_class, native_elements):
                    report["errors"].append(f"Template Violation: Figma style '{f_style}' maps to HTML native tag selector '{w_class}'.")
                    violations += 1
                    
            report["summary"]["templateViolations"] = violations
            if violations > 0:
                template_ok = False
        except Exception as e:
            report["warnings"].append(f"Error parsing mapping or Webflow template: {e}")

    # Final verdict
    if schema_ok and not missing_vars and not missing_styles and not placeholders and template_ok:
        report["status"] = "passed"
        txt_msg = "Validation PASSED: All required variables, styles, and schemas are valid and fully populated."
    else:
        report["status"] = "failed"
        txt_msg = f"Validation FAILED: {len(report['errors'])} error(s) found:\n"
        for err in report["errors"]:
            txt_msg += f"- {err}\n"

    print(txt_msg)
    
    # Save reports
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    report_txt_path.write_text(txt_msg, encoding="utf-8")

    if report["status"] == "passed":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
