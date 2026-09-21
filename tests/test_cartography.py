"""Testes da capability neutra `check_cartography.py` (Slice 1 do SDD
docs/sdd/REDMUR_CANONICAL_CARTOGRAPHY_GRAPH_SDD_v0.1.md, seções 29–30 e 35).

Usa a fixture neutra `tests/fixtures/cartography/canon/` (mini-mundo sem nada de
nenhuma obra). Cada mutação isolada, aplicada a uma CÓPIA do modelo, precisa
produzir a categoria de achado exata. 100% offline.

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_cartography -v
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import check_cartography as cc  # noqa: E402

SCRIPT = REPO / "engine" / "scripts" / "check_cartography.py"
FIXTURE = REPO / "tests" / "fixtures" / "cartography" / "canon"
SCHEMA = REPO / "engine" / "contracts" / "CARTOGRAPHY.schema.json"
TEMPLATE = REPO / "engine" / "templates" / "CARTOGRAPHY_TEMPLATE.yaml"
_MODEL = cc.load_model(FIXTURE)


def model():
    return copy.deepcopy(_MODEL)


def cats(findings, prefix):
    return [f for f in findings if f["category"].startswith(prefix)]


def loc(m, lid):
    return next(l for l in m["locations"] if l["id"] == lid)


class CleanFixture(unittest.TestCase):
    def test_fixture_has_no_findings(self):
        self.assertEqual(cc.validate(model()), [])

    def test_origin_projects_to_zero_and_shared_scale(self):
        proj = cc.project_all(model())
        self.assertEqual((proj["TS-CEN-ORG"]["x"], proj["TS-CEN-ORG"]["y"]), (0, 0))
        self.assertEqual((proj["TS-CEN-CAP"]["x"], proj["TS-CEN-CAP"]["y"]), (-300, 100))
        # Mapa B: 100 m/px; ver fixture
        self.assertEqual((proj["TS-REG-ALD"]["x"], proj["TS-REG-ALD"]["y"]), (0, 3000))
        self.assertEqual(proj["TS-REG-ALD"]["accuracy_m"], 840)

    def test_subterranean_inherits_portal_position_and_junction_is_unknown(self):
        proj = cc.project_all(model())
        self.assertEqual(proj["TS-SUB-POR"]["x"], proj["TS-CEN-CAP"]["x"])
        self.assertIsNone(proj["TS-JCT-1"])
        self.assertIsNone(proj["TS-SUB-SEL"])


class Integrity(unittest.TestCase):
    def test_dangling_edge(self):  # T03
        m = model()
        m["edges"].append({"id": "EDG-X", "from": "TS-CEN-ORG", "to": "NAO-EXISTE", "edge_type": "ROAD"})
        self.assertTrue(cats(cc.validate(m), "CG-01"))

    def test_duplicate_id(self):
        m = model()
        m["locations"].append(copy.deepcopy(loc(m, "TS-CEN-EST")))
        self.assertTrue(cats(cc.validate(m), "CG-02"))

    def test_origin_not_zero(self):
        m = model()
        loc(m, "TS-CEN-ORG")["source_px"][0]["px"] = [51, 40]
        self.assertTrue(cats(cc.validate(m), "CG-03"))

    def test_unknown_type(self):
        m = model()
        loc(m, "TS-CEN-EST")["type"] = "PORTAL_MAGICO"
        self.assertTrue(cats(cc.validate(m), "CG-04"))

    def test_type_extension_must_be_declared(self):
        m = model()
        m["manifest"]["metadata"]["type_extensions"].remove("MILL")
        self.assertTrue(cats(cc.validate(m), "CG-04"))

    def test_coordinate_without_source(self):
        m = model()
        del loc(m, "TS-CEN-EST")["source_px"]
        self.assertTrue(cats(cc.validate(m), "CG-05"))

    def test_cached_coordinate_must_match_derived(self):  # CN-05 / INV-C15
        m = model()
        loc(m, "TS-CEN-CAP")["coordinates_cache"] = {"x": 0, "y": 0}
        self.assertTrue(cats(cc.validate(m), "CN-05"))
        loc(m, "TS-CEN-CAP")["coordinates_cache"] = {"x": -300, "y": 100}
        self.assertFalse(cats(cc.validate(m), "CN-05"))

    def test_source_hash_mismatch(self):
        m = model()
        m["sources"]["sources"][0]["sha256"] = "0" * 64
        self.assertTrue(cats(cc.validate(m), "CG-06"))

    def test_cross_layer_edge_needs_portal(self):
        m = model()
        m["edges"].append({"id": "EDG-X", "from": "TS-CEN-CAP", "to": "TS-SUB-POR", "edge_type": "ROAD"})
        self.assertTrue(cats(cc.validate(m), "CG-07"))

    def test_name_collision(self):
        m = model()
        loc(m, "TS-CEN-EST")["canonical_name"] = "marco  ZERO"
        self.assertTrue(cats(cc.validate(m), "CG-09"))

    def test_inventory_item_unmapped(self):  # T02
        m = model()
        m["inventory"].append({"item": "rótulo esquecido", "kind": "LABEL", "maps_to": "NAO-EXISTE"})
        self.assertTrue(cats(cc.validate(m), "CG-08"))

    def test_edge_shorter_than_euclid(self):
        m = model()
        m["edges"].append({"id": "EDG-X", "from": "TS-CEN-ORG", "to": "TS-URB-MOI", "edge_type": "TRAIL",
                           "distance_meters": {"min": 50, "nominal": 60}})
        self.assertTrue(cats(cc.validate(m), "CX-04"))

    def test_scale_ratio_mismatch(self):  # T34
        m = model()
        m["sources"]["sources"][1]["scale_evidence"]["meters_per_px"] = 55
        self.assertTrue(cats(cc.validate(m), "CG-13"))

    def test_changing_scale_only_moves_map_b_only_nodes(self):  # T28
        m = model()
        before = cc.project_all(m)
        m["sources"]["sources"][1]["scale_evidence"]["meters_per_px"] = 50
        after = cc.project_all(m)
        self.assertEqual(before["TS-CEN-CAP"], after["TS-CEN-CAP"])
        self.assertEqual(before["TS-CEN-ORG"], after["TS-CEN-ORG"])
        self.assertNotEqual(before["TS-REG-ALD"]["y"], after["TS-REG-ALD"]["y"])
        self.assertEqual(after["TS-REG-ALD"]["y"], 1500)

    def test_schematic_anchor_never_used_for_metric(self):
        m = model()
        loc(m, "TS-CEN-ORG")["source_px"] = [{"source": "SRC-MAP-B", "px": [10, 10], "anchor": "SCHEMATIC"}]
        self.assertIsNone(cc.project_all(m)["TS-CEN-ORG"])


class Subterranean(unittest.TestCase):
    def test_component_without_portal_fails(self):  # T06
        m = model()
        m["edges"] = [e for e in m["edges"] if e["edge_type"] != "PORTAL"]
        self.assertTrue(cats(cc.validate(m), "CX-02"))

    def test_undeclared_node_is_exempt_but_inert(self):
        f = cc.validate(model())
        self.assertFalse(cats(f, "CX-02"))

    def test_undeclared_node_with_edges_fails(self):
        m = model()
        m["edges"].append({"id": "EDG-S-9", "from": "TS-SUB-SEL", "to": "TS-JCT-1", "edge_type": "SECRET_PASSAGE"})
        self.assertTrue(cats(cc.validate(m), "CONNECTIVITY_UNDECLARED_HAS_EDGES"))

    def test_orphan_is_info_until_digitized(self):
        m = model()
        m["edges"] = [e for e in m["edges"] if e["from"] != "TS-URB-MOI" and e["to"] != "TS-URB-MOI"]
        f = cats(cc.validate(m), "CG-10")
        self.assertTrue(f)
        self.assertEqual(f[0]["severity"], "MEDIUM")   # fixture declara edges_digitized: true
        m["manifest"]["metadata"]["edges_digitized"] = False
        self.assertEqual(cats(cc.validate(m), "CG-10")[0]["severity"], "INFO")


class Register(unittest.TestCase):
    def test_line_count_drift(self):
        m = model()
        m["register"]["entries"].pop()
        self.assertTrue(cats(cc.validate(m), "CG-12"))

    def test_display_index_must_be_string(self):
        m = model()
        m["register"]["entries"][0]["display_index"] = 1
        self.assertTrue(cats(cc.validate(m), "CG-12"))

    def test_duplicate_index_is_preserved_not_flagged(self):
        self.assertFalse(cats(cc.validate(model()), "CG-12"))   # fixture tem "02" duas vezes

    def test_ordering_significance_needs_truth_ref(self):
        m = model()
        m["register"]["entries"][0]["ordering_significance"] = "ENCRYPTED"
        self.assertTrue(cats(cc.validate(m), "MY-04"))


class MysteryPreservation(unittest.TestCase):
    def test_true_exit_class_is_not_representable(self):  # T10
        m = model()
        m["exits"][0]["claims"].append({"class": "TRUE_EXIT", "text": "x", "source": "SRC-MAP-A"})
        self.assertTrue(cats(cc.validate(m), "EXIT_CLASS_INVALID"))

    def test_true_exit_key_is_blocked(self):
        m = model()
        m["exits"][0]["true_exit"] = "EXT-01"
        f = cc.validate(m)
        self.assertTrue(cats(f, "MY-02"))
        self.assertTrue(any(x["severity"] == "BLOCKER" for x in cats(f, "MY-02")))

    def test_true_exit_string_is_blocked(self):
        m = model()
        m["exits"][0]["note"] = "esta é a saída verdadeira"
        self.assertTrue(cats(cc.validate(m), "MY-02"))

    def test_verbatim_map_text_is_exempt_from_scans(self):
        m = model()
        m["artifacts"][1]["text"] = "a saída verdadeira é um portal mágico"   # é alegação do artefato, não do sistema
        self.assertEqual(cc.validate(m), [])

    def test_beyond_frame_is_always_off_map(self):
        m = model()
        m["exits"][0]["physical"]["beyond_frame"] = "REGION_X"
        self.assertTrue(cats(cc.validate(m), "MY-02"))

    def test_exit_classes_are_a_projection(self):
        m = model()
        m["exits"][0]["exit_classes"] = ["OFFICIAL_EXIT"]
        self.assertTrue(cats(cc.validate(m), "EXIT_CLASSES_DRIFT"))

    def test_false_exit_needs_proof(self):
        m = model()
        m["exits"][0]["truth_ref"] = None   # sem ponteiro para o ledger e sem prova física
        m["exits"][0]["claims"].append({"class": "FALSE_EXIT", "text": "x", "source": "SRC-MAP-A"})
        m["exits"][0]["exit_classes"].append("FALSE_EXIT")
        self.assertTrue(cats(cc.validate(m), "EXIT_FALSE_WITHOUT_PROOF"))

    def test_hidden_answer_keys(self):  # T11
        for key in ("actual_pattern", "verdade", "truth", "solution"):
            m = model()
            m["mysteries"][0][key] = "x"
            self.assertTrue(cats(cc.validate(m), "MY-01"), key)

    def test_resolved_without_truth_ref(self):  # T23
        m = model()
        m["mysteries"][0]["resolution_state"] = "RESOLVED"
        self.assertTrue(cats(cc.validate(m), "MY-04"))
        m["mysteries"][0]["truth_ref"] = "GT-1"
        m["mysteries"][0]["question_ref"] = "Q-1"
        self.assertFalse(cats(cc.validate(m), "MY-04"))

    def test_never_question_cannot_resolve(self):
        m = model()
        m["mysteries"][1]["resolution_state"] = "RESOLVED"
        self.assertTrue(cats(cc.validate(m), "MY-03"))

    def test_motto_is_artifact_not_answer(self):
        m = model()
        m["route_mysteries"][0]["motto_status"] = "TRUE"
        self.assertTrue(cats(cc.validate(m), "MY-03"))

    def test_candidate_interpretation_has_no_truth_value(self):
        m = model()
        m["mysteries"][0]["candidate_interpretations"] = [{"text": "x", "plausible": 0.9}]
        self.assertTrue(cats(cc.validate(m), "MY-03"))

    def test_glyph_reading_never_becomes_link(self):
        m = model()
        m["glyphs"][0]["attributed_to"] = "RMY-R1"
        self.assertTrue(cats(cc.validate(m), "MY-03"))

    def test_undecided_anomaly_cannot_be_clue(self):  # T22
        m = model()
        m["mysteries"][0]["activation"]["requires_anomalies"] = ["ANM-02"]
        self.assertTrue(cats(cc.validate(m), "MY-06"))

    def test_structure_reference_is_not_a_clue_violation(self):
        m = model()
        m["mysteries"][0]["activation"]["requires_anomalies"] = ["UNL-01"]
        self.assertFalse(cats(cc.validate(m), "MY-06"))

    def test_map_author_cannot_be_revealed(self):
        m = model()
        m["artifacts"][0]["author"] = "INST-X"
        self.assertTrue(cats(cc.validate(m), "MY-08"))

    def test_institutional_layer_implies_author(self):
        m = model()
        m["artifacts"][0]["map_layer"] = "LYR-MODERN-OFFICIAL"
        self.assertTrue(cats(cc.validate(m), "MY-08"))

    def test_map_text_is_never_fact(self):
        m = model()
        m["artifacts"][1]["epistemic_status"] = "FACT"
        self.assertTrue(cats(cc.validate(m), "TEXT_CLAIMED_AS_FACT"))

    def test_supernatural_is_blocked(self):  # INV-C00
        m = model()
        loc(m, "TS-CEN-CAP")["note"] = "a capela teletransporta quem entra"
        self.assertTrue(cats(cc.validate(m), "CX-05"))


class Contract(unittest.TestCase):
    def test_schema_enums_match_validator(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        d = schema["$defs"]
        self.assertEqual(set(d["Edge"]["properties"]["edge_type"]["enum"]), cc.EDGE_TYPES)
        self.assertEqual(set(d["Exit"]["properties"]["exit_classes"]["items"]["enum"]), cc.EXIT_CLASSES)
        self.assertEqual(set(d["CartographicMystery"]["properties"]["resolution_state"]["enum"]), cc.RESOLUTION_STATES)
        self.assertEqual(set(d["Boundary"]["properties"]["kind"]["enum"]), cc.BOUNDARY_KINDS)
        self.assertEqual(set(d["Artifact"]["properties"]["kind"]["enum"]), cc.ARTIFACT_KINDS)
        self.assertEqual(set(d["Anomaly"]["properties"]["classification"]["enum"]), cc.ANOMALY_CLASSES)
        self.assertEqual(set(d["Epistemic"]["enum"]), cc.EPISTEMIC)
        self.assertEqual(set(d["Location"]["properties"]["layer"]["enum"]), cc.LAYERS)
        self.assertEqual(set(d["Location"]["properties"]["status"]["enum"]), cc.LOCATION_STATUS)
        self.assertEqual(set(d["Register"]["properties"]["entries"]["items"]["properties"]["placement"]["enum"]),
                         cc.REGISTER_PLACEMENTS)
        import cartography_maps as mp
        self.assertEqual(set(d["Depiction"]["properties"]["relation"]["enum"]), mp.DEPICTION_RELATIONS)

    def test_no_enum_can_represent_a_true_exit(self):
        blob = json.dumps(json.loads(SCHEMA.read_text(encoding="utf-8"))["$defs"])
        self.assertNotIn("TRUE_EXIT", blob.replace('"true_exit"', ""))
        self.assertNotIn("REAL_EXIT", blob)

    def test_template_parses_and_uses_known_keys_only(self):
        data = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
        allowed = set(cc.LIST_KEYS) | {"apiVersion", "kind", "metadata", "includes", "register", "settings",
                                       "mutations", "mutation_log"}
        self.assertLessEqual(set(data), allowed)
        for key in data:
            self.assertNotIn(cc.normalize_key(key), {cc.normalize_key(k) for k in cc.HIDDEN_ANSWER_KEYS})

    def test_engine_script_is_genre_and_book_neutral(self):
        text = SCRIPT.read_text(encoding="utf-8").lower()
        for word in ("redmur", "saint morrow", "sem rosto", "manfred", "flarry"):
            self.assertNotIn(word, text)


class Cli(unittest.TestCase):
    def run_cli(self, path, *extra):
        env = {"PYTHONIOENCODING": "utf-8", "PATH": __import__("os").environ.get("PATH", "")}
        return subprocess.run([sys.executable, str(SCRIPT), "--canon", str(path), *extra],
                              capture_output=True, text=True, encoding="utf-8", env=env)

    def test_clean_fixture_exits_zero_and_json_parses(self):
        r = self.run_cli(FIXTURE, "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["findings"], [])
        self.assertEqual(payload["summary"]["register_lines"], 3)

    def test_blocking_finding_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "canon"
            shutil.copytree(FIXTURE, dst)
            p = dst / "MYSTERIES.seed.yaml"
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            data["exits"][0]["true_exit"] = "EXT-01"
            p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
            r = self.run_cli(dst, "--json")
            self.assertEqual(r.returncode, 1)
            self.assertTrue(any(f["category"].startswith("MY-02") for f in json.loads(r.stdout)["findings"]))

    def test_coords_table(self):
        r = self.run_cli(FIXTURE, "--coords")
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = {row["id"]: row for row in json.loads(r.stdout)}
        self.assertEqual((rows["TS-CEN-CAP"]["x"], rows["TS-CEN-CAP"]["y"]), (-300, 100))
        self.assertIsNone(rows["TS-SUB-SEL"]["x"])

    def test_missing_manifest_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.run_cli(Path(tmp))
            self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
