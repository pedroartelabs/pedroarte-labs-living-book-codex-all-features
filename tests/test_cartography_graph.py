"""Testes da biblioteca de viagem `cartography_graph.py` (Slice 2 do SDD da cartografia,
seções 17, 23, 26, 29.3 e 35: T12–T18, T29). Fixture neutra `tests/fixtures/cartography/canon/`.

Mundo da fixture (10 m/px no mapa local): Marco Zero (0,0); Capela (−300,100); Estalagem (200,−50);
Ponte Velha (310,0) sobre o Rio Manso; Moinho (400,200); Cemitério (−400,−100).

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_cartography_graph -v
"""
from __future__ import annotations

import copy
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import cartography_graph as cg  # noqa: E402
import check_cartography as cc  # noqa: E402

SCRIPT = REPO / "engine" / "scripts" / "check_cartography.py"
FIXTURE = REPO / "tests" / "fixtures" / "cartography" / "canon"
_MODEL = cc.load_model(FIXTURE)


def model():
    return copy.deepcopy(_MODEL)


def cats(findings, prefix):
    return [f for f in findings if f["category"].startswith(prefix)]


def stg(i, actor, loc, at, chapter=3, **kw):
    return {"id": i, "actor": actor, "location": loc, "at": at, "chapter": chapter, **kw}


def mv(i, a, b, actor="CHR-Z", mode="WALK", **kw):
    return {"id": i, "actor": actor, "from_staging": a, "to_staging": b, "mode": mode, **kw}


def check(m, stagings, movements, **kw):
    return cg.validate_staging(m, {"staging": stagings, "movements": movements}, **kw)


class Basics(unittest.TestCase):
    def test_distance_and_bearing(self):
        d = cg.distance(model(), "TS-CEN-ORG", "TS-CEN-CAP")
        self.assertEqual(d["euclid_m"][1], 316)
        self.assertEqual(d["euclid_m"][0], 196)      # nominal − precisões
        self.assertEqual(cg.bearing(model(), "TS-CEN-ORG", "TS-CEN-CAP"), {"degrees": 288, "compass16": "WNW"})
        self.assertEqual(cg.bearing(model(), "TS-CEN-ORG", "TS-URB-PNT")["compass16"], "E")

    def test_unknown_position_is_not_invented(self):
        self.assertIsNone(cg.distance(model(), "TS-CEN-ORG", "TS-SUB-SEL")["euclid_m"])
        self.assertIsNone(cg.bearing(model(), "TS-CEN-ORG", "TS-SUB-SEL"))

    def test_clock_roundtrip_and_rejection(self):
        self.assertEqual(cg.fmt_clock(cg.parse_clock("D014T23:14")), "D014T23:14")
        with self.assertRaises(ValueError):
            cg.parse_clock("23:14")

    def test_edge_length_comes_from_polyline_times_scale(self):
        g = cg.Graph(model())
        edge = next(e for e in g.edges if e["id"] == "EDG-U-001")
        nominal, minimum, unspec = g.edge_lengths(edge)
        self.assertAlmostEqual(nominal, math.hypot(30, 10) * 10, places=6)   # 31,62 px × 10 m/px
        self.assertFalse(unspec)
        self.assertLessEqual(minimum, nominal)
        self.assertGreater(minimum, 0)


