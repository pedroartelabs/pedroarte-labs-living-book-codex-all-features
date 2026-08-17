"""Testes da capacidade de geração de imagem do motor.

Rodar:
    .venv/Scripts/python.exe -m unittest discover -s tests -v

A credencial vem de `.env` na raiz do repositório (nunca de código-fonte).
Os testes NUNCA imprimem o valor da chave — apenas presença e tamanho.

Divisão proposital:
  - Testes de unidade (offline) validam a lógica que causa reprovação no
    GATE_MEDIA_ASSETS: escolha de tamanho e enquadramento exato. Não gastam
    crédito e rodam sempre.
  - Um teste de integração faz UMA chamada real à API e grava em
    tests/outputs/. É pulado automaticamente se não houver credencial, para
    que a suíte continue utilizável em CI sem segredo.
"""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

from PIL import Image  # noqa: E402

import generate_image  # noqa: E402
from generate_image import cover_fit, load_dotenv, nearest_size  # noqa: E402

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"

# Contratos que o motor exige (espelham engine/scripts/validate_media_assets.py).
COVER_SIZE = (1600, 2560)
STORY_SIZE = (1080, 1920)
MIN_DPI = 300


def api_key() -> str | None:
    load_dotenv(REPO)
    return os.environ.get("OPENAI_API_KEY")


class TestCredentialLoading(unittest.TestCase):
    """A credencial precisa vir do .env, e o .env não pode vazar para o git."""

    def test_dotenv_is_found_and_key_is_loaded(self):
        path = load_dotenv(REPO)
        self.assertIsNotNone(path, "nenhum .env encontrado a partir da raiz do repo")
        key = os.environ.get("OPENAI_API_KEY")
        self.assertTrue(key, "OPENAI_API_KEY ausente ou vazia no .env")
        # Nunca imprima o valor. Verificações estruturais apenas.
        # Não guardamos aqui nenhum fragmento de credencial real, nem da chave
        # antiga: este arquivo vai para um repositório público, e um prefixo de
        # chave é material sensível o bastante para disparar secret scanners.
        self.assertGreater(len(key), 20, "chave suspeita de truncamento")
        self.assertTrue(key.startswith("sk-"), "formato inesperado de chave OpenAI")

    def test_dotenv_is_gitignored(self):
        gitignore = (REPO / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", gitignore, "'.env' precisa estar no .gitignore")

    def test_no_key_is_hardcoded_in_engine_sources(self):
        for path in (REPO / "engine" / "scripts").glob("*.py"):
            self.assertNotIn(
                "sk-proj-", path.read_text(encoding="utf-8"),
                f"credencial hardcoded encontrada em {path.name}",
            )


class TestSizeSelection(unittest.TestCase):
    """A API não produz as dimensões do motor; escolher o tamanho mais próximo
    em proporção é o que evita distorção depois do corte."""

    def test_cover_picks_portrait_size(self):
        self.assertEqual(nearest_size("gpt-image-1", *COVER_SIZE), "1024x1536")

    def test_story_picks_portrait_size(self):
        self.assertEqual(nearest_size("dall-e-3", *STORY_SIZE), "1024x1792")

    def test_landscape_target_picks_landscape_size(self):
        self.assertEqual(nearest_size("gpt-image-1", 1600, 1000), "1536x1024")

    def test_unknown_model_falls_back_without_raising(self):
        self.assertIn("x", nearest_size("modelo-inexistente", 1000, 1000))


class TestCoverFit(unittest.TestCase):
    """Enquadramento: precisa bater a dimensão EXATA sem distorcer."""

    def test_produces_exact_target_dimensions(self):
        src = Image.new("RGB", (1024, 1536), (10, 10, 10))
        self.assertEqual(cover_fit(src, *COVER_SIZE).size, COVER_SIZE)

    def test_handles_aspect_mismatch_in_both_directions(self):
        for src_size in [(1024, 1024), (1536, 1024), (1024, 1792)]:
            with self.subTest(src=src_size):
                src = Image.new("RGB", src_size, (10, 10, 10))
                self.assertEqual(cover_fit(src, *STORY_SIZE).size, STORY_SIZE)

    def test_does_not_distort_aspect_ratio(self):
        """Um círculo continua redondo: escala uniforme + corte, nunca stretch."""
        src = Image.new("RGB", (1024, 1024), (0, 0, 0))
        for x in range(462, 562):  # faixa central horizontal
            for y in range(462, 562):
                src.putpixel((x, y), (255, 255, 255))
        out = cover_fit(src, 1000, 1000)
        white = [(x, y) for x in range(1000) for y in range(1000)
                 if out.getpixel((x, y))[0] > 200]
        xs = [p[0] for p in white]
        ys = [p[1] for p in white]
        largura, altura = max(xs) - min(xs), max(ys) - min(ys)
        self.assertAlmostEqual(largura / altura, 1.0, delta=0.05,
                               msg="quadrado deixou de ser quadrado: houve distorção")


@unittest.skipUnless(api_key(), "OPENAI_API_KEY ausente; teste de integração pulado")
class TestRealImageGeneration(unittest.TestCase):
    """Chamada real à API. Gasta crédito — uma única imagem, qualidade baixa."""

    @classmethod
    def setUpClass(cls):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.out = OUTPUT_DIR / "test_cover.jpg"
        raw, cls.usage = generate_image.request_image(
            api_key=api_key(),
            model="gpt-image-1",
            prompt=(
                "Teste técnico. Fundo preto absoluto com um único ponto de luz "
                "dourada no centro. Minimalismo extremo. Sem texto, sem rostos, "
                "sem logotipos."
            ),
            size=nearest_size("gpt-image-1", *COVER_SIZE),
            quality="low",
        )
        from io import BytesIO
        with Image.open(BytesIO(raw)) as generated:
            final = cover_fit(generated.convert("RGB"), *COVER_SIZE)
            final.save(cls.out, format="JPEG", quality=95, dpi=(MIN_DPI, MIN_DPI))

    def test_file_was_created(self):
        self.assertTrue(self.out.is_file())
        self.assertGreater(self.out.stat().st_size, 10_000, "arquivo pequeno demais para ser real")

    def test_meets_gate_media_assets_contract(self):
        """O mesmo contrato que validate_media_assets.py exige."""
        with Image.open(self.out) as img:
            self.assertEqual(img.format, "JPEG")
            self.assertEqual(img.size, COVER_SIZE)
            self.assertEqual(img.mode, "RGB")
            dpi = img.info.get("dpi", (0, 0))
            self.assertGreaterEqual(dpi[0], MIN_DPI)
            self.assertGreaterEqual(dpi[1], MIN_DPI)

    def test_api_returned_usage_telemetry(self):
        """Sem telemetria da API não há como atribuir custo por artefato."""
        self.assertTrue(self.usage, "API não devolveu bloco 'usage'")
        self.assertIn("output_tokens", self.usage)
        self.assertGreater(self.usage["output_tokens"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
