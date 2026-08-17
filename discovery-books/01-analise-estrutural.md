# Análise Estrutural — PEDRO_ARTE_LIVING_BOOK_ENGINE_v1

> Metodologia: leitura direta de todo o código-fonte relevante (`engine/scripts/livingbook.py`,
> `engine/scripts/runtime_taskgraph.py`, `engine/scripts/validate_media_assets.py`),
> de todos os arquivos de especificação declarativa (`ENGINE_GRAPH.yaml`, `BOOK_SPEC.yaml`,
> `BOOK_GRAPH.yaml`, `chapter_architecture.yaml`, `immutable_rules.yaml`, `protected_scenes.yaml`,
> `quality_profile.yaml`, `capability_requirements.yaml`), de amostras representativas dos
> 68 perfis de agente em `engine/agents/*.toml`, dos 6 JSON Schemas em `engine/contracts/`,
> e do único runtime já materializado (`runtime/antes-que-as-criancas-crescam/`). Nenhum
> arquivo foi alterado. Onde a análise depende de inferência (porque não há execução real
> registrada no repositório), isso é sinalizado explicitamente.

---

## 1. As três camadas

```
engine/            → motor reutilizável (agnóstico de obra)
books/<slug>/      → DNA literário de UMA obra ("BOOK_PACKAGE")
runtime/<slug>/    → merge gerado e executável de engine + livro
```

Isso é declarado explicitamente em `docs/ARCHITECTURE.md` e reforçado em
`AGENTS.md` ("separation rule"): o `engine/` **não pode** conter nomes de
personagem, títulos de capítulo, frases finais, vetos de gênero ou regras de
mundo — essas coisas pertencem exclusivamente ao pacote do livro. Esta é a
decisão arquitetural mais importante do repositório e está bem executada: hoje
existem dois livros plugáveis (`o_jardim_dos_doze`, `a_morte_ainda_nao_nasceu`)
consumindo o mesmo motor sem duplicar uma única linha de orquestração.

`docs/MIGRATION_FROM_SUPER_PROMPTS.md` documenta a motivação: antes existia
"um Codex prompt gigante = DNA criativo + orquestração + arquitetura de agentes
+ pipeline de entrega" por livro (evidência residual disso ainda vive em
`books/o_jardim_dos_doze/CODEX_RUN_PROMPT.md`, um artefato do modelo antigo,
com nomenclatura de tarefas — `T000_BOOT_PROJECT` … `T370_DELIVERY` — que **não
bate** com a numeração atual do `TASK_GRAPH.yaml` gerado — `T000_INITIALIZE_RUNTIME`
… `T805_FINAL_DELIVERY`. É lixo/dívida documental de uma migração incompleta,
inofensivo mas confuso para quem chegar ao repo pela primeira vez).

## 2. Composição: como `engine + book` viram `runtime`

`engine/scripts/livingbook.py` é **Python puro, sem nenhuma chamada de LLM**.
É um gerador/validador de grafo, não um orquestrador de execução. Comandos:

| Comando | O que faz |
|---|---|
| `validate-engine` | Confere que todo agente referenciado em `ENGINE_GRAPH.yaml` tem um `.toml` existente com `name`/`description`/`developer_instructions`. |
| `validate-book` | Confere consistência do `BOOK_SPEC.yaml` (contagem de capítulos = títulos = waves, arquivos referenciados existem, agentes dos *packs* existem no engine ou no livro). |
| `compose --book <path>` | Constrói o grafo (`build_standard_graph`), valida (`validate_graph`: ciclos, IDs duplicados, *owners*/dependências desconhecidas) e materializa `runtime/<slug>/`. |
| `smoke-test --runtime <path>` | Confere que o runtime materializado tem os arquivos esperados e que a primeira tarefa `READY` é `T000_INITIALIZE_RUNTIME`. |
| `ready --runtime <path>` | Lista as tarefas atualmente `READY`. |
| `new-book --slug --title --chapters` | Faz o scaffold de um pacote de livro novo, com waves de escrita calculadas automaticamente (`ceil(chapters/5)` capítulos por wave). |

`build_standard_graph()` é o coração do motor: uma função de ~140 linhas que
**gera proceduralmente** de 244 a 248 nós de tarefa (medido diretamente nos dois
livros reais do repositório, ver seção 8) a partir de:

- fases fixas do motor (`BOOTSTRAP`, `CANON`, `LIVING_BOOK`, `VOICE_CALIBRATION`,
  `INTEGRATION`, `LEGAL`, `DELIVERY` — sempre presentes);
- fases parametrizadas pelo número de capítulos (`CHAPTER_BRIEFS` gera 1 tarefa
  por capítulo; `VISUAL_PRODUCTION` gera 5 tarefas por capítulo);
- fases condicionais por *feature flag* do `BOOK_SPEC.yaml`
  (`features.images.enabled`, `features.living_sound.enabled`,
  `features.translation_preparation.enabled`, `features.kdp_docx.enabled`);
- *waves* de escrita definidas no `BOOK_SPEC.yaml` (`writing_waves`), cada uma
  expandida em 7 subtarefas fixas (preflight → write → merge → review →
  revision → canon_update → approval);
- extensões declaradas em `BOOK_GRAPH.yaml` (`additional_tasks`,
  `gate_extensions`, `custom_validators`) — o ponto de extensão para
  peculiaridades de uma obra específica sem tocar no motor.

Isso confirma a frase do `docs/ARCHITECTURE.md`: *"a new book does not need a
new 1,500-line orchestration prompt. It needs a new book package."* É uma
arquitetura genuinamente **declarativa e paramétrica**, não um template
copiado/colado por livro.

## 3. Taxonomia dos agentes (68 genéricos + agentes específicos por livro)

Todos os agentes vivem como arquivos `.toml` minúsculos (4 campos: `name`,
`description`, `developer_instructions` de 3-7 linhas, nada mais — **sem** campo
de modelo, sem lista de ferramentas, sem temperatura, sem limite de tokens).
Isso por si só é um dado estrutural relevante para a Parte 2 desta análise.

Agrupando os 68 agentes genéricos por função (classificação minha, não existe
no repo):

| Grupo | Agentes (exemplos) | Papel |
|---|---|---|
| **Meta/Governança** | `MASTER_ORCHESTRATOR`, `EXECUTIVE_EDITOR`, `CANON_GUARDIAN` | Donos exclusivos de estado, locks e síntese de conflito |
| **Arquitetura de canon** | `BRIEFING_ARCHITECT`, `SPEC_ARCHITECT`, `NARRATIVE_ARCHITECT`, `PLOT_ENGINEER`, `SCENE_ARCHITECT`, `SYMBOLISM_ARCHITECT`, `TEMPORAL_ARCHITECT`, `WORLD_ARCHITECT` | Constroem as "bíblias" fundacionais |
| **Psicologia/voz** | `CHARACTER_PSYCHOLOGIST`, `CHILD_VOICE_GUARDIAN`, `EMOTIONAL_PHYSIOLOGY_ARCHITECT`, `REALISM_ENGINEER`, `PHYSICALITY_AND_BODY_AGENT`, `SENSORY_AGENT` | Definem quem os personagens são e como soam |
| **Guardiões de gênero/ética** | `GENRE_GUARDIAN`, `ANTI_MANIPULATION_GUARDIAN` | Vetoes transversais |
| **Prosa** | `LEAD_NOVELIST`, `CHAPTER_WRITER`, `DIALOGUE_DIRECTOR`, `LITERARY_STYLE_GUARDIAN`, `SUBTEXT_EDITOR`, `EMOTIONAL_REPETITION_AUDITOR`, `READER_VITALS_AGENT`, `PAGE_BREATHING_ARCHITECT` | Escrevem e regulam o texto |
| **Visual** | `VISUAL_DIRECTOR`, `FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT`, `CHAPTER_IMAGE_DIRECTOR`, `IMAGE_GENERATOR`, `IMAGE_CONTINUITY_QA` | Pipeline de imagem por capítulo |
| **Som (Living Sound)** | `LIVING_SOUNDTRACK_ARCHITECT`, `SOUND_BIOME_ARCHITECT`, `ENVIRONMENT_ACOUSTIC_EVOLUTION_AGENT`, `LIVING_SOUND_PROMPT_ENGINEER` | Geram **prompts** de som, não áudio |
| **Legal/originalidade** | `LEGAL_EDITOR_BR`, `LEGAL_EDITOR_GLOBAL`, `COPYRIGHT_ORIGINALITY_AUDITOR` | Compliance e ineditismo |
| **Revisão editorial** | `DEVELOPMENTAL_EDITOR`, `PLOT_CONTINUITY_REVIEWER`, `CHARACTER_CONTINUITY_REVIEWER`, `WORLD_RULES_REVIEWER`, `EMOTIONAL_EDITOR`, `PTBR_GRAMMAR_EDITOR`, `TYPOGRAPHY_TEXT_REVIEWER`, `REDUNDANCY_REVIEWER`, `CLICHE_REVIEWER`, `FINAL_PROOFREADER` | Camadas sucessivas de leitura crítica |
| **Integração** | `MERGE_COORDINATOR`, `MASTER_INTEGRATOR`, `PROTECTED_SCENE_AUDITOR` | Costuram o manuscrito e auditam cenas protegidas |
| **Crítica de mercado** | `LITERARY_CRITIC`, `CINEMA_CRITIC`, `COMMERCIAL_EDITOR_CRITIC`, `CLICHE_HUNTER` | Painel de crítica pré-lançamento |
| **Layout/KDP** | `BOOK_LAYOUT_ARCHITECT`, `TABLE_OF_CONTENTS_AGENT`, `IMAGE_LAYOUT_AGENT`, `KDP_FORMATTER`, `KDP_REQUIREMENTS_RESEARCHER` | Produção do DOCX/KDP |
| **Tradução** | `TRANSLATION_ARCHITECT`, `LITERARY_TRANSLATOR_EN`, `ENGLISH_CHILD_VOICE_GUARDIAN`, `ENGLISH_LITERARY_EDITOR`, `CULTURAL_ADAPTATION_GUARDIAN` | Preparação (não execução completa) de versão EN |
| **Entrega** | `MEDIA_AND_KDP_AGENT`, `DELIVERY_AGENT` | Pacote de mídia e manifesto final |

