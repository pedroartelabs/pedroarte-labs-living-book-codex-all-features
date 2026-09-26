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

Slice 2 — mistérios, rumores e conhecimento:

- package: contratos de MYSTERIES/RUMORS, cobertura do dossiê §18, consistência incógnita ↔ mistério
- plan --runtime R: sobre o ledger causal do runtime (REUSE `check_causal_ledger`)
    SR-KN   personagem não conhece o que não aprendeu; incógnita nunca é aprendida; proveniência
    SR-RD   leitor idem (READER é conhecedor do ledger)
    SR-RUM  rumor/teoria nunca é fato canônico (inferências proibidas casadas em `facts`)
    SR-MYS  estado projetado do mistério ≤ teto do livro; mistério reservado nunca resolvível
    SR-CR-09 registry do runtime em sincronia com as incógnitas/inferências da obra
- consultas: --is-true, --who-knows, --reader-at, --mystery, --emit-registry-fragment

Conhecimento é token em `knowledge_delta.learns` (o ledger aceita qualquer id): id puro = sabe;
`SR:BELIEVES:<id>`, `SR:SUSPECTS:<id>`, `SR:MISREMEMBERS:<id>`, `SR:TOLD:<id>` = modalidades (SDD 17.2).
Saber que um rumor existe (`RUM-*` puro) é permitido; crer nele (`SR:BELIEVES:RUM-*`) também; o que o
sistema bloqueia é o conteúdo virar fato ou uma incógnita ser aprendida.

O validador não lê prosa nestes slices e não guarda resposta de nada. Modos `scene`, `wave`,
`final` e `regression` chegam nos Slices 3–4; as regras deles já estão no catálogo (RULE_CATALOG)
para que os locks possam citá-las, e o relatório diz quais ainda são planejadas.

Uso:
    python books/sem-rosto/validators/check_sem_rosto_canon.py --mode package [--canon books/sem-rosto/canon] [--json]
    python books/sem-rosto/validators/check_sem_rosto_canon.py --mode plan --runtime <rt> [--book B1]
    python books/sem-rosto/validators/check_sem_rosto_canon.py --is-true "<id|texto>"
    python books/sem-rosto/validators/check_sem_rosto_canon.py --runtime <rt> --who-knows <token> [--at-chapter N]
    python books/sem-rosto/validators/check_sem_rosto_canon.py --runtime <rt> --reader-at N
    python books/sem-rosto/validators/check_sem_rosto_canon.py --mystery MYS-* [--runtime <rt> --at-chapter N]
    python books/sem-rosto/validators/check_sem_rosto_canon.py --emit-registry-fragment

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
    "MYSTERIES.seed.yaml": "SemRostoMysteries",
    "RUMORS.seed.yaml": "SemRostoRumors",
}
SEED_ROOT_FIELDS = {
    "SemRostoCanonRecords": {"apiVersion", "kind", "metadata", "records"},
    "SemRostoHardLocks": {"apiVersion", "kind", "metadata", "locks"},
    "SemRostoBookGates": {"apiVersion", "kind", "metadata", "book_gates", "series"},
    "SemRostoMysteries": {"apiVersion", "kind", "metadata", "mysteries"},
    "SemRostoRumors": {"apiVersion", "kind", "metadata", "rumors"},
}
METADATA_FIELDS = {"project_id", "version", "owner", "source", "approval"}
LOCK_SEEDS = {"HARD_LOCKS.seed.yaml", "BOOK_GATES.seed.yaml", "MYSTERIES.seed.yaml"}   # edição após aprovação = BLOCKER

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

MYSTERY_STATUSES = {"UNOPENED", "OPEN", "EXPANDING", "PARTIALLY_RESOLVED", "RESOLVED", "PERMANENTLY_AMBIGUOUS",
                    "RESERVED", "CANON_PROPOSAL_REQUIRED"}
STATE_RANK = {"UNOPENED": 0, "OPEN": 1, "EXPANDING": 2, "PARTIALLY_RESOLVED": 3, "RESOLVED": 4}
MINIMUM_BOOKS = {"B1", "B2", "B3", "FUTURE", "NEVER"}
MYSTERY_FIELDS = {"id", "question", "scope", "dossier_item", "status", "minimum_book", "full_explanation",
                  "unknown_refs", "prohibited_refs", "records", "forbidden_gates", "interpretive_question",
                  "by_book", "source", "notes", "human_approval_required", "resolution_contract"}
