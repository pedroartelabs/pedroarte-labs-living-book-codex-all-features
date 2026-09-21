"""Saídas, mapas (oficial × físico × leitor), camadas e crença por artefato (capability neutra `features.cartography`).

Slice 4 de docs/sdd/*CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md (seções 19–25, 29.3). Não contém nome de nenhuma obra.

Princípios:
  * o sistema cartográfico conhece ESTRUTURA; o sistema narrativo conhece SIGNIFICADO. Nenhuma função daqui
    devolve uma saída "verdadeira": a consulta de saídas devolve classes e alegações, e `exit_truth` devolve
    apenas ponteiros opacos (`truth_ref`), confirmando pertinência só com autorização explícita;
  * mapa do leitor é PROJEÇÃO (baseline dos mapas impressos + ledger + cenas realizadas), nunca o grafo físico;
  * um mapa descreve o mundo por relações (`depicts`); relação diferente de ACCURATE é afirmação sobre a verdade
    e exige base física verificável ou `truth_ref`;
  * crença por artefato: planejar por um mapa falso é narrativa legítima (INFO), atravessar onde não há via não é.

Sem dependências novas: biblioteca padrão.
"""
from __future__ import annotations

import re

import cartography_graph as cg
import check_cartography as cc

EXIT_NOTICE = "EXIT_TRUTH_NOT_IN_CARTOGRAPHY"
DEPICTION_RELATIONS = {"ACCURATE", "OMITS", "PHANTOM", "FALSIFIED_STATUS", "RENAMED", "MISPLACED", "FALSIFIED_ACCESS"}
PHYSICALLY_CHECKABLE = {"OMITS", "PHANTOM", "MISPLACED"}
READER_STATES = ("UNSEEN", "MENTIONED", "SEEN_ON_MAP", "VISITED", "CONNECTION_KNOWN")
_RANK = {s: i for i, s in enumerate(READER_STATES)}
LEVEL_TO_STATE = {"EXISTS": "MENTIONED", "ACCESS": "MENTIONED", "ROUTE": "CONNECTION_KNOWN",
                  "FAMILIAR": "VISITED", "VISITED": "VISITED"}
BLOCKED_STATES = {"BLOCKED", "COLLAPSED", "FLOODED", "SEALED", "DESTROYED"}
RESERVED_LAYER_KEYS = {"id", "name", "status", "era", "note", "author"}


def _f(cat, sev, chapter, evidence, detail, action):
    return cc.finding(cat, sev, chapter, evidence, detail, action)


# ---------------------------------------------------------------------------
# o que está impresso (SDD 22.6)
# ---------------------------------------------------------------------------

def printed_sources(model):
    """Ids de fonte cujo mapa é impresso no livro (artefato MAP com `printed_in_book`)."""
    return {a.get("source_file") for a in model["artifacts"]
            if a.get("kind") == "MAP" and a.get("printed_in_book") and a.get("source_file")}


def printed_ids(model):
    """{locations, edges}: ids que constam dos mapas impressos.

    Lugar: tem `source_px`/nome em fonte impressa, ou é nó do inset subterrâneo desenhado (não `connectivity:
    UNDECLARED`), a menos que `omitted_by` cite o mapa. Aresta: os dois extremos estão impressos e ela é
    desenhada (não é `printed: false`, ligação inferida nem criada por mutação)."""
    src = printed_sources(model)
    maps = {a.get("id") for a in model["artifacts"] if a.get("kind") == "MAP" and a.get("printed_in_book")}
    locs = set()
    for loc in model["locations"]:
        if loc.get("printed") is False or (set(cc.as_list(loc.get("omitted_by"))) & maps and not loc.get("source_px")):
            continue
        by_px = any(p.get("source") in src for p in cc.as_list(loc.get("source_px")))
        by_name = any(n.get("source") in src for n in cc.as_list(loc.get("names"))) or             any(c.get("source") in src for c in cc.as_list(loc.get("claims")))
        inset = loc.get("layer") == "SUBTERRANEAN" and loc.get("connectivity") != "UNDECLARED"
        if by_px or by_name or inset or set(cc.as_list(loc.get("depicted_by"))) & maps:
            locs.add(loc["id"])
    edges = set()
    for e in model["edges"]:
        if e.get("printed") is False or e.get("basis") == "INFERRED" or (e.get("distance_meters") or {}).get("basis") == "INFERRED":
            continue
        if e.get("from") in locs and e.get("to") in locs:
            edges.add(e["id"])
    return {"locations": locs, "edges": edges}


