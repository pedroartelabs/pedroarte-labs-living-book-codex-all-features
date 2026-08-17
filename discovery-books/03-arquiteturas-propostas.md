# Arquiteturas Propostas — "Living Book Engine v2"

> Objetivo: a partir do que a Parte 1 revelou (um bom modelo declarativo
> engine+book, mas executado como *role-play* dentro de uma única sessão de
> CLI, sem orquestrador real, sem roteamento de modelo, sem retrieval e sem
> QA determinístico onde daria) e do que a Parte 2 diagnosticou (custo e
> tempo dominados por releitura cumulativa, comitês duplicados e gates 100%
> seriais), propor como um motor de livros vivos seria desenhado hoje por um
> time de engenharia de produto de IA, olhando para como pipelines de
> conteúdo longo em produção (agentes de código, pipelines de vídeo/áudio
> gerativo, ferramentas de escrita assistida) resolvem os mesmos problemas:
> orquestração real, memória por *retrieval*, custo determinístico onde
> possível, e observabilidade desde o dia um.

---

## 0. O que preservar do design atual

Antes de propor mudanças, vale nomear o que já está certo e não deveria ser
jogado fora:

- A separação **motor / DNA da obra / runtime gerado** é sólida — mantenha.
- A doutrina de **propriedade exclusiva** (canon só muda por um agente, prosa
  final só por um agente) é uma boa transposição de processo editorial real —
  mantenha, mas torne-a **tecnicamente imposta**, não só textual.
- `immutable_rules.yaml` / `protected_scenes.yaml` / `quality_profile.yaml`
  como contratos declarativos por livro são um ótimo padrão de produto —
  mantenha e reforce.
- O padrão de validação 100% determinística usado em
  `validate_media_assets.py` (Pillow, sem LLM) é o modelo certo — **generalize-o**
  em vez de mantê-lo como exceção isolada.

A proposta abaixo não é "jogue tudo fora e comece de novo" — é "troque o
motor de execução por baixo do mesmo modelo de dados, e feche as lacunas de
engenharia de confiabilidade que hoje dependem só de disciplina textual".

## 1. Pilar 1 — Um orquestrador de verdade, não uma LLM fingindo ser 68 agentes

**Problema hoje**: uma única sessão de CLI agentica lê `TASK_GRAPH.yaml`,
decide o que é `READY`, "spawna" subagentes dentro do próprio ambiente da
CLI, e manualmente roda `mark <task> <state>` para atualizar o YAML. Isso é
frágil (depende de disciplina, não de garantia), não é paralelizável de
verdade além do que a CLI hospedeira permitir (`max_threads=8`,
`max_depth=1`), e — crucialmente — não permite seleção de modelo por tarefa
porque o modelo é uma propriedade da sessão, não do grafo.

**Proposta**: um executor real (pode ser tão simples quanto um *runner*
Python `asyncio` que lê o mesmo `TASK_GRAPH.yaml` e chama a API do provedor
de LLM diretamente por tarefa; ou um motor de workflow estabelecido — Temporal,
Prefect, ou um grafo estilo LangGraph/CrewAI) que:

- chama o modelo certo por tarefa (`model=` explícito no nó, implementando o
  tiering da Parte 2 **em código**, não por convenção);
- executa passos independentes como chamadas de API **realmente concorrentes**,
  não "espere o subagente da CLI terminar";
- persiste estado em um armazenamento real (SQLite/Postgres — uma linha por
  tarefa, com histórico, não um único YAML sobrescrito);
- ganha *retry*, *backoff* e idempotência de graça (nativos de qualquer motor
  de workflow maduro), em vez do laço `STOP.FIX.REVALIDATE.CONTINUE` sem
  limite declarado de hoje;
- registra tokens/custo/tempo por chamada automaticamente (resolve o ponto
  cego de telemetria da Parte 2, seção 4).

O `TASK_GRAPH.yaml` gerado por `build_standard_graph()` continua sendo o
formato de intercâmbio — o gerador de grafo em `livingbook.py` não precisa
mudar. O que muda é **quem executa o grafo**: hoje é uma LLM lendo Markdown e
confiando na própria memória; na v2, é um processo determinístico que só
delega à LLM exatamente o que exige julgamento.

## 2. Pilar 2 — Canon por *retrieval*, não por releitura de arquivo inteiro

**Problema hoje**: `STORY_BIBLE.md`, `CHARACTER_BIBLE.md`, `WORLD_BIBLE.md`,
`TIMELINE.md`, `CANON_REGISTRY.yaml` crescem com o livro e são relidos
inteiros por dezenas de agentes em cada estágio — custo O(capítulos²).