MYSTERY_BOOK_FIELDS = {"state_ceiling", "required", "partial_gate", "allowed"}
MYS_ID_RE = re.compile(r"^MYS-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
RUMOR_ID_RE = re.compile(r"^(RUM|THEORY)-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
RUMOR_FIELDS = {"id", "statement_neutral", "status", "epistemic_class", "archive", "origin", "origin_confidence",
                "truth_relation", "unknown_refs", "prohibited_as_fact", "mysteries", "versions", "beneficiaries",
                "must_coexist_with_alternatives", "source", "notes"}
RUMOR_VERSION_FIELDS = {"id", "carrier", "first_heard", "differs_from", "elements", "source"}
ARCHIVES = {"PAPER", "STONE", "BODY", "VOICE"}

# tokens de conhecimento (SDD 17.2)
MODALITIES = {"BELIEVES", "SUSPECTS", "MISREMEMBERS", "TOLD"}
TOKEN_RE = re.compile(r"^SR:(BELIEVES|SUSPECTS|MISREMEMBERS|TOLD):(\S+)$")
SR_NAMESPACE_RE = re.compile(r"^(CR|CAP|UNK-SR|PRO-SR|ENT|INST|FAM|MYS|RUM|THEORY|ITM)-")
PROVENANCE_SOURCE_RE = re.compile(r"^(EV|EVD|ITM|CHR|STG)-\S+$")
STATE_DELTA_TYPES = {"KNOWLEDGE_PROVENANCE", "FACE_EVENT", "COFFER_STATE", "COFFER_TOUCH", "CONSENT_GRANT",
                     "CONSENT_REVOKE", "CIVIC_TRANSITION", "RECOGNITION", "ITEM_CUSTODY", "ANOMALY",
                     "IRREVERSIBLE", "INJURY", "PULL_FACTORS"}
STATE_DELTA_TYPES_IMPLEMENTED = {"KNOWLEDGE_PROVENANCE"}
CONFIDENCES = {"FULL", "PARTIAL", "MISREAD"}

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
IMPLEMENTED_SLICE = 2
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
    reserved_items = []
    for ln in body("18"):
        if ln.startswith("- "):
            reserved_items.append(ln)
        elif reserved_items and ln.strip():
            break                      # só a primeira lista de §18 (os mistérios reservados)
    return {"sections": sections, "unknown_items": unknown_items, "writing_gates": writing_gates,
            "reserved_items": reserved_items}


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
        self.mysteries: dict[str, dict] = {}
        self.rumors: dict[str, dict] = {}
        self.coverage: dict = {}
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


def index_mysteries_and_rumors(ctx: Context) -> None:
    for seed, table, key, id_re in (("MYSTERIES.seed.yaml", ctx.mysteries, "mysteries", MYS_ID_RE),
                                    ("RUMORS.seed.yaml", ctx.rumors, "rumors", RUMOR_ID_RE)):
        for item in as_list((ctx.seeds.get(seed) or {}).get(key)):
            iid = item.get("id") if isinstance(item, dict) else None
            if not iid or not id_re.match(str(iid)):
                ctx.add("SR-CR-03", "ID_MALFORMED", "HIGH", f"{seed}:{iid}", "Id fora do padrão.", "Renomear.")
                continue
            if iid in table or iid in ctx.records:
                ctx.add("SR-CR-02", "DUPLICATE_ID", "HIGH", iid, "Id duplicado.", "Um id por item.")
                continue
            table[iid] = item


def check_mysteries(ctx: Context) -> None:
    for mid, mys in ctx.mysteries.items():
        for key in sorted(set(mys) - MYSTERY_FIELDS):
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "MEDIUM", f"{mid}.{key}", "Campo desconhecido.", "Remover.")
        for key in ("question", "status", "minimum_book", "source", "by_book"):
            if mys.get(key) in (None, "", {}):
                ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"{mid}.{key}", "Campo obrigatório.", "Preencher.")
        if mys.get("status") not in MYSTERY_STATUSES:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{mid}.status", f"'{mys.get('status')}'.", f"{sorted(MYSTERY_STATUSES)}.")
        if mys.get("minimum_book") not in MINIMUM_BOOKS:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{mid}.minimum_book", f"'{mys.get('minimum_book')}'.", f"{sorted(MINIMUM_BOOKS)}.")
        check_source_ref(ctx, mid, mys.get("source"))
        check_refs(ctx, mid, "unknown_refs", mys.get("unknown_refs"), {"UNKNOWN"})
        check_refs(ctx, mid, "prohibited_refs", mys.get("prohibited_refs"), {"PROHIBITED_INFERENCE"})
        check_refs(ctx, mid, "records", mys.get("records"))
        for gid in as_list(mys.get("forbidden_gates")):
            if gid not in ctx.gate_ids:
                ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", f"{mid}.forbidden_gates", f"'{gid}'.", "Corrigir.")
        reserved = mys.get("status") == "RESERVED" or mys.get("minimum_book") in {"B2", "B3", "FUTURE", "NEVER"}
        for book, spec in (mys.get("by_book") or {}).items():
            if book not in BOOK_SCOPES - {"SERIES"} or not isinstance(spec, dict):
                ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{mid}.by_book.{book}", "Livro inválido.", "B1|B2|B3.")
                continue
            for key in sorted(set(spec) - MYSTERY_BOOK_FIELDS):
                ctx.add("SR-CR-01", "CONTRACT_INVALID", "MEDIUM", f"{mid}.by_book.{book}.{key}", "Campo desconhecido.", "Remover.")
            ceiling = spec.get("state_ceiling")
            if ceiling not in STATE_RANK:
                ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{mid}.by_book.{book}.state_ceiling", f"'{ceiling}'.", f"{sorted(STATE_RANK)}.")
            elif reserved and STATE_RANK[ceiling] > STATE_RANK["EXPANDING"]:
                ctx.add("SR-MYS-01", "PREMATURE_RESOLUTION", "BLOCKER", f"{mid}.by_book.{book}.state_ceiling",
                        f"Mistério reservado com teto {ceiling}: o livro poderia resolvê-lo.",
                        "Teto ≤ EXPANDING até decisão humana que libere o mistério para este livro.")
            for gid in as_list(spec.get("required")) + as_list(spec.get("partial_gate")):
                if gid not in ctx.gate_ids:
                    ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", f"{mid}.by_book.{book}", f"'{gid}'.", "Corrigir.")
        if mys.get("interpretive_question") and not re.match(r"^Q-[A-Z0-9_-]+$", str(mys["interpretive_question"])):
            ctx.add("SR-CR-03", "ID_MALFORMED", "HIGH", f"{mid}.interpretive_question", "Esperado Q-*.", "Corrigir.")
        for key in mys:
            if normalize_key(key) in {"world_truth", "solution", "resolution"} or normalize_key(key) in HIDDEN_ANSWER_KEYS:
                ctx.add("SR-MYS-02", "HIDDEN_ANSWER_PRESENT", "BLOCKER", f"{mid}.{key}",
                        "Mistério com campo de resposta: world_truth não é campo (SDD 20.2).", "Remover.")
        if mys.get("status") == "CANON_PROPOSAL_REQUIRED" and mys.get("unknown_refs"):
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "MEDIUM", mid, "Slot de proposta com incógnitas declaradas.", "Revisar.")

    # cobertura do dossiê §18 (mistérios reservados), um MYS por item
    if ctx.dossier is not None:
        expected = len(ctx.dossier["reserved_items"])
        seen: dict = {}
        for mid, mys in ctx.mysteries.items():
            if mys.get("dossier_item") is not None:
                seen.setdefault(mys["dossier_item"], []).append(mid)
        missing = [i for i in range(1, expected + 1) if i not in seen]
        dupes = {i: ids for i, ids in seen.items() if len(ids) > 1}
        if missing or dupes or any(not (isinstance(i, int) and 1 <= i <= expected) for i in seen):
            ctx.add("SR-CR-08", "COVERAGE_GAP", "HIGH", "dossiê §18",
                    f"§18 tem {expected} mistérios reservados; faltando {missing}, duplicados {dupes}.",
                    "Um MYS-* por item de §18 (dossier_item = posição).")

    # toda incógnita bloqueada no Livro 1 pertence a algum mistério (senão é incógnita solta)
    owned = {u for mys in ctx.mysteries.values() for u in as_list(mys.get("unknown_refs"))}
    for rid, rec in ctx.records.items():
        if record_kind(rid) == "UNKNOWN" and rec.get("unlock") == "B1_LOCKED" and rid not in owned:
            ctx.add("SR-MYS-02", "UNKNOWN_WITHOUT_MYSTERY", "MEDIUM", rid,
                    "Incógnita bloqueada no Livro 1 que nenhum MYS-* declara: o gate de revelação não a enxerga.",
                    "Acrescentar a incógnita ao unknown_refs do mistério correspondente.")


