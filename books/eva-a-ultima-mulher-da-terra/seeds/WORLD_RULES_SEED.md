# World Rules Seed — Eva: A Última Mulher da Terra

Regras cruas de mundo, física social e cronologia. Este documento é a fonte
de verdade numérica e temporal que o `CANON_GUARDIAN` deve formalizar em
`canon/CANON_REGISTRY.yaml`. Nenhum destes números precisa aparecer citado
exatamente no manuscrito fora dos interlúdios de contador — eles existem para
manter consistência entre capítulos escritos em ondas diferentes.

## 1. O fenômeno (Dia Zero)

- "Dia Zero" é o nascimento de Eva Duarte, em Campo Alegre. A partir desse
  instante, todo nascimento humano registrado no mundo é do sexo masculino.
- Gestações em curso no momento do Dia Zero completam normalmente (algumas já
  eram meninas, confirmando que o corte é abrupto, não gradual).
- Mulheres já nascidas continuam existindo, envelhecendo e podendo engravidar
  normalmente enquanto férteis — apenas os bebês que geram são todos meninos.
- Isso significa que a população **feminina** entra em queda estrutural
  imediatamente (sem reposição), enquanto a população **humana total** continua
  crescendo por algumas décadas (meninos nascendo normalmente de mães ainda
  férteis) antes de entrar em colapso quando essas mães encerram a vida fértil
  e, décadas depois, morrem de velhice.
- Nenhuma causa é jamais confirmada. Hipóteses que personagens podem levantar,
  defender e abandonar ao longo da obra (nenhuma privilegiada pelo narrador):
  agente viral latente; mutação no cromossomo Y de propagação inexplicável;
  intervenção divina (Nova Eva); experimento militar ou científico vazado;
  fenômeno ambiental/epigenético; simples limite estatístico da espécie que
  "decidiu" parar; hipótese alienígena (marginal, tratada com ceticismo no
  próprio mundo); hipótese de que o fenômeno é sintoma, não causa, de algo
  maior ainda não observado.

## 2. Cronologia mestra (anos após o Dia Zero = idade de Eva)

| Ano/idade | Marco |
|---|---|
| 0 | Nascimento de Eva. Ninguém sabe ainda. |
| +1 a +2 | Primeiras suspeitas regionais (pediatras, cartórios). |
| +2 | Confirmação estatística mundial: nenhum nascimento feminino em lugar nenhum. Eva é identificada como a última. Imprensa mundial. |
| +5 a +10 | Onda de ausência sobe da creche ao ensino fundamental. Primeiros protocolos de segurança formais. |
| +10 a +15 | Onda atinge o ensino médio. Primeiros tratados sobre material genético. Primeiras seitas Evistas. |
| +15 a +20 | Debate constitucional sobre reserva reprodutiva compulsória. Maioridade de Eva e recusa legal. |
| +20 a +30 | Eva tenta vida civil comum; fracassa repetidamente; movimento Eva Livre nasce e cresce. |
| +30 a +50 | Eva torna-se cientista. Grande evento: embrião XX viável nasce menino (~ano +42). Mudança de pergunta. |
| +45 a +60 | Últimas mulheres nascidas antes do Dia Zero encerram a vida fértil (menopausa da última geração natural). Natalidade total começa a cair estruturalmente. |
| +50 a +80 | "Mundo dos homens": automação necessária, cidades encolhendo, novas famílias. População humana total em queda acelerada. |
| +60 a +100 | A geração de mulheres nascida pouco antes do Dia Zero atinge expectativa de vida e começa a morrer em massa. Fenômeno cultural do "ranking das mulheres mais jovens vivas". |
| ~+90 a +110 | Eva ultrapassa a expectativa de vida humana documentada (primeira menção pública da sua longevidade como segunda anomalia, ~ano 90). Últimas dezenas de mulheres. |
| ~+108 a +112 | Morte da penúltima mulher viva. Eva torna-se oficialmente "a última mulher da Terra". |
| +110 a +137 | Colapso final de governos e infraestrutura. População humana total cai de milhões a centenas. |
| ~+130 a +137 | Restam dezenas, depois poucos seres humanos. Tomás Rocha emerge como companheiro final de Eva. |
| +137 | Morte de Tomás Rocha. Eva torna-se a única pessoa viva. O contador de população humana para em 1. |
| +137 a +147 | "A Era de Eva": década de solidão total. A Terra recupera-se ecologicamente sem gestão humana. |
| 147 | Idade final de Eva. Incidente do deserto: dor, náusea, "Não...", pássaros, desmaio. Fim do livro sem confirmação de causa, gravidez ou morte. |

