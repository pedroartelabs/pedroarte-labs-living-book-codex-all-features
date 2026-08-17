# Como Executar um Livro — Guia Passo a Passo

> Este guia responde a uma pergunta prática: **eu tenho uma ideia de livro,
> como faço o motor produzi-lo de ponta a ponta?** Ele não repete a análise
> arquitetural — para isso, veja `docs/ARCHITECTURE.md` e a pasta
> `discovery-books/`. Aqui é comando, arquivo e ordem: o que rodar, onde
> escrever o roteiro, como pedir a execução, e onde os resultados aparecem.
>
> Convenção usada abaixo: `<slug>` é o identificador do seu livro (letras
> minúsculas, números e hífen — vira o nome da pasta em `books/` e
> `runtime/`). Substitua por algo como `meu-romance` ou `a-cidade-de-vidro`.

---

## Visão geral em uma tela

```
1. Você escreve o "DNA" do livro em books/<slug>/         (o roteiro vive aqui)
2. O motor valida e compõe                                 → runtime/<slug>/
3. Você abre runtime/<slug>/ no Claude Code e pede a execução
4. A sessão executa o grafo de tarefas: canon → capítulos → revisão →
   imagens → KDP → entrega — parando nos pontos que você aprova
5. Os resultados finais aparecem em runtime/<slug>/manuscript/final/,
   outputs/ e media/outputs/
```

Nada disso reescreve o motor (`engine/`). Você só cria arquivos dentro de
`books/<slug>/` e aprova pontos de controle — a "fábrica" já existe.

---

## Antes de começar

### 1. Ambiente Python

O motor precisa de um interpretador com as dependências instaladas. Use
sempre esse mesmo interpretador em todos os comandos — misturar com o Python
do sistema é a causa mais comum de erro (`ModuleNotFoundError`).

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\pip install -r requirements.txt
```

bash/zsh:
```bash
.venv/bin/pip install -r requirements.txt
```

A partir daqui, todo comando deste guia é `python engine/scripts/...` — na
prática, use `.venv\Scripts\python.exe engine/scripts/...` (Windows) ou
`.venv/bin/python engine/scripts/...` (bash), para garantir que é o
interpretador certo.

### 2. Credencial de imagem (opcional, só se quiser gerar imagens)

Se o seu livro tiver `features.images.enabled: true` (o padrão), a geração de
imagem via API precisa de uma chave. Copie o modelo e preencha:

```bash
cp .env.example .env
```

Edite `.env` e defina `OPENAI_API_KEY=sua-chave-aqui`. **Nunca** cole a chave
em outro arquivo do repositório — `.env` está no `.gitignore` por esse
motivo exato.

Sem credencial, o motor não trava: ele emite `CAPABILITY_BLOCKER` na etapa de
imagem e segue com o resto (texto, KDP). Capa e Stories têm um caminho sem
custo de API — veja a seção de imagens mais abaixo.

### 3. Uma ferramenta de coding agent

A composição do runtime (passos 1-5 abaixo) é Python puro e não usa nenhuma
LLM. A **execução** do livro em si — escrever capítulos, revisar, gerar
imagem — acontece dentro de uma sessão de coding agent (Claude Code é o
hospedeiro validado neste repositório) que abre o runtime gerado e segue as
instruções nele. É o passo 7 deste guia.

---

## Passo 1 — Escreva o roteiro: crie o pacote do livro

**É aqui que você informa a história.** O pacote de livro em `books/<slug>/`
é o único lugar onde você escreve criativamente antes da execução — tudo o
que vem depois é o motor interpretando esses arquivos.

### 1.1 Gere o esqueleto

```bash
python engine/scripts/livingbook.py new-book --slug <slug> --title "Título do Livro" --chapters 24
```

Isso cria `books/<slug>/` com todos os arquivos abaixo já no formato certo,
preenchidos com `TO_DEFINE` onde você precisa escrever. Ajuste `--chapters`
para o tamanho real do seu livro (o piloto deste repositório usa 4; os
livros de catálogo usam 24).

### 1.2 Preencha cada arquivo — o que escrever em cada um

| Arquivo | O que é | O que escrever |
|---|---|---|
| `CREATIVE_BRIEF.md` | O pitch | Gênero, premissa, tom, extensão em palavras, uma ou duas frases de logline. É o primeiro arquivo que a execução lê. |
| `BOOK_CONSTITUTION.md` | As leis mais profundas da obra | Regras que nenhum capítulo pode violar: o que o livro é e não é, disciplina de tom, limites éticos específicos da história. |
| `chapter_architecture.yaml` | **O roteiro, capítulo a capítulo** | Para cada capítulo: `number`, `title`, `movement` (em que ato/parte ele está) e `function` (o que esse capítulo precisa realizar na trama, em uma frase). Isto é o esqueleto que todo o resto do motor deriva. |
| `immutable_rules.yaml` | Regras bloqueantes | Fatos e restrições que, se violados, reprovam a obra inteira (ex.: "nenhuma erotização de personagem infantil", "a causa da doença nunca é revelada"). |
| `protected_scenes.yaml` | Cenas que não podem ser diluídas | Momentos-chave da trama com uma descrição do que precisa ser preservado, e opcionalmente um auditor específico. |
| `quality_profile.yaml` | Alvos numéricos de qualidade | Pontuações mínimas (coerência, força de cena, subtexto...) e máximas de risco (sentimentalismo, clichê...), de 0 a 10. |
| `capability_requirements.yaml` | O que a execução vai precisar | Geração de imagem, DOCX, pesquisa de KDP atual, etc. — o motor confere isso automaticamente no bootstrap. |
| `seeds/WORLD_RULES_SEED.md` | Regras de mundo, cruas | Physics/sociedade/tecnologia da história, antes de virarem a bíblia formal. |
| `visual_profile.md` | Direção de arte | Paleta, referências visuais, o que evitar nas imagens de capítulo. |
| `sound_profile.md` | Direção sonora | Só relevante se `features.living_sound.enabled: true`. |

Um exemplo real e enxuto de `CREATIVE_BRIEF.md`, do livro `o_jardim_dos_doze`
deste repositório:

```markdown
# Creative Brief — O Jardim dos Doze