def check_rumors(ctx: Context) -> None:
    for rid, rum in ctx.rumors.items():
        for key in sorted(set(rum) - RUMOR_FIELDS):
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "MEDIUM", f"{rid}.{key}", "Campo desconhecido.", "Remover.")
        for key in ("statement_neutral", "status", "epistemic_class", "source", "truth_relation"):
            if rum.get(key) in (None, ""):
                ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"{rid}.{key}", "Campo obrigatório.", "Preencher.")
        expected_class = "THEORY" if rid.startswith("THEORY-") else "RUMOR"
        if rum.get("epistemic_class") != expected_class:
            ctx.add("SR-ST-03", "RUMOR_PROMOTED_TO_FACT", "BLOCKER", f"{rid}.epistemic_class",
                    f"'{rum.get('epistemic_class')}': o conteúdo de {rid} só pode ser {expected_class}.",
                    "A existência do rumor é canon; o conteúdo nunca é fato (SDD 13.3).")
        if rum.get("status") != "CANON_APPROVED":
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{rid}.status", f"'{rum.get('status')}'.", "CANON_APPROVED.")
        truth = rum.get("truth_relation")
        if truth != "UNCONFIRMED" and not (isinstance(truth, str) and truth in ctx.records
                                           and (ctx.records[truth].get("epistemic_class") == "FACT")):
            ctx.add("SR-ST-03", "RUMOR_PROMOTED_TO_FACT", "BLOCKER", f"{rid}.truth_relation",
                    f"'{truth}': relação de verdade só é UNCONFIRMED ou um CR-* FACT aprovado por humano.",
                    "Voltar a UNCONFIRMED; confirmar exige decisão humana que cria novo registro.")
        if rum.get("archive") is not None and rum["archive"] not in ARCHIVES:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{rid}.archive", f"'{rum['archive']}'.", f"{sorted(ARCHIVES)}.")
        origin = rum.get("origin", "UNKNOWN")
        if origin != "UNKNOWN" and origin not in ctx.records:
            ctx.add("SR-RUM-03", "RUMOR_ORIGIN_INVENTED", "HIGH", f"{rid}.origin",
                    f"Origem '{origin}' sem canon.", "UNKNOWN até decisão da autora.")
        for ben in as_list(rum.get("beneficiaries")):
            if ben not in ctx.records:
                ctx.add("SR-RUM-03", "RUMOR_ORIGIN_INVENTED", "HIGH", f"{rid}.beneficiaries",
                        f"Beneficiário '{ben}' sem canon.", "Remover; beneficiário nunca é inferido.")
        if rum.get("prohibited_as_fact"):
            check_refs(ctx, rid, "prohibited_as_fact", rum["prohibited_as_fact"], {"PROHIBITED_INFERENCE"})
        elif expected_class == "THEORY":
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", f"{rid}.prohibited_as_fact",
                    "Teoria sem inferência proibida que a impeça de virar fato.", "Declarar PRO-SR-*.")
        check_refs(ctx, rid, "unknown_refs", rum.get("unknown_refs"), {"UNKNOWN"})
        for mid in as_list(rum.get("mysteries")):
            if mid not in ctx.mysteries:
                ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", f"{rid}.mysteries", f"'{mid}'.", "Corrigir.")
        check_source_ref(ctx, rid, rum.get("source"))
        seen_versions = set()
        for ver in as_list(rum.get("versions")):
            vid = ver.get("id") if isinstance(ver, dict) else None
            if not vid or vid in seen_versions:
                ctx.add("SR-CR-02", "DUPLICATE_ID", "HIGH", f"{rid}.versions", f"Versão sem id ou duplicada: {vid}.", "Corrigir.")
            seen_versions.add(vid)
            if isinstance(ver, dict):
                for key in sorted(set(ver) - RUMOR_VERSION_FIELDS):
                    ctx.add("SR-RUM-02", "RUMOR_NORMALIZED", "HIGH", f"{rid}.{vid}.{key}",
                            "Versão de rumor com campo fora do contrato (versões nunca são marcadas verdadeiras).",
                            "Remover; versões são preservadas lado a lado.")
                check_source_ref(ctx, f"{rid}.{vid}", ver.get("source"))


