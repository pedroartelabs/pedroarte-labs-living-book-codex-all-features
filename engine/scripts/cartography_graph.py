"""Grafo, viagem, conhecimento e validação de deslocamento (capability neutra `features.cartography`).

Slice 2 de docs/sdd/*CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md (seções 7.5, 13, 17, 23, 26, 29.3).
Não contém nome de nenhuma obra. Consome o modelo carregado por `check_cartography.load_model`.

Princípios:
  * comprimento de via = polilinha em pixels da fonte × metros/pixel da fonte (nunca digitado);
  * FAIL só com o MÍNIMO físico (nunca com estimativa);
  * o ator só usa aresta secreta que conhece; o motor (view ENGINE) vê tudo, marcado;
  * o estado de uma aresta é o `fold` das mutações aprovadas (nunca edição no lugar);
  * "saída verdadeira" não existe aqui: o grafo termina na moldura.

Sem dependências novas: biblioteca padrão.
"""
from __future__ import annotations

import heapq
import math
import re
from collections import defaultdict

import check_cartography as cc

# ---------------------------------------------------------------------------
# parâmetros aprovados (SDD 16.3, 17.2, 17.3; decisão OQ-CART-14). O manifesto pode sobrescrever.
# ---------------------------------------------------------------------------

PHYS_WALK = [(5000, 2.2), (10000, 2.1), (math.inf, 2.0)]
PHYS_RUN = [(400, 9.0), (1500, 7.3), (5000, 6.6), (10000, 6.3), (math.inf, 6.0)]
PHYS_CRAWL = [(1500, 0.5), (math.inf, 0.4)]
PHYS_VEHICLE = {"MAIN": 25.0, "SECONDARY": 17.0, "TRACK": 8.0, "TRAIL": 8.0}
VEHICLE_EXPECTED = {"MAIN": 12.0, "SECONDARY": 8.0, "TRACK": 4.0, "TRAIL": 4.0}

PROFILES = {
    "UNTRAINED": {"WALK": 1.25, "RUN_S": 2.6, "RUN_MAX": 3.4, "CRAWL": 0.25, "STOOP": 0.6},
    "FIT": {"WALK": 1.35, "RUN_S": 3.2, "RUN_MAX": 4.2, "CRAWL": 0.30, "STOOP": 0.7},
    "ATHLETIC": {"WALK": 1.45, "RUN_S": 3.8, "RUN_MAX": 5.2, "CRAWL": 0.35, "STOOP": 0.8},
    "IMPAIRED": {"WALK": 0.8, "RUN_S": 1.5, "RUN_MAX": 1.5, "CRAWL": 0.15, "STOOP": 0.4},
    "ELDERLY": {"WALK": 1.0, "RUN_S": 1.8, "RUN_MAX": 2.5, "CRAWL": 0.15, "STOOP": 0.5},
}
WALK_BRISK_MPS = 1.8   # limiar do aviso TR-02 (caminhada muito rápida ≈ 1,33 × perfil FIT); parâmetro derivado
TERRAIN_FACTOR = {"ROAD_SURFACE": 1.0, "TRACK": 1.10, "FIELD": 1.25, "FOREST_FLOOR": 1.35, "MARSH": 2.5}
INEVITABLE_TERRAIN = {"MARSH", "FOREST_FLOOR"}
LIGHTING_FACTOR = {"DAYLIGHT": 1.0, "OVERCAST": 1.0, "TWILIGHT": 1.0, "NIGHT_MOON": 1.15, "NIGHT_LIGHT": 1.10}
NIGHT_DARK = {"familiar": 1.30, "unfamiliar": 1.60}
WEATHER_FACTOR = {"CLEAR": 1.0, "RAIN": 1.10, "SNOW": 1.50, "FOG": 1.20}
INJURY_FACTOR = {"NONE": 1.0, "MINOR": 1.30, "MAJOR": 2.20}
CARRY_FACTOR = {"NONE": 1.0, "PERSON": 2.0}
UNFAMILIAR_ROUTE = 1.20
PORTAL_DELAY_S = {"min": 60.0, "expected": 120.0}
REASONABLE_MULTIPLIER = 1.75

BLOCKING_STATES = {"BLOCKED", "COLLAPSED", "FLOODED", "SEALED", "DESTROYED"}
PUBLIC_SECRET_LEVELS = {None, "NONE"}
CLOCK_RE = re.compile(r"^D(\d+)T(\d{2}):(\d{2})$")


def band(table, dist):
    for limit, v in table:
        if dist <= limit:
            return v
    return table[-1][1]


def parse_clock(text) -> float:
    """'D014T23:14' -> minutos absolutos desde o dia 0."""
    m = CLOCK_RE.match(str(text))
    if not m:
        raise ValueError(f"relógio inválido: {text!r} (esperado DnnnTHH:MM)")
    return int(m.group(1)) * 1440 + int(m.group(2)) * 60 + int(m.group(3))


