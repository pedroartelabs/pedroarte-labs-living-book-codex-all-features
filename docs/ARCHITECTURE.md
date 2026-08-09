# Architecture

## Three layers

### ENGINE
Reusable literary production platform.

### BOOK_PACKAGE
One work's literary DNA.

### RUNTIME
Generated merge of engine + package. The runtime owns execution state and artifacts.

## Composition

```text
engine/ENGINE_GRAPH.yaml
          +
books/<slug>/BOOK_SPEC.yaml
          +
books/<slug>/BOOK_GRAPH.yaml
          +
book-specific agents/rules/protected scenes
          |
          v
runtime/<slug>/TASK_GRAPH.yaml
```

The engine generator builds the standard lifecycle dynamically from chapter count, writing waves, feature flags and agent packs.

This means a new book does not need a new 1,500-line orchestration prompt. It needs a new book package.
