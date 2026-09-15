# SDD v0.1 — `NARCISO` (Bea Halden) — SDD Canônico da Obra

> **Status:** `PROPOSTA — OQ-N1..OQ-N5 DECIDIDAS PELO HUMANO EM 2026-09-15 (seção 36.1); DEMAIS PERGUNTAS ABERTAS`. Nenhum código de
> produção foi escrito. Nenhum runtime, contrato, template, agente, script ou
> pacote de livro foi criado ou alterado. Nenhum capítulo, cena ou ilustração
> foi produzido. **Único arquivo criado nesta sessão: este documento.**
>
> **Escopo:** extensão de obra sobre o PEDRO_ARTE_LIVING_BOOK_ENGINE,
> `engine/ENGINE_GRAPH.yaml` versão `1.1.0`, branch `main`, commit `b1bd12b` +
> working tree contendo as capabilities `DARK_ROMANCE_CANON_ARCHITECT` e
> `BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM` implementadas e **não commitadas**
> (verificado em 2026-09-15: `Ran 274 tests … OK`).
>
> **Regras aplicadas:** `REUSE > EXTEND > CREATE`, `SIMPLICIDADE SEMPRE`,
> OFF por padrão para tudo que tocar o motor, `/engine` neutro de gênero.
>
> **Convenção:** mesma das SDDs irmãs — texto em PT-BR; identificadores,
> enums, estados e invariantes em inglês.
>
> **SDDs irmãs (dependências diretas, não alteradas):**
> `docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md` (ledger causal, gate
> adulto, consentimento, Second-Read, governança Bea Halden) e
> `docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md` (Author DNA, canon
> visual, Chekhov, sigils, edições, acabamentos, thumbnail).
>
> **North Star:**
>
> > **Narciso se apaixonou pelo próprio reflexo. O leitor deve correr o risco
> > de cometer o mesmo erro.**

---

## Índice

1. Executive Summary
2. Discovery Findings
3. Existing Architecture Map
4. REUSE / EXTEND / CREATE Matrix
5. NARCISO Product Thesis
6. Myth Adaptation Contract
7. Narrative Canon
8. Character Architecture
9. Narcissus Uncertainty Principle
10. Love Ambiguity System
11. Desire/Decay Progression
12. Bea Halden Voice Profile
13. Visual Bible
14. Narcissus Visual DNA
15. Symbol Registry
16. Illustration Canon
17. Visual Narrative Progression
18. Book-as-Mirror System
19. Text/Image Relationship System
20. Reread Layer
21. Physical Book / Possession Experience
22. Print Capability Matrix
23. Collector Edition Strategy
24. Social Object Design
25. Canon & Continuity Contracts
26. Gates & Validators
27. Metrics
28. Task Graph Integration
29. Proposed Schemas
30. Testing Strategy
31. Failure Modes
32. Copyright / Public-Domain Considerations
33. Safety / Adult Character Rules
34. Acceptance Criteria
35. Implementation Slices
36. Open Questions
37. Final Recommendation
- Apêndice A — Arquivos inspecionados e comandos executados
- Apêndice B — Glossário de ids

---

## 1. Executive Summary

### 1.1 O que é

NARCISO é o segundo pacote Dark Romance de Bea Halden no motor, e o primeiro
em que **o objeto físico e as ilustrações são canon narrativo**, não
embalagem. Esta SDD define identidade, regras, contratos e integração para que
um agente futuro execute a obra sem redescobri-la, e para que o motor possa
responder objetivamente — até onde o objetivo alcança — à pergunta
**"isto parece NARCISO?"**.

### 1.2 A descoberta que mais moldou o desenho

**Quase tudo o que NARCISO precisa já existe no repositório**, em três camadas
já implementadas e testadas:

| Necessidade de NARCISO | Já existe como |
|---|---|
| causalidade de personagem, consentimento, idade adulta, crenças do leitor, releitura sem retcon | `canon/CAUSAL_LEDGER.yaml` + `check_causal_ledger.py` (L0–L10) |
| identidade visual autoral, símbolos com significado ancorado, progressão por estados, spoiler por superfície, edições e acabamentos com fallback, thumbnail | `authors/bea_halden/AUTHOR_VISUAL_DNA.v1.yaml` + `canon/VISUAL_NARRATIVE_CANON.yaml` + `check_visual_canon.py` (V0–V9, ST-01..09) |
| mito/folclore em domínio público com clean-room e delta de adaptação | precedente `books/a-noiva-esquecida/planning/01_SOURCE_CANON.md`, `02_ADAPTATION_DELTA.md`, `IR007` |
| mistério que nunca se resolve | precedentes `eva` (`IR002`, `IR019`, `MYSTERY_AMBIGUITY_GUARDIAN`) e `a_morte` (`unknowns`, `prohibited_inferences`, `LIMINALITY_GUARDIAN`) |
| identidade facial estável entre imagens | `FACE_CANON_TEMPLATE.md`, `T038/T039`, `generate_image.py --reference/--edit`, `T4NN_FACE_QA` |
| extensão de obra sem tocar o motor | `BOOK_GRAPH.yaml` → `additional_tasks`, `gate_extensions`, `custom_validators` (`livingbook.py:589-592`) + `books/<slug>/agents/*.toml` + `books/<slug>/validators/*.py` |

O que **não** existe é pequeno e nomeável:

1. **Ambiguidade interpretativa estruturada** — nenhum artefato verificável
   diz "esta evidência sustenta estas hipóteses e não exclui aquelas". Os
   precedentes vivem em prosa e em guardiões LLM.
2. **Mais de uma ilustração por capítulo, com categoria e relação
   texto×imagem** — o compositor gera exatamente uma imagem por capítulo
   (`livingbook.py:492`); `features.images.primary_per_chapter` existe nos
   `BOOK_SPEC` mas **nenhum script o lê**.
3. **Progressão de desejo com regra de repetição por significado** — o
   ledger mede amplitude emocional (L6), não o que muda entre recorrências
   da mesma classe de cena.
4. **Continuidade de corpo parcial e de definhamento** — `FACE_CANON` cobre
   rosto; a classe `FIGURE` existe no validador visual
   (`check_visual_canon.py:67-70`) mas **não tem nenhuma regra própria**.
5. **Efeitos físicos de espelho** (papel metalizado, placa espelhada) e
   **ephemera** (cards, marcadores, slipcase) — ausentes de
   `EDITION_CAPABILITIES.yaml`.

### 1.3 A menor arquitetura que cumpre NARCISO

```text
PACOTE DA OBRA (sem tocar /engine)
  books/narciso/                         pacote padrão (BOOK_SPEC, CONSTITUTION, rules, scenes, architecture…)
  books/narciso/planning/                source canon, adaptation delta, visual bible, voice profile (precedente noiva)
  books/narciso/seeds/INTERPRETIVE_CANON.seed.yaml   hipóteses, evidências, leituras de amor, ocorrências de desejo, pistas de releitura
  books/narciso/agents/                  2 guardiões da obra (precedente eva/a_morte)
  books/narciso/validators/validate_narciso.py      1 validador da obra, 4 modos (precedente validate_book_dna.py)
  books/narciso/BOOK_GRAPH.yaml          2 tarefas adicionais + anexação do validador a gates existentes

RUNTIME (gerado)
  canon/NARCISO_INTERPRETIVE_CANON.yaml  dono CANON_GUARDIAN, lock CANON_WRITE (REUSE de governança)
  canon/CAUSAL_LEDGER.yaml               REUSE integral
  canon/VISUAL_NARRATIVE_CANON.yaml      REUSE + bloco opcional `illustration` em compositions (EXTEND)

MOTOR (EXTEND, neutro de gênero, OFF por padrão, goldens intactos)
  check_visual_canon.py                  regras para `FIGURE` e para o bloco `illustration`
  livingbook.py                          tarefas de ilustração por id de composição (além de 1/capítulo)
  build_kdp_docx.py                      placement de pranchas por id + pares de página (spread)
  EDITION_CAPABILITIES.yaml              efeitos MIRROR_BOARD / METALLIZED_PAPER / SLIPCASE / INSERT_CARD (VENDOR_DEPENDENT)

0 gates novos · 0 agentes genéricos novos · 0 dependências novas · 0 serviços
```

### 1.4 O que NÃO é

- **Não** é um "Narcissus Engine", "Reflection Engine", "Desire Engine" ou
  "Reread Engine". Todos os conceitos pedidos viraram **campo, projeção,
  consulta ou regra de validador** sobre mecanismos existentes.
- **Não** é pontuação de desejo do leitor. Métricas são diagnóstico (seção 27).
- **Não** é prosa, cena, capítulo ou arte. É contrato.
- **Não** muda nenhum livro existente (golden de compose intacto é critério de
  aceite de todo slice que tocar o motor).

### 1.5 Recomendação em uma linha

```text
READY_FOR_SLICE_1 (pacote narrativo NARCISO, sem tocar o motor) = YES,
com OQ-N1..OQ-N5 já decididas pelo humano (seção 36.1).
```

---

## 2. Discovery Findings

Todas as afirmações abaixo foram verificadas lendo código, templates, pacotes
e runtimes reais nesta sessão (Apêndice A). Nenhuma veio só de documentação.

### 2.1 Estado do repositório

| Fato | Evidência |
|---|---|
| Motor válido | `livingbook.py validate-engine` → `ENGINE VALID | generic agents: 66 | version: 1.1.0` |
| Suíte offline verde | `python -m unittest tests.test_causal_ledger tests.test_visual_canon tests.test_compose_regression tests.test_visual_narrative_rendering` → `Ran 274 tests … OK` |
| Pacote Bea Halden real existe | `books/a-noiva-esquecida/BOOK_SPEC.yaml:7` (`author: Bea Halden`), `:82-91` (`causal_ledger` + `visual_narrative` ligados); `validate-book` → `BOOK PACKAGE VALID | A Noiva Esquecida | chapters: 40` |
| Runtime Bea Halden real em execução | `runtime/a-noiva-esquecida/project_state/PROJECT_STATUS.yaml` (T000–T019 e `T021_LEDGER_SNAPSHOT` aprovados; `T020` pendente) |
| Author DNA aprovado | `authors/bea_halden/AUTHOR_VISUAL_DNA.v1.yaml` (`status: APPROVED`, 2026-09-14) |
| Capabilities não commitadas | `git status`: `?? docs/sdd/`, `?? engine/scripts/check_causal_ledger.py`, `?? engine/scripts/check_visual_canon.py`, `?? authors/`, `?? books/a-noiva-esquecida/`, `M engine/scripts/livingbook.py` |
| Nenhuma SDD de obra existe | `docs/sdd/` tem só as duas SDDs de capability + calibração; esta é a primeira SDD **de livro** |

### 2.2 Achados por área pedida (seção 30 da missão)

| Área | Componente real encontrado | Natureza / limite para NARCISO |
|---|---|---|
| LIVING_BOOK_ENGINE | `engine/ENGINE_GRAPH.yaml`, `livingbook.py::build_standard_graph` | DAG gerado do `BOOK_SPEC`; features condicionais |
| Especificações / SDDs | `docs/sdd/*.md`, `discovery-books/00–09` | padrão documental seguido aqui |
| World Bible / Character Bible | `T014_WORLD_BIBLE`, `T013_CHARACTER_BIBLE` (Markdown) | REUSE; camadas GT/SM/SP no ledger |
| Canon Registry | `canon/CANON_REGISTRY.yaml` (sem schema; varia por runtime) | `unknowns` + `prohibited_inferences` em `a_morte` (`CANON_REGISTRY.yaml:555,579`) = precedente exato para "Reflexo nunca explicado" |
| Plot Map | `T016_PLOT_DEPENDENCY_MAP` | REUSE; eventos `PLANNED` no ledger |
| Reader Vitals | `T032_READER_VITALS` (prosa, gap informacional) | REUSE; não é canon (SDD irmã, E.4) |
| Memory/Motif | `T035_MEMORY_MOTIF_MAP` (S/R/T/P/E), `MEMORY_STATE_VALUES` (`check_visual_canon.py:102`) | REUSE para evolução de símbolos |
| Reread | ledger `beliefs`, `--recontextualized`, L5 Second-Read; `eva/seeds/WORLD_RULES_SEED.md §8` ("Pistas de releitura — plantar, nunca resolver") | REUSE; **limite:** INV-11 exige que revisão de crença divulgue uma GT — incompatível com o Reflexo (2.4, D-N5) |
| Image pipeline | `T4NN_IMAGE_BRIEF → GENERATE → FACE_QA → CONTINUITY_QA → APPROVE` (`livingbook.py:492-494`), `generate_image.py` (`--reference`, `--edit`), `MODEL_TIERS.yaml:64-92` | **uma** imagem por capítulo, arquivo `chapter_NN.jpg` fixo (`KDP_LAYOUT_DEFAULTS.yaml:62-66`) |
| Visual canon | `FACE_CANON.md`, `CHARACTER_VISUAL_BIBLE.md` (`artifact_contracts.VISUAL_CANON`); `VISUAL_NARRATIVE_CANON.yaml` | faces: sim; corpo parcial/definhamento: não |
| Repetition detector | `detect_repetition.py` + `TEXT_QUALITY_DEFAULTS.yaml` (override por `book/text_quality.yaml`) | formulação, não significado — declarado no próprio script (linhas 12-21) |
| Genre guardians | `GENRE_GUARDIAN` (lê config inexistente — D6 da SDD irmã); guardiões por livro em `books/<slug>/agents/` | REUSE do padrão por livro |
| Dark Romance layer | `DARK_ROMANCE_CANON_ARCHITECT` (ledger), `BEA_HALDEN_AUTHORIAL_GOVERNANCE` (SDD irmã, S) | REUSE integral; "Reference Knowledge" é FUTURE e **não** é criado aqui |
| Consent | ledger L8 (`CONSENT_CANONICAL_VALUES`, `ABILITY_TO_REFUSE_VALUES`, `BOUNDARY_STATE_VALUES` — `check_causal_ledger.py:82-85`), `ANTI_MANIPULATION_GUARDIAN` (Tier S) | REUSE |
| Adult gate | `ADULT_EVENT_KINDS`, `MIN_ADULT_AGE = 18` (`check_causal_ledger.py:72-80`) | REUSE; precisa de regra complementar visual (seção 33) |
| Copyright/legal | `T600/T601/T602` em `GATE_LEGAL`; `T602` já recebe o canon visual quando a feature está ligada (`livingbook.py:502-509`); `IMITATION_PATTERN` (`check_visual_canon.py:119`) | REUSE |
| Manuscript validators | `books/eva-…/validators/validate_final_manuscript.py`, `books/a_morte…/validators/validate_book_dna.py` | precedente de validador de obra com léxico proibido |
| Book composer | `build_kdp_docx.py` (placements `OPEN`/`HINGE`/`AFTER` — linhas 71-74; `mirrorMargins` — linha 518; sigil acima do rótulo — `KDP_LAYOUT_DEFAULTS.yaml:80-84`) | **sem** capitular, **sem** pranchas por id, **sem** pares de spread declarados |
| Task graph / state machine | `runtime_taskgraph.py` (estados, gates, `custom_validators`, `requires_human_approval`) | REUSE |
| Configs | `EXECUTION_PROFILES.yaml` (DRAFT desliga `images`), `EDITION_CAPABILITIES.yaml`, `PRINT_GEOMETRY.yaml` | REUSE/EXTEND |
| Schemas | `engine/contracts/*.schema.json` — **não executados** (D2 irmã); templates YAML executáveis são o contrato real | seguir templates, não JSON Schema |
| Testes | `tests/test_*.py` (unittest, offline), goldens em `tests/fixtures/golden/*.json` | REUSE do padrão |
| Livros reais | 7 pacotes em `books/`; 6 runtimes | `a-noiva-esquecida` é o precedente mais próximo (Bea Halden, retelling, ledger + visual) |

### 2.3 Precedentes diretos de NARCISO

| Precedente | Evidência | O que prova |
|---|---|---|
| Retelling de domínio público com proveniência | `a-noiva-esquecida/planning/01_SOURCE_CANON.md` (edição-fonte datada, fontes, política `FOLKTALE_1852` × `BEA_HALDEN_ORIGINAL`, crédito de front matter) | o Myth Adaptation Contract tem forma pronta |
| Delta de adaptação + clean-room | `02_ADAPTATION_DELTA.md` (tabela raiz → transformação; "não pesquisar adaptações recentes"; auditoria compara **cadeia de cenas**) | `MYTH_ELEMENT -> BEA_HALDEN_REINTERPRETATION` já foi feito uma vez |
| Reflexo como motivo de Bea Halden | `a-noiva-esquecida/visual_profile.md` e `planning/10_VISUAL_MOTIF_MAP.md` ("reflexo: testemunha legal/ética — atraso → ausência → multiplicação") | **risco de autocanibalização**: NARCISO precisa de um reflexo **ontologicamente** diferente (seção 13.6) |
| Ambiguidade como regra bloqueante | `eva/immutable_rules.yaml` `IR002` (causa nunca confirmada), `IR006` (morte nem confirmada nem descartada), `IR015` (sem epílogo explicativo), `IR019` (hipótese só como inferência do leitor) | a Uncertainty Principle tem gramática de regra pronta |
| Guardião de ambiguidade | `eva/agents/mystery_ambiguity_guardian.toml` (Tier S; léxico proibido por capítulo; "distinguish observed chronology from character hypothesis and narrator truth") | REUSE do padrão, não do arquivo |
| Incógnitas canônicas | `a_morte/CANON_REGISTRY.yaml:555-590` (`UNK-* status: MUST_REMAIN_UNKNOWN`; `PRO-*` inferências proibidas) | "o motor sabe que não sabe" já é canon |
| Deterioração corporal com dignidade | `a_morte/immutable_rules.yaml` `IR011` ("Deterioração corporal não pode ser erotizada, fetichizada nem usada como espetáculo de horror") | NARCISO precisa de uma versão **mais fina**: erotismo e declínio coexistem por desenho (seção 11) |
| Consentimento pós-condição | `a-noiva-esquecida` `IR002`, cenas protegidas `FIRST_INTIMACY`, `BODY_MEMORY_BOUNDARY` (auditor `ANTI_MANIPULATION_GUARDIAN`) | padrão de cena íntima protegida |
| Prompt de ilustração com vetos e âncoras | `runtime/a_morte…/images/chapters/chapter_01/GENERATION_REPORT.md` (prompt, SHA-256, inspeção, handoff de QA); `output/eva-capitulos-v1/PROMPTS.md` (vetos repetidos por prompt) | contrato de prompt futuro (seção 16.6) |
| Identidade facial que sobreviveu 24 imagens | `FACE_CANON_TEMPLATE.md`; `MODEL_TIERS.yaml:71-78` ("regeneração por prompt textual falhou; `--reference` funcionou") | continuidade de Narciso deve ancorar em imagem aprovada |

### 2.4 Divergências e limites descobertos (registrados, não corrigidos)

| ID | Divergência / limite | Evidência | Impacto e decisão nesta SDD |
|---|---|---|---|
| D-N1 | `features.images.primary_per_chapter` não é lido por nenhum script; grafo gera 1 imagem por capítulo | grep em `engine/scripts` (só aparece nos `BOOK_SPEC`); `livingbook.py:492` | Illustration Canon exige EXTEND do compositor (Slice 4) |
| D-N2 | Classe `FIGURE` existe no vocabulário mas não tem regra própria (nem vínculo com `FACE_CANON`, nem `FIGURE_ON_COVER`) | `check_visual_canon.py:69`; grep por `FIGURE` só encontra a linha 69 | EXTEND (seção 25.4) |
| D-N3 | Papel `METAL` do Author DNA declara `material_family: WARM_METAL`, mas o validador não verifica família de material | `AUTHOR_VISUAL_DNA.v1.yaml:50`; grep `material_family` sem ocorrência no validador | prata/espelho **não** entra como `METAL`; entra como material de acabamento (seção 13.2, OQ-N6) |
| D-N4 | Não há capitular (drop cap) no builder DOCX | grep `drop|capitular` em `build_kdp_docx.py` sem ocorrência | tipografia narrativa de capitular é EXTEND opcional; KDP/Kindle precisam de fallback (seção 18.5) — **Slice 5: omitida** |
| D-N5 | Ledger: `truth ∈ {TRUE, INCOMPLETE, FALSE}` e INV-11 exige que revisão de crença divulgue GT | `check_causal_ledger.py:87`; SDD irmã H.1 | Reflexo **nunca** é modelado como crença revisada; só `left_open: true` (seção 9.5) |
| D-N6 | INV-06 reprova participante de evento adulto com `age: null` | `check_causal_ledger.py:72-80` | o Reflexo **nunca** é `participant` nem `character` no ledger (seção 9.5, 33) |
| D-N7 | No mito (Ovídio, *Met.* III), Narciso tem dezesseis anos | fonte clássica | idade canônica 27; proibição de codificação juvenil em texto e imagem (seção 33) |
| D-N8 | Author DNA v1: `forbid_literal_protagonist_on_cover: true` (default, não invariante) | `AUTHOR_VISUAL_DNA.v1.yaml:43`; SDD irmã 17.2 | Narciso na capa exige `role_overrides` + aprovação humana — **decidido**: fragmento do rosto (OQ-N1, seção 23.2) |
| D-N9 | Watchlist da autora contém `SHIRTLESS_MALE`, `BLOOD`, `GENERIC_COUPLE` | `AUTHOR_VISUAL_DNA.v1.yaml:83-91` | nudez artística de Narciso só com Chekhov `PROVEN`; nenhuma exceção (seção 14.9) |
| D-N10 | Perfil `DRAFT` desliga `images` | `EXECUTION_PROFILES.yaml:36-43` | NARCISO só é aceito em `STANDARD`/`PREMIUM`; `DRAFT` serve apenas para teste de texto |
| D-N11 | Fatos de fabricação KDP datados de 2026-09-14; hardcover com chaves `TO_VERIFY` | `EDITION_CAPABILITIES.yaml:33`; `PRINT_GEOMETRY.yaml:54-55` | nenhum acabamento é afirmado disponível sem `T699` (seção 22) |
| D-N12 | Kindle é refluível (interior entregue como DOCX): não há spread garantido | `build_kdp_docx.py`; SDD irmã OQ-10 | Book-as-Mirror tem manifestação por edição (seção 18.6) |
| D-N13 | Imagens de capítulo só começam depois de `GATE_FULL_MANUSCRIPT` | `livingbook.py:493` | correto para ilustração `FORESHADOW`, mas o **planejamento** das ilustrações precisa entrar no canon visual em `GATE_LIVING_BOOK` (seção 28) |
| D-N14 | Working tree com capabilities não commitadas | `git status` | pré-condição de todo slice que toque o motor: commit + goldens estáveis |
| D-N15 | `GENRE_GUARDIAN` lê configuração que nenhum `BOOK_SPEC` declara | D6 da SDD irmã | NARCISO não depende dele para nenhuma regra bloqueante |

---

## 3. Existing Architecture Map

### 3.1 Camadas e onde NARCISO entra

```text
ENGINE (neutro)             engine/ENGINE_GRAPH.yaml · scripts · templates · 66 agentes
   │                        + capability DARK_ROMANCE_CANON_ARCHITECT   (features.causal_ledger)
   │                        + capability BEA_HALDEN_VISUAL_NARRATIVE     (features.visual_narrative)
   ▼
AUTHOR (catálogo)           authors/bea_halden/AUTHOR_VISUAL_DNA.v1.yaml  (camada A, imutável, pinada)
   ▼
BOOK PACKAGE                books/narciso/   ← ESTA SDD DEFINE
   │   BOOK_SPEC · CONSTITUTION · immutable_rules · protected_scenes · chapter_architecture
   │   planning/ · seeds/ · agents/ · validators/ · BOOK_GRAPH (additional_tasks, gate_extensions)
   ▼  compose
RUNTIME                     runtime/narciso/
       canon/CANON_REGISTRY.yaml            (CANON_GUARDIAN)
       canon/CAUSAL_LEDGER.yaml             (CANON_GUARDIAN)
       canon/NARCISO_INTERPRETIVE_CANON.yaml (CANON_GUARDIAN)     ← único canon novo, específico da obra
       canon/VISUAL_NARRATIVE_CANON.yaml    (VISUAL_DIRECTOR)
       images/canon/FACE_CANON.md · CHARACTER_VISUAL_BIBLE.md (FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT)
```

### 3.2 Ciclo de vida relevante (grafo gerado hoje, com as duas features ligadas)

```text
GATE_BOOTSTRAP
 → CANON  T010 brief → T011 story → T012 world rules → T013 CHARACTER_BIBLE → T014 world
          → T015 SYMBOL_BIBLE → T016 PLOT_DEPENDENCY_MAP → T017 TIMELINE
          → T018 CANON_REGISTRY (+ ledger) → T019 CANON_REVIEW          ⇒ GATE_CANON  [V_CAUSAL_LEDGER_PLAN, humano]
 → T021 LEDGER_SNAPSHOT · T020 CANON_DIGEST
 → LIVING_BOOK T030..T041 (T035 MOTIF_MAP, T036 VISUAL_LIFE_SPEC, T038 FACE_CANON, T039 CHARACTER_VISUAL_BIBLE)
          + T042 VISUAL_DISCOVERY → T043 VISUAL_NARRATIVE_CANON → T044 snapshot
                                                                       ⇒ GATE_LIVING_BOOK [V_VISUAL_CANON_PLAN]
 → T1NN BRIEF_CHAPTER                                                  ⇒ GATE_CHAPTER_BRIEFS
 → T156/T157 VOICE                                                     ⇒ GATE_VOICE [humano]
 → WAVES: PREFLIGHT → WRITE → MERGE → REVIEW → REVISION → CANON_UPDATE ⇒ GATE_WAVE_n [V_CAUSAL_LEDGER_WAVE_n]
 → INTEGRATION T300..T310 FREEZE → T311 VISUAL_STATE_REALIZATION → T312 snapshot
                                                                       ⇒ GATE_FULL_MANUSCRIPT [ledger final, visual realized, humano]
 → VISUAL_PRODUCTION T4NN (1 por capítulo)                             ⇒ GATE_VISUAL
 → LEGAL T600..T604 (T602 lê canon visual)                             ⇒ GATE_LEGAL
 → KDP T698 EDITION_PLAN · T699..T706 · T707 PRINT_GEOMETRY            ⇒ GATE_KDP [V_VISUAL_EDITION]
 → DELIVERY T800..T805                                                 ⇒ GATE_MEDIA_ASSETS [V_VISUAL_ASSETS] ⇒ GATE_DELIVERY
```

### 3.3 Mecanismos de extensão que esta SDD usa (e só estes)

| Mecanismo | Onde | Uso em NARCISO |
|---|---|---|
| Campos extras em `chapter_architecture.yaml` | precedente `pov`, `irreversible_turn`, `dramatic_question`, `continuity` (noiva) | `desire_stage`, `mirror_of`, `reflection_presence`, `love_evidence`, `illustration_slots` |
| `BOOK_GRAPH.additional_tasks` / `gate_extensions` / `custom_validators` | `livingbook.py:589-592`; `a_morte/BOOK_GRAPH.yaml` | 2 tarefas da obra; validador da obra em 4 gates existentes |
| Guardião por obra | `books/<slug>/agents/*.toml` | `NARCISSUS_AMBIGUITY_GUARDIAN`, `DESIRE_DECAY_GUARDIAN` |
| Validador por obra | `books/<slug>/validators/*.py` | `validate_narciso.py` |
| `book/text_quality.yaml` | override de `TEXT_QUALITY_DEFAULTS.yaml` | clichês de beleza masculina e de dark romance |
| `quality_profile.yaml` | scores e riscos por livro | métricas diagnósticas de NARCISO |
| `CANON_PROPOSAL_PROTOCOL` | `ENGINE_GRAPH.protocols` | toda mutação de canon interpretativo |
| Aprovação humana por decisão com hash | `project_state/APPROVALS/VISUAL/APR-*.md` | capa, arte-herói, nudez, reflexos-chave |
| `role_overrides` com razão e aprovação | Author DNA / canon visual | Narciso na capa (se aprovado) |

---

## 4. REUSE / EXTEND / CREATE Matrix

Legenda: uma decisão por linha. "Motor" = alteração em `/engine` (sempre neutra
de gênero e OFF por padrão). "Obra" = arquivo em `books/narciso/`.

### 4.1 Narrativa

| Requirement | Existing Component | Decision | Reason |
|---|---|---|---|
| Myth DNA preservado | `planning/01_SOURCE_CANON.md` + `02_ADAPTATION_DELTA.md` (noiva) | **REUSE** (padrão) → CREATE conteúdo na Obra | forma já validada num livro Bea Halden real |
| `MYTH_ELEMENT -> REINTERPRETATION` verificável | tabela Markdown (noiva) | **EXTEND** (Obra) | versão YAML curta checada por `validate_narciso.py --mode package` (`MYTH_DNA_LOST`) |
| Personagens causais (GT/SM/SP) | ledger `characters[]` | **REUSE** | LAW 01 já cobre |
| Relação Narciso↔Eco com memória | ledger `relationships` + deltas | **REUSE** | LAW 02 |
| Reflexo nunca explicado | `unknowns` + `prohibited_inferences` (a_morte); `IR002/IR019` (eva) | **REUSE** (forma) | regra imutável + incógnita canônica + inferências proibidas |
| Evidência sustenta ≥2 hipóteses | — | **CREATE** (Obra) | nenhum artefato verificável existe; `NARCISO_INTERPRETIVE_CANON.reflection_evidence` |
| Ambiguidade de amor | ledger `beliefs` (`left_open`) | **EXTEND** (Obra) | crenças não guardam leitura dupla com força; `love_readings` no canon interpretativo |
| Motivo de Narciso sem resolver o amor | ledger GT `kind: CONTRADICTION` | **REUSE** | a verdade do motor **é** a contradição (seção 10.3) |
| Curva de desejo/definhamento | ledger L6 `emotional_movement` | **EXTEND** (Obra) | L6 mede intensidade; NARCISO precisa de estágio monotônico → campo `desire_stage` + regra da obra |
| Repetição muda significado | `detect_repetition.py`, `EMOTIONAL_REPETITION_AUDITOR` | **EXTEND** (Obra) | detector vê formulação; `desire_occurrences[]` com função única e teto de explicitude |
| Consentimento | ledger L8 + `ANTI_MANIPULATION_GUARDIAN` | **REUSE** | integral |
| Idade adulta | ledger INV-06 | **REUSE** + **EXTEND** (Obra) | regra adicional para Reflexo, hipóteses e codificação visual |
| Releitura | ledger L5 + `--recontextualized` + `MEMORY_MOTIF_MAP` | **REUSE** + **EXTEND** (Obra) | pistas ambíguas não "revisam"; `reread_clues[]` ligam texto, arte e hipóteses |
| Final ambíguo com nova evidência | `IR006`, `IR015` (eva) | **REUSE** (forma) | regras imutáveis da obra |
| Cenas protegidas | `protected_scenes.yaml` + `T32NN` | **REUSE** | 12 cenas (seção 7.6) |
| Voz Bea Halden para NARCISO | `T156_BUILD_VOICE_REFERENCE`, `LITERARY_STYLE_GUARDIAN`, `book/text_quality.yaml` | **REUSE** + CREATE conteúdo (Obra) | SDD irmã S.4: Bea Halden **não** é template de estilo; perfil é da obra |
| Dark Romance expert layer | ledger + governança Bea Halden | **REUSE** | "Reference Knowledge" é FUTURE nas SDDs irmãs — **DO NOT CREATE** |
| Guardiões de gênero específicos | padrão `books/<slug>/agents/` | **CREATE** (Obra, 2) | ambiguidade dupla e desejo/definhamento exigem critérios que nenhum `.toml` genérico carrega |

### 4.2 Visual

