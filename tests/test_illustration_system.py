"""Sistema de ilustração genérico do motor — Slice 4 de
docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md (seções 16, 19, 25.4, 28.3).

Três extensões OFF por padrão, neutras de gênero:
- `livingbook.py`: tarefas por slot (`features.images.illustration_slots`);
- `check_visual_canon.py`: bloco `illustration` e regras de `FIGURE`;
- `build_kdp_docx.py`: `illustrations[]` em layout/IMAGE_PLACEMENT.yaml.

A não regressão dos livros existentes é provada pelos goldens de
tests/test_compose_regression.py e pelos testes de DOCX de
tests/test_visual_narrative_rendering.py, que continuam intactos.

Execução (offline): .venv/Scripts/python.exe -m unittest tests.test_illustration_system -v
"""
from __future__ import annotations

import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml
from docx import Document
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import build_kdp_docx as bd  # noqa: E402
import check_visual_canon as vc  # noqa: E402
import livingbook as lb  # noqa: E402
from tests.test_visual_narrative_rendering import _docx_content_hash, _write_minimal_runtime  # noqa: E402

VN_FIXTURE_BOOK = REPO / "tests" / "fixtures" / "books" / "visual_narrative_mvp"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _dump(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _book_with_slots(tmp: Path, slots: dict[int, list[str]], flag: bool = True) -> Path:
    book = tmp / "book"
    shutil.copytree(VN_FIXTURE_BOOK, book)
    spec = _load(book / "BOOK_SPEC.yaml")
    # DRAFT remove o pipeline de imagens; STANDARD o mantém.
    spec["spec"]["execution_profile"] = "STANDARD"
    spec["spec"]["features"]["images"]["illustration_slots"] = flag
    _dump(book / "BOOK_SPEC.yaml", spec)
    arch = _load(book / "chapter_architecture.yaml")
    for chapter in arch["chapters"]:
        if chapter["number"] in slots:
            chapter["illustration_slots"] = slots[chapter["number"]]
    _dump(book / "chapter_architecture.yaml", arch)
    return book


class TestSlotTasks(unittest.TestCase):

    def test_slots_replace_per_chapter_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = _book_with_slots(Path(tmp), {1: ["IL-01", "IL-02"], 3: ["IL-03"]})
            graph = lb.build_standard_graph(book)
            tasks = {t["id"]: t for t in graph["spec"]["tasks"]}
            self.assertEqual(lb.validate_graph(graph, REPO), [])
            self.assertNotIn("T401_IMAGE_BRIEF", tasks)
            for nn, chapter in (("01", 1), ("02", 1), ("03", 3)):
                brief = tasks[f"T45{nn}_IL_BRIEF"]
                self.assertEqual(brief["parameters"], {"illustration_id": f"IL-{nn}", "chapter": chapter})
                self.assertIn("/canon/VISUAL_NARRATIVE_CANON.yaml", brief["inputs"])
                self.assertEqual(tasks[f"T45{nn}_IL_APPROVE"]["outputs"], [f"/images/approved/IL-{nn}.jpg"])
            self.assertEqual(graph["spec"]["gates"]["GATE_VISUAL"]["requires"],
                             ["T4501_IL_APPROVE", "T4502_IL_APPROVE", "T4503_IL_APPROVE"])
            self.assertIn("illustration_slots", tasks["T702_IMAGE_PLACEMENT"]["parameters"])

    def test_flag_off_keeps_per_chapter_pipeline_even_with_slots_declared(self):
        with tempfile.TemporaryDirectory() as tmp:
            with_slots_flag_off = lb.build_standard_graph(_book_with_slots(Path(tmp) / "a", {1: ["IL-01"]}, flag=False))
            original_book = _book_with_slots(Path(tmp) / "b", {}, flag=False)
            spec = _load(original_book / "BOOK_SPEC.yaml")
            spec["spec"]["features"]["images"].pop("illustration_slots")
            _dump(original_book / "BOOK_SPEC.yaml", spec)
            original = lb.build_standard_graph(original_book)
        ids = {t["id"] for t in with_slots_flag_off["spec"]["tasks"]}
        self.assertIn("T401_IMAGE_BRIEF", ids)
        self.assertEqual(with_slots_flag_off["spec"]["gates"]["GATE_VISUAL"], original["spec"]["gates"]["GATE_VISUAL"])

    def test_validate_book_rejects_invalid_and_duplicated_slots(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = _book_with_slots(Path(tmp), {1: ["IL-01", "plate-2"], 2: ["IL-01"]})
            errors = lb.validate_book_data(book, _load(book / "BOOK_SPEC.yaml"), _load(book / "BOOK_GRAPH.yaml"))
            self.assertTrue(any("invalid ids" in e for e in errors), errors)
            self.assertTrue(any("duplicated ids" in e for e in errors), errors)

    def test_validate_book_requires_slots_when_flag_is_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = _book_with_slots(Path(tmp), {})
            errors = lb.validate_book_data(book, _load(book / "BOOK_SPEC.yaml"), _load(book / "BOOK_GRAPH.yaml"))
            self.assertTrue(any("requires illustration_slots" in e for e in errors), errors)


def _context() -> dict:
    return {
        "bibles": {},
        "chapter_architecture": [
            {"number": n, "irreversible_turn": f"virada {n}", "illustration_slots": s}
            for n, s in ((1, ["IL-01"]), (2, []), (3, ["IL-02"]), (4, ["IL-03"]), (5, []), (6, []))
        ],
        "protected_scenes": [{"id": "THE_TURN", "chapters": [5], "purpose": "virada"}],
    }


def _canon() -> dict:
    return {
        "elements": [
            {"id": "FIG-A", "class": "FIGURE", "identity_ref": "DOC:/images/canon/FACE_CANON.md#fig-a",
             "states": [{"id": "S0", "initial": True}, {"id": "S1"}],
             "transitions": [{"from": "S0", "to": "S1", "trigger": "TURN:3", "display_from": "NEXT_CHAPTER"}]},
            {"id": "SYM-B", "class": "MOTIF"},
        ],
        "compositions": [
            {"id": "COMP-FRONT", "surface": "FRONT_COVER", "elements": [{"element": "FIG-A", "prominence": "DOMINANT"}],
             "approval": {"policy": "REQUIRE_APPROVAL", "id": "APR-1"}},
            {"id": "IL-01", "surface": "INTERIOR_PLATE", "chapter": 1,
             "elements": [{"element": "FIG-A", "prominence": "DOMINANT", "state": "S0"}],
             "illustration": {"category": "HERO", "text_relation": "COMPLEMENT", "adds": "o gesto que o texto não diz"}},
            {"id": "IL-02", "surface": "INTERIOR_PLATE", "chapter": 3,
             "elements": [{"element": "SYM-B", "prominence": "DOMINANT"}],
             "illustration": {"category": "SYMBOL", "text_relation": "FORESHADOW", "payoff_anchor": "SCENE:THE_TURN"}},
            {"id": "IL-03", "surface": "INTERIOR_PLATE", "chapter": 4,
             "elements": [{"element": "FIG-A", "prominence": "DOMINANT", "state": "S1"}],
             "illustration": {"category": "CALLBACK", "text_relation": "CONTRADICT",
                              "contradicts": "a personagem acredita estar sozinha", "callback_of": "IL-01",
                              "callback_changes": [{"what": "a figura mudou de estado"}],
                              "placement": "AFTER"}},
        ],
    }


class TestIllustrationAndFigureRules(unittest.TestCase):

    def findings(self, mutate=None) -> list[dict]:
        canon = _canon()
        context = _context()
        if mutate:
            mutate(canon, context)
        return vc.check_illustrations(canon, context) + vc.check_figures(canon, context)

    def assertCategory(self, mutate, category, severity):
        found = [f for f in self.findings(mutate) if f["category"] == category]
        self.assertTrue(found, f"{category} não emitido: {[f['category'] for f in self.findings(mutate)]}")
        self.assertIn(severity, {f["severity"] for f in found})

    @staticmethod
    def comp(canon, cid):
        return next(c for c in canon["compositions"] if c["id"] == cid)

    def test_valid_canon_has_no_findings(self):
        self.assertEqual(self.findings(), [])

    def test_canon_without_illustrations_or_figures_is_untouched(self):
        canon = {"elements": [{"id": "SYM-B", "class": "MOTIF"}],
                 "compositions": [{"id": "COMP-X", "surface": "FRONT_COVER", "elements": [{"element": "SYM-B"}]}]}
        context = {"bibles": {}}
        self.assertEqual(vc.check_illustrations(canon, context) + vc.check_figures(canon, context), [])

    def test_text_relation_missing(self):
        self.assertCategory(lambda c, x: self.comp(c, "IL-01")["illustration"].pop("text_relation"),
                            "TEXT_RELATION_MISSING", "HIGH")

    def test_literal_illustration(self):
        self.assertCategory(lambda c, x: self.comp(c, "IL-01")["illustration"].pop("adds"), "LITERAL_ILLUSTRATION", "MEDIUM")

    def test_contradiction_undeclared(self):
        self.assertCategory(lambda c, x: self.comp(c, "IL-03")["illustration"].pop("contradicts"),
                            "CONTRADICTION_UNDECLARED", "HIGH")

    def test_foreshadow_payoff_must_be_later(self):
        self.assertCategory(lambda c, x: self.comp(c, "IL-02")["illustration"].update(payoff_anchor="TURN:2"),
                            "FORESHADOW_WITHOUT_PAYOFF", "HIGH")

    def test_foreshadow_payoff_must_resolve(self):
        self.assertCategory(lambda c, x: self.comp(c, "IL-02")["illustration"].update(payoff_anchor="SCENE:NOPE"),
                            "FORESHADOW_WITHOUT_PAYOFF", "HIGH")

    def test_category_missing(self):
        self.assertCategory(lambda c, x: self.comp(c, "IL-02")["illustration"].pop("category"),
                            "ILLUSTRATION_CATEGORY_MISSING", "HIGH")

    def test_invalid_placement(self):
        self.assertCategory(lambda c, x: self.comp(c, "IL-03")["illustration"].update(placement="MIDDLE"),
                            "INVALID_ENUM", "HIGH")

    def test_callback_to_later_plate(self):
        self.assertCategory(lambda c, x: self.comp(c, "IL-01")["illustration"].update(callback_of="IL-03"),
                            "CALLBACK_UNRESOLVED", "HIGH")

    def test_slot_without_composition(self):
        def mutate(canon, context):
            canon["compositions"] = [c for c in canon["compositions"] if c["id"] != "IL-02"]
        self.assertCategory(mutate, "ILLUSTRATION_SLOT_MISMATCH", "HIGH")

    def test_composition_without_slot(self):
        def mutate(canon, context):
            context["chapter_architecture"][3]["illustration_slots"] = []
        self.assertCategory(mutate, "ILLUSTRATION_SLOT_MISMATCH", "HIGH")

    def test_composition_in_other_chapter_than_slot(self):
        self.assertCategory(lambda c, x: self.comp(c, "IL-02").update(chapter=2), "ILLUSTRATION_SLOT_MISMATCH", "HIGH")

    def test_figure_without_identity_ref(self):
        self.assertCategory(lambda c, x: c["elements"][0].pop("identity_ref"), "FIGURE_WITHOUT_IDENTITY_REF", "HIGH")

    def test_figure_on_cover_without_approval(self):
        self.assertCategory(lambda c, x: self.comp(c, "COMP-FRONT").update(approval={"policy": "SUGGEST"}),
                            "FIGURE_ON_COVER_UNAPPROVED", "HIGH")

    def test_figure_state_unresolved(self):
        self.assertCategory(lambda c, x: self.comp(c, "IL-01")["elements"][0].update(state="S9"),
                            "FIGURE_STATE_UNRESOLVED", "HIGH")

    def test_figure_state_mismatch_with_projection(self):
        # IL-03 no capítulo 4: TURN:3 + NEXT_CHAPTER projeta S1; declarar S0 é deriva.
        self.assertCategory(lambda c, x: self.comp(c, "IL-03")["elements"][0].update(state="S0"),
                            "FIGURE_STATE_MISMATCH", "HIGH")

    def test_existing_fixtures_gain_no_illustration_or_figure_findings(self):
        fixtures = REPO / "tests" / "fixtures" / "visual_narrative"
        for runtime in (fixtures / "runtime_cisne_negro", fixtures / "runtime_mare_de_chumbo"):
            canon = _load(runtime / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
            context = vc.load_context(runtime)
            self.assertEqual(vc.check_illustrations(canon, context) + vc.check_figures(canon, context), [], runtime.name)


class TestDocxIllustrations(unittest.TestCase):

    @staticmethod
    def _runtime_with_plates(tmp: Path, plates: list[dict]) -> Path:
        runtime = _write_minimal_runtime(tmp, chapter_count=2)
        for plate in plates:
            Image.new("RGB", (100, 150), (40, 40, 40)).save(runtime / "images" / "approved" / f"{plate['id']}.jpg")
        (runtime / "layout").mkdir(parents=True, exist_ok=True)
        _dump(runtime / "layout" / "IMAGE_PLACEMENT.yaml", {"illustrations": plates})
        return runtime

    def test_multiple_plates_per_chapter_by_id(self):
        plates = [
            {"id": "IL-01", "chapter": 1, "placement": "OPEN", "category": "HERO", "alt": "abertura"},
            {"id": "IL-02", "chapter": 1, "placement": "AFTER", "anchor": "capítulo 1", "category": "SYMBOL"},
            {"id": "IL-03", "chapter": 2, "placement": "AFTER", "anchor": "capítulo 2"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._runtime_with_plates(Path(tmp), plates)
            self.assertEqual(bd.build(runtime), 0)
            doc = Document(runtime / "outputs" / "KDP_DRAFT.docx")
            titles = [s._inline.docPr.get("title") for s in doc.inline_shapes]
            self.assertEqual(titles, ["Ilustração IL-01", "Ilustração IL-02", "Ilustração IL-03"])
            hero, symbol = doc.inline_shapes[0], doc.inline_shapes[1]
            self.assertAlmostEqual(hero.width.inches, 4.25, places=2)
            self.assertAlmostEqual(symbol.height.inches, 3.0, places=2)

    def test_missing_anchor_fails_the_build(self):
        plates = [{"id": "IL-01", "chapter": 1, "placement": "AFTER", "anchor": "texto que não existe"}]
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._runtime_with_plates(Path(tmp), plates)
            with self.assertRaises(SystemExit) as raised:
                bd.build(runtime)
            self.assertIn("IL-01", str(raised.exception))

    def test_missing_image_fails_the_build(self):
        plates = [{"id": "IL-09", "chapter": 2, "placement": "OPEN"}]
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._runtime_with_plates(Path(tmp), plates)
            (runtime / "images" / "approved" / "IL-09.jpg").unlink()
            with self.assertRaises(SystemExit):
                bd.build(runtime)

    def test_placement_file_without_illustrations_keeps_old_docx(self):
        hashes = []
        for with_file in (False, True):
            with tempfile.TemporaryDirectory() as tmp:
                runtime = _write_minimal_runtime(Path(tmp), chapter_count=2)
                if with_file:
                    (runtime / "layout").mkdir(parents=True, exist_ok=True)
                    _dump(runtime / "layout" / "IMAGE_PLACEMENT.yaml",
                          {"chapters": {1: {"placement": "OPEN"}, 2: {"placement": "OPEN"}}})
                self.assertEqual(bd.build(runtime), 0)
                hashes.append(_docx_content_hash(runtime / "outputs" / "KDP_DRAFT.docx"))
        self.assertEqual(hashes[0], hashes[1])


if __name__ == "__main__":
    unittest.main()
