#!/usr/bin/env python3
"""Validate Claude skill anatomy for the MAS workspace."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_RESOURCE_DIRS = ("references", "scripts", "assets")
REQUIRED_SECTIONS = ("## Use When", "## Workflow", "## Validation")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def validate_skill(skill_dir: Path) -> list[str]:
    failures: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    text = read_text(skill_file)
    if not text.strip():
        return [f"{skill_file.as_posix()} is missing or empty"]

    frontmatter = parse_frontmatter(text)
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        failures.append(f"{skill_file.as_posix()} has invalid name")
    if len(description) < 40:
        failures.append(f"{skill_file.as_posix()} needs a trigger-oriented description")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"{skill_file.as_posix()} missing section {section}")

    for directory in REQUIRED_RESOURCE_DIRS:
        if not (skill_dir / directory).is_dir():
            failures.append(f"{skill_dir.as_posix()} missing {directory}/")

    if len(text.splitlines()) > 500:
        failures.append(f"{skill_file.as_posix()} exceeds 500 lines")
    return failures


def validate(root: Path) -> list[str]:
    skills_root = root / ".claude" / "skills"
    if not skills_root.is_dir():
        return [".claude/skills is missing"]

    failures: list[str] = []
    skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
    if not skill_dirs:
        return [".claude/skills has no skill folders"]
    for skill_dir in skill_dirs:
        failures.extend(validate_skill(skill_dir))
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Folder to validate")
    args = parser.parse_args(argv)

    failures = validate(Path(args.target).resolve())
    if failures:
        print("skill anatomy gate: fail")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("skill anatomy gate: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

