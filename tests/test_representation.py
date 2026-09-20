"""Testes do Slice 1 de REPRESENTATION_INTEGRITY.

Ver docs/sdd/REPRESENTATION_INTEGRITY_SDD_v0.1.md (seções 12-14, 17, 29).

Padrão do repositório: `unittest`, 100% offline, uma mutação por teste
afirmando a CATEGORIA EXATA do achado (mesmo padrão de test_causal_ledger.py).
As mutações são feitas em cópias em memória de uma fixture válida.

    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_representation -v

As fixtures não contêm prosa nem conteúdo explícito: só fatos resumidos, ids
e números. Os testes de propriedade usam `random.Random(seed)` (sem
`hypothesis`, que não é dependência do repositório).
"""
from __future__ import annotations

import builtins
import copy
import json
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import check_causal_ledger as cl  # noqa: E402
import check_representation as cr  # noqa: E402

FIXTURE = REPO / "tests" / "fixtures" / "representation" / "runtime_vale_escuro" / "canon" / "CAUSAL_LEDGER.yaml"
POLICY = REPO / "tests" / "fixtures" / "representation" / "authors" / "test_author" / "REPRESENTATION_POLICY.v1.yaml"
LEDGER_TEMPLATE = REPO / "engine" / "templates" / "CAUSAL_LEDGER_TEMPLATE.yaml"
POLICY_TEMPLATE = REPO / "engine" / "templates" / "REPRESENTATION_POLICY_TEMPLATE.yaml"
SCRIPT = REPO / "engine" / "scripts" / "check_representation.py"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def ev(ledger: dict, event_id: str) -> dict:
    return next(e for e in ledger["events"] if e["id"] == event_id)


def char(ledger: dict, char_id: str) -> dict:
    return next(c for c in ledger["characters"] if c["id"] == char_id)


def cats(findings: list[dict]) -> list[str]:
    return sorted(f["category"] for f in findings)


def validate(ledger: dict, policy: dict | None = None):
    return cr.validate(ledger, policy)


class Base(unittest.TestCase):
    def setUp(self):
        self.ledger = copy.deepcopy(load(FIXTURE))
        self.policy = copy.deepcopy(load(POLICY))

    def run_cats(self, ledger=None, policy="default"):
        policy = self.policy if policy == "default" else policy
        return cats(validate(self.ledger if ledger is None else ledger, policy))


# ---------------------------------------------------------------------------
# Fixture, templates e contrato
# ---------------------------------------------------------------------------

class TestFixtureAndTemplates(Base):
    def test_fixture_has_no_findings(self):
        self.assertEqual(validate(self.ledger, self.policy), [])

    def test_fixture_is_clean_for_the_causal_ledger_validator(self):
        hard = [f for f in cl.validate(self.ledger) if f["severity"] in ("HIGH", "BLOCKER")]
        self.assertEqual(hard, [])

    def test_ledger_template_passes_both_validators(self):
        template = load(LEDGER_TEMPLATE)
        self.assertEqual([f for f in cr.validate(template) if f["severity"] in ("HIGH", "BLOCKER")], [])
        self.assertEqual([f for f in cl.validate(template) if f["severity"] in ("HIGH", "BLOCKER")], [])

    def test_policy_template_and_test_policy_are_valid(self):
        self.assertEqual(cr.check_policy(load(POLICY_TEMPLATE)), [])
        self.assertEqual(cr.check_policy(self.policy), [])

    def test_template_fields_match_validator(self):
        """Todo campo do bloco `representation` do template é conhecido pelo
        validador (padrão test_template_fields_match_validator do LTE)."""
        template = load(LEDGER_TEMPLATE)
        blocks = [e["representation"] for e in template["events"] if "representation" in e]
        self.assertTrue(blocks, "o template precisa exemplificar o bloco representation")
        known = {"content_classes", "themes", "narrative_function", "intended", "realized",
                 "status", "gap", "age_at_event"}
        for block in blocks:
            self.assertLessEqual(set(block), known)
            self.assertLessEqual(set(block["content_classes"]), cr.CONTENT_CLASSES)
            self.assertIn(block["intended"]["execution"], cr.EXECUTIONS)
        policy_known = {"apiVersion", "kind", "metadata", "permissions", "additional_hard_boundaries",
                        "always_review", "on_constrained_representation", "thresholds",
                        "reader_warnings", "lexicons"}
        self.assertLessEqual(set(load(POLICY_TEMPLATE)), policy_known)

    def test_vocabularies_never_contain_forbidden_as_writable_value(self):
        self.assertNotIn("FORBIDDEN", cr.EXECUTIONS)
        self.assertNotIn("FORBIDDEN", cr.STATUSES)


