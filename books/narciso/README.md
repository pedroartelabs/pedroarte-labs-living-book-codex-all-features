# Narciso — pacote de livro

Autora: **Bea Halden**. Dark Romance psicológico e gótico, releitura adulta e
livre do mito de Eco e Narciso.

Este pacote é o **Slice 1** de `docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md`: o DNA
narrativo da obra, sem nenhuma alteração no motor.

| Arquivo | Papel |
|---|---|
| `CREATIVE_BRIEF.md` | pitch, contrato com o leitor, proibições |
| `BOOK_CONSTITUTION.md` | tese interna e leis dramáticas |
| `BOOK_SPEC.yaml` | capítulos, waves, features, agent packs |
| `chapter_architecture.yaml` | os 33 capítulos palíndromos |
| `immutable_rules.yaml` | `IR-N01..IR-N16` |
| `protected_scenes.yaml` | 12 cenas protegidas |
| `quality_profile.yaml` | métricas diagnósticas |
| `text_quality.yaml` | clichês da obra (estende a base do motor) |
| `planning/` | fonte mítica, delta de adaptação, voz, mapa do Myth DNA, elenco, léxicos |
| `seeds/INTERPRETIVE_CANON.seed.yaml` | semente do canon de leituras: hipóteses, evidências, amor, desejo, releitura |
| `INTERPRETIVE_CANON_RUNBOOK.md` | como manter `canon/NARCISO_INTERPRETIVE_CANON.yaml` no runtime |
| `agents/` | `NARCISSUS_AMBIGUITY_GUARDIAN`, `DESIRE_DECAY_GUARDIAN` |
| `planning/NARCISSUS_VISUAL_BIBLE.md` | bíblia visual: tese, paleta, prata como acabamento, luz, vetos |
| `planning/FACE_CANON.seed.md`, `planning/CHARACTER_VISUAL_BIBLE.seed.md` | identidade FV-NARCISO-01, corpo, reflexo, declínio |
| `seeds/VISUAL_NARRATIVE_CANON.seed.yaml` | canon visual: FIG-NARCISO, 7 símbolos, sigil, capa, acabamentos |
| `seeds/VISUAL_CANDIDATES.seed.yaml` | variantes de capa (candidatos) |
| `BOOK_GRAPH.yaml` | validadores da obra nos gates e tarefas T018N/T019N/T021N/T20NN |
| `validators/validate_narciso.py` | validador da obra: `package`, `plan`, `wave`, `final`, `--snapshot-as` |

Decisões humanas registradas (2026-09-15): Narciso na capa por fragmento do
rosto; sem hipótese de gêmeo; 33 capítulos palíndromos com Coro; capítulo 18
com teto de explicitude `SENSUAL`; compulsão modelada como capacidade de
recusa reduzida.

Pendentes (não bloqueiam este slice): OQ-N6 (prata como acabamento), OQ-N7
(quantidade de pranchas e cor do miolo), OQ-N9 (última evidência — adotada a
recomendação F-C), OQ-N12 (nomes próprios — adotadas as propostas da SDD).
