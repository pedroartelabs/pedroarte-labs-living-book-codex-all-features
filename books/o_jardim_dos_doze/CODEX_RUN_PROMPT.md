\# CODEX RUN PROMPT



\## O Jardim dos Doze



Use o motor editorial já existente em:



`PEDRO\_ARTE\_LIVING\_BOOK\_ENGINE\_v1`



Não recrie o engine, não duplique agentes canônicos e não substitua sua arquitetura genérica. Crie e execute o projeto específico:



`/projects/O\_JARDIM\_DOS\_DOZE/`



A fonte principal de requisitos é:



`/projects/O\_JARDIM\_DOS\_DOZE/PROJECT\_SPEC.md`



\## Objetivo



Produzir integralmente o romance adulto distópico:



\*\*O Jardim dos Doze\*\*

\*\*Onde ninguém cresce, ninguém é inocente.\*\*

\*\*Pedro Arte\*\*



Execute o `TASK\_GRAPH.yaml` completo, respeitando dependências, quality gates, fontes de verdade, regras éticas e definição de pronto.



\## Requisitos incontornáveis



\* 24 capítulos completos;

\* entre 60.000 e 90.000 palavras;

\* português do Brasil;

\* narrativa literária, cinematográfica e adulta;

\* horror psicológico, político e social;

\* nenhuma erotização ou sexualização de personagens com aparência infantil;

\* 1 imagem conceitual em JPG por capítulo;

\* 1 prompt visual por capítulo;

\* revisão visual e de identidade de rostos;

\* LIVING SOUND integrado;

\* revisão estrutural;

\* revisão de trama;

\* revisão de continuidade;

\* revisão científica;

\* revisão política;

\* revisão filosófica;

\* revisão ética;

\* revisão de estilo;

\* revisão gramatical;

\* revisão de originalidade;

\* sumário funcional;

\* formatação Amazon KDP;

\* entrega final em DOCX;

\* relatório final;

\* manifesto de arquivos;

\* ZIP de entrega.



\## Modo de execução



```yaml

engine: PEDRO\_ARTE\_LIVING\_BOOK\_ENGINE\_v1

project: O\_JARDIM\_DOS\_DOZE

execution\_mode: FULL\_BUILD

resume\_allowed: true

checkpointing: true

parallelism:

&#x20; planning\_agents: true

&#x20; chapter\_writers: true

&#x20; image\_prompt\_generation: true

&#x20; independent\_reviews: true

strict\_gates:

&#x20; - ethical\_review

&#x20; - continuity\_review

&#x20; - manuscript\_completeness

&#x20; - visual\_completeness

&#x20; - kdp\_validation

&#x20; - final\_qa

```



Antes de escrever capítulos:



1\. valide o projeto;

2\. normalize a especificação;

3\. construa e bloqueie as bíblias;

4\. gere o mapa de cenas;

5\. valide ciência, política, continuidade e ética;

6\. somente então inicie a escrita.



Escreva os capítulos em blocos controlados pelo engine. Após cada ato, gere checkpoint e relatório de continuidade.



Não substitua narrativa completa por resumos. Não encerre a execução enquanto houver capítulos, imagens, revisões ou arquivos obrigatórios pendentes.



\## Arquivo DOCX obrigatório



`/projects/O\_JARDIM\_DOS\_DOZE/outputs/docx/O\_Jardim\_dos\_Doze\_KDP.docx`



O DOCX deve conter:



\* página de rosto;

\* direitos autorais;

\* sumário;

\* divisão em três atos;

\* 24 capítulos;

\* uma imagem por capítulo;

\* quebras de página;

\* estilos editoriais consistentes;

\* metadados;

\* formatação adequada a livro 6 × 9;

\* estrutura compatível com Amazon KDP.



\## Entrega obrigatória



Ao concluir, gerar:



`/projects/O\_JARDIM\_DOS\_DOZE/outputs/O\_JARDIM\_DOS\_DOZE\_DELIVERY.zip`



O ZIP deve conter todos os manuscritos, imagens, prompts, bíblias, relatórios, arquivos KDP, DOCX e manifesto.



Ao final da execução, imprimir:



```text

PROJECT: O JARDIM DOS DOZE

STATUS: PASSED | FAILED | PARTIAL



MANUSCRIPT WORD COUNT:

CHAPTERS COMPLETED:

CHAPTER IMAGES:

IMAGE PROMPTS:

SOUND PROMPTS:

ETHICAL REVIEW:

CONTINUITY REVIEW:

KDP VALIDATION:

FINAL QA:



MAIN DOCX:

PRINT INTERIOR:

EBOOK DOCX:

DELIVERY ZIP:

FINAL REPORT:



PENDING ITEMS:

```



Inicie agora pelo `T000\_BOOT\_PROJECT` e prossiga até `T370\_DELIVERY`.



