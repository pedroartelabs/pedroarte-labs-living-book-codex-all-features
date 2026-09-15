# SDD v0.1 — `BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM`

> **Status:** `READY_FOR_IMPLEMENTATION` (escopo Slices 1–4; Slices 5+ condicionados
> às decisões OQ-1 e OQ-2, ver seção 33). Nenhum código de produção foi escrito
> nesta sessão. Nenhum agente, script, template ou pacote foi criado ou
> alterado. Único arquivo criado: este documento.
>
> **Escopo:** extensão do PEDRO_ARTE_LIVING_BOOK_ENGINE, `engine/ENGINE_GRAPH.yaml`
> versão `1.1.0`, branch `main`, commit `b1bd12b` + working tree com a
> capability `DARK_ROMANCE_CANON_ARCHITECT` implementada e não commitada
> (57 testes offline passando em 2026-09-14).
>
> **Regras aplicadas:** `REUSE > EXTEND > CREATE`, `SIMPLICIDADE SEMPRE`,
> OFF por padrão, nenhum comportamento existente alterado.
>
> **Convenção:** segue `docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md`
> (única SDD do repositório): texto em PT-BR; identificadores, estados,
> enums e invariantes em inglês.
>
> **SDD irmã e dependência conceitual:** `DARK_ROMANCE_CANON_ARCHITECT` (seção
> S daquela SDD registra `DEFAULT_AUTHOR_IDENTITY = BEA_HALDEN`). Esta SDD
> **não** altera nenhuma lei, invariante, gate ou slice daquela.

---

## Índice

1. Title / Status → cabeçalho
2. Context
3. Problem
4. Goals
5. Non-Goals
6. Principles (camada constitucional)
7. Discovery Findings (inclui divergências D-V1..D-V12)
8. Existing Architecture
9. Reuse Analysis (REUSE / EXTEND / CREATE / DO NOT CREATE)
10. Proposed Architecture
11. Domain Model
12. Contracts
13. Canon Hierarchy (precedência e resolução de conflitos)
14. State Model (progressão, memória visual)
15. Edition Model
16. Capability Matrix
17. Cover Model (capa, tipografia, lombada, marca autoral)
18. Chapter Sigils
19. Narrative Artifacts, Endpapers, Edges, Dust Jacket Duality
20. Physical Edition Model (superfícies e acabamentos)
21. KDP Strategy (PRINT_SPEC, geometria)
22. Collector Strategy (manifesto de produção e máscaras)
23. Validation / Gates
24. Failure Modes
25. Observability
26. Security / IP / Human-in-the-loop / Cost
27. Versioning / Determinism
28. Backward Compatibility / Configuration
29. Testing Strategy
30. Worked Example — O CISNE NEGRO (+ segunda obra hipotética)
31. Implementation Slices
32. Risks
33. Open Questions
34. Acceptance Criteria (do SDD e respostas às 20 perguntas críticas)
35. Decision Log
36. Self-Review adversarial
- Apêndice A — Arquivos inspecionados e fontes externas

---

## 2. Context

O motor produz hoje **livros para ler**: manuscrito, uma imagem primária por
capítulo, DOCX de interior KDP, uma capa JPEG de marketing do eBook e cinco
Stories. A identidade visual de cada obra vive em prosa
(`books/<slug>/visual_profile.md` → `living_book/VISUAL_LIFE_SPEC.md`,
`IMAGE_BIOME.md`, `specs/SYMBOL_BIBLE.md`, `living_book/MEMORY_MOTIF_MAP.md`,
`media/COVER_BRIEF.md`).

O catálogo Dark Romance tem autora pública decidida: **Bea Halden**
(`DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md`, seção S). A tese editorial desta
capability é **THE BOOK TO POSSESS**: capa, lombada, bordas, sobrecapa,
hardcover, guardas, aberturas de capítulo e artefatos internos participam da
narrativa — e a identidade da autora é reconhecível entre livros sem virar
fórmula.

## 3. Problem

1. **Não existe memória visual verificável.** Decisões visuais vivem em
   Markdown livre. Nenhum script consegue perguntar "por que este símbolo está
   na capa?", "qual o estado do sigil no capítulo 15?" ou "este acabamento
   existe no KDP?". Precedente real de deriva: o brief de capa de
   `eva-a-ultima-mulher-da-terra` registrou "nenhuma figura humana" como regra
   e a revogou depois porque era **tática** (falta de imagens), não
   **narrativa** — sem campo que distinguisse as duas.
2. **Não existe identidade de autora.** `metadata.author` é só uma string;
   paleta, tipografia, marca e gramática de lombada seriam redefinidas (e
   derivariam) a cada livro.
3. **Não existe modelo de edição.** O motor conhece exatamente um alvo de
   capa (JPEG 1600×2560 de eBook). Paperback wrap, hardcover, collector,
   acabamentos, bordas e guardas não têm representação; nada impede prometer
   foil num livro KDP.
4. **Não existe separação entre intenção e manifestação.** Um "título em
   cobre" é hoje uma cor RGB hardcoded em `DEFAULT_DESIGN.palette.accent` de
   `build_cover_and_stories.py`, não uma intenção que o Kindle simula e a
   gráfica aplica como hot foil.
5. **Capas genéricas não são detectáveis** — nem símbolos sem suporte
   narrativo, nem spoilers visuais (fora de vetos em prosa como os pássaros
   de `eva`).

## 4. Goals

| ID | Goal |
|---|---|
| G1 | Separar **AUTHOR VISUAL DNA** (Bea Halden, versionado, compartilhado entre livros) de **BOOK VISUAL DNA** (por obra) e de **NARRATIVE VISUAL STATE** (por capítulo). |
| G2 | Um único **VISUAL NARRATIVE CANON** por livro, com dono, protocolo de proposta, versionamento e aprovação humana — no mesmo padrão do `CAUSAL_LEDGER.yaml`. |
| G3 | **Design once → render by edition:** intenção semântica única; resolução determinística por alvo (Kindle, KDP paperback, KDP hardcover, Collector) com fallbacks explícitos. |
| G4 | Formalizar **Visual Chekhov**, **Anti-Generic**, **Spoiler Safety**, **Thumbnail** e **Readability** como regras verificáveis (determinísticas onde possível, agente/humano no resíduo). |
| G5 | Chapter Sigils que evoluem por **âncora narrativa**, nunca por número de capítulo arbitrário, legíveis em P&B/e-ink. |
| G6 | Narrative Artifacts compostos com o canon narrativo existente (sem inventar fatos). |
| G7 | Contratos de produção (PRINT_SPEC, geometria de capa, manifesto de ativos e máscaras) sem gerar arte nem prepress. |
| G8 | Rastreabilidade: toda decisão responde `WHY / EVIDENCE`. |
| G9 | OFF por padrão; grafo de todo livro existente idêntico ao golden. |

## 5. Non-Goals (primeira versão)

- Substituir software de prepress; gerar PDF CMYK final de gráfica.
- Controlar impressora, falar com gráfica, publicar na Amazon.
- Gerar automaticamente todo artwork final (capa, guardas, bordas, máscaras).
- Garantir Pantone/ΔE; executar foil/emboss.
- Visão computacional de "originalidade" ou comparação com capas de mercado.
- Marketplace, inventário, box set, audiobook, web edition (extensão futura
  declarada em 15.4).
- Novos agentes. Nenhum agente é criado (seção 9.3).
- Tornar a Halden Spine contínua obrigatória (seção 17.6).

## 6. Principles (camada constitucional)

Os princípios estão **acima** de todo mecanismo derivado. Nenhum perfil de
execução, alvo de edição ou preferência de marketing os revoga.

| ID | Princípio | Verificação determinística | Resíduo de julgamento |
|---|---|---|---|
| **VP-01 NOTHING IS JUST DECORATION** | Todo elemento com `prominence ≥ SUPPORTING` declara ≥1 função narrativa do vocabulário fechado (11.3). Decoração pura só como `class: DECORATIVE`, `prominence: TEXTURE`, dentro do orçamento decorativo da autora. | V2 (`DECORATION_WITHOUT_FUNCTION`) | A função declarada é real na página? (`VISUAL_DIRECTOR`, `SYMBOLISM_ARCHITECT`) |
| **VP-02 VISUAL CHEKHOV** | Todo elemento destacado tem significado/função/consequência/payoff **ancorado** em fonte narrativa resolvível; contagem > 1 exige justificativa; mudança de estado exige causa narrativa. | V2 (`UNJUSTIFIED`, `UNJUSTIFIED_COUNT`, `ARBITRARY_STATE_MUTATION`) | A âncora sustenta *este* significado? (revisão de gate + humano) |
| **VP-03 DESIGN ONCE → RENDER BY EDITION** | Significado, símbolos e hierarquia existem uma vez no canon. Edição só escolhe manifestação; nunca muda significado. | V7 (`EDITION_CHANGES_MEANING`) | — |
| **VP-04 IDENTITY NEVER DESTROYS READING** | Corpo de texto, contraste mínimo e legibilidade de elementos essenciais têm precedência sobre qualquer identidade ou progressão. | V6 | Render-QA de `GATE_KDP` (existente) |
| **VP-05 VISUAL NEVER CREATES NARRATIVE FACT** | O canon visual cita fatos; não os cria. Um artefato que precisa de fato novo passa por `CANON_PROPOSAL_PROTOCOL`. | V2 (`VISUAL_INVENTS_FACT`) | `CANON_GUARDIAN` |
| **VP-06 SIGNATURE WITHOUT FORMULA** | (herdado da SDD irmã, S.5) Bea Halden é gramática, não repertório: a autora fixa estrutura; o livro escolhe símbolos. | V1 (`AUTHOR_LAYER_CONTAINS_BOOK_SYMBOL`) | Portfolio review (FUTURE) |
| **VP-07 EXPOSURE IS TIME** | Toda superfície tem um momento de exposição ao leitor; nenhum elemento é exposto antes de sua âncora de revelação. | V5 | Auditor de cena protegida |
| **VP-08 CANDIDATE ≠ CANON** | Descoberta produz candidatos; só aprovação promove. Nenhum renderer lê candidatos. | V0/V9 | Humano em decisões `REQUIRE_APPROVAL` |

Síntese:

> **IF THERE IS A SYMBOL HERE, IT MEANS SOMETHING — AND THE ENGINE CAN SAY WHAT, WHY, SINCE WHEN, AND WHERE IT MAY APPEAR.**

---

## 7. Discovery Findings

### 7.1 O que o repositório é (confirmado no código, não na documentação)

- **Não há modelo de domínio em código.** Memória narrativa = *blackboard* de
  arquivos escritos por agentes, protegido por propriedade textual e por
  **validadores determinísticos anexados a gates** (`custom_validators`,
  `runtime_taskgraph.py validate-gate`).
- **Composição:** `engine/scripts/livingbook.py::build_standard_graph()` gera o
  DAG a partir de `BOOK_SPEC.yaml`; features condicionais (`images`,
  `living_sound`, `translation_preparation`, `kdp_docx`, `causal_ledger`).
- **Precedente exato do padrão de capability:** `DARK_ROMANCE_CANON_ARCHITECT`
  entrou como 1 arquivo de canon (`canon/CAUSAL_LEDGER.yaml`), 1 validador
  (`check_causal_ledger.py`, 1.585 linhas, stdlib+PyYAML), 1 template
  executável, 1 runbook copiado como `canon/AGENTS.md`, flag lida com `.get()`,
  tarefas snapshot com `tool` via `TOOL_BY_PATTERN`, anotações de
  inputs/parameters em tarefas existentes, validadores anexados a gates
  existentes, e **golden JSON** dos seis livros em `tests/fixtures/golden/`.
- Verificado nesta sessão: `validate-engine` → `ENGINE VALID | generic agents: 66 | version: 1.1.0`;
  `python -m unittest tests.test_causal_ledger tests.test_compose_regression` → `Ran 57 tests … OK`.

### 7.2 Pipeline visual e editorial existente

```text
books/<slug>/visual_profile.md  (prosa: bioma, paleta, luz, motivos, VETO)
books/<slug>/BOOK_SPEC.yaml → spec.symbol_priorities (lista de strings)
        │
GATE_CANON ← T015_SYMBOL_BIBLE (SYMBOLISM_ARCHITECT): motivo, função, evolução por capítulo, veto
        │
LIVING_BOOK
  T035_MEMORY_MOTIF_MAP (SYMBOLISM_ARCHITECT): estados S seed / R recall / T transform / P payoff / E echo
  T036_VISUAL_LIFE_SPEC (VISUAL_DIRECTOR): tese visual, leis, sistema editorial de imagem
  T037_IMAGE_BIOME, T038_FACE_CANON, T039_CHARACTER_VISUAL_BIBLE (lock FACE_CANON_WRITE)
        │  ⇒ GATE_LIVING_BOOK
BRIEFS → VOICE → WAVES → INTEGRATION ⇒ GATE_FULL_MANUSCRIPT
        │
VISUAL_PRODUCTION (se images): T4NN brief → generate → FACE_QA → CONTINUITY_QA → approve ⇒ GATE_VISUAL
LEGAL: T602_ORIGINALITY_AUDIT ⇒ GATE_LEGAL
KDP: T699 requisitos atuais → T700 PAGE_BIBLE → T701 TOC → T702 IMAGE_PLACEMENT
     → T703_BUILD_DOCX (tool: build_kdp_docx.py) → T704 QA → T705 → T706 ⇒ GATE_KDP
DELIVERY: T800 media package (COVER_BRIEF.md) → T801_KDP_BOOK_COVER (tool: build_cover_and_stories.py)
          → T802 Stories ⇒ GATE_MEDIA_ASSETS (V_MEDIA_ASSET_PACKAGE) → T803..T805
```

### 7.3 Componentes relevantes por conceito pedido

| Conceito pedido | Componente real | Natureza / limite |
|---|---|---|
| Canon | `canon/CANON_REGISTRY.yaml` (sem schema, diverge por runtime), `CANON_PROPOSALS/`, `CANON_GUARDIAN` | atômico `{id,status,fact,source}` em `a_morte` |
| Canon estruturado estrito | `canon/CAUSAL_LEDGER.yaml` (quando `causal_ledger`) | eventos `EV-*`, GT `GT-*`, crenças `RB-*`, com capítulo e `reader_access` |
| Style/visual bible | `visual_profile.md`, `VISUAL_LIFE_SPEC.md`, `IMAGE_BIOME.md` | prosa; vetos em texto |
| Símbolos e progressão | `SYMBOL_BIBLE.md` ("Evolution" por capítulo), `MEMORY_MOTIF_MAP.md` (S/R/T/P/E) | **precedente direto** de estado visual progressivo, em prosa |
| Character bible / faces | `CHARACTER_BIBLE.md`, `FACE_CANON.md`, `CHARACTER_VISUAL_BIBLE.md` | grupo `artifact_contracts.VISUAL_CANON` no ENGINE_GRAPH |
| Plot map / chapter briefs | `PLOT_DEPENDENCY_MAP.md`, `chapter_architecture.yaml` (`pov`, `irreversible_turn`, `living_book_vitals`), `briefs/chapters/*` | campos extras por livro já validados por `validate_book_dna.py` |
| Cenas protegidas | `protected_scenes.yaml` (`id`, `chapters`, `auditor`) + `T32NN_PROTECTED_*` | âncoras com id **e** capítulo |
| Image generation | `generate_image.py` (OpenAI, `--reference`/`--edit`), `MODEL_TIERS.image_generation` | pago; capacidade de host |
| Capa | `build_cover_and_stories.py` + `media/MEDIA_DESIGN.yaml` (override opcional: palette, tamanhos, tagline, beats) | fontes escolhidas por *tipo* (`serif_bold`…), não por família |
| Interior | `build_kdp_docx.py` + `KDP_LAYOUT_DEFAULTS.yaml` ← `layout/KDP_LAYOUT.yaml`; `layout/IMAGE_PLACEMENT.yaml` (`OPEN`/`HINGE`/`AFTER` com `anchor` textual) | abertura = rótulo + título; glifo de quebra de cena configurável |
| Validação de mídia | `validate_media_assets.py` (dimensões, RGB, DPI, DPI efetivo, SHA-256 no manifesto) | precedente de proveniência por hash |
| Requisitos KDP atuais | `T699` → `layout/KDP_CURRENT_REQUIREMENTS.md` (verificado em fontes oficiais) | prosa com data de verificação |
| Originalidade | `T602_ORIGINALITY_AUDIT` em `GATE_LEGAL` | bloqueante |
| Checkpoints humanos | `requires_human_approval` + `project_state/APPROVALS/<GATE>.md` (motor nunca escreve) | por gate, por perfil |
| Perfis / custo | `EXECUTION_PROFILES.yaml` (`DRAFT` desliga `images`), `MODEL_TIERS.yaml` | — |
| Identidade autoral | `BOOK_SPEC.metadata.author` → `build_kdp_docx.py` (rosto, core properties) | string; nada visual |
| Contratos JSON | `engine/contracts/*.schema.json` | **não executados** por nenhum script (D2 da SDD irmã) |

### 7.4 Precedentes que antecipam a capability

| Precedente | Evidência | O que prova |
|---|---|---|
| Estado progressivo de motivo | `runtime/a_morte…/living_book/MEMORY_MOTIF_MAP.md` (S/R/T/P/E por capítulo; "No motif may receive payoff before a practical seed") | a progressão visual por estado já é pensamento editorial real |
| Evolução de símbolo por capítulo + veto | `specs/SYMBOL_BIBLE.md` ("Evolution", "Veto") | significado + função + evolução + proibição já existem, sem estrutura |
| Lei de densidade simbólica | `VISUAL_LIFE_SPEC.md` lei 9: "One dominant motif and at most one secondary motif may organize an image" | anti-overload já é regra do motor na prática |
| Spoiler visual na capa | `runtime/eva…/media/COVER_BRIEF.md`: pássaros proibidos na capa porque pertencem à última cena | spoiler safety por superfície tem caso real |
| Regra tática confundida com canon | mesmo brief, revisado em 2026-09-06, revoga "sem figura humana" | decisões precisam de `rule_kind` e versionamento |
| Diagnóstico de capa genérica / thumbnail | `runtime/eva…/reviews/COVER_STORIES_CRITIQUE.md` ("zero thumb-stopping power", "o padrão mais genérico possível"); `runtime/loja…/media/staging/pre_kdp/COVER_PRODUCTION_REPORT_PREVIEW.md` (miniatura 320×512 inspecionada) | gate de thumbnail já é praticado manualmente |
| Âncora textual determinística | `build_kdp_docx.py` falha se `anchor` de `IMAGE_PLACEMENT.yaml` não existe literalmente no manuscrito | padrão para ancorar artefatos e sigils na prosa congelada |
| Aprovação humana não automatizável | `runtime_taskgraph.py` (`AWAITING_HUMAN_APPROVAL`) | reutilizável para decisões visuais de alto impacto |
| Canon com dono + snapshot + imutabilidade | `CAUSAL_LEDGER.yaml`, `T*_LEDGER_SNAPSHOT`, L10 | versionamento de canon visual por snapshot |

### 7.5 Divergências e fatos registrados (não corrigidos)

| ID | Divergência / fato | Evidência | Impacto nesta SDD |
|---|---|---|---|
| D-V1 | O nome `VISUAL_CANON` já existe em `ENGINE_GRAPH.artifact_contracts` e designa `FACE_CANON.md` + `CHARACTER_VISUAL_BIBLE.md` | `engine/ENGINE_GRAPH.yaml` | o artefato novo chama-se `VISUAL_NARRATIVE_CANON` para não colidir; faces continuam onde estão |
| D-V2 | `build_cover_and_stories.py` escolhe fonte por *tipo* de uma lista fixa por plataforma; `MEDIA_DESIGN.yaml` não seleciona família | `FONT_CANDIDATES`, `load_font()` | a camada "font implementation" exige extensão (Slice 6); até lá, papéis tipográficos mapeiam para tipos existentes |
| D-V3 | Não existe geração de capa impressa (wrap PDF) em nenhum script; `IMPLEMENT.md` a declara "separate PDF" | `engine/IMPLEMENT.md`, grep | PRINT_SPEC e geometria são contrato novo; geração de PDF é FUTURE |
| D-V4 | `validate_media_assets.py` aceita capa de eBook até 50 MB; a página oficial de capa Kindle consultada em 2026-09-14 indica "5MB or fewer" para a imagem de marketing | `MAX_COVER_BYTES`; KDP G6GTK3T3NUHKLEFX | não corrigido; OQ-9 (verificar via `T699`) |
| D-V5 | Capa impressa KDP exige imagens CMYK ≥300 DPI; todo o pipeline atual é RGB | KDP G201953020; `save_jpeg()` | conversão CMYK é prepress, fora do MVP; PRINT_SPEC declara `color_space_required` |
| D-V6 | KDP hardcover é **case laminate**: sem sobrecapa; arte impressa direto na capa; wrap 0,51", hinge 0,4", texto a 0,635" da borda | KDP GDTKFJPNQCBTMRV6, G201834180 | `DUST_JACKET` e todos os acabamentos especiais = `UNSUPPORTED` no KDP |
| D-V7 | Acabamento de capa KDP: apenas glossy ou matte; papel de capa 80 lb/220 GSM | KDP G201834180 | `LAMINATE_FINISH` é o único acabamento físico KDP modelado |
| D-V8 | Faixa de páginas de hardcover (75–550) e 8 trims vieram de fonte **não oficial** nesta sessão | busca web (coverlabpro, vappingo) | tratados como "a verificar"; nunca hardcoded (seção 21) |
| D-V9 | Nenhum `BOOK_SPEC.yaml` é Dark Romance; todos têm `author: Pedro Arte` | seis pacotes em `books/` | worked examples são fictícios; piloto real depende de OQ-3 |
| D-V10 | `spec.symbol_priorities` existe em `BOOK_SPEC` (lista de strings), sem consumidor no compositor | `a_morte` BOOK_SPEC; grep em `livingbook.py` | REUSE como semente de descoberta |
| D-V11 | Runtimes antigos têm nomes de mídia fora do contrato (`story_01_o_gancho.jpg`, `A_MORTE_…_KDP_EBOOK_COVER.jpg`) | `runtime/a_morte…/media/outputs/` | evidência de que especificação canônica evita deriva; sem ação |
| D-V12 | Herdadas da SDD irmã e ainda válidas: D2 (schemas não executados), D3 (`chapter ≤ 30` nos schemas), D8 (`/engine` neutro de gênero), D9 (features via `[]`), D10 (`test_image_generation.py` faz chamada paga), D12 (working tree sujo) | SDD irmã, seção B.5 | mesmas mitigações: validador é o contrato; testes por módulo; golden antes de tocar o compositor |

---

## 8. Existing Architecture (o que esta capability precisa respeitar)

```text
engine/        reutilizável; NUNCA contém canon, motivos, nomes ou vetos de gênero (engine/AGENTS.md)
books/<slug>/  DNA literário de UMA obra
runtime/<slug> gerado por compose; nunca editado à mão fora de tarefa de reparo
```

Regras de governança que a capability herda sem exceção:

| Regra | Fonte |
|---|---|
| Um dono escritor por arquivo de canon; demais propõem | `ENGINE_GRAPH.canon_write_policy`, `CANON_PROPOSAL_PROTOCOL` |
| Revisores não reescrevem; reportam `REVIEW_FINDING` | `BASE_WAVE_REVIEW_PROTOCOL` |
| Trabalho mecânico = `tool` determinística; julgamento = agente | `run_deterministic.py`, `TOOL_BY_TASK` |
| Gate só passa com validadores `PASS` e, se declarado, arquivo de aprovação humana | `runtime_taskgraph.py` |
| Perfil nunca rebaixa canon, legal, mídia, entrega | `EXECUTION_PROFILES.yaml` |
| KDP atual deve ser revalidado em fonte oficial, ou `CAPABILITY_BLOCKER` | `IMPLEMENT.md` |
| Contrato de arquivo de mídia é por nome fixo + SHA-256 no manifesto | `artifact_contract_rules.MEDIA_DELIVERY_CORE` |

