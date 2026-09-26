"""Gera SURFACE.seed.yaml (vias de superfície do Mapa A) a partir da tabela de pontos-chave abaixo.

Reprodutível: `python books/sem-rosto/cartography/digitization/build_surface_seed.py` (na raiz do repositório).
O operador edita SÓ esta tabela (lugares/cruzamentos em pixels); o rastreador
(engine/scripts/trace_map_paths.py) segue a via desenhada; um humano confere a sobreposição
(`--overlay`) antes de a aresta ser tratada como CANONICAL (SDD 36.3).

Confiança: PROBABLE = via nítida no mapa; UNCERTAIN = ligação plausível mas não inequívoca (ex.: portão de cemitério).
Nada aqui decide segredo, estado além do desenhado ou significado de rota.
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
IMG_A = PKG / "sources" / "MAP_A_redmur_map.png"
A = "SRC-MAP-A"
MPP_A = 4.05

# ---- cruzamentos e pontas soltas (id, nome, px) -----------------------------
JUNCTIONS = [
    ("RM-JCT-U01", "cruzamento South Gate Road / vias do oeste", (552, 830)),
    ("RM-JCT-U02", "South Gate Road: ramal do Constabulary e do Old Coach Stop", (565, 655)),
    ("RM-JCT-U03", "rua leste: junção do Village Clinic", (700, 556)),
    ("RM-JCT-U04", "South Gate Road: ramal do Ruined Tool Shed", (563, 800)),
    ("RM-JCT-U05", "junção norte (via de Manfred Farm e via leste)", (650, 447)),
    ("RM-JCT-U06", "junção do General Mercantile", (700, 455)),
    ("RM-JCT-U07", "junção leste (via de Burn Bridge)", (790, 472)),
    ("RM-JCT-U08", "junção de Manfred Farm (via norte e R3)", (715, 300)),
    ("RM-JCT-U09", "via oeste: junção do cemitério e da trilha sul", (250, 652)),
    ("RM-JCT-U10", "trilha sudoeste: junção norte", (245, 705)),
    ("RM-JCT-U11", "trilha sudoeste: junção de Caretaker House", (300, 752)),
    ("RM-JCT-U12", "via noroeste: junção de Flarry Estate", (335, 285)),
    ("RM-JCT-U13", "via leste de Manfred Farm: bifurcação", (880, 325)),
    ("RM-JCT-U14", "via leste: junção da via de Manfred Farm", (855, 480)),
    ("RM-JCT-U15", "rua leste: ponta desenhada (a via segue além do trecho digitalizado)", (900, 585)),
    ("RM-JCT-U16", "R1: ponta desenhada a leste (fim da linha vermelha)", (430, 505)),
    ("RM-JCT-U17", "rua leste: junção do Redmur Constabulary", (610, 556)),
    ("RM-JCT-U18", "via da capela ao centro: ponto onde a R1 desemboca (conexão inferida)", (440, 480)),
    ("RM-FRM-A-N1", "via noroeste: ponta desenhada ao norte (sai da área detalhada)", (525, 125)),
]
FRAME_TYPES = {"RM-FRM-A-N1": "FRAME_PORTAL"}

# ---- arestas: (id, de, para, tipo, classe, via, waypoints, confiança, extras) --
S, P, T, PA = "SECONDARY", "MAIN", "TRAIL", "PATH"
EDGES = [
    ("EDG-U-001", "RM-CEN-SMC", "RM-JCT-U02", "ROAD", P, "ROAD-SGR", [(521, 545), (566, 655)], "PROBABLE", {}),
    ("EDG-U-002", "RM-JCT-U02", "RM-JCT-U04", "ROAD", P, "ROAD-SGR", [(566, 655), (563, 800)], "PROBABLE", {}),
    ("EDG-U-003", "RM-JCT-U04", "RM-JCT-U01", "ROAD", P, "ROAD-SGR", [(563, 800), (552, 830)], "PROBABLE", {}),
    ("EDG-U-004", "RM-JCT-U01", "RM-FRM-A-S", "ROAD", P, "ROAD-SGR", [(552, 830), (583, 985)], "PROBABLE", {}),
    ("EDG-U-005", "RM-URB-DCU", "RM-JCT-U01", "TRAIL", T, None, [(358, 885), (475, 822), (548, 832)], "PROBABLE", {}),
    ("EDG-U-006", "RM-JCT-U11", "RM-JCT-U01", "TRAIL", T, None, [(300, 752), (440, 800), (548, 832)], "PROBABLE", {}),
    ("EDG-U-007", "RM-JCT-U11", "RM-URB-CTH", "TRAIL", PA, None, [(300, 752), (330, 790)], "PROBABLE", {}),
    ("EDG-U-008", "RM-JCT-U10", "RM-JCT-U11", "TRAIL", T, None, [(245, 705), (300, 752)], "PROBABLE", {}),
    ("EDG-U-009", "RM-URB-RCH", "RM-JCT-U10", "TRAIL", T, None, [(205, 860), (196, 800), (245, 705)], "PROBABLE", {}),
    ("EDG-U-010", "RM-URB-RCH", "RM-URB-DCU", "TRAIL", T, None, [(205, 865), (300, 905), (358, 885)], "PROBABLE", {}),
    ("EDG-U-011", "RM-JCT-U09", "RM-JCT-U10", "TRAIL", T, None, [(250, 652), (245, 705)], "PROBABLE", {}),
    ("EDG-U-012", "RM-JCT-U09", "RM-CEN-SMC", "ROAD", S, None,
     [(250, 652), (380, 680), (470, 665), (505, 640), (515, 570), (521, 545)], "PROBABLE", {}),
    ("EDG-U-013", "RM-JCT-U09", "RM-CEN-CHP", "TRAIL", T, None,
     [(250, 652), (180, 615), (140, 600), (95, 560), (80, 480), (90, 420), (160, 390), (220, 385), (300, 395), (318, 410)],
     "PROBABLE", {"note": "anel externo que contorna o Old Parish Cemetery"}),
    ("EDG-U-014", "RM-URB-OPC", "RM-JCT-U09", "TRAIL", T, None, [(185, 495), (240, 548), (250, 600), (250, 652)], "UNCERTAIN",
     {"note": "acesso ao cemitério: portão não desenhado com clareza"}),
    ("EDG-U-015", "RM-CEN-CHP", "RM-JCT-U18", "ROAD", S, None, [(318, 410), (380, 450), (440, 480)], "PROBABLE", {}),
    ("EDG-U-045", "RM-JCT-U18", "RM-CEN-SMC", "ROAD", S, None, [(440, 480), (470, 495), (521, 527)], "PROBABLE", {}),
    ("EDG-U-046", "RM-JCT-U16", "RM-JCT-U18", "OPEN_GROUND", PA, None, [(430, 505), (440, 480)], "UNCERTAIN",
     {"printed": False, "note": "CONEXÃO INFERIDA: a linha vermelha R1 termina entre casas a ~110 m desta via; o mapa não desenha a ligação. "
              "Sem ela o cemitério ficaria a 2,9 km do Red Stag Pub (1,5 km em linha reta)."}),
    ("EDG-U-016", "RM-CEN-OCP", "RM-CEN-SMC", "ROAD", S, None, [(355, 540), (430, 555), (521, 540)], "PROBABLE", {}),
    ("EDG-U-017", "RM-CEN-CAH", "RM-CEN-SMC", "ROAD", S, None, [(400, 605), (470, 600), (515, 560)], "UNCERTAIN", {}),
    ("EDG-U-018", "RM-CEN-SMC", "RM-CEN-RSP", "ROAD", S, None, [(521, 527), (548, 480)], "PROBABLE", {}),
    ("EDG-U-019", "RM-CEN-SMC", "RM-JCT-U05", "ROAD", S, None, [(521, 530), (565, 520), (625, 500), (650, 447)], "PROBABLE", {}),
    ("EDG-U-020", "RM-JCT-U05", "RM-JCT-U06", "ROAD", S, None, [(650, 447), (700, 455)], "PROBABLE", {}),
    ("EDG-U-021", "RM-JCT-U06", "RM-JCT-U07", "ROAD", S, None, [(700, 455), (750, 460), (790, 472)], "PROBABLE", {}),
    ("EDG-U-022", "RM-JCT-U07", "RM-JCT-U14", "ROAD", P, "ROAD-EAST", [(790, 472), (855, 480)], "PROBABLE", {}),
    ("EDG-U-023", "RM-JCT-U14", "RM-URB-BBR", "ROAD", P, "ROAD-EAST", [(855, 480), (925, 475), (1050, 500), (1150, 492)], "PROBABLE", {}),
    ("EDG-U-024", "RM-CEN-GMC", "RM-JCT-U06", "ROAD", PA, None, [(700, 478), (700, 455)], "PROBABLE", {}),
    ("EDG-U-025", "RM-JCT-U05", "RM-JCT-U08", "ROAD", S, None, [(650, 447), (680, 410), (700, 360), (715, 300)], "PROBABLE", {}),
    ("EDG-U-026", "RM-JCT-U08", "RM-URB-SBO", "ROAD", S, None, [(715, 300), (700, 220), (690, 170), (640, 140)], "PROBABLE", {}),
    ("EDG-U-027", "RM-JCT-U08", "RM-URB-MNF", "ROAD", PA, None, [(715, 300), (790, 295)], "PROBABLE", {}),
    ("EDG-U-028", "RM-CEN-SMC", "RM-JCT-U17", "ROAD", S, None, [(521, 545), (600, 555), (610, 556)], "PROBABLE", {}),
    ("EDG-U-043", "RM-JCT-U17", "RM-JCT-U03", "ROAD", S, None, [(610, 556), (700, 556)], "PROBABLE", {}),
    ("EDG-U-044", "RM-CEN-CON", "RM-JCT-U17", "ROAD", PA, None, [(615, 590), (610, 558)], "PROBABLE", {}),
    ("EDG-U-029", "RM-JCT-U03", "RM-CEN-CLN", "ROAD", PA, None, [(700, 556), (720, 600), (735, 622)], "PROBABLE", {}),
    ("EDG-U-030", "RM-JCT-U03", "RM-JCT-U02", "ROAD", S, None, [(700, 556), (700, 600), (650, 640), (590, 650), (565, 655)], "PROBABLE",
     {"note": "laço ao redor do Redmur Constabulary"}),
    ("EDG-U-031", "RM-JCT-U02", "RM-CEN-OCS", "ROAD", PA, None, [(590, 660), (640, 680)], "PROBABLE", {}),
    ("EDG-U-032", "RM-JCT-U04", "RM-URB-RTS", "TRAIL", T, None, [(563, 800), (640, 850), (735, 870)], "PROBABLE", {}),
    ("EDG-U-033", "RM-URB-BBR", "RM-URB-PMP", "TRAIL", S, None, [(1150, 492), (1200, 470), (1255, 440)], "PROBABLE", {}),
    ("EDG-U-034", "RM-URB-PMP", "RM-URB-RSV", "TRAIL", PA, None, [(1255, 425), (1270, 390)], "PROBABLE", {}),
    ("EDG-U-035", "RM-URB-BBR", "RM-URB-ERC", "ROAD", P, "ROAD-EAST", [(1150, 492), (1210, 500), (1280, 507)], "PROBABLE",
     {"state": "RESTRICTED", "government_control": {"claim": "Officially Closed", "source": "MAP-A-LBL-EASTROAD",
                                                    "epistemic_status": "OFFICIAL_CLAIM"},
      "note": "barreira física no X; o fechamento é alegação do artefato"}),
    ("EDG-U-036", "RM-CEN-CHP", "RM-JCT-U12", "ROAD", S, None, [(318, 410), (345, 380), (340, 330), (335, 285)], "PROBABLE", {}),
    ("EDG-U-037", "RM-JCT-U12", "RM-URB-FLE", "ROAD", PA, None, [(335, 285), (300, 262), (270, 245)], "PROBABLE", {}),
    ("EDG-U-038", "RM-JCT-U12", "RM-FRM-A-N1", "ROAD", S, None, [(335, 285), (370, 265), (430, 235), (490, 195), (525, 125)], "PROBABLE", {}),
    ("EDG-U-039", "RM-URB-MNF", "RM-JCT-U13", "ROAD", PA, None, [(790, 295), (870, 325), (880, 325)], "UNCERTAIN", {}),
    ("EDG-U-040", "RM-JCT-U13", "RM-JCT-U14", "ROAD", S, None, [(880, 325), (880, 390), (860, 470), (855, 480)], "UNCERTAIN", {}),
    ("EDG-U-041", "RM-JCT-U13", "RM-URB-BBR", "ROAD", S, None,
     [(880, 325), (950, 322), (1005, 355), (1100, 415), (1140, 470), (1150, 492)], "UNCERTAIN",
     {"note": "margem oeste do Ash Burn até a ponte"}),
    ("EDG-U-042", "RM-JCT-U03", "RM-JCT-U15", "ROAD", S, None, [(700, 556), (757, 545), (830, 555), (900, 585)], "UNCERTAIN", {}),
]
# rotas desenhadas (linhas vermelhas): (id da aresta, de, para, rota, waypoints)
ROUTE_EDGES = [
    ("EDG-U-R1", "RM-URB-OPC", "RM-JCT-U16", "RTE-A-R1", [(215, 462), (300, 500), (370, 508), (430, 505)]),
    ("EDG-U-R2", "RM-URB-SBO", "RM-URB-ROW", "RTE-A-R2", [(648, 133), (740, 150), (880, 200), (1000, 205), (1075, 190), (1085, 222)]),
    ("EDG-U-R3", "RM-URB-OQY", "RM-JCT-U08", "RTE-A-R3", [(470, 340), (550, 315), (625, 320), (715, 302)]),
]
WATER = ("WAT-ASH", [(975, 245), (1015, 285), (1065, 305), (1120, 345), (1150, 370), (1190, 400), (1200, 425), (1190, 450),
                     (1160, 472), (1152, 490), (1140, 520), (1170, 545), (1210, 570)])


def spec_entries():
    out = [{"id": e[0], "via": [list(p) for p in e[6]]} for e in EDGES]
    out += [{"id": r[0], "mode": "red", "tol": 2.0, "via": [list(p) for p in r[4]]} for r in ROUTE_EDGES]
    out.append({"id": WATER[0], "mode": "water", "tol": 3.0, "margin": 30, "via": [list(p) for p in WATER[1]]})
    return out


def main():
    specs = spec_entries()
    (PKG / "digitization" / "paths_A.spec.yaml").write_text(
        "# GERADO por build_surface_seed.py — não editar à mão. Pontos-chave (pixels do Mapa A) de cada via.\n"
        + yaml.safe_dump({"paths": specs}, allow_unicode=True, sort_keys=False, default_flow_style=None, width=160), encoding="utf-8")
    traced = {t["id"]: t for t in tmp.trace(IMG_A, specs)}
    bad = [k for k, v in traced.items() if not v.get("points")]
    if bad:
        raise SystemExit(f"sem caminho: {bad}")

    locations = []
    for jid, name, px in JUNCTIONS:
        locations.append({"id": jid, "canonical_name": name, "type": FRAME_TYPES.get(jid, "JUNCTION"), "layer": "URBAN",
                          "geometry": "POINT", "source_px": [{"source": A, "px": list(px), "anchor": "EDGE" if jid in FRAME_TYPES else "ICON"}],
                          "note": "cruzamento/ponta de via digitalizado; não é lugar canônico nomeável"})

    def edge(eid, a, b, typ, klass, road, pts, conf, extra):
        length_m = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:])) * MPP_A
        e = {"id": eid, "from": a, "to": b, "edge_type": typ, "road_class": klass if klass != "PATH" else "PATH",
             "directionality": "BOTH", "source_polyline_px": {"source": A, "points": pts},
             "distance_meters": {"nominal": round(length_m), "basis": "DIGITIZED"},
             "terrain": "ROAD_SURFACE" if klass in ("MAIN", "SECONDARY") else "TRACK",
             "visibility": "OPEN", "public_knowledge": "PUBLIC", "secret_level": "NONE", "canon_status": "CANONICAL",
             "confidence": conf, "state_timeline": [{"from_chapter": 0, "state": extra.get("state", "OPEN")}]}
        if road:
            e["road"] = road
        for k in ("note", "government_control", "printed"):
            if k in extra:
                e[k] = extra[k]
        return e

    edges = []
    for eid, a, b, typ, klass, road, wp, conf, extra in EDGES:
        edges.append(edge(eid, a, b, typ, klass, road, traced[eid]["points"], conf, extra))
    for eid, a, b, rte, wp in ROUTE_EDGES:
        e = edge(eid, a, b, "TRAIL", "TRAIL", None, traced[eid]["points"], "PROBABLE",
                 {"note": f"traçado da linha vermelha {rte} (rota do mapa); o desenho é o único fato, a continuação é UNKNOWN"})
        e["route_membership"] = [rte]
        e["legend_class"] = "ESCAPE_ROUTE"
        edges.append(e)
    header = ("Vias de superfície do Mapa A (Slice 2). GERADO por books/sem-rosto/cartography/digitization/build_surface_seed.py.\n"
              "Polilinhas em pixels da fonte; metros derivam de source_px × escala. Confiança PROBABLE/UNCERTAIN até a conferência humana.")
    (SEEDS / "SURFACE.seed.yaml").write_text("# " + header.replace("\n", "\n# ") + "\n" + yaml.safe_dump(
        {"locations": locations, "edges": edges}, allow_unicode=True, sort_keys=False, default_flow_style=None, width=140), encoding="utf-8")

    # Ash Burn: curso rastreado (substitui a linha grosseira de 3 pontos)
    lp = SEEDS / "LOCATIONS.seed.yaml"
    text = lp.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    for l in data["locations"]:
        if l["id"] == "WAT-ASH":
            l["polyline_px"] = [{"source": A, "px": p} for p in traced["WAT-ASH"]["points"]]
            l.pop("note", None)
            l["note"] = "Curso rastreado sobre a imagem; nascente e continuação além do bosque desconhecidas (ANM-A-04)."
    head = "".join(line for line in text.splitlines(keepends=True) if line.startswith("#"))
    lp.write_text(head + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=None, width=140), encoding="utf-8")

    # rotas: agora apontam para arestas
    rp = SEEDS / "ROUTES.seed.yaml"
    rtext = rp.read_text(encoding="utf-8")
    rdata = yaml.safe_load(rtext)
    by_route = {r[3]: r[0] for r in ROUTE_EDGES}
    for r in rdata["routes"]:
        if r["id"] in by_route:
            r["edges"] = [by_route[r["id"]]]
            r["trace_status"] = "DIGITIZED"
    rhead = "".join(line for line in rtext.splitlines(keepends=True) if line.startswith("#"))
    rp.write_text(rhead + yaml.safe_dump(rdata, allow_unicode=True, sort_keys=False, default_flow_style=None, width=140), encoding="utf-8")

    # vias nomeadas: lista de arestas
    ep = SEEDS / "EDGES.seed.yaml"
    etext = ep.read_text(encoding="utf-8")
    edata = yaml.safe_load(etext)
    for road in edata["roads"]:
        road["edges"] = [e["id"] for e in edges if e.get("road") == road["id"]]
    ehead = "".join(line for line in etext.splitlines(keepends=True) if line.startswith("#"))
    ep.write_text(ehead + yaml.safe_dump(edata, allow_unicode=True, sort_keys=False, default_flow_style=None, width=140), encoding="utf-8")

    # manifesto: inclui SURFACE e marca a digitalização por camada
    mp = SEEDS / "CARTOGRAPHY.seed.yaml"
    mtext = mp.read_text(encoding="utf-8")
    mdata = yaml.safe_load(mtext)
    if "SURFACE" not in mdata["includes"]:
        mdata["includes"].insert(mdata["includes"].index("SUBTERRANEAN") + 1, "SURFACE")
    mdata["metadata"].setdefault("edges_digitized", {"REGIONAL": False}).update({"URBAN": True, "SUBTERRANEAN": True})
    mhead = "".join(line for line in mtext.splitlines(keepends=True) if line.startswith("#"))
    mp.write_text(mhead + yaml.safe_dump(mdata, allow_unicode=True, sort_keys=False, default_flow_style=None, width=140), encoding="utf-8")
    print(f"{len(edges)} arestas de superfície; {len(locations)} cruzamentos; rio com {len(traced['WAT-ASH']['points'])} pontos")


if __name__ == "__main__":
    main()
