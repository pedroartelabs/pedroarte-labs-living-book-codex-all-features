# World Rules Seed — Motor de Livros Vivos

Este é um livro de não-ficção. As "regras de mundo" aqui não descrevem uma
realidade ficcional — descrevem os limites factuais que o texto não pode
ultrapassar ao falar do motor.

## O que o motor é, de fato

- Um gerador de grafo de tarefas em Python puro (a etapa de composição não faz
  nenhuma chamada de modelo de linguagem).
- Um conjunto de mais de sessenta personas de agente (arquivos de instrução
  curtos), cada uma com um papel e, desde a rodada de dosagem de custo, um
  tier de modelo declarado.
- Um formato de execução onde a produção real do texto, das imagens e da
  mídia acontece dentro de uma sessão de agente de código (Claude Code, Codex
  ou equivalente) interpretando esse grafo.

## O que o motor não é

- Não é uma inteligência geral autônoma. Não decide sozinho o que escrever
  sem um pacote de livro (briefing, canon, regras) definido por um humano.
- Não tem consciência. Linguagem como "o motor respira" ou "o guardião
  protege" é editorial, não literal.
- Não gera imagem ou áudio por conta própria — depende de ferramentas
  externas (uma API de geração de imagem, por exemplo) chamadas por código
  explícito.

## Disciplina de precisão numérica

Quando o livro citar números sobre o próprio motor (quantidade de agentes,
de tarefas, de portões de validação, resultado de testes de dosagem de
custo), esses números devem vir da arquitetura real do repositório, não de
estimativa arredondada para soar mais impressionante.
