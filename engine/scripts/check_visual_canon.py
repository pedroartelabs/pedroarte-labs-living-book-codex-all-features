"""Validador determinístico do `VISUAL_NARRATIVE_CANON.yaml` — capability
`BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM`.

Ver `docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md` para o desenho
completo (seções 11 a 14, 19, 23, 26).

**Slice 1** implementou:
  V0 — integridade de contrato; V1 — consistência com o Author Visual DNA;
  V2 — Visual Chekhov (os cinco status do elemento); V3 — Anti-Generic.

**Slice 2** (este acréscimo) implementa:
  Estado narrativo — sigils, motivos e artefatos progressivos, com estado
    SEMPRE projetado a partir de transições ancoradas, nunca armazenado
    (ST-01..ST-09, seção 14 da SDD);
  Narrative Artifacts — conteúdo citado do canon/prosa, nunca inventado
    (VISUAL_INVENTS_FACT, ARTIFACT_OWNER_UNKNOWN, ARTIFACT_BEFORE_FIRST_
    APPEARANCE, ARTIFACT_ILLEGIBLE — seção 19.2 da SDD);
  Dust Jacket Duality — DJ-02/03/04 (DJ-01/05, que dependem de resolução de
    edição, ficam para o Slice 3 — seção 19.5 da SDD);
  Spoiler Safety — exposição é tempo: cada superfície tem um capítulo de
    exposição e um teto de spoiler; cada elemento tem nível e âncora de
    revelação, herdada automaticamente de `reader_access` do ledger quando
    não declarada (SURFACE_SPOILER, SPOILER_UNANCHORED, PREMATURE_EXPOSURE,
    HIDDEN_SURFACE_SPOILER — seção 26.1 da SDD);
  Human-in-the-loop — REQUIRE_APPROVAL só vale com
    `project_state/APPROVALS/VISUAL/<APR-id>.md` cujo `subject_sha256`
    confere com o hash canônico do bloco aprovado; um bloco que muda depois
    de aprovado vira `APPROVAL_STALE` (seção 26.2 da SDD);
  Âncora `TEXT:capítulo:"trecho"` — só resolve em modo `realized`+, contra
    o manuscrito congelado (11.2 da SDD): em `plan`, permanece sempre não
    resolvida, por desenho, não por limitação temporária.

Princípio de armazenamento (seção 11.1 da SDD): decisões e âncoras são
armazenadas; estado por capítulo, exposição e manifestação por edição são
projetados. Este script nunca lê nem escreve um "estado atual".

Sem dependências novas: biblioteca padrão + PyYAML, como o resto do motor.

Uso:
    python engine/scripts/check_visual_canon.py --runtime runtime/<slug>
    python engine/scripts/check_visual_canon.py --canon caminho/VISUAL_NARRATIVE_CANON.yaml \
        --author-dna caminho/AUTHOR_VISUAL_DNA.v1.yaml
    python engine/scripts/check_visual_canon.py --runtime . --mode realized --baseline canon/snapshots/VISUAL_NARRATIVE_CANON.PLAN.yaml
    python engine/scripts/check_visual_canon.py --runtime . --why SYM-SWAN
    python engine/scripts/check_visual_canon.py --runtime . --evidence "cisne" "swan"
    python engine/scripts/check_visual_canon.py --runtime . --state SIG-SWAN --at-chapter 15
    python engine/scripts/check_visual_canon.py --runtime . --timeline
    python engine/scripts/check_visual_canon.py --runtime . --exposure
    python engine/scripts/check_visual_canon.py --runtime . --end-state
    python engine/scripts/check_visual_canon.py --runtime . --mode assets --cover-image media/outputs/cover/BOOK_COVER_KDP.jpg
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageFilter

# --- vocabulário fechado (seção 11 da SDD) ----------------------------------

CLASS_VALUES = {
    "MOTIF", "SIGIL", "NARRATIVE_ARTIFACT", "DECORATIVE_ILLUSTRATION",
    "TYPOGRAPHIC", "AUTHOR_MARK", "FIGURE",
}
PROMINENCE_VALUES = {"DOMINANT", "SECONDARY", "SUPPORTING", "TEXTURE"}
PROMINENCE_RANK = {"TEXTURE": 0, "SUPPORTING": 1, "SECONDARY": 2, "DOMINANT": 3}
SPOILER_VALUES = {"NONE", "LOW", "MEDIUM", "HIGH", "CORE"}
COST_CLASS_VALUES = {"ESSENTIAL", "OPTIONAL", "PREMIUM", "COLLECTOR_ONLY"}
APPROVAL_POLICY_VALUES = {"AUTO", "SUGGEST", "REQUIRE_APPROVAL"}

# Tipo de âncora -> força (11.2 da SDD). TEXT só resolve em modo `realized`
# (Slice 2) — aqui ele sempre falha, o que é o comportamento correto no
# modo `plan`.
ANCHOR_STRENGTH = {
    "LEDGER": "STRUCTURAL", "SCENE": "STRUCTURAL", "TURN": "STRUCTURAL",
    "CHAPTER_FIELD": "STRUCTURAL", "TEXT": "STRUCTURAL",
    "CANON": "SUPPORTED", "DOC": "SUPPORTED", "RULE": "SUPPORTED",
}
# .+ (não \S+): âncoras TEXT:capítulo:"trecho" legitimamente contêm espaços
# dentro das aspas.
ANCHOR_TOKEN_RE = re.compile(r"^(LEDGER|SCENE|TURN|CHAPTER_FIELD|CANON|DOC|RULE|TEXT):.+$")
TEXT_ANCHOR_RE = re.compile(r'^(\d+):"(.+)"$')

# ids GT-*/EV-* pertencem ao ledger causal; SYM-/SIG-/ART- são convenção de
# id de elemento do canon visual do LIVRO. Nenhum destes deve aparecer no
# Author Visual DNA (VP-06 / AUTHOR_LAYER_CONTAINS_BOOK_SYMBOL).
BOOK_ELEMENT_ID_RE = re.compile(r"\b(SYM|SIG|ART)-[A-Za-z0-9][A-Za-z0-9_-]*\b")

# CAND-* é o id de um candidato de descoberta (VISUAL_CANDIDATES.yaml).
# Nenhum renderer ou canon aprovado pode citá-lo diretamente (VP-08) — a
# promoção sempre cria um novo id SYM-/SIG-/ART-.
CANDIDATE_ID_RE = re.compile(r"\bCAND-[A-Za-z0-9][A-Za-z0-9_-]*\b")

# Vocabulário fechado de memory_state, reutilizado de MEMORY_MOTIF_MAP.md
# (seção 14.1 da SDD): S seed, R recall, T transform, P payoff, E echo.
MEMORY_STATE_VALUES = {"S", "R", "T", "P", "E"}

SPOILER_RANK = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CORE": 4}

# Superfícies semiescondidas por natureza (26.1 da SDD). CASE_* fica de fora
# daqui: sua classificação depende de reading_layer (HIDDEN_TRUTH => semi-
# escondida) porque case laminate sem sobrecapa é PÚBLICO (DJ-05) — decisão
# de edição real fica para o Slice 3; aqui a composição já diz a intenção.
SEMI_HIDDEN_SURFACES = {"ENDPAPER_BACK", "INSERT"}
CHAPTER_SCOPED_SURFACES = {"CHAPTER_OPENER", "INTERIOR_PLATE"}

ARTIFACT_TYPE_VALUES = {
    "LETTER", "CONTRACT", "PHOTOGRAPH", "POLAROID", "MAP", "DRAWING",
    "NEWSPAPER_CLIPPING", "REPORT", "DOCUMENT", "NOTE", "DIARY",
    "BLUEPRINT", "MESSAGE", "RECORD_CARD", "SYMBOL", "EVIDENCE",
}

IMITATION_PATTERN = re.compile(r"\bno estilo de\b|\bin the style of\b|\bà la\b|\bao estilo de\b", re.IGNORECASE)


# --- utilidades --------------------------------------------------------------

def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def finding(category: str, severity: str, chapter, evidence: str, detail: str,
            recommended_action: str) -> dict:
    return {
        "category": category,
        "severity": severity,
        "chapter": chapter if chapter is not None else "WHOLE_BOOK",
        "evidence": evidence,
        "detail": detail,
        "recommended_action": recommended_action,
    }


def _rgb_to_hsl(r: float, g: float, b: float) -> tuple[float, float]:
    """r/g/b em 0..1. Retorna (lightness, saturation), 0..1. Hue omitido —
    nenhum papel de cor do Author DNA restringe matiz, só claridade/saturação."""
    mx, mn = max(r, g, b), min(r, g, b)
    lightness = (mx + mn) / 2
    if mx == mn:
        saturation = 0.0
    else:
        delta = mx - mn
        saturation = delta / (2 - mx - mn) if lightness > 0.5 else delta / (mx + mn)
    return lightness, saturation


def hex_to_hsl(hexstr: str):
    """Converte #RRGGBB em (lightness, saturation), 0..1. None se inválido."""
    if not isinstance(hexstr, str):
        return None
    h = hexstr.lstrip("#")
    if len(h) != 6:
        return None
    try:
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError:
        return None
    return _rgb_to_hsl(r, g, b)


# --- Markdown → seções, para âncoras DOC: -----------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


def slugify_heading(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower())
    return slug.strip("-")