# ---------------------------------------------------------------------------
# saídas e o MYSTERY PRESERVATION GATE, barreira 4 (SDD 20.4)
# ---------------------------------------------------------------------------

def _revealed(item, chapter):
    fr = item.get("first_allowed_reveal", "OPEN")
    return chapter is None or fr in (None, "OPEN") or (isinstance(fr, int) and fr <= chapter)


def exits_query(model, chapter=None):
    """Saídas com classes e alegações. Nunca diz qual é a verdadeira: além da moldura é OFF_MAP."""
    proj = cc.project_all(model)
    out = []
    for ex in model["exits"]:
        if not _revealed(ex, chapter):
            continue
        fp = ex.get("frame_portal")
        out.append({
            "id": ex.get("id"), "road": ex.get("road"), "frame_portal": fp,
            "frame_position": proj.get(fp) if fp else None,
            "exit_classes": sorted(cc.as_list(ex.get("exit_classes"))),
            "claims": [{k: c.get(k) for k in ("class", "text", "source", "epistemic_status")} for c in cc.as_list(ex.get("claims"))],
            "physical": {"drawn_to": (ex.get("physical") or {}).get("drawn_to"), "beyond_frame": "OFF_MAP",
                         "passable_to_frame": (ex.get("physical") or {}).get("passable_to_frame", "UNKNOWN")},
            "frame_status": ex.get("frame_status", "DIGITIZED" if fp else "UNKNOWN"),
            "first_allowed_reveal": ex.get("first_allowed_reveal", "OPEN"),
        })
    return {"notice": EXIT_NOTICE, "count": len(out), "exits": out}


def _ground_truths(ledger):
    found = {}
    for ch in (ledger or {}).get("characters") or []:
        for gt in ch.get("ground_truth") or []:
            if gt.get("id"):
                found[gt["id"]] = gt
    return found


def exit_truth(model, engine_view=False, authorized_by=None, ledger=None):
    """Só ponteiros. O conteúdo da verdade continua no ledger; aqui nunca é lido.

    Sem `engine_view` + `authorized_by` (um GT do ledger) devolve `truth_ref` opaco e nada mais. Com ambos, e se o
    `truth_ref` da saída é exatamente esse GT existente, marca `pertinent: True`: confirma o id, não o significado."""
    gts = _ground_truths(ledger)
    authorized = bool(engine_view and authorized_by and authorized_by in gts)
    rows = []
    for ex in model["exits"]:
        ref = ex.get("truth_ref")
        row = {"exit": ex.get("id"), "truth_ref": ref}
        if authorized and ref:
            row["pertinent"] = (ref == authorized_by)
        rows.append(row)
    status = "AUTHORIZED_ID_CONFIRMATION" if authorized else "POINTERS_ONLY"
    reason = None
    if engine_view and authorized_by and authorized_by not in gts:
        reason = "GT_NOT_FOUND_IN_LEDGER"
    elif authorized_by and not engine_view:
        reason = "ENGINE_VIEW_REQUIRED"
    return {"notice": EXIT_NOTICE, "status": status, "reason": reason, "exits": rows}


# ---------------------------------------------------------------------------
# mapa do leitor (SDD 22.3, 22.6)
# ---------------------------------------------------------------------------

