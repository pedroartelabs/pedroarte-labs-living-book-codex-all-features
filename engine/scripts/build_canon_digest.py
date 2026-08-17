"""Gera um digest compacto do canon, para leitura por agente.

O problema
----------
As bíblias de canon de um livro real somam ~25 mil palavras — cerca de 33 mil
tokens por leitura integral. Dezenas de tarefas releem esse corpo: cada
revisor de wave, cada painel de crítica, cada passada de linha. E ele só
cresce com o livro, então o custo de contexto avança perto de O(capítulos²):
quanto mais tarde a tarefa, mais canon ela reingere.

A observação que resolve
------------------------
`CANON_REGISTRY.yaml` já guarda o canon como FATOS ATÔMICOS aprovados
(`{id, status, fact, source}`), agrupados por categoria. As bíblias em prosa
são a elaboração desses fatos — necessárias para quem escreve, redundantes
para quem confere. Um revisor de continuidade precisa saber que "Ester tem 52
anos e é mãe de Joana"; não precisa dos três parágrafos que desenvolvem isso.

Este script destila o registry num digest de uma linha por fato, opcionalmente
recortado por capítulo.

Quem ainda precisa da bíblia inteira
------------------------------------
LEAD_NOVELIST e CHAPTER_WRITER escrevendo uma cena, e CANON_GUARDIAN mutando
canon. Para esses, o digest não substitui nada. Para o resto — a maioria das
chamadas — ele substitui.

Uso:
    python engine/scripts/build_canon_digest.py --runtime runtime/<slug>
    python engine/scripts/build_canon_digest.py --runtime <rt> --chapter 12
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import yaml

APPROVED = {"CANON_APPROVED", "APPROVED", "FINAL"}

# Ordem de apresentação: o que orienta uma cena vem antes do que a contextualiza.
CATEGORY_ORDER = [
    "characters", "setting", "ontology", "timeline",
    "care_and_consent", "evidence_artifacts",
]
CATEGORY_LABEL = {
    "characters": "Personagens",
    "setting": "Cenário",
    "ontology": "Ontologia do mundo",
    "timeline": "Linha do tempo",
    "care_and_consent": "Cuidado e consentimento",
    "evidence_artifacts": "Artefatos e evidências",
}


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn")


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def collect_facts(registry: dict) -> dict[str, list[dict]]:
    """Fatos aprovados, por categoria. Proposta não aprovada não é canon —
    é a regra que o próprio ENGINE_GRAPH declara."""
    out: dict[str, list[dict]] = {}
    for key, node in registry.items():
        if not isinstance(node, list):
            continue
        facts = []
        for item in node:
            if not isinstance(item, dict) or "fact" not in item:
                continue
            status = str(item.get("status", "")).upper()
            if status and status not in APPROVED:
                continue
            facts.append(item)
        if facts:
            out[key] = facts
    return out


def chapter_entities(runtime: Path, chapter: int) -> set[str]:
    """Nomes próprios que a arquitetura e o brief associam a este capítulo.
    É o que permite recortar o digest sem depender de leitura semântica."""
    blobs: list[str] = []
    arch = runtime / "book" / "chapter_architecture.yaml"
    if arch.is_file():
        for entry in (load_yaml(arch).get("chapters") or []):
            if isinstance(entry, dict) and entry.get("number") == chapter:
                blobs.append(" ".join(str(v) for v in entry.values()))
    brief = runtime / "briefs" / "chapters" / f"CHAPTER_{chapter:02d}_BRIEF.md"
    if brief.is_file():
        blobs.append(brief.read_text(encoding="utf-8", errors="replace"))
    names: set[str] = set()
    for blob in blobs:
        for word in re.findall(r"\b[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\wÀ-ÿ]{2,}\b", blob):
            names.add(strip_accents(word.lower()))
    return names


def relevant(fact: str, names: set[str]) -> bool:
    plain = strip_accents(fact.lower())
    return any(name in plain for name in names)


def build(runtime: Path, chapter: int | None) -> tuple[str, dict]:
    registry_path = runtime / "canon" / "CANON_REGISTRY.yaml"
    if not registry_path.is_file():
        raise SystemExit(f"CANON_REGISTRY não encontrado: {registry_path}")
    registry = load_yaml(registry_path)
    facts = collect_facts(registry)

    names = chapter_entities(runtime, chapter) if chapter else set()
    lines = [f"# Canon Digest — {registry.get('metadata', {}).get('title', '')}\n\n"]
    if chapter:
        lines.append(f"Recorte do capítulo {chapter}. ")
    lines.append(
        "Um fato por linha, apenas canon **aprovado**. Este digest substitui a "
        "leitura das bíblias completas em tarefas de CONFERÊNCIA. Quem escreve "
        "cena nova (LEAD_NOVELIST, CHAPTER_WRITER) e quem muta canon "
        "(CANON_GUARDIAN) continuam lendo as bíblias — resumo não substitui "
        "material de composição.\n\n"
    )

    stats = {"total": 0, "included": 0}
    ordered = [k for k in CATEGORY_ORDER if k in facts]
    ordered += [k for k in facts if k not in CATEGORY_ORDER]

    for key in ordered:
        items = facts[key]
        stats["total"] += len(items)
        chosen = [f for f in items if not names or relevant(f["fact"], names)]
        if not chosen:
            continue
        stats["included"] += len(chosen)
        lines.append(f"## {CATEGORY_LABEL.get(key, key)}\n\n")
        for item in chosen:
            text = " ".join(str(item["fact"]).split())
            lines.append(f"- `{item.get('id', '?')}` {text}\n")
        lines.append("\n")

    rules = registry.get("immutable_rules") or {}
    if rules.get("ids"):
        lines.append("## Regras imutáveis em vigor\n\n")
        lines.append(f"IDs: {', '.join(str(i) for i in rules['ids'])}\n")
        lines.append(f"Fonte integral: `{rules.get('source', 'book/immutable_rules.yaml')}`\n\n")

    pov = registry.get("point_of_view") or {}
    if pov.get("chapters"):
        lines.append("## Ponto de vista\n\n")
        for narrator, chs in pov["chapters"].items():
            if chapter and isinstance(chs, list) and chapter not in chs:
                continue
            lines.append(f"- **{narrator}**: capítulos {chs}\n")
        if pov.get("forbidden"):
            lines.append(f"- Proibido: {'; '.join(str(f) for f in pov['forbidden'])}\n")
        lines.append("\n")

    return "".join(lines), stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Destila CANON_REGISTRY.yaml num digest compacto por agente."
    )
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--chapter", type=int,
                        help="Recorta o digest para as entidades deste capítulo.")
    parser.add_argument("--out", type=Path, help="Caminho de saída do digest.")
    args = parser.parse_args()

    runtime = args.runtime.resolve()
    digest, stats = build(runtime, args.chapter)

    out = args.out or (runtime / "canon" /
                       (f"CANON_DIGEST_CH{args.chapter:02d}.md" if args.chapter
                        else "CANON_DIGEST.md"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(digest, encoding="utf-8")

    digest_words = len(digest.split())
    bibles = list((runtime / "specs").glob("*.md")) + [runtime / "canon" / "CANON_REGISTRY.yaml"]
    bible_words = sum(len(p.read_text(encoding="utf-8", errors="replace").split())
                      for p in bibles if p.is_file())

    print(f"DIGEST OK | {out}")
    print(f"- fatos: {stats['included']} de {stats['total']} aprovados"
          + (f" (recorte do capítulo {args.chapter})" if args.chapter else ""))
    print(f"- digest: {digest_words} palavras")
    if bible_words:
        print(f"- bíblias completas: {bible_words} palavras "
              f"({digest_words * 100 // bible_words}% do tamanho)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