def parse_markdown_sections(text: str) -> dict:
    sections: dict[str, str] = {}
    current, buf = None, []
    for line in text.splitlines():
        m = _HEADING_RE.match(line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current, buf = slugify_heading(m.group(2)), []
        else:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


# Mesmo padrão de KDP_LAYOUT_DEFAULTS.yaml (manuscript.chapter_heading_pattern)
# e do parser de build_kdp_docx.py — não reinventa outro formato.
_CHAPTER_HEADING_RE = re.compile(r"^# (\d+)\. (.+)$")


def load_manuscript(runtime: Path) -> dict:
    """Manuscrito congelado, indexado por número de capítulo. Ausente antes
    de `T310_FREEZE_MANUSCRIPT` — âncoras TEXT: simplesmente não resolvem,
    o que é o comportamento correto em `plan`, não um erro."""
    candidates = [
        runtime / "manuscript" / "final" / "MANUSCRIPT_FINAL_PTBR.md",
        runtime / "manuscript" / "final" / "MANUSCRIPT_FINAL_PTBR.txt",
    ]
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        return {}
    chapters: dict[int, list[str]] = {}
    current: int | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = _CHAPTER_HEADING_RE.match(line)
        if heading:
            current = int(heading.group(1))
            chapters[current] = []
            continue
        if line.strip() == "---":
            continue
        if current is not None:
            chapters[current].append(line)
    # Normaliza espaço em branco (inclusive quebras de linha de wrap) para um
    # único espaço: a fonte real de um manuscrito é comumente quebrada em
    # ~70-80 colunas, e uma citação literal como "cláusula quinta" não pode
    # falhar a resolver só porque o editor quebrou a linha entre as palavras.
    return {num: re.sub(r"\s+", " ", " ".join(lines)).strip() for num, lines in chapters.items()}


def load_bibles(runtime: Path) -> dict:
    """Todo .md do runtime, indexado por caminho posix com barra inicial
    (o mesmo formato usado nas âncoras DOC:/specs/ARQUIVO.md#slug)."""
    bibles: dict[str, dict] = {}
    if not runtime.is_dir():
        return bibles
    for md in sorted(runtime.rglob("*.md")):
        rel = "/" + md.relative_to(runtime).as_posix()
        try:
            bibles[rel] = parse_markdown_sections(md.read_text(encoding="utf-8"))
        except OSError:
            continue
    return bibles


# --- contexto narrativo (fontes que as âncoras resolvem contra) -------------

def load_context(runtime: Path) -> dict:
    """Carrega as fontes de âncora disponíveis num runtime. Nenhuma é
    obrigatória: um livro sem `causal_ledger` simplesmente não tem âncoras
    LEDGER: resolvíveis, e isso é reportado como âncora não resolvida —
    nunca como erro de carregamento."""
    context: dict = {"bibles": load_bibles(runtime), "manuscript": load_manuscript(runtime)}
    registry_path = runtime / "canon" / "CANON_REGISTRY.yaml"
    if registry_path.is_file():
        context["canon_registry"] = load_yaml(registry_path)
    ledger_path = runtime / "canon" / "CAUSAL_LEDGER.yaml"
    if ledger_path.is_file():
        context["causal_ledger"] = load_yaml(ledger_path)
    arch_path = runtime / "book" / "chapter_architecture.yaml"
    if arch_path.is_file():
        context["chapter_architecture"] = (load_yaml(arch_path) or {}).get("chapters", [])
    scenes_path = runtime / "book" / "protected_scenes.yaml"
    if scenes_path.is_file():
        context["protected_scenes"] = (load_yaml(scenes_path) or {}).get("scenes", [])
    rules_path = runtime / "book" / "immutable_rules.yaml"
    if rules_path.is_file():
        context["immutable_rules"] = (load_yaml(rules_path) or {}).get("rules", [])
    return context


def find_canon_id(node, target: str):
    """Busca recursiva por qualquer nó com `id: target` em CANON_REGISTRY.yaml
    (que não tem schema fixo e varia por runtime — ver D4 da SDD irmã)."""
    if isinstance(node, dict):
        if node.get("id") == target:
            return node
        for value in node.values():
            found = find_canon_id(value, target)
            if found is not None:
                return found
    elif isinstance(node, list):
        for item in node:
            found = find_canon_id(item, target)
            if found is not None:
                return found
    return None


def resolve_anchor(token: str, context: dict, mode: str = "plan") -> dict | None:
    """Resolve uma âncora contra o contexto narrativo. Retorna
    {'ok', 'strength', 'chapter', 'excerpt'} ou {'ok': False, ...}.

    `mode` só afeta âncoras TEXT: (resolvem apenas em `realized`/`edition`/
    `assets`, contra o manuscrito congelado). Todos os outros tipos
    resolvem igual em qualquer modo — LEDGER:, por exemplo, não fica mais
    "verdadeiro" por estar em modo `realized`; o que muda em `realized` é
    que ST-06/TRIGGER_NOT_REALIZED passa a exigir que o evento citado já
    tenha status REALIZED, não que a resolução em si funcione diferente."""
    if not isinstance(token, str):
        return {"ok": False, "reason": "NOT_A_STRING"}
    m = re.match(r"^([A-Z_]+):(.+)$", token)
    if not m:
        return {"ok": False, "reason": "MALFORMED"}
    kind, rest = m.group(1), m.group(2)
    if kind not in ANCHOR_STRENGTH:
        return {"ok": False, "reason": "UNKNOWN_ANCHOR_TYPE"}
    strength = ANCHOR_STRENGTH[kind]

    if kind == "LEDGER":
        ledger = context.get("causal_ledger")
        if not ledger:
            return {"ok": False, "reason": "ANCHOR_SOURCE_DISABLED"}
        if rest.startswith("EV-"):
            ev = next((e for e in ledger.get("events") or [] if e.get("id") == rest), None)
            if ev:
                return {"ok": True, "strength": strength, "chapter": ev.get("chapter"),
                        "excerpt": "; ".join(ev.get("facts") or [])[:160]}
            return {"ok": False, "reason": "NOT_FOUND"}
        if rest.startswith("GT-"):
            for char in ledger.get("characters") or []:
                for gt in char.get("ground_truth") or []:
                    if gt.get("id") == rest:
                        return {"ok": True, "strength": strength, "chapter": None,
                                "excerpt": (gt.get("statement") or "")[:160]}
            return {"ok": False, "reason": "NOT_FOUND"}
        return {"ok": False, "reason": "UNKNOWN_LEDGER_ID_SHAPE"}

    if kind == "SCENE":
        scene = next((s for s in context.get("protected_scenes") or [] if s.get("id") == rest), None)
        if scene:
            chapters = scene.get("chapters") or []
            return {"ok": True, "strength": strength, "chapter": chapters[0] if chapters else None,
                    "excerpt": (scene.get("purpose") or "")[:160]}
        return {"ok": False, "reason": "NOT_FOUND"}

    if kind == "TURN":
        if not rest.isdigit():
            return {"ok": False, "reason": "MALFORMED"}
        chapter_num = int(rest)
        chapter = next((c for c in context.get("chapter_architecture") or []
                         if c.get("number") == chapter_num), None)
        turn = (chapter or {}).get("irreversible_turn") or ""
        if chapter and turn.strip():
            return {"ok": True, "strength": strength, "chapter": chapter_num, "excerpt": turn[:160]}
        return {"ok": False, "reason": "NOT_FOUND"}

    if kind == "CHAPTER_FIELD":
        chapters = context.get("chapter_architecture") or []
        if any((c.get(rest) not in (None, "")) for c in chapters):
            return {"ok": True, "strength": strength, "chapter": None,
                    "excerpt": f"campo '{rest}' presente em chapter_architecture.yaml"}
        return {"ok": False, "reason": "NOT_FOUND"}

    if kind == "CANON":
        found = find_canon_id(context.get("canon_registry") or {}, rest)
        if found is not None:
            return {"ok": True, "strength": strength, "chapter": None,
                    "excerpt": (found.get("fact") or "")[:160]}
        return {"ok": False, "reason": "NOT_FOUND"}

    if kind == "DOC":
        path, _, slug = rest.partition("#")
        doc = context.get("bibles", {}).get(path)
        if doc is None:
            return {"ok": False, "reason": "DOC_NOT_FOUND"}
        if not slug:
            return {"ok": True, "strength": strength, "chapter": None, "excerpt": path}
        excerpt = doc.get(slug)
        if excerpt is None:
            return {"ok": False, "reason": "SLUG_NOT_FOUND"}
        return {"ok": True, "strength": strength, "chapter": None, "excerpt": excerpt[:160]}

    if kind == "RULE":
        rule = next((r for r in context.get("immutable_rules") or [] if r.get("id") == rest), None)
        if rule:
            return {"ok": True, "strength": strength, "chapter": None, "excerpt": (rule.get("rule") or "")[:160]}
        return {"ok": False, "reason": "NOT_FOUND"}

    if kind == "TEXT":
        # Só resolve fora de `plan`, contra o manuscrito congelado. Em
        # `plan`, é sempre não resolvida — comportamento correto (a prosa
        # ainda não existe para ser citada), não uma limitação temporária.
        if mode == "plan":
            return {"ok": False, "reason": "TEXT_ANCHOR_REQUIRES_REALIZED_MODE"}
        text_match = TEXT_ANCHOR_RE.match(rest)
        if not text_match:
            return {"ok": False, "reason": "MALFORMED"}
        chapter_num, needle = int(text_match.group(1)), text_match.group(2)
        chapter_text = context.get("manuscript", {}).get(chapter_num)
        if chapter_text is None:
            return {"ok": False, "reason": "CHAPTER_NOT_FOUND"}
        idx = chapter_text.find(needle)
        if idx == -1:
            return {"ok": False, "reason": "TEXT_NOT_FOUND"}
        excerpt = chapter_text[max(0, idx - 40):idx + len(needle) + 40]
        return {"ok": True, "strength": strength, "chapter": chapter_num, "excerpt": excerpt[:160]}

    return {"ok": False, "reason": "UNKNOWN_ANCHOR_TYPE"}


# --- V0 — integridade de contrato -------------------------------------------

def check_integrity(canon: dict) -> list[dict]:
    findings = []
    for required in ("apiVersion", "kind", "metadata"):
        if required not in canon:
            findings.append(finding("CONTRACT_MISSING_FIELD", "HIGH", None, required,
                                     f"VISUAL_NARRATIVE_CANON sem campo obrigatório '{required}'.",
                                     "Adicionar o campo ao arquivo de canon."))
    if canon.get("kind") not in (None, "VisualNarrativeCanon"):
        findings.append(finding("CONTRACT_MISSING_FIELD", "HIGH", None, "kind",
                                 f"kind deveria ser VisualNarrativeCanon, encontrado {canon.get('kind')!r}.",
                                 "Corrigir kind."))

    metadata = canon.get("metadata") or {}
    for required in ("project_id", "owner"):
        if not metadata.get(required):
            findings.append(finding("CONTRACT_MISSING_FIELD", "HIGH", None, f"metadata.{required}",
                                     f"metadata.{required} ausente ou vazio.",
                                     f"Preencher metadata.{required}."))
    author_dna_ref = metadata.get("author_dna") or {}
    for required in ("author_id", "version"):
        if not author_dna_ref.get(required):
            findings.append(finding("CONTRACT_MISSING_FIELD", "HIGH", None,
                                     f"metadata.author_dna.{required}",
                                     f"metadata.author_dna.{required} ausente.",
                                     "Pinar o Author Visual DNA usado (author_id + version)."))

    seen_ids: dict[str, str] = {}

    def check_id(container_name: str, item: dict):
        item_id = item.get("id")
        if not item_id:
            findings.append(finding("CONTRACT_MISSING_FIELD", "HIGH", None, container_name,
                                     f"item em {container_name} sem id.", "Todo item precisa de id único."))
            return
        if item_id in seen_ids:
            findings.append(finding("DUPLICATE_ID", "HIGH", None, item_id,
                                     f"id '{item_id}' duplicado ({seen_ids[item_id]} e {container_name}).",
                                     "Tornar os ids únicos no canon."))
        else:
            seen_ids[item_id] = container_name

    known_element_ids = {el.get("id") for el in canon.get("elements") or [] if el.get("id")}

    for element in canon.get("elements") or []:
        check_id("elements", element)
        el_class = element.get("class")
        if el_class and el_class not in CLASS_VALUES:
            findings.append(finding("INVALID_ENUM", "HIGH", None, element.get("id"),
                                     f"class inválida: {el_class!r}.",
                                     f"Usar um valor de {sorted(CLASS_VALUES)}."))
        prominence = element.get("prominence")
        if prominence and prominence not in PROMINENCE_VALUES:
            findings.append(finding("INVALID_ENUM", "HIGH", None, element.get("id"),
                                     f"prominence inválida: {prominence!r}.",
                                     "Usar DOMINANT|SECONDARY|SUPPORTING|TEXTURE."))
        spoiler = (element.get("exposure") or {}).get("spoiler_level")
        if spoiler and spoiler not in SPOILER_VALUES:
            findings.append(finding("INVALID_ENUM", "HIGH", None, element.get("id"),
                                     f"exposure.spoiler_level inválido: {spoiler!r}.",
                                     "Usar NONE|LOW|MEDIUM|HIGH|CORE."))
        cost_class = element.get("cost_class")
        if cost_class and cost_class not in COST_CLASS_VALUES:
            findings.append(finding("INVALID_ENUM", "HIGH", None, element.get("id"),
                                     f"cost_class inválido: {cost_class!r}.",
                                     "Usar ESSENTIAL|OPTIONAL|PREMIUM|COLLECTOR_ONLY."))
        policy = (element.get("approval") or {}).get("policy")
        if policy and policy not in APPROVAL_POLICY_VALUES:
            findings.append(finding("INVALID_ENUM", "HIGH", None, element.get("id"),
                                     f"approval.policy inválida: {policy!r}.",
                                     "Usar AUTO|SUGGEST|REQUIRE_APPROVAL."))
        for fn in element.get("functions") or []:
            for anchor in fn.get("anchors") or []:
                if not (isinstance(anchor, str) and ANCHOR_TOKEN_RE.match(anchor)):
                    findings.append(finding("MALFORMED_ANCHOR", "HIGH", None, element.get("id"),
                                             f"âncora malformada: {anchor!r}.",
                                             "Âncora deve seguir TIPO:valor "
                                             "(LEDGER|SCENE|TURN|CHAPTER_FIELD|CANON|DOC|RULE|TEXT)."))

    for composition in canon.get("compositions") or []:
        check_id("compositions", composition)
        referenced = {ref.get("element") for ref in composition.get("elements") or []}
        for missing in referenced - known_element_ids:
            findings.append(finding("DANGLING_REFERENCE", "HIGH", None, composition.get("id"),
                                     f"composição referencia elemento inexistente '{missing}'.",
                                     "Corrigir o id referenciado ou declarar o elemento em elements[]."))

    for fi in canon.get("finish_intents") or []:
        check_id("finish_intents", fi)
    for veto in canon.get("vetoes") or []:
        check_id("vetoes", veto)

    # VP-08: candidato != canon. Nenhum id CAND-* pode ser citado dentro do
    # canon aprovado — promoção sempre cria um novo id SYM-/SIG-/ART-.
    dump = yaml.safe_dump(canon, allow_unicode=True)
    leaked_candidates = sorted(set(CANDIDATE_ID_RE.findall(dump)))
    if leaked_candidates:
        findings.append(finding(
            "CANDIDATE_CONSUMED", "HIGH", None, "VISUAL_NARRATIVE_CANON",
            f"referência(s) a candidato(s) não promovido(s) encontradas no canon: {leaked_candidates}.",
            "Um candidato de canon/CANON_PROPOSALS/VISUAL_CANDIDATES.yaml precisa ser promovido a "
            "um id de elemento (SYM-/SIG-/ART-) antes de aparecer no canon aprovado — nunca citado "
            "diretamente (VP-08)."))

    return findings


# --- V1 — consistência com o Author Visual DNA ------------------------------

def canonical_dna_bytes(dna: dict) -> bytes:
    """Hash canônico do DNA, ignorando `metadata.status` (única mutação
    permitida num DNA já pinado — ver seção 27.2 da SDD)."""
    clean = copy.deepcopy(dna)
    if isinstance(clean.get("metadata"), dict):
        clean["metadata"].pop("status", None)
    return json.dumps(clean, sort_keys=True, ensure_ascii=False).encode("utf-8")


def canonical_dna_sha256(dna: dict) -> str:
    return hashlib.sha256(canonical_dna_bytes(dna)).hexdigest()


def watchlist_match(element: dict, watchlist: list[dict]) -> list[str]:
    text = " ".join(filter(None, [
        element.get("label", ""), element.get("meaning", ""),
        element.get("visual_description", ""),
    ])).lower()
    hits = []
    for entry in watchlist or []:
        for term in entry.get("match") or []:
            if term.lower() in text:
                hits.append(entry.get("id"))
                break
    return hits


def check_author_consistency(canon: dict, author_dna: dict) -> list[dict]:
    findings = []

    pin = ((canon.get("metadata") or {}).get("author_dna")) or {}
    pinned_sha = pin.get("sha256")
    if pinned_sha:
        actual = canonical_dna_sha256(author_dna)
        if actual != pinned_sha:
            findings.append(finding(
                "AUTHOR_DNA_TAMPERED", "BLOCKER", None, pin.get("author_id", "?"),
                f"sha256 pinado ({pinned_sha[:12]}…) difere do DNA atual ({actual[:12]}…).",
                "Recompor o pin com o hash do DNA realmente aprovado, ou investigar edição "
                "não autorizada de um Author Visual DNA já publicado (imutável — seção 27.2)."))

    dump = yaml.safe_dump(author_dna, allow_unicode=True)
    leaked = sorted(set(BOOK_ELEMENT_ID_RE.findall(dump)))
    if leaked:
        findings.append(finding(
            "AUTHOR_LAYER_CONTAINS_BOOK_SYMBOL", "HIGH", None, "AUTHOR_VISUAL_DNA",
            f"ids de elemento específicos de livro encontrados no DNA da autora: {leaked}.",
            "Remover símbolos/sigils/artefatos de obra do Author DNA — a autora define "
            "gramática (cor, tipografia, marca), o livro define símbolo (VP-06)."))

    invariants = author_dna.get("invariants") or {}
    for override in (canon.get("book_dna") or {}).get("role_overrides") or []:
        key = override.get("key", "")
        top_key = key.split(".")[0] if key else ""
        if key.startswith("invariants.") or top_key in invariants:
            findings.append(finding(
                "AUTHOR_INVARIANT_OVERRIDE", "BLOCKER", None, key,
                f"role_override tenta sobrescrever invariante '{key}'.",
                "Invariantes da autora nunca podem ser sobrescritas pelo livro."))
        elif not (override.get("override_reason") or "").strip():
            findings.append(finding(
                "OVERRIDE_WITHOUT_REASON", "MEDIUM", None, key,
                f"role_override de '{key}' sem override_reason.",
                "Adicionar override_reason explicando por que o livro se afasta do "
                "default da autora."))

    roles = (author_dna.get("color") or {}).get("roles") or {}
    palette = (canon.get("book_dna") or {}).get("palette") or {}
    for role_key, value in palette.items():
        role = roles.get(role_key)
        if not role:
            continue
        hex_value = value.get("hex") if isinstance(value, dict) else value
        hsl = hex_to_hsl(hex_value)
        if not hsl:
            continue
        lightness, saturation = hsl
        l_range, s_range = role.get("lightness"), role.get("saturation")
        out_of_range = (
            (l_range and not (l_range[0] <= lightness <= l_range[1]))
            or (s_range and not (s_range[0] <= saturation <= s_range[1]))
        )
        if out_of_range:
            findings.append(finding(
                "AUTHOR_DNA_DRIFT", "HIGH", None, role_key,
                f"book_dna.palette.{role_key}={hex_value} fora da faixa do papel {role_key} "
                f"(lightness={l_range}, saturation={s_range}; medido l={lightness:.2f} s={saturation:.2f}).",
                "Escolher um valor dentro da faixa do papel da autora, ou registrar "
                "override_reason com aprovação."))

    mark = author_dna.get("author_mark") or {}
    mark_id = mark.get("id")
    required_on = invariants.get("author_mark_required_on") or []
    forbidden_on = mark.get("forbidden_surfaces") or []
    elements_by_id = {el.get("id"): el for el in canon.get("elements") or []}
    compositions = canon.get("compositions") or []

    def has_mark(composition: dict) -> bool:
        for ref in composition.get("elements") or []:
            element = elements_by_id.get(ref.get("element"))
            if ref.get("element") == mark_id or (element and element.get("class") == "AUTHOR_MARK"):
                return True
        return False

    for surface in required_on:
        composition = next((c for c in compositions if c.get("surface") == surface), None)
        if composition is None:
            continue
        if not has_mark(composition):
            findings.append(finding(
                "AUTHOR_MARK_MISSING", "MEDIUM", None, surface,
                f"composição de {surface} não referencia a marca autoral ({mark_id}).",
                f"Incluir a marca ({mark_id}) na composição de {surface}, conforme "
                "invariants.author_mark_required_on."))
    for composition in compositions:
        if composition.get("surface") in forbidden_on and has_mark(composition):
            findings.append(finding(
                "AUTHOR_MARK_MISPLACED", "HIGH", None, composition.get("id"),
                f"marca autoral em {composition.get('surface')}, superfície proibida.",
                f"Remover a marca de {composition.get('surface')} — ver author_mark.forbidden_surfaces."))

    return findings


# --- V2 — Visual Chekhov ------------------------------------------------------

def veto_match(element: dict, vetoes: list[dict]) -> list[dict]:
    text = " ".join(filter(None, [element.get("label", ""), element.get("meaning", "")])).lower()
    hits = []
    for veto in vetoes or []:
        for term in veto.get("match") or []:
            if term.lower() in text:
                hits.append(veto)
                break
    return hits


def resolve_element_functions(element: dict, context: dict, mode: str = "plan") -> dict:
    """Resolve todas as âncoras de todas as funções declaradas.

    Retorna: has_functions, all_resolved (toda função tem >=1 âncora ok),
    all_structural (toda função tem >=1 âncora STRUCTURAL — o requisito
    formal de PROVEN, 11.5), chapters (capítulos distintos entre TODAS as
    âncoras resolvidas, usado na regra de 2 capítulos para DOMINANT)."""
    functions = element.get("functions") or []
    resolved_info = []
    chapters: set[int] = set()
    all_resolved = bool(functions)
    all_structural = bool(functions)
    for fn in functions:
        best = None
        for anchor in fn.get("anchors") or []:
            result = resolve_anchor(anchor, context, mode)
            if result and result.get("ok"):
                if result.get("chapter") is not None:
                    chapters.add(result["chapter"])
                if best is None or (result["strength"] == "STRUCTURAL" and best["strength"] != "STRUCTURAL"):
                    best = result
        if best is None:
            all_resolved = False
            all_structural = False
        elif best["strength"] != "STRUCTURAL":
            all_structural = False
        resolved_info.append({"function": fn.get("function"), "resolved": best})
    return {
        "resolved": resolved_info, "chapters": chapters,
        "has_functions": bool(functions), "all_resolved": all_resolved,
        "all_structural": all_structural,
    }


def chekhov_status(element: dict, canon: dict, context: dict, watchlist: list[dict],
                    mode: str = "plan"):
    """Um dos cinco status de 11.5: PROVEN, SUPPORTED, DECORATIVE_ALLOWED,
    UNJUSTIFIED, CONTRADICTORY. Retorna (status, info) — info carrega o
    motivo estrutural exato para o gerador de achados."""
    matched_vetoes = veto_match(element, canon.get("vetoes") or [])
    if matched_vetoes and not element.get("veto_override"):
        return "CONTRADICTORY", {"vetoes": [v.get("id") for v in matched_vetoes]}

    info = resolve_element_functions(element, context, mode)

    count = element.get("count") or 1
    if count and count > 1:
        rationale = element.get("count_rationale") or {}
        rationale_anchors = rationale.get("anchors") or []
        count_ok = bool(rationale_anchors) and any(
            (resolve_anchor(a, context, mode) or {}).get("ok") for a in rationale_anchors)
        if not count_ok:
            return "UNJUSTIFIED", {"reason": "count_without_rationale", **info}

    prominence = element.get("prominence", "SUPPORTING")
    if info["has_functions"] and info["all_resolved"]:
        if info["all_structural"]:
            distinct_chapters = {c for c in info["chapters"] if c is not None}
            if prominence == "DOMINANT" and len(distinct_chapters) < 2:
                return "UNJUSTIFIED", {"reason": "dominant_needs_2_chapters", **info}
            return "PROVEN", info
        return "SUPPORTED", info

    if (element.get("class") == "DECORATIVE_ILLUSTRATION" and prominence == "TEXTURE"
            and not watchlist_match(element, watchlist)):
        return "DECORATIVE_ALLOWED", info

    return "UNJUSTIFIED", {"reason": "no_resolved_function", **info}


def check_chekhov(canon: dict, context: dict, author_dna: dict, mode: str = "plan"):
    findings = []
    status_map: dict[str, tuple[str, dict]] = {}
    watchlist = author_dna.get("generic_trope_watchlist") or []

    for element in canon.get("elements") or []:
        element_id = element.get("id")
        status, info = chekhov_status(element, canon, context, watchlist, mode)
        status_map[element_id] = (status, info)
        prominence = element.get("prominence", "SUPPORTING")
        rank = PROMINENCE_RANK.get(prominence, 1)

        if status == "CONTRADICTORY":
            findings.append(finding(
                "CONTRADICTORY", "HIGH", None, element_id,
                f"{element_id} casa o(s) veto(s) {info.get('vetoes')} sem veto_override.",
                "Remover o elemento, revisar o veto, ou registrar veto_override aprovado."))
        elif status == "UNJUSTIFIED":
            reason = info.get("reason")
            if reason == "count_without_rationale":
                findings.append(finding(
                    "UNJUSTIFIED_COUNT", "HIGH" if rank >= 1 else "MEDIUM", None, element_id,
                    f"{element_id}: count={element.get('count')} sem count_rationale resolvível.",
                    "Adicionar count_rationale com âncora que justifique a quantidade "
                    "(por que exatamente esse número)."))
            elif reason == "dominant_needs_2_chapters":
                findings.append(finding(
                    "UNJUSTIFIED", "HIGH", None, element_id,
                    f"{element_id} é DOMINANT, mas suas âncoras resolvem em menos de "
                    "2 capítulos distintos.",
                    "Adicionar âncoras estruturais em capítulos adicionais, ou reduzir "
                    "a proeminência para SECONDARY/SUPPORTING."))
            else:
                findings.append(finding(
                    "UNJUSTIFIED", "HIGH" if rank >= 1 else "MEDIUM", None, element_id,
                    f"{element_id}: nenhuma função declarada tem âncora resolvível "
                    "(status UNJUSTIFIED).",
                    "Adicionar âncora resolvível para cada função, ou reclassificar "
                    "como TEXTURE/DECORATIVE_ILLUSTRATION."))
        elif status == "SUPPORTED" and prominence == "DOMINANT":
            findings.append(finding(
                "UNJUSTIFIED", "HIGH", None, element_id,
                f"{element_id} é DOMINANT mas status é SUPPORTED (nem toda função tem "
                "âncora STRUCTURAL).",
                "Elemento dominante exige status PROVEN: inclua ao menos uma âncora "
                "STRUCTURAL por função e presença em 2 capítulos distintos."))

        functions_declared = {fn.get("function") for fn in element.get("functions") or []}
        if functions_declared and functions_declared == {"ATMOSPHERE"} and rank >= 2:
            findings.append(finding(
                "ATMOSPHERE_ONLY_PROMINENT", "MEDIUM", None, element_id,
                f"{element_id} só declara função ATMOSPHERE com prominence {prominence}.",
                "Atmosfera sozinha não justifica destaque; declare uma função "
                "adicional do vocabulário fechado, ou reduza a proeminência."))

    return findings, status_map


# --- V3 — Anti-Generic ---------------------------------------------------------

def check_anti_generic(canon: dict, author_dna: dict, status_map: dict) -> list[dict]:
    findings = []
    watchlist = author_dna.get("generic_trope_watchlist") or []

    for element in canon.get("elements") or []:
        element_id = element.get("id")
        status, _ = status_map.get(element_id, (None, {}))
        hits = watchlist_match(element, watchlist)
        if hits and status != "PROVEN":
            findings.append(finding(
                "GENERIC_TROPE_UNJUSTIFIED", "HIGH", None, element_id,
                f"{element_id} casa a watchlist {hits} e status é {status}.",
                "Ancorar cada função declarada em evidência STRUCTURAL específica "
                "desta obra, ou remover o elemento — objeto de gênero sem "
                "justificativa não é permitido, mesmo que 'combine com Dark Romance'."))
            if "BLOOD" in hits and element.get("class") == "DECORATIVE_ILLUSTRATION":
                findings.append(finding(
                    "DECORATIVE_VIOLENCE", "HIGH", None, element_id,
                    f"{element_id}: sangue usado como decoração, sem função narrativa.",
                    "Remover, ou justificar com função e âncora ancorada."))
        text = " ".join(filter(None, [element.get("meaning", ""),
                                       element.get("visual_description", "")]))
        if IMITATION_PATTERN.search(text):
            findings.append(finding(
                "IMITATION_REFERENCE", "HIGH", None, element_id,
                f"{element_id} referencia estilo/composição de terceiros.",
                "Descrever princípios de design (hierarquia, espaço negativo, "
                "contraste), nunca uma obra, autora ou capa específica de referência."))

    for composition in canon.get("compositions") or []:
        if IMITATION_PATTERN.search(composition.get("atmosphere") or ""):
            findings.append(finding(
                "IMITATION_REFERENCE", "HIGH", None, composition.get("id"),
                f"{composition.get('id')} referencia estilo de terceiros na atmosfera.",
                "Remover a referência nominal; descrever apenas a intenção própria."))

    density = (author_dna.get("defaults") or {}).get("density") or {}
    max_secondary = density.get("max_secondary_per_surface", 2)
    max_decorative = density.get("decorative_budget_per_surface", 1)
    max_dominant = (author_dna.get("invariants") or {}).get("max_dominant_per_surface", 1)

    for composition in canon.get("compositions") or []:
        counts = {"DOMINANT": 0, "SECONDARY": 0, "TEXTURE": 0}
        for ref in composition.get("elements") or []:
            prominence = ref.get("prominence")
            if prominence in counts:
                counts[prominence] += 1
        if counts["DOMINANT"] > max_dominant or counts["SECONDARY"] > max_secondary \
                or counts["TEXTURE"] > max_decorative:
            findings.append(finding(
                "VISUAL_OVERLOAD", "HIGH", None, composition.get("id"),
                f"{composition.get('id')} ({composition.get('surface')}): "
                f"dominant={counts['DOMINANT']} secondary={counts['SECONDARY']} "
                f"texture={counts['TEXTURE']}, excede o orçamento da autora "
                f"({max_dominant}/{max_secondary}/{max_decorative}).",
                "Reduzir elementos destacados por superfície, ou registrar orçamento "
                "maior no book_dna com override_reason e aprovação."))

    return findings


# --- Estado narrativo (seção 14 da SDD) — Slice 2 --------------------------

_COLOR_WORDS = {
    "vermelho", "vermelha", "azul", "verde", "dourado", "dourada",
    "prateado", "prateada", "preto", "preta", "branco", "branca",
    "amarelo", "amarela", "rosa", "roxo", "roxa", "cobre",
    "red", "blue", "green", "gold", "golden", "silver", "black", "white", "yellow",
}


def _strip_color_words(text: str) -> str:
    words = re.findall(r"[a-zà-ú]+", text.lower())
    return " ".join(w for w in words if w not in _COLOR_WORDS)


def _differs_only_by_color(a: str, b: str) -> bool:
    if not a or not b or a.strip() == b.strip():
        return False
    return _strip_color_words(a) == _strip_color_words(b)


def _build_transition_graph(element: dict, context: dict, mode: str,
                             state_ids: set[str], eid: str) -> tuple[dict, list[dict]]:
    """Resolve os triggers das transições declaradas e monta o grafo
    from -> [(to, chapter, reversible)]. Retorna também os achados de
    ST-02 (ARBITRARY_STATE_MUTATION) e RANDOM_SIGIL_MUTATION."""
    findings = []
    graph: dict[str, list[tuple[str, int | None, bool]]] = {}
    for t in element.get("transitions") or []:
        frm, to = t.get("from"), t.get("to")
        if frm not in state_ids or to not in state_ids:
            findings.append(finding(
                "RANDOM_SIGIL_MUTATION", "HIGH", None, eid,
                f"{eid}: transição referencia estado não declarado ({frm!r} -> {to!r}).",
                "Toda transição precisa de 'from' e 'to' declarados em states[] — um "
                "estado citado ad hoc, fora do modelo, é uma mutação não rastreável."))
            continue
        trigger = t.get("trigger")
        result = resolve_anchor(trigger, context, mode) if trigger else None
        if not (result and result.get("ok") and result.get("strength") == "STRUCTURAL"):
            findings.append(finding(
                "ARBITRARY_STATE_MUTATION", "HIGH", None, eid,
                f"{eid}: transição {frm}->{to} com trigger não resolvido/não estrutural ({trigger!r}).",
                "O gatilho de uma transição precisa ser uma âncora STRUCTURAL resolvida "
                "(LEDGER:/SCENE:/TURN:/CHAPTER_FIELD:/TEXT:) — nunca um número de capítulo nu."))
            continue
        if mode != "plan" and isinstance(trigger, str) and trigger.startswith("LEDGER:EV-"):
            ledger = context.get("causal_ledger") or {}
            event_id = trigger.split(":", 1)[1]
            event = next((e for e in ledger.get("events") or [] if e.get("id") == event_id), None)
            if event and event.get("status") != "REALIZED":
                findings.append(finding(
                    "TRIGGER_NOT_REALIZED", "HIGH", None, eid,
                    f"{eid}: transição {frm}->{to} dispara em evento ainda PLANNED ({trigger}).",
                    "Só promover a transição depois que o evento correspondente virar REALIZED "
                    "no ledger causal."))
        if t.get("display_from", "NEXT_CHAPTER") == "SAME_CHAPTER" and not t.get("spoiler_ack"):
            findings.append(finding(
                "OPENER_PRE_ANNOUNCES_EVENT", "MEDIUM", None, eid,
                f"{eid}: transição {frm}->{to} usa display_from=SAME_CHAPTER sem spoiler_ack.",
                "A abertura de capítulo é vista antes da prosa: SAME_CHAPTER antecipa o "
                "evento. Use NEXT_CHAPTER (padrão), ou registre spoiler_ack com aprovação."))
        graph.setdefault(frm, []).append((to, result.get("chapter"), bool(t.get("reversible"))))
    return graph, findings


def _arrival_chapters(initial_id: str, graph: dict) -> dict[str, int | None]:
    """Capítulo em que cada estado se torna alcançável, via busca a partir
    do estado inicial. O inicial tem chapter=None (sempre "já alcançado")."""
    arrival: dict[str, int | None] = {initial_id: None}
    stack = [initial_id]
    while stack:
        node = stack.pop()
        for to, chapter, _reversible in graph.get(node, []):
            if to not in arrival:
                arrival[to] = chapter
                stack.append(to)
    return arrival


def _check_state_cycles(initial_id: str, graph: dict, eid: str) -> list[dict]:
    findings = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str):
        if node in visiting:
            findings.append(finding(
                "STATE_CYCLE_WITHOUT_CAUSE", "HIGH", None, eid,
                f"{eid}: ciclo de estado detectado envolvendo '{node}' sem transição reversible.",
                "Marcar a aresta de retorno como reversible: true (com âncora própria para a "
                "volta), ou remover o ciclo."))
            return
        if node in visited:
            return
        visiting.add(node)
        for to, _chapter, reversible in graph.get(node, []):
            if not reversible:
                visit(to)
        visiting.discard(node)
        visited.add(node)

    visit(initial_id)
    return findings


