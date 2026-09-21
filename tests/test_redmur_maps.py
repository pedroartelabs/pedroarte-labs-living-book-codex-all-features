"""Slice 4 sobre os dados reais de SEM ROSTO: saídas, MYSTERY PRESERVATION GATE (consulta), mapa do leitor a partir dos
mapas impressos (SDD 22.6, T33), camadas reservadas e autoria protegida (T36).

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_redmur_maps -v
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import cartography_maps as mp  # noqa: E402
import check_cartography as cc  # noqa: E402

CANON = REPO / "books" / "sem-rosto" / "cartography" / "seeds"
M = cc.load_model(CANON)
FORBIDDEN_EXIT_CLASSES = {"TRUE_EXIT", "REAL_EXIT", "SECRET_EXIT", "HIDDEN_EXIT"}


class Exits(unittest.TestCase):
    def test_dez_saidas_com_aviso_fixo(self):
        r = mp.exits_query(M)
        self.assertEqual(r["count"], 10)
        self.assertEqual(r["notice"], "EXIT_TRUTH_NOT_IN_CARTOGRAPHY")

    def test_toda_saida_termina_em_off_map(self):
        for e in mp.exits_query(M)["exits"]:
            self.assertEqual(e["physical"]["beyond_frame"], "OFF_MAP", e["id"])

    def test_classes_so_do_enum_fechado(self):
        for e in mp.exits_query(M)["exits"]:
            self.assertLessEqual(set(e["exit_classes"]), cc.EXIT_CLASSES, e["id"])
            self.assertFalse(set(e["exit_classes"]) & FORBIDDEN_EXIT_CLASSES)

    def test_entrada_principal_e_east_road_fechada(self):
        by = {e["id"]: e for e in mp.exits_query(M)["exits"]}
        self.assertIn("OFFICIAL_EXIT", by["EXT-01"]["exit_classes"])
        self.assertIn("CLOSED_EXIT", by["EXT-02"]["exit_classes"])
        self.assertEqual(by["EXT-02"]["claims"][0]["epistemic_status"], "OFFICIAL_CLAIM")   # 'fechada' é alegação do mapa

    def test_nenhuma_saida_tem_truth_ref_resolvido(self):
        r = mp.exit_truth(M)
        self.assertEqual(r["status"], "POINTERS_ONLY")
        self.assertTrue(all(x["truth_ref"] is None for x in r["exits"]))

    def test_varredura_t09_nas_consultas_reais(self):
        import cartography_graph as cg
        blobs = [mp.exits_query(M), mp.exit_truth(M), mp.reader_map(M, 0), cg.escape_routes(M, "RM-CEN-SMC")]
        for b in blobs:
            self.assertIsNone(cc.TRUE_EXIT_RE.search(json.dumps(b, ensure_ascii=False, default=str)))


class ReaderMap(unittest.TestCase):
    def test_t33_baseline_inclui_o_inset_subterraneo(self):
        st = mp.reader_map(M, 0)["states"]
        for i in ("EDG-S-001", "EDG-P-001", "EDG-P-003", "RM-SUB-CHB", "RM-CEN-CHP", "RM-SUB-CCT"):
            self.assertEqual(st.get(i), "SEEN_ON_MAP", i)

    def test_t33_nao_impressos_ficam_de_fora(self):
        st = mp.reader_map(M, 0)
        for i in ("RM-SUB-BTF", "RM-SUB-SC4"):          # Black Thistle Filling Station e Sealed Crypt IV
            self.assertNotIn(i, st["states"])
            self.assertIn(i, st["unseen"])

    def test_ligacao_inferida_nao_estava_no_mapa(self):
        self.assertNotIn("EDG-U-046", mp.reader_map(M, 0)["states"])
        self.assertIn("EDG-U-046", mp.reader_map(M, 0)["unseen"])

    def test_so_tres_ids_invisiveis_ao_leitor(self):
        self.assertEqual(mp.reader_map(M, 0)["counts"]["UNSEEN"], 3)

    def test_destinos_fora_da_moldura_estao_no_mapa_como_texto(self):
        st = mp.reader_map(M, 0)["states"]
        for i in ("RM-OFF-DNS", "RM-OFF-WSH", "RM-OFF-ELD"):
            self.assertEqual(st.get(i), "SEEN_ON_MAP", i)

    def test_projecao_sem_estado_fisico(self):
        blob = json.dumps(mp.reader_map(M, 0))
        for k in ("secret_level", "HIDDEN", "SECRET_PASSAGE", "state_timeline"):
            self.assertNotIn(k, blob)

    def test_ironia_dramatica_passagens_ocultas_que_o_pov_desconhece(self):
        gap = {r["edge"] for r in mp.reader_knows_pov_does_not(M, "CHR-QUALQUER", 1)["reader_knows_but_pov_does_not"]}
        for i in ("EDG-S-001", "EDG-P-001", "EDG-P-003"):
            self.assertIn(i, gap)
        self.assertNotIn("EDG-U-001", gap)                # via pública

    def test_kn02_nao_dispara_para_o_que_esta_no_mapa(self):
        self.assertEqual(mp.check_reader_leak(M, "Ela cruzou Burn Bridge até o Red Stag Pub e a Old Parish Cemetery.", 1), [])


class Gate(unittest.TestCase):
    def test_validador_real_sem_achado_bloqueante(self):
        self.assertEqual([f for f in cc.validate(M) if f["severity"] in cc.BLOCKING], [])

    def test_s4_nao_introduz_achados_novos(self):
        self.assertEqual([f for f in cc.validate(M) if f["category"].startswith(("MP-", "LY-"))], [])

    def test_camadas_historicas_reservadas_sem_conteudo(self):
        layers = {l["id"]: l for l in M["layers"]}
        self.assertEqual(len(layers), 8)
        self.assertTrue(all(l["status"] == "RESERVED" for l in layers.values()))
        self.assertEqual(mp.check_layers(M), [])

    def test_camada_oficial_moderna_nao_e_a_dos_mapas_a_e_b(self):
        for a in M["artifacts"]:
            if a.get("kind") == "MAP":
                self.assertEqual(a["map_layer"], "UNKNOWN")

    def test_autoria_dos_mapas_permanece_desconhecida(self):
        for a in M["artifacts"]:
            if a.get("kind") == "MAP":
                self.assertEqual(a["author"]["status"], "MUST_REMAIN_UNKNOWN")

    def test_nenhuma_relacao_de_mapa_afirma_o_que_nao_se_sabe(self):
        self.assertEqual(mp.check_depictions(M), [])
        self.assertTrue(all(not a.get("depicts") for a in M["artifacts"] if a.get("kind") == "MAP"))

    def test_t36_busca_por_autoria_que_resolve_reprova(self):
        lg = {"characters": [], "events": [{"id": "EV-1", "chapter": 7, "kind": ["PROVENANCE_INQUIRY"], "resolves": True}]}
        self.assertEqual(mp.check_author_protection(M, lg)[0]["category"], "MY-08 MAP_AUTHOR_REVEALED")

    def test_t36_busca_por_autoria_que_so_da_evidencia_passa(self):
        lg = {"characters": [], "events": [{"id": "EV-1", "chapter": 7, "kind": ["PROVENANCE_INQUIRY"],
                                            "knowledge_delta": [{"knower": "CHR-ENTRAO", "learns": ["EVD-PAPEL"]}]}]}
        self.assertEqual(mp.check_author_protection(M, lg), [])


if __name__ == "__main__":
    unittest.main()
