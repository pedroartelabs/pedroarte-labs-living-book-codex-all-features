# SDD v0.1 — `DARK_ROMANCE_CANON_ARCHITECT`

> **Status:** PROPOSTA — aguardando revisão e aprovação humana. Nenhum código
> de produção foi escrito. Nenhum agente foi criado. Nenhum comportamento do
> motor foi alterado.
>
> **Escopo:** extensão do PEDRO_ARTE_LIVING_BOOK_ENGINE (Motor de Livros Vivos),
> `engine/ENGINE_GRAPH.yaml` versão `1.1.0`, branch `main`, commit `b1bd12b`.
>
> **Regras aplicadas:** `REUSE > EXTEND > CREATE` e `SIMPLICIDADE SEMPRE`.
>
> **Convenção de linguagem:** texto em PT-BR; identificadores, estados e
> invariantes em inglês, como no restante do motor.

---

## Índice

- A. Executive Summary
- B. Repository Discovery (inclui divergências documentação × código)
- C. Reuse Analysis
- D. Constitutional Layer
- E. Domain Model
- F. State Ownership
- G. Causal Flow
- H. Invariants
- I. Gates
- J. Failure Modes
- K. MVP Scope
- L. Slice Plan
- M. Testing Strategy
- N. Observability / Explainability
- O. Migration / Compatibility
- P. Risks / Open Questions
- Q. Final Recommendation
- R. Revisão adversarial (Final Gate do SDD)
- S. Authorial / Portfolio Governance — `BEA_HALDEN_AUTHORIAL_GOVERNANCE`
- Apêndice 1 — Arquivos inspecionados
- Apêndice 2 — Cenário-fixture do MVP

---

## A. Executive Summary

### O que é

`DARK_ROMANCE_CANON_ARCHITECT` é uma **capability especializada** do Motor de
Livros Vivos que dá a um livro de Dark Romance **memória causal verificável**:
personagens com camadas independentes (verdade, autoimagem, persona), eventos
estruturais que deixam estado relacional, desejo com ancestralidade rastreável,
um modelo do que o leitor sabe e acredita, e um teste de segunda leitura que
distingue *twist* legítimo de *retcon*.

Depois da inspeção do repositório, a menor arquitetura capaz de preservar o
grafo causal central é:

```text
1 artefato de canon estruturado      canon/CAUSAL_LEDGER.yaml
                                      (dono: CANON_GUARDIAN, lock CANON_WRITE,
                                       mutação só via CANON_PROPOSAL)
1 validador determinístico           engine/scripts/check_causal_ledger.py
                                      (stdlib + PyYAML, sem LLM, sem dependência nova)
1 template documental                engine/templates/CAUSAL_LEDGER_TEMPLATE.yaml
1 feature flag OFF por padrão        BOOK_SPEC.spec.features.causal_ledger
extensões de tarefas já existentes   T013, T016, T018, T1xx, T2xx, T32xx
                                      (inputs/outputs/parameters — sem agente novo)
0 agentes novos, 0 engines, 0 serviços, 0 gates novos
```

O grafo causal vive **dentro de um único arquivo de eventos**. Estado de
relacionamento, conhecimento do leitor, crença do leitor, tensão de intimidade
e dívida narrativa **não são armazenados separadamente**: são *projeções*
determinísticas calculadas a partir dos eventos. Isso elimina, por
construção, a possibilidade de duas fontes de verdade.

### O que NÃO é

- **Não** é um novo motor de livros, nem um fork do pipeline.
- **Não** é uma coleção de tropes. Mafia, Stalker, Gothic, Bully, Captive etc.
  são configurações criativas do pacote de livro, nunca causa aceita pelo
  validador.
- **Não** cria Sex Engine, Heat Engine, Attraction Engine, Callback Engine,
  Reader Arousal Engine, Expert Router, agentes, juízes, votação ou personas
  de autor. Nenhum `ARCHITECTURAL_EXCEPTION_CANDIDATE` foi necessário (ver R).
- **Não** tenta prever fisiologia do leitor nem pontuar excitação.
- **Não** muda nada para livros que não ligam a feature.
- **Não** gera prosa explícita nem contorna políticas de conteúdo do modelo
  hospedeiro. O ledger trabalha com fatos e estados, não com texto de cena.

### Descoberta que mais moldou o desenho

O motor **não possui modelo de domínio em código**. Toda a memória narrativa é
um *blackboard* de arquivos escritos por agentes LLM (bíblias em Markdown,
`CANON_REGISTRY.yaml` sem schema), protegido por propriedade exclusiva textual
e por **validadores determinísticos plugados em gates**. A capability deve
seguir exatamente esse padrão — e o padrão já tem dois precedentes reais que a
antecipam parcialmente (ver B.4): consentimento estruturado em
`a_morte_ainda_nao_nasceu` e pistas de releitura em `eva-a-ultima-mulher-da-terra`.

---

## B. Repository Discovery

### B.1 Arquitetura real encontrada

```text
engine/                      motor reutilizável (sem canon, nomes ou vetos de gênero)
  ENGINE_GRAPH.yaml          políticas, estados, locks, 66 agentes, protocolos,
                             known_capabilities (de HOST), quality_defaults,
                             artifact_contracts
  scripts/livingbook.py      compositor: validate-engine | validate-book |
                             compose | smoke-test | ready | new-book
                             build_standard_graph() gera o DAG a partir do BOOK_SPEC
  scripts/runtime_taskgraph.py  máquina de estados do runtime (init/refresh/ready/
                             mark/validate-gate), gates com custom_validators e
                             requires_human_approval
  scripts/run_deterministic.py  executa tarefas READY que declaram `tool`
  scripts/check_*.py, detect_repetition.py, build_canon_digest.py
                             pré-filtros e validadores determinísticos
  contracts/*.schema.json    6 schemas documentais (não executados por código)
  templates/                 EXECUTION_PROFILES, TEXT_QUALITY_DEFAULTS,
                             FACE_CANON_TEMPLATE, KDP_LAYOUT_DEFAULTS
  agents/*.toml              66 personas genéricas com model_tier
books/<slug>/                DNA literário de uma obra
  BOOK_SPEC.yaml             features, waves, agent_packs, execution_profile
  BOOK_GRAPH.yaml            extensões: custom_validators, gate_extensions,
                             additional_tasks
  chapter_architecture.yaml  roteiro por capítulo (campos extensíveis por livro)
  immutable_rules.yaml, protected_scenes.yaml, quality_profile.yaml
  agents/*.toml              guardiões específicos da obra
  validators/*.py            validadores determinísticos da obra
runtime/<slug>/              gerado por compose (gitignored)
  TASK_GRAPH.yaml, project_state/PROJECT_STATUS.yaml
  specs/ canon/ living_book/ briefs/ manuscript/ reviews/ ...
```

**Ciclo relevante para esta capability** (gerado por `build_standard_graph`):

```text
GATE_BOOTSTRAP
 → CANON: T010 brief → T011 STORY_BIBLE → T013 CHARACTER_BIBLE (CHARACTER_PSYCHOLOGIST)
          → T016 PLOT_DEPENDENCY_MAP (PLOT_ENGINEER) → T017 TIMELINE
          → T018 CANON_REGISTRY (CANON_GUARDIAN, lock CANON_WRITE)
          → T019 CANON_REVIEW (spawn guardiões)            ⇒ GATE_CANON
 → T020 CANON_DIGEST (tool determinística)
 → LIVING_BOOK: T032 READER_VITALS, T033 EMOTIONAL_RESPIRATION, T035 MEMORY_MOTIF_MAP ...
                                                           ⇒ GATE_LIVING_BOOK
 → T1xx BRIEF_CHAPTER (SCENE_ARCHITECT)                    ⇒ GATE_CHAPTER_BRIEFS
 → VOICE_CALIBRATION                                       ⇒ GATE_VOICE
 → por wave: PREFLIGHT → WRITE (CHAPTER_WRITER/LEAD_NOVELIST, propõem CANON_PROPOSALS)
             → MERGE → REVIEW → REVISION → CANON_UPDATE (CANON_GUARDIAN) → APPROVAL
                                                           ⇒ GATE_WAVE_n
 → INTEGRATION: T300 assemble, T301, T302 critic panel, T32xx PROTECTED_* audits,
                T303..T310 freeze                          ⇒ GATE_FULL_MANUSCRIPT
 → VISUAL / SOUND / LEGAL (T602 ORIGINALITY) / KDP / DELIVERY
```

**Mecanismos de extensão já existentes (os únicos que esta SDD usa):**

| Mecanismo | Onde | Uso hoje |
|---|---|---|
| Feature flag condicional em `build_standard_graph` | `livingbook.py` (`images`, `living_sound`, `translation_preparation`, `kdp_docx`) | liga/desliga fases inteiras |
| `custom_validators` + `gate_extensions` | `BOOK_GRAPH.yaml`, `runtime_taskgraph.py validate-gate` | `VAL_BOOK_DNA`, `VAL_ENDING_INTEGRITY` |
| `tool` determinística por tarefa | `TOOL_BY_TASK` / `TOOL_BY_PATTERN` (vazio) + `run_deterministic.py` | digest, DOCX, capa |
| `CANON_PROPOSAL_PROTOCOL` | `ENGINE_GRAPH.protocols` | writers propõem, CANON_GUARDIAN promove |
| `PROTECTED_SCENE_PROTOCOL` | `protected_scenes.yaml` + tarefas `T32xx` | auditoria independente por cena |
| Instruções escopadas | `copy_runtime()` escreve `manuscript/AGENTS.md`, `images/AGENTS.md` ... | regras locais por diretório |
| Override de defaults por livro | `templates/TEXT_QUALITY_DEFAULTS.yaml` ← `book/text_quality.yaml` | clichês por obra |
| Campos extras em `chapter_architecture.yaml` | livros reais (`irreversible_turn`, `living_book_vitals`, `pov`) | validados por `validate_book_dna.py` |
| Guardião específico da obra | `books/<slug>/agents/*.toml` | `CONSENT_AND_CARE_GUARDIAN`, `LIMINALITY_GUARDIAN` |

### B.2 Componentes relevantes por conceito pedido

| Área pedida | Componente real | Natureza |
|---|---|---|
| Contratos | `engine/contracts/*.schema.json` | documental; não executado |
| Estados | `ENGINE_GRAPH.task_states`, `PROJECT_STATUS.yaml` | estado de **tarefa**, não narrativo |
| Engine/orchestrator | `build_standard_graph` (compositor) + sessão LLM | não há orquestrador em processo |
| Planners | `NARRATIVE_ARCHITECT`, `PLOT_ENGINEER`, `SCENE_ARCHITECT`, `READER_VITALS_AGENT` | agentes que escrevem Markdown |
| Canon | `CANON_REGISTRY.yaml`, `CANON_PROPOSALS/`, `CANON_GUARDIAN` | arquivo sem schema; dono exclusivo |
| Memory | "o repositório é a memória" (`AGENTS.md`); `mutation_log` no registry | arquivos |
| Character | `CHARACTER_BIBLE.md` (T013), `CHARACTER_CONTINUITY_REVIEWER` | Markdown |
| Worldbuilding | `WORLD_RULES.md`, `WORLD_BIBLE.md`, `WORLD_RULES_REVIEWER` | Markdown |
| Generation | `LEAD_NOVELIST`, `CHAPTER_WRITER` em waves | LLM |
| Gates / QA | 15–17 gates; validadores determinísticos; painéis de revisão rotacionados por perfil | híbrido |
| Human checkpoints | `requires_human_approval` + `project_state/APPROVALS/<GATE>.md` | por perfil |

### B.3 Padrões de SDD existentes

Não existe SDD formal no repositório (busca por `SDD` sem resultado). O padrão
documental mais próximo é a série `discovery-books/NN-*.md`: análise em PT-BR,
evidência citada por arquivo, recomendação explícita, "o que eu não fiz",
execução em **ondas/slices** aprovadas uma a uma. Esta SDD segue esse padrão e
inaugura `docs/sdd/`.

### B.4 Precedentes que já antecipam a capability

| Precedente | Evidência | O que prova |
|---|---|---|
| Consentimento como fato canônico atômico | `runtime/a_morte_ainda_nao_nasceu/canon/CANON_REGISTRY.yaml` → seção `care_and_consent` (`ETH-JOA-001`, `ETH-OLI-001`, `ETH-CARE-001`) | o CANON_GUARDIAN real já produz estado de consentimento estruturado |
| Guardião de consentimento por livro | `books/a_morte_ainda_nao_nasceu/agents/consent_and_care_guardian.toml` ("Track who knows what, who consents, whether consent can be withdrawn") | assimetria de informação + consentimento como auditoria bloqueante |
| Lei 02 como checagem declarada | `books/a_morte_ainda_nao_nasceu/quality_profile.yaml` → `required_checks: every scene changes relationship, information or physical condition` | a regra existe, mas só como texto para LLM |
| Virada irreversível por capítulo | `chapter_architecture.yaml` → `irreversible_turn`, exigido por `validate_book_dna.py` | precedente de validação determinística de mutação |
| Second-Read Test na prática | `books/eva-.../seeds/WORLD_RULES_SEED.md §8`, `IR019`, `runtime/eva-.../living_book/MEMORY_MOTIF_MAP.md` (P1–P7: "primeira leitura / segunda leitura") | releitura sem retcon já é objetivo editorial real |
| Tipos de elo causal | `runtime/eva-.../specs/PLOT_DEPENDENCY_MAP.md` → elos `F` fato, `R` relação, `P` pista de releitura | o PLOT_ENGINEER já pensa em ancestralidade tipada |
| Assimetria leitor × personagem | `runtime/eva-.../living_book/READER_VITALS.md` → campo "Gap informacional" por capítulo | Reader Model existe, mas só em prosa |
| Incógnitas e inferências proibidas | `CANON_REGISTRY` de `a_morte` → `unknowns`, `prohibited_inferences` | "o motor sabe, o leitor não" já é canon |