O número 147 nunca recebe explicação textual. Não deve ser destacado como
significativo por nenhum personagem ou pelo narrador.

## 3. Contador canônico — população feminina estimada

Usar exatamente esta sequência, distribuída como interlúdios entre os
capítulos indicados. Formato: página quase vazia, apenas o rótulo e o número,
sem comentário editorial.

| Interlúdio | Após o capítulo | Valor |
|---|---|---|
| CF-1 | 5 | 3.912.882.441 |
| CF-2 | 9 | 2.704.119.870 |
| CF-3 | 13 | 1.106.771.204 |
| CF-4 | 17 | 77.410.083 |
| CF-5 | 22 | 913.444 |
| CF-6 | 27 | 18.002 |
| CF-7 | 31 | 814 |
| CF-8 | 33 | 72 |
| CF-9 | 34 (antes da morte da penúltima) | 2 |
| CF-10 | 34 (depois da morte da penúltima) | 1 — EVA |

A partir de CF-10, o contador de população feminina nunca mais aparece:
Eva é, a partir desse ponto, o próprio contador de população humana total.

## 4. Contador canônico — população humana estimada

Inicia no capítulo 36 (colapso final de governos) e reaparece de forma cada
vez mais espaçada, com cada vez menos texto ao redor.

| Interlúdio | Após o capítulo | Valor |
|---|---|---|
| CH-1 | 36 | ~340.000.000 |
| CH-2 | 37 | ~2.100.000 |
| CH-3 | 38 | 41 |
| CH-4 | 39 (antes da morte de Tomás) | 2 |
| CH-5 | 39 (depois da morte de Tomás) | 1 — EVA |
| CH-6 | 40 | 1 |
| CH-7 | 41 | 1 |
| CH-8 | 42, antes do incidente final | 1 |
| CH-9 (final absoluto do livro) | 42, última página | POPULAÇÃO HUMANA ESTIMADA: 1 — NASCIMENTOS HUMANOS NO ÚLTIMO ANO: 0 |

O valor final é 1. Nunca 0, nunca 2. `validators/validate_final_manuscript.py`
reprova o manuscrito congelado se esta regra for violada.

## 5. Geografia e instituições

- Eva nasce em **Campo Alegre**, cidade fictícia de interior (Brasil).
  Realocada, por segurança, a partir dos ~6 anos para o **Instituto
  Meridian**, campus internacional de pesquisa e proteção sob mandato da ONU,
  em local neutro (Alpes suíços, fictício o suficiente para não amarrar a
  geopolítica real).
- **Conselho Mundial de Continuidade Humana (CMCH)**: corpo multilateral
  criado nos primeiros dez anos após o Dia Zero, dirigido por Amos Weller.
  Controla tratados sobre material genético, bancos de óvulos e propostas de
  reserva reprodutiva. Não criou o fenômeno; explora e administra a crise.
- **Movimento Eva Livre**: rede internacional de ativismo por autonomia
  corporal, fundada por Solenne Reyes quando Eva tem ~17 anos.
- **Continuacionistas**: corrente política e filosófica, não um partido único,
  que prioriza sobrevivência da espécie sobre autonomia individual em casos
  extremos; existe dentro de democracias e como doutrina de estado em regimes
  autoritários específicos (nenhum nomeado com país real).
- **Evistas**: movimento religioso que interpreta Eva como "Nova Eva" —
  internamente dividido entre veneração messiânica e leitura apenas simbólica.
  Voz principal: Bispo Ionatã Prade.
- **Naturalistas**: corrente filosófico-religiosa que prega aceitação da
  extinção como processo natural, não tragédia. Voz principal: Irmã Ângela
  Cruz (também dentro de tradição cristã, em polêmica direta com Prade) e o
  filósofo secular Dr. Wren Halloway.

## 6. Tecnologia especulativa (aplicar o protocolo de 4 passos da Constituição)

- Bancos internacionais de óvulos e preservação genética (~ano 15-20).
- Gametogênese artificial in vitro — tentativas repetidas, falhas parciais
  (ano ~30-40).