def _bump(states, key, new):
    if _RANK[new] > _RANK.get(states.get(key, "UNSEEN"), 0):
        states[key] = new


def reader_map(model, chapter=0, ledger=None, stagings=None):
    """Projeção: para cada id, UNSEEN · MENTIONED · SEEN_ON_MAP · VISITED · CONNECTION_KNOWN no capítulo.

    Baseline: tudo que está nos mapas impressos é SEEN_ON_MAP desde o capítulo 0 (inclusive a topologia do inset).
    Depois: `knowledge_delta` de READER (prefixo `CART:<NÍVEL>:` ou id puro) e stagings REALIZED com POV."""
    printed = printed_ids(model)
    loc_ids = {l["id"] for l in model["locations"]}
    edge_ids = {e["id"] for e in model["edges"]}
    states = {}
    for lid in printed["locations"]:
        states[lid] = "SEEN_ON_MAP"
    for eid in printed["edges"]:
        states[eid] = "SEEN_ON_MAP"
    if ledger:
        try:
            import check_causal_ledger as cl
            learned = cl.knowledge_state(ledger, "READER", chapter)
        except Exception:  # noqa: BLE001
            learned = []
        edges = cc.index_by_id(model["edges"])
        for item in learned:
            parts = item.split(":")
            level, ident = (parts[1], parts[-1]) if item.startswith("CART:") and len(parts) >= 3 else (None, item)
            if ident in edge_ids:
                _bump(states, ident, "CONNECTION_KNOWN")
                for end in (edges[ident].get("from"), edges[ident].get("to")):
                    _bump(states, end, "MENTIONED")
            elif ident in loc_ids:
                _bump(states, ident, LEVEL_TO_STATE.get(level, "MENTIONED"))
    for st in cc.as_list(stagings):
        if st.get("status") == "REALIZED" and st.get("pov") and st.get("location") in loc_ids \
                and (st.get("chapter") is None or st["chapter"] <= chapter):
            _bump(states, st["location"], "VISITED")
    counts = {s: 0 for s in READER_STATES}
    for lid in loc_ids | edge_ids:
        counts[states.get(lid, "UNSEEN")] += 1
    return {"view": "READER_PROJECTION", "chapter": chapter, "states": states, "counts": counts,
            "unseen": sorted((loc_ids | edge_ids) - set(states)),
            "baseline": {"printed_locations": len(printed["locations"]), "printed_edges": len(printed["edges"])},
            "notice": "Projeção do que o leitor viu. Sem estado físico, sem quem sabe o quê, sem verdade de mistério."}


def reader_knows_pov_does_not(model, actor, chapter, ledger=None):
    """Ironia dramática verificável: arestas que o leitor viu (impressas ou aprendidas) e o POV desconhece."""
    rm = reader_map(model, chapter, ledger)["states"]
    know = cg.Knowledge(model, actor, chapter, ledger)
    edges = cc.index_by_id(model["edges"])
    rows = []
    for eid, st in rm.items():
        e = edges.get(eid)
        if e is not None and st in ("SEEN_ON_MAP", "CONNECTION_KNOWN") and not know.knows_edge(e):
            rows.append({"edge": eid, "reader_state": st, "secret_level": e.get("secret_level"),
                         "note": "KN-01: o POV não pode usá-la enquanto não a conhecer."})
    return {"actor": actor, "chapter": chapter, "reader_knows_but_pov_does_not": rows}


def printed_divergences(model, chapter):
    """INFO: mutação faz um mapa impresso mentir (o leitor tem um mapa desatualizado)."""
    printed = printed_ids(model)["edges"]
    out = []
    for e in model["edges"]:
        if e["id"] in printed:
            now, then = cg.edge_state(model, e, chapter), cg.edge_state(model, e, 0)
            if now != then:
                out.append(_f("MUTATION_DIVERGES_FROM_PRINTED_MAP", "INFO", chapter, e["id"],
                              f"O mapa impresso mostra {then}; no capítulo {chapter} a aresta está {now}.",
                              "Legítimo: o leitor tem um mapa desatualizado (potencial de mistério)."))
    return out