# --- registry do runtime (REUSE do contrato do LTE: unknown_ref = CANON:UNK-*) --------------

def registry_fragment(ctx: Context) -> dict:
    unknowns, prohibited = [], []
    for rid, rec in ctx.records.items():
        kind = record_kind(rid)
        if kind == "UNKNOWN" and rec.get("status") == "CANON_UNKNOWN":
            unknowns.append({"id": rid, "status": "MUST_REMAIN_UNKNOWN", "question": rec.get("question")})
        elif kind == "PROHIBITED_INFERENCE" and rec.get("status") == "CANON_APPROVED":
            entry = {"id": rid, "statement": rec.get("statement")}
            if rec.get("match"):
                entry["match"] = as_list(rec["match"])
            prohibited.append(entry)
    return {"unknowns": unknowns, "prohibited_inferences": prohibited}


def check_registry_sync(ctx: Context, registry: dict) -> None:
    frag = registry_fragment(ctx)
    for block, prefix in (("unknowns", "UNK-SR-"), ("prohibited_inferences", "PRO-SR-")):
        want = {e["id"]: e for e in frag[block]}
        have = {e.get("id"): e for e in as_list(registry.get(block)) if str(e.get("id", "")).startswith(prefix)}
        for missing in sorted(set(want) - set(have)):
            ctx.add("SR-CR-09", "REGISTRY_DRIFT", "HIGH", f"CANON_REGISTRY.{block}.{missing}",
                    "Ausente do registry do runtime.", "Incluir o fragmento gerado por --emit-registry-fragment (T018).")
        for extra in sorted(set(have) - set(want)):
            ctx.add("SR-CR-09", "REGISTRY_DRIFT", "HIGH", f"CANON_REGISTRY.{block}.{extra}",
                    "No registry mas não no canon da obra.", "Remover do registry ou registrar por proposta.")
        for uid in sorted(set(want) & set(have)):
            if block == "unknowns" and have[uid].get("status") != "MUST_REMAIN_UNKNOWN":
                ctx.add("SR-CR-09", "REGISTRY_DRIFT", "HIGH", f"CANON_REGISTRY.unknowns.{uid}.status",
                        f"'{have[uid].get('status')}'.", "MUST_REMAIN_UNKNOWN.")


# --- conhecimento no runtime (REUSE do ledger causal) ---------------------------------------

def parse_token(token) -> tuple[str, str]:
    """(modalidade, id base). Modalidade 'KNOWS' para id puro."""
    text = str(token)
    m = TOKEN_RE.match(text)
    if m:
        return m.group(1), m.group(2)
    return "KNOWS", text


def is_sr_id(token_id: str) -> bool:
    return bool(SR_NAMESPACE_RE.match(token_id))


