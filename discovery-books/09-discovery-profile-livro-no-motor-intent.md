# Discovery — Viabilidade de um Profile "Livro" no Motor de Intenção

> **Sobre o escopo deste documento.** Ele vive neste repositório
> (`pedroarte-labs-living-book-codex-all-features`) por continuidade — é aqui
> que a série `discovery-books/` já existe — mas analisa principalmente
> **dois repositórios irmãos**, fora deste projeto:
> `pedroarte-labs-intention-discovery-engine` (o "motor intent") e
> `pedroarte-labs-motor-mestre-do-tcc` (o motor que hoje produz o TCC). Não
> alterei uma linha de código de nenhum dos dois — li o código-fonte real
> (entidades, políticas, agentes, prompts, schemas, testes), não apenas
> descrições. Onde a leitura foi parcial, digo isso explicitamente.

---

## 1. O achado que reformula a pergunta

Você pediu para isolar e proteger "qualquer ponto que tenha risco de mudar o
que já está funcionando no TCC". Essa frase pressupõe uma integração viva
entre o motor de intenção e o motor de TCC. **Ela não existe hoje.**

O próprio README do motor intent diz isso sem ambiguidade:

> *"Este repositório **não** integra com o TCC Engine — acoplar dois
> repositórios antes de qualquer contrato ter estabilizado seria exatamente a
> construção prematura de plataforma que o briefing veta."*

E confirmei do outro lado: `pedroarte-labs-motor-mestre-do-tcc` recebe entrada
hoje por um arquivo `input.md` escrito à mão (veja `examples/*.md` no
repositório) — não pelo schema JSON que o motor intent publica. O único ponto
de contato entre os dois é `tests/contract/test_experimental_preflight.py`,
com um DTO chamado literalmente `TccIntentSpecExperimental`,
`schema_version: "0.x"`, e uma classe `ExperimentalIntentRejected`. É um
*preflight* de compatibilidade, não uma integração em produção.

Um censo independente do ecossistema já existente
(`pedroarte-labs-discovery/00-repository-census.md`, feito via metadados
reais do GitHub, não por mim) corrobora isso: **nenhum repositório da conta
`pedroartelabs` está classificado como `PRODUCTION_LIKE`.** Os dois motores
em questão estão marcados `ACTIVE_EXPERIMENT`.

### Por que isso importa para a sua pergunta

"Proteger o que já funciona" deixa de ser uma frase só, e vira duas perguntas
com respostas muito diferentes:

| Risco | Existe hoje? |
|---|---|
| Adicionar um domínio "livro" quebrar a **produção do TCC em si** (`motor-mestre-do-tcc`) | **Nenhum.** Os repositórios não estão conectados em runtime. Nada no `motor-mestre-do-tcc` muda se o motor intent ganhar um segundo domínio. |
| Adicionar um domínio "livro" quebrar o **comportamento de descoberta de intenção para TCC**, dentro do próprio motor intent | **Real**, se a mudança tocar código hoje compartilhado por TCC. É esse o risco que este documento mapeia. |

## 2. Existe um precedente formal, e ele já respondeu parte da sua pergunta

`docs/adr/ADR-003-domain-specific-mvp.md`, no próprio motor intent, é uma
decisão de arquitetura registrada exatamente sobre isto:

> *"O conceito — descobrir intenção e transformá-la em especificação —
> generaliza para livros, planos de governo, sites, vídeos, artigos. A
> tentação de já construir a plataforma genérica é forte e quase sempre
> errada [...] Decisão: implementar **exclusivamente TCC**."*
>
> Roadmap explícito: *"Segundo domínio — **só** depois que o primeiro estiver
> em produção."*

Isso não é uma opinião desatualizada — é uma regra de governança que a equipe
escreveu, com o motivo documentado (abstração desenhada contra domínios
imaginários costuma errar quando o segundo domínio real aparece). Qualquer
recomendação minha precisa responder a essa regra, não ignorá-la. É o que
faço na seção 5.

## 3. Mapa de acoplamento real — o que é genérico e o que é TCC-específico

Li o código-fonte para responder com precisão, não por inferência do README.

### 3.1 Genérico hoje, zero risco de tocar

