# Plano de Desenvolvimento — Redução de Custo de LLM

> Escopo desta rodada: **exclusivamente custo.** Performance/tempo de parede,
> reescrita de orquestrador e as demais ideias de `03-arquiteturas-propostas.md`
> ficam fora deste plano, exceto onde uma mudança também reduz tempo como
> efeito colateral direto de reduzir chamadas/tokens (nesse caso, menciono o
> ganho de tempo apenas como nota, não como objetivo).
>
> Este documento foi desenhado para ser executável em cima do código real do
> motor (`engine/scripts/livingbook.py`, `engine/agents/*.toml`,
> `ENGINE_GRAPH.yaml`), não como uma reescrita hipotética.
>
> **Estado de implementação (atualizado após a execução):** Fase 0
> (telemetria) e Fase 1 (infraestrutura de dosagem + quick win) — **feitas**.
> Fase 2 (tabela completa nos 68 agentes genéricos + 2 agentes específicos de
> `a_morte_ainda_nao_nasceu`, incluindo o *override* de tarefa para
> `T4??_FACE_QA`) — **feita e validada** (`validate-engine`, `validate-book`
> dos dois livros, `compose` + `smoke-test` de teste). T-COST-0.4 (rodar um
> livro real para popular o *ledger* com custo de verdade) e a Fase 1B
> (impor a dosagem por código) continuam pendentes — exigem uma execução real
> do motor, fora do escopo de uma sessão de edição de arquivos.

---

## 1. Objetivo e critério de sucesso

**Objetivo**: reduzir o custo de tokens por livro produzido, sem reduzir os
alvos declarados em `quality_profile.yaml` de cada obra.

**Critério de sucesso (mensurável)**: custo total em US$ (ou tokens, na
ausência de preço) por livro de referência, medido pelo *ledger* de custo
introduzido na Fase 0, comparando um *run* antes e depois de cada fase
aplicada. Sem essa medição, nenhuma alegação de economia é verificável — por
isso a Fase 0 é pré-requisito de tudo, mesmo não sendo a peça mais
interessante do plano.

**Não-objetivo desta rodada**: tempo de execução, novo orquestrador,
retrieval de canon, QA determinística de imagem/DOCX. Essas continuam
válidas (documento 03) mas ficam para depois.

## 2. Princípio condutor: a dosagem por *tier* de modelo

Esta é a peça central pedida e organiza o resto do plano. Proposta de três
tiers, deliberadamente poucos (mais que isso vira complexidade de
manutenção sem ganho proporcional):

| Tier | Perfil de tarefa | Exemplo de classe de modelo (agnóstico de fornecedor) |
|---|---|---|
| **S — Frontier** | Julgamento criativo irredutível, decisões irreversíveis, risco ético/legal/de marca | Claude Opus-class / GPT-5-class (o "topo de linha" disponível) |
| **M — Equilibrado** | Execução competente contra uma especificação clara; checagem estruturada contra uma fonte de verdade (canon, timeline, regras) | Claude Sonnet-class / GPT-5-mini-class |
| **XS — Rápido/econômico** | Tarefa mecânica, de formato, checklist, ou verificação de padrão quase-objetiva | Claude Haiku-class / GPT-5-nano-class (ou, quando fizer sentido, nem LLM — ver §6) |

Regra de desempate: **quando a frequência de chamada é alta, o tier tende a
cair** (o custo é volume × preço-por-token; um agente chamado 24× no livro
pesa mais que um chamado 1×) — **exceto quando o risco de falha é
inaceitável** (ético, legal, canônico irreversível), caso em que o tier fica
em S mesmo com alta frequência. Essa exceção é explícita e nomeada na tabela
da Fase 2 (§4) para não virar uma regra ambígua.

## 3. Mecanismo técnico — como a dosagem realmente acontece

Hoje **não existe nenhum campo de modelo em lugar nenhum do repositório**
(nem em `engine/agents/*.toml`, nem em `ENGINE_GRAPH.yaml`, nem em
`TASK_GRAPH.yaml`). A seleção de modelo é 100% implícita: é o modelo da
sessão da CLI hospedeira (Codex CLI / Claude Code) rodando o repositório
inteiro. Para a dosagem virar realidade, ela precisa aparecer em três lugares
encadeados — e isso é uma mudança aditiva, de baixo risco, não uma reescrita:

