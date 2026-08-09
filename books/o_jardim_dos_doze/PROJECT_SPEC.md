\# PROJECT SPECIFICATION



\## PEDRO\_ARTE\_LIVING\_BOOK\_ENGINE\_v1



```yaml

project:

&#x20; id: PA-LB-OJDD-001

&#x20; slug: o\_jardim\_dos\_doze

&#x20; title: O Jardim dos Doze

&#x20; subtitle: Onde ninguém cresce, ninguém é inocente.

&#x20; author: Pedro Arte

&#x20; language: pt-BR

&#x20; country\_market: Brasil

&#x20; primary\_format: romance

&#x20; genres:

&#x20;   - distopia adulta

&#x20;   - horror psicológico

&#x20;   - thriller político

&#x20;   - ficção científica especulativa

&#x20;   - drama social

&#x20;   - mistério científico

&#x20; target\_word\_count:

&#x20;   minimum: 60000

&#x20;   ideal: 75000

&#x20;   maximum: 90000

&#x20; chapter\_count: 24

&#x20; acts: 3

&#x20; engine: PEDRO\_ARTE\_LIVING\_BOOK\_ENGINE\_v1

&#x20; execution\_mode: FULL\_BUILD

&#x20; publication\_target:

&#x20;   - Amazon KDP paperback

&#x20;   - Amazon KDP ebook

&#x20;   - DOCX editorial

&#x20; content\_rating: adulto

&#x20; status: READY\_FOR\_EXECUTION

```



\---



\# 1. DIRETRIZ DE INTEGRAÇÃO COM O ENGINE



Este projeto deve ser executado utilizando a arquitetura já existente no:



`PEDRO\_ARTE\_LIVING\_BOOK\_ENGINE\_v1`



O Codex não deve reconstruir o motor editorial, duplicar agentes canônicos ou alterar arquivos-base do engine, salvo quando uma correção técnica for indispensável.



O projeto deve funcionar como uma camada específica da obra:



```text

PEDRO\_ARTE\_LIVING\_BOOK\_ENGINE\_v1/

├── engine/

├── agents/

├── workflows/

├── validators/

├── templates/

├── scripts/

└── projects/

&#x20;   └── O\_JARDIM\_DOS\_DOZE/

```



Todos os arquivos específicos do livro devem ficar dentro de:



`/projects/O\_JARDIM\_DOS\_DOZE/`



Os agentes canônicos do engine devem ler as especificações desta pasta como fontes de verdade.



\---



\# 2. ESTRUTURA DO PROJETO



Criar a seguinte estrutura:



```text

/projects/O\_JARDIM\_DOS\_DOZE/

├── PROJECT\_MANIFEST.yaml

├── PROJECT\_SPEC.md

├── RUN\_CONFIG.yaml

├── TASK\_GRAPH.yaml

│

├── source/

│   ├── ORIGINAL\_CONCEPT.md

│   ├── APPROVED\_STORY\_PREMISE.md

│   └── AUTHORIAL\_INTENT.md

│

├── bibles/

│   ├── BOOK\_BIBLE.md

│   ├── STORY\_BIBLE.md

│   ├── WORLD\_BIBLE.md

│   ├── CHARACTER\_BIBLE.md

│   ├── TIMELINE.md

│   ├── PLOT\_BIBLE.md

│   ├── CHAPTER\_BIBLE.md

│   ├── SYMBOLISM\_BIBLE.md

│   ├── LANGUAGE\_BIBLE.md

│   ├── ETHICAL\_BIBLE.md

│   ├── CONTINUITY\_BIBLE.md

│   ├── LIVING\_BOOK\_BIBLE.md

│   ├── IMAGE\_BIOME.md

│   ├── VISUAL\_LIFE\_SPEC.md

│   ├── PAGE\_BIBLE.md

│   ├── LIVING\_SOUND\_BIBLE.md

│   └── KDP\_BIBLE.md

│

├── planning/

│   ├── ACT\_STRUCTURE.md

│   ├── CHARACTER\_ARCS.md

│   ├── REVEAL\_MAP.md

│   ├── FORESHADOWING\_MAP.md

│   ├── EMOTIONAL\_CURVE.md

│   ├── SCENE\_MATRIX.md

│   ├── IMAGE\_PLAN.md

│   └── SOUND\_PLAN.md

│

├── prompts/

│   ├── chapter\_prompts/

│   ├── image\_prompts/

│   ├── cover\_prompts/

│   ├── sound\_prompts/

│   └── marketing\_prompts/

│

├── drafts/

│   ├── chapter\_drafts/

│   ├── integrated/

│   ├── revised/

│   └── final/

│

├── assets/

│   ├── chapter\_images/

│   ├── cover/

│   ├── diagrams/

│   └── sound/

│

├── reviews/

│   ├── developmental/

│   ├── continuity/

│   ├── ethical/

│   ├── scientific/

│   ├── political/

│   ├── philosophical/

│   ├── style/

│   ├── grammar/

│   ├── visual/

│   ├── sound/

│   └── final\_qa/

│

├── outputs/

│   ├── manuscript/

│   ├── docx/

│   ├── kdp/

│   ├── images/

│   ├── cover/

│   ├── sound/

│   ├── marketing/

│   └── reports/

│

└── logs/

&#x20;   ├── execution.log

&#x20;   ├── agent\_decisions.log

&#x20;   ├── revision\_history.log

&#x20;   └── validation.log

```



\---



\# 3. FONTES DE VERDADE



A hierarquia de autoridade editorial será:



1\. `ETHICAL\_BIBLE.md`

2\. `AUTHORIAL\_INTENT.md`

3\. `BOOK\_BIBLE.md`

4\. `STORY\_BIBLE.md`

5\. `WORLD\_BIBLE.md`

6\. `CHARACTER\_BIBLE.md`

7\. `CHAPTER\_BIBLE.md`

8\. `TIMELINE.md`

9\. `CONTINUITY\_BIBLE.md`

10\. Rascunhos e decisões locais dos agentes



Em caso de conflito, a fonte posicionada acima prevalece.



Nenhum agente pode alterar silenciosamente uma definição canônica. Alterações relevantes devem ser registradas em:



`/logs/agent\_decisions.log`



\---



\# 4. BOOK BIBLE



\## 4.1 Identidade da obra



\*\*Título:\*\* O Jardim dos Doze

\*\*Subtítulo:\*\* Onde ninguém cresce, ninguém é inocente.

\*\*Autor:\*\* Pedro Arte



\## 4.2 Logline



Em um país onde todas as pessoas permanecem para sempre com aparência de 12 anos, uma arquivista do governo descobre que a humanidade talvez nunca tenha parado de amadurecer: foi impedida.



\## 4.3 Frase de capa



\*\*Eles parecem crianças. Mas aprenderam todos os crimes dos adultos.\*\*



\## 4.4 Pergunta dramática central



Nina conseguirá provar que a humanidade ainda pode crescer antes que o regime transforme essa possibilidade em mais uma ferramenta de controle?



\## 4.5 Pergunta filosófica central



O que significa ser adulto quando corpo, aparência, linguagem e sociedade foram construídos para impedir qualquer amadurecimento verdadeiro?



\## 4.6 Promessa ao leitor



A obra deve começar parecendo uma distopia visualmente lúdica e quase encantadora. A cada capítulo, a camada infantil deve se revelar como uma tecnologia de dominação política, social, psicológica e biológica.



\## 4.7 Experiência emocional pretendida



O leitor deve experimentar:



\* estranhamento;

\* fascínio visual;

\* curiosidade;

\* desconforto moral;

\* tristeza;

\* repulsa;

\* paranoia;

\* indignação;

\* esperança;

\* perda;

\* medo;

\* dúvida.



\## 4.8 Princípio narrativo



Toda imagem de inocência deve conter ou antecipar alguma forma de controle.



Toda manifestação de brutalidade deve preservar algum vestígio perturbador de estética infantil.



\---



\# 5. AUTHORIAL INTENT



A obra deve denunciar sociedades que:



\* preferem aparência a verdade;

\* transformam linguagem em anestesia moral;

\* infantilizam cidadãos para reduzir sua autonomia;

\* chamam controle de proteção;

\* chamam censura de cuidado;

\* chamam medo de segurança;

\* transformam a inocência em ferramenta de propaganda;

\* tentam impedir o amadurecimento moral, político e individual.



A história não deve afirmar que crianças são cruéis. Ela deve mostrar que adultos moralmente deformados utilizam a imagem social da infância como máscara.



O centro ético do romance é a violação do direito de crescer.



\---



\# 6. ETHICAL BIBLE



\## 6.1 Regra absoluta



A aparência fisicamente infantil dos personagens jamais poderá ser erotizada, fetichizada ou sexualizada.



\## 6.2 Conteúdos proibidos



Não incluir:



\* cenas sexuais explícitas;

\* nudez erotizada;

\* descrição sensual de corpos estabilizados aos 12 anos;

\* fetichização;

\* exploração sexual;

\* romance fundamentado em atração física infantil;

\* violência sexual;

\* conteúdo apelativo envolvendo aparência infantil;

\* imagens gráficas de mutilação;

\* tortura descrita com prazer ou excesso de detalhes.



\## 6.3 Reprodução e continuidade da espécie



A continuidade da espécie deve ser tratada de modo:



\* institucional;

\* médico;

\* científico;

\* burocrático;

\* político;

\* não explícito.



As \*\*Casas de Continuidade\*\* podem ser exploradas como instituições de controle reprodutivo, seleção genética e poder estatal, sem cenas íntimas ou descrições explícitas.



\## 6.4 Violência permitida



A violência pode existir quando necessária à trama, mas deve ser:



\* não gratuita;

\* prioritariamente psicológica;

\* politicamente significativa;

\* emocionalmente consequente;

\* descrita com sobriedade;

\* concentrada em atmosfera, reação e impacto.



\## 6.5 Imagens



As imagens dos capítulos devem priorizar:



\* arquitetura;

\* objetos;

\* silhuetas;

\* corredores;

\* propagandas;

\* brinquedos;

\* telas;

\* documentos;

\* ambientes vazios;

\* símbolos;

\* composição cinematográfica.



Evitar foco corporal desnecessário.



\## 6.6 Validação ética



Cada capítulo deve passar pelo `ETHICAL\_AND\_SENSITIVITY\_REVIEW\_AGENT`.



O agente pode:



\* aprovar;

\* aprovar com correções;

\* reprovar e devolver ao escritor.



\---



\# 7. WORLD BIBLE



\## 7.1 Evento fundador



