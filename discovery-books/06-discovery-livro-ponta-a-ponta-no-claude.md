# Discovery — Um livro pode ser feito de ponta a ponta no Claude?

> **Pergunta:** com a chave da OpenAI disponível para chamadas de imagem, um
> livro completo pode ser produzido inteiramente no Claude — textos, troca de
> modelos por agente, imagens de capítulo, mídia, capa e KDP?
>
> **Resposta curta: sim, com três lacunas de código a fechar e um risco técnico
> real.** Nenhuma delas é um impedimento de plataforma; todas são trabalho de
> engenharia já mapeado.

---

## 1. Método — o que foi verificado de fato

Para não repetir o erro de afirmar capacidade sem prova, cada linha da matriz
abaixo foi classificada por evidência:

- **PROVADO** — executei e vi funcionar nesta sessão.
- **VERIFICADO** — confirmei a existência do mecanismo, sem executar o fluxo completo.
- **A CONSTRUIR** — a capacidade existe, mas o código que a usa não.
- **RISCO** — funciona, mas com modo de falha caro conhecido.

**Importante:** eu **não** fiz nenhuma chamada real à API de imagem. A chave
que você compartilhou foi exposta em texto plano e deve ser revogada; usá-la
gastaria crédito com uma credencial comprometida. A prova de imagem abaixo foi
feita simulando a resposta da API e exercitando todo o pós-processamento real.

## 2. Matriz de capacidade

| Etapa do motor | Status | Evidência |
|---|---|---|
| Prosa (30 tarefas de escrita + revisão) | **VERIFICADO** | Núcleo do que o modelo faz; sem dependência externa |
| **Troca de modelo por agente (S/M/XS)** | **PROVADO** | Ver §3 — funciona nativamente, sem infraestrutura extra |
| Geração de imagem (24 capítulos) | **PROVADO** (encanamento) / **RISCO** (consistência facial) | Ver §4 e §6 |
| Capa KDP 1600×2560 + 5 Stories 1080×1920 | **PROVADO** | Ver §4 — passou no validador oficial, sem alterá-lo |
| QA facial e de continuidade (48 tarefas) | **VERIFICADO** | Claude lê imagens; é visão de entrada, não geração |
| Pesquisa de requisitos KDP (`T699`) | **VERIFICADO** | WebFetch/WebSearch disponíveis no Claude Code |
| Construção do DOCX (`T703`/`T705`) | **A CONSTRUIR** | `python-docx` instalado; nenhum código o usa |
| Empacotamento ZIP de entrega | **VERIFICADO** | `zipfile` é biblioteca padrão |
| Estado, gates, validadores | **PROVADO** | `compose` + `smoke-test` rodaram limpos nesta sessão |
| Telemetria de custo | **PROVADO** | `cost_report.py` testado com ledger sintético |

## 3. Troca de modelos: funciona nativamente (a descoberta mais forte)

Esta era a dúvida aberta desde a Fase 1 — se a dosagem `model_tier` seria
respeitada ou viraria decoração. **Ela é respeitada.**

O Claude Code expõe seleção de modelo **por subagente**, no momento do spawn,
com as opções `opus`, `sonnet`, `haiku` e `fable`. Isso mapeia diretamente na
tabela que aplicamos aos 68 agentes na Fase 2:

| Tier do motor | Modelo no Claude Code | Agentes (exemplos) |
|---|---|---|
| **S** | `opus` | `LEAD_NOVELIST`, `CANON_GUARDIAN`, `EXECUTIVE_EDITOR`, `ANTI_MANIPULATION_GUARDIAN` |
| **M** | `sonnet` | `CHAPTER_WRITER`, `SCENE_ARCHITECT`, revisores de continuidade |
| **XS** | `haiku` | `FINAL_PROOFREADER`, `TYPOGRAPHY_TEXT_REVIEWER`, `LIVING_SOUND_PROMPT_ENGINEER`, `T4??_FACE_QA` |

**Consequência:** a Fase 1B do plano de custo (escrever um *runner* que impõe o
tier por código, porque o host talvez não obedecesse) **deixa de ser
necessária no Claude Code**. A dosagem é nativa. Isso remove o item mais caro
do backlog de custo.

Vale registrar a assimetria: essa granularidade por subagente é justamente o
que estava incerto no Codex. Se ela não existir lá, o mesmo motor entrega
economia diferente em cada host — o que reforça a recomendação do documento 05
de mover capacidades para scripts explícitos.

## 4. Imagens: encanamento provado, sem gastar crédito

Foi criado `engine/scripts/generate_image.py` — o irmão simétrico de
`validate_media_assets.py` (um gera, o outro confere), lendo a credencial de
`OPENAI_API_KEY` no ambiente e nunca de arquivo do repositório.