Além disso, um livro pode declarar **agentes próprios** em
`books/<slug>/agents/*.toml` (ex.: `liminality_guardian.toml`,
`consent_and_care_guardian.toml` em `a_morte_ainda_nao_nasceu`) — personas
adicionais só relevantes para aquela obra, plugadas via `agent_packs.book_agents`
no `BOOK_SPEC.yaml`.

## 4. O ciclo de vida da tarefa e o motor de estado

`runtime_taskgraph.py` (copiado para dentro de cada runtime gerado) é um
motor de estado de ~80 linhas, também 100% Python puro:

- **Estados possíveis**: `PENDING, READY, SPAWNING, RUNNING, WAITING_DEPENDENCIES,
  UNDER_REVIEW, REVISION_REQUIRED, BLOCKED, FAILED, APPROVED, CANON_APPROVED, FINAL`.
- **`compute()`**: recalcula, para cada tarefa, se todas as dependências (`depends_on`,
  que podem apontar para outra tarefa ou para um *gate*) estão em um estado de
  sucesso (`APPROVED|CANON_APPROVED|FINAL`); se sim, e a tarefa ainda não foi
  tocada, ela vira `READY`.
- **Gates**: um *gate* é uma barreira que agrega N tarefas (`requires`). Fica
  `PENDING` até todas as tarefas exigidas serem sucesso; se o gate tem
  `custom_validators`, ele fica em `VALIDATION_REQUIRED` até um comando de
  shell externo (registrado em `spec.custom_validators`) rodar e retornar 0.
  Só existe **um** validador de fato registrado no motor genérico:
  `V_MEDIA_ASSET_PACKAGE` → `python scripts/validate_media_assets.py`.
- **`mark <task> <state>`**: comando manual — é a própria LLM executando o
  trabalho que decide chamar isso para declarar uma tarefa como concluída. Não
  há verificação automática de que o artefato declarado em `outputs` realmente
  foi escrito antes de aceitar o `mark` (exceto para o único gate com validador
  de mídia).
- **`validate-gate <GATE_ID>`**: roda os validadores customizados do gate e
  persiste `PASS`/`FAIL` em `validator_results`.

Ou seja: **o controle de estado é cooperativo, não coercitivo.** A "verdade"
sobre o progresso do livro é o que a LLM escreve em `PROJECT_STATUS.yaml`
via `mark`. O motor garante *consistência estrutural* (você não pode avançar
uma tarefa cujas dependências não estão em sucesso) mas **não garante
veracidade** de que o trabalho foi de fato bem-feito — isso é delegado
inteiramente ao julgamento da própria LLM em cada papel, e ao único checador
determinístico que existe (dimensões/DPI de imagem via Pillow).

