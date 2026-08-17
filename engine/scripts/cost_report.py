from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

LEDGER_RELATIVE_PATH = Path("logs/COST_LEDGER.md")
COLUMNS = [
    "task_id",
    "phase",
    "owner",
    "model_tier",
    "model_actual",
    "tokens_in",
    "tokens_out",
    "cost_usd",
    "wall_seconds",
    "state",
]
NUMERIC_COLUMNS = {"tokens_in", "tokens_out", "cost_usd", "wall_seconds"}


def parse_ledger(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != len(COLUMNS):
            continue
        if cells[0].lower() == "task_id":
            continue  # header row
        if set("".join(cells)) <= {"-", " "}:
            continue  # separator row (|---|---|...)
        rows.append(dict(zip(COLUMNS, cells)))
    return rows


def to_number(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def load_pricing(runtime: Path) -> dict[str, dict[str, float]]:
    """Le a tabela de precos de MODEL_TIERS.yaml, se disponivel."""
    for candidate in (runtime / "MODEL_TIERS.yaml", Path(__file__).resolve().parents[1] / "MODEL_TIERS.yaml"):
        if candidate.is_file():
            try:
                import yaml
                data = yaml.safe_load(candidate.read_text(encoding="utf-8"))
                return data.get("spec", {}).get("pricing_usd_per_mtok", {}) or {}
            except Exception:
                return {}
    return {}


def derive_cost(row: dict[str, str], pricing: dict[str, dict[str, float]]) -> float:
    """Se a linha nao trouxe cost_usd, calcula a partir de tokens + tabela de precos."""
    declared = to_number(row.get("cost_usd", ""))
    if declared:
        return declared
    price = pricing.get(row.get("model_actual", ""))
    if not price:
        return 0.0
    tin = to_number(row.get("tokens_in", ""))
    tout = to_number(row.get("tokens_out", ""))
    return (tin * price.get("input", 0) + tout * price.get("output", 0)) / 1_000_000


def aggregate(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, float]]:
    totals: dict[str, dict[str, float]] = defaultdict(lambda: {c: 0.0 for c in NUMERIC_COLUMNS} | {"count": 0})
    for row in rows:
        bucket = totals[row.get(key) or "(sem valor)"]
        bucket["count"] += 1
        for col in NUMERIC_COLUMNS:
            bucket[col] += to_number(row.get(col, ""))
    return dict(totals)


def print_table(title: str, totals: dict[str, dict[str, float]]) -> None:
    print(f"\n-- {title} --")
    if not totals:
        print("  (sem dados)")
        return
    # Ordena por custo quando ha custo; senao por tokens (a telemetria mais
    # confiavel enquanto o preco por modelo nao esta cadastrado).
    has_cost = any(t["cost_usd"] for t in totals.values())
    key_fn = (lambda k: -totals[k]["cost_usd"]) if has_cost else (lambda k: -totals[k]["tokens_out"])
    for key in sorted(totals, key=key_fn):
        t = totals[key]
        print(
            f"  {key:<30} n={int(t['count']):<4} "
            f"tokens={int(t['tokens_in'] + t['tokens_out']):<9} "
            f"cost_usd={t['cost_usd']:<9.4f} seg={int(t['wall_seconds'])}"
        )


# Atribuicao por artefato de negocio: responde "quanto custou cada capitulo",
# "quanto custou a capa", "quanto custou a midia". A chave e derivada do
# task_id, que no motor ja codifica o artefato.
ARTIFACT_RULES = [
    (r"T1\d\dA?_?.*CHAPTER_(\d+)|T15\d[ABC]_.*CHAPTER_(\d+)", lambda m: f"capitulo_{m.group(1) or m.group(2)}"),
    (r"T4(\d\d)_IMAGE|T4(\d\d)_FACE_QA|T4(\d\d)_CONTINUITY_QA", lambda m: f"imagem_cap_{int(m.group(1) or m.group(2) or m.group(3))}"),
    (r"T801_KDP_BOOK_COVER", lambda m: "capa_kdp"),
    (r"T802_INSTAGRAM_STORIES", lambda m: "stories_instagram"),
    (r"T800_MEDIA_PACKAGE", lambda m: "midia_texto_kdp"),
    (r"T70\d|T699", lambda m: "docx_kdp"),
    (r"T2\d\d_", lambda m: "waves_escrita"),
    (r"T3\d\d", lambda m: "integracao_revisao"),
    (r"T0\d\d|T01\d", lambda m: "canon_bootstrap"),
    (r"T03\d|T04\d", lambda m: "living_book"),
    (r"T6\d\d", lambda m: "legal"),
    (r"T80[345]", lambda m: "entrega"),
]


def artifact_of(task_id: str) -> str:
    import re as _re
    for pattern, namer in ARTIFACT_RULES:
        m = _re.match(pattern, task_id)
        if m:
            return namer(m)
    return "outros"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lê logs/COST_LEDGER.md e imprime custo total, por fase, por agente e por model_tier. "
        "Não faz nenhuma chamada de LLM: é leitura e soma de um arquivo de texto."
    )
    parser.add_argument(
        "--runtime",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Diretório raiz do runtime; por padrão, o runtime que contém este script.",
    )
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    ledger_path = runtime / LEDGER_RELATIVE_PATH
    rows = parse_ledger(ledger_path)

    if not rows:
        print(f"COST LEDGER VAZIO ({ledger_path.relative_to(runtime) if ledger_path.is_file() else ledger_path})")
        print("Nenhuma tarefa registrada ainda. Isso é esperado logo após `compose` — "
              "cada tarefa concluída deve adicionar uma linha ao ledger (ver logs/AGENTS.md).")
        return 0

    # Converte tokens em USD usando a tabela de precos, quando a linha nao
    # trouxe custo explicito.
    pricing = load_pricing(runtime)
    for row in rows:
        row["cost_usd"] = f"{derive_cost(row, pricing):.6f}"

    total = {c: 0.0 for c in NUMERIC_COLUMNS}
    for row in rows:
        for col in NUMERIC_COLUMNS:
            total[col] += to_number(row.get(col, ""))

    print(f"COST REPORT | {ledger_path.relative_to(runtime)} | tarefas registradas: {len(rows)}")
    print(
        f"TOTAL | tokens_in={int(total['tokens_in'])} tokens_out={int(total['tokens_out'])} "
        f"cost_usd={total['cost_usd']:.4f} wall_seconds={int(total['wall_seconds'])}"
    )

    # Atribuicao por artefato de negocio (capitulo, capa, midia, DOCX...).
    for row in rows:
        row["artifact"] = artifact_of(row.get("task_id", ""))

    print_table("Por ARTEFATO (o que cada entregavel custou)", aggregate(rows, "artifact"))
    print_table("Por fase", aggregate(rows, "phase"))
    print_table("Por model_tier", aggregate(rows, "model_tier"))
    print_table("Por agente (owner)", aggregate(rows, "owner"))

    unpriced = sum(1 for r in rows if to_number(r.get("cost_usd", "")) == 0)
    if unpriced:
        print(
            f"\nNota: {unpriced} de {len(rows)} linhas sem cost_usd. Tokens e tempo sao "
            "telemetria real; a conversao para USD exige a tabela de precos por modelo "
            "(ver MODEL_TIERS.yaml) e ainda nao esta cadastrada."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
