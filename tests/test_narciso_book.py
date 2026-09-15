"""Testes offline da obra NARCISO — Slices 1 e 2.

Desenho: docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md (seções 30 e 35).

Slice 1: o pacote `books/narciso/` é válido para o motor e o validador da obra
reprova cada mutação do pacote com a categoria exata.

Slice 2: canon interpretativo, guardiões e modos plan/wave/final. O runtime de
teste é COMPOSTO a partir do pacote real num diretório temporário; ledger,
registry, relatório e manuscrito neutro são gerados a partir da própria
semente, sem prosa erótica e sem nenhum arquivo novo de fixture no repositório.

Execução (por módulo, sem rede):
    .venv/Scripts/python.exe -m unittest tests.test_narciso_book -v
"""
from __future__ import annotations

import copy
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
BOOK = REPO / "books" / "narciso"
LIVINGBOOK = REPO / "engine" / "scripts" / "livingbook.py"
VALIDATOR = BOOK / "validators" / "validate_narciso.py"

_spec = importlib.util.spec_from_file_location("validate_narciso", VALIDATOR)
vn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vn)

sys.path.insert(0, str(REPO / "engine" / "scripts"))
import livingbook as lb  # noqa: E402


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, encoding="utf-8")


def chapter(bundle: dict, number: int) -> dict:
    return next(c for c in bundle["architecture"]["chapters"] if c["number"] == number)


def dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


# --- fixture de runtime, derivada da semente --------------------------------

def build_fixture_ledger(seed: dict, roster: dict) -> dict:
    characters = [{"id": c["id"], "major": c["role"] in {"PROTAGONIST", "SUPPORTING"}, "age": c["age"],
                   "age_source": "/book/planning/CHARACTER_ROSTER.yaml"} for c in roster["characters"]]
    beliefs = [
        {"id": "RB-LOVE-A", "about": ["CHR-NARCISO"], "interpretation": "Narciso ama Eco.", "confidence": "MEDIUM",
         "truth": "INCOMPLETE", "left_open": True},
        {"id": "RB-LOVE-B", "about": ["CHR-NARCISO"], "interpretation": "Narciso só ama a própria imagem.",
         "confidence": "MEDIUM", "truth": "INCOMPLETE", "left_open": True},
        {"id": "RB-RFX-01", "about": ["EV-RFX-02"], "interpretation": "Algo olha de volta da água.",
         "confidence": "LOW", "truth": "INCOMPLETE", "left_open": True},
    ]
    events = []
    for row in seed["reflection_evidence"]:
        events.append({"id": row["event"], "status": row["status"], "chapter": row["chapter"], "structural": True,
                       "kind": ["REFLECTION_EVIDENCE"], "actor": "CHR-NARCISO", "participants": ["CHR-NARCISO"],
                       "facts": [row["perception"]],
                       "knowledge_delta": [{"knower": "READER", "learns": [row["event"]]}]})
    for row in seed["love_readings"]:
        events.append({"id": row["event"], "status": row["status"], "chapter": row["chapter"], "structural": True,
                       "kind": ["LOVE_EVIDENCE"], "actor": "CHR-NARCISO", "participants": ["CHR-NARCISO", "CHR-ECO"],
                       "facts": [row["gesture"]],
                       "relationship_delta": [{"pair": "CHR-ECO->CHR-NARCISO", "dimension": "trust",
                                               "from": "WARY", "to": "UNSETTLED"}],
                       "beliefs": {"establishes": list(row["beliefs"])}})
    for row in seed["desire_occurrences"]:
        model = row["consent_model"]
        events.append({"id": row["event"], "status": row["status"], "chapter": row["chapter"], "structural": True,
                       "kind": ["SEXUAL", "COMPULSION_OCCURRENCE"], "actor": "CHR-NARCISO",
                       "participants": ["CHR-NARCISO"], "facts": [row["consequence"]],
                       "consent": {"canonical": "CONSENSUAL", "manipulation_present": False,
                                   "power_imbalance_present": False, "ability_to_refuse": model["ability_to_refuse"],
                                   "boundary_state": model["boundary_state"], "perceived": {}},
                       "knowledge_delta": [{"knower": "READER", "learns": [row["event"]]}]})
    for row in seed["partnered_intimacy"]:
        model = row["consent_model"]
        events.append({"id": row["event"], "status": row["status"], "chapter": row["chapter"], "structural": True,
                       "kind": ["INTIMACY"], "actor": "CHR-ECO", "participants": ["CHR-NARCISO", "CHR-ECO"],
                       "facts": ["intimidade negociada com sinal de parada"],
                       "consent": {"canonical": model["canonical"], "manipulation_present": False,
                                   "power_imbalance_present": False, "ability_to_refuse": model["ability_to_refuse"],
                                   "boundary_state": model["boundary_state"], "perceived": {}},
                       "relationship_delta": [{"pair": "CHR-ECO->CHR-NARCISO", "dimension": "intimacy",
                                               "from": "NONE", "to": "ESTABLISHED"}]})
    for character in characters:
        if character["id"] == "CHR-NARCISO":
            character["ground_truth"] = [
                {"id": "GT-NAR-01", "type": "CONTRADICTION", "statement": "Nenhum gesto tem motivo único.",
                 "reader_access": "NEVER"},
                {"id": "GT-NAR-04", "type": "WOUND", "statement": "Culpa não admitida pelo desaparecimento de Amintas.",
                 "reader_access": {"from_event": "EV-REV-INSCRIPTION"}},
                {"id": "GT-NAR-05", "type": "SECRET", "statement": "Pagou anonimamente a internação da mãe de Eco.",
                 "reader_access": {"from_event": "EV-REV-DEBT"}},
            ]
    for row in seed.get("revelations") or []:
        beliefs.append({"id": row["revises"], "about": [f["event"] for f in row["formed_by"]],
                        "interpretation": row["first_read"], "confidence": "MEDIUM", "truth": "FALSE",
                        "disclosed_by_revision": list(row["discloses"])})
        for formed in row["formed_by"]:
            events.append({"id": formed["event"], "status": "PLANNED", "chapter": formed["chapter"], "structural": True,
                           "kind": ["DECISION"], "actor": "CHR-NARCISO", "participants": ["CHR-NARCISO"],
                           "facts": [row["first_read"]], "caused_by": list(row["discloses"]),
                           "beliefs": {"establishes": [row["revises"]]}})
        events.append({"id": row["event"], "status": row["status"], "chapter": row["chapter"], "structural": True,
                       "kind": ["REVELATION"], "actor": "CHR-ECO", "participants": ["CHR-ECO"],
                       "facts": [row["second_read"]], "beliefs": {"revises": [row["revises"]]},
                       "knowledge_delta": [{"knower": "READER", "learns": list(row["discloses"])}]})
    return {"apiVersion": "pedroarte.livingbooks/v1", "kind": "CausalLedger",
            "metadata": {"project_id": "narciso", "version": "0.1.0", "owner": "CANON_GUARDIAN"},
            "characters": characters, "relationships": [], "loops": [], "beliefs": beliefs, "events": events}


FIXTURE_REGISTRY = {
    "unknowns": [{"id": "UNK-NAR-001", "status": "MUST_REMAIN_UNKNOWN", "question": "O que olha de volta?"}],
    "prohibited_inferences": [{"id": f"PRO-NAR-{i:03d}", "statement": s} for i, s in enumerate([
        "É projeção.", "É sobrenatural.", "É o próprio Narciso.", "É outra pessoa.",
        "Nasceu da contemplação.", "Narciso tem duplo biológico."], start=1)],
}


def neutral_chapter(number: int, title: str) -> str:
    return (f"# {number}. {title}\n\n"
            "A água da cava continuava parada quando a luz mudou de lugar.\n\n"
            "— Fica mais um pouco — disse alguém, sem pressa.\n")


def compose_fixture_runtime(root: Path) -> Path:
    runtime = root / "narciso"
    compose = run(LIVINGBOOK, "compose", "--book", BOOK, "--runtime", runtime)
    if compose.returncode != 0:
        raise RuntimeError(compose.stdout + compose.stderr)
    seed = yaml.safe_load((runtime / "book/seeds/INTERPRETIVE_CANON.seed.yaml").read_text(encoding="utf-8"))
    roster = yaml.safe_load((runtime / "book/planning/CHARACTER_ROSTER.yaml").read_text(encoding="utf-8"))
    canon = copy.deepcopy(seed)
    canon["metadata"]["source"] = "T018N_INTERPRETIVE_CANON"
    dump(runtime / vn.CANON_FILE, canon)
    dump(runtime / vn.LEDGER_FILE, build_fixture_ledger(seed, roster))
    dump(runtime / vn.REGISTRY_FILE, FIXTURE_REGISTRY)
    visual = yaml.safe_load((runtime / "book/seeds/VISUAL_NARRATIVE_CANON.seed.yaml").read_text(encoding="utf-8"))
    dump(runtime / vn.VISUAL_CANON_FILE, visual)
    (runtime / vn.REVIEW_FILE).parent.mkdir(parents=True, exist_ok=True)
    (runtime / vn.REVIEW_FILE).write_text("# Revisão de ambiguidade\n\nSem achados bloqueantes.\n", encoding="utf-8")
    titles = yaml.safe_load((runtime / "book/BOOK_SPEC.yaml").read_text(encoding="utf-8"))["spec"]["chapter_titles"]
    raw = runtime / "manuscript/raw"
    raw.mkdir(parents=True, exist_ok=True)
    parts = []
    for number, title in sorted((int(k), v) for k, v in titles.items()):
        text = neutral_chapter(number, title)
        (raw / f"chapter_{number:02d}.md").write_text(text, encoding="utf-8")
        parts.append(text)
    final = runtime / vn.FINAL_MANUSCRIPT
    final.parent.mkdir(parents=True, exist_ok=True)
    final.write_text("\n---\n\n".join(parts), encoding="utf-8")
    snapshot = run(VALIDATOR, "--runtime", runtime, "--snapshot-as", "WAVE_00")
    if snapshot.returncode != 0:
        raise RuntimeError(snapshot.stdout + snapshot.stderr)
    return runtime


