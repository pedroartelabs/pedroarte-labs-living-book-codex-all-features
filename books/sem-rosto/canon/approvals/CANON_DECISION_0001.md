# Decisões — SEM ROSTO Canonical Story System 0001

**Sujeito:** `docs/sdd/SEM_ROSTO_CANONICAL_STORY_SYSTEM_SDD_v0.1.md` (Open Questions OQ-SR-01, 02, 04, 05)
**Aprovador:** Pedro, em sessão (2026-09-21): "01-sim; 02-sim; 04-não, os mistérios já foram
discutidos no dossiê, pode seguir como achar melhor; 05-decida."
**Registrado em:** 2026-09-21

subject_sha256 (SDD antes destas decisões): 289ec9181c8251bb7bc5624f4b174dd5b7b8008bcbda6171aa7cee7b1be56ca3

As decisões de OQ-SR-04 e OQ-SR-05 foram **delegadas** pelo aprovador. Foram
tomadas pelo critério mais conservador compatível com o dossiê congelado:
nenhuma delas cria fato novo; todas podem ser revistas por decisão humana
posterior (CANON_DECISION_0002+).

| OQ | Decisão | Tomada por |
|---|---|---|
| OQ-SR-01 | Freeze aprovado → `CANON_FREEZE_0001.md` | aprovador |
| OQ-SR-02 | Dossiê versionado em `books/sem-rosto/canon/sources/` com sha256 pinado | aprovador |
| OQ-SR-04 | **Nenhum mistério reservado vira pergunta `Q-*` do canon interpretativo agora.** Todos ficam como `MYS-*` (escopo e teto por livro) + `UNK-SR-*`/`PRO-SR-*` no registry, exatamente como o dossiê os trata (§12.4, §14.9, §16.8, §17, §18). No Livro 1 o canon interpretativo terá apenas `Q-MAP-AUTHOR` (`NEVER`, decisão cartográfica OQ-CART-02b) e `Q-CRIME-B1` (`RESOLVED_AT`, quando o crime existir). | delegada |
| OQ-SR-05a | **Local do Six-Month Protocol:** existe, é institucionalmente visível e fisicamente localizável no mundo (R4), e pertence à cartografia existente (não é infraestrutura nova). **Qual lugar do mapa ele é permanece `UNK-SR-CHILD-FACILITY-LOCATION`** (dossiê §17). `Village Clinic` não é presumida. Cenas podem mostrar o prédio e o procedimento visível sem posicioná-lo; cena que exija a posição → `CANON_PROPOSAL_REQUIRED`. | delegada |
| OQ-SR-05b | **Preservation Boundary = limite do District of Civic Preservation** (`BND-ADM-CP` do Mapa A). Extensão continua `UNKNOWN`; a legenda do mapa continua `OFFICIAL_CLAIM`. Não é fronteira internacional (§5, §1.1). | delegada |
| OQ-SR-05c | **Veil House e Transfer Zone** existem na Preservation Boundary (P3: instalação intermediária de entrada; zona de mercadorias), mas **não estão nos mapas**: posição `UNK-SR-VEIL-HOUSE-LOCATION` / `UNK-SR-TRANSFER-ZONE-LOCATION`. Não entram no grafo nem em rotas sem decisão cartográfica; cenas podem mostrar o interior; cena que exija rota de chegada ou posição → `CANON_PROPOSAL_REQUIRED`. | delegada |

## Consequências registradas

- **Por que não criar `Q-*` para mistérios reservados:** uma pergunta interpretativa exige
  interpretações concorrentes escritas (teses). O dossiê não as define; escrevê-las agora seria
  criar canon (ou orientar a narrativa) sem necessidade. Quando o plano do Livro 1 quiser semear
  dupla evidência sobre um mistério reservado, isso entra por proposta.
- **Efeito na cartografia (OQ-CART-20 / CART_OPEN_DECISIONS B4):** `Q-MAP-AUTHOR` deixa de ser a
  "4ª" pergunta `NEVER` — com esta decisão ela é a única do Livro 1, dentro do limite padrão (3)
  de `check_interpretive_canon.py`. A premissa das três perguntas vinha do DEDR §33, que não é canon
  (D-SR-02).
- Nenhum arquivo da cartografia foi alterado por estas decisões. A aplicação de OQ-SR-05b nos dados
  cartográficos (`BND-ADM-CP`) e de D-SR-11 (`LYR-PRE-COFFER`) fica para o slice de integração.
