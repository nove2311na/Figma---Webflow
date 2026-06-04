#!/usr/bin/env python3
import json
import subprocess
import shutil
import unittest
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
WORKSPACE_DIR = Path("workspace/test-sync-workspace")

class TestDesignSystemSync(unittest.TestCase):
    def setUp(self):
        # Create fresh test workspace
        WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        self.ds_dir = WORKSPACE_DIR / "design-system"
        self.ds_dir.mkdir(parents=True, exist_ok=True)
        self.figma_contract = self.ds_dir / "figma-contract.json"
        
        # Load correct template as base
        self.template_path = BASE_DIR / "template" / "figma-design-system-contract.json"
        with open(self.template_path, "r", encoding="utf-8") as f:
            self.valid_template = json.load(f)

    def tearDown(self):
        # Clean up test workspace
        if WORKSPACE_DIR.exists():
            shutil.rmtree(WORKSPACE_DIR)

    def test_validation_passed_happy_path(self):
        # Save valid figma contract
        data = json.loads(json.dumps(self.valid_template))
        # Remove placeholders recursively and fill realistic types
        for v_name, v_meta in data.get("variables", {}).items():
            v_type = v_meta.get("type")
            if v_type == "color":
                v_meta["value"] = "#ffffff"
                v_meta["resolvedValue"] = "#ffffff"
            elif v_type in ["size", "number", "font-weight", "letter-spacing"]:
                v_meta["value"] = 16
                v_meta["resolvedValue"] = 16
            elif v_type == "font-family":
                v_meta["value"] = "Inter"
                v_meta["resolvedValue"] = "Inter"
                
        self.figma_contract.write_text(json.dumps(data), encoding="utf-8")

        # Run validate_figma_extraction.py
        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "validate_figma_extraction.py"),
            "--workspace", "test-sync-workspace",
            "--guide", str(BASE_DIR / "references" / ".user-figma-setup.md"),
            "--schema", str(BASE_DIR / "schema" / "figma-design-system-contract.schema.json")
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        
        # Verify JSON report was created
        report_path = self.ds_dir / "validations" / "validation_report.json"
        self.assertTrue(report_path.exists())
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "passed")

    def test_validation_failed_missing_required(self):
        # Missing variables
        data = {
            "meta": self.valid_template["meta"],
            "variables": {},
            "styles": {}
        }
        self.figma_contract.write_text(json.dumps(data), encoding="utf-8")

        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "validate_figma_extraction.py"),
            "--workspace", "test-sync-workspace"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 1)
        
        report_path = self.ds_dir / "validations" / "validation_report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "failed")
        self.assertGreater(report["summary"]["missingRequiredVariables"], 0)

    def test_validation_failed_placeholder_value(self):
        # Fill variables but inject one "[VALUE]" placeholder
        data = json.loads(json.dumps(self.valid_template))
        for v_name, v_meta in data.get("variables", {}).items():
            v_type = v_meta.get("type")
            if v_type == "color":
                v_meta["value"] = "#ffffff"
            else:
                v_meta["value"] = 16
        
        # Inject placeholder
        first_var = list(data["variables"].keys())[0]
        data["variables"][first_var]["value"] = "[VALUE]"
        
        self.figma_contract.write_text(json.dumps(data), encoding="utf-8")

        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "validate_figma_extraction.py"),
            "--workspace", "test-sync-workspace"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 1)
        
        report_path = self.ds_dir / "validations" / "validation_report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "failed")
        self.assertGreater(report["summary"]["placeholdersFound"], 0)

    def test_map_variables_happy_path(self):
        # 1. Prepare valid figma contract
        data = json.loads(json.dumps(self.valid_template))
        for v_name, v_meta in data.get("variables", {}).items():
            v_type = v_meta.get("type")
            if v_type == "color":
                v_meta["value"] = "#ffffff"
            else:
                v_meta["value"] = 16
        self.figma_contract.write_text(json.dumps(data), encoding="utf-8")

        # 2. Run map_variables.py
        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "map_variables.py"),
            "--workspace", "test-sync-workspace",
            "--input", str(self.figma_contract),
            "--output", str(self.ds_dir / "webflow-contract.json"),
            "--mapping", str(BASE_DIR / "references" / "figma-webflow-mapping.md"),
            "--report", str(self.ds_dir / "validations" / "mapping-report.json")
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        
        # Verify Webflow contract is generated
        wf_contract_path = self.ds_dir / "webflow-contract.json"
        self.assertTrue(wf_contract_path.exists())
        
        wf_data = json.loads(wf_contract_path.read_text(encoding="utf-8"))
        self.assertIn("--_layout---gaps--large", wf_data["variables"])
        self.assertIn("heading-style-h1", wf_data["styles"])

    def test_extract_baseline_pure_native_fails(self):
        # Pure native Webflow CSS
        native_css = """
        .w-button { color: red; }
        .w-nav { display: block; }
        html { margin: 0; }
        """
        css_file = self.ds_dir / "native.css"
        css_file.write_text(native_css, encoding="utf-8")
        out_contract = self.ds_dir / "native-baseline.json"
        out_report = self.ds_dir / "validations" / "native-report.json"

        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "extract_client_first_baseline.py"),
            "--input-css", str(css_file),
            "--output-contract", str(out_contract),
            "--report", str(out_report),
            "--strict"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("NO_CLIENT_FIRST_BASELINE_FOUND", result.stdout)

    def test_extract_baseline_happy_path_passes(self):
        # Client-first baseline CSS
        cf_css = """
        :root {
            --brand--blue: #0000ff;
            --_layout---gaps--large: 24px;
        }
        .heading-style-h1 {
            font-size: 3rem;
            line-height: 1.2;
        }
        .w-button {
            background-color: blue;
        }
        """
        css_file = self.ds_dir / "cf.css"
        css_file.write_text(cf_css, encoding="utf-8")
        out_contract = self.ds_dir / "cf-baseline.json"
        out_report = self.ds_dir / "validations" / "cf-report.json"

        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "extract_client_first_baseline.py"),
            "--input-css", str(css_file),
            "--output-contract", str(out_contract),
            "--report", str(out_report),
            "--strict"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        self.assertTrue(out_contract.exists())
        
        contract_data = json.loads(out_contract.read_text(encoding="utf-8"))
        self.assertIn("--brand--blue", contract_data["variables"])
        self.assertIn("heading-style-h1", contract_data["classes"])
        # w-button should be in excluded
        self.assertIn(".w-button", contract_data["excluded"]["webflowNativeSelectors"])

    def test_mapping_native_webflow_fails(self):
        # Create baseline with excluded w-button
        baseline_data = {
            "meta": {"schemaVersion": "1.0.0", "source": "test", "baseline": "test", "scope": "client-first-only", "generatedAt": "2026-06-04T00:00:00Z"},
            "variables": {},
            "classes": {},
            "excluded": {
                "webflowNativeSelectors": [".w-button"],
                "nativeElementSelectors": ["h1"],
                "unsupportedSelectors": []
            }
        }
        baseline_file = self.ds_dir / "test-baseline.json"
        baseline_file.write_text(json.dumps(baseline_data), encoding="utf-8")

        # Figma contract mapping a style to w-button
        figma_data = {
            "meta": self.valid_template["meta"],
            "variables": {},
            "styles": {
                "Heading 1": {
                    "type": "text-style",
                    "mode": "default",
                    "properties": {
                        "font-family": "Inter",
                        "font-size": {"value": 32, "unit": "px"},
                        "font-weight": 700,
                        "line-height": {"value": 40, "unit": "px"}
                    }
                }
            }
        }
        self.figma_contract.write_text(json.dumps(figma_data), encoding="utf-8")

        # Mapping file mapping Heading 1 to .w-button
        mapping_content = """
        ## Class Mapping
        | Figma Style | Webflow Class |
        | `Heading 1` | `w-button` |
        """
        mapping_file = self.ds_dir / "test-mapping.md"
        mapping_file.write_text(mapping_content, encoding="utf-8")

        # Run map_variables.py and expect failure
        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "map_variables.py"),
            "--workspace", "test-sync-workspace",
            "--input", str(self.figma_contract),
            "--output", str(self.ds_dir / "webflow-contract.json"),
            "--mapping", str(mapping_file),
            "--report", str(self.ds_dir / "validations" / "mapping-report.json"),
            "--baseline", str(baseline_file),
            "--strict"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("maps to Webflow native selector", result.stdout)

    def test_mapping_valid_class_passes(self):
        # Create baseline with heading-style-h1
        baseline_data = {
            "meta": {"schemaVersion": "1.0.0", "source": "test", "baseline": "test", "scope": "client-first-only", "generatedAt": "2026-06-04T00:00:00Z"},
            "variables": {},
            "classes": {
                "heading-style-h1": {
                    "selector": ".heading-style-h1",
                    "type": "text-style",
                    "category": "typography",
                    "properties": {
                        "font-size": "32px"
                    },
                    "breakpoints": {"main": {}, "medium": {}, "small": {}, "tiny": {}},
                    "pseudoStates": {},
                    "editableInFigma": True,
                    "syncPolicy": "figma"
                }
            },
            "excluded": {
                "webflowNativeSelectors": [],
                "nativeElementSelectors": [],
                "unsupportedSelectors": []
            }
        }
        baseline_file = self.ds_dir / "test-baseline.json"
        baseline_file.write_text(json.dumps(baseline_data), encoding="utf-8")

        # Figma contract mapping a style to heading-style-h1
        figma_data = {
            "meta": self.valid_template["meta"],
            "variables": {},
            "styles": {
                "Heading 1": {
                    "type": "text-style",
                    "mode": "default",
                    "properties": {
                        "font-family": "Inter",
                        "font-size": {"value": 32, "unit": "px"},
                        "font-weight": 700,
                        "line-height": {"value": 40, "unit": "px"}
                    }
                }
            }
        }
        self.figma_contract.write_text(json.dumps(figma_data), encoding="utf-8")

        # Mapping file mapping Heading 1 to heading-style-h1
        mapping_content = """
        ## Class Mapping
        | Figma Style | Webflow Class |
        | `Heading 1` | `heading-style-h1` |
        """
        mapping_file = self.ds_dir / "test-mapping.md"
        mapping_file.write_text(mapping_content, encoding="utf-8")

        # Run map_variables.py and expect success
        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "map_variables.py"),
            "--workspace", "test-sync-workspace",
            "--input", str(self.figma_contract),
            "--output", str(self.ds_dir / "webflow-contract.json"),
            "--mapping", str(mapping_file),
            "--report", str(self.ds_dir / "validations" / "mapping-report.json"),
            "--baseline", str(baseline_file),
            "--strict"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        self.assertTrue((self.ds_dir / "webflow-contract.json").exists())

if __name__ == "__main__":
    unittest.main()
