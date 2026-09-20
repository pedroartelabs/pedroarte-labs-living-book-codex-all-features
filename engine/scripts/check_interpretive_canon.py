"""Validador determinístico do `INTERPRETIVE_CANON.yaml` — capability
`LIVING_THEORY_ENGINE`.

Ver `docs/sdd/LIVING_THEORY_ENGINE_SDD_v0.1.md` para o desenho completo.

**Slice 1** implementou o modelo mínimo: integridade do contrato, perguntas
(Duality Seeds) e seus limites, meia-vida (HL-01..03), partições e relações do
Theory Graph (TG-01, TG-02, TG-05), NO_HIDDEN_ANSWER (AD-01..04, AD-06) e a
fronteira teoria × canon (CI-01, CI-02 só para perguntas `NEVER`, CI-04, CI-05).

**Slice 2** (este acréscimo) implementa o Evidence Ledger:

- linhas de evidência ancoradas (EL-01, EL-09), âncora que presume fato
  inexistente (CI-03), suporte S/C/X por interpretação (EL-02), observável que
  enuncia resposta (EL-03);
- suporte mínimo, contraevidência, viabilidade e dominância (EL-04..06),
  interpretação sem evidência e evidência sem suporte (TG-03, TG-04);
- dupla evidência projetada, nunca declarada (DE-01..06);
- testemunho e narradores não confiáveis (EL-08);
- red herrings justos × misdirection barata (RH-01..05, RH-07; RH-06 depende de
  conhecimento por POV e entra no Slice 4);
- sinal/ruído estrutural (16.3): densidade, saliência, camada de releitura,
  cobertura de capítulos;
- consultas `--ledger`, `--double`, `--heatmap`.

Âncoras são resolvidas com `check_visual_canon.resolve_anchor` (REUSE; mesmo
vocabulário LEDGER:/SCENE:/TURN:/CANON:/DOC:/RULE:/TEXT:). Elas só resolvem
quando há `chapter_architecture` — sem ela as regras que dependem de capítulo
não rodam e o relatório declara isso. `text_anchor` (TEXT:) só é conferido
contra o manuscrito congelado no Slice 4.

A comparação de tese com fato/observável é lexical (fração das palavras de
conteúdo da tese presentes no texto). Ela pega cópia e quase-cópia; paráfrase
continua sendo julgamento de CANON_GUARDIAN e SUBTEXT_EDITOR.

Dependências: biblioteca padrão + PyYAML (+ o módulo do canon visual, que usa Pillow).

Uso:
    python engine/scripts/check_interpretive_canon.py --runtime runtime/<slug>
    python engine/scripts/check_interpretive_canon.py --canon caminho/INTERPRETIVE_CANON.yaml
        [--registry CANON_REGISTRY.yaml] [--causal-ledger CAUSAL_LEDGER.yaml]
        [--book-spec BOOK_SPEC.yaml] [--immutable-rules immutable_rules.yaml]
        [--json] [--out relatorio.md]
    python engine/scripts/check_interpretive_canon.py --runtime <rt> --ledger Q-01
    python engine/scripts/check_interpretive_canon.py --runtime <rt> --double [Q-01]
    python engine/scripts/check_interpretive_canon.py --runtime <rt> --heatmap
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import yaml

import check_visual_canon as cvc

SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "BLOCKER"]
BLOCKING = {"HIGH", "BLOCKER"}

API_VERSION = "pedroarte.livingbooks/v1"
CANON_KIND = "InterpretiveCanon"
CANON_OWNER = "CANON_GUARDIAN"

# --- vocabulário fechado (ver INTERPRETIVE_CANON_TEMPLATE.yaml) -------------

AXIS_VALUES = {"FACTUAL", "TEXTUAL", "EPISTEMIC", "PSYCHOLOGICAL", "MORAL", "ONTOLOGICAL", "RELATIONAL"}
HALF_LIFE_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
RESOLUTION_POLICIES = {"NEVER", "LATE_PARTIAL", "RESOLVED_AT"}
SEQUEL_POLICIES = {"SEQUEL"}                   # AD-06: nenhuma pergunta depende de volume futuro
SEED_POLICIES = {"NEVER", "LATE_PARTIAL"}      # Duality Seed = aberta + meia-vida >= MEDIUM
RESOLVING_POLICIES = {"LATE_PARTIAL", "RESOLVED_AT"}
SHAPE_VALUES = {"BINARY", "PLURAL"}
DEFAULT_MIN_VIABLE = {"BINARY": 2, "PLURAL": 3}
RELATION_KINDS = {"IMPLIES", "TENSIONS", "EXCLUDES", "AMPLIFIES"}
MUST_REMAIN_UNKNOWN = "MUST_REMAIN_UNKNOWN"
OPEN_BELIEF_TRUTH = "INCOMPLETE"
AMBIGUITY_GT_KIND = "CONTRADICTION"
NEVER_ACCESS = "NEVER"

EVIDENCE_STATUSES = {"PLANNED", "REALIZED", "RETIRED"}
CHANNELS = {
    "DIALOGUE", "BEHAVIOR", "ABSENCE", "TIMING", "MEMORY", "VERSION_DELTA", "ENVIRONMENT",
    "OBJECT", "DOCUMENT", "PERCEPTION_CONFLICT", "ILLUSTRATION", "PHYSICAL_BOOK", "PARATEXT",
}
VISUAL_CHANNELS = {"ILLUSTRATION", "PHYSICAL_BOOK"}
FIXED_SOURCES = {"NARRATOR", "DOCUMENT", "ILLUSTRATION", "OBJECT"}
SALIENCE_VALUES = {"TEXTURE", "SUPPORTING", "NOTICEABLE"}
DISCOVERABLE_VALUES = {"FIRST_READ", "REREAD"}
SUPPORT_VALUES = {"S", "C", "X", "-"}
STRENGTH_RANK = {"WEAK": 0, "MEDIUM": 1, "STRONG": 2}
ROLE_VALUES = {"CLUE", "RED_HERRING"}
PROJECTED_ROLES = {"DOUBLE_EVIDENCE", "DESTABILIZER", "TEXTURE"}   # nunca declarados (12.2)
AFTER_FUNCTIONS = {"CHARACTERIZES", "MUTATES", "THEMATIC"}
CHAPTER_ANCHOR_KINDS = {"LEDGER", "SCENE", "TURN"}   # âncoras que localizam a evidência num capítulo
CAUSE_ANCHOR_KINDS = {"LEDGER", "RULE", "DOC", "CANON"}   # causa dentro do mundo de um red herring
FACT_ANCHOR_KINDS = {"LEDGER", "CANON"}             # âncora inexistente destes tipos presume fato novo

_ID = r"[A-Z0-9][A-Z0-9_-]*"
QUESTION_ID_RE = re.compile(rf"^Q-{_ID}$")
INTERPRETATION_ID_RE = re.compile(rf"^(Q-{_ID})/({_ID})$")
PARTITION_ID_RE = re.compile(rf"^(Q-{_ID})~({_ID})$")
EVIDENCE_ID_RE = re.compile(rf"^EVD-{_ID}$")
NARRATOR_ID_RE = re.compile(rf"^NRL-{_ID}$")
CHARACTER_ID_RE = re.compile(rf"^CHR-{_ID}$")
CANON_REF_RE = re.compile(r"^CANON:(\S+)$")
LEDGER_EVENT_REF_RE = re.compile(r"^LEDGER:(EV-\S+)$")
LEDGER_EVENT_ID_RE = re.compile(r"^EV-\S+$")
RULE_REF_RE = re.compile(r"^RULE:(\S+)$")
ANCHOR_KIND_RE = re.compile(r"^([A-Z_]+):")
TEXT_ANCHOR_RE = re.compile(r'^TEXT:(\d+):"(.+)"$')
# Qualquer id desta capability que aparecer como causa no ledger é teoria virando causa.
THEORY_ID_RE = re.compile(rf"^(Q-{_ID}([/~]{_ID})?|(EVD|MUT|FR|DST|NRL)-\S+)$")

# AD-02: nenhuma chave, em nenhum nível, guarda resposta. Comparação sem
# acento, sem caixa, com separadores normalizados para "_".
HIDDEN_ANSWER_KEYS = {
    "truth", "answer", "correct", "correct_answer", "canonical_answer", "author_answer",
    "hidden_answer", "intended", "intended_reading", "true_nature", "real_identity",
    "resposta", "resposta_correta", "verdade",
}

KNOWN_FIELDS = {
    "root": {"apiVersion", "kind", "metadata", "policy", "narrators", "questions", "partitions",
             "relations", "evidence", "mutation_log"},
    "metadata": {"project_id", "version", "owner", "refs"},
    "policy": {"no_hidden_answer", "thresholds"},
    "question": {
        "id", "question", "axis", "half_life", "half_life_rationale", "resolution_policy",
        "resolved_at", "unknown_ref", "prohibited_refs", "rule_ref", "shape",
        "min_viable_at_end", "ledger_beliefs", "ledger_ground_truths", "interpretations",
    },
    "interpretation": {"id", "thesis"},
    "partition": {"id", "of", "question", "sides"},
    "relation": {"from", "to", "kind", "synthesis"},
    "narrator": {"id", "voice", "scope", "unreliability", "tells"},
    "evidence": {
        "id", "status", "anchor", "text_anchor", "channel", "source", "observable", "salience",
        "discoverable_on", "role", "support", "readings", "approval", "language_dependent",
        "ledger_event", "fair_herring",
    },
    "reading": {"reading", "strength", "corroborated_by"},
    "fair_herring": {"points_toward", "in_world_cause", "survives_reveal", "counter_available_before",
                     "after_function"},
}
# Blocos de slices futuros: aceitos no arquivo, ainda sem regras.
RESERVED_ROOT_FIELDS = {"mutations", "false_resolutions", "destabilizers"}
REQUIRED_QUESTION_FIELDS = ("id", "question", "axis", "half_life", "resolution_policy", "shape", "interpretations")

DEFAULT_CONFIG = {
    # Slice 1 — sementes e fronteira
    "max_duality_seeds": 3,
    "max_never_questions": 3,
    "max_partitions_per_seed": 4,
    "min_high_half_life_seeds": 1,
    "max_interpretations_per_question": 6,
    "thesis_overlap_threshold": 0.8,
    "min_content_words_for_overlap": 3,
    # Slice 2 — Evidence Ledger (valores iniciais: hipótese de calibração, seção 16.3)
    "min_support": 3,
    "min_support_resolved": 1,
    "max_support_ratio": 2.0,
    "min_double_evidence": 3,
    "max_double_per_chapter": 2,
    "max_double_tilt": 1,
    "max_evidence_per_chapter": 3,
    "max_noticeable_share": 0.25,
    "min_reread_only_share": 0.30,
    "max_evidence_chapter_share": 0.70,
    "max_red_herring_share": 0.15,
}

# Palavras funcionais (>= 4 letras, sem acento) ignoradas na comparação lexical.
STOPWORDS = {
    "para", "como", "mais", "pelo", "pela", "pelos", "pelas", "porque", "quando", "onde", "mesmo",
    "mesma", "sobre", "entre", "depois", "antes", "ainda", "isso", "esse", "essa", "este", "esta",
    "estes", "estas", "aquele", "aquela", "seus", "suas", "dele", "dela", "deles", "delas", "eles",
    "elas", "nunca", "sempre", "muito", "muita", "toda", "todo", "todos", "todas", "outra", "outro",
    "tambem", "apenas", "estava", "estavam", "tinha", "tinham", "sido", "seria", "foram", "fosse",
    "that", "with", "from", "this", "have", "were", "what", "which", "there", "their", "they",
    "been", "into", "only", "would", "could",
}


# --- utilidades --------------------------------------------------------------

def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def optional_yaml(path: Path | None):
    return load_yaml(path) if path is not None and path.is_file() else None


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


def as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def normalize_text(text) -> str:
    return re.sub(r"[^a-z0-9]+", " ", _strip_accents(str(text)).lower()).strip()


def normalize_key(key) -> str:
    return re.sub(r"[^a-z0-9]+", "_", _strip_accents(str(key)).lower()).strip("_")


def content_words(text) -> set[str]:
    return {w for w in normalize_text(text).split() if len(w) >= 4 and w not in STOPWORDS}


def containment(needle, haystack, min_words: int) -> float:
    """Fração das palavras de conteúdo de `needle` presentes em `haystack`.
    Retorna 0.0 quando `needle` tem palavras de conteúdo demais poucas para
    que a comparação signifique alguma coisa."""
    words = content_words(needle)
    if len(words) < min_words:
        return 0.0
    return len(words & content_words(haystack)) / len(words)


def term_hit(term, text) -> bool:
    normalized = normalize_text(term)
    return bool(normalized) and f" {normalized} " in f" {normalize_text(text)} "


def iter_keys(node, path: str = ""):
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            yield key, here
            yield from iter_keys(value, here)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from iter_keys(item, f"{path}[{i}]")


def find_by_id(node, target: str):
    """Busca recursiva por `id: target` — CANON_REGISTRY.yaml não tem schema
    fixo e varia por runtime (mesmo critério de check_visual_canon.find_canon_id)."""
    return cvc.find_canon_id(node, target)


def iter_facts(node):
    """Todo nó do registry com `fact` em texto: (id, fact)."""
    if isinstance(node, dict):
        if isinstance(node.get("fact"), str):
            yield node.get("id"), node["fact"]
        for value in node.values():
            yield from iter_facts(value)
    elif isinstance(node, list):
        for item in node:
            yield from iter_facts(item)


def anchor_kind(token) -> str | None:
    match = ANCHOR_KIND_RE.match(str(token or ""))
    return match.group(1) if match else None


def living_theory_features(book_spec) -> dict:
    features = (((book_spec or {}).get("spec") or {}).get("features") or {}) if isinstance(book_spec, dict) else {}
    return features if isinstance(features, dict) else {}


# --- configuração ------------------------------------------------------------

def resolve_config(canon: dict, book_spec: dict | None, override: dict | None) -> tuple[dict, list[dict]]:
    """Padrões < policy.thresholds do canon < BOOK_SPEC.features.living_theory.thresholds < override."""
    cfg = dict(DEFAULT_CONFIG)
    out: list[dict] = []
    policy = canon.get("policy") if isinstance(canon.get("policy"), dict) else {}
    living_theory = living_theory_features(book_spec).get("living_theory")
    sources = [
        ("policy.thresholds", policy.get("thresholds") or {}),
        ("BOOK_SPEC.features.living_theory.thresholds",
         (living_theory.get("thresholds") or {}) if isinstance(living_theory, dict) else {}),
        ("override", override or {}),
    ]
    for label, values in sources:
        if not isinstance(values, dict):
            out.append(finding("THRESHOLD_INVALID", "LOW", None, label,
                               "thresholds precisa ser um mapa chave → número.", "Corrigir o bloco."))
            continue
        for key, value in values.items():
            if key not in DEFAULT_CONFIG:
                out.append(finding("THRESHOLD_UNKNOWN", "LOW", None, f"{label}.{key}",
                                   f"Limiar desconhecido; conhecidos: {', '.join(sorted(DEFAULT_CONFIG))}.",
                                   "Corrigir o nome (provável erro de digitação) ou remover."))
            elif isinstance(value, bool) or not isinstance(value, (int, float)):
                out.append(finding("THRESHOLD_INVALID", "LOW", None, f"{label}.{key}={value!r}",
                                   "Limiar precisa ser numérico; o padrão foi mantido.", "Corrigir o valor."))
            else:
                cfg[key] = value
    return cfg, out


# --- integridade e índice ----------------------------------------------------

def _unknown_fields(node: dict, level: str, label: str) -> list[dict]:
    allowed = KNOWN_FIELDS[level] | (RESERVED_ROOT_FIELDS if level == "root" else set())
    return [finding("UNKNOWN_FIELD", "MEDIUM", None, f"{label}.{key}",
                    f"Campo desconhecido em {level}; conhecidos: {', '.join(sorted(KNOWN_FIELDS[level]))}.",
                    "Corrigir o nome (provável erro de digitação) ou remover o campo.")
            for key in node if key not in allowed]


def check_contract(canon: dict) -> list[dict]:
    out: list[dict] = []
    if canon.get("apiVersion") != API_VERSION:
        out.append(finding("CONTRACT_INVALID", "HIGH", None, f"apiVersion={canon.get('apiVersion')!r}",
                           f"apiVersion precisa ser {API_VERSION}.", "Corrigir apiVersion."))
    if canon.get("kind") != CANON_KIND:
        out.append(finding("CONTRACT_INVALID", "HIGH", None, f"kind={canon.get('kind')!r}",
                           f"kind precisa ser {CANON_KIND} (canon interpretativo genérico do motor).",
                           "Corrigir kind; um canon de obra específico não é este contrato."))
    out += _unknown_fields(canon, "root", "root")
    metadata = canon.get("metadata")
    if not isinstance(metadata, dict):
        out.append(finding("FIELD_MISSING", "HIGH", None, "metadata", "metadata é obrigatório.", "Declarar metadata."))
    else:
        out += _unknown_fields(metadata, "metadata", "metadata")
        if metadata.get("owner") != CANON_OWNER:
            out.append(finding("CONTRACT_INVALID", "HIGH", None, f"metadata.owner={metadata.get('owner')!r}",
                               "O canon interpretativo tem dono exclusivo CANON_GUARDIAN (lock CANON_WRITE).",
                               "Definir owner: CANON_GUARDIAN."))
    if isinstance(canon.get("policy"), dict):
        out += _unknown_fields(canon["policy"], "policy", "policy")
    if not isinstance(canon.get("questions"), list) or not canon.get("questions"):
        out.append(finding("FIELD_MISSING", "HIGH", None, "questions",
                           "O canon interpretativo declara ao menos uma pergunta.", "Declarar questions."))
    for block in ("partitions", "relations", "narrators"):
        if canon.get(block) is not None and not isinstance(canon.get(block), list):
            out.append(finding("CONTRACT_INVALID", "HIGH", None, block, f"{block} precisa ser uma lista.",
                               f"Corrigir {block}."))
    return out


def build_index(canon: dict) -> tuple[dict, list[dict]]:
    idx = {"questions": {}, "owner": {}, "thesis": {}, "q_interps": {}}
    out: list[dict] = []
    for q in as_list(canon.get("questions")):
        if not isinstance(q, dict):
            out.append(finding("CONTRACT_INVALID", "HIGH", None, repr(q), "Pergunta precisa ser um mapa.",
                               "Corrigir a entrada."))
            continue
        qid = q.get("id")
        if not QUESTION_ID_RE.match(str(qid)):
            out.append(finding("ID_MALFORMED", "HIGH", None, f"questions.id={qid!r}",
                               "Id de pergunta segue o padrão Q-<MAIÚSCULAS>.", "Corrigir o id."))
            continue
        if qid in idx["questions"]:
            out.append(finding("QUESTION_DUPLICATE", "HIGH", None, qid, "Ids de pergunta são únicos.",
                               "Remover ou renomear a duplicata."))
            continue
        idx["questions"][qid] = q
        idx["q_interps"][qid] = []
        for interp in as_list(q.get("interpretations")):
            if not isinstance(interp, dict):
                out.append(finding("CONTRACT_INVALID", "HIGH", None, f"{qid}.interpretations",
                                   "Interpretação precisa ser um mapa {id, thesis}.", "Corrigir a entrada."))
                continue
            iid = interp.get("id")
            match = INTERPRETATION_ID_RE.match(str(iid))
            if not match or match.group(1) != qid:
                out.append(finding("INTERPRETATION_ID_MISMATCH", "HIGH", None, f"{qid}: {iid!r}",
                                   f"Id de interpretação segue o padrão {qid}/<MAIÚSCULAS> da própria pergunta.",
                                   "Corrigir o id."))
                continue
            if iid in idx["owner"]:
                out.append(finding("INTERPRETATION_DUPLICATE", "HIGH", None, iid,
                                   "Ids de interpretação são únicos.", "Remover a duplicata."))
                continue
            idx["owner"][iid] = qid
            idx["thesis"][iid] = interp.get("thesis") or ""
            idx["q_interps"][qid].append(iid)
    return idx, out


def _min_viable(q: dict, count: int) -> int:
    value = q.get("min_viable_at_end")
    if isinstance(value, int) and not isinstance(value, bool) and 2 <= value <= count:
        return value
    return min(DEFAULT_MIN_VIABLE.get(q.get("shape"), 2), max(count, 2))


def _policy(idx: dict, qid: str):
    return idx["questions"][qid].get("resolution_policy")


# --- perguntas ---------------------------------------------------------------

def check_questions(idx: dict, cfg: dict, immutable_rules: list | None) -> list[dict]:
    out: list[dict] = []
    rule_ids = {r.get("id") for r in immutable_rules or [] if isinstance(r, dict)}
    for qid, q in idx["questions"].items():
        out += _unknown_fields(q, "question", qid)
        for field in REQUIRED_QUESTION_FIELDS:
            if q.get(field) in (None, "", []):
                out.append(finding("FIELD_MISSING", "HIGH", None, f"{qid}.{field}",
                                   f"{field} é obrigatório em toda pergunta.", f"Declarar {field}."))
        for field, allowed in (("axis", AXIS_VALUES), ("half_life", set(HALF_LIFE_RANK)), ("shape", SHAPE_VALUES)):
            if q.get(field) is not None and q.get(field) not in allowed:
                out.append(finding("INVALID_ENUM", "HIGH", None, f"{qid}.{field}={q.get(field)!r}",
                                   f"Valores aceitos: {', '.join(sorted(allowed))}.", f"Corrigir {field}."))
        policy = q.get("resolution_policy")
        if policy in SEQUEL_POLICIES:
            out.append(finding("SEQUEL_DEPENDENCY", "HIGH", None, f"{qid}.resolution_policy={policy}",
                               "Nenhuma pergunta pode depender de volume futuro para fazer sentido (AD-06).",
                               "Escolher NEVER, LATE_PARTIAL ou RESOLVED_AT dentro desta obra."))
        elif policy is not None and policy not in RESOLUTION_POLICIES:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{qid}.resolution_policy={policy!r}",
                               f"Valores aceitos: {', '.join(sorted(RESOLUTION_POLICIES))}.",
                               "Corrigir resolution_policy."))

        interpretations = as_list(q.get("interpretations"))
        for interp in interpretations:
            if isinstance(interp, dict):
                out += _unknown_fields(interp, "interpretation", f"{qid}:{interp.get('id')}")
                if not str(interp.get("thesis") or "").strip():
                    out.append(finding("FIELD_MISSING", "HIGH", None, f"{interp.get('id')}.thesis",
                                       "Toda interpretação declara a tese em uma frase concreta.",
                                       "Escrever a tese."))
        count = len(interpretations)
        shape = q.get("shape")
        if (shape == "BINARY" and count != 2) or (shape == "PLURAL" and count < 3):
            out.append(finding("SHAPE_MISMATCH", "HIGH", None, f"{qid}: shape={shape} interpretações={count}",
                               "BINARY tem exatamente 2 interpretações; PLURAL tem 3 ou mais.",
                               "Ajustar shape ou interpretações."))
        if count > cfg["max_interpretations_per_question"]:
            out.append(finding("TOO_MANY_INTERPRETATIONS", "MEDIUM", None, f"{qid}: {count}",
                               f"Mais de {cfg['max_interpretations_per_question']} leituras dispersa o leitor "
                               "em taxonomia em vez de discussão.",
                               "Fundir leituras próximas ou transformar distinções em partições."))
        min_viable = q.get("min_viable_at_end")
        if min_viable is not None and (isinstance(min_viable, bool) or not isinstance(min_viable, int)
                                       or not 2 <= min_viable <= count):
            out.append(finding("INVALID_VIABILITY", "HIGH", None, f"{qid}.min_viable_at_end={min_viable!r}",
                               f"min_viable_at_end é inteiro entre 2 e o nº de interpretações ({count}).",
                               "Corrigir o valor."))

        half_life = q.get("half_life")
        axis = q.get("axis")
        if half_life == "HIGH" and not str(q.get("half_life_rationale") or "").strip():
            out.append(finding("HALF_LIFE_RATIONALE_MISSING", "MEDIUM", None, qid,
                               "Meia-vida HIGH declara por que a pergunta sobrevive a todos os fatos conhecidos.",
                               "Escrever half_life_rationale."))
        if axis == "FACTUAL" and half_life == "HIGH":
            out.append(finding("HALF_LIFE_INFLATED", "MEDIUM", None, qid,
                               "Pergunta factual tende a morrer quando o fato aparece (HL-01).",
                               "Rebaixar half_life ou reformular a pergunta no eixo que realmente dura."))

        rule_ref = q.get("rule_ref")
        if rule_ref is not None:
            match = RULE_REF_RE.match(str(rule_ref))
            if not match:
                out.append(finding("RULE_REF_INVALID", "HIGH", None, f"{qid}.rule_ref={rule_ref!r}",
                                   "rule_ref segue o formato RULE:<id de immutable_rules.yaml>.",
                                   "Corrigir a referência."))
            elif immutable_rules is not None and match.group(1) not in rule_ids:
                out.append(finding("RULE_REF_INVALID", "HIGH", None, f"{qid}.rule_ref={rule_ref}",
                                   "A regra imutável citada não existe em book/immutable_rules.yaml.",
                                   "Corrigir a referência."))
        if axis == "FACTUAL" and policy == "NEVER" and rule_ref is None:
            out.append(finding("FACT_WITHHELD_AS_MYSTERY", "HIGH", None, qid,
                               "Pergunta factual que nunca se resolve costuma ser informação escondida, não "
                               "ambiguidade sustentada (HL-03, BAD AMBIGUITY).",
                               "Responder o fato na obra, reformular no eixo que dura, ou declarar rule_ref para "
                               "a regra imutável que exige o silêncio."))

        resolved_at = q.get("resolved_at")
        if policy == "RESOLVED_AT":
            if not LEDGER_EVENT_REF_RE.match(str(resolved_at or "")):
                out.append(finding("RESOLUTION_ANCHOR_INVALID", "HIGH", None, f"{qid}.resolved_at={resolved_at!r}",
                                   "Pergunta RESOLVED_AT aponta o evento de revelação no ledger (LEDGER:EV-*).",
                                   "Declarar resolved_at."))
        elif resolved_at is not None:
            out.append(finding("RESOLUTION_ANCHOR_INVALID", "HIGH", None, f"{qid}.resolved_at={resolved_at!r}",
                               f"Só RESOLVED_AT declara resolved_at; esta pergunta é {policy}.",
                               "Remover resolved_at ou corrigir a política."))

        unknown_ref = q.get("unknown_ref")
        if policy == "NEVER" and not unknown_ref:
            out.append(finding("UNKNOWN_REF_MISSING", "HIGH", None, qid,
                               "Pergunta NEVER aponta a incógnita MUST_REMAIN_UNKNOWN do registry: o motor "
                               "precisa saber que não sabe (CI-04).",
                               "Declarar unknown_ref: \"CANON:UNK-*\"."))
        elif unknown_ref and not CANON_REF_RE.match(str(unknown_ref)):
            out.append(finding("UNKNOWN_REF_INVALID", "HIGH", None, f"{qid}.unknown_ref={unknown_ref!r}",
                               "unknown_ref segue o formato CANON:<id>.", "Corrigir a referência."))
        prohibited_refs = q.get("prohibited_refs")
        if prohibited_refs is not None and not isinstance(prohibited_refs, list):
            out.append(finding("CONTRACT_INVALID", "HIGH", None, f"{qid}.prohibited_refs",
                               "prohibited_refs é uma lista.", "Corrigir."))
            prohibited_refs = []
        if policy == "NEVER" and not prohibited_refs:
            out.append(finding("PROHIBITED_REFS_MISSING", "MEDIUM", None, qid,
                               "Ambiguidade engenheirada é delimitada: pergunta NEVER cita as inferências "
                               "proibidas que o texto não pode permitir.",
                               "Declarar prohibited_refs com PRO-* do registry."))
        for ref in prohibited_refs or []:
            if not CANON_REF_RE.match(str(ref)):
                out.append(finding("UNKNOWN_REFERENCE", "HIGH", None, f"{qid}.prohibited_refs={ref!r}",
                                   "prohibited_refs usa o formato CANON:<id>.", "Corrigir a referência."))
        for field in ("ledger_beliefs", "ledger_ground_truths"):
            if q.get(field) is not None and not isinstance(q.get(field), list):
                out.append(finding("CONTRACT_INVALID", "HIGH", None, f"{qid}.{field}",
                                   f"{field} é uma lista de ids do ledger.", "Corrigir."))
    return out


def check_seed_limits(idx: dict, cfg: dict) -> list[dict]:
    out: list[dict] = []
    questions = idx["questions"]
    seeds = sorted(qid for qid, q in questions.items()
                   if q.get("resolution_policy") in SEED_POLICIES and HALF_LIFE_RANK.get(q.get("half_life"), -1) >= 1)
    nevers = sorted(qid for qid, q in questions.items() if q.get("resolution_policy") == "NEVER")
    high = [qid for qid, q in questions.items() if q.get("half_life") == "HIGH"]
    if len(seeds) > cfg["max_duality_seeds"]:
        out.append(finding("TOO_MANY_DUALITY_SEEDS", "MEDIUM", None, f"sementes={seeds}",
                           f"No máximo {cfg['max_duality_seeds']} perguntas de alta profundidade: acima disso "
                           "o leitor dispersa em vez de discutir (10.4).",
                           "Escolher as sementes mais enraizadas em personagem e transformar o resto em partições."))
    if len(nevers) > cfg["max_never_questions"]:
        out.append(finding("TOO_MANY_OPEN_QUESTIONS", "MEDIUM", None, f"NEVER={nevers}",
                           f"No máximo {cfg['max_never_questions']} perguntas sem resposta: o livro também "
                           "precisa responder coisas (DD-03).",
                           "Resolver dentro da obra as perguntas que a narrativa precisa fechar."))
    if questions and len(high) < cfg["min_high_half_life_seeds"]:
        out.append(finding("NO_DURABLE_QUESTION", "MEDIUM", None, f"HIGH={len(high)}",
                           f"Ao menos {cfg['min_high_half_life_seeds']} pergunta(s) de meia-vida HIGH (HL-02).",
                           "Declarar a pergunta psicológica, moral, ontológica ou relacional que sustenta a obra."))
    return out


# --- Theory Graph: partições e relações -------------------------------------

def check_partitions(canon: dict, idx: dict, cfg: dict) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    per_seed: dict[str, int] = defaultdict(int)
    for part in as_list(canon.get("partitions")):
        if not isinstance(part, dict):
            out.append(finding("CONTRACT_INVALID", "HIGH", None, repr(part), "Partição precisa ser um mapa.",
                               "Corrigir a entrada."))
            continue
        pid, of = part.get("id"), part.get("of")
        out += _unknown_fields(part, "partition", str(pid))
        match = PARTITION_ID_RE.match(str(pid))
        if not match or match.group(1) != of or of not in idx["questions"]:
            out.append(finding("PARTITION_INVALID", "HIGH", None, f"{pid!r} of={of!r}",
                               "Partição tem id <Q-id>~<NOME> e `of` aponta uma pergunta existente.",
                               "Corrigir id ou of."))
            continue
        if pid in seen:
            out.append(finding("PARTITION_INVALID", "HIGH", None, pid, "Ids de partição são únicos.",
                               "Remover a duplicata."))
            continue
        seen.add(pid)
        per_seed[of] += 1
        if not str(part.get("question") or "").strip():
            out.append(finding("FIELD_MISSING", "HIGH", None, f"{pid}.question",
                               "Partição declara a pergunta binária derivada.", "Escrever a pergunta."))
        sides = part.get("sides")
        if not isinstance(sides, dict) or len(sides) < 2:
            out.append(finding("PARTITION_INVALID", "HIGH", None, f"{pid}.sides",
                               "Partição tem ao menos duas faces, cada uma com interpretações.",
                               "Declarar sides."))
            continue
        placed: dict[str, str] = {}
        for side, members in sides.items():
            if not isinstance(side, str):
                # YAML 1.1 resolve YES/NO/ON/OFF/TRUE/FALSE sem aspas como booleano:
                # {YES: [...], NO: [...]} vira {True: [...], False: [...]}.
                out.append(finding("PARTITION_INVALID", "HIGH", None, f"{pid}.sides.{side!r}",
                                   "Nome de face precisa ser texto; YES/NO sem aspas viram booleanos em YAML 1.1.",
                                   "Escrever as faces entre aspas: {\"YES\": [...], \"NO\": [...]}."))
                continue
            if not isinstance(members, list) or not members:
                out.append(finding("PARTITION_INVALID", "HIGH", None, f"{pid}.sides.{side}",
                                   "Cada face lista ao menos uma interpretação.", "Completar a face."))
                continue
            for member in members:
                if idx["owner"].get(member) != of:
                    out.append(finding("PARTITION_INVALID", "HIGH", None, f"{pid}.sides.{side}: {member!r}",
                                       f"Faces só contêm interpretações de {of}.", "Corrigir o membro."))
                elif member in placed:
                    out.append(finding("PARTITION_INVALID", "HIGH", None,
                                       f"{pid}: {member} em {placed[member]} e {side}",
                                       "Uma interpretação fica em no máximo uma face (ou em nenhuma).",
                                       "Escolher a face ou deixar a interpretação sem face."))
                else:
                    placed[member] = side
        if idx["questions"][of].get("shape") == "BINARY":
            out.append(finding("PARTITION_REDUNDANT", "LOW", None, pid,
                               "Partir uma pergunta BINARY reproduz a própria pergunta.", "Remover a partição."))
    for seed, count in sorted(per_seed.items()):
        if count > cfg["max_partitions_per_seed"]:
            out.append(finding("TOO_MANY_PARTITIONS", "MEDIUM", None, f"{seed}: {count}",
                               f"No máximo {cfg['max_partitions_per_seed']} partições por semente: partição a "
                               "mais é taxonomia, não pergunta.", "Manter só as perguntas que leitores fariam."))
    return out


def build_relation_graph(canon: dict, idx: dict) -> tuple[dict, list[dict]]:
    owner = idx["owner"]
    implies: dict[str, set[str]] = defaultdict(set)
    excludes: set[frozenset] = set()
    amplifies: set[frozenset] = set()
    out: list[dict] = []
    for rel in as_list(canon.get("relations")):
        if not isinstance(rel, dict):
            out.append(finding("CONTRACT_INVALID", "HIGH", None, repr(rel), "Relação precisa ser um mapa.",
                               "Corrigir a entrada."))
            continue
        a, b, kind = rel.get("from"), rel.get("to"), rel.get("kind")
        label = f"{a} {kind} {b}"
        out += _unknown_fields(rel, "relation", label)
        if kind not in RELATION_KINDS:
            out.append(finding("INVALID_ENUM", "HIGH", None, label,
                               f"kind aceita: {', '.join(sorted(RELATION_KINDS))}.", "Corrigir kind."))
            continue
        if a not in owner or b not in owner or a == b:
            out.append(finding("RELATION_UNRESOLVED", "HIGH", None, label,
                               "Relação liga duas interpretações existentes e distintas (TG-01).",
                               "Corrigir from/to."))
            continue
        if owner[a] == owner[b]:
            if kind in ("EXCLUDES", "TENSIONS"):
                out.append(finding("RELATION_REDUNDANT", "LOW", None, label,
                                   "Interpretações da mesma pergunta já se excluem por definição.",
                                   "Remover a relação."))
            else:
                out.append(finding("RELATION_CONTRADICTORY", "HIGH", None, label,
                                   "Interpretações da mesma pergunta se excluem; uma não pode implicar ou "
                                   "amplificar a outra (TG-02).", "Remover a relação ou separar as perguntas."))
            continue
        pair = frozenset((a, b))
        if kind == "IMPLIES":
            implies[a].add(b)
        elif kind == "EXCLUDES":
            excludes.add(pair)
        elif kind == "AMPLIFIES":
            amplifies.add(pair)
    for pair in sorted(amplifies & excludes, key=sorted):
        out.append(finding("RELATION_CONTRADICTORY", "HIGH", None, " × ".join(sorted(pair)),
                           "O mesmo par não pode se amplificar e se excluir (TG-02).", "Escolher uma relação."))
    return {"implies": implies, "excludes": excludes}, out


def implication_closure(graph: dict, start: str) -> set[str]:
    seen = {start}
    stack = [start]
    while stack:
        for nxt in graph["implies"].get(stack.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def check_relation_consistency(graph: dict, idx: dict) -> list[dict]:
    """TG-02 transitivo: seguir IMPLIES a partir de uma interpretação não pode
    chegar a duas interpretações que se excluem."""
    owner = idx["owner"]
    out: list[dict] = []
    for start in sorted(graph["implies"]):
        closure = sorted(implication_closure(graph, start))
        conflicts = [
            (x, y) for i, x in enumerate(closure) for y in closure[i + 1:]
            if frozenset((x, y)) in graph["excludes"] or owner[x] == owner[y]
        ]
        if conflicts:
            out.append(finding("RELATION_CONTRADICTORY", "HIGH", None,
                               f"{start} ⇒ {closure}; conflitos={conflicts}",
                               "Seguir as implicações a partir desta interpretação chega a leituras que se "
                               "excluem (TG-02).", "Remover a implicação ou a exclusão incoerente."))
    return out


def check_graph_forces_resolution(graph: dict, idx: dict) -> list[dict]:
    """TG-05: revelar a resposta de uma pergunta RESOLVED_AT/LATE_PARTIAL não
    pode, pelas relações declaradas, deixar uma pergunta NEVER com menos
    interpretações viáveis que o mínimo. Como o canon nunca sabe qual
    interpretação será revelada, toda interpretação da pergunta resolvida é
    testada."""
    owner = idx["owner"]
    excluded_by: dict[str, set[str]] = defaultdict(set)
    for pair in graph["excludes"]:
        x, y = tuple(pair)
        excluded_by[x].add(y)
        excluded_by[y].add(x)
    out: list[dict] = []
    for qid, q in idx["questions"].items():
        targets = idx["q_interps"][qid]
        if q.get("resolution_policy") != "NEVER" or len(targets) < 2:
            continue
        minimum = _min_viable(q, len(targets))
        for rid, resolved in idx["questions"].items():
            if rid == qid or resolved.get("resolution_policy") not in RESOLVING_POLICIES:
                continue
            for assumed in idx["q_interps"][rid]:
                removed: set[str] = set()
                for node in implication_closure(graph, assumed):
                    removed |= excluded_by[node]
                    if owner[node] == qid:
                        removed |= set(targets) - {node}
                viable = [t for t in targets if t not in removed]
                if len(viable) < minimum:
                    out.append(finding("GRAPH_FORCES_RESOLUTION", "BLOCKER", None,
                                       f"se {assumed} for revelada: {qid} viáveis={viable} (mínimo {minimum})",
                                       f"A revelação de {rid} fecharia a pergunta NEVER {qid} pelas relações "
                                       "declaradas (TG-05).",
                                       "Remover a exclusão/implicação ou rever a política de uma das perguntas."))
    return out


# --- NO_HIDDEN_ANSWER --------------------------------------------------------

def check_hidden_answer(canon: dict) -> list[dict]:
    out: list[dict] = []
    policy = canon.get("policy")
    if not isinstance(policy, dict) or policy.get("no_hidden_answer") is not True:
        out.append(finding("HIDDEN_ANSWER_PRESENT", "BLOCKER", None, "policy.no_hidden_answer",
                           "A política NO_HIDDEN_ANSWER é obrigatória (AD-01).",
                           "Definir policy.no_hidden_answer: true."))
    for key, path in iter_keys(canon):
        if normalize_key(key) in HIDDEN_ANSWER_KEYS:
            out.append(finding("HIDDEN_ANSWER_PRESENT", "BLOCKER", None, path,
                               "Nenhum campo do canon interpretativo guarda resposta, verdade ou leitura "
                               "pretendida (AD-02). Se o motor souber, algum brief acaba sabendo.",
                               "Remover o campo; causalidade que o motor precisa mora no ledger como GT "
                               "CONTRADICTION com reader_access NEVER."))
    return out


# --- Evidence Ledger (Slice 2) -------------------------------------------------

def build_anchor_context(registry, ledger, immutable_rules, chapter_architecture, protected_scenes, bibles):
    """Mesmo formato de check_visual_canon.load_context, montado a partir dos
    argumentos já carregados (assim uma mutação em memória do ledger também muda
    a resolução de âncora). Sem chapter_architecture não há contexto."""
    if chapter_architecture is None:
        return None
    return {
        "canon_registry": registry or {},
        "causal_ledger": ledger,
        "chapter_architecture": chapter_architecture or [],
        "protected_scenes": protected_scenes or [],
        "immutable_rules": immutable_rules or [],
        "bibles": bibles or {},
        "manuscript": {},
    }


def _locate_anchor(eid: str, anchor, anchor_ctx) -> tuple[int | None, list[dict]]:
    """EL-01 / CI-03: a âncora de uma evidência resolve e localiza um capítulo."""
    if not str(anchor or "").strip():
        return None, [finding("FIELD_MISSING", "HIGH", None, f"{eid}.anchor",
                              "Toda evidência aponta onde está: LEDGER:EV-*, SCENE: ou TURN:.", "Declarar anchor.")]
    kind = anchor_kind(anchor)
    if kind not in CHAPTER_ANCHOR_KINDS:
        return None, [finding("EVIDENCE_ANCHOR_UNLOCATED", "HIGH", None, f"{eid}.anchor={anchor}",
                              "A âncora de evidência localiza um capítulo (LEDGER:EV-*, SCENE:, TURN:); a citação "
                              "literal vai em text_anchor.", "Trocar a âncora.")]
    if anchor_ctx is None:
        return None, []
    result = cvc.resolve_anchor(anchor, anchor_ctx, mode="plan") or {}
    if not result.get("ok"):
        if kind in FACT_ANCHOR_KINDS and result.get("reason") == "NOT_FOUND":
            return None, [finding("EVIDENCE_CREATES_FACT", "HIGH", None, f"{eid}.anchor={anchor}",
                                  "A evidência presume um fato que não existe no canon (CI-03).",
                                  "Propor o fato em canon/CANON_PROPOSALS ou corrigir a âncora.")]
        return None, [finding("EVIDENCE_ANCHOR_UNRESOLVED", "HIGH", None,
                              f"{eid}.anchor={anchor} ({result.get('reason')})",
                              "A âncora não resolve contra o canon/arquitetura deste runtime (EL-01).",
                              "Corrigir a âncora.")]
    if result.get("chapter") is None:
        return None, [finding("EVIDENCE_ANCHOR_UNLOCATED", "HIGH", None, f"{eid}.anchor={anchor}",
                              "A âncora resolve mas não localiza capítulo (ex.: LEDGER:GT-*).",
                              "Ancorar no evento ou turno em que a evidência aparece.")]
    return result["chapter"], []


def build_evidence(canon: dict, idx: dict, anchor_ctx, ledger, book_spec) -> tuple[list[dict], list[dict]]:
    out: list[dict] = []
    rows: list[dict] = []
    evidence = canon.get("evidence")
    if evidence is None:
        return rows, [finding("EVIDENCE_LEDGER_MISSING", "HIGH", None, "evidence",
                              "Sem evidências, toda interpretação é declaração vazia: o canon interpretativo "
                              "planeja as evidências que sustentam cada leitura (11).",
                              "Declarar evidence[].")]
    if not isinstance(evidence, list):
        return rows, [finding("CONTRACT_INVALID", "HIGH", None, "evidence", "evidence precisa ser uma lista.",
                              "Corrigir evidence.")]
    features = living_theory_features(book_spec)
    living_theory = features.get("living_theory") if isinstance(features.get("living_theory"), dict) else {}
    visual_narrative = features.get("visual_narrative") if isinstance(features.get("visual_narrative"), dict) else {}
    visual_enabled = living_theory.get("visual_evidence") is True and bool(visual_narrative.get("enabled"))
    ledger_events = {e.get("id"): e for e in as_list((ledger or {}).get("events")) if isinstance(e, dict)}
    characters = {c.get("id") for c in as_list((ledger or {}).get("characters")) if isinstance(c, dict)}
    seen: set[str] = set()

    for raw in evidence:
        if not isinstance(raw, dict):
            out.append(finding("CONTRACT_INVALID", "HIGH", None, repr(raw), "Evidência precisa ser um mapa.",
                               "Corrigir a entrada."))
            continue
        eid = raw.get("id")
        out += _unknown_fields(raw, "evidence", str(eid))
        if not EVIDENCE_ID_RE.match(str(eid)):
            out.append(finding("ID_MALFORMED", "HIGH", None, f"evidence.id={eid!r}",
                               "Id de evidência segue o padrão EVD-<MAIÚSCULAS>.", "Corrigir o id."))
            continue
        if eid in seen:
            out.append(finding("EVIDENCE_DUPLICATE", "HIGH", None, eid, "Ids de evidência são únicos (EL-09).",
                               "Remover ou renomear a duplicata."))
            continue
        seen.add(eid)

        status = raw.get("status")
        if status not in EVIDENCE_STATUSES:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{eid}.status={status!r}",
                               f"Valores aceitos: {', '.join(sorted(EVIDENCE_STATUSES))}.", "Corrigir status."))
        for field, allowed in (("channel", CHANNELS), ("salience", SALIENCE_VALUES),
                               ("discoverable_on", DISCOVERABLE_VALUES)):
            value = raw.get(field)
            if value is None:
                out.append(finding("FIELD_MISSING", "HIGH", None, f"{eid}.{field}", f"{field} é obrigatório.",
                                   f"Declarar {field}."))
            elif value not in allowed:
                out.append(finding("INVALID_ENUM", "HIGH", None, f"{eid}.{field}={value!r}",
                                   f"Valores aceitos: {', '.join(sorted(allowed))}.", f"Corrigir {field}."))
        source = raw.get("source")
        if source is None:
            out.append(finding("FIELD_MISSING", "HIGH", None, f"{eid}.source", "source é obrigatório.",
                               "Declarar quem apresenta a evidência."))
        elif source not in FIXED_SOURCES and not CHARACTER_ID_RE.match(str(source)):
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{eid}.source={source!r}",
                               f"source aceita {', '.join(sorted(FIXED_SOURCES))} ou CHR-*.", "Corrigir source."))
        elif CHARACTER_ID_RE.match(str(source)) and ledger is not None and source not in characters:
            out.append(finding("UNKNOWN_REFERENCE", "HIGH", None, f"{eid}.source={source}",
                               "O personagem citado não existe no ledger.", "Corrigir source."))
        role = raw.get("role") or "CLUE"
        if role in PROJECTED_ROLES:
            out.append(finding("ROLE_NOT_DECLARABLE", "HIGH", None, f"{eid}.role={role}",
                               "DOUBLE_EVIDENCE é projetado, DESTABILIZER vive em destabilizers[] e TEXTURE não "
                               "entra no canon (12.2).", "Remover o role ou usar CLUE/RED_HERRING."))
        elif role not in ROLE_VALUES:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{eid}.role={role!r}",
                               f"role aceita: {', '.join(sorted(ROLE_VALUES))}.", "Corrigir role."))
        if raw.get("fair_herring") is not None and role != "RED_HERRING":
            out.append(finding("RED_HERRING_INVALID", "LOW", None, f"{eid}.fair_herring",
                               "fair_herring só existe em evidências RED_HERRING.", "Remover o bloco ou o role."))
        if not str(raw.get("observable") or "").strip():
            out.append(finding("FIELD_MISSING", "HIGH", None, f"{eid}.observable",
                               "Toda evidência descreve o que se pode perceber — percepção, nunca verdade.",
                               "Escrever o observable."))
        if raw.get("language_dependent") is not None and not isinstance(raw.get("language_dependent"), bool):
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{eid}.language_dependent",
                               "language_dependent é true ou false.", "Corrigir."))
        if raw.get("channel") in VISUAL_CHANNELS and not visual_enabled:
            out.append(finding("VISUAL_EVIDENCE_DISABLED", "HIGH", None, f"{eid}.channel={raw.get('channel')}",
                               "Evidência visual exige features.living_theory.visual_evidence e "
                               "features.visual_narrative ligados (15.2).",
                               "Ligar as duas features ou mover a evidência para um canal textual."))

        chapter, anchor_findings = _locate_anchor(eid, raw.get("anchor"), anchor_ctx)
        out += anchor_findings

        text_anchor = raw.get("text_anchor")
        if text_anchor is not None:
            text_match = TEXT_ANCHOR_RE.match(str(text_anchor))
            if not text_match:
                out.append(finding("EVIDENCE_ANCHOR_UNRESOLVED", "HIGH", chapter, f"{eid}.text_anchor={text_anchor!r}",
                                   "text_anchor segue o formato TEXT:<capítulo>:\"trecho literal\".",
                                   "Corrigir o formato."))
            elif chapter is not None and int(text_match.group(1)) != chapter:
                out.append(finding("EVIDENCE_CHAPTER_MISMATCH", "MEDIUM", chapter, f"{eid}.text_anchor={text_anchor}",
                                   f"A citação está no capítulo {text_match.group(1)}, a âncora no {chapter}.",
                                   "Alinhar anchor e text_anchor."))
        elif status == "REALIZED":
            out.append(finding("TEXT_ANCHOR_MISSING", "HIGH", chapter, eid,
                               "Evidência REALIZED aponta o trecho literal da prosa que a realizou.",
                               "Declarar text_anchor ou devolver a linha para PLANNED."))

        ledger_event = raw.get("ledger_event")
        if ledger_event is not None:
            if not LEDGER_EVENT_ID_RE.match(str(ledger_event)):
                out.append(finding("UNKNOWN_REFERENCE", "HIGH", chapter, f"{eid}.ledger_event={ledger_event!r}",
                                   "ledger_event é um id EV-* do ledger causal.", "Corrigir a referência."))
            elif ledger is not None:
                event = ledger_events.get(ledger_event)
                if event is None:
                    out.append(finding("UNKNOWN_REFERENCE", "HIGH", chapter, f"{eid}.ledger_event={ledger_event}",
                                       "O evento citado não existe no ledger (EL-09).", "Corrigir a referência."))
                elif chapter is not None and event.get("chapter") != chapter:
                    out.append(finding("EVIDENCE_CHAPTER_MISMATCH", "MEDIUM", chapter,
                                       f"{eid}.ledger_event={ledger_event} (cap. {event.get('chapter')})",
                                       "O evento do ledger e a âncora da evidência estão em capítulos diferentes.",
                                       "Alinhar anchor e ledger_event."))

        support_raw = raw.get("support")
        support: dict[str, str] = {}
        if not isinstance(support_raw, dict) or not support_raw:
            out.append(finding("FIELD_MISSING", "HIGH", chapter, f"{eid}.support",
                               "Toda evidência declara o que sustenta (S), complica (C) ou exclui (X).",
                               "Declarar support."))
        else:
            for iid, value in support_raw.items():
                if iid not in idx["owner"]:
                    out.append(finding("UNKNOWN_REFERENCE", "HIGH", chapter, f"{eid}.support.{iid}",
                                       "A interpretação citada não existe.", "Corrigir a referência."))
                elif value not in SUPPORT_VALUES:
                    out.append(finding("INVALID_ENUM", "HIGH", chapter, f"{eid}.support.{iid}={value!r}",
                                       "support aceita S, C, X ou \"-\" (entre aspas no YAML).",
                                       "Corrigir o valor."))
                else:
                    support[iid] = value
            for qid in sorted({idx["owner"][iid] for iid in support}):
                missing = [iid for iid in idx["q_interps"][qid] if iid not in support_raw]
                if missing:
                    out.append(finding("SUPPORT_INCOMPLETE", "HIGH", chapter, f"{eid} × {qid}: faltam {missing}",
                                       "Tocar uma pergunta obriga a declarar o suporte para todas as suas "
                                       "interpretações (EL-02) — o neutro também é uma decisão.",
                                       "Declarar S, C, X ou \"-\" para cada interpretação."))
            for iid, value in support.items():
                qid = idx["owner"][iid]
                if value == "X" and _policy(idx, qid) == "NEVER" and not str(raw.get("approval") or "").strip():
                    out.append(finding("EXCLUSION_WITHOUT_APPROVAL", "HIGH", chapter, f"{eid}.support.{iid}=X",
                                       "Excluir uma leitura de pergunta NEVER exige aprovação humana registrada.",
                                       "Trocar X por C ou registrar approval."))

        readings_raw = raw.get("readings")
        readings: dict[str, dict] = {}
        if readings_raw is not None and not isinstance(readings_raw, dict):
            out.append(finding("CONTRACT_INVALID", "HIGH", chapter, f"{eid}.readings",
                               "readings é um mapa interpretação → {reading, strength, corroborated_by}.",
                               "Corrigir readings."))
        for iid, reading in (readings_raw or {}).items() if isinstance(readings_raw, dict) else ():
            if support.get(iid) != "S":
                out.append(finding("READING_WITHOUT_SUPPORT", "LOW", chapter, f"{eid}.readings.{iid}",
                                   "Leitura só se escreve para interpretação que a evidência sustenta (S).",
                                   "Remover a leitura ou corrigir o suporte."))
                continue
            if not isinstance(reading, dict):
                out.append(finding("CONTRACT_INVALID", "HIGH", chapter, f"{eid}.readings.{iid}",
                                   "Leitura é um mapa {reading, strength, corroborated_by}.", "Corrigir."))
                continue
            out += _unknown_fields(reading, "reading", f"{eid}.readings.{iid}")
            if not str(reading.get("reading") or "").strip():
                out.append(finding("FIELD_MISSING", "HIGH", chapter, f"{eid}.readings.{iid}.reading",
                                   "A leitura diz, numa frase concreta, como este grupo usa a evidência.",
                                   "Escrever a leitura."))
            if reading.get("strength") not in STRENGTH_RANK:
                out.append(finding("INVALID_ENUM", "HIGH", chapter,
                                   f"{eid}.readings.{iid}.strength={reading.get('strength')!r}",
                                   "strength aceita WEAK, MEDIUM ou STRONG.", "Corrigir strength."))
            if reading.get("corroborated_by") is not None and not isinstance(reading.get("corroborated_by"), list):
                out.append(finding("CONTRACT_INVALID", "HIGH", chapter, f"{eid}.readings.{iid}.corroborated_by",
                                   "corroborated_by é uma lista de EVD-*.", "Corrigir."))
            readings[iid] = reading

        rows.append({
            "id": eid, "raw": raw, "chapter": chapter, "active": status != "RETIRED",
            "support": support, "readings": readings, "source": source, "role": role,
        })
    return rows, out


def s_interps(row: dict, idx: dict, qid: str) -> list[str]:
    return [iid for iid in idx["q_interps"][qid] if row["support"].get(iid) == "S"]


def double_questions(row: dict, idx: dict) -> list[str]:
    """Perguntas em que esta linha é dupla evidência (projeção, 13.1)."""
    touched = sorted({idx["owner"][iid] for iid in row["support"]})
    return [qid for qid in touched if len(s_interps(row, idx, qid)) >= 2]


def check_narrators(canon: dict, rows_by_id: dict, anchor_ctx, ledger) -> tuple[list[dict], list[dict]]:
    out: list[dict] = []
    narrators: list[dict] = []
    characters = {c.get("id") for c in as_list((ledger or {}).get("characters")) if isinstance(c, dict)}
    seen: set[str] = set()
    for raw in as_list(canon.get("narrators")):
        if not isinstance(raw, dict):
            out.append(finding("CONTRACT_INVALID", "HIGH", None, repr(raw), "Narrador precisa ser um mapa.",
                               "Corrigir a entrada."))
            continue
        nid = raw.get("id")
        out += _unknown_fields(raw, "narrator", str(nid))
        if not NARRATOR_ID_RE.match(str(nid)) or nid in seen:
            out.append(finding("NARRATOR_INVALID", "HIGH", None, f"narrators.id={nid!r}",
                               "Id de narrador segue NRL-<MAIÚSCULAS> e é único.", "Corrigir o id."))
            continue
        seen.add(nid)
        voice = raw.get("voice")
        if voice != "NARRATOR" and not CHARACTER_ID_RE.match(str(voice)):
            out.append(finding("NARRATOR_INVALID", "HIGH", None, f"{nid}.voice={voice!r}",
                               "voice é NARRATOR ou um CHR-*.", "Corrigir voice."))
        elif CHARACTER_ID_RE.match(str(voice)) and ledger is not None and voice not in characters:
            out.append(finding("UNKNOWN_REFERENCE", "HIGH", None, f"{nid}.voice={voice}",
                               "O personagem citado não existe no ledger.", "Corrigir voice."))
        if not str(raw.get("unreliability") or "").strip():
            out.append(finding("FIELD_MISSING", "HIGH", None, f"{nid}.unreliability",
                               "Declarar em quê esta voz não é confiável.", "Escrever unreliability."))
        chapters: set[int] | None = None
        scopes = as_list(raw.get("scope"))
        if not scopes:
            out.append(finding("FIELD_MISSING", "HIGH", None, f"{nid}.scope",
                               "Não confiabilidade tem escopo: narrador não confiável não é desculpa universal.",
                               "Declarar scope (TURN:/SCENE:/LEDGER:EV-*)."))
        elif anchor_ctx is not None:
            chapters = set()
            for scope in scopes:
                result = cvc.resolve_anchor(scope, anchor_ctx, mode="plan") or {}
                if not result.get("ok") or result.get("chapter") is None:
                    out.append(finding("NARRATOR_SCOPE_UNRESOLVED", "HIGH", None, f"{nid}.scope={scope}",
                                       "O escopo não resolve para um capítulo.", "Corrigir o escopo."))
                else:
                    chapters.add(result["chapter"])
        tells = as_list(raw.get("tells"))
        if not tells:
            out.append(finding("UNRELIABILITY_WITHOUT_TELL", "MEDIUM", None, nid,
                               "Toda não confiabilidade deixa ao menos uma pista percebível (34).",
                               "Declarar tells com EVD-* que permitam desconfiar da voz."))
        for tell in tells:
            if tell not in rows_by_id:
                out.append(finding("UNKNOWN_REFERENCE", "HIGH", None, f"{nid}.tells={tell}",
                                   "A evidência citada não existe.", "Corrigir a referência."))
        narrators.append({"id": nid, "voice": voice, "chapters": chapters})
    return narrators, out


def check_evidence_balance(idx: dict, rows: list[dict], cfg: dict) -> list[dict]:
    out: list[dict] = []
    active = [r for r in rows if r["active"]]
    counts = {iid: {"S": 0, "C": 0, "X": 0} for iid in idx["owner"]}
    for row in active:
        for iid, value in row["support"].items():
            if value in counts[iid]:
                counts[iid][value] += 1
        if row["support"] and "S" not in row["support"].values():
            out.append(finding("EVIDENCE_WITHOUT_SUPPORT", "MEDIUM", row["chapter"], row["id"],
                               "Evidência que não sustenta nenhuma leitura é textura mal registrada (TG-04).",
                               "Tirar a linha do canon (detalhe estético não é evidência) ou declarar o que ela "
                               "sustenta."))
        for qid in sorted({idx["owner"][iid] for iid in row["support"]}):
            interps = idx["q_interps"][qid]
            x_count = sum(1 for iid in interps if row["support"].get(iid) == "X")
            if _policy(idx, qid) == "NEVER" and len(interps) >= 2 and x_count >= len(interps) - 1:
                out.append(finding("EVIDENCE_COLLAPSES_QUESTION", "BLOCKER", row["chapter"],
                                   f"{row['id']} × {qid}: X={x_count}",
                                   "Nenhuma evidência exclui todas as leituras de uma pergunta NEVER menos uma (EL-05).",
                                   "Trocar exclusões por complicações (C)."))

    for qid, q in idx["questions"].items():
        policy = q.get("resolution_policy")
        interps = idx["q_interps"][qid]
        minimum = cfg["min_support_resolved"] if policy == "RESOLVED_AT" else cfg["min_support"]
        for iid in interps:
            s_count = counts[iid]["S"]
            if s_count == 0:
                out.append(finding("INTERPRETATION_WITHOUT_EVIDENCE", "HIGH", None, iid,
                                   "Interpretação sem nenhuma evidência que a sustente é declaração vazia (TG-03).",
                                   "Planejar evidências ou remover a interpretação."))
            elif s_count < minimum:
                out.append(finding("EVIDENCE_STARVED", "MEDIUM", None, f"{iid}: S={s_count}",
                                   f"Interpretação precisa de ao menos {minimum} evidências de suporte (EL-04).",
                                   "Planejar mais evidências para esta leitura."))
            if policy in SEED_POLICIES and s_count > 0 and counts[iid]["C"] == 0:
                out.append(finding("INTERPRETATION_UNCHALLENGED", "MEDIUM", None, iid,
                                   "Toda leitura de pergunta aberta é complicada ao menos uma vez (EL-04).",
                                   "Planejar uma evidência que incomode esta leitura."))
        if policy == "NEVER" and len(interps) >= 2:
            viable = [iid for iid in interps if counts[iid]["X"] == 0]
            minimum_viable = _min_viable(q, len(interps))
            if len(viable) < minimum_viable:
                out.append(finding("QUESTION_COLLAPSED", "BLOCKER", None, f"{qid}: viáveis={viable}",
                                   f"Ao fim, ao menos {minimum_viable} leituras seguem sem exclusão (EL-05).",
                                   "Retirar exclusões."))
        if policy in SEED_POLICIES:
            supported = [counts[iid]["S"] for iid in interps if counts[iid]["X"] == 0 and counts[iid]["S"] > 0]
            if len(supported) >= 2 and max(supported) / min(supported) > cfg["max_support_ratio"]:
                out.append(finding("INTERPRETATION_DOMINANCE", "MEDIUM", None,
                                   f"{qid}: S={ {iid: counts[iid]['S'] for iid in interps} }",
                                   f"Nenhuma leitura tem mais que {cfg['max_support_ratio']}× o suporte da menos "
                                   "sustentada (EL-06).", "Rebalancear o suporte."))
    return out


def check_double_evidence(idx: dict, rows: list[dict], rows_by_id: dict, cfg: dict) -> list[dict]:
    out: list[dict] = []
    active = [r for r in rows if r["active"]]
    doubles_per_question: dict[str, int] = defaultdict(int)
    tilt: dict[str, dict[str, int]] = {qid: defaultdict(int) for qid in idx["questions"]}
    doubles_per_chapter: dict[int, list[str]] = defaultdict(list)

    for row in rows:
        for iid, reading in row["readings"].items():
            corroborators = reading.get("corroborated_by") if isinstance(reading.get("corroborated_by"), list) else []
            valid = []
            for other in corroborators:
                target = rows_by_id.get(other)
                if target is None:
                    out.append(finding("UNKNOWN_REFERENCE", "HIGH", row["chapter"],
                                       f"{row['id']}.readings.{iid}.corroborated_by={other}",
                                       "A evidência citada não existe.", "Corrigir a referência."))
                elif other != row["id"] and target["active"] and target["support"].get(iid) == "S":
                    valid.append(other)
            if not valid:
                out.append(finding("READING_UNCORROBORATED", "MEDIUM", row["chapter"], f"{row['id']}.readings.{iid}",
                                   "Cada leitura se apoia em outro elemento do texto: corroborated_by cita ao menos "
                                   "uma evidência distinta que sustenta a mesma interpretação (DE-04).",
                                   "Declarar a evidência que corrobora esta leitura."))

    for row in active:
        doubles = double_questions(row, idx)
        if doubles and row["chapter"] is not None:
            doubles_per_chapter[row["chapter"]].append(row["id"])
        for qid in doubles:
            doubles_per_question[qid] += 1
            sides = s_interps(row, idx, qid)
            missing = [iid for iid in sides if iid not in row["readings"]]
            if missing:
                out.append(finding("DOUBLE_EVIDENCE_WITHOUT_READING", "HIGH", row["chapter"],
                                   f"{row['id']} × {qid}: sem leitura para {missing}",
                                   "Dupla evidência escreve como cada grupo a usa: marcar S em duas colunas sem "
                                   "leitura concreta é desejo do planejador (DE-01).",
                                   "Escrever readings para cada interpretação sustentada."))
            weak = [iid for iid in sides if iid in row["readings"]
                    and STRENGTH_RANK.get(row["readings"][iid].get("strength"), -1) < STRENGTH_RANK["MEDIUM"]]
            if weak:
                out.append(finding("DOUBLE_EVIDENCE_WEAK_SIDE", "HIGH", row["chapter"], f"{row['id']} × {qid}: {weak}",
                                   "As leituras de uma dupla evidência são ao menos MEDIUM (DE-02).",
                                   "Fortalecer a leitura fraca na cena ou rebaixar para evidência simples."))
            strong = [iid for iid in sides if row["readings"].get(iid, {}).get("strength") == "STRONG"]
            if 0 < len(strong) < len(sides):
                for iid in strong:
                    tilt[qid][iid] += 1

    for qid, q in idx["questions"].items():
        if q.get("resolution_policy") != "NEVER":
            continue
        if doubles_per_question[qid] < cfg["min_double_evidence"]:
            out.append(finding("DOUBLE_EVIDENCE_SCARCE", "MEDIUM", None, f"{qid}: duplas={doubles_per_question[qid]}",
                               f"Pergunta NEVER tem ao menos {cfg['min_double_evidence']} duplas evidências (DE-05).",
                               "Planejar gestos que sustentem leituras incompatíveis ao mesmo tempo."))
        only_strong = [tilt[qid][iid] for iid in idx["q_interps"][qid]]
        if only_strong and max(only_strong) - min(only_strong) > cfg["max_double_tilt"]:
            out.append(finding("DOUBLE_EVIDENCE_TILTED", "MEDIUM", None,
                               f"{qid}: só-STRONG={ {iid: tilt[qid][iid] for iid in idx['q_interps'][qid]} }",
                               f"Duplas em que só um lado é STRONG diferem no máximo {cfg['max_double_tilt']} entre "
                               "as leituras (DE-03).", "Rebalancear a força das leituras."))
    for chapter, ids in sorted(doubles_per_chapter.items()):
        if len(ids) > cfg["max_double_per_chapter"]:
            out.append(finding("DOUBLE_EVIDENCE_CLUSTERED", "LOW", chapter, f"cap. {chapter}: {ids}",
                               f"No máximo {cfg['max_double_per_chapter']} duplas evidências por capítulo: "
                               "aglomerado vira charada (DE-06).", "Distribuir as duplas pela obra."))
    return out


def check_testimony(rows: list[dict], narrators: list[dict]) -> list[dict]:
    """EL-08: testemunho de personagem que sustenta uma leitura precisa de voz
    declarada em narrators[] ou de complicação vinda de outra fonte."""
    out: list[dict] = []
    voices = {n["voice"] for n in narrators}
    active = [r for r in rows if r["active"]]
    for row in active:
        source = row["source"]
        if not CHARACTER_ID_RE.match(str(source)) or source in voices:
            continue
        uncovered = [
            iid for iid, value in row["support"].items() if value == "S"
            and not any(other["source"] != source and other["support"].get(iid) == "C" for other in active)
        ]
        if uncovered:
            out.append(finding("TESTIMONY_UNQUALIFIED", "MEDIUM", row["chapter"], f"{row['id']} ({source}): {uncovered}",
                               "A leitura depende da palavra de um personagem sem que a obra dê como desconfiar dela.",
                               "Declarar a voz em narrators[] ou planejar contraevidência de outra fonte."))
    return out


def check_red_herrings(idx: dict, rows: list[dict], rows_by_id: dict, narrators: list[dict], anchor_ctx,
                       cfg: dict) -> list[dict]:
    out: list[dict] = []
    active = [r for r in rows if r["active"]]
    herrings = [r for r in active if r["role"] == "RED_HERRING"]
    for row in herrings:
        eid, chapter = row["id"], row["chapter"]
        fair = row["raw"].get("fair_herring")
        if not isinstance(fair, dict):
            out.append(finding("FIELD_MISSING", "HIGH", chapter, f"{eid}.fair_herring",
                               "Red herring declara por que é justo (17.1).", "Declarar fair_herring."))
            continue
        out += _unknown_fields(fair, "fair_herring", f"{eid}.fair_herring")
        points = fair.get("points_toward")
        if row["support"].get(points) != "S":
            out.append(finding("RED_HERRING_INVALID", "HIGH", chapter, f"{eid}.points_toward={points!r}",
                               "O red herring aponta para uma interpretação que a própria evidência sustenta.",
                               "Corrigir points_toward ou o suporte."))

        cause = fair.get("in_world_cause")
        cause_ok = anchor_kind(cause) in CAUSE_ANCHOR_KINDS
        if cause_ok and anchor_ctx is not None:
            cause_ok = bool((cvc.resolve_anchor(cause, anchor_ctx, mode="plan") or {}).get("ok"))
        if not cause_ok:
            out.append(finding("RED_HERRING_WITHOUT_CAUSE", "HIGH", chapter, f"{eid}.in_world_cause={cause!r}",
                               "O gesto enganoso tem causa dentro do mundo (GT/evento/regra/documento), não só a "
                               "intenção de enganar o leitor (RH-01).",
                               "Ancorar em LEDGER:GT-*/EV-*, RULE:, DOC: ou CANON:."))

        reveal = fair.get("survives_reveal")
        reveal_chapter = None
        if not reveal:
            out.append(finding("RED_HERRING_NOT_SURVIVING", "HIGH", chapter, f"{eid}.survives_reveal",
                               "Declarar onde a revelação acontece e o gesto continua verdadeiro (RH-02).",
                               "Declarar survives_reveal."))
        elif anchor_ctx is not None:
            result = cvc.resolve_anchor(reveal, anchor_ctx, mode="plan") or {}
            reveal_chapter = result.get("chapter") if result.get("ok") else None
            if reveal_chapter is None or (chapter is not None and reveal_chapter <= chapter):
                out.append(finding("RED_HERRING_NOT_SURVIVING", "HIGH", chapter, f"{eid}.survives_reveal={reveal}",
                                   "A revelação que desfaz o red herring resolve e vem depois dele (RH-02).",
                                   "Corrigir survives_reveal."))

        if row["source"] == "NARRATOR":
            covered = any(n["voice"] == "NARRATOR" and (n["chapters"] is None or chapter in n["chapters"])
                          for n in narrators)
            if not covered:
                out.append(finding("NARRATOR_LIE", "BLOCKER", chapter, eid,
                                   "Red herring apoiado na palavra do narrador confiável é fraude autoral (RH-03).",
                                   "Atribuir a um personagem, a um documento, ou declarar o narrador não confiável "
                                   "com escopo e pista."))

        counters = [c for c in as_list(fair.get("counter_available_before")) if c in rows_by_id]
        fair_counters = [
            c for c in counters
            if rows_by_id[c]["support"].get(points) == "C" and rows_by_id[c]["active"]
            and (reveal_chapter is None or rows_by_id[c]["chapter"] is None or rows_by_id[c]["chapter"] < reveal_chapter)
        ]
        for missing in [c for c in as_list(fair.get("counter_available_before")) if c not in rows_by_id]:
            out.append(finding("UNKNOWN_REFERENCE", "HIGH", chapter, f"{eid}.counter_available_before={missing}",
                               "A evidência citada não existe.", "Corrigir a referência."))
        if not fair_counters:
            out.append(finding("RED_HERRING_UNFAIR", "HIGH", chapter, f"{eid}.counter_available_before={counters}",
                               "O leitor atento pode desconfiar antes da revelação: ao menos uma evidência anterior "
                               "complica (C) a leitura para onde o red herring aponta (RH-04).",
                               "Planejar a contraevidência justa antes da revelação."))
        if fair.get("after_function") not in AFTER_FUNCTIONS:
            out.append(finding("RED_HERRING_ORPHAN", "MEDIUM", chapter, f"{eid}.after_function={fair.get('after_function')!r}",
                               f"Depois de desmentido, o red herring ainda serve: {', '.join(sorted(AFTER_FUNCTIONS))} (RH-05).",
                               "Declarar a função posterior."))
    if active and len(herrings) / len(active) > cfg["max_red_herring_share"]:
        out.append(finding("RED_HERRING_EXCESS", "MEDIUM", None, f"{len(herrings)}/{len(active)}",
                           f"No máximo {cfg['max_red_herring_share']:.0%} das evidências são red herrings: acima "
                           "disso o livro vira armadilha (RH-07).", "Converter red herrings em pistas reais."))
    return out


def check_observables(idx: dict, rows: list[dict], registry, book_spec, cfg: dict) -> list[dict]:
    """EL-03: o observável descreve percepção; nunca enuncia uma tese de pergunta
    NEVER, uma inferência proibida ou um termo do léxico de resposta da obra."""
    out: list[dict] = []
    living_theory = living_theory_features(book_spec).get("living_theory")
    lexicon = as_list(living_theory.get("answer_lexicon")) if isinstance(living_theory, dict) else []
    prohibited = [p for p in as_list((registry or {}).get("prohibited_inferences")) if isinstance(p, dict)]
    threshold, min_words = cfg["thesis_overlap_threshold"], cfg["min_content_words_for_overlap"]
    never_interps = [iid for iid, qid in sorted(idx["owner"].items()) if _policy(idx, qid) == "NEVER"]
    for row in rows:
        observable = str(row["raw"].get("observable") or "")
        if not observable:
            continue
        hits = [f"léxico: {term}" for term in lexicon if term_hit(term, observable)]
        hits += [f"tese: {iid}" for iid in never_interps
                 if containment(idx["thesis"][iid], observable, min_words) >= threshold]
        for pro in prohibited:
            terms = as_list(pro.get("match"))
            if (any(term_hit(t, observable) for t in terms) if terms
                    else containment(pro.get("statement") or "", observable, min_words) >= threshold):
                hits.append(f"inferência proibida: {pro.get('id')}")
        if hits:
            out.append(finding("OBSERVABLE_STATES_ANSWER", "HIGH", row["chapter"], f"{row['id']}: {hits}",
                               "O observável descreve o que se percebe, nunca a resposta (EL-03).",
                               "Reescrever como percepção: gesto, objeto, tempo, ausência."))
    return out


def check_signal_noise(rows: list[dict], book_spec, chapter_architecture, cfg: dict) -> list[dict]:
    """16.3: controles estruturais de sinal/ruído. O controle que importa de verdade
    é empírico (forum, Slice 6); estes impedem o excesso óbvio."""
    out: list[dict] = []
    active = [r for r in rows if r["active"]]
    if not active:
        return out
    per_chapter: dict[int, list[str]] = defaultdict(list)
    for row in active:
        if row["chapter"] is not None:
            per_chapter[row["chapter"]].append(row["id"])
    for chapter, ids in sorted(per_chapter.items()):
        if len(ids) > cfg["max_evidence_per_chapter"]:
            out.append(finding("EVIDENCE_OVERDENSE", "MEDIUM", chapter, f"cap. {chapter}: {ids}",
                               f"No máximo {cfg['max_evidence_per_chapter']} evidências por capítulo: acima disso a "
                               "cena vira catálogo de pistas (16.3).", "Mover ou cortar evidências."))
    noticeable = [r["id"] for r in active if r["raw"].get("salience") == "NOTICEABLE"]
    if len(noticeable) / len(active) > cfg["max_noticeable_share"]:
        out.append(finding("THEORY_BAIT_SALIENCE", "MEDIUM", None, f"{len(noticeable)}/{len(active)}: {noticeable}",
                           f"No máximo {cfg['max_noticeable_share']:.0%} das evidências são perceptíveis na primeira "
                           "leitura: pista demais em evidência ensina a gramática do motor (16.3, LT-LAW-05).",
                           "Rebaixar saliência para SUPPORTING/TEXTURE."))
    reread = [r["id"] for r in active if r["raw"].get("discoverable_on") == "REREAD"]
    if len(reread) / len(active) < cfg["min_reread_only_share"]:
        out.append(finding("REREAD_LAYER_THIN", "MEDIUM", None, f"{len(reread)}/{len(active)}",
                           f"Ao menos {cfg['min_reread_only_share']:.0%} das evidências existem só para quem relê (16.3).",
                           "Planejar evidências que só ganham sentido na releitura."))
    chapter_count = (book_spec or {}).get("metadata", {}).get("chapter_count") if isinstance(book_spec, dict) else None
    if not isinstance(chapter_count, int) and chapter_architecture:
        chapter_count = len(chapter_architecture)
    if isinstance(chapter_count, int) and chapter_count > 0 and per_chapter:
        share = len(per_chapter) / chapter_count
        if share > cfg["max_evidence_chapter_share"]:
            out.append(finding("EVIDENCE_EVERYWHERE", "MEDIUM", None, f"{len(per_chapter)}/{chapter_count} capítulos",
                               f"No máximo {cfg['max_evidence_chapter_share']:.0%} dos capítulos com evidência "
                               "planejada: capítulo sem pista é respiração (16.3).",
                               "Concentrar evidências e deixar capítulos só para a história."))
    return out


# --- fronteira com o canon ---------------------------------------------------

def check_registry_boundary(idx: dict, registry: dict, cfg: dict) -> list[dict]:
    out: list[dict] = []
    threshold, min_words = cfg["thesis_overlap_threshold"], cfg["min_content_words_for_overlap"]
    for qid, q in idx["questions"].items():
        policy = q.get("resolution_policy")
        match = CANON_REF_RE.match(str(q.get("unknown_ref") or ""))
        if match:
            node = find_by_id(registry, match.group(1))
            if node is None:
                out.append(finding("UNKNOWN_REF_INVALID", "HIGH", None, f"{qid}.unknown_ref={q.get('unknown_ref')}",
                                   "A incógnita citada não existe no CANON_REGISTRY (CI-04).",
                                   "Registrar a incógnita via CANON_PROPOSALS ou corrigir a referência."))
            elif policy == "NEVER" and node.get("status") != MUST_REMAIN_UNKNOWN:
                out.append(finding("UNKNOWN_REF_INVALID", "HIGH", None,
                                   f"{qid}.unknown_ref={q.get('unknown_ref')} status={node.get('status')!r}",
                                   f"Pergunta NEVER aponta incógnita com status {MUST_REMAIN_UNKNOWN} (CI-04).",
                                   "Corrigir o status no registry (CANON_GUARDIAN) ou a política da pergunta."))
        for ref in as_list(q.get("prohibited_refs")):
            ref_match = CANON_REF_RE.match(str(ref))
            if ref_match and find_by_id(registry, ref_match.group(1)) is None:
                out.append(finding("UNKNOWN_REFERENCE", "HIGH", None, f"{qid}.prohibited_refs={ref}",
                                   "A inferência proibida citada não existe no CANON_REGISTRY.",
                                   "Registrar a inferência via CANON_PROPOSALS ou corrigir a referência."))

    prohibited = [p for p in as_list(registry.get("prohibited_inferences")) if isinstance(p, dict)]
    for iid, qid in sorted(idx["owner"].items()):
        thesis = idx["thesis"][iid]
        for pro in prohibited:
            terms = as_list(pro.get("match"))
            if terms:
                hit = any(term_hit(term, thesis) for term in terms)
            else:
                hit = containment(pro.get("statement") or "", thesis, min_words) >= threshold
            if hit:
                out.append(finding("PROHIBITED_INTERPRETATION", "BLOCKER", None, f"{iid} ~ {pro.get('id')}",
                                   "A interpretação declara uma inferência que o canon proíbe (CI-05).",
                                   "Remover a interpretação; os limites da ambiguidade são canon."))

    never_interps = [iid for iid, qid in sorted(idx["owner"].items()) if _policy(idx, qid) == "NEVER"]
    for fact_id, fact in iter_facts(registry):
        for iid in never_interps:
            if containment(idx["thesis"][iid], fact, min_words) >= threshold:
                out.append(finding("THEORY_PROMOTED_TO_FACT", "BLOCKER", None, f"{iid} → registry {fact_id}",
                                   "A tese de uma pergunta NEVER aparece como fato do registry (CI-02).",
                                   "Retirar o fato do registry; interpretação nunca vira canon."))
    return out


def check_ledger_boundary(idx: dict, ledger: dict, cfg: dict) -> list[dict]:
    out: list[dict] = []
    threshold, min_words = cfg["thesis_overlap_threshold"], cfg["min_content_words_for_overlap"]
    events = [e for e in as_list(ledger.get("events")) if isinstance(e, dict)]
    event_ids = {e.get("id") for e in events}
    beliefs = {b.get("id"): b for b in as_list(ledger.get("beliefs")) if isinstance(b, dict)}
    revised = {rb for e in events for rb in as_list((e.get("beliefs") or {}).get("revises"))}
    ground_truths = {
        gt.get("id"): gt
        for character in as_list(ledger.get("characters")) if isinstance(character, dict)
        for gt in as_list(character.get("ground_truth")) if isinstance(gt, dict)
    }
    never_interps = [iid for iid, qid in sorted(idx["owner"].items()) if _policy(idx, qid) == "NEVER"]

    for event in events:
        chapter = event.get("chapter")
        for token in as_list(event.get("caused_by")):
            if THEORY_ID_RE.match(str(token)) or token in idx["owner"] or token in idx["questions"]:
                out.append(finding("THEORY_AS_CAUSE", "BLOCKER", chapter, f"{event.get('id')}.caused_by={token}",
                                   "Pergunta, interpretação ou evidência nunca é causa de evento (CI-01).",
                                   "Substituir por GT-* de participante ou EV-* anterior."))
        for fact in as_list(event.get("facts")):
            for iid in never_interps:
                if containment(idx["thesis"][iid], fact, min_words) >= threshold:
                    out.append(finding("THEORY_PROMOTED_TO_FACT", "BLOCKER", chapter,
                                       f"{iid} → {event.get('id')}.facts",
                                       "A tese de uma pergunta NEVER aparece como fato do ledger (CI-02).",
                                       "Reescrever o fato como o que objetivamente ocorre, sem decidir a leitura."))

    for qid, q in idx["questions"].items():
        policy = q.get("resolution_policy")
        match = LEDGER_EVENT_REF_RE.match(str(q.get("resolved_at") or ""))
        if policy == "RESOLVED_AT" and match and match.group(1) not in event_ids:
            out.append(finding("RESOLUTION_ANCHOR_INVALID", "HIGH", None, f"{qid}.resolved_at={q.get('resolved_at')}",
                               "O evento de revelação citado não existe no ledger.", "Corrigir a referência."))
        if policy != "NEVER":
            continue
        for rb_id in as_list(q.get("ledger_beliefs")):
            belief = beliefs.get(rb_id)
            if belief is None:
                out.append(finding("UNKNOWN_REFERENCE", "HIGH", None, f"{qid}.ledger_beliefs={rb_id}",
                                   "A crença citada não existe em beliefs[] do ledger.", "Corrigir a referência."))
                continue
            problems = []
            if str(belief.get("truth")) != OPEN_BELIEF_TRUTH:
                problems.append(f"truth={belief.get('truth')!r}")
            if belief.get("left_open") is not True:
                problems.append(f"left_open={belief.get('left_open')!r}")
            if rb_id in revised:
                problems.append("revisada por beliefs.revises")
            if problems:
                out.append(finding("LEDGER_BELIEF_CLOSES_NEVER_QUESTION", "BLOCKER", None,
                                   f"{qid} × {rb_id}: {', '.join(problems)}",
                                   f"Crença ligada a pergunta NEVER tem truth \"{OPEN_BELIEF_TRUTH}\", left_open: "
                                   "true e nunca é revisada (AD-03).",
                                   "Corrigir a crença no ledger ou desligá-la da pergunta."))
        for gt_id in as_list(q.get("ledger_ground_truths")):
            gt = ground_truths.get(gt_id)
            if gt is None:
                out.append(finding("UNKNOWN_REFERENCE", "HIGH", None, f"{qid}.ledger_ground_truths={gt_id}",
                                   "A Ground Truth citada não existe no ledger.", "Corrigir a referência."))
                continue
            if gt.get("reader_access") != NEVER_ACCESS:
                out.append(finding("GROUND_TRUTH_HOLDS_ANSWER", "HIGH", None,
                                   f"{qid} × {gt_id}: reader_access={gt.get('reader_access')!r}",
                                   "GT que sustenta uma pergunta NEVER nunca chega ao leitor (AD-04).",
                                   "Definir reader_access: NEVER."))
            if gt.get("kind") != AMBIGUITY_GT_KIND:
                sides = [iid for iid in idx["q_interps"][qid]
                         if containment(idx["thesis"][iid], gt.get("statement") or "", min_words) >= threshold]
                if len(sides) == 1:
                    out.append(finding("GROUND_TRUTH_HOLDS_ANSWER", "HIGH", None,
                                       f"{qid} × {gt_id}: kind={gt.get('kind')} descreve {sides[0]}",
                                       "A GT enuncia uma das teses: o motor guardaria a resposta (AD-04). "
                                       "Use GT CONTRADICTION que descreva a inseparabilidade das leituras.",
                                       "Reescrever como GT CONTRADICTION."))
    return out


def check_missing_context(idx: dict, registry, ledger, chapter_architecture) -> list[dict]:
    out: list[dict] = []
    if registry is None:
        out.append(finding("CONTEXT_MISSING", "HIGH", None, "canon/CANON_REGISTRY.yaml",
                           "Em runtime, o canon interpretativo é validado contra o registry (incógnitas, "
                           "inferências proibidas, fatos).", "Executar T018_CANON_REGISTRY antes deste gate."))
    if chapter_architecture is None:
        out.append(finding("CONTEXT_MISSING", "HIGH", None, "book/chapter_architecture.yaml",
                           "Em runtime, evidências são localizadas contra a arquitetura de capítulos.",
                           "Recompor o runtime a partir do pacote do livro."))
    if ledger is None:
        for qid, q in idx["questions"].items():
            refs = as_list(q.get("ledger_beliefs")) + as_list(q.get("ledger_ground_truths"))
            if refs or q.get("resolution_policy") == "RESOLVED_AT":
                out.append(finding("LEDGER_REFERENCE_WITHOUT_LEDGER", "HIGH", None, qid,
                                   "A pergunta cita o ledger causal, mas este runtime não tem "
                                   "canon/CAUSAL_LEDGER.yaml.",
                                   "Ligar features.causal_ledger ou remover as referências ao ledger."))
    return out


# --- orquestração ------------------------------------------------------------

def analyze(canon, registry: dict | None = None, ledger: dict | None = None,
            book_spec: dict | None = None, immutable_rules: list | None = None,
            chapter_architecture: list | None = None, protected_scenes: list | None = None,
            bibles: dict | None = None, config: dict | None = None,
            runtime_mode: bool = False) -> tuple[list[dict], dict]:
    """Roda todas as regras e devolve (achados, modelo). O modelo alimenta as
    consultas de observabilidade sem recalcular nada."""
    if not isinstance(canon, dict):
        return [finding("CONTRACT_INVALID", "BLOCKER", None, type(canon).__name__,
                        "O canon interpretativo precisa ser um mapa YAML.", "Corrigir o arquivo.")], {}
    cfg, findings = resolve_config(canon, book_spec, config)
    findings += check_contract(canon)
    idx, index_findings = build_index(canon)
    findings += index_findings
    findings += check_questions(idx, cfg, immutable_rules)
    findings += check_seed_limits(idx, cfg)
    findings += check_partitions(canon, idx, cfg)
    graph, graph_findings = build_relation_graph(canon, idx)
    findings += graph_findings
    findings += check_relation_consistency(graph, idx)
    findings += check_graph_forces_resolution(graph, idx)
    findings += check_hidden_answer(canon)

    anchor_ctx = build_anchor_context(registry, ledger, immutable_rules, chapter_architecture,
                                      protected_scenes, bibles)
    rows, evidence_findings = build_evidence(canon, idx, anchor_ctx, ledger, book_spec)
    findings += evidence_findings
    rows_by_id = {row["id"]: row for row in rows}
    narrators, narrator_findings = check_narrators(canon, rows_by_id, anchor_ctx, ledger)
    findings += narrator_findings
    if canon.get("evidence") is not None:
        findings += check_evidence_balance(idx, rows, cfg)
        findings += check_double_evidence(idx, rows, rows_by_id, cfg)
        findings += check_testimony(rows, narrators)
        findings += check_red_herrings(idx, rows, rows_by_id, narrators, anchor_ctx, cfg)
        findings += check_observables(idx, rows, registry, book_spec, cfg)
        findings += check_signal_noise(rows, book_spec, chapter_architecture, cfg)

    if registry is not None:
        findings += check_registry_boundary(idx, registry, cfg)
    if ledger is not None:
        findings += check_ledger_boundary(idx, ledger, cfg)
    if runtime_mode:
        findings += check_missing_context(idx, registry, ledger, chapter_architecture)
    model = {"cfg": cfg, "idx": idx, "rows": rows, "narrators": narrators, "canon": canon,
             "book_spec": book_spec, "chapter_architecture": chapter_architecture}
    return findings, model


def validate(canon, **kwargs) -> list[dict]:
    return analyze(canon, **kwargs)[0]


# --- consultas de observabilidade (seção 32) --------------------------------

def _row_entry(row: dict, iid: str | None = None) -> dict:
    entry = {"evidence": row["id"], "chapter": row["chapter"], "anchor": row["raw"].get("anchor"),
             "observable": row["raw"].get("observable")}
    if iid is not None and iid in row["readings"]:
        entry["reading"] = row["readings"][iid].get("reading")
        entry["strength"] = row["readings"][iid].get("strength")
    return entry


def ledger_report(model: dict, qid: str) -> dict:
    """--ledger Q-*: evidências por interpretação (S/C/X), com leituras."""
    idx = model["idx"]
    report = {"question": qid, "text": idx["questions"][qid].get("question"), "interpretations": {}}
    for iid in idx["q_interps"][qid]:
        buckets = {"thesis": idx["thesis"][iid], "S": [], "C": [], "X": []}
        for row in model["rows"]:
            value = row["support"].get(iid)
            if row["active"] and value in ("S", "C", "X"):
                buckets[value].append(_row_entry(row, iid))
        report["interpretations"][iid] = buckets
    return report


def double_report(model: dict, qid: str | None = None) -> dict:
    """--double [Q-*]: dupla evidência projetada por pergunta e por partição."""
    idx = model["idx"]
    active = [r for r in model["rows"] if r["active"]]
    questions = [qid] if qid else sorted(idx["questions"])
    report: dict = {"questions": {}, "partitions": {}}
    for q in questions:
        report["questions"][q] = [
            {**_row_entry(row), "sides": s_interps(row, idx, q)} for row in active if len(s_interps(row, idx, q)) >= 2
        ]
    for part in as_list(model["canon"].get("partitions")):
        if not isinstance(part, dict) or part.get("of") not in questions or not isinstance(part.get("sides"), dict):
            continue
        sides = {str(side): set(as_list(members)) for side, members in part["sides"].items()}
        placed = set().union(*sides.values()) if sides else set()
        entry = {"double": [], "only": {side: [] for side in sides},
                 "unassigned": sorted(set(idx["q_interps"].get(part["of"], [])) - placed)}
        for row in active:
            supported = {side for side, members in sides.items()
                         if any(row["support"].get(iid) == "S" for iid in members)}
            if len(supported) >= 2:
                entry["double"].append(row["id"])
            elif len(supported) == 1:
                entry["only"][next(iter(supported))].append(row["id"])
        report["partitions"][part.get("id")] = entry
    return report


def heatmap_report(model: dict) -> dict:
    """--heatmap: capítulo × pergunta, duplas por capítulo e limites de 16.3."""
    idx, cfg = model["idx"], model["cfg"]
    chapters: dict[int, dict] = {}
    for row in model["rows"]:
        if not row["active"] or row["chapter"] is None:
            continue
        cell = chapters.setdefault(row["chapter"], {"total": 0, "double": 0, "questions": defaultdict(int)})
        cell["total"] += 1
        cell["double"] += 1 if double_questions(row, idx) else 0
        for q in sorted({idx["owner"][iid] for iid in row["support"]}):
            cell["questions"][q] += 1
    book_spec = model.get("book_spec") or {}
    chapter_count = (book_spec.get("metadata") or {}).get("chapter_count") or len(model.get("chapter_architecture") or [])
    return {
        "chapter_count": chapter_count,
        "chapters_with_evidence": len(chapters),
        "limits": {k: cfg[k] for k in ("max_evidence_per_chapter", "max_double_per_chapter",
                                        "max_evidence_chapter_share")},
        "chapters": {n: {"total": c["total"], "double": c["double"], "questions": dict(c["questions"])}
                     for n, c in sorted(chapters.items())},
        "over_limit": sorted(n for n, c in chapters.items()
                             if c["total"] > cfg["max_evidence_per_chapter"] or c["double"] > cfg["max_double_per_chapter"]),
    }


# --- carga e CLI -------------------------------------------------------------

def load_runtime(runtime: Path) -> dict:
    def doc_list(path: Path, key: str):
        doc = optional_yaml(path)
        return as_list(doc.get(key)) if isinstance(doc, dict) else None

    return {
        "canon": optional_yaml(runtime / "canon" / "INTERPRETIVE_CANON.yaml"),
        "registry": optional_yaml(runtime / "canon" / "CANON_REGISTRY.yaml"),
        "ledger": optional_yaml(runtime / "canon" / "CAUSAL_LEDGER.yaml"),
        "book_spec": optional_yaml(runtime / "book" / "BOOK_SPEC.yaml"),
        "immutable_rules": doc_list(runtime / "book" / "immutable_rules.yaml", "rules"),
        "chapter_architecture": doc_list(runtime / "book" / "chapter_architecture.yaml", "chapters"),
        "protected_scenes": doc_list(runtime / "book" / "protected_scenes.yaml", "scenes"),
        "bibles": cvc.load_bibles(runtime),
    }


def render_report(findings: list[dict], source: str, context: dict) -> str:
    loaded = ", ".join(f"{name}={'sim' if present else 'não'}" for name, present in context.items())
    out = [
        "# Relatório do Canon Interpretativo\n\n",
        f"Fonte: `{source}`\n\n",
        f"Contexto carregado: {loaded}. Regras que dependem de fonte ausente não rodaram.\n\n",
        "Gerado por `engine/scripts/check_interpretive_canon.py` (Slices 1–2: modelo mínimo e Evidence Ledger). "
        "Ver docs/sdd/LIVING_THEORY_ENGINE_SDD_v0.1.md.\n\n",
    ]
    if not findings:
        out.append("Nenhum achado. Canon interpretativo consistente para as regras destes slices.\n")
        return "".join(out)
    counts: dict[str, int] = defaultdict(int)
    for f in findings:
        counts[f["severity"]] += 1
    out.append("| Severidade | Achados |\n|---|---:|\n")
    for sev in reversed(SEVERITY_ORDER):
        if counts.get(sev):
            out.append(f"| {sev} | {counts[sev]} |\n")
    out.append("\n")
    by_category: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        by_category[f["category"]].append(f)
    for category, items in by_category.items():
        out.append(f"## {category} ({len(items)})\n\n")
        for f in items:
            out.append(f"- **{f['severity']}** (cap. {f['chapter']}) — `{f['evidence']}`\n")
            out.append(f"  - {f['detail']}\n")
            out.append(f"  - Ação sugerida: {f['recommended_action']}\n")
        out.append("\n")
    return "".join(out)


def main() -> int:
    # Saída acentuada no console Windows (cp1252) quebrava subprocessos de teste
    # em outros validadores; aqui a saída é sempre UTF-8.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Validador determinístico do INTERPRETIVE_CANON.yaml (LIVING_THEORY_ENGINE).")
    parser.add_argument("--runtime", type=Path,
                        help="Raiz do runtime; lê canon/ (interpretativo, registry, ledger) e book/ "
                             "(BOOK_SPEC, immutable_rules, chapter_architecture, protected_scenes).")
    parser.add_argument("--canon", type=Path, help="Caminho direto para um INTERPRETIVE_CANON.yaml.")
    parser.add_argument("--registry", type=Path, help="CANON_REGISTRY.yaml (sobrescreve o do runtime).")
    parser.add_argument("--causal-ledger", type=Path, help="CAUSAL_LEDGER.yaml (sobrescreve o do runtime).")
    parser.add_argument("--book-spec", type=Path, help="BOOK_SPEC.yaml (limiares e léxico de features.living_theory).")
    parser.add_argument("--immutable-rules", type=Path, help="immutable_rules.yaml (resolve rule_ref).")
    parser.add_argument("--mode", choices=["plan"], default="plan",
                        help="Por ora só plan; realized/final entram no Slice 4.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--ledger", metavar="QUESTION_ID", help="Evidências por interpretação de uma pergunta.")
    parser.add_argument("--double", nargs="?", const="*", metavar="QUESTION_ID",
                        help="Dupla evidência projetada (todas as perguntas, ou uma) e por partição.")
    parser.add_argument("--heatmap", action="store_true", help="Capítulo × pergunta e limites de densidade.")
    args = parser.parse_args()

    if not args.runtime and not args.canon:
        parser.error("informe --runtime ou --canon")
    context = load_runtime(args.runtime) if args.runtime else {
        "canon": None, "registry": None, "ledger": None, "book_spec": None, "immutable_rules": None,
        "chapter_architecture": None, "protected_scenes": None, "bibles": None}
    canon_path = args.canon or (args.runtime / "canon" / "INTERPRETIVE_CANON.yaml")
    if args.canon:
        context["canon"] = optional_yaml(args.canon)
    if context["canon"] is None:
        print(f"INTERPRETIVE_CANON não encontrado: {canon_path}", file=sys.stderr)
        return 2
    for key, path in (("registry", args.registry), ("ledger", args.causal_ledger), ("book_spec", args.book_spec)):
        if path is not None:
            context[key] = optional_yaml(path)
    if args.immutable_rules is not None:
        rules_doc = optional_yaml(args.immutable_rules)
        context["immutable_rules"] = as_list(rules_doc.get("rules")) if isinstance(rules_doc, dict) else None

    canon = context.pop("canon")
    findings, model = analyze(canon, **context, runtime_mode=bool(args.runtime))

    if args.ledger or args.double or args.heatmap:
        wanted = args.ledger or (args.double if args.double not in (None, "*") else None)
        if wanted is not None and wanted not in model.get("idx", {}).get("questions", {}):
            print(f"pergunta desconhecida: {wanted}", file=sys.stderr)
            return 2
        if args.ledger:
            payload = ledger_report(model, args.ledger)
        elif args.double:
            payload = double_report(model, wanted)
        else:
            payload = heatmap_report(model)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    loaded = {name: context[name] is not None
              for name in ("registry", "ledger", "book_spec", "immutable_rules", "chapter_architecture")}
    if args.json:
        print(json.dumps({"context": loaded, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        report = render_report(findings, str(canon_path), loaded)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(report, encoding="utf-8")
            print(f"Relatório: {args.out}")
        else:
            print(report)

    counts: dict[str, int] = defaultdict(int)
    for f in findings:
        counts[f["severity"]] += 1
    print(f"\nTOTAL: {len(findings)} achado(s) "
          f"({', '.join(f'{v} {k}' for k, v in counts.items()) or 'nenhum'})", file=sys.stderr)
    return 1 if any(f["severity"] in BLOCKING for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
