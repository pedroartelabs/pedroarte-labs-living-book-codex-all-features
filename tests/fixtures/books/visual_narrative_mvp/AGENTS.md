# Book package: Prova de Mesa do Canon Visual

Pacote de teste, não um livro de catálogo. Existe exclusivamente para
`tests/test_compose_regression.py` provar que `features.visual_narrative.enabled: true`
(capability `BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM`) produz o grafo esperado —
`T042_VISUAL_DISCOVERY`, `T043_VISUAL_NARRATIVE_CANON`,
`T044_VISUAL_CANON_SNAPSHOT`, `T311_VISUAL_STATE_REALIZATION`,
`T312_VISUAL_CANON_SNAPSHOT`, `T698_EDITION_PLAN`, `T707_PRINT_GEOMETRY` e
os quatro validadores `V_VISUAL_*` — sem alterar o compositor para nenhum
outro livro.

Book-specific literary DNA only. Nenhum agente novo, nenhuma alteração em
`/engine`.
