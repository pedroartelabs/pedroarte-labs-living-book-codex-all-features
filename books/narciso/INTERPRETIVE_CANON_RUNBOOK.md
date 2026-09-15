# Runbook — `canon/NARCISO_INTERPRETIVE_CANON.yaml`

Desenho: `docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md`, seções 9, 10, 11, 20, 25 e 29.4.
Este arquivo basta para executar as tarefas; não é preciso ler a SDD.

## O que é

Um canon **de leituras**, não de verdades. Ao lado de `CANON_REGISTRY.yaml` e
`CAUSAL_LEDGER.yaml`, registra para cada evento do ledger:

- quais hipóteses sobre o que olha de volta ele sustenta (`reflection_evidence`);
- a leitura amorosa e a leitura narcisista de cada gesto de Narciso (`love_readings`);
- função, prazer, teto de explicitude e modelo de consentimento das ocorrências
  compulsivas (`desire_occurrences`) e da intimidade do capítulo 18 (`partnered_intimacy`);
- as pistas de releitura (`reread_clues`);
- as revelações não ontológicas (`revelations`): fatos que mudam uma crença do leitor
  sem tocar o que olha de volta nem o amor (a inscrição de Amintas, quem pagou a internação).

## Regra zero — `NO_HIDDEN_ANSWER`

Nenhum arquivo, campo, brief, prompt ou relatório guarda o que o reflexo "é"
nem se Narciso amou. Campos como `truth`, `answer`, `resposta` ou `verdade`
são reprovados. As crenças `RB-LOVE-A`, `RB-LOVE-B` e `RB-RFX-*` no ledger têm
`truth: INCOMPLETE` e `left_open: true` até o fim e nunca são revisadas.

## Dono e protocolo

- Dono exclusivo: `CANON_GUARDIAN`, lock `CANON_WRITE` (mesma governança do registry e do ledger).
- Demais agentes propõem em `canon/CANON_PROPOSALS/`.
- Cada linha tem `event` (id do ledger), `chapter` e `status` (`PLANNED` | `REALIZED`),
  espelhando o evento correspondente.
- Uma linha `REALIZED` é imutável contra o snapshot anterior (`INTERPRETIVE_RETCON`).

## Tarefas

| Tarefa | O que faz |
|---|---|
| `T018N_INTERPRETIVE_CANON` | Consolida `book/seeds/INTERPRETIVE_CANON.seed.yaml` em `canon/NARCISO_INTERPRETIVE_CANON.yaml`, criando no ledger os eventos citados (`kind` com `REFLECTION_EVIDENCE`, `LOVE_EVIDENCE`, `COMPULSION_OCCURRENCE`, `INTIMACY`), as crenças abertas e, no registry, `UNK-NAR-001` (`MUST_REMAIN_UNKNOWN`) e `PRO-NAR-001..006`. |
| `T019N_AMBIGUITY_REVIEW` | `NARCISSUS_AMBIGUITY_GUARDIAN` revisa e escreve `reviews/NARCISO_AMBIGUITY_REVIEW.md`. |
| `T021N_INTERPRETIVE_SNAPSHOT` | Mecânica: grava o snapshot `WAVE_00`. |
| `T2NN_CANON_UPDATE` | Além do ledger, promove as linhas da wave para `REALIZED`, com o mesmo status dos eventos, e grava `text_anchor` nas pistas de texto cuja pista ou gatilho caem na wave (ver "Pistas de texto"). |
| `T2NNN_INTERPRETIVE_SNAPSHOT` | Mecânica: grava o snapshot da wave (`WAVE_01`..`WAVE_06`). |

## Eventos do ledger

- O reflexo **nunca** é `character` nem `participant`. Eventos com ele têm
  `participants: [CHR-NARCISO]` (e testemunhas humanas), e `facts` descrevem só
  percepção.
- `LOVE_EVIDENCE`: sempre com `relationship_delta`.
- `COMPULSION_OCCURRENCE`: `participants: [CHR-NARCISO]`, `consent.canonical: CONSENSUAL` e
  `ability_to_refuse`/`boundary_state` iguais a `consent_model` (decisão OQ-N5):
  DSR-1 e DSR-2 `FULL/RESPECTED`; DSR-3 `FULL/PUSHED`; DSR-4 e DSR-5 `CONSTRAINED/PUSHED`;
  DSR-6 `CONSTRAINED/VIOLATED`.
- `INTIMACY` (cap. 18): `CONSENSUAL`, `FULL`, `NEGOTIATED`, participantes Narciso e Eco.

- `REVELATION` (`REV-*`): `beliefs.revises: [<crença>]`. A crença existe em `beliefs[]` com
  `about` = eventos de `formed_by` (capítulos anteriores) e `disclosed_by_revision` = `discloses`;
  a verdade divulgada está em `caused_by` de ao menos uma dessas cenas e nunca tem
  `reader_access: NEVER`. Crenças `RB-RFX-*` e `RB-LOVE-*` nunca são revisadas.

## Pistas de texto

Quando a wave escreve a pista ou o gatilho de uma pista `channel: TEXT` ancorada em
`TURN:` ou `SCENE:`, o `CANON_UPDATE` grava no lado correspondente:

```yaml
clue: {anchor: "TURN:13", text_anchor: 'TEXT:13:"trecho copiado literalmente da prosa"'}
```

O capítulo do `text_anchor` é o da âncora planejada (ou um dos capítulos da cena).
No modo `final` o trecho precisa existir literalmente no manuscrito congelado
(`REREAD_ANCHOR_MISSING`). Âncora gravada é imutável; se a revisão final mudar a frase,
a pista volta para revisão — nunca se reescreve a âncora para caber no texto.

## Final (modo `final`, `GATE_FULL_MANUSCRIPT`)

- Toda linha do canon está `REALIZED` (`FINAL_ROW_UNREALIZED`).
- O capítulo 33 tem exatamente uma evidência nova — `final_evidence` — e nenhum evento
  que revise crença (`FINAL_EVIDENCE_COUNT`, `EXPLANATORY_CLOSURE`).
- Nada de explicação no 33 (léxico `explanatory_closure`) nem confirmação de morte ou
  sobrevivência de Narciso do 31 ao 33 (léxico `fate_confirmation`, `FATE_RESOLVED`).
- A baseline é `WAVE_06`: nada realizado muda depois dela.

## Como validar

```
python book/validators/validate_narciso.py --runtime . --mode plan
python book/validators/validate_narciso.py --runtime . --mode wave --through-chapter 6 --baseline canon/snapshots/NARCISO_INTERPRETIVE_CANON.WAVE_00.yaml
python book/validators/validate_narciso.py --runtime . --mode final --baseline canon/snapshots/NARCISO_INTERPRETIVE_CANON.WAVE_06.yaml
python book/validators/validate_narciso.py --runtime . --snapshot-as WAVE_01
```

Os gates `GATE_CANON`, `GATE_LIVING_BOOK`, `GATE_WAVE_1..6` e `GATE_FULL_MANUSCRIPT`
rodam isto via `validate-gate`. Achados `HIGH`/`BLOCKER` bloqueiam.

## Regra de renderização

Se a prosa não sustentar uma leitura planejada, devolva a linha para `PLANNED`
e a wave para revisão — nunca reescreva `support`, `love`, `narcissism` ou
`consent_model` de uma linha `REALIZED` para caber no que foi escrito.
