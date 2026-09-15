"""Validador determinístico da obra NARCISO.

Desenho: docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md (seções 6, 7, 9, 10, 11, 20, 25, 26, 29.7).

Modos
-----
package  DNA narrativo do pacote (Slice 1) + semente do canon interpretativo (Slice 2).
plan     runtime: pacote + canon interpretativo + cruzamento com o ledger causal +
         incógnitas do registry + artefatos de T018N/T019N/T021N.        (GATE_CANON)
visual   plan + canon visual obrigatório: prata só como acabamento, capa por
         fragmento do rosto, declínio de Narciso, estados com significado,
         vetos e superfícies públicas (Slice 3).                         (GATE_LIVING_BOOK)
wave     plan + léxicos proibidos na prosa bruta até --through-chapter +
         imutabilidade contra --baseline.                                 (GATE_WAVE_n)
final    plan + prosa do manuscrito final + fechamento sem explicação +
         imutabilidade contra --baseline.                                 (GATE_FULL_MANUSCRIPT)

illustrations  visual + briefs de imagem sem nome de hipótese + QA de
         continuidade conferindo a anomalia declarada (Slice 4).        (GATE_VISUAL, GATE_MEDIA_ASSETS)

edition  visual + planos de edição sem efeito não físico nem camada escondida fora do
         collector, perfil de gráfica com evidência, textos de loja honestos (Slice 7). (GATE_KDP, GATE_MEDIA_ASSETS)

--snapshot-as NOME grava canon/snapshots/NARCISO_INTERPRETIVE_CANON.NOME.yaml.
As regras de pranchas (slots, categorias, gramática por ato, declínio
projetado, olhar, spoiler, nudez) rodam em todo modo que valida o canon visual.

Nenhuma chamada de modelo. Dependências: biblioteca padrão + PyYAML.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

BOOK_ROOT = Path(__file__).resolve().parents[1]

SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "BLOCKER"]
BLOCKING = {"HIGH", "BLOCKER"}

# --- vocabulário do pacote (Slice 1) -----------------------------------------

DESIRE_STAGES = [
    "CONTEMPLATION", "CURIOSITY", "ATTRACTION", "EXCITATION", "RITUAL",
    "COMPULSION", "DEPENDENCE", "DEGRADATION", "WITHERING",
]
RELAPSE_LIMIT_CHAPTER = 26
DSR_FUNCTIONS = ["DISCOVERY", "PLEASURE", "RITUAL", "NEED", "DEGRADATION", "ABSENCE"]
PLEASURE_ORDER = {"NEAR_ZERO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
EXPLICITNESS_ORDER = {"SUGGESTED": 0, "SENSUAL": 1, "FRANK": 2}
PARTNERED_CEILING = "SENSUAL"          # decisão humana OQ-N4
DSR_ESCALATION_FROM_INDEX = 3          # a partir de DSR-4, teto não cresce
DSR_PLEASURE_FROM_INDEX = 2            # a partir de DSR-3, prazer não cresce
ADULT_KINDS = {"SOLO_COMPULSION", "PARTNERED"}
REFLECTION_PRESENCE = {"NONE", "TRACE", "PRESENT"}

MYTH_IDS = [f"MYTH-{i:02d}" for i in range(1, 15)]
REQUIRED_RULE_IDS = [f"IR-N{i:02d}" for i in range(1, 17)]
REQUIRED_SCENE_IDS = [
    "CHORUS_FIRST_GAZE", "THE_REJECTION", "FIRST_WATER", "STATUE_BREAKS",
    "THE_CENTER", "NIGHT_WITHOUT_WORDS", "DSR_OCCURRENCES", "LIA_THREE_VERSIONS",
    "GLASS_JEALOUSY", "SECOND_REFUSAL", "THE_NAME_AT_DAWN", "WE_STILL_LOOK",
]
REQUIRED_LEXICONS = [
    "ontology_confirmation", "motive_declaration", "youth_coding", "twin",
    "clinical_answer", "reflection_named", "decay_glamour", "hypothesis_names",
    "explanatory_closure", "fate_confirmation", "finish_promise",
]
REQUIRED_CHARACTER_AGES = {"CHR-NARCISO": 27}
CHORUS_POV = "Coro"
MIN_ADULT_AGE = 18
MIN_CHORUS_AGE = 21
REFLECTION_NAME_TOKENS = ("reflexo", "reflection")

ANCHOR_RE = re.compile(r"^(SCENE|TURN):(.+)$")
REREAD_ANCHOR_RE = re.compile(r"^(TURN|SCENE|IL|OBJECT):(.+)$")
IL_RE = re.compile(r"^IL-\d{2}$")
IMITATION_RE = re.compile(r"\bno estilo de\b|\bao estilo de\b|\bin the style of\b", re.IGNORECASE)
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".toml"}
PLACEHOLDER = "TO_" + "DEFINE"

# --- vocabulário do canon interpretativo (Slice 2) ----------------------------

HYPOTHESIS_IDS = ["H-PROJ", "H-SUPER", "H-SELF", "H-OTHER", "H-GAZE"]
FORBIDDEN_HYPOTHESES = {"H-TWIN"}                     # OQ-N2
SUPPORT_VALUES = {"S", "C", "X", "-"}
STRENGTH_ORDER = {"WEAK": 0, "MEDIUM": 1, "STRONG": 2}
CONSENT_MODEL_BY_DSR = {                              # OQ-N5, SDD 11.4
    1: ("FULL", "RESPECTED"), 2: ("FULL", "RESPECTED"), 3: ("FULL", "PUSHED"),
    4: ("CONSTRAINED", "PUSHED"), 5: ("CONSTRAINED", "PUSHED"), 6: ("CONSTRAINED", "VIOLATED"),
}
PARTNERED_CONSENT = {"canonical": "CONSENSUAL", "ability_to_refuse": "FULL", "boundary_state": "NEGOTIATED"}
PARTNERED_PARTICIPANTS = {"CHR-NARCISO", "CHR-ECO"}
HIDDEN_ANSWER_KEYS = {"truth", "answer", "true_nature", "real_identity", "hidden_answer", "resposta", "verdade"}
LOVE_BELIEF_IDS = ("RB-LOVE-A", "RB-LOVE-B")
AMBIGUITY_BELIEF_PREFIXES = ("RB-RFX", "RB-LOVE")
OPEN_TRUTH = "INCOMPLETE"
REQUIRED_UNKNOWN_ID = "UNK-NAR-001"
REQUIRED_UNKNOWN_STATUS = "MUST_REMAIN_UNKNOWN"
REQUIRED_PROHIBITED_IDS = [f"PRO-NAR-{i:03d}" for i in range(1, 7)]
SECTION_EVENT_KIND = {
    "reflection_evidence": "REFLECTION_EVIDENCE",
    "love_readings": "LOVE_EVIDENCE",
    "desire_occurrences": "COMPULSION_OCCURRENCE",
    "partnered_intimacy": "INTIMACY",
    "revelations": "REVELATION",
}
IMMUTABLE_FIELDS = {
    "reflection_evidence": ["chapter", "event", "perception", "support"],
    "love_readings": ["chapter", "event", "love", "narcissism"],
    "desire_occurrences": ["chapter", "event", "function", "pleasure", "explicitness_ceiling", "consent_model"],
    "partnered_intimacy": ["chapter", "event", "explicitness_ceiling", "consent_model"],
    "revelations": ["chapter", "event", "revises", "formed_by", "discloses", "second_read"],
    # pista com text_anchor gravado está realizada; âncoras novas podem entrar, as gravadas não mudam
    "reread_clues": ["type", "channel", "clue", "trigger", "first_read", "second_read", "touches"],
}
REREAD_TYPES = {"IMPOSSIBLE_REFLECTION", "ROMANTIC_TO_NARCISSIST", "SELFISH_TO_LOVING",
                "ART_MEANING_SHIFT", "OBJECT", "CHORUS"}
REREAD_CHANNELS = {"TEXT", "ILLUSTRATION", "OBJECT"}
REREAD_VISUAL_CHANNELS = {"ILLUSTRATION", "OBJECT"}
REREAD_EXTRA_TOUCHES = {"LOVE-A", "LOVE-B"}
MIN_REREAD_PER_ACT = 3
MIN_REREAD_VISUAL = 4
REREAD_TEXT_CHANNEL = "TEXT"
TEXT_ANCHOR_RE = re.compile(r'^TEXT:(\d+):"(.+)"$')

# --- final e revelações (Slice 6) ---------------------------------------------------
REVELATION_ID_RE = re.compile(r"^REV-[A-Z0-9-]+$")
GT_ID_RE = re.compile(r"^GT-[A-Z]+-\d{2}$")
SEALED_READER_ACCESS = "NEVER"
FATE_OPEN_FROM_CHAPTER = 31          # THE_NAME_AT_DAWN: dali em diante o destino de Narciso fica aberto
FINAL_EVIDENCE_SECTIONS = ("reflection_evidence", "love_readings")
FINAL_EVIDENCE_EVENT_KINDS = {"REFLECTION_EVIDENCE", "LOVE_EVIDENCE"}

# --- runtime -------------------------------------------------------------------

CANON_FILE = "canon/NARCISO_INTERPRETIVE_CANON.yaml"
LEDGER_FILE = "canon/CAUSAL_LEDGER.yaml"
REGISTRY_FILE = "canon/CANON_REGISTRY.yaml"
REVIEW_FILE = "reviews/NARCISO_AMBIGUITY_REVIEW.md"
SNAPSHOT_DIR = "canon/snapshots"
SNAPSHOT_PREFIX = "NARCISO_INTERPRETIVE_CANON"
RAW_CHAPTER_RE = re.compile(r"^chapter_(\d+)\.md$")
FINAL_MANUSCRIPT = "manuscript/final/MANUSCRIPT_FINAL_PTBR.md"
CHAPTER_HEADING_RE = re.compile(r"^# (\d+)\. (.+)$")
OTHER_HEADING_RE = re.compile(r"^#{1,2} (?!\d+\. )(.+)$")
CLOSURE_RE = re.compile(r"ep[ií]logo|pr[oó]logo|nota d[ao] autor|posf[aá]cio|gloss[aá]rio", re.IGNORECASE)
DIALOGUE_PREFIXES = ("—", "–", "-", '"', "“")
SNAPSHOT_NAME_RE = re.compile(r"^[A-Z0-9_]+$")

# --- vocabulário visual (Slice 3) ----------------------------------------------

VISUAL_CANON_FILE = "canon/VISUAL_NARRATIVE_CANON.yaml"
FIGURE_ID = "FIG-NARCISO"
SIGIL_ID = "SIG-ESPELHO"
REQUIRED_SYMBOL_IDS = ["SYM-ESPELHO", "SYM-AGUA", "SYM-NARCISO", "SYM-OURO", "SYM-MARMORE",
                       "SYM-RACHADURA", "SYM-GOTA"]
SINGLE_COUNT_SYMBOLS = ("SYM-NARCISO", "SYM-GOTA")
DECAY_STATES = ["D0_PRISTINE", "D1_SLEEPLESS", "D2_FEVER", "D3_WITHERING", "D4_MARBLE", "D5_TRACE"]
DECAY_TRIGGERS = {
    "D1_SLEEPLESS": "SCENE:STATUE_BREAKS",
    "D2_FEVER": "SCENE:THE_CENTER",
    "D3_WITHERING": "LEDGER:EV-DSR-4",
    "D4_MARBLE": "LEDGER:EV-DSR-5",
    "D5_TRACE": "SCENE:THE_NAME_AT_DAWN",
}
PUBLIC_DECAY_STATE = "D0_PRISTINE"
REQUIRED_VETO_IDS = [f"VETO-N{i:02d}" for i in range(1, 15)]
BOOK_METAL_MATERIAL = "AGED_GOLD"
SILVER_TOKENS = ("prata", "prateado", "silver")
SILVER_FINISH_MATERIAL = "SILVER_MIRROR"      # decisão humana OQ-N6
SILVER_FINISH_ELEMENT = "SYM-ESPELHO"
SILVER_FINISH_COST = "COLLECTOR_ONLY"
COVER_OVERRIDE_KEY = "defaults.forbid_literal_protagonist_on_cover"   # decisão humana OQ-N1
COVER_MAX_VISIBLE_RATIO = 0.60
PUBLIC_SURFACES = {"FRONT_COVER", "BACK_COVER", "SPINE", "MARKETING_COVER", "DUST_JACKET_FRONT",
                   "DUST_JACKET_BACK", "DUST_JACKET_SPINE", "PROMO"}
REFLECTION_STATES = {"NONE", "TRUE_MIRROR", "ANOMALOUS_MIRROR", "FRAGMENTED", "OCCLUDED", "DOUBLE",
                     "ABSENT_REFLECTION"}
REFLECTION_ANOMALIES = {"mole", "ring", "scar", "part", "mouth", "decay_offset", "angle"}
FACE_CANON_SEED = "planning/FACE_CANON.seed.md"
VISUAL_BIBLE_SEED = "planning/CHARACTER_VISUAL_BIBLE.seed.md"
FACE_CANON_REQUIRED_TERMS = ["FV-NARCISO-01", "pinta", "olho direito", "canto esquerdo", "repartido à esquerda",
                             "cicatriz", "palma esquerda", "indicador direito", "27 anos"]
VISUAL_BIBLE_REQUIRED_SECTIONS = ["REFLECTION_RULES", "DECAY_TIMELINE", "Reconhecimento por fragmento",
                                  "Nudez artística"]
VISUAL_TRIGGER_RE = re.compile(r"^(SCENE|TURN|LEDGER):(.+)$")

# --- vocabulário de pranchas (Slice 4) --------------------------------------------

PLATE_CATEGORIES = {"HERO", "CHAPTER", "SYMBOL", "REFLECTION", "BODY_DETAIL", "DECAY", "CALLBACK"}
PLATE_SYMMETRY_BY_ACT = {0: "STRICT", 1: "BROKEN", 2: "FRAGMENTED"}
PLATE_CROPS_BY_ACT = {0: {"WIDE", "MEDIUM", "CLOSE"}, 1: {"MEDIUM", "CLOSE", "EXTREME_CLOSE"},
                      2: {"CLOSE", "EXTREME_CLOSE", "TRACE"}}
PLATE_NUDITY_CATEGORIES = {"HERO", "BODY_DETAIL", "REFLECTION"}
PLATE_SPOILER_LEVELS = ["NONE", "LOW", "MEDIUM", "HIGH", "CORE"]
PLATE_AFTER_PLACEMENTS = {"AFTER", "HINGE"}
GAZE_WITHDRAWAL_CHAPTER = 22
MAX_TOWARD_READER_PLATES = 4
MAX_DOUBLE_PLATES = 2
MAX_ABSENT_PLATES = 1
MIN_FORESHADOW_RATIO = 0.25
QA_ANOMALY_TOKEN = "anomalia"
APPROVED_ILLUSTRATIONS_DIR = "images/approved"
ILLUSTRATION_WORK_DIR = "images/illustrations"
ILLUSTRATION_PROMPTS_DIR = "images/prompts"
ILLUSTRATION_ID_FILE_RE = re.compile(r"^(IL-\d{2})")

# --- livro como espelho (Slice 5) --------------------------------------------------

MIRROR_MANIFESTATION_FILE = "planning/MIRROR_MANIFESTATION.yaml"
EDITION_TARGET_IDS = ["kindle_ebook", "kdp_paperback", "kdp_hardcover", "collector"]
MANIFEST_VALUES = {"INCLUDE", "SEQUENTIAL", "ASSET", "OMIT", "OUTER_ONLY"}
REQUIRED_MIRROR_TECHNIQUES = ["STRUCTURAL_PALINDROME", "IMAGE_OPENER_SPREAD", "CENTRAL_SPREAD", "DISTANT_CALLBACKS",
                              "TITLE_ECHO", "ACT_ORNAMENT", "DROP_CAP", "ACT_WATER_PAGES", "HIDDEN_TRUTH_CASE"]
KINDLE_REQUIRED = {"IMAGE_OPENER_SPREAD": "SEQUENTIAL", "CENTRAL_SPREAD": "SEQUENTIAL", "TITLE_ECHO": "OMIT",
                   "ACT_ORNAMENT": "OMIT", "DROP_CAP": "OMIT", "HIDDEN_TRUTH_CASE": "OMIT"}
PHYSICAL_MIRROR_SURFACE = "INSERT"
PHYSICAL_MIRROR_EDITION = "collector"
TITLE_ECHO_ACT = 1  # índice do Ato II em spec.movements

# --- posse e produção (Slice 7) ------------------------------------------------------

PRINT_SPEC_SEED = "seeds/PRINT_SPEC.seed.yaml"
PRINTER_PROFILE_TEMPLATE = "seeds/PRINTER_PROFILE.template.yaml"
PRINTER_RESEARCH_DOC = "planning/PRINTER_PROFILE_RESEARCH.md"
PRINTER_RESEARCH_SECTIONS = ["## Efeitos a confirmar", "## Evidência exigida", "## Produção", "## Decisão humana"]
PRINT_TARGETS = ["kdp_paperback", "kdp_hardcover", "collector"]
INTERIOR_INKS = {"BLACK", "STANDARD_COLOR", "PREMIUM_COLOR"}
COLLECTOR_TARGET = "collector"
MIRROR_EFFECTS = {"MIRROR_BOARD", "METALLIZED_PAPER"}
MIRROR_AREA_MAX_RATIO = 0.06
MIRROR_CONTRAST = "LOW"
EDITION_PLAN_TEMPLATE = "layout/editions/{target}/EDITION_PLAN.yaml"
CAPABILITIES_FILE = "templates/EDITION_CAPABILITIES.yaml"
PRINTER_PROFILE_FILE = "layout/PRINTER_PROFILE.yaml"
KDP_REQUIREMENTS_FILE = "layout/KDP_CURRENT_REQUIREMENTS.md"
PRINTER_EVIDENCE_FIELDS = ("vendor", "quote_ref", "date")
PRODUCTION_KEYS = ("numbered", "signed", "limited")
MARKETING_FILES = [  # saídas de T800/T802: textos de loja e redes, comuns a todos os alvos KDP
    "media/KDP_DESCRIPTION_4000.txt", "media/KDP_DESCRIPTION_SHORT.txt", "media/KDP_KEYWORDS.md",
    "media/SHAREABLE_EXCERPTS.md", "media/INSTAGRAM_STORIES_IDEAS.md", "media/outputs/INSTAGRAM_STORIES_COPY.md",
]


# --- utilidades ---------------------------------------------------------------

def finding(category: str, severity: str, chapter, evidence: str, detail: str,
            recommended_action: str) -> dict:
    return {
        "category": category,
        "severity": severity,
        "chapter": chapter,
        "evidence": evidence,
        "detail": detail,
        "recommended_action": recommended_action,
    }


def strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", str(text))
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize(text: str) -> str:
    return strip_accents(text).casefold()


def lexicon_hits(text: str, terms: list[str], case_sensitive: bool = False) -> list[str]:
    prepare = strip_accents if case_sensitive else normalize
    haystack = prepare(text)
    hits = []
    for term in terms or []:
        needle = prepare(term)
        if needle and re.search(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", haystack):
            hits.append(term)
    return hits


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def optional_yaml(path: Path):
    return load_yaml(path) if path.is_file() else None


def chapter_text(chapter: dict) -> str:
    parts = [chapter.get("function"), chapter.get("dramatic_question"), chapter.get("irreversible_turn")]
    parts.extend(chapter.get("continuity") or [])
    return " \n".join(str(p) for p in parts if p)


def as_list(value) -> list:
    if value is None:
        return []
    return list(value) if isinstance(value, (list, tuple)) else [value]


def find_base_cliches(book_dir: Path) -> list[str] | None:
    for base in [book_dir, *book_dir.parents]:
        for candidate in (base / "engine" / "templates" / "TEXT_QUALITY_DEFAULTS.yaml",
                          base / "templates" / "TEXT_QUALITY_DEFAULTS.yaml"):
            if candidate.is_file():
                data = load_yaml(candidate)
                return list(((data.get("spec") or {}).get("cliches") or {}).get("patterns") or [])
    return None


def _lexicons(bundle: dict) -> dict:
    return (bundle.get("lexicons") or {}).get("lexicons") or {}


# --- carga --------------------------------------------------------------------

def load_bundle(book_dir: Path) -> dict:
    """Carrega o pacote inteiro num dicionário. As checagens só leem este
    dicionário, o que permite testar mutações em memória."""
    book_dir = Path(book_dir)
    spec = load_yaml(book_dir / "BOOK_SPEC.yaml")
    sp = spec.get("spec") or {}

    texts = {}
    for path in sorted(book_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            texts[path.relative_to(book_dir).as_posix()] = path.read_text(encoding="utf-8")

    return {
        "spec": spec,
        "architecture": optional_yaml(book_dir / sp.get("chapter_architecture_file", "chapter_architecture.yaml")) or {},
        "rules": optional_yaml(book_dir / sp.get("immutable_rules_file", "immutable_rules.yaml")) or {},
        "scenes": optional_yaml(book_dir / sp.get("protected_scenes_file", "protected_scenes.yaml")) or {},
        "myth": optional_yaml(book_dir / "planning" / "MYTH_DNA_MAP.yaml") or {},
        "roster": optional_yaml(book_dir / "planning" / "CHARACTER_ROSTER.yaml") or {},
        "lexicons": optional_yaml(book_dir / "planning" / "LEXICONS.yaml") or {},
        "text_quality": optional_yaml(book_dir / "text_quality.yaml"),
        "interpretive_seed": optional_yaml(book_dir / "seeds" / "INTERPRETIVE_CANON.seed.yaml"),
        "visual_seed": optional_yaml(book_dir / "seeds" / "VISUAL_NARRATIVE_CANON.seed.yaml"),
        "mirror_manifestation": optional_yaml(book_dir / MIRROR_MANIFESTATION_FILE),
        "print_spec_seed": optional_yaml(book_dir / PRINT_SPEC_SEED),
        "printer_profile_template": optional_yaml(book_dir / PRINTER_PROFILE_TEMPLATE),
        "printer_research": texts.get(PRINTER_RESEARCH_DOC),
        "face_canon_seed": texts.get(FACE_CANON_SEED),
        "visual_bible_seed": texts.get(VISUAL_BIBLE_SEED),
        "world_seed": texts.get(str(sp.get("world_rules_seed", "seeds/WORLD_RULES_SEED.md")), ""),
        "texts": texts,
        "base_cliches": find_base_cliches(book_dir),
    }


def load_runtime(runtime: Path, baseline: str | None = None) -> dict:
    runtime = Path(runtime)
    raw = {}
    raw_dir = runtime / "manuscript" / "raw"
    if raw_dir.is_dir():
        for path in raw_dir.iterdir():
            match = RAW_CHAPTER_RE.match(path.name)
            if match and path.is_file():
                raw[int(match.group(1))] = path.read_text(encoding="utf-8")
    final_path = runtime / FINAL_MANUSCRIPT
    artifacts: dict[str, dict] = {}
    for path in sorted((runtime / APPROVED_ILLUSTRATIONS_DIR).glob("IL-*.jpg")):
        artifacts.setdefault(path.stem, {})["approved"] = True
    for path in sorted((runtime / ILLUSTRATION_PROMPTS_DIR).glob("IL-*_IMAGE_BRIEF.md")):
        match = ILLUSTRATION_ID_FILE_RE.match(path.name)
        if match:
            artifacts.setdefault(match.group(1), {})["brief"] = path.read_text(encoding="utf-8")
    for path in sorted((runtime / ILLUSTRATION_WORK_DIR).glob("IL-*/CONTINUITY_QA.md")):
        artifacts.setdefault(path.parent.name, {})["continuity_qa"] = path.read_text(encoding="utf-8")
    marketing = {rel: (runtime / rel).read_text(encoding="utf-8")
                 for rel in MARKETING_FILES if (runtime / rel).is_file()}
    rt = {
        "edition_plans": {t: optional_yaml(runtime / EDITION_PLAN_TEMPLATE.format(target=t)) for t in EDITION_TARGET_IDS},
        "capabilities": optional_yaml(runtime / CAPABILITIES_FILE),
        "printer_profile": optional_yaml(runtime / PRINTER_PROFILE_FILE),
        "has_kdp_requirements": (runtime / KDP_REQUIREMENTS_FILE).is_file(),
        "marketing": marketing,
        "illustration_artifacts": artifacts,
        "runtime": str(runtime),
        "bundle": load_bundle(runtime / "book"),
        "canon": optional_yaml(runtime / CANON_FILE),
        "ledger": optional_yaml(runtime / LEDGER_FILE),
        "registry": optional_yaml(runtime / REGISTRY_FILE),
        "visual_canon": optional_yaml(runtime / VISUAL_CANON_FILE),
        "has_review": (runtime / REVIEW_FILE).is_file(),
        "has_wave00_snapshot": (runtime / SNAPSHOT_DIR / f"{SNAPSHOT_PREFIX}.WAVE_00.yaml").is_file(),
        "raw_chapters": raw,
        "final_manuscript": final_path.read_text(encoding="utf-8") if final_path.is_file() else None,
        "baseline_path": baseline,
        "baseline": None,
    }
    if baseline:
        rt["baseline"] = optional_yaml(runtime / baseline)
    return rt


# --- regras do pacote (Slice 1) -----------------------------------------------

def _chapters(bundle: dict) -> list[dict]:
    return list((bundle.get("architecture") or {}).get("chapters") or [])


def _count(bundle: dict) -> int:
    return int(((bundle.get("spec") or {}).get("metadata") or {}).get("chapter_count") or 0)


def check_structure(bundle: dict) -> list[dict]:
    out = []
    count = _count(bundle)
    sp = (bundle.get("spec") or {}).get("spec") or {}
    titles = {int(k): v for k, v in (sp.get("chapter_titles") or {}).items()}
    chapters = _chapters(bundle)
    if len(chapters) != count:
        out.append(finding("CHAPTER_COUNT_MISMATCH", "HIGH", "WHOLE_BOOK",
                           f"architecture={len(chapters)} spec={count}",
                           "chapter_architecture.yaml e BOOK_SPEC.yaml divergem.",
                           "Alinhar a contagem de capítulos."))
    numbers = [c.get("number") for c in chapters]
    if numbers != list(range(1, len(chapters) + 1)):
        out.append(finding("CHAPTER_ORDER_INVALID", "HIGH", "WHOLE_BOOK", str(numbers),
                           "Capítulos precisam estar numerados em ordem, sem lacunas.",
                           "Renumerar a arquitetura."))
    required = ["function", "irreversible_turn", "pov", "desire_stage", "mirror_of",
                "reflection_presence", "dramatic_question"]
    for chapter in chapters:
        n = chapter.get("number")
        if titles.get(n) != chapter.get("title"):
            out.append(finding("CHAPTER_TITLE_MISMATCH", "HIGH", n,
                               f"spec={titles.get(n)!r} architecture={chapter.get('title')!r}",
                               "Título do capítulo difere entre BOOK_SPEC e arquitetura.",
                               "Usar o mesmo título nos dois arquivos."))
        for field in required:
            if chapter.get(field) in (None, "", []):
                out.append(finding("CHAPTER_FIELD_MISSING", "HIGH", n, field,
                                   f"Campo obrigatório `{field}` ausente.",
                                   "Preencher o campo conforme a seção 7.4 da SDD."))
        if chapter.get("reflection_presence") not in (None, *REFLECTION_PRESENCE):
            out.append(finding("INVALID_ENUM", "HIGH", n,
                               f"reflection_presence={chapter.get('reflection_presence')}",
                               "Valores: NONE, TRACE, PRESENT.", "Corrigir o valor."))
        if not (chapter.get("emotional_movement") or {}).get("intensity"):
            out.append(finding("EMOTIONAL_MOVEMENT_MISSING", "MEDIUM", n, "emotional_movement",
                               "Sem intensidade, o ledger (L6) não mede amplitude.",
                               "Declarar {from, to, intensity}."))
    covered = sorted(c for m in (sp.get("movements") or []) for c in (m.get("chapters") or []))
    if covered != list(range(1, count + 1)):
        out.append(finding("MOVEMENTS_COVERAGE_INVALID", "HIGH", "WHOLE_BOOK", str(covered),
                           "Os atos precisam cobrir todos os capítulos uma única vez.",
                           "Corrigir `movements` no BOOK_SPEC."))
    return out


def check_mirror_and_chorus(bundle: dict) -> list[dict]:
    out = []
    count = _count(bundle)
    chapters = _chapters(bundle)
    for chapter in chapters:
        n = chapter.get("number")
        expected = count + 1 - n
        if chapter.get("mirror_of") != expected:
            out.append(finding("MIRROR_PAIR_BROKEN", "HIGH", n,
                               f"mirror_of={chapter.get('mirror_of')} esperado={expected}",
                               "O capítulo n reflete o capítulo (contagem + 1 − n).",
                               "Corrigir o par espelhado (MIR-04)."))
    chorus = {c.get("number") for c in chapters if c.get("pov") == CHORUS_POV}
    broken = sorted(n for n in chorus if (count + 1 - n) not in chorus)
    if count and (1 not in chorus or count not in chorus):
        broken.append("extremos")
    if broken:
        out.append(finding("CHORUS_STRUCTURE_BROKEN", "HIGH", "WHOLE_BOOK",
                           f"coro={sorted(chorus)} sem par={broken}",
                           "O Coro abre e fecha o livro e aparece em pares espelhados (OQ-N3).",
                           "Restaurar os capítulos do Coro nas posições espelhadas."))
    return out


def check_desire_curve(bundle: dict) -> list[dict]:
    out = []
    chapters = _chapters(bundle)
    highest = -1
    for chapter in chapters:
        n = chapter.get("number")
        stage = chapter.get("desire_stage")
        if stage not in DESIRE_STAGES:
            out.append(finding("INVALID_ENUM", "HIGH", n, f"desire_stage={stage}",
                               f"Valores: {', '.join(DESIRE_STAGES)}.", "Corrigir o estágio."))
            continue
        index = DESIRE_STAGES.index(stage)
        if index < highest:
            anchor = chapter.get("relapse_anchor")
            if not (anchor and n < RELAPSE_LIMIT_CHAPTER):
                out.append(finding("DESIRE_STAGE_REGRESSION", "HIGH", n,
                                   f"{stage} depois de {DESIRE_STAGES[highest]}",
                                   "A curva de desejo não regride sem âncora declarada (IR-N07).",
                                   "Corrigir o estágio ou declarar relapse_anchor antes do capítulo 26."))
        highest = max(highest, index)
    if chapters:
        if chapters[0].get("desire_stage") != DESIRE_STAGES[0] or chapters[-1].get("desire_stage") != DESIRE_STAGES[-1]:
            out.append(finding("DESIRE_CURVE_ENDPOINTS", "MEDIUM", "WHOLE_BOOK",
                               f"{chapters[0].get('desire_stage')} → {chapters[-1].get('desire_stage')}",
                               "A curva começa em CONTEMPLATION e termina em WITHERING.",
                               "Ajustar os estágios dos extremos."))
    return out


def check_adult_content(bundle: dict) -> list[dict]:
    out = []
    chapters = _chapters(bundle)
    roster = {c.get("id"): c for c in (bundle.get("roster") or {}).get("characters") or []}
    youth_terms = _lexicons(bundle).get("youth_coding") or []
    solo = []
    for chapter in chapters:
        n = chapter.get("number")
        content = chapter.get("adult_content")
        if not content:
            continue
        kind = content.get("kind")
        if kind not in ADULT_KINDS:
            out.append(finding("INVALID_ENUM", "HIGH", n, f"adult_content.kind={kind}",
                               "Valores: SOLO_COMPULSION, PARTNERED.", "Corrigir o tipo."))
            continue
        ceiling = content.get("explicitness_ceiling")
        if ceiling not in EXPLICITNESS_ORDER:
            out.append(finding("INVALID_ENUM", "HIGH", n, f"explicitness_ceiling={ceiling}",
                               "Valores: SUGGESTED, SENSUAL, FRANK.", "Declarar o teto de explicitude."))
        if chapter.get("childhood_material"):
            out.append(finding("CHILDHOOD_EROTIC_PROXIMITY", "BLOCKER", n, "adult_content + childhood_material",
                               "Material de infância nunca aparece em capítulo com conteúdo erótico (IR-N06).",
                               "Separar o material de infância deste capítulo."))
        stage = chapter.get("desire_stage")
        if stage in DESIRE_STAGES and DESIRE_STAGES.index(stage) < DESIRE_STAGES.index("EXCITATION"):
            out.append(finding("ADULT_CONTENT_BEFORE_EXCITATION", "HIGH", n, f"desire_stage={stage}",
                               "Conteúdo erótico só a partir do estágio EXCITATION.",
                               "Mover a ocorrência ou revisar a curva."))
        hits = lexicon_hits(chapter_text(chapter), youth_terms)
        if hits:
            out.append(finding("YOUTH_CODING_IN_ADULT_CONTEXT", "BLOCKER", n, ", ".join(hits),
                               "Nenhuma codificação juvenil em capítulo com conteúdo adulto (IR-N05).",
                               "Remover os termos."))
        if kind == "PARTNERED":
            if ceiling in EXPLICITNESS_ORDER and EXPLICITNESS_ORDER[ceiling] > EXPLICITNESS_ORDER[PARTNERED_CEILING]:
                out.append(finding("NIGHT_EXPLICITNESS_ABOVE_CEILING", "BLOCKER", n,
                                   f"explicitness_ceiling={ceiling}",
                                   f"Intimidade entre personagens tem teto {PARTNERED_CEILING} (OQ-N4, DDC-09).",
                                   f"Reduzir o teto para {PARTNERED_CEILING}."))
            for participant in content.get("participants") or []:
                if participant not in roster:
                    out.append(finding("UNKNOWN_PARTICIPANT", "HIGH", n, str(participant),
                                       "Participante de cena adulta precisa existir no elenco com idade canônica.",
                                       "Usar um id de planning/CHARACTER_ROSTER.yaml."))
            if not content.get("consent"):
                out.append(finding("CONSENT_UNDECLARED", "HIGH", n, "adult_content.consent",
                                   "Intimidade entre adultos declara o regime de consentimento (IR-N12).",
                                   "Declarar consent."))
        else:
            solo.append((n, content))

    if len(solo) != len(DSR_FUNCTIONS):
        out.append(finding("DSR_SEQUENCE_INCOMPLETE", "HIGH", "WHOLE_BOOK",
                           f"ocorrências={len(solo)} esperadas={len(DSR_FUNCTIONS)}",
                           "A curva prevê seis ocorrências compulsivas.",
                           "Revisar adult_content dos capítulos."))
    seen_functions: list[str] = []
    previous = None
    for index, (n, content) in enumerate(solo):
        function = content.get("function")
        expected_id = f"DSR-{index + 1}"
        if content.get("occurrence") != expected_id:
            out.append(finding("DSR_ID_MISMATCH", "MEDIUM", n,
                               f"occurrence={content.get('occurrence')} esperado={expected_id}",
                               "Ids das ocorrências seguem a ordem dos capítulos.", "Renumerar."))
        if function in seen_functions:
            out.append(finding("REPETITION_WITHOUT_NEW_MEANING", "HIGH", n, f"function={function}",
                               "Cada retorno do desejo tem função narrativa nova (DDC-02).",
                               "Atribuir a função canônica desta ocorrência."))
        elif index < len(DSR_FUNCTIONS) and function != DSR_FUNCTIONS[index]:
            out.append(finding("DSR_FUNCTION_OUT_OF_ORDER", "HIGH", n,
                               f"function={function} esperado={DSR_FUNCTIONS[index]}",
                               f"Ordem canônica: {' → '.join(DSR_FUNCTIONS)}.", "Corrigir a função."))
        seen_functions.append(function)
        pleasure = content.get("pleasure")
        if pleasure not in PLEASURE_ORDER:
            out.append(finding("INVALID_ENUM", "HIGH", n, f"pleasure={pleasure}",
                               "Valores: HIGH, MEDIUM, LOW, NEAR_ZERO.", "Corrigir o valor."))
        if previous is not None:
            prev_content = previous[1]
            ceiling, prev_ceiling = content.get("explicitness_ceiling"), prev_content.get("explicitness_ceiling")
            if (index >= DSR_ESCALATION_FROM_INDEX and ceiling in EXPLICITNESS_ORDER
                    and prev_ceiling in EXPLICITNESS_ORDER
                    and EXPLICITNESS_ORDER[ceiling] > EXPLICITNESS_ORDER[prev_ceiling]):
                out.append(finding("EXPLICITNESS_ESCALATION", "BLOCKER", n,
                                   f"{prev_ceiling} → {ceiling}",
                                   "A partir da quarta ocorrência a explicitude não cresce (DDC-03).",
                                   "Reduzir o teto de explicitude."))
            prev_pleasure = prev_content.get("pleasure")
            if (index >= DSR_PLEASURE_FROM_INDEX and pleasure in PLEASURE_ORDER
                    and prev_pleasure in PLEASURE_ORDER
                    and PLEASURE_ORDER[pleasure] > PLEASURE_ORDER[prev_pleasure]):
                out.append(finding("PLEASURE_CURVE_BROKEN", "HIGH", n, f"{prev_pleasure} → {pleasure}",
                                   "A partir da terceira ocorrência o prazer não cresce (DDC-04).",
                                   "Reduzir o prazer declarado."))
        previous = (n, content)
    if solo and solo[-1][1].get("explicitness_ceiling") != "SUGGESTED":
        out.append(finding("EXPLICITNESS_ESCALATION", "BLOCKER", solo[-1][0],
                           f"última ocorrência={solo[-1][1].get('explicitness_ceiling')}",
                           "A última ocorrência é quase ausência de prazer, com teto SUGGESTED.",
                           "Definir explicitness_ceiling: SUGGESTED."))
    return out


def check_roster(bundle: dict) -> list[dict]:
    out = []
    characters = (bundle.get("roster") or {}).get("characters") or []
    if not characters:
        out.append(finding("ROSTER_MISSING", "HIGH", "WHOLE_BOOK", "planning/CHARACTER_ROSTER.yaml",
                           "Sem elenco não há como provar idade adulta.", "Criar o elenco."))
    for character in characters:
        cid = character.get("id")
        age = character.get("age")
        label = f"{cid} age={age}"
        if not isinstance(age, int) or isinstance(age, bool) or age < MIN_ADULT_AGE:
            out.append(finding("ADULT_AGE_FAIL", "BLOCKER", "WHOLE_BOOK", label,
                               "Toda personagem tem idade canônica inteira ≥ 18 (IR-N05).",
                               "Declarar idade adulta ou remover a personagem."))
        elif character.get("role") == "CHORUS" and age < MIN_CHORUS_AGE:
            out.append(finding("CHORUS_MEMBER_UNDER_21", "HIGH", "WHOLE_BOOK", label,
                               "Membros nomeados do Coro têm 21 anos ou mais.", "Ajustar a idade."))
        naming = normalize(f"{cid} {character.get('name', '')}")
        if any(token in naming for token in REFLECTION_NAME_TOKENS):
            out.append(finding("REFLECTION_AS_CHARACTER", "BLOCKER", "WHOLE_BOOK", label,
                               "O que olha de volta nunca é personagem (SDD 9.5, NO_HIDDEN_ANSWER).",
                               "Remover a entrada do elenco."))
    for cid, expected in REQUIRED_CHARACTER_AGES.items():
        match = next((c for c in characters if c.get("id") == cid), None)
        if match is None or match.get("age") != expected:
            out.append(finding("CANON_AGE_MISMATCH", "HIGH", "WHOLE_BOOK",
                               f"{cid} age={None if match is None else match.get('age')}",
                               f"Idade canônica de {cid} é {expected}.", "Corrigir o elenco."))
    return out


def check_rules_and_scenes(bundle: dict) -> list[dict]:
    out = []
    count = _count(bundle)
    rules = (bundle.get("rules") or {}).get("rules") or []
    rule_ids = [r.get("id") for r in rules]
    if len(rule_ids) != len(set(rule_ids)):
        out.append(finding("IMMUTABLE_RULE_DUPLICATE", "HIGH", "WHOLE_BOOK", str(rule_ids),
                           "Ids de regra imutável são únicos.", "Remover duplicatas."))
    for rid in REQUIRED_RULE_IDS:
        if rid not in rule_ids:
            out.append(finding("IMMUTABLE_RULE_MISSING", "HIGH", "WHOLE_BOOK", rid,
                               "Regra imutável obrigatória ausente (SDD 7.7).", "Restaurar a regra."))
    for rule in rules:
        if not rule.get("rule") or rule.get("blocking") is not True:
            out.append(finding("IMMUTABLE_RULE_INVALID", "HIGH", "WHOLE_BOOK", str(rule.get("id")),
                               "Regra imutável precisa de texto e blocking: true.", "Corrigir a regra."))
    scenes = (bundle.get("scenes") or {}).get("scenes") or []
    scene_ids = [s.get("id") for s in scenes]
    if len(scene_ids) != len(set(scene_ids)):
        out.append(finding("PROTECTED_SCENE_DUPLICATE", "HIGH", "WHOLE_BOOK", str(scene_ids),
                           "Ids de cena protegida são únicos.", "Remover duplicatas."))
    for sid in REQUIRED_SCENE_IDS:
        if sid not in scene_ids:
            out.append(finding("PROTECTED_SCENE_MISSING", "HIGH", "WHOLE_BOOK", sid,
                               "Cena protegida obrigatória ausente (SDD 7.6).", "Restaurar a cena."))
    for scene in scenes:
        chapters = scene.get("chapters") or []
        invalid = [c for c in chapters if not isinstance(c, int) or c < 1 or c > count]
        if not scene.get("must_preserve") or not scene.get("reject_if") or not chapters or invalid:
            out.append(finding("PROTECTED_SCENE_INVALID", "HIGH", "WHOLE_BOOK", str(scene.get("id")),
                               "Cena protegida precisa de capítulos válidos, must_preserve e reject_if.",
                               "Completar os critérios de auditoria."))
    return out


def check_myth(bundle: dict) -> list[dict]:
    out = []
    count = _count(bundle)
    chapters = {c.get("number"): c for c in _chapters(bundle)}
    scene_chapters = {s.get("id"): set(s.get("chapters") or [])
                      for s in (bundle.get("scenes") or {}).get("scenes") or []}
    elements = {e.get("id"): e for e in (bundle.get("myth") or {}).get("elements") or []}
    for mid in MYTH_IDS:
        element = elements.get(mid)
        if not element or not str(element.get("reinterpretation") or "").strip():
            out.append(finding("MYTH_DNA_LOST", "HIGH", "WHOLE_BOOK", mid,
                               "Elemento do DNA mítico sem reinterpretação (MAC-01).",
                               "Restaurar o elemento em planning/MYTH_DNA_MAP.yaml."))
            continue
        declared = set(element.get("chapters") or [])
        if not declared or any(not isinstance(c, int) or c < 1 or c > count for c in declared):
            out.append(finding("MYTH_CHAPTER_INVALID", "HIGH", "WHOLE_BOOK", f"{mid} chapters={sorted(declared, key=str)}",
                               "Capítulos do elemento mítico precisam existir.", "Corrigir os capítulos."))
        anchors = element.get("anchors") or []
        if not anchors:
            out.append(finding("MYTH_ANCHOR_UNRESOLVED", "HIGH", "WHOLE_BOOK", mid,
                               "Elemento mítico sem âncora narrativa.", "Declarar SCENE: ou TURN:."))
        for anchor in anchors:
            match = ANCHOR_RE.match(str(anchor))
            anchor_chapters: set = set()
            resolved = False
            if match and match.group(1) == "SCENE":
                resolved = match.group(2) in scene_chapters
                anchor_chapters = scene_chapters.get(match.group(2), set())
            elif match and match.group(1) == "TURN" and match.group(2).isdigit():
                number = int(match.group(2))
                resolved = bool((chapters.get(number) or {}).get("irreversible_turn"))
                anchor_chapters = {number}
            if not resolved:
                out.append(finding("MYTH_ANCHOR_UNRESOLVED", "HIGH", "WHOLE_BOOK", f"{mid} {anchor}",
                                   "Âncora não resolve contra cenas protegidas ou viradas de capítulo.",
                                   "Corrigir a âncora."))
            elif declared and not (anchor_chapters & declared):
                out.append(finding("MYTH_ANCHOR_CHAPTER_MISMATCH", "MEDIUM", "WHOLE_BOOK", f"{mid} {anchor}",
                                   "A âncora aponta para capítulos fora dos declarados no elemento.",
                                   "Alinhar capítulos e âncoras."))
    return out


def check_lexicons(bundle: dict) -> list[dict]:
    out = []
    lexicons = _lexicons(bundle)
    for name in REQUIRED_LEXICONS:
        if not lexicons.get(name):
            out.append(finding("LEXICON_MISSING", "HIGH", "WHOLE_BOOK", name,
                               "Léxico obrigatório ausente ou vazio.", "Preencher planning/LEXICONS.yaml."))
    scans = [
        ("ontology_confirmation", "ONTOLOGY_CONFIRMED_IN_PLAN", "HIGH",
         "O plano não pode confirmar a natureza do que olha de volta (IR-N01)."),
        ("motive_declaration", "LOVE_MOTIVE_DECLARED_IN_PLAN", "HIGH",
         "O plano não pode declarar se Narciso amou (IR-N03)."),
        ("clinical_answer", "DIAGNOSIS_AS_ANSWER_IN_PLAN", "HIGH",
         "Diagnóstico não é resposta (IR-N04)."),
        ("twin", "TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER",
         "Não existe hipótese de gêmeo, irmão ou duplo biológico (OQ-N2, UNC-10)."),
    ]
    for chapter in _chapters(bundle):
        text = chapter_text(chapter)
        for lexicon, category, severity, detail in scans:
            hits = lexicon_hits(text, lexicons.get(lexicon))
            if hits:
                out.append(finding(category, severity, chapter.get("number"), ", ".join(hits), detail,
                                   "Reescrever o campo do plano sem o termo."))
    extra_twin_sources = {"planning/CHARACTER_ROSTER.yaml": json.dumps(bundle.get("roster") or {}, ensure_ascii=False),
                          "seeds/WORLD_RULES_SEED.md": bundle.get("world_seed") or ""}
    for source, text in extra_twin_sources.items():
        hits = lexicon_hits(text, lexicons.get("twin"))
        if hits:
            out.append(finding("TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER", "WHOLE_BOOK", f"{source}: {', '.join(hits)}",
                               "Não existe hipótese de gêmeo, irmão ou duplo biológico (OQ-N2, UNC-10).",
                               "Remover o termo."))
    return out


def check_evidence_and_slots(bundle: dict) -> list[dict]:
    out = []
    chapters = _chapters(bundle)
    seen: dict[str, dict[str, int]] = {"reflection_evidence": {}, "love_evidence": {}, "illustration_slots": {}}
    duplicates = {"reflection_evidence": "RFX_DUPLICATE", "love_evidence": "LOVE_EVIDENCE_DUPLICATE",
                  "illustration_slots": "ILLUSTRATION_SLOT_DUPLICATE"}
    for chapter in chapters:
        n = chapter.get("number")
        for field, bucket in seen.items():
            for item in chapter.get(field) or []:
                if field == "illustration_slots" and not IL_RE.match(str(item)):
                    out.append(finding("ILLUSTRATION_SLOT_INVALID", "HIGH", n, str(item),
                                       "Slot de ilustração segue o padrão IL-NN.", "Corrigir o id."))
                if item in bucket:
                    out.append(finding(duplicates[field], "HIGH", n, f"{item} também no capítulo {bucket[item]}",
                                       "Cada id aparece em um único capítulo.", "Remover a duplicata."))
                else:
                    bucket[item] = n
        if chapter.get("reflection_evidence") and chapter.get("reflection_presence") == "NONE":
            out.append(finding("RFX_WITHOUT_PRESENCE", "MEDIUM", n, "reflection_presence=NONE",
                               "Capítulo com evidência precisa de presença TRACE ou PRESENT.",
                               "Ajustar reflection_presence."))
    declaring = [c for c in chapters if c.get("final_evidence")]
    last = chapters[-1] if chapters else {}
    if (len(declaring) != 1 or declaring[0] is not last
            or len(last.get("final_evidence") or []) != 1):
        out.append(finding("FINAL_EVIDENCE_COUNT", "BLOCKER", last.get("number", "WHOLE_BOOK"),
                           f"capítulos={[c.get('number') for c in declaring]} evidências={last.get('final_evidence')}",
                           "Só o último capítulo acrescenta exatamente uma evidência (IR-N10).",
                           "Declarar uma única final_evidence no último capítulo."))
    elif last.get("final_evidence")[0] not in (last.get("reflection_evidence") or []):
        out.append(finding("FINAL_EVIDENCE_UNDECLARED", "HIGH", last.get("number"),
                           str(last.get("final_evidence")),
                           "A evidência final precisa estar entre as evidências do capítulo.",
                           "Alinhar final_evidence e reflection_evidence."))
    return out


def check_text_hygiene(bundle: dict) -> list[dict]:
    out = []
    for rel, text in sorted((bundle.get("texts") or {}).items()):
        if PLACEHOLDER in text:
            out.append(finding("UNRESOLVED_TO_DEFINE", "HIGH", "WHOLE_BOOK", rel,
                               "Marcador de preenchimento pendente no pacote.", "Resolver o marcador."))
        if IMITATION_RE.search(text):
            out.append(finding("IMITATION_REFERENCE", "HIGH", "WHOLE_BOOK", rel,
                               "Referência imitativa a estilo de terceiros (MAC-04).",
                               "Remover a referência."))
    base = bundle.get("base_cliches")
    override = bundle.get("text_quality")
    if base is not None and override is not None:
        patterns = set(((override.get("spec") or {}).get("cliches") or {}).get("patterns") or [])
        missing = [p for p in base if p not in patterns]
        if missing:
            out.append(finding("BASE_CLICHES_DROPPED", "MEDIUM", "WHOLE_BOOK", ", ".join(missing[:5]),
                               "O override substitui a lista base por seção; itens da base sumiram.",
                               "Repetir a lista base inteira em text_quality.yaml."))
    return out


# --- canon interpretativo (Slice 2) -------------------------------------------

def _iter_keys(node, path: str = ""):
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            yield key, here
            yield from _iter_keys(value, here)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _iter_keys(value, f"{path}[{index}]")


def _chapter_to_act(bundle: dict) -> dict[int, int]:
    mapping = {0: 0}
    movements = ((bundle.get("spec") or {}).get("spec") or {}).get("movements") or []
    for index, movement in enumerate(movements):
        for number in movement.get("chapters") or []:
            mapping[number] = index
    return mapping


def resolve_reread_anchor(anchor, bundle: dict) -> int | None:
    match = REREAD_ANCHOR_RE.match(str(anchor or ""))
    if not match:
        return None
    kind, value = match.groups()
    chapters = _chapters(bundle)
    if kind == "OBJECT":
        return 0
    if kind == "TURN":
        if not value.isdigit():
            return None
        number = int(value)
        return number if any(c.get("number") == number and c.get("irreversible_turn") for c in chapters) else None
    if kind == "SCENE":
        for scene in (bundle.get("scenes") or {}).get("scenes") or []:
            if scene.get("id") == value and scene.get("chapters"):
                return min(scene["chapters"])
        return None
    for chapter in chapters:
        if value in (chapter.get("illustration_slots") or []):
            return chapter.get("number")
    return None


def check_interpretive(canon, bundle: dict, source: str) -> list[dict]:
    label = "seeds/INTERPRETIVE_CANON.seed.yaml" if source == "seed" else CANON_FILE
    if not canon:
        return [finding("INTERPRETIVE_CANON_MISSING", "HIGH", "WHOLE_BOOK", label,
                        "O canon interpretativo não existe (T018N / semente).",
                        "Criar o arquivo a partir da semente, conforme INTERPRETIVE_CANON_RUNBOOK.md.")]
    out = []
    lexicons = _lexicons(bundle)
    chapters = {c.get("number"): c for c in _chapters(bundle)}
    policy = canon.get("policy") or {}

    # NO_HIDDEN_ANSWER
    if policy.get("no_hidden_answer") is not True:
        out.append(finding("HIDDEN_ANSWER_PRESENT", "BLOCKER", "WHOLE_BOOK", f"{label}: policy.no_hidden_answer",
                           "A política NO_HIDDEN_ANSWER é obrigatória.", "Definir policy.no_hidden_answer: true."))
    for key, path in _iter_keys(canon):
        if normalize(key) in HIDDEN_ANSWER_KEYS:
            out.append(finding("HIDDEN_ANSWER_PRESENT", "BLOCKER", "WHOLE_BOOK", f"{label}: {path}",
                               "Nenhum campo guarda a verdade do reflexo ou do amor (NO_HIDDEN_ANSWER).",
                               "Remover o campo."))

    # hipóteses
    hypothesis_ids = [h.get("id") for h in canon.get("reflection_hypotheses") or []]
    for forbidden in FORBIDDEN_HYPOTHESES & set(hypothesis_ids):
        out.append(finding("TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER", "WHOLE_BOOK", f"{label}: {forbidden}",
                           "Não existe hipótese de gêmeo (OQ-N2).", "Remover a hipótese."))
    if sorted(h for h in hypothesis_ids if h not in FORBIDDEN_HYPOTHESES) != sorted(HYPOTHESIS_IDS):
        out.append(finding("HYPOTHESIS_SET_INVALID", "HIGH", "WHOLE_BOOK", f"{label}: {hypothesis_ids}",
                           f"Hipóteses canônicas: {', '.join(HYPOTHESIS_IDS)}.", "Corrigir o conjunto."))

    # evidências do reflexo
    evidence = canon.get("reflection_evidence") or []
    plan_rfx = {item: c.get("number") for c in chapters.values() for item in (c.get("reflection_evidence") or [])}
    rows_by_id = {}
    support_counts = {h: {"S": 0, "C": 0, "X": 0} for h in HYPOTHESIS_IDS}
    for row in evidence:
        rid = row.get("id")
        if rid in rows_by_id:
            out.append(finding("RFX_DUPLICATE", "HIGH", row.get("chapter"), f"{label}: {rid}",
                               "Ids de evidência são únicos.", "Remover a duplicata."))
        rows_by_id[rid] = row
        if plan_rfx.get(rid) != row.get("chapter"):
            out.append(finding("RFX_PLAN_MISMATCH", "HIGH", row.get("chapter"),
                               f"{label}: {rid} canon={row.get('chapter')} plano={plan_rfx.get(rid)}",
                               "Evidência e arquitetura de capítulos divergem.", "Alinhar capítulo e id."))
        support = row.get("support") or {}
        if sorted(support) != sorted(HYPOTHESIS_IDS) or any(v not in SUPPORT_VALUES for v in support.values()):
            out.append(finding("INVALID_ENUM", "HIGH", row.get("chapter"), f"{label}: {rid} support={support}",
                               "support declara S, C, X ou - para cada hipótese canônica.", "Corrigir o suporte."))
        s_count = sum(1 for v in support.values() if v == "S")
        x_count = sum(1 for v in support.values() if v == "X")
        if s_count < int(policy.get("min_support_per_evidence", 2)):
            out.append(finding("SINGLE_HYPOTHESIS_EVIDENCE", "HIGH", row.get("chapter"), f"{label}: {rid} S={s_count}",
                               "Toda evidência sustenta ao menos duas hipóteses (UNC-01).",
                               "Reescrever a evidência para sustentar leituras concorrentes."))
        if x_count >= len(HYPOTHESIS_IDS) - 1:
            out.append(finding("EVIDENCE_COLLAPSES_ONTOLOGY", "BLOCKER", row.get("chapter"), f"{label}: {rid} X={x_count}",
                               "Nenhuma evidência exclui todas as hipóteses menos uma (UNC-02).",
                               "Retirar a exclusão."))
        for hypothesis in HYPOTHESIS_IDS:
            value = support.get(hypothesis)
            if value in support_counts[hypothesis]:
                support_counts[hypothesis][value] += 1
        perception = str(row.get("perception") or "")
        if lexicon_hits(perception, lexicons.get("ontology_confirmation")):
            out.append(finding("ONTOLOGY_CONFIRMED_IN_CANON", "HIGH", row.get("chapter"), f"{label}: {rid}",
                               "Evidência descreve percepção, nunca ontologia.", "Reescrever a percepção."))
        if lexicon_hits(perception, lexicons.get("twin")):
            out.append(finding("TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER", row.get("chapter"), f"{label}: {rid}",
                               "Não existe hipótese de gêmeo (OQ-N2).", "Remover o termo."))
    missing_rows = sorted(set(plan_rfx) - set(rows_by_id))
    if missing_rows:
        out.append(finding("RFX_PLAN_MISMATCH", "HIGH", "WHOLE_BOOK", f"{label}: sem linha para {missing_rows}",
                           "Toda evidência planejada tem linha no canon interpretativo.", "Criar as linhas."))
    if evidence:
        viable = [h for h in HYPOTHESIS_IDS if support_counts[h]["X"] == 0]
        if len(viable) < int(policy.get("min_viable_hypotheses_at_end", 3)):
            out.append(finding("ONTOLOGY_CONVERGED", "BLOCKER", "WHOLE_BOOK", f"{label}: viáveis={viable}",
                               "Ao fim do livro ao menos três hipóteses seguem sem exclusão (UNC-03).",
                               "Retirar exclusões."))
        for hypothesis, counts in support_counts.items():
            if counts["S"] < 3:
                out.append(finding("HYPOTHESIS_STARVED", "MEDIUM", "WHOLE_BOOK", f"{label}: {hypothesis} S={counts['S']}",
                                   "Toda hipótese tem ao menos três evidências de suporte (UNC-04).",
                                   "Distribuir suporte."))
            if counts["C"] < 1:
                out.append(finding("HYPOTHESIS_UNCHALLENGED", "MEDIUM", "WHOLE_BOOK", f"{label}: {hypothesis}",
                                   "Toda hipótese é complicada ao menos uma vez (UNC-04).",
                                   "Adicionar uma complicação."))
        s_values = [counts["S"] for counts in support_counts.values()]
        if min(s_values) > 0 and max(s_values) / min(s_values) > float(policy.get("max_support_ratio", 2.0)):
            out.append(finding("HYPOTHESIS_DOMINANCE", "MEDIUM", "WHOLE_BOOK", f"{label}: S={s_values}",
                               "Nenhuma hipótese tem mais que o dobro do suporte da menos sustentada (UNC-05).",
                               "Rebalancear o suporte."))
    last_chapter = chapters.get(max(chapters)) if chapters else {}
    final_ids = (last_chapter or {}).get("final_evidence") or []
    if final_ids and final_ids[0] in rows_by_id:
        final_support = sum(1 for v in (rows_by_id[final_ids[0]].get("support") or {}).values() if v == "S")
        if final_support < int(policy.get("final_evidence_min_support", 3)):
            out.append(finding("FINAL_EVIDENCE_NARROW", "HIGH", last_chapter.get("number"),
                               f"{label}: {final_ids[0]} S={final_support}",
                               "A última evidência é compatível com ao menos três hipóteses (SDD 7.5).",
                               "Abrir a evidência final."))

    # leituras de amor
    love = canon.get("love_readings") or []
    plan_love = {item: c.get("number") for c in chapters.values() for item in (c.get("love_evidence") or [])}
    seen_love = set()
    only_love = only_narcissism = 0
    for row in love:
        rid = row.get("id")
        seen_love.add(rid)
        if plan_love.get(rid) != row.get("chapter"):
            out.append(finding("LOVE_PLAN_MISMATCH", "HIGH", row.get("chapter"),
                               f"{label}: {rid} canon={row.get('chapter')} plano={plan_love.get(rid)}",
                               "Leitura de amor e arquitetura divergem.", "Alinhar capítulo e id."))
        strengths = {}
        for side in ("love", "narcissism"):
            value = (row.get(side) or {}).get("strength")
            if value not in STRENGTH_ORDER or not (row.get(side) or {}).get("reading"):
                out.append(finding("INVALID_ENUM", "HIGH", row.get("chapter"), f"{label}: {rid}.{side}",
                                   "Cada lado declara reading e strength WEAK, MEDIUM ou STRONG.",
                                   "Completar a leitura."))
            strengths[side] = value
        if any(STRENGTH_ORDER.get(v, -1) < STRENGTH_ORDER["MEDIUM"] for v in strengths.values()):
            out.append(finding("LOVE_READING_WEAK", "HIGH", row.get("chapter"), f"{label}: {rid} {strengths}",
                               "As duas leituras são ao menos MEDIUM (LOV-01).", "Fortalecer a leitura fraca."))
        if strengths.get("love") == "STRONG" and strengths.get("narcissism") != "STRONG":
            only_love += 1
        if strengths.get("narcissism") == "STRONG" and strengths.get("love") != "STRONG":
            only_narcissism += 1
        if not set(LOVE_BELIEF_IDS) <= set(row.get("beliefs") or []):
            out.append(finding("LOVE_BELIEFS_MISSING", "HIGH", row.get("chapter"), f"{label}: {rid}",
                               "Todo gesto estabelece as duas crenças abertas do leitor.",
                               "Declarar beliefs: [RB-LOVE-A, RB-LOVE-B]."))
    missing_love = sorted(set(plan_love) - seen_love)
    if missing_love:
        out.append(finding("LOVE_PLAN_MISMATCH", "HIGH", "WHOLE_BOOK", f"{label}: sem linha para {missing_love}",
                           "Todo gesto planejado tem leitura dupla no canon.", "Criar as linhas."))
    if abs(only_love - only_narcissism) > 1:
        out.append(finding("LOVE_BALANCE_TILTED", "MEDIUM", "WHOLE_BOOK",
                           f"{label}: só-amor={only_love} só-narcisismo={only_narcissism}",
                           "A balança das leituras fortes difere no máximo em 1 (LOV-02).", "Rebalancear."))
    if love:
        last_love = max(love, key=lambda r: r.get("chapter") or 0)
        if not ((last_love.get("love") or {}).get("strength") == "STRONG"
                and (last_love.get("narcissism") or {}).get("strength") == "STRONG"):
            out.append(finding("LOVE_FINAL_RESOLVED", "HIGH", last_love.get("chapter"), f"{label}: {last_love.get('id')}",
                               "O último gesto sustenta as duas leituras com força STRONG (LOV-03).",
                               "Reforçar a leitura mais fraca."))

    # ocorrências de desejo
    plan_dsr = {}
    plan_partnered = {}
    for chapter in chapters.values():
        content = chapter.get("adult_content") or {}
        if content.get("kind") == "SOLO_COMPULSION":
            plan_dsr[content.get("occurrence")] = (chapter.get("number"), content)
        elif content.get("kind") == "PARTNERED":
            plan_partnered[chapter.get("number")] = content
    dsr_rows = {row.get("id"): row for row in canon.get("desire_occurrences") or []}
    for occurrence in sorted(set(plan_dsr) | set(dsr_rows), key=str):
        row = dsr_rows.get(occurrence)
        planned = plan_dsr.get(occurrence)
        if row is None or planned is None:
            out.append(finding("DSR_PLAN_MISMATCH", "HIGH", "WHOLE_BOOK", f"{label}: {occurrence}",
                               "Ocorrências do canon e da arquitetura coincidem uma a uma.", "Alinhar as ocorrências."))
            continue
        number, content = planned
        diffs = [field for field in ("function", "pleasure", "explicitness_ceiling")
                 if row.get(field) != content.get(field)]
        if row.get("chapter") != number:
            diffs.append("chapter")
        if diffs:
            out.append(finding("DSR_PLAN_MISMATCH", "HIGH", number, f"{label}: {occurrence} {diffs}",
                               "Ocorrência diverge da arquitetura de capítulos.", "Alinhar os campos."))
        match = re.match(r"^DSR-(\d+)$", str(occurrence))
        expected = CONSENT_MODEL_BY_DSR.get(int(match.group(1))) if match else None
        model = row.get("consent_model") or {}
        if expected and (model.get("ability_to_refuse"), model.get("boundary_state")) != expected:
            out.append(finding("CONSENT_MODEL_MISMATCH", "HIGH", number, f"{label}: {occurrence} {model}",
                               f"Modelo de consentimento decidido para {occurrence}: {expected} (OQ-N5).",
                               "Corrigir consent_model."))
        if not str(row.get("consequence") or "").strip():
            out.append(finding("DSR_WITHOUT_CONSEQUENCE", "HIGH", number, f"{label}: {occurrence}",
                               "Toda ocorrência tem consequência (DDC-05).", "Declarar a consequência."))
    partnered_rows = {row.get("chapter"): row for row in canon.get("partnered_intimacy") or []}
    for number in sorted(set(plan_partnered) | set(partnered_rows), key=str):
        row, content = partnered_rows.get(number), plan_partnered.get(number)
        if row is None or content is None:
            out.append(finding("PARTNERED_PLAN_MISMATCH", "HIGH", number, f"{label}: capítulo {number}",
                               "Intimidade do canon e da arquitetura coincidem.", "Alinhar."))
            continue
        if row.get("explicitness_ceiling") != content.get("explicitness_ceiling"):
            out.append(finding("PARTNERED_PLAN_MISMATCH", "HIGH", number, f"{label}: {row.get('id')}",
                               "Teto de explicitude diverge da arquitetura.", "Alinhar."))
        if EXPLICITNESS_ORDER.get(row.get("explicitness_ceiling"), 99) > EXPLICITNESS_ORDER[PARTNERED_CEILING]:
            out.append(finding("NIGHT_EXPLICITNESS_ABOVE_CEILING", "BLOCKER", number, f"{label}: {row.get('id')}",
                               f"Teto de intimidade entre personagens: {PARTNERED_CEILING} (OQ-N4).", "Reduzir o teto."))
        if (row.get("consent_model") or {}) != PARTNERED_CONSENT:
            out.append(finding("CONSENT_MODEL_MISMATCH", "HIGH", number, f"{label}: {row.get('id')}",
                               f"Modelo de consentimento da intimidade: {PARTNERED_CONSENT}.", "Corrigir consent_model."))

    # pistas de releitura
    act_of = _chapter_to_act(bundle)
    per_act: dict[int, int] = {}
    visual = 0
    valid_touches = set(HYPOTHESIS_IDS) | REREAD_EXTRA_TOUCHES
    for clue in canon.get("reread_clues") or []:
        cid = clue.get("id")
        if clue.get("type") not in REREAD_TYPES or clue.get("channel") not in REREAD_CHANNELS:
            out.append(finding("INVALID_ENUM", "MEDIUM", "WHOLE_BOOK", f"{label}: {cid}",
                               "Tipo ou canal de pista inválido.", "Corrigir type/channel."))
        clue_chapter = resolve_reread_anchor((clue.get("clue") or {}).get("anchor"), bundle)
        trigger_chapter = resolve_reread_anchor((clue.get("trigger") or {}).get("anchor"), bundle)
        if clue_chapter is None or trigger_chapter is None:
            out.append(finding("REREAD_ANCHOR_UNRESOLVED", "HIGH", "WHOLE_BOOK", f"{label}: {cid}",
                               "Âncoras de pista resolvem para TURN, SCENE, IL ou OBJECT.", "Corrigir as âncoras."))
        elif trigger_chapter <= clue_chapter:
            out.append(finding("REREAD_CLUE_WITHOUT_TRIGGER", "HIGH", clue_chapter,
                               f"{label}: {cid} pista={clue_chapter} gatilho={trigger_chapter}",
                               "O gatilho da releitura vem depois da pista (RRL-01).", "Mover o gatilho."))
        if clue_chapter is not None:
            act = act_of.get(clue_chapter, 0)
            per_act[act] = per_act.get(act, 0) + 1
        if clue.get("channel") in REREAD_VISUAL_CHANNELS:
            visual += 1
        second = str(clue.get("second_read") or "")
        for lexicon in ("ontology_confirmation", "motive_declaration", "twin"):
            if lexicon_hits(second, lexicons.get(lexicon)):
                out.append(finding("REREAD_RESOLVES_AMBIGUITY", "BLOCKER", clue_chapter, f"{label}: {cid}",
                                   "A segunda leitura nunca resolve o reflexo ou o amor (RRL-02).",
                                   "Reescrever a segunda leitura."))
                break
        invalid = [t for t in clue.get("touches") or [] if t not in valid_touches]
        if invalid or not clue.get("touches"):
            out.append(finding("REREAD_TOUCH_INVALID", "MEDIUM", clue_chapter, f"{label}: {cid} {invalid}",
                               "touches cita hipóteses canônicas ou LOVE-A/LOVE-B.", "Corrigir touches."))
    if canon.get("reread_clues") is not None:
        act_count = len(((bundle.get("spec") or {}).get("spec") or {}).get("movements") or []) or 1
        thin_acts = [a + 1 for a in range(act_count) if per_act.get(a, 0) < MIN_REREAD_PER_ACT]
        if thin_acts or visual < MIN_REREAD_VISUAL:
            out.append(finding("REREAD_LAYER_THIN", "MEDIUM", "WHOLE_BOOK",
                               f"{label}: atos fracos={thin_acts} visuais={visual}",
                               f"≥{MIN_REREAD_PER_ACT} pistas por ato e ≥{MIN_REREAD_VISUAL} em ilustração/objeto (RRL-03).",
                               "Adicionar pistas."))

    # revelações não ontológicas (RRL-05)
    count = max(chapters) if chapters else 0
    for row in canon.get("revelations") or []:
        rid, number = row.get("id"), row.get("chapter")
        problems = []
        if not REVELATION_ID_RE.match(str(rid)):
            problems.append("id fora de REV-*")
        if not isinstance(number, int) or not 1 <= number <= count:
            problems.append(f"chapter {number!r}")
        if not row.get("event"):
            problems.append("event ausente")
        if not str(row.get("revises") or "").startswith("RB-"):
            problems.append("revises não é crença RB-*")
        formed = [f for f in as_list(row.get("formed_by")) if isinstance(f, dict)]
        if not formed or any(not str(f.get("event") or "").startswith("EV-") or not isinstance(f.get("chapter"), int)
                             for f in formed):
            problems.append("formed_by declara {event: EV-*, chapter}")
        discloses = as_list(row.get("discloses"))
        if not discloses or any(not GT_ID_RE.match(str(g)) for g in discloses):
            problems.append("discloses sem GT-*")
        if problems:
            out.append(finding("REVELATION_INVALID", "HIGH", number, f"{label}: {rid} {problems}",
                               "Revelação declara evento, crença revisada, cenas de formação e verdade divulgada.",
                               "Completar a linha."))
        late = [f.get("event") for f in formed
                if isinstance(f.get("chapter"), int) and isinstance(number, int) and f["chapter"] >= number]
        if late:
            out.append(finding("RETCON_DISGUISED_AS_TWIST", "BLOCKER", number, f"{label}: {rid} formada em {late}",
                               "A crença revisada foi formada antes da revelação (RRL-05, INV-11).",
                               "Plantar a crença em capítulo anterior."))
        read_text = f"{row.get('first_read') or ''} \n{row.get('second_read') or ''}"
        touches = [h for lexicon in ("ontology_confirmation", "motive_declaration", "twin")
                   for h in lexicon_hits(read_text, lexicons.get(lexicon))]
        if str(row.get("revises") or "").startswith(AMBIGUITY_BELIEF_PREFIXES) or touches:
            out.append(finding("REVELATION_TOUCHES_AMBIGUITY", "BLOCKER", number,
                               f"{label}: {rid} revises={row.get('revises')} termos={touches}",
                               "Revelação muda um fato, nunca o que olha de volta nem se Narciso amou (RRL-02, RRL-05).",
                               "Restringir a revelação a um fato não ontológico."))
        if isinstance(number, int) and number >= count:
            out.append(finding("EXPLANATORY_CLOSURE", "BLOCKER", number, f"{label}: {rid}",
                               "O último capítulo entrega uma evidência, nunca uma revelação (UNC-08).",
                               "Mover a revelação para antes."))
    return out


def _gt_ancestors(events: dict, event_id: str, seen: set | None = None) -> set:
    seen = set() if seen is None else seen
    if event_id in seen:
        return set()
    seen.add(event_id)
    out = set()
    for token in as_list((events.get(event_id) or {}).get("caused_by")):
        token = str(token)
        if token.startswith("GT-"):
            out.add(token)
        elif token.startswith("EV-"):
            out |= _gt_ancestors(events, token, seen)
    return out


def check_revelation_ledger(row: dict, event: dict, ledger: dict, events: dict) -> list[dict]:
    """RRL-05 contra o ledger: mesma ancoragem de INV-11, feita aqui para o
    validador da obra reprovar sem depender do relatório L5 do motor."""
    out = []
    rid, number, belief_id = row.get("id"), row.get("chapter"), row.get("revises")
    if belief_id not in as_list((event.get("beliefs") or {}).get("revises")):
        out.append(finding("REVELATION_NOT_IN_LEDGER", "HIGH", number, f"{rid} → {event.get('id')}",
                           "O evento de revelação revisa a crença declarada (beliefs.revises).",
                           "Declarar beliefs.revises no evento."))
    belief = next((b for b in ledger.get("beliefs") or [] if b.get("id") == belief_id), None)
    if belief is None:
        out.append(finding("REVELATION_NOT_IN_LEDGER", "HIGH", number, f"{rid}: {belief_id}",
                           "A crença revisada existe no ledger.", "Registrar a crença."))
        return out
    about = [a for a in as_list(belief.get("about")) if str(a).startswith("EV-")]
    formed = {f.get("event"): f.get("chapter") for f in as_list(row.get("formed_by")) if isinstance(f, dict)}
    drift = [e for e, chapter in formed.items()
             if e not in about or (events.get(e) or {}).get("chapter") != chapter]
    disclosed = set(as_list(row.get("discloses")))
    if drift or set(as_list(belief.get("disclosed_by_revision"))) != disclosed:
        out.append(finding("REVELATION_NOT_IN_LEDGER", "HIGH", number,
                           f"{rid}: formação divergente={drift} disclosed={belief.get('disclosed_by_revision')}",
                           "Cenas de formação e verdade divulgada da linha e da crença coincidem.", "Alinhar."))
    late = [e for e in about if isinstance((events.get(e) or {}).get("chapter"), int)
            and isinstance(number, int) and events[e]["chapter"] >= number]
    ancestry = set()
    for event_id in about:
        ancestry |= _gt_ancestors(events, event_id)
    if late or not (disclosed & ancestry):
        out.append(finding("RETCON_DISGUISED_AS_TWIST", "BLOCKER", number,
                           f"{rid}: tardias={late} ancestralidade={sorted(ancestry)} divulga={sorted(disclosed)}",
                           "A verdade divulgada já estava na causa das cenas que formaram a crença (RRL-05, INV-11).",
                           "Plantar a verdade em caused_by de uma cena anterior."))
    truths = {gt.get("id"): gt for c in ledger.get("characters") or [] for gt in c.get("ground_truth") or []}
    for gt_id in sorted(disclosed):
        if gt_id not in truths:
            out.append(finding("REVELATION_NOT_IN_LEDGER", "HIGH", number, f"{rid}: {gt_id}",
                               "A verdade divulgada existe em ground_truth.", "Registrar a verdade."))
        elif truths[gt_id].get("reader_access") == SEALED_READER_ACCESS:
            out.append(finding("REVELATION_TOUCHES_AMBIGUITY", "BLOCKER", number, f"{rid}: {gt_id}",
                               "Verdade selada (reader_access NEVER) nunca é revelada.", "Divulgar outra verdade."))
    return out


def check_ledger_crossref(canon, ledger, bundle: dict) -> list[dict]:
    if not ledger:
        return [finding("LEDGER_MISSING", "HIGH", "WHOLE_BOOK", LEDGER_FILE,
                        "O canon interpretativo cruza com o ledger causal.", "Executar T018 antes de validar.")]
    if not canon:
        return []
    out = []
    lexicons = _lexicons(bundle)
    events = {e.get("id"): e for e in ledger.get("events") or []}
    roster = {c.get("id"): c for c in (bundle.get("roster") or {}).get("characters") or []}

    def participants_have_reflection(event):
        return any(any(tok in normalize(p) for tok in REFLECTION_NAME_TOKENS) for p in as_list(event.get("participants")))

    def mutates(event):
        loops = event.get("loops") or {}
        beliefs = event.get("beliefs") or {}
        return bool(event.get("relationship_delta") or event.get("knowledge_delta")
                    or any(loops.get(k) for k in ("opens", "feeds", "resolves"))
                    or any(beliefs.get(k) for k in ("establishes", "revises")))

    for section, kind_tag in SECTION_EVENT_KIND.items():
        for row in canon.get(section) or []:
            rid, event_id = row.get("id"), row.get("event")
            event = events.get(event_id)
            if event is None:
                out.append(finding("EVENT_MISSING", "HIGH", row.get("chapter"), f"{rid} → {event_id}",
                                   "Toda linha do canon interpretativo aponta para um evento do ledger.",
                                   "Criar o evento no ledger (T018N)."))
                continue
            if event.get("chapter") != row.get("chapter"):
                out.append(finding("EVENT_CHAPTER_MISMATCH", "HIGH", row.get("chapter"),
                                   f"{rid} canon={row.get('chapter')} ledger={event.get('chapter')}",
                                   "Capítulo da linha e do evento divergem.", "Alinhar o capítulo."))
            if kind_tag not in as_list(event.get("kind")):
                out.append(finding("EVENT_KIND_MISMATCH", "HIGH", row.get("chapter"), f"{event_id} kind={event.get('kind')}",
                                   f"O evento de {section} carrega o kind {kind_tag}.", "Corrigir kind."))
            if row.get("status") != event.get("status"):
                out.append(finding("STATUS_MISMATCH", "MEDIUM", row.get("chapter"),
                                   f"{rid}={row.get('status')} {event_id}={event.get('status')}",
                                   "Status da linha espelha o do evento.", "Alinhar no CANON_UPDATE."))
            if participants_have_reflection(event):
                out.append(finding("REFLECTION_AS_PARTICIPANT", "BLOCKER", row.get("chapter"), f"{event_id}",
                                   "O que olha de volta nunca é participante (SDD 9.5).", "Remover o participante."))
            if section == "reflection_evidence":
                facts = " ".join(str(f) for f in as_list(event.get("facts")))
                if lexicon_hits(facts, lexicons.get("ontology_confirmation")):
                    out.append(finding("RFX_FACT_NOT_PERCEPTION", "HIGH", row.get("chapter"), event_id,
                                       "facts de evidência descrevem percepção, nunca ontologia.",
                                       "Reescrever facts como percepção."))
                if lexicon_hits(facts, lexicons.get("twin")):
                    out.append(finding("TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER", row.get("chapter"), event_id,
                                       "Não existe hipótese de gêmeo (OQ-N2).", "Remover o termo."))
            elif section == "love_readings":
                if not event.get("relationship_delta"):
                    out.append(finding("LOVE_EVENT_WITHOUT_MUTATION", "HIGH", row.get("chapter"), event_id,
                                       "Todo gesto de amor ambíguo muda a relação (LOV-05).",
                                       "Declarar relationship_delta."))
            elif section == "desire_occurrences":
                if as_list(event.get("participants")) != ["CHR-NARCISO"]:
                    out.append(finding("DSR_PARTICIPANTS_INVALID", "HIGH", row.get("chapter"),
                                       f"{event_id} participants={event.get('participants')}",
                                       "Ocorrência compulsiva tem só Narciso como participante.",
                                       "Corrigir participants."))
                match = re.match(r"^DSR-(\d+)$", str(rid))
                expected = CONSENT_MODEL_BY_DSR.get(int(match.group(1))) if match else None
                consent = event.get("consent") or {}
                if expected and (consent.get("canonical"), consent.get("ability_to_refuse"),
                                 consent.get("boundary_state")) != ("CONSENSUAL", *expected):
                    out.append(finding("CONSENT_MODEL_MISMATCH", "HIGH", row.get("chapter"), f"{event_id} consent={consent}",
                                       f"Consentimento de {rid} no ledger: CONSENSUAL, {expected} (OQ-N5).",
                                       "Corrigir o bloco consent do evento."))
                if not mutates(event):
                    out.append(finding("DSR_WITHOUT_CONSEQUENCE", "HIGH", row.get("chapter"), event_id,
                                       "Ocorrência sem mutação no ledger é ornamental (DDC-05).",
                                       "Declarar o delta da consequência."))
            elif section == "partnered_intimacy":
                if not PARTNERED_PARTICIPANTS <= set(as_list(event.get("participants"))):
                    out.append(finding("UNKNOWN_PARTICIPANT", "HIGH", row.get("chapter"),
                                       f"{event_id} participants={event.get('participants')}",
                                       "A intimidade do capítulo 18 é entre Narciso e Eco.", "Corrigir participants."))
                consent = event.get("consent") or {}
                if {k: consent.get(k) for k in PARTNERED_CONSENT} != PARTNERED_CONSENT:
                    out.append(finding("CONSENT_MODEL_MISMATCH", "HIGH", row.get("chapter"), f"{event_id} consent={consent}",
                                       f"Consentimento da intimidade no ledger: {PARTNERED_CONSENT}.",
                                       "Corrigir o bloco consent do evento."))
            elif section == "revelations":
                out.extend(check_revelation_ledger(row, event, ledger, events))

    for character in ledger.get("characters") or []:
        cid = character.get("id")
        naming = normalize(f"{cid} {character.get('name', '')}")
        if any(token in naming for token in REFLECTION_NAME_TOKENS):
            out.append(finding("REFLECTION_AS_CHARACTER", "BLOCKER", "WHOLE_BOOK", f"{LEDGER_FILE}: {cid}",
                               "O que olha de volta nunca é personagem do ledger (SDD 9.5).", "Remover o personagem."))
        if cid in roster and character.get("age") != roster[cid].get("age"):
            out.append(finding("AGE_CANON_DRIFT", "HIGH", "WHOLE_BOOK",
                               f"{cid} ledger={character.get('age')} elenco={roster[cid].get('age')}",
                               "Idade do ledger e do elenco divergem.", "Alinhar a idade canônica."))

    beliefs = {b.get("id"): b for b in ledger.get("beliefs") or []}
    for belief_id in LOVE_BELIEF_IDS:
        belief = beliefs.get(belief_id)
        if belief is None or belief.get("left_open") is not True:
            out.append(finding("LOVE_BELIEF_RESOLVED", "HIGH", "WHOLE_BOOK", f"{belief_id}",
                               "As crenças RB-LOVE-A e RB-LOVE-B existem e ficam left_open (LOV-06).",
                               "Declarar a crença aberta."))
    for belief_id, belief in beliefs.items():
        if str(belief_id).startswith(AMBIGUITY_BELIEF_PREFIXES):
            if belief.get("truth") != OPEN_TRUTH or belief.get("left_open") is not True:
                out.append(finding("HIDDEN_ANSWER_PRESENT", "BLOCKER", "WHOLE_BOOK",
                                   f"{belief_id} truth={belief.get('truth')} left_open={belief.get('left_open')}",
                                   "Crenças de ambiguidade têm truth INCOMPLETE e left_open true (NO_HIDDEN_ANSWER).",
                                   "Corrigir a crença."))
    for event in ledger.get("events") or []:
        revised = [b for b in as_list((event.get("beliefs") or {}).get("revises"))
                   if str(b).startswith(AMBIGUITY_BELIEF_PREFIXES)]
        if revised:
            out.append(finding("AMBIGUITY_BELIEF_REVISED", "BLOCKER", event.get("chapter"),
                               f"{event.get('id')} revises={revised}",
                               "Nenhum evento revisa crença sobre o reflexo ou o amor (INV-11 não se aplica).",
                               "Remover a revisão."))
    return out


def _collect_ids(node, out: dict):
    if isinstance(node, dict):
        if "id" in node:
            out[str(node["id"])] = node
        for value in node.values():
            _collect_ids(value, out)
    elif isinstance(node, list):
        for value in node:
            _collect_ids(value, out)


def check_registry(registry) -> list[dict]:
    if not registry:
        return [finding("CANON_REGISTRY_MISSING", "HIGH", "WHOLE_BOOK", REGISTRY_FILE,
                        "O registry guarda as incógnitas e inferências proibidas da obra.", "Executar T018.")]
    ids: dict = {}
    _collect_ids(registry, ids)
    out = []
    unknown = ids.get(REQUIRED_UNKNOWN_ID)
    if not unknown or unknown.get("status") != REQUIRED_UNKNOWN_STATUS:
        out.append(finding("UNKNOWNS_MISSING", "HIGH", "WHOLE_BOOK", REQUIRED_UNKNOWN_ID,
                           f"{REQUIRED_UNKNOWN_ID} existe com status {REQUIRED_UNKNOWN_STATUS}.",
                           "Registrar a incógnita."))
    missing = [pid for pid in REQUIRED_PROHIBITED_IDS if pid not in ids]
    if missing:
        out.append(finding("UNKNOWNS_MISSING", "HIGH", "WHOLE_BOOK", ", ".join(missing),
                           "Inferências proibidas PRO-NAR-001..006 existem no registry.",
                           "Registrar as inferências proibidas."))
    return out


def check_plan_artifacts(rt: dict) -> list[dict]:
    out = []
    if not rt.get("has_review"):
        out.append(finding("AMBIGUITY_REVIEW_MISSING", "HIGH", "WHOLE_BOOK", REVIEW_FILE,
                           "T019N_AMBIGUITY_REVIEW não produziu o relatório.", "Executar T019N."))
    if not rt.get("has_wave00_snapshot"):
        out.append(finding("INTERPRETIVE_SNAPSHOT_MISSING", "HIGH", "WHOLE_BOOK",
                           f"{SNAPSHOT_DIR}/{SNAPSHOT_PREFIX}.WAVE_00.yaml",
                           "T021N_INTERPRETIVE_SNAPSHOT não gravou o snapshot inicial.", "Executar T021N."))
    return out


def _row_realized(section: str, row: dict) -> bool:
    if section == "reread_clues":
        return any((row.get(side) or {}).get("text_anchor") for side in ("clue", "trigger"))
    return row.get("status") == "REALIZED"


def _field_changed(section: str, field: str, old, new) -> bool:
    if section == "reread_clues" and field in ("clue", "trigger") and isinstance(old, dict) and isinstance(new, dict):
        return any(new.get(key) != value for key, value in old.items())
    return new != old


def check_immutability(canon, rt: dict) -> list[dict]:
    if rt.get("baseline_path") and rt.get("baseline") is None:
        return [finding("BASELINE_MISSING", "HIGH", "WHOLE_BOOK", str(rt.get("baseline_path")),
                        "O snapshot de baseline não existe.", "Gravar o snapshot da wave anterior.")]
    baseline = rt.get("baseline")
    if not baseline or not canon:
        return []
    out = []
    for section, fields in IMMUTABLE_FIELDS.items():
        current = {row.get("id"): row for row in canon.get(section) or []}
        for old in baseline.get(section) or []:
            if not _row_realized(section, old):
                continue
            new = current.get(old.get("id"))
            if new is None:
                out.append(finding("INTERPRETIVE_RETCON", "BLOCKER", old.get("chapter"), f"{old.get('id')} removida",
                                   "Linha REALIZED não pode sumir (ICN-IMM).", "Restaurar a linha."))
                continue
            changed = [f for f in fields if _field_changed(section, f, old.get(f), new.get(f))]
            if changed:
                out.append(finding("INTERPRETIVE_RETCON", "BLOCKER", old.get("chapter"), f"{old.get('id')} {changed}",
                                   "Linha REALIZED é imutável contra o snapshot anterior (ICN-IMM).",
                                   "Desfazer a mudança ou registrar revisão aprovada."))
    return out


def _is_dialogue(line: str) -> bool:
    return line.lstrip().startswith(DIALOGUE_PREFIXES)


def check_prose(texts: dict[int, str], bundle: dict) -> list[dict]:
    out = []
    lexicons = _lexicons(bundle)
    adult = {c.get("number") for c in _chapters(bundle) if c.get("adult_content")}
    for number in sorted(texts):
        buckets: dict[tuple[str, str], list[str]] = {}

        def add(category, severity, hits):
            buckets.setdefault((category, severity), []).extend(hits)

        for line in texts[number].splitlines():
            if not line.strip():
                continue
            dialogue = _is_dialogue(line)
            hits = lexicon_hits(line, lexicons.get("twin"))
            if hits:
                add("TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER", hits)
            hits = lexicon_hits(line, lexicons.get("ontology_confirmation"))
            if hits:
                add("ONTOLOGY_CONFIRMED_IN_PROSE", "HIGH" if dialogue else "BLOCKER", hits)
            hits = lexicon_hits(line, lexicons.get("motive_declaration"))
            if hits:
                add("LOVE_MOTIVE_DECLARED", "HIGH" if dialogue else "BLOCKER", hits)
            hits = lexicon_hits(line, lexicons.get("clinical_answer"))
            if hits:
                add("DIAGNOSIS_AS_ANSWER", "HIGH", hits)
            hits = lexicon_hits(line, lexicons.get("reflection_named"), case_sensitive=True)
            if hits:
                add("REFLECTION_NAMED", "HIGH", hits)
            if number in adult:
                hits = lexicon_hits(line, lexicons.get("youth_coding"))
                if hits:
                    add("YOUTH_CODING_IN_ADULT_CONTEXT", "BLOCKER", hits)
        details = {
            "TWIN_HYPOTHESIS_INTRODUCED": "Não existe hipótese de gêmeo, irmão ou duplo biológico (OQ-N2).",
            "ONTOLOGY_CONFIRMED_IN_PROSE": "O texto confirma a natureza do que olha de volta (IR-N01).",
            "LOVE_MOTIVE_DECLARED": "O texto declara se Narciso amou (IR-N03).",
            "DIAGNOSIS_AS_ANSWER": "Diagnóstico usado como resposta (IR-N04); o guardião julga o contexto.",
            "REFLECTION_NAMED": "A narração dá nome próprio ao que olha de volta.",
            "YOUTH_CODING_IN_ADULT_CONTEXT": "Codificação juvenil em capítulo com conteúdo adulto (IR-N05).",
        }
        for (category, severity), hits in sorted(buckets.items()):
            out.append(finding(category, severity, number, ", ".join(sorted(set(hits))), details[category],
                               "Reescrever o trecho; o guardião da obra decide a forma."))
    return out


def parse_final_manuscript(text: str) -> tuple[dict[int, str], list[str]]:
    chapters: dict[int, str] = {}
    extra_headings: list[str] = []
    current = None
    buffer: list[str] = []
    for line in text.splitlines():
        heading = CHAPTER_HEADING_RE.match(line)
        if heading:
            if current is not None:
                chapters[current] = "\n".join(buffer)
            current, buffer = int(heading.group(1)), []
            continue
        other = OTHER_HEADING_RE.match(line)
        if other and current is not None:
            extra_headings.append(other.group(1).strip())
        if current is not None:
            buffer.append(line)
    if current is not None:
        chapters[current] = "\n".join(buffer)
    return chapters, extra_headings


def check_final_manuscript(rt: dict) -> list[dict]:
    text = rt.get("final_manuscript")
    if text is None:
        return [finding("MANUSCRIPT_FINAL_MISSING", "HIGH", "WHOLE_BOOK", FINAL_MANUSCRIPT,
                        "Manuscrito final ausente.", "Congelar o manuscrito (T310).")]
    bundle = rt["bundle"]
    count = _count(bundle)
    chapters, extra = parse_final_manuscript(text)
    out = []
    missing = [n for n in range(1, count + 1) if n not in chapters]
    if missing:
        out.append(finding("MANUSCRIPT_CHAPTER_MISSING", "HIGH", "WHOLE_BOOK", str(missing),
                           "Capítulos ausentes no manuscrito final.", "Completar o manuscrito."))
    beyond = sorted(n for n in chapters if n > count)
    if beyond:
        out.append(finding("EXPLANATORY_CLOSURE", "BLOCKER", "WHOLE_BOOK", f"capítulos além de {count}: {beyond}",
                           "Nada vem depois do último capítulo (IR-N09).", "Remover o conteúdo excedente."))
    for heading in extra:
        if CLOSURE_RE.search(heading):
            out.append(finding("EXPLANATORY_CLOSURE", "BLOCKER", "WHOLE_BOOK", heading,
                               "Sem prólogo, epílogo, nota ou glossário no corpo do livro (IR-N09).",
                               "Remover a seção."))
        else:
            out.append(finding("MANUSCRIPT_STRUCTURE_UNEXPECTED", "MEDIUM", "WHOLE_BOOK", heading,
                               "Cabeçalho fora do padrão de capítulo.", "Confirmar com o layout."))
    out.extend(check_prose({n: t for n, t in chapters.items() if n <= count}, bundle))
    lexicons = _lexicons(bundle)
    for number, body in sorted(chapters.items()):
        if number > count:
            continue
        if number >= count:
            hits = lexicon_hits(body, lexicons.get("explanatory_closure"))
            if hits:
                out.append(finding("EXPLANATORY_CLOSURE", "BLOCKER", number, ", ".join(sorted(set(hits))),
                                   "Depois do capítulo 32 não há explicação, laudo, carta ou 'anos depois' (UNC-08).",
                                   "Terminar na evidência; o guardião decide a forma."))
        if number >= FATE_OPEN_FROM_CHAPTER:
            hits = lexicon_hits(body, lexicons.get("fate_confirmation"))
            if hits:
                out.append(finding("FATE_RESOLVED", "BLOCKER", number, ", ".join(sorted(set(hits))),
                                   "Nem morte nem sobrevivência de Narciso são confirmadas (SDD 7.5).",
                                   "Reescrever sem confirmar o destino."))
    out.extend(check_reread_text_anchors(rt.get("canon"), bundle, chapters))
    return out


def _planned_anchor_chapters(anchor, bundle: dict) -> set[int]:
    match = ANCHOR_RE.match(str(anchor or ""))
    if not match:
        return set()
    kind, value = match.groups()
    if kind == "TURN":
        return {int(value)} if value.isdigit() else set()
    scene = next((s for s in (bundle.get("scenes") or {}).get("scenes") or [] if s.get("id") == value), None)
    return set((scene or {}).get("chapters") or [])


def check_reread_text_anchors(canon, bundle: dict, chapters: dict[int, str]) -> list[dict]:
    """RRL-04: pista de texto aponta para um trecho literal do manuscrito
    congelado, no capítulo da âncora planejada (TURN ou cena protegida)."""
    out = []
    for clue in (canon or {}).get("reread_clues") or []:
        if clue.get("channel") != REREAD_TEXT_CHANNEL:
            continue
        for side in ("clue", "trigger"):
            block = clue.get(side) or {}
            planned = _planned_anchor_chapters(block.get("anchor"), bundle)
            if not planned:
                continue  # IL: e OBJECT: não são texto
            token = block.get("text_anchor")
            match = TEXT_ANCHOR_RE.match(str(token or ""))
            problem = None
            if token is None:
                problem = "text_anchor ausente"
            elif not match:
                problem = f"malformado {token!r}"
            elif int(match.group(1)) not in planned:
                problem = f"capítulo {match.group(1)} fora de {sorted(planned)}"
            elif match.group(2) not in chapters.get(int(match.group(1)), ""):
                problem = "trecho não encontrado no manuscrito congelado"
            if problem:
                out.append(finding("REREAD_ANCHOR_MISSING", "HIGH", min(planned), f"{clue.get('id')}.{side}: {problem}",
                                   "Pistas de texto apontam para trechos literais do manuscrito congelado (RRL-04).",
                                   'Gravar text_anchor TEXT:<capítulo>:"trecho" no CANON_UPDATE da wave.'))
    return out


def check_final_canon(rt: dict) -> list[dict]:
    """Final: tudo realizado, exatamente uma evidência nova no último capítulo
    e nenhuma revisão de crença ali (SDD 7.5, UNC-08)."""
    canon = rt.get("canon") or {}
    bundle = rt["bundle"]
    count = _count(bundle)
    out = []
    unrealized = [row.get("id") for section in SECTION_EVENT_KIND for row in canon.get(section) or []
                  if row.get("status") != "REALIZED"]
    if unrealized:
        out.append(finding("FINAL_ROW_UNREALIZED", "HIGH", "WHOLE_BOOK", str(unrealized),
                           "No manuscrito congelado toda leitura está REALIZED; o que a prosa não sustentou volta à wave.",
                           "Realizar na prosa ou devolver a wave para revisão (runbook)."))
    last = next((c for c in _chapters(bundle) if c.get("number") == count), {})
    declared = set(last.get("final_evidence") or [])
    in_last = {row.get("id") for section in FINAL_EVIDENCE_SECTIONS for row in canon.get(section) or []
               if row.get("chapter") == count}
    last_events = [e for e in (rt.get("ledger") or {}).get("events") or [] if e.get("chapter") == count]
    evidence_events = [e.get("id") for e in last_events if FINAL_EVIDENCE_EVENT_KINDS & set(as_list(e.get("kind")))]
    if len(in_last) != 1 or in_last != declared or len(evidence_events) != 1:
        out.append(finding("FINAL_EVIDENCE_COUNT", "BLOCKER", count,
                           f"canon={sorted(in_last)} declarada={sorted(declared)} ledger={evidence_events}",
                           "O último capítulo entrega exatamente uma evidência nova (SDD 7.5).",
                           "Deixar só a evidência final no capítulo."))
    revising = [e.get("id") for e in last_events if as_list((e.get("beliefs") or {}).get("revises"))]
    if revising:
        out.append(finding("EXPLANATORY_CLOSURE", "BLOCKER", count, str(revising),
                           "O último capítulo não revisa crença: entrega evidência, não explicação (UNC-08).",
                           "Remover a revisão."))
    return out


# --- orquestração -------------------------------------------------------------

# --- canon visual da obra (Slice 3) --------------------------------------------

def _visual_trigger_resolves(token, bundle: dict, ledger_events: set | None) -> bool:
    match = VISUAL_TRIGGER_RE.match(str(token or ""))
    if not match:
        return False
    kind, value = match.groups()
    if kind == "SCENE":
        return any(s.get("id") == value for s in (bundle.get("scenes") or {}).get("scenes") or [])
    if kind == "TURN":
        return value.isdigit() and any(c.get("number") == int(value) and c.get("irreversible_turn")
                                       for c in _chapters(bundle))
    return ledger_events is not None and value in ledger_events


def _zones_intersect(a, b) -> bool:
    if not (isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)) and len(a) == 4 and len(b) == 4):
        return False
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _seed_events(bundle: dict) -> dict:
    seed = bundle.get("interpretive_seed") or {}
    return {row.get("event"): row.get("chapter")
            for section in SECTION_EVENT_KIND for row in seed.get(section) or [] if row.get("event")}


def _trigger_chapter(token, bundle: dict, ledger_events: dict | None) -> int | None:
    match = VISUAL_TRIGGER_RE.match(str(token or ""))
    if not match:
        return None
    kind, value = match.groups()
    if kind == "SCENE":
        for scene in (bundle.get("scenes") or {}).get("scenes") or []:
            if scene.get("id") == value and scene.get("chapters"):
                return min(scene["chapters"])
        return None
    if kind == "TURN":
        return int(value) if value.isdigit() else None
    return (ledger_events or {}).get(value)


def projected_decay_state(figure: dict, chapter: int, bundle: dict, ledger_events: dict | None) -> str:
    """Mesma regra de projeção do motor (NEXT_CHAPTER por padrão), sem importar o motor."""
    state = next((s.get("id") for s in figure.get("states") or [] if s.get("initial")), DECAY_STATES[0])
    edges = []
    for transition in figure.get("transitions") or []:
        trigger_chapter = _trigger_chapter(transition.get("trigger"), bundle, ledger_events)
        if trigger_chapter is None:
            continue
        same = transition.get("display_from") in ("SAME_CHAPTER", "AFTER_ANCHOR_IN_CHAPTER")
        edges.append((trigger_chapter if same else trigger_chapter + 1, transition.get("from"), transition.get("to")))
    for effective, source, target in sorted(edges):
        if source == state and effective <= chapter:
            state = target
    return state


def check_plates(canon: dict, bundle: dict, label: str, ledger_events: dict | None) -> list[dict]:
    out = []
    plates = [c for c in canon.get("compositions") or [] if c.get("illustration") is not None]
    slots = {slot: c.get("number") for c in _chapters(bundle) for slot in c.get("illustration_slots") or []}
    plate_chapters = {p.get("id"): p.get("chapter") for p in plates}
    missing = sorted(set(slots) - set(plate_chapters))
    extra = sorted(set(plate_chapters) - set(slots))
    moved = sorted(s for s in slots if s in plate_chapters and plate_chapters[s] != slots[s])
    if missing or extra or moved:
        out.append(finding("ILLUSTRATION_SLOT_MISMATCH", "HIGH", "WHOLE_BOOK",
                           f"{label}: sem prancha={missing} sem slot={extra} capítulo divergente={moved}",
                           "As pranchas do canon realizam exatamente os slots da arquitetura (28.3).",
                           "Alinhar compositions IL-* e illustration_slots."))
    if not plates:
        return out
    figure = next((e for e in canon.get("elements") or [] if e.get("id") == FIGURE_ID), None)
    act_of = _chapter_to_act(bundle)
    figure_plates_by_act: dict[int, int] = {}
    toward = doubles = absents = foreshadow = 0
    for plate in plates:
        pid, chapter = plate.get("id"), plate.get("chapter")
        block = plate.get("illustration") or {}
        ext = ((plate.get("ext") or {}).get("narciso")) or {}
        category = block.get("category")
        reflection = ext.get("reflection_state", "NONE")
        decay = ext.get("decay_state")
        act = act_of.get(chapter, 0)
        has_figure = FIGURE_ID in {r.get("element") for r in plate.get("elements") or []}
        where = f"{label}: {pid}"

        if category not in PLATE_CATEGORIES:
            out.append(finding("ILLUSTRATION_CATEGORY_INVALID", "HIGH", chapter, where,
                               f"Categorias: {', '.join(sorted(PLATE_CATEGORIES))} (SDD 16.2).", "Corrigir a categoria."))
        if category == "REFLECTION" and reflection == "NONE":
            out.append(finding("REFLECTION_PLATE_WITHOUT_REFLECTION", "HIGH", chapter, where,
                               "Prancha de reflexo declara um estado de reflexo.", "Declarar reflection_state."))
        if category == "CALLBACK" and not block.get("callback_of"):
            out.append(finding("CALLBACK_UNDECLARED", "HIGH", chapter, where,
                               "Prancha de retorno aponta para a original (callback_of).", "Declarar callback_of."))
        if block.get("callback_of"):
            changes = [c for c in as_list(block.get("callback_changes"))
                       if isinstance(c, dict) and str(c.get("what") or "").strip()]
            if not changes:
                out.append(finding("CALLBACK_WITHOUT_CHANGE", "MEDIUM", chapter, where,
                                   "Todo retorno declara ao menos uma diferença (MIR-03).", "Declarar callback_changes."))
            elif sum(1 for c in changes if c.get("impossible")) > 1:
                out.append(finding("CALLBACK_OVERLOADED", "MEDIUM", chapter, where,
                                   "No máximo uma diferença impossível por retorno (MIR-03).", "Reduzir."))
        if category == "DECAY" and (decay not in DECAY_STATES or DECAY_STATES.index(decay) < 2):
            out.append(finding("DECAY_PLATE_TOO_EARLY", "HIGH", chapter, where,
                               "Prancha de definhamento só a partir de D2 (SDD 16.2).", "Revisar categoria ou estado."))
        if has_figure and figure and isinstance(chapter, int):
            expected = projected_decay_state(figure, chapter, bundle, ledger_events)
            if decay != expected:
                out.append(finding("DECAY_STATE_MISMATCH", "HIGH", chapter, f"{where} {decay}≠{expected}",
                                   "O estado de Narciso na prancha é o projetado no capítulo (VNP-02).",
                                   "Corrigir decay_state."))
            figure_plates_by_act[act] = figure_plates_by_act.get(act, 0) + 1
        if reflection != "NONE":
            supported = as_list(ext.get("hypotheses_supported"))
            if len({h for h in supported if h in HYPOTHESIS_IDS}) < 2 or any(h not in HYPOTHESIS_IDS for h in supported):
                out.append(finding("SINGLE_HYPOTHESIS_EVIDENCE", "HIGH", chapter, f"{where} {supported}",
                                   "Prancha com reflexo sustenta ao menos duas hipóteses canônicas (UNC-01).",
                                   "Declarar hypotheses_supported."))
            if ext.get("reflection_face_visibility") == "FULL":
                out.append(finding("REFLECTION_FACE_RESOLVED", "HIGH", chapter, where,
                                   "O rosto do que olha de volta nunca aparece inteiro (UNC-09).", "Reduzir para PARTIAL ou NONE."))
        if category != "CALLBACK":
            if ext.get("symmetry") != PLATE_SYMMETRY_BY_ACT.get(act) or ext.get("crop") not in PLATE_CROPS_BY_ACT.get(act, set()):
                out.append(finding("ACT_GRAMMAR_VIOLATION", "MEDIUM", chapter,
                                   f"{where} symmetry={ext.get('symmetry')} crop={ext.get('crop')}",
                                   "Simetria e enquadramento seguem a gramática do ato (VNP-01).", "Ajustar a composição."))
        if ext.get("gaze") == "TOWARD_READER":
            toward += 1
            if isinstance(chapter, int) and chapter > GAZE_WITHDRAWAL_CHAPTER:
                out.append(finding("GAZE_AFTER_WITHDRAWAL", "MEDIUM", chapter, where,
                                   "No Ato III o livro para de olhar para o leitor (GAZE-01).", "Mudar o olhar."))
        doubles += reflection == "DOUBLE"
        absents += reflection == "ABSENT_REFLECTION"
        foreshadow += block.get("text_relation") == "FORESHADOW"
        spoiler = block.get("spoiler_level", "NONE")
        if spoiler not in PLATE_SPOILER_LEVELS:
            out.append(finding("INVALID_ENUM", "HIGH", chapter, f"{where} spoiler_level={spoiler}",
                               "Valores: NONE, LOW, MEDIUM, HIGH, CORE.", "Corrigir o valor."))
        elif PLATE_SPOILER_LEVELS.index(spoiler) >= 2 and block.get("placement") not in PLATE_AFTER_PLACEMENTS:
            out.append(finding("PLATE_SPOILER_BEFORE_ANCHOR", "HIGH", chapter, f"{where} placement={block.get('placement')}",
                               "Prancha com spoiler MEDIUM ou maior entra depois da âncora (AFTER/HINGE).",
                               "Mover para AFTER."))
        if ext.get("nudity") and category not in PLATE_NUDITY_CATEGORIES:
            out.append(finding("PLATE_NUDITY_CATEGORY", "HIGH", chapter, where,
                               "Nudez artística só em HERO, BODY_DETAIL ou REFLECTION (SDD 14.6).", "Remover a nudez."))
    if figure_plates_by_act.get(2, 0) > figure_plates_by_act.get(1, 0):
        out.append(finding("DECAY_BODY_OVEREXPOSED", "MEDIUM", "WHOLE_BOOK", f"{label}: {figure_plates_by_act}",
                           "No Ato III o corpo aparece menos que no Ato II (VNP-03).", "Trocar pranchas por vestígios."))
    if toward > MAX_TOWARD_READER_PLATES:
        out.append(finding("GAZE_OVERUSED", "MEDIUM", "WHOLE_BOOK", f"{label}: {toward}",
                           f"No máximo {MAX_TOWARD_READER_PLATES} pranchas olham para o leitor.", "Reduzir."))
    if doubles > MAX_DOUBLE_PLATES:
        out.append(finding("REFLECTION_DOUBLE_OVERUSED", "MEDIUM", "WHOLE_BOOK", f"{label}: {doubles}",
                           f"No máximo {MAX_DOUBLE_PLATES} pranchas DOUBLE.", "Reduzir."))
    if absents > MAX_ABSENT_PLATES:
        out.append(finding("REFLECTION_ABSENT_OVERUSED", "MEDIUM", "WHOLE_BOOK", f"{label}: {absents}",
                           f"No máximo {MAX_ABSENT_PLATES} prancha ABSENT_REFLECTION.", "Reduzir."))
    if foreshadow / len(plates) < MIN_FORESHADOW_RATIO:
        out.append(finding("FORESHADOW_UNDERUSED", "LOW", "WHOLE_BOOK", f"{label}: {foreshadow}/{len(plates)}",
                           f"Ao menos {MIN_FORESHADOW_RATIO:.0%} das pranchas antecipam (TIR-06).", "Converter pranchas."))
    return out


def check_illustration_artifacts(rt: dict) -> list[dict]:
    """Modo `illustrations`: briefs sem nome de hipótese e QA de continuidade
    que confere a anomalia de reflexo declarada (SDD 16.6, 25.3)."""
    out = []
    lexicons = _lexicons(rt["bundle"])
    canon = rt.get("visual_canon") or {}
    plates = {c.get("id"): c for c in canon.get("compositions") or [] if c.get("illustration") is not None}
    for pid, artifact in sorted((rt.get("illustration_artifacts") or {}).items()):
        brief = artifact.get("brief")
        if brief is not None:
            hits = lexicon_hits(brief, lexicons.get("hypothesis_names")) + lexicon_hits(brief, lexicons.get("twin"))
            if hits:
                out.append(finding("PROMPT_LEAKS_HYPOTHESIS", "HIGH", "WHOLE_BOOK", f"{pid}: {', '.join(sorted(set(hits)))}",
                                   "O brief de imagem nunca sabe o que olha de volta (NO_HIDDEN_ANSWER).",
                                   "Reescrever o brief sem nome de hipótese."))
        if not artifact.get("approved"):
            continue
        plate = plates.get(pid)
        if plate is None:
            out.append(finding("ILLUSTRATION_SLOT_MISMATCH", "HIGH", "WHOLE_BOOK", pid,
                               "Imagem aprovada sem prancha no canon visual.", "Declarar a prancha ou remover a imagem."))
            continue
        ext = ((plate.get("ext") or {}).get("narciso")) or {}
        needs_qa = ext.get("reflection_state", "NONE") != "NONE" or FIGURE_ID in {
            r.get("element") for r in plate.get("elements") or []}
        if needs_qa and QA_ANOMALY_TOKEN not in normalize(artifact.get("continuity_qa") or ""):
            out.append(finding("REFLECTION_QA_SKIPPED", "HIGH", plate.get("chapter"), pid,
                               "CONTINUITY_QA precisa conferir a anomalia declarada contra a observada (SDD 25.3).",
                               f"Registrar em {ILLUSTRATION_WORK_DIR}/{pid}/CONTINUITY_QA.md a checagem de anomalia."))
    return out


def check_visual(canon, bundle: dict, source: str, ledger_events: set | None) -> list[dict]:
    label = "seeds/VISUAL_NARRATIVE_CANON.seed.yaml" if source == "seed" else VISUAL_CANON_FILE
    if not canon:
        return [finding("VISUAL_CANON_MISSING", "HIGH", "WHOLE_BOOK", label,
                        "O canon visual da obra não existe (T043 / semente).",
                        "Criar o canon a partir de seeds/VISUAL_NARRATIVE_CANON.seed.yaml.")]
    out = []
    lexicons = _lexicons(bundle)
    book_dna = canon.get("book_dna") or {}
    palette = book_dna.get("palette") or {}

    # prata só como acabamento (OQ-N6)
    for role, value in palette.items():
        if any(token in normalize(json.dumps(value, ensure_ascii=False)) for token in SILVER_TOKENS):
            out.append(finding("SILVER_AS_PALETTE_ROLE", "HIGH", "WHOLE_BOOK", f"{label}: palette.{role}",
                               "Prata não é papel de cor; existe só como acabamento (OQ-N6).",
                               "Remover a prata da paleta e usar finish_intents SILVER_MIRROR."))
    metal = palette.get("METAL")
    if not isinstance(metal, dict) or metal.get("material") != BOOK_METAL_MATERIAL:
        out.append(finding("METAL_MATERIAL_MISMATCH", "MEDIUM", "WHOLE_BOOK", f"{label}: palette.METAL={metal}",
                           f"O metal do livro é {BOOK_METAL_MATERIAL}.", "Corrigir palette.METAL.material."))
    silver = [fi for fi in canon.get("finish_intents") or [] if fi.get("semantic_material") == SILVER_FINISH_MATERIAL]
    if not silver:
        out.append(finding("SILVER_FINISH_MISSING", "MEDIUM", "WHOLE_BOOK", label,
                           "A prata do livro vive num acabamento SILVER_MIRROR (OQ-N6).",
                           "Declarar o acabamento do espelho."))
    compositions_by_id = {c.get("id"): c for c in canon.get("compositions") or []}
    for fi in silver:
        if fi.get("meaning_element") != SILVER_FINISH_ELEMENT or fi.get("cost_class") != SILVER_FINISH_COST:
            out.append(finding("SILVER_FINISH_MISPLACED", "HIGH", "WHOLE_BOOK", f"{label}: {fi.get('id')}",
                               f"Prata só ligada a {SILVER_FINISH_ELEMENT} e só em {SILVER_FINISH_COST}.",
                               "Corrigir meaning_element e cost_class."))
        trap = ((fi.get("ext") or {}).get("narciso")) or {}
        ratio = trap.get("area_ratio_max")
        host = compositions_by_id.get((fi.get("target") or {}).get("composition")) or {}
        problems = []
        if not isinstance(ratio, (int, float)) or ratio > MIRROR_AREA_MAX_RATIO:
            problems.append(f"area_ratio_max={ratio}")
        if trap.get("contrast") != MIRROR_CONTRAST:
            problems.append(f"contrast={trap.get('contrast')}")
        if (fi.get("approval") or {}).get("policy") != "REQUIRE_APPROVAL":
            problems.append("sem aprovação humana")
        if host.get("reading_layer") != "HIDDEN_TRUTH":
            problems.append(f"composição {host.get('id')} fora da camada escondida")
        if fi.get("preferred_effect") not in MIRROR_EFFECTS:
            problems.append(f"preferred_effect={fi.get('preferred_effect')}")
        if problems:
            out.append(finding("MIRROR_GIMMICK", "HIGH", "WHOLE_BOOK", f"{label}: {fi.get('id')} {problems}",
                               f"Espelho físico: placa espelhada, ≤ {MIRROR_AREA_MAX_RATIO:.0%} da face, contraste "
                               "baixo, só na capa nua e com aprovação humana (TRAP-01).",
                               "Ajustar o acabamento."))

    # elementos obrigatórios e figura
    elements = {e.get("id"): e for e in canon.get("elements") or []}
    for eid in [FIGURE_ID, SIGIL_ID, *REQUIRED_SYMBOL_IDS]:
        if eid not in elements:
            out.append(finding("VISUAL_ELEMENT_MISSING", "HIGH", "WHOLE_BOOK", f"{label}: {eid}",
                               "Elemento visual obrigatório da obra ausente (SDD 14, 15, 17).", "Declarar o elemento."))
    figure = elements.get(FIGURE_ID)
    if figure:
        if figure.get("class") != "FIGURE" or not figure.get("identity_ref"):
            out.append(finding("FIGURE_WITHOUT_IDENTITY_REF", "HIGH", "WHOLE_BOOK", f"{label}: {FIGURE_ID}",
                               "A figura recorrente aponta para o seu canon facial (FIG-01).",
                               "Declarar class FIGURE e identity_ref."))
        states = figure.get("states") or []
        if [s.get("id") for s in states] != DECAY_STATES or [s.get("id") for s in states if s.get("initial")] != DECAY_STATES[:1]:
            out.append(finding("DECAY_TIMELINE_INVALID", "HIGH", "WHOLE_BOOK", f"{label}: {[s.get('id') for s in states]}",
                               f"Estados de declínio canônicos: {' → '.join(DECAY_STATES)} (SDD 14.7).",
                               "Corrigir os estados."))
        triggers = {t.get("to"): t.get("trigger") for t in figure.get("transitions") or []}
        for state, expected in DECAY_TRIGGERS.items():
            if triggers.get(state) != expected:
                out.append(finding("DECAY_TRIGGER_MISMATCH", "HIGH", "WHOLE_BOOK",
                                   f"{label}: {state} trigger={triggers.get(state)} esperado={expected}",
                                   "O declínio de Narciso segue os gatilhos canônicos (SDD 14.7).",
                                   "Corrigir o gatilho."))
        figure_text = " ".join([str(figure.get("meaning") or "")]
                               + [f"{s.get('meaning') or ''} {s.get('visual_description') or ''}" for s in states])
        hits = lexicon_hits(figure_text, lexicons.get("decay_glamour"))
        if hits:
            out.append(finding("DECAY_GLAMORIZED", "BLOCKER", "WHOLE_BOOK", f"{label}: {', '.join(hits)}",
                               "Definhamento nunca é ideal de beleza corporal (IR-N08).", "Descrever perda, não magreza."))
        hits = lexicon_hits(figure_text, lexicons.get("youth_coding"))
        if hits:
            out.append(finding("YOUTH_CODING_IN_ADULT_CONTEXT", "BLOCKER", "WHOLE_BOOK", f"{label}: {', '.join(hits)}",
                               "Narciso é adulto inequívoco em toda imagem (IR-N05).", "Remover os termos."))

    # estados, significado e gatilhos (SYMR-02, SYMR-05)
    for eid, element in elements.items():
        previous = None
        for state in element.get("states") or []:
            meaning = str(state.get("meaning") or "").strip()
            if not meaning or (previous is not None and normalize(meaning) == normalize(previous)):
                out.append(finding("SYMBOL_STATE_WITHOUT_NEW_MEANING", "MEDIUM", "WHOLE_BOOK",
                                   f"{label}: {eid}.{state.get('id')}",
                                   "Todo estado declara um significado novo (SYMR-05).", "Declarar meaning próprio."))
            previous = meaning
        for transition in element.get("transitions") or []:
            if not _visual_trigger_resolves(transition.get("trigger"), bundle, ledger_events):
                out.append(finding("VISUAL_TRIGGER_UNRESOLVED", "HIGH", "WHOLE_BOOK",
                                   f"{label}: {eid} {transition.get('from')}→{transition.get('to')} trigger={transition.get('trigger')}",
                                   "Gatilho visual resolve contra cena protegida, virada de capítulo ou evento do ledger.",
                                   "Usar SCENE:, TURN: ou LEDGER:EV- existente; nunca número nu."))
    for eid in SINGLE_COUNT_SYMBOLS:
        if eid in elements and (elements[eid].get("count") or 1) != 1:
            out.append(finding("SYMBOL_COUNT_FIXED", "HIGH", "WHOLE_BOOK", f"{label}: {eid} count={elements[eid].get('count')}",
                               "A flor e a gota aparecem uma vez por composição (SYMR-06).", "Definir count: 1."))

    veto_ids = {v.get("id") for v in canon.get("vetoes") or []}
    missing_vetoes = [v for v in REQUIRED_VETO_IDS if v not in veto_ids]
    if missing_vetoes:
        out.append(finding("VETO_MISSING", "HIGH", "WHOLE_BOOK", f"{label}: {missing_vetoes}",
                           "Vetos visuais canônicos da obra ausentes (SDD 13.7).", "Restaurar os vetos."))
    if lexicon_hits(yaml.safe_dump(canon, allow_unicode=True), lexicons.get("twin")):
        out.append(finding("TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER", "WHOLE_BOOK", label,
                           "Não existe hipótese de gêmeo (OQ-N2).", "Remover o termo."))

    # capa por fragmento do rosto (OQ-N1, SDD 23.2.1)
    overrides = [o for o in book_dna.get("role_overrides") or [] if o.get("key") == COVER_OVERRIDE_KEY]
    override = overrides[0] if overrides else {}
    if override.get("value") is not False or not str(override.get("override_reason") or "").strip() or not override.get("approval"):
        out.append(finding("COVER_OVERRIDE_MISSING", "HIGH", "WHOLE_BOOK", f"{label}: {COVER_OVERRIDE_KEY}",
                           "Narciso na capa exige override do default da autora com razão e aprovação (OQ-N1).",
                           "Declarar o role_override."))
    compositions = canon.get("compositions") or []
    front = next((c for c in compositions if c.get("surface") == "FRONT_COVER"
                  and c.get("reading_layer") == "OUTER_TRUTH"), None)
    front_refs = {r.get("element"): r for r in (front or {}).get("elements") or []}
    if front is None or (front_refs.get(FIGURE_ID) or {}).get("prominence") != "DOMINANT":
        out.append(finding("COVER_FIGURE_MISSING", "HIGH", "WHOLE_BOOK", label,
                           "A capa pública tem Narciso por fragmento como elemento dominante (OQ-N1).",
                           "Declarar FIG-NARCISO DOMINANT em FRONT_COVER/OUTER_TRUTH."))
    if front is not None:
        fragment = (((front.get("ext") or {}).get("narciso")) or {}).get("face_fragment") or {}
        ratio = fragment.get("visible_ratio_max")
        if not isinstance(ratio, (int, float)) or ratio > COVER_MAX_VISIBLE_RATIO or not fragment.get("hidden_by"):
            out.append(finding("COVER_FACE_FULLY_REVEALED", "HIGH", "WHOLE_BOOK", f"{label}: {fragment}",
                               f"Só parte do rosto: até {COVER_MAX_VISIBLE_RATIO:.0%} visível e algo ocultando (COV-01).",
                               "Ajustar face_fragment."))
        if (front.get("approval") or {}).get("policy") != "REQUIRE_APPROVAL":
            out.append(finding("COVER_APPROVAL_POLICY", "HIGH", "WHOLE_BOOK", f"{label}: {front.get('id')}",
                               "A capa exige aprovação humana com hash.", "Definir approval.policy: REQUIRE_APPROVAL."))
        for typography in front.get("typography") or []:
            if _zones_intersect(typography.get("zone"), fragment.get("eyes_zone")):
                out.append(finding("ZONE_COLLISION_FOCAL", "MEDIUM", "WHOLE_BOOK", f"{label}: {typography.get('role')}",
                                   "A tipografia não cobre os olhos (COV-08).", "Mover a zona tipográfica."))
    for composition in compositions:
        ext = ((composition.get("ext") or {}).get("narciso")) or {}
        reflection = ext.get("reflection_state", "NONE")
        anomalies = as_list(ext.get("reflection_anomaly"))
        if reflection not in REFLECTION_STATES or any(a not in REFLECTION_ANOMALIES for a in anomalies):
            out.append(finding("INVALID_ENUM", "HIGH", "WHOLE_BOOK", f"{label}: {composition.get('id')}",
                               "reflection_state ou reflection_anomaly inválidos (SDD 14.8).", "Corrigir o valor."))
        if reflection == "ANOMALOUS_MIRROR" and len(anomalies) != 1:
            out.append(finding("REFLECTION_OVERLOADED", "HIGH", "WHOLE_BOOK", f"{label}: {composition.get('id')} {anomalies}",
                               "Reflexo anômalo declara exatamente uma anomalia (REF-03).", "Declarar uma anomalia."))
        public = composition.get("surface") in PUBLIC_SURFACES and composition.get("reading_layer") != "HIDDEN_TRUTH"
        if not public:
            continue
        if reflection != "NONE":
            out.append(finding("COVER_REFLECTION_SPOILER", "HIGH", "WHOLE_BOOK", f"{label}: {composition.get('id')}",
                               "Superfície pública nunca mostra o que olha de volta (COV-06).",
                               "Definir reflection_state: NONE."))
        if FIGURE_ID in {r.get("element") for r in composition.get("elements") or []} \
                and ext.get("decay_state") != PUBLIC_DECAY_STATE:
            out.append(finding("PUBLIC_DECAY_EXPOSURE", "HIGH", "WHOLE_BOOK", f"{label}: {composition.get('id')}",
                               "Superfície pública só mostra Narciso em D0 (VNP-04).", "Definir decay_state: D0_PRISTINE."))
        if ext.get("nudity"):
            out.append(finding("SURFACE_NUDITY", "HIGH", "WHOLE_BOOK", f"{label}: {composition.get('id')}",
                               "Nenhuma nudez em superfície pública (SDD 14.6).", "Remover a nudez."))
    out.extend(check_plates(canon, bundle, label, ledger_events))
    return out


def check_visual_documents(bundle: dict) -> list[dict]:
    out = []
    lexicons = _lexicons(bundle)
    face = bundle.get("face_canon_seed")
    if face is None:
        out.append(finding("FACE_CANON_SEED_MISSING", "HIGH", "WHOLE_BOOK", FACE_CANON_SEED,
                           "Semente do canon facial ausente.", "Criar a semente a partir do template."))
    else:
        missing = [term for term in FACE_CANON_REQUIRED_TERMS if normalize(term) not in normalize(face)]
        if missing:
            out.append(finding("FACE_CANON_ANCHOR_MISSING", "HIGH", "WHOLE_BOOK", f"{FACE_CANON_SEED}: {missing}",
                               "O canon facial declara código e âncoras de identidade de Narciso (SDD 14.1–14.3).",
                               "Restaurar as âncoras."))
    bible = bundle.get("visual_bible_seed")
    if bible is None:
        out.append(finding("VISUAL_BIBLE_SEED_MISSING", "HIGH", "WHOLE_BOOK", VISUAL_BIBLE_SEED,
                           "Semente da bíblia visual de personagem ausente.", "Criar a semente."))
    else:
        missing = [section for section in VISUAL_BIBLE_REQUIRED_SECTIONS if section not in bible]
        if missing:
            out.append(finding("VISUAL_BIBLE_SECTION_MISSING", "MEDIUM", "WHOLE_BOOK", f"{VISUAL_BIBLE_SEED}: {missing}",
                               "Seções obrigatórias da bíblia visual (SDD 14.6–14.9).", "Restaurar as seções."))
    for name, text in ((FACE_CANON_SEED, face or ""), (VISUAL_BIBLE_SEED, bible or "")):
        if lexicon_hits(text, lexicons.get("twin")):
            out.append(finding("TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER", "WHOLE_BOOK", name,
                               "Não existe hipótese de gêmeo (OQ-N2).", "Remover o termo."))
    return out


def check_mirror_manifestation(bundle: dict) -> list[dict]:
    """SDD 18.4–18.5: plano por edição, Kindle omitindo o que 18.5 omite,
    MIR-02, spread central único e coerência com o canon visual."""
    doc = bundle.get("mirror_manifestation")
    if not doc:
        return [finding("MIRROR_MANIFESTATION_MISSING", "HIGH", "WHOLE_BOOK", MIRROR_MANIFESTATION_FILE,
                        "Plano de manifestação por edição ausente (SDD 18.5).", "Criar o plano.")]
    out = []
    techniques = {t.get("id"): t for t in doc.get("techniques") or []}
    missing = [t for t in REQUIRED_MIRROR_TECHNIQUES if t not in techniques]
    if missing:
        out.append(finding("MIRROR_MANIFESTATION_INVALID", "HIGH", "WHOLE_BOOK", f"técnicas ausentes: {missing}",
                           "O plano cobre toda técnica da tabela 18.5.", "Declarar as técnicas."))
    for tid, technique in techniques.items():
        editions = technique.get("editions") or {}
        invalid = [f"{k}={v}" for k, v in editions.items() if k not in EDITION_TARGET_IDS or v not in MANIFEST_VALUES]
        absent = [k for k in EDITION_TARGET_IDS if k not in editions]
        if invalid or absent:
            out.append(finding("MIRROR_MANIFESTATION_INVALID", "HIGH", "WHOLE_BOOK",
                               f"{tid}: inválidos={invalid} ausentes={absent}",
                               f"Cada técnica declara as quatro edições com {sorted(MANIFEST_VALUES)}.", "Corrigir."))
        required = KINDLE_REQUIRED.get(tid)
        if required and editions.get("kindle_ebook") != required:
            out.append(finding("KINDLE_OMISSION_VIOLATED", "HIGH", "WHOLE_BOOK",
                               f"{tid}: kindle_ebook={editions.get('kindle_ebook')} esperado={required}",
                               "O Kindle refluível omite ou sequencia o que 18.5 manda.", f"Usar {required}."))
        if technique.get("requires_physical_mirror"):
            leaks = [k for k in EDITION_TARGET_IDS if k != PHYSICAL_MIRROR_EDITION and editions.get(k) != "OMIT"]
            if technique.get("surface") != PHYSICAL_MIRROR_SURFACE or leaks:
                out.append(finding("MIRROR_REQUIRED_TO_READ", "HIGH", "WHOLE_BOOK",
                                   f"{tid}: surface={technique.get('surface')} fora do collector={leaks}",
                                   "Nenhuma página exige espelho físico, exceto um INSERT do collector (MIR-02).",
                                   "Restringir a INSERT só no collector."))

    seed = bundle.get("visual_seed") or {}
    plates = [c for c in seed.get("compositions") or [] if c.get("illustration") is not None]
    spread = doc.get("spread") or {}
    spreads = [(p.get("id"), p.get("chapter")) for p in plates
               if (p.get("illustration") or {}).get("pair_with") == "SPREAD"]
    if spreads != [(spread.get("composition"), spread.get("chapter"))]:
        out.append(finding("SPREAD_MISPLACED", "HIGH", "WHOLE_BOOK",
                           f"plano={spread} canon={spreads}",
                           "Existe exatamente um spread central, no capítulo declarado (18.1).",
                           "Alinhar pair_with: SPREAD no canon ao plano."))
    declared_pairs = {tuple(p) for p in doc.get("callback_pairs") or []}
    canon_pairs = {((p.get("illustration") or {}).get("callback_of"), p.get("id")) for p in plates
                   if (p.get("illustration") or {}).get("callback_of")}
    if declared_pairs != canon_pairs:
        out.append(finding("CALLBACK_PAIRS_MISMATCH", "MEDIUM", "WHOLE_BOOK",
                           f"só no plano={sorted(declared_pairs - canon_pairs)} só no canon={sorted(canon_pairs - declared_pairs)}",
                           "Os pares de retorno do plano são os do canon (18.1).", "Alinhar."))

    act_of = _chapter_to_act(bundle)
    assets = seed.get("display_assets") or []
    echo = sorted(c for a in assets if a.get("kind") == "TITLE_ECHO" for c in a.get("chapters") or [])
    expected_echo = sorted(c.get("number") for c in _chapters(bundle)
                           if act_of.get(c.get("number")) == TITLE_ECHO_ACT and c.get("reflection_presence") == "PRESENT")
    if echo != expected_echo:
        out.append(finding("TITLE_ECHO_MISMATCH", "MEDIUM", "WHOLE_BOOK", f"canon={echo} esperado={expected_echo}",
                           "Eco do título só nos capítulos do Ato II com reflexo presente (18.3).", "Alinhar."))
    acts: dict[int, list[int]] = {}
    for number, act in act_of.items():
        if number:
            acts.setdefault(act, []).append(number)
    ornaments = sorted(sorted(a.get("chapters") or []) for a in assets if a.get("kind") == "ORNAMENT")
    if ornaments != sorted(sorted(chapters) for chapters in acts.values()):
        out.append(finding("ORNAMENT_ACT_MISMATCH", "MEDIUM", "WHOLE_BOOK", f"ornamentos={ornaments}",
                           "Um ornamento por ato, cobrindo o ato inteiro (18.3).", "Alinhar."))
    return out


def check_production_documents(bundle: dict) -> list[dict]:
    """Slice 7: semente de PRINT_SPEC honesta, modelo de perfil de gráfica que
    nunca confirma nada e roteiro de pesquisa humana (OQ-N8)."""
    out = []
    spec_doc = bundle.get("print_spec_seed")
    if not spec_doc:
        out.append(finding("PRINT_SPEC_SEED_MISSING", "HIGH", "WHOLE_BOOK", PRINT_SPEC_SEED,
                           "A obra declara a especificação de impressão por alvo.", "Criar a semente."))
    else:
        spec = spec_doc.get("spec") or {}
        for target in PRINT_TARGETS:
            entry = spec.get(target)
            if not isinstance(entry, dict) or (entry.get("interior") or {}).get("ink") not in INTERIOR_INKS:
                out.append(finding("PRINT_SPEC_INVALID", "HIGH", "WHOLE_BOOK", f"{PRINT_SPEC_SEED}: {target}",
                                   f"Cada alvo impresso declara interior.ink em {sorted(INTERIOR_INKS)}.",
                                   "Completar o alvo."))
                continue
            if entry.get("page_count") is not None:
                out.append(finding("PAGE_COUNT_INVENTED", "HIGH", "WHOLE_BOOK",
                                   f"{PRINT_SPEC_SEED}: {target}.page_count={entry.get('page_count')}",
                                   "page_count vem do DOCX medido (T703/T707), nunca da semente.",
                                   "Deixar page_count: null."))
    template = bundle.get("printer_profile_template")
    if template is None:
        out.append(finding("PRINTER_RESEARCH_MISSING", "MEDIUM", "WHOLE_BOOK", PRINTER_PROFILE_TEMPLATE,
                           "Modelo do perfil de gráfica ausente.", "Criar o modelo."))
    elif as_list(template.get("confirmed_effects")) or any(
            (template.get("production") or {}).get(key) is True for key in PRODUCTION_KEYS):
        out.append(finding("PRINTER_EFFECT_UNEVIDENCED", "HIGH", "WHOLE_BOOK", PRINTER_PROFILE_TEMPLATE,
                           "O modelo nunca confirma efeito nem produção: só uma gráfica real, com evidência (OQ-N8).",
                           "Esvaziar confirmed_effects e production."))
    research = bundle.get("printer_research")
    missing = [s for s in PRINTER_RESEARCH_SECTIONS if s not in (research or "")]
    if research is None or missing:
        out.append(finding("PRINTER_RESEARCH_MISSING", "MEDIUM", "WHOLE_BOOK", f"{PRINTER_RESEARCH_DOC}: {missing}",
                           "Roteiro de pesquisa de gráfica para a decisão humana do collector.", "Completar o roteiro."))
    return out


def _edition_targets(bundle: dict) -> list[str]:
    sp = (bundle.get("spec") or {}).get("spec") or {}
    visual = (sp.get("features") or {}).get("visual_narrative") or sp.get("visual_narrative") or {}
    return list(visual.get("edition_targets") or EDITION_TARGET_IDS)


def check_edition(rt: dict) -> list[dict]:
    """Modo `edition` (GATE_KDP, GATE_MEDIA_ASSETS): planos dos alvos sem
    efeito não físico, sem camada escondida fora do collector, perfil de
    gráfica com evidência e textos de loja honestos (TRAP-02, TRAP-05, 21.4, SOC-05)."""
    out = []
    bundle = rt["bundle"]
    canon = rt.get("visual_canon") or {}
    if not rt.get("has_kdp_requirements"):
        out.append(finding("KDP_REQUIREMENTS_UNVERIFIED", "HIGH", "WHOLE_BOOK", KDP_REQUIREMENTS_FILE,
                           "T699 revalida as capacidades do KDP antes de qualquer plano de edição.", "Executar T699."))
    capabilities = ((rt.get("capabilities") or {}).get("targets")) or {}
    profile = rt.get("printer_profile") or {}
    confirmed = set(as_list(profile.get("confirmed_effects")))
    silver_ids = {fi.get("id") for fi in canon.get("finish_intents") or []
                  if fi.get("semantic_material") == SILVER_FINISH_MATERIAL}
    for target in _edition_targets(bundle):
        plan = (rt.get("edition_plans") or {}).get(target)
        if plan is None:
            out.append(finding("EDITION_PLAN_MISSING", "HIGH", "WHOLE_BOOK", EDITION_PLAN_TEMPLATE.format(target=target),
                               "Todo alvo declarado tem EDITION_PLAN projetado (T698).", "Executar T698."))
            continue
        for entry in plan.get("compositions") or []:
            if (entry.get("reading_layer") == "HIDDEN_TRUTH" and entry.get("status") == "INCLUDED"
                    and target != COLLECTOR_TARGET):
                out.append(finding("HIDDEN_TRUTH_EXPOSED", "BLOCKER", "WHOLE_BOOK", f"{target}: {entry.get('composition')}",
                                   "A camada escondida nunca aparece em alvo KDP (TRAP-02).", "Omitir a composição."))
        effects = (capabilities.get(target) or {}).get("effects") or {}
        for entry in plan.get("finish_intents") or []:
            if entry.get("level") != "PHYSICAL":
                continue
            effect, finish_id = entry.get("effect"), entry.get("finish_intent")
            where = f"{target}: {finish_id} {effect}"
            if (effect in MIRROR_EFFECTS or finish_id in silver_ids) and target != COLLECTOR_TARGET:
                out.append(finding("MIRROR_OUTSIDE_COLLECTOR", "BLOCKER", "WHOLE_BOOK", where,
                                   "Espelho físico só existe na capa nua do collector (TRAP-02, TRAP-04).",
                                   "Refazer o plano com o resolver."))
            level = effects.get(effect)
            if level == "VENDOR_DEPENDENT":
                if effect not in confirmed:
                    out.append(finding("PRINTER_EFFECT_UNEVIDENCED", "HIGH", "WHOLE_BOOK", where,
                                       "Efeito de gráfica só é físico quando o perfil o confirma.",
                                       "Confirmar no PRINTER_PROFILE ou refazer o plano."))
            elif level != "PHYSICAL":
                out.append(finding("FINISH_NOT_PHYSICAL", "BLOCKER", "WHOLE_BOOK", f"{where} capacidade={level}",
                                   "O plano promete fabricação que o alvo não tem (KDP honesto).",
                                   "Refazer o plano com o resolver."))
    evidence = profile.get("evidence") or {}
    for effect in sorted(confirmed):
        record = evidence.get(effect) or {}
        if any(not record.get(field) for field in PRINTER_EVIDENCE_FIELDS) or record.get("sample_approved") is not True:
            out.append(finding("PRINTER_EFFECT_UNEVIDENCED", "HIGH", "WHOLE_BOOK", f"{PRINTER_PROFILE_FILE}: {effect}",
                               "Efeito confirmado registra gráfica, orçamento, data e prova aprovada.",
                               "Completar evidence ou retirar o efeito."))
    production = profile.get("production") or {}
    if any(production.get(key) is True for key in PRODUCTION_KEYS) and not str(production.get("decided_by") or "").strip():
        out.append(finding("PRINTER_EFFECT_UNEVIDENCED", "HIGH", "WHOLE_BOOK", f"{PRINTER_PROFILE_FILE}: production",
                           "Numeração, assinatura e tiragem limitada são decisão humana registrada (OQ-N8).",
                           "Registrar decided_by ou desligar."))
    lexicons = _lexicons(bundle)
    clue_phrases = []
    for clue in (rt.get("canon") or {}).get("reread_clues") or []:
        clue_phrases += [p for p in (clue.get("first_read"), clue.get("second_read")) if p]
        for side in ("clue", "trigger"):
            match = TEXT_ANCHOR_RE.match(str((clue.get(side) or {}).get("text_anchor") or ""))
            if match:
                clue_phrases.append(match.group(2))
    for rel, text in sorted((rt.get("marketing") or {}).items()):
        hits = lexicon_hits(text, lexicons.get("finish_promise"))
        if hits:
            out.append(finding("FINISH_PROMISE_MISMATCH", "HIGH", "WHOLE_BOOK", f"{rel}: {', '.join(sorted(set(hits)))}",
                               "Texto de loja e redes nunca promete espelho, numeração, assinatura ou acabamento "
                               "que os alvos KDP não fabricam (TRAP-05, SDD 21.4).", "Remover a promessa."))
        exposed = [p for p in clue_phrases if normalize(p) in normalize(text)]
        if exposed:
            out.append(finding("REREAD_CLUE_EXPOSED", "MEDIUM", "WHOLE_BOOK", f"{rel}: {exposed}",
                               "Frase pública nunca é pista de releitura (SOC-05).", "Trocar a frase."))
    return out


PACKAGE_CHECKS = [
    check_structure,
    check_mirror_and_chorus,
    check_desire_curve,
    check_adult_content,
    check_roster,
    check_rules_and_scenes,
    check_myth,
    check_lexicons,
    check_evidence_and_slots,
    check_text_hygiene,
]


def _sorted(findings: list[dict]) -> list[dict]:
    return sorted(findings, key=lambda f: (-SEVERITY_ORDER.index(f["severity"]), str(f["chapter"]), f["category"]))


def check_package(bundle: dict) -> list[dict]:
    snapshot = copy.deepcopy(bundle)
    findings: list[dict] = []
    for check in PACKAGE_CHECKS:
        findings.extend(check(snapshot))
    findings.extend(check_interpretive(snapshot.get("interpretive_seed"), snapshot, source="seed"))
    findings.extend(check_visual(snapshot.get("visual_seed"), snapshot, "seed", _seed_events(snapshot)))
    findings.extend(check_visual_documents(snapshot))
    findings.extend(check_mirror_manifestation(snapshot))
    findings.extend(check_production_documents(snapshot))
    return _sorted(findings)


def validate_runtime(rt: dict, mode: str, through_chapter: int | None = None) -> list[dict]:
    rt = copy.deepcopy(rt)
    bundle = rt["bundle"]
    findings = list(check_package(bundle))
    findings.extend(check_interpretive(rt.get("canon"), bundle, source="canon"))
    findings.extend(check_ledger_crossref(rt.get("canon"), rt.get("ledger"), bundle))
    findings.extend(check_registry(rt.get("registry")))
    if mode in ("plan", "visual"):
        findings.extend(check_plan_artifacts(rt))
    if mode in ("visual", "wave", "final", "illustrations", "edition") or rt.get("visual_canon") is not None:
        ledger_events = {e.get("id"): e.get("chapter") for e in (rt.get("ledger") or {}).get("events") or []}
        findings.extend(check_visual(rt.get("visual_canon"), bundle, "canon", ledger_events))
    if mode == "illustrations":
        findings.extend(check_illustration_artifacts(rt))
    if mode == "edition":
        findings.extend(check_edition(rt))
    if mode in ("wave", "final"):
        findings.extend(check_immutability(rt.get("canon"), rt))
    if mode == "wave":
        texts = {}
        for number in range(1, (through_chapter or 0) + 1):
            if number in rt.get("raw_chapters", {}):
                texts[number] = rt["raw_chapters"][number]
            else:
                findings.append(finding("MANUSCRIPT_CHAPTER_MISSING", "HIGH", number,
                                        f"manuscript/raw/chapter_{number:02d}.md",
                                        "Capítulo da wave sem prosa bruta.", "Escrever ou mesclar o capítulo."))
        findings.extend(check_prose(texts, bundle))
    if mode == "final":
        findings.extend(check_final_manuscript(rt))
        findings.extend(check_final_canon(rt))
    return _sorted(findings)


def write_snapshot(runtime: Path, name: str) -> Path:
    if not SNAPSHOT_NAME_RE.match(name):
        raise ValueError(f"nome de snapshot inválido: {name}")
    source = Path(runtime) / CANON_FILE
    if not source.is_file():
        raise FileNotFoundError(str(source))
    target = Path(runtime) / SNAPSHOT_DIR / f"{SNAPSHOT_PREFIX}.{name}.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(load_yaml(source), allow_unicode=True, sort_keys=False, width=120),
                      encoding="utf-8")
    return target


# --- CLI ----------------------------------------------------------------------

def summarize(bundle: dict) -> str:
    chapters = _chapters(bundle)
    slots = sum(len(c.get("illustration_slots") or []) for c in chapters)
    dsr = sum(1 for c in chapters if (c.get("adult_content") or {}).get("kind") == "SOLO_COMPULSION")
    return (f"chapters={len(chapters)} myth={len((bundle.get('myth') or {}).get('elements') or [])} "
            f"rules={len((bundle.get('rules') or {}).get('rules') or [])} "
            f"scenes={len((bundle.get('scenes') or {}).get('scenes') or [])} "
            f"dsr={dsr} illustration_slots={slots}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validador determinístico da obra NARCISO.")
    location = parser.add_mutually_exclusive_group()
    location.add_argument("--book", type=Path, help="Diretório do pacote (padrão: o pacote deste script).")
    location.add_argument("--runtime", type=Path, help="Runtime composto; o pacote fica em <runtime>/book.")
    parser.add_argument("--mode", default="package",
                        choices=["package", "plan", "visual", "wave", "final", "illustrations", "edition"])
    parser.add_argument("--through-chapter", type=int, help="Último capítulo da wave (modo wave).")
    parser.add_argument("--baseline", help="Snapshot anterior, relativo ao runtime (modos wave e final).")
    parser.add_argument("--snapshot-as", help="Grava canon/snapshots/NARCISO_INTERPRETIVE_CANON.<NOME>.yaml e sai.")
    parser.add_argument("--json", action="store_true", help="Emite os achados em JSON.")
    args = parser.parse_args()

    if args.snapshot_as:
        if not args.runtime:
            print("--snapshot-as exige --runtime", file=sys.stderr)
            return 2
        try:
            target = write_snapshot(args.runtime, args.snapshot_as)
        except (ValueError, FileNotFoundError) as error:
            print(f"snapshot não gravado: {error}", file=sys.stderr)
            return 2
        print(f"SNAPSHOT {target}")
        return 0

    if args.mode == "package":
        book_dir = (args.runtime / "book") if args.runtime else (args.book or BOOK_ROOT)
        if not (book_dir / "BOOK_SPEC.yaml").is_file():
            print(f"BOOK_SPEC.yaml ausente em {book_dir}", file=sys.stderr)
            return 2
        bundle = load_bundle(book_dir)
        findings = check_package(bundle)
        headline = f"NARCISO PACKAGE %s | {summarize(bundle)}"
    else:
        if not args.runtime:
            print(f"modo `{args.mode}` exige --runtime", file=sys.stderr)
            return 2
        if args.mode == "wave" and not args.through_chapter:
            print("modo `wave` exige --through-chapter", file=sys.stderr)
            return 2
        rt = load_runtime(args.runtime, args.baseline)
        findings = validate_runtime(rt, args.mode, args.through_chapter)
        headline = f"NARCISO {args.mode.upper()} %s | {summarize(rt['bundle'])}"

    blocking = [f for f in findings if f["severity"] in BLOCKING]
    if args.json:
        print(json.dumps({"mode": args.mode, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            print(f"[{f['severity']}] {f['category']} (cap. {f['chapter']}): {f['evidence']} — {f['detail']}")
        status = "INVALID" if blocking else "VALID"
        print(f"{headline % status} | findings={len(findings)} blocking={len(blocking)}")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
