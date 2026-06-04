#!/usr/bin/env python3
import argparse
import json
import sys
import re
from pathlib import Path
from datetime import datetime

def load_json(path: Path) -> dict:
    if not path.exists():
        print(f"Error: File not found at {path}")
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}")
        sys.exit(1)

def parse_markdown_mapping(path: Path) -> tuple[dict, dict, list]:
    if not path.exists():
        print(f"Error: Mapping file not found at {path}")
        sys.exit(1)
    
    content = path.read_text(encoding="utf-8")
    var_map = {}
    style_map = {}
    errors = []
    
    # Track duplicates
    seen_figma_vars = set()
    seen_wf_vars = set()
    seen_figma_styles = set()
    seen_wf_classes = set()

    mode = None
    for line in content.splitlines():
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
                
                # Clean up backticks
                if f_name.startswith("`") and f_name.endswith("`"):
                    f_name = f_name[1:-1].strip()
                if w_name.startswith("`") and w_name.endswith("`"):
                    w_name = w_name[1:-1].strip()
                
                if f_name and w_name:
                    if mode == "vars":
                        if f_name in seen_figma_vars:
                            errors.append(f"Duplicate mapping for Figma variable: '{f_name}'")
                        if w_name in seen_wf_vars:
                            errors.append(f"Duplicate mapping for Webflow variable: '{w_name}'")
                        var_map[f_name] = w_name
                        seen_figma_vars.add(f_name)
                        seen_wf_vars.add(w_name)
                    elif mode == "styles":
                        if f_name in seen_figma_styles:
                            errors.append(f"Duplicate mapping for Figma style: '{f_name}'")
                        if w_name in seen_wf_classes:
                            errors.append(f"Duplicate mapping for Webflow class: '{w_name}'")
                        style_map[f_name] = w_name
                        seen_figma_styles.add(f_name)
                        seen_wf_classes.add(w_name)
                        
    return var_map, style_map, errors