| Componente | Onde vive | Por que é seguro |
|---|---|---|
| Máquina de estados da conversa | `domain/value_objects/conversation_state.py` | Transições são dados (tabela), sem menção a TCC. |
| Algoritmo de fusão de fatos (`ADDED`/`REDUNDANT`/`UPDATED`/`CONFLICT`/`IGNORED`) | `domain/entities/tcc_intent.py`, método `offer()` | Opera só sobre `dict[Campo, Fato]`. Nada no algoritmo depende do tipo do campo — confirmei lendo a implementação linha a linha. |
| As quatro portas (`LLMPort`, `ConversationRepositoryPort`, `EventPublisherPort`, `ClockPort`) | `application/ports/` | Não conhecem TCC nem livro. |
| Formato de `FieldRequirement` (a metadata: importância, grupo, rótulo, condição) | `domain/policies/field_catalog.py` | A *forma* é genérica; só o *conteúdo* (`FIELD_CATALOG`, a tupla) é TCC. |
| Guardas de injeção e vazamento de prompt | `domain/policies/scope_policy.py` | Regras de segurança em nível de linguagem, não de domínio. |
| `Ambiguity`, `InformationGap`, `Constraint` | `domain/entities/` | Nenhum menciona TCC. |

### 3.2 Acoplado, mas de risco baixo e aditivo

| Componente | O que precisaria mudar | Risco ao comportamento de TCC |
|---|---|---|
| `PRODUCTION_MARKERS` (`scope_policy.py`) | Adicionar frases como "escreva meu livro", "escreva o romance", "gere os capítulos" | **Baixo.** É uma tupla; adicionar itens não remove nem reordena os existentes. Testado por `tests/unit` do próprio módulo. |
| `TCCIntentSpecification` + schema + `tcc_engine_mapper.py` | Nada muda — um domínio novo publica seu **próprio** schema e mapper, em arquivos novos | **Zero.** Contratos de saída são por domínio; não há um único ponto de saída compartilhado. |

### 3.3 O gargalo real — um ponto único e nomeável

```python
# domain/entities/conversation_session.py
intent: TCCIntent = field(default_factory=TCCIntent)
ask_counts: dict[TCCField, int] = field(default_factory=dict)
```

`ConversationSession` — o agregado raiz, o que toda a suíte de testes
(`unit`, `integration`, `contract`, `architecture`, `acceptance`) exercita —
está **estaticamente tipado para carregar um `TCCIntent`**. Não é um detalhe
menor: é o único lugar onde o "genérico" e o "específico" se cruzam na
mesma classe. Qualquer generalização de verdade (permitir que a mesma sessão
carregue um `BookIntent` em vez de um `TCCIntent`) passa por aqui — e é
exatamente aqui que uma mudança mal feita quebraria TCC de verdade, porque é
o ponto mais coberto por teste e mais central do sistema.

Dois componentes menores também estão hoje hardcoded para TCC, mas de forma
mais fácil de isolar:

- **`message_templates.py`** — `ready_message()`, `refusal_note()` e
  `blocked_message()` têm a palavra "TCC" escrita nas strings de fallback.
- **`prompts/system/intention_discovery.v1.md`** — o system prompt descreve
  explicitamente "uma pessoa que precisa produzir um TCC" e lista, como
  não-objetivos, coisas específicas de TCC (não gerar bibliografia, não
  formatar ABNT).

## 4. Três caminhos de arquitetura

### Caminho A — Segunda instância isolada (recomendado para agora)

Uma **cópia paramétrica** do motor intent — mesmo núcleo genérico (portas,
máquina de estados, algoritmo de fusão de fatos, guardas de segurança), mas
com catálogo de campos, templates, prompt de sistema e schema de saída
**próprios de livro**, rodando como deploy/processo separado do motor TCC.

- **Risco ao TCC: zero.** Nenhuma linha do repositório de TCC muda. Nenhuma
  linha do *caminho de execução* de TCC dentro do motor intent muda — é uma
  cópia, não uma edição.
- **Custo:** duplicação do que já é específico de domínio hoje (catálogo,
  templates, prompt, schema, mapper) — não do núcleo genérico.
- Isto é, na prática, o próprio ADR-003 aplicado uma segunda vez: em vez de
  abstrair agora, **duplicar agora e abstrair quando os dois domínios reais
  já existirem** — "make the change easy, then make the easy change", só que
  ainda não chegou a hora de fazer a mudança.

### Caminho B — Multi-domínio no mesmo processo (depois, não agora)

Generalizar `ConversationSession` para carregar um `DomainKind` e um
`Intent` genérico (Protocol ou union), com catálogo/templates/prompt
escolhidos por domínio em tempo de execução.

- É a versão "certa" a longo prazo, e a arquitetura hexagonal já não atrapalha
  nada disso — as quatro portas não mudam.
