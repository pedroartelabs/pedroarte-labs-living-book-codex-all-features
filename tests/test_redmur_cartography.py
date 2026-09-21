"""Testes dos DADOS de SEM ROSTO (Slice 1 do SDD REDMUR_CANONICAL_CARTOGRAPHY_GRAPH,
seção 35: T01–T09, T19–T21, T30, T32, T34 e verificações de transcrição).

Rodam sobre os seeds reais de `books/sem-rosto/cartography/seeds/` e sobre os dois
mapas canônicos pinados. 100% offline.

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_redmur_cartography -v
"""
from __future__ import annotations

import copy
import hashlib
import math
import sys
import unittest
from collections import defaultdict, deque
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import check_cartography as cc  # noqa: E402

PKG = REPO / "books" / "sem-rosto" / "cartography"
SEEDS = PKG / "seeds"
MODEL = cc.load_model(SEEDS)
PROJ = cc.project_all(MODEL)
LOCS = cc.index_by_id(MODEL["locations"])
ALL_IDS = {item["id"] for _, item in cc.all_id_carriers(MODEL)}

MAP_A_SHA = "98123fee45ea70b220c46bef719d2644729231d0f8df5d1ac00d90f6f9525f36"
MAP_B_SHA = "36cf98babb4864d0913847c845364641d55120836d8960e8e88cb4373a43b9f3"


def dist(a, b):
    return cc.euclid(PROJ[a], PROJ[b])


class Validator(unittest.TestCase):
    def test_no_blocking_findings(self):
        blocking = [f for f in cc.validate(copy.deepcopy(MODEL)) if f["severity"] in cc.BLOCKING]
        self.assertEqual(blocking, [])

    def test_only_expected_info_remains(self):
        findings = cc.validate(copy.deepcopy(MODEL))
        self.assertEqual([f["category"] for f in findings], ["CG-10 ORPHAN_NODE"])
        self.assertEqual(findings[0]["severity"], "INFO")   # arestas de superfície: Slice 2


class Sources(unittest.TestCase):
    def test_map_files_are_pinned(self):  # T32
        for name, sha in (("MAP_A_redmur_map.png", MAP_A_SHA), ("MAP_B_redmur_arredores_map.png", MAP_B_SHA)):
            self.assertEqual(hashlib.sha256((PKG / "sources" / name).read_bytes()).hexdigest(), sha)

    def test_decision_record_hashes_sources_yaml(self):
        text = (PKG / "approvals" / "CART_DECISION_0001.md").read_text(encoding="utf-8")
        sha = hashlib.sha256((PKG / "sources" / "SOURCES.yaml").read_bytes()).hexdigest()
        self.assertIn(f"subject_sha256: {sha}", text)

    def test_scale_ratio_is_7_25_percent(self):  # T34
        scales = cc.source_scales(MODEL)
        ratio = scales["SRC-MAP-A"]["mpp"] / scales["SRC-MAP-B"]["mpp"]
        self.assertAlmostEqual(ratio, 0.0725, delta=0.0725 * 0.005)
        # a moldura do Mapa A mede 7,25 % da largura do Mapa B (mesma razão)
        self.assertAlmostEqual(1448 * scales["SRC-MAP-A"]["mpp"] / (1448 * scales["SRC-MAP-B"]["mpp"]), 0.0725,
                               delta=0.0725 * 0.005)


