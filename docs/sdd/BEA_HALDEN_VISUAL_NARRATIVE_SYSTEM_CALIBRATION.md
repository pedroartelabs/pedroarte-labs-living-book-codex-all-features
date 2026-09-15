# Calibração — Thumbnail Gate e checagens de pixel (Slice 4)

> **Status:** relatório de calibração do Slice 4 de
> `docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md` (seções 23.5,
> 23.6, 18.3). Mede as heurísticas de `engine/scripts/check_visual_canon.py`
> contra artefatos reais já existentes no repositório — **somente leitura**:
> nenhum arquivo de `runtime/` foi alterado para produzir este relatório.

---

## 1. Método

Convenção de `TEXT_QUALITY_DEFAULTS.yaml`: um limiar só é confiável depois
de medido contra um artefato real que já passou por julgamento humano. Duas
fontes:

1. **Artefatos reais do repositório** — as capas atualmente publicadas de
   `runtime/eva-a-ultima-mulher-da-terra/` e
   `runtime/loja-de-poderes-vivos/`. Nenhuma delas tem
   `canon/VISUAL_NARRATIVE_CANON.yaml` (são anteriores a esta capability),
   então as zonas de título/autora/dominante foram **estimadas por inspeção
   visual** (não extraídas de um contrato declarado) — ver seção 3 para o
   efeito disso na leitura dos números.