**Conclusão:** as ideias não são inéditas no motor; o que falta é
**estrutura verificável**. Os precedentes vivem em prosa ou em schemas
divergentes por livro, então nenhum script consegue perguntar "este payoff tem
história?" ou "esta revelação alterou fatos passados?". É exatamente essa
lacuna — e só ela — que a capability preenche.

### B.5 Divergências documentação × código (registradas, não corrigidas)

| ID | Divergência | Evidência | Impacto nesta SDD |
|---|---|---|---|
| D1 | README, Makefile e `CODEX_ENGINE_BOOTSTRAP_PROMPT.md` apontam `books/antes-que-as-criancas-crescam`, que não existe em `books/` | `README.md`, `Makefile` | nenhum; não usar como referência |
| D2 | `engine/contracts/*.schema.json` não são carregados por nenhum script | grep por `schema.json`; `discovery-books/01 §5` | **não** criar schema JSON não executado; o validador é o contrato |
| D3 | Schemas limitam `chapter` a `maximum: 30`; livros reais têm 34 (`adao`) e 42 (`eva`) | `CANON_PROPOSAL`, `REVIEW_FINDING`, `CHAPTER_SCORECARD`, `IMAGE_APPROVAL` | o ledger não herda esse limite |
| D4 | `CANON_REGISTRY.yaml` não tem schema e varia por runtime: atômico `{id,status,fact,source}` (`a_morte`), `locked_facts` com referências (`adao`), dicts ricos (`eva`), só `MEASURED_FACTS.yaml` (`motor-de-livros-vivos`) | `runtime/*/canon/` | justifica arquivo **separado** com contrato estrito (ver E.1) |
| D5 | Alteração **não commitada** em `build_canon_digest.py` afirma que o schema atômico "nunca chegou a ser produzido por um CANON_GUARDIAN real"; o registry de `a_morte` usa exatamente esse schema | `git diff engine/scripts/build_canon_digest.py` × `runtime/a_morte.../CANON_REGISTRY.yaml` | nenhum; working tree não é tocado |
| D6 | `GENRE_GUARDIAN` lê "genre_guardians configuration", que nenhum `BOOK_SPEC` declara | `engine/agents/genre_guardian.toml` | anti-cliché de gênero não pode depender dessa config inexistente |
| D7 | "capability" no motor significa **capacidade de host** (`known_capabilities`, `capability_requirements.yaml`: imagem, DOCX), não feature narrativa | `ENGINE_GRAPH.yaml` | a capability entra como **feature**, não como `known_capability` |
| D8 | `engine/AGENTS.md` proíbe vetos específicos de gênero em `/engine` | `engine/AGENTS.md` | a parte em `/engine` precisa ser **neutra de gênero**; DNA de Dark Romance fica no pacote do livro (ver P, Q1) |
| D9 | `build_standard_graph` indexa `sp['features']['images']` diretamente (KeyError se ausente) | `livingbook.py:285,292,299,303` | a nova flag deve ser lida com `.get()` |
| D10 | A suíte `tests/` inclui teste de integração que faz **chamada paga real** quando `.env` tem chave, e um teste que falha sem `.env` | `tests/test_image_generation.py` | testes novos rodam isolados por módulo; ver M |
| D11 | Locks (`CANON_WRITE` etc.) são metadados textuais, não travas técnicas | `discovery-books/01 §6` | propriedade do ledger é convenção + validação de baseline |
| D12 | Working tree tem mudanças não commitadas em `build_canon_digest.py` e `build_kdp_docx.py`, e livros não rastreados (`adao`, `eva`, `loja`) | `git status` | fora de escopo; não alterados |

---

## C. Reuse Analysis

Legenda: ✅ decisão · — não se aplica. "Ledger" = `canon/CAUSAL_LEDGER.yaml`.
"Validador" = `check_causal_ledger.py`. Uma única marca por linha.

### C.1 Infraestrutura

| CONCEPT | EXISTING COMPONENT | REUSE | EXTEND | CREATE | DO NOT CREATE | JUSTIFICATION |
|---|---|---|---|---|---|---|
| Composição do DAG | `build_standard_graph` | | ✅ | | | Um bloco condicional `if features.causal_ledger.enabled`, igual a `images`/`living_sound`. |
| Estado de tarefas / gates | `runtime_taskgraph.py` | ✅ | | | | Validadores entram como `custom_validators`; nenhuma mudança na máquina de estados. |
| Tarefas determinísticas | `TOOL_BY_PATTERN` + `run_deterministic.py` | | ✅ | | | Snapshot do ledger por wave é mecânico; `TOOL_BY_PATTERN` já existe vazio para isto. |
| Memória narrativa estruturada | `CANON_REGISTRY.yaml` | | | ✅ | | Arquivo irmão com contrato estrito. Registry não tem schema e diverge por runtime (D4); embutir um subárvore estrita num documento livre convida deriva. Mesmo dono, mesmo lock, mesmo protocolo. |
| Contrato do ledger | `engine/contracts/` | | | ✅ (template YAML) | JSON Schema | D2: schema não executado seria segunda fonte de verdade. O validador é o contrato; o template é a documentação e é testado contra o validador. |
| Proposta de mutação | `CANON_PROPOSAL_PROTOCOL` | | ✅ | | | Writers propõem deltas de ledger junto com fatos de continuidade. |
| Formato de achado | shape de `check_canon_continuity.finding()` / `REVIEW_FINDING` | ✅ | | | | `category, severity, chapter, evidence, detail, recommended_action`. |
| Instruções a agentes | `copy_runtime()` → `<dir>/AGENTS.md` | | ✅ | | | `canon/AGENTS.md` escrito só quando a feature está ligada. Nenhum `.toml` genérico muda. |
| Auditoria de cena de revelação | `PROTECTED_SCENE_PROTOCOL` / `T32xx` | ✅ | | | | Revelações declaradas como cenas protegidas com critérios de Second-Read. |
| Perfis de execução | `EXECUTION_PROFILES.yaml` | ✅ | | | | Regras hard do validador nunca são rebaixadas por perfil (ver H). |
| Checkpoint humano | `requires_human_approval` | ✅ | | | | Veredito final do Second-Read cabe no `GATE_FULL_MANUSCRIPT` humano já existente em STANDARD/PREMIUM. |
| Novo gate ID | lista de gates | | | | ✅ | Validadores se anexam a `GATE_CANON`, `GATE_WAVE_n`, `GATE_FULL_MANUSCRIPT`. |
| Novos agentes | `engine/agents/` | | | | ✅ | Todos os autores/revisores necessários já existem (C.3). |

### C.2 Sistemas derivados (seção 6 da missão)

| CONCEPT | EXISTING COMPONENT | REUSE | EXTEND | CREATE | DO NOT CREATE | JUSTIFICATION |
|---|---|---|---|---|---|---|
| Character Ground Truth | `CHARACTER_BIBLE.md` (T013), fatos `CHR-*` do registry | | ✅ | | | Ledger `characters[].ground_truth[]` com ids citáveis; prosa elaborada continua na bíblia. |
| Character Self-Model | idem ("núcleo quer × teme" no perfil real de Eva) | | ✅ | | | `self_model[]` com `diverges_from` explícito. |
| Social Persona | idem ("o que a pessoa nunca diz") | | ✅ | | | `social_persona[]` com `conceals`. |
| Reader Model (do personagem) | `READER_VITALS.md` (gap informacional) | | ✅ | | | **Não armazenado no personagem.** É a projeção das crenças do leitor cujo `about` é o personagem. Evita 4ª cópia do personagem. |
| Character Archetype DNA | — | | | | ✅ | Arquétipo não é causa (Lei 01). Pode existir como rótulo descritivo na bíblia; o validador recusa como `caused_by`. |
| Relationship State Matrix | elo `R` do `PLOT_DEPENDENCY_MAP` | | ✅ | | | `relationships[].baseline` + `events[].relationship_delta`. Estado atual = projeção. Nunca armazenado. |
| Attraction / Seduction DNA | — | | ✅ | | | Dimensões direcionais `attraction`/`desire` dentro do delta relacional, com `because`. Nenhum atributo de personagem. |
| Sexual Tension & Payoff DNA | seeds/payoffs do `PLOT_ENGINEER` | | ✅ | | | `loops[]` com `kind` INTIMACY/EROTIC/VULNERABILITY/VERBAL/POWER/RELATIONAL + regras L3. |
| Intimacy Tension State | — | | ✅ | | | Projeção: loops íntimos abertos + dimensões `desire`/`restraint` atuais do par. Não é estado próprio. |
| Emotional Information Asymmetry | `consent_and_care_guardian` ("who knows what") | | ✅ | | | `events[].knowledge_delta` por conhecedor (personagem ou `READER`); conhecimento = projeção. |
| Narrative Debt / Relational Open Loops | seeds/payoffs (`plot_engineer.toml`) | | ✅ | | | `loops[]` guarda só identidade e pergunta; abertura/alimentação/resolução moram nos eventos. |
| Callback Seeds | elo `P` + `MEMORY_MOTIF_MAP` | ✅ | | | | Callback = evento que `feeds` um loop aberto antes. Sem conceito novo. |
| Relationship Archaeology | — | | | | ✅ | É uma **consulta** (`--relationship A B`) sobre eventos, não componente. |
| Belief Destruction | — | | ✅ | | | Operação `beliefs.revises` num evento. |
| Causal Character Foreshadowing | `unknowns`, `prohibited_inferences` do registry | | ✅ | | | `ground_truth[].reader_access` + ancestralidade `caused_by`. |
| Emotional Signature | `EMOTIONAL_RESPIRATION_MAP.md`, `living_book_vitals` | | ✅ | | | Campo por capítulo `emotional_movement {from,to,intensity}` em `chapter_architecture.yaml` (padrão de campo extra já usado). Declaração da assinatura no `BOOK_CONSTITUTION.md`. |
| Reader Experience State | `READER_VITALS.md` (pulso, gap, retenção) | ✅ | | | | Alvo pretendido, por capítulo, em prosa. Não entra no ledger (não é canon). |
| Surprise / Rupture mechanisms | — | | | | ✅ | Revisão de crença + contraste de amplitude já cobrem. |
| Normalization State | — | | | | ✅ | Sem evidência de necessidade; dessensibilização coberta pela Lei 05. FUTURE se aparecer evidência. |
| Taboo Ladder | — | | | | ✅ | GT `kind: TABOO/BOUNDARY` + deltas `boundary` + `consent.boundary_state` representam a progressão. |
| Canonical Consent State | `care_and_consent` (`a_morte`) | | ✅ | | | Bloco `consent` obrigatório em eventos íntimos/coercitivos, com percepções separadas. |
| Sexual Heat Profile | brief de capítulo (T1xx) | | ✅ | | | Seção de **planejamento de cena** no brief. Não é canon, não é estado, não é engine. |
| Narrative Camera Distance | brief de capítulo | | ✅ | | | Campo de cena. Invariante de não-reset é garantido pelo ledger (L2), não pela câmera. |
| Narrative Camera Shift | brief de capítulo | | ✅ | | | idem. |
| Human-Authored Scene Segment / Reentry Contract | `CANON_PROPOSAL_PROTOCOL` | | | | ✅ (MVP) | FUTURE: segmento humano entra pelo mesmo `CANON_UPDATE`. Nenhum contrato novo até haver uso real. |

### C.3 Expertise, originalidade, retelling, portfólio