class Transcription(unittest.TestCase):
    def test_saint_morrow_cross_is_origin(self):  # T01
        self.assertEqual((PROJ["RM-CEN-SMC"]["x"], PROJ["RM-CEN-SMC"]["y"]), (0, 0))
        self.assertEqual(MODEL["manifest"]["metadata"]["grid"]["origin"], "RM-CEN-SMC")

    def test_every_mission_place_has_a_node(self):
        required = ["Saint Morrow Cross", "Office of Civic Preservation", "Civil Archive Hall", "Redmur Constabulary",
                    "Saint Morrow Chapel", "Old Parish Cemetery", "Black Thistle Filling Station", "General Mercantile",
                    "Red Stag Pub", "Village Clinic", "Old Coach Stop", "Rowan Cottage", "Manfred Farm", "Flarry Estate",
                    "Strathmoor Woods", "Shepherd's Bothy", "Old Quarry", "Sheep Fields", "Ash Burn", "Burn Bridge",
                    "Pumping Station", "Reservoir", "Drainage Culvert", "Root Cellar Hideout", "Caretaker House",
                    "Sealed Crypt IV", "Ruined Tool Shed", "Glenath", "Creggan Bothy", "Blackridge Farm", "Corrie's End",
                    "Kirkhollow", "Elderglen", "Harrowmire", "Stonewell", "Cairnvale", "Grayfen", "Thistlebank",
                    "Letham", "Craigness", "Moor Cairn", "Ben Ràth", "Ruínas de Kellburne", "Carriden Hamlet",
                    "Blackthorn Cottage", "Willowford", "Fenside Grange", "Mossgate", "Raven's Holt", "Old Mill",
                    "Loch Draven", "Loch Calder", "Loch Ainslie", "Torran Mire", "Muirfield Farm"]
        names = {cc.normalize_name(n.get("name") if isinstance(n, dict) else n)
                 for l in MODEL["locations"] for n in cc.as_list(l.get("names")) + [l.get("canonical_name")]}
        register_names = {cc.normalize_name(e["printed_name"]) for e in MODEL["register"]["entries"]}
        # Letham e Passo de Muirchéin: só como linha do registro (NOT_ON_MAP), não como lugar
        for n in required:
            key = cc.normalize_name(n)
            self.assertTrue(key in names or key in register_names or any(key in x for x in names),
                            f"sem nó ou registro: {n}")
        self.assertIn(cc.normalize_name("Letham"), register_names)

    def test_no_edge_dangles(self):  # T03
        self.assertEqual([f for f in cc.validate(copy.deepcopy(MODEL)) if f["category"].startswith("CG-01")], [])

    def test_inventory_is_complete(self):  # T02
        self.assertGreaterEqual(len(MODEL["inventory"]), 150)
        self.assertTrue(all(i["maps_to"] in ALL_IDS for i in MODEL["inventory"]))

    def test_layers_are_present(self):
        layers = {l["layer"] for l in MODEL["locations"]}
        self.assertEqual(layers, {"URBAN", "REGIONAL", "SUBTERRANEAN"})

    def test_coordinates_match_sdd_tables(self):
        expected = {"RM-CEN-CHP": (-822, 474), "RM-URB-OPC": (-1361, 130), "RM-URB-ROW": (2345, 1235),
                    "RM-URB-BBR": (2547, 150), "RM-CEN-RSP": (158, 263), "RM-URB-OQY": (-348, 859),
                    "RM-URB-PMP": (2973, 413), "RM-REG-CRV": (-9385, -6145), "RM-REG-GLN": (12122, 18993),
                    "RM-REG-KLB": (26646, 20110)}
        for lid, (x, y) in expected.items():
            self.assertAlmostEqual(PROJ[lid]["x"], x, delta=2, msg=lid)
            self.assertAlmostEqual(PROJ[lid]["y"], y, delta=2, msg=lid)

    def test_shared_nodes_use_map_a_metric(self):
        for lid in ("RM-CEN-CHP", "RM-URB-OPC", "RM-URB-FLE", "RM-URB-OQY", "RM-URB-MNF", "RM-URB-ROW", "RM-URB-BBR"):
            self.assertEqual(PROJ[lid]["basis"], "SRC-MAP-A", lid)
            b = [e for e in LOCS[lid]["source_px"] if e["source"] == "SRC-MAP-B"]
            self.assertTrue(b and all(e["anchor"] == "SCHEMATIC" for e in b), lid)

    def test_map_b_only_nodes_use_decided_scale_and_accuracy(self):
        self.assertEqual(PROJ["RM-REG-CRV"]["basis"], "SRC-MAP-B")
        self.assertEqual(PROJ["RM-REG-CRV"]["accuracy_m"], 840)
        self.assertEqual(LOCS["RM-REG-BRT"]["elevation"]["elevation_asl"], 714)

    def test_sdd_worked_examples(self):
        self.assertAlmostEqual(dist("RM-CEN-RSP", "RM-URB-OPC"), 1525, delta=3)      # SDD 17.7: Red Stag → cemitério
        self.assertAlmostEqual(dist("RM-URB-OQY", "RM-URB-PMP"), 3351, delta=5)      # SDD 11.4: Quarry ↔ Pumping
        self.assertAlmostEqual(dist("RM-URB-ROW", "RM-URB-SBO"), 1933, delta=5)      # SDD Apêndice C, pergunta 2


