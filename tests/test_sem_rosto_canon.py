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
                         ["LOCK_DETECTORS_PLANNED"] + ["SEED_UNAPPROVED"] * 6)

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
        self.assertEqual(len(unapproved), 5)

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


FIXTURE_RT = REPO / "tests" / "fixtures" / "sem_rosto_canon" / "runtime_min"


class Slice2RealData(unittest.TestCase):
    def test_section18_every_reserved_mystery_has_a_record(self):
        mys = yaml.safe_load((CANON / "seeds" / "MYSTERIES.seed.yaml").read_text(encoding="utf-8"))["mysteries"]
        self.assertEqual(sorted(m["dossier_item"] for m in mys if "dossier_item" in m), list(range(1, 16)))

    def test_reserved_mysteries_never_above_expanding_in_book1(self):
        for m in yaml.safe_load((CANON / "seeds" / "MYSTERIES.seed.yaml").read_text(encoding="utf-8"))["mysteries"]:
            if m["status"] == "RESERVED":
                self.assertEqual(m["by_book"]["B1"]["state_ceiling"], "EXPANDING", m["id"])

    def test_no_mystery_becomes_interpretive_question(self):   # OQ-SR-04
        for m in yaml.safe_load((CANON / "seeds" / "MYSTERIES.seed.yaml").read_text(encoding="utf-8"))["mysteries"]:
            self.assertNotIn("interpretive_question", m, m["id"])

    def test_every_theory_has_prohibited_as_fact(self):
        for r in yaml.safe_load((CANON / "seeds" / "RUMORS.seed.yaml").read_text(encoding="utf-8"))["rumors"]:
            self.assertEqual(r["truth_relation"], "UNCONFIRMED", r["id"])
            if r["id"].startswith("THEORY-"):
                self.assertTrue(r["prohibited_as_fact"].startswith("PRO-SR-"), r["id"])

    def test_fixture_runtime_passes_plan_and_engine_ledger(self):
        import check_causal_ledger as ccl
        ledger = yaml.safe_load((FIXTURE_RT / "canon" / "CAUSAL_LEDGER.yaml").read_text(encoding="utf-8"))
        self.assertEqual([f for f in ccl.validate(ledger) if f["severity"] in {"HIGH", "BLOCKER"}], [])
        findings, summary = sr.validate(CANON, CARTO, FIXTURE_RT)
        self.assertEqual([f for f in findings if f["severity"] in sr.BLOCKING], [])
        self.assertEqual(summary["runtime"], {"events": 7, "deltas": 14})

    def test_registry_fragment_matches_fixture_registry(self):
        frag = sr.registry_fragment(sr.build_context(CANON, CARTO))
        reg = yaml.safe_load((FIXTURE_RT / "canon" / "CANON_REGISTRY.yaml").read_text(encoding="utf-8"))
        self.assertEqual(frag["unknowns"], reg["unknowns"])
        self.assertEqual(frag["prohibited_inferences"], reg["prohibited_inferences"])
        self.assertEqual(len(frag["unknowns"]), 30)


class Slice2Queries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = sr.build_context(CANON, CARTO)
        cls.rt = sr.load_runtime(FIXTURE_RT)

    def test_is_true_answers(self):
        cases = {"CR-P0-R1": "TRUE (FACT)", "CAP-DEAD-ARCHIVE": "CAPABILITY_ONLY",
                 "UNK-SR-TRUE-CHRONOLOGY": "CANON_UNKNOWN", "RUM-SELKA-COFFER": "CLAIMED_AS (RUMOR)",
                 "THEORY-CHILD-SUBSTITUTION": "CLAIMED_AS (THEORY)", "PRO-SR-PULL-FORCE": "FALSE",
                 "MYS-SELKA": "OPEN_QUESTION"}
        for ident, expected in cases.items():
            self.assertEqual(sr.query_is_true(self.ctx, ident)["answer"], expected, ident)

    def test_is_true_by_title_and_unknown_text(self):
        self.assertEqual(sr.query_is_true(self.ctx, "Combination ≠ Removal Authority")["id"], "CR-P0-R1")
        miss = sr.query_is_true(self.ctx, "quem guarda a chave da cripta")
        self.assertEqual((miss["answer"], miss["next"]), ("NOT_IN_CANON", "CANON_PROPOSAL_REQUIRED"))

    def test_who_knows_separates_modalities(self):
        rows = sr.query_who_knows(self.ctx, self.rt["ledger"], "RUM-SELKA-COFFER", None)
        self.assertIn({"knower": "CHR-FX-A", "modality": "BELIEVES", "token": "SR:BELIEVES:RUM-SELKA-COFFER",
                       "since_chapter": 2}, rows)
        self.assertEqual(sr.query_who_knows(self.ctx, self.rt["ledger"], "RUM-SELKA-COFFER", 1), [])

    def test_reader_at_projects_page_not_world(self):
        at3 = sr.query_reader_at(self.ctx, self.rt["ledger"], 3)
        self.assertEqual(at3["facts_seen"], ["CR-P1-02", "CR-P10-02"])
        self.assertEqual(at3["rumors_seen"], ["RUM-SELKA-COFFER"])
        self.assertNotIn("CR-P0-R1", str(sr.query_reader_at(self.ctx, self.rt["ledger"], 9)))   # só A foi informado

    def test_mystery_state_projection(self):
        led, itp = self.rt["ledger"], self.rt["interpretive"]
        self.assertEqual(sr.mystery_state(self.ctx, "MYS-FORTY-YEARS", led, itp, 2), "UNOPENED")
        self.assertEqual(sr.mystery_state(self.ctx, "MYS-FORTY-YEARS", led, itp, 3), "OPEN")
        self.assertEqual(sr.mystery_state(self.ctx, "MYS-SELKA", led, itp, 2), "OPEN")


