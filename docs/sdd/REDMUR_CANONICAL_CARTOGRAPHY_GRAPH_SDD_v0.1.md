# SDD v0.1 — `REDMUR_CANONICAL_CARTOGRAPHY_GRAPH`

> **"Redmur pode mentir sobre os caminhos. O sistema nunca pode mentir sobre onde os caminhos estão."**

| Campo | Valor |
|---|---|
| Status | **E0 — PROPOSTA.** Nenhum código escrito, nenhum arquivo de canon criado, nenhum comportamento do motor alterado. Aguarda aprovação humana explícita e as decisões bloqueantes da seção 40. |
| Data | 2026-09-19 |
| Obra | **SEM ROSTO** — autoria **Bea Halden** — gênero DEDR (*Dystopic Enigma Dark Romance*) |
| Papel | **Fundação canônica espacial** da obra (1 de 2). A outra — o SDD de canon narrativo/histórico, dono do **Story Truth Ledger** — ainda não existe e é referenciada aqui só por contrato (seção 22.4). |
| Tipo | **Capability neutra do motor** (`features.cartography`, OFF por padrão) **+ dados canônicos da obra** (`books/sem-rosto/cartography/`). O código não contém nenhum nome de Redmur. |
| Base | `engine/ENGINE_GRAPH.yaml` `1.1.0`, branch `slice-1/interpretive-canon-model`, commit `98a2f5c` + working tree (LTE Slices 1–2, DEDR, RI, UNSEEN, HDR, RELICS **não commitados** — não tocados por esta SDD) |
| SDDs irmãs | `DYSTOPIC_ENIGMA_DARK_ROMANCE_SDD_v0.1.md` (SEM ROSTO como caso-modelo, §33), `DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md` (ledger causal), `LIVING_THEORY_ENGINE_SDD_v0.1.md` (canon interpretativo), `NARCISO_CANONICAL_SDD_v0.1.md` (padrão de canon por obra) |
| Fontes canônicas | **MAPA A** `redmur_map.png` — sha256 `98123fee45ea70b220c46bef719d2644729231d0f8df5d1ac00d90f6f9525f36` — 1448×1086 RGB · **MAPA B** `redmur_arredores_map.png` — sha256 `36cf98babb4864d0913847c845364641d55120836d8960e8e88cb4373a43b9f3` — 1448×1086 RGB · hoje em `~/Downloads/SEM ROSTO/` (fora do repositório; ver D-CART-01) |
| Implementação | **S0 concluído (2026-09-20)** e **S1 concluído (2026-09-20)**: `engine/scripts/check_cartography.py`, `engine/contracts/CARTOGRAPHY.schema.json`, `engine/templates/CARTOGRAPHY_TEMPLATE.yaml`, fixture neutra `tests/fixtures/cartography/`, seeds de SEM ROSTO em `books/sem-rosto/cartography/seeds/`, `tests/test_cartography.py` e `tests/test_redmur_cartography.py`. Desvios do plano: a topologia subterrânea (nós, 11 arestas, 7 portais) foi entregue no S1 e não no S2 (é transcrição, não digitalização); `livingbook.py` não foi tocado. Pendente do S1: conferência humana do inventário contra os mapas. |
| Regras aplicadas | `REUSE > EXTEND > CREATE`; `SIMPLICIDADE SEMPRE`; texto em PT-BR, identificadores em inglês; **geometria é fato, anotação é alegação** (seção 5.3) |

## Decisões da autora (registradas em 2026-09-19)

| OQ | Decisão | Consequência no desenho |
|---|---|---|
| **OQ-CART-02** | **SIM**: os Mapas A e B existem dentro do mundo como documentos | passam a ser artefatos `MAP-DIEGETIC-A/B` (seção 22.5); seus textos viram alegações de um autor do mundo. Quem os produziu, quando e por quê continua **em aberto** (`OQ-CART-02b`) |
| **OQ-CART-03** | **SIM**: os mapas serão **impressos no livro**, inteiros, inclusive o inset "REDE SUBTERRÂNEA" | o leitor conhece a rede subterrânea desde o início (seção 22.6); o mapa do leitor tem linha de base não vazia; imprimir congela as anomalias (`OQ-CART-15`) |
| **OQ-CART-14** | **APROVADOS** os valores de velocidade, modificadores e limiares de visibilidade (seções 16.3, 17.2, 17.3) | deixam de ser "proposta"; mudança futura passa a ser decisão fundacional versionada |
| **OQ-CART-01** | "Considere o mapa dos arredores como uma escala de 100 e Redmur como 7,25% da escala do mapa dos arredores" | Mapa B = **55,86 m/px** (região ≈ 81 × 61 km); núcleo desenhado no Mapa B é esquemático; nós compartilhados usam o Mapa A (seção 7.4). Leitura linear a confirmar |
| **OQ-CART-05** | Black Thistle Filling Station e Sealed Crypt IV estão **no subterrâneo** | ambos `layer: SUBTERRANEAN`, fora do inset impresso, `connectivity: UNDECLARED` (seção 11.6) |
| **OQ-CART-02b** | Autoria dos mapas: discutida no livro, procurada por "entrões", **nunca revelada** | `PERMANENT_AMBIGUITY`: `Q-MAP-AUTHOR` `NEVER`, `author: MUST_REMAIN_UNKNOWN`, `MY-08` (seção 22.7) |
| **OQ-CART-15** | "Proposital vale para as anomalias dos mapas" | **as 22 anomalias do Apêndice B são `INTENTIONAL_ARTIFACT`** (seção 21.6). Deixam de ser inertes: podem alimentar `CMY`/`RMY`/`EVD`. Nenhuma tem significado atribuído, e nenhuma é corrigida; o arquivo impresso é o arquivo pinado |

## Índice

Parte 0 — Discovery (PHASE 0)

1. Purpose · 2. Scope · 3. Non-Goals · 4. Canonical Sources · 5. Terminology ·
6. Architecture · 7. Coordinate System · 8. World Graph Model · 9. Urban Graph ·
10. Regional Graph · 11. Underground Graph · 12. Location Schema · 13. Edge Schema ·
14. Route Schema · 15. Address Registry · 16. Visibility Model · 17. Travel Model ·
18. Hideout Model · 19. Boundary Model · 20. Exit Ambiguity Model ·
21. Cartographic Mystery Model · 22. Official vs Physical vs Reader Maps ·
23. Actor Knowledge · 24. Temporal Cartography · 25. Historical Maps ·
26. Canon Mutation Rules · 27. Scene Integration · 28. Chase Integration ·
29. Validation Gates · 30. Invariants · 31. Data Contracts · 32. Persistence ·
33. Observability · 34. Failure Modes · 35. Test Strategy · 36. Migration Strategy ·
37. Future Extensions · 38. Canonical Location Appendix · 39. Canonical Route Appendix ·
40. Open Questions

Apêndice A — Evidência de transcrição (pixels, recortes, medições) ·
Apêndice B — Anomalias cartográficas detectadas ·
Apêndice C — Condição de sucesso: as perguntas da missão respondidas ·
Apêndice D — Arquivos inspecionados e comandos

Mapeamento das fases da missão (§41) para este documento:

| Fase | Onde |
|---|---|
| PHASE 0 — Discovery | Parte 0 |
| PHASE 1 — SDD | seções 1–37 |
| PHASE 2 — Canon inventory | seções 9–11, 38, 39, Apêndices A e B |
| PHASE 3 — Data contracts | seções 12–15, 18–21, 31 |
| PHASE 4 — Validation design | seções 29, 30 |
| PHASE 5 — Integration design | seções 22–23, 26–28, 32–33, 36 |
| PHASE 6 — Test plan | seção 35 |

---

## Parte 0 — Discovery (PHASE 0)

Todas as afirmações abaixo foram verificadas nesta sessão lendo código,
contratos, templates, pacotes de livro, SDDs e **os dois mapas em resolução
nativa e ampliada** (Apêndices A e D).

### 0.1 O que o repositório já tem

```text
engine/                         motor neutro de gênero (engine/AGENTS.md proíbe canon de obra aqui)
  ENGINE_GRAPH.yaml             CANON_PROPOSAL_PROTOCOL (mutation_owner CANON_GUARDIAN,
                                unapproved_facts_are_canon: false), locks CANON_WRITE / TIMELINE_WRITE
  contracts/CANON_PROPOSAL.schema.json   proposta = texto livre (fact, reason), source_chapter 1..30,
                                additionalProperties: false
  contracts/MEDIA_MANIFEST.schema.json   entities.locations[] (lista livre de ids de local para mídia)
  scripts/livingbook.py         compose; features lidas com .get() (OFF por padrão); T012 WORLD_RULES,
                                T014 WORLD_BIBLE, T017 TIMELINE (Markdown), T018 CANON_REGISTRY, GATE_CANON
  scripts/check_causal_ledger.py      eventos por capítulo; knowledge_delta; knowledge_state(knower, chapter)
                                (:1056); READER_OMNISCIENCE_LEAK (:755-785); mutation_log
  scripts/check_interpretive_canon.py resolution_policy NEVER, MUST_REMAIN_UNKNOWN, prohibited_inferences,
                                HIDDEN_ANSWER_KEYS (:121) — chaves truth/answer/verdade reprovadas
  scripts/check_canon_continuity.py   nomes próprios da prosa que não existem no CANON_REGISTRY
                                (canon_text :90, check_unknown_entities :133)
  scripts/runtime_taskgraph.py  validate-gate executa custom_validators de um gate (:108)
books/narciso/                  precedente de canon POR OBRA: seeds/*.seed.yaml → /canon/<X>.yaml por tarefa
                                adicional do CANON_GUARDIAN; validators/validate_narciso.py; gate_extensions
authors/bea_halden/             perfil de autora (Visual DNA + approvals/ com subject_sha256)
docs/sdd/DYSTOPIC_ENIGMA_DARK_ROMANCE_SDD_v0.1.md   SEM ROSTO como caso-modelo (§33), sem pacote de livro
```

### 0.2 Mapa por item de discovery pedido (missão §1.2)

| Item pedido | Componente real | Estado | Leitura para a cartografia |
|---|---|---|---|
| Canon | `CANON_REGISTRY.yaml` (forma livre) + `CANON_PROPOSAL_PROTOCOL` | código + contrato | REUSE: dono único `CANON_GUARDIAN`; proposta textual |
| World State | `WORLD_RULES.md`, `WORLD_BIBLE.md` (prosa); ids `WR-*` propostos pelo DEDR | Markdown | não há estado de mundo estruturado; espaço físico não existe em lugar nenhum |
| Memory | "o repositório é a memória"; snapshots por wave (`canon/snapshots/`) | padrão | REUSE: snapshots da cartografia por wave |
| Registries | `CANON_REGISTRY.yaml` (`unknowns`, `prohibited_inferences`) | arquivo sem schema | REUSE para incógnitas e inferências proibidas **cartográficas** |
| Knowledge graphs | ledger causal (grafo causal de eventos), canon interpretativo (grafo de perguntas/evidências) | código | **nenhum grafo espacial**; REUSE do padrão de validador determinístico stdlib + PyYAML |
| Scene planning | `BRIEFING_ARCHITECT`, `SCENE_ARCHITECT`, briefs Markdown por capítulo | agentes + Markdown | EXTEND: um *pack* determinístico anexado ao brief (seção 27) |
| Character movement | — | **inexistente** | CREATE (staging + movimentos, seção 17.6) |
| Location systems | `entities.locations[]` do manifesto de mídia; `T014_WORLD_BIBLE` em prosa | lista livre / prosa | CREATE o grafo; o manifesto de mídia passa a referenciar os mesmos ids (REUSE de id) |
| Mystery systems | canon interpretativo (NEVER, evidência, narradores), DEDR (códigos, fontes não confiáveis) | código + proposta | REUSE: mistério cartográfico é **evidência espacial** de perguntas do canon interpretativo |
| Validation gates | `GATE_CANON`, `GATE_WAVE_n`, `GATE_FULL_MANUSCRIPT`; `custom_validators` + `gate_extensions` | código | REUSE integral (padrão Narciso) |
| Narrative continuity | `check_canon_continuity.py`, `PLOT_CONTINUITY_REVIEWER`, `WORLD_RULES_REVIEWER`, `REALISM_ENGINEER` | código + agentes | EXTEND mínimo: nomes de lugar entram no vocabulário canônico |
| Schemas | `engine/contracts/*.schema.json` | JSON Schema 2020-12 | CREATE `CARTOGRAPHY.schema.json` na mesma convenção |
| SDDs existentes | 10 SDDs em `docs/sdd/` | — | convenção de nome `<NOME>_SDD_v0.1.md`, status E0, slice plan, OQs |
| Testes | `tests/test_*.py` + `tests/fixtures/<capability>/` | pytest | CREATE `tests/test_cartography.py` + fixture neutra + teste de dados da obra |

### 0.3 REUSED / EXTENDED / CREATED

| Conceito da missão | Decisão | Componente | Justificativa |
|---|---|---|---|
| Mutação canônica (missão §22) | **REUSE** | `CANON_PROPOSAL_PROTOCOL` + `mutation_log` (padrão ledger) | a proposta continua textual; o *diff estruturado* mora na cartografia com `proposal_ref` (seção 26) |
| Conhecimento por ator (§21) | **REUSE** | `knowledge_delta.learns` do ledger aceita qualquer id (`check_causal_ledger.py:761-763` ignora ids que não são GT) | "CHR-X aprende EDG-SUB-07" é um `knowledge_delta` comum; nenhuma mudança no ledger |
| Mapa do leitor (§20) | **REUSE** | `knowledge_state(ledger, "READER", chapter)` | o mapa do leitor é **projeção**, nunca arquivo |
| Verdade não revelável (§17, §38) | **REUSE** | `resolution_policy: NEVER`, `MUST_REMAIN_UNKNOWN`, `HIDDEN_ANSWER_KEYS`, GT com `reader_access` | a cartografia não guarda resposta — **por construção** (seção 20.4) |
| Enigmas cartográficos (§18) | **REUSE + EXTEND de dados** | perguntas `Q-*` e evidências `EVD-*` do canon interpretativo | `CARTOGRAPHIC_MYSTERY` é o **lado espacial** de uma pergunta; não é um segundo sistema de mistério |
| Gates | **REUSE** | `custom_validators` + `gate_extensions` | nenhum gate novo |
| Nomes de lugar novos (INV 09) | **EXTEND** | `check_canon_continuity.py` passa a ler nomes/aliases da cartografia | hoje só lê o registry; uma função a mais |
| Digest de canon | **EXTEND** (opcional) | `build_canon_digest.py` | acrescenta bloco compacto de lugares ao digest |
| Grafo espacial (nós, arestas, rotas, subsolo) | **CREATE** | `engine/contracts/CARTOGRAPHY.schema.json`, `engine/scripts/check_cartography.py`, `engine/templates/CARTOGRAPHY_TEMPLATE.yaml` | nada equivalente existe; é neutro de gênero (qualquer livro com lugares) |
| Relógio de cena, staging e movimentos | **CREATE** | `STAGING.yaml` na cartografia | o ledger só tem `chapter`, não relógio nem lugar; estendê-lo contaminaria uma capability causal com física (D-CART-06) |
| Dados de Redmur | **CREATE** | `books/sem-rosto/cartography/` | DNA da obra, fora de `/engine` (engine/AGENTS.md) |
| Agente cartográfico | **NÃO CRIAR** | `WORLD_ARCHITECT` propõe, `CANON_GUARDIAN` decide, `REALISM_ENGINEER` e `PLOT_CONTINUITY_REVIEWER` leem relatórios | o validador conta; os agentes existentes julgam (princípio do DR SDD §D) |
| "Mapa oficial" como camada | **CREATE (dados)** | artefatos `MAP-*` com `depicts[]` | um mapa dentro da história é um objeto versionado que faz alegações sobre o grafo físico |

### 0.4 Divergências e riscos encontrados (registrados, não corrigidos)

| ID | Achado | Evidência | Decisão nesta SDD |
|---|---|---|---|
| **D-CART-01** | Os mapas canônicos **não estão no repositório** | encontrados em `~/Downloads/SEM ROSTO/` | Slice 0 versiona os PNGs em `books/sem-rosto/cartography/sources/` com sha256 pinado; toda coordenada cita `source_px` |
| **D-CART-02** | **Os dois mapas não dizem a mesma escala.** A barra do Mapa B implica 49–107 m/px; o ajuste sobre 14 lugares comuns dá 6,94 m/px | Apêndice A.4 | **RESOLVIDO** por decisão da autora (2026-09-19): Mapa A = 7,25 % da escala do Mapa B ⇒ 55,86 m/px; núcleo do Mapa B declarado esquemático (seção 7.4) |
| **D-CART-03** | R1 no Mapa A liga **Old Parish Cemetery à borda oeste do centro** (entre a capela e o Office of Civic Preservation); **não** toca a capela nem a rede de drenagem | recorte `city_00`, Apêndice A.2 | o mapa vence o briefing (missão §7); a ligação capela→cemitério→Culvert Exit existe **só** pela rede subterrânea (inset), não pela R1 |
| **D-CART-04** | R3 no Mapa A liga **Old Quarry a Manfred Farm**; **nenhum** trecho segue para a East Road | recorte `city_01` | idem D-CART-03; "direção da East Road" registrada como leitura do briefing não sustentada pelo mapa |
| **D-CART-05** | O trajeto Shepherd's Bothy ↔ Strathmoor Woods ↔ Rowan Cottage é **R2** no Mapa A e **R3** no Mapa B | `city_01`/`city_02` × `reg_01` | conflito de rótulo entre fontes canônicas → anomalia `ANM-X-01`, preservada, não corrigida |
| **D-CART-06** | O ledger causal não tem relógio nem lugar (`events[].chapter` inteiro) | `CAUSAL_LEDGER_TEMPLATE.yaml` | staging/movimento vivem na cartografia e **referenciam** `EV-*`; o ledger não muda |
| **D-CART-07** | `CANON_PROPOSAL.schema.json` exige `source_chapter` 1..30 e texto livre | contrato | decisões fundacionais pré-escrita (escala, âncoras) vão para `approvals/` (padrão AUTHOR_DNA); proposta canônica só para mutações nascidas na narrativa |
| **D-CART-08** | A missão pede `actual_pattern` e `false_interpretations` em `CARTOGRAPHIC_MYSTERY` | missão §18 | **desvio deliberado**: guardar o padrão real ou rotular interpretações como falsas é resposta escondida (LTE AD-02, `HIDDEN_ANSWER_KEYS`). Substituídos por `truth_ref` (id opaco) e `candidate_interpretations[]` sem valor de verdade (seção 21) |
| **D-CART-09** | A missão lista `TRUE_EXIT` como algo a nunca inferir | missão §15, §27 INV 07 | `TRUE_EXIT` **não é valor representável** em nenhum enum da cartografia (seção 20.4) — a garantia mais forte possível |
| **D-CART-10** | Dois lugares da missão **não aparecem em nenhum mapa**: `Black Thistle Filling Station` e `Sealed Crypt IV` | varredura completa dos dois mapas (Apêndice A) | **RESOLVIDO** pela autora (2026-09-19): estão no **subterrâneo**, fora do inset impresso (seção 11.6); como se ligam à rede: `OQ-CART-05b` |
| **D-CART-11** | Dois nomes do registro regional **não estão localizados** no Mapa B (`17 Letham`, `23 Passo de Muirchéin`), e um lugar do mapa **não está no registro** (`Muirfield Farm`) | `z_reg`, `z_nw` | registro é artefato; entradas sem lugar ficam `placement: NOT_ON_MAP` — o mapa diz "Nem todo nome no mapa é um lugar" |
| **D-CART-12** | O inset "REDE SUBTERRÂNEA" do Mapa A é **esquemático**: põe Quarry Crawlspace ao lado do Pumping Station Channel, mas na superfície Old Quarry e Pumping Station distam ≈ 3,3 km | `city_12` × coordenadas | topologia do inset = fato; posição no inset ≠ geografia; comprimento mínimo de túnel = distância entre âncoras de superfície (seção 11.4) |
| **D-CART-13** | Os mapas têm traços de renderização gerada (texto corrompido "REDNUR SEMPBE OBSERVA", barras de escala irregulares, índice `05` duplicado) | Apêndice B | toda anomalia nasce `UNDECIDED`: nem erro corrigido, nem pista. A autora classifica (`INTENTIONAL_ARTIFACT` / `RENDER_ERROR`); enquanto `UNDECIDED`, não pode ser usada como pista (seção 21.6) |
| **D-CART-14** | Os mapas têm aparência **diegética** (lemas "Disciplina. Memória. Preservação.", "Redmur sempre observa") — parecem mapas oficiais do próprio mundo | Mapas A e B | princípio de dupla leitura (seção 5.3): como fonte de produção, sua **geometria** é fato físico; seus **textos** são alegações de um artefato que ainda não se sabe quem produziu (`OQ-CART-02`) |
| **D-CART-15** | Não existe pacote `books/sem-rosto/`; o DEDR adia o pacote real para o seu S6 | DEDR §30 | a cartografia cria **só** `books/sem-rosto/cartography/` + `README.md` (pacote parcial, não compõe) — nada em `livingbook.py` itera `books/*` (verificado) |
| **D-CART-16** | Working tree tem mudanças não commitadas de outras frentes em `livingbook.py`, `run_deterministic.py`, `runtime_taskgraph.py` | `git status` | esta SDD não toca esses arquivos; o Slice de integração (S5) começa depois que eles forem versionados |

### 0.5 Conclusão do discovery

O motor sabe **quem causou o quê** (ledger), **o que pode ser pensado sobre
isso** (canon interpretativo) e **quem sabe o quê** (knowledge_state). Não sabe
**onde** nada acontece. A cartografia é a quarta perna, e se encaixa pelas
mesmas juntas: ids opacos, projeções em vez de arquivos, validadores
determinísticos em gates existentes, dono único do canon. O único conceito
realmente novo é **espaço + tempo de relógio** (grafo físico, staging e
movimento). Todo o resto — conhecimento, mistério, mutação, leitor — é REUSE.

---

## 1. Purpose

Transformar Redmur de **cenário** em **sistema espacial canônico** que:

1. registra cada lugar, caminho, túnel, ponte, rio e fronteira dos dois mapas
   oficiais como entidade com id, posição, proveniência e estado;
2. responde deterministicamente perguntas espaciais do planejamento de cena
   (distância, tempo, alcance, visibilidade, fuga, perseguição);
3. reprova, antes e depois da escrita, qualquer cena que teletransporte
   personagem, atravesse água sem travessia, use caminho secreto desconhecido,
   atravesse local fechado sem ação correspondente ou contradiga os mapas;
4. dá ao mistério cartográfico de SEM ROSTO uma infraestrutura (saídas ambíguas,
   rotas contestadas, registro numerado, mapas que mentem) **sem jamais
   resolvê-lo** — a resposta, quando existir, pertence ao Story Truth Ledger.

Princípio central (missão §39): **ambiguidade para o leitor não pode
significar ambiguidade para o motor** — exceto onde a própria verdade está
deliberadamente marcada `UNKNOWN`/`MUST_REMAIN_UNKNOWN` no canon da história.

## 2. Scope

| Dentro | Fora (seção 3) |
|---|---|
| Geografia, topologia, coordenadas, distâncias, rotas, acessos, subsolo, fronteiras, deslocamentos, visibilidade, esconderijos, perseguições | O **significado** de qualquer padrão, a identidade da saída verdadeira, a origem dos Cofres, a história de Redmur |
| Três escalas: Urban (Mapa A), Regional (Mapa B), Subterrânea (inset do Mapa A) e seus elos | Qualquer lugar fora das molduras dos dois mapas (é `OFF_MAP`, domínio do canon da história) |
| Camadas oficial / física / leitor / ator / histórica | Personagens, relações, eventos (ledger), perguntas e teses (canon interpretativo) |
| Mapas como artefatos versionados dentro da narrativa | Geração de imagem de mapa (visual narrative / media) |
| Mutação temporal do espaço via proposta canônica | Motor de jogo, simulação contínua, física de corpos |

## 3. Non-Goals

- **Não** é game engine. Perseguição é verificada por intervalos de tempo em
  nós do grafo, não simulada quadro a quadro.
- **Não** resolve enigmas: nenhum algoritmo classifica saída como verdadeira,
  interpreta rota contestada, decodifica o registro ou declara distância falsa.
- **Não** inventa precisão: onde o mapa não mede, o sistema guarda intervalo,
  proveniência e `UNKNOWN`.
- **Não** acrescenta sobrenatural: nada de portais, teletransporte,
  arquitetura impossível ou estrada que se move. `PHYSICAL_REALISM = TRUE`
  (seção 30, INV-C00) até decisão canônica explícita em contrário.
- **Não** cria lugar por conveniência: nenhum esconderijo, atalho, túnel ou
  endereço entra sem proposta aprovada.
- **Não** decide o que é impresso para o leitor (quais mapas viram paratexto)
  — isso é `OQ-CART-03`, decisão editorial.
- **Não** substitui `TEMPORAL_ARCHITECT`: o calendário e o relógio da história
  pertencem ao `TIMELINE`; a cartografia só exige que marcas de tempo de cena
  sejam comparáveis (seção 17.6).

## 4. Canonical Sources

### 4.1 Hierarquia de fontes

```text
S1  MAPA A  REDMUR — MAPA CANÔNICO DA CIDADE          (Level 1 + inset subterrâneo)
S2  MAPA B  REDMUR — MAPA CANÔNICO DOS ARREDORES      (Level 2)
S3  MISSION BRIEF desta SDD (texto da autora)          só para: tipos, nomes declarados fora dos mapas
S4  CANON_PROPOSALS aprovadas / approvals/             mutações e decisões posteriores
```

Regras de precedência:

1. **Mapa vence briefing** em posição, adjacência, conectividade e extensão de
   traçado (missão §7). Divergências viram `D-CART-*`, nunca correções.
2. **Dentro da moldura do Mapa A, o Mapa A é a autoridade métrica.** O Mapa B
   é autoridade de topologia e de posição relativa para tudo que o Mapa A não
   mostra, e para a métrica regional **depois** de `OQ-CART-01`.
3. Conflito entre Mapa A e Mapa B sobre o **mesmo** atributo (rótulo de rota,
   nome) **não é resolvido**: vira anomalia `ANM-X-*` (Apêndice B) com as duas
   leituras preservadas.
4. S3 só cria entidade que **não contradiz** S1/S2 (ex.: `Sealed Crypt IV`
   entra sem posição; `Black Thistle Filling Station` entra sem posição).
5. S4 muda o canon só por mutação registrada (seção 26), nunca por edição.

### 4.2 Pinagem

```yaml
# books/sem-rosto/cartography/sources/SOURCES.yaml   (Slice 0)
sources:
  - id: SRC-MAP-A
    title: "REDMUR — MAPA CANÔNICO DA CIDADE"
    subtitle: "District of Civic Preservation — Scottish Interior"
    file: sources/MAP_A_redmur_map.png
    sha256: 98123fee45ea70b220c46bef719d2644729231d0f8df5d1ac00d90f6f9525f36
    pixels: [1448, 1086]
    north: UP                      # rosa dos ventos: N para cima, O/L nas laterais
    scale_evidence: {bar_px: [186, 433], bar_m: [0, 1000], anomalies: [ANM-A-01]}
    grid: {columns: [A,B,C,D,E,F,G,H], rows: [1,2,3,4,5,6,7], spacing: IRREGULAR}   # ANM-A-02
  - id: SRC-MAP-B
    title: "REDMUR — MAPA CANÔNICO DOS ARREDORES"
    subtitle: "Terras, Vilarejos e Caminhos da Escócia Interior"
    file: sources/MAP_B_redmur_arredores_map.png
    sha256: 36cf98babb4864d0913847c845364641d55120836d8960e8e88cb4373a43b9f3
    pixels: [1448, 1086]
    north: UP
    scale_evidence: {bar_px: [901, 1143], bar_km: [0, 20], anomalies: [ANM-B-03]}
    grid: {columns: [A..M], rows: [1..10], spacing: REGULAR_APPROX}
```

Validador: `SOURCE_HASH_MISMATCH` (BLOCKER) se o arquivo pinado mudar sem nova
versão de fonte. Um mapa corrigido (ex.: a autora decide que `05` duplicado era
erro de renderização) entra como **nova fonte** `SRC-MAP-B@v1.1` com
`supersedes`, e a antiga fica arquivada — nunca sobrescrita.

### 4.3 O que é transcrito, e com que confiança

| Classe de elemento no mapa | Vira | Confiança padrão |
|---|---|---|
| Rótulo de lugar | nó + nome (`names[].kind = MAP_A_LABEL/MAP_B_LABEL`) | `CONFIRMED_VISUAL` |
| Ícone/edificação com rótulo | posição do nó (`source_px` do ícone, não do rótulo) | ±15 px |
| Linha de estrada/trilha | aresta(s) com `source_polyline_px` (digitalização, Slice 2) | `PROBABLE` até conferência humana |
| Linha vermelha tracejada (rota) | aresta física + pertinência a rota | `CONFIRMED_VISUAL` no traçado desenhado; `UNKNOWN` além dele |
| Hachura vermelha / X | estado de acesso (`RESTRICTED`/`BLOCKED`) como **alegação oficial** + fato físico de barreira no ponto | ver 5.3 |
| Texto solto (lemas, avisos, placas) | `MAP-*` artefato: alegação, nunca fato | — |
| Ornamento (rosas, serpente, caveira, rosa-dos-ventos) | artefato de ornamento, `cartographic_meaning: NONE_ASSUMED` | registrado, não interpretado |
| Glifo ilegível | `GLY-*` com posição e leituras candidatas | `ILLEGIBLE` |
| Edificação sem rótulo | `UNL-*` (não é lugar canônico até proposta) | — |

## 5. Terminology

### 5.1 Termos

| Termo | Definição |
|---|---|
| **RCG** | *Redmur Canonical Grid*: sistema cartesiano interno em metros, origem em Saint Morrow Cross (seção 7) |
| **Node / Location** | lugar com id (`RM-*`); pode ser ponto (edifício), área (bosque, campo) ou linha (rio) com ponto representativo |
| **Edge** | conexão física traversável entre dois nós, entidade canônica própria (`EDG-*`) |
| **Road / Trail entity** | agregado nomeado de arestas (`ROAD-*`), ex.: South Gate Road |
| **Route** | sequência nomeada de arestas com identidade narrativa (`RTE-*`), ex.: R1 |
| **Portal** | aresta vertical ou de acesso que liga superfície e subsolo, ou mapa A e mapa B |
| **Frame portal** | nó na moldura de um mapa por onde uma via sai do recorte desenhado |
| **OFF_MAP** | tudo além das molduras; a cartografia não modela, o canon da história pode |
| **Artifact** | mapa, placa, registro ou texto **dentro do mundo** que faz alegações sobre o espaço (`MAP-*`) |
| **Claim** | afirmação de um artefato ou fonte sobre o espaço, com `epistemic_status` |
| **Anomaly** | inconsistência detectada nas fontes canônicas (`ANM-*`), aguardando classificação da autora |
| **Staging** | fato planejado/realizado de "ator X está no lugar L no instante T" (`STG-*`) |
| **Movement** | deslocamento declarado entre dois stagings (`MOV-*`) |
| **Story Truth Ledger** | nome, nesta SDD, do conjunto de verdades narrativas: GTs do ledger causal com `reader_access` + perguntas/incógnitas do canon interpretativo + o futuro SDD de canon histórico |
| **Truth ref** | id opaco (`GT-*`, `Q-*`, `UNK-*`) que aponta para o Story Truth Ledger; a cartografia nunca copia o conteúdo |