class Routes(unittest.TestCase):
    RTE = cc.index_by_id(MODEL["routes"])
    RMY = cc.index_by_id(MODEL["route_mysteries"])

    def test_city_routes_exist(self):  # T04
        for rid in ("RTE-A-R1", "RTE-A-R2", "RTE-A-R3"):
            self.assertIn(rid, self.RTE)
            self.assertEqual(self.RTE[rid]["source"], "SRC-MAP-A")
            self.assertEqual(self.RTE[rid]["continuation_beyond_drawn"], "UNKNOWN")

    def test_map_a_routes_follow_the_map_not_the_brief(self):  # D-CART-03 / D-CART-04
        ends = lambda rid: [e.get("location") for e in self.RTE[rid]["drawn_endpoints"] if e.get("location")]
        self.assertEqual(ends("RTE-A-R2"), ["RM-URB-SBO", "RM-URB-ROW"])
        self.assertEqual(ends("RTE-A-R3"), ["RM-URB-OQY", "RM-URB-MNF"])
        self.assertEqual(ends("RTE-A-R1")[0], "RM-URB-OPC")
        self.assertNotIn("RM-URB-DCU", str(self.RTE["RTE-A-R1"]["drawn_endpoints"]))       # R1 não chega ao Culvert
        self.assertNotIn("RM-URB-ERC", str(self.RTE["RTE-A-R3"]["drawn_endpoints"]))       # R3 não segue para a East Road

    def test_regional_routes_and_mysteries(self):  # T05
        for k in ("R4", "R7", "R13", "R17"):
            self.assertIn(f"RTE-B-{k}", self.RTE)
            self.assertIn(f"RMY-{k}", self.RMY)
        for k in ("R1", "R2", "R3"):
            self.assertIn(f"RMY-{k}", self.RMY)
        self.assertEqual(self.RMY["RMY-R1"]["map_b_anchor"], {"status": "NOT_FOUND"})
        self.assertEqual(self.RMY["RMY-R2"]["map_b_anchor"], {"status": "NOT_FOUND"})

    def test_mottos_are_verbatim_artifacts_and_unresolved(self):
        mottos = {"R1": "O círculo retorna.", "R2": "Nem todo caminho continua.", "R3": "Há mais de uma margem.",
                  "R4": "Entrada ou saída?", "R7": "Desaparece após a ponte.", "R13": "Sinais foram removidos.",
                  "R17": "Usada, mas por quem?"}
        for k, m in mottos.items():
            r = self.RMY[f"RMY-{k}"]
            self.assertEqual(r["motto"], m)
            self.assertEqual(r["motto_status"], "MAP_ARTIFACT")
            self.assertEqual(r["resolution_state"], "UNRESOLVED")
            self.assertIsNone(r["truth_ref"])
            self.assertEqual(r["candidate_interpretations"], [])

    def test_same_label_does_not_imply_identity(self):
        # R3 tem três ocorrências; nenhuma foi fundida em uma rota só
        r3 = [r for r in MODEL["routes"] if r["label"] == "R3"]
        self.assertEqual(len(r3), 3)          # 1 no Mapa A + 2 no Mapa B com rótulo
        self.assertEqual(len({r["id"] for r in r3}), 3)
        qm = cc.index_by_id(MODEL["routes"])["RTE-B-QM"]
        self.assertEqual(qm["label"], "GLY-B-09")   # o glifo ilegível NÃO foi rotulado R3