# ---------------------------------------------------------------------------
# Teste 1 e separação: tema pesado não é removido; contexto > keyword; P4
# ---------------------------------------------------------------------------

class TestThematicFreedomAndSeparation(Base):
    def test_heavy_themes_are_not_findings(self):
        """Teste 1 (SDD 29.3). A fixture combina abuso histórico, violência,
        automutilação e intimidade: zero achados. O validador não tem
        opinião sobre tema."""
        classes = {c for _, b in cr._events_with_block(self.ledger) for c in b["content_classes"]}
        self.assertLessEqual({"SEXUAL", "VIOLENCE", "SELF_HARM", "SEXUAL_VIOLENCE"}, classes)
        self.assertEqual(validate(self.ledger, self.policy), [])

    def test_validator_never_reads_files_or_prose(self):
        """Contexto > keyword: validate() é função pura sobre o dict do ledger;
        não abre manuscrito nem nenhum arquivo."""
        def boom(*a, **k):
            raise AssertionError("o validador não pode fazer I/O")
        with mock.patch.object(builtins, "open", boom), mock.patch.object(Path, "read_text", boom):
            self.assertEqual(validate(self.ledger, self.policy), [])

    def test_theme_words_and_fact_words_never_change_findings(self):
        baseline = validate(self.ledger, self.policy)
        mutated = copy.deepcopy(self.ledger)
        ev(mutated, "EV-V1")["representation"]["themes"] = ["assassinato", "tortura", "suicidio", "estupro"]
        ev(mutated, "EV-V1")["facts"] = ["C prepara um jantar para A e os dois conversam sobre o dia."]
        self.assertEqual(validate(mutated, self.policy), baseline)

    def test_representation_block_is_invisible_to_the_causal_ledger_validator(self):
        """P4: mudar (ou remover) qualquer campo de `representation` não altera
        um único achado de check_causal_ledger.validate."""
        stripped = copy.deepcopy(self.ledger)
        for e in stripped["events"]:
            e.pop("representation", None)
        self.assertEqual(cl.validate(self.ledger), cl.validate(stripped))
        rng = random.Random(4)
        for _ in range(50):
            mutated = copy.deepcopy(self.ledger)
            for _, block in cr._events_with_block(mutated):
                block["intended"]["intensity"] = rng.randint(0, 10)
                block["narrative_function"] = f"função {rng.random()}"
                block["status"] = rng.choice(["FULLY_REPRESENTED", "CONSTRAINED", "AUTHOR_REVIEW"])
            self.assertEqual(cl.validate(mutated), cl.validate(stripped))

    def test_provider_names_are_telemetry_only(self):
        baseline = validate(self.ledger, self.policy)
        mutated = copy.deepcopy(self.ledger)
        ev(mutated, "EV-V1")["representation"]["realized"]["generated_by"] = {
            "task": "T203_WRITE", "model_tier": "S", "model_actual": "qualquer-provider-x"}
        self.assertEqual(validate(mutated, self.policy), baseline)


# ---------------------------------------------------------------------------
# Integridade do bloco
# ---------------------------------------------------------------------------

