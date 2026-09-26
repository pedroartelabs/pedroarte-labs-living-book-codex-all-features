# SDD v0.1 — `SEM_ROSTO_CANONICAL_STORY_SYSTEM`

> **O dossiê define o que é verdade. Este sistema impede que a história esqueça — e impede que ela saiba cedo demais.**

| Campo | Valor |
|---|---|
| Status | **E0 — PROPOSTA; Slices 0, 1 e 2 concluídos (2026-09-21 a 2026-09-26).** S0: dossiê pinado, freeze aprovado, OQ-SR-01/02/04/05 decididas (tabela abaixo). S1: seeds `CANON_RECORDS`/`HARD_LOCKS`/`BOOK_GATES` e validador `--mode package` (seção 79.1). S2: seeds `MYSTERIES`/`RUMORS`, modo `plan --runtime` (conhecimento, rumor-como-fato, teto de mistério, sincronia de registry) e as consultas `--is-true`/`--who-knows`/`--reader-at`/`--mystery` (seção 79.2). Nenhum comportamento do motor alterado. Próximo: Slice 3. |
| Data | 2026-09-21 |
| Obra | **SEM ROSTO** — autoria **Bea Halden** — gênero DEDR (*Distopic Enigma Dark Romance*) |
| Papel | **Fundação canônica narrativa** da obra (2 de 2). A outra é `REDMUR_CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md` (espacial). Este SDD é o "Story Truth Ledger" que a cartografia referencia por contrato (cartografia §22.4). |
| Tipo | **Canon de obra + validador de obra** (padrão Narciso / cartografia de Redmur), sobre capabilities neutras do motor. **Não** é capability do motor: `engine/AGENTS.md` proíbe canon de obra em `/engine`. |
| Fonte narrativa | `books/sem-rosto/canon/sources/REDMUR_CANON_RESOLUTION_DOSSIER_FINAL.md` — sha256 `7be721624539c6e1c9d5db983e4d643feea4fba77a6a59e0426645ed72cfbf86` — 1975 linhas — **FROZEN** (`approvals/CANON_FREEZE_0001.md`) |
| Base | branch `slice/redmur-cartography`, commit `81e4ff4` + working tree (DEDR, UNSEEN, HDR, RELICS, VAULT, DUAL_PLANE **não commitados** — não tocados por esta SDD) |
| SDDs irmãs | `REDMUR_CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md` (espaço), `DYSTOPIC_ENIGMA_DARK_ROMANCE_SDD_v0.1.md` (kit de gênero), `DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md` (ledger causal), `LIVING_THEORY_ENGINE_SDD_v0.1.md` (canon interpretativo), `REPRESENTATION_INTEGRITY_SDD_v0.1.md` (hard boundaries), `NARCISO_CANONICAL_SDD_v0.1.md` (padrão de canon por obra) |
| Regras aplicadas | `REUSE > EXTEND > CREATE`; `SIMPLICIDADE SEMPRE`; texto em PT-BR, identificadores em inglês; **o dossiê é referenciado, nunca reescrito** |

## Decisões humanas (registradas em 2026-09-21)

Fonte: `books/sem-rosto/canon/approvals/CANON_DECISION_0001.md`. OQ-SR-04 e OQ-SR-05 foram
**delegadas** pelo aprovador e decididas pelo critério mais conservador compatível com o
dossiê congelado — nenhuma cria fato novo.

| OQ | Decisão | Consequência no desenho |
|---|---|---|
| **OQ-SR-01** | Freeze aprovado (`CANON_FREEZE_0001.md`) | o validador roda em modo normal, não `advisory`; `SRC-DOSSIER.freeze.status: FROZEN` |
| **OQ-SR-02** | Dossiê versionado em `books/sem-rosto/canon/sources/` | D-SR-01 resolvido; `SOURCE_HASH_MISMATCH` protege o arquivo |
| **OQ-SR-04** | Nenhum mistério reservado vira `Q-*` agora | mistérios reservados vivem como `MYS-*` + `UNK-SR-*`/`PRO-SR-*`; o canon interpretativo do Livro 1 tem só `Q-MAP-AUTHOR` (`NEVER`) e `Q-CRIME-B1` (`RESOLVED_AT`, quando existir). Resolve D-SR-04 e esvazia OQ-CART-20 (a "4ª" `NEVER` vinha do DEDR §33) |
| **OQ-SR-05a** | Local do Six-Month Protocol: visível, localizável, pertence à cartografia existente; **qual lugar** continua `UNK-SR-CHILD-FACILITY-LOCATION` | D-SR-05 resolvido sem inventar; `Village Clinic` não é presumida; posicionar exige proposta |
| **OQ-SR-05b** | Preservation Boundary = limite do District of Civic Preservation (`BND-ADM-CP`), extensão `UNKNOWN` | D-SR-06 (parte da fronteira) resolvido |
| **OQ-SR-05c** | Veil House e Transfer Zone ficam na Preservation Boundary; posição `UNK-SR-*` (fora dos mapas) | D-SR-06 resolvido; interior pode ser mostrado, rota/posição exige proposta |

## Índice

1. Executive Summary · 2. Purpose · 3. Scope · 4. Non-Goals · 5. Canonical Sources ·
6. Source Precedence · 7. Terminology · 8. Design Principles · 9. Existing Architecture Discovery ·
10. Reuse / Extend / Create Matrix · 11. System Architecture · 12. Canon Data Model ·
13. Canon Status Model · 14. Provenance Model · 15. Hard Lock Engine · 16. World Truth Model ·
17. Character Knowledge Graph · 18. Reader Knowledge Ledger · 19. Public Belief / Rumor Model ·
20. Mystery Graph · 21. Mystery Firewall · 22. Face Disclosure Firewall · 23. Facial Reconstructibility ·
24. Self-Face Rules · 25. Sealed Facial Evidence · 26. Outside Facial Records ·
27. Faceless Expression Language · 28. Non-Facial Identity · 29. Coffer Canon Engine ·
30. Combination Authority · 31. Coffer Touch Semantics · 32. Consent State · 33. Age Semantic Firewall ·
34. Six-Month Child Protocol · 35. Visitor State Machine · 36. Returner State Machine ·
37. Palimpsest Jurisdiction · 38. The Pull · 39. Technology Veil · 40. Identity Stack ·
41. Tattoo Semiotics · 42. Economy Model · 43. Body Gap · 44. Blind Chronology · 45. Missing Forty Years ·
46. Four Archives · 47. Dead Archive · 48. Manfred Power Model · 49. Madre Selka Firewall ·
50. 1% Non-Human Rule · 51. Crime Payoff Model · 52. Fair Play Crime Ledger · 53. Double-Edge Evidence ·
54. Romance State Engine · 55. Relationship Irreversibility · 56. Evidence Integration ·
57. Cartography Integration · 58. Temporal Canon · 59. Dynamic Story State · 60. Canon Context Pack ·
61. Role-Based Canon Access · 62. No Canon Invention Gate · 63. Canon Proposal Workflow ·
64. Canon Mutation · 65. Validation Pipeline · 66. Error Taxonomy · 67. Chapter Snapshot ·
68. Reader Promise Ledger · 69. Book 1 Gates · 70. Future Book Gates · 71. Persistence ·
72. Versioning · 73. Observability · 74. Failure Modes · 75. Security / Spoiler Isolation ·
76. Test Strategy · 77. Migration / Adoption Strategy · 78. Open Questions · 79. Implementation Plan ·
80. Acceptance Criteria ·
Apêndice A — Canon Extraction Map (dossiê → sistema) ·
Apêndice B — Scene Generation Contract (forma renderizada) ·
Apêndice C — Arquivos inspecionados e comandos

Mapeamento das fases pedidas (§81 do prompt):

| Fase | Onde |
|---|---|
| PHASE 0 — Read source | dossiê lido integralmente (1975 linhas); pinagem em 5.2 |
| PHASE 1 — Repository discovery | seção 9 |
| PHASE 2 — Canon extraction map | Apêndice A (+ 5.3) |
| PHASE 3 — Conflict check | 9.4 (D-SR-*) |
| PHASE 4 — Architecture | seções 10–11 |
| PHASE 5 — Data contracts | seções 12–14, 29–32, 59–60, 63, 67–68 |
| PHASE 6 — Gates & validators | seções 15, 21–22, 33, 62, 65–66, 69–70 |
| PHASE 7 — Context pack | seções 60–61, Apêndice B |
| PHASE 8 — State management | seções 59, 64, 67 |
| PHASE 9 — Tests | seção 76 |
| PHASE 10 — SDD | este documento |

---

## 1. Executive Summary

### 1.1 O que é

Um **sistema de governança canônica executável** para SEM ROSTO: canon de
obra em YAML versionado + um validador determinístico da obra + um gerador de
**Canon Context Pack** por cena — tudo ligado às capabilities que o motor já
tem. Ele responde, com referência ao dossiê, perguntas como *"isto é verdade?"*,
*"o personagem sabe disso?"*, *"o leitor já viu isso?"*, *"esta cena revela um
rosto?"*, *"esta pista pode aparecer agora?"*, *"esta cena cria canon novo?"* —
e devolve `PASS`, `PASS_WITH_WARNINGS`, `FAIL` ou `CANON_PROPOSAL_REQUIRED`.

### 1.2 A descoberta que mais moldou o desenho

**O motor já separa, em três artefatos neutros, quase tudo o que o prompt pede
— e a cartografia de Redmur já está esperando por este SDD.**

| Pedido | Já existe como | Onde |
|---|---|---|
| WORLD_TRUTH ≠ CHARACTER_KNOWLEDGE ≠ READER_KNOWLEDGE | `knowledge_delta` + `knowledge_state(knower, chapter)`; `READER` é conhecedor | `engine/scripts/check_causal_ledger.py:1057` |
| Leitor não recebe verdade cedo | `reader_access` por GT + `READER_OMNISCIENCE_LEAK` (INV-12) | `check_causal_ledger.py:742-788` |
| Personagem não age sobre o que não sabe | `acts_on_knowledge` + `INFORMATION_LEAK` (INV-13) | `check_causal_ledger.py:791-825` |
| Consentimento em camadas, coerção nunca é payoff, idade ≥ 18 | bloco `consent`, INV-06..09, `ADULT_SEDUCTION_FAIL` BLOCKER | `check_causal_ledger.py:642, 852-905` |
| Hard boundary de menor | `HARD_BOUNDARY_MINOR_SEXUALIZATION` (HB-01) | `engine/scripts/check_representation.py:279-358` |
| Mistério sem resposta escondida | `resolution_policy: NEVER`, `MUST_REMAIN_UNKNOWN`, `HIDDEN_ANSWER_KEYS` | `engine/scripts/check_interpretive_canon.py:73-125` |
| Incógnitas e inferências proibidas como canon | `unknowns[]`, `prohibited_inferences[].match` | registry (precedente `a_morte`, fixture LTE) |
| Pista justa, twist sem retcon | INV-10/INV-11, evidência `FIRST_READ`/`REREAD`, red herring justo | ledger + canon interpretativo |
| Espaço, rota, tempo de viagem, saída ambígua, mapa do leitor | cartografia S0/S1 (`check_cartography.py`), `KNOWLEDGE_BASELINE`, contrato §22.4 | `books/sem-rosto/cartography/` |
| Canon de obra materializado por tarefa extra + validador da obra | `additional_tasks` + `custom_validators` + `gate_extensions` | `books/narciso/BOOK_GRAPH.yaml` |
| Proposta de canon com dono único | `CANON_PROPOSAL_PROTOCOL`, `unapproved_facts_are_canon: false` | `engine/ENGINE_GRAPH.yaml:242` |
| Checkpoint humano que o motor nunca escreve | `requires_human_approval` + `project_state/APPROVALS/` | `engine/IMPLEMENT.md` |

O que **não existe** — e é exatamente o que torna Redmur Redmur — é pequeno e
nomeável:

1. **Registro das regras do dossiê como canon citável** (id, status,
   proveniência, escopo de livro, lock) — hoje o dossiê é prosa fora do
   repositório.
2. **Status canônico de duas camadas**: *autoridade* (aprovado, desconhecido,
   reservado, capacidade de sistema…) separada de *classe epistêmica* dentro
   do mundo (fato, rumor, teoria, alegação oficial…). É o que impede
   `SYSTEM_CAPABILITY → CANONICAL_INSTANCE` e `RUMOR → FACT`.
3. **Firewalls específicos de Redmur**: rosto (personagem vê ≠ leitor vê),
   reconstrutibilidade, autoimagem, combinação ≠ remoção, toque de cofre,
   semântica etária, Selka, Manfred, 1% não humano.
4. **Estado dinâmico de Redmur** que o ledger não modela: cofres, combinações,
   autorizações, status cívico (Visitor/Returner), eventos faciais, custódia de
   evidência.
5. **Portões de livro** (Book 1 History Lock, contrato de resolução P14) e
   **portões de série** — o LTE, por desenho, recusa perguntas que dependem de
   volume futuro (D-SR-03).
6. **Canon Context Pack por cena**: a interseção mínima de ledger + canon
   interpretativo + registry + cartografia + locks que o escritor pode
   legitimamente receber.

### 1.3 A menor arquitetura que cumpre a missão

```text
MOTOR (0 mudanças no MVP)
  causal ledger · interpretive canon · registry · representation integrity · cartography
  gates · custom_validators · gate_extensions · additional_tasks · CANON_PROPOSAL_PROTOCOL

OBRA — books/sem-rosto/canon/                      (dados; aprovação humana)
  sources/   dossiê pinado (sha256) + SOURCES.yaml
  approvals/ CANON_FREEZE_0001.md (humano) + decisões fundacionais
  seeds/     CANON_RECORDS · HARD_LOCKS · BOOK_GATES · MYSTERIES · RUMORS ·
             COFFERS · CIVIC · JURISDICTION · LEXICON           (8 seeds)
OBRA — books/sem-rosto/validators/check_sem_rosto_canon.py    (1 validador de junção)
OBRA — books/sem-rosto/agents/redmur_canon_warden.toml         (1 revisor consultivo)

RUNTIME (quando o pacote completo existir)
  canon/SEM_ROSTO_CANON.yaml          canon estático materializado (CANON_GUARDIAN)
  canon/SEM_ROSTO_STATE_DELTAS.yaml   estado dinâmico de Redmur, deltas por EV-*   (CANON_GUARDIAN)
  canon/READER_PROMISES.yaml          única parte do "leitor" que é armazenada
  briefs/canon/CH_NN_<scene>_PACK.yaml    gerado (tool), zero token
  canon/snapshots/SEM_ROSTO.CH_NN.yaml    gerado (tool) ao fim de cada capítulo

0 mudanças no motor · 0 gates novos · 0 dependências novas
1 validador · 1 agente de obra · 8 seeds · 3 arquivos de runtime (+ gerados)
Knowledge graph, reader ledger, rumor graph, mystery state, romance state: PROJEÇÕES.
```

### 1.4 O que NÃO é

- **Não** escreve SEM ROSTO, não cria outline, não escolhe o crime, não nomeia protagonistas.
- **Não** guarda verdade que o dossiê não decidiu: `CANON_UNKNOWN` não tem
  conteúdo em nenhum arquivo — por construção (seção 16.3).
- **Não** é um segundo sistema de mistério, de conhecimento ou de espaço:
  referencia `Q-*`, `EVD-*`, `GT-*`, `EV-*`, `RM-*` por id.
- **Não** julga literatura sozinho. O validador prova estrutura e roda
  pré-filtros lexicais; o resíduo semântico (a prosa descreveu um rosto?) é do
  `REDMUR_CANON_WARDEN` e dos revisores existentes. Nunca se finge o contrário.

### 1.5 Recomendação em uma linha

```text
READY_FOR_SLICE_1 = YES  (pinagem + canon records + hard locks + book gates + validador de integridade; 0 mudança no motor)
READY_FOR_BOOK_INTEGRATION = NO até existir o pacote completo de SEM ROSTO (DEDR S6) e OQ-SR-01/04 decididas
```

---

## 2. Purpose

Transformar o cânone consolidado de SEM ROSTO em **restrições verificáveis**
que o Motor de Livros Vivos aplica antes, durante e depois de cada cena, de
modo que:

1. o motor saiba o que é verdade, o que é alegação, rumor, teoria, falsidade,
   desconhecido ou reservado — e nunca confunda essas classes;
2. cada agente receba **só** o que sua tarefa pode legitimamente conhecer;
3. nenhum rosto chegue ao leitor, nenhuma magia vire causa, nenhum menor
   receba semântica erótica, nenhuma combinação vire chave universal;
4. nenhum mistério reservado seja resolvido antes do livro que o permite;
5. nenhuma capacidade do sistema vire instância histórica por acidente;
6. toda lacuna real vire **pergunta à autora**, nunca invenção do escritor.

Princípio (§83 do prompt): **permitir que Bea Halden escreva livremente sem
quebrar Redmur** — o sistema restringe o que é canon, não o que é literatura.

## 3. Scope

| Dentro | Fora |
|---|---|
| Regras P0–P14 e patches R1–R11 do dossiê como registros citáveis | Reescrever, resumir ou "melhorar" o dossiê |
| Status, proveniência, escopo de livro, locks, gates de série | Decidir o que o dossiê deixou `CANON_UNKNOWN` |
| Conhecimento de personagem e leitor (projeção) | Prever interpretação real do leitor |
| Estado dinâmico de Redmur (cofres, combinações, consentimento, status cívico, eventos faciais, custódia) | Motor de simulação; estado não causado por evento |
| Contrato de cena (antes) e extração pós-cena (depois) | Escrever a cena |
| Portões do Livro 1 e estrutura para livros futuros | Decidir o conteúdo do Livro 2 |
| Referência mínima a evidência (id, arquivo, custódia) | O sistema completo REDMUR X-FILES (dossiê §20.1) |
| Integração com a cartografia | Duplicar grafo, rota ou tempo de viagem |

## 4. Non-Goals

Este SDD **não**: escreve SEM ROSTO; cria outline do Livro 1; escolhe o crime;
revela True Chronology; resolve Missing Forty Years, Aquele Dia, Flarry,
Selka, The Pull; cria Manfred novos; revela rostos; cria magia; escreve cenas
sexuais; constrói o REDMUR X-FILES nem o Death/Funeral System (dossiê §20);
duplica o Cartography Graph; decide obras futuras da franquia; converte todo
detalhe do dossiê em tabela (Apêndice A mapeia; a migração é incremental,
seção 77).

Também **não**: cria gate novo, engine, router, graph database, serviço ou
dependência. Se YAML + validador resolvem, é o que se usa (§73 do prompt).

---

## 5. Canonical Sources

### 5.1 Fontes

| id | Fonte | Autoridade | Estado no repo |
|---|---|---|---|
| `SRC-DOSSIER` | `REDMUR_CANON_RESOLUTION_DOSSIER_FINAL.md` | narrativa, histórica, social, institucional, cultural, jurídica, temática | **ausente** (em `~/Downloads/`) — D-SR-01 |
| `SRC-MAP-A` | Mapa canônico da cidade | espacial (geometria = fato) | `books/sem-rosto/cartography/sources/` (pinado) |
| `SRC-MAP-B` | Mapa canônico dos arredores | espacial | idem |
| `SDD-CART` | `REDMUR_CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md` + seeds | tradução computável do espaço | `docs/sdd/` + `books/sem-rosto/cartography/seeds/` |
| `APPROVALS` | decisões humanas registradas | mutações e decisões posteriores | `books/sem-rosto/*/approvals/` |

### 5.2 Pinagem (Slice 0)

```yaml
# books/sem-rosto/canon/sources/SOURCES.yaml
sources:
  - id: SRC-DOSSIER
    title: "REDMUR CANON RESOLUTION DOSSIER — FINAL"
    file: sources/REDMUR_CANON_RESOLUTION_DOSSIER_FINAL.md
    sha256: 7be721624539c6e1c9d5db983e4d643feea4fba77a6a59e0426645ed72cfbf86
    lines: 1975
    baseline: {P: [P0, P14], status: CANON_APPROVED, R: [R1, R11], patch_status: CANON_PATCH_APPROVED}
    freeze: {status: FROZEN, approval: ../approvals/CANON_FREEZE_0001.md}   # OQ-SR-01 (2026-09-21)
    editable: false            # CANON_FROZEN_SOURCE: correção = nova versão com supersedes
```

- `SR-SRC-01 SOURCE_HASH_MISMATCH` (BLOCKER): o arquivo pinado mudou sem nova
  versão de fonte (REUSE do padrão `CG-06` da cartografia).
- Uma nova resolução humana (ex.: R12) entra como **nova fonte**
  `SRC-DOSSIER@R12` com `supersedes` restrito ao escopo que corrige (regra de
  precedência do dossiê §0), nunca por edição do arquivo pinado.
- O dossiê **não é lido por agentes de escrita** (seção 61). É lido por
  humanos e pelo `CANON_GUARDIAN` na materialização; os demais recebem
  registros por id.

### 5.3 O que é extraído e o que fica só no dossiê

| Conteúdo do dossiê | Vira | Exemplo |
|---|---|---|
| Regra operável ("X ≠ Y", "é proibido", "não existe") | registro `CR-*` e, se inviolável, lock `HL-*` | §2.7 → `CR-P0-R1`, `HL-07` |
| Estado declarado `CANON_UNKNOWN` | `UNK-SR-*` (sem conteúdo) + `PRO-SR-*` quando houver inferência a proibir | §17 "causa da morte de Madre Selka" → `UNK-SR-SELKA-DEATH` |
| Mistério reservado | `MYS-*` com `minimum_book` | §18 "Aquele Dia" → `MYS-AQUELE-DIA` |
| Rumor/teoria do mundo | `RUM-*` (existência = canon; conteúdo = rumor) | §14.7 cofre de Selka enterrado → `RUM-SELKA-COFFER` |
| Capacidade do sistema | `CAP-*` com `system_capability_only: true` | §3.5 Sealed Facial Evidence → `CAP-SEALED-FACIAL-EVIDENCE` |
| Portão de livro | `BG1-*` / `BGF-*` | §12.4, §16.8, §21 |
| Frase canônica (§24) | `CR-PHRASE-*` com `usage: TONAL_REFERENCE` — nunca regra de validador | "Selka é uma chave. Nunca a chave." |
| Prosa explicativa, exemplos, justificativas | **fica no dossiê**; registro aponta `source_location` | — |

A lista completa, módulo a módulo, está no **Apêndice A**.

---

## 6. Source Precedence

### 6.1 Ordem adotada

```text
1. SRC-DOSSIER (dossiê final)                          narrativa, história, instituições, cultura, direito, tema
   1a. R1–R11 prevalecem sobre P0–P14 somente no escopo que corrigem (dossiê §0)
2. SRC-MAP-A / SRC-MAP-B                               evidência espacial (geometria = fato)
3. SDD-CART + seeds da cartografia                      tradução computável do espaço
4. SDDs e componentes do motor                          arquitetura técnica
5. Este SDD / o prompt de execução                      instruções de execução
6. CANON_PROPOSALS aprovadas / approvals/               mutações posteriores, com escopo
```

**Divergência registrada (D-SR-13):** o prompt lista o Cartography SDD
(prioridade 2) **acima** dos mapas (prioridade 3); o dossiê (§0, itens 4–5)
coloca os mapas **acima** do Cartography SDD, e o próprio Cartography SDD
concorda ("mapa vence briefing", cartografia §4.1). Como o prompt declara que
não pode substituir fatos do dossiê, e a precedência de fontes **é** um fato
do dossiê, adota-se a ordem do dossiê. Efeito prático: nulo hoje (o SDD-CART
transcreve os mapas e registra divergências como anomalias, sem corrigir).

### 6.2 Regras de precedência operáveis

| id | Regra | Achado |
|---|---|---|
| `SR-PRC-01` | Fato narrativo do dossiê não é alterado por nenhuma fonte de prioridade menor | `CANON_OVERRIDDEN_BY_LOWER_SOURCE` (BLOCKER) |
| `SR-PRC-02` | Espaço (posição, rota, conectividade) vem dos mapas; o dossiê não cria lugar físico sem `CART_DECISION` | `CARTOGRAPHIC_CONTRADICTION` (FAIL) |
| `SR-PRC-03` | Exigência espacial do dossiê sem lugar nos mapas vira decisão cartográfica pendente, nunca posição inventada | `CANON_PROPOSAL_REQUIRED` (ex.: D-SR-05) |
| `SR-PRC-04` | Patch `R*` só prevalece no escopo declarado em `supersedes_scope` | `PATCH_SCOPE_OVERREACH` (HIGH) |
| `SR-PRC-05` | Nenhum exemplo de stress test vira fato (dossiê §23) | `SYSTEM_CAPABILITY_AS_INSTANCE` (FAIL) |

---

## 7. Terminology

### 7.1 Termos

| Termo | Definição |
|---|---|
| **Canon Record** (`CR-*`) | regra ou fato do dossiê registrado com id, status, proveniência, escopo |
| **Hard Lock** (`HL-*`) | invariante que nenhuma cena, agente ou proposta ordinária pode violar; mudar exige revisão formal da franquia (dossiê §22) |
| **Unknown** (`UNK-SR-*`) | incógnita declarada; **não tem conteúdo**; status `MUST_REMAIN_UNKNOWN` no registry |
| **Prohibited inference** (`PRO-SR-*`) | leitura que o texto não pode estabelecer como verdade; `match` lexical opcional |
| **Mystery** (`MYS-*`) | mistério de série com escopo de livro; pode apontar `Q-*` do canon interpretativo |
| **Rumor** (`RUM-*`) | afirmação que circula no mundo; sua **existência** é canon, seu conteúdo não |
| **Capability** (`CAP-*`) | possibilidade do sistema do mundo; nunca implica instância |
| **Instance** | ocorrência concreta (esta fotografia, este cofre, esta combinação); só existe por canon explícito |
| **Book gate** (`BG1-*`, `BGF-*`) | o que um livro pode, pode parcialmente, não pode e precisa fazer |
| **State delta** (`SD-*`) | mudança do estado dinâmico de Redmur ligada a um `EV-*` do ledger |
| **Knowledge token** | id aprendido num `knowledge_delta`, com prefixo de modalidade (`SR:BELIEVES:`, …) |
| **Canon Context Pack** | recorte mínimo e seguro de canon para uma cena |
| **Warden** | `REDMUR_CANON_WARDEN`, revisor consultivo da obra; julga o resíduo semântico |
| **Engine view** | leitura que inclui o que o leitor ainda não recebe; nunca entra em brief de escrita sem autorização (padrão `--engine-view` do ledger) |

### 7.2 Glossário de Redmur (ids, não definições)

Os termos do mundo (cofre, Service Cowl, Emergency Breach, Dual Authorization,
Veil House, Visitor Coffer, OCP, Constabulary, Preservation Act, Savings
Clauses, Child Bulletins, The Return, Faceless Literacy, Four Archives, Dead
Archive…) recebem ids `CR-*` apontando para a seção do dossiê. **A definição é
a do dossiê**; o SDD não a parafraseia além do necessário para uma regra.

---

## 8. Design Principles

| # | Princípio | Consequência de desenho |
|---|---|---|
| DP-01 | `SYSTEM_CAPABILITY ≠ CANONICAL_INSTANCE` | `CAP-*` e instância são tipos distintos; nenhuma consulta converte um no outro (seção 15, `HL-05`) |
| DP-02 | **Guarda-se o mínimo; projeta-se o resto** (ledger E.2, LTE §8.2) | conhecimento, leitor, rumor, mistério, romance: projeções; só se armazena o que não é derivável |
| DP-03 | **Unknown não tem conteúdo** | `UNK-*` sem campo de resposta; chaves `HIDDEN_ANSWER_KEYS` reprovadas em todo seed/pack (REUSE AD-02) |
| DP-04 | **Existência de alegação ≠ verdade da alegação** | status de autoridade × classe epistêmica (seção 13) |
| DP-05 | **O motor conhece a causalidade; o leitor recebe evidência** (DR LAW 04) | pack de escrita sem engine view; leitor projetado de `READER` |
| DP-06 | **Character sees ≠ reader sees** | duas colunas distintas em todo evento facial (seção 22) |
| DP-07 | **Nenhuma camada implica outra** (identidade, acesso, corpo, consentimento — dossiê §15.6) | grants separados; `CONSENT_INFERENCE_VIOLATION` |
| DP-08 | **Validador conta; agente julga; humano decide** (DR SDD §D) | pré-filtro lexical nunca reprova sozinho um julgamento de prosa |
| DP-09 | **Lacuna vira pergunta, não invenção** | No Canon Invention Gate (seção 62) |
| DP-10 | **Mudança de estado não é retcon** | ponte destruída no cap. 20 = `WORLD_STATE_CHANGE` (seção 64) |
| DP-11 | **Um lugar para cada verdade** | nenhum fato em dois arquivos; sincronia registry ↔ canon verificada (seção 12.4) |
| DP-12 | **Simples o bastante para usar; estrito o bastante para proteger** | 1 validador, 1 agente, 8 seeds; limiares como hipótese de calibração |

---

## 9. Existing Architecture Discovery

Todas as afirmações abaixo foram verificadas nesta sessão (Apêndice C).

### 9.1 O que o repositório é

```text
engine/                      motor neutro (engine/AGENTS.md: nenhum canon de obra aqui)
  ENGINE_GRAPH.yaml          locks CANON_WRITE/TIMELINE_WRITE; CANON_PROPOSAL_PROTOCOL
  scripts/livingbook.py      compose: T012 WORLD_RULES, T013 CHARACTER_BIBLE, T016 PLOT_DEPENDENCY_MAP,
                             T017 TIMELINE, T018 CANON_REGISTRY, T019 CANON_REVIEW, T1NN_BRIEF_CHAPTER,
                             T2NN_{PREFLIGHT,WRITE,MERGE,REVIEW,REVISION,CANON_UPDATE,APPROVAL};
                             additional_tasks/gate_extensions/custom_validators por livro (:747-750)
  scripts/check_causal_ledger.py      L0–L10, INV-01..15, knowledge_state, beliefs, consent, adult gate
  scripts/check_interpretive_canon.py LTE S1–S2: questions (NEVER/LATE_PARTIAL/RESOLVED_AT), evidence,
                                      narrators, red herrings, HIDDEN_ANSWER_KEYS; SEQUEL recusado (AD-06)
  scripts/check_representation.py     RI S1: adult gate AG-*, hard boundaries HB-01/02/04
  scripts/check_cartography.py        cartografia S0–S1 (estrutura, fontes, mistérios, varredura de respostas)
  scripts/check_canon_continuity.py   entidades da prosa ausentes do registry; POV
  scripts/build_canon_digest.py       digest de canon (~11%) para tarefas de conferência
  scripts/detect_repetition.py        pré-filtro lexical de repetição/clichê (configurável por obra)
  contracts/CANON_PROPOSAL.schema.json   proposta textual; source_chapter 1..30; additionalProperties false
  agents/*.toml              66 agentes; CANON_GUARDIAN (tier S) único dono de mutação
books/sem-rosto/             pacote PARCIAL: só cartografia (não compõe runtime; README)
books/narciso/               padrão de canon por obra: seeds → T018N (CANON_GUARDIAN) → validador da obra
authors/bea_halden/          perfil de autora (Visual DNA + approvals com subject_sha256)
```

### 9.2 Mapa por item de discovery pedido (§2 do prompt)

| Item | Componente real | Estado | Leitura para este SDD |
|---|---|---|---|
| Arquitetura geral | engine / book package / runtime gerado | código | canon de obra fica em `books/sem-rosto/` |
| Canonical registries | `CANON_REGISTRY.yaml` (forma livre, sem schema) | arquivo | REUSE para `WR-*`, `UNK-*`, `PRO-*` (o LTE exige `CANON:UNK-*` ali) |
| World state | `WORLD_RULES.md`, `WORLD_BIBLE.md` (prosa); cartografia `mutations[]` para espaço | Markdown + código | CREATE `SEM_ROSTO_STATE_DELTAS.yaml` (não espacial) |
| Memory | "o repositório é a memória"; snapshots por wave | padrão | REUSE + snapshot por capítulo |
| Story state | ledger (eventos → projeções) | código | REUSE; SR só acrescenta deltas de Redmur |
| Knowledge graphs | ledger causal; canon interpretativo; cartografia | código | REUSE; tokens de modalidade (padrão `CART:EXISTS:` da cartografia §23.3) |
| Schema conventions | contrato real = template YAML testado; JSON Schema 2020-12 em `engine/contracts/` | convenção | YAML testado para seeds; JSON Schema só para pack e pós-cena (seção 12.6) |
| SDD conventions | `<NOME>_SDD_v0.1.md`, status E0, discovery, D-*, slices, OQs | convenção | seguida |
| Story/chapter/scene planning | `chapter_architecture.yaml`, `T016`, `T1NN_BRIEF_CHAPTER` (Markdown), cartografia `STAGING.yaml` | agentes + dados | EXTEND: sidecar estruturado de cenas (seção 60.2) |
| Character state | ledger `characters[]` (GT/SM/SP, age) | código | REUSE; assinatura não facial no canon da obra |
| Relationship state | `relationships[]` + `relationship_delta` (vocabulário aberto) | código | REUSE integral |
| Mystery systems | canon interpretativo; cartografia `CMY-*`/`RMY-*`; DEDR (proposta) | código + proposta | REUSE; `MYS-*` só para escopo de série |
| Evidence systems | `evidence[]` do canon interpretativo (Evidence Ledger, LTE §11) | código | REUSE; referência mínima a item físico (seção 56) |
| Timeline systems | `T017_TIMELINE` (Markdown), `TIMELINE_WRITE`; cartografia: dois eixos de tempo | Markdown + regra | REUSE + campos temporais nos registros |
| Validators | 12 validadores determinísticos + validadores de obra | código | 1 validador de junção da obra |
| Rule engines | não existe engine; regras são funções de validador | decisão registrada (DR SDD) | idem — "hard lock engine" = família de regras |
| Event systems | `events[]` do ledger | código | REUSE; `SD-*` referenciam `EV-*` |
| Prompt/context builders | `build_canon_digest.py` (por capítulo), cartografia `--pack` (especificado, S5) | código + proposta | CREATE `--pack` narrativo que **inclui** o pack cartográfico |
| RAG / retrieval | inexistente; HDR propõe RAG futuro | — | **não criar**: o recorte é determinístico por id |
| Orchestration | DAG + `run_deterministic.py` (`tool:`) + spawn declarado | código | REUSE: pack e snapshot são tarefas `tool` |
| Persistence | YAML no runtime; `mutation_log`; snapshots | padrão | REUSE |
| Tests | `unittest` offline, `PYTHONIOENCODING=utf-8`, uma mutação por teste | convenção | seguida |
| Observability | relatórios Markdown/JSON dos validadores; `validator_results` no status | padrão | REUSE |
| Versioning | `mutation_log`, snapshots, approvals com `subject_sha256`, sha de fontes | padrão | REUSE |
| Canon mutation | `CANON_PROPOSAL_PROTOCOL`, `PLANNED → REALIZED`, INV-10 | código | REUSE + sidecar estruturado |
| Cartography integration | contrato §22.4; `KNOWLEDGE_BASELINE` (READER vê os mapas no cap. 0) | dados + SDD | REUSE integral |
| Writer/reviewer/guardian agents | `CHAPTER_WRITER`, `LEAD_NOVELIST`, `SCENE_ARCHITECT`, `CANON_GUARDIAN`, `WORLD_RULES_REVIEWER`, `PLOT_CONTINUITY_REVIEWER`, `ANTI_MANIPULATION_GUARDIAN`, `SUBTEXT_EDITOR`, `PHYSICALITY_AND_BODY_AGENT`… | agentes | REUSE; 1 agente de obra para o resíduo de Redmur |

