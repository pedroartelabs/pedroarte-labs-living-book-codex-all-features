"""Pré-filtro determinístico de repetição, clichê e tiques de prosa.

Por que existe
--------------
O motor aciona três agentes de linguagem para o mesmo tipo de checagem —
CLICHE_REVIEWER, CLICHE_HUNTER e REDUNDANCY_REVIEWER — e cada um relê o
manuscrito inteiro. Detectar que uma frase de cinco palavras aparece quatro
vezes, ou que "coração disparado" está no texto, é contagem, não julgamento
literário. Contar com um modelo de linguagem custa tokens e tempo para produzir
o que um script produz igual, sempre.

O que este script NÃO faz
-------------------------
Ele não substitui o revisor. Encontra repetição de FORMULAÇÃO (as mesmas
palavras) e padrões catalogados. **Não** encontra repetição de IDEIA dita com
outras palavras, nem clichê que não esteja na lista, nem julga se uma
repetição é intencional — eco deliberado é recurso literário legítimo.

Essas três coisas continuam sendo trabalho do agente revisor. O que muda é o
volume: em vez de reler 460 mil caracteres à procura de tudo, ele recebe uma
lista de trechos concretos para julgar.

Sem dependências novas: biblioteca padrão + PyYAML.

Uso:
    python engine/scripts/detect_repetition.py --runtime runtime/<slug>
    python engine/scripts/detect_repetition.py --file caminho/para.md --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ENGINE = Path(__file__).resolve().parents[1]
DEFAULTS_PATH = ENGINE / "templates" / "TEXT_QUALITY_DEFAULTS.yaml"
SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "BLOCKER"]

# Palavras funcionais do PT-BR. Uma sequência feita só delas é estrutura da
# língua, não repetição autoral.
STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos",
    "das", "em", "no", "na", "nos", "nas", "por", "pelo", "pela", "para", "com",
    "sem", "sobre", "entre", "ate", "e", "ou", "mas", "que", "se", "como",
    "quando", "porque", "nao", "sim", "ja", "ainda", "mais", "menos", "muito",
    "pouco", "tao", "so", "tambem", "depois", "antes", "onde", "quem", "qual",
    "ele", "ela", "eles", "elas", "eu", "tu", "voce", "nos", "vos", "lhe",
    "lhes", "me", "te", "seu", "sua", "seus", "suas", "meu", "minha", "dele",
    "dela", "isso", "isto", "aquilo", "esse", "essa", "este", "esta", "aquele",
    "aquela", "ao", "aos", "a", "foi", "era", "ser", "estar", "ter", "tinha",
    "havia", "vai", "ia", "do", "num", "numa", "dum", "duma",
}

DIALOGUE_MARKERS = ("—", "–", "-")

# Numerais por extenso e unidades de tempo. Uma sequência feita deles é quase
# sempre uma data ou um horário — conteúdo factual, não formulação autoral.
# Calibrado contra um manuscrito real cuja trama gira em torno de registros
# horários: sem este filtro, "às nove e vinte e" virava achado de repetição.
NUMBER_WORDS = {
    "zero", "um", "uma", "dois", "duas", "tres", "quatro", "cinco", "seis",
    "sete", "oito", "nove", "dez", "onze", "doze", "treze", "quatorze",
    "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove",
    "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta",
    "oitenta", "noventa", "cem", "cento", "duzentos", "trezentos", "mil",
    "primeiro", "primeira", "segundo", "segunda", "terceiro", "terceira",
    "hora", "horas", "minuto", "minutos", "dia", "dias", "meia", "manha",
    "tarde", "noite", "madrugada",
}


def strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def load_config(runtime: Path | None) -> dict:
    cfg = yaml.safe_load(DEFAULTS_PATH.read_text(encoding="utf-8")).get("spec", {})
    if runtime:
        override = runtime / "book" / "text_quality.yaml"
        if override.is_file():
            data = yaml.safe_load(override.read_text(encoding="utf-8")) or {}
            for section, values in (data.get("spec") or {}).items():
                if isinstance(values, dict) and isinstance(cfg.get(section), dict):
                    cfg[section].update(values)
                else:
                    cfg[section] = values
    return cfg


def finding(kind, severity, chapter, evidence, detail, recommendation) -> dict:
    return {
        "category": kind,
        "severity": severity,
        "chapter": chapter,
        "evidence": evidence,
        "detail": detail,
        "recommended_action": recommendation,
    }


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def parse_chapters(text: str) -> dict[int, str]:
    """Divide pelo cabeçalho `# N. Título` do manuscrito congelado. Sem
    cabeçalhos reconhecíveis, trata tudo como capítulo 0."""
    chapters: dict[int, list[str]] = {}
    current = 0
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^#\s+(\d+)\.\s+(.+)$", line)
        if m:
            if buf:
                chapters.setdefault(current, []).extend(buf)
            current = int(m.group(1))
            buf = []
        else:
            buf.append(line)
    if buf:
        chapters.setdefault(current, []).extend(buf)
    return {k: "\n".join(v) for k, v in chapters.items()}


def paragraphs_of(text: str) -> list[str]:
    out = []
    for block in re.split(r"\n\s*\n", text):
        block = " ".join(block.split())
        if block and block != "* * *" and not block.startswith("#"):
            out.append(block)
    return out


def words_of(text: str) -> list[str]:
    return re.findall(r"\b[\wÀ-ÿ]+\b", text.lower())


def sentences_of(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?…])\s+", text)
    return [p.strip() for p in parts if p.strip()]


# --------------------------------------------------------------------------
# Detectores
# --------------------------------------------------------------------------

def detect_ngrams(chapters, cfg) -> list[dict]:
    conf = cfg["ngram_repetition"]
    if not conf.get("enabled", True):
        return []
    size = conf["size"]
    counter: Counter = Counter()
    locations: dict[tuple, set] = defaultdict(set)

    for number, text in chapters.items():
        for para in paragraphs_of(text):
            tokens = words_of(para)
            for i in range(len(tokens) - size + 1):
                gram = tuple(tokens[i:i + size])
                plain = [strip_accents(w) for w in gram]
                stops = sum(1 for w in plain if w in STOPWORDS)
                if stops / size > conf["max_stopword_ratio"]:
                    continue
                # Datas e horários por extenso são fato, não formulação.
                numeric = sum(1 for w in plain if w in NUMBER_WORDS or w.isdigit())
                if numeric / size >= conf.get("max_number_ratio", 0.4):
                    continue
                counter[gram] += 1
                locations[gram].add(number)

    findings = []
    for gram, count in counter.most_common():
        if count < conf["min_occurrences"]:
            break
        chapters_hit = sorted(locations[gram])
        findings.append(finding(
            "repeticao_de_formulacao", conf["severity"],
            chapters_hit[0] if chapters_hit else 0,
            " ".join(gram),
            f"{count} ocorrências, capítulos {chapters_hit}",
            "Confirmar se a repetição é eco deliberado; se não for, variar a formulação.",
        ))
    return findings


def shingles(words: list[str], size: int) -> set[tuple]:
    return {tuple(words[i:i + size]) for i in range(len(words) - size + 1)}


def detect_near_duplicates(chapters, cfg) -> list[dict]:
    conf = cfg["near_duplicate_paragraphs"]
    if not conf.get("enabled", True):
        return []
    entries = []
    for number, text in chapters.items():
        for para in paragraphs_of(text):
            words = words_of(para)
            if len(words) >= conf["min_words"]:
                entries.append((number, para, shingles(words, conf["shingle_size"])))

    findings = []
    for i in range(len(entries)):
        ch_a, para_a, sh_a = entries[i]
        if not sh_a:
            continue
        for j in range(i + 1, len(entries)):
            ch_b, para_b, sh_b = entries[j]
            if not sh_b:
                continue
            union = sh_a | sh_b
            if not union:
                continue
            score = len(sh_a & sh_b) / len(union)
            if score >= conf["threshold"]:
                findings.append(finding(
                    "paragrafos_quase_identicos", conf["severity"], ch_a,
                    f"cap.{ch_a}: {para_a[:110]}…\n    cap.{ch_b}: {para_b[:110]}…",
                    f"similaridade lexical {score:.0%}",
                    "Verificar se a repetição é estrutural (formulário, ritual) ou descuido.",
                ))
    return findings


def detect_cliches(chapters, cfg) -> list[dict]:
    conf = cfg["cliches"]
    if not conf.get("enabled", True):
        return []
    findings = []
    for number, text in chapters.items():
        flat = strip_accents(" ".join(text.split()).lower())
        for pattern in conf["patterns"]:
            needle = strip_accents(pattern.lower())
            count = flat.count(needle)
            if count:
                idx = flat.find(needle)
                findings.append(finding(
                    "cliche", conf["severity"], number, pattern,
                    f"{count}x no capítulo {number}; contexto: …{flat[max(0, idx-40):idx+len(needle)+40]}…",
                    "Substituir por imagem concreta e específica da cena.",
                ))
    return findings


def detect_adverbs(chapters, cfg) -> list[dict]:
    conf = cfg["adverbs_mente"]
    if not conf.get("enabled", True):
        return []
    findings = []
    for number, text in chapters.items():
        paras = paragraphs_of(text)
        total_words = sum(len(words_of(p)) for p in paras)
        adverbs = [w for p in paras for w in words_of(p) if w.endswith("mente") and len(w) > 7]
        if total_words >= 500:
            rate = len(adverbs) * 1000 / total_words
            if rate > conf["max_per_1000_words"]:
                findings.append(finding(
                    "densidade_de_adverbios", conf["severity"], number,
                    ", ".join(sorted(set(adverbs))[:8]),
                    f"{rate:.1f} advérbios em -mente por mil palavras (limite {conf['max_per_1000_words']})",
                    "Trocar advérbios por verbos mais precisos ou detalhe concreto.",
                ))
        for para in paras:
            hits = [w for w in words_of(para) if w.endswith("mente") and len(w) > 7]
            if len(hits) > conf["max_per_paragraph"]:
                findings.append(finding(
                    "adverbios_no_paragrafo", conf["severity"], number,
                    ", ".join(hits), f"{len(hits)} num só parágrafo: {para[:100]}…",
                    "Reduzir a um; o restante vira ação ou detalhe.",
                ))
    return findings


def detect_openings(chapters, cfg) -> list[dict]:
    conf = cfg["sentence_openings"]
    if not conf.get("enabled", True):
        return []
    findings = []
    limit = conf["max_consecutive_same"]
    for number, text in chapters.items():
        for para in paragraphs_of(text):
            firsts = []
            for sentence in sentences_of(para):
                words = words_of(sentence)
                firsts.append(words[0] if words else "")
            run, prev = 1, None
            for word in firsts:
                if word and word == prev:
                    run += 1
                    if run > limit:
                        findings.append(finding(
                            "aberturas_repetidas", conf["severity"], number, word,
                            f"{run} frases consecutivas começando com “{word}”: {para[:100]}…",
                            "Variar a estrutura de abertura das frases.",
                        ))
                        break
                else:
                    run, prev = 1, word
    return findings


def detect_dialogue_tags(chapters, cfg) -> list[dict]:
    conf = cfg["dialogue_tags"]
    if not conf.get("enabled", True):
        return []
    exotic_set = {strip_accents(t.lower()) for t in conf["exotic_tags"]}
    findings = []
    for number, text in chapters.items():
        exotic_hits: Counter = Counter()
        neutral = 0
        for para in paragraphs_of(text):
            if not para.startswith(DIALOGUE_MARKERS):
                continue
            tokens = [strip_accents(w) for w in words_of(para)]
            if "disse" in tokens or "falou" in tokens or "perguntou" in tokens:
                neutral += 1
            for token in tokens:
                if token in exotic_set:
                    exotic_hits[token] += 1
        total = neutral + sum(exotic_hits.values())
        if total >= 10 and sum(exotic_hits.values()) / total > conf["max_exotic_ratio"]:
            findings.append(finding(
                "verbos_de_fala_exoticos", conf["severity"], number,
                ", ".join(f"{k}×{v}" for k, v in exotic_hits.most_common(6)),
                f"{sum(exotic_hits.values())} de {total} marcações de fala são exóticas",
                "Preferir “disse”; o verbo de fala não deve competir com a fala.",
            ))
    return findings


DETECTORS = [detect_ngrams, detect_near_duplicates, detect_cliches,
             detect_adverbs, detect_openings, detect_dialogue_tags]


def analyse(text: str, cfg: dict) -> list[dict]:
    chapters = parse_chapters(text)
    findings: list[dict] = []
    for detector in DETECTORS:
        findings.extend(detector(chapters, cfg))
    findings.sort(key=lambda f: (-SEVERITY_ORDER.index(f["severity"]), f["chapter"]))
    return findings


def render(findings: list[dict], source: str, words: int) -> str:
    lines = [
        "# Relatório de repetição e clichê\n\n",
        f"Fonte: `{source}` — {words:,} palavras.\n\n".replace(",", "."),
        "Gerado por `engine/scripts/detect_repetition.py`. Este é um **pré-filtro "
        "mecânico**: ele encontra repetição de formulação e padrões catalogados, "
        "não repetição de ideia com outras palavras nem clichê fora da lista. "
        "O julgamento editorial — inclusive decidir que uma repetição é eco "
        "deliberado — continua sendo do agente revisor.\n\n",
    ]
    if not findings:
        lines.append("Nenhum achado acima dos limiares configurados.\n")
        return "".join(lines)

    by_severity = Counter(f["severity"] for f in findings)
    lines.append("| Severidade | Achados |\n|---|---:|\n")
    for sev in reversed(SEVERITY_ORDER):
        if by_severity.get(sev):
            lines.append(f"| {sev} | {by_severity[sev]} |\n")
    lines.append("\n")

    by_category = defaultdict(list)
    for f in findings:
        by_category[f["category"]].append(f)
    for category, items in by_category.items():
        lines.append(f"## {category} ({len(items)})\n\n")
        for f in items[:40]:
            lines.append(f"- **{f['severity']}** cap. {f['chapter']} — `{f['evidence']}`\n")
            lines.append(f"  - {f['detail']}\n")
            lines.append(f"  - Ação sugerida: {f['recommended_action']}\n")
        if len(items) > 40:
            lines.append(f"- …e mais {len(items) - 40} achados desta categoria.\n")
        lines.append("\n")
    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pré-filtro determinístico de repetição, clichê e tiques de prosa."
    )
    parser.add_argument("--runtime", type=Path, help="Raiz do runtime.")
    parser.add_argument("--file", type=Path, help="Analisar um arquivo específico.")
    parser.add_argument("--json", action="store_true", help="Saída JSON.")
    parser.add_argument("--out", type=Path, help="Grava o relatório neste caminho.")
    args = parser.parse_args()

    if args.file:
        source = args.file
        runtime = args.runtime
    elif args.runtime:
        runtime = args.runtime
        source = runtime / "manuscript/final/MANUSCRIPT_FINAL_PTBR.md"
    else:
        print("Informe --runtime ou --file.", file=sys.stderr)
        return 2

    if not source.is_file():
        print(f"Manuscrito não encontrado: {source}", file=sys.stderr)
        return 2

    cfg = load_config(runtime)
    text = source.read_text(encoding="utf-8")
    findings = analyse(text, cfg)
    total_words = len(words_of(text))

    if args.json:
        print(json.dumps({"source": str(source), "words": total_words,
                          "findings": findings}, ensure_ascii=False, indent=2))
    else:
        report = render(findings, str(source), total_words)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(report, encoding="utf-8")
            print(f"Relatório: {args.out}")
        else:
            print(report)

    blocking = cfg.get("blocking_severity", "BLOCKER")
    limit = SEVERITY_ORDER.index(blocking)
    hard = [f for f in findings if SEVERITY_ORDER.index(f["severity"]) >= limit]
    counts = Counter(f["severity"] for f in findings)
    print(f"\nTOTAL: {len(findings)} achados "
          f"({', '.join(f'{v} {k}' for k, v in counts.most_common()) or 'nenhum'})",
          file=sys.stderr)
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
