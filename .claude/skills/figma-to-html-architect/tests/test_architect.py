#!/usr/bin/env python3
import json
import subprocess
import shutil
import unittest
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
WORKSPACE_DIR = Path("workspace/test-arch-workspace")

class TestHTMLArchitect(unittest.TestCase):
    def setUp(self):
        # Create fresh test workspace
        WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        self.comp_dir = WORKSPACE_DIR / "components" / "test-node"
        self.comp_dir.mkdir(parents=True, exist_ok=True)
        self.raw_html_path = self.comp_dir / "raw-figma.html"
        self.val_dir = self.comp_dir / "validations"
        self.val_dir.mkdir(parents=True, exist_ok=True)
        
        # We need a webflow contract for process_html to match classes
        self.ds_dir = WORKSPACE_DIR / "design-system"
        self.ds_dir.mkdir(parents=True, exist_ok=True)
        self.wf_contract_path = self.ds_dir / "webflow-contract.json"
        
        # Populate dummy webflow contract variables & styles for matching
        wf_contract = {
            "variables": {
                "--_typography---h1--h1-font-size": {
                    "value": "64px",
                    "resolvedValue": "64px"
                }
            },
            "styles": {
                "heading-style-h1": {
                    "type": "text-style",
                    "figmaStyleName": "Heading Style / H1",
                    "webflowClassName": "heading-style-h1",
                    "properties": {
                        "font-size": "var(--_typography---h1--h1-font-size)",
                        "font-weight": "700",
                        "line-height": "1.1em"
                    },
                    "matchPolicy": {
                        "strategy": "property_similarity",
                        "requiredProperties": ["font-size", "font-weight"],
                        "optionalProperties": ["line-height"],
                        "minimumConfidence": 0.85
                    }
                }
            }
        }
        self.wf_contract_path.write_text(json.dumps(wf_contract), encoding="utf-8")

    def tearDown(self):
        # Clean up test workspace
        if WORKSPACE_DIR.exists():
            shutil.rmtree(WORKSPACE_DIR)

    def test_validation_strict_fail_on_generic(self):
        # HTML with generic Frame name
        html = '<div data-name="Frame 101" data-node-id="1:2">Content</div>'
        self.raw_html_path.write_text(html, encoding="utf-8")

        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "validate_figma_html.py"),
            "--workspace", "test-arch-workspace",
            "--node-id", "test-node",
            "--mode", "strict"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 1)
        
        # Report must exist and show failure
        report_path = self.val_dir / "html_validation_report.json"
        self.assertTrue(report_path.exists())
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "failed")
        self.assertEqual(len(report["criticalIssues"]), 1)

    def test_validation_warn_pass_on_generic(self):
        # HTML with generic Frame name
        html = '<div data-name="Frame 101" data-node-id="1:2">Content</div>'
        self.raw_html_path.write_text(html, encoding="utf-8")

        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "validate_figma_html.py"),
            "--workspace", "test-arch-workspace",
            "--node-id", "test-node",
            "--mode", "warn"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        
        report_path = self.val_dir / "html_validation_report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "passed")
        self.assertEqual(len(report["warnings"]), 1)

    def test_validation_ignore_pass_silently(self):
        # Generic name is allowed layout wrapper or decorative
        html = '<div data-name="wrapper_container" data-node-id="1:2">Content</div>'
        self.raw_html_path.write_text(html, encoding="utf-8")

        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "validate_figma_html.py"),
            "--workspace", "test-arch-workspace",
            "--node-id", "test-node",
            "--mode", "strict"
        ], capture_output=True, text=True)

        # Should pass even in strict mode since wrapper is allowed generic keyword
        self.assertEqual(result.returncode, 0)

    def test_processing_happy_path(self):
        # Raw HTML with heading name and inline style
        html = '<div data-name="heading_h1" style="font-size: 64px; font-weight: 700; line-height: 1.1em;">Heading text</div>'
        self.raw_html_path.write_text(html, encoding="utf-8")

        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "process_html.py"),
            "--workspace", "test-arch-workspace",
            "--node-id", "test-node"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        
        final_html_path = self.comp_dir / "final-webflow.html"
        self.assertTrue(final_html_path.exists())
        
        final_html = final_html_path.read_text(encoding="utf-8")
        # Check that it converted div to h1 and injected CSS class while removing inline style
        self.assertIn("<h1", final_html)
        self.assertIn('class="heading-style-h1"', final_html)
        self.assertNotIn("style=", final_html) # Fully matched, style should be cleaned up

    def test_void_tags_no_closing(self):
        # Figma sometimes emits <img></img>, we want to normalize it
        html = '<div data-name="image_logo"><img data-name="image" src="logo.png"></img></div>'
        self.raw_html_path.write_text(html, encoding="utf-8")

        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "process_html.py"),
            "--workspace", "test-arch-workspace",
            "--node-id", "test-node"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        
        final_html = (self.comp_dir / "final-webflow.html").read_text(encoding="utf-8")
        self.assertIn('<img data-name="image" src="logo.png" alt="">', final_html)
        self.assertNotIn("</img>", final_html)

    def test_validation_widget_conflict_strict_fails(self):
        # Layer named w-nav is forbidden
        html = '<div data-name="w-nav" data-node-id="1:2">Nav content</div>'
        self.raw_html_path.write_text(html, encoding="utf-8")

        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "validate_figma_html.py"),
            "--workspace", "test-arch-workspace",
            "--node-id", "test-node",
            "--mode", "strict"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 1)
        report_path = self.val_dir / "html_validation_report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "failed")
        self.assertIn("implies native Webflow widget behavior", report["criticalIssues"][0]["reason"])

    def test_processing_no_native_auto_injection(self):
        # Prepare baseline with excluded w-button and h1 tag selectors
        baseline_data = {
            "meta": {"schemaVersion": "1.0.0", "source": "test", "baseline": "test", "scope": "client-first-only", "generatedAt": "2026-06-04T00:00:00Z"},
            "variables": {},
            "classes": {
                "w-button": {
                    "selector": ".w-button",
                    "properties": {
                        "color": "red"
                    }
                },
                "h1": {
                    "selector": "h1",
                    "properties": {
                        "font-size": "32px"
                    }
                }
            },
            "excluded": {
                "webflowNativeSelectors": [".w-button"],
                "nativeElementSelectors": ["h1"],
                "unsupportedSelectors": []
            }
        }
        baseline_file = self.ds_dir / "test-baseline.json"
        baseline_file.write_text(json.dumps(baseline_data), encoding="utf-8")

        # Also add them to the Webflow contract to simulate them being in the stylesheet
        wf_contract = {
            "variables": {},
            "styles": {
                "w-button": {
                    "webflowClassName": "w-button",
                    "properties": {
                        "color": "red"
                    }
                },
                "h1": {
                    "webflowClassName": "h1",
                    "properties": {
                        "font-size": "32px"
                    }
                }
            }
        }
        self.wf_contract_path.write_text(json.dumps(wf_contract), encoding="utf-8")

        # HTML with matching style attributes
        html = '<div data-name="test-div" style="color: red; font-size: 32px;">Some text</div>'
        self.raw_html_path.write_text(html, encoding="utf-8")

        result = subprocess.run([
            "python", str(SCRIPTS_DIR / "process_html.py"),
            "--workspace", "test-arch-workspace",
            "--node-id", "test-node",
            "--baseline", str(baseline_file)
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        
        final_html = (self.comp_dir / "final-webflow.html").read_text(encoding="utf-8")
        # Should NOT automatically match w-button class or h1 class since they are native/excluded
        self.assertNotIn("w-button", final_html)
        self.assertNotIn("h1", final_html)

if __name__ == "__main__":
    unittest.main()
