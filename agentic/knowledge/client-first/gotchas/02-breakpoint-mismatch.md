---
_raw_url: null
_distilled_at: 2026-06-04
_token_estimate: 600
---

# Gotcha 02 — Breakpoint Mismatch

**Figma side**: design frames are at fixed widths (e.g. 1440px desktop, 768px tablet, 375px mobile). Stored as Figma frame size, not media query.

**Webflow side**: breakpoints are real CSS media queries. V2.2 default: desktop ≥ 992, tablet ≤ 991, mobile-landscape ≤ 767, mobile-portrait ≤ 479.

## Trap

Designers put a 1280px-wide design frame in Figma. Webflow's `container-large` is 80rem = 1280px. Looks aligned, but:
- Figma's 1440px frame ≠ Webflow's 1440px viewport if the user's browser has scrollbars (~17px lost).
- Figma's 768px tablet frame might not match Webflow's tablet breakpoint (991px) — different things.

## Detection

Check the Figma file's frame widths against Webflow's breakpoints:

| Figma frame | Webflow breakpoint it should match |
|---|---|
| 375 | mobile-portrait (≤479) |
| 768 | mobile-landscape / tablet boundary (between 767 and 991) |
| 1280 | desktop (≥992) |
| 1440 | desktop (≥992) — no separate "wide" breakpoint |

If a Figma frame is 1024px and there's no 1024px Webflow breakpoint, the design will display at the tablet size in Webflow, not "small desktop".

## Code-level rule

Always render HTML with explicit `@media (max-width: ...)` or `@media (min-width: ...)` queries that match Webflow's breakpoints. Don't invent new breakpoints in CSS without adding them to the Webflow project.

## Fix

1. Identify Figma frame widths used in the file.
2. Map each to a Webflow breakpoint (default 4: 479, 767, 991, 992+).
3. If a frame doesn't fit (e.g. 1024px), pick the closest Webflow breakpoint and add a design note: "this frame will display at tablet".
4. Generate media queries using the Webflow breakpoint values, not the Figma frame widths.
