"""Validador do canon cartográfico (capability neutra `features.cartography`).

Slices 1–2 de docs/sdd/*CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md: contrato, integridade do grafo,
proteção de mistério e consultas de viagem. NÃO contém nome de nenhuma obra: o que é de uma obra
mora nos seeds (books/<slug>/cartography/seeds/).

Regras (SDD 29.3):
  CG  integridade: arestas, ids, origem, tipos, fontes, inventário, registro
  CX  física: subsolo com entrada, aresta mais curta que a euclidiana, travessia de água sem estrutura
  MY  proteção de mistério: nenhuma resposta escondida, nenhuma saída "verdadeira", nenhuma
      interpretação promovida a fato, autoria protegida
  CN  coordenada divergente da derivada de `source_px`; mutação sem proposta/causa
  TR/AC/KN/HD  deslocamento, acesso, conhecimento e esconderijo (`--check-staging`, cartography_graph.py)

S4: `--exits`, `--exit-truth`, `--reader-map`, `--reader-gap`, `--belief`, `--check-prose` (cartography_maps.py).
Ainda não faz (Slice 5): pack de cena e integração no compose.

Princípio: coordenadas em metros nunca são digitadas — DERIVAM de `source_px` + escala da fonte.

Uso:
    python engine/scripts/check_cartography.py --canon books/<slug>/cartography/seeds
    python engine/scripts/check_cartography.py --canon <dir> --coords
    python engine/scripts/check_cartography.py --canon <dir> --json
    python engine/scripts/check_cartography.py --canon <dir> --route A B --actor CHR-X --lighting NIGHT_DARK
    python engine/scripts/check_cartography.py --canon <dir> --reachable A B | --time A B | --escape-routes A
    python engine/scripts/check_cartography.py --canon <dir> --check-staging STAGING.yaml

Sem dependências novas: biblioteca padrão + PyYAML.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import yaml

SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "BLOCKER"]
BLOCKING = {"HIGH", "BLOCKER"}

API_VERSION = "pedroarte.livingbooks/v1"
CANON_KIND = "CartographyCanon"
MANIFEST_NAME = "CARTOGRAPHY.seed.yaml"

# --- vocabulário fechado (SDD seções 12–21) ----------------------------------

BASE_TYPES = {
    "TOWN", "VILLAGE", "HAMLET", "ESTATE", "FARM", "COTTAGE", "HOUSE", "BOTHY", "CHAPEL",
    "CEMETERY", "CRYPT", "PUB", "SHOP", "GOVERNMENT_BUILDING", "ARCHIVE", "CLINIC", "POLICE",
    "ROAD", "TRAIL", "BRIDGE", "FOREST", "MOOR", "FIELD", "QUARRY", "RIVER", "BURN", "LAKE",
    "RESERVOIR", "MARSH", "RUIN", "TUNNEL", "CULVERT", "STORM_DRAIN", "CELLAR",
    "SUBTERRANEAN_PASSAGE", "BOUNDARY", "ROADBLOCK", "OUTPOST", "UNKNOWN",
}
LAYERS = {"URBAN", "REGIONAL", "SUBTERRANEAN"}
GEOMETRIES = {"POINT", "AREA", "LINE"}
LOCATION_STATUS = {"ACTIVE", "ABANDONED", "RUINED", "SEALED", "RESTRICTED", "DISPUTED", "UNKNOWN"}
EDGE_TYPES = {
    "ROAD", "TRAIL", "FOREST_PATH", "TUNNEL", "DRAIN", "SECRET_PASSAGE", "BRIDGE",
    "WATER_ROUTE", "SERVICE_ROUTE", "PORTAL", "FRAME_LINK", "OPEN_GROUND",
}
DIRECTIONALITY = {"BOTH", "A_TO_B", "B_TO_A"}
EPISTEMIC = {"FACT", "OFFICIAL_CLAIM", "HISTORICAL_CLAIM", "RUMOR", "MYSTERY", "FALSE_MAP_DATA", "UNKNOWN"}
EXIT_CLASSES = {
    "APPARENT_EXIT", "OFFICIAL_EXIT", "HISTORICAL_EXIT", "CLOSED_EXIT",
    "DISPUTED_EXIT", "FALSE_EXIT", "UNKNOWN_EXIT",
}
RESOLUTION_STATES = {"UNRESOLVED", "PARTIALLY_RESOLVED", "RESOLVED", "PERMANENTLY_AMBIGUOUS"}
ANOMALY_CLASSES = {"UNDECIDED", "INTENTIONAL_ARTIFACT", "RENDER_ERROR"}
BOUNDARY_KINDS = {"UNCERTAIN_LIMIT", "ADMINISTRATIVE", "RESTRICTED_ZONE", "NATURAL", "MAP_FRAME"}
ARTIFACT_KINDS = {"MAP", "TEXT", "FIGURE", "GLYPH_SET", "MARKER", "ORNAMENT", "REGISTER"}
ORDERING_SIGNIFICANCE = {"UNKNOWN", "ADMINISTRATIVE", "CHRONOLOGICAL", "CARTOGRAPHIC", "ENCRYPTED", "DECOY"}
REGISTER_PLACEMENTS = {"ON_MAP", "NOT_ON_MAP", "NO_STANDALONE_LABEL"}
INSTITUTIONAL_LAYERS = {"LYR-MODERN-OFFICIAL", "LYR-EARLY-PRESERVATION"}

# chaves que nunca podem guardar resposta (REUSE do canon interpretativo + extensão cartográfica)
_FALLBACK_HIDDEN_KEYS = {
    "truth", "answer", "correct", "correct_answer", "canonical_answer", "author_answer",
    "hidden_answer", "intended", "intended_reading", "true_nature", "real_identity",
    "resposta", "resposta_correta", "verdade",
}
try:  # pragma: no cover - depende do working tree
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from check_interpretive_canon import HIDDEN_ANSWER_KEYS as _IC_KEYS  # type: ignore
except Exception:  # noqa: BLE001
    _IC_KEYS = set()
CARTO_ANSWER_KEYS = {
    "true_exit", "real_exit", "saida_verdadeira", "actual_pattern", "solution", "solucao",
    "decoded", "decoding", "real_route", "verdadeira", "actual_author", "true_author",
}
HIDDEN_ANSWER_KEYS = set(_FALLBACK_HIDDEN_KEYS) | set(_IC_KEYS) | CARTO_ANSWER_KEYS
EVALUATION_KEYS = {"plausible", "true", "false", "score", "verdade", "correct", "likelihood", "probability"}

TRUE_EXIT_RE = re.compile(
    r"(true[\s_\-]?exit|real[\s_\-]?exit|sa[ií]da[\s_\-]?verdadeira|verdadeira[\s_\-]?sa[ií]da)", re.I)
SUPERNATURAL_RE = re.compile(
    r"(teleport|teletransport|m[aá]gic|magic|sobrenatural|supernatural|fantasma|ghost|"
    r"geometria[\s_\-]?imposs[ií]vel|impossible[\s_\-]?geometry)", re.I)
VERBATIM_KEYS = {"text", "motto", "printed_name", "printed_text"}

LIST_KEYS = (
    "locations", "edges", "roads", "routes", "addresses", "sightlines", "hideouts", "boundaries",
    "exits", "route_mysteries", "mysteries", "artifacts", "layers", "anomalies", "glyphs",
    "unlabeled", "baseline", "inventory",
)

DEFAULT_ACCURACY = {"POINT": 60, "AREA": 150, "LINE": 60}


# ----------------------------------------------------------------------------
# utilidades
# ----------------------------------------------------------------------------

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


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def normalize_key(key) -> str:
    return re.sub(r"[^a-z0-9]+", "_", strip_accents(str(key)).lower()).strip("_")


def normalize_name(name) -> str:
    return re.sub(r"[^a-z0-9]+", " ", strip_accents(str(name)).lower()).strip()


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------------
# carga
# ----------------------------------------------------------------------------

def load_model(canon_dir: Path) -> dict:
    """Lê o manifesto e todos os seeds incluídos; concatena as listas por chave."""
    canon_dir = Path(canon_dir)
    manifest_path = canon_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        raise FileNotFoundError(f"manifesto ausente: {manifest_path}")
    manifest = load_yaml(manifest_path) or {}
    model: dict = {"manifest": manifest, "_dir": canon_dir, "_files": [manifest_path.name]}
    for key in LIST_KEYS:
        model[key] = []
    model["register"] = None
    for name in as_list(manifest.get("includes")):
        path = canon_dir / f"{name}.seed.yaml"
        if not path.is_file():
            model.setdefault("_missing_includes", []).append(str(path.name))
            continue
        model["_files"].append(path.name)
        data = load_yaml(path) or {}
        for key in LIST_KEYS:
            model[key].extend(as_list(data.get(key)))
        if isinstance(data.get("register"), dict):
            model["register"] = data["register"]
    sources_rel = (manifest.get("metadata") or {}).get("sources")
    model["sources"] = None
    model["_sources_dir"] = None
    if sources_rel:
        sp = (canon_dir / sources_rel).resolve()
        if sp.is_file():
            model["sources"] = load_yaml(sp)
            model["_sources_dir"] = sp.parent
    return model


def all_id_carriers(model: dict):
    for key in LIST_KEYS:
        if key in ("inventory", "baseline"):   # apontam para ids; não são entidades com id próprio
            continue
        for item in model.get(key) or []:
            if isinstance(item, dict):
                yield key, item
    reg = model.get("register")
    if isinstance(reg, dict):
        for item in reg.get("entries") or []:
            if isinstance(item, dict):
                yield "register", item


def index_by_id(items) -> dict:
    return {i["id"]: i for i in items if isinstance(i, dict) and i.get("id")}


# ----------------------------------------------------------------------------
# projeção de coordenadas (derivadas, nunca digitadas)
# ----------------------------------------------------------------------------

def source_scales(model: dict) -> dict:
    out = {}
    for s in as_list((model.get("sources") or {}).get("sources")):
        scale = (s.get("scale_evidence") or {}).get("meters_per_px")
        origin = s.get("origin_px")
        if s.get("id") and scale and origin:
            out[s["id"]] = {"mpp": float(scale), "origin": (float(origin[0]), float(origin[1]))}
    return out


def project_px(scales: dict, source_id: str, px) -> tuple[float, float] | None:
    sc = scales.get(source_id)
    if not sc or not px or len(px) != 2:
        return None
    x = (float(px[0]) - sc["origin"][0]) * sc["mpp"]
    y = (sc["origin"][1] - float(px[1])) * sc["mpp"]
    return x, y


def project_location(model: dict, loc: dict, _seen=None) -> dict | None:
    """{x, y, accuracy_m, basis, source} ou None (posição desconhecida/declarada nula)."""
    scales = source_scales(model)
    locs = index_by_id(model["locations"])
    _seen = _seen or set()
    if loc.get("id") in _seen:
        return None
    _seen = _seen | {loc.get("id")}
    anchor = loc.get("anchor_to")
    if anchor:
        target = locs.get(anchor)
        return project_location(model, target, _seen) if target else None
    entries = [e for e in as_list(loc.get("source_px")) if isinstance(e, dict)]
    geometry = loc.get("geometry") or "POINT"
    acc_override = loc.get("position_accuracy_m")
    for wanted in ("SRC-MAP-A", None):
        for e in entries:
            if e.get("anchor") == "SCHEMATIC":
                continue
            if wanted and e.get("source") != wanted:
                continue
            xy = project_px(scales, e.get("source"), e.get("px"))
            if xy is None:
                continue
            is_b = e.get("source") != "SRC-MAP-A"
            acc = acc_override if acc_override is not None else (840 if is_b else DEFAULT_ACCURACY.get(geometry, 60))
            return {"x": xy[0], "y": xy[1], "accuracy_m": acc, "basis": e.get("source"), "source": e.get("source")}
    pl = as_list(loc.get("polyline_px"))
    if pl and isinstance(pl[0], dict):
        pts = [project_px(scales, p.get("source"), p.get("px")) for p in pl]
        pts = [p for p in pts if p]
        if pts:
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            src = pl[0].get("source")
            return {"x": cx, "y": cy, "accuracy_m": acc_override or (840 if src != "SRC-MAP-A" else 60),
                    "basis": src, "source": src}
    return None


def project_all(model: dict) -> dict:
    return {loc["id"]: project_location(model, loc) for loc in model["locations"] if loc.get("id")}


def euclid(a: dict, b: dict) -> float:
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


# ----------------------------------------------------------------------------
# regras
# ----------------------------------------------------------------------------

def check_structure(model: dict) -> list[dict]:
    out = []
    m = model["manifest"]
    if m.get("apiVersion") != API_VERSION or m.get("kind") != CANON_KIND:
        out.append(finding("MANIFEST_INVALID", "BLOCKER", None, f"{m.get('apiVersion')}/{m.get('kind')}",
                           f"O manifesto precisa declarar apiVersion {API_VERSION} e kind {CANON_KIND}.",
                           "Corrigir o cabeçalho de CARTOGRAPHY.seed.yaml."))
    for name in model.get("_missing_includes", []):
        out.append(finding("INCLUDE_MISSING", "BLOCKER", None, name,
                           "O manifesto inclui um seed que não existe.", "Criar o arquivo ou remover o include."))
    if model.get("sources") is None:
        out.append(finding("SOURCES_MISSING", "BLOCKER", None, "metadata.sources",
                           "SOURCES.yaml não encontrado a partir do manifesto.", "Apontar metadata.sources."))
    return out


def check_ids(model: dict) -> list[dict]:
    out = []
    seen: dict[str, str] = {}
    for kind, item in all_id_carriers(model):
        iid = item.get("id")
        if not iid:
            out.append(finding("ID_MISSING", "HIGH", None, f"{kind}: {str(item)[:60]}",
                               "Entidade sem id.", "Atribuir id estável."))
            continue
        if iid in seen:
            out.append(finding("CG-02 DUPLICATE_ID", "BLOCKER", None, iid,
                               f"Id repetido ({seen[iid]} e {kind}).", "Ids são únicos e nunca reutilizados."))
        seen[iid] = kind
    return out


def check_origin(model: dict, proj: dict) -> list[dict]:
    origin = ((model["manifest"].get("metadata") or {}).get("grid") or {}).get("origin")
    locs = index_by_id(model["locations"])
    if not origin or origin not in locs:
        return [finding("CG-03 ORIGIN_NOT_ZERO", "BLOCKER", None, str(origin),
                        "O manifesto precisa declarar grid.origin apontando para um lugar existente.",
                        "Declarar a origem do grid.")]
    p = proj.get(origin)
    if p is None or abs(p["x"]) > 1e-6 or abs(p["y"]) > 1e-6:
        return [finding("CG-03 ORIGIN_NOT_ZERO", "BLOCKER", None, origin,
                        f"A origem projeta para {None if p is None else (round(p['x'], 3), round(p['y'], 3))}, não (0, 0).",
                        "A origem é (0, 0) por definição: corrigir source_px ou origin_px da fonte.")]
    return []


def check_types_and_fields(model: dict) -> list[dict]:
    out = []
    exts = set(as_list((model["manifest"].get("metadata") or {}).get("type_extensions")))
    allowed = BASE_TYPES | exts
    for loc in model["locations"]:
        lid = loc.get("id", "?")
        types = as_list(loc.get("type"))
        if not types:
            out.append(finding("CG-04 UNKNOWN_TYPE", "HIGH", None, lid, "Lugar sem type.", "Declarar type."))
        for t in types:
            if t not in allowed:
                out.append(finding("CG-04 UNKNOWN_TYPE", "HIGH", None, f"{lid}.type={t}",
                                   "Tipo fora do vocabulário base e das extensões aprovadas.",
                                   "Usar tipo existente ou registrar extensão justificada no manifesto."))
        if loc.get("layer") not in LAYERS:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{lid}.layer={loc.get('layer')!r}",
                               f"layer ∈ {sorted(LAYERS)}.", "Corrigir layer."))
        if loc.get("geometry", "POINT") not in GEOMETRIES:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{lid}.geometry={loc.get('geometry')!r}",
                               f"geometry ∈ {sorted(GEOMETRIES)}.", "Corrigir geometry."))
        if loc.get("status", "UNKNOWN") not in LOCATION_STATUS:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{lid}.status={loc.get('status')!r}",
                               f"status ∈ {sorted(LOCATION_STATUS)}.", "Corrigir status."))
        if loc.get("epistemic_status", "FACT") not in EPISTEMIC:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{lid}.epistemic_status",
                               f"epistemic_status ∈ {sorted(EPISTEMIC)}.", "Corrigir."))
    for e in model["edges"]:
        eid = e.get("id", "?")
        if e.get("edge_type") not in EDGE_TYPES:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{eid}.edge_type={e.get('edge_type')!r}",
                               f"edge_type ∈ {sorted(EDGE_TYPES)}.", "Corrigir."))
        if e.get("directionality", "BOTH") not in DIRECTIONALITY:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{eid}.directionality",
                               f"directionality ∈ {sorted(DIRECTIONALITY)}.", "Corrigir."))
    return out


def check_positions(model: dict, proj: dict) -> list[dict]:
    """CG-05 (coordenada sem fonte) e CN-05 (cache diverge da derivada)."""
    out = []
    for loc in model["locations"]:
        lid = loc.get("id", "?")
        p = proj.get(lid)
        declared_null = loc.get("coordinates", "unset") is None or loc.get("position") == "UNKNOWN"
        is_frame_or_off = any(t in ("OFF_MAP_DESTINATION",) for t in as_list(loc.get("type")))
        if p is None and not declared_null and not is_frame_or_off and loc.get("source") != "AUTHOR_DECLARED" \
                and "JUNCTION" not in as_list(loc.get("type")) and loc.get("geometry") != "AGGREGATE":
            out.append(finding("CG-05 COORD_WITHOUT_SOURCE", "HIGH", None, lid,
                               "Lugar sem source_px derivável, sem anchor_to e sem declaração explícita de posição nula.",
                               "Registrar source_px (fonte + pixel do ícone) ou declarar `position: UNKNOWN`."))
        cache = loc.get("coordinates_cache")
        if isinstance(cache, dict) and p is not None:
            dx, dy = float(cache.get("x", 0)) - p["x"], float(cache.get("y", 0)) - p["y"]
            tol = max(p["accuracy_m"], 1.0)
            if math.hypot(dx, dy) > tol:
                out.append(finding("CN-05 MAP_POSITION_CONTRADICTION", "BLOCKER", None, lid,
                                   f"coordinates_cache ({cache.get('x')}, {cache.get('y')}) diverge da derivada "
                                   f"({round(p['x'])}, {round(p['y'])}) por mais que a precisão ({tol} m).",
                                   "Coordenadas são derivadas de source_px; remover ou regenerar o cache."))
        if p is None and isinstance(cache, dict):
            out.append(finding("CG-05 COORD_WITHOUT_SOURCE", "HIGH", None, lid,
                               "coordinates_cache sem posição derivável.", "Remover o cache ou registrar a fonte."))
    return out


def check_sources(model: dict) -> list[dict]:
    out = []
    src = model.get("sources") or {}
    base = model.get("_sources_dir")
    scales = source_scales(model)
    for s in as_list(src.get("sources")):
        sid = s.get("id", "?")
        f = s.get("file")
        if not f or base is None:
            out.append(finding("CG-06 SOURCE_HASH_MISMATCH", "BLOCKER", None, sid, "Fonte sem arquivo.", "Declarar file."))
            continue
        path = Path(base) / f
        if not path.is_file():
            out.append(finding("CG-06 SOURCE_HASH_MISMATCH", "BLOCKER", None, f"{sid}:{f}",
                               "Arquivo da fonte não encontrado.", "Restaurar o arquivo pinado."))
            continue
        actual = sha256_file(path)
        if actual != s.get("sha256"):
            out.append(finding("CG-06 SOURCE_HASH_MISMATCH", "BLOCKER", None, sid,
                               f"sha256 do arquivo ({actual[:12]}…) difere do pinado ({str(s.get('sha256'))[:12]}…).",
                               "Fontes não se editam: criar nova versão (SRC@v1.1) com `supersedes`."))
    # razão de escala entre os mapas (decisão OQ-CART-01): A = ratio × B
    for xf in as_list(src.get("transforms")):
        ratio = xf.get("scale_ratio_A_to_B")
        if ratio is None:
            continue
        a, b = scales.get("SRC-MAP-A"), scales.get(xf.get("source"))
        if a and b:
            expected = a["mpp"] / float(ratio)
            if abs(b["mpp"] - expected) / expected > 0.005:
                out.append(finding("CG-13 SCALE_RATIO_MISMATCH", "BLOCKER", None, xf.get("id", "?"),
                                   f"meters_per_px do Mapa B ({b['mpp']}) ≠ A/ratio ({expected:.2f}).",
                                   "A escala do Mapa B é derivada da razão declarada; corrigir uma das duas."))
    return out


def check_edges(model: dict, proj: dict) -> list[dict]:
    out = []
    locs = index_by_id(model["locations"])
    for e in model["edges"]:
        eid = e.get("id", "?")
        a, b = e.get("from"), e.get("to")
        for end in (a, b):
            if end not in locs:
                out.append(finding("CG-01 EDGE_DANGLING", "BLOCKER", None, f"{eid}: {end}",
                                   "Aresta aponta para nó inexistente.", "Criar o nó ou corrigir a aresta."))
        if a in locs and b in locs:
            la, lb = locs[a], locs[b]
            if la.get("layer") != lb.get("layer") and e.get("edge_type") not in ("PORTAL", "FRAME_LINK"):
                out.append(finding("CG-07 CROSS_LAYER_WITHOUT_PORTAL", "BLOCKER", None, eid,
                                   f"Liga camadas {la.get('layer')} e {lb.get('layer')} sem ser PORTAL/FRAME_LINK.",
                                   "Escalas só se conectam por portal."))
            pa, pb = proj.get(a), proj.get(b)
            dist = (e.get("distance_meters") or {})
            if pa and pb and isinstance(dist, dict) and dist.get("min") is not None \
                    and e.get("edge_type") not in ("PORTAL", "FRAME_LINK"):
                floor = euclid(pa, pb) - pa["accuracy_m"] - pb["accuracy_m"]
                if float(dist["min"]) < floor - 1e-6:
                    out.append(finding("CX-04 EDGE_SHORTER_THAN_EUCLID", "HIGH", None, eid,
                                       f"distance_meters.min={dist['min']} < distância euclidiana menos precisões ({round(floor)} m).",
                                       "Uma via não pode ser mais curta que a linha reta entre as pontas."))
    return out


def check_subterranean(model: dict) -> list[dict]:
    """CX-02: componente subterrâneo precisa de entrada física; UNDECLARED é isento e inerte."""
    out = []
    locs = index_by_id(model["locations"])
    sub = {i for i, l in locs.items() if l.get("layer") == "SUBTERRANEAN"}
    adj = defaultdict(set)
    portal_of = defaultdict(int)
    for e in model["edges"]:
        a, b = e.get("from"), e.get("to")
        if e.get("edge_type") == "PORTAL":
            for end, other in ((a, b), (b, a)):
                if end in sub and other in locs and locs[other].get("layer") != "SUBTERRANEAN":
                    portal_of[end] += 1
        elif a in sub and b in sub:
            adj[a].add(b)
            adj[b].add(a)
    seen: set[str] = set()
    for start in sorted(sub):
        if start in seen:
            continue
        comp, stack = set(), [start]
        while stack:
            n = stack.pop()
            if n in comp:
                continue
            comp.add(n)
            stack.extend(adj[n] - comp)
        seen |= comp
        undeclared = all(locs[n].get("connectivity") == "UNDECLARED" for n in comp)
        has_portal = any(portal_of[n] for n in comp)
        if not has_portal and not undeclared:
            out.append(finding("CX-02 SUBTERRANEAN_WITHOUT_PORTAL", "BLOCKER", None, ", ".join(sorted(comp)),
                               "Componente subterrâneo sem nenhuma entrada física (portal para a superfície).",
                               "Declarar o portal ou marcar `connectivity: UNDECLARED` (nó inerte)."))
    for i in sorted(sub):
        if locs[i].get("connectivity") == "UNDECLARED" and (adj[i] or portal_of[i]):
            out.append(finding("CONNECTIVITY_UNDECLARED_HAS_EDGES", "HIGH", None, i,
                               "Nó `connectivity: UNDECLARED` mas com arestas.",
                               "Passar a `connectivity: DECLARED` por proposta aprovada, ou remover as arestas."))
    return out


def check_orphans(model: dict) -> list[dict]:
    """CG-10. `edges_digitized` pode ser booleano ou {LAYER: bool}: só camadas digitalizadas exigem arestas."""
    meta = model["manifest"].get("metadata") or {}
    flag = meta.get("edges_digitized")
    touched = set()
    for e in model["edges"]:
        touched.update([e.get("from"), e.get("to")])

    def digitized(layer):
        return bool(flag.get(layer)) if isinstance(flag, dict) else bool(flag)

    orphans = [l for l in model["locations"]
               if l.get("id") and l.get("id") not in touched
               and "JUNCTION" not in as_list(l.get("type"))
               and l.get("geometry", "POINT") == "POINT"
               and l.get("source") != "AUTHOR_DECLARED"
               and "OFF_MAP_DESTINATION" not in as_list(l.get("type"))]
    hard = [l["id"] for l in orphans if digitized(l.get("layer"))]
    soft = [l["id"] for l in orphans if not digitized(l.get("layer"))]
    out = []
    if hard:
        out.append(finding("CG-10 ORPHAN_NODE", "MEDIUM", None, f"{len(hard)} nó(s): {', '.join(sorted(hard)[:8])}",
                           "Nós pontuais sem nenhuma aresta em camada já digitalizada.", "Ligar ou justificar cada nó."))
    if soft:
        out.append(finding("CG-10 ORPHAN_NODE", "INFO", None, f"{len(soft)} nó(s) sem aresta",
                           "Nós pontuais sem aresta em camada ainda não digitalizada.", "Digitalizar as vias que os ligam."))
    return out


def check_names(model: dict) -> list[dict]:
    out = []
    seen: dict[str, str] = {}
    for loc in model["locations"]:
        lid = loc.get("id", "?")
        names = {normalize_name(n.get("name") if isinstance(n, dict) else n)
                 for n in as_list(loc.get("names")) + [loc.get("canonical_name")] if n}
        for n in sorted(x for x in names if x):
            if n in seen and seen[n] != lid and not loc.get("shared_name_ok"):
                out.append(finding("CG-09 NAME_COLLISION", "BLOCKER", None, f"{n!r}: {seen[n]} × {lid}",
                                   "O mesmo nome normalizado em dois lugares.",
                                   "Diferenciar, ou declarar `shared_name_ok` com aprovação."))
            seen.setdefault(n, lid)
    return out


def check_inventory(model: dict) -> list[dict]:
    """CG-08: cada item do inventário de transcrição resolve para uma entidade."""
    ids = {item.get("id") for _, item in all_id_carriers(model)}
    out = []
    for inv in model["inventory"]:
        target = inv.get("maps_to")
        if target not in ids:
            out.append(finding("CG-08 INVENTORY_ITEM_UNMAPPED", "BLOCKER", None,
                               f"{inv.get('item')!r} → {target}",
                               "Item transcrito dos mapas sem entidade correspondente.",
                               "Criar o nó/artefato/registro ou corrigir maps_to."))
    return out


def check_register(model: dict) -> list[dict]:
    out = []
    reg = model.get("register")
    if not isinstance(reg, dict):
        return out
    entries = reg.get("entries") or []
    expected = reg.get("expected_lines")
    if expected is not None and len(entries) != expected:
        out.append(finding("CG-12 REGISTER_DRIFT", "BLOCKER", None, f"{len(entries)} linhas",
                           f"O registro precisa ter {expected} linhas (transcrição literal).", "Restaurar as linhas."))
    if reg.get("printed_order_is_artifact") is not True:
        out.append(finding("CG-12 REGISTER_DRIFT", "BLOCKER", None, "printed_order_is_artifact",
                           "A ordem impressa é artefato e precisa ser declarada como tal.", "Declarar true."))
    ids = {l.get("id") for l in model["locations"]}
    for i, en in enumerate(entries):
        eid = en.get("id", f"#{i}")
        if not isinstance(en.get("display_index"), str):
            out.append(finding("CG-12 REGISTER_DRIFT", "BLOCKER", None, eid,
                               "display_index precisa ser string literal (preserva zeros e duplicatas).",
                               "Citar o índice: \"05\"."))
        loc = en.get("location_id")
        if loc is not None and loc not in ids:
            out.append(finding("CG-01 EDGE_DANGLING", "BLOCKER", None, f"{eid}.location_id={loc}",
                               "Entrada de registro aponta para lugar inexistente.", "Corrigir."))
        if loc is None and en.get("placement") not in ("NOT_ON_MAP", "NO_STANDALONE_LABEL"):
            out.append(finding("CG-12 REGISTER_DRIFT", "HIGH", None, eid,
                               "Entrada sem lugar precisa declarar placement NOT_ON_MAP ou NO_STANDALONE_LABEL.", "Declarar."))
        if en.get("placement", "ON_MAP") not in REGISTER_PLACEMENTS:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{eid}.placement", f"placement ∈ {sorted(REGISTER_PLACEMENTS)}.", "Corrigir."))
        sig = en.get("ordering_significance", "UNKNOWN")
        if sig not in ORDERING_SIGNIFICANCE:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{eid}.ordering_significance", f"∈ {sorted(ORDERING_SIGNIFICANCE)}.", "Corrigir."))
        elif sig != "UNKNOWN" and not en.get("truth_ref"):
            out.append(finding("MY-04 PATTERN_WITHOUT_LEDGER", "BLOCKER", None, eid,
                               f"ordering_significance={sig} sem truth_ref.",
                               "Significado de ordenação só sai de UNKNOWN com referência ao Story Truth Ledger."))
    return out


def check_exits(model: dict) -> list[dict]:
    out = []
    ids = {item.get("id"): (k, item) for k, item in all_id_carriers(model)}
    for ex in model["exits"]:
        xid = ex.get("id", "?")
        road = ex.get("road")
        if road and (road not in ids or ids[road][0] != "roads"):
            out.append(finding("EXIT_ROAD_UNKNOWN", "HIGH", None, f"{xid}.road={road}", "Saída aponta para via inexistente.", "Corrigir."))
        fp = ex.get("frame_portal")
        if fp:
            if fp not in ids or ids[fp][0] != "locations":
                out.append(finding("CG-01 EDGE_DANGLING", "BLOCKER", None, f"{xid}.frame_portal={fp}", "Frame portal inexistente.", "Corrigir."))
            elif "FRAME_PORTAL" not in as_list(ids[fp][1].get("type")):
                out.append(finding("CG-04 UNKNOWN_TYPE", "HIGH", None, f"{xid}.frame_portal={fp}", "Precisa ser type FRAME_PORTAL.", "Corrigir."))
        elif ex.get("frame_status") != "TO_DIGITIZE":
            out.append(finding("EXIT_FRAME_MISSING", "MEDIUM", None, xid,
                               "Saída sem frame_portal e sem `frame_status: TO_DIGITIZE`.", "Digitalizar ou marcar."))
        phys = ex.get("physical") or {}
        if phys.get("beyond_frame") != "OFF_MAP":
            out.append(finding("MY-02 TRUE_EXIT_ASSERTED", "BLOCKER", None, f"{xid}.physical.beyond_frame={phys.get('beyond_frame')!r}",
                               "O que existe além da moldura é OFF_MAP: a cartografia não o modela.",
                               "Declarar beyond_frame: OFF_MAP."))
        classes = set()
        for c in as_list(ex.get("claims")):
            cls = c.get("class")
            if cls not in EXIT_CLASSES:
                out.append(finding("EXIT_CLASS_INVALID", "BLOCKER", None, f"{xid}: {cls!r}",
                                   f"Classe de saída fora do enum fechado {sorted(EXIT_CLASSES)}.",
                                   "Não existe classe de saída verdadeira: usar o enum."))
            else:
                classes.add(cls)
            if c.get("epistemic_status", "OFFICIAL_CLAIM") not in EPISTEMIC:
                out.append(finding("INVALID_ENUM", "HIGH", None, f"{xid}.claims.epistemic_status", "Corrigir.", "Corrigir."))
        if phys.get("drawn_to") == "FRAME":
            classes.add("APPARENT_EXIT")
        declared = set(as_list(ex.get("exit_classes")))
        if declared != classes:
            out.append(finding("EXIT_CLASSES_DRIFT", "MEDIUM", None, xid,
                               f"exit_classes {sorted(declared)} ≠ projetado das claims/geometria {sorted(classes)}.",
                               "exit_classes é projeção: regenerar."))
        if "FALSE_EXIT" in classes and not ex.get("truth_ref") and phys.get("drawn_to") != "LOOP_WITHIN_FRAME":
            out.append(finding("EXIT_FALSE_WITHOUT_PROOF", "HIGH", None, xid,
                               "FALSE_EXIT exige truth_ref ou prova física (via que volta ao núcleo sem tocar a moldura).",
                               "Registrar a prova física ou o truth_ref."))
    return out


def _collect_anomaly_refs(item, acc):
    if isinstance(item, dict):
        for k, v in item.items():
            if k in ("anomalies", "requires_anomalies"):
                acc.extend(as_list(v))
            else:
                _collect_anomaly_refs(v, acc)
    elif isinstance(item, list):
        for v in item:
            _collect_anomaly_refs(v, acc)


def check_mysteries(model: dict) -> list[dict]:
    out = []
    ids = {item.get("id") for _, item in all_id_carriers(model)}
    anomalies = index_by_id(model["anomalies"] + model["glyphs"] + model["unlabeled"])
    for group, items in (("route_mysteries", model["route_mysteries"]), ("mysteries", model["mysteries"])):
        for m in items:
            mid = m.get("id", "?")
            state = m.get("resolution_state")
            if state not in RESOLUTION_STATES:
                out.append(finding("INVALID_ENUM", "HIGH", None, f"{mid}.resolution_state={state!r}",
                                   f"∈ {sorted(RESOLUTION_STATES)}.", "Corrigir."))
            if state in ("RESOLVED", "PARTIALLY_RESOLVED") and not (m.get("truth_ref") and m.get("question_ref")):
                out.append(finding("MY-04 PATTERN_WITHOUT_LEDGER", "BLOCKER", None, mid,
                                   f"resolution_state={state} sem truth_ref e question_ref.",
                                   "Só o Story Truth Ledger resolve um mistério cartográfico."))
            if m.get("question_policy") == "NEVER" and state not in ("UNRESOLVED", "PERMANENTLY_AMBIGUOUS"):
                out.append(finding("MY-03 ROUTE_MYSTERY_INTERPRETED", "BLOCKER", None, mid,
                                   f"Pergunta NEVER com resolution_state={state}.", "Pergunta NEVER nunca se resolve."))
            if group == "route_mysteries" and m.get("motto_status") != "MAP_ARTIFACT":
                out.append(finding("MY-03 ROUTE_MYSTERY_INTERPRETED", "BLOCKER", None, mid,
                                   f"motto_status={m.get('motto_status')!r}: o lema é artefato do mapa, nunca resposta.",
                                   "Declarar motto_status: MAP_ARTIFACT."))
            for cand in as_list(m.get("candidate_interpretations")):
                if isinstance(cand, dict) and any(normalize_key(k) in EVALUATION_KEYS for k in cand):
                    out.append(finding("MY-03 ROUTE_MYSTERY_INTERPRETED", "BLOCKER", None, mid,
                                       "candidate_interpretations com campo de avaliação (plausível/verdadeiro/score).",
                                       "Interpretações candidatas não têm valor de verdade."))
            for ref in as_list(m.get("involved_locations")) + as_list(m.get("involved_routes")) + as_list(m.get("physical_routes")):
                if ref not in ids:
                    out.append(finding("CG-01 EDGE_DANGLING", "BLOCKER", None, f"{mid}: {ref}",
                                       "Mistério aponta para entidade inexistente.", "Corrigir."))
            refs: list = []
            _collect_anomaly_refs(m, refs)
            for a in refs:
                if a not in anomalies:
                    out.append(finding("CG-01 EDGE_DANGLING", "BLOCKER", None, f"{mid}: {a}", "Anomalia inexistente.", "Corrigir."))
                elif anomalies[a].get("classification") not in ("INTENTIONAL_ARTIFACT",) and anomalies[a].get("kind_of") != "STRUCTURE":
                    out.append(finding("MY-06 ANOMALY_USED_AS_CLUE", "HIGH", None, f"{mid}: {a}",
                                       f"Anomalia {anomalies[a].get('classification', 'UNDECIDED')} usada como pista.",
                                       "Só anomalia INTENTIONAL_ARTIFACT alimenta mistério."))
    return out


def check_anomalies(model: dict) -> list[dict]:
    out = []
    for a in model["anomalies"]:
        aid = a.get("id", "?")
        cls = a.get("classification", "UNDECIDED")
        if cls not in ANOMALY_CLASSES:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{aid}.classification={cls!r}", f"∈ {sorted(ANOMALY_CLASSES)}.", "Corrigir."))
        if cls == "INTENTIONAL_ARTIFACT" and not a.get("decided_by"):
            out.append(finding("ANOMALY_DECISION_MISSING", "MEDIUM", None, aid,
                               "Classificação sem decided_by (aprovação da autora).", "Referenciar a decisão."))
    for g in model["glyphs"]:
        if g.get("attributed_to"):
            out.append(finding("MY-03 ROUTE_MYSTERY_INTERPRETED", "BLOCKER", None, g.get("id", "?"),
                               "Glifo ilegível com leitura atribuída.",
                               "Leituras candidatas nunca viram vínculo."))
    return out


def check_artifacts(model: dict) -> list[dict]:
    out = []
    for a in model["artifacts"]:
        aid = a.get("id", "?")
        kind = a.get("kind")
        if kind not in ARTIFACT_KINDS:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{aid}.kind={kind!r}", f"∈ {sorted(ARTIFACT_KINDS)}.", "Corrigir."))
        if a.get("epistemic_status", "UNKNOWN") not in EPISTEMIC:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{aid}.epistemic_status", f"∈ {sorted(EPISTEMIC)}.", "Corrigir."))
        if kind == "TEXT":
            if not a.get("text"):
                out.append(finding("ARTIFACT_TEXT_MISSING", "MEDIUM", None, aid, "Artefato TEXT sem text.", "Transcrever."))
            if a.get("epistemic_status") == "FACT":
                out.append(finding("TEXT_CLAIMED_AS_FACT", "HIGH", None, aid,
                                   "Texto de mapa é alegação do artefato, nunca FACT.", "Usar OFFICIAL_CLAIM/UNKNOWN."))
        if kind == "MAP" and (a.get("source_file") or str(aid).startswith("MAP-DIEGETIC")):
            author = a.get("author")
            if not (isinstance(author, dict) and author.get("status") == "MUST_REMAIN_UNKNOWN"):
                out.append(finding("MY-08 MAP_AUTHOR_REVEALED", "BLOCKER", None, f"{aid}.author={author!r}",
                                   "A autoria dos mapas é mistério permanente: author precisa ser "
                                   "{status: MUST_REMAIN_UNKNOWN, question_ref, unk_ref}, nunca um id.",
                                   "Restaurar author MUST_REMAIN_UNKNOWN."))
            if a.get("map_layer") in INSTITUTIONAL_LAYERS:
                out.append(finding("MY-08 MAP_AUTHOR_REVEALED", "BLOCKER", None, f"{aid}.map_layer={a.get('map_layer')}",
                                   "Camada institucional implicaria autor institucional.", "Usar map_layer: UNKNOWN."))
    return out


def check_boundaries(model: dict) -> list[dict]:
    out = []
    for b in model["boundaries"]:
        if b.get("kind") not in BOUNDARY_KINDS:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{b.get('id')}.kind={b.get('kind')!r}", f"∈ {sorted(BOUNDARY_KINDS)}.", "Corrigir."))
    return out


DISCOVERABILITY = {"OBVIOUS", "FINDABLE", "OBSCURE", "NEAR_IMPOSSIBLE", "UNSPECIFIED"}


def check_hideouts(model: dict) -> list[dict]:
    out = []
    ids = {l.get("id") for l in model["locations"]}
    for h in model["hideouts"]:
        hid = h.get("id", "?")
        if h.get("location") not in ids:
            out.append(finding("CG-01 EDGE_DANGLING", "BLOCKER", None, f"{hid}.location={h.get('location')}",
                               "Esconderijo em lugar inexistente.", "Corrigir."))
        for field in ("capacity", "duration_safe"):
            v = h.get(field, "UNSPECIFIED")
            if v != "UNSPECIFIED" and not (isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0):
                out.append(finding("HIDEOUT_FIELD_INVALID", "HIGH", None, f"{hid}.{field}={v!r}",
                                   f"{field} é número positivo ou UNSPECIFIED (nada de valor inventado).", "Corrigir."))
        if h.get("discoverability", "UNSPECIFIED") not in DISCOVERABILITY:
            out.append(finding("INVALID_ENUM", "HIGH", None, f"{hid}.discoverability", f"∈ {sorted(DISCOVERABILITY)}.", "Corrigir."))
        for ev in as_list(h.get("compromise_events")):
            if ev.get("effect") not in ("COMPROMISED", "DESTROYED", "WATCHED"):
                out.append(finding("INVALID_ENUM", "HIGH", None, f"{hid}.compromise_events.effect={ev.get('effect')!r}",
                                   "effect ∈ COMPROMISED | DESTROYED | WATCHED.", "Corrigir."))
    return out


def scan_answers(model: dict) -> list[dict]:
    """MY-01 / MY-02 / CX-05: varredura de todas as chaves e strings de todos os seeds."""
    out = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                nk = normalize_key(k)
                if nk in {normalize_key(x) for x in HIDDEN_ANSWER_KEYS}:
                    cat = "MY-02 TRUE_EXIT_ASSERTED" if TRUE_EXIT_RE.search(str(k)) else "MY-01 HIDDEN_ANSWER_PRESENT"
                    out.append(finding(cat, "BLOCKER", None, f"{path}.{k}",
                                       "Chave que guarda resposta: a cartografia guarda estrutura, nunca verdade narrativa.",
                                       "Remover; a verdade mora no Story Truth Ledger, referenciada por truth_ref."))
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")
        elif isinstance(node, str):
            leaf = path.rsplit(".", 1)[-1]
            if leaf in VERBATIM_KEYS:
                return
            if TRUE_EXIT_RE.search(node):
                out.append(finding("MY-02 TRUE_EXIT_ASSERTED", "BLOCKER", None, f"{path}: {node[:60]!r}",
                                   "O sistema não representa saída verdadeira.", "Remover."))
            if SUPERNATURAL_RE.search(node):
                out.append(finding("CX-05 SUPERNATURAL_ASSERTED", "BLOCKER", None, f"{path}: {node[:60]!r}",
                                   "Fenômeno sobrenatural sem decisão canônica explícita (PHYSICAL_REALISM = TRUE).",
                                   "Remover ou registrar decisão canônica."))

    for key in LIST_KEYS:
        walk(model.get(key), key)
    walk(model.get("register"), "register")
    return out


# ----------------------------------------------------------------------------
# orquestração
# ----------------------------------------------------------------------------

def validate(model: dict) -> list[dict]:
    proj = project_all(model)
    findings: list[dict] = []
    findings += check_structure(model)
    findings += check_ids(model)
    findings += check_types_and_fields(model)
    findings += check_origin(model, proj)
    findings += check_positions(model, proj)
    findings += check_sources(model)
    findings += check_edges(model, proj)
    findings += check_subterranean(model)
    findings += check_orphans(model)
    findings += check_names(model)
    findings += check_inventory(model)
    findings += check_register(model)
    findings += check_exits(model)
    findings += check_hideouts(model)
    findings += check_boundaries(model)
    findings += check_anomalies(model)
    findings += check_artifacts(model)
    findings += check_mysteries(model)
    findings += scan_answers(model)
    import cartography_graph as cg  # noqa: E402  (importação tardia: o grafo importa este módulo)
    findings += cg.check_water_crossings(model)
    findings += cg.check_mutations(model)
    import cartography_chase as chase  # noqa: E402
    findings += chase.check_sightlines(model)
    import cartography_maps as maps  # noqa: E402
    findings += maps.validate_maps(model)
    order = {s: i for i, s in enumerate(reversed(SEVERITY_ORDER))}
    return sorted(findings, key=lambda f: (order[f["severity"]], f["category"], f["evidence"]))


def summary(model: dict) -> dict:
    layers: dict[str, int] = defaultdict(int)
    unknown_pos = 0
    proj = project_all(model)
    for loc in model["locations"]:
        layers[loc.get("layer", "?")] += 1
        if proj.get(loc.get("id")) is None:
            unknown_pos += 1
    anomalies = defaultdict(int)
    for a in model["anomalies"]:
        anomalies[a.get("classification", "UNDECIDED")] += 1
    return {
        "locations_by_layer": dict(layers),
        "locations_without_position": unknown_pos,
        "edges": len(model["edges"]),
        "roads": len(model["roads"]),
        "routes": len(model["routes"]),
        "exits": len(model["exits"]),
        "route_mysteries": len(model["route_mysteries"]),
        "mysteries": len(model["mysteries"]),
        "artifacts": len(model["artifacts"]),
        "anomalies": dict(anomalies),
        "register_lines": len((model.get("register") or {}).get("entries") or []),
    }


def coords_table(model: dict) -> list[dict]:
    proj = project_all(model)
    rows = []
    for loc in model["locations"]:
        p = proj.get(loc["id"])
        rows.append({
            "id": loc["id"], "name": loc.get("canonical_name"),
            "x": None if p is None else round(p["x"]), "y": None if p is None else round(p["y"]),
            "distance_m": None if p is None else round(math.hypot(p["x"], p["y"])),
            "accuracy_m": None if p is None else p["accuracy_m"],
            "basis": None if p is None else p["basis"],
        })
    return rows


def render_report(findings: list[dict], source: str, sm: dict) -> str:
    out = [
        "# Relatório do Canon Cartográfico\n\n",
        f"Fonte: `{source}`\n\n",
        "Gerado por `engine/scripts/check_cartography.py` (Slice 1: contrato, integridade e proteção de mistério). "
        "Ver docs/sdd/*CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md.\n\n",
        "```json\n" + json.dumps(sm, ensure_ascii=False, indent=2) + "\n```\n\n",
    ]
    if not findings:
        out.append("Nenhum achado.\n")
        return "".join(out)
    counts: dict[str, int] = defaultdict(int)
    for f in findings:
        counts[f["severity"]] += 1
    out.append("| Severidade | Achados |\n|---|---:|\n")
    for sev in reversed(SEVERITY_ORDER):
        if counts.get(sev):
            out.append(f"| {sev} | {counts[sev]} |\n")
    out.append("\n")
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        by_cat[f["category"]].append(f)
    for cat, items in by_cat.items():
        out.append(f"## {cat} ({len(items)})\n\n")
        for f in items:
            out.append(f"- **{f['severity']}** — `{f['evidence']}`\n  - {f['detail']}\n  - Ação: {f['recommended_action']}\n")
        out.append("\n")
    return "".join(out)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Valida o canon cartográfico (SDD CANONICAL_CARTOGRAPHY_GRAPH).")
    ap.add_argument("--canon", type=Path, required=True, help="Diretório com CARTOGRAPHY.seed.yaml e os seeds.")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--coords", action="store_true", help="Tabela de coordenadas derivadas e sai.")
    ap.add_argument("--distance", nargs=2, metavar=("A", "B"))
    ap.add_argument("--bearing", nargs=2, metavar=("A", "B"))
    ap.add_argument("--time", nargs=2, metavar=("A", "B"), help="Tempos mínimo/esperado/razoável entre dois lugares.")
    ap.add_argument("--reachable", nargs=2, metavar=("A", "B"))
    ap.add_argument("--route", nargs=2, metavar=("A", "B"))
    ap.add_argument("--kind", choices=["shortest", "safest", "hidden"], default="shortest")
    ap.add_argument("--escape-routes", metavar="A")
    ap.add_argument("--check-staging", type=Path, metavar="STAGING.yaml",
                    help="Valida deslocamentos, visão declarada, esconderijos e perseguições de um STAGING.yaml.")
    ap.add_argument("--visible", nargs=2, metavar=("A", "B"), help="A observa B (visibilidade).")
    ap.add_argument("--target-lit", action="store_true", help="Alvo com luz própria (para --visible).")
    ap.add_argument("--recognize", action="store_true", help="Pergunta de reconhecimento: sempre fora de escopo.")
    ap.add_argument("--exits", action="store_true", help="Saídas: classes e alegações. Nunca a verdadeira (EXIT_TRUTH_NOT_IN_CARTOGRAPHY).")
    ap.add_argument("--exit-truth", action="store_true", help="Só os truth_ref (ponteiros opacos).")
    ap.add_argument("--engine-view", action="store_true", help="Com --authorized-by GT-*: confirma a pertinência do id, nunca o conteúdo.")
    ap.add_argument("--authorized-by", metavar="GT")
    ap.add_argument("--reader-map", action="store_true", help="Projeção do leitor no --chapter (baseline: mapas impressos).")
    ap.add_argument("--reader-gap", metavar="ACTOR", help="Arestas que o leitor viu e o POV desconhece (ironia dramática).")
    ap.add_argument("--belief", metavar="ARTIFACT", help="Como um artefato de mapa descreve o mundo (crença por artefato).")
    ap.add_argument("--check-prose", type=Path, metavar="FILE", help="KN-02: prosa do --chapter revela lugar antes da hora?")
    ap.add_argument("--hideouts", metavar="A", help="Esconderijos registrados acessíveis a partir de A e o veredito de vigilância.")
    ap.add_argument("--bottlenecks", action="store_true", help="Pontos de articulação e pontes do grafo permitido.")
    ap.add_argument("--layer", action="append", help="Restringe --bottlenecks a uma camada (repetível).")
    ap.add_argument("--travel-mode", choices=["WALK", "RUN", "CRAWL", "VEHICLE"], default="WALK")
    ap.add_argument("--profile", default="FIT")
    ap.add_argument("--actor")
    ap.add_argument("--chapter", type=int)
    ap.add_argument("--lighting", default="DAYLIGHT")
    ap.add_argument("--weather", default="CLEAR")
    ap.add_argument("--ledger", type=Path, help="CAUSAL_LEDGER.yaml (conhecimento por ator).")
    args = ap.parse_args()

    try:
        model = load_model(args.canon)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.coords:
        print(json.dumps(coords_table(model), ensure_ascii=False, indent=2))
        return 0
    if args.exits or args.exit_truth or args.reader_map or args.reader_gap or args.belief or args.check_prose:
        import cartography_maps as maps
        ledger = load_yaml(args.ledger) if args.ledger else None
        ch = args.chapter if args.chapter is not None else 0
        code = 0
        if args.exits:
            payload = maps.exits_query(model, args.chapter)
        elif args.exit_truth:
            payload = maps.exit_truth(model, args.engine_view, args.authorized_by, ledger)
        elif args.reader_map:
            payload = maps.reader_map(model, ch, ledger)
        elif args.reader_gap:
            payload = maps.reader_knows_pov_does_not(model, args.reader_gap, ch, ledger)
        elif args.belief:
            payload = maps.belief_view(model, args.belief) or {"found": False}
        else:
            fs = maps.check_reader_leak(model, args.check_prose.read_text(encoding="utf-8"), ch, ledger)
            payload = {"chapter": ch, "findings": fs}
            code = 1 if any(f["severity"] in BLOCKING for f in fs) else 0
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return code
    queries = (args.distance, args.bearing, args.time, args.reachable, args.route, args.escape_routes, args.check_staging,
               args.visible, args.bottlenecks, args.hideouts)
    if any(queries):
        import cartography_graph as cg
        ledger = load_yaml(args.ledger) if args.ledger else None
        ctx = {"mode": args.travel_mode, "profile": args.profile, "chapter": args.chapter,
               "lighting": args.lighting, "weather": args.weather, "ledger": ledger}
        if args.actor:
            ctx.update(view="ACTOR", actor=args.actor)
        import cartography_chase as chase
        if args.visible:
            payload = chase.visible_from(model, *args.visible, ctx={"lighting": args.lighting, "weather": args.weather,
                                                                   "target_lit": args.target_lit, "recognize": args.recognize})
        elif args.hideouts:
            payload = {"hideouts": chase.accessible_hideouts(model, args.hideouts, ctx)}
        elif args.bottlenecks:
            payload = chase.bottlenecks(model, ctx, layers=set(args.layer) if args.layer else None)
        elif args.distance:
            payload = cg.distance(model, *args.distance)
        elif args.bearing:
            payload = cg.bearing(model, *args.bearing)
        elif args.time:
            payload = cg.travel_times(model, *args.time, ctx=ctx) or {"found": False}
        elif args.reachable:
            payload = cg.reachable(model, *args.reachable, ctx=ctx)
        elif args.route:
            payload = cg.route(model, *args.route, ctx=ctx, kind=args.kind)
        elif args.escape_routes:
            payload = cg.escape_routes(model, args.escape_routes, ctx=ctx)
        else:
            res = chase.validate_scene(model, load_yaml(args.check_staging), ledger=ledger)
            print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
            return 1 if any(f["severity"] in BLOCKING for f in res["findings"]) else 0
        if ctx.get("view") != "ACTOR" and not args.check_staging:
            payload = {"ENGINE_VIEW": "não entregar a personagem nem ao leitor", **(payload if isinstance(payload, dict) else {"result": payload})}
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return 0
    findings = validate(model)
    if args.ledger:
        import cartography_maps as maps
        findings = findings + maps.check_author_protection(model, load_yaml(args.ledger))
    sm = summary(model)
    if args.json:
        print(json.dumps({"summary": sm, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        report = render_report(findings, str(args.canon), sm)
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
    sys.exit(main())
