from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _layout_config import load_layout_config  # noqa: E402


COVER_RELATIVE_PATH = Path("media/outputs/cover/BOOK_COVER_KDP.jpg")
STORIES_RELATIVE_DIR = Path("media/outputs/instagram_stories")
MANIFEST_RELATIVE_PATH = Path("media/outputs/MEDIA_ASSET_MANIFEST.md")
EXPECTED_STORIES = [f"story_{index:02d}.jpg" for index in range(1, 6)]

COVER_SIZE = (1600, 2560)
STORY_SIZE = (1080, 1920)
MIN_DPI = 300
MAX_COVER_BYTES = 50 * 1024 * 1024

# Imagens de miolo: o DPI que importa é o EFETIVO na colocação, não o rótulo
# gravado no arquivo. Um JPEG de 1024 px marcado como 96 DPI, inserido em
# 3,25 pol., imprime a ~315 DPI. Validar só o metadado reprovaria, por engano,
# exatamente o tipo de imagem que a execução real provou ser adequada.
INTERIOR_IMAGES_RELATIVE_DIR = Path("images/approved")
INTERIOR_FILENAME_RE = re.compile(r"^chapter_(\d{2})\.jpg$", re.IGNORECASE)
MIN_EFFECTIVE_DPI = 300
SHA256_RE = re.compile(r"\b([0-9a-f]{64})\b", re.IGNORECASE)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def validate_interior_image(path: Path, label: str, width_in: float, height_in: float) -> list[str]:
    """Imagens de miolo. O critério é o DPI EFETIVO na colocação — pixels
    divididos pelas polegadas em que a imagem é inserida no DOCX — porque é
    isso que a gráfica imprime. O DPI de metadado é cosmético: a maioria dos
    geradores grava 96 por padrão, e reprovar por isso seria um falso negativo."""
    errors: list[str] = []
    if not path.is_file():
        return [f"{label}: arquivo ausente: {path}"]
    try:
        with Image.open(path) as image:
            if image.format != "JPEG":
                errors.append(f"{label}: formato interno deve ser JPEG, encontrado {image.format}")
            if image.mode != "RGB":
                errors.append(f"{label}: modo deve ser RGB, encontrado {image.mode}")
            px_w, px_h = image.size
            eff_x = px_w / width_in if width_in else 0
            eff_y = px_h / height_in if height_in else 0
            if eff_x < MIN_EFFECTIVE_DPI or eff_y < MIN_EFFECTIVE_DPI:
                errors.append(
                    f"{label}: DPI efetivo {eff_x:.0f}x{eff_y:.0f} abaixo de "
                    f"{MIN_EFFECTIVE_DPI} ({px_w}x{px_h} px em "
                    f"{width_in}x{height_in} pol.)"
                )
    except (OSError, UnidentifiedImageError) as exc:
        errors.append(f"{label}: JPEG inválido: {exc}")
    return errors


def manifest_hashes(runtime: Path) -> tuple[set[str], bool]:
    """Todos os SHA-256 citados no manifesto, em qualquer formatação.

    Verifica o fato (o hash está declarado e confere), não o layout do
    documento — o agente que escreve o manifesto continua livre para
    organizá-lo em tabela, lista ou seções."""
    path = runtime / MANIFEST_RELATIVE_PATH
    if not path.is_file():
        return set(), False
    text = path.read_text(encoding="utf-8", errors="replace")
    return {m.group(1).lower() for m in SHA256_RE.finditer(text)}, True


def validate_runtime(runtime: Path) -> list[str]:
    errors: list[str] = []
    delivery_assets: list[tuple[Path, str]] = []

    cover = runtime / COVER_RELATIVE_PATH
    errors.extend(
        validate_jpeg(
            cover,
            COVER_SIZE,
            "capa KDP",
            max_bytes=MAX_COVER_BYTES,
        )
    )
    if cover.is_file():
        delivery_assets.append((cover, "capa KDP"))

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
        story = stories_dir / filename
        errors.extend(validate_jpeg(story, STORY_SIZE, f"Story {filename[6:8]}"))
        if story.is_file():
            delivery_assets.append((story, f"Story {filename[6:8]}"))

    # Imagens de miolo, quando existirem: DPI efetivo na colocação declarada.
    interior_dir = runtime / INTERIOR_IMAGES_RELATIVE_DIR
    if interior_dir.is_dir():
        images_cfg = load_layout_config(runtime).get("images", {})
        width_in = float(images_cfg.get("width_in", 3.25))
        height_in = float(images_cfg.get("height_in", 4.875))
        for image_path in sorted(interior_dir.iterdir()):
            match = INTERIOR_FILENAME_RE.match(image_path.name)
            if match:
                errors.extend(
                    validate_interior_image(
                        image_path, f"miolo cap. {match.group(1)}", width_in, height_in
                    )
                )

    # Proveniência: cada artefato de entrega precisa do SHA-256 no manifesto.
    declared, manifest_exists = manifest_hashes(runtime)
    if not manifest_exists:
        errors.append(f"Manifesto ausente: {runtime / MANIFEST_RELATIVE_PATH}")
    else:
        for path, label in delivery_assets:
            digest = sha256_of(path)
            if digest not in declared:
                errors.append(
                    f"{label}: SHA-256 {digest} não consta em "
                    f"{MANIFEST_RELATIVE_PATH.as_posix()} — manifesto desatualizado "
                    "ou arquivo alterado após a geração"
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
    print("- stories: 5 | 1080x1920 | JPEG RGB | >=300 DPI")
    interior = runtime / INTERIOR_IMAGES_RELATIVE_DIR
    if interior.is_dir():
        count = sum(1 for p in interior.iterdir() if INTERIOR_FILENAME_RE.match(p.name))
        if count:
            print(f"- miolo: {count} imagens | DPI efetivo na colocação >={MIN_EFFECTIVE_DPI}")
    print(f"- proveniência: SHA-256 de cada artefato conferido em {MANIFEST_RELATIVE_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
