"""Resolve a Figma node to (tag, classHints, attributes, warning, source).

Three resolution tiers:
  Tier 1 — exact keyword match against `convention.exact`
            (longest keyword wins, case-insensitive, tokenized by `_`)
  Tier 2 — type heuristic against `convention.heuristics`
            (matched on figm_type + optional size/child hints)
  Tier 3 — unmapped fallback (`convention.fallback`)

Public entry points:
    resolve_figma_node(node: dict) -> ResolvedNode
    resolve_batch(nodes: Iterable[dict]) -> list[ResolvedNode]
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

LOG = logging.getLogger("resolve_figma_name")

DEFAULT_CONVENTION_PATH = (
    Path(__file__).resolve().parent.parent
    / "references"
    / "figma-naming-convention.json"
)

TOKEN_SPLIT = re.compile(r"[_\-\s]+")


@dataclass
class ResolvedNode:
    original_name: str
    figma_type: str
    tag: str
    class_hints: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    required_attributes: list[str] = field(default_factory=list)
    confidence: float = 0.0
    source: str = "fallback"  # exact | heuristic | fallback
    warning: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _tokenize(name: str) -> list[str]:
    return [t.lower() for t in TOKEN_SPLIT.split(name.strip()) if t]


def _match_exact(tokens: list[str], exact_rules: list[dict]) -> dict | None:
    """Longest matching keyword wins; keyword tokens must appear as a contiguous subsequence."""
    best: dict | None = None
    best_len = 0
    for rule in exact_rules:
        keyword_tokens = _tokenize(rule["keyword"])
        klen = len(keyword_tokens)
        if klen == 0 or klen > len(tokens):
            continue
        for i in range(len(tokens) - klen + 1):
            if tokens[i : i + klen] == keyword_tokens:
                if klen > best_len or (klen == best_len and best is not None and rule.get("priority", 0) > best.get("priority", 0)):
                    best = rule
                    best_len = klen
                break
    return best


def _match_heuristic(node: dict, heuristics: list[dict]) -> dict | None:
    figma_type = str(node.get("type", "")).upper()
    font_size = node.get("font_size")
    has_image_fill = node.get("has_image_fill", False)
    child_count = node.get("child_count", 0)

    candidates: list[dict] = []
    for rule in heuristics:
        if rule.get("figma_type") and rule["figma_type"].upper() != figma_type:
            continue
        if "font_size_gte" in rule and not (isinstance(font_size, (int, float)) and font_size >= rule["font_size_gte"]):
            continue
        if "font_size_lt" in rule and not (isinstance(font_size, (int, float)) and font_size < rule["font_size_lt"]):
            continue
        if rule.get("has_image_fill") is not None and rule["has_image_fill"] != has_image_fill:
            continue
        if "child_count" in rule and child_count != rule["child_count"]:
            continue
        if "child_count_gte" in rule and child_count < rule["child_count_gte"]:
            continue
        candidates.append(rule)

    if not candidates:
        return None
    return max(candidates, key=lambda r: r.get("confidence", 0))


def _apply_rule(rule: dict, original_name: str, figma_type: str, source: str) -> ResolvedNode:
    return ResolvedNode(
        original_name=original_name,
        figma_type=figma_type,
        tag=rule.get("tag", "div"),
        class_hints=list(rule.get("classHints", [])),
        attributes=dict(rule.get("attributes", {})),
        required_attributes=list(rule.get("requiredAttributes", [])),
        confidence=float(rule.get("confidence", 0.0)),
        source=source,
        warning=rule.get("warning"),
    )


def resolve_figma_node(node: dict, *, convention: dict | None = None) -> ResolvedNode:
    conv = convention or _load_convention()
    name = str(node.get("name") or node.get("data_name") or "")
    figma_type = str(node.get("type", ""))
    tokens = _tokenize(name)

    rule = _match_exact(tokens, conv.get("exact", []))
    if rule is not None:
        return _apply_rule(rule, name, figma_type, "exact")

    hrule = _match_heuristic(node, conv.get("heuristics", []))
    if hrule is not None:
        return _apply_rule(hrule, name, figma_type, "heuristic")

    return _apply_rule(conv.get("fallback", {"tag": "div"}), name, figma_type, "fallback")


def resolve_batch(nodes: Iterable[dict], *, convention: dict | None = None) -> list[ResolvedNode]:
    return [resolve_figma_node(n, convention=convention) for n in nodes]


def _load_convention(path: Path = DEFAULT_CONVENTION_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    sample_nodes = [
        {"name": "section_hero", "type": "FRAME", "child_count": 4},
        {"name": "heading_h2", "type": "TEXT"},
        {"name": "Some Random Frame", "type": "FRAME", "child_count": 2},
        {"name": "Hero Title", "type": "TEXT", "font_size": 56},
        {"name": "Rectangle 4", "type": "RECTANGLE", "has_image_fill": True},
    ]
    for n in sample_nodes:
        result = resolve_figma_node(n)
        print(f"{n['name']!r:30s} -> <{result.tag}> src={result.source} warn={result.warning}")