- Embrião XX geneticamente confirmado, gestado por voluntária (Renata
  Sobral), nasce fenotipicamente menino (Theo) por volta do ano 42 — evento
  central "Menino". Nenhuma explicação definitiva é alcançada: os exames
  pré-natais mostravam XX; o exame pós-natal mostra características
  fenotípicas masculinas sem cariótipo XY completo — uma anomalia dentro da
  anomalia, nunca resolvida.
- Úteros artificiais experimentais (ano ~48-55) — avanço técnico real, sem
  impacto no problema central.
- Automação civilizacional necessária a partir do ano ~55-60, por escassez de
  mão de obra, não por escolha.

## 7. O motivo dos pássaros — inventário exato de uso permitido

Espécie fictícia de referência: **andorinhões-de-vidro**, ave migratória de
voo alto e silencioso. Aparecem, sem comentário do narrador além de
observação sensorial, nestes momentos e apenas nestes:

1. Capítulo 1 — no instante do nascimento de Eva (menção mínima, no ambiente
   externo ao hospital, nunca dentro do quarto).
2. Capítulo 4 — no dia em que a identidade de Eva como "a última" se torna
   pública.
3. Capítulo 17 — no dia da maioridade legal de Eva.
4. Capítulo 26 — no dia do nascimento de Theo ("Menino").
5. Capítulo 34 — no dia da morte da penúltima mulher viva.
6. Capítulo 39 — no momento da morte de Tomás Rocha.
7. Capítulo 41 e 42 — no deserto final, com maior presença sensorial e a
   palavra "esperando" reservada exclusivamente para a última aparição do
   livro.

Regras absolutas: nunca contados com precisão superior a "um bando", "dezenas
demais para contar", ou equivalente vago; nunca descritos como
sobrenaturais; nunca associados explicitamente a nenhuma religião do livro;
nunca mencionados por nenhum cientista como objeto de estudo; a palavra
"esperando" (ou sinônimo com a mesma implicação de intenção) é reservada para
a última linha do Capítulo 42 e não pode ser usada sobre os pássaros em
nenhum outro ponto do manuscrito.

## 8. Pistas de releitura (plantar, nunca resolver)

Distribuir discretamente ao longo do manuscrito, sem nunca conectá-las
explicitamente entre si nem com o desfecho:

- Capítulo 2 ou 3: um exame pediátrico de rotina de Eva registra uma
  variação hormonal "sem significado clínico aparente" — nunca mais
  investigada até muito mais tarde.
- Capítulo 9 ou 11: Eva se recupera de uma doença comum da infância mais
  rápido do que o esperado; ninguém comenta além de "sorte".
- Capítulo 23 ou 24: ao entrar para a pesquisa, Eva descobre que uma amostra
  biológica sua, coletada na infância, foi classificada e arquivada sob um
  protocolo que ninguém sabe explicar quem criou.
- Capítulo 27 ("A Pergunta Errada"): Eva, estudando a si mesma, encontra uma
  anomalia genética própria não catalogada em nenhuma literatura científica —
  o ponto exato em que a pergunta do livro vira. Isto é o giro central e deve
  ser tratado como descoberta real, não bombástica.
- Capítulo 31 ("Recorde"): um pesquisador aposentado menciona, en passant,
  ter visto "o mesmo padrão" em dados antigos de longevidade excepcional
  registrados décadas antes do Dia Zero — nunca mais citado.
- Capítulo 37: Eva encontra, entre pertences antigos dos pais, uma
  observação informal (carta, diário, bilhete) de que ela "quase não chorou"
  ao nascer — detalhe deixado sem peso aparente.
- Capítulo 41-42: os padrões dos andorinhões-de-vidro (ver seção 7) são a
  última pista, nunca verbalizada como pista.

Nenhum agente pode transformar estas pistas em explicação. Elas existem para
recompensa de releitura, não para resolução.

## 9. Regras de corpo e realismo médico

Eva envelhece de forma visível e dolorosa em todas as partes tardias do
livro: rugas, perda de força, fragilidade óssea, falhas de memória, fadiga.
Nenhuma cena pode retratá-la como eternamente jovem. Sua longevidade é
perturbadora precisamente porque o corpo dela mostra o tempo passando —
apenas não termina quando deveria.