### 9.3 Estado de implementação das dependências

| Dependência | Estado | Consequência |
|---|---|---|
| Ledger causal | implementado, integrado ao compose | disponível |
| Canon interpretativo (LTE S1–S2) | implementado (commit `cc0cc7a`); **sem compose** (LTE S5) | obra usa tarefa extra à la Narciso, ou espera LTE S5 (OQ-SR-06) |
| Representation Integrity (S1) | implementado (`ab61553`) | HB-01 disponível |
| Cartografia S0–S5 | implementado (até `0bd528a`): grafo de superfície do Mapa A, viagem, visibilidade, perseguição, saídas, mapa do leitor, compose (`features.cartography`) e pack (`cartography_runtime.py --pack`); Mapa B ainda não digitalizado | integração espacial disponível para o pack narrativo |
| DEDR kit | proposta E0, não commitada | opcional; conflito D-SR-02 |
| UNSEEN L11, HDR | propostas E0 | não usadas no MVP |

### 9.4 Conflict check (PHASE 3) — registrados, não corrigidos

Nenhum item abaixo altera o cânone. Cada um diz qual fonte vence e o que o
sistema faz.

| ID | Achado | Evidência | Decisão |
|---|---|---|---|
| **D-SR-01** | O dossiê **não estava no repositório** | `~/Downloads/REDMUR_CANON_RESOLUTION_DOSSIER_FINAL.md` | **RESOLVIDO (S0, OQ-SR-02):** versionado em `books/sem-rosto/canon/sources/` com sha256 pinado (padrão D-CART-01) |
| **D-SR-02** | A ilustração de SEM ROSTO no DEDR §33 **contradiz o dossiê**: "a humanidade colocou seus rostos dentro dos Cofres" (dossiê §1.1: Redmur é uma pequena cidade; o mundo é contemporâneo); escada com "o rosto inteiro" como degrau (permitido ao personagem; `READER_SEES = FALSE`); "um beijo exige cometer um crime" (não decidido no dossiê); `ELITE_EXEMPTION` "elites têm Cofres removíveis" (não está no dossiê); `Q-ORIGIN NEVER` para a série (dossiê: origem dos cofres é `CANON_UNKNOWN` com lock **do Livro 1**, avanço futuro possível, §22); 13 hipóteses de origem (não estão no dossiê); "um dígito da combinação" como degrau (compatível com §2.7 só se não virar autoridade) | DEDR §33.1–33.6 | **O dossiê vence.** O §33 do DEDR já se declara "não canon"; nenhum registro deste sistema o cita como fonte. A fixture DEDR `runtime_sem_rosto_recorte` (DEDR §28.1) **deve** ser construída a partir do dossiê. OQ-SR-07 |
| **D-SR-03** | O LTE **recusa** `resolution_policy: SEQUEL` (AD-06: "nenhuma pergunta depende de volume futuro"), mas o dossiê reserva verdades para o Livro 2+ (True Chronology = P10-B, §12; §22) | `check_interpretive_canon.py:75` | No canon interpretativo **do Livro 1**, todo mistério reservado é `NEVER` (escopo = o livro). O escopo de série vive em `MYS-*.minimum_book` / `BGF-*` deste sistema. O LTE continua correto no seu escopo; nada muda nele |
| **D-SR-04** (RESOLVIDO por OQ-SR-04) | O LTE limita `max_never_questions: 3`; o dossiê tem dezenas de incógnitas; a cartografia já usa `Q-MAP-AUTHOR` (OQ-CART-20) | `check_interpretive_canon.py:157`; cartografia §22.7 | Incógnita bloqueada **não precisa** ser `Q-*`: `UNK-SR-*` + `PRO-SR-*` no registry bastam (precedente `a_morte`). Só vira `Q-*` o mistério que o Livro 1 **semeia ativamente com dupla evidência** — escolha da autora, ≤ limite (OQ-SR-04) |
| **D-SR-05** (RESOLVIDO por OQ-SR-05a) | R4 exige que o local do Six-Month Protocol "pertença à cartografia canônica existente", mas nenhum lugar dos mapas está rotulado como tal; o dossiê §17 lista "localização/uso narrativo final do local infantil" como `CANON_UNKNOWN` "salvo decisão cartográfica posterior explícita" | `LOCATIONS.seed.yaml` (inventário); dossiê §4.6, §17 | Consistente dentro do dossiê: localização = `UNK-SR-CHILD-FACILITY-LOCATION`. Nenhuma cena posiciona o local até `CART_DECISION` (OQ-SR-05). `Village Clinic` (`RM-*`) **não** é presumida como o local |
| **D-SR-06** (RESOLVIDO por OQ-SR-05b/c) | Veil House, Transfer Zone e Preservation Boundary (P3) não aparecem como lugares nos mapas; o Mapa A traz `BND-ADM-CP` "District of Civic Preservation", `extent: UNKNOWN`, `OFFICIAL_CLAIM` | `BOUNDARIES.seed.yaml:12`; dossiê §5 | Existência = canon (P3). Posição = `UNK-SR-*` até `CART_DECISION`. Identificar Preservation Boundary com `BND-ADM-CP` é decisão humana, não inferência (OQ-SR-05) |
| **D-SR-07** | `CANON_PROPOSAL.schema.json` exige `source_chapter` 1..30 e texto livre; `additionalProperties: false` | `engine/contracts/CANON_PROPOSAL.schema.json` | Lacunas de **planejamento** (antes do cap. 1) vão para `approvals/` (padrão D-CART-07). Propostas nascidas na escrita usam o schema inalterado + **sidecar** estruturado com o mesmo `proposal_id` (seção 63). 0 mudança no motor |
| **D-SR-08** (RESOLVIDO por OQ-SR-01) | O dossiê declara-se "PENDING HUMAN CANON FREEZE"; o prompt manda tratá-lo como `CANON_FROZEN_SOURCE` | dossiê cabeçalho e §27 | O prompt é instrução humana explícita. O motor **nunca** escreve aprovação: o humano registra `approvals/CANON_FREEZE_0001.md` com `subject_sha256` (OQ-SR-01). Até lá, o validador roda em modo `advisory` |
| **D-SR-09** | O gate adulto do ledger (INV-06) dispara só para `ADULT_EVENT_KINDS`; toque de cofre, pescoço ou combinação num contexto infantil **não erótico** não é evento adulto, logo não é vigiado por INV-06 | `check_causal_ledger.py:74, 642` | É exatamente o risco R11 (migração de semântica). O Age Semantic Firewall (seção 33) cobre por contexto + léxico + deltas de toque; REUSE HB-01 para o caso erótico |
| **D-SR-10** | A cartografia usa `INST-CIVIC-PRESERVATION` como id **ilustrativo**; o dossiê nomeia o órgão "Office of Civic Preservation — OCP"; o Mapa A rotula `RM-CEN-OCP` | cartografia §23.3; `LOCATIONS.seed.yaml:69` | Alinhamento, não conflito: id institucional `INST-OCP`, sede `RM-CEN-OCP`. Idem `INST-CONSTABULARY` ↔ `Redmur Constabulary` |
| **D-SR-11** | A camada `LYR-PRE-COFFER` da cartografia cita `Q-ORIGIN` do DEDR como pergunta `NEVER` | cartografia §25.1 | Reapontar para `UNK-SR-COFFER-ORIGIN` (Livro 1: locked; série: aberto). Mudança de dados na cartografia, a fazer no slice de integração (S5) |
| **D-SR-12** | Personagens: o dossiê não nomeia protagonistas; menciona "a instalação da protagonista" (§2.4); Selka é a única pessoa histórica nomeada; "Flarry" aparece sem natureza definida; o Mapa A rotula `Flarry Estate` | dossiê §2.4, §12.1, §14.2; `LOCATIONS.seed.yaml:169` | Protagonistas: `CANON_PROPOSAL_REQUIRED` (pacote do livro). "Flarry": `entity_kind: UNSPECIFIED`; **nenhum** vínculo com `Flarry Estate` é afirmado. Existe uma protagonista cuja instalação de cofre é possível pelo sistema de Dual Authorization — o dossiê não diz que ela é Returner nem Visitor |
| **D-SR-13** | Precedência entre mapas e Cartography SDD diverge entre prompt e dossiê | prompt §1; dossiê §0 | Adota-se a do dossiê (seção 6.1) |
| **D-SR-14** | O ledger tem campo `truth` em crenças (visão do motor) — colide com `NO_HIDDEN_ANSWER` só no canon interpretativo (LTE R-04) | `CAUSAL_LEDGER_TEMPLATE.yaml` | Crença ligada a mistério reservado é `truth: "INCOMPLETE"` + `left_open: true`, nunca revisada no Livro 1 (REUSE AD-03) |
| **D-SR-15** | Agentes de composição leem bíblias completas (`IMPLEMENT.md`, "Digest de canon"); isolamento de subagente é por instrução (LTE R-07) | `engine/IMPLEMENT.md`; LTE §5.4 | A proteção mais forte é **não haver verdade reservada escrita** (DP-03). O pack reduz ruído e improviso; não finge isolamento criptográfico (seção 75) |
| **D-SR-16** | O dossiê (§7.1) diz que nome e data do Preservation Act "podem ser refinados posteriormente" | dossiê §7.1 | `CR-P5-ACT.name_status: PROVISIONAL`; data `CANON_UNKNOWN`; nenhuma cena fixa data do Act sem proposta |

---

## 10. Reuse / Extend / Create Matrix

### 10.1 Resumo pedido (§3 do prompt)

**REUSED** (sem mudança): ledger causal (personagens, GT/SM/SP, eventos,
`knowledge_delta`, `acts_on_knowledge`, `reader_access`, crenças, loops,
consentimento, gate adulto, snapshots, `--why`, `--end-state`); canon
interpretativo (perguntas, evidência, narradores, red herrings,
`HIDDEN_ANSWER_KEYS`, `NEVER`/`RESOLVED_AT`); registry (`unknowns`,
`prohibited_inferences`); RI (HB-01/HB-02, AG-*); cartografia (grafo,
`KNOWLEDGE_BASELINE`, mapa do leitor, `MUST_REMAIN_UNKNOWN` de autoria,
mutações espaciais, pack cartográfico); `CANON_PROPOSAL_PROTOCOL`; locks;
`custom_validators` + `gate_extensions` + `additional_tasks`; `tool:` +
`run_deterministic.py`; `requires_human_approval`; `detect_repetition.py`
(léxico configurável por obra); `check_canon_continuity.py`;
`build_canon_digest.py`; agentes `CANON_GUARDIAN`, `SCENE_ARCHITECT`,
`CHAPTER_WRITER`, `LEAD_NOVELIST`, revisores e guardiões.

**EXTENDED** (dados/configuração da obra, nunca código do motor):
registry da obra ganha `WR-*`/`UNK-SR-*`/`PRO-SR-*` projetados dos seeds;
`knowledge_delta.learns` passa a carregar tokens de modalidade `SR:*`
(o ledger já aceita qualquer id — `check_causal_ledger.py:761-763`);
brief de capítulo ganha sidecar estruturado de cenas; `text_quality.yaml` da
obra ganha famílias de sinal corporal para o anti-loop gestual; cartografia
reaponta `LYR-PRE-COFFER` (D-SR-11).

**CREATED**: 8 seeds de canon da obra; `SEM_ROSTO_STATE_DELTAS.yaml` (estado
dinâmico de Redmur); `READER_PROMISES.yaml`; 1 validador de junção
`check_sem_rosto_canon.py`; 1 agente consultivo `REDMUR_CANON_WARDEN`;
2 JSON Schemas de fronteira (pack e pós-cena) na pasta da obra; aprovação de
freeze; fixture e testes.

### 10.2 Por conceito

| Conceito do prompt | Decisão | Componente | Justificativa |
|---|---|---|---|
| Canon Record (§6) | **CREATE (dados)** | `seeds/CANON_RECORDS.seed.yaml` → `canon/SEM_ROSTO_CANON.yaml` | registry é forma livre sem status/escopo; o dossiê precisa de ids citáveis |
| Status model (§5) | **CREATE (dados)** | duas camadas (seção 13) | nada no motor separa autoridade de classe epistêmica (a cartografia faz só para espaço) |
| Hard Lock Engine (§7) | **CREATE (regras)** | família `SR-HL` do validador + `seeds/HARD_LOCKS.seed.yaml` | "engine" = regras declaradas + funções; nada de rule engine genérico |
| World truth / unknown | **REUSE** | registry `unknowns[]`/`prohibited_inferences[]` | exigido pelo LTE (`unknown_ref: CANON:UNK-*`) |
| Character knowledge (§40–41) | **REUSE + EXTEND (dados)** | `knowledge_state` + tokens `SR:*` + proveniência em `SD-*` | projeção; nenhum grafo armazenado |
| Reader knowledge (§39) | **REUSE** | `knowledge_state(READER)` + evidência + mapa do leitor | só promessas são armazenadas |
| Rumor graph (§27) | **CREATE (dados mínimos)** | `seeds/RUMORS.seed.yaml` + evidência `source: CHR-*` | rumor precisa de mutação por família sem normalização; o LTE não tem "rumor" |
| Mystery graph (§31) | **REUSE + CREATE (escopo)** | `Q-*`/`UNK-*` + `MYS-*` (só `minimum_book`, estados, contratos) | D-SR-03/04 |
| Mystery gate (§32) | **CREATE (regra)** | `SR-MYS` + decisão ALLOW… (seção 21) | junção ledger × interpretativo × gates |
| Face firewall (§8) | **CREATE (regra + dados)** | `SD` tipo `FACE_EVENT` + `SR-FACE` | não existe no motor; é o coração da obra |
| Faceless Expression (§9) | **REUSE + CREATE (léxico)** | `detect_repetition.py` + `LEXICON.seed.yaml` + Warden | anti-loop = repetição; resíduo é julgamento |
| Coffer / Combination / Touch (§11–13) | **CREATE (dados)** | `seeds/COFFERS.seed.yaml` + `SD` tipos | domínio de Redmur |
| Consent (§14) | **REUSE + EXTEND** | bloco `consent` do ledger + grants por camada em `SD` | o ledger tem consentimento canônico/percebido; faltam camadas de cofre/lock/remoção/rosto |
| Age firewall (§15) | **REUSE + CREATE** | INV-06, HB-01 + `SR-AGE` contextual | D-SR-09 |
| Six-Month / Visitor / Returner (§16–17) | **CREATE (dados)** | `seeds/CIVIC.seed.yaml` + `SD` `CIVIC_TRANSITION` | máquina de estados de obra |
| Palimpsest jurisdiction (§19) | **CREATE (dados)** | `seeds/JURISDICTION.seed.yaml` | tabela de competência |
| Technology / Identity / Tattoo / Economy (§20–23) | **CREATE (registros)** | `CANON_RECORDS` + regras curtas | poucas regras; maior parte é orientação ao Warden |
| Chronology / Archives (§24–26) | **REUSE + CREATE** | evidência `channel: DOCUMENT/OBJECT/MEMORY` + `archive_type` na referência de item | HDR provenance é candidato futuro (OQ-SR-15) |
| Manfred / Selka / 1% (§28–30) | **CREATE (regras)** | `SR-MAN`, `SR-SEL`, `SR-NH` | proteções específicas |
| Crime / Fair play / Double edge (§34–36) | **REUSE + CREATE** | `Q-CRIME-B1` `RESOLVED_AT` + INV-11 + regras DEDR DX-FP (se o kit existir) ou locais | o LTE já tem pergunta resolvível; falta contrato P14 |
| Romance / Irreversibility (§37–38) | **REUSE** | loops, deltas, `STATE_RESET`, `POST_PAYOFF_AMNESIA`; + marca `irreversible` em `SD` | 1 marca nova |
| Evidence (§50) | **REUSE + CREATE (mínimo)** | `EVD-*` + `ITM-*` (item físico com custódia) | X-FILES é SDD futuro |
| Cartography (§55) | **REUSE** | pack cartográfico + validador de caminho | nenhuma duplicação |
| Story state (§42) | **REUSE + CREATE** | ledger + cartografia + `SEM_ROSTO_STATE_DELTAS.yaml` | estado = fold de deltas |
| Context pack (§43–44) | **CREATE (tool)** | `check_sem_rosto_canon.py --pack` | inexistente para canon narrativo |
| Role-based access (§45, §69) | **REUSE** | `inputs` declarados por tarefa + visão padrão × engine view | nenhum ACL novo (D-SR-15) |
| No invention / proposals (§46–47) | **REUSE + sidecar** | `CANON_PROPOSAL_PROTOCOL` + `CP-SR-*.yaml` | D-SR-07 |
| Validation pipeline (§56) | **REUSE + CREATE** | gates existentes + `--mode scene/wave/final` | 0 gates novos |
| Chapter snapshot (§59) | **CREATE (tool)** | `--snapshot-chapter N` | padrão de snapshot de wave, granularidade de capítulo |
| Promise ledger (§60) | **CREATE (dados)** | `canon/READER_PROMISES.yaml` | não derivável |
| Agent | **CREATE (1)** | `REDMUR_CANON_WARDEN` | precedente de guardião por obra (Narciso, Eva); resíduo semântico de rosto/idade/sobrenatural/Manfred |

### 10.3 Considerado e rejeitado

| Alternativa | Por que não |
|---|---|
| Capability do motor `features.story_canon` | `engine/AGENTS.md` (canon de obra fora do motor); abstração antes do 2º caso (DR SDD Q1) |
| Graph database / serviço de conhecimento | o grafo é projeção de YAML; SQL/grafo não traz nada que `knowledge_state` não dê |
| Um validador por firewall (15 scripts) | mesmo ciclo de vida, mesmo input; uma junção com famílias é mais simples |
| Um agente por firewall | o que diferencia Redmur é o acoplamento; o resíduo semântico cabe num revisor + revisores existentes |
| Copiar o dossiê em centenas de arquivos | migração incremental (seção 77); o dossiê continua sendo a prosa de referência |
| Campos de Redmur dentro de `CAUSAL_LEDGER.yaml` | contaminaria capability neutra; precedente cartografia D-CART-06 (estado vive fora, referencia `EV-*`) |
| Campos de Redmur dentro de `INTERPRETIVE_CANON.yaml` | `UNKNOWN_FIELD` (`KNOWN_FIELDS`); precedente DEDR D-DEDR-07 |
| RAG sobre o dossiê para montar contexto | recorte probabilístico vaza spoiler e perde regra; o pack é determinístico por id |
| "Truth vault" com as respostas reservadas | não há respostas decididas para guardar; e guardar tese de `NEVER` viola AD-02 |

---

## 11. System Architecture

### 11.1 Camadas

```text
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ HUMANO — Bea Halden / Pedro: autoridade final de canon (approvals/, CANON_PROPOSALS)   │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ OBRA  books/sem-rosto/                                                                 │
│   canon/sources/  dossiê pinado       canon/approvals/  freeze + decisões              │
│   canon/seeds/    CANON_RECORDS  HARD_LOCKS  BOOK_GATES  MYSTERIES  RUMORS             │
│                   COFFERS  CIVIC  JURISDICTION  LEXICON                                │
│   cartography/    (existente; SDD-CART)                                                │
│   validators/check_sem_rosto_canon.py   agents/redmur_canon_warden.toml                │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ RUNTIME  runtime/sem-rosto/                                                            │
│   canon/CANON_REGISTRY.yaml        (REUSE; recebe WR-*/UNK-SR-*/PRO-SR-* projetados)   │
│   canon/CAUSAL_LEDGER.yaml         (REUSE; personagens, eventos, conhecimento, consent) │
│   canon/INTERPRETIVE_CANON.yaml    (REUSE; Q-*, EVD-*; Q-CRIME-B1)                      │
│   canon/cartography/*.yaml         (REUSE; espaço, staging, mutações espaciais)         │
│   canon/SEM_ROSTO_CANON.yaml       estático: registros, locks, gates, mistérios, rumores│
│   canon/SEM_ROSTO_STATE_DELTAS.yaml dinâmico: SD-* por EV-*                             │
│   canon/READER_PROMISES.yaml       promessas ao leitor                                  │
│   briefs/chapters/CHAPTER_NN_SCENES.yaml   (planejamento; SCENE_ARCHITECT)             │
│   briefs/canon/CH_NN_<SC>_PACK.yaml        (gerado; tool)                              │
│   canon/snapshots/SEM_ROSTO.CH_NN.yaml     (gerado; tool)                              │
│   reviews/SEM_ROSTO_CANON_REPORT_<modo>.md (gerado)                                    │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ MOTOR (inalterado): ledger · interpretive canon · representation · cartography ·      │
│   gates · proposals · locks · tool runner · digest · repetition · continuity           │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### 11.2 O validador de junção

`check_sem_rosto_canon.py` (stdlib + PyYAML, como todos os validadores) **importa**
em vez de reescrever:

| Importa | Para |
|---|---|
| `check_causal_ledger.knowledge_state`, `build_indices`, `transitive_gt_ancestors`, `relationship_projection`, `validate` | conhecimento, leitor, ancestralidade causal, estado relacional, achados do ledger |
| `check_interpretive_canon.HIDDEN_ANSWER_KEYS`, carregamento/índices de `questions`/`evidence` | varredura de respostas; mistério; evidência por capítulo |
| `check_representation.hard_boundary_events` | HB-01/HB-02 |
| `check_cartography` (biblioteca de consulta; pack quando o S5 dela existir) | espaço |

Modos (mesma convenção dos validadores do motor; exit 1 com `HIGH`/`BLOCKER`):

| Modo | Escopo | Onde roda |
|---|---|---|
| `package` | seeds da obra: contrato, ids, status, proveniência, sincronia com o dossiê pinado | `GATE_CANON` |
| `plan` | canon materializado + ledger/interpretativo `PLANNED`: locks, gates, mistérios, crime, estado inicial | `GATE_CANON` |
| `scene --chapter N --scene SC` | contrato de cena + rascunho + pós-cena: pipeline da seção 65 | uso livre do escritor/revisor (pré-filtro), sem gate |
| `wave --through-chapter N --baseline S` | tudo que depende de `REALIZED` até N | `GATE_WAVE_n` |
| `final --baseline S` | livro inteiro + Book 1 Gates `REQUIRED` | `GATE_FULL_MANUSCRIPT` |
| `regression` | todos os `HL-*` + gates sobre o canon atual **e** todos os snapshots | após qualquer mudança de canon (seção 76.4) |

Consultas (seção 73): `--is-true`, `--who-knows`, `--reader-at`, `--pack`,
`--why-blocked`, `--locks`, `--mystery`, `--snapshot-chapter`, `--verdict`.

### 11.3 Fluxo no DAG existente

```text
T012_WORLD_RULES          WORLD_ARCHITECT lê os registros; propõe WR-* coerentes
T013_CHARACTER_BIBLE      personagens com age inteiro e assinatura não facial; protagonistas = proposta humana
T016_PLOT_DEPENDENCY_MAP  eventos PLANNED; crime; loops; Q-CRIME-B1
T018_CANON_REGISTRY ──▶ T018S_SEM_ROSTO_CANON (CANON_GUARDIAN, CANON_WRITE)      ← additional_task
                         └─ materializa SEM_ROSTO_CANON.yaml + fragmento de registry
T019_CANON_REVIEW         + REDMUR_CANON_WARDEN em canon_guardians
GATE_CANON ◀── V_SR_PACKAGE, V_SR_PLAN (+ ledger, interpretativo, cartografia)
T1NN_BRIEF_CHAPTER        SCENE_ARCHITECT escreve CHAPTER_NN_SCENES.yaml
T1NNS_CANON_PACK (tool) ──▶ briefs/canon/CH_NN_*_PACK.yaml                         ← additional_task
T2NN_WRITE                lê brief + pack; propõe pós-cena em CANON_PROPOSALS
T2NN_REVIEW               + WARDEN em wave_reviewers
T2NN_CANON_UPDATE         CANON_GUARDIAN: PLANNED→REALIZED; SD-* realizados
T2NNS_CHAPTER_SNAPSHOTS (tool) ──▶ canon/snapshots/SEM_ROSTO.CH_NN.yaml            ← additional_task
GATE_WAVE_n ◀── V_SR_WAVE_n
GATE_FULL_MANUSCRIPT ◀── V_SR_FINAL (+ checkpoint humano já existente)
```

Tudo por mecanismos de livro (`BOOK_GRAPH.yaml`). Limite herdado de Narciso
(D-N16): `gate_extensions` só acrescenta validadores; as tarefas extras
dependem de tarefas do motor e o validador reprova quando os artefatos delas
faltam — o efeito é bloqueante sem tocar o motor.

---

## 12. Canon Data Model

### 12.1 Canon Record (`CR-*`)

Os campos pedidos (§6 do prompt) foram mantidos quando têm consumidor; os que
já têm casa melhor apontam para ela.

```yaml
- canon_id: CR-P0-R1                      # CR-<módulo>-<n>  (módulo: ABS, P0..P14, R1..R11, UNK, B1, PHRASE)
  domain: COFFER                           # vocabulário fechado (12.3)
  subdomain: ACCESS
  title: "Combination ≠ Removal Authority"
  statement: "Conhecer a combinação não concede capacidade nem autoridade para remover o cofre."
  status: CANON_PATCH_APPROVED             # seção 13.1 (autoridade)
  epistemic_class: FACT                    # seção 13.2 (dentro do mundo)
  source: {id: SRC-DOSSIER, priority: 1, location: "§2.7 (R1)"}
  temporal: {valid_from: UNKNOWN, valid_until: null, historical_period: PRESENT}   # seção 58
  scope:
    book: SERIES                           # SERIES | B1 | B2 | ...
    reader: OPEN                           # OPEN | GATED | NEVER   (o leitor pode conhecer a REGRA)
    character: {default: PUBLIC_KNOWLEDGE} # quem no mundo conhece a regra (seção 17.4)
    institution: [INST-OCP]
  depends_on: [CR-P0-01]
  conflicts_with: []
  supersedes: null
  superseded_by: null
  lock: {hard: HL-07, mystery: null}
  reveal: {level: OPEN, minimum_book: B1, requires: []}   # para registros GATED: quando e depois de quê
  gates: {allowed_in: [B1, SERIES], forbidden_in: []}
  system_capability_only: false
  human_approval_required: true            # mudar este registro exige decisão humana
  notes: null
  revision: 1
  created_at: 2026-09-21
  updated_at: 2026-09-21
```

Campos deliberadamente **ausentes**: qualquer `answer`, `truth`, `real_*`,
`hidden_*` (varredura `HIDDEN_ANSWER_KEYS`); `character_knows` como lista
(conhecimento é projeção, seção 17).

### 12.2 Tipos de registro na mesma coleção

| Prefixo | Tipo | Campos extras | Exemplo |
|---|---|---|---|
| `CR-*` | regra/fato | — | `CR-P1-02` Facial Exposure = crime (§3.2) |
| `CAP-*` | capacidade do sistema | `system_capability_only: true`, `instances: []` (vazio até canon explícito) | `CAP-SEALED-FACIAL-EVIDENCE` (§3.5) |
| `UNK-SR-*` | incógnita | `status: MUST_REMAIN_UNKNOWN`; `scope.book`; `unlock_policy` (seção 70) | `UNK-SR-40Y-CAUSE` (§12.1) |
| `PRO-SR-*` | inferência proibida | `statement`, `match[]`, `scope.book` | `PRO-SR-SELKA-GHOST` (§14.8) |
| `ENT-*` / `INST-*` / `FAM-*` | entidade (pessoa histórica, instituição, família, tipo de documento) | `entity_kind`, `map_ref` | `ENT-SELKA`, `INST-OCP`, `FAM-MANFRED` |
| `THEORY-*` | teoria que existe no mundo | `epistemic_class: THEORY`, `prohibited_as_fact: PRO-SR-*` | `THEORY-CHILD-SUBSTITUTION` (§4.5) |
| `CR-PHRASE-*` | frase canônica | `usage: TONAL_REFERENCE` (nunca regra) | dossiê §24 |

### 12.3 Vocabulário de `domain`

`ABSOLUTE · COFFER · FACE · CHILD_PROTOCOL · VISITOR · RETURNER · JURISDICTION ·
PULL · TECHNOLOGY · IDENTITY · TATTOO · ECONOMY · BODY · CHRONOLOGY · ARCHIVE ·
MANFRED · SELKA · NON_HUMAN · EXPRESSION · INTIMACY · CONSENT · AGE ·
BOOK_CONTRACT · CARTOGRAPHY_DEPENDENCY · MYSTERY`. Extensível só por versão do seed.

### 12.4 Sincronia com o registry (DP-11)

O LTE exige `unknown_ref: "CANON:UNK-*"` no **registry**. Para não haver a
mesma incógnita em dois lugares:

- `SEM_ROSTO_CANON.yaml` é a fonte dos `UNK-SR-*`/`PRO-SR-*`/`WR-*` da obra;
- `check_sem_rosto_canon.py --emit-registry-fragment` gera o bloco
  correspondente (id, status, question/statement, match); o `CANON_GUARDIAN`
  o inclui em `T018`;
- `SR-CR-09 REGISTRY_DRIFT` (HIGH): ids `UNK-SR-*`/`PRO-SR-*`/`WR-*` do
  registry ≠ projeção do canon da obra.

### 12.5 Onde cada dado mora

| Dado | Artefato | Dono | É canon? |
|---|---|---|---|
| Regras, capacidades, entidades, incógnitas, inferências proibidas | `SEM_ROSTO_CANON.yaml` (+ fragmento no registry) | `CANON_GUARDIAN` | sim |
| Hard locks e gates de livro | `SEM_ROSTO_CANON.yaml` (`locks`, `book_gates`) | `CANON_GUARDIAN`; mudança = humano | sim |
| Mistérios de série (escopo, estado, contrato) | `SEM_ROSTO_CANON.yaml` (`mysteries`) | `CANON_GUARDIAN` | pergunta e escopo sim; resposta nunca |
| Rumores (existência, origem, versões) | `SEM_ROSTO_CANON.yaml` (`rumors`) | `CANON_GUARDIAN` | existência sim; conteúdo não |
| Personagens, idade, GT, eventos, relação, conhecimento, consentimento canônico | `CAUSAL_LEDGER.yaml` | `CANON_GUARDIAN` | sim |
| Perguntas interpretativas e evidência | `INTERPRETIVE_CANON.yaml` | `CANON_GUARDIAN` | pergunta e evidência sim; tese nunca |
| Espaço, staging, movimento | `canon/cartography/` | `CANON_GUARDIAN` | sim |
| Cofres, combinações, grants por camada, status cívico, eventos faciais, custódia de item, marcas de irreversibilidade | `SEM_ROSTO_STATE_DELTAS.yaml` | `CANON_GUARDIAN` | sim (deltas; estado é projeção) |
| Promessas ao leitor | `READER_PROMISES.yaml` | `CANON_GUARDIAN` (propostas por `NARRATIVE_ARCHITECT`) | não (planejamento verificável) |
| Plano de cena | `CHAPTER_NN_SCENES.yaml` | `SCENE_ARCHITECT` | não |
| Pack, snapshot, relatório | gerados | ninguém | não |

### 12.6 Formato dos contratos

Convenção do repositório: **contrato real = template YAML testado**
(LTE §5.1; `CAUSAL_LEDGER_TEMPLATE.yaml`). Assim:

- os 8 seeds têm template executável em `books/sem-rosto/canon/templates/`
  com teste "campo do template ⇔ campo do validador";
- **JSON Schema 2020-12** só para os dois artefatos que cruzam a fronteira
  entre agentes e que um agente produz livremente:
  `books/sem-rosto/canon/contracts/CANON_CONTEXT_PACK.schema.json` e
  `POST_SCENE_REPORT.schema.json` — na obra, não em `engine/contracts/`.

---

## 13. Canon Status Model

### 13.1 Eixo 1 — autoridade (quem decidiu, e o que o motor pode fazer com isso)

| `status` | Significado | O motor pode | O motor não pode |
|---|---|---|---|
| `CANON_APPROVED` | aprovado em P0–P14 | usar como fato/regra | alterar |
| `CANON_PATCH_APPROVED` | aprovado em R1–R11; prevalece no escopo | idem | estender além de `supersedes_scope` |
| `CANON_UNKNOWN` | o dossiê declara desconhecido | citar que é desconhecido | preencher, presumir, sugerir resposta |
| `RESERVED` | encerramento proibido até `minimum_book` | semear conforme gate | resolver antes |
| `SYSTEM_CAPABILITY` | possibilidade do sistema do mundo | dizer que o mundo **permite** | afirmar que **ocorreu** |
| `CANON_PROPOSAL_REQUIRED` | necessário para a obra, ainda inexistente | bloquear e perguntar | escolher |
| `PENDING_HUMAN_DECISION` | proposta aberta aguardando humano | listar alternativas | autoaprovar |
| `DEPRECATED_CANON` | não vale mais (decisão humana) | citar em histórico | usar |
| `SUPERSEDED` | substituído por `superseded_by` no escopo | seguir o substituto | usar no escopo substituído |

### 13.2 Eixo 2 — classe epistêmica (o que a afirmação é **dentro do mundo**)

| `epistemic_class` | Significado | Corresponde a (cartografia §5.2 / LTE / ledger) |
|---|---|---|
| `FACT` | verdade do mundo | `FACT` |
| `OFFICIAL_CLAIM` | o que uma instituição afirma | `OFFICIAL_CLAIM` |
| `HISTORICAL_CLAIM` | o que um registro antigo afirma | `HISTORICAL_CLAIM` |
| `RUMOR` | circula sem fonte documental | `RUMOR` |
| `THEORY` | hipótese formulada no mundo | interpretação `Q-*/X` (nunca fato) |
| `CHARACTER_BELIEF` | alguém acredita | token `SR:BELIEVES:` (seção 17) |
| `DISPUTED` | fontes do mundo divergem | evidências com suportes divergentes |
| `PARTIAL` | parte é conhecida, parte não | registro + `UNK-*` complementar |
| `FALSE` | contradito por fato canônico | `FALSE_MAP_DATA` (espaço); crença `truth: "FALSE"` (leitor) |
| `UNKNOWN` | ninguém — nem o motor — decidiu | `UNK-*` |

### 13.3 A regra que as duas camadas permitem

```text
RUM-SELKA-COFFER.status          = CANON_APPROVED       # é canon que o rumor existe (§14.7)
RUM-SELKA-COFFER.epistemic_class = RUMOR                # o conteúdo é rumor
UNK-SR-SELKA-COFFER-MODEL        = MUST_REMAIN_UNKNOWN  # modelo e conteúdo (§14.7)