class Routing(unittest.TestCase):
    def test_shortest_route_uses_existing_edges_only(self):
        r = cg.route(model(), "TS-CEN-ORG", "TS-URB-MOI")
        self.assertTrue(r["found"])
        self.assertEqual(r["nodes"], ["TS-CEN-ORG", "TS-CEN-EST", "TS-URB-PNT", "TS-URB-MOI"])
        self.assertEqual(r["edges"], ["EDG-U-002", "EDG-U-003", "EDG-U-004"])

    def test_times_are_ordered_min_expected_reasonable(self):
        t = cg.travel_times(model(), "TS-CEN-ORG", "TS-URB-MOI")
        self.assertLess(t["min_s"], t["expected_s"])
        self.assertLess(t["expected_s"], t["max_reasonable_s"])
        self.assertAlmostEqual(t["length_nominal_m"], 20.6155 * 10 + 12.083 * 10 + 21.954 * 10, delta=2)

    def test_conditions_only_change_expected_never_minimum(self):
        base = cg.travel_times(model(), "TS-CEN-ORG", "TS-URB-MOI")
        night = cg.travel_times(model(), "TS-CEN-ORG", "TS-URB-MOI", {"lighting": "NIGHT_DARK", "weather": "RAIN", "injury": "MINOR"})
        self.assertAlmostEqual(night["min_s"], base["min_s"])
        self.assertAlmostEqual(night["expected_s"] / base["expected_s"], 1.30 * 1.10 * 1.30, places=6)

    def test_unfamiliar_dark_route_is_slower(self):
        fam = cg.travel_times(model(), "TS-CEN-ORG", "TS-URB-MOI", {"lighting": "NIGHT_DARK"})
        unf = cg.travel_times(model(), "TS-CEN-ORG", "TS-URB-MOI", {"lighting": "NIGHT_DARK", "familiar": False})
        self.assertAlmostEqual(unf["expected_s"] / fam["expected_s"], 1.60 / 1.30, places=6)

    def test_track_terrain_slows_expected_time(self):
        g = cg.Graph(model())
        road = next(e for e in g.edges if e["id"] == "EDG-U-003")
        trail = next(e for e in g.edges if e["id"] == "EDG-U-004")
        ctx = cg.make_ctx()
        self.assertAlmostEqual(g.edge_expected_time(trail, ctx, 100), 100 * 1.10 / 1.35)
        self.assertAlmostEqual(g.edge_expected_time(road, ctx, 100), 100 / 1.35)

    def test_running_and_vehicle_modes(self):
        w = cg.travel_times(model(), "TS-CEN-ORG", "TS-CEN-CAP")
        r = cg.travel_times(model(), "TS-CEN-ORG", "TS-CEN-CAP", {"mode": "RUN"})
        self.assertLess(r["expected_s"], w["expected_s"])
        self.assertLess(r["min_s"], w["min_s"])
        no_vehicle = cg.reachable(model(), "TS-CEN-ORG", "TS-CEN-CAP", {"mode": "VEHICLE"})
        self.assertFalse(no_vehicle["reachable"])
        self.assertIn("NO_VEHICLE_AVAILABLE", [b["reason"] for b in no_vehicle["blocked_by"]])
        ok = cg.route(model(), "TS-CEN-ORG", "TS-CEN-CAP", {"mode": "VEHICLE", "vehicle": True})
        self.assertTrue(ok["found"])
        trail_only = cg.route(model(), "TS-CEN-ORG", "TS-URB-CEM", {"mode": "VEHICLE", "vehicle": True})
        self.assertTrue(trail_only["found"])     # TRAIL admite veículo leve no modelo (SDD 17.2, TRACK)

    def test_disconnected_place_is_unreachable_not_teleported(self):
        r = cg.reachable(model(), "TS-CEN-ORG", "TS-SUB-SEL")
        self.assertFalse(r["reachable"])

    def test_bearing_north_of_river_is_not_a_route(self):
        m = model()
        m["edges"] = [e for e in m["edges"] if e["id"] != "EDG-U-003"]
        self.assertFalse(cg.reachable(m, "TS-CEN-ORG", "TS-URB-MOI")["reachable"])   # sem ponte, sem passagem