A humanidade foi atingida, 72 anos antes da narrativa principal, pela pandemia chamada \*\*Febre do Berço\*\*.



A doença provocou alterações:



\* endócrinas;

\* epigenéticas;

\* ósseas;

\* metabólicas;

\* reprodutivas;

\* celulares.



As novas gerações deixaram de atravessar completamente a puberdade e estabilizaram a aparência física ao redor dos 12 anos.



\## 7.2 Síndrome dos Doze



Nome científico inicial:



\*\*Síndrome de Estagnação Puberal Global — SEPG-12\*\*



Nome popular:



\*\*Síndrome dos Doze\*\*



Características:



\* interrupção da maturação física aparente;

\* preservação do desenvolvimento cognitivo;

\* preservação da memória;

\* preservação do envelhecimento psicológico;

\* redução significativa de alguns sinais externos de envelhecimento;

\* manutenção de vulnerabilidades biológicas;

\* expectativa de vida ampliada, mas não ilimitada;

\* ausência de imortalidade.



As pessoas ainda adoecem, acumulam lesões e morrem. Apenas não apresentam a aparência tradicional do envelhecimento adulto.



\## 7.3 Verdade secreta



A Síndrome original não era igualmente permanente em todas as pessoas.



Uma parcela minoritária começou a apresentar reativação natural do amadurecimento.



O Estado suprimiu essa descoberta.



O composto \*\*Anilina-12\*\* foi desenvolvido para:



\* bloquear reativações hormonais;

\* estabilizar o fenótipo dos Doze;

\* facilitar monitoramento biológico;

\* impedir o surgimento de adultos fisicamente maduros;

\* preservar o sistema político criado após a pandemia.



\## 7.4 República de Anil



A história principal acontece na República de Anil.



Características:



\* regime autoritário;

\* propaganda infantilizada;

\* vigilância biológica;

\* economia concentrada;

\* estética pastel;

\* linguagem simplificada;

\* educação permanente;

\* cidadania condicionada à obediência;

\* religião integrada ao poder;

\* controle estatal da memória.



\## 7.5 Sistema político



Nome informal:



\*\*Puerocracia\*\*



Órgão superior:



\*\*Conselho do Jardim\*\*



Chefe de Estado:



\*\*Primeiro Monitor da República\*\*



Líder atual:



\*\*Abel Nóbrega\*\*



Principais instituições:



\* Ministério da Alegria Cívica;

\* Ministério da Continuidade;

\* Guardiões do Recreio;

\* Arquivo da Memória Autorizada;

\* Casas de Continuidade;

\* Escola Modelo Girassol;

\* Jardim Fechado;

\* Igreja do Primeiro Recreio;

\* Laboratórios do Projeto Recreio.



\## 7.6 Eleições



As eleições são chamadas de:



\*\*Festa da Escolha\*\*



Características:



\* candidatos previamente autorizados;

\* estética de festa escolar;

\* doces, balões e mascotes;

\* músicas oficiais;

\* debates roteirizados;

\* apuração manipulada;

\* oposição cenográfica;

\* voto monitorado por identidade biológica.



\## 7.7 Classes sociais e biológicas



\### Doze Puros



Cidadãos considerados biologicamente exemplares. São utilizados em propaganda.



\### Doze Úteis



População produtiva e obediente.



\### Doze Turvos



Pessoas com dúvidas ideológicas, instabilidade emocional ou pequenas anomalias.



\### Doze Rachados



Pessoas classificadas como social ou biologicamente perigosas.



\### Crescidos Impossíveis



Indivíduos que apresentam sinais de amadurecimento físico.



A existência oficial dos Crescidos é negada.



\## 7.8 Broches de ciclo



Cada cidadão usa um broche indicando sua idade real:



\* azul-claro: 12 a 20 anos;

\* amarelo: 21 a 40;

\* verde: 41 a 60;

\* vermelho: 61 a 90;

\* preto: mais de 90.



O broche também funciona como:



\* identificador;

\* rastreador;

\* sensor biológico;

\* credencial de trabalho;

\* carteira civil;

\* dispositivo de vigilância.



\## 7.9 Trabalho



Empresas são organizadas como escolas corporativas.



Termos oficiais:



\* chefe: monitor;

\* departamento: turma;

\* treinamento: recreio formativo;

\* avaliação: boletim produtivo;

\* demissão: recreio definitivo;

\* punição: atividade de correção.



\## 7.10 Justiça



Tribunais são chamados de:



\*\*Salas de Correção\*\*



Punições:



\* perda do direito às cores;

\* reeducação;

\* isolamento;

\* apagamento documental;

\* trabalho compulsório;

\* transferência ao Jardim Fechado;

\* desaparecimento administrativo.



\## 7.11 Religião



Instituição dominante:



\*\*Igreja do Primeiro Recreio\*\*



Doutrina:



\* crescer foi o pecado da humanidade;

\* a aparência infantil é sinal de pureza;

\* desejar amadurecer é rejeitar a salvação;

\* o Conselho protege a nova forma humana.



Lema:



\*\*A criança é pura. O adulto é a doença.\*\*



\## 7.12 Economia



Setores dominantes:



\* Indústria da Fofura;

\* biotecnologia de estabilização;

\* vigilância;

\* memória editada;

\* propaganda;

\* educação permanente;

\* Casas de Continuidade;

\* entretenimento nostálgico.



\## 7.13 Arquitetura



Características:



\* formas arredondadas;

\* cores pastéis;

\* prédios públicos semelhantes a escolas;

\* câmeras em mascotes;

\* alto-falantes escondidos;

\* praças com brinquedos;

\* corredores excessivamente limpos;

\* ausência pública de imagens adultas;

\* espaços projetados para provocar submissão, não conforto.



\## 7.14 Linguagem oficial



| Realidade           | Nome oficial              |

| ------------------- | ------------------------- |

| Prisão              | Cantinho de pausa         |

| Execução            | Encerramento educativo    |

| Censura             | Arrumação do mural        |

| Polícia             | Guardiões do Recreio      |

| Ditador             | Primeiro Monitor          |

| Denúncia            | Bilhete de cuidado        |

| Tortura psicológica | Conversa de reorganização |

| Desaparecimento     | Transferência de turma    |

| Propaganda          | Orientação alegre         |

| Campo de detenção   | Jardim Fechado            |

| Revolta             | Crise de crescimento      |

| Dissidente          | Doze Rachado              |



\## 7.15 Propaganda



Mascote oficial:



\*\*Tico-Tico da Ordem\*\*



Slogan:



\*\*Quem cresce se perde. Quem obedece floresce.\*\*



Mensagem de encerramento dos noticiários:



\*\*Durma pequeno. A República cuida.\*\*



\---



\# 8. CHARACTER BIBLE



\## 8.1 Nina Vale



```yaml

name: Nina Vale

real\_age: 43

visual\_age: 12

role: protagonista

occupation: arquivista do Ministério da Alegria Cívica

cycle\_badge: verde

core\_wound: ajudou a apagar os registros do próprio irmão

external\_goal: descobrir o destino de Ícaro

internal\_goal: recuperar a capacidade de confiar em sua própria memória

fear: descobrir que sempre soube parte da verdade

secret: guarda uma fotografia adulta de Helena

moral\_contradiction: preservou o sistema que agora deseja destruir

arc\_start: obediente, resignada e emocionalmente anestesiada

arc\_middle: investigadora perseguida e culpada

arc\_end: testemunha da verdade sem garantia de vitória

```



Voz:



\* precisa;

\* observadora;

\* contida;

\* marcada por culpa;

\* progressivamente mais emocional.



\## 8.2 Abel Nóbrega



```yaml

name: Abel Nóbrega

real\_age: 78

visual\_age: 12

role: antagonista ideológico

position: Primeiro Monitor da República

core\_wound: sobreviveu ao colapso social da primeira geração

desire: impedir o retorno do caos

fear: que a humanidade volte a desejar mudança

secret: conhece a verdadeira origem da Anilina-12

belief: liberdade é um luxo que civilizações instáveis não podem suportar

contradiction: ama a humanidade abstrata e destrói seres humanos concretos

arc: de líder paternalista a defensor explícito do controle biológico

```



Abel não deve ser retratado como vilão caricatural. Ele acredita que a mentira foi necessária para impedir guerras e fome.



\## 8.3 Caio Sereno



```yaml

real\_age: 51

role: aliado ambíguo

occupation: compositor e roteirista de propaganda

wound: perdeu a filha após uma denúncia fabricada

desire: destruir o Conselho sem provocar guerra civil

fear: que a verdade também seja uma arma

secret: criou jingles usados durante operações de repressão

arc: cúmplice cínico -> conspirador -> sacrifício autoral

```



\## 8.4 Helena Vale



```yaml

real\_age: 69

role: mãe de Nina e guardiã do segredo

former\_occupation: enfermeira das Casas de Continuidade

wound: entregou Ícaro ao Estado

desire: proteger Nina

fear: morrer sem ser perdoada

secret: Ícaro começou a crescer e ela o denunciou

contradiction: sacrificou um filho para salvar outro

arc: silêncio -> confissão -> resistência final

```



\## 8.5 Dr. Silas Nóbrega



```yaml

real\_age: 96

role: cientista da origem

occupation: geneticista

desire: confessar antes de perder a memória

fear: que a cura provoque novo colapso

secret: a Síndrome não era irreversível em todos

contradiction: salvou milhões no curto prazo e aprisionou gerações

destiny: morte ou eliminação após registrar depoimento

```



\## 8.6 Amélia Canto



```yaml

real\_age: 62

role: antagonista comunicacional

position: Ministra da Alegria Cívica

desire: controlar a interpretação pública da realidade

fear: o silêncio após uma tragédia

secret: autorizou o apagamento dos primeiros Crescidos

belief: uma mentira organizada é mais humana que uma verdade caótica

arc: propagandista -> arquiteta da adaptação do regime

```



\## 8.7 Tomás Grilo



```yaml

real\_age: 37

role: perseguidor e aliado tardio

position: capitão dos Guardiões do Recreio

wound: foi denunciado pelos próprios pais

desire: nunca mais ser impotente

fear: compaixão

secret: começou a apresentar sinais de amadurecimento

contradiction: caça aquilo que está se tornando

arc: repressão -> negação -> escolha moral -> sacrifício

```



\## 8.8 Lídia Pomar



```yaml

real\_age: 29

role: fiel sincera ao sistema

occupation: professora de Obediência Cívica

wound: perdeu a família em conflitos anteriores

desire: preservar ordem e segurança

fear: liberdade sem autoridade

secret: denuncia alunos considerados instáveis

contradiction: ama os alunos e os entrega ao Estado

arc: fé -> dúvida -> escolha deliberada pela crença

```



