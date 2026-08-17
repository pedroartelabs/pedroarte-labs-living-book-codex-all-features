"""Sobrepõe tipografia real a um fundo de Story e grava o JPEG final.

Por que existe: modelos de imagem produzem texto corrompido com frequência.
A abordagem confiável para peças de marketing é híbrida — a API gera o fundo,
o código desenha o texto. É também a mais barata: a tipografia não custa
tokens.

Entrada: um fundo já nas dimensões finais (ver generate_image.py).
Saída: JPEG que satisfaz validate_media_assets.py (1080x1920, RGB, >=300 DPI).
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WINDOWS_FONTS = Path("C:/Windows/Fonts")
FONT_CANDIDATES_BOLD = ["georgiab.ttf", "timesbd.ttf", "arialbd.ttf", "segoeuib.ttf"]
FONT_CANDIDATES_REGULAR = ["georgia.ttf", "times.ttf", "arial.ttf", "segoeui.ttf"]


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for name in (FONT_CANDIDATES_BOLD if bold else FONT_CANDIDATES_REGULAR):
        candidate = WINDOWS_FONTS / name
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main() -> int:
    p = argparse.ArgumentParser(description="Compoe um Story final: fundo + tipografia.")
    p.add_argument("--bg", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--headline", required=True)
    p.add_argument("--kicker", default="")
    p.add_argument("--footer", default="")
    p.add_argument("--dpi", type=int, default=300)
    a = p.parse_args()

    with Image.open(a.bg) as src:
        img = src.convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img, "RGBA")

    margin = int(W * 0.10)
    max_w = W - 2 * margin
    gold = (232, 183, 90)
    cream = (242, 238, 228)

    # Véu escuro no topo garante contraste do texto sobre qualquer fundo.
    draw.rectangle([0, 0, W, int(H * 0.52)], fill=(10, 8, 6, 150))

    y = int(H * 0.10)
    if a.kicker:
        f = load_font(int(W * 0.032), bold=True)
        draw.text((margin, y), a.kicker.upper(), font=f, fill=gold)
        y += int(W * 0.075)

    f_head = load_font(int(W * 0.078), bold=True)
    for line in wrap(draw, a.headline, f_head, max_w):
        draw.text((margin, y), line, font=f_head, fill=cream)
        y += int(W * 0.092)

    if a.footer:
        f_foot = load_font(int(W * 0.030))
        fy = H - int(H * 0.07)
        draw.text((margin, fy), a.footer, font=f_foot, fill=gold)

    a.out.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.out, format="JPEG", quality=95, dpi=(a.dpi, a.dpi))
    print(f"STORY OK | {a.out} | {W}x{H} | RGB | {a.dpi} DPI | {a.out.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