def fmt_clock(minutes: float) -> str:
    m = int(round(minutes))
    d, r = divmod(m, 1440)
    return f"D{d:03d}T{r // 60:02d}:{r % 60:02d}"


# ---------------------------------------------------------------------------
# geometria das arestas
# ---------------------------------------------------------------------------

def polyline_rcg(model, edge):
    """Polilinha da aresta em metros RCG, ou None."""
    spec = edge.get("source_polyline_px")
    if not isinstance(spec, dict):
        return None
    scales = cc.source_scales(model)
    pts = [cc.project_px(scales, spec.get("source"), p) for p in spec.get("points") or []]
    return pts if pts and all(pts) else None


def polyline_length(pts) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def _segments_intersect(p1, p2, p3, p4):
    d1 = (p2[0] - p1[0], p2[1] - p1[1])
    d2 = (p4[0] - p3[0], p4[1] - p3[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-12:
        return None
    t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / den
    u = ((p3[0] - p1[0]) * d1[1] - (p3[1] - p1[1]) * d1[0]) / den
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (p1[0] + t * d1[0], p1[1] + t * d1[1])
    return None


def polyline_intersections(a, b):
    out = []
    for p1, p2 in zip(a, a[1:]):
        for p3, p4 in zip(b, b[1:]):
            x = _segments_intersect(p1, p2, p3, p4)
            if x is not None:
                out.append(x)
    return out


CROSSING_TYPES = {"BRIDGE", "CULVERT", "TUNNEL", "FORD"}


def check_water_crossings(model) -> list[dict]:
    """CX-01: aresta cuja polilinha cruza um curso d'água precisa de estrutura de travessia próxima."""
    out = []
    locs = cc.index_by_id(model["locations"])
    proj = cc.project_all(model)
    water = {}
    scales = cc.source_scales(model)
    for l in model["locations"]:
        if l.get("geometry") == "LINE" and set(cc.as_list(l.get("type"))) & {"BURN", "RIVER"}:
            pts = [cc.project_px(scales, p.get("source"), p.get("px")) for p in cc.as_list(l.get("polyline_px")) if isinstance(p, dict)]
            pts = [p for p in pts if p]
            if len(pts) >= 2:
                water[l["id"]] = pts
    if not water:
        return out
    for e in model["edges"]:
        if e.get("edge_type") in ("PORTAL", "FRAME_LINK") or locs.get(e.get("from"), {}).get("layer") == "SUBTERRANEAN":
            continue
        poly = polyline_rcg(model, e)
        if not poly:
            continue
        declared = {c.get("water"): c.get("via") for c in cc.as_list(e.get("crossings")) if isinstance(c, dict)}
        for wid, wpts in water.items():
            for x in polyline_intersections(poly, wpts):
                ok = False
                candidates = [e.get("from"), e.get("to"), declared.get(wid)]
                for cid in candidates:
                    cl = locs.get(cid)
                    if not cl or not (set(cc.as_list(cl.get("type"))) & CROSSING_TYPES):
                        continue
                    cp = proj.get(cid)
                    if cp and math.hypot(cp["x"] - x[0], cp["y"] - x[1]) <= max(150.0, cp["accuracy_m"] * 2):
                        ok = True
                if not ok:
                    out.append(cc.finding("CX-01 WATER_CROSSING_WITHOUT_STRUCTURE", "BLOCKER", None,
                                          f"{e.get('id')} × {wid} em ({round(x[0])}, {round(x[1])})",
                                          "A via cruza um curso d'água sem ponte, vau, bueiro ou túnel próximo.",
                                          "Declarar a travessia (proposta) ou corrigir o traçado."))
    return out


# ---------------------------------------------------------------------------
# estado por capítulo (fold das mutações) e conhecimento
# ---------------------------------------------------------------------------

def edge_state(model, edge, chapter, mutations=None):
    """Estado físico da aresta no capítulo: último `state_timeline` + mutações aprovadas com efeito ≤ capítulo."""
    ch = chapter if chapter is not None else 10 ** 9
    state = "OPEN"
    for step in sorted(cc.as_list(edge.get("state_timeline")), key=lambda s: s.get("from_chapter", 0)):
        if step.get("from_chapter", 0) <= ch:
            state = step.get("state", state)
    muts = cc.as_list(model["manifest"].get("mutations")) if mutations is None else mutations
    for m in sorted(muts, key=lambda x: (x.get("chapter", 0))):
        if m.get("chapter", 0) > ch:
            continue
        for ef in cc.as_list(m.get("effects")):
            if ef.get("edge") == edge.get("id"):
                state = ef.get("new_state", state)
        if m.get("target") == edge.get("id") and m.get("field") == "state":
            state = m.get("new_state", state)
    return state


def check_mutations(model) -> list[dict]:
    """CN-02 (sem proposta ou previous_state incoerente), CN-03 (sem causa)."""
    out = []
    edges = cc.index_by_id(model["edges"])
    applied = []
    for m in sorted(cc.as_list(model["manifest"].get("mutations")), key=lambda x: x.get("chapter", 0)):
        mid = m.get("id", "?")
        chapter = (m.get("canon_effective_from") or {}).get("chapter", m.get("chapter", 0))
        if not m.get("proposal_ref"):
            out.append(cc.finding("CN-02 MUTATION_WITHOUT_PROPOSAL", "BLOCKER", chapter, mid,
                                  "Mudança física sem CANON_PROPOSAL aprovada.", "Registrar a proposta."))
        if not m.get("cause"):
            out.append(cc.finding("CN-03 MUTATION_WITHOUT_CAUSE", "HIGH", chapter, mid,
                                  "Mudança física sem evento causador no ledger.", "Apontar o evento (uma ponte não desaba sozinha)."))
        for ef in cc.as_list(m.get("effects")):
            e = edges.get(ef.get("edge"))
            if e is None:
                out.append(cc.finding("CG-01 EDGE_DANGLING", "BLOCKER", chapter, f"{mid}: {ef.get('edge')}",
                                      "Efeito de mutação em aresta inexistente.", "Corrigir."))
                continue
            prev = edge_state(model, e, chapter, mutations=applied)
            if ef.get("previous_state") is not None and ef["previous_state"] != prev:
                out.append(cc.finding("CN-02 MUTATION_WITHOUT_PROPOSAL", "HIGH", chapter, f"{mid}: {ef.get('edge')}",
                                      f"previous_state={ef['previous_state']} ≠ estado projetado {prev}.",
                                      "previous_state precisa ser o estado projetado no ponto de efeito."))
        applied.append(m)
    return out


class Knowledge:
    """Conhecimento de arestas/lugares por ator (baseline + ledger). view ENGINE ignora."""

    def __init__(self, model, actor=None, chapter=None, ledger=None, extra_edges=None):
        self.actor = actor
        self.known = set(extra_edges or [])
        base = model.get("baseline") or []
        for b in base:
            k = b.get("knower")
            if k in ("PUBLIC", actor):
                knows = b.get("knows") or {}
                for lvl in ("ROUTE", "FAMILIAR", "ACCESS", "EXISTS"):
                    v = knows.get(lvl)
                    if isinstance(v, list):
                        self.known.update(v)
        if ledger and actor:
            try:  # REUSE: conhecimento por conhecedor do ledger causal
                import check_causal_ledger as cl
                for item in cl.knowledge_state(ledger, actor, chapter):
                    self.known.add(item.split(":")[-1] if item.startswith("CART:") else item)
            except Exception:  # noqa: BLE001
                pass

    def knows_edge(self, edge):
        return edge.get("secret_level") in PUBLIC_SECRET_LEVELS or edge.get("id") in self.known


# ---------------------------------------------------------------------------
# contexto e grafo
# ---------------------------------------------------------------------------

def make_ctx(**kw):
    ctx = {"mode": "WALK", "profile": "FIT", "lighting": "DAYLIGHT", "weather": "CLEAR", "injury": "NONE",
           "carrying": "NONE", "familiar": True, "chapter": None, "view": "ENGINE", "actor": None,
           "knowledge": None, "access_actions": [], "has": set(), "vehicle": False}
    ctx.update(kw)
    return ctx


class Graph:
    def __init__(self, model):
        self.model = model
        self.locs = cc.index_by_id(model["locations"])
        self.proj = cc.project_all(model)
        self.scales = cc.source_scales(model)
        self.edges = model["edges"]
        self.adj = defaultdict(list)
        for e in self.edges:
            a, b, d = e.get("from"), e.get("to"), e.get("directionality", "BOTH")
            if a in self.locs and b in self.locs:
                if d in ("BOTH", "A_TO_B"):
                    self.adj[a].append((b, e))
                if d in ("BOTH", "B_TO_A"):
                    self.adj[b].append((a, e))

    def pos(self, lid):
        return self.proj.get(lid)

    # ---- comprimentos -------------------------------------------------
    def edge_lengths(self, e):
        """(nominal, mínimo, unspecified?) em metros."""
        if e.get("edge_type") == "PORTAL":
            return 0.0, 0.0, False
        dm = e.get("distance_meters") or {}
        poly = polyline_rcg(self.model, e)
        pa, pb = self.pos(e.get("from")), self.pos(e.get("to"))
        acc = (pa["accuracy_m"] if pa else 0) + (pb["accuracy_m"] if pb else 0)
        eu = cc.euclid(pa, pb) if (pa and pb) else None
        if poly:
            nominal = polyline_length(poly)
            floor = max(0.0, eu - acc) if eu is not None else 0.0
            # mínimo = 90 % do traçado (erro de digitalização), nunca abaixo da linha reta menos as precisões
            return nominal, min(nominal, max(floor, 0.9 * nominal)), False
        if dm.get("nominal") is not None:
            nominal = float(dm["nominal"])
            return nominal, float(dm.get("min", nominal)), False
        if eu is not None and e.get("edge_type") not in ("SECRET_PASSAGE", "TUNNEL", "DRAIN"):
            return eu * 1.2, max(0.0, eu - acc), False
        return None, None, True

    # ---- filtros -------------------------------------------------------
    def usable(self, e, ctx):
        """(ok, motivo, aviso)"""
        st = edge_state(self.model, e, ctx["chapter"])
        if st in BLOCKING_STATES:
            return False, f"BLOCKED:{st}", None
        if st == "RESTRICTED" and not ctx["access_actions"]:
            return False, "CLOSED_WITHOUT_ACTION", None
        if ctx["view"] == "ACTOR":
            kn = ctx["knowledge"]
            if kn is not None and not kn.knows_edge(e):
                return False, "SECRET_UNKNOWN_TO_ACTOR", None
        req = e.get("access_requirement")
        if req and req not in ctx["has"]:
            return False, f"REQUIRES:{req}", None
        if ctx["mode"] == "VEHICLE":
            if not ctx["vehicle"] or e.get("vehicle_access") in ("NO", False) or e.get("road_class") not in PHYS_VEHICLE:
                return False, "NO_VEHICLE_ACCESS", None
        warn = "STATE_UNKNOWN" if st == "UNKNOWN" else None
        return True, None, warn

    # ---- velocidade ----------------------------------------------------
    def edge_expected_speed(self, e, ctx):
        prof = PROFILES[ctx["profile"]]
        terrain = e.get("terrain")
        if terrain == "CRAWLSPACE":
            return prof["CRAWL"]
        if terrain in ("DRAIN_CHANNEL",) or (e.get("edge_type") in ("SECRET_PASSAGE", "TUNNEL", "DRAIN")
                                            and (e.get("max_passage") in (None, "UNSPECIFIED", "ADULT_STOOPED"))):
            return prof["STOOP"]
        m = ctx["mode"]
        if m == "RUN":
            return prof["RUN_S"]
        if m == "CRAWL":
            return prof["CRAWL"]
        if m == "VEHICLE":
            return VEHICLE_EXPECTED.get(e.get("road_class"), 4.0)
        return prof["WALK"]

    def global_factor(self, ctx):
        f = 1.0
        light = ctx["lighting"]
        f *= NIGHT_DARK["familiar" if ctx["familiar"] else "unfamiliar"] if light == "NIGHT_DARK" else LIGHTING_FACTOR.get(light, 1.0)
        f *= WEATHER_FACTOR.get(ctx["weather"], 1.0) * INJURY_FACTOR.get(ctx["injury"], 1.0) * CARRY_FACTOR.get(ctx["carrying"], 1.0)
        return f

    def edge_expected_time(self, e, ctx, length=None):
        if length is None:
            nom, _, unspec = self.edge_lengths(e)
            length = nom if nom is not None else 0.0
        v = self.edge_expected_speed(e, ctx)
        t = length * TERRAIN_FACTOR.get(e.get("terrain"), 1.0) / v
        if e.get("edge_type") == "PORTAL":
            t = PORTAL_DELAY_S["expected"]
        return t * (1.0 if e.get("edge_type") == "PORTAL" else self.global_factor(ctx))

    # ---- rotas ----------------------------------------------------------
    def weight(self, e, ctx, kind):
        nom, _, unspec = self.edge_lengths(e)
        if nom is None:
            pa, pb = self.pos(e.get("from")), self.pos(e.get("to"))
            nom = cc.euclid(pa, pb) if (pa and pb) else 50.0
        t = self.edge_expected_time(e, ctx, nom)
        if kind == "safest":
            risk = {"LOW": 0.0, "MEDIUM": 0.5, "HIGH": 1.0, "LETHAL": 2.0}.get(e.get("risk"), 0.5)
            expo = {"NONE": 0.0, "LOW": 0.25, "MEDIUM": 0.6, "HIGH": 1.0}.get(e.get("cover_exposure"), 0.5)
            return t * (1 + risk) * (1 + expo)
        if kind == "hidden":
            f = {"OPEN": 3.0, "PARTIAL": 1.0, "HIDDEN": 0.2, "UNDERGROUND": 0.2}.get(e.get("visibility", "OPEN"), 3.0)
            return t * (1 + f)
        return t

    def shortest_path(self, a, b, ctx, kind="shortest"):
        """Dijkstra. Retorna {edges:[(from,to,edge)], nodes:[...], cost} ou None."""
        if a not in self.locs or b not in self.locs:
            return None
        dist = {a: 0.0}
        prev = {}
        heap = [(0.0, a)]
        while heap:
            d, n = heapq.heappop(heap)
            if n == b:
                break
            if d > dist.get(n, math.inf):
                continue
            for m, e in self.adj.get(n, []):
                ok, _, _ = self.usable(e, ctx)
                if not ok:
                    continue
                nd = d + self.weight(e, ctx, kind)
                if nd < dist.get(m, math.inf):
                    dist[m] = nd
                    prev[m] = (n, e)
                    heapq.heappush(heap, (nd, m))
        if b not in dist:
            return None
        seq, n = [], b
        while n != a:
            p, e = prev[n]
            seq.append((p, n, e))
            n = p
        seq.reverse()
        return {"edges": seq, "nodes": [a] + [s[1] for s in seq], "cost": dist[b]}

    # ---- tempos ----------------------------------------------------------
    def resolve_lengths(self, path):
        """Comprimentos nominal/mínimo por aresta do caminho. Trechos de comprimento não especificado
        (passagens subterrâneas) recebem a distância entre as âncoras conhecidas mais próximas (SDD 11.4)."""
        seq = path["edges"]
        nodes = path["nodes"]
        n = len(seq)
        lnom, lmin, flag = [], [], []
        for _, _, e in seq:
            nom, mn, unspec = self.edge_lengths(e)
            lnom.append(nom)
            lmin.append(mn)
            flag.append(unspec)
        warnings = []
        i = 0
        while i < n:
            if not flag[i]:
                i += 1
                continue
            j = i
            while j + 1 < n and flag[j + 1]:
                j += 1
            k1 = i
            while k1 > 0 and not self.pos(nodes[k1]):
                k1 -= 1
            k2 = j + 1
            while k2 < len(nodes) - 1 and not self.pos(nodes[k2]):
                k2 += 1
            p1, p2 = self.pos(nodes[k1]), self.pos(nodes[k2])
            if p1 and p2:
                eu = cc.euclid(p1, p2)
                run_nom, run_min = eu, max(0.0, eu - p1["accuracy_m"] - p2["accuracy_m"])
            else:
                run_nom = run_min = 0.0
                warnings.append("SUBTERRANEAN_LENGTH_UNKNOWN")
            for t in range(i, j + 1):
                lnom[t] = run_nom if t == i else 0.0
                lmin[t] = run_min if t == i else 0.0
            warnings.append("SUBTERRANEAN_DIMENSIONS_UNSPECIFIED")
            i = j + 1
        return lnom, lmin, warnings

    def path_times(self, path, ctx):
        seq = path["edges"]
        lnom, lmin, warnings = self.resolve_lengths(path)
        total_nom = sum(x or 0.0 for x in lnom)
        total_min = sum(x or 0.0 for x in lmin)
        mode = ctx["mode"]
        prof = PROFILES[ctx["profile"]]
        # mínimo físico: comprimento mínimo ÷ velocidade absoluta da banda × terreno inevitável; portal = atraso mínimo
        if mode == "VEHICLE":
            vmax = max((PHYS_VEHICLE.get(e.get("road_class"), 8.0) for _, _, e in seq if e.get("edge_type") != "PORTAL"), default=8.0)
        elif mode == "RUN":
            vmax = band(PHYS_RUN, total_min)
        elif mode == "CRAWL":
            vmax = band(PHYS_CRAWL, total_min)
        else:
            vmax = band(PHYS_WALK, total_min)
        t_min = 0.0
        t_exp = 0.0
        t_profile_max = 0.0
        portals = 0
        gf = self.global_factor(ctx)
        for idx, (_, _, e) in enumerate(seq):
            if e.get("edge_type") == "PORTAL":
                portals += 1
                t_min += PORTAL_DELAY_S["min"]
                t_exp += PORTAL_DELAY_S["expected"]
                t_profile_max += PORTAL_DELAY_S["min"]
                continue
            lm, ln = lmin[idx] or 0.0, lnom[idx] or 0.0
            terrain = e.get("terrain")
            crawl = terrain == "CRAWLSPACE"
            v_abs = band(PHYS_CRAWL, total_min) if crawl else vmax
            inev = TERRAIN_FACTOR.get(terrain, 1.0) if terrain in INEVITABLE_TERRAIN else 1.0
            t_min += lm * inev / v_abs
            t_exp += self.edge_expected_time(e, ctx, ln) if ln else 0.0
            vprof = prof["CRAWL"] if crawl else (prof["RUN_MAX"] if mode == "RUN" else prof["WALK"])
            t_profile_max += lm * inev / vprof
        return {
            "min_s": t_min, "expected_s": t_exp, "max_reasonable_s": t_exp * REASONABLE_MULTIPLIER + portals * PORTAL_DELAY_S["expected"],
            "profile_max_effort_s": t_profile_max, "length_min_m": total_min, "length_nominal_m": total_nom,
            "portals": portals, "global_factor": gf, "warnings": sorted(set(warnings)),
        }

    def walk_brisk_s(self, path_times):
        return path_times["length_nominal_m"] / WALK_BRISK_MPS if path_times["length_nominal_m"] else 0.0


# ---------------------------------------------------------------------------
# API pública (missão §3)
# ---------------------------------------------------------------------------

def distance(model, a, b):
    g = Graph(model)
    pa, pb = g.pos(a), g.pos(b)
    if not pa or not pb:
        return {"euclid_m": None, "basis": "POSITION_UNKNOWN"}
    d = cc.euclid(pa, pb)
    acc = pa["accuracy_m"] + pb["accuracy_m"]
    return {"euclid_m": [round(max(0.0, d - acc)), round(d), round(d + acc)], "basis": f"{pa['basis']}/{pb['basis']}"}


def bearing(model, a, b):
    g = Graph(model)
    pa, pb = g.pos(a), g.pos(b)
    if not pa or not pb:
        return None
    deg = (math.degrees(math.atan2(pb["x"] - pa["x"], pb["y"] - pa["y"])) + 360) % 360
    names = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return {"degrees": round(deg), "compass16": names[int((deg + 11.25) // 22.5) % 16]}


def _ctx(model, ctx):
    ctx = dict(ctx)
    if ctx.get("view") == "ACTOR" and ctx.get("knowledge") is None:
        ctx["knowledge"] = Knowledge(model, ctx.get("actor"), ctx.get("chapter"), ctx.pop("ledger", None))
    return ctx


def route(model, a, b, ctx=None, kind="shortest"):
    ctx = _ctx(model, make_ctx(**(ctx or {})))
    g = Graph(model)
    p = g.shortest_path(a, b, ctx, kind)
    if p is None:
        return {"found": False, "view": ctx["view"]}
    t = g.path_times(p, ctx)
    return {"found": True, "view": ctx["view"], "nodes": p["nodes"], "edges": [e["id"] for _, _, e in p["edges"]], "times": t}


def travel_times(model, a, b, ctx=None):
    r = route(model, a, b, ctx)
    return r.get("times") if r["found"] else None


def reachable(model, a, b, ctx=None):
    ctx = make_ctx(**(ctx or {}))
    r = route(model, a, b, ctx)
    if r["found"]:
        return {"reachable": True, "path": r["nodes"], "edges": r["edges"], "blocked_by": []}
    blocked = []
    if ctx["view"] == "ACTOR":
        eng = route(model, a, b, {**ctx, "view": "ENGINE", "knowledge": None})
        if eng["found"]:
            kn = _ctx(model, ctx)["knowledge"]
            for eid in eng["edges"]:
                e = next(x for x in model["edges"] if x["id"] == eid)
                if kn is not None and not kn.knows_edge(e):
                    blocked.append({"edge": eid, "reason": "SECRET_UNKNOWN_TO_ACTOR"})
    lifted = route(model, a, b, {**ctx, "view": "ENGINE", "access_actions": ["_"]})
    if lifted["found"] and not blocked:
        for eid in lifted["edges"]:
            e = next(x for x in model["edges"] if x["id"] == eid)
            st = edge_state(model, e, ctx["chapter"])
            if st == "RESTRICTED":
                blocked.append({"edge": eid, "reason": "CLOSED_WITHOUT_ACTION"})
    if ctx.get("mode") == "VEHICLE" and not ctx.get("vehicle"):
        blocked.append({"edge": None, "reason": "NO_VEHICLE_AVAILABLE"})
    return {"reachable": False, "path": None, "blocked_by": blocked}


def escape_routes(model, origin, ctx=None):
    """Rotas conhecidas a partir de `origin` até esconderijos registrados, portais e saídas aparentes."""
    ctx = _ctx(model, make_ctx(**(ctx or {})))
    g = Graph(model)
    targets = {}
    for h in model["hideouts"]:
        targets[h["location"]] = "HIDEOUT"
    for l in model["locations"]:
        types = cc.as_list(l.get("type"))
        if "FRAME_PORTAL" in types:
            targets.setdefault(l["id"], "APPARENT_EXIT")
    out = []
    for tid, kind in targets.items():
        if tid == origin:
            continue
        p = g.shortest_path(origin, tid, ctx)
        if p:
            t = g.path_times(p, ctx)
            out.append({"to": tid, "kind": kind, "expected_s": round(t["expected_s"]), "length_m": round(t["length_nominal_m"]),
                        "edges": [e["id"] for _, _, e in p["edges"]]})
    out.sort(key=lambda r: r["expected_s"])
    return out


# ---------------------------------------------------------------------------
# validação de deslocamento (SDD 17.7)
# ---------------------------------------------------------------------------

def _add(out, code, sev, chapter, evidence, detail, action):
    out.append(cc.finding(code, sev, chapter, evidence, detail, action))


def validate_movement(model, mv, stagings, ledger=None, defaults=None):
    """Valida um movimento entre dois stagings. Retorna {verdict, findings, times}."""
    defaults = defaults or {}
    out = []
    st = {s["id"]: s for s in stagings}
    a, b = st.get(mv.get("from_staging")), st.get(mv.get("to_staging"))
    mid = mv.get("id", "?")
    if not a or not b:
        _add(out, "STAGING_MISSING", "HIGH", None, mid, "Movimento aponta para staging inexistente.", "Corrigir.")
        return {"verdict": "FAIL", "findings": out, "times": None}
    chapter = b.get("chapter")
    actor = mv.get("actor") or a.get("actor")
    cond = mv.get("conditions") or {}
    ctx = make_ctx(mode=mv.get("mode", "WALK"), chapter=chapter, view="ACTOR", actor=actor, ledger=ledger,
                   lighting=cond.get("lighting", "DAYLIGHT"), weather=cond.get("weather", "CLEAR"),
                   injury=cond.get("injury", "NONE"), carrying=cond.get("carrying", "NONE"),
                   profile=defaults.get("profiles", {}).get(actor, "FIT"), access_actions=cc.as_list(mv.get("access_actions")),
                   familiar=cond.get("familiar", True), vehicle=bool(defaults.get("vehicle")))
    ctx = _ctx(model, ctx)
    g = Graph(model)
    interval = (parse_clock(b["at"]) - parse_clock(a["at"])) * 60.0   # segundos
    if interval < 0:
        _add(out, "TR-01 TRAVEL_PHYSICALLY_IMPOSSIBLE", "HIGH", chapter, mid, "Chegada anterior à partida.", "Corrigir os horários.")
        return {"verdict": "FAIL", "findings": out, "times": None}
    declared = cc.as_list(mv.get("route"))
    origin, dest = a.get("location"), b.get("location")
    if origin == dest:
        return {"verdict": "PASS", "findings": out, "times": None}
    path = None
    if declared:
        edges = cc.index_by_id(model["edges"])
        seq, cur, ok = [], origin, True
        for eid in declared:
            e = edges.get(eid)
            if e is None:
                _add(out, "CG-01 EDGE_DANGLING", "BLOCKER", chapter, f"{mid}: {eid}", "Rota declarada usa aresta inexistente.", "Corrigir.")
                ok = False
                break
            nxt = e["to"] if e["from"] == cur else e["from"] if e["to"] == cur else None
            if nxt is None:
                _add(out, "TR-06 NO_PERMITTED_PATH", "HIGH", chapter, f"{mid}: {eid}", f"A rota declarada não é contínua em {cur}.", "Corrigir a sequência.")
                ok = False
                break
            okk, reason, _ = g.usable(e, ctx)
            if not okk:
                code = {"SECRET_UNKNOWN_TO_ACTOR": "KN-01 SECRET_ROUTE_UNKNOWN_TO_ACTOR", "CLOSED_WITHOUT_ACTION": "AC-01 CLOSED_TRAVERSAL_WITHOUT_ACTION"}.get(reason, "TR-06 NO_PERMITTED_PATH")
                _add(out, code, "HIGH", chapter, f"{mid}: {eid}", f"A rota declarada usa aresta indisponível ({reason}).",
                     "Ensinar a rota ao ator (knowledge_delta), registrar a ação que a abre, ou trocar a rota.")
                ok = False
            seq.append((cur, nxt, e))
            cur = nxt
        if ok and cur != dest:
            _add(out, "TR-06 NO_PERMITTED_PATH", "HIGH", chapter, mid, f"A rota declarada termina em {cur}, não em {dest}.", "Corrigir.")
            ok = False
        if ok:
            path = {"edges": seq, "nodes": [origin] + [s[1] for s in seq], "cost": 0}
    else:
        path = g.shortest_path(origin, dest, ctx)
        if path is None:
            r = reachable(model, origin, dest, {**{k: v for k, v in ctx.items() if k != "knowledge"}, "view": "ACTOR",
                                                "knowledge": ctx["knowledge"]})
            reasons = ", ".join(x["reason"] for x in r["blocked_by"]) or "sem ligação no grafo"
            code = "KN-01 SECRET_ROUTE_UNKNOWN_TO_ACTOR" if "SECRET_UNKNOWN_TO_ACTOR" in reasons else \
                   "AC-01 CLOSED_TRAVERSAL_WITHOUT_ACTION" if "CLOSED_WITHOUT_ACTION" in reasons else "TR-06 NO_PERMITTED_PATH"
            _add(out, code, "HIGH", chapter, f"{mid}: {origin} → {dest}", f"Nenhum caminho permitido ({reasons}).",
                 "Declarar como o ator sabe/abre o caminho, ou mudar o destino.")
    times = None
    if path is not None:
        times = g.path_times(path, ctx)
        for w in times["warnings"]:
            _add(out, w, "MEDIUM", chapter, mid, "Dimensões do subsolo não especificadas (SDD 11.4): tempo esperado a passo agachado.", "Declarar por proposta.")
        if any(edge_state(model, e, chapter) == "UNKNOWN" for _, _, e in path["edges"]):
            _add(out, "SUBTERRANEAN_STATE_UNSPECIFIED", "MEDIUM", chapter, mid, "Aresta com estado físico UNKNOWN em uso.", "Declarar o estado.")
        mode = ctx["mode"]
        if interval < times["min_s"] - 1e-6:
            _add(out, "TR-01 TRAVEL_PHYSICALLY_IMPOSSIBLE", "HIGH", chapter, mid,
                 f"Intervalo {round(interval)} s < mínimo físico {round(times['min_s'])} s ({mode}, {round(times['length_min_m'])} m).",
                 f"Aumentar o intervalo para ≥ {round(times['min_s'] / 60, 1)} min ou aproximar os lugares.")
        else:
            if mode == "RUN" and interval < times["profile_max_effort_s"] - 1e-6:
                _add(out, "TR-03 TRAVEL_BEYOND_PROFILE", "HIGH", chapter, mid,
                     f"Intervalo {round(interval)} s < tempo com o máximo esforço do perfil {ctx['profile']} ({round(times['profile_max_effort_s'])} s).",
                     "Só um corredor acima do perfil faria isso: ajustar o perfil do ator ou o intervalo.")
            elif mode == "WALK" and interval < g.walk_brisk_s(times) - 1e-6:
                _add(out, "TR-02 TRAVEL_REQUIRES_RUNNING", "MEDIUM", chapter, mid,
                     f"A pé só cabe em passo muito rápido (< {WALK_BRISK_MPS} m/s).", "Declarar corrida ou ampliar o intervalo.")
            elif interval < times["expected_s"] - 1e-6:
                _add(out, "TR-07 TRAVEL_TIGHT", "MEDIUM", chapter, mid, f"Intervalo {round(interval)} s < esperado {round(times['expected_s'])} s.",
                     "Possível, mas apertado.")
            elif interval > times["max_reasonable_s"] + 1e-6:
                _add(out, "TR-04 UNEXPLAINED_DELAY", "INFO", chapter, mid, f"Intervalo {round(interval)} s > razoável {round(times['max_reasonable_s'])} s.",
                     "A narrativa pode explicar o atraso.")
    sev = {f["severity"] for f in out}
    verdict = "FAIL" if sev & cc.BLOCKING else ("WARNING" if "MEDIUM" in sev else "PASS")
    return {"verdict": verdict, "findings": out, "times": times}


def validate_staging(model, doc, ledger=None, defaults=None):
    """Valida STAGING.yaml: movimentos declarados e inferidos entre stagings consecutivos do mesmo ator."""
    findings, results = [], []
    stagings = cc.as_list(doc.get("staging"))
    locs = cc.index_by_id(model["locations"])
    for s in stagings:
        if s.get("location") not in locs:
            findings.append(cc.finding("CG-01 EDGE_DANGLING", "BLOCKER", s.get("chapter"), f"{s.get('id')}.location={s.get('location')}",
                                       "Staging em lugar inexistente.", "Corrigir."))
        elif locs[s["location"]].get("connectivity") == "UNDECLARED" or cc.project_location(model, locs[s["location"]]) is None \
                and locs[s["location"]].get("layer") != "SUBTERRANEAN" and "JUNCTION" not in cc.as_list(locs[s["location"]].get("type")):
            findings.append(cc.finding("TR-06 NO_PERMITTED_PATH", "HIGH", s.get("chapter"), f"{s.get('id')}: {s.get('location')}",
                                       "Lugar sem posição/conectividade declarada não pode ser palco de cena.",
                                       "Declarar a conectividade por proposta antes de usar o lugar."))
        role = s.get("role")
        if role == "HIDING" and not any(h["location"] == s.get("location") for h in model["hideouts"]):
            findings.append(cc.finding("HD-01 SPONTANEOUS_HIDEOUT", "HIGH", s.get("chapter"), f"{s.get('id')}: {s.get('location')}",
                                       "Esconderijo espontâneo: o lugar não é um esconderijo registrado.", "Propor o esconderijo antes de usá-lo."))
    declared = {(m.get("from_staging"), m.get("to_staging")) for m in cc.as_list(doc.get("movements"))}
    for m in cc.as_list(doc.get("movements")):
        r = validate_movement(model, m, stagings, ledger, defaults)
        results.append({"movement": m.get("id"), **r})
        findings.extend(r["findings"])
    by_actor = defaultdict(list)
    for s in stagings:
        by_actor[s.get("actor")].append(s)
    for actor, lst in by_actor.items():
        lst.sort(key=lambda s: parse_clock(s["at"]))
        for x, y in zip(lst, lst[1:]):
            if x.get("location") != y.get("location") and (x["id"], y["id"]) not in declared:
                inferred = {"id": f"MOV-INFERRED-{x['id']}-{y['id']}", "actor": actor, "from_staging": x["id"], "to_staging": y["id"],
                            "mode": "WALK", "route": None}
                r = validate_movement(model, inferred, stagings, ledger, defaults)
                for f in r["findings"]:
                    if f["category"].startswith("TR-01") or f["category"].startswith("TR-06"):
                        f = dict(f, category="TR-05 TELEPORT", detail="Sem movimento declarado e sem tempo/caminho para o deslocamento: " + f["detail"])
                    findings.append(f)
                results.append({"movement": inferred["id"], **r})
    return {"findings": findings, "movements": results}