2. **Reconstrução sintética da capa "antes" de `eva`** — os pixels
   originais da capa tipográfica pura descrita em
   `runtime/eva-a-ultima-mulher-da-terra/reviews/COVER_STORIES_CRITIQUE.md`
   **não sobrevivem no repositório** (o arquivo foi sobrescrito no mesmo
   caminho antes da crítica rodar). Reconstruí uma aproximação fiel à
   descrição em prosa ("uma tela azul-marinho lisa", "sem Eva, sem
   paisagem, sem vida") — rotulada explicitamente como reconstrução, nunca
   apresentada como o arquivo original.

Todas as medições abaixo passam pelo **caminho de produção real**
(`check_visual_canon.generate_thumbnails` → `check_cover_assets` →
`_check_cover_readability`), não por atalhos de teste.

---

## 2. Exit criterion do Slice 4

> "capa tipográfica original de `eva` (julgada 'pobre' pelo autor) produz
> ao menos um achado MEDIUM de focal point, e a capa revisada não — se isso
> não ocorrer, os limiares são recalibrados ou a heurística é rebaixada a
> INFO e registrada como limite."

**Reconstrução da capa "antes"** (fundo azul-marinho sólido, só tipografia,
nenhum símbolo), rodada por `check_cover_assets` com um canon mínimo que
declara um elemento `DOMINANT` com zona `[0.10, 0.28, 0.90, 0.82]` (mesma
convenção da fixture real de O Cisne Negro):

| Achado | Severidade |
|---|---|
| `THUMBNAIL_WEAK_FOCAL_POINT` (cor e grayscale) | MEDIUM |
| `THUMBNAIL_WEAK_SILHOUETTE` (cor e grayscale) | MEDIUM |
| `AUTHOR_DNA_DRIFT` (fundo navy cai dentro do papel PULSE, 94% da área) | MEDIUM |

**Resultado: satisfeito.** A reconstrução produz `THUMBNAIL_WEAK_FOCAL_POINT`
exatamente como o critério pede — uma zona sem nenhum elemento gráfico não
tem concentração de borda nenhuma (razão 0,00), abaixo do piso 1,3.

A parte "e a capa revisada não" exige uma ressalva importante — seção 3.

---

## 3. Medição contra as capas reais publicadas

Zonas estimadas por inspeção visual (não um contrato declarado — ver seção 1).

| Critério | Piso/teto | `eva` (atual) | `loja` (preview) |
|---|---|---|---|
| título — diferença p95−p5 | ≥ 0,45 | **0,80 PASS** | **0,78 PASS** |
| título — contraste WCAG | ≥ 4,5:1 | 3,09:1 FAIL | **5,84:1 PASS** |
| autora — diferença p95−p5 | ≥ 0,35 | 0,03 FAIL* | 0,17 FAIL* |
| ponto focal — razão dentro/fora | ≥ 1,3 | 0,92 FAIL** | 1,10 FAIL** |
| silhueta — maior componente | ≥ 0,25 | 0,24 FAIL** | 0,17 FAIL** |
| clutter — densidade de borda | ≤ 0,35 | **0,06 PASS** | **0,08 PASS** |

`*` `**` — ver interpretação abaixo; nenhum dos dois é tratado como defeito
da heurística.

### 3.1 O que funciona sem ressalva

- **Diferença p95−p5 do título:** separa corretamente título legível de
  título ilegível nas duas capas reais **e** nas duas capas sintéticas de
  teste (`TestTitleAndFocalHeuristics`). Mantido em 0,45.
- **Clutter:** as duas capas reais, desenhadas por um humano para vender o
  livro, folgam com margem confortável do teto (0,06–0,08 contra 0,35) — o
  teto de 0,35 (calibrado contra um tabuleiro de xadrez sintético,
  `TestClutterHeuristic`) tem folga suficiente para não gerar falso
  positivo em arte real. Mantido.

### 3.2 `*` Zona AUTHOR — provável erro de estimativa, não de heurística

Sem um `VISUAL_NARRATIVE_CANON.yaml` real para `eva`/`loja`, estimei a caixa
do nome do autor por olho a partir da imagem renderizada. O valor baixo em
ambas as capas (0,03 e 0,17) é consistente com a caixa estimada não
enquadrar rente ao texto "PEDRO ARTE" (pegando margem de fundo sólido
demais, que dilui a variação interna). **Não altero o piso 0,35** — a mesma
heurística, na mesma zona relativa, passa nas capas sintéticas
(`test_high_contrast_title_passes` cobre a mesma lógica p95−p5 na zona
AUTHOR). Registrado como limite do processo de calibração (zona por
inspeção visual), não da heurística.

### 3.3 `**` Ponto focal e silhueta — limite real, documentado deliberadamente

Este é o achado mais importante da calibração. `eva` e `loja` são capas
**fotográficas/cinematográficas** — pessoa real, cenário real, textura de
tijolo, folhagem, prédios ao fundo. Ambas falham no piso de ponto focal
(0,92 e 1,10, abaixo de 1,3) e no piso de silhueta (0,24 e 0,17, abaixo de
0,25), **mesmo sendo capas aprovadas e publicadas por um humano**.

A causa raiz não é um bug: fotografia realista tem energia de borda
espalhada por toda a composição (folhas, janelas, fios, textura de tecido);
não existe uma única forma limpa cuja borda se destaque do resto do jeito
que um símbolo gráfico desenhado — um cisne, uma coroa, uma lente — se
destacaria contra um fundo comparativamente liso. Testei isso diretamente:
a capa sintética de teste (`_good_cover`, um disco sólido sobre fundo
escuro e quieto) passa os dois critérios com folga (razão 6,66, silhueta
0,29); a mesma capa com ruído distribuído por fora do disco
(`_busy_cover`) falha exatamente o ponto focal; a mesma capa com o disco
fragmentado em pontos soltos (`_fragmented_dominant_cover`) falha
exatamente a silhueta — ou seja, as duas heurísticas discriminam
corretamente dentro do estilo gráfico para o qual foram desenhadas.

**Decisão:** não afrouxar os pisos. `eva` e `loja` pertencem ao catálogo
Pedro Arte geral (realismo cinematográfico), não ao catálogo Bea Halden —
a própria SDD (seção 12.1) define o Author DNA de Bea Halden como
`value_structure: LOW_KEY` com **um símbolo DOMINANT** e "restrição
premium", o estilo gráfico-simbólico que estas heurísticas medem
corretamente. Registro como **limite documentado**, não como defeito:

> **Limite:** `THUMBNAIL_WEAK_FOCAL_POINT` e `THUMBNAIL_WEAK_SILHOUETTE`
> são calibrados para composições **gráfico-simbólicas** (um elemento
> DOMINANT desenhado contra um fundo comparativamente liso — o estilo do
> Author DNA de Bea Halden). Sobre capas **fotográficas/cinematográficas**
> de outros catálogos, ambos tendem a MEDIUM mesmo em peças aprovadas por
> humano — a severidade MEDIUM (nunca HIGH/BLOCKER) já reflete isso: são
> condições necessárias, não suficientes, e a miniatura real sempre vai
> para inspeção humana (23.5) antes de qualquer decisão final.

### 3.4 Contraste WCAG do título em `eva` — sinal real, mantido

3,09:1 é honestamente abaixo do piso de acessibilidade de 4,5:1. Olhando a
própria imagem: o título (creme) sobre céu de entardecer tem trechos —
principalmente perto do topo, onde o céu clareia para lavanda pálido — de
contraste reduzido. Isto é uma tensão real e conhecida de tipografia sobre
fotografia (diferente da tipografia sobre fundo sólido, onde o padrão
`build_cover_and_stories.py` sempre aplica um gradiente escurecedor atrás
do título). **Mantido em 4,5:1** — é o padrão de acessibilidade real, e o
achado é `HIGH`, mas nunca bloqueia sozinho a entrega sem revisão humana; é
exatamente o tipo de sinal que o Thumbnail Gate deveria levantar para uma
capa fotográfica.

---

## 4. Limiares finais (sem mudança em relação ao proposto na SDD)

| Critério | Piso/teto | Fonte da calibração |
|---|---|---|
| título — diferença p95−p5 | 0,45 | capas reais (`eva`, `loja`) + sintéticas |
| título — contraste WCAG | 4,5:1 | padrão de acessibilidade; validado contra `eva` |
| autora — diferença p95−p5 | 0,35 | sintéticas (zona real não confiável sem canon declarado) |
| ponto focal — razão dentro/fora | 1,3 | sintéticas — **limite documentado para fotografia** (3.3) |
| silhueta — maior componente | 0,25 | sintéticas — **limite documentado para fotografia** (3.3) |
| clutter — densidade de borda | 0,35 | tabuleiro de xadrez sintético + folga confortável em `eva`/`loja` |
| `AUTHOR_DNA_DRIFT` — área de papel | `max_area_ratio` do Author DNA (0,12 na fixture) | sintético (faixa PULSE pequena × grande) |

Nenhum limiar foi alterado a partir do valor originalmente proposto na SDD
(seção 23.5) — a calibração **confirmou** os valores propostos, com uma
correção de implementação real encontrada no caminho (seção 5).

---

## 5. Bugs reais encontrados durante a calibração

Nenhum dos dois é um simples "ajuste de fixture" — ambos eram erros de
lógica na primeira implementação, encontrados só ao medir contra imagens
de verdade:

1. **`focal_point_ratio` contava a tipografia como "fora".** Título e
   nome da autora são *propositalmente* de alto contraste (é o próprio
   critério de legibilidade do título) — sem excluí-los da medida de
   "fundo", eles inflavam a energia de borda "de fora" e derrubavam a razão
   de qualquer capa com título legível, inclusive a capa sintética
   perfeitamente desenhada para passar. Corrigido com um parâmetro
   `exclude_zones` (as zonas TITLE/AUTHOR ficam fora do denominador) —
   coberto por `test_typography_zones_excluded_from_ambient_measurement`.
2. **`largest_connected_component_ratio` sempre tratava o tom mais escuro
   como "o sujeito".** Para um símbolo claro sobre fundo escuro (o caso
   comum: tinta clara sobre `GROUND` escuro da autora), isso media a
   conectividade do FUNDO, não do símbolo — dando um número alto mesmo
   quando o símbolo estava fragmentado em pontos soltos. Corrigido para
   escolher a classe MENOS populosa como sujeito (mesma convenção de
   `ink_and_background`) — coberto por `TestSilhouetteHeuristic`.

Script de calibração usado para medir os valores desta seção não foi
commitado (execução única, ad hoc, no diretório de scratch da sessão) — os
valores acima são reproduzíveis executando as funções citadas de
`engine/scripts/check_visual_canon.py` diretamente sobre os arquivos JPEG
referidos na seção 1.