def _check_state_order(initial_id: str, graph: dict, eid: str) -> list[dict]:
    findings = []

    def walk(node: str, last_chapter: int | None, path: frozenset[str]):
        for to, chapter, reversible in graph.get(node, []):
            if reversible or to in path:
                continue
            if chapter is not None and last_chapter is not None and chapter < last_chapter:
                findings.append(finding(
                    "STATE_ORDER_VIOLATION", "HIGH", None, eid,
                    f"{eid}: transição para '{to}' (cap. {chapter}) ocorre antes da "
                    f"transição anterior no caminho (cap. {last_chapter}).",
                    "Triggers precisam avançar em ordem não decrescente de capítulo ao "
                    "longo de cada caminho de estado."))
            walk(to, chapter if chapter is not None else last_chapter, path | {to})

    walk(initial_id, None, frozenset({initial_id}))
    return findings


def _check_payoff_seed(eid: str, states: list[dict], arrival: dict, initial_id: str) -> list[dict]:
    findings = []
    memory_by_state = {s.get("id"): s.get("memory_state") for s in states}
    seed_ids = [sid for sid, m in memory_by_state.items() if m == "S"]
    if not seed_ids and memory_by_state.get(initial_id) is None:
        # Nenhum estado declara S explicitamente: o estado inicial é a
        # semente implícita, como em MEMORY_MOTIF_MAP (primeira aparição).
        seed_ids = [initial_id]
    seed_chapters = [arrival.get(sid) for sid in seed_ids]
    for state in states:
        if state.get("memory_state") != "P":
            continue
        payoff_chapter = arrival.get(state.get("id"))
        seeded = any(
            sc is None or (payoff_chapter is not None and sc < payoff_chapter)
            for sc in seed_chapters
        )
        if not seeded:
            findings.append(finding(
                "PAYOFF_WITHOUT_SEED", "HIGH", None, eid,
                f"{eid}: estado '{state.get('id')}' (payoff, memory_state=P) sem semente "
                "(memory_state=S) em capítulo anterior.",
                "Toda progressão com payoff precisa de uma semente estabelecida antes — "
                "mesma regra de MEMORY_MOTIF_MAP: sem payoff sem semente."))
    return findings


_PROTECTED_ROLE_TARGETS = {"BODY", "CHAPTER_TITLE", "MARGIN"}


def check_state_model(canon: dict, context: dict, mode: str = "plan") -> list[dict]:
    """ST-01..ST-09 (seção 14.3 da SDD) + RANDOM_SIGIL_MUTATION +
    OPENER_PRE_ANNOUNCES_EVENT, por elemento com `states`/`transitions`."""
    findings = []
    for element in canon.get("elements") or []:
        states = element.get("states") or []
        transitions = element.get("transitions") or []
        if not states and not transitions:
            continue
        eid = element.get("id")

        initials = [s for s in states if s.get("initial")]
        if len(initials) != 1:
            findings.append(finding(
                "STATE_MODEL_INVALID", "HIGH", None, eid,
                f"{eid}: esperado exatamente 1 estado com initial: true, encontrado {len(initials)}.",
                "Declarar exatamente um estado inicial."))

        for state in states:
            memory_state = state.get("memory_state")
            if memory_state is not None and memory_state not in MEMORY_STATE_VALUES:
                findings.append(finding(
                    "INVALID_ENUM", "HIGH", None, eid,
                    f"{eid}: memory_state inválido em '{state.get('id')}': {memory_state!r}.",
                    "Usar S | R | T | P | E."))
            if not (state.get("visual_description") or "").strip():
                findings.append(finding(
                    "STATE_BREAKS_CONSTRAINT", "HIGH", None, eid,
                    f"{eid}: estado '{state.get('id')}' sem visual_description.",
                    "Todo estado precisa de descrição visual própria — é o que garante um "
                    "sigil legível em P&B, sem depender de cor."))
            role = state.get("role") or (state.get("render") or {}).get("role")
            if role in _PROTECTED_ROLE_TARGETS:
                findings.append(finding(
                    "READING_LAYER_MUTATION", "BLOCKER", None, eid,
                    f"{eid}: estado '{state.get('id')}' tenta direcionar o papel protegido '{role}'.",
                    "Progressão narrativa nunca altera BODY, CHAPTER_TITLE ou margens (ST-09)."))

        if (element.get("accessibility") or {}).get("monochrome_safe"):
            for t in transitions:
                a = next((s for s in states if s.get("id") == t.get("from")), None)
                b = next((s for s in states if s.get("id") == t.get("to")), None)
                if a and b and _differs_only_by_color(a.get("visual_description", ""),
                                                       b.get("visual_description", "")):
                    findings.append(finding(
                        "STATE_DIFFERS_ONLY_BY_COLOR", "HIGH", None, eid,
                        f"{eid}: estados '{a.get('id')}' e '{b.get('id')}' só diferem por "
                        "palavra de cor na descrição.",
                        "Descrever uma diferença de FORMA entre os estados, não só de cor "
                        "— o sigil precisa funcionar em Kindle grayscale e impressão P&B."))

        state_ids = {s.get("id") for s in states if s.get("id")}
        graph, transition_findings = _build_transition_graph(element, context, mode, state_ids, eid)
        findings += transition_findings

        initial_id = initials[0].get("id") if len(initials) == 1 else None
        if initial_id:
            findings += _check_state_cycles(initial_id, graph, eid)
            findings += _check_state_order(initial_id, graph, eid)
            arrival = _arrival_chapters(initial_id, graph)
            findings += _check_payoff_seed(eid, states, arrival, initial_id)
    return findings


def project_state(element: dict, at_chapter: int, context: dict, mode: str = "plan") -> dict:
    """Projeta o estado de um elemento progressivo num capítulo — nunca lê
    nem escreve um "estado atual" salvo (14.4 da SDD)."""
    states = element.get("states") or []
    initial = next((s for s in states if s.get("initial")), None)
    current = initial.get("id") if initial else None
    edges = []
    for t in element.get("transitions") or []:
        trigger = t.get("trigger")
        result = resolve_anchor(trigger, context, mode) if trigger else None
        if not (result and result.get("ok")):
            continue
        chapter = result.get("chapter")
        display_from = t.get("display_from", "NEXT_CHAPTER")
        effective = None
        if chapter is not None:
            effective = chapter if display_from in ("SAME_CHAPTER", "AFTER_ANCHOR_IN_CHAPTER") else chapter + 1
        edges.append({"from": t.get("from"), "to": t.get("to"), "trigger": trigger,
                       "trigger_chapter": chapter, "display_from": display_from,
                       "effective_chapter": effective})
    trace = []
    while True:
        candidates = [e for e in edges if e["from"] == current and e["effective_chapter"] is not None
                      and e["effective_chapter"] <= at_chapter]
        if not candidates:
            break
        candidates.sort(key=lambda e: e["effective_chapter"])
        best = candidates[0]
        current = best["to"]
        trace.append(best)
        edges.remove(best)  # defesa contra grafo malformado com ciclo
    state_obj = next((s for s in states if s.get("id") == current), None)
    return {
        "state": current,
        "description": (state_obj or {}).get("visual_description"),
        "memory_state": (state_obj or {}).get("memory_state"),
        "trace": trace,
    }


def timeline_report(canon: dict, context: dict, mode: str = "plan") -> list[dict]:
    report = []
    for element in canon.get("elements") or []:
        if not element.get("transitions"):
            continue
        entries = []
        for t in element.get("transitions") or []:
            trigger = t.get("trigger")
            result = resolve_anchor(trigger, context, mode) if trigger else None
            chapter = result.get("chapter") if result and result.get("ok") else None
            display_from = t.get("display_from", "NEXT_CHAPTER")
            effective = None
            if chapter is not None:
                effective = chapter if display_from in ("SAME_CHAPTER", "AFTER_ANCHOR_IN_CHAPTER") else chapter + 1
            entries.append({"from": t.get("from"), "to": t.get("to"), "trigger": trigger,
                             "trigger_chapter": chapter, "display_from": display_from,
                             "effective_chapter": effective})
        entries.sort(key=lambda e: (e["effective_chapter"] is None, e["effective_chapter"]))
        report.append({"element": element.get("id"), "transitions": entries})
    return report


def end_state_report(canon: dict, context: dict, mode: str = "plan") -> list[dict]:
    far_future = 10 ** 9
    return [
        {"element": element.get("id"), **project_state(element, far_future, context, mode)}
        for element in canon.get("elements") or []
        if element.get("states")
    ]


def check_baseline_retcon(canon: dict, baseline: dict | None) -> list[dict]:
    """ST-08: transições de estados REALIZED são imutáveis contra o
    snapshot FREEZE — uma correção legítima vira mutation_log, nunca uma
    edição silenciosa (mesma regra do CAUSAL_LEDGER, L10/INV-10)."""
    findings = []
    if not baseline:
        return findings
    baseline_elements = {el.get("id"): el for el in baseline.get("elements") or [] if el.get("id")}
    watched = ("meaning", "functions", "states", "transitions", "class")
    for element in canon.get("elements") or []:
        eid = element.get("id")
        base = baseline_elements.get(eid)
        if not base or base.get("status") != "REALIZED" or element.get("status") != "REALIZED":
            continue
        current_slice = {k: element.get(k) for k in watched}
        base_slice = {k: base.get(k) for k in watched}
        if current_slice != base_slice:
            findings.append(finding(
                "VISUAL_RETCON", "BLOCKER", None, eid,
                f"{eid}: campos REALIZED (meaning/functions/states/transitions/class) mudaram "
                "contra o snapshot FREEZE.",
                "Reverter para o conteúdo do snapshot, ou registrar mutation_log com "
                "action: VISUAL_REVISION e uma nova aprovação — nunca editar silenciosamente "
                "o que já foi realizado."))
    return findings


# --- Narrative Artifacts (seção 19.2 da SDD) --------------------------------

def check_artifacts(canon: dict, context: dict, mode: str = "plan") -> list[dict]:
    findings = []
    for element in canon.get("elements") or []:
        if element.get("class") != "NARRATIVE_ARTIFACT":
            continue
        eid = element.get("id")

        artifact_type = element.get("artifact_type")
        if artifact_type and artifact_type not in ARTIFACT_TYPE_VALUES:
            findings.append(finding(
                "INVALID_ENUM", "HIGH", None, eid,
                f"{eid}: artifact_type inválido: {artifact_type!r}.",
                f"Usar um valor de {sorted(ARTIFACT_TYPE_VALUES)}."))

        canon_ref = element.get("canon_ref")
        if canon_ref:
            result = resolve_anchor(canon_ref, context, mode)
            if not (result and result.get("ok")):
                findings.append(finding(
                    "VISUAL_INVENTS_FACT", "HIGH", None, eid,
                    f"{eid}: canon_ref '{canon_ref}' não resolve contra o canon narrativo.",
                    "canon_ref precisa apontar para um fato/evento real (LEDGER: ou CANON:) — "
                    "o artefato cita canon, nunca o inventa."))

        if not element.get("in_world_owner"):
            findings.append(finding(
                "ARTIFACT_OWNER_UNKNOWN", "HIGH", None, eid,
                f"{eid} sem in_world_owner declarado.",
                "Todo artefato narrativo precisa de um dono in-world — id de personagem ou "
                "instituição já existente no canon."))

        content = element.get("content") or {}
        if content.get("mode") == "QUOTED":
            quotes = content.get("quotes") or []
            if not quotes:
                findings.append(finding(
                    "VISUAL_INVENTS_FACT", "HIGH", None, eid,
                    f"{eid}: content.mode=QUOTED sem quotes.",
                    "Citar ao menos um trecho literal (TEXT:) da prosa."))
            elif mode != "plan":
                # Em `plan` a prosa ainda não existe: a citação é uma
                # intenção, não uma prova. Só em realized+ ela precisa
                # resolver de verdade contra o manuscrito congelado.
                for quote in quotes:
                    result = resolve_anchor(quote, context, mode)
                    if not (result and result.get("ok")):
                        findings.append(finding(
                            "VISUAL_INVENTS_FACT", "HIGH", None, eid,
                            f"{eid}: citação '{quote}' não resolve na prosa congelada.",
                            "Corrigir a citação para um trecho literal existente, ou "
                            "aguardar o freeze do manuscrito."))

        first_appearance = element.get("first_appearance")
        first_result = resolve_anchor(first_appearance, context, mode) if first_appearance else None
        placement = element.get("placement") or {}
        anchor_token = placement.get("anchor")
        if first_result and first_result.get("ok") and anchor_token:
            anchor_result = resolve_anchor(anchor_token, context, mode)
            if (anchor_result and anchor_result.get("ok")
                    and first_result.get("chapter") is not None
                    and anchor_result.get("chapter") is not None
                    and anchor_result["chapter"] < first_result["chapter"]):
                findings.append(finding(
                    "ARTIFACT_BEFORE_FIRST_APPEARANCE", "HIGH", None, eid,
                    f"{eid}: placement.anchor (cap. {anchor_result['chapter']}) é anterior a "
                    f"first_appearance (cap. {first_result['chapter']}).",
                    "Mover o placement para depois da primeira aparição, ou corrigir "
                    "first_appearance."))

        accessibility = element.get("accessibility") or {}
        min_pt = accessibility.get("min_text_pt")
        if min_pt is not None and min_pt < 7 and content.get("mode") != "ILLEGIBLE_BY_DESIGN":
            findings.append(finding(
                "ARTIFACT_ILLEGIBLE", "HIGH", None, eid,
                f"{eid}: min_text_pt={min_pt} abaixo do piso KDP de 7pt.",
                "Aumentar o corpo do texto do artefato para pelo menos 7pt, ou marcar "
                "content.mode: ILLEGIBLE_BY_DESIGN deliberadamente (com transcrição no corpo, "
                "se o texto for necessário à trama)."))
    return findings


# --- Dust Jacket × Naked Hardcover (seção 19.5 da SDD) ----------------------
# DJ-01 e DJ-05 dependem de resolução de edição (EDITION_CAPABILITIES) —
# ficam para o Slice 3. Aqui: DJ-02, DJ-03, DJ-04, que são fatos do canon
# do livro, sem precisar saber para qual alvo ele vai ser publicado.