class Underground(unittest.TestCase):
    def graph(self):
        adj = defaultdict(set)
        for e in MODEL["edges"]:
            adj[e["from"]].add(e["to"])
            adj[e["to"]].add(e["from"])
        return adj

    def reach(self, start, layer_only=True):
        adj, seen, q = self.graph(), {start}, deque([start])
        while q:
            n = q.popleft()
            for m in adj[n]:
                if m not in seen and (not layer_only or LOCS[m]["layer"] == "SUBTERRANEAN"):
                    seen.add(m); q.append(m)
        return seen

    def test_network_navigable_only_through_existing_edges(self):  # T06
        comp = self.reach("RM-SUB-CHB")
        self.assertEqual(comp, {"RM-SUB-CHB", "RM-SUB-CCT", "RM-SUB-STD", "RM-SUB-RCP", "RM-SUB-PSC", "RM-SUB-QCS",
                                "RM-SUB-ROT", "RM-SUB-CUX", "RM-JCT-S1", "RM-JCT-S2", "RM-JCT-S3"})

    def test_chapel_to_cemetery_goes_through_junction_in_two_edges(self):
        e = {frozenset((x["from"], x["to"])) for x in MODEL["edges"]}
        self.assertNotIn(frozenset(("RM-SUB-CHB", "RM-SUB-CCT")), e)              # sem aresta direta
        self.assertIn(frozenset(("RM-SUB-CHB", "RM-JCT-S1")), e)
        self.assertIn(frozenset(("RM-JCT-S1", "RM-SUB-CCT")), e)

    def test_every_connected_sub_node_reaches_a_portal(self):
        portals = {e["to"] for e in MODEL["edges"] if e["edge_type"] == "PORTAL"}
        self.assertEqual(len(portals), 7)
        for n in self.reach("RM-SUB-CHB"):
            if LOCS[n]["type"] != "JUNCTION" and n != "RM-SUB-STD":
                self.assertIn(n, portals, n)

    def test_arrows_are_not_directionality(self):  # T30
        edges = [e for e in MODEL["edges"] if e["id"].startswith("EDG-S-")]
        self.assertEqual(len(edges), 11)
        self.assertTrue(all(e["directionality"] == "BOTH" for e in edges))
        self.assertTrue(any(e["drawn_arrow"] for e in edges))    # a seta fica como anotação

    def test_underground_dimensions_are_unspecified_not_invented(self):
        for e in MODEL["edges"]:
            if e["id"].startswith(("EDG-S-", "EDG-P-")):
                self.assertEqual(e["distance_meters"], {"basis": "UNSPECIFIED"})

    def test_black_thistle_and_sealed_crypt_are_undeclared_underground(self):  # T21
        for lid in ("RM-SUB-BTF", "RM-SUB-SC4"):
            l = LOCS[lid]
            self.assertEqual(l["layer"], "SUBTERRANEAN")
            self.assertEqual(l["source"], "AUTHOR_DECLARED")
            self.assertEqual(l["connectivity"], "UNDECLARED")
            self.assertIsNone(PROJ[lid])
            self.assertNotIn("inset_px", l)                                  # não estão no inset impresso
            self.assertEqual(l["omitted_by"], ["MAP-DIEGETIC-A"])
            self.assertFalse([e for e in MODEL["edges"] if lid in (e["from"], e["to"])])
        self.assertEqual(LOCS["RM-SUB-SC4"]["status"], "SEALED")
        # nenhuma cripta I–III foi criada por causa do "IV"
        self.assertFalse([n for n in LOCS if "Sealed Crypt" in LOCS[n]["canonical_name"] and n != "RM-SUB-SC4"])

    def test_quarry_crawlspace_anomaly_is_preserved_not_fixed(self):
        # o inset desenha Quarry Crawlspace ao lado do Pumping Station Channel; ancorado na Old Quarry, o piso é ~3,35 km
        self.assertGreater(dist("RM-SUB-QCS", "RM-SUB-PSC"), 3300)


