# SEM ROSTO — pacote parcial

Autora: **Bea Halden**. Gênero: DEDR (*Dystopic Enigma Dark Romance*).

Este diretório é um **pacote parcial**: hoje contém a **cartografia canônica de
Redmur** e a **fonte canônica narrativa** (dossiê congelado). Ele **não** é um pacote de livro completo (não há
`BOOK_SPEC.yaml` nem `BOOK_GRAPH.yaml`) e **não compõe** runtime. O pacote real
da obra é decisão futura (DEDR SDD, Slice 6).

| Caminho | Papel |
|---|---|
| `cartography/sources/` | os dois mapas canônicos (PNG) com sha256 pinado + transformações de coordenadas |
| `cartography/approvals/` | decisões fundacionais da autora, com `subject_sha256` |
| `canon/sources/` | dossiê narrativo canônico (`REDMUR_CANON_RESOLUTION_DOSSIER_FINAL.md`, FROZEN, sha256 pinado) |
| `canon/approvals/` | freeze do cânone e decisões do Canonical Story System, com `subject_sha256` |
| `canon/seeds/` | registros canônicos, travas absolutas, gates de livro, mistérios de série e rumores/teorias (apontam para o dossiê por §) |
| `validators/check_sem_rosto_canon.py` | validador do canon narrativo (`--mode package`/`plan`; consultas `--is-true`/`--who-knows`/`--reader-at`/`--mystery`) |

Especificação espacial: `docs/sdd/REDMUR_CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md`
(status E0; Slice 0 registrado aqui).

Regras de manutenção:

- Os PNGs **não são editados**. Correção = nova fonte versionada com `supersedes`.
- Os PNGs aqui são os que serão **impressos no livro**.
- Nada em `/engine` conhece Redmur (`engine/AGENTS.md`).
- O dossiê em `canon/sources/` **não é editado**. Correção = nova resolução (R12+) versionada com `supersedes`.

Especificação narrativa: `docs/sdd/SEM_ROSTO_CANONICAL_STORY_SYSTEM_SDD_v0.1.md` (E0; Slice 0 registrado em `canon/`).