## 5. Contratos e schemas (governança "por convenção", não "por execução")

`engine/contracts/*.schema.json` define 6 formatos JSON Schema:
`BOOK_SPEC`, `CANON_PROPOSAL`, `CHAPTER_SCORECARD`, `IMAGE_APPROVAL`,
`REVIEW_FINDING`, `TASK_RESULT`. Achado relevante: **nenhum script do
repositório carrega ou valida contra esses schemas em tempo de execução.**
`validate_book_data()` em `livingbook.py` reimplementa manualmente as
checagens de `BOOK_SPEC.yaml` sem tocar em `BOOK_SPEC.schema.json`. Os
schemas existem como **documentação estrutural para a LLM** (formato esperado
de um `TaskResult`, de um `ReviewFinding`, de um `ChapterScorecard`) — um
contrato de fato "seguido na fé", não "verificado em código". Isso é
consistente com o resto do design (blackboard cooperativo), mas é uma lacuna
real de engenharia de confiabilidade.

## 6. Interação entre agentes: *blackboard* baseado em arquivo, não *message passing*

Não existe fila, broker de mensagens ou API entre agentes. A coordenação é:

1. **Spawn declarado no próprio nó da tarefa** (`spawn: {mode: PARALLEL_SUBAGENTS,
   agents: [...] | jobs: [...] | foreach_chapter: "1..N", wait_for_all: true}`).
   O agente dono da tarefa (tipicamente `MASTER_ORCHESTRATOR` ou
   `EXECUTIVE_EDITOR`) é instruído a criar explicitamente esses subagentes,
   entregando a cada um **apenas**: tarefa, inputs declarados, canon necessário,
   output esperado, critérios de aceite, vocabulário de reprovação (isso está
   escrito literalmente em `CODEX_ENGINE_BOOTSTRAP_PROMPT.md`), e esperar por
   todos antes de consolidar.
2. **Locks exclusivos** declarados em `ENGINE_GRAPH.spec.locks`
   (`CANON_WRITE`, `STORY_BIBLE_WRITE`, `CHARACTER_BIBLE_WRITE`,
   `TIMELINE_WRITE`, `MANUSCRIPT_FINAL_WRITE`, `MANUSCRIPT_MERGE`,
   `FACE_CANON_WRITE`, `DOCX_BUILD`, `DELIVERY_BUILD`) — mas são **metadados
   textuais**, não *locks* de SO/arquivo de verdade. A serialização real
   depende inteiramente de a LLM/orquestrador respeitar a convenção.
3. **Doutrina de propriedade** (`AGENTS.md`): `CANON_GUARDIAN` é o único que
   muta canon; `LEAD_NOVELIST` é o único dono da prosa final;
   `EXECUTIVE_EDITOR` resolve conflitos editoriais; agentes de revisão têm
   `reviewer_write_access: {manuscript: false, canon: false, reports: true}`
   — só podem escrever em `/reviews/*`. Isso é reforçado por uma frase **copiada
   literalmente em todos os 68 `.toml`**: *"Review agents report findings and
   do not silently rewrite final prose."* — uma barreira de convenção repetida
   massivamente, não uma barreira técnica (sandboxing de escrita por agente).
4. **Padrão de síntese em comitê**: em cada wave e na integração final, N
   críticos escrevem relatórios independentes em `/reviews/`,
   `EXECUTIVE_EDITOR` sintetiza tudo em uma diretriz única
   (`MASTER_REVISION_DIRECTIVE.md`), e só então `LEAD_NOVELIST` aplica a
   revisão — um funil claro de muitos-para-um-para-um, que evita escrita
   caótica simultânea mas multiplica leituras do mesmo texto (ver Parte 2).

## 7. Onde roda o *runtime* (a pergunta mais importante)

**Não há runtime de execução dentro deste repositório.** `runtime/<slug>/`
é apenas um diretório de arquivos gerados (YAML, Markdown, pastas vazias) —
não um processo, não um servidor, não uma fila. A evidência mais forte disso
é `.codex/config.toml`, gerado por `copy_runtime()`:

```toml
[agents]
max_threads = 8
max_depth = 1
job_max_runtime_seconds = 1800
```