THEORY-CHILD-SUBSTITUTION.status          = CANON_APPROVED   # a teoria existe no mundo (§4.5)
THEORY-CHILD-SUBSTITUTION.epistemic_class = THEORY
PRO-SR-CHILD-SUBSTITUTION-FACT            = narrar a troca de crianças como fato   # proibido

CAP-SEALED-FACIAL-EVIDENCE.status = SYSTEM_CAPABILITY ; instances: []   # §3.5, §23
```

### 13.4 Transições permitidas

| De → Para | Quem | Exige |
|---|---|---|
| `CANON_UNKNOWN` → `CANON_APPROVED` | **só humano** | `CANON_PROPOSAL` + aprovação registrada + `revision+1` |
| `RESERVED` → revelado (parcial/total) | gate do livro | `minimum_book` alcançado + pré-requisitos + humano para `FULL` |
| `SYSTEM_CAPABILITY` → instância | **só humano** | proposta que cria a instância (novo id); a capacidade continua capacidade |
| `CANON_PROPOSAL_REQUIRED` → `PENDING_HUMAN_DECISION` | qualquer agente | sidecar `CP-SR-*` |
| `PENDING_HUMAN_DECISION` → aprovado/rejeitado | **só humano** | decisão registrada |
| `CANON_APPROVED` → `SUPERSEDED`/`DEPRECATED_CANON` | **só humano** | patch R12+ (dossiê §25) |
| epistêmico `RUMOR`/`THEORY`/`CHARACTER_BELIEF` → `FACT` | **nunca por agente** | só decisão humana que cria **novo** `CR-*` `FACT` (o rumor continua rumor) |

`SR-ST-01 UNKNOWN_AS_FACT` (BLOCKER) · `SR-ST-02 STATUS_TRANSITION_WITHOUT_APPROVAL`
(BLOCKER) · `SR-ST-03 RUMOR_PROMOTED_TO_FACT` (BLOCKER) ·
`SR-ST-04 SYSTEM_CAPABILITY_AS_INSTANCE` (BLOCKER).

---

## 14. Provenance Model

### 14.1 Toda afirmação responde "como sabemos?"

| Camada | Campo | Resolve para |
|---|---|---|
| Canon estático | `source: {id, priority, location}` | seção do dossiê, mapa (`source_px`), approval, proposta |
| Evento | ledger `facts` + `caused_by` | `GT-*`/`EV-*` (REUSE INV-01) |
| Conhecimento | `SD` `KNOWLEDGE_PROVENANCE` (seção 17.5) | `EVD-*`, `ITM-*`, `EV-*`, `CHR-*` (testemunha), `STG-*` (presença) |
| Evidência | `EVD-*.anchor`, `text_anchor`, `source` | capítulo/cena/texto (REUSE) |
| Item físico | `ITM-*.custody[]` | `EV-*` de transferência |
| Estado | `SD-*.event` | `EV-*` `REALIZED` |
| Proposta | `CP-SR-*.need` | cena/tarefa que gerou a lacuna |

### 14.2 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-PV-01` | todo `CR/CAP/UNK/PRO/MYS/RUM/THEORY` tem `source.location` que existe no dossiê pinado (âncora `§N[.N]`) | `CANON_WITHOUT_PROVENANCE` | HIGH |
| `SR-PV-02` | todo `SD-*` referencia `EV-*` existente; `REALIZED` só com evento `REALIZED` | `STATE_WITHOUT_CAUSE` | HIGH |
| `SR-PV-03` | todo `ITM-*` usado como evidência tem `origin` e custódia contínua até o capítulo de uso | `EVIDENCE_WITHOUT_PROVENANCE` | HIGH |
| `SR-PV-04` | conhecimento estrutural (em `acts_on_knowledge` ou no pack como "o POV sabe") tem proveniência | `KNOWLEDGE_WITHOUT_PROVENANCE` | HIGH |
| `SR-PV-05` | registro cuja fonte não é dossiê/mapa/approval/proposta aceita | `IMPROVISED_CANON` | BLOCKER |

---

## 15. Hard Lock Engine

### 15.1 O que é um lock aqui

Uma entrada em `HARD_LOCKS.seed.yaml` com: id, enunciado (a fórmula do
dossiê), fonte, escopo (`SERIES` ou `B1`), **detectores** (regras do validador
que o aplicam) e **modo de verificação**:

| Modo | Significado |
|---|---|
| `STRUCTURAL` | verificável por dados (evento, delta, status, gate) — reprova sozinho |
| `LEXICAL_PREFILTER` | pré-filtro sobre prosa/brief; gera `WARNING` roteado ao Warden, nunca FAIL sozinho |
| `JUDGMENT` | só agente/humano; o lock entra no pack e no checklist do revisor |

Nenhum lock é "só julgamento" se houver forma estrutural; nenhum finge ser
estrutural quando depende de ler prosa.

### 15.2 Catálogo

| id | Lock (fórmula do dossiê) | Fonte | Escopo | Modos / detector |
|---|---|---|---|---|
| `HL-01` | `SUPERNATURAL_CANON = FALSE` | §1.3, §22 | SERIES | STRUCTURAL (nenhum `CR` `FACT` sobrenatural; `caused_by` nunca aponta força não humana) · LEXICAL (`LEXICON.supernatural_confirmation`) · JUDGMENT |
| `HL-02` | `MAGICAL_CAUSALITY = FORBIDDEN` | §1.3 | SERIES | STRUCTURAL (evento estrutural sem causa humana/institucional/física na ancestralidade → FAIL) |
| `HL-03` | `UNKNOWN ≠ SUPERNATURAL`; `RESIDUAL ≠ SUPERNATURAL` | §1.3, §14.1 | SERIES | STRUCTURAL (registro `RESIDUAL` não tem campo de confirmação sobrenatural, por construção) · JUDGMENT |
| `HL-04` | `READER_SEES = FALSE` para rosto reconstruível, mesmo com `CHARACTER_SEES = TRUE` | §1.4, §22 | SERIES | STRUCTURAL (`FACE_EVENT.reader_visibility` ∈ {`NONE`,`NON_RECONSTRUCTIBLE`}) · LEXICAL · JUDGMENT |
| `HL-05` | `SYSTEM_CAPABILITY ≠ CANONICAL_INSTANCE` | §0, §23 | SERIES | STRUCTURAL (`CAP-*.instances` vazio salvo instância aprovada; referência a instância inexistente → FAIL) |
| `HL-06` | `MINOR_EROTIC_SEMANTICS = ABSOLUTELY_DISABLED`; `NARRATIVE_EROTICIZATION_OF_MINORS = FORBIDDEN` | §4.8, §15.5 | SERIES | STRUCTURAL (REUSE HB-01; `SR-AGE`) · LEXICAL · JUDGMENT |
| `HL-07` | `KNOWING_COMBINATION ≠ PERMISSION_TO_TOUCH ≠ PERMISSION_TO_MANIPULATE_LOCK ≠ REMOVAL_AUTHORITY ≠ FACIAL_EXPOSURE_PERMISSION` | §2.7 (R1) | SERIES | STRUCTURAL (seção 30) |
| `HL-08` | camadas de consentimento independentes; `AUTHORITY/FEAR/COERCION ≠ CONSENT` | §15.4–15.5 | SERIES | STRUCTURAL (seção 32) · JUDGMENT |
| `HL-09` | `PHYSICAL_PRESENCE ≠ AUTOMATIC_RETURNER_ACTIVE_STATUS` | §6.2 (R2) | SERIES | STRUCTURAL (seção 36) |
| `HL-10` | `ELIGIBILITY_RULE ≠ EXTRATERRITORIAL_POLICE_POWER`; Redmur não é soberana | §1.1, §4.7 (R3), §7 | SERIES | STRUCTURAL (seção 37) · JUDGMENT |
| `HL-11` | `NO_DELIBERATE_SELF_VIEWING` | §3.7 (R8) | SERIES | STRUCTURAL (`FACE_EVENT kind: SELF_VIEWING, deliberate: true` → FAIL) · LEXICAL (espelho comum) |
| `HL-12` | Sealed Facial Evidence só com os 7 requisitos; sem banco facial, thumbnail, acesso público ou captura geral pela OCP | §3.5 (R6) | SERIES | STRUCTURAL (seção 25) |
| `HL-13` | `LAWFUL_EXTERNAL_EXISTENCE ≠ LAWFUL_LOCAL_POSSESSION ≠ LAWFUL_LOCAL_EXPOSURE`; sem purge global | §3.6 (R7) | SERIES | STRUCTURAL (seção 26) |
| `HL-14` | Selka: `NO CROSSOVER DEPENDENCY`, `NO ONTOLOGY LEAKAGE`; `KEY, NEVER THE KEY` | §14.8–14.9 | SERIES | STRUCTURAL + LEXICAL (seção 49) |
| `HL-15` | nunca "os Manfred fizeram" como explicação automática | §13.3 | SERIES | STRUCTURAL (ator/causa em nível de família → FAIL) · JUDGMENT |
| `HL-16` | `CANON_UNKNOWN` não autoriza invenção durante a escrita | §17 | SERIES | STRUCTURAL (seção 62) |
| `HL-17` | Redmur sobrevive ao Livro 1; `WORLD_SYSTEM_STABLE = TRUE` | §16.8 | B1 | STRUCTURAL (nenhum `SD`/evento com efeito `ABOLISH_COFFERS`/`DESTROY_TOWN`/`SYSTEM_OVERTHROWN`/`LIBERATE_REDMUR`) |
| `HL-18` | `VILLAIN_EXPLAINS_REDMUR` proibido | §16.6 | B1 | STRUCTURAL (evento de revelação do crime não altera estado de `MYS-*` reservado) · JUDGMENT |
| `HL-19` | tatuagem: sem números explícitos de combinação; nunca rosto humano individualizado/reconstruível | §10.3, §14.7 | SERIES | STRUCTURAL (`TAT-*.encodes_digits`, `depicts_face` proibidos) · LEXICAL |
| `HL-20` | sem retcon sobrenatural futuro | §1.3, §14.1, §22 | SERIES | STRUCTURAL (mudar `HL-01..03` exige revisão formal da franquia — humano) |
| `HL-21` | `THE HEAD IS INSIDE THE COFFER. THE HEAD DOES NOT CARRY THE COFFER.`; sobrevivência não depende só de energia elétrica | §2.1 | SERIES | JUDGMENT (+ LEXICAL: pescoço sustentando o peso) |
| `HL-22` | nenhuma infraestrutura recorrente nova sem proposta/atualização cartográfica | §19 | SERIES | STRUCTURAL (REUSE cartografia INV 09) |
| `HL-23` | não existe combinação universal simples que abra todos os cofres | §2.3 | SERIES | STRUCTURAL (`CMB-*` com escopo > 1 cofre → FAIL) |
| `HL-24` | `COFFER ≠ PERSON`; `COFFER_IDENTITY ≠ PERSON_IDENTITY` | §2.6, §10.1 | SERIES | STRUCTURAL (identificação por cofre só gera `SOCIAL_RECOGNITION`, seção 40) |
| `HL-25` | `FACILITY_VISIBILITY ≠ PROTOCOL_TRANSPARENCY` | §4.6 (R4) | SERIES | STRUCTURAL (ver o prédio não ensina `UNK-SR-SIX-MONTH-CONTENTS`) |
| `HL-26` | `PEDIATRIC_ACCESS = CLINICAL / PROTECTIVE / FUNCTIONAL`; nunca presumir erotismo | §2.8 (R5) | SERIES | STRUCTURAL + LEXICAL (seção 33) |
| `HL-27` | sem IA central onisciente; sem vigilância facial indiscriminada | §9.1–9.2 | SERIES | STRUCTURAL (seção 39) · JUDGMENT |
| `HL-28` | nenhum rosto identificável como recompensa final | §16.8 | B1 (+ SERIES por HL-04) | STRUCTURAL |

### 15.3 Regras gerais

- `SR-HL-01 HARD_LOCK_VIOLATION` (BLOCKER): qualquer detector `STRUCTURAL` de
  um lock reprova. Nenhum perfil de execução rebaixa (política de INV-06..10).
- `SR-HL-02 HARD_LOCK_EDIT` (BLOCKER): lock alterado sem approval humano com
  `subject_sha256` do seed.
- `SR-HL-03 LOCK_WITHOUT_DETECTOR` (MEDIUM): lock sem regra nem item de
  checklist que o aplique — lock decorativo.

---

## 16. World Truth Model

### 16.1 O que o motor sabe

```text
WORLD_TRUTH(chapter) =
    CR-* / CAP-* / ENT-* com epistemic_class FACT          (estático, dossiê)
  ∪ facts de eventos REALIZED do ledger até o capítulo      (dinâmico)
  ∪ GT-* dos personagens                                    (engine-only por padrão)
  ∪ fold(SEM_ROSTO_STATE_DELTAS) até o capítulo             (dinâmico de Redmur)
  ∪ grafo físico da cartografia no capítulo                 (espaço)
```

### 16.2 O que o motor sabe que não sabe

`UNK-SR-*` — dossiê §17 inteiro (Apêndice A), mais incógnitas espalhadas
(§3.7, §4.5, §7.3, §8, §11.5, §12.1, §14.3–14.8). Uma pergunta sobre um
`UNK-*` devolve `CANON_UNKNOWN`, com a fonte, **e nada mais**.

### 16.3 O que não existe em nenhum arquivo (por construção)

True Chronology; causa dos Missing Forty Years; natureza de Aquele Dia; origem
dos cofres e da proibição facial; propósito do tabu de autoimagem; o que ocorre
nos seis meses; explicação completa de The Pull e do Body Gap; causa da morte
de Selka; localização do túmulo; modelo/conteúdo do cofre de Selka; significado
de suas tatuagens; lista objetiva das 10 Relíquias; origem de "Aqui ninguém
termina a oração."; autoria dos mapas; qualquer Facial Record histórico
específico.

Quando a autora decidir uma dessas verdades para um livro futuro, ela entra
como `GT-*` **engine-only** no ledger (ou `CR-*` com `scope.reader: GATED` e
`reveal.minimum_book`), por proposta humana — nunca antes, nunca por agente
(seção 70.3).

### 16.4 Consulta "isto é verdade em SEM ROSTO?"

`--is-true "<id|alias|texto>"` devolve uma das respostas, sempre com fonte:

| Resposta | Quando |
|---|---|
| `TRUE (FACT)` | `CR-*` `FACT` ou evento `REALIZED` |
| `CLAIMED_AS (OFFICIAL/HISTORICAL/RUMOR/THEORY/BELIEF)` | existe como alegação; o conteúdo não é fato |
| `CAPABILITY_ONLY` | `CAP-*`: o mundo permite; nenhuma instância |
| `CANON_UNKNOWN` | `UNK-*` |
| `FALSE` | contradiz `FACT`, lock ou casa com `PRO-*` |
| `NOT_IN_CANON → CANON_PROPOSAL_REQUIRED` | nada resolve; é lacuna |

Texto livre é casado por id, alias e `match[]` de `PRO-*`; sem casamento, a
resposta é `NOT_IN_CANON` — o sistema não adivinha por similaridade.

---

## 17. Character Knowledge Graph

### 17.1 Princípio

`WORLD_TRUTH ≠ CHARACTER_KNOWLEDGE ≠ READER_KNOWLEDGE` (dossiê §21 item 9;
cartografia §23.1). O motor **guarda** a primeira e **projeta** as outras.

### 17.2 Modalidades como tokens (REUSE do ledger, zero mudança)

O ledger aceita qualquer id em `knowledge_delta.learns` e só restringe `GT-*`
(`check_causal_ledger.py:761-763`). A cartografia já usa prefixo de nível
(`CART:EXISTS:RM-*`). Este sistema faz o mesmo para modalidade:

| Modalidade pedida | Token / fonte | Observação |
|---|---|---|
| `knows` | id puro (`CR-*`, `EV-*`, `GT-*`, `ITM-*`, `RM-*`…) | padrão do ledger |
| `believes` | `SR:BELIEVES:<id>` | pode ser crença em `RUM-*`, `THEORY-*` ou em algo `FALSE` |
| `suspects` | `SR:SUSPECTS:<id>` | |
| `misremembers` | `SR:MISREMEMBERS:<id>` + `SD` com a versão lembrada | a versão errada nunca vira fato |
| `was_told` | `SR:TOLD:<id>` + proveniência `source: CHR-*` | não implica crer |
| `personally_witnessed` | presença em evento/staging (conhecimento trivial, INV-13) | projeção |
| `has_document` | custódia de `ITM-*` (seção 56) | ter ≠ ter lido |
| `has_access` | grants de acesso (lugar, arquivo, lock) em `SD` | acesso ≠ conhecimento |
| `is_lying_about` | `GT-*` `kind: SECRET` + evento com `interpretations` divergentes | REUSE |
| `refuses_to_discuss` | `social_persona` com `conceals` | REUSE |
| `does_not_know` | complemento do acima | projeção |
| `cannot_know_yet` | tokens bloqueados por gate/lock/`UNK-*`/pré-requisito | projeção (seção 21) |

### 17.3 Projeção

```text
knowledge(CHR, N)       = knowledge_state(ledger, CHR, N)          # REUSE
                        ∪ trivial(CHR, N)                           # presença em EV/STG
                        ∪ baseline(CHR)                             # cap. 0: canon da obra + KNOWLEDGE_BASELINE
                        ∪ inherited(CHR)  só se member_of(..., inherits_knowledge: true)   # cartografia §23.5
cannot_know_yet(CHR, N) = tokens em UNK-* ∪ tokens com reveal.minimum_book > livro ∪ pré-requisitos não cumpridos
```

### 17.4 Conhecimento público de regra

Uma regra do mundo (`CR-*`) tem `scope.character.default`:
`PUBLIC_KNOWLEDGE` (todo residente adulto conhece — ex.: Facial Exposure é
crime), `INSTITUTIONAL` (quem opera o procedimento), `SPECIALIST`
(coffermakers, fitting), `NONE`. Visitantes herdam só o que o Visitor Protocol
comunica (seção 35). **O leitor não herda o conhecimento público do POV
automaticamente**: conhece o que a página deu (seção 18). Os valores concretos
de `default` por registro são decisão da autora na migração (seção 77, fase 2);
na ausência, o padrão é `NONE` — o conservador.

### 17.5 Knowledge Acquisition Events (§41 do prompt)

Todo `knowledge_delta` **estrutural** tem linha de proveniência em
`SEM_ROSTO_STATE_DELTAS.yaml`:

```yaml
- id: SD-0112
  event: EV-31                        # evento do ledger que contém o knowledge_delta
  type: KNOWLEDGE_PROVENANCE
  knower: CHR-P
  token: "SR:SUSPECTS:ITM-017"
  source: ITM-017                     # EVD-* | ITM-* | EV-* | CHR-* (testemunha) | STG-*
  confidence: PARTIAL                 # FULL | PARTIAL | MISREAD
  chapter: 12
  scene: SC-12-03
```

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-KN-01` | personagem age/fala sobre token fora de `knowledge(CHR, N)` | `CHARACTER_KNOWLEDGE_LEAK` (REUSE INV-13 + tokens SR) | FAIL |
| `SR-KN-02` | token estrutural sem `KNOWLEDGE_PROVENANCE` | `KNOWLEDGE_WITHOUT_PROVENANCE` | HIGH |
| `SR-KN-03` | token em `cannot_know_yet` aparece em `learns` | `PREMATURE_MYSTERY_REVEAL` / `BOOK1_HISTORY_LOCK_VIOLATION` | BLOCKER |
| `SR-KN-04` | `SR:TOLD:` usado como conhecimento em `acts_on_knowledge` sem `SR:BELIEVES:` | `TOLD_AS_KNOWN` | MEDIUM |
| `SR-KN-05` | rota secreta usada sem fonte | REUSE cartografia `KN-01`/`KN-03` | FAIL/HIGH |
| `SR-KN-06` | ter documento tratado como ter lido | `DOCUMENT_POSSESSION_AS_KNOWLEDGE` | MEDIUM |

---

## 18. Reader Knowledge Ledger

### 18.1 Projeção, não arquivo

| Campo pedido | Fonte |
|---|---|
| `facts_seen` | `knowledge_state(READER, N)` + evidência `REALIZED` até N |
| `rumors_seen` | `RUM-*` com evidência `REALIZED` até N (`source: CHR-*`, canal `DIALOGUE`) |
| `theories_available` | interpretações `Q-*/X` com suporte `S` até N |
| `contradictions_seen` | pares de evidência com suporte divergente até N (+ `contradiction_map` do DEDR, se existir) |
| `clues_seen` | `EVD-*` `FIRST_READ` até N |
| `clues_understood` | **não projetável** (depende do leitor real) → forum LTE, só diagnóstico |
| `false_inferences_supported` | crenças `RB-*` com `truth: "FALSE"` ativas em N (engine view) |
| `faces_not_seen` | **invariante**: todos. `FACE_EVENT.reader_visibility` nunca `RECONSTRUCTIBLE` (HL-04) |
| `knowledge_withheld` | GT com `reader_access` futuro/`NEVER` + `cannot_know_yet(READER)` (engine view) |
| `knowledge_promised` | `READER_PROMISES.yaml` (seção 68) |
| `resolved_questions` | `Q-*` `RESOLVED_AT` com evento ≤ N; `MYS-*` `RESOLVED` |
| `new_questions` | `Q-*`/promessas com primeira evidência em N |

Linha de base não vazia: por `OQ-CART-03`, os mapas são impressos; o leitor
tem `SEEN_ON_MAP` para todo id das fontes no capítulo 0 (cartografia §22.6).
Outro paratexto (epígrafe, documento impresso) entra na linha de base **só**
por declaração `front_matter` — nunca por suposição.

### 18.2 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-RD-01` | `READER` aprende GT antes de `reader_access` | REUSE `READER_OMNISCIENCE_LEAK` ≡ `READER_KNOWLEDGE_LEAK` | FAIL |
| `SR-RD-02` | `READER` aprende token em `cannot_know_yet(READER)` | `READER_KNOWLEDGE_LEAK` | BLOCKER |
| `SR-RD-03` | narração onisciente acidental | REUSE `OBSERVABLE_STATES_ANSWER` + Warden | HIGH |
| `SR-RD-04` | ironia dramática declarada (`reader_knows_but_pov_does_not`) | permitida e mostrada no pack | INFO |

---

## 19. Public Belief / Rumor Model

### 19.1 Contrato mínimo

```yaml
rumors:
  - id: RUM-SELKA-COFFER
    statement_neutral: "Circula que Selka foi enterrada com o cofre."   # descrição, não tese
    status: CANON_APPROVED                   # a existência do rumor
    epistemic_class: RUMOR
    source: {id: SRC-DOSSIER, location: "§14.7"}
    origin: UNKNOWN                          # CHR-* | FAM-* | INST-* | UNKNOWN
    origin_confidence: UNKNOWN
    truth_relation: UNK-SR-SELKA-COFFER-MODEL    # aponta a incógnita; nunca TRUE/FALSE sem FACT canônico
    related: {mysteries: [MYS-SELKA], families: [], events: []}
    versions: []                             # RUV-* (19.2), declaradas por proposta
    beneficiaries: []                        # só com canon; nunca inferido
    # PROJETADOS (nunca escritos à mão): believers, repeaters, skeptics, known_liars,
    # uncertain_characters, reader_seen, first_appearance, last_reinforced
```

Rumores e teorias com existência canônica no dossiê: o cofre enterrado com
Selka (§14.7); "A Sepultura Que Falta" como sendo Selka (§14.5, `THEORY`); as
listas das 10 Relíquias (§14.6); a substituição de crianças (§4.5, `THEORY`);
"Manfred apagou os 40 anos" (§13.3, `THEORY` que deve continuar tentadora e
**coexistir** com alternativas). Versões de "Aquele Dia" entre famílias são
**capacidade** (`CAP-RUMOR-MUTATION`) até a autora declarar versões concretas.

### 19.2 Versões e mutação sem normalização

```yaml
versions:
  - id: RUV-AQUELE-DIA-01                # FORMA; nenhuma versão existe hoje
    carrier: FAM-X                        # quem conta
    first_heard: {event: EV-*, chapter: N}
    differs_from: [RUV-AQUELE-DIA-02]
    elements: ["descrição neutra do que esta versão afirma"]
```

Versões **nunca** são fundidas numa "versão verdadeira". Repetidor, crente e
cético são projetados de tokens `SR:TOLD:`/`SR:BELIEVES:` e de evidência
`source: CHR-*`.

### 19.3 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-RUM-01` | narração trata conteúdo de `RUM-*` como fato (evento `facts`, ou evidência `source: NARRATOR` afirmando) | `RUMOR_AS_WORLD_TRUTH` | FAIL |
| `SR-RUM-02` | versões fundidas, ou uma marcada verdadeira sem `CR-*` `FACT` | `RUMOR_NORMALIZED` | HIGH |
| `SR-RUM-03` | `beneficiaries` ou `origin` preenchido sem canon | `RUMOR_ORIGIN_INVENTED` | HIGH |
| `SR-RUM-04` | rumor novo recorrente (≥2 cenas) sem `RUM-*` | `IMPROVISED_CANON` | MEDIUM → proposta |

---

## 20. Mystery Graph

### 20.1 Três camadas, uma para cada coisa

| Camada | Guarda | Artefato |
|---|---|---|
| **Escopo de série** | pergunta, estado, `minimum_book`, teto por livro, contrato de resolução | `MYS-*` em `SEM_ROSTO_CANON.yaml` |
| **Incógnita** | "o motor sabe que não sabe" | `UNK-SR-*` no registry |
| **Teoria ativa do livro** | interpretações e evidência com dupla leitura | `Q-*` em `INTERPRETIVE_CANON.yaml` (≤ limites do LTE) |

### 20.2 Contrato `MYS-*`

```yaml
- id: MYS-FORTY-YEARS
  question: "O que ocorreu nos Missing Forty Years?"      # neutra
  scope: SERIES
  status: RESERVED       # UNOPENED | OPEN | EXPANDING | PARTIALLY_RESOLVED | RESOLVED | PERMANENTLY_AMBIGUOUS | RESERVED
  source: {id: SRC-DOSSIER, location: "§12.1, §12.4, §16.8, §18"}
  unknown_refs: [UNK-SR-40Y-CAUSE, UNK-SR-40Y-DELIBERATE, UNK-SR-40Y-SINGLE-ACTOR]
  prohibited_refs: [PRO-SR-40Y-SOLVED-B1]
  interpretive_question: null               # Q-* se o livro semeia dupla evidência (D-SR-04)
  minimum_book: FUTURE                      # §22: "investigação mais profunda" possível no futuro; só a True Chronology é "Livro 2/futuro" (§12)
  by_book:
    B1:
      state_ceiling: EXPANDING
      allowed: [CITE, PROVOKE, SHOW_DATES, CONTRADICT_DOCUMENTS, PRESENT_SYMBOLS,
                REVEAL_CONSEQUENCES, DEMONSTRATE_INCOMPATIBILITIES]      # §12.4
      required: [EXISTS_AS_REAL_PROBLEM]                                 # §12.4
      forbidden: [WHAT_HAPPENED, RESOLVE_BY_EXHUMATION, RESOLVE_BY_SELKA] # §12.3, §12.4, §14.9
  resolution_contract: null                 # só humano define, quando decidir
  partial_resolution_allowed: {B1: false}
  human_approval_required: true
  # PROJETADOS: reader_state, character_states, institution_states, related_clues,
  # red_herrings, contradictions, rumors, documents, locations, people
```

`world_truth` **não é campo**. Para mistério com resposta no livro (o crime),
a resposta mora no ledger como `GT-*` engine-only e `Q-CRIME-B1 RESOLVED_AT`
(seção 51); para mistério `CANON_UNKNOWN`, não mora em lugar nenhum.

### 20.3 Registro inicial (dossiê §8, §11.5, §12.4, §14, §16.8, §17, §18)

| `MYS-*` | Status inicial | `minimum_book` | Teto no Livro 1 |
|---|---|---|---|
| `MYS-TRUE-CHRONOLOGY` | RESERVED | B2 (P10-B) | `OPEN` |
| `MYS-FORTY-YEARS` | RESERVED | FUTURE | `EXPANDING` ("existem como problema real") |
| `MYS-AQUELE-DIA` | RESERVED | FUTURE | `EXPANDING` (sem causa definitiva) |
| `MYS-LUA-SANGRENTA` | RESERVED | FUTURE | `OPEN` |
| `MYS-MANFRED-ROLE` | RESERVED | FUTURE | `EXPANDING` |
| `MYS-FLARRY` | RESERVED | FUTURE | `OPEN` |
| `MYS-LOST-CHILD` | RESERVED | FUTURE | `OPEN` |
| `MYS-COFFER-ORIGIN` | RESERVED | FUTURE | `OPEN` |
| `MYS-SIX-MONTH` | RESERVED | FUTURE | `OPEN` |
| `MYS-PRESERVATION-ACT` / `MYS-SAVINGS-CLAUSES` | RESERVED | FUTURE | `OPEN` |
| `MYS-THE-PULL` | RESERVED; explicação completa `PERMANENTLY_AMBIGUOUS` (§8) | — | explicação parcial só por subtexto |
| `MYS-SELKA` (morte, túmulo, cofre, tatuagens) | RESERVED | FUTURE | `RUMOR → FRAGMENTO → CONTRADIÇÃO → PISTA → TEORIA` (§14.9) |
| `MYS-MISSING-GRAVE` / `MYS-TEN-RELICS` | RESERVED | FUTURE | `OPEN` |
| `MYS-FOUR-ARCHIVES` / `MYS-DEAD-ARCHIVE` | RESERVED | FUTURE | `EXPANDING` |
| `MYS-UK-VS-PRESERVATION` / `MYS-WHY-STAY` | RESERVED | FUTURE | `EXPANDING` |
| `MYS-BODY-GAP` | OPEN; explicação total `CANON_UNKNOWN` (§11.5) | — | `OPEN` |
| `MYS-SELF-FACE-TABOO-ORIGIN` | origem `UNKNOWN` (§3.7) | — | `OPEN` |
| `MYS-MAP-AUTHOR` | `PERMANENTLY_AMBIGUOUS` (cartografia OQ-CART-02b) | NEVER | `OPEN` |
| `MYS-CRIME-B1` | `CANON_PROPOSAL_REQUIRED` (crime não escolhido) | B1 | `RESOLVED` **exigido** (§16.1) |

`FUTURE` = o dossiê §22 permite avanço futuro sem presumir resolução; qual
livro pode avançar é decisão humana (`BGF-*`, seção 70). Os tetos acima são a
leitura mais conservadora do dossiê; `EXPANDING` só onde o dossiê explicitamente
permite contradizer/provocar/demonstrar no Livro 1.

### 20.4 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-MYS-01` | estado projetado do mistério no livro > `state_ceiling` | `PREMATURE_RESOLUTION` | BLOCKER |
| `SR-MYS-02` | `MYS-*` com `world_truth`/`answer`/tese | `HIDDEN_ANSWER_PRESENT` (REUSE AD-02) | BLOCKER |
| `SR-MYS-03` | `MYS-*` reservado cuja `interpretive_question` não é `NEVER` no livro | `RESERVED_NOT_NEVER_IN_BOOK` | BLOCKER |
| `SR-MYS-04` | mistério `REQUIRED` do livro (crime) sem `Q-*` `RESOLVED_AT` | `CRIME_UNRESOLVED` | HIGH (final) |

Estado projetado de um `MYS-*` no capítulo N: `OPEN` se há evidência/rumor
`REALIZED`; `EXPANDING` se há ≥2 evidências em capítulos distintos ou
contradição; `PARTIALLY_RESOLVED` se algum `UNK-*` do mistério recebeu
proposta aprovada e revelação; `RESOLVED` se todos. Como os `UNK-*` do Livro 1
não têm conteúdo, `PARTIALLY_RESOLVED`/`RESOLVED` são **inalcançáveis por
construção** para mistérios reservados — a menos que alguém crie canon, que é
exatamente o que a regra detecta.

---

## 21. Mystery Firewall — `MYSTERY_DISCLOSURE_GATE`

### 21.1 Entrada

Uma **revelação candidata**: `(book, chapter, scene, knower ∈ {CHR-*, READER}, token, via ∈ {EVENT, EVIDENCE, DIALOGUE, DOCUMENT, NARRATION})`.

### 21.2 Algoritmo (determinístico, ordem fixa)

```text
1. token resolve para canon?            não → CANON_PROPOSAL_REQUIRED (No Canon Invention Gate)
2. token é UNK-*?                       → BLOCK   (ninguém aprende incógnita)
                                           exceto hipótese atribuída: via DIALOGUE/DOCUMENT com classe
                                           RUMOR/THEORY → ALLOW_AS_RUMOR / ALLOW_AS_THEORY
3. atinge hard lock?                    → BLOCK (cita HL-*)
4. book gate FORBIDDEN no livro?        → BLOCK ;  PARTIAL → segue com teto
5. estado resultante do MYS-* > state_ceiling?          → BLOCK (PREMATURE_RESOLUTION)
6. reveal.requires cumpridos (EVD-*/EV-* anteriores)?   não → BLOCK
7. knower = CHR: fonte acessível (presença, custódia, testemunha, grant)?   não → BLOCK
8. knower = READER: reader_access da GT permite neste evento?               não → BLOCK
9. classe epistêmica do conteúdo:
     FACT                         → ALLOW
     RUMOR                        → ALLOW_AS_RUMOR   (a narração não confirma)
     THEORY / CHARACTER_BELIEF    → ALLOW_AS_THEORY
     PARTIAL (ou teto PARTIAL)    → ALLOW_AS_PARTIAL (lista explicitamente o que fica de fora)
```

