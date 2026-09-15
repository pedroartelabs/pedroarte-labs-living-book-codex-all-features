# Face Canon — semente de Narciso

Estrutura de `engine/templates/FACE_CANON_TEMPLATE.md`. `T038_FACE_CANON`
(`FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT`, lock `FACE_CANON_WRITE`) produz
`images/canon/FACE_CANON.md` a partir desta semente. Fonte:
`docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md`, seção 14.

## Propósito

Manter Narciso e Eco imediatamente reconhecíveis entre capa, pranchas e
fragmentos, sem deriva de beleza, de idade ou de identidade. São rostos
ficcionais e não imitam pessoa real ou figura pública.

Veto próprio da obra: nenhum rosto carrega a resposta sobre o que olha de
volta. O reflexo nunca aparece com rosto inteiro e nítido.

## Condições de referência

Cabeça e ombros; perspectiva equivalente a 85–105 mm; luz lateral suave;
rosto relaxado, boca fechada; frontal, três-quartos esquerdo e perfil direito;
textura de pele real; sem filtro de beleza.

Uso operacional: toda imagem com Narciso é gerada com
`scripts/generate_image.py --reference <referência aprovada>`; correções
pontuais usam `--edit`.

---

## Narciso Céfiso — código de identidade FV-NARCISO-01

### Identidade estável

- aparência de idade: 27 anos; ossatura adulta; linhas finas no canto externo dos olhos; nunca rejuvenescido;
- pele: oliva-pálida, subtom frio, poros e textura reais;
- formato do rosto: oval longo; maçãs altas sem angulosidade de vilão;
- sobrancelhas: retas e baixas, densidade média; a esquerda levemente mais alta;
- olhos: cinza-esverdeado escuro, cor de água parada, anel limbal escuro, pálpebra superior pesada;
- nariz: dorso longo e reto com pequena saliência, ponta estreita;
- boca: lábios de espessura média; canto esquerdo mais alto (meio sorriso sempre à esquerda);
- marca: pinta pequena e escura sob o olho direito;
- mandíbula: definida, não quadrada; barba feita no Ato I;
- cabelo: preto com reflexo castanho-azulado, ondulado, na altura da mandíbula, repartido à esquerda;
- mãos: cicatriz fina e clara, diagonal, na palma esquerda;
- anel: aro de ouro envelhecido no indicador direito.

### Faixa de expressão

Atenção demorada e imóvel. Desejo estreita o olhar e para o movimento das
mãos; não o transforma em sorriso aberto. Medo aparece como rigidez da
mandíbula, não como olhos arregalados. O definhamento apaga a luz da pele e a
postura; nunca muda a anatomia do rosto.

### Âncoras de continuidade

1. pinta sob o olho direito;
2. canto esquerdo da boca mais alto;
3. cabelo repartido à esquerda;
4. cicatriz na palma esquerda;
5. anel no indicador direito;
6. olhos cinza-esverdeados escuros.

### Rejeitar

Rosto simétrico de modelo; mandíbula quadrada hipermasculina; pele lisa sem
textura; olhos azuis ou verdes claros; pinta ausente ou migrada sem
declaração; cabelo curto ou liso; corpo musculoso de academia; aparência
abaixo de 25 anos; sorriso aberto; beleza aumentada nos estados de declínio;
corpo mais magro apresentado como mais belo; semelhança com pessoa real.

---

## Elisa "Eco" Varela — código de identidade FV-ECO-01

31 anos; pele morena-clara com sardas discretas no nariz; rosto de maçãs
largas; olhos castanho-escuros atentos; sobrancelhas grossas e naturais;
cabelo castanho-escuro preso de forma prática, com fios soltos na nuca;
pequena marca de fone na cartilagem da orelha direita. Expressão padrão de
escuta. Nunca aparece como silhueta decorativa ao lado de Narciso.

---

## Controles de deriva

Rejeitar a imagem se um rosto recorrente mudar valor ou subtom de pele além
do que a luz explica, cor dos olhos, formato do rosto, idade aparente,
repartição do cabelo ou qualquer âncora de continuidade. Uma anomalia de
espelho só é aceita quando declarada na composição.

## Pontuação de QA

Identidade estrutural, continuidade de idade e de pele/cabelo: mínimo 9/10.
Ausência de codificação juvenil e de glamour do definhamento: aprovação
obrigatória. Falha de identidade é `FACE_IDENTITY_FAILURE`.
