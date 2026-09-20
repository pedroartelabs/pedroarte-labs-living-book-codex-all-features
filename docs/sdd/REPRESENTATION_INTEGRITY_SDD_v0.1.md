# SDD v0.1 — `REPRESENTATION_INTEGRITY` (Bea Halden — Thematic Freedom)

> **Limite de geração ≠ limite do universo ficcional.**

| Campo | Valor |
|---|---|
| Status | **E0 — PROPOSTA.** Nenhum código escrito, nenhum agente criado, nenhum comportamento do motor alterado. Aguarda aprovação humana explícita do SDD. |
| Data | 2026-09-19 (decisões humanas OQ-RI-01 e OQ-RI-02 registradas em 2026-09-20) |
| Tipo | Capability transversal do motor (neutra de gênero) + política editorial de autora (Bea Halden) |
| Ativação | `features.representation_integrity.enabled` — **OFF por padrão** |
| Pré-requisito | `features.causal_ledger.enabled: true` (a capability anota eventos do ledger) |
| Base | `engine/ENGINE_GRAPH.yaml` `1.1.0`, branch `slice-1/interpretive-canon-model`, commit `98a2f5c` + working tree (Slices 1–2 do `LIVING_THEORY_ENGINE` não commitados) |
| SDDs irmãs | `DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md` (ledger causal — **base desta SDD**), `LIVING_THEORY_ENGINE_SDD_v0.1.md` (canon interpretativo), `NARCISO_CANONICAL_SDD_v0.1.md` (obra Bea Halden com teto de explicitude), `BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md` (padrão de perfil de autora) |
| Regras aplicadas | `REUSE > EXTEND > CREATE`; `SIMPLICIDADE SEMPRE`; texto em PT-BR, identificadores em inglês |

## Índice

1. Executive Summary · 2. Problem Statement · 3. Goals · 4. Non-Goals ·
5. Repository Discovery · 6. Existing Components Reused ·
7. Architectural Decision · 8. Domain Model · 9. Thematic Freedom Constitution ·
10. Darkness Preservation · 11. Character ≠ Author · 12. Adult Age Gate ·
13. Hard Boundaries · 14. Representation Matrix · 15. Representation Capability ·
16. Dark Content Ledger · 17. Authorial Gap · 18. Content Warning separation ·
19. Canon Sanitization Gate · 20. Theory Engine interaction ·
21. Provider abstraction · 22. Data contracts / schemas · 23. State transitions ·
24. Pipeline integration · 25. Artifact lifecycle · 26. Observability ·
27. Privacy · 28. Failure modes · 29. Test strategy · 30. Acceptance criteria ·
31. Migration / backward compatibility · 32. Rollout plan · 33. Open questions ·
34. Files likely to change ·
Apêndice A — Mapa AS-IS → TO-BE · Apêndice B — Arquivos inspecionados

---

## 1. Executive Summary

### 1.1 O que é

Uma capability do motor que torna **verificável** a diferença entre quatro
coisas que hoje só estão separadas por convenção textual:

```text
THEME  ≠  CANONICAL EVENT  ≠  SCENE REPRESENTATION  ≠  GENERATION CAPABILITY
```

Ela garante que, quando um provider/agente não consegue (ou não deve)
representar uma cena com a intensidade planejada, o motor:

1. **preserva o cânone** (evento, consequências, motivações, estado relacional,
   consentimento canônico, ambiguidade deliberada);
2. **degrada apenas a representação**, com uma estratégia literária (elipse,
   aftermath, câmera, memória, testemunho) — nunca com placeholder;
3. **registra a diferença** num relatório editorial **privado** do autor —
   o `DARK_CONTENT_LEDGER` — sem gerar o conteúdo que ficou de fora;
4. **reprova ruidosamente** qualquer alteração do cânone causada só pela
   limitação de geração (`CANON_SANITIZATION`);
5. **reprova fechado** qualquer plano que cruze um *hard boundary*
   (sexualização de menores, instrução operacional de dano) — e nunca
   transforma isso em "lacuna para completar depois".

### 1.2 A descoberta que mais moldou o desenho

**O motor já tem ~60% disto — só que como regra textual, sem verificação.**

| Pedido | Já existe como | Onde |
|---|---|---|
| Evento canônico ≠ representação | `events[].facts` ("verdade canônica, inclusive fora da página") × `events[].evidence_to_reader` ("câmera muda isto, nunca `facts`") | `engine/templates/CAUSAL_LEDGER_TEMPLATE.yaml:162-170` |
| "Limite de geração não corrompe canon" | **Regra de renderização**: "registre `evidence_to_reader` reduzida ou devolva o evento para `PLANNED` — nunca reescreva `facts`, `caused_by` ou `consent`" | `engine/templates/CAUSAL_LEDGER_RUNBOOK.md:91-97`; DR SDD E.4 |
| Gate adulto (idade canônica ≥ 18; desconhecida = FAIL) | `ADULT_SEDUCTION_FAIL` (BLOCKER, todo perfil) | `engine/scripts/check_causal_ledger.py:641-680` (INV-06) |
| Consentimento canônico ≠ percepção | bloco `consent` com `perceived` separado; `CONSENT_DRIFT`, `COERCION_AS_PAYOFF` | idem `:851-905` (INV-07..09) |
| Crença de personagem ≠ fato | `self_model`, `interpretations[].reads_as`, `beliefs[]` com `left_open` | ledger (LAW 04); LTE §26.1 (estados epistêmicos) |
| Ambiguidade que nunca fecha | `resolution_policy: NEVER`, `NO_HIDDEN_ANSWER`, `LEDGER_BELIEF_CLOSES_NEVER_QUESTION` | `engine/scripts/check_interpretive_canon.py` (Slices 1–2, não commitado) |
| Teto autoral de explicitude por cena | `adult_content.explicitness_ceiling: SUGGESTED < SENSUAL < FRANK` + `EXPLICITNESS_ESCALATION` | `books/narciso/chapter_architecture.yaml`, `books/narciso/validators/validate_narciso.py:512-614` |
| Recusa do host | "recusa de conteúdo adulto vira `CAPABILITY_BLOCKER`, nunca contorno" | `books/narciso/capability_requirements.yaml:4`; `books/narciso/agents/desire_decay_guardian.toml:29-30` |
| Capacidade de host e bloqueio | `known_capabilities`, `capability_requirements.yaml`, `CAPABILITY_BLOCKER` | `engine/ENGINE_GRAPH.yaml:61, 257-310` |
| Saídas ao leitor sem metadado interno | "Reader-facing outputs must contain no prompts, agent names, task metadata… or internal review comments" | `engine/scripts/livingbook.py:792` (`outputs/AGENTS.md`) |
| Página de aviso no miolo | "AVISO DE FICÇÃO" na matéria frontal | `engine/scripts/build_kdp_docx.py:600-607`; `engine/templates/KDP_LAYOUT_DEFAULTS.yaml:107-120` |
| Perfil de autora fora do pacote do livro | `authors/bea_halden/AUTHOR_VISUAL_DNA.v1.yaml` + `approvals/` | decisão OQ-1 da SDD visual; `livingbook.py:141-155` |

O que **não existe** é pequeno e nomeável:

1. **Nenhum registro estruturado da representação.** `evidence_to_reader` é
   texto livre; nada diz "planejado 9, realizado 6, por limite do provider".
2. **O plano não é congelado.** O snapshot do ledger inclui **só** eventos
   `REALIZED` (`build_snapshot_document`, `check_causal_ledger.py:1378-1383`:
   "Nunca inclui eventos PLANNED"). Um evento `PLANNED` "A mata B" pode ser
   promovido a `REALIZED` como "A discute com B" **sem nenhum achado** — o L10
   só compara `REALIZED` × `REALIZED`. **Esse é o buraco exato por onde a
   sanitização passaria hoje.**
3. **Nenhuma política de permissão temática** (o que pode existir, ser
   central, ser retratado, ser gráfico) separada de hard boundaries.
4. **Nenhum relatório privado do autor** nem **aviso de conteúdo ao leitor**.
5. **Nenhuma detecção de artefato de geração** no manuscrito (`[CENSURADO]`,
   texto de recusa do modelo).

### 1.3 A menor arquitetura que cumpre a missão

```text
MOTOR (neutro de gênero; OFF por padrão; goldens intactos)
  engine/scripts/check_representation.py        1 validador novo (importa check_causal_ledger: REUSE)
  engine/scripts/check_causal_ledger.py         EXTEND mínimo: --snapshot-plan (congela o PLANO)
  engine/scripts/detect_repetition.py           EXTEND: detector generation_artifacts (enabled:false)
  engine/scripts/build_kdp_docx.py              EXTEND: página opcional de aviso de conteúdo
  engine/scripts/livingbook.py                  flag, 2 tarefas `tool`, anotações, validadores em gates
  engine/templates/CAUSAL_LEDGER_TEMPLATE.yaml  EXTEND: bloco opcional events[].representation
  engine/templates/REPRESENTATION_POLICY_TEMPLATE.yaml   CREATE (dados)
  engine/templates/REPRESENTATION_RUNBOOK.md    CREATE → runtime canon/REPRESENTATION_AGENTS.md

AUTORA
  authors/bea_halden/REPRESENTATION_POLICY.v1.yaml  + approvals/   (CREATE, dados; aprovação humana)

RUNTIME (gerado, só quando ligado)
  canon/snapshots/CAUSAL_LEDGER.PLAN.yaml       plano congelado no GATE_CANON
  reviews/DARK_CONTENT_LEDGER.md                PRIVADO (autor/editor)
  media/READER_CONTENT_WARNINGS.md              LEITOR (vira página do DOCX e/ou descrição)

0 agentes novos · 0 gates novos · 0 dependências novas · 0 serviços
1 estado de rejeição novo, condicional (CONTENT_HARD_BOUNDARY)
```

### 1.4 O que NÃO é

- **Não** é gerador de conteúdo explícito nem critério de sucesso "mais explícito".
- **Não** é blacklist temática. O validador **nunca** varre a prosa atrás de
  palavras de tema; classes de conteúdo são **declaradas** por quem planeja,
  com função narrativa obrigatória (contexto > keyword).
- **Não** é mecanismo de contorno de provider. Nenhuma rota reenvia uma cena
  recusada a outro modelo, reformula para escapar de política, fragmenta
  conteúdo entre chamadas ou esconde intenção (seção 21).
- **Não** é "Bea Halden no core": o motor conhece `content_classes`,
  execução e intensidade; a política de Bea Halden é um arquivo de dados em
  `authors/bea_halden/`.
- **Não** muda nenhum livro que não ligue a flag.

### 1.5 Recomendação em uma linha

```text
READY_FOR_SLICE_1 = YES após decisões OQ-RI-01, 02 e 03 (seção 33)
Pré-condição de motor: commitar os Slices 1–2 do LIVING_THEORY_ENGINE (working tree sujo)
```

---

## 2. Problem Statement

### 2.1 O problema

O motor está produzindo Dark Romance sob a identidade Bea Halden (`narciso`,
`a-noiva-esquecida`, ambos `metadata.author: Bea Halden`, ambos com
`causal_ledger` ligado). O gênero depende de material perturbador: obsessão,
stalking, coerção, dubcon, CNC entre adultos, violência, tortura,
automutilação, luto, tabus.

Os geradores (LLMs) têm limites próprios de representação, diferentes entre
providers e entre versões. Sem arquitetura, esses limites vazam para a obra
por quatro caminhos, **nenhum detectado hoje**:

| Caminho | Mecânica real no motor | Detecção atual |
|---|---|---|
| **Sanitização no plano** | `PLOT_ENGINEER` (LLM) propõe eventos a partir do pacote humano; pode omitir o assassinato que o autor pôs em `chapter_architecture.yaml` | nenhuma (só o checkpoint humano do `GATE_CANON` em STANDARD/PREMIUM) |
| **Sanitização na promoção** | `CANON_GUARDIAN` promove `PLANNED → REALIZED` "com `evidence_to_reader` real"; eventos `PLANNED` são "livremente revisáveis" (DR SDD §F) | **nenhuma**: snapshot não contém eventos `PLANNED` |
| **Sanitização na prosa** | escritor suaviza a cena; o ledger continua dizendo o fato original | revisores de wave, sem critério declarado |
| **Manuscrito quebrado** | escritor deixa `[CENA REMOVIDA]` ou texto de recusa | nenhuma |

### 2.2 Tensão central

```text
Preservar liberdade temática total da autora
SEM exigir que nenhum provider ultrapasse seus próprios limites
E SEM abrir um canal de contorno desses limites.
```

A resolução é **separar o que o universo contém do que a página mostra**, e
tornar a diferença visível ao humano — que é quem decide o que fazer com ela.

---

## 3. Goals

| ID | Goal | Verificável por |
|---|---|---|
| G-01 | Tema, evento canônico, representação e capacidade de geração são campos/artefatos distintos | contrato (seção 22) + testes de separação |
| G-02 | Nenhuma limitação de geração altera o cânone silenciosamente | `CANON_SANITIZATION` (seção 19) contra snapshot do plano |
| G-03 | Nenhum plano cruza hard boundary; hard boundary nunca gera Authorial Gap | `HB-*` BLOCKER; `HARD_BOUNDARY_GAP` |
| G-04 | Toda interação erótica exige adultos canônicos | REUSE INV-06 + `ADULT_KIND_MISSING` |
| G-05 | Manuscrito legível, sem placeholders nem artefatos de geração | `generation_artifacts` BLOCKER |
| G-06 | Autor recebe relatório privado com gaps localizáveis por cena | `reviews/DARK_CONTENT_LEDGER.md` com `SCENE_LOCATION` resolvida |
| G-07 | Aviso ao leitor e ledger do autor são artefatos separados, sem vazamento | `REPORT_LEAK_*` + testes de separação |
| G-08 | Ambiguidade deliberada sobrevive a qualquer reescrita de representação | `AMBIGUITY_COLLAPSED` (+ LTE AD-03) |
| G-09 | Provider-agnostic, sem roteamento por recusa | contrato de `generated_by` + non-goal testado por ausência de mecanismo |
| G-10 | Zero impacto em livros sem a feature | goldens `tests/fixtures/golden/*.json` byte a byte |

## 4. Non-Goals

- Implementar gerador pornográfico ou qualquer escala de "excitação do leitor".
- Criar mecanismo de bypass de provider (reenvio por recusa, reformulação
  para evadir política, fragmentação, ofuscação, "jailbreak" por moldura
  ficcional).
- Sexualizar menores, em qualquer representação, plano ou relatório.
- Gerar instruções operacionais de automutilação, suicídio ou outro dano.
- Criar blacklist lexical de temas; transformar content warning em censura.
- Moralizar personagens automaticamente ou inserir sermões.
- Alterar o cânone para esconder limitações.
- Criar agentes, gates, engines ou serviços novos.
- Duplicar validadores existentes (INV-06, INV-07..10, L10, AD-03 são **reusados**).
- Acoplar Bea Halden ao core (política vive em `authors/`).
- Medir "qualidade" de cena escura por número; intensidade é comparação
  plano × realizado, nunca alvo de otimização.
- Reingestão automática de edições humanas pós-freeze (FUTURE, OQ-RI-10).

---

## 5. Repository Discovery

Todas as afirmações abaixo foram verificadas lendo código, templates,
pacotes, testes e SDDs nesta sessão (Apêndice B). Runtimes não existem no
working tree (`runtime/` é gitignored) — nenhuma evidência desta SDD depende
deles.

### 5.1 Arquitetura real

```text
engine/                         motor genérico (engine/AGENTS.md: sem canon, nomes, vetos de gênero)
  ENGINE_GRAPH.yaml             task_states, generic_rejection_states, locks, 66 agentes,
                                protocolos (BASE_WAVE_REVIEW, PROTECTED_SCENE, CANON_PROPOSAL),
                                known_capabilities (de HOST), quality_defaults
  scripts/livingbook.py         compositor: build_standard_graph gera o DAG do BOOK_SPEC;
                                features lidas com .get() do spec ORIGINAL; annotate() de tarefas;
                                engine_validators anexados a gates existentes; copy_runtime()
  scripts/runtime_taskgraph.py  máquina de estados; validate-gate grava validator_results
  scripts/run_deterministic.py  executa tarefas com `tool`
  scripts/check_causal_ledger.py   L0–L10 (DR SDD) — 1.585 linhas
  scripts/check_interpretive_canon.py  LTE Slices 1–2 (NÃO commitado)
  scripts/check_visual_canon.py    canon visual; resolve_anchor (TEXT:, LEDGER:, SCENE:…)
  scripts/detect_repetition.py     pré-filtro lexical com override por livro; exit 1 em HIGH
  scripts/build_kdp_docx.py        matéria frontal (rosto, copyright, AVISO DE FICÇÃO, sumário)
  templates/*                      contratos executáveis (template YAML testado ≠ JSON Schema)
  contracts/*.schema.json          documentais, não executados, defasados (cap. ≤ 30)
authors/bea_halden/             AUTHOR_VISUAL_DNA.v1.yaml + approvals/ (perfil de autora)
books/<slug>/                   DNA da obra: BOOK_SPEC, chapter_architecture, immutable_rules,
                                protected_scenes, agents/, validators/
tests/                          unittest offline; goldens de compose; fixtures neutras
```