def freeze_fixture_runtime(runtime: Path) -> None:
    """Estado do GATE_FULL_MANUSCRIPT: canon e ledger realizados, pistas de texto
    com trecho literal no manuscrito congelado e snapshot WAVE_06."""
    canon_path, ledger_path = runtime / vn.CANON_FILE, runtime / vn.LEDGER_FILE
    canon = yaml.safe_load(canon_path.read_text(encoding="utf-8"))
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    for section in vn.SECTION_EVENT_KIND:
        for row in canon.get(section) or []:
            row["status"] = "REALIZED"
    for event in ledger["events"]:
        event["status"] = "REALIZED"
    bundle = vn.load_bundle(runtime / "book")
    extra: dict[int, list[str]] = {}
    for clue in canon["reread_clues"]:
        if clue["channel"] != vn.REREAD_TEXT_CHANNEL:
            continue
        for side in ("clue", "trigger"):
            planned = vn._planned_anchor_chapters(clue[side]["anchor"], bundle)
            if not planned:
                continue
            number = min(planned)
            literal = f"uma marca pequena na página {clue['id'].lower()} {side}"
            clue[side]["text_anchor"] = f'TEXT:{number}:"{literal}"'
            extra.setdefault(number, []).append(f"Havia {literal}.")
    dump(canon_path, canon)
    dump(ledger_path, ledger)
    titles = yaml.safe_load((runtime / "book/BOOK_SPEC.yaml").read_text(encoding="utf-8"))["spec"]["chapter_titles"]
    parts = []
    for number, title in sorted((int(k), v) for k, v in titles.items()):
        text = neutral_chapter(number, title) + "".join(f"\n{line}\n" for line in extra.get(number, []))
        (runtime / f"manuscript/raw/chapter_{number:02d}.md").write_text(text, encoding="utf-8")
        parts.append(text)
    (runtime / vn.FINAL_MANUSCRIPT).write_text("\n---\n\n".join(parts), encoding="utf-8")
    snapshot = run(VALIDATOR, "--runtime", runtime, "--snapshot-as", "WAVE_06")
    if snapshot.returncode != 0:
        raise RuntimeError(snapshot.stdout + snapshot.stderr)


# --- Slice 1 -------------------------------------------------------------------

