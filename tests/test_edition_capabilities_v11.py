"""EDITION_CAPABILITIES 1.1.0 — Slice 7 de docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md (21–23, 29.6).

Dados novos no motor, neutros de gênero: placa espelhada, papel metalizado,
relevo cego, slipcase e cards; superfícies SLIPCASE_*; promessas de produção
(numerada, assinada, limitada) que só valem no collector com decisão registrada.
Os planos golden do fixture Cisne continuam idênticos (tests/test_visual_canon.py).

Execução (offline): .venv/Scripts/python.exe -m unittest tests.test_edition_capabilities_v11 -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import check_visual_canon as vc  # noqa: E402

NEW_EFFECTS = ("MIRROR_BOARD", "METALLIZED_PAPER", "BLIND_EMBOSS", "SLIPCASE", "INSERT_CARD")


def _capabilities() -> dict:
    return yaml.safe_load(vc.DEFAULT_CAPABILITIES_PATH.read_text(encoding="utf-8"))


def _canon() -> dict:
    return {
        "metadata": {"project_id": "t", "version": "1.0.0"},
        "compositions": [{"id": "COMP-BOX", "surface": "SLIPCASE_FRONT", "reading_layer": "NEUTRAL"}],
        "finish_intents": [
            {"id": "FI-MIRROR", "semantic_material": "SILVER_MIRROR", "preferred_effect": "MIRROR_BOARD",
             "fallbacks": ["METALLIZED_PAPER", "SIMULATED_METALLIC_PRINT"], "cost_class": "OPTIONAL",
             "layer_name": "L_MIRROR"},
            {"id": "FI-BOX", "preferred_effect": "SLIPCASE", "fallbacks": [], "cost_class": "COLLECTOR_ONLY"},
        ],
    }


def _entry(plan: dict, finish_id: str) -> dict:
    return next(f for f in plan["finish_intents"] if f["finish_intent"] == finish_id)


class TestCapabilityData(unittest.TestCase):

    def test_new_effects_are_unsupported_on_kdp_and_vendor_dependent_on_collector(self):
        targets = _capabilities()["targets"]
        for effect in NEW_EFFECTS:
            for target in ("kindle_ebook", "kdp_paperback", "kdp_hardcover"):
                self.assertEqual(targets[target]["effects"][effect], "UNSUPPORTED", (target, effect))
            self.assertEqual(targets["collector"]["effects"][effect], "VENDOR_DEPENDENT", effect)

    def test_slipcase_surfaces_only_on_collector(self):
        capabilities = _capabilities()
        self.assertIn("SLIPCASE_FRONT", capabilities["targets"]["collector"]["surfaces"])
        composition = _canon()["compositions"][0]
        self.assertEqual(vc.resolve_composition_surface(composition, "collector")[0], "SLIPCASE_FRONT")
        for target in ("kindle_ebook", "kdp_paperback", "kdp_hardcover"):
            self.assertIsNone(vc.resolve_composition_surface(composition, target)[0])


class TestMirrorLadder(unittest.TestCase):

    def test_kdp_falls_back_to_simulation(self):
        plan = vc.resolve_edition_plan(_canon(), _capabilities(), "kdp_paperback", None)
        self.assertEqual((_entry(plan, "FI-MIRROR")["effect"], _entry(plan, "FI-MIRROR")["level"]),
                         ("SIMULATED_METALLIC_PRINT", "SIMULATED"))
        self.assertEqual(_entry(plan, "FI-BOX")["level"], "OMIT")

    def test_collector_without_profile_never_claims_physical(self):
        plan = vc.resolve_edition_plan(_canon(), _capabilities(), "collector", None)
        mirror = _entry(plan, "FI-MIRROR")
        # cai na simulação da escada; printer_unconfirmed só marca quando nada resolve (comportamento existente)
        self.assertEqual((mirror["effect"], mirror["level"]), ("SIMULATED_METALLIC_PRINT", "SIMULATED"))
        self.assertEqual(_entry(plan, "FI-BOX")["level"], "OMIT")

    def test_collector_with_confirmed_mirror_board_projects_mirror_mask(self):
        profile = {"metadata": {"id": "p"}, "confirmed_effects": ["MIRROR_BOARD", "SLIPCASE"]}
        canon = _canon()
        plan = vc.resolve_edition_plan(canon, _capabilities(), "collector", profile)
        self.assertEqual((_entry(plan, "FI-MIRROR")["effect"], _entry(plan, "FI-MIRROR")["level"]),
                         ("MIRROR_BOARD", "PHYSICAL"))
        manifest = vc.build_production_manifest(canon, "collector", plan, profile)
        kinds = {a["finish_intent"]: a["kind"] for a in manifest["assets"]}
        self.assertEqual(kinds["FI-MIRROR"], "MIRROR_MASK")
        self.assertEqual(kinds["FI-BOX"], "FULL_ARTWORK")


class TestHonestPromises(unittest.TestCase):

    def categories(self, target, text, profile=None, confirmed=()):
        plan = vc.resolve_edition_plan(_canon(), _capabilities(), target,
                                       {"confirmed_effects": list(confirmed)} if confirmed else None)
        return [f["category"] for f in vc.check_finish_promise(plan, text, profile)]

    def test_mirror_promise_on_kdp(self):
        self.assertIn("FINISH_PROMISE_MISMATCH", self.categories("kdp_hardcover", "Capa espelhada, edição de luxo."))

    def test_mirror_promise_on_collector_with_metallized_paper(self):
        self.assertEqual(self.categories("collector", "Capa nua espelhada.", confirmed=("METALLIZED_PAPER",)), [])

    def test_numbered_on_kdp_is_always_a_mismatch(self):
        profile = {"production": {"numbered": True}}
        self.assertIn("FINISH_PROMISE_MISMATCH", self.categories("kdp_paperback", "Edição numerada.", profile))

    def test_numbered_on_collector_requires_production_decision(self):
        self.assertIn("FINISH_PROMISE_MISMATCH", self.categories("collector", "Exemplares numerados."))
        self.assertEqual(self.categories("collector", "Exemplares numerados.", {"production": {"numbered": True}}), [])

    def test_slipcase_promise_without_physical_slipcase(self):
        self.assertIn("FINISH_PROMISE_MISMATCH", self.categories("collector", "Vem num slipcase negro."))
        self.assertEqual(self.categories("collector", "Vem num slipcase negro.", confirmed=("SLIPCASE",)), [])


if __name__ == "__main__":
    unittest.main()
