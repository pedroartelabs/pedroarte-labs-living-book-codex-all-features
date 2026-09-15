# Pesquisa de gráfica — edição de colecionador de NARCISO

Desenho: `docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md`, seções 21–23 e Slice 7.
Isto é um roteiro para uma pessoa conduzir. O motor não pesquisa, não escolhe e
não contata fornecedores; ele só lê `layout/PRINTER_PROFILE.yaml` quando alguém
o preenche com evidência. Enquanto isso não acontece, todo acabamento do
collector degrada para simulação ou omissão — e nenhum texto promete o contrário.

## Efeitos a confirmar

| Efeito (`EDITION_CAPABILITIES`) | Onde no livro | Acabamento | Se não houver |
|---|---|---|---|
| `MIRROR_BOARD` ou `METALLIZED_PAPER` | capa nua, poça do espelho (`FI-MIRROR-POOL`) | área ≤ 6% da face, baixo contraste, devolve um reflexo desfocado | foil → impressão metálica simulada |
| `METALLIC_FOIL` | título (`FI-TITLE`) | ouro envelhecido | impressão metálica simulada |
| `SPOT_UV` | água da capa (`FI-WATER`) | brilho localizado sobre fosco | simulação de contraste |
| `DEBOSS` | rachadura na capa nua (`FI-CRACK`) | baixo-relevo sem tinta | relevo tonal simulado |
| `BLIND_EMBOSS` | narciso na lombada nua (`FI-FLOWER`) | relevo cego, marfim | omitir |
| `SPRAYED_EDGE` / `STENCILED_EDGE` | borda frontal (`FI-EDGE`) | preto com ondulação | omitir |
| `RIBBON_MARKER` | fita (`FI-RIBBON`) | fita negra fina | omitir |
| `SLIPCASE` | caixa (`FI-SLIPCASE`) | caixa negra com janela de água | omitir |
| `DUST_JACKET`, `PRINTED_ENDPAPER` | sobrecapa e guardas | sobrecapa com a capa pública; guardas de lençóis e espelhos | sem collector |
| `INSERT_CARD` | cards lacrados (inscrição de Amintas, folha de contato de Íris) | só com artefato narrativo aprovado | omitir |

## Evidência exigida

Para cada efeito listado em `confirmed_effects`, `evidence.<EFEITO>` registra:

- `vendor` — nome da gráfica;
- `quote_ref` — referência do orçamento ou proposta;
- `date` — data da confirmação;
- `sample_approved: true` — prova física aprovada por uma pessoa.

Perguntas para cada gráfica: tiragem mínima; prazo; tolerância de registro entre a
arte e a máscara (espelho, foil, relevo); legibilidade do espelho sob luz comum;
durabilidade do espelho ao manuseio e ao risco; compatibilidade entre sobrecapa e
capa nua; sangria e espessura por página (`bleed_in`, `spine_in_per_page`);
formatos de arquivo das máscaras (vetor ou 1 bit, 100% K); custo por exemplar.

## Produção

Numeração, assinatura e tiragem limitada não são capacidade de impressão: são
decisão comercial e logística (OQ-N8). Só depois dela `production.numbered`,
`production.signed` ou `production.limited` viram `true`, com `decided_by`
preenchido. Até lá nenhum texto — nem do collector — promete essas coisas.
Fragrância fica fora (SDD 21.5).

## Decisão humana

- Escolher a gráfica e aprovar a prova física de cada efeito confirmado.
- Aprovar `APR-FI-MIRROR` (TRAP-01) olhando a prova: o espelho é sussurro, nunca parque de diversão.
- Decidir OQ-N7 (cor do miolo e quantidade de pranchas) e OQ-N8 (tiragem, numeração, assinatura).
- Só então copiar o modelo `seeds/PRINTER_PROFILE.template.yaml` para `layout/PRINTER_PROFILE.yaml`.
