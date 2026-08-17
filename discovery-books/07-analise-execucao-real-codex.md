# Análise — A Execução Real do Codex em `a_morte_ainda_nao_nasceu`

> Diferente dos discoveries anteriores (baseados em leitura estrutural do
> motor, sem execução registrada), este documento analisa uma **execução real
> e quase completa**: `runtime/a_morte_ainda_nao_nasceu/`, produzida pelo
> Codex. 252 de 262 nós em `APPROVED`, 14 de 16 *gates* fechados — só
> `GATE_KDP` e `GATE_DELIVERY` seguem pendentes, e por um motivo legítimo (ver
> §4). Isso muda o tipo de evidência disponível: não é mais "o que o motor
> promete", é "o que aconteceu de fato, com prompts, decisões, hashes e
> relatórios de QA reais". Todos os números abaixo vêm de arquivos lidos
> diretamente nesta sessão — nenhum foi estimado.

---

## 1. Panorama da execução

| | |
|---|---|
| Estado dos nós | 252 `APPROVED` / 8 `PENDING` / 1 `READY` / 1 `INITIALIZED` / 1 `CANON_APPROVED` (de 262) |
| Gates fechados | 14 de 16 — só `GATE_KDP` e `GATE_DELIVERY` em aberto |
| Capítulos | 24, todos com manuscrito aprovado, imagem aprovada, revisão de voz, legal e tradução completos |
| Versão do motor nesta composição | `pedro-arte-living-book-engine` v1.0.0 (grafo de 246 tarefas/16 gates — **anterior** ao refino de `GATE_MEDIA_ASSETS` que hoje existe no motor) |
| Ferramenta hospedeira | Codex (confirmado por `.codex/agents/`, `.codex/config.toml`, e pela ferramenta `built-in image_gen` citada nos relatórios) |

O único trabalho que falta é a validação externa final do DOCX (Print
Previewer da KDP, prova física) — algo que nenhuma ferramenta local pode
substituir, e que o Codex corretamente **não fingiu ter feito**. Isso já é um
primeiro sinal de disciplina: o motor prevê exatamente esse tipo de limite
(`STOP.FIX.REVALIDATE.CONTINUE`), e a execução o respeitou.

## 2. Qualidade de imagem — o que o Codex fez muito bem

### 2.1 O achado técnico mais importante: existe uma ferramenta nativa de imagem

`images/chapters/chapter_05/GENERATION_REPORT.md` documenta literalmente:

> *"Modo: built-in `image_gen`... Skill: `imagegen`, modo built-in
> preferencial."*

Isso **refina** — não invalida — o que os documentos 05 e 06 concluíram. A
tese central (a capacidade de gerar imagem é do host, não do motor) segue
correta e agora tem confirmação empírica: o Codex tem uma ferramenta nativa
de imagem embutida na própria CLI, algo que o Claude não tem (por isso a
rota de `engine/scripts/generate_image.py` + API externa, construída na
sessão anterior, continua sendo o caminho certo para o lado Claude — só
agora sabemos exatamente o que ela precisa igualar).

### 2.2 Prompt engineering de nível profissional

O prompt real do capítulo 5 (reproduzido integralmente no relatório) segue
uma estrutura rígida e reutilizável: `Use case → Asset type → Primary
request → Subject (com um código de identidade estável, ex. FV-ESTER-01) →
Composition/framing → Lighting/mood → Color palette → Materials/textures →
Continuity → Constraints → Avoid`. A lista de "Avoid" é longa e
extremamente específica ao risco temático do livro (`no pregnant silhouette`,
`no fetus imagery`, `no savior document`, `no supernatural yellow beam`) —
não é um prompt genérico de "ilustração bonita", é um prompt calibrado
diretamente contra as regras imutáveis e cenas protegidas do livro.

### 2.3 `FACE_CANON.md` — um padrão de qualidade acima do que o motor exige