```
engine/agents/<AGENTE>.toml            → declara seu próprio model_tier
        │
        ▼ (build_standard_graph)
runtime/<slug>/TASK_GRAPH.yaml          → cada nó de tarefa carrega o model_tier do seu owner/spawn
        │
        ▼ (IMPLEMENT.md / AGENTS.md)
sessão de execução (Codex CLI / Claude Code) → instruída a spawnar cada subagente
                                                 no modelo do tier declarado
```

O terceiro passo é o único que depende de capacidade do host: tanto Codex CLI
quanto Claude Code já permitem indicar explicitamente qual modelo um
subagente/subtarefa deve usar no momento do *spawn* — ou seja, **este
mecanismo funciona hoje, sem esperar por um orquestrador novo**. Ele é a
versão "sugestão forte, seguida por instrução textual" do tiering. Uma versão
"imposta por código" (um *runner* que de fato chama a API certa por tier) é
descrita como extensão opcional em §7 (Fase 1B), fora do caminho crítico.

## 4. Fase 0 — Fundação de medição (pré-requisito)

Sem isto, nenhuma das fases seguintes pode provar que funcionou.

| ID | Tarefa | Entregável | Esforço |
|---|---|---|---|
| T-COST-0.1 | Estender o uso do schema já existente `engine/contracts/TASK_RESULT.schema.json` (ele já aceita `additionalProperties`) — formalizar os campos `model_tier`, `model_actual`, `tokens_in`, `tokens_out`, `cost_usd`, `wall_seconds` como convenção documentada | Schema atualizado + exemplo preenchido | S (pequeno) |
| T-COST-0.2 | Criar `logs/COST_LEDGER.md` como artefato padrão de todo runtime (uma linha por tarefa concluída), instruído em `IMPLEMENT.md` e no `AGENTS.md` gerado por `copy_runtime()` | Novo artefato + instrução de preenchimento | S |
| T-COST-0.3 | Script `engine/scripts/cost_report.py` — Python puro (mesmo padrão de `validate_media_assets.py`, zero LLM) que lê o ledger e imprime: custo total, custo por fase, custo por agente, custo por tier | Script + saída de exemplo | M |
| T-COST-0.4 | *Baseline run* real — executar (ainda sem nenhuma mudança de tiering) um livro de teste em escala reduzida (ex.: 6-8 capítulos, não o livro comercial inteiro) só para popular o ledger e ter um "antes" medido, não estimado | Ledger populado + relatório baseline | L (depende de rodar a CLI de verdade) |

## 5. Fase 1 — Infraestrutura de dosagem + o "quick win" já existente no motor

### 5.1 Achado importante: o motor já tem meio-caminho andado

`BOOK_SPEC.yaml` já declara `lead_novelist_owned_chapters` (ex.:
`[1, 24]` — abertura e fechamento) e `build_standard_graph()` já usa esse
campo para decidir, capítulo a capítulo, se quem escreve é `LEAD_NOVELIST`
ou `CHAPTER_WRITER`:

```python
if ch in sp.get('lead_novelist_owned_chapters', []):
    groups.append({'agent': 'LEAD_NOVELIST', 'chapters': [ch]})
else:
    ...
    groups.append({'agent': 'CHAPTER_WRITER', 'chapters': grp})
```

Isso significa que **o hook de dosagem por capítulo já existe** — só falta
ligar cada um desses dois agentes a um tier diferente. É o menor esforço com
maior demonstração de valor possível: sem tocar em `build_standard_graph()`,
só marcando `LEAD_NOVELIST` como Tier S e `CHAPTER_WRITER` como Tier M nos
seus `.toml`, o livro inteiro já passa a escrever a maior parte de seu volume
de prosa (todos os capítulos exceto abertura/fechamento) num modelo mais
barato — e isso, sozinho, ataca a maior linha de custo do livro, porque
capítulos de romance são o maior volume de token gerado no pipeline inteiro.

### 5.2 Tarefas de infraestrutura