A lacuna central é uma só: **o motor tem três pacotes de canon (livro,
narrativo, facial) e nenhum para a identidade visual narrativa, nem nenhum
nível acima do livro.** A arquitetura proposta preenche essas duas lacunas e
nada além delas.

---

## 9. Reuse Analysis

Legenda: ✅ decisão. Uma única marca por linha.

### 9.1 Infraestrutura

| CONCEPT | EXISTING COMPONENT | REUSE | EXTEND | CREATE | DO NOT CREATE | JUSTIFICATION |
|---|---|---|---|---|---|---|
| Composição condicional | `build_standard_graph` | | ✅ | | | Bloco `if visual_narrative_enabled`, lido com `.get()`, idêntico ao de `causal_ledger`. |
| Máquina de estados / gates | `runtime_taskgraph.py` | ✅ | | | | Validadores entram como `custom_validators`. |
| Tarefas mecânicas | `TOOL_BY_PATTERN` + `run_deterministic.py` | | ✅ | | | Snapshot de canon visual, plano de edição e geometria são mecânicos. |
| Canon visual por livro | `CANON_REGISTRY.yaml` / `CAUSAL_LEDGER.yaml` | | | ✅ | | Arquivo irmão com contrato estrito `canon/VISUAL_NARRATIVE_CANON.yaml`. Não cabe no registry (sem schema, D4) nem no ledger (causalidade de personagem, só Dark Romance, dono diferente). |
| Identidade da autora | `BOOK_SPEC.metadata.author` | | | ✅ | | Novo **nível de pacote** `authors/<author_id>/`, versionado. Duplicar DNA em cada livro viola "definida uma vez" (G1) e o versionamento sem retroatividade (seção 27). `/engine` não pode recebê-lo (D8: contém vetos de gênero). Decisão sujeita a OQ-1. |
| Semente do DNA do livro | `visual_profile.md`, `symbol_priorities`, `SYMBOL_BIBLE.md`, `MEMORY_MOTIF_MAP.md` | ✅ | | | | Discovery lê o que já existe; nenhum arquivo novo obrigatório no pacote do livro. |
| Contrato | `engine/contracts/*.schema.json` | | | ✅ (template YAML executável) | JSON Schema | D2: schema não executado seria segunda verdade. |
| Formato de achado | `finding()` de `check_canon_continuity.py` / `REVIEW_FINDING` | ✅ | | | | `category, severity, chapter, evidence, detail, recommended_action`. |
| Instruções escopadas | `copy_runtime()` → `<dir>/AGENTS.md` | | ✅ | | | Runbook copiado condicionalmente, como `canon/AGENTS.md` do ledger. |
| Aprovação humana | `project_state/APPROVALS/` | | ✅ | | | Aprovação por **decisão**, com hash do bloco aprovado (seção 26.2). Máquina de gate intacta. |
| Proveniência de ativos | SHA-256 em `MEDIA_ASSET_MANIFEST.md` | | ✅ | | | Manifesto de produção por edição cita versão de canon + hash de plano + hash de ativos. |
| Matriz de capacidades | `known_capabilities` (capacidade de **host**) | | | ✅ | reusar `known_capabilities` | Edição ≠ host (D7 da SDD irmã). Template novo `engine/templates/EDITION_CAPABILITIES.yaml`, neutro de gênero, com proveniência e data. |
| Geometria de impressão | `KDP_LAYOUT_DEFAULTS.yaml` (interior), `T699` (requisitos) | | ✅ | | | Constantes de fabricação em template com proveniência; valores do livro (trim, páginas, papel) em `layout/PRINT_SPEC.yaml`. |
| Novo gate | lista de gates | | | | ✅ | Validadores se anexam a `GATE_LIVING_BOOK`, `GATE_FULL_MANUSCRIPT`, `GATE_KDP`, `GATE_MEDIA_ASSETS`. |
| Novos agentes | `engine/agents/` | | | | ✅ | Todos os papéis existem (9.3). |
| Novo lock | `ENGINE_GRAPH.locks` | | ✅ | | | `VISUAL_CANON_WRITE` injetado **só no grafo composto** quando a feature está ligada (precedente: `FACE_CANON_WRITE` como canon visual com dono próprio). `ENGINE_GRAPH.yaml` não muda. |

### 9.2 Conceitos pedidos (seção 24 da missão)

| CONCEPT | Decisão | Forma final |
|---|---|---|
| `VisualAuthorDNA` | CREATE | `authors/<id>/AUTHOR_VISUAL_DNA.v<N>.yaml` |
| `BookVisualDNA` | EXTEND (vira seção) | `VISUAL_NARRATIVE_CANON.book_dna` — não é arquivo próprio |
| `VisualCanon` | CREATE | `canon/VISUAL_NARRATIVE_CANON.yaml` |
| `VisualMotif` | EXTEND | `elements[]` com `class: MOTIF`, ancorado em `SYMBOL_BIBLE.md` |
| `NarrativeSigil` | EXTEND | `elements[]` `class: SIGIL` + `states[]` + `transitions[]` |
| `NarrativeArtifact` | EXTEND | `elements[]` `class: NARRATIVE_ARTIFACT`, conteúdo sempre citado de canon/manuscrito |
| `VisualProgression` | DO NOT CREATE | é o mesmo mecanismo `states/transitions` aplicado a qualquer elemento |
| `EditionProfile` / `EditionCapabilities` | CREATE (1 arquivo) | `engine/templates/EDITION_CAPABILITIES.yaml` |
| `FinishIntent` | EXTEND | `finish_intents[]` no canon |
| `CoverConcept` / `SpineConcept` / `EdgeConcept` / `EndpaperConcept` | DO NOT CREATE como tipos | todos são `compositions[]` sobre uma **superfície** (`FRONT_COVER`, `SPINE`, `EDGE_FORE`, `ENDPAPER_FRONT`…) — um único tipo |
| `ProductionSpec` | CREATE (livro) | `layout/PRINT_SPEC.yaml` (fatos de produção do livro) |
| `AssetManifest` | EXTEND | projeção `layout/editions/<target>/EDITION_PLAN.yaml` + manifesto de ativos com SHA-256 |
| `VisualValidationReport` | REUSE | `reviews/VISUAL_CANON_REPORT_<mode>.md` + `validator_results` |
| `TypographySystem` | EXTEND | `typography.roles` (autora) + `typography.bindings` (livro/edição) |
| `VisualMemory/State` | DO NOT CREATE | projeção de transições (princípio E.2 da SDD irmã) + snapshots |

### 9.3 Agentes reutilizados (nenhum criado)

| Papel | Agente existente | Tarefa |
|---|---|---|
| Descobrir candidatos (motivos, dualidades, artefatos, progressões) | `SYMBOLISM_ARCHITECT` | nova tarefa condicional `T042` |
| **Único escritor** do canon visual; decisões de capa, sigils, acabamentos | `VISUAL_DIRECTOR` ("Dono da linguagem visual e aprovação estética") | `T043`, `T311` |
| Verificar que âncoras citam fatos reais; aprovar artefatos com fato | `CANON_GUARDIAN` | spawn em `T043`, propostas via `CANON_PROPOSALS` |
| Tipografia e página | `BOOK_LAYOUT_ARCHITECT`, `TYPOGRAPHY_TEXT_REVIEWER` | `T700`, `T704` (anotados) |
| Arte de sigils/artefatos | `IMAGE_GENERATOR`, `IMAGE_CONTINUITY_QA` | `T45N` condicionais (só com `images`) |
| Capa, lombada, Stories | `MEDIA_AND_KDP_AGENT` | `T800`, `T801` (anotados) |
| Requisitos de fabricação atuais | `KDP_REQUIREMENTS_RESEARCHER` | `T699` (anotado: capa impressa, hardcover) |
| Especificação de produção collector | `BOOK_LAYOUT_ARCHITECT` | `T709` condicional |
| Originalidade / cópia de composição | `COPYRIGHT_ORIGINALITY_AUDITOR` | `T602` (anotado) |
| Clichê visual de gênero (resíduo) | `GENRE_GUARDIAN`, `COMMERCIAL_EDITOR_CRITIC` | spawn em `T043` |
| Spoiler de revelação | `PROTECTED_SCENE_AUDITOR` | `T32NN` (input: relatório de exposição) |
| Rosto de personagem em capa | `FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT` | FACE_QA existente |

---

## 10. Proposed Architecture

### 10.1 A menor arquitetura que cumpre os requisitos

```text
1 pacote de autora (novo nível)     authors/bea_halden/AUTHOR_VISUAL_DNA.v1.yaml
                                      (+ authors/bea_halden/marks/ para ativos da marca)
1 arquivo de canon por livro         runtime/<slug>/canon/VISUAL_NARRATIVE_CANON.yaml
                                      (dono VISUAL_DIRECTOR, lock VISUAL_CANON_WRITE)
1 matriz de edição (neutra)          engine/templates/EDITION_CAPABILITIES.yaml
2 templates executáveis              engine/templates/AUTHOR_VISUAL_DNA_TEMPLATE.yaml
                                     engine/templates/VISUAL_NARRATIVE_CANON_TEMPLATE.yaml
1 runbook                            engine/templates/VISUAL_NARRATIVE_RUNBOOK.md → runtime/canon/VISUAL_AGENTS.md
1 validador/resolvedor               engine/scripts/check_visual_canon.py (stdlib + PyYAML + Pillow, já instalados)
1 flag OFF por padrão                BOOK_SPEC.spec.features.visual_narrative
projeções geradas (nunca editadas)   layout/editions/<target>/EDITION_PLAN.yaml
                                     layout/editions/<target>/COVER_GEOMETRY.yaml
                                     media/MEDIA_DESIGN.yaml (quando gerado a partir do canon)
extensões de tarefas existentes      T035, T036, T602, T699, T700, T702, T703, T800, T801
tarefas condicionais novas           T042, T043, T044(tool), T311, T698(tool), T707(tool), T709*, T45N*
0 agentes · 0 gates novos · 0 serviços · 0 dependências novas
```

`*` só quando `collector` está entre os alvos (`T709`) ou `images` está ligado (`T45N`).

### 10.2 Separação das três camadas

```text
LAYER A  AUTHOR VISUAL DNA     authors/bea_halden/AUTHOR_VISUAL_DNA.v1.yaml
         gramática permanente: estrutura de valor, papéis de cor, papéis tipográficos,
         marca BH, gramática de lombada, orçamento de densidade, watchlist de tropes,
         política de spoiler de superfície, política de aprovação
         NUNCA contém: símbolo, objeto, motivo, cena ou hue específico de uma obra
                 │ pin por versão + sha256
                 ▼
LAYER B  BOOK VISUAL DNA        VISUAL_NARRATIVE_CANON.book_dna + elements + compositions + finish_intents
         tese visual da obra, símbolos com significado ancorado, paleta concreta dentro dos
         papéis da autora, artefatos, conceito de capa/lombada/bordas/guardas
                 │ transições ancoradas em eventos narrativos
                 ▼
LAYER C  NARRATIVE VISUAL STATE projeção de elements[].states/transitions por capítulo
         (nunca armazenado como "estado atual"; snapshots só como baseline de imutabilidade)
                 │ × EDITION_CAPABILITIES
                 ▼
MANIFESTATION  layout/editions/<target>/EDITION_PLAN.yaml (derivado, determinístico)
                 │
GENERATED ARTIFACTS  pixels, PDFs, máscaras — variação permitida; proveniência obrigatória
```

### 10.3 Fluxo pelo pipeline real (DISCOVERY / DECISION / CANONIZATION / GENERATION / VALIDATION / EXPORT)

```text
GATE_CANON (existente; narrativa aprovada)
   │
DISCOVERY      T042_VISUAL_DISCOVERY (SYMBOLISM_ARCHITECT)
               lê: visual_profile.md, symbol_priorities, SYMBOL_BIBLE, MEMORY_MOTIF_MAP,
                   chapter_architecture, protected_scenes, CANON_REGISTRY, CAUSAL_LEDGER (se houver),
                   AUTHOR_VISUAL_DNA pinado
               escreve: canon/CANON_PROPOSALS/VISUAL_CANDIDATES.yaml   (status CANDIDATE)
               apoio determinístico: check_visual_canon.py --evidence "<termo>" (contagem por fonte)
   │
DECISION       T043_VISUAL_NARRATIVE_CANON (VISUAL_DIRECTOR, lock VISUAL_CANON_WRITE,
               spawn CANON_GUARDIAN + GENRE_GUARDIAN + COMMERCIAL_EDITOR_CRITIC)
               promove candidatos → elements/compositions/finish_intents (status PLANNED)
               decisões REQUIRE_APPROVAL ficam PENDING_APPROVAL até arquivo humano
   │
CANONIZATION   T044_VISUAL_CANON_SNAPSHOT (tool) → canon/snapshots/VISUAL_NARRATIVE_CANON.PLAN.yaml
               V_VISUAL_CANON_PLAN  ⇒ GATE_LIVING_BOOK
   │
   │  (T036 VISUAL_LIFE_SPEC e T1NN briefs passam a citar ids do canon visual)
   │
WAVES / INTEGRATION (inalterados)
   │
REALIZATION    T311_VISUAL_STATE_REALIZATION (VISUAL_DIRECTOR), após T310_FREEZE_MANUSCRIPT:
               confirma âncoras contra a prosa congelada; PLANNED → REALIZED; artefatos citam
               trechos literais; estados de sigil projetados
               V_VISUAL_CANON_REALIZED  ⇒ GATE_FULL_MANUSCRIPT
               T312_VISUAL_CANON_SNAPSHOT (tool) → snapshots/…FREEZE.yaml
   │
GENERATION     T45N sigil/artefact art (se images) → aprovação VISUAL_DIRECTOR
               T800/T801: capa a partir de compositions[FRONT_COVER] (MEDIA_DESIGN.yaml projetado)
   │
EDITION PLAN   T698_EDITION_PLAN (tool): canon × EDITION_CAPABILITIES → EDITION_PLAN por alvo
               T707_PRINT_GEOMETRY (tool, após T705): PRINT_SPEC → COVER_GEOMETRY por alvo impresso
               T709_COLLECTOR_PRODUCTION_SPEC (BOOK_LAYOUT_ARCHITECT, se collector)
               V_VISUAL_EDITION  ⇒ GATE_KDP
   │
VALIDATION     V_VISUAL_ASSETS (thumbnail, grayscale, deriva de paleta, proveniência) ⇒ GATE_MEDIA_ASSETS
   │
EXPORT         T803..T805 (inalterados); manifesto cita canon_version + plan_sha256
```

---

## 11. Domain Model

### 11.1 Princípio de armazenamento

> **Decisões e transições são armazenadas. Estado por capítulo e manifestação por edição são projetados.**

| Armazenado | Projetado (nunca armazenado à mão) |
|---|---|
| Author DNA (versão imutável) | estado de qualquer elemento no capítulo N |
| `book_dna`, `elements[]` (significado, âncoras, estados possíveis, transições) | status Chekhov de cada elemento |
| `compositions[]` por superfície | exposição de cada elemento por superfície (spoiler) |
| `finish_intents[]` com escada de fallback | resolução do acabamento por edição (`EDITION_PLAN`) |
| `vetoes[]` com fonte | geometria de capa impressa (`COVER_GEOMETRY`) |
| `approvals[]` (referência ao arquivo humano + hash) | `MEDIA_DESIGN.yaml` derivado |
| `mutation_log[]`, `releases[]` | relatório de observabilidade |

### 11.2 Âncora narrativa (o átomo de suporte)

Toda justificativa, gatilho de estado, primeira aparição e revelação é uma
**âncora**: string tipada que o validador resolve de forma determinística.

| Tipo de âncora | Sintaxe | Resolve contra | Tem capítulo verificável? | Força |
|---|---|---|---|---|
| Evento do ledger | `LEDGER:EV-12` | `canon/CAUSAL_LEDGER.yaml` (se feature ligada) | sim (`chapter`) | STRUCTURAL |
| Ground truth do ledger | `LEDGER:GT-A-02` | idem; `reader_access` informa revelação | via `reader_access.from_event` | STRUCTURAL |
| Cena protegida | `SCENE:CROWN_REFUSAL` | `book/protected_scenes.yaml` | sim (`chapters[0]`) | STRUCTURAL |
| Virada de capítulo | `TURN:19` | `book/chapter_architecture.yaml` → `irreversible_turn` do capítulo 19 (deve existir e não ser vazio) | sim | STRUCTURAL |
| Campo de capítulo | `CHAPTER_FIELD:pov` | `chapter_architecture.yaml` (atribuição por valor, ex. POV) | sim, por capítulo | STRUCTURAL |
| Fato de canon | `CANON:ONT-004` | qualquer nó `id:` em `canon/CANON_REGISTRY.yaml` (busca recursiva; D4) | não | SUPPORTED |
| Seção de bíblia | `DOC:/specs/SYMBOL_BIBLE.md#motif-3-salt` | slug de heading Markdown | não | SUPPORTED |
| Regra imutável | `RULE:IR007` | `book/immutable_rules.yaml` | não | SUPPORTED (usada em `conflicts_with`) |
| Trecho de manuscrito | `TEXT:23:"primeira certidão"` | substring literal em `manuscript/final/MANUSCRIPT_FINAL_PTBR.md`, no capítulo 23 (mesmo parser de `build_kdp_docx.py`) | sim | STRUCTURAL (só em modo `realized`) |

Números de capítulo **nus** (`at_chapter: 15`) não são âncora. Um gatilho sem
âncora resolvível é `ARBITRARY_STATE_MUTATION` (HIGH).

### 11.3 Vocabulário fechado de função

`CHARACTER`, `RELATIONSHIP`, `WORLD`, `ATMOSPHERE`, `CONFLICT`, `PROGRESSION`,
`FORESHADOWING`, `CLUE`, `CONTRAST`, `REVELATION`, `MEMORY`, `TRANSFORMATION`,
`PAYOFF` — as treze funções da missão (personagem, relação, mundo, atmosfera,
conflito, progressão, antecipação, pista, contraste, revelação, memória,
transformação, payoff) — e mais uma, restrita à camada A:

- `AUTHORIAL_IDENTITY` — permitido **apenas** a elementos definidos no Author
  DNA (marca BH, gramática de lombada). Um elemento de livro que declare só
  essa função é `AUTHOR_FUNCTION_MISUSE`. Isso impede que "é a identidade da
  autora" vire justificativa para decoração.

`ATMOSPHERE` sozinha **não** basta para `prominence ≥ SECONDARY`: atmosfera
é qualidade da composição, não razão para um objeto destacado
(`ATMOSPHERE_ONLY_PROMINENT`, MEDIUM).

### 11.4 Proeminência e classe

| `prominence` | Significado | Exige |
|---|---|---|
| `DOMINANT` | ponto focal de uma superfície | Chekhov `PROVEN`; ≤ `author.density.max_dominant_per_surface` (Bea Halden v1: 1) |
| `SECONDARY` | segundo nível de leitura | `PROVEN` ou `SUPPORTED`; ≤ `max_secondary_per_surface` (v1: 2) |
| `SUPPORTING` | reconhecível, não focal | `SUPPORTED` |
| `TEXTURE` | ruído material, padrão, grão | pode ser `DECORATIVE_ALLOWED` |

`class`: `MOTIF` · `SIGIL` · `NARRATIVE_ARTIFACT` · `DECORATIVE_ILLUSTRATION` ·
`TYPOGRAPHIC` · `AUTHOR_MARK` (só camada A) · `FIGURE` (pessoa/personagem —
exige FACE_CANON quando recorrente e aprovação humana em capa).

### 11.5 Status Visual Chekhov (projeção determinística)

Calculado por elemento, por superfície em que aparece:

| Status | Condição (primeira regra que casar, de cima para baixo) |
|---|---|
| `CONTRADICTORY` | elemento casa um `vetoes[]` do livro sem `veto_override` aprovado; ou uma âncora de suporte cita `RULE:` listada em `conflicts_with`; ou exposição da superfície é anterior à âncora `reveal` (ver 26.1) |
| `PROVEN` | ≥1 âncora `STRUCTURAL` resolvida para cada função declarada; se `count > 1`, `count_rationale` com âncora resolvida; se `states` existem, toda transição tem gatilho `STRUCTURAL`; se `payoff` declarado, resolve; para `DOMINANT`, âncoras em ≥2 capítulos distintos |
| `SUPPORTED` | todas as funções têm ≥1 âncora resolvida, mas alguma só `SUPPORTED` |
| `DECORATIVE_ALLOWED` | `class: DECORATIVE_ILLUSTRATION`, `prominence: TEXTURE`, não está na watchlist da autora, dentro de `author.density.decorative_budget_per_surface` |
| `UNJUSTIFIED` | qualquer outro caso |

Bloqueio: `UNJUSTIFIED` ou `CONTRADICTORY` com `prominence ≥ SUPPORTING` →
HIGH; `DOMINANT` diferente de `PROVEN` → HIGH; qualquer elemento da
watchlist de tropes diferente de `PROVEN` → HIGH (seção 23.4).

---

## 12. Contracts

Os contratos são **templates YAML executáveis** testados contra o validador,
exatamente como `CAUSAL_LEDGER_TEMPLATE.yaml`. Nenhum JSON Schema (D2).
`apiVersion: pedroarte.livingbooks/v1` em todos.

### 12.1 `authors/<id>/AUTHOR_VISUAL_DNA.v<N>.yaml` (camada A)

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: AuthorVisualDNA
metadata:
  author_id: bea_halden
  public_name: Bea Halden          # deve ser igual a BOOK_SPEC.metadata.author dos livros que a pinam
  version: 1                        # inteiro; arquivo IMUTÁVEL após o primeiro release que o pina
  status: APPROVED                  # DRAFT | APPROVED | SUPERSEDED
  approved_by_file: approvals/AUTHOR_DNA_v1.md   # escrito por humano
  supersedes: null
thesis:                             # texto de identidade (não validado semanticamente)
  - dark elegance
  - psychological danger
  - premium restraint
  - collectible design
invariants:                         # o livro NÃO pode sobrescrever
  author_name_on: [FRONT_COVER, SPINE, TITLE_PAGE]
  author_mark_required_on: [SPINE, BACK_COVER]
  title_hierarchy: TITLE_OVER_AUTHOR          # TITLE_OVER_AUTHOR | AUTHOR_OVER_TITLE
  max_dominant_per_surface: 1
  chekhov_required: true
  sigils_monochrome_safe: true
  hidden_surface_max_spoiler: MEDIUM          # teto para capa nua / guarda traseira
  public_surface_max_spoiler: LOW
defaults:                           # o livro PODE sobrescrever, com override_reason
  density:
    max_secondary_per_surface: 2
    decorative_budget_per_surface: 1
  forbid_literal_protagonist_on_cover: true   # default, não lei: livro pode sobrescrever com aprovação
color:
  value_structure: LOW_KEY                    # fundo escuro dominante, luz quente como tinta
  roles:                                      # papéis, não hexadecimais obrigatórios
    GROUND:  {lightness: [0.04, 0.20], saturation: [0.00, 0.25], default: "#1E1C1B", label: charcoal}
    INK:     {lightness: [0.80, 0.95], saturation: [0.05, 0.30], default: "#E8DFCC", label: bone / aged ivory}
    METAL:   {material_family: WARM_METAL, default_material: BURNT_COPPER, default: "#9A5B3A"}
    PULSE:   {lightness: [0.15, 0.40], saturation: [0.40, 0.90], max_area_ratio: 0.12, default: "#5E1621", label: blood wine}
  signature_material: BURNT_COPPER            # SÓ a marca BH usa sempre; o livro escolhe seu METAL