class Boundaries(unittest.TestCase):
    EXT = cc.index_by_id(MODEL["exits"])
    ROADS = cc.index_by_id(MODEL["roads"])

    def test_east_road_starts_officially_closed(self):  # T07
        claims = self.ROADS["ROAD-EAST"]["claims"]
        self.assertEqual(claims[0]["text"], "Officially Closed")
        self.assertEqual(claims[0]["epistemic_status"], "OFFICIAL_CLAIM")
        self.assertEqual(LOCS["RM-URB-ERC"]["status"], "RESTRICTED")
        self.assertEqual(LOCS["RM-URB-ERC"]["status_source"], "OFFICIAL_CLAIM")
        self.assertIn("CLOSED_EXIT", self.EXT["EXT-02"]["exit_classes"])

    def test_south_gate_road_is_the_known_main_entrance(self):  # T08
        texts = [c["text"] for c in self.ROADS["ROAD-SGR"]["claims"]]
        self.assertIn("Entrada Principal", texts)
        self.assertEqual(self.ROADS["ROAD-SGR"]["road_class"], "MAIN")
        self.assertEqual(self.EXT["EXT-01"]["frame_portal"], "RM-FRM-A-S")

    def test_no_exit_is_declared_true(self):  # T09
        self.assertEqual(len(self.EXT), 10)
        for x in self.EXT.values():
            self.assertLessEqual(set(x["exit_classes"]), cc.EXIT_CLASSES)
            self.assertEqual(x["physical"]["beyond_frame"], "OFF_MAP")
            self.assertIsNone(x["truth_ref"])
        text = "\n".join(p.read_text(encoding="utf-8") for p in SEEDS.glob("*.yaml")).lower()
        self.assertEqual(cc.scan_answers(copy.deepcopy(MODEL)), [])     # chaves e valores parseados
        for banned in ("true_exit", "real_exit", "saida_verdadeira"):    # comentários podem explicar a regra em prosa
            self.assertNotIn(banned, text)

    def test_every_frame_portal_of_map_b_signs_exists(self):
        for pid in ("RM-FRM-B-NE", "RM-FRM-B-W", "RM-FRM-B-SW1", "RM-FRM-B-SW2", "RM-FRM-B-SE1", "RM-FRM-B-SE2"):
            self.assertEqual(LOCS[pid]["type"], "FRAME_PORTAL")

    def test_sign_distances_are_claims_not_physics(self):
        for oid in ("RM-OFF-CLR", "RM-OFF-DNS", "RM-OFF-WSH", "RM-OFF-INV", "RM-OFF-ELD"):
            self.assertIsNone(PROJ[oid])
            self.assertEqual(LOCS[oid]["claims"][0]["epistemic_status"], "OFFICIAL_CLAIM")
        self.assertIsNone(LOCS["RM-OFF-INV"]["claims"][0]["distance_claim_mi"])   # dígito ilegível preservado


class Register(unittest.TestCase):
    ENTRIES = MODEL["register"]["entries"]

    def test_thirty_lines_in_printed_order(self):  # T19
        self.assertEqual(len(self.ENTRIES), 30)
        self.assertEqual([e["line"] for e in self.ENTRIES], list(range(1, 30 + 1)))
        self.assertEqual(self.ENTRIES[0]["printed_name"], "Redmur")
        self.assertEqual(self.ENTRIES[-1]["printed_name"], "Old Mill")

    def test_duplicate_05_and_missing_06_are_preserved(self):
        idx = [e["display_index"] for e in self.ENTRIES]
        self.assertTrue(all(isinstance(i, str) for i in idx))
        self.assertEqual(idx.count("05"), 2)
        self.assertNotIn("06", idx)
        self.assertEqual([e["printed_name"] for e in self.ENTRIES if e["display_index"] == "05"], ["Rowan Cottage", "Glenath"])

    def test_letham_and_muirchein_are_not_on_the_map(self):  # T20
        for name in ("Letham", "Passo de Muirchéin"):
            e = next(x for x in self.ENTRIES if x["printed_name"] == name)
            self.assertEqual(e["placement"], "NOT_ON_MAP")
            self.assertIsNone(e["location_id"])
        for n in ("letham", "muirch"):
            self.assertFalse([l for l in MODEL["locations"] if n in cc.normalize_name(l["canonical_name"])])

    def test_saint_morrow_is_not_forced_onto_a_place(self):
        e = next(x for x in self.ENTRIES if x["printed_name"] == "Saint Morrow")
        self.assertIsNone(e["location_id"])
        self.assertEqual(set(e["candidates"]), {"RM-CEN-CHP", "RM-CEN-SMC"})

    def test_ordering_significance_stays_unknown(self):
        self.assertTrue(all(e["ordering_significance"] == "UNKNOWN" and e["truth_ref"] is None for e in self.ENTRIES))
        self.assertTrue(MODEL["register"]["printed_order_is_artifact"])


