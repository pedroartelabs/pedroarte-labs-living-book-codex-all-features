# CART_OPEN_DECISIONS — o que a autora precisa decidir para a cartografia responder "sim"

**Status: PEDIDO, não aprovação.** Nada aqui é canon. Enquanto cada item estiver aberto, o motor responde `UNDETERMINED` / `UNKNOWN` em vez de
inventar. Decisões entram uma vez, por proposta aprovada, e ficam registradas (padrão de `CART_DECISION_0001.md`).

## A. Decisões que destravam respostas (impacto direto na escrita)

| # | Decisão | Hoje | O que destrava |
|---|---|---|---|
| A1 | **Vigilância** de cada lugar (patrulhado / posto / nada). O motor lista os que estão na rota do esconderijo: Cemetery, Root Cellar Hideout | tudo `UNKNOWN` | Pergunta 5 ("esconderijo sem área vigiada") passa de `UNDETERMINED_SURVEILLANCE` a sim/não |
| A2 | **Root Cellar Hideout**: capacidade, permanência segura, descobribilidade, ocultação, isolamento de som | tudo `UNSPECIFIED` | `HD-02/03/04`; cenas de esconderijo com número |
| A3 | **Sightlines** (o que se vê de onde): vegetação ciliar do Ash Burn, altura de prédios, curvas cegas | nenhuma; dentro do alcance = `UNDETERMINED` | Afirmar "ela o viu atravessar a ponte" (`VS-01`) |
| A4 | **Passagens ocultas**: estado físico, dimensões, sentido, comprimento real | `UNSPECIFIED` (tempo esperado a passo agachado, mínimo = distância entre âncoras) | Tempos de fuga/perseguição subterrânea definitivos |
| A5 | **Ano presente da história** (`story_present_year`) | `UNKNOWN` | `--at-year`, camadas históricas, `CN-04` |
| A6 | **Perfis de mobilidade** por personagem (FIT, ferido, idoso, criança) | só `FIT` padrão | `TR-03` e janelas de perseguição por personagem |
| A7 | **Quais rotas R1–R3 são públicas** (`OQ-CART-11`) e se a R1 liga de fato o cemitério ao centro | R1 termina a ~110 m da via; ligação `EDG-U-046` é **inferida** (não impressa) | Pergunta 1 (rotas que a protagonista conhece) |

## B. Decisões de método (confirmar ou corrigir o que assumi)

| # | Decisão | Assumido | Risco se estiver errado |
|---|---|---|---|
| B1 | "7,25% da escala" = razão **linear** (Mapa B = 55,86 m/px). A leitura por área daria ≈ 15 m/px | Linear | Todas as distâncias do Mapa B (só usadas como esquemáticas hoje) |
| B2 | `walk_brisk_mps = 1,8` (passo muito rápido que dispara `TR-02`/`TR-07`) — parâmetro **meu**, derivado dos valores aprovados | 1,8 m/s | Falsos WARNING/erros em cenas apertadas |
| B3 | Ligação inferida `EDG-U-046` (R1 ↔ via da capela), 121 m | Existe, `UNCERTAIN`, não impressa | Sem ela o cemitério fica a 2,9 km do Red Stag Pub |
| B4 | `Q-MAP-AUTHOR` como **4ª** pergunta que nunca se resolve (limite configurável hoje: 3) | Aceitar 4 | O canon interpretativo reprova ao ligar o ledger |
| B5 | Conferência visual das 49 vias digitalizadas (`digitization/overlay_A.png`); nenhuma está `CONFIRMED_VISUAL` | Tudo `PROBABLE`/`UNCERTAIN` | Distâncias com erro de tortuosidade |

## C. Trabalho técnico que depende de você só para começar

- **Mapa B (arredores)**: digitalizar as vias regionais e posicionar as saídas `EXT-*` marcadas `TO_DIGITIZE` na moldura.
- **BOOK_SPEC completo de SEM ROSTO** (`books/sem-rosto/` é um pacote parcial): sem ele `features.cartography` não liga e não há capítulos com staging.
- **Ids de personagem** do ledger (hoje o motor usa placeholders `CHR-*` só em testes/exemplo).

## Como decidir

Responda item a item (sim/não/valor). Cada resposta vira uma linha em `approvals/CART_DECISION_0002.md`; o motor passa a usá-la sem mudança de código.