| Requirement | Existing Component | Decision | Reason |
|---|---|---|---|
| Identidade Bea Halden | `AUTHOR_VISUAL_DNA.v1.yaml` | **REUSE** | pin v1; nenhuma mudança na camada A |
| Visual Bible de NARCISO | `visual_profile.md` → `VISUAL_LIFE_SPEC`, `IMAGE_BIOME` | **REUSE** + CREATE conteúdo (Obra) | `planning/NARCISSUS_VISUAL_BIBLE.md` alimenta T036/T037/T042 |
| Paleta | `book_dna.palette` dentro dos papéis | **REUSE** | preto/marfim/ouro/vinho cabem nos papéis; prata não (D-N3) |
| Prata/espelho | `finish_intents.semantic_material` | **EXTEND** (valor novo de material) | não viola papel `METAL`; é acabamento com significado |
| Narcissus Visual DNA (rosto) | `FACE_CANON_TEMPLATE.md` + `T038` | **REUSE** | código `FV-NARCISO-01` |
| Corpo parcial reconhecível | — | **EXTEND** (Obra no FACE_CANON; Motor em `FIGURE`) | âncoras de mão/ombro/cabelo/olho + regra `FIGURE_WITHOUT_IDENTITY_REF` |
| Definhamento visual | canon visual `states/transitions` | **REUSE** | `FIG-NARCISO` com estados ancorados em eventos (seção 17.3) |
| Reflection rules visuais | — | **CREATE** (Obra) + **EXTEND** (Motor: campo genérico `reflection_state`? não) | enum de estado de reflexo fica na Obra (`ext.narciso`); motor só aceita bloco de extensão |
| Symbol registry com evolução | `elements[]` + `states` + `MEMORY_MOTIF_MAP` | **REUSE** | 7 símbolos (seção 15) |
| Illustration canon (metadados) | `compositions[]` (`surface`, `elements`, `exposure`, `approval`) | **EXTEND** (Motor) | bloco genérico `illustration {category, text_relation, callback_of, anchor}` |
| Categorias HERO/CHAPTER/SYMBOL/REFLECTION/BODY/DECAY/CALLBACK | — | **CREATE** (Obra) | vocabulário declarado pela obra; motor valida só que existe |
| Mais de uma ilustração por capítulo | `T4NN` (1 por capítulo) | **EXTEND** (Motor) | tarefas por id de composição (`T45xx`), OFF quando canon não declara pranchas |
| Relação texto×imagem (COMPLEMENT/CONTRADICT/FORESHADOW) | — | **EXTEND** (Motor, enum genérico) | conceito literário neutro de gênero |
| Spoiler de ilustração | V5 (`exposure`, `reveal`, `CHAPTER_SCOPED_SURFACES`) | **REUSE** | integral |
| Continuidade de imagem | `T4NN_FACE_QA`, `T4NN_CONTINUITY_QA`, `--reference` | **REUSE** | integral, com checklist de reflexo (seção 25.5) |
| Capa | `compositions[FRONT_COVER]`, V4 thumbnail, `build_cover_and_stories.py` | **REUSE** | integral |
| Capa como armadilha (dualidade) | `book_dna.duality` + `reading_layer` + DJ-01..05 | **REUSE** | a armadilha é exatamente `OUTER_TRUTH`/`HIDDEN_TRUTH` |
| Chapter sigil | `SIGIL` + estados + `KDP_LAYOUT.chapter_opening.sigil` | **REUSE** | `SIG-ESPELHO` (seção 17.4) |
| Capitular narrativa | — | **EXTEND** (Motor, opcional) | builder sem drop cap (D-N4); fallback tipográfico simples |
| Spreads espelhados | `OPEN` (verso antes da abertura recto) + `start_on_recto` | **REUSE** + **EXTEND** (Motor: `pair_with`) | o spread imagem-verso/abertura-recto já existe; pares distantes precisam de declaração |

### 4.3 Objeto físico e produção

| Requirement | Existing Component | Decision | Reason |
|---|---|---|---|
| Matriz de viabilidade | `EDITION_CAPABILITIES.yaml` | **REUSE** | KDP × collector com proveniência |
| Efeitos de espelho, slipcase, cards, marcadores | — | **EXTEND** (Motor, dados) | novas chaves `VENDOR_DEPENDENT`; zero código de regra nova além do resolvedor existente |
| Promessa de acabamento honesta | `FINISH_PROMISE_MISMATCH` (V7) | **REUSE** | integral |
| Geometria de capa | `PRINT_GEOMETRY.yaml`, `T707` | **REUSE** | hardcover segue `TO_VERIFY` |
| Collector manifest e máscaras | `PRODUCTION_MANIFEST`, `PRINTER_PROFILE` | **REUSE** | integral |
| Aroma | — | **DO NOT CREATE** | fora do motor; checklist de pesquisa humana (seção 21.5) |
| Social object map | Stories `T802` + V5 público | **EXTEND** (Obra) | lista de artefatos compartilháveis com teto de spoiler |
| Edição numerada/assinatura | — | **DO NOT CREATE** (motor) | decisão comercial humana; registrada em `PRODUCTION_MANIFEST.printer_instructions` |

### 4.4 Governança e validação

| Requirement | Existing Component | Decision | Reason |
|---|---|---|---|
| Gates pedidos (16) | 17 gates existentes + validadores | **REUSE** | **0 gates novos**; ver seção 26 |
| Métricas | `quality_profile.yaml` + contagens determinísticas | **REUSE** + **EXTEND** (Obra) | nenhum score "de desejo" automatizado |
| Canon interpretativo | `CANON_REGISTRY` / ledger | **CREATE** (Obra; 1 arquivo) | não cabe no ledger (leituras ≠ fatos) nem no registry (sem schema) |
| Governança do canon interpretativo | `CANON_WRITE`, `CANON_GUARDIAN`, `CANON_PROPOSALS` | **REUSE** | mesmo dono, mesmo lock, mesmo protocolo |
| Checkpoints humanos | `EXECUTION_PROFILES.human_checkpoints` | **REUSE** | perfil `PREMIUM` recomendado |
| Motor de ambiguidade genérico | — | **DO NOT CREATE** (agora) | três precedentes em prosa + NARCISO estruturado = candidato real; promover só depois de NARCISO provar (OQ-N10) |

---

## 5. NARCISO Product Thesis

### 5.1 Tese

> **NARCISO não é apenas um livro para ser lido. É um livro para ser
> desejado, tocado, observado, colecionado e possuído.**

A experiência física e visual **é narrativa**. A contradição é deliberada:
quanto mais o romance mostra que a obsessão pela beleza destrói, mais belo o
objeto se torna. O leitor critica Narciso enquanto reproduz seu comportamento
— volta à ilustração, inclina a capa contra a luz, fotografa, exibe, deseja
uma edição mais bonita.

> **O leitor deve perceber tarde demais que também esteve olhando para Narciso.**

### 5.2 Sequência de impulsos (critério de produto)

```text
OLHAR → TOCAR → POSSUIR → (só então) LER
```

| Impulso | Onde é produzido | Mecanismo existente | Verificação |
|---|---|---|---|
| OLHAR | capa, lombada, miniatura | `compositions[FRONT_COVER]`, V4 thumbnail | V4 + checkpoint humano ("eu quero esse livro") |
| TOCAR | acabamento, relevo simulado/físico, papel | `finish_intents` + `EDITION_PLAN` | V7 + prova física (humano) |
| POSSUIR | coerência de coleção, arte-herói, capa nua, guardas | `duality`, `collector`, `SHAREABLE_ARTIFACT_MAP` | V5/V7/V8 + humano |
| LER | gancho do Coro no capítulo 1 | `protected_scenes: CHORUS_FIRST_GAZE` | auditoria de cena + `GATE_VOICE` |

### 5.3 As três perguntas pós-livro (critério narrativo)

| Momento | Pergunta | Sustentada por |
|---|---|---|
| DURANTE | Quem é o Reflexo? | Uncertainty Principle (seção 9) |
| AO TERMINAR | Narciso amou alguém? | Love Ambiguity System (seção 10) |
| DIAS DEPOIS | Por que eu também fiquei fascinado por Narciso? | Coro em primeira pessoa do plural + Book-as-Mirror + Reread Layer (seções 7.3, 18, 20) |

A terceira é o triunfo da obra e **não é mensurável pelo motor**. O motor
garante as condições estruturais; o veredito é humano (seção 34.3).

### 5.4 Paradoxo de produto como regra de engenharia

A tese cria um risco real: um objeto desenhado para ser desejado pode
**glamourizar** o que o romance critica (obsessão, definhamento). Resolução
formal adotada em toda esta SDD:

```text
A BELEZA DO OBJETO PODE SEDUZIR.
A BELEZA DO OBJETO NUNCA PODE PROMETER QUE A DESTRUIÇÃO É BELA.
```

Operacionalmente: a arte do definhamento migra do **corpo** para os
**vestígios** (seção 14.7); o erotismo decresce enquanto o declínio cresce
(seção 11); nenhuma superfície pública mostra estágio de degradação
(seção 26.1).

---

## 6. Myth Adaptation Contract

### 6.1 Fonte e hierarquia (padrão `01_SOURCE_CANON.md` da noiva)

| Nível | Fonte | Uso permitido |
|---|---|---|
| `SOURCE_CANON` | Ovídio, *Metamorphoses*, livro III (Eco e Narciso), texto latino | motivos, estrutura mítica, citação só em tradução **própria** e curta |
| `SOURCE_VARIANT` | Cônon, *Narrativas* 24 (Amínias) | raiz da hipótese concorrente `H-OTHER`; nunca como "resposta" |
| `EXCLUDED_VARIANT` | Pausânias, *Descrição da Grécia* IX.31 (variante da irmã gêmea) | **não usada** — decisão humana OQ-N2: não existe hipótese de gêmeo na obra |
| `ICONOGRAPHY_PD` | pinturas anteriores ao século XX amplamente em domínio público (ex.: Caravaggio, Waterhouse) | **somente** estudo de tradição; composição nunca reproduzida (seção 32) |
| `PROHIBITED_REFERENCE` | adaptações, traduções, ilustrações e obras modernas sobre Narciso/Eco ainda protegidas | não consultar durante arquitetura, prosa ou arte (clean-room da noiva) |
| `BEA_HALDEN_ORIGINAL` | tudo que a tabela 6.3 marca como reinterpretação | é o livro |

A verificação de proveniência de qualquer tradução usada é tarefa de
`T601_LEGAL_GLOBAL` + `T602_ORIGINALITY_AUDIT`. Esta SDD **não** afirma status de
domínio público de nenhuma tradução específica.

### 6.2 `ORIGINAL_MYTH_DNA`

| ID | Elemento do mito | Por que é DNA (sem ele não é Narciso) |
|---|---|---|
| `MYTH-01` | Narciso | nome e figura central |
| `MYTH-02` | beleza extraordinária | motor do desejo alheio |
| `MYTH-03` | admiradores | o olhar dos outros |
| `MYTH-04` | rejeição | a crueldade que gera maldição |
| `MYTH-05` | Eco | a voz que só devolve |
| `MYTH-06` | reflexo | o objeto impossível |
| `MYTH-07` | água | superfície que mostra e não entrega |
| `MYTH-08` | impossibilidade de possuir o contemplado | o centro trágico |
| `MYTH-09` | definhamento | o corpo que se consome |
| `MYTH-10` | flor narciso | o que resta |
| `MYTH-11` | morte/transformação | desaparecimento sem corpo |
| `MYTH-12` | identidade / profecia ("se não se conhecer") | o conhecimento de si como ameaça |
| `MYTH-13` | amor impossível | a pergunta que sobrevive |
| `MYTH-14` | maldição do admirador rejeitado / Nêmesis | a causa aparente |

### 6.3 `MYTH_ELEMENT -> BEA_HALDEN_REINTERPRETATION`

| Myth DNA | Raiz no mito | Reinterpretação de Bea Halden | Transformação dominante |
|---|---|---|---|
| `MYTH-01` | jovem filho de Cefiso e Liríope | **Narciso Céfiso**, 27, herdeiro da pedreira de mármore alagada da família | contemporânea/gótica |
| `MYTH-02` | beleza que ninguém resiste | beleza que **ele nunca pôde ver**: cresceu numa casa de espelhos cobertos; conhece o próprio rosto apenas pelo desejo dos outros | psicológica |
| `MYTH-03` | ninfas e jovens | o **Coro**: galeristas, colecionadores, fotógrafos, desconhecidos — narram capítulos em "nós" e implicam o leitor | metanarrativa |
| `MYTH-04` | Narciso rejeita todos | rejeições precisas e cruéis, que podem ser proteção ou desprezo (seção 10) | ambígua |
| `MYTH-05` | Eco, que só repete | **Elisa "Eco" Varela**, 31, dubladora e restauradora de áudio contratada para digitalizar o arquivo sonoro da casa; profissão de repetir vozes alheias; fala pouco e responde mais do que inicia — traço de personagem, **não** maldição | contemporânea |
| `MYTH-06` | reflexo na fonte | o **Reflexo**: presença em água, vidro, mármore polido, tela apagada; nunca explicado (seção 9) | fantástica/psicológica |
| `MYTH-07` | fonte intocada | a **Pedreira Alagada**: cava de mármore negro inundada, água parada como espelho; proibida a Narciso desde a infância | gótica |
| `MYTH-08` | não pode tocar a imagem | toda tentativa de toque chega um instante adiantada ou atrasada (`RFX-07`) | horror de identidade |
| `MYTH-09` | definha à beira da fonte | compulsão, insônia, fome, recusa de ajuda; corpo que se torna estátua | corporal/psicológica |
| `MYTH-10` | flor surge no lugar do corpo | um narciso branco nasce da rachadura da estátua de mármore negro, onde não há terra (`RFX-14`) | fantástica ambígua |
| `MYTH-11` | corpo desaparece | Narciso desaparece; nenhum corpo; nenhuma confirmação de morte | ambígua |
| `MYTH-12` | profecia de Tirésias | **Teodoro Braga**, 78, restaurador cego que esculpe pelo toque, disse a Lia: "Viverá muito, se não se conhecer" | contemporânea |
| `MYTH-13` | ama o que não pode ter | ama Eco? ama o Reflexo? ama só a si? — nunca respondido | ambígua |
| `MYTH-14` | Amínias/Nêmesis amaldiçoa | **Amintas Rocha**, 34, escultor rejeitado, desaparecido antes do capítulo 1; deixa uma estátua inacabada de Narciso em mármore negro do **Veio Nêmesis** e uma inscrição na base | gótica |

### 6.4 A implicação obscura (o que o livro "descobre" dentro do mito)

> **Narciso não se apaixonou por si mesmo porque se amava. Apaixonou-se
> porque nunca tinha visto a si mesmo — só o desejo dos outros. O reflexo
> foi o primeiro olhar que não queria nada dele. Ou foi o primeiro que
> queria tudo.**

Esta frase é **tese interna** (vive em `BOOK_CONSTITUTION.md`), nunca
enunciada no manuscrito.

### 6.5 Regras do contrato

| ID | Regra | Verificação |
|---|---|---|
| `MAC-01` | Todo `MYTH-*` tem ≥1 reinterpretação ancorada em ≥1 capítulo e ≥1 evento/cena | `validate_narciso.py --mode package` → `MYTH_DNA_LOST` (HIGH) |
| `MAC-02` | Nenhuma reinterpretação é tradução literal de cena do mito (ex.: Eco repetindo mecanicamente a última palavra por encanto) | `NARCISSUS_AMBIGUITY_GUARDIAN` + `T602` (cadeia de cenas) |
| `MAC-03` | Nenhuma variante (`SOURCE_VARIANT`) é confirmada como verdade da obra | regra imutável `IR-N03` |
| `MAC-04` | Clean-room: nenhuma adaptação moderna é citada em `planning/`, briefs ou prompts | `IMITATION_REFERENCE` + busca de nomes no validador da obra |
| `MAC-05` | Crédito de front matter aprovado por humano, no padrão da noiva | `planning/01_SOURCE_CANON.md` |

Crédito proposto (sujeito a `T601`):

> "Esta obra é uma releitura adulta e livre de motivos do mito de Eco e
> Narciso, preservado nas *Metamorfoses* de Ovídio. *Narciso* desenvolve
> personagens, ambientação, conflitos e linguagem próprios."

---

## 7. Narrative Canon

> Todo o conteúdo desta seção é **proposta de canon** (`status: PROPOSED`).
> Vira canon somente em `GATE_CANON` com aprovação humana, pelo fluxo
> existente (`T010..T019`). Nenhuma prosa é escrita aqui.

### 7.1 Premissa

No Vale do Cefiso, uma região fictícia de mármore em declínio, a família
Céfiso deixou a pedreira alagar. Narciso cresceu na casa à beira da cava
inundada com todos os espelhos cobertos por ordem da mãe. Quando o escultor
que o usava como modelo desaparece perto da água, deixando uma estátua
inacabada de Narciso, e uma restauradora de áudio chega para digitalizar as
fitas antigas da casa, Narciso desce pela primeira vez, adulto, até a água
proibida — e alguma coisa olha de volta.

### 7.2 Logline

Um homem que nunca pôde ver o próprio rosto encontra, na água de uma pedreira
inundada, a única presença que não o deseja — ou que o deseja inteiro — e
começa a desaparecer dentro dela, enquanto a mulher que o ama grava tudo.

### 7.3 Arquitetura estrutural — o livro palíndromo

- **33 capítulos**, **centro no capítulo 17** ("O Centro").
- **Espelho estrutural:** o capítulo `n` reflete o capítulo `34 − n`
  (`mirror_of`). Pares não repetem conteúdo; **invertem** situação, ponto de
  vista ou significado.
- **Três atos**:
  - **I — A SUPERFÍCIE** (1–11): contemplação, curiosidade, atração.
  - **II — O ESPELHO** (12–22): excitação, ritual, compulsão.
  - **III — O FUNDO** (23–33): dependência, degradação, definhamento.
- **POV:** terceira pessoa limitada a Narciso ou Eco (um POV por capítulo);
  capítulo 25 em Lia; capítulos **1, 11, 23, 33** em primeira pessoa do
  plural do **Coro** — admiradores que nunca acessam a mente de Narciso.
  O Coro é o dispositivo pelo qual o leitor passa a olhar junto.
- **Extensão proposta:** 80.000–95.000 palavras.
- **Tempo:** do fim do outono à primeira floração de narcisos.
- **Sem prólogo, sem epílogo, sem nota explicativa final** (`IR-N09`).

### 7.4 `chapter_architecture` proposto

Campos novos por capítulo (padrão de campos extras já usado pela noiva):
`desire_stage`, `mirror_of`, `reflection_presence` (`NONE|TRACE|PRESENT`),
`love_evidence` (id ou vazio), `illustration_slots` (ids planejados, seção 16).

| # | Título | Ato | POV | `desire_stage` | Função | Virada irreversível | `mirror_of` |
|---|---|---|---|---|---|---|---|
| 1 | Nós o Vimos Primeiro | I | Coro | CONTEMPLATION | Na apresentação da estátua inacabada de Amintas, o Coro descreve Narciso e nota que ele nunca olha vidro | Narciso sai sem olhar a estátua; Amintas é dado como desaparecido | 33 |
| 2 | A Casa dos Espelhos Cobertos | I | Narciso | CONTEMPLATION | Volta à casa; Lia; lençóis sobre espelhos; chegada de Eco | O carro de Amintas é encontrado na estrada da pedreira | 32 |
| 3 | Repetir | I | Eco | CONTEMPLATION | Eco digitaliza fitas; numa gravação de infância, a voz do menino fala com alguém que não responde — ou responde baixo demais | Eco decide estender o contrato | 31 |
| 4 | O Cego que Esculpe pelo Toque | I | Narciso | CURIOSITY | Teodoro toca a estátua e diz que o rosto está "inacabado do lado errado" | Narciso ouve a frase da profecia | 30 |
| 5 | A Recusa | I | Eco | CURIOSITY | Aproximação de Eco; rejeição pública e precisa (`LOVE-E1`) | Eco é humilhada diante do Coro | 29 |
| 6 | Água Proibida | I | Narciso | CURIOSITY | Primeira descida adulta à cava; primeira presença na água (`RFX-02`) | Narciso volta na noite seguinte | 28 |
| 7 | Através das Paredes | I | Eco | ATTRACTION | Eco ouve Narciso falar à noite; o gravador registra só a voz dele | Eco escolhe continuar gravando — e esconde isso | 27 |
| 8 | O Rosto que Atrasa | I | Narciso | ATTRACTION | Na janela, a figura pisca um instante depois; a pinta parece do lado errado (`RFX-03`) | Narciso descobre o primeiro espelho da casa | 26 |
| 9 | O Arquivo de Lia | I | Eco | ATTRACTION | Diário da mãe: "cobri os espelhos para que ele não o visse" (`RFX-04`) | Eco arranca e guarda a página | 25 |
| 10 | Ouro em Folha | I | Narciso | ATTRACTION | Íris fotografa Narciso dourado para a campanha de restauro; as fotos não concordam entre si (`RFX-05`) | Narciso destrói as fotos, menos uma | 24 |
| 11 | O Que Vimos na Superfície | I | Coro | ATTRACTION | Ele está mais belo; um de nós o seguiu até a água e o viu conversando (`RFX-06`) | O Coro passa a vigiar a pedreira | 23 |
| 12 | Descoberta | II | Narciso | EXCITATION | Primeira ocorrência erótica diante do reflexo (`DSR-1 DISCOVERY`) | Ele não consegue não voltar | 22 |
| 13 | A Voz Guardada | II | Eco | EXCITATION | Eco descobre que Narciso guarda e ouve as gravações dela (`LOVE-E2`) | Confronto sem confissão | 21 |
| 14 | Mármore Negro | II | Narciso | EXCITATION | Na base da estátua, a inscrição de Amintas; quando Eco toca o rosto de pedra, Narciso o quebra (`LOVE-E3`) | O rosto da estátua racha | 20 |
| 15 | Prazer | II | Narciso | RITUAL | Segunda ocorrência (`DSR-2 PLEASURE`); espelhos migram para o quarto | A ala de Narciso fica sem nenhum espelho coberto | 19 |
| 16 | A Dívida Paga | II | Eco | RITUAL | Eco descobre que foi Narciso quem pagou anonimamente a internação da mãe dela (`LOVE-E4`) | Eco fica — por gratidão ou por escolha | 18 |
| 17 | O Centro | II | Narciso | RITUAL | Tentativa de tocar o Reflexo; as mãos não chegam juntas (`RFX-07`); uma gota cai | O espelho quebra; a cicatriz da palma reabre | 17 |
| 18 | Uma Noite sem Palavras | II | Eco | RITUAL | Narciso pede que ela fique e não fale; consentimento negociado e revogável (`LOVE-E5`) | Eco diz uma palavra; ele se afasta | 16 |
| 19 | Rito | II | Narciso | COMPULSION | Terceira ocorrência (`DSR-3 RITUAL`): hora, água, ouro, velas | Narciso cancela o mundo de fora | 15 |
| 20 | O Segundo Respirar | II | Eco | COMPULSION | A gravação do quarto mostra duas respirações fora de fase (`RFX-08`) | Eco decide ir embora e não vai | 14 |
| 21 | Cópias | II | Narciso | COMPULSION | Narciso ensaia as falas de Eco; as fitas dela passam a responder às dele | Eco se ouve repetida e deixa de reconhecer a própria voz | 13 |
| 22 | Necessidade | II | Narciso | DEPENDENCE | Quarta ocorrência (`DSR-4 NEED`): menos prazer, mais custo | Narciso tranca-se na sala de espelhos e entrega a chave a Eco | 12 |
| 23 | O Que Vimos no Fundo | III | Coro | DEPENDENCE | Uma foto de longe mostra a margem com uma figura e um reflexo em ângulo impossível — ou só granulação (`RFX-11`) | A obsessão do Coro vira peregrinação | 11 |
| 24 | A Fotografia que Ficou | III | Narciso | DEPENDENCE | Narciso entrega a única foto guardada (`LOVE-E9`) | Não resta imagem dele fora da água | 10 |
| 25 | O Que Lia Cobriu | III | Lia | DEPENDENCE | Três versões incompatíveis da origem das regras da casa — doença de família, lenda da água da cava, profecia do autoconhecimento —, cada uma com um documento; nenhuma envolve gêmeo (`RFX-12`) | Lia queima o diário | 9 |
| 26 | Ciúme do Vidro | III | Narciso | DEGRADATION | Quando o reflexo de Eco surge ao lado do seu, a figura parece olhá-la; Narciso a tira do quadro (`LOVE-E6`, `RFX-13`) | Eco deixa a casa | 8 |
| 27 | Degradação | III | Narciso | DEGRADATION | Quinta ocorrência (`DSR-5 DEGRADATION`); fome, frio, compulsão sem gozo | Narciso para de dormir e de responder | 7 |
| 28 | A Última Água | III | Eco | DEGRADATION | Eco volta e o vê de longe à beira da cava | Eco decide entrar na casa de novo | 6 |
| 29 | A Segunda Recusa | III | Narciso | WITHERING | Eco oferece tirá-lo dali; ele recusa (`LOVE-E7`) | A recusa agora custa a ele | 5 |
| 30 | Tirésias Toca o Mármore | III | Eco | WITHERING | Teodoro toca o rosto de Narciso: "Este não é o rosto que esculpiram." (`RFX-09`) | Teodoro recusa voltar | 4 |
| 31 | Quase Nada | III | Narciso | WITHERING | Sexta ocorrência (`DSR-6 ABSENCE`); ao amanhecer, ele chama um nome e a resposta volta (`LOVE-E8`) | A cena termina antes de qualquer resolução | 3 |
| 32 | A Casa dos Espelhos Descobertos | III | Eco | WITHERING | Busca; nenhum corpo; espelhos frente a frente; o narciso na rachadura da estátua (`RFX-14`) | Eco não colhe a flor | 2 |
| 33 | Nós Ainda Olhamos | III | Coro | WITHERING | Visitantes fotografam a cava; uma foto publicada mostra algo na água que o Coro não consegue concordar em nomear (`RFX-15`) | A última evidência é entregue; nenhuma é resolvida | 1 |

### 7.5 Final (contrato)

| Deve preservar | Deve evitar |
|---|---|
| destino ambíguo de Narciso | "era tudo alucinação" |
| Reflexo inexplicado | "era um fantasma" |
| possibilidade de continuidade | "era outra pessoa" |
| dúvida sobre amor | "era Narciso" |
| sensação de perda | morte confirmada ou sobrevivência confirmada |
| inquietação | epílogo, nota, glossário ou explicação posterior à última imagem |

**Última evidência (capítulo 33):** uma fotografia amadora publicada por um
visitante. Candidatas alternativas registradas para decisão humana (OQ-N9):
`F-A` a flor na rachadura (hoje em 32), `F-B` um reflexo a menos no corredor de
espelhos, `F-C` a fotografia do Coro. Regra: **exatamente uma** nova evidência
no último capítulo, compatível com ≥3 hipóteses.

### 7.6 Cenas protegidas propostas (`protected_scenes.yaml`)

| id | Capítulos | Auditor | Deve preservar | Rejeitar se |
|---|---|---|---|---|
| `CHORUS_FIRST_GAZE` | 1 | `NARCISSUS_AMBIGUITY_GUARDIAN` | "nós" externo; beleza concreta; leitor implicado sem ser nomeado | Coro acessa mente de Narciso; beleza genérica |
| `FIRST_WATER` | 6 | `NARCISSUS_AMBIGUITY_GUARDIAN` | percepção sensorial concreta; ≥3 hipóteses viáveis | figura nítida; fala; confirmação sobrenatural |
| `THE_REJECTION` | 5 | `ANTI_MANIPULATION_GUARDIAN` | crueldade precisa; leitura A e B verdadeiras | humilhação como erotização de Eco |
| `STATUE_BREAKS` | 14 | `CHARACTER_CONTINUITY_REVIEWER` | gesto único; ciúme e posse indistinguíveis | explicação interior do motivo |
| `THE_CENTER` | 17 | `NARCISSUS_AMBIGUITY_GUARDIAN` | toque fora de tempo; gota; cicatriz | mão atravessa; Reflexo fala; Reflexo age sozinho de forma inequívoca |
| `NIGHT_WITHOUT_WORDS` | 18 | `ANTI_MANIPULATION_GUARDIAN` | cena íntima **em página** com teto de explicitude `SENSUAL` (decisão humana OQ-N4); consentimento explícito e revogável; sinal combinado de parada; silêncio **não** é consentimento; tensão e desconforto do olhar de Narciso para a janela | silêncio tratado como sim; Eco sem capacidade de interromper; explicitude acima de `SENSUAL`; mecânica corporal descrita |
| `DSR_OCCURRENCES` | 12, 15, 19, 22, 27, 31 | `DESIRE_DECAY_GUARDIAN` | função única por ocorrência; consequência; teto de explicitude (seção 11) | explicitude como diferença principal; pornografia gratuita |
| `LIA_THREE_VERSIONS` | 25 | `NARCISSUS_AMBIGUITY_GUARDIAN` | três versões documentadas e incompatíveis | uma versão privilegiada pela narração |
| `GLASS_JEALOUSY` | 26 | `ANTI_MANIPULATION_GUARDIAN` | Eco com agência e saída própria | violência física romantizada |
| `SECOND_REFUSAL` | 29 | `DESIRE_DECAY_GUARDIAN` | recusa lúcida e custosa; Eco não é salvadora | resgate; sermão; ameaça de autolesão |
| `THE_NAME_AT_DAWN` | 31 | `NARCISSUS_AMBIGUITY_GUARDIAN` | nome ambíguo; eco ambíguo; nenhum ato de autolesão descrito | "Eco" dito inequivocamente para ela; entrada deliberada na água narrada |
| `WE_STILL_LOOK` | 33 | `NARCISSUS_AMBIGUITY_GUARDIAN` | uma evidência nova; implicação do olhar do leitor | explicação; moral; epílogo |

### 7.7 Regras imutáveis propostas (`immutable_rules.yaml`)

| id | Categoria | Regra (bloqueante) |
|---|---|---|
| `IR-N01` | ontology | A natureza do Reflexo nunca é confirmada por narrador, personagem, documento, imagem ou paratexto. |
| `IR-N02` | ontology_evidence | Toda evidência sobre o Reflexo sustenta ≥2 hipóteses de `REFLECTION_HYPOTHESES` e nenhuma exclui todas menos uma. |
| `IR-N03` | love | O manuscrito nunca afirma, por narração ou pensamento de Narciso, que ele amou ou que nunca amou alguém; motivos são mostrados por gesto, nunca declarados. |
| `IR-N04` | diagnosis | Nenhum diagnóstico clínico, laudo ou termo psiquiátrico é usado como resposta para o Reflexo ou para o comportamento de Narciso. |
| `IR-N05` | adults | Todo personagem com presença erótica ou de sedução tem 18 anos ou mais canonicamente; Narciso tem 27; o Reflexo nunca aparenta idade diferente da de Narciso; nenhuma hipótese implica menor de idade. |
| `IR-N06` | childhood | Material de infância (fitas, lembranças, diário) nunca aparece em cena com conteúdo erótico ou sensual. |
| `IR-N07` | desire_curve | `desire_stage` nunca regride sem âncora declarada; ocorrências `DSR` seguem funções únicas e teto decrescente de explicitude a partir de `DSR-4`. |
| `IR-N08` | decay_dignity | Definhamento nunca é apresentado como ideal de beleza corporal; nenhuma medida corporal, peso ou magreza é celebrada. |
| `IR-N09` | closure | Não há prólogo, epílogo, nota do autor ou glossário interpretativo. |
| `IR-N10` | final | Narciso não tem morte nem sobrevivência confirmadas; nenhum ato de autolesão é narrado; o último capítulo acrescenta exatamente uma evidência. |
| `IR-N11` | taboo | O tabu da obra é o desejo pela própria imagem. Não existe hipótese de gêmeo, irmão ou duplo biológico: nenhum texto, documento, imagem, brief ou prompt a introduz (OQ-N2). |
| `IR-N12` | consent | Silêncio, beleza, dívida, gratidão ou compulsão nunca são narrados como consentimento. |
| `IR-N13` | myth | Todo `ORIGINAL_MYTH_DNA` permanece reconhecível; nenhuma adaptação moderna é referência. |
| `IR-N14` | pov | Coro nunca acessa a mente de Narciso; nenhum capítulo tem acesso oportunista a outra mente. |
| `IR-N15` | eco_agency | Eco é personagem causal completa, com decisões irreversíveis próprias; nunca existe só para refletir Narciso (princípio de agência de Bea Halden, SDD irmã S.5). |
| `IR-N16` | amintas | O destino de Amintas nunca é confirmado; nenhum método de morte ou autolesão é descrito. |

