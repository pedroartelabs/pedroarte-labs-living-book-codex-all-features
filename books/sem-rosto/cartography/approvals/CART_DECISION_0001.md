# Aprovação humana — Cartografia de Redmur, decisões fundacionais 0001

**Sujeito:** `books/sem-rosto/cartography/sources/SOURCES.yaml` (fontes pinadas + transformações)
**SDD:** `docs/sdd/REDMUR_CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md`
**Aprovador:** Pedro, por instrução explícita em sessão.
**Decisões tomadas em:** 2026-09-19 · **Registradas em:** 2026-09-20 (Slice 0)

subject_sha256: 3f8d011d1897f37c05e57bfcfd468d2361f9554824f9f7cfdd4fad89b7b3ced4

## Decisões

| OQ | Decisão da autora |
|---|---|
| OQ-CART-01 | "Considere o mapa dos arredores como uma escala de 100 e Redmur como 7,25% da escala do mapa dos arredores." Lida como razão linear ⇒ Mapa B = 55,86 m/px. **Leitura linear (não de área) ainda a confirmar.** |
| OQ-CART-02 | Os Mapas A e B **existem dentro do mundo** como documentos. |
| OQ-CART-02b | Quem os produziu é discutido e procurado no livro, **nunca revelado** (pergunta `NEVER`; `author: MUST_REMAIN_UNKNOWN`). |
| OQ-CART-03 | Os mapas serão **impressos no livro**, inteiros, inclusive o inset "REDE SUBTERRÂNEA". |
| OQ-CART-05 | Black Thistle Filling Station e Sealed Crypt IV estão **no subterrâneo**, fora do inset; conectividade não declarada. |
| OQ-CART-14 | Velocidades, modificadores e limiares de visibilidade **aprovados** (SDD 16.3, 17.2, 17.3). |
| OQ-CART-15 | As **22 anomalias** do Apêndice B (ANM-A-01..05, ANM-X-01..03, ANM-B-01..14) são `INTENTIONAL_ARTIFACT`; os mapas são impressos como estão. |
| OQ-CART-04 | Slug **`sem-rosto`** e pacote parcial (adotado por padrão; sem objeção). |

## Ainda em aberto

- Confirmar a leitura linear da escala (OQ-CART-01).
- OQ-CART-20: `Q-MAP-AUTHOR` seria a 4ª pergunta `NEVER`; o limite é 3 (`check_interpretive_canon.py`, configurável em `features.living_theory.thresholds`).
