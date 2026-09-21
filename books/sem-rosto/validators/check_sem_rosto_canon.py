"""Validador de junção do canon narrativo de SEM ROSTO.

Desenho: docs/sdd/SEM_ROSTO_CANONICAL_STORY_SYSTEM_SDD_v0.1.md. Este arquivo é da OBRA
(books/sem-rosto/validators/), não do motor: `engine/AGENTS.md` proíbe canon de obra em /engine.

Slice 1 — modo `package`: integridade dos seeds de books/sem-rosto/canon/.

- SR-SRC   dossiê pinado (sha256) e freeze aprovado por humano
- SR-CR    contrato, ids, enums, referências, incógnitas sem conteúdo, varredura de respostas,
           cobertura do dossiê §17 (incógnitas) e §21 (gates de escrita), aprovação dos seeds
- SR-ST-04 capacidade do sistema nunca vira instância sem aprovação
- SR-PV    proveniência: toda âncora §N[.N] existe no dossiê; nenhuma fonte improvisada
- SR-HL    locks com detectores resolvíveis; lock editado depois de aprovado

O validador não lê prosa neste slice e não guarda resposta de nada. Modos `plan`, `scene`,
`wave`, `final` e `regression` chegam nos Slices 2–4; as regras deles já estão no catálogo
(RULE_CATALOG) para que os locks possam citá-las, e o relatório diz quais ainda são planejadas.

Uso:
    python books/sem-rosto/validators/check_sem_rosto_canon.py --mode package [--canon books/sem-rosto/canon] [--json]

Sem dependências novas: biblioteca padrão + PyYAML (+ o validador do canon interpretativo do motor,
de onde vem a lista de chaves de resposta proibidas).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

HERE = Path(__file__).resolve()
PACKAGE_ROOT = HERE.parents[1]                       # books/sem-rosto  (ou runtime/<slug>/book)
DEFAULT_CANON = PACKAGE_ROOT / "canon"


def _find_engine_scripts() -> Path | None:
    for base in HERE.parents:
        for cand in (base / "engine" / "scripts", base / "scripts"):
            if (cand / "check_interpretive_canon.py").exists():
                return cand
    return None


ENGINE_SCRIPTS = _find_engine_scripts()
if ENGINE_SCRIPTS is not None and str(ENGINE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(ENGINE_SCRIPTS))

try:  # REUSE: a mesma definição de "chave de resposta" do canon interpretativo (AD-02)
    from check_interpretive_canon import HIDDEN_ANSWER_KEYS, normalize_key
    HIDDEN_KEYS_SOURCE = "engine:check_interpretive_canon"
except Exception:  # pragma: no cover - só quando o motor não está acessível
    HIDDEN_ANSWER_KEYS = {
        "truth", "answer", "correct", "correct_answer", "canonical_answer", "author_answer",
        "hidden_answer", "intended", "intended_reading", "true_nature", "real_identity",
        "resposta", "resposta_correta", "verdade",
    }

    def normalize_key(key) -> str:
        text = "".join(c for c in unicodedata.normalize("NFKD", str(key)) if not unicodedata.combining(c))
        return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    HIDDEN_KEYS_SOURCE = "fallback-local"

SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "BLOCKER"]
BLOCKING = {"HIGH", "BLOCKER"}
API_VERSION = "pedroarte.livingbooks/v1"

SEED_KINDS = {
    "CANON_RECORDS.seed.yaml": "SemRostoCanonRecords",
    "HARD_LOCKS.seed.yaml": "SemRostoHardLocks",
    "BOOK_GATES.seed.yaml": "SemRostoBookGates",
}
SEED_ROOT_FIELDS = {
    "SemRostoCanonRecords": {"apiVersion", "kind", "metadata", "records"},
    "SemRostoHardLocks": {"apiVersion", "kind", "metadata", "locks"},
    "SemRostoBookGates": {"apiVersion", "kind", "metadata", "book_gates", "series"},
}
METADATA_FIELDS = {"project_id", "version", "owner", "source", "approval"}
LOCK_SEEDS = {"HARD_LOCKS.seed.yaml", "BOOK_GATES.seed.yaml"}   # edição após aprovação = BLOCKER

# --- vocabulário fechado (SDD seções 12–13) ---------------------------------------------

DOMAINS = {
    "ABSOLUTE", "COFFER", "FACE", "CHILD_PROTOCOL", "VISITOR", "RETURNER", "JURISDICTION", "PULL",
    "TECHNOLOGY", "IDENTITY", "TATTOO", "ECONOMY", "BODY", "CHRONOLOGY", "ARCHIVE", "MANFRED", "SELKA",
    "NON_HUMAN", "EXPRESSION", "INTIMACY", "CONSENT", "AGE", "BOOK_CONTRACT", "CARTOGRAPHY_DEPENDENCY",
    "MYSTERY",
}
AUTHORITY_STATUSES = {
    "CANON_APPROVED", "CANON_PATCH_APPROVED", "CANON_UNKNOWN", "RESERVED", "SYSTEM_CAPABILITY",
    "CANON_PROPOSAL_REQUIRED", "PENDING_HUMAN_DECISION", "DEPRECATED_CANON", "SUPERSEDED",
}
EPISTEMIC_CLASSES = {
    "FACT", "OFFICIAL_CLAIM", "HISTORICAL_CLAIM", "RUMOR", "THEORY", "CHARACTER_BELIEF", "DISPUTED",
    "PARTIAL", "FALSE", "UNKNOWN",
}
BOOK_SCOPES = {"SERIES", "B1", "B2", "B3"}
READER_SCOPES = {"OPEN", "GATED", "NEVER"}
UNLOCK_POLICIES = {"B1_LOCKED", "NEVER", "CARTOGRAPHIC_DECISION", "HUMAN_DECISION"}
ENTITY_KINDS = {"HISTORICAL_PERSON", "FAMILY", "INSTITUTION", "UNSPECIFIED"}
PATCH_RE = re.compile(r"^R(?:[1-9]|1[01])$")
LOCK_SCOPES = {"SERIES", "B1"}
LOCK_MODES = {"STRUCTURAL", "LEXICAL_PREFILTER", "JUDGMENT"}
CEILINGS = {"UNOPENED", "OPEN", "EXPANDING", "THEORY", "PARTIALLY_RESOLVED"}
EARLIEST_REVEALS = {"B2", "B3", "FUTURE"}

# kind por prefixo; statuses e campos por kind
KIND_BY_PREFIX = [
    (re.compile(r"^CR-PHRASE-[A-Z0-9-]+$"), "PHRASE"),
    (re.compile(r"^CR-[A-Z0-9]+(?:-[A-Z0-9]+)*$"), "RULE"),
    (re.compile(r"^CAP-[A-Z0-9]+(?:-[A-Z0-9]+)*$"), "CAPABILITY"),
    (re.compile(r"^UNK-SR-[A-Z0-9]+(?:-[A-Z0-9]+)*$"), "UNKNOWN"),
    (re.compile(r"^PRO-SR-[A-Z0-9]+(?:-[A-Z0-9]+)*$"), "PROHIBITED_INFERENCE"),
    (re.compile(r"^(?:ENT|INST|FAM)-[A-Z0-9]+(?:-[A-Z0-9]+)*$"), "ENTITY"),
]
STATUSES_BY_KIND = {
    "RULE": {"CANON_APPROVED", "CANON_PATCH_APPROVED", "RESERVED", "CANON_PROPOSAL_REQUIRED",
             "PENDING_HUMAN_DECISION", "DEPRECATED_CANON", "SUPERSEDED"},
    "PHRASE": {"CANON_APPROVED"},
    "CAPABILITY": {"SYSTEM_CAPABILITY", "DEPRECATED_CANON", "SUPERSEDED"},
    "UNKNOWN": {"CANON_UNKNOWN", "SUPERSEDED"},
    "PROHIBITED_INFERENCE": {"CANON_APPROVED", "DEPRECATED_CANON", "SUPERSEDED"},
    "ENTITY": {"CANON_APPROVED", "PENDING_HUMAN_DECISION", "DEPRECATED_CANON", "SUPERSEDED"},
}
COMMON_FIELDS = {"id", "domain", "status", "source", "scope", "notes", "revision", "created_at", "updated_at",
                 "depends_on", "conflicts_with", "supersedes", "superseded_by", "human_approval_required"}
FIELDS_BY_KIND = {
    "RULE": COMMON_FIELDS | {"title", "statement", "epistemic_class", "lock", "patch", "reveal", "gates",
                             "system_capability_only", "map_refs", "components", "classes", "interval",
                             "name_status", "date", "temporal"},
    "PHRASE": COMMON_FIELDS | {"title", "statement", "epistemic_class", "usage"},
    "CAPABILITY": COMMON_FIELDS | {"title", "statement", "epistemic_class", "lock", "system_capability_only",
                                   "instances", "components", "mandatory", "stages"},
    # Incógnita: NENHUM campo de conteúdo (statement, thesis, hipótese…). SDD DP-03.
    "UNKNOWN": {"id", "domain", "question", "status", "dossier_item", "unlock", "decided_by", "source",
                "scope", "notes", "superseded_by"},
    "PROHIBITED_INFERENCE": {"id", "domain", "statement", "match", "status", "source", "scope", "notes",
                             "superseded_by"},
    "ENTITY": COMMON_FIELDS | {"title", "statement", "epistemic_class", "entity_kind", "map_refs", "lock"},
}
REQUIRED_BY_KIND = {
    "RULE": ("id", "domain", "title", "statement", "status", "epistemic_class", "source", "scope"),
    "PHRASE": ("id", "domain", "statement", "status", "source", "usage"),
    "CAPABILITY": ("id", "domain", "title", "statement", "status", "epistemic_class", "source", "scope",
                   "system_capability_only", "instances"),
    "UNKNOWN": ("id", "domain", "question", "status", "unlock", "source", "scope"),
    "PROHIBITED_INFERENCE": ("id", "domain", "statement", "status", "source", "scope"),
    "ENTITY": ("id", "domain", "title", "statement", "status", "entity_kind", "source", "scope"),
}
LOCK_FIELDS = {"id", "formula", "source", "scope", "franchise_level", "modes", "records", "detectors", "notes"}
LOCK_ID_RE = re.compile(r"^HL-\d{2}$")
GATE_ID_RE = {
    "required": re.compile(r"^BG1-R-[A-Z0-9-]+$"),
    "partial": re.compile(r"^BG1-P-[A-Z0-9-]+$"),
    "forbidden": re.compile(r"^BG1-F-[A-Z0-9-]+$"),
    "future": re.compile(r"^BGF-[A-Z0-9-]+$"),
}
DETECTOR_ENGINE_RE = re.compile(r"^ENGINE:(check_[a-z_]+):([A-Za-z0-9_-]+)$")
DETECTOR_JUDGMENT_RE = re.compile(r"^JUDGMENT:([A-Z_]+)$")
ENGINE_VALIDATORS = {"check_causal_ledger", "check_interpretive_canon", "check_representation", "check_cartography"}
BOOK_AGENTS_PLANNED = {"REDMUR_CANON_WARDEN"}        # agents/redmur_canon_warden.toml (Slice 5)

# --- catálogo de regras (SDD seção 66) --------------------------------------------------
# família -> slice em que a regra é implementada. Uma regra citada por lock mas de slice
# futuro aparece no relatório como PLANEJADA, nunca como verificada.

FAMILY_SLICE = {
    "SRC": 1, "CR": 1, "ST": 1, "PV": 1, "HL": 1,
    "RUM": 2, "MYS": 2, "KN": 2, "RD": 2,
    "FACE": 3, "FRC": 3, "SFE": 3, "EXT": 3, "CMB": 3, "TCH": 3, "CNS": 3, "AGE": 3, "CIV": 3, "VIS": 3,
    "JUR": 3, "TEC": 3, "TAT": 3, "MAN": 3, "SEL": 3, "NH": 3, "COF": 3, "CPR": 3, "IDN": 3, "IDS": 3,
    "PUL": 3, "ECO": 3, "BG": 3, "CHR": 3, "40Y": 3, "ARC": 3, "DA": 3, "TMP": 3, "EVI": 3,
    "CTX": 4, "CRM": 4, "FP": 4, "DE": 4, "IRR": 4, "PRM": 4, "PS": 4, "MUT": 4, "CP": 4, "B1": 4, "BF": 4,
    "DEN": 4, "CART": 4, "PRC": 4,
}
RULE_COUNTS = {
    "SRC": 2, "CR": 11, "ST": 4, "PV": 5, "HL": 3, "RUM": 4, "MYS": 4, "KN": 6, "RD": 4, "FACE": 7, "FRC": 3,
    "SFE": 6, "EXT": 2, "CMB": 7, "TCH": 5, "CNS": 6, "AGE": 5, "CIV": 6, "VIS": 5, "JUR": 6, "TEC": 4,
    "TAT": 5, "MAN": 6, "SEL": 6, "NH": 5, "COF": 7, "CPR": 6, "IDN": 2, "IDS": 3, "PUL": 4, "ECO": 3,
    "BG": 3, "CHR": 4, "40Y": 4, "ARC": 3, "DA": 3, "TMP": 2, "EVI": 2, "CTX": 4, "CRM": 6, "FP": 6, "DE": 4,
    "IRR": 4, "PRM": 4, "PS": 1, "MUT": 3, "CP": 1, "B1": 11, "BF": 3, "DEN": 1, "CART": 2, "PRC": 5,
}
RULE_CATALOG = {f"SR-{fam}-{n:02d}": FAMILY_SLICE[fam] for fam, count in RULE_COUNTS.items()
                for n in range(1, count + 1)}
IMPLEMENTED_SLICE = 1
SR_RULE_RE = re.compile(r"^SR-([A-Z0-9]+)-(\d{2})$")

SECTION_RE = re.compile(r"^(#{1,2})\s+(\d+(?:\.\d+)?)[.\s]")
LOCATION_RE = re.compile(r"§(\d+(?:\.\d+)?)")


# --------------------------------------------------------------------------------------------

def finding(rule: str, category: str, severity: str, evidence: str, detail: str, action: str) -> dict:
    return {"rule": rule, "category": category, "severity": severity, "evidence": evidence,
            "detail": detail, "recommended_action": action}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def record_kind(record_id) -> str | None:
    if not isinstance(record_id, str):
        return None
    for pattern, kind in KIND_BY_PREFIX:
        if pattern.match(record_id):
            return kind
    return None


def parse_dossier(text: str) -> dict:
    """Seções (§N e §N.N), itens de §17 (incógnitas) e de §21 (gates de escrita)."""
    sections: set[str] = set()
    top_of_line: list[tuple[int, str]] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        m = SECTION_RE.match(line)
        if m:
            sections.add(m.group(2))
            if len(m.group(1)) == 1:
                top_of_line.append((idx, m.group(2)))

    def body(section: str) -> list[str]:
        for pos, (start, sec) in enumerate(top_of_line):
            if sec == section:
                end = top_of_line[pos + 1][0] if pos + 1 < len(top_of_line) else len(lines)
                return lines[start + 1:end]
        return []

    unknown_items = [ln for ln in body("17") if ln.startswith("- ")]
    writing_gates = [ln for ln in body("21") if re.match(r"^\d+\.\s", ln)]
    return {"sections": sections, "unknown_items": unknown_items, "writing_gates": writing_gates}


def scan_hidden_keys(node, path: str, out: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            if normalize_key(key) in HIDDEN_ANSWER_KEYS:
                out.append(here)
            scan_hidden_keys(value, here, out)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            scan_hidden_keys(value, f"{path}[{i}]", out)


def cartography_ids(cartography_dir: Path | None) -> set[str] | None:
    if cartography_dir is None or not cartography_dir.is_dir():
        return None
    ids: set[str] = set()
    for path in sorted(cartography_dir.glob("*.seed.yaml")):
        text = path.read_text(encoding="utf-8")
        ids.update(re.findall(r"\bid:\s*['\"]?([A-Z][A-Z0-9_-]+)", text))
    return ids


def engine_agent_names() -> set[str] | None:
    if ENGINE_SCRIPTS is None:
        return None
    agents_dir = ENGINE_SCRIPTS.parent / "agents"
    if not agents_dir.is_dir():
        return None
    names = set()
    for path in agents_dir.glob("*.toml"):
        m = re.search(r'^name\s*=\s*"([A-Z_]+)"', path.read_text(encoding="utf-8"), re.M)
        if m:
            names.add(m.group(1))
    return names


# --------------------------------------------------------------------------------------------

class Context:
    def __init__(self, canon_dir: Path, cartography_dir: Path | None):
        self.canon_dir = canon_dir
        self.cartography_dir = cartography_dir
        self.findings: list[dict] = []
        self.sources: dict[str, dict] = {}
        self.dossier: dict | None = None
        self.seeds: dict[str, dict] = {}
        self.records: dict[str, dict] = {}
        self.locks: dict[str, dict] = {}
        self.gate_ids: set[str] = set()
        self.map_ids = cartography_ids(cartography_dir)
        self.agents = engine_agent_names()

    def add(self, *args):
        self.findings.append(finding(*args))

    def approval_path(self, name: str) -> Path:
        return self.canon_dir / "approvals" / f"{name}.md"


def check_sources(ctx: Context) -> None:
    src_file = ctx.canon_dir / "sources" / "SOURCES.yaml"
    if not src_file.exists():
        ctx.add("SR-SRC-01", "SOURCE_HASH_MISMATCH", "BLOCKER", str(src_file), "SOURCES.yaml ausente.",
                "Registrar a fonte pinada (Slice 0).")
        return
    doc = load_yaml(src_file) or {}
    for src in as_list(doc.get("sources")):
        sid = src.get("id")
        ctx.sources[sid] = src
        path = src_file.parent / str(src.get("file", ""))
        if not path.is_file():
            ctx.add("SR-SRC-01", "SOURCE_HASH_MISMATCH", "BLOCKER", f"{sid}.file",
                    f"Arquivo da fonte ausente: {path.name}.", "Restaurar o arquivo pinado.")
            continue
        actual = sha256_file(path)
        if actual != src.get("sha256"):
            ctx.add("SR-SRC-01", "SOURCE_HASH_MISMATCH", "BLOCKER", f"{sid}.sha256",
                    f"sha256 do arquivo ({actual[:12]}…) difere do pinado ({str(src.get('sha256'))[:12]}…). "
                    "O dossiê congelado não é editado.",
                    "Restaurar o arquivo; correção legítima entra como nova fonte com `supersedes`.")
            continue
        if sid == "SRC-DOSSIER":
            ctx.dossier = parse_dossier(path.read_text(encoding="utf-8"))
        freeze = src.get("freeze") or {}
        if freeze.get("status") == "FROZEN":
            approval = (src_file.parent / str(freeze.get("approval", ""))).resolve()
            ok = approval.is_file() and f"subject_sha256: {actual}" in approval.read_text(encoding="utf-8")
            if not ok:
                ctx.add("SR-SRC-02", "FREEZE_NOT_APPROVED", "BLOCKER", f"{sid}.freeze",
                        "Fonte declarada FROZEN sem aprovação humana com o subject_sha256 do arquivo.",
                        "Um humano registra approvals/CANON_FREEZE_<n>.md; o motor nunca escreve aprovação.")
        elif sid == "SRC-DOSSIER":
            ctx.add("SR-SRC-02", "FREEZE_NOT_APPROVED", "MEDIUM", f"{sid}.freeze",
                    "Dossiê ainda não congelado: o validador roda em modo consultivo.",
                    "Registrar o freeze humano (OQ-SR-01).")
    if "SRC-DOSSIER" not in ctx.sources:
        ctx.add("SR-SRC-01", "SOURCE_HASH_MISMATCH", "BLOCKER", "SOURCES.yaml", "SRC-DOSSIER não declarado.",
                "Pinar o dossiê.")


def load_seeds(ctx: Context) -> None:
    seeds_dir = ctx.canon_dir / "seeds"
    for name, kind in SEED_KINDS.items():
        path = seeds_dir / name
        if not path.is_file():
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", name, "Seed obrigatório ausente.", "Criar o seed.")
            continue
        doc = load_yaml(path)
        if not isinstance(doc, dict):
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", name, "Seed vazio ou não é mapa.", "Corrigir.")
            continue
        ctx.seeds[name] = doc
        if doc.get("apiVersion") != API_VERSION or doc.get("kind") != kind:
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"{name}.kind",
                    f"Esperado apiVersion {API_VERSION} e kind {kind}.", "Corrigir o cabeçalho.")
        for key in set(doc) - SEED_ROOT_FIELDS[kind]:
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"{name}.{key}",
                    "Campo de raiz desconhecido.", "Remover ou declarar no contrato (SDD seção 12).")
        meta = doc.get("metadata") or {}
        for key in set(meta) - METADATA_FIELDS:
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "MEDIUM", f"{name}.metadata.{key}",
                    "Campo de metadata desconhecido.", "Remover.")
        hidden: list[str] = []
        scan_hidden_keys(doc, name, hidden)
        for where in hidden:
            ctx.add("SR-CR-07", "HIDDEN_ANSWER_PRESENT", "BLOCKER", where,
                    "Chave de resposta em seed de canon: nenhum arquivo guarda resposta (DP-03, AD-02).",
                    "Remover a chave; verdade decidida entra como registro por proposta humana.")


def check_approvals(ctx: Context) -> None:
    for name, doc in ctx.seeds.items():
        approval = (doc.get("metadata") or {}).get("approval")
        if not approval:
            ctx.add("SR-CR-10", "SEED_UNAPPROVED", "MEDIUM", f"{name}.metadata.approval",
                    "Seed ainda sem aprovação humana registrada.",
                    "Humano registra approvals/CANON_SEEDS_<n>.md com subject_sha256 deste seed.")
            continue
        path = (ctx.canon_dir / "seeds" / str(approval)).resolve()
        if not path.is_file():
            path = ctx.approval_path(str(approval))
        sha = sha256_file(ctx.canon_dir / "seeds" / name)
        ok = path.is_file() and f"subject_sha256: {sha}" in path.read_text(encoding="utf-8")
        if not ok:
            if name in LOCK_SEEDS:
                ctx.add("SR-HL-02", "HARD_LOCK_EDIT", "BLOCKER", f"{name}",
                        "Seed de locks/gates difere do que foi aprovado (ou a aprovação não existe).",
                        "Reverter a mudança ou registrar nova aprovação humana; HL-01..04/HL-20 exigem revisão da franquia.")
            else:
                ctx.add("SR-CR-11", "SEED_EDITED_AFTER_APPROVAL", "HIGH", f"{name}",
                        "Seed difere do que foi aprovado (ou a aprovação não existe).",
                        "Reverter ou registrar nova aprovação humana.")


def check_source_ref(ctx: Context, owner: str, source) -> None:
    if not isinstance(source, dict) or not source.get("id"):
        ctx.add("SR-PV-01", "CANON_WITHOUT_PROVENANCE", "HIGH", f"{owner}.source",
                "Registro sem fonte.", "Declarar source: {id, location}.")
        return
    sid, location = source.get("id"), str(source.get("location") or "")
    if sid.startswith("APPROVAL:"):
        path = ctx.approval_path(sid.split(":", 1)[1])
        if not path.is_file():
            ctx.add("SR-PV-05", "IMPROVISED_CANON", "BLOCKER", f"{owner}.source",
                    f"Aprovação inexistente: {path.name}.", "Registrar a decisão humana ou remover o registro.")
        elif not location or location not in path.read_text(encoding="utf-8"):
            ctx.add("SR-PV-01", "CANON_WITHOUT_PROVENANCE", "HIGH", f"{owner}.source.location",
                    f"'{location}' não aparece em {path.name}.", "Apontar o item da decisão.")
        return
    known_sources = set(ctx.sources) | {"SRC-MAP-A", "SRC-MAP-B"}
    if sid not in known_sources:
        ctx.add("SR-PV-05", "IMPROVISED_CANON", "BLOCKER", f"{owner}.source.id",
                f"Fonte '{sid}' não é dossiê, mapa ou aprovação humana.",
                "Canon só nasce das fontes canônicas ou de proposta aprovada.")
        return
    if sid == "SRC-DOSSIER" and ctx.dossier is not None:
        anchors = LOCATION_RE.findall(location)
        missing = [a for a in anchors if a not in ctx.dossier["sections"]]
        if not anchors or missing:
            ctx.add("SR-PV-01", "CANON_WITHOUT_PROVENANCE", "HIGH", f"{owner}.source.location",
                    f"Âncora inexistente no dossiê pinado: {missing or location!r}.",
                    "Citar seção existente (§N ou §N.N).")


def check_refs(ctx: Context, owner: str, field: str, refs, allowed_kinds: set[str] | None = None) -> None:
    for ref in as_list(refs):
        kind = record_kind(ref)
        ok = ref in ctx.records and (allowed_kinds is None or kind in allowed_kinds)
        if not ok:
            ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", f"{owner}.{field}",
                    f"'{ref}' não resolve para registro{'' if allowed_kinds is None else ' ' + '/'.join(sorted(allowed_kinds))}.",
                    "Corrigir o id ou criar o registro por proposta.")


def check_records(ctx: Context) -> None:
    doc = ctx.seeds.get("CANON_RECORDS.seed.yaml")
    if not doc:
        return
    items = as_list(doc.get("records"))
    for rec in items:
        rid = rec.get("id") if isinstance(rec, dict) else None
        if rid in ctx.records:
            ctx.add("SR-CR-02", "DUPLICATE_ID", "HIGH", str(rid), "Id duplicado.", "Um id por registro.")
        elif rid:
            ctx.records[rid] = rec
    for rec in items:
        if not isinstance(rec, dict):
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", "records[]", "Registro não é mapa.", "Corrigir.")
            continue
        rid = rec.get("id")
        kind = record_kind(rid)
        if kind is None:
            ctx.add("SR-CR-03", "ID_MALFORMED", "HIGH", str(rid),
                    "Id fora dos prefixos CR-/CAP-/UNK-SR-/PRO-SR-/ENT-/INST-/FAM-.", "Renomear.")
            continue
        for key in REQUIRED_BY_KIND[kind]:
            if rec.get(key) in (None, "", []) and not (key == "instances" and rec.get(key) == []):
                ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"{rid}.{key}", f"Campo obrigatório ({kind}).",
                        "Preencher.")
        extra = set(rec) - FIELDS_BY_KIND[kind]
        if kind == "UNKNOWN" and extra:
            ctx.add("SR-CR-06", "UNKNOWN_HAS_CONTENT", "BLOCKER", f"{rid}.{sorted(extra)}",
                    "Incógnita com campo de conteúdo: CANON_UNKNOWN não tem resposta em arquivo nenhum (HL-16).",
                    "Remover o conteúdo; se a autora decidiu a verdade, criar registro por proposta aprovada.")
        else:
            for key in sorted(extra):
                ctx.add("SR-CR-01", "CONTRACT_INVALID", "MEDIUM", f"{rid}.{key}",
                        f"Campo desconhecido para {kind}.", "Remover ou declarar no contrato.")
        status = rec.get("status")
        if status not in AUTHORITY_STATUSES:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{rid}.status", f"'{status}' não é status.", "Corrigir.")
        elif status not in STATUSES_BY_KIND[kind]:
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"{rid}.status",
                    f"Status '{status}' não é válido para {kind}.", "Usar o tipo certo (ex.: incógnita = UNK-SR-*).")
        if rec.get("domain") not in DOMAINS:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{rid}.domain", f"'{rec.get('domain')}'.", "Corrigir.")
        if "epistemic_class" in rec and rec["epistemic_class"] not in EPISTEMIC_CLASSES:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{rid}.epistemic_class", f"'{rec['epistemic_class']}'.",
                    "Corrigir.")
        scope = rec.get("scope") or {}
        if not isinstance(scope, dict) or scope.get("book") not in BOOK_SCOPES:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{rid}.scope.book", f"'{scope}'.", "SERIES|B1|B2|B3.")
        elif "reader" in scope and scope["reader"] not in READER_SCOPES:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{rid}.scope.reader", f"'{scope['reader']}'.", "OPEN|GATED|NEVER.")
        # patch
        if status == "CANON_PATCH_APPROVED" and not PATCH_RE.match(str(rec.get("patch", ""))):
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"{rid}.patch",
                    "Registro de patch sem `patch: R1..R11`.", "Indicar o patch que o aprova.")
        if "patch" in rec and status != "CANON_PATCH_APPROVED":
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"{rid}.patch",
                    "`patch` só existe em registro CANON_PATCH_APPROVED.", "Corrigir o status ou remover.")
        # capacidade ≠ instância
        if kind == "CAPABILITY":
            if rec.get("system_capability_only") is not True:
                ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"{rid}.system_capability_only",
                        "Capacidade precisa declarar system_capability_only: true.", "Corrigir.")
            for inst in as_list(rec.get("instances")):
                approved = isinstance(inst, dict) and str(inst.get("approved_by", "")).startswith("APPROVAL:") \
                    and ctx.approval_path(str(inst["approved_by"]).split(":", 1)[1]).is_file()
                if not approved:
                    ctx.add("SR-ST-04", "SYSTEM_CAPABILITY_AS_INSTANCE", "BLOCKER", f"{rid}.instances",
                            f"Instância {inst!r} sem aprovação humana: a capacidade não canoniza instância (HL-05).",
                            "Remover a instância, ou registrar decisão humana e citá-la em approved_by.")
        elif rec.get("system_capability_only") is True:
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"{rid}.system_capability_only",
                    "Só CAP-* é capacidade.", "Renomear para CAP-* ou remover o campo.")
        if kind == "UNKNOWN":
            if rec.get("unlock") not in UNLOCK_POLICIES:
                ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{rid}.unlock", f"'{rec.get('unlock')}'.",
                        f"{sorted(UNLOCK_POLICIES)}.")
            if scope.get("reader") != "NEVER":
                ctx.add("SR-CR-06", "UNKNOWN_HAS_CONTENT", "BLOCKER", f"{rid}.scope.reader",
                        "Incógnita acessível ao leitor: não há o que entregar.", "scope.reader: NEVER.")
        if kind == "ENTITY" and rec.get("entity_kind") not in ENTITY_KINDS:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{rid}.entity_kind", f"'{rec.get('entity_kind')}'.", "Corrigir.")
        if kind == "PROHIBITED_INFERENCE" and "match" in rec and not all(isinstance(m, str) and m for m in as_list(rec["match"])):
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "MEDIUM", f"{rid}.match", "match deve ser lista de textos.", "Corrigir.")
        check_source_ref(ctx, rid, rec.get("source"))
        for field in ("depends_on", "conflicts_with", "supersedes", "superseded_by"):
            check_refs(ctx, rid, field, rec.get(field))
        if rec.get("lock") is not None and rec["lock"] not in ctx.locks:
            ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", f"{rid}.lock", f"'{rec['lock']}' não é lock.", "Corrigir.")
        if rec.get("map_refs"):
            if ctx.map_ids is None:
                ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "INFO", f"{rid}.map_refs",
                        "Seeds da cartografia não encontrados: map_refs não conferidos.", "Passar --cartography.")
            else:
                for ref in as_list(rec["map_refs"]):
                    if ref not in ctx.map_ids:
                        ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", f"{rid}.map_refs",
                                f"'{ref}' não existe na cartografia.", "Corrigir; a cartografia é a autoridade espacial.")

    # cobertura do dossiê §17: um UNK por item, na ordem
    if ctx.dossier is not None:
        expected = len(ctx.dossier["unknown_items"])
        items_seen: dict[int, list[str]] = {}
        for rid, rec in ctx.records.items():
            if record_kind(rid) == "UNKNOWN" and rec.get("dossier_item") is not None:
                items_seen.setdefault(rec["dossier_item"], []).append(rid)
        missing = [i for i in range(1, expected + 1) if i not in items_seen]
        dupes = {i: ids for i, ids in items_seen.items() if len(ids) > 1}
        extra = [i for i in items_seen if not (isinstance(i, int) and 1 <= i <= expected)]
        if missing or dupes or extra:
            ctx.add("SR-CR-08", "COVERAGE_GAP", "HIGH", "dossiê §17",
                    f"§17 tem {expected} incógnitas; faltando {missing}, duplicadas {dupes}, fora do intervalo {extra}.",
                    "Um UNK-SR-* por item de §17 (dossier_item = posição).")


def check_detector(ctx: Context, owner: str, det) -> str:
    """Devolve a classe do detector: SR-planned | SR-implemented | ENGINE | JUDGMENT | INVALID."""
    text = str(det)
    m = SR_RULE_RE.match(text)
    if m:
        if text not in RULE_CATALOG:
            ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", f"{owner}.detectors", f"Regra '{text}' fora do catálogo.",
                    "Citar regra do SDD (seção 66).")
            return "INVALID"
        return "SR-implemented" if RULE_CATALOG[text] <= IMPLEMENTED_SLICE else "SR-planned"
    m = DETECTOR_ENGINE_RE.match(text)
    if m:
        if m.group(1) not in ENGINE_VALIDATORS:
            ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", f"{owner}.detectors", f"Validador '{m.group(1)}' desconhecido.",
                    f"Um de {sorted(ENGINE_VALIDATORS)}.")
            return "INVALID"
        return "ENGINE"
    m = DETECTOR_JUDGMENT_RE.match(text)
    if m:
        agent = m.group(1)
        if agent not in BOOK_AGENTS_PLANNED and ctx.agents is not None and agent not in ctx.agents:
            ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", f"{owner}.detectors", f"Agente '{agent}' inexistente.",
                    "Citar agente do motor ou da obra.")
            return "INVALID"
        return "JUDGMENT"
    ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", f"{owner}.detectors", f"Detector malformado: {text!r}.",
            "SR-*, ENGINE:<script>:<id> ou JUDGMENT:<AGENTE>.")
    return "INVALID"


def index_locks(ctx: Context) -> None:
    doc = ctx.seeds.get("HARD_LOCKS.seed.yaml")
    for lock in as_list((doc or {}).get("locks")):
        lid = lock.get("id") if isinstance(lock, dict) else None
        if lid in ctx.locks:
            ctx.add("SR-CR-02", "DUPLICATE_ID", "HIGH", str(lid), "Lock duplicado.", "Um id por lock.")
        elif lid:
            ctx.locks[lid] = lock


def check_locks(ctx: Context) -> dict:
    coverage = {"implemented": [], "planned_only": [], "judgment_only": []}
    for lid, lock in ctx.locks.items():
        if not LOCK_ID_RE.match(lid):
            ctx.add("SR-CR-03", "ID_MALFORMED", "HIGH", lid, "Lock fora de HL-NN.", "Renomear.")
        for key in set(lock) - LOCK_FIELDS:
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "MEDIUM", f"{lid}.{key}", "Campo desconhecido.", "Remover.")
        for key in ("formula", "source", "scope", "modes"):
            if not lock.get(key):
                ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"{lid}.{key}", "Campo obrigatório.", "Preencher.")
        if lock.get("scope") and lock["scope"] not in LOCK_SCOPES:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{lid}.scope", f"'{lock['scope']}'.", "SERIES|B1.")
        modes = set(as_list(lock.get("modes")))
        if modes - LOCK_MODES:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{lid}.modes", f"{sorted(modes - LOCK_MODES)}.", "Corrigir.")
        check_source_ref(ctx, lid, lock.get("source"))
        check_refs(ctx, lid, "records", lock.get("records"))
        detectors = as_list(lock.get("detectors"))
        if not detectors:
            ctx.add("SR-HL-03", "LOCK_WITHOUT_DETECTOR", "MEDIUM", lid,
                    "Lock sem regra nem item de checklist que o aplique — lock decorativo.", "Declarar detectores.")
            continue
        classes = [check_detector(ctx, lid, d) for d in detectors]
        machine = {"SR-implemented", "SR-planned", "ENGINE"}
        if "STRUCTURAL" in modes and not machine & set(classes):
            ctx.add("SR-HL-03", "LOCK_WITHOUT_DETECTOR", "MEDIUM", lid,
                    "Lock declarado STRUCTURAL só tem detectores de julgamento.",
                    "Acrescentar regra estrutural ou retirar STRUCTURAL de modes.")
        if "SR-implemented" in classes or "ENGINE" in classes:
            coverage["implemented"].append(lid)
        elif "SR-planned" in classes:
            coverage["planned_only"].append(lid)
        else:
            coverage["judgment_only"].append(lid)
    if coverage["planned_only"]:
        ctx.add("SR-HL-03", "LOCK_DETECTORS_PLANNED", "INFO", ", ".join(coverage["planned_only"]),
                f"Detectores estruturais destes locks são de slices futuros (hoje implementado: Slice {IMPLEMENTED_SLICE}); "
                "até lá o lock vale como item de checklist do revisor.", "Nada a fazer neste slice.")
    return coverage


def check_gates(ctx: Context) -> None:
    doc = ctx.seeds.get("BOOK_GATES.seed.yaml")
    if not doc:
        return
    b1 = ((doc.get("book_gates") or {}).get("B1")) or {}
    entries: list[tuple[str, dict]] = []
    for section in ("required", "partial", "forbidden"):
        for gate in as_list(b1.get(section)):
            entries.append((section, gate))
    series = doc.get("series") or {}
    for gate in as_list(series.get("future_domains")):
        entries.append(("future", gate))
    for section, gate in entries:
        gid = gate.get("id") if isinstance(gate, dict) else None
        if gid in ctx.gate_ids:
            ctx.add("SR-CR-02", "DUPLICATE_ID", "HIGH", str(gid), "Gate duplicado.", "Um id por gate.")
        elif gid:
            ctx.gate_ids.add(gid)
        if not gid or not GATE_ID_RE[section].match(gid):
            ctx.add("SR-CR-03", "ID_MALFORMED", "HIGH", str(gid), f"Gate {section} com id fora do padrão.", "Renomear.")
    for section, gate in entries:
        gid = gate.get("id")
        check_source_ref(ctx, gid, gate.get("source"))
        check_refs(ctx, gid, "unknowns", gate.get("unknowns"), {"UNKNOWN"})
        check_refs(ctx, gid, "records", gate.get("records"))
        if section == "forbidden" and not (gate.get("unknowns") or gate.get("records")):
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", gid, "Proibição sem unknowns nem records.", "Ancorar.")
        if section == "partial" and gate.get("ceiling") not in CEILINGS:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{gid}.ceiling", f"'{gate.get('ceiling')}'.", f"{sorted(CEILINGS)}.")
        if section == "future" and gate.get("earliest_allowed_reveal") not in EARLIEST_REVEALS:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{gid}.earliest_allowed_reveal",
                    f"'{gate.get('earliest_allowed_reveal')}'.", f"{sorted(EARLIEST_REVEALS)} (nunca B1).")
        for det in as_list(gate.get("verify")):
            check_detector(ctx, gid, det)
    if b1.get("contract") and b1["contract"] not in ctx.records:
        ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", "B1.contract", f"'{b1['contract']}'.", "Corrigir.")

    # gates de escrita do dossiê §21
    writing = as_list(b1.get("writing_gates"))
    for wg in writing:
        for ref in as_list(wg.get("verify")):
            ok = ref in ctx.locks or ref in ctx.gate_ids or ref in ctx.records or ref in RULE_CATALOG
            if not ok:
                ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", f"writing_gates[{wg.get('item')}]",
                        f"'{ref}' não resolve.", "Citar lock, gate, registro ou regra.")
    if ctx.dossier is not None:
        expected = len(ctx.dossier["writing_gates"])
        got = sorted(wg.get("item") for wg in writing if isinstance(wg.get("item"), int))
        if got != list(range(1, expected + 1)):
            ctx.add("SR-CR-08", "COVERAGE_GAP", "HIGH", "dossiê §21",
                    f"§21 tem {expected} gates de escrita; mapeados {got}.", "Um writing_gate por item de §21.")

    # locks estruturais da série (§22)
    for lid in as_list(series.get("structural_locks")):
        lock = ctx.locks.get(lid)
        if lock is None:
            ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", "series.structural_locks", f"'{lid}'.", "Corrigir.")
        elif lock.get("franchise_level") is not True or lock.get("scope") != "SERIES":
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"series.structural_locks.{lid}",
                    "Lock estrutural da série precisa ser SERIES e franchise_level: true.", "Corrigir o lock.")
    if series.get("structural_locks_source"):
        check_source_ref(ctx, "series.structural_locks", series["structural_locks_source"])
    b2 = (doc.get("book_gates") or {}).get("B2")
    if b2 and b2 != {"status": "UNDEFINED"}:
        ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", "book_gates.B2",
                "Gates do Livro 2 só por decisão humana; o seed os mantém UNDEFINED (SDD 70).", "Reverter.")


def validate(canon_dir: Path | str = DEFAULT_CANON, cartography_dir: Path | str | None = "default") -> tuple[list[dict], dict]:
    canon_dir = Path(canon_dir)
    if cartography_dir == "default":
        cartography_dir = canon_dir.parent / "cartography" / "seeds"
    ctx = Context(canon_dir, Path(cartography_dir) if cartography_dir else None)
    check_sources(ctx)
    load_seeds(ctx)
    index_locks(ctx)
    check_records(ctx)
    coverage = check_locks(ctx)
    check_gates(ctx)
    check_approvals(ctx)
    ctx.findings.sort(key=lambda f: (-SEVERITY_ORDER.index(f["severity"]), f["rule"], f["evidence"]))
    kinds: dict[str, int] = {}
    for rid in ctx.records:
        kinds[record_kind(rid)] = kinds.get(record_kind(rid), 0) + 1
    summary = {
        "records": len(ctx.records), "records_by_kind": dict(sorted(kinds.items())), "locks": len(ctx.locks),
        "gates": len(ctx.gate_ids), "lock_coverage": {k: len(v) for k, v in coverage.items()},
        "dossier_sections": len(ctx.dossier["sections"]) if ctx.dossier else 0,
        "hidden_keys_source": HIDDEN_KEYS_SOURCE, "implemented_slice": IMPLEMENTED_SLICE,
    }
    return ctx.findings, summary


def render(findings: list[dict], summary: dict, canon_dir: Path) -> str:
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_ORDER}
    blocked = counts["HIGH"] + counts["BLOCKER"]
    lines = [
        "# SEM ROSTO — relatório de canon (modo package)",
        "",
        f"- canon: `{canon_dir}`",
        f"- registros: {summary['records']} {summary['records_by_kind']}",
        f"- locks: {summary['locks']} (com detector implementado/motor: {summary['lock_coverage']['implemented']}, "
        f"só planejado: {summary['lock_coverage']['planned_only']}, só julgamento: {summary['lock_coverage']['judgment_only']})",
        f"- gates: {summary['gates']} · seções do dossiê indexadas: {summary['dossier_sections']}",
        f"- achados: " + ", ".join(f"{s} {counts[s]}" for s in reversed(SEVERITY_ORDER)),
        f"- resultado: **{'FAIL' if blocked else ('PASS_WITH_WARNINGS' if findings else 'PASS')}**",
        "",
    ]
    for f in findings:
        lines.append(f"- [{f['severity']}] {f['rule']} {f['category']} — `{f['evidence']}`: {f['detail']} → {f['recommended_action']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--mode", default="package", choices=["package"])
    parser.add_argument("--canon", default=str(DEFAULT_CANON))
    parser.add_argument("--cartography", default="default",
                        help="seeds da cartografia para conferir map_refs (padrão: <canon>/../cartography/seeds)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    findings, summary = validate(args.canon, args.cartography)
    if args.json:
        print(json.dumps({"summary": summary, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        print(render(findings, summary, Path(args.canon)), end="")
    return 1 if any(f["severity"] in BLOCKING for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