def norm_text(text) -> str:
    stripped = "".join(c for c in unicodedata.normalize("NFKD", str(text)) if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", stripped.lower()).strip()


def events_sorted(ledger: dict) -> list[dict]:
    return [ev for _, ev in sorted(enumerate(ledger.get("events") or []),
                                   key=lambda pair: (pair[1].get("chapter", 0), pair[0]))]


def knowledge_of(ledger: dict, knower: str, at_chapter: int | None = None) -> list[tuple[str, str, str, int]]:
    """[(token, modalidade, id base, capítulo)] em ordem de aquisição — o mesmo fold de
    `check_causal_ledger.knowledge_state`, com capítulo e modalidade."""
    out, seen = [], set()
    for ev in events_sorted(ledger):
        if at_chapter is not None and ev.get("chapter", 0) > at_chapter:
            break
        for kd in ev.get("knowledge_delta") or []:
            if kd.get("knower") != knower:
                continue
            for tok in kd.get("learns") or []:
                if tok not in seen:
                    seen.add(tok)
                    modality, base = parse_token(tok)
                    out.append((str(tok), modality, base, ev.get("chapter", 0)))
    return out


def check_runtime_knowledge(ctx: Context, ledger: dict, deltas: list[dict], book: str) -> None:
    import check_causal_ledger as ccl   # REUSE: INV-12 (leitor) e INV-13 (personagem)
    idx, _ = ccl.build_indices(ledger)
    for f in ccl.check_reader_omniscience(ledger, idx):
        ctx.add("SR-RD-01", "READER_KNOWLEDGE_LEAK", f["severity"], f"cap. {f['chapter']}: {f['evidence']}",
                f["detail"], f["recommended_action"])
    for f in ccl.check_information_leak(ledger, idx):
        ctx.add("SR-KN-01", "CHARACTER_KNOWLEDGE_LEAK", f["severity"], f"cap. {f['chapter']}: {f['evidence']}",
                f["detail"], f["recommended_action"])

    provenance = {(d.get("event"), d.get("knower"), d.get("token")): d for d in deltas
                  if d.get("type") == "KNOWLEDGE_PROVENANCE"}
    all_ids = set(ctx.records) | set(ctx.mysteries) | set(ctx.rumors)
    learned: dict[str, set[str]] = {}
    for ev in events_sorted(ledger):
        eid, chapter = ev.get("id"), ev.get("chapter")
        for kd in ev.get("knowledge_delta") or []:
            knower = kd.get("knower")
            reader = knower == "READER"
            for tok in kd.get("learns") or []:
                modality, base = parse_token(tok)
                if not is_sr_id(base):
                    continue           # GT-*, EV-*, CART:* … são do ledger e da cartografia
                where = f"cap. {chapter}: {eid} {knower} learns {tok}"
                if base.startswith("ITM-"):
                    pass               # itens físicos: Slice 3
                elif base not in all_ids:
                    ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", where,
                            "Conhecimento de id que não existe no canon da obra.",
                            "Corrigir o id; fato novo entra por proposta, nunca por knowledge_delta.")
                    continue
                kind = record_kind(base)
                if kind == "UNKNOWN":
                    rec = ctx.records[base]
                    if book == "B1" and rec.get("unlock") == "B1_LOCKED":
                        cat, rule = "BOOK1_HISTORY_LOCK_VIOLATION", "SR-KN-03"
                    else:
                        cat, rule = ("READER_KNOWLEDGE_LEAK", "SR-RD-02") if reader else ("PREMATURE_MYSTERY_REVEAL", "SR-KN-03")
                    ctx.add(rule, cat, "BLOCKER", where,
                            f"{base} é incógnita ({rec.get('source', {}).get('location')}): não há o que aprender; "
                            "nenhum conhecedor aprende uma incógnita, em nenhuma modalidade.",
                            "Remover; hipótese de personagem é THEORY-*/evidência, nunca UNK-*.")
                    continue
                if kind == "PROHIBITED_INFERENCE" and modality == "KNOWS":
                    ctx.add("SR-ST-01", "UNKNOWN_AS_FACT", "BLOCKER", where,
                            f"{base} é inferência proibida: pode ser crida, suspeitada ou contada, nunca sabida.",
                            "Usar SR:BELIEVES:/SR:SUSPECTS:/SR:TOLD: ou remover.")
                    continue
                reveal = (ctx.records.get(base) or {}).get("reveal") or {}
                minimum = reveal.get("minimum_book")
                if minimum and minimum in BOOK_SCOPES and minimum != book and book < minimum:
                    ctx.add("SR-KN-03", "READER_KNOWLEDGE_LEAK" if reader else "PREMATURE_MYSTERY_REVEAL", "BLOCKER",
                            where, f"{base} só pode ser revelado a partir de {minimum}.", "Remover ou mover.")
                prov = provenance.get((eid, knower, tok))
                if prov is None:
                    ctx.add("SR-KN-02", "KNOWLEDGE_WITHOUT_PROVENANCE", "HIGH", where,
                            "Aquisição de conhecimento de canon sem linha KNOWLEDGE_PROVENANCE (fonte, confiança).",
                            "Declarar em SEM_ROSTO_STATE_DELTAS.yaml de onde o conhecedor aprendeu (SDD 17.5).")
                else:
                    src = str(prov.get("source", ""))
                    if not (PROVENANCE_SOURCE_RE.match(src) or src in all_ids):
                        ctx.add("SR-KN-02", "KNOWLEDGE_WITHOUT_PROVENANCE", "HIGH", f"{prov.get('id')}.source",
                                f"Fonte '{src}' não é EV/EVD/ITM/CHR/STG nem id do canon.", "Corrigir a fonte.")
                    if prov.get("confidence") not in CONFIDENCES:
                        ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{prov.get('id')}.confidence",
                                f"'{prov.get('confidence')}'.", f"{sorted(CONFIDENCES)}.")
                learned.setdefault(knower, set()).add(str(tok))
        # SR-KN-04: agir sobre o que só foi contado
        actor = ev.get("actor")
        for tok in ev.get("acts_on_knowledge") or []:
            modality, base = parse_token(tok)
            have = learned.get(actor, set())
            if modality == "KNOWS" and is_sr_id(base) and tok not in have and f"SR:TOLD:{base}" in have \
                    and f"SR:BELIEVES:{base}" not in have:
                ctx.add("SR-KN-04", "TOLD_AS_KNOWN", "MEDIUM", f"cap. {chapter}: {eid} {actor} acts on {tok}",
                        "O personagem só foi informado (SR:TOLD:), não sabe nem crê.",
                        "Agir sobre SR:TOLD:/SR:BELIEVES:, ou registrar o aprendizado.")

    # proveniência órfã (linha sem knowledge_delta correspondente)
    learned_triples = {(ev.get("id"), kd.get("knower"), str(tok)) for ev in ledger.get("events") or []
                       for kd in ev.get("knowledge_delta") or [] for tok in kd.get("learns") or []}
    for key, prov in provenance.items():
        if key not in learned_triples:
            ctx.add("SR-PV-02", "STATE_WITHOUT_CAUSE", "HIGH", str(prov.get("id")),
                    "KNOWLEDGE_PROVENANCE sem knowledge_delta correspondente no ledger.", "Corrigir evento/conhecedor/token.")


def check_rumor_as_fact(ctx: Context, ledger: dict, interpretive: dict | None) -> None:
    """Uma inferência proibida (com `match`) casada no texto canônico do mundo: `facts` dos eventos do
    ledger e evidência observada pelo NARRADOR. Personagens podem dizer; o mundo não pode afirmar."""
    rumor_pro = {r.get("prohibited_as_fact"): rid for rid, r in ctx.rumors.items() if r.get("prohibited_as_fact")}
    patterns = []
    for rid, rec in ctx.records.items():
        if record_kind(rid) == "PROHIBITED_INFERENCE":
            for m in as_list(rec.get("match")):
                patterns.append((rid, norm_text(m)))
    if not patterns:
        return
    texts = []
    for ev in ledger.get("events") or []:
        for fact in as_list(ev.get("facts")):
            texts.append((f"cap. {ev.get('chapter')}: {ev.get('id')}.facts", fact))
    for evd in as_list((interpretive or {}).get("evidence")):
        if evd.get("source") == "NARRATOR":
            texts.append((f"{evd.get('id')}.observable", evd.get("observable")))
    for where, text in texts:
        low = norm_text(text)
        for pid, pat in patterns:
            if pat and pat in low:
                if pid in rumor_pro:
                    ctx.add("SR-RUM-01", "RUMOR_AS_WORLD_TRUTH", "HIGH", where,
                            f"O texto canônico afirma o conteúdo de {rumor_pro[pid]} ({pid}).",
                            "Atribuir a fala a um personagem (evidência source: CHR-*) ou remover.")
                else:
                    ctx.add("SR-ST-01", "UNKNOWN_AS_FACT", "BLOCKER", where,
                            f"O texto canônico afirma a inferência proibida {pid}.", "Remover.")