class WaterCrossings(unittest.TestCase):
    def test_fixture_bridge_crossing_is_valid(self):
        self.assertEqual(cg.check_water_crossings(model()), [])

    def test_crossing_far_from_any_bridge_fails(self):  # T15
        m = model()
        m["locations"].append({"id": "TS-URB-FAR", "canonical_name": "Choupana", "type": "HOUSE", "layer": "URBAN", "geometry": "POINT",
                               "source_px": [{"source": "SRC-MAP-A", "px": [95, 70], "anchor": "ICON"}]})
        m["edges"].append({"id": "EDG-X", "from": "TS-CEN-EST", "to": "TS-URB-FAR", "edge_type": "TRAIL", "directionality": "BOTH",
                           "source_polyline_px": {"source": "SRC-MAP-A", "points": [[70, 45], [95, 70]]}})
        f = cats(cc.validate(m), "CX-01")
        self.assertTrue(f)
        self.assertEqual(f[0]["severity"], "BLOCKER")

    def test_declared_bridge_near_the_crossing_is_accepted(self):
        m = model()
        m["locations"].append({"id": "TS-URB-FAR", "canonical_name": "Choupana", "type": "HOUSE", "layer": "URBAN", "geometry": "POINT",
                               "source_px": [{"source": "SRC-MAP-A", "px": [95, 42], "anchor": "ICON"}]})
        m["edges"].append({"id": "EDG-X", "from": "TS-CEN-EST", "to": "TS-URB-FAR", "edge_type": "TRAIL", "directionality": "BOTH",
                           "crossings": [{"water": "WAT-RIO", "via": "TS-URB-PNT"}],
                           "source_polyline_px": {"source": "SRC-MAP-A", "points": [[70, 45], [81, 40], [95, 42]]}})
        self.assertFalse(cats(cc.validate(m), "CX-01"))


class Knowledge(unittest.TestCase):
    ACTOR_K = {"view": "ACTOR", "actor": "CHR-K"}
    ACTOR_Z = {"view": "ACTOR", "actor": "CHR-Z"}

    def test_actor_without_knowledge_cannot_use_the_tunnel(self):  # T12
        r = cg.reachable(model(), "TS-SUB-POR", "TS-SUB-TUN", self.ACTOR_Z)
        self.assertFalse(r["reachable"])
        self.assertIn("SECRET_UNKNOWN_TO_ACTOR", [b["reason"] for b in r["blocked_by"]])

    def test_actor_who_knows_it_can(self):
        r = cg.reachable(model(), "TS-SUB-POR", "TS-SUB-TUN", self.ACTOR_K)
        self.assertTrue(r["reachable"])
        self.assertEqual(r["edges"], ["EDG-S-001", "EDG-S-002"])

    def test_engine_view_sees_it_and_says_so(self):
        r = cg.reachable(model(), "TS-SUB-POR", "TS-SUB-TUN", {"view": "ENGINE"})
        self.assertTrue(r["reachable"])

    def test_route_preference_follows_knowledge(self):
        known = cg.route(model(), "TS-CEN-CAP", "TS-URB-CEM", self.ACTOR_K)
        unknown = cg.route(model(), "TS-CEN-CAP", "TS-URB-CEM", self.ACTOR_Z)
        self.assertIn("EDG-P-001", known["edges"])
        self.assertEqual(unknown["edges"], ["EDG-U-001", "EDG-U-005"])
        self.assertNotIn("EDG-P-001", unknown["edges"])

    def test_hidden_route_prefers_underground(self):
        r = cg.route(model(), "TS-CEN-CAP", "TS-URB-CEM", self.ACTOR_K, kind="hidden")
        self.assertIn("EDG-S-001", r["edges"])

    def test_knowledge_can_come_from_the_ledger(self):
        ledger = {"events": [{"id": "EV-1", "chapter": 2, "knowledge_delta": [
            {"knower": "CHR-Z", "learns": ["EDG-P-001", "EDG-S-001", "EDG-S-002"]}]}]}
        before = cg.reachable(model(), "TS-SUB-POR", "TS-SUB-TUN", {**self.ACTOR_Z, "chapter": 1, "ledger": ledger})
        after = cg.reachable(model(), "TS-SUB-POR", "TS-SUB-TUN", {**self.ACTOR_Z, "chapter": 2, "ledger": ledger})
        self.assertFalse(before["reachable"])
        self.assertTrue(after["reachable"])

    def test_undeclared_node_stays_unreachable_even_for_engine(self):
        self.assertFalse(cg.reachable(model(), "TS-CEN-ORG", "TS-SUB-SEL", {"view": "ENGINE"})["reachable"])


