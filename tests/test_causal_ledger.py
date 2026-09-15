"""Testes do validador `check_causal_ledger.py` — Slice 1 da capability
`DARK_ROMANCE_CANON_ARCHITECT` (ver docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md).

100% offline, sem dependência de rede nem de credencial: só PyYAML.

Rodar:
    .venv/Scripts/python.exe -m unittest tests.test_causal_ledger -v
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import check_causal_ledger as cl  # noqa: E402

FIXTURE_PATH = REPO / "tests" / "fixtures" / "causal_ledger" / "mvp_ledger.yaml"
TEMPLATE_PATH = REPO / "engine" / "templates" / "CAUSAL_LEDGER_TEMPLATE.yaml"
SNAPSHOT_PATH = REPO / "tests" / "fixtures" / "causal_ledger" / "snapshot_wave_01.yaml"
CHAPTER_ARCHITECTURE_PATH = REPO / "tests" / "fixtures" / "causal_ledger" / "chapter_architecture.yaml"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def categories(findings: list[dict]) -> set[str]:
    return {f["category"] for f in findings}


def hard(findings: list[dict]) -> list[dict]:
    return [f for f in findings if f["severity"] in ("HIGH", "BLOCKER")]


class TestFixtureAndTemplateAreValid(unittest.TestCase):
    """SDD Slice 1: 'fixture válida -> exit 0, zero achados HIGH/BLOCKER' e
    'template válido -> exit 0'."""

    def test_fixture_has_no_hard_findings(self):
        ledger = load(FIXTURE_PATH)
        findings = cl.validate(ledger)
        self.assertEqual(hard(findings), [],
                          f"fixture não deveria ter achados HIGH/BLOCKER: {hard(findings)}")

    def test_template_has_no_hard_findings(self):
        ledger = load(TEMPLATE_PATH)
        findings = cl.validate(ledger)
        self.assertEqual(hard(findings), [],
                          f"template não deveria ter achados HIGH/BLOCKER: {hard(findings)}")

    def test_template_has_no_findings_at_all(self):
        # O template foi desenhado para citar toda GT declarada e alimentar
        # todo loop com o mínimo exigido — deve ficar limpo mesmo em soft.
        ledger = load(TEMPLATE_PATH)
        findings = cl.validate(ledger)
        self.assertEqual(findings, [])


class TestMutationsProduceExactCategory(unittest.TestCase):
    """Cada mutação isolada precisa produzir a categoria de achado exata
    descrita no SDD (seção L, Slice 1)."""

    def setUp(self):
        self.ledger = load(FIXTURE_PATH)

    def test_genre_label_causality(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["events"][0]["caused_by"] = ["TROPE:alpha"]
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "GENRE_LABEL_CAUSALITY"]
        self.assertTrue(matches, "trope como causa deveria reprovar LAW 01")
        self.assertEqual(matches[0]["severity"], "HIGH")
        self.assertEqual(matches[0]["chapter"], 1)

    def test_attraction_as_attribute(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["characters"][0]["charm"] = 95
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "ATTRACTION_AS_ATTRIBUTE"]
        self.assertTrue(matches, "atributo numérico de charme deveria reprovar INV-02")
        self.assertEqual(matches[0]["severity"], "HIGH")
        self.assertIn("charm", matches[0]["evidence"])

    def test_relationship_amnesia(self):
        ledger = copy.deepcopy(self.ledger)
        # EV-01 também estabelece RB-01 (beliefs.establishes); por INV-15 isso
        # sozinho já conta como mutação de estado, então isolar esta falha
        # exige remover TODOS os sinais de mutação, não só o delta relacional.
        ledger["events"][0]["relationship_delta"] = []
        ledger["events"][0].pop("beliefs", None)
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "RELATIONSHIP_AMNESIA"]
        self.assertTrue(matches, "evento estrutural sem nenhuma mutação deveria reprovar LAW 02")
        self.assertEqual(matches[0]["chapter"], 1)

    def test_state_reset(self):
        ledger = copy.deepcopy(self.ledger)
        # EV-03 declara from=WARY (o estado projetado correto após EV-01);
        # corromper para NONE simula reset de estado por troca de câmera/wave.
        ledger["events"][2]["relationship_delta"][0]["from"] = "NONE"
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "STATE_RESET"]
        self.assertTrue(matches, "`from` divergente do estado projetado deveria reprovar INV-04")
        self.assertEqual(matches[0]["chapter"], 3)

    def test_heat_without_history(self):
        ledger = copy.deepcopy(self.ledger)
        # Remove a contribuição de EV-03 como alimentador de LP-01, deixando
        # só EV-04: um único capítulo alimentador é insuficiente (min=2).
        del ledger["events"][2]["loops"]
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "HEAT_WITHOUT_HISTORY"]
        self.assertTrue(matches, "payoff com um único alimentador deveria reprovar LAW 03")

    def test_post_payoff_amnesia(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["events"][4]["relationship_delta"] = []
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "POST_PAYOFF_AMNESIA"]
        self.assertTrue(matches, "payoff sem aftermath deveria reprovar LAW 03")
        self.assertEqual(matches[0]["chapter"], 5)

    def test_adult_seduction_fail_unknown_age(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["characters"][1]["age"] = None  # CHR-B, participante de EV-05 (INTIMACY)
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "ADULT_SEDUCTION_FAIL"]
        self.assertTrue(matches, "idade desconhecida em evento de intimidade deveria reprovar o gate adulto")
        self.assertTrue(all(f["severity"] == "BLOCKER" for f in matches))

    def test_adult_seduction_fail_minor_age(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["characters"][1]["age"] = 17
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "ADULT_SEDUCTION_FAIL"]
        self.assertTrue(matches, "participante menor de idade em evento de intimidade deveria reprovar")
        self.assertTrue(all(f["severity"] == "BLOCKER" for f in matches))

    def test_adult_gate_is_blocker_regardless_of_other_findings(self):
        # O gate adulto nunca pode ser mascarado por outros achados: mesmo
        # com uma segunda mutação (causa inválida) presente, o BLOCKER segue
        # aparecendo e o exit code correspondente seria 1.
        ledger = copy.deepcopy(self.ledger)
        ledger["characters"][1]["age"] = 16
        ledger["events"][0]["caused_by"] = ["TROPE:alpha"]
        findings = cl.validate(ledger)
        self.assertIn("ADULT_SEDUCTION_FAIL", categories(findings))
        self.assertIn("GENRE_LABEL_CAUSALITY", categories(findings))
        self.assertTrue(any(f["severity"] == "BLOCKER" for f in findings))


class TestCoreThesisStructural(unittest.TestCase):
    """Provas estruturais da tese central (SDD, Apêndice 2), sobre a fixture
    intocada — cada teste nomeia a prova que demonstra."""

    def setUp(self):
        self.ledger = load(FIXTURE_PATH)
        self.idx, _ = cl.build_indices(self.ledger)

    def test_thesis_1_action_caused_by_differs_from_self_interpretation(self):
        """Um personagem age por uma causa que difere de sua própria
        interpretação: EV-01 é causado por GT-A-02, e a autoexplicação de A
        (SM-A-01) diverge exatamente dessa GT."""
        report = cl.why_report(self.ledger, self.idx, "EV-01")
        self.assertTrue(report["found"])
        self.assertTrue(report["diverges_from_cause"])
        ancestor_ids = {a["id"] for a in report["ancestors"] if a["type"] == "GT"}
        self.assertIn("GT-A-02", ancestor_ids)

    def test_thesis_2_structural_interaction_persistently_changes_relationship(self):
        """Uma interação estrutural altera persistentemente o relacionamento:
        o estado de confiança muda de NONE em t0 até BROKEN no capítulo 5, e
        nunca volta ao ponto de partida sem causa."""
        state = cl.relationship_state(self.ledger, "CHR-B", "CHR-A", at_chapter=5)
        self.assertEqual(state["trust"], "BROKEN")
        self.assertEqual(state["attraction"], "PROVOKED")
        self.assertEqual(state["vulnerability"], "OPEN")
        self.assertEqual(state["intimacy"], "ESTABLISHED")

    def test_thesis_4_reader_receives_true_facts_but_wrong_interpretation(self):
        """O leitor recebe fatos verdadeiros mas é conduzido a uma
        interpretação incompleta ou incorreta: RB-01 é FALSE, RB-02 é
        INCOMPLETE, e nenhuma delas se apoia em fato inventado — o leitor só
        aprende a GT que as corrige em EV-06 (cap. 6), nunca antes."""
        beliefs_by_id = {b["id"]: b for b in self.ledger["beliefs"]}
        self.assertEqual(beliefs_by_id["RB-01"]["truth"], "FALSE")
        self.assertEqual(beliefs_by_id["RB-02"]["truth"], "INCOMPLETE")
        # o leitor não sabia GT-A-02 antes da revelação...
        self.assertNotIn("GT-A-02", cl.knowledge_state(self.ledger, "READER", at_chapter=5))
        # ...mas a evidência que formou a crença errada é real, não inventada:
        # os `facts` de EV-01 e EV-03 (que fundamentam RB-01/RB-02) continuam
        # verdadeiros mesmo depois da revelação (checado contra o snapshot).
        _, tampered = cl.check_baseline_immutability(self.ledger, self.idx, load(SNAPSHOT_PATH))
        self.assertEqual(tampered, set())
        self.assertTrue(cl.why_report(self.ledger, self.idx, "EV-01")["facts"])

    def test_relationship_projection_partial_state(self):
        state = cl.relationship_state(self.ledger, "CHR-B", "CHR-A", at_chapter=2)
        self.assertEqual(state["trust"], "WARY")
        self.assertEqual(state["attraction"], "PROVOKED")
        # ainda não tocadas neste ponto da história:
        self.assertEqual(state["vulnerability"], "CLOSED")
        self.assertEqual(state["intimacy"], "NONE")

    def test_thesis_3_payoff_inherits_causal_ancestry(self):
        """Um payoff importante herda causalidade de acontecimentos
        anteriores: EV-05 resolve LP-01, aberto em EV-02 e alimentado em
        EV-03 e EV-04, ambos em capítulos anteriores distintos."""
        report = cl.payoff_report(self.ledger, self.idx, "EV-05")
        self.assertTrue(report["found"])
        resolve = report["resolves"][0]
        self.assertEqual(resolve["loop"], "LP-01")
        self.assertEqual({e["event"] for e in resolve["opened_by"]}, {"EV-02"})
        fed_chapters = {e["chapter"] for e in resolve["fed_by"]}
        self.assertEqual(fed_chapters, {3, 4})
        self.assertTrue(report["relationship_delta"], "payoff precisa de aftermath")

    def test_thesis_5_revelation_recontextualizes_without_retcon(self):
        """Informação posterior recontextualiza cenas anteriores sem retcon:
        EV-06 (leitor deste teste: EV-03, a mentira) permanece com os mesmos
        `facts` e a mesma ancestralidade GT-A-02 antes e depois da leitura —
        o validador não acusa retcon nesta fixture intocada."""
        findings = cl.validate(self.ledger)
        self.assertEqual(hard(findings), [])
        report = cl.why_report(self.ledger, self.idx, "EV-03")
        ancestor_ids = {a["id"] for a in report["ancestors"] if a["type"] == "GT"}
        self.assertIn("GT-A-02", ancestor_ids)

    def test_thesis_7_final_state_preserves_memory_for_continuation(self):
        """O estado final preserva memória suficiente para continuação: o
        loop sucessor LP-03 (nascido do payoff) segue aberto, e o
        relacionamento final diverge do baseline."""
        loop_ids = {lp["id"] for lp in self.ledger["loops"]}
        resolved_ids = set()
        for ev in self.ledger["events"]:
            for r in (ev.get("loops") or {}).get("resolves") or []:
                resolved_ids.add(r["loop"])
        open_loops = loop_ids - resolved_ids
        self.assertIn("LP-03", open_loops)
        self.assertIn("LP-02", open_loops)
        final_state = cl.relationship_state(self.ledger, "CHR-B", "CHR-A")
        baseline = next(
            r["baseline"] for r in self.ledger["relationships"] if r["pair"] == "CHR-B->CHR-A"
        )
        self.assertNotEqual(final_state, baseline)

    def test_knowledge_state_gates_the_secret_to_its_revelation_chapter(self):
        self.assertEqual(cl.knowledge_state(self.ledger, "READER", at_chapter=5), [])
        self.assertIn("GT-A-02", cl.knowledge_state(self.ledger, "READER", at_chapter=6))

    def test_beliefs_state_hides_truth_unless_engine_view(self):
        before = cl.beliefs_state(self.ledger, at_chapter=5)
        rb01_before = next(b for b in before if b["id"] == "RB-01")
        self.assertNotIn("truth", rb01_before)
        self.assertTrue(rb01_before["active"])

        after = cl.beliefs_state(self.ledger, at_chapter=6)
        rb01_after = next(b for b in after if b["id"] == "RB-01")
        self.assertFalse(rb01_after["active"])
        self.assertEqual(rb01_after["revised_chapter"], 6)

        engine = cl.beliefs_state(self.ledger, at_chapter=6, engine_view=True)
        rb01_engine = next(b for b in engine if b["id"] == "RB-01")
        self.assertEqual(rb01_engine["truth"], "FALSE")

    def test_recontextualized_report_marks_facts_unchanged(self):
        baseline = load(SNAPSHOT_PATH)
        _, tampered = cl.check_baseline_immutability(self.ledger, self.idx, baseline)
        report = cl.recontextualized_report(self.ledger, self.idx, tampered_event_ids=tampered)
        seen = {(r["event"], r["facts_unchanged"]) for r in report}
        self.assertIn(("EV-01", "sim"), seen)
        self.assertIn(("EV-03", "sim"), seen)
        classifications = {r["event"]: r["classification"] for r in report}
        self.assertEqual(classifications["EV-01"], "STRONG")
        self.assertEqual(classifications["EV-03"], "STRONG")


class TestSlice2ReaderBeliefAndConsent(unittest.TestCase):
    """Mutações do SDD, Slice 2: crença do leitor, imutabilidade contra
    snapshot e consentimento canônico."""

    def setUp(self):
        self.ledger = load(FIXTURE_PATH)
        self.baseline = load(SNAPSHOT_PATH)

    def test_retcon_on_tampered_facts(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["events"][0]["facts"] = ["Uma versão diferente do que aconteceu."]
        findings = cl.validate(ledger, mode="realized", baseline=self.baseline)
        matches = [f for f in findings if f["category"] == "RETCON"]
        self.assertTrue(matches, "facts divergentes do snapshot deveriam reprovar INV-10")

        idx, _ = cl.build_indices(ledger)
        _, tampered = cl.check_baseline_immutability(ledger, idx, self.baseline)
        self.assertIn("EV-01", tampered)
        classifications = cl.second_read_classifications(ledger, idx, tampered_event_ids=tampered)
        self.assertEqual(classifications["RB-01"]["classification"], "WEAK")

    def test_retcon_disguised_as_twist_when_gt_removed_from_ancestry(self):
        ledger = copy.deepcopy(self.ledger)
        # Remove GT-A-02 da ancestralidade tanto de EV-01 quanto de EV-03 —
        # a revelação em EV-06 passa a "explicar" cenas que nunca a causaram.
        ledger["events"][0]["caused_by"] = ["GT-B-01"]
        ledger["events"][2]["caused_by"] = ["EV-01"]
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "RETCON_DISGUISED_AS_TWIST"]
        self.assertTrue(matches, "revelação sem ancoragem causal prévia deveria reprovar INV-11")
        self.assertTrue(all(f["chapter"] == 6 for f in matches))
        rb_ids_flagged = {f["evidence"].split(" revises ")[1] for f in matches}
        self.assertEqual(rb_ids_flagged, {"RB-01", "RB-02"})

    def test_reader_omniscience_leak_when_secret_learned_too_early(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["events"][2].setdefault("knowledge_delta", []).append(
            {"knower": "READER", "learns": ["GT-A-02"]}
        )
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "READER_OMNISCIENCE_LEAK"]
        self.assertTrue(matches, "leitor aprendendo o segredo antes do capítulo 6 deveria vazar LAW 04")
        self.assertEqual(matches[0]["chapter"], 3)

    def test_information_leak_when_actor_acts_on_unlearned_knowledge(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["events"][1]["acts_on_knowledge"] = ["GT-A-02"]  # EV-02, ator CHR-B
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "INFORMATION_LEAK"]
        self.assertTrue(matches, "personagem agindo sobre o que não aprendeu deveria reprovar INV-13")
        self.assertEqual(matches[0]["chapter"], 2)

    def test_consent_drift_when_canonical_changes_after_baseline(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["events"][4]["consent"]["canonical"] = "DUBIOUS"
        findings = cl.validate(ledger, mode="realized", baseline=self.baseline)
        matches = [f for f in findings if f["category"] == "CONSENT_DRIFT"]
        self.assertTrue(matches, "consentimento reescrito depois da wave aprovada deveria reprovar INV-08")
        self.assertEqual(matches[0]["chapter"], 5)

    def test_consent_layer_collapse_when_perceived_carries_canonical(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["events"][4]["consent"]["perceived"]["canonical"] = "CONSENSUAL"
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "CONSENT_LAYER_COLLAPSE"]
        self.assertTrue(matches, "percepção carregando `canonical` deveria colapsar as camadas de consentimento")

    def test_coercion_as_payoff_when_consent_is_coercive(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["events"][4]["consent"]["canonical"] = "COERCIVE"
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "COERCION_AS_PAYOFF"]
        self.assertTrue(matches, "payoff coercivo de loop de intimidade deveria reprovar INV-09")
        self.assertEqual(matches[0]["chapter"], 5)

    def test_consent_missing_on_intimacy_event(self):
        ledger = copy.deepcopy(self.ledger)
        del ledger["events"][4]["consent"]
        findings = cl.validate(ledger)
        matches = [f for f in findings if f["category"] == "CONSENT_MISSING"]
        self.assertTrue(matches, "evento de intimidade sem bloco consent deveria reprovar INV-07")
        self.assertEqual(matches[0]["chapter"], 5)

    def test_clean_fixture_has_no_hard_findings_against_baseline(self):
        # Nenhuma das checagens novas do Slice 2 deveria acusar nada na
        # fixture intocada, mesmo comparada contra o snapshot aprovado.
        findings = cl.validate(copy.deepcopy(self.ledger), mode="realized", baseline=self.baseline)
        self.assertEqual(hard(findings), [])


class TestSlice3EmotionalAmplitudeAndEndState(unittest.TestCase):
    """Mutações do SDD, Slice 3: L6 (amplitude emocional por contraste) e L9
    (memória de continuação)."""

    def setUp(self):
        self.ledger = load(FIXTURE_PATH)
        self.idx, _ = cl.build_indices(self.ledger)
        self.chapters = load(CHAPTER_ARCHITECTURE_PATH)["chapters"]

    def test_clean_chapter_architecture_has_no_l6_findings(self):
        findings = cl.check_emotional_amplitude(self.chapters)
        self.assertEqual(findings, [])

    def test_validate_accepts_chapter_architecture_and_stays_clean(self):
        findings = cl.validate(self.ledger, chapter_architecture=self.chapters)
        self.assertEqual(hard(findings), [])
        self.assertNotIn("CONTINUOUS_ESCALATION", categories(findings))
        self.assertNotIn("PEAK_WITHOUT_CONTRAST", categories(findings))

    def test_continuous_escalation_on_five_chapter_non_decreasing_run(self):
        chapters = copy.deepcopy(self.chapters)
        # SDD: intensidades MEDIUM,HIGH,HIGH,PEAK,PEAK (caps. 2-6) — só os
        # capítulos 4 e 6 realmente mudam; o resultado cobre a obra inteira
        # (caps. 1-6) numa única corrida não decrescente.
        by_number = {c["number"]: c for c in chapters}
        by_number[4]["emotional_movement"]["intensity"] = "HIGH"
        by_number[6]["emotional_movement"]["intensity"] = "PEAK"
        findings = cl.check_emotional_amplitude(chapters)
        matches = [f for f in findings if f["category"] == "CONTINUOUS_ESCALATION"]
        self.assertTrue(matches, "6 capítulos não decrescentes deveriam reprovar LAW 05 (SOFT-01)")
        self.assertTrue(all(f["severity"] == "MEDIUM" for f in matches))

    def test_peak_without_contrast_when_valley_is_removed(self):
        chapters = copy.deepcopy(self.chapters)
        by_number = {c["number"]: c for c in chapters}
        by_number[4]["emotional_movement"]["intensity"] = "HIGH"  # remove o vale antes do PEAK (cap. 5)
        findings = cl.check_emotional_amplitude(chapters)
        matches = [f for f in findings if f["category"] == "PEAK_WITHOUT_CONTRAST"]
        self.assertTrue(matches, "PEAK sem vale nos 2 capítulos anteriores deveria reprovar LAW 05 (SOFT-02)")
        self.assertEqual(matches[0]["chapter"], 5)

    def test_end_state_reports_open_loop_closed_beliefs_and_changed_relationship(self):
        state = cl.end_state(self.ledger, self.idx)
        open_loop_ids = {lp["id"] for lp in state["open_loops"]}
        self.assertIn("LP-03", open_loop_ids)
        self.assertNotIn("LP-01", open_loop_ids)  # resolvido (TRANSFORMED) em EV-05
        # ambas as crenças foram revisadas em EV-06 — nenhuma fica pendurada
        self.assertEqual(state["open_beliefs"], [])
        final = state["relationship_states"]["CHR-B->CHR-A"]
        baseline = next(r["baseline"] for r in self.ledger["relationships"] if r["pair"] == "CHR-B->CHR-A")
        self.assertNotEqual(final, baseline)
        undisclosed_ids = {gt["id"] for gt in state["undisclosed_ground_truth"]}
        self.assertIn("GT-A-01", undisclosed_ids)   # reader_access: NEVER
        self.assertNotIn("GT-A-02", undisclosed_ids)  # já divulgada em EV-06


class TestCoreThesis(unittest.TestCase):
    """SDD, Apêndice 2 — um teste por prova (1 a 7) da tese central, sobre a
    mesma fixture. Os sete verdes fecham
    `DARK_ROMANCE_CORE_THESIS_STRUCTURAL = PROVEN` (SDD, seção K)."""

    def setUp(self):
        self.ledger = load(FIXTURE_PATH)
        self.idx, _ = cl.build_indices(self.ledger)
        self.chapters = load(CHAPTER_ARCHITECTURE_PATH)["chapters"]
        self.baseline = load(SNAPSHOT_PATH)

    def test_proof_1_character_acts_by_a_cause_that_differs_from_self_interpretation(self):
        report = cl.why_report(self.ledger, self.idx, "EV-01")
        self.assertTrue(report["diverges_from_cause"])
        self.assertIn("GT-A-02", {a["id"] for a in report["ancestors"] if a["type"] == "GT"})

    def test_proof_2_structural_interaction_persistently_alters_relationship(self):
        final_state = cl.relationship_state(self.ledger, "CHR-B", "CHR-A", at_chapter=6)
        baseline = next(r["baseline"] for r in self.ledger["relationships"] if r["pair"] == "CHR-B->CHR-A")
        self.assertNotEqual(final_state, baseline)

    def test_proof_3_major_payoff_inherits_causal_ancestry(self):
        report = cl.payoff_report(self.ledger, self.idx, "EV-05")
        resolve = report["resolves"][0]
        self.assertGreaterEqual(len({e["chapter"] for e in resolve["fed_by"]}), 2)
        self.assertTrue(report["relationship_delta"])

    def test_proof_4_reader_receives_true_facts_but_an_incomplete_or_wrong_interpretation(self):
        beliefs = {b["id"]: b for b in self.ledger["beliefs"]}
        self.assertIn(beliefs["RB-01"]["truth"], ("FALSE", "INCOMPLETE"))
        self.assertEqual(cl.knowledge_state(self.ledger, "READER", at_chapter=5), [])

    def test_proof_5_later_information_recontextualizes_earlier_scenes_without_retcon(self):
        _, tampered = cl.check_baseline_immutability(self.ledger, self.idx, self.baseline)
        self.assertEqual(tampered, set())
        report = cl.recontextualized_report(self.ledger, self.idx, tampered_event_ids=tampered)
        self.assertTrue(report)
        self.assertTrue(all(r["facts_unchanged"] == "sim" for r in report))

    def test_proof_6_emotional_trajectory_uses_contrast_not_continuous_escalation(self):
        self.assertEqual(cl.check_emotional_amplitude(self.chapters), [])

    def test_proof_7_final_state_preserves_memory_for_continuation(self):
        state = cl.end_state(self.ledger, self.idx)
        self.assertEqual(state["open_beliefs"], [])
        self.assertIn("LP-03", {lp["id"] for lp in state["open_loops"]})


if __name__ == "__main__":
    unittest.main()
