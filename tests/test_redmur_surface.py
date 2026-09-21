"""Testes dos DADOS de superfície de SEM ROSTO (Slice 2 do SDD da cartografia: seções 13, 17, 26, 35 —
T07, T15–T18, T21, T24, T29 — e as perguntas da missão §42 / SDD Apêndice C), sobre as vias digitalizadas
do Mapa A e o curso rastreado do Ash Burn.

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_redmur_surface -v
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from collections import defaultdict, deque
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import cartography_graph as cg  # noqa: E402
import check_cartography as cc  # noqa: E402

SEEDS = REPO / "books" / "sem-rosto" / "cartography" / "seeds"
MODEL = cc.load_model(SEEDS)
LOCS = cc.index_by_id(MODEL["locations"])
PROJ = cc.project_all(MODEL)
SURFACE = [e for e in MODEL["edges"] if e["id"].startswith("EDG-U-")]


def fresh():
    return copy.deepcopy(MODEL)


def dist(a, b):
    return cc.euclid(PROJ[a], PROJ[b])


def stg(i, actor, loc, at, chapter=7, **kw):
    return {"id": i, "actor": actor, "location": loc, "at": at, "chapter": chapter, **kw}


def route(a, b, **ctx):
    return cg.route(fresh(), a, b, ctx)


def cats(findings, prefix):
    return [f for f in findings if f["category"].startswith(prefix)]


class SurfaceDigitization(unittest.TestCase):
    def test_all_edges_are_digitized_from_the_source_image(self):
        self.assertGreaterEqual(len(SURFACE), 45)
        for e in SURFACE:
            self.assertEqual(e["distance_meters"]["basis"], "DIGITIZED", e["id"])
            self.assertEqual(e["source_polyline_px"]["source"], "SRC-MAP-A", e["id"])
            self.assertGreaterEqual(len(e["source_polyline_px"]["points"]), 2, e["id"])
            self.assertIn(e["confidence"], {"PROBABLE", "UNCERTAIN"}, e["id"])   # nada é CANONICAL sem conferência humana

    def test_declared_length_matches_the_polyline(self):
        g = cg.Graph(fresh())
        for e in SURFACE:
            nominal, minimum, _ = g.edge_lengths(e)
            self.assertAlmostEqual(nominal, e["distance_meters"]["nominal"], delta=2, msg=e["id"])
            self.assertLessEqual(minimum, nominal)                      # T29: mínimo nunca excede o nominal

    def test_uncertain_links_are_exactly_the_ones_the_map_does_not_show_clearly(self):
        unc = {e["id"] for e in SURFACE if e["confidence"] == "UNCERTAIN"}
        self.assertEqual(unc, {"EDG-U-014", "EDG-U-017", "EDG-U-039", "EDG-U-040", "EDG-U-041", "EDG-U-042", "EDG-U-046"})

    def test_r1_junction_is_an_inferred_link_and_says_so(self):
        e = next(x for x in SURFACE if x["id"] == "EDG-U-046")
        self.assertEqual(e["edge_type"], "OPEN_GROUND")
        self.assertIn("INFERIDA", e["note"])

    def test_drawn_routes_have_their_own_edges_and_stay_unresolved(self):
        routes = cc.index_by_id(MODEL["routes"])
        for rid, eid in (("RTE-A-R1", "EDG-U-R1"), ("RTE-A-R2", "EDG-U-R2"), ("RTE-A-R3", "EDG-U-R3")):
            self.assertEqual(routes[rid]["edges"], [eid])
            self.assertEqual(routes[rid]["trace_status"], "DIGITIZED")
            self.assertEqual(routes[rid]["continuation_beyond_drawn"], "UNKNOWN")
            edge = next(x for x in MODEL["edges"] if x["id"] == eid)
            self.assertEqual(edge["route_membership"], [rid])

    def test_named_roads_list_their_edges(self):
        roads = cc.index_by_id(MODEL["roads"])
        self.assertEqual(roads["ROAD-SGR"]["edges"], ["EDG-U-001", "EDG-U-002", "EDG-U-003", "EDG-U-004"])
        self.assertEqual(roads["ROAD-EAST"]["edges"], ["EDG-U-022", "EDG-U-023", "EDG-U-035"])

    def test_every_urban_place_is_on_one_connected_surface_network(self):
        adj = defaultdict(set)
        for e in SURFACE:
            adj[e["from"]].add(e["to"])
            adj[e["to"]].add(e["from"])
        seen, q = {"RM-CEN-SMC"}, deque(["RM-CEN-SMC"])
        while q:
            n = q.popleft()
            for m in adj[n] - seen:
                seen.add(m)
                q.append(m)
        urban_points = [l["id"] for l in MODEL["locations"] if l["layer"] == "URBAN" and l.get("geometry", "POINT") == "POINT"
                        and "FRAME_PORTAL" not in cc.as_list(l["type"])]
        self.assertEqual([i for i in urban_points if i not in seen], [])

    def test_regional_layer_is_not_digitized_and_says_so(self):
        flag = MODEL["manifest"]["metadata"]["edges_digitized"]
        self.assertEqual(flag, {"URBAN": True, "SUBTERRANEAN": True, "REGIONAL": False})
        self.assertFalse([e for e in MODEL["edges"] if LOCS[e["from"]]["layer"] == "REGIONAL" or LOCS[e["to"]]["layer"] == "REGIONAL"])

    def test_validator_reports_only_the_regional_gap(self):
        f = cc.validate(fresh())
        self.assertEqual([(x["category"], x["severity"]) for x in f], [("CG-10 ORPHAN_NODE", "INFO")])


class WaterAndClosure(unittest.TestCase):
    def test_no_road_crosses_ash_burn_except_at_the_bridge(self):  # T15
        self.assertEqual(cg.check_water_crossings(fresh()), [])
        bridge_edges = {e["id"] for e in SURFACE if "RM-URB-BBR" in (e["from"], e["to"])}
        self.assertEqual(bridge_edges, {"EDG-U-023", "EDG-U-033", "EDG-U-035", "EDG-U-041"})

    def test_ash_burn_polyline_is_traced_not_a_stub(self):
        pts = LOCS["WAT-ASH"]["polyline_px"]
        self.assertGreaterEqual(len(pts), 15)
        self.assertEqual(pts[0]["px"], [975, 245])            # nascente visível (ANM-A-04)

    def test_a_road_across_the_river_far_from_the_bridge_would_be_rejected(self):
        m = fresh()
        m["edges"].append({"id": "EDG-X", "from": "RM-URB-MNF", "to": "RM-URB-RSV", "edge_type": "TRAIL", "directionality": "BOTH",
                           "source_polyline_px": {"source": "SRC-MAP-A", "points": [[790, 295], [1270, 360]]}})
        self.assertTrue(cg.check_water_crossings(m))

    def test_east_road_is_closed_until_a_narrative_action_opens_it(self):  # T07 + INV-C06
        closed = cg.reachable(fresh(), "RM-CEN-SMC", "RM-URB-ERC")
        self.assertFalse(closed["reachable"])
        self.assertEqual(closed["blocked_by"], [{"edge": "EDG-U-035", "reason": "CLOSED_WITHOUT_ACTION"}])
        self.assertTrue(cg.reachable(fresh(), "RM-CEN-SMC", "RM-URB-ERC", {"access_actions": ["EV-1"]})["reachable"])

    def test_pumping_station_is_reachable_without_the_closed_stretch(self):
        r = cg.reachable(fresh(), "RM-CEN-SMC", "RM-URB-PMP", {"view": "ACTOR", "actor": "CHR-P"})
        self.assertTrue(r["reachable"])
        self.assertNotIn("EDG-U-035", r["edges"])
        self.assertIn("EDG-U-033", r["edges"])

    def test_rowan_cottage_is_reached_only_by_the_drawn_route(self):
        self.assertEqual([e["id"] for e in MODEL["edges"] if "RM-URB-ROW" in (e["from"], e["to"])], ["EDG-U-R2"])


class MissionQuestions(unittest.TestCase):
    """As perguntas da missão (§42) e do SDD (Apêndice C), respondidas pelo motor."""

    def test_q2_rowan_cottage_to_shepherds_bothy(self):
        r = route("RM-URB-ROW", "RM-URB-SBO", view="ACTOR", actor="CHR-P")
        self.assertEqual(r["edges"], ["EDG-U-R2"])
        t = r["times"]
        self.assertTrue(2000 < t["length_nominal_m"] < 2300)
        self.assertTrue(12 * 60 < t["min_s"] < 17 * 60)
        self.assertTrue(24 * 60 < t["expected_s"] < 35 * 60)

    def test_q3_underground_chapel_to_cemetery(self):
        r = route("RM-CEN-CHP", "RM-URB-OPC", view="ENGINE")
        self.assertEqual(r["edges"], ["EDG-P-001", "EDG-S-001", "EDG-S-002", "EDG-P-002"])
        self.assertAlmostEqual(r["times"]["length_nominal_m"], dist("RM-CEN-CHP", "RM-URB-OPC"), delta=1)
        self.assertIn("SUBTERRANEAN_DIMENSIONS_UNSPECIFIED", r["times"]["warnings"])

    def test_q3_an_ordinary_character_does_not_know_the_tunnel(self):
        r = route("RM-CEN-CHP", "RM-URB-OPC", view="ACTOR", actor="CHR-P")
        self.assertTrue(r["found"])
        self.assertFalse([e for e in r["edges"] if e.startswith(("EDG-P-", "EDG-S-"))])

    def test_q1_routes_out_of_the_cemetery_known_to_an_ordinary_character(self):
        out = cg.escape_routes(fresh(), "RM-URB-OPC", {"view": "ACTOR", "actor": "CHR-P"})
        for x in out:
            self.assertFalse([e for e in x["edges"] if e.startswith(("EDG-P-", "EDG-S-"))], x)
        self.assertEqual({x["kind"] for x in out}, {"HIDEOUT", "APPARENT_EXIT"})
        self.assertEqual(next(x for x in out if x["kind"] == "HIDEOUT")["to"], "RM-URB-RCH")

    def test_q1_underground_escape_appears_for_an_actor_who_learned_it(self):
        m = fresh()
        m["baseline"].append({"knower": "CHR-P", "knows": {"ROUTE": ["EDG-P-002", "EDG-S-002", "EDG-S-001", "EDG-P-001"]}})
        r = cg.route(m, "RM-URB-OPC", "RM-CEN-CHP", {"view": "ACTOR", "actor": "CHR-P"})
        self.assertIn("EDG-S-002", r["edges"])

    def test_q7_red_stag_to_cemetery_in_four_minutes_fails(self):
        for mode in ("WALK", "RUN"):
            res = cg.validate_staging(fresh(), {
                "staging": [stg("S1", "CHR-P", "RM-CEN-RSP", "D014T23:14"), stg("S2", "CHR-P", "RM-URB-OPC", "D014T23:18")],
                "movements": [{"id": "M1", "actor": "CHR-P", "from_staging": "S1", "to_staging": "S2", "mode": mode}]})
            self.assertEqual(res["movements"][0]["verdict"], "FAIL", mode)
            self.assertTrue(cats(res["findings"], "TR-0"), mode)

    def test_q7_the_same_walk_is_fine_with_enough_time(self):
        res = cg.validate_staging(fresh(), {
            "staging": [stg("S1", "CHR-P", "RM-CEN-RSP", "D014T23:14"), stg("S2", "CHR-P", "RM-URB-OPC", "D014T23:54")],
            "movements": [{"id": "M1", "actor": "CHR-P", "from_staging": "S1", "to_staging": "S2", "mode": "WALK",
                           "conditions": {"lighting": "NIGHT_DARK"}}]})
        self.assertNotEqual(res["movements"][0]["verdict"], "FAIL")

    def test_q7_minimum_is_close_to_the_sdd_straight_line_estimate(self):
        t = route("RM-CEN-RSP", "RM-URB-OPC", view="ACTOR", actor="CHR-P")["times"]
        straight = dist("RM-CEN-RSP", "RM-URB-OPC") / 2.2
        self.assertGreater(t["min_s"], straight)                      # nunca menor que a linha reta
        self.assertLess(t["min_s"], straight * 1.5)                   # e a via não é absurda

    def test_the_engine_never_names_a_true_exit(self):  # T09 sobre os algoritmos de rota
        blob = json.dumps([cg.escape_routes(fresh(), lid, {"view": "ENGINE"})
                           for lid in ("RM-CEN-SMC", "RM-URB-OPC", "RM-URB-ROW", "RM-CEN-CHP")]).lower()
        self.assertNotIn("true_exit", blob)
        self.assertNotIn("real_exit", blob)

    def test_underdeclared_places_cannot_host_scenes(self):  # T21
        for lid in ("RM-SUB-BTF", "RM-SUB-SC4"):
            res = cg.validate_staging(fresh(), {"staging": [stg("S1", "CHR-P", lid, "D001T10:00")]})
            self.assertTrue(cats(res["findings"], "TR-06"), lid)
            self.assertFalse(cg.reachable(fresh(), "RM-CEN-SMC", lid, {"view": "ENGINE"})["reachable"])

    def test_only_registered_hideout_hosts_hiding(self):  # T24
        bad = cg.validate_staging(fresh(), {"staging": [stg("S1", "CHR-P", "RM-URB-RTS", "D001T10:00", role="HIDING")]})
        self.assertTrue(cats(bad["findings"], "HD-01"))
        ok = cg.validate_staging(fresh(), {"staging": [stg("S1", "CHR-P", "RM-URB-RCH", "D001T10:00", role="HIDING")]})
        self.assertFalse(cats(ok["findings"], "HD-01"))


class MutatedWorld(unittest.TestCase):
    def test_bridge_collapse_isolates_the_east_bank_from_chapter_19(self):  # T18 nos dados reais
        m = fresh()
        m["manifest"]["mutations"] = [{
            "id": "CMUT-TEST", "proposal_ref": "CP-TEST", "cause": "EV-TEST", "chapter": 19, "target": "RM-URB-BBR", "field": "status",
            "previous_state": "ACTIVE", "new_state": "DESTROYED", "canon_effective_from": {"chapter": 19},
            "effects": [{"edge": "EDG-U-023", "previous_state": "OPEN", "new_state": "DESTROYED"},
                        {"edge": "EDG-U-041", "previous_state": "OPEN", "new_state": "DESTROYED"}]}]
        self.assertEqual(cg.check_mutations(m), [])
        self.assertTrue(cg.reachable(m, "RM-CEN-SMC", "RM-URB-PMP", {"chapter": 18, "view": "ACTOR", "actor": "CHR-P"})["reachable"])
        self.assertFalse(cg.reachable(m, "RM-CEN-SMC", "RM-URB-PMP", {"chapter": 19, "view": "ACTOR", "actor": "CHR-P"})["reachable"])   # única travessia do rio


if __name__ == "__main__":
    unittest.main()