\## 8.9 Ícaro Vale



```yaml

real\_age\_if\_alive: 45

role: presença ausente e motor da investigação

condition: Crescido Impossível

desire: deixar uma prova

fear: ser apagado completamente

secret: colaborou com pesquisadores para proteger outros prisioneiros

destiny: morto antes do presente narrativo

legacy: registros, material biológico e mensagens

```



\## 8.10 Bento Luar



```yaml

real\_age: 18

role: prova viva

occupation: aluno permanente

wound: aprendeu a odiar as mudanças do próprio corpo

desire: viver sem ser tratado como doença

fear: ser levado ao Jardim Fechado

secret: parou de tomar Anilina-12

arc: segredo familiar -> captura -> símbolo involuntário -> esperança ambígua

```



\---



\# 9. RELAÇÕES PRINCIPAIS



```text

Nina <-> Helena

Amor, ressentimento, dependência e segredo.



Nina <-> Ícaro

Culpa construída pela ausência e pela memória apagada.



Nina <-> Caio

Aliança baseada em desconfiança e crimes compartilhados.



Nina <-> Bento

Proteção que começa como investigação e se torna responsabilidade moral.



Nina <-> Abel

Conflito entre verdade individual e estabilidade coletiva.



Abel <-> Silas

Filho político de uma ciência comprometida pelo medo.



Tomás <-> Bento

Caçador e prova viva daquilo que o caçador esconde em si.



Amélia <-> Nina

Duas arquivistas da realidade: uma tenta libertá-la, outra tenta administrá-la.

```



\---



\# 10. TIMELINE



\## Marco zero



Ano 0 — início da Febre do Berço.



\## Anos 1 a 5



\* colapso sanitário;

\* identificação da Síndrome;

\* mortes de adultos da antiga geração;

\* falência de governos;

\* migrações;

\* guerras de abastecimento.



\## Anos 6 a 15



\* surgimento das primeiras crianças biologicamente estabilizadas;

\* criação das Casas de Continuidade;

\* início dos estudos sobre longevidade;

\* primeiros casos de reativação de amadurecimento.



\## Anos 16 a 25



\* desenvolvimento da Anilina-12;

\* fundação do Projeto Recreio;

\* desaparecimento dos primeiros Crescidos;

\* ascensão política de Anil;

\* criação do Conselho do Jardim.



\## Anos 26 a 45



\* consolidação da Puerocracia;

\* proibição de imagens adultas;

\* transformação das escolas em centros permanentes;

\* crescimento da Igreja do Primeiro Recreio;

\* infância convertida em identidade nacional.



\## Anos 46 a 60



\* estabelecimento dos Doze Puros;

\* expansão da vigilância por broches;

\* criação do Jardim Fechado;

\* desaparecimento de Ícaro;

\* Nina entra no Ministério.



\## Ano 72



Presente narrativo.



Duração da trama principal:



Aproximadamente 18 dias.



\---



\# 11. PLOT BIBLE



\## 11.1 Conspiração em camadas



\### Camada 1 — mentira sanitária



O governo afirma que Crescidos são anomalias contagiosas.



\### Camada 2 — mentira médica



O governo afirma que o amadurecimento inevitavelmente provoca morte.



\### Camada 3 — mentira histórica



Arquivos sobre adultos e reativações foram apagados.



\### Camada 4 — mentira farmacológica



A Anilina-12 é vendida como suplemento protetor, mas bloqueia o amadurecimento.



\### Camada 5 — mentira política



A Puerocracia depende da permanência dos corpos infantis.



\### Camada 6 — verdade moral



Mesmo depois de a mentira ser revelada, o regime pode sobreviver apropriando-se da ideia de crescimento.



\## 11.2 Revelação principal



A humanidade não permaneceu completamente incapaz de crescer.



A possibilidade de amadurecimento foi:



\* escondida;

\* patologizada;

\* medicalizada;

\* criminalizada;

\* interrompida;

\* convertida em ameaça política.



\## 11.3 Clímax



Nina e Caio utilizam o jingle nacional para transmitir os arquivos secretos durante o Dia Nacional do Jardim.



\## 11.4 Reversão do clímax



A população reage, mas o governo ativa o Protocolo Berço e neutraliza a revolta.



\## 11.5 Desfecho



Bento apresenta sinais inequívocos de amadurecimento. Simultaneamente, o governo anuncia o programa \*\*Crescimento Seguro\*\*, indicando que tentará monopolizar a própria revolução.



\---



\# 12. ESTRUTURA DOS ATOS



\## Ato I — A Casca Colorida



Capítulos 1 a 8.



Objetivos:



\* apresentar o mundo;

\* construir estranhamento;

\* introduzir Nina;

\* mostrar a linguagem infantilizada;

\* revelar Ícaro como Crescido;

\* conectar Nina a Caio e Bento;

\* transformar dúvida em investigação.



Ponto de virada:



Nina descobre que seu broche a monitora e que o Estado já percebeu sua investigação.



\## Ato II — O País Debaixo da Tinta



Capítulos 9 a 18.



Objetivos:



\* revelar o Jardim Fechado;

\* comprovar a existência dos Crescidos;

\* revelar a Anilina-12;

\* aprofundar a culpa de Helena;

\* ampliar a perseguição;

\* revelar o papel da Igreja;

\* confirmar o destino de Ícaro;

\* preparar o plano nacional do governo.



Ponto de virada:



Abel anuncia a vacinação nacional reforçada e transforma Nina em inimiga pública.



\## Ato III — Crescer é Crime



Capítulos 19 a 24.



Objetivos:



\* executar a transmissão;

\* sacrificar Helena e Caio;

\* provocar reação popular;

\* destruir a esperança imediata;

\* salvar Bento;

\* mostrar a capacidade adaptativa do regime;

\* encerrar com esperança ambígua.



\---



\# 13. CHAPTER BIBLE



\## Capítulo 1 — A Praça dos Balões Murchos



```yaml

act: 1

pov: Nina

primary\_location: Praça da Harmonia

dramatic\_function: introduzir estética e contradição do mundo

conflict: Nina presencia falha em transmissão pública

reveal: surge por segundos a imagem proibida de um adulto

dominant\_emotion: estranhamento

visual\_symbol: balões murchos

foreshadowing: imagens adultas foram sistematicamente apagadas

hook: Nina recebe ordem para eliminar o arquivo original

image\_direction: praça pastel, balões murchos, telão com rosto adulto fragmentado

sound\_motif: melodia de caixa de música com nota grave deslocada

```



\## Capítulo 2 — O Ministério da Alegria Cívica



```yaml

pov: Nina

function: mostrar a máquina de edição da realidade

conflict: Nina precisa suavizar notícia de repressão fatal

reveal: encontra o nome Ícaro Vale

emotion: culpa

symbol: carimbo sorridente sobre fotografia censurada

hook: classificação Crescido Impossível

image\_direction: mesa burocrática, carimbos alegres, documentos escuros

sound\_motif: teclas mecânicas e coro infantil processado

```



\## Capítulo 3 — A Festa da Escolha



```yaml

pov: Nina

function: expor política infantilizada

conflict: eleição encenada

reveal: resultado decidido antes da contagem

emotion: impotência

symbol: urna semelhante a caixa de brinquedos

hook: cidadão grita que deseja crescer

image\_direction: eleição pastel com balões, urna e sombras de guardas

sound\_motif: banda escolar excessivamente alegre

```



\## Capítulo 4 — A Casa de Helena



```yaml

pov: Nina

function: introduzir segredo familiar

conflict: Helena tenta impedir a investigação

reveal: fotografia adulta da mãe

emotion: melancolia

symbol: retrato amarelado

hook: Helena afirma que Ícaro não morreu pequeno

image\_direction: casa antiga, fotografia adulta iluminada por fim de tarde

sound\_motif: piano doméstico e respiração envelhecida

```



\## Capítulo 5 — A Escola Modelo Girassol



```yaml

pov: Nina

function: apresentar Bento e a doutrinação

conflict: exame biológico escolar

reveal: Bento possui código semelhante ao de Ícaro

emotion: apreensão

symbol: giz quebrado

hook: alerta médico silencioso

image\_direction: sala colorida, carteiras pequenas, giz quebrado, câmera de pelúcia

sound\_motif: sino escolar desacelerado

```



\## Capítulo 6 — Atividade Educativa



```yaml

pov: Nina

function: revelar brutalidade pública

conflict: execução apresentada como educação

reveal: condenado denuncia desaparecimento dos Crescidos

emotion: horror

symbol: palco escolar com cadeira central

hook: mensagem Procure o Recreio

image\_direction: palco colorido vazio, cadeira sob holofote, bandeirolas

sound\_motif: aplausos artificiais cortados por silêncio

```



\## Capítulo 7 — O Homem que Escrevia Canções



```yaml

pov: Nina

function: introduzir Caio

conflict: Nina não sabe se pode confiar nele

reveal: jingles possuem códigos de condicionamento

emotion: paranoia

symbol: partitura infantil riscada

hook: Ícaro passou pelo Jardim Fechado

image\_direction: estúdio de propaganda, partitura, microfone e mascote sorridente

sound\_motif: jingle desmontado em camadas inquietantes

```



\## Capítulo 8 — O Espelho sem Futuro



```yaml

pov: Nina

function: consolidar crise interna

conflict: Nina confronta a própria aparência

reveal: broche contém rastreador biológico

emotion: repulsa íntima

symbol: espelho coberto por adesivos

hook: o rastreador envia alerta ao Ministério

image\_direction: reflexo infantil e sombra adulta indefinida

sound\_motif: pulso eletrônico semelhante a batimento

```



\## Capítulo 9 — Jardim Fechado



```yaml

act: 2

pov: Nina

function: comprovar a conspiração

conflict: invasão de arquivo subterrâneo

reveal: vídeos de pessoas amadurecendo

emotion: choque

symbol: corredor hospitalar pintado com nuvens

hook: Ícaro chama Nina pelo nome em uma gravação

image\_direction: corredor clínico pastel, portas numeradas, tela antiga

sound\_motif: ventilação hospitalar e voz distante

```



\## Capítulo 10 — Os Doze Puros



```yaml

pov: Nina

function: destruir símbolo propagandístico

conflict: investigação dos cidadãos-modelo

reveal: recebem tratamentos contínuos

emotion: nojo

symbol: sorriso em cartaz rasgado

hook: um modelo morre durante campanha

image\_direction: cartaz perfeito rasgado revelando equipamentos médicos

sound\_motif: flashes fotográficos e sintetizador instável

```



