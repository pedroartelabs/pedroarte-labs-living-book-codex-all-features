"""Visibilidade, esconderijos, gargalos e perseguição (capability neutra `features.cartography`).

Slice 3 de docs/sdd/*CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md (seções 16, 18, 28, 29.3).
Não contém nome de nenhuma obra. Não é um game engine: perseguição é verificada por JANELAS de
chegada em nós (mais cedo / mais tarde), nunca por simulação contínua.

Princípios:
  * DETECTAR uma figura não é RECONHECER quem é: reconhecimento é fora de escopo (canon narrativo);
  * sem relevo nem altura de edifícios nas fontes, visibilidade só é VISIBLE por sightline declarada;
    dentro do limiar sem obstáculo classificado é UNDETERMINED (a prosa não pode afirmar visão);
  * a superfície nunca vê o subsolo; o perseguidor só usa aresta que conhece;
  * o motor não decide quem vence: aponta o que é fisicamente coerente e onde está a tensão.

Sem dependências novas: biblioteca padrão.
"""
from __future__ import annotations

import heapq
import math
from collections import defaultdict

import cartography_graph as cg
import check_cartography as cc

# limiar (m) de detecção de figura humana em movimento, alvo sem luz própria (SDD 16.3; OQ-CART-14 aprovado)
DETECTION_UNLIT = {"DAYLIGHT": 1500.0, "OVERCAST": 1000.0, "TWILIGHT": 400.0, "NIGHT_MOON": 150.0, "NIGHT_DARK": 30.0}
DETECTION_LIT = {"TWILIGHT": 1500.0, "NIGHT_MOON": 2000.0, "NIGHT_DARK": 2000.0}
FOG_UNLIT, FOG_LIT = 60.0, 150.0
SIGHT_RESULTS = {"VISIBLE", "PARTIAL", "NOT_VISIBLE"}
GROUP_KEY = {"DAYLIGHT": "DAYLIGHT", "OVERCAST": "DAYLIGHT"}
EFFORT_PHASE_M = 400.0                         # primeiros 400 m em esforço máximo (SDD 17.3)
CLOSABLE_TOLERANCE = 1e-6


# ---------------------------------------------------------------------------
# visibilidade (SDD 16)
# ---------------------------------------------------------------------------

def detection_limit(model, lighting, lit=False, fog=False):
    table = dict(DETECTION_UNLIT)
    table.update({k: float(v) for k, v in ((model["manifest"].get("settings") or {}).get("detection_thresholds_m") or {}).items()})
    limit = table.get(lighting, table["DAYLIGHT"])
    if lit and lighting in DETECTION_LIT:
        limit = DETECTION_LIT[lighting]
    if fog:
        limit = min(limit, FOG_LIT if lit else FOG_UNLIT)
    return limit


def _declared(model, a, b, lighting):
    key = GROUP_KEY.get(lighting, lighting)
    for s in model.get("sightlines") or []:
        ends = {s.get("from"), s.get("to")}
        if ends == {a, b} and (s.get("symmetric", True) or (s.get("from"), s.get("to")) == (a, b)):
            res = (s.get("result") or {}).get(key)
            if res in SIGHT_RESULTS:
                return s, res
    return None, None


