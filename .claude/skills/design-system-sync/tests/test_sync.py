import json
import shutil
import subprocess
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parents[2]
SCRIPTS_DIR = BASE_DIR / "scripts"
WORKSPACE_NAME = "test-sync-workspace"
WORKSPACE_DIR = REPO_ROOT / "workspace" / WORKSPACE_NAME


class TestDesignSystemSync(unittest.TestCase):
    def setUp(self):
        if WORKSPACE_DIR.exists():
            shutil.rmtree(WORKSPACE_DIR)
        self.ds_dir = WORKSPACE_DIR / "design-system"
        self.raw_dir = self.ds_dir / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)

        self.figma_template_path = BASE_DIR / "template" / "figma-design-system-contract.json"
        self.webflow_template_path = BASE_DIR / "template" / "webflow-design-system-contract.json"
        self.figma_template = json.loads(self.figma_template_path.read_text(encoding="utf-8"))

    def tearDown(self):
        if WORKSPACE_DIR.exists():
            shutil.rmtree(WORKSPACE_DIR)

    def write_complete_mcp_payload(self) -> Path:
        variables = {}
        for index, (name, entry) in enumerate(self.figma_template["variables"].items(), start=1):
            item = dict(entry)
            item["name"] = name
            item["figmaId"] = f"VariableID:real-variable-{index}:1"
            item["value"] = entry.get("value")
            item["resolvedValue"] = entry.get("resolvedValue", entry.get("value"))
            variables[name] = item

        styles = {}
        for index, (name, entry) in enumerate(self.figma_template["styles"].items(), start=1):
            item = dict(entry)
            item["name"] = name
            item["figmaId"] = f"VariableID:real-style-{index}:1"
            styles[name] = item

        payload_path = self.raw_dir / "figma-mcp-variable-defs.json"
        payload_path.write_text(json.dumps({"variables": variables, "styles": styles}), encoding="utf-8")
        return payload_path

    def test_build_figma_design_system_from_complete_mcp_payload(self):
        payload_path = self.write_complete_mcp_payload()

        result = subprocess.run(
            [
                "python",
                str(SCRIPTS_DIR / "build_figma_design_system.py"),
                "--workspace",
                WORKSPACE_NAME,
                "--input",
                str(payload_path),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        output_path = self.ds_dir / "figma-design-system.json"
        report_path = self.ds_dir / "validations" / "build-figma-design-system-report.json"
        self.assertTrue(output_path.exists())
        self.assertTrue(report_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "passed")
        built = json.loads(output_path.read_text(encoding="utf-8"))
        first_var = next(iter(built["variables"].values()))
        self.assertNotIn(":tpl-", first_var["figmaId"])

    def test_build_figma_design_system_fails_when_template_key_missing(self):
        payload_path = self.raw_dir / "figma-mcp-variable-defs.json"
        first_variable_name, first_variable = next(iter(self.figma_template["variables"].items()))
        first_style_name, first_style = next(iter(self.figma_template["styles"].items()))
        payload_path.write_text(
            json.dumps(
                {
                    "variables": {
                        first_variable_name: {
                            "name": first_variable_name,
                            "figmaId": "VariableID:partial-variable:1",
                            "value": first_variable.get("value"),
                            "resolvedValue": first_variable.get("resolvedValue", first_variable.get("value")),
                        }
                    },
                    "styles": {
                        first_style_name: {
                            "name": first_style_name,
                            "figmaId": "StyleID:partial-style",
                            "properties": first_style.get("properties", {}),
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                "python",
                str(SCRIPTS_DIR / "build_figma_design_system.py"),
                "--workspace",
                WORKSPACE_NAME,
                "--input",
                str(payload_path),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        report = json.loads((self.ds_dir / "validations" / "build-figma-design-system-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "failed")
        self.assertGreater(report["summary"]["missingVariables"], 0)
        self.assertFalse((self.ds_dir / "figma-design-system.json").exists())

    def test_build_figma_design_system_fails_when_mcp_input_shape_invalid(self):
        payload_path = self.raw_dir / "figma-mcp-variable-defs.json"
        payload_path.write_text(json.dumps({"variableCollections": []}), encoding="utf-8")

        result = subprocess.run(
            [
                "python",
                str(SCRIPTS_DIR / "build_figma_design_system.py"),
                "--workspace",
                WORKSPACE_NAME,
                "--input",
                str(payload_path),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        report = json.loads((self.ds_dir / "validations" / "build-figma-design-system-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "failed")
        self.assertGreater(report["summary"]["inputSchemaErrors"], 0)
        self.assertIn("inputSchemaErrors", report)
        self.assertFalse((self.ds_dir / "figma-design-system.json").exists())

    def test_validate_built_figma_design_system_passes(self):
        payload_path = self.write_complete_mcp_payload()
        build = subprocess.run(
            [
                "python",
                str(SCRIPTS_DIR / "build_figma_design_system.py"),
                "--workspace",
                WORKSPACE_NAME,
                "--input",
                str(payload_path),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)

        result = subprocess.run(
            [
                "python",
                str(SCRIPTS_DIR / "validate_figma_extraction.py"),
                "--workspace",
                WORKSPACE_NAME,
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        report = json.loads((self.ds_dir / "validations" / "validation_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "passed")

    def test_map_variables_with_small_template_passes(self):
        figma_data = {
            "meta": self.figma_template["meta"],
            "variables": {
                "Brand / Primary": {
                    "type": "color",
                    "value": "#112233",
                    "resolvedValue": "#112233",
                    "unit": None,
                    "mode": "default",
                    "collection": "Brand",
                    "aliasOf": None,
                    "name": "Brand / Primary",
                    "figmaId": "VariableID:brand-primary:1",
                    "namespace": "brand",
                    "modes": {"default": "#112233"},
                    "editableInFigma": True,
                    "projectExtension": False,
                }
            },
            "styles": {
                "Heading Style / H1": {
                    "type": "text-style",
                    "properties": {"font-size": {"value": 64, "unit": "px"}},
                    "mode": "default",
                    "name": "Heading Style / H1",
                    "figmaId": "VariableID:style-h1:1",
                    "figmaStyleName": "Heading Style / H1",
                    "category": "heading",
                }
            },
        }
        self.ds_dir.mkdir(parents=True, exist_ok=True)
        figma_path = self.ds_dir / "figma-design-system.json"
        figma_path.write_text(json.dumps(figma_data), encoding="utf-8")

        webflow_template = {
            "meta": {"schemaVersion": "1.0.0", "source": "webflow"},
            "variables": {
                "--brand--primary": {
                    "figmaName": "Brand / Primary",
                    "webflowName": "--brand--primary",
                    "type": "color",
                    "value": "#000000",
                    "resolvedValue": "#000000",
                    "unit": None,
                    "mode": "default",
                    "updatePolicy": "update_value_only",
                    "name": "--brand--primary",
                    "figmaId": "VariableID:tpl-brand-primary:1",
                    "namespace": "brand",
                    "modes": {"default": "#000000"},
                    "editableInFigma": True,
                    "projectExtension": False,
                }
            },
            "styles": {
                "heading-style-h1": {
                    "type": "text-style",
                    "figmaStyleName": "Heading Style / H1",
                    "webflowClassName": "heading-style-h1",
                    "properties": {"font-size": "64px"},
                    "breakpoints": {"main": {}},
                    "matchPolicy": {},
                    "name": "heading-style-h1",
                    "figmaId": "VariableID:tpl-style-h1:1",
                    "category": "heading",
                }
            },
        }
        webflow_template_path = self.ds_dir / "webflow-template.json"
        webflow_template_path.write_text(json.dumps(webflow_template), encoding="utf-8")

        mapping_path = self.ds_dir / "mapping.md"
        mapping_path.write_text(
            "\n".join(
                [
                    "# Test Mapping",
                    "## Variable Mapping",
                    "| Figma Variable | Webflow Variable |",
                    "|---|---|",
                    "| `Brand / Primary` | `--brand--primary` |",
                    "## Class Mapping",
                    "| Figma Style | Webflow Class |",
                    "|---|---|",
                    "| `Heading Style / H1` | `heading-style-h1` |",
                ]
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                "python",
                str(SCRIPTS_DIR / "map_variables.py"),
                "--workspace",
                WORKSPACE_NAME,
                "--input",
                str(figma_path),
                "--output",
                str(self.ds_dir / "webflow-design-system.json"),
                "--mapping",
                str(mapping_path),
                "--report",
                str(self.ds_dir / "validations" / "mapping-report.json"),
                "--webflow-template",
                str(webflow_template_path),
                "--strict",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        webflow_data = json.loads((self.ds_dir / "webflow-design-system.json").read_text(encoding="utf-8"))
        self.assertEqual(webflow_data["variables"]["--brand--primary"]["value"], "#112233")
        self.assertIn("heading-style-h1", webflow_data["styles"])


if __name__ == "__main__":
    unittest.main()