| CONCEPT | EXISTING COMPONENT | REUSE | EXTEND | CREATE | DO NOT CREATE | JUSTIFICATION |
|---|---|---|---|---|---|---|
| Contextual Expertise Selection Layer | `agent_packs` + `rotate_pack` + `spawn` | ✅ | | | | Seleção mínima suficiente já é o que packs rotacionados fazem. |
| Scene Problem Profile | brief de capítulo | | | | ✅ (MVP) | FUTURE: seção do brief. |
| Expert Capability / Minimum Sufficient Panel / Constraint Ladder / Expert Confidence / Expert Trace | agent packs, `REVIEW_FINDING.severity` | ✅ | | | | Sem sistema novo; ordem de autoridade formalizada em H.3. |
| Reference Knowledge | — | | | | ✅ (MVP) | FUTURE. Regra anti-imitação entra como texto no `BOOK_CONSTITUTION` da obra. |
| Anti-Cliché | `detect_repetition.py` + `book/text_quality.yaml` + `REPETITION_AND_CLICHE_REVIEWER` + `GENRE_GUARDIAN` | | ✅ | | | Subconjunto **estrutural** vira regra do validador; clichês lexicais do gênero entram no `text_quality.yaml` do livro (override já suportado). |
| Originality Gate | `T602_ORIGINALITY_AUDIT` (`COPYRIGHT_ORIGINALITY_AUDITOR`) + `T601_LEGAL_GLOBAL` | ✅ | | | | Existe e é bloqueante em `GATE_LEGAL`. |
| Dark Classic Retelling | `creative_sources` do BOOK_SPEC, T602 | | | | ✅ (MVP) | FUTURE multiplier: `source_provenance` no pacote + IP Provenance no T602. Nenhum Retelling Engine. |
| Portfolio Governance (Book DNA, Cross-Book Similarity, Self-Cannibalization, Signature) | — | | | | ✅ (MVP) | FUTURE. O ledger por livro torna a comparação **mais barata depois**, mas não gratuita agora. A identidade autoral padrão do catálogo Dark Romance (`BEA_HALDEN_AUTHORIAL_GOVERNANCE`) já está registrada hoje como documentação, sem depender do ledger — ver seção S. |
| Causal Thread | eventos do ledger | ✅ | | | | É o próprio encadeamento `caused_by → delta → loop → belief`. Documentado em G; sem `CausalThreadEngine`. |

### C.3.1 Agentes reutilizados (nenhum criado)

| Papel na capability | Agente existente | Tarefa existente |
|---|---|---|
| Propor camadas GT/SM/SP | `CHARACTER_PSYCHOLOGIST` | T013 |
| Propor eventos planejados, loops e crenças do leitor | `PLOT_ENGINEER` | T016 |
| **Único escritor** do ledger | `CANON_GUARDIAN` | T018, T2xx_CANON_UPDATE |
| Alvo de experiência do leitor | `READER_VITALS_AGENT` | T032 |
| Pistas de releitura ↔ crenças | `SYMBOLISM_ARCHITECT` | T035 |
| Heat profile, câmera, evidência entregue ao leitor | `SCENE_ARCHITECT` | T1xx |
| Propor deltas realizados | `CHAPTER_WRITER`, `LEAD_NOVELIST` | T2xx_WRITE |
| Consentimento/manipulação | `ANTI_MANIPULATION_GUARDIAN` | T019, briefs, waves |
| Personality swap | `CHARACTER_CONTINUITY_REVIEWER` | waves |
| Veredito de Second-Read | `PROTECTED_SCENE_AUDITOR` (ou guardião declarado na cena) | T32xx |

---

## D. Constitutional Layer

As cinco leis estão **acima** de todo mecanismo derivado. Nenhuma regra de
validador, perfil de execução, alvo de experiência do leitor ou expectativa
de gênero pode revogá-las. Síntese constitucional:

> **THE PAST MUST BE ABLE TO CHANGE WITHOUT THE PAST CHANGING.**

Cada lei é verificada em duas camadas: a **parte estrutural**, checável
deterministicamente sobre o ledger, e o **resíduo de julgamento**, que continua
com agentes existentes. O validador nunca finge julgar literatura; o agente
nunca é chamado para contar.

| Lei | Verificação determinística (validador) | Resíduo de julgamento (agente existente) |
|---|---|---|
| **LAW 01 — CAUSAL CHARACTER** | L1: personagem maior tem ≥1 GT, ≥1 SM, ≥1 SP; todo evento estrutural tem `caused_by` que resolve para GT de participante ou evento anterior; token que não é id (`TROPE:`, `GENRE:`, `READER_TARGET:`, texto livre) é recusado; chaves de atributo de atração (`charm`, `sex_appeal`...) são recusadas | A GT em si é trope disfarçado? (`CHARACTER_PSYCHOLOGIST` no T013, `T019` com `GENRE_GUARDIAN`); personality swap na prosa (`CHARACTER_CONTINUITY_REVIEWER`) |
| **LAW 02 — IRREVERSIBLE RELATIONSHIP** | L2: evento estrutural com ≥2 participantes tem ≥1 `relationship_delta` com `from ≠ to`; `from` de cada delta **igual** ao estado projetado imediatamente anterior (pega amnésia e reset por troca de câmera) | A prosa realmente mostra a mudança? (revisores de wave) |
| **LAW 03 — LONG-HORIZON DESIRE** | L3: resolução de loop íntimo exige loop aberto em capítulo anterior, ≥`min_payoff_feeds` eventos alimentadores em capítulos distintos anteriores, `why_now` que resolve para ids, e delta relacional no próprio payoff (aftermath); `TRANSFORMED` exige loop sucessor | O payoff é *sentido* como inevitável e surpreendente? (`EMOTIONAL_EDITOR`, painel crítico) |
| **LAW 04 — READER BELIEF** | L4: conhecimento é monotônico; ninguém age sobre o que ainda não aprendeu; `READER` não recebe GT antes de `reader_access`; crença com `truth ≠ TRUE` é revisada depois ou marcada `left_open`; revisão divulga ao leitor a GT declarada. L5: pré-classificação do Second-Read | A evidência na página sustenta a interpretação pretendida? (`SUBTEXT_EDITOR`, auditoria de cena protegida) |
| **LAW 05 — EMOTIONAL AMPLITUDE** | L6: sobre `emotional_movement` por capítulo — sequência monotônica de intensidade acima de `max_monotonic_run`; `PEAK` sem capítulo anterior de intensidade menor | A curva é própria desta obra ou uma skin? (`EMOTIONAL_EDITOR`, `EMOTIONAL_REPETITION_AUDITOR`) |

**Second-Read Test** não é sexta lei: é um gate emergente das Leis 01 + 04
(ver I.2).

---

## E. Domain Model

### E.1 Por que um único arquivo, e por que separado do registry

- **Um arquivo:** o grafo causal é mais importante que qualquer componente. Se
  personagem, relação, crença e dívida morarem em arquivos diferentes, a
  ancestralidade atravessa fronteiras de dono e de versão. Um arquivo mantém
  todo elo resolvível por id numa leitura só.
- **Separado de `CANON_REGISTRY.yaml`:** o registry é livre e diverge entre
  runtimes (D4). O ledger precisa de contrato estrito para ser checável. Ficar
  separado também garante que livros sem a feature nunca vejam o arquivo e que
  `build_canon_digest.py` / `check_canon_continuity.py` não mudem de
  comportamento.
- **Mesma governança do canon:** dono `CANON_GUARDIAN`, lock `CANON_WRITE`,
  mutação só via `CANON_PROPOSALS`, `mutation_log` no próprio arquivo — idêntico
  ao registry de `a_morte`.

### E.2 Princípio de armazenamento

> **Eventos são a única fonte de verdade temporal. Todo "estado atual" é projeção.**

| Armazenado | Projetado (nunca armazenado) |
|---|---|
| `characters[]` (camadas GT/SM/SP, idade) | Reader Model de personagem |
| `relationships[].baseline` (t0) | estado relacional em qualquer capítulo |
| `events[]` com deltas | conhecimento de cada conhecedor, incluindo `READER` |
| `loops[]` (identidade + pergunta) | quem abriu/alimentou/resolveu cada loop; Intimacy Tension State |
| `beliefs[]` (interpretação + verdade) | quando foi estabelecida/revisada; cenas recontextualizadas |
| `mutation_log[]` | — |

### E.3 Contrato v0.1 (forma mínima)

Os nomes abaixo são o contrato proposto; `CAUSAL_LEDGER_TEMPLATE.yaml` será a
sua versão executável e testada (Slice 1). Enums pequenos e **categóricos**;
nenhum número de "quantidade de atração".

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: CausalLedger
metadata:
  project_id: <slug>
  version: 0.1.0
  owner: CANON_GUARDIAN

characters:
  - id: CHR-A                      # reutiliza o id do CANON_REGISTRY quando existir
    major: true
    age: 31                        # inteiro | null   (null = UNKNOWN ≠ adulto)
    age_source: /specs/CHARACTER_BIBLE.md#chr-a
    ground_truth:                  # ENGINE ONLY — nunca entregue ao leitor por padrão
      - id: GT-A-01
        kind: FEAR                 # FORMATIVE_HISTORY | WOUND | CORE_BELIEF | WORLDVIEW |
                                   # CONSCIOUS_WANT | UNCONSCIOUS_WANT | FEAR | NEED |
                                   # CONTRADICTION | DEFENSE | ATTACHMENT_PATTERN |
                                   # BOUNDARY | TABOO | SECRET | VULNERABILITY |
                                   # TRIGGER | CONDITION | MOTIVE
        statement: "..."
        reader_access: {from_event: EV-06}   # | NEVER | OPEN
    self_model:
      - id: SM-A-01
        statement: "..."
        diverges_from: [GT-A-01]   # opcional; ausência = coincide
    social_persona:
      - id: SP-A-01
        statement: "..."
        conceals: [GT-A-01]
    # continuidade física: referência a FACE_CANON/CHARACTER_BIBLE, não duplicada

relationships:
  - pair: CHR-A->CHR-B             # direcional; B->A é outra entrada
    baseline: {trust: NONE, desire: LATENT, fear: NONE, power_actual: A_OVER_B}

loops:
  - id: LP-01
    kind: INTIMACY                 # INTIMACY | EROTIC | VULNERABILITY | VERBAL |
                                   # POWER | RELATIONAL | PLOT
    pair: CHR-A<->CHR-B
    question: "..."

beliefs:
  - id: RB-01
    about: [EV-01]                 # ids de eventos e/ou personagens
    interpretation: "..."
    confidence: MEDIUM             # LOW | MEDIUM | HIGH
    expectation: "..."
    truth: FALSE                   # TRUE | INCOMPLETE | FALSE — ENGINE ONLY
    disclosed_by_revision: [GT-A-01]
    left_open: false

events:
  - id: EV-01
    status: REALIZED               # PLANNED | REALIZED
    chapter: 1
    structural: true
    kind: [REJECTION]              # vocabulário aberto; subconjuntos com regra: ver H
    actor: CHR-A
    participants: [CHR-A, CHR-B]
    facts: ["..."]                 # verdade canônica do que ocorreu (inclui off-page)
    caused_by: [GT-A-01]           # só ids: GT-* ou EV-* de capítulo anterior
    self_attribution: SM-A-01      # como o ator explica o próprio ato
    acts_on_knowledge: []          # ids que o ator precisa já saber
    interpretations:               # percepção, nunca verdade
      - {by: CHR-B, reads_as: "..."}
    relationship_delta:
      - {pair: CHR-B->CHR-A, dimension: trust, from: NONE, to: WARY}
    knowledge_delta:
      - {knower: READER, learns: [EV-01]}
    evidence_to_reader: ["..."]    # o que a página mostra; câmera muda isto, não `facts`
    loops: {opens: [], feeds: [], resolves: []}
    # resolves: [{loop: LP-01, mode: CLOSED|TRANSFORMED, into: LP-03, why_now: [EV-04]}]
    beliefs: {establishes: [RB-01], revises: []}
    consent: null                  # obrigatório em ADULT_KINDS e COERCION (ver H)
    # consent:
    #   canonical: CONSENSUAL      # CONSENSUAL | DUBIOUS | COERCIVE | NON_CONSENSUAL
    #   manipulation_present: false
    #   power_imbalance_present: true
    #   ability_to_refuse: FULL    # FULL | CONSTRAINED | NONE
    #   boundary_state: NEGOTIATED # RESPECTED | NEGOTIATED | PUSHED | VIOLATED
    #   perceived: {CHR-A: ..., CHR-B: ..., READER: ...}

mutation_log:
  - {version: 0.1.0, task: T018_CANON_REGISTRY, owner: CANON_GUARDIAN, action: "..."}
