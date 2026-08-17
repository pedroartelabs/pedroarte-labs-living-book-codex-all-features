# Prompt de Continuação — Plano de Desenvolvimento das Melhorias

> **Isto é um prompt endereçado a mim mesmo** (ou a qualquer sessão futura do
> Claude que retome este trabalho), não só um documento de referência. Se
> você está lendo isto para continuar o trabalho depois que o contexto desta
> conversa se perdeu: leia primeiro `discovery-books/00-INDICE.md` e os
> documentos 01–07 na ordem. Este documento pressupõe que você já sabe o que
> eles dizem — ele não repete a análise, **compila as decisões que ela já
> aponta** em algo executável.
>
> **Status no momento em que isto foi escrito: plano, não execução.** Nenhum
> código foi alterado para produzir este documento. O usuário vai revisar e
> aprovar antes de qualquer onda começar — não comece a implementar só por
> ler isto numa sessão nova; confirme com o usuário qual onda está aprovada.

---

## Como cheguei a este plano (raciocínio, não só conclusão)

Reli os sete documentos anteriores procurando um padrão específico que o
usuário nomeou explicitamente: pontos que **demoraram muito e queimaram
processamento probabilístico (chamadas de LLM) para resolver algo que, na
prática, é uma checagem mecânica** — o exemplo mais forte e mais bem
documentado é o DOCX (documento 07, §3): seis dias, mais de 1.100 linhas de
script escritas do zero pelo Codex, um reinício de Windows no meio do
caminho, para produzir um artefato cuja estrutura (margens espelhadas,
cabeçalhos pares/ímpares, `PAGEREF` bloqueado) é inteiramente descritível por
regras, não por julgamento criativo.

Uma vez que esse padrão ficou claro, voltei aos documentos 01–04 com essa
lente e achei mais casos da mesma família que eu não tinha visto com a
força devida na primeira passada: revisão de clichê/redundância (três
agentes LLM diferentes fazendo, essencialmente, detecção de repetição),
checagem de continuidade (releitura de prosa inteira por LLM para achar o
que uma comparação estruturada contra `CANON_REGISTRY.yaml` acharia mais
barato), e a checagem de DPI de imagem (que hoje é feita certo via Pillow,
mas com uma regra que o documento 07 mostrou ser semanticamente incompleta).

Organizei o plano em **ondas** porque o volume é grande demais para uma
aprovação única sensata — cada onda é independentemente aprovável, entrega
valor sozinha, e a ordem entre elas segue risco crescente e dependência
real, não só "o que é mais importante". A Onda 1 vem primeiro porque é
exatamente o que o usuário apontou, tem a evidência mais forte (um caso real
medido, não uma hipótese), e não tem nenhuma dependência de nada que ainda
não existe.

---

## Onda 0 — Higiene de repositório (pré-requisito barato, quase sem risco)

Verificação pedida explicitamente no final: **`runtime/` está no
`.gitignore`**, e isso está funcionando parcialmente, com uma pendência que
vale a pena resolver antes de qualquer onda de código.

| Achado | Detalhe |
|---|---|
| `runtime/` está no `.gitignore` | Sim, adicionado numa sessão anterior. Funcionou para os runtimes criados depois: `runtime/a_morte_ainda_nao_nasceu/` (412 MB, a execução real do Codex) e `runtime/motor-de-livros-vivos/` (o piloto) **nunca foram rastreados pelo git** — o `.gitignore` os impediu corretamente. |
| Pendência real | `runtime/antes-que-as-criancas-crescam/` (o runtime órfão da primeira análise) **já estava commitado antes do `.gitignore` existir** — 126 arquivos em `HEAD`. Adicionar ao `.gitignore` não desfaz isso retroativamente. |
| Estado atual do git | Esses 126 arquivos aparecem como **staged for deletion**. |
| O que isso significa na prática | Nada commitado ainda; `.gitignore` em si nunca foi commitado — mudança de working tree, reversível. |