typography:
  roles:                                      # SEMANTIC ROLE → intenção, nunca arquivo de fonte
    TITLE:          {classification: HIGH_CONTRAST_SERIF, case: UPPER, tracking: WIDE, weight: [500, 700]}
    SUBTITLE:       {classification: HIGH_CONTRAST_SERIF, case: SENTENCE, style: ITALIC}
    AUTHOR:         {classification: GEOMETRIC_SANS, case: UPPER, tracking: VERY_WIDE, weight: [300, 400]}
    SERIES:         {classification: GEOMETRIC_SANS, case: UPPER, size_relative_to: AUTHOR, ratio: 0.6}
    TAGLINE:        {classification: HIGH_CONTRAST_SERIF, style: ITALIC}
    EDITION_LABEL:  {classification: GEOMETRIC_SANS, case: UPPER}
    CHAPTER_NUMBER: {classification: GEOMETRIC_SANS, case: UPPER, tracking: WIDE}
    CHAPTER_TITLE:  {classification: HIGH_CONTRAST_SERIF}
    BODY:           {classification: BOOK_SERIF, inherit_from: KDP_LAYOUT}   # identidade NUNCA altera corpo
  min_body_pt: 7.0                            # piso KDP; o layout do livro manda acima disso
author_mark:
  id: BH_SEAL
  assets: {vector: marks/BH_SEAL.v1.svg, raster_1bit: marks/BH_SEAL.v1.png}
  monochrome_required: true
  min_size_mm: 5
  clearspace_ratio: 0.5
  allowed_surfaces: [SPINE, BACK_COVER, TITLE_PAGE, COPYRIGHT_PAGE, DUST_JACKET_FLAP, CASE_SPINE, BOX, AUDIO_SQUARE, PROMO]
  forbidden_surfaces: [CHAPTER_OPENER]        # não compete com o sigil do livro (seção 17.5)
spine_grammar:
  mode: INDIVIDUAL_CONSISTENT                 # INDIVIDUAL_CONSISTENT | SERIES_CONTINUOUS (FUTURE)
  title_axis: TOP_TO_BOTTOM
  author_zone: {from: 0.80, to: 0.93}         # fração da altura, a partir do topo
  mark_zone:   {from: 0.94, to: 0.98}
  band: {position: 0.08, height_ratio: 0.012, role_color: METAL}
generic_trope_watchlist:                      # específico de gênero → vive aqui, nunca em /engine
  - {id: SKULL,           match: [skull, caveira]}
  - {id: ROSE,            match: [rose, rosa, petal, pétala]}
  - {id: KNIFE,           match: [knife, faca, dagger, punhal]}
  - {id: CROWN,           match: [crown, coroa]}
  - {id: SHIRTLESS_MALE,  match: [shirtless, torso nu]}
  - {id: CHAINS,          match: [chain, corrente]}
  - {id: BLOOD,           match: [blood, sangue]}
  - {id: GENERIC_COUPLE,  match: [couple embrace, casal abraçado]}
approval_policy_defaults:                     # ver 26.2
  AUTHOR_MARK: REQUIRE_APPROVAL
  COVER_COMPOSITION: REQUIRE_APPROVAL
  DOMINANT_SYMBOL: REQUIRE_APPROVAL
  FINISH_INTENT_COLLECTOR: REQUIRE_APPROVAL
  HIDDEN_SURFACE: REQUIRE_APPROVAL
  EDGE_ART: REQUIRE_APPROVAL
  FIGURE_ON_COVER: REQUIRE_APPROVAL
  NARRATIVE_ARTIFACT: SUGGEST
  SIGIL_STATE: SUGGEST
  PALETTE_WITHIN_ROLES: AUTO
```

**Por que estes itens são AUTHOR DNA e outros não** (decisão, não
preferência):

| Item | Camada | Justificativa |
|---|---|---|
| Estrutura de valor escura + tinta clara quente | A (invariante de papel) | É o que torna a lombada reconhecível numa estante sem ler o nome; independe de símbolo. |
| Charcoal, bone, blood wine como **hex** | A (default) | São valores iniciais; um livro de mar e chumbo precisa trocar a pulsação sem perder a autora. |
| Burnt copper | A (material assinatura só da marca BH); default de METAL | A marca precisa de um material constante; o livro pode usar outro metal. |
| Papéis tipográficos + hierarquia | A (invariante) | Hierarquia é a assinatura mais barata e mais durável. |
| Famílias de fonte | **binding**, fora do DNA | Licença, host e embedding variam (D-V2, KDP exige fontes embutidas). |
| Cisne, coroa, rosas, vermelho profundo | B (O Cisne Negro) | Pertencem à obra; nunca entram no DNA (`AUTHOR_LAYER_CONTAINS_BOOK_SYMBOL`). |
| Watchlist de tropes | A | É política de catálogo de gênero; não pode ir para `/engine` (D8). |

### 12.2 `canon/VISUAL_NARRATIVE_CANON.yaml` (camadas B e C)

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: VisualNarrativeCanon
metadata:
  project_id: <slug>
  version: 0.3.0                    # semver do canon visual do livro
  owner: VISUAL_DIRECTOR
  author_dna: {author_id: bea_halden, version: 1, sha256: "<hash do arquivo pinado>"}
  narrative_canon_refs:             # versões de canon narrativo contra as quais foi validado
    canon_registry_version: 0.6.0
    causal_ledger_version: null
book_dna:
  visual_thesis: "Uma frase: a verdade visual desta obra."
  duality: {outer_truth: "…", hidden_truth: "…"}      # opcional; alimenta dust jacket × capa nua
  palette:                          # valores concretos DENTRO dos papéis da autora
    GROUND: "#141214"
    INK:    "#E6DCCB"
    METAL:  {material: AGED_GOLD, hex: "#8C6A3C"}
    PULSE:  "#6A0F1F"
  role_overrides: []                # [{key: defaults.forbid_literal_protagonist_on_cover, value: false,
                                    #   override_reason: "...", approval: APR-xx}]
  typography_bindings:              # FONT IMPLEMENTATION (por livro; edição pode refinar)
    TITLE:  {family: "<família licenciada>", file: "<caminho>", license: "<SPDX ou contrato>", embeddable: true}
vetoes:                             # transcritos de visual_profile.md / briefs, com fonte e tipo
  - id: VETO-01
    match: [skull, caveira]
    source: DOC:/book/visual_profile.md#veto
    rule_kind: CANONICAL            # CANONICAL (narrativa) | TACTICAL (produção; expira)
    rationale: "..."
elements:
  - id: SYM-SWAN
    label: black swan
    class: MOTIF                    # MOTIF | SIGIL | NARRATIVE_ARTIFACT | DECORATIVE_ILLUSTRATION | TYPOGRAPHIC | FIGURE
    watchlist_ids: []               # preenchido pelo validador por match; declarar à mão é permitido
    meaning: "O que significa NESTA obra."
    functions:
      - {function: CHARACTER,     anchors: [LEDGER:GT-A-01, DOC:/specs/SYMBOL_BIBLE.md#motif-1-swan]}
      - {function: TRANSFORMATION, anchors: [SCENE:CROWN_REFUSAL]}
    count: 1
    count_rationale: null           # obrigatório com âncora se count > 1 e prominence ≥ SUPPORTING
    first_appearance: TURN:1
    exposure:
      spoiler_level: NONE           # NONE | LOW | MEDIUM | HIGH | CORE
      reveal: null                  # âncora; obrigatória se spoiler_level ≥ MEDIUM
    accessibility:
      monochrome_safe: true
      min_render_size_mm: 8
      text_alternative: "Cisne negro sobre água escura."
    cost_class: ESSENTIAL           # ESSENTIAL | OPTIONAL | PREMIUM | COLLECTOR_ONLY
    approval: {policy: REQUIRE_APPROVAL, id: APR-03}
    states: []                      # ver seção 14
    transitions: []
    status: PLANNED                 # CANDIDATE nunca aparece aqui; PLANNED | REALIZED | RETIRED
    promoted_from: CAND-07          # id em CANON_PROPOSALS/VISUAL_CANDIDATES.yaml
compositions:                       # um tipo para capa, lombada, contracapa, bordas, guardas, aberturas
  - id: COMP-FRONT
    surface: FRONT_COVER
    reading_layer: OUTER_TRUTH      # OUTER_TRUTH | HIDDEN_TRUTH | NEUTRAL
    elements:
      - {element: SYM-SWAN, prominence: DOMINANT, placement: {zone: [0.15, 0.30, 0.85, 0.78]}}
    typography:
      - {role: TITLE,  text_source: BOOK_SPEC.metadata.title,  zone: [0.08, 0.06, 0.92, 0.22]}
      - {role: AUTHOR, text_source: AUTHOR_DNA.metadata.public_name, zone: [0.20, 0.86, 0.80, 0.93]}
    atmosphere: "…"
    forbidden_elements: [VETO-01]
    thumbnail_intent: {focal_element: SYM-SWAN, silhouette_readable: true}
    approval: {policy: REQUIRE_APPROVAL, id: APR-01}
finish_intents:
  - id: FI-TITLE
    target: {composition: COMP-FRONT, role: TITLE}
    semantic_material: AGED_GOLD
    meaning_element: SYM-CROWN      # o acabamento também obedece Chekhov
    preferred_effect: METALLIC_FOIL
    fallbacks: [SIMULATED_METALLIC_PRINT, FLAT_ROLE_COLOR]
    cost_class: PREMIUM
    approval: {policy: REQUIRE_APPROVAL, id: APR-05}
approvals:                          # referências; o arquivo é escrito por humano
  - {id: APR-01, file: /project_state/APPROVALS/VISUAL/APR-01.md, subject: COMP-FRONT, subject_sha256: "<hash canônico do bloco>"}
releases:                           # congelamento por edição publicada (seção 27)
  - {edition: kindle_ebook, edition_version: 1, canon_version: 0.3.0, plan_sha256: "…", assets_manifest_sha256: "…", date: 2026-10-01}
mutation_log:
  - {version: 0.1.0, task: T043_VISUAL_NARRATIVE_CANON, owner: VISUAL_DIRECTOR, action: "Consolidação a partir de VISUAL_CANDIDATES."}
```