def visible_from(model, a, b, ctx=None):
    """`visible_from(A, B)`: A observa B. Retorna {result, basis, reason, distance_m, threshold_m}."""
    ctx = ctx or {}
    lighting = ctx.get("lighting", "DAYLIGHT")
    lit = bool(ctx.get("target_lit"))
    fog = ctx.get("weather") == "FOG"
    g = cg.Graph(model)
    out = {"from": a, "to": b, "lighting": lighting, "target_lit": lit}
    if ctx.get("recognize"):
        out["recognition"] = "RECOGNITION_OUT_OF_SCOPE"      # quem é: decisão do canon narrativo
    if a == b:
        return {**out, "result": "VISIBLE", "basis": "DERIVED_RULE", "reason": "SAME_LOCATION"}
    if a not in g.locs or b not in g.locs:
        return {**out, "result": "UNDETERMINED", "basis": "UNDETERMINED", "reason": "UNKNOWN_LOCATION"}
    sgt, res = _declared(model, a, b, lighting)
    if sgt:
        return {**out, "result": res, "basis": "DECLARED", "reason": sgt.get("id")}
    la, lb = g.locs[a], g.locs[b]
    under = lambda l: l.get("layer") == "SUBTERRANEAN" or l.get("visibility") == "UNDERGROUND"
    if under(la) or under(lb):
        return {**out, "result": "NOT_VISIBLE", "basis": "DERIVED_RULE", "reason": "UNDERGROUND"}
    pa, pb = g.pos(a), g.pos(b)
    if not pa or not pb:
        return {**out, "result": "UNDETERMINED", "basis": "UNDETERMINED", "reason": "POSITION_UNKNOWN"}
    d_nom = cc.euclid(pa, pb)
    d_min = max(0.0, d_nom - pa["accuracy_m"] - pb["accuracy_m"])
    limit = detection_limit(model, lighting, lit, fog)
    out.update(distance_m=[round(d_min), round(d_nom)], threshold_m=limit)
    if d_min > limit:
        return {**out, "result": "NOT_VISIBLE", "basis": "DERIVED_RULE", "reason": "BEYOND_DETECTION_LIMIT"}
    return {**out, "result": "UNDETERMINED", "basis": "UNDETERMINED", "reason": "WITHIN_LIMIT_OBSTACLES_UNCLASSIFIED"}


def check_sightlines(model) -> list[dict]:
    """Validação de seeds: sightline aponta para lugares existentes, com resultado válido e proposta de origem."""
    out = []
    ids = {l["id"] for l in model["locations"]}
    for s in model.get("sightlines") or []:
        sid = s.get("id", "?")
        for end in (s.get("from"), s.get("to")):
            if end not in ids:
                out.append(cc.finding("CG-01 EDGE_DANGLING", "BLOCKER", None, f"{sid}: {end}", "Sightline em lugar inexistente.", "Corrigir."))
        for k, v in (s.get("result") or {}).items():
            if v not in SIGHT_RESULTS:
                out.append(cc.finding("INVALID_ENUM", "HIGH", None, f"{sid}.result.{k}={v!r}", f"∈ {sorted(SIGHT_RESULTS)}.", "Corrigir."))
        if not s.get("source"):
            out.append(cc.finding("SIGHTLINE_WITHOUT_SOURCE", "HIGH", None, sid,
                                  "Sightline sem proposta de origem: visibilidade não se decide por conveniência de cena.",
                                  "Referenciar a proposta aprovada."))
    return out


# ---------------------------------------------------------------------------
# gargalos (SDD 28.2): pontos de articulação e pontes do grafo permitido
# ---------------------------------------------------------------------------

def bottlenecks(model, ctx=None, layers=None):
    ctx = cg._ctx(model, cg.make_ctx(**(ctx or {})))
    g = cg.Graph(model)
    adj = defaultdict(list)
    for e in g.edges:
        ok, _, _ = g.usable(e, ctx)
        if not ok:
            continue
        a, b = e["from"], e["to"]
        if layers and (g.locs[a].get("layer") not in layers or g.locs[b].get("layer") not in layers):
            continue
        adj[a].append((b, e["id"]))
        adj[b].append((a, e["id"]))
    disc, low, art, bridges = {}, {}, set(), []
    timer = 0
    for root in list(adj):
        if root in disc:
            continue
        disc[root] = low[root] = timer
        timer += 1
        root_children = 0
        stack = [(root, None, iter(adj[root]))]
        while stack:
            node, into, it = stack[-1]
            advanced = False
            for nbr, eid in it:
                if eid == into:
                    continue
                if nbr in disc:
                    low[node] = min(low[node], disc[nbr])
                else:
                    disc[nbr] = low[nbr] = timer
                    timer += 1
                    stack.append((nbr, eid, iter(adj[nbr])))
                    advanced = True
                    break
            if advanced:
                continue
            stack.pop()
            if stack:
                par = stack[-1][0]
                low[par] = min(low[par], low[node])
                if low[node] > disc[par]:
                    bridges.append(into)
                if par == root:
                    root_children += 1
                elif low[node] >= disc[par]:
                    art.add(par)
        if root_children > 1:
            art.add(root)
    return {"articulation_points": sorted(art), "bridges": sorted(bridges)}