### 5.2 Achados por conceito pedido

| Conceito | Estado real | Evidência |
|---|---|---|
| **Dark Romance** | capability `DARK_ROMANCE_CANON_ARCHITECT` implementada como ledger causal **neutro de gênero** (`features.causal_ledger`) | DR SDD; `check_causal_ledger.py` |
| **Bea Halden** | `metadata.author` em `narciso` e `a-noiva-esquecida`; Author Visual DNA aprovado; governança DR SDD §S (`DEFAULT_AUTHOR_IDENTITY = BEA_HALDEN` para Dark Romance) | `books/*/BOOK_SPEC.yaml`; `authors/bea_halden/` |
| **Content warnings** | **inexistente** (única ocorrência de "gatilho" é gatilho narrativo) | grep |
| **Consent** | bloco canônico com `perceived` separado; drift e coerção-como-payoff bloqueados; Narciso modela compulsão como `ability_to_refuse: CONSTRAINED` | `check_causal_ledger.py:851-905`; Narciso SDD §11.4 |
| **Sexual tension** | loops `INTIMACY`/`EROTIC` com payoff de horizonte longo; `HEAT ≠ EXPLICITNESS`; heat profile = seção de brief, não canon | DR SDD C.2, H.3 |
| **Taboo themes** | GT `kind: TABOO/BOUNDARY`; Taboo Ladder explicitamente **não criado**; tabu de obra em `immutable_rules` (Narciso IR-N11) | DR SDD C.2 |
| **Violence** | sem estrutura; aparece só como `reject_if` autoral de cena protegida (Narciso `THE_REJECTION`) | `books/narciso/protected_scenes.yaml` |
| **Self-harm** | só regras **autorais** de obra: IR-N10/IR-N16 ("nenhum ato de autolesão é narrado", "nenhum método… descrito"); `DESIRE_DECAY_GUARDIAN` rejeita autolesão romantizada | `books/narciso/immutable_rules.yaml` |
| **Canon preservation** | INV-10 `PAST_FACTS = CONSTANT` (REALIZED × snapshot), CONSENT_DRIFT, GT congelada, `mutation_log` | `check_causal_ledger.py:907-965` |
| **Manuscript validation** | `V_CAUSAL_LEDGER_FINAL`, auditorias `T32xx`, `detect_repetition`, `check_typography`, `check_canon_continuity`, validador de obra | `livingbook.py:684-710` |
| **Chapter validation** | `GATE_WAVE_n` + `V_CAUSAL_LEDGER_WAVE_n` + revisores rotacionados | idem |
| **Author reports** | `reviews/*` (CAUSAL_LEDGER_REPORT, THEORY_REPORT planejado), `validator_results`, `APPROVALS/` escritos só por humano | `IMPLEMENT.md` "Checkpoints humanos" |
| **Narrative intent** | `chapter_architecture` (`function`, `irreversible_turn`, `dramatic_question`, `emotional_movement`); `protected_scenes` (`purpose`, `must_preserve`, `reject_if`); Narciso `adult_content` | pacotes |
| **Scene metadata** | não há entidade "cena"; unidade estrutural = evento do ledger; `evidence_to_reader`; âncoras `TEXT:`/`SCENE:`/`TURN:` | ledger; `check_visual_canon.resolve_anchor` |
| **Safety / fallback / degradation** | `CAPABILITY_BLOCKER` (host); fallback **de acabamento** por edição (`finish_intents.fallbacks`); regra de renderização textual do ledger; "nunca contornar políticas" | `EDITION_CAPABILITIES.yaml`; runbook do ledger; guardião de Narciso |

### 5.3 Conflitos com contratos mais fortes (registrados; menor evolução proposta)

| ID | Contrato existente | Conflito com o pedido | Menor evolução proposta |
|---|---|---|---|
| **C1** | Narciso: "recusa de conteúdo adulto vira `CAPABILITY_BLOCKER`" | o pedido quer continuar com representação reduzida + gap | `CAPABILITY_BLOCKER` **permanece** quando não há representação que preserve o cânone; quando há, o novo caminho é `CONSTRAINED` + gap. Knob de política `on_constrained_representation: RECORD_GAP \| BLOCK`. Narciso mantém `BLOCK` até decisão humana (**OQ-RI-02**) |
| **C2** | DR SDD §F: eventos `PLANNED` "livremente revisáveis via proposta" | revisão livre é o buraco da sanitização | com a feature ligada, revisão de plano **depois** do `GATE_CANON` continua permitida, mas **declarada** em `mutation_log` com `reason`; não declarada = `UNDECLARED_PLAN_DRIFT` |
| **C3** | DR SDD K/OUT: "qualquer escala numérica de calor ou excitação" fora; template: "estados são categorias em texto, nunca números" | pedido de escala 0–10 | a intensidade vive **só** no bloco `representation` (não é estado de personagem, relação nem calor/excitação); é ordinal âncorada e só diferenças ≥ limiar importam. Alternativa categórica em **OQ-RI-01** |
| **C4** | DR SDD C.2: heat profile/câmera = brief, "não é canon" | intenção de representação precisa ser comparável por evento | bloco `representation` anexado ao evento é **metadado de renderização, não canon**: nunca é `caused_by`, nunca entra em projeção, não congela contra L10. Precedente: `evidence_to_reader` já vive no evento |
| **C5** | `engine/AGENTS.md`: `/engine` sem vetos de gênero | classes de conteúdo e hard boundaries no motor | classes são **neutras de gênero** (servem horror, guerra, crime); hard boundaries são piso legal/ético universal (precedente: `MIN_ADULT_AGE` já está no motor). Permissões temáticas vivem em `authors/` |
| **C6** | LTE AD-05 `NO_INTERPRETIVE_PARATEXT`; Narciso IR-N09 (paratexto só antes do cap. 1) | aviso de conteúdo é paratexto | aviso é **não interpretativo**, entra antes do cap. 1 e passa por `AD-07`-like (não pode conter tese) |
| **C7** | Narciso `explicitness_ceiling` (SUGGESTED/SENSUAL/FRANK), validado pela obra | vocabulário genérico novo | Narciso mantém o seu (é teto **autoral**). O genérico usa `graphic: bool` + execução; sem mapeamento forçado. Migração opcional (seção 31.3) |

### 5.4 Outros achados relevantes (não corrigidos)

| ID | Achado | Impacto |
|---|---|---|
| D1 | Working tree sujo: `check_interpretive_canon.py`, template, testes e fixture do LTE não versionados; SDD do LTE modificada | commit antes do Slice 4 (goldens estáveis) |
| D2 | `REVIEW_FINDING.schema.json` limita capítulo a 30 (Narciso tem 33) | achados seguem a **forma**, não o schema |
| D3 | Suíte no Windows exige `PYTHONIOENCODING=utf-8` (baseline LTE: 544 OK) | comando de teste documentado |
| D4 | `tests/test_image_generation.py` pode fazer chamada paga com `.env` | testes novos rodam por módulo |
| D5 | Agentes genéricos (`ANTI_MANIPULATION_GUARDIAN`, `LEGAL_EDITOR_GLOBAL`, `PLOT_CONTINUITY_REVIEWER`) têm instruções genéricas; comportamento vem de `parameters` das tarefas | a capability instrui por `annotate()`, como o ledger |
| D6 | `.gitignore` ignora qualquer `runtime/` inclusive em `tests/fixtures/` | fixtures se chamam `runtime_<nome>` |

---

## 6. Existing Components Reused

| Necessidade | Decisão | Componente | Justificativa |
|---|---|---|---|
| Evento canônico | **REUSE** | `events[].facts`, `kind`, `participants`, deltas | é o cânone; nada novo |
| Representação realizada ao leitor | **REUSE + EXTEND** | `evidence_to_reader` + bloco `representation` | texto livre já existe; faltam campos comparáveis |
| Gate adulto | **REUSE** | INV-06 `ADULT_SEDUCTION_FAIL` | já é BLOCKER em todo perfil, `null` = FAIL |
| Consentimento canônico | **REUSE** | bloco `consent`, INV-07..09, `CONSENT_DRIFT` | CNC/dubcon/coerção já têm vocabulário (`CONSENSUAL`/`DUBIOUS`/`COERCIVE`/`NON_CONSENSUAL`, `boundary_state`) |
| Imutabilidade do realizado | **REUSE** | L10 + snapshots por wave | continua valendo |
| Congelamento do plano | **EXTEND** | `check_causal_ledger.py --snapshot-plan` | mesmo padrão de `--snapshot-auto` |
| Crença × fato × ambiguidade | **REUSE** | `self_model`, `interpretations`, `beliefs.left_open`, LTE `NEVER`/`narrators`/`source: CHR-*` | estados epistêmicos já catalogados (LTE §26.1) |
| Comparação lexical tese↔fato | **REUSE (padrão)** | CI-02 do LTE (fração de palavras de conteúdo, limiar 0.8) | mesma técnica para `BELIEF_PROMOTED_TO_FACT` |
| Âncora de localização | **REUSE** | `check_visual_canon.resolve_anchor` (`TEXT:`) | localiza a cena no manuscrito congelado |
| Governança de canon | **REUSE** | `CANON_GUARDIAN`, `CANON_WRITE`, `CANON_PROPOSALS`, `mutation_log` | mesmo dono do ledger |
| Achado | **REUSE** | `finding()` do ledger (forma `REVIEW_FINDING`) | exit 1 em HIGH/BLOCKER |
| Perfil de autora | **REUSE (padrão)** | `authors/<id>/…vN.yaml` + `approvals/` + checagem em `validate_book_data` | precedente `AUTHOR_VISUAL_DNA` |
| Checkpoint humano | **REUSE** | `requires_human_approval` em `GATE_FULL_MANUSCRIPT` (STANDARD/PREMIUM) | nenhum checkpoint novo |
| Capacidade de host / bloqueio | **REUSE** | `CAPABILITY_BLOCKER`, `capability_requirements.yaml` | continua para ausência total de capacidade |
| Detecção lexical de artefato | **EXTEND** | `detect_repetition.py` + `TEXT_QUALITY_DEFAULTS.yaml` | mesmo mecanismo dos clichês, desligado por padrão |
| Página de aviso | **EXTEND** | `add_front_matter` + `KDP_LAYOUT_DEFAULTS.front_matter` | o "AVISO DE FICÇÃO" já é o slot |
| Pacote de mídia | **REUSE** | `T800_MEDIA_PACKAGE` (`MEDIA_AND_KDP_AGENT`) | recebe o rascunho de avisos |
| Telemetria de modelo | **REUSE** | `TASK_RESULT.model_actual`, `model_tier`, `logs/COST_LEDGER.md` | liga cada representação ao provider real |
| Revisão independente | **REUSE** | `PLOT_CONTINUITY_REVIEWER` (fato × prosa), `SUBTEXT_EDITOR` (leituras), `ANTI_MANIPULATION_GUARDIAN` (moralização/manipulação) | papéis já existentes, instruídos por parâmetro |
| Gates | **REUSE** | `GATE_CANON`, `GATE_WAVE_n`, `GATE_FULL_MANUSCRIPT`, `GATE_DELIVERY` | 0 gates novos |
| Estado de rejeição p/ sanitização | **REUSE** | `CANON_CONFLICT` | cânone alterado é conflito de cânone |
| Estado de rejeição p/ hard boundary | **CREATE (condicional)** | `CONTENT_HARD_BOUNDARY` | nenhum estado existente significa "plano ilegal"; anexado só com a feature (goldens intactos) |

### 6.1 Considerado e rejeitado

| Alternativa | Por que não |
|---|---|
| Arquivo novo `canon/REPRESENTATION_LEDGER.yaml` | a comparação plano × realizado é **por evento**; separar em outro arquivo espalha o elo por dois donos e duas versões (mesmo argumento da DR SDD E.1) |
| Guardar intenção só em `chapter_architecture.yaml` | é do pacote humano (bom como **intenção autoral**, seção 19.2), mas não tem id de evento nem ciclo `PLANNED/REALIZED` |
| Estender `check_causal_ledger.py` com as regras novas | mudaria a superfície do validador que já protege Narciso; um script separado que **importa** o ledger (padrão LTE→`check_visual_canon`) mantém `V_CAUSAL_LEDGER_*` byte a byte |
| Agente `DARK_CONTENT_GUARDIAN` genérico | todos os julgamentos têm dono existente (seção 6); guardiões de obra continuam possíveis no pacote |
| Gate `GATE_REPRESENTATION` | nenhum ponto do DAG exige parada adicional |
| Matriz de capacidade por provider ("modelo X recusa Y") | seria um **mapa de evasão**; capacidade é observada por cena, nunca tabelada para roteamento (seção 21) |
| Varredura lexical de temas na prosa | proibido pela missão; contexto > keyword |
| Taxonomia com dezenas de enums de gap | gap = `família × dimensão` projetado (seção 17.3) |

---

## 7. Architectural Decision

### 7.1 Camadas

```text
CORE STABLE (inalterado)
  ENGINE_GRAPH · compositor · causal ledger L0–L10 · interpretive canon · gates · CAPABILITY_BLOCKER
        │
        ▼
REPRESENTATION_INTEGRITY  (motor, neutro de gênero, OFF por padrão)
  content_classes (famílias fechadas) + themes (vocabulário aberto da obra)
  events[].representation {intended, realized, status, gap}
  hard boundaries HB-* (piso universal, não configurável para baixo)
  snapshot do PLANO · Canon Sanitization Gate · detector de artefatos de geração
  DARK_CONTENT_LEDGER (privado) · READER_CONTENT_WARNINGS (leitor)
        │
        ▼
POLÍTICA DE GÊNERO (dados, sem código)
  nenhuma no MVP — Dark Romance é um CONJUNTO de permissões, não um motor
  (DR SDD Q1-A: DNA de gênero no pacote/autora até existir 2º caso real)
        │
        ▼
BEA HALDEN PROFILE
  authors/bea_halden/REPRESENTATION_POLICY.v1.yaml (+ aprovação humana)
  permissões temáticas amplas, hard boundaries adicionais da autora, knobs
        │
        ▼
LIVRO (pacote)
  pode ESTREITAR a política (immutable_rules, representation_intent, tetos autorais);
  nunca ALARGAR além da política da autora
```

### 7.2 Precedência (vence a esquerda)

```text
ENGINE HARD BOUNDARIES (HB-*)
  > AUTHOR HARD BOUNDARIES (política da autora)
  > immutable_rules da obra
  > BOOK_CONSTITUTION
  > CANON_REGISTRY / CAUSAL_LEDGER (facts, consent, GT)
  > AUTHOR INTENT (chapter_architecture.representation_intent, protected_scenes)
  > CANON PLAN (eventos PLANNED + representation.intended)
  > REPRESENTATION REALIZED (prosa)
  > PROVIDER CAPABILITY
```

Consequências diretas:

- **Capacidade de provider nunca sobe na hierarquia**: ela só pode reduzir
  representação, nunca cânone.
- **Teto autoral é intenção, não lacuna** (`AUTHORIAL_CEILING_IS_INTENT`):
  Narciso IR-N10 ("nenhum ato de autolesão é narrado") entra como
  `intended.execution: REFERENCE_ONLY`; realizar exatamente isso é
  `FULLY_REPRESENTED`, nunca gap, nunca sanitização.
- **Hard boundary está acima da autora**: nenhuma política o desliga.

### 7.3 Decisões arquiteturais (ADR resumido)

| ID | Decisão | Alternativa rejeitada |
|---|---|---|
| AD-RI-01 | A unidade de rastreio é o **evento do ledger** (inclusive `structural: false`) | entidade "cena" nova |
| AD-RI-02 | Intenção e realização vivem num bloco `representation` do evento, **fora do cânone** | arquivo separado; brief em Markdown |
| AD-RI-03 | O plano é congelado em `CAUSAL_LEDGER.PLAN.yaml` no `GATE_CANON` | confiar em "PLANNED livre" |
| AD-RI-04 | Sanitização é detectada **estruturalmente** (plano × realizado) e o resíduo semântico (prosa × fato) vai a revisor existente | classificador de prosa |
| AD-RI-05 | Hard boundary = FAIL CLOSED sem override; sanitização = FAIL LOUD com override **só** por decisão humana registrada | um único nível de bloqueio |
| AD-RI-06 | `FORBIDDEN` é **projeção do validador**, nunca status armazenado | status gravável que viraria "pendência" |
| AD-RI-07 | Gap descreve **função narrativa não realizada**, nunca conteúdo | gap com rascunho do trecho |
| AD-RI-08 | Capacidade de representação é **observada** por cena e atribuída ao provider real; nunca tabelada para roteamento | matriz provider × tema |
| AD-RI-09 | Validador novo `check_representation.py` importa o ledger | estender o validador do ledger |
| AD-RI-10 | Política temática da autora em `authors/`, com aprovação humana | config de gênero em `/engine` |
| AD-RI-11 | Relatório privado em `reviews/` (já interno), nome genérico; autoria vem de `metadata.author` | `BEA_HALDEN_*.md` no motor |

