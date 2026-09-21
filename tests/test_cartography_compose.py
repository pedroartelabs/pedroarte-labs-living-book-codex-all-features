"""Integração da cartografia no compose (Slice 5 do SDD da cartografia, seções 27.2, 29.1, 36.1; T29, T31).

`features.cartography` OFF por padrão: nenhum livro que não a declara muda (o golden de
tests/test_compose_regression.py continua sendo a prova; aqui está a versão legível). O livro-fixture
`tests/fixtures/books/cartography_mvp` liga a feature com o mini-mundo neutro de Valdoro.

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_cartography_compose -v
"""
from __future__ import annotations

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

import livingbook as lb  # noqa: E402

FIXTURE_BOOK = REPO / "tests" / "fixtures" / "books" / "cartography_mvp"
LEDGER_BOOK = REPO / "tests" / "fixtures" / "books" / "causal_ledger_mvp"
EXISTING = ["a_morte_ainda_nao_nasceu", "motor-de-livros-vivos", "o_jardim_dos_doze", "eva-a-ultima-mulher-da-terra",
            "adao-o-ultimo-homem-da-terra", "loja-de-poderes-vivos"]
LIVINGBOOK = REPO / "engine" / "scripts" / "livingbook.py"
GRAPH = lb.build_standard_graph(FIXTURE_BOOK)
TASKS = {t["id"]: t for t in GRAPH["spec"]["tasks"]}
GATES = GRAPH["spec"]["gates"]
VALIDATORS = {v["id"]: v for v in GRAPH["spec"]["custom_validators"]}


class OffByDefault(unittest.TestCase):
    def test_t31_nenhum_livro_existente_ganha_cartografia(self):
        for slug in EXISTING:
            with self.subTest(slug=slug):
                blob = json.dumps(lb.build_standard_graph(REPO / "books" / slug), ensure_ascii=False).upper()
                self.assertNotIn("CARTO", blob)

    def test_ledger_fixture_nao_ganha_cartografia(self):
        self.assertNotIn("CARTO", json.dumps(lb.build_standard_graph(LEDGER_BOOK), ensure_ascii=False).upper())

    def test_sem_features_cartography_o_livro_da_fixture_seria_o_do_ledger_menos_o_ledger(self):
        spec = yaml.safe_load((FIXTURE_BOOK / "BOOK_SPEC.yaml").read_text(encoding="utf-8"))
        self.assertTrue(spec["spec"]["features"]["cartography"]["enabled"])
        self.assertNotIn("causal_ledger", spec["spec"]["features"])