class TestStructure(Base):
    def test_forbidden_is_not_a_writable_status(self):
        ev(self.ledger, "EV-V1")["representation"]["status"] = "FORBIDDEN"
        self.assertIn("INVALID_ENUM", self.run_cats())

    def test_forbidden_is_not_a_writable_execution(self):
        ev(self.ledger, "EV-V1")["representation"]["intended"]["execution"] = "FORBIDDEN"
        self.assertIn("INVALID_ENUM", self.run_cats())

    def test_unknown_content_class(self):
        ev(self.ledger, "EV-V1")["representation"]["content_classes"] = ["VIOLENCIA"]
        self.assertIn("INVALID_ENUM", self.run_cats())

    def test_empty_content_classes_is_incomplete(self):
        ev(self.ledger, "EV-V1")["representation"]["content_classes"] = []
        self.assertIn("REPRESENTATION_INCOMPLETE", self.run_cats())

    def test_narrative_function_is_mandatory(self):
        del ev(self.ledger, "EV-V1")["representation"]["narrative_function"]
        self.assertIn("REPRESENTATION_INCOMPLETE", self.run_cats())

    def test_intensity_out_of_range_and_bool_are_rejected(self):
        for bad in (11, -1, True, "alta"):
            ledger = copy.deepcopy(self.ledger)
            ev(ledger, "EV-V1")["representation"]["intended"]["intensity"] = bad
            self.assertIn("INVALID_ENUM", self.run_cats(ledger), bad)

    def test_realized_requires_status(self):
        del ev(self.ledger, "EV-05")["representation"]["status"]
        self.assertIn("REPRESENTATION_INCOMPLETE", self.run_cats())

    def test_planned_event_cannot_carry_realized(self):
        ev(self.ledger, "EV-05")["status"] = "PLANNED"
        self.assertIn("REALIZED_BEFORE_REALIZATION", self.run_cats())

    def test_invalid_policy_is_reported(self):
        self.policy["permissions"]["VIOLENCE"]["depiction_ceiling"] = "TUDO"
        self.assertIn("POLICY_INVALID", self.run_cats())


# ---------------------------------------------------------------------------
# Testes 9, 10, 11: gate adulto
# ---------------------------------------------------------------------------

class TestAdultAgeGate(Base):
    def test_adults_pass_the_age_gate(self):  # teste 11
        idx, _ = cl.build_indices(self.ledger)
        self.assertEqual(cr.age_verification(self.ledger, idx, ev(self.ledger, "EV-05")), "PASS")
        self.assertEqual(cr.age_verification(self.ledger, idx, ev(self.ledger, "EV-V1")), "N/A")

    def test_erotic_participant_under_18_fails(self):  # teste 9
        char(self.ledger, "CHR-A")["age"] = 17
        found = self.run_cats()
        self.assertIn("ADULT_SEDUCTION_FAIL", found)
        self.assertIn("HARD_BOUNDARY_MINOR_SEXUALIZATION", found)
        idx, _ = cl.build_indices(self.ledger)
        self.assertEqual(cr.age_verification(self.ledger, idx, ev(self.ledger, "EV-05")), "FAIL")

    def test_unknown_age_in_erotic_scene_fails(self):  # teste 10
        char(self.ledger, "CHR-B")["age"] = None
        found = self.run_cats()
        self.assertIn("ADULT_SEDUCTION_FAIL", found)
        self.assertIn("HARD_BOUNDARY_MINOR_SEXUALIZATION", found)
        idx, _ = cl.build_indices(self.ledger)
        self.assertEqual(cr.age_verification(self.ledger, idx, ev(self.ledger, "EV-05")), "FAIL")

    def test_result_is_fail_closed_for_the_age_gate(self):
        char(self.ledger, "CHR-A")["age"] = 17
        self.assertEqual(cr.classify(validate(self.ledger, self.policy), self.ledger), "FAIL_HARD_BOUNDARY")

    def test_sexual_class_without_adult_kind_is_caught(self):
        ev(self.ledger, "EV-05")["kind"] = ["CARE"]
        self.assertIn("ADULT_KIND_MISSING", self.run_cats())

    def test_missing_age_source_is_caught(self):
        del char(self.ledger, "CHR-A")["age_source"]
        self.assertIn("AGE_SOURCE_UNRESOLVED", self.run_cats())

    def test_age_at_event_cannot_launder_a_minor(self):
        char(self.ledger, "CHR-A")["age"] = 17
        ev(self.ledger, "EV-05")["representation"]["age_at_event"] = {"CHR-A": 30}
        self.assertIn("HARD_BOUNDARY_MINOR_SEXUALIZATION", self.run_cats())

    def test_flashback_minor_age_at_event_is_a_hard_boundary(self):
        ev(self.ledger, "EV-05")["representation"]["age_at_event"] = {"CHR-A": 16}
        self.assertIn("HARD_BOUNDARY_MINOR_SEXUALIZATION", self.run_cats())

    def test_hard_boundary_has_no_policy_override(self):
        """Nenhuma política, por mais permissiva, libera HB-01."""
        char(self.ledger, "CHR-A")["age"] = 17
        for family in cr.CONTENT_CLASSES:
            self.policy["permissions"][family] = {"depiction_ceiling": "CAN_BE_GRAPHICALLY_DEPICTED",
                                                   "central_theme": True}
        self.assertIn("HARD_BOUNDARY_MINOR_SEXUALIZATION", self.run_cats())