def mystery_state(ctx: Context, mid: str, ledger: dict, interpretive: dict | None,
                  at_chapter: int | None = None) -> str:
    mys = ctx.mysteries[mid]
    q = mys.get("interpretive_question")
    if q and interpretive:
        question = next((x for x in as_list(interpretive.get("questions")) if x.get("id") == q), None)
        if question and question.get("resolution_policy") == "RESOLVED_AT":
            return "RESOLVED"
        if question and question.get("resolution_policy") == "LATE_PARTIAL":
            return "PARTIALLY_RESOLVED"
    related = {mid} | set(as_list(mys.get("records"))) | \
              {rid for rid, r in ctx.rumors.items() if mid in as_list(r.get("mysteries"))}
    chapters = {ch for _, _, base, ch in knowledge_of(ledger, "READER", at_chapter) if base in related}
    if not chapters:
        return "UNOPENED"
    return "EXPANDING" if len(chapters) >= 2 else "OPEN"


def check_runtime_mysteries(ctx: Context, ledger: dict, interpretive: dict | None, book: str) -> None:
    for mid, mys in ctx.mysteries.items():
        spec = (mys.get("by_book") or {}).get(book) or {}
        ceiling = spec.get("state_ceiling")
        q = mys.get("interpretive_question")
        if q and interpretive is not None:
            question = next((x for x in as_list(interpretive.get("questions")) if x.get("id") == q), None)
            reserved = mys.get("status") == "RESERVED"
            if question is None:
                ctx.add("SR-CR-05", "UNKNOWN_REFERENCE", "HIGH", f"{mid}.interpretive_question",
                        f"'{q}' não existe no canon interpretativo.", "Corrigir.")
            elif reserved and question.get("resolution_policy") != "NEVER":
                ctx.add("SR-MYS-03", "RESERVED_NOT_NEVER_IN_BOOK", "BLOCKER", f"{mid} → {q}",
                        f"Pergunta de mistério reservado com resolution_policy {question.get('resolution_policy')}.",
                        "NEVER dentro do livro (D-SR-03).")
        if ceiling in STATE_RANK:
            state = mystery_state(ctx, mid, ledger, interpretive)
            if STATE_RANK[state] > STATE_RANK[ceiling]:
                ctx.add("SR-MYS-01", "PREMATURE_RESOLUTION", "BLOCKER", mid,
                        f"Estado projetado {state} acima do teto {ceiling} no {book}.", "Rever a revelação.")


def load_runtime(runtime: Path) -> dict:
    canon = runtime / "canon"
    out = {"ledger": None, "registry": None, "deltas": [], "interpretive": None}
    for key, name in (("ledger", "CAUSAL_LEDGER.yaml"), ("registry", "CANON_REGISTRY.yaml"),
                      ("interpretive", "INTERPRETIVE_CANON.yaml")):
        path = canon / name
        if path.is_file():
            out[key] = load_yaml(path) or {}
    path = canon / "SEM_ROSTO_STATE_DELTAS.yaml"
    if path.is_file():
        doc = load_yaml(path) or {}
        out["deltas_doc"] = doc
        out["deltas"] = as_list(doc.get("deltas"))
    return out


def check_state_deltas(ctx: Context, rt: dict, ledger: dict) -> None:
    doc = rt.get("deltas_doc")
    if doc is None:
        return
    if doc.get("apiVersion") != API_VERSION or doc.get("kind") != "SemRostoStateDeltas":
        ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", "SEM_ROSTO_STATE_DELTAS.kind",
                "Esperado kind SemRostoStateDeltas.", "Corrigir o cabeçalho.")
    events = {ev.get("id"): ev for ev in ledger.get("events") or []}
    seen = set()
    for d in rt["deltas"]:
        did = d.get("id")
        if not did or not re.match(r"^SD-\d+$", str(did)) or did in seen:
            ctx.add("SR-CR-03", "ID_MALFORMED", "HIGH", str(did), "Delta sem id SD-NNNN ou duplicado.", "Corrigir.")
        seen.add(did)
        if d.get("type") not in STATE_DELTA_TYPES:
            ctx.add("SR-CR-04", "INVALID_ENUM", "HIGH", f"{did}.type", f"'{d.get('type')}'.", f"{sorted(STATE_DELTA_TYPES)}.")
        elif d.get("type") not in STATE_DELTA_TYPES_IMPLEMENTED:
            ctx.add("SR-CR-01", "STATE_DELTA_TYPE_PLANNED", "INFO", f"{did}.type",
                    f"Tipo {d.get('type')} ainda sem regras (Slice 3); aceito sem verificação.", "Nada a fazer.")
        ev = events.get(d.get("event"))
        if ev is None:
            ctx.add("SR-PV-02", "STATE_WITHOUT_CAUSE", "HIGH", f"{did}.event", f"Evento '{d.get('event')}' inexistente no ledger.",
                    "Todo delta de estado tem causa num EV-* (SDD 14.2).")
        elif d.get("status") == "REALIZED" and ev.get("status") != "REALIZED":
            ctx.add("SR-PV-02", "STATE_WITHOUT_CAUSE", "HIGH", f"{did}.status",
                    f"Delta REALIZED sobre evento {ev.get('status')}.", "Promover o evento ou voltar o delta a PLANNED.")


