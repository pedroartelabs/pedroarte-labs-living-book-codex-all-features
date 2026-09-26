"""Dados regionais de SEM ROSTO (Mapa B, Slice 6): vias digitalizadas, escala, ligações entre escalas, rotas contestadas,
saídas e a proteção do mistério sobre elas.

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_redmur_regional -v
"""
from __future__ import annotations

import collections
import copy
import json
import math
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import cartography_graph as cg  # noqa: E402
import cartography_maps as mp  # noqa: E402
import check_cartography as cc  # noqa: E402

M = cc.load_model(REPO / "books" / "sem-rosto" / "cartography" / "seeds")
MPP_B = 55.86
REGIONAL = [e for e in M["edges"] if e["id"].startswith("EDG-R-")]
LINKS = [e for e in M["edges"] if e["id"].startswith("EDG-L-")]


def model():
    return copy.deepcopy(M)


class Digitization(unittest.TestCase):
    def test_manifest_marks_regional_as_digitized(self):
        self.assertEqual(M["manifest"]["metadata"]["edges_digitized"], {"URBAN": True, "SUBTERRANEAN": True, "REGIONAL": True})

    def test_validator_is_clean(self):
        self.assertEqual(cc.validate(model()), [])

    def test_lengths_derive_from_polyline_and_the_b_scale(self):
        for e in REGIONAL:
            pts = e["source_polyline_px"]["points"]
            px = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
            self.assertAlmostEqual(e["distance_meters"]["nominal"], px * MPP_B, delta=1.0, msg=e["id"])
            self.assertLessEqual(e["distance_meters"]["min"], e["distance_meters"]["nominal"])

    def test_nothing_is_confirmed_visual_before_human_review(self):
        self.assertEqual({e["confidence"] for e in REGIONAL} - {"PROBABLE", "UNCERTAIN"}, set())

    def test_every_regional_edge_records_how_it_was_traced(self):
        for e in REGIONAL:
            if "digitization" in e:
                self.assertTrue(0 <= e["digitization"]["road_fraction"] <= 1)

    def test_edges_are_drawn_on_map_b_only(self):
        for e in REGIONAL:
            self.assertEqual(e["source_polyline_px"]["source"], "SRC-MAP-B")

    def test_no_edge_uses_the_frame_panels(self):
        for e in REGIONAL:
            for x, y in e["source_polyline_px"]["points"]:
                self.assertFalse(1195 <= x <= 1448 and 290 <= y <= 1000, e["id"])       # painel do registro/rotas


class ScaleSeams(unittest.TestCase):
    def test_places_on_both_maps_are_linked_by_zero_length_frame_links(self):
        self.assertGreaterEqual(len(LINKS), 12)
        for e in LINKS:
            self.assertEqual(e["edge_type"], "FRAME_LINK")
            self.assertEqual(e["distance_meters"]["nominal"], 0)
            self.assertEqual(e["confidence"], "UNCERTAIN")

    def test_a_link_never_joins_two_places_that_are_not_the_same(self):
        locs = cc.index_by_id(M["locations"])
        for e in LINKS:
            a, b = locs[e["from"]], locs[e["to"]]
            self.assertEqual(a["layer"], "REGIONAL")
            self.assertIn(b["layer"], ("URBAN", "REGIONAL"))
            if b["layer"] == "URBAN":
                key = a["canonical_name"].split(" (")[0].split(":")[0]
                self.assertTrue(cc.normalize_name(key)[:6] in cc.normalize_name(b["canonical_name"]) or e["to"] in ("RM-CEN-SMC", "RM-FRM-A-S"),
                                (e["id"], a["canonical_name"], b["canonical_name"]))

    def test_metric_position_never_comes_from_the_schematic_core(self):
        proj = cc.project_all(model())
        smc = proj["RM-CEN-SMC"]
        self.assertEqual((smc["x"], smc["y"]), (0.0, 0.0))
        self.assertEqual(smc["source"], "SRC-MAP-A")

    def test_regional_villages_are_reachable_from_the_cross(self):
        g = cg.Graph(model())
        ctx = cg._ctx(model(), cg.make_ctx())
        seen, q = {"RM-CEN-SMC"}, collections.deque(["RM-CEN-SMC"])
        while q:
            n = q.popleft()
            for nb, e in g.adj.get(n, []):
                if g.usable(e, ctx)[0] and nb not in seen:
                    seen.add(nb)
                    q.append(nb)
        villages = [l["id"] for l in M["locations"] if l["id"].startswith("RM-REG-") and l["type"] in ("VILLAGE", "HAMLET", "FARM", "COTTAGE", "BOTHY", "TOWN")]
        self.assertEqual([v for v in villages if v not in seen], [])

    def test_regional_trip_takes_hours_not_minutes(self):
        t = cg.travel_times(model(), "RM-CEN-RSP", "RM-REG-MSG", ctx=cg.make_ctx())
        self.assertGreater(t["length_min_m"], 20000)
        self.assertGreater(t["expected_s"], 5 * 3600)


