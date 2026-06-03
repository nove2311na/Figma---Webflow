# 04 — Phase 2: Client-First Library Contract

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## 1. Bối cảnh

CSS Client-First thật phải là machine-readable contract. LLM không được dùng class “nghe có vẻ đúng”. Research examples chỉ là conceptual nếu class chưa có trong contract.

## 2. Create files

```text
tools/css_indexer/parser.py
tools/css_indexer/classifier.py
tools/css_indexer/contract_builder.py
scripts/index_css_library.py
scripts/gates/validate_css_contract.py
scripts/gates/validate_css_index.py
source-css/README.md
```

Ensure source CSS exists:

```text
source-css/normalize.css
source-css/webflow.css
source-css/client-first-v2-2.webflow.css
```

## 3. CLI

```bash
python scripts/index_css_library.py   --normalize source-css/normalize.css   --webflow source-css/webflow.css   --client-first source-css/client-first-v2-2.webflow.css   --out knowledge-base/generated
```

## 4. Generated outputs

```text
knowledge-base/generated/client-first-library-contract.json
knowledge-base/generated/css-variable-index.json
knowledge-base/generated/css-class-index.json
knowledge-base/generated/css-selector-index.json
knowledge-base/generated/css-property-value-index.json
knowledge-base/generated/css-breakpoint-index.json
knowledge-base/generated/webflow-native-class-index.json
```

## 5. Parser requirements

Extract:
- all CSS variables including breakpoint overrides;
- all classes and combo class selectors;
- selectors and pseudo selectors;
- media query scope;
- property/value declarations;
- Webflow native `.w-*` classes;
- styleguide-only `fs-styleguide_*` classes.

Combo class rule:
```text
.button.is-secondary = class button + combo is-secondary
not one class named button.is-secondary
```

## 6. Contract shape

```json
{
  "version": "1.0.0",
  "source": {
    "normalize_css": "source-css/normalize.css",
    "webflow_css": "source-css/webflow.css",
    "client_first_css": "source-css/client-first-v2-2.webflow.css",
    "client_first_css_hash": ""
  },
  "strict_mode": true,
  "allowed_classes": [],
  "allowed_combo_classes": [],
  "allowed_variables": [],
  "allowed_selectors": [],
  "breakpoints": [],
  "reserved_webflow_classes": [],
  "styleguide_only_classes": [],
  "structural_convention_classes": ["page-wrapper", "main-wrapper"],
  "forbidden_in_final_html": ["fs-styleguide_*"],
  "invalid_until_contract_proves": ["button_component", "card_component", "hero_layout"]
}
```

## 7. Class categories

- spacing: `padding-*`, `margin-*`, `spacer-*`;
- gap: `gap-*`;
- grid: `grid-*`;
- flex: `flex-*`;
- typography: `heading-style-*`, `text-size-*`, `text-weight-*`, `text-style-*`;
- color: `text-color-*`, `background-color-*`;
- components/custom: `button`, `button-group`, `form_input`, `nav_component`, `section_*`;
- native: `.w-*`;
- styleguide-only: `fs-styleguide_*`.

## 8. Update curated map

Update `knowledge-base/client-first-class-map.json`:

```json
{
  "_note": "Curated interpretation only. Generated client-first-library-contract.json is source of truth. If conflict, generated contract wins."
}
```

## 9. Gate

`validate_css_contract.py` fails if:

```text
[x] contract missing
[x] CSS hash missing
[x] allowed_classes empty
[x] allowed_variables empty
[x] known classes missing: button, padding-global, container-large, heading-style-h1, text-size-medium, form_input, nav_component, grid-2-col
[x] known variables missing: --_layout---spacing--medium, --_layout---spacing--global-padding, --_theme---text-color--primary
[x] fs-styleguide_* not marked styleguide-only
[x] .w-* not marked native/reserved
```

## 10. Done checklist

```text
[x] CSS indexer tool exists.
[x] Contract generated.
[x] CSS indexes generated.
[x] Contract gate passes.
[x] Class-selection rules reference contract.
[x] Curated map no longer source of truth.
```