Romance adulto distópico de 60.000 a 90.000 palavras, em português do Brasil...
Em uma sociedade onde todos conservam aparência de doze anos, a arquivista
Nina descobre que o amadurecimento não desapareceu: foi bloqueado pelo
Estado...
```

E uma linha real de `chapter_architecture.yaml` do mesmo livro:

```yaml
- {number: 1, title: A Praça dos Balões Murchos, movement: Ato I — A Cerca,
   function: Nina presencia falha em transmissão pública e recebe ordem
   para eliminar a imagem proibida de um adulto.}
```

### 1.3 Alternativa: copiar um pacote existente como modelo

Se preferir começar de um exemplo real em vez do esqueleto vazio, copie
`books/o_jardim_dos_doze/` ou `books/a_morte_ainda_nao_nasceu/` para
`books/<slug>/` e reescreva o conteúdo — a estrutura de arquivos é idêntica.

---

## Passo 2 — Escolha o perfil de execução (a "torneira")

Em `books/<slug>/BOOK_SPEC.yaml`, o campo `spec.execution_profile` controla
velocidade × qualidade:

| Perfil | Quando usar | O que muda |
|---|---|---|
| `DRAFT` | Testar se a história funciona antes de produzir de verdade | Sem imagens, sem som, sem tradução, sem calibração de voz, painéis de revisão menores. ~46% menos chamadas de agente. |
| `STANDARD` | Uso corrente (padrão para livros novos) | Painéis de revisão reduzidos com rotação, revisões de integração consolidadas. |
| `PREMIUM` | Lançamento comercial definitivo | Tudo ligado — o comportamento histórico do motor. |

```yaml
spec:
  execution_profile: STANDARD   # DRAFT | STANDARD | PREMIUM
