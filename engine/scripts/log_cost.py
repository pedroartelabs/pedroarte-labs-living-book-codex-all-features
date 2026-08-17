"""Acrescenta uma linha ao logs/COST_LEDGER.md do runtime.

Existe porque o registro manual do ledger é a parte mais fácil de esquecer e
a mais fácil de errar (colunas fora de ordem quebram o cost_report.py).

Fontes reais de telemetria, por tipo de tarefa:
  - tarefa executada por subagente: o retorno do spawn traz tokens e duração;
    passe-os em --tokens-total e --wall-seconds.
  - tarefa de geração de imagem: a resposta da API traz `usage`; passe
    --tokens-in/--tokens-out e --cost-usd quando o preço for conhecido.
  - tarefa executada inline pela própria sessão orquestradora: não há
    introspecção de tokens disponível; use --tokens-total 0 e o valor será
    gravado como N/D, que o cost_report.py trata como zero sem fingir medição.
"""
from __future__ import annotations

import argparse
from pathlib import Path

COLUMNS = 10


def main() -> int:
    p = argparse.ArgumentParser(description="Acrescenta uma linha ao COST_LEDGER.md.")
    p.add_argument("--runtime", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--task", required=True)
    p.add_argument("--phase", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--tier", required=True, choices=["S", "M", "XS", "N/D"])
    p.add_argument("--model", required=True)
    p.add_argument("--tokens-in", default="N/D")
    p.add_argument("--tokens-out", default="N/D")
    p.add_argument("--tokens-total", default=None,
                   help="Se informado e tokens-in/out ausentes, grava o total em tokens_out.")
    p.add_argument("--cost-usd", default="N/D")
    p.add_argument("--wall-seconds", default="N/D")
    p.add_argument("--state", default="APPROVED")
    a = p.parse_args()

    tokens_in, tokens_out = a.tokens_in, a.tokens_out
    if a.tokens_total and tokens_in == "N/D" and tokens_out == "N/D":
        tokens_in, tokens_out = "0", a.tokens_total

    ledger = a.runtime / "logs/COST_LEDGER.md"
    if not ledger.is_file():
        print(f"COST_LEDGER.md ausente em {ledger}")
        return 1

    row = (
        f"| {a.task} | {a.phase} | {a.owner} | {a.tier} | {a.model} | "
        f"{tokens_in} | {tokens_out} | {a.cost_usd} | {a.wall_seconds} | {a.state} |\n"
    )
    if row.count("|") != COLUMNS + 1:
        print("Linha malformada; abortando para nao corromper o ledger.")
        return 1

    with ledger.open("a", encoding="utf-8") as fh:
        fh.write(row)
    print(f"ledger += {a.task} ({a.tier}/{a.model})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