def _mentions(prose_norm, name):
    n = cc.normalize_name(name)
    return len(n) >= 4 and re.search(rf"(?<![a-z0-9]){re.escape(n)}(?![a-z0-9])", prose_norm) is not None


def check_reader_leak(model, prose, chapter, ledger=None):
    """KN-02 READER_MAP_LEAK: a prosa revela, antes da hora, id que não está impresso nem foi aprendido pelo leitor."""
    printed = printed_ids(model)["locations"]
    seen = reader_map(model, chapter, ledger)["states"]
    text = cc.normalize_name(prose)
    out = []
    for loc in model["locations"]:
        lid = loc["id"]
        fr = loc.get("first_allowed_reveal")
        if lid in printed or not isinstance(fr, int) or fr <= chapter or seen.get(lid, "UNSEEN") != "UNSEEN":
            continue
        names = [loc.get("canonical_name")] + [n.get("name") for n in cc.as_list(loc.get("names"))]
        hit = next((n for n in names if n and _mentions(text, n)), None)
        if hit:
            out.append(_f("KN-02 READER_MAP_LEAK", "HIGH", chapter, f"{lid}: {hit!r}",
                          f"A prosa do capítulo {chapter} nomeia um lugar liberado só no capítulo {fr} e ausente dos mapas impressos.",
                          "Remover a menção, antecipar a revelação por proposta, ou dar ao leitor a fonte (knowledge_delta)."))
    return out


# ---------------------------------------------------------------------------
# mapas do mundo: relações com o físico (SDD 22.2)
# ---------------------------------------------------------------------------

def check_depictions(model):
    """MP-01..03: cada relação de `depicts` é verificada contra o grafo físico ou ancorada em truth_ref."""
    out = []
    ids = {item.get("id"): (k, item) for k, item in cc.all_id_carriers(model)}
    proj = cc.project_all(model)
    for art in model["artifacts"]:
        if art.get("kind") != "MAP":
            continue
        aid = art.get("id", "?")
        for d in cc.as_list(art.get("depicts")):
            rel, tgt = d.get("relation"), d.get("target")
            ev = f"{aid}: {tgt} {rel}"
            if rel not in DEPICTION_RELATIONS:
                out.append(_f("INVALID_ENUM", "HIGH", None, f"{aid}.depicts.relation={rel!r}", f"∈ {sorted(DEPICTION_RELATIONS)}.", "Corrigir."))
                continue
            if rel == "PHANTOM":
                if tgt in ids and not ids[tgt][1].get("valid_until"):
                    out.append(_f("MP-01 PHANTOM_EXISTS", "HIGH", None, ev, "PHANTOM descreve o que NÃO existe (mais); o alvo existe no grafo físico sem `valid_until`.",
                                  "Usar RENAMED/MISPLACED/ACCURATE, ou registrar valid_until."))
                continue
            if tgt not in ids:
                out.append(_f("CG-01 EDGE_DANGLING", "BLOCKER", None, ev, "O mapa descreve entidade inexistente no grafo físico.", "Corrigir."))
                continue
            kind, item = ids[tgt]
            if rel == "MISPLACED":
                pos, claimed = proj.get(tgt), d.get("as_position_px")
                scales = cc.source_scales(model)
                shown = cc.project_px(scales, art.get("source_file"), claimed) if claimed and art.get("source_file") else None
                if pos and shown:
                    dist = cc.euclid(pos, {"x": shown[0], "y": shown[1]})
                    acc = pos.get("accuracy_m", 60)
                    if dist <= acc:
                        out.append(_f("MP-02 MISPLACED_WITHIN_TOLERANCE", "MEDIUM", None, ev, f"Deslocamento {round(dist)} m ≤ precisão {round(acc)} m: não é erro do mapa.", "Usar ACCURATE."))
                        continue
                if not shown and not d.get("truth_ref"):
                    out.append(_f("MP-03 DEPICTION_WITHOUT_BASIS", "HIGH", None, ev, "MISPLACED sem posição desenhada verificável nem truth_ref.", "Informar as_position_px ou truth_ref."))
                continue
            if rel == "OMITS":
                continue
            if rel == "RENAMED":
                known = {cc.normalize_name(n.get("name")) for n in cc.as_list(item.get("names"))} | {cc.normalize_name(item.get("canonical_name"))}
                if cc.normalize_name(d.get("as_name")) not in known and not d.get("truth_ref"):
                    out.append(_f("MP-03 DEPICTION_WITHOUT_BASIS", "HIGH", None, ev, "RENAMED com nome que o canon não registra e sem truth_ref.", "Registrar o nome em names[] ou apontar truth_ref."))
                continue
            if rel in ("FALSIFIED_STATUS", "FALSIFIED_ACCESS") and not d.get("truth_ref"):
                out.append(_f("MP-03 DEPICTION_WITHOUT_BASIS", "HIGH", None, ev, f"{rel} é afirmação sobre a verdade e exige truth_ref.", "Apontar o GT no Story Truth Ledger."))
    return out