# ---------------------------------------------------------------------------
# esconderijos em uso (SDD 18): HD-02..04 (HD-01 vive em cartography_graph.validate_staging)
# ---------------------------------------------------------------------------

def _num(v):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def check_hideout_usage(model, stagings, ledger=None) -> list[dict]:
    out = []
    hideouts = {h["location"]: h for h in model["hideouts"]}
    hiding = [s for s in stagings if s.get("role") == "HIDING" and s.get("location") in hideouts]
    by_place_time = defaultdict(list)
    for s in hiding:
        by_place_time[(s["location"], s["at"])].append(s)
    for (loc, at), group in by_place_time.items():
        cap = _num(hideouts[loc].get("capacity"))
        total = sum(int(x.get("group_size", 1)) for x in group)
        if cap is not None and total > cap:
            out.append(cc.finding("HD-02 HIDEOUT_OVER_CAPACITY", "HIGH", group[0].get("chapter"), f"{hideouts[loc]['id']} @ {at}",
                                  f"{total} pessoas escondidas para capacidade {int(cap)}.", "Reduzir o grupo ou usar outro esconderijo registrado."))
    by_actor = defaultdict(list)
    for s in stagings:
        by_actor[s.get("actor")].append(s)
    for actor, lst in by_actor.items():
        lst.sort(key=lambda s: cg.parse_clock(s["at"]))
        for i, s in enumerate(lst):
            if s.get("role") != "HIDING" or s.get("location") not in hideouts:
                continue
            h = hideouts[s["location"]]
            safe_h = _num(h.get("duration_safe"))
            if safe_h is not None:
                j = i
                while j + 1 < len(lst) and lst[j + 1].get("location") == s["location"]:
                    j += 1
                stay = (cg.parse_clock(lst[j]["at"]) - cg.parse_clock(s["at"])) / 60.0
                if stay > safe_h and (i == 0 or lst[i - 1].get("location") != s["location"] or lst[i - 1].get("role") != "HIDING"):
                    out.append(cc.finding("HD-03 HIDEOUT_OVERSTAY", "HIGH", s.get("chapter"), f"{h['id']}: {actor}",
                                          f"Permanência de {stay:.1f} h > duration_safe {safe_h:g} h.", "Encurtar a permanência ou justificar o risco."))
            known = cg.Knowledge(model, actor, s.get("chapter"), ledger).known
            for ev in cc.as_list(h.get("compromise_events")):
                if ev.get("chapter", 0) > (s.get("chapter") or 0):
                    continue
                effect = ev.get("effect")
                if actor and ev.get("event") in known:
                    sev = "HIGH" if effect in ("COMPROMISED", "DESTROYED") else "MEDIUM"
                    out.append(cc.finding("HD-04 COMPROMISED_HIDEOUT_REUSED", sev, s.get("chapter"), f"{h['id']}: {actor} × {ev.get('event')}",
                                          f"O ator sabe que o esconderijo foi {effect} e o usa de novo sem nova ação.",
                                          "Registrar a ação que o torna seguro de novo, ou escolher outro."))
                else:
                    out.append(cc.finding("HD-04 COMPROMISED_HIDEOUT_REUSED", "INFO", s.get("chapter"), f"{h['id']}: {actor} × {ev.get('event')}",
                                          f"Esconderijo {effect} e o ator ainda não sabe (tensão dramática legítima).", "Nenhuma."))
    return out


