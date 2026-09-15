# Runbook — `canon/VISUAL_NARRATIVE_CANON.yaml`

Este runtime usa a capability `BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM`
(`features.visual_narrative.enabled: true` no `BOOK_SPEC.yaml` deste livro).
Veja `docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md` no repositório
do motor para o desenho completo — este arquivo basta para executar a
tarefa, não é preciso ler o SDD.

## O que é

Um terceiro arquivo de canon, ao lado de `canon/CANON_REGISTRY.yaml` e (se
a capability `causal_ledger` também estiver ligada) `canon/CAUSAL_LEDGER.yaml`,
que registra a **identidade visual narrativa** do livro: símbolos, sigilos
de capítulo, artefatos narrativos, composições por superfície e intenções de
acabamento — sempre justificados contra o texto (Regra do Chekhov Visual),
nunca decoração solta. A identidade visual **permanente** da autora vive em
`author/AUTHOR_VISUAL_DNA.v<N>.yaml` (cópia somente-leitura de
`authors/<author_id>/` no repositório do motor); este runtime nunca a edita.

## Dono e protocolo

- **Dono exclusivo:** `VISUAL_DIRECTOR`, sob o lock `VISUAL_CANON_WRITE`.
- Um elemento nasce `status: PLANNED` e só é promovido quando a arte que ele
  descreve de fato existe.
- Um snapshot `PLAN` (`canon/snapshots/VISUAL_NARRATIVE_CANON.PLAN.yaml`,
  gravado por `T044_VISUAL_CANON_SNAPSHOT`) e um snapshot `FREEZE`
  (`canon/snapshots/VISUAL_NARRATIVE_CANON.FREEZE.yaml`, gravado por
  `T312_VISUAL_CANON_SNAPSHOT`) são os dois pontos de congelamento contra os
  quais o `--baseline` das próximas validações é comparado (ST-08 /
  `VISUAL_RETCON` — um elemento cuja `meaning` muda depois de congelado é um
  achado, não um ajuste silencioso).

## Onde cada tarefa contribui

| Tarefa | O que faz |
|---|---|
| `T042_VISUAL_DISCOVERY` | Levanta candidatos visuais (`VISUAL_CANDIDATES`) a partir do canon já existente e do `AUTHOR_VISUAL_DNA`. |
| `T043_VISUAL_NARRATIVE_CANON` | `VISUAL_DIRECTOR` decide e escreve o canon visual: elementos, composições, `finish_intents`. |
| `T044_VISUAL_CANON_SNAPSHOT` | Congela o snapshot `PLAN` (mecânica, `check_visual_canon.py --snapshot-as PLAN`). |
| `T1{NN}_BRIEF_CHAPTER` | Cita os elementos (`SIG-*`, `ART-*`) e o estado de progressão vigentes no capítulo, quando o canon já os declara. |
| `T311`/`T312` (`VISUAL_CANON_SNAPSHOT`) | Revalida o canon contra o manuscrito completo (`--mode realized`) e congela o snapshot `FREEZE`. |
| `T602_ORIGINALITY_AUDIT` | Inclui os elementos visuais no crivo de originalidade/IP (seção 26.4 da SDD — nenhum símbolo pode reproduzir marca ou obra de terceiros). |
| `T698_EDITION_PLAN` | Projeta o `EDITION_PLAN` (elegibilidade/fallback de cada item de `finish_intents`) para **todo** alvo em `edition_targets` declarado em `BOOK_SPEC.yaml` — `check_visual_canon.py --edition-plan-all`. |
| `T699`/`T700`/`T702`/`T703` | Consomem o `EDITION_PLAN`/`COVER_GEOMETRY` ao montar o pacote KDP (nenhuma mudança de contrato — só leem os arquivos que T698/T707 já escreveram). |
| `T707_PRINT_GEOMETRY` | Projeta `COVER_GEOMETRY` (medidas físicas de capa) para todo alvo impresso de `edition_targets` — `check_visual_canon.py --print-geometry-all`. |
| `T800`/`T801` | Renderizam a capa/artefatos finais; o Thumbnail Gate (`--mode assets`) roda sobre o JPEG real que estas tarefas produzem. |

## Contrato de referência

`templates/VISUAL_NARRATIVE_CANON_TEMPLATE.yaml` e
`author/AUTHOR_VISUAL_DNA.v<N>.yaml` são os contratos executáveis — todo
campo, enum e exemplo que existe. Um elemento tem, no mínimo: `id`, `class`,
`meaning`, `functions` (cada uma com `anchors` que resolvem de verdade —
`LEDGER:`, `SCENE:`, `TURN:`, `CHAPTER_FIELD:`, `TEXT:`, `CANON:`, `DOC:`,
`RULE:`), `prominence`, `exposure.spoiler_level`, `approval.policy`,
`status`.

## Como validar

```
python scripts/check_visual_canon.py --runtime . --mode plan
python scripts/check_visual_canon.py --runtime . --mode realized --baseline canon/snapshots/VISUAL_NARRATIVE_CANON.PLAN.yaml
python scripts/check_visual_canon.py --runtime . --validate-editions
python scripts/check_visual_canon.py --runtime . --mode assets --cover-image media/outputs/cover/BOOK_COVER_KDP.jpg
```

Os gates correspondentes (`GATE_LIVING_BOOK`, `GATE_FULL_MANUSCRIPT`,
`GATE_KDP` ou `GATE_DELIVERY`, `GATE_MEDIA_ASSETS`) já rodam isto
automaticamente via `validate-gate` — normalmente você não precisa chamar o
script à mão, só ler o relatório quando o gate reprovar. Achados
`HIGH`/`BLOCKER` bloqueiam o gate.

## Diagnóstico

```
python scripts/check_visual_canon.py --runtime . --why SYM-XXX
python scripts/check_visual_canon.py --runtime . --evidence termo1 termo2
python scripts/check_visual_canon.py --runtime . --state SIG-XXX --at-chapter 5
python scripts/check_visual_canon.py --runtime . --end-state
python scripts/check_visual_canon.py --runtime . --timeline
python scripts/check_visual_canon.py --runtime . --exposure
python scripts/check_visual_canon.py --runtime . --target kdp_hardcover --edition-plan
python scripts/check_visual_canon.py --runtime . --target kdp_hardcover --resolve FI-XXX
python scripts/check_visual_canon.py --runtime . --target kdp_hardcover --geometry
python scripts/check_visual_canon.py --runtime . --target collector --production-manifest
```

## Regra de renderização

Se a arte final não conseguir realizar um elemento planejado (limite do
gerador, corte de composição, restrição de acabamento na gráfica), registre
o elemento de volta em `status: PLANNED` ou ajuste `finish_intents.fallbacks`
— nunca reescreva `meaning` ou os `anchors` de uma função para caber no que
foi produzido. Limitação de geração não corrompe canon.