**Ação proposta (Onda 0, requer aprovação explícita antes de rodar `git
commit`):** aceitar a remoção staged de `runtime/antes-que-as-criancas-crescam/`
do controle de versão e commitar `.gitignore` junto. Isso é coerente com o
próprio princípio do motor (`runtime/` é gerado, recriável por `compose`,
nunca deveria ter sido commitado) e com o que o usuário reafirmou nesta
mensagem: *"runtime são apenas os outputs de cada livro"*.

Não vou rodar `git commit` sem confirmação explícita — commit é uma ação
visível/histórica, diferente de editar arquivo local.

### ✅ EXECUTADA — correções ao que estava escrito acima

Duas imprecisões desta seção, descobertas ao executar e corrigidas aqui:

1. **O diretório não foi apenas destrackeado — foi apagado do disco.** Escrevi
   "nada foi perdido"; o correto é que a *cópia de trabalho* já não existia, e
   eu supus errado que o `.gitignore` teria destrackeado sozinho (ele não faz
   isso: adicionar uma regra nunca remove do índice o que já estava rastreado).
   Alguém rodou `git rm`/apagou antes. O que permanece verdadeiro é o essencial:
   **nada é irrecuperável** — os 126 arquivos estão íntegros no histórico.
2. Resgate, se algum dia for necessário:
   `git checkout f27f3d1~1 -- runtime/antes-que-as-criancas-crescam/`

**Resultado da execução** (commit `f27f3d1`, na branch
`chore/untrack-runtime-outputs`, ainda não mesclada em `main`):

- `runtime/` rastreado no commit atual: **0 arquivos**;
- `runtime/a_morte_ainda_nao_nasceu/` (1.219 arquivos) e
  `runtime/motor-de-livros-vivos/` (160 arquivos) intactos em disco e
  invisíveis ao git;
- `.env` confirmado protegido; `.env.example` commitado limpo, sem valor real;
- escopo do commit restrito à higiene — as Fases 0/1/2 e `discovery-books/`
  permanecem fora, para commits próprios.

**Pendências de higiene fora do escopo aprovado** (não executadas, ficam para
decisão): `.venv/` e `engine/scripts/__pycache__/livingbook.cpython-311.pyc`
seguem rastreados de commits antigos — o `.gitignore` novo impede arquivos
futuros, mas não destrackeia os que já estão. Mesmo tratamento do
`runtime/`, se quiser.

---

## Onda 1 — Determinismo comprovado: DOCX, capa e mídia (a prioridade que o usuário apontou)

**Por que primeiro:** é o único item deste plano com **evidência de execução
real** (documento 07) mostrando o custo exato do status quo — não é uma
hipótese de engenharia, é um caso medido. E não compete com a dosagem de
modelo da Fase 2: tira trabalho da coluna "LLM" inteiramente, não só troca
de tier.

| ID | Tarefa | Entregável | Esforço | Fonte |
|---|---|---|---|---|
| W1.1 | `engine/scripts/build_kdp_docx.py` — generalizar as ~425 linhas provadas em `a_morte_ainda_nao_nasceu/scripts/build_kdp_docx.py`, parametrizado por `layout/PAGE_BIBLE.md` em vez de hardcoded | Script determinístico reutilizável, testado no mesmo manuscrito que já tem resultado aprovado para comparar 1:1 | L | Doc 07 §3.1, §5.3 |
| W1.2 | `engine/scripts/build_cover_and_stories.py` — generalizar as ~258 linhas de `build_cover_and_stories.py` real, reaproveitando a lógica de cover-fit que já existe em `generate_image.py` | Script determinístico para composição tipográfica de capa/Stories | M | Doc 07 §5.3 |
| W1.3 | Declarar capacidade `docx_pdf_rendering` em `capability_requirements.yaml`/`ENGINE_GRAPH.yaml`, com caminho preferencial por host (Claude → Agent Skill nativa de `docx`; Codex/local → LibreOffice, com aviso explícito de dependência de sistema) | Nova capacidade nomeada, checável em `T001_VALIDATE_CAPABILITIES` | M | Doc 07 §3.3, §5.4 |
| W1.4 | Corrigir semântica de DPI em `validate_media_assets.py`: aceitar DPI de metadado (capa/Stories) **ou** DPI efetivo de colocação = px ÷ polegadas de inserção no DOCX (imagens internas) | Validador corrigido, com teste de regressão usando os números reais do documento 07 (1024px ÷ 3,25pol ≈ 315 DPI efetivo) | S | Doc 07 §2.7, §5.5 |
| W1.5 | Exigir hash SHA-256 no manifesto de mídia (`MEDIA_DELIVERY_CORE`), formalizado como campo obrigatório do contrato em `ENGINE_GRAPH.yaml`, não escolha ad hoc | Contrato atualizado + geração automática de hash no script de entrega | S | Doc 07 §5.6 |

