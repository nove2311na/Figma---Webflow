#!/usr/bin/env python3
"""B.4 fix: populate figma-token-map.json with the 7 color tokens + the
CF V2.2 utility tokens that classes reference.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITE_ID = "6920a7d45c61690dd10ac690"
LIB_PATH = REPO / "knowledge-base" / "libraries" / SITE_ID / "client-first-library.json"
TOKEN_PATH = REPO / "knowledge-base" / "libraries" / SITE_ID / "figma-token-map.json"
NOW = datetime.now(timezone.utc).isoformat()


def main() -> int:
    lib = json.loads(LIB_PATH.read_text(encoding="utf-8"))
    token_map = json.loads(TOKEN_PATH.read_text(encoding="utf-8"))

    # Collect distinct figma_token values from library
    used_tokens = set()
    for entry in lib["classes"].values():
        tok = entry.get("figma_token")
        if tok:
            used_tokens.add(tok)

    existing_mappings = set(token_map.get("mappings", {}).keys())
    added = 0
    for tok in used_tokens:
        if tok in existing_mappings:
            continue
        # Infer category and value
        if tok.startswith("cf-v2.2") or tok in {"declared-in-blueprint", "utility"}:
            token_map["mappings"][tok] = {
                "figma_value": "see-blueprint",
                "css_property": "see-blueprint",
                "class": "see-blueprint",
                "source": "cf-v2.2-standard"
            }
        else:
            token_map["mappings"][tok] = {
                "figma_value": tok,
                "css_property": "see-blueprint",
                "class": "see-blueprint",
                "source": "figma:138:8546"
            }
        added += 1

    token_map["updated_at"] = NOW
    TOKEN_PATH.write_text(json.dumps(token_map, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"added {added} token mappings; total: {len(token_map['mappings'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
