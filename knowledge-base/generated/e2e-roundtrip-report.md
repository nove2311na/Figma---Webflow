# End-to-End Round-Trip Evidence

**Generated:** 2026-06-04T09:23:30.600966+00:00
**Workspace:** `workspace/_fixtures/finsweet-template/`
**Source of truth:** backfilled LLM-fillable templates at `.claude/skills/design-system-sync/template/`

## Stages

| Stage | Artifact | Producer | Tier |
|---|---|---|---|
| A | `design-system/figma-contract.json` | `figma-mcp/get_local_variables` | block |
| B | `design-system/webflow-contract.json` | `design-system-sync/task-3-map_variables` | block |
| C | `blueprint.json` | `figma-to-html-architect/task-3` | warn |
| D | `design-system/validations/webflow-sync-preview.json` | `branch-a/mcp-sync-preview` | block |

## Counts

- Variables in figma-contract: **156**
- Variables in webflow-contract: **156**
- Variables aligned by figmaId across A→B: **8**
- Styles in figma-contract: **19**
- Alias chains preserved: **1** (expected: 2)
- figmaId preserved across A→B: **True**
- modes round-tripped across A→B: **True**

## Alignment strategy: figmaId, not name

Figma template names use display paths (`Layout / Gaps / Large`). Webflow template uses CSS slugs (`--_layout---spacing--medium`). Names drift; `figmaId` doesn't. Round-trip alignment walks `figmaId` across all four stages.

## Alias chain evidence

| Webflow name | aliasOf (Figma source figmaId) |
|---|---|
| `_theme---text-color--primary` | `VariableID:example-_neutral-black:9006` |

## Single-variable trace: `_theme---text-color--primary`

**Stage A (Figma side):**
```json
{
  "name": "_theme---text-color--primary",
  "figmaId": "VariableID:example-_theme-text-color-primary:9000",
  "namespace": "_theme",
  "type": "alias",
  "value": "var(--neutral--black)",
  "modes": {
    "default": "var(--neutral--black)",
    "dark": "var(--neutral--white)"
  }
}
```
**Stage B (Webflow side, after `map_variables`):**
```json
{
  "name": "_theme---text-color--primary",
  "figmaId": "VariableID:example-_theme-text-color-primary:9000",
  "webflowId": "VariableID:wf-466c408412",
  "namespace": "_theme",
  "type": "alias",
  "value": "var(--neutral--black)",
  "modes": {
    "default": "var(--neutral--black)",
    "dark": "var(--neutral--white)"
  },
  "aliasOf": "VariableID:example-_neutral-black:9006"
}
```
**Diffs vs Stage A:**
- `figmaId`: **VariableID:example-_theme-text-color-primary:9000** → **VariableID:example-_theme-text-color-primary:9000** (unchanged)
- `modes`: **OrderedDict([('default', 'var(--neutral--black)'), ('dark', 'var(--neutral--white)')])** → **OrderedDict([('default', 'var(--neutral--black)'), ('dark', 'var(--neutral--white)')])** (unchanged)
- `webflowId`: <none> → **VariableID:wf-466c408412** (added by write step)
- `aliasOf`: <none> → **VariableID:example-_neutral-black:9006** (set by `map_variables` for theme aliases)

## Multi-mode evidence

Variables with multiple modes (subset):

| figmaId | modes |
|---|---|
| `VariableID:example-_brand-blue:9005` | `OrderedDict([('default', '#2d62ff'), ('dark', '#d9e5ff')])` |
| `VariableID:example-_neutral-black:9006` | `OrderedDict([('default', '#000'), ('dark', '#fff')])` |
| `VariableID:example-_theme-text-color-primary:9000` | `OrderedDict([('default', 'var(--neutral--black)'), ('dark', 'var(--neutral--white)')])` |

## Blueprint token references

`blueprint.json` references variables by **figmaId**, not name. Names drift; figmaId doesn't.

Sample section:

```json
{
  "name": "hero",
  "tag": "section",
  "class": "section_hero",
  "layers": [
    {
      "tag": "h1",
      "class": "heading-style-h1",
      "text": "Finsweet Client-First V2.2",
      "tokenRefs": [
        {
          "property": "font-size",
          "figmaId": "VariableID:example-_brand-blue:9005"
        },
        {
          "property": "color",
          "figmaId": "VariableID:example-_focus-width:9004"
        }
      ]
    }
  ]
}
```

`tokenIndex` (sample):

```json
{
  "VariableID:example-_brand-blue:9005": {
    "figmaName": "_brand--blue",
    "webflowName": "_brand--blue"
  },
  "VariableID:example-_focus-width:9004": {
    "figmaName": "_focus--width",
    "webflowName": "_focus--width"
  },
  "VariableID:example-_font-weight-bold:9007": {
    "figmaName": "_font-weight--bold",
    "webflowName": "_font-weight--bold"
  },
  "VariableID:example-_layout-spacing-medium:9003": {
    "figmaName": "_layout---spacing--medium",
    "webflowName": "_layout---spacing--medium"
  },
  "VariableID:example-_neutral-black:9006": {
    "figmaName": "_neutral--black",
    "webflowName": "_neutral--black"
  }
}
```

## Validation gate result

Command: `python3 scripts/validation/validate_artifacts.py --workspace _fixtures/finsweet-template --tier block`
Exit code: **0** (PASS)

```
[BLOCK] OK   workspace/_fixtures/finsweet-template/design-system/webflow-contract.json
[BLOCK] OK   workspace/_fixtures/finsweet-template/design-system/figma-contract.json
[BLOCK] OK   workspace/_fixtures/finsweet-template/design-system/client-first-baseline-contract.json
[BLOCK] OK   workspace/_fixtures/finsweet-template/design-system/validations/webflow-sync-preview.json
[BLOCK] OK   workspace/_fixtures/finsweet-template/write-audit-log.jsonl

Summary: block=5P/0F  warn=0P/0F  log=0P/0F
```

## Verdict

**FAIL** — figmaId + modes + alias chains survive the Figma → Webflow round-trip; validation gate exits 0.
