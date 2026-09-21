# Cartografia canônica — runbook do CANON_GUARDIAN e dos planejadores de cena

Capability `features.cartography` (SDD `docs/sdd/*CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md`). Este arquivo é copiado para
`canon/CARTOGRAPHY_RUNBOOK.md` quando a feature está ligada. **A cartografia conhece estrutura; o canon narrativo conhece
significado.** Ela diz onde as coisas estão e quanto custa ir de uma a outra; nunca diz o que significam.

## O que você pode e não pode fazer

| Você pode | Você não pode |
|---|---|
| Consultar distância, tempo, rota, alcance e visão (`check_cartography.py --canon canon/cartography ...`) | Digitar coordenada (elas derivam de pixel × escala da fonte) |
| Declarar cena em `canon/cartography/STAGING.yaml` (`PLANNED`) | Marcar `REALIZED` sem a cena existir no manuscrito |
| Propor mudança física por **mutação** (ponte cai, passagem selada) com `proposal_ref` e `cause` | Editar seed ou estado no lugar: o estado atual é sempre `fold(seed, mutações)` |
| Usar só as passagens que o personagem **conhece** (baseline ou `knowledge_delta`) | Fazer o POV usar passagem oculta que ele não aprendeu (`KN-01`) |
| Registrar esconderijo novo **por proposta** | Usar um lugar qualquer como esconderijo (`HD-01`) |
| Afirmar o que está dentro do alcance de detecção **com** sightline aprovada | Afirmar que alguém viu ou reconheceu outro sem base (`VS-01`; reconhecer é do canon narrativo) |

## Fluxo por capítulo

1. **Brief.** Declare staging e movimentos `PLANNED` (lugares `RM-*`, relógio `DnnnTHH:MM`, modo, condições).
2. **Pack.** `python scripts/check_cartography.py --runtime . --pack --chapter N` → `briefs/cartography/CHAPTER_NN_PACK.yaml`.
   O pack lista o possível e o proibido; a cena escolhe. Passagens ocultas desconhecidas pelo POV aparecem só como contagem.
3. **Escrita.** O escritor lê o pack junto com o brief.
4. **Wave.** `--mode wave` valida só o que está `REALIZED`. `FAIL/HIGH` reprova; `WARNING/MEDIUM` vai ao relatório; `INFO` é tensão dramática legítima
   (ex.: `PLANNED_ON_FALSE_BELIEF`, `MUTATION_DIVERGES_FROM_PRINTED_MAP`).
5. **Snapshot.** Ao fim da wave, `T2nnY_CARTOGRAPHY_SNAPSHOT` congela o estado. Renomear lugar sem mutação (`CN-06`) e mutação com efeito em
   capítulo congelado (`CN-07`) reprovam na wave seguinte.

## Mistério: as quatro barreiras

- Não existe classe de saída "verdadeira": as saídas são `APPARENT/OFFICIAL/HISTORICAL/CLOSED/DISPUTED/FALSE/UNKNOWN_EXIT`. O que há além da moldura é `OFF_MAP`.
- Nenhum campo de resposta (`truth`, `answer`, `solution`, `true_exit`...) em nenhum arquivo da cartografia.
- A única ponte para a verdade é `truth_ref`, id opaco do Story Truth Ledger; o conteúdo nunca é copiado para cá.
- `--exits` devolve classes e alegações; `--exit-truth` devolve só ponteiros, e só confirma pertinência com `--engine-view --authorized-by <GT-*>`.

Anomalias dos mapas classificadas `INTENTIONAL_ARTIFACT` **não são interpretadas**: intencional diz "foi posto ali de propósito", nunca *por quê*.
Autoria dos mapas é `MUST_REMAIN_UNKNOWN`: nenhuma busca resolve, nenhum `knowledge_delta` ensina.

## O que a autora precisa decidir para o motor responder "sim"

Enquanto estes campos estiverem `UNKNOWN`/`UNSPECIFIED`, o motor responde `UNDETERMINED` em vez de inventar: vigilância de lugares, capacidade/permanência/
descobribilidade de esconderijos, sightlines e obstáculos de visão, estado físico/dimensões das passagens ocultas, ano presente da história. Cada decisão entra por
proposta aprovada, uma vez, e fica registrada.
