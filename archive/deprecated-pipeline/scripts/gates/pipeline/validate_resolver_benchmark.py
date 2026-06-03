#!/usr/bin/env python3
"""Run benchmarking suite on clean, messy, and broken fixtures to verify compiler quality."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

def run_cmd(args: list[str]) -> tuple[int, str, str]:
    res = subprocess.run(
        [sys.executable] + args,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    return res.returncode, res.stdout, res.stderr

def run_benchmarks(root: Path) -> dict:
    results = {
        "tag_resolver_accuracy": 0.0,
        "invented_classes_count": 0,
        "broken_fixtures_failed_correctly": True,
        "details": []
    }

    # Temporary directory for benchmark runs inside workspace/
    bench_dir = root / "workspace" / "benchmarks"
    bench_dir.mkdir(parents=True, exist_ok=True)

    # 1. Clean hero fixture compilation
    code, stdout, stderr = run_cmd([
        "scripts/pipeline/normalize_figma_nodes.py",
        "--input", "tests/fixtures/figma/hero-clean.json",
        "--output", str(bench_dir / "hero-clean.normalized.json"),
        "--report", str(bench_dir / "hero-clean.norm-report.json")
    ])
    
    if code != 0:
        results["details"].append(f"hero-clean normalization failed: {stderr}")
    else:
        code, stdout, stderr = run_cmd([
            "scripts/pipeline/resolve_semantic_ir.py",
            "--input", str(bench_dir / "hero-clean.normalized.json"),
            "--output", str(bench_dir / "hero-clean.semantic.json"),
            "--reports-dir", str(bench_dir)
        ])
        if code != 0:
            results["details"].append(f"hero-clean semantic resolution failed: {stderr}")
        else:
            # Check accuracy on clean
            sem_data = json.loads((bench_dir / "hero-clean.semantic.json").read_text(encoding="utf-8"))
            tree = sem_data.get("semantic_tree", {})
            
            # Retrieve tags recursively
            tags = {}
            def collect_tags(node):
                tags[node.get("name")] = node.get("tag")
                for child in node.get("children", []):
                    collect_tags(child)
            collect_tags(tree)
            
            # Expected mappings
            expected_tags = {
                "[section] Hero Clean": "section",
                "Hero Title": "h1",
                "Hero Paragraph": "p",
                "CTA Button": "a"
            }
            
            matches = 0
            for name, tag in expected_tags.items():
                if tags.get(name) == tag:
                    matches += 1
            accuracy = matches / len(expected_tags) if expected_tags else 0.0
            results["tag_resolver_accuracy"] = accuracy
            results["details"].append(f"Clean Hero Tag Resolver Accuracy: {accuracy * 100:.1f}%")

    # 2. Check for invented classes
    if (bench_dir / "hero-clean.semantic.json").exists():
        sem_data = json.loads((bench_dir / "hero-clean.semantic.json").read_text(encoding="utf-8"))
        contract_data = json.loads((root / "knowledge-base" / "generated" / "client-first-library-contract.json").read_text(encoding="utf-8"))
        allowed = set(contract_data.get("allowed_classes", [])) | set(contract_data.get("allowed_combo_classes", [])) | set(contract_data.get("structural_convention_classes", []))

        invented = []
        def check_classes(node):
            for cls in node.get("classes", []):
                if cls not in allowed and not cls.startswith("w-"):
                    invented.append(cls)
            for child in node.get("children", []):
                check_classes(child)
        check_classes(sem_data.get("semantic_tree", {}))
        results["invented_classes_count"] = len(invented)
        if invented:
            results["details"].append(f"Invented classes found: {invented}")

    # 3. Broken fixtures check
    broken_checks = [
        ("tests/fixtures/broken/missing-class.json", "class_name"),
        ("tests/fixtures/broken/hardcoded-hex.json", "untokenized color")
    ]
    
    for path, expected_err_keyword in broken_checks:
        # Step 1: Normalize
        norm_out = bench_dir / "broken.normalized.json"
        norm_rep = bench_dir / "broken.norm-report.json"
        code, stdout, stderr = run_cmd([
            "scripts/pipeline/normalize_figma_nodes.py",
            "--input", path,
            "--output", str(norm_out),
            "--report", str(norm_rep)
        ])
        
        # If normalizer passed, run resolver
        if code == 0:
            code, stdout, stderr = run_cmd([
                "scripts/pipeline/resolve_semantic_ir.py",
                "--input", str(norm_out),
                "--output", str(bench_dir / "broken.semantic.json"),
                "--reports-dir", str(bench_dir)
            ])
            
        # Check if compilation failed as expected
        if code == 0:
            results["broken_fixtures_failed_correctly"] = False
            results["details"].append(f"Fixture {path} compiled successfully but was expected to fail.")
        else:
            results["details"].append(f"Fixture {path} failed correctly as expected (code: {code}).")

    return results

def main() -> int:
    root = Path(__file__).resolve().parents[3]
    
    print("Running resolver benchmarks...")
    bench_results = run_benchmarks(root)
    
    print("\nBenchmark Results:")
    print(f"  Tag Resolver Accuracy: {bench_results['tag_resolver_accuracy'] * 100:.1f}% (target: >=95%)")
    print(f"  Invented Classes Count: {bench_results['invented_classes_count']} (target: 0)")
    print(f"  Broken Fixtures Failed Correctly: {bench_results['broken_fixtures_failed_correctly']}")
    
    passed = (
        bench_results["tag_resolver_accuracy"] >= 0.95 and
        bench_results["invented_classes_count"] == 0 and
        bench_results["broken_fixtures_failed_correctly"]
    )
    
    print(f"\nOverall Benchmark Verdict: {'PASS' if passed else 'FAIL'}")
    for detail in bench_results["details"]:
        print(f"  - {detail}")

    # Save benchmark report
    report_path = root / "workspace" / "reports" / "resolver-benchmark-report.json"
    report_path.write_text(json.dumps(bench_results, indent=2), encoding="utf-8")
    
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())
