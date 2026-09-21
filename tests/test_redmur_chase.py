"""Testes dos DADOS de SEM ROSTO para o Slice 3 (visibilidade, esconderijos, gargalos, perseguição): as perguntas
4, 5 e 6 da missão §42 / SDD Apêndice C, sobre as vias digitalizadas do Mapa A e a rede subterrânea do inset.

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_redmur_chase -v
"""
from __future__ import annotations

import copy
import sys
import unittest
from collections import defaultdict, deque
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engine" / "scripts"))

import cartography_chase as ch  # noqa: E402
import cartography_graph as cg  # noqa: E402
import check_cartography as cc  # noqa: E402

SEEDS = REPO / "books" / "sem-rosto" / "cartography" / "seeds"
MODEL = cc.load_model(SEEDS)
LOCS = cc.index_by_id(MODEL["locations"])
SDD_TUNNEL = ["EDG-P-001", "EDG-S-001", "EDG-S-003", "EDG-S-004", "EDG-P-004"]     # capela → Root Cellar (SDD 28.1)
SHORT_TUNNEL = ["EDG-P-001", "EDG-S-001", "EDG-S-002", "EDG-P-002"]                 # capela → cemitério


def fresh(knows=None, actor="CHR-P"):
    m = copy.deepcopy(MODEL)
    if knows:
        m["baseline"].append({"knower": actor, "knows": {"ROUTE": list(knows)}})
    return m


def cats(findings, prefix):
    return [f for f in findings if f["category"].startswith(prefix)]


def stg(i, actor, loc, at, chapter=15, **kw):
    return {"id": i, "actor": actor, "location": loc, "at": at, "chapter": chapter, **kw}


class SeedState(unittest.TestCase):
    def test_no_sightline_is_invented(self):
        self.assertEqual(MODEL["sightlines"], [])                      # sightlines só por proposta

    def test_only_one_registered_hideout_and_nothing_is_invented_about_it(self):
        self.assertEqual([h["id"] for h in MODEL["hideouts"]], ["HID-RCH"])
        h = MODEL["hideouts"][0]
        for f in ("capacity", "discoverability", "concealment", "duration_safe"):
            self.assertEqual(h[f], "UNSPECIFIED", f)
        self.assertEqual(cc.check_hideouts(copy.deepcopy(MODEL)), [])

    def test_validator_is_still_clean_with_the_new_rules(self):
        f = cc.validate(copy.deepcopy(MODEL))
        self.assertEqual([(x["category"], x["severity"]) for x in f], [("CG-10 ORPHAN_NODE", "INFO")])


class Q4Visibility(unittest.TestCase):
    """“Esse personagem poderia ter visto outro personagem atravessar a ponte?”"""

    def vis(self, a, b, **ctx):
        return ch.visible_from(copy.deepcopy(MODEL), a, b, ctx)

    def test_pumping_station_to_burn_bridge_by_day_is_undetermined(self):
        r = self.vis("RM-URB-PMP", "RM-URB-BBR")
        self.assertEqual((r["result"], r["basis"]), ("UNDETERMINED", "UNDETERMINED"))
        self.assertTrue(370 <= r["distance_m"][0] <= 400 and 490 <= r["distance_m"][1] <= 510)     # ≈ 500 m (SDD 16.4)
        self.assertEqual(r["threshold_m"], 1500.0)

    def test_the_same_pair_at_night_without_light_is_impossible(self):
        r = self.vis("RM-URB-PMP", "RM-URB-BBR", lighting="NIGHT_DARK")
        self.assertEqual((r["result"], r["reason"]), ("NOT_VISIBLE", "BEYOND_DETECTION_LIMIT"))

    def test_a_lantern_makes_it_undetermined_but_never_recognized(self):
        r = self.vis("RM-URB-PMP", "RM-URB-BBR", lighting="NIGHT_DARK", target_lit=True, recognize=True)
        self.assertEqual((r["result"], r["recognition"]), ("UNDETERMINED", "RECOGNITION_OUT_OF_SCOPE"))

    def test_the_surface_never_sees_the_printed_underground(self):
        for a, b in (("RM-CEN-CHP", "RM-SUB-CHB"), ("RM-URB-OPC", "RM-SUB-CCT"), ("RM-URB-RCH", "RM-SUB-RCP")):
            self.assertEqual(self.vis(a, b)["reason"], "UNDERGROUND", (a, b))

    def test_scene_claims_are_checked(self):
        doc = {"staging": [stg("S1", "CHR-P", "RM-URB-PMP", "D020T23:30", sees=["RM-URB-BBR"], conditions={"lighting": "NIGHT_DARK"}),
                           stg("S2", "CHR-Q", "RM-CEN-CHP", "D020T23:30", sees=["RM-SUB-CHB"])]}
        f = ch.check_sees(copy.deepcopy(MODEL), doc)
        self.assertEqual(sorted(x["category"].split()[0] for x in f), ["VS-01", "VS-02"])