---

## 8. Character Architecture

> Camadas `GT/SM/SP` seguem o ledger (`CAUSAL_LEDGER_TEMPLATE.yaml`). Idades
> são canônicas e inteiras (INV-06). Nenhum personagem é baseado em pessoa real.

### 8.1 Elenco

| id | Nome | Idade | Função mítica | `major` |
|---|---|---|---|---|
| `CHR-NARCISO` | Narciso Céfiso | 27 | Narciso | sim |
| `CHR-ECO` | Elisa "Eco" Varela | 31 | Eco | sim |
| `CHR-LIA` | Liríope "Lia" Céfiso | 61 | Liríope | sim |
| `CHR-TEODORO` | Teodoro Braga | 78 | Tirésias | sim |
| `CHR-AMINTAS` | Amintas Rocha | 34 | Amínias | sim (ausente em cena) |
| `CHR-IRIS` | Íris Maia | 29 | admiradora / câmera | não |
| `CHR-CORO` | o Coro | adultos (≥21 cada membro nomeado) | admiradores | coletivo, sem GT própria |
| — | o Reflexo | **não é personagem no ledger** | reflexo | ver 9.5 |

### 8.2 `CHR-NARCISO`

| Camada | id | Conteúdo |
|---|---|---|
| GT | `GT-NAR-01` `CONTRADICTION` | Nenhum ato de Narciso tem motivo único: todo gesto de cuidado contém autopreservação, todo gesto de posse contém perda real, e ele próprio não consegue separá-los. `reader_access: NEVER` (nunca enunciada; só inferível) |
| GT | `GT-NAR-02` `FORMATIVE_HISTORY` | Cresceu sem ver o próprio rosto; conhece-se pelo desejo alheio, que sempre quis algo dele. `reader_access: {from_event: EV-NAR-09}` |
| GT | `GT-NAR-03` `FEAR` | Teme que ser visto por inteiro o destrua — e deseja isso. `reader_access: OPEN` |
| GT | `GT-NAR-04` `WOUND` | Culpa não admitida pelo desaparecimento de Amintas. `reader_access: {from_event: EV-REV-INSCRIPTION}` (cap. 14) |
| GT | `GT-NAR-05` `SECRET` | Pagou anonimamente a internação da mãe de Eco — o que permitiu a ela estender o contrato (3). `reader_access: {from_event: EV-REV-DEBT}` (cap. 16) |
| SM | `SM-NAR-01` | "Recuso as pessoas porque elas amam uma imagem, não a mim." `diverges_from: [GT-NAR-01]` |
| SP | `SP-NAR-01` | Frieza elegante, humor seco, cortesia impecável que funciona como distância. `conceals: [GT-NAR-02, GT-NAR-03]` |

Traços de comportamento canônicos: imobilidade; toca superfícies com a ponta
dos dedos, nunca com a palma; cobre a boca com o dorso da mão ao pensar;
nunca inicia contato físico antes do capítulo 18; recusa ser fotografado.

### 8.3 `CHR-ECO`

| Camada | id | Conteúdo |
|---|---|---|
| GT | `GT-ECO-01` `CONTRADICTION` | Passou a vida devolvendo vozes alheias com perfeição e teme não ter uma voz própria que alguém queira ouvir. `reader_access: {from_event: EV-ECO-21}` |
| GT | `GT-ECO-02` `CONSCIOUS_WANT` | Quer ser escolhida por Narciso, não admirada nem usada. `OPEN` |
| GT | `GT-ECO-03` `BOUNDARY` | Não aceita ser tratada como superfície; sai quando percebe que virou uma. `reader_access: {from_event: EV-ECO-26}` |
| SM | `SM-ECO-01` | "Fico porque o trabalho não terminou." `diverges_from: [GT-ECO-02]` |
| SP | `SP-ECO-01` | Profissional discreta, precisa, que responde mais do que pergunta. `conceals: [GT-ECO-01]` |

Decisões irreversíveis próprias (`IR-N15`): estender o contrato (3), esconder
a página do diário (9), ficar após a dívida (16), negociar os termos da noite
(18), sair da casa (26), voltar (28), não colher a flor (32).

Questão ética própria: grava Narciso sem consentimento (7) — isso tem
consequência no ledger (`knowledge_delta`, `relationship_delta`) e nunca é
romantizado.

### 8.4 `CHR-LIA`

`GT-LIA-01 CONTRADICTION`: protegeu o filho de algo que nunca soube nomear, e
a proteção o moldou para aquilo que temia. `SM`: "Cumpri uma profecia para
salvá-lo." `SP`: dama reclusa e severa. Guarda três versões incompatíveis da
origem das regras (25). Nenhuma versão é privilegiada.

### 8.5 `CHR-TEODORO`

`GT-TEO-01 CONDITION`: cego há décadas; conhece rostos pelo toque e confia
mais nisso do que em qualquer imagem. `SM`: "O toque não mente." `SP`:
artesão lacônico. Função: testemunha tátil — suas frases (4, 30) sustentam
hipóteses opostas porque o toque é tão falível quanto a visão.

### 8.6 `CHR-AMINTAS` (ausente)

`GT-AMI-01 MOTIVE`: esculpiu Narciso por desejo e ressentimento; a inscrição
("que ame e não possua", paráfrase própria de *Met.* III) é maldição ou carta
de amor. Nunca aparece em cena presente; nunca confirmado vivo ou morto
(`IR-N16`). Hipótese `H-OTHER` depende dele, sem jamais ser confirmada.

### 8.7 Relações (baseline)

| par | baseline | eixo dramático |
|---|---|---|
| `CHR-NARCISO->CHR-ECO` | `trust: NONE, desire: LATENT, fear: LOW` | desejo que não sabe se é por ela |
| `CHR-ECO->CHR-NARCISO` | `trust: NONE, desire: ACTIVE, fear: NONE` | amor que corre o risco de virar eco |
| `CHR-NARCISO->CHR-LIA` | `trust: BROKEN, fear: MEDIUM` | proteção como prisão |
| `CHR-NARCISO->CHR-TEODORO` | `trust: WARY` | a única mão que o "vê" |

### 8.8 Loops narrativos

| id | kind | par | pergunta |
|---|---|---|---|
| `LP-REFLEXO` | PLOT | NARCISO | O que olha de volta? (nunca `resolves`; `left_open`) |
| `LP-ECO` | RELATIONAL | NARCISO↔ECO | Ele pode desejá-la sem que ela vire superfície? |
| `LP-AMINTAS` | PLOT | NARCISO↔AMINTAS | O que aconteceu na estrada da pedreira? (`left_open`) |
| `LP-LIA` | RELATIONAL | NARCISO↔LIA | Do que ela o protegia? |
| `LP-SELF` | VULNERABILITY | NARCISO | Ser visto inteiro destrói? |
| `LP-INTIMACY` | INTIMACY | NARCISO↔ECO | loop adulto; resolve `TRANSFORMED` em 18 → `LP-ECO` |

---

## 9. Narcissus Uncertainty Principle

### 9.1 Enunciado canônico

> **Toda evidência referente ao Reflexo deverá suportar, sempre que
> narrativamente possível, duas ou mais interpretações ontológicas. Nenhuma
> evidência pode destruir todas as interpretações alternativas.**

### 9.2 `REFLECTION_HYPOTHESES`

| id | Hipótese | Raiz |
|---|---|---|
| `H-PROJ` | projeção, alucinação, privação de sono, compulsão | psicológica |
| `H-SUPER` | manifestação sobrenatural ligada à água/Veio Nêmesis | gótica |
| `H-SELF` | o próprio Narciso (cisão, outro tempo de si) | identidade |
| `H-OTHER` | outra pessoa real (Amintas ou alguém na propriedade) | policial |
| `H-GAZE` | algo nascido da contemplação — inclusive do olhar do leitor | metanarrativa |

### 9.3 `REFLECTION_EVIDENCE` (plano)

Suporte: `S` sustenta · `C` complica (não exclui) · `X` exclui · `—` neutro.

| id | Cap. | Evidência (percepção, nunca ontologia) | PROJ | SUPER | SELF | OTHER | GAZE |
|---|---|---|---|---|---|---|---|
| `RFX-01` | 3 | fita de infância: voz do menino e silêncio com ritmo de resposta | S | S | S | C | — |
| `RFX-02` | 6 | figura na água noturna, sob lua e vento parado | S | S | S | S | S |
| `RFX-03` | 8 | piscar atrasado; pinta aparentemente do lado errado | S | S | S | C | S |
| `RFX-04` | 9 | diário: "para que ele não o visse" (pronome ambíguo) | S | S | S | S | — |
| `RFX-05` | 10 | fotos discordam; câmera tinha modo espelho ligado? | S | C | S | — | S |
| `RFX-06` | 11 | membro do Coro o viu "conversando" sozinho — ou com alguém fora do ângulo | S | S | S | S | — |
| `RFX-07` | 17 | as mãos não chegam juntas ao vidro; uma gota cai | S | S | S | — | S |
| `RFX-08` | 20 | duas respirações fora de fase na gravação | S | S | C | S | — |
| `RFX-09` | 30 | Teodoro: "Este não é o rosto que esculpiram." | S | S | S | S | — |
| `RFX-10` | 21 | fitas de Eco "respondem" às falas ensaiadas por Narciso | S | S | S | C | S |
| `RFX-11` | 23 | foto granulada: reflexo em ângulo impossível | S | S | — | S | S |
| `RFX-12` | 25 | três versões documentadas de Lia (doença de família, lenda da água, profecia do autoconhecimento) | S | S | S | — | C |
| `RFX-13` | 26 | a figura parece olhar Eco | S | S | S | S | S |
| `RFX-14` | 32 | narciso nasce da rachadura da estátua sem terra | C | S | S | C | S |
| `RFX-15` | 33 | fotografia publicada por visitante | S | S | S | S | S |

Contagem de `S`: PROJ 14 · SUPER 14 · SELF 13 · OTHER 8 · GAZE 9 — toda
hipótese tem ≥1 `C` (`UNC-04` ✓) e a razão máx./mín. é 1,75 (`UNC-05` ✓).
Hipótese de gêmeo removida por decisão humana (OQ-N2).

Nenhuma célula `X` é planejada. `X` é permitido pelo contrato (seção 9.4),
mas exige aprovação humana.

### 9.4 Regras determinísticas (`validate_narciso.py`)

| id | Regra | Achado | Severidade |
|---|---|---|---|
| `UNC-01` | toda `RFX-*` tem ≥2 `S` | `SINGLE_HYPOTHESIS_EVIDENCE` | HIGH |
| `UNC-02` | nenhuma `RFX-*` tem `X` em ≥(N−1) hipóteses | `EVIDENCE_COLLAPSES_ONTOLOGY` | BLOCKER |
| `UNC-03` | ao fim do livro, ≥3 hipóteses sem nenhum `X` acumulado | `ONTOLOGY_CONVERGED` | BLOCKER |
| `UNC-04` | toda hipótese tem ≥3 `S` e ≥1 `C` no livro | `HYPOTHESIS_STARVED` / `HYPOTHESIS_UNCHALLENGED` | MEDIUM |
| `UNC-05` | nenhuma hipótese tem mais do que o dobro de `S` da menos sustentada | `HYPOTHESIS_DOMINANCE` | MEDIUM |
| `UNC-06` | todo `RFX-*` aponta para um `EV-*` do ledger e vice-versa para eventos `kind: REFLECTION_EVIDENCE` | `RFX_LEDGER_MISMATCH` | HIGH |
| `UNC-07` | manuscrito sem léxico de confirmação na narração (lista na Obra: "era uma alucinação", "era um fantasma", "era outra pessoa", "era Amintas", "ele era o reflexo", "diagnóstico", termos clínicos listados) | `ONTOLOGY_CONFIRMED_IN_PROSE` | BLOCKER |
| `UNC-08` | nenhum capítulo após o 32 contém "explicação" (epílogo, carta final explicativa, laudo) | `EXPLANATORY_CLOSURE` | BLOCKER |
| `UNC-09` | nenhuma ilustração com `reflection_state` ≠ `NONE` mostra o rosto do Reflexo com visibilidade `FULL` | `REFLECTION_FACE_RESOLVED` | HIGH |
| `UNC-10` | nenhum texto, documento, brief, prompt ou `support` introduz gêmeo, irmão ou duplo biológico de Narciso (léxico: "gêmeo", "irmão gêmeo", "irmão perdido", "natimorto" ligado a Narciso, equivalentes) | `TWIN_HYPOTHESIS_INTRODUCED` | BLOCKER |

`UNC-07` é pré-filtro de léxico (precedente `IR005` da eva). O resíduo — uma
frase que confirma sem usar as palavras — é do `NARCISSUS_AMBIGUITY_GUARDIAN`.

### 9.5 Como o Reflexo entra no ledger sem quebrá-lo

| Problema | Decisão |
|---|---|
| INV-06 reprova participante adulto sem idade (D-N6) | o Reflexo **nunca** é `character` nem `participant`; eventos com ele têm `participants: [CHR-NARCISO]` (e testemunhas humanas) |
| `facts` guardam verdade canônica | em eventos `REFLECTION_EVIDENCE`, `facts` descrevem **somente percepção** ("Narciso vê na água uma figura cuja mão chega antes da sua") — regra `RFX_FACT_IS_PERCEPTION` (validador da obra, por léxico de ontologia em `facts`) |
| INV-11 exige GT divulgada em revisão (D-N5) | nenhuma crença sobre o Reflexo é revisada; crenças `RB-RFX-*` têm `truth: INCOMPLETE`, `left_open: true` |
| O motor precisa de causa para agir (LAW 01) | ações de Narciso têm `caused_by` em GTs dele; o Reflexo nunca é causa |
| Resposta escondida vaza por prompt | **`NO_HIDDEN_ANSWER`**: nenhum arquivo do runtime contém a "verdade" do Reflexo. `CANON_REGISTRY.unknowns: UNK-NAR-001 status: MUST_REMAIN_UNKNOWN` e `prohibited_inferences: PRO-NAR-001..005` (uma por hipótese: "o Reflexo é X") + `PRO-NAR-006` ("Narciso tem gêmeo ou duplo biológico" — OQ-N2) |

`NO_HIDDEN_ANSWER` é a decisão mais importante desta seção: se o motor
soubesse, algum brief acabaria sabendo, e a prosa convergiria.

---

## 10. Love Ambiguity System

### 10.1 Pergunta

> **Narciso alguma vez amou alguém além de si mesmo?**

O romance termina; a discussão continua. Leitores diferentes devem conseguir
defender conclusões opostas com **evidências textuais verdadeiras**.

### 10.2 `LOVE_EVIDENCE_MATRIX`

Força: `WEAK | MEDIUM | STRONG`. `AMBIGUITY_STRENGTH = min(love, narcissism)`.

| EVENT | Cap. | Gesto (fato) | LOVE_READING | NARCISSISM_READING | AMBIGUITY_STRENGTH |
|---|---|---|---|---|---|
| `LOVE-E1` | 5 | rejeita Eco em público com precisão cruel | a afasta porque sabe que destrói quem se aproxima (Amintas) | tédio e desprezo por mais uma admiradora | MEDIUM |
| `LOVE-E2` | 13 | guarda e ouve à noite as gravações de Eco | saudade da voz dela | a voz dela repete as falas dele: ouve a si mesmo | STRONG |
| `LOVE-E3` | 14 | quebra o rosto da estátua quando Eco o toca | ciúme; protege Eco da maldição | ninguém toca a imagem dele | STRONG |
| `LOVE-E4` | 16 | paga anonimamente a internação da mãe de Eco | cuidado sem cobrança | compra de gratidão e permanência | MEDIUM |
| `LOVE-E5` | 18 | pede que ela fique e não fale | vulnerabilidade: palavras o ferem | quer uma superfície silenciosa | STRONG |
| `LOVE-E6` | 26 | tira o reflexo de Eco do quadro | a protege do que olha | não divide o Reflexo com ninguém | STRONG |
| `LOVE-E7` | 29 | recusa ser salvo por ela | poupa Eco de afundar com ele | prefere o Reflexo a ela | STRONG |
| `LOVE-E8` | 31 | chama um nome ao amanhecer; a resposta volta | o nome é "Eco" | o nome é o dele, e o eco é da própria voz | STRONG |
| `LOVE-E9` | 24 | entrega a única foto que guardava | dá a ela a única imagem de si | livra-se da imagem que não obedece ao Reflexo | MEDIUM |

### 10.3 Por que a ambiguidade é estável (e não indecisão do autor)

A verdade do motor para Narciso é `GT-NAR-01` (`CONTRADICTION`): **o amor e o
narcisismo são o mesmo movimento nele**. Assim:

- LAW 01 é satisfeita: todo gesto tem causa (`caused_by: [GT-NAR-01, …]`).
- Nenhum writer pode "decidir" o amor ao ler o ledger: a GT descreve a
  inseparabilidade, não um lado.
- `reader_access: NEVER` impede que a GT seja enunciada.

### 10.4 Regras

| id | Regra | Verificação | Severidade |
|---|---|---|---|
| `LOV-01` | todo `LOVE-E*` tem `love` e `narcissism` ≥ `MEDIUM` | validador da obra `LOVE_READING_WEAK` | HIGH |
| `LOV-02` | contagem de `STRONG` só-amor vs só-narcisismo: diferença ≤1 | `LOVE_BALANCE_TILTED` | MEDIUM |
| `LOV-03` | o último `LOVE-E*` do livro tem as duas leituras `STRONG` | `LOVE_FINAL_RESOLVED` | HIGH |
| `LOV-04` | nenhum pensamento de Narciso declara motivo amoroso ou narcisista (léxico: "porque a amava", "só amava a si", "nunca amou", "a amava de verdade", equivalentes listados) | `LOVE_MOTIVE_DECLARED` | BLOCKER |
| `LOV-05` | todo `LOVE-E*` é evento `REALIZED` do ledger com `relationship_delta` | `LOVE_EVENT_WITHOUT_MUTATION` (reuso de INV-03) | HIGH |
| `LOV-06` | crenças `RB-LOVE-A` e `RB-LOVE-B` coexistem até o fim com `left_open: true` | ledger L4/SOFT-03 | HIGH |

Resíduo de julgamento: se a página realmente sustenta as duas leituras →
`NARCISSUS_AMBIGUITY_GUARDIAN` + `SUBTEXT_EDITOR` + checkpoint humano.

---

## 11. Desire/Decay Progression

### 11.1 Curva canônica

```text
CONTEMPLATION → CURIOSITY → ATTRACTION → EXCITATION → RITUAL → COMPULSION → DEPENDENCE → DEGRADATION → WITHERING
     1–3            4–6         7–11         12–14       15–18      19–21        22–25         26–28          29–33
```

`desire_stage` por capítulo (seção 7.4). Regra `DDC-01`: não decrescente;
regressão só com `relapse_anchor` (evento do ledger) e nunca depois do 26.

### 11.2 Ocorrências compulsivas (`DSR`)

A masturbação compulsiva ligada ao Reflexo é **função narrativa de
deterioração**, nunca pornografia gratuita. Cada retorno muda o significado;
explicitude **não** é o diferencial.

| id | Cap. | Função (única) | Prazer | Teto de explicitude | Consequência obrigatória |
|---|---|---|---|---|---|
| `DSR-1` | 12 | `DISCOVERY` | HIGH | `SENSUAL` | ele volta à água na noite seguinte |
| `DSR-2` | 15 | `PLEASURE` | HIGH | `FRANK` | espelhos migram para o quarto |
| `DSR-3` | 19 | `RITUAL` | MEDIUM | `FRANK` | cancela o mundo de fora |
| `DSR-4` | 22 | `NEED` | LOW | `SENSUAL` | tranca-se; entrega a chave |
| `DSR-5` | 27 | `DEGRADATION` | LOW | `SUGGESTED` | para de dormir e responder |
| `DSR-6` | 31 | `ABSENCE` | NEAR_ZERO | `SUGGESTED` | a cena termina em ausência |

Vocabulário de explicitude (categórico, nunca numérico):
`SUGGESTED < SENSUAL < FRANK`. Não há nível "gráfico mecânico" no contrato
(`HEAT ≠ EXPLICITNESS`, SDD irmã H.3).

### 11.3 Regras

| id | Regra | Achado | Severidade |
|---|---|---|---|
| `DDC-01` | `desire_stage` não decrescente sem âncora | `DESIRE_STAGE_REGRESSION` | HIGH |
| `DDC-02` | funções `DSR` únicas e na ordem canônica | `REPETITION_WITHOUT_NEW_MEANING` | HIGH |
| `DDC-03` | explicitude de `DSR-n` ≤ `DSR-(n−1)` a partir de `DSR-4`; `DSR-6` = `SUGGESTED` | `EXPLICITNESS_ESCALATION` | BLOCKER |
| `DDC-04` | prazer não crescente a partir de `DSR-3` | `PLEASURE_CURVE_BROKEN` | HIGH |
| `DDC-05` | toda `DSR` é evento `REALIZED` do ledger com `kind` adulto, bloco `consent` completo e `≥1` delta | ledger INV-07 + `DSR_WITHOUT_CONSEQUENCE` | HIGH |
| `DDC-06` | nenhuma `DSR` na mesma cena que material de infância (`IR-N06`) | `CHILDHOOD_EROTIC_PROXIMITY` | BLOCKER |
| `DDC-07` | capítulos de `DEGRADATION`/`WITHERING` não descrevem o corpo como mais atraente por estar mais magro (léxico e revisão) | `DECAY_GLAMORIZED` | BLOCKER |
| `DDC-08` | ≥1 capítulo `LOW` de intensidade emocional entre duas `DSR` consecutivas | reuso de L6 `PEAK_WITHOUT_CONTRAST` | MEDIUM |
| `DDC-09` | todo evento adulto entre personagens (hoje só `NIGHT_WITHOUT_WORDS`, cap. 18) declara `explicitness_ceiling` e não passa de `SENSUAL` (OQ-N4) | `NIGHT_EXPLICITNESS_ABOVE_CEILING` | BLOCKER |

### 11.4 Consentimento em ocorrências solitárias

Ocorrências `DSR` são eventos adultos com um participante humano. Proposta de
modelagem com o vocabulário existente — **decidida pelo humano (OQ-N5,
2026-09-15)**: a compulsão é modelada como capacidade de recusa reduzida
(`ability_to_refuse: CONSTRAINED`), sem enum novo:

| `DSR` | `canonical` | `ability_to_refuse` | `boundary_state` | Leitura |
|---|---|---|---|---|
| 1–2 | `CONSENSUAL` | `FULL` | `RESPECTED` | escolha |
| 3 | `CONSENSUAL` | `FULL` | `PUSHED` | o rito empurra limites próprios |
| 4–5 | `CONSENSUAL` | `CONSTRAINED` | `PUSHED` | compulsão reduz a capacidade de parar |
| 6 | `CONSENSUAL` | `CONSTRAINED` | `VIOLATED` | o corpo já não obedece ao próprio limite |

O Reflexo nunca figura em `perceived` como sujeito de consentimento.

### 11.5 Horror corporal sem espetáculo

- A progressão física é contada por **perda**: de luz na pele, de simetria,
  de sono, de gesto, de voz — não por inventário de ossos.
- A última ocorrência deve ler-se como **quase ausência de prazer**: o texto
  fica mais curto, mais frio e mais distante.
- `DESIRE_DECAY_GUARDIAN` julga o resíduo; `PHYSICALITY_AND_BODY_AGENT`
  revisa coerência física.

---

## 12. Bea Halden Voice Profile

### 12.1 `BEA_HALDEN_NARCISSUS_VOICE_PROFILE`

Arquivo proposto: `books/narciso/planning/VOICE_PROFILE.md`, lido por
`T156_BUILD_VOICE_REFERENCE`; aprovado em `GATE_VOICE` (humano). Não é
identidade da autora para outros livros (SDD irmã S.4).

| Qualidade | Regra operacional | Anti-padrão |
|---|---|---|
| elegante | sintaxe limpa; adjetivo único e exato | empilhamento de adjetivos de beleza |
| íntima | câmera próxima de superfície: pele, água, respiração | interioridade explicada |
| sensual | desejo por textura, temperatura, distância, demora | inventário anatômico |
| perturbadora | beleza descrita com precisão de quem descreve uma ameaça | "algo estava errado" |
| econômica | frases curtas em picos; um parágrafo pode ser uma linha | ornamentação constante |
| lírica sem excesso | no máximo uma imagem figurada forte por parágrafo | metáfora sobre metáfora |
| psicológica | comportamento revela; nunca diagnostica | termos clínicos (`IR-N04`) |
| silêncio | cortes, brancos, cenas que terminam antes | fechamento de cada cena com moral |
| não explicar | `SUGESTÃO > EXPLICAÇÃO` | narrador que resume o que o leitor sentiu |

### 12.2 Registros por POV

| POV | Registro |
|---|---|
| Narciso | sensorial, frio, preciso; percebe superfícies antes de pessoas; nunca nomeia o próprio motivo |
| Eco | auditivo; ouve antes de ver; escuta ritmos, respirações, ecos; frase mais longa, mais afetiva |
| Lia | seca, cerimoniosa, contraditória |
| Coro | "nós" coletivo, sedutor e ligeiramente vergonhoso; descreve Narciso como quem descreve uma obra de arte que quer possuir; cada capítulo do Coro termina com o olhar voltado para fora da página |

### 12.3 Calibração

- `voice_calibration_chapters: [1, 6, 17, 18]` (Coro, primeira água, centro,
  intimidade).
- `lead_novelist_owned_chapters: [1, 6, 11, 12, 17, 18, 23, 26, 29, 31, 32, 33]`.
- Referência não é imitação: nenhum brief, prompt ou `VOICE_REFERENCE` cita
  autores, títulos ou "no estilo de" (`IMITATION_PATTERN`, T602).

### 12.4 `book/text_quality.yaml` (override proposto)

Clichês adicionais (lista inicial, severidade `MEDIUM`):

```yaml
cliches:
  patterns:
    - deus grego
    - beleza estonteante
    - beleza de tirar o fôlego
    - perfeito demais para ser real
    - olhos penetrantes
    - abdômen definido
    - corpo esculpido          # permitido só em uso literal de mármore (revisor julga)
    - mandíbula esculpida
    - sorriso predatório
    - olhar predatório
    - aura de perigo
    - calor subiu pelo corpo
    - não conseguia desviar o olhar
    - como se pudesse ver sua alma
    - reflexo sombrio
    - espelho da alma
```

Regras de vocabulário da obra (validador, não detector genérico):
`narciso` como flor aparece com inicial minúscula e nunca em trocadilho com o
nome na narração; a palavra "reflexo" como substantivo próprio ("o Reflexo")
**não** é usada no manuscrito — a presença nunca recebe nome próprio pela
narração (`REFLECTION_NAMED`, HIGH). O nome "Reflexo" é só identificador de
engenharia.

---

## 13. Visual Bible — `NARCISSUS_VISUAL_BIBLE`

Arquivo proposto: `books/narciso/planning/NARCISSUS_VISUAL_BIBLE.md` →
consumido por `T036_VISUAL_LIFE_SPEC`, `T037_IMAGE_BIOME`, `T042_VISUAL_DISCOVERY`,
`T043_VISUAL_NARRATIVE_CANON`. O canon visual **cita** esta bíblia (`DOC:`);
não a duplica (SDD irmã, seção 36).

### 13.1 Tese visual

```yaml
book_dna:
  visual_thesis: "A beleza é uma superfície que olha de volta."
  vocabulary: BELEZA + ÁGUA + REFLEXO + CORPO + FLOR + OURO + DECADÊNCIA
  duality:
    outer_truth: "Narciso olha para quem o segura."
    hidden_truth: "Narciso olha para o reflexo que o livro produz."
    anchors: ["SCENE:THE_CENTER", "SCENE:WE_STILL_LOOK"]
```

### 13.2 Paleta (dentro dos papéis de `AUTHOR_VISUAL_DNA.v1`)

| Papel | Nome editorial | Hex proposto | HSL (L, S) calculado | Faixa v1 | Uso |
|---|---|---|---|---|---|
| `GROUND` | preto profundo | `#0E0D0F` | 0,05 · 0,07 | L 0,03–0,22 · S 0,00–0,20 | fundo dominante, água à noite |
| — (textura de `GROUND`) | carvão / mármore negro | `#1C1B1D` | 0,11 · 0,04 | idem | veios, pedra |
| `INK` | marfim | `#E9E1D2` | 0,87 · 0,34 | L 0,75–0,95 · S 0,10–0,45 | tipografia, pele iluminada |
| — (variação de `INK`) | branco narciso | `#F2EEE3` | 0,92 · 0,37 | idem | pétalas, gota, luz de amanhecer |
| `METAL` | dourado envelhecido | `#8A6C3E` | 0,39 · 0,38 | L 0,25–0,55 · S 0,10–0,70 | ouro em folha, título |
| — (conteúdo de ilustração) | bronze | `#6E4F33` | — | não é papel | molduras, luz de vela |
| `PULSE` | vinho extremamente escuro | `#3E0C16` | 0,15 · 0,68 | L 0,10–0,35 · S 0,35–0,90 · área ≤ 12% | só boca, sombra quente, lacre; nunca sangue |
| — (acabamento) | reflexo prateado discreto | `semantic_material: SILVER_MIRROR` | — | **não** é `METAL` (D-N3) | só `finish_intents` e realce pontual |

Valores são **propostas**. A validação oficial é V1 do `check_visual_canon.py`
no Slice 3. `METAL: AGED_GOLD` para o livro; a marca BH continua em
`BURNT_COPPER` (material assinatura da autora).

Regra de saturação: nenhuma ilustração tem cor dominante fora dos papéis;
pele é a única cor quente de área grande permitida e deve ficar dessaturada.

### 13.3 Materiais visuais

| Material | Significado | Regra de render | Veto |
|---|---|---|---|
| mármore | perfeição que parece viva; corpo que vira estátua | veios visíveis, frio, polido ou fosco conforme ato | mármore branco "grego" de cartão-postal |
| água | nascimento do Reflexo; instabilidade; intocável | sempre parada ou quase; negra; reflete mais do que deixa ver | água azul-turquesa; ondas decorativas |
| vidro | separação transparente | reflexo sobreposto, nunca transparência total | vidro com texto |
| espelho | identidade, duplicação, desejo, mentira | coberto (Ato I), descoberto (II), múltiplo/rachado (III) | espelho de selfie com celular |
| ouro | beleza transformada em objeto | folha fina que descasca; nunca joia ostensiva | coroa, louros, dourado brilhante uniforme |
| papel | arquivo, memória, diário, foto | fibra visível, bordas gastas | texto legível em ilustração (exceto artefato citado) |
| pele | o corpo como obra | textura real, poros, pelos naturais adultos | pele de filtro; brilho oleoso; pele sem idade |
| flores | narciso: beleza, morte, retorno | branco narciso, uma flor por composição | buquês, pétalas em profusão |
| lágrimas / gotas | água do corpo; desejo; perda | uma gota por composição quando presente | lágrimas múltiplas melodramáticas |
| tecido negro | véu, luto, ocultação | lençóis sobre espelhos; lã; linho escuro | cetim de capa de romance genérico |
| pedra / rachadura | fragmentação da identidade | fissura fina que atravessa forma | rachaduras decorativas por toda superfície |

### 13.4 Luz

- **Uma fonte**: lateral, estreita, fria (lua, amanhecer) ou quente (vela).
- Narciso ocupa a luz; o resto da composição fica em `GROUND`.
- Cáusticas de água são permitidas como luz refletida no rosto/teto.
- Proibido: rim light de cinema de ação, neon, brilho de beleza, halos.

### 13.5 Gramática de composição por ato

Detalhada na seção 17. Resumo: **Ato I simetria e espaço**; **Ato II
duplicação e água invadindo**; **Ato III fragmento, close, vestígio**.

### 13.6 Anti-autocanibalização em relação a *A Noiva Esquecida*

