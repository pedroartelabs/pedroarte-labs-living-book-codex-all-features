"""Gera REGIONAL.seed.yaml (vias do Mapa B) e liga as rotas e saídas regionais ao restante do canon.

Reprodutível: `python books/sem-rosto/cartography/digitization/build_regional_seed.py` (raiz do repositório).
Método (SDD 36.3, estendido no S6): as ligações entre vilarejos NÃO são adivinhadas à mão. Para cada par de nós a menos de
360 px o rastreador segue a via desenhada (modo `thin`: contraste local, porque as vias do Mapa B são finas e escuras);
foram aceitas só as ligações DIRETAS (o traçado não passa junto de outro nó), sobre via (>= 70 % dos pixels) e sem
sobreposição majoritária com ligações mais curtas. A tabela `PAIRS` abaixo é o resultado congelado dessa seleção;
`ROUTES_RED` e `EXIT_PATHS` são pontos-chave do operador. Painéis, título e legenda são bloqueados (`BLOCKS`).

Escala: 55,86 m/px (decisão OQ-CART-01: razão LINEAR, ainda a confirmar). O núcleo do Mapa B é ESQUEMÁTICO: lugares que
existem nos dois mapas entram aqui por nós-junção regionais ligados ao lugar urbano por `FRAME_LINK` de comprimento zero
(o lugar é o mesmo, a escala muda). Distâncias regionais têm precisão de centenas de metros (accuracy 840 m).

Confiança: PROBABLE = via nítida e direta (>= 85 % sobre via, desvio <= 1,5); UNCERTAIN = o resto. Nada CONFIRMED_VISUAL
até a conferência humana de `overlay_B.png`. Nada aqui decide segredo, estado além do desenhado ou significado de rota.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "engine" / "scripts"))
import trace_map_paths as tmp  # noqa: E402

PKG = ROOT / "books" / "sem-rosto" / "cartography"
SEEDS = PKG / "seeds"
IMG_B = PKG / "sources" / "MAP_B_redmur_arredores_map.png"
B = "SRC-MAP-B"
MPP_B = 55.86
BLOCKS = [[1190, 285, 1448, 1000], [30, 35, 490, 185], [95, 895, 870, 1075], [880, 975, 1190, 1075]]

# alias -> id de lugar existente (regional ou moldura)
REG = {
    "GLN": "RM-REG-GLN", "CRB": "RM-REG-CRB", "CRE": "RM-REG-CRE", "KRK": "RM-REG-KRK", "ELG": "RM-REG-ELG", "STW": "RM-REG-STW",
    "CRV": "RM-REG-CRV", "GRF": "RM-REG-GRF", "THB": "RM-REG-THB", "CRG": "RM-REG-CRG", "SBA": "RM-REG-SBA", "MCR": "RM-REG-MCR",
    "KLB": "RM-REG-KLB", "CRH": "RM-REG-CRH", "BTC": "RM-REG-BTC", "WLF": "RM-REG-WLF", "FSG": "RM-REG-FSG", "MSG": "RM-REG-MSG",
    "RVH": "RM-REG-RVH", "OML": "RM-REG-OML", "MFF": "RM-REG-MFF", "BRF": "RM-REG-BRF",
    "X_NE": "RM-FRM-B-NE", "X_W": "RM-FRM-B-W", "X_SW1": "RM-FRM-B-SW1", "X_SW2": "RM-FRM-B-SW2", "X_SE1": "RM-FRM-B-SE1",
    "X_SE2": "RM-FRM-B-SE2",
}
# nós-junção regionais para lugares que existem nos DOIS mapas: (alias, id, nome, px no Mapa B, lugar urbano ligado)
SEAMS = [
    ("H", "RM-JCT-B-RDM", "Redmur (núcleo esquemático no Mapa B)", (665, 535), "RM-CEN-SMC"),
    ("OQY", "RM-JCT-B-OQY", "Old Quarry (no Mapa B)", (580, 425), "RM-URB-OQY"),
    ("FLE", "RM-JCT-B-FLE", "Flarry Estate (no Mapa B)", (485, 290), "RM-URB-FLE"),
    ("SBO", "RM-JCT-B-SBO", "Shepherd's Bothy (no Mapa B)", (690, 310), "RM-URB-SBO"),
    ("MNF", "RM-JCT-B-MNF", "Manfred Farm (no Mapa B)", (800, 405), "RM-URB-MNF"),
    ("ROW", "RM-JCT-B-ROW", "Rowan Cottage (no Mapa B)", (1050, 345), "RM-URB-ROW"),
    ("BBR", "RM-JCT-B-BBR", "Burn Bridge (no Mapa B)", (985, 512), "RM-URB-BBR"),
    ("ERC", "RM-JCT-B-ERC", "East Road, ponto de bloqueio (no Mapa B)", (1037, 538), "RM-URB-ERC"),
    ("PMP", "RM-JCT-B-PMP", "Pumping Station (no Mapa B)", (1080, 487), "RM-URB-PMP"),
    ("CHP", "RM-JCT-B-CHP", "Saint Morrow Chapel (no Mapa B)", (518, 457), "RM-CEN-CHP"),
    ("OPC", "RM-JCT-B-OPC", "Old Parish Cemetery (no Mapa B)", (505, 525), "RM-URB-OPC"),
    ("S1", "RM-JCT-B-SGR", "South Gate Road: saída do núcleo (no Mapa B)", (690, 650), "RM-FRM-A-S"),
]
PX = {"GLN": (855, 190), "CRB": (553, 230), "CRE": (400, 355), "KRK": (140, 445), "ELG": (110, 540), "STW": (340, 695),
      "CRV": (470, 640), "GRF": (555, 835), "THB": (262, 830), "CRG": (170, 640), "SBA": (245, 620), "MCR": (355, 265),
      "KLB": (1115, 170), "CRH": (850, 640), "BTC": (960, 570), "WLF": (1020, 700), "FSG": (1115, 625), "MSG": (1030, 825),
      "RVH": (850, 855), "OML": (722, 790), "MFF": (268, 480), "BRF": (265, 400),
      "X_NE": (1375, 222), "X_W": (48, 680), "X_SW1": (160, 810), "X_SW2": (243, 875), "X_SE1": (1147, 870), "X_SE2": (1133, 955)}
PX.update({a: px for a, _, _, px, _ in SEAMS})
ID = {**REG, **{a: i for a, i, _, _, _ in SEAMS}}

# ligações diretas aceitas na seleção automática (pares congelados)
PAIRS = """BBR-BTC BBR-ERC BBR-S1 BTC-FSG CHP-OPC CRB-GLN CRE-BRF CRE-CHP CRE-MCR CRG-MFF CRH-BTC CRV-OPC CRV-STW ELG-MFF
ELG-X_SW1 ERC-PMP FLE-CRB FLE-CRE FLE-SBO GLN-KLB GRF-THB H-MNF H-S1 KRK-MFF KRK-X_W MFF-CHP MNF-BBR MNF-ROW MNF-SBO
OML-GRF OQY-CHP OQY-S1 OQY-SBO RVH-MSG S1-GRF S1-OPC S1-RVH SBO-CRB STW-SBA WLF-CRH WLF-FSG
""".split()
# saídas e ligações especificadas pelo operador: (par, waypoints intermediários, papel)
EXIT_PATHS = [
    ("ROW-X_NE", [], "EXT-03"),                                 # Estrada 13 (linha branca tracejada)
    ("KLB-X_NE", [], "EXT-10"),                                 # via NE com trechos vermelhos (estrada bloqueada)
    ("MSG-X_SE2", [(1005, 880), (1040, 935)], "EXT-08"),        # via sul de Mossgate (trecho vermelho no fim)
    ("MSG-X_SE1", [], "EXT-07"),                                # R13: "Para Eldham (41 milhas)"
    ("THB-X_SW2", [], "EXT-06"),                                # "Para Inverloch (?7 milhas)"
    ("THB-X_SW1", [], "EXT-05"),                                # "Para Westhaven (29 milhas)", margem do Loch Calder
    ("CRG-X_W", [], "EXT-04"),                                  # trilha oeste, "Para Dunsgate (17 milhas)"
]
# linhas de rota contestadas (modo red): (id de rota, [pontos-chave]) — só o trecho DESENHADO
ROUTES_RED = [
    ("RTE-B-R3-STR", [(710, 301), (1017, 326)]),
    ("RTE-B-R3-GLN", [(774, 221), (795, 154)]),
    ("RTE-B-QM", [(619, 440), (731, 428)]),
    ("RTE-B-CHP", [(536, 513), (588, 531)]),
    ("RTE-B-R17", [(380, 785), (616, 726)]),
]
NEIGHBOUR_MAX_ON_ROAD_DROP = 0.70
# Ash Burn no Mapa B (curso lido em recorte ampliado; o rastreador `water` refina)
WATER_B = [(930, 378), (951, 396), (977, 408), (986, 428), (1004, 443), (1027, 452), (1033, 464), (1009, 478), (983, 487),
           (978, 499), (983, 511), (992, 528), (1004, 546), (1033, 564), (1062, 578), (1104, 590), (1145, 596)]


def polyline_len_px(pts):
    return sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:]))


def main():
    specs = []
    for pair in PAIRS:
        a, b = pair.split("-", 1)
        specs.append({"id": pair, "via": [list(PX[a]), list(PX[b])], "mode": "thin", "snap": 10, "margin": 90})
    for pair, wps, role in EXIT_PATHS:
        a, b = pair.split("-", 1)
        specs.append({"id": pair, "via": [list(PX[a])] + [list(w) for w in wps] + [list(PX[b])], "mode": "thin", "snap": 10, "margin": 90})
    traced = {t["id"]: t for t in tmp.trace(IMG_B, specs, blocks=BLOCKS)}
    red = {t["id"]: t for t in tmp.trace(IMG_B, [{"id": rid, "mode": "red", "tol": 2.0, "margin": 40, "via": [list(p) for p in pts]}
                                                for rid, pts in ROUTES_RED])}
    river = tmp.trace(IMG_B, [{"id": "WAT-ASH-B", "mode": "water", "tol": 2.5, "margin": 25, "via": [list(p) for p in WATER_B]}])[0]
    bad = [k for k, v in {**traced, **red}.items() if not v.get("points")] + ([] if river.get("points") else ["WAT-ASH-B"])
    if bad:
        raise SystemExit(f"sem caminho: {bad}")
    (PKG / "digitization" / "paths_B.spec.yaml").write_text(
        "# GERADO por build_regional_seed.py — não editar à mão. Pontos-chave (pixels do Mapa B) de cada via.\n"
        + yaml.safe_dump({"paths": specs + [{"id": r, "mode": "red", "via": [list(p) for p in pts]} for r, pts in ROUTES_RED]},
                         allow_unicode=True, sort_keys=False, default_flow_style=None, width=160), encoding="utf-8")

    locations = [{"id": i, "canonical_name": n, "type": ["JUNCTION", "BRIDGE"] if i == "RM-JCT-B-BBR" else "JUNCTION", "layer": "REGIONAL", "geometry": "POINT",
                  "source_px": [{"source": B, "px": list(px), "anchor": "ICON"}],
                  **({"crosses": ["WAT-ASH"]} if i == "RM-JCT-B-BBR" else {}),
                  "note": "nó-junção do Mapa B; o lugar urbano correspondente é ligado por FRAME_LINK de comprimento zero (mesmo lugar, escala diferente)"}
                 for a, i, n, px, _ in SEAMS]

    edges, n = [], 0

    def reg_edge(pair, tr, klass="ROAD", note=None, route=None):
        nonlocal n
        n += 1
        a, b = pair.split("-", 1)
        pts = tr["points"]
        conf = "PROBABLE" if tr["road_fraction"] >= 0.85 and tr["detour_ratio"] <= 1.5 else "UNCERTAIN"
        e = {"id": f"EDG-R-{n:03d}", "from": ID[a], "to": ID[b], "edge_type": klass, "road_class": "UNCLASSIFIED",
             "directionality": "BOTH", "source_polyline_px": {"source": B, "points": pts},
             "distance_meters": {"nominal": round(polyline_len_px(pts) * MPP_B), "min": round(0.9 * polyline_len_px(pts) * MPP_B),
                                 "basis": "DIGITIZED_SCHEMATIC"},
             "terrain": "TRACK", "visibility": "OPEN", "public_knowledge": "PUBLIC", "secret_level": "NONE",
             "canon_status": "CANONICAL", "confidence": conf,
             "digitization": {"road_fraction": tr["road_fraction"], "detour_ratio": tr["detour_ratio"]},
             "state_timeline": [{"from_chapter": 0, "state": "OPEN"}]}
        if note:
            e["note"] = note
        return e

    roles = {pair: role for pair, _, role in EXIT_PATHS}
    for pair in PAIRS:
        tr = traced[pair]
        if tr["road_fraction"] < NEIGHBOUR_MAX_ON_ROAD_DROP:
            continue
        edges.append(reg_edge(pair, tr))
    exit_edge = {}
    for pair, _, role in EXIT_PATHS:
        e = reg_edge(pair, traced[pair], note=f"via de saída ({role}); a moldura do Mapa B termina a via, o que há além é OFF_MAP")
        e["confidence"] = "UNCERTAIN"
        edges.append(e)
        exit_edge[role] = e["id"]
    # linhas de rota contestadas (só o trecho desenhado); não têm extremos em lugares: pontas soltas nomeadas
    route_edge = {}
    for rid, pts in ROUTES_RED:
        tr = red[rid]
        a, b = (f"RM-JCT-B-{rid.split('-', 2)[2]}-A", f"RM-JCT-B-{rid.split('-', 2)[2]}-B")
        for jid, p in ((a, tr["points"][0]), (b, tr["points"][-1])):
            locations.append({"id": jid, "canonical_name": f"ponta {'inicial' if jid == a else 'final'} desenhada da rota {rid} (Mapa B)", "type": "JUNCTION", "layer": "REGIONAL",
                              "geometry": "POINT", "source_px": [{"source": B, "px": list(p), "anchor": "ICON"}],
                              "note": "ponta do trecho vermelho desenhado; a continuação é UNKNOWN"})
        n += 1
        length = polyline_len_px(tr["points"])
        route_edge[rid] = f"EDG-R-{n:03d}"
        edges.append({"id": route_edge[rid], "from": a, "to": b, "edge_type": "TRAIL", "road_class": "CONTESTED",
                      "directionality": "BOTH", "source_polyline_px": {"source": B, "points": tr["points"]},
                      "distance_meters": {"nominal": round(length * MPP_B), "min": round(0.9 * length * MPP_B), "basis": "DIGITIZED_SCHEMATIC"},
                      "terrain": "TRACK", "visibility": "OPEN", "public_knowledge": "PUBLIC", "secret_level": "NONE",
                      "canon_status": "CANONICAL", "confidence": "UNCERTAIN", "route_membership": [rid],
                      "legend_class": "CONTESTED_ROUTE", "state_timeline": [{"from_chapter": 0, "state": "OPEN"}],
                      "note": f"traçado da linha vermelha {rid} (rota do mapa); o desenho é o único fato, a continuação é UNKNOWN"})
    # ligações de escala: mesmo lugar nos dois mapas (comprimento zero)
    k = 0
    for a, i, _, _, urban in SEAMS:
        k += 1
        edges.append({"id": f"EDG-L-{k:03d}", "from": i, "to": urban, "edge_type": "FRAME_LINK", "directionality": "BOTH",
                      "distance_meters": {"nominal": 0, "min": 0, "basis": "SCALE_TRANSITION"},
                      "visibility": "OPEN", "public_knowledge": "PUBLIC", "secret_level": "NONE", "canon_status": "CANONICAL",
                      "confidence": "UNCERTAIN", "state_timeline": [{"from_chapter": 0, "state": "OPEN"}],
                      "note": "identidade entre escalas (o lugar é o mesmo); o núcleo do Mapa B é esquemático (SDD 7.4)"})
    k += 1
    edges.append({"id": f"EDG-L-{k:03d}", "from": "RM-REG-RDM", "to": "RM-JCT-B-RDM", "edge_type": "FRAME_LINK", "directionality": "BOTH",
                  "distance_meters": {"nominal": 0, "min": 0, "basis": "SCALE_TRANSITION"}, "visibility": "OPEN", "public_knowledge": "PUBLIC",
                  "secret_level": "NONE", "canon_status": "CANONICAL", "confidence": "UNCERTAIN",
                  "state_timeline": [{"from_chapter": 0, "state": "OPEN"}], "note": "Redmur (verbete do registro) = núcleo do Mapa B"})

    def patch(name, fn):
        path = SEEDS / name
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        fn(data)
        head = "".join(line for line in text.splitlines(keepends=True) if line.startswith("#"))
        path.write_text(head + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=None, width=140), encoding="utf-8")

    def routes(d):
        for r in d["routes"]:
            if r["id"] in route_edge:
                r["edges"] = [route_edge[r["id"]]]
                r["trace_status"] = "DIGITIZED"
                r["continuation_beyond_drawn"] = "UNKNOWN"

    def exits(d):
        for x in d["exits"]:
            eid = exit_edge.get(x["id"])
            if eid:
                x["edges"] = [eid]
                if x.get("frame_status") == "TO_DIGITIZE":
                    x.pop("frame_status")
                if x["id"] == "EXT-10":
                    x["frame_portal"] = "RM-FRM-B-NE"
                    x["note"] = "As linhas vermelhas desta via chegam à moldura NE junto da Estrada 13 (EXT-03): mesmo portal de moldura, duas vias desenhadas."
            elif x["id"] == "EXT-09":
                x["edges"] = [route_edge["RTE-B-R3-GLN"]]
                x["frame_status"] = "ENDS_BEFORE_FRAME"
                x["note"] = "A linha vermelha R3 sobe a cordilheira e termina desenhada antes da moldura; a continuação é UNKNOWN."
            elif x["id"] == "EXT-02":
                x["frame_status"] = "ENDS_BEFORE_FRAME"
                x["note"] = "No Mapa B a East Road termina na zona restrita (X); não há via desenhada além dela."
    def water(d):
        for l in d["locations"]:
            if l["id"] == "WAT-ASH":
                l["polyline_px"] = [p for p in l["polyline_px"] if p.get("source") != B] + [{"source": B, "px": p} for p in river["points"]]
    patch("LOCATIONS.seed.yaml", water)
    patch("ROUTES.seed.yaml", routes)
    patch("BOUNDARIES.seed.yaml", exits)

    road_of = {"EXT-03": "ROAD-E13", "EXT-04": "ROAD-B-W", "EXT-05": "ROAD-B-SW1", "EXT-06": "ROAD-B-SW2", "EXT-07": "ROAD-B-R13",
               "EXT-08": "ROAD-B-SE2", "EXT-10": "ROAD-B-KEL"}
    by_id = {e["id"]: e for e in edges}
    for role, road in road_of.items():
        if role in exit_edge:
            by_id[exit_edge[role]]["road"] = road
    by_id[route_edge["RTE-B-R3-GLN"]]["road"] = "ROAD-B-R3N"

    header = ("Vias do Mapa B (regional, Slice 6). GERADO por books/sem-rosto/cartography/digitization/build_regional_seed.py.\n"
              "Polilinhas em pixels da fonte (55,86 m/px, linear, a confirmar). Núcleo esquemático; confiança PROBABLE/UNCERTAIN até a conferência humana.")
    (SEEDS / "REGIONAL.seed.yaml").write_text("# " + header.replace("\n", "\n# ") + "\n" + yaml.safe_dump(
        {"locations": locations, "edges": edges}, allow_unicode=True, sort_keys=False, default_flow_style=None, width=140), encoding="utf-8")

    def roads(d):
        for road in d["roads"]:
            regional = [e["id"] for e in edges if e.get("road") == road["id"]]
            if regional:
                road["edges"] = regional
    patch("EDGES.seed.yaml", roads)

    def manifest(d):
        if "REGIONAL" not in d["includes"]:
            d["includes"].insert(d["includes"].index("SURFACE") + 1, "REGIONAL")
        d["metadata"]["edges_digitized"] = {"URBAN": True, "SUBTERRANEAN": True, "REGIONAL": True}
    patch("CARTOGRAPHY.seed.yaml", manifest)
    print(f"{len(edges)} arestas regionais e de ligação; {len(locations)} nós; exits: {exit_edge}")


if __name__ == "__main__":
    main()
