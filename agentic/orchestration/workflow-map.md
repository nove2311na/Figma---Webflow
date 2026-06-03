# Workflow Map

## Phase 0: Safety & Audit
- **Trigger**: New compile run or page transition.
- **Steps**: Verify archive cleanup, check target details, validate folder boundaries.

## Phase 1: CSS Contract & Library
- **Trigger**: Safety gate passed.
- **Steps**: Compile CSS Library Contract from normalize/webflow/client-first CSS sources.

## Phase 2: Figma Extraction
- **Trigger**: Library contract established.
- **Steps**: Extract raw Figma context and serialize into a stable node bundle.

## Phase 3: Design-System Sync
- **Trigger**: Node bundle saved.
- **Steps**: Sync figma color/typography/spacing tokens against the CSS contract.

## Phase 4: Component Registry & Signatures
- **Trigger**: Design-system synced.
- **Steps**: Match elements against known components and structure topologies.

## Phase 5: Figma Normalization
- **Trigger**: Component matching done.
- **Steps**: Recover generic names, auto-layouts, and snap raw colors.

## Phase 6: Semantic IR Resolution
- **Trigger**: Normalization tree ready.
- **Steps**: Resolve tag intents and Client-First class choices strictly.

## Phase 7: HTML Blueprint & Render QA
- **Trigger**: Semantic IR tree ready.
- **Steps**: Generate logical blueprint, render physical HTML, and run quality gates.

## Phase 8: Asset & Alt policy
- **Trigger**: HTML compiled.
- **Steps**: Create asset manifest and enforce accessibility alt rules.

## Phase 9: Chunk Slicing & Golden Benchmarks
- **Trigger**: Alt policy verified.
- **Steps**: Slice page HTML into section chunks and benchmark accuracy against fixtures.

## Phase 10: Webflow Native Plan
- **Trigger**: Benchmarks passed.
- **Steps**: Compile section chunks into serialized native build plans.

## Phase 11: Approval & Deployment
- **Trigger**: Plan validated.
- **Steps**: Present plan to user, wait for approval, and execute branch mutations sequentially with audit logging.
