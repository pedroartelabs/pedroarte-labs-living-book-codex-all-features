# Character Visual Bible — semente de Narciso

`T039_CHARACTER_VISUAL_BIBLE` produz `images/canon/CHARACTER_VISUAL_BIBLE.md`
a partir desta semente e de `FACE_CANON.seed.md`. Fonte:
`docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md`, seções 14, 17 e 25.3.

## Corpo

1,86 m; longo e magro-atlético, como um nadador que não nada; ombros médios;
pescoço longo; clavículas visíveis só como elegância no Ato I; veias discretas
nos antebraços; pelos naturais de adulto em antebraços e peito; mãos de dedos
longos, nós salientes e unhas curtas.

## Postura e gestos

Imobilidade; peso na perna esquerda; cabeça inclinada cerca de 10° para a
esquerda; toca superfícies com a ponta dos dedos, nunca com a palma; dorso da
mão sobre a boca quando pensa; a partir do Ato II, o polegar percorre a
própria mandíbula; nunca sorri inteiro.

## Figurino

Ato I: lã preta e carvão, camisa de linho marfim, casaco escuro longo, pés
descalços em casa. Ato II: camisa aberta, mangas dobradas, mãos sempre
úmidas. Ato III: a mesma camisa de linho, suja, e um lençol negro sobre os
ombros. Sem logotipos; nenhuma joia além do anel.

## Nudez artística

Só em pranchas herói, de detalhe do corpo ou de reflexo, com justificativa
narrativa ancorada. Enquadramento por costas, ombro, nuca, linha d'água,
sombra ou tecido. Nunca genitália, ato sexual ou pose de conteúdo explícito.
Nenhuma nudez em superfície pública.

## REFLECTION_RULES

O rosto é assimétrico de propósito para que o espelho seja verificável:

| Âncora | Narciso | Reflexo verdadeiro |
|---|---|---|
| canto mais alto da boca | esquerdo | direito |
| pinta sob o olho | direito | esquerdo |
| repartição do cabelo | esquerda | direita |
| cicatriz na palma | esquerda | direita |
| anel | indicador direito | indicador esquerdo |

Estados de reflexo: `NONE`, `TRUE_MIRROR`, `ANOMALOUS_MIRROR` (exatamente uma
âncora não espelhada, ou um estado de declínio mais íntegro que o corpo),
`FRAGMENTED`, `OCCLUDED`, `DOUBLE` (no máximo duas pranchas), `ABSENT_REFLECTION`
(no máximo uma prancha). O rosto do reflexo nunca aparece inteiro e nítido; a
anomalia declarada entra na checagem de continuidade, e anomalia não
declarada é defeito.

## DECAY_TIMELINE

| Estado | Gatilho | Muda | Nunca muda |
|---|---|---|---|
| D0_PRISTINE | inicial | — | âncoras de identidade |
| D1_SLEEPLESS | cena protegida STATUE_BREAKS | olheiras, barba de dois dias, lábio seco | âncoras de identidade |
| D2_FEVER | cena protegida THE_CENTER | cabelo molhado colado, rubor, mãos trêmulas, cicatriz aberta | âncoras de identidade |
| D3_WITHERING | quarta ocorrência compulsiva | pele baça, unhas roídas, camisa suja; perda de luz, não de peso | âncoras de identidade |
| D4_MARBLE | quinta ocorrência compulsiva | palidez acinzentada, imobilidade de estátua, lábios rachados | âncoras de identidade |
| D5_TRACE | cena protegida THE_NAME_AT_DAWN | o corpo sai de quadro: só camisa, lençol, marca na água, anel | — |

Toda transição é exibida a partir do capítulo seguinte ao gatilho. Superfícies
públicas mostram apenas D0.

## Reconhecimento por fragmento

| Recorte | Âncoras mínimas visíveis |
|---|---|
| mão molhada | cicatriz ou anel, dedos longos e nós |
| olho | cor, pinta (lado direito), sobrancelha reta |
| boca | canto esquerdo mais alto |
| ombro ou nuca | cabelo úmido na altura da mandíbula, pescoço longo |
| cabelos sobre a água | preto azulado, ondulação, repartição |
| silhueta | inclinação da cabeça, pescoço longo, peso na perna esquerda |
| reflexo fragmentado | ao menos uma âncora espelhada verificável |

## Protocolo de consulta antes de gerar

1. `check_visual_canon.py --state FIG-NARCISO --at-chapter N`
2. `check_visual_canon.py --state SIG-ESPELHO --at-chapter N`
3. `check_visual_canon.py --exposure`
4. ler as âncoras de FV-NARCISO-01 e as REFLECTION_RULES
5. escolher a referência aprovada compatível com o estado de declínio
6. escrever o brief sem nome de hipótese sobre o reflexo
7. gerar e registrar prompt, modelo, referência e SHA-256
8. FACE_QA e CONTINUITY_QA, conferindo a anomalia declarada contra a observada