```

### E.4 Onde ficam os planos que não são canon

| Camada | Artefato | Dono | Pode alterar canon? |
|---|---|---|---|
| **CANON** | `canon/CAUSAL_LEDGER.yaml` (eventos `REALIZED`, GT, consentimento canônico) | `CANON_GUARDIAN` | é o canon |
| **STORY PLANNING** | eventos `PLANNED` no ledger; `chapter_architecture.yaml` (`emotional_movement`); `PLOT_DEPENDENCY_MAP.md`; `READER_VITALS.md` | pacote do livro / `PLOT_ENGINEER` / `READER_VITALS_AGENT` | não; plano pode mudar sem retcon porque o leitor ainda não o viu |
| **SCENE PLANNING** | `briefs/chapters/CHAPTER_NN_BRIEF.md` (heat profile, câmera, `evidence_to_reader` pretendido, alvo de experiência) | `SCENE_ARCHITECT` | não |
| **PROSE RENDERING** | `manuscript/` | `LEAD_NOVELIST` | não; só propõe |

**Regra de renderização:** quando a prosa não consegue realizar um delta
planejado (limite do modelo, *fade to black*, corte de câmera), o
`CANON_UPDATE` registra `evidence_to_reader` reduzida — **nunca** reescreve GT,
`facts` ou consentimento canônico para caber no que foi renderizado. Se o delta
relacional não aconteceu de fato, o evento volta a `PLANNED` e a wave recebe
`REVISION_REQUIRED`. Limitação de renderer não corrompe canon.

---

## F. State Ownership

Regra geral: **um dono escritor por arquivo**; os demais agentes propõem.
Nenhum estado aparece em duas listas de "armazenado".

| Estado | Owner | Writer | Readers | Persistence | Mutation rules |
|---|---|---|---|---|---|
| `characters[]` (GT/SM/SP, idade) | CANON_GUARDIAN | CANON_GUARDIAN (T018, T2xx_CANON_UPDATE) | CHARACTER_PSYCHOLOGIST, LEAD_NOVELIST, CHAPTER_WRITER, SCENE_ARCHITECT, revisores, validador | `canon/CAUSAL_LEDGER.yaml` | GT citada por evento `REALIZED` ou já divulgada ao `READER` é congelada (L0/L5); `age` só muda com entrada em `mutation_log` e nunca de adulto confirmado para `null` sem bloquear eventos íntimos |
| `relationships[].baseline` | CANON_GUARDIAN | CANON_GUARDIAN (T018) | validador, writers | ledger | congelado após o primeiro evento `REALIZED` do par |
| Estado relacional atual | — (projeção) | ninguém | todos, via `--relationship` | não persistido | calculado dobrando deltas em ordem de capítulo |
| `events[]` `PLANNED` | CANON_GUARDIAN | CANON_GUARDIAN a partir de proposta do PLOT_ENGINEER (T016) | SCENE_ARCHITECT, writers | ledger | livremente revisáveis via proposta até virarem `REALIZED` |
| `events[]` `REALIZED` | CANON_GUARDIAN | CANON_GUARDIAN (T2xx_CANON_UPDATE) a partir de CANON_PROPOSALS da wave | todos | ledger + snapshot por wave | `facts`, `caused_by`, `consent` imutáveis contra o snapshot anterior; correção só como nova entrada `mutation_log` com `action: RETCON`, que reprova L5 |
| `loops[]` | CANON_GUARDIAN | CANON_GUARDIAN | PLOT_ENGINEER, SCENE_ARCHITECT, validador | ledger | identidade e pergunta; ciclo de vida só em eventos |
| `beliefs[]` | CANON_GUARDIAN | CANON_GUARDIAN a partir de proposta do PLOT_ENGINEER/SYMBOLISM_ARCHITECT | READER_VITALS_AGENT, SCENE_ARCHITECT, auditor de cena protegida | ledger | `truth` e `disclosed_by_revision` congelados depois que a crença é estabelecida por evento `REALIZED` |
| Conhecimento por conhecedor | — (projeção) | ninguém | todos, via `--knowledge` | não persistido | dobra de `knowledge_delta` |
| Snapshot por wave | motor (tarefa determinística) | `run_deterministic.py` | validador (`--baseline`) | `canon/snapshots/CAUSAL_LEDGER.WAVE_NN.yaml` | somente escrita, nunca editado |
| `emotional_movement` por capítulo | pacote do livro | autor humano / NARRATIVE_ARCHITECT via pacote | validador L6, EMOTIONAL_EDITOR | `book/chapter_architecture.yaml` | alterado no pacote e recomposto, como qualquer campo do roteiro |
| Alvo de experiência do leitor | READER_VITALS_AGENT | READER_VITALS_AGENT (T032) | SCENE_ARCHITECT | `living_book/READER_VITALS.md` | não é canon; não pode ser citado como causa (L1) |
| Heat profile / câmera | SCENE_ARCHITECT | SCENE_ARCHITECT (T1xx) | writers | brief do capítulo | não é canon; não altera ledger |
| Achados | validador / revisores | validador escreve relatório | EXECUTIVE_EDITOR | `reviews/CAUSAL_LEDGER_REPORT*.md` + `validator_results` do `PROJECT_STATUS.yaml` | regenerado a cada execução |

**Duas fontes de verdade evitadas explicitamente:**

1. Relacionamento não é campo de personagem nem arquivo próprio: é baseline +
   deltas.
2. Dívida narrativa não duplica relacionamento: loop guarda a *pergunta*;
   o *estado* do par está só nos deltas. Um payoff muda os dois porque o
   evento carrega `loops.resolves` **e** `relationship_delta`.

---

## G. Causal Flow

### G.1 O grafo central mapeado a campos

| Nó do grafo | Campo no ledger | Tipo |
|---|---|---|
| `GROUND_TRUTH` | `characters[].ground_truth[]` | armazenado |
| `SELF_MODEL` | `characters[].self_model[]` + `diverges_from` | armazenado |
| `SOCIAL_PERSONA` | `characters[].social_persona[]` + `conceals` | armazenado |
| `BEHAVIOR` | `events[]` com `actor`, `facts`, `caused_by`, `self_attribution` | armazenado |
| `PARTNER_INTERPRETATION` | `events[].interpretations[]` | armazenado |
| `READER_INTERPRETATION` | `beliefs[]` estabelecidas pelo evento | armazenado |
| `ATTRACTION / REPULSION` | `relationship_delta` em `attraction`/`desire`/`fear`... | armazenado (delta) |
| `RELATIONSHIP_STATE` | dobra dos deltas | projeção |
| `NARRATIVE_DEBT` | `loops.opens/feeds` | armazenado (evento) |
| `FUTURE_BEHAVIOR` | evento posterior com `caused_by` → evento anterior | armazenado |
| `NEW_EVIDENCE` | `knowledge_delta` para `READER` / personagem | armazenado |
| `BELIEF_UPDATE` | `beliefs.revises` | armazenado (evento) |
| `RECONTEXTUALIZATION` | eventos que estabeleceram a crença revisada | projeção |

### G.2 Fluxo pelo pipeline

```text
CANON (T013, T016 propõem → T018 CANON_GUARDIAN escreve ledger)
  GT/SM/SP + baseline + eventos PLANNED + loops + crenças planejadas
        │   V_CAUSAL_LEDGER --mode plan              ⇒ GATE_CANON
        ▼
T021_LEDGER_SNAPSHOT (tool)  → snapshots/WAVE_00
        ▼
LIVING_BOOK (T032 alvos de leitor, T035 pistas ↔ crenças)
        ▼
BRIEFS (T1xx): cada brief cita os EV-* do capítulo, a evidência pretendida
               ao leitor, heat profile e câmera
        ▼
WAVE n: WRITE (writers propõem deltas realizados em CANON_PROPOSALS)
        → REVIEW → REVISION
        → CANON_UPDATE (CANON_GUARDIAN: PLANNED→REALIZED, evidence_to_reader real)
        │   V_CAUSAL_LEDGER_WAVE_n --mode realized --through-chapter N
        │                          --baseline snapshots/WAVE_{n-1}   ⇒ GATE_WAVE_n
        ▼
T2(n+1)_LEDGER_SNAPSHOT (tool) → snapshots/WAVE_n → próxima wave
        ▼
INTEGRATION: T32xx auditoria das cenas de revelação (Second-Read)
        │   V_CAUSAL_LEDGER_FINAL --mode final --baseline último snapshot
        ▼                                                  ⇒ GATE_FULL_MANUSCRIPT
