# SDD v0.1 — `LIVING_THEORY_ENGINE` (camada `POST_READ_LIFE_CYCLE`)

> **O livro termina. A investigação começa.**

| Campo | Valor |
|---|---|
| Status | E0 — proposta; nenhuma linha de código escrita |
| Data | 2026-09-15 |
| Tipo | Capability transversal do motor (neutra de gênero, autora e obra) |
| Ativação | `features.living_theory.enabled` — **OFF por padrão** |
| Golden case | `books/narciso` (Bea Halden) — **só** como cenário de aceite (seção 38) |
| SDDs irmãs | `DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md` (ledger causal), `BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md` (canon visual), `NARCISO_CANONICAL_SDD_v0.1.md` (obra) |

## Índice

1. Executive Summary · 2. Problem Statement · 3. Goals · 4. Non-Goals ·
5. Architectural Discovery · 6. Existing Components to Reuse ·
7. Proposed Architecture · 8. Domain Model · 9. Theory Graph ·
10. Duality Seeds · 11. Evidence Ledger · 12. Evidence Taxonomy ·
13. Double Evidence · 14. Reread Mutation · 15. Visual Canon Evidence ·
16. Signal/Noise · 17. Red Herrings · 18. Theory Collision ·
19. Forum Simulation · 20. Theory Validation Gates · 21. Theory Half-Life ·
22. Last Evidence Bomb · 23. Author Deniability · 24. Dual-Depth Reading ·
25. Post-Read Life Cycle · 26. Canon Integration · 27. Metrics ·
28. Agent Responsibilities · 29. Pipeline Integration · 30. Configuration ·
31. Schemas / Contracts · 32. Observability · 33. Failure Modes ·
34. Anti-Patterns · 35. Testing Strategy · 36. Migration / Backward Compatibility ·
37. E0–E4 Rollout · 38. Narciso Golden Case · 39. Acceptance Criteria ·
40. Open Questions · 41. Implementation Slices ·
Apêndice A — Arquivos inspecionados e comandos executados

---

## 1. Executive Summary

### 1.1 O que é

Uma capability do motor que torna **arquitetável e verificável** a propriedade
de uma obra continuar existindo socialmente depois da última página: poucas
perguntas profundas, interpretações incompatíveis entre si, e cada uma delas
**defensável com evidência canônica rastreável** — sem que o texto peça ao
leitor para teorizar e sem prejudicar quem só quer ler a história.

Alvo formal (seção 2.2): **ENGINEERED INTERPRETIVE CONFLICT**, nunca
ambiguidade por falta de informação.

### 1.2 A descoberta que mais moldou o desenho

**O motor já implementou cerca de 70% desta capability — mas espalhado, e o
núcleo está preso a um único livro.**

| Conceito pedido | Já existe como | Onde |
|---|---|---|
| Theory Graph + Evidence Ledger + Double Evidence | hipóteses + matriz de suporte `S/C/X/-` por evidência; leituras duplas com força | `books/narciso/seeds/INTERPRETIVE_CANON.seed.yaml` (`reflection_hypotheses`, `reflection_evidence`, `love_readings`) |
| Balance / Consensus collapse / Random | `min_support_per_evidence`, `max_support_ratio`, `min_viable_hypotheses_at_end`, `HYPOTHESIS_STARVED/UNCHALLENGED/DOMINANCE`, `ONTOLOGY_CONVERGED`, `LOVE_BALANCE_TILTED` | `books/narciso/validators/validate_narciso.py:817-1063` |
| Author Deniability | `NO_HIDDEN_ANSWER` (chaves `truth/answer/verdade` reprovadas) | idem, `:828-836`; `INTERPRETIVE_CANON_RUNBOOK.md` "Regra zero" |
| Reread Mutation (A→B) | `reread_clues` com `first_read`, `trigger`, `second_read`, `touches`, `channel: TEXT/ILLUSTRATION/OBJECT`; `REREAD_RESOLVES_AMBIGUITY` | seed + validador Narciso `:1021-1062` |
| Revelação sem retcon | Second-Read Test (L5), INV-10/INV-11 `RETCON_DISGUISED_AS_TWIST`, crenças do leitor com `left_open` | `engine/scripts/check_causal_ledger.py:705-739, 827-849, 968-1036` |
| UNKNOWN / DELIBERATE AMBIGUITY | `unknowns[].status: MUST_REMAIN_UNKNOWN` + `prohibited_inferences[]` | `runtime/a_morte_ainda_nao_nasceu/canon/CANON_REGISTRY.yaml:554-595`; Narciso `UNK-NAR-001`, `PRO-NAR-001..006` |
| Signal/Noise visual | Visual Chekhov: `PROVEN / SUPPORTED / DECORATIVE_ALLOWED / UNJUSTIFIED / CONTRADICTORY` | `engine/scripts/check_visual_canon.py:680-713` |
| Âncoras rastreáveis | `LEDGER: SCENE: TURN: CHAPTER_FIELD: CANON: DOC: RULE: TEXT:` (TEXT resolve contra manuscrito congelado) | `check_visual_canon.py:79-91, 287-398` |
| Dualidade no objeto físico | `book_dna.duality {outer_truth, hidden_truth, anchors}` | `check_visual_canon.py:1243-1293`; seed visual Narciso |
| Memória de motivo / releitura | `MEMORY_MOTIF_MAP` com estados `S/R/T/P/E`, "Re-reading controls", "Forbidden false echoes" | `T035_MEMORY_MOTIF_MAP`; `runtime/a-noiva-esquecida/living_book/MEMORY_MOTIF_MAP.md` |
| Guardião de ambiguidade | 3 guardiões quase isomórficos, um por obra | `books/{eva…,adao…,narciso}/agents/*ambiguity*|*mystery*` |
| "Melhor argumento de cada lado" | `IMPARTIALITY_GUARDIAN` | `books/eva-a-ultima-mulher-da-terra/agents/impartiality_guardian.toml` |
| Painel multiagente pós-manuscrito | `T302_CRITIC_PANEL` (spawn paralelo com rotação por perfil) | `engine/scripts/livingbook.py:459-460` |
| Extensão sem tocar o motor | `BOOK_GRAPH.yaml` → `additional_tasks`, `gate_extensions`, `custom_validators` | `livingbook.py:622-626` |

O que **não existe** é pequeno e nomeável:

1. **Um contrato genérico** do canon interpretativo. O de Narciso tem as
   hipóteses, o léxico, o modelo de consentimento e o `DSR` **codificados** no
   validador (`HYPOTHESIS_IDS`, `LOVE_BELIEF_IDS`, `CONSENT_MODEL_BY_DSR`).
2. **Leitores cegos.** Todo agente atual lê canon; nenhum mede se a evidência
   planejada é *percebida* por quem não conhece o plano.
3. **Oscilação A→B→A, destabilizadores, falsas resoluções, relações entre
   perguntas e perguntas derivadas** — nenhum validador os representa.
4. **Justiça de descoberta entre edições** (evidência que só existe na guarda
   do collector) e **fragilidade de tradução** de dupla evidência.
5. **Detecção de theory bait** (a pergunta retórica do narrador).

### 1.3 A menor arquitetura que cumpre a missão

```text
MOTOR (EXTEND/CREATE mínimo, OFF por padrão, goldens intactos)
  engine/templates/INTERPRETIVE_CANON_TEMPLATE.yaml   contrato executável (generaliza a semente de Narciso)
  engine/templates/INTERPRETIVE_CANON_RUNBOOK.md      vira runtime/canon/THEORY_AGENTS.md (padrão dos outros runbooks)
  engine/templates/FORUM_PERSONAS.yaml                posturas epistêmicas neutras de gênero (dados, não agentes)
  engine/scripts/check_interpretive_canon.py          1 validador, modos plan | realized | final | forum + consultas
  engine/scripts/compare_forum_responses.py           comparação determinística das respostas cegas
  engine/agents/forum_reader.toml                     ÚNICO agente novo (isolamento é o contrato; seção 19.3)
  livingbook.py                                        tarefas condicionais + anotações (padrão causal_ledger)
  TEXT_QUALITY_DEFAULTS.yaml                           detector `theory_bait` desligado por padrão
  EXECUTION_PROFILES.yaml                              chave `forum_panel_limit`

RUNTIME (gerado, só quando ligado)
  canon/INTERPRETIVE_CANON.yaml     dono CANON_GUARDIAN, lock CANON_WRITE (REUSE de governança)
  reviews/FORUM_SIMULATION/*.yaml   respostas cegas (nunca canon)
  reviews/FORUM_SYNTHESIS.yaml      derivado, mecânico
  reviews/THEORY_REPORT.md          observabilidade

0 gates novos · 1 agente novo · 0 dependências novas · 0 serviços
Theory Graph e Evidence Ledger são DUAS PROJEÇÕES DO MESMO ARQUIVO, não dois arquivos.
```

### 1.4 O que NÃO é

- **Não** é um "engine" no sentido de subsistema: é contrato + validador +
  uma tarefa de simulação, sobre mecanismos existentes. O nome é da capability.
- **Não** gera finais abertos. Um livro que só "ficou aberto" reprova (seção 20).
- **Não** é métrica de viralidade. Nenhum número aprova um livro (precedente
  `NARCISO_CANONICAL_SDD_v0.1.md` §27.1).