O `.toml` genérico de `FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT` tem 5 linhas
de instrução. O que ele produziu neste runtime tem **327 linhas**: um código
de identidade por personagem (`FV-ESTER-01`, `FV-JOANA-01`...), uma "matriz
de semelhança familiar" comparando traços entre parentes, uma lista explícita
de **âncoras de continuidade** (features específicas que qualquer imagem
precisa preservar) e uma lista de **rejeição** por personagem — não genérica,
calibrada contra os vieses conhecidos de modelos de imagem para este tipo de
cena (`"glamorous silver streak with salon precision"`, `"maternal warmth
represented by permanent soft smile"`, `"beatific labor"`). Termina com uma
rubrica de pontuação numérica obrigatória (identidade estrutural ≥ 9/10,
continuidade de idade ≥ 9/10, etc.).

Isso é o tipo de artefato que separa "uma imagem bonita" de "uma imagem que
não trai o livro" — e hoje **não existe em lugar nenhum do motor genérico**
como template. É conhecimento tácito que o Codex teve que reconstruir para
este livro específico.

### 2.4 O padrão de correção que resolveu o problema de consistência facial

A análise de custo anterior (`02-analise-custo-tempo.md`) apontou consistência
facial como o maior risco de custo do pipeline visual — um loop sem limite de
tentativas. Esta execução mostra **como o problema foi resolvido na prática**,
não só que existia:

1. `candidate_v1` do capítulo 5 foi rejeitado (vazamento de luz amarela na
   pele, pseudo-texto).
2. `candidate_v2` corrigiu isso via prompt mais restritivo — passou na
   inspeção de cena, mas **falhou na FACE_QA** por deriva de identidade em
   relação aos capítulos 1–2.
3. A correção final não foi "gerar de novo e torcer" — foi **regenerar
   usando `chapter_01/candidate_v1.png` como referência de identidade**, e
   depois aplicar um **edit pontual** (não uma regeneração completa) só para
   remover uma legenda legível que sobrou.
4. `candidate_v4` passou com 9,5/10 em identidade estrutural.

Ou seja: o mecanismo que resolveu o risco foi **geração por referência de
imagem + edição localizada**, não múltiplas tentativas de geração cega. Isso
confirma, com prova real, a mitigação que o documento 06 propôs como hipótese
("`gpt-image-1` aceita imagem de entrada... permite ancorar o rosto numa
referência aprovada") — e mostra que `generate_image.py` (que hoje só faz
geração nova, sem modo de referência/edição) precisa desse modo para igualar
o resultado do Codex.

### 2.5 O overhead real de regeneração — medido, não estimado

Contei os arquivos `candidate_v*.png` em `images/chapters/`: **43 candidatos
gerados para 24 imagens finais aprovadas** — uma média de ~1,8 tentativa por
capítulo. O capítulo 5 (relatado acima) levou 4; a maioria levou 1 ou 2.
**O loop convergiu em todos os 24 capítulos, sem exceção** — o risco teórico
de loop sem limite (apontado no documento 02) não se realizou aqui, mas o
overhead de ~80% em chamadas de geração de imagem é real e mensurável, e é
exatamente o tipo de número que `logs/COST_LEDGER.md` (introduzido na Fase 0)
deveria capturar automaticamente daqui para frente.

### 2.6 Capa e mídia: o contrato de pixel já era respeitado antes do validador existir

`media/outputs/cover/A_MORTE_AINDA_NAO_NASCEU_KDP_EBOOK_COVER.jpg` mede
exatamente **1600×2560px, RGB, 300 DPI** — e os 5 Stories, exatamente
**1080×1920px, 300 DPI**. Isso bate 100% com o contrato que
`validate_media_assets.py` audita hoje, mesmo essa execução sendo anterior à
existência do validador. Ou seja: o contrato de pixel já estava certo nos
`parameters` da tarefa (`T801`/`T802` do `ENGINE_GRAPH.yaml`); o validador
que construímos na análise anterior audita uma promessa que o motor já fazia
corretamente — só não a **verificava**. `MEDIA_ASSET_MANIFEST.md` também
registra hash SHA-256 de cada arquivo final, uma prática de proveniência que
o motor genérico não exige, mas deveria.