### 5.2 Status epistêmico (missão §37)

Todo atributo que não é geometria desenhada carrega um `epistemic_status`:

| Valor | Significado | Quem pode atribuir |
|---|---|---|
| `FACT` | verdade física canônica | fonte S1/S2 (geometria) ou mutação aprovada |
| `OFFICIAL_CLAIM` | o que uma autoridade do mundo afirma (ex.: "Officially Closed") | transcrição de artefato |
| `HISTORICAL_CLAIM` | o que um registro antigo afirma | artefato histórico |
| `RUMOR` | o que circula sem fonte documental | canon da história |
| `MYSTERY` | elemento deliberadamente aberto, ligado a pergunta `Q-*` | canon interpretativo |
| `FALSE_MAP_DATA` | alegação de artefato que **contradiz** o grafo físico | **só** com prova física na própria cartografia (o grafo físico mostra o contrário) **ou** `truth_ref` resolvido |
| `UNKNOWN` | ninguém — nem o motor — decidiu ainda | padrão para tudo que as fontes não mostram |

Regra: um valor só sobe de `UNKNOWN`/`*_CLAIM` para `FACT` por fonte S1/S2 ou
mutação aprovada. **Padrão percebido não é fonte** (missão §18).

### 5.3 Princípio de dupla leitura: geometria é fato, anotação é alegação

Os mapas são ao mesmo tempo **fonte de produção** (a autora os declarou
canônicos) e **objetos com cara de documento oficial do mundo** (lemas do
District of Civic Preservation). O desenho resolve isso assim:

| Elemento | Leitura física (motor) | Leitura diegética (mistério) |
|---|---|---|
| Posição de lugar, traçado de via, rio, lago, ponte | **FACT** | — |
| Nome em rótulo | **FACT** (o lugar se chama assim neste mapa) | pode haver outros nomes |
| "Officially Closed", "Em Disputa", "Entrada Principal" | barreira/estado físico no ponto = `UNKNOWN` salvo marca física desenhada (X = barreira física `FACT`) | `OFFICIAL_CLAIM` |
| Barra de escala, distâncias em placas | **não** são métrica física (seção 7.4) | `OFFICIAL_CLAIM`/`MAP_ARTIFACT` |
| Lemas, avisos, registro numerado, lemas das rotas | nada | artefatos de mistério |
| Linha desenhada além da qual nada é desenhado | a via existe **até onde foi desenhada** | continuação = `UNKNOWN`/`OFF_MAP` |

Assim o motor sabe exatamente onde os caminhos **estão**, e o mistério fica
com tudo o que os caminhos **significam**.

---

## 6. Architecture

### 6.1 Camadas

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│ OBRA   books/sem-rosto/cartography/                                               │
│   sources/ (PNGs pinados)  seeds/*.seed.yaml (inventário, arestas, rotas, subsolo,│
│   artefatos, mistérios, camadas, conhecimento-base)  approvals/ (decisões)        │
├──────────────────────────────────────────────────────────────────────────────────┤
│ RUNTIME  runtime/sem-rosto/canon/cartography/*.yaml  (dono: CANON_GUARDIAN)       │
│          runtime/sem-rosto/canon/cartography/STAGING.yaml (PLANNED → REALIZED)    │
│          runtime/sem-rosto/briefs/cartography/CHAPTER_NN_PACK.yaml (gerado)       │
│          runtime/sem-rosto/reports/cartography/*.json|md (gerado)                 │
├──────────────────────────────────────────────────────────────────────────────────┤
│ MOTOR (neutro)                                                                    │
│   contracts/CARTOGRAPHY.schema.json · templates/CARTOGRAPHY_TEMPLATE.yaml         │
│   scripts/check_cartography.py  = validador + biblioteca de consultas             │
│      importa: check_causal_ledger.knowledge_state (conhecimento, leitor)          │
│               check_interpretive_canon.HIDDEN_ANSWER_KEYS (proteção de mistério)  │
│   livingbook.py: features.cartography (OFF por padrão) → T018C, gates, pack       │
├──────────────────────────────────────────────────────────────────────────────────┤
│ CAPABILITIES EXISTENTES (inalteradas)                                             │
│   CAUSAL_LEDGER (eventos, knowledge_delta, GT/reader_access)                      │
│   INTERPRETIVE_CANON (Q-*, EVD-*, NEVER)   CANON_REGISTRY (unknowns, prohibited)  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Por que capability do motor e não validador da obra

| Critério | Validador só da obra (padrão Narciso) | Capability neutra (padrão causal ledger) |
|---|---|---|
| DNA de gênero no código? | — | **nenhum**: nós, arestas, tempo, visibilidade e alegações servem a qualquer livro com lugares |
| Reuso no 2º livro | cópia | ligar a feature |
| Risco de abstração prematura (DR SDD Q1) | baixo | baixo: o domínio é física + epistemologia, não gênero |
| Custo no motor | zero | 1 script, 1 contrato, 1 template, ~40 linhas em `livingbook.py` (S5) |

Recomendação: **código neutro no motor desde o S1**, mas o compose só é
tocado no S5. Até lá o validador roda standalone contra fixture e contra os
seeds da obra (mesmo caminho dos Slices 1–2 do LTE).

### 6.3 Fluxo

```text
autora + WORLD_ARCHITECT ──propõe──▶ seeds (books/sem-rosto/cartography/seeds)
                                      │  approvals/ (escala, âncoras, anomalias)
T018C_CARTOGRAPHY (CANON_GUARDIAN, lock CANON_WRITE) ──▶ /canon/cartography/
GATE_CANON  ◀── V_CARTO_CANON (integridade, física, proteção de mistério)
briefing de capítulo ──▶ staging PLANNED ──▶ check_cartography --pack ──▶ CHAPTER_NN_PACK
escrita ──▶ staging REALIZED ──▶ GATE_WAVE_n ◀── V_CARTO_WAVE (viagem, conhecimento, acesso, perseguição)
evento que muda o espaço ──▶ CANON_PROPOSAL + mutations[] ──▶ estado por capítulo
GATE_FULL_MANUSCRIPT ◀── V_CARTO_FINAL
```

---

## 7. Coordinate System

### 7.1 REDMUR CANONICAL GRID (RCG)

| Eixo | Sentido | Unidade |
|---|---|---|
| `x` | oeste (−) → leste (+) | metro |
| `y` | sul (−) → norte (+) | metro |
| `z` | elevação **relativa** ao nível do solo em Saint Morrow Cross (`z = 0`); subsolo negativo | metro |

- **Origem:** `RM-CEN-SMC` Saint Morrow Cross = `(0, 0, 0)` por **definição**
  (o próprio Mapa A imprime "(0,0)" sob o monumento). Ponto de referência: a
  base do monumento, pixel `(521, 527)` do Mapa A.
- **Norte de grade = norte do mapa** (as duas rosas dos ventos apontam N para
  cima; nenhuma declinação é informada — `OQ-CART-10` só se a obra precisar).
- **Altitude absoluta** (`elevation_asl`) é campo separado. Só um valor absoluto
  existe nas fontes: **Ben Ràth, 714 m**. A altitude de Saint Morrow Cross é
  `UNKNOWN`; enquanto for, `z` de Ben Ràth relativo à origem é `UNKNOWN`.
- **Sem GPS real.** A "Escócia Interior" é ambientação; nenhuma coordenada do
  mundo real é canônica.

### 7.2 Transformação do Mapa A (Level 1 e âncoras de subsolo)

```text
x_m = (px_x − 521) × 4,05
y_m = (527 − px_y) × 4,05
```

- Escala derivada **das extremidades** da barra (0 m em px 186; 1.000 m em
  px 433 → 247 px = 1.000 m → **4,05 m/px**). As marcas internas da barra são
  irregulares e rotuladas `0 · 250 · 300 · 750 · 1.000 m` (o "300" ocupa a
  posição de um 500) → `ANM-A-01`; por isso só as extremidades são usadas.
- Moldura do Mapa A em RCG: `x ∈ [−2110, +3754]`, `y ∈ [−2264, +2134]`
  (≈ 5,9 × 4,4 km).
- Precisão de posição: `position_accuracy_m = 60` para ícones (±15 px),
  `150` para áreas (bosque, campo), `UNKNOWN` para o que não tem ícone.

### 7.3 A grade de referência dos mapas

O Mapa A tem colunas `A–H` e linhas `1–7`; o Mapa B, colunas `A–M` e linhas
`1–10`. No Mapa A os centros das colunas **não são equidistantes**
(137, 293, 437, 578, 783, 909, 1040, 1165 px) → `ANM-A-02`.
`map_grid_reference` é portanto **rótulo de localização**, derivado da célula
cujo centro é o mais próximo, **nunca** métrica. Formato: `A:D4` (mapa A,
célula D4), `B:H6`.

### 7.4 Escala regional (decisão OQ-CART-01, 2026-09-19)

Decisão da autora: **"Considere o mapa dos arredores como uma escala de 100 e
Redmur como 7,25% da escala do mapa dos arredores."**

**Leitura adotada (linear):** a razão de escala Mapa A : Mapa B é **7,25 : 100**.
Como o Mapa A tem 4,05 m/px, o Mapa B tem

```text
s_B = 4,05 / 0,0725 = 55,86 m/px
```

| Consequência | Valor |
|---|---|
| Moldura do Mapa B (1448 × 1086 px) | ≈ **80,9 × 60,7 km** |
| Moldura do Mapa A em km | ≈ 5,86 × 4,40 km = **7,25 %** da largura do Mapa B (a mesma razão) |
| Pegada do Mapa A dentro do Mapa B | ≈ 105 × 79 px em torno da cruz `(638, 530)`: x 585–690, y 490–570 |
| Vilarejos do Mapa B | de ≈ 11 km (Cairnvale) a ≈ 33 km (Ruínas de Kellburne) da cruz |
| Verificação com a barra do Mapa B | o trecho 0→5 km dá 49 m/px (−12 % em relação a 55,86); a faixa interna da barra (49–107 m/px) contém o valor; 0→20 km dá 82,6 m/px. A barra é **irregular** (`ANM-B-03`, intencional) e **não** é a escala: a escala é a decidida |

**Consequência para os lugares desenhados nos dois mapas** (capela, cemitério,
Old Quarry, Sheep Fields, Shepherd's Bothy, Manfred Farm, Flarry Estate, Rowan
Cottage, Reservoir, Pumping Station, Burn Bridge, East Road, South Gate Road):
no Mapa B eles aparecem espalhados por até ≈ 250 px, fora da pegada de 105 px
que a razão 7,25 % reserva ao Mapa A. Portanto **o Mapa B desenha o núcleo de
Redmur ampliado**; a razão 7,25 % só se cumpre se as posições desses lugares no
Mapa B forem tratadas como **esquemáticas** (ordem, direção, adjacência e
topologia preservadas; métrica não). Regras:

1. **Nós presentes nos dois mapas:** posição métrica = **Mapa A**. O `source_px`
   do Mapa B é registrado com `anchor: SCHEMATIC` e **não** entra em nenhum
   cálculo de distância.
2. **Nós só do Mapa B:** posição = px do Mapa B × 55,86 m/px a partir da cruz,
   **sem rotação** (as duas rosas dos ventos apontam N para cima; a rotação de
   −2,1° do ajuste anterior nascia de tratar os nós compartilhados como
   métricos e foi descartada).
3. `position_accuracy_m = 840` (±15 px do Mapa B); `coordinate_status:
   CANONICAL`. Precisão menor (áreas, glifos ilegíveis) declarada por item.
4. **Anel de transição:** para vias que ligam a pegada do Mapa A ao restante
   do Mapa B, o comprimento no trecho dentro da pegada vem do Mapa A e fora
   dela do Mapa B; o nó de junção é o `FRAME_LINK` (seção 8.1).
5. As distâncias em **milhas** das placas e a barra do Mapa B são
   `OFFICIAL_CLAIM` de artefato: continuam alegações, nunca entram na física.
   O motivo de a barra e as placas não baterem com a escala é `MYSTERY`
   (`CMY-06`); a cartografia não o explica.

Transformação (Mapa B → RCG) para nós exclusivos do Mapa B, ancorada na cruz do
Mapa B:

```text
x_m = (px_x − 638) × 55,86
y_m = (530 − px_y) × 55,86
position_accuracy_m = 840
xform_id = XFM-B@S7.25   # scale_ratio_A_to_B = 0,0725; recalcula tudo se mudar
```

**Interpretação a confirmar:** adotei "7,25 % da escala" como razão **linear** de
escala. Se a autora quis dizer **área** (Redmur ocupa 7,25 % da *área* do Mapa B),
a escala seria ≈ 15,0 m/px e a região ≈ 22 × 16 km; não foi adotada porque a
própria barra do Mapa B (49–107 m/px) a exclui. Trocar exige apenas alterar
`scale_ratio_A_to_B` (nenhuma coordenada é digitada à mão).

Histórico (não adotado): hipótese H-A (layouts verdadeiros, Mapa B ≈ 6,94 m/px,
região ≈ 10 × 7,5 km) e H-B (barra literal, ≈ 83 m/px). A decisão da autora
fica entre as duas e tem uma vantagem sobre H-A: **preserva a razão 7,25 : 100
entre os mapas**, ao custo de declarar esquemático o desenho do núcleo no
Mapa B.

### 7.5 Funções do sistema de coordenadas (missão §3)

Todas puras, determinísticas, sem dependência externa (stdlib `math`):

| Função | Retorno | Notas |
|---|---|---|
| `distance(A, B)` | `{euclid_m: [min, nominal, max], graph_m?: [...], basis}` | intervalo = nominal ± soma das precisões; `graph_m` quando há caminho |
| `bearing(A, B)` | `{degrees, compass16}` | 0° = norte, horário |
| `walking_time(A, B, ctx)` | `{min_s, expected_s, max_reasonable_s, path}` | seção 17 |
| `running_time(A, B, ctx)` | idem, modo `RUN` | |
| `vehicle_time(A, B, ctx)` | idem, modo `VEHICLE`; `NO_VEHICLE_ACCESS` se nenhuma aresta permitir | |
| `reachable(A, B, ctx)` | `{reachable: bool, path?, blocked_by: [...]}` | respeita conhecimento, estado e acesso |
| `shortest_route(A, B, ctx)` | caminho de menor tempo esperado | Dijkstra |
| `safest_route(A, B, ctx)` | menor risco × exposição | pesos da seção 17.5 |
| `hidden_route(A, B, ctx)` | menor visibilidade, só arestas **conhecidas pelo ator** | nunca usa segredo desconhecido |
| `escape_routes(A, ctx)` | rotas para esconderijos, portais e saídas aparentes, ordenadas | seção 28 |
| `visible_from(A, B, ctx)` | `VISIBLE | PARTIAL | NOT_VISIBLE | UNDETERMINED` + `basis` | seção 16 |

`ctx` = `{actor?, chapter, story_time?, mode, conditions{lighting, weather,
injury, carrying, pursuit}, knowledge_view: ACTOR|ENGINE}`. Toda consulta sem
`actor` roda em `knowledge_view: ENGINE` e o resultado é marcado
`ENGINE_VIEW — não entregar ao leitor nem a personagem`.

## 8. World Graph Model

### 8.1 Um grafo, três escalas, várias camadas

```text
                    ┌──────────── camadas de alegação (não mudam a física) ─────────────┐
                    │ OFFICIAL (MAP-*)   HISTORICAL (LYR-*)   PRIVATE (MAP-*)   READER    │
                    └───────────────────────────────▲────────────────────────────────────┘
                                                    │ depicts / omits / renames / falsifies
┌──────────────── PHYSICAL WORLD GRAPH (verdade espacial; dono CANON_GUARDIAN) ─────────────┐
│ L1 URBAN   (Mapa A)   RM-CEN-*, RM-URB-*       ◀── FRAME_PORTAL ──▶  L2 REGIONAL (Mapa B) │
│        ▲ PORTAL (vertical)                                            RM-REG-*, RM-OFF-*   │
│        ▼                                                                                   │
│ L3 SUBTERRANEAN (inset do Mapa A)  RM-SUB-*                                                │
└────────────────────────────────────────────────────────────────────────────────────────────┘
        ▲ estado por capítulo (mutations[])         ▲ quem conhece o quê (ledger knowledge_delta)
```

- **Um único espaço de ids e um único grafo**; `layer ∈ {URBAN, REGIONAL,
  SUBTERRANEAN}` é atributo, não arquivo separado de verdade. Isso torna
  trivial a consulta que cruza escalas (capela → porão → drenos → culvert).
- **Nós compartilhados** entre Mapa A e Mapa B (Flarry Estate, Manfred Farm,
  Rowan Cottage, Shepherd's Bothy, Old Quarry, Sheep Fields, a capela, o
  cemitério, a cruz, South Gate Road, Burn Bridge, East Road, Ash Burn,
  Reservoir, Pumping Station, Strathmoor Woods) existem **uma vez**, com
  `source_px` nos dois mapas; a coordenada vem do Mapa A (seção 4.1 regra 2).
- **FRAME_PORTAL**: onde uma via do Mapa A cruza a moldura do Mapa A, um nó
  de moldura é casado com o ponto correspondente da via no Mapa B. É assim
  que Level 1 e Level 2 se conectam sem duplicar estrada.
- **Portas de moldura do Mapa B** são saídas **aparentes** por geometria (a
  via sai do desenho), nunca saídas verdadeiras (seção 20).

### 8.2 Entidades

| Entidade | Prefixo | Seção | Arquivo (seed) |
|---|---|---|---|
| Location | `RM-<ZONA>-<CÓD>` | 12 | `LOCATIONS.seed.yaml` |
| Edge | `EDG-<L>-<nnn>` | 13 | `EDGES.seed.yaml` |
| Road/Trail | `ROAD-*` | 13.4 | `EDGES.seed.yaml` |
| Route | `RTE-<MAPA>-<nome>` | 14 | `ROUTES.seed.yaml` |
| Water feature (linha/polígono) | `WAT-*` | 13.5 | `LOCATIONS.seed.yaml` (tipo RIVER/BURN/LAKE…) |
| Address | `ADR-*` | 15 | `ADDRESSES.seed.yaml` |
| Sightline | `SGT-*` | 16 | `VISIBILITY.seed.yaml` |
| Hideout | `HID-*` | 18 | `HIDEOUTS.seed.yaml` |
| Boundary | `BND-*` | 19 | `BOUNDARIES.seed.yaml` |
| Exit | `EXT-*` | 20 | `BOUNDARIES.seed.yaml` |
| Route mystery | `RMY-*` | 21.3 | `MYSTERIES.seed.yaml` |
| Cartographic mystery | `CMY-*` | 21 | `MYSTERIES.seed.yaml` |
| Register entry | `REG-B-nn[a]` | 21.5 | `MYSTERIES.seed.yaml` |
| Map artifact | `MAP-*` | 22, 33 da missão | `ARTIFACTS.seed.yaml` |
| Historical layer | `LYR-*` | 25 | `LAYERS.seed.yaml` |
| Anomaly | `ANM-*` | Apêndice B | `ANOMALIES.seed.yaml` |
| Illegible glyph | `GLY-*` | Apêndice A | `ANOMALIES.seed.yaml` |
| Unlabeled structure | `UNL-*` | 9.4 | `ANOMALIES.seed.yaml` |
| Transform | `XFM-*` | 7 | `SOURCES.yaml` |
| Staging / Movement / Chase | `STG-*` / `MOV-*` / `CHS-*` | 17.6, 28 | `STAGING.yaml` (runtime) |
| Mutation | `CMUT-*` | 26 | `MUTATIONS` bloco no manifesto |
| Knowledge baseline | — | 23 | `KNOWLEDGE_BASELINE.seed.yaml` |

### 8.3 Zonas de id

| Zona | Uso |
|---|---|
| `CEN` | núcleo urbano em torno da cruz (≤ ~1 km) |
| `URB` | restante do Mapa A (periferia, fazendas, bosques, instalações) |
| `REG` | lugares só do Mapa B |
| `SUB` | subsolo (inset + subsolo declarado) |
| `OFF` | destinos fora das molduras (só alegações de placa) |
| `FRM` | nós de moldura (FRAME_PORTAL) |
| `JCT` | junções sem nome necessárias ao grafo |

O id é **estável**: renomear um lugar muda `names[]`, nunca o id (seção 26).

---

## 9. Urban Graph (LEVEL 1 — Mapa A)

### 9.1 Leitura do mapa

```text
                      N
            Flarry Estate      Shepherd's Bothy ─ ─ R2 ─ ─ Strathmoor Woods ─ ─ ▶ Rowan Cottage
                 │  Old Quarry ─ ─ R3 ─ ─ Sheep Fields ─ ─ Manfred Farm        Ash Burn ╲   Reservoir
 Old Parish ─R1─ Saint Morrow Chapel                                                     ╲  Pumping Station
 Cemetery   ╲    Office of Civic Pres.   Red Stag   General Mercantile                 Burn Bridge ═ East Road ✕ (closed)
             ╲   Civil Archive Hall   SAINT MORROW CROSS (0,0)   Village Clinic
                                       Redmur Constabulary   Old Coach Stop   (+)
          Caretaker House                  │
 Root Cellar Hideout ● Drainage Culvert   South Gate Road (Entrada Principal)   Ruined Tool Shed
                                           ▼ "Para os vales e o resto do mundo"
```

O centro é um **nó radial**: a cruz fica numa praça da qual saem vias para
norte (Red Stag → Sheep Fields → Shepherd's Bothy), oeste (Office of Civic
Preservation → capela → cemitério), leste (Mercantile → Burn Bridge → East
Road), nordeste (Manfred Farm) e sul (South Gate Road, a única via desenhada
como **estrada principal** que chega à moldura sul, com a legenda "PARA OS
VALES E O RESTO DO MUNDO").

### 9.2 Inventário Level 1 (resumo; completo na seção 38)

| id | Nome | Tipo | Grade | RCG (x, y) m | d. cruz | Fonte |
|---|---|---|---|---|---|---|
| `RM-CEN-SMC` | Saint Morrow Cross | LANDMARK | A:D4 | (0, 0) | 0 | A, B |
| `RM-CEN-RSP` | Red Stag Pub | PUB | A:D4 | (158, 263) | 307 | A |
| `RM-CEN-CON` | Redmur Constabulary | POLICE | A:D5 | (381, −255) | 458 | A |
| `RM-CEN-CAH` | Civil Archive Hall | ARCHIVE | A:C5 | (−490, −316) | 583 | A |
| `RM-CEN-OCP` | Office of Civic Preservation | GOVERNMENT_BUILDING | A:B4 | (−672, −53) | 674 | A |
| `RM-CEN-GMC` | General Mercantile | SHOP | A:E4 | (725, 211) | 755 | A |
| `RM-CEN-OCS` | Old Coach Stop | TRANSPORT_STOP | A:D6 | (482, −620) | 785 | A |
| `RM-CEN-CLN` | Village Clinic | CLINIC | A:E5 | (867, −385) | 948 | A |
| `RM-CEN-CHP` | Saint Morrow Chapel | CHAPEL | A:B3 | (−822, 474) | 949 | A, B |
| `RM-URB-OQY` | Old Quarry | QUARRY | A:C3 | (−348, 859) | 927 | A, B |
| `RM-URB-SHF` | Sheep Fields | FIELD (área) | A:D2 | (401, 1081) | 1.153 | A, B |
| `RM-URB-CTH` | Caretaker House | HOUSE | A:B7 | (−774, −1065) | 1.316 | A |
| `RM-URB-OPC` | Old Parish Cemetery | CEMETERY | A:A4 | (−1361, 130) | 1.367 | A, B ("Cemitério Antigo") |
| `RM-URB-MNF` | Manfred Farm | FARM | A:E2 | (1089, 940) | 1.439 | A, B |
| `RM-URB-FLE` | Flarry Estate | ESTATE | A:B2 | (−1065, 1183) | 1.592 | A, B |
| `RM-URB-DCU` | Drainage Culvert | CULVERT | A:B7 | (−660, −1450) | 1.593 | A |
| `RM-URB-SBO` | Shepherd's Bothy | BOTHY | A:D1 | (441, 1567) | 1.628 | A, B |
| `RM-URB-RTS` | Ruined Tool Shed | RUIN | A:E7 | (867, −1430) | 1.672 | A |
| `RM-URB-RCH` | Root Cellar Hideout | CELLAR | A:A7 | (−1280, −1349) | 1.859 | A |
| `RM-URB-BBR` | Burn Bridge | BRIDGE | A:H4 | (2547, 150) | 2.552 | A, B |
| `RM-URB-ROW` | Rowan Cottage | COTTAGE | A:G2 | (2345, 1235) | 2.650 | A, B |
| `RM-URB-PMP` | Pumping Station | UTILITY | A:H3 | (2973, 413) | 3.001 | A, B |
| `RM-URB-ERC` | East Road — ponto de bloqueio (X) | ROADBLOCK | A:H4 | (3074, 81) | 3.075 | A, B |
| `RM-URB-RSV` | Reservoir | RESERVOIR (área) | A:H3 | (3033, 676) | 3.108 | A, B |
| `RM-URB-SWD` | Strathmoor Woods | FOREST (área) | A:E1–G2 | rótulo (1839, 1596) | — | A, B |
| `WAT-ASH` | Ash Burn | BURN (linha) | A:G2→H4→H5 | de (1839, 1142) a (2750, −174) | — | A, B |
| `ROAD-SGR` | South Gate Road — Entrada Principal | ROAD | A:D5–D7 | rótulo (219, −1430); moldura (251, −1855) | — | A, B |
| `ROAD-EAST` | East Road — Officially Closed | ROAD | A:H4 | trecho a leste de Burn Bridge até a moldura | — | A, B |

Precisão: `position_accuracy_m: 60` (ícone) ou `150` (área).

### 9.3 Lugares declarados pela missão e ausentes dos mapas

| id | Nome | Situação | Tratamento |
|---|---|---|---|
| `RM-SUB-BTF` | Black Thistle Filling Station | **não aparece** nos mapas: fica no **subterrâneo** (decisão da autora), fora do inset | `layer: SUBTERRANEAN`, `source: AUTHOR_DECLARED`, `coordinates: null`, `connectivity: UNDECLARED`, **sem arestas**; ver 11.6. Nenhuma edificação de superfície é atribuída a ele |
| `RM-SUB-SC4` | Sealed Crypt IV | **não aparece** no inset: fica no **subterrâneo** (decisão da autora) | `layer: SUBTERRANEAN`, `source: AUTHOR_DECLARED`, `type: CRYPT`, `status: SEALED` (pelo nome), `connectivity: UNDECLARED`; ver 11.6. Ligação ao Old Parish Cemetery **não assumida** |

### 9.4 Estruturas sem rótulo (não são lugares canônicos)

| id | Posição (A px → RCG) | Descrição | Observação |
|---|---|---|---|
| `UNL-A-01` | (770, 720) → (1008, −782) | pequena edificação com **"+" branco** a sudeste do Old Coach Stop, entre campos lavrados | o "+" lembra o símbolo da legenda "Túmulo/Cripta" (que é †), mas não é idêntico → significado `UNKNOWN`. **Não** é atribuído a Sealed Crypt IV |
| `UNL-A-02` | (298, 708) → (−903, −733) | casa isolada a oeste da trilha para Caretaker House | — |
| `UNL-A-03` | (957, 393) → (1766, 543) | casa isolada entre Manfred Farm e Ash Burn | — |
| `UNL-A-04` | (530, 686) → (36, −644) | edificação baixa junto à South Gate Road | — |

Regra: um `UNL-*` só vira lugar por proposta (`INV-C09`). Ele existe no grafo
**como obstáculo/cobertura** (é físico), não como destino nomeável.

### 9.5 Textos, figuras e ornamentos do Mapa A (artefatos, não fatos)

| id | Conteúdo | Posição |
|---|---|---|
| `MAP-A-TXT-01` | "Algumas verdades sempre encontram um caminho de volta." | margem oeste |
| `MAP-A-TXT-02` | "O que é escondido também pertence a Redmur." | margem nordeste |
| `MAP-A-TXT-03` | "Montanhas guardam segredos. Redmur os preserva." | rodapé |
| `MAP-A-TXT-04` | "Lugares também guardam memórias." | margem leste |
| `MAP-A-TXT-05` | "Redmur sempre observa." | canto sudeste |
| `MAP-A-TXT-06` | "Disciplina. Memória. Preservação." | rodapé |
| `MAP-A-TXT-07` | "District of Civic Preservation — Scottish Interior" | subtítulo |
| `MAP-A-TXT-08` | "Para os vales e o resto do mundo" (seta para sul na South Gate Road) | moldura sul |
| `MAP-A-FIG-01` | figura humana escura na via, logo abaixo de "(0,0)" | px (527, 603) |
| `MAP-A-FIG-02` | figura encapuzada caminhando na South Gate Road | px (579, 763) |
| `MAP-A-ORN-*` | rosas, serpente (oeste), caveira (inset), rosa-dos-ventos com rosa | molduras |

Figuras e ornamentos: `cartographic_meaning: NONE_ASSUMED`. Estão registrados
porque a missão proíbe tratar elementos do mapa como "meramente decorativos";
registrá-los **não** os promove a pista.

---

## 10. Regional Graph (LEVEL 2 — Mapa B)

### 10.1 Leitura do mapa

O Mapa B coloca Redmur ("REDMUR" + Saint Morrow Cross) no centro de uma malha
de estradas principais, secundárias e trilhas que ligam cerca de 30
localidades, cercada ao norte por uma cordilheira (Ben Ràth, 714 m, a
noroeste), com três lagos (Lago Negro/Loch Draven ao norte, Loch Calder a
sudoeste, Loch Ainslie a sudeste), dois pântanos (Harrowmire a noroeste,
Torran Mire a sudeste) e o Ash Burn a leste. Sete marcadores de rota
contestada (`R1 R2 R3 R4 R7 R13 R17`) são listados numa legenda própria;
seis placas apontam para destinos fora da moldura.

### 10.2 Tipos (missão §8, §9)

O tipo vem do **ícone** (legenda do Mapa B: vilarejo/localidade, ruínas,
capela/igreja, casa isolada, ponte, moinho, pedra erguida/marcos, cemitério,
construção notável) e do **nome**; quando os dois divergem ou são fracos,
`type_confidence: LOW`.

### 10.3 Inventário Level 2 (resumo; completo na seção 38)

Coordenadas derivadas da escala decidida (seção 7.4: Mapa B = 55,86 m/px), `coordinate_status: CANONICAL`, `position_accuracy_m: 840` (±15 px).
Confiança do tipo: H alta, M média, L baixa.

| id | Nome no mapa | Tipo (conf.) | Reg. | Grade | RCG (x, y) m | d. cruz |
|---|---|---|---|---|---|---|
| `RM-REG-CRV` | Cairnvale | VILLAGE (M) | 14 | B:F8 | (−9385, −6145) | 11.218 |
| `RM-REG-CRH` | Carriden Hamlet | HAMLET (H) | 24 | B:H8 | (11843, −6145) | 13.342 |
| `RM-REG-OML` | Old Mill (em ruínas) | MILL · RUINED (H) | 30 | B:G9 | (4692, −14524) | 15.263 |
| `RM-REG-LDR` | Lago Negro (Loch Draven) | LAKE (H) | — | B:G3 | (3463, 15753) | 16.129 |
| `RM-REG-CRE` | Corrie's End | VILLAGE (L) | 09 | B:D5 | (−13295, 9776) | 16.502 |
| `RM-REG-CRB` | Creggan Bothy | BOTHY (H) | 07 | B:E3 | (−4748, 16759) | 17.418 |
| `RM-REG-GRF` | Grayfen | HAMLET (L) | 15 | B:F10 | (−4637, −17038) | 17.658 |
| `RM-REG-BTC` | Blackthorn Cottage | COTTAGE (H) | 25 | B:J7 | (17988, −2234) | 18.126 |
| `RM-REG-STW` | Stonewell | HAMLET (L) | 13 | B:D9 | (−16647, −9217) | 19.028 |
| `RM-REG-MFF` | Muirfield Farm | FARM (H) | **—** | B:C6 | (−20669, 2793) | 20.857 |
| `RM-REG-MCR` | Moor Cairn | STANDING_STONES (H) | 20 | B:D3 | (−15809, 14803) | 21.658 |
| `RM-REG-RVH` | Raven's Holt | HAMLET (M) | 29 | B:H10 | (11843, −18155) | 21.676 |
| `RM-REG-BRF` | Blackridge Farm | FARM (H) | 08 | B:C5 | (−20837, 7262) | 22.066 |
| `RM-REG-SBA` | Abadia em Ruínas de Saint Bride | ABBEY · RUIN (H) | 19 | B:C8 | (−21954, −5028) | 22.522 |
| `RM-REG-GLN` | Glenath | VILLAGE (M) | 05ᵇ | B:H2 | (12122, 18993) | 22.532 |
| `RM-REG-WLF` | Willowford | VILLAGE (H) | 26 | B:K9 | (21339, −9497) | 23.357 |
| `RM-REG-CRG` | Craigness | VILLAGE (H) | 18 | B:B8 | (−26143, −6145) | 26.856 |
| `RM-REG-THB` | Thistlebank | HAMLET (M) | 16 | B:C10 | (−21004, −16759) | 26.871 |
| `RM-REG-FSG` | Fenside Grange | FARM (M) | 27 | B:L8 | (26646, −5307) | 27.170 |
| `RM-REG-MSG` | Mossgate | VILLAGE (M) | 28 | B:K10 | (21898, −16479) | 27.406 |
| `RM-REG-BRT` | Ben Ràth (714 m) | MOUNTAIN (H) | 21 | B:C3 | (−21674, 17038) | 27.569 |
| `RM-REG-HRW` | Harrowmire (charco) | MARSH (H) | 12 | B:A4 | (−25585, 10893) | 27.807 |
| `RM-REG-LCD` | Loch Calder | LAKE (H) | — | B:B10 | (−24914, −12848) | 28.032 |
| `RM-REG-KRK` | Kirkhollow | VILLAGE (H) | 10 | B:B6 | (−27819, 4748) | 28.222 |
| `RM-REG-LAN` | Loch Ainslie | LAKE (H) | — | B:L9 | (26646, −9497) | 28.288 |
| `RM-REG-ELG` | Elderglen | HAMLET (L) | 11 | B:B7 | (−29495, −559) | 29.500 |
| `RM-REG-TRM` | Torran Mire (pântano) | MARSH (H) | — | B:L10 | (28043, −14245) | 31.453 |
| `RM-REG-KLB` | Ruínas de Kellburne | RUIN (H) | 22 | B:K2 | (26646, 20110) | 33.383 |
| `RM-REG-RDM` | Redmur | TOWN (agregado) | 01 | B:G6 | região-pai de `RM-CEN-*` | — |
| — | Saint Morrow | — | 02 | — | **sem rótulo próprio** no Mapa B | — |
| — | Letham | — | 17 | — | **não localizado** | — |
| — | Passo de Muirchéin | — | 23 | — | **não localizado** | — |

Notas:

- `05ᵇ`: o registro atribui **05** a Rowan Cottage **e** a Glenath; não há 06
  (`ANM-B-01`). O índice exibido é preservado literalmente (seção 21.5).
- Muirfield Farm está no mapa e **não** está no registro (`ANM-B-02`).
- Saint Morrow (02) não tem rótulo isolado: o mapa tem "Saint Morrow Chapel" e
  "Saint Morrow Cross". O registro **não** é casado com nenhum dos dois
  (`register_entry.location_id: null`, `candidates: [RM-CEN-CHP, RM-CEN-SMC]`,
  `OQ-CART-07`).
- Letham e Passo de Muirchéin viram entradas de registro sem lugar
  (`placement: NOT_ON_MAP`). Nenhuma montanha, passagem ou estrada é
  atribuída a "Muirchéin" por semelhança de forma.
- Estruturas sem rótulo relevantes do Mapa B: `UNL-B-01` pequeno lago a sul de
  Carriden Hamlet; `UNL-B-02` cordilheira norte sem nome; `UNL-B-03`
  **triângulo branco** junto à capela/cemitério — símbolo **ausente da
  legenda** (`ANM-B-11`).

### 10.4 Destinos fora da moldura (placas)

| id | Placa | Distância alegada | Onde a via toca a moldura | Anomalias |
|---|---|---|---|---|
| `RM-OFF-CLR` | "Para Caelrith? (32 milhas)" | 32 mi | NE, após "Estrada 13 Em Disputa" | o **"?" faz parte da placa** (`ANM-B-05`); grafia Caelrith/Coelrith incerta |
| `RM-OFF-DNS` | "Para Dunsgate (17 milhas)" | 17 mi | O, em linha pontilhada branca (trilha ou limite incerto — símbolo ambíguo) | — |
| `RM-OFF-WSH` | "Para Westhaven (29 milhas)" | 29 mi | SO, junto a Loch Calder | grafia **Westhaven/Weathoven** incerta (`ANM-B-08`) |
| `RM-OFF-INV` | "Para Inverloch (?7 milhas)" | 77? mi | SO, abaixo de Thistlebank | dígito inicial ilegível (`ANM-B-07`) |
| `RM-OFF-ELD` | "Para Eldham (41 milhas)" **×2** | 41 mi e 41 mi | SE: (a) estrada a leste de R13; (b) trilha vermelha ao sul de Mossgate | **mesmo destino e mesma distância em duas vias diferentes** (`ANM-B-04`) |

As distâncias em milhas são `OFFICIAL_CLAIM` de placa (o Mapa B usa km na
barra: `ANM-B-06`) e **nunca** entram no cálculo físico. O destino é `OFF_MAP`:
a cartografia não sabe se a via chega lá.

### 10.5 Textos do Mapa B (artefatos)

| id | Texto |
|---|---|
| `MAP-B-TXT-01` | "Mesmos caminhos, outros rostos." |
| `MAP-B-TXT-02` | "Não há fronteiras, apenas mais estradas." |
| `MAP-B-TXT-03` | "O que parece saída pode ser apenas outra entrada." |
| `MAP-B-TXT-04` | "Os vales guardam segredos. Redmur é apenas o centro. — E talvez não seja o fim." |
| `MAP-B-TXT-05` | "Nem todo nome no mapa é um lugar. Alguns são avisos." (rodapé do registro) |
| `MAP-B-TXT-06` | "Todo mapa mente um pouco." (rodapé das rotas contestadas) |
| `MAP-B-TXT-07` | "Lugares também guardam memórias." |
| `MAP-B-TXT-08` | "Redmur sempre observa." (renderizado corrompido: `ANM-B-12`) |
| `MAP-B-TXT-09` | "Disciplina. Memória. Preservação." |
| `MAP-B-TXT-10` | "Registro dos Vilarejos (e não apenas deles)" |
| `MAP-B-TXT-11` | "Estrada 13 Em Disputa" (rótulo de via, NE) |

`MAP-B-TXT-06` é a única frase dos mapas que **se refere ao próprio mapa**.
Ela é registrada como alegação de artefato; **não** autoriza o motor a tratar
qualquer dado do mapa como falso (isso exigiria `truth_ref`).

---

## 11. Underground Graph (LEVEL 3)

### 11.1 Leitura do inset "REDE SUBTERRÂNEA"

O inset é um **diagrama esquemático** (não uma planta): oito entradas
desenhadas como arcos/portas, ligadas por linha vermelha pontilhada — símbolo
de **"Passagem oculta"** na legenda do Mapa A. Topologia lida (Apêndice A.3):

```text
Cemetery Crypt Tunnel ⊤─◀─┐                 Chapel Basement
                          └──────── J1 ◀────────┘
                                    │▼
Root Cellar Passage ⊤─◀────── Storm Drains ──────── J2 ────●  Pumping Station Channel ⊤──┐
        │                                            │                                     │
        ⊤ (+)                                        + (+)                          Quarry Crawlspace ⊤
        │                                            │
Culvert Exit ────────(+)──────────────────────────── J3 ────●  Reservoir Overflow Tunnel
```

| Aresta | De | Para | Glifos desenhados |
|---|---|---|---|
| `EDG-S-001` | `RM-SUB-CHB` Chapel Basement | `RM-JCT-S1` | — |
| `EDG-S-002` | `RM-JCT-S1` | `RM-SUB-CCT` Cemetery Crypt Tunnel | ponta de seta apontando ao túnel; `⊤` no fim |
| `EDG-S-003` | `RM-JCT-S1` | `RM-SUB-STD` Storm Drains | ponta de seta apontando aos drenos |
| `EDG-S-004` | `RM-SUB-STD` | `RM-SUB-RCP` Root Cellar Passage | ponta de seta apontando ao Root Cellar; `⊤` no fim |
| `EDG-S-005` | `RM-SUB-STD` | `RM-JCT-S2` | — |
| `EDG-S-006` | `RM-JCT-S2` | `RM-SUB-PSC` Pumping Station Channel | `●` no fim |
| `EDG-S-007` | `RM-SUB-PSC` | `RM-SUB-QCS` Quarry Crawlspace | `⊤` nas duas pontas |
| `EDG-S-008` | `RM-JCT-S2` | `RM-JCT-S3` | marcas `+` ao longo |
| `EDG-S-009` | `RM-JCT-S3` | `RM-SUB-ROT` Reservoir Overflow Tunnel | `●` no fim |
| `EDG-S-010` | `RM-JCT-S3` | `RM-SUB-CUX` Culvert Exit | marca `+` |
| `EDG-S-011` | `RM-SUB-RCP` | `RM-SUB-CUX` | `⊤` e `+` |

**Glifos do inset** (`⊤`, `●`, `+`, pontas de seta) **não estão na legenda**.
Ficam em `MAP-A-INSET-GLYPHS` com `meaning: UNKNOWN`. Em especial: **ponta de
seta não é direcionalidade**. Toda aresta subterrânea nasce
`directionality: BOTH` até decisão (`OQ-CART-08`); a seta desenhada fica como
anotação (`drawn_arrow: TOWARD_B`), útil ao mistério e inerte à física.

Não há, no inset, **aresta direta capela ↔ cemitério**: a ligação passa pela
junção `RM-JCT-S1`. "Existe passagem subterrânea entre a capela e o
cemitério?" → **sim, via J1, duas arestas** (Apêndice C, pergunta 3).

### 11.2 Âncoras de superfície (portais)

| Nó subterrâneo | Portal para | Casamento | Confiança |
|---|---|---|---|
| `RM-SUB-CHB` Chapel Basement | `RM-CEN-CHP` Saint Morrow Chapel | nome | HIGH |
| `RM-SUB-CCT` Cemetery Crypt Tunnel | `RM-URB-OPC` Old Parish Cemetery | nome | HIGH |
| `RM-SUB-QCS` Quarry Crawlspace | `RM-URB-OQY` Old Quarry | nome | HIGH — mas ver `ANM-A-03` |
| `RM-SUB-RCP` Root Cellar Passage | `RM-URB-RCH` Root Cellar Hideout | nome | HIGH |
| `RM-SUB-PSC` Pumping Station Channel | `RM-URB-PMP` Pumping Station | nome | HIGH |
| `RM-SUB-ROT` Reservoir Overflow Tunnel | `RM-URB-RSV` Reservoir | nome | HIGH |
| `RM-SUB-CUX` Culvert Exit | `RM-URB-DCU` Drainage Culvert | nome parcial ("culvert") | **MEDIUM** (`OQ-CART-09`) |
| `RM-SUB-STD` Storm Drains | — | **nenhum acesso de superfície desenhado** | posição `UNKNOWN` |
| `RM-JCT-S1..S3` | — | junções do diagrama | posição `UNKNOWN` |

A posição (x, y) de um nó subterrâneo ancorado = a do portal; `z` =
`UNKNOWN` (`depth_class: UNKNOWN`). O ponto exato da entrada **dentro** do
lugar de superfície (qual cripta, qual porta do porão) é `UNKNOWN`.

### 11.3 Atributos por nó subterrâneo (missão §6)

Cada nó e aresta `SUB` tem **todos** os campos pedidos. Nenhum valor que o
mapa não mostra é inventado: ele nasce `UNSPECIFIED` e o validador aplica
limites conservadores (11.4).

```yaml
- id: RM-SUB-CCT
  canonical_name: Cemetery Crypt Tunnel
  type: TUNNEL
  layer: SUBTERRANEAN
  portals: [{edge: EDG-P-002, surface: RM-URB-OPC, entry_point: UNKNOWN}]
  entries: [EDG-P-002, EDG-S-002]      # projetado das arestas; nunca lista manual divergente
  exits:   [EDG-P-002, EDG-S-002]
  direction: UNSPECIFIED               # orientação física do túnel
  length_m: UNSPECIFIED                # piso físico: ver 11.4
  width_m: UNSPECIFIED
  max_passage: UNSPECIFIED             # ADULT_UPRIGHT | ADULT_STOOPED | ADULT_CRAWL | CHILD_ONLY | UNSPECIFIED
  depth_class: UNKNOWN                 # SHALLOW | MEDIUM | DEEP | UNKNOWN
  risk: UNSPECIFIED                    # LOW | MEDIUM | HIGH | LETHAL | UNSPECIFIED
  visibility: UNDERGROUND              # sempre: invisível da superfície (VS-02)
  lighting: UNSPECIFIED
  environment: {water: UNSPECIFIED, air: UNSPECIFIED, sound_carry: UNSPECIFIED}
  restrictions: UNSPECIFIED
  blockable: UNSPECIFIED               # porta, grade, entulho?
  chase_viable: UNSPECIFIED
  known_connections: [RM-JCT-S1]       # projetado do inset
  secret_connections: []               # só por proposta; hoje nenhuma além do inset
  discovery_requirement: UNSPECIFIED   # o que é preciso saber/ter para achar a entrada
  secret_level: HIDDEN                 # legenda do Mapa A: "Passagem oculta"
  status: UNKNOWN                      # ativo? selado? inundado? — não mostrado
  source: {map: SRC-MAP-A, inset: true, px: [965, 668]}
```

### 11.4 Física mínima do subsolo sem inventar medidas

| Regra | Efeito |
|---|---|
| **Comprimento mínimo = distância entre âncoras** | `length_m ≥ euclid(portal_A, portal_B)` para todo caminho subterrâneo entre dois portais; declarar menos é `TUNNEL_SHORTER_THAN_ANCHORS` (FAIL) |
| Caminho que só existe por junções sem posição | o comprimento mínimo do **caminho inteiro** ≥ distância entre os portais extremos |
| `max_passage: UNSPECIFIED` | tempo **mínimo** a passo de caminhada; tempo **esperado** a passo agachado (0,7 m/s) com `WARNING SUBTERRANEAN_DIMENSIONS_UNSPECIFIED` |
| `status: UNKNOWN` | aresta utilizável no planejamento, mas cada uso gera `WARNING SUBTERRANEAN_STATE_UNSPECIFIED` até a autora declarar |
| Nó sem portal (Storm Drains, junções) | alcançável só por arestas; nunca é ponto de entrada/saída de cena |

Consequência já visível: **Quarry Crawlspace ↔ Pumping Station Channel** tem
comprimento mínimo de **≈ 3,35 km** (âncoras em (−348, 859) e (2973, 413)),
embora o inset os desenhe lado a lado (`ANM-A-03`). O motor não "corrige" o
inset nem rebaixa a ligação: registra o piso físico. Se a autora pretende um
crawlspace **diferente** do Old Quarry, isso é proposta, não inferência
(`OQ-CART-09`).

Pisos físicos de alguns pares de portais (distância entre âncoras; o
comprimento real só pode ser maior):

| Par | Caminho no inset | Piso físico |
|---|---|---|
| Chapel Basement → Cemetery Crypt Tunnel | S-001, S-002 | ≈ 640 m |
| Chapel Basement → Culvert Exit | S-001, S-003, S-005, S-008, S-010 **ou** S-001, S-003, S-004, S-011 | ≈ 1.930 m |
| Root Cellar Passage → Culvert Exit | S-011 | ≈ 630 m |
| Pumping Station Channel → Reservoir Overflow Tunnel | S-006, S-008, S-009 | ≈ 270 m |

### 11.5 Portais

Portais são arestas `edge_type: PORTAL` (superfície ↔ subsolo) com
`vertical_delay_s` (`UNSPECIFIED` → proposta: 60 s mínimo / 120 s esperado),
`public_knowledge`, `secret_level`, `access_requirement` e estado próprio (uma
cripta pode estar selada mesmo que o túnel esteja aberto).

| Portal | Superfície | Subsolo | `secret_level` inicial |
|---|---|---|---|
| `EDG-P-001` | Saint Morrow Chapel | Chapel Basement | `HIDDEN` para a passagem; o porão em si pode ser conhecido (`OQ-CART-11`) |
| `EDG-P-002` | Old Parish Cemetery | Cemetery Crypt Tunnel | `HIDDEN` |
| `EDG-P-003` | Old Quarry | Quarry Crawlspace | `HIDDEN` |
| `EDG-P-004` | Root Cellar Hideout | Root Cellar Passage | `HIDDEN` |
| `EDG-P-005` | Pumping Station | Pumping Station Channel | `UNKNOWN` (instalação: provavelmente restrita, não necessariamente oculta) |
| `EDG-P-006` | Reservoir | Reservoir Overflow Tunnel | `UNKNOWN` |
| `EDG-P-007` | Drainage Culvert | Culvert Exit | `NONE` na boca (o bueiro com grade é desenhado na superfície); a ligação com a rede é `HIDDEN` |

### 11.6 Nós subterrâneos fora do inset (decisão da autora, 2026-09-19)

**Black Thistle Filling Station** e **Sealed Crypt IV** não aparecem nos mapas
porque **ficam no subterrâneo**. Como o inset "REDE SUBTERRÂNEA" também não os
desenha, a decisão tem uma consequência física que o motor registra e **não
interpreta**:

- o inset impresso **não é a representação completa** do subsolo
  (`MAP-DIEGETIC-A` `OMITS` `RM-SUB-BTF` e `RM-SUB-SC4`). Se a omissão é
  deliberada, descuido ou desconhecimento do autor do mapa é `MYSTERY` ligado
  à autoria (22.7);
- ambos nascem `layer: SUBTERRANEAN`, `first_allowed_reveal` posterior ao
  capítulo 0 (o leitor **não** os vê no mapa impresso; estado de leitor
  `UNSEEN`), `epistemic_status: FACT` para a existência e a localização
  subterrânea, `UNKNOWN` para todo o resto;
- `connectivity: UNDECLARED`: nenhum portal, aresta ou junção é assumido.
  Não se liga a nenhum nó do inset por proximidade nem por nome (Sealed Crypt
  IV **não** é assumida sob o Old Parish Cemetery; o posto **não** é assumido
  sob nenhum edifício de superfície).

```yaml
- id: RM-SUB-SC4
  canonical_name: Sealed Crypt IV
  layer: SUBTERRANEAN
  type: CRYPT
  status: SEALED                     # pelo nome; confirmar por proposta
  source: AUTHOR_DECLARED
  coordinates: null
  connectivity: UNDECLARED           # UNDECLARED | DECLARED (com portal/aresta aprovados)
  depicted_by: []                    # nenhum mapa os desenha
  omitted_by: [MAP-DIEGETIC-A]       # relação OMITS
  first_allowed_reveal: {after_chapter: 0}
```

Regras:

- `CX-02` (subterrâneo sem portal) **não** reprova nó com `connectivity:
  UNDECLARED` — reprovaria por INV-C03. Em contrapartida, o nó fica **inerte**:
  não pode ser origem, destino ou parada de staging, movimento ou perseguição
  (`TR-06`); `reachable` para ele responde `UNDECLARED_CONNECTIVITY`, não
  "não" e não "sim". Quando a autora declarar como se entra (entrada, corredor,
  junção, distância), a conectividade passa a `DECLARED` por proposta e o nó
  vira navegável, com o piso físico de 11.4.
- A relação com `Sealed Crypt IV` ser "IV" (numeração) **não** cria as
  criptas I–III: só uma proposta as cria.
- `MYSTERY`: nenhum. A existência é fato; o que há neles, quem os usa e como se
  chega a eles pertence ao canon da história.

---

## 12. Location Schema

### 12.1 Contrato

Todos os campos pedidos pela missão (§10) estão presentes; os marcados
**projetado** não são armazenados, são calculados (princípio do motor:
"guarda-se o mínimo declarado; tudo que é derivável é projetado").

```yaml
- id: RM-URB-BBR                       # location_id — estável, nunca reutilizado
  canonical_name: Burn Bridge
  names:                               # aliases e nomenclatura (12.3)
    - {name: Burn Bridge, kind: MAP_A_LABEL, source: SRC-MAP-A}
    - {name: Burn Bridge, kind: MAP_B_LABEL, source: SRC-MAP-B}
  type: BRIDGE                         # vocabulário 12.2
  type_confidence: HIGH
  geometry: POINT                      # POINT | AREA | LINE
  layer: URBAN                         # map_layer: URBAN | REGIONAL | SUBTERRANEAN
  source_px:                           # proveniência — a coordenada é DERIVADA disto
    - {source: SRC-MAP-A, px: [1150, 490], anchor: ICON}
    - {source: SRC-MAP-B, px: [985, 512], anchor: ICON}
  coordinates: {x: 2547, y: 150, z: null}      # projetado de source_px + XFM; cacheado no runtime
  position_accuracy_m: 60
  coordinate_status: CANONICAL                  # CANONICAL | PROVISIONAL | UNKNOWN
  map_grid_reference: [A:H4, B:I6]              # rótulo, não métrica
  parent_region: RM-REG-RDM
  elevation: {z_rel: null, elevation_asl: null, z_hint: null}
  terrain: RIVER_CROSSING
  crosses: [WAT-ASH]                   # BRIDGE/FORD/CULVERT/TUNNEL: qual água atravessa
  # adjacent_locations, roads, trails, subterranean_links, visible_connections,
  # hidden_connections, distance_from_redmur_center → PROJETADOS de edges[] e coordinates
  access:
    public_access: UNKNOWN             # YES | NO | CONDITIONAL | UNKNOWN
    restricted_access: UNKNOWN
    access_conditions: []
    opening_hours: null                # só se canônico
    vehicle_access: UNKNOWN            # estrada principal desenhada → PROBABLE; proposta confirma
    foot_access: YES
  surveillance: UNKNOWN                # NONE | PATROLLED | WATCHED | POSTED | UNKNOWN
  population: null                     # só se canônico
  occupancy: UNKNOWN                   # INHABITED | WORKPLACE | ABANDONED | SEASONAL | UNKNOWN
  cover_level: LOW                     # NONE | LOW | MEDIUM | HIGH (proteção contra visão)
  concealment_level: LOW               # facilidade de se esconder NO lugar
  escape_potential: null               # projetado (grau, portais, rotas conhecidas)
  pursuit_difficulty: null             # projetado (ponte = gargalo, seção 28)
  weather_sensitivity: []              # só se canônico (ex.: FLOODS_IN_SPATE)
  knowledge:
    known_by_public: YES               # lugar desenhado com rótulo em mapa de aparência pública
    known_by_authorities: YES
    known_by_specific_characters: []   # projetado de KNOWLEDGE_BASELINE + ledger
  significance:
    historical: []                     # ids de claims/camadas — nunca texto de verdade
    mystery: []                        # RMY-*/CMY-* SÓ por vínculo aprovado, nunca por semelhança
  clue_ids: []                         # EVD-* do canon interpretativo
  canon_dependencies: []               # WR-*, GT-*, INST-*
  scene_dependencies: []               # projetado de STAGING
  first_allowed_reveal: OPEN           # OPEN | {chapter: N} | {event: EV-*} | NEVER
  reader_visibility_state: null        # projetado (22.3)
  status: ACTIVE                       # ACTIVE | ABANDONED | RUINED | SEALED | RESTRICTED | DISPUTED | UNKNOWN
  status_source: MAP_GEOMETRY
  valid_from: null                     # histórico (ano do mundo); null = desconhecido
  valid_until: null
  epistemic_status: FACT