Essa é a sintaxe nativa de configuração de agentes/subagentes de uma
ferramenta de *coding agent* estilo **Codex CLI** (o próprio nome da pasta,
`.codex/`, e o vocabulário de `AGENTS.md`/`IMPLEMENT.md` confirmam isso — o
mesmo padrão de arquivo `AGENTS.md` também é reconhecido por outras CLIs
agenticas, incluindo Claude Code). Ou seja: **o "runtime" de fato é a sessão
de uma LLM rodando dentro de um coding agent local (ou em nuvem do
fornecedor), fora do controle deste repositório.** O repositório só entrega:
o grafo (`TASK_GRAPH.yaml`), o estado (`PROJECT_STATUS.yaml`), as personas
(`.codex/agents/*.toml`) e os runbooks em Markdown que instruem essa sessão
sobre como se comportar.

**Confirmação empírica dentro do próprio repo:** o runtime já materializado,
`runtime/antes-que-as-criancas-crescam/` (30 capítulos, ~330 tarefas), tem
**100% das tarefas em `PENDING`** e as pastas `manuscript/`, `outputs/`,
`images/` contêm apenas o `AGENTS.md` de instrução — nenhum capítulo, nenhuma
imagem, nenhum DOCX. Nota-se também que o pacote de livro original que gerou
esse runtime (`books/antes-que-as-criancas-crescam/`) **não existe mais** em
`books/` (foi substituído pelos dois livros atuais) — o runtime é órfão,
sobrevivendo como prova de composição bem-sucedida, não como execução real.
**Conclusão honesta:** este repositório, tal como entregue, nunca produziu um
livro de ponta a ponta dentro de si mesmo — ele é um *scaffold* estrutural e
declarativo, validado por testes de composição/fumaça, mas a "fábrica" só
liga quando um agente de código externo abre o repo e começa a executar o
`IMPLEMENT.md`.

## 8. Números reais (extraídos programaticamente, sem alterar o repo)

Rodei `build_standard_graph()` em memória (sem chamar `compose`, portanto sem
escrever nada em disco) para os dois pacotes de livro atuais:

| | `o_jardim_dos_doze` (24 cap.) | `a_morte_ainda_nao_nasceu` (24 cap.) |
|---|---|---|
| Nós de tarefa | 244 | 248 |
| *Gates* (todos bloqueantes) | 16 | 17 |
| Agentes disponíveis | 68 | 70 |
| Invocações reais de LLM estimadas (dono da tarefa + subagentes *spawned*) | **≈ 409** | ≈ 420 |
| Fase com mais tarefas | `VISUAL_PRODUCTION`: 120 (24 cap. × 5 subtarefas) | idem |
| Tarefa com maior *fan-out* de subagentes | `T503_SOUND_PROMPTS`: 25 (1 por capítulo) | idem |

Essa estimativa de ~409 invocações **não inclui**: laços de
`REVISION_REQUIRED`, o ciclo `STOP → FIX → REVALIDATE → CONTINUE` sempre que
um *gate* falha, nem o fato de que uma única "invocação de agente" numa CLI
agentica real normalmente consome vários turnos internos de raciocínio/uso de
ferramenta. É um piso, não um teto.

## 9. Inputs e outputs — respostas diretas aos 7 pontos pedidos

### 9.1 De onde a LLM lê o briefing para começar a análise

Em dois momentos distintos:

- **Autoria do pacote (uma vez, por humano/editor)**: o "briefing" no sentido
  amplo é o conjunto de arquivos em `books/<slug>/` —
  `CREATIVE_BRIEF.md` (pitch curto) e `BOOK_CONSTITUTION.md` (leis mais
  profundas da obra), declarados explicitamente como `spec.creative_sources`
  no `BOOK_SPEC.yaml`. Não existe formulário, UI ou chat — é edição direta de
  arquivos de texto, com `livingbook.py new-book` fazendo o scaffold inicial.
- **Consumo pela LLM (início de cada execução)**: a sequência obrigatória é
  `README.md` → `AGENTS.md` (raiz) → `engine/IMPLEMENT.md` →
  `engine/ENGINE_GRAPH.yaml` → escolher **um** pacote de livro → `compose` →
  ler `runtime/<slug>/AGENTS.md`, `IMPLEMENT.md`, `TASK_GRAPH.yaml`,
  `project_state/PROJECT_STATUS.yaml`. A primeira tarefa real do grafo,
  `T010_MASTER_BRIEF`, é executada pelo agente `BRIEFING_ARCHITECT`, que lê
  `/book/CREATIVE_BRIEF.md` + `/book/BOOK_CONSTITUTION.md` e escreve
  `/specs/MASTER_BRIEF.md` — o briefing "cru" só é lido uma vez; a partir daí
  todo o resto do sistema lê a versão normalizada (`MASTER_BRIEF.md`).