### 12.3 `canon/CANON_PROPOSALS/VISUAL_CANDIDATES.yaml` (descoberta)

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: VisualCandidates
metadata: {project_id: <slug>, produced_by: T042_VISUAL_DISCOVERY}
candidates:
  - id: CAND-07
    label: black swan
    kind_hint: DOMINANT_OBJECT      # DOMINANT_OBJECT | RECURRING_MOTIF | LOCATION | COLOR | TEXTURE |
                                   # SYMBOL | RELATIONSHIP | TRANSFORMATION | ARTIFACT | DUALITY |
                                   # SECRET | CHAPTER_PROGRESSION
    evidence:
      - {anchor: DOC:/specs/SYMBOL_BIBLE.md#motif-1-swan, note: "evolução em 4 estados"}
      - {anchor: LEDGER:GT-A-01}
    counts: {manuscript_mentions: null, bible_mentions: 14}   # de --evidence; null antes do manuscrito
    proposed_functions: [CHARACTER, TRANSFORMATION]
    risks: [WATCHLIST:none, SPOILER:LOW]
    status: CANDIDATE               # CANDIDATE | PROMOTED | REJECTED  (rejeição exige motivo)
    decision_note: null
```

Nenhum renderer, tarefa de geração ou projeção lê este arquivo (VP-08;
`CANDIDATE_CONSUMED` se um `EDITION_PLAN` citar `CAND-*`).

### 12.4 `engine/templates/EDITION_CAPABILITIES.yaml` (neutro de gênero)

Contrato na seção 16. `layout/PRINT_SPEC.yaml` e `EDITION_PLAN.yaml` na seção 21.

---

## 13. Canon Hierarchy

### 13.1 A ordem pedida e por que ela precisa de dois eixos

A ordem linear `ENGINE > AUTHOR > BOOK > EDITION > CHAPTER` falha em um caso
real: o Author DNA propõe `PULSE = blood wine`; o `visual_profile.md` de
`a_morte_ainda_nao_nasceu` diz "evitar vermelho de horror". Se a autora sempre
vencesse, o livro não poderia proteger seu próprio tom. Se o livro sempre
vencesse, a autora não teria identidade.

Resolução: **toda regra é CONSTRAINT (proibição, mínimo, teto) ou PREFERENCE
(valor default, escolha).** Os dois tipos resolvem de formas opostas.

| Eixo | Regra de resolução |
|---|---|
| **CONSTRAINTS** | **Acumulam.** Vale a união de todas as proibições e o mais restritivo de todos os mínimos/tetos, de qualquer nível. Nenhum nível remove uma constraint de nível superior. |
| **PREFERENCES** | **Vence o mais específico** (`CHAPTER_STATE > EDITION > BOOK > AUTHOR.defaults > ENGINE`), desde que respeite todas as constraints acumuladas. |
| **Invariantes de autora** | São constraints: o livro não sobrescreve `AUTHOR.invariants`. |
| **Defaults de autora** | São preferences: o livro sobrescreve com `role_overrides[]` + `override_reason` + aprovação quando a política exigir. |
| **Edição** | Só altera **manifestação** (efeito, fallback, geometria, binding de fonte). Mudar `meaning`, `elements` ou `functions` numa edição é `EDITION_CHANGES_MEANING` (BLOCKER). |
| **Estado de capítulo** | Só altera propriedades declaradas em `states[]` de um elemento. Nunca cria elemento, nunca muda paleta global, nunca toca `BODY`. |

### 13.2 Precedência formal

```text
CONSTRAINTS (acumulam; em conflito entre si, a mais restritiva)
  C0 ENGINE GLOBAL          fatos de fabricação (EDITION_CAPABILITIES), mínimos de acessibilidade,
                            legal/IP (T602), princípios VP-01..VP-08
  C1 NARRATIVE CANON        immutable_rules.yaml, CANON_REGISTRY, CAUSAL_LEDGER (fatos, reader_access)
  C2 AUTHOR INVARIANTS      AUTHOR_VISUAL_DNA.invariants, watchlist, tetos de spoiler de superfície
  C3 BOOK VETOES            VISUAL_NARRATIVE_CANON.vetoes (CANONICAL)
  C4 EDITION LIMITS         capacidade do alvo (UNSUPPORTED não pode ser prometido)

PREFERENCES (mais específico vence, dentro das constraints)
  P4 CHAPTER/SCENE STATE    estados projetados de elementos
  P3 EDITION                escolha de fallback, binding de fonte por alvo
  P2 BOOK CANON             book_dna, palette, compositions, role_overrides
  P1 AUTHOR DEFAULTS        AUTHOR_VISUAL_DNA.defaults, color.roles.*.default
  P0 ENGINE DEFAULTS        DEFAULT_DESIGN, KDP_LAYOUT_DEFAULTS
```

Herdado do motor e da SDD irmã, inalterado: `immutable_rules.yaml >
BOOK_CONSTITUTION.md > CANON_REGISTRY / ledger > bíblias > briefs > prosa`. O
canon visual se posiciona **abaixo do canon narrativo** (VP-05) e **acima de
briefs de imagem e de capa** (`COVER_BRIEF.md`, `CHAPTER_NN_IMAGE_BRIEF.md`
passam a citá-lo).

### 13.3 Regras de resolução de conflito (determinísticas)

| # | Conflito | Resultado | Achado |
|---|---|---|---|
| R1 | Preferência de livro fora da faixa de um papel de cor da autora | inválido | `AUTHOR_DNA_DRIFT` (HIGH) |
| R2 | Livro sobrescreve default sem `override_reason` | inválido | `OVERRIDE_WITHOUT_REASON` (MEDIUM) |
| R3 | Livro tenta sobrescrever invariante | inválido | `AUTHOR_INVARIANT_OVERRIDE` (BLOCKER) |
| R4 | Elemento visual contradiz fato/regra narrativa | canon narrativo vence | `CONTRADICTORY` → HIGH |
| R5 | Default da autora colide com veto `CANONICAL` do livro (ex.: PULSE vermelho × "sem vermelho de horror") | veto vence; livro deve escolher PULSE dentro da faixa e fora do veto | `VETO_BLOCKS_AUTHOR_DEFAULT` (INFO) + exige `palette.PULSE` explícito |
| R6 | Veto `TACTICAL` expira (`expires_when`) | deixa de valer só com nova versão do canon + `mutation_log` | `TACTICAL_VETO_EXPIRED` (INFO) |
| R7 | Edição sem capacidade para efeito `ESSENTIAL` e sem fallback viável | edição bloqueada | `ESSENTIAL_UNRENDERABLE` (BLOCKER) |
| R8 | Dois níveis de mesma especificidade discordam (ex.: duas compositions na mesma superfície e camada) | inválido | `AMBIGUOUS_COMPOSITION` (HIGH) |
| R9 | Estado de capítulo alteraria constraint (ex.: sigil perde `monochrome_safe`) | constraint vence | `STATE_BREAKS_CONSTRAINT` (HIGH) |

---

## 14. State Model

### 14.1 Estados e transições (serve sigils, motivos, progressão interna)

```yaml
elements:
  - id: SIG-SWAN
    class: SIGIL
    scope: BOOK                   # BOOK | CHARACTER | POV | RELATIONSHIP | OBJECT | TIME
    assignment:                   # em quais capítulos o sigil aparece
      mode: ALL_CHAPTERS          # ALL_CHAPTERS | BY_CHAPTER_FIELD | BY_ANCHOR_LIST
      # mode: BY_CHAPTER_FIELD, field: pov, value: Isadora   (resolvido em chapter_architecture.yaml)
    states:
      - id: PRISTINE
        initial: true
        visual_description: "Cisne de perfil, contorno contínuo."
        memory_state: S           # REUSE do vocabulário de MEMORY_MOTIF_MAP: S R T P E
        render: {mode: GLYPH, asset: images/sigils/SIG-SWAN/PRISTINE.png}   # GLYPH | RASTER_1BIT | VECTOR
      - id: CRACKED
        memory_state: T
        visual_description: "Mesmo contorno, uma fratura atravessa a asa."
      - id: CROWNLESS
        memory_state: P
        visual_description: "Coroa sobre a cabeça partida em duas."
    transitions:
      - from: PRISTINE
        to: CRACKED
        trigger: LEDGER:EV-09     # âncora STRUCTURAL obrigatória
        because: "Isadora descobre o contrato das cinco herdeiras."
        display_from: NEXT_CHAPTER    # NEXT_CHAPTER (padrão) | AFTER_ANCHOR_IN_CHAPTER | SAME_CHAPTER
      - from: CRACKED
        to: CROWNLESS
        trigger: SCENE:CROWN_REFUSAL
        because: "Recusa pública da coroa."
        display_from: NEXT_CHAPTER
```

### 14.2 Projeção

```text
state(element, chapter N) =
    initial state,
    then, in trigger-chapter order, apply each transition whose
    effective_display_chapter(transition) ≤ N
effective_display_chapter =
    NEXT_CHAPTER            → chapter(trigger) + 1
    AFTER_ANCHOR_IN_CHAPTER → chapter(trigger), mas só em superfícies posicionadas após o
                              parágrafo-âncora (padrão HINGE/AFTER de IMAGE_PLACEMENT.yaml)
    SAME_CHAPTER            → chapter(trigger); exige exposure.spoiler_ack com aprovação
```

Por que `NEXT_CHAPTER` é o padrão: a abertura de capítulo é vista **antes**
da prosa do capítulo. Um sigil que racha na abertura do capítulo em que a
rachadura acontece anuncia o evento — spoiler estrutural pequeno, mas real
(`OPENER_PRE_ANNOUNCES_EVENT`, MEDIUM, se `SAME_CHAPTER` sem `spoiler_ack`).

### 14.3 Invariantes de estado

| ID | Invariante | Achado |
|---|---|---|
| ST-01 | Exatamente um estado `initial`. | `STATE_MODEL_INVALID` (HIGH) |
| ST-02 | Todo `trigger` é âncora `STRUCTURAL` resolvida; número de capítulo nu é recusado. | `ARBITRARY_STATE_MUTATION` (HIGH) |
| ST-03 | Transições formam caminho sem ciclos, a menos que `reversible: true` com âncora própria para a volta. | `STATE_CYCLE_WITHOUT_CAUSE` (HIGH) |
| ST-04 | Triggers em ordem não decrescente de capítulo ao longo do caminho. | `STATE_ORDER_VIOLATION` (HIGH) |
| ST-05 | Estado `P` (payoff) exige estado `S` anterior em capítulo menor (regra de `MEMORY_MOTIF_MAP`: sem payoff sem semente). | `PAYOFF_WITHOUT_SEED` (HIGH) |
| ST-06 | Em modo `realized`, a âncora do trigger existe na prosa congelada ou no ledger `REALIZED`. | `TRIGGER_NOT_REALIZED` (HIGH) |
| ST-07 | Todo estado preserva as constraints do elemento (monocromia, tamanho mínimo). | `STATE_BREAKS_CONSTRAINT` (HIGH) |
| ST-08 | Transições de estados `REALIZED` são imutáveis contra o snapshot `FREEZE`. | `VISUAL_RETCON` (BLOCKER) |
| ST-09 | Progressão interna nunca altera papel `BODY`, `CHAPTER_TITLE` ou margens. | `READING_LAYER_MUTATION` (BLOCKER) |

### 14.4 Persistência e continuação ("saber o último estado")

- **Não há "estado atual" salvo.** Qualquer consumidor — `build_kdp_docx.py`
  escolhendo o asset da abertura, um brief de imagem, uma continuação da
  série — chama a projeção: `check_visual_canon.py --state SIG-SWAN --at-chapter 27`.
- **Snapshots** (`canon/snapshots/VISUAL_NARRATIVE_CANON.PLAN.yaml`,
  `.FREEZE.yaml`, `.RELEASE_<edition>_<n>.yaml`) são baseline de
  imutabilidade, **não** fonte de estado — mesmo papel dos snapshots do ledger.
- **`--end-state`** projeta o estado final de todo elemento progressivo, para
  um próximo livro da série herdar (FUTURE: `inherits_from:
  <slug>@<release>` no canon do livro seguinte).
- Reuse verificado: o Living Book Engine **não** possui store de estado
  narrativo além de arquivos; `PROJECT_STATUS.yaml` é estado de tarefa. O
  modelo "transições armazenadas, estado projetado" é o mesmo que o
  `CAUSAL_LEDGER` já implementa e testa — nenhum sistema novo de memória.

---

## 15. Edition Model

### 15.1 Alvos

| Target id | Produto | Superfícies disponíveis | Fonte das restrições |
|---|---|---|---|
| `kindle_ebook` | eBook Kindle | `MARKETING_COVER`, `INTERNAL_COVER`, `TITLE_PAGE`, `CHAPTER_OPENER`, `INTERIOR_PLATE`, `PROMO` | KDP eBook cover (G6GTK3T3NUHKLEFX) |
| `kdp_paperback` | brochura KDP | `FRONT_COVER`, `BACK_COVER`, `SPINE` (se ≥ limiar de páginas), `TITLE_PAGE`, `CHAPTER_OPENER`, `INTERIOR_PLATE` | G201953020, G201834180 |
| `kdp_hardcover` | hardcover case laminate KDP | `CASE_FRONT`, `CASE_BACK`, `CASE_SPINE`, `TITLE_PAGE`, `CHAPTER_OPENER`, `INTERIOR_PLATE` | GDTKFJPNQCBTMRV6 |
| `collector` | edição de gráfica especializada | todas acima + `DUST_JACKET_FRONT/BACK/SPINE/FLAP_FRONT/FLAP_BACK`, `CASE_*` (nua), `ENDPAPER_FRONT/BACK`, `EDGE_TOP/FORE/BOTTOM`, `INSERT`, `RIBBON` | **perfil de gráfica** declarado pelo livro (OQ-4) |

Um livro escolhe alvos em `features.visual_narrative.edition_targets`. Uma
composição cuja superfície não existe no alvo é **mapeada** (15.2) ou
**omitida com registro** — nunca silenciosamente perdida.

### 15.2 Mapeamento de superfície entre edições

| Superfície canônica | kindle_ebook | kdp_paperback | kdp_hardcover | collector |
|---|---|---|---|---|
| `FRONT_COVER` (OUTER_TRUTH) | `MARKETING_COVER` | `FRONT_COVER` | `CASE_FRONT` | `DUST_JACKET_FRONT` |
| `HIDDEN_TRUTH` front | OMIT | OMIT | OMIT (padrão) ou `INTERIOR_PLATE` final se `hidden_truth_fallback: FINAL_PLATE` | `CASE_FRONT` (nua) |
| `SPINE` | — | `SPINE` | `CASE_SPINE` | `DUST_JACKET_SPINE` + `CASE_SPINE` |
| `BACK_COVER` | — | `BACK_COVER` (zona de código de barras reservada) | `CASE_BACK` | `DUST_JACKET_BACK` |
| `ENDPAPER_*` | OMIT ou `INTERIOR_PLATE` (opt-in) | OMIT ou `INTERIOR_PLATE` (opt-in, custa páginas) | idem | `ENDPAPER_*` |
| `EDGE_*` | OMIT | OMIT | OMIT | `EDGE_*` |
| `CHAPTER_OPENER` | `CHAPTER_OPENER` | idem | idem | idem |

Regra: a hidden truth **nunca** migra para uma superfície pública por
fallback (`HIDDEN_TRUTH_EXPOSED`, BLOCKER). Omitir é sempre permitido.

### 15.3 Resolução determinística de acabamento

```text
resolve(finish_intent, target):
  if cost_class == COLLECTOR_ONLY and target != collector:
      return OMIT                              # nem simulado; registra motivo
  if cost_class not in target.budget: return OMIT (registra)
  for effect in [preferred_effect] + fallbacks:
      level = CAPABILITIES[target][effect]
      if level in {PHYSICAL, SIMULATED}: return (effect, level)
      if level == VENDOR_DEPENDENT and printer_profile confirms: return (effect, PHYSICAL)
  if cost_class == ESSENTIAL: BLOCKER ESSENTIAL_UNRENDERABLE
  return OMIT
```

Orçamento por alvo (default, sobrescrevível por livro):

| Target | Classes permitidas |
|---|---|
| `kindle_ebook` | ESSENTIAL |
| `kdp_paperback` | ESSENTIAL, OPTIONAL |
| `kdp_hardcover` | ESSENTIAL, OPTIONAL, PREMIUM (apenas SIMULATED) |
| `collector` | todas |

### 15.4 Extensão futura (sem código no MVP)

`epub_external`, `audiobook_square` (superfície `AUDIO_SQUARE`), `web_edition`,
`print_house_<id>`, `box_set` (superfícies `BOX_*` e, só aqui, lombada contínua
controlada). Cada um é **uma entrada nova** em `EDITION_CAPABILITIES.yaml`
+ mapeamento de superfícies; nada no canon muda.

---

## 16. Capability Matrix

### 16.1 Níveis

`PHYSICAL` (fabricado de verdade) · `SIMULATED` (representação gráfica
impressa/exibida) · `UNSUPPORTED` · `VENDOR_DEPENDENT` (depende do perfil de
gráfica confirmado).

### 16.2 `engine/templates/EDITION_CAPABILITIES.yaml` (valores iniciais propostos)

Fatos de fabricação com proveniência verificada em **2026-09-14**. `T699`
revalida antes de qualquer release; divergência vira `CAPABILITY_BLOCKER`,
nunca edição silenciosa.

| Feature / efeito | kindle_ebook | kdp_paperback | kdp_hardcover | collector | Evidência |
|---|---|---|---|---|---|
| `COLOR_PRINT` (arte de capa) | SIMULATED (RGB tela) | PHYSICAL (CMYK) | PHYSICAL | PHYSICAL | G201953020 (CMYK ≥300 DPI) |
| `LAMINATE_FINISH` matte/glossy | UNSUPPORTED | PHYSICAL | PHYSICAL | VENDOR_DEPENDENT | G201834180 |
| `METALLIC_FOIL` | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | VENDOR_DEPENDENT | nenhuma opção KDP documentada |
| `SIMULATED_METALLIC_PRINT` | SIMULATED | SIMULATED | SIMULATED | SIMULATED | — |
| `EMBOSS` / `DEBOSS` | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | VENDOR_DEPENDENT | idem |
| `TONAL_RELIEF_SIMULATION` | SIMULATED | SIMULATED | SIMULATED | SIMULATED | — |
| `SPOT_UV` / `SELECTIVE_VARNISH` | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | VENDOR_DEPENDENT | idem |
| `CONTRAST_SIMULATION` | SIMULATED | SIMULATED | SIMULATED | SIMULATED | — |
| `SPRAYED_EDGE` / `STENCILED_EDGE` | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | VENDOR_DEPENDENT | idem |
| `DUST_JACKET` | UNSUPPORTED | UNSUPPORTED | **UNSUPPORTED** | VENDOR_DEPENDENT | GDTKFJPNQCBTMRV6: "will not have a dust jacket" |
| `CLOTH_CASE` | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED (case laminate) | VENDOR_DEPENDENT | G201834180 |
| `PRINTED_ENDPAPER` | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | VENDOR_DEPENDENT | nenhuma opção KDP documentada |
| `DIE_CUT` | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | VENDOR_DEPENDENT | idem |
| `RIBBON_MARKER` | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | VENDOR_DEPENDENT | idem |
| `SPINE_TEXT` | — | PHYSICAL se páginas ≥ `spine_text_min_pages` | PHYSICAL | PHYSICAL | G201953020 (≥79 páginas) |
| `NARRATIVE_SIGIL` (P&B) | PHYSICAL (tela) | PHYSICAL | PHYSICAL | PHYSICAL | interior DOCX existente |
| `NARRATIVE_ARTIFACT` interior | PHYSICAL | PHYSICAL | PHYSICAL | PHYSICAL | idem |
| `INTERIOR_COLOR` | device-dependent (e-ink = grayscale) | PHYSICAL se premium/standard color | PHYSICAL premium color (standard color indisponível em hardcover) | VENDOR_DEPENDENT | G201834180 |
| `FLAT_ROLE_COLOR` / `OMIT` | sempre | sempre | sempre | sempre | — |

Estrutura do template (resumo):

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: EditionCapabilities
metadata: {version: 1.0.0, verified_on: 2026-09-14, verified_by: T699_KDP_REQUIREMENTS_REFRESH|SDD}
targets:
  kdp_hardcover:
    surfaces: [CASE_FRONT, CASE_BACK, CASE_SPINE, TITLE_PAGE, CHAPTER_OPENER, INTERIOR_PLATE]
    budget: [ESSENTIAL, OPTIONAL, PREMIUM]
    effects: {METALLIC_FOIL: UNSUPPORTED, SIMULATED_METALLIC_PRINT: SIMULATED, LAMINATE_FINISH: PHYSICAL, ...}
    geometry_ref: PRINT_GEOMETRY.kdp_hardcover     # seção 21
    sources: [https://kdp.amazon.com/en_US/help/topic/GDTKFJPNQCBTMRV6]
  collector:
    printer_profile_required: true   # sem layout/PRINTER_PROFILE.yaml, VENDOR_DEPENDENT = UNSUPPORTED
```

A matriz **não** é definitiva: é um arquivo de dados com data. Mudança da
Amazon = nova versão do template, nenhuma mudança de código ou canon.

---

## 17. Cover Model

### 17.1 Cover concept = composição sobre `FRONT_COVER`

Não existe tipo `CoverConcept`. A capa é a `composition` com
`surface: FRONT_COVER`, e o que a missão lista para `COVER_CONCEPT` mapeia
para campos já definidos:

| Campo pedido | Onde vive |
|---|---|
| `book_id` | `metadata.project_id` |
| `visual_thesis` | `book_dna.visual_thesis` |
| `dominant_symbol` / `secondary_symbols` | `compositions[FRONT_COVER].elements[].prominence` |
| `title_hierarchy` / `author_hierarchy` | `AUTHOR.invariants.title_hierarchy` + `typography[]` com zonas |
| `atmosphere` | `compositions[].atmosphere` (não justifica objeto — 11.3) |
| `composition` | `placement.zone` normalizado `[x0,y0,x1,y1]` |
| `palette` | `book_dna.palette` (dentro dos papéis) |
| `materials` | `finish_intents[]` que miram a composição |
| `narrative_meaning` | `elements[].meaning` + `functions[].anchors` |
| `thumbnail_test` | `thumbnail_intent` + V4 (23.5) |
| `forbidden_elements` | `forbidden_elements` → `vetoes[]` |
| `edition_adaptations` | **não armazenado**: projeção em `EDITION_PLAN` (VP-03) |

### 17.2 A capa deve comunicar três coisas — como cada uma é garantida

| Comunicação | Mecanismo |
|---|---|
| DARK ROMANCE | estrutura de valor `LOW_KEY` + papéis tipográficos da autora (C2) + `COMMERCIAL_EDITOR_CRITIC` no spawn de `T043` (resíduo) |
| BEA HALDEN | `author_name_on: FRONT_COVER`, hierarquia, papel `AUTHOR`, gramática reconhecível — **sem** exigir a marca BH na frente (marca é de lombada/contracapa) |
| ESTE LIVRO | exatamente 1 `DOMINANT` `PROVEN` cujas âncoras pertencem a este livro (`DOMINANT_NOT_BOOK_SPECIFIC` se só houver âncoras `DOC:` genéricas) |

Default da autora v1: `forbid_literal_protagonist_on_cover: true`. É
**default**, não invariante, porque o precedente de `eva` mostra que a
proibição de figura pode ser tática. Um livro que queira figura humana usa
`role_overrides` + `FIGURE_ON_COVER: REQUIRE_APPROVAL` + FACE_CANON.

### 17.3 Integração com o compositor de capa existente (sem reescrevê-lo)

`build_cover_and_stories.py` já aceita `media/MEDIA_DESIGN.yaml`
(`palette.ground/ink/accent/muted`, tamanhos, `tagline`, `base_image`,
`story_beats`). Com a feature ligada, uma projeção determinística escreve
esse arquivo a partir do canon:

| MEDIA_DESIGN | ← canon |
|---|---|
| `palette.ground` | `book_dna.palette.GROUND` |
| `palette.ink` | `INK` |
| `palette.accent` | cor resolvida de `METAL` para `kindle_ebook` (SIMULATED) |
| `palette.muted` | `INK` com luminosidade reduzida (fórmula fixa) |
| `cover.base_image` | arte aprovada da composição `FRONT_COVER` (gerada em `T800/T801`), nunca imagem de capítulo aleatória |
| `tagline` | `typography[role=TAGLINE].text_source` |

O arquivo gerado carrega cabeçalho `generated_from: VISUAL_NARRATIVE_CANON@<version>`
e `sha256` do próprio conteúdo; edição manual posterior é detectada
(`DERIVED_ARTIFACT_EDITED`, HIGH). Limite registrado (D-V2): a família de
fonte ainda não é selecionável — Slice 6 estende `load_font()` para aceitar
`typography_bindings` opcionais sem mudar o comportamento padrão.

### 17.4 Typography System

```text
SEMANTIC ROLE (autora: classificação, caixa, tracking, peso, hierarquia)
      ↓ binding (livro, opcional por edição)
FONT IMPLEMENTATION (família, arquivo, licença, embeddable)
      ↓ consumidores
build_cover_and_stories.py (TITLE, SUBTITLE, AUTHOR, TAGLINE, EDITION_LABEL)
build_kdp_docx.py via layout/KDP_LAYOUT.yaml (CHAPTER_NUMBER, CHAPTER_TITLE, BODY — BODY só lido)
artefatos (ARTIFACT_HANDWRITTEN, ARTIFACT_TYPEWRITTEN, ARTIFACT_PRINTED — definidos por livro)
```

Regras: binding sem `embeddable: true` → `FONT_NOT_EMBEDDABLE` (HIGH, KDP exige
fontes incorporadas); binding que contradiz a classificação do papel →
`TYPE_ROLE_MISMATCH` (MEDIUM, heurística por metadado declarado); qualquer
tentativa de mudar `BODY` fora de `KDP_LAYOUT` → `READING_LAYER_MUTATION`.

### 17.5 Marca autoral BH SEAL

| Superfície | Uso | Justificativa |
|---|---|---|
| Lombada | **obrigatório** | reconhecimento de catálogo na estante; custo zero |
| Contracapa | **obrigatório** | assinatura junto à sinopse; não compete com o símbolo do livro |
| Folha de rosto / copyright | permitido | página funcional, sem disputa semântica |
| Aba de sobrecapa, box, quadrado de audiobook, promo | permitido | superfícies de catálogo |
| Collector (capa nua, lombada) | permitido, candidato a foil real | intenção `FI-BH-SEAL` com material assinatura |
| Frente da capa | não por padrão | a frente pertence ao livro (17.2) |
| Abertura de capítulo | **proibido** | a abertura é território do sigil narrativo; a marca ali seria decoração repetida 30 vezes (VP-01) |

A marca tem uma função só, `AUTHORIAL_IDENTITY` (11.3), é monocromática, tem
tamanho mínimo e área de proteção, e **é versionada com o DNA**: mudar a
marca = `AUTHOR_VISUAL_DNA.v2`.

### 17.6 THE HALDEN SPINE

**Avaliação de viabilidade.** Uma imagem contínua através de lombadas de
vários livros (muralha, fortaleza) exige larguras e alinhamento controlados.
No KDP isso não é garantível:

1. A largura da lombada é função da contagem de páginas e do papel
   (`páginas × 0,002252"` branco / `0,0025"` creme / `0,002347"` premium color —
   G201953020); cada livro tem largura própria.
2. A própria Amazon declara variação de produção de `0,0625"` de cada lado da
   dobra.
3. Ordem e proximidade dos volumes na estante do leitor não são controláveis.

**Decisão:**

| Modo | Status | Descrição |
|---|---|---|
| `INDIVIDUAL_CONSISTENT` | **MVP** | Gramática fixa em frações da altura (eixo do título, zona do autor, zona da marca, faixa de metal). Lado a lado, a *repetição rítmica* forma a "muralha" sem depender de largura. Cada lombada funciona sozinha. |
| `SERIES_CONTINUOUS` | FUTURE, só `box_set`/`collector` com perfil de gráfica | Arte panorâmica fatiada por largura real de cada volume (`COVER_GEOMETRY` de todos os volumes), tolerância de dobra absorvida por zonas neutras. |

Extensibilidade: `spine_grammar.mode` + `series: {id, volume_index,
continuous_art_ref}` no canon do livro; o validador só aceita
`SERIES_CONTINUOUS` quando todos os volumes têm geometria resolvida e o alvo
é `box_set` ou `collector` (`CONTINUOUS_SPINE_UNSUPPORTED_TARGET`).

---

## 18. Chapter Sigils

### 18.1 O que é

Um elemento `class: SIGIL` com `scope`, `assignment`, `states` e
`transitions` (seção 14). Representa, conforme `scope`: livro, personagem,
POV, estado psicológico, relação, perigo, objeto, pista ou passagem do tempo.
Várias famílias podem coexistir (ex.: sigil de livro + marcador de POV), mas
`author.density.max_dominant_per_surface` vale para `CHAPTER_OPENER`: **um**
sigil dominante por abertura.

### 18.2 Como a mudança de estado é ativada por narrativa

1. `SYMBOLISM_ARCHITECT` (`T042`) propõe a progressão a partir da
   "Evolution" do `SYMBOL_BIBLE` e dos estados S/R/T/P/E do `MEMORY_MOTIF_MAP`.
2. `VISUAL_DIRECTOR` (`T043`) registra cada transição com gatilho **âncora
   STRUCTURAL** (`LEDGER:EV-*`, `SCENE:*`, `TURN:N`) — ST-02.
3. POV e similares usam `assignment.mode: BY_CHAPTER_FIELD`, resolvido em
   `chapter_architecture.yaml` (campo `pov` existe em livros reais): nenhum
   número de capítulo é digitado.
4. Em `T311`, após o freeze, o validador confirma que o gatilho aconteceu na
   prosa/ledger (ST-06). Se a prosa mudou e o evento migrou de capítulo, a
   projeção **acompanha** automaticamente — é a vantagem de ancorar em evento e
   não em número.

### 18.3 Requisitos essenciais de legibilidade

| Requisito | Regra | Verificação |
|---|---|---|
| P&B | `render.mode` em `GLYPH`, `RASTER_1BIT` ou `VECTOR` monocromático | V6: raster com >5% de pixels em tons médios (luminância 0,15–0,85) → `SIGIL_NOT_MONOCHROME` (HIGH) |
| Kindle / telas pequenas | `min_render_size_mm ≥ 8` (default) | V6 com tamanho de colocação de `KDP_LAYOUT`/placement |
| Impressão comum | DPI efetivo na colocação ≥ 300 (mesma regra de `validate_media_assets.py` para miolo) | V6 |
| Sem depender de cor | diferença entre estados precisa ser de **forma**, não de cor: `states[].distinguishing_feature` obrigatório e não pode citar só cor | V6 `STATE_DIFFERS_ONLY_BY_COLOR` (HIGH, por palavras-chave de cor no campo) + revisão visual |
| Alternativa textual | `text_alternative` por estado (precedente: `alt_text_prefix` em `KDP_LAYOUT`) | V0 |
| Linhas | traço ≥ 0,75 pt na colocação (piso KDP para linhas) | declarado; render-QA do `GATE_KDP` |

### 18.4 Render

- **Caminho barato (padrão):** `GLYPH` — ornamento tipográfico ou arquivo
  1-bit desenhado uma vez; zero chamada de API. Funciona com
  `features.images.enabled: false` (inclusive perfil `DRAFT`).
- **Caminho premium:** `RASTER_1BIT`/`VECTOR` gerado em `T45N`
  (`IMAGE_GENERATOR`) e aprovado por `VISUAL_DIRECTOR`.
- **Inserção:** Slice 6 estende `build_kdp_docx.py`: quando existir
  `layout/editions/<target>/EDITION_PLAN.yaml` com `chapter_openers[]`, insere o
  asset do estado projetado acima do rótulo `CAPÍTULO N`. Sem plano →
  comportamento atual byte a byte (teste de regressão de DOCX).

### 18.5 Falhas específicas

`RANDOM_SIGIL_MUTATION` (estado difere entre capítulos consecutivos sem
transição) · `ARBITRARY_STATE_MUTATION` · `OPENER_PRE_ANNOUNCES_EVENT` ·
`SIGIL_NOT_MONOCHROME` · `SIGIL_DENSITY_EXCEEDED` · `SIGIL_WITHOUT_FUNCTION`.

---

## 19. Narrative Artifacts, Endpapers, Edges, Dust Jacket Duality

### 19.1 Narrative Artifact × Decorative Illustration

| | `NARRATIVE_ARTIFACT` | `DECORATIVE_ILLUSTRATION` |
|---|---|---|
| Existe dentro do universo da história | sim | não |
| Conteúdo | citado de canon/manuscrito, nunca inventado | livre |
| Exige âncora de origem e primeira aparição | sim | não |
| Exige dono in-world | sim (id de personagem ou instituição do canon) | não |
| Pode ser `DOMINANT` | sim, com `PROVEN` | não |
| Spoiler | obrigatório | só se evocar evento |

### 19.2 Campos adicionais de artefato (compostos com o canon existente)

```yaml
  - id: ART-CONTRACT
    class: NARRATIVE_ARTIFACT
    artifact_type: CONTRACT         # LETTER | CONTRACT | PHOTOGRAPH | POLAROID | MAP | DRAWING |
                                    # NEWSPAPER_CLIPPING | REPORT | DOCUMENT | NOTE | DIARY |
                                    # BLUEPRINT | MESSAGE | RECORD_CARD | SYMBOL | EVIDENCE
    canon_ref: LEDGER:EV-09          # ou CANON:<id>; o FATO do artefato mora no canon narrativo
    in_world_owner: CHR-HOUSE-VANE   # id existente no canon
    source: "Arquivo da família"     # procedência in-world
    first_appearance: TEXT:9:"o contrato dobrado em quatro"
    content:
      mode: QUOTED                   # QUOTED (literal da prosa congelada) | CANON_FACT | ILLEGIBLE_BY_DESIGN
      quotes: [TEXT:9:"cláusula quinta"]
    canon_status: REALIZED           # herdado do canon narrativo; artefato não tem status próprio de fato
    exposure: {spoiler_level: MEDIUM, reveal: LEDGER:EV-09}
    reveal_state: SEALED             # estados do artefato usam o mesmo mecanismo da seção 14
    payoff: SCENE:CROWN_REFUSAL
    placement: {surface: INTERIOR_PLATE, mode: AFTER, anchor: TEXT:9:"cláusula quinta"}
    accessibility: {text_alternative: "...", min_text_pt: 7, transcription_in_body: true}
```

Regras: `VISUAL_INVENTS_FACT` (conteúdo não resolve para citação ou fato);
`ARTIFACT_OWNER_UNKNOWN`; `ARTIFACT_BEFORE_FIRST_APPEARANCE` (placement antes
da âncora); `ARTIFACT_ILLEGIBLE` (texto essencial abaixo de 7 pt, piso KDP, ou
sem transcrição quando `transcription_in_body: false` e o texto é necessário
à trama). O schema da missão é seguido em espírito, mas **`first_appearance`,
`canon_status` e `payoff` são âncoras e referências**, não campos livres —
isso é o que "compor com o canon" significa aqui.

### 19.3 Endpapers

`compositions[]` com `surface: ENDPAPER_FRONT | ENDPAPER_BACK`.

| Tipo | Critério | Exigências |
|---|---|---|
| **Canônico** | contém ≥1 elemento `MOTIF`/`NARRATIVE_ARTIFACT`/`SIGIL` com função narrativa (mapa do lugar, antes/depois, dualidade) | Chekhov completo; spoiler por superfície (26.1) |
| **Decorativo** | só `TEXTURE` `DECORATIVE_ALLOWED` | orçamento decorativo; sem símbolo destacado |

Exposição: `ENDPAPER_FRONT` = pré-leitura (capítulo 0).
`ENDPAPER_BACK` = pré-leitura também (qualquer pessoa abre o fim do livro),
mas é classificada como superfície *semiescondida*: teto
`hidden_surface_max_spoiler` (Bea Halden v1: `MEDIUM`). "Antes/depois" é
permitido desde que o "depois" não mostre evento `CORE`.

### 19.4 Narrative Edges

`compositions[]` com `surface: EDGE_FORE | EDGE_TOP | EDGE_BOTTOM`;
`cost_class` efetivo sempre `COLLECTOR_ONLY` (nenhum alvo KDP tem a
superfície). Exigem `EDGE_ART: REQUIRE_APPROVAL`, Chekhov `PROVEN` para
qualquer motivo reconhecível (penas, rachaduras, fogo), e verificação de que o
motivo **não é spoiler** (bordas são a superfície mais exposta do objeto
físico). Fallback em KDP: `OMIT` — não há simulação honesta de borda
pintada; imprimir "bordas falsas" na capa seria gimmick (VP-01).

### 19.5 Dust Jacket × Naked Hardcover

Formalização por **camada de leitura** na composição, sem hardcode de exemplo:

```yaml
book_dna:
  duality:
    outer_truth:  "O que o mundo vê / primeira verdade."
    hidden_truth: "O que existe por baixo / segunda verdade."
    anchors: [LEDGER:GT-A-01, SCENE:CROWN_REFUSAL]
compositions:
  - {id: COMP-JACKET-FRONT, surface: FRONT_COVER, reading_layer: OUTER_TRUTH, ...}
  - {id: COMP-CASE-FRONT,   surface: CASE_FRONT,  reading_layer: HIDDEN_TRUTH, ...}
```

Regras:

| ID | Regra | Achado |
|---|---|---|
| DJ-01 | `HIDDEN_TRUTH` só em superfície semiescondida (`CASE_*` sob sobrecapa, `ENDPAPER_BACK`) e só em alvo que tenha sobrecapa física | `HIDDEN_TRUTH_EXPOSED` (BLOCKER) |
| DJ-02 | Spoiler da hidden truth ≤ `hidden_surface_max_spoiler` | `HIDDEN_SURFACE_SPOILER` (HIGH) |
| DJ-03 | As duas camadas compartilham ≥1 elemento (a dualidade é *do mesmo* símbolo, não duas capas) | `DUALITY_WITHOUT_SHARED_ELEMENT` (MEDIUM) |
| DJ-04 | `duality.anchors` resolvem (a segunda verdade é canon, não marketing) | `UNJUSTIFIED` |
| DJ-05 | Em `kdp_hardcover` (case laminate), o case recebe **OUTER_TRUTH** | projeção automática, registrada |

---

## 20. Physical Edition Model

### 20.1 Superfícies (vocabulário fechado, neutro)

`MARKETING_COVER`, `INTERNAL_COVER`, `FRONT_COVER`, `BACK_COVER`, `SPINE`,
`CASE_FRONT`, `CASE_BACK`, `CASE_SPINE`, `DUST_JACKET_FRONT`,
`DUST_JACKET_BACK`, `DUST_JACKET_SPINE`, `DUST_JACKET_FLAP_FRONT`,
`DUST_JACKET_FLAP_BACK`, `ENDPAPER_FRONT`, `ENDPAPER_BACK`, `EDGE_TOP`,
`EDGE_FORE`, `EDGE_BOTTOM`, `TITLE_PAGE`, `COPYRIGHT_PAGE`, `CHAPTER_OPENER`,
`INTERIOR_PLATE`, `INSERT`, `RIBBON`, `BOX_*`, `AUDIO_SQUARE`, `PROMO`.

Cada superfície tem no template: `exposure: PUBLIC | SEMI_HIDDEN | IN_READING`,
`physical: bool`, e — quando impressa — referência de geometria.

### 20.2 Special Finish Semantics

A intenção é armazenada como **material semântico + efeito preferido +
escada de fallback + significado**. Isso é melhor que o exemplo da missão em
dois pontos: (1) o fallback é uma **lista ordenada** resolvida por capacidade,
não um único fallback; (2) o acabamento aponta para um **elemento com
significado** (`meaning_element`), então Visual Chekhov vale também para foil
e verniz — "foil porque é premium" falha.

| Campo | Exemplo | Nota |
|---|---|---|
| `target` | `{composition: COMP-FRONT, role: TITLE}` ou `{composition, element: SYM-SWAN, part: FEATHERS}` | parte nomeada vira camada no artwork |
| `semantic_material` | `BURNT_COPPER`, `AGED_GOLD`, `OBSIDIAN_GLOSS`, `BONE_MATTE` | material, não cor |
| `preferred_effect` | `METALLIC_FOIL`, `SPOT_UV`, `EMBOSS`, `DEBOSS`, `SPRAYED_EDGE` | vocabulário de 16.2 |
| `fallbacks` | `[SIMULATED_METALLIC_PRINT, FLAT_ROLE_COLOR]` | ordem importa |
| `meaning_element` | `SYM-CROWN` | Chekhov |
| `cost_class` | `PREMIUM` | orçamento por alvo |
| `must_survive_grayscale` | `false` | `true` para qualquer coisa essencial |
| `layer_name` | `L_FOIL_TITLE` | contrato com o artwork para gerar máscara (seção 22) |

Materiais semânticos têm, no Author DNA ou canon do livro, um mapeamento para
simulação (`SIMULATED_METALLIC_PRINT` de `AGED_GOLD` = gradiente declarado em
papéis `METAL`), para que Kindle e KDP simulem **o mesmo** material.

---

## 21. KDP Strategy

### 21.1 CREATIVE DESIGN × MANUFACTURING GEOMETRY

```text
CREATIVE DESIGN (canon)            zonas normalizadas [0..1] por superfície; nunca polegadas
        +
PRINT_SPEC (fatos do livro)        trim, contagem final de páginas, papel, tinta, alvo
        +
PRINT_GEOMETRY (fatos do fabricante, template com proveniência)
        ↓ T707_PRINT_GEOMETRY (tool, determinístico)
COVER_GEOMETRY (projeção)          polegadas/mm/pixels de cada superfície do wrap
        ↓ (FUTURE) gerador de wrap
PDF de capa
```

Nenhuma dimensão física aparece no canon. Uma composição aprovada sobrevive a
uma mudança de trim ou de contagem de páginas sem nova aprovação — só a
geometria é recalculada; a aprovação cobre intenção e zonas, não polegadas.

### 21.2 `layout/PRINT_SPEC.yaml` (fatos do livro)

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: PrintSpec
spec:
  kdp_paperback:
    trim_in: {width: 6.0, height: 9.0}        # default: KDP_LAYOUT.page (fonte única com o interior)
    interior: {ink: BLACK, paper: CREAM}        # BLACK/CREAM | BLACK/WHITE | STANDARD_COLOR | PREMIUM_COLOR
    page_count: null                            # OBRIGATÓRIO antes de T707; medido no render de T704/T705
    page_count_source: /qa/<render>/PAGE_COUNT.txt
    laminate: MATTE
  kdp_hardcover:
    trim_in: {width: 6.0, height: 9.0}
    interior: {ink: PREMIUM_COLOR, paper: WHITE}
    page_count: null
    laminate: MATTE
```

`page_count: null` em alvo impresso → `T707` falha (`PAGE_COUNT_UNKNOWN`,
defeito de entrada). O motor não estima contagem de páginas.

### 21.3 `engine/templates/PRINT_GEOMETRY.yaml` (fatos do fabricante)

Valores iniciais propostos, verificados em 2026-09-14 em fontes oficiais,
com `sources` por chave; `T699` revalida.

```yaml
kdp_paperback:
  bleed_in: 0.125                     # topo, base, bordas externas
  safe_from_trim_in: 0.125
  spine_text_min_pages: 79
  spine_text_clearance_in: 0.0625
  fold_variance_in: 0.0625
  spine_in_per_page: {BLACK/WHITE: 0.002252, BLACK/CREAM: 0.0025, PREMIUM_COLOR: 0.002347, STANDARD_COLOR: 0.002252}
  color_space_required: CMYK
  min_image_dpi: 300
  file: {format: PDF, single_spread: true, recommended_max_mb: 40}
  barcode_zone: {source: KDP_COVER_TEMPLATE, status: TO_VERIFY}   # OQ-8
kdp_hardcover:
  construction: CASE_LAMINATE
  wrap_in: 0.51
  hinge_in: 0.4
  safe_from_edge_in: 0.635
  spine_in_per_page: {status: TO_VERIFY, rule: "obter do KDP Cover Calculator"}  # OQ-8
  page_range: {status: TO_VERIFY}                                                # D-V8
kindle_ebook:
  marketing_cover_px: {width: 1600, height: 2560}
  color_space_required: RGB
  min_dpi: 300
  max_mb: {value: 5, status: TO_VERIFY_AGAINST_ENGINE_50MB}                      # D-V4
```

Chaves com `status: TO_VERIFY` são **proibidas** em cálculo: `T707` recusa
calcular com elas (`MANUFACTURING_FACT_UNVERIFIED`) em vez de inventar.

### 21.4 `layout/editions/<target>/COVER_GEOMETRY.yaml` (projeção)

Para paperback, com `W` = trim width, `H` = trim height, `S` = páginas ×
fator, `B` = bleed:

```text
full_width  = B + W + S + W + B
full_height = B + H + B
BACK_COVER  = [B, B, B+W, B+H]
SPINE       = [B+W, B, B+W+S, B+H]      (texto só se páginas ≥ 79; zona segura S − 2×0,0625)
FRONT_COVER = [B+W+S, B, B+2W+S, B+H]
safe(front/back) = recuo de 0,125 de cada trim
pixels = polegadas × 300
```

Hardcover usa `wrap_in`, `hinge_in` e `safe_from_edge_in` no lugar de
bleed/safe, com fator de lombada vindo do template quando verificado.

Mapeamento criativo → físico: cada `placement.zone` normalizado é aplicado ao
retângulo **seguro** da superfície (tipografia) ou ao retângulo **com bleed**
(fundo). Um elemento cuja zona projetada toca a zona de código de barras ou a
tolerância de dobra → `ZONE_COLLIDES_WITH_MANUFACTURING` (HIGH).

### 21.5 O que o KDP recebe de cada intenção

| Intenção | kdp_paperback / kdp_hardcover |
|---|---|
| Foil de título | `SIMULATED_METALLIC_PRINT` com gradiente do material; nota no plano: "sem foil físico" |
| Spot UV em penas | `CONTRAST_SIMULATION` (penas em preto brilhante simulado sobre preto fosco de laminação matte) |
| Emboss de coroa | `TONAL_RELIEF_SIMULATION` ou `OMIT` conforme fallback |
| Sobrecapa / capa nua | case recebe OUTER_TRUTH; HIDDEN_TRUTH omitida (DJ-05) |
| Bordas, guardas, fita | `OMIT`, registrado |
| Sigils, artefatos | físicos no interior (P&B) |

O sistema **nunca** gera texto de marketing, briefing ou manifesto afirmando
acabamento não fabricado (`FINISH_PROMISE_MISMATCH`: V7 varre
`media/KDP_DESCRIPTION_*.txt` e `COVER_PRODUCTION_REPORT.md` por termos de
acabamento — foil, emboss, spot UV, sprayed edges, dust jacket, e equivalentes
PT — que não estejam `PHYSICAL` no plano da edição).

---

## 22. Collector Strategy

### 22.1 Pré-condição

Collector não é um fabricante: é uma **classe** de edição. Sem
`layout/PRINTER_PROFILE.yaml` (capacidades confirmadas da gráfica escolhida,
com data e contato registrado por humano), todo `VENDOR_DEPENDENT` resolve
como `UNSUPPORTED` e o plano sai marcado `PRINTER_UNCONFIRMED`.

### 22.2 Contrato do manifesto de produção (sem gerar ativos)

`layout/editions/collector/PRODUCTION_MANIFEST.yaml`, produzido por
`T709_COLLECTOR_PRODUCTION_SPEC` (`BOOK_LAYOUT_ARCHITECT`) a partir do
`EDITION_PLAN` — o agente escreve instruções, a lista de ativos é projetada:

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: CollectorProductionManifest
metadata: {project_id: <slug>, canon_version: 0.3.0, plan_sha256: "…", printer_profile: <id>}
assets:
  - id: A-JACKET-FULL
    kind: FULL_ARTWORK              # FULL_ARTWORK | FRONT | BACK | SPINE | DUST_JACKET | NAKED_CASE |
                                    # FOIL_MASK | EMBOSS_MASK | DEBOSS_MASK | SPOT_UV_MASK | DIE_CUT_MASK |
                                    # ENDPAPER_ART | EDGE_ART | INSERT_CARD | PRINTER_INSTRUCTIONS |
                                    # MATERIAL_FINISH_MANIFEST
    surface_set: [DUST_JACKET_FLAP_BACK, DUST_JACKET_BACK, DUST_JACKET_SPINE, DUST_JACKET_FRONT, DUST_JACKET_FLAP_FRONT]
    geometry_ref: COVER_GEOMETRY.collector.dust_jacket
    color_space: CMYK
    min_dpi: 300
    layers_required: [L_ART, L_TYPE, L_FOIL_TITLE, L_SPOT_UV_FEATHERS]
    status: SPECIFIED               # SPECIFIED | PRODUCED | APPROVED
    file: null
    sha256: null
  - id: A-FOIL-TITLE
    kind: FOIL_MASK
    derived_from: {asset: A-JACKET-FULL, layer: L_FOIL_TITLE}
    finish_intent: FI-TITLE
    mask_rules: {mode: VECTOR_OR_1BIT, ink: "100% K", registration: SAME_GEOMETRY_AS_PARENT,
                 min_line_pt: VENDOR, min_gap_pt: VENDOR}
    material: {semantic: AGED_GOLD, vendor_code: null}   # código do fornecedor é humano
materials:
  - {finish_intent: FI-TITLE, effect: METALLIC_FOIL, surface: DUST_JACKET_FRONT, vendor_confirmed: false}
printer_instructions:
  - "Instruções em linguagem natural, geradas por T709, citando ids de ativos."
```

### 22.3 Como as máscaras técnicas poderão ser produzidas depois

A regra que torna máscaras **deriváveis** é imposta agora, no contrato:

1. Toda `finish_intent` com efeito físico declara `layer_name`.
2. O artwork do collector é entregue **em camadas nomeadas** (`layers_required`).
3. Máscara = rasterização/vetorização de uma camada, na mesma geometria, em
   100% K — operação mecânica (FUTURE: `tool` determinística).
4. `V8` confere: todo efeito `PHYSICAL` no plano tem um ativo de máscara
   especificado; toda máscara aponta para uma `finish_intent` existente; toda
   `finish_intent` aponta para um elemento com Chekhov válido.

Hot foil sem significado (`FI` sem `meaning_element` resolvido) falha antes
de chegar à gráfica.

---

## 23. Validation / Gates

### 23.1 Simplificação dos onze gates pedidos

**Nenhum gate novo.** Um validador (`check_visual_canon.py`) com famílias de
regras `V0`–`V9`, anexado a quatro gates existentes, mais agentes existentes
para o resíduo de julgamento.

| Gate pedido | Implementação | Onde roda | Bloqueante |
|---|---|---|---|
| G0 CONTRACT VALIDATION | **V0** integridade: ids únicos, enums, âncoras sintaticamente válidas, referências internas resolvem, pin de Author DNA com sha256 correto | todos os modos | sim |
| G1 AUTHOR DNA CONSISTENCY | **V1** papéis de cor (faixas), invariantes, overrides com razão, DNA sem símbolo de livro, marca nas superfícies obrigatórias | plan, assets | sim |
| G2 BOOK CANON SUPPORT + G3 VISUAL CHEKHOV | **V2** (fundidos: suporte é a condição do Chekhov) — resolução de âncoras, status 11.5, contagem, função, artefato não inventa fato | plan, realized | sim (HIGH) |
| G4 ANTI-GENERIC | **V3** watchlist exige `PROVEN`; overload; `ATMOSPHERE_ONLY_PROMINENT`; `IMITATION_REFERENCE` + REUSE `GENRE_GUARDIAN`, `T602` | plan, assets | estrutural sim; julgamento editorial |
| G5 THUMBNAIL | **V4** heurísticas sobre JPEG + miniaturas salvas para inspeção | assets | MEDIUM por padrão; `HIGH` para título ilegível |
| G6 READABILITY | **V6** monocromia de sigils, tamanhos, DPI efetivo, corpo intacto + REUSE render-QA `T704` | realized, edition, assets | sim para essenciais |
| G7 SPOILER SAFETY | **V5** exposição por superfície × âncora de revelação + REUSE `PROTECTED_SCENE_AUDITOR` | plan, realized, edition | sim |
| G8 EDITION CAPABILITY | **V7** resolução de acabamentos, `EDITION_CHANGES_MEANING`, `FINISH_PROMISE_MISMATCH`, hidden truth | edition | sim |
| G9 MANUFACTURING SPEC | **V8** PRINT_SPEC completo, fatos verificados, colisões de zona, manifesto collector coerente | edition | sim para alvos impressos selecionados |
| G10 FINAL VISUAL CANON | **V9** aprovações humanas com hash atual + snapshot `FREEZE` + imutabilidade `ST-08` + checkpoint humano existente em `GATE_FULL_MANUSCRIPT` (STANDARD/PREMIUM) | realized, edition | sim |

### 23.2 Modos e anexação

| Modo | Regras | Gate | Validator id |
|---|---|---|---|
| `plan` | V0, V1, V2, V3, V5, V7 (dry-run), V9 (decisões `REQUIRE_APPROVAL` já decididas) | `GATE_LIVING_BOOK` | `V_VISUAL_CANON_PLAN` |
| `realized --baseline snapshots/…PLAN.yaml` | V0, V2 (âncoras `TEXT:` e ledger `REALIZED`), V5, V6 (declarado), V9, ST-01..ST-09 | `GATE_FULL_MANUSCRIPT` | `V_VISUAL_CANON_REALIZED` |
| `edition --baseline snapshots/…FREEZE.yaml` | V0, V6, V7, V8, V9 | `GATE_KDP` | `V_VISUAL_EDITION` |
| `assets` | V1 (deriva de paleta em pixels), V3, V4, V6 (ativos), proveniência | `GATE_MEDIA_ASSETS` | `V_VISUAL_ASSETS` |

Saída: Markdown ou `--json`, achados no shape de `REVIEW_FINDING`; exit 1 com
`HIGH`/`BLOCKER`. `GATE_TRANSLATION_PREP` e gates rebaixáveis por perfil não
recebem nenhum validador desta capability. Nenhum dos quatro gates acima está
em `non_blocking_gates` de nenhum perfil hoje.

### 23.3 Visual Chekhov Validator — "WHY IS THIS HERE?"

Para cada `(element, surface)`:

```text
1. resolve cada âncora → {ok, strength, chapter, excerpt}
2. aplica tabela 11.5 → status
3. se count > 1 e prominence ≥ SUPPORTING → count_rationale resolve?
4. se states → ST-01..ST-07
5. se finish_intent aponta para o elemento → herda o status (foil sem Chekhov = UNJUSTIFIED)
6. emite linha de explicabilidade (seção 25) mesmo quando PASS
```

Estados `PROVEN`, `SUPPORTED`, `DECORATIVE_ALLOWED`, `UNJUSTIFIED`,
`CONTRADICTORY` — exatamente os da missão, cada um com condição
determinística. O resíduo ("a âncora sustenta *este* significado?") vai para
o spawn de `T043` e para o checkpoint humano; o script nunca finge julgar
simbolismo.

### 23.4 Anti-Generic Gate

Não proíbe objetos; proíbe **uso sem justificativa**.

| Detector | Regra determinística | Achado |
|---|---|---|
| generic skull/rose/knife/crown/shirtless male/chains/blood | elemento casa `generic_trope_watchlist` (label, `meaning` ou `visual_description`) e status ≠ `PROVEN` | `GENERIC_TROPE_UNJUSTIFIED` (HIGH) |
| decorative blood | watchlist `BLOOD` + `class: DECORATIVE_ILLUSTRATION` | `DECORATIVE_VIOLENCE` (HIGH) |
| symbol with no narrative support | status `UNJUSTIFIED` | `UNJUSTIFIED` (HIGH) |
| visual overload | `DOMINANT` > 1, `SECONDARY` > máx., elementos totais > `max_dominant + max_secondary + decorative_budget` | `VISUAL_OVERLOAD` (HIGH) |
| poor thumbnail readability | V4 | ver 23.5 |
| copycat composition | campos `style_reference`, `in the style of`, nomes próprios de autoras/marcas em `atmosphere`/`visual_description` (lista mantida no Author DNA) | `IMITATION_REFERENCE` (HIGH) + REUSE `T602` com o canon como input |
| author DNA drift | V1 R1 + em pixels: 5 cores dominantes do JPEG (quantização Pillow) vs papéis; área de PULSE > `max_area_ratio` | `AUTHOR_DNA_DRIFT` (MEDIUM em pixels, HIGH em canon) |
| "porque o gênero tem" | função declarada só `ATMOSPHERE` em elemento destacado | `ATMOSPHERE_ONLY_PROMINENT` (MEDIUM) |

Uma rosa com `functions: [{function: MEMORY, anchors: [LEDGER:EV-03, SCENE:ROSE_GARDEN_CONTRACT]}]`
passa como `PROVEN`. A mesma rosa com `anchors: []` falha como
`GENERIC_TROPE_UNJUSTIFIED`.

### 23.5 Thumbnail Gate

Contrato primeiro, heurística simples, sem visão computacional complexa.
Somente Pillow (já instalado).

| Critério | Heurística | Limiar default (configurável no Author DNA) |
|---|---|---|
| leitura reduzida | gerar miniaturas em larguras `[320, 160, 96]` px → `media/outputs/thumbnails/` para inspeção humana/agente (precedente `loja`: 320×512) | arquivos existem |
| título | na zona `typography[TITLE].zone`, a diferença de luminância entre percentis p95 e p5 na miniatura de 160 px | ≥ 0,45 |
| contraste | razão de contraste WCAG entre mediana da tinta (pixels mais claros/escuros da zona) e fundo | ≥ 4,5 : 1 |
| focal point | razão da energia de borda (filtro `FIND_EDGES`) dentro da zona do `DOMINANT` vs fora | ≥ 1,3 |
| author visibility | mesmo teste de título na zona `AUTHOR`, miniatura 320 | ≥ 0,35 |
| clutter | densidade média de borda na miniatura 160 | ≤ limiar da autora |
| silhouette | binarização por Otsu na zona do `DOMINANT` na miniatura 96: componente conexo principal ≥ 25% da zona | se `silhouette_readable: true` |
| recognizability | **não automatizado**: miniatura 96 px na revisão `T801` e no checkpoint humano | resíduo |
| grayscale | todos os critérios repetidos sobre `convert('L')` (e-ink) | — |

Limites honestos: as heurísticas medem condições necessárias, não
suficientes. Título ilegível → HIGH; demais → MEDIUM. Os limiares iniciais são
propostos e **calibrados no Slice 4** contra as capas reais já produzidas
(`eva` antes/depois, `loja` preview), como `TEXT_QUALITY_DEFAULTS.yaml` foi
calibrado contra um manuscrito real.

### 23.6 Readability / Accessibility

| Superfície | Regra |
|---|---|
| Corpo de texto | intocável (ST-09, 17.4) |
| Kindle grayscale / e-ink | sigils e artefatos essenciais passam V6 em `L`; nenhum significado só por cor |
| Telas pequenas | sigil ≥ 8 mm; artefato com texto essencial transcrito no corpo ou ≥ 7 pt |
| Impressão P&B | DPI efetivo ≥ 300; linhas ≥ 0,75 pt |
| Contraste | capa: 23.5; interior: fundo de artefato não pode baixar contraste do texto citado abaixo de 4,5:1 |
| Densidade decorativa | aberturas: 1 sigil dominante; progressão interna nunca adiciona ornamento ao corpo de página |
| Texto alternativo | todo elemento em interior tem `text_alternative` (padrão `alt_text_prefix` existente) |

---

## 24. Failure Modes

| Failure mode | Como aparece | Detecção | Onde |
|---|---|---|---|
| Capa de Dark Romance genérica | caveira/rosa/coroa sem história | V3 `GENERIC_TROPE_UNJUSTIFIED` + `COMMERCIAL_EDITOR_CRITIC` | plan |
| Todos os livros iguais | autora vira repertório de símbolos | V1 `AUTHOR_LAYER_CONTAINS_BOOK_SYMBOL`; `DOMINANT_NOT_BOOK_SPECIFIC`; FUTURE: comparação entre canons | plan / portfólio |
| Deriva visual entre execuções | nova sessão escolhe outra paleta/composição | canon + snapshot + `DERIVED_ARTIFACT_EDITED` + aprovação com hash | todos |
| Regra tática vira dogma (caso `eva`) | veto de produção tratado como narrativo | `rule_kind: TACTICAL` + `expires_when` | plan |
| Sigil muda "porque chegou o capítulo 15" | gatilho numérico | ST-02 `ARBITRARY_STATE_MUTATION` | plan |
| Sigil anuncia o evento na abertura | `SAME_CHAPTER` sem ack | `OPENER_PRE_ANNOUNCES_EVENT` | plan / realized |
| Sigil ilegível em e-ink | significado por cor | `SIGIL_NOT_MONOCHROME`, `STATE_DIFFERS_ONLY_BY_COLOR` | realized / assets |
| Artefato inventa fato | carta com conteúdo que a prosa não tem | `VISUAL_INVENTS_FACT` | realized |
| Spoiler na capa, borda, guarda traseira, Stories | revelação central em superfície pública | V5 | plan / assets |
| Hidden truth exposta no KDP | fallback leva capa nua ao case laminate | DJ-01 `HIDDEN_TRUTH_EXPOSED` | edition |
| Promessa de acabamento inexistente | descrição KDP menciona foil | `FINISH_PROMISE_MISMATCH` | edition |
| Geometria inventada | fator de lombada de hardcover chutado | `MANUFACTURING_FACT_UNVERIFIED` | edition |
| Corpo de texto sacrificado pela identidade | fonte de corpo "gótica" | `READING_LAYER_MUTATION` | edition |
| Cópia de capa existente | "no estilo de…" | `IMITATION_REFERENCE` + `T602` | plan / legal |
| Candidato vira canon sem decisão | renderer lê `VISUAL_CANDIDATES.yaml` | `CANDIDATE_CONSUMED` | edition |
| Aprovação humana envelhecida | bloco muda depois de aprovado | `APPROVAL_STALE` (hash) | todos |
| Author DNA alterado depois de publicado | edição silenciosa de v1 | `AUTHOR_DNA_TAMPERED` (sha256 do pin) | todos |
| Gimmick de progressão | página inteira "deteriora" | ST-09; progressão limitada a elementos declarados | realized |
| Overengineering | tipos por superfície, engines por conceito | seção 36; um tipo `composition`, um script | processo |
| Custo explode | todo livro vira collector | `cost_class` × orçamento por alvo; `GLYPH` como padrão | plan |

---

## 25. Observability

Todas as respostas vêm do mesmo canon e do mesmo script. Nenhum log novo.

| Pergunta | Comando | Resposta |
|---|---|---|
| WHY IS THIS HERE? | `check_visual_canon.py --runtime . --why SYM-SWAN` | significado, funções, cada âncora com tipo/força/capítulo/trecho, status Chekhov, aprovação, superfícies |
| Quanta evidência existe? | `--evidence "cisne" "swan"` | ocorrências por capítulo no manuscrito (se existir) e por arquivo de bíblia |
| Qual o estado no capítulo N? | `--state SIG-SWAN --at-chapter 27` | estado, transição que o produziu, gatilho, capítulo do gatilho, regra de exibição |
| Linha do tempo visual | `--timeline` | por capítulo: sigils, estados, artefatos expostos |
| O que cada edição recebe? | `--edition-plan kdp_hardcover` | por intenção: efeito escolhido, nível, fallbacks descartados e por quê |
| Por que este acabamento virou simulação? | `--resolve FI-TITLE --edition kdp_paperback` | escada com o nível de cada degrau |
| O que é spoiler onde? | `--exposure` | matriz elemento × superfície × exposição × revelação |
| Qual geometria? | `--geometry kdp_paperback` | retângulos em pol./px e fórmula aplicada |
| Estado para continuação | `--end-state` | estado final de todo elemento progressivo |

Formato de explicação obrigatório (exemplo de saída):

```text
WHY: DOMINANT(FRONT_COVER) = SYM-SWAN  [PROVEN]
MEANING: a persona perfeita que Isadora foi treinada para ser
EVIDENCE:
  CHARACTER      LEDGER:GT-A-01          STRUCTURAL  reader_access from EV-19
  TRANSFORMATION SCENE:CROWN_REFUSAL     STRUCTURAL  ch.19
  MEMORY         DOC:SYMBOL_BIBLE#swan   SUPPORTED   evolução em 4 estados
  mentions: manuscript 31 (ch.1–28, 17 capítulos distintos), bibles 14
APPROVAL: APR-03 (hash ok, 2026-09-20)
NOT: "escolhido porque é bonito" — nenhuma função ATMOSPHERE-only
```

Persistência: `validate-gate` já grava stdout/stderr em
`PROJECT_STATUS.yaml → validator_results`; relatórios legíveis em
`reviews/VISUAL_CANON_REPORT_<mode>.md`. **Proteção de vazamento:** `--why` e
`--exposure` omitem `hidden_truth`, `reveal` e trechos de GT não divulgada por
padrão; `--engine-view` é explícito — mesma regra do ledger, para que um
brief de capa não receba por colagem a revelação que a capa não pode mostrar.

---

## 26. Security / IP / Spoilers / Human-in-the-loop / Cost

### 26.1 Spoiler Safety

Modelo: **exposição é tempo.** Cada superfície tem um capítulo de exposição;
cada elemento tem nível e âncora de revelação.

| Superfície | Exposição | Teto de spoiler (Bea Halden v1) |
|---|---|---|
| `MARKETING_COVER`, `FRONT/BACK_COVER`, `SPINE`, `CASE_*` sem sobrecapa, `DUST_JACKET_*`, `EDGE_*`, `PROMO`, Stories | capítulo 0, `PUBLIC` | `LOW` |
| `ENDPAPER_FRONT` | capítulo 0, `PUBLIC` | `LOW` |
| `CASE_*` sob sobrecapa, `ENDPAPER_BACK`, `INSERT` lacrado | capítulo 0, `SEMI_HIDDEN` | `MEDIUM` |
| `CHAPTER_OPENER` do capítulo N | N (antes da prosa) | por âncora (14.2) |
| `INTERIOR_PLATE` com `AFTER`/`HINGE` | N, após o parágrafo-âncora | por âncora |

Regras V5:

- `spoiler_level > teto(superfície)` → `SURFACE_SPOILER` (HIGH; `CORE` em
  superfície pública → BLOCKER).
- `spoiler_level ≥ MEDIUM` sem `reveal` resolvida → `SPOILER_UNANCHORED` (HIGH).
- `exposure_chapter(superfície) < chapter(reveal)` → `PREMATURE_EXPOSURE` (HIGH).
- Com `causal_ledger`: elemento cuja âncora é `GT-*` com `reader_access` futuro
  herda `reveal = reader_access.from_event` automaticamente (INV-12 da SDD irmã
  aplicado a pixels).
- `T800`/`T802` (Stories, descrição) recebem `--exposure` público como input.

Collector não é exceção: capa nua é `SEMI_HIDDEN`, não privada.

### 26.2 Human-in-the-loop

| Política | Efeito |
|---|---|
| `AUTO` | decisão vale ao ser escrita pelo dono |
| `SUGGEST` | vale; aparece em lista de revisão do gate |
| `REQUIRE_APPROVAL` | status `PENDING_APPROVAL` até existir `project_state/APPROVALS/VISUAL/<APR-id>.md` escrito por humano contendo `subject_sha256` igual ao hash canônico (JSON ordenado) do bloco aprovado |

Decisões de alto impacto e política mínima (nenhum perfil rebaixa; livro só
pode **subir**): Author mark, Author DNA (`REQUIRE`); cover composition,
dominant symbol, collector finishes, hidden hardcover, edge art, figura
humana/personagem em capa (`REQUIRE`); canonical artifact (`REQUIRE` se
`spoiler_level ≥ MEDIUM`, senão `SUGGEST`); sigil states (`SUGGEST` no plano,
cobertos pelo checkpoint humano de `GATE_FULL_MANUSCRIPT` no freeze); paleta
dentro dos papéis (`AUTO`).

O motor nunca escreve arquivo de aprovação (regra existente). Mudança no bloco
depois da aprovação → `APPROVAL_STALE`.

### 26.3 IP / Originality

- Nenhum campo do canon aceita referência nominal a capa, autora, marca ou
  obra de terceiros como *estilo* (`IMITATION_REFERENCE`). Princípios gerais de
  design (hierarquia, espaço negativo, contraste) são livres.
- `T602_ORIGINALITY_AUDIT` recebe o canon, as composições aprovadas e as
  miniaturas como input, com instrução explícita de comparar composição e
  símbolos contra identidades reconhecíveis.
- Símbolo de domínio público (cisne, coroa) não imuniza **composição**
  protegida: ver risco concreto no worked example (30.9).
- Fontes: binding exige licença e `embeddable: true`.
- Proveniência de pixels: prompt, modelo, fonte, hash — mesma regra do
  `MEDIA_ASSET_MANIFEST.md`; imagens de IA declaradas conforme política KDP já
  registrada em `KDP_CURRENT_REQUIREMENTS.md`.
- Marca BH: registro de marca é decisão legal humana (OQ-6), fora do motor.

### 26.4 Cost Awareness

| Classe | Significado | Exemplos |
|---|---|---|
| `ESSENTIAL` | todo alvo precisa; nunca omitido | capa, hierarquia tipográfica, marca na lombada, sigil `GLYPH` se o livro tem sigils |
| `OPTIONAL` | escalável | artefatos em página própria, marcador de POV |
| `PREMIUM` | só simulado fora do collector | foil, spot UV, relevo como intenção |
| `COLLECTOR_ONLY` | nunca aparece fora do collector | bordas, sobrecapa, guardas físicas |

`features.visual_narrative.budget: MINIMAL | STANDARD | COLLECTOR` limita
quais classes o `T043` pode propor (MINIMAL = só ESSENTIAL). Perfil `DRAFT`
força `MINIMAL` e `render: GLYPH` (não pode desligar gates hard).
Degradação elegante = a escada de fallback + omissão registrada; o livro
Kindle continua completo, não "versão pobre".

---

## 27. Versioning / Determinism

### 27.1 CANONICAL DESIGN SPEC × GENERATED ARTIFACT

| | Canonical Design Spec | Generated Artifact |
|---|---|---|
| O quê | Author DNA pinado, canon visual, `EDITION_PLAN`, `COVER_GEOMETRY`, manifestos | JPEG, PNG, PDF, máscaras |
| Variação | **nenhuma**: mesma entrada → mesmo arquivo byte a byte (YAML ordenado, sem timestamps no corpo das projeções) | permitida |
| Reprodução | reexecutar `T698`/`T707` | regenerar com mesma spec; resultado pode diferir e precisa de nova aprovação visual |
| Prova | `plan_sha256`, `canon_version` | SHA-256 no manifesto + `generated_from` |
| Aprovação cobre | conceito, composição (zonas), símbolos, cores, hierarquia, materiais, significados | pixel específico aprovado |

Teste de determinismo: projeções executadas duas vezes geram o mesmo hash
(Slice 3).

### 27.2 Author DNA v1 → v2 sem retroatividade

1. `AUTHOR_VISUAL_DNA.v1.yaml` é **imutável** a partir do primeiro `release`
   de qualquer livro que o pine; o validador compara sha256.
2. Mudança = novo arquivo `v2`, `supersedes: 1`, `v1.status: SUPERSEDED` (única
   mutação permitida em v1: esse campo de metadado fica fora do hash — o hash é
   calculado sobre o documento sem `metadata.status`).
3. Livros publicados continuam pinados em v1 e continuam validando.
4. Um livro migra só por decisão explícita: novo pin + `mutation_log` +
   revalidação completa + nova aprovação das decisões afetadas.
5. `--dna-diff 1 2` lista invariantes e papéis alterados, para estimar impacto
   no catálogo.

### 27.3 Book Visual Canon

- `metadata.version` semver: patch = texto/explicação; minor = elemento ou
  composição nova sem alterar aprovado; major = altera algo aprovado ou
  `REALIZED`.
- Snapshots: `PLAN`, `FREEZE`, `RELEASE_<edition>_<n>`.
- `releases[]`: edição publicada congela `canon_version` + `plan_sha256` +
  `assets_manifest_sha256`. Edição nova (ex.: segunda impressão com capa
  revisada) = nova entrada, nunca sobrescrita.
- `VISUAL_RETCON` (BLOCKER): mudança em transição/elemento `REALIZED` contra
  `FREEZE` sem entrada `mutation_log.action: VISUAL_REVISION` + aprovação.

---

## 28. Backward Compatibility / Configuration

### 28.1 Ativação

Segue exatamente o padrão de `features.*` do `BOOK_SPEC.yaml`:

```yaml
# books/<slug>/BOOK_SPEC.yaml
metadata:
  author: Bea Halden                 # REUSE — já é o autor publicado (SDD irmã, S.2)
spec:
  features:
    visual_narrative:
      enabled: true                  # ausente ≡ false
      author_profile: bea_halden     # → authors/bea_halden/
      author_dna_version: 1          # pin explícito; sem "latest"
      edition_targets: [kindle_ebook, kdp_paperback, kdp_hardcover, collector]
      budget: STANDARD               # MINIMAL | STANDARD | COLLECTOR
      sigils: true                   # opcional; default false
      thumbnail_widths_px: [320, 160, 96]   # opcional
```

Mapeamento dos nomes da missão: `visual_narrative.enabled` ✅;
`author_identity.profile` → `visual_narrative.author_profile` (dentro da mesma
feature para não criar chave de topo nova em `spec`); `edition_targets` ✅.
`kindle` → `kindle_ebook` para não confundir com o "KDP JPEG" que o motor já
chama de capa Kindle.

### 28.2 O que muda quando ligada (e só então)

| Ponto | Mudança condicional |
|---|---|
| `validate_book_data` | se ligada: `authors/<profile>/AUTHOR_VISUAL_DNA.v<N>.yaml` existe; `public_name == metadata.author` |
| `build_standard_graph` | tarefas T042/T043/T044/T311/T312/T698/T707 (+T709, T45N); lock `VISUAL_CANON_WRITE` no grafo composto; validadores `V_VISUAL_*` nos quatro gates; anotações de inputs/parameters em T035, T036, T602, T699, T700, T702, T703, T800, T801 |
| `copy_runtime` | copia DNA pinado para `runtime/<slug>/author/`, marcas, `EDITION_CAPABILITIES.yaml`, `PRINT_GEOMETRY.yaml`, templates, `check_visual_canon.py`; escreve `canon/VISUAL_AGENTS.md` a partir do runbook |
| `TOOL_BY_PATTERN` | `T*_VISUAL_CANON_SNAPSHOT`, `T698_EDITION_PLAN`, `T707_PRINT_GEOMETRY` |

Tarefas novas com fase `LIVING_BOOK` entram automaticamente em
`GATE_LIVING_BOOK.requires` (o gate é calculado por fase); `T041_LIVING_BOOK_REVIEW`
recebe `T043` como dependência adicional só com a feature ligada.

### 28.3 Garantias de compatibilidade

- **INV-VN-01:** livro sem `features.visual_narrative.enabled: true` compõe
  grafo **idêntico** aos goldens de `tests/fixtures/golden/*.json` (seis livros).
- **INV-VN-02:** `build_cover_and_stories.py`, `build_kdp_docx.py` e
  `validate_media_assets.py` produzem saída idêntica quando não existem os
  arquivos derivados da capability (teste de regressão de bytes/hashes).
- **INV-VN-03:** composição com `causal_ledger` e `visual_narrative` juntos
  não altera nenhuma tarefa ou validador do ledger (fixture combinada).
- Nenhum runtime existente é migrado; nenhum `.toml` genérico muda; nenhum
  script existente muda de comportamento padrão.
- Livro com a feature ligada mas sem `sigils`, sem `collector` e `budget:
  MINIMAL` recebe só: canon visual de capa + tipografia + marca + plano
  Kindle/KDP — o MVP operacional mais barato.

---

## 29. Testing Strategy

Convenção do repositório: `unittest`, scripts importados via `sys.path` para
`engine/scripts`, 100% offline, nenhuma dependência nova, imagens de teste
geradas **em memória/diretório temporário** com Pillow (nenhum binário novo
commitado). Execução por módulo (D10):
`.venv/Scripts/python.exe -m unittest tests.test_visual_canon tests.test_compose_regression -v`.

Fixtures propostas:

```text
tests/fixtures/visual_narrative/
  authors/bea_halden_fixture/AUTHOR_VISUAL_DNA.v1.yaml
  authors/bea_halden_fixture/AUTHOR_VISUAL_DNA.v2.yaml          (versionamento)
  runtime_cisne_negro/                                          (mini-runtime sem prosa longa)
    book/BOOK_SPEC.yaml, chapter_architecture.yaml (6 caps, pov), protected_scenes.yaml,
    immutable_rules.yaml, visual_profile.md
    canon/CANON_REGISTRY.yaml, canon/CAUSAL_LEDGER.yaml (reuso do formato do ledger)
    specs/SYMBOL_BIBLE.md
    manuscript/final/MANUSCRIPT_FINAL_PTBR.md (6 capítulos de 2–3 frases neutras com as âncoras TEXT:)
    canon/VISUAL_NARRATIVE_CANON.yaml
    canon/snapshots/VISUAL_NARRATIVE_CANON.PLAN.yaml
  runtime_mare_de_chumbo/canon/VISUAL_NARRATIVE_CANON.yaml     (segunda obra, mesmo DNA)
  golden/cisne_negro_edition_plans.json                         (planos semânticos esperados)
tests/fixtures/books/visual_narrative_mvp/                      (pacote compose, Slice 5)
```

| Camada | Casos | Onde |
|---|---|---|
| **UNIT** | resolução de cada tipo de âncora (9 tipos); status Chekhov (5 estados, uma fixture por estado); faixas de papel de cor; precedência constraints×preferences (R1–R9); projeção de estado (`NEXT_CHAPTER`, `AFTER_ANCHOR`, `SAME_CHAPTER`); resolução de fallback por alvo e orçamento; exposição × teto × revelação; hash canônico de aprovação; fórmulas de geometria (paperback) contra valores calculados à mão; heurísticas de thumbnail sobre imagens sintéticas (título com contraste alto/baixo, um/três focos) | `tests/test_visual_canon.py` |
| **CONTRACT** | templates `AUTHOR_VISUAL_DNA_TEMPLATE` e `VISUAL_NARRATIVE_CANON_TEMPLATE` validam sem achados HIGH; runbook só cita campos que o validador conhece; achados no shape de `REVIEW_FINDING`; serialização estável (duas projeções → mesmo sha256); canon v0.1 continua válido após adição de campo opcional; DNA v1 continua válido quando v2 existe | idem |
| **INTEGRATION** | discovery → canon: `VISUAL_CANDIDATES.yaml` não é lido por projeções; canon → `EDITION_PLAN` para 4 alvos; intenção collector → `PRODUCTION_MANIFEST` com máscaras derivadas; `--state` acompanha evento movido de capítulo no ledger; compose + smoke-test do pacote fixture em diretório temporário; `validate-gate` executa `V_VISUAL_*` | `tests/test_visual_canon.py`, `tests/test_compose_regression.py` |
| **GOLDEN** | O Cisne Negro: `EDITION_PLAN` semântico dos 4 alvos igual ao golden; seis livros existentes: grafo igual ao golden atual (INV-VN-01); `build_cover_and_stories.py --no-base-image` sobre runtime sem canon: hashes iguais antes/depois (INV-VN-02) | idem |
| **NEGATIVE** (cada teste afirma a **categoria exata**) | caveira decorativa sem suporte → `GENERIC_TROPE_UNJUSTIFIED`; rosa com âncoras → PASS; foil `COLLECTOR_ONLY` para `kdp_paperback` → resolvido `OMIT` com motivo, e `PREMIUM` foil → `SIMULATED_METALLIC_PRINT`; elemento `CORE` na capa → `SURFACE_SPOILER` BLOCKER; sigil com `trigger: 15` → `ARBITRARY_STATE_MUTATION`; estados diferentes em capítulos consecutivos sem transição → `RANDOM_SIGIL_MUTATION`; hidden truth em `kdp_hardcover` → `HIDDEN_TRUTH_EXPOSED`; DNA com "swan" em papel da autora → `AUTHOR_LAYER_CONTAINS_BOOK_SYMBOL`; livro sobrescrevendo invariante → `AUTHOR_INVARIANT_OVERRIDE`; `count: 5` sem rationale → `UNJUSTIFIED_COUNT`; artefato com citação inexistente → `VISUAL_INVENTS_FACT`; bloco alterado após aprovação → `APPROVAL_STALE`; DNA v1 editado → `AUTHOR_DNA_TAMPERED`; `page_count: null` → `PAGE_COUNT_UNKNOWN`; fator hardcover `TO_VERIFY` usado → `MANUFACTURING_FACT_UNVERIFIED`; sigil com tons médios → `SIGIL_NOT_MONOCHROME`; "no estilo de" em atmosfera → `IMITATION_REFERENCE`; `KDP_DESCRIPTION` com "hot foil" em plano KDP → `FINISH_PROMISE_MISMATCH` | idem |
| **Optional paid** | piloto real (Slice 7): geração de arte, capa e sigils num pacote Bea Halden real, veredito humano | manual, **nunca** na suíte |

---

## 30. Worked Example — O CISNE NEGRO

> Obra **fictícia**, sem prosa, para demonstrar a separação de camadas. Nenhum
> arquivo desta seção existe no repositório; ela vira fixture no Slice 1.
> Personagens adultos. Nomes e fatos inventados para o exemplo.

### 30.1 Premissa canônica mínima (canon narrativo, não visual)

Autora: **Bea Halden**. Título: **O CISNE NEGRO**. 28 capítulos, POV
alternado entre `Isadora` (29) e `Dante` (37).

| Âncora | Fato |
|---|---|
| `LEDGER:GT-A-01` | Isadora foi educada pela família Vane para ser a "herdeira perfeita" — a quinta de uma linhagem de noivas por contrato; ela sabe disso desde criança e o esconde (`reader_access: from EV-19`) |
| `CANON:OBJ-003` | a coroa de noivado da família, de ouro envelhecido, usada pelas cinco herdeiras anteriores |
| `LEDGER:EV-03` (cap. 3) | o contrato é assinado no roseiral da mãe morta; Isadora arranca uma rosa e a guarda |
| `LEDGER:EV-09` (cap. 9) | Isadora encontra a cópia do contrato com os nomes das cinco herdeiras anteriores |
| `SCENE:CROWN_REFUSAL` (cap. 19) | cena protegida: Isadora quebra a coroa diante da família |
| `LEDGER:EV-19` (cap. 19) | o leitor aprende `GT-A-01` |
| `LEDGER:EV-27` (cap. 27) | Isadora incendeia a casa do lago (evento `CORE`) |
| `TURN:1` | chegada à casa do lago; o cisne negro no lago é o primeiro plano da prosa |
| `DOC:/specs/SYMBOL_BIBLE.md#motif-1-black-swan` | evolução: presença → ferida → recusa → voo |
| `chapter_architecture.pov` | `Isadora` nos ímpares, `Dante` nos pares |

### 30.2 O que vem do AUTHOR DNA (camada A) — igual em todo livro Bea Halden

- estrutura `LOW_KEY`: fundo escuro, tinta de osso;
- papéis tipográficos: TITLE serifa de alto contraste em caixa alta com
  tracking largo; AUTHOR sans geométrica espaçada; hierarquia `TITLE_OVER_AUTHOR`;
- `BEA HALDEN` na capa, lombada e folha de rosto; **BH SEAL** na lombada e
  contracapa, em cobre queimado (material assinatura);
- lombada `INDIVIDUAL_CONSISTENT`: faixa de metal a 8% da altura, autor em
  80–93%, selo em 94–98%;
- 1 dominante, ≤ 2 secundários por superfície; watchlist de tropes; tetos de
  spoiler `LOW` público / `MEDIUM` semiescondido; políticas de aprovação.

### 30.3 O que vem do BOOK DNA (camada B) — só O Cisne Negro

```yaml
book_dna:
  visual_thesis: "A perfeição é uma jaula com forma de ave."
  duality:
    outer_truth: "O cisne perfeito que a família exibe."
    hidden_truth: "A coroa que ela quebra."
    anchors: [LEDGER:GT-A-01, SCENE:CROWN_REFUSAL]
  palette:
    GROUND: "#121113"        # dentro de GROUND [0.04–0.20]
    INK: "#E6DCCB"
    METAL: {material: AGED_GOLD, hex: "#8C6A3C"}     # o livro escolhe ouro; a marca BH segue cobre
    PULSE: "#5A0E1C"         # vermelho profundo, área ≤ 12%
elements:
  - id: SYM-SWAN      # DOMINANT na capa; PROVEN
    functions: [CHARACTER: GT-A-01, TRANSFORMATION: SCENE:CROWN_REFUSAL, MEMORY: DOC:SYMBOL_BIBLE#motif-1]
  - id: SYM-WATER     # SECONDARY; reflexo; function CONTRAST → TURN:1 (lago), DOC:WORLD_BIBLE#casa-do-lago
  - id: SYM-CROWN     # watchlist CROWN → exige PROVEN: CANON:OBJ-003 + SCENE:CROWN_REFUSAL (cap. 19) + LEDGER:EV-09 → PROVEN
  - id: SYM-ROSE      # watchlist ROSE → PROVEN só porque LEDGER:EV-03 (roseiral do contrato) + MEMORY
    count: 1          # uma rosa, não um buquê: é a rosa arrancada
  - id: SYM-FIVE-SWANS
    class: MOTIF
    count: 5
    count_rationale: {anchors: [LEDGER:EV-09, CANON:OBJ-003], note: "as cinco herdeiras anteriores"}
    exposure: {spoiler_level: MEDIUM, reveal: LEDGER:EV-09}
  - id: SIG-SWAN      # sigil de livro, 3 estados (seção 14.1)
  - id: SIG-POV       # marcador de POV: ponto à esquerda (Isadora) / direita (Dante), BY_CHAPTER_FIELD pov
  - id: ART-CONTRACT  # artefato: cópia do contrato, citações literais do cap. 9
  - id: ART-FIRE      # candidato rejeitado para capa: incêndio da casa = CORE (30.8)
```

### 30.4 Composições

| Composição | Superfície | Camada | Elementos (proeminência) | Chekhov |
|---|---|---|---|---|
| `COMP-FRONT` | `FRONT_COVER` | OUTER_TRUTH | SYM-SWAN (DOMINANT), SYM-WATER (SECONDARY), SYM-CROWN só como **reflexo na água** (SECONDARY) | todos PROVEN |
| `COMP-BACK` | `BACK_COVER` | NEUTRAL | pena única (TEXTURE, `DECORATIVE_ALLOWED`), sinopse, BH SEAL | ok |
| `COMP-SPINE` | `SPINE` | NEUTRAL | título, autora, faixa de ouro envelhecido, BH SEAL | gramática da autora |
| `COMP-CASE` | `CASE_FRONT` | HIDDEN_TRUTH | SYM-CROWN partida (DOMINANT), SYM-SWAN como silhueta vazia (SECONDARY) | PROVEN; spoiler MEDIUM (a recusa é tema, não o incêndio) |
| `COMP-END-F` | `ENDPAPER_FRONT` | NEUTRAL | mapa da casa do lago e do roseiral (NARRATIVE_ARTIFACT) | PROVEN; spoiler NONE |
| `COMP-END-B` | `ENDPAPER_BACK` | HIDDEN_TRUTH | SYM-FIVE-SWANS no lago, seis lugares, um vazio | PROVEN; MEDIUM ≤ teto semiescondido |
| `COMP-EDGE` | `EDGE_FORE` | NEUTRAL | penas negras em stencil sobre borda preta | PROVEN via SYM-SWAN; spoiler NONE |
| `COMP-OPENER` | `CHAPTER_OPENER` | IN_READING | SIG-SWAN (DOMINANT) + SIG-POV (SUPPORTING) | PROVEN |

Tipografia `COMP-FRONT`: `O CISNE NEGRO` em TITLE, zona `[0.08,0.06,0.92,0.22]`;
`BEA HALDEN` em AUTHOR, zona `[0.20,0.86,0.80,0.93]`. Sem protagonistas
humanos (default da autora, mantido).

### 30.5 Progressão do sigil

| Capítulos | Estado projetado | Por quê |
|---|---|---|
| 1–9 | `PRISTINE` | inicial |
| 10–19 | `CRACKED` | `LEDGER:EV-09` (cap. 9) + `NEXT_CHAPTER` |
| 20–28 | `CROWNLESS` | `SCENE:CROWN_REFUSAL` (cap. 19) + `NEXT_CHAPTER` |

Se a revisão da wave 3 mover a descoberta do contrato para o capítulo 11, a
projeção passa a `PRISTINE` 1–11 / `CRACKED` 12–19 **sem editar o canon
visual** — porque o gatilho é o evento, não o número.

Um quarto estado `OPEN_WINGS` ancorado em `LEDGER:EV-27` foi **recusado** no
plano: exibido na abertura do capítulo 28 anunciaria o incêndio (`CORE`) e só
teria função `PAYOFF` numa página que ninguém vê antes de ler o 27 —
`SAME_CHAPTER` sem ack e spoiler CORE em opener → recusado; alternativa
aceita: uma `INTERIOR_PLATE` após o parágrafo final do capítulo 27
(`AFTER_ANCHOR_IN_CHAPTER`).

### 30.6 Acabamentos e resolução por edição

| Intenção | Material / efeito | Classe | kindle_ebook | kdp_paperback | kdp_hardcover | collector |
|---|---|---|---|---|---|---|
| `FI-TITLE` (TITLE, significado SYM-CROWN: o ouro da linhagem) | AGED_GOLD / METALLIC_FOIL → SIMULATED_METALLIC_PRINT → FLAT_ROLE_COLOR | PREMIUM | `OMIT` do efeito; título em `FLAT_ROLE_COLOR` (orçamento ESSENTIAL) — o título em si é ESSENTIAL via tipografia | `OMIT` do efeito → FLAT (PREMIUM fora do orçamento paperback) | `SIMULATED_METALLIC_PRINT` | `METALLIC_FOIL` (se gráfica confirma) |
| `FI-FEATHERS` (penas do SYM-SWAN) | OBSIDIAN_GLOSS / SPOT_UV → CONTRAST_SIMULATION | OPTIONAL | `OMIT` | `CONTRAST_SIMULATION` sobre laminação matte | `CONTRAST_SIMULATION` | `SPOT_UV` |
| `FI-CROWN-CASE` (COMP-CASE) | AGED_GOLD / DEBOSS + FOIL | COLLECTOR_ONLY | — | — | — (case recebe OUTER_TRUTH) | `DEBOSS` + `METALLIC_FOIL` |
| `FI-EDGE` | stencil preto + penas | COLLECTOR_ONLY | — | — | — | `STENCILED_EDGE` |
| `FI-BH-SEAL` | BURNT_COPPER / METALLIC_FOIL → SIMULATED | ESSENTIAL (marca) com efeito PREMIUM | não se aplica (sem lombada) | selo em FLAT_ROLE_COLOR na lombada/contracapa | `SIMULATED_METALLIC_PRINT` | `METALLIC_FOIL` |

Nota de desenho: quando o **efeito** de uma intenção é premium mas o
**elemento** é essencial, a intenção se divide em dois níveis — o elemento
sempre aparece (cor de papel), o efeito é que degrada. O validador exige que
todo elemento `ESSENTIAL` tenha representação `FLAT_ROLE_COLOR` como último
fallback.

### 30.7 Artefatos

| Artefato | Âncora de conteúdo | Placement | Spoiler | Resultado |
|---|---|---|---|---|
| `ART-CONTRACT` | `TEXT:9:"cláusula quinta"` + `LEDGER:EV-09` | `INTERIOR_PLATE`, `AFTER` a âncora do cap. 9 | MEDIUM, reveal EV-09 | PASS; transcrição no corpo; 8 pt |
| `ART-MAP` (guarda frontal) | `DOC:/specs/WORLD_BIBLE.md#casa-do-lago` | `ENDPAPER_FRONT`; KDP → `OMIT` (opt-in `INTERIOR_PLATE` recusado por custo de páginas) | NONE | PASS |
| `ART-ROSE-NOTE` (bilhete da mãe, proposto) | nenhuma citação encontrada na prosa | — | — | **FAIL** `VISUAL_INVENTS_FACT` → proposta vira `CANON_PROPOSAL` para o `CANON_GUARDIAN`, ou é descartada |

### 30.8 Validação negativa neste livro

| Proposta | Achado | Por quê |
|---|---|---|
| Casa do lago em chamas na contracapa | `SURFACE_SPOILER` BLOCKER | `LEDGER:EV-27` é CORE; contracapa é PUBLIC |
| Chuva de pétalas vermelhas na capa | `GENERIC_TROPE_UNJUSTIFIED` + `UNJUSTIFIED_COUNT` | a rosa canônica é **uma** rosa arrancada; pétalas em profusão não têm âncora |
| Dante sem camisa na capa | `GENERIC_TROPE_UNJUSTIFIED` (SHIRTLESS_MALE) + `FIGURE_ON_COVER` sem aprovação + default da autora | nenhuma função; figura exige override aprovado |
| Faca na lombada "para sinalizar dark romance" | `GENERIC_TROPE_UNJUSTIFIED` + `ATMOSPHERE_ONLY_PROMINENT` | função só ATMOSPHERE |
| Case laminate KDP com a coroa quebrada | `HIDDEN_TRUTH_EXPOSED` BLOCKER | case KDP é PUBLIC (sem sobrecapa) |
| Descrição KDP: "edição com detalhes em foil" | `FINISH_PROMISE_MISMATCH` | foil não é `PHYSICAL` em nenhum alvo KDP |
| Sigil racha "no capítulo 10" (número digitado) | `ARBITRARY_STATE_MUTATION` | gatilho sem âncora |

### 30.9 Risco de IP registrado neste exemplo

"Cisne negro" é símbolo e tema de domínio público (balé do século XIX), mas
existe material cinematográfico e de pôster muito reconhecível associado ao
título em português ("Cisne Negro", 2010). O canon deve **proibir** por veto
explícito a composição de rosto humano com maquiagem/penas rachadas e
tipografia de pôster de filme (`VETO-IP-01`, `rule_kind: CANONICAL`,
`rationale: originalidade`), e o `T602` recebe esse veto como critério. A
colisão de título com obra conhecida é decisão comercial/legal humana (OQ-7),
não do validador.

### 30.10 Segunda obra hipotética — **A MARÉ DE CHUMBO** (prova de não-dependência)

Mesma autora, mesmo `AUTHOR_VISUAL_DNA.v1`. Premissa fictícia: uma
restauradora de faróis (32) e um pescador que carrega uma dívida de sangue da
família (40), numa ilha de chumbo e sal; POV único.

| Camada | O Cisne Negro | A Maré de Chumbo |
|---|---|---|
| Tese visual | "A perfeição é uma jaula com forma de ave." | "A luz que guia também expõe." |
| Dominante da capa | cisne negro | lente de Fresnel com uma única fratura de luz |
| Secundários | água/reflexo, coroa refletida | corda com nó de marinheiro |
| Sigil | cisne: PRISTINE → CRACKED → CROWNLESS | nó: FROUXO → APERTADO → CORTADO (gatilhos: `SCENE:DEBT_NAMED`, `LEDGER:EV-21`) |
| METAL do livro | AGED_GOLD | PEWTER (chumbo polido) |
| PULSE do livro | vinho profundo `#5A0E1C` | âmbar de lâmpada de sódio `#7A4A0C` (dentro da faixa de saturação/luminosidade) |
| Artefatos | contrato, mapa do lago | carta náutica anotada, recibo de dívida |
| Dualidade | cisne perfeito / coroa quebrada | farol aceso / lente vazia |
| Bordas collector | penas em stencil | linha de maré em spray cinza |
| **Zero** de: cisne, coroa, rosa, vermelho | — | ✅ |

O que continua **Bea Halden** sem nenhum desses símbolos:

- estrutura de valor escura com tinta de osso;
- a mesma hierarquia e os mesmos papéis tipográficos;
- `BEA HALDEN` na mesma zona; **BH SEAL em cobre queimado** na lombada e
  contracapa (enquanto o livro usa estanho — a marca é a constante material);
- a mesma gramática de lombada: lado a lado, as duas lombadas formam a mesma
  arquitetura de faixas, zona de autor e selo;
- restrição: um dominante, sigil com progressão ancorada, artefatos que
  existem na história, nada decorativo destacado.

Teste que prova isso (Slice 1): as duas fixtures validam contra o mesmo DNA;
um teste afirma que a interseção dos `elements[].label` dos dois canons é
vazia e que ambos têm `V1` sem achados; um terceiro canon que copia `SYM-SWAN`
para o DNA da autora falha com `AUTHOR_LAYER_CONTAINS_BOOK_SYMBOL`.

---

## 31. Implementation Slices

Cada slice entrega comportamento observável, é aprovado antes do próximo e é
reversível por `git revert` de um único commit. Slices 1–4 **só criam
arquivos novos** e não tocam compositor nem scripts existentes — risco de
regressão zero por construção (verificável por `git diff --stat`).

Pré-condição de todos: working tree com `DARK_ROMANCE_CANON_ARCHITECT`
commitado (D12), para que os goldens sejam estáveis.

### Slice 1 — Author DNA, Book canon e Visual Chekhov (núcleo semântico)

- **Goal:** provar separação A/B, âncoras, Chekhov e anti-generic sobre
  fixtures, sem nenhuma geração.
- **Files likely affected (todos novos):**
  `engine/scripts/check_visual_canon.py`;
  `engine/templates/AUTHOR_VISUAL_DNA_TEMPLATE.yaml`;
  `engine/templates/VISUAL_NARRATIVE_CANON_TEMPLATE.yaml`;
  `tests/fixtures/visual_narrative/authors/bea_halden_fixture/AUTHOR_VISUAL_DNA.v1.yaml`;
  `tests/fixtures/visual_narrative/runtime_cisne_negro/**` (sem manuscrito ainda);
  `tests/fixtures/visual_narrative/runtime_mare_de_chumbo/canon/VISUAL_NARRATIVE_CANON.yaml`;
  `tests/test_visual_canon.py`.
- **Contracts:** 12.1, 12.2 (sem `states`, `finish_intents`, `releases`), 11.2
  (âncoras LEDGER/SCENE/TURN/CHAPTER_FIELD/CANON/DOC/RULE), 11.5, 13.
- **Rules:** V0, V1, V2, V3 (sem pixels); modo `plan` parcial; `--why`, `--evidence` (bíblias).
- **Tests:** template → PASS; fixture Cisne → PASS; fixture Maré → PASS com o
  mesmo DNA; interseção de símbolos vazia; negativos: `GENERIC_TROPE_UNJUSTIFIED`,
  rosa com âncora PASS, `UNJUSTIFIED_COUNT`, `AUTHOR_LAYER_CONTAINS_BOOK_SYMBOL`,
  `AUTHOR_INVARIANT_OVERRIDE`, `AUTHOR_DNA_DRIFT` (hex fora da faixa),
  `OVERRIDE_WITHOUT_REASON`, `VISUAL_OVERLOAD`, `ATMOSPHERE_ONLY_PROMINENT`,
  `IMITATION_REFERENCE`, `AUTHOR_DNA_TAMPERED`; um teste por status Chekhov.
- **Exit criteria:** `python -m unittest tests.test_visual_canon -v` verde
  offline; `tests.test_causal_ledger` e `tests.test_compose_regression`
  continuam verdes; `validate-engine` inalterado; `git diff --stat` só com
  arquivos novos.
- **Risks:** heurística de match da watchlist por palavra gera falso positivo
  (ex.: "rosa" como cor) → match só em `label`/`watchlist_ids` e
  `visual_description`, com teste de falso positivo; validador crescer demais →
  limite de desenho: um módulo, funções puras por família de regra.
- **Rollback:** remover os arquivos novos.

### Slice 2 — Estado narrativo: sigils, progressão, artefatos, spoilers, aprovações

- **Goal:** provar G5/G6/VP-07 e reprodutibilidade de decisões aprovadas.
- **Files:** `check_visual_canon.py` (estende); fixture Cisne + manuscrito de
  6 capítulos neutros com âncoras `TEXT:`, `CAUSAL_LEDGER.yaml` mínimo,
  `snapshots/…PLAN.yaml`, `project_state/APPROVALS/VISUAL/APR-*.md` de teste;
  `tests/test_visual_canon.py` (estende).
- **Contracts:** 14 completo, 19.2, 19.5, 26.1, 26.2, âncora `TEXT:`.
- **Rules:** ST-01..ST-09, V5, V9, modo `realized --baseline`; `--state`,
  `--timeline`, `--exposure`, `--end-state`.
- **Tests:** projeção 1–9/10–19/20–28 (escala reduzida à fixture); evento
  movido de capítulo no ledger → projeção acompanha sem editar canon;
  negativos `ARBITRARY_STATE_MUTATION`, `RANDOM_SIGIL_MUTATION`,
  `OPENER_PRE_ANNOUNCES_EVENT`, `PAYOFF_WITHOUT_SEED`, `TRIGGER_NOT_REALIZED`,
  `VISUAL_RETCON`, `VISUAL_INVENTS_FACT`, `ARTIFACT_BEFORE_FIRST_APPEARANCE`,
  `SURFACE_SPOILER` (CORE BLOCKER), `SPOILER_UNANCHORED`, `PREMATURE_EXPOSURE`
  (herdado de `reader_access`), `HIDDEN_SURFACE_SPOILER`, `APPROVAL_STALE`,
  `CANDIDATE_CONSUMED`.
- **Exit criteria:** Slice 1 intacto; `--why SYM-SWAN` produz o bloco de
  explicação da seção 25.
- **Risks:** parser de capítulos do manuscrito diverge do de
  `build_kdp_docx.py` → importar o padrão de `KDP_LAYOUT.manuscript.chapter_heading_pattern`
  via `_layout_config.py` (reuso, não cópia).
- **Rollback:** reverter o commit do slice.

### Slice 3 — Edições: capacidades, fallbacks, plano, geometria, manifesto collector

- **Goal:** provar G3/G7 e "design once → render by edition".
- **Files (novos):** `engine/templates/EDITION_CAPABILITIES.yaml`,
  `engine/templates/PRINT_GEOMETRY.yaml`; `check_visual_canon.py` (estende:
  `--edition-plan`, `--resolve`, `--geometry`, `--production-manifest`);
  `tests/fixtures/visual_narrative/golden/cisne_negro_edition_plans.json`;
  fixture `layout/PRINT_SPEC.yaml`, `layout/PRINTER_PROFILE.yaml`.
- **Contracts:** 15, 16, 20.2, 21, 22.
- **Rules:** V7, V8; projeções `EDITION_PLAN`, `COVER_GEOMETRY`, `PRODUCTION_MANIFEST`.
- **Tests:** golden dos 4 planos; determinismo (duas execuções, mesmo sha256);
  geometria paperback 6×9, 300 páginas creme conferida à mão
  (`spine = 300 × 0,0025 = 0,75"`, `full_width = 0,125 + 6 + 0,75 + 6 + 0,125 = 13,0"`, `full_height = 9,25"`);
  negativos `ESSENTIAL_UNRENDERABLE`, `HIDDEN_TRUTH_EXPOSED`,
  `EDITION_CHANGES_MEANING`, `PAGE_COUNT_UNKNOWN`,
  `MANUFACTURING_FACT_UNVERIFIED`, `ZONE_COLLIDES_WITH_MANUFACTURING`,
  `FINISH_PROMISE_MISMATCH`, `PRINTER_UNCONFIRMED`; toda máscara aponta para
  intenção com Chekhov válido.
- **Exit criteria:** `DARK_ROMANCE`/visual tests verdes; tese estrutural
  `VISUAL_NARRATIVE_THESIS_STRUCTURAL = PROVEN` (seção 34.3).
- **Risks:** fatos KDP mudarem → template datado + `T699`; geometria hardcover
  incompleta → `TO_VERIFY` explícito, teste garante recusa.
- **Rollback:** reverter commit.

### Slice 4 — Ativos: thumbnail, grayscale, deriva em pixels, proveniência

- **Goal:** G4 (thumbnail/readability) sobre imagens reais, com limiares
  calibrados.
- **Files:** `check_visual_canon.py` (estende modo `assets`); testes com
  imagens sintéticas geradas em `tempfile`; relatório de calibração
  `docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_CALIBRATION.md` (medições
  sobre capas existentes de `eva` e `loja`, somente leitura).
- **Contracts:** 23.5, 23.6, 18.3.
- **Rules:** V4, V6 (ativos), V1 pixels, verificação de `generated_from` +
  `DERIVED_ARTIFACT_EDITED`.
- **Tests:** título alto/baixo contraste; um foco × três focos; sigil 1-bit ×
  sigil com gradiente (`SIGIL_NOT_MONOCHROME`); estados que diferem só por cor;
  área de PULSE acima do teto; miniaturas geradas nos três tamanhos.
- **Exit criteria:** limiares registrados com a medição real que os
  justifica; capa tipográfica original de `eva` (julgada "pobre" pelo autor)
  produz ao menos um achado MEDIUM de focal point, e a capa revisada não —
  **se** isso não ocorrer, os limiares são recalibrados ou a heurística é
  rebaixada a INFO e registrada como limite.
- **Risks:** heurística enganosa → severidade MEDIUM, miniaturas sempre
  entregues para olho humano.
- **Rollback:** reverter commit.

### Slice 5 — Integração OFF por padrão (compositor, pacote de autora, runbook)

- **Dependências:** Slices 1–4; **decisões OQ-1 e OQ-2**; working tree limpo.
- **Goal:** runtime de livro com a feature ligada recebe tarefas, lock,
  validadores e arquivos; todo o resto compõe idêntico.
- **Files:** `engine/scripts/livingbook.py` (bloco condicional em
  `validate_book_data`, `build_standard_graph`, `copy_runtime`,
  `TOOL_BY_PATTERN`); `engine/templates/VISUAL_NARRATIVE_RUNBOOK.md`;
  `engine/IMPLEMENT.md` (um parágrafo, como o do ledger);
  `authors/bea_halden/AUTHOR_VISUAL_DNA.v1.yaml` **em status DRAFT** (vira
  APPROVED só com arquivo humano); `tests/fixtures/books/visual_narrative_mvp/`;
  `tests/test_compose_regression.py` (estende).
- **Tests:** goldens dos seis livros e da fixture do ledger idênticos
  (INV-VN-01, INV-VN-03); fixture visual: tarefas T042/T043/T044/T311/T312/T698/T707
  presentes com dependências corretas, `VISUAL_CANON_WRITE` só nesse grafo,
  `V_VISUAL_*` nos quatro gates, `validate_graph` sem erros, compose +
  smoke-test em diretório temporário; runbook só cita campos conhecidos.
- **Exit criteria:** `SMOKE TEST OK` no fixture; nenhum golden alterado.
- **Risks:** `T041` depender de `T043` cria ordem nova no LIVING_BOOK →
  teste de ciclo; nome de pasta `authors/` conflitar com distribuição → ver
  `DISTRIBUTION_MANIFEST.md` antes (OQ-1).
- **Rollback:** reverter commit; goldens garantem que nada mais mudou.

### Slice 6 — Hooks de renderização existentes (sem mudança padrão)

- **Goal:** o canon passa a governar capa e aberturas reais.
- **Files:** `engine/scripts/check_visual_canon.py` (`--project-media-design`);
  `engine/scripts/build_cover_and_stories.py` (`typography_bindings`
  opcionais em `load_font`); `engine/scripts/build_kdp_docx.py` (asset de
  sigil acima do rótulo quando existir `EDITION_PLAN.chapter_openers`);
  testes de regressão de bytes.
- **Tests:** INV-VN-02 (hash de capa `--no-base-image` e DOCX de fixture
  idênticos sem plano); com plano: DOCX contém N imagens de sigil nos
  capítulos esperados e com o estado projetado; `MEDIA_DESIGN.yaml` projetado
  estável.
- **Exit criteria:** `GATE_KDP` render-QA de um fixture curto aprovado por
  inspeção humana.
- **Risks:** python-docx e posicionamento de imagem pequena em abertura →
  reutilizar `add_image_page`/`add_picture` existente, inline.
- **Rollback:** reverter; ausência de plano = comportamento antigo.

### Slice 7 — Piloto real (opcional, pago)

- **Dependências:** Slice 6; primeiro pacote Bea Halden real (OQ-3);
  orçamento aprovado.
- **Goal:** `VISUAL_NARRATIVE_THESIS = PROVEN`: capa Kindle, lombada/plano
  KDP paperback e sigils gerados por pipeline, com veredito humano.
- **Files:** nenhum código; runtime gerado; aprovações humanas.
- **Tests:** gates visuais sem HIGH/BLOCKER; checkpoint humano responde "sim"
  a: "reconheço Bea Halden?", "cada símbolo significa algo?", "isto não é capa
  genérica?".
- **Rollback:** descartar runtime.

### FUTURE (fora desta SDD)

Geração de wrap PDF CMYK; renderização automática de máscaras; `SERIES_CONTINUOUS`
spine e `box_set`; comparação entre canons do catálogo (self-cannibalization
visual); herança de estado entre volumes (`inherits_from`); audiobook, web,
EPUB externo.

---

## 32. Risks

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Custo de autoria: `VISUAL_DIRECTOR` mantendo YAML denso de âncoras | alta | médio | só elementos com `prominence ≥ SUPPORTING` exigem âncoras; `--evidence` automatiza contagens; template com exemplos; `budget: MINIMAL` |
| Validador vira "fórmula de bom design" | média | alto | status Chekhov e thumbnail são **condições necessárias**; veredito é humano/agente; severidades MEDIUM onde heurístico |
| Heurísticas de thumbnail enganosas | média | médio | calibração com capas reais (Slice 4); miniaturas sempre entregues para inspeção |
| Fatos KDP mudam | média | alto | template datado, `T699`, `TO_VERIFY` bloqueia cálculo, `CAPABILITY_BLOCKER` |
| Collector sem gráfica definida | alta | médio | `PRINTER_UNCONFIRMED`; manifesto é especificação, não compromisso |
| Pacote `authors/` rompe convenção de distribuição (`DISTRIBUTION_MANIFEST.md`) | média | médio | OQ-1; alternativa B documentada (33) |
| Identidade da autora engessa (fórmula) | média | alto | invariantes mínimos (estrutura, hierarquia, marca, gramática de lombada); todo símbolo é do livro; defaults sobrescrevíveis; revisão de portfólio FUTURE |
| Spoiler por colagem de relatório em prompt de capa | média | alto | visão padrão oculta hidden truth e revelações (`--engine-view` explícito) |
| Modelo de imagem não produz sigil 1-bit legível | média | médio | caminho `GLYPH` como padrão; `SIGIL_NOT_MONOCHROME` pega o resto |
| Conflito de ownership com `CANON_GUARDIAN` | baixa | alto | VP-05: canon visual não cria fato; artefato com fato novo vai para `CANON_PROPOSALS`; `CANON_GUARDIAN` no spawn de `T043` |
| Working tree sujo invalida goldens | média | médio | pré-condição de todos os slices |
| `DRAFT` desliga `images` e deixa sigil raster sem arte | alta | baixo | `DRAFT` força `GLYPH`; nenhum gate hard é rebaixado |
| Colisão de título/composição com obras conhecidas | média | alto | `IMITATION_REFERENCE`, vetos IP, `T602`; decisão legal humana (OQ-7) |

---

## 33. Open Questions

| ID | Pergunta | Bloqueia | Recomendação |
|---|---|---|---|
| **OQ-1** | Onde vive o Author DNA? **A)** `authors/<id>/` (novo nível de pacote, versionado, copiado para o runtime no compose) · **B)** arquivo repetido em cada `books/<slug>/` com hash de referência · **C)** repositório/pacote externo | Slice 5 | **A.** B duplica e deriva, contra G1; C adiciona dependência operacional sem necessidade. Exige confirmar impacto em `DISTRIBUTION_MANIFEST.md`. |
| **OQ-2** | Dono do canon visual: `VISUAL_DIRECTOR` com lock `VISUAL_CANON_WRITE` (proposta) ou `CANON_GUARDIAN` sob `CANON_WRITE`? | Slice 5 | `VISUAL_DIRECTOR` (precedente `FACE_CANON_WRITE`; mantém `CANON_GUARDIAN` focado em fatos). |
| **OQ-3** | Qual será o primeiro pacote Dark Romance real de Bea Halden para o piloto? | Slice 7 | — |
| **OQ-4** | Existe gráfica/fornecedor collector em vista? Quais acabamentos ela confirma? | `collector` real | Até lá, manifesto em `PRINTER_UNCONFIRMED`. |
| **OQ-5** | Valores iniciais do Author DNA v1 (hex defaults, faixas, classificações tipográficas, marca BH desenhada) devem ser aprovados por humano. Os desta SDD são **propostas**. | aprovação do `AUTHOR_VISUAL_DNA.v1` | Sessão de direção de arte dedicada antes do Slice 5. |
| **OQ-6** | A marca BH SEAL será registrada como marca? | uso comercial da marca | Decisão legal humana. |
| **OQ-7** | "O Cisne Negro" é só exemplo ou título pretendido? Se pretendido, avaliar colisão com obras conhecidas. | nenhum slice | — |
| **OQ-8** | Fator de lombada e faixa de páginas de hardcover KDP, e posição/tamanho da zona de código de barras: confirmar no Cover Calculator oficial. | cálculo de geometria hardcover / zona de barcode | `T699` com instrução explícita; até lá `TO_VERIFY`. |
| **OQ-9** | Limite de tamanho da capa de eBook: 5 MB (página oficial consultada) × 50 MB (validador atual). | nenhum slice desta SDD | Verificar e, se confirmado, corrigir o validador em mudança separada. |
| **OQ-10** | Kindle interior: o motor entrega DOCX; imagens de sigil no eBook serão validadas no mesmo DOCX ou num pipeline EPUB/KPF? | alvo `kindle_ebook` para sigils | Assumir DOCX (existente) no MVP; registrar limite. |
| **OQ-11** | Os limiares de thumbnail devem ser do Author DNA (identidade) ou do motor (ergonomia)? | Slice 4 | Motor define piso; autora pode endurecer. |

