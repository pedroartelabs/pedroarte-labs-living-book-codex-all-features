"""Carregamento compartilhado da configuração de layout KDP.

Usado por `build_kdp_docx.py`, `build_cover_and_stories.py` e
`validate_media_assets.py`. Vive num módulo próprio para que os três leiam
exatamente a mesma configuração — se o construtor e o validador divergissem
sobre, digamos, o tamanho de colocação da imagem, o validador reprovaria
artefatos corretos (ou aprovaria errados).

Precedência: defaults do motor <- overrides do livro (`layout/KDP_LAYOUT.yaml`).
"""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

ENGINE = Path(__file__).resolve().parents[1]
DEFAULTS_PATH = ENGINE / "templates" / "KDP_LAYOUT_DEFAULTS.yaml"
OVERRIDE_RELATIVE = Path("layout/KDP_LAYOUT.yaml")


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def deep_merge(base: dict, override: dict) -> dict:
    """Merge recursivo: o override do livro vence chave a chave, sem exigir
    que ele repita a configuração inteira do motor."""
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_layout_config(runtime: Path) -> dict:
    cfg = load_yaml(DEFAULTS_PATH).get("spec", {})
    override = runtime / OVERRIDE_RELATIVE
    if override.is_file():
        cfg = deep_merge(cfg, load_yaml(override).get("spec", {}))
    return cfg


def load_book_metadata(runtime: Path) -> dict:
    """Metadados do livro a partir de book/BOOK_SPEC.yaml."""
    spec = load_yaml(runtime / "book" / "BOOK_SPEC.yaml")
    meta, body = spec.get("metadata", {}), spec.get("spec", {})
    titles = {int(k): v for k, v in (body.get("chapter_titles") or {}).items()}
    return {
        "title": meta.get("title", ""),
        "author": meta.get("author", ""),
        "language": meta.get("language", "pt-BR"),
        "chapter_count": meta.get("chapter_count", len(titles)),
        "titles": titles,
    }