# ---------------------------------------------------------------------------
# Teste 8 e P3: hard boundary nunca vira gap
# ---------------------------------------------------------------------------

GAP = {"dimensions": ["ON_PAGE_PRESENCE"], "description": "Função não realizada, em uma frase.",
       "author_review": "RECOMMENDED"}


class TestHardBoundaryIsNotAGap(Base):
    def test_historical_abuse_as_non_sexualized_fact_is_allowed(self):
        """Assunto != sexualização: a fixture já contém abuso na infância como
        fato canônico (testemunho + consequência) e passa limpa."""
        self.assertEqual(validate(self.ledger, self.policy), [])

    def test_gap_on_minor_abuse_event_is_a_hard_boundary_gap(self):  # teste 8
        ev(self.ledger, "EV-H1")["representation"]["gap"] = copy.deepcopy(GAP)
        self.assertIn("HARD_BOUNDARY_GAP", self.run_cats())

    def test_limited_status_on_minor_abuse_event_is_a_hard_boundary_gap(self):
        ev(self.ledger, "EV-H1")["representation"]["status"] = "CONSTRAINED"
        self.assertIn("HARD_BOUNDARY_GAP", self.run_cats())

    def test_minor_abuse_event_never_yields_authorial_gap_findings(self):
        block = ev(self.ledger, "EV-H1")["representation"]
        block["intended"]["intensity"] = 6
        block["status"], block["gap"] = "CONSTRAINED", copy.deepcopy(GAP)
        found = self.run_cats()
        self.assertIn("HARD_BOUNDARY_GAP", found)
        self.assertNotIn("AUTHORIAL_GAP_MISSING", found)

    def test_minor_abuse_depiction_beyond_reference_only(self):
        for execution in ("FADE_TO_BLACK", "SENSITIVE", "NORMAL"):
            ledger = copy.deepcopy(self.ledger)
            ev(ledger, "EV-H1")["representation"]["intended"]["execution"] = execution
            self.assertIn("HARD_BOUNDARY_MINOR_ABUSE_DEPICTION", self.run_cats(ledger), execution)

    def test_minor_abuse_graphic_in_realized(self):
        ev(self.ledger, "EV-H1")["representation"]["realized"]["graphic"] = True
        self.assertIn("HARD_BOUNDARY_MINOR_ABUSE_DEPICTION", self.run_cats())

    def test_minor_abuse_in_same_chapter_as_erotic_event(self):
        ev(self.ledger, "EV-H1")["chapter"] = ev(self.ledger, "EV-05")["chapter"]
        self.assertIn("HARD_BOUNDARY_MINOR_ABUSE_DEPICTION", self.run_cats())

    def test_unknown_age_participant_is_treated_as_possible_minor(self):
        del ev(self.ledger, "EV-H1")["representation"]["age_at_event"]
        char(self.ledger, "CHR-C")["age"] = None
        ev(self.ledger, "EV-H1")["representation"]["intended"]["execution"] = "FADE_TO_BLACK"
        self.assertIn("HARD_BOUNDARY_MINOR_ABUSE_DEPICTION", self.run_cats())

    def test_adult_sexual_violence_is_a_theme_not_a_hard_boundary(self):
        """Entre adultos, SEXUAL_VIOLENCE é subject dentro da política da
        autora (aqui: CAN_BE_DEPICTED), não hard boundary."""
        block = ev(self.ledger, "EV-H1")["representation"]
        del block["age_at_event"]
        block["intended"] = {"execution": "FADE_TO_BLACK", "intensity": 5, "graphic": False}
        block["realized"] = {**block["realized"], "execution": "FADE_TO_BLACK", "intensity": 5, "graphic": False}
        self.assertEqual(validate(self.ledger, self.policy), [])

    def test_property_hard_boundary_never_passes_with_a_gap(self):
        """P3: qualquer combinação de status/gap/execução num evento HB-02
        que carregue gap ou status limitado é BLOCKER, nunca exit 0."""
        rng = random.Random(3)
        for _ in range(300):
            ledger = copy.deepcopy(self.ledger)
            block = ev(ledger, "EV-H1")["representation"]
            block["status"] = rng.choice(["FULLY_REPRESENTED", "CONSTRAINED", "AUTHOR_REVIEW"])
            if rng.random() < 0.6:
                block["gap"] = copy.deepcopy(GAP)
            block["realized"]["intensity"] = rng.randint(0, 10)
            block["intended"]["intensity"] = rng.randint(0, 10)
            found = validate(ledger, self.policy)
            has_gap = block.get("gap") is not None or block["status"] != "FULLY_REPRESENTED"
            if has_gap:
                self.assertTrue(any(f["severity"] == "BLOCKER" for f in found))
                self.assertEqual(cr.classify(found, ledger), "FAIL_HARD_BOUNDARY")