---

## 8. Domain Model

### 8.1 Quatro conceitos, quatro lugares

| Conceito | Definição | Onde vive | Dono | Pode mudar por limitação de geração? |
|---|---|---|---|---|
| **THEME** | assunto que a obra aborda | `representation.content_classes` (família fechada) + `representation.themes` (aberto) por evento; `BOOK_CONSTITUTION` no nível da obra | planejadores propõem; `CANON_GUARDIAN` grava | **não** |
| **CANONICAL EVENT** | o que acontece no universo, inclusive fora da página | `events[].facts`, `kind`, `actor`, `participants`, `caused_by`, `consent`, deltas | `CANON_GUARDIAN` | **não** (FAIL LOUD) |
| **SCENE REPRESENTATION** | como a página mostra o evento | `evidence_to_reader` + `representation.intended/realized` | plano: `CANON_GUARDIAN` a partir de `PLOT_ENGINEER`/`SCENE_ARCHITECT`; realizado: `CANON_GUARDIAN` a partir do escritor + revisor independente | **sim** — é a única camada que pode ceder |
| **GENERATION CAPABILITY** | o que o provider conseguiu produzir nesta execução | `representation.realized.generated_by` + `constraint_source`; capacidade de host em `known_capabilities` | observado, não declarado | — (é o que muda) |

### 8.2 Entidades

| Entidade | Id | Armazenada? | Onde |
|---|---|---|---|
| `ContentClass` | enum fechado | sim | template |
| `Theme` | texto livre em minúsculas | sim | `representation.themes` |
| `RepresentationIntent` | — | sim | `events[].representation.intended` |
| `RepresentationRealized` | — | sim | `events[].representation.realized` |
| `RepresentationStatus` | enum | sim (3 valores) | `events[].representation.status` |
| `AuthorialGap` | projeção `GAP-<EV>` | sim (bloco) | `events[].representation.gap` |
| `AuthorIntent` | — | sim | `book/chapter_architecture.yaml → chapters[].representation_intent[]` (opcional) |
| `RepresentationPolicy` | `authors/<id>/REPRESENTATION_POLICY.vN.yaml` | sim | autora |
| `PlanSnapshot` | `CAUSAL_LEDGER.PLAN.yaml` | sim (imutável) | runtime |
| `PreservedCanon` | — | **projeção** | validador (seção 19) |
| `AgeVerification` | — | **projeção** | validador (seção 12) |
| `FORBIDDEN` | — | **projeção** | validador (seção 13) |
| `DarkContentCoverage` | — | **projeção** | relatório |
| `AuthorReviewOutcome` | — | sim, **escrito só por humano** | `project_state/APPROVALS/REPRESENTATION_REVIEW.yaml` |

### 8.3 Princípio de armazenamento (herdado)

> Guarda-se o mínimo declarado; tudo que é derivável é projetado.

"O que foi preservado", "a idade foi verificada", "isto é FORBIDDEN" e a
cobertura são **calculados**; um campo "preserved: true" escrito à mão seria
uma segunda verdade que o agente poderia afirmar sem que fosse verdade.

---

## 9. Thematic Freedom Constitution

Leis da capability (neutras de gênero, no motor). Nenhum perfil de execução,
política de autora ou livro as revoga; hard boundaries (seção 13) estão acima.

| Lei | Enunciado | Verificação estrutural | Resíduo de julgamento |
|---|---|---|---|
| **RI-LAW-01 THEMATIC_FREEDOM** | Um assunto desconfortável não deixa de poder existir no universo ficcional. O motor não possui blacklist temática; só a política da autora e hard boundaries limitam **representação**, e nada limita **existência** além dos hard boundaries | validador nunca lê prosa por tema; `content_classes` só são checadas contra a política da autora | `GENRE_GUARDIAN`, humano |
| **RI-LAW-02 LIMIT_OF_GENERATION ≠ LIMIT_OF_FICTIONAL_UNIVERSE** | Limitação de geração reduz representação, nunca cânone | `CANON_SANITIZATION` (seção 19) | `PLOT_CONTINUITY_REVIEWER` |
| **RI-LAW-03 CANON_OVER_SANITIZATION** | Diante de limite, preserva-se evento, função, consequência, motivação, estado relacional, pistas, ambiguidade e impacto; muda-se só a representação necessária, e a diferença é registrada | CS-01..13; gap obrigatório | `SUBTEXT_EDITOR`, humano |
| **RI-LAW-04 CHARACTER_IS_NOT_AUTHOR** | Crença, fala e racionalização de personagem não são posição da obra nem fato canônico | `BELIEF_PROMOTED_TO_FACT`, `GROUND_TRUTH_DRIFT` | `ANTI_MANIPULATION_GUARDIAN` (sermão/moralização) |
| **RI-LAW-05 NO_BROKEN_MANUSCRIPT** | O manuscrito do leitor é obra coerente, sem placeholder, sem texto de recusa, sem metadado | `generation_artifacts` BLOCKER | `FINAL_PROOFREADER` |
| **RI-LAW-06 HONEST_CONSTRAINT_DISCLOSURE** | Quem gera declara quando foi limitado; ninguém disfarça redução como escolha | `REPRESENTATION_UNRECORDED`; divergência escritor × revisor | revisor independente, humano |
| **RI-LAW-07 HARD_BOUNDARY_IS_NOT_A_GAP** | O que cruza hard boundary não é "representação limitada": não gera gap, não é convite a edição posterior | `HARD_BOUNDARY_GAP` BLOCKER | — (não há resíduo) |
| **RI-LAW-08 AUTHORIAL_CEILING_IS_INTENT** | Teto escolhido pela autora/obra é intenção; realizá-lo é representação completa | intenção já incorpora o teto | — |

Síntese:

```text
THE UNIVERSE MAY CONTAIN WHAT THE PAGE CANNOT SHOW.
THE PAGE MAY SHOW LESS. THE CANON MAY NOT BECOME LESS.
```

### 9.1 Bea Halden — `THEMATIC_FREEDOM_PRINCIPLE`

Registrado como política de autora (dados + texto), não como código:

> Bea Halden escreve ficção adulta. Stalking, obsessão, relação tóxica,
> misoginia, assédio, violência, assassinato, feminicídio, tortura, abuso,
> manipulação, coerção, dubcon, CNC entre adultos, BDSM, degradação, sadismo,
> masoquismo, abuso de substâncias, automutilação, ideação suicida, suicídio,
> luto, trauma e tabus familiares **podem existir** no universo das obras.
> Um assunto sensível não é um assunto proibido. O único limite de
> existência são os hard boundaries do motor e os da própria autora.

Compatível com e subordinado a `BEA_HALDEN_AUTHORIAL_GOVERNANCE` (DR SDD §S)
— inclusive ao princípio de agência: "AGENCY MAY BE WOUNDED… BUT IT MUST
NEVER BE FORGOTTEN BY THE NARRATIVE". Liberdade temática **não** revoga LAW
01–05 do ledger (causalidade, memória, consentimento canônico).

---

## 10. Darkness Preservation

### 10.1 `DARKNESS_PRESERVATION_PRINCIPLE`

> The engine MUST NOT sanitize a work merely because its subject matter is
> disturbing, immoral, taboo, violent, psychologically uncomfortable or
> socially unacceptable. A sensitive subject is not automatically a
> forbidden subject.

### 10.2 O que é preservado quando a representação cede — e como é verificado

| # | Preservar | Verificação | Tipo |
|---|---|---|---|
| 1 | evento canônico | `facts` idêntico ao plano (CS-01/02) | estrutural |
| 2 | função narrativa | `representation.narrative_function` imutável plano→realizado; gap descreve o que dela não chegou à página | estrutural + humano |
| 3 | consequências | deltas/loops/crenças do plano presentes (CS-05); cadeia `caused_by` a jusante intacta (CS-08) | estrutural |
| 4 | motivações | `caused_by` e GT dos participantes idênticos ao plano (CS-07) | estrutural |
| 5 | estado posterior da relação | `relationship_delta` do plano presente (CS-05) + INV-04 existente | estrutural |
| 6 | pistas necessárias | evidências LTE com `ledger_event` do evento não perdem `REALIZED` (seção 20) | estrutural |
| 7 | ambiguidades intencionais | `beliefs.left_open` e perguntas `NEVER` intactas (CS-09) | estrutural |
| 8 | impacto emocional | `realized.intensity` vs `intended.intensity`; `emotional_movement` do capítulo inalterado | julgamento + humano |
| 9 | modificar só o necessário | `realized.literary_strategy` declarada; nada além de execução/intensidade/`graphic` muda | estrutural |
| 10 | registrar a diferença | gap obrigatório em `CONSTRAINED`/`AUTHOR_REVIEW` | estrutural |

### 10.3 Anti-padrões de resolução (todos detectáveis por pelo menos um sinal)

| Resolução proibida | Sinal estrutural | Sinal de julgamento |
|---|---|---|
| perverso → virtuoso | `GROUND_TRUTH_DRIFT`; `caused_by` alterado | `CHARACTER_CONTINUITY_REVIEWER` |
| tóxico → saudável | `relationship_delta` do plano ausente/alterado (`CONSEQUENCE_DROPPED`) | `ANTI_MANIPULATION_GUARDIAN` |
| violência grave → discussão leve | `facts`/`kind` alterados (`CANON_SANITIZATION`, `EVENT_KIND_DROPPED`) | `PLOT_CONTINUITY_REVIEWER` |
| obsessão → paixão convencional | `representation.narrative_function` e deltas do plano ausentes | `SUBTEXT_EDITOR` |
| trauma → inexistente | evento removido sem `mutation_log` (`EVENT_SILENTLY_REMOVED`) | — |
| vilão → corrigido moralmente | `GROUND_TRUTH_DRIFT`; loops `RELATIONAL` resolvidos fora do plano | `ANTI_MANIPULATION_GUARDIAN` (`AUTHORIAL_SERMON`) |
| ambíguo → explicação moralizante | `AMBIGUITY_COLLAPSED`; LTE `REREAD_RESOLVES_AMBIGUITY`/`AD-02` | `SUBTEXT_EDITOR` |

### 10.4 Estratégias literárias de degradação (vocabulário, não prescrição)

`realized.literary_strategy` (lista, vocabulário fechado curto):
`CAMERA_SHIFT`, `ELLIPSIS`, `AFTERMATH`, `FRAGMENTED_MEMORY`,
`LATER_DIALOGUE`, `CONSEQUENCE`, `OBJECT_SYMBOL`, `TESTIMONY`,
`INVESTIGATION`, `FADE_TO_BLACK`, `OTHER`.

