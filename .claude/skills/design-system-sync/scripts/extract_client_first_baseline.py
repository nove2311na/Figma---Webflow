#!/usr/bin/env python3
import argparse
import json
import sys
import re
from pathlib import Path
from datetime import datetime

def is_allowed_var(name):
    allowed_patterns = [
        r"^--_theme---",
        r"^--_typography---",
        r"^--_layout---",
        r"^--_sizes---",
        r"^--brand--",
        r"^--neutral--",
        r"^--font-family--",
        r"^--font-weight--",
        r"^--focus--"
    ]
    return any(re.match(pat, name) for pat in allowed_patterns)

def is_allowed_class(name):
    allowed_patterns = [
        r"^heading-style-", r"^text-size-", r"^text-weight-", r"^text-style-",
        r"^text-color-", r"^background-color-", r"^max-width-", r"^margin-",
        r"^padding-", r"^container-", r"^button-", r"^form-", r"^icon-",
        r"^hide$", r"^show$", r"^overflow-", r"^z-index-", r"^align-",
        r"^flex-", r"^grid-", r"^display-"
    ]
    return any(re.match(pat, name) for pat in allowed_patterns)

def determine_var_type(name):
    name_lower = name.lower()
    if "color" in name_lower or "brand" in name_lower or "neutral" in name_lower or "transparent" in name_lower:
        return "color"
    elif "weight" in name_lower:
        return "font-weight"
    elif "family" in name_lower:
        return "font-family"
    elif "spacing" in name_lower or "gap" in name_lower or "padding" in name_lower or "margin" in name_lower or "width" in name_lower or "size" in name_lower or "radius" in name_lower:
        return "size"
    elif "count" in name_lower:
        return "number"
    return "string"

def parse_declarations(dec_str):
    props = {}
    for item in dec_str.split(";"):
        item = item.strip()
        if ":" in item:
            k, v = item.split(":", 1)
            k = k.strip().lower()
            v = v.strip()
            # Normalize colors and font-family quotes
            if v.startswith("#"):
                v = v.lower()
            if k == "font-family":
                v = v.replace('"', '').replace("'", "")
            props[k] = v
    return props