def accessible_hideouts(model, origin, ctx=None):
    """Esconderijos registrados alcançáveis a partir de `origin`, com o veredito de vigilância da rota.

    Vigilância só é conhecida quando o canon a declara (`surveillance` no lugar): enquanto houver lugar da rota com
    vigilância UNKNOWN o veredito é `UNDETERMINED_SURVEILLANCE` e a resposta lista o que precisa ser decidido —
    o motor não inventa vigilância."""
    ctx = cg._ctx(model, cg.make_ctx(**(ctx or {})))
    g = cg.Graph(model)
    out = []
    for h in model["hideouts"]:
        path = g.shortest_path(origin, h["location"], ctx)
        if path is None:
            out.append({"hideout": h["id"], "reachable": False})
            continue
        restricted = [e["id"] for _, _, e in path["edges"] if cg.edge_state(model, e, ctx["chapter"]) == "RESTRICTED"]
        nodes = path["nodes"]
        states = {n: g.locs[n].get("surveillance", "UNKNOWN") for n in nodes}
        watched = [n for n, v in states.items() if v in ("PATROLLED", "WATCHED", "POSTED")]
        unknown = [n for n, v in states.items() if v == "UNKNOWN" and "JUNCTION" not in cc.as_list(g.locs[n].get("type"))]
        verdict = "WATCHED" if watched else "UNDETERMINED_SURVEILLANCE" if unknown else "NOT_WATCHED_KNOWN"
        out.append({"hideout": h["id"], "reachable": True, "edges": [e["id"] for _, _, e in path["edges"]], "restricted_edges": restricted,
                    "surveillance": verdict, "watched_places": watched, "surveillance_to_decide": unknown})
    return out


# ---------------------------------------------------------------------------
# perseguição (SDD 28)
# ---------------------------------------------------------------------------

def dijkstra_all(g, start, ctx, kind="shortest"):
    dist, prev = {start: 0.0}, {}
    heap = [(0.0, start)]
    while heap:
        d, n = heapq.heappop(heap)
        if d > dist.get(n, math.inf):
            continue
        for m, e in g.adj.get(n, []):
            ok, _, _ = g.usable(e, ctx)
            if not ok:
                continue
            nd = d + g.weight(e, ctx, kind)
            if nd < dist.get(m, math.inf):
                dist[m] = nd
                prev[m] = (n, e)
                heapq.heappush(heap, (nd, m))
    return dist, prev


def _role_ctx(ch, role, ledger, defaults):
    cond = role.get("conditions") or {}
    return cg.make_ctx(mode=role.get("mode", "RUN"), profile=role.get("profile") or (defaults or {}).get("profiles", {}).get(role.get("actor"), "FIT"),
                       chapter=ch.get("chapter"), view="ACTOR", actor=role.get("actor"), ledger=ledger,
                       lighting=ch.get("lighting", "DAYLIGHT"), weather=ch.get("weather", "CLEAR"),
                       injury=cond.get("injury", "NONE"), carrying=cond.get("carrying", "NONE"),
                       familiar=cond.get("familiar", True), access_actions=cc.as_list(role.get("access_actions")))


def _declared_path(g, model, start, route, ctx):
    """(path|None, [(edge_id, reason)])"""
    edges = cc.index_by_id(model["edges"])
    seq, cur, problems = [], start, []
    for eid in route:
        e = edges.get(eid)
        if e is None:
            problems.append((eid, "EDGE_UNKNOWN"))
            return None, problems
        nxt = e["to"] if e["from"] == cur else e["from"] if e["to"] == cur else None
        if nxt is None:
            problems.append((eid, "NOT_CONTINUOUS"))
            return None, problems
        ok, reason, _ = g.usable(e, ctx)
        if not ok:
            problems.append((eid, reason))
        seq.append((cur, nxt, e))
        cur = nxt
    return {"edges": seq, "nodes": [start] + [s[1] for s in seq], "cost": 0}, problems