class Slice2Mutations(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sr_s2_"))
        self.canon = self.tmp / "canon"
        self.rt = self.tmp / "rt"
        shutil.copytree(CANON, self.canon)
        shutil.copytree(FIXTURE_RT, self.rt)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def load(self, path):
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def dump(self, path, doc):
        path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def seed_path(self, name):
        return self.canon / "seeds" / name

    def ledger_path(self):
        return self.rt / "canon" / "CAUSAL_LEDGER.yaml"

    def deltas_path(self):
        return self.rt / "canon" / "SEM_ROSTO_STATE_DELTAS.yaml"

    def event(self, ledger, eid):
        return next(e for e in ledger["events"] if e["id"] == eid)

    def add_learn(self, eid, knower, token, provenance=True):
        led = self.load(self.ledger_path())
        self.event(led, eid)["knowledge_delta"].append({"knower": knower, "learns": [token]})
        self.dump(self.ledger_path(), led)
        if provenance:
            deltas = self.load(self.deltas_path())
            ev = self.event(led, eid)
            deltas["deltas"].append({"id": f"SD-{9000 + len(deltas['deltas'])}", "event": eid,
                                     "type": "KNOWLEDGE_PROVENANCE", "status": "PLANNED", "chapter": ev["chapter"],
                                     "knower": knower, "token": token, "source": eid, "confidence": "FULL"})
            self.dump(self.deltas_path(), deltas)

    def findings(self, runtime=True):
        return sr.validate(self.canon, CARTO, self.rt if runtime else None)[0]

    def assertCategory(self, category, severity=None, runtime=True):
        found = self.findings(runtime)
        hits = [f for f in found if f["category"] == category and (severity is None or f["severity"] == severity)]
        self.assertTrue(hits, f"{category} não encontrado em {categories(found)}")

    def assertNoBlocking(self):
        self.assertEqual([f for f in self.findings() if f["severity"] in sr.BLOCKING], [])

    def mystery(self, doc, mid):
        return next(m for m in doc["mysteries"] if m["id"] == mid)

    # --- seeds de mistério e rumor
    def test_reserved_mystery_with_resolved_ceiling(self):
        doc = self.load(self.seed_path("MYSTERIES.seed.yaml"))
        self.mystery(doc, "MYS-SELKA")["by_book"]["B1"]["state_ceiling"] = "RESOLVED"
        self.dump(self.seed_path("MYSTERIES.seed.yaml"), doc)
        self.assertCategory("PREMATURE_RESOLUTION", "BLOCKER", runtime=False)

    def test_mystery_with_world_truth(self):
        doc = self.load(self.seed_path("MYSTERIES.seed.yaml"))
        self.mystery(doc, "MYS-AQUELE-DIA")["world_truth"] = "uma enchente"
        self.dump(self.seed_path("MYSTERIES.seed.yaml"), doc)
        self.assertCategory("HIDDEN_ANSWER_PRESENT", "BLOCKER", runtime=False)

    def test_section18_coverage_gap(self):
        doc = self.load(self.seed_path("MYSTERIES.seed.yaml"))
        doc["mysteries"] = [m for m in doc["mysteries"] if m.get("dossier_item") != 2]
        self.dump(self.seed_path("MYSTERIES.seed.yaml"), doc)
        self.assertCategory("COVERAGE_GAP", "HIGH", runtime=False)

    def test_locked_unknown_without_mystery(self):
        doc = self.load(self.seed_path("MYSTERIES.seed.yaml"))
        m = self.mystery(doc, "MYS-SELKA")
        m["unknown_refs"] = [u for u in m["unknown_refs"] if u != "UNK-SR-SELKA-TATTOO-COUNT"]
        self.dump(self.seed_path("MYSTERIES.seed.yaml"), doc)
        self.assertCategory("UNKNOWN_WITHOUT_MYSTERY", "MEDIUM", runtime=False)

    def test_rumor_content_promoted_to_fact(self):
        doc = self.load(self.seed_path("RUMORS.seed.yaml"))
        doc["rumors"][0]["epistemic_class"] = "FACT"
        self.dump(self.seed_path("RUMORS.seed.yaml"), doc)
        self.assertCategory("RUMOR_PROMOTED_TO_FACT", "BLOCKER", runtime=False)

    def test_rumor_marked_true(self):
        doc = self.load(self.seed_path("RUMORS.seed.yaml"))
        doc["rumors"][0]["truth_relation"] = "CONFIRMED"
        self.dump(self.seed_path("RUMORS.seed.yaml"), doc)
        self.assertCategory("RUMOR_PROMOTED_TO_FACT", "BLOCKER", runtime=False)

    def test_rumor_origin_invented(self):
        doc = self.load(self.seed_path("RUMORS.seed.yaml"))
        doc["rumors"][0]["origin"] = "FAM-FLARRY"
        self.dump(self.seed_path("RUMORS.seed.yaml"), doc)
        self.assertCategory("RUMOR_ORIGIN_INVENTED", "HIGH", runtime=False)

    def test_theory_without_prohibition(self):
        doc = self.load(self.seed_path("RUMORS.seed.yaml"))
        del next(r for r in doc["rumors"] if r["id"] == "THEORY-CHILD-SUBSTITUTION")["prohibited_as_fact"]
        self.dump(self.seed_path("RUMORS.seed.yaml"), doc)
        self.assertCategory("CONTRACT_INVALID", "HIGH", runtime=False)

    def test_rumor_version_marked_true(self):
        doc = self.load(self.seed_path("RUMORS.seed.yaml"))
        doc["rumors"][0]["versions"] = [{"id": "RUV-01", "carrier": "FAM-MANFRED", "elements": ["x"], "is_true": True,
                                         "source": {"id": "SRC-DOSSIER", "location": "§14.7"}}]
        self.dump(self.seed_path("RUMORS.seed.yaml"), doc)
        self.assertCategory("RUMOR_NORMALIZED", "HIGH", runtime=False)

    # --- conhecimento no runtime
    def test_book1_learns_locked_unknown(self):   # TEST 10
        self.add_learn("EV-03", "CHR-FX-A", "UNK-SR-40Y-CAUSE")
        self.assertCategory("BOOK1_HISTORY_LOCK_VIOLATION", "BLOCKER")

    def test_belief_in_unknown_is_still_blocked(self):
        self.add_learn("EV-03", "CHR-FX-A", "SR:BELIEVES:UNK-SR-SELKA-DEATH")
        self.assertCategory("BOOK1_HISTORY_LOCK_VIOLATION", "BLOCKER")

    def test_reader_learns_unlockable_unknown(self):
        self.add_learn("EV-03", "READER", "UNK-SR-BODY-GAP")
        self.assertCategory("READER_KNOWLEDGE_LEAK", "BLOCKER")

    def test_character_learns_unlockable_unknown(self):
        self.add_learn("EV-03", "CHR-FX-B", "UNK-SR-TEN-RELICS")
        self.assertCategory("PREMATURE_MYSTERY_REVEAL", "BLOCKER")

    def test_prohibited_inference_known_as_fact(self):   # TEST 03 (forma estrutural)
        self.add_learn("EV-03", "CHR-FX-A", "PRO-SR-CHILD-SUBSTITUTION-FACT")
        self.assertCategory("UNKNOWN_AS_FACT", "BLOCKER")

    def test_prohibited_inference_believed_is_allowed(self):
        self.add_learn("EV-03", "CHR-FX-A", "SR:BELIEVES:PRO-SR-CHILD-SUBSTITUTION-FACT")
        self.assertNoBlocking()

    def test_character_acts_on_unlearned(self):   # TEST 05
        led = self.load(self.ledger_path())
        self.event(led, "EV-03")["acts_on_knowledge"].append("CR-P0-R1")
        self.dump(self.ledger_path(), led)
        self.assertCategory("CHARACTER_KNOWLEDGE_LEAK", "HIGH")

    def test_told_is_not_known(self):
        led = self.load(self.ledger_path())
        led["events"].append({"id": "EV-05", "status": "PLANNED", "chapter": 6, "structural": False,
                              "kind": ["ATTEMPT"], "actor": "CHR-FX-A", "participants": ["CHR-FX-A"],
                              "facts": ["A tenta algo."], "caused_by": ["EV-04"], "acts_on_knowledge": ["CR-P0-R1"]})
        self.dump(self.ledger_path(), led)
        self.assertCategory("TOLD_AS_KNOWN", "MEDIUM")

    def test_learning_without_provenance(self):
        self.add_learn("EV-03", "CHR-FX-B", "CR-P1-R9", provenance=False)
        self.assertCategory("KNOWLEDGE_WITHOUT_PROVENANCE", "HIGH")

    def test_provenance_with_bogus_source(self):
        deltas = self.load(self.deltas_path())
        deltas["deltas"][0]["source"] = "porque sim"
        self.dump(self.deltas_path(), deltas)
        self.assertCategory("KNOWLEDGE_WITHOUT_PROVENANCE", "HIGH")

    def test_orphan_provenance(self):
        deltas = self.load(self.deltas_path())
        deltas["deltas"][0]["token"] = "CR-P0-05"
        self.dump(self.deltas_path(), deltas)
        self.assertCategory("STATE_WITHOUT_CAUSE", "HIGH")

    def test_learning_nonexistent_canon(self):
        self.add_learn("EV-03", "CHR-FX-A", "CR-P0-99")
        self.assertCategory("UNKNOWN_REFERENCE", "HIGH")

    def test_rumor_narrated_as_world_truth(self):   # TEST 06
        doc = self.load(self.seed_path("CANON_RECORDS.seed.yaml"))
        next(r for r in doc["records"] if r["id"] == "PRO-SR-SELKA-COFFER-FACT")["match"] = ["enterrada com o cofre"]
        self.dump(self.seed_path("CANON_RECORDS.seed.yaml"), doc)
        led = self.load(self.ledger_path())
        self.event(led, "EV-03")["facts"].append("Selka foi Enterrada com o Cofre.")
        self.dump(self.ledger_path(), led)
        self.assertCategory("RUMOR_AS_WORLD_TRUTH", "HIGH")

    def test_prohibited_inference_in_facts(self):
        doc = self.load(self.seed_path("CANON_RECORDS.seed.yaml"))
        next(r for r in doc["records"] if r["id"] == "PRO-SR-PULL-FORCE")["match"] = ["maldição de redmur"]
        self.dump(self.seed_path("CANON_RECORDS.seed.yaml"), doc)
        led = self.load(self.ledger_path())
        self.event(led, "EV-01")["facts"].append("A maldição de Redmur prende A.")
        self.dump(self.ledger_path(), led)
        self.assertCategory("SUPERNATURAL_CONFIRMATION", "BLOCKER")   # PRO-SR-PULL-FORCE -> SR-PUL-02 (Slice 3)

    def test_rumor_voiced_by_character_is_allowed(self):
        doc = self.load(self.seed_path("CANON_RECORDS.seed.yaml"))
        next(r for r in doc["records"] if r["id"] == "PRO-SR-SELKA-COFFER-FACT")["match"] = ["enterrada com o cofre"]
        self.dump(self.seed_path("CANON_RECORDS.seed.yaml"), doc)
        led = self.load(self.ledger_path())
        self.event(led, "EV-02")["evidence_to_reader"] = ["B diz que Selka foi enterrada com o cofre."]
        self.dump(self.ledger_path(), led)
        self.assertNotIn("RUMOR_AS_WORLD_TRUTH", categories(self.findings()))

    def test_registry_drift(self):
        reg_path = self.rt / "canon" / "CANON_REGISTRY.yaml"
        reg = self.load(reg_path)
        reg["unknowns"] = [u for u in reg["unknowns"] if u["id"] != "UNK-SR-PULL-COMPLETE"]
        reg["unknowns"][0]["status"] = "RESOLVED"
        self.dump(reg_path, reg)
        self.assertEqual(len([f for f in self.findings() if f["category"] == "REGISTRY_DRIFT"]), 2)

    def test_reserved_mystery_as_resolvable_question(self):
        doc = self.load(self.seed_path("MYSTERIES.seed.yaml"))
        self.mystery(doc, "MYS-SELKA")["interpretive_question"] = "Q-SELKA"
        self.dump(self.seed_path("MYSTERIES.seed.yaml"), doc)
        self.dump(self.rt / "canon" / "INTERPRETIVE_CANON.yaml",
                  {"questions": [{"id": "Q-SELKA", "resolution_policy": "RESOLVED_AT"}]})
        found = categories(self.findings())
        self.assertIn("RESERVED_NOT_NEVER_IN_BOOK", found)
        self.assertIn("PREMATURE_RESOLUTION", found)

    def test_state_delta_contract(self):
        deltas = self.load(self.deltas_path())
        deltas["deltas"].append({"id": "SD-0100", "event": "EV-99", "type": "MAGIC", "status": "PLANNED"})
        self.dump(self.deltas_path(), deltas)
        found = categories(self.findings())
        self.assertIn("INVALID_ENUM", found)
        self.assertIn("STATE_WITHOUT_CAUSE", found)

    def test_cli_plan_and_queries(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = sr.main(["--mode", "plan", "--runtime", str(self.rt), "--canon", str(self.canon),
                            "--cartography", str(CARTO)])
        self.assertEqual(code, 0)
        self.assertIn("modo plan", out.getvalue())
        with contextlib.redirect_stdout(io.StringIO()) as out:
            sr.main(["--canon", str(self.canon), "--is-true", "UNK-SR-SELKA-DEATH"])
        self.assertIn("CANON_UNKNOWN", out.getvalue())


class Slice3Mutations(unittest.TestCase):
    """Uma mutação por teste sobre a cópia do runtime real (7 eventos, 14 deltas, cenário PASS)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sr_s3_"))
        self.canon = self.tmp / "canon"
        self.rt = self.tmp / "rt"
        shutil.copytree(CANON, self.canon)
        shutil.copytree(FIXTURE_RT, self.rt)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def load(self, path):
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def dump(self, path, doc):
        path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def seed_path(self, name):
        return self.canon / "seeds" / name

    def ledger_path(self):
        return self.rt / "canon" / "CAUSAL_LEDGER.yaml"

    def deltas_path(self):
        return self.rt / "canon" / "SEM_ROSTO_STATE_DELTAS.yaml"

    def event(self, ledger, eid):
        return next(e for e in ledger["events"] if e["id"] == eid)

    def sd(self, deltas, did):
        return next(d for d in deltas["deltas"] if d["id"] == did)

    def findings(self):
        return sr.validate(self.canon, CARTO, self.rt)[0]

    def assertCategory(self, category, severity=None):
        found = self.findings()
        hits = [f for f in found if f["category"] == category and (severity is None or f["severity"] == severity)]
        self.assertTrue(hits, f"{category} não encontrado em {categories(found)}")
        return hits

    def assertNoBlocking(self):
        self.assertEqual([f for f in self.findings() if f["severity"] in sr.BLOCKING], [])

    # --- FACE (TEST 01, 02, 22)
    def test_face_reveal_invalid_visibility(self):
        d = self.load(self.deltas_path())
        self.sd(d, "SD-0009")["reader_visibility"] = "RECONSTRUCTIBLE"
        self.dump(self.deltas_path(), d)
        self.assertCategory("FACE_REVEAL_VIOLATION", "BLOCKER")

    def test_face_reveal_pass_baseline(self):
        self.assertNoBlocking()

    def test_facial_reconstructibility_violation(self):
        d = self.load(self.deltas_path())
        sd9 = self.sd(d, "SD-0009")
        sd9["reconstructibility"] = "RECONSTRUCTIBLE_FACE"
        sd9["reader_visibility"] = "NON_RECONSTRUCTIBLE"
        self.dump(self.deltas_path(), d)
        self.assertCategory("FACIAL_RECONSTRUCTIBILITY_VIOLATION", "BLOCKER")

    def test_self_face_violation(self):   # TEST 22
        d = self.load(self.deltas_path())
        sd9 = self.sd(d, "SD-0009")
        sd9["kind"] = "SELF_VIEWING"
        sd9["subject"] = "CHR-FX-A"
        sd9["deliberate"] = {"subject": True, "viewers": []}
        self.dump(self.deltas_path(), d)
        self.assertCategory("SELF_FACE_VIOLATION", "BLOCKER")

    def test_nonconsensual_exposure_unmarked(self):
        d = self.load(self.deltas_path())
        sd9 = self.sd(d, "SD-0009")
        sd9["consent_ref"] = None
        sd9["setting"] = "PUBLIC"
        self.dump(self.deltas_path(), d)
        self.assertCategory("NONCONSENSUAL_EXPOSURE_UNMARKED", "HIGH")

    def test_facial_record_unclassified(self):
        d = self.load(self.deltas_path())
        self.sd(d, "SD-0009")["record"] = {"id": "ITM-FX-01", "external_lawful": True,
                                            "local_possession_status": "LAWFUL", "local_exposure_status": "UNLAWFUL"}
        self.dump(self.deltas_path(), d)
        self.assertCategory("FACIAL_RECORD_UNCLASSIFIED", "HIGH")

    def test_external_legality_collapsed(self):
        d = self.load(self.deltas_path())
        self.sd(d, "SD-0009")["record"] = {"id": "ITM-FX-01", "external_lawful": True}
        self.sd(d, "SD-0009")["authorization"] = "SFE-0001"
        self.dump(self.deltas_path(), d)
        self.assertCategory("EXTERNAL_LEGALITY_COLLAPSED", "HIGH")

    def test_face_description_suspected(self):
        led = self.load(self.ledger_path())
        self.event(led, "EV-02")["evidence_to_reader"] = ["B sorriu para A antes de contar o rumor."]
        self.dump(self.ledger_path(), led)
        self.assertCategory("FACE_DESCRIPTION_SUSPECTED", "MEDIUM")

    def test_pediatric_eroticization(self):
        led = self.load(self.ledger_path())
        self.event(led, "EV-01")["participants"] = ["CHR-FX-A", "CHR-FX-D"]
        led["characters"].append({"id": "CHR-FX-D", "major": False, "age": 9, "age_source": "fixture",
                                  "ground_truth": [{"id": "GT-FX-D-01", "kind": "FEAR", "statement": "x"}]})
        self.dump(self.ledger_path(), led)
        d = self.load(self.deltas_path())
        sd9 = self.sd(d, "SD-0009")
        sd9["event"], sd9["subject"], sd9["kind"] = "EV-01", "CHR-FX-D", "EXPOSURE"
        sd9["setting"], sd9["legal_reading"] = "PUBLIC", "EXPOSURE"
        self.dump(self.deltas_path(), d)
        self.assertCategory("PEDIATRIC_EROTICIZATION", "BLOCKER")

    # --- FRC (TEST 23, 24, 25)
    def test_frc_fragment_cited_without_existing(self):
        d = self.load(self.deltas_path())
        d["face_fragments"][0]["combinable_with"] = ["FRG-9999"]
        self.dump(self.deltas_path(), d)
        self.assertCategory("SYSTEM_CAPABILITY_AS_INSTANCE", "BLOCKER")

    def test_frc_composite_reader_visible(self):
        d = self.load(self.deltas_path())
        d["face_fragments"].append({"id": "FRG-0002", "subject": "CHR-FX-B", "carrier": "EV-05",
                                    "class": "PARTIALLY_FACIAL", "combinable_with": [], "combined_class": None,
                                    "reader_visibility": "NON_RECONSTRUCTIBLE"})
        d["face_fragments"][0]["combinable_with"] = ["FRG-0002"]
        d["face_fragments"][0]["combined_class"] = "RECONSTRUCTIBLE_FACE"
        self.dump(self.deltas_path(), d)
        self.assertCategory("FACIAL_RECONSTRUCTIBILITY_VIOLATION", "BLOCKER")

    def test_frc_composite_engine_only_passes(self):   # TEST 24
        d = self.load(self.deltas_path())
        d["face_fragments"].append({"id": "FRG-0002", "subject": "CHR-FX-B", "carrier": "EV-05",
                                    "class": "PARTIALLY_FACIAL", "combinable_with": [], "combined_class": None,
                                    "reader_visibility": "NONE"})
        d["face_fragments"][0]["combinable_with"] = ["FRG-0002"]
        d["face_fragments"][0]["combined_class"] = "RECONSTRUCTIBLE_FACE"
        self.dump(self.deltas_path(), d)
        self.assertNoBlocking()

    # --- SFE (TEST 19, 20)
    def test_sfe_incomplete(self):
        d = self.load(self.deltas_path())
        del d["sealed_evidence"][0]["necessity"]
        self.dump(self.deltas_path(), d)
        self.assertCategory("SEALED_EVIDENCE_INCOMPLETE", "BLOCKER")

    def test_sfe_public_access(self):   # TEST 20
        d = self.load(self.deltas_path())
        d["sealed_evidence"][0]["access_log"][0]["authorized"] = False
        self.dump(self.deltas_path(), d)
        self.assertCategory("SEALED_EVIDENCE_PUBLIC", "BLOCKER")

    def test_sfe_unbounded_authority(self):   # TEST 19
        d = self.load(self.deltas_path())
        d["sealed_evidence"][0]["capturing_authority"] = "INST-OCP"
        del d["sealed_evidence"][0]["procedure"]
        self.dump(self.deltas_path(), d)
        self.assertCategory("FACIAL_AUTHORITY_UNBOUNDED", "BLOCKER")

    def test_sfe_derived_copy_unprotected(self):
        d = self.load(self.deltas_path())
        d["sealed_evidence"][0]["derived_copies"] = ["SFE-9999"]
        self.dump(self.deltas_path(), d)
        self.assertCategory("DERIVED_COPY_UNPROTECTED", "HIGH")

    def test_sfe_access_unlogged(self):
        d = self.load(self.deltas_path())
        d["sealed_evidence"][0]["access_log"] = []
        self.dump(self.deltas_path(), d)
        self.assertCategory("SEALED_ACCESS_UNLOGGED", "HIGH")

    # --- Tattoo (HL-19)
    def test_tattoo_numeric_combination(self):
        d = self.load(self.deltas_path())
        d["tattoos"][0]["encodes_digits"] = True
        self.dump(self.deltas_path(), d)
        self.assertCategory("TATTOO_NUMERIC_COMBINATION", "BLOCKER")

    def test_tattoo_depicts_face(self):
        d = self.load(self.deltas_path())
        d["tattoos"][0]["depicts_face"] = True
        self.dump(self.deltas_path(), d)
        self.assertCategory("FACIAL_RECONSTRUCTIBILITY_VIOLATION", "BLOCKER")

    # --- Combination (TEST 15; HL-07, HL-23)
    def test_universal_combination(self):
        d = self.load(self.deltas_path())
        d["combinations"][0]["coffer"] = ["COF-FX-0001", "COF-FX-0002"]
        self.dump(self.deltas_path(), d)
        self.assertCategory("UNIVERSAL_COMBINATION", "BLOCKER")

    def test_combination_revealed_for_convenience(self):
        d = self.load(self.deltas_path())
        d["combinations"][0]["value_status"] = "REVEALED_TO_READER"
        d["combinations"][0]["value_ref"] = "1234"
        self.dump(self.deltas_path(), d)
        self.assertCategory("COMBINATION_REVEALED_FOR_CONVENIENCE", "HIGH")

    def test_combination_value_without_proposal(self):
        d = self.load(self.deltas_path())
        d["combinations"][0]["value_ref"] = "1234"
        self.dump(self.deltas_path(), d)
        self.assertCategory("IMPROVISED_CANON", "BLOCKER")

    def test_combination_as_removal_authority(self):   # TEST 15
        led = self.load(self.ledger_path())
        led["events"].append({"id": "EV-08", "status": "PLANNED", "chapter": 11, "structural": False,
                              "kind": ["REMOVE_COFFER"], "actor": "CHR-FX-A", "participants": ["CHR-FX-A", "CHR-FX-B"],
                              "facts": ["A remove o cofre de B."], "caused_by": ["EV-05"],
                              "acts_on_knowledge": ["SR:CMB:FULL:CMB-0001"]})
        self.dump(self.ledger_path(), led)
        self.assertCategory("COMBINATION_AS_REMOVAL_AUTHORITY", "BLOCKER")

    def test_combination_removal_with_authority_passes(self):
        led = self.load(self.ledger_path())
        led["events"].append({"id": "EV-08", "status": "PLANNED", "chapter": 11, "structural": False,
                              "kind": ["REMOVE_COFFER"], "actor": "CHR-FX-A", "participants": ["CHR-FX-A", "CHR-FX-B"],
                              "facts": ["A remove o cofre de B, com autorização institucional dupla."],
                              "caused_by": ["EV-05"], "acts_on_knowledge": ["SR:CMB:FULL:CMB-0001"],
                              "removal_authority": True})
        self.dump(self.ledger_path(), led)
        self.assertNotIn("COMBINATION_AS_REMOVAL_AUTHORITY", categories(self.findings()))

    def test_consent_inference_violation_lock_manipulation(self):   # TEST 16
        led = self.load(self.ledger_path())
        led["events"].append({"id": "EV-08", "status": "PLANNED", "chapter": 11, "structural": False,
                              "kind": ["LOCK_MANIPULATION"], "actor": "CHR-FX-A", "participants": ["CHR-FX-A", "CHR-FX-B"],
                              "facts": ["A manipula o lock do cofre de B."], "caused_by": ["EV-05"],
                              "acts_on_knowledge": ["SR:CMB:PARTIAL:CMB-0001"]})
        self.dump(self.ledger_path(), led)
        self.assertCategory("CONSENT_INFERENCE_VIOLATION", "BLOCKER")

    def test_character_knowledge_leak_partial_combination(self):
        led = self.load(self.ledger_path())
        led["events"].append({"id": "EV-08", "status": "PLANNED", "chapter": 11, "structural": False,
                              "kind": ["LOCK_MANIPULATION"], "actor": "CHR-FX-A", "participants": ["CHR-FX-A", "CHR-FX-B"],
                              "facts": ["A tenta com um valor incompleto."], "caused_by": ["EV-05"],
                              "acts_on_knowledge": ["SR:CMB:PARTIAL:CMB-0001"],
                              "consent": {"canonical": "CONSENSUAL", "manipulation_present": False,
                                          "power_imbalance_present": False, "ability_to_refuse": "FULL",
                                          "boundary_state": "NEGOTIATED", "perceived": {}}})
        self.dump(self.ledger_path(), led)
        self.assertCategory("CHARACTER_KNOWLEDGE_LEAK", "HIGH")

    # --- Civic (HL-09)
    def test_physical_return_as_reactivation(self):   # HL-09
        d = self.load(self.deltas_path())
        for delta in d["deltas"]:
            if delta["id"] in ("SD-0011", "SD-0012"):
                delta["preconditions_met"] = []
        self.dump(self.deltas_path(), d)
        self.assertCategory("PHYSICAL_RETURN_AS_REACTIVATION", "BLOCKER")

    # --- Recognition / identity (HL-24)
    def test_signature_as_proof(self):
        d = self.load(self.deltas_path())
        rec = self.sd(d, "SD-0014")
        rec["used_as"] = "PROOF"
        self.dump(self.deltas_path(), d)
        cats = categories(self.findings())
        self.assertIn("SIGNATURE_AS_PROOF", cats)

    def test_coffer_signature_as_proof(self):
        d = self.load(self.deltas_path())
        rec = self.sd(d, "SD-0014")
        rec["used_as"] = "PROOF"
        rec["channels_used"] = ["COFFER"]
        self.dump(self.deltas_path(), d)
        found = self.findings()
        self.assertTrue(any(f["rule"] == "SR-COF-05" for f in found))
        self.assertTrue(any(f["rule"] == "SR-IDS-03" for f in found))

    # --- Non-human (TEST 08, 09)
    def test_residual_without_rational_path(self):
        d = self.load(self.deltas_path())
        self.sd(d, "SD-0013")["human_explanations_available"] = []
        self.dump(self.deltas_path(), d)
        self.assertCategory("RESIDUAL_WITHOUT_RATIONAL_PATH", "HIGH")

    def test_residual_with_explanation_passes(self):   # TEST 09
        self.assertNotIn("RESIDUAL_WITHOUT_RATIONAL_PATH", categories(self.findings()))

    def test_ambiguity_ungrounded(self):
        d = self.load(self.deltas_path())
        self.sd(d, "SD-0013")["register"] = "AMBIGUOUS"
        self.dump(self.deltas_path(), d)
        self.assertCategory("AMBIGUITY_UNGROUNDED", "MEDIUM")

    def test_supernatural_confirmation(self):   # TEST 08
        led = self.load(self.ledger_path())
        self.event(led, "EV-07")["facts"].append("Foi um fantasma que a guiou de volta.")
        self.dump(self.ledger_path(), led)
        self.assertCategory("SUPERNATURAL_CONFIRMATION", "BLOCKER")

    def test_non_human_overuse(self):
        d = self.load(self.deltas_path())
        for i, ch in enumerate((11, 12), start=15):
            d["deltas"].append({"id": f"SD-{i:04d}", "event": "EV-07", "type": "ANOMALY", "status": "PLANNED",
                                "chapter": ch, "register": "RESIDUAL", "human_explanations_available": ["GT-FX-A-01"],
                                "residual_detail": "x"})
        self.dump(self.deltas_path(), d)
        self.assertCategory("NON_HUMAN_OVERUSE", "MEDIUM")

    # --- The Pull (HL-02, extra structural)
    def test_pull_magical_causality(self):
        led = self.load(self.ledger_path())
        self.event(led, "EV-07")["caused_by"] = []
        self.dump(self.ledger_path(), led)
        self.assertCategory("MAGICAL_CAUSALITY", "BLOCKER")

    # --- Manfred / Selka (TEST 07, 30)
    def test_manfred_universal_causality(self):   # TEST 07
        led = self.load(self.ledger_path())
        led["events"].append({"id": "EV-08", "status": "PLANNED", "chapter": 11, "structural": False,
                              "kind": ["REVELATION"], "actor": "FAM-MANFRED", "participants": ["FAM-MANFRED"],
                              "facts": ["Os Manfred apagaram os registros."], "caused_by": ["EV-03"]})
        self.dump(self.ledger_path(), led)
        self.assertCategory("MANFRED_UNIVERSAL_CAUSALITY", "BLOCKER")

    def test_manfred_lexical_suspected(self):
        led = self.load(self.ledger_path())
        self.event(led, "EV-03")["facts"].append("Os Manfred apagaram os quarenta anos.")
        self.dump(self.ledger_path(), led)
        self.assertCategory("MANFRED_UNIVERSAL_CAUSALITY", "MEDIUM")

    def test_selka_book1_history_lock(self):
        led = self.load(self.ledger_path())
        led["events"].append({"id": "EV-08", "status": "PLANNED", "chapter": 11, "structural": False,
                              "kind": ["FIND_GRAVE"], "actor": "CHR-FX-A", "participants": ["CHR-FX-A", "ENT-SELKA"],
                              "facts": ["A encontra o túmulo de Selka."], "caused_by": ["EV-03"]})
        self.dump(self.ledger_path(), led)
        self.assertCategory("BOOK1_HISTORY_LOCK_VIOLATION", "BLOCKER")

    def test_selka_as_the_key(self):   # TEST 30
        led = self.load(self.ledger_path())
        # um único evento ensina ao leitor um registro de MYS-SELKA (CR-P12-03) e registros de
        # DUAS outras mysteries reservadas (CR-P10-02 -> MYS-FORTY-YEARS, CR-P11-04 -> MYS-MANFRED-ROLE)
        self.event(led, "EV-03")["knowledge_delta"] = [
            {"knower": "READER", "learns": ["CR-P12-03", "CR-P10-02", "CR-P11-04"]}]
        self.dump(self.ledger_path(), led)
        self.assertCategory("SELKA_AS_THE_KEY", "BLOCKER")

    def test_selka_ontology_leak(self):
        led = self.load(self.ledger_path())
        self.event(led, "EV-02")["facts"].append("A alma de Selka age agora sobre A, vinda do inferno.")
        self.dump(self.ledger_path(), led)
        self.assertCategory("SELKA_ONTOLOGY_LEAK", "BLOCKER")

    # --- Jurisdiction / technology / coffer lexical
    def test_extraterritorial_power(self):
        led = self.load(self.ledger_path())
        self.event(led, "EV-04")["facts"].append("A OCP prendeu fora de Redmur.")
        self.dump(self.ledger_path(), led)
        self.assertCategory("EXTRATERRITORIAL_POWER", "BLOCKER")

    def test_sovereignty_assumed(self):
        led = self.load(self.ledger_path())
        self.event(led, "EV-04")["facts"].append("Redmur é um Estado soberano e independente.")
        self.dump(self.ledger_path(), led)
        self.assertCategory("SOVEREIGNTY_ASSUMED", "BLOCKER")

    def test_forbidden_technology_present(self):
        led = self.load(self.ledger_path())
        self.event(led, "EV-01")["facts"].append("Uma IA central onisciente vigiava todos os rostos.")
        self.dump(self.ledger_path(), led)
        self.assertCategory("FORBIDDEN_TECHNOLOGY_PRESENT", "BLOCKER")

    def test_external_purge_assumed(self):   # TEST 21
        led = self.load(self.ledger_path())
        self.event(led, "EV-04")["facts"].append("A OCP apagou o registro facial dela em Glasgow.")
        self.dump(self.ledger_path(), led)
        self.assertCategory("EXTERNAL_PURGE_ASSUMED", "HIGH")

    def test_coffer_mechanics_violation(self):
        led = self.load(self.ledger_path())
        self.event(led, "EV-05")["evidence_to_reader"] = ["O pescoço sustentava todo o peso do cofre."]
        self.dump(self.ledger_path(), led)
        self.assertCategory("COFFER_MECHANICS_VIOLATION", "MEDIUM")

    def test_technology_creep_battery_only(self):
        led = self.load(self.ledger_path())
        self.event(led, "EV-05")["facts"].append("Ela sobrevivia apenas com a bateria do cofre.")
        self.dump(self.ledger_path(), led)
        self.assertCategory("TECHNOLOGY_CREEP", "HIGH")

    # --- Child protocol relabel (HL-25)
    def test_cpr_relabels_six_month_leak(self):
        led = self.load(self.ledger_path())
        self.event(led, "EV-03")["knowledge_delta"].append({"knower": "CHR-FX-A", "learns": ["UNK-SR-SIX-MONTH-CONTENTS"]})
        self.dump(self.ledger_path(), led)
        found = self.findings()
        self.assertTrue(any(f["rule"] == "SR-CPR-01" for f in found))
        self.assertTrue(any(f["rule"] == "SR-KN-03" for f in found))

    # --- Lock coverage regression: package mode should have ~26/28 implemented
    def test_lock_coverage_near_complete(self):
        _, summary = sr.validate(self.canon, CARTO)
        self.assertGreaterEqual(summary["lock_coverage"]["implemented"], 26)
        self.assertLessEqual(summary["lock_coverage"]["planned_only"], 2)



if __name__ == "__main__":
    unittest.main()