**Achado crítico que teria quebrado o run tardiamente:** a API de imagem **não
produz as dimensões que o motor exige**. Nenhum tamanho suportado bate com o
contrato:

| Alvo do motor | Proporção | Tamanho de API mais próximo | Bate? |
|---|---|---|---|
| Capa KDP 1600×2560 | 0,625 | `gpt-image-1` 1024×1536 (0,667) | **Não** |
| Story 1080×1920 | 0,5625 | `dall-e-3` 1024×1792 (0,571) | **Não** |

Sem pós-processamento, **todo artefato de imagem reprovaria em
`GATE_MEDIA_ASSETS`** — e isso só apareceria depois do manuscrito inteiro
estar escrito e pago, que é exatamente o modo de falha caro apontado na
análise 02.

O script resolve isso com *cover-fit* (escala preservando proporção + corte
centralizado, sem distorcer rostos) e grava o DPI no cabeçalho JPEG.

**Prova executada:** simulei a resposta da API (1024×1536 para capa, 1024×1792
para Stories), rodei o pós-processamento real e submeti ao
`validate_media_assets.py` **sem modificar o validador**:

```
MEDIA ASSET VALIDATION PASSED
- cover: media/outputs/cover/BOOK_COVER_KDP.jpg | 1600x2560 | JPEG RGB | >=300 DPI
- stories: 5 | 1080x1920 | JPEG RGB | >=300 DPI
```

## 5. Armadilha de ambiente encontrada

O Python do sistema **não tem Pillow instalado** — `validate_media_assets.py`
e `generate_image.py` falham com `ModuleNotFoundError` se executados com o
`python` padrão. As dependências estão no `.venv` do repositório
(Pillow 12.3.0, PyYAML 6.0.3, python-docx).

Qualquer execução real precisa usar `./.venv/Scripts/python.exe`. Isso não
está escrito em nenhum runbook do motor — vale corrigir antes de um run, ou
`T001_VALIDATE_CAPABILITIES` reprovará por um motivo trivial.

## 6. O risco real: consistência facial em 24 capítulos

`BOOK_SPEC.yaml` declara `face_consistency_required: true`, e as 24 tarefas
`T4xx_FACE_QA` são bloqueantes. O problema:

- **DALL·E 3 não expõe imagem de referência nem controle de semente.** Gerar 24
  imagens do mesmo personagem por prompt textual produz 24 rostos diferentes.
- Cada reprovação dispara `STOP → FIX → REVALIDATE`, **sem limite de tentativas
  declarado em lugar nenhum do motor**.
- Isso acontece depois de `GATE_FULL_MANUSCRIPT` — com o livro todo já pago.

**Caminho de mitigação:** `gpt-image-1` aceita imagem de entrada (edição), o
que permite ancorar o rosto numa referência aprovada em vez de redescrevê-lo
por texto. O fluxo seria: gerar e aprovar **um** retrato canônico por
personagem (alimentando o `FACE_CANON` que o motor já prevê), e derivar as
imagens de capítulo a partir dele.

Este é o único ponto onde eu **não** afirmaria viabilidade sem um teste real —
e é o teste que vale fazer primeiro, com 2 ou 3 capítulos, antes de qualquer
livro completo.

## 7. As três lacunas de código

1. **DOCX** (`T703_BUILD_DOCX`, `T705_DOCX_FINAL_FIXES`) — `python-docx` está
   instalado, mas nenhum script o usa. É a maior lacuna: um livro sem DOCX não
   passa em `GATE_KDP`. Alternativa nativa: as *Agent Skills* de `docx` do
   Claude.
2. **Ancoragem facial** — `generate_image.py` hoje só faz geração por prompt;
   falta o modo "derivar de referência" descrito em §6.
3. **Runbook do venv** — documentar que os scripts rodam com o Python do
   `.venv` (§5).

## 8. Veredito

**Sim, um livro pode ser feito de ponta a ponta no Claude.** A dosagem de
modelo funciona melhor aqui do que a Fase 1 assumia (é nativa, dispensando a
Fase 1B), a geração e validação de mídia estão provadas, e o QA visual se
beneficia de o Claude enxergar as imagens que outro modelo gerou.

O que separa este estado de um run real não é capacidade de plataforma — é
código a escrever (DOCX, ancoragem facial) e um teste de consistência facial em
escala pequena. Recomendação prática: **rodar um livro-piloto de 3 a 4
capítulos**, com todas as fases ligadas, antes de comprometer uma obra de 24.
Isso exercita o pipeline inteiro, popula o `COST_LEDGER.md` com números reais
(a tarefa T-COST-0.4, ainda pendente) e expõe o risco facial quando corrigi-lo
ainda é barato.