# ---------------------------------------------------------------------------
# Matriz SUBJECT_PERMISSION x SCENE_EXECUTION
# ---------------------------------------------------------------------------

class TestRepresentationMatrix(Base):
    def test_graphic_above_ceiling_exceeds_policy(self):
        ev(self.ledger, "EV-S1")["representation"]["intended"]["graphic"] = True   # SELF_HARM = CAN_BE_DEPICTED
        self.assertIn("REPRESENTATION_EXCEEDS_POLICY", self.run_cats())

    def test_realized_is_checked_too(self):
        ev(self.ledger, "EV-S1")["representation"]["realized"]["graphic"] = True
        self.assertIn("REPRESENTATION_EXCEEDS_POLICY", self.run_cats())

    def test_can_exist_allows_only_reference_only(self):
        self.policy["permissions"]["VIOLENCE"]["depiction_ceiling"] = "CAN_EXIST"
        self.assertIn("REPRESENTATION_EXCEEDS_POLICY", self.run_cats())   # EV-V1 é SENSITIVE

    def test_absent_family_defaults_to_can_exist(self):
        del self.policy["permissions"]["VIOLENCE"]
        self.assertIn("REPRESENTATION_EXCEEDS_POLICY", self.run_cats())

    def test_reference_only_is_valid_under_can_exist(self):
        self.policy["permissions"]["SELF_HARM"]["depiction_ceiling"] = "CAN_EXIST"
        self.assertEqual(validate(self.ledger, self.policy), [])   # EV-S1 é REFERENCE_ONLY

    def test_without_policy_the_matrix_is_not_applied(self):
        self.assertNotIn("REPRESENTATION_EXCEEDS_POLICY", cats(validate(self.ledger, None)))

    def test_property_ceiling_ladder_is_monotonic(self):
        """P5: o que é válido num nível continua válido no seguinte."""
        def valid(level: int, execution: str, graphic: bool) -> bool:
            ledger = copy.deepcopy(self.ledger)
            block = ev(ledger, "EV-V1")["representation"]
            block["intended"] = {"execution": execution, "intensity": 5, "graphic": graphic}
            block["realized"] = {**block["realized"], "execution": execution, "intensity": 5, "graphic": graphic}
            block.pop("gap", None)
            block["status"] = "FULLY_REPRESENTED"
            policy = {"kind": "RepresentationPolicy",
                      "permissions": {"VIOLENCE": {"depiction_ceiling": cr.DEPICTION_CEILINGS[level]}}}
            # só o EV-V1: os demais eventos não estão cobertos pela política mínima deste teste
            return not any(f["category"] == "REPRESENTATION_EXCEEDS_POLICY" and f["evidence"].startswith("EV-V1")
                           for f in cr.validate(ledger, policy))
        for execution in sorted(cr.EXECUTIONS):
            for graphic in (False, True):
                results = [valid(level, execution, graphic) for level in range(3)]
                self.assertEqual(results, sorted(results), (execution, graphic))
        self.assertTrue(valid(2, "NORMAL", True))
        self.assertFalse(valid(0, "NORMAL", False))


# ---------------------------------------------------------------------------
# Teste 7: Authorial Gap
# ---------------------------------------------------------------------------