def validate(canon_dir: Path | str = DEFAULT_CANON, cartography_dir: Path | str | None = "default",
             runtime: Path | str | None = None, book: str = "B1") -> tuple[list[dict], dict]:
    ctx = build_context(canon_dir, cartography_dir)
    rt_summary = None
    if runtime is not None:
        rt = load_runtime(Path(runtime))
        if rt["ledger"] is None:
            ctx.add("SR-CR-01", "CONTRACT_INVALID", "HIGH", "canon/CAUSAL_LEDGER.yaml",
                    "Modo plan exige o ledger causal do runtime.", "Rodar depois de T018.")
        else:
            check_runtime_knowledge(ctx, rt["ledger"], rt["deltas"], book)
            check_rumor_as_fact(ctx, rt["ledger"], rt["interpretive"])
            check_runtime_mysteries(ctx, rt["ledger"], rt["interpretive"], book)
            check_state_deltas(ctx, rt, rt["ledger"])
        if rt["registry"] is not None:
            check_registry_sync(ctx, rt["registry"])
        rt_summary = {"events": len((rt["ledger"] or {}).get("events") or []), "deltas": len(rt["deltas"])}
    ctx.findings.sort(key=lambda f: (-SEVERITY_ORDER.index(f["severity"]), f["rule"], f["evidence"]))
    kinds: dict[str, int] = {}
    for rid in ctx.records:
        kinds[record_kind(rid)] = kinds.get(record_kind(rid), 0) + 1
    summary = {
        "records": len(ctx.records), "records_by_kind": dict(sorted(kinds.items())), "locks": len(ctx.locks),
        "gates": len(ctx.gate_ids), "mysteries": len(ctx.mysteries), "rumors": len(ctx.rumors),
        "lock_coverage": {k: len(v) for k, v in ctx.coverage.items()},
        "dossier_sections": len(ctx.dossier["sections"]) if ctx.dossier else 0,
        "hidden_keys_source": HIDDEN_KEYS_SOURCE, "implemented_slice": IMPLEMENTED_SLICE,
        "runtime": rt_summary,
    }
    return ctx.findings, summary


def build_context(canon_dir, cartography_dir="default") -> Context:
    canon_dir = Path(canon_dir)
    if cartography_dir == "default":
        cartography_dir = canon_dir.parent / "cartography" / "seeds"
    ctx = Context(canon_dir, Path(cartography_dir) if cartography_dir else None)
    check_sources(ctx)
    load_seeds(ctx)
    index_locks(ctx)
    check_records(ctx)
    ctx.coverage = check_locks(ctx)
    check_gates(ctx)
    index_mysteries_and_rumors(ctx)
    check_mysteries(ctx)
    check_rumors(ctx)
    check_approvals(ctx)
    return ctx


# --- consultas (SDD seção 73) — visão padrão: ids e enunciados, nunca conteúdo engine-only ---------

def query_is_true(ctx: Context, needle: str) -> dict:
    def answer(kind, ident, verdict, extra=None):
        rec = ctx.records.get(ident) or ctx.rumors.get(ident) or ctx.mysteries.get(ident) or {}
        out = {"query": needle, "answer": verdict, "id": ident, "kind": kind,
               "source": (rec.get("source") or {}).get("location")}
        out.update(extra or {})
        return out

    ident = needle.strip()
    if ident in ctx.records:
        rec, kind = ctx.records[ident], record_kind(ident)
        if kind == "UNKNOWN":
            return answer(kind, ident, "CANON_UNKNOWN", {"question": rec.get("question")})
        if kind == "CAPABILITY":
            return answer(kind, ident, "CAPABILITY_ONLY", {"statement": rec.get("statement"), "instances": rec.get("instances")})
        if kind == "PROHIBITED_INFERENCE":
            return answer(kind, ident, "FALSE", {"statement": rec.get("statement")})
        return answer(kind, ident, f"TRUE ({rec.get('epistemic_class', 'FACT')})", {"statement": rec.get("statement")})
    if ident in ctx.rumors:
        rum = ctx.rumors[ident]
        return answer("RUMOR", ident, f"CLAIMED_AS ({rum.get('epistemic_class')})",
                      {"statement": rum.get("statement_neutral"), "truth_relation": rum.get("truth_relation")})
    if ident in ctx.mysteries:
        return answer("MYSTERY", ident, "OPEN_QUESTION", {"question": ctx.mysteries[ident].get("question")})
    low = norm_text(needle)
    for rid, rec in ctx.records.items():
        if record_kind(rid) == "PROHIBITED_INFERENCE":
            pats = [norm_text(m) for m in as_list(rec.get("match"))] + [norm_text(rec.get("statement", ""))]
            if any(p and p in low for p in pats) or low == norm_text(rec.get("statement", "")):
                return answer("PROHIBITED_INFERENCE", rid, "FALSE", {"statement": rec.get("statement")})
        if norm_text(rec.get("title", "")) == low:
            return query_is_true(ctx, rid)
    return {"query": needle, "answer": "NOT_IN_CANON", "next": "CANON_PROPOSAL_REQUIRED",
            "note": "O sistema não adivinha por similaridade: nada no canon resolve este texto."}


def query_who_knows(ctx: Context, ledger: dict, token: str, at_chapter: int | None) -> list[dict]:
    knowers = {kd.get("knower") for ev in ledger.get("events") or [] for kd in ev.get("knowledge_delta") or []}
    out = []
    for knower in sorted(k for k in knowers if k):
        for tok, modality, base, chapter in knowledge_of(ledger, knower, at_chapter):
            if tok == token or base == token:
                out.append({"knower": knower, "modality": modality, "token": tok, "since_chapter": chapter})
    return out