```

Se você omitir o campo, o motor usa `PREMIUM`. Pode trocar de perfil e
recompor (passo 4) a qualquer momento antes de começar a execução — depois
que o runtime existe, o perfil já está "congelado" no grafo gerado.

---

## Passo 3 — Valide o pacote

```bash
python engine/scripts/livingbook.py validate-book --book books/<slug>
```

Confere que os arquivos existem, que a contagem de capítulos bate em todos
os lugares, que as *waves* de escrita cobrem todos os capítulos em ordem, e
que todo agente citado em `agent_packs` existe de fato. Corrija os erros
listados antes de seguir — nada disso depende de LLM, é checagem estrutural
instantânea.

---

## Passo 4 — Componha o runtime

```bash
python engine/scripts/livingbook.py compose --book books/<slug>
```

Isso gera `runtime/<slug>/` — a fusão executável de `engine/` +
`books/<slug>/`. O runtime é descartável: pode apagar a pasta e rodar
`compose` de novo a qualquer momento antes de iniciar a execução, para
recomeçar do zero com o pacote atualizado.

Saída esperada:
```
COMPOSED runtime/<slug> | tasks: 119 | gates: 15 | agents: 66
```

(Os números variam com a contagem de capítulos e as *features* ligadas.)

---

## Passo 5 — Rode o smoke test

```bash
python engine/scripts/livingbook.py smoke-test --runtime runtime/<slug>
```

Confirma que o runtime está íntegro e que a primeira tarefa pronta é
`T000_INITIALIZE_RUNTIME`. Se isso passar, o runtime está pronto para ser
aberto por um coding agent.

---

## Passo 6 — Abra o runtime e peça a execução

Abra a pasta `runtime/<slug>/` no Claude Code (ou outra ferramenta de coding
agent compatível). O runtime já contém o roteiro de execução — você não
precisa reexplicar o livro, só pedir que ele comece.

**Como pedir**, de forma simples e direta:

> Leia `AGENTS.md` e `IMPLEMENT.md` deste runtime e comece a executar o
> `TASK_GRAPH.yaml` a partir das tarefas `READY`. Antes de qualquer tarefa,
> rode `scripts/run_deterministic.py --runtime . --loop` para resolver o que
> for mecânico sem gastar chamada de agente. Ao spawnar um subagente, use o
> modelo do `model_tier` declarado na tarefa (S → Opus, M → Sonnet, XS →
> Haiku). Pare nos gates que exigirem aprovação humana e me diga o que
> avaliar.

O que a sessão faz sozinha a partir daí (modo autônomo,
`continue_without_user_confirmation: true`):

1. Lê `TASK_GRAPH.yaml`, `project_state/PROJECT_STATUS.yaml` e
   `book/BOOK_SPEC.yaml`.
2. Roda `scripts/run_deterministic.py` a cada gate aberto, resolvendo sem
   custo de LLM tudo que tem `tool` associado no grafo (digest de canon,
   DOCX, capa/Stories).
3. Para o resto, spawna os agentes certos — cada tarefa do grafo já carrega
   `model_tier` (S/M/XS) e, quando spawna vários, `spawn.model_tiers` por
   subagente.
4. Marca cada tarefa concluída com
   `scripts/runtime_taskgraph.py mark <task_id> APPROVED` e registra o custo
   real em `logs/COST_LEDGER.md`.
5. Para nos gates com `requires_human_approval: true` (ver Passo 8) e nos
   `CAPABILITY_BLOCKER` (ex.: falta de credencial de imagem).

---

## Passo 7 — Acompanhe o progresso

A qualquer momento, mesmo com a sessão rodando:

```bash
# quais tarefas estão liberadas agora
python runtime/<slug>/scripts/runtime_taskgraph.py ready

# quanto já foi gasto, por fase, agente e tier
python runtime/<slug>/scripts/cost_report.py --runtime runtime/<slug>
```

`project_state/PROJECT_STATUS.yaml` é a fonte de verdade do estado — cada
tarefa e cada gate aparecem lá com seu estado atual
(`PENDING`/`READY`/`APPROVED`/`AWAITING_HUMAN_APPROVAL`/...).

---

## Passo 8 — Os checkpoints humanos

Dependendo do perfil escolhido no Passo 2, alguns gates só avançam com sua
aprovação explícita — mesmo que todas as tarefas dentro deles já estejam
`APPROVED`:

| Perfil | Onde o motor para para você avaliar |
|---|---|
| `DRAFT` | Nunca — pensado para iteração rápida sem fricção |
| `STANDARD` | Canon (a arquitetura da obra), Voz (o estilo calibrado), Manuscrito completo |
| `PREMIUM` | Os três acima + a prova final de KDP |

Quando um desses gates travar, a sessão vai te dizer o que precisa ser
avaliado. Depois de ler (o canon em `canon/CANON_REGISTRY.yaml`, o
manuscrito em `manuscript/`, o que for o caso), aprove criando o arquivo:

```bash
mkdir -p runtime/<slug>/project_state/APPROVALS
echo "Aprovado — <seu nome>, <data>" > runtime/<slug>/project_state/APPROVALS/GATE_CANON.md
```

**O motor nunca cria esse arquivo sozinho.** Essa é a única parte do
pipeline que não é automatizável por desenho — só você sabe se é o livro que
você quer.

---

## Passo 9 — Onde estão os resultados

Ao final da execução completa, dentro de `runtime/<slug>/`:

| O quê | Onde |
|---|---|
| Manuscrito final | `manuscript/final/MANUSCRIPT_FINAL_PTBR.md` (e `.txt`) |
| DOCX para a KDP | `outputs/BOOK_KDP_FINAL.docx` |
| Capa (1600×2560, 300 DPI) | `media/outputs/cover/BOOK_COVER_KDP.jpg` |
| 5 Instagram Stories (1080×1920) | `media/outputs/instagram_stories/story_01.jpg` … `story_05.jpg` |
| Imagens de capítulo aprovadas | `images/approved/chapter_NN.jpg` |
| Manifesto de entrega | `outputs/DELIVERY_MANIFEST.md` |
| Sentinela de conclusão | `project_state/FINAL_DELIVERY_APPROVED` |

Antes de subir para a Amazon KDP, o DOCX ainda precisa passar pelo Print
Previewer da própria KDP e por uma prova física — isso nenhuma ferramenta
local substitui, e o motor não finge que substitui.

---

## Sobre imagens: dois caminhos, dependendo do que você tem

**Com créditos de API disponíveis**: `generate_image.py` gera as imagens de
capítulo, com `--reference` para ancorar a identidade facial numa imagem já
aprovada (evita o rosto "derivar" entre capítulos) e `--edit` para correção
pontual sem regerar do zero.

**Sem créditos, ou economizando**: `build_cover_and_stories.py
--no-base-image` compõe capa e Stories só com tipografia — sem nenhuma
chamada de API — e ainda satisfaz o `GATE_MEDIA_ASSETS`. As imagens internas
de capítulo, essas não têm equivalente sem geração real; ficam como
`CAPABILITY_BLOCKER` até haver crédito.

---

## Exemplo completo, do zero ao runtime

Usando o pacote-piloto já incluído neste repositório
(`books/motor-de-livros-vivos/`, 4 capítulos):

```bash
# 1. ambiente (uma vez só)
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt        # ou .venv/bin/pip no bash

