# Component Signature Matching Specification

This document defines the rules, metrics, and algorithm used to match Figma node instances against registered component signatures.

## Matching Levels

- **Exact Match** (Confidence $\ge 0.95$):
  - Structurally, topologically, and name-wise identical.
  - Maps directly with no overrides.
- **Usable Match** ($0.85 \le$ Confidence $< 0.95$):
  - Identical layout topology but contains minor spacing, font size, or design token overrides.
  - Maps with style overrides.
- **Candidate Match** ($0.60 \le$ Confidence $< 0.85$):
  - Shares visual and naming similarities but exhibits structural discrepancies (e.g. missing child elements or extra unexpected layers).
  - Triggers a compiler warning. Requires user intervention or manual matching override.
- **No Match** (Confidence $< 0.60$):
  - Does not match any known signatures. Treated as custom markup or layout primitives.
  - In **strict mode**, any "No Match" on a known Figma component instance stops execution.

## Signature Criteria

Each signature in `knowledge-base/component-signatures.json` defines matching criteria:

1. **Name Matching (`name_pattern`)**:
   - A regular expression checked against the Figma node name.
2. **Node Type (`node_type`)**:
   - Matches the Figma element type (e.g., `INSTANCE`, `FRAME`, `TEXT`, `RECTANGLE`).
3. **Layout Topology (`layout_topology`)**:
   - Specifies child element counts, order, and node types/roles.
   - For example, a `Card` layout signature expects children matching image/text/button roles.
4. **Token Cluster (`token_cluster`)**:
   - Key design tokens (padding, gap, borders, background, font-size) or class suffixes.
5. **Repeated Patterns (`repeated_patterns`)**:
   - Identifies repeated grids/lists (e.g., a Button Group containing multiple buttons).

## Scoring Algorithm

The match confidence is calculated as a weighted average of four scores:

$$S_{\text{total}} = w_1 S_{\text{name}} + w_2 S_{\text{type}} + w_3 S_{\text{topology}} + w_4 S_{\text{tokens}}$$

Recommended default weights:
- $w_1$ (Name match): 0.20
- $w_2$ (Node type match): 0.10
- $w_3$ (Layout topology): 0.50
- $w_4$ (Token/class cluster): 0.20

### 1. Name Score ($S_{\text{name}}$)
- $1.0$ if the name matches the regex exactly.
- $0.5$ if the name contains the component name as a substring.
- $0.0$ otherwise.

### 2. Node Type Score ($S_{\text{type}}$)
- $1.0$ if the node type matches.
- $0.0$ otherwise.

### 3. Layout Topology Score ($S_{\text{topology}}$)
- Evaluates the child node constraints.
- Score is calculated as:
  $$S_{\text{topology}} = \frac{\text{Number of satisfied child role rules}}{\text{Total number of child role rules}}$$
- Also takes into account minimum and maximum child bounds.

### 4. Token Cluster Score ($S_{\text{tokens}}$)
- Matches key CSS classes or styling property existence.
- $1.0$ if all required styles/classes match.
- Evaluates partial matches line-by-line.

## Strict Mode Enforcement
In **strict mode**:
- If an instance matches a signature with confidence $< 0.85$, it is flagged as a blocker.
- The matcher records all matching errors in `workspace/reports/component-match-report.json`.
- The compilation step is aborted.