| Eixo | A Noiva Esquecida | NARCISO |
|---|---|---|
| Dominante de capa | maçã negra, objeto | figura (parcial) ou superfície de água com olhar |
| Reflexo | testemunha ética/legal; atraso → ausência → multiplicação | ontologia indecidível; objeto do desejo |
| `METAL` | cobre queimado | ouro envelhecido (+ prata só como acabamento) |
| Figura humana | vetada ("sem casal, rosto ou torso") | fragmento do rosto na capa e fragmentos no miolo, com aprovação (decidido, OQ-N1) |
| Material-chave | ferro, madeira, gelo | mármore, água parada, ouro em folha |
| Sigil | INTACT → … → RETURNED_DIFFERENT | VELADO → … → VAZIO (seção 17.4) |

Regra: nenhum `elements[].label` de NARCISO coincide com um dominante ou
secundário da noiva (teste de interseção, padrão do worked example da SDD
irmã, 30.10). "Reflexo" é compartilhado como **motivo**, mas com `meaning` e
estados diferentes; o validador de interseção aceita motivo compartilhado só
se `meaning` e estados divergirem (FUTURE Portfolio; nesta obra, revisão
humana).

### 13.7 Vetos visuais (`vetoes[]`, `rule_kind: CANONICAL`)

| id | Veto | Motivo |
|---|---|---|
| `VETO-N01` | beleza masculina de banco de imagens: músculo oleado, abdômen em evidência, pose de modelo | anti-genérico (D-N9) |
| `VETO-N02` | torso nu sem função narrativa | watchlist `SHIRTLESS_MALE` |
| `VETO-N03` | pétalas de rosa, rosas, sangue decorativo, caveira, correntes, faca | watchlist da autora |
| `VETO-N04` | kitsch grego: toga, louros, colunas, templo | clichê mítico |
| `VETO-N05` | reprodução de composição de pinturas conhecidas de Narciso (qualquer época) | originalidade (seção 32) |
| `VETO-N06` | imagem derretida/surreal reconhecível de obras modernas protegidas | IP |
| `VETO-N07` | codificação juvenil: rosto infantilizado, corpo sem pelos, proporções adolescentes, uniforme escolar | seção 33 |
| `VETO-N08` | glamour de magreza: costelas/clavículas exibidas como beleza no definhamento | `IR-N08` |
| `VETO-N09` | selfie com celular diante do espelho como imagem de capa ou herói | banaliza a tese |
| `VETO-N10` | gradientes roxos/neon "dark romance", fumaça, faíscas | anti-genérico |
| `VETO-N11` | texto, marca d'água, logotipo em ilustração | padrão `eva`/`a_morte` |
| `VETO-N12` | genitália ou ato sexual representado em ilustração | seção 14.6 e 33 |
| `VETO-N13` | rosto do Reflexo totalmente visível e nítido | `UNC-09` |
| `VETO-N14` | semelhança com pessoa real ou celebridade | `FACE_CANON_TEMPLATE.md` |

---

## 14. Narcissus Visual DNA — `NARCISSUS_VISUAL_DNA`

Vive em `images/canon/FACE_CANON.md` (seção de rosto, template existente) e em
`images/canon/CHARACTER_VISUAL_BIBLE.md` (corpo, gesto, figurino,
definhamento), escritos em `T038`/`T039` por
`FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT`, a partir desta seção. Código de
identidade: **`FV-NARCISO-01`**.

### 14.1 Rosto

| Traço | Canon |
|---|---|
| aparência de idade | 27; ossatura adulta; linhas finas no canto externo dos olhos; nunca rejuvenescido |
| formato | oval longo; maçãs altas sem angulosidade de vilão |
| olhos | cinza-esverdeado escuro ("cor de água parada"), anel limbal escuro; pálpebra superior pesada; olhar demorado |
| sobrancelhas | retas, baixas, densidade média; a esquerda levemente mais alta |
| nariz | dorso longo e reto com pequena saliência; ponta estreita |
| boca | lábios de espessura média; **canto esquerdo mais alto** (meio sorriso sempre à esquerda) |
| marca | **pinta pequena escura abaixo do olho direito** |
| mandíbula | definida, não quadrada; barba feita no Ato I |
| pele | oliva-pálida, subtom frio, textura real; "de mármore" só pela uniformidade de luz, nunca por filtro |

### 14.2 Cabelo

Preto com reflexo castanho-azulado; ondulado; na altura da mandíbula;
**repartido à esquerda**; parece úmido mesmo seco; cai sobre a testa quando
ele se inclina para a água.

### 14.3 Corpo

| Traço | Canon |
|---|---|
| altura / estrutura | 1,86 m; longo e magro-atlético (nadador que não nada); ombros médios |
| pescoço / clavículas | pescoço longo; clavículas marcadas **no Ato I** como elegância, nunca exibidas no III (`VETO-N08`) |
| antebraços | veias discretas visíveis |
| pelos | naturais de adulto em antebraços e peito (marcador de idade, `VETO-N07`) |
| mãos | dedos longos, nós salientes, unhas curtas; **cicatriz fina e clara diagonal na palma esquerda** (espelho quebrado na infância; reabre no cap. 17) |
| anel | **aro de ouro envelhecido no indicador direito** (herança dos Céfiso) |

### 14.4 Postura e gestos recorrentes

- imobilidade; peso na perna esquerda; cabeça inclinada ~10° para a esquerda;
- toca superfícies com a ponta dos dedos, nunca com a palma;
- dorso da mão sobre a boca quando pensa;
- polegar percorrendo a própria mandíbula (surge no Ato II);
- nunca sorri inteiro.

### 14.5 Figurino

Ato I: lã preta/carvão, camisa de linho marfim, casaco escuro longo, pés
descalços em casa. Ato II: camisa aberta, mangas dobradas, mãos sempre úmidas.
Ato III: a mesma camisa de linho, suja; lençol negro sobre os ombros. Sem
logotipos, sem joias além do anel.

### 14.6 Nudez artística

- Permitida só em categorias `HERO`, `BODY_DETAIL`, `REFLECTION` e só com
  Chekhov `PROVEN` (âncora estrutural por função).
- Enquadramento por costas, ombro, nuca, linha d'água, sombra, tecido.
- **Nunca** genitália, ato sexual ou pose de conteúdo erótico explícito
  (`VETO-N12`).
- Nudez em capa ou superfície pública: proibida (seção 26.1; KDP a verificar
  em `T699`).

### 14.7 Definhamento visual — `DECAY_TIMELINE`

Estados do elemento `FIG-NARCISO` (canon visual, classe `FIGURE`),
projetados por evento (seção 17.3):

| Estado | Vigência (projeção) | Muda | Nunca muda |
|---|---|---|---|
| `D0_PRISTINE` | 1–14 | — | todas as âncoras de identidade 14.1–14.3 |
| `D1_SLEEPLESS` | após `STATUE_BREAKS` | olheiras, barba de dois dias, lábio seco | idem |
| `D2_FEVER` | após `THE_CENTER` | cabelo molhado colado, rubor, mãos trêmulas, cicatriz aberta | idem |
| `D3_WITHERING` | após `DSR-4` | pele baça, unhas roídas, camisa suja; **perda de luz, não de peso exibido** | idem |
| `D4_MARBLE` | após `DSR-5` | palidez acinzentada, imobilidade de estátua, lábios rachados | idem |
| `D5_TRACE` | após `THE_NAME_AT_DAWN` | **o corpo sai de quadro**: só vestígios (camisa, lençol, marca na água, anel) | — |

Regra `DECAY_FROM_BODY_TO_TRACE`: a partir de `D3`, a proporção de
ilustrações `DECAY` com o corpo em quadro diminui; em `D5`, zero.

### 14.8 `REFLECTION_RULES`

O rosto de Narciso foi desenhado **assimétrico de propósito**, para que o
espelho seja verificável por olho humano:

| Âncora | Narciso | Reflexo verdadeiro (espelhado) |
|---|---|---|
| canto mais alto da boca | esquerdo | direito |
| pinta sob o olho | direito | esquerdo |
| repartição do cabelo | esquerda | direita |
| cicatriz na palma | esquerda | direita |
| anel | indicador direito | indicador esquerdo |

| `reflection_state` | Definição | Regra |
|---|---|---|
| `NONE` | sem reflexo em quadro | — |
| `TRUE_MIRROR` | todas as âncoras espelhadas corretamente | permitido em qualquer ato |
| `ANOMALOUS_MIRROR` | **exatamente uma** âncora não espelhada (ou `decay_offset: -1`) | só a partir do cap. 8; declarar qual âncora |
| `FRAGMENTED` | reflexo partido por água, rachadura, vapor | rosto nunca completo |
| `OCCLUDED` | reflexo existe atrás de vidro, sombra, tecido | — |
| `DOUBLE` | duas figuras de Narciso em quadro sem fonte de espelho óbvia | máx. 2 ilustrações no livro; aprovação humana |
| `ABSENT_REFLECTION` | superfície refletora em quadro sem o reflexo esperado | máx. 1 ilustração; spoiler ≥ HIGH |

Regras adicionais:

- `REF-01` rosto do Reflexo com visibilidade no máximo `PARTIAL` (`UNC-09`).
- `REF-02` `decay_offset ∈ {0, -1}`: o Reflexo pode aparecer **um estado mais
  belo** que o corpo; nunca mais degradado. Sustenta `H-PROJ`, `H-SUPER`,
  `H-SELF` e `H-GAZE`.
- `REF-03` nunca duas anomalias na mesma ilustração.
- `REF-04` a anomalia declarada entra na checklist de `T4NN_CONTINUITY_QA`
  (acerto ≠ erro de geração: anomalia **não declarada** é defeito e reprova).

### 14.9 Reconhecimento por fragmento

| Recorte | Âncoras obrigatórias visíveis (mín.) |
|---|---|
| mão molhada | cicatriz **ou** anel + dedos longos + nós |
| olho | cor + pinta (se lado direito em quadro) + sobrancelha reta |
| boca | assimetria do canto esquerdo |
| curva do ombro / nuca | cabelo úmido na altura da mandíbula + pescoço longo |
| cabelos sobre a água | preto azulado + ondulação + repartição |
| silhueta | inclinação de cabeça + pescoço longo + peso na perna esquerda |
| reflexo fragmentado | ≥1 âncora espelhada verificável |

`FIGURE_FRAGMENT_UNRECOGNIZABLE` (MEDIUM, revisão de `FACE_QA`): fragmento sem
as âncoras mínimas. Regra de geração: todo fragmento usa `--reference` numa
imagem de referência aprovada de `FV-NARCISO-01`.

### 14.10 Lista de rejeição de `FACE_QA` (calibrada para NARCISO)

Rejeitar: rosto "de modelo" simétrico; mandíbula quadrada hipermasculina;
pele lisa sem textura; olhos azuis ou verdes claros; pinta ausente ou migrada
sem declaração; cabelo curto ou liso; corpo musculoso de academia; aparência
abaixo de 25 anos; sorriso aberto; beleza aumentada nos estados `D3–D4`;
magreza exibida; semelhança com pessoa real.

---

## 15. Symbol Registry — `SYMBOL_REGISTRY`

Cada símbolo é um `elements[]` do canon visual com `functions` ancoradas,
`states` e `transitions` (SDD irmã, 14). Nenhum símbolo existe só como
decoração (VP-01). Gatilhos são âncoras, nunca números de capítulo; a coluna
"Cap." é a projeção prevista.

### 15.1 `SYM-ESPELHO` — identidade, duplicação, desejo, mentira

| Estado | `memory_state` | Gatilho (âncora) | Cap. | Significado vigente |
|---|---|---|---|---|
| `VELADO` | S | inicial | 1 | proteção / proibição |
| `DESCOBERTO` | R | `LEDGER:EV-NAR-08` (primeiro espelho descoberto) | 8 | curiosidade proibida |
| `MULTIPLICADO` | T | `LEDGER:EV-NAR-15` (espelhos no quarto) | 15 | desejo que se replica |
| `FRATURADO` | T | `SCENE:THE_CENTER` | 17 | identidade partida |
| `FRENTE_A_FRENTE` | P | `LEDGER:EV-NAR-27` | 27 | infinito sem saída |
| `VAZIO` | E | `SCENE:THE_NAME_AT_DAWN` | 31 | ausência — de quem? |

### 15.2 `SYM-AGUA` — nascimento do Reflexo, instabilidade, impossibilidade

`PROIBIDA` (S, 2) → `CONTEMPLADA` (R, `SCENE:FIRST_WATER`, 6) →
`INVASORA` (T, `LEDGER:EV-NAR-19`: água em bacias, chão molhado, 19) →
`PARADA` (P, `LEDGER:EV-NAR-27`, 27) → `SUPERFÍCIE_PÚBLICA` (E, `SCENE:WE_STILL_LOOK`, 33).

### 15.3 `SYM-NARCISO` (flor) — beleza, morte, renascimento, vaidade

`BULBO` (S: bulbos dormentes na estufa de Lia, 2) → `FORÇADO` (R: flor forçada
em vaso dentro de casa, `LEDGER:EV-LIA-09`, 9) → `MURCHO` (T: a flor forçada
murcha no quarto de espelhos, `LEDGER:EV-NAR-22`, 22) → `NA_RACHADURA` (P:
`LEDGER:EV-ECO-32`, 32). `count: 1` por composição, sempre.

### 15.4 `SYM-OURO` — beleza transformada em objeto

`HERANÇA` (S: anel, molduras, 1–2) → `FOLHA_SOBRE_A_PELE` (R: `LEDGER:EV-NAR-10`, 10) →
`RITUAL` (T: ouro no rito, `LEDGER:EV-NAR-19`, 19) → `DESCASCANDO` (P: a foto
guardada e o anel frouxo, `LEDGER:EV-NAR-24`, 24) → `ANEL_SEM_MÃO` (E: vestígio
em `D5_TRACE`, 32).

### 15.5 `SYM-MARMORE` — perfeição que parece viva; corpo que vira estátua

`ESTÁTUA_VELADA` (S, 1) → `ESTÁTUA_TOCADA` (R, `LEDGER:EV-TEO-04`, 4) →
`ROSTO_QUEBRADO` (T, `SCENE:STATUE_BREAKS`, 14) → `CORPO_DE_PEDRA` (P, `D4_MARBLE`,
`LEDGER:EV-NAR-27`, 27–30) → `PEDRA_QUE_FLORESCE` (E, 32).

### 15.6 `SYM-RACHADURA` — fragmentação da identidade

`FIO` (S: fissura fina num espelho coberto, 2) → `NO_ROSTO_DE_PEDRA` (R, 14) →
`NA_PALMA` (T: cicatriz reaberta, `SCENE:THE_CENTER`, 17) → `NA_BOCA` (P: lábio
rachado em `D4`, 27) → `DE_ONDE_NASCE` (E: a flor, 32).

### 15.7 `SYM-GOTA` — água, suor, lágrima, desejo

`ORVALHO` (S, 6) → `SUOR` (R, `DSR-2`, 15) → `A_GOTA_ENTRE_AS_MÃOS` (T,
`SCENE:THE_CENTER`, 17) → `LÁGRIMA` (P, `LEDGER:EV-NAR-29`, 29) →
`GOTA_QUE_DESFAZ_O_REFLEXO` (E, 31). `count: 1` por composição.

### 15.8 Regras do registro

| id | Regra | Achado (existente) |
|---|---|---|
| `SYMR-01` | todo símbolo tem `S` antes de `P` | `PAYOFF_WITHOUT_SEED` (ST-05) |
| `SYMR-02` | estado muda só por âncora | `ARBITRARY_STATE_MUTATION` (ST-02) |
| `SYMR-03` | abertura mostra estado com `display_from: NEXT_CHAPTER` | `OPENER_PRE_ANNOUNCES_EVENT` |
| `SYMR-04` | ≤1 dominante e ≤2 secundários por superfície | `VISUAL_OVERLOAD` |
| `SYMR-05` | significado evolui: o `meaning` de cada estado é declarado e diferente do anterior | **novo na obra**: `SYMBOL_STATE_WITHOUT_NEW_MEANING` (MEDIUM) |
| `SYMR-06` | flor e gota com `count: 1` | `UNJUSTIFIED_COUNT` |
| `SYMR-07` | nenhum símbolo resolve ontologia do Reflexo | `UNC-*` |

---

## 16. Illustration Canon — `ILLUSTRATION_CANON`

### 16.1 Princípio

As ilustrações **são canon**. Cada uma tem função narrativa declarada,
relação com o texto, estado de reflexo, nível de spoiler e requisitos de
continuidade. Nenhuma é preenchimento.

**Onde vive:** cada ilustração é uma `compositions[]` do
`canon/VISUAL_NARRATIVE_CANON.yaml` (superfície `INTERIOR_PLATE` ou
`CHAPTER_OPENER`) — REUSE de exposição, spoiler, elementos, aprovação e
edição — com dois blocos novos (seção 29.3):

- `illustration` (**motor**, neutro de gênero): `category`, `text_relation`,
  `adds`, `payoff_anchor`, `callback_of`, `pair_with`, `placement_anchor`;
- `ext.narciso` (**obra**, validado por `validate_narciso.py`):
  `reflection_state`, `reflection_anomaly`, `decay_state`, `gaze`,
  `symmetry`, `crop`, `hypotheses_supported`, `reader_emotion`.

### 16.2 Categorias

| Categoria | Função | Superfícies | Alvo (proposta) | Regras específicas |
|---|---|---|---|---|
| `HERO` | grandes imagens de Narciso | `INTERIOR_PLATE` (página inteira ou spread) | 4 | só em 1, 10, 17, 33; aprovação humana; nudez só por 14.6 |
| `CHAPTER` | abertura de capítulo | `CHAPTER_OPENER` | 33 | sigil `SIG-ESPELHO` + ornamento do ato; nunca cena |
| `SYMBOL` | flor, água, rachadura, gota, ouro | `INTERIOR_PLATE` (meia página) | 6 | 1 símbolo dominante; sem figura |
| `REFLECTION` | imagens deliberadamente ambíguas | `INTERIOR_PLATE` | 6 | `reflection_state ≠ NONE`; ≥2 hipóteses; `UNC-09` |
| `BODY_DETAIL` | olhos, mãos, boca, nuca, costas, pele | `INTERIOR_PLATE` | 3 | âncoras de fragmento 14.9; justificativa narrativa |
| `DECAY` | transformação progressiva | `INTERIOR_PLATE` | 3 | `decay_state` ≥ D2; `DECAY_FROM_BODY_TO_TRACE` |
| `CALLBACK` | arte anterior que retorna modificada | `INTERIOR_PLATE` | 5 | `callback_of` obrigatório; mesma composição base; ≥1 diferença declarada; ≤ 1 diferença "impossível" |

Total proposto: **24 pranchas + 33 aberturas + 2 guardas (collector) + sistema de
capa**. O número final é decisão humana (custo de páginas, OQ-N7).

### 16.3 Metadados (contrato pedido → campo real)

| Campo pedido | Onde vive |
|---|---|
| `illustration_id` | `compositions[].id` (`IL-NN`) |
| `chapter` | derivado de `illustration.placement_anchor` (`TEXT:`/`TURN:`) — nunca número nu |
| `canonical_moment` | `illustration.placement_anchor` + `LEDGER:EV-*` em `elements[].functions` |
| `characters` | `elements[]` de classe `FIGURE` (`FIG-NARCISO`, `FIG-ECO`…) |
| `visual_symbols` | `elements[]` com `SYM-*` e `prominence` |
| `reader_emotion` | `ext.narciso.reader_emotion` (texto curto; não validado semanticamente) |
| `composition` | `elements[].placement.zone` + `ext.narciso.symmetry` + `crop` + `gaze` |
| `lighting` | `atmosphere` (não justifica objeto — `ATMOSPHERE_ONLY_PROMINENT`) |
| `reflection_state` | `ext.narciso.reflection_state` (+ `reflection_anomaly`) |
| `spoiler_level` | `elements[].exposure.spoiler_level` + `reveal` (REUSE V5) |
| `continuity_requirements` | `ext.narciso.decay_state` + âncoras 14.9 + `FV-NARCISO-01` |
| `print_requirements` | `EDITION_PLAN` projetado (REUSE) + `must_survive_grayscale` |

### 16.4 Inventário proposto

`rel` = `text_relation` (`COMP` complement · `CONTRA` contradict · `FORE`
foreshadow). Spoiler conforme V5.

| id | Cap. | Categoria | Momento | rel | `reflection_state` | `decay` | Spoiler | Par espelhado |
|---|---|---|---|---|---|---|---|---|
| `IL-01` | 1 | HERO | Narciso de costas diante da estátua velada; o Coro em desfoque | COMP | NONE | D0 | NONE | `IL-24` |
| `IL-02` | 2 | SYMBOL | corredor de espelhos cobertos por lençóis negros | FORE | NONE | — | NONE | `IL-22` |
| `IL-03` | 4 | BODY_DETAIL | mãos de Teodoro sobre o rosto de pedra | FORE | NONE | — | NONE | `IL-20` |
| `IL-04` | 6 | REFLECTION | cabelos sobre água negra; ondulação parte a figura | CONTRA | FRAGMENTED | D0 | LOW | `IL-19` |
| `IL-05` | 8 | REFLECTION | perfil na janela noturna; reflexo com a pinta do lado não espelhado | FORE | ANOMALOUS_MIRROR (`mole`) | D0 | LOW | — |
| `IL-06` | 9 | SYMBOL (artefato) | página arrancada do diário; frase ilegível por desenho | COMP | NONE | — | MEDIUM (`reveal` cap. 9, `AFTER`) | — |
| `IL-07` | 10 | HERO | ombro e pescoço cobertos de ouro em folha | COMP | NONE | D0 | NONE | `IL-17` |
| `IL-08` | 11 | REFLECTION | margem da cava vista de longe, figura e reflexo mínimos | FORE | OCCLUDED | D0 | LOW | — |
| `IL-09` | 12 | BODY_DETAIL | mão molhada espalmada no vidro embaçado | CONTRA | OCCLUDED | D0 | LOW | — |
| `IL-10` | 14 | SYMBOL | rosto de mármore negro rachado | COMP | NONE | — | LOW | `IL-23` |
| `IL-11` | 15 | REFLECTION | costas nuas diante de três espelhos; uma figura parece de frente | CONTRA | DOUBLE | D1 | MEDIUM | — |
| `IL-12` | 17 | HERO (spread) | duas mãos quase se tocando através da superfície; uma gota entre elas | FORE | ANOMALOUS_MIRROR (`scar`) | D1 | MEDIUM | centro |
| `IL-13` | 18 | BODY_DETAIL | nuca e ombro na penumbra; janela reflete só uma figura | CONTRA | OCCLUDED | D2 | LOW | — |
| `IL-14` | 19 | SYMBOL | bacia de água, velas, ouro — espelho doméstico | COMP | TRUE_MIRROR | — | LOW | — |
| `IL-15` | 22 | DECAY | chave sobre mármore; mão de unhas roídas | COMP | NONE | D2 | MEDIUM | — |
| `IL-16` | 23 | REFLECTION (artefato foto) | fotografia granulada do Coro | CONTRA | ANOMALOUS_MIRROR (`angle`) | D3 | MEDIUM | — |
| `IL-17` | 24 | CALLBACK | a foto guardada: o ouro de `IL-07` descascando | COMP | NONE | D0→D3 | MEDIUM | `IL-07` |
| `IL-18` | 27 | DECAY | lençol caído de um espelho; o reflexo mais íntegro que o corpo cortado de quadro | FORE | ANOMALOUS_MIRROR (`decay_offset -1`) | D3 | HIGH (`AFTER`) | — |
| `IL-19` | 28 | CALLBACK | água negra com uma única gota caindo (composição de `IL-04`, sem figura) | CONTRA | ABSENT_REFLECTION | — | HIGH (`AFTER`) | `IL-04` |
| `IL-20` | 30 | CALLBACK | mãos de Teodoro sobre rosto de carne imóvel (composição de `IL-03`) | COMP | NONE | D4 | HIGH (`AFTER`) | `IL-03` |
| `IL-21` | 31 | REFLECTION | amanhecer; névoa sobre a cava; reflexo parcial de uma silhueta | CONTRA | FRAGMENTED | D4 | HIGH (`AFTER`) | — |
| `IL-22` | 32 | CALLBACK | o corredor de `IL-02`, espelhos descobertos frente a frente | FORE | TRUE_MIRROR | D5 | HIGH (`AFTER`) | `IL-02` |
| `IL-23` | 32 | CALLBACK | narciso nascendo da rachadura de `IL-10` | COMP | NONE | — | HIGH (`AFTER`) | `IL-10` |
| `IL-24` | 33 | CALLBACK (HERO) | composição de `IL-01`: estátua, Coro fotografando, Narciso ausente; a água no primeiro plano | FORE | UNDETERMINED por névoa | D5 | HIGH (`AFTER`) | `IL-01` |

Distribuição: COMP 9 · CONTRA 8 · FORE 7 (≈ 38% / 33% / 29%).

### 16.5 Aberturas de capítulo (`CHAPTER`)

- Estrutura fixa: `NÚMERO ROMANO` → `TÍTULO` → sigil `SIG-ESPELHO` no estado
  projetado → (Ato I) espaço; (Ato II) ornamento duplicado; (Ato III)
  ornamento incompleto.
- Nenhuma cena nas aberturas; nenhuma figura humana.
- Render padrão `GLYPH` / `RASTER_1BIT` (SDD irmã DL-22).
- Capítulos do Coro (1, 11, 23, 33) usam o sigil com uma variação fixa: o
  quadro visto **de fora** (moldura sem espelho).

### 16.6 Contrato de prompt futuro (não gerar agora)

Arquivo por prancha: `images/prompts/IL-NN_IMAGE_BRIEF.md`, escrito por
`CHAPTER_IMAGE_DIRECTOR`, no padrão real de
`runtime/a_morte…/images/chapters/chapter_01/GENERATION_REPORT.md`:

```text
[USE CASE] illustration-story, NARCISO, IL-NN, categoria, rel
[CANON]    âncora de momento (sem revelar GT/hipótese preferida)
[FIGURE]   FV-NARCISO-01 via --reference <imagem aprovada>; decay_state; âncoras de fragmento visíveis
[REFLECTION] reflection_state; se ANOMALOUS: qual âncora (e só uma); rosto do reflexo ≤ PARTIAL
[COMPOSITION] symmetry · crop · gaze · zona do dominante · espaço negativo
[LIGHT]    uma fonte; direção; temperatura
[PALETTE]  papéis GROUND/INK/METAL/PULSE; pele dessaturada; grayscale-safe
[MATERIALS] 13.3
[VETOES]   VETO-N01..N14 repetidos por extenso (padrão eva: vetos em todo prompt)
[OUTPUT]   proporção por categoria; sem texto; sem marca d'água
```

Regras:

- `PROMPT_LEAKS_HYPOTHESIS` (HIGH, validador da obra): prompt contém nome de
  hipótese (`gêmeo`, `fantasma`, `alucinação`, `Amintas` como identidade do
  reflexo…) — o gerador não pode "saber".
- `GENERATION_REPORT.md` por prancha com prompt, modelo, referência, SHA-256,
  inspeção, anomalia declarada × observada.
- Exploração no tier `draft` (`MODEL_TIERS.yaml:80-86`); final em
  `chapter_final`; correção com `--edit`.

### 16.7 Aprovações

`REQUIRE_APPROVAL` (humano, com hash): todo `HERO`, todo `REFLECTION` com
`DOUBLE`/`ABSENT_REFLECTION`, toda nudez parcial, `IL-12`, `IL-18`, `IL-24`.
`SUGGEST`: `SYMBOL`, `CHAPTER`, `CALLBACK` sem figura.

---

## 17. Visual Narrative Progression

### 17.1 Gramática por ato (campos `ext.narciso`)

| Dimensão | Ato I — A SUPERFÍCIE | Ato II — O ESPELHO | Ato III — O FUNDO |
|---|---|---|---|
| domínio da composição | Narciso domina | Narciso divide o quadro | Narciso sai do quadro |
| `symmetry` | `STRICT` | `BROKEN` | `FRAGMENTED` |
| `crop` | `WIDE`/`MEDIUM` | `MEDIUM`/`CLOSE` | `CLOSE`/`EXTREME_CLOSE`/`TRACE` |
| espaço negativo | amplo, controlado | invadido por água/reflexo | irregular |
| água | ausente ou distante | invade páginas (margens de água em `SYMBOL`) | parada, total |
| `reflection_state` permitido | `NONE`, `FRAGMENTED`, `ANOMALOUS` (≥8) | todos exceto `ABSENT_REFLECTION` | todos |
| `decay_state` | D0 | D0–D2 | D3–D5 |
| rachaduras | fio | no rosto de pedra, na palma | na boca, na pedra que floresce |
| flores | bulbo | forçada | murcha → na rachadura |
| ornamento de abertura | inteiro | duplicado | incompleto |

### 17.2 Regras de progressão (`validate_narciso.py --mode plan`)

| id | Regra | Achado | Severidade |
|---|---|---|---|
| `VNP-01` | `symmetry` e `crop` respeitam a tabela do ato do capítulo | `ACT_GRAMMAR_VIOLATION` | MEDIUM |
| `VNP-02` | `decay_state` de cada prancha = estado projetado de `FIG-NARCISO` no capítulo | `DECAY_STATE_MISMATCH` | HIGH |
| `VNP-03` | no Ato III, pranchas com figura em quadro são ≤ as do Ato II | `DECAY_BODY_OVEREXPOSED` | MEDIUM |
| `VNP-04` | nenhuma prancha em superfície pública com `decay_state ≥ D2` | `PUBLIC_DECAY_EXPOSURE` | HIGH |

### 17.3 `FIG-NARCISO` como elemento com estados

```yaml
- id: FIG-NARCISO
  class: FIGURE
  identity_ref: "DOC:/images/canon/FACE_CANON.md#fv-narciso-01"     # campo novo (seção 25.4)
  meaning: "O corpo como obra que se consome."
  functions:
    - {function: CHARACTER, anchors: ["LEDGER:GT-NAR-02"]}
    - {function: TRANSFORMATION, anchors: ["SCENE:THE_CENTER", "SCENE:DSR_OCCURRENCES"]}
  states:
    - {id: D0_PRISTINE, initial: true, memory_state: S}
    - {id: D1_SLEEPLESS, memory_state: R}
    - {id: D2_FEVER, memory_state: T}
    - {id: D3_WITHERING, memory_state: T}
    - {id: D4_MARBLE, memory_state: P}
    - {id: D5_TRACE, memory_state: E}
  transitions:
    - {from: D0_PRISTINE, to: D1_SLEEPLESS, trigger: "SCENE:STATUE_BREAKS", display_from: NEXT_CHAPTER}
    - {from: D1_SLEEPLESS, to: D2_FEVER, trigger: "SCENE:THE_CENTER", display_from: NEXT_CHAPTER}
    - {from: D2_FEVER, to: D3_WITHERING, trigger: "LEDGER:EV-NAR-22", display_from: NEXT_CHAPTER}
    - {from: D3_WITHERING, to: D4_MARBLE, trigger: "LEDGER:EV-NAR-27", display_from: NEXT_CHAPTER}
    - {from: D4_MARBLE, to: D5_TRACE, trigger: "SCENE:THE_NAME_AT_DAWN", display_from: NEXT_CHAPTER}
```

### 17.4 Sigil `SIG-ESPELHO`

Mesmos estados de `SYM-ESPELHO` (15.1), render `GLYPH`, monocromático,
diferença entre estados por **forma** (moldura coberta, moldura vazia com
reflexo em linha, moldura com duas linhas, moldura rachada, duas molduras
frente a frente, moldura vazia sem linha). Estados que diferem só por cor são
reprovados (`STATE_DIFFERS_ONLY_BY_COLOR`).

### 17.5 "A identidade visual também definha"

Somente elementos **de exibição** definham: ornamentos de abertura, sigil,
peso das molduras, densidade de ouro nos acabamentos da parte III. Nunca o
corpo do texto, margens ou títulos (ST-09 `READING_LAYER_MUTATION`).

---

## 18. Book-as-Mirror System — `BOOK_AS_MIRROR_SYSTEM`

### 18.1 Níveis

