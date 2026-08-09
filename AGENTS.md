# Pedro Arte Living Book Engine v1

This repository is an agent-first literary production engine.

## Mandatory startup

1. Read `/README.md`.
2. Read `/CODEX_ENGINE_BOOTSTRAP_PROMPT.md` when bootstrapping a book runtime.
3. Read `/engine/ENGINE_GRAPH.yaml` and `/engine/IMPLEMENT.md`.
4. Select exactly one book package under `/books/`.
5. Compose a runtime with `python engine/scripts/livingbook.py compose --book <book-package>`.
6. Execute only READY tasks from the runtime graph.
7. Explicitly spawn subagents declared by task policy and wait for required results.
8. When a gate declares custom validators and its dependencies are complete, run `python scripts/runtime_taskgraph.py validate-gate <GATE_ID>`.
9. Run acceptance checks and blocking gates.
10. When validation fails: STOP. FIX. REVALIDATE. CONTINUE.
11. Persist project state and decision logs.
12. A book is not complete until the actual KDP cover JPEG and exactly five actual Instagram Story JPEGs pass `GATE_MEDIA_ASSETS`.

## Separation rule

`/engine` is reusable and must not contain book-specific canon, character names, chapter titles, motifs, final sentences, genre vetoes, or world rules.

`/books/<slug>` contains the literary DNA of one work.

`/runtime/<slug>` is generated. Do not hand-edit generated engine files unless a repair task explicitly requires it.

## Ownership

- The repository is memory.
- CANON_GUARDIAN owns canon mutations.
- LEAD_NOVELIST owns final prose.
- EXECUTIVE_EDITOR resolves editorial conflicts.
- Review agents report findings; they do not silently rewrite manuscript prose.

## Literary priority

Process exists to protect literature, not replace it.