Estado final do ledger = memória para continuação (L9)
```

### G.3 Exemplo de travessia (fixture do Apêndice 2)

`GT-A-02` (A teme que B vire alvo se for associada a ele) → `EV-01` A recusa B
em público, `self_attribution: SM-A-01` ("não me envolvo com ninguém") → B lê
como desprezo → leitor estabelece `RB-01` (A é indiferente; `truth: FALSE`) →
delta `B->A trust NONE→WARY`, `attraction NONE→PROVOKED` → `EV-02` abre
`LP-01` → `EV-03` mentira (`caused_by: GT-A-02, EV-01`) → `EV-04` cuidado
alimenta `LP-01` → `EV-05` payoff íntimo `TRANSFORMED` em `LP-03` com
`why_now: [EV-04]` → `EV-06` revelação: `knowledge_delta READER learns GT-A-02`,
`revises: [RB-01, RB-02]` → recontextualiza `EV-01` e `EV-03`, cujos `facts`
continuam idênticos ao snapshot e cuja ancestralidade já continha `GT-A-02`.

---

## H. Invariants

### H.1 Hard (bloqueiam; nenhum perfil rebaixa)

| ID | Invariante |
|---|---|
| INV-01 | `caused_by` contém apenas ids resolvíveis (`GT-*` de participante, ou `EV-*` de capítulo anterior). Trope, arquétipo, rótulo de gênero e alvo de leitor nunca são causa. |
| INV-02 | Personagem não possui atributo de atração; atração só existe como delta relacional direcional. |
| INV-03 | Evento estrutural com ≥2 participantes produz `R(t+1) ≠ R(t)`. |
| INV-04 | `from` de todo delta é igual ao estado projetado anterior (sem amnésia, sem reset por câmera). |
| INV-05 | Todo payoff de loop íntimo tem ancestralidade: loop aberto antes, alimentado em capítulos distintos anteriores, `why_now` resolvível, e delta relacional no próprio evento. |
| INV-06 | `ADULT_SEDUCTION_GATE`: todo participante de evento em `ADULT_KINDS` (`SEDUCTION`, `EROTIC_VERBAL`, `INTIMACY`, `SEXUAL`) e todo membro de par de loop `INTIMACY`/`EROTIC` tem `age` inteiro ≥ 18. `null` = FAIL. |
| INV-07 | Evento em `ADULT_KINDS` ou `COERCION` tem bloco `consent` completo; `perceived` nunca contém a chave `canonical`. |
| INV-08 | `CONSENT_DRIFT`: `consent` de evento `REALIZED` é idêntico ao snapshot anterior. |
| INV-09 | Evento com consentimento canônico `COERCIVE` ou `NON_CONSENSUAL` não resolve loop `INTIMACY`/`EROTIC`. Pode abrir ou alimentar loops `RELATIONAL`, `POWER`, `VULNERABILITY` — como consequência, nunca como recompensa. |
| INV-10 | `PAST_FACTS = CONSTANT`: `facts` e `caused_by` de eventos `REALIZED` e GT congelada são idênticos ao snapshot anterior. |
| INV-11 | Revisão de crença divulga ao leitor uma GT que já estava na ancestralidade transitiva de ao menos um evento que estabeleceu a crença. Sem isso é `RETCON_DISGUISED_AS_TWIST`. |
| INV-12 | `READER` não aprende GT antes de `reader_access.from_event`; GT `NEVER` nunca é aprendida pelo leitor. |
| INV-13 | Nenhum conhecedor tem `acts_on_knowledge` sobre o que ainda não aprendeu. |
| INV-14 | Livro sem `features.causal_ledger.enabled: true` compõe um `TASK_GRAPH.yaml` idêntico ao de hoje. |
| INV-15 | `STRUCTURAL_EVENT_WITHOUT_MUTATION`: todo evento `structural: true` tem ao menos um de `relationship_delta`, `knowledge_delta`, `loops.*` ou `beliefs.*` (cobre decisões solitárias; adicionado na revisão adversarial R). |

### H.2 Soft (achados MEDIUM/LOW; EXECUTIVE_EDITOR decide)

| ID | Invariante |
|---|---|
| SOFT-01 | Nenhuma sequência de mais de `max_monotonic_run` capítulos (padrão 3) com intensidade não decrescente. |
| SOFT-02 | Capítulo `PEAK` é precedido, dentro de dois capítulos, por intensidade `LOW` ou `MEDIUM`. |
| SOFT-03 | Crença com `truth ≠ TRUE` sem revisão nem `left_open` ao final. |
| SOFT-04 | Loop aberto sem nenhum `feeds` por mais de `max_loop_silence` capítulos (padrão 6) — tensão sem transformação. |
| SOFT-05 | Personagem maior sem nenhum `self_model.diverges_from` (camadas colapsadas). |
| SOFT-06 | Evento estrutural sem `evidence_to_reader`. |
| SOFT-07 | `UNUSED_GROUND_TRUTH`: GT de personagem maior que nenhum evento cita em `caused_by` até o final — atributo decorativo, não causa (adicionado na revisão adversarial R). |

### H.3 Regra de autoridade (formal)

Em conflito, vence a esquerda. Aplica-se a agentes, validadores, briefs e
perfis.

```text
CANON                    > EXPERTISE
CHARACTER_CAUSALITY      > GENRE_EXPECTATION
RELATIONSHIP_HISTORY     > GENERIC_TROPE
SCENE_CONTEXT            > SUBGENRE_LABEL
ABSTRACT_CRAFT_KNOWLEDGE > AUTHOR_IMITATION
MINIMUM_SUFFICIENT_EXPERTISE > EXPERT_SWARM
GROUND_TRUTH             > CONVENIENT_PLOT
CAUSALITY                > SHOCK_VALUE
MEMORY                   > RESET
IMMUTABLE_RULES / HARD INVARIANTS > READER_EXPERIENCE_TARGET
```

E, herdadas do motor: `immutable_rules.yaml` > `BOOK_CONSTITUTION.md` >
`CANON_REGISTRY` / ledger > bíblias > briefs > prosa.

**Princípios de fronteira:**

- `THE ENGINE KNOWS CAUSALITY. THE READER RECEIVES EVIDENCE.`
- `HEAT ≠ EXPLICITNESS`; `EXPLICIT_VOCABULARY ≠ GRAPHIC_MECHANICS`;
  `CAMERA_DISTANCE ≠ EMOTIONAL_DISTANCE`.
- `CAMERA_SHIFT MUST NOT RESET CHARACTER OR RELATIONSHIP STATE` (garantido por INV-04).
- `EXPERTISE_MUST_EXPLAIN_THE_CHARACTER, NEVER_REPLACE_THE_CHARACTER`.
- `AUTHORS ARE REFERENCES. EXPERT PERSONAS, IF EVER USED, ARE SYNTHETIC.`
- `UNKNOWN_PROVENANCE ≠ ORIGINAL`; `RETURN_TO_SOURCE_WHEN_IN_DOUBT` (FUTURE, retelling).
- Linguagem adulta não é tratada por lista de palavras proibidas; função
  linguística é julgada por contexto, personagem e voz. Dirty talk é extensão
  de `Character Voice` (VOICE_REFERENCE), não engine.

---

## I. Gates

### I.1 Agrupamento

Doze gates pedidos → **nenhum gate novo**. Um validador determinístico com
famílias de regras (`L0`–`L9`) anexado a três gates que já existem, mais
agentes e tarefas que já existem para o resíduo de julgamento.

| Gate pedido | Implementação | Onde roda | Bloqueante |
|---|---|---|---|
| Canon Consistency | **L0** integridade do ledger (ids únicos, referências resolvem, enums, ordem) + REUSE `T019_CANON_REVIEW`, `check_canon_continuity.py` | GATE_CANON, GATE_WAVE_n | sim |
| Character Causality | **L1** + REUSE `CHARACTER_CONTINUITY_REVIEWER` | todos | sim (estrutura) |
| Relationship Mutation | **L2** | GATE_WAVE_n, final | sim |
| Long-Horizon Payoff + Why-Now | **L3** (fundidos: why-now é condição do payoff) | plan (estrutura planejada), wave, final | sim |
| Reader Belief | **L4** + REUSE `SUBTEXT_EDITOR` | wave, final | sim (vazamento); soft (SOFT-03) |
| Second-Read Test | **L5** pré-classificação + REUSE `PROTECTED_SCENE_PROTOCOL` (veredito) | final; T32xx | L5 retcon: sim; veredito: agente + checkpoint humano |
| Emotional Amplitude | **L6** + REUSE `EMOTIONAL_EDITOR` | plan, final | não (soft) |
| Adult Seduction | **L7** | todos | **sempre**, independente de perfil |
| Canonical Consent / Consent Drift | **L8** + REUSE `ANTI_MANIPULATION_GUARDIAN` | todos | **sempre** |
| Anti-Cliché | subconjunto estrutural em L1/L2/L3/L8 + REUSE `detect_repetition.py` com `book/text_quality.yaml` + `REPETITION_AND_CLICHE_REVIEWER` + `GENRE_GUARDIAN` | wave, integração | estrutural: sim; lexical/julgamento: editorial |
| Originality | REUSE `T602_ORIGINALITY_AUDIT` em `GATE_LEGAL` | legal | sim (já é) |
| — (memória de continuação) | **L9** projeção final: loops abertos, crenças abertas, estado relacional final | final | não; relatório |
| — (imutabilidade) | **L10** baseline: INV-08, INV-10 contra snapshot | wave, final | sim |

Modos do validador:

| Modo | Regras | Escopo |
|---|---|---|
| `plan` | L0, L1, L3 (planejado), L4 (planejado), L6, L7, L8 (campos) | eventos `PLANNED` e `REALIZED` |
| `realized --through-chapter N --baseline S` | L0–L4, L7, L8, L10 | eventos `REALIZED` até N |
| `final --baseline S` | tudo, incluindo L5 e L9 | livro inteiro |

Saída: relatório Markdown ou `--json` com achados no shape de
`REVIEW_FINDING`; código de saída 1 se houver `HIGH` ou `BLOCKER` (mesma
convenção de `check_canon_continuity.py`). L6 e SOFT-* emitem no máximo `MEDIUM`.

### I.2 Second-Read Test — como a ancestralidade permite o teste

Pergunta: *depois das principais revelações, existem cenas anteriores cujo
significado muda substancialmente sem que os fatos dessas cenas precisem ser
alterados?*

```text
PAST_FACTS          = CONSTANT   (L10: facts/caused_by iguais ao snapshot)
PAST_INTERPRETATION = MUTABLE    (beliefs.revises)
```

Para cada crença revisada `RB` por um evento `R`:

1. `E(RB)` = eventos `REALIZED` que estabeleceram `RB` (projeção).
2. `G(RB)` = `disclosed_by_revision`; `R` precisa entregar `G(RB)` ao `READER`.
3. Para cada `e ∈ E(RB)`: `G(RB) ∩ ancestralidade_transitiva(e.caused_by) ≠ ∅`?
4. Para cada `e ∈ E(RB)`: `facts` e `caused_by` inalterados contra o snapshot?

**Pré-classificação estrutural** (evidência, **não** veredito):

| Resultado | Condição estrutural |
|---|---|
| `NOT_APPLICABLE` | nenhuma crença é revisada no livro |
| `WEAK` | alguma revisão falha em 3 ou 4 (retcon ou twist sem ancestralidade) — também bloqueia via INV-10/INV-11 |
| `PARTIAL` | 3 e 4 passam, mas só uma cena anterior é recontextualizada, ou a crença revisada tinha `confidence: LOW` |
| `STRONG` | 3 e 4 passam, ≥2 cenas em capítulos distintos são recontextualizadas, e a crença tinha `confidence ≥ MEDIUM` |

Não é fórmula de qualidade. Um `STRONG` estrutural pode ser literariamente
fraco se a página nunca sustentou a primeira interpretação. Por isso o
**veredito** vem da auditoria de cena protegida da revelação — o livro declara
a cena em `protected_scenes.yaml` com `must_preserve` ("a cena do cap. X
continua verdadeira palavra por palavra") e `reject_if` ("a revelação exige que
um fato anterior tenha sido diferente") — recebendo o relatório L5 como input.
Em STANDARD/PREMIUM, `GATE_FULL_MANUSCRIPT` já exige aprovação humana.

---

## J. Failure Modes

| Failure mode | Como aparece | Detecção | Onde |
|---|---|---|---|
| Trope substitution | GT é rótulo de gênero ("possessivo porque é mafioso") | L1 recusa causa não-id; conteúdo da GT: T019 + GENRE_GUARDIAN | plan / canon |
| Personality swap | voz ou escolha incompatível com GT/SM na prosa | CHARACTER_CONTINUITY_REVIEWER; SOFT-05 sinaliza camadas colapsadas | wave |
| Relationship amnesia | cena íntima ou traição sem consequência na cena seguinte | INV-03, INV-04 (`from` diverge do estado projetado) | wave |
| Payoff without history | intimacy porque "chegou o capítulo" | INV-05 (`HEAT_WITHOUT_HISTORY`) | plan / wave |
| Fake foreshadowing | pista sem ligação causal com a verdade | INV-11 (GT fora da ancestralidade) | final |
| Retcon disguised as twist | revelação exige fato passado diferente | INV-10 contra snapshot; L5 `WEAK` | wave / final |
| Reader omniscience leakage | narrador entrega GT cedo | INV-12 no ledger; na prosa, SUBTEXT_EDITOR com `reader_access` como critério | wave |
| Information leak | personagem age sobre o que não sabe | INV-13 | wave |
| Endless tension without transformation | loop aberto indefinidamente | SOFT-04; L9 lista loops abertos | final |
| Continuous escalation | cada capítulo mais sombrio/explícito | SOFT-01, SOFT-02 | plan / final |
| Ornamental intimacy | cena íntima sem mudança de estado | INV-03 + INV-05 (payoff sem delta = `POST_PAYOFF_AMNESIA`) | wave |
| Consent drift | consentimento reescrito para tornar payoff palatável | INV-08, INV-09 | wave / final |
| Cliché generation | frase feita do gênero, sedução genérica | `detect_repetition.py` + `book/text_quality.yaml`; REPETITION_AND_CLICHE_REVIEWER; GENRE_GUARDIAN | wave / integração |
| Minor sexualization | participante sem idade confirmada | INV-06 — FAIL em `null` | todos |
| Renderer corrupts canon | canon ajustado ao que a prosa conseguiu mostrar | E.4 regra de renderização; INV-10 | wave |
| Overengineering | módulos para perspectivas, engines por nome | R (revisão adversarial); essencialismo nos slices; nenhum slice só de scaffolding | processo |
| Ledger authoring drift | agente escreve ledger inconsistente | L0 bloqueia; template testado; exemplos no `canon/AGENTS.md` | canon / wave |

---

## K. MVP Scope

### IN

- Contrato do ledger (template executável) e validador determinístico com
  L0–L10.
- Projeções: estado relacional, conhecimento, crenças, loops, ancestralidade.
- Relatórios de explicabilidade (seção N).
- Fixture de 6 capítulos (Apêndice 2), sem prosa, com as sete provas da tese.
- Integração OFF por padrão no compositor, com teste de não-regressão para
  todos os livros existentes.
- Instruções escopadas `canon/AGENTS.md` e extensões de inputs/outputs/
  parameters das tarefas T013, T016, T018, T1xx, T2xx.

### OUT

- Qualquer agente novo, engine, serviço, roteador, votação, persona.
- Heat profile como estado; qualquer escala numérica de calor ou excitação.
- Normalization State, Taboo Ladder, Surprise engine.
- Geração de prosa explícita como critério de sucesso do MVP.
- Mudança nos 66 `.toml` genéricos ou nos scripts existentes além do bloco
  condicional do compositor.

### FUTURE

- Genre profile reutilizável para Dark Romance (depende de Q1).
- Scene Problem Profile e Constraint Ladder como seções de brief.
- Reference Knowledge com fluxo `REFERENCE → CRAFT_OBSERVATION →
  ABSTRACT_PATTERN → GENERIC_CAPABILITY`.
- Dark Classic Retelling: `source_provenance`, `public_domain_confidence`,
  jurisdição/edição/tradução, `SOURCE_PURITY_RULE`,
  `PROTECTED_DERIVATIVE_FIREWALL` dentro de T602/T601.
- Human-Authored Scene Segment / Reentry pelo `CANON_UPDATE`.
- Portfolio Governance (Book DNA a partir dos ledgers, Cross-Book Similarity,
  Authorial Self-Cannibalization Gate). Para o catálogo Dark Romance, o
  conceito provisório de "Pedro Arte Signature" é especializado como
  `BEA_HALDEN_AUTHORIAL_SIGNATURE` (ver seção S); a identidade Pedro Arte
  permanece inalterada para os demais catálogos/gêneros.
- Guardião de consentimento genérico, se um segundo livro repetir o padrão de
  `CONSENT_AND_CARE_GUARDIAN` (hoje é por livro, e está certo assim).

### Tese do MVP

```text
DARK_ROMANCE_CORE_THESIS_STRUCTURAL = PROVEN   ao fim do Slice 3
  (a arquitetura representa e verifica as 7 propriedades num cenário)
DARK_ROMANCE_CORE_THESIS            = PROVEN   ao fim do Slice 6
  (o pipeline LLM produz um texto curto que as satisfaz, com veredito humano)