class TestAuthorialGap(Base):
    def test_gap_is_created_when_needed(self):  # teste 7 (positivo)
        block = ev(self.ledger, "EV-V1")["representation"]
        self.assertEqual(block["status"], "CONSTRAINED")
        self.assertEqual(cr.gap_names(block), ["VIOLENCE_GRAPHIC_DETAIL_GAP"])
        self.assertEqual(validate(self.ledger, self.policy), [])

    def test_missing_gap_block_is_caught(self):  # teste 7 (negativo)
        del ev(self.ledger, "EV-V1")["representation"]["gap"]
        self.assertIn("AUTHORIAL_GAP_MISSING", self.run_cats())

    def test_reduction_declared_as_fully_represented_is_caught(self):
        block = ev(self.ledger, "EV-V1")["representation"]
        block["status"] = "FULLY_REPRESENTED"
        del block["gap"]
        self.assertIn("AUTHORIAL_GAP_MISSING", self.run_cats())

    def test_gap_on_a_fully_represented_scene_is_inconsistent(self):
        ev(self.ledger, "EV-05")["representation"]["gap"] = copy.deepcopy(GAP)
        self.assertIn("GAP_STATUS_INCONSISTENT", self.run_cats())

    def test_small_difference_below_threshold_needs_no_gap(self):
        block = ev(self.ledger, "EV-05")["representation"]
        block["realized"]["intensity"] = 5        # planejado 6: diferença 1 < gap_threshold 2
        self.assertEqual(validate(self.ledger, self.policy), [])

    def test_execution_drop_alone_requires_a_gap(self):
        block = ev(self.ledger, "EV-05")["representation"]
        block["realized"]["execution"] = "FADE_TO_BLACK"
        self.assertIn("AUTHORIAL_GAP_MISSING", self.run_cats())

    def test_graphic_drop_alone_requires_a_gap(self):
        block = ev(self.ledger, "EV-05")["representation"]
        block["intended"]["graphic"] = True
        self.assertIn("AUTHORIAL_GAP_MISSING", self.run_cats())

    def test_large_difference_must_escalate_to_author_review(self):
        block = ev(self.ledger, "EV-V1")["representation"]
        block["realized"]["intensity"] = 4        # 9 - 4 = 5 >= review_threshold 4
        self.assertIn("AUTHOR_REVIEW_NOT_ESCALATED", self.run_cats())
        block["status"], block["gap"]["author_review"] = "AUTHOR_REVIEW", "REQUIRED"
        self.assertEqual(validate(self.ledger, self.policy), [])

    def test_unknown_constraint_source_must_escalate(self):
        ev(self.ledger, "EV-V1")["representation"]["realized"]["constraint_source"] = "UNKNOWN"
        self.assertIn("AUTHOR_REVIEW_NOT_ESCALATED", self.run_cats())

    def test_always_review_family_must_escalate_when_limited(self):
        block = ev(self.ledger, "EV-S1")["representation"]           # SELF_HARM está em always_review
        block["realized"]["intensity"] = 1                          # 3 - 1 = 2 >= gap_threshold
        block["status"], block["gap"] = "CONSTRAINED", copy.deepcopy(GAP)
        self.assertIn("AUTHOR_REVIEW_NOT_ESCALATED", self.run_cats())

    def test_block_policy_turns_any_reduction_into_a_capability_blocker(self):
        """Narciso (OQ-RI-02): a política BLOCK preserva o comportamento
        atual — recusa/redução bloqueia; o cânone não é alterado."""
        self.policy["on_constrained_representation"] = "BLOCK"
        found = self.run_cats()
        self.assertIn("CAPABILITY_BLOCKER", found)
        self.assertNotIn("AUTHORIAL_GAP_MISSING", found)

    def test_property_consistent_gaps_never_produce_findings(self):
        """Toda combinação intended/realized cujo status e gap seguem a regra
        (calculada independentemente aqui) passa limpa."""
        rng = random.Random(7)
        rank = {"NORMAL": 3, "SENSITIVE": 3, "FADE_TO_BLACK": 2, "REFERENCE_ONLY": 1}
        for _ in range(300):
            ledger = copy.deepcopy(self.ledger)
            block = ev(ledger, "EV-V1")["representation"]
            i_exec = rng.choice(sorted(rank)); i_int = rng.randint(0, 10); i_gr = rng.random() < .5
            r_exec = rng.choice(sorted(rank)); r_int = rng.randint(0, 10); r_gr = rng.random() < .5
            block["intended"] = {"execution": i_exec, "intensity": i_int, "graphic": i_gr}
            block["realized"] = {**block["realized"], "execution": r_exec, "intensity": r_int,
                                 "graphic": r_gr, "constraint_source": "PROVIDER_LIMIT"}
            diff = i_int - r_int
            reduced = diff >= 2 or rank[i_exec] > rank[r_exec] or (i_gr and not r_gr)
            block.pop("gap", None)
            if reduced:
                escalate = diff >= 4
                block["status"] = "AUTHOR_REVIEW" if escalate else "CONSTRAINED"
                block["gap"] = {**GAP, "author_review": "REQUIRED" if escalate else "RECOMMENDED"}
            else:
                block["status"] = "FULLY_REPRESENTED"
            self.assertEqual(validate(ledger, self.policy), [], (i_exec, i_int, i_gr, r_exec, r_int, r_gr))