### 2.7 Uma imprecisão a corrigir sobre DPI de imagem interna

As 24 imagens de capítulo (`images/approved/chapter_NN.jpg`) medem
1024×1536px mas **96 DPI de metadado** — abaixo do limiar de 300 que
`validate_media_assets.py` exige para capa/Stories. À primeira vista isso
pareceria uma falha de qualidade de impressão. Não é: o relatório de build do
DOCX (`T703_BUILD_REPORT.md`) mostra que essas imagens são inseridas em
**3,25 × 4,875 polegadas** — o que dá uma resolução **efetiva** de
1024/3,25 ≈ **315 DPI**, acima do limiar de impressão. O metadado de 96 DPI é
cosmético (a maioria dos geradores de imagem grava esse valor por padrão) e
**não reflete a resolução real de impressão**, que depende do tamanho de
colocação no documento, não do rótulo gravado no arquivo. Isso é uma correção
importante para qualquer validador futuro de imagens internas: checar DPI de
metadado sozinho, sem saber o tamanho de colocação no DOCX, produziria um
falso negativo.

## 3. A dor real desta execução: não foi o texto, nem a imagem — foi o DOCX

Este é o achado mais custoso, e nenhuma análise anterior deste repositório o
previu.

### 3.1 O motor não fornece nenhuma ferramenta de DOCX — o Codex construiu uma do zero

`engine/agents/kdp_formatter.toml` tem 5 linhas de instrução. O que o Codex
efetivamente escreveu para cumprir essa tarefa:

| Script | Linhas | Função |
|---|---:|---|
| `scripts/build_kdp_docx.py` | 425 | Gerador de DOCX do zero (seções, margens espelhadas, cabeçalhos pares/ímpares, `PAGEREF` bloqueado, placement de imagem `OPEN`/`HINGE`) |
| `scripts/build_cover_and_stories.py` | 258 | Compositor tipográfico de capa/Stories |
| `scripts/audit_kdp_docx.py` | 145 | Auditor estrutural do OOXML |
| `scripts/audit_kdp_render.py` | 137 | Auditor do render visual |
| `scripts/apply_heading1_to_chapters.py` | 109 | Correção de estilo de título para compatibilidade de sumário automático |
| `scripts/normalize_kdp_style_names.py` | 47 | Normalização de nomes de estilo OOXML |
| + 3 scripts PowerShell | 125 | Automação de render/reboot |

**Mais de 1.100 linhas de ferramenta, nenhuma vinda do motor**, para uma
capacidade que `capability_requirements.yaml` já declarava como obrigatória
desde o início. Isso confirma, com evidência concreta em vez de inferência de
código ausente, a lacuna já apontada no documento 05: `python-docx` está
instalado, nenhum código do motor o usa.

### 3.2 A verdadeira dor: o ambiente de renderização, não o conteúdo

O relatório `T704_KDP_QA.md` narra uma sequência de falhas de infraestrutura
completamente alheias à qualidade do livro:

1. `Word SaveAs2` para PDF **trava mesmo num DOCX de uma linha** (teste de
   controle isolando o problema do ambiente, não do livro).
2. `Word PrintOut` para "Microsoft Print to PDF" também trava.
3. LibreOffice teve que ser baixado manualmente (com verificação de hash),
   extraído sem instalação — e mesmo assim travou.
4. Foi necessário atualizar o **Microsoft Visual C++ Redistributable**
   (14.40 → 14.51), cujo instalador retornou código `3010`: **requer reinício
   do Windows**.
5. O reinício não foi automático — o processo ficou bloqueado esperando uma
   ação fora do controle do agente.
6. Só depois do reboot, com LibreOffice Portable 25.2.7.2, o render
   finalmente funcionou: 263 páginas renderizadas, 17 *contact sheets*,
   inspeção completa.