def main():
    parser = argparse.ArgumentParser(description="Map Figma variables/styles to Webflow baseline")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--input", required=True, help="Path to figma-contract.json")
    parser.add_argument("--output", required=True, help="Path to write webflow-contract.json")
    parser.add_argument("--mapping", required=True, help="Path to figma-webflow-mapping.md")
    parser.add_argument("--report", required=True, help="Path to write mapping-report.json")
    parser.add_argument("--baseline", default=".claude/skills/design-system-sync/template/webflow-design-system-contract.json")
    parser.add_argument("--strict", action="store_true", help="Fail on any errors/warnings")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    mapping_path = Path(args.mapping)
    report_json_path = Path(args.report)
    report_md_path = report_json_path.with_suffix(".md")
    baseline_path = Path(args.baseline)

    # 1. Load baseline & Figma input
    baseline = load_json(baseline_path)
    figma_data = load_json(in_path)

    # 2. Parse Markdown mapping table
    var_map, style_map, mapping_errors = parse_markdown_mapping(mapping_path)

    # 3. Initialize mapping report
    report = {
        "status": "passed",
        "summary": {
            "totalFigmaVariables": len(figma_data.get("variables", {})),
            "mappedVariables": 0,
            "unmappedVariables": 0,
            "totalFigmaStyles": len(figma_data.get("styles", {})),
            "mappedStyles": 0,
            "unmappedStyles": 0,
            "typeMismatches": 0,
            "missingValues": 0,
            "baselineViolations": 0,
            "mappingErrors": len(mapping_errors)
        },
        "mapped": [],
        "errors": list(mapping_errors),
        "warnings": []
    }

    # 4. Initialize Webflow Contract structure
    webflow_contract = {
        "meta": {
            "schemaVersion": "1.0.0",
            "source": "mapped-from-figma",
            "baseline": "finsweet-client-first-2.2",
            "generatedAt": datetime.utcnow().isoformat() + "Z"
        },
        "variables": {},
        "styles": {}
    }

    # 5. Map Variables
    baseline_vars = baseline.get("variables", {})
    figma_vars = figma_data.get("variables", {})
    baseline_excluded = baseline.get("excluded", {})
    webflow_native = set(baseline_excluded.get("webflowNativeSelectors", []))
    native_elements = set(baseline_excluded.get("nativeElementSelectors", []))

    def is_native_wf(name):
        clean = name.strip()
        if clean.startswith("--"): clean = clean[2:]
        if clean.startswith("."): clean = clean[1:]
        return clean.startswith("w-") or clean.startswith("wf-") or f".{clean}" in webflow_native or clean in webflow_native
        
    def is_html_tag(name):
        clean = name.strip()
        if clean.startswith("--"): clean = clean[2:]
        if clean.startswith("."): clean = clean[1:]
        html_tags = {"html", "body", "img", "h1", "h2", "h3", "h4", "h5", "h6", "p", "a", "ul", "ol", "li",
                     "blockquote", "figure", "figcaption", "label", "button", "fieldset", "input", "textarea", "select", "*"}
        return clean in html_tags or f".{clean}" in native_elements or clean in native_elements

    for f_var, f_meta in figma_vars.items():
        if f_var not in var_map:
            report["summary"]["unmappedVariables"] += 1
            report["warnings"].append(f"Figma Variable '{f_var}' is not in the mapping guide.")
            continue
        
        w_var = var_map[f_var]
        
        # Check baseline native violations
        if is_native_wf(w_var) or w_var.startswith("--w-") or w_var.startswith("--wf-"):
            report["summary"]["baselineViolations"] += 1
            report["errors"].append(f"Baseline Violation: Figma variable '{f_var}' maps to Webflow native variable '{w_var}'.")
            continue
        if is_html_tag(w_var):
            report["summary"]["baselineViolations"] += 1
            report["errors"].append(f"Baseline Violation: Figma variable '{f_var}' maps to HTML native tag variable '{w_var}'.")
            continue

        # Check baseline existence
        is_extension = f_meta.get("projectExtension", False)
        if w_var not in baseline_vars:
            if is_extension:
                report["warnings"].append(f"Figma Variable '{f_var}' maps to Webflow Variable '{w_var}' which is not in the baseline (permitted as projectExtension).")
                b_meta = {
                    "type": f_meta.get("type"),
                    "updatePolicy": "update_value_only"
                }
            else:
                report["summary"]["baselineViolations"] += 1
                report["errors"].append(f"Baseline Violation: Webflow Variable '{w_var}' is mapped but does not exist in Webflow baseline template (missing projectExtension: true).")
                continue
        else:
            b_meta = baseline_vars[w_var]
        
        # Check type mismatch
        f_type = f_meta.get("type")
        b_type = b_meta.get("type")
        if f_type != b_type:
            report["summary"]["typeMismatches"] += 1
            report["errors"].append(f"Type mismatch: Figma Variable '{f_var}' (type: {f_type}) maps to Webflow Variable '{w_var}' (expected type: {b_type}).")
            continue

        # Check missing value
        val = f_meta.get("value")
        if val is None or val == "":
            report["summary"]["missingValues"] += 1
            report["errors"].append(f"Missing value for Figma Variable: '{f_var}'.")
            continue

        # Map variable
        webflow_contract["variables"][w_var] = {
            "figmaName": f_var,
            "webflowName": w_var,
            "type": f_type,
            "value": val,
            "resolvedValue": f_meta.get("resolvedValue", val),
            "unit": f_meta.get("unit"),
            "mode": f_meta.get("mode", "default"),
            "updatePolicy": b_meta.get("updatePolicy", "update_value_only")
        }
        
        report["summary"]["mappedVariables"] += 1
        report["mapped"].append({
            "figmaName": f_var,
            "webflowName": w_var,
            "type": f_type,
            "status": "mapped"
        })

    # 6. Map Styles/Classes
    baseline_styles = baseline.get("styles", baseline.get("classes", {}))
    figma_styles = figma_data.get("styles", {})

    for f_style, f_meta in figma_styles.items():
        if f_style not in style_map:
            report["summary"]["unmappedStyles"] += 1
            report["warnings"].append(f"Figma Style '{f_style}' is not in the mapping guide.")
            continue
        
        w_class = style_map[f_style]
        
        # Check baseline native violations
        if is_native_wf(w_class):
            report["summary"]["baselineViolations"] += 1
            report["errors"].append(f"Baseline Violation: Figma style '{f_style}' maps to Webflow native selector '{w_class}'.")
            continue
        if is_html_tag(w_class):
            report["summary"]["baselineViolations"] += 1
            report["errors"].append(f"Baseline Violation: Figma style '{f_style}' maps to HTML native tag selector '{w_class}'.")
            continue

        # Check baseline existence
        is_extension = f_meta.get("projectExtension", False)
        baseline_keys = set(baseline_styles.keys())
        clean_w_class = w_class[1:] if w_class.startswith(".") else w_class
        
        found_key = None
        for bk in baseline_keys:
            clean_bk = bk[1:] if bk.startswith(".") else bk
            if clean_bk == clean_w_class:
                found_key = bk
                break
                
        if not found_key:
            if is_extension:
                report["warnings"].append(f"Figma Style '{f_style}' maps to Webflow Class '{w_class}' which is not in the baseline (permitted as projectExtension).")
                b_style = {
                    "properties": {},
                    "breakpoints": {
                        "main": {},
                        "medium": {},
                        "small": {},
                        "tiny": {}
                    },
                    "matchPolicy": {}
                }
            else:
                report["summary"]["baselineViolations"] += 1
                report["errors"].append(f"Baseline Violation: Webflow Class '{w_class}' is mapped but does not exist in Webflow baseline template (missing projectExtension: true).")
                continue
        else:
            b_style = baseline_styles[found_key]
        
        # Process properties - resolve Figma values to strings
        f_props = f_meta.get("properties", {})
        b_props = b_style.get("properties", {})
        mapped_props = {}
        
        for prop, b_val in b_props.items():
            if prop in f_props:
                f_val = f_props[prop]
                if isinstance(f_val, dict) and "value" in f_val and "unit" in f_val:
                    # e.g. {"value": 16, "unit": "px"} -> "16px"
                    mapped_props[prop] = f"{f_val['value']}{f_val['unit']}"
                elif isinstance(f_val, (int, float)) and prop == "font-weight":
                    mapped_props[prop] = str(f_val)
                else:
                    mapped_props[prop] = str(f_val)
            else:
                # If Figma doesn't specify but Webflow has a var, keep Webflow's var
                mapped_props[prop] = b_val

        # Also copy over any extra property from Figma if it is projectExtension
        if is_extension:
            for prop, f_val in f_props.items():
                if prop not in mapped_props:
                    if isinstance(f_val, dict) and "value" in f_val and "unit" in f_val:
                        mapped_props[prop] = f"{f_val['value']}{f_val['unit']}"
                    else:
                        mapped_props[prop] = str(f_val)

        webflow_contract["styles"][w_class] = {
            "type": "text-style",
            "figmaStyleName": f_style,
            "webflowClassName": w_class,
            "properties": mapped_props,
            "breakpoints": b_style.get("breakpoints", {}),
            "matchPolicy": b_style.get("matchPolicy", {})
        }
        
        report["summary"]["mappedStyles"] += 1

    # 7. Check for unmapped required items (warnings/errors depending on strict)
    # Check if there are variables/styles in the baseline template that are NOT mapped
    unmapped_baseline_vars = set(baseline_vars.keys()) - set(var_map.values())
    if unmapped_baseline_vars:
        for uv in sorted(unmapped_baseline_vars):
            msg = f"Webflow baseline variable '{uv}' is not covered by any Figma mapping."
            if args.strict:
                report["errors"].append(msg)
            else:
                report["warnings"].append(msg)

    # 8. Determine final status
    if report["errors"]:
        report["status"] = "failed"
    elif args.strict and report["warnings"]:
        report["status"] = "failed"
    else:
        report["status"] = "passed"

    # Save outputs
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save Webflow Contract if passed or non-strict
    if report["status"] == "passed" or not args.strict:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(webflow_contract, f, indent=2)
            
    # Save Report JSON
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Save Markdown report
    md_content = f"# Design System Mapping Report\n\n"
    md_content += f"- **Status**: {report['status'].upper()}\n"
    md_content += f"- **Date**: {webflow_contract['meta']['generatedAt']}\n\n"
    md_content += "## Summary\n"
    for k, v in report["summary"].items():
        md_content += f"- {k}: {v}\n"
    
    if report["errors"]:
        md_content += "\n## Errors\n"
        for err in report["errors"]:
            md_content += f"- ❌ {err}\n"
            
    if report["warnings"]:
        md_content += "\n## Warnings\n"
        for wrn in report["warnings"]:
            md_content += f"- ⚠️ {wrn}\n"

    report_md_path.write_text(md_content, encoding="utf-8")

    # Output to console
    print(f"Mapping complete. Status: {report['status'].upper()}")
    if report["status"] == "failed":
        print(f"Errors found: {len(report['errors'])}")
        for err in report["errors"]:
            print(f"- {err}")
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