def check_duality(canon: dict, author_dna: dict, context: dict, mode: str = "plan") -> list[dict]:
    findings = []
    duality = (canon.get("book_dna") or {}).get("duality")
    if not duality:
        return findings

    anchors = duality.get("anchors") or []
    unresolved = [a for a in anchors if not (resolve_anchor(a, context, mode) or {}).get("ok")]
    if not anchors or unresolved:
        findings.append(finding(
            "UNJUSTIFIED", "HIGH", None, "book_dna.duality",
            f"duality.anchors não resolvem: {unresolved or 'nenhuma âncora declarada'}.",
            "A dualidade (outer_truth/hidden_truth) precisa ser ancorada em fatos reais do "
            "canon narrativo (DJ-04) — nunca uma promessa de marketing."))

    hidden_ceiling = (author_dna.get("invariants") or {}).get("hidden_surface_max_spoiler", "MEDIUM")
    hidden_ceiling_rank = SPOILER_RANK.get(hidden_ceiling, 2)
    elements_by_id = {el.get("id"): el for el in canon.get("elements") or []}

    outer_elements: set[str] = set()
    hidden_elements: set[str] = set()
    for composition in canon.get("compositions") or []:
        layer = composition.get("reading_layer")
        refs = {ref.get("element") for ref in composition.get("elements") or []}
        if layer == "OUTER_TRUTH":
            outer_elements |= refs
        elif layer == "HIDDEN_TRUTH":
            hidden_elements |= refs
            for element_id in refs:
                element = elements_by_id.get(element_id)
                if not element:
                    continue
                level = (element.get("exposure") or {}).get("spoiler_level", "NONE")
                if SPOILER_RANK.get(level, 0) > hidden_ceiling_rank:
                    findings.append(finding(
                        "HIDDEN_SURFACE_SPOILER", "HIGH", None, composition.get("id"),
                        f"{element_id} em {composition.get('id')} (HIDDEN_TRUTH) tem "
                        f"spoiler_level={level}, acima do teto {hidden_ceiling}.",
                        "Reduzir spoiler_level, ou mover a revelação para depois do "
                        "capítulo apropriado (hidden_surface_max_spoiler da autora)."))

    if outer_elements and hidden_elements and not (outer_elements & hidden_elements):
        findings.append(finding(
            "DUALITY_WITHOUT_SHARED_ELEMENT", "MEDIUM", None, "book_dna.duality",
            "Nenhum elemento aparece nas composições OUTER_TRUTH e HIDDEN_TRUTH ao mesmo tempo.",
            "A dualidade precisa ser do MESMO símbolo em duas leituras, não duas capas "
            "sem relação — compartilhe ao menos um elemento entre as duas composições."))
    return findings


# --- Spoiler Safety (seção 26.1 da SDD) -------------------------------------

def surface_exposure(composition: dict) -> tuple[str, int | None]:
    """(categoria, capítulo_de_exposição). categoria é PUBLIC, SEMI_HIDDEN
    ou CHAPTER_SCOPED. A camada de leitura (HIDDEN_TRUTH) manda mais que o
    nome literal da superfície — um case laminate sob sobrecapa é
    semiescondido mesmo chamando-se CASE_FRONT; a promoção para PÚBLICO
    quando o alvo não tem sobrecapa física (DJ-05) é decisão de edição,
    Slice 3."""
    surface = composition.get("surface")
    layer = composition.get("reading_layer", "NEUTRAL")
    if layer == "HIDDEN_TRUTH":
        return "SEMI_HIDDEN", None
    if surface in CHAPTER_SCOPED_SURFACES:
        return "CHAPTER_SCOPED", composition.get("chapter")
    if surface in SEMI_HIDDEN_SURFACES:
        return "SEMI_HIDDEN", None
    return "PUBLIC", None


def effective_reveal(element: dict, context: dict, mode: str = "plan") -> dict | None:
    """A âncora de revelação declarada, ou — se ausente — derivada
    automaticamente de `reader_access` do ledger causal quando o elemento
    cita uma Ground Truth (aplica INV-12 da SDD irmã a pixels: o leitor não
    pode ver o que a GT ainda não libera)."""
    exposure = element.get("exposure") or {}
    token = exposure.get("reveal")
    if token:
        return resolve_anchor(token, context, mode)
    ledger = context.get("causal_ledger")
    if not ledger:
        return None
    for fn in element.get("functions") or []:
        for anchor in fn.get("anchors") or []:
            if isinstance(anchor, str) and anchor.startswith("LEDGER:GT-"):
                gt_id = anchor.split(":", 1)[1]
                for char in ledger.get("characters") or []:
                    for gt in char.get("ground_truth") or []:
                        if gt.get("id") == gt_id:
                            access = gt.get("reader_access")
                            if isinstance(access, dict) and access.get("from_event"):
                                return resolve_anchor(f"LEDGER:{access['from_event']}", context, mode)
    return None


def check_spoiler_safety(canon: dict, author_dna: dict, context: dict, mode: str = "plan") -> list[dict]:
    findings = []
    invariants = author_dna.get("invariants") or {}
    public_ceiling = invariants.get("public_surface_max_spoiler", "LOW")
    hidden_ceiling = invariants.get("hidden_surface_max_spoiler", "MEDIUM")
    elements_by_id = {el.get("id"): el for el in canon.get("elements") or []}

    for composition in canon.get("compositions") or []:
        category, comp_chapter = surface_exposure(composition)
        for ref in composition.get("elements") or []:
            element = elements_by_id.get(ref.get("element"))
            if not element:
                continue
            exposure = element.get("exposure") or {}
            level = exposure.get("spoiler_level", "NONE")
            if level == "NONE":
                # Um elemento declarado sem risco de spoiler não é
                # spoiler-gated só porque uma de suas âncoras de SUPORTE
                # (Chekhov) cita uma GT com revelação futura — a presença
                # visual do motivo (ex.: o cisne na capa desde o capítulo 1)
                # não é a mesma coisa que expor o segredo por trás dele.
                continue
            level_rank = SPOILER_RANK.get(level, 0)
            reveal = effective_reveal(element, context, mode)

            if category in ("PUBLIC", "SEMI_HIDDEN"):
                ceiling = public_ceiling if category == "PUBLIC" else hidden_ceiling
                ceiling_rank = SPOILER_RANK.get(ceiling, 1)
                if level_rank > ceiling_rank:
                    severity = "BLOCKER" if (level == "CORE" and category == "PUBLIC") else "HIGH"
                    findings.append(finding(
                        "SURFACE_SPOILER", severity, None, f"{element.get('id')}@{composition.get('id')}",
                        f"{element.get('id')} tem spoiler_level={level} em {composition.get('id')} "
                        f"({category}), acima do teto {ceiling}.",
                        "Reduzir o spoiler_level, ou mover o elemento para uma superfície "
                        "semiescondida/chapter-scoped compatível com sua revelação."))

            if level_rank >= SPOILER_RANK["MEDIUM"] and not (reveal and reveal.get("ok")):
                findings.append(finding(
                    "SPOILER_UNANCHORED", "HIGH", None, f"{element.get('id')}@{composition.get('id')}",
                    f"{element.get('id')}: spoiler_level={level} sem exposure.reveal resolvível.",
                    "Toda revelação de MEDIUM+ precisa de uma âncora de reveal (LEDGER:/SCENE:) "
                    "que prove quando ela deixa de ser segredo."))

            if reveal and reveal.get("ok") and reveal.get("chapter") is not None:
                if category == "CHAPTER_SCOPED":
                    exposure_chapter = comp_chapter if comp_chapter is not None else 0
                else:
                    exposure_chapter = 0
                if exposure_chapter < reveal["chapter"]:
                    findings.append(finding(
                        "PREMATURE_EXPOSURE", "HIGH", None, f"{element.get('id')}@{composition.get('id')}",
                        f"{element.get('id')} exposto em {composition.get('id')} (cap. "
                        f"{exposure_chapter}) antes de sua revelação (cap. {reveal['chapter']}).",
                        "Adiar a exposição para depois do capítulo de revelação, ou remover "
                        "o elemento dessa superfície."))
    return findings


def exposure_report(canon: dict, author_dna: dict, context: dict, mode: str = "plan") -> list[dict]:
    invariants = author_dna.get("invariants") or {}
    public_ceiling = invariants.get("public_surface_max_spoiler", "LOW")
    hidden_ceiling = invariants.get("hidden_surface_max_spoiler", "MEDIUM")
    elements_by_id = {el.get("id"): el for el in canon.get("elements") or []}
    rows = []
    for composition in canon.get("compositions") or []:
        category, comp_chapter = surface_exposure(composition)
        for ref in composition.get("elements") or []:
            element = elements_by_id.get(ref.get("element"))
            if not element:
                continue
            exposure = element.get("exposure") or {}
            reveal = effective_reveal(element, context, mode)
            ceiling = {"PUBLIC": public_ceiling, "SEMI_HIDDEN": hidden_ceiling}.get(category)
            rows.append({
                "element": element.get("id"), "composition": composition.get("id"),
                "surface": composition.get("surface"), "category": category,
                "spoiler_level": exposure.get("spoiler_level", "NONE"), "ceiling": ceiling,
                "reveal_chapter": reveal.get("chapter") if reveal and reveal.get("ok") else None,
                "exposure_chapter": comp_chapter if category == "CHAPTER_SCOPED" else 0,
            })
    return rows


# --- Human-in-the-loop (seção 26.2 da SDD) ----------------------------------

_APPROVAL_HASH_RE = re.compile(r"subject_sha256:\s*([0-9a-f]{64})")


