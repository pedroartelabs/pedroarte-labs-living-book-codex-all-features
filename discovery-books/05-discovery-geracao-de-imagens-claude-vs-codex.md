# Discovery — Geração de Imagens: Codex (DALL·E) vs. Claude

> **Pergunta investigada:** o Codex foi o hospedeiro nativo deste motor e gera as
> imagens via DALL·E. Se a criação de um livro fosse executada no Claude — que
> não usa DALL·E — como o Claude lidaria com a etapa de imagem? Ele buscaria uma
> forma nova de criar a imagem, ou seria preciso conectar um servidor MCP que
> chamasse o DALL·E por trás?
>
> **Escopo:** este documento é discovery, não implementação. Nenhum código do
> motor foi alterado para produzi-lo.

---

## 1. Achado que enquadra tudo: o motor não gera imagem — em nenhum host

Antes de comparar hospedeiros, o dado mais importante veio do próprio
repositório: **não existe uma única linha de geração de imagem no motor.**

- `Pillow` está em `requirements.txt`, mas é usado **exclusivamente para
  validar** (`engine/scripts/validate_media_assets.py` checa dimensão, modo de
  cor e DPI). Nunca para criar.
- Busca por qualquer API de imagem (`openai`, `dall`, `gpt-image`,
  `stable diffusion`, `midjourney`, `api_key`) em `engine/`, `books/`,
  `AGENTS.md` e `README.md`: **zero ocorrências**.
- O `.toml` do `IMAGE_GENERATOR` diz literalmente *"Executa **ou prepara**
  geração de imagens editoriais"*. O "ou prepara" é a hesitação do próprio
  desenho: o motor não sabe se o hospedeiro consegue gerar pixels.

**Conclusão:** a capacidade de gerar imagem **nunca foi do motor** — sempre foi
uma dependência implícita do hospedeiro. No Codex isso ficou invisível porque a
capacidade estava lá. A pergunta sobre o Claude não expõe uma limitação do
Claude; expõe uma **dependência oculta que o motor sempre teve** e que só se
torna visível ao trocar de host.

## 2. Resposta direta: o Claude não "inventaria" uma forma de gerar a imagem

Nenhum modelo Claude produz imagem raster como saída. O Claude é multimodal na
**entrada** (lê e interpreta imagens), não na saída. Isso não é uma limitação
de configuração ou de plano — é uma propriedade do modelo. Não existe prompt,
flag ou ferramenta interna que faça o Claude "desenhar".

Então a resposta honesta à primeira metade da pergunta é: **não, o modelo não
buscaria uma nova forma de criar a imagem por conta própria.** O que ele faria,
posto diante da tarefa `T4xx_IMAGE_GENERATE`, é uma destas quatro coisas — e
vale conhecer as quatro porque só uma delas é a resposta certa para este motor:

### Caminho A — Escrever código que chama uma API de imagem externa

O Claude escreve um script (Python/Node) que chama a API de imagem de terceiro
— inclusive a própria API de imagens da OpenAI, a mesma que está por trás do
DALL·E — e salva o JPEG no caminho declarado pela tarefa.

**Detalhe técnico que importa muito aqui, e que é contraintuitivo:** existem
dois ambientes de execução no mundo Claude, e eles se comportam de forma
oposta neste ponto.

| Ambiente | Rede? | Serve para chamar API de imagem? |
|---|---|---|
| **Bash do Claude Code** (CLI local, o análogo direto do Codex CLI) | Sim — roda na máquina do usuário | **Sim.** É o caminho viável. |
| **Ferramenta server-side `code_execution`** (sandbox da API) | **Não** — o sandbox é totalmente isolado, sem internet | Não. Serve para gerar imagem *programaticamente*, não para chamar API. |

Ou seja: no Claude Code — que é o cenário equivalente ao Codex CLI — o caminho
A funciona hoje, desde que exista chave de API e acesso à rede. É a tradução
mais direta do que o Codex já faz.

### Caminho B — Servidor MCP (a hipótese da pergunta)

Funciona, e em duas variantes distintas:

- **MCP local no Claude Code**: um servidor stdio registrado na configuração do
  projeto, expondo uma ferramenta `generate_image` que encapsula a chamada ao
  DALL·E. A geração vira uma *tool call* nativa em vez de um comando de shell.
- **Conector MCP da própria API Claude**: `mcp_servers` + `mcp_toolset` (beta
  `mcp-client-2025-11-20`), em que a Anthropic conecta ao servidor MCP remoto
  do lado do servidor.

**Vale a pena?** Depende do que você quer. O MCP paga por si quando: várias
ferramentas/agentes precisam gerar imagem, você quer entradas tipadas e erros
estruturados, ou quer trocar de provedor de imagem sem tocar em quem chama.
Não paga por si se for só este motor chamando uma função — aí é um servidor a
mais para configurar, rodar e manter, resolvendo o mesmo que um script resolve.

**Portanto: MCP é *uma* resposta correta, não a *única*.** A pergunta assumia
que seria necessário; a verificação mostra que é opcional.

### Caminho C — Composição programática com Pillow (sem API nenhuma)

Aqui há uma assimetria que vale explorar, porque o motor exige dois tipos muito
diferentes de imagem:

| Artefato | Natureza | Pillow resolve? |
|---|---|---|
| Capa KDP (1600×2560) + 5 Stories (1080×1920) | Majoritariamente tipografia sobre fundo, composição gráfica | **Sim.** E o Pillow já é dependência declarada. |
| 24 ilustrações conceituais de capítulo, com consistência facial | Arte generativa | **Não.** Precisa de modelo de imagem. |

