import re
import hashlib
import tinycss2

class CSSParser:
    def __init__(self):
        pass

    @staticmethod
    def get_md5_hash(file_path):
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def parse_css_file(self, file_path):
        """
        Parses a CSS file and extracts rules, declarations, variables, classes, selectors, and media queries.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        rules = tinycss2.parse_stylesheet(css_content, skip_comments=True)
        
        extracted_data = {
            "classes": set(),
            "combo_classes": set(),
            "variables": {},  # var_name -> list of values with media scope
            "selectors": set(),
            "breakpoints": set(),
            "declarations": [] # list of (selector, property, value, media)
        }

        self._parse_rules(rules, extracted_data, media_query=None)
        return extracted_data

    def _parse_rules(self, rules, data, media_query=None):
        for rule in rules:
            if rule.type == "qualified-rule":
                # Parse selector
                selector_str = tinycss2.serialize(rule.prelude).strip()
                if not selector_str:
                    continue
                
                # Split by commas for multiple selectors
                selectors = [s.strip() for s in selector_str.split(",")]
                for sel in selectors:
                    data["selectors"].add(sel)
                    
                    # Extract classes and combo classes
                    # E.g. .button.is-secondary -> class 'button', combo 'is-secondary'
                    # E.g. .container-large -> class 'container-large'
                    # Split by space to get individual element selectors
                    parts = sel.split()
                    for part in parts:
                        # Extract all class sequences: .class1.class2
                        classes_in_part = re.findall(r"\.([a-zA-Z0-9_-]+)", part)
                        if classes_in_part:
                            # The first one is the main class
                            main_class = classes_in_part[0]
                            data["classes"].add(main_class)
                            # Subsequent ones in the same compounded selector are combo classes
                            for combo in classes_in_part[1:]:
                                data["combo_classes"].add(combo)

                # Parse declarations
                decls = tinycss2.parse_declaration_list(rule.content, skip_comments=True)
                for decl in decls:
                    if decl.type == "declaration":
                        prop_name = decl.name
                        prop_val = tinycss2.serialize(decl.value).strip()
                        
                        # Check if it is a CSS variable definition
                        if prop_name.startswith("--"):
                            if prop_name not in data["variables"]:
                                data["variables"][prop_name] = []
                            data["variables"][prop_name].append({
                                "value": prop_val,
                                "media": media_query
                            })
                        
                        for sel in selectors:
                            data["declarations"].append({
                                "selector": sel,
                                "property": prop_name,
                                "value": prop_val,
                                "media": media_query
                            })
                            
            elif rule.type == "at-rule" and rule.at_keyword == "media":
                media_str = tinycss2.serialize(rule.prelude).strip()
                data["breakpoints"].add(media_str)
                # Parse sub-rules recursively
                sub_rules = tinycss2.parse_rule_list(rule.content, skip_comments=True)
                self._parse_rules(sub_rules, data, media_query=media_str)