def main():
    parser = argparse.ArgumentParser(description="Extract Client-First baseline contract from Webflow CSS")
    parser.add_argument("--input-css", required=True, help="Path to exported Webflow CSS")
    parser.add_argument("--output-contract", required=True, help="Path to output client-first-baseline-contract.json")
    parser.add_argument("--report", required=True, help="Path to output client-first-extraction-report.json")
    parser.add_argument("--strict", action="store_true", help="Fail if any parser errors occur")
    args = parser.parse_args()

    input_css_path = Path(args.input_css)
    output_contract_path = Path(args.output_contract)
    report_json_path = Path(args.report)
    report_md_path = report_json_path.with_suffix(".md")

    report = {
        "status": "passed",
        "summary": {
            "totalSelectorsParsed": 0,
            "clientFirstSelectorsIncluded": 0,
            "webflowNativeSelectorsExcluded": 0,
            "nativeElementSelectorsExcluded": 0,
            "unsupportedSelectors": 0,
            "variablesIncluded": 0
        },
        "included": {
            "variables": [],
            "classes": []
        },
        "excluded": {
            "webflowNative": [],
            "nativeElements": [],
            "unsupported": []
        },
        "warnings": [],
        "errors": []
    }

    if not input_css_path.exists():
        msg = f"Error: Input CSS file not found at {input_css_path}"
        report["status"] = "failed"
        report["errors"].append(msg)
        report_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(msg)
        sys.exit(1)

    css_content = input_css_path.read_text(encoding="utf-8")
    
    # 1. Clean comments
    css_content = re.sub(r"/\*.*?\*/", "", css_content, flags=re.DOTALL)

    # 2. Match rules: selector { declarations }
    # Using a simple parser loop to handle braces correctly
    rules = []
    current_selector = []
    current_declarations = []
    in_declarations = False
    
    # Simple brace parsing
    brace_depth = 0
    buffer = []
    
    for char in css_content:
        if char == "{":
            if brace_depth == 0:
                current_selector = "".join(buffer).strip()
                buffer = []
                in_declarations = True
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1
            if brace_depth == 0:
                current_declarations = "".join(buffer).strip()
                buffer = []
                in_declarations = False
                rules.append((current_selector, current_declarations))
            else:
                buffer.append(char)
        else:
            buffer.append(char)

    # Allowlist/Denylist categories
    variables = {}
    classes = {}

    html_tags = {
        "html", "body", "img", "h1", "h2", "h3", "h4", "h5", "h6", "p", "a", "ul", "ol", "li",
        "blockquote", "figure", "figcaption", "label", "button", "fieldset", "input", "textarea", "select", "*"
    }

    for raw_selector, dec_str in rules:
        # Split multiple selectors, e.g., h1, h2
        selectors = [s.strip() for s in raw_selector.split(",") if s.strip()]
        for sel in selectors:
            # Handle media queries or keyframes (nested rules)
            if sel.startswith("@"):
                report["excluded"]["unsupported"].append(sel)
                report["summary"]["unsupportedSelectors"] += 1
                continue
                
            report["summary"]["totalSelectorsParsed"] += 1

            # Parse variables under :root or HTML selectors
            if sel == ":root" or sel == "html" or sel == "body":
                props = parse_declarations(dec_str)
                for k, v in props.items():
                    if k.startswith("--"):
                        if is_allowed_var(k):
                            v_type = determine_var_type(k)
                            variables[k] = {
                                "name": k,
                                "type": v_type,
                                "value": v,
                                "source": {
                                    "selector": sel,
                                    "property": k
                                },
                                "editableInFigma": True,
                                "syncPolicy": "figma_value_to_webflow"
                            }
                            report["included"]["variables"].append(k)
                            report["summary"]["variablesIncluded"] += 1
                        else:
                            # Not an allowed Client-First variable pattern
                            report["excluded"]["unsupported"].append(k)
                            report["summary"]["unsupportedSelectors"] += 1
                continue

            # Class selectors
            if sel.startswith("."):
                class_name = sel[1:].split(":")[0].split(".")[0].strip() # Strip pseudo states and compound classes
                
                # Check excludes
                if class_name.startswith("w-") or class_name.startswith("wf-"):
                    report["excluded"]["webflowNative"].append(sel)
                    report["summary"]["webflowNativeSelectorsExcluded"] += 1
                    continue
                
                if is_allowed_class(class_name):
                    props = parse_declarations(dec_str)
                    classes[class_name] = {
                        "selector": f".{class_name}",
                        "type": "text-style" if "heading" in class_name or "text" in class_name else "style",
                        "category": "typography" if "heading" in class_name or "text" in class_name else "layout",
                        "properties": props,
                        "breakpoints": {
                            "main": {},
                            "medium": {},
                            "small": {},
                            "tiny": {}
                        },
                        "pseudoStates": {},
                        "editableInFigma": True,
                        "syncPolicy": "figma_value_to_webflow"
                    }
                    report["included"]["classes"].append(sel)
                    report["summary"]["clientFirstSelectorsIncluded"] += 1
                else:
                    report["excluded"]["unsupported"].append(sel)
                    report["summary"]["unsupportedSelectors"] += 1
                continue

            # HTML Native tags
            if sel in html_tags:
                report["excluded"]["nativeElements"].append(sel)
                report["summary"]["nativeElementSelectorsExcluded"] += 1
                continue

            # Unsupported/other selectors
            report["excluded"]["unsupported"].append(sel)
            report["summary"]["unsupportedSelectors"] += 1

    # Check baseline presence
    if not variables and not classes:
        msg = "Error: NO_CLIENT_FIRST_BASELINE_FOUND. No Client-First variables or classes were parsed from the CSS."
        report["status"] = "failed"
        report["errors"].append(msg)
        
        # Save failure report
        report_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(msg)
        sys.exit(1)

    # Build final baseline contract
    baseline_contract = {
        "meta": {
            "schemaVersion": "1.0.0",
            "source": "webflow-css-export",
            "baseline": "finsweet-client-first-2.2",
            "scope": "client-first-only",
            "generatedAt": datetime.utcnow().isoformat() + "Z"
        },
        "variables": variables,
        "classes": classes,
        "excluded": {
            "webflowNativeSelectors": list(set(report["excluded"]["webflowNative"])),
            "nativeElementSelectors": list(set(report["excluded"]["nativeElements"])),
            "unsupportedSelectors": list(set(report["excluded"]["unsupported"]))
        }
    }

    # Save outputs
    output_contract_path.parent.mkdir(parents=True, exist_ok=True)
    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_contract_path, "w", encoding="utf-8") as f:
        json.dump(baseline_contract, f, indent=2)

    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Markdown report
    md_content = f"# Client-First Baseline Extraction Report\n\n"
    md_content += f"- **Status**: {report['status'].upper()}\n"
    md_content += f"- **Date**: {baseline_contract['meta']['generatedAt']}\n\n"
    md_content += "## Extraction Summary\n"
    for k, v in report["summary"].items():
        md_content += f"- **{k}**: {v}\n"
    
    if report["errors"]:
        md_content += "\n## Errors\n"
        for err in report["errors"]:
            md_content += f"- ❌ {err}\n"
            
    if report["warnings"]:
        md_content += "\n## Warnings\n"
        for wrn in report["warnings"]:
            md_content += f"- ⚠️ {wrn}\n"

    report_md_path.write_text(md_content, encoding="utf-8")

    print(f"Extraction successful. Baseline contract written to {output_contract_path}")
    sys.exit(0)

if __name__ == "__main__":
    main()