def node_windows(g, path, ctx):
    """[(nó, mais_cedo_s, mais_tarde_s, distância_nominal_m)] — janela de chegada em cada nó do caminho."""
    lnom, lmin, _ = g.resolve_lengths(path)
    prof = cg.PROFILES[ctx["profile"]]
    mode = ctx["mode"]
    v_effort = prof["RUN_MAX"] if mode == "RUN" else prof["CRAWL"] if mode == "CRAWL" else prof["WALK"]
    v_sust = prof["RUN_S"] if mode == "RUN" else v_effort
    t_early = t_late = 0.0
    dist_min = dist_nom = 0.0
    out = [(path["nodes"][0], 0.0, 0.0, 0.0)]
    for idx, (_, b, e) in enumerate(path["edges"]):
        lm, ln = lmin[idx] or 0.0, lnom[idx] or 0.0
        if e.get("edge_type") == "PORTAL":
            t_early += cg.PORTAL_DELAY_S["min"]
            t_late += cg.PORTAL_DELAY_S["expected"]
        else:
            stooped = e.get("terrain") in ("DRAIN_CHANNEL", "CRAWLSPACE") or (
                e.get("edge_type") in ("SECRET_PASSAGE", "TUNNEL", "DRAIN") and e.get("max_passage") in (None, "UNSPECIFIED", "ADULT_STOOPED"))
            if stooped:
                cap = prof["CRAWL"] if e.get("terrain") == "CRAWLSPACE" else prof["STOOP"]
                speed_first = speed_rest = cap
            else:
                speed_first, speed_rest = v_effort, v_sust
            # esforço máximo nos primeiros 400 m percorridos (mínimo do intervalo), depois sustentado
            rem = lm
            if dist_min < EFFORT_PHASE_M and rem > 0:
                take = min(rem, EFFORT_PHASE_M - dist_min)
                t_early += take / speed_first
                rem -= take
            t_early += rem / speed_rest
            t_late += g.edge_expected_time(e, ctx, ln) if ln else 0.0
        dist_min += lm
        dist_nom += ln
        out.append((b, t_early, t_late, dist_nom))
    return out


def _window_map(windows):
    return {n: (early, late, d) for n, early, late, d in windows}


