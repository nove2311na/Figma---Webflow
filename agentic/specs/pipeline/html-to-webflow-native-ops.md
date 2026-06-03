# HTML to Webflow Native Ops Specification

This spec outlines the compiler mandates for translating local HTML section chunks into safe, serialized Webflow Native Build Plans.

## Build Plan Compilation Rules

1. **Compilation Only**: The compile phase must not trigger actual Webflow mutations. It parses local HTML section chunks and writes logical plan files only.
2. **Allowed Native Exceptions**: The build plan compiler may output native operations for structures requiring specific native features:
   - Navigation bars (`[nav]`, `nav_component`)
   - Forms and Form fields (`w-form`, `form_component`)
   - Tabs, Dropdowns, and Sliders
   - Rich Text wrappers (`text-rich-text`)
   - Asset IDs and image bindings
3. **Execution Restrictions**: Webflow writes must carry the following pre-requisites:
   - Approved local HTML
   - Approved Asset manifest
   - Approved Section manifest
   - Compiled Native build plan
   - Rollback and QA check plan
4. **Data Marker Lineage**: Every Webflow element must carry `data-section`, `data-component`, and `data-figma-node` properties to trace Webflow elements back to Figma nodes.