```

A distinção é deliberada: uma fixture escrita à mão prova que o sistema
*reconhece* causalidade e memória; só a execução prova que o motor as *produz*.

---

## L. Slice Plan

Cada slice entrega comportamento observável e é aprovado antes do próximo.
Nenhum slice é só scaffolding. Slices 1–3 não tocam o compositor: risco de
regressão zero por construção.

### Slice 1 — Ledger causal: personagem, relação, payoff e idade adulta

- **Objetivo:** provar as teses 1, 2 e 3 no nível do ledger e travar o gate
  adulto desde o primeiro dia.
- **Arquivos esperados:**
  - `engine/scripts/check_causal_ledger.py` (novo; stdlib + PyYAML)
  - `engine/templates/CAUSAL_LEDGER_TEMPLATE.yaml` (novo)
  - `tests/fixtures/causal_ledger/mvp_ledger.yaml` (novo; capítulos 1–5 do Apêndice 2)
  - `tests/test_causal_ledger.py` (novo; `unittest`, offline)
- **Contratos:** E.3 (`characters`, `relationships`, `loops`, `events` sem
  `beliefs`); shape de achado de `REVIEW_FINDING`.
- **Regras:** L0, L1, L2, L3, L7; modo `plan`; `--why EV`, `--relationship A B`,
  `--payoff EV`.
- **Testes:**
  - fixture válida → exit 0, zero achados HIGH/BLOCKER;
  - template válido → exit 0 (template não deriva do validador);
  - mutações em memória (cópia do dict), cada uma com exatamente a categoria esperada:
    `caused_by: ["TROPE:alpha"]` → `GENRE_LABEL_CAUSALITY`;
    `characters[0].charm: 95` → `ATTRACTION_AS_ATTRIBUTE`;
    delta removido de evento estrutural → `RELATIONSHIP_AMNESIA`;
    `from` diferente do estado projetado → `STATE_RESET`;
    payoff com um único alimentador → `HEAT_WITHOUT_HISTORY`;
    payoff sem delta → `POST_PAYOFF_AMNESIA`;
    `age: null` em participante de `INTIMACY` → `ADULT_SEDUCTION_FAIL` (BLOCKER);
    `age: 17` → idem;
  - tese 1: existe evento cujo `caused_by` contém GT listada em
    `self_attribution.diverges_from`;
  - projeção: `--relationship CHR-B CHR-A` no capítulo 5 retorna a sequência de
    estados esperada.
- **Acceptance criteria:** todos os testes passam com
  `.venv/Scripts/python.exe -m unittest tests.test_causal_ledger -v` sem rede;
  `validate-engine` continua `ENGINE VALID | generic agents: 66`.
- **Regressions protected:** nenhuma alteração em arquivos existentes
  (verificável por `git diff --stat` mostrando só arquivos novos).
- **Dependencies:** nenhuma.
- **Estimated complexity:** M (~350–450 linhas de validador, ~250 de teste).

### Slice 2 — Tempo: crença do leitor, assimetria, imutabilidade e consentimento

- **Objetivo:** provar as teses 4 e 5 e impedir consent drift.
- **Arquivos esperados:** `check_causal_ledger.py` (estende);
  `tests/fixtures/causal_ledger/mvp_ledger.yaml` (+ capítulo 6, `beliefs`,
  `knowledge_delta`, `consent`); `tests/fixtures/causal_ledger/snapshot_wave_01.yaml`;
  `tests/test_causal_ledger.py` (estende).
- **Contratos:** `beliefs`, `knowledge_delta`, `acts_on_knowledge`,
  `reader_access`, `consent`, `--baseline`.
- **Regras:** L4, L5 (pré-classificação), L8, L10; modos `realized` e `final`;
  `--knowledge KNOWER --at-chapter N`, `--beliefs --at-chapter N`,
  `--recontextualized`.
- **Testes:** fixture → L5 `STRONG` para `RB-01`; mutações:
  `facts` de `EV-01` alterado vs snapshot → `RETCON` + L5 `WEAK`;
  `GT-A-02` removida da ancestralidade de `EV-01` e `EV-03` → `RETCON_DISGUISED_AS_TWIST`;
  leitor aprende `GT-A-02` no cap. 3 → `READER_OMNISCIENCE_LEAK`;
  B age sobre a mentira antes de aprendê-la → `INFORMATION_LEAK`;
  `consent.canonical` alterado vs snapshot → `CONSENT_DRIFT`;
  `perceived.canonical` presente → `CONSENT_LAYER_COLLAPSE`;
  evento `COERCIVE` resolvendo `LP-01` → `COERCION_AS_PAYOFF`;
  evento `INTIMACY` sem bloco `consent` → `CONSENT_MISSING`;
  tese 4: `RB-01.truth == FALSE` e todos os fatos entregues ao leitor antes
  do cap. 6 pertencem a `facts` de eventos reais.
- **Acceptance criteria:** idem Slice 1; relatório `--recontextualized` lista
  `EV-01` e `EV-03` com "fatos inalterados: sim".
- **Regressions protected:** testes do Slice 1 intactos.
- **Dependencies:** Slice 1.
- **Estimated complexity:** M.

### Slice 3 — Amplitude e memória de continuação (tese estrutural completa)

- **Objetivo:** provar as teses 6 e 7 e fechar
  `DARK_ROMANCE_CORE_THESIS_STRUCTURAL = PROVEN`.
- **Arquivos esperados:** `check_causal_ledger.py` (estende);
  `tests/fixtures/causal_ledger/chapter_architecture.yaml` (6 capítulos com
  `emotional_movement`); `tests/test_causal_ledger.py` (+ `TestCoreThesis`).
- **Regras:** L6, L9; `--end-state`.
- **Testes:** fixture sem achados L6; mutação com intensidades
  `MEDIUM,HIGH,HIGH,PEAK,PEAK` → `CONTINUOUS_ESCALATION`; `PEAK` sem vale →
  `PEAK_WITHOUT_CONTRAST`; `--end-state` retorna `LP-03` aberto, estado
  relacional final ≠ baseline, crenças fechadas; `TestCoreThesis` com um teste
  nomeado por prova (1–7) sobre a mesma fixture.
- **Acceptance criteria:** os 7 testes da tese passam; o relatório final cabe
  numa tela e responde às seis perguntas da seção N.
- **Regressions protected:** Slices 1–2.
- **Dependencies:** Slice 2.
- **Estimated complexity:** S–M.

### Slice 4 — Integração OFF por padrão no compositor

- **Objetivo:** runtime de um livro com a feature ligada recebe o ledger,
  validadores nos gates e snapshots; qualquer outro livro compõe exatamente
  como hoje.
- **Arquivos esperados:** `engine/scripts/livingbook.py` (bloco condicional
  via `.get()`; `TOOL_BY_PATTERN` para `T*_LEDGER_SNAPSHOT`; cópia do script e
  do template; `canon/AGENTS.md` condicional); `engine/IMPLEMENT.md` (um
  parágrafo apontando para `canon/AGENTS.md` quando existir);
  `tests/test_compose_regression.py` (novo); `tests/fixtures/books/causal_ledger_mvp/`
  (pacote mínimo de 6 capítulos, `DRAFT`).
- **Contratos:** `BOOK_SPEC.spec.features.causal_ledger: {enabled, min_payoff_feeds, max_monotonic_run, max_loop_silence}`
  (nome sujeito a Q1).
- **Testes:** golden — antes de alterar o compositor, gravar o dict de
  `build_standard_graph()` de cada livro em `books/` e comparar igualdade
  exata depois; livro fixture → T018 declara `/canon/CAUSAL_LEDGER.yaml`,
  `GATE_CANON`/`GATE_WAVE_n`/`GATE_FULL_MANUSCRIPT` têm `V_CAUSAL_LEDGER*`,
  `T021_LEDGER_SNAPSHOT` tem `tool`; `validate_graph` sem erros; compose em
  diretório temporário + `smoke-test` OK.
- **Acceptance criteria:** INV-14 provado por teste; `smoke-test` do fixture
  `SMOKE TEST OK`.
- **Regressions protected:** grafos de `a_morte_ainda_nao_nasceu`,
  `motor-de-livros-vivos`, `o_jardim_dos_doze`, `eva-...`, `adao-...`,
  `loja-...` idênticos; perfis e checkpoints humanos inalterados.
- **Dependencies:** Slice 3; decisão Q1.
- **Estimated complexity:** M.

### Slice 5 — Instruções de tarefa sem agentes novos

- **Objetivo:** as tarefas existentes sabem ler, propor e manter o ledger.
- **Arquivos esperados:** `livingbook.py` (inputs/outputs/parameters condicionais
  em T013, T016, T018, T032, T035, T1xx, T2xx_WRITE, T2xx_CANON_UPDATE);
  `engine/templates/CAUSAL_LEDGER_RUNBOOK.md` (fonte do `canon/AGENTS.md`);
  pacote fixture com cena de revelação em `protected_scenes.yaml` e clichês de
  gênero em `text_quality.yaml`.
- **Testes:** golden do Slice 4 continua verde; fixture composto tem os inputs
  esperados por tarefa; runbook cita apenas campos que o validador conhece
  (teste que extrai nomes de campo do runbook e compara ao template).
- **Acceptance criteria:** um executor humano consegue seguir `canon/AGENTS.md`
  sem ler esta SDD.
- **Regressions protected:** INV-14.
- **Dependencies:** Slice 4.
- **Estimated complexity:** M.

### Slice 6 — Execução real curta (opcional, paga)

- **Objetivo:** fechar `DARK_ROMANCE_CORE_THESIS = PROVEN`.
- **Arquivos esperados:** nenhum código; runtime gerado do pacote fixture;
  `reviews/` e `CAUSAL_LEDGER_REPORT_FINAL.md` produzidos pela execução.
- **Testes:** execução `DRAFT` de 3–6 capítulos; validador final sem
  HIGH/BLOCKER; auditoria da cena de revelação; aprovação humana em
  `project_state/APPROVALS/`.
- **Acceptance criteria:** o autor responde "sim" ao Second-Read Test lendo a
  prosa, e o relatório estrutural concorda.
- **Regressions protected:** nenhuma mudança de código.
- **Dependencies:** Slice 5; orçamento aprovado; capacidade do host de gerar o
  conteúdo pretendido dentro das políticas do modelo.
- **Estimated complexity:** L (tempo e custo, não código).

---

## M. Testing Strategy

Convenção do repositório: `unittest` (pytest não está instalado), scripts
importados via `sys.path` para `engine/scripts`, sem dependência nova.

| Camada | O que prova | Onde | Determinístico | Padrão |
|---|---|---|---|---|
| Unit | cada regra L0–L10 isolada; projeções (dobra de deltas, conhecimento, ancestralidade transitiva) | `tests/test_causal_ledger.py` | sim | sempre |
| Contract | template e fixture passam; runbook só cita campos conhecidos; achados no shape de `REVIEW_FINDING` | idem | sim | sempre |
| State transition | `from` = estado anterior; `PLANNED → REALIZED`; snapshot N−1 → N sem mudança em passado | idem | sim | sempre |
| Causal-chain | ancestralidade de payoff; GT revelada ∈ ancestralidade das cenas recontextualizadas; `TestCoreThesis` 1–7 | idem | sim | sempre |
| Regression | INV-14: grafo de cada livro existente idêntico ao golden | `tests/test_compose_regression.py` | sim | sempre (a partir do Slice 4) |
| Integration | compose + smoke-test do pacote fixture em diretório temporário; `validate-gate` executa `V_CAUSAL_LEDGER*` | idem | sim | sempre (a partir do Slice 4) |
| Optional paid-LLM evaluation | o pipeline produz prosa que satisfaz o ledger e o Second-Read humano | Slice 6, manual | não | **nunca** na suíte padrão |

Regras:

- Mutações de fixture são feitas em memória a partir de uma fixture válida;
  cada teste afirma **a categoria exata** do achado, não só "falhou".
- Fixtures não contêm prosa nem descrição explícita: só fatos resumidos,
  estados e ids.
- Por causa de D10, os testes novos são executados por módulo
  (`-m unittest tests.test_causal_ledger tests.test_compose_regression`), e o
  relatório de cada slice registra o comando exato. Tornar
  `tests/test_image_generation.py` opt-in por variável de ambiente é
  recomendável, mas fica fora desta capability.

---

## N. Observability / Explainability

Todas as respostas vêm do mesmo arquivo e do mesmo script. Nenhum log novo,
nenhum trace store.

| Pergunta | Comando | Resposta |
|---|---|---|
| `WHY DID THIS CHARACTER DO THIS?` | `check_causal_ledger.py --runtime . --why EV-03` | árvore de `caused_by` até GTs; `self_attribution` e divergência declarada; persona exibida |
| `WHAT CHANGED IN THE RELATIONSHIP?` | `--relationship CHR-B CHR-A [--at-chapter N]` | linha do tempo `dimension: from → to` por evento, a partir do baseline |
| `WHAT DID THE READER KNOW?` | `--knowledge READER --at-chapter N` | ids aprendidos, evento de origem, GTs ainda bloqueadas por `reader_access` |
| `WHAT DID THE READER BELIEVE?` | `--beliefs --at-chapter N` | crenças ativas, `confidence`, expectativa; `truth` só com `--engine-view` |
| `WHICH PAST EVENTS CAUSED THIS PAYOFF?` | `--payoff EV-05` | loop resolvido, alimentadores por capítulo, `why_now`, delta de aftermath, loop sucessor |
| `WHICH OLD SCENES WERE RECONTEXTUALIZED?` | `--recontextualized` | por crença revisada: cenas, GT divulgada, ancestralidade ok, fatos inalterados, pré-classificação L5 |
| Estado para continuar a obra | `--end-state` | loops abertos, crenças abertas, estado relacional final, GTs nunca divulgadas |

Persistência de diagnóstico: `validate-gate` já grava `stdout`/`stderr` do
validador em `project_state/PROJECT_STATUS.yaml → validator_results`. Os
relatórios legíveis vão para `reviews/CAUSAL_LEDGER_REPORT_<modo>.md`.

**Proteção de vazamento na observabilidade:** a visão padrão dos comandos de
leitor omite `truth` e GT não divulgada; `--engine-view` é explícito. Isso
evita que um brief ou prompt de escrita receba, por colagem de relatório, a
verdade que a cena não pode revelar.

---

## O. Migration / Compatibility

- **OFF por padrão**, seguindo o padrão das features do motor: ausência de
  `features.causal_ledger` ≡ `enabled: false`, lido com `.get()` (D9).
- **Nenhum livro existente muda:** INV-14 com teste golden sobre os seis
  pacotes em `books/`.
- **Nenhum runtime existente muda:** runtimes são gerados; nada é migrado.
  Um runtime já composto só ganha a capability se o pacote ligar a flag e for
  recomposto (regra atual do motor: "edite o pacote e recomponha").
- **Nenhum `.toml` genérico muda.** Instruções chegam por `canon/AGENTS.md`
  condicional e por inputs/parameters das tarefas.
- **Scripts existentes não mudam** (`build_canon_digest.py`,
  `check_canon_continuity.py`, `detect_repetition.py`): o ledger é arquivo
  separado. Integração futura com o digest é opcional.
- **Perfis:** `DRAFT` pode rebaixar gates que já rebaixa hoje; as regras hard
  do validador (INV-06..INV-10) retornam exit 1 em qualquer perfil, e os gates
  a que se anexam (`GATE_CANON`, `GATE_WAVE_n`, `GATE_FULL_MANUSCRIPT`) não
  constam de nenhuma lista `non_blocking_gates`.
- **Versão:** ledger `apiVersion: pedroarte.livingbooks/v1`, `kind: CausalLedger`,
  `metadata.version` semântica; mudança incompatível de contrato = nova versão
  de template + regra de validador que recusa versão desconhecida.
- **Trabalho em andamento:** as mudanças não commitadas em
  `build_canon_digest.py`/`build_kdp_docx.py` e os livros não rastreados (D12)
  devem ser resolvidos pelo autor antes do Slice 4, que precisa de um golden
  estável.

---

## P. Risks / Open Questions

### P.1 Pergunta bloqueante (bloqueia o Slice 4, não o Slice 1)

**Q1 — Onde vive o DNA de Dark Romance e como a flag se chama.**
Evidência: `engine/AGENTS.md` proíbe vetos específicos de gênero em `/engine`
(D8). A parte proposta para `/engine` (ledger, validador, flag) é neutra: não
contém tropes, clichês, subgêneros nem vocabulário do gênero; as regras são de
causalidade, memória, consentimento e idade adulta, e têm precedentes em livros
que não são romance (`a_morte`, `eva`).

| Opção | Custo | Risco |
|---|---|---|
| **A (recomendada)** — flag neutra `features.causal_ledger` no motor; DNA de Dark Romance (assinatura emocional, heat profile de referência, clichês de gênero, cenas de revelação protegidas) no pacote de cada livro | zero mudança de governança; duplicação entre livros de Dark Romance | duplicação até existir o segundo livro real |
| B — `features.dark_romance` no motor + `engine/genre_profiles/dark_romance/` | emenda explícita em `engine/AGENTS.md` | abstrair antes do segundo caso real (mesmo alerta do precedente citado em `discovery-books/09`) |

A recomendação é A agora e reavaliar B após o segundo livro de Dark Romance.
O nome comercial `DARK_ROMANCE_CANON_ARCHITECT` continua sendo o nome da
capability no pacote e na documentação.

### P.2 Riscos

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Custo de autoria: CANON_GUARDIAN (tier S) mantém um YAML denso a cada wave | alta | ledger só para personagens maiores e eventos estruturais; template com exemplos; L0 barato e imediato; medir no Slice 6 via `COST_LEDGER.md` |
| Ledger vira "planilha de atributos" | média | INV-01/INV-02; enums categóricos; SOFT-05; revisão adversarial R |
| Correção estrutural ≠ qualidade literária | alta | deliberado: validador prova a estrutura, agentes e humano julgam a página; L5 é evidência, não veredito |
| Deriva entre prosa e ledger (prosa mostra algo que o ledger não registra) | média | proposta obrigatória no `WRITE`; revisores de wave comparam evidência na página com `evidence_to_reader` |
| Modelo hospedeiro recusa ou suaviza cenas adultas | média | fora do controle do motor; o ledger não depende de explicitude (`HEAT ≠ EXPLICITNESS`); Slice 6 registra como `CAPABILITY_BLOCKER`, nunca contorna |
| Locks textuais (D11) permitem escrita concorrente do ledger | baixa | `concurrent_write: false` já é política; L10 detecta mudança de passado entre snapshots |
| Suíte de testes existente com chamada paga (D10) | média | testes novos por módulo; recomendação registrada |
| Golden de compose instável por working tree sujo (D12) | média | resolver D12 antes do Slice 4 |

---

## Q. Final Recommendation

```text
READY_FOR_SLICE_1 = YES
```

Justificativa:

1. **Arquitetura real conhecida:** compositor, máquina de estados, gates,
   validadores, protocolo de canon e precedentes (`a_morte`, `eva`) foram
   lidos no código e nos runtimes, não inferidos da documentação.
2. **Menor desenho possível:** um arquivo de canon, um validador, um template,
   uma flag. Zero agentes, zero engines, zero gates novos, zero
   `ARCHITECTURAL_EXCEPTION_CANDIDATE`.
3. **Slice 1 é independente de toda pergunta aberta:** cria apenas arquivos
   novos neutros de gênero, não toca o compositor, não depende de Q1, roda
   offline com a dependência já instalada (PyYAML).
4. **Comportamento observável desde o Slice 1:** o validador aceita a fixture
   e recusa cada falha nomeada com a categoria exata, incluindo o gate adulto.
5. **Compatibilidade garantida por teste** antes de qualquer mudança no
   compositor (Slice 4).

Condição para o Slice 4: decisão humana sobre Q1 e working tree limpo (D12).

---

## R. Revisão adversarial (Final Gate do SDD)

Cada pergunta foi usada para tentar derrubar o desenho. Onde a resposta foi
"sim, pode acontecer", o SDD foi corrigido e a correção está registrada.

| Pergunta | Resposta | Correção aplicada |
|---|---|---|
| Estamos apenas construindo um trope engine sofisticado? | Não. O ledger não tem vocabulário de trope; `kind` de evento é vocabulário aberto e **nunca** é causa — só aciona subconjuntos de regra (`ADULT_KINDS`, `COERCION`). Tropes vivem no pacote do livro como configuração criativa. | INV-01 recusa qualquer causa que não seja id. |
| Algum personagem ainda pode virar lista de atributos? | **Sim, parcialmente:** GT é uma lista de enunciados, e um enunciado nunca citado é atributo decorativo. | Adicionado **SOFT-07 `UNUSED_GROUND_TRUTH`** (GT de personagem maior que nenhum evento cita até o final). Mantidos INV-02 e SOFT-05. |
| Existe mais de uma fonte de verdade para relacionamento? | Não. Baseline + deltas; estado atual é projeção; loops não guardam estado do par. | Primeira versão do rascunho tinha `loops.opened_by/fed_by`: movido para os eventos (E.2). |
| Reader Model está sendo confundido com Reader Experience? | Não. Reader Model = crenças do leitor (canon, com `truth` só para o motor). Reader Experience = afeto pretendido em `READER_VITALS.md` (não canon, não causa). | L1 recusa alvo de leitor como causa. |
| Reader Belief está sendo confundido com Character Knowledge? | Não. `READER` é um conhecedor em `knowledge_delta` (o que sabe); `beliefs[]` é só do leitor (o que acha que significa); percepção de personagem é `interpretations[]` do evento. Três campos distintos. | — |
| Sexual Heat está duplicando Sexual Tension? | Não. Tension = loops + deltas (canon). Heat = parâmetros de renderização da cena no brief (não canon, não estado). | Heat profile rebaixado de "estado" para "seção de brief" (C.2). |
| Narrative Debt está duplicando Relationship State? | Não. Loop guarda a pergunta; o estado está nos deltas; o payoff altera os dois no mesmo evento. | — |
| Ground Truth pode vazar indevidamente? | **Sim, na prosa:** writers precisam ler GT para escrever causalmente. O ledger impede vazamento estrutural (INV-12), não o de uma frase. | Visão padrão de observabilidade oculta `truth` e GT não divulgada; `evidence_to_reader` explícito no brief; SUBTEXT_EDITOR usa `reader_access` como critério. Risco residual registrado em P.2. |
| Um twist pode passar sem causal ancestry? | Não estruturalmente: INV-11 bloqueia. Pode passar um twist com ancestralidade formal e sem sustentação na página. | Veredito por auditoria de cena protegida + checkpoint humano (I.2). |
| Um payoff pode passar sem memória? | Não: INV-05 exige alimentadores anteriores e delta de aftermath. | — |
| Uma cena estrutural pode terminar sem state mutation? | **Sim:** INV-03 só cobria eventos com ≥2 participantes; uma decisão solitária estrutural passava sem nada mudar. | Adicionado **INV-15 `STRUCTURAL_EVENT_WITHOUT_MUTATION`**: todo evento `structural: true` tem ao menos um de `relationship_delta`, `knowledge_delta`, `loops.*`, `beliefs.*`. |
| Estamos criando módulos para conceitos que deveriam ser propriedades? | Não depois das correções: Reader Model, Intimacy Tension, Relationship Archaeology, Callback, Camera, Heat, Taboo Ladder e Emotional Signature viraram campo, projeção ou consulta. | JSON Schema removido (D2); `dark_romance_profile.yaml` removido do MVP; Human Reentry adiado. |
| Estamos criando agentes sem evidência? | Não. Zero agentes; tabela C.3.1 mapeia cada papel a um agente existente. | — |
| O MVP está tentando provar coisas demais? | O núcleo determinístico (Slices 1–3) prova só as 7 teses. Slice 5 existe apenas para permitir o Slice 6; ambos podem ser adiados sem invalidar a prova estrutural. | Separadas `THESIS_STRUCTURAL` e `THESIS` (K). |
| Uma obra não-Dark-Romance continua funcionando exatamente como antes? | Sim, por INV-14 com teste golden sobre os seis pacotes antes de tocar o compositor. | Golden gravado **antes** da alteração (Slice 4). |
| O Second-Read virou fórmula? | Não: pré-classificação categórica por condições estruturais, explicitamente sem valor de veredito. | Texto de I.2 reforçado. |
| Um perfil DRAFT pode desligar o gate adulto ou de consentimento? | Não: são exit 1 em qualquer modo, em gates que nenhum perfil rebaixa. | O. |

---

## S. Authorial / Portfolio Governance — `BEA_HALDEN_AUTHORIAL_GOVERNANCE`

> **Natureza desta seção:** registra uma decisão editorial/comercial **já
> aprovada por humano**, fora do ciclo de aprovação de slices. Não introduz
> agente, engine, capability, gate, invariante ou lei. É **documentação de
> governança**, aplicada via campo já existente do motor (`metadata.author`
> de `BOOK_SPEC.yaml`, ver S.2). Segue `REUSE > EXTEND > CREATE` e
> `SIMPLICIDADE SEMPRE`, como o resto desta SDD.

### S.1 Decisão canônica

```text
DEFAULT_AUTHOR_IDENTITY = BEA_HALDEN
```

Para toda obra classificada como Dark Romance neste catálogo, o nome autoral
público padrão para publicação, metadados editoriais e governança de catálogo
é:

```text
Bea Halden
```

Somente uma instrução humana explícita sobrescreve essa identidade para uma
obra específica. O motor nunca infere outro pseudônimo automaticamente.

### S.2 Onde `Bea Halden` vive arquiteturalmente

**Não em código novo.** O motor já possui exatamente o campo necessário:

| Componente existente | Papel |
|---|---|
| `BOOK_SPEC.yaml → metadata.author` | campo obrigatório (`engine/contracts/BOOK_SPEC.schema.json:23`), hoje `Pedro Arte` em todos os seis pacotes de `books/` |
| `engine/scripts/build_kdp_docx.py:424,492` | lê `book["author"]` e grava na página de rosto (`title_page_author_pt`) e em `doc.core_properties.author` do DOCX final — é o autor **realmente publicado** |

Para um livro Dark Romance deste catálogo, `metadata.author` é preenchido com
`Bea Halden` no `BOOK_SPEC.yaml` do próprio pacote — o mesmo lugar e o mesmo
mecanismo já usados por `Pedro Arte` nos seis livros existentes. Nenhum novo
campo, schema, script ou validador é necessário; `BOOK_SPEC.schema.json` já
exige `author` como string livre.

Nenhum `BOOK_SPEC.yaml` existente é Dark Romance (`genre:` de todos os seis
pacotes não menciona o gênero — Apêndice 1), portanto **nenhum arquivo de
livro precisou ser alterado agora**. Esta seção registra o padrão a ser
aplicado quando o primeiro pacote Dark Romance for criado.

### S.3 Hierarquia conceitual

```text
PEDRO_ARTE_LIVING_BOOK_ENGINE          (motor, neutro de gênero — engine/AGENTS.md, D8)
            ↓