| Nível | Mecanismo | Base existente | Decisão |
|---|---|---|---|
| estrutural | capítulos palíndromos `n ↔ 34−n` | campo `mirror_of` em `chapter_architecture` | REUSE (campo extra) |
| spread | imagem no verso + abertura no recto | `placement: OPEN` + `start_on_recto` (`build_kdp_docx.py:71-74`, `KDP_LAYOUT_DEFAULTS.yaml:75`) | REUSE |
| spread central | `IL-12` ocupa verso+recto no capítulo 17 | — | EXTEND (`pair_with`) |
| páginas quase idênticas distantes | pares `CALLBACK` (`IL-01↔IL-24`, `IL-02↔IL-22`, `IL-03↔IL-20`, `IL-04↔IL-19`, `IL-07↔IL-17`, `IL-10↔IL-23`) | `callback_of` | EXTEND |
| tipografia refletida | só em exibição: título de capítulo com duplicata espelhada em tinta muito clara nos capítulos com `reflection_presence: PRESENT` do Ato II | papéis tipográficos da autora | EXTEND opcional (asset de abertura) |
| superfícies de água | páginas negras de divisão de ato com textura de água parada | `compositions` `INTERIOR_PLATE` | REUSE |
| ocultação parcial | reflexos `OCCLUDED`/`FRAGMENTED` | 14.8 | REUSE |
| olhar | `gaze` declarado por prancha | `ext.narciso.gaze` | CREATE (obra) |
| objeto | capa × capa nua (seção 23.3) | `duality` + `reading_layer` + DJ-01..05 | REUSE |

### 18.2 Contrato do olhar (`gaze`)

| Valor | Uso permitido |
|---|---|
| `TOWARD_READER` | capa (`OUTER_TRUTH`), página de rosto, `IL-07` e `IL-12`; máximo 4 no livro (`IL-01` é de costas: `AWAY`) |
| `TOWARD_REFLECTION` | pranchas `REFLECTION` |
| `AWAY` | `BODY_DETAIL`, `DECAY` |
| `UNDETERMINED` | `IL-24` e toda composição em que não se sabe quem olha quem |

Regra `GAZE-01`: nenhuma prancha `TOWARD_READER` depois do capítulo 22 —
a partir do Ato III, **o livro para de olhar para o leitor**; o leitor
continua olhando. `GAZE_AFTER_WITHDRAWAL` (MEDIUM).

### 18.3 Tipografia narrativa

| Elemento | Regra | Evolução |
|---|---|---|
| título da obra | papel `TITLE` (serifa de alto contraste, caixa alta, tracking largo) | fixo |
| número de capítulo | romano, papel `CHAPTER_NUMBER` | fixo |
| título de capítulo | papel `CHAPTER_TITLE` | Ato I centrado; Ato II duplicata espelhada clara quando `PRESENT`; Ato III alinhamento deslocado 1 unidade de grade |
| capitular | serifa do corpo ampliada, 3 linhas | Ato I inteira; Ato II com fio duplo; Ato III com uma serifa ausente (asset, nunca fonte alterada) |
| ornamento | um fio fino | inteiro → duplicado → interrompido |
| espaçamento | tracking do título de capítulo +2% por ato | só exibição |
| corpo | papel `BODY` herdado de `KDP_LAYOUT` | **intocável** |

Capitular não existe no builder (D-N4). **Decidido no Slice 5: omissão** em
todas as edições (`planning/MIRROR_MANIFESTATION.yaml`, `decisions.drop_cap`);
a evolução por ato fica no ornamento, entregue como imagem abaixo do título.
Nunca exigir recurso tipográfico que o Kindle não renderiza de forma confiável.

### 18.4 Regras anti-gimmick

| id | Regra | Achado |
|---|---|---|
| `MIR-01` | nenhum texto de leitura espelhado ou invertido | `READING_LAYER_MUTATION` (ST-09) |
| `MIR-02` | nenhuma página exige espelho físico para ser lida (exceto um `INSERT` collector opcional, fora do miolo) | `MIRROR_REQUIRED_TO_READ` (HIGH, obra) |
| `MIR-03` | todo par `callback_of` declara ≥1 diferença e ≤1 diferença "impossível" | `CALLBACK_WITHOUT_CHANGE` / `CALLBACK_OVERLOADED` (MEDIUM) |
| `MIR-04` | pares estruturais `mirror_of` são simétricos (`a.mirror_of == b` ⇔ `b.mirror_of == a`) e somam 34 | `MIRROR_PAIR_BROKEN` (HIGH, obra) |
| `MIR-05` | legibilidade: toda prancha passa grayscale (V6) | existente |

### 18.5 Manifestação por edição

| Técnica | kindle_ebook | kdp_paperback | kdp_hardcover | collector |
|---|---|---|---|---|
| palíndromo estrutural | ✅ | ✅ | ✅ | ✅ |
| spread imagem/abertura | sequencial (refluível) | ✅ | ✅ | ✅ |
| spread central `IL-12` | duas páginas sequenciais | ✅ (sem arte na dobra) | ✅ | ✅ |
| callbacks distantes | ✅ | ✅ | ✅ | ✅ |
| duplicata tipográfica espelhada | OMIT | ✅ (asset) | ✅ | ✅ |
| capitular erodida | OMIT ou fallback simples | asset | asset | asset |
| páginas negras de ato | ✅ (tela) | ✅ (custo de tinta/page) | ✅ | ✅ |
| capa × capa nua | OMIT hidden truth | OMIT | OUTER no case (DJ-05) | ✅ |

---

## 19. Text/Image Relationship System

### 19.1 Três relações

| `text_relation` | Definição | Regra obrigatória |
|---|---|---|
| `COMPLEMENT` | a imagem acrescenta informação que o texto não dá | `adds` não vazio, e não é paráfrase do trecho-âncora (resíduo: `CHAPTER_IMAGE_DIRECTOR` + `VISUAL_DIRECTOR`) |
| `CONTRADICT` | a imagem cria dúvida sobre o texto | contradiz **percepção ou interpretação** do POV, **nunca fato canônico** (VP-05); declara `contradicts` (o que o POV acredita) |
| `FORESHADOW` | contém informação cujo significado só aparece depois | `payoff_anchor` resolvível em capítulo posterior; spoiler da prancha ≤ teto de exposição (V5) |

### 19.2 Regras

| id | Regra | Achado | Severidade |
|---|---|---|---|
| `TIR-01` | relação declarada em toda prancha | `TEXT_RELATION_MISSING` | HIGH (motor) |
| `TIR-02` | `FORESHADOW` com `payoff_anchor` posterior ao capítulo da prancha | `FORESHADOW_WITHOUT_PAYOFF` | HIGH (motor) |
| `TIR-03` | `CONTRADICT` sem `contradicts` ou contradizendo `facts` do ledger | `IMAGE_CONTRADICTS_CANON` | BLOCKER (motor) |
| `TIR-04` | `COMPLEMENT` sem `adds` | `LITERAL_ILLUSTRATION` | MEDIUM (motor) |
| `TIR-05` | `CONTRADICT` posicionado antes da âncora que ele contradiz | `CONTRADICTION_BEFORE_CLAIM` | MEDIUM (motor) |
| `TIR-06` | ≥25% de `FORESHADOW` no livro | `FORESHADOW_UNDERUSED` | LOW (obra) |

Por que `CONTRADICT` não quebra VP-05: o canon visual continua sem criar
fato; a imagem mostra **o que o narrador não percebeu ou percebeu de outro
modo**, e o ledger já tem o campo exato para isso — `interpretations[]` por
personagem × `facts`.

---

## 20. Reread Layer — `NARCISSUS_REREAD_LAYER`

### 20.1 Objetivo

> **O segundo Narciso não deve ser exatamente o mesmo livro que o primeiro
> Narciso. Não porque o conteúdo mudou. Porque o leitor mudou.**

### 20.2 Tipos de pista

| Tipo | Primeira leitura → segunda leitura | Canal |
|---|---|---|
| `RR-ROMANTIC_TO_NARCISSIST` | frase que soa amorosa → soa autocentrada | TEXT |
| `RR-SELFISH_TO_LOVING` | gesto egoísta → cuidado | TEXT |
| `RR-IMPOSSIBLE_REFLECTION` | reflexo comum → reflexo impossível dado evento posterior | ILLUSTRATION |
| `RR-ART_MEANING_SHIFT` | prancha decorativa aparente → evidência | ILLUSTRATION |
| `RR-OBJECT` | capa/guarda/sigil → segunda verdade | OBJECT |
| `RR-CHORUS` | admiração do Coro → confissão de posse | TEXT |

### 20.3 Registro proposto (`reread_clues[]`)

| id | Tipo | Onde | Primeira leitura | Gatilho posterior | Segunda leitura | Hipóteses/leituras tocadas |
|---|---|---|---|---|---|---|
| `RR-01` | IMPOSSIBLE_REFLECTION | `IL-05` (8) | reflexo na janela | `IL-12` (17): cicatriz "do lado errado" | a pinta já estava errada no 8 | PROJ, SUPER, SELF, GAZE |
| `RR-02` | ROMANTIC_TO_NARCISSIST | cap. 13 (`LOVE-E2`) | ele ouve a voz dela por saudade | cap. 21 ("Cópias") | a voz dela dizia as falas dele | LOVE-A/B |
| `RR-03` | SELFISH_TO_LOVING | cap. 5 (`LOVE-E1`) | crueldade | cap. 14 (inscrição de Amintas) | afastar podia ser proteção | LOVE-A/B |
| `RR-04` | ART_MEANING_SHIFT | `IL-02` (2) | lençóis sobre espelhos | `IL-22` (32) | o corredor foi preparado desde o início | GAZE, SUPER |
| `RR-05` | IMPOSSIBLE_REFLECTION | `IL-08` (11) | margem distante | cap. 23 (foto) | o mesmo ângulo impossível | OTHER, SUPER, PROJ |
| `RR-06` | OBJECT | capa (0) | Narciso olha o leitor | cap. 17 + cap. 33 | olhava o reflexo que a capa produz | GAZE |
| `RR-07` | CHORUS | cap. 1 | "nós o vimos primeiro" | cap. 33 | o Coro somos nós | GAZE |
| `RR-08` | ROMANTIC_TO_NARCISSIST | cap. 18 ("não fale") | vulnerabilidade | cap. 26 | queria uma superfície | LOVE-A/B |
| `RR-09` | IMPOSSIBLE_REFLECTION | fita do cap. 3 | criança sozinha | cap. 20 (duas respirações) | a pausa tinha o ritmo de outro fôlego | SUPER, PROJ, SELF |
| `RR-10` | ART_MEANING_SHIFT | `IL-10` (14) | rosto de pedra rachado | `IL-23` (32) | a rachadura era o lugar da flor | SUPER, GAZE, SELF |
| `RR-11` | SELFISH_TO_LOVING | cap. 24 (foto entregue) | livrar-se da imagem | cap. 32 (Eco guarda a foto e não a flor) | dar a ela a única imagem de si | LOVE-A/B |
| `RR-12` | OBJECT | guarda frontal (collector) | padrão de lençóis | guarda traseira | espelhos descobertos | GAZE |

### 20.4 Regras

| id | Regra | Achado | Severidade |
|---|---|---|---|
| `RRL-01` | todo `RR-*` tem gatilho em capítulo posterior ao da pista | `REREAD_CLUE_WITHOUT_TRIGGER` | HIGH |
| `RRL-02` | nenhum `RR-*` tem segunda leitura que resolva a ontologia ou o amor | `REREAD_RESOLVES_AMBIGUITY` | BLOCKER |
| `RRL-03` | ≥3 pistas por ato; ≥4 canais `ILLUSTRATION`/`OBJECT` no livro | `REREAD_LAYER_THIN` | MEDIUM |
| `RRL-04` | pistas `TEXT` apontam para `TEXT:` âncoras literais no manuscrito congelado (modo final) | `REREAD_ANCHOR_MISSING` | HIGH |
| `RRL-05` | revelações não ontológicas (dívida paga, inscrição, versões de Lia) usam o Second-Read do ledger (L5) sem retcon | ledger INV-10/INV-11 | BLOCKER |

### 20.5 Integração com o ledger

- Pistas `LOVE`: crenças `RB-LOVE-A`/`RB-LOVE-B` estabelecidas por eventos
  `LOVE-E*`, `left_open: true`.
- Pistas do Reflexo: crenças `RB-RFX-*`, `left_open: true` (9.5).
- Pistas não ontológicas com revelação real (ex.: quem pagou a dívida —
  revelado no 16): usar `beliefs.revises` normalmente; L5 pré-classifica
  `STRONG/PARTIAL/WEAK`. Registro na obra: `revelations[]` do canon
  interpretativo (`REV-INSCRIPTION`, `REV-DEBT`; Slice 6). As versões de Lia
  não são revelação — continuam evidência ambígua.

---

## 21. Physical Book / Possession Experience — `POSSESSION_EXPERIENCE`

### 21.1 Prioridade sensorial

```text
VISÃO → TOQUE → PESO → TEXTURA → SOM DAS PÁGINAS → EXPERIÊNCIA DE MANUSEIO
```

| Sentido | Decisão de produto | Onde é especificado | Viabilidade (seção 22) |
|---|---|---|---|
| visão | capa `LOW_KEY`, olhar, ouro | `compositions[FRONT_COVER]` | todos os alvos |
| toque | fosco + brilho localizado; relevo onde há significado | `finish_intents` | KDP: só laminação; collector: vendor |
| peso | capa dura; papel encorpado | `PRINT_SPEC` | KDP hardcover (case laminate); collector |
| textura | contraste fosco/brilho na água; relevo na rachadura | `FI-WATER`, `FI-CRACK` | simulado em KDP |
| som das páginas | papel de gramatura mais alta | `PRINTER_PROFILE` | só collector |
| manuseio | marcador de fita; guardas; bordas | superfícies collector | só collector |

### 21.2 Intenções de acabamento (todas com `meaning_element`)

| id | Alvo | Material / efeito preferido | Fallbacks | Significado (`meaning_element`) | Classe |
|---|---|---|---|---|---|
| `FI-TITLE` | `TITLE` na capa | `AGED_GOLD` / `METALLIC_FOIL` | `SIMULATED_METALLIC_PRINT` → `FLAT_ROLE_COLOR` | `SYM-OURO` | PREMIUM |
| `FI-WATER` | superfície de água da capa | `OBSIDIAN_GLOSS` / `SPOT_UV` | `CONTRAST_SIMULATION` → `OMIT` | `SYM-AGUA` | OPTIONAL |
| `FI-MIRROR-POOL` | forma da água na capa nua | `SILVER_MIRROR` / `MIRROR_BOARD` (novo) | `METALLIC_FOIL` → `SIMULATED_METALLIC_PRINT` → `OMIT` | `SYM-ESPELHO` | COLLECTOR_ONLY |
| `FI-CRACK` | rachadura no case | `STONE_MATTE` / `DEBOSS` | `TONAL_RELIEF_SIMULATION` → `OMIT` | `SYM-RACHADURA` | COLLECTOR_ONLY |
| `FI-FLOWER` | narciso na lombada do case | `IVORY` / `BLIND_EMBOSS` (`EMBOSS`) | `OMIT` | `SYM-NARCISO` | COLLECTOR_ONLY |
| `FI-EDGE` | borda frontal | `GROUND` + ondulação / `SPRAYED_EDGE` + `STENCILED_EDGE` | `OMIT` | `SYM-AGUA` | COLLECTOR_ONLY |
| `FI-BH-SEAL` | marca BH | `BURNT_COPPER` / `METALLIC_FOIL` | `SIMULATED_METALLIC_PRINT` → `FLAT_ROLE_COLOR` | autora (`AUTHORIAL_IDENTITY`) | ESSENTIAL (elemento) / PREMIUM (efeito) |

"Foil porque é premium" é reprovado: toda intenção acima aponta para um
símbolo com Chekhov (V2 herdado por acabamento).

### 21.3 Unboxing e ephemera

| Item | Forma | Regra de Chekhov | Superfície | Viabilidade |
|---|---|---|---|---|
| slipcase | caixa negra com janela de água espelhada | forma de `SYM-AGUA` | `BOX_*` / `SLIPCASE` (EXTEND) | terceiro |
| card 1 | transcrição da inscrição de Amintas (paráfrase própria) | `NARRATIVE_ARTIFACT` citado | `INSERT` (lacrado → SEMI_HIDDEN) | terceiro |
| card 2 | folha de contato de Íris (fotos discordantes, sem rosto nítido) | `NARRATIVE_ARTIFACT` (`RFX-05`) | `INSERT` | terceiro |
| marcador | fita negra | `SYM-AGUA` (fio de água) | `RIBBON` | terceiro |
| pôster | reprodução de `IL-12` sem texto | prancha aprovada | fora do livro (`PROMO`) | terceiro |
| embalagem | papel de seda negro, lacre `PULSE` | `SYM-OURO`/lacre só como marca da edição | fora do motor | terceiro |

Regra: **nenhuma ephemera genérica** (brindes sem vínculo narrativo). Todo item
é artefato citado ou prancha aprovada. Spoiler: cards `INSERT` só lacrados e
≤ `MEDIUM`.

### 21.4 Numeração e assinatura

Decisão comercial e logística **humana** (OQ-N8). O motor só registra em
`PRODUCTION_MANIFEST.printer_instructions` e nunca promete numeração em texto
de marketing de alvos KDP (`FINISH_PROMISE_MISMATCH` estendido por léxico:
"numerada", "assinada", "limitada").

### 21.5 Fragrância (pesquisa, fora do motor)

Não recomendada para o MVP. Se estudada para collector, checklist humano
obrigatório antes de qualquer decisão: segurança dermatológica, alergênicos
declarados, estabilidade no papel/tinta, interação com acabamentos,
logística e armazenamento, regulamentação de cosméticos/fragrâncias por
jurisdição de venda, custo e devolução. Nenhum campo de canon é criado para
isso.

---

## 22. Print Capability Matrix

Fonte: `engine/templates/EDITION_CAPABILITIES.yaml` (verificado em
**2026-09-14**) e `PRINT_GEOMETRY.yaml`. **Nada abaixo é afirmado como
disponível no KDP sem revalidação por `T699_KDP_REQUIREMENTS_REFRESH`** antes
de qualquer release.

| Item | `KDP_FEASIBLE` | `SPECIAL_EDITION_FEASIBLE` | `THIRD_PARTY_PRINTER_REQUIRED` | Evidência / nota |
|---|---|---|---|---|
| capa dura | ✅ (case laminate, sem sobrecapa) | ✅ | — | `EDITION_CAPABILITIES.yaml:101-130`; geometria hardcover `TO_VERIFY` |
| acabamento fosco / brilho | ✅ (laminação matte ou glossy, capa inteira) | ✅ | — | `LAMINATE_FINISH: PHYSICAL` |
| detalhes brilhantes localizados (spot UV) | ❌ → simulação de contraste | ✅ | ✅ | `SPOT_UV: UNSUPPORTED` KDP |
| hot stamping / foil | ❌ → impressão metálica simulada | ✅ | ✅ | `METALLIC_FOIL: UNSUPPORTED` KDP |
| relevo / baixo-relevo | ❌ → relevo tonal simulado | ✅ | ✅ | `EMBOSS/DEBOSS: UNSUPPORTED` KDP |
| verniz localizado | ❌ | ✅ | ✅ | `SELECTIVE_VARNISH: UNSUPPORTED` KDP |
| guardas ilustradas | ❌ (miolo pode ter prancha opcional) | ✅ | ✅ | `PRINTED_ENDPAPER: UNSUPPORTED` KDP |
| bordas decoradas | ❌ | ✅ | ✅ | `SPRAYED_EDGE/STENCILED_EDGE: UNSUPPORTED` KDP |
| sobrecapa | ❌ | ✅ | ✅ | `DUST_JACKET: UNSUPPORTED` KDP ("will not have a dust jacket") |
| papel premium | parcial (opções de papel/tinta KDP) | ✅ | ✅ | cor interior: paperback standard/premium; hardcover só premium (`:125`) |
| marcador de fita | ❌ | ✅ | ✅ | `RIBBON_MARKER: UNSUPPORTED` KDP |
| placa espelhada / papel metalizado | ❌ | ✅ | ✅ | **não existe na matriz** → EXTEND como `VENDOR_DEPENDENT` |
| slipcase / caixa | ❌ | ✅ | ✅ | superfície `BOX_*` é FUTURE na SDD irmã → EXTEND |
| cards / pôsteres | ❌ (fora do livro) | ✅ | ✅ | produto separado |
| edição numerada / assinatura | ❌ (não é capacidade de impressão KDP) | ✅ | ✅ + logística humana | decisão comercial |
| embalagem / unboxing | ❌ | ✅ | ✅ | fora do motor |
| fragrância | ❌ | ⚠ pesquisa | ✅ | seção 21.5; não recomendado |
| nudez parcial em capa | **a verificar** (diretrizes de conteúdo vigentes) | a verificar com gráfica/varejo | — | `T699`; política desta SDD: nenhuma nudez em superfície pública |
| ilustração colorida no miolo | ✅ com custo (standard/premium color) | ✅ | — | decisão OQ-N7; arte é grayscale-safe para permitir P&B |

---

## 23. Collector Edition Strategy

### 23.1 Linha de edições

| Edição | Alvo do motor | Conteúdo | Pré-condição |
|---|---|---|---|
| Kindle | `kindle_ebook` | texto + pranchas + aberturas; sem hidden truth | — |
| Brochura | `kdp_paperback` | P&B com pranchas grayscale-safe | `PRINT_SPEC.page_count` medido |
| Capa dura | `kdp_hardcover` | premium color opcional; case com OUTER_TRUTH | chaves `TO_VERIFY` resolvidas por `T699` |
| Colecionador | `collector` | sobrecapa, capa nua, guardas, bordas, fita, cards, slipcase | `layout/PRINTER_PROFILE.yaml` humano (OQ-N8) |

### 23.2 Capa (seções 15 e 16 da missão)

Critério: reação imediata **"eu quero esse livro"** antes de "sobre o que é".
Síntese: `CLASSICAL BEAUTY × DARK ROMANCE × LUXURY × MIRROR × DECAY`.

Variantes a explorar em `T043` (candidatos, não canon):

| Variante | Dominante | Olhar | Riscos (validador) | Força |
|---|---|---|---|---|
| `CV-A` rosto parcial | metade superior do rosto, olhos para o leitor, linha d'água cortando abaixo do nariz | `TOWARD_READER` | `FIGURE_ON_COVER` (override + aprovação), `VETO-N07` | armadilha máxima |
| `CV-B` água com olhar | superfície negra; só os olhos refletidos, invertidos | `UNDETERMINED` | thumbnail fraca (V4) | ambiguidade máxima |
| `CV-C` escultura | rosto de mármore negro rachado com olhos de ouro | `TOWARD_READER` | autocanibalização? não; watchlist não | clássico/luxo |
| `CV-D` mão | mão com cicatriz e anel tocando a água, reflexo da mão chegando antes | — | fragmento reconhecível (14.9) | tátil |
| `CV-E` flor | um narciso branco refletido como outra flor | — | genérico se sem âncora | delicado |
| `CV-F` composição dupla | rosto em cima, reflexo embaixo com uma âncora não espelhada | `UNDETERMINED` | dois dominantes? → um dominante com reflexo `SECONDARY` | tese inteira |
| `CV-G` ausência do rosto | capa só com água, anel e névoa | — | pode ler como thriller | máxima contenção |

**Decisão humana (OQ-N1, 2026-09-15):** Narciso **aparece na capa por
fragmento — parte do rosto**. A capa precisa estancar o olhar com **beleza
pura, bruta e apaixonante**, preservando parte do mistério. `CV-A` é a
direção canônica de `OUTER_TRUTH`; `CV-F` permanece como `HIDDEN_TRUTH`
(só collector). `CV-B` fica apenas como contingência técnica se nenhum
candidato passar a rubrica `COV-H`.

#### 23.2.1 Contrato do fragmento de capa (`COVER_FACE_FRAGMENT`)

```yaml
role_overrides:
  - key: defaults.forbid_literal_protagonist_on_cover
    value: false
    override_reason: "Decisão humana OQ-N1: a beleza de Narciso é a isca da tese; aparece por fragmento do rosto."
    approval: APR-COVER-01
compositions:
  - id: COMP-FRONT
    surface: FRONT_COVER
    reading_layer: OUTER_TRUTH
    elements:
      - {element: FIG-NARCISO, prominence: DOMINANT, state: D0_PRISTINE}
      - {element: SYM-AGUA, prominence: SECONDARY}
    ext:
      narciso:
        face_fragment: {visible_ratio_max: 0.60, required: [eyes, mole_right, brow_line], hidden_by: [water_line, shadow, frame_edge]}
        gaze: TOWARD_READER
        crop: EXTREME_CLOSE
```

| id | Regra | Verificação | Achado | Severidade |
|---|---|---|---|---|
| `COV-01` | **só parte do rosto**: nunca o rosto inteiro; ≤ 60% da face em quadro; boca ao menos parcialmente oculta por linha d'água, sombra ou borda | declarado + `FACE_QA` na miniatura | `COVER_FACE_FULLY_REVEALED` | HIGH |
| `COV-02` | olhos são o `DOMINANT` e o foco da miniatura (zona do dominante = olhos) | V4 `focal_point_ratio` na zona dos olhos | `THUMBNAIL_WEAK_FOCAL_POINT` (existente) | MEDIUM |
| `COV-03` | identidade reconhecível pelo fragmento: cor dos olhos, **pinta sob o olho direito**, sobrancelha reta, textura real de pele | `FACE_QA` + 14.9 | `FIGURE_FRAGMENT_UNRECOGNIZABLE` | HIGH |
| `COV-04` | beleza **bruta**, não de catálogo: pele com poros, cílios e imperfeições reais, sem filtro, sem brilho cosmético, sem simetria de modelo | rubrica `COV-H` + `VETO-N01` | `GENERIC_MALE_BEAUTY_COVER` | HIGH |
| `COV-05` | adulto inequívoco (27): linhas finas nos cantos dos olhos, ossatura adulta | `VETO-N07` + `FACE_QA` | `FACE_IDENTITY_FAILURE` (existente) | BLOCKER |
| `COV-06` | mistério preservado: o fragmento é o `D0_PRISTINE` de Narciso, **nunca** o Reflexo nem uma anomalia de espelho na capa pública | `reflection_state: NONE` obrigatório em `OUTER_TRUTH` | `COVER_REFLECTION_SPOILER` | HIGH |
| `COV-07` | sem nudez, sem ombros nus, sem expressão sensual explícita (a sedução está no olhar, não na pose) | `VETO-N02/N12` + `SOC-03` | `SURFACE_SPOILER` / `GENERIC_TROPE_UNJUSTIFIED` | HIGH |
| `COV-08` | tipografia não cobre os olhos; título na zona superior ou inferior, autora abaixo (hierarquia v1) | V4 + zonas declaradas | `ZONE_COLLISION_FOCAL` | MEDIUM |
| `COV-09` | gerado com `--reference` numa referência aprovada de `FV-NARCISO-01`; ≥ 6 candidatos no tier `draft` antes do final | `GENERATION_REPORT.md` | `REFLECTION_QA_SKIPPED` | HIGH |

**Rubrica humana `COV-H`** (aprovação `APR-COVER-01`, todas "sim"):

1. Parei de rolar a tela nesta capa, a 96 px?
2. É beleza que dá vontade de olhar de novo — e não "homem bonito de capa de romance"?
3. Sinto que ele está me olhando, e isso me incomoda um pouco?
4. Não sei o rosto inteiro dele, e quero saber?
5. Reconheço Bea Halden (paleta, tipografia, contenção)?
6. Depois de ler o capítulo 17, esta capa muda de sentido?

`CV-F` (capa nua, collector) mostra o mesmo fragmento visto do lado da água,
com **uma** âncora não espelhada e a área `FI-MIRROR-POOL` onde estariam os
olhos refletidos (23.3). Ela é a única superfície onde o espelho aparece.

### 23.3 A capa como armadilha — implementação sem gimmick

```text
OUTER_TRUTH (sobrecapa / capa KDP)
  Narciso olha diretamente para fora da capa. O comprador acredita que é olhado.

HIDDEN_TRUTH (capa nua, só collector)
  A mesma composição vista do lado da água: o olhar sobe da superfície.
  No lugar exato onde estariam os olhos refletidos, uma pequena área de
  SILVER_MIRROR (FI-MIRROR-POOL) devolve, desfocado, o rosto de quem segura o livro.
  Uma única âncora de Narciso não está espelhada (REF ANOMALOUS).

EFEITO APÓS A LEITURA
  Narciso talvez nunca tenha olhado para o comprador: olhava para o reflexo
  que a capa produz — que, na capa nua, é o próprio leitor.
```

Regras:

| id | Regra | Achado |
|---|---|---|
| `TRAP-01` | área espelhada ≤ 6% da face do case; baixo contraste; nunca "espelho de parque de diversão" | `MIRROR_GIMMICK` (HIGH, obra; aprovação humana) |
| `TRAP-02` | a camada escondida nunca aparece em alvos KDP | `HIDDEN_TRUTH_EXPOSED` (BLOCKER, existente) |
| `TRAP-03` | spoiler da capa nua ≤ `MEDIUM` | `HIDDEN_SURFACE_SPOILER` (existente) |
| `TRAP-04` | em KDP a armadilha é só narrativa: `OUTER_TRUTH` + releitura (`RR-06`) | — |
| `TRAP-05` | nenhum texto de marketing KDP menciona espelho físico | `FINISH_PROMISE_MISMATCH` |

### 23.4 Superfícies collector

| Superfície | Composição | Camada | Spoiler |
|---|---|---|---|
| `DUST_JACKET_FRONT` | `CV-A` | OUTER | LOW |
| `CASE_FRONT` (nua) | `CV-F` + `FI-MIRROR-POOL` + `FI-CRACK` | HIDDEN | MEDIUM |
| `CASE_SPINE` | narciso em relevo cego (`FI-FLOWER`) + marca BH | NEUTRAL | NONE |
| `ENDPAPER_FRONT` | padrão de lençóis sobre espelhos (seed de `IL-02`) | NEUTRAL | NONE |
| `ENDPAPER_BACK` | os mesmos espelhos descobertos (sem figura) | HIDDEN | MEDIUM |
| `EDGE_FORE` | preto com ondulação de água em stencil | NEUTRAL | NONE |
| `INSERT` | cards 1–2 lacrados | HIDDEN | MEDIUM |
| `RIBBON` | fita negra | NEUTRAL | NONE |

`PRODUCTION_MANIFEST` exige camadas nomeadas: `L_ART`, `L_TYPE`,
`L_FOIL_TITLE`, `L_SPOT_UV_WATER`, `L_MIRROR_POOL`, `L_DEBOSS_CRACK`,
`L_EMBOSS_FLOWER`, `L_EDGE_STENCIL`.

---

## 24. Social Object Design — `SHAREABLE_ARTIFACT_MAP`

### 24.1 Princípio

Nenhuma página é desenhada "para Instagram". O mapa é **descoberto** em
`T800_MEDIA_PACKAGE` a partir de composições **já aprovadas** por razões
narrativas; nada entra no livro por ser compartilhável (VP-01).

### 24.2 Mapa

| Artefato | Por que é belo por si | Spoiler | Uso público permitido | Edições |
|---|---|---|---|---|
| capa `OUTER_TRUTH` | o olhar que atravessa a vitrine | LOW | sim (Stories, loja) | todas |
| livro fechado (lombada + borda) | gramática Bea Halden + faixa de ouro + borda negra | NONE | sim | KDP (lombada), collector (borda) |
| páginas negras de ato | uma linha marfim sobre preto: "A SUPERFÍCIE" | NONE | sim | todas |
| sequência de sigils `VELADO` | molduras cobertas | NONE | sim | todas |
| `IL-01` | costas diante da estátua velada | NONE | sim | todas |
| `IL-07` | ouro sobre pele | NONE | sim, sem recorte erótico | todas |
| `IL-12` spread central | as mãos e a gota | MEDIUM | **não** antes de 90 dias do lançamento (decisão humana); nunca em Stories | todas |
| guardas collector | lençóis | NONE | sim | collector |
| capa nua | espelho que devolve o leitor | MEDIUM | só por leitores (não por marketing) | collector |
| frases curtas | trechos `TEXT:` do manuscrito congelado, ≤ 20 palavras, sem spoiler | ≤ LOW | sim | — |

