# SEM ROSTO — pacote parcial

Autora: **Bea Halden**. Gênero: DEDR (*Dystopic Enigma Dark Romance*).

Este diretório é um **pacote parcial**: hoje contém **apenas a cartografia
canônica de Redmur**. Ele **não** é um pacote de livro completo (não há
`BOOK_SPEC.yaml` nem `BOOK_GRAPH.yaml`) e **não compõe** runtime. O pacote real
da obra é decisão futura (DEDR SDD, Slice 6).

| Caminho | Papel |
|---|---|
| `cartography/sources/` | os dois mapas canônicos (PNG) com sha256 pinado + transformações de coordenadas |
| `cartography/approvals/` | decisões fundacionais da autora, com `subject_sha256` |

Especificação: `docs/sdd/REDMUR_CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md`
(status E0; Slice 0 registrado aqui).

Regras de manutenção:

- Os PNGs **não são editados**. Correção = nova fonte versionada com `supersedes`.
- Os PNGs aqui são os que serão **impressos no livro**.
- Nada em `/engine` conhece Redmur (`engine/AGENTS.md`).