Essa cadeia — de 2 a 8 de agosto de 2026, seis dias — não tem nada a ver com
escrita, canon ou imagem. É **fragilidade de ambiente de renderização de
documento**, e é provavelmente o maior componente de tempo-de-parede desta
execução inteira. Nenhum dos documentos de análise anteriores (01–06) previu
essa categoria de dor — todos focaram em custo de token de LLM. Este é um
tipo de custo diferente: **custo de infraestrutura frágil**, e ele é
evidenciado aqui pela primeira vez com dados reais.

### 3.3 Por que isso é uma boa notícia para o lado Claude

O Claude tem uma *Agent Skill* nativa de `.docx` que produz o arquivo e não
depende de instalar LibreOffice, mexer em runtime C++ ou reiniciar o sistema
operacional. Isso não é uma vantagem teórica — à luz desta execução real, é a
correção direta do maior ponto de fragilidade observado. Vale, porém, uma
ressalva: a *skill* precisa ser testada contra os requisitos específicos que
este runtime provou serem necessários (margens espelhadas, cabeçalhos
pares/ímpares, `PAGEREF` bloqueado, placement `OPEN`/`HINGE` de imagem,
estilo `Heading 1` para sumário automático) — não é garantido que ela cubra
tudo isso pronta, mas o caminho de falha (ambiente de renderização) deixa de
existir por construção.

## 4. Confirmação empírica do diagnóstico de custo

Busquei em todo o runtime por qualquer menção a modelo usado, tokens ou
custo: **zero ocorrências**. Não existe `logs/COST_LEDGER.md` (a Fase 0 é
posterior a esta execução), não existe nenhum registro de qual modelo de
linguagem executou qual tarefa. Isso é a confirmação empírica, não mais só
estrutural, do diagnóstico central de `02-analise-custo-tempo.md`: **esta
execução real rodou sem nenhum rastreamento de custo ou diferenciação de
modelo, exatamente como a análise estrutural previu antes de qualquer
execução existir.**

## 5. Recomendações concretas para o motor

Cada uma abaixo já nasce pensada para não contradizer a dosagem de custo da
Fase 2 — a maioria delas *reduz* custo (menos regeneração, menos ambiente
quebrado) em vez de competir com ela.

### 5.1 Adicionar modo de referência e edição pontual a `generate_image.py`

Hoje o script só faz geração nova. Adicionar dois modos, espelhando
exatamente o padrão que resolveu o capítulo 5 no Codex:
- `--reference <arquivo>`: gera usando uma imagem aprovada anterior como
  âncora de identidade (equivalente ao que salvou a consistência de Ester).
- `--edit <arquivo> --mask-instruction "..."`: edição localizada em vez de
  regeneração completa, para correções pontuais (remover um texto legível,
  por exemplo) sem arriscar nova deriva de identidade.

Isso **reduz custo**: um edit pontual é mais barato que uma regeneração
completa, e evita reintroduzir problemas já resolvidos em outras partes da
imagem.

### 5.2 Promover `FACE_CANON.md` desta execução a template do motor

Os 327 linhas de canon facial encontrados aqui — código de identidade,
matriz de semelhança familiar, âncoras de continuidade, lista de rejeição
calibrada, rubrica numérica — deveriam virar
`engine/templates/FACE_CANON_TEMPLATE.md`, referenciado pelo `.toml` de
`FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT`. Isso não é sobre gastar mais: é
sobre não perder, a cada livro novo, um padrão de qualidade que já foi
provado — e reduz custo porque uma definição de canon mais precisa na
primeira tentativa gera menos candidatos rejeitados depois (o overhead de
1,8× do §2.5 tende a cair quanto mais específico for o canon inicial).

### 5.3 Trazer `build_kdp_docx.py` e `build_cover_and_stories.py` para o motor genérico

