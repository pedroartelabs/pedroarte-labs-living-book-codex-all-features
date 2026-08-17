# Análise Crítica — Custo e Tempo (a dor real de usar o engine)

> Contexto: a dor relatada é "custo alto de LLM" e "dias a uma semana para
> concluir um livro". O repositório não contém nenhum log de execução real,
> nenhuma métrica de token e nenhum runtime completado (ver `01-analise-estrutural.md`,
> seção 7-8) — então esta análise não pode citar números observados de uma
> execução real. Em vez disso, ela é construída sobre **estrutura verificável**:
> a contagem exata de tarefas/gates/agentes extraída programaticamente do
> próprio gerador de grafo (`build_standard_graph`), e sobre os mecanismos de
> design que, por construção, multiplicam trabalho. É diagnóstico estrutural,
> não medição — e é exatamente por isso que a causa raiz fica visível: **o
> motor nunca foi instrumentado para medir nem para economizar.**

---

## 1. De onde vem o custo — os quatro multiplicadores estruturais

### 1.1 Nenhum roteamento de modelo — tudo roda no modelo mais caro disponível

Nenhum dos 68 `.toml` de agente, nem `ENGINE_GRAPH.yaml`, nem `BOOK_SPEC.yaml`,
nem `TASK_GRAPH.yaml` declara um campo de modelo. A seleção de modelo é uma
propriedade da **sessão da CLI hospedeira** (Codex/Claude Code), não do grafo.
Isso significa, na prática, que `FINAL_PROOFREADER` corrigindo crase e
`LEAD_NOVELIST` escrevendo o clímax do livro rodam **no mesmo modelo, ao mesmo
preço por token** — porque o sistema não tem como dizer ao host "esta tarefa é
mecânica, use algo mais barato". Isto é a causa raiz nº 1 do custo, e é
também a mais barata de corrigir (não exige reescrever a arquitetura, ver
seção 3).

### 1.2 Volume de invocações — ~409 chamadas de agente por livro de 24 capítulos

Medido diretamente (ver `01-analise-estrutural.md`, seção 8):

- 244 nós de tarefa no grafo;
- somando o *fan-out* de `spawn.agents` / `spawn.jobs` / `spawn.foreach_chapter`,
  ≈ 409 invocações reais de agente/LLM;
- os maiores multiplicadores isolados: `VISUAL_PRODUCTION` (120 tarefas = 24
  capítulos × 5 subtarefas: brief, generate, face_qa, continuity_qa, approve),
  `T503_SOUND_PROMPTS` (25 invocações, 1 por capítulo), 4 waves de escrita × 7
  fases cada = 28 tarefas só de esqueleto de wave (sem contar os subagentes de
  revisão dentro de cada uma).
- **Isto é um piso.** Não inclui: laços `REVISION_REQUIRED`, o ciclo
  `STOP→FIX→REVALIDATE→CONTINUE` sempre que um gate falha (e com 16-17 gates
  todos bloqueantes, a chance estatística de pelo menos um falhar na primeira
  tentativa é alta), nem o fato de que, numa CLI agentica real, uma única
  "invocação de agente" é ela mesma vários turnos de raciocínio/ferramenta.

### 1.3 Releitura cumulativa de contexto — custo cresce mais rápido que o livro

O design é "todo agente lê os arquivos de canon inteiros que precisar". À
medida que o livro avança, `STORY_BIBLE.md`, `CHARACTER_BIBLE.md`,
`WORLD_BIBLE.md`, `TIMELINE.md`, `CANON_REGISTRY.yaml` e o manuscrito
acumulado só crescem — e são **relidos do zero, por inteiro**, por dezenas de
agentes diferentes em pontos diferentes do pipeline (revisores de wave, painel
de críticos da integração, revisores de linha, revisor PT-BR, provador final).
Não existe nenhum mecanismo de resumo, *retrieval* seletivo ou *diff*
incremental — é releitura total, repetida, em cada uma das 4 waves + na
integração final. Isso empurra o custo de token para perto de **O(capítulos²)**
em vez de O(capítulos), porque quanto mais tarde no livro, maior o contexto
que cada revisor precisa reingerir.

### 1.4 Sobreposição de papéis de revisão — o mesmo texto lido por comitês quase-duplicados

Contando os *packs* declarados em `BOOK_SPEC.yaml` para `o_jardim_dos_doze`:

| Painel | Quando roda | Agentes |
|---|---|---|
| `wave_reviewers` | a cada uma das 4 waves | 6: continuidade de trama, personagem, regras de mundo, editor emocional, guardião de gênero, guardião anti-manipulação |
| `critic_panel` | 1x, na integração | 6: crítico literário, crítico de cinema, crítico comercial, caçador de clichê, editor de desenvolvimento, **continuidade de trama de novo** |
| `line_reviewers` | 1x, na integração | 8: diálogo, estilo, subtexto, sensorial, corporeidade, tipografia, redundância, clichê |
| + `T305_DEVELOPMENTAL_REVIEW`, `T306_LINE_REVIEW`, `T307_FINAL_LITERARY_REVISION`, `T308_PTBR_REVIEW`, `T309_FINAL_PROOF` | sequenciais, na integração | mais 5 passadas de leitura completa |

`PLOT_CONTINUITY_REVIEWER` está tanto em `wave_reviewers` quanto em
`critic_panel` — o mesmo tipo de checagem roda 5 vezes ao longo do livro (4
waves + integração). `CLICHE_REVIEWER` (em `line_reviewers`) e `CLICHE_HUNTER`
(em `critic_panel`) são, pelo nome e pela instrução (`.toml`), a mesma
verificação com dois nomes. Isso não é uma suposição vaga — é visível
diretamente na composição declarada dos *packs* em `BOOK_SPEC.yaml`. Cada
painel a mais é uma releitura completa do manuscrito por N agentes a mais.

## 2. Por que "dias a uma semana" é estruturalmente esperado, não um bug isolado

Com 16-17 *gates* **todos `blocking: true`** e nenhuma tarefa podendo pular
fila, o caminho crítico do livro é inteiramente sequencial em nível de fase:

```
BOOTSTRAP → CANON → LIVING_BOOK → CHAPTER_BRIEFS → VOICE_CALIBRATION →
WAVE_1 → WAVE_2 → WAVE_3 → WAVE_4 → INTEGRATION (16 tarefas, quase todas
sequenciais) → VISUAL_PRODUCTION (só começa após manuscrito congelado) →
SOUND → LEGAL → [TRADUÇÃO] → KDP → DELIVERY
```

Dentro de cada wave, as 7 subfases (`preflight → write → merge → review →
revision → canon_update → approval`) são **elas mesmas sequenciais e
com locks exclusivos** (`MANUSCRIPT_MERGE`, `MANUSCRIPT_FINAL_WRITE`,
`CANON_WRITE`) — mesmo quando só um subconjunto de arquivos realmente
conflitaria. Nada da wave 2 pode começar até a wave 1 fechar `GATE_WAVE_1`
por completo, incluindo toda a revisão E a atualização de canon E a
aprovação. Some a isso: `VOICE_CALIBRATION` já é serial por definição (o
capítulo 2 só começa depois que o capítulo 1 passa por escrever → revisar →
reescrever). O resultado é uma cadeia longa de ~17 barreiras de sincronização
total, cada uma exigindo que **todo** trabalho paralelo dentro dela termine
antes de qualquer coisa da próxima começar — a definição clássica de um
pipeline com baixo *throughput* mesmo quando tem paralelismo interno alto
(`max_parallel_writers: 4`, `max_parallel_critics: 8`).

Multiplique isso por: (a) o fato de tudo isso ser mediado por uma única sessão
de CLI agentica com `job_max_runtime_seconds = 1800` por subagente e
`max_depth = 1` (subagentes não podem ter subagentes — outro limitador de
paralelismo real), e (b) o fato de o ciclo `STOP.FIX.REVALIDATE.CONTINUE` não
ter nenhum limite de tentativas ou *circuit breaker* declarado em lugar
nenhum — e a soma de latência de execução + possíveis reinícios de sessão +
laços de correção facilmente chega à escala de dias.

## 3. Plano de ação — quatro frentes pedidas

### 3.1 Tiering de modelo (trocar caro por barato onde dá)

Proposta concreta e de baixo risco: adicionar um campo `model_tier` a cada
`engine/agents/*.toml` (mudança de configuração, não de arquitetura — o
formato TOML já suporta campos livres) e fazer o host CLI (ou, melhor, um
orquestrador real — ver `03-arquiteturas-propostas.md`) respeitá-lo.

