#!/usr/bin/env python3
"""Contract test: every skill that can write to Webflow must have an explicit
approval gate in its SKILL.md. This is a structural check, not a runtime one.

The gate string is the literal `APPROVAL GATE` (case-sensitive) inside a code
fence or a markdown list item, paired with one of `approve` / `revise` /
`cancel` as the user's allowed response. If this test fails, the gate was
removed or reworded; restore the gate per CLAUDE.md:51 ("Branch-first
Deployments") and CLAUDE.md:54 ("Auto-Publish Forbidden").
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parent.parent
SKILL_FILES = [
    SKILLS_ROOT / "design-system-sync" / "SKILL.md",
    SKILLS_ROOT / "figma-to-html-architect" / "SKILL.md",
    SKILLS_ROOT / "figma-to-webflow-orchestrator" / "SKILL.md",
]

REQUIRED_GATE_MARKER = "APPROVAL GATE"
REQUIRED_USER_RESPONSES = ("approve", "revise", "cancel")


class TestApprovalGates(unittest.TestCase):
    def test_all_skills_have_approval_gates(self):
        for skill_path in SKILL_FILES:
            with self.subTest(skill=skill_path.name):
                self.assertTrue(skill_path.exists(), f"missing SKILL.md: {skill_path}")
                body = skill_path.read_text(encoding="utf-8")
                self.assertIn(
                    REQUIRED_GATE_MARKER,
                    body,
                    f"{skill_path.name} does not contain the literal '{REQUIRED_GATE_MARKER}' "
                    f"string. Restore the gate per CLAUDE.md:51/54.",
                )

    def test_all_gates_offer_approve_revise_cancel(self):
        pattern = re.compile(
            r"APPROVAL GATE.*?(?=\n##|\n---|\Z)", re.DOTALL
        )
        for skill_path in SKILL_FILES:
            with self.subTest(skill=skill_path.name):
                body = skill_path.read_text(encoding="utf-8")
                gate_blocks = pattern.findall(body)
                self.assertTrue(
                    gate_blocks,
                    f"{skill_path.name} has '{REQUIRED_GATE_MARKER}' but no parseable gate block.",
                )
                for block in gate_blocks:
                    for response in REQUIRED_USER_RESPONSES:
                        self.assertIn(
                            response,
                            block,
                            f"{skill_path.name} gate block does not list '{response}' "
                            f"as an allowed user response.",
                        )


if __name__ == "__main__":
    unittest.main()