\## Capítulo 11 — A Confissão do Dr. Silas



```yaml

pov: Nina

function: explicar origem científica

conflict: Silas teme revelar a verdade

reveal: Projeto Recreio prolongou a Síndrome

emotion: devastação

symbol: frascos azuis alinhados

hook: fórmula parcial da Anilina-12

image\_direction: laboratório antigo com frascos azuis e desenhos infantis

sound\_motif: vidro, relógio e cordas graves

```



\## Capítulo 12 — O Suplemento Azul



```yaml

pov: Nina

function: relacionar conspiração ao cotidiano

conflict: confronto com Helena

reveal: Helena participou das primeiras aplicações

emotion: traição

symbol: copo azul de merenda

hook: Guardiões cercam a casa

image\_direction: mesa familiar, copo azul, luzes de repressão na janela

sound\_motif: colher batendo no copo e sirene melódica

```



\## Capítulo 13 — A Fuga pela Cidade Doce



```yaml

pov: Nina

function: converter investigação em perseguição

conflict: fuga urbana

reveal: Tomás deixa Nina escapar

emotion: pânico

symbol: escorregador como rota de fuga

hook: Helena é capturada

image\_direction: cidade pastel à noite, parquinho, drones e sombras

sound\_motif: percussão de brinquedo acelerada

```



\## Capítulo 14 — A Professora que Acreditava



```yaml

pov: Lídia

function: mostrar cumplicidade sincera

conflict: Lídia denuncia Bento

reveal: exames oficiais foram adulterados

emotion: angústia

symbol: nomes apagados do mural

hook: Bento é levado

image\_direction: mural escolar com silhueta removida

sound\_motif: coro escolar desafinado

```



\## Capítulo 15 — O Primeiro Recreio



```yaml

pov: Nina

function: revelar participação religiosa

conflict: infiltração em culto

reveal: Igreja conhece o Projeto Recreio

emotion: sufocamento

symbol: vitral de criança sem rosto

hook: Nina rouba chave do arquivo sagrado

image\_direction: templo colorido, vitral vazio, congregação em sombra

sound\_motif: órgão, palmas lentas e sussurros

```



\## Capítulo 16 — A Cidade sem Adultos



```yaml

pov: Nina

function: devolver ao leitor imagens do mundo perdido

conflict: Nina enfrenta arquivos proibidos

reveal: imagens adultas foram proibidas para eliminar desejo

emotion: luto histórico

symbol: álbum queimado

hook: gravação final de Ícaro

image\_direction: arquivo escuro, fotografias adultas espalhadas

sound\_motif: projetor antigo e violoncelo

```



\## Capítulo 17 — Antes, Durante, Sem Conclusão



```yaml

pov: Nina através da gravação

function: revelar destino de Ícaro

conflict: testemunho fragmentado

reveal: ele cresceu após abandonar a Anilina-12

emotion: perda

symbol: sapato pequeno diante de pegada maior

hook: Bento é a próxima prova

image\_direction: sala de observação, pegadas de tamanhos diferentes

sound\_motif: fita magnética e voz interrompida

```



\## Capítulo 18 — O Pronunciamento de Abel



```yaml

pov: Nina e transmissão oficial

function: elevar conflito para escala nacional

conflict: Nina é declarada terrorista

reveal: nova dose será aplicada a toda população

emotion: urgência

symbol: mascote sorrindo durante decreto

hook: aplicação no Dia Nacional do Jardim

image\_direction: telão monumental, Abel e mascote sob luz alegre

sound\_motif: marcha infantil e graves militares

```



\## Capítulo 19 — O Dia Nacional do Jardim



```yaml

act: 3

pov: Nina

function: iniciar operação final

conflict: infiltração no sistema nacional

reveal: Helena será usada em transmissão

emotion: expectativa

symbol: confetes azuis

hook: Helena acusa Nina diante do país

image\_direction: festival nacional, confetes e central de transmissão

sound\_motif: jingle triunfal com ruído escondido

```



\## Capítulo 20 — A Mãe no Telão



```yaml

pov: Nina

function: concluir arco de Helena

conflict: salvar a mãe ou liberar os arquivos

reveal: Helena fornece o código

emotion: dor

symbol: rosto dividido em telas

hook: arquivos começam a ser liberados

image\_direction: mosaico de telas com Helena e códigos

sound\_motif: voz materna, estática e piano

```



\## Capítulo 21 — A Verdade Cantada



```yaml

pov: Nina e Caio

function: clímax da transmissão

conflict: manter sinal ativo

reveal: o jingle carrega os arquivos

emotion: catarse

symbol: partitura transformada em denúncia

hook: o país inteiro fica em silêncio

image\_direction: alto-falantes urbanos emitindo fragmentos de documentos

sound\_motif: tema oficial se desfazendo em canto humano

```



\## Capítulo 22 — A Esperança Interrompida



```yaml

pov: múltiplos fragmentos controlados

function: destruir vitória imediata

conflict: revolta popular versus Protocolo Berço

reveal: drones liberam névoa calmante

emotion: esperança destruída

symbol: confete misturado à fumaça azul

hook: Bento cai dizendo que não é doença

image\_direction: multidão sob névoa azul e confetes

sound\_motif: vozes coletivas abafadas

```



\## Capítulo 23 — O Corpo de Bento



```yaml

pov: Nina

function: resgatar a prova viva

conflict: invasão da clínica móvel

reveal: Tomás escolhe ajudar

emotion: sacrifício

symbol: uniforme abandonado

hook: Tomás fecha a porta e fica para trás

image\_direction: corredor móvel, uniforme de guarda no chão

sound\_motif: respiração, metal e batimento crescente

```



\## Capítulo 24 — O Último Recreio



```yaml

pov: Nina

function: desfecho ambíguo

conflict: compreender se houve vitória

reveal: Bento amadurece; regime lança Crescimento Seguro

emotion: incerteza

symbol: árvore no pátio rachado

final\_image: sombra adulta projetada por Bento

sound\_motif: vento real, madeira, nota única de piano

final\_sentence: E, pela primeira vez em décadas, uma criança impossível projetou uma sombra adulta sobre o chão do Jardim.

```



\---



\# 14. REVEAL MAP



| Percentual aproximado | Revelação                                   |

| --------------------- | ------------------------------------------- |

| 5%                    | Imagens adultas foram apagadas              |

| 10%                   | Ícaro foi classificado como Crescido        |

| 20%                   | Bento apresenta a mesma classificação       |

| 30%                   | O Jardim Fechado existe                     |

| 38%                   | Pessoas realmente amadurecem                |

| 45%                   | Doze Puros são tratados artificialmente     |

| 52%                   | O Projeto Recreio prolongou a Síndrome      |

| 58%                   | A Anilina-12 é distribuída diariamente      |

| 65%                   | Helena entregou Ícaro                       |

| 72%                   | A Igreja participou da conspiração          |

| 78%                   | Ícaro cresceu após interromper o suplemento |

| 82%                   | O governo planeja reforçar o bloqueio       |

| 90%                   | A verdade é transmitida                     |

| 94%                   | A revolta é neutralizada                    |

| 100%                  | O regime absorve o conceito de crescimento  |



\---



\# 15. FORESHADOWING MAP



Inserir antecipações discretas:



\* balões que nunca sobem completamente;

\* portas e móveis inadequados para pessoas de idades reais diferentes;

\* pessoas com dores crônicas em corpos aparentemente jovens;

\* suplementos azuis em escolas e empresas;

\* câmeras que analisam temperatura e postura;

\* proibição de fotografias antigas;

\* desenhos de figuras altas apagados por professores;

\* Tomás tocando discretamente o próprio maxilar;

\* Bento recusando a merenda;

\* Helena escondendo objetos de Ícaro;

\* Abel utilizando a expressão “crescimento administrado” antes da revelação;

\* Amélia demonstrando capacidade de absorver narrativas opositoras.



\---



\# 16. CHARACTER ARC MAP



\## Nina



```text

obediência

→ desconforto

→ investigação

→ culpa

→ ruptura

→ perda da mãe

→ transmissão da verdade

→ responsabilidade por Bento

→ aceitação da incerteza

```



\## Abel



```text

paternalismo

→ contenção

→ perseguição

→ defesa ideológica da mentira

→ aparente derrota

→ sobrevivência estrutural do sistema

```



\## Helena



```text

silêncio

→ evasão

→ confissão

→ captura

→ denúncia forçada

→ código libertador

→ desaparecimento

```



\## Caio



```text

cinismo

→ colaboração

→ revelação da culpa

→ criação da transmissão

→ sacrifício

→ legado musical

```



\## Tomás



```text

repressão

→ sinais físicos

→ negação

→ compaixão involuntária

→ perseguição pelo próprio sistema

→ sacrifício

```



\## Bento



```text

vergonha

→ medo

→ denúncia

→ captura

→ quase apagamento

→ resgate

→ amadurecimento

→ símbolo disputado

```



\---



\# 17. STYLE BIBLE



\## 17.1 Pessoa narrativa



Terceira pessoa limitada, predominantemente acompanhando Nina.



Capítulos específicos podem acompanhar Lídia ou fragmentos públicos, desde que a transição seja claramente sinalizada.



\## 17.2 Tempo verbal



Passado.



\## 17.3 Estilo



\* literário;

\* cinematográfico;

\* sensorial;

\* claro;

\* sombrio;

\* emocionalmente contido;

\* sem floreios excessivos;

\* sem explicações didáticas longas;

\* com imagens simbólicas recorrentes.



\## 17.4 Ritmo



Capítulos devem alternar:



\* observação;

\* investigação;

\* revelação;

\* confronto;

\* perseguição;

\* perda;

\* reflexão;

\* ação.



Não escrever todos os capítulos com o mesmo ritmo.



\## 17.5 Diálogos



Diálogos devem:



\* revelar poder;

\* ocultar intenções;

\* evitar exposição artificial;

\* diferenciar as vozes;

\* utilizar linguagem oficial quando pertinente;

\* mostrar conflito entre palavras suaves e significados cruéis.



\## 17.6 Linguagem governamental



Sempre que o regime praticar violência, utilizar inicialmente o eufemismo oficial. A narração deve gradualmente revelar a realidade por trás dele.



\## 17.7 Descrições físicas



Evitar descrições repetitivas sobre aparência de 12 anos.



A condição deve ser demonstrada por:



\* contraste entre voz e rosto;

\* broches de ciclo;

\* postura;

\* autoridade;