| ID | Tarefa | Entregável | Esforço |
|---|---|---|---|
| T-COST-1.1 | Criar `engine/MODEL_TIERS.yaml` — mapeamento **tier → modelo concreto**, separado da lista de agentes (permite trocar de fornecedor/modelo sem tocar 68 arquivos) | Novo arquivo de config | S |
| T-COST-1.2 | Adicionar campo `model_tier = "S" \| "M" \| "XS"` a cada um dos 68 `.toml` em `engine/agents/` conforme a tabela de dosagem completa (§6) | 68 arquivos editados (mudança mecânica, mesma linha em cada) | M |
| T-COST-1.3 | Estender `validate_profiles()` em `livingbook.py` para exigir `model_tier` válido em cada agente — mesma disciplina que hoje já existe para `name`/`description`/`developer_instructions` | ~5 linhas em `livingbook.py` | S |
| T-COST-1.4 | Propagar `model_tier` para cada nó do `TASK_GRAPH.yaml` dentro de `build_standard_graph()` — resolvido a partir do `owner` da tarefa, e também por item de `spawn.agents`/`spawn.jobs` (uma única tarefa pode ter subagentes de tiers diferentes, ex. `T013_CHARACTER_BIBLE` spawna `CHILD_VOICE_GUARDIAN`) | Alteração em `task()`/`build_standard_graph()` | M |
| T-COST-1.5 | Atualizar `IMPLEMENT.md`, `CODEX_ENGINE_BOOTSTRAP_PROMPT.md` e o `AGENTS.md` gerado por `copy_runtime()` com a instrução explícita: *"ao spawnar um subagente, use o modelo do `model_tier` declarado na tarefa; nunca suba de tier sem justificativa registrada no log"* | Texto atualizado em 3 arquivos | S |
| T-COST-1.6 | Piloto validando o quick win de §5.1 isoladamente: rodar o mesmo livro de teste da Fase 0 só com `LEAD_NOVELIST`→S / `CHAPTER_WRITER`→M ligados, comparar custo de prosa contra o baseline | Comparação antes/depois no ledger | M |

## 6. Fase 2 — Tabela de dosagem completa (os 68 agentes do motor)

Esta é a peça que "não pode faltar". Classificação de todos os agentes
genéricos do `ENGINE_GRAPH.yaml`, com a razão de cada tier. Frequência
aproximada = quantas vezes o agente é efetivamente invocado num livro de 24
capítulos (extraído da estrutura real do grafo, não estimado no vácuo).

### 6.1 Governança e canon fundacional

| Agente | Tier | Frequência | Por quê |
|---|---|---|---|
| `CANON_GUARDIAN` | **S** | ~6× | Único dono de mutação de canon; erro aqui contamina o livro inteiro e é caro de reverter |
| `EXECUTIVE_EDITOR` | **S** | ~15× | Síntese de conflito entre revisores e aprovação final de wave — ponto de decisão de maior alavancagem do pipeline |
| `BRIEFING_ARCHITECT` | **S** | 1× | Único ponto de leitura do brief cru; define o tom que todo o resto herda — barato de rodar em S por ser 1× |
| `NARRATIVE_ARCHITECT` | **S** | 1× | STORY_BIBLE é a fundação estrutural do livro inteiro |
| `PLOT_ENGINEER` | **S** | 1× | Mapa de dependência de trama — erros aqui geram furos de continuidade caros de corrigir depois |
| `WORLD_ARCHITECT` | **S** | 2× | Define o que é fisicamente/socialmente possível na obra inteira |
| `CHARACTER_PSYCHOLOGIST` | **S** | 1× | Bíblia de personagem é a fundação de toda voz e prosa subsequente |
| `SPEC_ARCHITECT` | XS | 1× | Validação de capacidades é checklist, não julgamento |
| `SCENE_ARCHITECT` | **M** | 24× (1/capítulo) | Alto volume; brief estruturado a partir de fontes já aprovadas — execução competente, não fundação nova |
| `SYMBOLISM_ARCHITECT` | M | 2× | Camada de suporte criativo, não a prosa final |
| `TEMPORAL_ARCHITECT` | M | 1× | Linha do tempo é lógica/consistência de fatos mais que voz literária |

### 6.2 Voz, psicologia e guardiões transversais

| Agente | Tier | Frequência | Por quê |
|---|---|---|---|
| `ANTI_MANIPULATION_GUARDIAN` | **S** | ~30×+ | **Exceção deliberada à regra de frequência** — risco ético é a única categoria de falha inaceitável em qualquer volume |
| `CHILD_VOICE_GUARDIAN` | M | ~2-5× | Guardrail específico de voz, checagem contra critério declarado |
| `EMOTIONAL_PHYSIOLOGY_ARCHITECT` | M | 3× | Conceito repetido de "livro vivo"; aplicação sistemática de um conceito já definido, não invenção |
| `REALISM_ENGINEER` | M | variável | Checagem de plausibilidade contra regras já estabelecidas |
| `PHYSICALITY_AND_BODY_AGENT` | M | ~4×+ (line reviewer) | Nuance literária real, mas checagem sobre texto já escrito |
| `SENSORY_AGENT` | M | ~4×+ | Idem |
| `GENRE_GUARDIAN` | M | ~10×+ | Alta frequência, checagem contra regras de gênero já explícitas |