- **Risco real:** toca o agregado raiz que hoje é 100% coberto pela suíte de
  TCC. Uma regressão aqui quebra TCC de verdade, não hipoteticamente.
- Só faz sentido depois que o Caminho A tiver rodado de verdade com dois
  domínios reais — é exatamente o critério que o ADR-003 already impõe
  ("segundo domínio, só depois do primeiro em produção" generaliza para "a
  generalização, só depois de dois casos reais").

### Caminho C — Roteador de intenção na frente dos dois motores

Uma camada fininha, **determinística** (não um julgamento de modelo — o
próprio motor intent já tem esse princípio de segurança: *"um controle do
qual o modelo pode ser convencido não é um controle"*), que olha a primeira
mensagem e decide "isto é sobre TCC ou sobre livro?", roteando para a
instância correspondente.

Na prática, o Caminho C é o Caminho A com uma porta de entrada única. Vale
propor os dois juntos: A resolve o isolamento; C resolve a experiência do
usuário não precisar saber que existem duas instâncias.

## 5. Recomendação

**Caminho A + C.** Uma nova instância do motor intent, especializada em
livro, publicada como um novo domínio isolado — sem tocar em nenhuma linha
do caminho de TCC — com um roteador leve e determinístico na frente. É a
opção de menor risco possível, e é literalmente o que a governança já
registrada em ADR-003 recomendaria se perguntada.

## 6. Superfície de trabalho concreta, se o Caminho A for aprovado

Isto responde à parte do seu pedido sobre "conversa com o usuário, recebe
briefing e informações básicas e monta a estrutura":

| Peça nova | Espelha, no motor intent hoje | Conteúdo |
|---|---|---|
| `BookField` (enum) + `BOOK_FIELD_CATALOG` | `TCCField` + `FIELD_CATALOG` | Ver tabela na seção 7 — já derivei os campos certos, porque construí manualmente esse levantamento no motor de livros vivos ao longo desta sessão. |
| `BookIntent` (entidade) | `TCCIntent` | Se copiado, é literalmente o mesmo arquivo trocando o tipo do campo — o algoritmo de fusão (seção 3.1) já é genérico. |
| `book_message_templates.py` | `message_templates.py` | Falas próprias de livro; mesma disciplina de Question Economy. |
| `prompts/system/book_discovery.v1.md` | `prompts/system/intention_discovery.v1.md` | Mesmo esqueleto de segurança (canário, tag `<dados_do_usuario>`, guarda de saída); escopo trocado para "não escrever o livro". |
| Entradas em `PRODUCTION_MARKERS` | (extensão aditiva) | "escreva meu livro", "escreva o romance", "escreva os capítulos", "gere a história completa". |
| `BookIntentSpecification` + `schemas/book-engine-input-v1.schema.json` | `TCCIntentSpecification` + schema | Contrato de saída próprio — ver seção 7. |
| `book_engine_mapper.py` | `tcc_engine_mapper.py` | **Este é o que fecha o círculo com o motor deste repositório — seção 8.** |

## 7. O catálogo de campos — já derivado, não hipotético

Este repositório passou a sessão inteira definindo exatamente o que um
pacote de livro precisa (`books/<slug>/`, documentado agora em
`docs/COMO_EXECUTAR_UM_LIVRO.md`). Traduzo isso direto para o vocabulário do
motor intent (`importance`: `IMPORTANT` / `CONDITIONAL` / `OPTIONAL`, no
mesmo sentido de `field_catalog.py`):

| Campo | Importância | Por quê |
|---|---|---|
| `genre` | IMPORTANT | Governa tudo — voz, extensão típica, expectativa do leitor. |
| `premise` | IMPORTANT | O pitch. Equivalente a `theme` no TCC. |
| `target_length_words` | IMPORTANT | Define `chapter_count` e as *waves* de escrita. |
| `language` | OPTIONAL | Inferível da conversa, como no TCC. |
| `tone` | IMPORTANT | Alimenta `BOOK_CONSTITUTION.md`. |
| `ethical_boundaries` | CONDITIONAL (ativo se o tema tocar território sensível) | Alimenta `immutable_rules.yaml` — o análogo do risco que `ANTI_MANIPULATION_GUARDIAN` audita neste motor. |
| `protagonist_sketch` | OPTIONAL | Ponto de partida para `CHARACTER_PSYCHOLOGIST`, não substitui a bíblia de personagem. |
| `execution_profile` | OPTIONAL | `DRAFT` / `STANDARD` / `PREMIUM` — a pessoa pode nem saber que essa escolha existe; o motor de livro tem um padrão sensato. |
| `images_enabled` | OPTIONAL | Se a pessoa já sabe que não quer gastar com imagem, evita perguntar depois. |
| `deadline` | OPTIONAL | Mesmo padrão do TCC. |

O que eu **não** colocaria no catálogo, mesmo sendo tentador: um
`chapter_architecture` completo (24 linhas de função de capítulo). Isso não
é extração de fato de uma conversa — é elaboração criativa. O próprio motor
intent tem a doutrina certa para isso, já expressa no TCC: *"o domínio
decide, o modelo redige — nunca inventa."* Pedir a arquitetura de capítulos
completa numa conversa de descoberta seria o motor intent começando a fazer
o trabalho do motor de livro. A fronteira certa é a mesma que já existe hoje
entre motor intent e TCC: a especificação é o esqueleto, o motor
especialista é quem elabora.

## 8. A ponte concreta para este motor — o que fecha o círculo

Este é o ponto de maior valor prático do discovery: **eu sei exatamente o
formato de entrada que este motor de livros vivos espera**, porque documentei
isso nesta mesma sessão. Um `book_engine_mapper.py` no motor intent poderia
gerar, a partir de uma `BookIntentSpecification` confirmada, o próprio
pacote `books/<slug>/` pronto para `compose`:

| `BookIntentSpecification` | Vira, neste repositório |
|---|---|
| `genre` + `premise` + `tone` | `books/<slug>/CREATIVE_BRIEF.md` |
| `ethical_boundaries` | `books/<slug>/immutable_rules.yaml` (rascunho — ainda exige revisão humana, como já é hoje) |
| `target_length_words` → capítulos estimados | `books/<slug>/BOOK_SPEC.yaml: metadata.chapter_count` |
| `execution_profile` | `books/<slug>/BOOK_SPEC.yaml: spec.execution_profile` |
| `images_enabled` | `books/<slug>/BOOK_SPEC.yaml: spec.features.images.enabled` |
| `language` | `books/<slug>/BOOK_SPEC.yaml: metadata.language` |

E a partir daí, o fluxo que já existe e já está documentado assume:
`livingbook.py validate-book` → `compose` → `smoke-test` → abrir no Claude
Code (`docs/COMO_EXECUTAR_UM_LIVRO.md`, passo 6 em diante). A conversa deixa
de terminar num JSON solto e passa a terminar num comando `compose` pronto
para rodar.

**Limite honesto:** isso ainda deixa `chapter_architecture.yaml` (o roteiro
capítulo a capítulo) para ser elaborado — corretamente — por
`NARRATIVE_ARCHITECT`/`SCENE_ARCHITECT` já dentro do motor de livros, a
partir do `CREATIVE_BRIEF.md` gerado. Não é uma lacuna do desenho; é a
fronteira de responsabilidade funcionando como deveria.

## 9. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Regressão no comportamento de TCC | Caminho A: zero código de TCC é tocado, então não há regressão possível por construção. |
| Conversa de livro confundida com TCC (ou vice-versa) | Scope Guardian determinístico no roteador (Caminho C) — mesma filosofia de "regra, não julgamento do modelo" já usada para injeção. |
| Motor inventar estrutura de livro em vez de coletar fato | A doutrina FACT/INFERENCE/ASSUMPTION já existe e é reaproveitável sem mudança — só o catálogo de campos é novo. |
| Saída do mapper não bater com o que o motor de livros espera | Testes de contrato, no mesmo padrão de `tests/contract/test_specification_schema.py` do motor intent — validar o YAML gerado com `livingbook.py validate-book` antes de aceitar o mapper como correto. |
| Dívida técnica de duplicação (Caminho A) nunca ser resolvida | Nomear como dívida aceita explicitamente, com o próprio ADR-003 como precedente de que isso é uma escolha deliberada, não descuido — e registrar como um ADR-009 no motor intent, se este caminho for adiante. |

## 10. O que eu não fiz, e por quê

Não escrevi nenhum código nos dois repositórios irmãos, não criei branch,
não abri PR. É uma decisão de arquitetura de outro projeto — cabe a você
aprová-la antes. Também não rodei a suíte de testes desses repositórios:
não alterei nada neles, então não havia o que validar além da leitura.

Se você aprovar o Caminho A, o próximo passo natural é eu voltar a este
discovery como um plano de implementação — no mesmo formato que usamos aqui
neste repositório (ondas, cada uma validada antes de avançar) — mas dentro
do repositório `pedroarte-labs-intention-discovery-engine`, respeitando a
suíte de testes de arquitetura que já existe lá.