DARK_ROMANCE_CANON_ARCHITECT           (esta SDD — como o Dark Romance funciona)
            ↓
BEA_HALDEN_AUTHORIAL_GOVERNANCE        (esta seção — quem assina e por quê)
            ↓
BEA_HALDEN_BOOK                        (BOOK_SPEC.yaml de um livro do catálogo)
```

Governança autorial fica **acima/ao redor** das cinco leis constitucionais
(seção D) como `AUTHORIAL / PORTFOLIO GOVERNANCE`, nunca como sexta lei. Não
altera LAW 01–05, nenhum invariante (H), nenhum gate (I) e nenhum slice (L).

### S.4 O que `Bea Halden` NÃO é

| Pergunta | Resposta |
|---|---|
| É personagem, narradora ou persona dentro da narrativa? | Não. É identidade autoral externa à ficção; nunca é inserida em prosa, nunca fala pelos personagens. |
| Substitui a identidade Pedro Arte? | Não. É específica do catálogo Dark Romance; outros gêneros/projetos continuam com `Pedro Arte`. |
| Obriga todos os livros a terem o mesmo estilo, voz, protagonista, MMC, heat ou tropes? | Não. `AUTHORIAL_IDENTITY ≠ STYLE_TEMPLATE` e `AUTHORIAL_IDENTITY ≠ BOOK_DNA`. Cada obra mantém `BOOK_CONSTITUTION.md`, `CREATIVE_BRIEF.md` e Book DNA próprios (padrão já usado pelos seis pacotes existentes). |
| Presume um público leitor único? | Não. `Reader Experience`, `Target Audience` e `Resonance Hypotheses` continuam contextuais por obra (`READER_VITALS.md`, T032). |
| Altera o `ADULT_SEDUCTION_GATE`? | Não. INV-06 (idade canônica ≥ 18 para participantes de sedução/erotismo/intimidade) permanece integral e independente desta decisão. |

### S.5 Síntese e princípios (candidatos a `BEA_HALDEN_AUTHORIAL_SIGNATURE`)

Registrados como **texto de identidade editorial**, não como regra de
validador — nenhum destes três textos é checado por `check_causal_ledger.py`
nem por qualquer script. Uso pretendido: `BOOK_CONSTITUTION.md` de livros do
catálogo pode citá-los; nenhum livro é obrigado a usá-los como slogan de capa
ou sinopse.

**Manifesto:**

```text
A mulher que atravessa o inferno,
encontra a fortaleza
e prefere queimá-la a se render.
```

**Princípio de agência** — compatível com, e nunca substituto de, LAW 01
(CAUSAL CHARACTER; seção D) e do modelo GT/SM/SP (E.3):

```text
AGENCY MAY BE WOUNDED, COMPROMISED, CONFLICTED OR SURRENDERED
BY CHOICE — BUT IT MUST NEVER BE FORGOTTEN BY THE NARRATIVE.
```

Interpretação: a protagonista pode errar, perder controle, desejar submissão,
ser manipulada, permanecer em relações destrutivas — o princípio não exige
vitória, independência ou invulnerabilidade. Exige apenas que o motor nunca
deixe de tratá-la como personagem causalmente completa (Ground Truth,
Self-Model, Social Persona, contradição própria — já garantido por LAW 01 e
pelo modelo de personagem existente), nunca como objeto narrativo a serviço
exclusivo do interesse romântico.

**Princípio de portfólio** (FUTURE — depende de Portfolio Governance, ainda
não implementado; ver C.2/C.3, K):

```text
BEA HALDEN MUST HAVE A SIGNATURE WITHOUT HAVING A FORMULA.
```

Quando `Authorial Self-Cannibalization Gate` existir (K, FUTURE), ele
comparará entre livros do catálogo Bea Halden: protagonistas, interesses
românticos, Ground Truth, traumas, arquétipos, dinâmica de poder, Attraction/
Sexual Tension DNA, payoffs, twists, Emotional Signature, Relationship
Archaeology, finais, tropes e worldbuilding — reaproveitando os campos já
propostos pelo ledger por livro (E.3), que tornam essa comparação futura mais
barata. Nada disso é implementado nesta decisão.

### S.6 REUSE / EXTEND / CREATE

| Item | Decisão | Justificativa |
|---|---|---|
| Campo que carrega a identidade autoral | REUSE `BOOK_SPEC.yaml → metadata.author` | já obrigatório, já lido por `build_kdp_docx.py`, já é o autor publicado de fato |
| Local da decisão de governança | EXTEND `docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md` (esta seção) | SDD já é a casa arquitetural do que é específico de Dark Romance (D8: `/engine` fica neutro); seção documental não conflita com nenhum slice em andamento |
| Ponteiro de Portfolio Governance (K, C.3) | EXTEND (renomeado de "Pedro Arte Signature" para `BEA_HALDEN_AUTHORIAL_SIGNATURE`, escopado a Dark Romance) | mission item 9; identidade Pedro Arte inalterada para outros catálogos |
| `BEA_HALDEN_*` Engine/Agent/Persona Agent/Writer Agent/Style Engine/Prompt Engine | NÃO CRIADO | proibido explicitamente pela missão; nenhuma lacuna arquitetural o exigiria — autoria é metadado, não comportamento de geração |
| Campo novo em `BOOK_SPEC.schema.json` (ex.: enum de autor, default) | NÃO CRIADO | schema não é executado por nenhum script (D2); um default aí seria documentação morta, não governança |
| `engine/genre_profiles/dark_romance/` ou config em `/engine` | NÃO CRIADO | violaria a neutralidade de gênero do motor (D8); a decisão é de catálogo, não de motor |
| Slogan/subtítulo obrigatório de capa citando o manifesto | NÃO CRIADO | mission item 4 proíbe explicitamente transformar o manifesto em regra obrigatória |
| Alteração das cinco leis constitucionais (D) | NÃO ALTERADO | mission item confirma; governança autoral é camada acima, não substituição |

### S.7 Acceptance criteria

| Pergunta | Resposta |
|---|---|
| Quem assina por padrão um Dark Romance deste catálogo? | `Bea Halden` |
| Isso altera as cinco leis constitucionais? | Não |
| Bea Halden é personagem/persona narrativa? | Não |
| Bea Halden obriga todos os livros a terem o mesmo estilo? | Não |
| Existe uma assinatura editorial? | Sim (S.5, candidata a `BEA_HALDEN_AUTHORIAL_SIGNATURE`; enforcement fica FUTURE, junto de Portfolio Governance) |

---

## Apêndice 1 — Arquivos inspecionados

**Raiz e documentação:** `AGENTS.md`, `README.md`, `CODEX_ENGINE_BOOTSTRAP_PROMPT.md`,
`Makefile`, `requirements.txt`, `.gitignore`, `docs/ARCHITECTURE.md`,
`docs/BOOK_PACKAGE_MODEL.md`, `docs/COMO_EXECUTAR_UM_LIVRO.md`,
`docs/MIGRATION_FROM_SUPER_PROMPTS.md`, `discovery-books/00-INDICE.md`,
`discovery-books/01-analise-estrutural.md` (§5, §6 e índice),
`discovery-books/03-arquiteturas-propostas.md` (§0–§4 e índice),
`discovery-books/08-plano-desenvolvimento-melhorias.md` (índice),
`discovery-books/09-discovery-profile-livro-no-motor-intent.md`.

**Motor:** `engine/AGENTS.md`, `engine/ENGINE_GRAPH.yaml`, `engine/IMPLEMENT.md`,
`engine/MODEL_TIERS.yaml`, `engine/contracts/*.schema.json` (6),
`engine/templates/EXECUTION_PROFILES.yaml`, `TEXT_QUALITY_DEFAULTS.yaml`,
`BOOK_PACKAGE_CHECKLIST.md`, `BOOK_CREATION_PROMPT_TEMPLATE.md`,
`engine/scripts/livingbook.py` (integral), `runtime_taskgraph.py`,
`run_deterministic.py`, `check_canon_continuity.py`, `build_canon_digest.py`
(+ diff não commitado), `detect_repetition.py` (cabeçalho).

**Agentes genéricos:** `canon_guardian`, `character_psychologist`,
`subtext_editor`, `reader_vitals_agent`, `originality_auditor`,
`repetition_and_cliche_reviewer`, `genre_guardian`, `anti_manipulation_guardian`,
`emotional_editor`, `emotional_repetition_auditor`, `plot_engineer`,
`scene_architect`, `narrative_architect`, `protected_scene_auditor`,
`character_continuity_reviewer`, `plot_continuity_reviewer`,
`physicality_and_body_agent`, `symbolism_architect`, `temporal_architect`,
`dialogue_director`, `lead_novelist`, `chapter_writer`, `executive_editor`,
`legal_editor_global`, `developmental_editor`.

**Pacotes de livro:** `books/a_morte_ainda_nao_nasceu/` (BOOK_SPEC, BOOK_GRAPH,
immutable_rules, protected_scenes, quality_profile, chapter_architecture
(início), capability_requirements, `agents/consent_and_care_guardian.toml`,
`agents/liminality_guardian.toml`, `validators/validate_book_dna.py`);
`books/eva-a-ultima-mulher-da-terra/` (BOOK_SPEC, BOOK_GRAPH, IR019,
`seeds/WORLD_RULES_SEED.md §8`, `validators/validate_final_manuscript.py`);
`books/adao-o-ultimo-homem-da-terra/BOOK_GRAPH.yaml`;
`books/loja-de-poderes-vivos/` (BOOK_CONSTITUTION, immutable_rules,
CREATIVE_BRIEF); gêneros de todos os `BOOK_SPEC.yaml`.

**Runtimes (somente leitura):** `runtime/a_morte_ainda_nao_nasceu/canon/CANON_REGISTRY.yaml`
e `canon/CANON_PROPOSALS/WAVE_01_CONTINUITY_PROPOSALS.md`;
`runtime/adao-o-ultimo-homem-da-terra/canon/CANON_REGISTRY.yaml`;
`runtime/eva-a-ultima-mulher-da-terra/` (`specs/CHARACTER_BIBLE.md`,
`specs/PLOT_DEPENDENCY_MAP.md`, `living_book/READER_VITALS.md`,
`living_book/MEMORY_MOTIF_MAP.md`, `briefs/chapters/CHAPTER_05_BRIEF.md`,
chaves do `CANON_REGISTRY.yaml`); listagens de `canon/` e `project_state/` de
todos os runtimes.

**Testes:** `tests/test_image_generation.py`.

**Comandos executados (somente leitura):** `livingbook.py validate-engine`
(`ENGINE VALID | generic agents: 66 | version: 1.1.0`) e `validate-book` para
`a_morte_ainda_nao_nasceu`, `motor-de-livros-vivos`, `o_jardim_dos_doze`,
`eva-a-ultima-mulher-da-terra` (todos `VALID`). `compose` **não** foi executado
(escreve em `runtime/`). A suíte de testes **não** foi executada (D10: chamada
paga).

---

## Apêndice 2 — Cenário-fixture do MVP

Seis capítulos, dois adultos (`CHR-A`, 31; `CHR-B`, 27), sem prosa, sem
conteúdo explícito. Descrição neutra de propósito: a fixture prova mecanismo,
não subgênero.

| Cap. | Evento | Causa (ids) | Mutação | Leitor | Movimento emocional |
|---|---|---|---|---|---|
| 1 | `EV-01` A recusa B em público | `GT-A-02` (A teme que B vire alvo se associada a ele); `self_attribution: SM-A-01` "não me envolvo" (`diverges_from: GT-A-02`) | `B->A trust NONE→WARY`; `attraction NONE→PROVOKED` | estabelece `RB-01` "A despreza B" (`truth: FALSE`, `MEDIUM`) | SAFETY→DANGER · MEDIUM |
| 2 | `EV-02` B provoca A verbalmente | `GT-B-01`, `EV-01` | `A->B desire LATENT→ACTIVE`, `restraint →HIGH`; abre `LP-01` (INTIMACY) | — | DISTANCE→DESIRE · MEDIUM |
| 3 | `EV-03` A mente sobre onde esteve | `GT-A-02`, `EV-01` | `B->A trust WARY→BROKEN`; alimenta `LP-01`; knowledge: B aprende que houve mentira | estabelece `RB-02` "A esconde algo vergonhoso" (`INCOMPLETE`) | TRUST→BETRAYAL · HIGH |
| 4 | `EV-04` A cuida de B ferida | `GT-A-02`, `EV-03` | `B->A vulnerability →OPEN`; alimenta `LP-01`; abre `LP-02` (VULNERABILITY) | — | DANGER→TENDERNESS · LOW |
| 5 | `EV-05` intimidade (payoff) | `EV-02`, `EV-04`; `why_now: [EV-04]` | resolve `LP-01` `TRANSFORMED` → `LP-03` (RELATIONAL: "e quando B souber?"); `intimacy →ESTABLISHED`; `consent: CONSENSUAL, FULL, NEGOTIATED` | — | RESTRAINT→DESIRE · PEAK |
| 6 | `EV-06` revelação | `EV-03`, `EV-05` | `B->A trust BROKEN→REBUILDING` (transformação, não reset); knowledge: `READER` e B aprendem `GT-A-02`; `LP-03` continua aberto | revisa `RB-01`, `RB-02`; recontextualiza `EV-01`, `EV-03` com fatos inalterados | TRUST→HOPE · HIGH |

| Prova da tese | Onde a fixture a demonstra |
|---|---|
| 1. age por causa diferente da própria interpretação | `EV-01`: `caused_by GT-A-02` × `self_attribution SM-A-01` |
| 2. interação estrutural altera relação persistentemente | deltas de `EV-01`..`EV-06`, com `from` encadeado |
| 3. payoff herda causalidade | `EV-05` ← `EV-02`, `EV-03`, `EV-04` (caps. 2–4) |
| 4. fatos verdadeiros, interpretação incorreta | `RB-01 truth: FALSE` construída só com `facts` reais |
| 5. informação posterior recontextualiza sem retcon | `EV-06` + L10 contra snapshot da wave 1 (caps. 1–3) |
| 6. contraste, não escalada | MEDIUM → MEDIUM → HIGH → **LOW** → PEAK → HIGH |
| 7. memória para continuação | `--end-state`: `LP-03` e `LP-02` abertos, relação final ≠ baseline |
