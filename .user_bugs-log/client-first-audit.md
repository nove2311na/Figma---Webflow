Prompt: 
"You are an independent Client-First V2 knowledge auditor.

TASK: Cross-check these project files against official Finsweet Client-First docs.
Find: (1) classes/rules we documented incorrectly, (2) CF classes we missed entirely,
(3) rules we stated that contradict the docs.

OUTPUT FORMAT — one finding per line:
  [WRONG] file:section — what we said vs what CF docs actually say
  [MISSING] class or rule name — where it belongs, what it does
  [AMBIGUOUS] file:section — what is unclear or incomplete

DO NOT praise. Only findings. If nothing wrong in a section, skip it.

## Files to read (in this project):
- knowledge-base/client-first-class-map.json
- knowledge-base/client-first-theory.md
- agentic/prompts/write-html-contract.md
- agentic/specs/figma-to-client-first-mapping.md

## CF docs to fetch and cross-check against:
- https://finsweet.com/client-first/docs/classes-strategy-1
- https://finsweet.com/client-first/docs/classes-strategy-2
- https://finsweet.com/client-first/docs/core-structure-strategy
- https://finsweet.com/client-first/docs/utility-class-systems
- https://finsweet.com/client-first/docs/typography-strategy
- https://finsweet.com/client-first/docs/spacing-strategy
- https://finsweet.com/client-first/docs/sizes-and-rem
- https://finsweet.com/client-first/docs/variables
- https://finsweet.com/client-first/docs/folders-strategy
- https://finsweet.com/client-first/docs/semantic-html-tags
- https://finsweet.com/client-first/docs/accessibility

Fetch each URL, read our files, then audit."

---