**Nota de sequência interna:** W1.4 e W1.5 são pequenas e podem sair antes
de W1.1/W1.2 se o usuário quiser um primeiro lote "rápido" para aprovar
separadamente — não têm dependência entre si.

### ✅ ONDA 1 EXECUTADA — resultados

**W1.1 — `engine/scripts/build_kdp_docx.py`.** Validado reconstruindo *A Morte
Ainda Não Nasceu* e comparando com o DOCX aprovado (71 PASS / 0 FAIL):

| | Codex | Motor |
|---|---:|---:|
| Prosa do leitor | 2.933 parág. / 459.699 chars | idêntico |
| Imagens / seções / bookmarks / quebras | 24 / 67 / 24 / 70 | idêntico |
| Geometria | 8640×12960 twips | idêntico |

Dois desvios, ambos explicados: 3 parágrafos **vazios** a mais no arquivo do
Codex (resíduo do round-trip pelo Word) e forma do campo PAGEREF (`fldSimple`
pré-Word vs `fldChar` pós-Word). Nenhum é defeito. Melhoria embutida: títulos
nascem em `Heading 1`, dispensando `apply_heading1_to_chapters.py` (109 linhas).

**W1.4 — semântica de DPI.** A regra antiga errava nos dois sentidos, e ambos
foram provados por teste negativo: imagem de 1024 px com metadado 96 DPI
**passa** (315 efetivo em 3,25 pol.); imagem de 600 px com metadado 300 DPI
**reprova** (185 efetivo). Antes, a primeira seria rejeitada e a segunda aceita.

**W1.5 — proveniência.** Hash SHA-256 de cada artefato conferido contra o
manifesto; formalizado em `artifact_contract_rules` no `ENGINE_GRAPH.yaml`. O
validador extrai qualquer hash de 64 chars, então a formatação do manifesto
segue livre — obrigatório é o fato, não o layout. Teste negativo: hash
adulterado é detectado.

**W1.3 — `check_render_capability.py`.** Preflight que cria um DOCX mínimo de
controle e tenta convertê-lo. Neste ambiente reporta `BLOCKED` (sem
LibreOffice no PATH) em segundos — a mesma descoberta que, na execução real,
custou seis dias e um reboot. Capacidade nomeada em `known_capabilities` com
rota por host.

**W1.2 — `build_cover_and_stories.py`.** Três correções sobre o original:
fontes descobertas por plataforma (o original tinha caminhos fixos de Windows
— bug de portabilidade), paleta/copy configuráveis via `media/MEDIA_DESIGN.yaml`,
e um caminho `--no-base-image` que compõe só com tipografia. Esse último
**destrava o `GATE_MEDIA_ASSETS` sem custo de API** — relevante enquanto a
conta de imagem está no limite de faturamento.