\* memória;

\* cansaço;

\* objetos;

\* contexto social.



\## 17.8 Proibições estilísticas



Evitar:



\* excesso de adjetivos;

\* melodrama contínuo;

\* vilões explicando toda a conspiração;

\* capítulos puramente expositivos;

\* repetição constante da premissa;

\* uso banal de “criança” para todos os personagens;

\* humor que diminua o horror;

\* ciência impossível sem regras internas;

\* finais excessivamente explicados.



\---



\# 18. SYMBOLISM BIBLE



\## Jardim



Representa:



\* sociedade;

\* cultivo controlado;

\* beleza artificial;

\* poda;

\* vigilância;

\* crescimento permitido apenas pelo jardineiro.



\## Número 12



Representa:



\* limite;

\* fronteira;

\* identidade compulsória;

\* relógio interrompido;

\* ciclo incompleto.



\## Azul-anil



Representa:



\* segurança oficial;

\* anestesia;

\* medicamento;

\* vigilância;

\* mentira institucional.



\## Balões



Representam:



\* celebração;

\* fragilidade;

\* promessa de ascensão;

\* incapacidade de subir;

\* alegria vazia.



\## Espelhos



Representam:



\* corpo aprisionado;

\* identidade política;

\* distância entre consciência e aparência.



\## Árvores



Representam:



\* crescimento orgânico;

\* memória;

\* mudança sem autorização;

\* revolução biológica.



\## Sapatos e pegadas



Representam:



\* passagem;

\* crescimento;

\* tamanho imposto;

\* evidência material da mudança.



\## Música



Representa:



\* condicionamento coletivo;

\* memória;

\* propaganda;

\* comunicação clandestina;

\* possibilidade de libertação.



\---



\# 19. LIVING BOOK BIBLE



A obra deve ser tratada como um organismo narrativo.



\## 19.1 Batimento



O batimento básico é:



```text

doçura visual

→ percepção de algo errado

→ revelação parcial

→ repressão

→ silêncio

```



\## 19.2 Respiração



Capítulos de alta tensão devem ser seguidos por cenas mais silenciosas que permitam:



\* culpa;

\* luto;

\* reflexão;

\* assimilação da revelação.



\## 19.3 Temperatura emocional



\* Ato I: morna, artificial e desconfortável;

\* Ato II: fria, clínica e paranoica;

\* Ato III: febril, pública e instável;

\* Epílogo narrativo: vento natural e ambiguidade.



\## 19.4 Metabolismo narrativo



Cada capítulo deve consumir uma certeza anterior e produzir uma nova dúvida.



\## 19.5 Sistema imunológico da obra



Os agentes revisores devem eliminar:



\* incoerência;

\* exposição excessiva;

\* repetição;

\* sensacionalismo;

\* sexualização;

\* violência vazia;

\* simbolismo sem função;

\* personagens unidimensionais.



\---



\# 20. IMAGE BIOME



\## 20.1 Identidade visual



Estética:



\* distopia pastel;

\* arquitetura escolar;

\* iluminação cinematográfica;

\* simetria institucional;

\* espaços limpos demais;

\* objetos infantis deslocados;

\* sombras longas;

\* sinais discretos de decadência;

\* sensação de memória proibida.



\## 20.2 Paleta conceitual



\* azul-anil;

\* amarelo escolar desbotado;

\* rosa pálido;

\* verde hospitalar;

\* branco clínico;

\* cinza de concreto;

\* vermelho usado apenas como alerta.



A paleta serve como referência conceitual. Não é obrigatório impor valores exatos de cor durante a geração.



\## 20.3 Regras de personagens



Quando personagens aparecerem:



\* postura e expressão devem refletir idade real;

\* roupas devem ser institucionais e não sensualizadas;

\* enquadramento deve privilegiar narrativa;

\* nenhum foco corporal apelativo;

\* evitar aparência excessivamente fotográfica de crianças reais;

\* preferir composição ficcional, estilizada, simbólica ou parcialmente ocultada.



\## 20.4 Imagem por capítulo



Gerar 24 imagens em alta resolução.



Padrão:



```text

/assets/chapter\_images/chapter\_01.jpg

...

/assets/chapter\_images/chapter\_24.jpg

```



Criar também:



```text

/prompts/image\_prompts/chapter\_01.md

...

/prompts/image\_prompts/chapter\_24.md

```



\## 20.5 Orientação



Imagens internas:



\* preferencialmente verticais;

\* adequadas a página 6 × 9;

\* mínimo de 1800 × 2700 pixels;

\* JPG;

\* 300 DPI quando aplicável;

\* sem texto embutido, salvo propaganda diegética indispensável.



\## 20.6 Continuidade visual



O `FACE\_AND\_VISUAL\_IDENTITY\_AGENT` deve criar fichas visuais canônicas de:



\* Nina;

\* Abel;

\* Caio;

\* Helena;

\* Silas;

\* Amélia;

\* Tomás;

\* Lídia;

\* Bento.



Salvar em:



`/bibles/VISUAL\_CHARACTER\_IDENTITIES.md`



\---



\# 21. VISUAL LIFE SPEC



As imagens não devem parecer ilustrações independentes. Devem transmitir a sensação de que o próprio livro as produziu.



Cada imagem deve conter:



\* um sinal vital narrativo;

\* um símbolo do capítulo;

\* alguma forma de controle;

\* um contraste entre superfície e verdade;

\* continuidade com a imagem anterior;

\* preparação emocional para a imagem seguinte.



Exemplo:



```text

Capítulo 1: balões que não sobem

Capítulo 2: carimbos que escondem

Capítulo 3: votos que não escolhem

Capítulo 4: fotografia que lembra

Capítulo 5: giz que se quebra

...

Capítulo 24: árvore que cresce

```



\---



\# 22. LIVING SOUND BIBLE



\## 22.1 Princípio



A trilha não deve apenas acompanhar a história. Deve parecer um som produzido pelo próprio livro porque ele está vivo.



\## 22.2 Identidade sonora



Elementos principais:



\* caixa de música;

\* sino escolar;

\* coro distante;

\* brinquedos percussivos;

\* sintetizadores analógicos;

\* ruído de fitas;

\* ventilação hospitalar;

\* anúncios públicos;

\* piano doméstico;

\* cordas graves;

\* silêncios abruptos;

\* sons naturais raros.



\## 22.3 Motivo da República



Uma melodia curta, doce e repetitiva, composta por cinco notas.



Ao longo do livro, ela deve:



\* surgir limpa;

\* tornar-se desafinada;

\* receber graves;

\* fragmentar-se;

\* transformar-se em código;

\* desaparecer no capítulo final.



\## 22.4 Motivo de Nina



\* piano abafado;

\* som de papel;

\* batimento eletrônico;

\* notas incompletas.



\## 22.5 Motivo de Bento



\* respiração;

\* madeira estalando;

\* corda musical subindo lentamente;

\* sons orgânicos.



\## 22.6 Motivo de Ícaro



\* fita magnética;

\* voz parcialmente apagada;

\* ruído de projetor;

\* intervalos incompletos.



\## 22.7 Motivo de Abel



\* marcha escolar;

\* palmas sincronizadas;

\* graves militares quase imperceptíveis.



\## 22.8 Evolução sonora por ato



\### Ato I



Música doce com pequenas dissonâncias.



\### Ato II



Ambientes clínicos, ruído mecânico e fragmentação dos jingles.



\### Ato III



Propaganda em escala nacional, sobreposição de vozes, colapso sonoro e retorno gradual do som natural.



\## 22.9 Entregáveis sonoros



Criar:



\* `LIVING\_SOUND\_BIBLE.md`;

\* 24 prompts de atmosfera sonora;

\* tema principal;

\* motivo de Nina;

\* motivo de Abel;

\* motivo de Bento;

\* motivo do Jardim;

\* prompt de teaser sonoro;

\* orientação para audiobook;

\* relatório de continuidade sonora.



Não é obrigatório gerar arquivos de áudio se o ambiente não possuir modelo apropriado. Os prompts e especificações são obrigatórios.



\---



\# 23. PAGE BIBLE



\## 23.1 Formato principal



Paperback Amazon KDP:



\* tamanho: 6 × 9 polegadas;

\* interior: preto e branco ou escala de cinza;

\* sangria: de acordo com o uso das imagens;

\* imagens preferencialmente sem sangria, centralizadas;

\* capítulos iniciando em nova página.



\## 23.2 Estrutura editorial



1\. Página de rosto;

2\. Página de direitos autorais;

3\. Dedicatória opcional;

4\. Epígrafe;

5\. Sumário;

6\. Nota ética opcional;

7\. Ato I;

8\. Capítulos 1 a 8;

9\. Ato II;

10\. Capítulos 9 a 18;

11\. Ato III;

12\. Capítulos 19 a 24;

13\. Nota do autor opcional;

14\. Sobre o autor.



\## 23.3 Página de capítulo



Ordem:



1\. quebra de página;

2\. imagem do capítulo;

3\. número e título do capítulo;

4\. epígrafe curta opcional;

5\. texto.



\## 23.4 Tipografia



Fontes permitidas:



\* Garamond;

\* EB Garamond;

\* Georgia;

\* Times New Roman;

\* outra fonte serifada segura.



Configuração recomendada:



\* corpo: 11 ou 11,5 pt;

\* título de capítulo: 18 a 24 pt;

\* espaçamento entre linhas: aproximadamente 1,1 a 1,2;

\* recuo de primeira linha;

\* sem espaço excessivo entre parágrafos;

\* cenas separadas por ornamento simples.



\## 23.5 Sumário



Criar sumário automático no DOCX utilizando estilos reais de título.



Também criar versão de sumário compatível com conversão para ebook.



\## 23.6 Cabeçalhos e rodapés



\* nome do livro em páginas pares;

\* nome do autor em páginas ímpares;

\* sem cabeçalho na primeira página de capítulos;

\* numeração iniciando no corpo principal.



\---



\# 24. KDP BIBLE



\## 24.1 Arquivos finais obrigatórios



```text

/outputs/docx/O\_Jardim\_dos\_Doze\_KDP.docx

/outputs/manuscript/O\_Jardim\_dos\_Doze\_Final.md

/outputs/manuscript/O\_Jardim\_dos\_Doze\_Final.txt

/outputs/kdp/O\_Jardim\_dos\_Doze\_Print\_Interior.pdf

/outputs/kdp/O\_Jardim\_dos\_Doze\_Ebook.docx

```



O PDF deve ser gerado apenas se o ambiente possuir método confiável de conversão e validação.



\## 24.2 Metadados