def check_layers(model):
    """Camadas RESERVED existem como id e não têm conteúdo; artefato só usa camada existente."""
    out = []
    layers = {l.get("id"): l for l in model["layers"]}
    for lid, l in layers.items():
        if l.get("status") == "RESERVED":
            extra = sorted(set(l) - RESERVED_LAYER_KEYS)
            if extra:
                out.append(_f("LY-01 RESERVED_LAYER_HAS_CONTENT", "HIGH", None, f"{lid}: {extra}", "Camada RESERVED não tem conteúdo; conteúdo só por proposta.", "Remover ou aprovar por proposta."))
    for a in model["artifacts"]:
        ml = a.get("map_layer")
        if ml and ml != "UNKNOWN" and ml not in layers:
            out.append(_f("CG-01 EDGE_DANGLING", "BLOCKER", None, f"{a.get('id')}.map_layer={ml}", "Camada inexistente.", "Corrigir."))
    return out


# ---------------------------------------------------------------------------
# autoria protegida no ledger (SDD 22.7, MY-08)
# ---------------------------------------------------------------------------

def check_author_protection(model, ledger):
    """MY-08: nenhum knowledge_delta ensina a autoria; PROVENANCE_INQUIRY produz evidência, jamais resolução."""
    out = []
    questions = {(a.get("author") or {}).get("question_ref") for a in model["artifacts"]
                 if a.get("kind") == "MAP" and isinstance(a.get("author"), dict)} - {None}
    answers = {gid for gid, gt in _ground_truths(ledger).items() if gt.get("answers") in questions or gt.get("question_ref") in questions}
    for ev in (ledger or {}).get("events") or []:
        eid = ev.get("id", "?")
        kinds = cc.as_list(ev.get("kind"))
        if "PROVENANCE_INQUIRY" in kinds and (ev.get("resolves") or ev.get("resolution")):
            out.append(_f("MY-08 MAP_AUTHOR_REVEALED", "BLOCKER", ev.get("chapter"), eid, "PROVENANCE_INQUIRY que resolve a autoria dos mapas.",
                          "A busca produz evidência (EVD-*), nunca resolução."))
        for kd in ev.get("knowledge_delta") or []:
            for item in cc.as_list(kd.get("learns")):
                if item in answers or str(item).startswith("CART:AUTHOR:"):
                    out.append(_f("MY-08 MAP_AUTHOR_REVEALED", "BLOCKER", ev.get("chapter"), f"{eid}: {kd.get('knower')} learns {item}",
                                  "Nenhum conhecedor (personagem ou READER) pode aprender quem fez os mapas.", "Remover o knowledge_delta."))
    return out