class Q5Hideouts(unittest.TestCase):
    """“Há algum esconderijo acessível sem atravessar área vigiada?”"""

    def test_registered_hideout_is_reachable_without_the_restricted_zone_but_surveillance_is_undecided(self):
        r = ch.accessible_hideouts(copy.deepcopy(MODEL), "RM-URB-OPC", {"view": "ACTOR", "actor": "CHR-P"})
        self.assertEqual(len(r), 1)
        self.assertEqual((r[0]["hideout"], r[0]["reachable"], r[0]["restricted_edges"]), ("HID-RCH", True, []))
        self.assertEqual(r[0]["surveillance"], "UNDETERMINED_SURVEILLANCE")               # nada de vigilância foi declarado
        self.assertIn("RM-URB-RCH", r[0]["surveillance_to_decide"])

    def test_the_answer_becomes_definite_once_surveillance_is_declared(self):
        m = copy.deepcopy(MODEL)
        for lid in ("RM-URB-OPC", "RM-URB-RCH", "RM-CEN-CHP"):
            LOCS_M = cc.index_by_id(m["locations"])
            LOCS_M[lid]["surveillance"] = "NONE"
        r = ch.accessible_hideouts(m, "RM-URB-OPC", {"view": "ACTOR", "actor": "CHR-P"})[0]
        self.assertEqual(r["surveillance"], "NOT_WATCHED_KNOWN")
        cc.index_by_id(m["locations"])["RM-URB-OPC"]["surveillance"] = "PATROLLED"
        self.assertEqual(ch.accessible_hideouts(m, "RM-URB-OPC", {"view": "ACTOR", "actor": "CHR-P"})[0]["surveillance"], "WATCHED")

    def test_from_the_east_bank_the_hideout_needs_the_closed_road_or_the_tunnels(self):
        blocked = ch.accessible_hideouts(copy.deepcopy(MODEL), "RM-URB-ERC", {"view": "ACTOR", "actor": "CHR-P"})[0]
        self.assertFalse(blocked["reachable"])                             # a única saída do X é a East Road fechada
        opened = ch.accessible_hideouts(copy.deepcopy(MODEL), "RM-URB-ERC", {"view": "ACTOR", "actor": "CHR-P", "access_actions": ["EV-1"]})[0]
        self.assertEqual((opened["reachable"], opened["restricted_edges"]), (True, ["EDG-U-035"]))

    def test_a_spontaneous_hiding_place_is_rejected(self):
        res = cg.validate_staging(copy.deepcopy(MODEL), {"staging": [stg("S1", "CHR-P", "RM-URB-RTS", "D020T23:30", role="HIDING")]})
        self.assertTrue(cats(res["findings"], "HD-01"))
        ok = cg.validate_staging(copy.deepcopy(MODEL), {"staging": [stg("S1", "CHR-P", "RM-URB-RCH", "D020T23:30", role="HIDING")]})
        self.assertFalse(cats(ok["findings"], "HD-01"))


