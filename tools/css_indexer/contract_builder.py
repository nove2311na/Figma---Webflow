import os
import json
from tools.css_indexer.parser import CSSParser
from tools.css_indexer.classifier import CSSClassifier

class ContractBuilder:
    def __init__(self, normalize_path, webflow_path, client_first_path):
        self.normalize_path = normalize_path
        self.webflow_path = webflow_path
        self.client_first_path = client_first_path
        self.parser = CSSParser()

    def build(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
        # Parse files
        norm_data = self.parser.parse_css_file(self.normalize_path)
        webflow_data = self.parser.parse_css_file(self.webflow_path)
        cf_data = self.parser.parse_css_file(self.client_first_path)
        
        cf_hash = self.parser.get_md5_hash(self.client_first_path)
        
        # 1. Allowed Classes & Combo Classes (Client-First specific)
        allowed_classes = sorted(list(cf_data["classes"]))
        allowed_combo_classes = sorted(list(cf_data["combo_classes"]))
        allowed_variables = sorted(list(cf_data["variables"].keys()))
        allowed_selectors = sorted(list(cf_data["selectors"]))
        breakpoints = sorted(list(cf_data["breakpoints"]))
        
        # Webflow native reserved classes
        reserved_webflow_classes = sorted(list(webflow_data["classes"]))
        
        # Styleguide classes
        styleguide_only_classes = sorted([c for c in allowed_classes if CSSClassifier.classify_class(c) == "styleguide-only"])
        
        # 2. Build library contract JSON
        contract = {
            "version": "1.0.0",
            "source": {
                "normalize_css": self.normalize_path,
                "webflow_css": self.webflow_path,
                "client_first_css": self.client_first_path,
                "client_first_css_hash": cf_hash
            },
            "strict_mode": True,
            "allowed_classes": allowed_classes,
            "allowed_combo_classes": allowed_combo_classes,
            "allowed_variables": allowed_variables,
            "allowed_selectors": allowed_selectors,
            "breakpoints": breakpoints,
            "reserved_webflow_classes": reserved_webflow_classes,
            "styleguide_only_classes": styleguide_only_classes,
            "structural_convention_classes": ["page-wrapper", "main-wrapper"],
            "forbidden_in_final_html": ["fs-styleguide_*"],
            "invalid_until_contract_proves": ["button_component", "card_component", "hero_layout"]
        }
        
        # 3. Create indices
        
        # CSS Variable index
        all_variables = {}
        for source_data in [norm_data, webflow_data, cf_data]:
            for var_name, definitions in source_data["variables"].items():
                if var_name not in all_variables:
                    all_variables[var_name] = []
                all_variables[var_name].extend(definitions)
                
        # CSS Class Index
        class_index = {}
        for c in set(allowed_classes) | set(reserved_webflow_classes):
            class_index[c] = {
                "category": CSSClassifier.classify_class(c),
                "is_combo": False
            }
        for cc in allowed_combo_classes:
            class_index[cc] = {
                "category": "combo",
                "is_combo": True
            }
            
        # CSS Selector Index
        selector_index = {}
        for source_data in [norm_data, webflow_data, cf_data]:
            for decl in source_data["declarations"]:
                sel = decl["selector"]
                if sel not in selector_index:
                    selector_index[sel] = []
                selector_index[sel].append({
                    "property": decl["property"],
                    "value": decl["value"],
                    "media": decl["media"]
                })
                
        # Property Value Index
        property_value_index = {}
        for source_data in [norm_data, webflow_data, cf_data]:
            for decl in source_data["declarations"]:
                prop = decl["property"]
                if prop not in property_value_index:
                    property_value_index[prop] = []
                property_value_index[prop].append({
                    "selector": decl["selector"],
                    "value": decl["value"],
                    "media": decl["media"]
                })
                
        # Breakpoint Index
        breakpoint_index = {}
        for bp in breakpoints:
            breakpoint_index[bp] = []
        for source_data in [norm_data, webflow_data, cf_data]:
            for decl in source_data["declarations"]:
                media = decl["media"]
                if media:
                    if media not in breakpoint_index:
                        breakpoint_index[media] = []
                    breakpoint_index[media].append({
                        "selector": decl["selector"],
                        "property": decl["property"],
                        "value": decl["value"]
                    })
                    
        # Webflow Native Class Index
        webflow_native_index = {
            "version": "1.0.0",
            "reserved_classes": reserved_webflow_classes,
            "mappings": {}
        }
        for c in reserved_webflow_classes:
            webflow_native_index["mappings"][c] = {
                "is_reserved": True,
                "notes": "Webflow native engine structural class"
            }
            
        # Write JSONs
        files_to_write = {
            "client-first-library-contract.json": contract,
            "css-variable-index.json": all_variables,
            "css-class-index.json": class_index,
            "css-selector-index.json": selector_index,
            "css-property-value-index.json": property_value_index,
            "css-breakpoint-index.json": breakpoint_index,
            "webflow-native-class-index.json": webflow_native_index
        }
        
        for fname, data in files_to_write.items():
            path = os.path.join(output_dir, fname)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
        print(f"Contract and indices built successfully in {output_dir}")