**Proposta**: manter os documentos longos como *fonte de verdade legível por
humano* (bom para o editor revisar), mas indexar seus fatos atômicos
(personagem, evento de linha do tempo, regra de mundo, restrição
imutável) em um armazenamento consultável — pode ser tão simples quanto um
SQLite com uma tabela de fatos taggeados por capítulo/personagem/tema, ou um
índice vetorial se a escala justificar. Cada agente recebe, por padrão, só os
fatos relevantes à sua tarefa atual (personagens na cena, regras de mundo que
tocam o capítulo, eventos anteriores que a cena referencia) — não o arquivo
inteiro. Isso é o padrão já consolidado em ferramentas de escrita longa
assistida por IA em produção: memória como *retrieval*, não memória como
"jogue tudo no contexto e espere o modelo filtrar".

`CANON_GUARDIAN` continua sendo o único a escrever fatos novos — a mudança é
só na forma de leitura pelos outros agentes.

## 3. Pilar 3 — QA determinística onde o critério é objetivo; LLM só onde é julgamento

**Problema hoje**: só a validação de mídia (`validate_media_assets.py`) é
determinística. Gramática, clichê, redundância, tipografia, contagem de
palavras, consistência de ponto de vista — tudo isso passa por um agente LLM
"lendo e opinando", multiplicando custo em checagens que são, por natureza,
objetivas.

**Proposta**: expandir a família de `custom_validators` (mecanismo que já
existe em `ENGINE_GRAPH.yaml` / `BOOK_GRAPH.yaml`, hoje usado só para imagem)
com checadores de texto:

- contagem de palavras por capítulo/livro (regra de `immutable_rules.yaml`
  já existe, ex. "mínimo 60000 palavras" — hoje isso depende de um agente
  contar; deveria ser uma linha de Python);
- lista de frases-clichê banidas + detecção de repetição de *n-gramas* /
  similaridade de embedding entre parágrafos (substitui boa parte do
  trabalho de `CLICHE_REVIEWER`/`CLICHE_HUNTER`/`REDUNDANCY_REVIEWER`);
- corretor gramatical determinístico (motor tipo LanguageTool para PT-BR) como
  primeira passada antes de `PTBR_GRAMMAR_EDITOR` — o agente LLM só entra
  para os casos ambíguos que o corretor sinalizar, não para reler tudo;
- checagem de continuidade factual como *diff* estruturado contra o índice de
  canon do Pilar 2 (nomes, datas, objetos) em vez de um agente relendo prosa
  para "sentir" inconsistência;
- geração de DOCX/KDP via template determinístico em vez de um agente
  `KDP_FORMATTER` "produzindo" o arquivo. `python-docx` já está em
  `requirements.txt`, mas nenhum script do repositório o importa — a biblioteca
  está instalada e o código que a usaria não existe. Essa lacuna é de
  capacidade, não só de custo.

O LLM continua insubstituível para: prosa em si, julgamento tonal/temático,
qualidade de diálogo, decisões editoriais de síntese — exatamente onde o
`LEAD_NOVELIST`, `EXECUTIVE_EDITOR` e os críticos literários já atuam hoje.

## 4. Pilar 4 — Pipeline incremental por capítulo, não *big-bang waves*

**Problema hoje**: capítulos avançam em lotes ("waves") com 16-17 barreiras
totalmente bloqueantes; nada da wave seguinte começa até a anterior fechar
por completo (escrita + merge + revisão + revisão + canon + aprovação).

**Proposta**: cada capítulo tem seu próprio pipeline curto e local
(esboço → rascunho → QA automática do Pilar 3 → revisão dirigida só nos
pontos que a QA sinalizou → aprovação), publicando um evento de "capítulo
pronto" de forma assíncrona. Uma passada de continuidade global roda
periodicamente (a cada N capítulos, ou sob demanda) em vez de uma única
integração monolítica de fim de livro. Isso é o mesmo salto que engenharia de
software deu de "QA manual no fim do projeto" para "CI por *pull request*" —
feedback em minutos por capítulo, não uma auditoria gigante no final que
precisa reler o livro inteiro de uma vez.

Os *gates* duros continuam existindo, mas só nos pontos de **risco real**:
aprovação de voz (uma vez), aprovação de cena protegida (quando aplicável),
congelamento do manuscrito, aprovação de mídia final — não em cada
subtransição interna de wave.

## 5. Pilar 5 — Humano no ciclo só nos pontos de maior densidade de valor

**Problema hoje**: 16-17 *gates* bloqueantes tentam simular consenso de
comitê com múltiplos agentes-críticos em cada estágio — caro e lento — em vez
de gastar esse orçamento no único lugar que reduz risco de produto de
verdade: aprovação humana.

