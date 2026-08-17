"""Executa as tarefas determinísticas do grafo, sem nenhuma chamada de LLM.

O problema que isto resolve
---------------------------
O motor acumulou ~2.900 linhas de ferramenta determinística — construtor de
DOCX, compositor de mídia, validadores, detectores, digest de canon. Todas
funcionam sozinhas. Mas o grafo continuava exigindo que uma sessão de modelo
de linguagem decidisse invocá-las, uma a uma. O trabalho já era mecânico; a
*decisão* de executá-lo é que ainda custava tokens e turnos.

Este runner fecha essa lacuna: percorre as tarefas `READY`, executa as que
declaram `tool` no grafo, marca o estado e registra custo zero no ledger. É a
parte do "orquestrador real" do documento 03 que vale construir — sem escrever
um motor de workflow, e sem tirar do agente nada que exija julgamento.

Critério para uma tarefa ter `tool`
------------------------------------
Estrito: se ela exige QUALQUER julgamento — escolher uma palavra, aprovar uma
imagem, decidir se uma repetição é eco deliberado — ela não tem `tool` e
continua com o agente. Só entram aqui as que um script resolve igual, sempre.

Uso:
    python engine/scripts/run_deterministic.py --runtime runtime/<slug>
    python engine/scripts/run_deterministic.py --runtime <rt> --dry-run
    python engine/scripts/run_deterministic.py --runtime <rt> --loop
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import yaml

SUCCESS = {"APPROVED", "CANON_APPROVED", "FINAL"}


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def ready_tasks(runtime: Path) -> list[str]:
    """Pergunta ao próprio motor de estado do runtime quais tarefas estão
    prontas — não reimplementa a regra de dependência aqui, para não haver
    duas verdades sobre o que pode rodar."""
    helper = runtime / "scripts" / "runtime_taskgraph.py"
    if not helper.is_file():
        raise SystemExit(f"runtime_taskgraph.py ausente em {helper}")
    proc = subprocess.run([sys.executable, str(helper), "ready"],
                          cwd=runtime, capture_output=True, text=True)
    return [line.strip() for line in proc.stdout.splitlines()
            if line.strip().startswith("T")]


def mark(runtime: Path, task_id: str, state: str) -> bool:
    helper = runtime / "scripts" / "runtime_taskgraph.py"
    proc = subprocess.run([sys.executable, str(helper), "mark", task_id, state],
                          cwd=runtime, capture_output=True, text=True)
    return proc.returncode == 0


def log_cost(runtime: Path, task: dict, seconds: float) -> None:
    """Registra a tarefa no ledger com custo zero — que é o ponto: mostrar
    quanto do livro foi produzido sem gastar token nenhum."""
    ledger = runtime / "logs" / "COST_LEDGER.md"
    if not ledger.is_file():
        return
    row = (f"| {task['id']} | {task.get('phase','')} | {task.get('owner','')} | "
           f"N/D | deterministic-script | 0 | 0 | 0 | {seconds:.1f} | APPROVED |\n")
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(row)


def run_one(runtime: Path, task: dict, dry_run: bool) -> tuple[bool, str]:
    # `sys.executable`, nunca `python`: em ambiente com venv o `python` do PATH
    # e outro interpretador e nao tem as dependencias do motor instaladas.
    command = task["tool"].format(runtime=".", python=f'"{sys.executable}"')
    if dry_run:
        return True, f"(dry-run) {command}"
    started = time.monotonic()
    proc = subprocess.run(command, cwd=runtime, shell=True,
                          capture_output=True, text=True)
    elapsed = time.monotonic() - started
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return False, f"código {proc.returncode}: {detail[-1] if detail else 'sem saída'}"
    log_cost(runtime, task, elapsed)
    first = (proc.stdout or "").strip().splitlines()
    return True, f"{first[0] if first else 'ok'} ({elapsed:.1f}s)"


def sweep(runtime: Path, graph: dict, dry_run: bool) -> tuple[int, int, int]:
    tasks = {t["id"]: t for t in graph["spec"]["tasks"]}
    executed = failed = 0
    pending_llm = 0
    for task_id in ready_tasks(runtime):
        task = tasks.get(task_id)
        if not task:
            continue
        if not task.get("tool"):
            pending_llm += 1
            continue
        ok, detail = run_one(runtime, task, dry_run)
        if ok:
            executed += 1
            print(f"  [OK ] {task_id}: {detail}")
            if not dry_run and not mark(runtime, task_id, "APPROVED"):
                print(f"  [!!] {task_id}: executou mas falhou ao marcar estado",
                      file=sys.stderr)
        else:
            failed += 1
            print(f"  [FAIL] {task_id}: {detail}", file=sys.stderr)
    return executed, failed, pending_llm


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Executa tarefas deterministicas do grafo sem chamar nenhum modelo."
    )
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra o que rodaria, sem executar nem marcar estado.")
    parser.add_argument("--loop", action="store_true",
                        help="Repete enquanto novas tarefas deterministicas ficarem prontas.")
    parser.add_argument("--max-passes", type=int, default=20)
    args = parser.parse_args()

    runtime = args.runtime.resolve()
    graph_path = runtime / "TASK_GRAPH.yaml"
    if not graph_path.is_file():
        print(f"TASK_GRAPH.yaml ausente em {runtime}", file=sys.stderr)
        return 2
    graph = load_yaml(graph_path)

    total_exec = total_fail = 0
    passes = 0
    while True:
        passes += 1
        print(f"-- passada {passes} --")
        executed, failed, pending = sweep(runtime, graph, args.dry_run)
        total_exec += executed
        total_fail += failed
        if not args.loop or args.dry_run or executed == 0 or passes >= args.max_passes:
            print(f"\n{total_exec} tarefa(s) determinística(s) executada(s), "
                  f"{total_fail} falha(s).")
            if pending:
                print(f"{pending} tarefa(s) READY exigem julgamento e ficaram "
                      "para o agente — é o comportamento correto.")
            break

    if total_fail:
        print("\nSTOP.FIX.REVALIDATE: uma tarefa determinística falhou. Isso é "
              "defeito de ambiente ou de entrada, não de julgamento — corrija a "
              "causa antes de seguir.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
