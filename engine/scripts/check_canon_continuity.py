"""Pré-filtro determinístico de continuidade contra o canon aprovado.

Por que existe
--------------
PLOT_CONTINUITY_REVIEWER, CHARACTER_CONTINUITY_REVIEWER e WORLD_RULES_REVIEWER
releem o manuscrito inteiro a cada wave e de novo na integração — cinco
passadas de leitura completa num livro de 24 capítulos. Parte do que procuram é
verificável por comparação: um nome próprio que aparece na prosa e não existe
no canon, o mesmo personagem grafado de duas formas, um capítulo narrado por
quem não deveria narrá-lo.

O que este script verifica
---------------------------
1. **Entidades não canônicas** — nomes próprios recorrentes na prosa que não
   aparecem em nenhum fato do CANON_REGISTRY. É o sintoma de um personagem ou
   lugar introduzido durante a escrita sem passar pelo CANON_GUARDIAN, que o
   motor classifica como CANON_CONFLICT.
2. **Variação de grafia** — nomes muito próximos entre si (Olívia/Olivia,
   Damião/Damiao), quase sempre erro de digitação e não dois personagens.
3. **Ponto de vista** — o canon declara quais capítulos pertencem a cada
   narrador, com contagem. Isso é fato estruturado e é conferido literalmente.

O que este script NÃO verifica
-------------------------------
Os fatos do canon são frases em prosa ("Ester Vilar is 52, Olívia's daughter").
Confirmar que a prosa respeita a idade, o parentesco ou a cronologia exige
entender o texto — continua sendo trabalho do agente revisor. O script reduz o
volume que ele precisa ler; não substitui o julgamento.

Sem dependências novas: biblioteca padrão + PyYAML.

Uso:
    python engine/scripts/check_canon_continuity.py --runtime runtime/<slug>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import yaml

SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "BLOCKER"]

# Capitalizadas que não são entidades: início de frase, dias, meses, títulos.
NOT_ENTITIES = {
    "a", "o", "e", "mas", "que", "quando", "se", "por", "para", "com", "sem",
    "ela", "ele", "eles", "elas", "isso", "isto", "aquilo", "nao", "sim",
    "depois", "antes", "agora", "ainda", "entao", "ate", "ja", "la", "ali",
    "segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo",
    "janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho",
    "agosto", "setembro", "outubro", "novembro", "dezembro",
    "senhor", "senhora", "doutor", "doutora", "dona", "seu", "sua",
    "seus", "suas", "um", "uma", "os", "as", "no", "na", "de", "do", "da",
    "capitulo", "parte", "livro",
}


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn")


def finding(kind, severity, chapter, evidence, detail, action) -> dict:
    return {"category": kind, "severity": severity, "chapter": chapter,
            "evidence": evidence, "detail": detail, "recommended_action": action}


def parse_chapters(text: str) -> dict[int, str]:
    chapters: dict[int, list[str]] = {}
    current, buf = 0, []
    for line in text.splitlines():
        m = re.match(r"^#\s+(\d+)\.\s+(.+)$", line)
        if m:
            if buf:
                chapters.setdefault(current, []).extend(buf)
            current, buf = int(m.group(1)), []
        else:
            buf.append(line)
    if buf:
        chapters.setdefault(current, []).extend(buf)
    return {k: "\n".join(v) for k, v in chapters.items()}


def canon_text(registry: dict) -> str:
    """Concatena todo texto do registry, para busca de menção de entidade."""
    parts: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, str):
            parts.append(node)

    walk(registry)
    return " ".join(parts)


def extract_entities(text: str) -> Counter:
    """Nomes próprios candidatos.

    Heurística: uma palavra capitalizada só conta como entidade se aparecer
    capitalizada em posição de MEIO de frase pelo menos uma vez — no início de
    frase, a maiúscula não distingue nome próprio de palavra comum.
    """
    counts: Counter = Counter()
    for sentence in re.split(r"(?<=[.!?…])\s+|\n", text):
        words = re.findall(r"\b[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\wÀ-ÿ]{2,}\b", sentence)
        if not words:
            continue
        # Descarta a primeira palavra da frase (posição ambígua).
        first = re.match(r"\s*[—–-]?\s*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\wÀ-ÿ]{2,})", sentence)
        skip_first = first.group(1) if first else None
        for word in words:
            if skip_first and word == skip_first:
                skip_first = None
                continue
            if strip_accents(word.lower()) in NOT_ENTITIES:
                continue
            counts[word] += 1
    return counts


def check_unknown_entities(chapters, registry, cfg) -> list[dict]:
    canon_blob = strip_accents(canon_text(registry).lower())
    min_occurrences = cfg.get("min_entity_occurrences", 4)
    findings = []
    per_entity_chapters: dict[str, set] = defaultdict(set)
    totals: Counter = Counter()

    for number, text in chapters.items():
        for entity, count in extract_entities(text).items():
            totals[entity] += count
            per_entity_chapters[entity].add(number)

    for entity, count in totals.most_common():
        if count < min_occurrences:
            continue
        if strip_accents(entity.lower()) in canon_blob:
            continue
        chs = sorted(per_entity_chapters[entity])
        # Uma entidade presente em muitos capítulos e muitas vezes carrega
        # peso narrativo; ausente do canon, é lacuna séria. Uma que aparece
        # quatro vezes num capítulo pode ser figurante sem necessidade de
        # registro. A frequência gradua a severidade em vez de tratar as duas
        # como o mesmo problema.
        if count >= 15 or len(chs) >= 4:
            severity = "HIGH"
        elif count >= 8:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        findings.append(finding(
            "entidade_fora_do_canon", severity, chs[0], entity,
            f"{count} ocorrências em {len(chs)} capítulo(s) {chs}; "
            "não mencionada no CANON_REGISTRY",
            "Se for personagem ou lugar da obra, registrar via CANON_PROPOSAL. "
            "Termos institucionais e conceituais em maiúscula (nomes de órgãos, "
            "de documentos, do fenômeno central) também caem aqui e podem ser "
            "dispensados com uma nota.",
        ))
    return findings


def check_spelling_variants(chapters, cfg) -> list[dict]:
    threshold = cfg.get("name_similarity_threshold", 0.86)
    totals: Counter = Counter()
    for text in chapters.values():
        totals.update(extract_entities(text))
    names = [n for n, c in totals.items() if c >= 2]
    findings, seen = [], set()
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if (a, b) in seen or a == b:
                continue
            pa, pb = strip_accents(a.lower()), strip_accents(b.lower())
            if pa == pb and a != b:
                ratio = 1.0
            else:
                ratio = SequenceMatcher(None, pa, pb).ratio()
            if ratio >= threshold:
                seen.add((a, b))
                findings.append(finding(
                    "grafia_divergente", "HIGH" if pa == pb else "MEDIUM", 0,
                    f"{a} ({totals[a]}x) / {b} ({totals[b]}x)",
                    f"similaridade {ratio:.0%}"
                    + (" — diferem apenas por acento" if pa == pb else ""),
                    "Confirmar se são a mesma entidade; unificar a grafia canônica.",
                ))
    return findings


def check_point_of_view(chapters, registry) -> list[dict]:
    """O canon declara quais capítulos pertencem a cada narrador, com contagem.
    Isso é fato estruturado — dá para conferir literalmente."""
    pov = registry.get("point_of_view") or {}
    declared = pov.get("chapters") or {}
    counts = pov.get("counts") or {}
    findings = []

    for narrator, chapter_list in declared.items():
        if not isinstance(chapter_list, list):
            continue
        expected = counts.get(narrator)
        if expected is not None and expected != len(chapter_list):
            findings.append(finding(
                "pov_contagem_divergente", "HIGH", 0, narrator,
                f"canon declara {expected} capítulos mas lista {len(chapter_list)}",
                "Corrigir o CANON_REGISTRY: contagem e lista precisam concordar.",
            ))
        for entry in chapter_list:
            number = entry if isinstance(entry, int) else None
            if number is None:
                m = re.search(r"\d+", str(entry))
                number = int(m.group()) if m else None
            if number is not None and number not in chapters:
                findings.append(finding(
                    "pov_capitulo_inexistente", "HIGH", number or 0, narrator,
                    f"canon atribui o capítulo {number} a {narrator}, "
                    "mas ele não existe no manuscrito",
                    "Conferir numeração de capítulos entre canon e manuscrito.",
                ))

    assigned: dict[int, list[str]] = defaultdict(list)
    for narrator, chapter_list in declared.items():
        if isinstance(chapter_list, list):
            for entry in chapter_list:
                number = entry if isinstance(entry, int) else None
                if number is None:
                    m = re.search(r"\d+", str(entry))
                    number = int(m.group()) if m else None
                if number is not None:
                    assigned[number].append(narrator)
    for number, narrators in sorted(assigned.items()):
        if len(narrators) > 1:
            findings.append(finding(
                "pov_conflitante", "HIGH", number, ", ".join(narrators),
                f"capítulo {number} atribuído a mais de um narrador",
                "Um capítulo tem um ponto de vista; resolver no canon.",
            ))
    if declared:
        missing = sorted(set(chapters) - set(assigned) - {0})
        if missing:
            findings.append(finding(
                "pov_nao_declarado", "LOW", missing[0], str(missing),
                f"{len(missing)} capítulos sem narrador declarado no canon",
                "Registrar o ponto de vista de cada capítulo no CANON_REGISTRY.",
            ))
    return findings


def render(findings, source, registry_path) -> str:
    out = [
        "# Relatório de continuidade contra o canon\n\n",
        f"Manuscrito: `{source}`\nCanon: `{registry_path}`\n\n",
        "Gerado por `engine/scripts/check_canon_continuity.py`. Verifica o que é "
        "**comparável**: inventário de entidades, grafia e mapa de ponto de vista. "
        "Não verifica se a prosa respeita o conteúdo dos fatos do canon (idade, "
        "parentesco, cronologia) — isso exige leitura e continua sendo do agente "
        "revisor.\n\n",
    ]
    if not findings:
        out.append("Nenhuma divergência estrutural encontrada.\n")
        return "".join(out)
    counts = Counter(f["severity"] for f in findings)
    out.append("| Severidade | Achados |\n|---|---:|\n")
    for sev in reversed(SEVERITY_ORDER):
        if counts.get(sev):
            out.append(f"| {sev} | {counts[sev]} |\n")
    out.append("\n")
    by_cat: dict[str, list] = defaultdict(list)
    for f in findings:
        by_cat[f["category"]].append(f)
    for cat, items in by_cat.items():
        out.append(f"## {cat} ({len(items)})\n\n")
        for f in items[:30]:
            out.append(f"- **{f['severity']}** — `{f['evidence']}`\n")
            out.append(f"  - {f['detail']}\n")
            out.append(f"  - Ação sugerida: {f['recommended_action']}\n")
        if len(items) > 30:
            out.append(f"- …e mais {len(items) - 30} nesta categoria.\n")
        out.append("\n")
    return "".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pré-filtro determinístico de continuidade contra o canon."
    )
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--manuscript", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--min-entity-occurrences", type=int, default=4)
    args = parser.parse_args()

    runtime = args.runtime.resolve()
    source = args.manuscript or runtime / "manuscript/final/MANUSCRIPT_FINAL_PTBR.md"
    registry_path = runtime / "canon/CANON_REGISTRY.yaml"
    if not source.is_file():
        print(f"Manuscrito não encontrado: {source}", file=sys.stderr)
        return 2
    if not registry_path.is_file():
        print(f"CANON_REGISTRY não encontrado: {registry_path}", file=sys.stderr)
        return 2

    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    chapters = parse_chapters(source.read_text(encoding="utf-8"))
    cfg = {"min_entity_occurrences": args.min_entity_occurrences}

    findings = []
    findings += check_unknown_entities(chapters, registry, cfg)
    findings += check_spelling_variants(chapters, cfg)
    findings += check_point_of_view(chapters, registry)
    findings.sort(key=lambda f: (-SEVERITY_ORDER.index(f["severity"]), f["chapter"]))

    if args.json:
        print(json.dumps({"findings": findings}, ensure_ascii=False, indent=2))
    else:
        report = render(findings, str(source), str(registry_path))
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
    return 1 if any(f["severity"] in ("HIGH", "BLOCKER") for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
