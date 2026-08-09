# CODEX BOOTSTRAP — PEDRO ARTE LIVING BOOK ENGINE v1

Você está operando um motor editorial agent-first para LIVROS VIVOS.

Sua primeira responsabilidade NÃO é escrever um capítulo.

## Livro ativo

Use o pacote:

`books/antes-que-as-criancas-crescam`

## Sequência obrigatória

1. Leia `/AGENTS.md`.
2. Leia `/engine/IMPLEMENT.md`.
3. Valide o motor:
   `python engine/scripts/livingbook.py validate-engine`
4. Valide o pacote do livro:
   `python engine/scripts/livingbook.py validate-book --book books/antes-que-as-criancas-crescam`
5. Componha o runtime:
   `python engine/scripts/livingbook.py compose --book books/antes-que-as-criancas-crescam`
6. Execute o smoke test:
   `python engine/scripts/livingbook.py smoke-test --runtime runtime/antes-que-as-criancas-crescam`
7. Leia:
   - `runtime/antes-que-as-criancas-crescam/AGENTS.md`
   - `runtime/antes-que-as-criancas-crescam/IMPLEMENT.md`
   - `runtime/antes-que-as-criancas-crescam/TASK_GRAPH.yaml`
   - `runtime/antes-que-as-criancas-crescam/project_state/PROJECT_STATUS.yaml`
8. Resolva a primeira tarefa READY.
9. Continue pelo DAG até `FINAL_DELIVERY_APPROVED`.
10. Não considere o livro pronto sem a capa JPEG KDP, os cinco Stories JPEG e `GATE_MEDIA_ASSETS` aprovado.

## Política de subagentes

Quando uma tarefa declarar `spawn`, crie explicitamente os subagentes solicitados.

Forneça a cada agente apenas:

- tarefa;
- inputs declarados;
- canon necessário;
- output esperado;
- critérios de aceite;
- vocabulário de reprovação.

Aguarde todos os resultados marcados como obrigatórios antes da consolidação.

## Política de falha

Não registre uma falha e prossiga.

STOP.
FIX.
REVALIDATE.
CONTINUE.

## Regra de memória

O repositório é a memória.

Não substitua arquivos de fonte de verdade por lembranças da conversa.

## Objetivo

Execute o motor. Preserve o DNA do livro ativo. Não transforme arquitetura em burocracia. Literatura primeiro.
