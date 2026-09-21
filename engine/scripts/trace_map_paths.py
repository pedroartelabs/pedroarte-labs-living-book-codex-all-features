"""Ferramenta de digitalização de vias sobre um mapa em imagem (neutra de obra).

Slice 2 do SDD da cartografia (seção 36.3): em vez de marcar cada curva à mão,
o operador informa só os pontos-chave de cada via (origem, cruzamentos, destino)
em pixels; a ferramenta segue a via DESENHADA pelo caminho de menor custo sobre
a imagem (vias são mais claras que o terreno) e devolve a polilinha simplificada.
O resultado é sempre conferido por um humano em uma imagem de sobreposição.

    python engine/scripts/trace_map_paths.py --image MAP.png --spec paths.yaml --out traced.yaml [--overlay o.png]

`paths.yaml`:
    paths:
      - {id: EDG-U-001, via: [[521, 545], [552, 830]], tol: 1.5}
Saída: os mesmos ids com `points` (polilinha simplificada) e `length_px`.

Depende de Pillow e PyYAML (já em requirements.txt).
"""
from __future__ import annotations

import argparse
import heapq
import math
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw


def cost_grid(img: Image.Image, mode: str = "road"):
    """Custo por pixel. mode=road: pixels claros (vias). mode=red: vermelho (rotas). mode=water: azulado (cursos d'água)."""
    w, h = img.size
    rgb = img.convert("RGB")
    px = rgb.load()
    cost = [[1.0] * w for _ in range(h)]
    for y in range(h):
        row = cost[y]
        for x in range(w):
            r, g, b = px[x, y]
            if mode == "water":
                blue = max(0.0, (b - r - 8) / 40.0)
                row[x] = 1.0 + 40.0 * (1.0 - min(1.0, blue)) ** 2
                continue
            if mode == "red":
                redness = max(0.0, (r - max(g, b) - 40) / 120.0)
                row[x] = 1.0 + 40.0 * (1.0 - min(1.0, redness)) ** 2
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            sat = max(r, g, b) - min(r, g, b)
            bright = max(0.0, (185.0 - lum) / 185.0)
            row[x] = 1.0 + 40.0 * bright * bright + 0.05 * sat
    return cost


def astar(cost, start, goal, margin=60):
    w, h = len(cost[0]), len(cost)
    x0, y0 = max(0, min(start[0], goal[0]) - margin), max(0, min(start[1], goal[1]) - margin)
    x1, y1 = min(w - 1, max(start[0], goal[0]) + margin), min(h - 1, max(start[1], goal[1]) + margin)
    sx, sy, gx, gy = int(start[0]), int(start[1]), int(goal[0]), int(goal[1])
    open_heap = [(0.0, 0.0, sx, sy)]
    best = {(sx, sy): 0.0}
    came = {}
    moves = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
             (-1, -1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (1, 1, 1.4142)]
    while open_heap:
        _, g, x, y = heapq.heappop(open_heap)
        if (x, y) == (gx, gy):
            path = [(x, y)]
            while (x, y) in came:
                x, y = came[(x, y)]
                path.append((x, y))
            return path[::-1]
        if g > best.get((x, y), 1e18):
            continue
        for dx, dy, step in moves:
            nx, ny = x + dx, y + dy
            if nx < x0 or nx > x1 or ny < y0 or ny > y1:
                continue
            ng = g + step * (cost[ny][nx] + cost[y][x]) / 2.0
            if ng < best.get((nx, ny), 1e18):
                best[(nx, ny)] = ng
                came[(nx, ny)] = (x, y)
                hh = math.hypot(gx - nx, gy - ny)
                heapq.heappush(open_heap, (ng + hh, ng, nx, ny))
    return None


def simplify(points, tol):
    """Douglas-Peucker."""
    if len(points) < 3:
        return points
    (ax, ay), (bx, by) = points[0], points[-1]
    dmax, idx = 0.0, 0
    for i in range(1, len(points) - 1):
        px, py = points[i]
        if (ax, ay) == (bx, by):
            d = math.hypot(px - ax, py - ay)
        else:
            d = abs((by - ay) * px - (bx - ax) * py + bx * ay - by * ax) / math.hypot(by - ay, bx - ax)
        if d > dmax:
            dmax, idx = d, i
    if dmax > tol:
        left = simplify(points[: idx + 1], tol)
        right = simplify(points[idx:], tol)
        return left[:-1] + right
    return [points[0], points[-1]]


def trace(img_path: Path, specs, default_tol=2.0):
    img = Image.open(img_path)
    grids = {}
    out = []
    for spec in specs:
        mode = spec.get("mode", "road")
        if mode not in grids:
            grids[mode] = cost_grid(img, mode)
        cost = grids[mode]
        via = [tuple(p) for p in spec["via"]]
        full = []
        failed = False
        for a, b in zip(via, via[1:]):
            seg = astar(cost, a, b, margin=spec.get("margin", 60))
            if seg is None:
                failed = True
                break
            full.extend(seg if not full else seg[1:])
        if failed:
            out.append({"id": spec["id"], "points": None, "error": "sem caminho"})
            continue
        pts = simplify(full, spec.get("tol", default_tol))
        length = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(full, full[1:]))
        straight = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(via, via[1:]))
        out.append({"id": spec["id"], "points": [list(p) for p in pts], "length_px": round(length, 1),
                    "detour_ratio": round(length / straight, 2) if straight else 1.0})
    return out


def overlay(img_path: Path, traced, out: Path, scale=2, crop=None):
    img = Image.open(img_path).convert("RGB")
    if crop:
        img = img.crop(crop)
    ox, oy = (crop[0], crop[1]) if crop else (0, 0)
    img = img.resize((img.width * scale, img.height * scale), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    palette = [(255, 60, 60), (60, 255, 60), (80, 160, 255), (255, 230, 40), (255, 90, 255), (60, 255, 255), (255, 150, 30)]
    for i, t in enumerate(traced):
        if not t.get("points"):
            continue
        col = palette[i % len(palette)]
        pts = [((x - ox) * scale, (y - oy) * scale) for x, y in t["points"]]
        d.line(pts, fill=col, width=3)
        mx, my = pts[len(pts) // 2]
        d.text((mx + 4, my - 12), t["id"].replace("EDG-", ""), fill=col)
    img.save(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", type=Path, required=True)
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--overlay", type=Path)
    ap.add_argument("--crop", type=int, nargs=4)
    args = ap.parse_args()
    specs = yaml.safe_load(args.spec.read_text(encoding="utf-8"))["paths"]
    traced = trace(args.image, specs)
    args.out.write_text(yaml.safe_dump({"paths": traced}, allow_unicode=True, sort_keys=False, default_flow_style=None), encoding="utf-8")
    if args.overlay:
        overlay(args.image, traced, args.overlay, crop=args.crop)
    bad = [t["id"] for t in traced if not t.get("points")]
    print(f"{len(traced) - len(bad)} vias traçadas" + (f"; sem caminho: {bad}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