Isso significa que a parte **bloqueante da entrega** (`GATE_MEDIA_ASSETS` —
capa + 5 Stories, o único gate com validação determinística real) pode ser
resolvida sem nenhuma API de imagem, com a biblioteca que o repositório já
instala. Só as 24 ilustrações exigem geração de verdade.

### Caminho D — Emitir `CAPABILITY_BLOCKER`

É a resposta que o motor **projetou** para este caso:
`capability_requirements.yaml` declara `raster_image_generation: {required: true,
count: 24, format: jpg}`, `CAPABILITY_BLOCKER` está nos
`generic_rejection_states`, e `T001_VALIDATE_CAPABILITIES` roda logo após o
bootstrap justamente para detectar isso cedo.

Um Claude bem-comportado seguindo o `IMPLEMENT.md` **pararia e sinalizaria** em
vez de fingir. Isso é o desenho funcionando, não falhando.

## 3. Onde o Claude é melhor que o Codex neste pipeline

A comparação não é de mão única. Duas fases do motor são mais fortes no Claude:

**QA visual (`T4xx_FACE_QA`, `IMAGE_CONTINUITY_QA` — 48 tarefas).** Essas
tarefas não geram imagem: elas **olham** a imagem gerada e comparam com o
`FACE_CANON`. Isso é visão de entrada, exatamente o que o Claude faz bem. O
Claude lê o JPEG gerado e julga consistência facial contra a referência
canônica. A geração pode ser terceirizada; o julgamento não precisa ser.

**Produção do DOCX/KDP.** O Claude tem *Agent Skills* nativas para `docx`,
`xlsx`, `pptx` e `pdf`, que rodam no sandbox de execução e devolvem o arquivo
binário pronto. Para a fase `T703_BUILD_DOCX` → `T705_DOCX_FINAL_FIXES`, isso é
um caminho de primeira classe — enquanto no motor atual essa etapa é só uma
persona de prompt (`KDP_FORMATTER`) torcendo para o host saber gerar `.docx`.

Ou seja, uma divisão realista de forças:

```
geração das 24 ilustrações  → precisa de modelo de imagem (Codex/DALL·E, ou API via script)
QA facial e de continuidade → Claude (visão de entrada)
capa + 5 Stories            → Pillow, em qualquer host
DOCX / KDP                  → Claude (Agent Skills) ou script determinístico
```

## 4. A recomendação: tornar a pergunta irrelevante

A conclusão arquitetural deste discovery não é "use Codex" nem "use Claude". É:
**a geração de imagem não deveria ser uma propriedade do host.**

Hoje ela é uma dependência invisível: troque de CLI e o pipeline quebra numa
fase tardia e cara. A correção é a mesma que o repositório já aplicou para
validação — um script determinístico em `engine/scripts/`:

```
engine/scripts/validate_media_assets.py   ← já existe: VALIDA imagem (Pillow)
engine/scripts/generate_image.py          ← proposto: GERA imagem (API), o par que falta
```

Um `generate_image.py` que receba prompt + caminho de saída + dimensões, chame
o provedor configurado e salve o JPEG com DPI correto tem três consequências
boas:

1. **Encaixa no padrão que o motor já tem.** Ele vira o irmão simétrico do
   validador — um gera, o outro confere.
2. **Funciona em Codex e em Claude igualmente**, porque ambos sabem executar um
   script. O motor deixa de depender de qual CLI abriu o repositório — que é
   exatamente o princípio de separação que o repo já declara em `AGENTS.md`.
3. **Torna a consistência facial controlável.** Chamando a API diretamente,
   você controla os parâmetros de referência de personagem. Isso ataca o pior
   modo de falha de custo identificado na análise 02: `face_consistency_required:
   true` + 24 imagens + `T4xx_FACE_QA` bloqueante = laço `STOP → FIX →
   REVALIDATE` sem limite declarado, disparado **depois** de o manuscrito
   inteiro já estar pago. Vale notar que o DALL·E 3 historicamente não expõe
   controle de semente nem referência de personagem — então mesmo no Codex esse
   risco existe, e escolher um modelo de imagem com suporte a imagem de
   referência importa mais para o custo do que escolher o CLI.

## 5. Resposta consolidada às duas perguntas

**"O modelo buscaria uma nova forma de criar a imagem?"**
Não. Nenhum modelo Claude gera imagem. Ele escreveria código que chama uma API
de imagem externa (viável no Bash do Claude Code, **não** no sandbox
server-side, que não tem rede), ou comporia a imagem com Pillow quando ela for
tipográfica, ou — seguindo o `IMPLEMENT.md` — emitiria `CAPABILITY_BLOCKER` e
pararia.

**"Seria preciso um servidor MCP com DALL·E por trás?"**
É uma solução válida, mas **não é obrigatória**. Um script chamando a API
resolve o mesmo problema com menos peças móveis. O MCP passa a valer a pena
quando várias ferramentas ou agentes precisarem da mesma capacidade, ou quando
você quiser trocar de provedor de imagem sem tocar em quem chama.

**A recomendação que atravessa as duas:** independentemente do host escolhido,
tirar a geração de imagem de "capacidade implícita do CLI" e colocá-la em
`engine/scripts/` como código explícito. Isso remove a dependência oculta,
funciona nos dois hosts, e dá controle sobre o parâmetro (referência facial) que
mais afeta o custo do pipeline visual.