---

## 34. Acceptance Criteria

### 34.1 Checklist do SDD

| Critério | Status | Onde |
|---|---|---|
| arquitetura real foi investigada | ✅ | 7, 8, Apêndice A |
| mecanismos existentes foram reutilizados sempre que possível | ✅ | 9 (0 agentes, 0 gates, 0 dependências) |
| author DNA e book DNA estão separados | ✅ | 10.2, 12.1, 12.2, 30.2–30.3 |
| existe Visual Canon | ✅ | 12.2 (`VISUAL_NARRATIVE_CANON`) |
| existe estratégia de Chapter Sigils | ✅ | 14, 18 |
| existe estratégia de Narrative Artifacts | ✅ | 19.1–19.2 |
| Kindle/KDP/Collector compartilham o mesmo modelo semântico | ✅ | 15, 20.2, 30.6 |
| limitações físicas por edição estão representadas | ✅ | 16, 21 |
| fallbacks estão definidos | ✅ | 15.3, 20.2, 21.5 |
| Visual Chekhov está formalizado | ✅ | 11.5, 23.3 |
| Anti-Generic está formalizado | ✅ | 23.4 |
| spoiler safety está definido | ✅ | 26.1, DJ-01..05 |
| visual progression possui state model | ✅ | 14 |
| backward compatibility está preservada | ✅ | 28.3 |
| worked example de O CISNE NEGRO está completo | ✅ | 30.1–30.9 |
| segunda obra hipotética prova que Bea Halden não depende de cisne/coroa/vermelho | ✅ | 30.10 |
| plano de implementação dividido em slices | ✅ | 31 |
| riscos e perguntas em aberto registrados | ✅ | 32, 33 |
| nenhuma implementação foi realizada nesta sessão | ✅ | só este arquivo foi criado |