O resultado vai para o pack (antes da cena) e para o relatório (depois).

### 21.3 Saídas

| Resultado | Consequência na cena |
|---|---|
| `ALLOW` | pode ser afirmado |
| `ALLOW_AS_RUMOR` | só como fala/crença atribuída; narrador não confirma |
| `ALLOW_AS_THEORY` | só como hipótese de personagem; nenhuma evidência `X` nas alternativas |
| `ALLOW_AS_PARTIAL` | só a parte liberada; o resto entra em `YOU MAY NOT REVEAL` |
| `BLOCK` | não pode aparecer; o pack cita o lock/gate |
| `CANON_PROPOSAL_REQUIRED` | a cena depende de fato inexistente (seção 62) |

---

## 22. Face Disclosure Firewall

### 22.1 Princípio

> **`CHARACTER_SEES = TRUE` não autoriza `READER_SEES = TRUE`.** (dossiê §1.4)

O rosto existe fisicamente (§15.1). O que o sistema controla é **quem recebe
informação facial, em que forma, e se ela é preservável**. Cada ocorrência vira
um evento facial estruturado, com colunas separadas para cada nível.

### 22.2 Estados distintos (§8 do prompt → dossiê)

| Estado | Definição operacional | Fonte |
|---|---|---|
| `FACE_PHYSICALLY_UNCOVERED` | o rosto está descoberto; não é crime por si só | §3.1 |
| `FACE_VISIBLE_TO_CHARACTER` | um terceiro tem acesso visual | §3.2 |
| `FACE_RECONSTRUCTIBLE` | o material (isolado ou razoavelmente combinável) permite recuperar representação facial coerente e individualizada | §3.4 (R9) |
| `FACE_VISIBLE_TO_READER` | a página entrega informação facial | §1.4 — **nunca** acima de `NON_RECONSTRUCTIBLE` |
| `FACIAL_RECORD_CREATED` | representação reconstruível preservada (foto, vídeo, desenho, pintura, arquivo, escultura, molde, 3D, IA, composição) | §3.3 |
| `AUTHORIZED_CAPTURE` | captura sob Sealed Facial Evidence | §3.5 (R6) |
| `SEALED_FACIAL_EVIDENCE` | a peça resultante, com custódia e acesso controlado | §3.5 |
| `SELF_VIEWING` | a pessoa vê o próprio rosto (deliberado ou acidental) | §3.7 (R8) |
| `EXTERNAL_RECORD` | registro facial que existe sob lei externa | §3.6 (R7) |

### 22.3 Contrato do evento facial

```yaml
- id: SD-0200
  event: EV-44                        # evento do ledger (a cena)
  type: FACE_EVENT
  subject: CHR-X                      # de quem é o rosto
  kind: UNCOVERING                    # UNCOVERING | EXPOSURE | CAPTURE | SELF_VIEWING | RECORD_ACCESS | EXTERNAL_RECORD_ENCOUNTER
  setting: SERVICE_COWL               # SERVICE_COWL | FITTING_CHAMBER | EMERGENCY_BREACH | MEDICAL | FORENSIC | PRIVATE | PUBLIC | UNKNOWN
  uncovered: true
  viewers: [CHR-P]                    # personagens com acesso visual (vazio = descoberto sem exposição)
  deliberate: {subject: true, viewers: [CHR-P]}
  reconstructibility: NON_RECONSTRUCTIBLE   # para o que PERSISTE (registro), seção 23
  record: null                        # ITM-* se algo foi preservado
  authorization: null                 # SFE-* (seção 25) quando captura autorizada
  consent_ref: SD-0199                # grant CONSENT_TO_FACIAL_EXPOSURE (seção 32), quando há viewers
  legal_reading: EXPOSURE             # NONE | EXPOSURE | OFFENCE_RECORD | AUTHORIZED | UNKNOWN — classificação, não julgamento moral
  reader_visibility: NONE             # NONE | NON_RECONSTRUCTIBLE   (RECONSTRUCTIBLE não é valor representável)
  narration_mode: FEEL_OBSERVE_INFER  # seção 27
```

`reader_visibility: RECONSTRUCTIBLE` **não existe** no enum (mesma técnica
da cartografia com `TRUE_EXIT`, D-CART-09): a garantia mais forte possível é
não haver como escrevê-lo.

### 22.4 O que o pack diz ao escritor quando o POV vê um rosto

```text
YOU MAY NARRATE:   o que o POV sente (mãos, respiração, distância, voz, temperatura, o silêncio do cofre aberto),
                   a consequência, o risco jurídico, a reação do observado, a memória do POV de que viu.
YOU MAY IMPLY:     que o POV viu; o efeito emocional; "ele sabia agora como era" sem dizer como era.
YOU MAY NOT:       traços, cores, formas, proporções, marcas, semelhanças ("parecia com…"), comparação com outro rosto,
                   qualquer conjunto de detalhes que, somado a detalhes já publicados, individualize o rosto.
```

A última linha é **Composite Reconstructibility aplicada à própria prosa**: o
pack lista os `face_fragments_published` do sujeito (projeção dos
`FACE_EVENT` com `reader_visibility: NON_RECONSTRUCTIBLE` e dos fragmentos
aprovados), para que o escritor e o Warden vejam o acumulado (seção 23.3).

### 22.5 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-FACE-01` | `reader_visibility` ausente ou fora do enum | `FACE_REVEAL_VIOLATION` | BLOCKER |
| `SR-FACE-02` | soma de fragmentos publicados do mesmo sujeito marcada `RECONSTRUCTIBLE` pelo Warden, ou fragmento com classe `RECONSTRUCTIBLE_FACE` entregue ao leitor | `FACIAL_RECONSTRUCTIBILITY_VIOLATION` | BLOCKER |
| `SR-FACE-03` | `viewers ≠ ∅` sem grant de exposição do sujeito e sem `setting` autorizado → é exposição sem consentimento; permitido como **evento** (Dark Romance pode representar violação), exige `consent.canonical` coerente e nunca resolve loop íntimo | `NONCONSENSUAL_EXPOSURE_UNMARKED` | HIGH |
| `SR-FACE-04` | `record ≠ null` sem `authorization` → `UNAUTHORIZED_RECONSTRUCTIBLE_FACIAL_RECORD` é **ofensa no mundo** (permitido como evento, com consequência); falta de marcação é que reprova | `FACIAL_RECORD_UNCLASSIFIED` | HIGH |
| `SR-FACE-05` | pré-filtro lexical: vocabulário de traço facial (`LEXICON.face_features`) próximo ao nome de personagem cujo rosto não está acessível ao POV, ou em cena com `FACE_EVENT` | `FACE_DESCRIPTION_SUSPECTED` | WARNING → Warden |
| `SR-FACE-06` | ilustração, capa, Story, mapa ou prompt de mídia com rosto reconstruível | REUSE do canon visual + `FACE_REVEAL_VIOLATION` | BLOCKER |
| `SR-FACE-07` | `FACE_CANON_TEMPLATE.md` / `face_consistency_required` do motor ligados para personagens de Redmur | `FACE_CANON_CONFLICT` | BLOCKER (seção 75.3) |

---

## 23. Facial Reconstructibility

### 23.1 Classificação (R9)

`NON_RECONSTRUCTIBLE · PARTIALLY_FACIAL · RECONSTRUCTIBLE_FACE`. Nenhum
percentual e nenhuma contagem de traços decidem sozinhos (§3.4). Distinções
obrigatórias: `IDENTIFIABLE ≠ FACIAL`, `RECOGNIZABLE ≠ RECONSTRUCTIBLE`,
`INFORMATION_ABOUT_A_FACE ≠ RECONSTRUCTIBLE_FACE`, `NECK = NOT FACE`.

### 23.2 Quem classifica

A classificação de um fragmento é **julgamento** (Warden + humano quando
contestado). O sistema guarda a classificação e **proíbe** o que é
estruturalmente decidível:

- fragmento classificado `RECONSTRUCTIBLE_FACE` nunca tem `reader_visibility`;
- o conjunto de fragmentos de um mesmo sujeito é reavaliado a cada fragmento
  novo (`SR-FACE-02`);
- "reconhecível por outro personagem" não sobe a classificação.

### 23.3 Composite Reconstructibility sem canonizar composição

```yaml
- id: FRG-0007                        # fragmento facial como item de informação
  subject: CHR-X
  carrier: ITM-021                    # documento/objeto/prosa (TEXT:) que o carrega
  class: PARTIALLY_FACIAL
  combinable_with: []                 # SÓ fragmentos canônicos; o sistema não cria o conjunto
  combined_class: null                # classificação do conjunto, quando declarado
```

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-FRC-01` | um `FRG-*` citado sem existir (o escritor "descobre" um fragmento que completa um rosto) | `SYSTEM_CAPABILITY_AS_INSTANCE` | FAIL |
| `SR-FRC-02` | conjunto declarado cuja `combined_class` = `RECONSTRUCTIBLE_FACE` com qualquer membro visível ao leitor | `FACIAL_RECONSTRUCTIBILITY_VIOLATION` | BLOCKER |
| `SR-FRC-03` | tatuagem, pintura, escultura ou molde com `depicts_face` individualizado | REUSE `HL-19` | BLOCKER |

TEST 23/24/25 (seção 76) exercitam exatamente esta tabela.

---

## 24. Self-Face Rules

| Fato (R8, §3.7) | Registro | Verificação |
|---|---|---|
| `NO_DELIBERATE_SELF_VIEWING` | `CR-R8-01` + `HL-11` | `FACE_EVENT kind: SELF_VIEWING, deliberate.subject: true` → `SELF_FACE_VIOLATION` (FAIL), salvo proposta aprovada |
| encontro acidental não é crime por si só | `CR-R8-02` | `deliberate.subject: false` → permitido; o pack avisa que a consequência é narrativa, não jurídica |
| memória facial própria é permitida | `CR-R8-03` | POV pode lembrar do próprio rosto (Adult Returner) |
| tocar o próprio rosto é permitido | `CR-R8-04` | autoconhecimento tátil; narrado como `FEEL` |
| espelhos comuns reconstrutores não são normais em Redmur | `CR-R8-05` | LEXICAL: "espelho" sem qualificador em cena dentro de Redmur → `WARNING` (Warden verifica se o espelho é do desenho previsto: fosco, oxidado, distorcido, gravado, interrompido, opaco) |
| residente desde a infância pode não ter memória visual útil do próprio rosto | `CR-R8-06` | personagem com `civic.born_redmur: true` e sem `SR:SELF_FACE_MEMORY` não descreve o próprio rosto |
| Adult Returner pode conservar memória anterior | `CR-R8-07` | permitido |
| origem/propósito do tabu | `UNK-SR-SELF-FACE-ORIGIN` | nenhuma cena explica (`PRO-SR-SELF-FACE-EXPLAINED`) |

"Espelho comum dentro de Redmur" é o TEST 22 (FAIL salvo mudança aprovada).

---

## 25. Sealed Facial Evidence

### 25.1 Capacidade, não instância

`CAP-SEALED-FACIAL-EVIDENCE` (`SYSTEM_CAPABILITY`, `instances: []`). A
existência da categoria **não** canoniza fotografia de Selka, Manfred,
protagonistas, Missing Forty Years, Aquele Dia ou qualquer arquivo (§3.5).

### 25.2 Instância (só por canon explícito)

```yaml
- id: SFE-0001                         # criado apenas por proposta aprovada ou evento REALIZED que o produz
  capability: CAP-SEALED-FACIAL-EVIDENCE
  context: FORENSIC                    # MEDICAL | FORENSIC | AUTOPSY | JUDICIAL
  necessity: "por que era necessária (texto curto)"
  minimum_necessary_exposure: true
  capturing_authority: ENT-*           # autoridade autorizada; nunca "OCP em geral"
  purpose_limitation: "finalidade única"
  custody: [{holder: ENT-*, from_event: EV-*}]
  access_log: [{by: CHR-*|ENT-*, event: EV-*, authorized: true}]
  derived_copies: []                   # toda cópia herda a classificação protegida
  item: ITM-*
```

### 25.3 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-SFE-01` | `SFE-*` sem algum dos 7 requisitos (necessidade, exposição mínima, autoridade, custódia, finalidade, acesso controlado, log) | `SEALED_EVIDENCE_INCOMPLETE` | FAIL |
| `SR-SFE-02` | acesso público, exibição pública, thumbnail, banco geral de reconhecimento | `SEALED_EVIDENCE_PUBLIC` (TEST 20) | BLOCKER |
| `SR-SFE-03` | `capturing_authority` genérica (`INST-OCP` como captura geral) ou polícia/OCP com autoridade facial ilimitada | `FACIAL_AUTHORITY_UNBOUNDED` (TEST 19) | BLOCKER |
| `SR-SFE-04` | cópia derivada sem classificação | `DERIVED_COPY_UNPROTECTED` | HIGH |
| `SR-SFE-05` | acesso sem linha em `access_log` | `SEALED_ACCESS_UNLOGGED` | HIGH |
| `SR-SFE-06` | o leitor recebe o conteúdo facial de uma SFE | REUSE `FACE_REVEAL_VIOLATION` | BLOCKER |

---

## 26. Outside Facial Records

| Fato (R7, §3.6) | Regra |
|---|---|
| Redmur regula exposição local, não existência global | `EXTERNAL_RECORD` nunca recebe ordem de destruição por autoridade de Redmur com efeito fora de Redmur → `EXTERNAL_PURGE_ASSUMED` (FAIL; TEST 21) |
| registros externos podem existir legalmente | possível; **nenhum específico existe** sem canon (`CAP-EXTERNAL-FACIAL-RECORD`, `instances: []`) — "Glasgow possui foto" é `SYSTEM_CAPABILITY_AS_INSTANCE` (§23) |
| Returner não precisa apagar a vida anterior; documentos externos válidos | transição cívica nunca exige `PURGE` |
| exposição deliberada dentro de Redmur segue regras locais | trazer registro externo para dentro e **mostrá-lo** é `FACE_EVENT kind: RECORD_ACCESS` com `legal_reading` local |

`LAWFUL_EXTERNAL_EXISTENCE ≠ LAWFUL_LOCAL_POSSESSION ≠ LAWFUL_LOCAL_EXPOSURE`:
três campos distintos no `ITM-*` que carrega um registro externo
(`external_lawful`, `local_possession_status`, `local_exposure_status`); a
regra `SR-EXT-02 EXTERNAL_LEGALITY_COLLAPSED` (HIGH) reprova quando um é
inferido do outro.

---

## 27. Faceless Expression Language

### 27.1 Gramática `FEEL → OBSERVE → INFER` (§15.1)

| Camada | Quem | Pode | Exemplo de forma (não de texto) |
|---|---|---|---|
| `FEEL` | o POV sobre si | sensação interna de olhos, boca, mandíbula, lágrimas, expressão sentida | "sentiu a própria boca endurecer" |
| `OBSERVE` | o POV sobre o outro | sinais **acessíveis**: voz, mãos, postura, corpo, distância, respiração, som do cofre, tatuagens, roupa, toque, contexto | "a voz baixou meio tom" |
| `INFER` | o POV conclui | inferência marcada como inferência | "pareceu sorrir" |
| **proibido** | o POV sobre o outro | expressão facial como observação objetiva sem acesso | "ele sorriu para ela" |

Quando o POV **tem** acesso facial (`FACE_EVENT` com o POV em `viewers`), a
expressão pode ser observada pelo personagem — mas a **descrição que chega ao
leitor** continua sob a seção 22 (o leitor recebe o efeito, não o rosto).

### 27.2 Implementação

| Parte | Mecanismo | Tipo |
|---|---|---|
| verbo de expressão facial com sujeito sem acesso facial para o POV | `LEXICON.facial_expression_verbs` (sorriu, franziu, piscou, corou, mordeu o lábio, arqueou a sobrancelha…) × personagens em cena sem `FACE_EVENT` para o POV | LEXICAL → `WARNING` `FACELESS_EXPRESSION_SUSPECTED` → Warden |
| marca de inferência presente | `LEXICON.inference_markers` (pareceu, talvez, como se, soube que…) na mesma frase | atenua o warning (não o elimina) |
| anti-loop gestual (§15.2) | REUSE `detect_repetition.py` com `books/sem-rosto/text_quality.yaml` → famílias `signal_families: {breath, fists, tilt, tremor, posture, coffer_sound, hands, voice}` com limite por capítulo e por janela | LEXICAL → `GESTURE_LOOP` (MEDIUM) |
| significado do gesto | **nenhum dicionário** "gesto X = emoção Y" (proibido pelo prompt §9 e pelo dossiê §15.2, §15.4) | — |
| "escrever rosto e traduzir para corpo" (§15.2) | julgamento | Warden + `PHYSICALITY_AND_BODY_AGENT` + `SUBTEXT_EDITOR` (REUSE) |

A contagem de famílias é **diagnóstico de densidade**, não significado: o
relatório diz "respiração apareceu 14 vezes no cap. 7", nunca "respiração
significa medo".

---

## 28. Non-Facial Identity (assinatura perceptiva)

### 28.1 Contrato

```yaml
# no canon da obra, por personagem (id do ledger)
signatures:
  - character: CHR-X
    channels:                          # só o que a autora declarou; nada inferido
      VOICE: "descrição curta"
      GAIT: null
      HANDS: null
      COFFER: {coffer: COF-0003, heraldry_notes: "…"}   # COFFER ≠ PERSON (HL-24)
      TATTOOS: [TAT-0011]
      SCENT: null
      TOUCH_PATTERN: null
      HABITS: []
    reliability: CONTEXTUAL            # sempre: SIGNATURE ≠ INFALLIBLE IDENTITY
```

### 28.2 Reconhecimento como evento (misrecognition permitido)

```yaml
- id: SD-0301
  event: EV-52
  type: RECOGNITION
  observer: CHR-P
  claimed_identity: CHR-X               # quem o observador acha que é
  actual: CHR-Y                         # engine-only; pode ser igual a claimed
  channels_used: [VOICE, COFFER]
  level: SOCIAL_RECOGNITION             # seção 40
  confidence: PARTIAL                   # FULL | PARTIAL | WRONG
```

- `SR-IDN-01 SIGNATURE_AS_PROOF` (HIGH): decisão de enredo (acusação, prova
  do crime, identificação de corpo) baseada **só** em `SOCIAL_RECOGNITION`.
- `SR-IDN-02 SIGNATURE_DRIFT` (MEDIUM): canal declarado contradito na prosa
  sem evento que explique (pré-filtro + `CHARACTER_CONTINUITY_REVIEWER`).
- `claimed ≠ actual` com o leitor informado cedo demais → REUSE
  `READER_KNOWLEDGE_LEAK`. Impersonation, fraude e roubo de cofre são
  representáveis e não mudam identidade (§10: roubar cofre não transforma
  alguém em outra pessoa).

---

## 29. Coffer Canon Engine

### 29.1 O que é canon (P0 + R1, R5, R10, R11)

`COFFERS.seed.yaml` registra **capacidades e classes**, com a fonte de cada
componente:

| Bloco | Conteúdo (ids) | Fonte |
|---|---|---|
| princípio | `CR-P0-01` THE HEAD IS INSIDE THE COFFER; `HL-21` | §2.1 |
| componentes possíveis | `CAP-COF-{INTERNAL_FRAME, EXTERNAL_SHELL, SHOULDER_YOKE, LOAD_DISTRIBUTION, ROTATING_COLLAR, PASSIVE_VENTILATION (obrigatória), ACTIVE_VENTILATION (opcional), OPTICAL_LABYRINTH, ACOUSTIC_CHANNELS, VOICE_GRILLE, FEEDING_DRAWER, DRAINAGE_HYGIENE, SERVICE_COWL, EMERGENCY_SYSTEMS, SEALS, MAINTENANCE_FITTING, SENSORS, FANS, PASSIVE_ID, LIMITED_TELEMETRY}` | §2.1, §9.2 |
| regras | sobrevivência não depende só de energia (`CR-P0-02`); Service Cowl: uncovering sem exposure (`CR-P0-03`); Emergency Breach pode exigir ruptura irreversível de selos (`CR-P0-04`); sem combinação universal (`HL-23`); Dual Authorization para procedimentos críticos (`CR-P0-05`) | §2.1–2.4 |
| classes predominantes | `CLS-A` Helmet · `CLS-B` Shoulder (padrão cívico) · `CLS-C` Torso Cage (custódia/contenção) · `CLS-D` Dual-Shell (elite; carcaças herdáveis e modernizáveis) — **não é casta jurídica rígida** | §2.5 |
| visitante | `CLS-VISITOR` comunica `OUTSIDER`, não casta | §5.1 |
| heráldica | material, acabamento, bordas, fechos, rebites, formato, desgaste comunicam classe/instituição/tradição/família/geração; `COFFER ≠ PERSON` | §2.6 |
| identificação | Coffer Civic Seal; `COFFER_IDENTITY ≠ PERSON_IDENTITY`; autenticação multifator não facial | §10.1 |
| ciclo de vida | `PERMANENT_REQUIREMENT ≠ PERMANENT_HARDWARE`: crescimento, substituição, fitting, manutenção, medicina, emergência, troca de componentes | §2.8 (R5) |
| indústria | coffermaking estratégico; fabricados, mantidos, restaurados, herdados, modernizados; não descartáveis | §11.1 |
| pânico | `PÂNICO + PROTEÇÃO` (claustrofobia: hiperventilação, suor, fechamento, compulsão de remover, distorções) | §8.7 |

Componente sem fonte (ex.: "trava magnética biométrica") é
`CANON_PROPOSAL_REQUIRED` — `TECHNOLOGY_CREEP` se for tecnologia (seção 39).

### 29.2 Instância de cofre (estado dinâmico)

```yaml
# fold de SD-* do tipo COFFER_* ; só existem cofres que alguma cena ou decisão canonizou
- id: COF-0003
  wearer: CHR-X
  class: CLS-D
  heritage_shell: {inherited: true, from: FAM-*|UNKNOWN, generations: UNKNOWN}
  civic_seal: SEAL-*|UNKNOWN
  components: [CAP-COF-SERVICE_COWL, ...]      # subconjunto das capacidades
  combination: CMB-0003
  fitted: {event: EV-*, dual_authorization: [ENT-*, ENT-*]}
  repair_history: [{event: EV-*, by: ENT-*, kind: MAINTENANCE}]
  wear: "descrição curta" | null
  social_signals: [CLASS, FAMILY]              # o que a heráldica comunica (sem provar identidade)
  state: FITTED                                # FITTED | SERVICE_OPEN | BREACHED | REMOVED_AUTHORIZED | REMOVED_UNAUTHORIZED | REPLACED | STOLEN | IN_STORAGE
```

### 29.3 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-COF-01` | componente fora de `CAP-COF-*` | `COFFER_COMPONENT_UNCANONICAL` | HIGH → proposta |
| `SR-COF-02` | remoção/instalação/fitting sem `dual_authorization` quando o procedimento é crítico | `DUAL_AUTHORIZATION_MISSING` | HIGH |
| `SR-COF-03` | `BREACHED` sem selos rompidos / sem protocolo extraordinário | `EMERGENCY_BREACH_TRIVIALIZED` | HIGH |
| `SR-COF-04` | estado muda sem `SD` causado por `EV-*` | `STATE_WITHOUT_CAUSE` | HIGH |
| `SR-COF-05` | cofre usado como prova de identidade | REUSE `HL-24` → `SIGNATURE_AS_PROOF` | HIGH |
| `SR-COF-06` | classe tratada como casta jurídica rígida (texto de regra do mundo) | `CASTE_AS_LAW` | MEDIUM (Warden) |
| `SR-COF-07` | cabeça "carregando" o cofre / pescoço como suporte de carga | `COFFER_MECHANICS_VIOLATION` (LEXICAL → Warden) | WARNING |

---

## 30. Combination Authority

### 30.1 Cadeia (R1, §2.7)

```text
KNOWING_COMBINATION ≠ PERMISSION_TO_TOUCH ≠ PERMISSION_TO_MANIPULATE_LOCK ≠ REMOVAL_AUTHORITY ≠ FACIAL_EXPOSURE_PERMISSION
```

### 30.2 Contrato

```yaml
- id: CMB-0003
  coffer: COF-0003                     # exatamente 1 (HL-23)
  value_status: UNDEFINED              # UNDEFINED | DEFINED_ENGINE_ONLY | REVEALED_TO_READER
  value_ref: null                      # GT-* engine-only quando DEFINED (nunca texto no pack de escrita)
  truth_status: FACT                   # a combinação existe; se o VALOR que alguém conhece é o certo, é projeção
# PROJETADOS (nunca escritos à mão):
#   who_knows[]      ← knowledge tokens  SR:CMB:FULL:CMB-0003 | SR:CMB:PARTIAL:CMB-0003 | SR:CMB:WRONG:CMB-0003
#   how_learned/when ← KNOWLEDGE_PROVENANCE do token
#   authorized_to_touch / _to_manipulate ← grants CONSENT_TO_COFFER_TOUCH / CONSENT_TO_LOCK_MANIPULATION (seção 32)
#   removal_authority ← institucional: ENT-* com procedimento + dual authorization (nunca derivável de CMB)
#   reader_knows     ← knowledge_state(READER) ∋ token ; e value_status
```

A combinação pode ter valor íntimo, criminal, informacional, romântico e
institucional (§2.7; mercado negro §11.4) — isso é **uso narrativo**, não
autoridade.

### 30.3 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-CMB-01` | ato de remoção/abertura justificado por conhecer a combinação (evento `REMOVE`/`OPEN_LOCK` com `caused_by` ou `acts_on_knowledge` apenas em `SR:CMB:*`, sem grant/autoridade) | `COMBINATION_AS_REMOVAL_AUTHORITY` (TEST 15) | BLOCKER |
| `SR-CMB-02` | conhecer a combinação usado como consentimento de toque/manipulação/exposição | `CONSENT_INFERENCE_VIOLATION` | BLOCKER |
| `SR-CMB-03` | `CMB-*` com escopo > 1 cofre | `UNIVERSAL_COMBINATION` (HL-23) | BLOCKER |
| `SR-CMB-04` | `value_status` sobe para `REVEALED_TO_READER` sem evento de revelação e aprovação | `COMBINATION_REVEALED_FOR_CONVENIENCE` | HIGH |
| `SR-CMB-05` | personagem usa o valor sem token `SR:CMB:FULL` (ou com `WRONG` e o lock abre) | `CHARACTER_KNOWLEDGE_LEAK` | FAIL |
| `SR-CMB-06` | valor da combinação em tatuagem como número explícito | REUSE `HL-19` | BLOCKER |
| `SR-CMB-07` | valor definido inventado pelo escritor | `IMPROVISED_CANON` | BLOCKER |

---

## 31. Coffer Touch Semantics

### 31.1 Princípio (R10, §15.4)

`PHYSICAL_TOUCH ≠ FIXED_MEANING`. `TOUCH_IS_AUTOMATICALLY_SEXUAL = FALSE`.
`TOUCH_IS_AUTOMATICALLY_ILLEGAL = FALSE`. O significado depende de zona,
pressão, duração, intenção, consentimento, relação e contexto.

### 31.2 Contrato (classificação, não significado)

```yaml
- id: SD-0405
  event: EV-60
  type: COFFER_TOUCH
  toucher: CHR-P
  wearer: CHR-X
  class: FRONTAL_PLATE_TOUCH     # FUNCTIONAL | INCIDENTAL | DELIBERATE_NONFUNCTIONAL | FRONTAL_PLATE |
                                 # LOCK_TOUCH | TWO_HANDED_HOLD | COFFER_TO_COFFER | VIOLENT_HANDLING
  zone: FRONTAL_PLATE
  pressure: LIGHT                # LIGHT | FIRM | FORCEFUL | UNKNOWN
  duration: BRIEF                # BRIEF | SUSTAINED | UNKNOWN
  context: PRIVATE               # PRIVATE | PUBLIC | MEDICAL | TECHNICAL | PARENTAL | PEDIATRIC | CUSTODIAL
  consent_ref: SD-0404           # grant CONSENT_TO_COFFER_TOUCH, quando aplicável
  reading: null                  # NUNCA preenchido pelo sistema; a leitura é da prosa e dos personagens (interpretations do ledger)
```

### 31.3 O que é estrutural e o que é julgamento

| Classe (dossiê) | Estrutural | Julgamento |
|---|---|---|
| functional / incidental | podem ser neutros; não exigem grant | — |
| deliberate nonfunctional | socialmente marcado → evento estrutural | significado na cena |
| frontal plate / frontal palm | alta significância pessoal; sem significado fixo → exige grant ou marca de violação | qual significado |
| lock touch | boundary-sensitive → exige `CONSENT_TO_LOCK_MANIPULATION` para manipular | — |
| unauthorized lock manipulation | violação grave → evento com consequência | — |
| two-handed coffer hold | alta intensidade dependente de contexto e consentimento → exige grant | — |
| coffer-to-coffer | proximidade; não automaticamente romântico/sexual; ritual oficial **não** é canon (§23) | — |
| violent handling | `consent.canonical: COERCIVE/NON_CONSENSUAL`; nunca payoff (INV-09) | — |

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-TCH-01` | toque de cofre usado como consentimento sexual (grant sexual derivado de `COFFER_TOUCH`, ou evento `SEXUAL` cujo único antecedente de consentimento é o toque) | `CONSENT_INFERENCE_VIOLATION` (TEST 16) | BLOCKER |
| `SR-TCH-02` | `reading` preenchido no canon | `TOUCH_DICTIONARY` | HIGH |
| `SR-TCH-03` | `LOCK_TOUCH` com manipulação sem grant e sem marca de violação | `LOCK_MANIPULATION_UNMARKED` | HIGH |
| `SR-TCH-04` | `COFFER_TO_COFFER` apresentado como ritual oficial | `SYSTEM_CAPABILITY_AS_INSTANCE` | FAIL |
| `SR-TCH-05` | contexto `PEDIATRIC`/`PARENTAL`/`MEDICAL`/`TECHNICAL` com `adult_semantics` | seção 33 | BLOCKER |

---

## 32. Consent State

### 32.1 Camadas independentes (§15.4–15.6)

```text
IDENTITY → Coffer/Face     ACCESS → Lock/Combination     BODY → Neck/Décolletage/Posture     CONSENT → camada independente
IDENTITY ≠ ACCESS ≠ BODY ≠ CONSENT ;  INTIMACY ≠ SEXUALITY ;  VIOLENCE ≠ DESIRE
AUTHORITY ≠ CONSENT ;  FEAR ≠ CONSENT ;  COERCION ≠ CONSENT
```

### 32.2 Grants por camada (complemento do bloco `consent` do ledger)

O ledger já guarda o consentimento **canônico e percebido** de eventos
adultos (REUSE INV-07). O que falta é **granularidade de Redmur**: cada
camada é um grant separado.

```yaml
- id: SD-0404
  event: EV-60
  type: CONSENT_GRANT                  # CONSENT_GRANT | CONSENT_REVOKE
  grantor: CHR-X
  grantee: CHR-P
  layer: CONSENT_TO_COFFER_TOUCH       # CONSENT_TO_TOUCH | CONSENT_TO_COFFER_TOUCH | CONSENT_TO_LOCK_MANIPULATION |
                                       # CONSENT_TO_REMOVAL | CONSENT_TO_NECK_TOUCH | CONSENT_TO_BODY_TOUCH |
                                       # CONSENT_TO_SEXUAL_ACTIVITY | CONSENT_TO_FACIAL_EXPOSURE
  scope: THIS_SCENE                    # THIS_SCENE | UNTIL_REVOKED | {until_event: EV-*}
  given_under: FREE                    # FREE | AUTHORITY_PRESSURE | FEAR | COERCION | DECEPTION | INTOXICATION | UNKNOWN
  capacity: FULL                       # FULL | CONSTRAINED | NONE   (espelha ability_to_refuse)
  evidence_to_reader: "o que a página mostra do consentimento (curto)"
```

`given_under ∉ {FREE}` ⇒ o grant é **inválido como consentimento**
(é registrado para a história, e o evento correspondente precisa de
`consent.canonical` coerente no ledger: `DUBIOUS`/`COERCIVE`/`NON_CONSENSUAL`).

### 32.3 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-CNS-01` | ato de uma camada sem grant válido da **mesma** camada, não marcado como violação | `CONSENT_INFERENCE_VIOLATION` | BLOCKER |
| `SR-CNS-02` | grant de uma camada deduzido de outra (combinação → toque; toque de cofre → pescoço; pescoço exposto → toque; decote → toque; autoridade → remoção) | `CONSENT_INFERENCE_VIOLATION` (hard consent locks §15.5) | BLOCKER |
| `SR-CNS-03` | grant com `given_under` ≠ `FREE` tratado como consentimento (resolve loop íntimo, ou `consent.canonical: CONSENSUAL`) | REUSE INV-09 `COERCION_AS_PAYOFF` + `CONSENT_UNDER_DURESS` | BLOCKER |
| `SR-CNS-04` | grant usado depois de `CONSENT_REVOKE` | `CONSENT_AFTER_REVOCATION` | BLOCKER |
| `SR-CNS-05` | evento adulto sem bloco `consent` | REUSE `CONSENT_MISSING` | HIGH |
| `SR-CNS-06` | medo/coerção reclassificados como consentimento pela narração | JUDGMENT (Warden + `ANTI_MANIPULATION_GUARDIAN`) | — |

Dark Romance pode representar desejo, conflito, violência, transgressão e
relações moralmente problemáticas (§15.5): o sistema **não bloqueia o
evento**; bloqueia a **reclassificação** de medo ou coerção como consentimento.

---

## 33. Age Semantic Firewall

### 33.1 Locks

`HL-06` (`MINOR_EROTIC_SEMANTICS = ABSOLUTELY_DISABLED`,
`NARRATIVE_EROTICIZATION_OF_MINORS = FORBIDDEN`) e `HL-26`
(`PEDIATRIC_ACCESS = CLINICAL / PROTECTIVE / FUNCTIONAL`). Adult status é
necessário, **não suficiente** (§15.5): o contexto adulto precisa estabelecer
a leitura.

### 33.2 Três camadas de proteção