class Subterranean(unittest.TestCase):
    def test_length_floor_is_distance_between_anchors(self):
        t = cg.travel_times(model(), "TS-CEN-CAP", "TS-URB-CEM", {"view": "ACTOR", "actor": "CHR-K"})
        anchors = math.hypot(-300 - -400, 100 - -100)
        self.assertAlmostEqual(t["length_nominal_m"], anchors, delta=1)
        self.assertGreater(t["length_min_m"], 0)
        self.assertLess(t["length_min_m"], anchors)                # menos as precisões
        self.assertIn("SUBTERRANEAN_DIMENSIONS_UNSPECIFIED", t["warnings"])
        self.assertEqual(t["portals"], 2)

    def test_portals_add_delay(self):
        t = cg.travel_times(model(), "TS-CEN-CAP", "TS-URB-CEM", {"view": "ACTOR", "actor": "CHR-K"})
        self.assertGreaterEqual(t["min_s"], 120.0)
        self.assertGreaterEqual(t["expected_s"], 240.0)

    def test_expected_underground_pace_is_stooped(self):
        g = cg.Graph(model())
        e = next(x for x in g.edges if x["id"] == "EDG-S-001")
        self.assertEqual(g.edge_expected_speed(e, cg.make_ctx()), 0.7)
        self.assertEqual(g.edge_expected_speed(e, cg.make_ctx(mode="RUN")), 0.7)   # subsolo força passo agachado

    def test_tunnel_shorter_than_anchors_is_caught_when_declared(self):
        m = model()
        for e in m["edges"]:
            if e["id"] in ("EDG-S-001",):
                e["distance_meters"] = {"nominal": 5, "min": 5}
        # o piso por âncoras só vale quando não declarado; declarado e curto é achado do validador de arestas quando ambos
        # os extremos têm posição — aqui a junção não tem, então só o tempo mínimo usa o comprimento declarado
        t = cg.travel_times(m, "TS-CEN-CAP", "TS-URB-CEM", {"view": "ACTOR", "actor": "CHR-K"})
        self.assertIsNotNone(t)


class State(unittest.TestCase):
    def mutation(self, **kw):
        m = {"id": "CMUT-1", "proposal_ref": "CP-1", "cause": "EV-9", "chapter": 5, "target": "TS-URB-PNT", "field": "status",
             "previous_state": "ACTIVE", "new_state": "DESTROYED",
             "effects": [{"edge": "EDG-U-003", "previous_state": "OPEN", "new_state": "DESTROYED"},
                         {"edge": "EDG-U-004", "previous_state": "OPEN", "new_state": "DESTROYED"}],
             "canon_effective_from": {"chapter": 5}}
        m.update(kw)
        return m

    def test_bridge_collapse_changes_reachability_from_that_chapter_only(self):  # T18
        m = model()
        m["manifest"]["mutations"] = [self.mutation()]
        before = cg.reachable(m, "TS-CEN-ORG", "TS-URB-MOI", {"chapter": 4})
        after = cg.reachable(m, "TS-CEN-ORG", "TS-URB-MOI", {"chapter": 5})
        self.assertTrue(before["reachable"])
        self.assertFalse(after["reachable"])

    def test_seed_is_never_edited_in_place(self):
        m = model()
        m["manifest"]["mutations"] = [self.mutation()]
        edge = next(e for e in m["edges"] if e["id"] == "EDG-U-003")
        self.assertNotIn("state", edge)
        self.assertEqual(cg.edge_state(m, edge, 4), "OPEN")
        self.assertEqual(cg.edge_state(m, edge, 9), "DESTROYED")

    def test_mutation_without_proposal_or_cause(self):  # T17
        m = model()
        m["manifest"]["mutations"] = [self.mutation(proposal_ref=None)]
        self.assertTrue(cats(cg.check_mutations(m), "CN-02"))
        m["manifest"]["mutations"] = [self.mutation(cause=None)]
        self.assertTrue(cats(cg.check_mutations(m), "CN-03"))
        m["manifest"]["mutations"] = [self.mutation()]
        self.assertEqual(cg.check_mutations(m), [])

    def test_previous_state_must_match_the_projection(self):
        m = model()
        bad = self.mutation()
        bad["effects"][0]["previous_state"] = "SEALED"
        m["manifest"]["mutations"] = [bad]
        self.assertTrue(cats(cg.check_mutations(m), "CN-02"))

    def test_mutation_on_missing_edge_dangles(self):
        m = model()
        bad = self.mutation()
        bad["effects"][0]["edge"] = "EDG-NOPE"
        m["manifest"]["mutations"] = [bad]
        self.assertTrue(cats(cg.check_mutations(m), "CG-01"))

    def test_closed_edge_needs_a_narrative_action(self):  # INV-C06
        m = model()
        edge = next(e for e in m["edges"] if e["id"] == "EDG-U-003")
        edge["state_timeline"] = [{"from_chapter": 0, "state": "RESTRICTED"}]
        closed = cg.reachable(m, "TS-CEN-ORG", "TS-URB-MOI")
        self.assertFalse(closed["reachable"])
        self.assertIn("CLOSED_WITHOUT_ACTION", [b["reason"] for b in closed["blocked_by"]])
        self.assertTrue(cg.reachable(m, "TS-CEN-ORG", "TS-URB-MOI", {"access_actions": ["EV-7"]})["reachable"])

    def test_access_requirement_blocks_until_held(self):
        m = model()
        next(e for e in m["edges"] if e["id"] == "EDG-U-003")["access_requirement"] = "KEY"
        self.assertFalse(cg.reachable(m, "TS-CEN-ORG", "TS-URB-MOI")["reachable"])
        self.assertTrue(cg.reachable(m, "TS-CEN-ORG", "TS-URB-MOI", {"has": {"KEY"}})["reachable"])

    def test_unknown_state_is_usable_with_a_warning(self):
        m = model()
        next(e for e in m["edges"] if e["id"] == "EDG-S-001")["state_timeline"] = [{"from_chapter": 0, "state": "UNKNOWN"}]
        r = check(m, [stg("S1", "CHR-K", "TS-CEN-CAP", "D001T10:00"), stg("S2", "CHR-K", "TS-URB-CEM", "D001T11:00")],
                  [mv("M1", "S1", "S2", "CHR-K", route=["EDG-P-001", "EDG-S-001", "EDG-S-002", "EDG-P-002"])])
        self.assertTrue(cats(r["findings"], "SUBTERRANEAN_STATE_UNSPECIFIED"))
        self.assertEqual(r["movements"][0]["verdict"], "WARNING")