### 6.3 Prosa — a maior linha de custo do livro

| Agente | Tier | Frequência | Por quê |
|---|---|---|---|
| `LEAD_NOVELIST` | **S** | Capítulos-âncora (abertura/fechamento) + revisões finais | Voz definitiva do livro; ver quick win §5.1 |
| `CHAPTER_WRITER` | **M** | Maioria dos capítulos (ex. 22 de 24) | **Maior alavancagem de custo isolada do plano** — ver §5.1 |
| `DIALOGUE_DIRECTOR` | M | ~8×+ | Revisão de linha, checagem contra padrão de voz já calibrado |
| `LITERARY_STYLE_GUARDIAN` | M | ~10×+ | Checagem contra `VOICE_REFERENCE.md` já aprovado, não criação de voz |
| `SUBTEXT_EDITOR` | M | ~4×+ | Leitura crítica sobre texto existente |
| `EMOTIONAL_REPETITION_AUDITOR` | XS | 1× | Detecção de padrão repetido — próximo de checagem quase-objetiva |
| `READER_VITALS_AGENT` | M | 1× | Documento fundacional único, mas de suporte, não prosa final |
| `PAGE_BREATHING_ARCHITECT` | M | 1× | Idem |

### 6.4 Visual, som — produção de alto volume, baixo risco individual

| Agente | Tier | Frequência | Por quê |
|---|---|---|---|
| `VISUAL_DIRECTOR` | M | ~26× (bíblia + 24 aprovações) | Aprovação contra spec já definida, alta frequência |
| `FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT` | M (definição do FACE_CANON) / **XS** (as 24 checagens `T4xx_FACE_QA`) | 2 + 24 | Definir o cânone facial exige julgamento (M); checar rosto gerado contra cânone já definido 24× é comparação repetitiva — candidata a virar checagem determinística no futuro (documento 03), XS por ora |
| `CHAPTER_IMAGE_DIRECTOR` | M | 24× | Brief estruturado por capítulo contra spec visual já aprovada |
| `IMAGE_GENERATOR` | — | 24× | Fora do escopo de tiering de texto; mesmo princípio se aplica ao modelo de imagem: reservar o gerador mais caro só para capa KDP + 5 Stories comerciais |
| `IMAGE_CONTINUITY_QA` | XS | 24× | Comparação repetitiva contra referência já aprovada |
| `LIVING_SOUNDTRACK_ARCHITECT` | M | 2× | Bíblia de som, feita poucas vezes |
| `SOUND_BIOME_ARCHITECT` | M | 2× | Idem |
| `ENVIRONMENT_ACOUSTIC_EVOLUTION_AGENT` | M | 1× | Documento único |
| `LIVING_SOUND_PROMPT_ENGINEER` | **XS** | 24× (1/capítulo) | Aplicação mecânica de uma bíblia de som já aprovada a um prompt curto por capítulo — caso clássico de Tier XS |

### 6.5 Legal, originalidade — risco alto, frequência baixa

| Agente | Tier | Frequência | Por quê |
|---|---|---|---|
| `LEGAL_EDITOR_BR` | **S** | 1× | Risco legal real; baixa frequência torna o custo de manter em S desprezível |
| `LEGAL_EDITOR_GLOBAL` | **S** | 1× | Idem |
| `COPYRIGHT_ORIGINALITY_AUDITOR` | M | 1× | Checagem de ineditismo, estruturada |

### 6.6 Revisão editorial — o maior número de agentes, o maior potencial de corte