### 34.2 Respostas às 20 perguntas críticas

| # | Pergunta | Resposta |
|---|---|---|
| 1 | O que pertence à identidade permanente de Bea Halden? | Estrutura de valor escura/tinta clara, papéis de cor (faixas, não símbolos), papéis tipográficos e hierarquia, nome nas superfícies, marca BH e seu material assinatura, gramática de lombada, tetos de densidade e spoiler, watchlist de tropes, políticas de aprovação (12.1). |
| 2 | O que pertence somente a um livro? | Tese visual, símbolos e significados, paleta concreta, metal e pulsação, composições, artefatos, sigils e progressões, dualidade, acabamentos (12.2). |
| 3 | Como impedir que todos os livros pareçam iguais? | O DNA não pode conter símbolo (`AUTHOR_LAYER_CONTAINS_BOOK_SYMBOL`); o dominante precisa de âncoras do próprio livro (`DOMINANT_NOT_BOOK_SPECIFIC`); a segunda obra prova com interseção vazia (30.10). |
| 4 | Como impedir Dark Romance genérico? | Watchlist exige `PROVEN`; overload; atmosfera não justifica objeto; referência imitativa proibida (23.4). |
| 5 | Como um símbolo ganha suporte narrativo? | Por âncoras resolvíveis em canon/ledger/cena protegida/virada/prosa, com força STRUCTURAL ou SUPPORTED (11.2). |
| 6 | Como registrar seu significado? | `elements[].meaning` + `functions[]` com âncoras, promovido de candidato por decisão com aprovação (12.2–12.3). |
| 7 | Como um Chapter Sigil evolui? | Transições com gatilho em evento narrativo e regra de exibição (`NEXT_CHAPTER` por padrão) (14.1–14.2, 18.2). |
| 8 | Como persistir seu estado? | Não persiste "estado atual": transições armazenadas, estado projetado; snapshots só como baseline de imutabilidade (14.4). |
| 9 | Como evitar spoilers? | Exposição por superfície × nível × âncora de revelação, herança de `reader_access`, tetos da autora (26.1). |
| 10 | Como Kindle, KDP e Collector compartilham a intenção? | Um canon; edição só resolve manifestação; mudar significado por edição é BLOCKER (13.1, 15). |
| 11 | Como degradar um acabamento não suportado? | Escada ordenada de fallbacks resolvida contra a matriz datada; elemento essencial sempre termina em cor de papel; omissão registrada (15.3, 30.6). |
| 12 | Como representar foil/emboss/spot UV semanticamente? | `finish_intents`: material semântico + efeito preferido + fallbacks + elemento com significado + camada nomeada (20.2). |
| 13 | Como produzir máscaras técnicas depois? | Contrato de camadas nomeadas e `PRODUCTION_MANIFEST` com máscaras derivadas por camada na mesma geometria (22.2–22.3). |
| 14 | Como separar arte criativa da geometria de impressão? | Zonas normalizadas no canon; `PRINT_SPEC` do livro + `PRINT_GEOMETRY` do fabricante → `COVER_GEOMETRY` projetado (21.1). |
| 15 | Como preservar decisões aprovadas? | Aprovação humana com hash do bloco, snapshots, `releases[]`, `APPROVAL_STALE`, `VISUAL_RETCON` (26.2, 27.3). |
| 16 | Como versioná-las? | DNA por arquivo imutável `vN` com pin sha256; canon por semver + snapshots + releases (27). |
| 17 | Como provar Visual Chekhov? | Tabela determinística de status por elemento e superfície + explicação `WHY/EVIDENCE` (11.5, 23.3, 25). |
| 18 | Como avaliar legibilidade em thumbnail? | Miniaturas em três larguras + heurísticas de contraste de zona, foco, clutter, silhueta e grayscale, calibradas; reconhecimento fica com humano (23.5). |
| 19 | Como continuar funcionando sem a capability? | Flag ausente = grafo idêntico aos goldens; scripts idênticos sem arquivos derivados (28.3). |
| 20 | Qual o menor MVP arquitetural que prova o conceito? | Slices 1–3: DNA + dois canons de livro + Chekhov/anti-generic + um sigil de três estados + spoiler + um acabamento resolvido nos quatro alvos + geometria paperback — tudo determinístico, sobre fixtures, sem gerar arte, sem tocar o compositor. |