def analyze_chase(model, ch, ledger=None, defaults=None):
    """Analisa uma perseguição: janelas, pontos de interceptação e de fuga, gargalos, becos, transições ocultas + achados."""
    g = cg.Graph(model)
    cid = ch.get("id", "?")
    chapter = ch.get("chapter")
    findings = []
    roles = {}
    for role_name, code_unknown in (("target", "CH-06 ESCAPE_THROUGH_UNKNOWN"), ("pursuer", "CH-02 PURSUER_SECRET_ROUTE")):
        role = ch.get(role_name) or {}
        ctx = _role_ctx(ch, role, ledger, defaults)
        ctx = cg._ctx(model, ctx)
        path, problems = None, []
        start = role.get("start")
        if start not in g.locs:
            findings.append(cc.finding("CG-01 EDGE_DANGLING", "BLOCKER", chapter, f"{cid}.{role_name}.start={start}", "Partida em lugar inexistente.", "Corrigir."))
            roles[role_name] = {"ctx": ctx, "path": None, "windows": {}, "role": role, "start": start, "kn": ctx.get("knowledge")}
            continue
        if role.get("route"):
            path, problems = _declared_path(g, model, start, cc.as_list(role["route"]), ctx)
        elif role.get("end"):
            path = g.shortest_path(start, role["end"], ctx)
            if path is None:
                problems.append((None, "NO_PERMITTED_PATH"))
        for eid, reason in problems:
            if reason == "SECRET_UNKNOWN_TO_ACTOR":
                findings.append(cc.finding(code_unknown, "HIGH", chapter, f"{cid}.{role_name}: {eid}",
                                           "A rota usa aresta secreta que o ator ainda não conhece (INV-C04).",
                                           "Ensinar a rota ao ator antes, ou escolher rota conhecida."))
            elif reason == "CLOSED_WITHOUT_ACTION":
                findings.append(cc.finding("AC-01 CLOSED_TRAVERSAL_WITHOUT_ACTION", "HIGH", chapter, f"{cid}.{role_name}: {eid}",
                                           "A rota atravessa aresta fechada sem ação narrativa.", "Registrar a ação que a abre."))
            else:
                findings.append(cc.finding("TR-06 NO_PERMITTED_PATH", "HIGH", chapter, f"{cid}.{role_name}: {eid or role.get('end')}",
                                           f"Rota inviável ({reason}).", "Corrigir a rota ou o destino."))
        wins = node_windows(g, path, ctx) if path else ([(start, 0.0, 0.0, 0.0)] if start in g.locs else [])
        roles[role_name] = {"ctx": ctx, "path": path, "windows": _window_map(wins), "role": role, "start": start,
                            "kn": ctx.get("knowledge")}
    tgt, pur = roles["target"], roles["pursuer"]

    # início: lacuna e visibilidade declaradas versus o grafo
    ts, ps = (tgt.get("start"), pur.get("start"))
    if ts in g.locs and ps in g.locs and ts != ps:
        pa, pb = g.pos(ts), g.pos(ps)
        gap = _num(ch.get("initial_gap_m"))
        if pa and pb and gap is not None:
            floor = max(0.0, cc.euclid(pa, pb) - pa["accuracy_m"] - pb["accuracy_m"])
            if gap < floor:
                findings.append(cc.finding("CH-08 GAP_INCONSISTENT", "HIGH", chapter, f"{cid}: gap {gap:g} m < {round(floor)} m",
                                           "A lacuna inicial é menor que a distância mínima entre os pontos de partida.", "Corrigir a lacuna ou as partidas."))
    if ch.get("initial_visibility") and ts in g.locs and ps in g.locs:
        v = visible_from(model, ps, ts, {"lighting": ch.get("lighting", "DAYLIGHT"), "weather": ch.get("weather"),
                                         "target_lit": (ch.get("target") or {}).get("lit")})
        if ch["initial_visibility"] == "VISIBLE" and v["result"] == "NOT_VISIBLE":
            findings.append(cc.finding("VS-01 SIGHT_CLAIM_NOT_VISIBLE", "HIGH", chapter, f"{cid}: {ps} → {ts}",
                                       f"A prosa começa com o alvo visível; o grafo diz NOT_VISIBLE ({v['reason']}).", "Ajustar iluminação/lugares ou a afirmação."))
        elif ch["initial_visibility"] == "VISIBLE" and v["result"] == "UNDETERMINED":
            findings.append(cc.finding("VS-03 SIGHT_CLAIM_UNDETERMINED", "MEDIUM", chapter, f"{cid}: {ps} → {ts}",
                                       "Visibilidade inicial indeterminada: declare a sightline.", "Propor a sightline."))

    def pursuer_earliest(node):
        """Menor tempo (mais cedo) do perseguidor até `node`, pela rota dele ou pelo melhor caminho que ele conhece."""
        w = pur["windows"].get(node)
        if w:
            return w[0], (pur.get("path") or {}).get("nodes")
        if ps not in g.locs:
            return None, None
        path = g.shortest_path(ps, node, pur["ctx"])
        if not path:
            return None, None
        wins = _window_map(node_windows(g, path, pur["ctx"]))
        return wins[node][0], path["nodes"]

    # eventos declarados pela prosa
    for i, ev in enumerate(cc.as_list(ch.get("declared_events"))):
        kind = ev.get("kind") or ev.get("claim") or "ARRIVES"
        eid = f"{cid}.event[{i}]:{kind}"
        node = ev.get("at_node")
        if kind in ("ARRIVES", "TARGET_REACHES_HIDEOUT", "TARGET_REACHES", "PURSUER_REACHES"):
            actor_role = "pursuer" if kind == "PURSUER_REACHES" or ev.get("actor") == (ch.get("pursuer") or {}).get("actor") else "target"
            r = roles[actor_role]
            w = r["windows"].get(node)
            if w is None:
                findings.append(cc.finding("CH-01 CHASE_TELEPORT", "HIGH", chapter, f"{eid} @ {node}",
                                           f"O {actor_role} aparece em nó fora da própria rota/janela alcançável.", "Incluir o nó na rota ou corrigir."))
            elif ev.get("at_s") is not None and float(ev["at_s"]) < w[0] - 1e-6:
                findings.append(cc.finding("CH-01 CHASE_TELEPORT", "HIGH", chapter, f"{eid} @ {node}",
                                           f"Chegada em {ev['at_s']} s < mais cedo possível {round(w[0])} s.", f"Chegada só a partir de {round(w[0])} s."))
        elif kind == "INTERCEPT":
            tw = tgt["windows"].get(node)
            pe, _ = pursuer_earliest(node)
            if tw is None or pe is None:
                findings.append(cc.finding("CH-04 INTERCEPT_IMPOSSIBLE", "HIGH", chapter, f"{eid} @ {node}",
                                           "Interceptação num nó que não está na rota do alvo ou que o perseguidor não alcança.", "Escolher um nó comum."))
            elif pe > tw[1] + 1e-6:
                findings.append(cc.finding("CH-04 INTERCEPT_IMPOSSIBLE", "HIGH", chapter, f"{eid} @ {node}",
                                           f"O perseguidor chega no mais cedo a {round(pe)} s; o alvo já passou (mais tarde {round(tw[1])} s).", "Sem sobreposição de janelas."))
            elif ev.get("at_s") is not None and float(ev["at_s"]) < pe - 1e-6:
                findings.append(cc.finding("CH-01 CHASE_TELEPORT", "HIGH", chapter, f"{eid} @ {node}",
                                           f"O perseguidor não chega antes de {round(pe)} s.", "Ajustar o instante."))
        elif kind == "GAP_CLOSED":
            over = _num(ev.get("over_s")) or 0.0
            claimed = (_num(ev.get("from_gap_m")) or 0.0) - (_num(ev.get("to_gap_m")) or 0.0)
            pp, tp = cg.PROFILES[pur["ctx"]["profile"]], cg.PROFILES[tgt["ctx"]["profile"]]
            v_p = (pp["RUN_MAX"] if pur["ctx"]["mode"] == "RUN" else pp["WALK"]) / g.global_factor(pur["ctx"])
            v_t = (tp["RUN_S"] if tgt["ctx"]["mode"] == "RUN" else tp["WALK"]) / g.global_factor(tgt["ctx"])
            closable = max(0.0, v_p - v_t) * over
            if claimed > closable + CLOSABLE_TOLERANCE:
                findings.append(cc.finding("CH-03 GAP_CLOSURE_IMPOSSIBLE", "HIGH", chapter, eid,
                                           f"A prosa fecha {claimed:g} m em {over:g} s; a diferença máxima de velocidades permite {closable:.0f} m.",
                                           "Aumentar o tempo, reduzir a distância fechada ou mudar condições/perfis."))
        elif kind == "SIGHT_REACQUIRED":
            v = visible_from(model, ev.get("pursuer_at"), ev.get("target_at"), {"lighting": ch.get("lighting", "DAYLIGHT"), "weather": ch.get("weather"),
                                                                                   "target_lit": ev.get("target_lit")})
            if v["result"] == "NOT_VISIBLE":
                findings.append(cc.finding("CH-05 LOS_REACQUIRE_UNJUSTIFIED", "MEDIUM", chapter, eid,
                                           f"O perseguidor 'volta a ver' o alvo onde a visão é impossível ({v['reason']}).", "Justificar (luz, sightline) ou remover."))
            elif v["result"] == "UNDETERMINED":
                findings.append(cc.finding("CH-05 LOS_REACQUIRE_UNJUSTIFIED", "INFO", chapter, eid,
                                           "Visão indeterminada: a cena pode seguir, mas a sightline não está declarada.", "Propor a sightline."))

    # derivados
    tpath = tgt.get("path")
    tnodes = tpath["nodes"] if tpath else []
    intercept, escape, hidden = [], [], []
    for n in tnodes:
        pe, _ = pursuer_earliest(n)
        if pe is not None and n in tgt["windows"] and pe <= tgt["windows"][n][1] + 1e-6 and n != tgt.get("start"):
            intercept.append({"node": n, "pursuer_earliest_s": round(pe), "target_latest_s": round(tgt["windows"][n][1])})
    pk = pur.get("kn")
    if tpath:
        for a, b, e in tpath["edges"]:
            if pk is not None and not pk.knows_edge(e):
                escape.append({"from": a, "to": b, "edge": e["id"], "why": "ARESTA_DESCONHECIDA_DO_PERSEGUIDOR"})
            if e.get("secret_level") not in (None, "NONE") or e.get("visibility") in ("HIDDEN", "UNDERGROUND") or e.get("edge_type") == "PORTAL":
                hidden.append({"edge": e["id"], "type": e.get("edge_type")})
    bn = bottlenecks(model, {**{k: v for k, v in tgt["ctx"].items() if k != "knowledge"}, "knowledge": tgt["ctx"].get("knowledge")})
    on_route = [n for n in tnodes[1:-1] if n in bn["articulation_points"]]
    for n in on_route:
        pe, _ = pursuer_earliest(n)
        if pe is not None and n in tgt["windows"] and pe <= tgt["windows"][n][0]:
            findings.append(cc.finding("CH-07 BOTTLENECK_IGNORED", "INFO", chapter, f"{cid} @ {n}",
                                       "A rota do alvo passa por um gargalo que o perseguidor pode alcançar primeiro: tensão disponível.", "Nenhuma (informativo)."))
    dead = []
    if tgt.get("start") in g.locs:
        dist, _ = dijkstra_all(g, tgt["start"], tgt["ctx"])
        deg = defaultdict(set)
        for e in g.edges:
            ok, _, _ = g.usable(e, tgt["ctx"])
            if ok:
                deg[e["from"]].add(e["to"])
                deg[e["to"]].add(e["from"])
        hideout_locs = {h["location"] for h in model["hideouts"]}
        for n, d in dist.items():
            l = g.locs[n]
            if len(deg[n]) == 1 and d <= 300.0 and n not in hideout_locs and "FRAME_PORTAL" not in cc.as_list(l.get("type")) \
                    and n != tgt.get("start") and "JUNCTION" not in cc.as_list(l.get("type")):
                dead.append(n)
    return {"id": cid, "target": {"route": tnodes, "windows": {n: [round(w[0]), round(w[1]), round(w[2])] for n, w in tgt["windows"].items()}},
            "pursuer": {"route": (pur.get("path") or {}).get("nodes", []),
                        "windows": {n: [round(w[0]), round(w[1]), round(w[2])] for n, w in pur["windows"].items()}},
            "intercept_points": intercept, "escape_points": escape, "hidden_transitions": hidden,
            "bottlenecks": bn, "bottlenecks_on_target_route": on_route, "dead_ends": sorted(dead), "findings": findings}


