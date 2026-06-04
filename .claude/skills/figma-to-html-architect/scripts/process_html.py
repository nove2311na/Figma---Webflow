#!/usr/bin/env python3
import argparse
import sys
import json
import re
from pathlib import Path
from html.parser import HTMLParser

# Make the shared module importable when this script is run from any cwd.
_SKILLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(_SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILLS_DIR))
from _shared.selector_guards import is_native_selector, is_html_tag_selector  # noqa: E402

PIXELS_PER_REM = 16
_ALLOWED_UNITS = ("PIXELS", "PX", "REM", "PERCENT", "%")

VOID_TAGS = {
    "img", "input", "br", "hr", "meta", "link", "source", 
    "area", "base", "col", "embed", "param", "track", "wbr"
}

def parse_num_unit(val):
    if not val: return None
    val = str(val).strip()
    # Handle negative values as well
    m = re.match(r"^(-?[\d\.]+)([a-zA-Z%]*)$", val)
    if m:
        try:
            return float(m.group(1)), m.group(2).lower()
        except ValueError:
            return None
    return None

def normalize_style_dict(style_str):
    if not style_str: return {}
    style_dict = {}
    for part in style_str.split(';'):
        if ':' in part:
            k, v = part.split(':', 1)
            k = k.strip().lower()
            v = v.strip()
            if v.startswith("#"):
                v = v.lower()
            if k == "font-family":
                v = v.replace('"', '').replace("'", "")
            style_dict[k] = v
    return style_dict

def resolve_variable(val, variables):
    val = str(val).strip()
    if val.startswith("var(") and val.endswith(")"):
        var_name = val[4:-1].strip()
        if var_name in variables:
            var_meta = variables[var_name]
            var_val = var_meta.get("value")
            # If size unit is present, normalize per CLAUDE.md: REM mandate
            if isinstance(var_val, dict) and "value" in var_val and "unit" in var_val:
                raw_unit = str(var_val["unit"]).upper()
                if raw_unit in ("PIXELS", "PX"):
                    try:
                        px = float(var_val["value"])
                        rem = px / PIXELS_PER_REM
                        rem_str = f"{rem:.4f}".rstrip("0").rstrip(".")
                        return f"{rem_str}rem"
                    except (TypeError, ValueError):
                        return f"{var_val['value']}{var_val['unit']}"
                if raw_unit == "REM":
                    return f"{var_val['value']}rem"
                if raw_unit in ("PERCENT", "%"):
                    return f"{var_val['value']}%"
                raise ValueError(
                    f"Unsupported unit '{var_val['unit']}' on Figma variable "
                    f"'{var_name}'. CLAUDE.md mandates REM for spacing/typography. "
                    f"Allowed units: px, rem, %."
                )
            elif var_val is not None:
                return str(var_val)
        return var_name
    return val

def values_match(html_val, contract_val, variables):
    if html_val == contract_val:
        return True
        
    html_resolved = resolve_variable(html_val, variables)
    contract_resolved = resolve_variable(contract_val, variables)
    
    if html_resolved.lower() == contract_resolved.lower():
        return True
        
    # Compare parsed numeric values
    p_html = parse_num_unit(html_resolved)
    p_contract = parse_num_unit(contract_resolved)
    
    if p_html and p_contract:
        h_num, h_unit = p_html
        c_num, c_unit = p_contract
        
        # If units match, or if line-height compared (where unit might be em vs empty)
        if h_unit == c_unit or h_unit == "" or c_unit == "":
            if abs(h_num - c_num) < 0.01:
                return True
                
    return False

