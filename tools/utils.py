"""Client-First utility helpers for MAS Figma-to-Webflow workflows."""
from __future__ import annotations

import math
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_FONT_SIZE = 16
COLOR_THRESHOLD = 15
SPACING_SCALE = {
    "tiny": 4,
    "small": 8,
    "medium": 16,
    "large": 32,
    "huge": 64,
    "section-small": 40,
    "section-medium": 80,
    "section-large": 120,
}
CLIENT_FIRST_MAP_PATH = Path(__file__).resolve().parents[1] / "knowledge-base" / "client-first-class-map.json"


@dataclass(frozen=True)
class RgbaColor:
    """RGBA color with 0-255 RGB channels and 0-1 alpha."""

    r: int
    g: int
    b: int
    a: float = 1.0


def to_rem(value: str | int | float | list[str | int | float] | None) -> str:
    """Convert px-like values into rem strings."""
    if value is None:
        return "0rem"

    def convert_one(item: str | int | float) -> str:
        try:
            number = float(str(item).replace("px", ""))
        except ValueError:
            return "0rem"
        if number == 0:
            return "0rem"
        converted = number / BASE_FONT_SIZE
        return f"{converted:.3f}".rstrip("0").rstrip(".") + "rem"

    if isinstance(value, list):
        return " ".join(convert_one(item) for item in value)
    if isinstance(value, str) and " " in value.strip():
        return " ".join(convert_one(item) for item in value.split())
    return convert_one(value)


def slugify(value: str) -> str:
    """Create a Client-First-safe slug while preserving underscores."""
    normalized = unicodedata.normalize("NFD", value.lower().strip())
    ascii_text = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    cleaned = re.sub(r"[^a-z0-9\s\-_]", "", ascii_text)
    return re.sub(r"-+", "-", re.sub(r"\s+", "-", cleaned)).strip("-")


def format_class(prefix: str, element: str | None = None, *, is_utility: bool = False) -> str:
    """Format a class according to Client-First naming conventions."""
    clean_prefix = slugify(prefix)
    if is_utility or not element:
        return clean_prefix
    return f"{clean_prefix}_{slugify(element)}"


def parse_color(value: str | dict[str, Any]) -> RgbaColor | None:
    """Parse a hex string or Figma RGBA dict into a color."""
    if isinstance(value, dict) and {"r", "g", "b"}.issubset(value):
        return RgbaColor(
            r=round(float(value["r"]) * 255),
            g=round(float(value["g"]) * 255),
            b=round(float(value["b"]) * 255),
            a=round(float(value.get("a", 1)), 2),
        )
    if isinstance(value, str):
        return hex_to_rgba(value)
    return None


def hex_to_rgba(value: str) -> RgbaColor | None:
    """Parse #RGB, #RGBA, #RRGGBB, or #RRGGBBAA."""
    text = value.strip().lstrip("#")
    if len(text) in {3, 4}:
        text = "".join(char * 2 for char in text)
    if len(text) not in {6, 8} or not re.fullmatch(r"[0-9a-fA-F]+", text):
        return None
    alpha = int(text[6:8], 16) / 255 if len(text) == 8 else 1.0
    return RgbaColor(
        r=int(text[0:2], 16),
        g=int(text[2:4], 16),
        b=int(text[4:6], 16),
        a=round(alpha, 2),
    )


def color_distance(first: str | dict[str, Any], second: str | dict[str, Any]) -> float:
    """Return Euclidean color distance including alpha."""
    first_color = parse_color(first)
    second_color = parse_color(second)
    if not first_color or not second_color:
        return 1000.0
    return math.sqrt(
        (second_color.r - first_color.r) ** 2
        + (second_color.g - first_color.g) ** 2
        + (second_color.b - first_color.b) ** 2
        + ((second_color.a - first_color.a) * 255) ** 2
    )


def log_entry(agent: str, entry_type: str, message: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create a standardized workspace log entry."""
    safe_context = context or {}
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "phase": safe_context.get("phase", "unknown"),
        "type": entry_type,
        "message": message,
        "context": safe_context,
        "resolution": "pending",
    }


def load_client_first_class_map(path: Path | None = None) -> dict[str, Any]:
    """Load the structured Client-First class map."""
    class_map_path = path or CLIENT_FIRST_MAP_PATH
    return json.loads(class_map_path.read_text(encoding="utf-8"))


def suggest_client_first_classes(figma_properties: dict[str, Any], class_map: dict[str, Any] | None = None) -> list[dict[str, str]]:
    """Suggest Client-First class decisions from a small Figma property sample.

    The helper is intentionally conservative: it returns mapping candidates with
    source rules, but the architect still decides final class application.
    """
    library = class_map or load_client_first_class_map()
    mappings = library.get("figma_property_map", [])
    suggestions: list[dict[str, str]] = []
    property_text = " ".join(f"{key}={value}" for key, value in figma_properties.items()).lower()

    for mapping in mappings:
        signals = mapping.get("signals", [])
        if any(str(signal).lower() in property_text for signal in signals):
            suggestions.append(
                {
                    "figma_property": str(mapping.get("figma_property", "")),
                    "client_first_decision": str(mapping.get("client_first_decision", "")),
                    "source": "knowledge-base/client-first-class-map.json",
                }
            )
    return suggestions
