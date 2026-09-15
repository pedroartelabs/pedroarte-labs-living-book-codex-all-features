"""Testes do validador `check_visual_canon.py` — Slice 1 da capability
`BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM`
(ver docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md).

100% offline: só PyYAML, sem rede, sem credencial.

Camadas de teste (seção 29 da SDD):
- CONTRACT: os templates neutros do motor (engine/templates/) validam
  contrato (V0) e consistência de autora (V1). V2 (Chekhov) e V3
  (Anti-Generic) exigem canon narrativo real — por desenho, um template
  isolado não tem contra o que resolver âncoras, então não é testado
  através deles (fronteira documentada no próprio template).
- UNIT: resolução de cada tipo de âncora; os cinco status de Chekhov;
  faixas de papel de cor; precedência de constraints/preferences.
- INTEGRATION: as duas fixtures completas (O Cisne Negro / A Maré de
  Chumbo) validam sem achados HIGH/BLOCKER, provando que o mesmo Author
  DNA sustenta dois livros com zero símbolos em comum.
- NEGATIVE: cada mutação isolada produz a categoria de achado exata.

Rodar:
    .venv/Scripts/python.exe -m unittest tests.test_visual_canon -v
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import check_visual_canon as vc  # noqa: E402

FIXTURES = REPO / "tests" / "fixtures" / "visual_narrative"
AUTHOR_TEMPLATE_PATH = REPO / "engine" / "templates" / "AUTHOR_VISUAL_DNA_TEMPLATE.yaml"
CANON_TEMPLATE_PATH = REPO / "engine" / "templates" / "VISUAL_NARRATIVE_CANON_TEMPLATE.yaml"
BEA_DNA_PATH = FIXTURES / "authors" / "bea_halden_fixture" / "AUTHOR_VISUAL_DNA.v1.yaml"
CISNE_RUNTIME = FIXTURES / "runtime_cisne_negro"
MARE_RUNTIME = FIXTURES / "runtime_mare_de_chumbo"
GOLDEN_EDITION_PLANS_PATH = FIXTURES / "golden" / "cisne_negro_edition_plans.json"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def hard(findings: list[dict]) -> list[dict]:
    return [f for f in findings if f["severity"] in ("HIGH", "BLOCKER")]


def categories(findings: list[dict]) -> set[str]:
    return {f["category"] for f in findings}


class TestTemplatesAreContractValid(unittest.TestCase):
    """Templates neutros do motor: só V0 (integridade) e V1 (consistência
    de autora) são exigíveis sem canon narrativo real — ver docstring do
    módulo e o comentário no próprio VISUAL_NARRATIVE_CANON_TEMPLATE.yaml."""

    def test_author_dna_template_is_well_formed_yaml(self):
        dna = load(AUTHOR_TEMPLATE_PATH)
        self.assertEqual(dna.get("kind"), "AuthorVisualDNA")

    def test_canon_template_passes_integrity(self):
        canon = load(CANON_TEMPLATE_PATH)
        findings = vc.check_integrity(canon)
        self.assertEqual(hard(findings), [])

    def test_canon_template_passes_author_consistency_against_author_template(self):
        canon = load(CANON_TEMPLATE_PATH)
        dna = load(AUTHOR_TEMPLATE_PATH)
        findings = vc.check_author_consistency(canon, dna)
        self.assertEqual(hard(findings), [])


class TestFixturesAreClean(unittest.TestCase):
    """SDD Slice 1: 'fixture Cisne -> PASS; fixture Maré -> PASS com o
    mesmo DNA'."""

    def _validate_runtime(self, runtime: Path):
        canon = load(runtime / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        dna = load(BEA_DNA_PATH)
        context = vc.load_context(runtime)
        return vc.validate(canon, dna, context)

    def test_cisne_negro_has_no_hard_findings(self):
        findings = self._validate_runtime(CISNE_RUNTIME)
        self.assertEqual(hard(findings), [], f"achados inesperados: {hard(findings)}")

    def test_mare_de_chumbo_has_no_hard_findings(self):
        findings = self._validate_runtime(MARE_RUNTIME)
        self.assertEqual(hard(findings), [], f"achados inesperados: {hard(findings)}")

    def test_second_book_proves_author_dna_independence(self):
        """A mesma autora sustenta dois livros sem nenhum símbolo em comum —
        prova de não-dependência de cisne/coroa/rosa/vermelho (seção 30.10
        da SDD)."""
        cisne = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        mare = load(MARE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        cisne_labels = {el["label"] for el in cisne["elements"]}
        mare_labels = {el["label"] for el in mare["elements"]}
        self.assertEqual(cisne_labels & mare_labels, set())
        # e os dois usam o MESMO Author DNA pinado
        self.assertEqual(cisne["metadata"]["author_dna"]["author_id"],
                          mare["metadata"]["author_dna"]["author_id"])

    def test_a_third_canon_copying_a_book_symbol_into_author_dna_fails(self):
        dna = load(BEA_DNA_PATH)
        tampered = copy.deepcopy(dna)
        tampered["thesis"].append("o cisne negro, SYM-SWAN, é sempre o dominante")
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        findings = vc.check_author_consistency(canon, tampered)
        self.assertIn("AUTHOR_LAYER_CONTAINS_BOOK_SYMBOL", categories(findings))


class TestAnchorResolution(unittest.TestCase):
    def setUp(self):
        self.context = vc.load_context(CISNE_RUNTIME)

    def test_ledger_event_anchor_resolves_structural_with_chapter(self):
        result = vc.resolve_anchor("LEDGER:EV-19", self.context)
        self.assertTrue(result["ok"])
        self.assertEqual(result["strength"], "STRUCTURAL")
        self.assertEqual(result["chapter"], 19)

    def test_ledger_ground_truth_anchor_resolves_without_chapter(self):
        result = vc.resolve_anchor("LEDGER:GT-A-01", self.context)
        self.assertTrue(result["ok"])
        self.assertIsNone(result["chapter"])

    def test_scene_anchor_resolves_with_first_chapter(self):
        result = vc.resolve_anchor("SCENE:CROWN_REFUSAL", self.context)
        self.assertTrue(result["ok"])
        self.assertEqual(result["strength"], "STRUCTURAL")
        self.assertEqual(result["chapter"], 19)

    def test_turn_anchor_resolves_when_irreversible_turn_present(self):
        result = vc.resolve_anchor("TURN:3", self.context)
        self.assertTrue(result["ok"])
        self.assertEqual(result["chapter"], 3)

    def test_turn_anchor_fails_for_undeclared_chapter(self):
        result = vc.resolve_anchor("TURN:2", self.context)
        self.assertFalse(result["ok"])

    def test_canon_anchor_resolves_as_supported(self):
        result = vc.resolve_anchor("CANON:OBJ-003", self.context)
        self.assertTrue(result["ok"])
        self.assertEqual(result["strength"], "SUPPORTED")

    def test_doc_anchor_resolves_heading_slug(self):
        result = vc.resolve_anchor("DOC:/specs/SYMBOL_BIBLE.md#motif-1-black-swan", self.context)
        self.assertTrue(result["ok"])
        self.assertEqual(result["strength"], "SUPPORTED")

    def test_doc_anchor_fails_for_unknown_slug(self):
        result = vc.resolve_anchor("DOC:/specs/SYMBOL_BIBLE.md#nao-existe", self.context)
        self.assertFalse(result["ok"])

    def test_unresolvable_ledger_anchor_without_causal_ledger_context(self):
        result = vc.resolve_anchor("LEDGER:EV-01", {"bibles": {}})
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "ANCHOR_SOURCE_DISABLED")

    def test_text_anchor_never_resolves_in_slice_1(self):
        result = vc.resolve_anchor("TEXT:1:\"qualquer coisa\"", self.context)
        self.assertFalse(result["ok"])

    def test_malformed_anchor_is_not_a_crash(self):
        result = vc.resolve_anchor(42, self.context)
        self.assertFalse(result["ok"])
        result = vc.resolve_anchor("capitulo 15", self.context)
        self.assertFalse(result["ok"])


class TestChekhovStatuses(unittest.TestCase):
    """Um teste por status do vocabulário fechado (seção 11.5 da SDD)."""

    def setUp(self):
        self.context = vc.load_context(CISNE_RUNTIME)
        self.canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        self.watchlist = load(BEA_DNA_PATH)["generic_trope_watchlist"]

    def _status(self, element):
        return vc.chekhov_status(element, self.canon, self.context, self.watchlist)

    def test_proven(self):
        swan = next(e for e in self.canon["elements"] if e["id"] == "SYM-SWAN")
        status, _ = self._status(swan)
        self.assertEqual(status, "PROVEN")

    def test_supported(self):
        element = {
            "id": "TEST-SUPPORTED", "label": "no watchlist match here",
            "prominence": "SUPPORTING",
            "functions": [{"function": "WORLD", "anchors": ["CANON:OBJ-003"]}],
        }
        status, _ = self._status(element)
        self.assertEqual(status, "SUPPORTED")

    def test_decorative_allowed(self):
        element = {
            "id": "TEST-DECORATIVE", "label": "quiet texture",
            "class": "DECORATIVE_ILLUSTRATION", "prominence": "TEXTURE",
            "functions": [],
        }
        status, _ = self._status(element)
        self.assertEqual(status, "DECORATIVE_ALLOWED")

    def test_unjustified(self):
        element = {
            "id": "TEST-UNJUSTIFIED", "label": "unanchored thing",
            "class": "MOTIF", "prominence": "SUPPORTING",
            "functions": [{"function": "CHARACTER", "anchors": ["LEDGER:EV-999"]}],
        }
        status, info = self._status(element)
        self.assertEqual(status, "UNJUSTIFIED")
        self.assertEqual(info["reason"], "no_resolved_function")

    def test_contradictory(self):
        element = {
            "id": "TEST-CONTRADICTORY", "label": "a skull on the table",
            "class": "MOTIF", "prominence": "SUPPORTING",
            "functions": [{"function": "CHARACTER", "anchors": ["LEDGER:GT-A-01"]}],
        }
        status, info = self._status(element)
        self.assertEqual(status, "CONTRADICTORY")
        self.assertIn("VETO-01", info["vetoes"])

    def test_veto_override_bypasses_contradictory(self):
        element = {
            "id": "TEST-OVERRIDE", "label": "a skull on the table",
            "class": "MOTIF", "prominence": "SUPPORTING", "veto_override": "APR-99",
            "functions": [{"function": "CHARACTER", "anchors": ["LEDGER:GT-A-01"]}],
        }
        status, _ = self._status(element)
        self.assertNotEqual(status, "CONTRADICTORY")

    def test_dominant_requires_two_distinct_chapters(self):
        element = {
            "id": "TEST-DOMINANT-1CH", "label": "single-chapter dominant",
            "class": "MOTIF", "prominence": "DOMINANT",
            "functions": [{"function": "TRANSFORMATION", "anchors": ["SCENE:CROWN_REFUSAL"]}],
        }
        status, info = self._status(element)
        self.assertEqual(status, "UNJUSTIFIED")
        self.assertEqual(info["reason"], "dominant_needs_2_chapters")

    def test_count_greater_than_one_requires_rationale(self):
        element = {
            "id": "TEST-COUNT", "label": "five swans", "class": "MOTIF",
            "prominence": "SUPPORTING", "count": 5,
            "functions": [{"function": "MEMORY", "anchors": ["LEDGER:EV-09"]}],
        }
        status, info = self._status(element)
        self.assertEqual(status, "UNJUSTIFIED")
        self.assertEqual(info["reason"], "count_without_rationale")

    def test_count_with_resolved_rationale_passes(self):
        element = {
            "id": "TEST-COUNT-OK", "label": "five swans", "class": "MOTIF",
            "prominence": "SUPPORTING", "count": 5,
            "count_rationale": {"anchors": ["LEDGER:EV-09"]},
            "functions": [{"function": "MEMORY", "anchors": ["LEDGER:EV-09"]}],
        }
        status, _ = self._status(element)
        self.assertEqual(status, "PROVEN")


class TestAuthorDnaDrift(unittest.TestCase):
    def setUp(self):
        self.dna = load(BEA_DNA_PATH)
        self.canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")

    def test_palette_within_role_range_is_clean(self):
        findings = vc.check_author_consistency(self.canon, self.dna)
        self.assertNotIn("AUTHOR_DNA_DRIFT", categories(findings))

    def test_palette_outside_role_range_flags_drift(self):
        canon = copy.deepcopy(self.canon)
        canon["book_dna"]["palette"]["INK"] = "#FF0000"  # vermelho puro e saturado, fora da faixa de INK
        findings = vc.check_author_consistency(canon, self.dna)
        self.assertIn("AUTHOR_DNA_DRIFT", categories(findings))

    def test_hex_to_hsl_matches_known_values(self):
        lightness, saturation = vc.hex_to_hsl("#FFFFFF")
        self.assertAlmostEqual(lightness, 1.0, places=2)
        self.assertAlmostEqual(saturation, 0.0, places=2)


class TestOverridesAndInvariants(unittest.TestCase):
    def setUp(self):
        self.dna = load(BEA_DNA_PATH)
        self.canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")

    def test_override_of_invariant_is_blocked(self):
        canon = copy.deepcopy(self.canon)
        canon["book_dna"]["role_overrides"] = [
            {"key": "invariants.max_dominant_per_surface", "value": 3,
             "override_reason": "queremos mais destaque"},
        ]
        findings = vc.check_author_consistency(canon, self.dna)
        matches = [f for f in findings if f["category"] == "AUTHOR_INVARIANT_OVERRIDE"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "BLOCKER")

    def test_override_without_reason_is_medium(self):
        canon = copy.deepcopy(self.canon)
        canon["book_dna"]["role_overrides"] = [
            {"key": "defaults.forbid_literal_protagonist_on_cover", "value": False},
        ]
        findings = vc.check_author_consistency(canon, self.dna)
        matches = [f for f in findings if f["category"] == "OVERRIDE_WITHOUT_REASON"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "MEDIUM")

    def test_override_with_reason_and_outside_invariants_is_clean(self):
        canon = copy.deepcopy(self.canon)
        canon["book_dna"]["role_overrides"] = [
            {"key": "defaults.forbid_literal_protagonist_on_cover", "value": False,
             "override_reason": "esta capa usa uma figura aprovada em APR-07.",
             "approval": "APR-07"},
        ]
        findings = vc.check_author_consistency(canon, self.dna)
        self.assertNotIn("AUTHOR_INVARIANT_OVERRIDE", categories(findings))
        self.assertNotIn("OVERRIDE_WITHOUT_REASON", categories(findings))


class TestAuthorDnaTampering(unittest.TestCase):
    def test_matching_pin_is_clean(self):
        dna = load(BEA_DNA_PATH)
        canon = {"metadata": {"author_dna": {"author_id": "bea_halden_fixture", "version": 1,
                                              "sha256": vc.canonical_dna_sha256(dna)}}}
        findings = vc.check_author_consistency(canon, dna)
        self.assertNotIn("AUTHOR_DNA_TAMPERED", categories(findings))

    def test_edited_dna_after_pin_is_tampered(self):
        original = load(BEA_DNA_PATH)
        pinned_sha = vc.canonical_dna_sha256(original)
        tampered = copy.deepcopy(original)
        tampered["color"]["roles"]["PULSE"]["default"] = "#000000"
        canon = {"metadata": {"author_dna": {"author_id": "bea_halden_fixture", "version": 1,
                                              "sha256": pinned_sha}}}
        findings = vc.check_author_consistency(canon, tampered)
        matches = [f for f in findings if f["category"] == "AUTHOR_DNA_TAMPERED"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "BLOCKER")

    def test_status_field_alone_does_not_count_as_tampering(self):
        """metadata.status é a única mutação permitida num DNA pinado
        (seção 27.2 da SDD) — SUPERSEDED não deve disparar TAMPERED."""
        original = load(BEA_DNA_PATH)
        pinned_sha = vc.canonical_dna_sha256(original)
        superseded = copy.deepcopy(original)
        superseded["metadata"]["status"] = "SUPERSEDED"
        canon = {"metadata": {"author_dna": {"author_id": "bea_halden_fixture", "version": 1,
                                              "sha256": pinned_sha}}}
        findings = vc.check_author_consistency(canon, superseded)
        self.assertNotIn("AUTHOR_DNA_TAMPERED", categories(findings))


class TestNegativeMutationsProduceExactCategory(unittest.TestCase):
    """Cada mutação isolada precisa produzir a categoria de achado exata
    (SDD, seção 31, Slice 1)."""

    def setUp(self):
        self.dna = load(BEA_DNA_PATH)
        self.context = vc.load_context(CISNE_RUNTIME)

    def test_generic_trope_unjustified(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["elements"].append({
            "id": "SYM-SKULL-PENDANT", "label": "skull pendant", "class": "MOTIF",
            "prominence": "SUPPORTING", "functions": [], "count": 1,
        })
        findings = vc.validate(canon, self.dna, self.context)
        self.assertIn("GENERIC_TROPE_UNJUSTIFIED", categories(findings))

    def test_rose_with_anchor_passes(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        rose = next(e for e in canon["elements"] if e["id"] == "SYM-ROSE")
        status, _ = vc.chekhov_status(rose, canon, self.context, self.dna["generic_trope_watchlist"])
        self.assertEqual(status, "PROVEN")
        findings = vc.validate(canon, self.dna, self.context)
        self.assertNotIn("GENERIC_TROPE_UNJUSTIFIED", categories(findings))

    def test_unjustified_count(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["elements"][0]["count"] = 5
        canon["elements"][0]["count_rationale"] = None
        findings = vc.validate(canon, self.dna, self.context)
        self.assertIn("UNJUSTIFIED_COUNT", categories(findings))

    def test_author_invariant_override(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["book_dna"]["role_overrides"] = [
            {"key": "invariants.chekhov_required", "value": False, "override_reason": "x"},
        ]
        findings = vc.validate(canon, self.dna, self.context)
        self.assertIn("AUTHOR_INVARIANT_OVERRIDE", categories(findings))

    def test_author_dna_drift_hex_out_of_range(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["book_dna"]["palette"]["GROUND"] = "#00FF00"
        findings = vc.validate(canon, self.dna, self.context)
        self.assertIn("AUTHOR_DNA_DRIFT", categories(findings))

    def test_override_without_reason(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["book_dna"]["role_overrides"] = [{"key": "defaults.density.max_secondary_per_surface", "value": 5}]
        findings = vc.validate(canon, self.dna, self.context)
        self.assertIn("OVERRIDE_WITHOUT_REASON", categories(findings))

    def test_visual_overload(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["elements"].append({
            "id": "SYM-EXTRA-DOMINANT", "label": "second dominant thing", "class": "MOTIF",
            "prominence": "DOMINANT", "count": 1,
            "functions": [
                {"function": "CHARACTER", "anchors": ["LEDGER:GT-A-01"]},
                {"function": "TRANSFORMATION", "anchors": ["LEDGER:EV-09"]},
            ],
        })
        canon["compositions"][0]["elements"].append({"element": "SYM-EXTRA-DOMINANT", "prominence": "DOMINANT"})
        findings = vc.validate(canon, self.dna, self.context)
        self.assertIn("VISUAL_OVERLOAD", categories(findings))

    def test_atmosphere_only_prominent(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["elements"].append({
            "id": "SYM-MOOD", "label": "generic fog", "class": "MOTIF",
            "prominence": "SECONDARY", "count": 1,
            "functions": [{"function": "ATMOSPHERE", "anchors": ["LEDGER:EV-03"]}],
        })
        findings = vc.validate(canon, self.dna, self.context)
        self.assertIn("ATMOSPHERE_ONLY_PROMINENT", categories(findings))

    def test_imitation_reference(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["elements"][0]["meaning"] += " no estilo de outra autora conhecida do gênero."
        findings = vc.validate(canon, self.dna, self.context)
        self.assertIn("IMITATION_REFERENCE", categories(findings))

    def test_author_dna_tampered_end_to_end(self):
        original = load(BEA_DNA_PATH)
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["metadata"]["author_dna"]["sha256"] = vc.canonical_dna_sha256(original)
        tampered_dna = copy.deepcopy(original)
        tampered_dna["invariants"]["max_dominant_per_surface"] = 2
        findings = vc.validate(canon, tampered_dna, self.context)
        self.assertIn("AUTHOR_DNA_TAMPERED", categories(findings))


class TestIntegrityCatchesMalformedContracts(unittest.TestCase):
    def test_duplicate_id(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["elements"].append(copy.deepcopy(canon["elements"][0]))
        findings = vc.check_integrity(canon)
        self.assertIn("DUPLICATE_ID", categories(findings))

    def test_invalid_enum(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["elements"][0]["prominence"] = "MAXIMUM"
        findings = vc.check_integrity(canon)
        self.assertIn("INVALID_ENUM", categories(findings))

    def test_malformed_anchor(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["elements"][0]["functions"][0]["anchors"] = ["capitulo 15"]
        findings = vc.check_integrity(canon)
        self.assertIn("MALFORMED_ANCHOR", categories(findings))

    def test_dangling_reference(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["compositions"][0]["elements"].append({"element": "SYM-DOES-NOT-EXIST", "prominence": "TEXTURE"})
        findings = vc.check_integrity(canon)
        self.assertIn("DANGLING_REFERENCE", categories(findings))

    def test_missing_required_metadata(self):
        findings = vc.check_integrity({"apiVersion": "x", "kind": "VisualNarrativeCanon"})
        self.assertIn("CONTRACT_MISSING_FIELD", categories(findings))


class TestEvidenceAndWhyReports(unittest.TestCase):
    def setUp(self):
        self.context = vc.load_context(CISNE_RUNTIME)
        self.canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        self.dna = load(BEA_DNA_PATH)

    def test_evidence_counts_bible_mentions(self):
        # A bíblia está em PT-BR ("cisne"); o termo em inglês só aparece no
        # texto do heading (que vira a chave da seção, não o corpo), então
        # não é contado — comportamento correto do parser por seção.
        report = vc.evidence_report(self.context, ["cisne", "swan"])
        self.assertGreater(report["cisne"]["total"], 0)

    def test_why_report_explains_proven_element(self):
        report = vc.why_report(self.canon, self.context, self.dna, "SYM-SWAN")
        self.assertEqual(report["status"], "PROVEN")
        self.assertEqual(report["id"], "SYM-SWAN")

    def test_why_report_unknown_element(self):
        report = vc.why_report(self.canon, self.context, self.dna, "SYM-NOPE")
        self.assertIn("error", report)


# =====================================================================
# Slice 2 — estado narrativo, artefatos, dualidade, spoiler, aprovações
# =====================================================================

class TestTextAnchorAcrossModes(unittest.TestCase):
    def setUp(self):
        self.context = vc.load_context(CISNE_RUNTIME)

    def test_text_anchor_never_resolves_in_plan(self):
        result = vc.resolve_anchor('TEXT:9:"cláusula quinta"', self.context, mode="plan")
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "TEXT_ANCHOR_REQUIRES_REALIZED_MODE")

    def test_text_anchor_resolves_in_realized_mode(self):
        result = vc.resolve_anchor('TEXT:9:"cláusula quinta"', self.context, mode="realized")
        self.assertTrue(result["ok"])
        self.assertEqual(result["strength"], "STRUCTURAL")
        self.assertEqual(result["chapter"], 9)

    def test_text_anchor_fails_for_absent_chapter(self):
        result = vc.resolve_anchor('TEXT:2:"qualquer coisa"', self.context, mode="realized")
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "CHAPTER_NOT_FOUND")

    def test_text_anchor_fails_for_absent_phrase(self):
        result = vc.resolve_anchor('TEXT:9:"frase que não existe no capítulo"', self.context, mode="realized")
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "TEXT_NOT_FOUND")


class TestSigilProgression(unittest.TestCase):
    """SDD Slice 2: 'projeção 1–9/10–19/20–28' sobre o sigil SIG-SWAN."""

    def setUp(self):
        self.context = vc.load_context(CISNE_RUNTIME)
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        self.canon = canon
        self.sig_swan = next(e for e in canon["elements"] if e["id"] == "SIG-SWAN")

    def test_pristine_before_discovery(self):
        for chapter in (1, 5, 9):
            with self.subTest(chapter=chapter):
                result = vc.project_state(self.sig_swan, chapter, self.context)
                self.assertEqual(result["state"], "PRISTINE")

    def test_cracked_after_discovery_next_chapter(self):
        for chapter in (10, 15, 19):
            with self.subTest(chapter=chapter):
                result = vc.project_state(self.sig_swan, chapter, self.context)
                self.assertEqual(result["state"], "CRACKED")

    def test_crownless_after_refusal_next_chapter(self):
        for chapter in (20, 27, 28):
            with self.subTest(chapter=chapter):
                result = vc.project_state(self.sig_swan, chapter, self.context)
                self.assertEqual(result["state"], "CROWNLESS")

    def test_end_state_matches_final_projection(self):
        report = vc.end_state_report(self.canon, self.context)
        entry = next(r for r in report if r["element"] == "SIG-SWAN")
        self.assertEqual(entry["state"], "CROWNLESS")
        self.assertEqual(entry["memory_state"], "P")

    def test_timeline_report_is_chapter_ordered(self):
        report = vc.timeline_report(self.canon, self.context)
        entry = next(r for r in report if r["element"] == "SIG-SWAN")
        effective = [t["effective_chapter"] for t in entry["transitions"]]
        self.assertEqual(effective, [10, 20])


class TestLedgerEventMovedChapterAffectsProjection(unittest.TestCase):
    """SDD Slice 2: 'evento movido de capítulo no ledger -> projeção
    acompanha sem editar canon' — a âncora é o evento, não o número."""

    def test_projection_follows_moved_event_without_touching_canon_file(self):
        context = vc.load_context(CISNE_RUNTIME)
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        sig_swan = next(e for e in canon["elements"] if e["id"] == "SIG-SWAN")

        original_at_10 = vc.project_state(sig_swan, 10, context)
        self.assertEqual(original_at_10["state"], "CRACKED")  # EV-09 (cap.9) + NEXT_CHAPTER

        moved_context = copy.deepcopy(context)
        event = next(e for e in moved_context["causal_ledger"]["events"] if e["id"] == "EV-09")
        event["chapter"] = 11

        still_pristine = vc.project_state(sig_swan, 10, moved_context)
        self.assertEqual(still_pristine["state"], "PRISTINE")  # 11+1=12 > 10, ainda não chegou
        now_cracked = vc.project_state(sig_swan, 12, moved_context)
        self.assertEqual(now_cracked["state"], "CRACKED")

        canon_on_disk = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        self.assertEqual(canon_on_disk, canon, "o canon no disco não deveria mudar")


class TestStateModelInvariants(unittest.TestCase):
    """ST-01..ST-09 (seção 14.3 da SDD), sobre mutações de SIG-SWAN."""

    def setUp(self):
        self.context = vc.load_context(CISNE_RUNTIME)
        self.canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")

    def _sig_swan(self, canon):
        return next(e for e in canon["elements"] if e["id"] == "SIG-SWAN")

    def test_clean_fixture_has_no_state_model_findings(self):
        findings = vc.check_state_model(self.canon, self.context)
        self.assertEqual(findings, [])

    def test_state_model_invalid_two_initials(self):
        canon = copy.deepcopy(self.canon)
        self._sig_swan(canon)["states"][1]["initial"] = True
        findings = vc.check_state_model(canon, self.context)
        self.assertIn("STATE_MODEL_INVALID", categories(findings))

    def test_arbitrary_state_mutation_bare_chapter_trigger(self):
        canon = copy.deepcopy(self.canon)
        self._sig_swan(canon)["transitions"][0]["trigger"] = "15"
        findings = vc.check_state_model(canon, self.context)
        self.assertIn("ARBITRARY_STATE_MUTATION", categories(findings))

    def test_random_sigil_mutation_undeclared_state(self):
        canon = copy.deepcopy(self.canon)
        self._sig_swan(canon)["transitions"][0]["to"] = "GHOST_WING"
        findings = vc.check_state_model(canon, self.context)
        self.assertIn("RANDOM_SIGIL_MUTATION", categories(findings))

    def test_opener_pre_announces_event_without_ack(self):
        canon = copy.deepcopy(self.canon)
        self._sig_swan(canon)["transitions"][0]["display_from"] = "SAME_CHAPTER"
        findings = vc.check_state_model(canon, self.context)
        self.assertIn("OPENER_PRE_ANNOUNCES_EVENT", categories(findings))

    def test_opener_same_chapter_with_ack_is_clean(self):
        canon = copy.deepcopy(self.canon)
        transition = self._sig_swan(canon)["transitions"][0]
        transition["display_from"] = "SAME_CHAPTER"
        transition["spoiler_ack"] = "APR-09"
        findings = vc.check_state_model(canon, self.context)
        self.assertNotIn("OPENER_PRE_ANNOUNCES_EVENT", categories(findings))

    def test_payoff_without_seed(self):
        canon = copy.deepcopy(self.canon)
        # Sem estado S explícito e sem o inicial servir de semente implícita,
        # CROWNLESS (P) fica sem semente.
        self._sig_swan(canon)["states"][0]["memory_state"] = "T"
        findings = vc.check_state_model(canon, self.context)
        self.assertIn("PAYOFF_WITHOUT_SEED", categories(findings))

    def test_state_cycle_without_cause(self):
        canon = copy.deepcopy(self.canon)
        self._sig_swan(canon)["transitions"].append(
            {"from": "CROWNLESS", "to": "PRISTINE", "trigger": "LEDGER:EV-27"})
        findings = vc.check_state_model(canon, self.context)
        self.assertIn("STATE_CYCLE_WITHOUT_CAUSE", categories(findings))

    def test_reversible_cycle_is_allowed(self):
        canon = copy.deepcopy(self.canon)
        self._sig_swan(canon)["transitions"].append(
            {"from": "CROWNLESS", "to": "PRISTINE", "trigger": "LEDGER:EV-27", "reversible": True})
        findings = vc.check_state_model(canon, self.context)
        self.assertNotIn("STATE_CYCLE_WITHOUT_CAUSE", categories(findings))

    def test_state_order_violation(self):
        canon = copy.deepcopy(self.canon)
        sig = self._sig_swan(canon)
        sig["transitions"][0]["trigger"] = "SCENE:CROWN_REFUSAL"   # cap. 19
        sig["transitions"][1]["trigger"] = "LEDGER:EV-09"          # cap. 9, depois de 19 no caminho
        findings = vc.check_state_model(canon, self.context)
        self.assertIn("STATE_ORDER_VIOLATION", categories(findings))

    def test_missing_visual_description_breaks_constraint(self):
        canon = copy.deepcopy(self.canon)
        self._sig_swan(canon)["states"][1]["visual_description"] = ""
        findings = vc.check_state_model(canon, self.context)
        self.assertIn("STATE_BREAKS_CONSTRAINT", categories(findings))

    def test_state_differs_only_by_color(self):
        canon = copy.deepcopy(self.canon)
        sig = self._sig_swan(canon)
        sig["states"][0]["visual_description"] = "Cisne dourado de perfil."
        sig["states"][1]["visual_description"] = "Cisne prateado de perfil."
        findings = vc.check_state_model(canon, self.context)
        self.assertIn("STATE_DIFFERS_ONLY_BY_COLOR", categories(findings))

    def test_reading_layer_mutation_guard(self):
        canon = copy.deepcopy(self.canon)
        self._sig_swan(canon)["states"][0]["role"] = "BODY"
        findings = vc.check_state_model(canon, self.context)
        matches = [f for f in findings if f["category"] == "READING_LAYER_MUTATION"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "BLOCKER")

    def test_trigger_not_realized_only_in_realized_mode(self):
        canon = copy.deepcopy(self.canon)
        context = copy.deepcopy(self.context)
        event = next(e for e in context["causal_ledger"]["events"] if e["id"] == "EV-09")
        event["status"] = "PLANNED"
        plan_findings = vc.check_state_model(canon, context, mode="plan")
        self.assertNotIn("TRIGGER_NOT_REALIZED", categories(plan_findings))
        realized_findings = vc.check_state_model(canon, context, mode="realized")
        self.assertIn("TRIGGER_NOT_REALIZED", categories(realized_findings))


class TestVisualRetcon(unittest.TestCase):
    """ST-08: transições de estados REALIZED são imutáveis contra o
    snapshot FREEZE."""

    def setUp(self):
        self.canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")

    def test_changed_realized_element_against_baseline_is_retcon(self):
        canon = copy.deepcopy(self.canon)
        baseline = copy.deepcopy(self.canon)
        for doc in (canon, baseline):
            swan = next(e for e in doc["elements"] if e["id"] == "SYM-SWAN")
            swan["status"] = "REALIZED"
        canon_swan = next(e for e in canon["elements"] if e["id"] == "SYM-SWAN")
        canon_swan["meaning"] = "Outra coisa completamente diferente."
        findings = vc.check_baseline_retcon(canon, baseline)
        matches = [f for f in findings if f["category"] == "VISUAL_RETCON"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "BLOCKER")

    def test_promotion_from_planned_to_realized_is_not_retcon(self):
        baseline = copy.deepcopy(self.canon)  # ainda PLANNED
        canon = copy.deepcopy(self.canon)
        swan = next(e for e in canon["elements"] if e["id"] == "SYM-SWAN")
        swan["status"] = "REALIZED"
        findings = vc.check_baseline_retcon(canon, baseline)
        self.assertNotIn("VISUAL_RETCON", categories(findings))

    def test_no_baseline_means_no_check(self):
        findings = vc.check_baseline_retcon(self.canon, None)
        self.assertEqual(findings, [])


class TestArtifactRules(unittest.TestCase):
    """Seção 19.2 da SDD, sobre o artefato ART-CONTRACT."""

    def setUp(self):
        self.context = vc.load_context(CISNE_RUNTIME)
        self.canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")

    def _art(self, canon):
        return next(e for e in canon["elements"] if e["id"] == "ART-CONTRACT")

    def test_clean_fixture_has_no_artifact_findings_in_plan(self):
        findings = vc.check_artifacts(self.canon, self.context, mode="plan")
        self.assertEqual(findings, [])

    def test_clean_fixture_has_no_artifact_findings_in_realized(self):
        findings = vc.check_artifacts(self.canon, self.context, mode="realized")
        self.assertEqual(findings, [])

    def test_canon_ref_must_resolve(self):
        canon = copy.deepcopy(self.canon)
        self._art(canon)["canon_ref"] = "LEDGER:EV-999"
        findings = vc.check_artifacts(canon, self.context, mode="plan")
        self.assertIn("VISUAL_INVENTS_FACT", categories(findings))

    def test_missing_in_world_owner(self):
        canon = copy.deepcopy(self.canon)
        del self._art(canon)["in_world_owner"]
        findings = vc.check_artifacts(canon, self.context, mode="plan")
        self.assertIn("ARTIFACT_OWNER_UNKNOWN", categories(findings))

    def test_unresolved_quote_is_fine_while_planning(self):
        canon = copy.deepcopy(self.canon)
        self._art(canon)["content"]["quotes"] = ['TEXT:9:"frase que não existe"']
        findings = vc.check_artifacts(canon, self.context, mode="plan")
        self.assertNotIn("VISUAL_INVENTS_FACT", categories(findings))

    def test_unresolved_quote_fails_once_realized(self):
        canon = copy.deepcopy(self.canon)
        self._art(canon)["content"]["quotes"] = ['TEXT:9:"frase que não existe"']
        findings = vc.check_artifacts(canon, self.context, mode="realized")
        self.assertIn("VISUAL_INVENTS_FACT", categories(findings))

    def test_artifact_before_first_appearance(self):
        canon = copy.deepcopy(self.canon)
        art = self._art(canon)
        art["placement"]["anchor"] = 'TEXT:3:"arrancou uma única rosa"'  # cap. 3, antes do cap. 9
        findings = vc.check_artifacts(canon, self.context, mode="realized")
        self.assertIn("ARTIFACT_BEFORE_FIRST_APPEARANCE", categories(findings))

    def test_artifact_illegible_below_kdp_floor(self):
        canon = copy.deepcopy(self.canon)
        self._art(canon)["accessibility"]["min_text_pt"] = 5
        findings = vc.check_artifacts(canon, self.context, mode="plan")
        self.assertIn("ARTIFACT_ILLEGIBLE", categories(findings))

    def test_invalid_artifact_type(self):
        canon = copy.deepcopy(self.canon)
        self._art(canon)["artifact_type"] = "SELFIE"
        findings = vc.check_artifacts(canon, self.context, mode="plan")
        self.assertIn("INVALID_ENUM", categories(findings))


class TestCandidateLeak(unittest.TestCase):
    """VP-08: candidato != canon — nenhum id CAND-* pode ser citado num
    canon aprovado."""

    def test_clean_canon_has_no_candidate_leak(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        findings = vc.check_integrity(canon)
        self.assertNotIn("CANDIDATE_CONSUMED", categories(findings))

    def test_candidate_id_referenced_anywhere_in_canon_is_flagged(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        canon["elements"][0]["meaning"] += " (ver candidato CAND-07)"
        findings = vc.check_integrity(canon)
        self.assertIn("CANDIDATE_CONSUMED", categories(findings))


class TestDualityRules(unittest.TestCase):
    """Seção 19.5 da SDD — DJ-02, DJ-03, DJ-04 (DJ-01/05 dependem de
    resolução de edição e ficam para o Slice 3)."""

    def setUp(self):
        self.dna = load(BEA_DNA_PATH)
        self.context = vc.load_context(CISNE_RUNTIME)
        self.canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")

    def test_clean_duality_has_no_findings(self):
        findings = vc.check_duality(self.canon, self.dna, self.context)
        self.assertEqual(findings, [])

    def test_unresolved_duality_anchor_is_unjustified(self):
        canon = copy.deepcopy(self.canon)
        canon["book_dna"]["duality"]["anchors"] = ["LEDGER:GT-DOES-NOT-EXIST"]
        findings = vc.check_duality(canon, self.dna, self.context)
        self.assertIn("UNJUSTIFIED", categories(findings))

    def test_duality_without_shared_element(self):
        canon = copy.deepcopy(self.canon)
        hidden = next(c for c in canon["compositions"] if c["id"] == "COMP-CASE-HIDDEN")
        hidden["elements"] = [{"element": "SYM-ROSE", "prominence": "DOMINANT"}]
        findings = vc.check_duality(canon, self.dna, self.context)
        self.assertIn("DUALITY_WITHOUT_SHARED_ELEMENT", categories(findings))

    def test_hidden_surface_spoiler_over_ceiling(self):
        canon = copy.deepcopy(self.canon)
        crown = next(e for e in canon["elements"] if e["id"] == "SYM-CROWN")
        crown["exposure"] = {"spoiler_level": "HIGH"}
        findings = vc.check_duality(canon, self.dna, self.context)
        self.assertIn("HIDDEN_SURFACE_SPOILER", categories(findings))


class TestEffectiveRevealDerivation(unittest.TestCase):
    def test_derives_reveal_from_ground_truth_reader_access(self):
        context = vc.load_context(CISNE_RUNTIME)
        element = {"functions": [{"function": "CHARACTER", "anchors": ["LEDGER:GT-A-01"]}], "exposure": {}}
        reveal = vc.effective_reveal(element, context)
        self.assertTrue(reveal["ok"])
        self.assertEqual(reveal["chapter"], 19)  # GT-A-01.reader_access.from_event == EV-19

    def test_no_reveal_when_no_gt_anchor_and_no_declared_reveal(self):
        context = vc.load_context(CISNE_RUNTIME)
        element = {"functions": [{"function": "WORLD", "anchors": ["CANON:OBJ-003"]}], "exposure": {}}
        self.assertIsNone(vc.effective_reveal(element, context))


class TestSpoilerSafetyRules(unittest.TestCase):
    """Seção 26.1 da SDD."""

    def setUp(self):
        self.dna = load(BEA_DNA_PATH)
        self.context = vc.load_context(CISNE_RUNTIME)
        self.canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")

    def test_clean_fixture_has_no_spoiler_findings(self):
        findings = vc.check_spoiler_safety(self.canon, self.dna, self.context)
        self.assertEqual(findings, [])

    def test_core_spoiler_on_public_surface_is_blocker(self):
        canon = copy.deepcopy(self.canon)
        swan = next(e for e in canon["elements"] if e["id"] == "SYM-SWAN")
        swan["exposure"] = {"spoiler_level": "CORE"}
        findings = vc.check_spoiler_safety(canon, self.dna, self.context)
        matches = [f for f in findings if f["category"] == "SURFACE_SPOILER"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "BLOCKER")

    def test_spoiler_unanchored(self):
        canon = copy.deepcopy(self.canon)
        rose = next(e for e in canon["elements"] if e["id"] == "SYM-ROSE")
        rose["exposure"] = {"spoiler_level": "MEDIUM"}
        front = next(c for c in canon["compositions"] if c["id"] == "COMP-FRONT")
        front["elements"].append({"element": "SYM-ROSE", "prominence": "SUPPORTING"})
        findings = vc.check_spoiler_safety(canon, self.dna, self.context)
        self.assertIn("SPOILER_UNANCHORED", categories(findings))

    def test_premature_exposure_with_explicit_reveal(self):
        canon = copy.deepcopy(self.canon)
        plate = next(c for c in canon["compositions"] if c["id"] == "COMP-CONTRACT-PLATE")
        plate["chapter"] = 5  # ART-CONTRACT (reveal cap. 9) exposto antes da hora
        findings = vc.check_spoiler_safety(canon, self.dna, self.context)
        self.assertIn("PREMATURE_EXPOSURE", categories(findings))

    def test_premature_exposure_derived_from_reader_access(self):
        canon = copy.deepcopy(self.canon)
        canon["elements"].append({
            "id": "SYM-TEST-DERIVED", "label": "derived reveal test", "class": "MOTIF",
            "prominence": "SUPPORTING", "count": 1,
            "functions": [{"function": "CHARACTER", "anchors": ["LEDGER:GT-A-01"]}],
            "exposure": {"spoiler_level": "MEDIUM"},
        })
        front = next(c for c in canon["compositions"] if c["id"] == "COMP-FRONT")
        front["elements"].append({"element": "SYM-TEST-DERIVED", "prominence": "SUPPORTING"})
        findings = vc.check_spoiler_safety(canon, self.dna, self.context)
        self.assertIn("PREMATURE_EXPOSURE", categories(findings))

    def test_declared_spoiler_none_is_never_gated(self):
        # SYM-SWAN cita LEDGER:GT-A-01 (reader_access em EV-19) mas declara
        # spoiler_level: NONE — presença visual != exposição do segredo.
        findings = vc.check_spoiler_safety(self.canon, self.dna, self.context)
        self.assertEqual([f for f in findings if "SYM-SWAN" in f["evidence"]], [])


class TestApprovalWorkflow(unittest.TestCase):
    """Seção 26.2 da SDD."""

    def setUp(self):
        self.canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")

    def test_matching_approval_file_is_clean(self):
        findings = vc.check_approvals(self.canon, CISNE_RUNTIME)
        self.assertEqual([f for f in findings if f["evidence"] == "COMP-FRONT"], [])

    def test_stale_approval_after_mutation(self):
        canon = copy.deepcopy(self.canon)
        comp = next(c for c in canon["compositions"] if c["id"] == "COMP-FRONT")
        comp["atmosphere"] = "Mudança não aprovada."
        findings = vc.check_approvals(canon, CISNE_RUNTIME)
        matches = [f for f in findings if f["category"] == "APPROVAL_STALE"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "HIGH")

    def test_pending_approval_without_declared_id(self):
        # SYM-SWAN exige aprovação mas não declara approval.id nem tem arquivo.
        findings = vc.check_approvals(self.canon, CISNE_RUNTIME)
        matches = [f for f in findings if f["evidence"] == "SYM-SWAN"]
        self.assertTrue(any(f["category"] == "APPROVAL_MISSING" for f in matches))

    def test_no_runtime_skips_approval_checks_entirely(self):
        findings = vc.check_approvals(self.canon, None)
        self.assertEqual(findings, [])

    def test_canonical_block_hash_is_deterministic(self):
        comp = next(c for c in self.canon["compositions"] if c["id"] == "COMP-FRONT")
        first = vc.canonical_block_sha256(comp)
        second = vc.canonical_block_sha256(copy.deepcopy(comp))
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)


class TestFullPipelineWithRuntimeAndApprovals(unittest.TestCase):
    """Roda validate() com runtime (liga V9) — precisa continuar limpo de
    achados HIGH/BLOCKER: aprovação pendente é MEDIUM, não bloqueia."""

    def test_clean_fixture_stays_hard_clean_with_approvals_engaged(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        dna = load(BEA_DNA_PATH)
        context = vc.load_context(CISNE_RUNTIME)
        findings = vc.validate(canon, dna, context, runtime=CISNE_RUNTIME)
        self.assertEqual(hard(findings), [], f"achados inesperados: {hard(findings)}")

    def test_clean_fixture_is_hard_clean_in_realized_mode(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        dna = load(BEA_DNA_PATH)
        context = vc.load_context(CISNE_RUNTIME)
        findings = vc.validate(canon, dna, context, mode="realized")
        self.assertEqual(hard(findings), [], f"achados inesperados: {hard(findings)}")


class TestSlice1ExitCriteriaStillHold(unittest.TestCase):
    """SDD Slice 2 exit criteria: 'Slice 1 intacto; --why SYM-SWAN produz o
    bloco de explicação da seção 25' — depois de todas as adições."""

    def test_why_report_still_explains_swan(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        dna = load(BEA_DNA_PATH)
        context = vc.load_context(CISNE_RUNTIME)
        report = vc.why_report(canon, context, dna, "SYM-SWAN")
        self.assertEqual(report["status"], "PROVEN")
        self.assertEqual(report["id"], "SYM-SWAN")
        self.assertEqual(len(report["functions"]), 3)


# =====================================================================
# Slice 3 — edições: capacidades, fallbacks, plano, geometria, collector
# =====================================================================

def _cisne_setup():
    canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
    capabilities = load(vc.DEFAULT_CAPABILITIES_PATH)
    print_geometry = load(vc.DEFAULT_PRINT_GEOMETRY_PATH)
    print_spec = load(CISNE_RUNTIME / "layout" / "PRINT_SPEC.yaml")["spec"]
    printer_profile = load(CISNE_RUNTIME / "layout" / "PRINTER_PROFILE.yaml")
    return canon, capabilities, print_geometry, print_spec, printer_profile


class TestGoldenEditionPlans(unittest.TestCase):
    """SDD Slice 3: 'golden dos 4 planos'."""

    def test_all_four_targets_match_golden(self):
        canon, capabilities, _pg, _ps, printer_profile = _cisne_setup()
        golden = json.loads(GOLDEN_EDITION_PLANS_PATH.read_text(encoding="utf-8"))
        for target in vc.EDITION_TARGETS:
            with self.subTest(target=target):
                plan = vc.resolve_edition_plan(canon, capabilities, target, printer_profile)
                self.assertEqual(plan, golden[target],
                                  f"plano de {target} divergiu do golden — regressão de design "
                                  "once/render by edition (VP-03), ou golden precisa ser regravado "
                                  "deliberadamente.")


class TestEditionPlanDeterminism(unittest.TestCase):
    """SDD Slice 3: 'determinismo (duas execuções, mesmo sha256)'."""

    def test_two_resolutions_produce_identical_plan_and_hash(self):
        canon, capabilities, _pg, _ps, printer_profile = _cisne_setup()
        for target in vc.EDITION_TARGETS:
            with self.subTest(target=target):
                plan_a = vc.resolve_edition_plan(canon, capabilities, target, printer_profile)
                plan_b = vc.resolve_edition_plan(copy.deepcopy(canon), capabilities, target,
                                                  copy.deepcopy(printer_profile))
                self.assertEqual(plan_a, plan_b)
                self.assertEqual(vc.canonical_block_sha256(plan_a), vc.canonical_block_sha256(plan_b))


class TestSurfaceMapping(unittest.TestCase):
    def setUp(self):
        self.canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")

    def _comp(self, comp_id):
        return next(c for c in self.canon["compositions"] if c["id"] == comp_id)

    def test_front_cover_maps_per_target(self):
        front = self._comp("COMP-FRONT")
        expected = {
            "kindle_ebook": "MARKETING_COVER", "kdp_paperback": "FRONT_COVER",
            "kdp_hardcover": "CASE_FRONT", "collector": "DUST_JACKET_FRONT",
        }
        for target, mapped in expected.items():
            with self.subTest(target=target):
                surface, note = vc.resolve_composition_surface(front, target)
                self.assertEqual(surface, mapped)
                self.assertIsNone(note)

    def test_hidden_truth_omitted_everywhere_except_collector(self):
        hidden = self._comp("COMP-CASE-HIDDEN")
        for target in ("kindle_ebook", "kdp_paperback", "kdp_hardcover"):
            with self.subTest(target=target):
                surface, note = vc.resolve_composition_surface(hidden, target)
                self.assertIsNone(surface)
                self.assertIn("DJ-01/05", note)
        surface, note = vc.resolve_composition_surface(hidden, "collector")
        self.assertEqual(surface, "CASE_FRONT")
        self.assertIsNone(note)

    def test_edge_only_exists_in_collector(self):
        edge = self._comp("COMP-EDGE")
        for target in ("kindle_ebook", "kdp_paperback", "kdp_hardcover"):
            surface, _note = vc.resolve_composition_surface(edge, target)
            self.assertIsNone(surface)
        surface, _note = vc.resolve_composition_surface(edge, "collector")
        self.assertEqual(surface, "EDGE_FORE")


class TestFinishIntentResolution(unittest.TestCase):
    """15.3 da SDD — a escada determinística, por finish_intent real da
    fixture, contra os quatro alvos."""

    def setUp(self):
        self.canon, self.capabilities, _pg, _ps, self.printer_profile = _cisne_setup()

    def _fi(self, fi_id):
        return next(f for f in self.canon["finish_intents"] if f["id"] == fi_id)

    def test_title_foil_omits_on_kindle_and_paperback_simulates_on_hardcover_physical_on_collector(self):
        title = self._fi("FI-TITLE")
        self.assertEqual(vc.resolve_finish_intent(title, "kindle_ebook", self.capabilities)["level"], "OMIT")
        self.assertEqual(vc.resolve_finish_intent(title, "kdp_paperback", self.capabilities)["level"], "OMIT")
        hc = vc.resolve_finish_intent(title, "kdp_hardcover", self.capabilities)
        self.assertEqual(hc["level"], "SIMULATED")
        self.assertEqual(hc["effect"], "SIMULATED_METALLIC_PRINT")
        collector = vc.resolve_finish_intent(title, "collector", self.capabilities, self.printer_profile)
        self.assertEqual(collector["level"], "PHYSICAL")
        self.assertEqual(collector["effect"], "METALLIC_FOIL")

    def test_feathers_simulate_on_print_targets_omit_on_kindle(self):
        feathers = self._fi("FI-FEATHERS")
        self.assertEqual(vc.resolve_finish_intent(feathers, "kindle_ebook", self.capabilities)["level"], "OMIT")
        for target in ("kdp_paperback", "kdp_hardcover"):
            result = vc.resolve_finish_intent(feathers, target, self.capabilities)
            self.assertEqual(result["level"], "SIMULATED")
            self.assertEqual(result["effect"], "CONTRAST_SIMULATION")

    def test_edge_is_collector_only_shortcut(self):
        edge = self._fi("FI-EDGE")
        for target in ("kindle_ebook", "kdp_paperback", "kdp_hardcover"):
            result = vc.resolve_finish_intent(edge, target, self.capabilities)
            self.assertEqual(result["level"], "OMIT")
            self.assertEqual(result["reason"], "COLLECTOR_ONLY fora do alvo collector")
        collector = vc.resolve_finish_intent(edge, "collector", self.capabilities, self.printer_profile)
        self.assertEqual(collector["level"], "PHYSICAL")

    def test_collector_without_printer_profile_never_reaches_physical(self):
        # FI-TITLE tem um fallback SIMULATED (SIMULATED_METALLIC_PRINT): sem
        # perfil de gráfica, degrada graciosamente para ele — nunca PHYSICAL,
        # e sem precisar sinalizar printer_unconfirmed (o fallback resolveu).
        title = self._fi("FI-TITLE")
        result = vc.resolve_finish_intent(title, "collector", self.capabilities, printer_profile=None)
        self.assertEqual(result["level"], "SIMULATED")
        self.assertFalse(result["printer_unconfirmed"])

        # FI-EDGE não tem NENHUM fallback (19.4: sem simulação honesta de
        # borda pintada) — sem perfil confirmando, esgota a escada e só
        # então sinaliza printer_unconfirmed.
        edge = self._fi("FI-EDGE")
        result = vc.resolve_finish_intent(edge, "collector", self.capabilities, printer_profile=None)
        self.assertNotEqual(result["level"], "PHYSICAL")
        self.assertTrue(result["printer_unconfirmed"])


class TestPaperbackGeometryHandVerified(unittest.TestCase):
    """SDD Slice 3: 'geometria paperback 6×9, 300 páginas creme conferida
    à mão (spine = 300 × 0,0025 = 0,75\", full_width = 13,0\", full_height
    = 9,25\")'."""

    def test_hand_verified_numbers(self):
        _canon, _cap, print_geometry, print_spec, _pp = _cisne_setup()
        geometry, findings = vc.compute_paperback_geometry(print_spec, print_geometry)
        self.assertEqual(findings, [])
        self.assertEqual(geometry["spine_in"], 0.75)
        self.assertEqual(geometry["full_width_in"], 13.0)
        self.assertEqual(geometry["full_height_in"], 9.25)
        self.assertTrue(geometry["spine_text_allowed"])  # 300 >= 79


class TestHardcoverGeometryBlocked(unittest.TestCase):
    """Risco registrado na SDD: 'geometria hardcover incompleta -> TO_VERIFY
    explícito, teste garante recusa' — isto é o comportamento CORRETO
    enquanto OQ-8/D-V8 não forem resolvidos por um humano."""

    def test_hardcover_geometry_refuses_with_current_template(self):
        _canon, _cap, print_geometry, print_spec, _pp = _cisne_setup()
        geometry, findings = vc.compute_hardcover_geometry(print_spec, print_geometry)
        self.assertIsNone(geometry)
        self.assertIn("MANUFACTURING_FACT_UNVERIFIED", categories(findings))


class TestCollectorGeometry(unittest.TestCase):
    def test_with_printer_profile_computes(self):
        _canon, _cap, _pg, print_spec, printer_profile = _cisne_setup()
        geometry, findings = vc.compute_collector_geometry(print_spec, printer_profile)
        self.assertEqual(findings, [])
        self.assertEqual(geometry["spine_in"], 0.75)

    def test_without_printer_profile_is_unconfirmed(self):
        _canon, _cap, _pg, print_spec, _pp = _cisne_setup()
        geometry, findings = vc.compute_collector_geometry(print_spec, None)
        self.assertIsNone(geometry)
        self.assertIn("PRINTER_UNCONFIRMED", categories(findings))


class TestKindleGeometry(unittest.TestCase):
    def test_kindle_geometry_is_fixed_pixels(self):
        _canon, _cap, print_geometry, _ps, _pp = _cisne_setup()
        geometry, findings = vc.compute_kindle_geometry(print_geometry)
        self.assertEqual(findings, [])
        self.assertEqual(geometry["width_px"], 1600)
        self.assertEqual(geometry["height_px"], 2560)


class TestNegativeEditionFindings(unittest.TestCase):
    """Cada mutação isolada produz a categoria de achado exata (SDD, Slice 3)."""

    def setUp(self):
        self.canon, self.capabilities, self.print_geometry, self.print_spec, self.printer_profile = _cisne_setup()

    def test_essential_unrenderable(self):
        fi = {"id": "FI-TEST-ESSENTIAL", "cost_class": "ESSENTIAL",
              "preferred_effect": "METALLIC_FOIL", "fallbacks": []}
        result = vc.resolve_finish_intent(fi, "kdp_paperback", self.capabilities)
        self.assertEqual(result["level"], "BLOCKER")
        plan = {"compositions": [], "finish_intents": [{"finish_intent": "FI-TEST-ESSENTIAL", **result}]}
        findings = vc.check_edition_plan(self.canon, "kdp_paperback", plan, {})
        matches = [f for f in findings if f["category"] == "ESSENTIAL_UNRENDERABLE"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "BLOCKER")

    def test_hidden_truth_exposed_defensive_check(self):
        # Constrói um plano à mão (bypassando o resolver) para provar que a
        # checagem é uma segunda linha de defesa, não só confiança cega no
        # resolver que já a impede por construção.
        plan = {"compositions": [{"composition": "COMP-CASE-HIDDEN", "reading_layer": "HIDDEN_TRUTH",
                                   "status": "INCLUDED"}], "finish_intents": []}
        findings = vc.check_edition_plan(self.canon, "kdp_paperback", plan, {})
        matches = [f for f in findings if f["category"] == "HIDDEN_TRUTH_EXPOSED"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "BLOCKER")

    def test_hidden_truth_included_in_collector_is_not_exposed(self):
        plan = {"compositions": [{"composition": "COMP-CASE-HIDDEN", "reading_layer": "HIDDEN_TRUTH",
                                   "status": "INCLUDED"}], "finish_intents": []}
        findings = vc.check_edition_plan(self.canon, "collector", plan, {})
        self.assertNotIn("HIDDEN_TRUTH_EXPOSED", categories(findings))

    def test_edition_changes_meaning(self):
        canon = copy.deepcopy(self.canon)
        canon["book_dna"]["role_overrides"] = [
            {"edition": "kdp_hardcover", "key": "elements.SYM-SWAN.meaning",
             "value": "outra coisa", "override_reason": "tentativa inválida"},
        ]
        findings = vc.check_edition_semantic_stability(canon, "kdp_hardcover")
        matches = [f for f in findings if f["category"] == "EDITION_CHANGES_MEANING"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "BLOCKER")

    def test_edition_changes_meaning_scoped_to_its_own_target(self):
        canon = copy.deepcopy(self.canon)
        canon["book_dna"]["role_overrides"] = [
            {"edition": "collector", "key": "elements.SYM-SWAN.meaning", "value": "x"},
        ]
        # Um override para 'collector' não deveria disparar ao checar kdp_hardcover.
        findings = vc.check_edition_semantic_stability(canon, "kdp_hardcover")
        self.assertEqual(findings, [])

    def test_page_count_unknown(self):
        spec = copy.deepcopy(self.print_spec)
        spec["kdp_paperback"]["page_count"] = None
        _geometry, findings = vc.compute_paperback_geometry(spec, self.print_geometry)
        self.assertIn("PAGE_COUNT_UNKNOWN", categories(findings))

    def test_manufacturing_fact_unverified_missing_bleed(self):
        geom = copy.deepcopy(self.print_geometry)
        del geom["kdp_paperback"]["bleed_in"]
        _geometry, findings = vc.compute_paperback_geometry(self.print_spec, geom)
        self.assertIn("MANUFACTURING_FACT_UNVERIFIED", categories(findings))

    def test_zone_collides_with_manufacturing(self):
        canon = copy.deepcopy(self.canon)
        spine_comp = next(c for c in canon["compositions"] if c["id"] == "COMP-SPINE")
        spine_comp["elements"][0]["zone"] = [0.0, 0.08, 0.85, 0.092]  # toca a borda esquerda
        geometry, _f = vc.compute_paperback_geometry(self.print_spec, self.print_geometry)
        findings = vc.check_zone_collisions(canon, geometry, self.print_geometry["kdp_paperback"]["fold_variance_in"])
        self.assertIn("ZONE_COLLIDES_WITH_MANUFACTURING", categories(findings))

    def test_clean_spine_zone_has_no_collision(self):
        geometry, _f = vc.compute_paperback_geometry(self.print_spec, self.print_geometry)
        findings = vc.check_zone_collisions(self.canon, geometry,
                                             self.print_geometry["kdp_paperback"]["fold_variance_in"])
        self.assertEqual(findings, [])

    def test_finish_promise_mismatch(self):
        plan = vc.resolve_edition_plan(self.canon, self.capabilities, "kdp_paperback", None)
        findings = vc.check_finish_promise(plan, "Esta edição vem com detalhes em hot foil no título.")
        self.assertIn("FINISH_PROMISE_MISMATCH", categories(findings))

    def test_finish_promise_matching_physical_effect_is_clean(self):
        plan = vc.resolve_edition_plan(self.canon, self.capabilities, "collector", self.printer_profile)
        findings = vc.check_finish_promise(plan, "Esta edição de colecionador vem com foil metálico no título.")
        self.assertEqual(findings, [])

    def test_printer_unconfirmed(self):
        plan = vc.resolve_edition_plan(self.canon, self.capabilities, "collector", None)
        findings = vc.check_edition_plan(self.canon, "collector", plan, {})
        matches = [f for f in findings if f["category"] == "PRINTER_UNCONFIRMED"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "MEDIUM")

    def test_printer_unconfirmed_absent_when_confirmed(self):
        plan = vc.resolve_edition_plan(self.canon, self.capabilities, "collector", self.printer_profile)
        findings = vc.check_edition_plan(self.canon, "collector", plan, {})
        self.assertNotIn("PRINTER_UNCONFIRMED", categories(findings))


class TestFinishIntentChekhov(unittest.TestCase):
    """20.2/22.3 da SDD: todo acabamento aponta para um elemento com
    significado real."""

    def setUp(self):
        self.canon, _cap, _pg, _ps, _pp = _cisne_setup()
        _findings, self.status_map = vc.check_chekhov(self.canon, vc.load_context(CISNE_RUNTIME),
                                                        load(BEA_DNA_PATH))

    def test_clean_finish_intents_have_valid_chekhov(self):
        findings = vc.check_finish_intent_chekhov(self.canon, self.status_map)
        self.assertEqual(findings, [])

    def test_finish_intent_with_unknown_meaning_element(self):
        canon = copy.deepcopy(self.canon)
        canon["finish_intents"][0]["meaning_element"] = "SYM-DOES-NOT-EXIST"
        findings = vc.check_finish_intent_chekhov(canon, self.status_map)
        self.assertIn("FINISH_WITHOUT_CHEKHOV", categories(findings))

    def test_finish_intent_pointing_to_unjustified_element(self):
        canon = copy.deepcopy(self.canon)
        canon["elements"].append({
            "id": "SYM-UNJUSTIFIED", "label": "loose thing", "class": "MOTIF",
            "prominence": "SUPPORTING", "count": 1, "functions": [],
        })
        canon["finish_intents"].append({
            "id": "FI-LOOSE", "target": {"composition": "COMP-FRONT"},
            "semantic_material": "BONE_MATTE", "meaning_element": "SYM-UNJUSTIFIED",
            "preferred_effect": "EMBOSS", "fallbacks": [], "cost_class": "OPTIONAL",
        })
        _findings, status_map = vc.check_chekhov(canon, vc.load_context(CISNE_RUNTIME), load(BEA_DNA_PATH))
        findings = vc.check_finish_intent_chekhov(canon, status_map)
        matches = [f for f in findings if f["evidence"] == "FI-LOOSE"]
        self.assertTrue(matches)


class TestProductionManifest(unittest.TestCase):
    def setUp(self):
        self.canon, self.capabilities, _pg, _ps, self.printer_profile = _cisne_setup()

    def test_manifest_only_applies_to_collector(self):
        plan = vc.resolve_edition_plan(self.canon, self.capabilities, "kdp_paperback", None)
        manifest = vc.build_production_manifest(self.canon, "kdp_paperback", plan, None)
        self.assertIn("error", manifest)

    def test_collector_manifest_only_includes_physical_effects(self):
        plan = vc.resolve_edition_plan(self.canon, self.capabilities, "collector", self.printer_profile)
        manifest = vc.build_production_manifest(self.canon, "collector", plan, self.printer_profile)
        asset_ids = {a["finish_intent"] for a in manifest["assets"]}
        self.assertEqual(asset_ids, {"FI-TITLE", "FI-FEATHERS", "FI-EDGE"})  # todas PHYSICAL com o perfil confirmado
        for asset in manifest["assets"]:
            self.assertIsNotNone(asset["mask_rules"])
            self.assertTrue(asset["finish_intent"])  # toda máscara aponta para uma finish_intent

    def test_collector_manifest_without_printer_profile_has_no_physical_assets(self):
        plan = vc.resolve_edition_plan(self.canon, self.capabilities, "collector", None)
        manifest = vc.build_production_manifest(self.canon, "collector", plan, None)
        self.assertEqual(manifest["assets"], [])


class TestVisualNarrativeThesisStructural(unittest.TestCase):
    """SDD Slice 3 exit criteria: 'tese estrutural
    VISUAL_NARRATIVE_THESIS_STRUCTURAL = PROVEN (seção 34.3)' — o pipeline
    completo (V0-V9 + edição) roda limpo de HIGH/BLOCKER para os quatro
    alvos da fixture principal."""

    def test_full_pipeline_clean_across_all_targets(self):
        canon, capabilities, _pg, _ps, printer_profile = _cisne_setup()
        dna = load(BEA_DNA_PATH)
        context = vc.load_context(CISNE_RUNTIME)
        book_findings = vc.validate(canon, dna, context, runtime=CISNE_RUNTIME)
        self.assertEqual(hard(book_findings), [], f"achados de canon: {hard(book_findings)}")
        _chekhov, status_map = vc.check_chekhov(canon, context, dna)
        for target in vc.EDITION_TARGETS:
            with self.subTest(target=target):
                plan = vc.resolve_edition_plan(canon, capabilities, target, printer_profile)
                edition_findings = vc.check_edition_plan(canon, target, plan, status_map)
                self.assertEqual(hard(edition_findings), [],
                                  f"achados de edição em {target}: {hard(edition_findings)}")


# =====================================================================
# Slice 4 — ativos: thumbnail, grayscale, deriva em pixels, proveniência
# =====================================================================
#
# Imagens sintéticas, geradas em diretório temporário (nunca commitadas
# como binário) — calibradas empiricamente contra as próprias funções antes
# de virar asserção de teste, como TEXT_QUALITY_DEFAULTS.yaml foi calibrado
# contra um manuscrito real. Ver docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_CALIBRATION.md
# para a medição adicional sobre capas reais do repositório (eva, loja).

from PIL import Image, ImageDraw  # noqa: E402
import random  # noqa: E402
import tempfile  # noqa: E402

COVER_W, COVER_H = 400, 640  # mesmo aspecto 1600x2560 da capa real (0,625)
TITLE_ZONE = (0.08, 0.06, 0.92, 0.22)
AUTHOR_ZONE = (0.20, 0.86, 0.80, 0.93)
DOMINANT_ZONE = (0.10, 0.28, 0.90, 0.82)  # mesma zone do elemento DOMINANT na fixture


def _stripes(draw, zone, color, count=6, fill_frac=0.4):
    x0, y0, x1, y1 = [int(v * d) for v, d in zip(zone, (COVER_W, COVER_H, COVER_W, COVER_H))]
    band_h = (y1 - y0) / count
    for i in range(count):
        yy0 = y0 + i * band_h
        yy1 = yy0 + band_h * fill_frac
        draw.rectangle([x0 + 4, yy0, x1 - 4, yy1], fill=color)


def _base_cover(bg=(20, 18, 17), title_color=(240, 235, 225), author_color=(200, 195, 185)):
    """Fundo + tipografia simulada (faixas de alto contraste, sem depender
    de fonte) nas zonas TITLE/AUTHOR reais da fixture."""
    img = Image.new("RGB", (COVER_W, COVER_H), bg)
    draw = ImageDraw.Draw(img)
    _stripes(draw, TITLE_ZONE, title_color)
    _stripes(draw, AUTHOR_ZONE, author_color, count=2, fill_frac=0.5)
    return img


def _good_cover():
    """Passa em todos os critérios: título/autora de alto contraste, um
    único disco claro como ponto focal sobre fundo escuro e quieto."""
    img = _base_cover()
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = [int(v * d) for v, d in zip(DOMINANT_ZONE, (COVER_W, COVER_H, COVER_W, COVER_H))]
    draw.ellipse([x0 + 10, y0 + 10, x1 - 10, y1 - 10], fill=(225, 215, 195))
    return img


def _busy_cover():
    """Mesma capa boa, mas com centenas de formas coloridas espalhadas
    FORA da zona dominante — três focos competindo em vez de um."""
    img = _good_cover()
    draw = ImageDraw.Draw(img)
    dz = [int(v * d) for v, d in zip(DOMINANT_ZONE, (COVER_W, COVER_H, COVER_W, COVER_H))]
    rng = random.Random(7)
    for _ in range(1500):
        x, y = rng.randint(0, COVER_W - 6), rng.randint(0, COVER_H - 6)
        if dz[0] <= x <= dz[2] and dz[1] <= y <= dz[3]:
            continue
        color = rng.choice([(200, 60, 60), (60, 200, 60), (60, 60, 200), (230, 230, 230)])
        draw.rectangle([x, y, x + 5, y + 5], fill=color)
    return img


def _fragmented_dominant_cover():
    """Título/autora legíveis, mas o elemento dominante vira poeira de
    pontos soltos em vez de UMA silhueta — sobrevive mal a 96px."""
    img = _base_cover()
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = [int(v * d) for v, d in zip(DOMINANT_ZONE, (COVER_W, COVER_H, COVER_W, COVER_H))]
    rng = random.Random(3)
    for _ in range(60):
        cx, cy = rng.randint(x0, x1), rng.randint(y0, y1)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(225, 215, 195))
    return img


def _low_contrast_title_cover():
    """Título e autora quase da mesma cor do fundo — ilegível em miniatura."""
    return _base_cover(bg=(110, 108, 106), title_color=(130, 128, 126), author_color=(118, 116, 114))


def _checkerboard_cover():
    """Densidade de borda alta por toda a imagem — clutter puro."""
    img = Image.new("RGB", (COVER_W, COVER_H), (20, 18, 17))
    draw = ImageDraw.Draw(img)
    step = 8
    for y in range(0, COVER_H, step):
        for x in range(0, COVER_W, step):
            if ((x // step) + (y // step)) % 2 == 0:
                draw.rectangle([x, y, x + step, y + step], fill=(230, 220, 200))
    return img


class TestOtsuAndWcagMath(unittest.TestCase):
    def test_wcag_black_on_white_is_maximum_contrast(self):
        ratio = vc.wcag_contrast_ratio((0, 0, 0), (255, 255, 255))
        self.assertAlmostEqual(ratio, 21.0, places=1)

    def test_wcag_identical_colors_is_one(self):
        self.assertAlmostEqual(vc.wcag_contrast_ratio((128, 128, 128), (128, 128, 128)), 1.0, places=6)

    def test_otsu_splits_clean_bimodal_histogram(self):
        # Toda t em [20,229] dá a mesma variância entre classes para este
        # histograma perfeitamente bimodal — o algoritmo fica com o primeiro
        # (t=20, por causa do `>` estrito). O que importa é que o limiar
        # SEPARA CORRETAMENTE as duas classes originais, não seu valor exato.
        values = [20] * 100 + [230] * 100
        threshold = vc.otsu_threshold(values)
        self.assertTrue(all(v <= threshold for v in values if v == 20))
        self.assertTrue(all(v > threshold for v in values if v == 230))


class TestThumbnailGeneration(unittest.TestCase):
    def test_generates_three_widths_with_preserved_aspect(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            image_path = tmp / "cover.jpg"
            _good_cover().save(image_path, "JPEG", quality=95)
            thumbs = vc.generate_thumbnails(image_path, tmp / "thumbnails")
            self.assertEqual(set(thumbs), set(vc.THUMBNAIL_WIDTHS))
            for width, path in thumbs.items():
                self.assertTrue(path.is_file())
                with Image.open(path) as img:
                    self.assertEqual(img.width, width)
                    self.assertAlmostEqual(img.height / img.width, COVER_H / COVER_W, places=1)


class TestTitleAndFocalHeuristics(unittest.TestCase):
    """Calibrado empiricamente (ver script de calibração citado no
    docstring da seção) contra as próprias funções antes de virar limiar."""

    def test_high_contrast_title_passes(self):
        img = _good_cover().resize((160, round(160 * COVER_H / COVER_W)))
        self.assertGreaterEqual(vc.title_contrast_ratio(img, TITLE_ZONE), 0.45)
        ink, bg = vc.ink_and_background(vc.crop_zone(img, TITLE_ZONE))
        self.assertGreaterEqual(vc.wcag_contrast_ratio(ink, bg), 4.5)

    def test_low_contrast_title_fails(self):
        img = _low_contrast_title_cover().resize((160, round(160 * COVER_H / COVER_W)))
        self.assertLess(vc.title_contrast_ratio(img, TITLE_ZONE), 0.45)
        ink, bg = vc.ink_and_background(vc.crop_zone(img, TITLE_ZONE))
        self.assertLess(vc.wcag_contrast_ratio(ink, bg), 4.5)

    def test_single_focal_point_passes(self):
        img = _good_cover().resize((160, round(160 * COVER_H / COVER_W)))
        ratio = vc.focal_point_ratio(img, DOMINANT_ZONE, exclude_zones=[TITLE_ZONE, AUTHOR_ZONE])
        self.assertGreaterEqual(ratio, 1.3)

    def test_three_competing_focal_points_fails(self):
        img = _busy_cover().resize((160, round(160 * COVER_H / COVER_W)))
        ratio = vc.focal_point_ratio(img, DOMINANT_ZONE, exclude_zones=[TITLE_ZONE, AUTHOR_ZONE])
        self.assertLess(ratio, 1.3)

    def test_typography_zones_excluded_from_ambient_measurement(self):
        # Sem exclude_zones, o texto de alto contraste (deliberado) infla
        # a energia de borda "de fora" e derruba injustamente a razão —
        # provando por que o parâmetro existe.
        img = _good_cover().resize((160, round(160 * COVER_H / COVER_W)))
        with_exclusion = vc.focal_point_ratio(img, DOMINANT_ZONE, exclude_zones=[TITLE_ZONE, AUTHOR_ZONE])
        without_exclusion = vc.focal_point_ratio(img, DOMINANT_ZONE)
        self.assertGreater(with_exclusion, without_exclusion)


class TestSilhouetteHeuristic(unittest.TestCase):
    def test_single_clear_shape_passes(self):
        img = _good_cover().resize((96, round(96 * COVER_H / COVER_W)))
        ratio = vc.largest_connected_component_ratio(img, DOMINANT_ZONE)
        self.assertGreaterEqual(ratio, 0.25)

    def test_fragmented_shape_fails(self):
        img = _fragmented_dominant_cover().resize((96, round(96 * COVER_H / COVER_W)))
        ratio = vc.largest_connected_component_ratio(img, DOMINANT_ZONE)
        self.assertLess(ratio, 0.25)


class TestClutterHeuristic(unittest.TestCase):
    def test_quiet_cover_is_below_ceiling(self):
        img = _good_cover().resize((160, round(160 * COVER_H / COVER_W)))
        self.assertLess(vc.clutter_density(img), 0.35)

    def test_checkerboard_exceeds_ceiling(self):
        img = _checkerboard_cover().resize((160, round(160 * COVER_H / COVER_W)))
        self.assertGreaterEqual(vc.clutter_density(img), 0.35)


class TestAuthorDnaDriftPixels(unittest.TestCase):
    def setUp(self):
        self.dna = load(BEA_DNA_PATH)

    def test_small_pulse_area_is_clean(self):
        img = Image.new("RGB", (COVER_W, COVER_H), (18, 17, 16))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, round(COVER_H * 0.94), COVER_W, COVER_H], fill=(90, 14, 28))
        findings = vc.check_author_dna_drift_pixels(img, self.dna)
        self.assertEqual(findings, [])

    def test_excessive_pulse_area_flags_drift(self):
        img = Image.new("RGB", (COVER_W, COVER_H), (18, 17, 16))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, COVER_W, round(COVER_H * 0.4)], fill=(90, 14, 28))
        findings = vc.check_author_dna_drift_pixels(img, self.dna)
        matches = [f for f in findings if f["category"] == "AUTHOR_DNA_DRIFT"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "MEDIUM")


class TestSigilMonochromePixels(unittest.TestCase):
    def _sigil_canon(self, render_asset_name):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        sig = next(e for e in canon["elements"] if e["id"] == "SIG-SWAN")
        sig["states"][0]["render"] = {"mode": "RASTER_1BIT", "asset": f"images/sigils/{render_asset_name}"}
        return canon

    def test_glyph_mode_is_never_inspected(self):
        # A fixture padrão usa render.mode: GLYPH em todos os estados —
        # nada em pixels a checar, mesmo sem nenhum asset no disco.
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        findings = vc.check_sigil_monochrome_pixels(canon, CISNE_RUNTIME)
        self.assertEqual(findings, [])

    def test_true_monochrome_raster_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp)
            asset_dir = runtime / "images" / "sigils"
            asset_dir.mkdir(parents=True)
            img = Image.new("L", (64, 64), 0)
            draw = ImageDraw.Draw(img)
            draw.ellipse([10, 10, 54, 54], fill=255)  # preto/branco puro, sem meio-tom
            img.save(asset_dir / "pristine.png")
            canon = self._sigil_canon("pristine.png")
            findings = vc.check_sigil_monochrome_pixels(canon, runtime)
            self.assertEqual(findings, [])

    def test_gradient_raster_flags_not_monochrome(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp)
            asset_dir = runtime / "images" / "sigils"
            asset_dir.mkdir(parents=True)
            img = Image.new("L", (64, 64))
            for y in range(64):
                for x in range(64):
                    img.putpixel((x, y), (x * 4) % 256)  # gradiente cheio de tons médios
            img.save(asset_dir / "gradient.png")
            canon = self._sigil_canon("gradient.png")
            findings = vc.check_sigil_monochrome_pixels(canon, runtime)
            matches = [f for f in findings if f["category"] == "SIGIL_NOT_MONOCHROME"]
            self.assertTrue(matches)
            self.assertEqual(matches[0]["severity"], "HIGH")


class TestCheckCoverAssetsEndToEnd(unittest.TestCase):
    def setUp(self):
        self.canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        self.dna = load(BEA_DNA_PATH)

    def _run(self, cover_image):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp) / "media" / "outputs" / "cover"
            runtime.mkdir(parents=True)
            image_path = runtime / "BOOK_COVER_KDP.jpg"
            cover_image.save(image_path, "JPEG", quality=95)
            return vc.check_cover_assets(self.canon, self.dna, image_path)

    def test_good_cover_has_no_hard_thumbnail_findings(self):
        findings = self._run(_good_cover())
        hard_findings = hard(findings)
        self.assertEqual(hard_findings, [], f"achados inesperados: {hard_findings}")

    def test_bad_title_contrast_produces_high_finding(self):
        findings = self._run(_low_contrast_title_cover())
        matches = [f for f in findings if f["category"] == "THUMBNAIL_TITLE_ILLEGIBLE"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "HIGH")

    def test_busy_cover_produces_weak_focal_point(self):
        findings = self._run(_busy_cover())
        self.assertIn("THUMBNAIL_WEAK_FOCAL_POINT", categories(findings))

    def test_fragmented_dominant_produces_weak_silhouette(self):
        findings = self._run(_fragmented_dominant_cover())
        self.assertIn("THUMBNAIL_WEAK_SILHOUETTE", categories(findings))

    def test_checkerboard_produces_clutter_finding(self):
        findings = self._run(_checkerboard_cover())
        self.assertIn("THUMBNAIL_CLUTTER", categories(findings))

    def test_thumbnails_are_always_written_regardless_of_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp) / "media" / "outputs" / "cover"
            runtime.mkdir(parents=True)
            image_path = runtime / "BOOK_COVER_KDP.jpg"
            _low_contrast_title_cover().save(image_path, "JPEG", quality=95)
            vc.check_cover_assets(self.canon, self.dna, image_path)
            thumb_dir = runtime.parent / "thumbnails"
            for width in vc.THUMBNAIL_WIDTHS:
                self.assertTrue((thumb_dir / f"BOOK_COVER_KDP_{width}.jpg").is_file())

    def test_missing_image_returns_no_findings_not_a_crash(self):
        findings = vc.check_cover_assets(self.canon, self.dna, Path("does/not/exist.jpg"))
        self.assertEqual(findings, [])


class TestValidateAssetsModeEndToEnd(unittest.TestCase):
    def test_validate_mode_assets_includes_cover_and_sigil_checks(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        dna = load(BEA_DNA_PATH)
        context = vc.load_context(CISNE_RUNTIME)
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "cover.jpg"
            _good_cover().save(image_path, "JPEG", quality=95)
            findings = vc.validate(canon, dna, context, mode="assets", runtime=CISNE_RUNTIME,
                                    cover_image=image_path)
        # a fixture inteira (capa boa + sigils GLYPH, sem raster) deve
        # continuar limpa de HIGH/BLOCKER mesmo com o modo assets ligado
        self.assertEqual(hard(findings), [], f"achados inesperados: {hard(findings)}")

    def test_plan_mode_never_runs_pixel_checks(self):
        canon = load(CISNE_RUNTIME / "canon" / "VISUAL_NARRATIVE_CANON.yaml")
        dna = load(BEA_DNA_PATH)
        context = vc.load_context(CISNE_RUNTIME)
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "cover.jpg"
            _low_contrast_title_cover().save(image_path, "JPEG", quality=95)
            findings = vc.validate(canon, dna, context, mode="plan", runtime=CISNE_RUNTIME,
                                    cover_image=image_path)
        self.assertNotIn("THUMBNAIL_TITLE_ILLEGIBLE", categories(findings))


class TestDerivedArtifactIntegrity(unittest.TestCase):
    def test_stamp_and_verify_round_trip_is_clean(self):
        body = {"palette": {"ground": "#121113"}, "tagline": "x"}
        document = vc.stamp_derived_artifact(body, "VISUAL_NARRATIVE_CANON@0.1.0")
        findings = vc.check_derived_artifact_integrity(document)
        self.assertEqual(findings, [])

    def test_hand_edited_document_is_flagged(self):
        body = {"palette": {"ground": "#121113"}, "tagline": "x"}
        document = vc.stamp_derived_artifact(body, "VISUAL_NARRATIVE_CANON@0.1.0")
        document["tagline"] = "editado à mão depois de gerado"
        findings = vc.check_derived_artifact_integrity(document)
        matches = [f for f in findings if f["category"] == "DERIVED_ARTIFACT_EDITED"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "HIGH")

    def test_document_without_provenance_is_not_tracked(self):
        findings = vc.check_derived_artifact_integrity({"palette": {"ground": "#121113"}})
        self.assertEqual(findings, [])

    def test_unexpected_generator_prefix_is_medium(self):
        body = {"tagline": "x"}
        document = vc.stamp_derived_artifact(body, "SOME_OTHER_GENERATOR@1.0.0")
        findings = vc.check_derived_artifact_integrity(document, expected_generator_prefix="VISUAL_NARRATIVE_CANON")
        matches = [f for f in findings if f["category"] == "DERIVED_ARTIFACT_EDITED"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["severity"], "MEDIUM")


class TestMediaDesignProjection(unittest.TestCase):
    """Slice 6 (seção 17.3 da SDD): projeção determinística de
    `media/MEDIA_DESIGN.yaml` a partir do canon."""

    def test_hex_to_rgb(self):
        self.assertEqual(vc.hex_to_rgb("#121113"), [18, 17, 19])
        self.assertEqual(vc.hex_to_rgb("E6DCCB"), [230, 220, 203])
        self.assertIsNone(vc.hex_to_rgb("not-a-color"))
        self.assertIsNone(vc.hex_to_rgb(None))

    def test_palette_projects_ground_ink_accent_and_derives_muted(self):
        canon = {"book_dna": {"palette": {
            "GROUND": "#121113", "INK": "#E6DCCB",
            "METAL": {"material": "AGED_GOLD", "hex": "#8C6A3C"},
        }}}
        document = vc.project_media_design(canon)
        palette = document["spec"]["palette"]
        self.assertEqual(palette["ground"], [18, 17, 19])
        self.assertEqual(palette["ink"], [230, 220, 203])
        self.assertEqual(palette["accent"], [140, 106, 60])
        # muted = ink * MUTED_LUMINOSITY_FACTOR, canal a canal — nunca mais
        # claro que ink, sempre o mesmo matiz (escala uniforme).
        for ink_ch, muted_ch in zip(palette["ink"], palette["muted"]):
            self.assertLessEqual(muted_ch, ink_ch)
            self.assertEqual(muted_ch, round(ink_ch * vc.MUTED_LUMINOSITY_FACTOR))

    def test_metal_as_plain_hex_string_also_resolves(self):
        canon = {"book_dna": {"palette": {"METAL": "#8C6A3C"}}}
        document = vc.project_media_design(canon)
        self.assertEqual(document["spec"]["palette"]["accent"], [140, 106, 60])

    def test_missing_palette_projects_no_palette_key(self):
        document = vc.project_media_design({"book_dna": {}})
        self.assertNotIn("palette", document["spec"])

    def test_tagline_resolves_from_book_spec_dotted_path(self):
        canon = {"book_dna": {}, "compositions": [
            {"surface": "FRONT_COVER", "typography": [
                {"role": "TITLE", "text_source": "BOOK_SPEC.metadata.title"},
                {"role": "TAGLINE", "text_source": "BOOK_SPEC.metadata.tagline"},
            ]},
        ]}
        book_spec = {"metadata": {"title": "O Cisne Negro", "tagline": "A jaula tem forma de ave."}}
        document = vc.project_media_design(canon, book_spec=book_spec)
        self.assertEqual(document["spec"]["tagline"], "A jaula tem forma de ave.")

    def test_tagline_resolves_from_author_dna_dotted_path(self):
        canon = {"book_dna": {}, "compositions": [
            {"surface": "FRONT_COVER", "typography": [
                {"role": "TAGLINE", "text_source": "AUTHOR_DNA.metadata.public_name"},
            ]},
        ]}
        author_dna = {"metadata": {"public_name": "Bea Halden"}}
        document = vc.project_media_design(canon, author_dna=author_dna)
        self.assertEqual(document["spec"]["tagline"], "Bea Halden")

    def test_tagline_absent_without_a_tagline_row(self):
        canon = {"book_dna": {}, "compositions": [{"surface": "FRONT_COVER", "typography": []}]}
        document = vc.project_media_design(canon)
        self.assertNotIn("tagline", document["spec"])

    def test_unresolvable_text_source_is_silently_omitted(self):
        canon = {"book_dna": {}, "compositions": [
            {"surface": "FRONT_COVER", "typography": [
                {"role": "TAGLINE", "text_source": "BOOK_SPEC.metadata.nonexistent"},
            ]},
        ]}
        document = vc.project_media_design(canon, book_spec={"metadata": {}})
        self.assertNotIn("tagline", document["spec"])

    def test_typography_bindings_pass_through_verbatim(self):
        bindings = {"TITLE": {"family": "Custom", "file": "fonts/custom.ttf",
                              "license": "OFL", "embeddable": True}}
        canon = {"book_dna": {"typography_bindings": bindings}}
        document = vc.project_media_design(canon)
        self.assertEqual(document["spec"]["typography_bindings"], bindings)

    def test_cover_base_image_is_never_projected(self):
        # Deliberado (17.3): nenhuma tarefa desta capability ainda produz
        # "arte aprovada da composição FRONT_COVER" — projetar um caminho
        # inventado quebraria o default seguro de build_cover_and_stories.py.
        canon = {"book_dna": {"palette": {"GROUND": "#121113"}}}
        document = vc.project_media_design(canon)
        self.assertNotIn("cover", document["spec"])

    def test_output_is_a_clean_derived_artifact(self):
        canon = {"metadata": {"version": "0.2.0"},
                 "book_dna": {"palette": {"GROUND": "#121113", "INK": "#E6DCCB"}}}
        document = vc.project_media_design(canon)
        self.assertEqual(document["_generated"]["generated_from"], "VISUAL_NARRATIVE_CANON@0.2.0")
        self.assertEqual(vc.check_derived_artifact_integrity(document), [])
        document["spec"]["palette"]["ground"] = [0, 0, 0]
        findings = vc.check_derived_artifact_integrity(document)
        self.assertEqual([f["category"] for f in findings], ["DERIVED_ARTIFACT_EDITED"])


class TestChapterOpenerProjection(unittest.TestCase):
    """Slice 6 (seções 18.2-18.4 da SDD): `chapter_openers[]` para
    `layout/editions/<target>/EDITION_PLAN.yaml`, consumido por
    `build_kdp_docx.py`."""

    def _canon_with_sigil(self):
        return {
            "elements": [{
                "id": "SIG-SWAN", "class": "SIGIL",
                "states": [
                    {"id": "PRISTINE", "initial": True,
                     "render": {"mode": "GLYPH", "asset": "images/sigils/SIG-SWAN/PRISTINE.png"}},
                    {"id": "CRACKED",
                     "render": {"mode": "RASTER_1BIT", "asset": "images/sigils/SIG-SWAN/CRACKED.png"}},
                ],
                "transitions": [
                    {"from": "PRISTINE", "to": "CRACKED", "trigger": "TURN:2",
                     "display_from": "NEXT_CHAPTER"},
                ],
            }],
            "compositions": [
                {"id": "COMP-OPENER", "surface": "CHAPTER_OPENER",
                 "elements": [{"element": "SIG-SWAN", "prominence": "DOMINANT"}]},
            ],
        }

    def test_projects_one_entry_per_chapter_with_render_info(self):
        canon = self._canon_with_sigil()
        context = {"chapter_architecture": [
            {"number": 1}, {"number": 2, "irreversible_turn": "a coroa racha"},
            {"number": 3}, {"number": 4},
        ]}
        openers = vc.project_chapter_openers(canon, context, chapter_count=4)
        self.assertEqual([o["chapter"] for o in openers], [1, 2, 3, 4])
        # TURN:2 desloca para NEXT_CHAPTER (capítulo 3 em diante) — mesma
        # semântica de display_from já coberta por project_state.
        self.assertEqual([o["state"] for o in openers], ["PRISTINE", "PRISTINE", "CRACKED", "CRACKED"])
        self.assertEqual(openers[0]["render_mode"], "GLYPH")
        self.assertEqual(openers[0]["asset"], "images/sigils/SIG-SWAN/PRISTINE.png")
        self.assertEqual(openers[2]["render_mode"], "RASTER_1BIT")
        self.assertEqual(openers[2]["asset"], "images/sigils/SIG-SWAN/CRACKED.png")
        self.assertTrue(all(o["element"] == "SIG-SWAN" for o in openers))
        self.assertTrue(all(o["composition"] == "COMP-OPENER" for o in openers))

    def test_no_chapter_opener_composition_yields_empty_list(self):
        canon = {"elements": [], "compositions": [{"surface": "FRONT_COVER", "elements": []}]}
        self.assertEqual(vc.project_chapter_openers(canon, {}, chapter_count=6), [])

    def test_non_sigil_dominant_element_is_ignored(self):
        canon = {
            "elements": [{"id": "SYM-SWAN", "class": "MOTIF", "states": []}],
            "compositions": [{"surface": "CHAPTER_OPENER",
                              "elements": [{"element": "SYM-SWAN", "prominence": "DOMINANT"}]}],
        }
        self.assertEqual(vc.project_chapter_openers(canon, {}, chapter_count=3), [])

    def test_secondary_only_composition_has_no_dominant_to_project(self):
        canon = {
            "elements": [{"id": "SIG-SWAN", "class": "SIGIL", "states": []}],
            "compositions": [{"surface": "CHAPTER_OPENER",
                              "elements": [{"element": "SIG-SWAN", "prominence": "SECONDARY"}]}],
        }
        self.assertEqual(vc.project_chapter_openers(canon, {}, chapter_count=3), [])

    def test_zero_chapter_count_yields_empty_list(self):
        canon = self._canon_with_sigil()
        self.assertEqual(vc.project_chapter_openers(canon, {}, chapter_count=0), [])


if __name__ == "__main__":
    unittest.main()
