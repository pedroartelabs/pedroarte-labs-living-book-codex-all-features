"""Compõe deterministicamente a capa KDP e os cinco Instagram Stories.

Generaliza `scripts/build_cover_and_stories.py` do runtime
`a_morte_ainda_nao_nasceu`, cuja saída atende exatamente ao contrato que
`validate_media_assets.py` audita (capa 1600×2560, Stories 1080×1920, RGB,
300 DPI).

Três correções em relação ao original
--------------------------------------
1. **Portabilidade.** O original carregava fontes de caminhos fixos do Windows
   (`C:\\Windows\\Fonts\\georgia.ttf`). Aqui há descoberta de fonte por
   plataforma, com fallback explícito — o script não quebra fora do Windows,
   e diz qual fonte usou.
2. **Paleta e textos configuráveis.** Cor, tipografia e copy vêm de
   `media/MEDIA_DESIGN.yaml` (opcional) e de `BOOK_SPEC.yaml`, não do código.
3. **Caminho sem custo de API.** Capa e Stories são majoritariamente
   tipográficos. Sem imagem base disponível — conta de API sem crédito, host
   sem geração de imagem — o script compõe sobre fundo sólido/gradiente e
   ainda satisfaz o GATE_MEDIA_ASSETS. Geração de pixel deixa de ser um
   bloqueio duro para a entrega.

Uso:
    python engine/scripts/build_cover_and_stories.py --runtime runtime/<slug>
    python engine/scripts/build_cover_and_stories.py --runtime <rt> --no-base-image
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _layout_config import load_book_metadata, load_yaml  # noqa: E402

COVER_SIZE = (1600, 2560)
STORY_SIZE = (1080, 1920)
DPI = (300, 300)

COVER_OUT = Path("media/outputs/cover/BOOK_COVER_KDP.jpg")
STORY_OUT_DIR = Path("media/outputs/instagram_stories")
MANIFEST_OUT = Path("media/outputs/MEDIA_ASSET_MANIFEST.md")
DESIGN_CONFIG = Path("media/MEDIA_DESIGN.yaml")

# Famílias procuradas por plataforma, em ordem de preferência. A primeira que
# existir vence; se nenhuma existir, cai para a fonte embutida do Pillow (que
# funciona, mas não é tipograficamente aceitável para publicação — o script
# avisa em vez de fingir que está tudo bem).
FONT_CANDIDATES = {
    "serif": [
        "C:/Windows/Fonts/georgia.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    ],
    "serif_bold": [
        "C:/Windows/Fonts/georgiab.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    ],
    "sans": [
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ],
    "sans_bold": [
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ],
}

DEFAULT_DESIGN = {
    "palette": {
        "ground": [20, 37, 49],
        "ink": [242, 237, 222],
        "accent": [111, 45, 55],
        "muted": [224, 220, 207],
    },
    "cover": {
        "base_image": "images/approved/chapter_01.jpg",
        "overlay_top_alpha": 120,
        "overlay_bottom_alpha": 232,
        "title_size": 132,
        "author_size": 54,
        "tagline_size": 46,
    },
    "stories": {
        "overlay_top_alpha": 150,
        "overlay_bottom_alpha": 238,
        "headline_size": 74,
        "body_size": 42,
        "label_size": 30,
    },
}


def resolve_font(kind: str) -> tuple[Path | None, str]:
    for candidate in FONT_CANDIDATES[kind]:
        path = Path(candidate)
        if path.is_file():
            return path, path.name
    return None, "PIL default (bitmap)"


def load_font(kind: str, size: int) -> ImageFont.ImageFont:
    path, _ = resolve_font(kind)
    if path is None:
        return ImageFont.load_default()
    return ImageFont.truetype(str(path), size=size)


def deep_get(cfg: dict, *keys, default=None):
    node = cfg
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node


def merged_design(runtime: Path) -> dict:
    design = {k: dict(v) for k, v in DEFAULT_DESIGN.items()}
    path = runtime / DESIGN_CONFIG
    if path.is_file():
        override = load_yaml(path).get("spec", {}) or {}
        for section, values in override.items():
            if isinstance(values, dict):
                design.setdefault(section, {}).update(values)
            else:
                design[section] = values
    return design


def crop_fill(image: Image.Image, size: tuple[int, int], focus_y: float = 0.5) -> Image.Image:
    """Escala preservando proporção e corta o excedente — nunca distorce."""
    image = image.convert("RGB")
    target_ratio = size[0] / size[1]
    source_ratio = image.width / image.height
    if source_ratio > target_ratio:
        width = round(image.height * target_ratio)
        left = (image.width - width) // 2
        box = (left, 0, left + width, image.height)
    else:
        height = round(image.width / target_ratio)
        top = round((image.height - height) * max(0.0, min(1.0, focus_y)))
        top = max(0, min(image.height - height, top))
        box = (0, top, image.width, top + height)
    return image.crop(box).resize(size, Image.Resampling.LANCZOS)


def vertical_gradient(size, color, top_alpha: int, bottom_alpha: int) -> Image.Image:
    """Gradiente vertical em faixas de 1 px — barato e suficiente, já que o
    gradiente é sempre vertical e uniforme na horizontal."""
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    height = max(1, size[1] - 1)
    for y in range(size[1]):
        t = y / height
        alpha = round(top_alpha * (1 - t) + bottom_alpha * t)
        draw.line([(0, y), (size[0], y)], fill=(*color, alpha))
    return overlay


def make_ground(size, base_path: Path | None, color, top_alpha, bottom_alpha) -> Image.Image:
    """Fundo da peça: imagem base escurecida por gradiente, ou — sem imagem
    disponível — gradiente puro sobre cor sólida. O segundo caminho não custa
    nenhuma chamada de API."""
    if base_path and base_path.is_file():
        with Image.open(base_path) as src:
            ground = crop_fill(src, size, focus_y=0.42)
    else:
        ground = Image.new("RGB", size, tuple(color))
        # Sem foto, um leve degradê evita o aspecto de bloco chapado.
        ground = Image.alpha_composite(
            ground.convert("RGBA"),
            vertical_gradient(size, (0, 0, 0), 0, 90),
        ).convert("RGB")
    return Image.alpha_composite(
        ground.convert("RGBA"),
        vertical_gradient(size, tuple(color), top_alpha, bottom_alpha),
    ).convert("RGB")


def wrap(text: str, face, max_width: int, draw: ImageDraw.ImageDraw) -> str:
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=face) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


def save_jpeg(image: Image.Image, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(
        path, "JPEG", quality=96, subsampling=0, optimize=True,
        progressive=True, dpi=DPI,
    )
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_cover(runtime: Path, book: dict, design: dict, use_base: bool) -> tuple[Path, str]:
    palette, cover_cfg = design["palette"], design["cover"]
    base = runtime / cover_cfg["base_image"] if use_base else None
    use_base_image = bool(base and base.is_file())
    img = make_ground(COVER_SIZE, base, palette["ground"],
                      cover_cfg["overlay_top_alpha"], cover_cfg["overlay_bottom_alpha"])
    draw = ImageDraw.Draw(img)
    margin = 150
    inner = COVER_SIZE[0] - 2 * margin

    # Posições proporcionais à altura, não pixels fixos: com foto de fundo o
    # título sobe (deixa a imagem respirar); sem foto ele desce ao terço
    # superior, senão a peça fica com um vazio morto no meio.
    height = COVER_SIZE[1]
    title_y = round(height * (0.12 if use_base_image else 0.28))
    tagline_y = round(height * (0.74 if use_base_image else 0.50))
    rule_y = round(height * 0.83)
    author_y = round(height * 0.86)

    title_face = load_font("serif_bold", cover_cfg["title_size"])
    author_face = load_font("serif", cover_cfg["author_size"])
    title = wrap(book["title"].upper(), title_face, inner, draw)
    draw.multiline_text((COVER_SIZE[0] // 2, title_y), title, font=title_face,
                        fill=tuple(palette["ink"]), anchor="ma", align="center", spacing=18)

    tagline = design.get("tagline")
    if tagline:
        tag_face = load_font("serif", cover_cfg["tagline_size"])
        draw.multiline_text((COVER_SIZE[0] // 2, tagline_y),
                            wrap(tagline, tag_face, inner, draw), font=tag_face,
                            fill=tuple(palette["muted"]), anchor="ma", align="center", spacing=12)

    draw.line([(margin + 260, rule_y), (COVER_SIZE[0] - margin - 260, rule_y)],
              fill=tuple(palette["accent"]), width=4)
    draw.multiline_text((COVER_SIZE[0] // 2, author_y),
                        book["author"].upper(), font=author_face,
                        fill=tuple(palette["ink"]), anchor="ma", align="center")

    out = runtime / COVER_OUT
    return out, save_jpeg(img, out)


def build_stories(runtime: Path, book: dict, design: dict, use_base: bool) -> list[tuple[Path, str]]:
    palette, story_cfg = design["palette"], design["stories"]
    beats = design.get("story_beats") or [
        {"label": "O GANCHO", "headline": book["title"].upper()},
        {"label": "A SUSPENSÃO", "headline": "Uma pergunta sem resposta fácil."},
        {"label": "O CONFLITO", "headline": "Nada aqui se resolve sozinho."},
        {"label": "A PROMESSA", "headline": "Uma história que continua depois da última página."},
        {"label": "DISPONÍVEL", "headline": book["title"].upper(),
         "body": f"{book['author']} — disponível na Amazon."},
    ]
    results = []
    for index, beat in enumerate(beats[:5], start=1):
        base = None
        if use_base:
            candidate = runtime / "images/approved" / f"chapter_{index:02d}.jpg"
            base = candidate if candidate.is_file() else None
        img = make_ground(STORY_SIZE, base, palette["ground"],
                          story_cfg["overlay_top_alpha"], story_cfg["overlay_bottom_alpha"])
        draw = ImageDraw.Draw(img)
        inner = STORY_SIZE[0] - 200

        label_face = load_font("sans_bold", story_cfg["label_size"])
        draw.text((STORY_SIZE[0] // 2, 300), beat.get("label", ""), font=label_face,
                  fill=tuple(palette["accent"]), anchor="ma")

        head_face = load_font("serif_bold", story_cfg["headline_size"])
        draw.multiline_text((STORY_SIZE[0] // 2, 420),
                            wrap(beat.get("headline", ""), head_face, inner, draw),
                            font=head_face, fill=tuple(palette["ink"]),
                            anchor="ma", align="center", spacing=16)

        if beat.get("body"):
            body_face = load_font("serif", story_cfg["body_size"])
            draw.multiline_text((STORY_SIZE[0] // 2, STORY_SIZE[1] - 560),
                                wrap(beat["body"], body_face, inner, draw),
                                font=body_face, fill=tuple(palette["muted"]),
                                anchor="ma", align="center", spacing=12)

        draw.text((STORY_SIZE[0] // 2, STORY_SIZE[1] - 220), book["author"].upper(),
                  font=load_font("sans", story_cfg["label_size"]),
                  fill=tuple(palette["muted"]), anchor="ma")

        out = runtime / STORY_OUT_DIR / f"story_{index:02d}.jpg"
        results.append((out, save_jpeg(img, out)))
    return results


def write_manifest(runtime: Path, book: dict, assets: list[tuple[Path, str]], base_used: bool):
    lines = [
        f"# Media Asset Manifest — {book['title']}\n\n",
        "Gerado por `engine/scripts/build_cover_and_stories.py`.\n",
        f"Base de imagem: {'imagens aprovadas do livro' if base_used else 'composição tipográfica, sem geração de imagem'}.\n\n",
        "| Arquivo | Dimensões | SHA-256 |\n|---|---|---|\n",
    ]
    for path, digest in assets:
        with Image.open(path) as im:
            size = f"{im.size[0]}×{im.size[1]}"
        lines.append(f"| {path.relative_to(runtime).as_posix()} | {size} | `{digest}` |\n")
    out = runtime / MANIFEST_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(lines), encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compõe capa KDP e os cinco Instagram Stories no contrato do motor."
    )
    parser.add_argument("--runtime", type=Path, default=Path.cwd())
    parser.add_argument("--no-base-image", action="store_true",
                        help="Compõe só com tipografia, sem usar imagens de capítulo.")
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    if not (runtime / "book" / "BOOK_SPEC.yaml").is_file():
        print(f"Erro: {runtime} não parece um runtime.", file=sys.stderr)
        return 2

    book = load_book_metadata(runtime)
    design = merged_design(runtime)
    use_base = not args.no_base_image

    serif, serif_name = resolve_font("serif_bold")
    if serif is None:
        print("AVISO: nenhuma fonte TrueType encontrada; a saída usará a fonte "
              "bitmap do Pillow e NÃO tem qualidade de publicação. Instale uma "
              "família serifada ou aponte outra em media/MEDIA_DESIGN.yaml.",
              file=sys.stderr)

    assets = []
    cover_path, cover_hash = build_cover(runtime, book, design, use_base)
    assets.append((cover_path, cover_hash))
    assets.extend(build_stories(runtime, book, design, use_base))
    manifest = write_manifest(runtime, book, assets, use_base)

    print(f"MEDIA OK | fonte: {serif_name}")
    print(f"- capa: {cover_path.relative_to(runtime).as_posix()} | 1600×2560 | 300 DPI")
    print(f"- stories: 5 | 1080×1920 | 300 DPI")
    print(f"- manifesto: {manifest.relative_to(runtime).as_posix()} (SHA-256 de cada artefato)")
    print("Valide com: python scripts/validate_media_assets.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