```

### 12.2 Vocabulário de tipo

Base (missão §9): `TOWN VILLAGE HAMLET ESTATE FARM COTTAGE HOUSE BOTHY CHAPEL
CEMETERY CRYPT PUB SHOP GOVERNMENT_BUILDING ARCHIVE CLINIC POLICE ROAD TRAIL
BRIDGE FOREST MOOR FIELD QUARRY RIVER BURN LAKE RESERVOIR MARSH RUIN TUNNEL
CULVERT STORM_DRAIN CELLAR SUBTERRANEAN_PASSAGE BOUNDARY ROADBLOCK OUTPOST
UNKNOWN`.

Extensões v1 — cada uma exigida por um elemento real dos mapas:

| Extensão | Elemento que a exige |
|---|---|
| `LANDMARK` | Saint Morrow Cross (monumento em praça) |
| `TRANSPORT_STOP` | Old Coach Stop |
| `UTILITY` | Pumping Station |
| `MOUNTAIN` | Ben Ràth (714 m), cordilheira norte |
| `STANDING_STONES` | Moor Cairn (legenda: "Pedra erguida / marcos") |
| `MILL` | Old Mill (legenda: "Moinho") |
| `ABBEY` | Abadia em Ruínas de Saint Bride (com `RUIN`) |
| `JUNCTION` | junções do grafo (`RM-JCT-*`) |
| `FRAME_PORTAL` | pontos onde vias cruzam a moldura (`RM-FRM-*`) |
| `OFF_MAP_DESTINATION` | destinos de placa (`RM-OFF-*`) |

Regras: `type` pode ser lista quando o mapa sobrepõe (Abadia = `[ABBEY,
RUIN]`; Old Mill = `[MILL]` + `status: RUINED`). Tipo novo = entrada em
`type_extensions[]` com `justified_by` (id de elemento de fonte ou proposta)
e aprovação; tipo fora do vocabulário reprova (`UNKNOWN_TYPE`). "Hideout"
**não** é tipo: é papel registrado em `HID-*` sobre um lugar (seção 18).

### 12.3 Nomenclatura (missão §26)

```yaml
names:
  - {name: Old Parish Cemetery, kind: MAP_A_LABEL,  source: SRC-MAP-A, lang: en}
  - {name: Cemitério Antigo,    kind: MAP_B_LABEL,  source: SRC-MAP-B, lang: pt}
  # kinds: CANONICAL | MAP_A_LABEL | MAP_B_LABEL | REGISTER | HISTORICAL | COLLOQUIAL
  #        | GOVERNMENT | ARCHIVE | SECRET | PTBR_DISPLAY
  # opcionais: valid_from, valid_until, known_by: [CHR-*|INST-*|PUBLIC], epistemic_status
```

- `canonical_name` é **um** dos `names[]`, escolhido por aprovação; mudar é
  mutação (`RENAME_WITHOUT_PROPOSAL`).
- `NAME_COLLISION` (BLOCKER): o mesmo nome normalizado em dois lugares
  diferentes, salvo `shared_name_ok` aprovado.
- **Língua dos nomes** (`OQ-CART-06`): o Mapa A rotula em inglês; o Mapa B
  mistura inglês, gaélico e português ("Cemitério Antigo", "Lago Negro",
  "Ruínas de Kellburne", "Passo de Muirchéin"). O motor guarda todos; qual
  forma a prosa PT-BR usa é decisão editorial.
- A identidade **Old Parish Cemetery = Cemitério Antigo** é aceita por
  posição relativa e tipo (confiança HIGH), mas registrada como casamento de
  nomes (`ANM-X-03`), não como fato de que "antigo" e "paroquial" sejam o
  mesmo título oficial.
- O exemplo da missão ("East Road" / "Dead Road" / "Eastern Civic Route 13")
  é **conceitual**: nenhum desses aliases está nas fontes. Em particular,
  **"Estrada 13 Em Disputa" (NE do Mapa B) não é ligada à East Road**
  (geometrias diferentes). Ligá-las seria resolver enigma.

---

## 13. Edge Schema

### 13.1 Contrato

```yaml
- id: EDG-U-041
  from: RM-URB-BBR
  to: RM-URB-ERC
  edge_type: ROAD            # ROAD | TRAIL | FOREST_PATH | TUNNEL | DRAIN | SECRET_PASSAGE | BRIDGE
                             # | WATER_ROUTE | SERVICE_ROUTE | PORTAL | FRAME_LINK | OPEN_GROUND
  road: ROAD-EAST            # entidade nomeada, se houver
  road_class: MAIN           # MAIN | SECONDARY | TRAIL | PATH | NONE (legenda do mapa)
  directionality: BOTH       # BOTH | A_TO_B | B_TO_A — só por fato físico (desnível, porta de um lado só)
  drawn_arrow: null          # anotação do mapa; não afeta física
  source_polyline_px: {source: SRC-MAP-A, points: [[1150,490],[1210,500],[1280,507]]}
  distance_meters:
    nominal: 540             # comprimento da polilinha em RCG
    min: 500                 # nunca < euclid(from, to) − precisões
    basis: DIGITIZED         # DIGITIZED | EUCLID_TORTUOSITY | DECLARED | UNSPECIFIED
  estimated_times: null      # PROJETADO pela seção 17 (walk/run/vehicle/crawl); nunca armazenado
  terrain: ROAD_SURFACE      # ROAD_SURFACE | TRACK | FOREST_FLOOR | FIELD | MARSH | TUNNEL_FLOOR
                             # | DRAIN_CHANNEL | CRAWLSPACE | ROCK | STAIRS
  crossings: []              # [{water: WAT-ASH, via: RM-URB-BBR}]
  visibility: OPEN           # OPEN | PARTIAL | HIDDEN | UNDERGROUND
  cover: LOW                 # NONE | LOW | MEDIUM | HIGH
  noise: UNSPECIFIED         # QUIET | NORMAL | LOUD | UNSPECIFIED
  risk: UNSPECIFIED
  access_requirement: null   # null | KEY | PERMIT | CLIMB | SWIM | FORCE | KNOWLEDGE
  state_timeline:            # estado físico por capítulo (seção 24); fold de mutations[]
    - {from_chapter: 0, state: OPEN}
  blocked_state: null        # PROJETADO de state_timeline no capítulo da consulta
  seasonal_state: []         # [{season: WINTER, effect: IMPASSABLE_VEHICLE}] só se canônico
  government_control: {claim: "Officially Closed", source: MAP-A-LBL-EASTROAD, epistemic_status: OFFICIAL_CLAIM}
  public_knowledge: PUBLIC   # PUBLIC | LOCAL | RESTRICTED | SECRET | UNKNOWN
  secret_level: NONE         # NONE | OBSCURE | HIDDEN | SEALED_SECRET
  canon_status: CANONICAL    # CANONICAL | PROVISIONAL | PROPOSED
  confidence: CONFIRMED_VISUAL   # CONFIRMED_VISUAL | PROBABLE | UNCERTAIN (transcrição)
  mystery_tags: []           # RMY-*/CMY-* — só por vínculo aprovado
  route_membership: []       # PROJETADO de routes[]
  first_allowed_reveal: OPEN
