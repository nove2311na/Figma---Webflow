Prompt

"You are an independent workflow completeness auditor for a Figma→Webflow HTML contract pipeline.

TASK: Trace through the full Figma→HTML pipeline using common real-world design patterns.
For each pattern below, walk through the pipeline step by step and find where the instructions
are missing, ambiguous, or wrong.

OUTPUT FORMAT:
  [GAP] pattern_name — which file/step — what decision is missing or underspecified
  [CONFLICT] file A vs file B — what contradicts
  [EDGE CASE] scenario — what the pipeline does not handle

Test these patterns:
1. Section with dark background + white text — does color mapping + section add-on class rule work?
2. 3-column card grid that goes 1-column on mobile — does responsive Case 4 get caught?
3. Figma component "Button/Ghost" (a variant not in our button list) — what happens?
4. Nested component: Card containing an Icon + Text — how does class naming cascade?
5. Section with no auto-layout (manually positioned absolute layers) — layout decision?
6. Text block that needs max-width constraint inside a container-large — utility or custom?
7. Image with 16:9 aspect ratio crop — what classes get applied?
8. Nav component outside main-wrapper — does the structural skeleton handle this?
9. A Figma color variable that exists but was not added to the per-project library yet — what happens?
10. Heading that is H2 semantically but visually H4 size — typography algorithm outcome?

## Files to read:
- agentic/prompts/read-figma-data.md
- agentic/prompts/write-html-contract.md
- agentic/specs/figma-to-client-first-mapping.md
- knowledge-base/client-first-class-map.json"

---

[GAP] Section with dark background + white text — figma-to-client-first-mapping.md:Section F — lacks instructions on how to convert a section-level background variable (e.g. background-color-dark) into a section style combo class (e.g. section-style-dark)
[CONFLICT] write-html-contract.md:Layer 1 vs figma-to-client-first-mapping.md:Section F — write-html-contract.md Layer 1 states section-level visual styles must be applied as a section style combo class (e.g., section-style-dark), but figma-to-client-first-mapping.md Section F maps a background variable directly to background-color-[token], leading to a layout class + visual utility mismatch
[GAP] Figma component "Button/Ghost" — write-html-contract.md:new_classes — lacks instructions on how to register and create new combo class variations (e.g., is-ghost) when they do not exist in the per-project library
[AMBIGUOUS] Nested component: Card containing an Icon + Text — figma-to-client-first-mapping.md:Section G — does not clarify how custom element names cascade for nested components (e.g. whether nested elements inside a reusable card wrapper should use the card's prefix or the parent section's prefix)
[GAP] Section with no auto-layout — figma-to-client-first-mapping.md:Section B — lacks instructions for handling absolute-positioned child elements that are not full-cover (i.e. those requiring custom top/left offsets rather than the generic layer utility)
[AMBIGUOUS] Text block that needs max-width constraint inside a container-large — write-html-contract.md:Layer 4 — conflict between forcing max-width-[size] utility vs creating a custom class (e.g., hero_intro-text) when both max-width and custom margins are needed
[EDGE CASE] Image with 16:9 aspect ratio crop — figma-to-client-first-mapping.md:Section A — does not specify how to style the actual <img> tag inside the aspect-ratio wrapper (width/height 100% and object-fit: cover) to ensure it scales correctly
[GAP] Nav component outside main-wrapper — write-html-contract.md:Layer 1 — the structural skeleton (lines 42-57) lacks placeholders or instructions showing where the global nav_component and footer_component should be placed (sibling to main-wrapper)
[EDGE CASE] A Figma color variable that exists but was not added to the library yet — figma-to-client-first-mapping.md:Section F — lacks instructions on how to handle raw, hardcoded hex values in Figma that have no variable mapping in the design file

---

## Ground-Truth Reconciliation (live Client-First V2.2, 2026-06-03)

| Finding | Status | Evidence |
|---|---|---|
| Dark bg section: Section F (bg utility) vs Layer 1 (section-style) conflict | CONFIRMED GAP | Section F should distinguish background-color utility vs section-style add-on. Section-style-dark is a global add-on, not a variable-backed utility. Guidance clarified in write-html-contract.md |
| Button/Ghost variant: no guidance for new combos | CONFIRMED GAP | Write-html-contract.md updated: only is-secondary/is-text ship in CF V2.2; new combos must be declared in new_classes with Case 5 |
| Nav outside main-wrapper: skeleton missing | CONFIRMED GAP | write-html-contract.md Layer 1 updated with note that nav_component and footer_component are siblings of main-wrapper, outside it |
| Img in aspect-ratio wrapper: object-fit missing | RESOLVED | All aspect-ratio-* classes include object-fit:cover. No separate class needed |
| Hex without variable: no handling guidance | CONFIRMED GAP | Section F updated: if Figma color has no variable → flag as blocker; if it's a hardcoded hex not in the library, operator must add to library first |
| Text block max-width: utility vs custom ambiguity | CONFIRMED GAP | Decision rule clarified: use max-width-[size] utility when it fits; create custom class only when both max-width and unique layout/margin needed simultaneously |
| Nested component class cascade | CONFIRMED GAP | Section G updated with _component wrapper + _[el] children + multi-level nested naming |
| Gap token round-to-clean-rem rule | SUPERSEDED | Use token snap, not px/16 math. Variable provides responsive value automatically |