| Camada | Mecanismo | Tipo |
|---|---|---|
| Idade canônica | REUSE ledger: `age` inteiro, `null` = desconhecida ≠ adulta; INV-06 `ADULT_SEDUCTION_FAIL`; RI HB-01; idade **nunca** inferida de aparência (rosto oculto — DEDR D-DEDR-14) | STRUCTURAL |
| Contexto da cena | o pack calcula `adult_semantics: ENABLED | DISABLED` por cena: `DISABLED` se qualquer participante tem `age < 18` ou `null`, ou se o contexto é `PEDIATRIC`/`PARENTAL`/`CHILD_PROTOCOL`/`MEDICAL` com menor; o pack remove do contrato **todo** registro de semântica adulta (pescoço, decote, combinação como intimidade, progressão `COFFER → EDGE → NECK → CLAVICLE → CLEAVAGE → BODY`) | STRUCTURAL |
| Léxico | `LEXICON.adult_semantics` (desejo, erótico, sensual, provocante, excitação, carícia… e o framing do pescoço/decote) em cena `DISABLED` | LEXICAL → `MINOR_EROTIC_SEMANTIC_VIOLATION` suspeito → Warden; confirmação = BLOCKER |

### 33.3 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-AGE-01` | `SD` de `COFFER_TOUCH`/`CONSENT_GRANT` com camada sexual/de pescoço/de corpo envolvendo participante `< 18` ou `null` | `MINOR_EROTIC_SEMANTIC_VIOLATION` (TEST 18) | BLOCKER |
| `SR-AGE-02` | cena `DISABLED` com evento de `ADULT_EVENT_KINDS` | REUSE HB-01 | BLOCKER |
| `SR-AGE-03` | cena `DISABLED` com termos de `adult_semantics` | `MINOR_EROTIC_SEMANTIC_SUSPECTED` | WARNING → Warden (FAIL se confirmado) |
| `SR-AGE-04` | toque médico/técnico/parental/pediátrico com `adult_semantics` | `PEDIATRIC_EROTICIZATION` | BLOCKER |
| `SR-AGE-05` | idade de personagem em cena íntima derivada de aparência/voz/corpo | `AGE_INFERRED` | BLOCKER |

TEST 17 (pescoço adulto em contexto apropriado recebe carga erótica → PASS)
exige: todos os participantes com `age ≥ 18`, contexto adulto, grant de
`CONSENT_TO_NECK_TOUCH` quando há toque (exposição sem toque não exige grant:
`EXPOSED_NECK ≠ CONSENT_TO_TOUCH` protege a outra direção).

---

## 34. Six-Month Child Protocol

### 34.1 Máquina de estados (P2 + R3, R4, R5, R11)

```text
BORN
 └─▶ NEONATAL_WINDOW        pais podem conhecer visualmente o recém-nascido; FACIAL_RECORD proibido (§4.1)
      └─▶ TRANSFER           após estabilização clínica (§4.2)
           └─▶ INSTITUTIONAL_CUSTODY   ~6 meses; sem visitas presenciais regulares; CHILD_BULLETINS (saúde, peso,
           │                           alimentação, desenvolvimento, fitting, retorno)
           │                           CONTEÚDO INTEGRAL = UNK-SR-SIX-MONTH-CONTENTS
           └─▶ THE_RETURN     ~6 meses; retorna com o primeiro sistema de proteção apropriado à idade (§4.3)
                └─▶ INFANT_PROTECTION   estágios funcionais possíveis: INFANT_VEIL → INFANT_FRAME → FIRST_COFFER
                     └─▶ REPLACEMENT_THROUGH_GROWTH   (obrigação permanente, hardware não — R5)
```

- A sequência `INFANT_VEIL → INFANT_FRAME → FIRST_COFFER` é
  `SYSTEM_CAPABILITY` ("pode ocorrer progressivamente", §4.4): o sistema
  **não** exige nem presume os três estágios para uma criança específica.
- O desenho pediátrico prioriza segurança clínica e desenvolvimento; nunca
  miniaturização de cofre adulto (§4.4) → LEXICAL/Warden.
- **Crianças visitantes não entram no protocolo** (§5.3): transição de
  criança com `category: VISITOR` para `TRANSFER` → `VISITOR_CHILD_IN_PROTOCOL` (BLOCKER).
- O Estado sabe que o sistema existe; pode haver inspeção, regulação,
  licenciamento (§7.5). O prédio pode ser visível (`HL-25`); sua localização
  é `UNK-SR-CHILD-FACILITY-LOCATION` (D-SR-05).

### 34.2 O que cada conhecedor pode saber

| Conhecedor | Pode | Não pode |
|---|---|---|
| pais | memória facial neonatal (`SR:NEONATAL_FACE_MEMORY:<child>`); boletins | preservar representação facial identificável |
| instituição | o que o dossiê atribui a ela (procedimento, boletins) | nada que resolva `UNK-SR-SIX-MONTH-CONTENTS` |
| leitor | o que a página mostra do procedimento visível | o conteúdo integral; a teoria como fato |

### 34.3 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-CPR-01` | cena revela o que ocorre integralmente nos seis meses | `UNKNOWN_AS_FACT` / `PREMATURE_MYSTERY_REVEAL` | BLOCKER |
| `SR-CPR-02` | troca de crianças narrada como fato | `PRO-SR-CHILD-SUBSTITUTION-FACT` → `THEORY_AS_FACT` | BLOCKER |
| `SR-CPR-03` | `FACIAL_RECORD` neonatal sem enquadramento de ofensa | REUSE `FACIAL_RECORD_UNCLASSIFIED` | HIGH |
| `SR-CPR-04` | qualquer semântica adulta em cena do protocolo | REUSE seção 33 | BLOCKER |
| `SR-CPR-05` | local do protocolo posicionado no mapa | `CARTOGRAPHIC_CONTRADICTION` → `CANON_PROPOSAL_REQUIRED` | FAIL |
| `SR-CPR-06` | "prédio secreto" como fundamento do mistério | `FACILITY_VISIBILITY_AS_TRANSPARENCY` (HL-25, invertido) | MEDIUM (Warden) |

---

## 35. Visitor State Machine

### 35.1 Três eixos ortogonais (nunca um só "status")

| Eixo | Valores | Muda por |
|---|---|---|
| `category` | `VISITOR · OUTSIDER_CONTRACTOR · OFFICIAL · BORN_REDMUR · RESIDENT · RETURNER` (dossiê §6) + subcategorias de visitante (§5.3: turista, jornalista, profissional externo, familiar, autoridade, prestador) | evento institucional |
| `civic_link` | `NONE · ELIGIBLE · REACTIVATION_IN_PROCESS · ACTIVE · DEPARTED · RELEASED` | evento institucional (reativação, release) |
| `presence` | `OUTSIDE · VEIL_HOUSE · TRANSFER_ZONE · INSIDE` | movimento (cartografia) |

`REACTIVATION_IN_PROCESS` é **estado de modelagem** para "a reativação depende
de processo institucional aplicável" (§6.2) — os passos do processo são
`CANON_UNKNOWN` além do que §6.3 lista (dual authorization, medidas, fitting,
stabilization, ventilação, locking, sealing, mobility test; sedação não é
rotina).

### 35.2 Visitante (P3)

```text
OUTSIDE ──(entra na Veil House)──▶ VEIL_HOUSE ──(aceita Visitor Coffer em fitting chamber privada)──▶ INSIDE
                                      └──(recusa)──▶ OUTSIDE        "Se recusar: simplesmente não entra." (§5.1)
INSIDE ──(sai)──▶ OUTSIDE            Visitors may leave. (§6.5)
```

- dispositivos visuais podem ser lacrados/armazenados/limitados; **sem
  obrigação geral de apagar** (§5.2) → `DEVICE_PURGE_ASSUMED` (HIGH);
- documentos fotográficos usam protocolo de ocultação facial (§5.2);
- mercadorias podem usar `TRANSFER_ZONE` (§5.3);
- Police Scotland, bombeiros, paramédicos e autoridades competentes mantêm
  seus poderes; emergências podem sobrepor o protocolo local (§5.3);
- entrada acidental: proteção e correção, não punição automática (§5.3);
- a posição física de Veil House/Transfer Zone é `UNK-SR-*` até decisão
  cartográfica (D-SR-06).

### 35.3 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-VIS-01` | visitante dentro sem ter aceitado o Visitor Coffer | `VISITOR_PROTOCOL_BYPASS` (permitido só como evento de transgressão marcado) | HIGH |
| `SR-VIS-02` | visitante impedido de sair por força/regra (não por escolha, relação, dívida, medo humano) | `OPEN_GATE_VIOLATED` | BLOCKER |
| `SR-VIS-03` | Visitor Coffer comunicando casta | `VISITOR_COFFER_CASTE` | MEDIUM |
| `SR-VIS-04` | autoridade externa competente sem seus poderes dentro de Redmur | `EXTERNAL_AUTHORITY_SUSPENDED` | HIGH |
| `SR-VIS-05` | entrada acidental punida automaticamente | `ACCIDENTAL_ENTRY_PUNISHED` | MEDIUM |

---

## 36. Returner State Machine

### 36.1 Transições (P4 + R2)

```text
                 presença                         vínculo cívico
BORN_REDMUR/RESIDENT  ACTIVE ──(sai fisicamente)──▶ DEPARTED   (PHYSICAL_DEPARTURE ≠ CIVIC_RELEASE, §6.1)
DEPARTED ──(processo de release)──▶ RELEASED                    (Civic Release, §6.4)
DEPARTED/ELIGIBLE + presença INSIDE ──▶ continua DEPARTED/ELIGIBLE   (PHYSICAL_RETURN ≠ CIVIC_REACTIVATION, R2)
ELIGIBLE ──(aceitação + processo)──▶ REACTIVATION_IN_PROCESS ──(instalação)──▶ ACTIVE (category RETURNER)
ACTIVE (RETURNER) ⇒ regras de Facial Preservation + cofre individual permanente, não Visitor Coffer (§6.3)
```

Nascimento em Redmur não cria obrigação eterna absoluta (§6.1).

### 36.2 Contrato de transição

```yaml
- id: SD-0500
  event: EV-70
  type: CIVIC_TRANSITION
  person: CHR-P
  axis: civic_link                       # category | civic_link | presence
  from: ELIGIBLE
  to: REACTIVATION_IN_PROCESS
  preconditions_met: [ACCEPTANCE]        # vocabulário do CIVIC.seed (só o que o dossiê lista)
  documents: [ITM-*]
  authorities: [ENT-*, ENT-*]            # dual authorization quando há instalação
```

### 36.3 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-CIV-01` | mudança de `civic_link` causada por mudança de `presence` (cruzar a fronteira ativa Returner) | `PHYSICAL_RETURN_AS_REACTIVATION` (HL-09) | BLOCKER |
| `SR-CIV-02` | `ACTIVE` como Returner sem instalação de cofre individual | `RETURNER_WITHOUT_COFFER` | HIGH |
| `SR-CIV-03` | Returner ativo com Visitor Coffer | `RETURNER_WITH_VISITOR_COFFER` | HIGH |
| `SR-CIV-04` | sedação como rotina da instalação | `SEDATION_AS_ROUTINE` | MEDIUM |
| `SR-CIV-05` | release tratado como sair fisicamente | `DEPARTURE_AS_RELEASE` | HIGH |
| `SR-CIV-06` | Returner obrigado a apagar vida anterior | REUSE `EXTERNAL_PURGE_ASSUMED` | FAIL |

---

## 37. Palimpsest Jurisdiction

### 37.1 Tabela de competência (P5, R3)

```yaml
# JURISDICTION.seed.yaml
layers:
  NORMAL_SCOTLAND:      # Redmur integra Escócia e Reino Unido; não é secreta (§7)
    competences: [TAXATION, COURTS, POLICING, NHS, PUBLIC_SERVICES, GENERAL_LAW, CRIMINAL_PROSECUTION]
    bodies: {POLICING: ENT-POLICE-SCOTLAND, CRIMINAL_PROSECUTION: ENT-COPFS, COURTS: ENT-SCOTTISH-COURTS, NHS: ENT-NHS}
  PRESERVATION_REDMUR:
    competences: [FACIAL_PRESERVATION, COFFERS, FITTINGS, SPECIAL_REGISTRIES, VISITORS, RETURNERS, DETERMINED_PROTOCOLS]
    bodies: {STATUTORY: INST-OCP, CIVIC_SECURITY: INST-CONSTABULARY}   # Constabulary = wardens de competência limitada (§7.4)
statute: {id: CR-P5-ACT, name_status: PROVISIONAL, date: UNKNOWN}      # Redmur Preservation Act (§7.1; D-SR-16)
savings_clauses: {exists: true, why: UNK-SR-SAVINGS-CLAUSES-WHY}       # §7.3
```

### 37.2 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-JUR-01` | ato de `INST-OCP`/`INST-CONSTABULARY` fora de suas competências (prender por crime comum como polícia soberana, julgar, tributar) | `JURISDICTION_OVERREACH` | HIGH |
| `SR-JUR-02` | poder policial de Redmur fora de Redmur; OCP como polícia internacional | `EXTRATERRITORIAL_POWER` (HL-10) | BLOCKER |
| `SR-JUR-03` | Redmur tratada como Estado soberano / com fronteira internacional | `SOVEREIGNTY_ASSUMED` | BLOCKER |
| `SR-JUR-04` | Police Scotland/COPFS/tribunais sem competência em Redmur | `NORMAL_SCOTLAND_SUSPENDED` | HIGH |
| `SR-JUR-05` | "Londres nunca soube" como premissa | `STATE_IGNORANCE_ASSUMED` (a pergunta canônica é por que gerações preservaram a anomalia, §7.3) | MEDIUM (Warden) |
| `SR-JUR-06` | antiga carta real isolada como explicação da autoridade contemporânea | `CHARTER_AS_EXPLANATION` (§7) | MEDIUM |

---

## 38. The Pull

### 38.1 Modelo multicausal (P6)

Componentes canônicos (etiquetas de causa, não forças): `ANONYMITY_RELIEF`,
`FORBIDDEN_INTIMACY`, `SECRET_SEEKING_COMPULSION`, `SOCIAL_ROOTING`,
`PERCEPTUAL_ACCLIMATIZATION`, `DARK_EROTIC_FIELD`, `COFFER_PANIC_PROTECTION`
(§8.1–8.7). `THE_PULL_COMPLETE_EXPLANATION` = `UNK-SR-PULL-COMPLETE`
(permanente: "Nunca deve ser integralmente explicado", §8).

### 38.2 Como uma decisão de ficar é representada

Uma decisão estrutural de ficar/voltar é um evento do ledger com `caused_by`
em `GT-*`/`EV-*` humanos (REUSE INV-01). Opcionalmente, `SD`
`PULL_FACTORS: [SOCIAL_ROOTING, ...]` etiqueta a causa.

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-PUL-01` | decisão de ficar sem causa humana na ancestralidade | `MAGICAL_CAUSALITY` (HL-02) | BLOCKER |
| `SR-PUL-02` | The Pull como maldição, hipnose, campo, entidade (LEXICON.pull_supernatural) | `SUPERNATURAL_CONFIRMATION` suspeito → Warden | WARNING/FAIL |
| `SR-PUL-03` | todos os componentes explicitados como a explicação completa | `PREMATURE_RESOLUTION` (`MYS-THE-PULL`) | BLOCKER |
| `SR-PUL-04` | Livro 1 com explicação de The Pull fora de subtexto (evento de revelação que ensina `UNK-SR-PULL-*`) | `BOOK1_HISTORY_LOCK_VIOLATION` | BLOCKER |

Metáfora de POV ("a cidade parecia chamá-la") é permitida como `FEEL`; a
fronteira entre metáfora e afirmação causal é julgamento do Warden.

---

## 39. Technology Veil

| Categoria (P7) | Regra operável |
|---|---|
| `PUBLIC_TECHNOLOGY` | papel, carimbo, livro, ficha — interface jurídica/cultural (`PAPER FACE`) |
| `INSTITUTIONAL_TECHNOLOGY` | bancos de dados, servidores, backups, indexação, sistemas externos (`DIGITAL SHADOW`) |
| `HIDDEN_TECHNOLOGY` | deve permanecer plausível e contemporânea |
| `EXTERNAL_TECHNOLOGY` | o mundo é contemporâneo; dispositivos de visitante podem ser lacrados |
| `FORBIDDEN_TECHNOLOGY` | vigilância facial indiscriminada; banco geral de reconhecimento facial; IA central onisciente |

Redmur **não** é tecnologicamente atrasada (eletricidade, água, saneamento,
medicina moderna, telecom, logística, informática). Cofres podem ter
sensores, ventiladores, identificação passiva e telemetria técnica limitada;
segurança fundamental não depende só de eletrônica; preferência por sensores
ambientais, identificação mecânica e biometria não facial (§9.2).

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-TEC-01` | tecnologia sem categoria ou além do contemporâneo plausível | `TECHNOLOGY_CREEP` | HIGH → proposta |
| `SR-TEC-02` | IA central onisciente; vigilância facial generalizada | `FORBIDDEN_TECHNOLOGY_PRESENT` (HL-27) | BLOCKER |
| `SR-TEC-03` | Redmur retratada como pré-moderna em infraestrutura | `TECH_REGRESSION` | MEDIUM (Warden) |
| `SR-TEC-04` | sobrevivência do usuário dependente só de bateria | REUSE `HL-21` | HIGH |

---

## 40. Identity Stack

`PEOPLE RECOGNIZE. INSTITUTIONS VERIFY. FORENSICS PROVE.` (§10). Três níveis,
cada reconhecimento/prova tem um:

| Nível | Canais | Pode sustentar | Não sustenta sozinho |
|---|---|---|---|
| `SOCIAL_RECOGNITION` | voz, marcha, movimento, mãos, postura, altura, proporções, cheiro, respiração, roupa, cofre, hábitos, contexto (Faceless Literacy) | convicção de personagem, suspeita | acusação formal, prova do crime |
| `CIVIC_VERIFICATION` | Coffer Civic Seal, autenticação multifator não facial, registros | ato institucional | prova forense |
| `FORENSIC_VERIFICATION` | perícia (e, quando cabível, SFE) | prova | — |

Impersonation temporária é possível; roubo de cofre não troca identidade;
misidentification, fraude, prova parcial e *identity mismatch* são estados
representáveis via `RECOGNITION.confidence` e `claimed ≠ actual`.

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-IDS-01` | solução do crime baseada só em `SOCIAL_RECOGNITION` | `SIGNATURE_AS_PROOF` | HIGH |
| `SR-IDS-02` | um único sinal tratado como substituto do rosto | `SINGLE_SIGNAL_IDENTITY` | MEDIUM |
| `SR-IDS-03` | selo cívico tratado como pessoa (`COFFER_IDENTITY = PERSON_IDENTITY`) | REUSE `HL-24` | HIGH |

---

## 41. Tattoo Semiotics

`BODY = INFORMATION`, `BODY ≠ TRUTH` (§10.2–10.3). Tatuagens podem
representar rituais, animais, luas, relíquias, religião, profanação,
sexualidade adulta, histórias, passado, enigmas, pertencimento, mentiras.

```yaml
- id: TAT-0011
  bearer: CHR-X
  placement: "local do corpo"
  motifs: [MOON_PHASE, ANIMAL]          # vocabulário: symbols, animals, moon_phases, objects, patterns, composition, ritual_imagery
  encodes_digits: false                  # true é proibido (HL-19)
  depicts_face: false                    # true é proibido (HL-19)
  readings: []                           # leituras são evidência (EVD-*) com source CHR-*, nunca fato
  clue_ref: null                         # EVD-* quando é pista declarada; tatuagem pode, não precisa, esconder pista (§23)
```

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-TAT-01` | combinação por número explícito (ex.: dígitos tatuados) | `TATTOO_NUMERIC_COMBINATION` (HL-19) | BLOCKER |
| `SR-TAT-02` | rosto reconstruível em tatuagem | `FACIAL_RECONSTRUCTIBILITY_VIOLATION` | BLOCKER |
| `SR-TAT-03` | leitura de tatuagem narrada como verdade | `BODY_AS_TRUTH` | FAIL |
| `SR-TAT-04` | toda tatuagem tratada como pista | `SYSTEM_CAPABILITY_AS_INSTANCE` (§23) | MEDIUM |
| `SR-TAT-05` | tatuagem com semântica sexual adulta em menor | REUSE seção 33 | BLOCKER |

---

## 42. Economy Model

Registros (P9, §11): Redmur **não** é autossuficiente (`CR-P9-01`); usa GBP,
banco britânico, tributação, contratos, importação, exportação, logística;
produz localmente parte relevante de alimentos, agricultura, artesanato,
couro, metal, madeira, tailoring e manutenção; importa medicamentos,
equipamentos, combustível, componentes, tecnologia, veículos, industriais.
Setores com registro próprio: coffermaking (`CR-P9-COFFERMAKING`), tattoo
economy (tatuadores de grande prestígio; reputação externa possível),
Manfred Estate Network (terras, leases, imóveis, trusts, propriedades
agrícolas, participações; sem soberania), information market (informação
pode valer mais que dinheiro; mercadorias clandestinas possíveis:
combinação, Facial Record, arquivo, registro infantil, documento antigo,
identidade — Facial Records clandestinos raros, perigosos, difíceis de
autenticar).

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-ECO-01` | Redmur apresentada como autossuficiente / fora do sistema monetário britânico | `SELF_SUFFICIENCY_ASSUMED` | HIGH |
| `SR-ECO-02` | item específico no mercado negro (uma combinação concreta, um Facial Record concreto) sem canon | `SYSTEM_CAPABILITY_AS_INSTANCE` | FAIL |
| `SR-ECO-03` | Facial Record clandestino fácil de obter/autenticar | `BLACK_MARKET_TRIVIALIZED` | MEDIUM (Warden) |

---

## 43. Body Gap

```yaml
- canon_id: CR-P9-BODYGAP
  flags: {BODY_CULTIVATION_PRESSURE: true, BODY_UNIFORMITY: false, BODY_DISPARITY: OBSERVABLE,
          SINGLE_CAUSE: false, FULL_EXPLANATION: UNK-SR-BODY-GAP}
  mundane_causes_possible: [GENETICS, AGE, PROFESSION, ACCIDENT, INEQUALITY, NUTRITION, MEDICINE, COFFER_EFFECTS]
  source: {id: SRC-DOSSIER, location: "§11.5"}
```

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-BG-01` | população retratada como corporalmente uniforme | `BODY_UNIFORMITY_ASSUMED` | MEDIUM (Warden) |
| `SR-BG-02` | uma causa única apresentada como explicação da disparidade | `PREMATURE_RESOLUTION` (`MYS-BODY-GAP`) | HIGH |
| `SR-BG-03` | corpo cultivado de menor com framing adulto | REUSE seção 33 | BLOCKER |

---

## 44. Blind Chronology

### 44.1 Seis cronologias, só uma armazenável hoje

| Cronologia | O que é | Armazenada? |
|---|---|---|
| `TRUE_CHRONOLOGY` | o que de fato ocorreu | **não existe** (`MYS-TRUE-CHRONOLOGY`, `UNK-SR-*`); P10-B reservada |
| `BLIND_CHRONOLOGY` (P10-A) | a cronologia do Livro 1: o que se pode datar, com lacunas | sim: `CHRONO-*` com fonte e arquivo |
| `BELIEVED_CHRONOLOGIES` | o que grupos/personagens creem | projeção de tokens `SR:BELIEVES:CHRONO-*` |
| `HISTORICAL_CLAIMS` | o que registros afirmam | `CHRONO-*` `epistemic_class: HISTORICAL_CLAIM` |
| `RUMOR_CHRONOLOGIES` | versões orais | `RUM-*`/`RUV-*` com datas |
| `READER_CHRONOLOGY` | o que a página datou | projeção (`knowledge_state(READER)` ∩ `CHRONO-*`) |

### 44.2 Contrato

```yaml
- id: CHRONO-0004
  claim: "descrição neutra do que o registro data"
  claimed_date: {year: null, precision: UNKNOWN}   # nunca inventar ano
  archive: PAPER                                    # PAPER | STONE | BODY | VOICE (seção 46)
  carrier: ITM-*|TAT-*|RUM-*|RM-*
  epistemic_class: HISTORICAL_CLAIM
  contradicts: []                                   # CHRONO-* — contradição preservada, nunca resolvida
  interval: IN_BLACK_INTERVAL | BEFORE | AFTER | UNKNOWN
```

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-CHR-01` | cena estabelece ordem causal completa do intervalo | `TRUE_CHRONOLOGY_LEAK` | BLOCKER |
| `SR-CHR-02` | contradição entre `CHRONO-*` resolvida sem canon | `CHRONOLOGY_NORMALIZED` | HIGH |
| `SR-CHR-03` | ano inventado para evento histórico (`claimed_date.year` sem fonte) | `IMPROVISED_CANON` | HIGH |
| `SR-CHR-04` | `story_present_year` usado sem estar definido (hoje `UNKNOWN`, cartografia §24.1) | `CANON_PROPOSAL_REQUIRED` | — |

---

## 45. Missing Forty Years

`CR-P10-BLACK-INTERVAL`: aproximadamente quarenta anos perderam
**continuidade**; não são quarenta anos sem documentos (existem cartas,
registros, recibos, mortes, nascimentos, atas, objetos, documentos). Datas de
início e fim: `UNKNOWN`. `CAUSE = CANON_UNKNOWN`,
`DELIBERATE_ERASURE = UNCONFIRMED`, `SINGLE_ACTOR = UNCONFIRMED` (§12.1).
Orbitam o intervalo, **sem ordem causal definida**: Aquele Dia, Manfred,
Flarry, a criança perdida, cofres, Preservation Act, Six-Month Protocol.

Livro 1: descoberta permitida = **os quarenta anos existem como problema
real**; proibido = **o que aconteceu neles** (§12.4).

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-40Y-01` | intervalo apresentado como vazio documental ("não há registros") | `FORTY_YEARS_AS_EMPTY` | HIGH |
| `SR-40Y-02` | qualquer `UNK-SR-40Y-*` ensinado a qualquer conhecedor no Livro 1 | `BOOK1_HISTORY_LOCK_VIOLATION` (TEST 10) | BLOCKER |
| `SR-40Y-03` | ligação causal entre elementos que orbitam o intervalo afirmada como fato | `CAUSAL_ORDER_INVENTED` | BLOCKER |
| `SR-40Y-04` | apagamento deliberado ou ator único confirmado | `UNKNOWN_AS_FACT` | BLOCKER |

---

## 46. Four Archives

| Arquivo | O que preserva (§12.2) | Canal LTE típico |
|---|---|---|
| `PAPER` | o que instituições registraram | `DOCUMENT` |
| `STONE` | arquitetura, túmulos, edifícios, cofres, objetos | `OBJECT`, `ENVIRONMENT` |
| `BODY` | tatuagens, cicatrizes, corpos | `BEHAVIOR`, `OBJECT` (tatuagem como portadora) |
| `VOICE` | o que gerações repetiram oralmente | `DIALOGUE`, `MEMORY` |

**Nenhum é soberano.** Cada referência de evidência/item carrega
`archive_type`, `provenance`, `reliability` (`HIGH|MEDIUM|LOW|UNKNOWN`),
`tampering_risk`, `interpretation` (sempre como `readings` de `EVD-*`),
`contradictions`, `reader_visibility` (projeção), `character_access`
(projeção), `historical_period`, `associated_mysteries`.

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-ARC-01` | um arquivo declarado soberano sobre outro ("o papel prova, a voz mente") como regra | `ARCHIVE_SOVEREIGNTY` | HIGH |
| `SR-ARC-02` | contradição entre arquivos resolvida automaticamente | `ARCHIVE_CONFLICT_RESOLVED` | HIGH |
| `SR-ARC-03` | relação entre os quatro arquivos resolvida no Livro 1 | `PREMATURE_RESOLUTION` (`MYS-FOUR-ARCHIVES`) | BLOCKER |

---

## 47. Dead Archive

`CAP-DEAD-ARCHIVE` (`SYSTEM_CAPABILITY`): mortos podem funcionar como
arquivos involuntários; tatuagens sobrevivem a documentos; túmulos preservam
corpo, símbolos, cofres e informação material (§12.3). **Capacidade**: não
autoriza exumação, nem resolver os quarenta anos no Livro 1. Morte,
identificação post-mortem, autópsia, funeral, exumação e acesso facial
pós-morte pertencem ao futuro Death/Funeral System (§20.2) — este SDD só
reserva a interface:

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-DA-01` | evento de exumação sem proposta aprovada | `CANON_PROPOSAL_REQUIRED` | — |
| `SR-DA-02` | exumação que resolve `MYS-FORTY-YEARS` no Livro 1 | `BOOK1_HISTORY_LOCK_VIOLATION` | BLOCKER |
| `SR-DA-03` | acesso facial post-mortem sem enquadramento SFE | REUSE seção 25 | FAIL |

---

## 48. Manfred Power Model

### 48.1 Modelo (P11)

`POWER WITHOUT A THRONE` — `INHERITED STRUCTURAL GRAVITY` por terra,
patrimônio, capital, patronage, informação, arquivos privados, tradição,
relações, memória institucional, deferência cultural. Sem soberania; sem
controle automático de Police Scotland, OCP, tribunais ou instituições. Um
Manfred pode ouvir "não". `MANFRED ≠ MANFREDS`: facções, gerações, ricos,
pobres, reformistas, tradicionalistas, afastados, conflitos internos; pode
haver Manfred sem poder e não-Manfred com enorme influência na rede.
**There is no Manfred who knows everything the Manfreds know.**

### 48.2 Representação

```yaml
entities:
  - id: FAM-MANFRED                 # a família como ENTIDADE (patrimônio, nome); NUNCA como ator de evento
    entity_kind: FAMILY
    power_types: [LEGAL_POWER, INSTITUTIONAL_INFLUENCE, CULTURAL_DEFERENCE, FINANCIAL_POWER, LAND_POWER, INFORMATION_ACCESS]
    members: []                     # CHR-* declarados pelo pacote; nenhum criado por este SDD
    factions: []                    # FAC-MANFRED-* declaradas por proposta
    map_refs: [RM-*]                # Manfred Farm existe no mapa; outras propriedades: UNKNOWN
```

Uma afirmação de poder Manfred em evento/estado declara:
`{actor: CHR-*|FAC-MANFRED-*, when: chapter|CHRONO-*, power_type, evidence: [EVD-*|ITM-*], with_faction: FAC-*|null}` —
as quatro perguntas do dossiê (**qual Manfred? quando? com que evidência?
com qual facção?**) são campos obrigatórios.

### 48.3 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-MAN-01` | `FAM-MANFRED` como `actor`/`participant`/`caused_by` de evento, ou explicação causal genérica | `MANFRED_UNIVERSAL_CAUSALITY` (TEST 7) | FAIL (estrutural) |
| `SR-MAN-02` | pré-filtro: "os Manfred" + verbo causal em narração ou brief sem os 4 campos | `MANFRED_UNIVERSAL_CAUSALITY` suspeito | WARNING → Warden |
| `SR-MAN-03` | um `CHR-*` Manfred cujo conhecimento projetado ⊇ todos os fatos de arquivo familiar | `MANFRED_OMNISCIENCE` | HIGH |
| `SR-MAN-04` | Manfred com poder legal sobre Police Scotland/OCP/tribunais | `SOVEREIGNTY_ASSUMED` | BLOCKER |
| `SR-MAN-05` | "Manfred apagou os 40 anos" narrado como fato; ou apresentado sem alternativa viva | `THEORY_AS_FACT` / `HYPOTHESIS_MONOPOLY` | BLOCKER / MEDIUM |
| `SR-MAN-06` | Manfred novo criado pelo escritor | `IMPROVISED_CANON` | BLOCKER |

---

## 49. Madre Selka Firewall

### 49.1 O que é canon (P12, §14.2–14.9)

`ENT-SELKA`: mulher real; viveu em Redmur; freira; viveu durante os Missing
Forty Years; vida privada clandestina parcialmente incompatível com a
identidade religiosa pública (`PUBLIC_SELKA ≠ PRIVATE_SELKA`; detalhes
`RESERVED`); morreu em Redmur ou em circunstâncias diretamente ligadas à
cidade. Tinha tatuagens (quantidade e significado `UNKNOWN`). Incógnitas:
`UNK-SR-SELKA-DEATH`, `-GRAVE-LOCATION`, `-COFFER-MODEL`, `-TATTOO-MEANING`,
`-PRIVATE-LIFE`, `-PRAYER-ORIGIN` ("Aqui ninguém termina a oração." — origem
`RESERVED`). Rumores/teorias: `RUM-SELKA-COFFER`,
`THEORY-MISSING-GRAVE-IS-SELKA`, `RUM-TEN-RELICS` (Túmulo de Selka em
versões importantes; valor informacional).

### 49.2 Ontology firewall

`NO CROSSOVER DEPENDENCY` · `NO ONTOLOGY LEAKAGE`. O destino pós-morte de
Selka em outra obra (*1000 ANOS NO INFERNO DA LUXÚRIA*) **não** pode explicar
Redmur, confirmar magia, criar fantasma, causar The Pull, mover objetos ou
solucionar mistérios; não se explica didaticamente a identidade entre as
obras (§14.8).

| Mecanismo | Tipo |
|---|---|
| nenhum `CR-*`/evento/`SD` referencia ids, entidades ou regras de outra obra | STRUCTURAL |
| `LEXICON.selka_ontology` (vocabulário da outra obra: pós-morte, inferno, danação, aparição de Selka, voz de Selka que age…) em cena que menciona Selka | LEXICAL → Warden |
| nenhuma evidência com `S` sobrenatural sobre Selka | STRUCTURAL (HL-01) |

### 49.3 Book 1 Selka Lock (§14.9)