```

### 13.2 Regras

- **Aresta é entidade**: tem estado, segredo e conhecimento próprios. A
  vizinhança de um nó é sempre **projetada** das arestas (`ADJACENCY_DRIFT`
  se alguém armazenar lista de vizinhos divergente).
- `distance_meters.min` nunca é menor que a distância euclidiana entre as
  pontas menos as precisões (`EDGE_SHORTER_THAN_EUCLID`, FAIL).
- `basis: EUCLID_TORTUOSITY` (antes da digitalização) usa fator 1,20 para
  `ROAD`, 1,35 para `TRAIL`/`FOREST_PATH`, 1,00 para `PORTAL`, e marca a
  aresta `PROVISIONAL`. Para `FAIL` de viagem o validador usa sempre o fator
  1,00 — **nunca reprova por estimativa**.
- Aresta cujo traçado cruza a linha/polígono de um `WAT-*` precisa de
  `crossings[]` apontando para nó `BRIDGE`, `CULVERT`, `TUNNEL` ou `FORD`
  (INV-C02). O teste é geométrico (interseção de segmentos em RCG), não
  declarativo.

### 13.3 Arestas conhecidas vs. secretas

`secret_level > NONE` torna a aresta **invisível para quem não a conhece**:
ela não aparece em `reachable`, rotas ou packs com `knowledge_view: ACTOR` de
quem não a aprendeu (seção 23). Em `ENGINE` ela aparece, marcada.

### 13.4 Entidades de via

```yaml
- id: ROAD-SGR
  names:
    - {name: "South Gate Road", kind: MAP_A_LABEL}
    - {name: "South Gate Road (Entrada Principal)", kind: MAP_B_LABEL}
  road_class: MAIN
  edges: [EDG-U-001, EDG-U-002, EDG-U-003, EDG-U-004]      # ordem física cruz → moldura sul
  claims:
    - {text: "Entrada Principal", source: SRC-MAP-A, epistemic_status: OFFICIAL_CLAIM}
    - {text: "Para os vales e o resto do mundo", source: SRC-MAP-A, epistemic_status: OFFICIAL_CLAIM}
  named_extent: DRAWN      # até onde o NOME vale: DRAWN | SEGMENT_ONLY | UNKNOWN
```

`ROAD-EAST`: o rótulo "East Road — Officially Closed" está **a leste** de
Burn Bridge; se o trecho entre a cruz e a ponte também se chama East Road é
`named_extent: SEGMENT_ONLY` + `OQ-CART-12`.

### 13.5 Água

`WAT-ASH` (Ash Burn) é `LINE` com polilinha digitalizada nos dois mapas;
lagos e pântanos são `AREA` com polígono. `MARSH` é atravessável a pé com
fator de terreno alto; `LAKE`, `RESERVOIR`, `BURN`, `RIVER` exigem estrutura
de travessia (ou `WATER_ROUTE` com barco canônico). Travessia conhecida hoje
sobre o Ash Burn no Mapa A: **apenas Burn Bridge**. Duas questões abertas
(`ANM-A-04`): (a) a via que sai de Rowan Cottage para oeste parece cruzar o
Ash Burn perto do px (990, 280) sem ponte desenhada; (b) a R2 passa ao norte
da nascente **visível** do Ash Burn — se o curso continua sob o bosque, a R2
cruza água. O validador reprovará (a) e (b) até a autora decidir: travessia
não desenhada (proposta) ou traçado que não cruza.

---

## 14. Route Schema

### 14.1 Contrato

```yaml
- id: RTE-A-R1
  label: R1
  source: SRC-MAP-A
  legend_class: ESCAPE_ROUTE        # ESCAPE_ROUTE ("Rota de fuga", A) | CONTESTED ("Rota contestada", B)
                                    # | BLOCKED ("Estrada bloqueada", B) | HIDDEN_PASSAGE ("Passagem oculta", A)
  edges: [EDG-U-110, EDG-U-111, EDG-U-112]    # traçado físico desenhado
  endpoints_drawn: [RM-URB-OPC, RM-JCT-U07]   # onde o desenho começa e acaba
  continuation_beyond_drawn: UNKNOWN          # nunca inferida
  drawn_arrow: null
  cross_map_counterpart: {route: RTE-B-CHP, relation: SAME_CORRIDOR, confidence: MEDIUM}
  mystery: RMY-R1                   # o lema "O círculo retorna." vive no RMY, não aqui
  epistemic_status: FACT            # o caminho existe onde foi desenhado
```

### 14.2 Rotas lidas nos mapas

| id | Rótulo | Mapa | Traçado desenhado | Observações |
|---|---|---|---|---|
| `RTE-A-R1` | R1 | A | Old Parish Cemetery (borda leste) → sudeste → borda oeste do centro, entre Saint Morrow Chapel e Office of Civic Preservation, ≈ (−369, 89) | ≈ 900 m desenhados; **não** chega à capela nem ao Culvert (D-CART-03) |
| `RTE-A-R2` | R2 | A | Shepherd's Bothy → leste, pela borda sul de Strathmoor Woods → desce até Rowan Cottage | ponta de seta desenhada junto a Rowan Cottage (anotação, não sentido) |
| `RTE-A-R3` | R3 | A | Old Quarry (borda leste) → leste, pela margem sul de Sheep Fields → Manfred Farm | **não** segue para a East Road (D-CART-04) |
| `RTE-B-R3-STR` | R3 | B | mesmo corredor de `RTE-A-R2` (Bothy → Strathmoor → Rowan) | **rótulo diverge** (`ANM-X-01`) |
| `RTE-B-R3-GLN` | R3 | B | trilha vermelha pontilhada que desce da cordilheira norte até a estrada de Glenath | ao norte some na montanha → `EXT-09` |
| `RTE-B-QM` | glifo ilegível | B | mesmo corredor de `RTE-A-R3` (Old Quarry → Manfred Farm) | glifo `GLY-B-09`, leitura candidata "R3" (baixa confiança) |
| `RTE-B-CHP` | sem rótulo | B | segmento vermelho contínuo entre capela/cemitério e o casario | mesmo corredor de `RTE-A-R1` |
| `RTE-B-R4` | R4 | B | junto à South Gate Road (Entrada Principal), traço vermelho curto para sudeste (rumo a Carriden) | ver `EXT-01` |
| `RTE-B-R7` | R7 | B | estrada ao sul de Muirfield Farm, sentido leste–oeste, com traço vermelho curto a leste do marcador | lema "Desaparece após a ponte." — **nenhuma ponte identificada** junto ao marcador (`OQ-CART-13`) |
| `RTE-B-R13` | R13 | B | estrada ao norte de Mossgate, de Willowford para leste, rumo à placa "Para Eldham (41 milhas)" | lema "Sinais foram removidos." |
| `RTE-B-R17` | R17 | B | tracejado vermelho do entroncamento Stonewell/Thistlebank para nordeste, rumo a Cairnvale/South Gate | lema "Usada, mas por quem?" |
| — | R1, R2 | B | listados na legenda "Rotas Contestadas" **sem marcador localizado** no Mapa B | `ANM-B-10`; glifos ilegíveis `GLY-B-*` podem ser eles — **não** atribuídos |

"As R1, R2, R3 do Mapa A são as mesmas R1, R2, R3 da legenda do Mapa B?"
**não** é respondida pela cartografia: é `CMY-02` (seção 21.4).

### 14.3 Regras

- Rota é **conjunto nomeado de arestas físicas**; o traçado desenhado é fato.
  Rota não cria aresta: se o desenho não coincide com via existente, a
  digitalização cria a aresta (`TRAIL`) com a mesma proveniência.
- `continuation_beyond_drawn` é sempre `UNKNOWN` na transcrição.
- `legend_class` é classe **do mapa** ("rota de fuga" é o que o mapa diz;
  ninguém verificou que ela sirva para fugir).
- Rota não herda `secret_level` da legenda: "Rota de fuga" impressa num mapa
  de aparência oficial é contraditória com segredo; o `secret_level` de cada
  aresta é decisão (`OQ-CART-11`).

---

## 15. Address Registry

### 15.1 Princípio

Nenhuma fonte mostra endereço. O registro nasce **vazio** e só cresce por
proposta. Os exemplos da missão ("17 Saint Morrow Road", "3 Preservation
Square") **não** entram: nem "Saint Morrow Road" nem "Preservation Square"
existem nos mapas — criá-los seria nomear via e praça por conveniência.

### 15.2 Contrato

```yaml
- id: ADR-0001
  location: RM-URB-MNF
  form: OFFICIAL                 # OFFICIAL | HISTORICAL | COLLOQUIAL | POSTAL | ARCHIVE
  text: "Manfred Farm, <via canônica>"
  parts: {number: null, road: ROAD-XXX, locality: RM-REG-RDM, district: null}
  valid_from: null
  valid_until: null
  source: CP-0012                # proposta aprovada que o criou
  epistemic_status: FACT         # ou OFFICIAL_CLAIM se é o que o governo registra
```

Regras: `road` precisa resolver para `ROAD-*` existente
(`ADDRESS_ROAD_UNKNOWN`); `location` precisa existir; dois endereços `OFFICIAL`
válidos no mesmo período para o mesmo lugar reprovam (`ADDRESS_DUPLICATE`).
Nome de via novo = proposta de `ROAD-*` primeiro.

---

## 16. Visibility Model

### 16.1 O que o sistema pode e não pode saber

As fontes **não têm relevo** (salvo Ben Ràth, 714 m) nem altura de edifícios.
Um cálculo de linha de visada por terreno seria precisão falsa. Por isso a
visibilidade é respondida em três bases, sempre declaradas na resposta:

| `basis` | Quando | Confiabilidade |
|---|---|---|
| `DECLARED` | existe `SGT-*` aprovado para o par (ou para as áreas que os contêm) | canônica |
| `DERIVED_RULE` | não há sightline, mas as regras 16.3 decidem sem ambiguidade (subsolo, distância acima do limiar, interior de edifício) | canônica por regra |
| `UNDETERMINED` | as regras não decidem (distância dentro do limiar e terreno intermediário sem classificação) | **não** permite afirmar visão na prosa (`VS-03`) |

### 16.2 Classes de visibilidade de lugar e aresta (missão §13)

`OPEN` · `PARTIALLY_OBSTRUCTED` · `HIDDEN` · `UNDERGROUND` · `DENSE_VEGETATION` ·
`ELEVATION_ADVANTAGE` (ponto de observação; exige proposta) · `BLIND_CORNER`
(curva/muro que corta a visada; exige proposta) · `INTERIOR`.

### 16.3 Regras derivadas

1. Observador ou alvo em `UNDERGROUND`/`INTERIOR` sem abertura declarada →
   `NOT_VISIBLE` (a superfície nunca vê o subsolo: `VS-02`).
2. Distância mínima (`euclid − precisões`) maior que o **limiar de detecção**
   da iluminação → `NOT_VISIBLE`.
3. O segmento observador→alvo cruza polígono `FOREST` com `DENSE_VEGETATION`
   por mais de 50 m → `NOT_VISIBLE`; por menos → `PARTIAL`.
4. O segmento cruza `UNL-*`/edifício digitalizado → `PARTIAL`.
5. Caso contrário, dentro do limiar e sem obstáculo classificado → `VISIBLE`
   **somente se** todo o segmento estiver em terreno classificado como aberto;
   senão `UNDETERMINED`.

Limiares de **detecção de uma figura humana em movimento** (**aprovados** pela autora em 2026-09-19 — `OQ-CART-14`):

| Iluminação | Alvo sem luz | Alvo com luz própria |
|---|---|---|
| `DAYLIGHT` | 1.500 m | — |
| `OVERCAST` | 1.000 m | — |
| `TWILIGHT` | 400 m | 1.500 m |
| `NIGHT_MOON` | 150 m | 2.000 m |
| `NIGHT_DARK` | 30 m | 2.000 m |
| `FOG` (modificador) | mín(limiar, 60 m) | mín(limiar, 150 m) |

**Detectar não é reconhecer.** Em SEM ROSTO, por premissa do DEDR (§33), o
rosto não está disponível; reconhecer *quem* é uma figura depende de pistas
que só o canon da história define (andar, roupa, voz, objetos). A cartografia
responde "poderia ter visto **alguém** atravessar a ponte"; "poderia ter
reconhecido **ela**" retorna `RECOGNITION_OUT_OF_SCOPE` com a distância e a
iluminação, para o julgamento do canon narrativo.

### 16.4 Sightlines declaradas

```yaml
- id: SGT-0001
  from: RM-URB-PMP            # ou área/aresta
  to: RM-URB-BBR
  result: {DAYLIGHT: VISIBLE, NIGHT_MOON: PARTIAL, NIGHT_DARK: NOT_VISIBLE}
  symmetric: true
  occluders: []
  source: CP-0031             # proposta aprovada
```

`VS-01 SIGHT_CLAIM_NOT_VISIBLE` (FAIL): staging declara `sees: <ator/lugar>`
e a consulta devolve `NOT_VISIBLE`. `VS-03 SIGHT_CLAIM_UNDETERMINED`
(WARNING): devolve `UNDETERMINED` — a cena pode seguir, mas a autora deve
declarar a sightline.

Exemplo (Apêndice C, pergunta 4): do Pumping Station a Burn Bridge a
distância é ≈ 500 m (±85). `DAYLIGHT` → dentro do limiar; a vegetação ciliar
do Ash Burn entre os dois não está classificada → `UNDETERMINED`.
`NIGHT_DARK` sem luz → `NOT_VISIBLE` por regra 2 (500 m > 30 m); com o alvo
carregando lanterna → dentro do limiar, novamente `UNDETERMINED` até a
sightline ser declarada.

---

## 17. Travel Model

### 17.1 Três tempos (missão §12)

Para uma viagem `A → B` em modo `M` sob condições `C`:

| Tempo | Definição | Uso |
|---|---|---|
| `minimum_travel_time` | comprimento **mínimo** do melhor caminho permitido ÷ **velocidade física máxima absoluta** do modo para aquela distância; só modificadores inevitáveis (tipo de terreno obrigatório, portais) | limite de `FAIL` físico |
| `expected_travel_time` | comprimento **nominal** ÷ velocidade do **perfil** do ator × todos os modificadores | referência de planejamento |
| `maximum_reasonable_travel_time` | `expected × 1,75 + atrasos de portal` | acima disso: `INFO UNEXPLAINED_DELAY` (a narrativa pode explicar) |

"Melhor caminho permitido" = menor tempo esperado entre caminhos que **o
ator conhece**, cujas arestas estão **abertas naquele capítulo** e cujo
acesso o ator **satisfaz** (seção 17.4).

### 17.2 Velocidades (**aprovadas** — `OQ-CART-14`)

Velocidade **física máxima absoluta** (humano de elite; só para `FAIL`; **aprovada**):

| Modo | ≤ 400 m | ≤ 1.500 m | ≤ 5 km | ≤ 10 km | > 10 km |
|---|---|---|---|---|---|
| `WALK` | 2,2 m/s | 2,2 | 2,2 | 2,1 | 2,0 |
| `RUN` | 9,0 m/s | 7,3 | 6,6 | 6,3 | 6,0 |
| `CRAWL` | 0,5 m/s | 0,5 | 0,4 | 0,4 | 0,4 |
| `VEHICLE` | limite por `road_class` (MAIN 25 m/s, SECONDARY 17, TRACK 8) | | | | |

Velocidades de **perfil** (para `expected` e `TRAVEL_BEYOND_PROFILE`; **aprovadas**):

| Perfil | `WALK` | `RUN` sustentado | `RUN` máx. esforço | `CRAWL` | `STOOP` |
|---|---|---|---|---|---|
| `UNTRAINED` | 1,25 | 2,6 | 3,4 | 0,25 | 0,6 |
| `FIT` (padrão) | 1,35 | 3,2 | 4,2 | 0,30 | 0,7 |
| `ATHLETIC` | 1,45 | 3,8 | 5,2 | 0,35 | 0,8 |
| `IMPAIRED` | 0,8 | — | 1,5 | 0,15 | 0,4 |
| `ELDERLY` | 1,0 | 1,8 | 2,5 | 0,15 | 0,5 |

O perfil de cada personagem vem do canon da história (`mobility_profiles`
no pacote); ausente → `FIT` com `INFO MOBILITY_PROFILE_DEFAULTED`. Veículos
(carro, carroça do Old Coach Stop, bicicleta) só existem se o canon da
história os declarar disponíveis — a cartografia só sabe quais arestas os
suportam (`vehicle_access`).

### 17.3 Modificadores (multiplicam o tempo)

| Fator | Valor | Inevitável? (entra no mínimo) |
|---|---|---|
| Terreno `ROAD_SURFACE` / `TRACK` / `FIELD` / `FOREST_FLOOR` / `MARSH` | 1,00 / 1,10 / 1,25 / 1,35 / 2,50 | sim para `MARSH` e `FOREST_FLOOR` fora de trilha; não para os demais |
| `DRAIN_CHANNEL` | força `STOOP` | sim |
| `CRAWLSPACE` | força `CRAWL` | sim |
| Portal (`vertical_delay_s`) | +60 s mín. / +120 s esperado (proposta) | sim |
| `NIGHT_DARK` sem luz, rota familiar / não familiar | 1,30 / 1,60 | não |
| `NIGHT_MOON` / `NIGHT_LIGHT` | 1,15 / 1,10 | não |
| `RAIN` / `SNOW` / `FOG` | 1,10 / 1,50 / 1,20 | não |
| Ferimento `MINOR` / `MAJOR` | 1,30 / 2,20 | não (salvo `MAJOR` declarado incapacitante) |
| Carregando pessoa | 2,00 | não |
| Rota conhecida mas não familiar | 1,20 | não |
| Perseguição (alvo ou perseguidor) | troca o modo para `RUN` máx. esforço por até 400 m, depois sustentado | — |

### 17.4 Filtros de caminho

Um caminho só é candidato se, **no capítulo e instante da viagem**:

1. todas as arestas estão `OPEN` (ou `RESTRICTED` com `access_action` —
   seção 17.6);
2. todas as arestas `secret_level > NONE` estão no conhecimento do ator
   (`knowledge_view: ACTOR`, seção 23);
3. o modo é suportado (`vehicle_access`, `max_passage` ≥ corpo do ator);
4. nenhuma travessia de água sem estrutura (INV-C02 já garante no grafo);
5. horários de funcionamento respeitados quando declarados.

### 17.5 Pesos de rota

| Consulta | Peso da aresta |
|---|---|
| `shortest_route` | tempo esperado |
| `safest_route` | tempo × (1 + risco) × (1 + exposição), com `risk` e `surveillance` `UNSPECIFIED` tratados como 0,5 e **sinalizados** no resultado |
| `hidden_route` | tempo × (1 + fator de visibilidade: `OPEN` 3, `PARTIAL` 1, `HIDDEN`/`UNDERGROUND` 0) |

### 17.6 Staging, movimentos e o relógio da cena

```yaml
# runtime/<slug>/canon/cartography/STAGING.yaml   (dono: CANON_GUARDIAN; PLANNED → REALIZED)
clock:
  format: "D<nnn>T<HH:MM>"        # dia da história + hora local; o calendário é do TIMELINE
staging:
  - id: STG-0101
    status: PLANNED               # PLANNED | REALIZED
    chapter: 7
    scene: SC-07-02
    actor: CHR-P                  # id do ledger
    at: "D014T23:14"
    location: RM-CEN-RSP
    sees: []                      # afirmações de visão a validar (seção 16)
    ledger_event: EV-31           # opcional: evento do ledger que esta cena realiza
movements:
  - id: MOV-0044
    status: PLANNED
    actor: CHR-P
    from_staging: STG-0101
    to_staging: STG-0102
    mode: WALK                    # WALK | RUN | CRAWL | VEHICLE | MIXED
    route: null                   # null = o validador escolhe o melhor caminho permitido;
                                  # lista de EDG-* = rota declarada (validada aresta a aresta)
    conditions: {lighting: NIGHT_DARK, weather: RAIN, injury: NONE, carrying: NONE}
    access_actions: []            # EV-* do ledger que justificam atravessar algo fechado
    planned_on: KNOWLEDGE         # KNOWLEDGE | BELIEF:<MAP-*>  (seção 23.4)
```

Regras: dois stagings consecutivos do mesmo ator em lugares diferentes
**exigem** movimento viável entre eles (declarado ou inferido). Sem
movimento declarado, o validador infere o melhor caminho e aplica os mesmos
limites (`TR-05 TELEPORT` se nenhum caminho permitido existir no intervalo).

### 17.7 Veredito do validador de caminho (missão §28)

Entrada: `character_id, origin, destination, start_time, arrival_time,
travel_mode, known_routes (projetado), scene_id`. Saída:

| Veredito | Código | Condição |
|---|---|---|
| `FAIL` | `TR-01 TRAVEL_PHYSICALLY_IMPOSSIBLE` | intervalo < `minimum_travel_time` |
| `FAIL` | `TR-06 NO_PERMITTED_PATH` | não há caminho que satisfaça 17.4 |
| `FAIL` | `KN-01 SECRET_ROUTE_UNKNOWN_TO_ACTOR` | rota declarada usa aresta secreta que o ator não conhece |
| `FAIL` | `AC-01 CLOSED_TRAVERSAL_WITHOUT_ACTION` | rota declarada atravessa aresta/lugar fechado naquele capítulo sem `access_actions` |
| `FAIL` | `TR-03 TRAVEL_BEYOND_PROFILE` | intervalo < tempo com o **máximo esforço do perfil** do ator |
| `WARNING` | `TR-02 TRAVEL_REQUIRES_RUNNING` | modo declarado `WALK`, mas só correndo cabe |
| `WARNING` | `TR-07 TRAVEL_TIGHT` | intervalo < `expected` (possível, apertado) |
| `WARNING` | `COORDINATE_PROVISIONAL` | viagem toca nó `PROVISIONAL` (a escala regional já está decidida; sobra o caso de digitalização `UNCERTAIN`) |
| `INFO` | `TR-04 UNEXPLAINED_DELAY` | intervalo > `maximum_reasonable` |
| `PASS` | — | nenhum dos acima |

Exemplo da missão (Apêndice C, pergunta 2): **sair do Red Stag Pub às 23:14 e
chegar ao Old Parish Cemetery às 23:18 caminhando.** Distância mínima
≈ 1.525 m (euclidiana; o caminho por vias só pode ser maior). Mínimo físico a
pé: 1.525 ÷ 2,2 ≈ **11 min 33 s**. Intervalo declarado: 4 min →
**`FAIL TR-01`**. Mesmo correndo (perfil `FIT`, máximo esforço 4,2 m/s):
≈ 6 min 03 s → **`FAIL TR-03`**. O motor sugere o que é possível: a pé, pelo caminho
por vias (≈ 1,83 km, estimativa `EUCLID_TORTUOSITY` até a digitalização),
chegada esperada entre ≈ 23:37 (via iluminada) e ≈ 23:43 (noite sem luz, rota
familiar) — a iluminação pública de Redmur é `UNKNOWN`.

---

## 18. Hideout Model

### 18.1 Contrato (missão §14)

```yaml
- id: HID-RCH
  location: RM-URB-RCH               # Root Cellar Hideout — único esconderijo rotulado nas fontes
  source: {map: SRC-MAP-A, label: "Root Cellar Hideout", marker: RED_DOT_AT_ENTRANCE}
  capacity: UNSPECIFIED              # pessoas
  discoverability: UNSPECIFIED       # OBVIOUS | FINDABLE | OBSCURE | NEAR_IMPOSSIBLE
  entry_points: [EDG-U-201]          # superfície (projetado + declarado)
  exit_points: [EDG-U-201, EDG-P-004]    # inclui o portal para Root Cellar Passage
  concealment: UNSPECIFIED
  sound_isolation: UNSPECIFIED
  weather_protection: UNSPECIFIED
  duration_safe: UNSPECIFIED         # horas antes de risco (ar, água, busca)
  known_by: []                       # projetado (baseline + ledger)
  historical_usage: []               # claims
  clue_presence: []                  # EVD-*
  escape_routes: null                # PROJETADO: escape_routes(HID-RCH, ctx)
  compromise_events: []              # [{event: EV-*, chapter, effect: COMPROMISED|DESTROYED|WATCHED}]
  status: UNKNOWN
```

### 18.2 Regras

- **Nenhum esconderijo espontâneo**: staging com `role: HIDING` num lugar que
  não é `HID-*` → `HD-01 SPONTANEOUS_HIDEOUT` (FAIL). Esconder-se atrás de
  algo (cobertura momentânea numa perseguição) não é esconderijo — é
  `cover` de aresta/lugar (seção 28).
- `HD-02 HIDEOUT_OVER_CAPACITY`, `HD-03 HIDEOUT_OVERSTAY` (`duration_safe`),
  `HD-04 COMPROMISED_HIDEOUT_REUSED` (usar sem nova ação depois de evento
  `COMPROMISED` conhecido pelo ator).
- O **ponto vermelho** junto à entrada do Root Cellar Hideout é o único
  marcador desse tipo no Mapa A; significado `UNKNOWN` (`MAP-A-MRK-01`).
- Candidatos naturais (Shepherd's Bothy, Creggan Bothy, Ruined Tool Shed,
  ruínas) **não** são esconderijos até proposta.

---

## 19. Boundary Model

### 19.1 Contrato

```yaml
- id: BND-B-01
  kind: UNCERTAIN_LIMIT        # UNCERTAIN_LIMIT | ADMINISTRATIVE | RESTRICTED_ZONE | NATURAL | MAP_FRAME
  source: {map: SRC-MAP-B, legend: "Limite incerto", px_polyline: [...]}
  geometry: LINE
  certainty: UNCERTAIN         # a própria legenda diz "incerto"
  crossing_effect: NONE_PHYSICAL   # limite não é barreira física, salvo declaração
  claims: []
  epistemic_status: OFFICIAL_CLAIM
```

### 19.2 Fronteiras identificadas

| id | Tipo | Onde | Observação |
|---|---|---|---|
| `BND-B-01` | `UNCERTAIN_LIMIT` | NE do Mapa B, linhas brancas pontilhadas cruzando a "Estrada 13 Em Disputa" | legenda: "Limite incerto" |
| `BND-B-02` | `UNCERTAIN_LIMIT` ou trilha | O do Mapa B, linha pontilhada rumo a "Para Dunsgate" | símbolo entre "Trilha" e "Limite incerto" — `ANM-B-14` |
| `BND-A-01` | `RESTRICTED_ZONE` | hachura vermelha sobre a East Road, a leste de Burn Bridge (Mapa A) e sobre o Ash Burn a sudeste da ponte (Mapa B) | legenda A: "Área restrita"; X = bloqueio físico no ponto |
| `BND-A-FRAME` / `BND-B-FRAME` | `MAP_FRAME` | molduras | **não é fronteira do mundo**: é o limite do que foi desenhado |
| `BND-ADM-CP` | `ADMINISTRATIVE` | "District of Civic Preservation" (subtítulo do Mapa A) | extensão `UNKNOWN`; nenhuma linha desenhada |

"Não há fronteiras, apenas mais estradas" (`MAP-B-TXT-02`) é alegação; ela
convive com o fato físico de que a moldura existe e com a alegação da
legenda de que há limites incertos.

---

## 20. Exit Ambiguity Model

### 20.1 Onde termina a competência da cartografia

Uma via que toca a moldura **sai do desenho**. Se ela sai **do vale**, de
Redmur ou do mundo conhecido é uma pergunta sobre o que existe **além da
moldura** — domínio `OFF_MAP`, que a cartografia **não modela**. Por isso:

```text
INV-C07  Nenhuma saída verdadeira pode ser inferida pelo motor.
         Não por política: por construção. O grafo físico termina na moldura.
         shortest_path só pode chegar a um FRAME_PORTAL, nunca a "fora".
```

### 20.2 Contrato

```yaml
- id: EXT-03
  road: ROAD-E13                           # "Estrada 13 Em Disputa"
  frame_portal: RM-FRM-B-NE1
  physical:
    drawn_to: FRAME                        # FRAME | DEAD_END | LOOP_WITHIN_FRAME | BLOCKED_POINT
    beyond_frame: OFF_MAP                  # sempre; a cartografia não sabe
    passable_to_frame: UNKNOWN             # há bloqueio desenhado antes da moldura?
  claims:                                  # o que fontes/artefatos dizem — nenhuma é verdade por si
    - {class: DISPUTED_EXIT, text: "Estrada 13 Em Disputa", source: SRC-MAP-B, epistemic_status: OFFICIAL_CLAIM}
    - {class: APPARENT_EXIT, text: "Para Caelrith? (32 milhas)", source: SRC-MAP-B, epistemic_status: OFFICIAL_CLAIM}
  exit_classes: [APPARENT_EXIT, DISPUTED_EXIT]   # PROJETADO das claims; nunca inclui valor fora do enum
  route_mysteries: []                      # RMY-* ligados por proposta
  truth_ref: null                          # GT-*/Q-* no Story Truth Ledger, se e quando existir
  first_allowed_reveal: OPEN