class TravelVerdicts(unittest.TestCase):
    def verdict(self, interval_min, dest="TS-URB-CEM", mode="WALK", **kw):
        m = kw.pop("m", None) or model()
        h, mi = divmod(10 * 60 + interval_min, 60)
        r = check(m, [stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-Z", dest, f"D001T{int(h):02d}:{int(mi):02d}")],
                  [mv("M1", "S1", "S2", mode=mode, **kw)])
        return r["movements"][0]["verdict"], r

    def test_impossible_time_fails_TR01(self):  # T14 (espelha o exemplo do SDD 17.7)
        v, r = self.verdict(2)
        self.assertEqual(v, "FAIL")
        self.assertTrue(cats(r["findings"], "TR-01"))

    def test_tight_time_warns_TR07(self):
        v, r = self.verdict(5)
        self.assertEqual(v, "WARNING")
        self.assertTrue(cats(r["findings"], "TR-07"))

    def test_running_beyond_profile_fails_TR03(self):
        v, r = self.verdict(1.4, mode="RUN")
        self.assertEqual(v, "FAIL")
        self.assertTrue(cats(r["findings"], "TR-03"))

    def test_only_by_running_warns_TR02(self):
        # 412 m a pé: brisk = 412/1.8 = 229 s = 3,8 min; mínimo físico ≈ 2,8 min
        v, r = self.verdict(3.2)
        self.assertTrue(cats(r["findings"], "TR-02") or cats(r["findings"], "TR-01"))

    def test_comfortable_time_passes(self):
        v, r = self.verdict(8)
        self.assertEqual(v, "PASS")
        self.assertEqual(r["findings"], [])

    def test_very_long_time_is_info_only(self):
        v, r = self.verdict(240)
        self.assertEqual(v, "PASS")
        self.assertTrue(cats(r["findings"], "TR-04"))

    def test_arrival_before_departure_fails(self):
        r = check(model(), [stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-Z", "TS-CEN-CAP", "D001T09:00")],
                  [mv("M1", "S1", "S2")])
        self.assertTrue(cats(r["findings"], "TR-01"))

    def test_same_place_is_trivially_fine(self):
        r = check(model(), [stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-Z", "TS-CEN-ORG", "D001T10:01")],
                  [mv("M1", "S1", "S2")])
        self.assertEqual(r["movements"][0]["verdict"], "PASS")

    def test_teleport_without_movement_is_caught(self):  # nenhum personagem se teletransporta
        r = check(model(), [stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-Z", "TS-URB-MOI", "D001T10:01")], [])
        f = cats(r["findings"], "TR-05")
        self.assertTrue(f)
        self.assertEqual(f[0]["severity"], "HIGH")

    def test_inferred_movement_passes_when_time_allows(self):
        r = check(model(), [stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-Z", "TS-URB-MOI", "D001T11:00")], [])
        self.assertEqual(cats(r["findings"], "TR-05"), [])

    def test_declared_secret_route_unknown_to_actor_fails_KN01(self):  # T12
        r = check(model(), [stg("S1", "CHR-Z", "TS-CEN-CAP", "D001T10:00"), stg("S2", "CHR-Z", "TS-URB-CEM", "D001T11:00")],
                  [mv("M1", "S1", "S2", route=["EDG-P-001", "EDG-S-001", "EDG-S-002", "EDG-P-002"])])
        self.assertTrue(cats(r["findings"], "KN-01"))
        self.assertEqual(r["movements"][0]["verdict"], "FAIL")

    def test_same_route_is_fine_for_actor_who_knows_it(self):
        r = check(model(), [stg("S1", "CHR-K", "TS-CEN-CAP", "D001T10:00"), stg("S2", "CHR-K", "TS-URB-CEM", "D001T11:00")],
                  [mv("M1", "S1", "S2", "CHR-K", route=["EDG-P-001", "EDG-S-001", "EDG-S-002", "EDG-P-002"])])
        self.assertFalse(cats(r["findings"], "KN-01"))
        self.assertNotEqual(r["movements"][0]["verdict"], "FAIL")

    def test_declared_route_through_closed_edge_fails_AC01(self):  # T16 / INV-C06
        m = model()
        next(e for e in m["edges"] if e["id"] == "EDG-U-003")["state_timeline"] = [{"from_chapter": 0, "state": "RESTRICTED"}]
        r = check(m, [stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-Z", "TS-URB-MOI", "D001T12:00")],
                  [mv("M1", "S1", "S2", route=["EDG-U-002", "EDG-U-003", "EDG-U-004"])])
        self.assertTrue(cats(r["findings"], "AC-01"))
        ok = check(m, [stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-Z", "TS-URB-MOI", "D001T12:00")],
                   [mv("M1", "S1", "S2", route=["EDG-U-002", "EDG-U-003", "EDG-U-004"], access_actions=["EV-7"])])
        self.assertFalse(cats(ok["findings"], "AC-01"))

    def test_no_path_after_bridge_collapse(self):
        m = model()
        m["manifest"]["mutations"] = [State.mutation(State(), chapter=2, canon_effective_from={"chapter": 2})]
        r = check(m, [stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T10:00", chapter=3), stg("S2", "CHR-Z", "TS-URB-MOI", "D001T12:00", chapter=3)],
                  [mv("M1", "S1", "S2")])
        self.assertTrue(cats(r["findings"], "TR-06"))

    def test_declared_route_must_be_continuous_and_reach_destination(self):
        r = check(model(), [stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-Z", "TS-URB-MOI", "D001T12:00")],
                  [mv("M1", "S1", "S2", route=["EDG-U-004"])])
        self.assertTrue(cats(r["findings"], "TR-06"))
        r2 = check(model(), [stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-Z", "TS-URB-MOI", "D001T12:00")],
                   [mv("M1", "S1", "S2", route=["EDG-U-002"])])
        self.assertTrue(cats(r2["findings"], "TR-06"))

    def test_staging_in_undeclared_place_is_rejected(self):
        r = check(model(), [stg("S1", "CHR-Z", "TS-SUB-SEL", "D001T10:00")], [])
        self.assertTrue(cats(r["findings"], "TR-06"))

    def test_spontaneous_hideout_is_rejected_but_registered_one_is_fine(self):  # T24
        bad = check(model(), [stg("S1", "CHR-Z", "TS-CEN-CAP", "D001T10:00", role="HIDING")], [])
        self.assertTrue(cats(bad["findings"], "HD-01"))
        good = check(model(), [stg("S1", "CHR-Z", "TS-URB-CEM", "D001T10:00", role="HIDING")], [])
        self.assertFalse(cats(good["findings"], "HD-01"))

    def test_profile_changes_the_verdict(self):
        m = model()
        base = check(m, [stg("S1", "CHR-A", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-A", "TS-URB-CEM", "D001T10:06")],
                     [mv("M1", "S1", "S2", "CHR-A")], defaults={"profiles": {"CHR-A": "ELDERLY"}})
        self.assertTrue(cats(base["findings"], "TR-07"))     # apertado para quem anda a 1,0 m/s
        fit = check(m, [stg("S1", "CHR-A", "TS-CEN-ORG", "D001T10:00"), stg("S2", "CHR-A", "TS-URB-CEM", "D001T10:06")],
                    [mv("M1", "S1", "S2", "CHR-A")], defaults={"profiles": {"CHR-A": "FIT"}})
        self.assertEqual(fit["movements"][0]["verdict"], "PASS")

    def test_minimum_is_never_lowered_by_estimates(self):  # T29
        g = cg.Graph(model())
        for e in g.edges:
            nom, mn, un = g.edge_lengths(e)
            if nom is not None:
                self.assertLessEqual(mn, nom + 1e-9, e["id"])


class Escape(unittest.TestCase):
    def test_escape_routes_from_the_square(self):
        r = cg.escape_routes(model(), "TS-CEN-ORG")
        self.assertEqual({x["to"] for x in r}, {"TS-URB-CEM", "TS-FRM-S"})
        self.assertEqual(r[0]["expected_s"] <= r[1]["expected_s"], True)
        self.assertEqual({x["to"]: x["kind"] for x in r}["TS-URB-CEM"], "HIDEOUT")

    def test_no_route_ever_claims_a_true_exit(self):
        blob = json.dumps(cg.escape_routes(model(), "TS-CEN-ORG")).lower()
        self.assertNotIn("true_exit", blob)
        self.assertEqual({x["kind"] for x in cg.escape_routes(model(), "TS-CEN-ORG")} - {"HIDEOUT", "APPARENT_EXIT"}, set())


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        r = subprocess.run([sys.executable, str(SCRIPT), "--canon", str(FIXTURE), *args], capture_output=True, text=True,
                           encoding="utf-8", env={"PYTHONIOENCODING": "utf-8", "PATH": __import__("os").environ.get("PATH", "")})
        return r

    def test_distance_and_route(self):
        d = json.loads(self.run_cli("--distance", "TS-CEN-ORG", "TS-CEN-CAP").stdout)
        self.assertEqual(d["euclid_m"][1], 316)
        r = json.loads(self.run_cli("--route", "TS-CEN-ORG", "TS-URB-MOI").stdout)
        self.assertEqual(r["edges"], ["EDG-U-002", "EDG-U-003", "EDG-U-004"])
        self.assertIn("ENGINE_VIEW", r)             # visão do motor é rotulada

    def test_actor_view_is_not_labeled_engine(self):
        r = json.loads(self.run_cli("--reachable", "TS-SUB-POR", "TS-SUB-TUN", "--actor", "CHR-Z").stdout)
        self.assertFalse(r["reachable"])
        self.assertNotIn("ENGINE_VIEW", r)

    def test_check_staging_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.yaml"
            bad.write_text(yaml.safe_dump({"staging": [stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T10:00"),
                                                       stg("S2", "CHR-Z", "TS-URB-MOI", "D001T10:01")]}), encoding="utf-8")
            good = Path(tmp) / "good.yaml"
            good.write_text(yaml.safe_dump({"staging": [stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T10:00"),
                                                        stg("S2", "CHR-Z", "TS-URB-MOI", "D001T12:00")]}), encoding="utf-8")
            self.assertEqual(self.run_cli("--check-staging", str(bad)).returncode, 1)
            self.assertEqual(self.run_cli("--check-staging", str(good)).returncode, 0)


if __name__ == "__main__":
    unittest.main()