### 34.3 Tese

```text
VISUAL_NARRATIVE_THESIS_STRUCTURAL = PROVEN   ao fim do Slice 3
  (o motor representa, verifica e explica identidade autoral, significado ancorado,
   progressão narrativa, spoiler e manifestação por edição sobre fixtures)
VISUAL_NARRATIVE_THESIS            = PROVEN   ao fim do Slice 7
  (o pipeline produz capa, lombada e sigils reais que um humano reconhece como
   Bea Halden, não genéricos, e em que cada símbolo significa algo)
```

---

## 35. Decision Log

| ID | Decisão | Alternativas rejeitadas | Motivo |
|---|---|---|---|
| DL-01 | Seguir o padrão exato de `DARK_ROMANCE_CANON_ARCHITECT` (1 canon + 1 validador + templates + runbook + flag + anotações + goldens) | engine visual, serviço, agentes novos | precedente implementado e testado no próprio repositório |
| DL-02 | Criar nível `authors/<id>/` para o Author DNA | DNA em `/engine`; DNA copiado em cada livro | `/engine` neutro (D8); cópia viola "definida uma vez" e versionamento |
| DL-03 | `VISUAL_NARRATIVE_CANON` como nome | `VISUAL_CANON` | colisão com `artifact_contracts.VISUAL_CANON` (D-V1) |
| DL-04 | Um tipo `composition` por superfície | `CoverConcept`, `SpineConcept`, `EdgeConcept`, `EndpaperConcept` | mesma estrutura; tipos separados multiplicariam regras e testes |
| DL-05 | Estado projetado de transições ancoradas | estado por capítulo armazenado; gatilho por número de capítulo | uma fonte de verdade; acompanha mudança de capítulo; impede mutação arbitrária |
| DL-06 | `NEXT_CHAPTER` como regra padrão de exibição | `SAME_CHAPTER` | abertura é vista antes da prosa (spoiler estrutural) |
| DL-07 | Constraints acumulam, preferences por especificidade | hierarquia linear única | resolve autora × veto do livro sem perder nenhum dos dois |
| DL-08 | Canon visual abaixo do canon narrativo; não cria fato | canon visual autônomo | preserva propriedade exclusiva de `CANON_GUARDIAN` |
| DL-09 | `VISUAL_DIRECTOR` como dono (sujeito a OQ-2) | `CANON_GUARDIAN` | agente já dono da linguagem visual; precedente `FACE_CANON_WRITE` |
| DL-10 | Matriz de capacidades como template de dados datado | tabela hardcoded; reuso de `known_capabilities` | fatos mudam; edição ≠ host |
| DL-11 | Escada ordenada de fallbacks + `meaning_element` no acabamento | fallback único; acabamento sem significado | degradação previsível e Chekhov também para materiais |
| DL-12 | Zonas normalizadas no canon; geometria projetada | dimensões no design | trim e páginas mudam sem invalidar aprovação |
| DL-13 | Chaves `TO_VERIFY` proibidas em cálculo | usar valores de fontes não oficiais | não inventar fabricação |
| DL-14 | Nenhum gate novo; quatro modos em gates existentes | onze gates G0–G10 | mesmo resultado com menos superfície de manutenção |
| DL-15 | Thumbnail por heurística Pillow + miniaturas para humano | visão computacional/modelo | missão pede contrato e heurística primeiro; zero dependência |
| DL-16 | Halden Spine `INDIVIDUAL_CONSISTENT` no MVP | lombada contínua obrigatória | largura variável por páginas e variação de dobra de 0,0625" documentada |
| DL-17 | Marca BH proibida em aberturas de capítulo | marca em todo lugar | aberturas pertencem ao sigil; repetição seria decoração |
| DL-18 | Protagonista literal na capa como **default** da autora, não invariante | proibição absoluta | precedente `eva`: regra de figura foi tática |
| DL-19 | Artefato só cita prosa/canon | artefato com conteúdo livre | VP-05 |
| DL-20 | Aprovação por decisão com hash, reutilizando `APPROVALS/` | novo mecanismo de aprovação; aprovação por gate só | decisões visuais são mais granulares que gates; motor continua sem escrever aprovações |
| DL-21 | Collector depende de `PRINTER_PROFILE` humano | matriz collector fixa | "collector" não é fabricante |
| DL-22 | `GLYPH` como render padrão de sigil | raster gerado por IA | custo zero, monocromático, funciona em `DRAFT` |

