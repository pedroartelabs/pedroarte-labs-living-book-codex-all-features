from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError


COVER_RELATIVE_PATH = Path("media/outputs/cover/BOOK_COVER_KDP.jpg")
STORIES_RELATIVE_DIR = Path("media/outputs/instagram_stories")
EXPECTED_STORIES = [f"story_{index:02d}.jpg" for index in range(1, 6)]

COVER_SIZE = (1600, 2560)
STORY_SIZE = (1080, 1920)
MIN_DPI = 300
MAX_COVER_BYTES = 50 * 1024 * 1024


def normalized_dpi(image: Image.Image) -> tuple[float, float]:
    raw = image.info.get("dpi", (0, 0))
    if not isinstance(raw, (tuple, list)) or len(raw) < 2:
        return 0.0, 0.0
    try:
        return float(raw[0]), float(raw[1])
    except (TypeError, ValueError):
        return 0.0, 0.0


def validate_jpeg(
    path: Path,
    expected_size: tuple[int, int],
    label: str,
    *,
    max_bytes: int | None = None,
) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"{label}: arquivo ausente: {path}"]
    if path.suffix.lower() not in {".jpg", ".jpeg"}:
        errors.append(f"{label}: extensão deve ser JPG/JPEG")
    if max_bytes is not None and path.stat().st_size > max_bytes:
        errors.append(
            f"{label}: arquivo excede {max_bytes // (1024 * 1024)} MB "
            f"({path.stat().st_size} bytes)"
        )
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            if image.format != "JPEG":
                errors.append(f"{label}: formato interno deve ser JPEG, encontrado {image.format}")
            if image.size != expected_size:
                errors.append(
                    f"{label}: dimensões {image.size[0]}x{image.size[1]}, "
                    f"esperado {expected_size[0]}x{expected_size[1]}"
                )
            if image.mode != "RGB":
                errors.append(f"{label}: perfil/modo deve ser RGB, encontrado {image.mode}")
            dpi_x, dpi_y = normalized_dpi(image)
            if dpi_x < MIN_DPI or dpi_y < MIN_DPI:
                errors.append(
                    f"{label}: DPI deve ser pelo menos {MIN_DPI}x{MIN_DPI}, "
                    f"encontrado {dpi_x:g}x{dpi_y:g}"
                )
    except (OSError, UnidentifiedImageError) as exc:
        errors.append(f"{label}: JPEG inválido: {exc}")
    return errors


def validate_runtime(runtime: Path) -> list[str]:
    errors: list[str] = []
    cover = runtime / COVER_RELATIVE_PATH
    errors.extend(
        validate_jpeg(
            cover,
            COVER_SIZE,
            "capa KDP",
            max_bytes=MAX_COVER_BYTES,
        )
    )

    stories_dir = runtime / STORIES_RELATIVE_DIR
    if not stories_dir.is_dir():
        errors.append(f"Stories: diretório ausente: {stories_dir}")
        return errors

    found = sorted(
        path.name
        for path in stories_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg"}
    )
    if found != EXPECTED_STORIES:
        errors.append(
            "Stories: devem existir exatamente cinco JPEGs nomeados "
            f"{', '.join(EXPECTED_STORIES)}; encontrados: {', '.join(found) or 'nenhum'}"
        )
    for filename in EXPECTED_STORIES:
        errors.extend(
            validate_jpeg(
                stories_dir / filename,
                STORY_SIZE,
                f"Story {filename[6:8]}",
            )
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida a capa KDP e os cinco Instagram Stories obrigatórios."
    )
    parser.add_argument(
        "--runtime",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Diretório raiz do runtime; por padrão, o runtime que contém este script.",
    )
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    errors = validate_runtime(runtime)
    if errors:
        print("MEDIA ASSET VALIDATION FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("MEDIA ASSET VALIDATION PASSED")
    print(f"- cover: {COVER_RELATIVE_PATH.as_posix()} | 1600x2560 | JPEG RGB | >=300 DPI")
    print(f"- stories: 5 | 1080x1920 | JPEG RGB | >=300 DPI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