```yaml

title: O Jardim dos Doze

subtitle: Onde ninguém cresce, ninguém é inocente.

author: Pedro Arte

language: Portuguese

keywords:

&#x20; - distopia adulta

&#x20; - ficção científica distópica

&#x20; - horror psicológico

&#x20; - thriller político

&#x20; - sociedade autoritária

&#x20; - futuro sombrio

&#x20; - conspiração genética

```



\## 24.3 Descrição comercial



Criar duas versões:



\* descrição curta de até 1.000 caracteres;

\* descrição Amazon KDP de até 4.000 caracteres.



\## 24.4 Categorias sugeridas



Avaliar categorias KDP disponíveis no momento da publicação relacionadas a:



\* ficção científica distópica;

\* thrillers políticos;

\* horror psicológico;

\* ficção especulativa;

\* ficção social.



Não assumir códigos fixos de categorias sem validação atual.



\---



\# 25. COVER BRIEF



\## Conceito principal



Uma figura de aparência infantil diante de um espelho. A figura real permanece pequena, mas o reflexo projeta uma sombra adulta, alta e deformada pela censura visual.



\## Elementos



\* corredor escolar ou ministerial;

\* cores pastéis desbotadas;

\* broche com o número 12;

\* câmera escondida em mascote;

\* árvore ou rachadura discreta;

\* atmosfera literária;

\* forte legibilidade em miniatura.



\## Título



\*\*O JARDIM DOS DOZE\*\*



\## Subtítulo



\*\*Onde ninguém cresce, ninguém é inocente.\*\*



\## Autor



\*\*PEDRO ARTE\*\*



\## Regras



\* sem sexualização;

\* sem aparência de literatura infantil;

\* sem excesso de elementos;

\* não utilizar rostos de crianças reais identificáveis;

\* comunicar claramente distopia adulta;

\* composição profissional para KDP;

\* título altamente legível.



\## Conceitos alternativos



1\. Mesa de governo com cadeiras pequenas e documentos de execução.

2\. Parquinho vazio sob luzes policiais.

3\. Broche número 12 sobre uniforme institucional.

4\. Árvore crescendo em pátio escolar rachado.

5\. Fotografia de adulto sendo coberta por adesivos sorridentes.



\---



\# 26. CENAS OBRIGATÓRIAS



O manuscrito deve conter organicamente:



\* reunião de governo com decisões cruéis;

\* propaganda do Tico-Tico da Ordem;

\* execução como atividade educativa;

\* escola de doutrinação adulta;

\* Festa da Escolha;

\* refeição familiar escondendo o segredo de Ícaro;

\* Nina diante do espelho;

\* confissão científica de Silas;

\* fuga pela cidade pastel;

\* revolta nacional;

\* destruição da esperança pela névoa;

\* revelação da mentira;

\* anúncio de Crescimento Seguro;

\* sombra adulta de Bento no final.



\---



\# 27. REQUISITOS DE CAPÍTULO



Cada capítulo deve conter:



```yaml

minimum\_words: 2200

ideal\_words: 2800

maximum\_words: 3800

required\_elements:

&#x20; - objetivo dramático

&#x20; - conflito

&#x20; - progressão

&#x20; - mudança de estado

&#x20; - símbolo visual

&#x20; - detalhe sensorial

&#x20; - continuidade

&#x20; - gancho final

&#x20; - prompt de imagem

&#x20; - prompt sonoro

```



Capítulos podem ultrapassar a faixa quando necessário, mas capítulos muito curtos devem ser justificados pelo ritmo narrativo.



\---



\# 28. AGENTES CANÔNICOS A SEREM ACIONADOS



O engine deve utilizar, quando presentes, os seguintes papéis canônicos:



\* `EDITORIAL\_DIRECTOR\_AGENT`

\* `BOOK\_ARCHITECT\_AGENT`

\* `WORLD\_BUILDING\_AGENT`

\* `PLOT\_ARCHITECT\_AGENT`

\* `CHARACTER\_ARCHITECT\_AGENT`

\* `TIMELINE\_AND\_CONTINUITY\_AGENT`

\* `SCIENTIFIC\_COHERENCE\_AGENT`

\* `POLITICAL\_SYSTEM\_AGENT`

\* `ETHICAL\_AND\_SENSITIVITY\_REVIEW\_AGENT`

\* `PRIMARY\_WRITER\_AGENT`

\* `CHAPTER\_WRITER\_AGENTS`

\* `DEVELOPMENTAL\_EDITOR\_AGENT`

\* `PLOT\_REVIEW\_AGENT`

\* `PHILOSOPHICAL\_REVIEW\_AGENT`

\* `CONTINUITY\_REVIEW\_AGENT`

\* `STYLE\_REVIEW\_AGENT`

\* `GRAMMAR\_REVIEW\_AGENT`

\* `MERGE\_AND\_INTEGRATION\_AGENT`

\* `FACE\_AND\_VISUAL\_IDENTITY\_AGENT`

\* `IMAGE\_BIOME\_AGENT`

\* `CHAPTER\_IMAGE\_AGENT`

\* `VISUAL\_CONTINUITY\_AGENT`

\* `LIVING\_SOUNDTRACK\_ARCHITECT`

\* `LIVING\_SOUND\_COMPOSER\_AGENT`

\* `SOUND\_CONTINUITY\_AGENT`

\* `PAGE\_ARCHITECT\_AGENT`

\* `DOCX\_FORMATTER\_AGENT`

\* `KDP\_COMPLIANCE\_AGENT`

\* `LEGAL\_AND\_ORIGINALITY\_AGENT`

\* `FINAL\_QA\_AGENT`

\* `DELIVERY\_AGENT`



Caso os nomes internos sejam diferentes, mapear por responsabilidade sem duplicar agentes.



\---



\# 29. TASK GRAPH