```

Enum fechado de `class` (missão §15): `APPARENT_EXIT · OFFICIAL_EXIT ·
HISTORICAL_EXIT · CLOSED_EXIT · DISPUTED_EXIT · FALSE_EXIT · UNKNOWN_EXIT`.

- `APPARENT_EXIT` é o **único** valor que o motor atribui sozinho: toda via que
  chega à moldura. É geometria.
- `FALSE_EXIT` só com `truth_ref` resolvido **ou** prova física dentro da
  moldura (a via desenhada "Para X" volta ao núcleo sem tocar a moldura →
  `drawn_to: LOOP_WITHIN_FRAME` → aí a alegação "Para X" é fisicamente falsa
  **dentro do desenho**, e é isso que se registra — nada sobre X).
- As demais classes vêm de texto de fonte/artefato.

### 20.3 Saídas identificadas

| id | Via | Moldura | Alegações | Classes |
|---|---|---|---|---|
| `EXT-01` | South Gate Road | A: sul · B: sul | "Entrada Principal" (A e B); "Para os vales e o resto do mundo" (A); marcador R4 "Entrada ou saída?" adjacente (B) | `APPARENT_EXIT`, `OFFICIAL_EXIT` (alegada — o rótulo diz *entrada*) |
| `EXT-02` | East Road | A: leste · B: leste | "Officially Closed"; X e hachura "Área restrita" | `APPARENT_EXIT`, `CLOSED_EXIT` (alegada; a barreira no X é física) |
| `EXT-03` | Estrada 13 | B: NE | "Em Disputa"; "Para Caelrith? (32 milhas)"; limites incertos cruzando | `APPARENT_EXIT`, `DISPUTED_EXIT` |
| `EXT-04` | trilha oeste | B: O | "Para Dunsgate (17 milhas)"; linha possivelmente "limite incerto" | `APPARENT_EXIT`, `UNKNOWN_EXIT` |
| `EXT-05` | estrada SO (Loch Calder) | B: SO | "Para Westhaven (29 milhas)" | `APPARENT_EXIT` |
| `EXT-06` | estrada SO (Thistlebank) | B: SO | "Para Inverloch (?7 milhas)" | `APPARENT_EXIT` |
| `EXT-07` | estrada E–SE (R13) | B: SE | "Para Eldham (41 milhas)"; R13 "Sinais foram removidos." | `APPARENT_EXIT` |
| `EXT-08` | trilha vermelha S de Mossgate | B: SE | "Para Eldham (41 milhas)" (segunda placa) | `APPARENT_EXIT` |
| `EXT-09` | R3 norte (Glenath) | B: N (montanha) | trilha contestada que sobe a cordilheira | `UNKNOWN_EXIT` |
| `EXT-10` | via NE perto de Kellburne | B: NE | trechos vermelhos pontilhados = "Estrada bloqueada" | `APPARENT_EXIT`, `CLOSED_EXIT` (alegada) |
| `EXT-11..` | demais vias que tocam a moldura do Mapa B | B | nenhuma | `APPARENT_EXIT` (inventário na digitalização, S2) |

Vias que cruzam a moldura **do Mapa A** não são saídas: são `FRAME_LINK`
para o Mapa B (seção 8.1).

### 20.4 MYSTERY PRESERVATION GATE (missão §38)

Quatro barreiras independentes:

1. **Não representável.** `TRUE_EXIT`, `REAL_EXIT` e equivalentes não existem
   em nenhum enum; qualquer string com essa semântica em qualquer campo reprova
   (`MY-02 TRUE_EXIT_ASSERTED`, BLOCKER).
2. **Sem chave de resposta.** REUSE de `HIDDEN_ANSWER_KEYS`
   (`check_interpretive_canon.py:121`) + extensão cartográfica
   `{true_exit, real_exit, saida_verdadeira, actual_pattern, solution,
   decoded, decoding, real_route, verdadeira}` em **todos** os níveis de
   **todos** os arquivos da cartografia (`MY-01 HIDDEN_ANSWER_PRESENT`,
   BLOCKER).
3. **Só ponteiro.** A única ponte para a verdade é `truth_ref` (id opaco).
   O validador verifica que o id resolve no ledger/canon interpretativo e que
   nada do conteúdo foi copiado (`MY-05 TRUTH_REF_UNRESOLVED`,
   `MY-07 TRUTH_CONTENT_COPIED` por comparação de texto com o GT).
4. **Consulta recusada.** `check_cartography.py --exits` devolve as saídas com
   classes e alegações e a frase fixa `EXIT_TRUTH_NOT_IN_CARTOGRAPHY`. Um
   pedido explícito (`--exit-truth`) devolve apenas os `truth_ref` e, **só**
   com `--engine-view --authorized-by <GT-*>` de um GT cujo `reader_access` o
   caller está autorizado a ver (mesma regra de `beliefs_state` do ledger, que
   omite `truth` sem `--engine-view`), o id é confirmado como pertinente. O
   conteúdo continua no ledger.

"O sistema cartográfico conhece estrutura. O sistema narrativo conhece
significado."

---

## 21. Cartographic Mystery Model

### 21.1 Posição na arquitetura

Um `CARTOGRAPHIC_MYSTERY` é o **lado espacial** de uma pergunta. Ele não
guarda hipóteses concorrentes com peso nem verdade: isso já existe no canon
interpretativo (`questions[].interpretations`, evidências com suporte
`S/C/X/-`, `resolution_policy`). O `CMY` junta **quais elementos do mapa**
participam da pergunta, e o canon interpretativo cuida do resto.

### 21.2 Contrato

```yaml
- id: CMY-02
  question: "As rotas R1–R3 do mapa urbano são as mesmas R1–R3 da legenda regional?"
  question_ref: null                 # Q-* no canon interpretativo, quando a autora criar
  involved_locations: [RM-URB-OPC, RM-URB-SBO, RM-URB-ROW, RM-URB-OQY, RM-URB-MNF]
  involved_routes: [RTE-A-R1, RTE-A-R2, RTE-A-R3, RTE-B-R3-STR, RTE-B-R3-GLN, RTE-B-QM, RTE-B-CHP]
  numbers: ["R1", "R2", "R3"]
  names: []
  ordering: null
  map_artifacts: [SRC-MAP-A, SRC-MAP-B, MAP-B-TXT-06]
  anomalies: [ANM-X-01]
  reader_visible_pattern: "O trajeto Bothy–Rowan é R2 no mapa da cidade e R3 no mapa dos arredores."
  pattern_space: [NUMBERS, ROUTES]   # tipos de padrão possíveis (missão §18); NÃO é afirmação de padrão
  candidate_interpretations: []      # leituras propostas; SEM valor de verdade (D-CART-08)
  required_clues: []                 # EVD-* necessários para qualquer leitura ser defensável
  forbidden_early_reveals: []        # ids que não podem chegar ao leitor antes de X
  truth_ref: null                    # único vínculo com a verdade (D-CART-08)
  activation: CONTINGENT_ON [ANM-X-01 = INTENTIONAL_ARTIFACT]
  resolution_state: UNRESOLVED       # UNRESOLVED | PARTIALLY_RESOLVED | RESOLVED | PERMANENTLY_AMBIGUOUS
```

Regras:

- `resolution_state ∈ {RESOLVED, PARTIALLY_RESOLVED}` exige `truth_ref` e
  `question_ref` resolvidos (`MY-04 PATTERN_WITHOUT_LEDGER`).
- `question_ref` com `resolution_policy: NEVER` ⇒ `resolution_state ∈
  {UNRESOLVED, PERMANENTLY_AMBIGUOUS}` (REUSE da regra NEVER do LTE).
- `candidate_interpretations[]` aceita texto, mas **nenhum** campo de
  avaliação (`plausible`, `true`, `false`, `score`) — `MY-01`.
- `activation: CONTINGENT_ON` um `ANM-*` `UNDECIDED` ⇒ o CMY é inerte: não
  pode ser citado por evidência, brief ou staging (`MY-06
  ANOMALY_USED_AS_CLUE`).

### 21.3 Route Mystery records (missão §16)

| id | Rótulo | Lema (literal) | Âncora no Mapa B | Rotas físicas | Estado |
|---|---|---|---|---|---|
| `RMY-R1` | R1 | "O círculo retorna." | **não localizada** (`ANM-B-10`) | candidata física: `RTE-A-R1` (só pelo rótulo igual — **não** vinculada) | `UNRESOLVED` |
| `RMY-R2` | R2 | "Nem todo caminho continua." | **não localizada** | idem `RTE-A-R2` | `UNRESOLVED` |
| `RMY-R3` | R3 | "Há mais de uma margem." | três ocorrências (`RTE-B-R3-GLN`, `RTE-B-R3-STR`, glifo candidato em `RTE-B-QM`) | `ANM-B-09` | `UNRESOLVED` |
| `RMY-R4` | R4 | "Entrada ou saída?" | junto à South Gate Road | `RTE-B-R4` | `UNRESOLVED` |
| `RMY-R7` | R7 | "Desaparece após a ponte." | sul de Muirfield Farm | `RTE-B-R7`; ponte não identificada | `UNRESOLVED` |
| `RMY-R13` | R13 | "Sinais foram removidos." | a leste de Willowford, rumo a Eldham | `RTE-B-R13` | `UNRESOLVED` |
| `RMY-R17` | R17 | "Usada, mas por quem?" | entre Stonewell/Thistlebank e Cairnvale | `RTE-B-R17` | `UNRESOLVED` |

```yaml
- id: RMY-R7
  label: R7
  motto: "Desaparece após a ponte."
  motto_status: MAP_ARTIFACT           # lema é artefato, nunca instrução ao motor
  map_b_anchor: {px: [262, 545], confidence: HIGH}
  physical_routes: [RTE-B-R7]
  physical_facts_checked:              # o que a cartografia pode dizer sem interpretar
    - "Nenhum nó BRIDGE a menos de 300 m do marcador na transcrição v0."
  candidate_interpretations: []
  truth_ref: null
  resolution_state: UNRESOLVED
```

`physical_facts_checked` é a contribuição **legítima** do motor ao mistério:
ele pode dizer "não há ponte perto do marcador R7" (fato), nunca "logo o lema
é falso" (interpretação).

### 21.4 Mistérios cartográficos iniciais

Todos `UNRESOLVED`, `truth_ref: null`, sem interpretação registrada:

| id | Pergunta | Ativação |
|---|---|---|
| `CMY-01` | Alguma das vias que tocam a moldura leva para fora de Redmur? Qual? | ativo |
| `CMY-02` | As rotas R1–R3 do Mapa A são as mesmas da legenda do Mapa B? | **ativo** (`ANM-X-01` intencional) |
| `CMY-03` | Por que o registro tem dois "05" e nenhum "06"? | **ativo** (`ANM-B-01` intencional) |
| `CMY-04` | Por que os marcadores são R1, R2, R3, R4, R7, R13, R17? | ativo |
| `CMY-05` | Letham e Passo de Muirchéin são lugares ou avisos? | ativo (o próprio mapa sugere a pergunta: `MAP-B-TXT-05`) |
| `CMY-06` | As distâncias do Mapa B (barra, placas, duas Eldham a 41 milhas) são verdadeiras? | **ativo** (`ANM-X-02`, `ANM-B-03/04/06` intencionais); a parte física depende de `OQ-CART-01`; o **porquê** fica aqui |
| `CMY-07` | O que é o triângulo branco junto à capela no Mapa B? | **ativo** (`ANM-B-11` intencional) |
| `CMY-08` | Os lemas dos dois mapas compõem uma mensagem? | ativo |
| `CMY-09` | Quem produziu os mapas dentro do mundo? | ativo · `PERMANENTLY_AMBIGUOUS` (22.7); `question_ref: Q-MAP-AUTHOR` |

### 21.5 O Registro dos Vilarejos (missão §19)

```yaml
register:
  artifact: MAP-B-REG
  title: "Registro dos Vilarejos (e não apenas deles)"
  footer: "Nem todo nome no mapa é um lugar. Alguns são avisos."
  entries:
    - {id: REG-B-01,  display_index: "01", printed_name: "Redmur",              location_id: RM-REG-RDM}
    - {id: REG-B-02,  display_index: "02", printed_name: "Saint Morrow",        location_id: null,
       candidates: [RM-CEN-CHP, RM-CEN-SMC], placement: NO_STANDALONE_LABEL}
    - {id: REG-B-05a, display_index: "05", printed_name: "Rowan Cottage",       location_id: RM-URB-ROW}
    - {id: REG-B-05b, display_index: "05", printed_name: "Glenath",             location_id: RM-REG-GLN}
    - {id: REG-B-17,  display_index: "17", printed_name: "Letham",              location_id: null, placement: NOT_ON_MAP}
    - {id: REG-B-23,  display_index: "23", printed_name: "Passo de Muirchéin",  location_id: null, placement: NOT_ON_MAP}
    # ... 30 linhas impressas no total (lista completa na seção 38.4)
  per_entry_defaults:
    public_interpretation: null        # o que o mundo diz que a lista é (claim), quando o canon disser
    historical_interpretation: null
    truth_ref: null
    ordering_significance: UNKNOWN     # UNKNOWN | ADMINISTRATIVE | CHRONOLOGICAL | CARTOGRAPHIC | ENCRYPTED | DECOY
  printed_order_is_artifact: true      # a ordem impressa é preservada byte a byte; nunca reordenada
```

Regras: `display_index` é **string literal** (preserva "05" duplicado e zeros
à esquerda); a ordem das entradas no arquivo = ordem impressa; o validador
compara com a transcrição da fonte (`REGISTER_DRIFT`). `ordering_significance`
só sai de `UNKNOWN` com `truth_ref`. Nenhuma função do motor computa
acrósticos, somas ou padrões sobre o registro — isso é `pattern_space`, e
pertence ao leitor.

### 21.6 Anomalias como porta de entrada do mistério

```text
ANM-* DETECTED ──(autora)──▶ INTENTIONAL_ARTIFACT ──▶ pode alimentar CMY/RMY/EVD
                 └─────────▶ RENDER_ERROR ──▶ nova versão da fonte (SRC@v1.x), antiga arquivada
                 └─────────▶ UNDECIDED (padrão) ──▶ preservada, inerte, não citável como pista
```

A distinção importa porque os mapas carregam sinais de renderização gerada
(D-CART-13): tratar erro de renderização como pista seria fabricar mistério;
corrigi-lo sem perguntar seria destruir um possível mistério. A decisão é da
autora, uma vez, e fica registrada.

**Decisão registrada (2026-09-19, OQ-CART-15): todas as 22 anomalias do
Apêndice B são `INTENTIONAL_ARTIFACT`.** Efeitos:

- os `CMY` com `activation: CONTINGENT_ON [ANM-* = INTENTIONAL_ARTIFACT]`
  (`CMY-02`, `CMY-03`, `CMY-07`) passam a **ativos**; `MY-06` deixa de
  bloquear a citação dessas anomalias por evidência, brief ou staging;
- **intencional não é interpretado**: a decisão diz que o artefato foi
  posto ali de propósito, não *por quê*, nem *o que significa*. Todo `CMY`
  continua `UNRESOLVED`, sem `truth_ref` e sem `candidate_interpretations`
  até que o Story Truth Ledger decida (INV-C08);
- nenhuma fonte é corrigida: o arquivo impresso é o arquivo pinado
  (`CG-06`); o texto corrompido de `ANM-B-12` e as barras de escala
  irregulares são impressos **como estão**;
- os glifos ilegíveis `GLY-B-01..09` seguem sem leitura atribuída: "proposital"
  não os torna legíveis, e nenhuma leitura candidata vira vínculo;
- `ANM-X-02` (escalas incompatíveis) sendo intencional é coerente com a escala decidida (`OQ-CART-01`, seção 7.4): a barra do Mapa B
  não é a escala, e o desenho ampliado do núcleo é esquemático.

---

## 22. Official vs Physical vs Reader Maps

### 22.1 Camadas (missão §20)

| Camada | O que é | Armazenada? | Dono |
|---|---|---|---|
| `PHYSICAL` | o que existe (grafo desta SDD) | sim | `CANON_GUARDIAN` |
| `OFFICIAL` | o que o governo de Redmur afirma existir: um ou mais artefatos `MAP-*` com `author: INST-*` | sim (como artefato) | `CANON_GUARDIAN` |
| `HISTORICAL` | versões do território em outras épocas (seção 25) | sim (como artefato + camada) | `CANON_GUARDIAN` |
| `ACTOR` | o que cada personagem/instituição sabe ou acredita | **projeção** (baseline + ledger + artefatos vistos) | — |
| `READER` | o que foi revelado ao leitor até o capítulo N | **projeção** (`knowledge_state(READER)` + stagings de POV + paratexto) | — |

### 22.2 Um artefato descreve o mundo com relações explícitas

```yaml
- id: MAP-OFF-MODERN-01
  title: "Mapa oficial do District of Civic Preservation"
  author: INST-CIVIC-PRESERVATION        # id do registry (Story canon)
  date: null
  depicts:
    - {target: RM-URB-ROW, relation: ACCURATE}
    - {target: RM-SUB-CCT, relation: OMITS}                       # existe e não aparece
    - {target: PHANTOM-001, relation: PHANTOM, as_name: "...", as_position_px: [..]}   # aparece e não existe (mais)
    - {target: RM-URB-ERC, relation: FALSIFIED_STATUS, as_status: OPEN}
    - {target: RM-URB-OPC, relation: RENAMED, as_name: "Cemitério Antigo"}
    - {target: RM-REG-KLB, relation: MISPLACED, as_position_px: [..]}
```

Os quatro casos da missão §20 viram relações: existe e não aparece =
`OMITS`; aparece e não existe = `PHANTOM` (com `valid_until` no físico, ou
nunca existiu); dois nomes = `RENAMED` + `names[]`; entrada pública falsa e
real oculta = `FALSIFIED_ACCESS` apontando para o portal verdadeiro. Uma
relação diferente de `ACCURATE` **é afirmação sobre a verdade** e por isso
exige: ou comparação direta com o grafo físico (o motor pode verificar
`PHANTOM`/`OMITS`/`MISPLACED` sozinho), ou `truth_ref` quando a comparação
envolve o que não é físico.

### 22.3 Mapa do leitor (projeção)

Para cada id, no capítulo N: `UNSEEN · MENTIONED · SEEN_ON_MAP · VISITED ·
CONNECTION_KNOWN`. Fontes da projeção: `knowledge_delta` de `READER` no
ledger (REUSE `knowledge_state`), stagings `REALIZED` com o POV presente, e
**mapas impressos como paratexto** (decisão `OQ-CART-03`: os mapas **serão impressos**; o leitor já conhece,
no capítulo 0, a topologia do inset "REDE SUBTERRÂNEA" — ver 22.6).

`KN-02 READER_MAP_LEAK` (HIGH): a prosa do capítulo N revela um id com
`first_allowed_reveal` posterior a N (detecção por nome/alias na prosa —
REUSE da extração de entidades de `check_canon_continuity.py`).

### 22.4 Contrato com o Story Truth Ledger

| A cartografia exige do canon narrativo | Onde vive hoje |
|---|---|
| ids de personagem e instituição | ledger `characters[]`; registry `INST-*` (DEDR) |
| eventos que causam mudança física ou acesso | ledger `events[]` |
| verdades com controle de revelação | ledger `GT-*` + `reader_access` |
| perguntas deliberadamente abertas | canon interpretativo `Q-*`, registry `UNK-*` |
| calendário e ano presente da história | `TIMELINE` (T017) |
| perfis de mobilidade, veículos disponíveis | pacote da obra (a definir pelo SDD narrativo) |

A cartografia **nunca** escreve nesses artefatos. O futuro SDD de canon
histórico deve apenas respeitar: ids de lugar são `RM-*`; um fato histórico
sobre um lugar é `HISTORICAL_CLAIM` ou mutação, nunca edição do grafo.

### 22.5 Os mapas como documentos do mundo (decisão OQ-CART-02)

```yaml
- id: MAP-DIEGETIC-A
  title: "REDMUR — MAPA CANÔNICO DA CIDADE"
  source_file: SRC-MAP-A                # o arquivo impresso é a fonte de produção E o documento do mundo
  author: {status: MUST_REMAIN_UNKNOWN, question_ref: Q-MAP-AUTHOR, unk_ref: UNK-MAP-AUTHOR}   # decisão OQ-CART-02b: ver 22.7
  date: UNKNOWN
  map_layer: UNKNOWN                     # NÃO atribuir camada oficial: implicaria autor institucional (22.7)
  accuracy: UNKNOWN
  tampering_status: UNKNOWN
  printed_in_book: true
  associated_mysteries: [CMY-01, CMY-08]
- id: MAP-DIEGETIC-B                     # idem, SRC-MAP-B
```

O que a decisão **muda**: os lemas ("Todo mapa mente um pouco", "Redmur
sempre observa", "Nem todo nome no mapa é um lugar") passam a ser falas de um
autor do mundo, e o inset subterrâneo passa a ser algo que **alguém desse
mundo soube desenhar**.

O que ela **não decide** (permanece `UNKNOWN`, sem preenchimento por
inferência): quem fez cada mapa; se os dois têm o mesmo autor; se o inset é
conhecimento oficial, de manutenção ou vazamento; se as anomalias são
deliberadas; se os mapas são exatos. a autoria é **mistério permanente** (22.7).

Regra derivada: um mapa diegético que **desenha** uma passagem oculta prova
que o autor do mapa a conhece — mas não que o **governo** a conhece, nem que
qualquer personagem a conhece. `KN-03` continua exigindo fonte para cada
conhecimento de ator.

### 22.6 Mapas impressos no livro (decisão OQ-CART-03)

Impressos: Mapa A completo (incluindo o inset "REDE SUBTERRÂNEA" e a legenda)
e Mapa B completo (incluindo o registro dos vilarejos e as rotas contestadas).

**Efeito sobre o mapa do leitor (projeção 22.3):**

- A linha de base do leitor **não é vazia**: no `front_matter` (capítulo 0),
  todo id que consta em `SRC-MAP-A`/`SRC-MAP-B` tem estado `SEEN_ON_MAP`; isto
  inclui a **topologia** da rede subterrânea (arestas `EDG-S-*`, portais
  `EDG-P-*`) na forma esquemática do inset.
- Não inclui: estado físico (selado? inundado?), dimensões, sentido de fluxo,
  quem sabe o quê, nem a resolução de qualquer mistério. O leitor vê o
  desenho; a verdade sobre ele continua no Story Truth Ledger.
- `KN-02 READER_MAP_LEAK` deixa de se aplicar a ids que estão nos mapas
  impressos e continua valendo para tudo que **não** está neles (esconderijos
  não desenhados, estados mutados, passagens fora do inset, camadas
  históricas).
- Ironia dramática passa a ser possível **e verificável**: o pack
  (seção 27.1) mostra, por cena, `reader_knows_but_pov_does_not` — ex.: o
  leitor viu a passagem capela–cemitério no mapa; o POV não a conhece
  (`KN-01` continua proibindo o POV de usá-la).
- Toda mutação que faça um mapa impresso mentir (uma ponte desaba, uma
  passagem é selada) gera `INFO MUTATION_DIVERGES_FROM_PRINTED_MAP`: o leitor
  tem um mapa desatualizado — legítimo e potencialmente poderoso para o
  mistério, e por isso visível ao escritor.

**Efeito sobre os mistérios:** o leitor já tem, desde a primeira página, as
anomalias, os lemas das rotas, o registro (com o "05" duplicado e o "06"
ausente), o triângulo, as placas de milhas e o "?" de Caelrith. A fase de
teoria começa **antes** do capítulo 1. Consequências práticas:

1. As anomalias impressas estão todas classificadas (`OQ-CART-15`:
   `INTENTIONAL_ARTIFACT`); portanto vão para a página **como estão**,
   incluindo `ANM-B-12` ("REDNUR SEMPBE OBSERVA", texto corrompido), as barras
   de escala e os glifos ilegíveis `GLY-B-*`. Qualquer retoque futuro é nova
   versão pinada, nunca edição silenciosa.
2. `CG-06 SOURCE_HASH_MISMATCH` protege a edição: o arquivo impresso **é** o
   arquivo pinado. Uma versão corrigida para impressão é `SRC-MAP-x@v1.1` com
   `supersedes`, nunca uma edição silenciosa.
3. Edições: mapa em imagem de página inteira; legibilidade em e-reader não
   pode alterar conteúdo (`EDITION_CAPABILITIES` modela restrições de
   edição — checar o que o Kindle preserva antes de fixar tamanho e
   resolução; `OQ-CART-03b`).
4. O contrato com o canon narrativo (22.4) ganha uma linha: o SDD de canon
   histórico não pode contradizer nada que esteja impresso — o impresso é
   canon **de leitura** ainda que suas alegações sejam falsas no mundo.

Novo teste (seção 35): **T33** — todo id presente nas fontes impressas tem
`reader_state: SEEN_ON_MAP` a partir do capítulo 0; nenhum id ausente delas
tem; `KN-02` só dispara para ids ausentes das fontes.

### 22.7 Autoria dos mapas: mistério permanente (decisão OQ-CART-02b, 2026-09-19)

Decisão da autora: **quem produziu os mapas dentro do mundo é discutido no
livro, questionado, e há "entrões" que procuram essa informação; a resposta
nunca é revelada na história.**

Em termos do motor: uma pergunta `NEVER` do canon interpretativo, com a
incógnita correspondente `MUST_REMAIN_UNKNOWN` no registry
(REUSE — nenhuma capability nova).

```yaml
# INTERPRETIVE_CANON (dono: CANON_GUARDIAN; a cartografia só aponta)
- id: Q-MAP-AUTHOR
  question: "Quem produziu os mapas de Redmur?"
  resolution_policy: NEVER
# CANON_REGISTRY
unknowns:
  - {id: UNK-MAP-AUTHOR, status: MUST_REMAIN_UNKNOWN}
prohibited_inferences:
  - {id: PRO-MAP-AUTHOR, match: "os mapas foram (feitos|produzidos|desenhados) por"}   # ilustrativo
```

**Na cartografia:**

- `MAP-DIEGETIC-*.author` é `{status: MUST_REMAIN_UNKNOWN, question_ref, unk_ref}`,
  **nunca** um id. Nenhuma camada (`map_layer`) que implique autoria
  institucional é atribuída aos Mapas A/B.
- `CMY-09` "Quem fez os mapas?" nasce `PERMANENTLY_AMBIGUOUS`, com
  `question_ref: Q-MAP-AUTHOR`.
- Os "entrões" são atores como quaisquer outros: suas buscas são **staging e
  movimento** validados fisicamente (onde vão, quanto leva, o que conhecem,
  que acesso têm a arquivos e a lugares fechados). O motor garante que as
  buscas sejam **fisicamente coerentes**; não garante nem impede que achem
  pistas.
- Eventos de busca usam `kind: [PROVENANCE_INQUIRY]` no ledger. Cada um pode
  produzir evidência (`EVD-*`, com suporte a qualquer interpretação) e
  **jamais** resolução: nenhum `knowledge_delta` de nenhum conhecedor
  (personagem ou `READER`) pode ensinar quem fez os mapas
  (`MY-08 MAP_AUTHOR_REVEALED`, BLOCKER).
- Se **existe** uma verdade sobre a autoria no mundo (um `GT-*` com
  `reader_access: NEVER`, como o `GT-NAR-01` de Narciso) é decisão do canon
  narrativo; a cartografia **não sabe** e não tem como saber.
- O que **pode** ser dito, por serem fatos físicos e não de autoria: onde os
  exemplares estão, quem os teve a cada capítulo (`owner_by_chapter`), o estado
  do papel/adulteração se o canon o declarar.
- As demais alegações dos mapas (lemas, alegações de placas) **não** herdam
  autor: continuam `OFFICIAL_CLAIM` de um artefato de autoria desconhecida.
  "Official" aqui significa "alegação que o mapa faz", não "governo de Redmur".

**Limite do desenho:** o teto `max_never_questions: 3` do canon interpretativo
(`check_interpretive_canon.py:157`, ajustável em
`BOOK_SPEC.features.living_theory.thresholds`) pode ser ultrapassado, porque o
DEDR (§33.3) já usa 3 perguntas `NEVER` para SEM ROSTO. Ver `OQ-CART-20`.

---

## 23. Actor Knowledge

### 23.1 Princípio (missão §21)

`WORLD TRUTH ≠ CHARACTER KNOWLEDGE ≠ READER KNOWLEDGE.` O motor guarda a
primeira; projeta as outras duas.

### 23.2 Níveis

| Nível | Significa | Permite |
|---|---|---|
| `EXISTS` | sabe que o lugar/passagem existe | mencionar |
| `ACCESS` | sabe onde fica a entrada | chegar à entrada |
| `ROUTE` | sabe percorrer | usar em `reachable`/rotas |
| `FAMILIAR` | percorre com facilidade (inclusive no escuro) | sem fator "não familiar"; fator noturno menor |

### 23.3 Fontes (REUSE, zero mudança no ledger)

```yaml
# books/sem-rosto/cartography/seeds/KNOWLEDGE_BASELINE.seed.yaml   (estado no capítulo 0)
baseline:
  - knower: PUBLIC                   # todo ator herda
    knows: {ROUTE: "*public_knowledge in [PUBLIC]*"}      # seletor projetado, não lista manual
  - knower: INST-CIVIC-PRESERVATION  # ilustrativo — id real vem do registry da obra
    knows: {EXISTS: [RM-SUB-STD], ROUTE: [EDG-P-005, EDG-S-006]}
    source: "a definir pelo canon narrativo"
  - knower: CHR-P
    knows: {ROUTE: [RTE-A-R2]}
```

Aprendizado durante o livro = `knowledge_delta` do ledger, com os ids da
cartografia em `learns` (o ledger aceita qualquer id em `learns` e só
restringe `GT-*`, `check_causal_ledger.py:761-763`):

```yaml
# CAUSAL_LEDGER.yaml
- id: EV-44
  chapter: 12
  knowledge_delta:
    - {knower: CHR-P, learns: [EDG-S-002, "CART:EXISTS:RM-SUB-STD"]}   # id puro = ROUTE; prefixo = nível
    - {knower: READER, learns: [EDG-S-002]}
