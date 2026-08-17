# Face Canon — TEMPLATE

> **Como usar.** Copie para `/images/canon/FACE_CANON.md` do runtime e preencha.
> Este template é a estrutura extraída de um FACE_CANON real que sustentou 24
> imagens de capítulo com identidade facial preservada — inclusive depois de
> uma deriva detectada e corrigida no meio da produção. A estrutura não é
> decorativa: cada seção existe porque a ausência dela produziu uma reprovação
> concreta em `FACE_QA`.
>
> Apague estas instruções ao preencher. Substitua tudo em `<colchetes>`.
>
> **Por que isto é caro de improvisar.** O `.toml` do
> `FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT` tem poucas linhas de instrução. O
> documento que ele precisa produzir tem centenas. Sem um template, cada livro
> redescobre do zero que precisa de código de identidade, âncoras de
> continuidade e lista de rejeição — e um canon vago gera candidatos rejeitados,
> que custam mais que o tempo de escrever o canon direito.

Task: `T038_FACE_CANON`
Owner: `FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT`
Lock: `FACE_CANON_WRITE`

## Propósito

Manter identidades recorrentes imediatamente reconhecíveis entre imagens de
capítulo, sem deriva de beleza, de idade, de etnia ou de emoção. São rostos
ficcionais e não podem imitar pessoa real ou figura pública.

`<Regra de veto próprio da obra — por exemplo: nenhum rosto carrega informação
sobrenatural; personagens X, Y e Z nunca são ligados por brilho, expressão
espelhada, marca transferida ou olhar místico.>`

## Condições de referência

Toda personagem recorrente exige uma referência neutra de identidade:

- cabeça e ombros;
- perspectiva de retrato equivalente a 85–105 mm;
- luz natural suave e neutra;
- sem gradação de cor dramática;
- rosto relaxado, boca fechada, sem sorriso forçado;
- frontal, três-quartos esquerdo e perfil direito;
- textura de pele e marcas de idade naturais;
- sem filtro de beleza nem nitidez excessiva.

O canon textual prevalece quando um prompt de geração conflitar com ele.

**Uso operacional da referência.** Aprovada a referência, gere as imagens de
capítulo com `python scripts/generate_image.py --reference <arquivo aprovado>`.
Redescrever um rosto por palavras não converge entre capítulos; ancorar numa
imagem aprovada converge. Para consertar um detalhe pontual (um letreiro
legível, um vazamento de luz), use `--edit` em vez de regerar: além de mais
barato, não reintroduz problemas já resolvidos no resto da imagem.

---

# `<Família ou grupo 1>`

`<Se houver parentesco: descreva a semelhança como restrita — traços
compartilhados E traços que distinguem. Sem isso, o gerador produz versões
envelhecidas do mesmo modelo.>`

- `<traço compartilhado 1>`;
- `<traço compartilhado 2>`;
- proporções, bocas, queixos e cabelos diferentes entre si.

## `<Nome completo>` — código de identidade `<FV-NOME-01>`

### Identidade estável

- aparência de idade: `<N>`, nunca rejuvenescida;
- pele: `<tom, subtom, textura, marcas de sol/trabalho>`;
- formato do rosto: `<...>`;
- testa: `<...>`;
- sobrancelhas: `<forma, densidade, assimetria>`;
- olhos: `<cor, formato, espaçamento, pálpebras>`;
- nariz: `<dorso, largura, ponta, narinas>`;
- boca: `<largura, proporção dos lábios, assimetria de movimento>`;
- mandíbula/queixo: `<...>`;
- cabelo: `<cor, textura, corte, grisalhos e onde>`;
- `<objeto ou detalhe estável: óculos, aliança, cicatriz de história comum>`.

### Faixa de expressão

`<Descreva o estado de atenção padrão e o que a pressão faz ao rosto. Este é o
campo que impede a personagem de virar arquétipo: diga o que a emoção NÃO pode
transformar. Exemplo: escuta genuína suaviza a mandíbula e para o movimento dos
olhos; não a transforma numa figura sorridente de rosto aberto.>`

### Âncoras de continuidade

Use pelo menos quatro em todo rosto visível:

1. `<âncora 1>`;
2. `<âncora 2>`;
3. `<âncora 3>`;
4. `<âncora 4>`;
5. `<âncora 5>`;
6. `<âncora 6>`.

### Rejeitar

`<Lista calibrada contra os vieses conhecidos do gerador para este tipo de
cena. Genérico não serve: "não fazer feio" não é critério. Exemplos do que
funciona — mecha grisalha glamorosa com precisão de salão; rosto anguloso de
vilão; pele lisa rejuvenescida; cor de olhos trocada; ternura materna
representada por sorriso permanente; luto representado por nova anatomia
facial.>`

---

# Identidades de uso limitado

## `<Nome>` — código `<FV-NOME-01>`

`<Parágrafo curto: idade, pele, traços marcantes, e a restrição ética ou
narrativa específica. Para recém-nascidos e crianças pequenas, declare
explicitamente que a semelhança familiar não pode ser precisa o bastante para
funcionar como prova de trama, e proíba olhar adultizado, marca simbólica ou
pose significativa.>`

---

# Matriz de semelhança familiar

| Traço | `<Pessoa A>` | `<Pessoa B>` | `<Pessoa C>` |
|---|---|---|---|
| família da sobrancelha | | | |
| família do nariz | | | |
| distinção dos olhos | | | |
| distinção da mandíbula | | | |
| distinção do cabelo | | | |
| textura de idade | | | |

# Controles de deriva entre capítulos

Rejeitar a imagem se um rosto recorrente mudar:

- valor ou subtom de pele além do que a iluminação explica;
- cor dos olhos;
- formato do rosto, arquitetura do nariz ou espaçamento dos olhos;
- idade além do que o cansaço ou a doença da cena permitem;
- textura ou corte estável de cabelo sem causa narrativa;
- qualquer âncora de continuidade;
- semelhança familiar a ponto de virar clonagem do mesmo modelo.

Expressão, hidratação, sono, esforço e luz podem alterar a aparência — nunca
a identidade.

# Pontuação de QA

Cada rosto recorrente precisa atingir:

- identidade estrutural: mínimo 9/10;
- continuidade de idade: mínimo 9/10;
- continuidade de pele/cabelo: mínimo 9/10;
- expressão adequada à cena: mínimo 8/10;
- ausência de codificação sobrenatural: aprovação obrigatória;
- ausência de deriva de embelezamento ou body horror: aprovação obrigatória.

Falha em identidade estrutural, no estatuto humano ordinário de uma criança ou
no veto de causalidade sobrenatural é `FACE_IDENTITY_FAILURE`: rejeita-se a
imagem, não se racionaliza o resultado.

# Registro de correção

Quando uma imagem for reprovada e regerada, registre em
`/images/chapters/chapter_NN/GENERATION_REPORT.md`: o que falhou, qual
referência foi usada na correção, e se a correção foi regeneração ancorada
(`--reference`) ou edição pontual (`--edit`). Esse histórico é o que permite
distinguir uma deriva isolada de um problema sistemático do canon.