Permitido: `RUMOR → FRAGMENTO → CONTRADIÇÃO → PISTA → TEORIA`. Proibido no
Livro 1: encontrar túmulo, corpo ou cofre; descobrir tatuagens diretamente;
solucionar a morte; localizar a sepultura; resolver os Missing Forty Years
por Selka. `SELKA IS A KEY, NEVER THE KEY`; `ENCONTRAR SELKA ≠ RESOLVER SELKA`.

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-SEL-01` | evento B1 com `kind` ∈ {`FIND_GRAVE`, `FIND_BODY`, `FIND_COFFER`, `READ_TATTOOS_DIRECT`, `RESOLVE_DEATH`, `LOCATE_GRAVE`} sobre `ENT-SELKA` | `BOOK1_HISTORY_LOCK_VIOLATION` | BLOCKER |
| `SR-SEL-02` | revelação sobre Selka que colapsa `MYS-*` além de Selka (ela explica Redmur) | `SELKA_AS_THE_KEY` (TEST 30) | BLOCKER |
| `SR-SEL-03` | dependência de outra obra / ontologia importada | `SELKA_ONTOLOGY_LEAK` | BLOCKER |
| `SR-SEL-04` | tatuagem de Selka com código numérico | REUSE `HL-19` | BLOCKER |
| `SR-SEL-05` | estágio da escada de Selka acima de `TEORIA` no Livro 1 | `PREMATURE_RESOLUTION` | BLOCKER |
| `SR-SEL-06` | Selka centraliza a maior parte da evidência dos mistérios de série | `SELKA_OVERCENTRALIZATION` (fração de `EVD-*` de `MYS-*` reservados que citam `ENT-SELKA` > limiar, hipótese 0.5) | MEDIUM |

---

## 50. 1% Non-Human Rule

### 50.1 Registro epistêmico (P12, §14.1)

`RATIONAL` (sabemos o que ocorreu) · `AMBIGUOUS` (duas ou mais explicações
humanas possíveis) · `RESIDUAL` (a informação disponível não explica um
detalhe). `RESIDUAL ≠ SUPERNATURAL`. Estrutura possível:
`evento estranho → impressão sobrenatural → explicação racional parcial → alívio → detalhe residual`.

```yaml
- id: SD-0610
  event: EV-81
  type: ANOMALY
  register: RESIDUAL                  # RATIONAL | AMBIGUOUS | RESIDUAL
  human_explanations_available: [EVD-*|GT-*|EV-*]   # ≥1 para AMBIGUOUS/RESIDUAL; ≥2 para AMBIGUOUS
  residual_detail: "descrição neutra do que ficou sem explicação"
  # não existe campo para confirmação sobrenatural (HL-03)
```

### 50.2 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-NH-01` | `RESIDUAL` sem explicação humana parcial disponível | `RESIDUAL_WITHOUT_RATIONAL_PATH` | HIGH |
| `SR-NH-02` | `AMBIGUOUS` com < 2 explicações humanas | `AMBIGUITY_UNGROUNDED` | MEDIUM |
| `SR-NH-03` | evidência/narração confirma fantasma, maldição, entidade, portal | `SUPERNATURAL_CONFIRMATION` (TEST 8) | BLOCKER |
| `SR-NH-04` | densidade: `ANOMALY` em fração de cenas > limiar (hipótese: 0.15) ou em capítulos consecutivos > 2 | `NON_HUMAN_OVERUSE` ("não usar em toda cena") | MEDIUM |
| `SR-NH-05` | `RESIDUAL` com explicações humanas ainda possíveis | — | PASS (TEST 9) |

---

## 51. Crime Payoff Model

### 51.1 Contrato do Livro 1 (P14)

```text
CRIME → CLOSED     DARK ROMANCE → IRREVERSIBLE, NOT CLOSED     REDMUR → EXPANDED
```

O crime **não foi escolhido** (non-goal). O sistema cria um **slot**
verificável:

```yaml
crime_contract:
  id: CRIME-B1
  status: CANON_PROPOSAL_REQUIRED       # até a autora decidir
  requirements:                          # §16.1–16.6
    concrete: true
    bounded: true                        # menor que o mistério de Redmur
    investigable: true
    solvable: true
    human_motive: true                   # desejo | medo | vergonha | dinheiro | proteção | obsessão | ciúme | vingança | poder
    not_forty_years_question: true       # não pode ser "quem apagou os quarenta anos?"
    redmur_mechanisms_min: 2             # coffer | FACIAL_EXPOSURE | tattoo | caste | faceless recognition | body archive | institutional procedure
    retrospective_clues_min: 3
    crime_romance_coupling: REQUIRED
    double_edge_evidence: REQUIRED
    villain_explains_redmur: FORBIDDEN
    culprit_needs_redmur_truth: false    # "O criminoso não precisa conhecer a verdade de Redmur"
  interpretive_question: Q-CRIME-B1      # resolution_policy: RESOLVED_AT, resolved_at: LEDGER:EV-<revelação>
  cliffhanger_architecture: [CONVERGENCE, LAST_EVIDENCE, CRIME_REVELATION, HUMAN_MOTIVE,
                             ROMANTIC_CONSEQUENCE, DOUBLE_EDGE_EVIDENCE, LARGER_CONTRADICTION, CLIFFHANGER]   # §16.5
```

A **solução** do crime, quando existir, mora no ledger: GT(s) do culpado
(`MOTIVE`, `SECRET`) com `reader_access: {from_event: EV-<revelação>}`, eventos
`PLANNED` fora da página com `facts`, e `Q-CRIME-B1` com interpretações
concorrentes (suspeitos) e red herrings justos (REUSE LTE §17).

### 51.2 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-CRM-01` | `CRIME-B1` sem os requisitos (validador por campo) | `CRIME_CONTRACT_INCOMPLETE` | HIGH (plan) |
| `SR-CRM-02` | mecanismos de Redmur < 2, ou mecanismo sem evento/`SD` que o use | `CRIME_GENERIC` | HIGH |
| `SR-CRM-03` | motivo do culpado sem GT humano | `CRIME_WITHOUT_HUMAN_MOTIVE` | HIGH |
| `SR-CRM-04` | revelação do crime altera estado de `MYS-*` reservado (vilão explica Redmur) | `VILLAIN_EXPLAINS_REDMUR` (HL-18) | BLOCKER |
| `SR-CRM-05` | `Q-CRIME-B1` sem `RESOLVED_AT` no final | `CRIME_UNRESOLVED` | HIGH |
| `SR-CRM-06` | Livro 1 resolve crime intermediário | — | PASS (TEST 11) |

---

## 52. Fair Play Crime Ledger

### 52.1 Projeção sobre artefatos existentes

| Campo pedido | Fonte |
|---|---|
| `crime_id`, `victim`, `actors`, `motive`, `means`, `opportunity` | ledger (GT/EV) referenciado por `crime_contract` |
| `event`, `timeline` | eventos do ledger + staging da cartografia (tempo e lugar verificáveis) |
| `Redmur-specific mechanisms` | `SD-*` e eventos com `kind` do vocabulário do contrato |
| `evidence`, `clues`, `false_clues` | `EVD-*` de `Q-CRIME-B1` (`role: CLUE | RED_HERRING`) |
| `reader_access`, `character_access` | projeções (seções 17–18) |
| `retroactive relevance` | `discoverable_on: REREAD` + suporte `S` na interpretação vencedora |
| `solution`, `reveal_chapter` | `resolved_at` de `Q-CRIME-B1` |

### 52.2 Regras (REUSE + contrato P14)

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-FP-01` | < 3 evidências com `S` na interpretação resolvida, em capítulos **anteriores** à revelação, ≥ 2 capítulos distintos, ≥ 1 `FIRST_READ` (padrão DEDR `FOUNDATIONAL`) | `UNSEEDED_REVEAL` | HIGH |
| `SR-FP-02` | evidência decisiva cuja primeira âncora está no capítulo da revelação, ou que nenhum conhecedor podia acessar antes (custódia/staging) | `DEUS_EX_DOCUMENT` (TEST 12) | BLOCKER |
| `SR-FP-03` | revelação com crença do leitor revisada sem GT na ancestralidade | REUSE INV-11 `RETCON_DISGUISED_AS_TWIST` | HIGH |
| `SR-FP-04` | red herring sem causa no mundo ou sem contraevidência prévia | REUSE `RED_HERRING_UNFAIR`/`_WITHOUT_CAUSE` | HIGH |
| `SR-FP-05` | viagem/presença do culpado impossível no tempo | REUSE cartografia (`IMPOSSIBLE_TRAVEL`) | FAIL |
| `SR-FP-06` | identificação do culpado só por `SOCIAL_RECOGNITION` | REUSE `SIGNATURE_AS_PROOF` | HIGH |

---

## 53. Double-Edge Evidence

### 53.1 Definição operável

A evidência final `EVD-DE` precisa, **ao mesmo tempo** (§16.6):

- **(A)** ter `S` na interpretação resolvida de `Q-CRIME-B1` e ser a âncora de
  `resolved_at` (ou estar no mesmo evento);
- **(B)** abrir contradição maior: `S`/`C` em ≥1 `Q-*` ou evidência de um
  `MYS-*` reservado, **e** o estado projetado desse `MYS-*` sobe no máximo
  para `EXPANDING` — nunca `PARTIALLY_RESOLVED`/`RESOLVED`.

`LARGER_CONTRADICTION ≠ MACRO_MYSTERY_SOLUTION`. A evidência pode provar
mentira, incompatibilidade, data impossível, coordenada, conexão, ausência,
documento inconsistente, sobreposição impossível, identidade incorreta — mas
não explica **por quê**.

### 53.2 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-DE-01` | nenhuma evidência satisfaz (A) e (B) | `DOUBLE_EDGE_MISSING` | HIGH (final) |
| `SR-DE-02` | (B) eleva `MYS-*` reservado acima do teto | `PREMATURE_RESOLUTION` / `TRUE_CHRONOLOGY_LEAK` (TEST 14) | BLOCKER |
| `SR-DE-03` | (B) com `X` em interpretações de `Q-*` `NEVER` (fecha teoria) | REUSE `EVIDENCE_COLLAPSES_QUESTION` | BLOCKER |
| `SR-DE-04` | (A)+(B) corretos | — | PASS (TEST 13) |

---

## 54. Romance State Engine

### 54.1 REUSE do ledger

O par protagonista é `relationships[]` direcional do ledger (vocabulário de
dimensão aberto). As dimensões pedidas mapeiam assim:

| Pedido | Onde |
|---|---|
| attraction, trust, fear, resentment, desire, dependency, dominance, submission, vulnerability | dimensões do ledger (`relationship_delta`) — vocabulário da obra |
| knowledge_shared, secrets, suspicions | tokens de conhecimento (seção 17) |
| combination_knowledge | tokens `SR:CMB:*` (seção 30) |
| coffer_access, body_intimacy, neck_intimacy | grants por camada (seção 32) + `COFFER_TOUCH` |
| consent_state | bloco `consent` + grants |
| betrayals | eventos `kind: [BETRAYAL]` |
| relationship_irreversibility | marcas `IRREVERSIBLE` (seção 55) |

Atração é propriedade da relação, nunca atributo (INV-02); estado nunca é
escrito, é projetado (`STATE_RESET`, `POST_PAYOFF_AMNESIA`,
`HEAT_WITHOUT_HISTORY` — REUSE).

### 54.2 `CRIME_ROMANCE_COUPLING = REQUIRED` (§16.3)

| Direção | Elo projetado | Achado se vazio |
|---|---|---|
| crime → romance | ≥1 evento que é `ledger_event` de `EVD-*` de `Q-CRIME-B1` **e** tem `relationship_delta` no par | `CRIME_WITHOUT_ROMANTIC_COST` (HIGH) |
| romance → crime | ≥1 evento com `relationship_delta` no par que produz `knowledge_delta` usado depois em `acts_on_knowledge` de investigação, ou é `ledger_event` de evidência do crime | `ROMANCE_WITHOUT_INVESTIGATIVE_EFFECT` (HIGH) |

(Mesma técnica da matriz de acoplamento DEDR §8.2; se o kit DEDR for adotado,
estas regras são REUSE de `ROMANCE_REVEALS_NOTHING`/`ENIGMA_WITHOUT_INTIMATE_COST`.)

---

## 55. Relationship Irreversibility

```yaml
- id: SD-0700
  event: EV-90
  type: IRREVERSIBLE
  pair: CHR-P<->CHR-X
  crossed: BETRAYAL        # BETRAYAL | CHOICE | LOSS | REVELATION | INTIMATE_SHARE | CROSSING   (§16.7: atravessado, traído, escolhido, perdido, revelado, intimamente compartilhado)
  note: "descrição curta do que não pode ser desfeito"
```

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-IRR-01` | final sem ≥1 `IRREVERSIBLE` no par protagonista | `RELATIONSHIP_IRREVERSIBILITY_MISSING` | HIGH (final) |
| `SR-IRR-02` | estado projetado final do par = baseline em todas as dimensões usadas | REUSE `STATE_RESET` → `RELATIONSHIP_RESET` | HIGH |
| `SR-IRR-03` | evento posterior que desfaz o efeito de um `IRREVERSIBLE` (delta que retorna ao valor anterior à marca sem novo evento que o justifique) | `RELATIONSHIP_STATE_CONTRADICTION` (TEST 29) | FAIL |
| `SR-IRR-04` | irreversibilidade confundida com final feliz obrigatório | — (o sistema não exige `UNION`; §16.7) | — |

---

## 56. Evidence Integration

### 56.1 Duas coisas diferentes, dois ids

| Id | O que é | Artefato |
|---|---|---|
| `EVD-*` | **leitura possível** de um observável, com suporte por interpretação | canon interpretativo (REUSE) |
| `ITM-*` | **objeto físico/documental** do mundo, com custódia | `SEM_ROSTO_STATE_DELTAS.yaml` (mínimo) |

Um `ITM-*` pode ser portador de vários `EVD-*` (`EVD.anchor` ou
`ledger_event` → evento de descoberta do item).

### 56.2 Referência mínima (§50 do prompt; o REDMUR X-FILES completo é SDD futuro)

```yaml
items:
  - id: ITM-017
    type: DOCUMENT                   # DOCUMENT | PHOTO_CENSORED | OBJECT | COFFER_PART | TATTOO_RECORD | MAP | RECORDING | OTHER
    origin: {event: EV-*|null, date: CHRONO-*|null, creator: CHR-*|ENT-*|UNKNOWN}
    archive_type: PAPER
    authenticity: UNKNOWN            # AUTHENTIC | FORGED | ALTERED | UNKNOWN (engine-only quando decidido)
    tampering_status: UNKNOWN
    facial_evidence_class: NONE      # NONE | NON_RECONSTRUCTIBLE | PARTIALLY_FACIAL | SEALED (SFE-*) | UNAUTHORIZED_RECORD
    reconstructibility: NON_RECONSTRUCTIBLE
    external_lawful: null            # só para registros externos (seção 26)
    custody:                         # contínua; cada troca é um EV-*
      - {holder: CHR-*|ENT-*|RM-*, from_event: EV-*}
    related: {crime: CRIME-B1|null, mysteries: [MYS-*]}
    # PROJETADOS: reader_seen, characters_seen, chain_of_custody_valid
```

Regras: `SR-PV-03` (proveniência), `SR-FP-02` (deus ex document), `SR-SFE-*`
(facial), `SR-EVI-01 CUSTODY_GAP` (HIGH: item usado por quem não tinha
custódia nem acesso), `SR-EVI-02 ITEM_INVENTED` (BLOCKER: item citado sem
existir; se necessário → proposta).

---

## 57. Cartography Integration

Nada espacial é duplicado. O Story Canon System **consome** a cartografia:

| Necessidade | Consumo | Estado |
|---|---|---|
| ids de lugar | `RM-*` em staging, itens, entidades (`map_refs`) | disponível |
| pack espacial por cena | `cartography_runtime.py --runtime . --pack --chapter N [--scene SC]` embutido no pack narrativo (seção 60) | disponível (cartografia S5, §36.7) |
| validar lugar, rota, distância, tempo, acesso, rotas ocultas/conhecidas, visibilidade, fuga, subsolo | validador de caminho da cartografia (TR-*, AC-*, KN-*, CH-*) chamado no pipeline (seção 65, passo 7) | S2–S5 da cartografia |
| conhecimento espacial de personagem | tokens `CART:*` no mesmo `knowledge_delta` (REUSE) | disponível |
| mapa do leitor | `SEEN_ON_MAP` no cap. 0 (mapas impressos) | disponível |
| lugares exigidos pelo dossiê e ausentes dos mapas | `UNK-SR-*-LOCATION` + `CART_DECISION` (D-SR-05, D-SR-06) | decisão humana |
| mistérios cartográficos com verdade | `truth_ref` da cartografia aponta `UNK-*`/`GT-*` deste sistema (contrato §22.4) | integração S5 |

Contrato em sentido inverso (este SDD promete à cartografia): ids de
personagem e instituição (`CHR-*`, `INST-OCP`, `INST-CONSTABULARY`,
`FAM-MANFRED`…); eventos que causam mudança física (`EV-*` como `cause` de
`CMUT-*`); verdades com controle de revelação (`GT-*` + `reader_access`);
incógnitas (`UNK-SR-*`); nunca contradizer o impresso (cartografia §22.6,
item 4). `SR-CART-01 CARTOGRAPHIC_CONTRADICTION` (FAIL) e `SR-CART-02
IMPOSSIBLE_TRAVEL` (FAIL) são **reexportações** dos achados da cartografia no
relatório narrativo — não reimplementações. Túnel/passagem nova na prosa
(TEST 26) é REUSE da invariante INV 09 da cartografia.

---

## 58. Temporal Canon

Dois eixos, nunca misturados (REUSE da regra da cartografia §24.1):

| Eixo | Campos | Uso |
|---|---|---|
| **Histórico** (ano do mundo) | `temporal.valid_from`, `valid_until`, `historical_period` em `CR-*`, `CHRONO-*`, `ITM-*.origin.date` | Missing Forty Years, sistemas antigos de cofre, história Manfred, Selka, Preservation Act, evolução institucional, protocolos infantis |
| **Narrativo** (capítulo/cena) | `known_since` = primeiro `knowledge_delta` (projeção por conhecedor); `revealed_since` = primeiro `knowledge_delta` de `READER` (projeção) | conhecimento, leitor, estado dinâmico |

`known_since`/`revealed_since` **nunca** são escritos à mão — são projeções,
portanto não divergem. `historical_period` usa vocabulário
`PRESENT · BLACK_INTERVAL · BEFORE_INTERVAL · AFTER_INTERVAL · UNKNOWN`; um
registro não pode afirmar `BLACK_INTERVAL` como época de um fato sem fonte
(`SR-TMP-01 PERIOD_ASSIGNED_WITHOUT_SOURCE`, HIGH), porque situar um fato no
intervalo já é uma afirmação sobre ele. `SR-TMP-02
HISTORICAL_OVERRIDES_PRESENT` (BLOCKER): REUSE `CN-04` da cartografia.

---

## 59. Dynamic Story State

### 59.1 Estático × dinâmico

| `STATIC_CANON` (regras do mundo) | `DYNAMIC_STORY_STATE` (o que muda na história) |
|---|---|
| `SEM_ROSTO_CANON.yaml`, registry, grafo físico da cartografia no seed, interpretativo (perguntas) | ledger (eventos, conhecimento, relação, consentimento) + cartografia (staging, mutações espaciais) + `SEM_ROSTO_STATE_DELTAS.yaml` + evidência `REALIZED` |
| muda só por decisão humana (patch/proposta) | muda por evento `REALIZED` promovido pelo `CANON_GUARDIAN` |

### 59.2 `SEM_ROSTO_STATE_DELTAS.yaml` — tipos

`KNOWLEDGE_PROVENANCE` · `FACE_EVENT` · `COFFER_STATE` (fitting, service,
breach, remoção, troca, roubo, reparo) · `COFFER_TOUCH` · `CONSENT_GRANT` /
`CONSENT_REVOKE` · `CIVIC_TRANSITION` · `RECOGNITION` · `ITEM_CUSTODY` ·
`ANOMALY` · `IRREVERSIBLE` · `INJURY` (ferimento com efeito continuado) ·
`PULL_FACTORS`. Toda linha: `id`, `event` (`EV-*`), `status`
(`PLANNED | REALIZED`), `chapter`, `scene`.

Estado atual = `fold(baseline_da_obra, SD-* REALIZED até N)` — nunca escrito.
Linha `REALIZED` é imutável contra snapshot (REUSE INV-10; correção = nova
linha + `mutation_log`).

### 59.3 Quem está onde

`presence` é da cartografia (`STG-*`). Este sistema não repete lugar; lê.

---

## 60. Canon Context Pack

### 60.1 Princípio

`MINIMUM SUFFICIENT CANON CONTEXT`: maximizar relevância, clareza e restrição
correta; minimizar ruído, lore irrelevante e exposição acidental de spoiler.
O writer **nunca** recebe o dossiê nem o canon inteiro.

### 60.2 Entrada: o plano de cena (sidecar do brief)

```yaml
# briefs/chapters/CHAPTER_07_SCENES.yaml   (SCENE_ARCHITECT em T107_BRIEF_CHAPTER)
scenes:
  - id: SC-07-02
    chapter: 7
    pov: CHR-P
    participants: [CHR-P, CHR-X]
    staging: [STG-0071, STG-0072]         # lugar e hora vêm da cartografia
    events: [EV-44]                       # eventos PLANNED do ledger realizados nesta cena
    evidence: [EVD-12]                    # evidência que a cena planta
    intends:                              # o que a cena QUER fazer (checado pelo gate antes de escrever)
      reveals: [{knower: READER, token: CR-P1-02}]
      face_events: [SD-0200]
      touches: [SD-0405]
      grants: [SD-0404]
      civic: []
    topics: [MYS-SELKA]                   # mistérios que a cena toca (mesmo sem revelar)
```

### 60.3 Algoritmo de recorte (determinístico)

```text
relevant_records =
    locks SERIES e do livro                                        (sempre; forma curta)
  ∪ CR-* cujo domain ∈ domínios ativados pela cena
       (FACE se há FACE_EVENT ou participante com cofre; COFFER se toque/cofre; AGE se participante < 18 ou null;
        CHILD_PROTOCOL se contexto pediátrico; VISITOR/RETURNER se participante não-RESIDENT; JURISDICTION se
        INST-* participa; SELKA/MANFRED/NON_HUMAN se topics/participants/evidência os citam …)
  ∪ CR-* citados por events/evidence/SD da cena
  ∪ MYS-* em topics  → só pergunta, teto do livro, allowed/forbidden (nunca unknown_refs em texto)
  − tudo com scope.reader/character que o POV não pode conhecer (vira 'cannot_know_yet' por id, sem conteúdo)
character_knowledge = knowledge(pov, N-1) ∩ tokens relevantes           (seção 17)
reader_knowledge    = knowledge(READER, N-1) ∩ tokens relevantes        (seção 18)
disclosure          = MYSTERY_DISCLOSURE_GATE(intends.reveals)          (seção 21)
cartography         = check_cartography --pack (embutido)               (seção 57)
state               = fold(SD) restrito aos participantes e cofres/combinações da cena
```

Orçamento: o pack traz **ids + enunciado curto** (o `statement` do
registro), nunca a prosa do dossiê. Meta de tamanho (hipótese de
calibração): ≤ 1.500 palavras por cena; acima disso, `PACK_OVERSIZE` (LOW)
indica recorte frouxo.

### 60.4 Saída (campos pedidos)

```yaml
# briefs/canon/CH_07_SC-07-02_PACK.yaml   (validado por CANON_CONTEXT_PACK.schema.json)
scene_id: SC-07-02
book: B1
chapter: 7
pov_character: CHR-P
current_location: {id: RM-CEN-CHP, from: cartography}
time: {at: "D014T23:14", from: cartography}
characters_present: [CHR-P, CHR-X]
relevant_world_rules: [{id: CR-P1-02, statement: "..."}, {id: CR-R8-01, statement: "..."}]
character_knowledge: {knows: [...], believes: [...], suspects: [...], cannot_know_yet: [ids]}
reader_knowledge: {knows: [...], reader_knows_but_pov_does_not: [...]}
relationship_state: {pair: CHR-P->CHR-X, dims: {trust: TESTED, desire: ACTIVE}}
consent_state: {active_grants: [SD-0404], revoked: [], invalid: []}
coffer_states: [{coffer: COF-0003, state: FITTED}]
combination_states: [{combination: CMB-0003, pov_level: NONE, reader_knows: false}]
facial_rules: {reader_visibility_max: NON_RECONSTRUCTIBLE, face_fragments_published: {CHR-X: []}}
adult_semantics: ENABLED
local_institution_rules: [{id: CR-P5-OCP-01, statement: "..."}]
active_mysteries: [{id: MYS-SELKA, b1_ceiling: THEORY, allowed: [...], forbidden: [...]}]
allowed_clues: [EVD-12]
disclosure: [{token: CR-P1-02, knower: READER, result: ALLOW}]
forbidden_reveals: [{id: MYS-SELKA, what: [FIND_GRAVE, RESOLVE_DEATH], lock: BG1-F-SELKA}]
historical_locks: [BG1-F-40Y, BG1-F-TRUE-CHRONOLOGY]
cartography_context: {…pack cartográfico embutido…}
continuity_notes: ["..."]
required_callbacks: [PRM-0004]        # promessas ao leitor que esta cena deve alimentar
hard_locks: [HL-04, HL-06, HL-07, HL-11]
prohibited_assumptions: [PRO-SR-SELKA-GHOST, PRO-SR-CHILD-SUBSTITUTION-FACT]
engine_notes: null                    # só com --engine-view (CANON_GUARDIAN / LEAD_NOVELIST autorizado)
```

A forma renderizada para o escritor — **Scene Generation Contract** (§77 do
prompt: YOU MAY USE / YOU MAY IMPLY / YOU MAY NOT REVEAL / …) — está no
Apêndice B e é gerada do mesmo YAML.

### 60.5 Regras do pack

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-CTX-01` | pack contém conteúdo de `UNK-*`, tese de `NEVER`, GT sem `reader_access` e sem `--engine-view` | `PACK_SPOILER_LEAK` | BLOCKER |
| `SR-CTX-02` | pack sem `hard_locks` ou `adult_semantics` | `PACK_INCOMPLETE` | HIGH |
| `SR-CTX-03` | pack desatualizado (hash do canon ≠ `source_hash` do pack) | `PACK_STALE` | HIGH |
| `SR-CTX-04` | pack acima do orçamento | `PACK_OVERSIZE` | LOW |

---

## 61. Role-Based Canon Access

### 61.1 Níveis (§45, §69 do prompt)

| Nível | Contém | Não contém |
|---|---|---|
| `PUBLIC_CANON` | o que um leitor de marketing pode saber: premissa pública, regras que a página 1 ensina | qualquer mistério além da pergunta |
| `BOOK_SAFE_CANON` | todos os `CR-*`/`CAP-*`/`ENT-*`/`UNK-*` (só id + "desconhecido") com `scope.book` ≤ livro; gates do livro | `GT-*` engine-only; reservas de livros futuros |
| `SCENE_SAFE_CANON` | o pack da cena (seção 60) | tudo que o POV não pode conhecer, exceto como id em `cannot_know_yet` |
| `MYSTERY_PRIVILEGED_CANON` | + solução do crime do livro (GT engine-only), crenças com `truth`, red herrings com `points_toward` | reservas de livros futuros sem decisão humana |
| `FULL_TRUTH_CANON` | + qualquer verdade reservada **que a autora tenha decidido** para livro futuro | (hoje: praticamente vazio, por DP-03) |

### 61.2 Papéis reais do motor

| Papel pedido | Agente(s) do motor | Nível | Como é aplicado |
|---|---|---|---|
| DIRECTOR | `MASTER_ORCHESTRATOR`, `EXECUTIVE_EDITOR` | `MYSTERY_PRIVILEGED` | inputs declarados da tarefa |
| WORLD ARCHITECT | `WORLD_ARCHITECT` | `BOOK_SAFE` + dossiê (leitura humana-assistida em T012) | `inputs` de T012 |
| STORY PLANNER | `NARRATIVE_ARCHITECT`, `PLOT_ENGINEER` | `MYSTERY_PRIVILEGED` (precisam da solução do crime para planejar pistas) | T016 |
| MYSTERY ARCHITECT | `PLOT_ENGINEER` + `REDMUR_CANON_WARDEN` (+ `DEDR_EXPERT` se adotado) | `MYSTERY_PRIVILEGED` | T016/T019 |
| SCENE PLANNER | `SCENE_ARCHITECT` | `BOOK_SAFE` + solução do crime **só** como "o que plantar" (observável), nunca a tese | T1NN |
| WRITER | `CHAPTER_WRITER`, `LEAD_NOVELIST` | `SCENE_SAFE` (+ brief) | T2NN_WRITE lê pack, não o canon inteiro |
| NARRATIVE REVIEWER | revisores de wave, `SUBTEXT_EDITOR`, `PHYSICALITY_AND_BODY_AGENT` | `SCENE_SAFE` + relatório do validador | T2NN_REVIEW |
| CANON GUARDIAN | `CANON_GUARDIAN`, `REDMUR_CANON_WARDEN` | `FULL_TRUTH` (validação) | T018S, T2NN_CANON_UPDATE |
| MEDIA AGENTS | `VISUAL_DIRECTOR`, `CHAPTER_IMAGE_DIRECTOR`, `IMAGE_GENERATOR`, mídia | `VISUAL_SAFE` = `PUBLIC_CANON` + `HL-04`/`HL-06`/`HL-19` como restrições de imagem; **nunca** rosto, nunca reserva | inputs + canon visual |

Isolamento é **por declaração de inputs**, como em todo o motor (LTE R-07):
um subagente tecnicamente consegue ler o repositório. A defesa real é tripla:
(1) reservas não decididas não existem em arquivo (DP-03); (2) o que existe
engine-only mora no ledger/`--engine-view`, fora dos packs; (3) canário de
vazamento (seção 75.2).

---

## 62. No Canon Invention Gate

### 62.1 Regra

```text
IF required_fact NOT IN canon:
    DO NOT INVENT
    classify: CANON_UNKNOWN | CANON_GAP | CANON_PROPOSAL_REQUIRED | NARRATIVE_WORKAROUND_AVAILABLE
```

| Classe | Quando | O escritor pode continuar? |
|---|---|---|
| `CANON_UNKNOWN` | o fato é um `UNK-*` | só sem o fato (a cena trata a lacuna como lacuna) |
| `CANON_GAP` | o dossiê não fala; não é incógnita deliberada; não é necessário para a história | sim, se a cena não afirmar nada (ex.: não nomear quem tem a chave) |
| `CANON_PROPOSAL_REQUIRED` | a cena **precisa** do fato | não: abre `CP-SR-*`, cena volta ao plano |
| `NARRATIVE_WORKAROUND_AVAILABLE` | há alternativa que não cria canon | sim, pelo workaround (listado no pack) |

Exemplo do prompt ("Quem possui a chave?"): se nunca foi definido, o pack
diz `CANON_GAP: posse da chave de X` e o workaround `"a cena pode mostrar a
fechadura trancada e alguém que não tem a chave; não pode nomear quem a
tem"` — ou, se o enredo depende disso, `CANON_PROPOSAL_REQUIRED`.

### 62.2 Detecção

| Sinal | Mecanismo | Achado |
|---|---|---|
| nome próprio recorrente sem canon | REUSE `check_canon_continuity.py` (vocabulário ampliado com ids/aliases da obra e da cartografia) | `IMPROVISED_CANON` |
| pós-cena com `NEW_FACTS` que não resolvem para id | `POST_SCENE_REPORT` (seção 65) | `IMPROVISED_CANON` → proposta |
| referência a `CAP-*` como instância | `SR-ST-04` | `SYSTEM_CAPABILITY_AS_INSTANCE` |
| lugar/passagem nova | REUSE cartografia INV 09 | `CARTOGRAPHIC_CONTRADICTION` |
| evento cuja `facts` afirma conteúdo de `UNK-*` | casamento por `PRO-*.match` + Warden | `UNKNOWN_AS_FACT` |

TEST 27: cena que exige fato indefinido → `CANON_PROPOSAL_REQUIRED`.

---

## 63. Canon Proposal Workflow

### 63.1 Duas vias (padrão cartografia D-CART-07)

| Tipo | Via |
|---|---|
| **Planejamento** (antes do cap. 1): protagonistas, crime, lugares exigidos pelo dossiê sem mapa, valores de combinação, versões de rumor | `books/sem-rosto/canon/approvals/CANON_DECISION_<n>.md` com `subject_sha256` do seed afetado |
| **Nascida na escrita** | `canon/CANON_PROPOSALS/` com a entrada do schema do motor (inalterado) **+** sidecar `CP-SR-<n>.yaml` com o mesmo `proposal_id` |

### 63.2 Sidecar

```yaml
proposal_id: CP-SR-0012
need: "A cena SC-12-03 precisa saber quem guardou o documento ITM-017 entre os caps. 4 e 12."
requested_fact: "descrição neutra do fato pedido"
reason: "por que a história precisa, e por que um workaround não serve"
affected: {modules: [ARCHIVE], characters: [CHR-*], mysteries: [MYS-*], books: [B1]}
contradiction_risk: [{against: CR-*|HL-*|BG1-*, why: "..."}]
alternatives:
  - {id: ALT-1, summary: "…", creates_canon: false}      # workaround
  - {id: ALT-2, summary: "…", creates_canon: true}
recommended_minimal_solution: ALT-1
requires_human_approval: true                             # sempre true para estrutural
status: PENDING_HUMAN_DECISION
decided_by: null                                          # HUMAN_GATE_OWNER; nunca agente para estrutural
```

- Nenhum agente autoaprova mudança estrutural (`SR-CP-01
  SELF_APPROVED_STRUCTURAL_CANON`, BLOCKER). Estrutural = toca `HL-*`,
  `BG*`, `MYS-*`, `UNK-*`, `CAP-*`→instância, entidade nova recorrente,
  personagem maior, crime.
- Não estrutural (ex.: nome de uma rua sem função no mapa? **não**, isso é
  cartografia; ex.: cor do casaco de um figurante) pode ser aceito pelo
  `CANON_GUARDIAN` (REUSE do protocolo), registrado em `mutation_log`.

---

## 64. Canon Mutation

| Tipo | Significado | Via | Exemplo |
|---|---|---|---|
| `DISCOVERED_CANON` | canon que já existia é mostrado | evento `REALIZED` + `knowledge_delta` | o leitor descobre uma regra do Preservation Act já registrada |
| `NEW_CANON` | fato novo | proposta aprovada | a autora define o crime |
| `STORY_STATE_CHANGE` / `WORLD_STATE_CHANGE` | estado muda por evento | `SD-*` / `CMUT-*` (cartografia) | ponte destruída no cap. 20; cofre arrombado |
| `CLARIFICATION` | detalhe compatível que especifica sem mudar | proposta não estrutural | acabamento de um cofre |
| `PATCH` | correção de canon aprovado no escopo | R12+ humano | — |
| `SUPERSESSION` | substituição declarada | `supersedes`/`superseded_by` | — |
| `RETCON` | reescrever o que o leitor já viu | **altamente restrito**: só humano, com `mutation_log`, e nunca sobre evento `REALIZED` sem nova entrada | — |