```

O exemplo da missão fica assim: a protagonista conhece a estrada da Old
Quarry (`PUBLIC`); a instituição conhece o `EDG-P-003` (Quarry Crawlspace);
um Manfred (id do canon narrativo) conhece `EDG-S-007`; o leitor não conhece
nada disso até um `knowledge_delta` de `READER` (ou paratexto).

### 23.4 Crença baseada em artefato

Um ator que **viu** um mapa (`artifact_seen: [{artifact: MAP-OFF-MODERN-01,
from_chapter: 3}]`) pode planejar com `planned_on: BELIEF:MAP-OFF-MODERN-01`:
o planejamento usa o grafo **como o artefato o descreve** (inclusive estradas
`PHANTOM`), e a validação física roda contra o grafo real. Resultado: o
motor distingue "a personagem tentou uma estrada que não existe e deu num
beco" (narrativa legítima, `INFO PLANNED_ON_FALSE_BELIEF`) de "a personagem
atravessou por onde não há estrada" (`FAIL TR-06`).

### 23.5 Regras

- `KN-01 SECRET_ROUTE_UNKNOWN_TO_ACTOR` (FAIL, INV-C04).
- `KN-03 KNOWLEDGE_UNSOURCED` (HIGH): o baseline dá a um ator conhecimento de
  aresta `HIDDEN` sem `source`.
- Perseguidor nunca usa aresta que não conhece (`CH-02`).
- Instituição conhecer ≠ todo membro conhecer: agentes individuais de uma
  instituição só herdam o conhecimento dela se o canon declarar `member_of`
  com `inherits_knowledge: true`.

---

## 24. Temporal Cartography

### 24.1 Dois eixos de tempo, nunca misturados

| Eixo | Unidade | Campos | Exemplo |
|---|---|---|---|
| **Histórico** | ano do mundo | `valid_from`, `valid_until` em nós, arestas, nomes, endereços | estrada que existiu de 1891 a 1928 |
| **Narrativo** | capítulo + relógio de cena | `state_timeline` (fold de `mutations[]`), `STAGING.at` | Burn Bridge desaba no capítulo 19 |

- O **presente físico** é o ano presente da história (`story_present_year`,
  dono: TIMELINE — hoje `UNKNOWN`). Uma consulta sem `--at-year` responde
  para o presente; com `--at-year 1900`, filtra `valid_from/valid_until`.
- Entidade com `valid_until < story_present_year` **não é navegável** no
  presente, mas continua no grafo (pode ser depictada por artefatos,
  procurada, escavada). É assim que "a estrada de 1891 aparece no mapa
  histórico mas não existe em 2026" (missão §23) é representável.
- `CN-04 HISTORICAL_OVERRIDES_PRESENT` (BLOCKER): um estado de camada
  histórica nunca altera `state_timeline`; o inverso também.

### 24.2 Estado por capítulo

`state(entity, chapter)` = último `state` de `state_timeline` com
`from_chapter ≤ chapter`, onde `state_timeline` é **gerado** das mutações
aprovadas (seção 26). Estados de aresta: `OPEN · RESTRICTED · BLOCKED ·
COLLAPSED · FLOODED · SEALED · DESTROYED · UNKNOWN`. Estados de lugar: os
de `status` (seção 12).

---

## 25. Historical Maps

### 25.1 Camadas reservadas (missão §24)

| id | Nome | Era | Autor | Estado |
|---|---|---|---|---|
| `LYR-VICTORIAN` | Victorian Map | `UNKNOWN` | `UNKNOWN` | `RESERVED` |
| `LYR-PRE-COFFER` | Pre-Coffer Map | `UNKNOWN` — a data de início dos Cofres é do canon narrativo e pode tocar pergunta `NEVER` do DEDR (Q-ORIGIN) | `UNKNOWN` | `RESERVED` |
| `LYR-EARLY-PRESERVATION` | Early Preservation Map | `UNKNOWN` | `INST-*` a definir | `RESERVED` |
| `LYR-MODERN-OFFICIAL` | Modern Official Map | presente | `INST-CIVIC-PRESERVATION` (a definir) | `RESERVED` — **não** é a camada dos Mapas A/B (a autoria deles é `MUST_REMAIN_UNKNOWN`, 22.7) |
| `LYR-UNDERGROUND-MAINTENANCE` | Underground Maintenance Map | `UNKNOWN` | `UNKNOWN` | `RESERVED` |
| `LYR-PRIVATE-MANFRED` / `LYR-PRIVATE-FLARRY` | Private Family Maps | `UNKNOWN` | famílias (canon narrativo) | `RESERVED` |
| `LYR-RELIGIOUS` | Religious Records Map | `UNKNOWN` | paróquia de Saint Morrow (a definir) | `RESERVED` |

Uma camada `RESERVED` existe como id (para ser referenciada por mistérios e
propostas) e **não tem conteúdo**. Conteúdo só por proposta.

### 25.2 Contrato de artefato (missão §33)

```yaml
- id: MAP-HIST-0001
  title: null
  author: null                # CHR-* | INST-* | UNKNOWN
  date: null                  # ano do mundo
  source: null                # onde o objeto está/estava (lugar RM-* ou "OFF_MAP")
  map_layer: LYR-VICTORIAN
  version: 1
  supersedes: null
  accuracy: UNKNOWN           # SURVEYED | SKETCH | SCHEMATIC | PROPAGANDA | UNKNOWN
  tampering_status: UNKNOWN   # NONE | ALTERED | FORGED | PARTIALLY_DESTROYED | UNKNOWN
  missing_sections: []        # regiões (polígono em RCG) ausentes/rasgadas
  annotations: []             # [{text, by: CHR-*|UNKNOWN, px|rcg, date}]
  depicts: []                 # relações (22.2)
  owner_by_chapter: []        # [{from_chapter, owner}]
  reader_seen: null           # PROJETADO (primeiro capítulo em que o leitor o vê)
  associated_mysteries: []    # CMY-*/RMY-*
  physical_copies: 1
```

"Mapas rabiscados, históricos, Manfred, Flarry, da igreja, de manutenção"
(missão §33) são instâncias deste contrato.

---

## 26. Canon Mutation Rules

### 26.1 Duas vias

| Tipo de decisão | Via | Por quê |
|---|---|---|
| **Fundacional, pré-escrita** (escala regional, âncoras, classificação de anomalias, posição de Black Thistle, tipos novos) | `books/sem-rosto/cartography/approvals/CART_DECISION_<n>.md` com `subject_sha256` do seed afetado (padrão `authors/bea_halden/approvals/AUTHOR_DNA_v1.md`) | `CANON_PROPOSAL.schema.json` exige `source_chapter` 1..30 (D-CART-07) |
| **Nascida na narrativa** (ponte desaba, passagem descoberta, esconderijo comprometido, lugar novo recorrente) | `CANON_PROPOSAL` (REUSE, inalterado) + `mutations[]` estruturado na cartografia | dono único `CANON_GUARDIAN`; `unapproved_facts_are_canon: false` |

### 26.2 Contrato de mutação (missão §22)

```yaml
mutations:
  - id: CMUT-0007
    proposal_ref: CP-0043           # CANON_PROPOSAL aprovada (texto humano do fato)
    cause: EV-58                    # evento do ledger que causa a mudança física
    chapter: 19
    at: "D041T04:10"
    target: RM-URB-BBR
    field: status
    previous_state: ACTIVE
    new_state: DESTROYED
    effects:                        # arestas afetadas, derivadas ou declaradas
      - {edge: EDG-U-040, previous_state: OPEN, new_state: DESTROYED}
      - {edge: EDG-U-041, previous_state: OPEN, new_state: DESTROYED}
    approval: {decided_by: CANON_GUARDIAN, date: 2026-10-02}
    canon_effective_from: {chapter: 19, at: "D041T04:10"}
```

### 26.3 Regras

- `CN-02 MUTATION_WITHOUT_PROPOSAL` (BLOCKER): mudança de estado sem
  `proposal_ref` aceita.
- `CN-03 MUTATION_WITHOUT_CAUSE` (HIGH): mudança física sem `cause` no ledger
  (uma ponte não desaba sozinha — ou desaba, e então o evento "a ponte
  desabou" existe no ledger).
- `CN-07 RETROACTIVE_MUTATION` (BLOCKER): `canon_effective_from` anterior a
  um staging `REALIZED` que usou o estado antigo.
- `previous_state` precisa ser o estado projetado no ponto de efeito (mesmo
  princípio do `relationship_delta.from` do ledger).
- `CN-06 RENAME_WITHOUT_PROPOSAL`: `canonical_name` difere do snapshot da
  wave anterior sem mutação.
- A cartografia **nunca é editada no lugar**: o estado atual é sempre
  `fold(seed, mutations)`. O seed só muda por decisão fundacional versionada.

Exemplo da missão ("uma ponte desaba"): não se escreve
`Burn Bridge = destroyed`. Registra-se `CMUT-0007` acima. Consequências
automáticas: a partir do capítulo 19, `reachable(RM-CEN-SMC, RM-URB-ERC)`
deixa de encontrar caminho pela ponte; qualquer staging posterior que cruze
o Ash Burn por ali reprova `AC-01`; o Ash Burn passa a separar a margem leste
(Pumping Station, Reservoir, East Road) do núcleo **até que outra travessia
exista** — e a análise de gargalos (seção 28.3) mostra isso antes da escrita.

---

## 27. Scene Integration

### 27.1 Cartography Context Pack (missão §29)

Gerado **deterministicamente** (zero token de modelo) antes da escrita de
todo capítulo cujo brief declara staging:

```bash
python scripts/check_cartography.py --runtime . --pack --chapter 7 [--scene SC-07-02]
```

Saída: `briefs/cartography/CHAPTER_07_PACK.yaml`, lido pelo `CHAPTER_WRITER`
e pelo `SCENE_ARCHITECT` junto com o brief. O pack **ajuda sem decidir**: ele
lista o que é possível e o que é proibido; a cena escolhe.

```yaml
scene: SC-07-02
pov: CHR-P
chapter: 7
at: "D014T23:14"
conditions: {lighting: NIGHT_DARK, weather: RAIN}
current_location: {id: RM-CEN-CHP, name: Saint Morrow Chapel, type: CHAPEL, status: ACTIVE}
adjacent_locations:                      # superfície, arestas abertas neste capítulo
  - {id: RM-URB-OPC, via: EDG-U-110, walk_expected: "9–13 min", visible_exit: true}
  - {id: RM-CEN-OCP, via: EDG-U-115, walk_expected: "8–11 min", visible_exit: true}
visible_exits: [EDG-U-110, EDG-U-115, EDG-U-116]
hidden_exits_known_by_pov:               # só o que o POV conhece
  - {edge: EDG-P-001, to: RM-SUB-CHB, level: ACCESS}
hidden_exits_unknown_to_pov: 1           # CONTAGEM apenas — o escritor sabe que existe algo,
                                         # não o quê; detalhes em engine_notes se autorizado
approximate_distances:
  - {to: RM-URB-OPC, euclid_m: [520, 760]}
  - {to: RM-CEN-SMC, euclid_m: [890, 1010]}
pursuit_routes: []                       # preenchido se houver CHS-* na cena
dead_ends: []                            # nós de grau 1 alcançáveis em ≤ 5 min que não são saída nem esconderijo
cover: {at_location: MEDIUM, along_exits: {EDG-U-110: LOW}}
surveillance: {at_location: UNKNOWN}
underground_access: {known_to_pov: [EDG-P-001], state: UNKNOWN}
weather_effects: ["RAIN ×1,10 em deslocamento", "NIGHT_DARK: detecção de figura ≤ 30 m"]
canon_constraints:
  - "Nenhuma travessia do Ash Burn fora de Burn Bridge."
  - "Root Cellar Hideout é o único esconderijo registrado."
  - "O POV NÃO conhece EDG-S-002; não usar a passagem cripta–capela nesta cena."
forbidden:                               # o que reprovará no gate
  - {code: KN-01, detail: "usar EDG-S-002 / EDG-S-003"}
  - {code: KN-02, detail: "nomear 'Storm Drains' (first_allowed_reveal: capítulo 12)"}
reader_state: {RM-SUB-CHB: UNSEEN, RM-URB-OPC: VISITED}
engine_notes: null                       # só com --engine-view (CANON_GUARDIAN/LEAD_NOVELIST autorizado)
mystery_notice: "Saídas regionais: ver --exits. A cartografia não conhece a saída verdadeira."
```

### 27.2 Integração com os demais componentes (PHASE 5)

| Componente | Integração | Tipo |
|---|---|---|
| Scene planner (`SCENE_ARCHITECT`, `BRIEFING_ARCHITECT`) | escrevem staging `PLANNED`; recebem o pack; consultam `reachable`, `escape_routes`, `visible_from` | REUSE de agentes + CLI |
| Chapter planner (`chapter_architecture.yaml`, `T016_PLOT_DEPENDENCY_MAP`) | lugares por capítulo passam a ser ids `RM-*`; `--chapter-plan` verifica que a sequência de lugares é percorrível no tempo entre capítulos | EXTEND de dados |
| Canon (`CANON_GUARDIAN`, `T018_CANON_REGISTRY`) | nova tarefa `T018C_CARTOGRAPHY` materializa seeds + mutações em `/canon/cartography/` | EXTEND do compose (S5) |
| Memory | snapshots por wave (`canon/snapshots/CARTOGRAPHY.WAVE_nn/`); `--baseline` compara wave a wave (renomeação, mutação retroativa) | REUSE do padrão |
| Mystery / truth ledger | `truth_ref`, `question_ref`, `EVD-*` em `clue_ids`; MYSTERY PRESERVATION GATE | REUSE |
| Narrative validator (`check_canon_continuity.py`) | nomes e aliases da cartografia entram no vocabulário canônico; lugar novo recorrente sem proposta vira achado | EXTEND (1 função) |
| Revisores (`PLOT_CONTINUITY_REVIEWER`, `WORLD_RULES_REVIEWER`, `REALISM_ENGINEER`) | recebem o relatório de wave da cartografia; julgam o que o validador marcou `WARNING`/`INFO` | REUSE |
| Mídia (`MEDIA_MANIFEST.entities.locations`) | ids de local da mídia = ids `RM-*`; `check_media_handoff.py` pode validar existência | REUSE de id |
| Digest (`build_canon_digest.py`) | bloco compacto: id, nome, tipo, zona, d. cruz | EXTEND opcional |

---

## 28. Chase Integration

### 28.1 Modelo (missão §30)

Perseguição é validada por **janelas de chegada em nós**, não por simulação
contínua.

```yaml
chases:
  - id: CHS-0003
    chapter: 15
    scene: SC-15-03
    start_at: "D031T22:40"
    lighting: NIGHT_MOON
    target:   {actor: CHR-P, start: RM-CEN-CHP, route: [EDG-P-001, EDG-S-001, EDG-S-003, EDG-S-004, EDG-P-004], profile: FIT}
    pursuer:  {actor: CHR-X, start: RM-CEN-OCP, route: null, profile: FIT}      # null = melhor rota conhecida
    initial_gap_m: 120
    initial_visibility: VISIBLE
    declared_events:                    # o que a prosa afirma
      - {at_node: RM-JCT-S1, claim: PURSUER_LOSES_SIGHT}
      - {at_node: RM-URB-RCH, claim: TARGET_REACHES_HIDEOUT}
