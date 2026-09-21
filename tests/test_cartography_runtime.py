"""Testes de `cartography_runtime.py` (Slice 5 do SDD da cartografia, seções 26.3, 27.1, 29.1; T27, T29).
Runtime montado a partir do livro-fixture `tests/fixtures/books/cartography_mvp` (mundo neutro de Valdoro).

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_cartography_runtime -v
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

import cartography_runtime as rt  # noqa: E402
import check_cartography as cc  # noqa: E402

BOOK_CARTO = REPO / "tests" / "fixtures" / "books" / "cartography_mvp" / "cartography"
SCRIPT = REPO / "engine" / "scripts" / "check_cartography.py"


def make_runtime(tmp, materialize=True):
    root = Path(tmp) / "rt"
    (root / "book").mkdir(parents=True)
    shutil.copytree(BOOK_CARTO, root / "book" / "cartography")
    if materialize:
        rt.materialize(root)
    return root


def write_staging(root, doc):
    (root / "canon" / "cartography" / "STAGING.yaml").write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")


def cats(findings, prefix):
    return [f for f in findings if f["category"].startswith(prefix)]


def blocking(findings):
    return [f for f in findings if f["severity"] in cc.BLOCKING]


def stg(i, actor, loc, at, chapter=3, status="REALIZED", **kw):
    return {"id": i, "status": status, "actor": actor, "location": loc, "at": at, "chapter": chapter, "scene": f"SC-{chapter:02d}-01", **kw}


class Materialize(unittest.TestCase):
    def test_copia_seeds_fontes_e_cria_staging_vazio(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d, materialize=False)
            r = rt.materialize(root)
            self.assertEqual(r["status"], "MATERIALIZED")
            canon = root / "canon" / "cartography"
            self.assertTrue((canon / "CARTOGRAPHY.seed.yaml").is_file())
            self.assertTrue((canon / "sources" / "SOURCES.yaml").is_file())
            doc = yaml.safe_load((canon / "STAGING.yaml").read_text(encoding="utf-8"))
            self.assertEqual((doc["staging"], doc["movements"], doc["chases"]), ([], [], []))

    def test_caminho_das_fontes_e_reescrito_e_valida(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            manifest = (root / "canon" / "cartography" / "CARTOGRAPHY.seed.yaml").read_text(encoding="utf-8")
            self.assertIn("sources: sources/SOURCES.yaml", manifest)
            self.assertEqual(blocking(rt.run_mode(root, "canon")), [])

    def test_nunca_sobrescreve_canon_existente(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            mark = root / "canon" / "cartography" / "LOCATIONS.seed.yaml"
            mark.write_text(mark.read_text(encoding="utf-8") + "\n# editado por mutação\n", encoding="utf-8")
            self.assertEqual(rt.materialize(root)["status"], "ALREADY_MATERIALIZED")
            self.assertIn("# editado por mutação", mark.read_text(encoding="utf-8"))

    def test_sem_seeds_na_obra(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(rt.materialize(Path(d))["status"], "NO_SEEDS")


class Modes(unittest.TestCase):
    def test_canon_ausente_bloqueia_o_gate(self):
        with tempfile.TemporaryDirectory() as d:
            f = rt.run_mode(make_runtime(d, materialize=False), "canon")
            self.assertEqual([(x["category"], x["severity"]) for x in f], [("CARTOGRAPHY_CANON_MISSING", "BLOCKER")])

    def test_canon_limpo_passa(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(blocking(rt.run_mode(make_runtime(d), "canon")), [])

    def test_canon_protege_a_autoria_pelo_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            (root / "canon" / "CAUSAL_LEDGER.yaml").write_text(yaml.safe_dump({"characters": [], "events": [
                {"id": "EV-1", "chapter": 2, "knowledge_delta": [{"knower": "READER", "learns": ["CART:AUTHOR:CHR-K"]}]}]}), encoding="utf-8")
            self.assertTrue(cats(rt.run_mode(root, "canon"), "MY-08"))

    def test_wave_ignora_planned_e_capitulos_posteriores(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            write_staging(root, {"staging": [
                stg("S1", "CHR-K", "TS-CEN-ORG", "D001T10:00", 3), stg("S2", "CHR-K", "TS-CEN-CAP", "D001T10:01", 3, status="PLANNED"),
                stg("S3", "CHR-K", "TS-CEN-ORG", "D002T10:00", 5), stg("S4", "CHR-K", "TS-URB-CEM", "D002T10:01", 5)],
                "movements": [{"id": "M1", "status": "PLANNED", "actor": "CHR-K", "from_staging": "S1", "to_staging": "S2", "mode": "WALK"},
                              {"id": "M2", "status": "REALIZED", "actor": "CHR-K", "from_staging": "S3", "to_staging": "S4", "mode": "WALK"}]})
            self.assertEqual(cats(rt.run_mode(root, "wave", through_chapter=3), "TR-"), [])
            self.assertTrue(cats(rt.run_mode(root, "wave", through_chapter=5), "TR-01"))

    def test_wave_reprova_teletransporte_realizado(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            write_staging(root, {"staging": [stg("S1", "CHR-K", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-K", "TS-URB-MOI", "D001T10:01")],
                                 "movements": [{"id": "M1", "status": "REALIZED", "actor": "CHR-K", "from_staging": "S1", "to_staging": "S2", "mode": "WALK"}]})
            f = rt.run_mode(root, "wave", through_chapter=3)
            self.assertTrue([x for x in f if x["category"].startswith("TR-01") and x["severity"] == "HIGH"])

    def test_wave_conhecimento_do_ator_vem_do_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            write_staging(root, {"staging": [stg("S1", "CHR-X", "TS-CEN-CAP", "D001T10:00"), stg("S2", "CHR-X", "TS-URB-CEM", "D001T12:00")],
                                 "movements": [{"id": "M1", "status": "REALIZED", "actor": "CHR-X", "from_staging": "S1", "to_staging": "S2",
                                                "mode": "CRAWL", "route": ["EDG-P-001", "EDG-S-001", "EDG-S-002", "EDG-P-002"]}]})
            self.assertTrue(cats(rt.run_mode(root, "wave", through_chapter=3), "KN-01"))
            (root / "canon" / "CAUSAL_LEDGER.yaml").write_text(yaml.safe_dump({"characters": [], "events": [
                {"id": "EV-1", "chapter": 1, "knowledge_delta": [{"knower": "CHR-X", "learns": ["EDG-P-001", "EDG-S-001", "EDG-S-002", "EDG-P-002"]}]}]}), encoding="utf-8")
            self.assertEqual(cats(rt.run_mode(root, "wave", through_chapter=3), "KN-01"), [])

    def test_final_kn02_sobre_o_manuscrito(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            (root / "manuscript" / "approved").mkdir(parents=True)
            (root / "manuscript" / "approved" / "chapter_03.md").write_text("Ela viu a Cripta Selada.", encoding="utf-8")
            (root / "manuscript" / "approved" / "chapter_08.md").write_text("A Cripta Selada estava aberta.", encoding="utf-8")
            f = cats(rt.run_mode(root, "final"), "KN-02")
            self.assertEqual([x["chapter"] for x in f], [3])

    def test_final_sem_manuscrito_e_info(self):
        with tempfile.TemporaryDirectory() as d:
            f = cats(rt.run_mode(make_runtime(d), "final"), "MANUSCRIPT_NOT_FOUND")
            self.assertEqual([x["severity"] for x in f], ["INFO"])


class Snapshots(unittest.TestCase):
    def test_numeracao_automatica(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            names = [rt.snapshot_auto(root).name for _ in range(3)]
            self.assertEqual(names, [f"CARTOGRAPHY.WAVE_{i:02d}.yaml" for i in range(3)])

    def test_congela_capitulo_realizado_mais_alto(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            write_staging(root, {"staging": [stg("S1", "CHR-K", "TS-CEN-ORG", "D001T10:00", 2), stg("S2", "CHR-K", "TS-CEN-ORG", "D001T11:00", 4, status="PLANNED")]})
            snap = yaml.safe_load(rt.snapshot_auto(root).read_text(encoding="utf-8"))
            self.assertEqual(snap["through_chapter"], 2)
            self.assertEqual(snap["locations"]["TS-CEN-CAP"]["canonical_name"], "Capela do Vau")

    def _model(self):
        return cc.load_model(REPO / "tests" / "fixtures" / "cartography" / "canon")

    def test_cn06_renome_sem_mutacao(self):
        m = self._model()
        snap = rt.build_snapshot(m)
        m2 = copy.deepcopy(m)
        next(l for l in m2["locations"] if l["id"] == "TS-CEN-CAP")["canonical_name"] = "Capela Nova"
        f = rt.check_baseline(m2, snap)
        self.assertEqual([(x["category"], x["severity"]) for x in f], [("CN-06 RENAME_WITHOUT_PROPOSAL", "HIGH")])

    def test_cn06_renome_por_mutacao_passa(self):
        m = self._model()
        snap = rt.build_snapshot(m)
        m2 = copy.deepcopy(m)
        next(l for l in m2["locations"] if l["id"] == "TS-CEN-CAP")["canonical_name"] = "Capela Nova"
        m2["manifest"]["mutations"] = [{"id": "MUT-9", "chapter": 4, "target": "TS-CEN-CAP", "field": "canonical_name"}]
        self.assertEqual(rt.check_baseline(m2, snap), [])

    def test_cn07_mutacao_retroativa(self):
        m = self._model()
        snap = {**rt.build_snapshot(m), "through_chapter": 5}
        m2 = copy.deepcopy(m)
        m2["manifest"]["mutations"] = [{"id": "MUT-1", "chapter": 3, "proposal_ref": "P", "cause": "EV-1"}]
        f = rt.check_baseline(m2, snap)
        self.assertEqual([(x["category"], x["severity"]) for x in f], [("CN-07 RETROACTIVE_MUTATION", "BLOCKER")])

    def test_cn07_mutacao_futura_ou_ja_conhecida_passa(self):
        m = self._model()
        snap = {**rt.build_snapshot(m), "through_chapter": 5}
        m2 = copy.deepcopy(m)
        m2["manifest"]["mutations"] = [{"id": "MUT-1", "chapter": 6, "proposal_ref": "P", "cause": "EV-1"}]
        self.assertEqual(rt.check_baseline(m2, snap), [])
        snap["mutations"] = ["MUT-1"]
        m2["manifest"]["mutations"][0]["chapter"] = 2
        self.assertEqual(rt.check_baseline(m2, snap), [])

    def test_baseline_ausente_e_medium(self):
        with tempfile.TemporaryDirectory() as d:
            f = cats(rt.run_mode(make_runtime(d), "wave", 3, baseline="canon/snapshots/NAO_EXISTE.yaml"), "BASELINE_MISSING")
            self.assertEqual([x["severity"] for x in f], ["MEDIUM"])


class Pack(unittest.TestCase):
    def pack(self, actor, loc="TS-CEN-CAP", engine_view=False, **stg_kw):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            doc = {"staging": [stg("S1", actor, loc, "D001T23:14", 3, status="PLANNED", **stg_kw)], "movements": [], "chases": []}
            model = cc.load_model(root / "canon" / "cartography")
            return rt.build_pack(model, doc, 3, engine_view=engine_view)

    def test_estrutura_e_conteudo_basico(self):
        e = self.pack("CHR-X", conditions={"lighting": "NIGHT_DARK", "weather": "RAIN"})["scenes"][0]
        self.assertEqual(e["current_location"]["id"], "TS-CEN-CAP")
        self.assertEqual(e["conditions"], {"lighting": "NIGHT_DARK", "weather": "RAIN"})
        self.assertIn("RAIN ×1.10 em deslocamento", e["weather_effects"])
        self.assertTrue(any("30 m" in w for w in e["weather_effects"]))
        self.assertEqual(e["mystery_notice"], rt.MYSTERY_NOTICE)
        self.assertIsNone(e["engine_notes"])

    def test_adjacentes_so_por_arestas_publicas_com_tempo(self):
        e = self.pack("CHR-X")["scenes"][0]
        self.assertEqual([a["id"] for a in e["adjacent_locations"]], ["TS-CEN-ORG"])
        self.assertRegex(e["adjacent_locations"][0]["walk_expected"], r"^\d+(\.\d+)?–\d+(\.\d+)? min$")
        self.assertEqual(e["visible_exits"], ["EDG-U-001"])

    def test_passagem_oculta_desconhecida_e_so_contagem(self):
        e = self.pack("CHR-X")["scenes"][0]
        self.assertEqual(e["hidden_exits_unknown_to_pov"], 1)
        self.assertEqual(e["hidden_exits_known_by_pov"], [])
        # o id só aparece onde o SDD 22.6 manda: o que o LEITOR viu impresso (ironia dramática), nunca como saída do POV
        rest = {k: v for k, v in e.items() if k != "reader_knows_but_pov_does_not"}
        self.assertNotIn("EDG-P-001", json.dumps(rest))

    def test_passagem_oculta_conhecida_aparece(self):
        e = self.pack("CHR-K")["scenes"][0]
        self.assertEqual([h["edge"] for h in e["hidden_exits_known_by_pov"]], ["EDG-P-001"])
        self.assertEqual(e["hidden_exits_unknown_to_pov"], 0)
        self.assertEqual(e["underground_access"]["known_to_pov"], ["EDG-P-001"])

    def test_engine_view_libera_os_ids(self):
        e = self.pack("CHR-X", engine_view=True)["scenes"][0]
        self.assertEqual(e["engine_notes"]["hidden_exits_unknown_to_pov"], ["EDG-P-001"])

    def test_estado_do_leitor_e_ironia(self):
        e = self.pack("CHR-X")["scenes"][0]
        self.assertEqual(e["reader_state"]["TS-CEN-CAP"], "SEEN_ON_MAP")
        self.assertIn("EDG-P-001", e["reader_knows_but_pov_does_not"])     # o leitor viu no mapa; o POV não sabe
        self.assertNotIn("EDG-P-001", self.pack("CHR-K")["scenes"][0]["reader_knows_but_pov_does_not"])

    def test_proibicoes_e_restricoes_de_canon(self):
        e = self.pack("CHR-X")["scenes"][0]
        self.assertEqual({f["code"] for f in e["forbidden"]}, {"KN-01", "KN-02", "VS-01"})
        self.assertTrue(any("Rio Manso" in c and "Ponte Velha" in c for c in e["canon_constraints"]))
        self.assertTrue(any("único esconderijo" in c for c in e["canon_constraints"]))

    def test_vigilancia_e_cobertura_nunca_inventadas(self):
        e = self.pack("CHR-X")["scenes"][0]
        self.assertEqual(e["surveillance"], {"at_location": "UNKNOWN"})
        self.assertEqual(e["cover"], {"at_location": "UNSPECIFIED"})

    def test_lugar_inexistente_nao_derruba_o_pack(self):
        self.assertIn("error", self.pack("CHR-X", loc="TS-NAO-EXISTE")["scenes"][0])

    def test_filtro_por_cena_e_capitulo(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            doc = {"staging": [stg("S1", "CHR-X", "TS-CEN-CAP", "D001T10:00", 3), stg("S2", "CHR-X", "TS-CEN-ORG", "D001T11:00", 4)]}
            model = cc.load_model(root / "canon" / "cartography")
            self.assertEqual([s["staging"] for s in rt.build_pack(model, doc, 3)["scenes"]], ["S1"])
            self.assertEqual(rt.build_pack(model, doc, 3, scene="SC-99")["scenes"], [])

    def test_pack_e_deterministico(self):
        self.assertEqual(json.dumps(self.pack("CHR-X"), sort_keys=True), json.dumps(self.pack("CHR-X"), sort_keys=True))

    def test_pack_nunca_produz_saida_verdadeira(self):
        self.assertIsNone(cc.TRUE_EXIT_RE.search(json.dumps(self.pack("CHR-K"), ensure_ascii=False)))

    def test_becos_sem_saida_proximos(self):
        e = self.pack("CHR-X", loc="TS-CEN-ORG")["scenes"][0]
        self.assertIsInstance(e["dead_ends"], list)

    def test_write_pack_grava_o_arquivo(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            write_staging(root, {"staging": [stg("S1", "CHR-X", "TS-CEN-CAP", "D001T10:00", 7, status="PLANNED")]})
            out = rt.write_pack(root, 7)
            self.assertEqual(out, root / "briefs" / "cartography" / "CHAPTER_07_PACK.yaml")
            self.assertEqual(yaml.safe_load(out.read_text(encoding="utf-8"))["scenes"][0]["staging"], "S1")


class Cli(unittest.TestCase):
    def run_cli(self, root, *args):
        p = subprocess.run([sys.executable, str(SCRIPT), "--runtime", str(root), *args], capture_output=True, text=True, encoding="utf-8",
                           env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
        return p.returncode, p.stdout, p.stderr

    def test_materialize_canon_snapshot_pack(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d, materialize=False)
            self.assertEqual(self.run_cli(root, "--materialize")[0], 0)
            self.assertEqual(self.run_cli(root, "--mode", "canon")[0], 0)
            code, out, _ = self.run_cli(root, "--snapshot-auto")
            self.assertEqual(code, 0)
            self.assertTrue((root / "canon" / "snapshots" / "CARTOGRAPHY.WAVE_00.yaml").is_file())
            write_staging(root, {"staging": [stg("S1", "CHR-X", "TS-CEN-CAP", "D001T10:00", 2, status="PLANNED")]})
            self.assertEqual(self.run_cli(root, "--pack", "--chapter", "2")[0], 0)
            self.assertTrue((root / "briefs" / "cartography" / "CHAPTER_02_PACK.yaml").is_file())

    def test_pack_exige_capitulo(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_cli(make_runtime(d), "--pack")[0], 2)

    def test_modo_reprova_com_exit_1(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_runtime(d)
            write_staging(root, {"staging": [stg("S1", "CHR-K", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-K", "TS-URB-MOI", "D001T10:01")],
                                 "movements": [{"id": "M1", "status": "REALIZED", "actor": "CHR-K", "from_staging": "S1", "to_staging": "S2"}]})
            self.assertEqual(self.run_cli(root, "--mode", "wave", "--through-chapter", "3")[0], 1)

    def test_canon_ausente_exit_1(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_cli(make_runtime(d, materialize=False), "--mode", "canon")[0], 1)


if __name__ == "__main__":
    unittest.main()