| Agente | Tier | Frequência | Por quê |
|---|---|---|---|
| `DEVELOPMENTAL_EDITOR` | **S** | ~2× | Crítica estrutural de manuscrito inteiro, alto valor, baixa frequência |
| `PLOT_CONTINUITY_REVIEWER` | M | ~5× (4 waves + painel final) | Checagem estruturada contra `PLOT_DEPENDENCY_MAP`/`TIMELINE` já existentes — não é geração, é verificação de fato |
| `CHARACTER_CONTINUITY_REVIEWER` | M | ~4× | Idem, contra `CHARACTER_BIBLE` |
| `WORLD_RULES_REVIEWER` | M | ~4× | Idem, contra `WORLD_RULES` |
| `EMOTIONAL_EDITOR` | M | ~4× | Checagem de impacto emocional contra alvo declarado em `quality_profile.yaml` |
| `PTBR_GRAMMAR_EDITOR` | **XS** | 1-2× | Quase-mecânico; idealmente também ganha um corretor determinístico como primeira passada (fora de escopo aqui) |
| `TYPOGRAPHY_TEXT_REVIEWER` | **XS** | ~2× | Formato, não conteúdo |
| `REDUNDANCY_REVIEWER` | **XS** | ~2× | Detecção de repetição — candidato a virar *script* (documento 03) |
| `CLICHE_REVIEWER` | **XS** | ~2× | Idem — e candidato à fusão com `CLICHE_HUNTER` (fora do escopo de custo puro, ver `02-analise-custo-tempo.md`) |
| `FINAL_PROOFREADER` | **XS** | 2× | Última passada mecânica |

### 6.7 Integração e crítica de mercado

| Agente | Tier | Frequência | Por quê |
|---|---|---|---|
| `MERGE_COORDINATOR` | M | 5× (4 waves + integração) | Montagem de manuscrito é sensível o bastante (protegida por lock exclusivo) para não cair a XS |
| `MASTER_INTEGRATOR` | **S** | 1× | Único ponto de julgamento sobre a coerência do livro inteiro montado |
| `PROTECTED_SCENE_AUDITOR` | **S** | por cena protegida (tipicamente 2-4×) | *Gate* bloqueante nomeado explicitamente como crítico no `BOOK_SPEC`; baixa frequência, altíssimo risco |
| `LITERARY_CRITIC` | **S** | 1× | Julgamento estético final de maior peso no painel de crítica |
| `CINEMA_CRITIC` | M | 1× | Lente secundária, valiosa mas não insubstituível |
| `COMMERCIAL_EDITOR_CRITIC` | M | 1× | Crítica de mercado, estruturada |
| `CLICHE_HUNTER` | **XS** | 1× | Duplicado funcional de `CLICHE_REVIEWER` |

### 6.8 Layout, KDP, tradução, entrega

| Agente | Tier | Frequência | Por quê |
|---|---|---|---|
| `BOOK_LAYOUT_ARCHITECT` | M | ~2× | Bíblia de layout, estruturada |
| `TABLE_OF_CONTENTS_AGENT` | **XS** | 1× | Geração mecânica de sumário |
| `IMAGE_LAYOUT_AGENT` | M | 1× | Relatório de posicionamento contra regras já definidas |
| `KDP_FORMATTER` | M | 2× | Formatação contra especificação KDP já pesquisada; candidato a *renderer* determinístico no futuro (documento 03) |
| `KDP_REQUIREMENTS_RESEARCHER` | M | 1× | Pesquisa + resumo — erro aqui custa retrabalho caro no *gate* de entrega, não vale arriscar em XS |
| `TRANSLATION_ARCHITECT` | M | 1× | Planejamento, não prosa final |
| `LITERARY_TRANSLATOR_EN` | **M** | Alto volume (quase o livro inteiro, quando habilitado) | **Segunda maior alavancagem de custo do plano** — tradução é transformação contra uma fonte já fixada (o manuscrito PT-BR final), não criação original; não precisa de Tier S |
| `ENGLISH_CHILD_VOICE_GUARDIAN` | M | variável | Guardrail específico, mesmo raciocínio de `CHILD_VOICE_GUARDIAN` |
| `ENGLISH_LITERARY_EDITOR` | M | 1× | Polimento contra a tradução já feita |
| `CULTURAL_ADAPTATION_GUARDIAN` | M | 1× | Glossário estruturado |
| `MEDIA_AND_KDP_AGENT` | M | ~3× | Copy de marketing, estruturado, não voz literária do livro |
| `DELIVERY_AGENT` | **XS** | 3× | Manifesto e empacotamento final, mecânico |
| `MASTER_ORCHESTRATOR` | M | ~8× | Roteamento e consolidação de estado; precisa de confiabilidade de instrução, não de criatividade |