# ---------------------------------------------------------------------------
# cena completa: deslocamentos + visão declarada + esconderijos + perseguições
# ---------------------------------------------------------------------------

def check_sees(model, doc) -> list[dict]:
    out = []
    stagings = cc.as_list(doc.get("staging"))
    for s in stagings:
        for i, tgt in enumerate(cc.as_list(s.get("sees"))):
            spec = {"location": tgt} if isinstance(tgt, str) else dict(tgt)
            target_loc = spec.get("location")
            if target_loc is None and spec.get("actor"):
                other = next((x for x in stagings if x.get("actor") == spec["actor"] and x.get("at") == s.get("at")), None)
                target_loc = other.get("location") if other else None
            eid = f"{s.get('id')}.sees[{i}]"
            if target_loc is None:
                out.append(cc.finding("VS-03 SIGHT_CLAIM_UNDETERMINED", "MEDIUM", s.get("chapter"), eid,
                                      "Posição do alvo da visão desconhecida neste instante.", "Declarar o staging do alvo."))
                continue
            cond = s.get("conditions") or {}
            v = visible_from(model, s.get("location"), target_loc, {"lighting": cond.get("lighting", "DAYLIGHT"), "weather": cond.get("weather"),
                                                                     "target_lit": spec.get("lit")})
            if v["result"] == "NOT_VISIBLE":
                code = "VS-02 UNDERGROUND_SIGHT" if v["reason"] == "UNDERGROUND" else "VS-01 SIGHT_CLAIM_NOT_VISIBLE"
                out.append(cc.finding(code, "HIGH", s.get("chapter"), f"{eid}: {s.get('location')} → {target_loc}",
                                      f"A prosa afirma visão impossível ({v['reason']}).", "Mudar luz, distância ou a afirmação."))
            elif v["result"] == "UNDETERMINED":
                out.append(cc.finding("VS-03 SIGHT_CLAIM_UNDETERMINED", "MEDIUM", s.get("chapter"), f"{eid}: {s.get('location')} → {target_loc}",
                                      f"Visão indeterminada ({v['reason']}): a cena pode seguir; declare a sightline.", "Propor a sightline."))
    return out


def validate_scene(model, doc, ledger=None, defaults=None):
    base = cg.validate_staging(model, doc, ledger, defaults)
    findings = list(base["findings"]) + check_sees(model, doc) + check_hideout_usage(model, cc.as_list(doc.get("staging")), ledger)
    chases = []
    for ch in cc.as_list(doc.get("chases")):
        r = analyze_chase(model, ch, ledger, defaults)
        findings.extend(r["findings"])
        chases.append(r)
    return {"findings": findings, "movements": base["movements"], "chases": chases}