[WRONG] knowledge-base/client-first-class-map.json:class_groups.advanced_layout — aspect-ratio-portrait is mapped to 3/4 and aspect-ratio-landscape to 4/3 vs CF docs stating they are 2/3 and 3/2
[WRONG] agentic/prompts/write-html-contract.md:Layer 2 — aspect-ratio-portrait is mapped to 3:4 and aspect-ratio-landscape to 4:3 vs CF docs stating they are 2/3 and 3/2
[WRONG] knowledge-base/client-first-theory.md:Chapter 2 — states padding-section-[size] is located inside container vs CF docs stating it should be combined on the padding-global div block to reduce nesting
[WRONG] agentic/prompts/write-html-contract.md:Layer 1 — structural skeleton nests padding-section-[size] inside container-[size] vs CF docs stating it should be combined on the padding-global div block to reduce nesting
[WRONG] knowledge-base/client-first-class-map.json:class_groups.typography — lists text-weight-medium as a utility pattern vs CF docs not having a text-weight-medium utility class
[WRONG] agentic/specs/figma-to-client-first-mapping.md:Section E — maps font-weight 500 to text-weight-medium vs CF docs not having a text-weight-medium utility class
[WRONG] knowledge-base/client-first-class-map.json:class_groups.typography — lists text-size-huge as a utility pattern vs CF docs not having a text-size-huge utility class
[WRONG] agentic/prompts/write-html-contract.md:Layer 2 — lists text-size-huge as a utility class vs CF docs not having a text-size-huge utility class
[WRONG] knowledge-base/client-first-theory.md:Chapter 1 — lists margin-bottom-medium as a single utility class example vs CF docs using a two-class system (margin-bottom + margin-medium)
[WRONG] knowledge-base/client-first-theory.md:Chapter 1 — states HomeHero_Image is incorrect because it does not use PascalCase vs it actually using PascalCase (which is prohibited)
[WRONG] agentic/specs/figma-to-client-first-mapping.md:Section A — maps a navbar frame to `<nav>` and nav_component vs CF docs recommending wrapping nav_component in a `<header>` tag
[WRONG] agentic/specs/figma-to-client-first-mapping.md:Section A — maps button components to `<a>` or `<button>` tags vs CF docs stating `<button>` tags are not natively supported in Webflow
[MISSING] inherit-color — typography/color utility class, resets text color to inherit from parent element
[MISSING] fs-a11y_visually-hidden — accessibility utility class, hides element visually while keeping it readable for screen readers
[MISSING] margin-horizontal, margin-vertical, padding-horizontal, padding-vertical — spacing utility direction classes, applies spacing horizontally or vertically
[MISSING] margin/padding/spacer sizes (0, xxsmall, xsmall, xlarge, xxlarge, xhuge, xxhuge, custom*) — spacing utility size classes, provides spacing values outside the basic tiny/small/medium/large/huge set
[MISSING] text-size-regular — typography utility class, missing from client-first-class-map.json but is a standard Client-First size
[AMBIGUOUS] agentic/prompts/write-html-contract.md:Layer 1 — section-style-dark is called a combo class/combo add-on but does not use the is- prefix, violating combo class naming rules
[AMBIGUOUS] knowledge-base/client-first-theory.md:Chapter 1 — prohibits class stacking of more than 3 layers vs write-html-contract and CF docs stating 4 classes is the absolute maximum
[AMBIGUOUS] agentic/prompts/write-html-contract.md:Layer 5 — semantic HTML tags table contains duplicate rows for <article> and <aside>
[WRONG] knowledge-base/client-first-theory.md:Chapter 1 — entire custom-class convention follows V1 model (underscore = component-element) vs CF V2 where underscore = folder-element and component wrappers require explicit `_component` suffix (`pricing-card_card-wrapper` not `pricing-card_wrapper`); every custom-class example in class-map/contract is V1
[WRONG] knowledge-base/client-first-class-map.json:class_groups.structure — `padding-global` and `container-*` examples imply fixed nesting vs CF docs explicitly allowing `padding-global` as parent OR child of `container-large` ("with or without other essential page structures")
[WRONG] knowledge-base/client-first-theory.md:Chapter 5 — step 3 says "Spacing (Gap, Padding) -> Spacing System (Utility or Variables)" vs CF docs stating "We decided to not release size variables because there is no breakpoint feature on the variables panel"; size variables do not exist in CF
[WRONG] knowledge-base/client-first-class-map.json:class_groups.structure — `section_[section-name]` does not declare `<section>` HTML tag in webflow_properties vs CF core-structure explicitly recommending the `<section>` tag for the wrapping element
[WRONG] knowledge-base/client-first-class-map.json:class_groups.typography — `text-size-[tiny|small|medium|large|huge]` and `text-size-regular` referenced in write-html-contract vs CF utility-systems standard list being `tiny, small, regular, medium, large, huge` (regular must be in the canonical pattern)
[WRONG] knowledge-base/client-first-class-map.json:class_groups.typography — `text-weight-medium` listed as utility vs CF utility-systems shipping only `light, normal, semibold, bold, xbold` (5 weights; no medium)
[WRONG] knowledge-base/client-first-class-map.json:class_groups.color — pattern uses single-dash `background-color-primary` / `text-color-primary` / `border-color-primary` vs CF variables doc shipping defaults with double-dash format `background-color--background-primary` / `text-color--text-primary`
[WRONG] agentic/prompts/write-html-contract.md:Layer 1 — rule "Nesting order is fixed" for `padding-global` → `container-*` contradicts CF core-structure note that `padding-global` can be parent of `container-large`, child of `container-large`, or both together
[WRONG] agentic/prompts/write-html-contract.md:Layer 1 — HTML Contract Output Format example nests `padding-section-large` inside `container-large` vs CF spacing-strategy rule: "The padding-section-[size] utility class should be used on the div block with the padding-global class applied to reduce nesting elements"
[WRONG] agentic/prompts/write-html-contract.md:Layer 3 CASE 5 — button combo examples use `is-brand` and `is-outline` which are not CF defaults (CF ships only `is-secondary` and `is-text` as button combos) vs CF utility-systems showing base `button` = primary style, combos limited to `is-secondary`/`is-text`
[WRONG] agentic/specs/figma-to-client-first-mapping.md:Section B — gap conversion table "Round to nearest clean CF REM value: 0.5, 1, 1.5, 2, 2.5, 3, 4, 5" vs CF sizes-and-rem standard token list being 0.5, 1, 1.5, 2, 2.5, 3 (no 4 or 5 in canonical tokens)
[WRONG] agentic/specs/figma-to-client-first-mapping.md:Section G — custom-class naming uses V1 model `[section-prefix]_[element-name]` (`hero_content-row`) vs CF V2 expecting folder-element + `_component` suffix where component wrapper is `[folder]_component` (`pricing-card_component`) and child is `[folder]_child-element` (`pricing-card_card-wrapper`)
[MISSING] _component suffix convention — CF V2 requires explicit `_component` identifier on every component wrapper (e.g., `pricing-card_component`); all custom-class examples in class-map/contract/theory lack this
[MISSING] custom spacer folder pattern — CF folders-strategy: `_spacer_[element]_` (e.g., `_spacer_header`, `_spacer_footer`) for component-specific spacer overrides; not in any project file
[MISSING] folder nesting strategies — CF supports `[page-folder]_[keyword-folder]_[element]` and `[keyword-folder]_[page-folder]_[element]` for nested organization; class-map/contract/theory don't cover folder organization at all
[MISSING] section-style-* combo add-on classes — class-map doesn't list `section-style-dark`, `section-style-brand`, `section-style-light` (referenced in write-html-contract.md Layer 1 but absent from class-map and CF utility-systems official list)
[MISSING] same-category stacking rule — CF classes-strategy-2: "We recommend stacking global classes from the same CSS property or category type. Stack margin with margin, padding with padding, etc."; not in any project file
[MISSING] no-style-on-stacked-utilities rule — CF classes-strategy-2: "Do not apply new styles directly to stacked global utility classes — that creates a combo class and defeats the purpose of true global utility classes"; not in any project file
[MISSING] two justifications for global classes — CF classes-strategy-2 lists the two valid justifications ("Does this style have any benefit of being managed globally?" / "Does this lead to faster build time, efficient use of recurring styles, or client convenience?"); theory Ch 1.2 omits this gate
[MISSING] "no spacing utilities on typography" rule — CF spacing-strategy: "Don't apply spacing utility classes to typography elements (causes deep stacking). Use spacing blocks instead."; not enforced in class-map/contract
[MISSING] "no utility padding to size inner content" rule — CF spacing-strategy: apply to a custom class to allow breakpoint control; not in project files
[MISSING] "no margin on button class for button rows" rule — CF spacing-strategy: "Applying margin-right directly to the button class will limit how we can use our button"; not in project files
[MISSING] standard REM token table — CF sizes-and-rem lists 0.5/1/1.5/2/2.5/3 rem as canonical; project files reference spacing values but don't anchor to this exact list
[MISSING] Webflow native-component ARIA note — CF accessibility: "Webflow's native components (Navbar, Slider, Tabs, etc.) already include correct ARIA attributes"; not in project files
[MISSING] button-vs-link semantic rule for Webflow — CF accessibility: "Webflow's Button component is an `<a>` tag, not a `<button>`. When a `<button>` is needed, use a `<div>` with `role='button'`, `tabindex`, JS for Enter/Space activation, and `aria-pressed`/`aria-expanded`"; partially covered but the Webflow-specific gotcha is missing
[MISSING] `aria-hidden` for decorative elements — CF accessibility lists this as the way to hide visual-only elements from screen readers; project files have no ARIA coverage
[MISSING] focus-state styling rule — CF accessibility requires styled focus state for every focusable element; project files have no focus-state guidance
[MISSING] keyboard navigation rules — Tab/Shift+Tab, Enter, Space, Arrow, Esc, Home/End for accordions per CF accessibility; not in project files
[MISSING] `tabindex` rules — CF accessibility defines `tabindex="0"`, positive (avoid), `-1` semantics; not in project files
[MISSING] alt text guidance — CF accessibility does not list specifics but links A11y Project; class-map visibility hide-* utilities don't address image alt requirements
[MISSING] CF doc source URLs in references — write-html-contract.md Source References list only 3 CF URLs (classes-strategy-1, classes-strategy-2, utility-class-systems); missing core-structure-strategy, typography-strategy, spacing-strategy, sizes-and-rem, variables, folders-strategy, semantic-html-tags, accessibility; figma-to-client-first-mapping.md has zero CF doc references
[MISSING] primitive vs semantic token rule — CF variables: "Avoid directly linking primitive colors to classes unless there is a strong reason to do so"; class-map color section treats all colors as interchangeable tokens
[MISSING] "don't name variables by color" rule — CF variables: "Do not name a semantic variable with the name of the color"; theory Ch 5 step 3 doesn't address semantic naming
[MISSING] primary/alternate theme concept — CF variables: `background-primary` (dark) vs `background-alternate` (light) as default theme reference; class-map and theory don't capture theme-toggle semantics
[MISSING] inherit-color via variables — CF variables: "When we apply a color directly to a text element, we lose the ability to inherit the color from the parent element"; the rule + the `inherit-color` override class are missing from theory/contract
[AMBIGUOUS] knowledge-base/client-first-class-map.json:class_groups.layout — `[component]_[element]-wrapper` pattern signals "image, text, button, card, or media wrapper" but bundles wrapper roles that CF distinguishes (`_image-wrapper`, `_text-wrapper`, `_card-wrapper`, `_component`); the suffix `-wrapper` vs CF V2 `_wrapper` after a more specific role is inconsistent
[AMBIGUOUS] knowledge-base/client-first-class-map.json:class_groups.advanced_layout — `align-center` mapped to `margin: auto` but CF docs do not specify the implementation; behavior is also partially redundant with `margin-horizontal` + `margin-auto` direction utilities
[AMBIGUOUS] knowledge-base/client-first-class-map.json:class_groups.text_style — `text-style-muted` (`opacity: muted token`), `text-style-link` (`text-decoration: underline`), `text-style-quote` (`font-style: italic` + `border-left`) each invent a specific CSS implementation; CF docs do not specify values, only class names — these are project assumptions
[AMBIGUOUS] knowledge-base/client-first-class-map.json:class_groups.button — `class_strategy: "required_global"` for `button` and `class_strategy: "combo_class"` for `is-secondary`/`is-text` is correct vs CF, but the JSON does not capture CF's rule that base `button` is the primary style and `is-secondary`/`is-text` are the only shipped combo variants
[AMBIGUOUS] agentic/prompts/write-html-contract.md:Layer 1 — `section-style-dark`, `section-style-brand` shown without `is-` prefix; the file calls them "global style combos" but they are not standard CF utility classes (likely CF V2 examples referenced from `section-style-dark` global add-on, but the exact pattern isn't confirmed in the fetched CF docs)
[AMBIGUOUS] agentic/prompts/write-html-contract.md:Layer 2 — `text-size-huge` listed in typography utility table (line 109) vs class-map WRONG finding above and CF utility-systems not shipping `huge`; the contract contradicts the class-map and the docs
[AMBIGUOUS] knowledge-base/client-first-class-map.json:class_groups.advanced_layout — `aspect-ratio-portrait` (3/4) and `aspect-ratio-landscape` (4/3) values are wrong (existing audit) and the JSON also omits the `aspect-ratio-custom` flexibility that CF V2 ships for project-specific ratios
[AMBIGUOUS] agentic/specs/figma-to-client-first-mapping.md:Section C — container-size thresholds (`>=1200px → large`, `900-1199 → medium`, `<900 → small`) are presented as CF rules but CF does not publish these thresholds; they are a project choice
[AMBIGUOUS] agentic/specs/figma-to-client-first-mapping.md:Section D — padding-section thresholds (`>=120px → large`, `64-119 → medium`, `<64 → small`) are presented as CF rules but CF does not publish these thresholds; project choice
[AMBIGUOUS] agentic/specs/figma-to-client-first-mapping.md:Section A — "FRAME | named 'header' within a section → <header>" maps any Figma "header" frame to the `<header>` tag, but CF semantic-html-tags notes `<header>` "cannot be placed within a `<footer>`, `<address>` or another `<header>` element" and is most commonly for the navbar — section sub-header usage is "flexible" but the rule is permissive in the doc
[AMBIGUOUS] agentic/prompts/write-html-contract.md:Layer 1 — section-styling note treats "section-style-dark" and "section-style-brand" as globally reusable add-on classes but does not state where the file/class-style lives in the Webflow style guide or the folder convention (CF folders-strategy: where do these belong?)
[AMBIGUOUS] knowledge-base/client-first-class-map.json:class_groups.color — class_strategy `variable_backed_utility` listed for text/background/border color, but does not encode CF variables rule that utility classes link to *semantic* variables (not primitives) — see primitives-vs-semantic MISSING above
[AMBIGUOUS] agentic/prompts/write-html-contract.md:Hard Rules — "No layout utilities" rule correct, but does not capture CF classes-strategy-2 explicit "Stack margin with margin" / "No new styles on stacked utility globals" companion rules
[AMBIGUOUS] knowledge-base/client-first-theory.md:Chapter 2 — says `padding-global` is "Located directly inside section" as if fixed, vs CF core-structure allowing it to be parent/child of `container-large`; the doc treats the most common case as the only case
[AMBIGUOUS] knowledge-base/client-first-theory.md:Chapter 4 — covers spacing wrappers and REM units but omits CF spacing-strategy rule "Don't apply spacing utility classes to typography elements" — the central use-case the wrapper pattern was designed to address

---

## Ground-Truth Reconciliation (live Client-First V2.2, 2026-06-03)

Source: Webflow MCP live read of site `6a1fa213c04827556dcac7b5`.

| Finding (line # in original) | Status | Evidence |
|---|---|---|
| `text-weight-medium` not in CF | REJECTED | Class exists on live site. V2.2 ships 6 weights: light/normal/medium/semibold/bold/xbold |
| `text-size-huge` not in CF | CONFIRMED | Not on live site. V2.2 size scale: tiny/small/regular/medium/large |
| `text-size-regular` missing from catalog | CONFIRMED | Exists on live site. Added to class-map v0.5.0 |
| `aspect-ratio-portrait` = 3/4 (our catalog) | CONFIRMED as BUG | Real value = 2/3. Fixed in class-map v0.5.0. Also has object-fit:cover baked in |
| `aspect-ratio-landscape` = 4/3 | CONFIRMED as BUG | Real value = 3/2. Fixed |
| CF has no layout utilities (our rule) | SUPERSEDED | V2.2 ships flex-horizontal/vertical, gap-*, grid-N-col, grid-autofit/autofill, display-contents, overflow-*, align-center. Rule was based on V1 / old docs |
| Stacking rule "3-4 max" vs CF spec "4 absolute max" | CONFIRMED | CF spec correct; updated to 4 absolute max |
| `section-style-dark` not using is- prefix | CONFIRMED | Section add-on classes are not combos; updated language in write-html-contract.md |
| padding-section nesting (inside container vs on padding-global) | CONFIRMED GAP | CF best practice: apply padding-section on padding-global div to reduce nesting. Noted in docs |
| `_component` suffix convention | CONFIRMED | live site: `nav_component` (wrapper), `nav_brand` (child), `nav_menu_link` (nested). Added to mapping spec |
| CF has size variables (our claim: No) | CONFIRMED V2.2 HAS THEM | Layout + Sizes + Typography collections exist. CF V2.2 fully variable-backed. Old doc claim outdated |
| Color class double-dash convention | REJECTED | Double-dash = CSS variable name (--_theme---text-color--primary). Class name = single dash (text-color-primary). Auditor conflated the two |
| Gap rem tokens 4, 5 invalid | REJECTED | Spacing scale goes to 12rem (xxhuge). Gap tokens valid |
| `margin-horizontal`, `margin-vertical` missing | CONFIRMED | Exist on live site. Added to class-map |
| `spacing-clean` exists | CONFIRMED | Verified on live site |
| `inherit-text-color` and related | CONFIRMED | `inherit-text-color`, `inherit-text-weight`, `inherit-text-size`, `inherit-text-decoration`, `inherit-border-radius` all exist. Added to catalog |
| `text-style-1line`, `text-style-balance`, `text-style-pretty` | CONFIRMED | All exist on live site. Added to catalog |
| `button is-brand` / `button is-outline` (our examples) | CONFIRMED as BUG | Not in CF V2.2. Only `is-secondary` and `is-text` ship as button combos |
| Spacing is literal rem (our guidance) | SUPERSEDED | Spacing is variable-backed. Utilities reference Layout variables that auto-shift at tablet/mobile via collection modes |
| "Case 4 breakpoint custom class for spacing" | SUPERSEDED | Variable modes handle spacing/type responsive shifts automatically. Case 4 now applies only to structural reflow |