### 9.2 Como a LLM entende o que precisa ser feito

Por composição de **cinco camadas textuais redundantes**, nenhuma delas
executável isoladamente:

1. Persona do agente (`.toml`) — define **quem** ele é e seus limites (3-7 linhas).
2. Nó da tarefa em `TASK_GRAPH.yaml` — define **o quê**: `inputs`, `outputs`,
   `parameters`, `locks`, `spawn`. É o campo mais próximo de uma "especificação
   executável", mas ainda é metadado estrutural, não uma descrição em
   linguagem natural da tarefa.
3. `IMPLEMENT.md` (motor) — define o **runbook genérico** (ciclo de vida,
   receita de wave, regra de gate).
4. Arquivos de canon/constraint (`immutable_rules.yaml`, `protected_scenes.yaml`,
   `quality_profile.yaml`) — definem **os limites de aceitação**.
5. `ENGINE_GRAPH.spec.protocols` / `rejection_states` — definem o
   **vocabulário de reprovação** (`CANON_CONFLICT`, `WORLD_RULES_FAILURE`,
   `FACE_IDENTITY_FAILURE`, etc.).

Não existe um campo de "critério de aceite" em linguagem natural por tarefa —
a LLM precisa **inferir** "pronto" combinando essas cinco fontes. É um
contrato implícito, sustentado por repetição textual e por confiança na
capacidade de raciocínio do modelo, não por verificação de máquina (exceto
para a única validação Pillow de imagem).

### 9.3 Como são as interações entre os agentes

Ver seção 6 acima: *blackboard* em arquivo + spawn explícito de subagentes
declarado no grafo + locks exclusivos por convenção + funil comitê-de-críticos
→ editor executivo → romancista-líder. Não há passagem de mensagem direta
entre dois agentes-pares; toda comunicação passa pelo sistema de arquivos do
runtime e é mediada por um agente coordenador (`MASTER_ORCHESTRATOR` ou
`EXECUTIVE_EDITOR`).

### 9.4 Como é o controle de estado e artefatos

`project_state/PROJECT_STATUS.yaml` é a fonte única de verdade de estado
(tarefas + *gates* + resultados de validador + locks ativos + *findings*
bloqueantes), recalculada por uma função pura (`compute()`) a cada `refresh`.
Artefatos são organizados em ~25 diretórios padronizados dentro do runtime
(`specs/`, `canon/`, `briefs/chapters/`, `manuscript/{raw,revised,approved,final}/`,
`reviews/`, `integration/`, `living_book/`, `images/{canon,chapters,prompts,approved,rejected}/`,
`sound/`, `translation/`, `legal/`, `layout/`, `media/outputs/{cover,instagram_stories}/`,
`outputs/`, `logs/`). O `ENGINE_GRAPH.yaml` declara *bundles* nomeados de
artefatos esperados (`CANON_CORE`, `LIVING_BOOK_CORE`, `VISUAL_CANON`,
`SOUND_CANON`, `MEDIA_DELIVERY_CORE`) — uma checklist, não uma validação
automática (só a checklist de mídia final tem checador real). Não há banco de
dados, versionamento próprio, nem histórico de revisões além do que o próprio
Git do repositório capturar.

### 9.5 Onde é feito o *runtime*

Ver seção 7. Resposta curta: **fora do repositório**, dentro de uma sessão de
CLI agentica (Codex CLI, a julgar pela pasta `.codex/`) que interpreta os
arquivos gerados. O repositório fornece o roteiro; não é o palco.

### 9.6 Quais são os *outputs*

- **Manuscrito final**: `manuscript/final/MANUSCRIPT_FINAL_PTBR.{md,txt}`.
- **KDP**: `outputs/KDP_DRAFT.docx` → `outputs/BOOK_KDP_FINAL.docx`.
  `python-docx>=1.1.0` **está** declarado em `requirements.txt`, mas **não é
  importado por nenhum script do repositório** — é uma dependência instalada
  para o `KDP_FORMATTER` usar ad-hoc, não um gerador de DOCX pronto. Na
  prática, a criação do binário depende de a ferramenta hospedeira executar
  esse código.