class Bottlenecks(unittest.TestCase):
    def test_burn_bridge_is_the_only_link_to_the_east_bank_for_an_ordinary_character(self):
        b = ch.bottlenecks(copy.deepcopy(MODEL), {"view": "ACTOR", "actor": "CHR-P"}, layers={"URBAN"})
        self.assertIn("RM-URB-BBR", b["articulation_points"])
        adj = defaultdict(set)
        for e in MODEL["edges"]:
            if e["id"].startswith("EDG-U-"):
                adj[e["from"]].add(e["to"])
                adj[e["to"]].add(e["from"])
        seen, q = {"RM-CEN-SMC"}, deque(["RM-CEN-SMC"])
        while q:
            n = q.popleft()
            for m in adj[n] - seen - {"RM-URB-BBR"}:
                seen.add(m)
                q.append(m)
        for east in ("RM-URB-PMP", "RM-URB-RSV", "RM-URB-ERC"):
            self.assertNotIn(east, seen, east)                            # sem a ponte, o lado leste some do grafo

    def test_the_engine_view_knows_the_pumping_station_has_a_second_way_in(self):
        self.assertTrue(cg.reachable(copy.deepcopy(MODEL), "RM-CEN-CHP", "RM-URB-PMP", {"view": "ENGINE"})["reachable"])
        self.assertTrue(cg.route(copy.deepcopy(MODEL), "RM-CEN-CHP", "RM-URB-PMP", {"view": "ENGINE"})["found"])
        ordinary = cg.route(copy.deepcopy(MODEL), "RM-CEN-CHP", "RM-URB-PMP", {"view": "ACTOR", "actor": "CHR-P"})
        self.assertIn("EDG-U-033", ordinary["edges"])                     # o personagem comum vai pela ponte