**Proposta**: reduzir a 3-4 pontos de decisão humana real e assíncrona
(aprovar sinopse/arquitetura de capítulos, aprovar a amostra de calibração de
voz, ler o manuscrito completo em um *beta read*, aprovar capa/KDP final) —
expostos por uma interface simples (mesmo que só um arquivo `APPROVAL.md`
esperando edição, ou um webhook). É mais barato e mais confiável pagar um
punhado de decisões humanas de alto valor do que pagar 6 agentes-crítico para
simular consenso em cada uma das 4 waves.

## 6. Pilar 6 — Ferramentas nativas para imagem e layout, não personas de prompt

**Problema hoje**: `IMAGE_GENERATOR` e `KDP_FORMATTER` são personas de texto
que descrevem um papel, mas não há nenhuma integração de ferramenta real no
repositório — a geração de imagem e de DOCX depende inteiramente de a CLI
hospedeira "por acaso" ter essa capacidade (daí o mecanismo de
`CAPABILITY_BLOCKER` em `capability_requirements.yaml`, que é honesto sobre
essa fragilidade, mas não a resolve).

**Proposta**: nós de ferramenta explícitos no grafo — uma chamada de API de
imagem (com *LoRA*/referência de personagem para consistência facial, em vez
de reprompt textual e um agente `IMAGE_CONTINUITY_QA` tentando "julgar" se o
rosto bateu) e um *renderer* de template real para DOCX/KDP. A checagem de
identidade facial vira um score objetivo de similaridade de *embedding*
(rosto gerado vs. referência canônica), com LLM entrando só para o veredito
estético final — não para toda a cadeia de julgamento visual.

## 7. Pilar 7 — Observabilidade de custo desde o primeiro dia

Cada chamada registra `{task_id, agent, model, tokens_in, tokens_out, cost_usd,
wall_seconds, outcome}`. Isso não é um "nice to have" — é o que torna
verificável qualquer alegação futura de "reduzimos custo em X%" (ver Parte 2,
seção 4). Sem isso, tiering, simplificação e paralelismo são apostas às
cegas.

## 8. Comparação resumida

| Dimensão | v1 (atual) | v2 (proposta) |
|---|---|---|
| Execução | LLM única, dentro de uma sessão de CLI agentica, "spawnando" subagentes por convenção | Orquestrador real (workflow engine), chamadas de API concorrentes de verdade |
| Modelo por tarefa | Nenhum — herda o modelo da sessão hospedeira | Explícito por tarefa, com tiering S/M/XS |
| Memória de canon | Arquivos Markdown inteiros, relidos por completo a cada estágio | Fatos indexados, *retrieval* seletivo por tarefa |
| QA de texto mecânico | Agente LLM lê e "opina" | *Script* determinístico primeiro; LLM só nos casos ambíguos |
| Estrutura de progresso | *Waves* grandes, 16-17 *gates* 100% bloqueantes | Pipeline incremental por capítulo, *gates* duros só em pontos de risco real |
| Decisão humana | Implícita/nenhuma (modo autônomo) | 3-4 pontos explícitos de alto valor |
| Imagem/DOCX | Persona de prompt + dependência silenciosa da ferramenta hospedeira | Nós de ferramenta explícitos (API de imagem, *renderer* de template) |
| Custo/tempo | Não medido em lugar nenhum | Registrado por chamada, desde o primeiro *run* |

## 9. Caminho de migração (não precisa ser tudo de uma vez)

A boa notícia, confirmada pela leitura do código: `build_standard_graph()` já
separa claramente **geração do grafo** (dados) de **execução do grafo**
(hoje, uma LLM lendo Markdown). Isso significa que os pilares acima podem ser
adotados incrementalmente, mantendo o mesmo formato de `TASK_GRAPH.yaml` como
contrato estável:

1. Comece pelo Pilar 7 (telemetria) — barato, não-invasivo, e necessário para
   validar tudo o mais.
2. Pilar 1 (orquestrador real) é o de maior alavancagem: uma vez que exista,
   o tiering de modelo (Parte 2) e a paralelização de verdade (Parte 2,
   seção 3.3) ficam triviais de configurar.
3. Pilar 3 (QA determinística) pode ser adotado agente por agente, em
   paralelo, sem esperar o orquestrador — é só estender o mecanismo de
   `custom_validators` que já existe.
4. Pilares 2, 4, 5 e 6 são mudanças mais profundas de fluxo de trabalho —
   fazem sentido depois que 1, 3 e 7 já estiverem entregando economia
   mensurável, para não misturar variáveis na avaliação de impacto.