- **Não** substitui o validador de Narciso agora. A decisão registrada
  `OQ-N10` ("promover ambiguidade estruturada ao motor: não agora; reavaliar
  depois de NARCISO provar") é **respeitada**: a promoção entra por fixture
  própria (E1/E2) e Narciso só migra em E3, com execução paralela comprovando
  equivalência (Slice 9).
- **Não** muda nenhum livro existente (critério de aceite de todo slice que
  toque o motor: `tests/fixtures/golden/*.json` idênticos).

### 1.5 Recomendação em uma linha

```text
SLICE_0                 = CONCLUÍDO (2026-09-15; decisões em 40.3; baseline 544 testes OK)
READY_FOR_SLICE_1       = YES (contrato + validador em fixture, sem tocar compose)
READY_FOR_NARCISO_MIGRATION = NO até E2 verde e decisão OQ-LTE-06
```

---

## 2. Problem Statement

### 2.1 O problema

O motor já produz obras coerentes, com memória causal, pistas e releitura.
Quatro obras do repositório tiveram **ambiguidade bloqueante** (`eva`, `adao`,
`a_morte`, `narciso`), cada uma resolvida por regra imutável + guardião LLM +
(em Narciso) validador próprio. O motor não sabe dizer, para obra nenhuma:

- se a ambiguidade é **sustentada** (evidência real para cada lado) ou **pobre**
  (falta de informação);
- se leitores que **não conhecem o plano** percebem as evidências;
- se a primeira leitura funciona sem teoria nenhuma;
- se a releitura muda o significado de algo sem mudar o fato.

Cada nova obra repete o desenho à mão, e o que é repetido à mão diverge.

### 2.2 As quatro condições (formalização)

Seja `Q` uma pergunta interpretativa e `I(Q)` o conjunto de interpretações
declaradas. Seja `E` o conjunto de evidências canônicas **percebíveis** e
`sup(e, i) ∈ {S, C, X, -}`.

| Condição | Definição operacional | Veredito do motor |
|---|---|---|
| **BAD AMBIGUITY** | `∃ i ∈ I(Q)` com `|{e : sup(e,i)=S}| < min_support` **e** o texto não fecha `Q` → o leitor não sabe porque faltou informação | `RANDOM_AMBIGUITY` ou `EVIDENCE_STARVED` (seção 20) |
| **GOOD AMBIGUITY** | toda `i` viável tem suporte ≥ mínimo, e existe `e` com `S` em ≥2 interpretações incompatíveis | pré-condição de `THEORY_READY` |
| **RANDOM AMBIGUITY** | leitores divergem, mas as posições **não resolvem para âncoras** (`TEXT:` falha) ou o conjunto de posições é ilimitado | `RANDOM_AMBIGUITY` (forum) |
| **ENGINEERED INTERPRETIVE CONFLICT** | `2 ≤ |I_viável(Q)| ≤ max`, balanço dentro do limite, dupla evidência presente, e leitores cegos atentos **defendem posições incompatíveis citando o texto** | `THEORY_READY` / `THEORY_GENERATIVE` |

A diferença entre "boa" e "engenheirada" é a **delimitação**: poucas leituras
fortes, limitadas pelo canon (`prohibited_inferences`), em vez de qualquer
leitura possível.

### 2.3 Tensão central

```text
Quanto mais o motor planeja pistas, maior o risco de o texto soar planejado.
```

Por isso toda decisão desta SDD tem um contrapeso: densidade máxima de
evidência, teto de saliência, detector de theory bait, leitor casual como
gate de naturalidade e **Regra de Ouro** (seção 24) acima de qualquer métrica
de teoria.

---

## 3. Goals

| ID | Goal | Verificável por |
|---|---|---|
| G-01 | Representar perguntas, interpretações, evidências, contraevidências, relações e mutações num contrato único, neutro de gênero | template testado + fixture de gênero ≠ romance |
| G-02 | Nunca promover interpretação a fato; nunca guardar resposta para perguntas `NEVER` | `THEORY_PROMOTED_TO_FACT`, `HIDDEN_ANSWER_PRESENT` |
| G-03 | Detectar consenso, ambiguidade aleatória, trapaça autoral, theory bait e overengineering | famílias `LT-*` + forum |
| G-04 | Medir percepção real das evidências por leitores sem acesso ao plano | `FORUM_SIMULATION` + `DISCOVERY_FAIRNESS` |
| G-05 | Planejar e validar releitura A→B e A→B→A sem retcon | `mutations[]` + INV-10/INV-11 reusados |
| G-06 | Aceitar evidência visual e de objeto físico **opcionalmente** e com justiça entre edições | `VISUAL:` + `EDITION_EXCLUSIVE_EVIDENCE` |
| G-07 | Proteger a primeira leitura | `NARRATIVE_NATURALNESS` (bloqueia `THEORY_READY`) |
| G-08 | Zero impacto em livros sem a feature | goldens byte a byte |
| G-09 | Absorver Narciso sem perder nenhuma regra dele | execução paralela no Slice 9 |

## 4. Non-Goals

- Escuta social pós-publicação, scraping de fóruns, métricas de engajamento real.
- Gerar posts, vídeos ou "conteúdo para TikTok". O `T800` só **descobre**
  artefatos já aprovados (precedente `SHAREABLE_ARTIFACT_MAP`, Narciso §24).
- Otimizar divisividade como objetivo em si. Divisividade é consequência de
  profundidade, e o gate só a exige onde a obra **declarou** ambiguidade.
- Decidir respostas de nenhuma obra, incluindo Narciso.
- Substituir julgamento literário por número. Métricas são diagnóstico.
- Criar um guardião genérico de ambiguidade nesta versão (OQ-LTE-07).
- Criar JSON Schema novo em `engine/contracts/` (ver R-05: os existentes estão
  defasados e não são executados).
- Suporte a séries/sequels (a regra é o contrário: nenhuma teoria pode
  depender de sequel — seção 34).

---

## 5. Architectural Discovery

Todas as afirmações foram verificadas lendo código, templates, pacotes,
runtimes e testes nesta sessão (Apêndice A).

### 5.1 O que o motor é

| Fato | Evidência |
|---|---|
| Motor genérico + pacote de livro + runtime gerado | `AGENTS.md`, `README.md`, `engine/AGENTS.md` ("never introduce book-specific…") |
| DAG gerado a partir do `BOOK_SPEC` | `livingbook.py:209 build_standard_graph` |
| Features condicionais lidas com `.get()` do spec **original** (antes de `disable_features`) | `livingbook.py:222-236` |
| Capabilities anteriores entram sem gate novo: validador anexado a gates existentes | `livingbook.py:684-710` |
| Detecção de capability no runtime pelo próprio grafo, copiando runbook como `canon/*AGENTS.md` | `livingbook.py:799-812` |
| Anotação de tarefas existentes via `parameters` + `inputs` (sem agente novo) | `livingbook.py:398-455 annotate()` |
| Extensões por obra | `livingbook.py:622-626`; `books/narciso/BOOK_GRAPH.yaml` |
| Spawn com `template_agent` e `foreach_chapter` já existe | `livingbook.py:525` (`T503_SOUND_PROMPTS`), `:643` |
| Rotação de painel por perfil | `livingbook.py:197 rotate_pack`; `EXECUTION_PROFILES.yaml:99-107` |
| Checkpoints humanos: arquivo escrito só por pessoa | `EXECUTION_PROFILES.yaml:87-97`; `IMPLEMENT.md` "Checkpoints humanos" |
| Tarefas determinísticas por `tool` | `livingbook.py:35-55 TOOL_BY_TASK/TOOL_BY_PATTERN`; `run_deterministic.py` |
| Auditoria de cena protegida gerada por cena, com auditor da obra | `livingbook.py:461-464` (`T32NN_PROTECTED_*`) |
| Contrato real = template YAML testado, não JSON Schema | SDD irmã D2; `CAUSAL_LEDGER_TEMPLATE.yaml` cabeçalho |

### 5.2 Mapa por item da missão (seção 0)

| # | Pedido | Encontrado | Leitura para esta capability |
|---|---|---|---|
| 1 | Investigar repositório | 8 livros, 6 runtimes, 3 SDDs de capability/obra, 10 discoveries | — |
| 2 | Mecanismos semelhantes | canon interpretativo de Narciso; `unknowns`/`prohibited_inferences`; guardiões de ambiguidade | **promover**, não recriar |
| 3 | Contratos | `CAUSAL_LEDGER_TEMPLATE.yaml`, `VISUAL_NARRATIVE_CANON_TEMPLATE.yaml`, `REVIEW_FINDING.schema.json` (forma de achado), seed Narciso | novo template segue o mesmo formato |
| 4 | Agentes | 66 genéricos + agentes de obra; nenhum leitor cego | 1 CREATE justificado |
| 5 | Canon | `CANON_REGISTRY.yaml` (sem schema), ledger (L0–L10), canon visual (V0–V9) | interpretive canon abaixo de registry/ledger na precedência |
| 6 | Validators/gates | `check_causal_ledger.py`, `check_visual_canon.py`, `check_canon_continuity.py`, `detect_repetition.py`, validadores de obra | 1 validador novo, anexado a gates existentes |
| 7 | Memória | ledger `beliefs`, `knowledge_delta`, snapshots por wave; `CANON_DIGEST` | reuso integral |
| 8 | Pistas/callbacks/motifs/rereading | `T035` S/R/T/P/E; `reread_clues`; `TEXT_RELATION_VALUES = {COMPLEMENT, CONTRADICT, FORESHADOW}` e `CALLBACK_*` (`check_visual_canon.py:2559-2648`); `eva/seeds/WORLD_RULES_SEED.md §8` | `mutations[]` generaliza `reread_clues` |
| 9 | Briefs / plot map / world bible | `T1NN_BRIEF_CHAPTER`, `T016_PLOT_DEPENDENCY_MAP`, `T014`, `chapter_architecture.yaml` | anotações condicionais |
| 10 | Registro/ativação de capability | `features.<nome>.enabled` + compose condicional + runbook + validação em `validate_book_data` (`livingbook.py:111-167`) | mesmo padrão; `known_capabilities` só para capacidades de host |

### 5.3 Precedentes que já antecipam a capability

| Precedente | O que prova |
|---|---|
| `validate_narciso.py` UNC-01..05 | balanço e viabilidade são **contáveis** |
| `LOVE_READINGS` (`strength` por lado, `LOV-02` diferença ≤1) | dupla evidência binária com força já foi modelada |
| `REREAD_RESOLVES_AMBIGUITY` (BLOCKER) | mutação não pode fechar pergunta `NEVER` |
| `GT-NAR-01` kind `CONTRADICTION`, `reader_access: NEVER` (Narciso §10.3) | **padrão de ouro**: o motor pode conhecer causalidade sem conhecer a resposta — "amor e narcisismo são o mesmo movimento". Vira regra genérica (seção 23.3) |
| `eva IR019` "hipótese só como inferência do leitor" | theory bait proibido por regra |
| `a_morte PRO-*` | limites da interpretação são canon |
| `IMPARTIALITY_GUARDIAN` | balanço tem resíduo de julgamento |
| `ANTI_MANIPULATION_GUARDIAN` ("Veta manipulação emocional ou narrativa barata") | dono natural de `THEORY_BAIT` e `CHEAP_MISDIRECTION` |
| `COMMERCIAL_EDITOR_CRITIC` ("boca a boca sem sacrificar literatura") | dono natural do julgamento de ciclo pós-leitura |

### 5.4 Incompatibilidades e riscos encontrados (registrados, não corrigidos)

| ID | Achado | Evidência | Decisão nesta SDD |
|---|---|---|---|
| R-01 | Capabilities e Narciso **não versionados** | `git status`: `?? books/narciso/`, `?? engine/scripts/check_visual_canon.py`, `?? engine/scripts/check_causal_ledger.py`, `?? tests/test_*`, `M engine/scripts/livingbook.py` | pré-condição de todo slice de motor: commit + goldens estáveis |
| R-02 | ~~Suíte offline com 1 erro pré-existente~~ **Resolvido no Slice 0: era ambiente, não código** | Sem `PYTHONIOENCODING`: `Ran 471 tests … FAILED (errors=1)` em `test_narciso_book.TestNarcisoVisualRuntime.test_engine_cli_state` (subprocesso com saída acentuada no console Windows). Com `PYTHONIOENCODING=utf-8` e `unittest discover -s tests`: **`Ran 544 tests … OK`** (2026-09-15) | toda execução da suíte no Windows usa `PYTHONIOENCODING=utf-8`; baseline oficial = 544 OK |
| R-03 | **INV-11 é incompatível com ambiguidade permanente**: revisão de crença exige divulgar GT | `check_causal_ledger.py:705-739`; Narciso D-N5 | perguntas `NEVER` nunca usam `beliefs.revises`; usam `left_open: true` + `truth: "INCOMPLETE"`. `mutations[]` de perguntas `NEVER` não geram revisão no ledger |
| R-04 | Ledger tem campo `truth` (visão do motor) — colide conceitualmente com `NO_HIDDEN_ANSWER` | `CAUSAL_LEDGER_TEMPLATE.yaml:99-113` | varredura de chaves proibidas vale **só** para o canon interpretativo; crença ligada a pergunta `NEVER` é obrigatoriamente `INCOMPLETE` + `left_open` (`LEDGER_BELIEF_CLOSES_NEVER_QUESTION`) |
| R-05 | JSON Schemas defasados: `CANON_PROPOSAL`, `CHAPTER_SCORECARD`, `REVIEW_FINDING` limitam capítulo a 30; há livros com 33, 34, 40 e 42 capítulos | `engine/contracts/*.json`; `grep chapter_count books/*/BOOK_SPEC.yaml` | nenhum schema novo; achados seguem a **forma** de `REVIEW_FINDING` sem o limite |
| R-06 | Ordem do pipeline: imagens só depois de `GATE_FULL_MANUSCRIPT` | `livingbook.py:508-523`; Narciso D-N13 | forum de texto não vê ilustrações; passada visual é opcional e tardia (seção 15.6) |
| R-07 | Isolamento de leitor cego é **só por instrução**: subagentes de Codex/Claude conseguem ler o repositório | `CODEX_ENGINE_BOOTSTRAP_PROMPT.md` (spawn com inputs declarados) | canário de contaminação determinístico (19.7); dano limitado por `NO_HIDDEN_ANSWER` |
| R-08 | Leitores simulados do mesmo modelo tendem a convergir (viés de homogeneidade) e não são humanos | natureza do método | forum nunca é BLOCKER sozinho; checkpoint humano em `GATE_FULL_MANUSCRIPT` (já existe em STANDARD/PREMIUM) |
| R-09 | Geradores de imagem são pouco confiáveis para **contagens e assimetrias** (5 vs 6 botões) | `MODEL_TIERS.yaml:71-78` (regeneração textual falhou para identidade) | evidência visual declarada = observada via `IMAGE_CONTINUITY_QA`; regra de renderização: volta a `PLANNED`, nunca muda o significado |
| R-10 | Evidência que só existe em edição collector | `EDITION_CAPABILITIES.yaml`: `PRINTED_ENDPAPER: UNSUPPORTED` em KDP; Narciso `RR-12` usa `OBJECT:ENDPAPER_FRONT` | `EDITION_EXCLUSIVE_EVIDENCE` (seção 15.4) |
| R-11 | Dupla evidência pode colapsar na tradução (ambiguidade pronominal) | Narciso `RFX-04` "para que ele não o visse"; `features.translation_preparation` ligado em vários livros | campo `language_dependent` + anotação de `T5xx` de tradução |
| R-12 | `check_visual_canon.py` tem 3.222 linhas e importa Pillow no topo; `resolve_anchor` mora nele | `check_visual_canon.py:60-63, 287` | E1: importar e copiar o script para o runtime quando a feature liga; extração só se virar dor (OQ-LTE-05) |
| R-13 | `detect_repetition.py` roda para todo livro | `IMPLEMENT.md` "pré-filtros" | detector `theory_bait` nasce `enabled: false` |
| R-14 | Manuscrito inteiro por leitor cego é caro e pode exceder contexto de alguns modelos; digest de canon **não** serve (vaza plano) | `IMPLEMENT.md` "Digest de canon"; manuscrito real de Eva: 80.954 palavras | nova `known_capability: long_context_reading`; ausência vira `CAPABILITY_BLOCKER`, nunca leitura por resumo |
| R-15 | `GENRE_GUARDIAN` lê configuração que nenhum `BOOK_SPEC` declara | SDD irmã D6 | nenhuma regra desta capability depende dele |
| R-16 | Três guardiões de ambiguidade quase idênticos já existem por obra | seção 5.3 | sinal de abstração futura, não motivo para criar agora (OQ-LTE-07) |

---

## 6. Existing Components to Reuse

### 6.1 Matriz REUSE / EXTEND / CREATE

| Necessidade | Decisão | Componente | Justificativa |
|---|---|---|---|
| Governança de canon | **REUSE** | `CANON_GUARDIAN`, lock `CANON_WRITE`, `CANON_PROPOSAL_PROTOCOL`, `mutation_log` | idêntico a registry e ledger |
| Fatos, eventos, causa | **REUSE** | `CANON_REGISTRY.yaml`, `CAUSAL_LEDGER.yaml` | teoria cita, nunca cria |
| Crença do leitor | **REUSE** | ledger `beliefs` (`left_open`, `confidence`, `expectation`) | já é o modelo FACT→INTERPRETATION→BELIEF |
| Revelação justa | **REUSE** | INV-10, INV-11, L5 `--recontextualized` | para perguntas com resposta |
| Incógnita e limite | **REUSE** | `unknowns[]`, `prohibited_inferences[]` no registry | Narciso e a_morte já usam |
| Âncoras | **REUSE** | `check_visual_canon.resolve_anchor` | 8 tipos, `TEXT:` contra manuscrito congelado |
| Âncora visual | **EXTEND** | `resolve_anchor` + tipo `VISUAL:<element|composition>` | só resolve com `visual_narrative` ligado |
| Chekhov visual como sinal/ruído | **REUSE** | `chekhov_status` | `DECORATIVE_ALLOWED` = ruído legítimo |
| Acessibilidade e tamanho mínimo | **REUSE** | `elements[].accessibility.monochrome_safe`, `min_render_size_mm` | evidência visual precisa sobreviver a e-ink e impressão |
| Disponibilidade por edição | **REUSE** | `resolve_edition_plan`, `cost_class` | justiça entre edições |
| Contrato interpretativo | **EXTEND (promoção)** | seed Narciso → `INTERPRETIVE_CANON_TEMPLATE.yaml` | generaliza ids codificados |
| Regras de balanço/viabilidade | **EXTEND (promoção)** | `validate_narciso.check_interpretive` → `check_interpretive_canon.py` | mesmas regras, parametrizadas |
| Snapshots por wave | **REUSE** | padrão `T021`/`T2NNZ` + `--snapshot-as` | imutabilidade de linhas `REALIZED` |
| Painel de leitura | **REUSE** | spawn `PARALLEL_SUBAGENTS` + `template_agent` + `rotate_pack` | forum é spawn, não orquestrador novo |
| Leitor cego | **CREATE** | `engine/agents/forum_reader.toml` | todo agente existente é instruído a ler "active book package" — isolamento é o contrato (19.3) |
| Personas | **CREATE (dados)** | `engine/templates/FORUM_PERSONAS.yaml` | persona é parâmetro, não agente |
| Comparação de respostas | **CREATE** | `compare_forum_responses.py` | mecânico; `tool` no grafo |
| Theory bait lexical | **EXTEND** | `detect_repetition.py` + `TEXT_QUALITY_DEFAULTS.yaml` (`theory_bait`) + override `book/text_quality.yaml` | mesmo mecanismo dos clichês |
| Julgamento de bait/misdirection | **REUSE** | `ANTI_MANIPULATION_GUARDIAN` | escopo declarado já cobre |
| Julgamento de dupla leitura na página | **REUSE** | `SUBTEXT_EDITOR` | "o que a cena diz sem dizer" |
| Naturalidade/overengineering | **REUSE** | `LITERARY_CRITIC`, `DEVELOPMENTAL_EDITOR` em `T302` | já leem o manuscrito inteiro |
| Síntese e decisão | **REUSE** | `EXECUTIVE_EDITOR` em `T303` | árbitro de conflito |
| Cenas de ambiguidade | **REUSE** | `protected_scenes.yaml` (`must_preserve`, `reject_if`) | veredito de cena |
| Métricas de julgamento | **REUSE** | `quality_profile.yaml` `chapter_scores`/`risk_scores` | Narciso já tem `rereadability`, `*_ambiguity` |
| Aprovação humana | **REUSE** | `requires_human_approval` | nenhum checkpoint novo |
| Perfil de custo | **EXTEND** | `EXECUTION_PROFILES.yaml` → `forum_panel_limit` | torneira existente |
| Capacidade de host | **EXTEND** | `ENGINE_GRAPH.yaml known_capabilities` → `long_context_reading` | falhar no bootstrap, não no fim |
| Gates | **REUSE** | `GATE_CANON`, `GATE_WAVE_n`, `GATE_FULL_MANUSCRIPT`, `GATE_VISUAL`, `GATE_MEDIA_ASSETS` | 0 gates novos |

### 6.2 O que foi considerado e rejeitado

| Alternativa | Por que não |
|---|---|
| Arquivos separados `THEORY_GRAPH.yaml` + `EVIDENCE_LEDGER.yaml` | a mesma linha de evidência é aresta do grafo e entrada do ledger; dois arquivos = dessincronia garantida |
| Colocar teorias dentro de `CAUSAL_LEDGER.yaml` | ledger é verdade temporal (`facts`, `caused_by`); teoria não é verdade. Misturar quebraria INV-01 e permitiria teoria virar causa |
| Colocar evidências dentro de `VISUAL_NARRATIVE_CANON.yaml` | obra sem ilustração não teria onde registrar; visual deve ser canal opcional |
| Um agente por persona (10 agentes) | persona é postura de leitura; 10 perfis TOML iguais com uma frase diferente é burocracia |
| Gate `GATE_THEORY` novo | nenhum ponto do DAG exige parada adicional; validadores anexados cobrem |
| Generalizar reusando `validate_narciso.py` como biblioteca | validador de obra contém consentimento, `DSR`, gêmeo: não pode virar dependência do motor (`engine/AGENTS.md`) |
| Pontuação "Theory Score" composta | otimização cega; contradiz o precedente de métricas-como-diagnóstico |

---

## 7. Proposed Architecture

### 7.1 Camadas

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ POST_READ_LIFE_CYCLE  (camada conceitual — seção 25; não é código)       │
├──────────────────────────────────────────────────────────────────────────┤
│ LIVING_THEORY_ENGINE (capability)                                        │
│                                                                          │
│  PLANEJAMENTO           REALIZAÇÃO              VERIFICAÇÃO               │
│  T013/T015/T016 propõem  briefs citam EVD-*     check_interpretive_canon  │
│  T018 consolida canon    writers propõem         (plan/realized/final)    │
│  T019 revisa             TEXT: anchors           T302T forum cego         │
│  T022T snapshot PLAN     T2NN_CANON_UPDATE       T302U comparação         │
│                          T2NNT snapshot wave     T303 síntese + humano    │
├──────────────────────────────────────────────────────────────────────────┤
│ CANON (autoridade; inalterado por esta capability)                       │
│  immutable_rules > CONSTITUTION > CANON_REGISTRY / CAUSAL_LEDGER          │
│    > INTERPRETIVE_CANON (cita; nunca cria) > VISUAL_NARRATIVE_CANON       │
└──────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Três fontes de verdade sobre "teoria", nunca misturadas

| Natureza | Pergunta que responde | Artefato | Quem decide |
|---|---|---|---|
| **Estrutural** (plano) | a evidência *planejada* sustenta as leituras? | `canon/INTERPRETIVE_CANON.yaml` + validador | script (bloqueia) |
| **Empírica** (percepção) | leitores que não conhecem o plano *percebem* e *divergem*? | `reviews/FORUM_SIMULATION/`, `FORUM_SYNTHESIS.yaml` | script compara; `EXECUTIVE_EDITOR` julga; nunca bloqueia sozinho |
| **Julgamento** (página) | a prosa realmente sustenta as duas leituras e continua sendo romance? | relatórios de `SUBTEXT_EDITOR`, `ANTI_MANIPULATION_GUARDIAN`, críticos, guardiões da obra | agentes + checkpoint humano |

Princípio herdado e estendido:

```text
THE ENGINE KNOWS CAUSALITY.  THE READER RECEIVES EVIDENCE.
THE ENGINE KNOWS THE QUESTIONS.  THE ENGINE NEVER KNOWS THE ANSWER TO A NEVER-QUESTION.
THE PLAN PROPOSES EVIDENCE.  ONLY BLIND READERS PROVE IT IS PERCEIVED.
```

### 7.3 Leis constitucionais da capability

| Lei | Enunciado | Verificação estrutural | Resíduo |
|---|---|---|---|
| **LT-LAW-01 FIRST READ FIRST** | A primeira leitura funciona sem nenhuma teoria | densidade máxima, `PUZZLE_CHAPTER`, `LEVEL_1_CLOSURE` | `CASUAL_READER`, `LITERARY_CRITIC`, humano |
| **LT-LAW-02 EVIDENCE OR NOTHING** | Toda interpretação viável aponta evidência canônica rastreável | suporte mínimo, âncoras resolvem | forum: posições citam `TEXT:` |
| **LT-LAW-03 NO HIDDEN ANSWER** | Pergunta `NEVER` não tem resposta em nenhum artefato | chaves proibidas, crenças `INCOMPLETE`, GT de contradição | guardião da obra |
| **LT-LAW-04 THEORY IS NOT FACT** | Interpretação nunca vira fato, causa ou canon | `THEORY_AS_CAUSE`, `THEORY_PROMOTED_TO_FACT` | `CANON_GUARDIAN` |
| **LT-LAW-05 DISCOVERED, NOT ASKED** | O leitor encontra a pista; o texto não pede teoria | teto de saliência, léxico `theory_bait` | `ANTI_MANIPULATION_GUARDIAN`, forum |

Regra de autoridade (vence a esquerda):

```text
IMMUTABLE_RULES / CANON          > THEORY_PLAN
NARRATIVE_NATURALNESS            > THEORY_DENSITY
CHARACTER_CAUSALITY              > CLUE_PLACEMENT
FAIR_DISCOVERY                   > SURPRISE
TEXT_AS_PUBLISHED                > AUTHOR_INTENT
EMERGENT_READER_THEORY           > PLANNED_THEORY  (para diagnóstico; nunca para canon)
```

---

## 8. Domain Model

### 8.1 Entidades

| Entidade | Id | Papel | Armazenada? |
|---|---|---|---|
| `Question` (Duality Seed) | `Q-*` | pergunta interpretativa de alta profundidade | sim |
| `Interpretation` | `Q-*/A` | tese concorrente dentro de uma pergunta | sim |
| `Partition` (pergunta derivada) | `Q-*~NAME` | visão binária sobre interpretações de uma pergunta plural | sim (declaração); balanço projetado |
| `Relation` | — | aresta entre interpretações de perguntas distintas | sim |
| `Evidence` | `EVD-*` | observável ancorado + suporte por interpretação | sim |
| `Mutation` | `MUT-*` | arco de significado de uma evidência ao longo da leitura | sim |
| `FalseResolution` | `FR-*` | momento em que uma leitura parece vencer | sim |
| `Destabilizer` | `DST-*` | evidência que enfraquece a leitura aparentemente vencedora | sim |
| `NarratorReliability` | `NRL-*` | escopo de não confiabilidade de uma voz | sim |
| `DoubleEvidence` | — | evidência com `S` em ≥2 interpretações incompatíveis | **projeção** |
| `Leader(Q, chapter)` | — | interpretação dominante acumulada até o capítulo | **projeção** |
| `CollisionCandidate` | — | par de interpretações compatíveis com evidência compartilhada | **projeção** |
| `ForumResponse` | `FRM-<persona>` | leitura cega | fora do canon |
| `EmergentTheory` | `EMT-*` | tese de leitor não mapeada às declaradas | fora do canon |

### 8.2 Princípio de armazenamento

Mesmo princípio do ledger e do canon visual: **guarda-se o mínimo declarado;
tudo que é derivável é projetado** (dupla evidência, líder, colisões,
densidade, mutação oscilante, classificação final). Um campo "isto é dupla
evidência" escrito à mão seria uma segunda verdade que diverge.

### 8.3 Estados de linha

`PLANNED` → `REALIZED` (só `CANON_GUARDIAN`, depois que a prosa ou a arte
existe) → imutável contra snapshot (`INTERPRETIVE_RETCON`). `RETIRED` para
evidência cortada antes do congelamento (nunca depois de `REALIZED` sem
`mutation_log`). Mesmo vocabulário do ledger e do canon visual.

---

## 9. Theory Graph

### 9.1 Forma

O Theory Graph **não é um arquivo**. É a projeção de `questions`,
`interpretations`, `partitions`, `relations` e `evidence` do canon
interpretativo:

```text
Nós:     Q-* (pergunta) ─contém─▶ Q-*/X (interpretação)
         EVD-* (evidência)
Arestas: EVD ─S|C|X─▶ interpretação          (suporte)
         interpretação ─IMPLIES|TENSIONS|EXCLUDES|AMPLIFIES─▶ interpretação  (relations)
         Q-*~P ─agrupa─▶ {interpretações}     (partitions)
         MUT ─muda leitura de─▶ EVD           (mutations)
         DST ─enfraquece─▶ Leader              (destabilizers)
```

```text
                    Q-01  "X amou?"
                 ┌──────┴──────┐
              Q-01/A        Q-01/B
             (amou)      (nunca amou)
               ▲  ▲          ▲  ▲
            S  │  └── S ─ EVD-07 ─ S ──┘  │  S      ◀── DOUBLE EVIDENCE (projetada)
               │                          │
            EVD-03                     EVD-11
               │ C                        │ C        ◀── contraevidência
               ▼                          ▼
              Q-01/B                    Q-01/A
```

### 9.2 Vocabulário de relações

| `kind` | Semântica | Uso |
|---|---|---|
| `IMPLIES` | aceitar `a` torna `b` mais provável | teorias dependentes |
| `TENSIONS` | `a` e `b` são compatíveis, mas se incomodam | combustível de discussão |
| `EXCLUDES` | `a` e `b` não podem ser verdadeiras juntas | limita colisões |
| `AMPLIFIES` | `a` + `b` produzem uma leitura mais forte que cada uma | candidato explícito de colisão |

Interpretações da **mesma** pergunta são `EXCLUDES` implícito (definição de
pergunta) — declarar isso é erro (`RELATION_REDUNDANT`, LOW).

### 9.3 Regras estruturais

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `TG-01` | toda relação referencia interpretações existentes de perguntas distintas | `RELATION_UNRESOLVED` | HIGH |
| `TG-02` | ciclo de `IMPLIES` com `EXCLUDES` no mesmo par | `RELATION_CONTRADICTORY` | HIGH |
| `TG-03` | interpretação sem nenhuma evidência | `INTERPRETATION_WITHOUT_EVIDENCE` | HIGH |
| `TG-04` | evidência sem nenhum `S` | `EVIDENCE_WITHOUT_SUPPORT` | MEDIUM (é textura mal registrada: deve sair do canon) |
| `TG-05` | pergunta `NEVER` com `EXCLUDES` externo que elimina todas menos uma interpretação | `GRAPH_FORCES_RESOLUTION` | BLOCKER |

O grafo é deliberadamente **raso**: sem pesos numéricos nas arestas, sem
inferência probabilística. Profundidade vem das perguntas, não do grafo.

---

## 10. Duality Seeds

### 10.1 Definição

Uma **Duality Seed** é uma `Question` com `resolution_policy: NEVER` ou
`LATE_PARTIAL`, `half_life ≥ MEDIUM` e ≥2 interpretações incompatíveis, capaz
de gerar perguntas derivadas por **partição**.

### 10.2 Forma: binária ou plural

| `shape` | Exemplo abstrato | Regra de viabilidade final |
|---|---|---|
| `BINARY` | "Ele amou?" SIM ↔ NÃO | as duas viáveis (nenhum `X` acumulado que elimine) |
| `PLURAL` | "O que olha de volta?" 3–6 hipóteses | `≥ min_viable_at_end` (padrão 3) sem `X` |

### 10.3 Partições — poucas sementes, muitas perguntas

Uma pergunta plural gera perguntas binárias **sem nova evidência**:

```yaml
partitions:
  - id: Q-02~SUPERNATURAL
    of: Q-02
    question: "Existe algo sobrenatural?"
    sides: {YES: [Q-02/SUPER, Q-02/GAZE], NO: [Q-02/PROJ, Q-02/SELF, Q-02/OTHER]}
```

Uma interpretação pode ficar **fora** das duas faces (`unassigned`) — é aí
que leitores brigam por classificação, o que é teoria derivada legítima
(seção 38.4 mostra isso com dados reais).

### 10.4 Seleção e limites

| Regra | Padrão | Por quê |
|---|---|---|
| `max_duality_seeds` | 3 | "poucas perguntas de alta profundidade"; acima disso o leitor dispersa |
| `min_high_half_life_seeds` | 1 | ao menos uma pergunta sobrevive ao conhecimento dos fatos |
| `max_partitions_per_seed` | 4 | partição a mais é taxonomia, não pergunta |
| `max_never_questions` | 3 | o livro também precisa responder coisas (seção 24.3) |
| semente precisa de `unknown_ref` se `NEVER` | obrigatório | "o motor sabe que não sabe" vive no registry |
| semente `NEVER` precisa de ≥1 `prohibited_inferences` | recomendado (MEDIUM) | ambiguidade engenheirada é **delimitada** |

Critérios de seleção (julgamento, `T016` + `T019`), em ordem:

1. **Enraizada no personagem/tema** — a pergunta decorre de GT de personagem
   maior ou da tese da `BOOK_CONSTITUTION`, não de um mistério acoplado.
2. **Sobrevive aos fatos** — reler sabendo todos os eventos não fecha a pergunta.
3. **Custo moral ou emocional** — cada resposta muda como o leitor julga alguém.
4. **Evidência cotidiana** — pode ser sustentada por gesto, ausência, tempo,
   objeto, sem artifício.
5. **Não depende de informação ausente** — se a única razão da dúvida é o
   autor esconder algo, é BAD AMBIGUITY.

### 10.5 Distribuição

`DS-DIST-01` (MEDIUM): para cada semente, cada movimento/ato declarado em
`BOOK_SPEC.movements` contém ≥1 evidência. `DS-DIST-02` (MEDIUM): nenhum
trecho de `max_seed_silence` capítulos (padrão 6, mesmo número de
`max_loop_silence` do ledger) sem evidência de uma semente `HIGH`.

---

## 11. Evidence Ledger

### 11.1 O que é

A lista `evidence[]` do canon interpretativo. Cada linha responde, de forma
verificável: **onde está, o que o leitor pode perceber, quem diz, e o que
isso sustenta ou complica**. Nunca: o que é verdade.

### 11.2 Linha mínima

```yaml
- id: EVD-07
  status: PLANNED
  anchor: "TURN:13"             # REALIZED exige também text_anchor: "TEXT:13:\"...\""
  channel: BEHAVIOR             # seção 12
  source: NARRATOR              # NARRATOR | CHR-* | DOCUMENT | ILLUSTRATION | OBJECT
  observable: "ele guarda e ouve à noite as gravações dela"   # percepção, nunca ontologia
  salience: SUPPORTING          # TEXTURE | SUPPORTING | NOTICEABLE (teto de bait)
  discoverable_on: FIRST_READ   # FIRST_READ | REREAD
  support: {Q-01/A: S, Q-01/B: S}
  readings:                     # obrigatório para cada S quando a linha é dupla evidência
    Q-01/A: {reading: "saudade da voz dela", strength: STRONG}
    Q-01/B: {reading: "a voz dela repete as falas dele", strength: STRONG}
  language_dependent: false
  ledger_event: EV-LOVE-E2      # opcional; obrigatório se causal_ledger ligado e o gesto é estrutural
```

### 11.3 Valores de suporte

`S` sustenta · `C` complica sem excluir · `X` exclui · `-` neutro.
Herdado sem mudança da semente de Narciso. `X` em pergunta `NEVER` exige
`approval` humano (precedente Narciso §9.3).

### 11.4 Regras do ledger

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `EL-01` | `anchor` resolve (`resolve_anchor`); em `realized/final`, `text_anchor` resolve contra manuscrito congelado | `EVIDENCE_ANCHOR_UNRESOLVED` | HIGH |
| `EL-02` | `support` cobre todas as interpretações da(s) pergunta(s) tocada(s) com enum válido | `INVALID_ENUM` | HIGH |
| `EL-03` | `observable` sem léxico de ontologia/motivo da obra (`book/planning/LEXICONS.yaml` quando existir) | `OBSERVABLE_STATES_ANSWER` | HIGH |
| `EL-04` | interpretação viável tem `≥ min_support` (padrão 3) linhas `S` e ≥1 `C` | `EVIDENCE_STARVED` / `INTERPRETATION_UNCHALLENGED` | MEDIUM |
| `EL-05` | em pergunta `NEVER`, nenhuma linha com `X` em ≥ N−1 interpretações | `EVIDENCE_COLLAPSES_QUESTION` | BLOCKER |
| `EL-06` | `max(S)/min(S)` entre interpretações viáveis ≤ `max_support_ratio` (padrão 2.0) | `INTERPRETATION_DOMINANCE` | MEDIUM |
| `EL-07` | linha `REALIZED` idêntica ao snapshot em `anchor`, `observable`, `support` | `INTERPRETIVE_RETCON` | HIGH |
| `EL-08` | `source: CHR-*` com `S` em interpretação que depende da confiabilidade dessa voz → linha de `NarratorReliability` ou `C` de outra fonte | `TESTIMONY_UNQUALIFIED` | MEDIUM |
| `EL-09` | ids únicos; `ledger_event` resolve quando declarado | `EVIDENCE_DUPLICATE` / `UNKNOWN_REFERENCE` | HIGH |

`EL-04..06` são as regras `UNC-03..05` e `LOV-01..02` de Narciso,
parametrizadas.

---

## 12. Evidence Taxonomy

### 12.1 Canais (`channel`)

| Canal | Exemplos | Nota |
|---|---|---|
| `DIALOGUE` | frase dita, pronome ambíguo, resposta evasiva | `language_dependent` frequente |
| `BEHAVIOR` | gesto, evitar olhar, pagar em segredo | canal mais natural; preferido |
| `ABSENCE` | quem não aparece, o que não é dito, objeto que falta | exige âncora do que *deveria* estar lá |
| `TIMING` | atraso, ordem de eventos, simultaneidade | cruza com `TIMELINE.md` |
| `MEMORY` | versões divergentes de lembrança | cruza com ledger `self_model` |
| `VERSION_DELTA` | documento/relato que muda entre ocorrências | `C` em uma leitura é quase obrigatório |
| `ENVIRONMENT` | clima, luz, som, objeto de cena | limite de densidade mais estrito |
| `OBJECT` | objeto narrativo dentro da história | cruza com `SYMBOL_BIBLE` |
| `DOCUMENT` | carta, laudo, diário, foto dentro da ficção | nunca pode "resolver" (léxico) |
| `PERCEPTION_CONFLICT` | dois personagens percebem diferente | ledger `interpretations[]` |
| `ILLUSTRATION` | detalhe em prancha | exige `visual_narrative` (seção 15) |
| `PHYSICAL_BOOK` | capa, guarda, borda, paginação | exige `visual_narrative`; justiça por edição |
| `PARATEXT` | epígrafe, título de capítulo, sumário | `paratext_policy` pode proibir |

### 12.2 Papéis (`role`) — declarados só quando não são projetáveis

| `role` | Declarado? | Regra |
|---|---|---|
| `CLUE` | padrão implícito | — |
| `DOUBLE_EVIDENCE` | **nunca** (projetado) | seção 13 |
| `RED_HERRING` | sim, com bloco `fair_herring` | seção 17 |
| `DESTABILIZER` | via `destabilizers[]` | seção 22 |
| `TEXTURE` | **não entra no canon** | detalhe estético não é linha de evidência |

### 12.3 Taxonomia de estados epistêmicos (onde cada um vive)

Resposta direta à seção 22 da missão — detalhada em 26.1:
`CANONICAL FACT` (registry/ledger `facts`) · `PERCEPTION` (ledger
`interpretations`, `evidence_to_reader`; `observable` aqui) · `BELIEF`
(ledger `self_model`/`beliefs`) · `RUMOR` (evidência `source: CHR-*` +
`NarratorReliability`) · `INTERPRETATION`/`THEORY` (este canon) · `UNKNOWN`
(registry `unknowns`) · `DELIBERATE AMBIGUITY` (`resolution_policy: NEVER` +
`unknown_ref` + `prohibited_inferences`).

---

## 13. Double Evidence

### 13.1 Definição formal

```text
DOUBLE(e, Q) ⇔ ∃ a,b ∈ I(Q), a≠b : sup(e,a)=S ∧ sup(e,b)=S
               ∧ readings[a].strength ≥ MEDIUM ∧ readings[b].strength ≥ MEDIUM
Para partições: DOUBLE(e, Q~P) ⇔ S em ≥1 interpretação de cada face.
```

Nunca declarada; sempre projetada (`--double Q-01`).

### 13.2 Por que exigir `readings`

Marcar `S` em duas colunas é barato. Escrever **como** cada grupo defende a
conclusão com essa evidência é o teste mínimo de honestidade: se a leitura
não cabe numa frase concreta, o `S` é desejo do planejador.

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `DE-01` | linha projetada como dupla tem `readings` para cada `S` | `DOUBLE_EVIDENCE_WITHOUT_READING` | HIGH |
| `DE-02` | as duas leituras ≥ `MEDIUM` | `DOUBLE_EVIDENCE_WEAK_SIDE` | HIGH |
| `DE-03` | diferença de `STRONG` só-de-um-lado por pergunta ≤ 1 (LOV-02 generalizado) | `DOUBLE_EVIDENCE_TILTED` | MEDIUM |
| `DE-04` | cada leitura se apoia em **outro** elemento do texto: `readings[x].corroborated_by` cita ≥1 `EVD-*` distinto | `READING_UNCORROBORATED` | MEDIUM |
| `DE-05` | pergunta `NEVER` tem ≥ `min_double_evidence` (padrão 3) linhas duplas | `DOUBLE_EVIDENCE_SCARCE` | MEDIUM |
| `DE-06` | ≤ `max_double_share_per_chapter` (padrão: nenhum capítulo com mais de 2 duplas) | `DOUBLE_EVIDENCE_CLUSTERED` | LOW |

`DE-04` responde ao pedido "ambos precisam conseguir argumentar usando outros
elementos do texto": dupla evidência isolada é charada; dupla evidência
corroborada é argumento.

### 13.3 Como planejar sem charada

Diretriz de brief (`T1NN`), não regra: a cena é escrita para a **causa do
personagem** (ledger GT), e a dupla evidência é **consequência** de uma GT
de contradição (seção 23.3), não um enigma inserido. O brief recebe o
`observable` e as duas `readings` como *restrições* ("a cena não pode fechar
nenhuma das duas"), nunca como "plante esta pista". Teste de julgamento:
`SUBTEXT_EDITOR` lê a cena **sem** o bloco `readings` e declara as leituras
que encontra; divergência vira achado de wave.

---

## 14. Reread Mutation

### 14.1 Modelo

```yaml
mutations:
  - id: MUT-03
    evidence: EVD-07
    arc:
      - {phase: FIRST_READ, favors: [Q-01/A], reading: "saudade"}
      - {phase: AFTER, trigger: "TURN:21", favors: [Q-01/B], reading: "a voz dela dizia as falas dele"}
      - {phase: AFTER, trigger: "VISUAL:IL-22", favors: [Q-01/A], reading: "ele apagou só as falas dele das fitas"}
    ledger_belief: null          # só para perguntas com resposta: RB-* revisada (reusa INV-11/L5)
```

Projeções: `kind = SHIFT (A→B) | OSCILLATING (A→B→A…) | DEEPENING (A→A+)`.

### 14.2 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `RM-01` | capítulos de `trigger` estritamente crescentes e posteriores à evidência | `MUTATION_TRIGGER_NOT_LATER` | HIGH |
| `RM-02` | cada fase muda `favors` em relação à anterior (senão é repetição) | `MUTATION_WITHOUT_CHANGE` | MEDIUM |
| `RM-03` | pergunta `NEVER`: a última fase não pode deixar só uma interpretação viável nem conter léxico de resposta | `REREAD_RESOLVES_AMBIGUITY` | BLOCKER |
| `RM-04` | a evidência mutada é `REALIZED` e inalterada contra snapshot quando o gatilho é realizado — **o fato não muda; o leitor muda** | `INTERPRETIVE_RETCON` (reusa L10) | HIGH |
| `RM-05` | pergunta com resposta: `ledger_belief` presente e o evento gatilho a revisa (INV-11 reusado) | `MUTATION_WITHOUT_LEDGER_ANCHOR` | HIGH |
| `RM-06` | ≥ `min_mutations_per_movement` (padrão 1) e ≥1 `OSCILLATING` quando `reread_depth: DEEP` | `REREAD_LAYER_THIN` | MEDIUM |
| `RM-07` | gatilho não é o mesmo capítulo para > `max_triggers_per_chapter` (padrão 3) mutações | `REVELATION_DUMP` | LOW |

### 14.3 A→B→A sem trapaça

A oscilação só é justa se a terceira fase **adiciona** evidência (novo
gatilho ancorado), nunca se reinterpreta o mesmo gatilho. O validador exige
triggers distintos (`RM-01`). O julgamento (`REREADER` no forum) confirma se a
volta a A é *sentida* como descoberta e não como indecisão.

### 14.4 Relação com o que existe

`reread_clues` de Narciso → `mutations[]` com duas fases (mapeamento em 36.3).
`MEMORY_MOTIF_MAP` (`S/R/T/P/E`) continua sendo o mapa de motivos; quando um
motivo corresponde a uma mutação, cita `MUT-*` (mesmo padrão com que já cita
`RB-*` — `livingbook.py:430-433`).

## 15. Visual Canon Evidence

### 15.1 Princípio

Evidência visual é **opcional** e **nunca mais forte que o texto sozinho**
para sustentar uma interpretação viável. Ela multiplica releitura; não é
condição de entendimento.

### 15.2 Ativação

`features.living_theory.visual_evidence: true` exige
`features.visual_narrative.enabled: true` (`validate_book_data`). Sem isso,
canais `ILLUSTRATION`/`PHYSICAL_BOOK` e âncoras `VISUAL:` são rejeitados
(`VISUAL_EVIDENCE_DISABLED`, HIGH).

### 15.3 Âncora `VISUAL:` (EXTEND de `resolve_anchor`)

`VISUAL:<id>` resolve contra `canon/VISUAL_NARRATIVE_CANON.yaml`:
`elements[].id` (`SYM-/SIG-/ART-/FIG-`) ou `compositions[].id` (`COMP-*`,
pranchas `IL-*` do sistema de ilustração). Retorna `chapter` via
`_composition_chapter` (existente, `check_visual_canon.py:2565`) e força
`STRUCTURAL`. Nenhum outro tipo de âncora muda.

### 15.4 Regras

| id | Regra | Reuso | Achado | Sev. |
|---|---|---|---|---|
| `VE-01` | elemento citado tem Chekhov `PROVEN` ou `SUPPORTED` | `chekhov_status` | `VISUAL_EVIDENCE_UNJUSTIFIED` | HIGH |
| `VE-02` | `accessibility.monochrome_safe: true` quando algum alvo tem interior não colorido | `EDITION_CAPABILITIES INTERIOR_COLOR` | `VISUAL_EVIDENCE_COLOR_DEPENDENT` | HIGH |
| `VE-03` | detalhe de evidência declara `detail_min_size_mm` ≥ `min_render_size_mm` | `accessibility` | `VISUAL_EVIDENCE_TOO_SMALL` | MEDIUM |
| `VE-04` | **justiça entre edições**: interpretação viável não pode ter linha `S` indispensável que só existe em superfície/efeito `COLLECTOR_ONLY` ou `UNSUPPORTED` em algum alvo de `edition_targets`. Evidência exclusiva só é permitida como **redundância** (existe outra `S` equivalente disponível em todos os alvos) | `resolve_edition_plan`, `cost_class` | `EDITION_EXCLUSIVE_EVIDENCE` | HIGH |
| `VE-05` | `exposure.spoiler_level` do elemento ≤ teto da superfície pública; nenhuma evidência de mutação em superfície pública | `check_spoiler_safety` | `REREAD_CLUE_EXPOSED` | MEDIUM |
| `VE-06` | em modo `assets`, anomalia declarada = anomalia observada (contagem, lado, ausência) registrada por `IMAGE_CONTINUITY_QA` | `IMAGE_APPROVAL` + relatório de QA | `VISUAL_EVIDENCE_NOT_REALIZED` | HIGH |
| `VE-07` | evidência visual não pode ser a **única** `S` de uma interpretação viável | — | `VISUAL_ONLY_INTERPRETATION` | MEDIUM |

### 15.5 Regra de renderização (herdada)

Se o gerador não produz a assimetria planejada (5 botões × 6 no reflexo), a
linha volta a `PLANNED` e a interpretação perde aquele suporte — o
validador recalcula balanço. **Nunca** se reescreve `observable` para caber
no que o pixel mostrou, nem se aceita "quase seis botões". Limitação de
geração não corrompe canon (mesma regra dos runbooks de ledger e visual).

### 15.6 Forum visual

O forum principal roda em `T300` (texto). Pranchas só existem depois de
`GATE_FULL_MANUSCRIPT` (R-06). Quando `forum.visual_pass: true`, uma passada
curta `T4ZZT_VISUAL_FORUM_PASS` (depois das imagens aprovadas) entrega aos
leitores `REREADER` e `CLUE_HUNTER` manuscrito congelado + pranchas. Como o
texto já está congelado, achados só podem reprovar/refazer **imagens**. Isso
é honesto sobre o custo e o timing — e é exatamente onde nasce o "voltem ao
capítulo 7 e olhem a ilustração".

---

## 16. Signal/Noise

### 16.1 O risco

Se todo detalhe é pista, o leitor aprende a gramática do motor e a
descoberta morre. O motor precisa de **ruído legítimo**: detalhe estético,
coincidência, atmosfera — e precisa **não registrá-los como evidência**.

### 16.2 Classes

| Classe | Onde vive | Registrada no canon interpretativo? |
|---|---|---|
| Detalhe estético / atmosfera | prosa, `IMAGE_BIOME`, `DECORATIVE_ALLOWED` | não |
| Coincidência | prosa | não |
| Pista real | `evidence[]` | sim |
| Pista ambígua (dupla) | `evidence[]` (projetada) | sim |
| Red herring | `evidence[]` com `fair_herring` | sim |
| Símbolo com função não interpretativa | `SYMBOL_BIBLE`, canon visual | não (a menos que toque uma pergunta) |

### 16.3 Controles estruturais (configuráveis; valores iniciais são hipótese de calibração)

| Parâmetro | Inicial | Racional do valor inicial |
|---|---|---|
| `max_evidence_per_chapter` | 3 | Narciso planeja ≤2 por capítulo (RFX + LOVE) em 33 capítulos; 3 dá folga sem virar catálogo |
| `max_noticeable_share` | 0.25 | uma em cada quatro pistas pode ser perceptível na primeira leitura; o resto é textura ou releitura |
| `min_reread_only_share` | 0.30 | parte da camada precisa existir só para quem volta |
| `max_evidence_chapter_share` | 0.70 | pelo menos ~30% dos capítulos sem nenhuma evidência planejada: respiração |
| `max_visual_evidence_share` | 0.40 | dos elementos visuais ≥ `SUPPORTING`, no máximo 40% com função interpretativa |
| `min_decorative_visual_elements` | 2 | o leitor precisa ver ornamento que não significa nada |

Nenhum destes é universal. Seguem o precedente de `TEXT_QUALITY_DEFAULTS.yaml`
("limiares calibrados contra um manuscrito real"): começam como hipótese,
são recalibrados em E3 contra Narciso e contra a retro-auditoria (37.4), e
podem ser sobrescritos por `BOOK_SPEC.features.living_theory.thresholds`.

### 16.4 Controle empírico (o que realmente importa)

No forum, cada `CLUE_HUNTER`/`OBSESSIVE_READER` cita detalhes que acha
suspeitos. O comparador classifica cada citação como **planejada** (resolve
para `EVD-*`) ou **não planejada**.

| Métrica | Leitura | Faixa-alvo inicial |
|---|---|---|
| `planned_hit_rate` = planejadas encontradas / planejadas `FIRST_READ` | baixa → pistas invisíveis (`DISCOVERY_UNFAIR`) | ≥ 0.40 |
| `noise_share` = citações não planejadas / todas | muito baixa → o leitor só "vê" o que o motor plantou: **gramática aprendida** (`CLUE_GRAMMAR_LEGIBLE`) | 0.30–0.70 |
| `casual_clue_mentions` | leitor casual cita pistas espontaneamente com frequência → bait | ≤ 1 por pergunta |

Ruído alto é saudável: significa que o livro tem textura suficiente para que
nem tudo seja pista.

---

## 17. Red Herrings

### 17.1 Contrato

```yaml
- id: EVD-12
  role: RED_HERRING
  support: {Q-03/A: S, Q-03/B: C}
  fair_herring:
    points_toward: Q-03/A
    in_world_cause: "LEDGER:GT-LIA-02"        # por que o personagem age assim, independente do leitor
    survives_reveal: "TURN:25"                # onde a leitura posterior mantém o gesto verdadeiro
    counter_available_before: [EVD-09]        # contraevidência justa antes do desmentido
    after_function: CHARACTERIZES             # CHARACTERIZES | MUTATES (MUT-*) | THEMATIC
```

### 17.2 FAIR RED HERRING × CHEAP MISDIRECTION

| id | Critério de FAIR | Violação = CHEAP MISDIRECTION | Verificação | Sev. |
|---|---|---|---|---|
| `RH-01` | tem causa dentro do mundo (GT/SM de personagem ou regra de mundo) | existe só para enganar | âncora `in_world_cause` resolve para `LEDGER:GT-*`, `LEDGER:EV-*`, `RULE:` ou `DOC:` | HIGH |
| `RH-02` | continua verdadeiro depois da revelação | revelação exige fato diferente | reusa INV-10/L10; `survives_reveal` resolve | HIGH |
| `RH-03` | não depende de mentira do narrador confiável | narrador afirma falso sem `NarratorReliability` | `source: NARRATOR` + sem `NRL-*` cobrindo o capítulo | BLOCKER |
| `RH-04` | contraevidência disponível antes do desmentido | só dá para desconfiar depois | `counter_available_before` com capítulo < desmentido | HIGH |
| `RH-05` | tem função depois de desmentido | pista órfã | `after_function` presente; se `MUTATES`, `MUT-*` existe | MEDIUM |
| `RH-06` | não esconde o que o POV sabe sem motivo | narração em terceira próxima omite conhecimento do POV | com ledger ligado: `knowledge_state(pov, chapter)` contém a GT que desmentiria e o capítulo não declara `withholding_motive` | HIGH (`POV_WITHHOLDING`) |
| `RH-07` | proporção | livro vira armadilha | `red_herrings ≤ max_red_herring_share` (padrão 0.15 das evidências) | MEDIUM |

`RH-06` é possível porque o ledger já projeta conhecimento por conhecedor e
capítulo (`check_causal_ledger.py:1056 knowledge_state`) e
`check_canon_continuity.py` já confere mapa de POV.

---

## 18. Theory Collision

### 18.1 Definição

```text
COLLISION_CANDIDATE(a ∈ I(Qi), b ∈ I(Qj), i≠j) ⇔
     não existe relação EXCLUDES entre a e b
  ∧ |{e : sup(e,a)=S ∧ sup(e,b)=S}| ≥ min_shared_evidence   (padrão 2)
  ∧ nenhuma prohibited_inference casa com a conjunção declarada (se houver `synthesis`)
```

A terceira teoria **não precisa ser planejada**. O motor só garante que o
espaço combinatório existe e é delimitado.

### 18.2 Três níveis

| Nível | Fonte | Artefato | Canon? |
|---|---|---|---|
| declarada | autor/planejador | `relations[].kind: AMPLIFIES` com `synthesis` | sim |
| projetada | validador | `--collisions` | não (consulta) |
| emergente | forum | `FORUM_SYNTHESIS.emergent_theories[]` | **nunca** |

### 18.3 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `TC-01` | teoria emergente cujas âncoras citadas resolvem e não contradizem registry/ledger conta para `THEORY_GENERATIVE` | classificação | INFO |
| `TC-02` | teoria emergente que casa com `prohibited_inferences` = o texto **vaza** uma inferência proibida | `PROHIBITED_INFERENCE_EMERGED` | HIGH |
| `TC-03` | colisão declarada `AMPLIFIES` sem ≥ `min_shared_evidence` | `COLLISION_UNSUPPORTED` | MEDIUM |
| `TC-04` | número de candidatos projetados = 0 com ≥2 sementes | `SEEDS_ISOLATED` (as perguntas não conversam) | LOW |

`TC-02` é a regra mais valiosa desta seção: `prohibited_inferences` deixa de
ser lista passiva e vira detector.

### 18.4 Depois do congelamento

Teoria emergente nunca muda manuscrito congelado nem canon. Antes do
congelamento, `EXECUTIVE_EDITOR` pode transformá-la em proposta
(`CANON_PROPOSALS`) de nova interpretação — só se ela **já** é sustentada
pelo texto; nunca se exigir texto novo para caber.

---

## 19. Forum Simulation

### 19.1 Objetivo

Medir o que nenhum validador mede: **percepção e divergência de leitores que
não conhecem o plano**. É instrumento de diagnóstico sujeito a viés de
modelo (R-08); nunca aprova nem reprova sozinho.

### 19.2 Onde entra

```text
T300_ASSEMBLE_FULL_MANUSCRIPT
   ├─▶ T302_CRITIC_PANEL (existente)
   ├─▶ T302T_FORUM_SIMULATION      spawn template_agent FORUM_READER × personas (rotate_pack)
   │      └─▶ T302U_FORUM_COMPARISON   tool: compare_forum_responses.py (determinístico)
   └─▶ T303_REVIEW_SYNTHESIS (existente) — recebe FORUM_SYNTHESIS.yaml como input
```

Roda sobre o manuscrito **montado** (antes de `T304`) para que achados ainda
possam virar revisão. Uma passada só; confirmação pós-congelamento é
OQ-LTE-02.

### 19.3 Por que um agente novo (o único CREATE de agente)

Todo `developer_instructions` genérico do motor diz "Read the active task,
declared inputs, **active book package** and scoped AGENTS.md"
(`engine/agents/*.toml`). O pacote contém `CREATIVE_BRIEF`, `BOOK_CONSTITUTION`,
`immutable_rules` — o plano. Reusar `LITERARY_CRITIC` como leitor cego
exigiria contradizer a instrução do próprio perfil. O isolamento é o
contrato; por isso existe `FORUM_READER`:

```toml
name = "FORUM_READER"
description = "Leitor cego: lê só o manuscrito entregue, sem canon, pacote, briefs ou relatórios."
model_tier = "M"
developer_instructions = """
Read ONLY the files listed in the task's `inputs` (a manuscript copy and the persona card).
Never open book/, canon/, specs/, briefs/, reviews/, living_book/ or any AGENTS.md.
Read as the persona describes. Answer the two phases in the declared YAML contract.
Every claim cites a literal quote (≤ 25 words) and chapter number. Do not invent quotes.
If you did not notice something on first reading, say so; do not search for clues unless
your persona is REREADER or CLUE_HUNTER.
"""
```

### 19.4 Personas

**Posturas do motor** (neutras de gênero) em `engine/templates/FORUM_PERSONAS.yaml`:

| Persona | Postura | Modo |
|---|---|---|
| `CASUAL_READER` | lê pela história; não procura pistas | FIRST_READ |
| `OBSESSIVE_READER` | atenção total, anota tudo | FIRST_READ |
| `SKEPTIC` | exige prova; desconfia de leituras sobrenaturais e românticas igualmente | FIRST_READ |
| `CLUE_HUNTER` | procura inconsistências e detalhes | FIRST_READ |
| `CONTRARIAN` | defende a leitura menos óbvia | FIRST_READ |
| `REREADER` | lê tudo, depois relê capítulos que escolher | REREAD |
| `LITERARY_CRITIC` | forma, tema, se o livro "trapaceia" | FIRST_READ |

**Personas da obra** (simpatias; gênero vive no pacote) em
`BOOK_SPEC.features.living_theory.forum.book_personas`: ex. `ROMANTIC_READER`,
`SUPERNATURALIST`, `PSYCHOLOGICAL_READER`, cada uma com `sympathizes_with`
(interpretações). Isso mantém `ROMANTIC` e `SUPERNATURALIST` fora do motor.

Personas de simpatia **não contam** para consenso/divisividade (sua posição
é o viés declarado). O que se mede nelas: citam a contraevidência mais forte
do outro lado como "detalhe que incomoda"? Se não citam, a contraevidência
não é percebida.

### 19.5 Protocolo em duas fases

| Fase | O leitor recebe | Responde | Por quê |
|---|---|---|---|
| **1 — aberta** | manuscrito + cartão da persona | que perguntas ficaram; o que acredita; evidências; o que incomoda; que cena releria; que pergunta postaria; que detalhe fotografaria/citaria; a história funcionou sem teoria? | captura teorias emergentes e perguntas não planejadas sem contaminar |
| **2 — mapeada** | texto **neutro** das `questions` e a lista **embaralhada por persona** de teses + "nenhuma" | posição mais próxima por pergunta, confiança, 3 citações, contraevidência reconhecida | permite comparação determinística |

A fase 2 só é entregue depois de a fase 1 estar persistida (dois spawns ou
arquivo da fase 1 como pré-condição da fase 2).

### 19.6 Contrato de resposta

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: ForumResponse
persona: SKEPTIC
reading_mode: FIRST_READ
phase_1:
  open_questions: ["..."]
  beliefs:
    - statement: "..."
      confidence: MEDIUM
      evidence: [{chapter: 13, quote: "..."}]
      troubling_detail: {chapter: 26, quote: "..."}
      alternative_considered: "..."
  reread_targets: [{chapter: 8, why: "..."}]
  forum_post_title: "..."
  share_detail: {chapter: 17, quote: "...", illustration: null}
  naturalness:
    story_worked_without_theory: true
    felt_like_puzzle: 2          # 0-10
    felt_asked_to_theorize: false
    note: "..."
phase_2:
  - question: Q-01
    position: Q-01/B               # ou NONE
    confidence: HIGH
    evidence: [{chapter: 13, quote: "..."}, {chapter: 21, quote: "..."}, {chapter: 31, quote: "..."}]
    counter_acknowledged: [{chapter: 16, quote: "..."}]
```

### 19.7 Comparação determinística (`compare_forum_responses.py`)

1. Resolve toda `quote` como `TEXT:<chapter>:"<quote>"` contra o manuscrito
   entregue (reusa `resolve_anchor`). Citação que não resolve =
   `FORUM_QUOTE_FABRICATED` (descartada da contagem; persona com >30%
   fabricado é invalidada).
2. Casa citações resolvidas com `EVD-*` por sobreposição de trecho com
   `text_anchor` (planejada × não planejada, 16.4).
3. **Canário de contaminação**: similaridade de shingles (mesmo algoritmo de
   `detect_repetition.detect_near_duplicates`) entre texto da fase 1 e
   `thesis`/`readings` do canon. Acima do limiar = `FORUM_CONTAMINATION`
   (resposta descartada; tarefa refeita).
4. Projeta: posições por pergunta (sem personas de simpatia), entropia
   normalizada, `planned_hit_rate`, `noise_share`, evidências por
   interpretação defendidas, teorias emergentes (fase 1 não mapeável a
   nenhuma tese, com ≥2 citações resolvidas), casamento com
   `prohibited_inferences` (léxico declarado em `PRO-*.match` quando existir;
   senão `EXECUTIVE_EDITOR` classifica).
5. Escreve `reviews/FORUM_SYNTHESIS.yaml` e classificação (seção 20).

### 19.8 Custo e capacidade

Cada leitor recebe o manuscrito inteiro (R-14). Ordem de grandeza: um
manuscrito de ~80 mil palavras ocupa por volta de 110–130 mil tokens de
entrada por leitor; `REREADER` paga releitura parcial. `forum_panel_limit`
controla o painel; o custo real vai para `logs/COST_LEDGER.md` como qualquer
tarefa. Sem contexto suficiente no host: `CAPABILITY_BLOCKER`
(`long_context_reading`), **nunca** leitura por resumo ou digest.

---

## 20. Theory Validation Gates

### 20.1 Nenhum gate novo

| Gate existente | Validador anexado | Modo |
|---|---|---|
| `GATE_CANON` | `V_THEORY_PLAN` | `plan` |
| `GATE_WAVE_n` | `V_THEORY_WAVE_n` | `realized --through-chapter N --baseline WAVE_{n-1}` |
| `GATE_FULL_MANUSCRIPT` | `V_THEORY_FINAL` | `final --baseline WAVE_last --forum reviews/FORUM_SYNTHESIS.yaml` |
| `GATE_VISUAL` (se existe) | `V_THEORY_VISUAL` | `assets` |
| `GATE_MEDIA_ASSETS` | `V_THEORY_PARATEXT` | `paratext` (descrição, Stories) |

### 20.2 Classificação final

| Veredito | Detecção estrutural | Detecção empírica (forum) | Julgamento | Bloqueia? |
|---|---|---|---|---|
| **FAILURE — CONSENSUS COLLAPSE** | `EL-05`, `EL-06`, `TG-05`, viáveis < mínimo | ≥ `consensus_threshold` (padrão 0.8) das posturas neutras na mesma tese com confiança `HIGH` | `SUBTEXT_EDITOR`, guardião da obra | estrutural: sim · forum: HIGH para `T303` |
| **FAILURE — RANDOM AMBIGUITY** | `EVIDENCE_STARVED`, `INTERPRETATION_WITHOUT_EVIDENCE` | posições divergem, mas <50% das citações resolvem ou cada posição tem <2 citações | `DEVELOPMENTAL_EDITOR` | estrutural: sim · forum: HIGH |
| **FAILURE — AUTHORIAL CHEATING** | `RH-03`, `RH-06`, `EDITION_EXCLUSIVE_EVIDENCE`, interpretação cujas `S` são todas `REREAD` e nenhuma `FIRST_READ`, GT `reader_access: NEVER` usada como evidência | interpretação planejada `STRONG` não defendida nem percebida por nenhuma persona, inclusive `REREADER` e `CLUE_HUNTER` | `ANTI_MANIPULATION_GUARDIAN` | sim (estrutural) |
| **FAILURE — THEORY BAIT** | detector `theory_bait` (prosa e paratexto), `max_noticeable_share` | `felt_asked_to_theorize: true` em `CASUAL_READER` ou `LITERARY_CRITIC`; `casual_clue_mentions` alto | `ANTI_MANIPULATION_GUARDIAN` | lexical: pré-filtro · forum: HIGH |
| **FAILURE — OVERENGINEERING** | densidade (16.3), `PUZZLE_CHAPTER`, `DOUBLE_EVIDENCE_CLUSTERED` | `felt_like_puzzle ≥ 6` em casual ou crítico; `story_worked_without_theory: false` | `LITERARY_CRITIC`, humano | **naturalidade é HIGH e impede THEORY_READY** |
| **SUCCESS — THEORY READY** | nenhum HIGH/BLOCKER estrutural | cada tese viável defendida por ≥1 persona neutra com ≥3 citações resolvidas; divisividade ≥ limiar; naturalidade passa | `EXECUTIVE_EDITOR` | — |
| **EXCEPTIONAL — THEORY GENERATIVE** | — | ≥1 teoria emergente (`TC-01`) sem `TC-02` | `EXECUTIVE_EDITOR` | — (classificação) |

### 20.3 Severidade e perfis

- Achado estrutural HIGH/BLOCKER bloqueia em qualquer perfil onde o gate bloqueia.
- Achado **só** empírico nunca passa de HIGH e vai para `T303`; o
  `GATE_FULL_MANUSCRIPT` já exige aprovação humana em STANDARD e PREMIUM
  (`EXECUTION_PROFILES.yaml:87-97`).
- `NARRATIVE_NATURALNESS` é a única métrica empírica que impede a
  classificação `THEORY_READY` mesmo com estrutura perfeita (Regra de Ouro).
- Perguntas `LATE_PARTIAL`/`RESOLVED_AT` não exigem divergência final —
  exigem justiça (L5/INV-11) e divergência **antes** da revelação.

---

## 21. Theory Half-Life

### 21.1 Classes

| Classe | Natureza da pergunta | Por que decai/dura | Exemplo abstrato |
|---|---|---|---|
| `LOW` | `FACTUAL` | um fato encontrado encerra | "Quem pegou a chave?" |
| `MEDIUM` | `TEXTUAL`/`EPISTEMIC` | exige investigação, mas a investigação tende a convergir | "O narrador mentiu no capítulo 9?" |
| `HIGH` | `PSYCHOLOGICAL`, `MORAL`, `ONTOLOGICAL`, `RELATIONAL` | continua discutível **com todos os fatos conhecidos** | "Ele amou?", "O final é libertação?" |

### 21.2 Contrato

`questions[].axis` + `half_life` + `half_life_rationale` (obrigatória, uma
frase sobre por que a pergunta sobrevive aos fatos).

### 21.3 Regras e medição honesta

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `HL-01` | `axis: FACTUAL` não pode declarar `HIGH` | `HALF_LIFE_INFLATED` | MEDIUM |
| `HL-02` | ≥ `min_high_half_life_seeds` perguntas `HIGH` | `NO_DURABLE_QUESTION` | MEDIUM |
| `HL-03` | pergunta `FACTUAL` + `NEVER` é suspeita de BAD AMBIGUITY (esconder um fato) | `FACT_WITHHELD_AS_MYSTERY` | HIGH — exceto quando `unknown_ref` aponta regra imutável da obra (precedente eva `IR002`) |

Meia-vida real só existe depois de publicado. Antes, o motor tem dois
**proxies**: (1) na fase 2, `REREADER` responde se a pergunta continua
aberta *depois* de reler sabendo tudo; (2) a pergunta aparece na fase 1 de
personas diferentes sem estímulo. O relatório chama isso de
`half_life_estimate`, nunca de meia-vida.

---

## 22. Last Evidence Bomb

### 22.1 Definição operacional

```text
Leader(Q, c) = interpretação com maior soma ponderada de S (WEAK=1, MEDIUM=2, STRONG=3; S sem strength=2)
               em linhas REALIZED com capítulo ≤ c. Empate = sem líder.
LAST_EVIDENCE_BOMB(d) ⇔ d ∈ destabilizers[], kind: LAST_EVIDENCE_BOMB
  ∧ capítulo(d) ≥ último movimento
  ∧ ∃ Leader(Q, capítulo(d) − 1)
  ∧ sup(d, Leader) ∈ {C}                    (enfraquece, não exclui)
  ∧ ∃ outra i viável com sup(d, i) = S
  ∧ não resolve Q (sem X que deixe < mínimo viável)
```

### 22.2 Uma ferramenta, não uma fórmula

- Declaração **opcional**. Nenhum livro é reprovado por não ter bomba.
- `max_last_evidence_bombs` = 1 por pergunta (duas bombas viram tique).
- Se declarada e não satisfaz 22.1 → `LEB_DOES_NOT_DESTABILIZE` (MEDIUM).
- Quando não há líder (empate), a evidência final equilibrada é
  classificada `OPEN_FINAL_EVIDENCE` — legítima, **mas não é bomba**. A
  seção 38.5 mostra que é exatamente o caso de Narciso hoje.

### 22.3 Falsa resolução

```yaml
false_resolutions:
  - {id: FR-01, question: Q-01, apparent_winner: Q-01/A, established_at: "TURN:18", broken_by: DST-02}
```

`FR-01` exige que `Leader(Q, established_at)` seja de fato `apparent_winner`
(`FALSE_RESOLUTION_NOT_PROJECTED`, MEDIUM) e que o destabilizador venha
depois. Isso transforma "o leitor achou que tinha entendido" em algo
verificável contra o próprio ledger.

## 23. Author Deniability

### 23.1 Enunciado

> O texto publicado é a autoridade canônica. O autor pode ter uma leitura; ela
> não tem autoridade superior ao que está no livro, e nenhuma ambiguidade da
> obra depende de entrevista, nota, glossário, sequel ou post.

### 23.2 Regras

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `AD-01` | `policy.no_hidden_answer: true` obrigatório | `HIDDEN_ANSWER_PRESENT` | BLOCKER |
| `AD-02` | nenhuma chave `truth`, `answer`, `correct`, `canonical_answer`, `author_answer`, `resposta`, `verdade`, `intended` em qualquer nível do canon interpretativo, briefs de capítulo gerados com a feature ou `FORUM_PERSONAS` | `HIDDEN_ANSWER_PRESENT` | BLOCKER |
| `AD-03` | crença do ledger ligada a pergunta `NEVER` tem `truth: "INCOMPLETE"` e `left_open: true`; nunca aparece em `beliefs.revises` | `LEDGER_BELIEF_CLOSES_NEVER_QUESTION` | BLOCKER |
| `AD-04` | GT citada por evidência de pergunta `NEVER` tem `reader_access: NEVER` e `kind: CONTRADICTION` (ou não contém léxico de uma única tese) | `GROUND_TRUTH_HOLDS_ANSWER` | HIGH |
| `AD-05` | `paratext_policy: NO_INTERPRETIVE_PARATEXT` (padrão quando a feature liga): sem epílogo explicativo, nota do autor interpretativa, glossário de símbolos | `INTERPRETIVE_PARATEXT` | HIGH |
| `AD-06` | nenhuma pergunta depende de volume futuro: `resolution_policy` não aceita `SEQUEL` | `SEQUEL_DEPENDENCY` | HIGH |
| `AD-07` | descrição KDP, Stories e textos de mídia sem léxico `theory_bait` nem teses | `THEORY_BAIT_IN_PARATEXT` | MEDIUM |

### 23.3 Padrão "verdade que preserva ambiguidade"

Achado do repositório (Narciso §10.3): o motor precisa de causa para o
personagem agir (LAW 01 do ledger), mas não pode ter resposta. A solução é
uma GT `CONTRADICTION` cujo enunciado descreve a **inseparabilidade** das
leituras ("amor e narcisismo são o mesmo movimento nele"), com
`reader_access: NEVER`. Esta SDD promove isso a padrão genérico
(`AMBIGUITY_PRESERVING_GROUND_TRUTH`) e o torna verificável por `AD-04`.

### 23.4 Checkpoint humano

No `GATE_FULL_MANUSCRIPT`, o arquivo `APPROVALS/GATE_FULL_MANUSCRIPT.md`
(escrito por pessoa) passa a ter uma pergunta a mais quando a feature está
ligada: *"Consigo defender publicamente minha leitura de cada pergunta `NEVER`
sem fechá-la?"* O motor não escreve nem avalia essa resposta.

---

## 24. Dual-Depth Reading

### 24.1 Níveis mapeados a artefatos existentes

| Nível | Experiência | Quem garante | Artefato |
|---|---|---|---|
| **L1 — Narrativa completa** | história, personagens, emoção, conflito, payoff, estética | motor inteiro, como hoje | `chapter_architecture` (`dramatic_question`, `irreversible_turn`), `protected_scenes`, `READER_VITALS`, ledger `loops` |
| **L2 — Investigação** | pistas percebíveis | esta capability | `evidence[]` `discoverable_on: FIRST_READ` |
| **L3 — Conexões sistêmicas** | teorias que conversam | esta capability | `relations`, `partitions`, colisões |
| **L4 — Releitura transformada** | significado muda | esta capability + ledger | `mutations[]`, L5 |

### 24.2 Regra de Ouro (constitucional)

> **O LIVING_THEORY_ENGINE nunca pode prejudicar leitores que só querem ler a
> história.** L2–L4 são opcionais para o leitor e obrigatoriamente
> subordinados a L1.

### 24.3 Regras estruturais

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `DD-01` | `function`, `dramatic_question` e `irreversible_turn` de nenhum capítulo citam ids `Q-*`/`EVD-*`/`MUT-*` — capítulo existe pela história | `PUZZLE_CHAPTER` | HIGH |
| `DD-02` | com ledger ligado: ≥1 loop `RELATIONAL`/`PLOT` resolvido (`CLOSED` ou `TRANSFORMED`) no último movimento | `LEVEL_1_CLOSURE_MISSING` | HIGH |
| `DD-03` | perguntas `NEVER` ≤ `max_never_questions` | `TOO_MANY_OPEN_QUESTIONS` | MEDIUM |
| `DD-04` | toda cena protegida com `auditor` de ambiguidade tem `must_preserve` que mencione efeito emocional ou dramático, não só a ambiguidade | `SCENE_PROTECTS_ONLY_THEORY` | LOW |

### 24.4 Métrica empírica central

`NARRATIVE_NATURALNESS` (27): `CASUAL_READER` e `LITERARY_CRITIC` precisam
declarar `story_worked_without_theory: true` e `felt_like_puzzle ≤ 5`, e as
notas de `quality_profile` já existentes (`scene_strength`,
`emotional_impact`, `authenticity_of_characters`) precisam estar no mínimo da
obra. Falha = sem `THEORY_READY`.

---

## 25. Post-Read Life Cycle

### 25.1 Camada conceitual — o que o motor pode e não pode fazer

```text
BOOK ─▶ INTERPRETATION ─▶ THEORY ─▶ COUNTER-THEORY ─▶ DISCUSSION ─▶ REREAD
  ▲                                                                    │
  │                                                                    ▼
NEW INTERPRETATIONS ◀─ NEW READERS ◀─ SOCIAL CONTENT ◀─ NEW THEORY ◀─ DISCOVERY
```

| Estágio | O motor produz a pré-condição via | O motor mede antes de publicar via | Fora do motor |
|---|---|---|---|
| BOOK | pipeline inteiro | gates existentes | — |
| INTERPRETATION | `evidence[]` `FIRST_READ` | forum fase 1 | — |
| THEORY | `questions[]` | forum `open_questions` | — |
| COUNTER-THEORY | `C` + dupla evidência | `counter_acknowledged` | — |
| DISCUSSION | balanço | divisividade | fóruns reais |
| REREAD | `mutations[]` | `REREADER`, `reread_targets` | — |
| DISCOVERY | `REREAD`-only evidence, visual | `planned_hit_rate`, visual pass | — |
| NEW THEORY | `relations`, colisões | teorias emergentes | — |
| SOCIAL CONTENT | `SHAREABLE_ARTIFACT_MAP` (composições **já** aprovadas) | `share_detail` do forum | produção de conteúdo |
| NEW READERS | pacote de mídia **sem** expor pistas | `REREAD_CLUE_EXPOSED`, `AD-07` | marketing |
| NEW INTERPRETATIONS | — | — | vida real da obra |

### 25.2 Princípio

O motor **maximiza pré-condições**, nunca o ciclo em si. Nenhum elemento
entra no livro por ser compartilhável (precedente VP-01 do canon visual). O
`share_detail` do forum serve para **descobrir** o que leitores já querem
citar e alimentar `T800` — nunca para plantar frase de efeito.

### 25.3 Futuro (fora desta versão)

Registrar teorias de leitores reais como `observed_theories` de uma edição
publicada, sem alterar canon, para informar nova edição ilustrada ou
tradução. Exige decisão humana e não entra antes de E4.

---

## 26. Canon Integration

### 26.1 Estados epistêmicos

| Estado | Definição | Onde vive | Pode virar fato? | Pode ser `caused_by`? |
|---|---|---|---|---|
| `CANONICAL_FACT` | o que ocorre no mundo | registry, ledger `events.facts` | — | sim (via `EV-*`) |
| `PERCEPTION` | o que alguém percebe | ledger `interpretations[]`, `evidence_to_reader`; `evidence.observable` | não | não |
| `BELIEF` (personagem) | o que alguém acredita | ledger `self_model`, `interpretations` | não | via `SM-*` só como atribuição, nunca causa |
| `BELIEF` (leitor) | o que o leitor passa a crer | ledger `beliefs[]` | revisável por GT (INV-11) | não |
| `RUMOR` | afirmação de personagem de confiabilidade limitada | `evidence.source: CHR-*` + `narrators[]` | não | não |
| `INTERPRETATION` | tese sobre uma pergunta | `questions[].interpretations[]` | **nunca** | **nunca** |
| `THEORY` | interpretação + relações/colisões | projeção do canon interpretativo | **nunca** | **nunca** |
| `UNKNOWN` | o motor sabe que não sabe | registry `unknowns[]` | só se status permitir revelação planejada | não |
| `DELIBERATE_AMBIGUITY` | desconhecido + delimitado + protegido | `resolution_policy: NEVER` + `unknown_ref` + `prohibited_inferences` | **nunca** | não |

Mentira de personagem = `facts` diz o que ocorre; a mentira é `source:
CHR-*` numa evidência. Nunca altera `facts`. Interpretação de leitor
(forum ou real) nunca toca canon.

### 26.2 Precedência

```text
immutable_rules > BOOK_CONSTITUTION > CANON_REGISTRY / CAUSAL_LEDGER
  > INTERPRETIVE_CANON (cita; nunca cria)
  > VISUAL_NARRATIVE_CANON (cita ambos; VP-05)
  > bíblias > briefs > prosa / pixels
Forum e relatórios: fora da hierarquia (diagnóstico).
```

### 26.3 Regras de fronteira

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `CI-01` | nenhum `caused_by` do ledger contém `Q-*`, `EVD-*`, `MUT-*` | `THEORY_AS_CAUSE` | BLOCKER |
| `CI-02` | `thesis` de interpretação não aparece (shingles ≥ limiar) em `facts` do ledger ou `fact` do registry | `THEORY_PROMOTED_TO_FACT` | BLOCKER |
| `CI-03` | evidência que exige fato inexistente não é aceita: âncora não resolve → proposta em `CANON_PROPOSALS` | `EVIDENCE_CREATES_FACT` | HIGH |
| `CI-04` | `unknown_ref` resolve para `unknowns[]` do registry com status coerente com `resolution_policy` | `UNKNOWN_REF_INVALID` | HIGH |
| `CI-05` | interpretação que casa com `prohibited_inferences` não pode ser declarada | `PROHIBITED_INTERPRETATION` | BLOCKER |

### 26.4 Governança

Dono exclusivo `CANON_GUARDIAN`, lock `CANON_WRITE`. Demais agentes propõem
em `canon/CANON_PROPOSALS/`. Snapshots em `canon/snapshots/INTERPRETIVE_CANON.<PLAN|WAVE_NN>.yaml`.
Correção de linha `REALIZED` = nova entrada em `mutation_log`.

---

## 27. Metrics

### 27.1 Princípio (herdado)

> Métricas são diagnóstico. Nenhuma métrica aprova um capítulo ou o livro.
> Não existe pontuação composta de "teoria" ou "viralidade".

### 27.2 Métricas

| Métrica | Criar/estender? | Natureza | Cálculo | Onde | Risco de otimização cega |
|---|---|---|---|---|---|
| `THEORY_DENSITY` | criar | estrutural | `Σ_Q |I_viável(Q)|` e evidências/10 capítulos | `--metrics` | mais teorias ≠ melhor; limitada por `max_*` |
| `EVIDENCE_BALANCE` | promover (`UNC-05`) | estrutural | `max(S)/min(S)` ponderado por pergunta | validador | balanço artificial com `S` fraco → `DE-02` |
| `REREAD_MUTATION` | promover (`RRL-03`) | estrutural + empírica | nº de `MUT` válidas, `OSCILLATING`, por movimento; confirmações do `REREADER` | validador + forum | contar pista ≠ releitura boa |
| `VISUAL_EVIDENCE` | criar | estrutural | linhas visuais / total; `PROVEN`; disponibilidade por edição | validador | tentação de pôr pista em ornamento → `max_visual_evidence_share` |
| `THEORY_COLLISION` | criar | estrutural + empírica | candidatos projetados; emergentes | validador + forum | colisão inventada → `TC-03` |
| `FORUM_DIVISIVENESS` | criar | empírica | entropia normalizada das posições da fase 2 (posturas neutras), ponderada por confiança | comparador | só exigida em perguntas declaradas ambíguas |
| `THEORY_HALF_LIFE` | criar | declarada + proxy empírico | classe declarada; `half_life_estimate` (21.3) | validador + forum | inflar classe → `HL-01` |
| `AUTHOR_DENIABILITY` | promover (`NO_HIDDEN_ANSWER`) | estrutural + humana | `AD-*` sem achado + rubrica humana | validador + checkpoint | — |
| `DISCOVERY_FAIRNESS` | criar | empírica + estrutural | `planned_hit_rate`; fração de interpretações com ≥1 `S` `FIRST_READ` percebida; `VE-04` | comparador + validador | pistas óbvias demais → `noise_share` |
| `NARRATIVE_NATURALNESS` | criar (**crítica**) | empírica + julgamento + humana | 24.4 | forum + `quality_profile` + checkpoint | nenhuma: é o contrapeso de todas as outras |

### 27.3 `quality_profile.yaml` (opcional por obra)

Chaves de julgamento já aceitas pelo formato existente, sugeridas quando a
feature liga: `interpretive_balance`, `rereadability`, `clue_naturalness`
(`chapter_scores`) e `theory_bait`, `puzzle_feel`, `motive_declaration`
(`risk_scores`). O motor não impõe; Narciso já declara equivalentes.

---

## 28. Agent Responsibilities

| Agente | Tarefa | Responsabilidade nova (parâmetro condicional) | Tipo |
|---|---|---|---|
| `CANON_GUARDIAN` | `T018`, `T2NN_CANON_UPDATE`, snapshots | dono do canon interpretativo; promove `PLANNED→REALIZED` com `text_anchor` | REUSE |
| `PLOT_ENGINEER` | `T016` | propõe `questions`, `evidence`, `false_resolutions`, `destabilizers`, `red_herrings` | REUSE |
| `CHARACTER_PSYCHOLOGIST` | `T013` | GTs `CONTRADICTION` que preservam ambiguidade; `narrators[]`; causas de red herring | REUSE |
| `SYMBOLISM_ARCHITECT` | `T015`, `T035` | evidência por motivo; `MUT-*` no `MEMORY_MOTIF_MAP`; ruído simbólico | REUSE |
| `READER_VITALS_AGENT` | `T032` | mapa L1 (o que o leitor casual sente por capítulo); nunca canon | REUSE |
| `SCENE_ARCHITECT` | `T1NN` | cita `EVD-*` do capítulo com `observable`, teto de saliência e "não fechar nenhuma leitura" | REUSE |
| `LEAD_NOVELIST` / `CHAPTER_WRITER` | `T2NN_WRITE` | realizam; propõem `text_anchor` | REUSE |
| `SUBTEXT_EDITOR` | wave review (quando no pack) | lê cena sem `readings` e declara as leituras que encontra | REUSE |
| `ANTI_MANIPULATION_GUARDIAN` | `T019`, briefs, waves | theory bait, cheap misdirection, retenção de POV | REUSE |
| `LITERARY_CRITIC`, `DEVELOPMENTAL_EDITOR` | `T302` | naturalidade, overengineering | REUSE |
| `COMMERCIAL_EDITOR_CRITIC` | `T302` | ciclo pós-leitura sem isca | REUSE |
| `EXECUTIVE_EDITOR` | `T019`, `T303` | adjudica forum × estrutura; classifica teorias emergentes | REUSE |
| `VISUAL_DIRECTOR` | `T043` | elementos de evidência visual, acessibilidade, edições | REUSE |
| `IMAGE_CONTINUITY_QA` | `T4NN` | anomalia declarada = observada | REUSE |
| `TRANSLATION_ARCHITECT` | tradução | preserva `language_dependent` | REUSE |
| `MEDIA_AND_KDP_AGENT` | `T800–T802` | sem teses, pistas ou bait em mídia | REUSE |
| `FORUM_READER` | `T302T`, `T4ZZT` | leitura cega | **CREATE** |
| Guardiões de ambiguidade da obra | como hoje | continuam donos das regras específicas da obra | REUSE (pacote) |

---

## 29. Pipeline Integration

Tudo condicional a `living_theory_enabled`, lido do spec **original**
(padrão de `livingbook.py:222-236`).

| Fase | Mudança | Detalhe |
|---|---|---|
| BOOTSTRAP | `T001` | checa `long_context_reading` se `forum.enabled` |
| CANON | anota `T013`, `T015`, `T016`, `T018`, `T019` | inputs: template + runbook; `T018` ganha output `/canon/INTERPRETIVE_CANON.yaml` e input opcional `/book/seeds/INTERPRETIVE_CANON.seed.yaml` |
| CANON | nova `T022T_THEORY_SNAPSHOT` (`tool`) | `check_interpretive_canon.py --snapshot-as PLAN`; entra em `GATE_CANON.requires` |
| LIVING_BOOK | anota `T032`, `T035`; se visual: `T042`, `T043` | — |
| BRIEFS | anota `T1NN` | inputs: canon interpretativo; parâmetro de salience/"não fechar" |
| WAVES | anota `T2NN_WRITE`, `T2NN_CANON_UPDATE`; nova `T2NNT_THEORY_SNAPSHOT` (`tool`) | entra em `GATE_WAVE_n.requires` |
| INTEGRATION | novas `T302T_FORUM_SIMULATION`, `T302U_FORUM_COMPARISON` (`tool`); `T303` ganha input `FORUM_SYNTHESIS.yaml` | entram em `GATE_FULL_MANUSCRIPT.requires` só se `forum.enabled` |
| VISUAL | opcional `T4ZZT_VISUAL_FORUM_PASS` | só se `visual_pass` |
| TRANSLATION | anota tarefa de tradução | `language_dependent` |
| DELIVERY | anota `T800–T802` | `AD-07`, `VE-05` |
| RUNTIME | copia `check_interpretive_canon.py`, `compare_forum_responses.py`, `check_visual_canon.py` (dependência de `resolve_anchor`), template, `FORUM_PERSONAS.yaml`; runbook → `canon/THEORY_AGENTS.md` | detecção pelo grafo (`T022T` existe), mesmo padrão `livingbook.py:799-812` |
| IMPLEMENT.md | um parágrafo "se `canon/THEORY_AGENTS.md` existir…" | igual aos dois existentes |

Custo em tarefas para um livro de 6 waves com forum: `1 + 6 + 2 = 9` tarefas,
das quais 7 são `tool` (custo de modelo zero) — só `T302T` gasta modelo de
forma nova.

---

## 30. Configuration

```yaml
# books/<slug>/BOOK_SPEC.yaml
spec:
  features:
    living_theory:
      enabled: true                       # ausente = false (OFF por padrão)
      visual_evidence: false              # true exige visual_narrative.enabled
      reread_depth: STANDARD              # STANDARD | DEEP (exige OSCILLATING)
      paratext_policy: NO_INTERPRETIVE_PARATEXT
      forum:
        enabled: true
        panel: [CASUAL_READER, SKEPTIC, CLUE_HUNTER, REREADER, LITERARY_CRITIC, CONTRARIAN]
        book_personas:
          - {id: SYMPATHY_A, stance: "lê a favor da interpretação A por temperamento", sympathizes_with: [Q-01/A]}
        visual_pass: false
      thresholds:                         # todos opcionais; defaults no validador
        max_duality_seeds: 3
        max_never_questions: 3
        min_support: 3
        max_support_ratio: 2.0
        min_double_evidence: 3
        max_evidence_per_chapter: 3
        max_noticeable_share: 0.25
        consensus_threshold: 0.8
```

```yaml
# engine/templates/EXECUTION_PROFILES.yaml (EXTEND)
DRAFT:    {forum_panel_limit: 2}      # validação estrutural completa; forum mínimo
STANDARD: {forum_panel_limit: 5}
PREMIUM:  {forum_panel_limit: null}   # painel inteiro
```

```yaml
# engine/templates/TEXT_QUALITY_DEFAULTS.yaml (EXTEND)
theory_bait:
  enabled: false                      # book/text_quality.yaml liga
  severity: MEDIUM
  scope: NARRATION                    # ignora falas entre travessões/aspas
  patterns: ["mas será que", "ou teria sido", "talvez nunca saibamos", "nada era o que parecia",
             "e se tudo", "o leitor", "cabe a você decidir", "a verdade estava diante"]
```

Validações em `validate_book_data` (`livingbook.py:111`): `visual_evidence`
sem `visual_narrative` → erro; persona de obra com `sympathizes_with`
vazio → erro; `forum.enabled` e `theory_bait` desligado → aviso.

---

## 31. Schemas / Contracts

### 31.1 `engine/templates/INTERPRETIVE_CANON_TEMPLATE.yaml` (contrato executável)

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: InterpretiveCanon
metadata:
  project_id: slug-do-livro
  version: 0.1.0
  owner: CANON_GUARDIAN
  refs: {canon_registry: /canon/CANON_REGISTRY.yaml, causal_ledger: null, visual_canon: null}
policy:
  no_hidden_answer: true
  thresholds: {}                        # sobrescreve defaults; BOOK_SPEC vence
narrators:
  - {id: NRL-01, voice: CHR-A, scope: "TURN:9", unreliability: "memória seletiva", tells: [EVD-05]}
questions:
  - id: Q-01
    question: "Pergunta interpretativa neutra, sem sugerir resposta."
    axis: RELATIONAL                    # FACTUAL|TEXTUAL|EPISTEMIC|PSYCHOLOGICAL|MORAL|ONTOLOGICAL|RELATIONAL
    half_life: HIGH
    half_life_rationale: "Continua discutível com todos os eventos conhecidos."
    resolution_policy: NEVER            # NEVER | LATE_PARTIAL | RESOLVED_AT
    resolved_at: null                   # "LEDGER:EV-*" quando RESOLVED_AT
    unknown_ref: "CANON:UNK-001"
    prohibited_refs: ["CANON:PRO-001"]
    shape: BINARY                       # BINARY | PLURAL
    min_viable_at_end: 2
    interpretations:
      - {id: Q-01/A, thesis: "Tese A."}
      - {id: Q-01/B, thesis: "Tese B."}
partitions: []
relations: []
evidence:
  - id: EVD-01
    status: PLANNED
    anchor: "TURN:3"
    text_anchor: null
    channel: BEHAVIOR
    source: NARRATOR
    observable: "O que se pode perceber."
    salience: SUPPORTING
    discoverable_on: FIRST_READ
    support: {Q-01/A: S, Q-01/B: S}
    readings:
      Q-01/A: {reading: "Como A lê.", strength: MEDIUM, corroborated_by: [EVD-02]}
      Q-01/B: {reading: "Como B lê.", strength: MEDIUM, corroborated_by: [EVD-03]}
    language_dependent: false
    ledger_event: null
mutations: []
false_resolutions: []
destabilizers: []
mutation_log:
  - {version: 0.1.0, task: T018_CANON_REGISTRY, owner: CANON_GUARDIAN, action: "Consolidação inicial."}
```

O template é validado pela suíte (mesma disciplina de
`CAUSAL_LEDGER_TEMPLATE.yaml`: campo que muda aqui muda no validador).

### 31.2 CLI do validador

```text
check_interpretive_canon.py --runtime . --mode plan|realized|final|assets|paratext
    [--through-chapter N] [--baseline <snapshot>] [--forum <FORUM_SYNTHESIS.yaml>]
    [--json] [--snapshot-as PLAN|WAVE_NN]
Consultas: --graph | --ledger Q-* | --double Q-* | --heatmap | --leader Q-* --at-chapter N
           --gaps | --mutations | --collisions | --exposure | --metrics | --end-state
```

Saída: Markdown ou JSON no **formato** de `REVIEW_FINDING` (sem o limite de
capítulo, R-05); exit 1 com HIGH/BLOCKER (convenção de todos os validadores).

### 31.3 Outros contratos

| Arquivo | `kind` | Seção |
|---|---|---|
| `engine/templates/FORUM_PERSONAS.yaml` | `ForumPersonas` | 19.4 |
| `reviews/FORUM_SIMULATION/<persona>.yaml` | `ForumResponse` | 19.6 |
| `reviews/FORUM_SYNTHESIS.yaml` | `ForumSynthesis` (derivado, carimbado com `generated_from`, reusa `stamp_derived_artifact`) | 19.7 |
| `CANON_REGISTRY.prohibited_inferences[].match` | campo opcional novo (lista de termos) | 18.3 |

## 32. Observability

### 32.1 Perguntas → consulta

| Pergunta pedida | Consulta / artefato |
|---|---|
| quais teorias estão ativas | `--graph` (texto + bloco Mermaid opcional no relatório) |
| onde suas evidências aparecem | `--ledger Q-*` (linha, capítulo, âncora, suporte, leituras) |
| quais capítulos concentram pistas | `--heatmap` (capítulo × pergunta; marca `max_evidence_per_chapter`) |
| qual interpretação domina | `--leader Q-* --at-chapter N` (trajetória) |
| onde falta evidência | `--gaps` (interpretações famintas, silêncios > `max_seed_silence`) |
| quais pistas sofreram mutação | `--mutations` (arco, `SHIFT/OSCILLATING`, gatilhos realizados) |
| quais teorias colidiram | `--collisions` + `FORUM_SYNTHESIS.emergent_theories` |
| quais leitores perceberam cada pista | `FORUM_SYNTHESIS.evidence_perception` (`EVD-*` × persona) |
| o que está exposto em superfícies públicas | `--exposure` |

### 32.2 Um relatório, não um painel

`reviews/THEORY_REPORT.md` é gerado em `GATE_CANON` e `GATE_FULL_MANUSCRIPT`
pela própria execução do validador (não por agente): resumo de 1 página,
achados, heatmap, trajetória do líder por pergunta, percepção por persona e
classificação final. Sem dashboard, sem banco, sem serviço — o repositório é
a memória.

### 32.3 Visão de motor × visão de escrita

Não há "verdade" a esconder (`NO_HIDDEN_ANSWER`), mas há **teses e leituras**
que podem induzir o escritor a sublinhar. Por isso briefs recebem só
`observable`, `salience` e a restrição "não fechar"; `--ledger` completo é
para planejamento e revisão, nunca colado em prompt de prosa (mesma
disciplina de `--engine-view` do ledger).

---

## 33. Failure Modes

| Failure mode | Como aparece | Detecção | Onde |
|---|---|---|---|
| Final só "aberto" | pergunta `NEVER` com pouca evidência | `EVIDENCE_STARVED`, `RANDOM_AMBIGUITY` | plan / final |
| Consenso disfarçado | matriz balanceada, prosa inclina | forum `CONSENSUS_COLLAPSE`; `SUBTEXT_EDITOR` | final |
| `S` de fachada | coluna marcada sem leitura concreta | `DE-01`, `DE-04`; forum não percebe | plan / final |
| Charada | capítulo existe para plantar | `PUZZLE_CHAPTER`, `felt_like_puzzle` | plan / final |
| Gramática aprendida | leitor só nota o que foi plantado | `noise_share` baixo | final |
| Pista invisível | nenhuma persona encontra | `planned_hit_rate`, `AUTHORIAL_CHEATING` | final |
| Narrador trapaceiro | narrador confiável afirma falso | `RH-03` | plan / wave |
| Retcon interpretativo | linha `REALIZED` muda para caber | `INTERPRETIVE_RETCON` | wave / final |
| Teoria vira fato | tese entra no registry/ledger | `CI-01`, `CI-02` | todos |
| Resposta vaza por GT | GT descreve um lado | `AD-04` | plan |
| Evidência de colecionador | pista indispensável só na guarda | `VE-04` | plan / assets |
| Pixel não realiza | 6 botões viram 5 | `VE-06`; volta a `PLANNED` | assets |
| Tradução colapsa | pronome ambíguo resolvido | `language_dependent` + revisão de tradução | tradução |
| Inferência proibida emerge | leitores concluem o que o canon proíbe | `PROHIBITED_INFERENCE_EMERGED` | final |
| Forum contaminado | leitor leu o canon | canário 19.7 | final |
| Forum homogêneo | todas as personas pensam igual por serem o mesmo modelo | variância baixa entre posturas opostas (`SKEPTIC` × `CONTRARIAN` concordando em tudo) → `FORUM_LOW_VARIANCE` (INFO) | final |
| Citação inventada | quote não existe | `FORUM_QUOTE_FABRICATED` | final |
| Bait no marketing | "você vai questionar tudo" | `AD-07` | mídia |
| Processo engole literatura | tarefas e relatórios demais | 9 tarefas, 7 determinísticas; Regra de Ouro; revisão adversarial (40) | processo |
| Contexto insuficiente | host não lê manuscrito inteiro | `CAPABILITY_BLOCKER long_context_reading` | bootstrap |

---

## 34. Anti-Patterns

| Anti-pattern | Proteção | Natureza |
|---|---|---|
| mistério pelo mistério | `DD-01`, seleção de sementes enraizadas em GT (10.4) | estrutural + julgamento |
| finais vagos | `EVIDENCE_STARVED`, `RANDOM_AMBIGUITY`, `LEVEL_1_CLOSURE_MISSING` | estrutural + forum |
| pistas impossíveis | `DISCOVERY_FAIRNESS`, `discoverable_on`, `VE-03/04` | empírica + estrutural |
| retcons | INV-10/INV-11 reusados, `INTERPRETIVE_RETCON`, `RM-04` | estrutural |
| contradição acidental tratada como profundidade | toda contradição que "conta" é linha `EVD-*` com âncora; o resto é achado de `PLOT_CONTINUITY_REVIEWER`/`check_canon_continuity.py` | estrutural |
| cliffhanger gratuito | `DD-02`; loops do ledger exigem transformação (SOFT-04) | estrutural |
| red herring sem função | `RH-05`, `RH-07` | estrutural |
| "era tudo um sonho" | `prohibited_inferences` padrão sugerido para toda obra (`PRO-*` "os eventos não ocorreram"); `TC-02` | estrutural + forum |
| narrador não confiável como desculpa universal | `narrators[]` com `scope` e `tells` obrigatórios; `EL-08` | estrutural |
| excesso de símbolos | `max_visual_evidence_share`, `min_decorative_visual_elements`, Chekhov | estrutural |
| puzzle tomando a narrativa | `NARRATIVE_NATURALNESS` bloqueia `THEORY_READY` | empírica |
| detalhe artificial para Reddit/TikTok | 25.2; `share_detail` só descobre; `AD-07` | processo + estrutural |
| ausência de resposta onde é necessária | `max_never_questions`, `HL-03`, `DD-02` | estrutural |
| dependência de sequel | `AD-06` | estrutural |
| teoria criada só por informação ausente | critério 10.4.5; `FACT_WITHHELD_AS_MYSTERY`; toda interpretação precisa de `S` **presente**, ausência só conta como canal `ABSENCE` ancorado | estrutural |

---

## 35. Testing Strategy

### 35.1 Padrão

`unittest`, 100% offline, fixtures em `tests/fixtures/`, uma mutação por
teste afirmando **a categoria exata** (padrão
`tests/test_causal_ledger.py::TestMutationsProduceExactCategory`). Nenhum
teste chama modelo; forum é testado com respostas enlatadas.

### 35.2 Fixture de validação — gênero diferente de romance

`tests/fixtures/books/living_theory_mvp/` — 6 capítulos, mistério rural
("quem tocou o sino da capela na noite em que ninguém tinha a chave"):
2 sementes (`Q-BELL` PLURAL/ONTOLOGICAL `NEVER`; `Q-GUILT` BINARY/MORAL
`NEVER`), 1 pergunta `RESOLVED_AT` (quem trocou a fechadura) com crença
revisada no ledger, 1 red herring justo, 1 mutação `OSCILLATING`, 1
destabilizador final, manuscrito congelado curto com as `TEXT:` âncoras, e
`tests/fixtures/living_theory/forum/*.yaml` (respostas enlatadas: um conjunto
`THEORY_READY`, um `CONSENSUS_COLLAPSE`, um contaminado, um com citações
fabricadas).

### 35.3 Suítes

| Suíte | Exemplos de teste (nome → categoria esperada) |
|---|---|
| **UNIT** (`test_interpretive_canon.py`) | template válido; ids duplicados → `EVIDENCE_DUPLICATE`; enum inválido → `INVALID_ENUM`; partição com interpretação de outra pergunta → `PARTITION_INVALID`; ciclo `IMPLIES`/`EXCLUDES` → `RELATION_CONTRADICTORY`; projeção de dupla evidência; projeção de líder com empate |
| **CONTRACT** (`test_compose_regression.py` estendido) | fixture compõe com `T022T`, `T2NNT`, `T302T/U`; validadores nos gates certos; runbook `canon/THEORY_AGENTS.md` copiado; `smoke-test` passa; `visual_evidence` sem `visual_narrative` → erro de `validate-book` |
| **CANON** | tese copiada para `facts` → `THEORY_PROMOTED_TO_FACT`; `EVD-*` em `caused_by` → `THEORY_AS_CAUSE`; chave `truth` → `HIDDEN_ANSWER_PRESENT`; crença `NEVER` em `revises` → `LEDGER_BELIEF_CLOSES_NEVER_QUESTION`; interpretação casando `PRO-*` → `PROHIBITED_INTERPRETATION` |
| **EVIDENCE** | interpretação sem `S` → `INTERPRETATION_WITHOUT_EVIDENCE`; dupla sem `readings` → `DOUBLE_EVIDENCE_WITHOUT_READING`; âncora `TEXT:` inexistente em `final` → `EVIDENCE_ANCHOR_UNRESOLVED` |
| **BALANCE** | inflar `S` de uma tese → `INTERPRETATION_DOMINANCE`; `X` em N−1 → `EVIDENCE_COLLAPSES_QUESTION` (BLOCKER) |
| **RANDOMNESS** | remover evidência até <`min_support` → `EVIDENCE_STARVED`; forum com citações não resolvidas → `RANDOM_AMBIGUITY` |
| **REREAD** | gatilho anterior à pista → `MUTATION_TRIGGER_NOT_LATER`; última fase fecha pergunta `NEVER` → `REREAD_RESOLVES_AMBIGUITY`; mudar `observable` realizado → `INTERPRETIVE_RETCON`; oscilação reconhecida como `OSCILLATING` |
| **VISUAL** (só com fixture visual existente `visual_narrative_mvp`) | evidência só em `COLLECTOR_ONLY` → `EDITION_EXCLUSIVE_EVIDENCE`; `monochrome_safe: false` → `VISUAL_EVIDENCE_COLOR_DEPENDENT`; `VISUAL:` com feature desligada → `VISUAL_EVIDENCE_DISABLED` |
| **FORUM** (`test_forum_comparison.py`) | quote inventada → `FORUM_QUOTE_FABRICATED`; resposta com tese do canon → `FORUM_CONTAMINATION`; 5/6 na mesma tese → `CONSENSUS_COLLAPSE`; personas de simpatia excluídas da entropia; emergente com âncoras → `THEORY_GENERATIVE`; emergente = `PRO-*` → `PROHIBITED_INFERENCE_EMERGED`; toda posição contada tem ≥1 citação resolvida (rastreabilidade) |
| **REGRESSION** | `tests/fixtures/golden/*.json` idênticos; `test_causal_ledger`, `test_visual_canon`, `test_narciso_book` (baseline R-02) sem novas falhas; `detect_repetition` produz relatório idêntico em livro sem `theory_bait` |
| **NATURALNESS** | fixture com capítulo cuja `function` cita `EVD-*` → `PUZZLE_CHAPTER`; densidade acima do limite → `EVIDENCE_OVERDENSE`; forum casual `felt_like_puzzle: 8` → sem `THEORY_READY`; livro sem loop resolvido → `LEVEL_1_CLOSURE_MISSING`. **Limite declarado:** naturalidade real não é testável offline — o teste garante que o *sinal* bloqueia a classificação, não que o sinal está certo |

### 35.4 Critério de template

`test_template_fields_match_validator`: toda chave do template é conhecida
pelo validador e vice-versa (padrão `TestCausalLedgerRunbookFieldNames`).

---

## 36. Migration / Backward Compatibility

### 36.1 Garantias

| id | Garantia | Prova |
|---|---|---|
| `LT-INV-00` | livro sem `features.living_theory` compõe `TASK_GRAPH` idêntico | goldens JSON |
| `LT-INV-01` | nenhum script existente muda saída para livro sem a feature | regressão de `detect_repetition` e validadores |
| `LT-INV-02` | `resolve_anchor` com `VISUAL:` não altera resolução de nenhum tipo existente | `test_visual_canon` inteiro verde |
| `LT-INV-03` | runtime sem `canon/THEORY_AGENTS.md` = livro não usa a capability | `IMPLEMENT.md` |
| `LT-INV-04` | Narciso continua passando no validador próprio até a migração explícita | `test_narciso_book` |

### 36.2 Pré-condições

1. Versionar o working tree (R-01).
2. Triar o erro pré-existente `test_engine_cli_state` (R-02) antes do Slice 7.

### 36.3 Migração de Narciso (Slice 9, E3)

| Narciso hoje | Contrato genérico |
|---|---|
| `reflection_hypotheses` + `reflection_evidence` | `Q-REFLECTION` (`PLURAL`) + `evidence[]` com `channel` inferido |
| `love_readings` (`love`/`narcissism` com força) | `Q-LOVE` (`BINARY`) + `evidence[].readings` |
| `policy.*` | `thresholds` equivalentes (`min_support_per_evidence` → regra por linha; `min_viable_hypotheses_at_end` → `min_viable_at_end`) |
| `reread_clues` | `mutations[]` de 2 fases; `touches` → `favors` |
| `final_evidence` (`chapter_architecture`) | `destabilizers[]` **ou** `OPEN_FINAL_EVIDENCE` (38.5) |
| `IL:`/`OBJECT:` | `VISUAL:<IL-*>` / `VISUAL:<COMP-*>` |
| `desire_occurrences`, `partnered_intimacy`, consentimento, gêmeo, léxicos | **permanecem** no validador da obra |

Passos: (a) script de adaptação gera `INTERPRETIVE_CANON.seed.yaml` genérico
a partir do seed atual, **sem apagar** o original; (b) execução paralela dos
dois validadores sobre seed e mutações dos testes existentes; tabela de
equivalência de categorias (`SINGLE_HYPOTHESIS_EVIDENCE` ↔ regra por linha,
`LOVE_FINAL_RESOLVED` ↔ `DE-02` na última linha etc.); (c) só com
equivalência completa, `validate_narciso.py` passa a delegar as regras
promovidas e liga `features.living_theory`; (d) `T018N_INTERPRETIVE_CANON` e
os snapshots `T2NNN` da obra são removidos do `BOOK_GRAPH` porque o motor os
provê — decisão humana registrada.

Enquanto (c) não acontece, `features.living_theory` **não** pode ser ligado em
Narciso: dois canons interpretativos no mesmo runtime seriam duas verdades
(`validate_book_data` recusa `living_theory` + `additional_tasks` com output
`/canon/*INTERPRETIVE_CANON.yaml`).

---

## 37. E0–E4 Rollout

| Estágio | Entrega | Critério de saída | Slices |
|---|---|---|---|
| **E0 — IDEIA** | esta SDD + decisões das OQs bloqueantes | humano aprova OQ-LTE-01, 03, 04 | 0 |
| **E1 — UX LOCAL** | template + `check_interpretive_canon.py --mode plan` + consultas sobre a fixture de mistério rural, rodados à mão; seed de Narciso passado por adaptador **somente leitura** para provar que o contrato cabe | fixture passa; mutações dão categorias exatas; adaptador reproduz contagens de 38.4; nenhum arquivo de `engine/scripts/livingbook.py` tocado | 1–4 |
| **E2 — FUNCIONAL LOCAL** | compose OFF por padrão, snapshots, modos `realized/final`, forum com agente + comparador (respostas enlatadas), bait, relatório | goldens idênticos; fixture compõe e passa `smoke-test`; suíte verde | 5, 6, 8 |
| **E3 — VALIDAÇÃO** | (a) **retro-auditoria** somente leitura de um manuscrito final já existente de gênero diferente — recomendado `eva-a-ultima-mulher-da-terra` (80.954 palavras, ambiguidade bloqueante por regra, guardião de mistério e de imparcialidade) — numa **cópia** do runtime; (b) Narciso: migração + execução real até `GATE_FULL_MANUSCRIPT`; (c) evidência visual se Narciso chegar a `GATE_VISUAL` | limiares de 16.3 recalibrados com dados; forum real pago produz classificação coerente com julgamento humano em ≥1 livro; nenhuma regra de Narciso perdida | 7, 9, 10 |
| **E4 — PRODUÇÃO** | capability documentada em `COMO_EXECUTAR_UM_LIVRO.md` e `BOOK_PACKAGE_CHECKLIST.md`; continua OFF por padrão; decisão sobre guardião genérico (OQ-LTE-07) | 2 livros completos com a feature; custo real de forum no `COST_LEDGER` | — |

A retro-auditoria em E3a é a peça mais barata e mais informativa do plano:
testa os **instrumentos** contra prosa real sem gastar geração, e diz se o
forum distingue um livro com ambiguidade engenheirada de um livro que só
deixa perguntas.

## 38. Narciso Golden Case

> Narciso é cenário de aceite, não arquitetura. Nada abaixo decide o que o
> reflexo é nem se Narciso amou. Todos os números vêm de
> `books/narciso/seeds/INTERPRETIVE_CANON.seed.yaml` e
> `chapter_architecture.yaml` como estão hoje (script de contagem no Apêndice A).

### 38.1 Por que Narciso é o caso certo

Identidade visual forte, ilustrações por slot, livro como espelho, perguntas
que o próprio pacote já trata como `NEVER` (`IR-N01`, `IR-N03`, `IR-N10`), e
o único canon interpretativo estruturado do repositório. Se o contrato
genérico não absorver Narciso sem perda, ele está errado.

### 38.2 Sementes

| Pergunta | `shape` | `axis` | `half_life` | `resolution_policy` | Âncora de incógnita |
|---|---|---|---|---|---|
| `Q-LOVE` "Narciso amou alguém além de si?" | BINARY | RELATIONAL/MORAL | HIGH | NEVER | `IR-N03` (hoje não há `UNK` próprio → **lacuna**: criar `UNK-NAR-002`) |
| `Q-REFLECTION` "O que olha de volta?" | PLURAL (5) | ONTOLOGICAL | HIGH | NEVER | `UNK-NAR-001`, `PRO-NAR-001..006` |

Duas sementes, ambas `HIGH`: dentro de `max_duality_seeds: 3`.

### 38.3 As quatro dualidades pedidas, sem sementes novas

| Dualidade pedida | Modelagem genérica | Por quê |
|---|---|---|
| "Narciso amou alguém?" SIM ↔ NÃO | `Q-LOVE` | semente |
| "O reflexo é apenas Narciso?" SIM ↔ NÃO | partição `Q-REFLECTION~ONLY_NARCISO`: `YES: [PROJ, SELF]`, `NO: [SUPER, OTHER, GAZE]` | derivada |
| "Existe algo sobrenatural?" SIM ↔ NÃO | partição `Q-REFLECTION~SUPERNATURAL`: `YES: [SUPER]`, `NO: [PROJ, SELF, OTHER]`, `GAZE` **não atribuída** | derivada |
| "Narciso percebe corretamente?" SIM ↔ NÃO | partição `Q-REFLECTION~PERCEPTION`: `NO: [PROJ]`, `YES: [SUPER, SELF, OTHER, GAZE]` | derivada (axis EPISTEMIC) |

Duas sementes produzem seis perguntas discutíveis. É a demonstração
concreta de "poucas perguntas profundas, muitas teorias derivadas".

### 38.4 O que o contrato genérico mede hoje, com os dados reais

**Dupla evidência por partição** (15 evidências `RFX`):

| Partição | Duplas | Só de um lado |
|---|---|---|
| `SUPERNATURAL` com `GAZE` no lado SIM | 15/15 | — |
| `SUPERNATURAL` estrita (`GAZE` não atribuída) | 14/15 | `RFX-05` só no lado NÃO (`H-SUPER: C`) |
| `ONLY_NARCISO` | 15/15 | — |
| `PERCEPTION` | 14/15 | `RFX-14` só no lado SIM (`H-PROJ: C`) |

Leitura: a partição sobrenatural é **sensível à classificação de `H-GAZE`**.
Se o leitor acha que "algo nascido da contemplação" é sobrenatural, a
pergunta é perfeitamente dupla; se não acha, `RFX-05` (fotos em modo espelho)
vira argumento só do lado cético. Esse desacordo sobre *classificar* uma
hipótese é teoria derivada legítima — o motor não o resolve; o
`--collisions`/forum o torna visível.

**Balanço (`EL-06`)**: `S` finais — PROJ 14 · SUPER 14 · SELF 13 · GAZE 9 ·
OTHER 8. Razão 1,75 ≤ 2,0: passa, mas `H-OTHER` é a interpretação mais
próxima de `EVIDENCE_STARVED` se uma linha voltar a `PLANNED` na realização.

**Trajetória do líder `Q-REFLECTION`** (soma de `S`): PROJ lidera ou empata
do capítulo 10 ao 30 (margem ≤ 2); no capítulo 32, PROJ = SUPER = 13 → **sem
líder** antes do capítulo 33.

**Trajetória do líder `Q-LOVE`** (WEAK=1, MEDIUM=2, STRONG=3): empate até o
14; amor 11×10 no 16 (`LOVE-E4`: amor STRONG, narcisismo MEDIUM); 14×13 no
18; empate 16×16 no 24 (`LOVE-E9`: amor MEDIUM, narcisismo STRONG) até o fim.

**Mutações**: 15 `reread_clues` → 15 `MUT` de duas fases; 0 `OSCILLATING`.

### 38.5 Achados do golden case (o que a migração vai exigir)

| # | Achado | Regra genérica | Severidade prevista | Decisão |
|---|---|---|---|---|
| N-01 | Nenhuma das 15 linhas `RFX` tem `readings`; todas são projetadas como dupla evidência | `DE-01` | HIGH ×15 | trabalho de migração: escrever as leituras (é também o melhor teste de honestidade da matriz) |
| N-02 | Linhas de testemunha externa — `RFX-06` (Coro), `RFX-09` (Teodoro), `RFX-11` e `RFX-15` (fotos) — marcam `H-PROJ: S`. Projeção sustentada por terceiro precisa de leitura explícita | `DE-01`, `EL-08` | HIGH | **sonda principal do forum**: `SKEPTIC` e `PSYCHOLOGICAL_READER` aceitam ou não |
| N-03 | Evidência final `RFX-15` tem `S` nas 5 hipóteses e não há líder antes dela | 22.2 | — | classificada `OPEN_FINAL_EVIDENCE`, **não** bomba. Coerente com a decisão OQ-N9; se a autora quiser uma bomba, é decisão nova, não correção |
| N-04 | Em `Q-LOVE`, a vantagem do amor no 16–18 é de 1 ponto e é desfeita por reequilíbrio (`LOVE-E9`), não por `C` | 22.1 | — | a definição estrita de destabilizador não reconhece isso como falsa resolução → **OQ-LTE-10** |
| N-05 | `RR-12` usa `OBJECT:ENDPAPER_FRONT`; guarda impressa é `UNSUPPORTED` em Kindle, paperback e hardcover KDP | `VE-04` | passa **só** se houver redundância: `RR-12` toca só `H-GAZE`, que tem 9 `S` textuais e `RR-07` (texto) | passa; teste obrigatório do Slice 7 |
| N-06 | `RR-06` (capa como espelho): a leitura oculta depende de acabamento `SILVER_MIRROR` `COLLECTOR_ONLY` (OQ-N6) nas edições em que "a capa produz reflexo" | `VE-04` | idem N-05 | passa por redundância textual (`SCENE:THE_CENTER`) |
| N-07 | `Q-LOVE` não tem `UNK` no registry | `CI-04` | HIGH | criar `UNK-NAR-002` (decisão humana, trivial) |
| N-08 | `RFX-04` "para que ele não o visse" é ambiguidade pronominal do português | `language_dependent` | — | marcar `true`; hoje `translation_preparation: false` |
| N-09 | Coro final (`WE_STILL_LOOK`, `RR-07` "o nós incluía quem lê") está a um passo de endereçar o leitor | `theory_bait` (`"o leitor"`) + `ANTI_MANIPULATION_GUARDIAN` | — | sonda de `CASUAL_READER`: `felt_asked_to_theorize` |
| N-10 | `PRO-NAR-006` (gêmeo) | `TC-02` | — | se alguma persona formular "gêmeo/irmão" na fase 1, é `PROHIBITED_INFERENCE_EMERGED` — o texto vaza o que `IR-N11` proíbe |
| N-11 | Densidade: máximo de 2 evidências por capítulo (ex.: cap. 26 `RFX-13` + `LOVE-E6`) | 16.3 | — | passa com folga |
| N-12 | Nenhuma mutação oscilante | `RM-06` | — | Narciso em `reread_depth: STANDARD`; `DEEP` é escolha autoral, não exigência |

### 38.6 Forum para Narciso

`panel`: as 7 posturas do motor (PREMIUM). `book_personas`:
`ROMANTIC_READER` (`sympathizes_with: [Q-LOVE/A]`), `SUPERNATURALIST`
(`[Q-REFLECTION/SUPER]`), `PSYCHOLOGICAL_READER` (`[Q-REFLECTION/PROJ,
Q-LOVE/B]`). `visual_pass: true` depois de `GATE_VISUAL` (é aqui que pranchas
como `IL-05`/`IL-12` — pinta do lado errado — viram argumento).

### 38.7 O critério final da missão, operacionalizado

> "Dois leitores inteligentes discutem uma hora, citando o livro, e terminam
> convencidos de interpretações incompatíveis. Um terceiro diz: voltem ao
> capítulo 7 e olhem a ilustração."

| Frase | Condição verificável no `FORUM_SYNTHESIS` |
|---|---|
| dois leitores inteligentes | duas posturas neutras (ex.: `SKEPTIC`, `LITERARY_CRITIC`) — não personas de simpatia |
| interpretações incompatíveis | posições diferentes na mesma pergunta ou em faces opostas de uma partição |
| ambos citando o livro | ≥3 citações resolvidas cada |
| boas evidências | citações casam com linhas `S` `STRONG`/`MEDIUM` da tese defendida |
| ainda convencidos | confiança `HIGH` **e** `counter_acknowledged` contém a evidência mais forte do outro lado |
| "voltem ao capítulo 7 e olhem a ilustração" | `REREADER`/`CLUE_HUNTER` na passada visual cita uma evidência (`VISUAL:` ou `TEXT:`) **não usada** pelos dois primeiros e que tem `S` em interpretação fora das duas posições → `THEORY_GENERATIVE` |

### 38.8 Aceite do golden case

1. Adaptador somente leitura (E1) reproduz exatamente as contagens de 38.4.
2. Execução paralela (Slice 9) produz achados equivalentes aos de
   `validate_narciso.py` nas mutações existentes de `test_narciso_book.py`.
3. N-01, N-02 e N-07 resolvidos pelo pacote; N-05/N-06 cobertos por teste.
4. Nenhuma resposta criada: `AD-01..04` sem achado.
5. As regras exclusivas da obra (`DSR`, consentimento, gêmeo, Coro, léxicos)
   continuam no validador da obra.

---

## 39. Acceptance Criteria

### 39.1 Da SDD (E0)

- [x] Discovery real com arquivos e linhas (5, Apêndice A).
- [x] REUSE/EXTEND/CREATE explícito (6.1) e alternativas rejeitadas (6.2).
- [x] Arquitetura genérica antes de Narciso (7–37 × 38).
- [x] 41 seções pedidas.
- [x] Incompatibilidades e riscos (5.4, 33).
- [x] Backward compatibility com prova por golden (36).
- [x] E0–E4 sem pular estágio (37).
- [x] Slices com objetivo, arquivos, contratos, testes, riscos, dependências, DoD (41).
- [x] Nenhuma resposta de Narciso decidida; livro não escrito.

### 39.2 Da capability (E2)

1. `features.living_theory` ausente ⇒ goldens idênticos e suíte sem novas falhas.
2. Fixture de gênero ≠ romance compõe, passa `smoke-test` e todos os modos do validador.
3. Cada falha de 20.2 tem ≥1 teste de mutação com categoria exata.
4. Interpretação nunca vira fato, causa ou canon (`CI-*` testados).
5. Forum: toda posição contada é rastreável a citação resolvida; contaminação e fabricação detectadas.
6. `NARRATIVE_NATURALNESS` falha impede `THEORY_READY`.
7. 1 agente novo, 0 gates novos, 0 dependências novas.

### 39.3 Da capability (E3)

8. Retro-auditoria de um livro de gênero diferente produz relatório que o humano considera correto em ≥80% dos achados HIGH.
9. Narciso migrado sem regra perdida (38.8).
10. Limiares de 16.3 revistos com dados e registrados com data e fonte.

## 40. Open Questions

### 40.1 Perguntas

| ID | Pergunta | Bloqueia | Recomendação |
|---|---|---|---|
| ~~OQ-LTE-01~~ | Nome do arquivo e da feature | — | **DECIDIDO** (40.3) |
| OQ-LTE-02 | Forum em `T300` (ainda revisável) ou também confirmação após `T310` | Slice 6 | só `T300` em E2; confirmação pós-congelamento só se E3 mostrar que `T304` destrói evidência |
| ~~OQ-LTE-03~~ | Achados só empíricos podem bloquear em PREMIUM? | — | **DECIDIDO** (40.3) |
| ~~OQ-LTE-04~~ | Diversidade de modelos no forum | — | **DECIDIDO** (40.3) |
| OQ-LTE-05 | Extrair `resolve_anchor` para módulo sem Pillow | Slice 7 | não agora; reavaliar quando o validador de Narciso delegar (terceiro consumidor) |
| OQ-LTE-06 | Livro de gênero diferente para E3: retro-auditoria de `eva` ou produção de `adao` | E3 | `eva` (manuscrito final existe; custo só de leitura) |
| OQ-LTE-07 | Guardião genérico de integridade interpretativa substituindo a metade comum dos 3 guardiões de obra | E4 | não criar antes de 2 livros com a feature; decidir com os relatórios em mãos |
| OQ-LTE-08 | Léxico `theory_bait` para `en` quando `translation_preparation` estiver ligado | Slice 8 | lista por idioma no mesmo arquivo; começar só `pt-BR` |
| OQ-LTE-09 | Leitores cegos podem ver o sumário/títulos de capítulo? (são paratexto e podem ser pista) | Slice 6 | sim — é o que o leitor real vê |
| OQ-LTE-10 | Destabilizador pode ser "contrapeso" (`S` mais forte do lado oposto) além de `C` no líder? | Slice 4 | aceitar como `kind: COUNTERWEIGHT` separado de `LAST_EVIDENCE_BOMB`; decidir com N-04 |
| OQ-LTE-11 | `prohibited_inferences[].match` (termos) no registry: campo novo num arquivo sem schema | Slice 6 | aceitar como opcional; sem ele, classificação humana |
| OQ-LTE-12 | Texto da rubrica humana de deniabilidade (23.4) | Slice 5 | autora redige |

### 40.2 Revisão adversarial (o que um crítico deste desenho diria)

| Crítica | Resposta | Mudança feita |
|---|---|---|
| "É o validador de Narciso com outro nome" | Em boa parte, sim — de propósito. O que é novo: leitores cegos, partições, mutação oscilante, destabilizadores, justiça entre edições, fronteira teoria/fato verificável | escopo novo listado em 1.2 |
| "Leitores LLM não são leitores" | Correto. Por isso o forum é diagnóstico, nunca veredito, e há canário, fabricação detectada e checkpoint humano | 19.1, 20.3 |
| "Matriz S/C/X é subjetiva" | É. `readings` + `corroborated_by` obrigam a subjetividade a ser escrita e confrontada pelo forum | `DE-01`, `DE-04` |
| "Muitas regras" | São ~60 achados, todos de uma família com precedente ou de risco encontrado no repo; 7 das 9 tarefas novas são determinísticas | 29 |
| "Otimizar divisividade corrompe literatura" | Divisividade só é exigida onde a obra declarou `NEVER`; naturalidade vence tudo | 20.2, 24.2 |
| "Evidência visual vai virar gimmick de colecionador" | `VE-04` e `VE-07` impedem pista indispensável fora do texto e fora de edições baratas | 15.4 |
| "Um agente novo viola REUSE" | Todo agente atual é instruído a ler o pacote; o isolamento é o contrato | 19.3 |
| "O motor vai ensinar escritores a plantar pistas" | Briefs recebem restrição ("não feche"), não instrução ("plante"); `SUBTEXT_EDITOR` lê sem `readings` | 13.3, 32.3 |

### 40.3 Registro de decisões humanas (2026-09-15, Slice 0)

| ID | Decisão | Efeito nesta SDD |
|---|---|---|
| OQ-LTE-01 | **`canon/INTERPRETIVE_CANON.yaml`** e **`features.living_theory`** | nomes de 1.3, 29, 30 e 31 confirmados; `kind: InterpretiveCanon` |
| OQ-LTE-03 | **Achado só do forum nunca bloqueia gate**, em nenhum perfil | 20.3 confirmado: teto HIGH, destino `T303` + checkpoint humano de `GATE_FULL_MANUSCRIPT` |
| OQ-LTE-04 | **Registrar `model_actual` por persona, sem exigir diversidade de provedores** | `ForumResponse` ganha `model_actual` obrigatório; `FORUM_LOW_VARIANCE` (33) continua INFO |
| Commit | Branch `slice-0/versionar-working-tree`; `output/` e `tmp/` no `.gitignore`; `.venv` rastreada fica como está | R-01 resolvido; nada enviado ao remote |

---

## 41. Implementation Slices

Ordem e dependências:

```text
S0 ─▶ S1 ─▶ S2 ─▶ S3 ─▶ S4 ─┬─▶ S5 ─▶ S6 ─▶ S8 ─┬─▶ S10
                             │                    │
                             └──────▶ S7 ─────────┤
                                                  └─▶ S9 (Narciso, E3)
E1 = S1–S4 · E2 = S5, S6, S8 · E3 = S7, S9, S10
```

### SLICE 0 — Discovery / contratos

- **Objetivo:** fechar esta SDD, decisões bloqueantes e pré-condições.
- **Arquivos:** `docs/sdd/LIVING_THEORY_ENGINE_SDD_v0.1.md`; commit do working tree existente (R-01).
- **Contratos:** nenhum código.
- **Testes:** baseline registrado: `PYTHONIOENCODING=utf-8 python -m unittest discover -s tests` → 544 testes OK (R-02).
- **Status:** **concluído em 2026-09-15** — decisões em 40.3.
- **Riscos:** começar a implementar sobre arquivos não versionados.
- **Dependências:** humano (OQ-LTE-01, 03, 04).
- **DoD:** SDD aprovada; working tree versionado; baseline de testes anotado no commit.

### SLICE 1 — Minimal Theory Model

- **Objetivo:** contrato mínimo e integridade: perguntas, interpretações, partições, `NO_HIDDEN_ANSWER`, fronteira de canon.
- **Arquivos:** `engine/templates/INTERPRETIVE_CANON_TEMPLATE.yaml` (novo); `engine/scripts/check_interpretive_canon.py` (novo, `--mode plan`, `--ledger`/`--runtime`); `tests/test_interpretive_canon.py`; `tests/fixtures/books/living_theory_mvp/` e `tests/fixtures/living_theory/runtime/`.
- **Contratos:** 31.1 (sem `mutations`, `destabilizers`); regras `AD-01..04`, `CI-01..05`, `TG-01/02/05`, limites de 10.4, `HL-01..03`.
- **Testes:** UNIT + CANON (35.3); template ↔ validador.
- **Riscos:** sobredesenho do schema antes de dados reais → só campos usados por alguma regra.
- **Dependências:** S0.
- **DoD:** fixture passa; cada mutação dá categoria exata; nenhum arquivo existente do motor alterado.

### SLICE 2 — Evidence Ledger

- **Objetivo:** linhas de evidência, suporte, balanço, dupla evidência projetada, red herrings, saliência.
- **Arquivos:** `check_interpretive_canon.py` (importa `resolve_anchor` de `check_visual_canon.py`); template; testes.
- **Contratos:** `EL-01..09`, `DE-01..06`, `RH-01..05, 07`, 16.3 estrutural; `--ledger`, `--double`, `--heatmap`.
- **Testes:** EVIDENCE, BALANCE, RANDOMNESS (estrutural).
- **Riscos:** acoplamento a módulo de 3,2 mil linhas com Pillow (R-12).
- **Dependências:** S1.
- **DoD:** consultas funcionam na fixture; `RH-06` fica para S4 (precisa ledger).

### SLICE 3 — Theory Graph

- **Objetivo:** relações, partições projetadas, colisões, trajetória de líder, distribuição por movimento.
- **Arquivos:** validador; testes.
- **Contratos:** `TG-03/04`, `TC-03/04`, `DS-DIST-01/02`; `--graph`, `--leader`, `--collisions`, `--gaps`.
- **Testes:** UNIT de projeção (empate, partição com não atribuída), colisão.
- **Riscos:** tentação de pesos/probabilidades → proibido nesta versão (9.3).
- **Dependências:** S2.
- **DoD:** adaptador somente leitura do seed de Narciso reproduz 38.4 **(marco E1 de UX)**.

### SLICE 4 — Reread Mutation (+ destabilizadores e ledger)

- **Objetivo:** `mutations`, `false_resolutions`, `destabilizers`, modos `realized`/`final`, snapshots, integração com ledger.
- **Arquivos:** validador (`--snapshot-as`, `--baseline`, `--through-chapter`, `--mutations`); testes; fixture de ledger da `living_theory_mvp`.
- **Contratos:** `RM-01..07`, 22.1–22.3, `EL-07`, `AD-03`, `RH-06`, `DD-02`; reuso de `knowledge_state` e `second_read_classifications` de `check_causal_ledger.py`.
- **Testes:** REREAD; retcon interpretativo; pergunta com resposta usando INV-11.
- **Riscos:** R-03 (INV-11 × `NEVER`) — coberto por `AD-03`; OQ-LTE-10.
- **Dependências:** S3.
- **DoD:** fixture passa em `plan`, `realized` e `final`; **E1 concluído**.

### SLICE 5 — Pipeline integration (OFF por padrão)

- **Objetivo:** ligar a capability no compositor sem alterar nenhum livro existente.
- **Arquivos:** `engine/scripts/livingbook.py` (flag, anotações, `T022T`, `T2NNT`, validadores em gates, cópia de scripts/runbook, `validate_book_data`); `engine/templates/INTERPRETIVE_CANON_RUNBOOK.md`; `engine/IMPLEMENT.md` (1 parágrafo); `engine/ENGINE_GRAPH.yaml` (`long_context_reading`); `EXECUTION_PROFILES.yaml` (`forum_panel_limit`); `tests/test_compose_regression.py`.
- **Contratos:** 29, 30, `LT-INV-00..03`.
- **Testes:** CONTRACT + REGRESSION (goldens byte a byte).
- **Riscos:** alterar ordem de tarefas de livros existentes → tudo dentro de `if living_theory_enabled`, lido do spec original.
- **Dependências:** S4.
- **DoD:** goldens idênticos; fixture compõe e passa `smoke-test`; `run_deterministic.py` executa os snapshots.

### SLICE 6 — Forum Simulation

- **Objetivo:** leitura cega em duas fases e comparação determinística.
- **Arquivos:** `engine/agents/forum_reader.toml`; `engine/templates/FORUM_PERSONAS.yaml`; `engine/scripts/compare_forum_responses.py`; `livingbook.py` (`T302T`, `T302U`, input em `T303`); `tests/test_forum_comparison.py`; `tests/fixtures/living_theory/forum/*.yaml`.
- **Contratos:** 19.4–19.7, 20.2 (empírico), `TC-01/02`, `ForumResponse`, `ForumSynthesis`.
- **Testes:** FORUM (35.3), todos com respostas enlatadas.
- **Riscos:** R-07, R-08, R-14; custo de tokens.
- **Dependências:** S5.
- **DoD:** as quatro respostas enlatadas geram as quatro classificações esperadas; spawn usa `template_agent` + `rotate_pack`; nenhum teste chama modelo.

### SLICE 7 — Visual Evidence

- **Objetivo:** âncora `VISUAL:`, justiça entre edições, acessibilidade, anomalia realizada, passada visual opcional.
- **Arquivos:** `check_visual_canon.py` (só `resolve_anchor` + `VISUAL`); `check_interpretive_canon.py` (`--mode assets`, `--exposure`); `livingbook.py` (`T4ZZT` condicional); testes sobre `visual_narrative_mvp`.
- **Contratos:** `VE-01..07`, 15.6.
- **Testes:** VISUAL; `test_visual_canon` inteiro verde (`LT-INV-02`).
- **Riscos:** R-02 precisa estar triado; R-09 (pixels); R-10.
- **Dependências:** S4; S6 para a passada visual.
- **DoD:** N-05 e N-06 de Narciso cobertos por teste com fixture equivalente; nenhuma regressão visual.

### SLICE 8 — Metrics / Observability / Bait

- **Objetivo:** relatório único, métricas de 27, detector de bait e paratexto.
- **Arquivos:** validador (`--metrics`, geração de `reviews/THEORY_REPORT.md`, `--mode paratext`); `detect_repetition.py` (`detect_theory_bait`); `TEXT_QUALITY_DEFAULTS.yaml` (`theory_bait` desligado); testes.
- **Contratos:** 27.2, 32, `AD-05..07`, `DD-01/03/04`.
- **Testes:** NATURALNESS estrutural; REGRESSION de `detect_repetition` sem a chave ligada.
- **Riscos:** relatório virar painel → uma página, sem serviço.
- **Dependências:** S6.
- **DoD:** `THEORY_REPORT.md` responde às 9 perguntas de 32.1 na fixture; **E2 concluído**.

### SLICE 9 — Narciso Golden Case

- **Objetivo:** migrar Narciso para o contrato genérico sem perder regra.
- **Arquivos:** script de adaptação (em `books/narciso/validators/`, não no motor); `books/narciso/seeds/INTERPRETIVE_CANON.seed.yaml` gerado ao lado do atual; `validate_narciso.py` (delegação); `books/narciso/BOOK_SPEC.yaml`, `BOOK_GRAPH.yaml`; `tests/test_narciso_book.py`.
- **Contratos:** 36.3, 38.
- **Testes:** execução paralela com tabela de equivalência; `test_narciso_book.py` verde.
- **Riscos:** divergência silenciosa entre validadores; esforço de N-01 (15 linhas × leituras); decisões humanas (N-03, N-04, N-07).
- **Dependências:** S4, S7; decisão humana explícita revogando a recomendação "não agora" de OQ-N10.
- **DoD:** 38.8 inteiro; runtime de Narciso com um único canon interpretativo.

### SLICE 10 — Regression / Hardening / Validação real

- **Objetivo:** provar e calibrar em prosa real.
- **Arquivos:** relatório da retro-auditoria (`discovery-books/` ou `docs/sdd/`); `thresholds` recalibrados; `docs/COMO_EXECUTAR_UM_LIVRO.md`; `engine/templates/BOOK_PACKAGE_CHECKLIST.md`.
- **Contratos:** 37 E3.
- **Testes:** suíte completa; retro-auditoria numa **cópia** do runtime de `eva` (nunca no runtime original); forum real pago uma vez.
- **Riscos:** custo; calibrar em um único livro (sobreajuste) → exigir Narciso + `eva`.
- **Dependências:** S8, S9.
- **DoD:** 39.3 inteiro; decisão registrada sobre OQ-LTE-07.

---

## Apêndice A — Arquivos inspecionados e comandos executados

### A.1 Arquivos

- Raiz: `AGENTS.md`, `README.md`, `CODEX_ENGINE_BOOTSTRAP_PROMPT.md`, `DISTRIBUTION_MANIFEST.md`, `Makefile`, `requirements.txt`.
- Motor: `engine/AGENTS.md`, `engine/ENGINE_GRAPH.yaml`, `engine/IMPLEMENT.md`; `engine/contracts/*.schema.json` (6); `engine/agents/` (`canon_guardian`, `symbolism_architect`, `reader_vitals_agent`, `literary_critic`, `plot_engineer`, `subtext_editor`, `narrative_architect`, `anti_manipulation_guardian`, `plot_continuity_reviewer`, `visual_director`, `image_continuity_qa`, `commercial_editor_critic`, `executive_editor`, `briefing_architect`); `engine/templates/` (`CAUSAL_LEDGER_TEMPLATE.yaml`, `CAUSAL_LEDGER_RUNBOOK.md`, `VISUAL_NARRATIVE_CANON_TEMPLATE.yaml`, `VISUAL_NARRATIVE_RUNBOOK.md`, `EDITION_CAPABILITIES.yaml`, `EXECUTION_PROFILES.yaml`, `TEXT_QUALITY_DEFAULTS.yaml`).
- Scripts: `engine/scripts/livingbook.py` (35–55, 111–167, 209–460, 461–486, 525, 615–712, 750–830), `check_causal_ledger.py` (esboço de funções; 705–739, 827–849, 968–1036, 1056), `check_visual_canon.py` (60–122, 287–398, 680–713, 1243–1293, 2559–2648), `detect_repetition.py` (esboço), `run_deterministic.py`, `runtime_taskgraph.py` (esboço).
- SDDs: `docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md` (1–2, 9, 10, 20, 24, 25, 27, 35 Slices 6–8, 36), `DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md` (D, H, I, J), `BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md` (índice); `discovery-books/09-*` (início).
- Narciso: `BOOK_SPEC.yaml`, `BOOK_GRAPH.yaml`, `capability_requirements.yaml`, `quality_profile.yaml`, `immutable_rules.yaml`, `protected_scenes.yaml`, `chapter_architecture.yaml` (cabeçalho, `final_evidence`), `INTERPRETIVE_CANON_RUNBOOK.md`, `seeds/INTERPRETIVE_CANON.seed.yaml`, `seeds/VISUAL_NARRATIVE_CANON.seed.yaml` (duality), `planning/MIRROR_MANIFESTATION.yaml`, `planning/LEXICONS.yaml` (chaves), `agents/*.toml`, `validators/validate_narciso.py` (esboço; 817–1063).
- Outras obras: `eva…/agents/mystery_ambiguity_guardian.toml`, `impartiality_guardian.toml`, `seeds/WORLD_RULES_SEED.md §8`, `validators/validate_final_manuscript.py` (esboço); `adao…/agents/mystery_integrity_guardian.toml`.
- Runtimes: `runtime/eva-a-ultima-mulher-da-terra/TASK_GRAPH.yaml` (tarefas e gates), `canon/CANON_REGISTRY.yaml` (início); `runtime/a_morte_ainda_nao_nasceu/canon/CANON_REGISTRY.yaml:550-595`; `runtime/a-noiva-esquecida/living_book/MEMORY_MOTIF_MAP.md`.
- Testes: `tests/test_compose_regression.py` (cabeçalho, classes), `tests/test_narciso_book.py` (classes; 812–836), `tests/test_causal_ledger.py`, `tests/test_book_as_mirror.py` (classes).

### A.2 Comandos

```text
git status --short / git log --oneline
python -m unittest tests.test_causal_ledger tests.test_visual_canon tests.test_compose_regression \
  tests.test_visual_narrative_rendering tests.test_narciso_book tests.test_book_as_mirror \
  tests.test_illustration_system
  → Ran 471 tests in 73.086s — FAILED (errors=1): test_narciso_book.TestNarcisoVisualRuntime.test_engine_cli_state
PYTHONIOENCODING=utf-8 python -m unittest discover -s tests -p "test_*.py"   (Slice 0)
  → Ran 544 tests in 113.177s — OK
grep chapter_count books/*/BOOK_SPEC.yaml → 40, 24, 34, 42, 24, 4, 33, 24
wc -w runtime/eva-a-ultima-mulher-da-terra/manuscript/final/MANUSCRIPT_FINAL_PTBR.md → 80954
script de contagem sobre books/narciso/seeds/INTERPRETIVE_CANON.seed.yaml
  (duplas por partição, trajetória acumulada de S, trajetória ponderada de LOVE, reread_clues) → seção 38.4
```