| Tier | Quando usar | Agentes candidatos |
|---|---|---|
| **S — frontier** | Julgamento criativo irredutível, decisões irreversíveis, risco ético/legal | `LEAD_NOVELIST`, `NARRATIVE_ARCHITECT`, `PLOT_ENGINEER`, `WORLD_ARCHITECT`, `CANON_GUARDIAN`, `EXECUTIVE_EDITOR`, `LITERARY_CRITIC`, `PROTECTED_SCENE_AUDITOR`, `ANTI_MANIPULATION_GUARDIAN` |
| **M — intermediário** | Checagem contra uma fonte de verdade estruturada, geração assistida | `CHAPTER_WRITER` (capítulos não-líder), `PLOT_CONTINUITY_REVIEWER`, `CHARACTER_CONTINUITY_REVIEWER`, `WORLD_RULES_REVIEWER`, `DIALOGUE_DIRECTOR`, `SENSORY_AGENT`, `CHAPTER_IMAGE_DIRECTOR`, `LIVING_SOUND_PROMPT_ENGINEER`, `KDP_FORMATTER`, `TABLE_OF_CONTENTS_AGENT`, tradutores |
| **XS — barato/rápido (ou nem LLM)** | Checagem mecânica, formato, checklist | `FINAL_PROOFREADER`, `PTBR_GRAMMAR_EDITOR`, `TYPOGRAPHY_TEXT_REVIEWER`, `REDUNDANCY_REVIEWER`, `CLICHE_REVIEWER`/`CLICHE_HUNTER`, `KDP_REQUIREMENTS_RESEARCHER`, `DELIVERY_AGENT`, `MASTER_ORCHESTRATOR` (é majoritariamente roteamento/contabilidade, não criação) |

Com a distribuição real de chamadas (~409/livro) pesando mais nas fases de
maior volume (`VISUAL_PRODUCTION`, revisões de linha, revisões de wave — que
são majoritariamente Tier M/XS), um roteamento assim pode plausivelmente
cortar **50-70% do custo em tokens caros** sem tocar em nenhuma tarefa
criativa central — porque a maior parte do volume de chamadas nunca foi
criativa, foi checklist.

### 3.2 Simplificação da dinâmica dos agentes sem perder qualidade

1. **Fundir papéis duplicados**: `CLICHE_REVIEWER` + `CLICHE_HUNTER` → um
   agente único, chamado uma vez. `REDUNDANCY_REVIEWER` pode entrar na mesma
   passada (é o mesmo tipo de verificação de repetição em escalas diferentes).
2. **Remover a tripla-checagem de continuidade**: `PLOT_CONTINUITY_REVIEWER`
   não precisa rodar em toda wave **e** no painel de crítica final — mantenha
   a checagem por wave (mais barata, escopo menor) e substitua a passada final
   por uma comparação estrutural contra o `CANON_REGISTRY.yaml` /
   `PLOT_DEPENDENCY_MAP.md` já existentes, em vez de uma releitura literária
   completa.
3. **Revisão incremental, não releitura total**: cada revisor deveria
   receber só o **delta** (capítulos novos/alterados da wave atual + um
   resumo compacto do canon), não o manuscrito inteiro relido do zero a cada
   estágio. Isso ataca diretamente o crescimento O(capítulos²) da seção 1.3.
4. **Converter crítica "de vibe" em checagem determinística onde o critério é
   objetivo**: o próprio repositório já prova que isso funciona —
   `validate_media_assets.py` checa dimensão/DPI/modo de cor de imagem sem
   gastar um único token de LLM. O mesmo princípio deveria existir para
   prosa: contagem de palavras, lista de frases-clichê banidas, repetição de
   *tags* de diálogo, consistência de ponto de vista — tudo isso é checável
   por *script* (regex, contagem de n-gramas, similaridade de embedding), não
   precisa de um agente `LITERARY_STYLE_GUARDIAN` relendo tudo para achar
   repetição óbvia.
5. **Reduzir o número de gates bloqueantes**: 16-17 é excessivo. Fundir
   `T305_DEVELOPMENTAL_REVIEW` + `T306_LINE_REVIEW` + `T307_FINAL_LITERARY_REVISION`
   em uma única passada consolidada de "polimento final" com checklist,
   reduzindo 3 barreiras sequenciais a 1.
6. **Orçamento de revisores por wave**: em vez de sempre acionar os 6
   `wave_reviewers`, alternar (ex.: 3 por wave, rotacionando foco), reservando
   o painel completo só para a passada final de integração.

### 3.3 Melhoria de performance (tempo de parede)