def query_reader_at(ctx: Context, ledger: dict, chapter: int) -> dict:
    facts, rumors, beliefs, other = [], [], [], []
    for tok, modality, base, ch in knowledge_of(ledger, "READER", chapter):
        if base in ctx.rumors:
            (rumors if modality == "KNOWS" else beliefs).append(tok)
        elif is_sr_id(base) and modality == "KNOWS":
            facts.append(tok)
        elif is_sr_id(base):
            beliefs.append(tok)
        else:
            other.append(tok)
    blocked = sorted(rid for rid in ctx.records if record_kind(rid) == "UNKNOWN")
    return {"chapter": chapter, "facts_seen": facts, "rumors_seen": rumors, "beliefs_supported": beliefs,
            "ledger_tokens": other, "cannot_know": len(blocked),
            "note": "Visão padrão: sem conteúdo engine-only (GT, crenças com truth)."}


def query_mystery(ctx: Context, mid: str, ledger: dict | None, interpretive: dict | None, at_chapter: int | None) -> dict:
    mys = ctx.mysteries.get(mid)
    if mys is None:
        return {"mystery": mid, "error": "inexistente"}
    out = {"mystery": mid, "question": mys.get("question"), "status": mys.get("status"),
           "minimum_book": mys.get("minimum_book"),
           "b1_ceiling": ((mys.get("by_book") or {}).get("B1") or {}).get("state_ceiling"),
           "unknowns": as_list(mys.get("unknown_refs")), "forbidden_gates": as_list(mys.get("forbidden_gates")),
           "source": (mys.get("source") or {}).get("location")}
    if ledger is not None:
        out["projected_state"] = mystery_state(ctx, mid, ledger, interpretive, at_chapter)
    return out


def render(findings: list[dict], summary: dict, canon_dir: Path) -> str:
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_ORDER}
    blocked = counts["HIGH"] + counts["BLOCKER"]
    lines = [
        f"# SEM ROSTO — relatório de canon (modo {'plan' if summary.get('runtime') else 'package'})",
        "",
        f"- canon: `{canon_dir}`",
        f"- registros: {summary['records']} {summary['records_by_kind']}",
        f"- locks: {summary['locks']} (com detector implementado/motor: {summary['lock_coverage']['implemented']}, "
        f"só planejado: {summary['lock_coverage']['planned_only']}, só julgamento: {summary['lock_coverage']['judgment_only']})",
        f"- gates: {summary['gates']} · mistérios: {summary['mysteries']} · rumores/teorias: {summary['rumors']} · "
        f"seções do dossiê indexadas: {summary['dossier_sections']}",
        *( [f"- runtime: {summary['runtime']['events']} eventos, {summary['runtime']['deltas']} deltas de estado"]
           if summary.get("runtime") else [] ),
        f"- achados: " + ", ".join(f"{s} {counts[s]}" for s in reversed(SEVERITY_ORDER)),
        f"- resultado: **{'FAIL' if blocked else ('PASS_WITH_WARNINGS' if findings else 'PASS')}**",
        "",
    ]
    for f in findings:
        lines.append(f"- [{f['severity']}] {f['rule']} {f['category']} — `{f['evidence']}`: {f['detail']} → {f['recommended_action']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split(chr(10) * 2)[0])
    parser.add_argument("--mode", default="package", choices=["package", "plan"])
    parser.add_argument("--canon", default=str(DEFAULT_CANON))
    parser.add_argument("--cartography", default="default",
                        help="seeds da cartografia para conferir map_refs (padrão: <canon>/../cartography/seeds)")
    parser.add_argument("--runtime", default=None, help="runtime com canon/CAUSAL_LEDGER.yaml (modo plan e consultas)")
    parser.add_argument("--book", default="B1", choices=sorted(BOOK_SCOPES - {"SERIES"}))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--is-true", dest="is_true")
    parser.add_argument("--who-knows", dest="who_knows")
    parser.add_argument("--reader-at", dest="reader_at", type=int)
    parser.add_argument("--mystery")
    parser.add_argument("--at-chapter", dest="at_chapter", type=int)
    parser.add_argument("--emit-registry-fragment", dest="emit_fragment", action="store_true")
    args = parser.parse_args(argv)

    queries = (args.is_true, args.who_knows, args.reader_at, args.mystery, args.emit_fragment)
    if any(q not in (None, False) for q in queries):
        ctx = build_context(args.canon, args.cartography)
        rt = load_runtime(Path(args.runtime)) if args.runtime else None
        ledger = (rt or {}).get("ledger")
        if args.emit_fragment:
            print(yaml.safe_dump(registry_fragment(ctx), allow_unicode=True, sort_keys=False), end="")
            return 0
        if args.is_true is not None:
            result = query_is_true(ctx, args.is_true)
        elif args.mystery:
            result = query_mystery(ctx, args.mystery, ledger, (rt or {}).get("interpretive"), args.at_chapter)
        else:
            if ledger is None:
                print("consulta exige --runtime com canon/CAUSAL_LEDGER.yaml", file=sys.stderr)
                return 2
            result = (query_who_knows(ctx, ledger, args.who_knows, args.at_chapter) if args.who_knows
                      else query_reader_at(ctx, ledger, args.reader_at))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.mode == "plan" and not args.runtime:
        parser.error("--mode plan exige --runtime")
    findings, summary = validate(args.canon, args.cartography, args.runtime if args.mode == "plan" else None, args.book)
    if args.json:
        print(json.dumps({"summary": summary, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        print(render(findings, summary, Path(args.canon)), end="")
    return 1 if any(f["severity"] in BLOCKING for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
