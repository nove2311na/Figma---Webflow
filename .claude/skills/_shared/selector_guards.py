"""Shared selector guards for design-system-sync and figma-to-html-architect skills.

These helpers detect selectors that must never appear in a Client-First V2.2 build:
- `is_native_selector`: Webflow native classes (`.w-*`, `.wf-*`) and any selectors
  listed in the baseline contract's `excluded.webflowNativeSelectors`.
- `is_html_tag_selector`: raw HTML tag selectors (e.g. `h1`, `body`) and any
  selectors listed in the baseline contract's `excluded.nativeElementSelectors`.

Both functions take a selector string and a container of known-bad selectors
from the baseline contract. They strip a leading `.` before comparing so callers
can pass either `.foo` or `foo` interchangeably.

Imported by:
- design-system-sync/scripts/validate_figma_extraction.py
- figma-to-html-architect/scripts/process_html.py
"""

from __future__ import annotations

_HTML_TAGS = frozenset({
    "html", "body", "img", "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "a", "ul", "ol", "li", "blockquote", "figure", "figcaption",
    "label", "button", "fieldset", "input", "textarea", "select", "*",
})


def _strip_dot(sel: str) -> str:
    sel = sel.strip()
    if sel.startswith("."):
        sel = sel[1:]
    return sel


def is_native_selector(sel: str, webflow_native=()) -> bool:
    """True if `sel` is a Webflow native class (`w-*`/`wf-*`) or is listed in
    `webflow_native` (the baseline contract's `excluded.webflowNativeSelectors`).
    Accepts both `.foo` and `foo` forms in the container.
    """
    clean = _strip_dot(sel)
    if clean.startswith("w-") or clean.startswith("wf-"):
        return True
    return f".{clean}" in webflow_native or clean in webflow_native


def is_html_tag_selector(sel: str, native_elements=()) -> bool:
    """True if `sel` is a raw HTML tag or is listed in `native_elements` (the
    baseline contract's `excluded.nativeElementSelectors`). Accepts both `.foo`
    and `foo` forms in the container.
    """
    clean = _strip_dot(sel)
    if clean in _HTML_TAGS:
        return True
    return f".{clean}" in native_elements or clean in native_elements