As ~700 linhas centrais (excluindo os scripts de auditoria de ambiente, que
são específicos da fragilidade do Codex) resolvem um problema genérico —
qualquer livro composto por este motor vai precisar exatamente da mesma
estrutura de seções, margens espelhadas, cabeçalhos pares/ímpares e
placement de imagem. Reescrever isso a cada livro é o oposto do princípio
central do motor ("o motor cuida da fábrica"). Trazer essas ~700 linhas para
`engine/scripts/`, parametrizadas por `layout/PAGE_BIBLE.md`, é puro ganho:
menos custo (não se reinventa a cada execução) e mais qualidade (a versão
testada e comparada pixel-a-pixel nesta execução vira o padrão, não um
protótipo descartável).

### 5.4 Declarar `docx_pdf_rendering` como capacidade explícita, com caminho preferencial por host

Adicionar a `capability_requirements.yaml` uma capacidade nomeada para
render-QA de DOCX, com resolução diferente por host: Codex/ambiente local →
LibreOffice (com o aviso explícito de que pode exigir dependências de
sistema); Claude Code → *Agent Skill* de `docx` nativa. Isso transforma uma
crise de ambiente de 6 dias em uma checagem de capacidade de 1 tarefa,
seguindo exatamente a doutrina que `T001_VALIDATE_CAPABILITIES` já existe
para aplicar — só faltava esta capacidade estar nomeada.

### 5.5 Corrigir a semântica de DPI para imagens internas

`validate_media_assets.py` deveria aceitar dois critérios diferentes: DPI de
metadado (para capa/Stories, usadas em tamanho nativo) **ou** DPI efetivo de
colocação = pixels ÷ tamanho físico de inserção no DOCX (para imagens
internas). Sem essa distinção, um validador mais rigoroso no futuro
reprovaria, por engano, exatamente o tipo de imagem que esta execução provou
ser adequada para impressão.

### 5.6 Exigir hash SHA-256 no manifesto de mídia, como padrão do motor

`MEDIA_ASSET_MANIFEST.md` desta execução já inclui hash de cada arquivo —
isso deveria ser um campo obrigatório do contrato `MEDIA_DELIVERY_CORE` no
`ENGINE_GRAPH.yaml`, não uma escolha ad hoc de uma execução específica.

### 5.7 Sobre "usar os modelos no nível mais alto" — a resposta que reconcilia com a dosagem

O pedido de usar sempre o melhor modelo para imagem **não contradiz** a
dosagem S/M/XS da Fase 2, porque são eixos diferentes: a tabela de tiers
dosa **modelo de texto** por tarefa; a geração de pixel é uma dimensão
separada. A recomendação concreta é:

- A **geração real de pixel** (a chamada que produz o arquivo final) deve
  sempre usar a melhor qualidade de imagem disponível — uma imagem cara é
  ordens de magnitude mais barata que refazer trabalho editorial por causa
  de uma reprovação evitável em `FACE_QA`.
- O **brief que antecede a geração** (`CHAPTER_IMAGE_DIRECTOR`, hoje Tier M)
  pode continuar em Tier M — como a seção 2.3 mostrou, o brief já entrega o
  prompt quase pronto; a etapa de geração em si não precisa de mais
  "inteligência" de texto, precisa de melhor modelo de imagem.
- Onde isso já existe como *hook* no motor: `engine/MODEL_TIERS.yaml`
  permanece o lugar certo para declarar qual modelo de imagem usar por
  padrão (hoje ilustrativo, `gpt-image-1`) — o ajuste é usar sempre a
  variante de maior qualidade disponível nesse campo para geração final,
  mantendo variantes mais baratas (`gpt-image-1-mini`, já com preço
  cadastrado) reservadas para candidatos de rascunho/teste antes da geração
  definitiva, se o motor algum dia quiser essa granularidade.

## 6. Síntese

Esta execução é, ao mesmo tempo, a melhor prova de que o motor funciona (24
capítulos, canon consistente, imagens de alta qualidade com identidade
facial preservada, capa e mídia no contrato exato) e a melhor evidência de
onde ele ainda exige reinvenção cara a cada livro: DOCX do zero, ambiente de
renderização frágil, nenhum rastreamento de custo. As recomendações acima não
pedem menos qualidade em nome de economia — pedem que a qualidade já provada
aqui pare de ser descartável.
