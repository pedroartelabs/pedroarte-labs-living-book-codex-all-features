"""Testes do Slice 1 do SEM_ROSTO_CANONICAL_STORY_SYSTEM (modo `package`).

Dois blocos:
- RealData: os seeds reais de books/sem-rosto/canon/ passam; dossiê pinado; cobertura de §17 e §21.
- Mutations: uma mutação por teste sobre uma cópia temporária, afirmando a categoria exata.

100% offline. Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_sem_rosto_canon -v
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
PKG = REPO / "books" / "sem-rosto"
CANON = PKG / "canon"
CARTO = PKG / "cartography" / "seeds"
VALIDATOR = PKG / "validators" / "check_sem_rosto_canon.py"
sys.path.insert(0, str(VALIDATOR.parent))

import check_sem_rosto_canon as sr  # noqa: E402

DOSSIER_SHA = "7be721624539c6e1c9d5db983e4d643feea4fba77a6a59e0426645ed72cfbf86"


def categories(findings, severities=None):
    return [f["category"] for f in findings if severities is None or f["severity"] in severities]


class RealData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.findings, cls.summary = sr.validate(CANON, CARTO)

    def test_no_blocking_findings(self):
        self.assertEqual([f for f in self.findings if f["severity"] in sr.BLOCKING], [])

    def test_only_expected_warnings(self):
        self.assertEqual(sorted(categories(self.findings)),
                         ["LOCK_DETECTORS_PLANNED", "SEED_UNAPPROVED", "SEED_UNAPPROVED", "SEED_UNAPPROVED"])

    def test_dossier_is_pinned_and_frozen(self):
        path = CANON / "sources" / "REDMUR_CANON_RESOLUTION_DOSSIER_FINAL.md"
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), DOSSIER_SHA)
        freeze = (CANON / "approvals" / "CANON_FREEZE_0001.md").read_text(encoding="utf-8")
        self.assertIn(f"subject_sha256: {DOSSIER_SHA}", freeze)

    def test_every_section17_unknown_has_a_record(self):
        records = yaml.safe_load((CANON / "seeds" / "CANON_RECORDS.seed.yaml").read_text(encoding="utf-8"))["records"]
        items = sorted(r["dossier_item"] for r in records if "dossier_item" in r)
        self.assertEqual(items, list(range(1, 25)))

    def test_unknowns_have_no_content(self):
        records = yaml.safe_load((CANON / "seeds" / "CANON_RECORDS.seed.yaml").read_text(encoding="utf-8"))["records"]
        for rec in records:
            if rec["id"].startswith("UNK-SR-"):
                self.assertNotIn("statement", rec, rec["id"])
                self.assertEqual(rec["scope"]["reader"], "NEVER", rec["id"])

    def test_capabilities_have_no_instances(self):
        records = yaml.safe_load((CANON / "seeds" / "CANON_RECORDS.seed.yaml").read_text(encoding="utf-8"))["records"]
        caps = [r for r in records if r["id"].startswith("CAP-")]
        self.assertGreaterEqual(len(caps), 5)
        self.assertTrue(all(r["instances"] == [] for r in caps))

    def test_28_locks_and_series_structural_locks(self):
        self.assertEqual(self.summary["locks"], 28)
        gates = yaml.safe_load((CANON / "seeds" / "BOOK_GATES.seed.yaml").read_text(encoding="utf-8"))
        self.assertEqual(gates["series"]["structural_locks"], ["HL-01", "HL-02", "HL-03", "HL-04", "HL-20"])
        self.assertEqual(gates["book_gates"]["B2"], {"status": "UNDEFINED"})

    def test_hidden_answer_keys_come_from_engine(self):
        self.assertEqual(self.summary["hidden_keys_source"], "engine:check_interpretive_canon")

    def test_cli_exit_zero(self):
        proc = subprocess.run([sys.executable, str(VALIDATOR), "--mode", "package"], capture_output=True,
                              text=True, encoding="utf-8", env={"PYTHONIOENCODING": "utf-8", "SYSTEMROOT": _sysroot()})
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS_WITH_WARNINGS", proc.stdout)


def _sysroot():
    import os
    return os.environ.get("SYSTEMROOT", "")


class Mutations(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sr_canon_"))
        self.canon = self.tmp / "canon"
        shutil.copytree(CANON, self.canon)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # helpers
    def seed(self, name):
        return yaml.safe_load((self.canon / "seeds" / name).read_text(encoding="utf-8"))

    def save(self, name, doc):
        (self.canon / "seeds" / name).write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def record(self, doc, rid):
        return next(r for r in doc["records"] if r["id"] == rid)

    def run_validator(self):
        findings, _ = sr.validate(self.canon, CARTO)
        return findings

    def assertCategory(self, category, severity=None):
        findings = self.run_validator()
        hits = [f for f in findings if f["category"] == category and (severity is None or f["severity"] == severity)]
        self.assertTrue(hits, f"{category} não encontrado em {categories(findings)}")
        return hits

    # fonte
    def test_dossier_edit_is_blocked(self):
        path = self.canon / "sources" / "REDMUR_CANON_RESOLUTION_DOSSIER_FINAL.md"
        path.write_bytes(path.read_bytes() + b"\nlinha nova\n")
        self.assertCategory("SOURCE_HASH_MISMATCH", "BLOCKER")

    def test_freeze_without_matching_approval(self):
        path = self.canon / "approvals" / "CANON_FREEZE_0001.md"
        path.write_text(path.read_text(encoding="utf-8").replace(DOSSIER_SHA, "0" * 64), encoding="utf-8")
        self.assertCategory("FREEZE_NOT_APPROVED", "BLOCKER")

    # registros
    def test_duplicate_id(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        doc["records"].append(dict(self.record(doc, "CR-P1-02")))
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("DUPLICATE_ID")

    def test_unknown_with_content(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        self.record(doc, "UNK-SR-SELKA-DEATH")["statement"] = "Selka foi assassinada."
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("UNKNOWN_HAS_CONTENT", "BLOCKER")

    def test_unknown_visible_to_reader(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        self.record(doc, "UNK-SR-40Y-CAUSE")["scope"]["reader"] = "OPEN"
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("UNKNOWN_HAS_CONTENT", "BLOCKER")

    def test_hidden_answer_key_anywhere(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        self.record(doc, "CR-P2-02")["notes"] = {"Verdade": "as crianças são trocadas"}
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("HIDDEN_ANSWER_PRESENT", "BLOCKER")

    def test_capability_instance_without_approval(self):   # TEST 04 (forma estática)
        doc = self.seed("CANON_RECORDS.seed.yaml")
        self.record(doc, "CAP-SEALED-FACIAL-EVIDENCE")["instances"] = ["fotografia de Selka"]
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("SYSTEM_CAPABILITY_AS_INSTANCE", "BLOCKER")

    def test_capability_instance_with_approval_passes(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        self.record(doc, "CAP-SEALED-FACIAL-EVIDENCE")["instances"] = [
            {"id": "SFE-0001", "approved_by": "APPROVAL:CANON_DECISION_0001"}]
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertNotIn("SYSTEM_CAPABILITY_AS_INSTANCE", categories(self.run_validator()))

    def test_anchor_missing_in_dossier(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        self.record(doc, "CR-P0-01")["source"]["location"] = "§99.4"
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("CANON_WITHOUT_PROVENANCE", "HIGH")

    def test_improvised_source(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        self.record(doc, "CR-P0-01")["source"]["id"] = "SRC-WRITER-BRIEF"
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("IMPROVISED_CANON", "BLOCKER")

    def test_approval_source_must_cite_existing_item(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        self.record(doc, "CR-DEC-05B")["source"]["location"] = "OQ-SR-99"
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("CANON_WITHOUT_PROVENANCE", "HIGH")

    def test_section17_coverage_gap(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        doc["records"] = [r for r in doc["records"] if r["id"] != "UNK-SR-TEN-RELICS"]
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("COVERAGE_GAP", "HIGH")

    def test_patch_status_without_patch(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        del self.record(doc, "CR-P0-R1")["patch"]
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("CONTRACT_INVALID", "HIGH")

    def test_invalid_status_enum(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        self.record(doc, "CR-P1-02")["status"] = "PROBABLY_TRUE"
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("INVALID_ENUM", "HIGH")

    def test_unknown_expressed_as_rule(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        self.record(doc, "CR-P6-01")["status"] = "CANON_UNKNOWN"
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("CONTRACT_INVALID", "HIGH")

    def test_map_ref_must_exist_in_cartography(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        self.record(doc, "INST-OCP")["map_refs"] = ["RM-CEN-SIXMONTH"]
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("UNKNOWN_REFERENCE", "HIGH")

    def test_dangling_dependency(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        self.record(doc, "CR-P0-01")["depends_on"] = ["CR-P0-99"]
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("UNKNOWN_REFERENCE", "HIGH")

    def test_unknown_root_field(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        doc["truths_for_later"] = []
        self.save("CANON_RECORDS.seed.yaml", doc)
        self.assertCategory("CONTRACT_INVALID", "HIGH")

    # locks
    def test_lock_without_detector(self):
        doc = self.seed("HARD_LOCKS.seed.yaml")
        next(l for l in doc["locks"] if l["id"] == "HL-23")["detectors"] = []
        self.save("HARD_LOCKS.seed.yaml", doc)
        self.assertCategory("LOCK_WITHOUT_DETECTOR", "MEDIUM")

    def test_structural_lock_with_only_judgment(self):
        doc = self.seed("HARD_LOCKS.seed.yaml")
        next(l for l in doc["locks"] if l["id"] == "HL-27")["detectors"] = ["JUDGMENT:REDMUR_CANON_WARDEN"]
        self.save("HARD_LOCKS.seed.yaml", doc)
        self.assertCategory("LOCK_WITHOUT_DETECTOR", "MEDIUM")

    def test_detector_outside_catalog(self):
        doc = self.seed("HARD_LOCKS.seed.yaml")
        next(l for l in doc["locks"] if l["id"] == "HL-07")["detectors"].append("SR-FOO-01")
        self.save("HARD_LOCKS.seed.yaml", doc)
        self.assertCategory("UNKNOWN_REFERENCE", "HIGH")

    def test_judgment_by_nonexistent_agent(self):
        doc = self.seed("HARD_LOCKS.seed.yaml")
        next(l for l in doc["locks"] if l["id"] == "HL-01")["detectors"].append("JUDGMENT:NOBODY_GUARDIAN")
        self.save("HARD_LOCKS.seed.yaml", doc)
        self.assertCategory("UNKNOWN_REFERENCE", "HIGH")

    def test_lock_edited_after_approval(self):
        doc = self.seed("HARD_LOCKS.seed.yaml")
        doc["metadata"]["approval"] = "CANON_SEEDS_9999"
        self.save("HARD_LOCKS.seed.yaml", doc)
        sha = hashlib.sha256((self.canon / "seeds" / "HARD_LOCKS.seed.yaml").read_bytes()).hexdigest()
        (self.canon / "approvals" / "CANON_SEEDS_9999.md").write_text(f"subject_sha256: {sha}\n", encoding="utf-8")
        self.assertNotIn("HARD_LOCK_EDIT", categories(self.run_validator()))
        doc["locks"] = [l for l in doc["locks"] if l["id"] != "HL-06"]      # remove a trava de menores
        self.save("HARD_LOCKS.seed.yaml", doc)
        self.assertCategory("HARD_LOCK_EDIT", "BLOCKER")

    def test_approved_seed_is_not_flagged(self):
        doc = self.seed("CANON_RECORDS.seed.yaml")
        doc["metadata"]["approval"] = "CANON_SEEDS_9998"
        self.save("CANON_RECORDS.seed.yaml", doc)
        sha = hashlib.sha256((self.canon / "seeds" / "CANON_RECORDS.seed.yaml").read_bytes()).hexdigest()
        (self.canon / "approvals" / "CANON_SEEDS_9998.md").write_text(f"subject_sha256: {sha}\n", encoding="utf-8")
        unapproved = [f for f in self.run_validator() if f["category"] == "SEED_UNAPPROVED"]
        self.assertEqual(len(unapproved), 2)

    # gates
    def test_writing_gate_coverage(self):
        doc = self.seed("BOOK_GATES.seed.yaml")
        doc["book_gates"]["B1"]["writing_gates"].pop()
        self.save("BOOK_GATES.seed.yaml", doc)
        self.assertCategory("COVERAGE_GAP", "HIGH")

    def test_forbidden_gate_must_point_to_unknown(self):
        doc = self.seed("BOOK_GATES.seed.yaml")
        doc["book_gates"]["B1"]["forbidden"][0]["unknowns"] = ["CR-P10-01"]
        self.save("BOOK_GATES.seed.yaml", doc)
        self.assertCategory("UNKNOWN_REFERENCE", "HIGH")

    def test_future_domain_cannot_open_in_book1(self):
        doc = self.seed("BOOK_GATES.seed.yaml")
        doc["series"]["future_domains"][0]["earliest_allowed_reveal"] = "B1"
        self.save("BOOK_GATES.seed.yaml", doc)
        self.assertCategory("INVALID_ENUM", "HIGH")

    def test_book2_is_not_decided_by_seed(self):
        doc = self.seed("BOOK_GATES.seed.yaml")
        doc["book_gates"]["B2"] = {"status": "DEFINED", "resolves": ["UNK-SR-TRUE-CHRONOLOGY"]}
        self.save("BOOK_GATES.seed.yaml", doc)
        self.assertCategory("CONTRACT_INVALID", "HIGH")

    def test_series_structural_lock_must_be_franchise_level(self):
        doc = self.seed("HARD_LOCKS.seed.yaml")
        del next(l for l in doc["locks"] if l["id"] == "HL-04")["franchise_level"]
        self.save("HARD_LOCKS.seed.yaml", doc)
        self.assertCategory("CONTRACT_INVALID", "HIGH")

    def test_cli_exits_one_on_blocker(self):
        path = self.canon / "sources" / "REDMUR_CANON_RESOLUTION_DOSSIER_FINAL.md"
        path.write_bytes(b"x")
        with contextlib.redirect_stdout(io.StringIO()):
            code = sr.main(["--canon", str(self.canon), "--cartography", str(CARTO), "--json"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