# ---------------------------------------------------------------------------
# crença por artefato (SDD 23.4)
# ---------------------------------------------------------------------------

def belief_view(model, artifact_id):
    art = cc.index_by_id(model["artifacts"]).get(artifact_id)
    if art is None:
        return None
    rel = {}
    for d in cc.as_list(art.get("depicts")):
        rel.setdefault(d.get("relation"), []).append(d.get("target"))
    return {"artifact": artifact_id, "believes_present_but_absent": sorted(rel.get("PHANTOM", [])),
            "omits": sorted(rel.get("OMITS", [])), "falsified": sorted(rel.get("FALSIFIED_STATUS", []) + rel.get("FALSIFIED_ACCESS", [])),
            "renamed": sorted(rel.get("RENAMED", [])), "misplaced": sorted(rel.get("MISPLACED", []))}


def check_planned_belief(model, artifact_id, planned_route, actual_route, chapter, evidence, seen_ok=True):
    """Planejar por um mapa falso é narrativa (INFO PLANNED_ON_FALSE_BELIEF); planejar por artefato que o ator nunca
    viu é KN-04; usar aresta que o artefato omite é outra informação, também INFO."""
    out = []
    view = belief_view(model, artifact_id)
    if view is None:
        return [_f("CG-01 EDGE_DANGLING", "BLOCKER", chapter, f"{evidence}: {artifact_id}", "planned_on aponta para artefato inexistente.", "Corrigir.")]
    if not seen_ok:
        out.append(_f("KN-04 BELIEF_ARTIFACT_NOT_SEEN", "HIGH", chapter, f"{evidence}: {artifact_id}",
                      "O ator planejou por um mapa que não viu.", "Registrar artifact_seen (ou CART:SEEN:<id> no ledger) antes."))
    edges = cc.index_by_id(model["edges"])
    for eid in cc.as_list(planned_route):
        e = edges.get(eid)
        if eid in view["believes_present_but_absent"] or eid in view["falsified"]:
            out.append(_f("PLANNED_ON_FALSE_BELIEF", "INFO", chapter, f"{evidence}: {eid}", f"O ator planejou por {artifact_id}, que descreve {eid} de forma falsa.",
                          "Legítimo: a personagem erra pelo mapa; a validação física continua valendo."))
        elif e is not None and cg.edge_state(model, e, chapter) in BLOCKED_STATES:
            out.append(_f("PLANNED_ON_FALSE_BELIEF", "INFO", chapter, f"{evidence}: {eid}", f"{eid} está {cg.edge_state(model, e, chapter)} no capítulo {chapter}; o mapa não sabe.",
                          "Legítimo: mapa desatualizado."))
    for eid in cc.as_list(actual_route):
        if eid in view["omits"] and eid not in cc.as_list(planned_route):
            out.append(_f("ROUTE_OMITTED_BY_BELIEF", "INFO", chapter, f"{evidence}: {eid}", f"{artifact_id} omite {eid}, mas a rota real a usa.",
                          "O ator sabe por outra fonte (KN-01 continua valendo)."))
    return out


def artifact_seen(mv, ledger, actor, chapter, artifact_id):
    for s in cc.as_list(mv.get("artifact_seen")):
        if s.get("artifact") == artifact_id and s.get("from_chapter", 0) <= (chapter if chapter is not None else 10 ** 9):
            return True
    if ledger and actor:
        try:
            import check_causal_ledger as cl
            return f"CART:SEEN:{artifact_id}" in cl.knowledge_state(ledger, actor, chapter)
        except Exception:  # noqa: BLE001
            return False
    return False


def validate_maps(model):
    """Regras estáticas do S4 (entram em `validate`)."""
    return check_depictions(model) + check_layers(model)