class FigmaHTMLRewriter(HTMLParser):
    def __init__(self, semantic_rules, webflow_contract, baseline_contract=None):
        super().__init__()
        self.rules = semantic_rules.get("rules", {})
        self.allowed_generic = semantic_rules.get("allowedGenericKeywords", [])
        self.decorative_keywords = semantic_rules.get("decorativeKeywords", [])
        
        self.variables = webflow_contract.get("variables", {})
        
        # Load baseline classes if available
        self.classes = {}
        baseline_excluded = {}
        if baseline_contract:
            baseline_excluded = baseline_contract.get("excluded", {})
            for cname, c_meta in baseline_contract.get("classes", {}).items():
                clean_name = cname[1:] if cname.startswith(".") else cname
                # Ensure we have a default matchPolicy if not provided
                if "matchPolicy" not in c_meta:
                    props_list = list(c_meta.get("properties", {}).keys())
                    c_meta["matchPolicy"] = {
                        "requiredProperties": props_list,
                        "optionalProperties": [],
                        "minimumConfidence": 0.85
                    }
                self.classes[clean_name] = c_meta
                
        # Overwrite/add with mapped webflow contract styles (which take precedence)
        for cname, c_meta in webflow_contract.get("styles", {}).items():
            clean_name = cname[1:] if cname.startswith(".") else cname
            self.classes[clean_name] = c_meta

        self.webflow_native = set(baseline_excluded.get("webflowNativeSelectors", []))
        self.native_elements = set(baseline_excluded.get("nativeElementSelectors", []))
        
        self.result = []
        self.tag_stack = []
        
        # Report variables
        self.report_nodes = 0
        self.report_semantic_changes = []
        self.report_classes_added = []
        self.report_styles_removed = []
        self.report_styles_preserved = []
        self.report_warnings = []

        # For accessibility heading sequence checks
        self.last_heading_level = 0

    def match_classes(self, style_dict):
        matched_classes = []
        properties_to_remove = set()

        for cname, c_meta in self.classes.items():
            # Block matching against Webflow native classes or HTML tag selectors
            if is_native_selector(cname, self.webflow_native) or is_html_tag_selector(cname, self.native_elements):
                continue

            c_props = c_meta.get("properties", {})
            match_policy = c_meta.get("matchPolicy", {})
            if not match_policy:
                props_list = list(c_props.keys())
                match_policy = {
                    "requiredProperties": props_list,
                    "optionalProperties": [],
                    "minimumConfidence": 0.85
                }
            
            req_props = match_policy.get("requiredProperties", [])
            opt_props = match_policy.get("optionalProperties", [])
            min_confidence = match_policy.get("minimumConfidence", 0.85)

            # Check required properties
            req_ok = True
            for rp in req_props:
                if rp not in style_dict or rp not in c_props:
                    req_ok = False
                    break
                if not values_match(style_dict[rp], c_props[rp], self.variables):
                    req_ok = False
                    break
            
            if not req_ok:
                continue

            # Compute confidence score
            # Intersection of contract properties and HTML style properties
            all_contract_props = set(c_props.keys())
            html_present_props = all_contract_props.intersection(set(style_dict.keys()))
            
            if not html_present_props:
                continue
                
            matched_count = 0
            for p in html_present_props:
                if values_match(style_dict[p], c_props[p], self.variables):
                    matched_count += 1
            
            confidence = matched_count / len(html_present_props)
            
            if confidence >= min_confidence:
                matched_classes.append({
                    "class": cname,
                    "confidence": confidence,
                    "matched_props": list(html_present_props)
                })
                # Add matched properties to the removal list
                for p in html_present_props:
                    if values_match(style_dict[p], c_props[p], self.variables):
                        properties_to_remove.add(p)

        # Sort matches by confidence descending
        matched_classes.sort(key=lambda x: x["confidence"], reverse=True)
        return [m["class"] for m in matched_classes], list(properties_to_remove)

    def resolve_semantic_tag(self, tag, data_name):
        # Sort rules by priority descending
        sorted_rules = sorted(self.rules.items(), key=lambda x: x[1].get("priority", 0), reverse=True)
        
        for keyword, r_meta in sorted_rules:
            match_mode = r_meta.get("match", "contains")
            matched = False
            
            if match_mode == "exact" and keyword == data_name:
                matched = True
            elif match_mode == "contains" and keyword in data_name:
                matched = True
                
            if matched:
                return r_meta
        return None

    def merge_classes_preserve_order(self, existing_classes, new_classes):
        # Preserve natural order: existing first, then new
        seen = set()
        result = []
        for cls in existing_classes + new_classes:
            if cls and cls not in seen:
                result.append(cls)
                seen.add(cls)
        return result

    def check_accessibility(self, tag, attr_dict):
        # Heading level validation
        m = re.match(r"^h([1-6])$", tag)
        if m:
            level = int(m.group(1))
            if self.last_heading_level > 0 and level > self.last_heading_level + 1:
                self.report_warnings.append(
                    f"Accessibility warning: Heading levels skipped from H{self.last_heading_level} to H{level}."
                )
            self.last_heading_level = level

        if tag == "img" and "alt" not in attr_dict:
            attr_dict["alt"] = ""
            self.report_warnings.append("Accessibility patch: Added missing alt=\"\" attribute to img tag.")
        
        if tag == "button" and "type" not in attr_dict:
            attr_dict["type"] = "button"
            
        if tag == "a" and "href" not in attr_dict:
            self.report_warnings.append("Accessibility warning: Link tag <a> is missing an href attribute.")

        if tag == "input" and "name" not in attr_dict:
            self.report_warnings.append("Accessibility warning: Form <input> tag is missing a name attribute.")

    def handle_starttag(self, tag, attrs):
        self.report_nodes += 1
        attr_dict = dict(attrs)
        data_name = attr_dict.get("data-name", "")
        
        # 1. Semantic Tag Resolution
        new_tag = tag
        rule_applied = self.resolve_semantic_tag(tag, data_name)
        if rule_applied:
            new_tag = rule_applied["tag"]
            # Inject default attributes
            for k, v in rule_applied.get("attributes", {}).items():
                attr_dict[k] = v
            self.report_semantic_changes.append({
                "dataName": data_name,
                "originalTag": tag,
                "newTag": new_tag,
                "confidence": rule_applied.get("confidence", 1.0)
            })

        # 2. CSS Class Resolution
        style_str = attr_dict.get("style", "")
        if style_str:
            style_dict = normalize_style_dict(style_str)
            matched_classes, covered_props = self.match_classes(style_dict)
            
            if matched_classes:
                existing_class_str = attr_dict.get("class", "")
                existing_classes = existing_class_str.split()
                merged = self.merge_classes_preserve_order(existing_classes, matched_classes)
                attr_dict["class"] = " ".join(merged)
                
                # Report
                self.report_classes_added.append({
                    "dataName": data_name,
                    "classes": matched_classes
                })
                
                # Cleanup covered properties
                for cp in covered_props:
                    if cp in style_dict:
                        self.report_styles_removed.append(f"{cp}: {style_dict[cp]}")
                        del style_dict[cp]
            
            # Rebuild remaining style
            if style_dict:
                attr_dict["style"] = "; ".join(f"{k}: {v}" for k, v in style_dict.items())
                self.report_styles_preserved.extend(style_dict.keys())
            else:
                if "style" in attr_dict:
                    del attr_dict["style"]

        # 3. Accessibility Checks
        self.check_accessibility(new_tag, attr_dict)

        # Re-build output string
        attrs_str = ""
        for k, v in attr_dict.items():
            if v is None or v == "":
                # For boolean attributes or empty values (like alt="")
                if k == "alt":
                    attrs_str += ' alt=""'
                else:
                    attrs_str += f' {k}'
            else:
                attrs_str += f' {k}="{v}"'

        self.tag_stack.append((tag, new_tag))
        
        # Check if void tag
        if new_tag in VOID_TAGS:
            self.result.append(f"<{new_tag}{attrs_str}>")
        else:
            self.result.append(f"<{new_tag}{attrs_str}>")

    def handle_endtag(self, tag):
        if self.tag_stack:
            orig_tag, new_tag = self.tag_stack.pop()
            # If it is a void tag, we DO NOT output the closing tag
            if new_tag not in VOID_TAGS:
                self.result.append(f"</{new_tag}>")
        else:
            if tag not in VOID_TAGS:
                self.result.append(f"</{tag}>")

    def handle_data(self, data):
        self.result.append(data)
        
    def handle_entityref(self, name):
        self.result.append(f"&{name};")
        
    def handle_charref(self, name):
        self.result.append(f"&#{name};")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--baseline", help="Path to client-first-baseline-contract.json")
    args = parser.parse_args()

    # Paths
    raw_html_path = Path(f"workspace/{args.workspace}/components/{args.node_id}/raw-figma.html")
    out_html_path = Path(f"workspace/{args.workspace}/components/{args.node_id}/final-webflow.html")
    val_dir = Path(f"workspace/{args.workspace}/components/{args.node_id}/validations")
    val_dir.mkdir(parents=True, exist_ok=True)
    report_json_path = val_dir / "html_processing_report.json"

    mapping_path = Path(".claude/skills/figma-to-html-architect/references/html-semantic-mapping.json")
    css_contract_path = Path(f"workspace/{args.workspace}/design-system/webflow-contract.json")
    baseline_path = Path(args.baseline) if args.baseline else Path(f"workspace/{args.workspace}/design-system/client-first-baseline-contract.json")

    if not raw_html_path.exists():
        print(f"Error: Raw HTML not found at {raw_html_path}")
        sys.exit(1)

    html_content = raw_html_path.read_text(encoding="utf-8")

    # Load mapping rules
    try:
        with open(mapping_path, "r", encoding="utf-8") as f:
            semantic_rules = json.load(f)
    except Exception as e:
        print(f"Error loading semantic mapping rules: {e}")
        sys.exit(1)

    # Load Webflow design system contract
    try:
        with open(css_contract_path, "r", encoding="utf-8") as f:
            webflow_contract = json.load(f)
    except Exception as e:
        print(f"Warning: Webflow contract not found or invalid ({e}). Proceeding without CSS mapping.")
        webflow_contract = {}

    # Load baseline contract
    baseline_contract = None
    if baseline_path.exists():
        try:
            with open(baseline_path, "r", encoding="utf-8") as f:
                baseline_contract = json.load(f)
        except Exception as e:
            print(f"Warning: Baseline contract at {baseline_path} could not be loaded ({e}).")

    # Run Parser
    rewriter = FigmaHTMLRewriter(semantic_rules, webflow_contract, baseline_contract)
    rewriter.feed(html_content)
    
    final_html = "".join(rewriter.result)

    # Save output HTML
    out_html_path.parent.mkdir(parents=True, exist_ok=True)
    out_html_path.write_text(final_html, encoding="utf-8")

    # Construct and save processing report
    report = {
        "status": "passed_with_warnings" if rewriter.report_warnings else "passed",
        "summary": {
            "nodesProcessed": rewriter.report_nodes,
            "semanticTagsChanged": len(rewriter.report_semantic_changes),
            "classesAdded": len(rewriter.report_classes_added),
            "inlineStylesRemoved": len(rewriter.report_styles_removed),
            "inlineStylesPreserved": len(rewriter.report_styles_preserved),
            "accessibilityWarnings": len(rewriter.report_warnings)
        },
        "semanticMappings": rewriter.report_semantic_changes,
        "classMappings": rewriter.report_classes_added,
        "warnings": rewriter.report_warnings,
        "errors": []
    }

    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"HTML Processing complete. Report saved to {report_json_path}")
    sys.exit(0)

if __name__ == "__main__":
    main()