```yaml

tasks:



&#x20; - id: T000\_BOOT\_PROJECT

&#x20;   agent: EDITORIAL\_DIRECTOR\_AGENT

&#x20;   depends\_on: \[]

&#x20;   outputs:

&#x20;     - PROJECT\_MANIFEST.yaml

&#x20;     - RUN\_CONFIG.yaml

&#x20;   gate: project\_initialized



&#x20; - id: T010\_INGEST\_SPEC

&#x20;   agent: BOOK\_ARCHITECT\_AGENT

&#x20;   depends\_on:

&#x20;     - T000\_BOOT\_PROJECT

&#x20;   inputs:

&#x20;     - PROJECT\_SPEC.md

&#x20;     - AUTHORIAL\_INTENT.md

&#x20;     - ETHICAL\_BIBLE.md

&#x20;   outputs:

&#x20;     - normalized\_project\_context.json

&#x20;   gate: sources\_normalized



&#x20; - id: T020\_BUILD\_BOOK\_BIBLE

&#x20;   agent: BOOK\_ARCHITECT\_AGENT

&#x20;   depends\_on:

&#x20;     - T010\_INGEST\_SPEC

&#x20;   outputs:

&#x20;     - BOOK\_BIBLE.md

&#x20;     - STORY\_BIBLE.md

&#x20;     - LIVING\_BOOK\_BIBLE.md

&#x20;   gate: book\_bible\_approved



&#x20; - id: T030\_BUILD\_WORLD

&#x20;   agent: WORLD\_BUILDING\_AGENT

&#x20;   depends\_on:

&#x20;     - T020\_BUILD\_BOOK\_BIBLE

&#x20;   outputs:

&#x20;     - WORLD\_BIBLE.md

&#x20;     - LANGUAGE\_BIBLE.md

&#x20;     - SYMBOLISM\_BIBLE.md

&#x20;   gate: world\_coherent



&#x20; - id: T035\_VALIDATE\_SCIENCE

&#x20;   agent: SCIENTIFIC\_COHERENCE\_AGENT

&#x20;   depends\_on:

&#x20;     - T030\_BUILD\_WORLD

&#x20;   outputs:

&#x20;     - reviews/scientific/world\_science\_review.md

&#x20;   gate: speculative\_science\_plausible



&#x20; - id: T040\_BUILD\_POLITICAL\_SYSTEM

&#x20;   agent: POLITICAL\_SYSTEM\_AGENT

&#x20;   depends\_on:

&#x20;     - T030\_BUILD\_WORLD

&#x20;   outputs:

&#x20;     - planning/political\_system\_spec.md

&#x20;   gate: political\_system\_coherent



&#x20; - id: T050\_BUILD\_CHARACTERS

&#x20;   agent: CHARACTER\_ARCHITECT\_AGENT

&#x20;   depends\_on:

&#x20;     - T020\_BUILD\_BOOK\_BIBLE

&#x20;     - T030\_BUILD\_WORLD

&#x20;   outputs:

&#x20;     - CHARACTER\_BIBLE.md

&#x20;     - CHARACTER\_ARCS.md

&#x20;   gate: characters\_approved



&#x20; - id: T060\_BUILD\_PLOT

&#x20;   agent: PLOT\_ARCHITECT\_AGENT

&#x20;   depends\_on:

&#x20;     - T040\_BUILD\_POLITICAL\_SYSTEM

&#x20;     - T050\_BUILD\_CHARACTERS

&#x20;   outputs:

&#x20;     - PLOT\_BIBLE.md

&#x20;     - ACT\_STRUCTURE.md

&#x20;     - REVEAL\_MAP.md

&#x20;     - FORESHADOWING\_MAP.md

&#x20;     - EMOTIONAL\_CURVE.md

&#x20;   gate: plot\_approved



&#x20; - id: T070\_BUILD\_TIMELINE

&#x20;   agent: TIMELINE\_AND\_CONTINUITY\_AGENT

&#x20;   depends\_on:

&#x20;     - T060\_BUILD\_PLOT

&#x20;   outputs:

&#x20;     - TIMELINE.md

&#x20;     - CONTINUITY\_BIBLE.md

&#x20;   gate: timeline\_valid



&#x20; - id: T080\_BUILD\_CHAPTER\_BIBLE

&#x20;   agent: PLOT\_ARCHITECT\_AGENT

&#x20;   depends\_on:

&#x20;     - T060\_BUILD\_PLOT

&#x20;     - T070\_BUILD\_TIMELINE

&#x20;   outputs:

&#x20;     - CHAPTER\_BIBLE.md

&#x20;     - SCENE\_MATRIX.md

&#x20;   gate: chapters\_planned



&#x20; - id: T090\_BUILD\_VISUAL\_IDENTITIES

&#x20;   agent: FACE\_AND\_VISUAL\_IDENTITY\_AGENT

&#x20;   depends\_on:

&#x20;     - T050\_BUILD\_CHARACTERS

&#x20;     - T080\_BUILD\_CHAPTER\_BIBLE

&#x20;   outputs:

&#x20;     - VISUAL\_CHARACTER\_IDENTITIES.md

&#x20;   gate: visual\_identities\_approved



&#x20; - id: T100\_BUILD\_IMAGE\_BIOME

&#x20;   agent: IMAGE\_BIOME\_AGENT

&#x20;   depends\_on:

&#x20;     - T030\_BUILD\_WORLD

&#x20;     - T080\_BUILD\_CHAPTER\_BIBLE

&#x20;     - T090\_BUILD\_VISUAL\_IDENTITIES

&#x20;   outputs:

&#x20;     - IMAGE\_BIOME.md

&#x20;     - VISUAL\_LIFE\_SPEC.md

&#x20;     - IMAGE\_PLAN.md

&#x20;   gate: visual\_system\_approved



&#x20; - id: T110\_BUILD\_LIVING\_SOUND

&#x20;   agent: LIVING\_SOUNDTRACK\_ARCHITECT

&#x20;   depends\_on:

&#x20;     - T020\_BUILD\_BOOK\_BIBLE

&#x20;     - T060\_BUILD\_PLOT

&#x20;     - T080\_BUILD\_CHAPTER\_BIBLE

&#x20;   outputs:

&#x20;     - LIVING\_SOUND\_BIBLE.md

&#x20;     - SOUND\_PLAN.md

&#x20;   gate: sound\_system\_approved



&#x20; - id: T120\_GENERATE\_CHAPTER\_PROMPTS

&#x20;   agent: PRIMARY\_WRITER\_AGENT

&#x20;   depends\_on:

&#x20;     - T080\_BUILD\_CHAPTER\_BIBLE

&#x20;     - T070\_BUILD\_TIMELINE

&#x20;   outputs:

&#x20;     - prompts/chapter\_prompts/chapter\_01.md

&#x20;     - prompts/chapter\_prompts/chapter\_24.md

&#x20;   gate: all\_chapter\_prompts\_exist



&#x20; - id: T130\_WRITE\_ACT\_1

&#x20;   agent: CHAPTER\_WRITER\_AGENTS

&#x20;   depends\_on:

&#x20;     - T120\_GENERATE\_CHAPTER\_PROMPTS

&#x20;   chapter\_range: 1-8

&#x20;   outputs:

&#x20;     - drafts/chapter\_drafts/chapter\_01.md

&#x20;     - drafts/chapter\_drafts/chapter\_08.md

&#x20;   gate: act\_1\_written



&#x20; - id: T140\_WRITE\_ACT\_2A

&#x20;   agent: CHAPTER\_WRITER\_AGENTS

&#x20;   depends\_on:

&#x20;     - T120\_GENERATE\_CHAPTER\_PROMPTS

&#x20;   chapter\_range: 9-13

&#x20;   outputs:

&#x20;     - drafts/chapter\_drafts/chapter\_09.md

&#x20;     - drafts/chapter\_drafts/chapter\_13.md

&#x20;   gate: act\_2a\_written



&#x20; - id: T150\_WRITE\_ACT\_2B

&#x20;   agent: CHAPTER\_WRITER\_AGENTS

&#x20;   depends\_on:

&#x20;     - T120\_GENERATE\_CHAPTER\_PROMPTS

&#x20;   chapter\_range: 14-18

&#x20;   outputs:

&#x20;     - drafts/chapter\_drafts/chapter\_14.md

&#x20;     - drafts/chapter\_drafts/chapter\_18.md

&#x20;   gate: act\_2b\_written



&#x20; - id: T160\_WRITE\_ACT\_3

&#x20;   agent: CHAPTER\_WRITER\_AGENTS

&#x20;   depends\_on:

&#x20;     - T120\_GENERATE\_CHAPTER\_PROMPTS

&#x20;   chapter\_range: 19-24

&#x20;   outputs:

&#x20;     - drafts/chapter\_drafts/chapter\_19.md

&#x20;     - drafts/chapter\_drafts/chapter\_24.md

&#x20;   gate: act\_3\_written



&#x20; - id: T170\_FIRST\_MERGE

&#x20;   agent: MERGE\_AND\_INTEGRATION\_AGENT

&#x20;   depends\_on:

&#x20;     - T130\_WRITE\_ACT\_1

&#x20;     - T140\_WRITE\_ACT\_2A

&#x20;     - T150\_WRITE\_ACT\_2B

&#x20;     - T160\_WRITE\_ACT\_3

&#x20;   outputs:

&#x20;     - drafts/integrated/full\_manuscript\_v1.md

&#x20;   gate: manuscript\_integrated



&#x20; - id: T180\_DEVELOPMENTAL\_REVIEW

&#x20;   agent: DEVELOPMENTAL\_EDITOR\_AGENT

&#x20;   depends\_on:

&#x20;     - T170\_FIRST\_MERGE

&#x20;   outputs:

&#x20;     - reviews/developmental/developmental\_review.md

&#x20;   gate: developmental\_review\_complete



&#x20; - id: T190\_PLOT\_REVIEW

&#x20;   agent: PLOT\_REVIEW\_AGENT

&#x20;   depends\_on:

&#x20;     - T170\_FIRST\_MERGE

&#x20;   outputs:

&#x20;     - reviews/developmental/plot\_review.md

&#x20;   gate: plot\_review\_complete



&#x20; - id: T200\_CONTINUITY\_REVIEW

&#x20;   agent: CONTINUITY\_REVIEW\_AGENT

&#x20;   depends\_on:

&#x20;     - T170\_FIRST\_MERGE

&#x20;     - T070\_BUILD\_TIMELINE

&#x20;   outputs:

&#x20;     - reviews/continuity/continuity\_review.md

&#x20;   gate: continuity\_review\_complete



&#x20; - id: T210\_ETHICAL\_REVIEW

&#x20;   agent: ETHICAL\_AND\_SENSITIVITY\_REVIEW\_AGENT

&#x20;   depends\_on:

&#x20;     - T170\_FIRST\_MERGE

&#x20;   outputs:

&#x20;     - reviews/ethical/ethical\_review.md

&#x20;   gate: ethical\_review\_passed



&#x20; - id: T220\_PHILOSOPHICAL\_REVIEW

&#x20;   agent: PHILOSOPHICAL\_REVIEW\_AGENT

&#x20;   depends\_on:

&#x20;     - T170\_FIRST\_MERGE

&#x20;   outputs:

&#x20;     - reviews/philosophical/philosophical\_review.md

&#x20;   gate: themes\_integrated



&#x20; - id: T230\_REVISION\_PASS

&#x20;   agent: PRIMARY\_WRITER\_AGENT

&#x20;   depends\_on:

&#x20;     - T180\_DEVELOPMENTAL\_REVIEW

&#x20;     - T190\_PLOT\_REVIEW

&#x20;     - T200\_CONTINUITY\_REVIEW

&#x20;     - T210\_ETHICAL\_REVIEW

&#x20;     - T220\_PHILOSOPHICAL\_REVIEW

&#x20;   outputs:

&#x20;     - drafts/revised/full\_manuscript\_v2.md

&#x20;   gate: structural\_revisions\_applied



&#x20; - id: T240\_STYLE\_REVIEW

&#x20;   agent: STYLE\_REVIEW\_AGENT

&#x20;   depends\_on:

&#x20;     - T230\_REVISION\_PASS

&#x20;   outputs:

&#x20;     - reviews/style/style\_review.md

&#x20;   gate: style\_consistent



&#x20; - id: T250\_GRAMMAR\_REVIEW

&#x20;   agent: GRAMMAR\_REVIEW\_AGENT

&#x20;   depends\_on:

&#x20;     - T240\_STYLE\_REVIEW

&#x20;   outputs:

&#x20;     - reviews/grammar/grammar\_review.md

&#x20;   gate: language\_correct



&#x20; - id: T260\_FINAL\_TEXT\_MERGE

&#x20;   agent: MERGE\_AND\_INTEGRATION\_AGENT

&#x20;   depends\_on:

&#x20;     - T250\_GRAMMAR\_REVIEW

&#x20;   outputs:

&#x20;     - drafts/final/O\_Jardim\_dos\_Doze\_Final.md

&#x20;     - drafts/final/O\_Jardim\_dos\_Doze\_Final.txt

&#x20;   gate: final\_text\_locked



&#x20; - id: T270\_GENERATE\_IMAGE\_PROMPTS

&#x20;   agent: CHAPTER\_IMAGE\_AGENT

&#x20;   depends\_on:

&#x20;     - T100\_BUILD\_IMAGE\_BIOME

&#x20;     - T260\_FINAL\_TEXT\_MERGE

&#x20;   outputs:

&#x20;     - prompts/image\_prompts/chapter\_01.md

&#x20;     - prompts/image\_prompts/chapter\_24.md

&#x20;   gate: image\_prompts\_complete



&#x20; - id: T280\_GENERATE\_IMAGES

&#x20;   agent: CHAPTER\_IMAGE\_AGENT

&#x20;   depends\_on:

&#x20;     - T270\_GENERATE\_IMAGE\_PROMPTS

&#x20;   outputs:

&#x20;     - assets/chapter\_images/chapter\_01.jpg

&#x20;     - assets/chapter\_images/chapter\_24.jpg

&#x20;   gate: twenty\_four\_images\_exist



&#x20; - id: T290\_VISUAL\_CONTINUITY\_REVIEW

&#x20;   agent: VISUAL\_CONTINUITY\_AGENT

&#x20;   depends\_on:

&#x20;     - T280\_GENERATE\_IMAGES

&#x20;   outputs:

&#x20;     - reviews/visual/visual\_continuity\_review.md

&#x20;   gate: visuals\_approved



&#x20; - id: T300\_GENERATE\_SOUND\_PROMPTS

&#x20;   agent: LIVING\_SOUND\_COMPOSER\_AGENT

&#x20;   depends\_on:

&#x20;     - T110\_BUILD\_LIVING\_SOUND

&#x20;     - T260\_FINAL\_TEXT\_MERGE

&#x20;   outputs:

&#x20;     - prompts/sound\_prompts/chapter\_01.md

&#x20;     - prompts/sound\_prompts/chapter\_24.md

&#x20;     - prompts/sound\_prompts/main\_theme.md

&#x20;   gate: sound\_prompts\_complete



&#x20; - id: T310\_SOUND\_CONTINUITY\_REVIEW

&#x20;   agent: SOUND\_CONTINUITY\_AGENT

&#x20;   depends\_on:

&#x20;     - T300\_GENERATE\_SOUND\_PROMPTS

&#x20;   outputs:

&#x20;     - reviews/sound/sound\_continuity\_review.md

&#x20;   gate: sound\_system\_consistent



&#x20; - id: T320\_BUILD\_PAGE\_SYSTEM

&#x20;   agent: PAGE\_ARCHITECT\_AGENT

&#x20;   depends\_on:

&#x20;     - T260\_FINAL\_TEXT\_MERGE

&#x20;     - T290\_VISUAL\_CONTINUITY\_REVIEW

&#x20;   outputs:

&#x20;     - PAGE\_BIBLE.md

&#x20;     - KDP\_BIBLE.md

&#x20;   gate: page\_system\_ready



&#x20; - id: T330\_BUILD\_DOCX

&#x20;   agent: DOCX\_FORMATTER\_AGENT

&#x20;   depends\_on:

&#x20;     - T320\_BUILD\_PAGE\_SYSTEM

&#x20;   outputs:

&#x20;     - outputs/docx/O\_Jardim\_dos\_Doze\_KDP.docx

&#x20;     - outputs/docx/O\_Jardim\_dos\_Doze\_Ebook.docx

&#x20;   gate: docx\_generated



&#x20; - id: T340\_KDP\_VALIDATION

&#x20;   agent: KDP\_COMPLIANCE\_AGENT

&#x20;   depends\_on:

&#x20;     - T330\_BUILD\_DOCX

&#x20;   outputs:

&#x20;     - reviews/final\_qa/kdp\_validation.md

&#x20;   gate: kdp\_validation\_passed



&#x20; - id: T350\_ORIGINALITY\_AND\_LEGAL\_REVIEW

&#x20;   agent: LEGAL\_AND\_ORIGINALITY\_AGENT

&#x20;   depends\_on:

&#x20;     - T260\_FINAL\_TEXT\_MERGE

&#x20;     - T290\_VISUAL\_CONTINUITY\_REVIEW

&#x20;   outputs:

&#x20;     - reviews/final\_qa/originality\_review.md

&#x20;   gate: originality\_approved



&#x20; - id: T360\_FINAL\_QA

&#x20;   agent: FINAL\_QA\_AGENT

&#x20;   depends\_on:

&#x20;     - T310\_SOUND\_CONTINUITY\_REVIEW

&#x20;     - T340\_KDP\_VALIDATION

&#x20;     - T350\_ORIGINALITY\_AND\_LEGAL\_REVIEW

&#x20;   outputs:

&#x20;     - reviews/final\_qa/final\_qa\_report.md

&#x20;   gate: project\_approved



&#x20; - id: T370\_DELIVERY

&#x20;   agent: DELIVERY\_AGENT

&#x20;   depends\_on:

&#x20;     - T360\_FINAL\_QA

&#x20;   outputs:

&#x20;     - outputs/reports/FINAL\_DELIVERY\_REPORT.md

&#x20;     - outputs/reports/FILE\_MANIFEST.json

&#x20;     - outputs/O\_JARDIM\_DOS\_DOZE\_DELIVERY.zip

&#x20;   gate: delivery\_complete

```



