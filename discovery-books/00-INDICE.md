# Discovery Books — Análise do PEDRO_ARTE_LIVING_BOOK_ENGINE_v1

Pasta de output com a análise completa do repositório
`pedroarte-labs-living-book-codex-all-features`, solicitada em 2026-08-15.

**Regra respeitada:** nenhuma análise alterou código, configuração ou dados do
repositório. Tudo aqui é observação + proposta em arquivos novos, isolados
nesta pasta.

## Documentos

1. [`01-analise-estrutural.md`](01-analise-estrutural.md) — Análise estrutural completa
   (estilo "wiki" de repositório): camadas, composição, taxonomia de agentes,
   ciclo de vida de tarefas, controle de estado, e resposta direta aos 7 pontos
   pedidos (onde a LLM lê o briefing, como entende a tarefa, como os agentes
   interagem, controle de estado/artefatos, onde roda o runtime, quais são os
   outputs, onde é feito o input).

2. [`02-analise-custo-tempo.md`](02-analise-custo-tempo.md) — Diagnóstico crítico da dor
   de custo/tempo (dias a uma semana por livro), com números reais extraídos do
   próprio grafo (409+ invocações de agente por livro de 24 capítulos), e um
   plano de ação em 4 frentes: tiering de modelos, simplificação de agentes,
   performance/paralelismo, e uma "torneira" de velocidade vs. qualidade.

3. [`03-arquiteturas-propostas.md`](03-arquiteturas-propostas.md) — Proposta de arquitetura
   de próxima geração ("Living Book Engine v2"), inspirada em como pipelines de
   conteúdo longo com IA são construídos hoje profissionalmente: orquestração
   real (não role-play em uma sessão de CLI), canon via retrieval em vez de
   re-leitura de arquivo inteiro, QA determinístico onde possível, pipeline
   incremental por capítulo em vez de "big-bang waves", e telemetria de custo.

4. [`04-plano-desenvolvimento-custo.md`](04-plano-desenvolvimento-custo.md) — Plano de
   desenvolvimento focado exclusivamente em custo: mecanismo técnico de dosagem
   de modelo (`model_tier` propagado do agente até o nó do grafo), a tabela
   completa de classificação S/M/XS para os 68 agentes do motor, o "quick win"
   já meio-pronto no código (`lead_novelist_owned_chapters`), telemetria de
   custo como pré-requisito, e sequenciamento em sprints.
   **Status: Fases 0, 1 e 2 implementadas e validadas.**

5. [`05-discovery-geracao-de-imagens-claude-vs-codex.md`](05-discovery-geracao-de-imagens-claude-vs-codex.md) —
   Discovery sobre a etapa de imagem ao trocar de hospedeiro: o motor não tem
   nenhuma linha de geração de imagem (Pillow só valida), então a capacidade
   sempre foi uma dependência implícita do CLI. Compara os quatro caminhos
   possíveis no Claude (script chamando API, servidor MCP, composição via
   Pillow, `CAPABILITY_BLOCKER`), aponta onde o Claude é mais forte que o Codex
   (QA facial por visão, DOCX via Agent Skills), e recomenda mover a geração
   para `engine/scripts/` para tornar o motor independente de host.

6. [`06-discovery-livro-ponta-a-ponta-no-claude.md`](06-discovery-livro-ponta-a-ponta-no-claude.md) —
   Verificação de viabilidade ponta a ponta no Claude, capacidade por
   capacidade, com evidência classificada (provado / verificado / a construir /
   risco). Confirma que a dosagem S/M/XS é **nativa** no Claude Code
   (dispensando a Fase 1B do plano de custo), prova que o pipeline de imagem
   satisfaz `GATE_MEDIA_ASSETS`, e isola o único risco real: consistência
   facial em 24 capítulos.

7. [`07-analise-execucao-real-codex.md`](07-analise-execucao-real-codex.md) — Análise da
   execução real e quase completa do Codex em `runtime/a_morte_ainda_nao_nasceu/`
   (252/262 tarefas aprovadas). Confirma empiricamente uma ferramenta nativa
   de imagem no Codex, documenta o padrão de correção por referência+edit que
   resolveu consistência facial (43 candidatos para 24 imagens aprovadas), e
   revela a maior dor não prevista pelas análises anteriores: não foi custo de
   LLM, foi renderização frágil de DOCX (1.100+ linhas de tooling ad hoc,
   6 dias, um reboot de Windows). Recomendações concretas para o motor,
   reconciliadas com a dosagem de custo da Fase 2.

8. [`08-plano-desenvolvimento-melhorias.md`](08-plano-desenvolvimento-melhorias.md) —
   Prompt de continuação: compila todos os pontos de melhoria levantados nos
   documentos 01–07 num plano executável em 6 ondas, priorizando substituir
   processamento probabilístico por ferramentas determinísticas do motor
   (DOCX/KDP como âncora, generalizado para clichê/redundância, gramática e
   continuidade). Inclui verificação de que `runtime/` está no `.gitignore`
   e o achado de 126 arquivos órfãos ainda rastreados de antes dessa regra.
   **Status: plano aguardando aprovação — nenhum código alterado.**

## Credenciais

Nenhuma chave de API está armazenada neste repositório, por desenho — ele é
distribuível e tem remote público. `engine/scripts/generate_image.py` lê
`OPENAI_API_KEY` do ambiente. Ver `.env.example` na raiz para configurar, e
`.gitignore` para as proteções.

## Resumo executivo (uma tela)

O motor é **um gerador de grafo de tarefas em Python puro** (`engine/scripts/livingbook.py`,
zero chamadas de LLM) que combina um "motor" reutilizável (`engine/`) com o "DNA"
de uma obra (`books/<slug>/`) para produzir um `runtime/<slug>/TASK_GRAPH.yaml`
declarativo — de ~244 a ~248 nós de tarefa e 16-17 *gates* bloqueantes para um
livro de 24 capítulos. A partir daí, **toda a execução real é feita por uma LLM
dentro de uma ferramenta de coding agent (Codex CLI, a julgar pela pasta
`.codex/`)**, que interpreta o grafo, decide o que é `READY`, spawna subagentes
com as 68+ personas TOML, escreve arquivos no disco e marca estados manualmente
via `runtime_taskgraph.py mark`. Não existe orquestrador de verdade, não existe
seleção de modelo por tarefa, não existe fila, não existe telemetria de custo —
é um **sistema de blackboard baseado 100% em arquivos**, com "a memória é o
repositório" como princípio literal.

**Correção em relação à primeira leitura deste resumo:** o runtime
`antes-que-as-criancas-crescam/` está de fato intocado (órfão, 100%
`PENDING`) — mas isso não significa que o motor nunca rodou. O documento 07
analisa `runtime/a_morte_ainda_nao_nasceu/`, uma execução real do Codex com
252 de 262 tarefas aprovadas, manuscrito completo, 24 imagens de capítulo
aprovadas, capa e mídia no contrato exato de pixel, e apenas os dois últimos
*gates* (KDP/entrega) pendentes por um motivo legítimo (validação externa que
nenhuma ferramenta local substitui). O motor funciona — a maior dor real
encontrada nessa execução não foi custo de LLM, foi fragilidade de ambiente
de renderização de DOCX (ver documento 07, seção 3).