def canonical_block_sha256(block: dict) -> str:
    return hashlib.sha256(json.dumps(block, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def load_approval_record(runtime: Path, approval_id: str) -> dict | None:
    path = runtime / "project_state" / "APPROVALS" / "VISUAL" / f"{approval_id}.md"
    if not path.is_file():
        return None
    match = _APPROVAL_HASH_RE.search(path.read_text(encoding="utf-8"))
    return {"path": path, "subject_sha256": match.group(1) if match else None}


def check_approvals(canon: dict, runtime: Path | None) -> list[dict]:
    """O motor nunca escreve o arquivo de aprovação — é o único ponto do
    pipeline em que a decisão não é automatizável por desenho (mesma regra
    de `requires_human_approval` do runtime_taskgraph.py)."""
    findings = []
    if runtime is None:
        return findings
    approvable = (
        [("elements", el) for el in canon.get("elements") or []]
        + [("compositions", comp) for comp in canon.get("compositions") or []]
        + [("finish_intents", fi) for fi in canon.get("finish_intents") or []]
    )
    for _kind, item in approvable:
        approval = item.get("approval") or {}
        if approval.get("policy") != "REQUIRE_APPROVAL":
            continue
        item_id = item.get("id")
        approval_id = approval.get("id")
        if not approval_id:
            findings.append(finding(
                "APPROVAL_MISSING", "MEDIUM", None, item_id,
                f"{item_id} exige aprovação (REQUIRE_APPROVAL) mas não declara approval.id.",
                "Atribuir um id de aprovação (APR-xx) e registrar o arquivo humano "
                "correspondente em project_state/APPROVALS/VISUAL/."))
            continue
        record = load_approval_record(runtime, approval_id)
        block_hash = canonical_block_sha256(item)
        if record is None:
            findings.append(finding(
                "PENDING_APPROVAL", "MEDIUM", None, item_id,
                f"{item_id} aguarda aprovação humana ({approval_id}).",
                f"Criar project_state/APPROVALS/VISUAL/{approval_id}.md com "
                f"subject_sha256: {block_hash}."))
        elif record.get("subject_sha256") != block_hash:
            findings.append(finding(
                "APPROVAL_STALE", "HIGH", None, item_id,
                f"{item_id} mudou depois da aprovação {approval_id} (hash não confere).",
                "Revisar a mudança e reaprovar, atualizando subject_sha256 no arquivo "
                "de aprovação — nunca tratar uma aprovação antiga como ainda válida."))
    return findings


# --- Edition Model (seções 15, 16, 20.2, 21, 22 da SDD) — Slice 3 ----------

EDITION_TARGETS = ("kindle_ebook", "kdp_paperback", "kdp_hardcover", "collector")

_ENGINE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CAPABILITIES_PATH = _ENGINE_ROOT / "templates" / "EDITION_CAPABILITIES.yaml"
DEFAULT_PRINT_GEOMETRY_PATH = _ENGINE_ROOT / "templates" / "PRINT_GEOMETRY.yaml"

# Mapeamento de superfície canônica -> superfície do alvo (seção 15.2 da
# SDD). Ausência de chave = OMIT (a superfície não existe nesse alvo — Slice
# 3 nunca perde uma composição silenciosamente: resolve_composition_surface
# sempre devolve status INCLUDED/OMITTED com motivo).
#
# Simplificação registrada: `collector.SPINE -> DUST_JACKET_SPINE` só. A
# SDD descreve a lombada do collector como DUST_JACKET_SPINE + CASE_SPINE
# (duas superfícies para uma composição). Modelar isso plenamente exigiria
# mapeamento um-para-muitos, que nenhuma outra linha desta tabela precisa;
# um livro que queira uma lombada nua distinta declara sua própria
# composição com surface: CASE_SPINE (já suportado via mapeamento direto).
SURFACE_MAP: dict[str, dict[str, str]] = {
    "kindle_ebook": {
        "FRONT_COVER": "MARKETING_COVER",
        "TITLE_PAGE": "TITLE_PAGE", "COPYRIGHT_PAGE": "COPYRIGHT_PAGE",
        "CHAPTER_OPENER": "CHAPTER_OPENER", "INTERIOR_PLATE": "INTERIOR_PLATE",
        "PROMO": "PROMO", "INTERNAL_COVER": "INTERNAL_COVER",
    },
    "kdp_paperback": {
        "FRONT_COVER": "FRONT_COVER", "BACK_COVER": "BACK_COVER", "SPINE": "SPINE",
        "TITLE_PAGE": "TITLE_PAGE", "COPYRIGHT_PAGE": "COPYRIGHT_PAGE",
        "CHAPTER_OPENER": "CHAPTER_OPENER", "INTERIOR_PLATE": "INTERIOR_PLATE",
    },
    "kdp_hardcover": {
        "FRONT_COVER": "CASE_FRONT", "BACK_COVER": "CASE_BACK", "SPINE": "CASE_SPINE",
        "CASE_FRONT": "CASE_FRONT", "CASE_BACK": "CASE_BACK", "CASE_SPINE": "CASE_SPINE",
        "TITLE_PAGE": "TITLE_PAGE", "COPYRIGHT_PAGE": "COPYRIGHT_PAGE",
        "CHAPTER_OPENER": "CHAPTER_OPENER", "INTERIOR_PLATE": "INTERIOR_PLATE",
    },
    "collector": {
        "FRONT_COVER": "DUST_JACKET_FRONT", "BACK_COVER": "DUST_JACKET_BACK",
        "SPINE": "DUST_JACKET_SPINE",
        "CASE_FRONT": "CASE_FRONT", "CASE_BACK": "CASE_BACK", "CASE_SPINE": "CASE_SPINE",
        "DUST_JACKET_FRONT": "DUST_JACKET_FRONT", "DUST_JACKET_BACK": "DUST_JACKET_BACK",
        "DUST_JACKET_SPINE": "DUST_JACKET_SPINE",
        "DUST_JACKET_FLAP_FRONT": "DUST_JACKET_FLAP_FRONT", "DUST_JACKET_FLAP_BACK": "DUST_JACKET_FLAP_BACK",
        "ENDPAPER_FRONT": "ENDPAPER_FRONT", "ENDPAPER_BACK": "ENDPAPER_BACK",
        "EDGE_TOP": "EDGE_TOP", "EDGE_FORE": "EDGE_FORE", "EDGE_BOTTOM": "EDGE_BOTTOM",
        "TITLE_PAGE": "TITLE_PAGE", "COPYRIGHT_PAGE": "COPYRIGHT_PAGE",
        "CHAPTER_OPENER": "CHAPTER_OPENER", "INTERIOR_PLATE": "INTERIOR_PLATE",
        "INSERT": "INSERT", "RIBBON": "RIBBON", "PROMO": "PROMO",
        "SLIPCASE_FRONT": "SLIPCASE_FRONT", "SLIPCASE_SPINE": "SLIPCASE_SPINE",
    },
}

_MEANING_FIELDS = {"meaning", "functions", "elements", "class", "first_appearance"}

_MASK_KIND_BY_EFFECT = {
    "METALLIC_FOIL": "FOIL_MASK", "EMBOSS": "EMBOSS_MASK", "DEBOSS": "DEBOSS_MASK",
    "SPOT_UV": "SPOT_UV_MASK", "SELECTIVE_VARNISH": "SPOT_UV_MASK",
    "SPRAYED_EDGE": "EDGE_ART", "STENCILED_EDGE": "EDGE_ART",
    "MIRROR_BOARD": "MIRROR_MASK", "METALLIZED_PAPER": "MIRROR_MASK", "BLIND_EMBOSS": "EMBOSS_MASK",
}


def resolve_composition_surface(composition: dict, target: str) -> tuple[str | None, str | None]:
    """(superfície mapeada ou None, nota). HIDDEN_TRUTH nunca migra para um
    alvo sem sobrecapa física — DJ-01/05: só `collector` a recebe (como
    CASE_* nu, atrás da sobrecapa); todo outro alvo omite."""
    surface = composition.get("surface")
    layer = composition.get("reading_layer", "NEUTRAL")
    if layer == "HIDDEN_TRUTH" and target != "collector":
        return None, "HIDDEN_TRUTH omitido: alvo sem sobrecapa física para esconder atrás (DJ-01/05)"
    mapped = SURFACE_MAP.get(target, {}).get(surface)
    if mapped is None:
        return None, f"superfície '{surface}' não existe no alvo {target}"
    return mapped, None


def resolve_edition_plan(canon: dict, capabilities: dict, target: str,
                          printer_profile: dict | None = None) -> dict:
    """Projeção EDITION_PLAN — nunca armazenada, sempre recalculada (VP-03:
    design once, render by edition). Determinística: mesma entrada, mesmo
    resultado byte a byte."""
    compositions_out = []
    for composition in canon.get("compositions") or []:
        mapped, note = resolve_composition_surface(composition, target)
        compositions_out.append({
            "composition": composition.get("id"),
            "canonical_surface": composition.get("surface"),
            "reading_layer": composition.get("reading_layer", "NEUTRAL"),
            "mapped_surface": mapped,
            "status": "INCLUDED" if mapped else "OMITTED",
            "note": note,
        })
    finishes_out = []
    for finish_intent in canon.get("finish_intents") or []:
        resolution = resolve_finish_intent(finish_intent, target, capabilities, printer_profile)
        finishes_out.append({"finish_intent": finish_intent.get("id"), **resolution})
    return {
        "target": target,
        "compositions": compositions_out,
        "finish_intents": finishes_out,
        "printer_profile_confirmed": printer_profile is not None,
    }


def resolve_finish_intent(finish_intent: dict, target: str, capabilities: dict,
                           printer_profile: dict | None = None) -> dict:
    """Algoritmo determinístico da seção 15.3 da SDD."""
    target_cfg = (capabilities.get("targets") or {}).get(target, {})
    cost_class = finish_intent.get("cost_class", "OPTIONAL")

    if cost_class == "COLLECTOR_ONLY" and target != "collector":
        return {"effect": None, "level": "OMIT", "reason": "COLLECTOR_ONLY fora do alvo collector",
                "printer_unconfirmed": False}
    budget = target_cfg.get("budget") or []
    if cost_class not in budget:
        return {"effect": None, "level": "OMIT", "reason": f"{cost_class} fora do orçamento de {target}",
                "printer_unconfirmed": False}

    effects_cfg = target_cfg.get("effects") or {}
    candidates = [finish_intent.get("preferred_effect")] + list(finish_intent.get("fallbacks") or [])
    attempted_vendor_dependent = False
    for effect in candidates:
        if not effect:
            continue
        level = effects_cfg.get(effect, "UNSUPPORTED")
        if level in ("PHYSICAL", "SIMULATED"):
            return {"effect": effect, "level": level, "reason": None, "printer_unconfirmed": False}
        if level == "VENDOR_DEPENDENT":
            confirmed = bool(printer_profile) and effect in ((printer_profile or {}).get("confirmed_effects") or [])
            if confirmed:
                return {"effect": effect, "level": "PHYSICAL",
                        "reason": "confirmado pelo perfil de gráfica (layout/PRINTER_PROFILE.yaml)",
                        "printer_unconfirmed": False}
            attempted_vendor_dependent = True

    if cost_class == "ESSENTIAL":
        return {"effect": None, "level": "BLOCKER", "reason": "ESSENTIAL_UNRENDERABLE",
                "printer_unconfirmed": attempted_vendor_dependent}
    reason = ("nenhum efeito da escada confirmado pelo perfil de gráfica" if attempted_vendor_dependent
              else "nenhum efeito da escada é PHYSICAL/SIMULATED neste alvo")
    return {"effect": None, "level": "OMIT", "reason": reason, "printer_unconfirmed": attempted_vendor_dependent}


def check_edition_semantic_stability(canon: dict, target: str) -> list[dict]:
    """VP-03: edição só escolhe manifestação — nunca significado."""
    findings = []
    for override in (canon.get("book_dna") or {}).get("role_overrides") or []:
        if override.get("edition") != target:
            continue
        key = override.get("key", "")
        field = key.split(".")[-1] if key else ""
        if field in _MEANING_FIELDS:
            findings.append(finding(
                "EDITION_CHANGES_MEANING", "BLOCKER", None, key,
                f"override por edição '{target}' tenta mudar '{key}', que é significado, não manifestação.",
                "Edição só pode escolher manifestação (efeito, fallback, geometria, binding de "
                "fonte) — significado é definido uma vez no canon do livro (design once, "
                "render by edition; VP-03)."))
    return findings


def check_finish_intent_chekhov(canon: dict, status_map: dict) -> list[dict]:
    """20.2/22.3: todo acabamento aponta para um elemento com significado
    real — 'foil porque é premium' falha o mesmo Chekhov que qualquer
    outro elemento destacado."""
    findings = []
    elements_by_id = {el.get("id"): el for el in canon.get("elements") or []}
    for finish_intent in canon.get("finish_intents") or []:
        fi_id = finish_intent.get("id")
        meaning_element = finish_intent.get("meaning_element")
        if not meaning_element or meaning_element not in elements_by_id:
            findings.append(finding(
                "FINISH_WITHOUT_CHEKHOV", "HIGH", None, fi_id,
                f"{fi_id}: meaning_element {meaning_element!r} não existe no canon.",
                "Todo acabamento especial precisa apontar para um elemento com significado "
                "real (meaning_element) — nunca solto."))
            continue
        status, _ = status_map.get(meaning_element, (None, {}))
        if status not in ("PROVEN", "SUPPORTED"):
            findings.append(finding(
                "FINISH_WITHOUT_CHEKHOV", "HIGH", None, fi_id,
                f"{fi_id}: meaning_element '{meaning_element}' tem status Chekhov {status}.",
                "Um acabamento (foil, spot UV, emboss) precisa apontar para um elemento com "
                "suporte narrativo comprovado — 'foil porque é premium' não é significado."))
    return findings


def check_edition_plan(canon: dict, target: str, plan: dict, status_map: dict) -> list[dict]:
    """V7: agrega os achados que dependem de uma edição já resolvida."""
    findings = []
    for entry in plan.get("compositions") or []:
        if (entry.get("reading_layer") == "HIDDEN_TRUTH" and target != "collector"
                and entry.get("status") == "INCLUDED"):
            findings.append(finding(
                "HIDDEN_TRUTH_EXPOSED", "BLOCKER", None, entry.get("composition"),
                f"{entry.get('composition')} (HIDDEN_TRUTH) ficou INCLUDED no alvo {target}, que "
                "não tem sobrecapa física para escondê-la atrás.",
                "HIDDEN_TRUTH só pode existir em superfície semiescondida de um alvo com "
                "sobrecapa física (hoje, só collector) — em qualquer outro alvo, omitir."))
    for entry in plan.get("finish_intents") or []:
        if entry.get("level") == "BLOCKER":
            findings.append(finding(
                "ESSENTIAL_UNRENDERABLE", "BLOCKER", None, entry.get("finish_intent"),
                f"{entry.get('finish_intent')}: nenhum efeito da escada resolve para {target}, "
                "mas cost_class é ESSENTIAL.",
                "Adicionar um fallback que resolva neste alvo (no mínimo FLAT_ROLE_COLOR), ou "
                "rebaixar cost_class se o acabamento não for de fato essencial."))
        elif entry.get("printer_unconfirmed"):
            findings.append(finding(
                "PRINTER_UNCONFIRMED", "MEDIUM", None, entry.get("finish_intent"),
                f"{entry.get('finish_intent')}: efeito VENDOR_DEPENDENT não confirmado por "
                "layout/PRINTER_PROFILE.yaml — degradou para fallback/omissão.",
                "Registrar o perfil de gráfica confirmando o efeito, se ele for realmente "
                "necessário nesta edição collector."))
    findings += check_edition_semantic_stability(canon, target)
    findings += check_finish_intent_chekhov(canon, status_map)
    return findings


FINISH_PROMISE_TERMS: dict[str, str] = {
    "foil": "METALLIC_FOIL", "hot foil": "METALLIC_FOIL", "folha de ouro": "METALLIC_FOIL",
    "emboss": "EMBOSS", "relevo": "EMBOSS", "deboss": "DEBOSS",
    "spot uv": "SPOT_UV", "verniz localizado": "SPOT_UV",
    "sprayed edge": "SPRAYED_EDGE", "borda pintada": "SPRAYED_EDGE", "stenciled edge": "STENCILED_EDGE",
    "dust jacket": "DUST_JACKET", "sobrecapa": "DUST_JACKET",
    "cloth case": "CLOTH_CASE", "capa de tecido": "CLOTH_CASE",
    # 1.1.0 (NARCISO SDD, 21.4 e TRAP-05)
    "espelhada": "MIRROR_BOARD", "espelhado": "MIRROR_BOARD", "mirror board": "MIRROR_BOARD",
    "papel metalizado": "METALLIZED_PAPER", "relevo seco": "BLIND_EMBOSS", "blind emboss": "BLIND_EMBOSS",
    "slipcase": "SLIPCASE", "fita marcadora": "RIBBON_MARKER", "marcador de fita": "RIBBON_MARKER",
    "guardas ilustradas": "PRINTED_ENDPAPER", "cards colecionáveis": "INSERT_CARD",
}
# Promessas de produção não são efeitos de impressão: só valem no collector e
# com o perfil de gráfica declarando `production.<chave>: true`.
PRODUCTION_PROMISE_TERMS: dict[str, str] = {
    "numerada": "numbered", "exemplares numerados": "numbered", "numbered edition": "numbered",
    "assinada": "signed", "autografada": "signed", "signed edition": "signed",
    "edição limitada": "limited", "tiragem limitada": "limited", "limited edition": "limited",
}
# efeitos que satisfazem a mesma promessa de superfície espelhada
_EQUIVALENT_PROMISE_EFFECTS = {"MIRROR_BOARD": {"MIRROR_BOARD", "METALLIZED_PAPER"},
                               "EMBOSS": {"EMBOSS", "BLIND_EMBOSS"}}


def check_finish_promise(plan: dict, text: str | None, printer_profile: dict | None = None) -> list[dict]:
    """21.5: o motor nunca gera texto de marketing afirmando acabamento não
    fabricado. `text` é qualquer conteúdo de saída (descrição KDP, relatório
    de produção de capa) a varrer — função pura, pronta para ser chamada
    sobre os arquivos reais de mídia quando eles existirem (Slice 6)."""
    findings = []
    if not text:
        return findings
    physical_effects = {f.get("effect") for f in plan.get("finish_intents") or [] if f.get("level") == "PHYSICAL"}
    lowered = text.lower()
    for term, effect in FINISH_PROMISE_TERMS.items():
        if term in lowered and not (_EQUIVALENT_PROMISE_EFFECTS.get(effect, {effect}) & physical_effects):
            findings.append(finding(
                "FINISH_PROMISE_MISMATCH", "HIGH", None, plan.get("target"),
                f"texto promete '{term}' ({effect}) mas o plano de {plan.get('target')} não tem "
                "esse efeito como PHYSICAL.",
                "Remover a promessa do texto, ou confirmar o acabamento físico real (perfil de "
                "gráfica, para collector) antes de publicar a descrição."))
    production = (printer_profile or {}).get("production") or {}
    for term, key in PRODUCTION_PROMISE_TERMS.items():
        if term in lowered and not (plan.get("target") == "collector" and production.get(key) is True):
            findings.append(finding(
                "FINISH_PROMISE_MISMATCH", "HIGH", None, plan.get("target"),
                f"texto promete '{term}' ({key}) sem produção confirmada para {plan.get('target')}.",
                "Numeração, assinatura e tiragem limitada são decisão humana de produção do collector "
                "(PRINTER_PROFILE.production) — nunca promessa de alvo KDP."))
    return findings


def check_zone_collisions(canon: dict, geometry: dict | None, fold_variance_in: float | None) -> list[dict]:
    """21.4: elemento de lombada cuja zona invade a tolerância de dobra."""
    findings = []
    if not geometry or not fold_variance_in:
        return findings
    spine_in = geometry.get("spine_in")
    if not spine_in or spine_in <= 0:
        return findings
    clearance = fold_variance_in / spine_in
    for composition in canon.get("compositions") or []:
        if composition.get("surface") != "SPINE":
            continue
        for ref in composition.get("elements") or []:
            zone = ref.get("zone")
            if not zone or len(zone) != 4:
                continue
            x0, _y0, x1, _y1 = zone
            if x0 < clearance or x1 > (1 - clearance):
                findings.append(finding(
                    "ZONE_COLLIDES_WITH_MANUFACTURING", "HIGH", None, composition.get("id"),
                    f"{composition.get('id')}: zona [{x0},{x1}] do elemento '{ref.get('element')}' "
                    f"invade a tolerância de dobra da lombada ({fold_variance_in}\" de {spine_in}\").",
                    "Recuar a zona do elemento para dentro da faixa segura da lombada — a "
                    "impressão real pode variar até essa tolerância em cada dobra."))
    return findings


def compute_kindle_geometry(print_geometry: dict) -> tuple[dict | None, list[dict]]:
    kindle = (print_geometry or {}).get("kindle_ebook") or {}
    px = kindle.get("marketing_cover_px") or {}
    if not px.get("width") or not px.get("height"):
        return None, [finding(
            "MANUFACTURING_FACT_UNVERIFIED", "HIGH", None, "kindle_ebook",
            "PRINT_GEOMETRY.yaml não declara marketing_cover_px completo para kindle_ebook.",
            "Declarar width/height em pixels antes de calcular geometria.")]
    return {"target": "kindle_ebook", "unit": "px", "width_px": px["width"], "height_px": px["height"],
            "min_dpi": kindle.get("min_dpi")}, []


def _paper_key(interior: dict) -> str | None:
    ink, paper = interior.get("ink"), interior.get("paper")
    if not ink or not paper:
        return None
    return f"{ink}/{paper}" if ink == "BLACK" else paper


def compute_paperback_geometry(print_spec: dict, print_geometry: dict) -> tuple[dict | None, list[dict]]:
    spec = (print_spec or {}).get("kdp_paperback") or {}
    geom = (print_geometry or {}).get("kdp_paperback") or {}

    page_count = spec.get("page_count")
    if page_count is None:
        return None, [finding(
            "PAGE_COUNT_UNKNOWN", "HIGH", None, "kdp_paperback",
            "layout/PRINT_SPEC.yaml (kdp_paperback) não declara page_count.",
            "Medir a contagem final de páginas no render (T704/T705) antes de calcular a "
            "geometria — o motor não estima contagem de páginas.")]

    trim = spec.get("trim_in") or {}
    width, height = trim.get("width"), trim.get("height")
    if width is None or height is None:
        return None, [finding(
            "PAGE_COUNT_UNKNOWN", "HIGH", None, "kdp_paperback",
            "layout/PRINT_SPEC.yaml (kdp_paperback) não declara trim_in completo.",
            "Declarar trim_in.width e trim_in.height.")]

    paper_key = _paper_key(spec.get("interior") or {})
    spine_table = geom.get("spine_in_per_page")
    bleed = geom.get("bleed_in")
    unverified = []
    factor = None
    if not isinstance(spine_table, dict) or spine_table.get("status") == "TO_VERIFY":
        unverified.append("spine_in_per_page")
    else:
        factor = spine_table.get(paper_key)
        if factor is None:
            unverified.append(f"spine_in_per_page[{paper_key}]")
    if bleed is None:
        unverified.append("bleed_in")
    if unverified:
        return None, [finding(
            "MANUFACTURING_FACT_UNVERIFIED", "HIGH", None, "kdp_paperback",
            f"fatos de fabricação não verificados: {unverified}.",
            "Confirmar os valores em engine/templates/PRINT_GEOMETRY.yaml (fonte oficial) "
            "antes de calcular a geometria — nunca inventar um número.")]

    spine_in = round(page_count * factor, 4)
    full_width_in = round(bleed + width + spine_in + width + bleed, 4)
    full_height_in = round(height + 2 * bleed, 4)
    geometry = {
        "target": "kdp_paperback", "unit": "in", "page_count": page_count,
        "spine_in": spine_in, "full_width_in": full_width_in, "full_height_in": full_height_in,
        "back_cover": [bleed, bleed, bleed + width, bleed + height],
        "spine_zone": [bleed + width, bleed, bleed + width + spine_in, bleed + height],
        "front_cover": [bleed + width + spine_in, bleed, bleed + 2 * width + spine_in, bleed + height],
        "spine_text_allowed": page_count >= (geom.get("spine_text_min_pages") or 10 ** 9),
        "pixels_per_inch": 300,
    }
    return geometry, []


def compute_hardcover_geometry(print_spec: dict, print_geometry: dict) -> tuple[dict | None, list[dict]]:
    spec = (print_spec or {}).get("kdp_hardcover") or {}
    geom = (print_geometry or {}).get("kdp_hardcover") or {}

    page_count = spec.get("page_count")
    if page_count is None:
        return None, [finding(
            "PAGE_COUNT_UNKNOWN", "HIGH", None, "kdp_hardcover",
            "layout/PRINT_SPEC.yaml (kdp_hardcover) não declara page_count.",
            "Medir a contagem final de páginas no render antes de calcular a geometria.")]

    spine_table = geom.get("spine_in_per_page")
    # No template atual, isto é SEMPRE {status: TO_VERIFY, ...} — OQ-8/D-V8
    # não foram confirmados em fonte oficial. Este bloqueio é intencional,
    # não um bug: o motor recusa calcular geometria de hardcover até um
    # humano confirmar o fator real no KDP Cover Calculator.
    if not isinstance(spine_table, dict) or not isinstance(spine_table.get("value"), (int, float)):
        return None, [finding(
            "MANUFACTURING_FACT_UNVERIFIED", "HIGH", None, "kdp_hardcover",
            "fator de lombada de hardcover (spine_in_per_page) ainda não verificado em fonte "
            "oficial (OQ-8, D-V8 da SDD).",
            "Obter o fator real no KDP Cover Calculator (Hardcover) e atualizar "
            "engine/templates/PRINT_GEOMETRY.yaml com um valor numérico verificado.")]

    trim = spec.get("trim_in") or {}
    width, height = trim.get("width"), trim.get("height")
    wrap, hinge, safe = geom.get("wrap_in"), geom.get("hinge_in"), geom.get("safe_from_edge_in")
    if None in (width, height, wrap, hinge, safe):
        return None, [finding(
            "MANUFACTURING_FACT_UNVERIFIED", "HIGH", None, "kdp_hardcover",
            "trim_in, wrap_in, hinge_in ou safe_from_edge_in ausentes.",
            "Completar layout/PRINT_SPEC.yaml e engine/templates/PRINT_GEOMETRY.yaml.")]

    factor = spine_table["value"]
    spine_in = round(page_count * factor, 4)
    full_width_in = round(2 * wrap + 2 * width + spine_in, 4)
    full_height_in = round(2 * wrap + height, 4)
    geometry = {
        "target": "kdp_hardcover", "unit": "in", "page_count": page_count,
        "spine_in": spine_in, "full_width_in": full_width_in, "full_height_in": full_height_in,
        "wrap_in": wrap, "hinge_in": hinge, "safe_from_edge_in": safe,
        "pixels_per_inch": 300,
    }
    return geometry, []


def compute_collector_geometry(print_spec: dict, printer_profile: dict | None) -> tuple[dict | None, list[dict]]:
    if not printer_profile:
        return None, [finding(
            "PRINTER_UNCONFIRMED", "HIGH", None, "collector",
            "collector sem layout/PRINTER_PROFILE.yaml: nenhuma geometria pode ser confirmada.",
            "Registrar o perfil de gráfica (capacidades confirmadas, com data e contato humano) "
            "antes de calcular geometria de collector — collector não é um fabricante, é uma "
            "classe de edição.")]

    spec = (print_spec or {}).get("collector") or {}
    page_count = spec.get("page_count")
    if page_count is None:
        return None, [finding(
            "PAGE_COUNT_UNKNOWN", "HIGH", None, "collector",
            "layout/PRINT_SPEC.yaml (collector) não declara page_count.",
            "Medir a contagem final de páginas antes de calcular a geometria.")]

    trim = spec.get("trim_in") or {}
    width, height = trim.get("width"), trim.get("height")
    bleed = printer_profile.get("bleed_in")
    factor = printer_profile.get("spine_in_per_page")
    if None in (width, height, bleed, factor):
        return None, [finding(
            "MANUFACTURING_FACT_UNVERIFIED", "HIGH", None, "collector",
            "trim_in, bleed_in ou spine_in_per_page ausentes no PRINT_SPEC/PRINTER_PROFILE.",
            "Completar layout/PRINT_SPEC.yaml (collector) e layout/PRINTER_PROFILE.yaml com os "
            "valores confirmados pela gráfica escolhida.")]

    spine_in = round(page_count * factor, 4)
    full_width_in = round(bleed + width + spine_in + width + bleed, 4)
    full_height_in = round(height + 2 * bleed, 4)
    geometry = {
        "target": "collector", "unit": "in", "page_count": page_count,
        "spine_in": spine_in, "full_width_in": full_width_in, "full_height_in": full_height_in,
        "pixels_per_inch": 300,
    }
    return geometry, []


def compute_cover_geometry(target: str, print_spec: dict, print_geometry: dict,
                            printer_profile: dict | None = None) -> tuple[dict | None, list[dict]]:
    if target == "kindle_ebook":
        return compute_kindle_geometry(print_geometry)
    if target == "kdp_paperback":
        return compute_paperback_geometry(print_spec, print_geometry)
    if target == "kdp_hardcover":
        return compute_hardcover_geometry(print_spec, print_geometry)
    if target == "collector":
        return compute_collector_geometry(print_spec, printer_profile)
    return None, [finding(
        "CONTRACT_MISSING_FIELD", "HIGH", None, target,
        f"alvo de edição desconhecido: {target!r}.",
        f"Usar um de {EDITION_TARGETS}.")]


def build_production_manifest(canon: dict, target: str, plan: dict,
                               printer_profile: dict | None = None) -> dict:
    """22.2: o agente escreve instruções; a lista de ativos é PROJETADA a
    partir do EDITION_PLAN — só efeitos PHYSICAL viram ativo de máscara.
    Só faz sentido para target=collector (é a única edição com produção de
    gráfica especializada)."""
    if target != "collector":
        return {"error": f"PRODUCTION_MANIFEST só se aplica a target=collector (recebido {target!r})."}
    finish_by_id = {fi.get("id"): fi for fi in canon.get("finish_intents") or []}
    assets, materials = [], []
    for entry in plan.get("finish_intents") or []:
        if entry.get("level") != "PHYSICAL":
            continue
        fi = finish_by_id.get(entry.get("finish_intent"), {})
        asset_id = f"A-{fi.get('id')}"
        assets.append({
            "id": asset_id,
            "kind": _MASK_KIND_BY_EFFECT.get(entry.get("effect"), "FULL_ARTWORK"),
            "derived_from": {"layer": fi.get("layer_name")} if fi.get("layer_name") else None,
            "finish_intent": fi.get("id"),
            "mask_rules": {"mode": "VECTOR_OR_1BIT", "ink": "100% K",
                           "registration": "SAME_GEOMETRY_AS_PARENT"},
            "material": {"semantic": fi.get("semantic_material"), "vendor_code": None},
            "status": "SPECIFIED", "file": None, "sha256": None,
        })
        materials.append({
            "finish_intent": fi.get("id"), "effect": entry.get("effect"),
            "vendor_confirmed": printer_profile is not None,
        })
    return {
        "apiVersion": "pedroarte.livingbooks/v1", "kind": "CollectorProductionManifest",
        "metadata": {
            "project_id": (canon.get("metadata") or {}).get("project_id"),
            "canon_version": (canon.get("metadata") or {}).get("version"),
            "printer_profile": (printer_profile or {}).get("metadata", {}).get("id"),
        },
        "assets": assets, "materials": materials,
        "printer_instructions": [
            f"Produzir {a['id']} ({a['kind']}) para {a['finish_intent']}, "
            f"material {a['material']['semantic']}."
            for a in assets
        ],
    }


# --- Assets (pixels) — seções 18.3, 23.5, 23.6, 16.2-pixels da SDD — Slice 4 --
#
# Contrato primeiro, heurística simples, sem visão computacional complexa
# (23.5): só Pillow, já instalado. As heurísticas medem condições
# NECESSÁRIAS, não suficientes — nunca substituem o olho humano no
# checkpoint de `T801`/`GATE_MEDIA_ASSETS`. Miniaturas são sempre salvas em
# disco para essa inspeção, sejam quais forem os achados.

THUMBNAIL_WIDTHS = (320, 160, 96)


def generate_thumbnails(image_path: Path, out_dir: Path,
                         widths: tuple[int, ...] = THUMBNAIL_WIDTHS) -> dict[int, Path]:
    """23.5: miniaturas em [320, 160, 96] px, salvas para inspeção humana —
    precedente `loja` (`BOOK_COVER_KDP_PREVIEW_thumb.jpg`, 320×512)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[int, Path] = {}
    with Image.open(image_path) as source:
        rgb = source.convert("RGB")
        width0, height0 = rgb.size
        for width in widths:
            height = max(1, round(width * height0 / width0))
            thumb = rgb.resize((width, height), Image.Resampling.LANCZOS)
            out_path = out_dir / f"{Path(image_path).stem}_{width}.jpg"
            thumb.save(out_path, "JPEG", quality=92)
            paths[width] = out_path
    return paths


def crop_zone(image: "Image.Image", zone) -> "Image.Image":
    """Recorta um retângulo normalizado [x0,y0,x1,y1] (frações 0..1) do
    espaço da superfície — mesma convenção de `placement.zone` (21.4)."""
    width, height = image.size
    x0, y0, x1, y1 = zone
    box = (round(x0 * width), round(y0 * height), round(x1 * width), round(y1 * height))
    box = (max(0, box[0]), max(0, box[1]), min(width, box[2]), min(height, box[3]))
    if box[2] <= box[0] or box[3] <= box[1]:
        return image.crop((0, 0, 1, 1))
    return image.crop(box)


def _percentile(values: list[int], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round(pct / 100 * (len(ordered) - 1))))
    return ordered[idx]


def title_contrast_ratio(image: "Image.Image", zone) -> float:
    """Diferença de luminância entre p95 e p5 dentro da zona, 0..1."""
    crop = crop_zone(image, zone).convert("L")
    values = list(crop.getdata())
    if not values:
        return 0.0
    return (_percentile(values, 95) - _percentile(values, 5)) / 255.0


def otsu_threshold(gray_values: list[int]) -> int:
    """Limiar de Otsu clássico sobre um histograma de 256 tons — separa uma
    zona bimodal (tinta × fundo) sem depender de cor."""
    if not gray_values:
        return 128
    histogram = [0] * 256
    for value in gray_values:
        histogram[value] += 1
    total = len(gray_values)
    sum_total = sum(i * histogram[i] for i in range(256))
    sum_below, weight_below = 0.0, 0
    best_variance, best_threshold = -1.0, 128
    for t in range(256):
        weight_below += histogram[t]
        if weight_below == 0:
            continue
        weight_above = total - weight_below
        if weight_above == 0:
            break
        sum_below += t * histogram[t]
        mean_below = sum_below / weight_below
        mean_above = (sum_total - sum_below) / weight_above
        variance = weight_below * weight_above * (mean_below - mean_above) ** 2
        if variance > best_variance:
            best_variance, best_threshold = variance, t
    return best_threshold


def _median_rgb(pixels: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    if not pixels:
        return (128, 128, 128)
    reds = sorted(p[0] for p in pixels)
    greens = sorted(p[1] for p in pixels)
    blues = sorted(p[2] for p in pixels)
    mid = len(pixels) // 2
    return (reds[mid], greens[mid], blues[mid])


def ink_and_background(image_rgb_crop: "Image.Image") -> tuple[tuple, tuple]:
    """Separa a zona em duas classes por Otsu (luminância) e devolve
    (cor mediana da tinta, cor mediana do fundo) — tinta = classe menos
    populosa, como texto sobre uma área maior de fundo."""
    gray_values = list(image_rgb_crop.convert("L").getdata())
    rgb_values = list(image_rgb_crop.convert("RGB").getdata())
    if not gray_values:
        return (0, 0, 0), (255, 255, 255)
    threshold = otsu_threshold(gray_values)
    dark = [rgb for gray, rgb in zip(gray_values, rgb_values) if gray <= threshold]
    light = [rgb for gray, rgb in zip(gray_values, rgb_values) if gray > threshold]
    ink, background = (dark, light) if len(dark) <= len(light) else (light, dark)
    return _median_rgb(ink), _median_rgb(background)


def _srgb_channel_to_linear(channel_0_255: float) -> float:
    c = channel_0_255 / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return (0.2126 * _srgb_channel_to_linear(r) + 0.7152 * _srgb_channel_to_linear(g)
            + 0.0722 * _srgb_channel_to_linear(b))


def wcag_contrast_ratio(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
    l1, l2 = relative_luminance(rgb1), relative_luminance(rgb2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def edge_energy(image_gray: "Image.Image") -> float:
    edges = image_gray.filter(ImageFilter.FIND_EDGES)
    values = list(edges.getdata())
    return sum(values) / len(values) if values else 0.0


def focal_point_ratio(image: "Image.Image", dominant_zone, exclude_zones=()) -> float:
    """Razão de energia de borda dentro da zona DOMINANT vs fora dela — um
    ponto focal real destaca-se do restante AMBIENTE da composição.

    `exclude_zones` (normalmente TITLE/AUTHOR) fica de fora da medida de
    "fora": tipografia é DELIBERADAMENTE de alto contraste (23.5 exige isso
    do título), então incluir o texto no lado "fora" contaminaria a medida
    com bordas nítidas que nada têm a ver com o elemento dominante — um
    texto legível não deveria fazer uma imagem parecer "sem foco"."""
    gray = image.convert("L")
    width, height = gray.size
    edges = gray.filter(ImageFilter.FIND_EDGES)
    total_energy_sum = sum(edges.getdata())
    n_total = width * height

    inside = crop_zone(edges, dominant_zone)
    inside_sum = sum(inside.getdata())
    n_inside = inside.size[0] * inside.size[1]

    excluded_sum, n_excluded = 0, 0
    for zone in exclude_zones:
        crop = crop_zone(edges, zone)
        excluded_sum += sum(crop.getdata())
        n_excluded += crop.size[0] * crop.size[1]

    n_outside = n_total - n_inside - n_excluded
    if n_outside <= 0:
        return 0.0
    inside_energy = inside_sum / n_inside if n_inside else 0.0
    outside_energy_sum = max(0.0, total_energy_sum - inside_sum - excluded_sum)
    outside_energy = outside_energy_sum / n_outside
    if outside_energy <= 0:
        return float("inf") if inside_energy > 0 else 0.0
    return inside_energy / outside_energy


def clutter_density(image: "Image.Image") -> float:
    """Densidade média de borda, 0..1 — quanto maior, mais "ocupada" a
    miniatura parece num scroll rápido."""
    return edge_energy(image.convert("L")) / 255.0


def largest_connected_component_ratio(image: "Image.Image", dominant_zone) -> float:
    """Binariza a zona por Otsu e mede a maior componente conexa como
    fração da área da zona — a "silhueta" que sobrevive numa miniatura de
    96 px precisa ser UMA forma reconhecível, não fragmentos."""
    crop = crop_zone(image, dominant_zone).convert("L")
    values = list(crop.getdata())
    if not values:
        return 0.0
    threshold = otsu_threshold(values)
    width, height = crop.size
    # Foreground = classe MENOS populosa (mesma convenção de
    # ink_and_background): o sujeito costuma ocupar menos área da zona do
    # que o fundo ao redor dele. Sem isto, uma silhueta clara sobre fundo
    # escuro mediria a conectividade do FUNDO, não do sujeito.
    dark_count = sum(1 for v in values if v <= threshold)
    light_count = len(values) - dark_count
    binary = ([1 if v <= threshold else 0 for v in values] if dark_count <= light_count
              else [1 if v > threshold else 0 for v in values])

    def at(x, y):
        return binary[y * width + x]

    visited = [False] * (width * height)
    best = 0
    for start_y in range(height):
        for start_x in range(width):
            start_idx = start_y * width + start_x
            if not binary[start_idx] or visited[start_idx]:
                continue
            stack = [(start_x, start_y)]
            visited[start_idx] = True
            size = 0
            while stack:
                x, y = stack.pop()
                size += 1
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        idx = ny * width + nx
                        if at(nx, ny) and not visited[idx]:
                            visited[idx] = True
                            stack.append((nx, ny))
            best = max(best, size)
    area = width * height
    return best / area if area else 0.0


def dominant_colors(image: "Image.Image", n: int = 5) -> list[dict]:
    """5 cores dominantes via quantização Pillow (16.2/23.4: 'author DNA
    drift ... em pixels')."""
    small = image.convert("RGB")
    small.thumbnail((150, 150 * 2))
    quantized = small.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette() or []
    counts = quantized.getcolors() or []
    counts.sort(key=lambda item: -item[0])
    total = sum(count for count, _ in counts) or 1
    colors = []
    for count, index in counts:
        rgb = tuple(palette[index * 3:index * 3 + 3]) if len(palette) >= index * 3 + 3 else (0, 0, 0)
        colors.append({"rgb": rgb, "ratio": count / total})
    return colors


def check_author_dna_drift_pixels(image: "Image.Image", author_dna: dict) -> list[dict]:
    """23.4: 'author DNA drift ... em pixels: 5 cores dominantes do JPEG
    vs papéis; área de PULSE > max_area_ratio' — MEDIUM em pixels (a
    checagem estrita é V1, em canon, e é HIGH: seção 13.1)."""
    findings = []
    roles = (author_dna.get("color") or {}).get("roles") or {}
    for role_key, role in roles.items():
        max_ratio = role.get("max_area_ratio")
        l_range, s_range = role.get("lightness"), role.get("saturation")
        if not max_ratio or not l_range or not s_range:
            continue
        for color in dominant_colors(image):
            r, g, b = (c / 255 for c in color["rgb"])
            lightness, saturation = _rgb_to_hsl(r, g, b)
            in_role = l_range[0] <= lightness <= l_range[1] and s_range[0] <= saturation <= s_range[1]
            if in_role and color["ratio"] > max_ratio:
                findings.append(finding(
                    "AUTHOR_DNA_DRIFT", "MEDIUM", None, role_key,
                    f"cor dominante {color['rgb']} (papel {role_key}) ocupa "
                    f"{color['ratio'] * 100:.1f}% da imagem, acima do teto "
                    f"max_area_ratio={max_ratio * 100:.0f}%.",
                    "Reduzir a área desse papel de cor na composição, ou registrar "
                    "override_reason com aprovação se o excesso for intencional."))
    return findings


def check_sigil_monochrome_pixels(canon: dict, runtime: Path | None) -> list[dict]:
    """18.3/V6: raster com >5% de pixels em tom médio (luminância
    0,15-0,85) → SIGIL_NOT_MONOCHROME. `GLYPH` (tipográfico, sem asset
    raster) nunca é inspecionado aqui — nada a checar em pixels."""
    findings = []
    if runtime is None:
        return findings
    for element in canon.get("elements") or []:
        if element.get("class") != "SIGIL":
            continue
        for state in element.get("states") or []:
            render = state.get("render") or {}
            if render.get("mode") not in ("RASTER_1BIT", "VECTOR"):
                continue
            asset_rel = render.get("asset")
            if not asset_rel:
                continue
            asset_path = runtime / asset_rel
            if not asset_path.is_file():
                continue
            with Image.open(asset_path) as img:
                values = list(img.convert("L").getdata())
            if not values:
                continue
            midtone = sum(1 for v in values if 0.15 * 255 <= v <= 0.85 * 255)
            ratio = midtone / len(values)
            if ratio > 0.05:
                findings.append(finding(
                    "SIGIL_NOT_MONOCHROME", "HIGH", None, f"{element.get('id')}/{state.get('id')}",
                    f"{ratio * 100:.1f}% dos pixels de {asset_rel} estão em tom médio "
                    "(luminância 0,15-0,85).",
                    "Regravar o asset como verdadeiramente monocromático (preto/branco "
                    "puro, ou vetor 1-bit) — sigils precisam funcionar em Kindle grayscale "
                    "e impressão P&B sem depender de meio-tom."))
    return findings


def _check_cover_readability(composition: dict, author_dna: dict, image_160, image_320,
                              image_96, *, grayscale: bool) -> list[dict]:
    findings = []
    suffix = " (grayscale/e-ink)" if grayscale else ""
    typography_by_role = {t.get("role"): t for t in composition.get("typography") or []}

    title_cfg = typography_by_role.get("TITLE")
    if title_cfg and title_cfg.get("zone"):
        zone = title_cfg["zone"]
        contrast_diff = title_contrast_ratio(image_160, zone)
        if contrast_diff < 0.45:
            findings.append(finding(
                "THUMBNAIL_TITLE_ILLEGIBLE", "HIGH", None, composition.get("id"),
                f"{composition.get('id')}: título com diferença de luminância "
                f"{contrast_diff:.2f} na miniatura de 160px{suffix}, abaixo do piso 0,45.",
                "Aumentar o contraste entre o título e o fundo na zona TITLE — título "
                "ilegível na miniatura é sempre bloqueante (23.5)."))
        ink, background = ink_and_background(crop_zone(image_160, zone))
        wcag = wcag_contrast_ratio(ink, background)
        if wcag < 4.5:
            findings.append(finding(
                "THUMBNAIL_TITLE_ILLEGIBLE", "HIGH", None, composition.get("id"),
                f"{composition.get('id')}: contraste WCAG do título {wcag:.2f}:1 na "
                f"miniatura de 160px{suffix}, abaixo do piso 4,5:1.",
                "Escolher tinta/fundo com contraste WCAG >= 4,5:1 na zona TITLE."))

    author_cfg = typography_by_role.get("AUTHOR")
    if author_cfg and author_cfg.get("zone"):
        contrast_diff = title_contrast_ratio(image_320, author_cfg["zone"])
        if contrast_diff < 0.35:
            findings.append(finding(
                "THUMBNAIL_AUTHOR_ILLEGIBLE", "MEDIUM", None, composition.get("id"),
                f"{composition.get('id')}: nome da autora com diferença de luminância "
                f"{contrast_diff:.2f} na miniatura de 320px{suffix}, abaixo do piso 0,35.",
                "Aumentar o contraste do nome da autora na zona AUTHOR — a autora "
                "precisa ser reconhecível mesmo em miniatura."))

    dominant_ref = next(
        (ref for ref in composition.get("elements") or []
         if ref.get("prominence") == "DOMINANT" and ref.get("zone")), None)
    if dominant_ref:
        zone = dominant_ref["zone"]
        typography_zones = [t["zone"] for t in composition.get("typography") or [] if t.get("zone")]
        ratio = focal_point_ratio(image_160, zone, exclude_zones=typography_zones)
        if ratio < 1.3:
            findings.append(finding(
                "THUMBNAIL_WEAK_FOCAL_POINT", "MEDIUM", None, composition.get("id"),
                f"{composition.get('id')}: razão de energia de borda dentro/fora da zona "
                f"DOMINANT é {ratio:.2f} na miniatura de 160px{suffix}, abaixo do piso 1,3.",
                "Reforçar o ponto focal (contraste, silhueta) do elemento DOMINANT contra "
                "o restante da composição, ou simplificar o entorno."))
        intent = composition.get("thumbnail_intent") or {}
        if intent.get("silhouette_readable"):
            component_ratio = largest_connected_component_ratio(image_96, zone)
            if component_ratio < 0.25:
                findings.append(finding(
                    "THUMBNAIL_WEAK_SILHOUETTE", "MEDIUM", None, composition.get("id"),
                    f"{composition.get('id')}: maior componente conexa na zona DOMINANT é "
                    f"{component_ratio * 100:.1f}% da área na miniatura de 96px{suffix}, "
                    "abaixo do piso 25%.",
                    "Simplificar a silhueta do elemento dominante — numa miniatura de "
                    "96px ela precisa permanecer UMA forma reconhecível, não fragmentos."))

    clutter_ceiling = ((author_dna.get("defaults") or {}).get("thumbnail_clutter_ceiling")
                        or 0.35)
    clutter = clutter_density(image_160)
    if clutter > clutter_ceiling:
        findings.append(finding(
            "THUMBNAIL_CLUTTER", "MEDIUM", None, composition.get("id"),
            f"{composition.get('id')}: densidade de borda {clutter:.2f} na miniatura de "
            f"160px{suffix}, acima do teto da autora {clutter_ceiling:.2f}.",
            "Simplificar a composição — muitos elementos competindo dificultam a leitura "
            "em thumbnail de loja."))
    return findings


def check_cover_assets(canon: dict, author_dna: dict, image_path: Path,
                        thumbnails_dir: Path | None = None) -> list[dict]:
    """V4 (thumbnail) + V1 pixels (author DNA drift), sobre a capa real
    (`compositions[surface=FRONT_COVER]`). Gera as miniaturas em disco
    independentemente do resultado — elas são sempre entregues para
    inspeção humana (23.5)."""
    findings = []
    image_path = Path(image_path)
    if not image_path.is_file():
        return findings
    composition = next(
        (c for c in canon.get("compositions") or [] if c.get("surface") == "FRONT_COVER"), None)
    if composition is None:
        return findings
    thumb_dir = Path(thumbnails_dir) if thumbnails_dir else image_path.parent.parent / "thumbnails"
    thumbs = generate_thumbnails(image_path, thumb_dir)

    with Image.open(thumbs[320]) as raw320, Image.open(thumbs[160]) as raw160, Image.open(thumbs[96]) as raw96:
        rgb320, rgb160, rgb96 = raw320.convert("RGB"), raw160.convert("RGB"), raw96.convert("RGB")
        findings += _check_cover_readability(composition, author_dna, rgb160, rgb320, rgb96, grayscale=False)
        gray160 = rgb160.convert("L").convert("RGB")
        gray320 = rgb320.convert("L").convert("RGB")
        gray96 = rgb96.convert("L").convert("RGB")
        findings += _check_cover_readability(composition, author_dna, gray160, gray320, gray96, grayscale=True)

    with Image.open(image_path) as full:
        findings += check_author_dna_drift_pixels(full.convert("RGB"), author_dna)
    return findings


# --- Proveniência de artefatos derivados (17.3, 27.1) -----------------------

def check_derived_artifact_integrity(document: dict, expected_generator_prefix: str | None = None) -> list[dict]:
    """17.3: um artefato PROJETADO do canon (ex.: `media/MEDIA_DESIGN.yaml`,
    Slice 6) carrega `_generated: {generated_from, sha256}` sobre o resto do
    próprio corpo. Editar o arquivo à mão depois de gerado quebra o hash —
    `DERIVED_ARTIFACT_EDITED`. Função pura: não sabe nada sobre COMO o
    arquivo foi gerado, só verifica a proveniência declarada nele mesmo."""
    findings = []
    meta = document.get("_generated") or {}
    generated_from = meta.get("generated_from")
    declared_sha = meta.get("sha256")
    if not generated_from or not declared_sha:
        return findings  # não é um artefato derivado rastreado — nada a checar
    body = {k: v for k, v in document.items() if k != "_generated"}
    actual_sha = canonical_block_sha256(body)
    if actual_sha != declared_sha:
        findings.append(finding(
            "DERIVED_ARTIFACT_EDITED", "HIGH", None, generated_from,
            f"artefato editado à mão depois de gerado a partir de {generated_from}: "
            f"sha256 declarado {declared_sha[:12]}… != atual {actual_sha[:12]}….",
            "Regenerar o arquivo a partir do canon — nunca editar manualmente um "
            "artefato PROJETADO. Se a mudança for intencional, promovê-la de volta ao "
            "canon primeiro, depois regenerar."))
    if expected_generator_prefix and not str(generated_from).startswith(expected_generator_prefix):
        findings.append(finding(
            "DERIVED_ARTIFACT_EDITED", "MEDIUM", None, generated_from,
            f"generated_from ({generated_from}) não corresponde ao gerador esperado "
            f"({expected_generator_prefix}).",
            "Confirmar que o arquivo foi produzido pelo pipeline correto."))
    return findings


def stamp_derived_artifact(body: dict, generated_from: str) -> dict:
    """Contraparte de escrita de `check_derived_artifact_integrity`: computa
    o hash do corpo e devolve o documento completo pronto para salvar."""
    sha = canonical_block_sha256(body)
    return {**body, "_generated": {"generated_from": generated_from, "sha256": sha}}


# --- Slice 6: hooks de renderização existentes (seções 17.3, 17.4, 18.4) ----
#
# "Sem mudança padrão": build_cover_and_stories.py e build_kdp_docx.py só
# ganham um arquivo opcional (media/MEDIA_DESIGN.yaml projetado) e um plano
# opcional (layout/editions/<target>/EDITION_PLAN.yaml com chapter_openers[])
# — a ausência de qualquer um dos dois deixa a saída byte a byte idêntica à
# de antes desta capability existir (INV-VN-02).

MUTED_LUMINOSITY_FACTOR = 0.85  # 17.3: "INK com luminosidade reduzida (fórmula fixa)"


def hex_to_rgb(hexstr) -> list[int] | None:
    if not isinstance(hexstr, str):
        return None
    h = hexstr.lstrip("#")
    if len(h) != 6:
        return None
    try:
        return [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    except ValueError:
        return None


def _role_hex(role_value) -> str | None:
    """Um papel de `book_dna.palette` é hex direto (`"#121113"`) ou
    `{material, hex}` (ex.: METAL) — mesma convenção do resto do arquivo."""
    if isinstance(role_value, dict):
        return role_value.get("hex")
    if isinstance(role_value, str):
        return role_value
    return None


def resolve_text_source(text_source, book_spec: dict | None, author_dna: dict | None) -> str | None:
    """`typography[].text_source` (12.2/17.3) é um caminho `BOOK_SPEC.*` ou
    `AUTHOR_DNA.*` contra os dois únicos documentos com metadado estável —
    nunca texto literal (evita duplicar título/nome de autora em dois
    lugares que podem divergir). Qualquer outro formato não resolve aqui."""
    if not isinstance(text_source, str):
        return None
    if text_source.startswith("BOOK_SPEC."):
        node, path = book_spec or {}, text_source[len("BOOK_SPEC."):]
    elif text_source.startswith("AUTHOR_DNA."):
        node, path = author_dna or {}, text_source[len("AUTHOR_DNA."):]
    else:
        return None
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node if isinstance(node, str) else None


def project_media_design(canon: dict, book_spec: dict | None = None,
                          author_dna: dict | None = None) -> dict:
    """17.3: projeção determinística de `media/MEDIA_DESIGN.yaml` a partir do
    canon — nunca o inverso. `cover.base_image` deliberadamente NÃO é
    projetado nesta slice: nenhuma tarefa desta capability ainda produz "arte
    aprovada da composição FRONT_COVER" (geração por elemento, T45N, continua
    fora de escopo); `build_cover_and_stories.py` mantém seu próprio default
    (`images/approved/chapter_01.jpg`) intacto."""
    palette = (canon.get("book_dna") or {}).get("palette") or {}
    ground = hex_to_rgb(_role_hex(palette.get("GROUND")))
    ink = hex_to_rgb(_role_hex(palette.get("INK")))
    accent = hex_to_rgb(_role_hex(palette.get("METAL")))
    projected_palette = {}
    if ground is not None:
        projected_palette["ground"] = ground
    if ink is not None:
        projected_palette["ink"] = ink
        projected_palette["muted"] = [min(255, round(c * MUTED_LUMINOSITY_FACTOR)) for c in ink]
    if accent is not None:
        projected_palette["accent"] = accent

    spec: dict = {}
    if projected_palette:
        spec["palette"] = projected_palette

    front_cover = next((c for c in canon.get("compositions") or [] if c.get("surface") == "FRONT_COVER"), None)
    tagline_row = next((t for t in (front_cover or {}).get("typography") or [] if t.get("role") == "TAGLINE"), None)
    tagline = resolve_text_source(tagline_row.get("text_source"), book_spec, author_dna) if tagline_row else None
    if tagline:
        spec["tagline"] = tagline

    typography_bindings = (canon.get("book_dna") or {}).get("typography_bindings") or {}
    if typography_bindings:
        spec["typography_bindings"] = typography_bindings

    version = (canon.get("metadata") or {}).get("version", "0.0.0")
    body = {"apiVersion": "pedroarte.livingbooks/v1", "kind": "MediaDesign", "spec": spec}
    return stamp_derived_artifact(body, f"VISUAL_NARRATIVE_CANON@{version}")


def project_chapter_openers(canon: dict, context: dict, chapter_count: int,
                             mode: str = "plan") -> list[dict]:
    """18.2-18.4: para cada composição `CHAPTER_OPENER`, projeta — capítulo a
    capítulo — o estado vigente do sigil `DOMINANT` (mesma projeção de
    `--state`, varrida em lote) e o `render` desse estado. `CHAPTER_OPENER`
    mapeia para si mesma em todo `SURFACE_MAP` (15.2): a lista é idêntica em
    qualquer `edition_target`, por isso é calculada uma vez e embutida em
    cada `EDITION_PLAN.yaml` projetado (T698)."""
    elements_by_id = {e.get("id"): e for e in canon.get("elements") or []}
    openers = []
    for composition in canon.get("compositions") or []:
        if composition.get("surface") != "CHAPTER_OPENER":
            continue
        dominant_ref = next((ce for ce in composition.get("elements") or []
                              if ce.get("prominence") == "DOMINANT"), None)
        if dominant_ref is None:
            continue
        element = elements_by_id.get(dominant_ref.get("element"))
        if element is None or element.get("class") != "SIGIL":
            continue
        states_by_id = {s.get("id"): s for s in element.get("states") or []}
        for chapter in range(1, chapter_count + 1):
            projected = project_state(element, chapter, context, mode)
            render = (states_by_id.get(projected["state"]) or {}).get("render") or {}
            openers.append({
                "chapter": chapter,
                "composition": composition.get("id"),
                "element": element.get("id"),
                "state": projected["state"],
                "render_mode": render.get("mode"),
                "asset": render.get("asset"),
            })
    return openers


# --- API pública -------------------------------------------------------------

# --- Illustration canon e FIGURE (genérico; desenho em docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md,
# seções 16, 19 e 25.4) -----------------------------------------------------------
# Só atua sobre composições que declaram o bloco `illustration` e sobre
# elementos `class: FIGURE`. Canon sem nenhum dos dois: nenhuma mudança.

TEXT_RELATION_VALUES = {"COMPLEMENT", "CONTRADICT", "FORESHADOW"}
PLATE_PLACEMENT_VALUES = {"OPEN", "HINGE", "AFTER"}
COVER_FIGURE_SURFACES = {"FRONT_COVER", "MARKETING_COVER", "CASE_FRONT", "CASE_BACK", "CASE_SPINE",
                         "DUST_JACKET_FRONT", "DUST_JACKET_BACK", "DUST_JACKET_SPINE"}


def _composition_chapter(composition: dict | None, context: dict, mode: str = "plan") -> int | None:
    if not composition:
        return None
    if isinstance(composition.get("chapter"), int):
        return composition["chapter"]
    anchor = (composition.get("illustration") or {}).get("placement_anchor")
    result = resolve_anchor(anchor, context, mode) if anchor else None
    return result.get("chapter") if result and result.get("ok") else None


def check_illustrations(canon: dict, context: dict, mode: str = "plan") -> list[dict]:
    """TIR-01..04, callbacks e slots de ilustração declarados em
    chapter_architecture.yaml (`illustration_slots`)."""
    findings = []
    compositions = canon.get("compositions") or []
    by_id = {c.get("id"): c for c in compositions}
    illustrated = [c for c in compositions if c.get("illustration") is not None]
    for composition in illustrated:
        cid = composition.get("id")
        block = composition.get("illustration") or {}
        chapter = _composition_chapter(composition, context, mode)
        if composition.get("surface") in CHAPTER_SCOPED_SURFACES and chapter is None:
            findings.append(finding(
                "ILLUSTRATION_CHAPTER_MISSING", "HIGH", None, cid,
                f"{cid}: ilustração de miolo sem capítulo (chapter ou placement_anchor resolvível).",
                "Declarar chapter ou uma placement_anchor estrutural."))
        if not str(block.get("category") or "").strip():
            findings.append(finding(
                "ILLUSTRATION_CATEGORY_MISSING", "HIGH", chapter, cid,
                f"{cid}: ilustração sem category.", "Declarar a categoria da prancha."))
        relation = block.get("text_relation")
        if relation not in TEXT_RELATION_VALUES:
            findings.append(finding(
                "TEXT_RELATION_MISSING", "HIGH", chapter, cid,
                f"{cid}: text_relation ausente ou inválida ({relation!r}).",
                "Declarar COMPLEMENT, CONTRADICT ou FORESHADOW — nenhuma prancha ilustra por ilustrar."))
        elif relation == "COMPLEMENT" and not str(block.get("adds") or "").strip():
            findings.append(finding(
                "LITERAL_ILLUSTRATION", "MEDIUM", chapter, cid,
                f"{cid}: COMPLEMENT sem `adds`.",
                "Declarar a informação que a imagem acrescenta ao texto."))
        elif relation == "CONTRADICT" and not str(block.get("contradicts") or "").strip():
            findings.append(finding(
                "CONTRADICTION_UNDECLARED", "HIGH", chapter, cid,
                f"{cid}: CONTRADICT sem `contradicts`.",
                "Declarar a percepção ou interpretação que a imagem contradiz — nunca um fato do canon."))
        elif relation == "FORESHADOW":
            payoff = block.get("payoff_anchor")
            result = resolve_anchor(payoff, context, mode) if payoff else None
            valid = bool(result and result.get("ok") and result.get("strength") == "STRUCTURAL"
                         and result.get("chapter") is not None
                         and (chapter is None or result["chapter"] > chapter))
            if not valid:
                findings.append(finding(
                    "FORESHADOW_WITHOUT_PAYOFF", "HIGH", chapter, cid,
                    f"{cid}: FORESHADOW sem payoff_anchor estrutural em capítulo posterior ({payoff!r}).",
                    "Apontar o payoff para uma âncora LEDGER:/SCENE:/TURN: depois da prancha."))
        placement = block.get("placement")
        if placement is not None and placement not in PLATE_PLACEMENT_VALUES:
            findings.append(finding(
                "INVALID_ENUM", "HIGH", chapter, cid,
                f"{cid}: placement inválido ({placement!r}).", "Usar OPEN, HINGE ou AFTER."))
        callback = block.get("callback_of")
        if callback:
            target = by_id.get(callback)
            target_chapter = _composition_chapter(target, context, mode)
            if (target is None or target.get("illustration") is None
                    or (chapter is not None and target_chapter is not None and target_chapter >= chapter)):
                findings.append(finding(
                    "CALLBACK_UNRESOLVED", "HIGH", chapter, cid,
                    f"{cid}: callback_of={callback!r} não aponta para uma ilustração anterior.",
                    "Referenciar a composição ilustrada original, de capítulo anterior."))
            changes = [c for c in block.get("callback_changes") or []
                       if isinstance(c, dict) and str(c.get("what") or "").strip()]
            if not changes:
                findings.append(finding(
                    "CALLBACK_WITHOUT_CHANGE", "MEDIUM", chapter, cid,
                    f"{cid}: retorno a {callback} sem callback_changes.",
                    "Declarar ao menos uma diferença em relação à prancha original (MIR-03)."))
            elif sum(1 for c in changes if c.get("impossible")) > 1:
                findings.append(finding(
                    "CALLBACK_OVERLOADED", "MEDIUM", chapter, cid,
                    f"{cid}: mais de uma diferença impossível no retorno a {callback}.",
                    "No máximo uma diferença impossível por retorno (MIR-03)."))
        pair = block.get("pair_with")
        if pair == "SPREAD":
            if composition.get("surface") != "INTERIOR_PLATE" or block.get("placement") not in SPREAD_PLACEMENTS:
                findings.append(finding(
                    "SPREAD_PLACEMENT_INVALID", "HIGH", chapter, cid,
                    f"{cid}: spread em {composition.get('surface')} com placement {block.get('placement')!r}.",
                    "Spread é prancha de miolo com placement HINGE ou AFTER — OPEN já forma o par imagem/abertura."))
        elif pair is not None:
            partner = by_id.get(pair)
            if (partner is None or partner is composition or partner.get("illustration") is None
                    or _composition_chapter(partner, context, mode) != chapter):
                findings.append(finding(
                    "PAIR_WITH_UNRESOLVED", "HIGH", chapter, cid,
                    f"{cid}: pair_with={pair!r} não é outra ilustração do mesmo capítulo.",
                    "Usar SPREAD ou o id de uma prancha do mesmo capítulo."))

    slots: dict[str, int] = {}
    for chapter_entry in context.get("chapter_architecture") or []:
        for slot in chapter_entry.get("illustration_slots") or []:
            slots[slot] = chapter_entry.get("number")
    if slots:
        realized = {c.get("id"): _composition_chapter(c, context, mode) for c in illustrated}
        for slot, number in sorted(slots.items()):
            if slot not in realized:
                findings.append(finding(
                    "ILLUSTRATION_SLOT_MISMATCH", "HIGH", number, slot,
                    f"slot {slot} declarado no capítulo {number} sem composição ilustrada no canon.",
                    "T043 realiza exatamente os slots de chapter_architecture.yaml."))
            elif realized[slot] is not None and realized[slot] != number:
                findings.append(finding(
                    "ILLUSTRATION_SLOT_MISMATCH", "HIGH", number, slot,
                    f"slot {slot}: canon no capítulo {realized[slot]}, arquitetura no {number}.",
                    "Alinhar o capítulo da composição ao slot."))
        for cid in sorted(set(realized) - set(slots)):
            findings.append(finding(
                "ILLUSTRATION_SLOT_MISMATCH", "HIGH", realized[cid], cid,
                f"{cid}: composição ilustrada sem slot em chapter_architecture.yaml.",
                "Declarar o slot no pacote (o grafo só gera tarefas para slots declarados)."))
    return findings


def check_figures(canon: dict, context: dict, mode: str = "plan") -> list[dict]:
    """FIG-01, FIG-02, FIG-04 (NARCISO SDD, 25.4)."""
    findings = []
    figures = {e.get("id"): e for e in canon.get("elements") or [] if e.get("class") == "FIGURE"}
    for eid, figure in figures.items():
        if not figure.get("identity_ref"):
            findings.append(finding(
                "FIGURE_WITHOUT_IDENTITY_REF", "HIGH", None, eid,
                f"{eid}: FIGURE sem identity_ref.",
                "Apontar para o canon facial da personagem (DOC:/images/canon/FACE_CANON.md#...)."))
    for composition in canon.get("compositions") or []:
        refs = [r for r in composition.get("elements") or [] if r.get("element") in figures]
        if not refs:
            continue
        cid = composition.get("id")
        if (composition.get("surface") in COVER_FIGURE_SURFACES
                and (composition.get("approval") or {}).get("policy") != "REQUIRE_APPROVAL"):
            findings.append(finding(
                "FIGURE_ON_COVER_UNAPPROVED", "HIGH", None, cid,
                f"{cid}: figura humana em {composition.get('surface')} sem REQUIRE_APPROVAL.",
                "Figura em capa exige aprovação humana com hash (FIGURE_ON_COVER)."))
        chapter = _composition_chapter(composition, context, mode)
        for ref in refs:
            state = ref.get("state")
            if not state:
                continue
            figure = figures[ref["element"]]
            if state not in {s.get("id") for s in figure.get("states") or []}:
                findings.append(finding(
                    "FIGURE_STATE_UNRESOLVED", "HIGH", chapter, f"{ref['element']}@{cid}",
                    f"{cid}: estado {state!r} não existe em {ref['element']}.",
                    "Usar um estado declarado da figura."))
                continue
            if chapter is not None and figure.get("transitions"):
                projected = project_state(figure, chapter, context, mode)["state"]
                if projected != state:
                    findings.append(finding(
                        "FIGURE_STATE_MISMATCH", "HIGH", chapter, f"{ref['element']}@{cid}",
                        f"{cid}: {ref['element']} declarado em {state}, projeção do capítulo {chapter} é {projected}.",
                        "Corrigir o estado da figura na composição — a projeção vem das transições ancoradas."))
    return findings


# --- Livro como espelho (NARCISO SDD, seção 18) ------------------------------------
# `display_assets` (eco do título, ornamento) e spreads são opcionais: canon sem
# eles não gera achado nem chave nova no EDITION_PLAN.

DISPLAY_ASSET_KINDS = {"TITLE_ECHO", "ORNAMENT"}
REFLOWABLE_TARGETS = {"kindle_ebook"}
SPREAD_PLACEMENTS = {"HINGE", "AFTER"}
REFLOWABLE_OMIT_REASON = "alvo refluível: recurso de exibição não renderiza de forma confiável (18.5)"


def check_display_assets(canon: dict, context: dict) -> list[dict]:
    findings = []
    count = len(context.get("chapter_architecture") or [])
    seen: set = set()
    taken: dict = {}
    for asset in canon.get("display_assets") or []:
        aid = asset.get("id")
        kind = asset.get("kind")
        problems = []
        if not aid or aid in seen:
            problems.append("id ausente ou duplicado")
        seen.add(aid)
        if kind not in DISPLAY_ASSET_KINDS:
            problems.append(f"kind inválido {kind!r}")
        chapters = asset.get("chapters") or []
        if not chapters or any(not isinstance(c, int) or c < 1 or (count and c > count) for c in chapters):
            problems.append(f"chapters inválidos {chapters!r}")
        pattern = asset.get("asset")
        if not isinstance(pattern, str) or not pattern.strip():
            problems.append("asset ausente")
        else:
            try:
                pattern.format(chapter=1)
            except (KeyError, IndexError, ValueError):
                problems.append("asset com placeholder inválido (só {chapter})")
        unknown = [t for t in asset.get("omit_in") or [] if t not in EDITION_TARGETS]
        if unknown:
            problems.append(f"omit_in com alvos desconhecidos {unknown}")
        for chapter in chapters:
            if isinstance(chapter, int):
                if (kind, chapter) in taken:
                    problems.append(f"capítulo {chapter} já tem {kind} ({taken[(kind, chapter)]})")
                taken.setdefault((kind, chapter), aid)
        if problems:
            findings.append(finding(
                "DISPLAY_ASSET_INVALID", "HIGH", None, str(aid),
                f"{aid}: {'; '.join(problems)}.",
                "Declarar id único, kind TITLE_ECHO|ORNAMENT, capítulos existentes e asset com no máximo {chapter}."))
    return findings


def project_mirror_manifestation(canon: dict, target: str) -> dict:
    """Pranchas e recursos de exibição por alvo (18.5): spread vira duas páginas
    sequenciais em alvo refluível; recursos de exibição saem de alvo refluível
    e de `omit_in`. Sem pranchas nem recursos, devolve {} (plano inalterado)."""
    plates = []
    for composition in canon.get("compositions") or []:
        block = composition.get("illustration")
        if block is None or composition.get("surface") != "INTERIOR_PLATE":
            continue
        mapped, _ = resolve_composition_surface(composition, target)
        if mapped is None:
            continue
        layout = "SINGLE"
        if block.get("pair_with") == "SPREAD":
            layout = "SEQUENTIAL" if target in REFLOWABLE_TARGETS else "SPREAD"
        plates.append({
            "composition": composition.get("id"),
            "chapter": composition.get("chapter"),
            "category": block.get("category"),
            "placement": block.get("placement", "OPEN"),
            "layout": layout,
            "callback_of": block.get("callback_of"),
        })
    display = []
    for asset in canon.get("display_assets") or []:
        for chapter in sorted(c for c in asset.get("chapters") or [] if isinstance(c, int)):
            if target in REFLOWABLE_TARGETS:
                status, reason = "OMITTED", REFLOWABLE_OMIT_REASON
            elif target in (asset.get("omit_in") or []):
                status, reason = "OMITTED", f"omit_in declara {target}"
            else:
                status, reason = "INCLUDED", None
            display.append({
                "chapter": chapter,
                "display_asset": asset.get("id"),
                "kind": asset.get("kind"),
                "asset": str(asset.get("asset")).format(chapter=chapter) if status == "INCLUDED" else None,
                "status": status,
                "reason": reason,
            })
    display.sort(key=lambda e: (e["chapter"], str(e["display_asset"])))
    out: dict = {}
    if plates:
        out["interior_plates"] = plates
    if display:
        out["chapter_display"] = display
    return out


def validate(canon: dict, author_dna: dict, context: dict | None = None,
             mode: str = "plan", runtime: Path | None = None,
             baseline: dict | None = None, cover_image: Path | None = None,
             thumbnails_dir: Path | None = None) -> list[dict]:
    """Ponto de entrada único.

    `mode`: plan | realized | edition | assets — plan é o padrão (Slice 1).
    `runtime`: quando informado, também roda V9 (aprovações humanas) e, em
    modo `assets`, a inspeção de pixel de sigils raster — sem ele, essas
    checagens são simplesmente puladas (não é um erro: nem todo caller tem
    ou precisa de um runtime em disco).
    `baseline`: canon dict de um snapshot anterior (ex.: `...PLAN.yaml`);
    quando informado, roda ST-08 (VISUAL_RETCON) contra ele.
    `cover_image`/`thumbnails_dir`: em modo `assets`, a capa real (JPEG) a
    inspecionar — sem ela, V4/thumbnail simplesmente não roda (o resto do
    modo `assets` ainda cobre sigils raster e o que mais estiver disponível)."""
    context = context or {"bibles": {}}
    findings: list[dict] = []
    findings += check_integrity(canon)
    findings += check_author_consistency(canon, author_dna)
    chekhov_findings, status_map = check_chekhov(canon, context, author_dna, mode)
    findings += chekhov_findings
    findings += check_anti_generic(canon, author_dna, status_map)
    findings += check_state_model(canon, context, mode)
    findings += check_artifacts(canon, context, mode)
    findings += check_duality(canon, author_dna, context, mode)
    findings += check_spoiler_safety(canon, author_dna, context, mode)
    findings += check_approvals(canon, runtime)
    findings += check_illustrations(canon, context, mode)
    findings += check_figures(canon, context, mode)
    findings += check_display_assets(canon, context)
    findings += check_baseline_retcon(canon, baseline)
    if mode == "assets":
        findings += check_sigil_monochrome_pixels(canon, runtime)
        if cover_image:
            findings += check_cover_assets(canon, author_dna, Path(cover_image), thumbnails_dir)
    return findings


def why_report(canon: dict, context: dict, author_dna: dict, element_id: str,
                mode: str = "plan") -> dict:
    element = next((e for e in canon.get("elements") or [] if e.get("id") == element_id), None)
    if element is None:
        return {"error": f"elemento '{element_id}' não encontrado no canon."}
    status, info = chekhov_status(element, canon, context,
                                   author_dna.get("generic_trope_watchlist") or [], mode)
    resolved = info.get("resolved") if isinstance(info, dict) else None
    return {
        "id": element_id,
        "status": status,
        "class": element.get("class"),
        "prominence": element.get("prominence"),
        "meaning": element.get("meaning"),
        "count": element.get("count", 1),
        "functions": resolved,
        "approval": element.get("approval"),
    }


def evidence_report(context: dict, terms: list[str]) -> dict:
    bibles = context.get("bibles") or {}
    report = {}
    for term in terms:
        needle = term.lower()
        hits = []
        for path, sections in bibles.items():
            for slug, text in sections.items():
                count = text.lower().count(needle)
                if count:
                    hits.append({"doc": path, "section": slug, "count": count})
        report[term] = {"total": sum(h["count"] for h in hits), "by_section": hits}
    return report


def render_evidence(report: dict) -> str:
    lines = []
    for term, data in report.items():
        lines.append(f"{term}: {data['total']} ocorrência(s)")
        for hit in data["by_section"]:
            lines.append(f"  {hit['doc']}#{hit['section']}: {hit['count']}")
    return "\n".join(lines)


def all_declared_targets(runtime: Path) -> list[str]:
    """Lê `features.visual_narrative.edition_targets` de `book/BOOK_SPEC.yaml`
    no runtime — usado pelas tarefas mecânicas que precisam varrer TODO
    alvo declarado sem exigir um `--target` por invocação (T698, T707,
    V_VISUAL_EDITION)."""
    spec_path = runtime / "book" / "BOOK_SPEC.yaml"
    if not spec_path.is_file():
        return []
    spec = load_yaml(spec_path)
    vn = ((spec.get("spec") or {}).get("features") or {}).get("visual_narrative") or {}
    return vn.get("edition_targets") or []


def write_named_snapshot(canon: dict, runtime: Path, name: str) -> Path:
    """Snapshot nomeado e fixo (PLAN, FREEZE) — ao contrário do ledger
    causal, o canon visual não numera por wave; só dois pontos de
    congelamento bastam para ST-08 (seção 27.3 da SDD). Tarefa 100%
    mecânica (T044/T312 via TOOL_BY_TASK em livingbook.py)."""
    snap_dir = runtime / "canon" / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    out_path = snap_dir / f"VISUAL_NARRATIVE_CANON.{name}.yaml"
    out_path.write_text(yaml.safe_dump(canon, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    return out_path


def validate_all_editions(canon: dict, author_dna: dict, context: dict, runtime: Path,
                           capabilities: dict, printer_profile: dict | None,
                           mode: str = "edition") -> list[dict]:
    """V_VISUAL_EDITION: roda `check_edition_plan` para TODO edition_target
    declarado — um livro pode publicar em vários alvos ao mesmo tempo
    (seção 15.1 da SDD)."""
    findings = []
    _chekhov_findings, status_map = check_chekhov(canon, context, author_dna, mode)
    for target in all_declared_targets(runtime):
        plan = resolve_edition_plan(canon, capabilities, target, printer_profile)
        findings += check_edition_plan(canon, target, plan, status_map)
    return findings


def render_report(findings: list[dict], source: str) -> str:
    lines = [f"# Visual Narrative Canon Report — {source}\n"]
    if not findings:
        lines.append("Nenhum achado.\n")
        return "".join(lines)
    for f in findings:
        lines.append(f"- **{f['severity']}** `{f['category']}` (cap. {f['chapter']}) — "
                      f"{f['evidence']}: {f['detail']}\n  Ação: {f['recommended_action']}\n")
    return "".join(lines)


# --- CLI -----------------------------------------------------------------------

def _resolve_paths(args):
    if args.canon:
        canon_path = args.canon
    elif args.runtime:
        canon_path = args.runtime / "canon" / "VISUAL_NARRATIVE_CANON.yaml"
    else:
        raise SystemExit("Erro: informe --runtime ou --canon.")
    if not canon_path.is_file():
        raise SystemExit(f"Erro: canon não encontrado em {canon_path}.")

    if args.author_dna:
        dna_path = args.author_dna
    elif args.runtime and (args.runtime / "author").is_dir():
        candidates = sorted((args.runtime / "author").glob("AUTHOR_VISUAL_DNA.v*.yaml"))
        dna_path = candidates[-1] if candidates else None
    else:
        dna_path = None
    if not dna_path or not dna_path.is_file():
        raise SystemExit("Erro: informe --author-dna, ou um --runtime com "
                          "author/AUTHOR_VISUAL_DNA.v*.yaml.")

    if args.runtime:
        runtime_root = args.runtime
    elif len(canon_path.parents) > 1:
        runtime_root = canon_path.parents[1]
    else:
        runtime_root = canon_path.parent
    return canon_path, dna_path, runtime_root


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida o VISUAL_NARRATIVE_CANON.yaml — capability "
                     "BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM.")
    parser.add_argument("--runtime", type=Path, help="Raiz do runtime; lê canon/VISUAL_NARRATIVE_CANON.yaml.")
    parser.add_argument("--canon", type=Path, help="Caminho direto para um VISUAL_NARRATIVE_CANON.yaml.")
    parser.add_argument("--author-dna", type=Path, help="Caminho direto para um AUTHOR_VISUAL_DNA.v<N>.yaml.")
    parser.add_argument("--mode", choices=["plan", "realized", "edition", "assets"], default="plan")
    parser.add_argument("--baseline", type=Path, help="Snapshot anterior (VISUAL_NARRATIVE_CANON.*.yaml) para checar ST-08 (VISUAL_RETCON).")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--why", metavar="ELEMENT_ID")
    parser.add_argument("--evidence", nargs="+", metavar="TERM")
    parser.add_argument("--state", metavar="ELEMENT_ID", help="Projeta o estado de um elemento progressivo.")
    parser.add_argument("--at-chapter", type=int, help="Capítulo para --state; omitido = estado final (--end-state).")
    parser.add_argument("--timeline", action="store_true", help="Linha do tempo de todas as transições do canon.")
    parser.add_argument("--exposure", action="store_true", help="Matriz elemento x superfície x spoiler.")
    parser.add_argument("--end-state", action="store_true", help="Estado final de todo elemento progressivo.")
    parser.add_argument("--target", choices=list(EDITION_TARGETS), help="Alvo de edição para --edition-plan/--resolve/--geometry/--production-manifest/--mode edition.")
    parser.add_argument("--capabilities", type=Path, help="EDITION_CAPABILITIES.yaml (default: engine/templates/).")
    parser.add_argument("--print-geometry", type=Path, dest="print_geometry_path", help="PRINT_GEOMETRY.yaml (default: engine/templates/).")
    parser.add_argument("--print-spec", type=Path, dest="print_spec_path", help="layout/PRINT_SPEC.yaml (default: <runtime>/layout/).")
    parser.add_argument("--printer-profile", type=Path, dest="printer_profile_path", help="layout/PRINTER_PROFILE.yaml (default: <runtime>/layout/, opcional).")
    parser.add_argument("--edition-plan", action="store_true", help="Projeta o EDITION_PLAN para --target.")
    parser.add_argument("--resolve", metavar="FINISH_INTENT_ID", help="Resolve um finish_intent para --target.")
    parser.add_argument("--geometry", action="store_true", help="Projeta COVER_GEOMETRY para --target.")
    parser.add_argument("--production-manifest", action="store_true", help="Projeta o PRODUCTION_MANIFEST (só target=collector).")
    parser.add_argument("--cover-image", type=Path, help="Capa real (JPEG) a inspecionar em --mode assets (relativo ao runtime, ou absoluto).")
    parser.add_argument("--thumbnails-dir", type=Path, help="Onde salvar as miniaturas de --mode assets (default: <pasta da capa>/../thumbnails).")
    parser.add_argument("--snapshot-as", choices=["PLAN", "FREEZE"], dest="snapshot_as",
                         help="Escreve canon/snapshots/VISUAL_NARRATIVE_CANON.<nome>.yaml (T044/T312).")
    parser.add_argument("--edition-plan-all", action="store_true",
                         help="Escreve layout/editions/<target>/EDITION_PLAN.yaml para todo edition_target "
                              "declarado em BOOK_SPEC.yaml (T698).")
    parser.add_argument("--print-geometry-all", action="store_true",
                         help="Escreve layout/editions/<target>/COVER_GEOMETRY.yaml para todo edition_target "
                              "declarado em BOOK_SPEC.yaml (T707).")
    parser.add_argument("--validate-editions", action="store_true",
                         help="V_VISUAL_EDITION: roda check_edition_plan para todo edition_target declarado.")
    parser.add_argument("--project-media-design", action="store_true",
                         help="Projeta media/MEDIA_DESIGN.yaml a partir do canon (Slice 6, seção 17.3).")
    args = parser.parse_args()

    canon_path, dna_path, runtime_root = _resolve_paths(args)
    canon = load_yaml(canon_path)
    author_dna = load_yaml(dna_path)
    context = load_context(runtime_root) if runtime_root.is_dir() else {"bibles": {}}
    baseline = load_yaml(args.baseline) if args.baseline else None

    if args.evidence:
        report = evidence_report(context, args.evidence)
        print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render_evidence(report))
        return 0

    if args.why:
        report = why_report(canon, context, author_dna, args.why, mode=args.mode)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.end_state:
        print(json.dumps(end_state_report(canon, context, args.mode), ensure_ascii=False, indent=2))
        return 0

    if args.timeline:
        print(json.dumps(timeline_report(canon, context, args.mode), ensure_ascii=False, indent=2))
        return 0

    if args.exposure:
        print(json.dumps(exposure_report(canon, author_dna, context, args.mode), ensure_ascii=False, indent=2))
        return 0

    if args.state:
        element = next((e for e in canon.get("elements") or [] if e.get("id") == args.state), None)
        if element is None:
            print(f"Erro: elemento '{args.state}' não encontrado.", file=sys.stderr)
            return 2
        at_chapter = args.at_chapter if args.at_chapter is not None else 10 ** 9
        print(json.dumps(project_state(element, at_chapter, context, args.mode), ensure_ascii=False, indent=2))
        return 0

    if args.snapshot_as:
        out_path = write_named_snapshot(canon, runtime_root, args.snapshot_as)
        print(f"Snapshot escrito: {out_path}")
        return 0

    if args.project_media_design:
        book_spec_path = runtime_root / "book" / "BOOK_SPEC.yaml"
        book_spec = load_yaml(book_spec_path) if book_spec_path.is_file() else {}
        document = project_media_design(canon, book_spec, author_dna)
        out_path = runtime_root / "media" / "MEDIA_DESIGN.yaml"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
        print(f"MEDIA_DESIGN projetado: {out_path}")
        return 0

    if args.edition_plan_all or args.print_geometry_all or args.validate_editions:
        capabilities = load_yaml(args.capabilities or DEFAULT_CAPABILITIES_PATH)
        print_geometry_data = load_yaml(args.print_geometry_path or DEFAULT_PRINT_GEOMETRY_PATH)
        print_spec_path = args.print_spec_path or (runtime_root / "layout" / "PRINT_SPEC.yaml")
        print_spec_data = (load_yaml(print_spec_path).get("spec") or {}) if print_spec_path.is_file() else {}
        printer_profile_path = args.printer_profile_path or (runtime_root / "layout" / "PRINTER_PROFILE.yaml")
        printer_profile = load_yaml(printer_profile_path) if printer_profile_path.is_file() else None
        targets = all_declared_targets(runtime_root)

        if args.edition_plan_all:
            # chapter_openers (18.4) independe de edition_target (CHAPTER_OPENER
            # mapeia para si mesma em todo SURFACE_MAP) — projetado uma vez,
            # embutido em cada EDITION_PLAN.yaml para build_kdp_docx.py ler sem
            # precisar saber qual alvo está construindo.
            chapter_count = len(context.get("chapter_architecture") or [])
            chapter_openers = project_chapter_openers(canon, context, chapter_count, mode=args.mode)
            for target in targets:
                plan = resolve_edition_plan(canon, capabilities, target, printer_profile)
                plan["chapter_openers"] = chapter_openers
                plan.update(project_mirror_manifestation(canon, target))
                out_dir = runtime_root / "layout" / "editions" / target
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "EDITION_PLAN.yaml").write_text(
                    yaml.safe_dump(plan, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
            print(f"EDITION_PLAN escrito para {len(targets)} alvo(s): {', '.join(targets) or '(nenhum declarado)'}")
            return 0

        if args.print_geometry_all:
            hard_any = False
            for target in targets:
                geometry, geom_findings = compute_cover_geometry(target, print_spec_data,
                                                                   print_geometry_data, printer_profile)
                out_dir = runtime_root / "layout" / "editions" / target
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "COVER_GEOMETRY.yaml").write_text(
                    yaml.safe_dump(geometry, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
                if geom_findings:
                    hard_any = True
                    for f in geom_findings:
                        print(f"[{target}] {f}", file=sys.stderr)
            print(f"COVER_GEOMETRY escrito para {len(targets)} alvo(s): {', '.join(targets) or '(nenhum declarado)'}")
            return 1 if hard_any else 0

        # args.validate_editions
        findings = validate_all_editions(canon, author_dna, context, runtime_root, capabilities,
                                          printer_profile, mode=args.mode)
        hard = [f for f in findings if f["severity"] in ("HIGH", "BLOCKER")]
        output = (json.dumps(findings, ensure_ascii=False, indent=2) if args.json
                  else render_report(findings, f"{canon_path} [all editions]"))
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output, encoding="utf-8")
        else:
            print(output)
        return 1 if hard else 0

    if args.edition_plan or args.resolve or args.geometry or args.production_manifest or args.mode == "edition":
        if not args.target:
            print("Erro: --target é obrigatório com --edition-plan/--resolve/--geometry/"
                  "--production-manifest/--mode edition.", file=sys.stderr)
            return 2
        capabilities = load_yaml(args.capabilities or DEFAULT_CAPABILITIES_PATH)
        # PRINT_GEOMETRY.yaml é lido "cru": suas chaves de topo (kdp_paperback,
        # kdp_hardcover, kindle_ebook) já são os alvos, sem wrapper `spec:`.
        print_geometry_data = load_yaml(args.print_geometry_path or DEFAULT_PRINT_GEOMETRY_PATH)
        print_spec_path = args.print_spec_path or (runtime_root / "layout" / "PRINT_SPEC.yaml")
        # PRINT_SPEC.yaml segue a convenção apiVersion/kind/spec do motor
        # (como BOOK_SPEC.yaml) — as chaves por alvo vivem em spec.*.
        print_spec_data = (load_yaml(print_spec_path).get("spec") or {}) if print_spec_path.is_file() else {}
        printer_profile_path = args.printer_profile_path or (runtime_root / "layout" / "PRINTER_PROFILE.yaml")
        printer_profile = load_yaml(printer_profile_path) if printer_profile_path.is_file() else None

        if args.edition_plan:
            plan = resolve_edition_plan(canon, capabilities, args.target, printer_profile)
            print(json.dumps(plan, ensure_ascii=False, indent=2))
            return 0
        if args.resolve:
            fi = next((f for f in canon.get("finish_intents") or [] if f.get("id") == args.resolve), None)
            if fi is None:
                print(f"Erro: finish_intent '{args.resolve}' não encontrado.", file=sys.stderr)
                return 2
            print(json.dumps(resolve_finish_intent(fi, args.target, capabilities, printer_profile),
                              ensure_ascii=False, indent=2))
            return 0
        if args.geometry:
            geometry, geom_findings = compute_cover_geometry(args.target, print_spec_data,
                                                               print_geometry_data, printer_profile)
            print(json.dumps({"geometry": geometry, "findings": geom_findings}, ensure_ascii=False, indent=2))
            return 1 if geom_findings else 0
        if args.production_manifest:
            plan = resolve_edition_plan(canon, capabilities, args.target, printer_profile)
            manifest = build_production_manifest(canon, args.target, plan, printer_profile)
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
            return 0

        # --mode edition sem flag de consulta: valida o canon (V0-V6) e, em
        # cima disso, o plano de edição do --target (V7/V8).
        plan = resolve_edition_plan(canon, capabilities, args.target, printer_profile)
        _chekhov_findings, status_map = check_chekhov(canon, context, author_dna, args.mode)
        findings = validate(canon, author_dna, context, mode=args.mode, runtime=runtime_root, baseline=baseline)
        findings += check_edition_plan(canon, args.target, plan, status_map)
        hard = [f for f in findings if f["severity"] in ("HIGH", "BLOCKER")]
        output = (json.dumps(findings, ensure_ascii=False, indent=2) if args.json
                  else render_report(findings, f"{canon_path} [{args.target}]"))
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output, encoding="utf-8")
        else:
            print(output)
        return 1 if hard else 0

    cover_image = args.cover_image
    if cover_image and not cover_image.is_absolute():
        cover_image = runtime_root / cover_image
    findings = validate(canon, author_dna, context, mode=args.mode, runtime=runtime_root,
                         baseline=baseline, cover_image=cover_image, thumbnails_dir=args.thumbnails_dir)
    hard = [f for f in findings if f["severity"] in ("HIGH", "BLOCKER")]
    output = (json.dumps(findings, ensure_ascii=False, indent=2) if args.json
              else render_report(findings, str(canon_path)))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