class Wiring(unittest.TestCase):
    def test_t018c_e_snapshot_inicial_no_gate_canon(self):
        self.assertEqual(TASKS["T018C_CARTOGRAPHY"]["owner"], "CANON_GUARDIAN")
        self.assertEqual(TASKS["T018C_CARTOGRAPHY"]["depends_on"], ["T018_CANON_REGISTRY"])
        self.assertEqual(TASKS["T018C_CARTOGRAPHY"]["locks"], ["CANON_WRITE"])
        self.assertIn("/canon/cartography/CARTOGRAPHY.seed.yaml", TASKS["T018C_CARTOGRAPHY"]["outputs"])
        self.assertIn("/canon/cartography/STAGING.yaml", TASKS["T018C_CARTOGRAPHY"]["outputs"])
        self.assertEqual(TASKS["T022C_CARTOGRAPHY_SNAPSHOT"]["depends_on"], ["T018C_CARTOGRAPHY"])
        self.assertEqual(TASKS["T022C_CARTOGRAPHY_SNAPSHOT"]["outputs"], ["/canon/snapshots/CARTOGRAPHY.WAVE_00.yaml"])
        self.assertLessEqual({"T018C_CARTOGRAPHY", "T022C_CARTOGRAPHY_SNAPSHOT"}, set(GATES["GATE_CANON"]["requires"]))

    def test_t018c_nao_depende_do_proprio_gate(self):
        self.assertNotIn("GATE_CANON", TASKS["T018C_CARTOGRAPHY"]["depends_on"])
        self.assertNotIn("GATE_CANON", TASKS["T022C_CARTOGRAPHY_SNAPSHOT"]["depends_on"])

    def test_tarefas_mecanicas_tem_tool(self):
        self.assertIn("--materialize", TASKS["T018C_CARTOGRAPHY"]["tool"])
        for tid, t in TASKS.items():
            if tid.endswith("_CARTOGRAPHY_SNAPSHOT"):
                self.assertIn("--snapshot-auto", t["tool"], tid)

    def test_snapshot_por_wave_depois_do_canon_update(self):
        waves = GRAPH["spec"]["tasks"]
        snaps = [t for t in waves if t["id"].endswith("Y_CARTOGRAPHY_SNAPSHOT")]
        self.assertEqual(len(snaps), 3)
        for wi, t in enumerate(snaps, 1):
            self.assertEqual(t["depends_on"], [f"T2{wi:02d}_CANON_UPDATE"])
            self.assertEqual(t["outputs"], [f"/canon/snapshots/CARTOGRAPHY.WAVE_{wi:02d}.yaml"])
            self.assertIn(t["id"], GATES[f"GATE_WAVE_{wi}"]["requires"])

    def test_tres_familias_de_validador_em_gates_existentes(self):
        self.assertIn("V_CARTO_CANON", GATES["GATE_CANON"]["custom_validators"])
        for wi in (1, 2, 3):
            self.assertIn(f"V_CARTO_WAVE_{wi}", GATES[f"GATE_WAVE_{wi}"]["custom_validators"])
        self.assertIn("V_CARTO_FINAL", GATES["GATE_FULL_MANUSCRIPT"]["custom_validators"])
        self.assertNotIn("GATE_CARTOGRAPHY", GATES)             # nenhum gate novo

    def test_comandos_dos_validadores(self):
        self.assertEqual(VALIDATORS["V_CARTO_CANON"]["command"], "python scripts/check_cartography.py --runtime . --mode canon")
        w2 = VALIDATORS["V_CARTO_WAVE_2"]["command"]
        self.assertIn("--mode wave --through-chapter 4", w2)                        # onda 2 = capítulos [3, 4]
        self.assertIn("--baseline canon/snapshots/CARTOGRAPHY.WAVE_01.yaml", w2)   # baseline = wave anterior
        self.assertIn("CARTOGRAPHY.WAVE_03.yaml", VALIDATORS["V_CARTO_FINAL"]["command"])

    def test_briefs_recebem_a_instrucao_do_pack(self):
        for ch in range(1, 7):
            t = TASKS[f"T1{ch:02d}_BRIEF_CHAPTER"]
            self.assertIn("/canon/cartography/CARTOGRAPHY.seed.yaml", t["inputs"])
            note = t["parameters"]["cartography"]
            self.assertIn(f"--pack --chapter {ch}", note)
            self.assertIn(f"CHAPTER_{ch:02d}_PACK.yaml", note)
            self.assertNotRegex(note.lower(), r"sa[ií]da verdadeira")

    def test_o_dono_do_canon_e_unico(self):
        owners = {t["owner"] for tid, t in TASKS.items() if "CARTOGRAPHY" in tid}
        self.assertEqual(owners, {"CANON_GUARDIAN"})

    def test_grafo_valida_sem_erros(self):
        self.assertEqual(lb.validate_graph(GRAPH, REPO) if lb.validate_graph.__code__.co_argcount == 2 else [], [])

    def test_ledger_e_cartografia_juntos(self):
        with tempfile.TemporaryDirectory() as d:
            book = Path(d) / "book"
            shutil.copytree(FIXTURE_BOOK, book)
            spec = yaml.safe_load((book / "BOOK_SPEC.yaml").read_text(encoding="utf-8"))
            spec["spec"]["features"]["causal_ledger"] = {"enabled": True}
            (book / "BOOK_SPEC.yaml").write_text(yaml.safe_dump(spec, allow_unicode=True, sort_keys=False), encoding="utf-8")
            g = lb.build_standard_graph(book)
            ids = {t["id"] for t in g["spec"]["tasks"]}
            self.assertLessEqual({"T021_LEDGER_SNAPSHOT", "T022C_CARTOGRAPHY_SNAPSHOT", "T201Y_CARTOGRAPHY_SNAPSHOT", "T201Z_LEDGER_SNAPSHOT"}, ids)
            self.assertEqual(len(ids), len(g["spec"]["tasks"]))          # ids únicos


class ComposeEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.runtime = Path(cls._tmp.name) / "cartography_mvp"
        run = subprocess.run([sys.executable, str(LIVINGBOOK), "compose", "--book", str(FIXTURE_BOOK), "--runtime", str(cls.runtime)],
                             cwd=REPO, capture_output=True, text=True)
        cls.compose = run

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def sh(self, *args):
        return subprocess.run([sys.executable, *args], cwd=self.runtime, capture_output=True, text=True, encoding="utf-8",
                              env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})

    def test_compose_e_smoke(self):
        self.assertEqual(self.compose.returncode, 0, self.compose.stdout + self.compose.stderr)
        smoke = subprocess.run([sys.executable, str(LIVINGBOOK), "smoke-test", "--runtime", str(self.runtime)], cwd=REPO, capture_output=True, text=True)
        self.assertEqual(smoke.returncode, 0, smoke.stdout + smoke.stderr)
        self.assertIn("SMOKE TEST OK", smoke.stdout)

    def test_scripts_da_cartografia_acompanham_o_runtime(self):
        for name in ("check_cartography.py", "cartography_graph.py", "cartography_chase.py", "cartography_maps.py", "cartography_runtime.py"):
            self.assertTrue((self.runtime / "scripts" / name).is_file(), name)

    def test_seeds_da_obra_vao_junto_com_o_livro(self):
        self.assertTrue((self.runtime / "book" / "cartography" / "seeds" / "CARTOGRAPHY.seed.yaml").is_file())

    def test_t29_gate_canon_executa_v_carto_canon(self):
        m = self.sh("scripts/check_cartography.py", "--runtime", ".", "--materialize")
        self.assertEqual(m.returncode, 0, m.stdout + m.stderr)
        self.assertEqual(self.sh("scripts/check_cartography.py", "--runtime", ".", "--mode", "canon").returncode, 0)
        graph = yaml.safe_load((self.runtime / "TASK_GRAPH.yaml").read_text(encoding="utf-8"))
        for tid in graph["spec"]["gates"]["GATE_CANON"]["requires"]:
            self.sh("scripts/runtime_taskgraph.py", "mark", tid, "APPROVED")
        g = self.sh("scripts/runtime_taskgraph.py", "validate-gate", "GATE_CANON")
        self.assertEqual(g.returncode, 0, g.stdout + g.stderr)
        self.assertIn("V_CARTO_CANON: PASS", g.stdout)

    def test_gate_reprova_quando_o_canon_nao_foi_materializado(self):
        with tempfile.TemporaryDirectory() as d:
            rt = Path(d) / "rt"
            shutil.copytree(self.runtime, rt, ignore=shutil.ignore_patterns("cartography") if False else None)
            shutil.rmtree(rt / "canon" / "cartography", ignore_errors=True)
            r = subprocess.run([sys.executable, "scripts/check_cartography.py", "--runtime", ".", "--mode", "canon"], cwd=rt,
                               capture_output=True, text=True, encoding="utf-8", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
            self.assertEqual(r.returncode, 1)
            self.assertIn("CARTOGRAPHY_CANON_MISSING", r.stdout)


if __name__ == "__main__":
    unittest.main()