```

### 28.2 Cálculo

Para cada nó `n` da rota de cada um: `earliest(n)` (velocidade de máximo
esforço, até 400 m, depois sustentada) e `latest(n)` (sustentada com
modificadores). Derivados:

| Conceito da missão | Derivação |
|---|---|
| POSITION / VELOCITY | janela `[earliest, latest]` por nó; velocidade do perfil e do modo |
| ROUTE | declarada ou melhor rota **conhecida pelo ator** |
| VISIBILITY | `visible_from(pursuer_pos, target_pos)` nos nós de ambas as rotas no mesmo intervalo |
| DISTANCE | intervalo de distância ao longo do grafo entre as janelas |
| INTERCEPT_POINTS | nós comuns onde `earliest_pursuer(n) ≤ latest_target(n)` |
| ESCAPE_POINTS | nós onde o alvo acessa aresta que o perseguidor **não conhece** (portal oculto, passagem) |
| BOTTLENECKS | pontes (arestas-ponte do grafo) e **pontos de articulação** (Tarjan) no subgrafo permitido — ex.: Burn Bridge para a margem leste |
| DEAD_ENDS | nós de grau 1 que não são saída aparente, portal ou esconderijo |
| HIDDEN_TRANSITIONS | arestas `UNDERGROUND`/`HIDDEN` na rota do alvo |

### 28.3 Regras

| Código | Severidade | Condição |
|---|---|---|
| `CH-01 CHASE_TELEPORT` | FAIL | alvo ou perseguidor aparece em nó fora da própria janela alcançável |
| `CH-02 PURSUER_SECRET_ROUTE` | FAIL | perseguidor usa aresta que não conhece |
| `CH-03 GAP_CLOSURE_IMPOSSIBLE` | FAIL | a prosa fecha a distância mais rápido que a diferença máxima de velocidades permite |
| `CH-04 INTERCEPT_IMPOSSIBLE` | FAIL | interceptação declarada num nó sem sobreposição de janelas |
| `CH-05 LOS_REACQUIRE_UNJUSTIFIED` | WARNING | perseguidor "volta a ver" o alvo onde `visible_from` é `NOT_VISIBLE` |
| `CH-06 ESCAPE_THROUGH_UNKNOWN` | FAIL | fuga por aresta que o alvo não conhece (é `KN-01` no contexto de perseguição) |
| `CH-07 BOTTLENECK_IGNORED` | INFO | rota do alvo passa por gargalo com perseguidor mais próximo dele — tensão que a cena talvez queira usar |

O motor não decide quem vence a perseguição; decide o que é **fisicamente
coerente** e aponta onde está a tensão (gargalos, pontos de fuga).

---

## 29. Validation Gates

### 29.1 Validadores e gates (REUSE de `custom_validators` + `gate_extensions`)

| Validador | Comando | Gate | Famílias |
|---|---|---|---|
| `V_CARTO_CANON` | `check_cartography.py --runtime . --mode canon` | `GATE_CANON` | `CG`, `CX`, `MY`, `CN-01/04/05/06`, fontes, schema |
| `V_CARTO_WAVE_n` | `--mode wave --through-chapter N --baseline canon/snapshots/CARTOGRAPHY.WAVE_nn` | `GATE_WAVE_n` | `TR`, `AC`, `KN`, `VS`, `HD`, `CH`, `CN-02/03/07` sobre stagings `REALIZED` até N |
| `V_CARTO_FINAL` | `--mode final` | `GATE_FULL_MANUSCRIPT` | tudo + `KN-02` sobre o manuscrito inteiro |
| pack (não bloqueante) | `--pack --chapter N` | tarefa de brief | gera `CHAPTER_NN_PACK.yaml`; falha de geração bloqueia o brief |

Sem gate novo: o DAG do motor já tem os pontos de parada certos (canon antes
da escrita, cada wave depois da escrita, manuscrito no fim).

### 29.2 Severidades

`BLOCKER` e `FAIL`/`HIGH` reprovam o gate; `WARNING`/`MEDIUM` vão ao relatório
e ao `EXECUTIVE_EDITOR`; `INFO` só ao relatório. Mapeamento para o enum do
motor (`INFO LOW MEDIUM HIGH BLOCKER`): `FAIL` = `HIGH`, `WARNING` = `MEDIUM`.

### 29.3 Catálogo de regras

| Família | Código | Sev. | Regra |
|---|---|---|---|
| **CG** integridade | `CG-01 EDGE_DANGLING` | BLOCKER | `from`/`to` inexistente (INV-C01) |
| | `CG-02 DUPLICATE_ID` | BLOCKER | |
| | `CG-03 ORIGIN_NOT_ZERO` | BLOCKER | `RM-CEN-SMC` ≠ (0, 0, 0) |
| | `CG-04 UNKNOWN_TYPE` | HIGH | tipo fora do vocabulário + extensões aprovadas |
| | `CG-05 COORD_WITHOUT_SOURCE` | HIGH | coordenada sem `source_px` + `XFM`, ou sem proposta |
| | `CG-06 SOURCE_HASH_MISMATCH` | BLOCKER | PNG pinado mudou |
| | `CG-07 CROSS_LAYER_WITHOUT_PORTAL` | BLOCKER | aresta liga `SUBTERRANEAN` a outra camada sem ser `PORTAL` |
| | `CG-08 INVENTORY_ITEM_UNMAPPED` | BLOCKER | item do inventário de transcrição (seção 38) sem nó, entrada de registro ou artefato |
| | `CG-09 NAME_COLLISION` | BLOCKER | |
| | `CG-10 ORPHAN_NODE` | MEDIUM | nó `POINT` sem aresta (exceto `AUTHOR_DECLARED` sem posição, `OFF`, `UNL`) |
| | `CG-11 ADJACENCY_DRIFT` | HIGH | lista de vizinhos armazenada diverge das arestas |
| | `CG-12 REGISTER_DRIFT` | BLOCKER | registro difere da transcrição literal |
| **CX** física | `CX-01 WATER_CROSSING_WITHOUT_STRUCTURE` | BLOCKER | INV-C02 |
| | `CX-02 SUBTERRANEAN_WITHOUT_PORTAL` | BLOCKER | componente conexo subterrâneo sem portal (INV-C03) |
| | `CX-03 TUNNEL_SHORTER_THAN_ANCHORS` | HIGH | |
| | `CX-04 EDGE_SHORTER_THAN_EUCLID` | HIGH | |
| | `CX-05 SUPERNATURAL_ASSERTED` | BLOCKER | campo/tipo/estado que implique teletransporte, portal mágico, geometria impossível sem decisão canônica (INV-C00) |
| **TR** viagem | `TR-01`…`TR-07` | 17.7 | |
| **AC** acesso | `AC-01 CLOSED_TRAVERSAL_WITHOUT_ACTION` | HIGH | INV-C06 |
| | `AC-02 HOURS_VIOLATION` | MEDIUM | |
| **KN** conhecimento | `KN-01 SECRET_ROUTE_UNKNOWN_TO_ACTOR` | HIGH | INV-C04 |
| | `KN-02 READER_MAP_LEAK` | HIGH | |
| | `KN-03 KNOWLEDGE_UNSOURCED` | HIGH | |
| **VS** visibilidade | `VS-01`, `VS-02 UNDERGROUND_SIGHT`, `VS-03` | HIGH/HIGH/MEDIUM | seção 16 |
| **HD** esconderijo | `HD-01`…`HD-04` | HIGH | seção 18 |
| **CH** perseguição | `CH-01`…`CH-07` | 28.3 | |
| **MY** mistério | `MY-01 HIDDEN_ANSWER_PRESENT` | BLOCKER | |
| | `MY-02 TRUE_EXIT_ASSERTED` | BLOCKER | INV-C07 |
| | `MY-03 ROUTE_MYSTERY_INTERPRETED` | BLOCKER | RMY/CMY com interpretação promovida a fato ou `resolution_state` sem `truth_ref` (INV-C08) |
| | `MY-04 PATTERN_WITHOUT_LEDGER` | BLOCKER | |
| | `MY-05 TRUTH_REF_UNRESOLVED` | HIGH | |
| | `MY-06 ANOMALY_USED_AS_CLUE` | HIGH | |
| | `MY-07 TRUTH_CONTENT_COPIED` | BLOCKER | |
| | `MY-08 MAP_AUTHOR_REVEALED` | BLOCKER | `author` com id, camada institucional atribuída aos Mapas A/B, ou `knowledge_delta` que ensine a autoria a qualquer conhecedor (22.7) |
| **CN** canon | `CN-01 NEW_PLACE_WITHOUT_PROPOSAL` | HIGH | INV-C09 |
| | `CN-02`, `CN-03`, `CN-07` | 26.3 | |
| | `CN-04 HISTORICAL_OVERRIDES_PRESENT` | BLOCKER | |
| | `CN-05 MAP_POSITION_CONTRADICTION` | BLOCKER | coordenada diverge da derivada de `source_px` além da precisão, ou staging/prosa afirma relação espacial contrária aos mapas (INV-C10) |
| | `CN-06 RENAME_WITHOUT_PROPOSAL` | HIGH | |

`CN-05` na prosa é detectado por **afirmações estruturadas** do staging
(`sees`, `adjacent_to`, `bearing_claim`: "a capela fica ao norte do pub") —
não por leitura de linguagem natural. O resto é julgamento de
`PLOT_CONTINUITY_REVIEWER` com o relatório na mão.

---

## 30. Invariants

| Invariante | Enunciado | Regra(s) |
|---|---|---|
| **INV-C00** | `PHYSICAL_REALISM = TRUE`: nenhum teletransporte, portal, estrada móvel, geometria impossível ou fenômeno sobrenatural sem decisão canônica explícita. Redmur pode *parecer* assombrada; o espaço é coerente | `CX-05`, `TR-05` |
| **INV-C01** | Toda aresta conecta dois nós existentes | `CG-01` |
| **INV-C02** | Nenhuma rota atravessa água sem ponte, vau, túnel, bueiro ou barco canônico | `CX-01` |
| **INV-C03** | Toda passagem subterrânea pertence a um componente com entrada física (portal) | `CX-02`, `CG-07` |
| **INV-C04** | Nenhum personagem usa rota secreta que ainda não conhece | `KN-01`, `CH-02`, `CH-06` |
| **INV-C05** | Nenhum deslocamento em tempo menor que o mínimo físico | `TR-01` |
| **INV-C06** | Local/aresta fechado só é atravessado com ação narrativa correspondente (evento do ledger) | `AC-01` |
| **INV-C07** | Nenhuma saída verdadeira é inferível pelo motor (o enum não a representa; o grafo termina na moldura) | `MY-02` |
| **INV-C08** | Rotas enigmáticas não são interpretadas automaticamente | `MY-03`, `MY-04` |
| **INV-C09** | Nenhum lugar recorrente novo entra na narrativa sem proposta canônica | `CN-01`, `HD-01` |
| **INV-C10** | Nenhuma cena contradiz o posicionamento dos dois mapas canônicos | `CN-05`, `CG-05`, `CG-06` |
| **INV-C11** | A cartografia não guarda verdade narrativa, só ponteiros | `MY-01`, `MY-05`, `MY-07` |
| **INV-C12** | Estado histórico e estado presente nunca se sobrescrevem | `CN-04` |
| **INV-C13** | O estado presente é sempre `fold(seed, mutações aprovadas)` | `CN-02`, `CN-07` |
| **INV-C14** | Anomalia `UNDECIDED` não é pista nem correção | `MY-06`, `CG-06` |
| **INV-C15** | Coordenadas são derivadas de fonte + transformação, nunca digitadas | `CG-05`, `CN-05` |

---

## 31. Data Contracts

### 31.1 Arquivos

| Caminho | Natureza | Dono |
|---|---|---|
| `docs/sdd/REDMUR_CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md` | este documento | — |
| `engine/contracts/CARTOGRAPHY.schema.json` | JSON Schema 2020-12 de todos os seeds/canon | motor |
| `engine/templates/CARTOGRAPHY_TEMPLATE.yaml` | template neutro (lugares fictícios A/B/C) | motor |
| `engine/scripts/check_cartography.py` | validador + biblioteca de consultas (stdlib + PyYAML) | motor |
| `books/sem-rosto/README.md` | declara o pacote **parcial** (só cartografia) | obra |
| `books/sem-rosto/cartography/sources/SOURCES.yaml` + 2 PNGs | fontes pinadas + transformações `XFM-*` | obra |
| `books/sem-rosto/cartography/seeds/CARTOGRAPHY.seed.yaml` | manifesto (`apiVersion`, `kind: CartographyCanon`, `includes`, `type_extensions`, `mutations: []`) | obra |
| `…/seeds/LOCATIONS.seed.yaml` | nós, água, áreas (L1, L2, L3, OFF, FRM, JCT) | obra |
| `…/seeds/EDGES.seed.yaml` | arestas + `ROAD-*` | obra |
| `…/seeds/ROUTES.seed.yaml` | `RTE-*` | obra |
| `…/seeds/SUBTERRANEAN.seed.yaml` | nós `SUB`, arestas `EDG-S-*`, portais `EDG-P-*` | obra |
| `…/seeds/ADDRESSES.seed.yaml` | vazio no início | obra |
| `…/seeds/VISIBILITY.seed.yaml` | `SGT-*` + limiares aprovados | obra |
| `…/seeds/HIDEOUTS.seed.yaml` | `HID-RCH` | obra |
| `…/seeds/BOUNDARIES.seed.yaml` | `BND-*`, `EXT-*` | obra |
| `…/seeds/MYSTERIES.seed.yaml` | `RMY-*`, `CMY-*`, registro | obra |
| `…/seeds/ARTIFACTS.seed.yaml` | `MAP-*` (textos, glifos do inset, ornamentos, artefatos diegéticos) | obra |
| `…/seeds/LAYERS.seed.yaml` | `LYR-*` reservadas | obra |
| `…/seeds/ANOMALIES.seed.yaml` | `ANM-*`, `GLY-*`, `UNL-*` | obra |
| `…/seeds/KNOWLEDGE_BASELINE.seed.yaml` | conhecimento no capítulo 0 | obra |
| `…/approvals/CART_DECISION_*.md` | decisões fundacionais | autora |
| `tests/fixtures/cartography/` | mini-mundo neutro (8 nós, 1 rio, 1 ponte, 1 túnel, 1 saída aparente) | testes |
| `tests/test_cartography.py` | testes da capability | testes |
| `tests/test_redmur_cartography.py` | testes dos dados de SEM ROSTO | testes |

Mapeamento para os caminhos sugeridos na missão §36: `canon/redmur/*.yaml` →
`books/sem-rosto/cartography/seeds/*.seed.yaml` (seed na obra, canon no
runtime — padrão Narciso); `schemas/redmur_cartography.schema.json` →
`engine/contracts/CARTOGRAPHY.schema.json` (convenção do motor, neutro);
`validators/redmur_cartography_validator.*` → `engine/scripts/check_cartography.py`;
`tests/test_redmur_cartography.*` → mantido.

### 31.2 Manifesto

```yaml
apiVersion: pedroarte.livingbooks/v1
kind: CartographyCanon
metadata:
  project_id: sem-rosto
  version: 0.1.0
  owner: CANON_GUARDIAN
  grid: {name: REDMUR_CANONICAL_GRID, origin: RM-CEN-SMC, units: m, axes: {x: EAST, y: NORTH, z: UP_REL}}
  sources: sources/SOURCES.yaml
  transforms: {SRC-MAP-A: XFM-A@v1, SRC-MAP-B: XFM-B@S7.25}      # OQ-CART-01 decidida: escala 55,86 m/px
includes: [LOCATIONS, EDGES, ROUTES, SUBTERRANEAN, ADDRESSES, VISIBILITY, HIDEOUTS,
           BOUNDARIES, MYSTERIES, ARTIFACTS, LAYERS, ANOMALIES, KNOWLEDGE_BASELINE]
type_extensions: [LANDMARK, TRANSPORT_STOP, UTILITY, MOUNTAIN, STANDING_STONES, MILL, ABBEY,
                  JUNCTION, FRAME_PORTAL, OFF_MAP_DESTINATION]
settings:                                # limiares aprovados (OQ-CART-14)
  speeds: {...}
  detection_thresholds_m: {...}
mutations: []
mutation_log: []
```

### 31.3 Schema

`CARTOGRAPHY.schema.json` define: `Location`, `Edge`, `Road`, `Route`,
`Address`, `Sightline`, `Hideout`, `Boundary`, `Exit`, `RouteMystery`,
`CartographicMystery`, `RegisterEntry`, `MapArtifact`, `Layer`, `Anomaly`,
`Staging`, `Movement`, `Chase`, `Mutation`, `KnowledgeBaseline`. Regras que
JSON Schema não expressa (referências cruzadas, geometria, tempo,
conhecimento) ficam no validador — mesmo corte do ledger e do canon
interpretativo. `additionalProperties: false` em tudo (o que também dá a
primeira barreira de `MY-01`: um campo `true_exit` nem passa pelo schema).

### 31.4 CLI e biblioteca

```text
check_cartography.py --runtime <rt> | --canon <dir>
  --mode canon|wave|final [--through-chapter N] [--baseline <snapshot>]
  --json --out <arquivo>
consultas (todas aceitam --chapter N --at <Dddd THH:MM> --actor <id> --mode <modo> --conditions k=v,...):
  --distance A B          --bearing A B           --time A B
  --reachable A B         --route A B [--shortest|--safest|--hidden]
  --escape-routes A       --visible A B           --known-routes ACTOR
  --reader-map            --exits                 --exit-truth [--engine-view --authorized-by GT-*]
  --pack --chapter N      --chase CHS-*           --bottlenecks [--layer L]
  --state ENTITY          --at-year YYYY          --explain   (fatores de cada veredito)
```

A mesma lógica é importável (`from check_cartography import load, reachable,
travel_times, visible_from, ...`) — o validador **é** a biblioteca, como
`knowledge_state` no ledger.

---

## 32. Persistence

- **YAML em disco, versionado em git.** Sem banco de dados, sem serviço, sem
  índice externo: o grafo de Redmur tem ordem de 10² nós e 10³ arestas;
  Dijkstra e Tarjan em Python puro respondem em milissegundos.
- **Seeds** (obra) → **canon** (runtime) por `T018C_CARTOGRAPHY`
  (`CANON_GUARDIAN`, lock `CANON_WRITE`), igual a `T018N_INTERPRETIVE_CANON`
  de Narciso.
- **Coordenadas em metros** são **cache** calculado de `source_px` + `XFM-*`
  e gravado no runtime com o hash da transformação; o validador recalcula e
  compara (`CN-05`).
- **Snapshots** por wave em `canon/snapshots/CARTOGRAPHY.WAVE_nn/` (cópia do
  diretório + `STAGING.yaml`), base de `--baseline`.
- **Relatórios** em `reports/cartography/{CANON,WAVE_nn,FINAL}.{json,md}`.
- **Packs** em `briefs/cartography/CHAPTER_NN_PACK.yaml` (regeneráveis; nunca
  editados à mão).
- Ordem estável em toda saída (ids ordenados) → diffs legíveis e testes
  golden possíveis.

## 33. Observability

| Sinal | Onde |
|---|---|
| Resumo por execução: nº de nós/arestas por camada, `PROVISIONAL`, `UNSPECIFIED`, anomalias por estado | cabeçalho do relatório |
| Achados por família e severidade, com `evidence` (ids, números) e `recommended_action` | formato `REVIEW_FINDING` do motor |
| Proveniência de cada coordenada (`source_px`, `XFM`, precisão) | `--explain` e relatório |
| Explicação de cada veredito de viagem: caminho, comprimento min/nominal, velocidades, modificadores | `--explain` |
| Cobertura de transcrição: itens do inventário × entidades | relatório `CANON` (`CG-08`) |
| Custo | zero chamadas de modelo; tempo de execução no relatório (o motor já registra custos com `log_cost.py`; este validador registra `tokens: 0`) |
| Mapa de calor capítulo × lugar (quais lugares a obra usa, quais nunca) | `--heatmap` (espelha `check_interpretive_canon.py --heatmap`) |

## 34. Failure Modes

| Modo de falha | Efeito | Mitigação |
|---|---|---|
| Erro de transcrição (rótulo mal lido, ícone deslocado) | canon errado com aparência de certeza | Apêndice A com pixel e recorte de cada item; confiança por item; conferência humana obrigatória no S1/S2; `source_px` sempre presente |
| Precisão falsa | cenas bloqueadas por números inventados | intervalos em toda distância; `FAIL` só com o **mínimo** físico; tortuosidade estimada nunca reprova |
| Escala regional decidida errado | tempos regionais errados | coordenadas derivadas; trocar `XFM-B` recalcula tudo; `WARNING` até decisão |
| Anomalia de renderização canonizada como pista | mistério fabricado | `UNDECIDED` inerte por padrão (`MY-06`) |
| Anomalia intencional "corrigida" | mistério destruído | nenhuma fonte é sobrescrita; correção = nova versão pinada |
| Motor vira oráculo do mistério | leitor/escritor recebe resposta pela porta dos fundos | enum sem `TRUE_EXIT`; `HIDDEN_ANSWER_KEYS`; `truth_ref` opaco; pack com contagem de segredos, não conteúdo |
| Validador rígido demais sufoca a prosa | escritor contorna o sistema | três níveis (FAIL/WARNING/INFO); o pack mostra o possível antes; `WARNING` não bloqueia; exceção = proposta, nunca flag silenciosa |
| Deriva seed × runtime | dois estados de verdade | runtime sempre regenerado; `SOURCE_HASH_MISMATCH`, `CN-05` |
| Staging esquecido (cena escrita sem staging) | teletransporte não detectado | `V_CARTO_WAVE` exige staging `REALIZED` para toda cena com POV (lista de cenas do brief); ausência = `STAGING_MISSING` HIGH |
| Conhecimento modelado errado | personagem "sabe" o que não deveria | `KN-03` exige fonte; `knowledge_view: ACTOR` é o padrão das consultas com ator |
| Mudanças paralelas não commitadas no motor (D-CART-16) | conflito no compose | integração só no S5, após versionamento |

---

## 35. Test Strategy

### 35.1 Camadas

| Camada | Arquivo | Dados |
|---|---|---|
| Unidade da capability | `tests/test_cartography.py` | fixture neutra `tests/fixtures/cartography/` (mini-mundo sem nomes de obra) |
| Dados da obra | `tests/test_redmur_cartography.py` | seeds reais de `books/sem-rosto/cartography/` |
| Golden | `tests/fixtures/cartography/golden/` | saída de `--pack`, `--exits`, `--explain` |
| Regressão do compose | `tests/test_compose_regression.py` (existente) | `features.cartography` ausente ⇒ grafo de tarefas **idêntico** ao golden atual |

Dependências: stdlib + PyYAML + pytest (as do repositório).

### 35.2 Matriz de testes

Obrigatórios da missão §34 primeiro; `F` = fixture neutra, `R` = dados de Redmur.

| # | Teste | Dados | Regra |
|---|---|---|---|
| T01 | Saint Morrow Cross existe em (0, 0) | R | `CG-03` |
| T02 | Todo item do inventário de transcrição (seção 38) tem nó, entrada de registro ou artefato | R | `CG-08` |
| T03 | Nenhuma aresta aponta para nó inexistente | F, R | `CG-01` |
| T04 | R1, R2 e R3 existem como `RTE-A-*` com traçado desenhado | R | — |
| T05 | R4, R7, R13, R17 existem como `RTE-B-*` + `RMY-*`; R1 e R2 existem como `RMY-*` com âncora `NOT_FOUND` no Mapa B | R | — |
| T06 | A rede subterrânea é navegável só por arestas existentes; nenhum nó `SUB` alcançável sem portal | F, R | `CX-02`, `CG-07` |
| T07 | East Road começa com `OFFICIAL_CLAIM` "Officially Closed" e barreira física no X | R | — |
| T08 | South Gate Road existe com alegação "Entrada Principal" | R | — |
| T09 | Nenhum algoritmo produz `TRUE_EXIT`: varredura de todos os retornos de `--exits`, `--route`, `--reachable`, `--escape-routes` sobre todos os pares de portais de moldura | F, R | `MY-02` |
| T10 | `TRUE_EXIT` inserido num seed reprova no schema **e** no validador | F | `MY-02` |
| T11 | Mistérios não vazam o truth ledger: seed com `actual_pattern`/`verdade`/`true_exit` reprova; `truth_ref` com texto copiado do GT reprova | F | `MY-01`, `MY-07` |
| T12 | Conhecimento do ator limita rotas: `reachable` com `actor` sem `EDG-S-*` não atravessa o subsolo; o mesmo par em `ENGINE` atravessa | F, R | `KN-01` |
| T13 | Estado histórico não sobrescreve o moderno: aresta com `valid_until` < presente não é navegável no presente e aparece com `--at-year` | F | `CN-04` |
| T14 | Tempo impossível gera FAIL: Red Stag 23:14 → Old Parish Cemetery 23:18 a pé ⇒ `TR-01` | R | `TR-01` |
| T15 | Rio sem ponte reprova: aresta cruzando `WAT-ASH` fora de Burn Bridge ⇒ `CX-01` | F, R | `CX-01` |
| T16 | Túnel mais curto que a distância entre âncoras reprova | F | `CX-03` |
| T17 | Mutação sem proposta, sem causa, retroativa | F | `CN-02/03/07` |
| T18 | Burn Bridge `DESTROYED` no cap. 19 ⇒ `reachable(cruz, East Road)` muda a partir do 19 e não antes | F | 26 |
| T19 | Registro: 30 linhas, "05" duas vezes, sem "06", ordem literal | R | `CG-12` |
| T20 | Letham e Passo de Muirchéin são `NOT_ON_MAP` e não têm coordenada | R | — |
| T21 | Black Thistle Filling Station e Sealed Crypt IV existem em `SUBTERRANEAN`, sem posição e sem arestas; não aparecem no mapa do leitor nem no inset; staging neles reprova até serem conectados por proposta | R | `CX-02` isento por `UNDECLARED`; `TR-06` |
| T35 | Nenhum caminho computado liga esses dois nós à rede do inset enquanto `connectivity: UNDECLARED`; a `OMITS` do inset é registrada, mas sem atribuir causa | R | 11.6 |
| T22 | Anomalia `UNDECIDED` citada por evidência/brief reprova | F | `MY-06` |
| T23 | `RMY-*` com `resolution_state: RESOLVED` sem `truth_ref` reprova | F | `MY-04` |
| T24 | Esconderijo espontâneo reprova; `HID-RCH` aceita | F, R | `HD-01` |
| T25 | Visibilidade: subsolo nunca visível da superfície; `NIGHT_DARK` > 30 m sem luz ⇒ `NOT_VISIBLE` | F | `VS-02`, 16.3 |
| T26 | Perseguição: interceptação sem sobreposição de janelas reprova; perseguidor por aresta desconhecida reprova | F | `CH-02`, `CH-04` |
| T27 | Pack do capítulo não contém id de aresta secreta desconhecida pelo POV (só contagem) | F | 27.1 |
| T28 | Coordenadas derivadas: alterar `scale_ratio_A_to_B` recalcula todos os `RM-REG-*` exclusivos do Mapa B sem tocar seeds; nós compartilhados não mudam | R | `CN-05` |
| T34 | Razão de escala: `scale(A)/scale(B) = 0,0725` e a moldura do Mapa A mede 7,25 % da largura do Mapa B (±0,05 pp) | R | 7.4 |
| T29 | Aresta `EUCLID_TORTUOSITY` nunca gera `TR-01` que o fator 1,00 não geraria | F | 13.2 |
| T30 | Setas do inset não viram direcionalidade (`EDG-S-*` todas `BOTH`) | R | 11.1 |
| T31 | `features.cartography` ausente ⇒ compose idêntico ao golden | — | 36 |
| T36 | Autoria: `MAP-DIEGETIC-*.author` com id reprova; `PROVENANCE_INQUIRY` que resolve reprova; `PROVENANCE_INQUIRY` que só produz evidência passa; `CMY-09` nunca sai de `PERMANENTLY_AMBIGUOUS` | F | `MY-08` |
| T33 | Mapas impressos: todo id nas fontes é `SEEN_ON_MAP` no cap. 0; ids ausentes não; `KN-02` só para ausentes | R | 22.6 |
| T32 | Hash das fontes pinadas confere | R | `CG-06` |

---

## 36. Migration Strategy

### 36.1 Compatibilidade

- `features.cartography` **OFF por padrão**, lida com `.get()` sobre o dict
  original do `BOOK_SPEC` (padrão de `causal_ledger`/`visual_narrative`,
  `livingbook.py:342-360`). Nenhum livro existente muda.
- Nenhum arquivo de outro livro, do ledger, do canon interpretativo ou do
  contrato de proposta é alterado.
- EXTENDs no motor, todos no S5: `livingbook.py` (tarefa `T018C`, validadores
  anexados, tarefa de pack), `check_canon_continuity.py` (vocabulário de
  lugares), `build_canon_digest.py` (bloco opcional).

### 36.2 Slice plan

```text
S0 ─▶ S1 ─▶ S2 ─▶ S3 ─▶ S4 ─▶ S5 ─▶ S6
decisões  contrato+  arestas+   visibil.+   mistério+   integração   uso real
          inventário viagem     esconderijo artefatos   compose      (capítulos)
                                +perseguição
```

| Slice | Objetivo | Arquivos | Testes | DoD |
|---|---|---|---|---|
| **S0 — Decisões** | aprovar esta SDD; decisões da autora já registradas (escala 7,25 %, mapas diegéticos e impressos, autoria `NEVER`, anomalias intencionais, dois lugares no subterrâneo, valores de viagem); pendentes: confirmar a leitura linear da escala, `OQ-CART-04` (slug/pacote parcial), `OQ-CART-20` (limite de perguntas `NEVER`); versionar os PNGs | `books/sem-rosto/README.md`, `cartography/sources/`, `approvals/CART_DECISION_0001.md` | T32 | fontes pinadas; decisões registradas com `subject_sha256` |
| **S1 — Contrato e inventário** | todos os nós (L1, L2, L3, OFF, FRM), registro, artefatos, anomalias, rotas como traçado declarado; transformações; `CG`, `MY`, `CN-05` | `CARTOGRAPHY.schema.json`, `CARTOGRAPHY_TEMPLATE.yaml`, `check_cartography.py --mode canon`, seeds de nós/mistérios/artefatos/anomalias, fixture neutra | T01–T05, T10, T11, T19–T23, T28, T30 | conferência humana do inventário contra os mapas (checklist por item do Apêndice A); nenhum arquivo em `engine/scripts/livingbook.py` alterado |
| **S2 — Arestas e viagem** | digitalização das vias (polilinhas em px, conferidas), água, travessias, portais; `distance/time/reachable/route`; validador de caminho; `TR`, `AC`, `KN`, `CX` | `EDGES.seed.yaml`, `SUBTERRANEAN.seed.yaml`, `STAGING` (formato), `--mode wave` | T03, T06–T09, T12–T18, T29 | Apêndice C perguntas 1–3 e 7 respondidas pelo CLI |
| **S3 — Visibilidade, esconderijos, perseguição** | `visible_from`, `SGT-*`, `HID-*`, `CHS-*`, gargalos | `VISIBILITY`, `HIDEOUTS`, `--chase`, `--bottlenecks` | T24–T26 | Apêndice C perguntas 4–6 |
| **S4 — Mistério e camadas** | `EXT-*`, `RMY-*`, `CMY-*`, `MAP-*` diegéticos, `LYR-*`, crença por artefato, MYSTERY PRESERVATION GATE completo | `BOUNDARIES`, `MYSTERIES`, `ARTIFACTS`, `LAYERS`, `--exits`, `--exit-truth` | T09–T11, T22, T23 | Apêndice C perguntas 8 e 9 |
| **S5 — Integração** | `features.cartography` no compose (`T018C`, `V_CARTO_*`, pack), continuidade, digest | `livingbook.py`, `check_canon_continuity.py`, `build_canon_digest.py`, fixture de livro | T27, T31 | compose do pacote-fixture + `validate-gate GATE_CANON` executa `V_CARTO_CANON`; golden idêntico sem a feature |
| **S6 — Uso real** | primeiros capítulos de SEM ROSTO com staging; recalibrar limiares | pacote real (DEDR S6) | — | a autora responde "sim": *o sistema me impediu de algo que eu não queria e me deixou fazer tudo que eu queria?* |

Complexidade: S1 M · S2 L (digitalização é o trabalho grosso) · S3 M · S4 M ·
S5 S · S6 variável.

### 36.3 Protocolo de digitalização (S2)

1. Para cada via visível, marcar polilinha em pixels sobre o PNG pinado
   (ferramenta qualquer; o artefato é a lista de pontos).
2. Gerar um PNG de verificação com a polilinha sobreposta
   (`reports/cartography/digitization/<edge>.png`).
3. Conferência humana: aceita / corrige / marca `UNCERTAIN`.
4. Só arestas `CONFIRMED_VISUAL` ou `PROBABLE` aceitas entram como
   `CANONICAL`; `UNCERTAIN` entra `PROVISIONAL`.

---

## 37. Future Extensions

| Extensão | Gatilho | Nota |
|---|---|---|
| Relevo (`z`) por curvas/altitudes declaradas | a obra precisar de linha de visada por terreno | substitui parte das regras 16.3 por cálculo; sem mudar contrato |
| Iluminação por data e latitude (crepúsculo longo escocês) | calendário da história definido | deriva `lighting` de `at` |
| Interiores (plantas de capela, arquivo, delegacia) | cena dentro de edifício precisar de rota interna | sub-grafo `INTERIOR` com portal para o nó do edifício |
| Ruído/audibilidade | perseguição por som | análogo a `visible_from` |
| Vigilância como agenda (rondas por horário) | a obra definir patrulhas | `surveillance` com `schedule` |
| Promoção de `unreliable_sources` do DEDR para artefatos `MAP-*` | DEDR S2 | artefato cartográfico é uma fonte não confiável coletiva |
| Relíquias como portadoras de mapas (`BEA_HALDEN_SACRED_RELICS`) | canon visual ligado | um mapa-objeto pode ser relíquia |
| Renderização de mapas do leitor por capítulo (paratexto progressivo) | decisão editorial | PNG gerado a partir de `--reader-map`; nunca a partir do físico |
| Segundo livro com lugares | qualquer | ligar `features.cartography`; o código já é neutro |

---

## 38. Canonical Location Appendix

Transcrição v0 (esta sessão). Toda linha precisa de conferência humana no S1.
Colunas: **A px / B px** = pixel do ícone nas fontes; **RCG** = metros
(Mapa A para nós do Mapa A; escala do Mapa B decidida — 7.4 — para nós só do Mapa B);
**Acc** = precisão em metros; **Conf** = confiança da transcrição.

### 38.1 Level 1 — Urbano (Mapa A)

| id | canonical_name | Outros nomes | Tipo | A px | B px | RCG (x, y) | Acc | Status | Conf |
|---|---|---|---|---|---|---|---|---|---|
| `RM-CEN-SMC` | Saint Morrow Cross | "(0,0)" | LANDMARK | 521, 527 | 638, 530 | 0, 0 | 0 | ACTIVE | HIGH |
| `RM-CEN-RSP` | Red Stag Pub | — | PUB | 560, 462 | — | 158, 263 | 60 | ACTIVE | HIGH |
| `RM-CEN-CON` | Redmur Constabulary | — | POLICE | 615, 590 | — | 381, −255 | 60 | ACTIVE | HIGH |
| `RM-CEN-CAH` | Civil Archive Hall | — | ARCHIVE | 400, 605 | — | −490, −316 | 60 | ACTIVE | HIGH |
| `RM-CEN-OCP` | Office of Civic Preservation | — | GOVERNMENT_BUILDING | 355, 540 | — | −672, −53 | 60 | ACTIVE | HIGH |
| `RM-CEN-GMC` | General Mercantile | — | SHOP | 700, 475 | — | 725, 211 | 60 | ACTIVE | HIGH |
| `RM-CEN-OCS` | Old Coach Stop | — | TRANSPORT_STOP | 640, 680 | — | 482, −620 | 60 | UNKNOWN (carruagem desenhada; uso atual não mostrado) | HIGH |
| `RM-CEN-CLN` | Village Clinic | — | CLINIC | 735, 622 | — | 867, −385 | 60 | ACTIVE | HIGH |
| `RM-CEN-CHP` | Saint Morrow Chapel | — | CHAPEL | 318, 410 | 518, 457 | −822, 474 | 60 | ACTIVE | HIGH |
| `RM-URB-OPC` | Old Parish Cemetery | Cemitério Antigo (B) | CEMETERY | 185, 495 | 505, 525 | −1361, 130 | 60 | ACTIVE | HIGH |
| `RM-URB-FLE` | Flarry Estate | — | ESTATE | 258, 235 | 485, 290 | −1065, 1183 | 60 | ACTIVE | HIGH |
| `RM-URB-OQY` | Old Quarry | — | QUARRY | 435, 315 | 580, 425 | −348, 859 | 60 | ABANDONED? → `UNKNOWN` | HIGH |
| `RM-URB-SHF` | Sheep Fields | — | FIELD | 620, 260 | 660, 387 | 401, 1081 | 150 | ACTIVE | HIGH |
| `RM-URB-SBO` | Shepherd's Bothy | — | BOTHY | 630, 140 | 690, 310 | 441, 1567 | 60 | UNKNOWN | HIGH |
| `RM-URB-MNF` | Manfred Farm | — | FARM | 790, 295 | 800, 405 | 1089, 940 | 60 | ACTIVE | HIGH |
| `RM-URB-SWD` | Strathmoor Woods | — | FOREST | rótulo 975, 133 | rótulo 892, 293 | área | 150 | ACTIVE | HIGH |
| `RM-URB-ROW` | Rowan Cottage | — | COTTAGE | 1100, 222 | 1050, 345 | 2345, 1235 | 60 | UNKNOWN | HIGH |
| `RM-URB-RSV` | Reservoir | — | RESERVOIR | 1270, 360 | 1105, 445 | 3033, 676 | 150 | ACTIVE | HIGH |
| `RM-URB-PMP` | Pumping Station | — | UTILITY | 1255, 425 | 1080, 487 | 2973, 413 | 60 | UNKNOWN | HIGH |
| `RM-URB-BBR` | Burn Bridge | — | BRIDGE | 1150, 490 | 985, 512 | 2547, 150 | 60 | ACTIVE | HIGH |
| `RM-URB-ERC` | East Road — ponto de bloqueio | "East Road — Officially Closed" | ROADBLOCK | 1280, 507 | 1037, 538 | 3074, 81 | 60 | RESTRICTED (alegado) | HIGH |
| `RM-URB-CTH` | Caretaker House | — | HOUSE | 330, 790 | — | −774, −1065 | 60 | UNKNOWN | HIGH |
| `RM-URB-RCH` | Root Cellar Hideout | — | CELLAR | 205, 860 | — | −1280, −1349 | 60 | UNKNOWN | HIGH |
| `RM-URB-DCU` | Drainage Culvert | — | CULVERT | 358, 885 | — | −660, −1450 | 60 | ACTIVE | HIGH |
| `RM-URB-RTS` | Ruined Tool Shed | — | RUIN | 735, 880 | — | 867, −1430 | 60 | RUINED | HIGH |
| `WAT-ASH` | Ash Burn | — | BURN | 975,245 → 1150,490 → 1200,570 | 970,380 → 985,512 → 1080,560 | linha | 60 | — | HIGH (curso); nascente `UNKNOWN` |
| `RM-FRM-A-S` | moldura sul (South Gate Road) | "Para os vales e o resto do mundo" | FRAME_PORTAL | 583, 985 | — | 251, −1855 | 60 | — | HIGH |
| `RM-FRM-A-E` | moldura leste (East Road) | — | FRAME_PORTAL | a digitalizar | — | — | — | — | MEDIUM |
| `RM-FRM-A-N` | moldura norte (via de Shepherd's Bothy) | — | FRAME_PORTAL | a digitalizar | — | — | — | — | MEDIUM |

### 38.2 Level 3 — Subterrâneo

| id | canonical_name | Tipo | Portal | Inset px (A) | RCG (x, y) | z | Status | Conf |
|---|---|---|---|---|---|---|---|---|
| `RM-SUB-CHB` | Chapel Basement | CELLAR | `EDG-P-001` → Chapel | 1095, 670 | = Chapel | UNKNOWN | UNKNOWN | HIGH |
| `RM-SUB-CCT` | Cemetery Crypt Tunnel | TUNNEL | `EDG-P-002` → Cemetery | 965, 668 | = Cemetery | UNKNOWN | UNKNOWN | HIGH |
| `RM-SUB-STD` | Storm Drains | STORM_DRAIN | — | 1100, 766 | `UNKNOWN` | UNKNOWN | UNKNOWN | HIGH |
| `RM-SUB-RCP` | Root Cellar Passage | SUBTERRANEAN_PASSAGE | `EDG-P-004` → Root Cellar Hideout | 990, 770 | = Hideout | UNKNOWN | UNKNOWN | HIGH |
| `RM-SUB-PSC` | Pumping Station Channel | TUNNEL | `EDG-P-005` → Pumping Station | 1298, 760 | = Pumping Station | UNKNOWN | UNKNOWN | HIGH |
| `RM-SUB-QCS` | Quarry Crawlspace | SUBTERRANEAN_PASSAGE | `EDG-P-003` → Old Quarry | 1248, 663 | = Old Quarry (`ANM-A-03`) | UNKNOWN | UNKNOWN | HIGH |
| `RM-SUB-ROT` | Reservoir Overflow Tunnel | TUNNEL | `EDG-P-006` → Reservoir | 1297, 845 | = Reservoir | UNKNOWN | UNKNOWN | HIGH |
| `RM-SUB-CUX` | Culvert Exit | CULVERT | `EDG-P-007` → Drainage Culvert | 1013, 857 | = Drainage Culvert (`OQ-CART-09`) | UNKNOWN | UNKNOWN | MEDIUM |
| `RM-JCT-S1` | junção capela | JUNCTION | — | ≈ 1102, 700 | `UNKNOWN` | UNKNOWN | — | HIGH |
| `RM-JCT-S2` | junção drenos–canal | JUNCTION | — | ≈ 1160, 736 | `UNKNOWN` | UNKNOWN | — | HIGH |
| `RM-JCT-S3` | junção inferior | JUNCTION | — | ≈ 1160, 823 | `UNKNOWN` | UNKNOWN | — | HIGH |
| `RM-SUB-BTF` | Black Thistle Filling Station | UNKNOWN (o nome sugere posto; `type_confidence: LOW`) | **nenhum declarado** | **fora do inset** | `null` | UNKNOWN | UNKNOWN | AUTHOR_DECLARED (subterrâneo) |
| `RM-SUB-SC4` | Sealed Crypt IV | CRYPT | **nenhum declarado** | **fora do inset** | `null` | UNKNOWN | SEALED (pelo nome) | AUTHOR_DECLARED (subterrâneo) |

### 38.3 Level 2 — Regional (Mapa B; escala decidida 55,86 m/px, Acc 840 m)

| id | canonical_name (rótulo) | Tipo | Reg. | B px | RCG (x, y) | d. cruz (km) | Conf |
|---|---|---|---|---|---|---|---|
| `RM-REG-RDM` | Redmur | TOWN | 01 | rótulo 705, 535 | agregado | — | HIGH |
| `RM-REG-GLN` | Glenath | VILLAGE | 05 | 855, 190 | (12122, 18993) | 22,5 | HIGH |
| `RM-REG-CRB` | Creggan Bothy | BOTHY | 07 | 553, 230 | (−4748, 16759) | 17,4 | HIGH |
| `RM-REG-BRF` | Blackridge Farm | FARM | 08 | 265, 400 | (−20837, 7262) | 22,1 | HIGH |
| `RM-REG-CRE` | Corrie's End | VILLAGE (L) | 09 | 400, 355 | (−13295, 9776) | 16,5 | HIGH |
| `RM-REG-KRK` | Kirkhollow | VILLAGE | 10 | 140, 445 | (−27819, 4748) | 28,2 | HIGH |
| `RM-REG-ELG` | Elderglen | HAMLET (L) | 11 | 110, 540 | (−29495, −559) | 29,5 | HIGH |
| `RM-REG-HRW` | Harrowmire | MARSH | 12 | 180, 335 | (−25585, 10893) | 27,8 | HIGH |
| `RM-REG-STW` | Stonewell | HAMLET (L) | 13 | 340, 695 | (−16647, −9217) | 19,0 | HIGH |
| `RM-REG-CRV` | Cairnvale | VILLAGE | 14 | 470, 640 | (−9385, −6145) | 11,2 | HIGH |
| `RM-REG-GRF` | Grayfen | HAMLET (L) | 15 | 555, 835 | (−4637, −17038) | 17,7 | HIGH |
| `RM-REG-THB` | Thistlebank | HAMLET | 16 | 262, 830 | (−21004, −16759) | 26,9 | HIGH |
| `RM-REG-CRG` | Craigness | VILLAGE | 18 | 170, 640 | (−26143, −6145) | 26,9 | HIGH |
| `RM-REG-SBA` | Abadia em Ruínas de Saint Bride | ABBEY · RUIN | 19 | 245, 620 | (−21954, −5028) | 22,5 | HIGH |
| `RM-REG-MCR` | Moor Cairn | STANDING_STONES | 20 | 355, 265 | (−15809, 14803) | 21,7 | HIGH |
| `RM-REG-BRT` | Ben Ràth | MOUNTAIN (714 m asl) | 21 | 250, 225 | (−21674, 17038) | 27,6 | HIGH |
| `RM-REG-KLB` | Ruínas de Kellburne | RUIN | 22 | 1115, 170 | (26646, 20110) | 33,4 | HIGH |
| `RM-REG-CRH` | Carriden Hamlet | HAMLET | 24 | 850, 640 | (11843, −6145) | 13,3 | HIGH |
| `RM-REG-BTC` | Blackthorn Cottage | COTTAGE | 25 | 960, 570 | (17988, −2234) | 18,1 | HIGH |
| `RM-REG-WLF` | Willowford | VILLAGE | 26 | 1020, 700 | (21339, −9497) | 23,4 | HIGH |
| `RM-REG-FSG` | Fenside Grange | FARM | 27 | 1115, 625 | (26646, −5307) | 27,2 | HIGH |
| `RM-REG-MSG` | Mossgate | VILLAGE | 28 | 1030, 825 | (21898, −16479) | 27,4 | HIGH |
| `RM-REG-RVH` | Raven's Holt | HAMLET | 29 | 850, 855 | (11843, −18155) | 21,7 | HIGH |
| `RM-REG-OML` | Old Mill (em ruínas) | MILL | 30 | 722, 790 | (4692, −14524) | 15,3 | HIGH |
| `RM-REG-MFF` | Muirfield Farm | FARM | — | 268, 480 | (−20669, 2793) | 20,9 | HIGH |
| `RM-REG-LDR` | Loch Draven | LAKE | — | 700, 248 | (3463, 15753) | 16,1 | HIGH |
| `RM-REG-LCD` | Loch Calder | LAKE | — | 192, 760 | (−24914, −12848) | 28,0 | HIGH |
| `RM-REG-LAN` | Loch Ainslie | LAKE | — | 1115, 700 | (26646, −9497) | 28,3 | HIGH |
| `RM-REG-TRM` | Torran Mire | MARSH | — | 1140, 785 | (28043, −14245) | 31,5 | HIGH |
| `ROAD-E13` | Estrada 13 | ROAD ("Em Disputa") | — | rótulo 1308, 270 | (37428, 14524) | 40,1 | HIGH |

Todas as coordenadas desta tabela vêm de `source_px` do Mapa B com a escala decidida
(seção 7.4): `x = (px_x − 638) × 55,86`, `y = (530 − px_y) × 55,86`.

### 38.4 Registro dos Vilarejos (transcrição literal, ordem impressa)

| Linha | Índice impresso | Nome impresso | `location_id` | `placement` |
|---|---|---|---|---|
| 1 | 01 | Redmur | `RM-REG-RDM` | ON_MAP |
| 2 | 02 | Saint Morrow | `null` (candidatos: `RM-CEN-CHP`, `RM-CEN-SMC`) | NO_STANDALONE_LABEL |
| 3 | 03 | Flarry Estate | `RM-URB-FLE` | ON_MAP |
| 4 | 04 | Manfred Farm | `RM-URB-MNF` | ON_MAP |
| 5 | **05** | Rowan Cottage | `RM-URB-ROW` | ON_MAP |
| 6 | **05** | Glenath | `RM-REG-GLN` | ON_MAP |
| 7 | 07 | Creggan Bothy | `RM-REG-CRB` | ON_MAP |
| 8 | 08 | Blackridge Farm | `RM-REG-BRF` | ON_MAP |
| 9 | 09 | Corrie's End | `RM-REG-CRE` | ON_MAP |
| 10 | 10 | Kirkhollow | `RM-REG-KRK` | ON_MAP |
| 11 | 11 | Elderglen | `RM-REG-ELG` | ON_MAP |
| 12 | 12 | Harrowmire | `RM-REG-HRW` | ON_MAP |
| 13 | 13 | Stonewell | `RM-REG-STW` | ON_MAP |
| 14 | 14 | Cairnvale | `RM-REG-CRV` | ON_MAP |
| 15 | 15 | Grayfen | `RM-REG-GRF` | ON_MAP |
| 16 | 16 | Thistlebank | `RM-REG-THB` | ON_MAP |
| 17 | 17 | Letham | `null` | **NOT_ON_MAP** |
| 18 | 18 | Craigness | `RM-REG-CRG` | ON_MAP |
| 19 | 19 | Abadia de Saint Bride | `RM-REG-SBA` (no mapa: "Abadia em Ruínas de Saint Bride") | ON_MAP |
| 20 | 20 | Moor Cairn | `RM-REG-MCR` | ON_MAP |
| 21 | 21 | Ben Ràth | `RM-REG-BRT` | ON_MAP |
| 22 | 22 | Ruínas de Kellburne | `RM-REG-KLB` | ON_MAP |
| 23 | 23 | Passo de Muirchéin | `null` | **NOT_ON_MAP** |
| 24 | 24 | Carriden Hamlet | `RM-REG-CRH` | ON_MAP |
| 25 | 25 | Blackthorn Cottage | `RM-REG-BTC` | ON_MAP |
| 26 | 26 | Willowford | `RM-REG-WLF` | ON_MAP |
| 27 | 27 | Fenside Grange | `RM-REG-FSG` | ON_MAP |
| 28 | 28 | Mossgate | `RM-REG-MSG` | ON_MAP |
| 29 | 29 | Raven's Holt | `RM-REG-RVH` | ON_MAP |
| 30 | 30 | Old Mill | `RM-REG-OML` | ON_MAP |

30 linhas impressas; 29 índices distintos; índice 06 ausente; 26 entradas
localizadas, 1 sem rótulo próprio, 2 não localizadas. Lugares do mapa fora do
registro: Muirfield Farm (lugar nomeado), além de lagos, pântano Torran Mire,
Sheep Fields, Old Quarry, Strathmoor Woods, Reservoir, Pumping Station, Burn
Bridge, Shepherd's Bothy e a capela/cemitério.

### 38.5 Inventário de transcrição (checklist de `CG-08`)

Todo item abaixo precisa mapear para exatamente um de: nó `RM-*`, via
`ROAD-*`, rota `RTE-*`, água `WAT-*`/lago/pântano, entrada de registro,
artefato `MAP-*`, glifo `GLY-*`, estrutura `UNL-*`, fronteira `BND-*`, saída
`EXT-*`.

- **Mapa A — rótulos (28):** Flarry Estate · Old Quarry · Sheep Fields ·
  Shepherd's Bothy · Manfred Farm · Strathmoor Woods · Rowan Cottage · Ash Burn
  · Reservoir · Pumping Station · Burn Bridge · East Road — Officially Closed ·
  Saint Morrow Chapel · Old Parish Cemetery · Red Stag Pub · General Mercantile
  · Office of Civic Preservation · Saint Morrow Cross (0,0) · Civil Archive
  Hall · Redmur Constabulary · Village Clinic · Old Coach Stop · Caretaker
  House · Root Cellar Hideout · Drainage Culvert · South Gate Road (Entrada
  Principal) · Ruined Tool Shed · R1/R2/R3.
- **Mapa A — inset (8 + glifos):** Cemetery Crypt Tunnel · Chapel Basement ·
  Quarry Crawlspace · Root Cellar Passage · Storm Drains · Pumping Station
  Channel · Culvert Exit · Reservoir Overflow Tunnel · `⊤ ● + ◀`.
- **Mapa A — legenda (8):** Estrada principal · Trilha · Rota de fuga ·
  Passagem oculta · Área restrita · Túmulo/Cripta · Água · Bosque.
- **Mapa A — textos (8), figuras (2), marcador (ponto vermelho do Root
  Cellar), escala, grade, rosa-dos-ventos.**
- **Mapa B — rótulos (≈ 45):** todos os da seção 38.3 + Saint Morrow Chapel ·
  Cemitério Antigo · Saint Morrow Cross · REDMUR · South Gate Road (Entrada
  Principal) · Old Quarry · Sheep Fields · Shepherd's Bothy · Manfred Farm ·
  Flarry Estate · Rowan Cottage · Strathmoor Woods · Ash Burn · Reservoir ·
  Pumping Station · Burn Bridge · East Road Officially Closed · Estrada 13 Em
  Disputa · R3 (×2) · R4 · R7 · R13 · R17.
- **Mapa B — placas (6):** Caelrith? 32 · Dunsgate 17 · Westhaven 29 ·
  Inverloch ?7 · Eldham 41 (×2).
- **Mapa B — legenda (16), registro (30 linhas + título + rodapé), rotas
  contestadas (7 + rodapé), textos (≈ 8), escala, grade, glifos vermelhos
  ilegíveis (9), triângulo sem legenda.**

---

## 39. Canonical Route Appendix

### 39.1 Vias do Level 1 (topologia provisória — `PROBABLE`, `EUCLID_TORTUOSITY` até o S2)

| id | Nome | Classe | Cadeia de nós (ordem física) | Conf |
|---|---|---|---|---|
| `ROAD-SGR` | South Gate Road | MAIN | `RM-CEN-SMC` → `RM-JCT-U01` (ramal Constabulary/Coach Stop) → `RM-JCT-U02` (ramal Tool Shed) → `RM-FRM-A-S` | HIGH (nome e traçado) |
| `ROAD-EAST` | East Road (nome só a leste da ponte) | MAIN? | … `RM-URB-BBR` → `RM-URB-ERC` → `RM-FRM-A-E` | HIGH (traçado); nome parcial |
| `ROAD-U-E` | (sem nome) via leste | SECONDARY | `RM-CEN-SMC` → sul do Mercantile → `RM-JCT-U05` → `RM-URB-BBR` | PROBABLE |
| `ROAD-U-N` | (sem nome) via norte | SECONDARY | `RM-CEN-SMC` → `RM-CEN-RSP` → borda leste de Sheep Fields → `RM-URB-SBO` → `RM-FRM-A-N` | PROBABLE |
| `ROAD-U-W` | (sem nome) via oeste | SECONDARY | `RM-CEN-SMC` → `RM-CEN-OCP` → `RM-JCT-U07` → `RM-CEN-CHP` → laço de `RM-URB-OPC` | PROBABLE |
| `ROAD-U-NW` | (sem nome) via noroeste | SECONDARY | `RM-CEN-CHP` → norte → oeste de `RM-URB-OQY` → ramal `RM-URB-FLE` → norte | PROBABLE |
| `ROAD-U-NE` | (sem nome) via nordeste | SECONDARY | `RM-CEN-GMC` → `RM-URB-MNF` ; ramal leste → `RM-JCT-U05` | PROBABLE |
| `ROAD-U-ROW` | (sem nome) acesso a Rowan | TRAIL | `RM-URB-ROW` → sudoeste → (travessia do Ash Burn? `ANM-A-04`) → malha leste | UNCERTAIN |
| `ROAD-U-PMP` | (sem nome) margem leste | TRAIL | `RM-URB-BBR` (lado leste) → `RM-URB-PMP` → `RM-URB-RSV` | PROBABLE |
| `ROAD-U-SW` | (sem nome) trilhas sudoeste | TRAIL | `RM-CEN-CAH` → sul → `RM-URB-CTH` → `RM-URB-RCH` ; `RM-URB-CTH` → `RM-URB-DCU` | PROBABLE |
| `ROAD-U-SE` | (sem nome) vielas sudeste | TRAIL | `RM-JCT-U01` → `RM-CEN-OCS` ; `RM-JCT-U02` → `RM-URB-RTS` ; `RM-CEN-CLN` → leste | PROBABLE |

### 39.2 Rotas nomeadas

| Rota | Traçado físico (fato) | Pertinência | Lema / mistério |
|---|---|---|---|
| `RTE-A-R1` | Old Parish Cemetery ↔ borda oeste do centro (`RM-JCT-U07`) | Mapa A | `RMY-R1` "O círculo retorna." (vínculo **não** assumido) |
| `RTE-A-R2` | Shepherd's Bothy ↔ Strathmoor Woods (borda sul) ↔ Rowan Cottage | Mapa A | `RMY-R2` "Nem todo caminho continua." (vínculo não assumido) |
| `RTE-A-R3` | Old Quarry ↔ Sheep Fields (margem sul) ↔ Manfred Farm | Mapa A | `RMY-R3` "Há mais de uma margem." (vínculo não assumido) |
| `RTE-B-R3-STR` | = corredor de `RTE-A-R2` | Mapa B | `RMY-R3`; `ANM-X-01` |
| `RTE-B-R3-GLN` | cordilheira norte ↔ estrada de Glenath | Mapa B | `RMY-R3`; `EXT-09` |
| `RTE-B-QM` | = corredor de `RTE-A-R3` | Mapa B | glifo `GLY-B-09` |
| `RTE-B-CHP` | = corredor de `RTE-A-R1` | Mapa B | sem rótulo |
| `RTE-B-R4` | ramal curto a sudeste da South Gate Road | Mapa B | `RMY-R4` "Entrada ou saída?" |
| `RTE-B-R7` | estrada ao sul de Muirfield Farm (E–O) | Mapa B | `RMY-R7` "Desaparece após a ponte." |
| `RTE-B-R13` | estrada Willowford → leste (Eldham) | Mapa B | `RMY-R13` "Sinais foram removidos." |
| `RTE-B-R17` | Stonewell/Thistlebank → nordeste (Cairnvale/South Gate) | Mapa B | `RMY-R17` "Usada, mas por quem?" |

### 39.3 Rede subterrânea

Arestas `EDG-S-001..011` e portais `EDG-P-001..007` (seção 11). Todas
`edge_type: SECRET_PASSAGE` (legenda "Passagem oculta") exceto os portais;
todas `directionality: BOTH`, `distance_meters.basis: UNSPECIFIED` com piso
físico por âncora (11.4).

### 39.4 Saídas

`EXT-01..EXT-10` (seção 20.3) + `EXT-11..` a inventariar no S2.

---

## 40. Open Questions

| ID | Pergunta | Bloqueia | Recomendação |
|---|---|---|---|
| ~~**OQ-CART-01**~~ | **DECIDIDA (2026-09-19)**: Mapa B = 55,86 m/px (7,25 : 100). | — | ver 7.4; confirmar só a leitura linear (não de área) |
| ~~**OQ-CART-02**~~ | **DECIDIDA (2026-09-19): SIM**, os mapas existem no mundo. | — | ver seção 22.5 |
| ~~**OQ-CART-02b**~~ | **DECIDIDA (2026-09-19)**: autoria nunca revelada; há investigadores. | — | ver 22.7 |
| ~~**OQ-CART-03**~~ | **DECIDIDA (2026-09-19): SIM**, ambos os mapas impressos, inteiros, com o inset. | — | ver seção 22.6 |
| **OQ-CART-03b** | Em que resolução e posição no livro os mapas são impressos (as anomalias entram como estão, por decisão `OQ-CART-15`)? | impressão | checar o que a edição Kindle preserva (`EDITION_CAPABILITIES`); legibilidade não pode alterar conteúdo |
| **OQ-CART-04** | Slug e pacote parcial `books/sem-rosto/` (só `cartography/` até o DEDR S6)? | S0 | sim, `sem-rosto` |
| ~~**OQ-CART-05**~~ | **DECIDIDA (2026-09-19)**: os dois lugares estão no subterrâneo. | — | ver 11.6 |
| **OQ-CART-05b** | Como se chega a cada um (entrada, corredor, junção, distância, estado)? | cenas nesses lugares | por proposta, quando a história precisar; `UNDECLARED` até lá |
| **OQ-CART-20** | `max_never_questions` (padrão 3): o DEDR já usa 3 perguntas `NEVER` em SEM ROSTO; `Q-MAP-AUTHOR` seria a 4ª | `check_interpretive_canon.py` no gate de canon | elevar o limite para 4 em `BOOK_SPEC.features.living_theory.thresholds` (configurável), ou fundir com uma pergunta existente; decidir junto ao SDD narrativo |
| OQ-CART-06 | Língua dos nomes na prosa PT-BR ("Loch Draven" ou "Lago Negro"?) | revisão editorial | guardar todos; escolher `PTBR_DISPLAY` por lugar |
| OQ-CART-07 | "Saint Morrow" (registro 02) é a paróquia, a cruz, a capela, uma localidade sem rótulo — ou é um dos "avisos"? | `REG-B-02` | deixar `null` até decisão; é `CMY-05`-adjacente |
| OQ-CART-08 | As pontas de seta do inset indicam algo físico (fluxo de água, porta de um lado só)? | direcionalidade subterrânea | `BOTH` até decisão |
| OQ-CART-09 | Culvert Exit = Drainage Culvert? Quarry Crawlspace fica sob o Old Quarry (túnel ≥ 3,35 km até o Pumping Station Channel)? | âncoras subterrâneas | confirmar as duas; se o crawlspace for outro lugar, criar nó por proposta |
| OQ-CART-10 | Declinação magnética / norte verdadeiro | — | ignorar salvo necessidade narrativa |
| OQ-CART-11 | `secret_level` das rotas R1–R3 (uma "rota de fuga" impressa num mapa de aparência oficial é pública?) e do porão da capela | conhecimento público | decidir com OQ-CART-02 |
| OQ-CART-12 | O trecho entre a cruz e Burn Bridge também se chama East Road? | nomenclatura | `SEGMENT_ONLY` até decisão |
| OQ-CART-13 | Existe ponte física perto do marcador R7? | `RMY-R7` (só a parte física) | a autora decide o **fato físico**; o lema continua mistério |
| ~~**OQ-CART-14**~~ | **APROVADOS (2026-09-19)** velocidades, modificadores e limiares (seções 16.3, 17.2, 17.3). | — | mudança futura = decisão fundacional versionada |
| ~~**OQ-CART-15**~~ | **DECIDIDA (2026-09-19)**: as 22 anomalias são `INTENTIONAL_ARTIFACT`. | — | ver 21.6; a impressão deixa de estar bloqueada por esta questão |
| **OQ-CART-16** | O Ash Burn é atravessado a oeste de Rowan Cottage (travessia não desenhada)? A R2 cruza o curso do Ash Burn sob o bosque? | `CX-01` em `ROAD-U-ROW` e `RTE-A-R2` | decidir o fato físico no S2 |
| OQ-CART-17 | Capability no motor (`features.cartography`) ou validador só da obra? | S1 | motor, neutro (seção 6.2) |
| OQ-CART-18 | Ano presente da história e altitude de Saint Morrow Cross | `--at-year` padrão; `z` de Ben Ràth | dono: TIMELINE / canon narrativo |
| OQ-CART-19 | Iluminação pública, vigilância, horários de funcionamento, veículos disponíveis, perfis de mobilidade | pack, `safest_route`, `vehicle_time` | dono: canon narrativo; a cartografia só guarda os campos |

---

## Apêndice A — Evidência de transcrição

### A.1 Método

- Fontes lidas em resolução nativa (1448×1086) e em recortes ampliados 2×–6×
  com Pillow (LANCZOS), em `scratchpad/tiles/` desta sessão: seis quadrantes
  por mapa, oito regiões do Mapa B, o registro, as barras de escala, a origem e
  uma folha de contato dos glifos vermelhos.
- Posição de lugar = centro visual do **ícone** (não do rótulo), ±15 px.
- Nada foi inferido de conhecimento externo; nomes transcritos como impressos.
- **Reprodutível**: o S1 exige repetir a transcrição sobre os PNGs pinados e
  anexar os recortes em `reports/cartography/transcription/`.

### A.2 Origem e grade do Mapa A

- Monumento de Saint Morrow Cross em px (521, 527); rótulo "(0,0)" em vermelho
  logo abaixo, em px ≈ (520, 590).
- Centros de coluna (topo): A 137 · B 293 · C 437 · D 578 · E 783 · F 909 ·
  G 1040 · H 1165. Centros de linha (lateral): 1 117 · 2 242 · 3 365 · 4 490 ·
  5 610 · 6 720 · 7 835.

### A.3 Leitura do inset subterrâneo (px no Mapa A)

- Janela do inset: x 900–1350, y 600–880.
- Chapel Basement (1095, 670) desce a J1 (≈ 1102, 700); de J1 uma linha para
  oeste com ponta de seta a ≈ (975, 700) sobe até o `⊤` de Cemetery Crypt
  Tunnel (≈ 967, 655); de J1 uma linha desce com ponta de seta até Storm
  Drains (≈ 1102, 735).
- De Storm Drains para oeste, com ponta de seta a ≈ (1000, 736), até o `⊤`
  de Root Cellar Passage (≈ 960, 758); dali vertical com `⊤`/`+` até Culvert
  Exit (≈ 958, 835).
- De Storm Drains para leste até J2 (≈ 1160, 736), seguindo até o `●` junto a
  Pumping Station Channel (≈ 1195, 736); do lado direito do canal, vertical com
  `⊤` nas duas pontas até Quarry Crawlspace (≈ 1277, 670).
- De J2 vertical (marcas `+`) até J3 (≈ 1160, 823); de J3 para leste até o `●`
  de Reservoir Overflow Tunnel (≈ 1190, 833); de J3 para oeste (marca `+` em
  ≈ 1040, 823) até Culvert Exit.

### A.4 Escalas e ajuste entre mapas

Perfil de brilho da barra do Mapa A (linha y = 1021): marca inicial em
x = 186, final em x = 432–433; rótulos 0 (186), 250 (232), 300 (307),
750 (369), 1.000 m (≈ 435); divisões internas em x ≈ 230, 267, 306, 402 — sem
proporção com os rótulos. Escala adotada: 1.000 m / 247 px = **4,05 m/px**.

Barra do Mapa B (y ≈ 1022): marcas em x ≈ 901 (0), 951 (2,5), 1003 (5),
1053 (10), 1103 (15), 1143 (20 km). Intervalos em px: 50, 52, 50, 50, 40 para
2,5 · 2,5 · 5 · 5 · 5 km. Leituras: 0→20 km = 82,6 m/px; 0→5 km = 49 m/px;
5→20 km = 107 m/px.

Ajuste de similaridade Mapa B → Mapa A (mínimos quadrados, 14 pares: cruz,
capela, cemitério, Flarry, Old Quarry, Sheep Fields, Shepherd's Bothy, Manfred
Farm, Rowan Cottage, Reservoir, Pumping Station, Burn Bridge, X da East Road,
South Gate Road): escala 1,71 px(A)/px(B) → 6,94 m/px; rotação −2,1° em
coordenadas de imagem (y para baixo) = +2,1° anti-horário em RCG.
Resíduos (m): cruz 71 · capela 85 · cemitério 452 · Flarry 388 · Old Quarry
237 · Sheep Fields 347 · Bothy 190 · Manfred 101 · Rowan 445 · Reservoir 158 ·
Pumping 87 · Burn Bridge 175 · X East Road 350 · South Gate 665 (âncora de
rótulo, não de ícone). RMS ≈ 317 m.

**Nota pós-decisão (2026-09-19).** O ajuste de 6,94 m/px acima descreve o
desenho do núcleo no Mapa B, não a escala do mapa: a escala é 55,86 m/px
(seção 7.4). O ajuste fica como evidência de que o núcleo está ampliado ≈ 8×.

### A.5 Glifos vermelhos ilegíveis do Mapa B

| id | B px | Junto a | Leituras possíveis (nenhuma atribuída) |
|---|---|---|---|
| `GLY-B-01` | 143, 368 | Harrowmire (início da estrada) | "10", "R0", "IO" |
| `GLY-B-02` | 218, 487 | Kirkhollow | "R1", "11", "R4" |
| `GLY-B-03` | 149, 669 | Craigness | "17", "R7", "Π" |
| `GLY-B-04` | 322, 727 | Stonewell | "11", "R1", "Π" |
| `GLY-B-05` | 1045, 250 | Ruínas de Kellburne (estrada) | "10", "1U", "R0" |
| `GLY-B-06` | 577, 233 | Creggan Bothy | "E7", "R7", "17" |
| `GLY-B-07` | 687, 295 | oeste de Shepherd's Bothy (início da rota R3 do Mapa B) | ilegível |
| `GLY-B-08` | 1002, 855 | Mossgate | "23", "R3", "25" |
| `GLY-B-09` | 730, 432 | ponta leste da rota Old Quarry → Manfred | "R3" (baixa) |

Qualquer coincidência entre uma leitura possível e números do registro ou das
rotas contestadas é registrada como **coincidência de leitura**, nunca como
vínculo (`INV-C08`).

---

## Apêndice B — Anomalias cartográficas detectadas

Todas nasceram `UNDECIDED` (seção 21.6). **Classificadas pela autora em
2026-09-19 (`OQ-CART-15`): todas `INTENTIONAL_ARTIFACT`.** A coluna "Efeito"
abaixo descreve o efeito **antes** da decisão; depois dela, as anomalias são
citáveis por mistério, evidência e cena, sem significado atribuído.

| id | Fonte | Anomalia | Efeito enquanto `UNDECIDED` |
|---|---|---|---|
| `ANM-A-01` | A | barra de escala rotulada 0 · 250 · **300** · 750 · 1.000 m, divisões internas desproporcionais | só as extremidades são usadas (7.2) |
| `ANM-A-02` | A | colunas da grade com espaçamento irregular | grade = rótulo, não métrica |
| `ANM-A-03` | A | inset põe Quarry Crawlspace ao lado de Pumping Station Channel; na superfície distam ≈ 3,35 km | piso físico do túnel = 3,35 km |
| `ANM-A-04` | A | via de Rowan Cottage parece cruzar o Ash Burn sem ponte; R2 passa ao norte da nascente visível | `CX-01` até `OQ-CART-16` |
| `ANM-A-05` | A | edificação com "+" branco (`UNL-A-01`) sem rótulo, símbolo diferente do "†" da legenda | inerte |
| `ANM-X-01` | A × B | corredor Bothy–Strathmoor–Rowan: **R2** no A, **R3** no B | `CMY-02` inerte |
| `ANM-X-02` | A × B | barra do Mapa B e desenho do núcleo não batem com a razão 7,25 : 100 | resolvida no plano físico por 7.4; o **porquê** é `CMY-06` |
| `ANM-X-03` | A × B | Old Parish Cemetery (A) = Cemitério Antigo (B) | alias aceito, casamento registrado |
| `ANM-B-01` | B | registro: índice **05 duas vezes** (Rowan Cottage, Glenath), **06 ausente** | preservado literal; `CMY-03` inerte |
| `ANM-B-02` | B | registro × mapa: Letham e Passo de Muirchéin sem lugar; Muirfield Farm sem registro; "Saint Morrow" sem rótulo | entradas `NOT_ON_MAP` / `null` |
| `ANM-B-03` | B | barra de escala não linear (intervalos iguais para 2,5 e 5 km) | não é a escala; vale a decidida (7.4) |
| `ANM-B-04` | B | duas placas "Para Eldham (41 milhas)" em vias diferentes | alegações independentes |
| `ANM-B-05` | B | "Para Caelrith?" — ponto de interrogação na placa | literal |
| `ANM-B-06` | B | placas em milhas, barra em km | nenhuma entra na física |
| `ANM-B-07` | B | "Inverloch (?7 milhas)" — dígito ilegível | literal "?7" |
| `ANM-B-08` | B | "Westhaven" ou "Weathoven" | ambas as grafias em `names[]` |
| `ANM-B-09` | B | rótulo R3 em três lugares distintos | `RMY-R3` com três âncoras |
| `ANM-B-10` | B | R1 e R2 na legenda sem marcador localizado | âncora `NOT_FOUND` |
| `ANM-B-11` | B | triângulo branco junto à capela, ausente da legenda | `CMY-07` inerte |
| `ANM-B-12` | B | "REDMUR SEMPRE OBSERVA" renderizado corrompido no canto inferior direito | texto registrado na forma pretendida + forma renderizada |
| `ANM-B-13` | B | nove glifos vermelhos ilegíveis | `GLY-B-01..09` |
| `ANM-B-14` | B | linha para Dunsgate entre os símbolos "trilha" e "limite incerto" | `BND-B-02` ambíguo |

---

## Apêndice C — Condição de sucesso: as perguntas da missão (§42)

Respostas como o sistema as dará após o S4, com os dados desta transcrição.
`ENGINE_VIEW` = visão do motor (não entregar a personagem nem ao leitor).

**1. "Quais rotas a protagonista conhece para sair do cemitério?"**
`--escape-routes RM-URB-OPC --actor CHR-P --chapter N`. Resposta = caminhos
a partir do cemitério filtrados pelo conhecimento de `CHR-P` no capítulo N:
por padrão (`PUBLIC`), as vias de superfície (laço do cemitério → via oeste →
centro; `RTE-A-R1` se `OQ-CART-11` a declarar pública). O túnel
`EDG-P-002`/`EDG-S-002` só aparece se o ledger registrou que ela o aprendeu.
Em `ENGINE_VIEW`, aparece marcado "desconhecido por CHR-P".

**2. "Quanto tempo leva para ir de Rowan Cottage até Shepherd's Bothy?"**
Distância mínima ≈ 1.933 m (euclidiana, ±120 m). Pela `RTE-A-R2` (estimativa
`EUCLID_TORTUOSITY` 1,35 → ≈ 2,6 km, borda de bosque): a pé, perfil `FIT`, de
dia: mínimo físico ≈ 14 min 40 s; esperado ≈ 43 min; à noite sem luz, rota
familiar: ≈ 56 min. Ressalva automática: `CX-01` pendente em `RTE-A-R2`
(`OQ-CART-16`).

**3. "Existe alguma passagem subterrânea entre a capela e o cemitério?"**
Sim (`ENGINE_VIEW`): `EDG-P-001` → `RM-SUB-CHB` → `EDG-S-001` → `RM-JCT-S1`
→ `EDG-S-002` → `RM-SUB-CCT` → `EDG-P-002`. Comprimento ≥ 640 m; dimensões,
estado e sentido `UNSPECIFIED`. Com `--actor`, a resposta depende do
conhecimento do ator.

**4. "Esse personagem poderia ter visto outro personagem atravessar a ponte?"**
`--visible <lugar do observador> RM-URB-BBR --lighting L`. Ex.: do Pumping
Station, ≈ 500 m: de dia `UNDETERMINED` (vegetação ciliar não classificada);
à noite sem luz `NOT_VISIBLE`; reconhecer **quem** atravessa:
`RECOGNITION_OUT_OF_SCOPE`.

**5. "Há algum esconderijo acessível sem atravessar área vigiada?"**
Único esconderijo registrado: `HID-RCH`. Rotas até ele não cruzam a única
área restrita desenhada (`BND-A-01`, East Road). Porém `surveillance` é
`UNKNOWN` em todos os lugares → resposta `UNDETERMINED_SURVEILLANCE`, com a
lista de lugares cujo estado de vigilância precisaria ser decidido para
responder `YES`.

**6. "É fisicamente possível realizar essa perseguição?"**
`--chase CHS-*` → veredito por regra `CH-01..07` com janelas por nó,
gargalos (ex.: Burn Bridge é o único elo entre o núcleo e a margem leste do
Ash Burn no Mapa A) e pontos de fuga.

**7. "É possível sair do Red Stag às 23:14 e chegar ao Old Parish Cemetery
às 23:18 caminhando?"** `FAIL TR-01` (mínimo físico a pé ≈ 11 min 33 s);
correndo, `FAIL TR-03` para perfil `FIT` (≈ 6 min).

**8. "Que estradas parecem sair de Redmur?"**
`--exits` → `EXT-01..EXT-10` (+ as do S2), cada uma com classes e alegações:
South Gate Road (`APPARENT`, "Entrada Principal"), East Road (`APPARENT`,
`CLOSED` alegado), Estrada 13 (`DISPUTED`, "Caelrith?"), vias para Dunsgate,
Westhaven, Inverloch, Eldham (×2), a R3 que sobe a cordilheira ao norte, a via
bloqueada perto de Kellburne.

**9. "Qual delas é realmente a saída?"**

```text
EXIT_TRUTH_NOT_IN_CARTOGRAPHY
A cartografia modela o espaço até as molduras dos mapas canônicos.
Saídas aparentes: EXT-01..EXT-10 (classes e alegações acima).
Nenhuma classe TRUE_EXIT existe neste sistema.
truth_ref: nenhum registrado no Story Truth Ledger.
```

---

## Apêndice D — Arquivos inspecionados e comandos

Arquivos lidos: `AGENTS.md`; `docs/ARCHITECTURE.md`;
`docs/sdd/DYSTOPIC_ENIGMA_DARK_ROMANCE_SDD_v0.1.md` (§1–7, §30–31, §33);
`engine/ENGINE_GRAPH.yaml` (execution_policy, protocols, known_capabilities);
`engine/contracts/CANON_PROPOSAL.schema.json`;
`engine/contracts/MEDIA_MANIFEST.schema.json` (`entities`);
`engine/templates/CAUSAL_LEDGER_TEMPLATE.yaml` (eventos, `knowledge_delta`,
`mutation_log`); `engine/scripts/check_causal_ledger.py` (:335-365, :755-790,
:1050-1090, argparse); `engine/scripts/check_interpretive_canon.py` (:115-127,
argparse); `engine/scripts/check_canon_continuity.py` (docstring, funções);
`engine/scripts/livingbook.py` (features, T012–T021, GATE_CANON);
`engine/scripts/runtime_taskgraph.py` (funções);
`books/narciso/BOOK_GRAPH.yaml`; listagens de `books/`, `authors/bea_halden/`,
`tests/`, `tests/fixtures/`, `engine/`, `output/cofres-youtube-v1/`.

Fontes: `~/Downloads/SEM ROSTO/redmur_map.png`,
`~/Downloads/SEM ROSTO/redmur_arredores_map.png` (lidas em resolução nativa e
em recortes ampliados).

Comandos relevantes: `git status --short`, `git log --oneline`,
`git branch -a`; `sha256sum` dos PNGs; buscas `grep -rniE
"location|geograph|spatial|coordinate|travel|route"` em `engine/` (nenhum
sistema espacial encontrado); `grep -ril "redmur|saint morrow"` (nenhuma
ocorrência de Redmur no repositório); recortes e perfis de brilho com Pillow
(`.venv`); ajuste de similaridade e cálculo de coordenadas em Python stdlib.

Nenhum arquivo do repositório foi alterado além da criação deste documento.