class TestNarcisoPackageIsValid(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bundle = vn.load_bundle(BOOK)

    def test_package_has_no_findings(self):
        findings = vn.check_package(self.bundle)
        self.assertEqual(findings, [], "\n".join(f"{f['category']}: {f['evidence']}" for f in findings))

    def test_check_package_does_not_mutate_bundle(self):
        before = copy.deepcopy(self.bundle)
        vn.check_package(self.bundle)
        self.assertEqual(self.bundle, before)

    def test_cli_package_mode_passes(self):
        proc = run(VALIDATOR, "--mode", "package")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("NARCISO PACKAGE VALID", proc.stdout)

    def test_cli_rejects_modes_of_later_slices_and_missing_runtime(self):
        self.assertEqual(run(VALIDATOR, "--mode", "illustrations").returncode, 2)
        self.assertEqual(run(VALIDATOR, "--mode", "final").returncode, 2)

    def test_engine_validate_book(self):
        proc = run(LIVINGBOOK, "validate-book", "--book", BOOK)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("BOOK PACKAGE VALID", proc.stdout)
        self.assertIn("book agents: 2", proc.stdout)


class TestNarcisoPackageMutations(unittest.TestCase):
    """Cada mutação do pacote afirma a categoria exata do achado."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = vn.load_bundle(BOOK)

    def findings_after(self, mutate) -> list[dict]:
        bundle = copy.deepcopy(self.bundle)
        mutate(bundle)
        return vn.check_package(bundle)

    def assertCategory(self, mutate, category, severity=None):
        findings = self.findings_after(mutate)
        matching = [f for f in findings if f["category"] == category]
        self.assertTrue(matching, f"{category} não emitido; achados: {[f['category'] for f in findings]}")
        if severity:
            self.assertIn(severity, {f["severity"] for f in matching})

    def test_missing_myth_element(self):
        def mutate(b):
            b["myth"]["elements"] = [e for e in b["myth"]["elements"] if e["id"] != "MYTH-07"]
        self.assertCategory(mutate, "MYTH_DNA_LOST", "HIGH")

    def test_unresolved_myth_anchor(self):
        def mutate(b):
            b["myth"]["elements"][0]["anchors"] = ["SCENE:DOES_NOT_EXIST"]
        self.assertCategory(mutate, "MYTH_ANCHOR_UNRESOLVED", "HIGH")

    def test_broken_mirror_pair(self):
        self.assertCategory(lambda b: chapter(b, 6).update(mirror_of=27), "MIRROR_PAIR_BROKEN", "HIGH")

    def test_chorus_structure(self):
        self.assertCategory(lambda b: chapter(b, 11).update(pov="Narciso"), "CHORUS_STRUCTURE_BROKEN", "HIGH")

    def test_desire_stage_regression(self):
        self.assertCategory(lambda b: chapter(b, 20).update(desire_stage="RITUAL"),
                            "DESIRE_STAGE_REGRESSION", "HIGH")

    def test_minor_character(self):
        def mutate(b):
            next(c for c in b["roster"]["characters"] if c["id"] == "CHR-ECO")["age"] = 17
        self.assertCategory(mutate, "ADULT_AGE_FAIL", "BLOCKER")

    def test_unknown_age_is_not_adult(self):
        def mutate(b):
            next(c for c in b["roster"]["characters"] if c["id"] == "CHR-IRIS")["age"] = None
        self.assertCategory(mutate, "ADULT_AGE_FAIL", "BLOCKER")

    def test_reflection_as_character(self):
        def mutate(b):
            b["roster"]["characters"].append({"id": "CHR-REFLEXO", "name": "Reflexo", "age": 27, "role": "SUPPORTING"})
        self.assertCategory(mutate, "REFLECTION_AS_CHARACTER", "BLOCKER")

    def test_twin_hypothesis_in_plan(self):
        def mutate(b):
            c = chapter(b, 25)
            c["function"] = c["function"] + " Uma das versões fala de um irmão gêmeo."
        self.assertCategory(mutate, "TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER")

    def test_twin_hypothesis_in_world_seed(self):
        self.assertCategory(lambda b: b.update(world_seed=b["world_seed"] + "\nO natimorto da família."),
                            "TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER")

    def test_explicitness_escalation(self):
        self.assertCategory(lambda b: chapter(b, 27)["adult_content"].update(explicitness_ceiling="FRANK"),
                            "EXPLICITNESS_ESCALATION", "BLOCKER")

    def test_last_occurrence_must_be_suggested(self):
        self.assertCategory(lambda b: chapter(b, 31)["adult_content"].update(explicitness_ceiling="SENSUAL"),
                            "EXPLICITNESS_ESCALATION", "BLOCKER")

    def test_partnered_ceiling(self):
        self.assertCategory(lambda b: chapter(b, 18)["adult_content"].update(explicitness_ceiling="FRANK"),
                            "NIGHT_EXPLICITNESS_ABOVE_CEILING", "BLOCKER")

    def test_repetition_without_new_meaning(self):
        self.assertCategory(lambda b: chapter(b, 19)["adult_content"].update(function="PLEASURE"),
                            "REPETITION_WITHOUT_NEW_MEANING", "HIGH")

    def test_pleasure_curve(self):
        self.assertCategory(lambda b: chapter(b, 31)["adult_content"].update(pleasure="MEDIUM"),
                            "PLEASURE_CURVE_BROKEN", "HIGH")

    def test_childhood_proximity(self):
        self.assertCategory(lambda b: chapter(b, 12).update(childhood_material=True),
                            "CHILDHOOD_EROTIC_PROXIMITY", "BLOCKER")

    def test_youth_coding_in_adult_chapter(self):
        def mutate(b):
            c = chapter(b, 15)
            c["function"] = c["function"] + " Ele parece um garoto."
        self.assertCategory(mutate, "YOUTH_CODING_IN_ADULT_CONTEXT", "BLOCKER")

    def test_partnered_without_consent(self):
        self.assertCategory(lambda b: chapter(b, 18)["adult_content"].pop("consent"), "CONSENT_UNDECLARED", "HIGH")

    def test_missing_immutable_rule(self):
        def mutate(b):
            b["rules"]["rules"] = [r for r in b["rules"]["rules"] if r["id"] != "IR-N11"]
        self.assertCategory(mutate, "IMMUTABLE_RULE_MISSING", "HIGH")

    def test_missing_protected_scene(self):
        def mutate(b):
            b["scenes"]["scenes"] = [s for s in b["scenes"]["scenes"] if s["id"] != "THE_CENTER"]
        self.assertCategory(mutate, "PROTECTED_SCENE_MISSING", "HIGH")

    def test_ontology_confirmed_in_plan(self):
        def mutate(b):
            chapter(b, 6)["irreversible_turn"] = "Narciso entende que era uma alucinação."
        self.assertCategory(mutate, "ONTOLOGY_CONFIRMED_IN_PLAN", "HIGH")

    def test_love_motive_declared_in_plan(self):
        self.assertCategory(lambda b: chapter(b, 29).update(function="Ele recusa porque a amava."),
                            "LOVE_MOTIVE_DECLARED_IN_PLAN", "HIGH")

    def test_missing_lexicon(self):
        self.assertCategory(lambda b: b["lexicons"]["lexicons"].update(twin=[]), "LEXICON_MISSING", "HIGH")

    def test_duplicate_illustration_slot(self):
        self.assertCategory(lambda b: chapter(b, 9).update(illustration_slots=["IL-06", "IL-05"]),
                            "ILLUSTRATION_SLOT_DUPLICATE", "HIGH")

    def test_two_final_evidences(self):
        self.assertCategory(lambda b: chapter(b, 33).update(final_evidence=["RFX-15", "RFX-14"]),
                            "FINAL_EVIDENCE_COUNT", "BLOCKER")

    def test_final_evidence_outside_last_chapter(self):
        self.assertCategory(lambda b: chapter(b, 32).update(final_evidence=["RFX-14"]),
                            "FINAL_EVIDENCE_COUNT", "BLOCKER")

    def test_chapter_title_mismatch(self):
        self.assertCategory(lambda b: chapter(b, 17).update(title="Outro Centro"), "CHAPTER_TITLE_MISMATCH", "HIGH")

    def test_unresolved_placeholder(self):
        def mutate(b):
            b["texts"]["CREATIVE_BRIEF.md"] += "\n" + "TO_" + "DEFINE"
        self.assertCategory(mutate, "UNRESOLVED_TO_DEFINE", "HIGH")

    def test_imitation_reference(self):
        def mutate(b):
            b["texts"]["planning/VOICE_PROFILE.md"] += "\nEscrever no estilo de uma autora famosa."
        self.assertCategory(mutate, "IMITATION_REFERENCE", "HIGH")

    def test_base_cliches_dropped(self):
        def mutate(b):
            b["text_quality"]["spec"]["cliches"]["patterns"] = ["deus grego"]
        self.assertCategory(mutate, "BASE_CLICHES_DROPPED", "MEDIUM")

    # --- semente do canon interpretativo (Slice 2, também no modo package) ---

    def test_seed_missing(self):
        self.assertCategory(lambda b: b.update(interpretive_seed=None), "INTERPRETIVE_CANON_MISSING", "HIGH")

    def test_seed_single_hypothesis(self):
        def mutate(b):
            b["interpretive_seed"]["reflection_evidence"][1]["support"] = {
                "H-PROJ": "S", "H-SUPER": "-", "H-SELF": "-", "H-OTHER": "-", "H-GAZE": "-"}
        self.assertCategory(mutate, "SINGLE_HYPOTHESIS_EVIDENCE", "HIGH")

    def test_seed_twin_hypothesis(self):
        def mutate(b):
            b["interpretive_seed"]["reflection_hypotheses"].append({"id": "H-TWIN", "label": "duplo"})
        self.assertCategory(mutate, "TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER")

    def test_seed_hidden_answer(self):
        self.assertCategory(lambda b: b["interpretive_seed"].update(truth="H-SELF"), "HIDDEN_ANSWER_PRESENT", "BLOCKER")

    def test_seed_dsr_mismatch_with_architecture(self):
        def mutate(b):
            b["interpretive_seed"]["desire_occurrences"][1]["pleasure"] = "LOW"
        self.assertCategory(mutate, "DSR_PLAN_MISMATCH", "HIGH")


# --- Slice 2: grafo --------------------------------------------------------------

class TestNarcisoGraph(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.graph = lb.build_standard_graph(BOOK)
        cls.tasks = {t["id"]: t for t in cls.graph["spec"]["tasks"]}
        cls.gates = cls.graph["spec"]["gates"]

    def test_graph_validates_without_errors(self):
        self.assertEqual(lb.validate_graph(self.graph, REPO), [])

    def test_book_guardians_are_registered_agents(self):
        for name in ("NARCISSUS_AMBIGUITY_GUARDIAN", "DESIRE_DECAY_GUARDIAN"):
            self.assertIn(name, self.graph["spec"]["agents"])

    def test_validators_attached_to_existing_gates(self):
        expected = {"GATE_CANON": ["V_NARCISO_PACKAGE", "V_NARCISO_PLAN"], "GATE_LIVING_BOOK": ["V_NARCISO_VISUAL"],
                    "GATE_FULL_MANUSCRIPT": ["V_NARCISO_FINAL"]}
        expected.update({f"GATE_WAVE_{i}": [f"V_NARCISO_WAVE_{i}"] for i in range(1, 7)})
        for gate, validators in expected.items():
            for validator in validators:
                self.assertIn(validator, self.gates[gate].get("custom_validators", []), gate)

    def test_interpretive_tasks_and_dependencies(self):
        self.assertEqual(self.tasks["T018N_INTERPRETIVE_CANON"]["depends_on"], ["T018_CANON_REGISTRY"])
        self.assertEqual(self.tasks["T019N_AMBIGUITY_REVIEW"]["owner"], "NARCISSUS_AMBIGUITY_GUARDIAN")
        self.assertIn("tool", self.tasks["T021N_INTERPRETIVE_SNAPSHOT"])
        for wave in range(1, 7):
            task = self.tasks[f"T20{wave}N_INTERPRETIVE_SNAPSHOT"]
            self.assertEqual(task["depends_on"], [f"T20{wave}_CANON_UPDATE"])
            self.assertIn(f"WAVE_{wave:02d}", task["tool"])

    def test_protected_scene_audits_use_book_guardians(self):
        owners = {t["parameters"]["scene_id"]: t["owner"] for t in self.graph["spec"]["tasks"]
                  if (t.get("parameters") or {}).get("scene_id")}
        self.assertEqual(owners["THE_CENTER"], "NARCISSUS_AMBIGUITY_GUARDIAN")
        self.assertEqual(owners["DSR_OCCURRENCES"], "DESIRE_DECAY_GUARDIAN")


# --- Slice 2: runtime ------------------------------------------------------------

class TestNarcisoRuntime(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.runtime = compose_fixture_runtime(Path(cls.tmp))
        cls.rt = vn.load_runtime(cls.runtime, "canon/snapshots/NARCISO_INTERPRETIVE_CANON.WAVE_00.yaml")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    # CLI de ponta a ponta

    def test_smoke_test(self):
        proc = run(LIVINGBOOK, "smoke-test", "--runtime", self.runtime)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_book_agents_copied_to_runtime(self):
        for name in ("narcissus_ambiguity_guardian.toml", "desire_decay_guardian.toml"):
            self.assertTrue((self.runtime / ".codex/agents" / name).is_file())

    def test_cli_plan_wave_final_pass(self):
        inner = self.runtime / "book/validators/validate_narciso.py"
        baseline = "canon/snapshots/NARCISO_INTERPRETIVE_CANON.WAVE_00.yaml"
        for args in (["--mode", "package"], ["--mode", "plan"], ["--mode", "visual"],
                     ["--mode", "wave", "--through-chapter", "6", "--baseline", baseline]):
            proc = run(inner, "--runtime", self.runtime, *args)
            self.assertEqual(proc.returncode, 0, f"{args}\n{proc.stdout}{proc.stderr}")

    def test_snapshot_written_by_cli(self):
        path = self.runtime / "canon/snapshots/NARCISO_INTERPRETIVE_CANON.WAVE_00.yaml"
        self.assertTrue(path.is_file())
        self.assertEqual(yaml.safe_load(path.read_text(encoding="utf-8")),
                         yaml.safe_load((self.runtime / vn.CANON_FILE).read_text(encoding="utf-8")))

    def test_wave_requires_through_chapter(self):
        self.assertEqual(run(VALIDATOR, "--runtime", self.runtime, "--mode", "wave").returncode, 2)

    # modos, em memória

    def test_all_modes_have_no_findings(self):
        # `final` exige canon realizado e âncoras de texto: coberto por TestNarcisoFrozenRuntime (Slice 6)
        for mode, through in (("plan", None), ("visual", None), ("wave", 33)):
            findings = vn.validate_runtime(self.rt, mode, through)
            self.assertEqual(findings, [], f"{mode}: " + "; ".join(f"{f['category']} {f['evidence']}" for f in findings))

    def findings_after(self, mutate, mode="final", through=None) -> list[dict]:
        rt = copy.deepcopy(self.rt)
        mutate(rt)
        return vn.validate_runtime(rt, mode, through)

    def assertCategory(self, mutate, category, severity=None, mode="final", through=None):
        findings = self.findings_after(mutate, mode, through)
        matching = [f for f in findings if f["category"] == category]
        self.assertTrue(matching, f"{category} não emitido; achados: {[f['category'] for f in findings]}")
        if severity:
            self.assertIn(severity, {f["severity"] for f in matching})
        return matching

    @staticmethod
    def event(rt, event_id):
        return next(e for e in rt["ledger"]["events"] if e["id"] == event_id)

    @staticmethod
    def row(rt, section, row_id):
        return next(r for r in rt["canon"][section] if r["id"] == row_id)

    # canon interpretativo

    def test_evidence_collapses_ontology(self):
        def mutate(rt):
            self.row(rt, "reflection_evidence", "RFX-02")["support"] = {
                "H-PROJ": "S", "H-SUPER": "X", "H-SELF": "X", "H-OTHER": "X", "H-GAZE": "X"}
        self.assertCategory(mutate, "EVIDENCE_COLLAPSES_ONTOLOGY", "BLOCKER")

    def test_ontology_converged(self):
        def mutate(rt):
            self.row(rt, "reflection_evidence", "RFX-02")["support"]["H-OTHER"] = "X"
            self.row(rt, "reflection_evidence", "RFX-03")["support"]["H-GAZE"] = "X"
            self.row(rt, "reflection_evidence", "RFX-04")["support"]["H-SELF"] = "X"
        self.assertCategory(mutate, "ONTOLOGY_CONVERGED", "BLOCKER")

    def test_final_evidence_narrow(self):
        def mutate(rt):
            self.row(rt, "reflection_evidence", "RFX-15")["support"] = {
                "H-PROJ": "S", "H-SUPER": "S", "H-SELF": "-", "H-OTHER": "-", "H-GAZE": "-"}
        self.assertCategory(mutate, "FINAL_EVIDENCE_NARROW", "HIGH")

    def test_love_reading_weak(self):
        self.assertCategory(lambda rt: self.row(rt, "love_readings", "LOVE-E3")["narcissism"].update(strength="WEAK"),
                            "LOVE_READING_WEAK", "HIGH")

    def test_love_final_resolved(self):
        self.assertCategory(lambda rt: self.row(rt, "love_readings", "LOVE-E8")["narcissism"].update(strength="MEDIUM"),
                            "LOVE_FINAL_RESOLVED", "HIGH")

    def test_love_balance_tilted(self):
        def mutate(rt):
            self.row(rt, "love_readings", "LOVE-E2")["narcissism"]["strength"] = "MEDIUM"
            self.row(rt, "love_readings", "LOVE-E3")["narcissism"]["strength"] = "MEDIUM"
        self.assertCategory(mutate, "LOVE_BALANCE_TILTED", "MEDIUM")

    def test_canon_consent_model_mismatch(self):
        self.assertCategory(lambda rt: self.row(rt, "desire_occurrences", "DSR-4")["consent_model"].update(
            ability_to_refuse="FULL"), "CONSENT_MODEL_MISMATCH", "HIGH")

    def test_reread_resolves_ambiguity(self):
        def mutate(rt):
            self.row(rt, "reread_clues", "RR-01")["second_read"] = "era o próprio Narciso desde o começo"
        self.assertCategory(mutate, "REREAD_RESOLVES_AMBIGUITY", "BLOCKER")

    def test_reread_trigger_before_clue(self):
        self.assertCategory(lambda rt: self.row(rt, "reread_clues", "RR-02")["trigger"].update(anchor="TURN:4"),
                            "REREAD_CLUE_WITHOUT_TRIGGER", "HIGH")

    def test_canon_hidden_answer(self):
        def mutate(rt):
            self.row(rt, "reflection_evidence", "RFX-07")["true_nature"] = "H-SUPER"
        self.assertCategory(mutate, "HIDDEN_ANSWER_PRESENT", "BLOCKER")

    # cruzamento com o ledger

    def test_event_missing(self):
        def mutate(rt):
            rt["ledger"]["events"] = [e for e in rt["ledger"]["events"] if e["id"] != "EV-RFX-07"]
        self.assertCategory(mutate, "EVENT_MISSING", "HIGH")

    def test_event_chapter_mismatch(self):
        self.assertCategory(lambda rt: self.event(rt, "EV-LOVE-E5").update(chapter=19), "EVENT_CHAPTER_MISMATCH", "HIGH")

    def test_event_kind_mismatch(self):
        self.assertCategory(lambda rt: self.event(rt, "EV-RFX-03").update(kind=["PACT"]), "EVENT_KIND_MISMATCH", "HIGH")

    def test_reflection_as_participant(self):
        self.assertCategory(lambda rt: self.event(rt, "EV-RFX-02")["participants"].append("CHR-REFLEXO"),
                            "REFLECTION_AS_PARTICIPANT", "BLOCKER")

    def test_rfx_fact_not_perception(self):
        self.assertCategory(lambda rt: self.event(rt, "EV-RFX-06").update(facts=["era um fantasma na margem"]),
                            "RFX_FACT_NOT_PERCEPTION", "HIGH")

    def test_love_event_without_mutation(self):
        self.assertCategory(lambda rt: self.event(rt, "EV-LOVE-E4").pop("relationship_delta"),
                            "LOVE_EVENT_WITHOUT_MUTATION", "HIGH")

    def test_ledger_consent_model_mismatch_for_compulsion(self):
        self.assertCategory(lambda rt: self.event(rt, "EV-DSR-5")["consent"].update(ability_to_refuse="FULL"),
                            "CONSENT_MODEL_MISMATCH", "HIGH")

    def test_ledger_partnered_consent(self):
        self.assertCategory(lambda rt: self.event(rt, "EV-NIGHT-18")["consent"].update(boundary_state="PUSHED"),
                            "CONSENT_MODEL_MISMATCH", "HIGH")

    def test_dsr_with_second_participant(self):
        self.assertCategory(lambda rt: self.event(rt, "EV-DSR-2")["participants"].append("CHR-ECO"),
                            "DSR_PARTICIPANTS_INVALID", "HIGH")

    def test_love_belief_with_truth(self):
        def mutate(rt):
            next(b for b in rt["ledger"]["beliefs"] if b["id"] == "RB-LOVE-A")["truth"] = "TRUE"
        self.assertCategory(mutate, "HIDDEN_ANSWER_PRESENT", "BLOCKER")

    def test_ambiguity_belief_revised(self):
        def mutate(rt):
            self.event(rt, "EV-RFX-15").setdefault("beliefs", {})["revises"] = ["RB-RFX-01"]
        self.assertCategory(mutate, "AMBIGUITY_BELIEF_REVISED", "BLOCKER")

    def test_age_drift_between_ledger_and_roster(self):
        def mutate(rt):
            next(c for c in rt["ledger"]["characters"] if c["id"] == "CHR-NARCISO")["age"] = 26
        self.assertCategory(mutate, "AGE_CANON_DRIFT", "HIGH")

    def test_registry_prohibited_inference_missing(self):
        def mutate(rt):
            rt["registry"]["prohibited_inferences"] = rt["registry"]["prohibited_inferences"][:-1]
        self.assertCategory(mutate, "UNKNOWNS_MISSING", "HIGH")

    def test_ledger_missing(self):
        self.assertCategory(lambda rt: rt.update(ledger=None), "LEDGER_MISSING", "HIGH", mode="plan")

    def test_plan_requires_review_and_snapshot(self):
        self.assertCategory(lambda rt: rt.update(has_review=False), "AMBIGUITY_REVIEW_MISSING", "HIGH", mode="plan")
        self.assertCategory(lambda rt: rt.update(has_wave00_snapshot=False), "INTERPRETIVE_SNAPSHOT_MISSING",
                            "HIGH", mode="plan")

    # imutabilidade

    def test_interpretive_retcon(self):
        def mutate(rt):
            rt["baseline"] = copy.deepcopy(rt["canon"])
            self.row({"canon": rt["baseline"]}, "reflection_evidence", "RFX-03")["status"] = "REALIZED"
            self.row(rt, "reflection_evidence", "RFX-03")["status"] = "REALIZED"
            self.event(rt, "EV-RFX-03")["status"] = "REALIZED"
            self.row(rt, "reflection_evidence", "RFX-03")["support"]["H-GAZE"] = "C"
        self.assertCategory(mutate, "INTERPRETIVE_RETCON", "BLOCKER", mode="wave", through=8)

    def test_baseline_missing(self):
        self.assertCategory(lambda rt: rt.update(baseline=None), "BASELINE_MISSING", "HIGH", mode="wave", through=6)

    # prosa

    def with_raw(self, number, extra):
        def mutate(rt):
            rt["raw_chapters"][number] = rt["raw_chapters"][number] + extra
        return mutate

    def test_prose_ontology_in_narration_blocks(self):
        matching = self.assertCategory(self.with_raw(6, "\nEra uma alucinação, e ele sabia.\n"),
                                       "ONTOLOGY_CONFIRMED_IN_PROSE", "BLOCKER", mode="wave", through=6)
        self.assertEqual({f["chapter"] for f in matching}, {6})

    def test_prose_ontology_in_dialogue_is_high_only(self):
        matching = self.assertCategory(self.with_raw(6, "\n— Era uma alucinação — disse Lia.\n"),
                                       "ONTOLOGY_CONFIRMED_IN_PROSE", "HIGH", mode="wave", through=6)
        self.assertNotIn("BLOCKER", {f["severity"] for f in matching})

    def test_prose_love_motive(self):
        self.assertCategory(self.with_raw(29, "\nEle ficou porque a amava.\n"),
                            "LOVE_MOTIVE_DECLARED", "BLOCKER", mode="wave", through=33)

    def test_prose_twin(self):
        self.assertCategory(self.with_raw(25, "\nLia falou do irmão gêmeo.\n"),
                            "TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER", mode="wave", through=28)

    def test_prose_reflection_named_is_case_sensitive(self):
        self.assertCategory(self.with_raw(8, "\nEle olhou o Reflexo.\n"), "REFLECTION_NAMED", "HIGH",
                            mode="wave", through=11)
        findings = self.findings_after(self.with_raw(8, "\nEle olhou o reflexo na janela.\n"), mode="wave", through=11)
        self.assertNotIn("REFLECTION_NAMED", {f["category"] for f in findings})

    def test_prose_youth_coding_only_in_adult_chapters(self):
        self.assertCategory(self.with_raw(15, "\nParecia um garoto.\n"),
                            "YOUTH_CODING_IN_ADULT_CONTEXT", "BLOCKER", mode="wave", through=17)
        findings = self.findings_after(self.with_raw(3, "\nA voz de menino na fita.\n"), mode="wave", through=6)
        self.assertNotIn("YOUTH_CODING_IN_ADULT_CONTEXT", {f["category"] for f in findings})

    def test_wave_raw_chapter_missing(self):
        self.assertCategory(lambda rt: rt["raw_chapters"].pop(5), "MANUSCRIPT_CHAPTER_MISSING", "HIGH",
                            mode="wave", through=6)

    def test_final_epilogue_heading(self):
        self.assertCategory(lambda rt: rt.update(final_manuscript=rt["final_manuscript"] + "\n# Epílogo\n\nDepois.\n"),
                            "EXPLANATORY_CLOSURE", "BLOCKER")

    def test_final_chapter_beyond_count(self):
        self.assertCategory(lambda rt: rt.update(final_manuscript=rt["final_manuscript"] + "\n# 34. Depois\n\nFim.\n"),
                            "EXPLANATORY_CLOSURE", "BLOCKER")

    def test_final_manuscript_prose_scanned(self):
        def mutate(rt):
            rt["final_manuscript"] = rt["final_manuscript"].replace(
                "# 31. Quase Nada\n", "# 31. Quase Nada\n\nEle nunca amou ninguém.\n")
        self.assertCategory(mutate, "LOVE_MOTIVE_DECLARED", "BLOCKER")


# --- Slice 6: final e releitura contra a prosa -------------------------------------

import re  # noqa: E402

WAVE_06 = "canon/snapshots/NARCISO_INTERPRETIVE_CANON.WAVE_06.yaml"


class TestNarcisoRevelationSeed(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bundle = vn.load_bundle(BOOK)

    def assertCategory(self, mutate, category, severity):
        bundle = copy.deepcopy(self.bundle)
        mutate(next(r for r in bundle["interpretive_seed"]["revelations"] if r["id"] == "REV-INSCRIPTION"))
        findings = vn.check_package(bundle)
        matching = [f for f in findings if f["category"] == category]
        self.assertTrue(matching, f"{category} não emitido; achados: {[f['category'] for f in findings]}")
        self.assertIn(severity, {f["severity"] for f in matching})

    def test_revision_of_ambiguity_belief(self):
        self.assertCategory(lambda r: r.update(revises="RB-LOVE-A"), "REVELATION_TOUCHES_AMBIGUITY", "BLOCKER")

    def test_second_read_confirms_ontology(self):
        self.assertCategory(lambda r: r.update(second_read="o que olhava de volta era Amintas"),
                            "REVELATION_TOUCHES_AMBIGUITY", "BLOCKER")

    def test_revelation_in_last_chapter(self):
        self.assertCategory(lambda r: r.update(chapter=33), "EXPLANATORY_CLOSURE", "BLOCKER")

    def test_belief_formed_after_revelation(self):
        self.assertCategory(lambda r: r["formed_by"][0].update(chapter=20), "RETCON_DISGUISED_AS_TWIST", "BLOCKER")

    def test_disclosed_truth_malformed(self):
        self.assertCategory(lambda r: r.update(discloses=["culpa"]), "REVELATION_INVALID", "HIGH")


class TestNarcisoFrozenRuntime(unittest.TestCase):
    """Aceite do Slice 6: fixture congelada passa; retcon interpretativo e
    epílogo reprovam."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.runtime = compose_fixture_runtime(Path(cls.tmp))
        freeze_fixture_runtime(cls.runtime)
        cls.rt = vn.load_runtime(cls.runtime, WAVE_06)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def findings_after(self, mutate) -> list[dict]:
        rt = copy.deepcopy(self.rt)
        mutate(rt)
        return vn.validate_runtime(rt, "final")

    def assertCategory(self, mutate, category, severity=None):
        findings = self.findings_after(mutate)
        matching = [f for f in findings if f["category"] == category]
        self.assertTrue(matching, f"{category} não emitido; achados: {[f['category'] for f in findings]}")
        if severity:
            self.assertIn(severity, {f["severity"] for f in matching})

    @staticmethod
    def row(rt, section, row_id):
        return next(r for r in rt["canon"][section] if r["id"] == row_id)

    @staticmethod
    def event(rt, event_id):
        return next(e for e in rt["ledger"]["events"] if e["id"] == event_id)

    @staticmethod
    def in_chapter(rt, number, line):
        rt["final_manuscript"] = re.sub(rf"(# {number}\. [^\n]+\n)", lambda m: m.group(1) + f"\n{line}\n",
                                        rt["final_manuscript"], count=1)

    def test_frozen_runtime_passes_final(self):
        findings = vn.validate_runtime(self.rt, "final")
        self.assertEqual(findings, [], "; ".join(f"{f['category']} {f['evidence']}" for f in findings))

    def test_cli_final_passes(self):
        proc = run(self.runtime / "book/validators/validate_narciso.py", "--runtime", self.runtime,
                   "--mode", "final", "--baseline", WAVE_06)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_seed_fixture_is_not_final(self):
        rt = vn.load_runtime(self.runtime, WAVE_06)
        rt["canon"] = yaml.safe_load((self.runtime / "book/seeds/INTERPRETIVE_CANON.seed.yaml").read_text(encoding="utf-8"))
        self.assertIn("FINAL_ROW_UNREALIZED", {f["category"] for f in vn.validate_runtime(rt, "final")})

    # epílogo e destino

    def test_epilogue_in_last_chapter(self):
        self.assertCategory(lambda rt: self.in_chapter(rt, 33, "Anos depois, a explicação chegou pelo correio."),
                            "EXPLANATORY_CLOSURE", "BLOCKER")

    def test_same_words_before_the_end_are_not_closure(self):
        findings = self.findings_after(lambda rt: self.in_chapter(rt, 20, "Anos depois, a explicação chegou pelo correio."))
        self.assertNotIn("EXPLANATORY_CLOSURE", {f["category"] for f in findings})

    def test_fate_confirmed(self):
        self.assertCategory(lambda rt: self.in_chapter(rt, 32, "Encontraram o corpo na margem."), "FATE_RESOLVED", "BLOCKER")

    def test_revision_in_last_chapter(self):
        self.assertCategory(lambda rt: self.event(rt, "EV-RFX-15").setdefault("beliefs", {}).update(revises=["RB-DEBT-01"]),
                            "EXPLANATORY_CLOSURE", "BLOCKER")

    def test_second_evidence_in_last_chapter(self):
        def mutate(rt):
            rt["ledger"]["events"].append({"id": "EV-RFX-99", "chapter": 33, "status": "REALIZED",
                                           "kind": ["REFLECTION_EVIDENCE"], "participants": ["CHR-NARCISO"]})
        self.assertCategory(mutate, "FINAL_EVIDENCE_COUNT", "BLOCKER")

    def test_love_reading_moved_to_last_chapter(self):
        self.assertCategory(lambda rt: self.row(rt, "love_readings", "LOVE-E8").update(chapter=33),
                            "FINAL_EVIDENCE_COUNT", "BLOCKER")

    def test_row_unrealized(self):
        def mutate(rt):
            self.row(rt, "reflection_evidence", "RFX-05")["status"] = "PLANNED"
            self.event(rt, "EV-RFX-05")["status"] = "PLANNED"
        self.assertCategory(mutate, "FINAL_ROW_UNREALIZED", "HIGH")

    # RRL-04

    def test_text_anchor_missing(self):
        self.assertCategory(lambda rt: self.row(rt, "reread_clues", "RR-02")["clue"].pop("text_anchor"),
                            "REREAD_ANCHOR_MISSING", "HIGH")

    def test_text_anchor_literal_rewritten_in_prose(self):
        def mutate(rt):
            rt["final_manuscript"] = rt["final_manuscript"].replace("página rr-03 clue", "página rr-03 pista")
        self.assertCategory(mutate, "REREAD_ANCHOR_MISSING", "HIGH")

    def test_text_anchor_in_wrong_chapter(self):
        self.assertCategory(lambda rt: self.row(rt, "reread_clues", "RR-03")["clue"].update(
            text_anchor='TEXT:6:"A água da cava continuava parada"'), "REREAD_ANCHOR_MISSING", "HIGH")

    # retcon interpretativo (ICN-IMM contra WAVE_06)

    def test_realized_support_retcon(self):
        self.assertCategory(lambda rt: self.row(rt, "reflection_evidence", "RFX-03")["support"].update({"H-GAZE": "C"}),
                            "INTERPRETIVE_RETCON", "BLOCKER")

    def test_reread_second_read_retcon(self):
        self.assertCategory(lambda rt: self.row(rt, "reread_clues", "RR-11").update(second_read="outra leitura"),
                            "INTERPRETIVE_RETCON", "BLOCKER")

    def test_revelation_retcon(self):
        self.assertCategory(lambda rt: self.row(rt, "revelations", "REV-DEBT").update(discloses=["GT-NAR-04"]),
                            "INTERPRETIVE_RETCON", "BLOCKER")

    def test_new_anchor_on_open_side_is_not_retcon(self):
        def mutate(rt):
            rt["baseline"] = copy.deepcopy(rt["canon"])
            self.row({"canon": rt["baseline"]}, "reread_clues", "RR-02")["trigger"].pop("text_anchor")
        findings = self.findings_after(mutate)
        self.assertNotIn("INTERPRETIVE_RETCON", {f["category"] for f in findings})

    # RRL-05

    def test_revelation_without_planted_cause(self):
        self.assertCategory(lambda rt: self.event(rt, "EV-NAR-01").pop("caused_by"), "RETCON_DISGUISED_AS_TWIST", "BLOCKER")

    def test_revelation_formed_after_reveal_in_ledger(self):
        self.assertCategory(lambda rt: self.event(rt, "EV-ECO-03").update(chapter=20), "RETCON_DISGUISED_AS_TWIST", "BLOCKER")

    def test_revelation_event_does_not_revise(self):
        self.assertCategory(lambda rt: self.event(rt, "EV-REV-DEBT").pop("beliefs"), "REVELATION_NOT_IN_LEDGER", "HIGH")

    def test_revelation_discloses_sealed_truth(self):
        def mutate(rt):
            self.row(rt, "revelations", "REV-DEBT")["discloses"] = ["GT-NAR-01"]
            next(b for b in rt["ledger"]["beliefs"] if b["id"] == "RB-DEBT-01")["disclosed_by_revision"] = ["GT-NAR-01"]
            self.event(rt, "EV-ECO-03")["caused_by"] = ["GT-NAR-01"]
        self.assertCategory(mutate, "REVELATION_TOUCHES_AMBIGUITY", "BLOCKER")


# --- Slice 7: posse e produção -----------------------------------------------------

class TestNarcisoProductionPackage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bundle = vn.load_bundle(BOOK)

    def assertCategory(self, mutate, category, severity):
        bundle = copy.deepcopy(self.bundle)
        mutate(bundle)
        findings = vn.check_package(bundle)
        matching = [f for f in findings if f["category"] == category]
        self.assertTrue(matching, f"{category} não emitido; achados: {[f['category'] for f in findings]}")
        self.assertIn(severity, {f["severity"] for f in matching})

    @staticmethod
    def mirror(bundle):
        return next(f for f in bundle["visual_seed"]["finish_intents"] if f["id"] == "FI-MIRROR-POOL")

    def test_mirror_area_too_large(self):
        self.assertCategory(lambda b: self.mirror(b)["ext"]["narciso"].update(area_ratio_max=0.2), "MIRROR_GIMMICK", "HIGH")

    def test_mirror_on_public_composition(self):
        self.assertCategory(lambda b: self.mirror(b)["target"].update(composition="COMP-FRONT"), "MIRROR_GIMMICK", "HIGH")

    def test_mirror_without_mirror_effect(self):
        self.assertCategory(lambda b: self.mirror(b).update(preferred_effect="METALLIC_FOIL"), "MIRROR_GIMMICK", "HIGH")

    def test_page_count_invented(self):
        self.assertCategory(lambda b: b["print_spec_seed"]["spec"]["kdp_paperback"].update(page_count=320),
                            "PAGE_COUNT_INVENTED", "HIGH")

    def test_print_spec_missing(self):
        self.assertCategory(lambda b: b.update(print_spec_seed=None), "PRINT_SPEC_SEED_MISSING", "HIGH")

    def test_template_confirms_effect(self):
        self.assertCategory(lambda b: b["printer_profile_template"].update(confirmed_effects=["MIRROR_BOARD"]),
                            "PRINTER_EFFECT_UNEVIDENCED", "HIGH")

    def test_research_incomplete(self):
        self.assertCategory(lambda b: b.update(printer_research="# Pesquisa\n"), "PRINTER_RESEARCH_MISSING", "MEDIUM")


class TestNarcisoEditionRuntime(unittest.TestCase):
    """Aceite do Slice 7: o resolver produz os 4 EDITION_PLAN sem prometer efeito
    não físico; HIDDEN_TRUTH_EXPOSED testado."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.runtime = compose_fixture_runtime(Path(cls.tmp))
        proc = run(REPO / "engine/scripts/check_visual_canon.py", "--runtime", cls.runtime, "--edition-plan-all")
        if proc.returncode != 0:
            raise RuntimeError(proc.stdout + proc.stderr)
        (cls.runtime / vn.KDP_REQUIREMENTS_FILE).write_text("# Requisitos KDP revalidados (fixture)\n", encoding="utf-8")
        cls.rt = vn.load_runtime(cls.runtime)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def findings_after(self, mutate) -> list[dict]:
        rt = copy.deepcopy(self.rt)
        mutate(rt)
        return vn.validate_runtime(rt, "edition")

    def assertCategory(self, mutate, category, severity):
        findings = self.findings_after(mutate)
        matching = [f for f in findings if f["category"] == category]
        self.assertTrue(matching, f"{category} não emitido; achados: {[f['category'] for f in findings]}")
        self.assertIn(severity, {f["severity"] for f in matching})

    def plan(self, rt, target):
        return rt["edition_plans"][target]

    @staticmethod
    def finish(plan, finish_id):
        return next(f for f in plan["finish_intents"] if f["finish_intent"] == finish_id)

    def test_four_plans_without_non_physical_promises(self):
        for target in ("kindle_ebook", "kdp_paperback", "kdp_hardcover", "collector"):
            plan = self.rt["edition_plans"][target]
            self.assertIsNotNone(plan, target)
            self.assertEqual([f["finish_intent"] for f in plan["finish_intents"] if f["level"] == "PHYSICAL"], [], target)
            status = {c["composition"]: c["status"] for c in plan["compositions"]}
            if target != "collector":
                for composition in ("COMP-CASE-HIDDEN", "COMP-ENDPAPER-BACK", "COMP-CASE-SPINE", "COMP-SLIPCASE"):
                    self.assertEqual(status[composition], "OMITTED", (target, composition))
        mirror = self.finish(self.rt["edition_plans"]["collector"], "FI-MIRROR-POOL")
        self.assertEqual((mirror["effect"], mirror["level"]), ("SIMULATED_METALLIC_PRINT", "SIMULATED"))
        omitted = {f["finish_intent"] for f in self.rt["edition_plans"]["collector"]["finish_intents"] if f["level"] == "OMIT"}
        self.assertTrue({"FI-FLOWER", "FI-EDGE", "FI-RIBBON", "FI-SLIPCASE"} <= omitted, omitted)

    def test_confirmed_printer_makes_mirror_physical_only_on_collector(self):
        canon = yaml.safe_load((self.runtime / vn.VISUAL_CANON_FILE).read_text(encoding="utf-8"))
        capabilities = self.rt["capabilities"]
        profile = {"metadata": {"id": "p"}, "confirmed_effects": ["MIRROR_BOARD"]}
        collector = cvc.resolve_edition_plan(canon, capabilities, "collector", profile)
        self.assertEqual(self.finish(collector, "FI-MIRROR-POOL")["effect"], "MIRROR_BOARD")
        manifest = cvc.build_production_manifest(canon, "collector", collector, profile)
        mask = next(a for a in manifest["assets"] if a["finish_intent"] == "FI-MIRROR-POOL")
        self.assertEqual((mask["kind"], mask["derived_from"]), ("MIRROR_MASK", {"layer": "L_MIRROR_POOL"}))
        hardcover = cvc.resolve_edition_plan(canon, capabilities, "kdp_hardcover", profile)
        self.assertEqual(self.finish(hardcover, "FI-MIRROR-POOL")["level"], "OMIT")

    def test_edition_mode_passes(self):
        findings = vn.validate_runtime(self.rt, "edition")
        self.assertEqual(findings, [], "; ".join(f"{f['category']} {f['evidence']}" for f in findings))

    def test_cli_edition_passes(self):
        proc = run(self.runtime / "book/validators/validate_narciso.py", "--runtime", self.runtime, "--mode", "edition")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_graph_attaches_edition_validator(self):
        gates = lb.build_standard_graph(BOOK)["spec"]["gates"]
        self.assertIn("V_NARCISO_EDITION", gates["GATE_KDP"]["custom_validators"])

    def test_hidden_truth_exposed(self):
        def mutate(rt):
            entry = next(c for c in self.plan(rt, "kdp_hardcover")["compositions"] if c["composition"] == "COMP-CASE-HIDDEN")
            entry.update(status="INCLUDED", mapped_surface="CASE_FRONT")
        self.assertCategory(mutate, "HIDDEN_TRUTH_EXPOSED", "BLOCKER")

    def test_mirror_physical_outside_collector(self):
        self.assertCategory(lambda rt: self.finish(self.plan(rt, "kdp_paperback"), "FI-MIRROR-POOL").update(
            effect="MIRROR_BOARD", level="PHYSICAL"), "MIRROR_OUTSIDE_COLLECTOR", "BLOCKER")

    def test_plan_claims_physical_effect_kdp_does_not_have(self):
        self.assertCategory(lambda rt: self.finish(self.plan(rt, "kdp_hardcover"), "FI-TITLE").update(
            effect="METALLIC_FOIL", level="PHYSICAL"), "FINISH_NOT_PHYSICAL", "BLOCKER")

    def test_vendor_effect_physical_without_printer(self):
        self.assertCategory(lambda rt: self.finish(self.plan(rt, "collector"), "FI-MIRROR-POOL").update(
            effect="MIRROR_BOARD", level="PHYSICAL"), "PRINTER_EFFECT_UNEVIDENCED", "HIGH")

    def test_printer_profile_without_evidence(self):
        self.assertCategory(lambda rt: rt.update(printer_profile={"confirmed_effects": ["MIRROR_BOARD"]}),
                            "PRINTER_EFFECT_UNEVIDENCED", "HIGH")

    def test_printer_profile_with_evidence_is_clean(self):
        profile = {"confirmed_effects": ["MIRROR_BOARD"], "evidence": {"MIRROR_BOARD": {
            "vendor": "gráfica", "quote_ref": "ORC-1", "date": "2026-10-01", "sample_approved": True}}}
        findings = self.findings_after(lambda rt: rt.update(printer_profile=profile))
        self.assertNotIn("PRINTER_EFFECT_UNEVIDENCED", {f["category"] for f in findings})

    def test_numbered_without_decision(self):
        self.assertCategory(lambda rt: rt.update(printer_profile={"production": {"numbered": True}}),
                            "PRINTER_EFFECT_UNEVIDENCED", "HIGH")

    def test_store_text_promises_mirror(self):
        self.assertCategory(lambda rt: rt["marketing"].update({"media/KDP_DESCRIPTION_4000.txt": "Uma capa espelhada."}),
                            "FINISH_PROMISE_MISMATCH", "HIGH")

    def test_store_text_promises_numbered_edition(self):
        self.assertCategory(lambda rt: rt["marketing"].update({"media/KDP_DESCRIPTION_SHORT.txt": "Edição numerada."}),
                            "FINISH_PROMISE_MISMATCH", "HIGH")

    def test_store_text_exposes_reread_clue(self):
        def mutate(rt):
            clue = next(c for c in rt["canon"]["reread_clues"] if c["id"] == "RR-02")
            rt["marketing"]["media/SHAREABLE_EXCERPTS.md"] = f"— {clue['second_read']}"
        self.assertCategory(mutate, "REREAD_CLUE_EXPOSED", "MEDIUM")

    def test_kdp_requirements_not_refreshed(self):
        self.assertCategory(lambda rt: rt.update(has_kdp_requirements=False), "KDP_REQUIREMENTS_UNVERIFIED", "HIGH")

    def test_edition_plan_missing(self):
        self.assertCategory(lambda rt: rt["edition_plans"].update(kdp_paperback=None), "EDITION_PLAN_MISSING", "HIGH")


# --- Slice 3: canon visual --------------------------------------------------------

import check_visual_canon as cvc  # noqa: E402


def element(canon: dict, element_id: str) -> dict:
    return next(e for e in canon["elements"] if e["id"] == element_id)


def composition(canon: dict, composition_id: str) -> dict:
    return next(c for c in canon["compositions"] if c["id"] == composition_id)


class TestNarcisoVisualSeedMutations(unittest.TestCase):
    """Regras visuais da obra sobre a semente, em memória."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = vn.load_bundle(BOOK)

    def assertCategory(self, mutate, category, severity=None):
        bundle = copy.deepcopy(self.bundle)
        mutate(bundle)
        findings = vn.check_package(bundle)
        matching = [f for f in findings if f["category"] == category]
        self.assertTrue(matching, f"{category} não emitido; achados: {[f['category'] for f in findings]}")
        if severity:
            self.assertIn(severity, {f["severity"] for f in matching})

    def test_visual_seed_missing(self):
        self.assertCategory(lambda b: b.update(visual_seed=None), "VISUAL_CANON_MISSING", "HIGH")

    def test_silver_as_palette_role(self):
        def mutate(b):
            b["visual_seed"]["book_dna"]["palette"]["METAL"] = {"material": "SILVER_MIRROR", "hex": "#8A6C3E"}
        self.assertCategory(mutate, "SILVER_AS_PALETTE_ROLE", "HIGH")

    def test_silver_finish_on_public_edition(self):
        def mutate(b):
            next(fi for fi in b["visual_seed"]["finish_intents"] if fi["id"] == "FI-MIRROR-POOL")["cost_class"] = "PREMIUM"
        self.assertCategory(mutate, "SILVER_FINISH_MISPLACED", "HIGH")

    def test_decay_trigger_mismatch(self):
        def mutate(b):
            element(b["visual_seed"], "FIG-NARCISO")["transitions"][2]["trigger"] = "TURN:20"
        self.assertCategory(mutate, "DECAY_TRIGGER_MISMATCH", "HIGH")

    def test_decay_timeline_invalid(self):
        def mutate(b):
            element(b["visual_seed"], "FIG-NARCISO")["states"].pop(3)
        self.assertCategory(mutate, "DECAY_TIMELINE_INVALID", "HIGH")

    def test_decay_glamorized(self):
        def mutate(b):
            element(b["visual_seed"], "FIG-NARCISO")["states"][4]["visual_description"] = "Magreza elegante e costelas à mostra."
        self.assertCategory(mutate, "DECAY_GLAMORIZED", "BLOCKER")

    def test_youth_coding_in_figure(self):
        def mutate(b):
            element(b["visual_seed"], "FIG-NARCISO")["states"][0]["visual_description"] = "Rosto de garoto."
        self.assertCategory(mutate, "YOUTH_CODING_IN_ADULT_CONTEXT", "BLOCKER")

    def test_state_without_new_meaning(self):
        def mutate(b):
            states = element(b["visual_seed"], "SYM-AGUA")["states"]
            states[2]["meaning"] = states[1]["meaning"]
        self.assertCategory(mutate, "SYMBOL_STATE_WITHOUT_NEW_MEANING", "MEDIUM")

    def test_bare_chapter_trigger(self):
        def mutate(b):
            element(b["visual_seed"], "SYM-OURO")["transitions"][0]["trigger"] = "15"
        self.assertCategory(mutate, "VISUAL_TRIGGER_UNRESOLVED", "HIGH")

    def test_flower_count_fixed(self):
        self.assertCategory(lambda b: element(b["visual_seed"], "SYM-NARCISO").update(count=3), "SYMBOL_COUNT_FIXED", "HIGH")

    def test_veto_missing(self):
        def mutate(b):
            b["visual_seed"]["vetoes"] = [v for v in b["visual_seed"]["vetoes"] if v["id"] != "VETO-N08"]
        self.assertCategory(mutate, "VETO_MISSING", "HIGH")

    def test_cover_override_missing(self):
        self.assertCategory(lambda b: b["visual_seed"]["book_dna"].update(role_overrides=[]), "COVER_OVERRIDE_MISSING", "HIGH")

    def test_cover_face_fully_revealed(self):
        def mutate(b):
            composition(b["visual_seed"], "COMP-FRONT")["ext"]["narciso"]["face_fragment"]["visible_ratio_max"] = 0.95
        self.assertCategory(mutate, "COVER_FACE_FULLY_REVEALED", "HIGH")

    def test_cover_face_without_occlusion(self):
        def mutate(b):
            composition(b["visual_seed"], "COMP-FRONT")["ext"]["narciso"]["face_fragment"]["hidden_by"] = []
        self.assertCategory(mutate, "COVER_FACE_FULLY_REVEALED", "HIGH")

    def test_cover_reflection_spoiler(self):
        def mutate(b):
            ext = composition(b["visual_seed"], "COMP-FRONT")["ext"]["narciso"]
            ext.update(reflection_state="ANOMALOUS_MIRROR", reflection_anomaly="mole")
        self.assertCategory(mutate, "COVER_REFLECTION_SPOILER", "HIGH")

    def test_public_decay_exposure(self):
        self.assertCategory(lambda b: composition(b["visual_seed"], "COMP-FRONT")["ext"]["narciso"].update(
            decay_state="D3_WITHERING"), "PUBLIC_DECAY_EXPOSURE", "HIGH")

    def test_surface_nudity(self):
        self.assertCategory(lambda b: composition(b["visual_seed"], "COMP-FRONT")["ext"]["narciso"].update(nudity=True),
                            "SURFACE_NUDITY", "HIGH")

    def test_typography_over_eyes(self):
        def mutate(b):
            composition(b["visual_seed"], "COMP-FRONT")["typography"][0]["zone"] = [0.08, 0.28, 0.92, 0.40]
        self.assertCategory(mutate, "ZONE_COLLISION_FOCAL", "MEDIUM")

    def test_reflection_overloaded(self):
        self.assertCategory(lambda b: composition(b["visual_seed"], "COMP-CASE-HIDDEN")["ext"]["narciso"].update(
            reflection_anomaly=["mole", "ring"]), "REFLECTION_OVERLOADED", "HIGH")

    def test_face_canon_anchor_missing(self):
        self.assertCategory(lambda b: b.update(face_canon_seed=b["face_canon_seed"].replace("palma esquerda", "mão")),
                            "FACE_CANON_ANCHOR_MISSING", "HIGH")

    def test_twin_in_visual_canon(self):
        def mutate(b):
            element(b["visual_seed"], "SYM-ESPELHO")["states"][1]["visual_description"] = "O gêmeo aparece no vidro."
        self.assertCategory(mutate, "TWIN_HYPOTHESIS_INTRODUCED", "BLOCKER")


class TestNarcisoVisualRuntime(unittest.TestCase):
    """O canon visual da obra passa no validador do MOTOR e projeta o declínio."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.runtime = compose_fixture_runtime(Path(cls.tmp))
        cls.canon = yaml.safe_load((cls.runtime / vn.VISUAL_CANON_FILE).read_text(encoding="utf-8"))
        cls.dna = yaml.safe_load((cls.runtime / "author/AUTHOR_VISUAL_DNA.v1.yaml").read_text(encoding="utf-8"))
        cls.context = cvc.load_context(cls.runtime)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_engine_visual_validator_has_no_blocking_findings(self):
        findings = cvc.validate(self.canon, self.dna, self.context, mode="plan", runtime=self.runtime)
        blocking = [f for f in findings if f["severity"] in {"HIGH", "BLOCKER"}]
        self.assertEqual(blocking, [], "\n".join(f"{f['category']}: {f['evidence']} {f['detail']}" for f in blocking))

    def test_only_pending_approvals_remain(self):
        findings = cvc.validate(self.canon, self.dna, self.context, mode="plan", runtime=self.runtime)
        self.assertEqual({f["category"] for f in findings} - {"PENDING_APPROVAL"}, set(),
                         [f"{f['category']} {f['evidence']}" for f in findings])

    def test_every_symbol_and_figure_is_proven(self):
        _, status_map = cvc.check_chekhov(self.canon, self.context, self.dna, "plan")
        for element_id in ["FIG-NARCISO", "SIG-ESPELHO", *vn.REQUIRED_SYMBOL_IDS]:
            self.assertEqual(status_map[element_id][0], "PROVEN", element_id)

    def test_decay_projection_follows_the_canon(self):
        figure = element(self.canon, "FIG-NARCISO")
        expected = {1: "D0_PRISTINE", 14: "D0_PRISTINE", 15: "D1_SLEEPLESS", 17: "D1_SLEEPLESS",
                    18: "D2_FEVER", 22: "D2_FEVER", 23: "D3_WITHERING", 27: "D3_WITHERING",
                    28: "D4_MARBLE", 31: "D4_MARBLE", 32: "D5_TRACE", 33: "D5_TRACE"}
        for chapter_number, state in expected.items():
            self.assertEqual(cvc.project_state(figure, chapter_number, self.context)["state"], state, chapter_number)

    def test_sigil_projection(self):
        sigil = element(self.canon, "SIG-ESPELHO")
        expected = {8: "VELADO", 9: "DESCOBERTO", 16: "MULTIPLICADO", 18: "FRATURADO", 28: "FRENTE_A_FRENTE", 32: "VAZIO"}
        for chapter_number, state in expected.items():
            self.assertEqual(cvc.project_state(sigil, chapter_number, self.context)["state"], state, chapter_number)

    def test_engine_cli_state(self):
        proc = run(REPO / "engine/scripts/check_visual_canon.py", "--runtime", self.runtime,
                   "--state", "FIG-NARCISO", "--at-chapter", "23")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("D3_WITHERING", proc.stdout)

    def test_book_visual_mode_passes_and_requires_canon(self):
        rt = vn.load_runtime(self.runtime)
        self.assertEqual(vn.validate_runtime(rt, "visual"), [])
        rt["visual_canon"] = None
        self.assertIn("VISUAL_CANON_MISSING", {f["category"] for f in vn.validate_runtime(rt, "visual")})

    def test_plan_mode_before_t043_does_not_require_visual_canon(self):
        rt = vn.load_runtime(self.runtime)
        rt["visual_canon"] = None
        self.assertNotIn("VISUAL_CANON_MISSING", {f["category"] for f in vn.validate_runtime(rt, "plan")})


# --- Slice 4: pranchas e sistema de ilustração -----------------------------------

class TestNarcisoPlateMutations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bundle = vn.load_bundle(BOOK)

    def assertCategory(self, mutate, category, severity=None):
        bundle = copy.deepcopy(self.bundle)
        mutate(bundle["visual_seed"])
        findings = vn.check_package(bundle)
        matching = [f for f in findings if f["category"] == category]
        self.assertTrue(matching, f"{category} não emitido; achados: {[f['category'] for f in findings]}")
        if severity:
            self.assertIn(severity, {f["severity"] for f in matching})

    @staticmethod
    def plate(canon, pid):
        return next(c for c in canon["compositions"] if c["id"] == pid)

    def test_seed_declares_all_24_plates(self):
        plates = [c for c in self.bundle["visual_seed"]["compositions"] if c.get("illustration")]
        self.assertEqual(sorted(p["id"] for p in plates), [f"IL-{i:02d}" for i in range(1, 25)])

    def test_slot_without_plate(self):
        def mutate(canon):
            canon["compositions"] = [c for c in canon["compositions"] if c["id"] != "IL-05"]
        self.assertCategory(mutate, "ILLUSTRATION_SLOT_MISMATCH", "HIGH")

    def test_invalid_category(self):
        self.assertCategory(lambda c: self.plate(c, "IL-02")["illustration"].update(category="POSTER"),
                            "ILLUSTRATION_CATEGORY_INVALID", "HIGH")

    def test_reflection_plate_without_reflection(self):
        self.assertCategory(lambda c: self.plate(c, "IL-04")["ext"]["narciso"].update(reflection_state="NONE"),
                            "REFLECTION_PLATE_WITHOUT_REFLECTION", "HIGH")

    def test_decay_state_mismatch_with_projection(self):
        self.assertCategory(lambda c: self.plate(c, "IL-16")["ext"]["narciso"].update(decay_state="D2_FEVER"),
                            "DECAY_STATE_MISMATCH", "HIGH")

    def test_decay_plate_too_early(self):
        def mutate(canon):
            plate = self.plate(canon, "IL-09")
            plate["illustration"]["category"] = "DECAY"
        self.assertCategory(mutate, "DECAY_PLATE_TOO_EARLY", "HIGH")

    def test_callback_undeclared(self):
        self.assertCategory(lambda c: self.plate(c, "IL-17")["illustration"].pop("callback_of"),
                            "CALLBACK_UNDECLARED", "HIGH")

    def test_reflection_plate_single_hypothesis(self):
        self.assertCategory(lambda c: self.plate(c, "IL-05")["ext"]["narciso"].update(hypotheses_supported=["H-SUPER"]),
                            "SINGLE_HYPOTHESIS_EVIDENCE", "HIGH")

    def test_reflection_face_resolved(self):
        self.assertCategory(lambda c: self.plate(c, "IL-18")["ext"]["narciso"].update(reflection_face_visibility="FULL"),
                            "REFLECTION_FACE_RESOLVED", "HIGH")

    def test_act_grammar(self):
        self.assertCategory(lambda c: self.plate(c, "IL-02")["ext"]["narciso"].update(symmetry="FRAGMENTED"),
                            "ACT_GRAMMAR_VIOLATION", "MEDIUM")

    def test_gaze_after_withdrawal(self):
        self.assertCategory(lambda c: self.plate(c, "IL-21")["ext"]["narciso"].update(gaze="TOWARD_READER"),
                            "GAZE_AFTER_WITHDRAWAL", "MEDIUM")

    def test_plate_spoiler_before_anchor(self):
        self.assertCategory(lambda c: self.plate(c, "IL-18")["illustration"].update(placement="OPEN"),
                            "PLATE_SPOILER_BEFORE_ANCHOR", "HIGH")

    def test_plate_nudity_category(self):
        self.assertCategory(lambda c: self.plate(c, "IL-10")["ext"]["narciso"].update(nudity=True),
                            "PLATE_NUDITY_CATEGORY", "HIGH")

    def test_body_overexposed_in_act_three(self):
        def mutate(canon):
            for pid in ("IL-17", "IL-19", "IL-22"):
                plate = self.plate(canon, pid)
                plate["elements"][0] = {"element": "FIG-NARCISO", "prominence": "DOMINANT"}
                plate["ext"]["narciso"]["decay_state"] = "D5_TRACE" if plate["chapter"] >= 32 else "D3_WITHERING" \
                    if plate["chapter"] < 28 else "D4_MARBLE"
        self.assertCategory(mutate, "DECAY_BODY_OVEREXPOSED", "MEDIUM")

    def test_foreshadow_underused(self):
        def mutate(canon):
            for plate in canon["compositions"]:
                block = plate.get("illustration")
                if block and block.get("text_relation") == "FORESHADOW":
                    block.update(text_relation="COMPLEMENT", adds="mudança de teste")
        self.assertCategory(mutate, "FORESHADOW_UNDERUSED", "LOW")


class TestNarcisoMirrorMutations(unittest.TestCase):
    """Slice 5: plano de manifestação por edição e coerência com o canon visual."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = vn.load_bundle(BOOK)

    def assertCategory(self, mutate, category, severity=None):
        bundle = copy.deepcopy(self.bundle)
        mutate(bundle)
        findings = vn.check_package(bundle)
        matching = [f for f in findings if f["category"] == category]
        self.assertTrue(matching, f"{category} não emitido; achados: {[f['category'] for f in findings]}")
        if severity:
            self.assertIn(severity, {f["severity"] for f in matching})

    @staticmethod
    def technique(bundle, tid):
        return next(t for t in bundle["mirror_manifestation"]["techniques"] if t["id"] == tid)

    @staticmethod
    def plate(bundle, pid):
        return next(c for c in bundle["visual_seed"]["compositions"] if c["id"] == pid)

    def test_manifestation_missing(self):
        self.assertCategory(lambda b: b.update(mirror_manifestation=None), "MIRROR_MANIFESTATION_MISSING", "HIGH")

    def test_technique_missing(self):
        def mutate(bundle):
            bundle["mirror_manifestation"]["techniques"] = [
                t for t in bundle["mirror_manifestation"]["techniques"] if t["id"] != "DROP_CAP"]
        self.assertCategory(mutate, "MIRROR_MANIFESTATION_INVALID", "HIGH")

    def test_kindle_must_omit_title_echo(self):
        self.assertCategory(lambda b: self.technique(b, "TITLE_ECHO")["editions"].update(kindle_ebook="ASSET"),
                            "KINDLE_OMISSION_VIOLATED", "HIGH")

    def test_kindle_must_sequence_central_spread(self):
        self.assertCategory(lambda b: self.technique(b, "CENTRAL_SPREAD")["editions"].update(kindle_ebook="INCLUDE"),
                            "KINDLE_OMISSION_VIOLATED", "HIGH")

    def test_physical_mirror_outside_collector_insert(self):
        self.assertCategory(lambda b: self.technique(b, "TITLE_ECHO").update(requires_physical_mirror=True),
                            "MIRROR_REQUIRED_TO_READ", "HIGH")

    def test_spread_moved(self):
        self.assertCategory(lambda b: self.plate(b, "IL-12")["illustration"].pop("pair_with"), "SPREAD_MISPLACED", "HIGH")

    def test_callback_pairs_mismatch(self):
        self.assertCategory(lambda b: b["mirror_manifestation"]["callback_pairs"].pop(), "CALLBACK_PAIRS_MISMATCH", "MEDIUM")

    def test_callback_without_change(self):
        self.assertCategory(lambda b: self.plate(b, "IL-23")["illustration"].pop("callback_changes"),
                            "CALLBACK_WITHOUT_CHANGE", "MEDIUM")

    def test_callback_overloaded(self):
        self.assertCategory(lambda b: self.plate(b, "IL-19")["illustration"]["callback_changes"][0].update(impossible=True),
                            "CALLBACK_OVERLOADED", "MEDIUM")

    def test_title_echo_outside_act_two_presence(self):
        self.assertCategory(lambda b: b["visual_seed"]["display_assets"][0]["chapters"].append(13),
                            "TITLE_ECHO_MISMATCH", "MEDIUM")

    def test_ornament_not_per_act(self):
        self.assertCategory(lambda b: b["visual_seed"]["display_assets"][1]["chapters"].pop(),
                            "ORNAMENT_ACT_MISMATCH", "MEDIUM")


class TestNarcisoIllustrationGraphAndRuntime(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.graph = lb.build_standard_graph(BOOK)
        cls.tmp = tempfile.mkdtemp()
        cls.runtime = compose_fixture_runtime(Path(cls.tmp))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_graph_has_slot_tasks_instead_of_chapter_images(self):
        ids = {t["id"] for t in self.graph["spec"]["tasks"]}
        self.assertNotIn("T401_IMAGE_BRIEF", ids)
        self.assertIn("T4505_IL_CONTINUITY_QA", ids)
        self.assertEqual(len(self.graph["spec"]["gates"]["GATE_VISUAL"]["requires"]), 24)
        self.assertIn("V_NARCISO_ILLUSTRATIONS", self.graph["spec"]["gates"]["GATE_VISUAL"]["custom_validators"])
        self.assertEqual(lb.validate_graph(self.graph, REPO), [])

    def test_engine_validator_accepts_the_24_plates(self):
        canon = yaml.safe_load((self.runtime / vn.VISUAL_CANON_FILE).read_text(encoding="utf-8"))
        dna = yaml.safe_load((self.runtime / "author/AUTHOR_VISUAL_DNA.v1.yaml").read_text(encoding="utf-8"))
        findings = cvc.validate(canon, dna, cvc.load_context(self.runtime), mode="plan", runtime=self.runtime)
        self.assertEqual({f["category"] for f in findings} - {"PENDING_APPROVAL"}, set(),
                         [f"{f['category']} {f['evidence']}" for f in findings if f["category"] != "PENDING_APPROVAL"])

    def test_edition_plans_manifest_the_mirror(self):
        proc = run(REPO / "engine/scripts/check_visual_canon.py", "--runtime", self.runtime, "--edition-plan-all")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        plans = {t: yaml.safe_load((self.runtime / f"layout/editions/{t}/EDITION_PLAN.yaml").read_text(encoding="utf-8"))
                 for t in ("kindle_ebook", "kdp_paperback")}
        layout = {t: {p["composition"]: p["layout"] for p in plans[t]["interior_plates"]} for t in plans}
        self.assertEqual(layout["kindle_ebook"]["IL-12"], "SEQUENTIAL")
        self.assertEqual(layout["kdp_paperback"]["IL-12"], "SPREAD")
        self.assertEqual({e["status"] for e in plans["kindle_ebook"]["chapter_display"]}, {"OMITTED"})
        paperback = plans["kdp_paperback"]["chapter_display"]
        self.assertEqual(sorted(e["chapter"] for e in paperback if e["kind"] == "TITLE_ECHO"), [12, 15, 17, 19, 22])
        self.assertEqual(len([e for e in paperback if e["kind"] == "ORNAMENT"]), 33)

    def test_illustrations_mode_without_artifacts_passes(self):
        rt = vn.load_runtime(self.runtime)
        self.assertEqual(vn.validate_runtime(rt, "illustrations"), [])

    def test_approved_reflection_plate_requires_anomaly_qa(self):
        rt = vn.load_runtime(self.runtime)
        rt["illustration_artifacts"] = {"IL-05": {"approved": True, "continuity_qa": "Rosto conferido."}}
        self.assertIn("REFLECTION_QA_SKIPPED", {f["category"] for f in vn.validate_runtime(rt, "illustrations")})
        rt["illustration_artifacts"] = {"IL-05": {"approved": True,
                                                  "continuity_qa": "Anomalia declarada: pinta. Anomalia observada: pinta."}}
        self.assertEqual(vn.validate_runtime(rt, "illustrations"), [])

    def test_prompt_leaking_hypothesis(self):
        rt = vn.load_runtime(self.runtime)
        rt["illustration_artifacts"] = {"IL-04": {"brief": "Mostrar que a figura na água é uma alucinação."}}
        self.assertIn("PROMPT_LEAKS_HYPOTHESIS", {f["category"] for f in vn.validate_runtime(rt, "illustrations")})

    def test_artifacts_are_loaded_from_disk(self):
        (self.runtime / "images/illustrations/IL-12").mkdir(parents=True, exist_ok=True)
        (self.runtime / "images/illustrations/IL-12/CONTINUITY_QA.md").write_text("Anomalia: cicatriz.", encoding="utf-8")
        (self.runtime / "images/prompts").mkdir(parents=True, exist_ok=True)
        (self.runtime / "images/prompts/IL-12_IMAGE_BRIEF.md").write_text("Duas mãos e uma gota.", encoding="utf-8")
        (self.runtime / "images/approved").mkdir(parents=True, exist_ok=True)
        (self.runtime / "images/approved/IL-12.jpg").write_bytes(b"jpg")
        rt = vn.load_runtime(self.runtime)
        self.assertEqual(set(rt["illustration_artifacts"]["IL-12"]), {"approved", "brief", "continuity_qa"})
        proc = run(self.runtime / "book/validators/validate_narciso.py", "--runtime", self.runtime, "--mode", "illustrations")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