### 24.3 Regras

| id | Regra | Achado |
|---|---|---|
| `SOC-01` | todo item de marketing cita composição aprovada ou âncora `TEXT:` literal | `FABRICATED_SHAREABLE` (HIGH, obra) |
| `SOC-02` | teto público `LOW` (Author DNA) vale para Stories, loja e descrição | `SURFACE_SPOILER` (existente) |
| `SOC-03` | nenhuma peça pública mostra `decay_state ≥ D2`, nudez, ou `reflection_state ∈ {DOUBLE, ABSENT_REFLECTION}` | `PUBLIC_DECAY_EXPOSURE` / `SURFACE_SPOILER` |
| `SOC-04` | reconhecibilidade do livro fechado: miniatura 96 px mantém título e olhar | V4 (existente) |
| `SOC-05` | frase pública nunca é uma das pistas `RR-*` | `REREAD_CLUE_EXPOSED` (MEDIUM, obra) |

---

## 25. Canon & Continuity Contracts

### 25.1 Arquivos de canon, donos e precedência

| Artefato | Dono / lock | Conteúdo | Muta por |
|---|---|---|---|
| `book/immutable_rules.yaml` | pacote (humano) | `IR-N01..N16` | edição do pacote + recompose |
| `book/BOOK_CONSTITUTION.md` | pacote (humano) | tese interna, leis dramáticas | idem |
| `canon/CANON_REGISTRY.yaml` | `CANON_GUARDIAN` / `CANON_WRITE` | fatos, `ENV-*`, `UNK-NAR-*`, `PRO-NAR-*` | `CANON_PROPOSALS` |
| `canon/CAUSAL_LEDGER.yaml` | `CANON_GUARDIAN` / `CANON_WRITE` | personagens, eventos `EV-*` (incl. `RFX`, `LOVE`, `DSR`), crenças | `CANON_PROPOSALS`, snapshots por wave |
| `canon/NARCISO_INTERPRETIVE_CANON.yaml` | `CANON_GUARDIAN` / `CANON_WRITE` | hipóteses, matriz de evidência, leituras de amor, ocorrências `DSR`, pistas `RR` | `CANON_PROPOSALS`, snapshots por wave |
| `canon/VISUAL_NARRATIVE_CANON.yaml` | `VISUAL_DIRECTOR` / `VISUAL_CANON_WRITE` | `book_dna`, símbolos, `FIG-*`, sigil, pranchas, capa, acabamentos | candidatos → decisão → snapshots PLAN/FREEZE |
| `images/canon/FACE_CANON.md` + `CHARACTER_VISUAL_BIBLE.md` | `FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT` / `FACE_CANON_WRITE` | `FV-NARCISO-01`, `FV-ECO-01`… | tarefa `T038/T039` e correções registradas |

Precedência (herdada e estendida):

```text
immutable_rules > BOOK_CONSTITUTION > CANON_REGISTRY / CAUSAL_LEDGER
  > NARCISO_INTERPRETIVE_CANON (leituras citam fatos; nunca os criam)
  > VISUAL_NARRATIVE_CANON (cita ambos; nunca cria fato — VP-05)
  > FACE_CANON / CHARACTER_VISUAL_BIBLE > bíblias > briefs > prosa / pixels
```

### 25.2 Canons pedidos → onde vivem (sem arquivo novo por conceito)

| Canon pedido | Local | Seção |
|---|---|---|
| `FACE_CANON` | `images/canon/FACE_CANON.md#fv-narciso-01` | 14.1 |
| `BODY_CANON` | `CHARACTER_VISUAL_BIBLE.md#narciso-corpo` | 14.3 |
| `HAIR_CANON` | `FACE_CANON.md#fv-narciso-01` (seção cabelo) | 14.2 |
| `WARDROBE_CANON` | `CHARACTER_VISUAL_BIBLE.md#narciso-figurino` | 14.5 |
| `AGE_CANON` | ledger `characters[].age` + `FACE_CANON` "aparência de idade" | 8.1, 14.1 |
| `SCAR_CANON` | `FACE_CANON.md` âncoras (cicatriz, pinta, anel) | 14.3, 14.8 |
| `SYMBOL_CANON` | `VISUAL_NARRATIVE_CANON.elements[SYM-*]` | 15 |
| `ENVIRONMENT_CANON` | `CANON_REGISTRY` `ENV-*` + `IMAGE_BIOME.md` | 25.6 |
| `REFLECTION_RULES` | `CHARACTER_VISUAL_BIBLE.md#reflection-rules` + `ext.narciso` | 14.8 |
| `DECAY_TIMELINE` | `VISUAL_NARRATIVE_CANON.elements[FIG-NARCISO].states` | 14.7, 17.3 |

### 25.3 Protocolo de consulta obrigatório antes de qualquer geração visual

```text
1. check_visual_canon.py --state FIG-NARCISO --at-chapter N      → decay_state
2. check_visual_canon.py --state SIG-ESPELHO --at-chapter N       → estado do sigil
3. check_visual_canon.py --exposure                                → teto de spoiler da superfície
4. validate_narciso.py --prancha IL-NN                             → reflection_state, anomalia declarada, gaze, crop
5. ler FACE_CANON#fv-narciso-01 (âncoras) + REFLECTION_RULES
6. escolher referência aprovada (--reference) compatível com o decay_state
7. escrever IL-NN_IMAGE_BRIEF.md (16.6) — sem nome de hipótese
8. gerar → GENERATION_REPORT.md (prompt, modelo, referência, SHA-256)
9. FACE_QA: rubrica do template (≥9/10 identidade, idade, pele/cabelo) + âncoras de fragmento
10. CONTINUITY_QA: anomalia declarada == anomalia observada; nenhuma anomalia extra; decay_state correto
11. VISUAL_DIRECTOR aprova (e humano quando REQUIRE_APPROVAL)
```

Qualquer passo pulado é registrado em `GENERATION_REPORT.md`; `CONTINUITY_QA`
sem a checagem 10 reprova (`REFLECTION_QA_SKIPPED`, HIGH).

### 25.4 Extensão da classe `FIGURE` (motor, neutra)

| Regra | Achado | Severidade |
|---|---|---|
| `FIG-01` todo `FIGURE` recorrente tem `identity_ref` resolvível (`DOC:` para `FACE_CANON`) | `FIGURE_WITHOUT_IDENTITY_REF` | HIGH |
| `FIG-02` `FIGURE` em `FRONT_COVER`/`CASE_*`/`DUST_JACKET_*` exige aprovação conforme `approval_policy_defaults.FIGURE_ON_COVER` | `FIGURE_ON_COVER_UNAPPROVED` | HIGH |
| `FIG-03` `FIGURE` com `states` segue ST-01..ST-09 (já genérico) | existentes | — |
| `FIG-04` `FIGURE` só pode aparecer em composição cujo estado projetado existe no capítulo | `FIGURE_STATE_UNRESOLVED` | HIGH |

Hoje o validador aceita `FIGURE` sem nenhuma dessas checagens (D-N2).

### 25.5 Consentimento e ética de gravação

- Todo evento adulto Narciso↔Eco tem bloco `consent` completo; `CONSENT_DRIFT`
  contra snapshot (INV-08).
- `NIGHT_WITHOUT_WORDS`: `consent.canonical: CONSENSUAL`,
  `ability_to_refuse: FULL`, `boundary_state: NEGOTIATED`; o sinal de parada
  combinado é `fact` do evento.
- Eco gravar Narciso sem consentimento (cap. 7) é `EV-ECO-07` com
  `knowledge_delta` e, quando descoberto, `relationship_delta` de confiança.
  Nunca vira gesto romântico (`ANTI_MANIPULATION_GUARDIAN`).

### 25.6 `ENVIRONMENT_CANON`

| id | Lugar | Âncoras visuais estáveis |
|---|---|---|
| `ENV-CAVA` | pedreira alagada | água negra parada; paredes de mármore com marcas de perfuração; um guindaste enferrujado; o Veio Nêmesis visível como faixa negra |
| `ENV-TERRACO` | terraço de pedra à beira da cava, onde fica a estátua | parapeito baixo; estátua de mármore negro sobre base com inscrição |
| `ENV-CASA` | casa de pedra dos Céfiso | janelas altas; pouca luz; molduras douradas vazias |
| `ENV-CORREDOR` | corredor dos espelhos cobertos | lençóis negros; espelhos altos em moldura de bronze |
| `ENV-QUARTO` | quarto de Narciso | cama baixa; bacia de água; espelhos migrados no Ato II |
| `ENV-ESTUFA` | estufa de Lia | bulbos de narciso; vidro embaçado |
| `ENV-OFICINA` | oficina de Teodoro | pó de mármore; ferramentas manuais |
| `ENV-ESTUDIO` | estúdio improvisado de Eco na biblioteca | fitas, gravador, fones, espuma acústica |

### 25.7 Snapshots e imutabilidade

| Canon | Snapshot | Produzido por |
|---|---|---|
| ledger | `CAUSAL_LEDGER.WAVE_NN.yaml` | existente |
| interpretativo | `NARCISO_INTERPRETIVE_CANON.WAVE_NN.yaml` | tarefa da obra com `tool` (`run_deterministic.py` executa `tool` de qualquer tarefa do grafo, inclusive `additional_tasks` — `run_deterministic.py:79,102`) |
| visual | `VISUAL_NARRATIVE_CANON.PLAN.yaml`, `.FREEZE.yaml` | existente |

Regra `ICN-IMM`: `reflection_evidence[*].support` e `love_readings[*]` de
eventos `REALIZED` são imutáveis contra o snapshot anterior
(`INTERPRETIVE_RETCON`, BLOCKER), no mesmo espírito de INV-10.

---

## 26. Gates & Validators

### 26.1 Princípio

**Nenhum gate novo.** Um validador da obra (`validate_narciso.py`, 5 modos)
anexado por `BOOK_GRAPH.gate_extensions` a gates existentes, mais os
validadores do motor já anexados pelas features, mais dois guardiões da obra
para o resíduo de julgamento.

Limite registrado (**D-N16**): `gate_extensions` só acrescenta
`custom_validators` (`livingbook.py:590-592`); não adiciona `requires` nem
dependências a tarefas do motor. Mitigação: o validador da obra reprova se o
artefato de uma tarefa adicional não existir — o efeito é bloqueante sem
tocar o motor.

### 26.2 Modos do validador da obra

| Modo | Validator id | Gate | Regras |
|---|---|---|---|
| `package` | `V_NARCISO_PACKAGE` | `GATE_CANON` | `MAC-*`, `MIR-04`, `DDC-01`, IR presentes, idades, léxicos declarados, `illustration_slots` coerentes |
| `plan` | `V_NARCISO_PLAN` | `GATE_CANON` e `GATE_LIVING_BOOK` | `UNC-01..06`, `LOV-01..03,05`, `DDC-02..05`, `RRL-01..03`, `SYMR-05`, `VNP-01..04`, `TIR-06`, `NO_HIDDEN_ANSWER` |
| `wave` | `V_NARCISO_WAVE_n` | `GATE_WAVE_n` | léxicos `UNC-07`, `LOV-04`, `REFLECTION_NAMED`, `DDC-06/07`, idade/juventude (seção 33), `ICN-IMM` |
| `final` | `V_NARCISO_FINAL` | `GATE_FULL_MANUSCRIPT` | tudo de `wave` no livro inteiro + `UNC-03,08`, `LOV-03,06`, `RRL-04,05`, final com exatamente 1 evidência |
| `illustrations` | `V_NARCISO_ILLUSTRATIONS` | `GATE_VISUAL`, `GATE_MEDIA_ASSETS` | `UNC-09`, `REF-01..04` (declarado), `PROMPT_LEAKS_HYPOTHESIS`, `REFLECTION_QA_SKIPPED`, `SOC-*`, `TRAP-01` (declarado) |

Comando no padrão de `a_morte/BOOK_GRAPH.yaml`:
`'"..\..\.venv\Scripts\python.exe" book\validators\validate_narciso.py --runtime . --mode <modo>'`.

### 26.3 Gates pedidos → implementação

| Gate pedido | Implementação | Gate existente | Bloqueia | Resíduo de julgamento |
|---|---|---|---|---|
| `MYTH_DNA_GATE` | `V_NARCISO_PACKAGE` (`MAC-*`) + `T602` | `GATE_CANON`, `GATE_LEGAL` | sim | `NARCISSUS_AMBIGUITY_GUARDIAN` |
| `REFLECTION_AMBIGUITY_GATE` | `UNC-*` + `REF-*` | `GATE_CANON`, `GATE_WAVE_n`, `GATE_FULL_MANUSCRIPT`, `GATE_VISUAL` | sim | `NARCISSUS_AMBIGUITY_GUARDIAN` |
| `LOVE_AMBIGUITY_GATE` | `LOV-*` | idem | sim | `NARCISSUS_AMBIGUITY_GUARDIAN`, `SUBTEXT_EDITOR` |
| `CHARACTER_CONTINUITY_GATE` | ledger L1/L2/L10 | `GATE_WAVE_n` | sim | `CHARACTER_CONTINUITY_REVIEWER` |
| `VISUAL_CONTINUITY_GATE` | `T4NN/T45NN_FACE_QA` + `CONTINUITY_QA` + `FIG-*` + 25.3 | `GATE_VISUAL` | sim | `FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT`, `IMAGE_CONTINUITY_QA` |
| `ILLUSTRATION_CANON_GATE` | V2/V5 + `TIR-*` (motor) + `VNP-*` (obra) | `GATE_LIVING_BOOK`, `GATE_FULL_MANUSCRIPT` | sim | `VISUAL_DIRECTOR` |
| `TABOO_INTENT_GATE` | `IR-N11` + léxico de parentesco em cena adulta + cena protegida | `GATE_WAVE_n` | sim | `DESIRE_DECAY_GUARDIAN`, `ANTI_MANIPULATION_GUARDIAN` |
| `CONSENT_CONTINUITY_GATE` | ledger L8 (`CONSENT_DRIFT`, `CONSENT_MISSING`) | `GATE_CANON`, `GATE_WAVE_n`, `GATE_FULL_MANUSCRIPT` | **sempre** | `ANTI_MANIPULATION_GUARDIAN` |
| `ADULT_CHARACTER_GATE` | ledger INV-06 + `IR-N05/N06` + `VETO-N07` + léxico de juventude | todos | **sempre** | `ANTI_MANIPULATION_GUARDIAN`, `FACE_QA` |
| `REPETITION_GATE` | `detect_repetition.py` + `book/text_quality.yaml` + `DDC-02..04` | `GATE_WAVE_n` | estrutural sim; lexical editorial | `EMOTIONAL_REPETITION_AUDITOR`, `REPETITION_AND_CLICHE_REVIEWER` |
| `REREAD_CLUE_GATE` | `RRL-*` + ledger L5 | `GATE_CANON` (plano), `GATE_FULL_MANUSCRIPT` | sim | `PROTECTED_SCENE_AUDITOR` + humano |
| `SYMBOL_EVOLUTION_GATE` | ST-01..09 + `SYMR-*` | `GATE_LIVING_BOOK`, `GATE_FULL_MANUSCRIPT` | sim | `SYMBOLISM_ARCHITECT` |
| `BEA_HALDEN_VOICE_GATE` | `T156/T157` + `LITERARY_STYLE_GUARDIAN` + léxicos | `GATE_VOICE` | sim (humano) | `LITERARY_STYLE_GUARDIAN` |
| `PRINT_FEASIBILITY_GATE` | V7/V8 + `FINISH_PROMISE_MISMATCH` + `T699` | `GATE_KDP` | sim | `KDP_REQUIREMENTS_RESEARCHER` |
| `COPYRIGHT_GATE` | `T600..T604` + `IMITATION_REFERENCE` + `MAC-04` + `VETO-N05/N06/N14` | `GATE_LEGAL` | sim | `COPYRIGHT_ORIGINALITY_AUDITOR` |
| `CANON_CONTRADICTION_GATE` | `check_canon_continuity.py` + L0/L10 + `VISUAL_RETCON` + `ICN-IMM` | `GATE_WAVE_n`, `GATE_FULL_MANUSCRIPT` | sim | `CANON_GUARDIAN` |
| *(adicional)* `DECAY_DIGNITY` | `IR-N08` + `DDC-07` + `VETO-N08` + `VNP-04` | `GATE_WAVE_n`, `GATE_VISUAL` | **sempre** | `DESIRE_DECAY_GUARDIAN` |

Nenhum destes gates está em `non_blocking_gates` de `STANDARD` ou `PREMIUM`
(`EXECUTION_PROFILES.yaml:55-68`).

### 26.4 Guardiões da obra (`books/narciso/agents/`)

| Agente | Tier | Escopo | Estados de rejeição |
|---|---|---|---|
| `NARCISSUS_AMBIGUITY_GUARDIAN` | S | ontologia do Reflexo; ambiguidade do amor; Coro; léxico de confirmação; final | `ONTOLOGY_CONFIRMED_FAILURE`, `LOVE_RESOLVED_FAILURE`, `EXPLANATORY_CLOSURE_FAILURE` |
| `DESIRE_DECAY_GUARDIAN` | S | curva de desejo; significado por recorrência; teto de explicitude; dignidade do definhamento; tabu; representação responsável de compulsão e autonegligência | `EXPLICITNESS_ESCALATION_FAILURE`, `DECAY_GLAMOUR_FAILURE`, `TABOO_INTENT_FAILURE` |

Precedente exato: `eva/agents/mystery_ambiguity_guardian.toml` (Tier S,
léxico, capítulos, "report findings; do not rewrite prose").

`book_specific_rejection_states` no `BOOK_SPEC`: os seis acima +
`MYTH_DNA_FAILURE`, `REFLECTION_FACE_RESOLVED_FAILURE`,
`CHILDHOOD_PROXIMITY_FAILURE`.

### 26.5 Agent packs propostos

```yaml
agent_packs:
  book_agents:
    NARCISSUS_AMBIGUITY_GUARDIAN: {profile: /book/agents/narcissus_ambiguity_guardian.toml}
    DESIRE_DECAY_GUARDIAN:        {profile: /book/agents/desire_decay_guardian.toml}
  character_support: [CHARACTER_PSYCHOLOGIST, ANTI_MANIPULATION_GUARDIAN, DESIRE_DECAY_GUARDIAN]
  canon_guardians:   [CANON_GUARDIAN, NARCISSUS_AMBIGUITY_GUARDIAN, ANTI_MANIPULATION_GUARDIAN, DESIRE_DECAY_GUARDIAN]
  wave_reviewers:    [NARCISSUS_AMBIGUITY_GUARDIAN, ANTI_MANIPULATION_GUARDIAN, DESIRE_DECAY_GUARDIAN,
                      CHARACTER_CONTINUITY_REVIEWER, PLOT_CONTINUITY_REVIEWER, EMOTIONAL_EDITOR]
  voice_reviewers:   [LITERARY_STYLE_GUARDIAN, SUBTEXT_EDITOR, PHYSICALITY_AND_BODY_AGENT, ANTI_MANIPULATION_GUARDIAN]
  critic_panel:      [LITERARY_CRITIC, COMMERCIAL_EDITOR_CRITIC, DEVELOPMENTAL_EDITOR, NARCISSUS_AMBIGUITY_GUARDIAN]
  line_reviewers:    [LITERARY_STYLE_GUARDIAN, SUBTEXT_EDITOR, SENSORY_AGENT, PHYSICALITY_AND_BODY_AGENT,
                      TYPOGRAPHY_TEXT_REVIEWER, REPETITION_AND_CLICHE_REVIEWER, EMOTIONAL_REPETITION_AUDITOR]
```

Guardiões éticos ficam nas **primeiras posições** dos packs: com limite de
rotação em `STANDARD` (`wave_reviewers_limit: 3`), a rotação ainda garante que
eles leiam toda wave par/ímpar; recomendação é `PREMIUM`, sem limite.

---

## 27. Metrics

### 27.1 Princípio

> **Métricas são instrumentos de diagnóstico. Nenhuma métrica aprova um
> capítulo, uma imagem ou o livro.**

Três naturezas, nunca misturadas: **estrutural** (script, determinística),
**julgamento** (agente, 0–10 em `quality_profile.yaml`, padrão do motor) e
**humana** (rubrica em checkpoint).

### 27.2 Métricas pedidas

| Métrica | Vale criar? | Natureza | Cálculo | Uso | Risco de otimização cega |
|---|---|---|---|---|---|
| `VISUAL_DESIRE_SCORE` | **não como número** | humana | rubrica sim/não em `APR` de capa e `HERO`: (1) quero pegar? (2) reconheço Bea Halden? (3) não é romance genérico? (4) o olhar me incomoda um pouco? (5) sobrevive a 96 px? | decisão de aprovação | um número de "desejo" empurraria para o clichê que a watchlist proíbe |
| `REFLECTION_AMBIGUITY_SCORE` | sim | estrutural + julgamento | estrutural: `min(hipóteses S por evidência)`, `hipóteses viáveis no fim`, `razão max/min de S`; julgamento: `reflection_ambiguity` ≥ 9 | diagnóstico de `UNC-*` | contar `S` sem página que sustente → guardião decide |
| `LOVE_AMBIGUITY_SCORE` | sim | estrutural + julgamento | estrutural: `min(love, narcissism)` por evento; saldo STRONG; julgamento: `love_ambiguity` ≥ 9 | `LOV-*` | idem |
| `SYMBOL_DENSITY` | sim | estrutural | menções por símbolo por 1.000 palavras por capítulo (`check_visual_canon.py --evidence`) + contagem por superfície | alerta de excesso/ausência | limiares só depois de calibração contra o manuscrito real (padrão `TEXT_QUALITY_DEFAULTS.yaml`) |
| `REREAD_VALUE` | sim | estrutural + humana | nº de `RR-*` com gatilho válido, `FORESHADOW`, `CALLBACK`; pré-classificação L5; rubrica humana de releitura parcial (atos I–II após o fim) | diagnóstico | contar pistas ≠ releitura boa |
| `VISUAL_CANON_CONSISTENCY` | sim | estrutural + julgamento | rubrica `FACE_QA` (≥9/10 identidade, idade, pele/cabelo); taxa anomalia declarada = observada (alvo 100%); `DECAY_STATE_MISMATCH` = 0 | bloqueio via QA existente | — |

### 27.3 `quality_profile.yaml` proposto

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: BookQualityProfile
chapter_scores:
  authenticity_of_characters: {minimum: 9}
  scene_strength:             {minimum: 8}
  subtext:                    {minimum: 9}
  sensory_concreteness:       {minimum: 9}
  coherence:                  {minimum: 9}
  emotional_impact:           {minimum: 8}
  reflection_ambiguity:       {minimum: 9}
  love_ambiguity:             {minimum: 9}
  eco_agency:                 {minimum: 9}
  symbol_evolution:           {minimum: 8}
  rereadability:              {minimum: 8}
risk_scores:
  sentimentalism:             {maximum: 2}
  effect_phrase_overuse:      {maximum: 2}
  cliche:                     {maximum: 2}
  continuity:                 {maximum: 1}
  ontology_overexplanation:   {maximum: 0}
  motive_declaration:         {maximum: 0}
  explicitness_escalation:    {maximum: 0}
  decay_glamorization:        {maximum: 0}
  generic_male_beauty:        {maximum: 1}
  psychological_self_explanation: {maximum: 1}
required_checks:
  - toda evidência do Reflexo sustenta ao menos duas hipóteses
  - nenhum pensamento de Narciso declara o próprio motivo
  - toda ocorrência DSR tem função nova e consequência
  - todo capítulo do Coro fica fora da mente de Narciso
  - toda cena adulta registra consentimento e idades
  - todo símbolo destacado muda de significado ao mudar de estado
```

---

## 28. Task Graph Integration

### 28.1 Tarefas existentes que NARCISO usa com novos inputs (sem mudar o motor)

| Tarefa | Recebe (via pacote/`creative_sources`/runbooks) | Produz para NARCISO |
|---|---|---|
| `T010_MASTER_BRIEF` | `CREATIVE_BRIEF`, `BOOK_CONSTITUTION`, `planning/01_SOURCE_CANON.md`, `02_ADAPTATION_DELTA.md` | brief com Myth DNA |
| `T013_CHARACTER_BIBLE` | seção 8 | GT/SM/SP (incl. `GT-NAR-01 CONTRADICTION`) |
| `T015_SYMBOL_BIBLE` | seção 15 | evolução dos 7 símbolos |
| `T016_PLOT_DEPENDENCY_MAP` | seções 7, 9, 10, 11 | eventos `PLANNED` `RFX`/`LOVE`/`DSR` |
| `T018_CANON_REGISTRY` | idem | ledger + `UNK-NAR-*`/`PRO-NAR-*` |
| `T032_READER_VITALS` | seção 5.3 | as três perguntas por ato |
| `T035_MEMORY_MOTIF_MAP` | seção 20 | pistas `RR` ligadas a `RB-*` |
| `T036/T037` | `planning/NARCISSUS_VISUAL_BIBLE.md` | spec visual e bioma |
| `T038/T039` | seção 14 | `FV-NARCISO-01`, corpo, reflexo, definhamento |
| `T042/T043` | seções 13–19, 23 | canon visual com pranchas e capa |
| `T1NN_BRIEF_CHAPTER` | campos `desire_stage`, `reflection_presence`, `love_evidence`, `illustration_slots` | briefs com teto de explicitude e evidência pretendida |
| `T156/T157` | `planning/VOICE_PROFILE.md` | voz aprovada |
| `T602` | canon visual (já), `planning/02_ADAPTATION_DELTA.md` | originalidade de cadeia de cenas e composição |
| `T699` | seção 22 | revalidação KDP (inclui diretrizes de conteúdo de capa) |

### 28.2 Tarefas adicionais da obra (`BOOK_GRAPH.additional_tasks`)

| id | Fase | Dono | Depende de | Saída | `tool` |
|---|---|---|---|---|---|
| `T018N_INTERPRETIVE_CANON` | CANON | `CANON_GUARDIAN` (lock `CANON_WRITE`) | `T018_CANON_REGISTRY` | `/canon/NARCISO_INTERPRETIVE_CANON.yaml` | — |
| `T019N_AMBIGUITY_REVIEW` | CANON | `NARCISSUS_AMBIGUITY_GUARDIAN` | `T018N_INTERPRETIVE_CANON` | `/reviews/NARCISO_AMBIGUITY_REVIEW.md` | — |
| `T021N_INTERPRETIVE_SNAPSHOT` | CANON | `CANON_GUARDIAN` | `T019N_AMBIGUITY_REVIEW` | `/canon/snapshots/NARCISO_INTERPRETIVE_CANON.WAVE_00.yaml` | `{python} book/validators/validate_narciso.py --runtime {runtime} --snapshot-as WAVE_00` |

`V_NARCISO_PLAN` em `GATE_CANON` reprova se as três saídas não existirem
(mitigação de D-N16). Snapshots de waves seguintes: o `CANON_UPDATE` de cada
wave chama o mesmo comando (instrução no runbook da obra), porque o pacote não
pode injetar tarefas dentro do laço de waves do motor.

### 28.3 Ilustrações: slots no pacote, não no canon

**Decisão arquitetural (DL-N01):** o grafo é composto **antes** de o canon
visual existir. Logo, tarefas por prancha não podem ser enumeradas a partir
do runtime. Os ids das pranchas são declarados no pacote em
`chapter_architecture[].illustration_slots` (aprovados por humano), e:

1. `compose` gera, para cada slot, `T45NN_IL_BRIEF → T45NN_IL_GENERATE →
   T45NN_IL_FACE_QA → T45NN_IL_CONTINUITY_QA → T45NN_IL_APPROVE`
   (EXTEND do motor, Slice 4; ausência de slots ⇒ grafo idêntico ao golden);
2. `T043` deve realizar **exatamente** esses ids como `compositions`
   (`ILLUSTRATION_SLOT_MISMATCH`, HIGH);
3. `GATE_VISUAL.requires` inclui os `T45NN_IL_APPROVE`.

### 28.4 Checkpoints humanos

Perfil recomendado: **`PREMIUM`** (`GATE_CANON`, `GATE_VOICE`,
`GATE_FULL_MANUSCRIPT`, `GATE_KDP`), mais aprovações visuais por decisão
(`APR-*`): Author DNA override de figura, capa `OUTER`/`HIDDEN`, `IL-12`,
`IL-18`, `IL-24`, todo `HERO`, toda nudez parcial, `TRAP-01`.

---

## 29. Proposed Schemas

> Contratos propostos em YAML, no padrão dos templates executáveis do motor.
> Nenhum JSON Schema (D2 da SDD irmã: schemas JSON não são executados).

### 29.1 `books/narciso/BOOK_SPEC.yaml` (excerto)

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: BookSpec
metadata:
  slug: narciso
  title: Narciso
  author: Bea Halden
  language: pt-BR
  genre: dark romance psicológico / gótico / horror de identidade / tensão erótica adulta
  chapter_count: 33
  version: 0.1.0
spec:
  execution_profile: PREMIUM
  creative_sources: [CREATIVE_BRIEF.md, BOOK_CONSTITUTION.md, planning/01_SOURCE_CANON.md,
                     planning/02_ADAPTATION_DELTA.md, planning/NARCISSUS_VISUAL_BIBLE.md,
                     planning/VOICE_PROFILE.md]
  movements:
    - {name: I — A Superfície, chapters: [1,2,3,4,5,6,7,8,9,10,11]}
    - {name: II — O Espelho,  chapters: [12,13,14,15,16,17,18,19,20,21,22]}
    - {name: III — O Fundo,   chapters: [23,24,25,26,27,28,29,30,31,32,33]}
  writing_waves: [[1,2,3,4,5,6], [7,8,9,10,11], [12,13,14,15,16,17], [18,19,20,21,22], [23,24,25,26,27,28], [29,30,31,32,33]]
  voice_calibration_chapters: [1, 6, 17, 18]
  lead_novelist_owned_chapters: [1, 6, 11, 12, 17, 18, 23, 26, 29, 31, 32, 33]
  features:
    living_book: {enabled: true}
    images: {enabled: true, primary_per_chapter: 0, illustration_slots: true}   # illustration_slots: EXTEND (Slice 4)
    living_sound: {enabled: false}
    translation_preparation: {enabled: false, target: en}
    kdp_docx: {enabled: true}
    media_package: {enabled: true}
    causal_ledger: {enabled: true, min_payoff_feeds: 2, max_monotonic_run: 3, max_loop_silence: 6}
    visual_narrative:
      enabled: true
      author_profile: bea_halden
      author_dna_version: 1
      edition_targets: [kindle_ebook, kdp_paperback, kdp_hardcover, collector]
      budget: COLLECTOR
      sigils: true
  symbol_priorities: [espelho, água, narciso, ouro, mármore, rachadura, gota]
  book_specific_rejection_states: [ONTOLOGY_CONFIRMED_FAILURE, LOVE_RESOLVED_FAILURE, EXPLANATORY_CLOSURE_FAILURE,
                                   EXPLICITNESS_ESCALATION_FAILURE, DECAY_GLAMOUR_FAILURE, TABOO_INTENT_FAILURE,
                                   MYTH_DNA_FAILURE, REFLECTION_FACE_RESOLVED_FAILURE, CHILDHOOD_PROXIMITY_FAILURE]
```

`primary_per_chapter: 0` não tem efeito hoje (D-N1); o comportamento vem de
`illustration_slots` (Slice 4, implementado): com a flag, o grafo gera as tarefas
por prancha no lugar da imagem única por capítulo.

### 29.2 `chapter_architecture.yaml` (uma entrada)

```yaml
- number: 17
  title: O Centro
  movement: II — O Espelho
  pov: Narciso
  desire_stage: RITUAL
  mirror_of: 17
  reflection_presence: PRESENT
  love_evidence: null
  function: Tentativa de tocar o que olha de volta; as mãos não chegam juntas.
  dramatic_question: O que acontece quando o desejo encontra a superfície?
  irreversible_turn: O espelho quebra e a cicatriz da palma reabre.
  illustration_slots: [IL-12]
  continuity: [cicatriz na palma esquerda, uma única gota, nenhuma fala do reflexo]
```

