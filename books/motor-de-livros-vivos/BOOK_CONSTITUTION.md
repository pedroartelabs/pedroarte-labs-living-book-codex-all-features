# Book Constitution — Motor de Livros Vivos

## Propósito

Explicar, para um leitor curioso sobre criação literária e IA (não
necessariamente engenheiro), o que é o Living Book Engine, por que ele existe,
como está estruturado e o que ele já entregou — sem inflar o que ainda é
promessa.

## Audiência

Leitores de não-ficção sobre criatividade, tecnologia editorial e o mercado
de publicação independente. Não pressupõe conhecimento técnico prévio de
arquitetura de software, mas não simplifica a ponto de mentir por omissão.

## Disciplina de fontes (a lei mais importante deste livro)

Este é um livro sobre um sistema real, não uma fábula sobre um sistema
imaginário. Toda afirmação técnica precisa ser rastreável a uma destas
fontes:

1. A arquitetura real do motor (camadas engine/book/runtime, ciclo de vida de
   tarefa, taxonomia de agentes, dosagem de modelo por tier).
2. O catálogo público em universopedroarte.com.br (obras publicadas e em
   desenvolvimento, a marca "Living Book Engine v2", o ecossistema de motores
   irmãos).
3. A presença de autor confirmada em pedroarte.com.br → Amazon.com.br.

Onde uma afirmação for tese do autor/marca (ex.: "livro vivo é um conceito
novo na literatura mundial") em vez de fato técnico verificável, o texto deve
assinalar isso como uma afirmação de autoria — convicção editorial, não
consenso acadêmico. Isso não enfraquece o livro; é o que o torna confiável.

## Tom

Autoral, seguro, didático sem ser condescendente. Entusiasmo pela engenharia
sem propaganda vazia. O livro pode e deve ser orgulhoso da inovação, mas nunca
às custas da precisão sobre o que existe versus o que está em construção.

## Estrutura do argumento

Origem → Arquitetura → Filosofia (o que torna isto "vivo") → Futuro. Cada
capítulo deve poder ser lido de forma independente, mas o livro é mais forte
lido em ordem: a arquitetura do capítulo 2 só faz sentido depois da motivação
do capítulo 1, e o catálogo do capítulo 3 só convence depois de o leitor
entender como as peças do capítulo 2 se encaixam.

## O que este livro não é

Não é um manual de instalação nem uma referência de API. Não é ficção — não
tem personagens no sentido narrativo tradicional; as "entidades" recorrentes
são o motor, seus agentes como categoria, e Pedro Arte como criador. Não é um
white paper de vendas: onde o motor tem limitação conhecida (por exemplo,
etapas que ainda dependem da capacidade da ferramenta hospedeira), o livro diz
isso.