class WaterAndBridges(unittest.TestCase):
    def test_ash_burn_is_drawn_on_both_maps(self):
        ash = next(l for l in M["locations"] if l["id"] == "WAT-ASH")
        self.assertEqual({p["source"] for p in ash["polyline_px"]}, {"SRC-MAP-A", "SRC-MAP-B"})

    def test_water_crossings_are_compared_only_within_the_same_map(self):
        self.assertEqual(cg.check_water_crossings(model()), [])

    def test_a_road_across_the_b_river_without_a_bridge_is_rejected(self):
        m = model()
        m["locations"] = [l for l in m["locations"] if l["id"] != "RM-JCT-B-BBR"]
        m["edges"] = [e for e in m["edges"] if "RM-JCT-B-BBR" not in (e.get("from"), e.get("to"))]
        m["edges"].append({"id": "EDG-X-CROSS", "from": "RM-REG-BTC", "to": "RM-URB-ROW", "edge_type": "ROAD", "directionality": "BOTH",
                           "source_polyline_px": {"source": "SRC-MAP-B", "points": [[960, 570], [1004, 440], [1050, 345]]}})
        self.assertTrue([f for f in cg.check_water_crossings(m) if f["category"].startswith("CX-01")])

    def test_burn_bridge_seam_is_a_bridge_over_the_ash_burn(self):
        seam = next(l for l in M["locations"] if l["id"] == "RM-JCT-B-BBR")
        self.assertIn("BRIDGE", seam["type"])
        self.assertEqual(seam["crosses"], ["WAT-ASH"])


class RoutesAndExits(unittest.TestCase):
    ROUTES = {r["id"]: r for r in M["routes"]}

    def test_drawn_stretches_of_the_contested_routes_are_digitized(self):
        for rid in ("RTE-B-R3-STR", "RTE-B-R3-GLN", "RTE-B-QM", "RTE-B-CHP", "RTE-B-R17"):
            r = self.ROUTES[rid]
            self.assertEqual(r["trace_status"], "DIGITIZED", rid)
            self.assertEqual(r["continuation_beyond_drawn"], "UNKNOWN", rid)
            self.assertEqual(len(r["edges"]), 1)

    def test_route_lines_are_facts_of_the_drawing_and_never_interpreted(self):
        for rid in ("RTE-B-R3-STR", "RTE-B-R17"):
            e = next(x for x in M["edges"] if x["id"] == self.ROUTES[rid]["edges"][0])
            self.assertEqual(e["route_membership"], [rid])
            self.assertEqual(e["confidence"], "UNCERTAIN")
            self.assertIn("continuação é UNKNOWN", e["note"])

    def test_unmapped_route_markers_stay_undigitized(self):
        for rid in ("RTE-B-R4", "RTE-B-R7", "RTE-B-R13"):
            self.assertEqual(self.ROUTES[rid]["trace_status"], "TO_DIGITIZE", rid)      # só o marcador foi lido; nada inventado

    def test_route_mysteries_remain_unresolved(self):
        for r in M["route_mysteries"]:
            self.assertEqual(r["resolution_state"], "UNRESOLVED")
            self.assertIsNone(r.get("truth_ref"))

    def test_every_exit_is_anchored_or_explicitly_marked(self):
        for e in mp.exits_query(model())["exits"]:
            self.assertTrue(e["frame_portal"] or e["frame_status"] in cc.EXIT_FRAME_STATUS, e["id"])

    def test_exits_with_edges_reach_the_frame_or_say_they_do_not(self):
        by = {x["id"]: x for x in M["exits"]}
        for xid in ("EXT-03", "EXT-04", "EXT-05", "EXT-06", "EXT-07", "EXT-08", "EXT-10"):
            self.assertTrue(by[xid]["edges"], xid)
            self.assertTrue(by[xid]["frame_portal"], xid)
        self.assertEqual(by["EXT-09"]["frame_status"], "ENDS_BEFORE_FRAME")
        self.assertEqual(by["EXT-02"]["frame_status"], "ENDS_BEFORE_FRAME")

    def test_exit_edges_end_at_the_frame_portal(self):
        edges = cc.index_by_id(M["edges"])
        for x in M["exits"]:
            if x.get("frame_portal") and x.get("edges") and x["id"] != "EXT-01":
                self.assertTrue(any(x["frame_portal"] in (edges[i]["from"], edges[i]["to"]) for i in x["edges"]), x["id"])

    def test_the_mystery_gate_still_holds(self):
        r = mp.exit_truth(model())
        self.assertEqual(r["status"], "POINTERS_ONLY")
        self.assertTrue(all(x["truth_ref"] is None for x in r["exits"]))
        for e in mp.exits_query(model())["exits"]:
            self.assertEqual(e["physical"]["beyond_frame"], "OFF_MAP")
        self.assertIsNone(cc.TRUE_EXIT_RE.search(json.dumps(mp.exits_query(model()), ensure_ascii=False)))

    def test_named_roads_list_their_regional_edges(self):
        roads = {r["id"]: r for r in M["roads"]}
        for rid in ("ROAD-E13", "ROAD-B-W", "ROAD-B-SW1", "ROAD-B-SW2", "ROAD-B-R13", "ROAD-B-SE2", "ROAD-B-KEL", "ROAD-B-R3N"):
            self.assertTrue(roads[rid]["edges"], rid)
        self.assertTrue(roads["ROAD-SGR"]["edges"])                                    # o rebuild regional não apagou as vias urbanas


class Reader(unittest.TestCase):
    def test_reader_baseline_now_includes_the_regional_map(self):
        c = mp.reader_map(model(), 0)["counts"]
        self.assertGreater(c["SEEN_ON_MAP"], 240)
        self.assertEqual(c["UNSEEN"], 3)              # Black Thistle, Sealed Crypt IV e a ligação inferida (S4)


if __name__ == "__main__":
    unittest.main()