1. **Desacoplar produção visual do congelamento total do manuscrito.** Hoje
   `VISUAL_PRODUCTION` só começa depois de `GATE_FULL_MANUSCRIPT` (16 tarefas
   de integração completas). Mas o *brief* de imagem por capítulo só depende
   da `CHARACTER_VISUAL_BIBLE` + do *brief* daquele capítulo, ambos
   disponíveis muito antes. Separe "rascunhar prompt visual" (pode começar
   logo após `GATE_CHAPTER_BRIEFS`) de "gerar pixel final" (esse sim depende
   do texto congelado) — isso tira ~120 tarefas do caminho crítico serial e
   as move para uma trilha paralela que roda **durante** as waves de escrita,
   não depois delas.
2. **Locks por arquivo/capítulo, não locks globais.** `MANUSCRIPT_MERGE` e
   `MANUSCRIPT_FINAL_WRITE` sendo exclusivos globais força a wave N+1 esperar
   a wave N terminar revisão + canon_update + aprovação inteiras, mesmo que
   os capítulos envolvidos não se toquem. Um lock por capítulo (ou por
   *movement*/ato) permite iniciar a escrita da wave seguinte assim que o
   *merge* da anterior termina, sem esperar toda a cadeia de revisão —
   *pipelining* em vez de *gating* estrito.
3. **Digest de canon em vez de releitura de bíblia inteira.** Manter, ao lado
   dos documentos longos, uma versão compacta e estruturada (JSON com fatos-
   chave: quem é quem, o que já aconteceu, o que é proibido) que a maioria
   dos agentes recebe por padrão — só agentes que literalmente escrevem canon
   (`CANON_GUARDIAN`, `NARRATIVE_ARCHITECT`) precisam da versão longa.
4. **Paralelizar a calibração de voz.** Hoje os capítulos 1 e 2 de calibração
   são estritamente sequenciais (escreve 1 → revisa → reescreve → só então
   começa 2). Escrever os dois em paralelo contra o mesmo guia de estilo e
   sincronizar apenas na etapa de "construir referência de voz" corta essa
   subfase praticamente ao meio.

### 3.4 A "torneira" de velocidade — um botão real de velocidade vs. qualidade

Proposta: um novo arquivo `execution_profile.yaml` (mesmo padrão dos arquivos
que já existem em `books/<slug>/`) com 3 perfis, consumido por
`build_standard_graph()` do mesmo jeito que hoje ela já lê
`features.images.enabled` para incluir/excluir fases inteiras — ou seja, é
uma **extensão natural de um mecanismo que já existe no código**, não uma
reescrita:

| Perfil | Calibração de voz | Revisores por wave | Painel de crítica final | Gates | Tradução/legal-global | Uso alvo |
|---|---|---|---|---|---|---|
| **DRAFT** | pulada (usa guia de estilo fixo) | 1-2 agentes | 1 passada única (`LITERARY_CRITIC` só) | maioria `blocking: false` (loga e segue) | pulados | iteração rápida com beta-leitor, custo mínimo |
| **STANDARD** | atual, mas com as fusões da seção 3.2 | 3 agentes rotativos | painel reduzido (3) | bloqueantes nos pontos críticos (ético, continuidade, entrega) | conforme feature flag | uso corrente recomendado |
| **PREMIUM** | atual completo | painel completo (6) | painel completo (6) + checkpoints humanos extras | todos bloqueantes, como hoje | completo | lançamento comercial final |

Tecnicamente isso é barato de implementar porque `build_standard_graph()` **já
é** condicional por *feature flag* — bastaria o perfil controlar: (a) o
tamanho das listas em `agent_packs` no `BOOK_SPEC.yaml`, (b) o valor
`blocking` de cada gate, e (c) se `T15xB/T15xC` (calibração) são incluídas ou
substituídas por um guia de estilo estático. Nenhuma tarefa nova precisa ser
inventada — é poda paramétrica do grafo que já existe.

## 4. O que falta para essas mudanças serem confiáveis: telemetria

Nenhuma das quatro frentes acima pode ser validada sem medir. Hoje o
repositório não tem **nenhum** mecanismo de log de tokens, custo ou tempo por
tarefa. Antes de qualquer otimização, vale adicionar ao `TaskResult` (já
existe o schema em `engine/contracts/TASK_RESULT.schema.json`, só falta um
campo) algo como `{"tokens_in": N, "tokens_out": N, "model": "...", "wall_seconds": N}`
por tarefa, persistido em `PROJECT_STATUS.yaml` ou em um `logs/COST_LEDGER.md`.
Sem isso, qualquer alegação de "economizamos X%" depois de aplicar esta
análise não pode ser comprovada — e é exatamente esse ponto cego que hoje
impede a equipe de saber, com precisão, onde o custo/tempo está realmente
concentrado.