class AuthorDecisions(unittest.TestCase):
    ANM = cc.index_by_id(MODEL["anomalies"])
    CMY = cc.index_by_id(MODEL["mysteries"])
    ART = cc.index_by_id(MODEL["artifacts"])

    def test_all_22_anomalies_are_intentional(self):
        self.assertEqual(len(self.ANM), 22)
        self.assertTrue(all(a["classification"] == "INTENTIONAL_ARTIFACT" and a["decided_by"] == "CART_DECISION_0001"
                            for a in self.ANM.values()))

    def test_intentional_does_not_mean_interpreted(self):
        for m in MODEL["mysteries"] + MODEL["route_mysteries"]:
            self.assertEqual(m["candidate_interpretations"], [], m["id"])
            self.assertIsNone(m["truth_ref"], m["id"])
            self.assertNotIn(m["resolution_state"], ("RESOLVED", "PARTIALLY_RESOLVED"), m["id"])
        for g in MODEL["glyphs"]:
            self.assertIsNone(g["attributed_to"], g["id"])

    def test_activated_mysteries_reference_intentional_anomalies(self):
        for cid in ("CMY-02", "CMY-03", "CMY-06", "CMY-07"):
            refs = self.CMY[cid]["activation"]["requires_anomalies"]
            self.assertTrue(refs and all(r in self.ANM for r in refs), cid)

    def test_map_authorship_is_permanent_mystery(self):
        for mid in ("MAP-DIEGETIC-A", "MAP-DIEGETIC-B"):
            a = self.ART[mid]
            self.assertEqual(a["author"]["status"], "MUST_REMAIN_UNKNOWN")
            self.assertEqual(a["author"]["question_ref"], "Q-MAP-AUTHOR")
            self.assertEqual(a["map_layer"], "UNKNOWN")
            self.assertTrue(a["printed_in_book"])
        c = self.CMY["CMY-09"]
        self.assertEqual((c["question_policy"], c["resolution_state"]), ("NEVER", "PERMANENTLY_AMBIGUOUS"))

    def test_printed_maps_are_the_pinned_files(self):
        self.assertTrue(all(s["printed_in_book"] for s in cc.as_list(MODEL["sources"]["sources"])))

    def test_reader_baseline_declares_printed_maps(self):
        reader = next(b for b in MODEL["baseline"] if b["knower"] == "READER")
        self.assertIn("SEEN_ON_MAP", reader["knows"])
        self.assertEqual(reader["from"], "front_matter")

    def test_map_texts_are_claims_never_facts(self):
        texts = [a for a in MODEL["artifacts"] if a["kind"] == "TEXT"]
        self.assertGreaterEqual(len(texts), 20)
        self.assertTrue(all(a["epistemic_status"] != "FACT" for a in texts))
        self.assertEqual(self.ART["MAP-B-TXT-08"]["rendered_text"], "REDNUR SEMPBE OBSERVA")   # impresso como está

    def test_approved_speeds_present(self):
        s = MODEL["manifest"]["settings"]
        self.assertEqual(s["approved_by"], "CART_DECISION_0001")
        self.assertEqual(s["detection_thresholds_m"]["NIGHT_DARK"], 30)
        self.assertEqual(s["speeds_mps"]["physical_max"]["WALK"], 2.2)


class EngineUntouched(unittest.TestCase):
    def test_compose_does_not_know_cartography_yet(self):
        text = (REPO / "engine" / "scripts" / "livingbook.py").read_text(encoding="utf-8")
        self.assertNotIn("cartography", text.lower())      # integração no compose só no Slice 5


if __name__ == "__main__":
    unittest.main()
