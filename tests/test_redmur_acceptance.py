"""Condição de sucesso da missão (§42 / SDD Apêndice C): as 9 perguntas, respondidas pelo sistema final sobre os dados
reais de SEM ROSTO. Uma asserção compacta por pergunta; a cobertura fina está em test_redmur_surface/chase/maps.

Também valida o exemplo de staging de `books/sem-rosto/cartography/examples/` (ilustrativo: NÃO é capítulo do livro).

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_redmur_acceptance -v
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import cartography_chase as ch  # noqa: E402
import cartography_graph as cg  # noqa: E402
import cartography_maps as mp  # noqa: E402
import check_cartography as cc  # noqa: E402

CART = REPO / "books" / "sem-rosto" / "cartography"
M = cc.load_model(CART / "seeds")
TUNNEL = ["EDG-P-001", "EDG-S-001", "EDG-S-002", "EDG-P-002"]


def m():
    return copy.deepcopy(M)


class MissionQuestions(unittest.TestCase):
    def test_q1_rotas_que_a_protagonista_conhece_para_sair_do_cemiterio(self):
        actor = cg.escape_routes(m(), "RM-URB-OPC", ctx=cg.make_ctx(view="ACTOR", actor="CHR-P", chapter=1))
        engine = cg.escape_routes(m(), "RM-URB-OPC", ctx=cg.make_ctx())
        self.assertTrue(actor)
        self.assertFalse(any("EDG-P-002" in r["edges"] for r in actor))          # o túnel não é dela
        self.assertTrue(any("EDG-P-002" in r["edges"] for r in engine))          # o motor o vê

    def test_q2_tempo_de_rowan_cottage_ao_shepherds_bothy(self):
        t = cg.travel_times(m(), "RM-URB-ROW", "RM-URB-SBO", ctx=cg.make_ctx())
        self.assertGreater(t["length_min_m"], 1900)
        self.assertTrue(t["min_s"] < t["expected_s"] < t["max_reasonable_s"])
        self.assertTrue(12 * 60 <= t["min_s"] <= 18 * 60 and 25 * 60 <= t["expected_s"] <= 35 * 60)
        night = cg.travel_times(m(), "RM-URB-ROW", "RM-URB-SBO", ctx=cg.make_ctx(lighting="NIGHT_DARK"))
        self.assertGreater(night["expected_s"], t["expected_s"])

    def test_q3_passagem_subterranea_entre_a_capela_e_o_cemiterio(self):
        r = cg.route(m(), "RM-CEN-CHP", "RM-URB-OPC", ctx=cg.make_ctx())
        self.assertEqual(r["edges"], TUNNEL)
        actor = cg.route(m(), "RM-CEN-CHP", "RM-URB-OPC", ctx=cg.make_ctx(view="ACTOR", actor="CHR-X", chapter=1))
        self.assertFalse(set(TUNNEL) & set(actor.get("edges") or []))            # quem não a conhece usa a superfície

    def test_q4_ver_alguem_atravessar_a_ponte(self):
        day = ch.visible_from(m(), "RM-URB-PMP", "RM-URB-BBR", {})
        night = ch.visible_from(m(), "RM-URB-PMP", "RM-URB-BBR", {"lighting": "NIGHT_DARK"})
        who = ch.visible_from(m(), "RM-URB-PMP", "RM-URB-BBR", {"recognize": True})
        self.assertEqual((day["result"], night["result"]), ("UNDETERMINED", "NOT_VISIBLE"))
        self.assertEqual(who["recognition"], "RECOGNITION_OUT_OF_SCOPE")

    def test_q5_esconderijo_sem_area_vigiada(self):
        r = ch.accessible_hideouts(m(), "RM-CEN-SMC")[0]
        self.assertEqual((r["hideout"], r["surveillance"], r["restricted_edges"]), ("HID-RCH", "UNDETERMINED_SURVEILLANCE", []))
        self.assertTrue(r["surveillance_to_decide"])                             # lista o que a autora precisa decidir

    def test_q6_perseguicao_fisicamente_possivel(self):
        spec = {"id": "CHS-Q6", "chapter": 3, "lighting": "NIGHT_DARK", "initial_gap_m": 300, "initial_visibility": "UNKNOWN",
                "target": {"actor": "CHR-X", "start": "RM-CEN-RSP", "end": "RM-URB-OPC"},
                "pursuer": {"actor": "CHR-Y", "start": "RM-CEN-SMC"}}
        r = ch.analyze_chase(m(), spec)
        self.assertTrue(r["target"]["windows"] and r["pursuer"]["windows"])      # janelas por nó, não simulação
        b = ch.bottlenecks(m(), {"view": "ACTOR", "actor": "CHR-P"}, layers={"URBAN"})   # personagem comum, superfície
        self.assertIn("RM-URB-BBR", b["articulation_points"])                    # Burn Bridge é gargalo

    def test_q7_sair_do_red_stag_as_2314_e_chegar_ao_cemiterio_as_2318(self):
        doc = {"staging": [{"id": "S1", "actor": "CHR-P", "location": "RM-CEN-RSP", "at": "D014T23:14", "chapter": 7},
                           {"id": "S2", "actor": "CHR-P", "location": "RM-URB-OPC", "at": "D014T23:18", "chapter": 7}],
               "movements": [{"id": "M1", "actor": "CHR-P", "from_staging": "S1", "to_staging": "S2", "mode": "WALK"}]}
        f = cg.validate_staging(m(), doc)["findings"]
        self.assertTrue([x for x in f if x["category"].startswith("TR-01") and x["severity"] == "HIGH"])
        doc["movements"][0]["mode"] = "RUN"
        f = cg.validate_staging(m(), doc)["findings"]
        self.assertTrue([x for x in f if x["category"].startswith(("TR-01", "TR-03")) and x["severity"] == "HIGH"])

    def test_q8_estradas_que_parecem_sair_de_redmur(self):
        r = mp.exits_query(m())
        self.assertEqual(r["count"], 10)
        by = {e["id"]: e for e in r["exits"]}
        self.assertIn("OFFICIAL_EXIT", by["EXT-01"]["exit_classes"])            # South Gate Road: "Entrada Principal"
        self.assertIn("CLOSED_EXIT", by["EXT-02"]["exit_classes"])              # East Road: fechada é alegação
        self.assertIn("DISPUTED_EXIT", by["EXT-03"]["exit_classes"])            # Estrada 13

    def test_q9_qual_delas_e_realmente_a_saida(self):
        r = mp.exit_truth(m())
        self.assertEqual((r["notice"], r["status"]), ("EXIT_TRUTH_NOT_IN_CARTOGRAPHY", "POINTERS_ONLY"))
        self.assertTrue(all(x["truth_ref"] is None for x in r["exits"]))
        for e in mp.exits_query(m())["exits"]:
            self.assertEqual(e["physical"]["beyond_frame"], "OFF_MAP")
        self.assertFalse(set(cc.EXIT_CLASSES) & {"TRUE_EXIT", "REAL_EXIT"})


class WorkedExample(unittest.TestCase):
    """`examples/STAGING.example.yaml`: cenas ilustrativas que mostram o formato e o que o motor diz. Não são capítulos."""

    PATH = CART / "examples" / "STAGING.example.yaml"

    def result(self):
        return ch.validate_scene(m(), yaml.safe_load(self.PATH.read_text(encoding="utf-8")))

    def test_o_exemplo_existe_e_se_declara_ilustrativo(self):
        text = self.PATH.read_text(encoding="utf-8")
        self.assertIn("ILUSTRATIVO", text)
        self.assertIn("não é canon", text)

    def test_o_exemplo_e_fisicamente_coerente(self):
        f = self.result()["findings"]
        self.assertEqual([x for x in f if x["severity"] in cc.BLOCKING], [])

    def test_o_exemplo_mostra_o_trajeto_apertado_como_warning(self):
        f = [x for x in self.result()["findings"] if x["category"].startswith("TR-")]
        self.assertEqual([(x["category"][:5], x["severity"], x["evidence"]) for x in f], [("TR-07", "MEDIUM", "MOV-EX-03")])

    def test_o_exemplo_so_usa_ids_que_existem_e_estados_planned(self):
        doc = yaml.safe_load(self.PATH.read_text(encoding="utf-8"))
        ids = {l["id"] for l in M["locations"]}
        self.assertTrue(all(s["location"] in ids for s in doc["staging"]))
        self.assertTrue(all(s["status"] == "PLANNED" for s in doc["staging"]))    # nada do exemplo vira REALIZED sem a autora


if __name__ == "__main__":
    unittest.main()