**Achado colateral:** a mídia do runtime real usa nomes descritivos
(`story_01_o_gancho.jpg`) em vez dos nomes do contrato, porque foi composta
sob o motor v1.0.0, anterior ao `GATE_MEDIA_ASSETS`. O validador reprova, e
está certo: nomes fixos são o que torna a validação determinística. Isso está
agora explícito em `artifact_contract_rules.filename_note`.

**Entrega no runtime:** `copy_runtime()` passou a distribuir as sete
ferramentas + o template de layout, e `IMPLEMENT.md` ganhou uma tabela
"Deterministic tools — use these instead of reasoning" instruindo a sessão a
rodar o script em vez de reproduzir o trabalho com um agente.

---

## Onda 2 — Generalizando o mesmo princípio para QA de texto

**Por que depois da Onda 1, não junto:** é a mesma ideia (determinismo em
vez de LLM para checagem mecânica), mas sem um caso real medido por trás —
são inferências dos documentos 02/03, não uma execução observada. Mais
seguro provar o padrão uma vez (Onda 1) e só então estender.

| ID | Tarefa | Entregável | Esforço | Fonte |
|---|---|---|---|---|
| W2.1 | Script de detecção de clichê/redundância por n-gramas e similaridade de embedding, como pré-filtro determinístico antes de qualquer agente LLM tocar o texto | `engine/scripts/detect_repetition.py` + integração como `custom_validator` | M | Doc 02 §3.2, Doc 03 Pilar 3 |
| W2.2 | Fundir `CLICHE_REVIEWER` + `CLICHE_HUNTER` + `REDUNDANCY_REVIEWER` num único agente que só entra depois do pré-filtro W2.1, revisando apenas o que o script sinalizou | `agent_packs` atualizados nos livros existentes; um `.toml` a menos no motor | S | Doc 02 §3.2 |
| W2.3 | Passada gramatical determinística (ferramenta tipo regras de estilo PT-BR) antes de `PTBR_GRAMMAR_EDITOR`, que passa a revisar só os casos ambíguos sinalizados | Script + agente com escopo reduzido | M | Doc 03 Pilar 3 |
| W2.4 | Pré-filtro de continuidade: *diff* estruturado contra `CANON_REGISTRY.yaml`/`PLOT_DEPENDENCY_MAP.md` (nomes, datas, fatos) antes da releitura de prosa por `PLOT_CONTINUITY_REVIEWER`/`CHARACTER_CONTINUITY_REVIEWER`/`WORLD_RULES_REVIEWER` | Script de diff estrutural; os três agentes continuam existindo, mas só leem o que o diff não conseguiu resolver sozinho | L | Doc 02 §3.2, Doc 03 Pilar 2/3 |

**Risco a monitorar nesta onda:** falso-negativo — um script de detecção de
padrão pode deixar passar clichê que não segue o padrão esperado. Por isso
W2.1/W2.2 mantêm o agente LLM como camada final, só reduzem o volume que ele
precisa reler — não removem o julgamento humano-equivalente, removem
trabalho redundante.

---

## Onda 3 — Geração de imagem: fechando as lacunas que o documento 07 expôs

**Por que nesta posição:** depende do que já existe (`generate_image.py`,
construído numa sessão anterior), não do que as Ondas 1–2 fazem — poderia
rodar em paralelo a elas. Coloquei depois porque tem menos urgência
(o pipeline de imagem já funciona; estas são melhorias de qualidade/robustez,
não uma dor aguda como o DOCX).

