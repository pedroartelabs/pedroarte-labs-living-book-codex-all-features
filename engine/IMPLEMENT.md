# Generic Living Book Execution Runbook

The engine composes one `BOOK_PACKAGE` into one runtime DAG.

## Startup

1. Validate engine.
2. Validate selected book package.
3. Compose runtime.
4. Read runtime `AGENTS.md`, `IMPLEMENT.md`, `TASK_GRAPH.yaml`, and project status.
5. Repair blocking failures first.
6. Otherwise execute READY tasks on the earliest critical path.

## Runtime task lifecycle

A task is READY only when all dependencies and gates are successful and required inputs exist.

When a gate has `custom_validators`, it remains `VALIDATION_REQUIRED` after dependency completion. Run `python scripts/runtime_taskgraph.py validate-gate <GATE_ID>`. The gate is approved only after all declared validator commands pass.

Tasks may explicitly declare `spawn`. Spawn those subagents, provide scoped inputs, wait for required outputs, then synthesize.

## Canon

Only CANON_GUARDIAN mutates the runtime canon registry.

Writers may propose continuity facts but may not silently promote them to canon.

## Writing waves

The standard generator builds waves from `BOOK_SPEC.yaml`.

Each wave follows:

1. preflight;
2. parallel writing according to writer groups;
3. merge;
4. parallel review;
5. editorial synthesis;
6. lead-novelist revision;
7. canon update;
8. validation;
9. approval.

## Protected scenes

Protected scenes are book-defined. The engine only knows the generic audit protocol.

## Visual production

One primary image per chapter is the engine default when `features.images.enabled=true`.

Recurring faces must pass FACE_CANON validation when the book uses recurring characters.

## Living Sound

Living Sound is the physiology of sound in the work. Final sound architecture is derived after manuscript freeze.

## KDP

Current KDP requirements must be refreshed from official Amazon documentation when network access is available. If freshness cannot be verified, emit a capability blocker instead of pretending current validation.

## Mandatory final media assets

For every book, briefs and promotional ideas are not final media assets. `features.media_package.enabled` is mandatory, and before delivery can complete the runtime must execute both production tasks:

1. `T801_KDP_BOOK_COVER`: create `media/outputs/cover/BOOK_COVER_KDP.jpg` as an actual 1600 × 2560 px JPEG, RGB, at least 300 DPI and below 50 MB;
2. `T802_INSTAGRAM_STORIES`: create exactly five actual commercial Story JPEGs, `story_01.jpg` through `story_05.jpg`, each 1080 × 1920 px, RGB and at least 300 DPI.

After both tasks are approved, run `python scripts/runtime_taskgraph.py validate-gate GATE_MEDIA_ASSETS`. The book is not delivery-ready until this blocking gate passes. A cover brief, Story ideas, prompts, mockups, PNG sources or incorrectly named files do not satisfy the gate.

The KDP JPEG is the eBook marketing/front-cover asset. A paperback or hardcover print wrap remains a separate PDF whose back cover, spine and bleed depend on final production parameters.

## Stop-and-fix

A blocking failure is not a note. It is a stop condition.

STOP. FIX. REVALIDATE. CONTINUE.