# ---------------------------------------------------------------------------
# Classificação do resultado e projeções
# ---------------------------------------------------------------------------

class TestClassification(Base):
    def test_pass_with_authorial_gaps(self):
        self.assertEqual(cr.classify(validate(self.ledger, self.policy), self.ledger), "PASS_WITH_AUTHORIAL_GAPS")

    def test_pass_without_gaps(self):
        block = ev(self.ledger, "EV-V1")["representation"]
        block["realized"] = {**block["realized"], "execution": "SENSITIVE", "intensity": 9, "graphic": True,
                             "constraint_source": "NONE"}
        block["status"] = "FULLY_REPRESENTED"
        del block["gap"]
        self.assertEqual(cr.classify(validate(self.ledger, self.policy), self.ledger), "PASS")

    def test_fail_contract(self):
        ev(self.ledger, "EV-V1")["representation"]["intended"]["intensity"] = 99
        self.assertEqual(cr.classify(validate(self.ledger, self.policy), self.ledger), "FAIL_CONTRACT")

    def test_gap_names_are_projected_never_stored(self):
        block = ev(self.ledger, "EV-V1")["representation"]
        self.assertNotIn("gap_names", block)
        self.assertNotIn("name", block["gap"])
        self.assertEqual(cr.gap_names({"content_classes": ["SELF_HARM", "TABOO"],
                                        "gap": {"dimensions": ["ON_PAGE_PRESENCE"]}}),
                         ["SELF_HARM_ON_PAGE_PRESENCE_GAP", "TABOO_ON_PAGE_PRESENCE_GAP"])

    def test_event_projection_never_exposes_generated_content(self):
        idx, _ = cl.build_indices(self.ledger)
        report = cr.event_report(self.ledger, idx, "EV-V1")
        self.assertEqual(report["age_verification"], "N/A")
        self.assertEqual(report["gap_names"], ["VIOLENCE_GRAPHIC_DETAIL_GAP"])
        self.assertIn("error", cr.event_report(self.ledger, idx, "EV-XX"))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

class TestCli(Base):
    def run_cli(self, *args: str):
        env = {"PYTHONIOENCODING": "utf-8", **__import__("os").environ}
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
                              encoding="utf-8", env=env)

    def test_clean_fixture_exits_zero(self):
        r = self.run_cli("--ledger", str(FIXTURE), "--policy", str(POLICY))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PASS_WITH_AUTHORIAL_GAPS", r.stderr)

    def test_json_output_carries_result(self):
        r = self.run_cli("--ledger", str(FIXTURE), "--policy", str(POLICY), "--json")
        data = json.loads(r.stdout)
        self.assertEqual(data["result"], "PASS_WITH_AUTHORIAL_GAPS")
        self.assertEqual(data["findings"], [])

    def test_blocking_finding_exits_one(self):
        char(self.ledger, "CHR-A")["age"] = 17
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.yaml"
            path.write_text(yaml.safe_dump(self.ledger, allow_unicode=True), encoding="utf-8")
            r = self.run_cli("--ledger", str(path), "--policy", str(POLICY))
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL_HARD_BOUNDARY", r.stderr)

    def test_missing_ledger_exits_two(self):
        self.assertEqual(self.run_cli("--ledger", "nao_existe.yaml").returncode, 2)
        self.assertEqual(self.run_cli().returncode, 2)

    def test_event_query(self):
        r = self.run_cli("--ledger", str(FIXTURE), "--event", "EV-05")
        self.assertEqual(json.loads(r.stdout)["age_verification"], "PASS")


if __name__ == "__main__":
    unittest.main()