---

## 36. Self-Review adversarial

Cada pergunta foi usada para tentar derrubar o desenho. Onde a resposta foi
"sim", o SDD foi corrigido nesta mesma sessão.

| Ataque | Resposta | Correção aplicada |
|---|---|---|
| **Duplicação?** `VISUAL_LIFE_SPEC.md`, `SYMBOL_BIBLE.md` e o canon visual dizem a mesma coisa? | **Parcialmente.** O rascunho copiava "evolução do símbolo" para o canon. | O canon **cita** a bíblia (`DOC:`) em vez de duplicar; `T036` passa a citar ids do canon. A bíblia continua sendo a prosa; o canon, a estrutura. |
| Duplicação com o `CAUSAL_LEDGER`? | Não: o ledger guarda causalidade de personagem; o canon visual só **referencia** `EV/GT` e herda `reader_access`. | Integração explícita em 26.1 e INV-VN-03. |
| **Complexidade excessiva?** Onze gates, dezessete contratos pedidos. | Seria. | Reduzido a 1 validador em 4 modos, 3 arquivos de contrato (DNA, canon, capacidades) + 1 de geometria + projeções. `CoverConcept/Spine/Edge/Endpaper` fundidos em `composition`; `VisualProgression` fundido em `states`. |
| **Abstração prematura?** `authors/` para uma única autora? | Risco real. | Justificado por requisito explícito de versionamento e consistência entre livros, não por generalidade; ainda assim marcado OQ-1 e só entra no Slice 5. Slices 1–4 usam fixture. |
| Abstração prematura: `SERIES_CONTINUOUS`, box set, audiobook? | Sim, se implementados. | Mantidos só como valores de enum/FUTURE, sem regra nem código. |
| **Coupling?** Validador visual depende de ledger, manuscrito, layout. | Dependência opcional: cada tipo de âncora falha como "não resolvível" quando a fonte não existe. | Âncoras `LEDGER:` só são aceitas se `causal_ledger` estiver ligado (`ANCHOR_SOURCE_DISABLED`); parser de capítulo reutiliza `_layout_config`. |
| Coupling com `build_kdp_docx.py`/`build_cover_and_stories.py`? | Existiria se o validador chamasse os builders. | Integração só por **arquivos projetados** (`MEDIA_DESIGN.yaml`, `EDITION_PLAN.yaml`), no Slice 6, com regressão de bytes. |
| **Canon drift?** Dá para editar o canon depois de aprovado? | Dava, no rascunho. | `APPROVAL_STALE` por hash, `VISUAL_RETCON` contra `FREEZE`, `DERIVED_ARTIFACT_EDITED`, `AUTHOR_DNA_TAMPERED`. |
| Regra tática endurece e vira canon? | Precedente real (`eva`). | `rule_kind` + `expires_when`. |
| **Suposições sobre KDP?** | Sim: faixa de páginas e fator de lombada de hardcover vieram de fonte não oficial. | `TO_VERIFY` bloqueia cálculo; `T699`; OQ-8; divergência D-V4 (5 MB × 50 MB) registrada, não "corrigida" por suposição. |
| **Suposições sobre collector?** | Sim: tratar collector como capaz de tudo. | `VENDOR_DEPENDENT` + `PRINTER_PROFILE` humano; sem perfil = `UNSUPPORTED`. |
| **Gimmicks visuais?** Progressão que "apodrece" o livro; bordas falsas; foil sem motivo. | Possíveis. | ST-09 protege leitura; bordas `COLLECTOR_ONLY` sem simulação; `meaning_element` obrigatório em acabamento; marca BH fora das aberturas. |
| **Falta de rastreabilidade?** | O rascunho explicava só falhas. | `--why` emite explicação também em PASS, com contagens e âncoras; visão padrão sem vazamento. |
| O Chekhov virou fórmula de qualidade? | Não: prova suporte, não beleza. | Texto 23.3 explicita o resíduo humano. |
| Um perfil `DRAFT` desliga spoiler ou anti-generic? | Não pode. | Gates alvo não são rebaixáveis; `DRAFT` só força `MINIMAL`/`GLYPH`. |
| A identidade Bea Halden pode destruir a leitura? | Não por construção. | `BODY` intocável; tetos de densidade; grayscale obrigatório para essenciais. |
| Livros sem a capability mudam? | Não. | INV-VN-01..03 com goldens existentes. |

---

## Apêndice A — Arquivos inspecionados e fontes externas

**Raiz e documentação:** `AGENTS.md`, `README.md`, `Makefile`,
`requirements.txt`, `.gitignore`, `docs/ARCHITECTURE.md`,
`docs/BOOK_PACKAGE_MODEL.md`, `docs/COMO_EXECUTAR_UM_LIVRO.md` (capa/KDP),
`docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md` (integral),
`discovery-books/09-discovery-profile-livro-no-motor-intent.md` (início).

**Motor:** `engine/AGENTS.md`, `engine/ENGINE_GRAPH.yaml`, `engine/IMPLEMENT.md`,
`engine/MODEL_TIERS.yaml`, `engine/contracts/*.schema.json` (6),
`engine/templates/KDP_LAYOUT_DEFAULTS.yaml`, `EXECUTION_PROFILES.yaml`,
`TEXT_QUALITY_DEFAULTS.yaml`, `BOOK_PACKAGE_CHECKLIST.md`,
`CAUSAL_LEDGER_TEMPLATE.yaml`, `CAUSAL_LEDGER_RUNBOOK.md`;
`engine/scripts/livingbook.py` (integral), `runtime_taskgraph.py`,
`run_deterministic.py`, `_layout_config.py`, `build_cover_and_stories.py`
(integral), `validate_media_assets.py` (integral), `build_kdp_docx.py`
(abertura de capítulo, imagens, metadados), `generate_image.py` (cabeçalho),
`check_canon_continuity.py` (`finding`), `check_causal_ledger.py` (cabeçalho).

**Agentes:** `visual_director`, `symbolism_architect`, `book_layout_architect`,
`media_kdp_agent`, `kdp_formatter`, `kdp_requirements_researcher`,
`chapter_image_director`, `image_generator`, `image_continuity_qa`,
`canon_guardian`, `originality_auditor`, `page_breathing_architect`,
`image_layout_agent`.

**Pacotes:** `books/a_morte_ainda_nao_nasceu/` (BOOK_SPEC, BOOK_GRAPH,
capability_requirements, visual_profile, quality_profile, protected_scenes,
immutable_rules, chapter_architecture (início)); metadados de `BOOK_SPEC` de
`loja-de-poderes-vivos`, `eva-a-ultima-mulher-da-terra`,
`adao-o-ultimo-homem-da-terra`; listagem de todos os pacotes.

**Runtimes (somente leitura):** `a_morte_ainda_nao_nasceu` (`CANON_REGISTRY.yaml`
início, `SYMBOL_BIBLE.md`, `VISUAL_LIFE_SPEC.md`, `MEMORY_MOTIF_MAP.md`,
`KDP_CURRENT_REQUIREMENTS.md`, `MEDIA_ASSET_MANIFEST.md`, árvore de diretórios);
`eva-a-ultima-mulher-da-terra` (`media/MEDIA_DESIGN.yaml`, `media/COVER_BRIEF.md`,
`reviews/COVER_STORIES_CRITIQUE.md`); `loja-de-poderes-vivos`
(`layout/KDP_LAYOUT.yaml`, `media/staging/pre_kdp/COVER_PRODUCTION_REPORT_PREVIEW.md`).

**Testes:** listagem de `tests/`; cabeçalho de `tests/test_compose_regression.py`.

**Comandos executados (somente leitura / sem efeitos no repositório):**
`git status`, `git ls-files`; `livingbook.py validate-engine` →
`ENGINE VALID | generic agents: 66 | version: 1.1.0`;
`python -m unittest tests.test_causal_ledger tests.test_compose_regression` →
`Ran 57 tests … OK`. `compose` **não** executado. `tests/test_image_generation.py`
**não** executado (chamada paga, D10).

**Fontes externas consultadas em 2026-09-14:**

- KDP — Create a Paperback Cover: https://kdp.amazon.com/en_US/help/topic/G201953020
- KDP — Create a Hardcover Cover: https://kdp.amazon.com/en_US/help/topic/GDTKFJPNQCBTMRV6
- KDP — Print Options: https://kdp.amazon.com/en_US/help/topic/G201834180
- KDP — eBook cover: https://kdp.amazon.com/en_US/help/topic/G6GTK3T3NUHKLEFX
- KDP — Cover Calculator: https://kdp.amazon.com/cover-calculator (não consultado em detalhe; OQ-8)
- Não oficiais, usadas só como pista e marcadas `TO_VERIFY`:
  https://coverlabpro.com/kdp-cover-size-guide.html,
  https://www.vappingo.com/word-blog/kdp-hardcover-formatting/