### 29.3 Bloco `illustration` (motor) + `ext.narciso` (obra) numa composição

```yaml
compositions:
  - id: IL-12
    surface: INTERIOR_PLATE
    reading_layer: IN_READING
    elements:
      - {element: FIG-NARCISO, prominence: DOMINANT}
      - {element: SYM-GOTA, prominence: SECONDARY}
      - {element: SYM-ESPELHO, prominence: SUPPORTING}
    atmosphere: "luz fria lateral; superfície negra; a gota é a única claridade"
    approval: {policy: REQUIRE_APPROVAL, id: APR-IL-12}
    illustration:                                  # EXTEND do motor — neutro de gênero
      category: HERO                               # vocabulário declarado pela obra
      text_relation: FORESHADOW                    # COMPLEMENT | CONTRADICT | FORESHADOW
      adds: null                                   # obrigatório em COMPLEMENT
      contradicts: null                            # obrigatório em CONTRADICT
      payoff_anchor: "SCENE:THE_NAME_AT_DAWN"      # obrigatório em FORESHADOW
      callback_of: null
      pair_with: SPREAD                            # SPREAD | null | id de outra composição
      placement_anchor: 'TEXT:17:"a gota"'         # resolvida só em modo realized
    ext:
      narciso:                                     # validado só por validate_narciso.py
        reflection_state: ANOMALOUS_MIRROR
        reflection_anomaly: scar                   # mole | ring | scar | part | mouth | decay_offset | angle
        decay_state: D1_SLEEPLESS
        gaze: TOWARD_READER
        symmetry: BROKEN
        crop: CLOSE
        hypotheses_supported: [H-PROJ, H-SUPER, H-SELF, H-GAZE]
        reader_emotion: "desejo de tocar junto; desconforto de não saber quem chega primeiro"
```

### 29.4 `canon/NARCISO_INTERPRETIVE_CANON.yaml`

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: NarcisoInterpretiveCanon
metadata: {project_id: narciso, version: 0.1.0, owner: CANON_GUARDIAN, ledger_ref: /canon/CAUSAL_LEDGER.yaml}
policy:
  no_hidden_answer: true                 # nenhum campo guarda a "verdade" do Reflexo
  min_support_per_evidence: 2
  min_viable_hypotheses_at_end: 3
reflection_hypotheses:
  - {id: H-PROJ,  label: projeção/alucinação}
  - {id: H-SUPER, label: manifestação sobrenatural}
  - {id: H-SELF,  label: o próprio Narciso}
  - {id: H-OTHER, label: outra pessoa real}
  - {id: H-GAZE,  label: nascido da contemplação}
reflection_evidence:
  - id: RFX-07
    event: EV-NAR-17                      # evento do ledger (kind inclui REFLECTION_EVIDENCE)
    perception: "as mãos não chegam juntas à superfície; uma gota cai"
    support:  {H-PROJ: S, H-SUPER: S, H-SELF: S, H-OTHER: "-", H-GAZE: S}
    illustrations: [IL-12]
    status: PLANNED                       # PLANNED | REALIZED (espelha o evento do ledger)
love_readings:
  - id: LOVE-E5
    event: EV-NAR-18
    gesture: "pede que ela fique e não fale"
    love: {reading: "vulnerabilidade: palavras o ferem", strength: STRONG}
    narcissism: {reading: "quer uma superfície silenciosa", strength: STRONG}
    beliefs: [RB-LOVE-A, RB-LOVE-B]
    status: PLANNED
desire_occurrences:
  - id: DSR-4
    event: EV-NAR-22
    function: NEED
    pleasure: LOW
    explicitness_ceiling: SENSUAL
    consequence: "tranca-se na sala de espelhos e entrega a chave a Eco"
    status: PLANNED
reread_clues:
  - id: RR-01
    type: IMPOSSIBLE_REFLECTION
    channel: ILLUSTRATION
    clue: {composition: IL-05, chapter_anchor: "TURN:8"}
    trigger: {composition: IL-12, chapter_anchor: "SCENE:THE_CENTER"}
    first_read: "reflexo na janela"
    second_read: "a pinta já estava do lado errado"
    touches: [H-PROJ, H-SUPER, H-SELF, H-GAZE]
mutation_log:
  - {version: 0.1.0, task: T018N_INTERPRETIVE_CANON, owner: CANON_GUARDIAN, action: "Consolidação a partir de seeds/INTERPRETIVE_CANON.seed.yaml."}
```

### 29.5 `books/narciso/BOOK_GRAPH.yaml`

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: BookGraphExtensions
metadata: {slug: narciso, version: 0.1.0}
spec:
  custom_validators:
    - {id: V_NARCISO_PACKAGE,       command: '"..\..\.venv\Scripts\python.exe" book\validators\validate_narciso.py --runtime . --mode package'}
    - {id: V_NARCISO_PLAN,          command: '"..\..\.venv\Scripts\python.exe" book\validators\validate_narciso.py --runtime . --mode plan'}
    - {id: V_NARCISO_FINAL,         command: '"..\..\.venv\Scripts\python.exe" book\validators\validate_narciso.py --runtime . --mode final'}
    - {id: V_NARCISO_ILLUSTRATIONS, command: '"..\..\.venv\Scripts\python.exe" book\validators\validate_narciso.py --runtime . --mode illustrations'}
    # V_NARCISO_WAVE_1..6: um id por wave, --mode wave --through-chapter N
  gate_extensions:
    GATE_CANON:           {validators: [V_NARCISO_PACKAGE, V_NARCISO_PLAN]}
    GATE_LIVING_BOOK:     {validators: [V_NARCISO_PLAN]}
    GATE_FULL_MANUSCRIPT: {validators: [V_NARCISO_FINAL]}
    GATE_VISUAL:          {validators: [V_NARCISO_ILLUSTRATIONS]}
    GATE_MEDIA_ASSETS:    {validators: [V_NARCISO_ILLUSTRATIONS]}
  additional_tasks:
    - {id: T018N_INTERPRETIVE_CANON, phase: CANON, owner: CANON_GUARDIAN, depends_on: [T018_CANON_REGISTRY],
       locks: [CANON_WRITE], outputs: [/canon/NARCISO_INTERPRETIVE_CANON.yaml]}
    - {id: T019N_AMBIGUITY_REVIEW, phase: CANON, owner: NARCISSUS_AMBIGUITY_GUARDIAN, depends_on: [T018N_INTERPRETIVE_CANON],
       outputs: [/reviews/NARCISO_AMBIGUITY_REVIEW.md]}
    - {id: T021N_INTERPRETIVE_SNAPSHOT, phase: CANON, owner: CANON_GUARDIAN, depends_on: [T019N_AMBIGUITY_REVIEW],
       tool: '{python} book/validators/validate_narciso.py --runtime {runtime} --snapshot-as WAVE_00',
       outputs: [/canon/snapshots/NARCISO_INTERPRETIVE_CANON.WAVE_00.yaml]}
```

### 29.6 Extensão de `EDITION_CAPABILITIES.yaml` (motor, dados)

```yaml
# novas chaves de efeito (todos os alvos KDP: UNSUPPORTED; collector: VENDOR_DEPENDENT)
MIRROR_BOARD: VENDOR_DEPENDENT
METALLIZED_PAPER: VENDOR_DEPENDENT
BLIND_EMBOSS: VENDOR_DEPENDENT
SLIPCASE: VENDOR_DEPENDENT
INSERT_CARD: VENDOR_DEPENDENT
# nova superfície collector
surfaces: [..., SLIPCASE_FRONT, SLIPCASE_SPINE]
```

### 29.7 Pseudocódigo de `validate_narciso.py`

```text
main(runtime, mode):
  ctx = load(book/, canon/CAUSAL_LEDGER, canon/NARCISO_INTERPRETIVE_CANON,
             canon/VISUAL_NARRATIVE_CANON, manuscript/ (se existir), images/prompts/ (se existir))
  findings = []
  if mode in {package}:        findings += myth_dna(ctx) + mirror_pairs(ctx) + desire_stage_curve(ctx)
                                           + adult_ages(ctx) + slots_consistency(ctx)
  if mode in {plan, final}:    findings += uncertainty(ctx) + love(ctx) + desire_occurrences(ctx)
                                           + reread(ctx) + symbol_meaning(ctx) + act_grammar(ctx)
                                           + no_hidden_answer(ctx) + ledger_crossref(ctx)
  if mode in {wave, final}:    findings += lexicon(ctx.manuscript[..N], LEXICONS) + childhood_proximity(ctx)
                                           + interpretive_immutability(ctx, baseline)
  if mode == final:            findings += final_evidence_count(ctx) + closure(ctx) + reread_anchors(ctx)
  if mode == illustrations:    findings += reflection_face(ctx) + prompt_leaks(ctx) + qa_reports(ctx)
                                           + public_exposure(ctx)
  emit(findings)  # shape REVIEW_FINDING; exit 1 se HIGH/BLOCKER (convenção check_*.py)
```

Dependências: stdlib + PyYAML (já instaladas). Nenhuma chamada de modelo.

---

## 30. Testing Strategy

Convenção do repositório: `unittest`, offline, execução por módulo (D10: não
rodar `tests/test_image_generation.py`, que faz chamada paga).

| Camada | O que prova | Onde | Determinístico |
|---|---|---|---|
| Unit (obra) | cada regra `MAC/UNC/LOV/DDC/RRL/SYMR/VNP/TIR/MIR/REF/SOC/TRAP` isolada | `tests/test_narciso_book.py` | sim |
| Contract | seed do canon interpretativo e fixture passam; achados no shape `REVIEW_FINDING`; léxicos carregados | idem | sim |
| Cross-reference | todo `RFX/LOVE/DSR` ↔ evento do ledger; todo `IL` ↔ slot ↔ composição | idem | sim |
| Mutation (negativos, categoria exata) | ver 30.1 | idem | sim |
| Motor (Slices 4, 5, 7) | `illustration`, `FIGURE`, slots, pares, novas chaves de edição | `tests/test_visual_canon.py`, `tests/test_compose_regression.py` | sim |
| Golden | grafos dos livros existentes idênticos; DOCX/capa sem plano idênticos em bytes | goldens existentes | sim |
| Integration | compose do pacote `narciso` em diretório temporário + `smoke-test` + `validate-gate GATE_CANON` sobre fixture | `tests/test_narciso_book.py` | sim |
| Humano | releitura, desejo visual, ambiguidade sentida, voz | checkpoints | não |
| Pago opcional | geração de 3 pranchas-piloto + 3 capítulos | Slice 8 | não; nunca na suíte |

### 30.1 Testes negativos obrigatórios (cada um afirma a categoria)

| Mutação sobre fixture válida | Categoria esperada |
|---|---|
| `RFX-03.support` só com um `S` | `SINGLE_HYPOTHESIS_EVIDENCE` |
| `RFX-14.support` com `X` em cinco hipóteses | `EVIDENCE_COLLAPSES_ONTOLOGY` |
| `X` acumulado deixa 2 hipóteses viáveis | `ONTOLOGY_CONVERGED` |
| manuscrito fixture com "era uma alucinação" na narração | `ONTOLOGY_CONFIRMED_IN_PROSE` |
| capítulo 34 com "carta explicativa" | `EXPLANATORY_CLOSURE` |
| `LOVE-E3.narcissism.strength: WEAK` | `LOVE_READING_WEAK` |
| pensamento "porque a amava" em POV Narciso | `LOVE_MOTIVE_DECLARED` |
| `DSR-5.explicitness_ceiling: FRANK` | `EXPLICITNESS_ESCALATION` |
| `DSR-3.function: PLEASURE` (repetida) | `REPETITION_WITHOUT_NEW_MEANING` |
| cena adulta com fita de infância na mesma cena | `CHILDHOOD_EROTIC_PROXIMITY` |
| Reflexo como `participant` com `age: null` | `ADULT_SEDUCTION_FAIL` (ledger, BLOCKER) |
| `desire_stage` volta de COMPULSION para RITUAL sem âncora | `DESIRE_STAGE_REGRESSION` |
| `mirror_of` do cap. 6 = 27 | `MIRROR_PAIR_BROKEN` |
| `IL-05` com duas anomalias | `REF-03` → `REFLECTION_OVERLOADED` |
| `IL-18` com rosto do reflexo `FULL` | `REFLECTION_FACE_RESOLVED` |
| prompt de `IL-16` contém "gêmeo" | `PROMPT_LEAKS_HYPOTHESIS` |
| `FORESHADOW` sem `payoff_anchor` | `FORESHADOW_WITHOUT_PAYOFF` |
| `CONTRADICT` contra `facts` do ledger | `IMAGE_CONTRADICTS_CANON` |
| Story com `IL-18` | `PUBLIC_DECAY_EXPOSURE` |
| `FIGURE` sem `identity_ref` | `FIGURE_WITHOUT_IDENTITY_REF` |
| campo `truth` do Reflexo presente no canon | `HIDDEN_ANSWER_PRESENT` |
| descrição KDP com "capa espelhada" | `FINISH_PROMISE_MISMATCH` |
| `RR-04` com segunda leitura "era um fantasma" | `REREAD_RESOLVES_AMBIGUITY` |
| diário de Lia na fixture menciona "irmão gêmeo" de Narciso | `TWIN_HYPOTHESIS_INTRODUCED` |
| composição de capa `CV-A` com rosto inteiro visível | `COVER_FACE_FULLY_REVEALED` |
| evento adulto do cap. 18 com `explicitness_ceiling: FRANK` | `NIGHT_EXPLICITNESS_ABOVE_CEILING` |
| `SYM-NARCISO` com `count: 3` | `UNJUSTIFIED_COUNT` |

Fixtures **não contêm prosa erótica nem descrição explícita**: só ids,
estados, percepções resumidas e trechos neutros de 1–2 frases para âncoras
`TEXT:`.

---

## 31. Failure Modes

| Failure mode | Como aparece | Detecção | Onde |
|---|---|---|---|
| Modernização rasa do mito | "Narciso influencer com selfie" | `MAC-02`, `VETO-N09`, guardião | canon |
| Mito irreconhecível | flor, Eco ou água somem | `MYTH_DNA_LOST` | package |
| Reflexo explicado | fala, laudo, carta, epílogo | `UNC-07/08`, guardião | wave/final |
| Convergência lenta de hipóteses | cada pista empurra para "sobrenatural" | `UNC-03/05` | plan/final |
| Resposta escondida vaza | brief "sabe" a verdade | `NO_HIDDEN_ANSWER`, `PROMPT_LEAKS_HYPOTHESIS` | todos |
| Amor resolvido | pensamento declara motivo | `LOV-04` | wave |
| Balança inclinada | narcisismo sempre mais forte | `LOV-02` | plan |
| Pornografia gratuita | ocorrência sem nova função | `DDC-02/05`, guardião | plan/wave |
| Escalada de explicitude | cada DSR mais gráfica | `DDC-03` (BLOCKER) | plan/wave |
| Glamour do definhamento | magreza como beleza | `IR-N08`, `DDC-07`, `VETO-N08` | wave/visual |
| Codificação juvenil | "menino" em cena sensual; rosto infantil | léxico de juventude + `VETO-N07` + FACE_QA | wave/visual |
| Eco vira espelho | sem decisões próprias | `IR-N15`, `eco_agency` ≥ 9 | wave |
| Coro onisciente | "ele pensou" num capítulo do Coro | `IR-N14`, guardião | wave |
| Narciso de banco de imagens | rosto simétrico, abdômen | `VETO-N01/02`, FACE_QA | visual |
| Deriva de rosto | pinta migra, cabelo muda | FACE_QA + `--reference` | visual |
| Anomalia acidental | gerador inverte pinta sem declaração | `REF-04` | visual |
| Reflexo nítido demais | rosto completo | `UNC-09` | visual |
| Ilustração literal | repete o parágrafo | `LITERAL_ILLUSTRATION` | plan |
| Imagem contradiz fato | prancha "corrige" o ledger | `IMAGE_CONTRADICTS_CANON` | plan |
| Símbolo decorativo | ouro "porque é luxo" | V2 Chekhov + `meaning_element` | plan |
| Símbolo sem evolução | estado muda, significado não | `SYMBOL_STATE_WITHOUT_NEW_MEANING` | plan |
| Gimmick de espelho | capa-espelho de parque | `TRAP-01`, aprovação | edition |
| Hidden truth no KDP | capa nua em case laminate | `HIDDEN_TRUTH_EXPOSED` | edition |
| Promessa falsa de acabamento | "foil" na página da Amazon | `FINISH_PROMISE_MISMATCH` | edition |
| Spoiler social | Story com `IL-18` | `PUBLIC_DECAY_EXPOSURE` | assets |
| Autocanibalização Bea Halden | NARCISO repete maçã/cobre/reflexo-testemunha da noiva | 13.6 + revisão humana | plan |
| Cópia iconográfica | pose de pintura célebre | `VETO-N05`, `T602` | legal |
| Retcon interpretativo | leitura muda depois de realizada | `ICN-IMM` | wave |
| Host recusa cena adulta | prosa suaviza ou falha | `CAPABILITY_BLOCKER`; nunca contornar; `HEAT ≠ EXPLICITNESS` | wave |
| Overengineering | engine por conceito | seção 4; 0 gates; 1 validador | processo |
| Custo explode | 24 pranchas + collector em todo alvo | `cost_class`, `budget`, OQ-N7 | plan |

---

## 32. Copyright / Public-Domain Considerations

| Tema | Consideração | Decisão |
|---|---|---|
| Ovídio, *Metamorphoses* III | texto antigo, domínio público | fonte primária; citações só em tradução própria e curta |
| traduções | traduções modernas podem ser protegidas | nenhuma tradução é usada sem verificação de `T601`; preferência por paráfrase própria |
| epígrafe opcional | verso latino da maldição ("sic amet ipse licet, sic non potiatur amato", *Met.* III — conferir numeração na edição usada) | latim original + tradução própria; decisão humana |
| variantes (Cônon; Pausânias excluída) | antigas, domínio público | Cônon só como raiz de `H-OTHER`; a variante da irmã gêmea não é usada (OQ-N2) |
| iconografia clássica | pinturas antigas em domínio público; **fotografias** de acervos podem ter termos próprios | nenhuma reprodução; nenhuma composição copiada (`VETO-N05`) |
| obras modernas sobre Narciso/Eco | pinturas, romances, filmes e traduções do século XX em diante podem estar protegidos | clean-room: não consultar durante arquitetura, prosa ou arte (`MAC-04`) |
| título "Narciso" | título isolado geralmente não é protegido por direito autoral, mas pode colidir com obras e marcas existentes | decisão comercial/legal humana (OQ-N11) |
| Bea Halden | pseudônimo decidido (SDD irmã S) | `metadata.author`; nenhuma persona em prosa |
| marca BH SEAL | registro é decisão legal humana (SDD visual OQ-6) | inalterado |
| imagens geradas por IA | proveniência (prompt, modelo, referência, hash) e divulgação conforme política KDP vigente | `GENERATION_REPORT.md` + `T699` |
| semelhança com pessoas reais | rostos ficcionais | `VETO-N14`, `FACE_CANON` |
| fontes tipográficas | licença e incorporação | `typography_bindings` com `license` e `embeddable: true` (existente) |
| referências de gênero | referência ≠ imitação; sem nomes de autoras, títulos ou "no estilo de" | `IMITATION_REFERENCE`, `T602` compara cadeia de cenas |

Nada nesta seção é parecer jurídico. As decisões finais de proveniência e
colisão são de `LEGAL_EDITOR_GLOBAL`/`LEGAL_EDITOR_BR` e do humano.

---

## 33. Safety / Adult Character Rules

### 33.1 Idade adulta

| Regra | Implementação |
|---|---|
| todo personagem com presença erótica ou de sedução tem ≥18 anos canônicos | ledger INV-06 (BLOCKER em todo perfil) |
| Narciso 27, Eco 31; membros nomeados do Coro ≥21 | `characters[].age` |
| **o mito tem Narciso aos dezesseis; o livro não** | `IR-N05`; nenhum texto, brief ou prompt cita a idade mítica |
| Reflexo nunca aparenta idade diferente da de Narciso | `IR-N05`, `REF-02` (só `decay_offset` 0/−1, nunca rejuvenescimento de idade) |
| nenhuma hipótese implica menor | `H-SELF` nunca é "Narciso criança" em contexto sensual; não existe hipótese de gêmeo (OQ-N2, `UNC-10`) |
| sem codificação juvenil em texto | léxico de juventude proibido em cenas com `desire_stage ≥ EXCITATION` e em qualquer cena adulta: "menino", "garoto", "rapazinho", "adolescente", "juvenil", "infantil", equivalentes (lista final na Obra) |
| sem codificação juvenil em imagem | `VETO-N07`, rubrica `FACE_QA` "aparência abaixo de 25 anos" |
| material de infância nunca próximo de erotismo | `IR-N06`, `CHILDHOOD_EROTIC_PROXIMITY` (BLOCKER) |

### 33.2 Consentimento

- Silêncio, beleza, dívida, gratidão ou compulsão nunca são consentimento
  (`IR-N12`).
- `NIGHT_WITHOUT_WORDS`: consentimento verbal prévio, sinal de parada
  combinado, revogabilidade explícita, capacidade plena.
- Gravação sem consentimento tem consequência e nunca é romantizada (25.5).

### 33.3 Compulsão, autonegligência e desaparecimento

| Risco | Regra |
|---|---|
| compulsão sexual como diagnóstico | nenhum termo clínico como resposta (`IR-N04`); comportamento mostrado com consequência |
| autonegligência e fome | sem medidas corporais, peso ou magreza celebrada (`IR-N08`); o declínio é contado por perda de luz, sono, gesto e voz |
| desaparecimento de Amintas e final de Narciso | nenhum ato de autolesão narrado, nenhum método, nenhuma romantização da morte como solução bela (`IR-N10`, `IR-N16`) |
| sedução estética da destruição | 5.4: a beleza do objeto nunca promete que a destruição é bela; superfícies públicas sem definhamento |

### 33.4 Nota de conteúdo

Recomendação: **nota de conteúdo breve na front matter** (conteúdo sexual
entre adultos, obsessão, compulsão, autonegligência, desaparecimento, horror
psicológico). Front matter não viola `IR-N09` (que proíbe paratexto
**interpretativo** após o fim). Redação final e eventual página de recursos de
apoio: decisão humana (OQ-N13), sempre antes do capítulo 1.

### 33.5 Limites do hospedeiro

Se o modelo hospedeiro recusar ou suavizar conteúdo adulto, registrar
`CAPABILITY_BLOCKER`; **nunca** contornar políticas. O desenho não depende de
explicitude: teto máximo `FRANK` só em `DSR-2/3`, e `HEAT ≠ EXPLICITNESS`.

### 33.6 Ilustrações

Nenhuma ilustração representa ato sexual ou genitália (`VETO-N12`); nenhuma
nudez em superfície pública; conteúdo de capa sujeito às diretrizes KDP
vigentes (`T699`).

---

## 34. Acceptance Criteria

### 34.1 Checklist desta SDD

| Critério | Status | Onde |
|---|---|---|
| discovery real do repositório com evidências | ✅ | 2, Apêndice A |
| REUSE / EXTEND / CREATE classificado | ✅ | 4 |
| Myth DNA e mapa de reinterpretação | ✅ | 6 |
| Uncertainty Principle com mecanismos de validação | ✅ | 9 |
| `LOVE_EVIDENCE_MATRIX` | ✅ | 10.2 |
| curva de desejo com repetição por significado e adultos | ✅ | 11, 33 |
| Visual Bible, Visual DNA, Symbol Registry | ✅ | 13, 14, 15 |
| Illustration Canon com metadados e categorias | ✅ | 16 |
| progressão visual por ato | ✅ | 17 |
| Book-as-Mirror, texto×imagem, releitura | ✅ | 18, 19, 20 |
| posse, matriz de impressão sem afirmar KDP indevidamente, collector, social | ✅ | 21–24 |
| continuidade (face, corpo, cabelo, figurino, idade, cicatriz, símbolo, ambiente, reflexo, definhamento) | ✅ | 14, 25 |
| gates mapeados sem gate novo | ✅ | 26 |
| métricas como diagnóstico | ✅ | 27 |
| integração ao grafo, schemas, testes, falhas, copyright, segurança | ✅ | 28–33 |
| slices ajustadas pela arquitetura real | ✅ | 35 |
| nenhuma implementação, prosa ou arte produzida | ✅ | só este arquivo foi criado |

### 34.2 `NARCISO_IDENTITY_TEST` — "Isso parece NARCISO?"

**Estrutural (o motor responde sozinho):**

| # | Pergunta | Fonte |
|---|---|---|
| S1 | Todo Myth DNA está presente e reinterpretado? | `MAC-01` |
| S2 | Toda evidência do Reflexo sustenta ≥2 hipóteses e ≥3 sobrevivem ao fim? | `UNC-01/03` |
| S3 | Nenhuma confirmação ontológica ou de motivo amoroso no texto? | `UNC-07`, `LOV-04` |
| S4 | Toda leitura de amor é dupla e o final é duplo? | `LOV-01/03` |
| S5 | A curva de desejo progride e a explicitude decresce do meio para o fim? | `DDC-01/03` |
| S6 | Todas as idades ≥18 e nenhuma codificação juvenil lexical? | INV-06, 33.1 |
| S7 | Todos os símbolos mudam de estado e de significado por evento? | ST-02, `SYMR-05` |
| S8 | Narciso é o mesmo em todas as pranchas (anomalias só as declaradas)? | FACE_QA, `REF-04` |
| S9 | O palíndromo estrutural e os callbacks estão íntegros? | `MIR-03/04` |
| S10 | Toda prancha tem relação texto×imagem válida e ≥25% `FORESHADOW`? | `TIR-*` |
| S11 | Nenhuma superfície pública mostra spoiler, definhamento ou nudez? | V5, `SOC-03` |
| S12 | Nenhum acabamento é prometido onde não é físico? | `FINISH_PROMISE_MISMATCH` |

**Humano (o motor prepara, a pessoa decide):**

| # | Pergunta |
|---|---|
| H1 | Diante da capa: "eu quero esse livro" antes de "sobre o que é"? |
| H2 | Eu reconheceria Narciso por uma mão, um olho, uma nuca? |
| H3 | Ao terminar, eu sei dizer quem é o Reflexo? (a resposta certa é "não, mas tenho uma teoria") |
| H4 | Consigo defender que ele amou **e** que nunca amou, com passagens reais? |
| H5 | Relendo o Ato I, alguma imagem mudou de significado? |
| H6 | Dias depois: por que eu também fiquei fascinado? |
| H7 | A beleza do livro me pareceu perigosa, e não uma celebração da destruição? |
| H8 | Soa como Bea Halden sem soar como *A Noiva Esquecida*? |

### 34.3 Tese

```text
NARCISO_STRUCTURAL = PROVEN   ao fim do Slice 2 (narrativa) e do Slice 4 (ilustração)
  o motor representa e verifica ambiguidade, desejo, idade, símbolo e prancha sobre fixtures
NARCISO_EXPERIENCE = PROVEN   só com livro físico e leitores humanos (S1–S12 verdes + H1–H8 "sim")
```

---

## 35. Implementation Slices

Ajustadas depois do discovery. Diferenças em relação à proposta da missão:

1. **Validadores não ficam para o fim**: cada slice entrega suas regras e
   testes negativos (padrão das duas capabilities existentes).
2. **Releitura se divide**: o plano entra com o canon narrativo (Slice 2); a
   verificação contra prosa congelada vem antes do manuscrito final (Slice 6).
3. **O bootstrap textual pode começar antes das ilustrações**: o pipeline de
   imagem só roda depois de `GATE_FULL_MANUSCRIPT` (D-N13); Slices 4–5 precisam
   estar prontos antes desse gate, não antes de `GATE_CANON`.
4. **Pré-condição de todo slice que toque o motor**: commitar o working tree
   atual (D-N14) para goldens estáveis.

### Slice 0 — Discovery (**concluído: este documento**)

- **Entrega:** esta SDD. **Arquivos:** `docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md`.
- **Aceite:** OQ-N1..OQ-N5 decididas pelo humano em 2026-09-15 (36.1). ✅

### Slice 1 — Pacote narrativo NARCISO (sem tocar o motor) — **concluído em 2026-09-15**

> Entregue: `books/narciso/` (pacote completo, planning, validador em modo
> `package`) e `tests/test_narciso_book.py` (37 testes). Resultados:
> `validate_narciso.py --mode package` → `VALID, findings=0`;
> `validate-book` → `BOOK PACKAGE VALID | Narciso | chapters: 33`; compose +
> smoke-test em diretório temporário OK. Desvios do plano: auditores das cenas
> protegidas usam agentes do motor com `planned_auditor` para os guardiões do
> Slice 2 (o grafo exige dono existente); OQ-N9 e OQ-N12 seguem as
> recomendações da SDD, pendentes de confirmação.

- **Objetivo:** `books/narciso/` válido e composto, com canon proposto das seções 6–12.
- **Arquivos (novos):** `BOOK_SPEC.yaml`, `CREATIVE_BRIEF.md`, `BOOK_CONSTITUTION.md`,
  `immutable_rules.yaml`, `protected_scenes.yaml`, `chapter_architecture.yaml` (33),
  `quality_profile.yaml`, `capability_requirements.yaml`, `text_quality.yaml`,
  `visual_profile.md`, `sound_profile.md`, `seeds/WORLD_RULES_SEED.md`,
  `planning/01_SOURCE_CANON.md`, `planning/02_ADAPTATION_DELTA.md`,
  `planning/VOICE_PROFILE.md`, `validators/validate_narciso.py` (modo `package`),
  `tests/test_narciso_book.py`.
- **Regras:** `MAC-*`, `MIR-04`, `DDC-01`, idades, léxicos declarados.
- **Testes:** pacote → PASS; mutações de `MYTH_DNA_LOST`, `MIRROR_PAIR_BROKEN`,
  `DESIRE_STAGE_REGRESSION`, idade < 18.
- **Aceite:** `validate-book --book books/narciso` → `VALID`; compose em
  diretório temporário + `smoke-test OK`; nenhuma alteração fora de `books/narciso/` e `tests/`.
- **Complexidade:** M (conteúdo) · S (código).

### Slice 2 — Canon interpretativo e guardiões (obra) — **concluído em 2026-09-15**

> Entregue: `seeds/INTERPRETIVE_CANON.seed.yaml` (5 hipóteses, 15 evidências,
> 9 leituras de amor, 6 ocorrências, 1 intimidade, 15 pistas de releitura),
> `agents/narcissus_ambiguity_guardian.toml` e `agents/desire_decay_guardian.toml`,
> `INTERPRETIVE_CANON_RUNBOOK.md`, `BOOK_GRAPH.yaml` (validadores em
> `GATE_CANON`, `GATE_LIVING_BOOK`, `GATE_WAVE_1..6`, `GATE_FULL_MANUSCRIPT`;
> tarefas `T018N`, `T019N`, `T021N` e snapshots por wave `T201N..T206N`),
> `validate_narciso.py` com modos `plan`, `wave`, `final` e `--snapshot-as`.
> Testes: `tests/test_narciso_book.py` → 88 testes OK; suíte existente 274 OK.
> Desvio do plano: em vez de uma fixture de 6 capítulos commitada, o teste
> compõe o pacote real num diretório temporário e deriva ledger, registry e
> manuscrito neutro da própria semente. Cenas protegidas de ambiguidade e de
> desejo agora são auditadas pelos guardiões da obra.

- **Objetivo:** Uncertainty Principle, Love Ambiguity, desejo/definhamento e plano de releitura verificáveis.
- **Arquivos:** `seeds/INTERPRETIVE_CANON.seed.yaml`, `agents/narcissus_ambiguity_guardian.toml`,
  `agents/desire_decay_guardian.toml`, `BOOK_GRAPH.yaml`, `validate_narciso.py` (modos `plan`, `wave`, `final`, `--snapshot-as`),
  fixture mini-runtime (6 capítulos neutros, ledger mínimo, sem prosa erótica).