- **Imagens**: `images/approved/chapter_NN.jpg` (1/capítulo) +
  `images/canon/FACE_CANON.md`, `CHARACTER_VISUAL_BIBLE.md`.
- **Mídia comercial obrigatória** (bloqueia entrega via `GATE_MEDIA_ASSETS`):
  `media/outputs/cover/BOOK_COVER_KDP.jpg` (1600×2560px, RGB, ≥300 DPI,
  <50 MB) + exatamente 5 `media/outputs/instagram_stories/story_0{1..5}.jpg`
  (1080×1920px) — **este é o único artefato do repositório inteiro com
  validação automática de verdade** (`validate_media_assets.py`, via Pillow).
- **Som**: apenas *prompts* de texto (`sound/prompts/CHAPTER_NN_SOUND_PROMPT.md`)
  — não há síntese de áudio real no repositório.
- **~20 documentos de "bíblia"** (STORY_BIBLE, CHARACTER_BIBLE, WORLD_BIBLE,
  TIMELINE, CANON_REGISTRY.yaml, LIVING_BOOK_BIBLE, etc.) e dezenas de
  relatórios de revisão — são "memória de trabalho" permanentemente
  persistida, não conteúdo voltado ao leitor, mas contam integralmente para o
  custo de token (ver Parte 2).
- **Manifesto de entrega**: `outputs/DELIVERY_MANIFEST.md` +
  `project_state/FINAL_DELIVERY_APPROVED` (arquivo-sentinela vazio que marca
  conclusão).

### 9.7 Onde é feito o *input*

Dois canais, nenhum deles um chat/formulário:

- **Input de autoria** (antes da execução): os ~10 arquivos YAML/MD dentro de
  `books/<slug>/` (ver 9.1), escritos manualmente ou via scaffold do
  `livingbook.py new-book`.
- **Input de execução** (durante o run): a própria LLM relendo seus artefatos
  anteriores (canon, briefs, reviews) conforme avança no grafo — um sistema
  fechado, sem necessidade de intervenção humana a cada passo
  (`execution_policy.mode: AUTONOMOUS`,
  `continue_without_user_confirmation: true`), exceto quando um
  `CAPABILITY_BLOCKER` é emitido (ex.: falta de acesso à internet para
  `T699_KDP_REQUIREMENTS_REFRESH`, ou falta de capacidade real de geração de
  imagem) — nesses casos o motor está desenhado para **parar e sinalizar**, não
  fingir sucesso.

## 10. Avaliação crítica da estrutura (pontos fortes e frágeis)

**Pontos fortes genuínos:**
- Separação motor/obra é limpa e comprovadamente reutilizável (2 livros reais
  no repo, zero acoplamento cruzado).
- Composição procedural do grafo a partir de *feature flags* é elegante e
  evita duplicação — a extensão certa (adicionar uma fase condicional) é
  barata em código.
- Doutrina de propriedade exclusiva (canon/prosa/decisão) é uma boa prática
  editorial transposta para agentes, e evita o caos clássico de "todo agente
  edita tudo".
- O padrão de validação determinística para mídia (`validate_media_assets.py`)
  é exatamente o tipo de engenharia que falta no resto do sistema — deveria
  ser o modelo, não a exceção.

**Pontos frágeis (fundamentam a Parte 2 e 3 desta análise):**
- Zero seleção de modelo por tarefa — toda a diferenciação de "papel" é
  textual, nenhuma é de custo/capacidade.
- Contratos (JSON Schema) existem mas não são verificados em código — governança
  "na fé".
- *Locks* são metadados, não mecanismos — a integridade depende inteiramente
  da disciplina da própria LLM dentro de uma única sessão.
- 16-17 *gates* **todos bloqueantes** força serialização total do pipeline
  mesmo onde a dependência real é parcial (ex.: produção visual não deveria
  precisar esperar o manuscrito congelado inteiro para começar a *rascunhar*
  prompts).
- Nenhuma telemetria de custo/token em lugar nenhum do repositório — não dá
  para otimizar o que nunca foi medido.
- Sobreposição de papéis de revisão (`CLICHE_REVIEWER` vs. `CLICHE_HUNTER`;
  `PLOT_CONTINUITY_REVIEWER` aparece tanto no painel de wave quanto no painel
  de crítica final) sugere que o *design* cresceu organicamente sem uma
  passada de consolidação.

Estas observações são a ponte direta para as Partes 2 e 3.
