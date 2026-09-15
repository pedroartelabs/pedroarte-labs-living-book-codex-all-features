"""Testes de regressão do compositor — Slice 4 de `DARK_ROMANCE_CANON_ARCHITECT`
(ver docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md).

Duas coisas precisam ser verdade ao mesmo tempo:

1. **INV-14** — um livro que não declara `features.causal_ledger` compõe um
   grafo IDÊNTICO ao de antes desta capability existir. Os arquivos em
   `tests/fixtures/golden/*.json` foram gerados chamando
   `build_standard_graph()` no compositor AINDA NÃO MODIFICADO (mesmo commit
   em que este arquivo de teste foi adicionado) — comparar contra eles é
   literalmente "gravar o dict antes, comparar depois", como o SDD pede.
2. O livro fixture que LIGA a feature (`tests/fixtures/books/causal_ledger_mvp/`)
   recebe exatamente a integração descrita no SDD: `CAUSAL_LEDGER.yaml` como
   saída de T018, `T021_LEDGER_SNAPSHOT` + um snapshot por wave com `tool`, e
   os três validadores `V_CAUSAL_LEDGER_*` presos a `GATE_CANON`, a cada
   `GATE_WAVE_n` e a `GATE_FULL_MANUSCRIPT`.

100% offline: `build_standard_graph()` não faz nenhuma chamada de rede ou de
modelo. Os testes de compose+smoke-test rodam num diretório temporário.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import livingbook as lb  # noqa: E402
import detect_repetition  # noqa: E402

GOLDEN_DIR = REPO / "tests" / "fixtures" / "golden"
FIXTURE_BOOK = REPO / "tests" / "fixtures" / "books" / "causal_ledger_mvp"
RUNBOOK_PATH = REPO / "engine" / "templates" / "CAUSAL_LEDGER_RUNBOOK.md"
LEDGER_TEMPLATE_PATH = REPO / "engine" / "templates" / "CAUSAL_LEDGER_TEMPLATE.yaml"

# BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM (docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md),
# Slice 5.
VN_FIXTURE_BOOK = REPO / "tests" / "fixtures" / "books" / "visual_narrative_mvp"
VN_RUNBOOK_PATH = REPO / "engine" / "templates" / "VISUAL_NARRATIVE_RUNBOOK.md"
VN_CANON_TEMPLATE_PATH = REPO / "engine" / "templates" / "VISUAL_NARRATIVE_CANON_TEMPLATE.yaml"
VN_AUTHOR_DNA_TEMPLATE_PATH = REPO / "engine" / "templates" / "AUTHOR_VISUAL_DNA_TEMPLATE.yaml"
VN_REAL_AUTHOR_DNA_PATH = REPO / "authors" / "bea_halden" / "AUTHOR_VISUAL_DNA.v1.yaml"
VN_SAMPLE_CANON_PATH = (REPO / "tests" / "fixtures" / "visual_narrative" / "runtime_cisne_negro"
                         / "canon" / "VISUAL_NARRATIVE_CANON.yaml")

# Os mesmos 6 livros listados no SDD, seção L (Slice 4, "Regressions protected").
EXISTING_BOOK_SLUGS = [
    "a_morte_ainda_nao_nasceu",
    "motor-de-livros-vivos",
    "o_jardim_dos_doze",
    "eva-a-ultima-mulher-da-terra",
    "adao-o-ultimo-homem-da-terra",
    "loja-de-poderes-vivos",
]


class TestExistingBooksAreUnaffected(unittest.TestCase):
    """INV-14: nenhum livro sem a feature muda de comportamento."""

    def test_golden_graphs_match_exactly(self):
        for slug in EXISTING_BOOK_SLUGS:
            with self.subTest(slug=slug):
                golden_path = GOLDEN_DIR / f"{slug}.json"
                self.assertTrue(golden_path.is_file(), f"golden ausente: {golden_path}")
                golden = json.loads(golden_path.read_text(encoding="utf-8"))
                current = lb.build_standard_graph(REPO / "books" / slug)
                self.assertEqual(current, golden,
                                 f"build_standard_graph({slug}) mudou depois do Slice 4 — "
                                 "isso é uma regressão de INV-14, não uma melhoria.")

    def test_no_existing_book_gains_causal_ledger_artifacts(self):
        # Redundante com o golden acima por desenho: é a versão legível caso o
        # golden precise ser regenerado por um motivo genuíno e não relacionado.
        for slug in EXISTING_BOOK_SLUGS:
            with self.subTest(slug=slug):
                graph = lb.build_standard_graph(REPO / "books" / slug)
                task_ids = {t["id"] for t in graph["spec"]["tasks"]}
                validator_ids = {v["id"] for v in graph["spec"]["custom_validators"]}
                self.assertFalse(any("LEDGER_SNAPSHOT" in tid for tid in task_ids), slug)
                self.assertFalse(any(vid.startswith("V_CAUSAL_LEDGER") for vid in validator_ids), slug)
                t018 = next(t for t in graph["spec"]["tasks"] if t["id"] == "T018_CANON_REGISTRY")
                self.assertEqual(t018["outputs"], ["/canon/CANON_REGISTRY.yaml"], slug)

    def test_no_existing_book_gains_visual_narrative_artifacts(self):
        # Mesma lógica, para a capability BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM
        # (Slice 5) — redundante com o golden acima por desenho.
        for slug in EXISTING_BOOK_SLUGS:
            with self.subTest(slug=slug):
                graph = lb.build_standard_graph(REPO / "books" / slug)
                task_ids = {t["id"] for t in graph["spec"]["tasks"]}
                validator_ids = {v["id"] for v in graph["spec"]["custom_validators"]}
                locks = {lock for t in graph["spec"]["tasks"] for lock in t.get("locks", [])}
                self.assertNotIn("T042_VISUAL_DISCOVERY", task_ids, slug)
                self.assertNotIn("T043_VISUAL_NARRATIVE_CANON", task_ids, slug)
                self.assertNotIn("VISUAL_CANON_WRITE", locks, slug)
                self.assertFalse(any(vid.startswith("V_VISUAL_") for vid in validator_ids), slug)

    def test_causal_ledger_fixture_does_not_gain_visual_narrative_artifacts(self):
        # Contraprova cruzada: o fixture que liga causal_ledger (mas não
        # visual_narrative) também não ganha nada da outra capability — as
        # duas features são lidas de chaves independentes em `features.*`.
        graph = lb.build_standard_graph(FIXTURE_BOOK)
        task_ids = {t["id"] for t in graph["spec"]["tasks"]}
        validator_ids = {v["id"] for v in graph["spec"]["custom_validators"]}
        self.assertNotIn("T042_VISUAL_DISCOVERY", task_ids)
        self.assertFalse(any(vid.startswith("V_VISUAL_") for vid in validator_ids))


class TestCausalLedgerFixtureBookWiring(unittest.TestCase):
    """O livro fixture, que liga a feature, recebe a integração completa."""

    @classmethod
    def setUpClass(cls):
        cls.graph = lb.build_standard_graph(FIXTURE_BOOK)

    def test_t018_declares_causal_ledger_output(self):
        t018 = next(t for t in self.graph["spec"]["tasks"] if t["id"] == "T018_CANON_REGISTRY")
        self.assertIn("/canon/CAUSAL_LEDGER.yaml", t018["outputs"])
        self.assertIn("/canon/CANON_REGISTRY.yaml", t018["outputs"])  # nada foi removido

    def test_snapshot_tasks_have_tool_and_correct_dependencies(self):
        tasks_by_id = {t["id"]: t for t in self.graph["spec"]["tasks"]}
        self.assertIn("T021_LEDGER_SNAPSHOT", tasks_by_id)
        self.assertEqual(tasks_by_id["T021_LEDGER_SNAPSHOT"]["depends_on"], ["T018_CANON_REGISTRY"])
        self.assertTrue(tasks_by_id["T021_LEDGER_SNAPSHOT"].get("tool"))
        wave_snapshot_ids = sorted(tid for tid in tasks_by_id if tid.endswith("Z_LEDGER_SNAPSHOT"))
        self.assertEqual(wave_snapshot_ids,
                         ["T201Z_LEDGER_SNAPSHOT", "T202Z_LEDGER_SNAPSHOT", "T203Z_LEDGER_SNAPSHOT"])
        for tid in wave_snapshot_ids:
            self.assertTrue(tasks_by_id[tid].get("tool"))

    def test_gates_carry_the_three_validator_families(self):
        gates = self.graph["spec"]["gates"]
        self.assertIn("V_CAUSAL_LEDGER_PLAN", gates["GATE_CANON"]["custom_validators"])
        self.assertIn("T021_LEDGER_SNAPSHOT", gates["GATE_CANON"]["requires"])
        for wi in (1, 2, 3):
            self.assertIn(f"V_CAUSAL_LEDGER_WAVE_{wi}", gates[f"GATE_WAVE_{wi}"]["custom_validators"])
            self.assertIn(f"T20{wi}Z_LEDGER_SNAPSHOT", gates[f"GATE_WAVE_{wi}"]["requires"])
        self.assertIn("V_CAUSAL_LEDGER_FINAL", gates["GATE_FULL_MANUSCRIPT"]["custom_validators"])

    def test_validator_commands_carry_book_declared_thresholds_and_baselines(self):
        validators = {v["id"]: v["command"] for v in self.graph["spec"]["custom_validators"]}
        for vid in ("V_CAUSAL_LEDGER_PLAN", "V_CAUSAL_LEDGER_WAVE_1", "V_CAUSAL_LEDGER_WAVE_2",
                    "V_CAUSAL_LEDGER_WAVE_3", "V_CAUSAL_LEDGER_FINAL"):
            self.assertIn("--min-payoff-feeds 2", validators[vid])
            self.assertIn("--max-monotonic-run 3", validators[vid])
        self.assertIn("--mode plan", validators["V_CAUSAL_LEDGER_PLAN"])
        self.assertIn("--baseline canon/snapshots/CAUSAL_LEDGER.WAVE_00.yaml", validators["V_CAUSAL_LEDGER_WAVE_1"])
        self.assertIn("--baseline canon/snapshots/CAUSAL_LEDGER.WAVE_01.yaml", validators["V_CAUSAL_LEDGER_WAVE_2"])
        self.assertIn("--baseline canon/snapshots/CAUSAL_LEDGER.WAVE_02.yaml", validators["V_CAUSAL_LEDGER_WAVE_3"])
        self.assertIn("--baseline canon/snapshots/CAUSAL_LEDGER.WAVE_03.yaml", validators["V_CAUSAL_LEDGER_FINAL"])
        self.assertIn("--chapter-architecture book/chapter_architecture.yaml", validators["V_CAUSAL_LEDGER_FINAL"])

    def test_graph_validates_without_errors(self):
        errors = lb.validate_graph(self.graph, FIXTURE_BOOK)
        self.assertEqual(errors, [])

    def test_slice5_task_instructions_are_wired(self):
        """SDD, Slice 5: as tarefas já existentes sabem ler, propor e manter
        o ledger — sem nenhum agente novo. Cada uma carrega `parameters.causal_ledger`
        e os `inputs` relevantes."""
        tasks_by_id = {t["id"]: t for t in self.graph["spec"]["tasks"]}
        ledger_template = "/engine/templates/CAUSAL_LEDGER_TEMPLATE.yaml"

        for task_id in ("T013_CHARACTER_BIBLE", "T016_PLOT_DEPENDENCY_MAP",
                        "T018_CANON_REGISTRY", "T032_READER_VITALS",
                        "T035_MEMORY_MOTIF_MAP", "T101_BRIEF_CHAPTER",
                        "T201_WRITE", "T201_CANON_UPDATE"):
            with self.subTest(task_id=task_id):
                self.assertIn("causal_ledger", tasks_by_id[task_id].get("parameters", {}))

        self.assertIn(ledger_template, tasks_by_id["T013_CHARACTER_BIBLE"]["inputs"])
        self.assertIn(ledger_template, tasks_by_id["T016_PLOT_DEPENDENCY_MAP"]["inputs"])
        self.assertIn("/canon/CANON_PROPOSALS", tasks_by_id["T018_CANON_REGISTRY"]["inputs"])
        self.assertIn("/canon/CAUSAL_LEDGER.yaml", tasks_by_id["T035_MEMORY_MOTIF_MAP"]["inputs"])
        self.assertIn("/canon/CAUSAL_LEDGER.yaml", tasks_by_id["T101_BRIEF_CHAPTER"]["inputs"])
        self.assertIn("/canon/CAUSAL_LEDGER.yaml",
                      tasks_by_id["T201_WRITE"]["spawn"]["shared_inputs"])
        self.assertIn("/canon/CAUSAL_LEDGER.yaml", tasks_by_id["T201_CANON_UPDATE"]["inputs"])
        self.assertIn("/canon/CANON_PROPOSALS", tasks_by_id["T201_CANON_UPDATE"]["inputs"])

    def test_slice5_instructions_touch_only_this_fixture(self):
        # Contraprova: os mesmos ids em livros sem a feature não ganham nada.
        graph = lb.build_standard_graph(REPO / "books/motor-de-livros-vivos")
        t013 = next(t for t in graph["spec"]["tasks"] if t["id"] == "T013_CHARACTER_BIBLE")
        self.assertNotIn("causal_ledger", t013.get("parameters", {}))
        self.assertNotIn("inputs", t013)


class TestCausalLedgerFixtureComposeAndSmoke(unittest.TestCase):
    """Fim a fim, num diretório temporário: compose + smoke-test precisam
    funcionar para o livro fixture exatamente como para qualquer outro."""

    def test_compose_then_smoke_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp) / "causal_ledger_mvp"
            compose = subprocess.run(
                [sys.executable, str(REPO / "engine/scripts/livingbook.py"), "compose",
                 "--book", str(FIXTURE_BOOK), "--runtime", str(runtime)],
                cwd=REPO, capture_output=True, text=True,
            )
            self.assertEqual(compose.returncode, 0, compose.stdout + compose.stderr)
            self.assertIn("COMPOSED", compose.stdout)

            smoke = subprocess.run(
                [sys.executable, str(REPO / "engine/scripts/livingbook.py"), "smoke-test",
                 "--runtime", str(runtime)],
                cwd=REPO, capture_output=True, text=True,
            )
            self.assertEqual(smoke.returncode, 0, smoke.stdout + smoke.stderr)
            self.assertIn("SMOKE TEST OK", smoke.stdout)

            self.assertTrue((runtime / "canon" / "AGENTS.md").is_file())
            self.assertTrue((runtime / "templates" / "CAUSAL_LEDGER_TEMPLATE.yaml").is_file())
            self.assertTrue((runtime / "scripts" / "check_causal_ledger.py").is_file())

    def test_runbook_is_copied_as_canon_agents_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp) / "causal_ledger_mvp"
            subprocess.run(
                [sys.executable, str(REPO / "engine/scripts/livingbook.py"), "compose",
                 "--book", str(FIXTURE_BOOK), "--runtime", str(runtime)],
                cwd=REPO, capture_output=True, text=True, check=True,
            )
            copied = (runtime / "canon" / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(copied, RUNBOOK_PATH.read_text(encoding="utf-8"))

    def test_existing_book_still_composes_with_no_canon_agents_md(self):
        # Contraprova no mesmo teste de integração: um livro sem a feature
        # não ganha canon/AGENTS.md nem os artefatos do ledger no runtime.
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp) / "motor-de-livros-vivos"
            compose = subprocess.run(
                [sys.executable, str(REPO / "engine/scripts/livingbook.py"), "compose",
                 "--book", str(REPO / "books/motor-de-livros-vivos"), "--runtime", str(runtime)],
                cwd=REPO, capture_output=True, text=True,
            )
            self.assertEqual(compose.returncode, 0, compose.stdout + compose.stderr)
            self.assertFalse((runtime / "canon" / "AGENTS.md").exists())


def _collect_yaml_keys(obj, keys=None):
    """Toda chave de dict, recursivamente — a superfície real de campos do
    contrato, derivada do próprio arquivo em vez de mantida à mão."""
    if keys is None:
        keys = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str):
                keys.add(k)
            _collect_yaml_keys(v, keys)
    elif isinstance(obj, list):
        for item in obj:
            _collect_yaml_keys(item, keys)
    return keys


# Flags reais de engine/scripts/check_causal_ledger.py (argparse). O runbook
# pode citar qualquer uma; não vêm do YAML do template, por isso são mantidas
# à parte.
KNOWN_CLI_FLAGS = {
    "why", "relationship", "payoff", "knowledge", "beliefs", "recontextualized",
    "engine-view", "chapter-architecture", "end-state", "snapshot-auto",
    "min-payoff-feeds", "max-monotonic-run", "max-loop-silence",
    "baseline", "mode", "runtime", "ledger", "json", "out", "at-chapter",
}

# Um punhado de palavras genéricas de prosa que passam pelo regex de token
# "snake_case" abaixo por acaso (sem hífen/maiúsculas) mas não são campo nem
# flag — a lista existe para o teste não ficar frágil por causa de prosa
# comum entre crases.
PROSE_EXCEPTIONS = {"nunca", "python"}


class TestCausalLedgerRunbookFieldNames(unittest.TestCase):
    """SDD, Slice 5: 'runbook cita apenas campos que o validador conhece' —
    todo token entre crases em formato snake_case ou `--flag` no runbook
    precisa ser um campo real do template ou uma flag real do CLI."""

    def test_runbook_backticked_fields_are_known(self):
        template = yaml.safe_load(LEDGER_TEMPLATE_PATH.read_text(encoding="utf-8"))
        known_fields = _collect_yaml_keys(template)
        # emotional_movement é campo real do contrato, mas deliberadamente NÃO
        # mora no ledger (E.4 do SDD) — o runbook o cita para explicar isso, e
        # seu esquema vive em chapter_architecture.yaml, não no template acima.
        arch_fixture = REPO / "tests/fixtures/causal_ledger/chapter_architecture.yaml"
        known_fields |= _collect_yaml_keys(yaml.safe_load(arch_fixture.read_text(encoding="utf-8")))

        text = RUNBOOK_PATH.read_text(encoding="utf-8")
        # Blocos ```fenced``` usam corridas de 3 crases para abrir/fechar; um
        # regex de crase única os leria como pares extras e desalinharia a
        # paridade de tudo que vem depois. Remova-os antes de extrair spans
        # de código inline.
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        backticked = re.findall(r"`([^`]+)`", text)

        field_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        flag_pattern = re.compile(r"^--([a-z][a-z-]*)$")

        unknown = []
        for token in backticked:
            token = token.strip()
            if flag_pattern.match(token):
                name = flag_pattern.match(token).group(1)
                if name not in KNOWN_CLI_FLAGS:
                    unknown.append(token)
                continue
            if field_pattern.match(token):
                if token in PROSE_EXCEPTIONS:
                    continue
                if token not in known_fields:
                    unknown.append(token)
            # tokens com '/', '.', maiúsculas ou espaço (caminhos, comandos,
            # constantes de estado) não são campos do ledger — não checados.
        self.assertEqual(unknown, [],
                         f"runbook cita token(s) que não são campo do template nem flag do CLI: {unknown}")


class TestCausalLedgerBookTextQuality(unittest.TestCase):
    """SDD, Slice 5: clichês de gênero em `book/text_quality.yaml`, mesclados
    com a base do motor (Anti-Cliché, C.3)."""

    def test_genre_cliches_extend_the_base_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp) / "causal_ledger_mvp"
            subprocess.run(
                [sys.executable, str(REPO / "engine/scripts/livingbook.py"), "compose",
                 "--book", str(FIXTURE_BOOK), "--runtime", str(runtime)],
                cwd=REPO, capture_output=True, text=True, check=True,
            )
            cfg = detect_repetition.load_config(runtime)
            patterns = set(cfg["cliches"]["patterns"])
            self.assertIn("coração disparado", patterns)          # base do motor preservada
            self.assertIn("sorriso predatório", patterns)          # extensão específica do gênero


class TestVisualNarrativeFixtureBookWiring(unittest.TestCase):
    """SDD, Slice 5 (BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM): o livro fixture que
    liga `features.visual_narrative` recebe a integração completa descrita
    na seção 28.2 e no próprio Slice 5 (tarefas, lock, gates, validadores)."""

    @classmethod
    def setUpClass(cls):
        cls.graph = lb.build_standard_graph(VN_FIXTURE_BOOK)

    def test_discovery_decision_canonization_tasks_have_correct_dependencies(self):
        tasks_by_id = {t["id"]: t for t in self.graph["spec"]["tasks"]}
        self.assertEqual(tasks_by_id["T042_VISUAL_DISCOVERY"]["depends_on"], ["GATE_CANON"])
        self.assertEqual(tasks_by_id["T043_VISUAL_NARRATIVE_CANON"]["depends_on"],
                          ["T042_VISUAL_DISCOVERY"])
        self.assertIn("VISUAL_CANON_WRITE", tasks_by_id["T043_VISUAL_NARRATIVE_CANON"]["locks"])
        self.assertEqual(tasks_by_id["T044_VISUAL_CANON_SNAPSHOT"]["depends_on"],
                          ["T043_VISUAL_NARRATIVE_CANON"])
        self.assertTrue(tasks_by_id["T044_VISUAL_CANON_SNAPSHOT"].get("tool"))

    def test_realization_tasks_depend_on_frozen_manuscript(self):
        tasks_by_id = {t["id"]: t for t in self.graph["spec"]["tasks"]}
        self.assertEqual(tasks_by_id["T311_VISUAL_STATE_REALIZATION"]["depends_on"],
                          ["T310_FREEZE_MANUSCRIPT"])
        self.assertIn("VISUAL_CANON_WRITE", tasks_by_id["T311_VISUAL_STATE_REALIZATION"]["locks"])
        self.assertEqual(tasks_by_id["T312_VISUAL_CANON_SNAPSHOT"]["depends_on"],
                          ["T311_VISUAL_STATE_REALIZATION"])
        self.assertTrue(tasks_by_id["T312_VISUAL_CANON_SNAPSHOT"].get("tool"))

    def test_edition_plan_and_print_geometry_tasks_are_mechanical(self):
        tasks_by_id = {t["id"]: t for t in self.graph["spec"]["tasks"]}
        self.assertEqual(tasks_by_id["T698_EDITION_PLAN"]["depends_on"], ["GATE_FULL_MANUSCRIPT"])
        self.assertTrue(tasks_by_id["T698_EDITION_PLAN"].get("tool"))
        self.assertEqual(tasks_by_id["T707_PRINT_GEOMETRY"]["depends_on"], ["T705_DOCX_FINAL_FIXES"])
        self.assertTrue(tasks_by_id["T707_PRINT_GEOMETRY"].get("tool"))

    def test_visual_canon_write_lock_is_scoped_to_exactly_two_tasks(self):
        locked = sorted(t["id"] for t in self.graph["spec"]["tasks"]
                         if "VISUAL_CANON_WRITE" in t.get("locks", []))
        self.assertEqual(locked, ["T043_VISUAL_NARRATIVE_CANON", "T311_VISUAL_STATE_REALIZATION"])

    def test_gates_carry_the_four_validator_families(self):
        gates = self.graph["spec"]["gates"]
        self.assertIn("V_VISUAL_CANON_PLAN", gates["GATE_LIVING_BOOK"]["custom_validators"])
        for tid in ("T042_VISUAL_DISCOVERY", "T043_VISUAL_NARRATIVE_CANON", "T044_VISUAL_CANON_SNAPSHOT"):
            self.assertIn(tid, gates["GATE_LIVING_BOOK"]["requires"])

        self.assertIn("V_VISUAL_CANON_REALIZED", gates["GATE_FULL_MANUSCRIPT"]["custom_validators"])
        for tid in ("T311_VISUAL_STATE_REALIZATION", "T312_VISUAL_CANON_SNAPSHOT"):
            self.assertIn(tid, gates["GATE_FULL_MANUSCRIPT"]["requires"])

        self.assertIn("V_VISUAL_EDITION", gates["GATE_KDP"]["custom_validators"])
        for tid in ("T698_EDITION_PLAN", "T707_PRINT_GEOMETRY"):
            self.assertIn(tid, gates["GATE_KDP"]["requires"])

        self.assertIn("V_VISUAL_ASSETS", gates["GATE_MEDIA_ASSETS"]["custom_validators"])
        self.assertIn("V_MEDIA_ASSET_PACKAGE", gates["GATE_MEDIA_ASSETS"]["custom_validators"])

    def test_graph_validates_without_errors(self):
        # Cobre também o risco de ciclo registrado no Slice 5 da SDD: T036
        # passa a depender de T043, e T041 herda essa ordem transitivamente
        # (T036 já é dependência de T041) — validate_graph detecta ciclo se
        # essa nova aresta formar um.
        errors = lb.validate_graph(self.graph, VN_FIXTURE_BOOK)
        self.assertEqual(errors, [])

    def test_t036_depends_on_t043_without_forming_a_cycle(self):
        tasks_by_id = {t["id"]: t for t in self.graph["spec"]["tasks"]}
        self.assertIn("T043_VISUAL_NARRATIVE_CANON", tasks_by_id["T036_VISUAL_LIFE_SPEC"]["depends_on"])
        self.assertEqual(tasks_by_id["T043_VISUAL_NARRATIVE_CANON"]["depends_on"],
                          ["T042_VISUAL_DISCOVERY"])  # nunca depende de volta de T036/T041


class TestVisualNarrativeFixtureComposeAndSmoke(unittest.TestCase):
    """Fim a fim, num diretório temporário: compose + smoke-test precisam
    funcionar para o livro fixture exatamente como para qualquer outro."""

    def test_compose_then_smoke_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp) / "visual_narrative_mvp"
            compose = subprocess.run(
                [sys.executable, str(REPO / "engine/scripts/livingbook.py"), "compose",
                 "--book", str(VN_FIXTURE_BOOK), "--runtime", str(runtime)],
                cwd=REPO, capture_output=True, text=True,
            )
            self.assertEqual(compose.returncode, 0, compose.stdout + compose.stderr)
            self.assertIn("COMPOSED", compose.stdout)

            smoke = subprocess.run(
                [sys.executable, str(REPO / "engine/scripts/livingbook.py"), "smoke-test",
                 "--runtime", str(runtime)],
                cwd=REPO, capture_output=True, text=True,
            )
            self.assertEqual(smoke.returncode, 0, smoke.stdout + smoke.stderr)
            self.assertIn("SMOKE TEST OK", smoke.stdout)

            self.assertTrue((runtime / "canon" / "VISUAL_AGENTS.md").is_file())
            self.assertTrue((runtime / "author" / "AUTHOR_VISUAL_DNA.v1.yaml").is_file())
            self.assertTrue((runtime / "scripts" / "check_visual_canon.py").is_file())
            self.assertTrue((runtime / "templates" / "EDITION_CAPABILITIES.yaml").is_file())
            self.assertTrue((runtime / "templates" / "PRINT_GEOMETRY.yaml").is_file())

    def test_runbook_is_copied_as_canon_visual_agents_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp) / "visual_narrative_mvp"
            subprocess.run(
                [sys.executable, str(REPO / "engine/scripts/livingbook.py"), "compose",
                 "--book", str(VN_FIXTURE_BOOK), "--runtime", str(runtime)],
                cwd=REPO, capture_output=True, text=True, check=True,
            )
            copied = (runtime / "canon" / "VISUAL_AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(copied, VN_RUNBOOK_PATH.read_text(encoding="utf-8"))

    def test_existing_book_still_composes_with_no_visual_agents_md(self):
        # Contraprova no mesmo teste de integração: um livro sem a feature
        # não ganha canon/VISUAL_AGENTS.md nem os artefatos da capability.
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp) / "motor-de-livros-vivos"
            compose = subprocess.run(
                [sys.executable, str(REPO / "engine/scripts/livingbook.py"), "compose",
                 "--book", str(REPO / "books/motor-de-livros-vivos"), "--runtime", str(runtime)],
                cwd=REPO, capture_output=True, text=True,
            )
            self.assertEqual(compose.returncode, 0, compose.stdout + compose.stderr)
            self.assertFalse((runtime / "canon" / "VISUAL_AGENTS.md").exists())
            self.assertFalse((runtime / "author").exists())


# Flags reais de engine/scripts/check_visual_canon.py (argparse).
VN_KNOWN_CLI_FLAGS = {
    "runtime", "canon", "author-dna", "mode", "baseline", "json", "out",
    "why", "evidence", "state", "at-chapter", "timeline", "exposure", "end-state",
    "target", "capabilities", "print-geometry", "print-spec", "printer-profile",
    "edition-plan", "resolve", "geometry", "production-manifest",
    "cover-image", "thumbnails-dir", "snapshot-as", "edition-plan-all",
    "print-geometry-all", "validate-editions",
}

# "causal_ledger" é o nome de outra capability, citado em prosa (não um campo
# do canon visual) — mesma ideia de PROSE_EXCEPTIONS acima, mantida à parte
# porque é específica deste runbook.
VN_PROSE_EXCEPTIONS = PROSE_EXCEPTIONS | {"causal_ledger"}


class TestVisualNarrativeRunbookFieldNames(unittest.TestCase):
    """SDD, Slice 5: 'runbook só cita campos conhecidos' — todo token entre
    crases em formato snake_case ou `--flag` no VISUAL_NARRATIVE_RUNBOOK.md
    precisa ser um campo real de um contrato ou uma flag real do CLI."""

    def test_runbook_backticked_fields_are_known(self):
        known_fields = set()
        known_fields |= _collect_yaml_keys(
            yaml.safe_load(VN_CANON_TEMPLATE_PATH.read_text(encoding="utf-8")))
        known_fields |= _collect_yaml_keys(
            yaml.safe_load(VN_AUTHOR_DNA_TEMPLATE_PATH.read_text(encoding="utf-8")))
        # O template deixa elements/compositions/finish_intents vazios (os
        # campos de cada item só existem como comentário de exemplo) — a
        # fixture de teste com dados reais (Slice 1) é a fonte real desses
        # nomes de campo, mesmo papel que chapter_architecture.yaml cumpre
        # para o runbook do ledger causal.
        known_fields |= _collect_yaml_keys(
            yaml.safe_load(VN_SAMPLE_CANON_PATH.read_text(encoding="utf-8")))
        # edition_targets é campo de BOOK_SPEC.yaml (features.visual_narrative),
        # não do canon visual nem do Author DNA.
        known_fields |= _collect_yaml_keys(
            yaml.safe_load((VN_FIXTURE_BOOK / "BOOK_SPEC.yaml").read_text(encoding="utf-8")))

        text = VN_RUNBOOK_PATH.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        backticked = re.findall(r"`([^`]+)`", text)

        field_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        flag_pattern = re.compile(r"^--([a-z][a-z-]*)$")

        unknown = []
        for token in backticked:
            token = token.strip()
            if flag_pattern.match(token):
                name = flag_pattern.match(token).group(1)
                if name not in VN_KNOWN_CLI_FLAGS:
                    unknown.append(token)
                continue
            if field_pattern.match(token):
                if token in VN_PROSE_EXCEPTIONS:
                    continue
                if token not in known_fields:
                    unknown.append(token)
        self.assertEqual(unknown, [],
                         f"runbook cita token(s) que não são campo de contrato nem flag do CLI: {unknown}")


if __name__ == "__main__":
    unittest.main()