\---



\# 30. QUALITY GATES



\## GATE 1 — Concept Integrity



O projeto só avança se:



\* o contraste entre inocência visual e brutalidade estiver preservado;

\* o horror for social, político e psicológico;

\* não houver erotização.



\## GATE 2 — World Coherence



Validar:



\* regras da Síndrome;

\* função da Anilina-12;

\* idade real;

\* envelhecimento;

\* mortalidade;

\* reprodução institucional;

\* cronologia;

\* sistema político.



\## GATE 3 — Character Coherence



Validar:



\* desejos;

\* feridas;

\* segredos;

\* mudanças;

\* destinos;

\* relações;

\* vozes.



\## GATE 4 — Chapter Quality



Cada capítulo precisa:



\* alterar a situação narrativa;

\* conter conflito;

\* possuir pelo menos uma imagem memorável;

\* evitar repetição;

\* terminar com impulso para o próximo.



\## GATE 5 — Ethical Safety



Aprovação obrigatória sem exceção.



\## GATE 6 — Manuscript Completeness



\* 24 capítulos;

\* mínimo de 60.000 palavras;

\* todos os atos completos;

\* frase final preservada ou melhorada com aprovação editorial;

\* ausência de placeholders.



\## GATE 7 — Visual Completeness



\* 24 imagens;

\* 24 prompts;

\* identidade visual consistente;

\* revisão ética visual aprovada.



\## GATE 8 — DOCX/KDP



\* sumário funcional;

\* estilos corretos;

\* imagens inseridas;

\* capítulos em novas páginas;

\* arquivo abre sem erro;

\* sem fontes ausentes críticas;

\* sem links quebrados;

\* sem imagens deformadas.



\---



\# 31. REGRAS DE AUTONOMIA DO CODEX



O Codex pode:



\* ampliar cenas;

\* aprofundar personagens;

\* criar personagens secundários;

\* melhorar diálogos;

\* ajustar títulos de capítulos;

\* redistribuir pequenas revelações;

\* criar instituições secundárias;

\* melhorar a plausibilidade científica;

\* aprimorar simbolismo.



O Codex não pode, sem registro e aprovação do Diretor Editorial:



\* alterar o título;

\* eliminar Nina, Bento, Ícaro, Helena, Abel ou Caio;

\* transformar a história em literatura juvenil;

\* incluir sexualização;

\* remover a Anilina-12;

\* remover o Projeto Recreio;

\* oferecer final completamente feliz;

\* destruir a ambiguidade final;

\* transformar Abel em vilão sem convicções;

\* apresentar o crescimento como solução simples;

\* retirar a imagem por capítulo;

\* retirar o DOCX;

\* retirar o sumário;

\* retirar o LIVING SOUND;

\* alterar o idioma principal.



\---



\# 32. ESTRATÉGIA DE CONTEXTO



Caso o contexto do modelo seja insuficiente para escrever o livro inteiro em uma única execução:



1\. construir todas as bíblias;

2\. bloquear os arquivos canônicos;

3\. escrever por ato;

4\. revisar cada ato;

5\. gerar resumo canônico de continuidade;

6\. iniciar o ato seguinte usando bíblias e resumo;

7\. realizar merge final;

8\. revisar o manuscrito completo.



Nunca substituir capítulos completos por resumos devido a limite de contexto.



Nunca declarar o projeto concluído com capítulos faltando.



\---



\# 33. CHECKPOINTS



Criar checkpoints após:



\* conclusão das bíblias;

\* conclusão do Ato I;

\* conclusão do Ato II;

\* conclusão do Ato III;

\* primeira integração;

\* revisão estrutural;

\* bloqueio do texto;

\* conclusão das imagens;

\* conclusão do DOCX;

\* validação final.



Formato:



```text

/logs/checkpoints/

&#x20; checkpoint\_01\_bibles\_complete.json

&#x20; checkpoint\_02\_act\_1\_complete.json

&#x20; checkpoint\_03\_act\_2\_complete.json

&#x20; checkpoint\_04\_act\_3\_complete.json

&#x20; checkpoint\_05\_text\_locked.json

&#x20; checkpoint\_06\_visuals\_complete.json

&#x20; checkpoint\_07\_docx\_complete.json

&#x20; checkpoint\_08\_delivery\_complete.json

```



\---



\# 34. ENTREGÁVEIS FINAIS



\## Manuscrito



\* Markdown;

\* TXT;

\* DOCX KDP;

\* DOCX ebook;

\* PDF de interior, quando tecnicamente confiável.



\## Imagens



\* 24 imagens JPG;

\* 24 prompts;

\* fichas visuais dos personagens;

\* relatório de continuidade visual.



\## Som



\* LIVING SOUND BIBLE;

\* 24 prompts sonoros;

\* tema principal;

\* motivos de personagens;

\* orientação de audiobook e teaser.



\## Capa



\* briefing;

\* prompt principal;

\* prompts alternativos;

\* capa frontal JPG, se houver geração;

\* especificação para capa completa, condicionada ao número final de páginas.



\## Marketing



\* descrição Amazon de até 4.000 caracteres;

\* sinopse curta;

\* 7 palavras-chave;

\* frase de capa;

\* 5 posts ou stories;

\* teaser comercial de 10 segundos;

\* argumento de adaptação audiovisual.



\## Relatórios



\* revisão estrutural;

\* revisão de trama;

\* revisão de continuidade;

\* revisão ética;

\* revisão científica;

\* revisão política;

\* revisão filosófica;

\* revisão de estilo;

\* revisão gramatical;

\* revisão visual;

\* revisão sonora;

\* validação KDP;

\* originalidade;

\* QA final;

\* entrega final.



\---



\# 35. DEFINITION OF DONE



O projeto somente será marcado como `DONE` quando:



```yaml

definition\_of\_done:

&#x20; manuscript:

&#x20;   chapters: 24

&#x20;   minimum\_words: 60000

&#x20;   placeholders: 0

&#x20;   unfinished\_scenes: 0

&#x20; images:

&#x20;   chapter\_images: 24

&#x20;   image\_prompts: 24

&#x20;   ethical\_visual\_approval: true

&#x20; sound:

&#x20;   living\_sound\_bible: true

&#x20;   chapter\_sound\_prompts: 24

&#x20; formatting:

&#x20;   title\_page: true

&#x20;   copyright\_page: true

&#x20;   table\_of\_contents: true

&#x20;   chapter\_page\_breaks: true

&#x20;   chapter\_images\_inserted: true

&#x20;   docx\_kdp: true

&#x20;   docx\_ebook: true

&#x20; reviews:

&#x20;   developmental: passed

&#x20;   plot: passed

&#x20;   continuity: passed

&#x20;   ethical: passed

&#x20;   philosophical: passed

&#x20;   style: passed

&#x20;   grammar: passed

&#x20;   visual: passed

&#x20;   kdp: passed

&#x20;   originality: passed

&#x20;   final\_qa: passed

&#x20; delivery:

&#x20;   zip\_created: true

&#x20;   manifest\_created: true

&#x20;   delivery\_report\_created: true

```



\---



\# 36. RESULTADO FINAL ESPERADO



O resultado deve ser um romance adulto, perturbador, visualmente memorável e comercialmente forte, no qual a infância não é utilizada como objeto de exploração, mas como símbolo político sequestrado por uma sociedade incapaz de amadurecer.



A última sensação do leitor deve ser:



Talvez crescer ainda seja possível.



Mas o poder já aprendeu a vender até mesmo a revolução.



