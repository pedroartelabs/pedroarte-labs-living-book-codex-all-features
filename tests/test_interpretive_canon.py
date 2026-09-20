"""Testes do validador `check_interpretive_canon.py` — Slices 1 e 2 da capability
`LIVING_THEORY_ENGINE` (ver docs/sdd/LIVING_THEORY_ENGINE_SDD_v0.1.md, seções 35 e 41).

Cada mutação isolada, aplicada a uma CÓPIA do runtime fixture "O Sino de Vale
Alto", precisa produzir a categoria de achado exata. 100% offline.

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_interpretive_canon -v
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import check_causal_ledger as cl  # noqa: E402
import check_interpretive_canon as ic  # noqa: E402

SCRIPT = REPO / "engine" / "scripts" / "check_interpretive_canon.py"
TEMPLATE_PATH = REPO / "engine" / "templates" / "INTERPRETIVE_CANON_TEMPLATE.yaml"
# Não chamar a pasta de `runtime/`: o .gitignore ignora qualquer diretório com esse nome.
FIXTURE_RUNTIME = REPO / "tests" / "fixtures" / "living_theory" / "runtime_sino_vale_alto"
_FIXTURE_CACHE = ic.load_runtime(FIXTURE_RUNTIME)


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def fixture():
    return copy.deepcopy(_FIXTURE_CACHE)


def run(ctx: dict, runtime_mode: bool = True) -> list[dict]:
    return ic.validate(**ctx, runtime_mode=runtime_mode)


def model(ctx: dict) -> dict:
    return ic.analyze(**ctx, runtime_mode=True)[1]


def matching(findings: list[dict], category: str) -> list[dict]:
    return [f for f in findings if f["category"] == category]


def question(ctx: dict, qid: str) -> dict:
    return next(q for q in ctx["canon"]["questions"] if q["id"] == qid)


def interpretation(ctx: dict, iid: str) -> dict:
    qid = iid.split("/")[0]
    return next(i for i in question(ctx, qid)["interpretations"] if i["id"] == iid)


def evidence(ctx: dict, eid: str) -> dict:
    return next(e for e in ctx["canon"]["evidence"] if e["id"] == eid)


def never_question(qid: str, unknown: str = "CANON:UNK-001") -> dict:
    return {
        "id": qid, "question": "Pergunta extra?", "axis": "PSYCHOLOGICAL", "half_life": "HIGH",
        "half_life_rationale": "Dura.", "resolution_policy": "NEVER", "unknown_ref": unknown,
        "prohibited_refs": ["CANON:PRO-003"], "shape": "BINARY", "min_viable_at_end": 2,
        "interpretations": [{"id": f"{qid}/A", "thesis": "Sim."}, {"id": f"{qid}/B", "thesis": "Não."}],
    }


def thresholds(ctx: dict) -> dict:
    return ctx["book_spec"]["spec"]["features"]["living_theory"]["thresholds"]


class _Base(unittest.TestCase):
    def assertCategory(self, findings, category, severity=None):
        found = matching(findings, category)
        self.assertTrue(found, f"esperava {category}; achados: {[f['category'] for f in findings]}")
        if severity is not None:
            self.assertTrue(all(f["severity"] == severity for f in found),
                            f"{category} deveria ser {severity}: {found}")
        return found

    def assertNoCategory(self, findings, category):
        self.assertFalse(matching(findings, category), f"não esperava {category}: {matching(findings, category)}")


# =============================================================================
# Slice 1 — modelo mínimo
# =============================================================================

class TestTemplateAndFixtureAreValid(_Base):
    def test_template_has_no_findings(self):
        self.assertEqual(ic.validate(load(TEMPLATE_PATH)), [])

    def test_fixture_runtime_has_no_findings(self):
        self.assertEqual(run(fixture()), [])

    def test_fixture_ledger_is_valid_for_the_causal_ledger_validator(self):
        # REUSE real: o canon interpretativo convive com o ledger do motor, não com um simulacro.
        ledger = fixture()["ledger"]
        hard = [f for f in cl.validate(ledger) if f["severity"] in ("HIGH", "BLOCKER")]
        self.assertEqual(hard, [])

    def test_resolved_question_may_become_fact(self):
        # EV-04 declara como fato a tese de Q-LOCK/TOMAS: legítimo, porque Q-LOCK é RESOLVED_AT.
        self.assertNoCategory(run(fixture()), "THEORY_PROMOTED_TO_FACT")

    def test_template_fields_match_validator_vocabulary(self):
        template = load(TEMPLATE_PATH)
        readings = [r for e in template["evidence"] for r in (e.get("readings") or {}).values()]
        levels = {
            "root": set(template),
            "metadata": set(template["metadata"]),
            "policy": set(template["policy"]),
            "question": set().union(*(set(q) for q in template["questions"])),
            "interpretation": set().union(*(set(i) for q in template["questions"] for i in q["interpretations"])),
            "partition": set().union(*(set(p) for p in template["partitions"])),
            "relation": set().union(*(set(r) for r in template["relations"])),
            "narrator": set().union(*(set(n) for n in template["narrators"])),
            "evidence": set().union(*(set(e) for e in template["evidence"])),
            "reading": set().union(*(set(r) for r in readings)),
            "fair_herring": set().union(*(set(e["fair_herring"]) for e in template["evidence"] if e["fair_herring"])),
        }
        for level, keys in levels.items():
            with self.subTest(level=level):
                self.assertEqual(keys, ic.KNOWN_FIELDS[level])

    def test_without_context_resolution_rules_do_not_run(self):
        ctx = fixture()
        question(ctx, "Q-BELL")["unknown_ref"] = "CANON:UNK-404"
        evidence(ctx, "EVD-02")["anchor"] = "TURN:99"
        self.assertEqual(ic.validate(ctx["canon"]), [])


class TestContractIntegrity(_Base):
    def test_wrong_kind(self):
        ctx = fixture()
        ctx["canon"]["kind"] = "NarcisoInterpretiveCanon"
        self.assertCategory(run(ctx), "CONTRACT_INVALID", "HIGH")

    def test_wrong_owner(self):
        ctx = fixture()
        ctx["canon"]["metadata"]["owner"] = "LEAD_NOVELIST"
        self.assertCategory(run(ctx), "CONTRACT_INVALID", "HIGH")

    def test_unknown_field_typo(self):
        ctx = fixture()
        question(ctx, "Q-BELL")["unkown_ref"] = "CANON:UNK-001"
        found = self.assertCategory(run(ctx), "UNKNOWN_FIELD", "MEDIUM")
        self.assertIn("unkown_ref", found[0]["evidence"])

    def test_reserved_future_blocks_are_accepted(self):
        ctx = fixture()
        ctx["canon"]["mutations"] = []
        ctx["canon"]["destabilizers"] = []
        self.assertEqual(run(ctx), [])

    def test_question_duplicate(self):
        ctx = fixture()
        ctx["canon"]["questions"].append(copy.deepcopy(question(ctx, "Q-LOCK")))
        self.assertCategory(run(ctx), "QUESTION_DUPLICATE", "HIGH")

    def test_question_id_malformed(self):
        ctx = fixture()
        question(ctx, "Q-LOCK")["id"] = "lock"
        self.assertCategory(run(ctx), "ID_MALFORMED", "HIGH")

    def test_interpretation_id_mismatch(self):
        ctx = fixture()
        interpretation(ctx, "Q-GUILT/GUILTY")["id"] = "Q-BELL/GUILTY"
        self.assertCategory(run(ctx), "INTERPRETATION_ID_MISMATCH", "HIGH")

    def test_invalid_axis(self):
        ctx = fixture()
        question(ctx, "Q-BELL")["axis"] = "SPIRITUAL"
        self.assertCategory(run(ctx), "INVALID_ENUM", "HIGH")

    def test_binary_with_three_interpretations(self):
        ctx = fixture()
        question(ctx, "Q-GUILT")["interpretations"].append({"id": "Q-GUILT/BOTH", "thesis": "As duas coisas."})
        self.assertCategory(run(ctx), "SHAPE_MISMATCH", "HIGH")

    def test_min_viable_above_interpretations(self):
        ctx = fixture()
        question(ctx, "Q-BELL")["min_viable_at_end"] = 4
        self.assertCategory(run(ctx), "INVALID_VIABILITY", "HIGH")

    def test_empty_thesis(self):
        ctx = fixture()
        interpretation(ctx, "Q-BELL/WIND")["thesis"] = ""
        found = self.assertCategory(run(ctx), "FIELD_MISSING", "HIGH")
        self.assertIn("Q-BELL/WIND.thesis", found[0]["evidence"])

    def test_too_many_interpretations(self):
        ctx = fixture()
        for letter in "ABCD":
            question(ctx, "Q-BELL")["interpretations"].append({"id": f"Q-BELL/X{letter}", "thesis": f"Leitura {letter}."})
        self.assertCategory(run(ctx), "TOO_MANY_INTERPRETATIONS", "MEDIUM")

    def test_sequel_dependency(self):
        ctx = fixture()
        question(ctx, "Q-GUILT")["resolution_policy"] = "SEQUEL"
        findings = run(ctx)
        self.assertCategory(findings, "SEQUEL_DEPENDENCY", "HIGH")
        self.assertFalse([f for f in matching(findings, "INVALID_ENUM") if "resolution_policy" in f["evidence"]])

    def test_resolved_at_missing(self):
        ctx = fixture()
        question(ctx, "Q-LOCK")["resolved_at"] = None
        self.assertCategory(run(ctx), "RESOLUTION_ANCHOR_INVALID", "HIGH")

    def test_resolved_at_unknown_event(self):
        ctx = fixture()
        question(ctx, "Q-LOCK")["resolved_at"] = "LEDGER:EV-404"
        self.assertCategory(run(ctx), "RESOLUTION_ANCHOR_INVALID", "HIGH")

    def test_never_question_with_resolved_at(self):
        ctx = fixture()
        question(ctx, "Q-BELL")["resolved_at"] = "LEDGER:EV-01"
        self.assertCategory(run(ctx), "RESOLUTION_ANCHOR_INVALID", "HIGH")

    def test_unknown_threshold(self):
        ctx = fixture()
        thresholds(ctx)["max_seeds"] = 2
        self.assertCategory(run(ctx), "THRESHOLD_UNKNOWN", "LOW")


class TestDualitySeedsAndHalfLife(_Base):
    def test_too_many_seeds_and_open_questions(self):
        ctx = fixture()
        ctx["canon"]["questions"] += [never_question("Q-EXTRA-A"), never_question("Q-EXTRA-B")]
        findings = run(ctx)
        self.assertCategory(findings, "TOO_MANY_DUALITY_SEEDS", "MEDIUM")
        self.assertCategory(findings, "TOO_MANY_OPEN_QUESTIONS", "MEDIUM")

    def test_book_spec_threshold_raises_limit(self):
        ctx = fixture()
        ctx["canon"]["questions"] += [never_question("Q-EXTRA-A"), never_question("Q-EXTRA-B")]
        thresholds(ctx).update({"max_duality_seeds": 5, "max_never_questions": 5})
        findings = run(ctx)
        self.assertNoCategory(findings, "TOO_MANY_DUALITY_SEEDS")
        self.assertNoCategory(findings, "TOO_MANY_OPEN_QUESTIONS")

    def test_book_spec_threshold_beats_canon_policy(self):
        ctx = fixture()
        ctx["canon"]["policy"]["thresholds"] = {"max_duality_seeds": 1}
        self.assertNoCategory(run(ctx), "TOO_MANY_DUALITY_SEEDS")  # BOOK_SPEC declara 3

    def test_no_durable_question(self):
        ctx = fixture()
        for qid in ("Q-BELL", "Q-GUILT"):
            question(ctx, qid)["half_life"] = "MEDIUM"
        self.assertCategory(run(ctx), "NO_DURABLE_QUESTION", "MEDIUM")

    def test_high_half_life_needs_rationale(self):
        ctx = fixture()
        question(ctx, "Q-BELL")["half_life_rationale"] = None
        self.assertCategory(run(ctx), "HALF_LIFE_RATIONALE_MISSING", "MEDIUM")

    def test_factual_high_is_inflated(self):
        ctx = fixture()
        question(ctx, "Q-LOCK").update(half_life="HIGH", half_life_rationale="Dura.")
        self.assertCategory(run(ctx), "HALF_LIFE_INFLATED", "MEDIUM")

    def _lock_as_never(self, ctx):
        question(ctx, "Q-LOCK").update(resolution_policy="NEVER", resolved_at=None,
                                       unknown_ref="CANON:UNK-001", prohibited_refs=["CANON:PRO-003"])

    def test_factual_never_is_withheld_fact(self):
        ctx = fixture()
        self._lock_as_never(ctx)
        self.assertCategory(run(ctx), "FACT_WITHHELD_AS_MYSTERY", "HIGH")

    def test_factual_never_with_rule_ref_is_allowed(self):
        ctx = fixture()
        self._lock_as_never(ctx)
        question(ctx, "Q-LOCK")["rule_ref"] = "RULE:IR-01"
        findings = run(ctx)
        self.assertNoCategory(findings, "FACT_WITHHELD_AS_MYSTERY")
        self.assertNoCategory(findings, "RULE_REF_INVALID")

    def test_rule_ref_unresolved(self):
        ctx = fixture()
        question(ctx, "Q-LOCK")["rule_ref"] = "RULE:IR-404"
        self.assertCategory(run(ctx), "RULE_REF_INVALID", "HIGH")

    def test_never_without_unknown_ref(self):
        ctx = fixture()
        question(ctx, "Q-BELL")["unknown_ref"] = None
        self.assertCategory(run(ctx), "UNKNOWN_REF_MISSING", "HIGH")

    def test_never_without_prohibited_refs(self):
        ctx = fixture()
        question(ctx, "Q-BELL")["prohibited_refs"] = []
        self.assertCategory(run(ctx), "PROHIBITED_REFS_MISSING", "MEDIUM")


class TestTheoryGraph(_Base):
    def test_relation_to_missing_interpretation(self):
        ctx = fixture()
        ctx["canon"]["relations"].append({"from": "Q-BELL/IRENE", "to": "Q-GUILT/NOPE", "kind": "IMPLIES"})
        self.assertCategory(run(ctx), "RELATION_UNRESOLVED", "HIGH")

    def test_invalid_relation_kind(self):
        ctx = fixture()
        ctx["canon"]["relations"].append({"from": "Q-BELL/IRENE", "to": "Q-GUILT/GUILTY", "kind": "CAUSES"})
        self.assertCategory(run(ctx), "INVALID_ENUM", "HIGH")

    def test_excludes_within_question_is_redundant(self):
        ctx = fixture()
        ctx["canon"]["relations"].append({"from": "Q-GUILT/GUILTY", "to": "Q-GUILT/INNOCENT", "kind": "EXCLUDES"})
        self.assertCategory(run(ctx), "RELATION_REDUNDANT", "LOW")

    def test_implies_within_question_is_contradictory(self):
        ctx = fixture()
        ctx["canon"]["relations"].append({"from": "Q-GUILT/GUILTY", "to": "Q-GUILT/INNOCENT", "kind": "IMPLIES"})
        self.assertCategory(run(ctx), "RELATION_CONTRADICTORY", "HIGH")

    def test_amplifies_and_excludes_same_pair(self):
        ctx = fixture()
        ctx["canon"]["relations"].append({"from": "Q-BELL/IRENE", "to": "Q-GUILT/GUILTY", "kind": "EXCLUDES"})
        self.assertCategory(run(ctx), "RELATION_CONTRADICTORY", "HIGH")

    def test_transitive_implication_reaches_exclusion(self):
        ctx = fixture()
        ctx["canon"]["relations"] += [
            {"from": "Q-GUILT/INNOCENT", "to": "Q-BELL/WIND", "kind": "IMPLIES"},
            {"from": "Q-BELL/WIND", "to": "Q-LOCK/TOMAS", "kind": "IMPLIES"},
            {"from": "Q-GUILT/INNOCENT", "to": "Q-LOCK/TOMAS", "kind": "EXCLUDES"},
        ]
        found = self.assertCategory(run(ctx), "RELATION_CONTRADICTORY", "HIGH")
        self.assertTrue(any("Q-GUILT/INNOCENT" in f["evidence"] for f in found))

    def test_revelation_forces_never_question_closed(self):
        ctx = fixture()
        ctx["canon"]["relations"].append({"from": "Q-LOCK/MAYOR", "to": "Q-BELL/IRENE", "kind": "EXCLUDES"})
        found = self.assertCategory(run(ctx), "GRAPH_FORCES_RESOLUTION", "BLOCKER")
        self.assertIn("Q-LOCK/MAYOR", found[0]["evidence"])

    def test_implication_from_revelation_forces_never_question_closed(self):
        ctx = fixture()
        ctx["canon"]["relations"].append({"from": "Q-LOCK/TOMAS", "to": "Q-GUILT/GUILTY", "kind": "IMPLIES"})
        self.assertCategory(run(ctx), "GRAPH_FORCES_RESOLUTION", "BLOCKER")

    def test_partition_member_from_other_question(self):
        ctx = fixture()
        ctx["canon"]["partitions"][0]["sides"]["YES"].append("Q-GUILT/GUILTY")
        self.assertCategory(run(ctx), "PARTITION_INVALID", "HIGH")

    def test_partition_member_on_two_sides(self):
        ctx = fixture()
        ctx["canon"]["partitions"][0]["sides"]["YES"].append("Q-BELL/IRENE")
        self.assertCategory(run(ctx), "PARTITION_INVALID", "HIGH")

    def test_unquoted_yes_no_sides_are_rejected(self):
        # Achado real do Slice 1: YAML 1.1 lê YES/NO sem aspas como booleano.
        ctx = fixture()
        ctx["canon"]["partitions"] = yaml.safe_load(
            "- id: Q-BELL~SUPERNATURAL\n  of: Q-BELL\n  question: Houve algo sobrenatural?\n"
            "  sides: {YES: [Q-BELL/DEAD], NO: [Q-BELL/IRENE, Q-BELL/WIND]}\n")
        self.assertCategory(run(ctx), "PARTITION_INVALID", "HIGH")

    def test_partition_id_not_matching_seed(self):
        ctx = fixture()
        ctx["canon"]["partitions"][0]["id"] = "Q-GUILT~SUPERNATURAL"
        self.assertCategory(run(ctx), "PARTITION_INVALID", "HIGH")

    def test_partition_of_binary_is_redundant(self):
        ctx = fixture()
        ctx["canon"]["partitions"].append({"id": "Q-GUILT~SPLIT", "of": "Q-GUILT", "question": "Culpada?",
                                           "sides": {"YES": ["Q-GUILT/GUILTY"], "NO": ["Q-GUILT/INNOCENT"]}})
        self.assertCategory(run(ctx), "PARTITION_REDUNDANT", "LOW")

    def test_too_many_partitions(self):
        ctx = fixture()
        for n in range(4):
            ctx["canon"]["partitions"].append({"id": f"Q-BELL~P{n}", "of": "Q-BELL", "question": f"Partição {n}?",
                                               "sides": {"A": ["Q-BELL/IRENE"], "B": ["Q-BELL/WIND"]}})
        self.assertCategory(run(ctx), "TOO_MANY_PARTITIONS", "MEDIUM")


class TestNoHiddenAnswer(_Base):
    def test_policy_required(self):
        ctx = fixture()
        ctx["canon"]["policy"]["no_hidden_answer"] = False
        self.assertCategory(run(ctx), "HIDDEN_ANSWER_PRESENT", "BLOCKER")

    def test_answer_key_in_question_accent_and_case_insensitive(self):
        ctx = fixture()
        question(ctx, "Q-BELL")["Resposta"] = "Q-BELL/WIND"
        found = self.assertCategory(run(ctx), "HIDDEN_ANSWER_PRESENT", "BLOCKER")
        self.assertIn("Resposta", found[0]["evidence"])

    def test_answer_key_nested_in_interpretation(self):
        ctx = fixture()
        interpretation(ctx, "Q-GUILT/INNOCENT")["author-answer"] = True
        self.assertCategory(run(ctx), "HIDDEN_ANSWER_PRESENT", "BLOCKER")

    def test_answer_key_nested_in_evidence_reading(self):
        ctx = fixture()
        evidence(ctx, "EVD-05")["readings"]["Q-GUILT/GUILTY"]["verdade"] = True
        self.assertCategory(run(ctx), "HIDDEN_ANSWER_PRESENT", "BLOCKER")

    def test_open_belief_cannot_be_false(self):
        ctx = fixture()
        next(b for b in ctx["ledger"]["beliefs"] if b["id"] == "RB-BELL")["truth"] = "FALSE"
        self.assertCategory(run(ctx), "LEDGER_BELIEF_CLOSES_NEVER_QUESTION", "BLOCKER")

    def test_open_belief_must_stay_left_open(self):
        ctx = fixture()
        next(b for b in ctx["ledger"]["beliefs"] if b["id"] == "RB-GUILT")["left_open"] = False
        self.assertCategory(run(ctx), "LEDGER_BELIEF_CLOSES_NEVER_QUESTION", "BLOCKER")

    def test_open_belief_cannot_be_revised(self):
        ctx = fixture()
        next(e for e in ctx["ledger"]["events"] if e["id"] == "EV-04")["beliefs"]["revises"].append("RB-BELL")
        self.assertCategory(run(ctx), "LEDGER_BELIEF_CLOSES_NEVER_QUESTION", "BLOCKER")

    def test_ground_truth_reaching_reader(self):
        ctx = fixture()
        ctx["ledger"]["characters"][0]["ground_truth"][0]["reader_access"] = "OPEN"
        self.assertCategory(run(ctx), "GROUND_TRUTH_HOLDS_ANSWER", "HIGH")

    def test_ground_truth_stating_one_side(self):
        ctx = fixture()
        gt = ctx["ledger"]["characters"][0]["ground_truth"][0]
        gt["kind"] = "SECRET"
        gt["statement"] = interpretation(ctx, "Q-GUILT/GUILTY")["thesis"]
        found = self.assertCategory(run(ctx), "GROUND_TRUTH_HOLDS_ANSWER", "HIGH")
        self.assertIn("Q-GUILT/GUILTY", found[0]["evidence"])

    def test_non_contradiction_ground_truth_without_thesis_is_allowed(self):
        ctx = fixture()
        ctx["ledger"]["characters"][0]["ground_truth"][0]["kind"] = "WOUND"
        self.assertNoCategory(run(ctx), "GROUND_TRUTH_HOLDS_ANSWER")


class TestCanonBoundary(_Base):
    def test_interpretation_as_cause(self):
        ctx = fixture()
        ctx["ledger"]["events"][0]["caused_by"].append("Q-BELL/IRENE")
        found = self.assertCategory(run(ctx), "THEORY_AS_CAUSE", "BLOCKER")
        self.assertEqual(found[0]["chapter"], 1)

    def test_evidence_id_as_cause(self):
        ctx = fixture()
        ctx["ledger"]["events"][2]["caused_by"].append("EVD-07")
        self.assertCategory(run(ctx), "THEORY_AS_CAUSE", "BLOCKER")

    def test_never_thesis_promoted_to_ledger_fact(self):
        ctx = fixture()
        ctx["ledger"]["events"][1]["facts"].append(interpretation(ctx, "Q-BELL/DEAD")["thesis"])
        found = self.assertCategory(run(ctx), "THEORY_PROMOTED_TO_FACT", "BLOCKER")
        self.assertEqual(found[0]["chapter"], 2)

    def test_never_thesis_promoted_to_registry_fact(self):
        ctx = fixture()
        ctx["registry"]["events"].append({"id": "FACT-099", "status": "CANON_APPROVED",
                                          "fact": "Ficou provado que Irene deixou a vela acesa sabendo que o padre dormia."})
        found = self.assertCategory(run(ctx), "THEORY_PROMOTED_TO_FACT", "BLOCKER")
        self.assertIn("FACT-099", found[0]["evidence"])

    def test_unknown_ref_not_in_registry(self):
        ctx = fixture()
        question(ctx, "Q-BELL")["unknown_ref"] = "CANON:UNK-404"
        self.assertCategory(run(ctx), "UNKNOWN_REF_INVALID", "HIGH")

    def test_unknown_ref_wrong_status(self):
        ctx = fixture()
        ctx["registry"]["unknowns"][0]["status"] = "REVEALED"
        self.assertCategory(run(ctx), "UNKNOWN_REF_INVALID", "HIGH")

    def test_prohibited_ref_not_in_registry(self):
        ctx = fixture()
        question(ctx, "Q-GUILT")["prohibited_refs"] = ["CANON:PRO-404"]
        self.assertCategory(run(ctx), "UNKNOWN_REFERENCE", "HIGH")

    def test_interpretation_matching_prohibited_terms(self):
        ctx = fixture()
        interpretation(ctx, "Q-BELL/WIND")["thesis"] = "Tomás armou o sino com um mecanismo escondido."
        found = self.assertCategory(run(ctx), "PROHIBITED_INTERPRETATION", "BLOCKER")
        self.assertIn("PRO-001", found[0]["evidence"])

    def test_interpretation_matching_prohibited_statement(self):
        ctx = fixture()
        interpretation(ctx, "Q-GUILT/GUILTY")["thesis"] = "O incêndio foi causado por um raio enviado como castigo divino."
        found = self.assertCategory(run(ctx), "PROHIBITED_INTERPRETATION", "BLOCKER")
        self.assertIn("PRO-002", found[0]["evidence"])

    def test_runtime_without_registry(self):
        ctx = fixture()
        ctx["registry"] = None
        self.assertCategory(run(ctx), "CONTEXT_MISSING", "HIGH")

    def test_runtime_without_chapter_architecture(self):
        ctx = fixture()
        ctx["chapter_architecture"] = None
        found = self.assertCategory(run(ctx), "CONTEXT_MISSING", "HIGH")
        self.assertIn("chapter_architecture", found[0]["evidence"])

    def test_runtime_without_ledger_but_ledger_references(self):
        ctx = fixture()
        ctx["ledger"] = None
        found = self.assertCategory(run(ctx), "LEDGER_REFERENCE_WITHOUT_LEDGER", "HIGH")
        self.assertEqual({f["evidence"] for f in found}, {"Q-BELL", "Q-GUILT", "Q-LOCK"})


# =============================================================================
# Slice 2 — Evidence Ledger
# =============================================================================

class TestEvidenceIntegrity(_Base):
    def test_evidence_block_missing(self):
        ctx = fixture()
        del ctx["canon"]["evidence"]
        self.assertCategory(run(ctx), "EVIDENCE_LEDGER_MISSING", "HIGH")

    def test_evidence_duplicate(self):
        ctx = fixture()
        ctx["canon"]["evidence"].append(copy.deepcopy(evidence(ctx, "EVD-09")))
        self.assertCategory(run(ctx), "EVIDENCE_DUPLICATE", "HIGH")

    def test_evidence_id_malformed(self):
        ctx = fixture()
        evidence(ctx, "EVD-09")["id"] = "clue-9"
        self.assertCategory(run(ctx), "ID_MALFORMED", "HIGH")

    def test_anchor_not_resolving(self):
        ctx = fixture()
        evidence(ctx, "EVD-02")["anchor"] = "TURN:9"
        self.assertCategory(run(ctx), "EVIDENCE_ANCHOR_UNRESOLVED", "HIGH")

    def test_ledger_anchor_to_missing_event_creates_fact(self):
        ctx = fixture()
        evidence(ctx, "EVD-09")["anchor"] = "LEDGER:EV-99"
        self.assertCategory(run(ctx), "EVIDENCE_CREATES_FACT", "HIGH")

    def test_canon_anchor_to_missing_fact_creates_fact(self):
        ctx = fixture()
        evidence(ctx, "EVD-09")["anchor"] = "CANON:FACT-999"
        self.assertCategory(run(ctx), "EVIDENCE_ANCHOR_UNLOCATED", "HIGH")  # CANON: nunca localiza capítulo

    def test_anchor_without_chapter(self):
        ctx = fixture()
        evidence(ctx, "EVD-09")["anchor"] = "LEDGER:GT-IRENE-01"
        self.assertCategory(run(ctx), "EVIDENCE_ANCHOR_UNLOCATED", "HIGH")

    def test_realized_without_text_anchor(self):
        ctx = fixture()
        evidence(ctx, "EVD-09")["status"] = "REALIZED"
        self.assertCategory(run(ctx), "TEXT_ANCHOR_MISSING", "HIGH")

    def test_text_anchor_malformed(self):
        ctx = fixture()
        evidence(ctx, "EVD-09")["text_anchor"] = "TEXT:5:sem aspas"
        self.assertCategory(run(ctx), "EVIDENCE_ANCHOR_UNRESOLVED", "HIGH")

    def test_text_anchor_in_other_chapter(self):
        ctx = fixture()
        evidence(ctx, "EVD-09")["text_anchor"] = 'TEXT:4:"Irene pede perdão"'
        self.assertCategory(run(ctx), "EVIDENCE_CHAPTER_MISMATCH", "MEDIUM")

    def test_ledger_event_missing(self):
        ctx = fixture()
        evidence(ctx, "EVD-09")["ledger_event"] = "EV-99"
        self.assertCategory(run(ctx), "UNKNOWN_REFERENCE", "HIGH")

    def test_ledger_event_in_other_chapter(self):
        ctx = fixture()
        evidence(ctx, "EVD-02")["ledger_event"] = "EV-02"
        self.assertCategory(run(ctx), "EVIDENCE_CHAPTER_MISMATCH", "MEDIUM")

    def test_support_to_unknown_interpretation(self):
        ctx = fixture()
        evidence(ctx, "EVD-02")["support"]["Q-BELL/GHOST"] = "S"
        self.assertCategory(run(ctx), "UNKNOWN_REFERENCE", "HIGH")

    def test_support_incomplete(self):
        ctx = fixture()
        del evidence(ctx, "EVD-02")["support"]["Q-BELL/DEAD"]
        self.assertCategory(run(ctx), "SUPPORT_INCOMPLETE", "HIGH")

    def test_support_value_invalid(self):
        ctx = fixture()
        evidence(ctx, "EVD-02")["support"]["Q-BELL/DEAD"] = "Y"
        self.assertCategory(run(ctx), "INVALID_ENUM", "HIGH")

    def test_channel_invalid(self):
        ctx = fixture()
        evidence(ctx, "EVD-02")["channel"] = "VIBES"
        self.assertCategory(run(ctx), "INVALID_ENUM", "HIGH")

    def test_projected_role_is_not_declarable(self):
        ctx = fixture()
        evidence(ctx, "EVD-01")["role"] = "DOUBLE_EVIDENCE"
        self.assertCategory(run(ctx), "ROLE_NOT_DECLARABLE", "HIGH")

    def test_visual_channel_without_feature(self):
        ctx = fixture()
        evidence(ctx, "EVD-02")["channel"] = "ILLUSTRATION"
        self.assertCategory(run(ctx), "VISUAL_EVIDENCE_DISABLED", "HIGH")

    def test_observable_with_answer_lexicon(self):
        ctx = fixture()
        evidence(ctx, "EVD-02")["observable"] = "A viga range e fica claro que foi o vento."
        self.assertCategory(run(ctx), "OBSERVABLE_STATES_ANSWER", "HIGH")

    def test_observable_with_never_thesis(self):
        ctx = fixture()
        evidence(ctx, "EVD-09")["observable"] = "Irene tentou salvar o padre e carrega uma culpa que não lhe pertence."
        found = self.assertCategory(run(ctx), "OBSERVABLE_STATES_ANSWER", "HIGH")
        self.assertIn("Q-GUILT/INNOCENT", found[0]["evidence"])

    def test_observable_with_prohibited_inference(self):
        ctx = fixture()
        evidence(ctx, "EVD-02")["observable"] = "Tomás armou o sino antes do amanhecer."
        self.assertCategory(run(ctx), "OBSERVABLE_STATES_ANSWER", "HIGH")


class TestEvidenceBalance(_Base):
    def test_interpretation_starved(self):
        ctx = fixture()
        evidence(ctx, "EVD-11")["support"]["Q-BELL/WIND"] = "-"
        found = self.assertCategory(run(ctx), "EVIDENCE_STARVED", "MEDIUM")
        self.assertIn("Q-BELL/WIND", found[0]["evidence"])

    def test_interpretation_without_any_evidence(self):
        ctx = fixture()
        for eid in ("EVD-01", "EVD-02", "EVD-11"):
            evidence(ctx, eid)["support"]["Q-BELL/WIND"] = "-"
        found = self.assertCategory(run(ctx), "INTERPRETATION_WITHOUT_EVIDENCE", "HIGH")
        self.assertEqual(found[0]["evidence"], "Q-BELL/WIND")

    def test_evidence_row_without_support(self):
        ctx = fixture()
        evidence(ctx, "EVD-02")["support"]["Q-BELL/WIND"] = "C"
        self.assertCategory(run(ctx), "EVIDENCE_WITHOUT_SUPPORT", "MEDIUM")

    def test_interpretation_unchallenged(self):
        ctx = fixture()
        for eid in ("EVD-08", "EVD-10"):
            evidence(ctx, eid)["support"]["Q-BELL/WIND"] = "-"
        self.assertCategory(run(ctx), "INTERPRETATION_UNCHALLENGED", "MEDIUM")

    def test_exclusion_needs_approval(self):
        ctx = fixture()
        evidence(ctx, "EVD-09")["support"]["Q-BELL/WIND"] = "X"
        self.assertCategory(run(ctx), "EXCLUSION_WITHOUT_APPROVAL", "HIGH")

    def test_approved_exclusion_is_allowed(self):
        ctx = fixture()
        evidence(ctx, "EVD-09")["support"]["Q-BELL/WIND"] = "X"
        evidence(ctx, "EVD-09")["approval"] = "APR-THEORY-01"
        findings = run(ctx)
        self.assertNoCategory(findings, "EXCLUSION_WITHOUT_APPROVAL")
        self.assertNoCategory(findings, "QUESTION_COLLAPSED")

    def test_evidence_collapses_question(self):
        ctx = fixture()
        row = evidence(ctx, "EVD-09")
        row["support"].update({"Q-BELL/IRENE": "X", "Q-BELL/WIND": "X"})
        row["approval"] = "APR-THEORY-01"
        findings = run(ctx)
        self.assertCategory(findings, "EVIDENCE_COLLAPSES_QUESTION", "BLOCKER")
        self.assertCategory(findings, "QUESTION_COLLAPSED", "BLOCKER")

    def test_retired_rows_do_not_count(self):
        ctx = fixture()
        evidence(ctx, "EVD-11")["status"] = "RETIRED"
        found = self.assertCategory(run(ctx), "EVIDENCE_STARVED", "MEDIUM")
        self.assertIn("Q-BELL/WIND", found[0]["evidence"])

    def test_interpretation_dominance(self):
        ctx = fixture()
        thresholds(ctx)["max_support_ratio"] = 1.2
        self.assertCategory(run(ctx), "INTERPRETATION_DOMINANCE", "MEDIUM")


class TestDoubleEvidence(_Base):
    def test_double_without_readings(self):
        ctx = fixture()
        evidence(ctx, "EVD-01")["readings"] = {}
        found = self.assertCategory(run(ctx), "DOUBLE_EVIDENCE_WITHOUT_READING", "HIGH")
        self.assertIn("EVD-01", found[0]["evidence"])

    def test_double_with_weak_side(self):
        ctx = fixture()
        evidence(ctx, "EVD-01")["readings"]["Q-BELL/IRENE"]["strength"] = "WEAK"
        self.assertCategory(run(ctx), "DOUBLE_EVIDENCE_WEAK_SIDE", "HIGH")

    def test_double_evidence_tilted(self):
        ctx = fixture()
        evidence(ctx, "EVD-06")["readings"]["Q-GUILT/GUILTY"]["strength"] = "STRONG"
        evidence(ctx, "EVD-07")["readings"]["Q-GUILT/GUILTY"]["strength"] = "STRONG"
        found = self.assertCategory(run(ctx), "DOUBLE_EVIDENCE_TILTED", "MEDIUM")
        self.assertIn("Q-GUILT", found[0]["evidence"])

    def test_reading_without_corroboration(self):
        ctx = fixture()
        evidence(ctx, "EVD-01")["readings"]["Q-BELL/IRENE"]["corroborated_by"] = []
        self.assertCategory(run(ctx), "READING_UNCORROBORATED", "MEDIUM")

    def test_corroboration_that_does_not_support_the_same_reading(self):
        ctx = fixture()
        evidence(ctx, "EVD-01")["readings"]["Q-BELL/IRENE"]["corroborated_by"] = ["EVD-04"]
        self.assertCategory(run(ctx), "READING_UNCORROBORATED", "MEDIUM")

    def test_corroboration_to_missing_evidence(self):
        ctx = fixture()
        evidence(ctx, "EVD-01")["readings"]["Q-BELL/IRENE"]["corroborated_by"] = ["EVD-99"]
        self.assertCategory(run(ctx), "UNKNOWN_REFERENCE", "HIGH")

    def test_reading_for_unsupported_interpretation(self):
        ctx = fixture()
        evidence(ctx, "EVD-10")["readings"]["Q-BELL/WIND"] = {"reading": "x", "strength": "MEDIUM",
                                                             "corroborated_by": ["EVD-02"]}
        self.assertCategory(run(ctx), "READING_WITHOUT_SUPPORT", "LOW")

    def test_double_evidence_scarce(self):
        ctx = fixture()
        thresholds(ctx)["min_double_evidence"] = 4
        found = self.assertCategory(run(ctx), "DOUBLE_EVIDENCE_SCARCE", "MEDIUM")
        self.assertIn("Q-GUILT", found[0]["evidence"])

    def test_double_evidence_clustered(self):
        ctx = fixture()
        evidence(ctx, "EVD-07")["anchor"] = "TURN:3"
        found = self.assertCategory(run(ctx), "DOUBLE_EVIDENCE_CLUSTERED", "LOW")
        self.assertEqual(found[0]["chapter"], 3)


class TestNarratorsAndTestimony(_Base):
    def test_testimony_without_qualification(self):
        ctx = fixture()
        for eid in ("EVD-04", "EVD-08"):
            evidence(ctx, eid)["support"]["Q-LOCK/MAYOR"] = "-"
        found = self.assertCategory(run(ctx), "TESTIMONY_UNQUALIFIED", "MEDIUM")
        self.assertIn("EVD-03", found[0]["evidence"])

    def test_declared_voice_qualifies_testimony(self):
        ctx = fixture()
        del ctx["canon"]["narrators"]
        self.assertNoCategory(run(ctx), "TESTIMONY_UNQUALIFIED")  # EVD-05 tem complicações de outras fontes

    def test_unreliability_without_tell(self):
        ctx = fixture()
        ctx["canon"]["narrators"][0]["tells"] = []
        self.assertCategory(run(ctx), "UNRELIABILITY_WITHOUT_TELL", "MEDIUM")

    def test_tell_to_missing_evidence(self):
        ctx = fixture()
        ctx["canon"]["narrators"][0]["tells"] = ["EVD-99"]
        self.assertCategory(run(ctx), "UNKNOWN_REFERENCE", "HIGH")

    def test_narrator_voice_unknown(self):
        ctx = fixture()
        ctx["canon"]["narrators"][0]["voice"] = "CHR-NOBODY"
        self.assertCategory(run(ctx), "UNKNOWN_REFERENCE", "HIGH")

    def test_narrator_scope_unresolved(self):
        ctx = fixture()
        ctx["canon"]["narrators"][0]["scope"] = "TURN:9"
        self.assertCategory(run(ctx), "NARRATOR_SCOPE_UNRESOLVED", "HIGH")


class TestRedHerrings(_Base):
    def _fair(self, ctx):
        return evidence(ctx, "EVD-03")["fair_herring"]

    def test_red_herring_without_fair_block(self):
        ctx = fixture()
        evidence(ctx, "EVD-03")["fair_herring"] = None
        found = self.assertCategory(run(ctx), "FIELD_MISSING", "HIGH")
        self.assertIn("EVD-03.fair_herring", found[0]["evidence"])

    def test_cause_is_a_trope(self):
        ctx = fixture()
        self._fair(ctx)["in_world_cause"] = "TROPE:mentiroso"
        self.assertCategory(run(ctx), "RED_HERRING_WITHOUT_CAUSE", "HIGH")

    def test_cause_does_not_resolve(self):
        ctx = fixture()
        self._fair(ctx)["in_world_cause"] = "LEDGER:GT-NOPE-01"
        self.assertCategory(run(ctx), "RED_HERRING_WITHOUT_CAUSE", "HIGH")

    def test_reveal_before_the_herring(self):
        ctx = fixture()
        self._fair(ctx)["survives_reveal"] = "TURN:1"
        self.assertCategory(run(ctx), "RED_HERRING_NOT_SURVIVING", "HIGH")

    def test_no_fair_counter_evidence(self):
        ctx = fixture()
        self._fair(ctx)["counter_available_before"] = []
        self.assertCategory(run(ctx), "RED_HERRING_UNFAIR", "HIGH")

    def test_counter_evidence_only_at_the_reveal(self):
        ctx = fixture()
        self._fair(ctx)["counter_available_before"] = ["EVD-08"]  # capítulo 5, o mesmo da revelação
        self.assertCategory(run(ctx), "RED_HERRING_UNFAIR", "HIGH")

    def test_herring_without_after_function(self):
        ctx = fixture()
        self._fair(ctx)["after_function"] = None
        self.assertCategory(run(ctx), "RED_HERRING_ORPHAN", "MEDIUM")

    def test_herring_points_where_it_does_not_support(self):
        ctx = fixture()
        self._fair(ctx)["points_toward"] = "Q-LOCK/TOMAS"
        self.assertCategory(run(ctx), "RED_HERRING_INVALID", "HIGH")

    def test_reliable_narrator_lying(self):
        ctx = fixture()
        evidence(ctx, "EVD-03")["source"] = "NARRATOR"
        self.assertCategory(run(ctx), "NARRATOR_LIE", "BLOCKER")

    def test_declared_unreliable_narrator_may_mislead_in_scope(self):
        ctx = fixture()
        evidence(ctx, "EVD-03")["source"] = "NARRATOR"
        ctx["canon"]["narrators"].append({"id": "NRL-02", "voice": "NARRATOR", "scope": "TURN:2",
                                          "unreliability": "O narrador repete a versão da vila.", "tells": ["EVD-04"]})
        self.assertNoCategory(run(ctx), "NARRATOR_LIE")

    def test_too_many_red_herrings(self):
        ctx = fixture()
        thresholds(ctx)["max_red_herring_share"] = 0.05
        self.assertCategory(run(ctx), "RED_HERRING_EXCESS", "MEDIUM")


class TestSignalNoise(_Base):
    def test_chapter_overdense(self):
        ctx = fixture()
        extra = copy.deepcopy(evidence(ctx, "EVD-02"))
        extra["id"] = "EVD-12"
        ctx["canon"]["evidence"].append(extra)
        found = self.assertCategory(run(ctx), "EVIDENCE_OVERDENSE", "MEDIUM")
        self.assertEqual(found[0]["chapter"], 1)

    def test_too_salient(self):
        ctx = fixture()
        evidence(ctx, "EVD-02")["salience"] = "NOTICEABLE"
        self.assertCategory(run(ctx), "THEORY_BAIT_SALIENCE", "MEDIUM")

    def test_reread_layer_thin(self):
        ctx = fixture()
        for row in ctx["canon"]["evidence"]:
            row["discoverable_on"] = "FIRST_READ"
        self.assertCategory(run(ctx), "REREAD_LAYER_THIN", "MEDIUM")

    def test_evidence_everywhere(self):
        ctx = fixture()
        evidence(ctx, "EVD-04")["anchor"] = "TURN:4"
        evidence(ctx, "EVD-10")["anchor"] = "TURN:6"
        self.assertCategory(run(ctx), "EVIDENCE_EVERYWHERE", "MEDIUM")


class TestObservabilityQueries(_Base):
    def test_ledger_report(self):
        report = ic.ledger_report(model(fixture()), "Q-GUILT")
        guilty = report["interpretations"]["Q-GUILT/GUILTY"]
        self.assertEqual([e["evidence"] for e in guilty["S"]], ["EVD-07", "EVD-05", "EVD-06"])
        self.assertEqual([e["evidence"] for e in guilty["C"]], ["EVD-09", "EVD-10"])
        self.assertEqual(guilty["S"][1]["strength"], "STRONG")

    def test_double_report_by_question_and_partition(self):
        report = ic.double_report(model(fixture()), "Q-BELL")
        self.assertEqual([e["evidence"] for e in report["questions"]["Q-BELL"]],
                         ["EVD-01", "EVD-11", "EVD-08", "EVD-10"])
        partition = report["partitions"]["Q-BELL~SUPERNATURAL"]
        self.assertEqual(partition["double"], ["EVD-11", "EVD-08", "EVD-10"])
        self.assertEqual(partition["only"]["YES"], ["EVD-09"])
        self.assertEqual(partition["only"]["NO"], ["EVD-01", "EVD-02", "EVD-05", "EVD-06"])
        self.assertEqual(partition["unassigned"], [])

    def test_heatmap_report(self):
        report = ic.heatmap_report(model(fixture()))
        self.assertEqual(report["chapter_count"], 6)
        self.assertEqual(report["chapters_with_evidence"], 4)
        self.assertEqual(report["chapters"][1], {"total": 3, "double": 2, "questions": {"Q-BELL": 3, "Q-GUILT": 1}})
        self.assertEqual(report["over_limit"], [])


class TestCommandLine(_Base):
    def _cli(self, *args):
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True,
                              text=True, encoding="utf-8", env=env)

    def test_fixture_runtime_exit_zero(self):
        proc = self._cli("--runtime", FIXTURE_RUNTIME)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("registry=sim", proc.stdout)
        self.assertIn("chapter_architecture=sim", proc.stdout)

    def test_blocker_exit_one_with_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp) / "rt"
            shutil.copytree(FIXTURE_RUNTIME, runtime)
            path = runtime / "canon" / "INTERPRETIVE_CANON.yaml"
            canon = load(path)
            canon["questions"][0]["verdade"] = "Q-BELL/IRENE"
            path.write_text(yaml.safe_dump(canon, allow_unicode=True, sort_keys=False), encoding="utf-8")
            proc = self._cli("--runtime", runtime, "--json")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("HIDDEN_ANSWER_PRESENT", {f["category"] for f in payload["findings"]})
        self.assertTrue(payload["context"]["ledger"])

    def test_template_exit_zero(self):
        proc = self._cli("--canon", TEMPLATE_PATH)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_missing_canon_exit_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._cli("--runtime", tmp)
        self.assertEqual(proc.returncode, 2)

    def test_queries(self):
        proc = self._cli("--runtime", FIXTURE_RUNTIME, "--double", "Q-GUILT")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(json.loads(proc.stdout)["questions"]["Q-GUILT"]), 3)
        proc = self._cli("--runtime", FIXTURE_RUNTIME, "--heatmap")
        self.assertEqual(json.loads(proc.stdout)["chapters_with_evidence"], 4)
        proc = self._cli("--runtime", FIXTURE_RUNTIME, "--ledger", "Q-NOPE")
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