# 2. validar o pacote existente
.venv/Scripts/python.exe engine/scripts/livingbook.py validate-book --book books/motor-de-livros-vivos

# 3. compor
.venv/Scripts/python.exe engine/scripts/livingbook.py compose --book books/motor-de-livros-vivos

# 4. smoke test
.venv/Scripts/python.exe engine/scripts/livingbook.py smoke-test --runtime runtime/motor-de-livros-vivos

# 5. abrir runtime/motor-de-livros-vivos/ no Claude Code e pedir a execução (Passo 6)
```

---

## Referência rápida de comandos

```bash
# Ciclo de vida do pacote
python engine/scripts/livingbook.py new-book --slug <slug> --title "..." --chapters N
python engine/scripts/livingbook.py validate-engine
python engine/scripts/livingbook.py validate-book --book books/<slug>
python engine/scripts/livingbook.py compose --book books/<slug>
python engine/scripts/livingbook.py smoke-test --runtime runtime/<slug>
python engine/scripts/livingbook.py ready --runtime runtime/<slug>

# Dentro do runtime, durante a execução
python runtime/<slug>/scripts/runtime_taskgraph.py ready
python runtime/<slug>/scripts/runtime_taskgraph.py mark <task_id> <ESTADO>
python runtime/<slug>/scripts/runtime_taskgraph.py validate-gate <GATE_ID>
python runtime/<slug>/scripts/run_deterministic.py --runtime runtime/<slug> --loop
python runtime/<slug>/scripts/cost_report.py --runtime runtime/<slug>
python runtime/<slug>/scripts/validate_media_assets.py --runtime runtime/<slug>
```

---

## Perguntas frequentes

**"ModuleNotFoundError" ao rodar qualquer script.**
Você está usando o Python do sistema, não o do `.venv`. Chame o
interpretador pelo caminho completo: `.venv/Scripts/python.exe` (Windows) ou
`.venv/bin/python` (bash).

**A sessão travou pedindo aprovação e eu não sei o que fazer.**
Veja o Passo 8. Leia o artefato do gate (canon, manuscrito, etc.), decida, e
crie o arquivo em `project_state/APPROVALS/<GATE_ID>.md`. Sem isso, o gate
não passa — mesmo que todas as tarefas dentro dele estejam aprovadas.

**Recebi `CAPABILITY_BLOCKER` de geração de imagem.**
Confira `.env` (`OPENAI_API_KEY` definida?) e se a conta tem crédito. Se for
só para destravar a entrega sem gastar em imagem, use o caminho
`--no-base-image` descrito acima para capa e Stories; as imagens de
capítulo continuam bloqueadas até haver crédito real.

**Quero recomeçar do zero.**
Apague `runtime/<slug>/` e rode `compose` de novo — ele é inteiramente
recriável a partir de `books/<slug>/`. Nunca edite o runtime esperando que
a mudança "grude"; edite o pacote em `books/<slug>/` e recomponha.

**Onde vejo quanto o livro está custando?**
`python runtime/<slug>/scripts/cost_report.py --runtime runtime/<slug>` —
total por fase, por agente e por tier de modelo, direto de
`logs/COST_LEDGER.md`.

---

## Para ir mais fundo

- `docs/ARCHITECTURE.md` — as três camadas do motor.
- `docs/BOOK_PACKAGE_MODEL.md` — o modelo de pacote de livro em detalhe.
- `engine/IMPLEMENT.md` — o runbook que a sessão de execução de fato segue.
- `discovery-books/` — análise completa do motor, diagnóstico de custo e o
  histórico das melhorias implementadas neste repositório.
