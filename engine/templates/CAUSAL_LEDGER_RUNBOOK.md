# Runbook — `canon/CAUSAL_LEDGER.yaml`

Este runtime usa a capability `DARK_ROMANCE_CANON_ARCHITECT`
(`features.causal_ledger.enabled: true` no `BOOK_SPEC.yaml` deste livro).
Veja `docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md` no repositório do
motor para o desenho completo — este arquivo basta para executar a tarefa,
não é preciso ler o SDD.

## O que é

Um segundo arquivo de canon, ao lado de `canon/CANON_REGISTRY.yaml`, que
registra **causalidade e memória** para personagens e relacionamentos:
Ground Truth de personagem, deltas de relação, dívida narrativa (loops) e
crenças do leitor — como eventos, nunca como "estado atual" solto. Estado
atual é sempre **projetado** a partir de eventos; nada além de eventos e
camadas de personagem é armazenado.

## Dono e protocolo

Mesma disciplina de `CANON_REGISTRY.yaml`:

- **Dono exclusivo:** `CANON_GUARDIAN`, sob o lock `CANON_WRITE`.
- Escritores (`CHARACTER_PSYCHOLOGIST`, `PLOT_ENGINEER`, `CHAPTER_WRITER`,
  `LEAD_NOVELIST`, `SCENE_ARCHITECT`) **propõem** em `canon/CANON_PROPOSALS`;
  não escrevem o ledger diretamente.
- Um evento nasce `status: PLANNED` (plano, pode mudar livremente — o leitor
  ainda não viu) e só `CANON_GUARDIAN` promove para `status: REALIZED`
  depois que a prosa realmente o produziu.
- Um evento `REALIZED` é imutável: `facts`, `caused_by` e `consent` nunca
  mudam depois de aprovados (INV-10). Uma correção legítima vira uma nova
  entrada em `mutation_log`, nunca uma edição silenciosa do que já existe.

## Onde cada tarefa contribui

| Tarefa | O que propõe para o ledger |
|---|---|
| `T013_CHARACTER_BIBLE` | `ground_truth`, `self_model`, `social_persona` de cada personagem maior (LAW 01: as três camadas nunca colapsam numa só). |
| `T016_PLOT_DEPENDENCY_MAP` | Eventos `PLANNED`, `loops` (dívida narrativa) e as crenças do leitor (`beliefs`) que o enredo pretende formar. |
| `T018_CANON_REGISTRY` | Escreve o arquivo de fato: promove propostas a `characters`/`relationships`/`loops`/`beliefs`/`events` aprovados. |
| `T032_READER_VITALS` | Define o pulso/gap informacional **pretendido** por capítulo — não é canon (READER EXPERIENCE ≠ READER MODEL); alimenta as crenças que T016/T018 registram, nunca as substitui. |
| `T035_MEMORY_MOTIF_MAP` | Onde uma pista de releitura corresponde a uma crença do leitor, cita o id (`RB-*`) para T018 poder ligar motivo a revisão de crença. |
| `T1{NN}_BRIEF_CHAPTER` | Cita os `EV-*` do capítulo; heat profile e câmera são planejamento de cena (não canon) e nunca resetam um estado que o ledger já registrou. |
| `T2{NN}_WRITE` | Escritores propõem deltas **realizados** (`relationship_delta`, `knowledge_delta`, efeitos de loop) em `canon/CANON_PROPOSALS` — nunca promovem `PLANNED` para `REALIZED` diretamente. |
| `T2{NN}_CANON_UPDATE` | `CANON_GUARDIAN` promove as propostas da wave: `PLANNED` → `REALIZED`, com `evidence_to_reader` real (o que a prosa de fato mostrou). |

## Contrato de referência

`templates/CAUSAL_LEDGER_TEMPLATE.yaml` é o contrato executável — todo campo,
enum e exemplo que existe. Um evento tem, no mínimo: `id`, `status`,
`chapter`, `structural`, `kind`, `actor`, `participants`, `facts`,
`caused_by`. `caused_by` só aceita ids `GT-*`/`EV-*` que resolvem — nunca um
rótulo de gênero, arquétipo ou trope como causa.

`emotional_movement` (intensidade emocional por capítulo) **não vive aqui**:
mora em `book/chapter_architecture.yaml`, porque é plano de capítulo (STORY
PLANNING), não canon — pode mudar livremente sem virar retcon.

## Como validar

```
python scripts/check_causal_ledger.py --runtime . --mode plan
python scripts/check_causal_ledger.py --runtime . --mode realized --baseline canon/snapshots/CAUSAL_LEDGER.WAVE_NN.yaml
python scripts/check_causal_ledger.py --runtime . --mode final --baseline canon/snapshots/CAUSAL_LEDGER.WAVE_NN.yaml --chapter-architecture book/chapter_architecture.yaml
```

O gate correspondente (`GATE_CANON`, cada `GATE_WAVE_n`, `GATE_FULL_MANUSCRIPT`)
já roda isto automaticamente via `validate-gate` — normalmente você não
precisa chamar o script à mão, só ler o relatório quando o gate reprovar.

Achados `HIGH`/`BLOCKER` bloqueiam o gate. O gate de sedução adulta
(participante de sedução/erotismo/intimidade sem idade canônica ≥ 18
confirmada) é sempre `BLOCKER`, em qualquer perfil de execução.

## Diagnóstico (nunca vaza a verdade do motor para o leitor por padrão)

```
python scripts/check_causal_ledger.py --runtime . --why EV-01
python scripts/check_causal_ledger.py --runtime . --relationship CHR-B CHR-A --at-chapter 5
python scripts/check_causal_ledger.py --runtime . --payoff EV-05
python scripts/check_causal_ledger.py --runtime . --knowledge READER --at-chapter 5
python scripts/check_causal_ledger.py --runtime . --beliefs --at-chapter 6
python scripts/check_causal_ledger.py --runtime . --recontextualized --baseline canon/snapshots/CAUSAL_LEDGER.WAVE_NN.yaml
python scripts/check_causal_ledger.py --runtime . --end-state
```

`--beliefs` omite `truth` e `disclosed_by_revision` por padrão — use
`--engine-view` só para depuração interna, nunca para montar um prompt de
escrita ou brief que o leitor possa ver de relance. `THE ENGINE KNOWS
CAUSALITY. THE READER RECEIVES EVIDENCE.`

## Regra de renderização

Se a prosa não conseguir realizar um delta planejado (limite do modelo,
corte de cena, *fade to black*), registre `evidence_to_reader` reduzida ou
devolva o evento para `PLANNED` — nunca reescreva `facts`, `caused_by` ou
`consent` para caber no que foi escrito. Limitação de geração não corrompe
canon.