class Q6Chase(unittest.TestCase):
    """“É fisicamente possível realizar essa perseguição?”"""

    def sdd_chase(self, **kw):
        base = {"id": "CHS-0003", "chapter": 15, "lighting": "NIGHT_MOON", "initial_gap_m": 120, "initial_visibility": "VISIBLE",
                "target": {"actor": "CHR-P", "start": "RM-CEN-CHP", "route": SDD_TUNNEL, "profile": "FIT"},
                "pursuer": {"actor": "CHR-X", "start": "RM-CEN-OCP", "end": "RM-URB-RCH", "profile": "FIT"}}
        base.update(kw)
        return base

    def test_the_sdd_example_chase_is_physically_incoherent_and_the_engine_says_why(self):
        r = ch.analyze_chase(fresh(SDD_TUNNEL), self.sdd_chase())
        self.assertEqual({"CH-08", "VS-01"}, {f["category"].split()[0] for f in r["findings"]})
        w = r["target"]["windows"]
        self.assertGreater(w["RM-URB-RCH"][0], 2400)                       # o subsolo capela→Root Cellar leva ≥ 40 min
        self.assertLess(r["pursuer"]["windows"]["RM-URB-RCH"][0], w["RM-URB-RCH"][0])   # o perseguidor chega antes, por cima

    def test_the_timed_claims_of_the_sdd_example_are_impossible(self):
        events = [{"kind": "ARRIVES", "actor": "CHR-P", "at_node": "RM-URB-RCH", "at_s": 1200},
                  {"kind": "ARRIVES", "actor": "CHR-P", "at_node": "RM-JCT-S1", "at_s": 5}]
        r = ch.analyze_chase(fresh(SDD_TUNNEL), self.sdd_chase(declared_events=events, initial_gap_m=800, initial_visibility="UNKNOWN"))
        self.assertEqual(len(cats(r["findings"], "CH-01")), 2)

    def test_secret_route_is_an_escape_the_pursuer_cannot_follow(self):
        r = ch.analyze_chase(fresh(SDD_TUNNEL), self.sdd_chase(initial_gap_m=800, initial_visibility="UNKNOWN"))
        self.assertEqual([e["edge"] for e in r["escape_points"]], SDD_TUNNEL)
        self.assertEqual([h["edge"] for h in r["hidden_transitions"]], SDD_TUNNEL)
        self.assertFalse([n for n in r["pursuer"]["route"] if n.startswith("RM-SUB") or n.startswith("RM-JCT-S")])

    def test_target_without_the_knowledge_cannot_flee_that_way(self):
        r = ch.analyze_chase(fresh(), self.sdd_chase(initial_gap_m=800, initial_visibility="UNKNOWN"))
        self.assertTrue(cats(r["findings"], "CH-06"))

    def test_pursuer_cannot_use_the_tunnel_unless_he_learned_it(self):
        spec = self.sdd_chase(initial_gap_m=800, initial_visibility="UNKNOWN",
                              pursuer={"actor": "CHR-X", "start": "RM-CEN-CHP", "route": SDD_TUNNEL})
        self.assertTrue(cats(ch.analyze_chase(fresh(SDD_TUNNEL), spec)["findings"], "CH-02"))
        both = fresh(SDD_TUNNEL)
        both["baseline"].append({"knower": "CHR-X", "knows": {"ROUTE": SDD_TUNNEL}})
        self.assertFalse(cats(ch.analyze_chase(both, spec)["findings"], "CH-02"))

    def test_a_coherent_short_chase_through_the_chapel_tunnel_passes(self):
        spec = {"id": "CHS-SHORT", "chapter": 15, "lighting": "NIGHT_DARK", "initial_gap_m": 700,
                "target": {"actor": "CHR-P", "start": "RM-CEN-CHP", "route": SHORT_TUNNEL},
                "pursuer": {"actor": "CHR-X", "start": "RM-CEN-OCP", "end": "RM-URB-OPC"}}
        r = ch.analyze_chase(fresh(SHORT_TUNNEL), spec)
        self.assertEqual(r["findings"], [])
        self.assertEqual(len(r["escape_points"]), 4)
        w = r["target"]["windows"]["RM-URB-OPC"]
        self.assertTrue(600 < w[0] < 1200 and w[1] > w[0])                # ≈ 11 a 20 min: subsolo a passo agachado

    def test_the_surface_pursuer_is_faster_than_the_underground_target_on_the_short_route_too(self):
        spec = {"id": "CHS-SHORT", "chapter": 15, "lighting": "DAYLIGHT",
                "target": {"actor": "CHR-P", "start": "RM-CEN-CHP", "route": SHORT_TUNNEL},
                "pursuer": {"actor": "CHR-X", "start": "RM-CEN-CHP", "end": "RM-URB-OPC"}}
        r = ch.analyze_chase(fresh(SHORT_TUNNEL), spec)
        self.assertLess(r["pursuer"]["windows"]["RM-URB-OPC"][0], r["target"]["windows"]["RM-URB-OPC"][0])
        self.assertEqual([p["node"] for p in r["intercept_points"]], ["RM-URB-OPC"])     # o perseguidor pode esperar no destino

    def test_full_scene_validation_on_real_data(self):
        doc = {"staging": [stg("S1", "CHR-P", "RM-CEN-CHP", "D031T22:40", conditions={"lighting": "NIGHT_MOON"}, sees=["RM-CEN-OCP"]),
                           stg("S2", "CHR-P", "RM-URB-RCH", "D031T23:40", role="HIDING")],
               "movements": [{"id": "M1", "actor": "CHR-P", "from_staging": "S1", "to_staging": "S2", "mode": "RUN", "route": SDD_TUNNEL}],
               "chases": [self.sdd_chase(initial_gap_m=800, initial_visibility="UNKNOWN")]}
        r = ch.validate_scene(fresh(SDD_TUNNEL), doc)
        kinds = {f["category"].split()[0] for f in r["findings"]}
        self.assertIn("VS-01", kinds)                                      # a ~550 m à luz da lua (limite 150 m) a capela não vê o Office
        self.assertIn("SUBTERRANEAN_DIMENSIONS_UNSPECIFIED", kinds)        # o trecho subterrâneo tem dimensões não especificadas
        self.assertEqual(len(r["chases"]), 1)


if __name__ == "__main__":
    unittest.main()
