"""Integração da cartografia com o runtime do motor (capability neutra `features.cartography`).

Slice 5 de docs/sdd/*CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md (seções 27, 29.1, 26.3, 36). Não contém nome de obra.

Layout do runtime (dono: CANON_GUARDIAN):
    canon/cartography/CARTOGRAPHY.seed.yaml + seeds + sources/   <- materializado dos seeds da obra (T018C)
    canon/cartography/STAGING.yaml                               <- cenas e movimentos (PLANNED → REALIZED)
    canon/CAUSAL_LEDGER.yaml                                     <- opcional; conhecimento por ator
    canon/snapshots/CARTOGRAPHY.WAVE_NN.yaml                     <- base do --baseline
    briefs/cartography/CHAPTER_NN_PACK.yaml                      <- Cartography Context Pack (determinístico)

Modos (validadores dos gates):
    canon  V_CARTO_CANON  integridade, física, proteção de mistério, autoria (GATE_CANON)
    wave   V_CARTO_WAVE_n canon estático + viagem/conhecimento/visão/perseguição sobre stagings REALIZED até N,
                          CN-06 (renome sem mutação) e CN-07 (mutação retroativa) contra o snapshot (GATE_WAVE_n)
    final  V_CARTO_FINAL  tudo + KN-02 sobre o manuscrito (GATE_FULL_MANUSCRIPT)

O pack AJUDA sem decidir: lista o que é possível e o que é proibido; a cena escolhe. Passagens ocultas que o POV
desconhece aparecem só como CONTAGEM; ids só com `engine_view`.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import yaml

import cartography_chase as chase
import cartography_graph as cg
import cartography_maps as maps
import check_cartography as cc

SNAPSHOT_GLOB = "CARTOGRAPHY.WAVE_*.yaml"
MYSTERY_NOTICE = "Saídas: ver --exits (classes e alegações). O que há além da moldura é OFF_MAP; a cartografia não o modela."
DEAD_END_MAX_S = 300.0
EMPTY_STAGING = 'clock: {format: "D<nnn>T<HH:MM>"}\nstaging: []\nmovements: []\nchases: []\n'


def paths(runtime) -> dict:
    rt = Path(runtime)
    return {"canon": rt / "canon" / "cartography", "staging": rt / "canon" / "cartography" / "STAGING.yaml",
            "ledger": rt / "canon" / "CAUSAL_LEDGER.yaml", "snapshots": rt / "canon" / "snapshots",
            "briefs": rt / "briefs" / "cartography", "book_seeds": rt / "book" / "cartography"}


def _load(path: Path):
    return cc.load_yaml(path) if path.is_file() else None


# ---------------------------------------------------------------------------
# materialização (T018C): seeds da obra → canon do runtime, sem sobrescrever
# ---------------------------------------------------------------------------

def materialize(runtime) -> dict:
    """Copia `book/cartography/{seeds,sources}` para `canon/cartography/` UMA vez. Se o canon já existe não toca
    em nada: depois da primeira vez o canon só muda por mutação/proposta, nunca por reposição de seed."""
    p = paths(runtime)
    src_seeds = p["book_seeds"] / "seeds"
    if not (src_seeds / cc.MANIFEST_NAME).is_file():
        return {"status": "NO_SEEDS", "detail": f"sem {src_seeds / cc.MANIFEST_NAME}"}
    if (p["canon"] / cc.MANIFEST_NAME).is_file():
        return {"status": "ALREADY_MATERIALIZED", "copied": []}
    p["canon"].mkdir(parents=True, exist_ok=True)
    copied = []
    for f in sorted(src_seeds.glob("*.yaml")):
        shutil.copy2(f, p["canon"] / f.name)
        copied.append(f.name)
    sources = p["book_seeds"] / "sources"
    if sources.is_dir():
        shutil.copytree(sources, p["canon"] / "sources", dirs_exist_ok=True)
        copied.append("sources/")
        # na obra as fontes são irmãs de seeds/ (`../sources/`); no canon do runtime moram dentro do diretório
        manifest = p["canon"] / cc.MANIFEST_NAME
        manifest.write_text(re.sub(r"(?m)^(\s*sources:\s*)\.\./sources/", lambda m: m.group(1) + "sources/", manifest.read_text(encoding="utf-8")), encoding="utf-8")
    if not p["staging"].is_file():   # o CANON_GUARDIAN/SCENE_ARCHITECT preenchem; a tarefa promete o arquivo
        p["staging"].write_text(EMPTY_STAGING, encoding="utf-8")
        copied.append("STAGING.yaml")
    return {"status": "MATERIALIZED", "copied": copied}


# ---------------------------------------------------------------------------
# snapshot (base do --baseline) e regras CN-06 / CN-07
# ---------------------------------------------------------------------------

def _realized(doc, through=None):
    def ok(x):
        return x.get("status") == "REALIZED" and (through is None or (x.get("chapter") or 0) <= through)
    stg = [s for s in cc.as_list((doc or {}).get("staging")) if ok(s)]
    ids = {s.get("id") for s in stg}
    mov = [m for m in cc.as_list((doc or {}).get("movements"))
           if m.get("status") == "REALIZED" and m.get("from_staging") in ids and m.get("to_staging") in ids]
    chs = [c for c in cc.as_list((doc or {}).get("chases")) if c.get("status", "REALIZED") == "REALIZED"
           and (through is None or (c.get("chapter") or 0) <= through)]
    return {**{k: v for k, v in (doc or {}).items() if k not in ("staging", "movements", "chases")},
            "staging": stg, "movements": mov, "chases": chs}


def _mut_chapter(m):
    return (m.get("canon_effective_from") or {}).get("chapter", m.get("chapter", 0))


def build_snapshot(model, doc=None) -> dict:
    """Congela o que a wave seguinte não pode reescrever sem mutação: nomes canônicos, tipos e mutações já aceitas."""
    frozen = max([s.get("chapter") or 0 for s in cc.as_list((doc or {}).get("staging")) if s.get("status") == "REALIZED"] or [0])
    return {"apiVersion": cc.API_VERSION, "kind": "CartographySnapshot", "through_chapter": frozen,
            "locations": {l["id"]: {"canonical_name": l.get("canonical_name"), "type": l.get("type")} for l in model["locations"] if l.get("id")},
            "edges": sorted(e["id"] for e in model["edges"] if e.get("id")),
            "mutations": sorted(m.get("id") for m in cc.as_list(model["manifest"].get("mutations")) if m.get("id"))}


def snapshot_auto(runtime) -> Path:
    p = paths(runtime)
    model = cc.load_model(p["canon"])
    p["snapshots"].mkdir(parents=True, exist_ok=True)
    nums = [int(m.group(1)) for f in p["snapshots"].glob(SNAPSHOT_GLOB) if (m := re.search(r"WAVE_(\d+)\.yaml$", f.name))]
    out = p["snapshots"] / f"CARTOGRAPHY.WAVE_{(max(nums) + 1) if nums else 0:02d}.yaml"
    out.write_text(yaml.safe_dump(build_snapshot(model, _load(p["staging"])), allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    return out


def check_baseline(model, snapshot) -> list[dict]:
    """CN-06: renome sem mutação. CN-07: mutação nova com efeito em capítulo já congelado."""
    out = []
    muts = cc.as_list(model["manifest"].get("mutations"))
    renamed = {m.get("target") for m in muts if m.get("field") in ("canonical_name", "name")}
    for l in model["locations"]:
        old = (snapshot.get("locations") or {}).get(l.get("id"))
        if old and old.get("canonical_name") != l.get("canonical_name") and l["id"] not in renamed:
            out.append(cc.finding("CN-06 RENAME_WITHOUT_PROPOSAL", "HIGH", None, l["id"],
                                  f"canonical_name mudou de {old.get('canonical_name')!r} para {l.get('canonical_name')!r} sem mutação.",
                                  "Registrar mutação aprovada (nome antigo vira alias), ou restaurar o nome."))
    known = set(snapshot.get("mutations") or [])
    frozen = snapshot.get("through_chapter") or 0
    for m in muts:
        if m.get("id") not in known and _mut_chapter(m) <= frozen:
            out.append(cc.finding("CN-07 RETROACTIVE_MUTATION", "BLOCKER", _mut_chapter(m), m.get("id", "?"),
                                  f"Mutação nova com efeito no capítulo {_mut_chapter(m)}, já congelado (até {frozen}).",
                                  "Mutação vale a partir do próximo capítulo ainda não realizado."))
    return out


# ---------------------------------------------------------------------------
# manuscrito → KN-02
# ---------------------------------------------------------------------------

def manuscript_chapters(runtime) -> dict[int, str]:
    rt = Path(runtime) / "manuscript"
    found = {}
    for sub in ("revised", "approved"):        # a versão mais avançada vence
        for f in sorted((rt / sub).glob("chapter_*.md")) if (rt / sub).is_dir() else []:
            if (m := re.search(r"chapter_(\d+)\.md$", f.name)):
                found[int(m.group(1))] = f.read_text(encoding="utf-8")
    return found


# ---------------------------------------------------------------------------
# modos dos validadores
# ---------------------------------------------------------------------------

def run_mode(runtime, mode, through_chapter=None, baseline=None) -> list[dict]:
    p = paths(runtime)
    if not (p["canon"] / cc.MANIFEST_NAME).is_file():
        return [cc.finding("CARTOGRAPHY_CANON_MISSING", "BLOCKER", None, str(p["canon"]),
                           "features.cartography ligada, mas canon/cartography/ não foi materializado (T018C).",
                           "Rodar T018C_CARTOGRAPHY (materialize) ou entregar os seeds em book/cartography/seeds.")]
    model = cc.load_model(p["canon"])
    ledger = _load(p["ledger"])
    findings = cc.validate(model)
    if ledger:
        findings += maps.check_author_protection(model, ledger)
    if mode == "canon":
        return findings
    doc = _realized(_load(p["staging"]), through_chapter if mode == "wave" else None)
    if doc["staging"] or doc["chases"]:
        res = chase.validate_scene(model, doc, ledger=ledger)
        findings += res["findings"]
    if baseline:
        snap = _load(Path(baseline) if Path(baseline).is_absolute() else Path(runtime) / baseline)
        if snap:
            findings += check_baseline(model, snap)
        else:
            findings.append(cc.finding("BASELINE_MISSING", "MEDIUM", None, str(baseline), "Snapshot da wave anterior ausente.",
                                       "Gerar com --snapshot-auto no fim da wave anterior."))
    if mode == "final":
        chapters = manuscript_chapters(runtime)
        if not chapters:
            findings.append(cc.finding("MANUSCRIPT_NOT_FOUND", "INFO", None, str(Path(runtime) / "manuscript"),
                                       "Sem capítulos para KN-02.", "Rodar depois de existirem capítulos revisados."))
        for n, text in sorted(chapters.items()):
            if through_chapter is None or n <= through_chapter:
                findings += maps.check_reader_leak(model, text, n, ledger)
    order = {s: i for i, s in enumerate(reversed(cc.SEVERITY_ORDER))}
    return sorted(findings, key=lambda f: (order[f["severity"]], f["category"], f["evidence"]))


# ---------------------------------------------------------------------------
# Cartography Context Pack (SDD 27.1)
# ---------------------------------------------------------------------------

def _range(a, b):
    if not a or not b:
        return None
    d = cc.euclid(a, b)
    slack = a.get("accuracy_m", 0) + b.get("accuracy_m", 0)
    return [round(max(0.0, d - slack)), round(d + slack)]


def _min(s):
    return round(s / 60.0, 1)


def build_pack(model, doc, chapter, scene=None, ledger=None, engine_view=False) -> dict:
    """Um pack por capítulo, com uma entrada por staging do POV na(s) cena(s)."""
    g = cg.Graph(model)
    locs = cc.index_by_id(model["locations"])
    reader = maps.reader_map(model, chapter, ledger)["states"]
    printed_edges = maps.printed_ids(model)["edges"]
    entries = []
    stagings = [s for s in cc.as_list((doc or {}).get("staging")) if s.get("chapter") == chapter and (scene is None or s.get("scene") == scene)]
    for s in stagings:
        actor, cur = s.get("actor"), s.get("location")
        loc = locs.get(cur)
        if loc is None:
            entries.append({"staging": s.get("id"), "error": f"lugar inexistente: {cur}"})
            continue
        cond = s.get("conditions") or next((m.get("conditions") for m in cc.as_list((doc or {}).get("movements")) if m.get("to_staging") == s.get("id")), None) or {}
        ctx = cg._ctx(model, cg.make_ctx(chapter=chapter, view="ACTOR", actor=actor, ledger=ledger, lighting=cond.get("lighting", "DAYLIGHT"),
                                         weather=cond.get("weather", "CLEAR"), familiar=cond.get("familiar", True)))
        know = ctx["knowledge"]
        adjacent, visible, hidden_known, hidden_unknown, adjacent_ids = [], [], [], 0, []
        for nb, e in g.adj.get(cur, []):
            state = cg.edge_state(model, e, chapter)
            public = e.get("secret_level") in cg.PUBLIC_SECRET_LEVELS
            if not public:
                if know.knows_edge(e):
                    hidden_known.append({"edge": e["id"], "to": nb, "state": state})
                else:
                    hidden_unknown += 1
                continue
            times = g.path_times({"edges": [(cur, nb, e)], "nodes": [cur, nb], "cost": 0}, ctx)
            adjacent.append({"id": nb, "name": locs[nb].get("canonical_name"), "via": e["id"], "state": state,
                             "walk_expected": f"{_min(times['min_s'])}–{_min(times['max_reasonable_s'])} min",
                             "visible_exit": True})
            visible.append(e["id"])
            adjacent_ids.append(nb)
        proj = cc.project_all(model)
        dead = []
        for n, l in locs.items():
            if n == cur or len(g.adj.get(n, [])) != 1 or l.get("layer") == "SUBTERRANEAN" or "FRAME_PORTAL" in cc.as_list(l.get("type")):
                continue
            if any(h["location"] == n for h in model["hideouts"]):
                continue
            t = cg.travel_times(model, cur, n, ctx=ctx)
            if t and t["expected_s"] <= DEAD_END_MAX_S:
                dead.append({"id": n, "expected_min": _min(t["expected_s"])})
        here = {e["id"] for e in model["edges"] if cur in (e.get("from"), e.get("to"))}
        gap = [r["edge"] for r in maps.reader_knows_pov_does_not(model, actor, chapter, ledger)["reader_knows_but_pov_does_not"] if r["edge"] in here]
        light = ctx["lighting"]
        weather = ctx["weather"]
        det = chase.detection_limit(model, light)
        entry = {
            "staging": s.get("id"), "scene": s.get("scene"), "pov": actor, "chapter": chapter, "at": s.get("at"),
            "conditions": {"lighting": light, "weather": weather},
            "current_location": {"id": cur, "name": loc.get("canonical_name"), "type": loc.get("type"), "status": loc.get("status", "UNKNOWN")},
            "adjacent_locations": adjacent, "visible_exits": visible,
            "hidden_exits_known_by_pov": hidden_known,
            "hidden_exits_unknown_to_pov": hidden_unknown,
            "approximate_distances": [{"to": n, "euclid_m": r} for n in adjacent_ids if (r := _range(proj.get(cur), proj.get(n)))],
            "dead_ends": dead,
            "cover": {"at_location": loc.get("cover", "UNSPECIFIED")},
            "surveillance": {"at_location": loc.get("surveillance", "UNKNOWN")},
            "underground_access": {"known_to_pov": [h["edge"] for h in hidden_known], "state": "UNKNOWN" if hidden_known else "NONE_KNOWN"},
            "weather_effects": [f"{weather} ×{cg.WEATHER_FACTOR.get(weather, 1.0):.2f} em deslocamento", f"{light}: detecção de figura ≤ {round(det)} m"],
            "canon_constraints": _constraints(model),
            "forbidden": [{"code": "KN-01", "detail": "usar passagem oculta que o POV não conhece"},
                          {"code": "KN-02", "detail": "nomear lugar com first_allowed_reveal posterior a este capítulo e fora dos mapas impressos"},
                          {"code": "VS-01", "detail": "afirmar que o POV vê além do limiar de detecção ou sem sightline declarada"}],
            "reader_state": {i: reader.get(i, "UNSEEN") for i in [cur] + adjacent_ids},
            "reader_knows_but_pov_does_not": gap,
            "engine_notes": None,
            "mystery_notice": MYSTERY_NOTICE,
        }
        if engine_view:
            entry["engine_notes"] = {"hidden_exits_unknown_to_pov": [e["id"] for _, e in g.adj.get(cur, [])
                                                                     if e.get("secret_level") not in cg.PUBLIC_SECRET_LEVELS and not know.knows_edge(e)]}
        entries.append(entry)
    chases = [{"id": c.get("id"), "target": (c.get("target") or {}).get("actor"), "pursuer": (c.get("pursuer") or {}).get("actor")}
              for c in cc.as_list((doc or {}).get("chases")) if c.get("chapter") == chapter and (scene is None or c.get("scene") == scene)]
    return {"chapter": chapter, "scene_filter": scene, "scenes": entries, "pursuit_routes": chases,
            "printed_edges_in_reader_baseline": len(printed_edges)}


def _constraints(model) -> list[str]:
    out = []
    locs = cc.index_by_id(model["locations"])
    rivers = {}
    for l in model["locations"]:
        for w in cc.as_list(l.get("crosses")):
            rivers.setdefault(w, []).append(l.get("canonical_name"))
    for w, bridges in sorted(rivers.items()):
        out.append(f"Nenhuma travessia de {locs.get(w, {}).get('canonical_name', w)} fora de: {', '.join(sorted(bridges))}.")
    if len(model["hideouts"]) == 1:
        out.append(f"{locs.get(model['hideouts'][0]['location'], {}).get('canonical_name', '?')} é o único esconderijo registrado.")
    out.append("O POV só usa passagens que conhece (knowledge_delta ou baseline).")
    return out


def write_pack(runtime, chapter, scene=None, engine_view=False) -> Path:
    p = paths(runtime)
    model = cc.load_model(p["canon"])
    pack = build_pack(model, _load(p["staging"]), chapter, scene, _load(p["ledger"]), engine_view)
    p["briefs"].mkdir(parents=True, exist_ok=True)
    out = p["briefs"] / f"CHAPTER_{chapter:02d}_PACK.yaml"
    out.write_text(yaml.safe_dump(pack, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    return out