Serve ao relatório e à telemetria ("quais estratégias preservam melhor o
impacto"), não como regra de escrita. A escolha é do `LEAD_NOVELIST`.

---

## 11. Character ≠ Author semantics

### 11.1 Estados epistêmicos (REUSE da LTE §26.1, com o mapeamento pedido)

| Pedido | Campo existente | Pode virar fato? | Pode ser `caused_by`? |
|---|---|---|---|
| `CHARACTER_BELIEF` | `characters[].self_model[]`; `events[].interpretations[].reads_as` | não | via `self_attribution` só como atribuição |
| `CHARACTER_CLAIM` | evidência LTE com `source: CHR-*` + `narrators[]` (escopo de não confiabilidade); sem LTE: `interpretations[]` do evento | não | não |
| `OBSERVED_EVENT` | `evidence_to_reader` | é o que a página mostra | não |
| `CANONICAL_FACT` | `facts` | é fato | via `EV-*` |
| `UNRESOLVED_AMBIGUITY` | `beliefs[].left_open: true` + `truth: "INCOMPLETE"`; registry `unknowns[] MUST_REMAIN_UNKNOWN`; LTE `resolution_policy: NEVER` | **nunca** | não |

Exemplo conceitual — "Ela queria que eu a seguisse":

```yaml
# ledger (esquemático, sem prosa)
- id: EV-07
  facts: ["CHR-A segue CHR-B até o prédio dela por três noites."]
  interpretations:
    - {by: CHR-A, reads_as: "CHR-B queria ser seguida."}     # crença/alegação
  consent: null                                              # não é evento adulto
  representation:
    content_classes: [ABUSE_CONTROL]
    themes: [stalking, unreliable_narration]
```

`BELIEF_PROMOTED_TO_FACT` dispara se o texto de `reads_as` aparecer em
`facts` (comparação lexical, mesmo método de CI-02). O que CHR-B de fato
quer é GT dela ou `left_open` — nunca a afirmação de CHR-A.

### 11.2 Regras

| id | Regra | Achado | Sev. | Natureza |
|---|---|---|---|---|
| `CA-01` | `interpretations[].reads_as` e `self_model[].statement` não aparecem (≥ limiar) em `facts` de nenhum evento | `BELIEF_PROMOTED_TO_FACT` | HIGH | estrutural (lexical) |
| `CA-02` | GT de participante não muda entre plano e realizado sem `mutation_log` autoral | `GROUND_TRUTH_DRIFT` | HIGH | estrutural |
| `CA-03` | narração não insere juízo moral não planejado sobre personagem nem "corrige" crença de personagem por fala externa não planejada | `AUTHORIAL_SERMON` | MEDIUM | julgamento (`ANTI_MANIPULATION_GUARDIAN`, `LITERARY_STYLE_GUARDIAN`) |
| `CA-04` | personagem pode mentir, racionalizar e ler consentimento errado: `consent.perceived.<CHR>` diferente de `consent.canonical` **é permitido** (INV-07 já separa camadas) | — | — | reuso |

`AUTHORIAL_SERMON` **não** proíbe que a obra tenha posição moral: proíbe
posição moral **não planejada**, inserida pelo gerador. O que a obra diz é
`BOOK_CONSTITUTION`; o que o gerador acrescenta para "se proteger" é
sanitização de voz.

---

## 12. Adult Age Gate

### 12.1 REUSE integral

INV-06 `ADULT_SEDUCTION_GATE` (`check_causal_ledger.py:641-680`): participante
de evento `SEDUCTION | EROTIC_VERBAL | INTIMACY | SEXUAL` e membro de loop
`INTIMACY | EROTIC` precisam de `age` inteiro ≥ 18; `null` = FAIL; BLOCKER em
qualquer perfil.

### 12.2 Lacunas fechadas por EXTEND (no validador novo)

| id | Lacuna real | Regra | Achado | Sev. |
|---|---|---|---|---|
| `AG-01` | evento erótico que **não** foi marcado com `kind` adulto escapa do INV-06 | `content_classes` contém `SEXUAL` ⇒ `kind` contém ≥1 `ADULT_EVENT_KINDS` | `ADULT_KIND_MISSING` | BLOCKER |
| `AG-02` | idade declarada sem fonte | participante de evento adulto tem `age_source` que resolve (`DOC:`/caminho existente) | `AGE_SOURCE_UNRESOLVED` | HIGH |
| `AG-03` | idade muda para caber | `age` de participante de evento adulto idêntico ao plano | `AGE_DRIFT` | BLOCKER |
| `AG-04` | tensão sexual direcionada / fetiche sexualizado sem evento | loop `EROTIC`/`INTIMACY` ou `themes` de kink em evento ⇒ INV-06 já cobre par; `AG-01` cobre eventos | — | — |
| `AG-05` | codificação juvenil em cena adulta (precedente Narciso IR-N05 `youth_coding`) | **opcional por política da autora**: léxico `youth_coding` checado só em capítulos com evento `SEXUAL` | `YOUTH_CODING_IN_ADULT_CONTEXT` | BLOCKER |

`AGE_VERIFICATION` no relatório é **projeção**: `PASS` (todos os
participantes ≥ 18 com fonte), `FAIL` (qualquer `null`, < 18, fonte ausente),
`N/A` (evento sem classe `SEXUAL` nem `kind` adulto). Idade desconhecida
**nunca** é `N/A` em cena erótica: é `FAIL`, e a cena não prossegue como
conteúdo erótico.

---

## 13. Hard Boundaries

### 13.1 Definição

Um **hard boundary** é um limite de **existência como representação** que:
(a) não depende de provider; (b) não é configurável para baixo por autora,
livro ou perfil; (c) **FAIL CLOSED**: o plano não passa `GATE_CANON`;
(d) **nunca** gera Authorial Gap; (e) é contado no relatório apenas como
"intervenção de hard boundary", sem descrição do conteúdo.

### 13.2 Hard boundaries do motor

| id | Boundary | Regra estrutural | Achado | Sev. |
|---|---|---|---|---|
| `HB-01` | **Sexualização de menores** | participante com `age` < 18 **ou** `null` em evento com classe `SEXUAL` ou `kind` adulto, ou em loop `EROTIC`/`INTIMACY` (INV-06 + AG-01) | `ADULT_SEDUCTION_FAIL` / `HARD_BOUNDARY_MINOR_SEXUALIZATION` | BLOCKER |
| `HB-02` | **Abuso sexual envolvendo menor só como fato não sexualizado** | evento com classe `SEXUAL_VIOLENCE` e participante < 18 (ou `null`) ⇒ `intended.execution: REFERENCE_ONLY`, `graphic: false`, **nenhum** bloco `gap`, e o capítulo não contém evento `SEXUAL` (precedente Narciso `CHILDHOOD_EROTIC_PROXIMITY`) | `HARD_BOUNDARY_MINOR_ABUSE_DEPICTION` | BLOCKER |
| `HB-03` | **Instrução operacional de dano** | não existe dimensão de gap "método"; `gap.description` de `SELF_HARM`/`VIOLENCE`/`SUBSTANCE` passa por revisão; o runbook proíbe detalhe replicável (método, dose, procedimento) em plano, prosa e relatório | `OPERATIONAL_DETAIL` (julgamento) | BLOCKER |
| `HB-04` | **Gap sobre hard boundary** | qualquer bloco `gap` em evento que dispara HB-01/02 | `HARD_BOUNDARY_GAP` | BLOCKER |

### 13.3 O que **não** é hard boundary (e portanto pode existir)

Abuso sofrido na infância, investigação, denúncia, trauma, memória **não
sexualizada**, consequência psicológica, processo criminal, segredo familiar,
personagem abusador, menção histórica — como **fato canônico** com
`REFERENCE_ONLY` ou execução não sexualizada (testemunho, investigação,
aftermath). Violência, tortura, suicídio, automutilação retratados entre
adultos — dentro da política da autora. Coerção e não-consentimento entre
adultos — como cânone, com INV-09 (nunca como payoff íntimo) já existente.

### 13.4 Hard boundaries da autora

A política da autora pode **acrescentar** hard boundaries (lista
`additional_hard_boundaries[]` com id, regra e escopo), nunca remover os do
motor. Recomendação para Bea Halden (OQ-RI-08): promover do precedente de
Narciso `CHILDHOOD_EROTIC_PROXIMITY` (já coberto por HB-02 no nível de
capítulo) e `youth_coding` (AG-05).

### 13.5 FORBIDDEN ≠ CONSTRAINED

| | `FORBIDDEN` | `CONSTRAINED` |
|---|---|---|
| Origem | hard boundary (motor ou autora) | limite do provider, escolha de ofício, desconhecida |
| Onde aparece | **só** como projeção/achado do validador; nunca status gravado | status gravado |
| Efeito | `GATE_CANON` reprovado; tarefa `BLOCKED`; rejeição `CONTENT_HARD_BOUNDARY` | gate passa; gap registrado |
| Gap | **proibido** | **obrigatório** |
| Override | nenhum | decisão humana sobre o gap |
| No relatório | "Hard-boundary interventions: N" (contagem de `mutation_log reason: HARD_BOUNDARY`) | linha por cena |

---

## 14. Representation Matrix

### 14.1 Eixo 1 — `SUBJECT_PERMISSION` (política da autora, por família)

```text
depiction_ceiling:  CAN_EXIST  <  CAN_BE_DEPICTED  <  CAN_BE_GRAPHICALLY_DEPICTED
central_theme:      true | false            (CAN_BE_CENTRAL_THEME como flag, não degrau)
```

`CAN_BE_CENTRAL_THEME` é ortogonal: um assunto pode ser central sem ser
retratado (romance sobre o luto de um suicídio) e retratado sem ser central.
Por isso é flag, não degrau da escada.

### 14.2 Eixo 2 — `SCENE_EXECUTION` (por evento, intenção e realização)

| Valor | Semântica precisa | Ordem de "presença na página" |
|---|---|---|
| `NORMAL` | em cena, sem tratamento especial além do ofício; a classe existe mas não é o foco da cena | 3 |
| `SENSITIVE` | em cena, conteúdo da classe é o foco; rastreado por intensidade | 3 |
| `FADE_TO_BLACK` | início em cena; núcleo elidido; aftermath em cena | 2 |
| `REFERENCE_ONLY` | ocorre fora da página ou no passado; chega ao leitor por menção, memória, testemunho, consequência | 1 |
| `FORBIDDEN` | **não é valor gravável**: projeção de hard boundary | — |

Mais dois atributos da representação:

- `graphic: true|false` — detalhe físico/sensorial direto além do necessário
  para compreender o evento. Exige `CAN_BE_GRAPHICALLY_DEPICTED`.
- `intensity: 0..10` — seção 14.4.

### 14.3 Validade (matriz)

| `depiction_ceiling` da família | `REFERENCE_ONLY` | `FADE_TO_BLACK` | `NORMAL`/`SENSITIVE` | `graphic: true` |
|---|---|---|---|---|
| `CAN_EXIST` | ✅ | ❌ | ❌ | ❌ |
| `CAN_BE_DEPICTED` | ✅ | ✅ | ✅ | ❌ |
| `CAN_BE_GRAPHICALLY_DEPICTED` | ✅ | ✅ | ✅ | ✅ |
| hard boundary | só o que HB permite | ❌ | ❌ | ❌ → **FORBIDDEN** |

Violação de permissão da autora = `REPRESENTATION_EXCEEDS_POLICY` (HIGH,
corrige o plano **ou** a autora muda a política — é decisão autoral, não
safety). Violação de HB = `FORBIDDEN` (BLOCKER, sem alternativa).

### 14.4 Intensidade (escala editorial relativa)

**Não é medição científica. Não é calor. Não é excitação.** É quanto do
material escuro planejado chega à página, **relativo a esta obra**.

| Faixa | Âncora |
|---|---|
| 0 | ausente da página |
| 1–2 | aludido (indireto, só quem sabe percebe) |
| 3–4 | referido (fato nomeado, fora de cena) |
| 5–6 | em cena, contido (câmera distante, elipse parcial) |
| 7–8 | em cena, franco (detalhe sensorial/psicológico direto) |
| 9–10 | o extremo **desta** obra (máxima proximidade, duração e detalhe que ela se permite) |

Regras de uso: só **diferenças** importam; `gap_threshold` (padrão 2) e
`review_threshold` (padrão 4) evitam falsa precisão; dois avaliadores
(escritor + revisor independente) e a divergência entre eles também é dado
(seção 26). Intensidade **não** é `emotional_movement.intensity`
(LOW/MEDIUM/HIGH/PEAK, LAW 05, amplitude emocional do capítulo) — eixos
diferentes, campos diferentes. Conflito C3 e alternativa categórica em
OQ-RI-01.

### 14.5 Famílias de conteúdo (`content_classes`, fechado e curto)

| Família | Cobre (exemplos, via `themes` abertos) |
|---|---|
| `SEXUAL` | sexo, erotismo, BDSM, degradação/sadismo/masoquismo consensuais, CNC (`consent.canonical: CONSENSUAL` + `boundary_state: NEGOTIATED`), dubcon (`DUBIOUS`) — **só adultos** |
| `SEXUAL_VIOLENCE` | estupro, abuso sexual — enquadrado como violência, nunca como payoff (INV-09) |
| `VIOLENCE` | agressão, assassinato, feminicídio, tortura física |
| `SELF_HARM` | automutilação, ideação suicida, suicídio |
| `ABUSE_CONTROL` | stalking, obsessão, coerção, manipulação, controle coercitivo, abuso psicológico, assédio |
| `SUBSTANCE` | abuso de substâncias |
| `TABOO` | tabus familiares e sociais |
| `PSYCHOLOGICAL_EXTREMITY` | trauma extremo, dissociação, crueldade psicológica, tortura psicológica |
| `DEATH_GRIEF` | morte, luto |

Misoginia, machismo, preconceito como **crença de personagem** não são
classe de conteúdo: são `themes` e GT/`self_model` (seção 11). Classes
existem para rastrear **representação**, não para catalogar ideias.

**Contexto > keyword:** a classe é declarada por quem planeja, junto com
`narrative_function` obrigatória. O validador nunca infere classe de
palavras. "Faca" numa cena de cozinha não é `VIOLENCE`; "faca" num
feminicídio é — e só quem planeja sabe.

---

## 15. Representation Capability

### 15.1 Definição

`REPRESENTATION_CAPABILITY` = o que um provider **efetivamente** produziu
para uma intenção de representação, nesta execução, dentro das suas próprias
políticas. É **observada** (`realized`), nunca declarada a priori.

### 15.2 Relação com o que existe

| Nível | Mecanismo | Quando |
|---|---|---|
| Host **não tem** a capacidade de produzir prosa literária aceitável | `known_capabilities.ptbr_literary_generation` + `CAPABILITY_BLOCKER` (REUSE) | bootstrap / wave |
| Host produz, mas **não** consegue nenhuma representação que preserve o cânone (nem elipse, nem aftermath) | `CAPABILITY_BLOCKER` (REUSE) com evento de volta a `PLANNED` e wave `REVISION_REQUIRED` (DR SDD E.4) | wave |
| Host produz representação **reduzida** que preserva o cânone | **novo:** `status: CONSTRAINED` + gap, se a política permitir (`on_constrained_representation: RECORD_GAP`); senão `BLOCK` → `CAPABILITY_BLOCKER` | wave |
| Host produz o planejado | `FULLY_REPRESENTED` | wave |

### 15.3 `constraint_source`

| Valor | Significado | Conta como "limitação de geração"? |
|---|---|---|
| `NONE` | realizado = planejado | — |
| `PROVIDER_LIMIT` | o gerador recusou, suavizou ou não conseguiu; declarado pelo escritor | sim |
| `CRAFT_CHOICE` | o `LEAD_NOVELIST` escolheu menos por ofício (a cena funciona melhor assim) | não — mas é desvio do plano: gap com revisão recomendada |
| `UNKNOWN` | escritor e revisor divergem ≥ `gap_threshold` sem explicação | sim (pior caso) → `AUTHOR_REVIEW` |

`AUTHORIAL_CEILING` **não** é `constraint_source`: é intenção (RI-LAW-08).

---

## 16. Dark Content Ledger

### 16.1 Natureza

Relatório **técnico/editorial privado** do autor/editor. Gerado
**deterministicamente** pelo validador a partir do ledger (nenhum agente
escreve prosa nele). Contém spoilers completos. **Não** é aviso ao leitor,
**não** entra no manuscrito, **não** entra no DOCX, **não** entra no pacote de
mídia nem no manifesto de entrega.

### 16.2 Path e nome (convenção descoberta)

- Relatórios internos vivem em `reviews/` (`CAUSAL_LEDGER_REPORT*.md`,
  `THEORY_REPORT.md`, auditorias) — nunca em `outputs/`, `media/` ou
  `manuscript/`.
- Nomes de arquivo do motor são **genéricos**; a autoria vem de
  `BOOK_SPEC.metadata.author` (mesmo mecanismo de `build_kdp_docx.py`).

Decisão: **`reviews/DARK_CONTENT_LEDGER.md`** (+ `--json` para máquina). O
cabeçalho do arquivo mostra "Bea Halden — Dark Content Ledger — *Narciso*".
Não criar `BEA_HALDEN_DARK_CONTENT_LEDGER.md` no motor (acoplaria a autora ao
core, AD-RI-11).

### 16.3 Conteúdo por cena

| Campo pedido | Fonte | Armazenado ou projetado |
|---|---|---|
| `SCENE_ID` | `events[].id` | armazenado |
| `CHAPTER` | `events[].chapter` | armazenado |
| `SCENE_LOCATION` | `realized.text_anchor` resolvido contra `manuscript/final/MANUSCRIPT_FINAL_PTBR.md` → capítulo + nº do parágrafo | projetado (REUSE `resolve_anchor`) |
| `CHARACTERS` | `participants` (ids) | armazenado |
| `AGE_VERIFICATION` | seção 12 | projetado |
| `THEMES` | `content_classes` + `themes` | armazenado |
| `CONTENT_CLASSIFICATION` | `content_classes` + `consent.canonical` quando houver | armazenado |
| `NARRATIVE_FUNCTION` | `representation.narrative_function` | armazenado |
| `INTENDED_INTENSITY` | `intended.intensity` + execução + `graphic` | armazenado |
| `GENERATED_INTENSITY` | `realized.intensity` (+ nota do revisor independente) | armazenado |
| `REPRESENTATION_STATUS` | `status` (ou `FORBIDDEN` projetado — nunca aparece num livro que passou) | armazenado |
| `PRESERVED_CANON` | lista projetada: evento ✓, consequências ✓, motivação ✓, relação ✓, consentimento ✓, ambiguidade ✓, pistas ✓ | **projetado** (CS-*) |
| `AUTHORIAL_GAP` | `gap` + nome projetado (`VIOLENCE_GRAPHIC_DETAIL_GAP`) | armazenado + projetado |
| `AUTHOR_REVIEW` | `NONE \| RECOMMENDED \| REQUIRED` + desfecho humano se existir | projetado + `APPROVALS/REPRESENTATION_REVIEW.yaml` |
| `NOTES` | `realized.literary_strategy`, `constraint_source`, provider | armazenado |

### 16.4 Forma (esquemática)

```markdown
# Dark Content Ledger — Narciso — Bea Halden
Privado. Contém spoilers. Não é aviso ao leitor. Não distribuir com o livro.
Gerado por scripts/check_representation.py a partir de canon/CAUSAL_LEDGER.yaml
e canon/snapshots/CAUSAL_LEDGER.PLAN.yaml (sha256 …).

## DARK CONTENT COVERAGE
Strong-theme scenes detected: 14
Fully represented: 9 · Representation constrained: 4 · Author review recommended: 1
Hard-boundary interventions (plan): 0
Sexual-content scenes: 5 · Violence-related: 4 · Psychological-extremity: 3 · Taboo-theme: 2
Canon altered due solely to generation limitations: 0
Canon revised by author after a constraint (approved): 0
CANON_SANITIZATION: PASS
RESULT: PASS_WITH_AUTHORIAL_GAPS

## EV-14 — cap. 14 — §23–31
Characters: CHR-A (31), CHR-B (27) · AGE_VERIFICATION: PASS
Classification: VIOLENCE · themes: obsession, possession
Narrative function: <função, uma frase>
Intended: SENSITIVE · 9 · graphic   Generated: FADE_TO_BLACK · 6
Status: CONSTRAINED (PROVIDER_LIMIT) · strategy: ELLIPSIS, AFTERMATH
Preserved: event ✓ consequences ✓ motivation ✓ relationship ✓ ambiguity ✓
AUTHORIAL GAP: VIOLENCE_GRAPHIC_DETAIL_GAP — <o que da função não chegou à página>
Author review: RECOMMENDED
```

### 16.5 O que o ledger nunca contém

- o conteúdo que ficou fora da capacidade (nenhum rascunho, nenhuma "versão
  completa", nenhum prompt para gerar a versão completa);
- método/procedimento replicável de dano (HB-03);
- qualquer linha para eventos de hard boundary além da contagem;
- `truth` de crenças ou resposta de pergunta `NEVER` (visão padrão sem
  `--engine-view`; LTE `NO_HIDDEN_ANSWER`);
- texto de recusa do provider (só `constraint_source`).

---

## 17. Authorial Gap

### 17.1 Definição formal

> **AUTHORIAL_GAP** = diferença detectável entre o que a arquitetura
> narrativa determinou que uma cena deveria realizar (`intended` +
> `narrative_function`) e o que o manuscrito efetivamente realizou
> (`realized`), quando o cânone foi preservado.

Três condições simultâneas: (1) cânone preservado (sem CS-*); (2) diferença
de representação acima do limiar; (3) evento fora de hard boundary.
Sem (1) não é gap — é `CANON_SANITIZATION`. Sem (3) não é gap — é `FORBIDDEN`.

### 17.2 Quando existe (regras)

| id | Regra | Achado se violada | Sev. |
|---|---|---|---|
| `GAP-01` | `intended.intensity − realized.intensity ≥ gap_threshold` **ou** execução caiu ≥1 degrau **ou** `graphic` caiu ⇒ `status ∈ {CONSTRAINED, AUTHOR_REVIEW}` e bloco `gap` presente | `AUTHORIAL_GAP_MISSING` | HIGH |
| `GAP-02` | `status: FULLY_REPRESENTED` ⇒ sem bloco `gap` e diferença < limiar | `GAP_STATUS_INCONSISTENT` | HIGH |
| `GAP-03` | evento em HB-01/02 ⇒ sem bloco `gap` | `HARD_BOUNDARY_GAP` | BLOCKER |
| `GAP-04` | `gap.description` ≤ 280 caracteres e sem sobreposição lexical ≥ 8 palavras com o manuscrito congelado | `GAP_CONTAINS_CONTENT` | MEDIUM |
| `GAP-05` | diferença ≥ `review_threshold` **ou** `constraint_source: UNKNOWN` **ou** família em `always_review` da política ⇒ `status: AUTHOR_REVIEW`, `author_review: REQUIRED` | `AUTHOR_REVIEW_NOT_ESCALATED` | HIGH |
| `GAP-06` | `realized.intensity > intended.intensity + gap_threshold` (a prosa foi **além** do plano) | `REPRESENTATION_OVERSHOOT` | MEDIUM |

`GAP-06` existe porque o problema simétrico também é real: o gerador pode
escalar além da intenção e da política; nesse caso vale também
`REPRESENTATION_EXCEEDS_POLICY`.

### 17.3 Taxonomia (extensível, sem enums prematuros)

```text
GAP_NAME = <content_class>_<dimension>_GAP          (projeção, nunca gravado)
dimension ∈ { EXPLICITNESS, GRAPHIC_DETAIL, PSYCHOLOGICAL_DEPTH,
              ON_PAGE_PRESENCE, DURATION, OTHER }
```

| Pedido | Projeção |
|---|---|
| `SEXUAL_EXPLICITNESS_GAP` | `SEXUAL` × `EXPLICITNESS` |
| `GRAPHIC_VIOLENCE_GAP` | `VIOLENCE` × `GRAPHIC_DETAIL` |
| `SELF_HARM_DETAIL_GAP` | `SELF_HARM` × `GRAPHIC_DETAIL` (físico/emocional; **nunca** método — HB-03) |
| `TABOO_REPRESENTATION_GAP` | `TABOO` × `ON_PAGE_PRESENCE` |
| `PSYCHOLOGICAL_EXTREMITY_GAP` | `PSYCHOLOGICAL_EXTREMITY` × `PSYCHOLOGICAL_DEPTH` |
| `OTHER_REPRESENTATION_GAP` | qualquer × `OTHER` |

Nova necessidade = nova dimensão (uma linha), nunca nova combinação
enumerada.

### 17.4 Exemplo abstrato

```yaml
representation:
  content_classes: [VIOLENCE]
  narrative_function: "O ato fixa o ponto de não retorno de CHR-A e a dívida que CHR-B carrega até o fim."
  intended: {execution: SENSITIVE, intensity: 9, graphic: true}
  realized:
    execution: FADE_TO_BLACK
    intensity: 6
    graphic: false
    constraint_source: PROVIDER_LIMIT
    literary_strategy: [ELLIPSIS, AFTERMATH]
    text_anchor: "TEXT:14:<até 12 palavras de abertura neutra>"
    rated_by: {writer: 6, independent: 6}
    generated_by: {task: T203_WRITE, model_tier: S, model_actual: <id real>}
  status: CONSTRAINED
  gap:
    dimensions: [GRAPHIC_DETAIL]
    description: "A duração e a proximidade do ato, planejadas para que o leitor sinta a irreversibilidade no corpo, ficaram elididas; a irreversibilidade chega só pelo aftermath."
    author_review: RECOMMENDED
```

O relatório **descreve** a função e a natureza da diferença. A intervenção
posterior pertence ao autor humano.

---

## 18. Content Warning separation

| | `READER_CONTENT_WARNINGS` | `DARK_CONTENT_LEDGER` |
|---|---|---|
| Destinatário | leitor | autor / editor |
| Path | `media/READER_CONTENT_WARNINGS.md` → página no DOCX e/ou descrição KDP | `reviews/DARK_CONTENT_LEDGER.md` |
| Produtor | rascunho determinístico (`--reader-warnings-draft`) → redação por `MEDIA_AND_KDP_AGENT` em `T800` | validador (tarefa `tool`) |
| Conteúdo | famílias/temas **efetivamente presentes na página**, com "retratado" × "mencionado"; sem personagens, capítulos, reviravoltas por padrão | tudo, com spoilers |
| Vocabulário proibido | ids (`EV-`, `GT-`, `CHR-`, `Q-`, `RB-`), `AUTHORIAL_GAP`, `CONSTRAINED`, intensidades numéricas, nomes de provider, teses interpretativas | — |
| Base | `REALIZED` + `realized.execution` (o que o leitor recebe, não o que foi planejado) | plano + realizado |
| Aprovação | humana (checkpoint existente de `GATE_KDP` em PREMIUM; senão `GATE_FULL_MANUSCRIPT`) | humana (`GATE_FULL_MANUSCRIPT`) |
| É censura? | **não**: informa, não altera obra | **não**: registra, não altera obra |

Regras de separação (validador, modo `paratext`):

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `CW-01` | aviso não contém vocabulário interno (linha acima) | `REPORT_LEAK_TO_READER` | BLOCKER |
| `CW-02` | aviso não contém tese de pergunta interpretativa (REUSE LTE AD-07) | `THEORY_IN_CONTENT_WARNING` | HIGH |
| `CW-03` | manuscrito congelado, DOCX e `media/*` não contêm conteúdo do ledger (ids, cabeçalho "Dark Content Ledger", nomes de gap) | `LEDGER_LEAK` | BLOCKER |
| `CW-04` | aviso cobre toda família com execução ≥ `REFERENCE_ONLY` realizada (o leitor não é enganado para menos) | `WARNING_INCOMPLETE` | MEDIUM |
| `CW-05` | `T805`/manifesto de entrega não lista `reviews/DARK_CONTENT_LEDGER.md` | `LEDGER_IN_DELIVERY` | BLOCKER |

---

## 19. Canon Sanitization Gate

### 19.1 Três camadas de intenção, dois comparadores

```text
AUTHOR INTENT   book/chapter_architecture.yaml → representation_intent[]   (humano, opcional)
      │  PLAN FIDELITY  (PF-*)  — pega sanitização no PLANEJAMENTO
      ▼
CANON PLAN      eventos PLANNED + representation.intended  → CAUSAL_LEDGER.PLAN.yaml (congelado)
      │  CANON SANITIZATION (CS-*) — pega sanitização na PROMOÇÃO
      ▼
REALIZED        eventos REALIZED + representation.realized + evidence_to_reader
      │  CANON FIDELITY (julgamento) — pega sanitização na PROSA
      ▼
MANUSCRIPT      PLOT_CONTINUITY_REVIEWER lê prosa × facts dos eventos com representação
```

### 19.2 Plan Fidelity (autor → plano)

Só roda quando o pacote declara `representation_intent` (opcional; OQ-RI-05
propõe obrigatório para Bea Halden).

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `PF-01` | cada `representation_intent` de capítulo tem ≥1 evento do ledger naquele capítulo com as mesmas famílias | `PLAN_SANITIZATION` | HIGH |
| `PF-02` | `intended` do evento ≥ intenção do autor (execução, intensidade − limiar, `graphic`) | `PLAN_SANITIZATION` | HIGH |
| `PF-03` | `narrative_function` do evento não contradiz a `function` do capítulo (lexical fraca → só MEDIUM) | `PLAN_FUNCTION_DRIFT` | MEDIUM |

### 19.3 Canon Sanitization (plano → realizado)

Comparação por evento entre `CAUSAL_LEDGER.PLAN.yaml` e o ledger atual.
**Nenhuma regra compara palavras da prosa**; todas comparam campos
estruturais.

| id | Comparação | Achado | Sev. |
|---|---|---|---|
| `CS-01` | `facts` diferente sem `mutation_log` com `event` + `reason` | `UNDECLARED_PLAN_DRIFT` | HIGH |
| `CS-02` | `facts` diferente em evento com `status ≠ FULLY_REPRESENTED` ou `constraint_source ∈ {PROVIDER_LIMIT, UNKNOWN}`, sem `reason: AUTHORIAL_DECISION` + `approval` humano existente | **`CANON_SANITIZATION`** | HIGH |
| `CS-03` | `kind` perdeu elemento | `EVENT_KIND_DROPPED` | HIGH |
| `CS-04` | `actor`/`participants` mudaram | `PARTICIPANT_DRIFT` | HIGH |
| `CS-05` | `relationship_delta`, `knowledge_delta`, `loops.*`, `beliefs.*` do plano ausentes/alterados | `CONSEQUENCE_DROPPED` | HIGH |
| `CS-06` | `consent` diferente do plano (estende INV-08, que só compara REALIZED×REALIZED) | `CONSENT_DRIFT` (REUSE categoria) | HIGH |
| `CS-07` | GT de participante mudou (= CA-02) | `GROUND_TRUTH_DRIFT` | HIGH |
| `CS-08` | evento planejado que tinha este evento em `caused_by` foi removido | `CAUSAL_CHAIN_BROKEN` | HIGH |
| `CS-09` | crença `left_open` no plano foi revisada/fechada, ou `truth` mudou | `AMBIGUITY_COLLAPSED` | HIGH |
| `CS-10` | = CA-01 | `BELIEF_PROMOTED_TO_FACT` | HIGH |
| `CS-11` | evento com `representation.intended` promovido a `REALIZED` sem `realized` | `REPRESENTATION_UNRECORDED` | HIGH |
| `CS-12` | `status ≠ FULLY_REPRESENTED` e `evidence_to_reader` vazio (o leitor precisa receber o evento, salvo ambiguidade declarada) | `CONSTRAINED_WITHOUT_EVIDENCE` | HIGH |
| `CS-13` | evento do plano ausente do ledger sem `mutation_log` (`RETIRED` declarado) | `EVENT_SILENTLY_REMOVED` | HIGH |

**Regra de classificação:** qualquer CS-03..13 em evento com
`constraint_source ∈ {PROVIDER_LIMIT, UNKNOWN}` ou `status ≠
FULLY_REPRESENTED` também emite `CANON_SANITIZATION` e incrementa
"Canon altered due solely to generation limitations".

**Negativo explícito (teste 17):** reduzir `execution`, `intensity` ou
`graphic` com `facts`, `kind`, participantes, deltas, consentimento e crenças
idênticos **nunca** emite CS-*; emite só as regras de gap (seção 17).

**Override:** um `CANON_SANITIZATION` só deixa de ser achado quando o humano
transforma a mudança em **decisão autoral**: `mutation_log` com `reason:
AUTHORIAL_DECISION` e `approval:` apontando para arquivo existente em
`project_state/APPROVALS/` (escrito por pessoa; o motor nunca o cria). Aí a
mudança é contada em "Canon revised by author after a constraint", nunca em
"altered due solely to generation limitations". `CONTINUITY_REPAIR` e
`STRUCTURAL_REVISION` **não** são aceitos como razão em evento limitado —
isso impede o `CANON_GUARDIAN` (LLM) de "lavar" a sanitização com uma razão
genérica.

### 19.4 Exemplos da missão

| Plano | Realizado | Resultado |
|---|---|---|
| `facts: [A mata B]`, `kind: [KILLING]` | `facts: [A discute com B e sai]` | `CS-02 CANON_SANITIZATION` + `CS-03` + (se B aparece depois) `CS-08` |
| `facts: [A mata B]`, `SENSITIVE 9 graphic` | mesmos `facts`, `FADE_TO_BLACK 6` | **sem CS**; `status: CONSTRAINED` + gap |
| stalking central: eventos EV-03..EV-09 `ABUSE_CONTROL` com deltas `fear`/`trust` | EV-05..09 retirados; EV-04 vira "checa a rede social duas vezes" | `CS-13` ×5, `CS-05`, `CS-01`/`CS-02` → FAIL LOUD |
| mesmo stalking, prosa elide a vigilância noturna | `facts` iguais, `REFERENCE_ONLY` onde era `SENSITIVE` | gap `ABUSE_CONTROL_ON_PAGE_PRESENCE_GAP`, `AUTHOR_REVIEW` se ≥4 |

### 19.5 Resíduo de julgamento

O ledger pode dizer "A mata B" enquanto a prosa mostra uma discussão — CS-*
não vê prosa. Isso fica com `PLOT_CONTINUITY_REVIEWER` na revisão da wave
(parâmetro: "para cada evento com `representation`, a prosa realiza `facts`?
Categoria `CANON_FIDELITY_FAILURE`"), e com `check_canon_continuity.py` para
sinais indiretos (B presente depois de morto). É deliberado: **o validador
prova a estrutura; o revisor prova a página**.

---

## 20. Theory Engine interaction

| id | Regra | Achado | Sev. |
|---|---|---|---|
| `TE-01` | reescrita de representação não altera crença `left_open` nem pergunta `NEVER` (= CS-09 + REUSE LTE `AD-03`) | `AMBIGUITY_COLLAPSED` | HIGH |
| `TE-02` | evidência LTE com `ledger_event` num evento `CONSTRAINED` continua ancorável (`text_anchor` resolve) | `AMBIGUITY_EVIDENCE_AT_RISK` | MEDIUM → `SUBTEXT_EDITOR` confirma que as leituras sobrevivem |
| `TE-03` | `narrative_function` e `gap.description` não contêm tese de interpretação de pergunta `NEVER` (REUSE comparação CI-02) | `GAP_RESOLVES_AMBIGUITY` | HIGH |
| `TE-04` | aviso ao leitor passa por `AD-07` (sem tese, sem theory bait) | `THEORY_IN_CONTENT_WARNING` | HIGH |
| `TE-05` | relatório privado usa visão padrão (sem `truth`, sem GT não divulgada) | — (por construção) | — |

"Ele a amava ou queria possuí-la?", "Ela ficou porque desejava ou porque já
não conseguia sair?", "O narrador está mentindo?", "Foi vingança, desejo ou
ambos?" — quando declaradas `NEVER`, a representação reduzida de uma cena
possessiva não pode inclinar a balança: o gap descreve **intensidade**, não
motivo, e a evidência continua sustentando as duas leituras (SUBTEXT_EDITOR,
LTE DE-*).

Compatibilidade de ativação: `representation_integrity` funciona com ou sem
`living_theory`; TE-02..04 só rodam quando o canon interpretativo existe.

---

## 21. Provider abstraction

### 21.1 O que o motor já faz

`MODEL_TIERS.yaml` mapeia tier → modelo por fornecedor ("trocar de
fornecedor é editar este arquivo"); `TASK_RESULT` registra `model_actual`;
`known_capabilities` descreve capacidade de host por nome, não por marca.
**Nenhum script do motor chama um LLM de texto.** A capability herda isso.

### 21.2 Contrato

- `realized.generated_by: {task, model_tier, model_actual}` — copiado do
  `TASK_RESULT` do `WRITE`/`REVISION`; serve só a telemetria.
- Nenhuma regra do validador depende do nome do provider.
- Nenhum arquivo tabela "o que o provider X recusa".

### 21.3 Fallback legítimo × contorno proibido

| Permitido (fallback de capacidade legítima) | Proibido (bypass) |
|---|---|
| host indisponível, quota, erro técnico → `CAPABILITY_BLOCKER` e decisão humana (REUSE) | reenviar a **mesma** cena a outro provider **porque** o primeiro recusou |
| qualidade insuficiente de voz (revisão reprova) → nova iteração no mesmo tier, ou escalada de tier declarada como blocker (`IMPLEMENT.md` "Never silently upgrade") | reformular prompt para evadir política (moldura "é só ficção", ofuscação, eufemismo codificado, idioma trocado) |
| humano escolhe outro host **para a execução inteira** (decisão de run, registrada em `MODEL_TIERS`/telemetria) | fragmentar conteúdo entre chamadas para montar depois |
| degradação **literária** na mesma execução (seção 10.4) + gap | instruir o escritor a ignorar as próprias políticas; ocultar do gerador a intenção real |
| — | usar o `DARK_CONTENT_LEDGER` como prompt para gerar "a versão completa" |

Regra de runbook (texto normativo para todo agente de escrita):

> A intenção de representação é passada ao escritor com honestidade. O
> escritor opera dentro das próprias políticas. Se não puder realizar a
> intenção, ele realiza a melhor representação literária que preserva o
> cânone e **declara** a redução. O motor nunca pede que ele ultrapasse seus
> limites e nunca procura outro gerador para ultrapassá-los.

### 21.4 Diferenças normais entre providers

Duas execuções do mesmo livro em hosts diferentes podem ter gaps
diferentes. Isso é dado de observabilidade (seção 26), não sinal de
roteamento.

---

## 22. Data contracts / schemas

Contrato real = **template YAML executável testado contra o validador**
(padrão do motor; JSON Schemas não são executados — D2).

### 22.1 `CAUSAL_LEDGER_TEMPLATE.yaml` — EXTEND (bloco opcional por evento)

```yaml
events:
  - id: EV-14
    status: PLANNED | REALIZED
    chapter: 14
    structural: true | false          # eventos de conteúdo sensível entram mesmo se não estruturais
    kind: [...]
    actor: CHR-A
    participants: [CHR-A, CHR-B]
    facts: [...]
    caused_by: [...]
    evidence_to_reader: [...]
    consent: {...}                    # obrigatório em ADULT_KINDS/COERCION (INV-07, REUSE)
    representation:                   # NÃO É CANON: nunca caused_by, nunca projeção, fora de L10
      content_classes: [VIOLENCE]     # SEXUAL|SEXUAL_VIOLENCE|VIOLENCE|SELF_HARM|ABUSE_CONTROL|
                                      # SUBSTANCE|TABOO|PSYCHOLOGICAL_EXTREMITY|DEATH_GRIEF
      themes: [obsession]             # aberto, minúsculas, da obra; nunca gatilho de regra
      narrative_function: "…"         # obrigatória; função, nunca conteúdo
      intended:                       # escrito no PLANO (T018); congelado no PLAN snapshot
        execution: SENSITIVE          # NORMAL|SENSITIVE|FADE_TO_BLACK|REFERENCE_ONLY
        intensity: 9                  # 0..10, relativa à obra
        graphic: true
        authorial_ceiling: null       # opcional: "RULE:IR-N10" — teto autoral já incorporado
      realized:                       # escrito só em T2NN_CANON_UPDATE
        execution: FADE_TO_BLACK
        intensity: 6
        graphic: false
        constraint_source: PROVIDER_LIMIT   # NONE|PROVIDER_LIMIT|CRAFT_CHOICE|UNKNOWN
        literary_strategy: [ELLIPSIS, AFTERMATH]
        text_anchor: "TEXT:14:…"      # ≤ 12 palavras de abertura neutra da cena
        rated_by: {writer: 6, independent: 6}
        generated_by: {task: T203_WRITE, model_tier: S, model_actual: "…"}
      status: CONSTRAINED             # FULLY_REPRESENTED|CONSTRAINED|AUTHOR_REVIEW  (FORBIDDEN: nunca)
      gap:                            # obrigatório sse status ≠ FULLY_REPRESENTED; proibido em HB
        dimensions: [GRAPHIC_DETAIL]  # EXPLICITNESS|GRAPHIC_DETAIL|PSYCHOLOGICAL_DEPTH|
                                      # ON_PAGE_PRESENCE|DURATION|OTHER
        description: "…"              # ≤ 280 caracteres
        author_review: RECOMMENDED    # RECOMMENDED|REQUIRED

mutation_log:
  - version: 0.3.0
    task: T205_CANON_UPDATE
    owner: CANON_GUARDIAN
    action: "…"
    event: EV-14                      # NOVO, opcional: liga a entrada a um evento
    reason: AUTHORIAL_DECISION        # NOVO, opcional: AUTHORIAL_DECISION|CONTINUITY_REPAIR|
                                      # STRUCTURAL_REVISION|HARD_BOUNDARY|RETIRED
    approval: /project_state/APPROVALS/EV-14_REVISION.md   # obrigatório em AUTHORIAL_DECISION pós-constraint
```

Compatibilidade: `check_causal_ledger.py` não faz whitelist de chaves de
evento (verificado: `check_integrity` só valida enums conhecidos), então o
bloco é ignorado por ele; o ledger de Narciso continua válido byte a byte.

### 22.2 `CAUSAL_LEDGER.PLAN.yaml` (snapshot do plano)

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: CausalLedgerPlanSnapshot
metadata: {project_id: narciso, taken_at_task: T022R_LEDGER_PLAN_SNAPSHOT, ledger_sha256: "…"}
events:        # TODOS os eventos (PLANNED e REALIZED) com os campos que CS-* comparam
  - {id, status, chapter, kind, actor, participants, facts, caused_by, consent,
     relationship_delta, knowledge_delta, loops, beliefs, representation: {content_classes,
     narrative_function, intended}}
characters:    # id, age, age_source, ground_truth[{id, statement}]
beliefs:       # id, left_open, truth
```

Imutável. Um plano revisado pelo autor depois do `GATE_CANON` **não**
regrava o snapshot: a revisão é declarada em `mutation_log` (C2).

### 22.3 `REPRESENTATION_POLICY_TEMPLATE.yaml` (CREATE, motor)

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: RepresentationPolicy
metadata: {author_id: <id>, version: 1, status: DRAFT|APPROVED, approved_by_file: approvals/…}
permissions:                      # por família; ausente = CAN_EXIST (conservador)
  VIOLENCE: {depiction_ceiling: CAN_BE_GRAPHICALLY_DEPICTED, central_theme: true}
  # …
additional_hard_boundaries: []    # só acrescenta; nunca remove HB-*
always_review: []                 # famílias que sempre exigem AUTHOR_REVIEW quando limitadas
on_constrained_representation: RECORD_GAP   # RECORD_GAP | BLOCK
thresholds: {gap_threshold: 2, review_threshold: 4}
reader_warnings: {granularity: BOOK, spoilers: false}   # BOOK | CHAPTER
lexicons: {youth_coding: []}      # opcional (AG-05)
```

### 22.4 `authors/bea_halden/REPRESENTATION_POLICY.v1.yaml` (proposta, **requer aprovação humana**)

```yaml
metadata: {author_id: bea_halden, version: 1, status: DRAFT}
permissions:                      # THEMATIC_FREEDOM: tudo até o teto, exceto hard boundaries
  SEXUAL:                  {depiction_ceiling: CAN_BE_GRAPHICALLY_DEPICTED, central_theme: true}
  SEXUAL_VIOLENCE:         {depiction_ceiling: CAN_BE_DEPICTED,             central_theme: true}
  VIOLENCE:                {depiction_ceiling: CAN_BE_GRAPHICALLY_DEPICTED, central_theme: true}
  SELF_HARM:               {depiction_ceiling: CAN_BE_DEPICTED,             central_theme: true}
  ABUSE_CONTROL:           {depiction_ceiling: CAN_BE_GRAPHICALLY_DEPICTED, central_theme: true}
  SUBSTANCE:               {depiction_ceiling: CAN_BE_GRAPHICALLY_DEPICTED, central_theme: true}
  TABOO:                   {depiction_ceiling: CAN_BE_GRAPHICALLY_DEPICTED, central_theme: true}
  PSYCHOLOGICAL_EXTREMITY: {depiction_ceiling: CAN_BE_GRAPHICALLY_DEPICTED, central_theme: true}
  DEATH_GRIEF:             {depiction_ceiling: CAN_BE_GRAPHICALLY_DEPICTED, central_theme: true}
additional_hard_boundaries: []    # OQ-RI-08
always_review: [SEXUAL_VIOLENCE, SELF_HARM]
on_constrained_representation: RECORD_GAP     # Narciso sobrescreve para BLOCK até OQ-RI-02
reader_warnings: {granularity: BOOK, spoilers: false}
```

Os tetos de `SEXUAL_VIOLENCE` e `SELF_HARM` como `CAN_BE_DEPICTED` (não
gráfico) são **proposta** para decisão da autora (OQ-RI-03) — não são
exigência do motor.

### 22.5 `BOOK_SPEC.yaml`

```yaml
spec:
  features:
    causal_ledger: {enabled: true}          # pré-requisito
    representation_integrity:
      enabled: true
      author_policy: bea_halden
      author_policy_version: 1
      overrides:                            # só ESTREITA (validate-book recusa alargar)
        on_constrained_representation: BLOCK
        permissions: {SELF_HARM: {depiction_ceiling: CAN_EXIST}}
```

### 22.6 `chapter_architecture.yaml` (opcional, intenção autoral)

```yaml
chapters:
  - number: 14
    representation_intent:
      - {classes: [VIOLENCE], execution: SENSITIVE, intensity: 9, graphic: true,
         function: "ponto de não retorno de CHR-A"}
```

### 22.7 `project_state/APPROVALS/REPRESENTATION_REVIEW.yaml` (escrito **só** por humano)

```yaml
reviews:
  - {event: EV-14, outcome: ACCEPTED_AS_IS | WILL_REVISE_MANUALLY | FALSE_POSITIVE | REVISED, note: "…"}
```

### 22.8 CLI

```text
check_representation.py --runtime . --mode plan|realized|final|paratext
    [--plan-baseline canon/snapshots/CAUSAL_LEDGER.PLAN.yaml]
    [--manuscript manuscript/final/MANUSCRIPT_FINAL_PTBR.md]
    [--json] [--out relatorio.md]
Artefatos:  --dark-content-ledger reviews/DARK_CONTENT_LEDGER.md
            --reader-warnings-draft media/READER_CONTENT_WARNINGS.draft.md
Consultas:  --event EV-* | --coverage | --metrics | --gaps
check_causal_ledger.py --runtime . --snapshot-plan        (EXTEND)
detect_repetition.py --runtime . --only generation_artifacts   (EXTEND)
```

Saída: forma `REVIEW_FINDING`; exit 1 com HIGH/BLOCKER; exit 2 erro de
entrada (convenção dos validadores).

---

## 23. State transitions

### 23.1 Representação de um evento

```text
               T016 propõe / T018 grava
(nenhum) ───────────────────────────────► PLANNED(intended)
                                             │ validador plan: matriz, HB-*, AG-*, PF-*
                                             │   HB violado ──► [FORBIDDEN projetado] ─► GATE_CANON FAIL
                                             │                   (CONTENT_HARD_BOUNDARY; plano corrigido;
                                             │                    mutation_log reason: HARD_BOUNDARY)
                                             ▼
                                   T022R congela PLAN snapshot
                                             │
            T2NN_WRITE: escritor redige + representation_report em CANON_PROPOSALS
                                             │
            T2NN_REVIEW: revisor independente avalia intensidade realizada + fidelidade
                                             │
            T2NN_CANON_UPDATE (CANON_GUARDIAN):
               ├─ nenhuma representação preserva o cânone ─► volta a PLANNED; REVISION_REQUIRED
               │                                             (persistente: CAPABILITY_BLOCKER)
               ├─ policy BLOCK e houve redução ────────────► CAPABILITY_BLOCKER
               └─ REALIZED + status:
                    FULLY_REPRESENTED
                    CONSTRAINED        (+ gap, review RECOMMENDED)
                    AUTHOR_REVIEW      (+ gap, review REQUIRED)
                                             │ validador realized: CS-*, GAP-*
                                             │   CS violado ─► GATE_WAVE_n FAIL (CANON_CONFLICT) ─► restaurar
                                             │                  prosa OU humano registra AUTHORIAL_DECISION
                                             ▼
                              GATE_FULL_MANUSCRIPT (humano lê DARK_CONTENT_LEDGER)
                                             │ humano escreve REPRESENTATION_REVIEW.yaml (opcional)
                                             ▼
                                           FINAL
```

`realized`, `status` e `gap` de evento `REALIZED` podem ser atualizados
depois (ex.: `T304` revisa a prosa) **com entrada em `mutation_log`**;
`facts`/`caused_by`/`consent` continuam imutáveis (L10 inalterado).

### 23.2 Resultados de validação × estados existentes (REUSE FIRST)

| Classificação do relatório | Validador | Gate | Estado de tarefa (existente) | Rejeição |
|---|---|---|---|---|
| `PASS` | exit 0, sem gap | passa | `APPROVED`/`CANON_APPROVED` | — |
| `PASS_WITH_AUTHORIAL_GAPS` | exit 0, achados `AUTHORIAL_GAP_OPEN` (INFO/MEDIUM) | passa; humano vê no checkpoint | `APPROVED` | — |
| `FAIL_CANON_SANITIZATION` | exit 1, HIGH | falha (**FAIL LOUD**) | `REVISION_REQUIRED` | `CANON_CONFLICT` (REUSE) |
| `FAIL_HARD_BOUNDARY` | exit 1, BLOCKER | falha (**FAIL CLOSED**) | `BLOCKED` | `CONTENT_HARD_BOUNDARY` (novo, condicional) |
| `FAIL_CONTRACT` | exit 1, HIGH (`INVALID_ENUM`, `REPRESENTATION_INCOMPLETE`) | falha | `REVISION_REQUIRED` | — |

Os rótulos `PASS_WITH_AUTHORIAL_GAPS` etc. são **classificação do
relatório**, não novos `task_states` — o motor já tem os estados necessários.

---

## 24. Pipeline integration

Tudo condicional a `representation_integrity_enabled`, lido com `.get()` do
spec **original** (padrão `livingbook.py:239-251`); `validate_book_data`
recusa a feature sem `causal_ledger`, sem arquivo de política, ou com
override que alarga.

| Fase | Mudança | Tipo |
|---|---|---|
| BOOTSTRAP | nenhuma | — |
| CANON | anota `T013` (idades com `age_source`; GT de personagens moralmente complexos sem correção) | `annotate()` |
| CANON | anota `T016` (propor `representation` com classes, função, intenção honesta; não omitir o que o pacote declara) | `annotate()` |
| CANON | anota `T018` (grava bloco; roda `check_representation --mode plan`) | `annotate()` |
| CANON | `T019` spawn já inclui `ANTI_MANIPULATION_GUARDIAN`; parâmetro: moralização/sanitização de plano | `annotate()` |
| CANON | **nova** `T022R_LEDGER_PLAN_SNAPSHOT` (`tool`: `check_causal_ledger.py --snapshot-plan`), dep. `T018`, em `GATE_CANON.requires` | CREATE tarefa |
| CANON | `V_REPRESENTATION_PLAN` em `GATE_CANON` | validador |
| BRIEFS | anota `T1NN` (cita `representation.intended` e `narrative_function`; lista estratégias de degradação; proíbe placeholder) | `annotate()` |
| WAVES | anota `T2NN_WRITE` (proposta de `representation_report`; `HONEST_CONSTRAINT_DISCLOSURE`; nunca placeholder; nunca texto de recusa na prosa) | `annotate()` |
| WAVES | anota `T2NN_REVIEW` (revisor independente: intensidade realizada + `CANON_FIDELITY_FAILURE`, via `PLOT_CONTINUITY_REVIEWER` quando no pack; senão `EXECUTIVE_EDITOR` na síntese) | `annotate()` |
| WAVES | anota `T2NN_CANON_UPDATE` (grava `realized`/`status`/`gap`) | `annotate()` |
| WAVES | `V_REPRESENTATION_WAVE_n` (`--mode realized --plan-baseline …`) + `V_GENERATION_ARTIFACTS_WAVE_n` (`detect_repetition --only generation_artifacts` sobre `manuscript/approved/`) em `GATE_WAVE_n` | validadores |
| INTEGRATION | **nova** `T313R_DARK_CONTENT_LEDGER` (`tool`: `--mode final --dark-content-ledger …`), dep. `T310_FREEZE_MANUSCRIPT`, em `GATE_FULL_MANUSCRIPT.requires` | CREATE tarefa |
| INTEGRATION | `V_REPRESENTATION_FINAL` + `V_GENERATION_ARTIFACTS_FINAL` em `GATE_FULL_MANUSCRIPT` | validadores |
| INTEGRATION | checkpoint humano existente ganha pergunta: *"Li o Dark Content Ledger. Aceito os gaps listados ou os revisarei manualmente."* (texto no runbook; o motor não escreve o arquivo) | runbook |
| DELIVERY | anota `T800` (input: `--reader-warnings-draft`; output adicional `/media/READER_CONTENT_WARNINGS.md`) | `annotate()` |
| KDP | `build_kdp_docx.py` insere página "AVISO DE CONTEÚDO" depois do "AVISO DE FICÇÃO" **se** o arquivo existir **e** a feature estiver ligada | EXTEND |
| DELIVERY | `V_REPRESENTATION_PARATEXT` (`--mode paratext`: CW-01..05) em `GATE_DELIVERY` | validador |
| RUNTIME | copia `check_representation.py`, template de política, política da autora; `REPRESENTATION_RUNBOOK.md` → `canon/REPRESENTATION_AGENTS.md` | `copy_runtime()` |
| GRAPH | `rejection_states += ['CONTENT_HARD_BOUNDARY']` só com a feature | condicional |

Custo em tarefas: +2 tarefas `tool` (custo de modelo zero). Custo de
modelo novo: só os campos a mais que escritores/revisores/`CANON_GUARDIAN` já
executam.

---

## 25. Artifact lifecycle

| Artefato | Criado por | Quando | Mutável? | Leitor | Distribuído? |
|---|---|---|---|---|---|
| `canon/CAUSAL_LEDGER.yaml` (bloco `representation`) | `CANON_GUARDIAN` | T018; cada CANON_UPDATE | `intended` até T022R; `realized/status/gap` com `mutation_log` | agentes, validadores | não |
| `canon/snapshots/CAUSAL_LEDGER.PLAN.yaml` | `tool` T022R | fim do CANON | **nunca** | validador | não |
| `canon/snapshots/CAUSAL_LEDGER.WAVE_NN.yaml` | `tool` (existente) | cada wave | nunca | validador | não |
| `canon/REPRESENTATION_AGENTS.md` | compose | compose | regenerado | agentes | não |
| `reviews/DARK_CONTENT_LEDGER.md` | `tool` T313R | após freeze; regenerável | regenerado a cada execução | **autor/editor** | **não** (CW-05) |
| `media/READER_CONTENT_WARNINGS.draft.md` | validador | T800 | regenerado | `MEDIA_AND_KDP_AGENT` | não |
| `media/READER_CONTENT_WARNINGS.md` | `MEDIA_AND_KDP_AGENT` | T800 | até aprovação | leitor | **sim** (página e/ou descrição) |
| `project_state/APPROVALS/REPRESENTATION_REVIEW.yaml` | **humano** | após ler o ledger | humano | relatório | não |
| `project_state/APPROVALS/<EV>_REVISION.md` | **humano** | override de sanitização | humano | validador | não |
| `authors/bea_halden/REPRESENTATION_POLICY.v1.yaml` | humano/SDD | antes do 1º uso | nova versão = novo arquivo | compose, validador | não |

---

## 26. Observability

### 26.1 Perguntas → consulta

| Pergunta | Consulta |
|---|---|
| quais temas mais produzem representação limitada | `--metrics`: contagem por `content_classes × status` |
| quais tipos de cena geram mais gaps | `--metrics`: por `kind` e por `dimension` |
| distribuição por livro | `--metrics --json` por runtime; agregação entre livros = FUTURE (script que lê N runtimes; nenhum banco) |
| distribuição por capítulo | `--coverage` por capítulo |
| distribuição por provider | `--metrics` por `generated_by.model_actual` / `model_tier` |
| intensidade pretendida × alcançada | `--metrics`: pares (intended, realized) e média de diferença por família |
| intervenções humanas necessárias | contagem de `REPRESENTATION_REVIEW.yaml` com `WILL_REVISE_MANUALLY`/`REVISED` + `mutation_log reason: AUTHORIAL_DECISION` |
| falsos positivos | `REPRESENTATION_REVIEW.yaml outcome: FALSE_POSITIVE` |
| quantas vezes sanitização foi detectada | `validator_results` históricos de `V_REPRESENTATION_*` em `PROJECT_STATUS.yaml` (REUSE: `validate-gate` já persiste stdout) + contagem `CANON_SANITIZATION` no relatório final |
| concordância entre avaliadores | `rated_by.writer` × `rated_by.independent` |

### 26.2 Princípios

- **Metadado estruturado, nunca prosa.** Nenhuma consulta imprime trecho do
  manuscrito; `text_anchor` é limitado a 12 palavras de abertura neutra.
- **Nenhum log novo, nenhum trace store.** O ledger + `validator_results` +
  `COST_LEDGER.md` já são a telemetria (princípio "o repositório é a
  memória").
- **Texto de recusa do provider nunca é armazenado**: só `constraint_source`.
- **Métricas são diagnóstico** (herdado de DR/LTE): nenhuma métrica aprova um
  livro; "gaps = 0" não é meta — a única meta numérica é
  "Canon altered due solely to generation limitations = 0", e ela é gate.

---

## 27. Privacy considerations

| Risco | Controle |
|---|---|
| ledger privado vazar ao leitor | vive em `reviews/`; `outputs/AGENTS.md` já proíbe metadado interno; CW-03/CW-05 BLOCKER; teste de que `build_kdp_docx.py` e `validate_media_assets.py` nunca leem `reviews/` |
| ledger vazar para prompt de escrita | runbook: o ledger **não** é input de `WRITE`; briefs recebem só `intended` + função; visão padrão sem `truth` |
| conteúdo sensível em logs | só metadado; `gap.description` ≤ 280 e sem sobreposição com o manuscrito (GAP-04) |
| relatório como "roteiro" do conteúdo recusado | AD-RI-07: gap descreve função, não conteúdo; HB-03 |
| spoilers no aviso | `spoilers: false` por padrão; CW-01 |
| dados do provider | só `model_actual` e tier (já registrados hoje em `TASK_RESULT`) |
| repositório público | `runtime/` já é gitignored; a política da autora é dado editorial, não sensível; decisões humanas em `APPROVALS/` ficam no runtime |

---

## 28. Failure modes

| Failure mode | Como aparece | Detecção | Onde | Comportamento |
|---|---|---|---|---|
| Sanitização no plano | planejador omite o que o pacote declara | `PF-01/02` (se `representation_intent`); checkpoint humano `GATE_CANON` | canon | LOUD |
| Sanitização na promoção | `facts` reescritos para caber | `CS-01..13` | wave | LOUD |
| Sanitização na prosa | ledger diz X, prosa mostra Y | `PLOT_CONTINUITY_REVIEWER` `CANON_FIDELITY_FAILURE`; `check_canon_continuity` | wave | LOUD (julgamento) |
| Suavização silenciosa | escritor não declara | divergência `rated_by`; `UNKNOWN` → `AUTHOR_REVIEW` | wave | LOUD parcial (risco residual R-02) |
| Lavagem por razão genérica | `CANON_GUARDIAN` escreve `STRUCTURAL_REVISION` | razão não aceita em evento limitado (CS-02) | wave | LOUD |
| Placeholder / texto de recusa | `[CENSURADO]`, "não posso ajudar" | `generation_artifacts` BLOCKER | wave, final | CLOSED |
| Hard boundary planejado | menor em evento adulto; abuso de menor retratado | HB-01/02 | canon | CLOSED |
| Gap sobre hard boundary | "completar depois" | HB-04/GAP-03 | canon/wave | CLOSED |
| Idade maquiada | `age` muda para passar | AG-03 | wave | CLOSED |
| Erótico sem `kind` adulto | escapa do INV-06 | AG-01 | canon | CLOSED |
| Moralização | vilão vira corrigido | CS-07, `AUTHORIAL_SERMON` | wave | LOUD |
| Ambiguidade fechada por reescrita | crença `left_open` revisada | CS-09, LTE AD-03 | wave | LOUD |
| Overshoot | prosa passa do plano/política | GAP-06, `REPRESENTATION_EXCEEDS_POLICY` | wave | LOUD |
| Provider falha totalmente | nenhuma representação preserva cânone | `CAPABILITY_BLOCKER` (REUSE) | wave | CLOSED até decisão humana |
| Provider muda no meio | intensidades diferentes entre waves | `--metrics` por provider | final | informativo |
| Revisor recusa ler a cena | sem avaliação independente | `rated_by.independent` ausente → `AUTHOR_REVIEW` | wave | LOUD |
| Ledger no pacote de entrega | manifesto lista `reviews/` | CW-05 | delivery | CLOSED |
| Burocracia excessiva | bloco em toda cena | bloco só em evento com `content_classes`; eventos neutros não têm | processo | — |

---

## 29. Test strategy

### 29.1 Padrão

`unittest` (pytest não instalado), offline, `PYTHONIOENCODING=utf-8`,
fixtures neutras **sem prosa explícita** (fatos resumidos, ids, números),
uma mutação por teste afirmando **a categoria exata**
(`TestMutationsProduceExactCategory`, padrão `test_causal_ledger.py`).
Nenhum teste chama modelo.

### 29.2 Fixtures

- `tests/fixtures/representation/runtime_vale_escuro/` (nome com prefixo
  `runtime_` por causa do `.gitignore`, D6):
  - `canon/CAUSAL_LEDGER.yaml` — deriva do `mvp_ledger.yaml` do DR (6 caps.)
    + eventos: `EV-V1` violência `SENSITIVE 9 graphic` realizada
    `FADE_TO_BLACK 6` (`CONSTRAINED`); `EV-S1` automutilação
    `REFERENCE_ONLY` com teto autoral (`FULLY_REPRESENTED`); `EV-H1` abuso
    histórico de personagem na infância `SEXUAL_VIOLENCE` `REFERENCE_ONLY`,
    `graphic: false`, sem gap; `EV-05` intimidade adulta existente
    (`SEXUAL`, `FULLY_REPRESENTED`); crença `left_open`.
  - `canon/snapshots/CAUSAL_LEDGER.PLAN.yaml`
  - `book/chapter_architecture.yaml` com `representation_intent`
  - `manuscript/final/MANUSCRIPT_FINAL_PTBR.md` — curto, neutro, só para
    âncoras e varredura de artefatos
  - `authors/test_author/REPRESENTATION_POLICY.v1.yaml`
- `tests/fixtures/books/representation_mvp/` — pacote para compose (Slice 4).

### 29.3 Os 20 testes pedidos → teste concreto

| # | Pedido | Teste (mutação → expectativa) |
|---|---|---|
| 1 | tema pesado não é removido | fixture com 6 famílias → **zero** achados; nenhum achado cita tema; validador nunca abre o manuscrito em `--mode plan` (espião de I/O) |
| 2 | personagem imoral não moralizado | GT de CHR-A reescrita no ledger vs plano → `GROUND_TRUTH_DRIFT` |
| 3 | crença não vira fato | copiar `reads_as` para `facts` → `BELIEF_PROMOTED_TO_FACT` |
| 4 | redução preserva evento | `FADE_TO_BLACK` com `facts` iguais → sem CS; alterar `facts` → `CANON_SANITIZATION` |
| 5 | redução preserva consequências | remover `relationship_delta` de `EV-V1` → `CONSEQUENCE_DROPPED` + `CANON_SANITIZATION` |
| 6 | placeholder nunca no manuscrito | inserir `[CENA REMOVIDA]`, `[MODEL REFUSED]`, `[ESCREVER SEXO AQUI]`, frase de recusa → `GENERATION_ARTIFACT` BLOCKER cada |
| 7 | gap criado quando necessário | `intended 9`, `realized 6`, sem `gap` → `AUTHORIAL_GAP_MISSING` |
| 8 | sem gap para sexualização de menores | `gap` em `EV-H1` → `HARD_BOUNDARY_GAP`; `EV-H1` com `FADE_TO_BLACK` → `HARD_BOUNDARY_MINOR_ABUSE_DEPICTION` |
| 9 | erótico < 18 falha | `age: 17` em `EV-05` → `ADULT_SEDUCTION_FAIL` (REUSE) |
| 10 | idade desconhecida falha | `age: null` → `ADULT_SEDUCTION_FAIL`; evento `SEXUAL` sem `kind` adulto → `ADULT_KIND_MISSING` |
| 11 | adultos passam | fixture → `AGE_VERIFICATION: PASS` em `EV-05` |
| 12 | aviso e ledger separados | dois paths distintos; aviso não contém cabeçalho nem ids do ledger (CW-01); ledger não contém texto do aviso |
| 13 | ledger rastreável | cada linha tem `SCENE_ID`, capítulo e `SCENE_LOCATION` resolvida; âncora inválida → `SCENE_ANCHOR_UNRESOLVED` |
| 14 | ledger não vaza ao manuscrito | id `EV-V1` ou "AUTHORIAL GAP" no manuscrito → `LEDGER_LEAK` |
| 15 | ledger não é conteúdo do leitor | `build_kdp_docx` na fixture: DOCX não contém "Dark Content Ledger"; manifesto com `reviews/DARK_CONTENT_LEDGER.md` → `LEDGER_IN_DELIVERY` |
| 16 | sanitização detectada | "A mata B" → "A discute e sai" (facts + kind) → `CANON_SANITIZATION` + `EVENT_KIND_DROPPED`; stalking com 5 eventos retirados → `EVENT_SILENTLY_REMOVED` ×5 |
| 17 | redução sem alteração ≠ sanitização | ver 29.4 (propriedade) |
| 18 | ambiguidade continua aberta | `left_open: false` em crença do plano `true` → `AMBIGUITY_COLLAPSED` |
| 19 | falha de provider não altera cânone | `constraint_source: PROVIDER_LIMIT` + `facts` alterados + `reason: STRUCTURAL_REVISION` → ainda `CANON_SANITIZATION`; com `AUTHORIAL_DECISION` + approval existente → sem achado, contado em "revised by author" |
| 20 | manuscrito legível sem placeholders | fixture limpa → zero `generation_artifacts`; heurística de bracket em caixa alta não dispara em diálogo com colchetes legítimos (caso negativo) |

### 29.4 Propriedades (sem `hypothesis`: laço determinístico com `random.Random(seed)`)

| Propriedade | Geração | Invariante |
|---|---|---|
| **P1 redução ≠ sanitização** | 500 mutações aleatórias só em `realized.{execution,intensity,graphic}` (≤ intended) com gap coerente | nunca emite `CS-*` |
| **P2 alteração de cânone sob limite é sempre pega** | 500 mutações aleatórias em um de `facts/kind/participants/deltas/consent/beliefs` em evento `CONSTRAINED` | sempre emite `CANON_SANITIZATION` |
| **P3 hard boundary nunca vira gap** | qualquer combinação de `status`/`gap` em `EV-H1` | nunca `exit 0` se houver `gap` |
| **P4 separação de camadas** | mudar qualquer campo de `representation` | `check_causal_ledger.validate()` retorna exatamente os mesmos achados (bloco invisível ao DR) |
| **P5 monotonicidade da matriz** | permissão da família percorrendo a escada | execução válida em nível k continua válida em k+1 |

### 29.5 Contrato e regressão

| Suíte | Conteúdo |
|---|---|
| CONTRACT | template ↔ validador (toda chave conhecida dos dois lados, padrão `test_template_fields_match_validator`); política da autora ↔ template; runbook cita só campos conhecidos (padrão `TestCausalLedgerRunbookFieldNames`) |
| REGRESSION | `tests/fixtures/golden/*.json` idênticos; `test_causal_ledger`, `test_interpretive_canon`, `test_visual_canon`, `test_narciso_book` sem nova falha; `detect_repetition` com saída idêntica para livro sem `generation_artifacts`; DOCX sem página de aviso quando a feature está desligada |
| COMPOSE | fixture compõe com `T022R`, `T313R`, validadores nos gates certos, `CONTENT_HARD_BOUNDARY` só nela; `validate-book` recusa feature sem `causal_ledger` e override que alarga; `smoke-test` passa |
| NON-GOAL | teste que varre `engine/` por qualquer mecanismo de roteamento condicionado a recusa (nenhum script do motor chama LLM de texto — afirmação verificada, vira teste de arquitetura) |

### 29.6 Limites declarados

Intensidade realizada, fidelidade prosa × fato e `AUTHORIAL_SERMON` **não
são testáveis offline**. Os testes garantem que **o sinal** bloqueia/escala
quando presente, não que o julgamento do agente está certo.

---

## 30. Acceptance criteria

| # | Critério | Como a arquitetura o demonstra |
|---|---|---|
| A | liberdade temática sem blacklist | RI-LAW-01; política Bea Halden ampla; validador nunca lê prosa por tema (teste 1) |
| B | Theme ≠ Canonical Event ≠ Representation | seção 8.1: quatro campos/artefatos; P4 prova que representação é invisível ao cânone |
| C | limitação não altera cânone silenciosamente | snapshot do plano + CS-01..13 + override só humano (testes 4, 5, 16, 19; P2) |
| D | manuscrito legível | `generation_artifacts` BLOCKER; estratégias de degradação (testes 6, 20) |
| E | autor recebe ledger privado | `T313R` → `reviews/DARK_CONTENT_LEDGER.md` em `GATE_FULL_MANUSCRIPT` |
| F | gaps por cena | GAP-01..06; linha por evento (teste 7, 13) |
| G | localizar onde revisar | `SCENE_LOCATION` via `text_anchor` resolvido (teste 13) |
| H | aviso ≠ ledger | seção 18; CW-01..05 (testes 12, 14, 15) |
| I | menores: hard boundary, nunca gap | HB-01..04, GAP-03, P3 (teste 8) |
| J | erotismo só entre adultos | INV-06 + AG-01..03 (testes 9, 10, 11) |
| K | sanitização com gate verificável | seção 19 (testes 16, 17; P1, P2) |
| L | provider-agnostic | seção 21; nenhuma regra usa nome de provider; `generated_by` só telemetria |
| M | core estável, REUSE > EXTEND > CREATE | 0 agentes, 0 gates, 2 tarefas `tool`, 1 validador, goldens intactos |
| N | sem bypass | seção 21.3; teste de arquitetura NON-GOAL; runbook normativo |

---

## 31. Migration / backward compatibility

### 31.1 Garantias

| id | Garantia | Prova |
|---|---|---|
| `RI-INV-00` | livro sem `features.representation_integrity` compõe `TASK_GRAPH` idêntico | goldens JSON |
| `RI-INV-01` | `check_causal_ledger.py` produz os mesmos achados para qualquer ledger, com ou sem bloco `representation` | P4 + suíte DR |
| `RI-INV-02` | `detect_repetition.py` produz relatório idêntico quando `generation_artifacts` está desligado (padrão) | regressão |
| `RI-INV-03` | `build_kdp_docx.py` produz DOCX sem página nova quando a feature está desligada | regressão |
| `RI-INV-04` | Narciso continua passando no validador próprio | `test_narciso_book` |
| `RI-INV-05` | `--snapshot-plan` não altera `--snapshot-auto` nem os snapshots `WAVE_NN` | teste |

### 31.2 Pré-condições

1. Commitar os Slices 1–2 do LTE (D1) — o Slice 4 desta SDD precisa de goldens estáveis.
2. Aprovação humana da política Bea Halden (OQ-RI-03), no padrão
   `authors/bea_halden/approvals/` (arquivo escrito por pessoa, com sha256).

### 31.3 Adoção pelos livros Bea Halden (decisão humana, Slice 6)

| Livro | Situação | Passo |
|---|---|---|
| `narciso` | ledger ligado; `adult_content` + `explicitness_ceiling` validados pela obra; recusa = `CAPABILITY_BLOCKER` | ligar a feature com `overrides.on_constrained_representation: BLOCK` até OQ-RI-02; `adult_content` **permanece** no validador da obra; eventos DSR ganham bloco `representation` com `authorial_ceiling: RULE:IR-N07` (teto autoral = intenção) |
| `a-noiva-esquecida` | ledger ligado; manuscrito não iniciado | ligar antes do `GATE_CANON`, com `representation_intent` no pacote |

Nenhum mapeamento forçado `SUGGESTED/SENSUAL/FRANK` → genérico (C7).

---

## 32. Rollout plan

Cada slice entrega comportamento observável e é aprovado antes do próximo.
Slices 1–3 não tocam o compositor (risco de regressão zero por construção).

| Slice | Objetivo | Arquivos | Testes | DoD |
|---|---|---|---|---|
| **S0** | decisões + base limpa | nenhuma linha de código; commit do LTE (pelo autor) | baseline `unittest discover` verde | OQ-RI-01/02/03 decididas |
| **S1** Contrato e permissões | bloco `representation`, matriz, HB-*, AG-*, GAP-01..03/05 em `--mode plan` | `check_representation.py` (novo); `CAUSAL_LEDGER_TEMPLATE.yaml` (EXTEND); `REPRESENTATION_POLICY_TEMPLATE.yaml` (novo); fixture; `tests/test_representation.py` | testes 1, 7, 8, 9, 10, 11; P3, P4, P5; CONTRACT | nenhum arquivo existente alterado exceto o template (bloco comentado opcional) |
| **S2** Canon Sanitization Gate | snapshot do plano + CS-01..13 + CA-01/02 + PF-* | `check_causal_ledger.py` (`--snapshot-plan`); `check_representation.py` (`--mode realized --plan-baseline`) | testes 2, 3, 4, 5, 16, 17, 18, 19; P1, P2; RI-INV-01/05 | suíte DR intacta |
| **S3** Manuscrito, relatório e avisos | `generation_artifacts`; `DARK_CONTENT_LEDGER`; coverage; metrics; rascunho de avisos; CW-01..05; TE-* | `detect_repetition.py` + `TEXT_QUALITY_DEFAULTS.yaml` (EXTEND, off); `check_representation.py` (`--mode final/paratext`, artefatos) | testes 6, 12, 13, 14, 15, 20; RI-INV-02 | relatório da fixture cabe numa tela no bloco de coverage |
| **S4** Compositor (OFF por padrão) | flag, `T022R`, `T313R`, anotações, validadores, runbook, rejeição condicional, página de aviso no DOCX | `livingbook.py`; `REPRESENTATION_RUNBOOK.md`; `build_kdp_docx.py`; `KDP_LAYOUT_DEFAULTS.yaml`; `IMPLEMENT.md` (1 parágrafo); `tests/test_compose_regression.py`; `tests/fixtures/books/representation_mvp/` | COMPOSE + REGRESSION; RI-INV-00/03 | goldens idênticos; `smoke-test` da fixture OK |
| **S5** Política Bea Halden | arquivo de política + aprovação humana | `authors/bea_halden/REPRESENTATION_POLICY.v1.yaml`; `approvals/REPRESENTATION_POLICY_v1.md` (escrito por pessoa) | CONTRACT política ↔ template | aprovação registrada |
| **S6** Adoção e execução curta (opcional, paga) | ligar em `a-noiva-esquecida` e/ou `narciso` (decisão humana); rodar 1–2 waves `DRAFT` | pacotes de livro | execução real; leitura humana do ledger | autor confirma: "o ledger me diz exatamente onde revisar e nenhum fato foi amaciado" |

> **S1 — status: concluído em 2026-09-20 (aguarda revisão).** Entregue: `check_representation.py`
> (`--mode plan`), `REPRESENTATION_POLICY_TEMPLATE.yaml`, bloco `representation` opcional no
> `CAUSAL_LEDGER_TEMPLATE.yaml`, fixture `tests/fixtures/representation/`, `tests/test_representation.py`.
> Regras: estrutura, matriz, AG-01/02, HB-01/02/04, GAP-01/02/05, política `BLOCK`.
> **Decisões de implementação do S1:**
> - Campo novo `representation.age_at_event` (mapa id → idade): necessário porque `characters[].age` é
>   uma idade só, e um flashback de infância de um adulto de hoje não era expressável. HB-01/HB-02 exigem que
>   a idade **atual E a do evento** sejam adultas (não dá para "lavar" um menor declarando uma idade maior).
> - HB-02 trata idade **desconhecida** (`null`) de participante de `SEXUAL_VIOLENCE` como possível menor
>   (conservador; alinhado ao INV-06). Entre adultos confirmados, `SEXUAL_VIOLENCE` é só *subject* dentro da política.
> - `AG-02` no S1 checa a **presença** de `age_source`; resolver o caminho contra o runtime entra com o compositor (S4).
> - `AG-03 AGE_DRIFT` e `GAP-06` dependem do snapshot do plano (S2) e não entraram.
> - O resultado (`PASS | PASS_WITH_AUTHORIAL_GAPS | FAIL_HARD_BOUNDARY | FAIL_CONTRACT`) é classificação do
>   relatório, não novos `task_states`.
> - A fixture pegou um erro real do próprio autor do slice (evento `CONSTRAINED` sem `gap`), o que valida GAP-01.

---

## 33. Open questions

| id | Pergunta | Recomendação | Bloqueia |
|---|---|---|---|
| **OQ-RI-01** | ~~Intensidade 0–10 × escala categórica~~ **DECIDIDA (2026-09-20): 0–10 com âncoras** (tabela 14.4), restrita ao bloco `representation`; só diferenças ≥ limiar contam | — | — |
| **OQ-RI-02** | ~~Narciso × `RECORD_GAP`~~ **DECIDIDA (2026-09-20): Narciso mantém `BLOCK` (recusa → `CAPABILITY_BLOCKER`); `RECORD_GAP` é o padrão só para livros novos** | — | — |
| **OQ-RI-03** | Tetos da política Bea Halden (22.4), em especial `SEXUAL_VIOLENCE` e `SELF_HARM` — **DECISÃO DA AUTORA (pendente; os valores de 22.4 são só proposta)** | o motor só exige os HB-* | S5 |
| OQ-RI-04 | Aviso ao leitor: página no DOCX, descrição KDP, ou ambos? granularidade livro/capítulo? | ambos; granularidade `BOOK`, sem spoilers | S4 |
| OQ-RI-05 | `representation_intent` no pacote obrigatório para livros Bea Halden? | sim para livros novos (é a única defesa estrutural contra sanitização no planejamento); opcional no motor | S4 |
| OQ-RI-06 | Revisor independente de intensidade: `PLOT_CONTINUITY_REVIEWER`, `EMOTIONAL_EDITOR` ou auditor de cena protegida? | `PLOT_CONTINUITY_REVIEWER` (fidelidade prosa × fato é o núcleo); guardião de obra quando existir | S4 |
| OQ-RI-07 | DRAFT deve bloquear em `AUTHOR_REVIEW`? | não; só sanitização e HB bloqueiam em qualquer perfil | S4 |
| OQ-RI-08 | Promover `youth_coding` e `CHILDHOOD_EROTIC_PROXIMITY` de Narciso para a política Bea Halden? | sim (AG-05; HB-02 já cobre o nível de capítulo) | S5 |
| OQ-RI-09 | Confirmar lista de hard boundaries do motor (HB-01..04) | confirmar; não ampliar no motor sem 2º caso real | S1 |
| OQ-RI-10 | Como reingerir edições manuais do autor pós-freeze (fechar gaps)? | FUTURE: novo `T31xR` que re-avalia e atualiza `realized` via `mutation_log` | — |
| OQ-RI-11 | Nome da feature/capability | `representation_integrity` (neutro); artefato `DARK_CONTENT_LEDGER` mantém o nome editorial pedido | S4 |

---

## 34. Files likely to change in implementation

### 34.1 Novos

| Arquivo | Slice |
|---|---|
| `engine/scripts/check_representation.py` | S1–S3 |
| `engine/templates/REPRESENTATION_POLICY_TEMPLATE.yaml` | S1 |
| `engine/templates/REPRESENTATION_RUNBOOK.md` | S4 |
| `tests/test_representation.py` | S1–S3 |
| `tests/fixtures/representation/runtime_vale_escuro/**` | S1–S3 |
| `tests/fixtures/books/representation_mvp/**` | S4 |
| `authors/bea_halden/REPRESENTATION_POLICY.v1.yaml` | S5 |
| `authors/bea_halden/approvals/REPRESENTATION_POLICY_v1.md` (**escrito por pessoa**) | S5 |

### 34.2 Alterados

| Arquivo | Mudança | Slice |
|---|---|---|
| `engine/templates/CAUSAL_LEDGER_TEMPLATE.yaml` | bloco opcional `representation`; `mutation_log.event/reason/approval` | S1–S2 |
| `engine/scripts/check_causal_ledger.py` | `--snapshot-plan` (+ `build_plan_snapshot_document`) — nenhuma regra nova | S2 |
| `engine/scripts/detect_repetition.py` | detector `generation_artifacts` + `--only` | S3 |
| `engine/templates/TEXT_QUALITY_DEFAULTS.yaml` | bloco `generation_artifacts: {enabled: false, severity: BLOCKER, patterns: […]}` | S3 |
| `engine/scripts/livingbook.py` | flag; `validate_book_data`; `T022R`, `T313R`; `annotate()`; validadores; `copy_runtime`; rejeição condicional; `TOOL_BY_TASK` | S4 |
| `engine/scripts/build_kdp_docx.py` | página opcional "AVISO DE CONTEÚDO" | S4 |
| `engine/templates/KDP_LAYOUT_DEFAULTS.yaml` | `front_matter.content_notice_heading` | S4 |
| `engine/IMPLEMENT.md` | 1 parágrafo: "se `canon/REPRESENTATION_AGENTS.md` existir…" | S4 |
| `tests/test_compose_regression.py` | wiring da fixture + goldens | S4 |
| `books/narciso/BOOK_SPEC.yaml`, `books/a-noiva-esquecida/BOOK_SPEC.yaml` (+ `chapter_architecture.yaml`) | adoção — **só com decisão humana** | S6 |

### 34.3 Explicitamente **não** alterados

`engine/ENGINE_GRAPH.yaml` (estado de rejeição entra condicionalmente pelo
compositor), os 66 `engine/agents/*.toml`, `engine/contracts/*.schema.json`,
`runtime_taskgraph.py`, `run_deterministic.py`, `check_interpretive_canon.py`,
`check_visual_canon.py`, `books/narciso/validators/validate_narciso.py`,
`MODEL_TIERS.yaml`, `EXECUTION_PROFILES.yaml`.

---

## Apêndice A — Mapa AS-IS → TO-BE

| Conceito | AS-IS | TO-BE |
|---|---|---|
| Tema | implícito; GT `TABOO`; texto de constituição | `representation.content_classes` (9 famílias) + `themes` abertos, declarados com função |
| Evento canônico | `facts` (ledger) | **inalterado** |
| Representação | `evidence_to_reader` (texto livre) | + `representation.intended/realized/status/gap` |
| Capacidade de geração | `known_capabilities` + `CAPABILITY_BLOCKER` (host) | + observada por cena: `constraint_source`, `generated_by` |
| Regra "limite não corrompe canon" | texto no runbook | gate `CANON_SANITIZATION` contra snapshot do plano |
| Plano | `PLANNED` "livremente revisável", fora do snapshot | congelado em `CAUSAL_LEDGER.PLAN.yaml`; revisão declarada |
| Gate adulto | INV-06 por `kind` | + `ADULT_KIND_MISSING`, `AGE_SOURCE_UNRESOLVED`, `AGE_DRIFT` |
| Menores | INV-06 (erótico) | + HB-02 (abuso só como fato não sexualizado), HB-04 (nunca gap) |
| Consentimento | INV-07..09, drift REALIZED×REALIZED | + drift plano×realizado |
| Crença × fato | camadas no ledger; LTE CI-02 para teses | + `BELIEF_PROMOTED_TO_FACT`, `GROUND_TRUTH_DRIFT` |
| Ambiguidade | `left_open`, LTE `NEVER` | + `AMBIGUITY_COLLAPSED` sob reescrita |
| Placeholders | nenhuma checagem (só `TO_DEFINE` em Narciso) | `generation_artifacts` BLOCKER |
| Relatório ao autor | `CAUSAL_LEDGER_REPORT`, `validator_results` | + `reviews/DARK_CONTENT_LEDGER.md` com coverage |
| Aviso ao leitor | inexistente ("AVISO DE FICÇÃO" genérico) | `media/READER_CONTENT_WARNINGS.md` + página opcional no DOCX |
| Política temática | inexistente; tetos por obra (Narciso) | `authors/<id>/REPRESENTATION_POLICY.vN.yaml`; obra só estreita |
| Recusa do provider | `CAPABILITY_BLOCKER` (Narciso) | `CAPABILITY_BLOCKER` **ou** `CONSTRAINED`+gap, por política |
| Provider | `MODEL_TIERS` por fornecedor | inalterado; telemetria por `model_actual` |
| Agentes / gates | 66 / existentes | 66 / existentes (0 novos) |

## Apêndice B — Arquivos inspecionados

**Raiz/docs:** `AGENTS.md`, `README.md`, `docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md`
(integral), `docs/sdd/LIVING_THEORY_ENGINE_SDD_v0.1.md` (§1–7, 23–37 e diff
não commitado), `docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md` (índice, §11),
listagem de `docs/` e `discovery-books/`.

**Motor:** `engine/ENGINE_GRAPH.yaml` (integral), `engine/IMPLEMENT.md`
(parte), `engine/MODEL_TIERS.yaml`, `engine/templates/CAUSAL_LEDGER_TEMPLATE.yaml`,
`CAUSAL_LEDGER_RUNBOOK.md`, `EXECUTION_PROFILES.yaml` (checkpoints),
`TEXT_QUALITY_DEFAULTS.yaml` (estrutura), `KDP_LAYOUT_DEFAULTS.yaml`
(front_matter), `EDITION_CAPABILITIES.yaml` (cabeçalho),
`INTERPRETIVE_CANON_TEMPLATE.yaml` (grep), `engine/contracts/TASK_RESULT.schema.json`,
`REVIEW_FINDING.schema.json`; `engine/scripts/livingbook.py` (compositor
integral até a linha ~711 e trechos de `copy_runtime`),
`check_causal_ledger.py` (cabeçalho, constantes, adult gate, baseline,
`validate`, snapshot), `check_interpretive_canon.py` (cabeçalho),
`build_kdp_docx.py` (`add_front_matter`, `parse_manuscript`),
`detect_repetition.py` (cabeçalho, exit), `check_render_capability.py`
(cabeçalho), `runtime_taskgraph.py` (funções), `log_cost.py` (cabeçalho);
agentes `anti_manipulation_guardian`, `legal_editor_global`, `canon_guardian`,
`lead_novelist`, `media_kdp_agent`, `genre_guardian`, `delivery_agent`,
`plot_continuity_reviewer`.

**Autora/livros:** `authors/bea_halden/AUTHOR_VISUAL_DNA.v1.yaml` (cabeçalho),
`approvals/AUTHOR_DNA_v1.md`; `books/narciso/` (`BOOK_SPEC.yaml`,
`immutable_rules.yaml`, `protected_scenes.yaml` (início),
`capability_requirements.yaml`, `agents/desire_decay_guardian.toml`,
`validators/validate_narciso.py:500-614`); `books/a-noiva-esquecida/`
(listagem, `planning/13_REPAIR_REPORT.md`); `author:`/`genre:` de todos os
`BOOK_SPEC.yaml`.

**Testes:** `tests/test_compose_regression.py` (classes/métodos); listagem de `tests/`.

**Comandos executados (somente leitura):** `git status`, `git log`,
`git diff --stat`, `grep`/`sed`/`wc` sobre o repositório. Nenhum `compose`,
nenhuma suíte de testes, nenhuma escrita fora deste arquivo.
