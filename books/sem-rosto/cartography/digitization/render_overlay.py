"""Renderiza a imagem de conferência humana: o Mapa A com as vias digitalizadas por cima.

    python books/sem-rosto/cartography/digitization/render_overlay.py [--scale 2] [--out overlay_A.png]

Verde = PROBABLE · laranja = UNCERTAIN · vermelho = linha de rota desenhada · azul = Ash Burn ·
amarelo = cruzamentos · ciano = lugares. A conferência humana aceita, corrige ou rebaixa cada via.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "engine" / "scripts"))
import check_cartography as cc  # noqa: E402

PKG = ROOT / "books" / "sem-rosto" / "cartography"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--out", type=Path, default=PKG / "digitization" / "overlay_A.png")
    args = ap.parse_args()
    model = cc.load_model(PKG / "seeds")
    img = Image.open(PKG / "sources" / "MAP_A_redmur_map.png").convert("RGB")
    sc = args.scale
    img = img.resize((int(img.width * sc), int(img.height * sc)), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    col = {"PROBABLE": (60, 255, 90), "UNCERTAIN": (255, 160, 30)}
    for l in model["locations"]:
        if l.get("id") == "WAT-ASH":
            pts = [(p["px"][0] * sc, p["px"][1] * sc) for p in l["polyline_px"] if p.get("source") == "SRC-MAP-A"]
            d.line(pts, fill=(70, 170, 255), width=3)
    for e in model["edges"]:
        poly = (e.get("source_polyline_px") or {}).get("points")
        if not poly or e["source_polyline_px"].get("source") != "SRC-MAP-A":
            continue
        pts = [(x * sc, y * sc) for x, y in poly]
        c = (255, 40, 40) if e.get("route_membership") else col.get(e.get("confidence"), (255, 255, 255))
        d.line(pts, fill=c, width=3)
        mx, my = pts[len(pts) // 2]
        d.text((mx + 3, my - 11), e["id"].replace("EDG-U-", "U"), fill=(255, 255, 255))
    for l in model["locations"]:
        for e in cc.as_list(l.get("source_px")):
            if e.get("source") == "SRC-MAP-A" and e.get("anchor") != "SCHEMATIC" and l.get("layer") == "URBAN":
                x, y = e["px"][0] * sc, e["px"][1] * sc
                jct = "JUNCTION" in cc.as_list(l.get("type"))
                r = 4
                d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 235, 60) if jct else (60, 240, 255), width=2)
    img.save(args.out, optimize=True)
    print(f"{args.out} ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