Regras: `SR-MUT-01 RETCON_BY_CONVENIENCE` (BLOCKER: mudança em evento
`REALIZED`/`SD` realizado sem mutation_log — REUSE INV-10);
`SR-MUT-02 STATE_CHANGE_AS_CANON_CONTRADICTION` (INFO: o validador reconhece
que mudança de estado causada por evento **não** é contradição — TEST 28);
`SR-MUT-03 STATIC_CANON_EDITED_BY_STORY` (BLOCKER: capítulo altera
`SEM_ROSTO_CANON.yaml` sem proposta).

---

## 65. Validation Pipeline

### 65.1 Ordem (§56 do prompt), mapeada para famílias do validador

```text
SCENE DRAFT (+ POST_SCENE_REPORT)
 1. CANON VALIDATOR              SR-CR, SR-ST, SR-PV, SR-GAP     (status, proveniência, invenção)
 2. KNOWLEDGE VALIDATOR          SR-KN, SR-RD  + ledger INV-12/13
 3. FACE FIREWALL                SR-FACE, SR-FRC, SR-SFE, SR-EXT, R8
 4. AGE / CONSENT FIREWALL       SR-AGE, SR-CNS, SR-TCH, SR-CMB  + ledger INV-06..09 + RI HB-01/02
 5. MYSTERY DISCLOSURE GATE      SR-MYS + gate (seção 21) + SR-SEL, SR-MAN, SR-NH, SR-RUM
 6. TIMELINE VALIDATOR           SR-CHR, SR-40Y, SR-TMP
 7. CARTOGRAPHY VALIDATOR        check_cartography (TR/AC/KN/CH) reexportado como SR-CART
 8. RELATIONSHIP STATE VALIDATOR SR-IRR, acoplamento crime↔romance + ledger L3/INV-04
 9. BOOK SCOPE VALIDATOR         SR-B1 / SR-BF (gates), SR-HL (locks), SR-CRM, SR-FP, SR-DE
OUTPUT → verdict + findings
```

Os passos rodam **todos** (não param no primeiro erro): o relatório precisa
listar tudo que a cena quebra.

### 65.2 Veredito

| Veredito | Regra |
|---|---|
| `FAIL` | ≥1 achado `BLOCKER` ou `HIGH` estrutural, ou achado lexical confirmado pelo Warden |
| `CANON_PROPOSAL_REQUIRED` | nenhum FAIL; ≥1 achado da classe proposta |
| `PASS_WITH_WARNINGS` | só `MEDIUM`/`LOW`/`WARNING` lexical pendente de Warden |
| `PASS` | nada |

Cada achado cita `canon_id`/`HL-*`/`BG1-*` **e** a seção do dossiê (`source.location`).

### 65.3 Pós-cena (§78 do prompt)

O escritor entrega, com a cena, `canon/CANON_PROPOSALS/CH_NN_<SC>_POST_SCENE.yaml`
(`POST_SCENE_REPORT.schema.json`):

```yaml
scene_id: SC-07-02
new_facts: []                 # cada um: {statement, needs: id|CANON_PROPOSAL}
new_knowledge: [{knower: CHR-P, token: "...", source: "..."}]
new_suspicions: []
new_rumors: []
new_evidence: [{carrier: ITM-*|TEXT, observable: "..."}]
new_relationship_state: [{pair: ..., dimension: ..., from: ..., to: ...}]
new_world_state: [{type: FACE_EVENT|COFFER_STATE|..., ...}]
new_reader_knowledge: [{token: "...", via: "..."}]
potential_canon_proposals: [CP-SR-*]
self_reported_violations: []
```

O `CANON_GUARDIAN` promove **apenas o autorizado**: cada linha vira evento
`REALIZED`/`SD` `REALIZED`/evidência `REALIZED`, ou é rejeitada, ou vira
proposta. O validador compara o relatório com o que foi promovido
(`SR-PS-01 POST_SCENE_UNRECONCILED`, MEDIUM, para linhas sem destino).

### 65.4 Onde cada modo roda

| Momento | Modo | Bloqueia? |
|---|---|---|
| antes de escrever (pack) | `--pack` + gate de revelação sobre `intends` | o pack já traz `BLOCK`/`CANON_PROPOSAL_REQUIRED`; o escritor não deveria começar |
| logo depois de escrever | `--mode scene` | não (pré-filtro para o escritor/revisor) |
| fim de wave | `--mode wave` em `GATE_WAVE_n` | sim |
| fim do livro | `--mode final` em `GATE_FULL_MANUSCRIPT` | sim (+ checkpoint humano) |

---

## 66. Error Taxonomy

Severidades do motor (`INFO < LOW < MEDIUM < HIGH < BLOCKER`); "FAIL" =
`HIGH`/`BLOCKER`. Detector: **S** estrutural · **L** pré-filtro lexical (→
Warden) · **J** julgamento.

| Código | Sev. | Det. | Regra(s) | Fonte |
|---|---|---|---|---|
| `FACE_REVEAL_VIOLATION` | BLOCKER | S+L+J | SR-FACE-01/05/06 | §1.4 |
| `FACIAL_RECONSTRUCTIBILITY_VIOLATION` | BLOCKER | S+J | SR-FACE-02, SR-FRC-02 | §3.4 (R9) |
| `SELF_FACE_VIOLATION` | HIGH | S+L | seção 24 | §3.7 (R8) |
| `MINOR_EROTIC_SEMANTIC_VIOLATION` | BLOCKER | S+L+J | SR-AGE-01..05 | §4.8, §15.5 (R11) |
| `CONSENT_INFERENCE_VIOLATION` | BLOCKER | S+J | SR-CNS-01/02, SR-TCH-01, SR-CMB-02 | §15.4–15.5 |
| `UNKNOWN_AS_FACT` | BLOCKER | S+J | SR-ST-01, SR-40Y-04, SR-CPR-01 | §17 |
| `SYSTEM_CAPABILITY_AS_INSTANCE` | BLOCKER | S | SR-ST-04, SR-FRC-01, SR-ECO-02, SR-TAT-04 | §0, §23 |
| `PREMATURE_MYSTERY_REVEAL` / `PREMATURE_RESOLUTION` | BLOCKER | S | SR-KN-03, SR-MYS-01 | §12.4, §16.8, §18 |
| `CHARACTER_KNOWLEDGE_LEAK` | HIGH | S | SR-KN-01, SR-CMB-05 | §21 (9) |
| `READER_KNOWLEDGE_LEAK` | HIGH/BLOCKER | S | SR-RD-01/02 | §21 (9) |
| `BOOK1_HISTORY_LOCK_VIOLATION` | BLOCKER | S | SR-40Y-02, SR-SEL-01, SR-PUL-04, SR-DA-02 | §12.4, §14.9 |
| `TRUE_CHRONOLOGY_LEAK` | BLOCKER | S+J | SR-CHR-01, SR-DE-02 | §12 |
| `MANFRED_UNIVERSAL_CAUSALITY` | HIGH | S+L+J | SR-MAN-01/02 | §13.3 |
| `SUPERNATURAL_CONFIRMATION` | BLOCKER | S+L+J | SR-NH-03, SR-PUL-02, HL-01 | §1.3 |
| `MAGICAL_CAUSALITY` | BLOCKER | S | HL-02, SR-PUL-01 | §1.3 |
| `SELKA_ONTOLOGY_LEAK` | BLOCKER | S+L | SR-SEL-03 | §14.8 |
| `SELKA_AS_THE_KEY` | BLOCKER | S | SR-SEL-02 | §14.9 |
| `IMPROVISED_CANON` | BLOCKER | S | SR-PV-05, SR-GAP, SR-MAN-06, SR-CMB-07 | §17, §19, §25 |
| `CARTOGRAPHIC_CONTRADICTION` | HIGH | S | SR-CART-01 (REUSE) | §19 |
| `IMPOSSIBLE_TRAVEL` | HIGH | S | SR-CART-02 (REUSE) | §19 |
| `RELATIONSHIP_STATE_CONTRADICTION` | HIGH | S | SR-IRR-03 | §16.7 |
| `EVIDENCE_WITHOUT_PROVENANCE` | HIGH | S | SR-PV-03 | §16.4 |
| `DEUS_EX_DOCUMENT` | BLOCKER | S | SR-FP-02 | §16.4 |
| `COMBINATION_AS_REMOVAL_AUTHORITY` | BLOCKER | S | SR-CMB-01 | §2.7 (R1) |
| `PHYSICAL_RETURN_AS_REACTIVATION` | BLOCKER | S | SR-CIV-01 | §6.2 (R2) |
| `EXTRATERRITORIAL_POWER` / `SOVEREIGNTY_ASSUMED` | BLOCKER | S+J | SR-JUR-02/03 | §4.7 (R3), §7 |
| `SEALED_EVIDENCE_PUBLIC` / `FACIAL_AUTHORITY_UNBOUNDED` | BLOCKER | S | SR-SFE-02/03 | §3.5 (R6) |
| `EXTERNAL_PURGE_ASSUMED` | HIGH | S | seção 26 | §3.6 (R7) |
| `TATTOO_NUMERIC_COMBINATION` | BLOCKER | S+L | SR-TAT-01 | §10.3 |
| `TECHNOLOGY_CREEP` / `FORBIDDEN_TECHNOLOGY_PRESENT` | HIGH/BLOCKER | S+J | SR-TEC-01/02 | §9 |
| `RUMOR_AS_WORLD_TRUTH` | HIGH | S+J | SR-RUM-01 | §18, §23 |
| `VILLAIN_EXPLAINS_REDMUR` | BLOCKER | S+J | SR-CRM-04 | §16.6 |
| `CRIME_GENERIC` / `CRIME_UNRESOLVED` / `UNSEEDED_REVEAL` / `DOUBLE_EDGE_MISSING` | HIGH | S | seções 51–53 | §16 |
| `RELATIONSHIP_IRREVERSIBILITY_MISSING` / `RELATIONSHIP_RESET` | HIGH | S | seção 55 | §16.7 |
| `PACK_SPOILER_LEAK` | BLOCKER | S | SR-CTX-01 | — |
| `HARD_LOCK_VIOLATION` / `HARD_LOCK_EDIT` | BLOCKER | S | SR-HL-01/02 | §22, §27 |
| `SOURCE_HASH_MISMATCH` | BLOCKER | S | SR-SRC-01 | §27 |
| `CANON_PROPOSAL_REQUIRED` | — | S | seção 62 | §17, §23 |

Achados `L` sozinhos são `WARNING` (Markdown) e entram no JSON como
`severity: MEDIUM, detector: LEXICAL, requires_judgment: true`. Eles
**não** bloqueiam gate até o Warden confirmar em `REVIEW_FINDING`
(`BLOCKER`, citando o código) — só então bloqueiam. Isso evita bloquear
literatura por palavra, e evita deixar passar um rosto por "o validador não
entende prosa".

---

## 67. Chapter Snapshot

`T2NNS_CHAPTER_SNAPSHOTS` (tool, zero token) gera um arquivo por capítulo da
wave depois do `CANON_UPDATE`:

```yaml
# canon/snapshots/SEM_ROSTO.CH_07.yaml   (gerado; nunca editado)
chapter: 7
source_hashes: {canon: sha, ledger: sha, interpretive: sha, state_deltas: sha, cartography: sha}
world_state: {mutations_applied: [CMUT-*], system_stable: true}
character_states: {CHR-P: {civic: {...}, injuries: [...], coffer: COF-0001}}
knowledge_states: {CHR-P: [...], CHR-X: [...]}
relationship_states: {CHR-P->CHR-X: {...}}
mystery_states: {MYS-SELKA: OPEN, MYS-FORTY-YEARS: EXPANDING}
crime_state: {Q-CRIME-B1: {viable: [...], leader: ...}}      # engine view; não entra em pack
evidence_state: {ITM-017: {holder: CHR-P}}
location_state: {CHR-P: RM-CEN-CHP}                           # da cartografia
coffer_state: {COF-0003: FITTED}
combination_state: {CMB-0003: {knowers: {CHR-P: PARTIAL}}}
reader_state: {facts: n, rumors: n, clues: n, faces_seen: 0}
open_promises: [PRM-0004]
new_unknowns: []                                              # UNK surgidos por proposta aprovada
```

Uso: o pack do capítulo N+1 parte do snapshot N (sem recalcular do zero);
o modo `wave --baseline` compara snapshots para detectar retcon
(`SR-MUT-01`). É projeção: se diverge da recomputação,
`SNAPSHOT_DRIFT` (HIGH) e o snapshot é regenerado — nunca corrigido à mão.

---

## 68. Reader Promise Ledger

A única parte do "leitor" que **precisa** ser armazenada: perguntas que o
texto promete implicitamente.

```yaml
# canon/READER_PROMISES.yaml
promises:
  - id: PRM-0004
    question: "pergunta neutra que o leitor passa a fazer"
    introduced_at: {chapter: 3, scene: SC-03-01, evidence: [EVD-05]}
    importance: MAJOR               # MINOR | MAJOR | FOUNDATIONAL
    expected_scope: B1              # B1 | SERIES | NEVER (ambiguidade deliberada)
    mystery: MYS-*|Q-*|null
    resolved: false
    resolution: {book: null, event: null}
    associated_clues: [EVD-05, EVD-11]
    density_class: CLUE             # seção 68.2
```

### 68.1 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-PRM-01` | promessa `expected_scope: B1` não resolvida no final | `PROMISE_ABANDONED` | HIGH |
| `SR-PRM-02` | promessa ligada a `MYS-*` reservado com `expected_scope: B1` | `PROMISE_EXCEEDS_GATE` | BLOCKER |
| `SR-PRM-03` | promessa sem alimentação (nenhuma evidência) por > N capítulos (hipótese: 6, REUSE `max_loop_silence`) | `PROMISE_FORGOTTEN` | MEDIUM |
| `SR-PRM-04` | evidência `CLUE` `NOTICEABLE` sem promessa nem `Q-*` | `ACCIDENTAL_MYSTERY` | LOW |

### 68.2 Mystery Density Control (§61 do prompt)

Todo detalhe marcado no plano recebe **uma** classe: `BACKGROUND · COLOR ·
CLUE · RED_HERRING · MYSTERY_SIGNAL · PAYOFF · RESIDUAL`. Só `CLUE`,
`RED_HERRING`, `MYSTERY_SIGNAL` e `PAYOFF` exigem proveniência e evidência;
`BACKGROUND`/`COLOR` **não** geram payoff e não podem ser cobrados
(`SR-DEN-01 COLOR_PROMOTED_TO_CLUE`, MEDIUM, quando um detalhe de cor vira
pista sem `EVD-*`). Nem toda irregularidade precisa de payoff; toda pista
intencional importante precisa de proveniência. Densidade máxima de sinais
por capítulo: REUSE `EVIDENCE_OVERDENSE` (LTE).

---

## 69. Book 1 Gates

`BOOK_GATES.seed.yaml`, com fonte por linha (dossiê §12.4, §14.9, §16, §21).

### 69.1 `BOOK_1_REQUIRED`

| id | Exigência | Verificação (modo `final`) |
|---|---|---|
| `BG1-R-CRIME` | crime concreto, delimitado, investigável, solucionável, humano | `SR-CRM-01..05` |
| `BG1-R-FAIRPLAY` | ≥3 pistas retroativas; sem documento milagroso | `SR-FP-01/02` |
| `BG1-R-REDMUR-CRIME` | crime depende de ≥2 características de Redmur | `SR-CRM-02` |
| `BG1-R-COUPLING` | crime ↔ romance | seção 54.2 |
| `BG1-R-DOUBLE-EDGE` | evidência final resolve e abre contradição maior | `SR-DE-01` |
| `BG1-R-IRREVERSIBLE` | relação irreversível, não fechada | `SR-IRR-01/02` |
| `BG1-R-LARGER-CONTRADICTION` | Redmur termina maior (≥1 `MYS-*` em `EXPANDING` a partir da evidência final) | seção 53 |
| `BG1-R-REDMUR-REMAINS` | `WORLD_SYSTEM_STABLE = TRUE` | `HL-17` |
| `BG1-R-NO-FACE` | leitor nunca vê rosto | `HL-04`, `HL-28` |
| `BG1-R-STATES-CHANGED` | `CHARACTER/KNOWLEDGE/RELATIONSHIP/INVESTIGATION_STATE_CHANGED = TRUE` | projeção snapshot 0 × final |
| `BG1-R-40Y-REAL` | os quarenta anos existem como problema real | `MYS-FORTY-YEARS.required` |

### 69.2 `BOOK_1_PARTIAL`

The Pull (explicação parcial por subtexto); Selka (até `TEORIA`); Missing
Forty Years (citar, provocar, datas, contradição, símbolos, consequências,
incompatibilidades); Manfred (tentação da hipótese, com alternativas); Four
Archives (contradições entre arquivos); jurisdição (contradições Reino
Unido × Preservation Redmur).

### 69.3 `BOOK_1_FORBIDDEN` (§12.4, §14.9, §16.8)

`BG1-F-TRUE-CHRONOLOGY` · `BG1-F-40Y` · `BG1-F-AQUELE-DIA-CAUSE` ·
`BG1-F-MANFRED-ROLE` · `BG1-F-FLARRY-ROLE` · `BG1-F-LOST-CHILD` ·
`BG1-F-COFFER-ORIGIN` · `BG1-F-SIX-MONTH-ORIGIN` · `BG1-F-ACT-MOTIVE` ·
`BG1-F-SAVINGS-MOTIVE` · `BG1-F-PULL` · `BG1-F-SELKA-GRAVE` ·
`BG1-F-SELKA-DEATH` · `BG1-F-SELKA-COFFER` · `BG1-F-SELKA-TATTOOS-DIRECT` ·
`BG1-F-SELKA-BODY` · `BG1-F-40Y-VIA-SELKA` · `BG1-F-40Y-VIA-EXHUMATION` ·
`BG1-F-MAGIC` · `BG1-F-FACE-REWARD` · `BG1-F-REDMUR-DESTROYED` (destruir a
cidade, abolir os cofres, derrubar todo o sistema, "libertar" Redmur).

### 69.4 `BOOK_1_ALLOWED`

Tudo que não está nas três listas e não viola lock — por padrão. O gate não é
uma lista branca de cenas: é uma lista negra de resoluções mais uma lista de
exigências.

### 69.5 Os 16 gates de escrita do dossiê (§21) → regras

| # dossiê | Regra |
|---|---|
| 1 | `HL-04`, `SR-FACE-*` |
| 2 | seção 27 (`FACELESS_EXPRESSION_SUSPECTED` → Warden) |
| 3 | `HL-01/02`, `SR-NH-03` |
| 4 | seção 29 |
| 5 | `SR-CMB-01` |
| 6 | `SR-CNS-*`, `SR-TCH-01` |
| 7 | seção 33 |
| 8 | seção 57 |
| 9 | seções 17–18 |
| 10 | `SR-ST-04` |
| 11 | `SR-MAN-*` |
| 12 | `SR-SEL-02` |
| 13 | `SR-40Y-02` |
| 14 | `SR-CHR-01` |
| 15 | `BG1-R-CRIME`, `BG1-R-LARGER-CONTRADICTION` |
| 16 | `SR-DE-01/02` |

---

## 70. Future Book Gates

### 70.1 Estrutura (sem decidir o Livro 2)

```yaml
book_gates:
  B1: {…seção 69…}
  B2: {status: UNDEFINED}          # nada é decidido aqui
series:
  structural_locks: [HL-01, HL-02, HL-03, HL-04, HL-20]   # "mesmo em livros futuros" (§22)
  future_domains:                                         # §22 — domínios onde livros futuros PODEM avançar
    - {mystery: MYS-TRUE-CHRONOLOGY, earliest_allowed_reveal: B2, label: P10-B}
    - {mystery: MYS-FORTY-YEARS, earliest_allowed_reveal: FUTURE}
    - {mystery: MYS-FOUR-ARCHIVES, earliest_allowed_reveal: FUTURE}
    - {mystery: MYS-FLARRY, earliest_allowed_reveal: FUTURE}
    - {mystery: MYS-MANFRED-ROLE, earliest_allowed_reveal: FUTURE}
    - {mystery: MYS-LOST-CHILD, earliest_allowed_reveal: FUTURE}
    - {mystery: MYS-SIX-MONTH, earliest_allowed_reveal: FUTURE}
    - {mystery: MYS-SELKA, earliest_allowed_reveal: FUTURE}
    - {mystery: MYS-THE-PULL, earliest_allowed_reveal: FUTURE, full_explanation: NEVER}
    - {mystery: MYS-UK-VS-PRESERVATION, earliest_allowed_reveal: FUTURE}
  never: [MYS-MAP-AUTHOR]
```

`FUTURE` ≠ "será resolvido": "Livro 2 ou etapas futuras podem avançar …, mas
não devem presumir que tudo será resolvido automaticamente" (§22).

### 70.2 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `SR-BF-01` | revelação antes de `earliest_allowed_reveal` | `PREMATURE_RESOLUTION` | BLOCKER |
| `SR-BF-02` | gate de livro futuro preenchido por agente | `SELF_APPROVED_STRUCTURAL_CANON` | BLOCKER |
| `SR-BF-03` | livro futuro altera lock estrutural | `HARD_LOCK_EDIT` (exige revisão formal da franquia) | BLOCKER |

### 70.3 Como uma verdade reservada entra, quando a autora decidir

1. decisão humana registrada (`CANON_DECISION_<n>.md`);
2. `CR-*`/`GT-*` com `scope.reader: GATED`, `reveal.minimum_book: B<n>`,
   `reveal.requires: [...]` — **engine-only** (`MYSTERY_PRIVILEGED`/`FULL_TRUTH`);
3. o `UNK-*` correspondente passa a `SUPERSEDED` **para o livro B<n> em
   diante**, e continua `MUST_REMAIN_UNKNOWN` no canon interpretativo dos
   livros anteriores (snapshots imutáveis);
4. regressão completa (seção 76.4).

---

## 71. Persistence

| Artefato | Local | Formato | Dono | Mutável? |
|---|---|---|---|---|
| dossiê | `books/sem-rosto/canon/sources/` | Markdown pinado | humano | não (nova versão) |
| seeds | `books/sem-rosto/canon/seeds/*.seed.yaml` | YAML | autora + `CANON_GUARDIAN` (proposta) | por approval |
| approvals | `books/sem-rosto/canon/approvals/` | Markdown + `subject_sha256` | **só humano** | não |
| canon materializado | `runtime/sem-rosto/canon/SEM_ROSTO_CANON.yaml` | YAML | `CANON_GUARDIAN` (`CANON_WRITE`) | por tarefa |
| deltas de estado | `runtime/sem-rosto/canon/SEM_ROSTO_STATE_DELTAS.yaml` | YAML | `CANON_GUARDIAN` | append-only para `REALIZED` |
| promessas | `runtime/sem-rosto/canon/READER_PROMISES.yaml` | YAML | `CANON_GUARDIAN` | sim |
| propostas | `runtime/sem-rosto/canon/CANON_PROPOSALS/` | schema do motor + sidecar | qualquer agente propõe | status por humano/guardião |
| plano de cena | `runtime/sem-rosto/briefs/chapters/CHAPTER_NN_SCENES.yaml` | YAML | `SCENE_ARCHITECT` | sim até a escrita |
| packs | `runtime/sem-rosto/briefs/canon/` | YAML + MD | gerado | regenerado |
| snapshots | `runtime/sem-rosto/canon/snapshots/` | YAML | gerado | nunca |
| relatórios | `runtime/sem-rosto/reviews/` | MD + JSON | gerado | regenerado |

Nenhum banco, nenhum serviço. "O repositório é a memória" (`AGENTS.md`).

## 72. Versioning

- **Fonte:** sha256 do dossiê pinado (`SR-SRC-01`); patch = nova fonte com
  `supersedes` e escopo.
- **Seeds:** `metadata.version` semântica; toda mudança com approval humano
  (`subject_sha256` do seed); `mutation_log` por arquivo.
- **Registros:** `revision` + `updated_at` por `CR-*`; `supersedes`/`superseded_by`.
- **Runtime:** `mutation_log` em cada arquivo de canon (padrão ledger/registry);
  snapshots por capítulo e por wave com `source_hashes`.
- **Packs e relatórios:** carregam `source_hash`; pack com hash antigo é
  `PACK_STALE`.
- **Contratos:** templates versionados com o validador; teste
  "campo do template ⇔ campo do validador".

## 73. Observability

"Isto não precisa ser infraestrutura pesada" (§70 do prompt): relatórios dos
validadores + consultas.

| Pergunta | Consulta |
|---|---|
| isto é verdade em SEM ROSTO? | `--is-true "<id|texto>"` |
| quem sabe X no capítulo N? | `--who-knows <token> --at-chapter N` |
| o que o leitor sabe no capítulo N? | `--reader-at N` (visão padrão; `--engine-view` mostra `knowledge_withheld`) |
| por que esta revelação foi bloqueada? | `--why-blocked <token> --scene SC` (cadeia do gate da seção 21) |
| quais locks esta cena aciona? | `--locks --scene SC` |
| estado de um mistério | `--mystery MYS-* [--at-chapter N]` |
| pack da cena | `--pack --chapter N --scene SC` |
| veredito | `--verdict --chapter N --scene SC` (seção 80) |

Registro de eventos de governança: o relatório de cada modo tem um bloco de
contadores — violações de canon, propostas abertas/decididas, revelações
bloqueadas, vazamentos de conhecimento/leitor/mistério, violações de rosto,
divergências de story state, violações cartográficas, tentativas
unknown-as-fact e capability-as-instance. `validate-gate` já grava stdout em
`PROJECT_STATUS.yaml → validator_results` (REUSE); nada novo a operar.

## 74. Failure Modes

| Failure mode | Como aparece | Detecção |
|---|---|---|
| Canon Drift | regra descrita diferente em capítulos | `SR-PRC-01`, `SR-CR-09`, Warden, `WORLD_RULES_REVIEWER` |
| Lore Hallucination | nome, instituição, costume sem fonte | `IMPROVISED_CANON`, `check_canon_continuity` |
| Knowledge Leakage | personagem sabe cedo | `CHARACTER_KNOWLEDGE_LEAK` |
| Reader Leakage | leitor sabe cedo | `READER_KNOWLEDGE_LEAK` |
| Mystery Collapse | teoria única sobra | REUSE `EVIDENCE_COLLAPSES_QUESTION`, `SR-MYS-01` |
| Premature Reveal | reserva resolvida | `PREMATURE_RESOLUTION`, `BOOK1_HISTORY_LOCK_VIOLATION` |
| False Supernatural Confirmation | fantasma real | `SUPERNATURAL_CONFIRMATION` |
| Face Rule Violation | rosto descrito ao leitor | `FACE_REVEAL_VIOLATION` |
| Retcon by Convenience | evento realizado reescrito | `SR-MUT-01` |
| Manfred Omnicausality | "foram os Manfred" | `MANFRED_UNIVERSAL_CAUSALITY` |
| Selka Overcentralization | Selka explica tudo | `SELKA_AS_THE_KEY`, `SELKA_OVERCENTRALIZATION` |
| Technology Creep | IA, scanner facial | `TECHNOLOGY_CREEP`, `FORBIDDEN_TECHNOLOGY_PRESENT` |
| Cartography Drift | túnel novo | REUSE cartografia INV 09 |
| Relationship Reset | casal volta ao início | `RELATIONSHIP_RESET` |
| Crime Deus Ex Machina | prova surge no clímax | `DEUS_EX_DOCUMENT` |
| Consent Collapse | uma camada implica outra | `CONSENT_INFERENCE_VIOLATION` |
| Minor Semantic Leakage | framing adulto migra para criança | `MINOR_EROTIC_SEMANTIC_VIOLATION` |
| System Capability Canonization | "existe uma foto de Selka" | `SYSTEM_CAPABILITY_AS_INSTANCE` |
| **Sistema engole a literatura** | pack enorme, escritor escreve para o validador | orçamento do pack (`PACK_OVERSIZE`); léxico nunca bloqueia sozinho; Regra de Ouro LTE §24.2; checkpoint humano |
| **Falso positivo lexical** | "sorriu" legítimo (POV com acesso facial; metáfora) | lexical = WARNING → Warden decide |
| **Falso negativo semântico** | rosto descrito sem vocabulário de traço | Warden + `SUBTEXT_EDITOR` + checkpoint humano; o validador não promete o que não pode |

## 75. Security / Spoiler Isolation

### 75.1 Camadas de proteção, da mais forte à mais fraca

1. **Não existência**: reservas não decididas não estão em arquivo (DP-03).
2. **Tipos não representáveis**: `reader_visibility: RECONSTRUCTIBLE` e
   campos de resposta não existem nos contratos.
3. **Engine-only por padrão**: GT sem `reader_access` nunca chega ao leitor
   (REUSE INV-12); `--engine-view` explícito para qualquer visão privilegiada.
4. **Recorte por pack**: tarefas de escrita declaram o pack como input, não
   o canon inteiro.
5. **Instrução**: o agente é instruído a não ler além dos inputs (fraca por
   natureza — LTE R-07).

### 75.2 Canário de vazamento

Um `UNK-SR-CANARY` com frase-sentinela **sem significado** (ex.: um termo
inventado sem relação com a obra) vive só no canon engine-only e **nunca** em
pack. Se aparecer em prosa, brief ou pack, `CANARY_LEAK` (BLOCKER): algum
agente leu além do que devia. Mesmo padrão do canário de contaminação do
forum LTE (§19.7). O canário não é canon e é marcado como tal.

### 75.3 Colisão com capabilities faciais do motor

O motor tem `FACE_CANON_TEMPLATE.md`, `facial_identity_expert` e
`face_consistency_required` (identidade facial recorrente em imagens). Para
SEM ROSTO isso **colide** com `HL-04`: o `BOOK_SPEC` da obra deve declarar
`images.face_consistency_required: false`, e a identidade visual recorrente
das ilustrações usa assinatura não facial (cofre, mãos, tatuagens, postura).
`SR-FACE-07 FACE_CANON_CONFLICT` (BLOCKER) reprova o pacote se a feature
estiver ligada. Decisão de pacote, não do motor (OQ-SR-09).

---

## 76. Test Strategy

### 76.1 Convenção

`unittest`, offline, `PYTHONIOENCODING=utf-8`, uma mutação por teste
afirmando a **categoria exata** (padrão `tests/test_causal_ledger.py`,
`tests/test_interpretive_canon.py`, `tests/test_redmur_cartography.py`).
Nenhum teste chama modelo.

### 76.2 Fixtures

- `tests/fixtures/sem_rosto_canon/runtime_redmur_min/` — canon mínimo
  **derivado do dossiê** (não do DEDR §33): ~20 `CR-*`, os 28 `HL-*`, gates do
  Livro 1, 6 `MYS-*`, 3 `RUM/THEORY-*`, 2 `CAP-*`; ledger com dois adultos
  fictícios de fixture (`CHR-FX-A`, `CHR-FX-B`, `age` inteiro) e uma criança
  de fixture (`CHR-FX-C`, `age: 1`); canon interpretativo com `Q-CRIME-FX`
  (`RESOLVED_AT`) e uma pergunta `NEVER`; deltas de estado com um cofre, uma
  combinação, dois grants, um evento facial; cartografia = fixture neutra já
  existente (`tests/fixtures/cartography/`). Nomes de fixture, **não**
  personagens de SEM ROSTO.
- `tests/fixtures/sem_rosto_canon/scenes/` — planos de cena, packs esperados
  e relatórios pós-cena.
- `tests/test_sem_rosto_canon_data.py` — os seeds reais de
  `books/sem-rosto/canon/` passam em `--mode package` (padrão
  `test_redmur_cartography.py`).

### 76.3 Os 30 testes obrigatórios

| # | Cenário (mutação) | Esperado | Categoria afirmada |
|---|---|---|---|
| 01 | `FACE_EVENT` com `reader_visibility` fora do enum / fragmentos `RECONSTRUCTIBLE` publicados | FAIL | `FACE_REVEAL_VIOLATION` / `FACIAL_RECONSTRUCTIBILITY_VIOLATION` |
| 02 | POV em `viewers`, `reader_visibility: NONE`, prosa sem traço facial | PASS | — |
| 03 | evento `facts` casa `PRO-*` de um `UNK-*` | FAIL | `UNKNOWN_AS_FACT` |
| 04 | cena cita `SFE-*` inexistente como "a foto de X" | FAIL | `SYSTEM_CAPABILITY_AS_INSTANCE` |
| 05 | `acts_on_knowledge` com token não aprendido | FAIL | `CHARACTER_KNOWLEDGE_LEAK` |
| 06 | evidência `source: NARRATOR` afirma conteúdo de `RUM-*` | FAIL | `RUMOR_AS_WORLD_TRUTH` |
| 07a | `FAM-MANFRED` como `actor` | FAIL | `MANFRED_UNIVERSAL_CAUSALITY` |
| 07b | "os Manfred" em narração sem campos | WARNING | `MANFRED_UNIVERSAL_CAUSALITY` (lexical) |
| 08 | evidência com `S` em interpretação sobrenatural confirmada | FAIL | `SUPERNATURAL_CONFIRMATION` |
| 09 | `ANOMALY RESIDUAL` com explicação humana disponível | PASS | — |
| 10 | `knowledge_delta` B1 ensina `UNK-SR-40Y-CAUSE` | FAIL | `BOOK1_HISTORY_LOCK_VIOLATION` |
| 11 | `Q-CRIME-FX` `RESOLVED_AT` com ≥3 sementes | PASS | — |
| 12 | evidência decisiva ancorada só no capítulo da revelação | FAIL | `DEUS_EX_DOCUMENT` |
| 13 | evidência final: `S` na solução + `C` num `MYS-*` reservado que sobe para `EXPANDING` | PASS | — |
| 14 | evidência final eleva `MYS-TRUE-CHRONOLOGY` a `RESOLVED` | FAIL | `TRUE_CHRONOLOGY_LEAK` / `PREMATURE_RESOLUTION` |
| 15 | evento `REMOVE` causado só por `SR:CMB:FULL` | FAIL | `COMBINATION_AS_REMOVAL_AUTHORITY` |
| 16 | grant sexual derivado de `COFFER_TOUCH` | FAIL | `CONSENT_INFERENCE_VIOLATION` |
| 17 | adultos, contexto adulto, `CONSENT_TO_NECK_TOUCH` válido | PASS | — |
| 18 | `COFFER_TOUCH`/grant de pescoço com `CHR-FX-C` | FAIL | `MINOR_EROTIC_SEMANTIC_VIOLATION` |
| 19 | `SFE-*` com `capturing_authority: INST-OCP` genérica | FAIL | `FACIAL_AUTHORITY_UNBOUNDED` |
| 20 | `SFE-*` com acesso público | FAIL | `SEALED_EVIDENCE_PUBLIC` |
| 21 | ordem local apaga `EXTERNAL_RECORD` | FAIL | `EXTERNAL_PURGE_ASSUMED` |
| 22 | `SELF_VIEWING deliberate: true` em espelho comum | FAIL | `SELF_FACE_VIOLATION` |
| 23 | `FRG-*` `PARTIALLY_FACIAL` isolado, visível ao leitor | PASS | — |
| 24 | conjunto declarado `combined_class: RECONSTRUCTIBLE_FACE` sem nenhum membro ao leitor | PASS | — |
| 25 | cena cita conjunto de fragmentos inexistente | FAIL | `SYSTEM_CAPABILITY_AS_INSTANCE` |
| 26 | staging usa passagem não existente no grafo | FAIL | `CARTOGRAPHIC_CONTRADICTION` (REUSE) |
| 27 | plano de cena exige fato não resolvível | `CANON_PROPOSAL_REQUIRED` | — |
| 28 | `COFFER_STATE` muda por evento `REALIZED` sem tocar `SEM_ROSTO_CANON.yaml` | PASS | (`SR-MUT-02` INFO) |
| 29 | delta posterior desfaz `IRREVERSIBLE` sem evento | FAIL | `RELATIONSHIP_STATE_CONTRADICTION` |
| 30 | revelação sobre `ENT-SELKA` altera ≥2 `MYS-*` além de Selka | FAIL | `SELKA_AS_THE_KEY` |