### 6.9 Leitura agregada da tabela — **status: implementado e medido**

Esta tabela foi aplicada aos 68 `.toml` de `engine/agents/` (mais os 2
agentes específicos de `books/a_morte_ainda_nao_nasceu/agents/`), com um
*override* de nível de tarefa para o caso especial de
`FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT` (padrão `T4??_FACE_QA` → XS,
independente do tier base do agente). Compondo o grafo real de
`a_morte_ainda_nao_nasceu` (24 capítulos, 248 tarefas, 70 agentes) e contando
os nós resultantes:

| | Nível do dono da tarefa (248 nós) | + chamadas de subagente via `spawn` (142) | Total combinado (390) |
|---|---|---|---|
| **S** | 48 (19%) | 50 | 98 (25%) |
| **M** | 146 (59%) | 85 | 231 (59%) |
| **XS** | 54 (22%) | 7 | 61 (16%) |

Isso é uma medição real, não a estimativa da rodada anterior deste
documento — e vale registrar a diferença: a fração de Tier S saiu **maior**
do que a projeção inicial de 12-15% (chegou a 25%). A causa é específica
deste livro: `a_morte_ainda_nao_nasceu` tem tema eticamente denso (morte,
gravidez, cuidado paliativo) e por isso seus `agent_packs` convocam com
frequência os guardiões de alto risco (`ANTI_MANIPULATION_GUARDIAN`,
`CONSENT_AND_CARE_GUARDIAN`, `LIMINALITY_GUARDIAN` — os três em Tier S por
desenho, ver §2) em múltiplos painéis de revisão. Um livro com menos
guardiões éticos por capítulo teria uma fração de S mais próxima da
projeção original. De qualquer forma, mesmo com Tier S em 25% em vez de
12-15%, isso ainda é uma inversão completa do estado anterior (**100% em
Tier S**, por ausência total de roteamento) — o corte de custo projetado de
50-70% permanece plausível, só que com uma margem um pouco mais conservadora
para livros tematicamente densos como este.

## 7. Fase 1B (opcional, fora do caminho crítico) — impor a dosagem por código

A Fase 1 depende de a sessão de execução *seguir a instrução* de usar o tier
certo — é forte, mas ainda é convenção. Para tarefas de Tier XS que são
quase-checklist (`FINAL_PROOFREADER`, `TYPOGRAPHY_TEXT_REVIEWER`,
`DELIVERY_AGENT`, `TABLE_OF_CONTENTS_AGENT`), é possível ir além e escrever um
*runner* leve (`engine/scripts/run_task.py`) que chama a API do modelo
correspondente diretamente, sem depender da CLI hospedeira respeitar a
instrução. Isso é o primeiro passo em direção ao "orquestrador real" do
documento 03, mas aqui teria escopo deliberadamente pequeno: só os agentes
Tier XS mais mecânicos, como prova de conceito. **Não é bloqueante para o
resto deste plano** — é o passo natural se, depois da Fase 1, a telemetria
mostrar que a sessão de execução não está respeitando a instrução de tier
com consistência suficiente.

## 8. Sequenciamento recomendado

```
Sprint 1 (Fundação)     Fase 0 (telemetria) + Fase 1 (infraestrutura + quick win LEAD_NOVELIST/CHAPTER_WRITER)
Sprint 2 (Dosagem cheia) Fase 2 aplicada nos 68 agentes, usando o ledger para validar tier a tier
Sprint 3 (Reforço)       Fase 1B, só se a Fase 2 mostrar desvio entre tier declarado e custo real observado
```

Fase 0 e o início da Fase 1 (T-COST-1.1 a T-COST-1.5) podem correr em
paralelo — não há dependência real entre criar o *ledger* e criar o campo
`model_tier`. O que depende de sequência é T-COST-1.6 (o piloto do quick win)
e toda a Fase 2: **precisam do ledger da Fase 0 já funcionando** para provar
que a dosagem está de fato economizando, e não só teoricamente correta.

## 9. Próximo passo

Este documento é o plano. Antes de tocar em qualquer arquivo do motor
(`engine/agents/*.toml`, `livingbook.py`, `IMPLEMENT.md`), a confirmação
recomendada é: começar pela Fase 0 + o quick win isolado da Fase 1 (§5.1),
porque é o menor conjunto de mudanças que já produz um número real e
comparável — sem esperar a tabela completa de 68 agentes estar 100%
aplicada.
