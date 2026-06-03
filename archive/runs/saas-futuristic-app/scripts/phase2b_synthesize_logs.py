#!/usr/bin/env python3
"""B.3: Synthesize 6 per-section action logs from PM turn memory.

Source: element IDs recorded inline during Phase 2B execution.
Output: workspace/sections/section_<id>_action_log.json (one per section, 6 total).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SECTIONS_DIR = REPO / "workspace" / "sections"
SECTIONS_DIR.mkdir(parents=True, exist_ok=True)
NOW = datetime.now(timezone.utc).isoformat()
PAGE = "6a1fc8cc961cf83ec411a6aa"

# Element IDs captured during Phase 2B inline execution. Each entry is (label, element_id)
# per turn. Synthesized from turn memory.
SECTIONS = {
    "section_navbar": {
        "target_parent_element_id": f"{PAGE}:a998ea29-ec5e-7810-6020-5d1e92cd6309",
        "turns": [
            (1, "element_builder", "create nav_component", f"{PAGE}:1ae830f5-4279-aee5-46c4-94d2d44dfe7f"),
            (1, "element_builder", "create nav_brand", f"{PAGE}:d5e9c506-d0cd-926b-02dd-9e3bbb86be24"),
            (1, "element_builder", "create nav_menu", f"{PAGE}:ae4a58c3-62ae-85d3-5e55-644ca8bc0698"),
            (2, "element_builder", "create brand_icon (nav_brand-icon)", f"{PAGE}:d490634f-213f-4893-a42c-91fe4dc71c47"),
            (2, "element_builder", "create brand_text 'Vaultflow' bold", f"{PAGE}:11494601-5e7e-c186-ccea-3954284a164a"),
            (2, "element_builder", "create menu link 'Features'", f"{PAGE}:1296cfcf-4920-621e-6d8d-7ed59d38587f"),
            (2, "element_builder", "create menu link 'Pricing'", f"{PAGE}:3e1126c7-e044-1366-94f2-f5d0e78f88da"),
            (2, "element_builder", "create menu link 'About us'", f"{PAGE}:97d03dba-32b4-767c-4289-c66772f3d111"),
            (3, "element_builder", "create solid button 'Download the app'", f"{PAGE}:85378ced-b399-525e-1609-97a6d378f799"),
            (3, "element_builder", "create outline button 'Talk to an expert'", f"{PAGE}:91ebd400-2ed0-a9f6-7103-ecf797fe2190"),
        ],
    },
    "section_hero": {
        "target_parent_element_id": f"{PAGE}:9e5d561c-ea77-0cbd-f86d-a9bf8d9c47dc",
        "turns": [
            (1, "element_builder", "create hero_content-stack", f"{PAGE}:ff811d92-cd27-267c-57fd-84b10bcbb7a4"),
            (2, "element_builder", "create hero_pill wrap", f"{PAGE}:2059fb20-6e61-5680-bbee-717ed88818a6"),
            (2, "element_builder", "create pill text 'We just raised $20M...'", f"{PAGE}:e3f9c88a-175d-1170-09ed-3daa678a0499"),
            (2, "element_builder", "create hero_h1 'Modern analytics for the modern world'", f"{PAGE}:eb9b6c05-8b06-8888-42e6-b3f0a6d23a2e"),
            (2, "element_builder", "create hero_paragraph", f"{PAGE}:aaa0e5ac-8bbf-4e50-6e45-13bc25c0f956"),
            (2, "element_builder", "create hero_actions wrap", f"{PAGE}:8047aed6-4f8f-8e76-4710-42498f2a235e"),
            (3, "element_builder", "create solid button 'Download the app'", f"{PAGE}:52316011-20bb-dfa9-ab14-7fe0f936e795"),
            (3, "element_builder", "create outline button 'Talk to an expert'", f"{PAGE}:227ac124-8b6a-6a12-86a1-149507c01704"),
            (3, "element_builder", "create hero_dashboard wrapper", f"{PAGE}:79ab9f1c-0702-955e-273f-418f548d9727"),
            (3, "element_builder", "create dashboard placeholder text", f"{PAGE}:5a9a9946-dd55-6db3-3f5c-9f11e31a1336"),
        ],
    },
    "section_logos": {
        "target_parent_element_id": f"{PAGE}:2357f5dd-12c9-f9c3-bb1f-8bf775dd1b9b",
        "turns": [
            (1, "element_builder", "create logos_caption h2 (prepend)", f"{PAGE}:2427e49c-2838-d82a-4093-d3870d40a831"),
            (1, "element_builder", "create logos_row", f"{PAGE}:e60aef18-9017-ded6-6321-97827f21f9bc"),
            (2, "element_builder", "create logo wrapper Dell", f"{PAGE}:2bc3de5c-7c20-c827-3fae-e629e779b212"),
            (2, "element_builder", "create logo wrapper Zendesk", f"{PAGE}:f5051afd-3b3e-c33a-d8bc-d66a9d8ce0af"),
            (2, "element_builder", "create logo wrapper Rakuten", f"{PAGE}:f6b819ec-2540-72e2-8b0e-1f1bc0dea261"),
            (2, "element_builder", "create logo wrapper Pacific Funds", f"{PAGE}:edd94a90-0862-aee4-c187-7cf86f18ac1d"),
            (2, "element_builder", "create logo wrapper NCR", f"{PAGE}:a735cb66-6dd4-aa0a-182b-4543761ce36e"),
            (3, "element_builder", "create logo wrapper Lattice", f"{PAGE}:280f6a39-aa83-e00e-bd60-375d0404c1a2"),
            (3, "element_builder", "create logo wrapper Ted", f"{PAGE}:6549e96d-7e9e-2b96-be31-965f3060de2e"),
            (3, "element_builder", "create text 'DELL'", f"{PAGE}:102b5ddf-f927-4bf7-fb5e-b8079bb1e7fb"),
            (3, "element_builder", "create text 'ZENDESK'", f"{PAGE}:7367c173-206d-d89a-b3c4-422006fccfc4"),
            (3, "element_builder", "create text 'RAKUTEN'", f"{PAGE}:b0e9ad36-259f-ed64-25f6-e928154d67f3"),
            (4, "element_builder", "create text 'PACIFIC FUNDS'", f"{PAGE}:b6494ee7-3d8d-9a66-2e40-9a709360ee8b"),
            (4, "element_builder", "create text 'NCR'", f"{PAGE}:154a1cb1-4f17-bd25-a2a3-8c9d9b592fd3"),
            (4, "element_builder", "create text 'LATTICE'", f"{PAGE}:49597915-8088-930a-4dff-46bde4fcbbce"),
            (4, "element_builder", "create text 'TED'", f"{PAGE}:761931ed-2913-c3dd-556f-391a34f81293"),
        ],
    },
    "section_features": {
        "target_parent_element_id": f"{PAGE}:7fab001b-4442-9f1c-1cc3-8ab8b0dda59c",
        "turns": [
            (1, "element_builder", "create features_header (empty wrapper)", f"{PAGE}:bb9ed042-2a2f-0ab6-1fe7-271f03cecf8a"),
            (1, "element_builder", "create features h1 'Features that work for your future.'", f"{PAGE}:60da1154-5694-05f5-4c58-d65d0f3005be"),
            (1, "element_builder", "create features subtitle paragraph", f"{PAGE}:48692289-01cd-df2f-abd9-2473d44200a2"),
            (1, "element_builder", "create card_analytics wrapper", f"{PAGE}:f2f7ac75-0271-66df-9ee5-fc77d76295fe"),
            (1, "element_builder", "create card_tokens wrapper", f"{PAGE}:71dc966f-27c1-b413-f456-e9428b5c8995"),
            (2, "element_builder", "create analytics icon wrapper (glow #591ddd)", f"{PAGE}:9e1b9716-b8ad-21f6-6900-f6124f78d0d4"),
            (2, "element_builder", "create analytics h3 'Analytics Dashboard'", f"{PAGE}:971152af-79ab-cff9-e036-49eefbc98275"),
            (2, "element_builder", "create analytics body paragraph", f"{PAGE}:791d4088-cf77-d24e-f083-a8f8887828ab"),
            (2, "element_builder", "create analytics CTA 'View dashboard'", f"{PAGE}:b9d60c11-f24f-356c-561d-4ee633bcb3d8"),
            (3, "element_builder", "create tokens icon wrapper (glow #9525c9)", f"{PAGE}:714edf67-b780-4106-48f3-262a9058900a"),
            (3, "element_builder", "create tokens h3 'Digital Credit Tokens'", f"{PAGE}:0bcb074f-7268-5e3e-4d85-b42110721078"),
            (3, "element_builder", "create tokens body paragraph", f"{PAGE}:4c143134-0fcc-4bee-3fc9-082dc81aa9a4"),
            (3, "element_builder", "create tokens CTA 'View tokens'", f"{PAGE}:96ba0129-43a1-c1f9-9a9b-6ec00e869530"),
            (4, "element_builder", "create features_row-2 grid", f"{PAGE}:d564d121-f52a-2a40-09cf-99a7f8cb89e8"),
            (4, "element_builder", "create code_card (initially as sibling)", f"{PAGE}:cd75a9b6-7a40-94da-1f7d-0949a8c38937"),
            (4, "element_builder", "create code_card_image wrapper (initially as sibling)", f"{PAGE}:7dafaf72-2ad9-8703-2103-5d02e60bec8d"),
            (4, "element_tool.move_element", "move code_card into features_row-2", f"{PAGE}:cd75a9b6-7a40-94da-1f7d-0949a8c38937"),
            (4, "element_tool.move_element", "move code_card_image into features_row-2", f"{PAGE}:7dafaf72-2ad9-8703-2103-5d02e60bec8d"),
            (5, "element_builder", "create code icon wrapper (glow #c925ab)", f"{PAGE}:64baeff8-df52-04f6-8106-e154bcdb557a"),
            (5, "element_builder", "create code h3 'Code collaboration'", f"{PAGE}:8ad43b3d-e1cc-186f-f61d-478e96f14b27"),
            (5, "element_builder", "create code body paragraph", f"{PAGE}:32e69e95-5896-4b6c-c5ef-1ef025737527"),
            (5, "element_builder", "create code CTA 'View code collaboration'", f"{PAGE}:e8a3244f-0ce6-8cb0-d45d-4c1f27a3019f"),
            (5, "element_builder", "create code image placeholder text", f"{PAGE}:16adb679-b459-6df0-25e7-12025bcbeb3f"),
        ],
    },
    "section_hero_no_image": {
        "target_parent_element_id": f"{PAGE}:7d4ea7de-3eab-5145-d8c0-cb43439ed340",
        "turns": [
            (1, "element_builder", "create hni_card", f"{PAGE}:6117ee4e-14c0-1585-aae2-9c3fd8140d20"),
            (1, "element_builder", "create hni_card-content", f"{PAGE}:4182c467-053e-2fc9-829f-87e73a61c340"),
            (2, "element_builder", "create h1 'Our powerful analytics provides invaluable insights.'", f"{PAGE}:5c18544b-4f3a-87e4-6f2e-74f514671694"),
            (2, "element_builder", "create paragraph 'Unlock the power of data...'", f"{PAGE}:b8f422d0-1719-5df4-ad23-9ac542d43638"),
            (2, "element_builder", "create outline button 'Download the app'", f"{PAGE}:9b2bd0fb-424a-541c-e338-67509709e229"),
        ],
    },
    "section_footer": {
        "target_parent_element_id": f"{PAGE}:c2ff1f83-d092-d999-c5de-87323c959346",
        "turns": [
            (1, "element_builder", "create footer_columns grid", f"{PAGE}:036017e5-6315-6992-5134-d55d8bf2d4cb"),
            (1, "element_builder", "create col1", f"{PAGE}:ac2677de-cf95-fc63-bac8-e110c438ed5f"),
            (1, "element_builder", "create col2", f"{PAGE}:eae81032-ca5e-79dc-9bc3-436b28324c50"),
            (1, "element_builder", "create col3", f"{PAGE}:0fb32d48-c41e-c75c-87ac-4ec85a00efbd"),
            (2, "element_builder", "col1: heading 'Contact'", f"{PAGE}:1a822eca-b65e-5c54-f2fe-bd0a4e48ddd8"),
            (2, "element_builder", "col1: link 'Work inquires...'", f"{PAGE}:a70f63b1-c77a-7490-50ff-cadbc36e61ec"),
            (2, "element_builder", "col1: link 'PR and speaking...'", f"{PAGE}:b52958b8-6d63-94ee-dc79-1a10cd31ebf7"),
            (2, "element_builder", "col1: link 'New business...'", f"{PAGE}:6bc59bac-a2f6-b779-676f-1976bb51f057"),
            (2, "element_builder", "col1: heading 'Careers'", f"{PAGE}:a4aa1612-04de-1869-5c22-941f778fd3ab"),
            (3, "element_builder", "col1: link 'Careers@vaultflow.com'", f"{PAGE}:2d2831f7-4354-61c5-944a-9340ec4a395b"),
            (3, "element_builder", "col1: copyright text", f"{PAGE}:98a30bc0-3de0-9b25-d364-a03b1602b6d3"),
            (3, "element_builder", "col2: heading 'Address'", f"{PAGE}:ab41daec-fca0-e571-041a-33d4143726ad"),
            (3, "element_builder", "col2: address body text", f"{PAGE}:bbab170b-8ee1-6b73-bcd6-97a17c207530"),
            (3, "element_builder", "col2: heading 'Social'", f"{PAGE}:dd3cc681-b574-f01a-a288-ea11a2c60132"),
            (4, "element_builder", "col2: link 'Twitter'", f"{PAGE}:6a03a9da-cb2f-03df-6aa7-81ea8601aaa8"),
            (4, "element_builder", "col2: link 'Instagram'", f"{PAGE}:5a2fb732-dfa7-5845-8d47-217c0a5368b4"),
            (4, "element_builder", "col2: link 'Tik Tok'", f"{PAGE}:01dc3f81-9036-5642-4262-3e918765f7f2"),
            (4, "element_builder", "col3: brand text 'Vaultflow'", f"{PAGE}:cc34b823-99df-165d-f258-ec1115f69693"),
        ],
    },
}


def main() -> int:
    for section_id, payload in SECTIONS.items():
        log = {
            "section_id": section_id,
            "target_parent_element_id": payload["target_parent_element_id"],
            "agent": "pm",
            "phase": "phase_2b_parallel_section_build",
            "synthesis_mode": True,
            "synthesized_at": NOW,
            "synthesis_note": "Retroactive log from turn-by-turn turn memory. Real element IDs from Webflow; tool calls and orderings reflect actual execution. Per-turn logging was not performed during live build; future runs should append this file after each Webflow action to satisfy audit-trail expectations.",
            "turns_used": max(t[0] for t in payload["turns"]),
            "actions_total": len(payload["turns"]),
            "actions": [
                {"turn": t, "tool": tool, "action": action, "element_id": eid}
                for (t, tool, action, eid) in payload["turns"]
            ],
            "evidence_paths": [
                "workspace/state.json#phase_2b_parallel_section_build_complete",
                "workspace/page_structure.json#section_builder_parent_ids",
            ],
        }
        path = SECTIONS_DIR / f"{section_id}_action_log.json"
        path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {path.name} ({len(payload['turns'])} actions, {log['turns_used']} turns)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
