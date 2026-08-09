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

## Stop-and-fix

A blocking failure is not a note. It is a stop condition.

STOP. FIX. REVALIDATE. CONTINUE.