- **Regras:** `UNC-*`, `LOV-*`, `DDC-02..08`, `RRL-01..03`, `NO_HIDDEN_ANSWER`, `ICN-IMM`, léxicos.
- **Testes:** seção 30.1 (parte narrativa); verificar em compose real se `additional_tasks`
  entram na ordem esperada e se o `tool` de `T021N` roda por `run_deterministic.py`.
- **Aceite:** `NARCISO_STRUCTURAL` (narrativa) = PROVEN; `validate-gate GATE_CANON` executa `V_NARCISO_*` na fixture.
- **Complexidade:** M.

### Slice 3 — Canon visual da obra (obra + decisões humanas) — **concluído em 2026-09-15**

> Entregue: `planning/NARCISSUS_VISUAL_BIBLE.md`, `planning/FACE_CANON.seed.md`,
> `planning/CHARACTER_VISUAL_BIBLE.seed.md`, `seeds/VISUAL_NARRATIVE_CANON.seed.yaml`
> (FIG-NARCISO com D0–D5, 7 símbolos com estados e significado por estado,
> SIG-ESPELHO, capa por fragmento do rosto, capa nua do collector, lombada,
> contracapa, abertura, 14 vetos, 4 acabamentos com prata só como
> `SILVER_MIRROR`), `seeds/VISUAL_CANDIDATES.seed.yaml`, léxico
> `decay_glamour`, modo `visual` do validador da obra em `GATE_LIVING_BOOK`.
> Resultados: o validador do motor (`check_visual_canon.py --mode plan`) roda
> sobre o canon da obra sem HIGH/BLOCKER — só `PENDING_APPROVAL` (MEDIUM),
> esperado até as aprovações humanas; figura, sigil e os 7 símbolos com status
> Chekhov `PROVEN`; `--state FIG-NARCISO` projeta D0 1–14, D1 15–17, D2 18–22,
> D3 23–27, D4 28–31, D5 32–33. Testes: 117 OK; suíte existente 274 OK.
> Desvio: além dos candidatos, a obra ganhou uma semente do canon visual
> (mesmo padrão do canon interpretativo), para que T043 consolide decisões já
> aprovadas em vez de redescobri-las.

- **Objetivo:** Visual Bible, Visual DNA, símbolos, sigil e `FIG-NARCISO` prontos para `T036–T043`.
- **Arquivos:** `planning/NARCISSUS_VISUAL_BIBLE.md`, seeds de `FACE_CANON`/`CHARACTER_VISUAL_BIBLE`
  (seção 14), `seeds/VISUAL_CANDIDATES.seed.yaml` (candidatos, nunca canon).
- **Regras:** V1 (paleta), V2/V3 (Chekhov e watchlist), ST-01..09 com `check_visual_canon.py` **existente**; `SYMR-05`, `VNP-*`.
- **Decisões humanas:** OQ-N1 já decidida (fragmento do rosto, contrato 23.2.1); pendente OQ-N6 (prata).
- **Aceite:** canon visual de fixture valida em `--mode plan` sem HIGH; `--state FIG-NARCISO` projeta 14.7.
- **Complexidade:** M (conteúdo) · S (código).

### Slice 4 — Sistema de ilustração (motor, neutro, OFF por padrão) — **concluído em 2026-09-15**

> Entregue (motor, tudo atrás de flag ou de campo opcional):
> `livingbook.py` — `features.images.illustration_slots` gera `T45NN_IL_BRIEF/GENERATE/FACE_QA/CONTINUITY_QA/APPROVE`
> por slot de `chapter_architecture.yaml` (parâmetros `illustration_id`/`chapter`, saída `images/approved/IL-NN.jpg`),
> `GATE_VISUAL.requires` = aprovações dos slots, T702 recebe a instrução de `illustrations[]`;
> `validate-book` reprova slots ausentes, fora de `IL-NN` ou duplicados.
> `check_visual_canon.py` — `check_illustrations` (`TEXT_RELATION_MISSING`, `LITERAL_ILLUSTRATION`,
> `CONTRADICTION_UNDECLARED`, `FORESHADOW_WITHOUT_PAYOFF`, `ILLUSTRATION_CATEGORY_MISSING`,
> `ILLUSTRATION_CHAPTER_MISSING`, `CALLBACK_UNRESOLVED`, `ILLUSTRATION_SLOT_MISMATCH`) e `check_figures`
> (`FIGURE_WITHOUT_IDENTITY_REF`, `FIGURE_ON_COVER_UNAPPROVED`, `FIGURE_STATE_UNRESOLVED`, `FIGURE_STATE_MISMATCH`
> contra `project_state`). Canon sem `illustration`/`FIGURE`: nenhum achado novo (fixtures Cisne/Maré limpas).
> `build_kdp_docx.py` — `illustrations[]` opcional em `layout/IMAGE_PLACEMENT.yaml` (id, chapter, placement OPEN/HINGE/AFTER,
> anchor literal, category, alt), várias pranchas por capítulo, tamanho por categoria em
> `KDP_LAYOUT_DEFAULTS.images.illustrations`; prancha ausente ou âncora não encontrada ⇒ `BUILD FAILED`.
> Sem a lista, DOCX idêntico (hash de conteúdo).
> Obra — as 24 composições `IL-01..IL-24` na semente do canon visual; `illustration_slots: true`; modo
> `illustrations` (briefs sem nome de hipótese — léxico `hypothesis_names` —, `REFLECTION_QA_SKIPPED` para prancha
> aprovada sem checagem de anomalia) em `GATE_VISUAL` e `GATE_MEDIA_ASSETS`; regras de prancha em todo modo que valida
> o canon visual (`ILLUSTRATION_CATEGORY_INVALID`, `REFLECTION_PLATE_WITHOUT_REFLECTION`, `CALLBACK_UNDECLARED`,
> `DECAY_PLATE_TOO_EARLY`, `DECAY_STATE_MISMATCH`, `SINGLE_HYPOTHESIS_EVIDENCE`, `REFLECTION_FACE_RESOLVED`,
> `ACT_GRAMMAR_VIOLATION`, `GAZE_AFTER_WITHDRAWAL`, `GAZE_OVERUSED`, `REFLECTION_DOUBLE_OVERUSED`,
> `REFLECTION_ABSENT_OVERUSED`, `PLATE_SPOILER_BEFORE_ANCHOR`, `PLATE_NUDITY_CATEGORY`, `DECAY_BODY_OVEREXPOSED`,
> `FORESHADOW_UNDERUSED`).
> Resultados: goldens dos 6 livros idênticos; `check_visual_canon.py` aceita as 24 pranchas só com `PENDING_APPROVAL`;
> testes: `test_narciso_book` 138 OK, `test_illustration_system` 26 OK, suíte existente 274 OK; `validate-engine` OK.
> Desvios: o commit prévio do working tree (OQ-N15) não foi feito — depende de autorização; a regressão foi garantida
> pelos goldens. OQ-N7 (quantidade/cor) segue aberta: o código não depende dela. Fora do escopo: `pair_with: SPREAD`
> no DOCX (Slice 5).

- **Objetivo:** mais de uma prancha por capítulo, com relação texto×imagem, `FIGURE` verificável e placement por id.
- **Arquivos:** `check_visual_canon.py` (bloco `illustration`, `FIG-01..04`, `TIR-01..05`, passthrough `ext.*`);
  `livingbook.py` (tarefas `T45NN_IL_*` a partir de `illustration_slots`; `GATE_VISUAL.requires`);
  `build_kdp_docx.py` (`IMAGE_PLACEMENT.yaml` por id, múltiplas por capítulo, arquivos `IL-NN.jpg`);
  `KDP_LAYOUT_DEFAULTS.yaml` (tamanhos por categoria, só lidos com slots);
  `validate_narciso.py --mode illustrations`; testes e goldens.
- **Aceite:** goldens dos livros existentes idênticos; DOCX de fixture sem slots idêntico em bytes;
  fixture com slots gera tarefas, valida `ILLUSTRATION_SLOT_MISMATCH`, insere pranchas por âncora.
- **Complexidade:** M–L.

### Slice 5 — Book-as-Mirror (motor pequeno + obra) — **concluído em 2026-09-15**

> Entregue (motor, opcional):
> `check_visual_canon.py` — MIR-03 (`callback_changes`: `CALLBACK_WITHOUT_CHANGE`, `CALLBACK_OVERLOADED`),
> `pair_with` (`SPREAD_PLACEMENT_INVALID`, `PAIR_WITH_UNRESOLVED`), `display_assets` TITLE_ECHO/ORNAMENT
> (`DISPLAY_ASSET_INVALID`) e `project_mirror_manifestation`: `--edition-plan-all` acrescenta ao EDITION_PLAN
> `interior_plates[]` (layout SINGLE/SPREAD, SEQUENTIAL em alvo refluível) e `chapter_display[]`
> (INCLUDED/OMITTED com motivo; Kindle sempre OMITTED). Canon sem pranchas nem recursos: plano inalterado.
> `build_kdp_docx.py` — spread: metade esquerda em seção que começa em página par, direita na ímpar seguinte
> (o Word insere a branca de paridade), com `{id}_verso`/`{id}_recto` ou a imagem inteira cortada ao meio sem perda;
> spread com placement OPEN falha o build; `chapter_display[]` INCLUDED vira imagem abaixo do título
> (arquivo ausente não entra, como o sigil). Sem essas chaves, DOCX idêntico.
> Obra — `planning/MIRROR_MANIFESTATION.yaml` (tabela 18.5 por edição, pares de retorno, spread `IL-12`@17);
> `callback_changes` nos 6 retornos; `display_assets` (eco do título em 12/15/17/19/22, um ornamento por ato);
> validador: `MIRROR_MANIFESTATION_MISSING/INVALID`, `KINDLE_OMISSION_VIOLATED`, `MIRROR_REQUIRED_TO_READ` (MIR-02),
> `SPREAD_MISPLACED`, `CALLBACK_PAIRS_MISMATCH`, `TITLE_ECHO_MISMATCH`, `ORNAMENT_ACT_MISMATCH`, MIR-03 no modo `package`.
> Decisão D-N4: **capitular omitida em todas as edições** — a erosão por ato passa ao ornamento; rever quando houver
> render-QA de PDF.
> Resultados: EDITION_PLAN do Kindle com `IL-12` SEQUENTIAL e todo recurso de exibição OMITTED; paperback com SPREAD,
> 5 ecos e 33 ornamentos. Testes: `test_book_as_mirror` + `test_illustration_system` 47 OK, `test_narciso_book` 150 OK,
> suíte existente 274 OK; `validate-engine` OK.
> Desvio: a render-QA (DOCX→PDF) não roda neste ambiente — `check_render_capability.py` não encontrou conversor;
> a paridade do spread foi provada pela estrutura das seções. Render visual continua obrigatório no `GATE_KDP`.
> `ACT_WATER_PAGES` e `COLLECTOR_MIRROR_INSERT` ficam `PENDING` (produção de miolo / Slice 7).

- **Objetivo:** spread central garantido, callbacks verificados, assets de exibição com fallback.
- **Arquivos:** `build_kdp_docx.py` (`pair_with: SPREAD` → página em branco quando necessário para verso/recto);
  `check_visual_canon.py` (`MIR-03`); assets 1-bit de capitular e duplicata espelhada (opcional);
  plano de manifestação por edição (18.5).
- **Aceite:** fixture de 3 capítulos com spread renderizado no par correto (render-QA existente); Kindle omite o que 18.5 omite.
- **Complexidade:** M.

### Slice 6 — Releitura e ambiguidade final contra prosa (obra) — **concluído em 2026-09-15**

> Entregue (só obra; motor intocado):
> modo `final` do validador — `FINAL_ROW_UNREALIZED` (toda linha REALIZED), `FINAL_EVIDENCE_COUNT` contra canon **e**
> ledger (exatamente uma evidência nova no 33, igual a `final_evidence`), `EXPLANATORY_CLOSURE` para evento que revisa
> crença no 33 e para o léxico `explanatory_closure` no último capítulo (UNC-08), `FATE_RESOLVED` para o léxico
> `fate_confirmation` do 31 ao 33 (7.5); RRL-04 `REREAD_ANCHOR_MISSING` — pistas `TEXT` com `text_anchor`
> `TEXT:<cap>:"trecho"` no capítulo da âncora planejada, achado literal no manuscrito congelado.
> RRL-05 — seção `revelations` (`REV-INSCRIPTION` 14 → `GT-NAR-04`; `REV-DEBT` 16 → `GT-NAR-05`), validada no pacote
> (`REVELATION_INVALID`, `REVELATION_TOUCHES_AMBIGUITY`, formação tardia `RETCON_DISGUISED_AS_TWIST`, revelação no
> último capítulo) e contra o ledger (`beliefs.revises`, `about` = `formed_by`, `disclosed_by_revision`, verdade
> divulgada na ancestralidade `caused_by`, nunca `reader_access: NEVER`) — a mesma ancoragem de INV-11, feita pela
> obra para bloquear no gate sem depender do relatório L5.
> ICN-IMM estendida: revelações realizadas e pistas com `text_anchor` gravado são imutáveis contra a baseline (âncoras
> novas no lado ainda aberto são permitidas). Runbook: protocolo de `text_anchor`, revelações e checklist do final.
> Resultados: fixture congelada (canon/ledger realizados, trechos literais, baseline `WAVE_06`) passa em `--mode final`
> pela CLI; mutações de epílogo, destino confirmado, segunda evidência, revisão no 33, âncora ausente/reescrita/fora do
> capítulo, retcon de suporte, de segunda leitura e de revelação, e revelação sem causa plantada reprovam.
> Testes: `test_narciso_book` 176 OK; suítes do motor 321 OK; pacote sem achados.
> Decisões registradas: `GT-NAR-05 SECRET` (quem pagou a internação) e a formação de `RB-DEBT-01` no capítulo 3
> (Eco estende o contrato) — propostas para T013/T018N confirmarem. As três versões de Lia (25) **não** são revelação:
> seguem evidência ambígua (`RFX-12`). A fixture de plano deixa de passar em `final` (correto: nada está realizado).

- **Objetivo:** `RRL-04/05`, `UNC-08`, final com exatamente uma evidência, léxicos no livro inteiro.
- **Arquivos:** `validate_narciso.py --mode final`; runbook da obra para `CANON_UPDATE` chamar snapshot interpretativo.
- **Aceite:** fixture congelada passa; mutações de retcon interpretativo e de epílogo reprovam.
- **Complexidade:** S–M.

### Slice 7 — Experiência de posse e produção (dados + obra) — **concluído em 2026-09-15**

> Entregue (motor, dados neutros): `EDITION_CAPABILITIES.yaml` 1.1.0 com `MIRROR_BOARD`, `METALLIZED_PAPER`,
> `BLIND_EMBOSS`, `SLIPCASE`, `INSERT_CARD` (UNSUPPORTED nos três alvos KDP, VENDOR_DEPENDENT no collector) e superfícies
> `SLIPCASE_FRONT/SPINE`; `MIRROR_MASK` no `PRODUCTION_MANIFEST`; `check_finish_promise` com termos novos (espelhada,
> relevo seco, slipcase, fita marcadora, guardas ilustradas) e promessas de produção (numerada, assinada, edição limitada)
> que só valem no collector com `PRINTER_PROFILE.production.<chave>: true`. Planos golden do Cisne idênticos.
> Obra: escada do espelho `MIRROR_BOARD → METALLIZED_PAPER → METALLIC_FOIL → SIMULATED_METALLIC_PRINT` com TRAP-01
> declarado (`MIRROR_GIMMICK`); superfícies do collector (lombada nua, guardas, borda, fita, slipcase) e acabamentos
> `FI-FLOWER`, `FI-EDGE`, `FI-RIBBON`, `FI-SLIPCASE`; `seeds/PRINT_SPEC.seed.yaml` (page_count sempre null,
> `PAGE_COUNT_INVENTED`; tinta segue a recomendação de OQ-N7); `seeds/PRINTER_PROFILE.template.yaml` que nunca confirma
> nada; `planning/PRINTER_PROFILE_RESEARCH.md` (roteiro humano, OQ-N8); léxico `finish_promise`.
> Modo `edition` (`V_NARCISO_EDITION` em `GATE_KDP` e `GATE_MEDIA_ASSETS`): `KDP_REQUIREMENTS_UNVERIFIED` (T699),
> `EDITION_PLAN_MISSING`, `HIDDEN_TRUTH_EXPOSED` (TRAP-02), `MIRROR_OUTSIDE_COLLECTOR`, `FINISH_NOT_PHYSICAL`,
> `PRINTER_EFFECT_UNEVIDENCED` (efeito ou produção sem evidência/decisão), `FINISH_PROMISE_MISMATCH` nos textos de
> loja e redes (TRAP-05, 21.4), `REREAD_CLUE_EXPOSED` (SOC-05).
> Resultados: o resolver gera os 4 `EDITION_PLAN` de NARCISO sem nenhum acabamento PHYSICAL; capa nua, guardas finais,
> lombada nua e slipcase OMITTED fora do collector; sem gráfica, o espelho vira impressão metálica simulada e os
> acabamentos só-gráfica são omitidos; com gráfica confirmando `MIRROR_BOARD`, só o collector ganha o espelho físico e
> a máscara `MIRROR_MASK`. Testes: `test_narciso_book` 200 OK, `test_edition_capabilities_v11` 10 OK, suítes do motor OK.
> Não feito (humano): escolher gráfica, provas físicas, OQ-N7, OQ-N8; `INSERT_CARD` sem composição até existirem os
> artefatos narrativos aprovados; T699 real ainda não executado.

- **Objetivo:** matriz com efeitos de espelho/slipcase/cards; collector especificável; KDP honesto.
- **Arquivos:** `EDITION_CAPABILITIES.yaml` (29.6), léxico de `FINISH_PROMISE_MISMATCH` ("espelhada", "numerada", "assinada"),
  `layout/PRINT_SPEC.yaml` e pesquisa de `PRINTER_PROFILE` (humano), `TRAP-01..05`.
- **Pré-condição:** `T699` revalida KDP (inclui diretrizes de conteúdo de capa).
- **Aceite:** resolver produz `EDITION_PLAN` dos 4 alvos para NARCISO sem prometer efeito não físico; `HIDDEN_TRUTH_EXPOSED` testado.
- **Complexidade:** S–M (código) · depende de fornecedor (collector).

### Slice 8 — Bootstrap da obra (execução real, pago)

- **Objetivo:** iniciar NARCISO de verdade.
- **Etapas:** compose `PREMIUM` → `GATE_CANON` (humano) → `GATE_LIVING_BOOK` → briefs → `GATE_VOICE` (humano);
  3 pranchas-piloto (`IL-01`, `IL-05`, `IL-12`) em tier `draft` e depois `chapter_final` somente após Slice 4.
- **Aceite:** gates sem HIGH/BLOCKER; humano responde H2 e H8 "sim" sobre a voz e as pranchas-piloto.
- **Dependências:** Slices 1–3 para texto; 4–5 antes de `GATE_FULL_MANUSCRIPT`; 6 antes de `GATE_FULL_MANUSCRIPT`; 7 antes de `GATE_KDP`.

### Ordem recomendada

```text
Slice 1 ─▶ Slice 2 ─▶ Slice 3 ─▶ Slice 8a (texto até GATE_VOICE)
                         │
       [commit do working tree] ─▶ Slice 4 ─▶ Slice 5 ─┐
                                   Slice 6 ────────────┼─▶ Slice 8b (waves → GATE_FULL_MANUSCRIPT → imagens)
                                   Slice 7 ────────────┴─▶ GATE_KDP / collector
```

---

## 36. Open Questions

| ID | Pergunta | Bloqueia | Recomendação |
|---|---|---|---|
| ~~OQ-N1~~ | Narciso aparece literalmente na capa? | — | **DECIDIDO** (36.1) |
| ~~OQ-N2~~ | Hipótese de gêmeo? | — | **DECIDIDO** (36.1) |
| ~~OQ-N3~~ | 33 capítulos palíndromos com Coro? | — | **DECIDIDO** (36.1) |
| ~~OQ-N4~~ | Capítulo 18 em página ou corte? | — | **DECIDIDO** (36.1) |
| ~~OQ-N5~~ | Consentimento da compulsão | — | **DECIDIDO** (36.1) |
| ~~OQ-N6~~ | Prata como material de acabamento | — | **DECIDIDO** (36.1) |
| OQ-N7 | Quantidade de pranchas (24) e cor do miolo (P&B × premium color) | Slice 4, custo | 24 grayscale-safe; cor só na capa dura e collector |
| OQ-N8 | Gráfica collector, numeração, assinatura, slipcase | Slice 7 | Pesquisa humana; manifesto em `PRINTER_UNCONFIRMED` até lá |
| OQ-N9 | Última evidência: foto do Coro (F-C), flor (F-A) ou reflexo a menos (F-B)? | Slice 1 | F-C no 33, com F-A no 32; F-B descartada por ser a mais conclusiva |
| OQ-N10 | Promover "ambiguidade interpretativa estruturada" a feature do motor | futuro | Não agora; reavaliar depois de NARCISO provar (quatro obras já tiveram ambiguidade bloqueante) |
| OQ-N11 | Colisão de título "Narciso" | lançamento | Decisão legal/comercial humana |
| OQ-N12 | Nomes próprios (Céfiso, Amintas, Teodoro, Íris) | Slice 1 | Aprovar ou trocar antes de `GATE_CANON` |
| OQ-N13 | Redação da nota de conteúdo e eventual página de recursos | Slice 8 | Front matter; humano |
| OQ-N14 | Perfil `PREMIUM` desde o início ou `STANDARD` até o piloto visual | Slice 8 | `STANDARD` até `GATE_VOICE`; `PREMIUM` antes das waves |
| OQ-N15 | Commit das capabilities não versionadas antes dos slices de motor | Slice 4 | Obrigatório |

---

### 36.1 Registro de decisões humanas (2026-09-15)

| ID | Decisão | Efeito nesta SDD |
|---|---|---|
| OQ-N1 | Narciso **na capa por fragmento — parte do rosto**; a capa deve estancar o olhar com beleza pura, bruta e apaixonante, preservando parte do mistério | `role_overrides` com `APR-COVER-01`; `CV-A` canônica em `OUTER_TRUTH`; contrato `COV-01..09` + rubrica `COV-H` (23.2.1) |
| OQ-N2 | **Sem hipótese de gêmeo** | `H-TWIN` removida; 5 hipóteses (`PROJ`, `SUPER`, `SELF`, `OTHER`, `GAZE`); matriz rebalanceada (9.3); variante de Pausânias excluída (6.1, 32); `IR-N11` reescrita; `UNC-10 TWIN_HYPOTHESIS_INTRODUCED` (BLOCKER); `PRO-NAR-006` |
| OQ-N3 | **Sim** aos 33 capítulos palíndromos com Coro em 1/11/23/33 | arquitetura 7.3–7.4 confirmada; `MIR-04` bloqueante |
| OQ-N4 | Capítulo 18 **com teto de explicitude** | cena em página, teto `SENSUAL`; `NIGHT_WITHOUT_WORDS` atualizada; `DDC-09` (BLOCKER) |
| OQ-N5 | **Sim**: compulsão modelada como capacidade de recusa reduzida com o vocabulário do ledger | tabela 11.4 vira canon de modelagem; nenhum enum novo |
| OQ-N6 | **Prata só como acabamento** | `SILVER_MIRROR` em `finish_intents`, ligado a `SYM-ESPELHO`, `COLLECTOR_ONLY`; nenhum papel de cor muda no Author DNA v1; `SILVER_AS_PALETTE_ROLE` e `SILVER_FINISH_MISPLACED` bloqueiam |

Registro de aprovação humana correspondente, quando o runtime existir:
`project_state/APPROVALS/VISUAL/APR-COVER-01.md` (capa) e
`project_state/APPROVALS/GATE_CANON.md` (arquitetura) — escritos por pessoa,
nunca pelo motor.

---

## 37. Final Recommendation

```text
READY_FOR_SLICE_1 = YES
READY_FOR_ENGINE_SLICES (4, 5, 7) = NO, até commit do working tree (D-N14) e decisão OQ-N7
```

Justificativa:

1. **A arquitetura necessária já existe em ~85%.** O ledger causal cobre
   personagem, consentimento, idade e releitura; o sistema visual Bea Halden
   cobre identidade, símbolo, estado, spoiler, edição e acabamento; o padrão
   de pacote cobre guardiões, validadores e tarefas da obra. NARCISO não
   precisa de engine novo, gate novo nem agente genérico novo.
2. **O que falta é pequeno, nomeado e localizado:** um canon interpretativo
   da obra (ambiguidade + desejo + releitura), um validador da obra, dois
   guardiões da obra, e três extensões neutras do motor (pranchas por slot,
   regras de `FIGURE`/`illustration`, efeitos de edição).
3. **A decisão mais importante é negativa:** `NO_HIDDEN_ANSWER`. Nenhum
   arquivo sabe o que é o Reflexo, e a verdade do motor sobre o amor de
   Narciso é a própria contradição. É o que impede o livro de convergir.
4. **Slice 1 é independente do motor e do working tree sujo:** só cria
   `books/narciso/` e testes da obra, valida com comandos existentes e é
   reversível removendo arquivos.
5. **O objeto físico foi tratado com honestidade de fabricação:** toda
   promessa de espelho, foil, relevo, borda ou sobrecapa passa pela matriz
   datada e por `T699`; o KDP recebe a armadilha narrativa, o collector
   recebe a física.

Síntese:

> **Narciso se apaixonou pelo próprio reflexo. O leitor deve correr o risco de
> cometer o mesmo erro. O motor deve garantir que o risco é real — e que ninguém,
> nem o próprio motor, sabe o que havia na água.**

---

## Apêndice A — Arquivos inspecionados e comandos executados

**Documentação:** `README.md`, `docs/ARCHITECTURE.md`, `docs/BOOK_PACKAGE_MODEL.md`,
`docs/COMO_EXECUTAR_UM_LIVRO.md`, `docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md`
(integral), `docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md` (integral),
`docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_CALIBRATION.md`,
`discovery-books/09-discovery-profile-livro-no-motor-intent.md`.

**Motor:** `engine/AGENTS.md`, `engine/ENGINE_GRAPH.yaml`, `engine/IMPLEMENT.md`
(trechos de capabilities), `engine/MODEL_TIERS.yaml` (eixo de imagem),
`engine/contracts/BOOK_SPEC.schema.json`, `CANON_PROPOSAL.schema.json`,
`IMAGE_APPROVAL.schema.json`, `REVIEW_FINDING.schema.json`;
`engine/templates/EXECUTION_PROFILES.yaml`, `FACE_CANON_TEMPLATE.md`,
`VISUAL_NARRATIVE_CANON_TEMPLATE.yaml`, `EDITION_CAPABILITIES.yaml`,
`AUTHOR_VISUAL_DNA_TEMPLATE.yaml`, `PRINT_GEOMETRY.yaml`,
`VISUAL_NARRATIVE_RUNBOOK.md`, `CAUSAL_LEDGER_RUNBOOK.md`,
`TEXT_QUALITY_DEFAULTS.yaml`, `KDP_LAYOUT_DEFAULTS.yaml` (imagens, abertura,
manuscrito); `engine/scripts/livingbook.py` (ids de tarefas e gates, bloco de
imagens `:486-494`, T602 `:502-509`, extensões `:578-592`, `task()` `:160`),
`run_deterministic.py` (integral), `check_visual_canon.py` (vocabulário
`:55-122`, índice de funções), `check_causal_ledger.py` (constantes e índice de
funções), `detect_repetition.py` (cabeçalho), `generate_image.py` (argumentos),
`build_kdp_docx.py` (placements, mirror margins).

**Agentes:** `genre_guardian`, `visual_director`, `image_continuity_qa`,
`chapter_image_director`, `originality_auditor`, `facial_identity_expert`,
`anti_manipulation_guardian`, `symbolism_architect`.

**Autora:** `authors/bea_halden/AUTHOR_VISUAL_DNA.v1.yaml`.

**Pacotes:** `books/a_morte_ainda_nao_nasceu/` (BOOK_SPEC, BOOK_GRAPH,
immutable_rules, protected_scenes, quality_profile,
`agents/consent_and_care_guardian.toml`, `validators/validate_book_dna.py`);
`books/a-noiva-esquecida/` (BOOK_SPEC, BOOK_CONSTITUTION, immutable_rules,
protected_scenes, quality_profile, visual_profile, chapter_architecture
(início), `planning/01,02,08,10,12`); `books/eva-a-ultima-mulher-da-terra/`
(`immutable_rules.yaml`, `agents/mystery_ambiguity_guardian.toml`,
`seeds/WORLD_RULES_SEED.md §8`); listagem de todos os pacotes.

**Runtimes (somente leitura):** `runtime/a-noiva-esquecida/` (listagem de
`canon/`, `specs/`, `author/`; `CAUSAL_LEDGER.yaml` início; `PROJECT_STATUS.yaml`
início); `runtime/a_morte_ainda_nao_nasceu/` (`images/` listagem,
`chapters/chapter_01/GENERATION_REPORT.md`, `canon/CANON_REGISTRY.yaml`
`unknowns`/`prohibited_inferences`); `output/eva-capitulos-v1/PROMPTS_FINAIS.md`
(início); listagem de `output/` e `tmp/`.

**Testes/fixtures:** listagem de `tests/` e `tests/fixtures/`.

**Comandos executados (sem efeito no repositório):**

```text
git ls-files · git status --short · git log --oneline
.venv\Scripts\python.exe engine/scripts/livingbook.py validate-engine
  → ENGINE VALID | generic agents: 66 | version: 1.1.0
.venv\Scripts\python.exe engine/scripts/livingbook.py validate-book --book books/a-noiva-esquecida
  → BOOK PACKAGE VALID | A Noiva Esquecida | chapters: 40 | book agents: 0
.venv\Scripts\python.exe -m unittest tests.test_causal_ledger tests.test_visual_canon tests.test_compose_regression tests.test_visual_narrative_rendering
  → Ran 274 tests … OK
```

`compose` **não** foi executado. `tests/test_image_generation.py` **não** foi
executado (chamada paga, D10). Nenhuma fonte externa foi consultada nesta
sessão; fatos KDP vêm dos templates datados do repositório.

## Apêndice B — Glossário de ids

| Prefixo | Significado | Arquivo |
|---|---|---|
| `MYTH-*` | elemento do DNA mítico | pacote / 6.2 |
| `IR-N*` | regra imutável da obra | `immutable_rules.yaml` |
| `CHR-*`, `GT-*`, `SM-*`, `SP-*`, `EV-*`, `LP-*`, `RB-*` | ledger causal | `CAUSAL_LEDGER.yaml` |
| `UNK-NAR-*`, `PRO-NAR-*`, `ENV-*` | incógnitas, inferências proibidas, ambientes | `CANON_REGISTRY.yaml` |
| `H-*` | hipótese ontológica do Reflexo | canon interpretativo |
| `RFX-*` | evidência do Reflexo | canon interpretativo |
| `LOVE-E*` | evento da matriz de amor | canon interpretativo |
| `DSR-*` | ocorrência de desejo compulsivo | canon interpretativo |
| `RR-*` | pista de releitura | canon interpretativo |
| `SYM-*`, `SIG-*`, `FIG-*`, `ART-*` | elementos visuais | `VISUAL_NARRATIVE_CANON.yaml` |
| `IL-*` | prancha / ilustração (composição) | `VISUAL_NARRATIVE_CANON.yaml` |
| `CV-*` | variante de capa (candidato) | `VISUAL_CANDIDATES.yaml` |
| `FI-*` | intenção de acabamento | `VISUAL_NARRATIVE_CANON.yaml` |
| `FV-NARCISO-01` | código de identidade facial | `FACE_CANON.md` |
| `VETO-N*` | veto visual | `VISUAL_NARRATIVE_CANON.yaml` |
| `APR-*` | aprovação humana com hash | `project_state/APPROVALS/VISUAL/` |
| `UNC/LOV/DDC/RRL/SYMR/VNP/TIR/MIR/REF/SOC/TRAP/FIG/MAC/ICN-*` | regras de validação | `validate_narciso.py` / `check_visual_canon.py` |
| `D-N*` | divergência descoberta | seção 2.4 |
| `OQ-N*` | pergunta aberta | seção 36 |
| `DL-N*` | decisão arquitetural | seções 28.3 e 37 |