| ID | Tarefa | Entregável | Esforço | Fonte |
|---|---|---|---|---|
| W3.1 | Modo `--reference <arquivo>` em `generate_image.py`: gera nova imagem usando uma imagem já aprovada como âncora de identidade | Replica o mecanismo que resolveu a consistência de Ester no capítulo 5 real | M | Doc 07 §2.4, §5.1 |
| W3.2 | Modo `--edit <arquivo> --instruction "..."` para correção pontual (inpainting-style) em vez de regeneração completa | Reduz custo de correção — um edit é mais barato que regenerar do zero | M | Doc 07 §2.4, §5.1 |
| W3.3 | `engine/templates/FACE_CANON_TEMPLATE.md` — promover a estrutura de 327 linhas encontrada em `a_morte_ainda_nao_nasceu` (código de identidade, matriz de semelhança familiar, âncoras de continuidade, lista de rejeição calibrada, rubrica numérica) a template reutilizável referenciado pelo `.toml` de `FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT` | Novo template + referência atualizada no agente | M | Doc 07 §2.3, §5.2 |
| W3.4 | `MODEL_TIERS.yaml`: separar explicitamente tier de **modelo de texto** (S/M/XS, já existe) de **modelo de imagem** (geração final sempre na melhor qualidade disponível; variante mais barata reservada para candidatos de rascunho, se o motor quiser essa granularidade) | Campo novo documentado, sem alterar a tabela de texto já validada na Fase 2 | S | Doc 07 §5.7 |

---

## Onda 4 — O que ficou pendente da própria Fase 2 (custo)

Itens que os documentos 02/04 já tinham identificado mas que não entraram no
escopo executado da Fase 0–2 (que focou em dosagem de modelo, não em volume
de chamadas).

| ID | Tarefa | Entregável | Esforço | Fonte |
|---|---|---|---|---|
| W4.1 | Digest de canon compacto (JSON/YAML estruturado, mantido por `CANON_GUARDIAN`) para a maioria dos agentes lerem em vez da bíblia completa | Reduz o crescimento quase-O(n²) de custo por capítulo | L | Doc 02 §3.2/§3.3, Doc 03 Pilar 2 |
| W4.2 | `execution_profile.yaml` (Draft/Standard/Premium) — a "torneira" de velocidade × qualidade, podando `agent_packs` e `blocking` dos gates conforme o perfil escolhido | Extensão de `build_standard_graph()` já preparada para *feature flags*; este é o mesmo mecanismo aplicado a mais um eixo | M | Doc 02 §3.4 |
| W4.3 | Consolidar `T305_DEVELOPMENTAL_REVIEW` + `T306_LINE_REVIEW` + `T307_FINAL_LITERARY_REVISION` numa única passada de polimento com checklist | Reduz 3 barreiras sequenciais a 1 | M | Doc 02 §3.2 |

---

## Onda 5 — Arquitetura de próxima geração (fora de escopo imediato)

Os sete pilares do documento 03 (orquestrador real, canon por *retrieval*,
pipeline incremental por capítulo, humano só nos pontos de maior valor)
continuam válidos como direção, mas **não têm evidência de execução real
por trás como a Onda 1 tem**, e mudam a forma como o motor é executado, não
só o que ele faz. Não proponho começar aqui — cito para não perder o fio
depois que as Ondas 1–4 estiverem rodando e puderem informar se essa
reescrita maior realmente compensa.

---

## Sequenciamento recomendado

```
Onda 0 (higiene)         → aprovação isolada, rápida, quase sem risco
Onda 1 (DOCX/mídia)      → prioridade do usuário, evidência mais forte
Onda 2 (QA de texto)     → mesmo princípio, generalizado
Onda 3 (imagem)          → pode rodar em paralelo à Onda 2
Onda 4 (custo pendente)  → depois de 1–3 provarem o padrão
Onda 5 (arquitetura v2)  → não iniciar sem revisitar após 1–4
```

## O que preciso de volta antes de tocar em qualquer código

1. Qual onda (ou quais itens dentro de uma onda) está aprovada para começar.
2. Confirmação explícita para o commit da Onda 0 (é a única ação deste plano
   que toca o histórico do git, não só arquivos locais).
3. Se alguma onda deve ser fatiada ainda mais fino antes de aprovar — cada
   linha das tabelas acima já é pequena o suficiente para ser aprovada
   individualmente, se preferir revisar item a item em vez de onda a onda.
