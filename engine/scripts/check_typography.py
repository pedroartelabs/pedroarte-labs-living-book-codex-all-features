"""Pré-passada mecânica de tipografia e pontuação do manuscrito.

Por que existe
--------------
TYPOGRAPHY_TEXT_REVIEWER e PTBR_GRAMMAR_EDITOR releem o manuscrito inteiro
procurando, entre outras coisas, aspas retas onde deveriam ser curvas, três
pontos onde deveria haver reticências, espaço duplo e espaço antes de vírgula.
Isso é comparação de caracteres — não exige julgamento linguístico.

Este script encontra e localiza esses casos por linha e coluna. O agente
revisor deixa de varrer o texto atrás deles e passa a decidir apenas o que
exige língua: concordância, regência, ambiguidade, registro.

Convenções detectadas automaticamente
--------------------------------------
O script NÃO impõe um padrão tipográfico: ele infere qual é o padrão dominante
do manuscrito e reporta as EXCEÇÕES. Um livro que usa aspas retas de propósito
não é inundado de achados — o que aparece é a inconsistência interna.

Sem dependências novas: biblioteca padrão + PyYAML.

Uso:
    python engine/scripts/check_typography.py --runtime runtime/<slug>
    python engine/scripts/check_typography.py --file caminho.md --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "BLOCKER"]

EM_DASH = "—"
EN_DASH = "–"
ELLIPSIS = "…"
CURLY = "“”‘’"


def finding(kind, severity, line_no, column, evidence, detail, action) -> dict:
    return {
        "category": kind, "severity": severity, "line": line_no,
        "column": column, "evidence": evidence, "detail": detail,
        "recommended_action": action,
    }


def detect_conventions(text: str) -> dict:
    """Infere o padrão dominante do próprio manuscrito, em vez de impor um."""
    straight_double = text.count('"')
    curly_double = text.count("“") + text.count("”")
    dotdotdot = len(re.findall(r"\.\.\.", text))
    real_ellipsis = text.count(ELLIPSIS)
    em = text.count(EM_DASH)
    hyphen_dialogue = len(re.findall(r"(?m)^-\s", text))
    return {
        "quotes": "curly" if curly_double >= straight_double else "straight",
        "quotes_counts": (curly_double, straight_double),
        "ellipsis": "char" if real_ellipsis >= dotdotdot else "dots",
        "ellipsis_counts": (real_ellipsis, dotdotdot),
        "dialogue_dash": "em" if em >= hyphen_dialogue else "hyphen",
        "dialogue_counts": (em, hyphen_dialogue),
    }


def analyse(text: str) -> tuple[list[dict], dict]:
    conv = detect_conventions(text)
    findings: list[dict] = []
    lines = text.splitlines()

    for i, line in enumerate(lines, 1):
        if line.startswith("#"):
            continue

        # Espaço duplo entre palavras.
        for m in re.finditer(r"\S(  +)\S", line):
            findings.append(finding(
                "espaco_duplo", "LOW", i, m.start() + 2,
                line[max(0, m.start() - 20):m.end() + 20],
                "dois ou mais espaços entre palavras",
                "Reduzir a um espaço.",
            ))

        # Espaço antes de pontuação.
        for m in re.finditer(r"\s+([,.;:!?])", line):
            findings.append(finding(
                "espaco_antes_de_pontuacao", "MEDIUM", i, m.start() + 1,
                line[max(0, m.start() - 25):m.end() + 15],
                f"espaço antes de “{m.group(1)}”",
                "Remover o espaço anterior à pontuação.",
            ))

        # Espaço em branco no fim da linha.
        if line != line.rstrip():
            findings.append(finding(
                "espaco_final", "INFO", i, len(line.rstrip()) + 1,
                repr(line[-12:]), "espaço(s) no fim da linha",
                "Remover; pode gerar quebra indevida na conversão.",
            ))

        # Aspas fora da convenção dominante.
        if conv["quotes"] == "curly":
            for m in re.finditer(r'"', line):
                findings.append(finding(
                    "aspas_inconsistentes", "MEDIUM", i, m.start() + 1,
                    line[max(0, m.start() - 25):m.start() + 25],
                    "aspas retas num manuscrito que usa aspas curvas",
                    "Trocar por “ ” conforme a abertura/fechamento.",
                ))

        # Reticências fora da convenção dominante.
        if conv["ellipsis"] == "char":
            for m in re.finditer(r"\.\.\.", line):
                findings.append(finding(
                    "reticencias_inconsistentes", "LOW", i, m.start() + 1,
                    line[max(0, m.start() - 25):m.end() + 15],
                    "três pontos num manuscrito que usa o caractere …",
                    "Trocar por …",
                ))
        # Quatro pontos ou mais nunca é correto.
        for m in re.finditer(r"\.{4,}", line):
            findings.append(finding(
                "pontuacao_invalida", "MEDIUM", i, m.start() + 1,
                line[max(0, m.start() - 20):m.end() + 15],
                f"{len(m.group(0))} pontos consecutivos",
                "Reticências têm exatamente três pontos (ou o caractere …).",
            ))

        # Travessão de diálogo fora da convenção.
        if conv["dialogue_dash"] == "em":
            if re.match(r"^[-–]\s", line):
                findings.append(finding(
                    "travessao_inconsistente", "MEDIUM", i, 1, line[:45],
                    "diálogo aberto com hífen/meia-risca num manuscrito que usa travessão",
                    f"Trocar por {EM_DASH} (travessão).",
                ))
            # Travessão sem espaço depois.
            if re.match(rf"^{EM_DASH}\S", line):
                findings.append(finding(
                    "travessao_sem_espaco", "LOW", i, 2, line[:45],
                    "travessão de diálogo colado à fala",
                    f"Inserir espaço após o {EM_DASH}.",
                ))

        # Pontuação duplicada.
        for m in re.finditer(r"([,;:])\1+|,\s*\.|\.\s*,", line):
            findings.append(finding(
                "pontuacao_duplicada", "MEDIUM", i, m.start() + 1,
                line[max(0, m.start() - 20):m.end() + 15],
                f"sequência de pontuação suspeita: {m.group(0)!r}",
                "Revisar manualmente.",
            ))

        # Parêntese/aspas curvas não fechadas na linha.
        if line.count("(") != line.count(")"):
            findings.append(finding(
                "parenteses_desbalanceados", "LOW", i, 1, line[:60],
                f"{line.count('(')} abre, {line.count(')')} fecha",
                "Conferir; pode ser intencional se o parêntese cruza parágrafos.",
            ))

    findings.sort(key=lambda f: (-SEVERITY_ORDER.index(f["severity"]), f["line"]))
    return findings, conv


def render(findings: list[dict], conv: dict, source: str) -> str:
    out = [
        "# Relatório de tipografia e pontuação\n\n",
        f"Fonte: `{source}`\n\n",
        "Gerado por `engine/scripts/check_typography.py`. O script infere as "
        "convenções do próprio manuscrito e reporta **exceções internas**, não "
        "impõe um padrão externo.\n\n",
        "## Convenções detectadas\n\n",
        f"- Aspas: **{conv['quotes']}** (curvas: {conv['quotes_counts'][0]}, retas: {conv['quotes_counts'][1]})\n",
        f"- Reticências: **{conv['ellipsis']}** (caractere …: {conv['ellipsis_counts'][0]}, três pontos: {conv['ellipsis_counts'][1]})\n",
        f"- Diálogo: **{conv['dialogue_dash']}** (travessão: {conv['dialogue_counts'][0]}, hífen: {conv['dialogue_counts'][1]})\n\n",
    ]
    if not findings:
        out.append("Nenhuma inconsistência tipográfica encontrada.\n")
        return "".join(out)

    counts = Counter(f["severity"] for f in findings)
    out.append("| Severidade | Achados |\n|---|---:|\n")
    for sev in reversed(SEVERITY_ORDER):
        if counts.get(sev):
            out.append(f"| {sev} | {counts[sev]} |\n")
    out.append("\n")

    by_cat: dict[str, list] = {}
    for f in findings:
        by_cat.setdefault(f["category"], []).append(f)
    for cat, items in by_cat.items():
        out.append(f"## {cat} ({len(items)})\n\n")
        for f in items[:30]:
            out.append(f"- **{f['severity']}** linha {f['line']}, col. {f['column']} — {f['detail']}\n")
            out.append(f"  - `{f['evidence'].strip()}`\n")
        if len(items) > 30:
            out.append(f"- …e mais {len(items) - 30} nesta categoria.\n")
        out.append("\n")
    return "".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pré-passada mecânica de tipografia e pontuação."
    )
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--file", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--fail-on", default="BLOCKER", choices=SEVERITY_ORDER)
    args = parser.parse_args()

    if args.file:
        source = args.file
    elif args.runtime:
        source = args.runtime / "manuscript/final/MANUSCRIPT_FINAL_PTBR.md"
    else:
        print("Informe --runtime ou --file.", file=sys.stderr)
        return 2
    if not source.is_file():
        print(f"Manuscrito não encontrado: {source}", file=sys.stderr)
        return 2

    text = source.read_text(encoding="utf-8")
    findings, conv = analyse(text)

    if args.json:
        print(json.dumps({"source": str(source), "conventions": conv,
                          "findings": findings}, ensure_ascii=False, indent=2))
    else:
        report = render(findings, conv, str(source))
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(report, encoding="utf-8")
            print(f"Relatório: {args.out}")
        else:
            print(report)

    counts = Counter(f["severity"] for f in findings)
    print(f"\nTOTAL: {len(findings)} achados "
          f"({', '.join(f'{v} {k}' for k, v in counts.most_common()) or 'nenhum'})",
          file=sys.stderr)
    limit = SEVERITY_ORDER.index(args.fail_on)
    return 1 if any(SEVERITY_ORDER.index(f["severity"]) >= limit for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
