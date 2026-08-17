"""Preflight da capacidade `docx_pdf_rendering`.

Por que este script existe
--------------------------
Numa execução real do motor, a renderização do DOCX para inspeção visual
consumiu seis dias e exigiu um reinício do Windows: o Word travava ao exportar
PDF mesmo num arquivo de uma linha, o LibreOffice precisou ser baixado e
verificado à mão, e o Microsoft Visual C++ Redistributable teve que ser
atualizado (instalador retornando código 3010, que pede reboot). Nada disso
tinha relação com o livro — era fragilidade de ambiente, descoberta no gate
final, depois de todo o manuscrito já estar escrito e pago.

Este script faz a mesma descoberta em segundos, no bootstrap. Ele cria um DOCX
mínimo de controle e tenta convertê-lo. Se o controle falha, o problema é
ambiental: nenhum ajuste no livro vai resolver, e a resposta correta é emitir
CAPABILITY_BLOCKER antes de gastar qualquer token de escrita.

Uso:
    python engine/scripts/check_render_capability.py
    python engine/scripts/check_render_capability.py --json
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CONVERTERS = [
    # (executável, argumentos para converter, rótulo)
    ("soffice", ["--headless", "--convert-to", "pdf", "--outdir"], "LibreOffice (soffice)"),
    ("libreoffice", ["--headless", "--convert-to", "pdf", "--outdir"], "LibreOffice"),
]


def make_control_docx(directory: Path) -> Path | None:
    """DOCX mínimo de controle. Se a conversão falhar AQUI, o defeito é do
    ambiente — não do livro, do layout nem das imagens."""
    try:
        from docx import Document
    except ImportError:
        return None
    path = directory / "control.docx"
    doc = Document()
    doc.add_paragraph("Controle de renderização do Living Book Engine.")
    doc.save(path)
    return path


def try_converter(executable: str, args: list[str], docx: Path, outdir: Path) -> tuple[bool, str]:
    binary = shutil.which(executable)
    if not binary:
        return False, "não encontrado no PATH"
    try:
        proc = subprocess.run(
            [binary, *args, str(outdir), str(docx)],
            capture_output=True, text=True, timeout=180,
        )
    except subprocess.TimeoutExpired:
        return False, "timeout de 180s — sintoma clássico de travamento de conversão"
    except OSError as exc:
        return False, f"falha ao executar: {exc}"
    produced = list(outdir.glob("*.pdf"))
    if proc.returncode == 0 and produced:
        return True, f"converteu {produced[0].name}"
    detail = (proc.stderr or proc.stdout or "").strip().splitlines()
    return False, f"código {proc.returncode}: {detail[-1] if detail else 'sem saída'}"


def probe() -> dict:
    result: dict = {"capability": "docx_pdf_rendering", "available": False, "routes": []}

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        control = make_control_docx(tmpdir)
        if control is None:
            result["status"] = "BLOCKED"
            result["reason"] = (
                "python-docx não está instalado; nem o DOCX de controle pode ser criado. "
                "Instale as dependências (requirements.txt) no interpretador em uso."
            )
            return result
        result["control_docx_created"] = True

        for executable, args, label in CONVERTERS:
            outdir = tmpdir / f"out_{executable}"
            outdir.mkdir(exist_ok=True)
            ok, detail = try_converter(executable, args, control, outdir)
            result["routes"].append({"route": label, "ok": ok, "detail": detail})
            if ok:
                result["available"] = True
                result["preferred_route"] = label

    if result["available"]:
        result["status"] = "AVAILABLE"
    else:
        result["status"] = "BLOCKED"
        result["reason"] = (
            "Nenhuma cadeia local de conversão DOCX->PDF respondeu ao arquivo de "
            "controle. Isto é falha de ambiente, não do livro."
        )
        result["host_alternatives"] = {
            "claude_code": (
                "Usar a Agent Skill nativa de docx/pdf, que não depende de "
                "LibreOffice, runtime C++ ou reinício do sistema."
            ),
            "codex_or_local": (
                "Instalar LibreOffice e conferir o Microsoft Visual C++ "
                "Redistributable. Se o instalador retornar 3010, o reinício é "
                "obrigatório antes de a conversão funcionar."
            ),
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifica se este ambiente consegue renderizar DOCX para PDF."
    )
    parser.add_argument("--json", action="store_true", help="Saída em JSON.")
    args = parser.parse_args()
    result = probe()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["available"] else 1

    print(f"CAPABILITY docx_pdf_rendering: {result['status']}")
    for route in result.get("routes", []):
        print(f"  [{'OK ' if route['ok'] else 'FAIL'}] {route['route']}: {route['detail']}")
    if result["available"]:
        print(f"\nRota preferencial: {result['preferred_route']}")
        print("GATE_KDP pode contar com inspeção visual local.")
        return 0

    print(f"\n{result.get('reason', '')}")
    for host, action in result.get("host_alternatives", {}).items():
        print(f"  - {host}: {action}")
    print(
        "\nEmita CAPABILITY_BLOCKER agora, no bootstrap. Descobrir isto no "
        "GATE_KDP significa ter pago o livro inteiro antes de saber."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
