#!/usr/bin/env python3
import argparse
import sys
import re
import json
from pathlib import Path

_SHARED_DIR = Path(__file__).resolve().parents[2] / "_shared" / "scripts"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))
from repo_root import find_repo_root, resolve_repo_path

REPO_ROOT = find_repo_root()

def main():
    parser = argparse.ArgumentParser(description="Validate Figma HTML layer naming compliance")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--mode", default="warn", choices=["strict", "warn", "ignore"], help="Validation mode")
    args = parser.parse_args()

    raw_html_path = REPO_ROOT / "workspace" / args.workspace / "html-nodes" / args.node_id / "raw-figma.html"
    val_dir = REPO_ROOT / "workspace" / args.workspace / "html-nodes" / args.node_id / "validations"
    val_dir.mkdir(parents=True, exist_ok=True)
    report_json_path = val_dir / "html_validation_report.json"
    report_txt_path = val_dir / "html_validation_report.txt"

    mapping_path = resolve_repo_path(REPO_ROOT, ".claude/skills/figma-to-html-architect/references/html-semantic-mapping.json")
    assert mapping_path is not None

    report = {
        "status": "passed",
        "mode": args.mode,
        "summary": {
            "totalDataNames": 0,
            "criticalIssues": 0,
            "warnings": 0,
            "ignored": 0
        },
        "criticalIssues": [],
        "warnings": [],
        "ignored": []
    }

    if not raw_html_path.exists():
        msg = f"Validation FAILED: Raw HTML not found at {raw_html_path}"
        print(msg)
        report["status"] = "failed"
        report["criticalIssues"].append(msg)
        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        report_txt_path.write_text(msg, encoding="utf-8")
        sys.exit(1)

    html_content = raw_html_path.read_text(encoding="utf-8")
    
    # Extract all data-name attributes
    data_names = re.findall(r'data-name="([^"]+)"', html_content)
    report["summary"]["totalDataNames"] = len(data_names)

    if not data_names:
        msg = "Warning: No data-name attributes found in the HTML. Cannot validate."
        print(msg)
        report["warnings"].append(msg)
        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        report_txt_path.write_text(msg, encoding="utf-8")
        sys.exit(0)

    # Load mapping configuration
    try:
        with open(mapping_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        msg = f"Failed to load semantic mapping from {mapping_path}: {e}"
        print(msg)
        sys.exit(1)

    critical_keywords = list(config.get("rules", {}).keys())
    allowed_generic = config.get("allowedGenericKeywords", [])
    decorative_keywords = config.get("decorativeKeywords", [])

    for name in data_names:
        # Check if matches any recognizable rules/keywords
        is_critical = any(kw in name for kw in critical_keywords)
        is_layout = any(kw in name for kw in allowed_generic)
        is_dec = any(kw in name for kw in decorative_keywords)

        # Check if implies native Webflow widgets
        is_native_widget = False
        native_widgets = ["w-nav", "w-slider", "w-tabs", "w-dropdown", "w-lightbox", "w-form", "w-input", "w-button"]
        matched_widget = None
        for nw in native_widgets:
            if nw in name:
                is_native_widget = True
                matched_widget = nw
                break

        # Check if generic words are present
        has_generic_wrapper = "Frame" in name or "Group" in name
        has_generic_shape = "Rectangle" in name or "Ellipse" in name or "Circle" in name or "Vector" in name or "Line" in name

        if is_native_widget:
            issue = {
                "dataName": name,
                "reason": f"Figma layer name implies native Webflow widget behavior '{matched_widget}' which is not allowed in this semantic HTML pass.",
                "suggestedRename": name.replace(matched_widget, matched_widget.replace("w-", ""))
            }
            if args.mode == "strict":
                report["criticalIssues"].append(issue)
            elif args.mode == "warn":
                report["warnings"].append(issue)
            else:
                report["ignored"].append(issue)

        elif has_generic_wrapper and not is_critical and not is_layout:
            suggested = name.split("/")[-1].strip().lower().replace(" ", "_")
            if not suggested or "frame" in suggested or "group" in suggested:
                suggested = "content_wrapper"
            
            issue = {
                "dataName": name,
                "reason": "Generic wrapper name (Frame/Group) detected with no layout/semantic keyword.",
                "suggestedRename": suggested
            }
            
            if args.mode == "strict":
                report["criticalIssues"].append(issue)
            elif args.mode == "warn":
                report["warnings"].append(issue)
            else:
                report["ignored"].append(issue)

        elif has_generic_shape and not is_critical and not is_dec:
            issue = {
                "dataName": name,
                "reason": "Generic shape/vector layer detected without decorative keyword.",
                "suggestedRename": "background_decoration"
            }
            if args.mode == "strict":
                report["criticalIssues"].append(issue)
            elif args.mode == "warn":
                report["warnings"].append(issue)
            else:
                report["ignored"].append(issue)
        else:
            # Fully compliant
            pass

    # Update summary counts
    report["summary"]["criticalIssues"] = len(report["criticalIssues"])
    report["summary"]["warnings"] = len(report["warnings"])
    report["summary"]["ignored"] = len(report["ignored"])

    # Determine final verdict
    if report["summary"]["criticalIssues"] > 0:
        report["status"] = "failed"
        txt_msg = f"Validation FAILED: Found {report['summary']['criticalIssues']} critical issue(s) under '{args.mode}' mode.\n"
        for issue in report["criticalIssues"]:
            if isinstance(issue, dict):
                txt_msg += f"- '{issue['dataName']}': {issue['reason']} (Try renaming to: '{issue['suggestedRename']}')\n"
            else:
                txt_msg += f"- {issue}\n"
    else:
        report["status"] = "passed"
        txt_msg = "Validation PASSED: HTML layer names comply with the rules.\n"
        if report["warnings"]:
            txt_msg += f"Warnings found ({len(report['warnings'])}):\n"
            for w in report["warnings"]:
                txt_msg += f"- '{w['dataName']}': {w['reason']} (Recommended name: '{w['suggestedRename']}')\n"

    print(txt_msg)

    # Save reports
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    report_txt_path.write_text(txt_msg, encoding="utf-8")

    if report["status"] == "failed":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
