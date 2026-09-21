"""Testes de `cartography_maps.py` (Slice 4 do SDD da cartografia, seções 19–25, 29.3 e 35: T09, T10, T22, T33, T36).
Fixture neutra `tests/fixtures/cartography/canon/`.

Mundo da fixture: duas saídas (EXT-01 oficial com truth_ref GT-EXIT-1; EXT-02 disputada, liberada só no cap. 5),
Cripta Selada (subsolo, `connectivity: UNDECLARED`, liberada no cap. 8, fora do mapa impresso), mapa oficial
MAP-OFF-01 (autor INST-GUARDA) com relações OMITS/PHANTOM/FALSIFIED_STATUS/RENAMED/ACCURATE.

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_cartography_maps -v
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import cartography_graph as cg  # noqa: E402
import cartography_maps as mp  # noqa: E402
import check_cartography as cc  # noqa: E402

SCRIPT = REPO / "engine" / "scripts" / "check_cartography.py"
FIXTURE = REPO / "tests" / "fixtures" / "cartography" / "canon"
_MODEL = cc.load_model(FIXTURE)


def model():
    return copy.deepcopy(_MODEL)


def cats(findings, prefix):
    return [f for f in findings if f["category"].startswith(prefix)]


def ledger(events=(), gts=None):
    return {"characters": [{"id": "CHR-K", "ground_truth": gts if gts is not None else
                            [{"id": "GT-EXIT-1", "reader_access": "NEVER", "truth": "CONTEUDO-SECRETO-DA-SAIDA"}]}],
            "events": list(events)}


def ev(i, chapter, knower, learns, **kw):
    return {"id": i, "chapter": chapter, "knowledge_delta": [{"knower": knower, "learns": learns}], **kw}


def art(m, aid):
    return next(a for a in m["artifacts"] if a["id"] == aid)


class ExitsQuery(unittest.TestCase):
    def test_devolve_classes_e_alegacoes_com_aviso_fixo(self):
        r = mp.exits_query(model())
        self.assertEqual(r["notice"], "EXIT_TRUTH_NOT_IN_CARTOGRAPHY")
        e1 = next(e for e in r["exits"] if e["id"] == "EXT-01")
        self.assertEqual(e1["exit_classes"], ["APPARENT_EXIT", "OFFICIAL_EXIT"])
        self.assertEqual(e1["claims"][0]["class"], "OFFICIAL_EXIT")
        self.assertEqual(e1["claims"][0]["epistemic_status"], "OFFICIAL_CLAIM")

    def test_alem_da_moldura_e_sempre_off_map(self):
        for e in mp.exits_query(model())["exits"]:
            self.assertEqual(e["physical"]["beyond_frame"], "OFF_MAP")
            self.assertEqual(e["physical"]["passable_to_frame"], "UNKNOWN")

    def test_posicao_do_portal_e_derivada_nao_digitada(self):
        e1 = next(e for e in mp.exits_query(model())["exits"] if e["id"] == "EXT-01")
        self.assertIsNotNone(e1["frame_position"])
        self.assertAlmostEqual(e1["frame_position"]["y"], -390.0, places=1)   # (40 − 79) px × 10 m/px

    def test_saida_por_digitalizar_marcada(self):
        e2 = next(e for e in mp.exits_query(model())["exits"] if e["id"] == "EXT-02")
        self.assertEqual(e2["frame_status"], "TO_DIGITIZE")
        self.assertIsNone(e2["frame_position"])

    def test_filtro_por_capitulo_respeita_first_allowed_reveal(self):
        ids = lambda ch: {e["id"] for e in mp.exits_query(model(), ch)["exits"]}  # noqa: E731
        self.assertEqual(ids(3), {"EXT-01"})
        self.assertEqual(ids(5), {"EXT-01", "EXT-02"})
        self.assertEqual(ids(None), {"EXT-01", "EXT-02"})

    def test_t09_nenhuma_consulta_produz_saida_verdadeira(self):
        m = model()
        g = cg.Graph(m)
        blobs = [mp.exits_query(m), mp.exit_truth(m, True, "GT-EXIT-1", ledger()), mp.reader_map(m, 9),
                 cg.reachable(m, "TS-CEN-ORG", "TS-FRM-S"), cg.route(m, "TS-CEN-ORG", "TS-FRM-S"),
                 cg.escape_routes(m, "TS-CEN-ORG")]
        for b in blobs:
            self.assertIsNone(cc.TRUE_EXIT_RE.search(json.dumps(b, ensure_ascii=False, default=str)))
        self.assertTrue(g.locs["TS-FRM-S"])

    def test_t10_true_exit_no_seed_reprova(self):
        m = model()
        m["exits"][0]["claims"].append({"class": "TRUE_EXIT", "text": "x", "source": "SRC-MAP-A", "epistemic_status": "FACT"})
        self.assertTrue(any(f["category"] == "EXIT_CLASS_INVALID" and f["severity"] == "BLOCKER" for f in cc.validate(m)))
        m2 = model()
        m2["exits"][0]["true_exit"] = "EXT-02"
        self.assertTrue(any(f["category"].startswith("MY-0") and f["severity"] == "BLOCKER" for f in cc.validate(m2)))


class ExitTruth(unittest.TestCase):
    def test_sem_autorizacao_so_ponteiros(self):
        r = mp.exit_truth(model(), ledger=ledger())
        self.assertEqual(r["status"], "POINTERS_ONLY")
        self.assertEqual({x["exit"]: x["truth_ref"] for x in r["exits"]}, {"EXT-01": "GT-EXIT-1", "EXT-02": None})
        self.assertTrue(all("pertinent" not in x for x in r["exits"]))

    def test_engine_view_com_gt_do_ledger_confirma_o_id(self):
        r = mp.exit_truth(model(), engine_view=True, authorized_by="GT-EXIT-1", ledger=ledger())
        self.assertEqual(r["status"], "AUTHORIZED_ID_CONFIRMATION")
        self.assertIs(next(x for x in r["exits"] if x["exit"] == "EXT-01")["pertinent"], True)

    def test_gt_diferente_nao_e_pertinente(self):
        lg = ledger(gts=[{"id": "GT-OUTRO", "reader_access": "NEVER"}])
        r = mp.exit_truth(model(), engine_view=True, authorized_by="GT-OUTRO", ledger=lg)
        self.assertIs(next(x for x in r["exits"] if x["exit"] == "EXT-01")["pertinent"], False)

    def test_authorized_by_sem_engine_view_recusa(self):
        r = mp.exit_truth(model(), engine_view=False, authorized_by="GT-EXIT-1", ledger=ledger())
        self.assertEqual(r["reason"], "ENGINE_VIEW_REQUIRED")
        self.assertTrue(all("pertinent" not in x for x in r["exits"]))

    def test_gt_inexistente_no_ledger_nao_autoriza(self):
        r = mp.exit_truth(model(), engine_view=True, authorized_by="GT-FANTASMA", ledger=ledger())
        self.assertEqual(r["reason"], "GT_NOT_FOUND_IN_LEDGER")
        self.assertEqual(r["status"], "POINTERS_ONLY")

    def test_conteudo_da_verdade_nunca_sai(self):
        for args in ((False, None), (True, "GT-EXIT-1")):
            blob = json.dumps(mp.exit_truth(model(), args[0], args[1], ledger()), ensure_ascii=False)
            self.assertNotIn("CONTEUDO-SECRETO", blob)


class PrintedAndReaderMap(unittest.TestCase):
    def test_o_que_esta_impresso(self):
        p = mp.printed_ids(model())
        self.assertIn("TS-SUB-POR", p["locations"])          # inset desenhado
        self.assertIn("TS-JCT-1", p["locations"])
        self.assertIn("EDG-S-001", p["edges"])
        self.assertIn("EDG-P-001", p["edges"])
        self.assertNotIn("TS-SUB-SEL", p["locations"])       # UNDECLARED: fora do mapa

    def test_t33_baseline_do_leitor_no_capitulo_zero(self):
        st = mp.reader_map(model(), 0)["states"]
        for i in ("TS-CEN-CAP", "TS-SUB-POR", "EDG-S-001", "EDG-P-002"):
            self.assertEqual(st[i], "SEEN_ON_MAP", i)
        self.assertNotIn("TS-SUB-SEL", st)
        self.assertIn("TS-SUB-SEL", mp.reader_map(model(), 0)["unseen"])

    def test_projecao_nao_carrega_estado_fisico_nem_verdade(self):
        blob = json.dumps(mp.reader_map(model(), 0))
        for k in ("secret_level", "HIDDEN", "status", "truth", "COLLAPSED"):
            self.assertNotIn(k, blob)

    def test_ledger_do_leitor_eleva_o_estado(self):
        lg = ledger([ev("EV-1", 4, "READER", ["CART:EXISTS:TS-SUB-SEL"]), ev("EV-2", 6, "READER", ["CART:VISITED:TS-SUB-SEL"])])
        self.assertEqual(mp.reader_map(model(), 3, lg)["states"].get("TS-SUB-SEL", "UNSEEN"), "UNSEEN")
        self.assertEqual(mp.reader_map(model(), 4, lg)["states"]["TS-SUB-SEL"], "MENTIONED")
        self.assertEqual(mp.reader_map(model(), 6, lg)["states"]["TS-SUB-SEL"], "VISITED")

    def test_aresta_aprendida_vira_connection_known_e_extremos_no_minimo_mencionados(self):
        st = mp.reader_map(model(), 2, ledger([ev("EV-1", 1, "READER", ["EDG-S-001"])]))["states"]
        self.assertEqual(st["EDG-S-001"], "CONNECTION_KNOWN")
        self.assertEqual(st["TS-SUB-POR"], "SEEN_ON_MAP")     # não rebaixa

    def test_staging_realizado_com_pov_marca_visitado(self):
        stg = [{"id": "S1", "location": "TS-URB-MOI", "status": "REALIZED", "pov": True, "chapter": 2}]
        self.assertEqual(mp.reader_map(model(), 2, None, stg)["states"]["TS-URB-MOI"], "VISITED")
        self.assertEqual(mp.reader_map(model(), 1, None, stg)["states"]["TS-URB-MOI"], "SEEN_ON_MAP")

    def test_conhecimento_de_outro_conhecedor_nao_vaza_para_o_leitor(self):
        st = mp.reader_map(model(), 9, ledger([ev("EV-1", 1, "CHR-K", ["CART:EXISTS:TS-SUB-SEL"])]))["states"]
        self.assertNotIn("TS-SUB-SEL", st)

    def test_ironia_dramatica_leitor_sabe_pov_nao(self):
        gap = lambda actor: {r["edge"] for r in mp.reader_knows_pov_does_not(model(), actor, 2)["reader_knows_but_pov_does_not"]}  # noqa: E731
        self.assertIn("EDG-S-001", gap("CHR-X"))
        self.assertNotIn("EDG-S-001", gap("CHR-K"))           # CHR-K conhece a passagem
        self.assertNotIn("EDG-U-001", gap("CHR-X"))           # estrada pública

    def test_ironia_some_quando_o_pov_aprende(self):
        lg = ledger([ev("EV-1", 1, "CHR-X", ["EDG-S-001"])])
        gap = {r["edge"] for r in mp.reader_knows_pov_does_not(model(), "CHR-X", 2, lg)["reader_knows_but_pov_does_not"]}
        self.assertNotIn("EDG-S-001", gap)

    def test_mutacao_faz_mapa_impresso_mentir(self):
        m = model()
        m["manifest"]["mutations"] = [{"id": "MUT-1", "chapter": 5, "proposal_ref": "P", "cause": "EV-9",
                                       "effects": [{"edge": "EDG-U-003", "previous_state": "OPEN", "new_state": "COLLAPSED"}]}]
        self.assertEqual(mp.printed_divergences(m, 4), [])
        f = mp.printed_divergences(m, 6)
        self.assertEqual([(x["category"], x["severity"], x["evidence"]) for x in f],
                         [("MUTATION_DIVERGES_FROM_PRINTED_MAP", "INFO", "EDG-U-003")])

    def test_aresta_inferida_nao_e_impressa(self):
        m = model()
        m["edges"][0] = {**m["edges"][0], "printed": False}
        self.assertNotIn(m["edges"][0]["id"], mp.printed_ids(m)["edges"])

    def test_destino_fora_da_moldura_com_alegacao_impressa_conta(self):
        m = model()
        m["locations"].append({"id": "TS-OFF-X", "canonical_name": "Longe", "type": "OFF_MAP_DESTINATION", "layer": "REGIONAL",
                               "geometry": "POINT", "claims": [{"text": "Para Longe", "source": "SRC-MAP-A"}]})
        self.assertIn("TS-OFF-X", mp.printed_ids(m)["locations"])


class ReaderLeak(unittest.TestCase):
    PROSE = "Ela desceu ao fundo da Cripta Selada, onde nada se movia."

    def test_kn02_menciona_antes_da_hora(self):
        f = mp.check_reader_leak(model(), self.PROSE, 3)
        self.assertEqual([(x["category"], x["severity"]) for x in f], [("KN-02 READER_MAP_LEAK", "HIGH")])

    def test_kn02_liberado_no_capitulo_nao_dispara(self):
        self.assertEqual(mp.check_reader_leak(model(), self.PROSE, 8), [])

    def test_kn02_leitor_ja_aprendeu_nao_dispara(self):
        lg = ledger([ev("EV-1", 2, "READER", ["CART:EXISTS:TS-SUB-SEL"])])
        self.assertEqual(mp.check_reader_leak(model(), self.PROSE, 3, lg), [])

    def test_kn02_nao_se_aplica_ao_que_esta_impresso(self):
        self.assertEqual(mp.check_reader_leak(model(), "Ela entrou na Capela do Vau.", 1), [])

    def test_kn02_ignora_acentos_e_caixa(self):
        self.assertTrue(mp.check_reader_leak(model(), "CRIPTA SELADA!", 1))


class Depictions(unittest.TestCase):
    def test_fixture_limpa_com_mapa_oficial_de_autor_institucional(self):
        f = cc.validate(model())
        self.assertEqual([x for x in f if x["severity"] in cc.BLOCKING], [])
        self.assertEqual(cats(f, "MP-"), [])

    def test_my08_continua_valendo_para_o_mapa_diegetico_impresso(self):
        m = model()
        art(m, "MAP-DIEGETIC-A")["author"] = "INST-GUARDA"
        self.assertTrue(cats(cc.validate(m), "MY-08"))

    def test_relacao_fora_do_enum(self):
        m = model()
        art(m, "MAP-OFF-01")["depicts"].append({"target": "TS-CEN-CAP", "relation": "TRUE_LOCATION"})
        self.assertTrue(any(f["category"] == "INVALID_ENUM" for f in cc.validate(m)))

    def test_phantom_que_existe_no_grafo(self):
        m = model()
        art(m, "MAP-OFF-01")["depicts"].append({"target": "TS-CEN-EST", "relation": "PHANTOM"})
        self.assertTrue(cats(cc.validate(m), "MP-01"))

    def test_phantom_com_valid_until_no_fisico_passa(self):
        m = model()
        next(l for l in m["locations"] if l["id"] == "TS-CEN-EST")["valid_until"] = 1850
        art(m, "MAP-OFF-01")["depicts"].append({"target": "TS-CEN-EST", "relation": "PHANTOM"})
        self.assertEqual(cats(cc.validate(m), "MP-01"), [])

    def test_alvo_inexistente_e_dangling(self):
        m = model()
        art(m, "MAP-OFF-01")["depicts"].append({"target": "TS-NAO-EXISTE", "relation": "OMITS"})
        self.assertTrue(any(f["category"] == "CG-01 EDGE_DANGLING" for f in cc.validate(m)))

    def test_falsified_sem_truth_ref_reprova(self):
        m = model()
        art(m, "MAP-OFF-01")["depicts"] = [{"target": "TS-URB-MOI", "relation": "FALSIFIED_STATUS", "as_status": "ACTIVE"}]
        self.assertTrue(cats(cc.validate(m), "MP-03"))

    def test_renamed_com_nome_registrado_dispensa_truth_ref(self):
        m = model()
        art(m, "MAP-OFF-01")["depicts"] = [{"target": "TS-URB-CEM", "relation": "RENAMED", "as_name": "Cemitério Velho"}]
        self.assertEqual(cats(cc.validate(m), "MP-"), [])

    def test_renamed_com_nome_desconhecido_exige_truth_ref(self):
        m = model()
        art(m, "MAP-OFF-01")["depicts"] = [{"target": "TS-URB-CEM", "relation": "RENAMED", "as_name": "Campo Santo"}]
        self.assertTrue(cats(cc.validate(m), "MP-03"))

    def test_misplaced_dentro_da_tolerancia_nao_e_erro_do_mapa(self):
        m = model()
        art(m, "MAP-OFF-01")["source_file"] = "SRC-MAP-A"
        art(m, "MAP-OFF-01")["author"] = {"status": "MUST_REMAIN_UNKNOWN"}
        art(m, "MAP-OFF-01")["depicts"] = [{"target": "TS-URB-MOI", "relation": "MISPLACED", "as_position_px": [91, 20]}]
        self.assertTrue(cats(cc.validate(m), "MP-02"))

    def test_misplaced_longe_passa(self):
        m = model()
        art(m, "MAP-OFF-01")["source_file"] = "SRC-MAP-A"
        art(m, "MAP-OFF-01")["author"] = {"status": "MUST_REMAIN_UNKNOWN"}
        art(m, "MAP-OFF-01")["depicts"] = [{"target": "TS-URB-MOI", "relation": "MISPLACED", "as_position_px": [150, 20]}]
        self.assertEqual(cats(cc.validate(m), "MP-"), [])

    def test_misplaced_sem_posicao_nem_truth_ref(self):
        m = model()
        art(m, "MAP-OFF-01")["depicts"] = [{"target": "TS-URB-MOI", "relation": "MISPLACED"}]
        self.assertTrue(cats(cc.validate(m), "MP-03"))


class Layers(unittest.TestCase):
    def test_camada_reservada_sem_conteudo_passa(self):
        self.assertEqual(cats(cc.validate(model()), "LY-"), [])

    def test_camada_reservada_com_conteudo_reprova(self):
        m = model()
        m["layers"][0]["depicts"] = [{"target": "TS-CEN-CAP", "relation": "ACCURATE"}]
        self.assertTrue(cats(cc.validate(m), "LY-01"))

    def test_artefato_com_camada_inexistente(self):
        m = model()
        art(m, "MAP-OFF-01")["map_layer"] = "LYR-NAO-EXISTE"
        self.assertTrue(any(f["category"] == "CG-01 EDGE_DANGLING" and "map_layer" in f["evidence"] for f in cc.validate(m)))


class AuthorProtection(unittest.TestCase):
    def test_t36_busca_que_so_produz_evidencia_passa(self):
        lg = ledger([ev("EV-1", 4, "CHR-K", ["EVD-01"], kind=["PROVENANCE_INQUIRY"])])
        self.assertEqual(mp.check_author_protection(model(), lg), [])

    def test_t36_busca_que_resolve_reprova(self):
        lg = ledger([ev("EV-1", 4, "CHR-K", ["EVD-01"], kind=["PROVENANCE_INQUIRY"], resolves=True)])
        f = mp.check_author_protection(model(), lg)
        self.assertEqual([(x["category"], x["severity"]) for x in f], [("MY-08 MAP_AUTHOR_REVEALED", "BLOCKER")])

    def test_t36_knowledge_delta_que_ensina_autoria_reprova(self):
        lg = ledger([ev("EV-1", 4, "READER", ["CART:AUTHOR:CHR-K"])])
        self.assertTrue(mp.check_author_protection(model(), lg))

    def test_gt_que_responde_a_pergunta_da_autoria_nao_pode_ser_aprendido(self):
        gts = [{"id": "GT-AUTOR", "reader_access": "NEVER", "answers": "Q-MAP-AUTHOR"}]
        lg = ledger([ev("EV-1", 9, "CHR-K", ["GT-AUTOR"])], gts=gts)
        self.assertTrue(mp.check_author_protection(model(), lg))

    def test_gt_de_outra_pergunta_nao_e_afetado(self):
        gts = [{"id": "GT-OUTRO", "reader_access": "NEVER", "answers": "Q-OUTRA"}]
        lg = ledger([ev("EV-1", 9, "CHR-K", ["GT-OUTRO"])], gts=gts)
        self.assertEqual(mp.check_author_protection(model(), lg), [])


class BeliefByArtifact(unittest.TestCase):
    def test_belief_view(self):
        v = mp.belief_view(model(), "MAP-OFF-01")
        self.assertEqual(v["omits"], ["TS-SUB-TUN"])
        self.assertEqual(v["believes_present_but_absent"], ["PHANTOM-EDG-1"])
        self.assertEqual(v["falsified"], ["TS-URB-MOI"])
        self.assertIsNone(mp.belief_view(model(), "MAP-NAO-EXISTE"))

    def test_planejar_por_via_fantasma_e_info(self):
        f = mp.check_planned_belief(model(), "MAP-OFF-01", ["PHANTOM-EDG-1"], [], 3, "MV-1")
        self.assertEqual([(x["category"], x["severity"]) for x in f], [("PLANNED_ON_FALSE_BELIEF", "INFO")])

    def test_artefato_nao_visto_e_kn04(self):
        f = mp.check_planned_belief(model(), "MAP-OFF-01", [], [], 3, "MV-1", seen_ok=False)
        self.assertEqual([(x["category"], x["severity"]) for x in f], [("KN-04 BELIEF_ARTIFACT_NOT_SEEN", "HIGH")])

    def test_artefato_inexistente_e_dangling(self):
        f = mp.check_planned_belief(model(), "MAP-X", [], [], 3, "MV-1")
        self.assertEqual(f[0]["severity"], "BLOCKER")

    def test_mapa_desatualizado_aresta_colapsada(self):
        m = model()
        m["manifest"]["mutations"] = [{"id": "MUT-1", "chapter": 2, "proposal_ref": "P", "cause": "EV-1",
                                       "effects": [{"edge": "EDG-U-001", "new_state": "COLLAPSED"}]}]
        f = mp.check_planned_belief(m, "MAP-OFF-01", ["EDG-U-001"], [], 3, "MV-1")
        self.assertEqual([x["category"] for x in f], ["PLANNED_ON_FALSE_BELIEF"])

    def test_rota_real_por_aresta_omitida_e_info(self):
        f = mp.check_planned_belief(model(), "MAP-OFF-01", [], ["TS-SUB-TUN"], 3, "MV-1")
        self.assertEqual([x["category"] for x in f], ["ROUTE_OMITTED_BY_BELIEF"])

    def test_artifact_seen_por_movimento_ou_ledger(self):
        self.assertTrue(mp.artifact_seen({"artifact_seen": [{"artifact": "MAP-OFF-01", "from_chapter": 2}]}, None, "CHR-K", 3, "MAP-OFF-01"))
        self.assertFalse(mp.artifact_seen({"artifact_seen": [{"artifact": "MAP-OFF-01", "from_chapter": 5}]}, None, "CHR-K", 3, "MAP-OFF-01"))
        lg = ledger([ev("EV-1", 1, "CHR-K", ["CART:SEEN:MAP-OFF-01"])])
        self.assertTrue(mp.artifact_seen({}, lg, "CHR-K", 3, "MAP-OFF-01"))
        self.assertFalse(mp.artifact_seen({}, None, "CHR-K", 3, "MAP-OFF-01"))


class MovementIntegration(unittest.TestCase):
    STAGINGS = [{"id": "S1", "actor": "CHR-K", "location": "TS-CEN-ORG", "at": "D003T10:00", "chapter": 3},
                {"id": "S2", "actor": "CHR-K", "location": "TS-CEN-CAP", "at": "D003T10:40", "chapter": 3}]

    def mv(self, **kw):
        return {"id": "MV-1", "from_staging": "S1", "to_staging": "S2", "actor": "CHR-K", "route": ["EDG-U-001"], **kw}

    def test_planejou_por_mapa_falso_mas_percurso_fisico_valido(self):
        r = cg.validate_movement(model(), self.mv(planned_on="BELIEF:MAP-OFF-01", planned_route=["PHANTOM-EDG-1", "EDG-U-001"],
                                                  artifact_seen=[{"artifact": "MAP-OFF-01", "from_chapter": 1}]), self.STAGINGS)
        self.assertNotEqual(r["verdict"], "FAIL")
        self.assertIn("PLANNED_ON_FALSE_BELIEF", [f["category"] for f in r["findings"]])
        self.assertNotIn("KN-04 BELIEF_ARTIFACT_NOT_SEEN", [f["category"] for f in r["findings"]])

    def test_sem_ter_visto_o_mapa_reprova(self):
        r = cg.validate_movement(model(), self.mv(planned_on="BELIEF:MAP-OFF-01", planned_route=["EDG-U-001"]), self.STAGINGS)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("KN-04 BELIEF_ARTIFACT_NOT_SEEN", [f["category"] for f in r["findings"]])

    def test_crenca_nao_afrouxa_a_fisica(self):
        st = [dict(self.STAGINGS[0]), {**self.STAGINGS[1], "at": "D003T10:01"}]
        r = cg.validate_movement(model(), self.mv(planned_on="BELIEF:MAP-OFF-01", planned_route=["PHANTOM-EDG-1"],
                                                  artifact_seen=[{"artifact": "MAP-OFF-01", "from_chapter": 1}]), st)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("TR-01 TRAVEL_PHYSICALLY_IMPOSSIBLE", [f["category"] for f in r["findings"]])


class CLI(unittest.TestCase):
    def run_cli(self, *args):
        p = subprocess.run([sys.executable, str(SCRIPT), "--canon", str(FIXTURE), *args], capture_output=True, text=True,
                           encoding="utf-8", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
        return p.returncode, p.stdout

    def test_exits(self):
        code, out = self.run_cli("--exits")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["notice"], "EXIT_TRUTH_NOT_IN_CARTOGRAPHY")

    def test_exits_com_capitulo(self):
        self.assertEqual(json.loads(self.run_cli("--exits", "--chapter", "3")[1])["count"], 1)

    def test_exit_truth_com_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            lp = Path(d) / "L.yaml"
            lp.write_text(yaml.safe_dump(ledger()), encoding="utf-8")
            code, out = self.run_cli("--exit-truth", "--engine-view", "--authorized-by", "GT-EXIT-1", "--ledger", str(lp))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["status"], "AUTHORIZED_ID_CONFIRMATION")
        self.assertNotIn("CONTEUDO-SECRETO", out)

    def test_reader_map_e_gap(self):
        self.assertEqual(json.loads(self.run_cli("--reader-map")[1])["view"], "READER_PROJECTION")
        gap = json.loads(self.run_cli("--reader-gap", "CHR-X", "--chapter", "2")[1])
        self.assertIn("EDG-S-001", {r["edge"] for r in gap["reader_knows_but_pov_does_not"]})

    def test_belief(self):
        self.assertEqual(json.loads(self.run_cli("--belief", "MAP-OFF-01")[1])["omits"], ["TS-SUB-TUN"])

    def test_check_prose_sai_com_erro_no_vazamento(self):
        with tempfile.TemporaryDirectory() as d:
            pp = Path(d) / "cap3.md"
            pp.write_text("Ele viu a Cripta Selada.", encoding="utf-8")
            code, out = self.run_cli("--check-prose", str(pp), "--chapter", "3")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["findings"][0]["category"], "KN-02 READER_MAP_LEAK")

    def test_validate_com_ledger_protege_autoria(self):
        with tempfile.TemporaryDirectory() as d:
            lp = Path(d) / "L.yaml"
            lp.write_text(yaml.safe_dump(ledger([ev("EV-1", 4, "READER", ["CART:AUTHOR:CHR-K"])])), encoding="utf-8")
            code, _ = self.run_cli("--ledger", str(lp))
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