Mais: `PHYSICAL_RETURN_AS_REACTIVATION`, `EXTRATERRITORIAL_POWER`,
`TATTOO_NUMERIC_COMBINATION`, `VISITOR_CHILD_IN_PROTOCOL`, `PACK_SPOILER_LEAK`,
`CANARY_LEAK`, `SOURCE_HASH_MISMATCH`, `REGISTRY_DRIFT`, contrato
template ⇔ validador.

### 76.4 Canon Regression Suite

`check_sem_rosto_canon.py --mode regression` roda, após **qualquer** mudança
em seeds, approvals, ou canon materializado:

1. todos os `HL-*` sobre o canon atual;
2. todos os `HL-*` e `BG*` sobre **cada snapshot** existente (uma mudança de
   canon não pode tornar inválido um capítulo já aprovado sem ser detectada);
3. varredura de respostas (`HIDDEN_ANSWER_KEYS`) em todos os seeds, packs e
   snapshots;
4. `SYSTEM_CAPABILITY ≠ CANONICAL_INSTANCE` em todo `CAP-*`;
5. implicações cruzadas do registro novo: Book 1 locks, Facial Record
   (um documento novo tem `facial_evidence_class`?), Selka, Manfred,
   cronologia, rumores, conhecimento do leitor;
6. suíte do motor inteira sem novas falhas; goldens `tests/fixtures/golden/*.json` idênticos.

Exemplo do prompt ("novo arquivo histórico é adicionado"): o `ITM-*` novo sem
`facial_evidence_class` falha no item 5; se ele ensina algo do intervalo a
qualquer conhecedor no B1, falha no item 1 (`BOOK1_HISTORY_LOCK_VIOLATION`);
se contradiz um snapshot aprovado, falha no item 2.

---

## 77. Migration / Adoption Strategy

Não migrar o dossiê inteiro de uma vez (§76 do prompt). Ordem adaptada ao
repositório:

| Fase | Entrega | Critério de pronto |
|---|---|---|
| **1 — Ingest** | dossiê em `books/sem-rosto/canon/sources/` + `SOURCES.yaml` + approval de freeze (humano) | `SOURCE_HASH_MISMATCH` testado |
| **2 — Hard locks** | `HARD_LOCKS.seed.yaml` (28) + `CANON_RECORDS` mínimos que eles citam | cada lock com ≥1 detector; `LOCK_WITHOUT_DETECTOR` vazio |
| **3 — Book gates** | `BOOK_GATES.seed.yaml` (seção 69) | 16 gates do dossiê §21 mapeados |
| **4 — Mistérios e incógnitas** | `MYSTERIES` + `UNK-SR-*` + `PRO-SR-*` + fragmento de registry | `REGISTRY_DRIFT` testado |
| **5 — Estado e conhecimento** | templates de `STATE_DELTAS`, tokens `SR:*`, `COFFERS`, `CIVIC`, `JURISDICTION`, `RUMORS` | fixture passa nas famílias SR-KN/CMB/CNS/CIV |
| **6 — Writer** | pack + Scene Generation Contract + pós-cena | TEST 01–30 verdes |
| **7 — Canon Guardian / Warden** | `redmur_canon_warden.toml`; `BOOK_GRAPH` com `V_SR_*` e tarefas extras | compose do pacote em diretório temporário |
| **8 — Regressão** | `--mode regression` em todo PR que toca `books/sem-rosto/canon/` | suíte e goldens estáveis |

Os `CR-*` "de cor" (economia, tecnologia, tatuagem) entram **quando uma cena
precisar**, não antes — o Apêndice A mapeia onde cada um está no dossiê.

---

## 78. Open Questions

| ID | Pergunta | Bloqueia | Recomendação |
|---|---|---|---|
| ~~OQ-SR-01~~ | Aprovar o freeze do dossiê | — | **DECIDIDA:** sim (`CANON_FREEZE_0001.md`) |
| ~~OQ-SR-02~~ | Versionar o dossiê no repositório | — | **DECIDIDA:** sim (`books/sem-rosto/canon/sources/`) |
| **OQ-SR-03** | Nome e escopo do agente de obra (`REDMUR_CANON_WARDEN`), tier S | S5 | um agente consultivo; nunca dono de canon |
| ~~OQ-SR-04~~ | Quais mistérios reservados viram `Q-*` | — | **DECIDIDA (delegada):** nenhum agora; ver tabela de decisões |
| ~~OQ-SR-05~~ | Local do Six-Month Protocol, Veil House, Transfer Zone, Preservation Boundary | — | **DECIDIDA (delegada):** ver tabela de decisões (05a/05b/05c) |
| **OQ-SR-06** | Canon interpretativo antes do compose LTE (S5): tarefa extra à la Narciso ou esperar | S5 | tarefa extra (`T018N`-like): a obra precisa do `Q-CRIME-B1` |
| **OQ-SR-07** | Adotar o kit DEDR para SEM ROSTO? Se sim, corrigir a fixture DEDR para a fonte do dossiê (D-SR-02) | S5 | adotar como REUSE de acoplamento/fair-play; §33 do DEDR fica como ilustração histórica |
| **OQ-SR-08** | Protagonistas, crime, valores de combinação | pacote do livro | decisão da autora; este SDD só fornece os slots |
| **OQ-SR-09** | `images.face_consistency_required: false` e identidade visual não facial no pacote | pacote | sim (75.3) |
| **OQ-SR-10** | Exposição facial deliberada entre adultos: exigir bloco `consent` do ledger mesmo sem `kind` adulto? (o dossiê não diz que ver o rosto é erótico; diz que é crime e exige camada própria de consentimento) | S3 | exigir o grant `CONSENT_TO_FACIAL_EXPOSURE` (SR); **não** mapear para `INTIMACY` por padrão — a leitura erótica é contextual |
| **OQ-SR-11** | Nome/data do Preservation Act (dossiê: "podem ser refinados") | cenas que citam | `PROVISIONAL`; decisão da autora |
| **OQ-SR-12** | `story_present_year` | cenas datadas | decisão da autora (TIMELINE) |
| **OQ-SR-13** | Natureza de "Flarry" (família? pessoa?) e relação com `Flarry Estate` | cenas com Flarry | decisão da autora; até lá `UNSPECIFIED` |
| **OQ-SR-14** | Valores padrão de `scope.character.default` por regra (quem no mundo conhece cada regra) | fase 2 | preencher com a autora; padrão conservador `NONE` |
| **OQ-SR-15** | Reusar o modelo de proveniência do `HISTORICAL_DARK_ROMANCE_CANON` para `CHRONO-*`/`ITM-*` quando aprovado | — | reavaliar depois; não bloquear |
| **OQ-SR-16** | Promover ao motor o que se mostrar genérico (pack narrativo, tokens de modalidade, status de duas camadas) | — | só no 2º livro que precisar (DR SDD Q1) |
| **OQ-SR-17** | Limiares de calibração (orçamento do pack 1.500 palavras; `NON_HUMAN_OVERUSE` 0.15; `SELKA_OVERCENTRALIZATION` 0.5; `PROMISE_FORGOTTEN` 6) | — | aceitar como hipótese; recalibrar no piloto |

## 79. Implementation Plan

Cada slice entrega comportamento observável e é aprovado antes do próximo.

```text
S0 ─▶ S1 ─▶ S2 ─▶ S3 ─▶ S4 ─┬─▶ S5 (integração no pacote; depende do pacote completo e de OQ-SR-06/07)
                            └─▶ S6 (piloto real, opcional)
```

| Slice | Objetivo | Arquivos | Testes / DoD | Compl. |
|---|---|---|---|---|
| **S0** Decisões e pinagem — **CONCLUÍDO 2026-09-21** | freeze, versionar dossiê | `books/sem-rosto/canon/sources/{REDMUR_CANON_RESOLUTION_DOSSIER_FINAL.md, SOURCES.yaml}`, `approvals/CANON_FREEZE_0001.md` (humano), README do pacote | hash conferido; OQ-SR-01/02 decididas | S |
| **S1** Registros, locks, gates — **CONCLUÍDO 2026-09-21** | contrato e integridade | `canon/seeds/{CANON_RECORDS, HARD_LOCKS, BOOK_GATES}.seed.yaml`, `canon/templates/*`, `validators/check_sem_rosto_canon.py` (`--mode package`), `tests/test_sem_rosto_canon.py`, fixture | SR-SRC, SR-CR, SR-ST, SR-PV, SR-HL-02/03; `git diff --stat engine/` vazio | M |
| **S2** Mistérios, rumores, conhecimento — **CONCLUÍDO 2026-09-26** | projeções | seeds `MYSTERIES`, `RUMORS`; `--mode plan --runtime`; `--emit-registry-fragment`; `--is-true`, `--who-knows`, `--reader-at`, `--mystery` | TEST 03, 05, 06, 10; `REGISTRY_DRIFT` | M |
| **S3** Firewalls | estado dinâmico e regras | seeds `COFFERS`, `CIVIC`, `JURISDICTION`, `LEXICON`; template `STATE_DELTAS`; famílias FACE/FRC/SFE/EXT/CMB/TCH/CNS/AGE/CIV/JUR/TEC/TAT/MAN/SEL/NH | TEST 01, 02, 04, 07–09, 15–25, 30 | L |
| **S4** Pack, contrato, pós-cena, crime | escrita guiada | `--pack`, Scene Generation Contract, `POST_SCENE_REPORT`, schemas; crime/fair-play/double-edge/irreversibilidade/promessas; `--mode wave/final/regression`; snapshots | TEST 11–14, 26–29; `--verdict` | L |
| **S5** Integração no pacote | pacote compõe com o sistema | `BOOK_SPEC`/`BOOK_GRAPH` de SEM ROSTO (quando existir), `agents/redmur_canon_warden.toml`, `text_quality.yaml`, tarefas `T018S`, `T1NNS`, `T2NNS`; cartografia: D-SR-11 | compose em diretório temporário; `validate-gate GATE_CANON`; goldens idênticos | M |
| **S6** Piloto (opcional, pago) | 2–3 capítulos em `DRAFT` | runtime real | humano responde "sim" à pergunta de aceite (seção 80) para as cenas do piloto e o relatório concorda | — |

### 79.1 Estado do Slice 1 (2026-09-21)

Entregue:

- `books/sem-rosto/canon/seeds/CANON_RECORDS.seed.yaml` — 136 registros (141 após o Slice 2, seção 79.2):
  82 `CR-*`, 5 `CAP-*` (todos com `instances: []`), 30 `UNK-SR-*` (um por item do dossiê §17 — 24 — mais
  6 citados por locks/gates e pelas decisões OQ-SR-05), 12 `PRO-SR-*`, 7 entidades (`ENT-SELKA`,
  `FAM-MANFRED`, `ENT-FLARRY` `UNSPECIFIED`, `INST-OCP`, `INST-CONSTABULARY`, Police Scotland, COPFS).
  Todo registro cita `§N[.N]` existente no dossiê pinado ou um item de aprovação humana.
- `HARD_LOCKS.seed.yaml` — os 28 locks da seção 15.2, com detectores `SR-*`, `ENGINE:<validador>:<regra>`
  ou `JUDGMENT:<agente>`.
- `BOOK_GATES.seed.yaml` — Livro 1: 11 `REQUIRED`, 4 `PARTIAL`, 21 `FORBIDDEN`, os 16 gates de escrita do
  §21; série: 5 locks estruturais e 10 domínios futuros; `B2: UNDEFINED`.
- `books/sem-rosto/validators/check_sem_rosto_canon.py --mode package` — famílias SR-SRC, SR-CR, SR-ST-04,
  SR-PV-01/05, SR-HL-02/03; lista de chaves de resposta importada do motor
  (`check_interpretive_canon.HIDDEN_ANSWER_KEYS`); `map_refs` conferidos contra os seeds da cartografia.
- `tests/test_sem_rosto_canon.py` — 39 testes (9 sobre os dados reais, 30 mutações com categoria exata).

Resultado nos dados reais: `PASS_WITH_WARNINGS` — 3 × `SEED_UNAPPROVED` (MEDIUM: os seeds aguardam
aprovação humana, como os da cartografia) e 1 `LOCK_DETECTORS_PLANNED` (INFO: 21 dos 28 locks só têm
detectores estruturais de slices futuros; até lá valem como checklist do revisor — o relatório diz isso
explicitamente em vez de fingir cobertura).

Desvios do texto do SDD, deliberados:

| Onde | SDD dizia | Implementado | Por quê |
|---|---|---|---|
| 12.1 | campo `canon_id` | `id` | convenção de todos os artefatos do repositório |
| 12.6 | templates separados em `canon/templates/` | os próprios seeds + testes de mutação são o contrato executável | um template a mais duplicaria 136 registros sem ganho; o contrato está em `FIELDS_BY_KIND`/`REQUIRED_BY_KIND` do validador |
| 13, 66 | regras SR-CR sem numeração | SR-CR-01..11 (contrato, duplicado, id, enum, referência, UNK com conteúdo, resposta escondida, cobertura, registry drift [S2], seed não aprovado, seed editado) e SR-SRC-02 `FREEZE_NOT_APPROVED`; SR-B1-01..11 = verificação final de cada `BG1-R-*` (S4) | os locks precisam citar regras por id |
| 12.2 | `THEORY-*`, `RUM-*`, `MYS-*` em `CANON_RECORDS` | ficam para o Slice 2 (`RUMORS`, `MYSTERIES`) | escopo do slice |

### 79.2 Estado do Slice 2 (2026-09-26)

Entregue:

- `books/sem-rosto/canon/seeds/MYSTERIES.seed.yaml` — 21 mistérios: 15 correspondem, um a um, ao dossiê
  §18 (`dossier_item` 1–15); 6 fora de §18 cobrem os bloqueios citados por `HARD_LOCKS`/`BOOK_GATES`
  (`MYS-TRUE-CHRONOLOGY`, `MYS-COFFER-ORIGIN`, `MYS-SIX-MONTH`, `MYS-BODY-GAP`, `MYS-SELF-FACE-TABOO`,
  `MYS-CRIME-B1`). Todo mistério reservado tem teto `EXPANDING` no Livro 1 (nunca `PARTIALLY_RESOLVED`);
  nenhum tem `interpretive_question` (decisão OQ-SR-04: nenhum mistério reservado vira `Q-*` do LTE).
- `RUMORS.seed.yaml` — 6 rumores/teorias com existência canônica; toda `THEORY-*` tem
  `prohibited_as_fact` apontando uma nova `PRO-SR-*` (5 acrescentadas a `CANON_RECORDS`, total 141).
- `check_sem_rosto_canon.py --mode plan --runtime <rt>` (novo modo, sobre o ledger causal do runtime):
  `SR-KN-01..06` (conhecimento de personagem; REUSE de `check_causal_ledger.check_information_leak`),
  `SR-RD-01/02` (conhecimento do leitor; REUSE de `check_reader_omniscience`), `SR-ST-01/03/04`
  (incógnita/rumor/capacidade nunca viram fato), `SR-MYS-01..03` (teto do mistério, mistério sem
  world_truth, pergunta reservada nunca resolvível), `SR-PV-02` (delta de estado sem causa),
  `SR-CR-09` (`REGISTRY_DRIFT`: fragmento gerado ⇔ `CANON_REGISTRY.yaml` do runtime).
- Tokens de conhecimento por modalidade (`SR:BELIEVES:`/`SUSPECTS:`/`MISREMEMBERS:`/`TOLD:` + id puro
  para "sabe"), exatamente como projetado na seção 17.2 — zero mudança no ledger, que já aceita
  qualquer id em `learns`.
- Consultas: `--is-true`, `--who-knows`, `--reader-at`, `--mystery`, `--emit-registry-fragment`
  (seção 73), todas em visão padrão (nunca `world_truth`, nunca conteúdo de `UNK-*`).
- Fixture `tests/fixtures/sem_rosto_canon/runtime_min/` (personagens `CHR-FX-*`, 4 eventos, 8 deltas
  de estado) — passa em `check_causal_ledger.validate` **e** no modo `plan`; usada pelas 39 novas
  asserções (9 dados reais + 7 consultas + 23 mutações), total 78 testes na suíte.

Resultado no pacote real (`--mode plan --runtime <fixture>`): `PASS_WITH_WARNINGS`, mesmos 5 avisos do
Slice 1 (4 seeds aguardando aprovação + `LOCK_DETECTORS_PLANNED`), nenhum achado bloqueante.

Desvios do texto do SDD, deliberados:

| Onde | SDD dizia | Implementado | Por quê |
|---|---|---|---|
| 20.1 | três camadas (série/incógnita/teoria ativa) sempre presentes | mistérios reservados do Livro 1 não têm camada de teoria ativa (nenhum `interpretive_question`) | OQ-SR-04: evita criar teses concorrentes que o dossiê não define |
| 21.2, passo 9 | classes epistêmicas completas (`ALLOW_AS_RUMOR`/`ALLOW_AS_THEORY`/`ALLOW_AS_PARTIAL`) | Slice 2 implementa só o binário ALLOW/BLOCK sobre conhecimento; as classes finas do `MYSTERY_DISCLOSURE_GATE` (passo 9 completo) ficam para o Slice 3, junto do pack de cena | o gate completo precisa do pack e do contrato de cena (seção 60), ainda não implementados |
| 60.3, 65 | `--mode scene`/pack por cena | não implementado neste slice | escopo do Slice 3 |

Pré-condição de S5: pacote completo de SEM ROSTO (hoje parcial — só
cartografia; DEDR S6) e working tree de outras frentes versionado (D-CART-16).

## 80. Acceptance Criteria

### 80.1 Definition of Done (§79 do prompt) → onde

| # | O motor consegue… | Seção / regra | Teste |
|---|---|---|---|
| 1 | carregar o cânone | 5, 12, 71 (`--mode package`) | S1 |
| 2 | distinguir verdade de rumor | 13, 19 | 06 |
| 3 | World Truth × Character Knowledge | 16, 17 | 05 |
| 4 | Character × Reader Knowledge | 17, 18 | 02, 10 |
| 5 | proteger hard locks | 15 | regressão |
| 6 | impedir descrição facial | 22–24 | 01, 02, 22 |
| 7 | proteger mistérios | 20–21 | 10, 14 |
| 8 | proteger Book 1 History Locks | 45, 49, 69 | 10, 30 |
| 9 | controlar combinações/cofres | 29–30 | 15 |
| 10 | controlar semântica corporal/consentimento | 31–32 | 16, 17 |
| 11 | proteger menores | 33–34 | 18 |
| 12 | preservar ausência de magia | 15 (HL-01..03), 38, 50 | 08, 09 |
| 13 | impedir Manfred universal | 48 | 07 |
| 14 | proteger Selka | 49 | 30 |
| 15 | integrar cartografia | 57 | 26 |
| 16 | acompanhar crime | 51–53 | 11–14 |
| 17 | acompanhar romance | 54–55 | 29 |
| 18 | gerar Canon Context Pack por cena | 60, Apêndice B | S4 |
| 19 | validar uma cena | 65 | S4 |
| 20 | bloquear invenção canônica | 62 | 27 |
| 21 | solicitar decisão humana | 63, 78 | 27 |
| 22 | persistir Story State | 59, 71 | 28 |
| 23 | produzir snapshot por capítulo | 67 | S4 |
| 24 | rodar regressões após mudança de cânone | 76.4 | S4 |

### 80.2 A pergunta de aceite

> **"Se Bea Halden escrever esta cena agora, ela continua dentro de SEM ROSTO?"**

```bash
python book/validators/check_sem_rosto_canon.py --runtime . --verdict --chapter 7 --scene SC-07-02
```

```text
VERDICT: FAIL
  [BLOCKER] CONSENT_INFERENCE_VIOLATION  SD-0405 → grant CONSENT_TO_NECK_TOUCH derivado de COFFER_TOUCH
            canon: HL-08 · CR-P13-R10 · dossiê §15.4 ("CONSENT_TO_COFFER_TOUCH ≠ ...") e §15.5 (COFFER_TOUCH ≠ CONSENT_TO_NECK_TOUCH)
            ação:  declarar grant próprio de CONSENT_TO_NECK_TOUCH, ou marcar o ato como violação com consent.canonical coerente
  [WARNING] FACELESS_EXPRESSION_SUSPECTED  TEXT:7:"sorriu para ela" — CHR-X sem FACE_EVENT para o POV
            canon: CR-P13-01 · dossiê §15.1 (FEEL → OBSERVE → INFER) · aguardando REDMUR_CANON_WARDEN
  [INFO]    reader_knows_but_pov_does_not: EDG-S-002 (mapa impresso)
```

Critério final: a resposta é sempre um de `PASS`, `PASS_WITH_WARNINGS`,
`FAIL`, `CANON_PROPOSAL_REQUIRED` — **com referência ao registro canônico e
à seção do dossiê** — e nenhuma resposta depende de o sistema conhecer uma
verdade que o dossiê não decidiu.

---

## Apêndice A — Canon Extraction Map (dossiê → sistema)

O dossiê não é reescrito; cada seção vira ids e regras que **apontam** para ela.

| § dossiê | Conteúdo | Registros | Regras / seções deste SDD |
|---|---|---|---|
| §0 | autoridade, precedência, `SYSTEM_CAPABILITY ≠ CANONICAL_INSTANCE` | `CR-ABS-00`, `HL-05` | 6, 13, 15 |
| §1.1 | Redmur não é o mundo; não soberana | `CR-ABS-01` | 37 (`SOVEREIGNTY_ASSUMED`) |
| §1.2 | burocracia vitoriana absorve tecnologia | `CR-ABS-02` | 39 |
| §1.3 | regra sobrenatural | `HL-01..03`, `HL-20` | 15, 50 |
| §1.4 | regra absoluta do rosto | `HL-04` | 22 |
| §1.5 | regra do mistério | `CR-ABS-05` | 20 (mistério tem estrutura; `MYS-*` sem resposta ≠ sem planejamento) |
| §1.6 | regra de humanidade | `CR-ABS-06` | 38, 50 (causa humana primeiro) |
| §2 (P0) | cofre, Service Cowl, Emergency Breach, Dual Authorization, classes, heráldica, R1, R5 | `CR-P0-*`, `CAP-COF-*`, `CLS-*`, `HL-07`, `HL-21`, `HL-23`, `HL-24`, `HL-26` | 29, 30 |
| §3 (P1) | Facial Uncovering/Exposure/Record, R9, R6, R7, R8 | `CR-P1-*`, `CR-R6..R9-*`, `CAP-SEALED-FACIAL-EVIDENCE`, `CAP-EXTERNAL-FACIAL-RECORD`, `UNK-SR-SELF-FACE-ORIGIN`, `HL-11..13` | 22–26 |
| §4 (P2) | Six-Month Protocol, R3, R4, R5, R11 | `CR-P2-*`, `THEORY-CHILD-SUBSTITUTION`, `UNK-SR-SIX-MONTH-CONTENTS`, `UNK-SR-CHILD-FACILITY-LOCATION`, `HL-06`, `HL-25` | 33, 34 |
| §5 (P3) | Visitor Protocol | `CR-P3-*`, `CLS-VISITOR`, `UNK-SR-VEIL-HOUSE-LOCATION` | 35 |
| §6 (P4) | Returner, Open Gate Paradox, R2 | `CR-P4-*`, `HL-09` | 35, 36 |
| §7 (P5) | Palimpsest Jurisdiction, Act, OCP, Savings Clauses, polícia | `CR-P5-*`, `INST-OCP`, `INST-CONSTABULARY`, `UNK-SR-SAVINGS-CLAUSES-WHY`, `HL-10` | 37 |
| §8 (P6) | The Pull | `CR-P6-*`, `UNK-SR-PULL-COMPLETE`, `MYS-THE-PULL` | 38 |
| §9 (P7) | Technology Veil, Paper Face / Digital Shadow | `CR-P7-*`, `HL-27` | 39 |
| §10 (P8) | Identity Stack, Faceless Literacy, Civic Seal, Dermal Identity, Combination Tattoos | `CR-P8-*`, `HL-19`, `HL-24` | 28, 40, 41 |
| §11 (P9) | economia, coffermaking, tattoo economy, Manfred Estate, information market, Body Gap | `CR-P9-*`, `UNK-SR-BODY-GAP` | 42, 43 |
| §12 (P10) | Blind Chronology, Black Interval, Four Archives, Dead Archive, Book 1 History Lock | `CR-P10-*`, `CAP-DEAD-ARCHIVE`, `UNK-SR-40Y-*`, `MYS-TRUE-CHRONOLOGY`, `MYS-FORTY-YEARS`, `BG1-F-*` | 44–47, 69 |
| §13 (P11) | Manfred Power Model | `CR-P11-*`, `FAM-MANFRED`, `THEORY-MANFRED-ERASED-40Y`, `HL-15` | 48 |
| §14 (P12) | 1% Non-Human, Selka, Lost Grave, Missing Grave, 10 Relics, Three-Layer Archive, Ontology Firewall, Book 1 Selka Lock | `CR-P12-*`, `ENT-SELKA`, `UNK-SR-SELKA-*`, `RUM-SELKA-COFFER`, `THEORY-MISSING-GRAVE-IS-SELKA`, `RUM-TEN-RELICS`, `HL-14` | 49, 50 |
| §15 (P13) | Feel→Observe→Infer, No Gesture Loop, Naked Neck, R10, R11, arquitetura de intimidade | `CR-P13-*`, `HL-06`, `HL-08` | 27, 31–33 |
| §16 (P14) | Book 1 Resolution Contract | `CR-P14-*`, `crime_contract`, `BG1-R-*`, `BG1-F-*`, `HL-17`, `HL-18`, `HL-28` | 51–55, 69 |
| §17 | CANON UNKNOWN | `UNK-SR-*` (um por item) | 16, 62 |
| §18 | RESERVED MYSTERIES | `MYS-*` | 20 |
| §19 | Cartography Dependency | `CR-CART-*`, `HL-22` | 57 |
| §20 | dependências separadas (X-Files, Death/Funeral, Power System Expansion) | interfaces reservadas (`ITM-*`, `SR-DA-*`) | 47, 56 |
| §21 | gates de escrita do Livro 1 | `BG1-*` | 69.5 |
| §22 | gates do Livro 2 / futuro | `BGF-*`, `series.structural_locks` | 70 |
| §23 | não-canonização acidental | `HL-05` + exemplos como testes | 15, 76 |
| §24 | frases canônicas | `CR-PHRASE-*` (`TONAL_REFERENCE`) | Warden (tom), nunca validador |
| §25 | consistency check; R12+ só por decisão humana | `SR-PRC-04`, 13.4 | 13, 64 |
| §26 | handoff para este SDD | — | este documento |
| §27 | condição de canon freeze | `SRC-DOSSIER.freeze`, OQ-SR-01 | 5.2 |
| §28 | princípio de encerramento (quatro perguntas) | `CR-PHRASE-CLOSING` (`TONAL_REFERENCE`) | Warden, crítica |

## Apêndice B — Scene Generation Contract (forma renderizada)

Gerado do pack (seção 60), no idioma da obra, curto. Exemplo de **forma** com
ids de fixture:

```text
SCENE GENERATION CONTRACT — SC-07-02 (cap. 7) · POV CHR-P · RM-CEN-CHP · D014T23:14 · adult_semantics: ENABLED

YOU MAY USE:
  - CR-P1-02  Facial Exposure é crime.  (§3.2)
  - CR-P0-03  O Service Cowl permite descobrir o rosto sem expô-lo.  (§2.2)
  - EVD-12    [observável a plantar] …
YOU MAY IMPLY:
  - que CHR-P viu o rosto de CHR-X (FACE_EVENT SD-0200); o efeito, nunca o rosto.
  - MYS-SELKA: rumor/fragmento/contradição/pista/teoria — nunca túmulo, corpo, cofre, morte.
YOU MAY NOT REVEAL:
  - qualquer traço do rosto de CHR-X (HL-04; fragmentos publicados até aqui: 0)
  - conteúdo de UNK-SR-40Y-CAUSE, UNK-SR-SELKA-DEATH, UNK-SR-SIX-MONTH-CONTENTS (desconhecidos — não preencher)
  - a solução de Q-CRIME-B1 (reader_access: EV-… no cap. 24)
THE POV CHARACTER KNOWS:        CR-P1-02 · ITM-017 (possui; não leu) · RTE-A-R2
THE POV CHARACTER BELIEVES:     RUM-SELKA-COFFER (como rumor)
THE POV CHARACTER CANNOT KNOW YET: 3 itens (ids no pack; sem conteúdo)
THE READER KNOWS:               CR-P1-02 · mapas impressos · EVD-05
  reader knows, POV does not:   EDG-S-002 (passagem no mapa impresso — POV não pode usá-la)
ACTIVE MYSTERIES:               MYS-SELKA (teto B1: TEORIA) · MYS-FORTY-YEARS (teto B1: EXPANDING)
FORBIDDEN SOLUTIONS:            BG1-F-SELKA-GRAVE · BG1-F-40Y · BG1-F-MAGIC
RELATIONSHIP STATE:             CHR-P→CHR-X  trust: TESTED · desire: ACTIVE    (irreversíveis: 0)
CONSENT STATE:                  CHR-X→CHR-P  CONSENT_TO_COFFER_TOUCH (esta cena) · nenhum outro grant
                                (toque de cofre NÃO autoriza pescoço, lock, remoção, rosto — HL-08)
COFFER / COMBINATION STATE:     COF-0003 FITTED · CMB-0003: CHR-P não conhece; leitor não conhece
LOCATION CONSTRAINTS:           [pack cartográfico] saídas visíveis …; nenhuma travessia do Ash Burn fora de Burn Bridge
CONTINUITY CONSTRAINTS:         PRM-0004 deve ser alimentada · sem espelho comum em Redmur (CR-R8-05)
IF YOU NEED A FACT THAT IS NOT HERE: não invente. Escreva em CANON_PROPOSALS (CP-SR-*) e siga pelo workaround listado, se houver.
```

## Apêndice C — Arquivos inspecionados e comandos

**Fonte:** `~/Downloads/REDMUR_CANON_RESOLUTION_DOSSIER_FINAL.md` (integral, 1975 linhas; sha256 calculado).

**Raiz e docs:** `AGENTS.md`, `README.md`, `engine/IMPLEMENT.md`, `docs/ARCHITECTURE.md`,
`docs/BOOK_PACKAGE_MODEL.md`, `books/sem-rosto/README.md`;
`docs/sdd/DYSTOPIC_ENIGMA_DARK_ROMANCE_SDD_v0.1.md` (integral);
`docs/sdd/REDMUR_CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md` (cabeçalho, decisões, Parte 0, §1–6, §22–27; índice completo);
`docs/sdd/LIVING_THEORY_ENGINE_SDD_v0.1.md` (§5–8; índice);
índices e resumos de `DARK_ROMANCE_CANON_ARCHITECT`, `REPRESENTATION_INTEGRITY`,
`UNSEEN_RECOGNITION_ECONOMY` (§1), `HISTORICAL_DARK_ROMANCE_CANON` (§10),
`SEM_ROSTO_VAULT_EDITION_MANUFACTURING_BIBLE`.

**Motor:** `engine/ENGINE_GRAPH.yaml` (locks, `CANON_PROPOSAL_PROTOCOL`);
`engine/contracts/{CANON_PROPOSAL, CANON_CONFLICT, REVIEW_FINDING}.schema.json`;
`engine/templates/{CAUSAL_LEDGER_TEMPLATE.yaml, CAUSAL_LEDGER_RUNBOOK.md, INTERPRETIVE_CANON_TEMPLATE.yaml}`;
`engine/scripts/check_causal_ledger.py` (constantes, funções, `check_reader_omniscience`,
`check_information_leak`, `knowledge_state`); `check_interpretive_canon.py` (60–180, categorias);
`check_representation.py` (hard boundaries); `check_canon_continuity.py` (docstring, funções);
`build_canon_digest.py`, `check_cartography.py` (funções); `livingbook.py` (features, T018/T019,
briefs, `additional_tasks`/`gate_extensions`); `engine/agents/{canon_guardian, chapter_writer}.toml`.

**Obra e precedentes:** `books/sem-rosto/cartography/{approvals/CART_DECISION_0001.md,
seeds/{CARTOGRAPHY, KNOWLEDGE_BASELINE, MYSTERIES, BOUNDARIES, ARTIFACTS, LOCATIONS,
SUBTERRANEAN}.seed.yaml}`; `books/narciso/BOOK_GRAPH.yaml`, `BOOK_SPEC.yaml` (features),
listagem de `books/narciso/`; `tests/fixtures/living_theory/runtime_sino_vale_alto/canon/CANON_REGISTRY.yaml`;
listagem de `tests/` e `tests/fixtures/`.

**Comandos (somente leitura):** `git status --short`, `git log --oneline`, `git ls-files`,
`git branch --show-current`, `wc -l`, `grep`/`sed` sobre os arquivos acima, `sha256sum` do dossiê.
Nenhum `compose`, nenhum teste executado, nenhum arquivo existente alterado. O único arquivo criado
é este SDD.
