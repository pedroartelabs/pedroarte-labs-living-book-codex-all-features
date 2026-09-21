"""Testes de `cartography_chase.py` (Slice 3 do SDD da cartografia, seções 16, 18, 28, 29.3 e 35: T25, T26, T27,
HD-01..04, VS-01..03, CH-01..08). Fixture neutra `tests/fixtures/cartography/canon/`.

Mundo da fixture (10 m/px no mapa local): Marco Zero (0,0); Capela (−300,100); Estalagem (200,−50);
Ponte Velha (310,0) sobre o Rio Manso; Moinho (400,200); Cemitério (−400,−100); passagem secreta
Capela↔Cemitério (só CHR-K a conhece); Cemitério é o único esconderijo registrado.

Rodar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest tests.test_cartography_chase -v
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

import cartography_chase as ch  # noqa: E402
import cartography_graph as cg  # noqa: E402
import check_cartography as cc  # noqa: E402

SCRIPT = REPO / "engine" / "scripts" / "check_cartography.py"
FIXTURE = REPO / "tests" / "fixtures" / "cartography" / "canon"
_MODEL = cc.load_model(FIXTURE)
TUNNEL = ["EDG-P-001", "EDG-S-001", "EDG-S-002", "EDG-P-002"]


def model():
    return copy.deepcopy(_MODEL)


def cats(findings, prefix):
    return [f for f in findings if f["category"].startswith(prefix)]


def stg(i, actor, loc, at, chapter=3, **kw):
    return {"id": i, "actor": actor, "location": loc, "at": at, "chapter": chapter, **kw}


def chase(**kw):
    base = {"id": "CHS-1", "chapter": 3, "lighting": "DAYLIGHT",
            "target": {"actor": "CHR-K", "start": "TS-CEN-CAP", "end": "TS-URB-CEM"},
            "pursuer": {"actor": "CHR-Z", "start": "TS-CEN-ORG", "end": "TS-URB-CEM"}}
    base.update(kw)
    return base


def run(ch_spec, m=None, ledger=None):
    return ch.analyze_chase(m or model(), ch_spec, ledger)


# ---------------------------------------------------------------------------
# visibilidade
# ---------------------------------------------------------------------------

class Visibility(unittest.TestCase):
    def vis(self, a, b, **ctx):
        return ch.visible_from(model(), a, b, ctx)

    def test_declared_sightline_wins_and_is_lighting_specific(self):
        self.assertEqual((self.vis("TS-CEN-EST", "TS-URB-PNT")["result"], self.vis("TS-CEN-EST", "TS-URB-PNT")["basis"]), ("VISIBLE", "DECLARED"))
        self.assertEqual(self.vis("TS-URB-PNT", "TS-CEN-EST", lighting="NIGHT_MOON")["result"], "PARTIAL")     # simétrica
        self.assertEqual(self.vis("TS-CEN-EST", "TS-URB-PNT", lighting="NIGHT_DARK")["result"], "NOT_VISIBLE")
        self.assertEqual(self.vis("TS-CEN-EST", "TS-URB-PNT", lighting="OVERCAST")["result"], "VISIBLE")       # OVERCAST usa a chave DAYLIGHT

    def test_underground_is_never_seen_from_the_surface(self):  # T25 / VS-02
        for lighting in ("DAYLIGHT", "NIGHT_MOON"):
            r = self.vis("TS-CEN-CAP", "TS-SUB-POR", lighting=lighting)
            self.assertEqual((r["result"], r["reason"]), ("NOT_VISIBLE", "UNDERGROUND"))
        self.assertEqual(self.vis("TS-SUB-POR", "TS-URB-CEM")["result"], "NOT_VISIBLE")

    def test_beyond_the_night_limit_is_not_visible(self):  # T25
        self.assertEqual(self.vis("TS-CEN-ORG", "TS-CEN-CAP", lighting="NIGHT_DARK")["result"], "NOT_VISIBLE")   # 196–316 m > 30 m
        self.assertEqual(self.vis("TS-CEN-ORG", "TS-CEN-CAP", lighting="NIGHT_MOON")["result"], "NOT_VISIBLE")   # 196 m > 150 m

    def test_within_limit_without_classified_obstacles_is_undetermined_not_visible(self):
        r = self.vis("TS-CEN-ORG", "TS-CEN-CAP")
        self.assertEqual((r["result"], r["basis"], r["reason"]), ("UNDETERMINED", "UNDETERMINED", "WITHIN_LIMIT_OBSTACLES_UNCLASSIFIED"))
        self.assertEqual(r["threshold_m"], 1500.0)

    def test_a_carried_light_extends_the_limit(self):
        dark = self.vis("TS-CEN-ORG", "TS-CEN-CAP", lighting="NIGHT_DARK")
        lit = self.vis("TS-CEN-ORG", "TS-CEN-CAP", lighting="NIGHT_DARK", target_lit=True)
        self.assertEqual(dark["result"], "NOT_VISIBLE")
        self.assertEqual((lit["result"], lit["threshold_m"]), ("UNDETERMINED", 2000.0))

    def test_fog_caps_the_limit_even_for_a_lit_target(self):
        self.assertEqual(self.vis("TS-CEN-ORG", "TS-CEN-CAP", weather="FOG")["result"], "NOT_VISIBLE")                     # 196 m > 60 m
        self.assertEqual(self.vis("TS-CEN-ORG", "TS-CEN-CAP", weather="FOG", lighting="NIGHT_DARK", target_lit=True)["result"], "NOT_VISIBLE")  # > 150 m
        self.assertEqual(self.vis("TS-CEN-EST", "TS-CEN-ORG", weather="FOG")["result"], "NOT_VISIBLE")                      # 206−120 = 86 m > 60 m

    def test_far_places_are_not_visible_by_day(self):
        self.assertEqual(self.vis("TS-CEN-ORG", "TS-REG-ALD")["reason"], "BEYOND_DETECTION_LIMIT")

    def test_detecting_is_not_recognizing(self):
        r = self.vis("TS-CEN-ORG", "TS-CEN-CAP", recognize=True)
        self.assertEqual(r["recognition"], "RECOGNITION_OUT_OF_SCOPE")
        self.assertNotIn("recognition", self.vis("TS-CEN-ORG", "TS-CEN-CAP"))

    def test_same_place_and_unknown_places(self):
        self.assertEqual(self.vis("TS-CEN-ORG", "TS-CEN-ORG")["result"], "VISIBLE")
        self.assertEqual(self.vis("TS-CEN-ORG", "NOPE")["reason"], "UNKNOWN_LOCATION")
        m = model()
        m["locations"].append({"id": "TS-URB-NOPOS", "canonical_name": "Sem posição", "type": "HOUSE", "layer": "URBAN", "position": "UNKNOWN"})
        self.assertEqual(ch.visible_from(m, "TS-CEN-ORG", "TS-URB-NOPOS")["reason"], "POSITION_UNKNOWN")

    def test_manifest_can_override_thresholds(self):
        m = model()
        m["manifest"]["settings"] = {"detection_thresholds_m": {"NIGHT_DARK": 500}}
        self.assertEqual(ch.visible_from(m, "TS-CEN-ORG", "TS-CEN-CAP", {"lighting": "NIGHT_DARK"})["result"], "UNDETERMINED")

    def test_sightline_seed_validation(self):
        m = model()
        m["sightlines"].append({"id": "SGT-X", "from": "TS-CEN-ORG", "to": "NOPE", "result": {"DAYLIGHT": "MAYBE"}})
        f = ch.check_sightlines(m)
        self.assertTrue(cats(f, "CG-01"))
        self.assertTrue(cats(f, "INVALID_ENUM"))
        self.assertTrue(cats(f, "SIGHTLINE_WITHOUT_SOURCE"))
        self.assertEqual(ch.check_sightlines(model()), [])
        self.assertTrue(cats(cc.validate(m), "SIGHTLINE_WITHOUT_SOURCE"))


class SeesClaims(unittest.TestCase):
    def check(self, stagings):
        return ch.check_sees(model(), {"staging": stagings})

    def test_impossible_sight_fails_VS01(self):  # T25
        f = self.check([stg("S1", "CHR-Z", "TS-CEN-EST", "D001T22:00", sees=["TS-URB-PNT"], conditions={"lighting": "NIGHT_DARK"})])
        self.assertEqual([x["category"].split()[0] for x in f], ["VS-01"])
        self.assertEqual(f[0]["severity"], "HIGH")

    def test_underground_sight_fails_VS02(self):
        f = self.check([stg("S1", "CHR-Z", "TS-CEN-CAP", "D001T12:00", sees=["TS-SUB-POR"])])
        self.assertEqual([x["category"].split()[0] for x in f], ["VS-02"])

    def test_undetermined_sight_warns_VS03_and_declared_sight_is_clean(self):
        warn = self.check([stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T12:00", sees=["TS-CEN-CAP"])])
        self.assertEqual([(x["category"].split()[0], x["severity"]) for x in warn], [("VS-03", "MEDIUM")])
        self.assertEqual(self.check([stg("S1", "CHR-Z", "TS-CEN-EST", "D001T12:00", sees=["TS-URB-PNT"])]), [])

    def test_a_target_can_be_an_actor_at_the_same_instant(self):
        ok = self.check([stg("S1", "CHR-Z", "TS-CEN-EST", "D001T12:00", sees=[{"actor": "CHR-Y"}]),
                         stg("S2", "CHR-Y", "TS-URB-PNT", "D001T12:00")])
        self.assertEqual(ok, [])
        lost = self.check([stg("S1", "CHR-Z", "TS-CEN-EST", "D001T12:00", sees=[{"actor": "CHR-Y"}])])
        self.assertEqual([x["category"].split()[0] for x in lost], ["VS-03"])

    def test_lit_target_flag_reaches_the_rule(self):
        f = self.check([stg("S1", "CHR-Z", "TS-CEN-ORG", "D001T22:00", sees=[{"location": "TS-CEN-CAP", "lit": True}],
                            conditions={"lighting": "NIGHT_DARK"})])
        self.assertEqual([x["category"].split()[0] for x in f], ["VS-03"])       # com lanterna: indeterminado, não impossível


# ---------------------------------------------------------------------------
# gargalos
# ---------------------------------------------------------------------------

class Bottlenecks(unittest.TestCase):
    def test_bridge_and_choke_points_of_the_public_surface(self):
        b = ch.bottlenecks(model(), {"view": "ACTOR", "actor": "CHR-Z"})
        self.assertIn("TS-URB-PNT", b["articulation_points"])         # o Moinho só se alcança pela Ponte
        self.assertIn("TS-CEN-EST", b["articulation_points"])
        self.assertIn("TS-CEN-ORG", b["articulation_points"])
        self.assertNotIn("TS-URB-MOI", b["articulation_points"])      # folha
        self.assertIn("EDG-U-004", b["bridges"])

    def test_secret_passage_creates_an_alternative_only_for_who_knows_it(self):
        pub = ch.bottlenecks(model(), {"view": "ACTOR", "actor": "CHR-Z"})
        known = ch.bottlenecks(model(), {"view": "ACTOR", "actor": "CHR-K"})
        self.assertIn("EDG-U-001", pub["bridges"])                    # a Capela pendura de um único caminho
        self.assertNotIn("EDG-U-001", known["bridges"])               # para CHR-K há um ciclo pelo subsolo

    def test_layer_filter(self):
        b = ch.bottlenecks(model(), {"view": "ENGINE"}, layers={"URBAN"})
        self.assertFalse([n for n in b["articulation_points"] if n.startswith("TS-SUB")])

    def test_closed_edge_changes_the_choke_points(self):
        m = model()
        next(e for e in m["edges"] if e["id"] == "EDG-U-003")["state_timeline"] = [{"from_chapter": 0, "state": "DESTROYED"}]
        b = ch.bottlenecks(m, {"view": "ACTOR", "actor": "CHR-Z"})
        self.assertNotIn("TS-URB-PNT", b["articulation_points"])      # a ponte caiu: Moinho e Ponte ficam fora do grafo


# ---------------------------------------------------------------------------
# esconderijos
# ---------------------------------------------------------------------------

class Hideouts(unittest.TestCase):
    def hide(self, m, stagings, ledger=None):
        return ch.check_hideout_usage(m, stagings, ledger)

    def m(self, **fields):
        m = model()
        m["hideouts"][0].update(fields)
        return m

    def test_unspecified_capacity_is_never_violated(self):
        s = [stg("S1", "CHR-A", "TS-URB-CEM", "D001T10:00", role="HIDING", group_size=9)]
        self.assertEqual(self.hide(model(), s), [])

    def test_over_capacity_fails_HD02(self):
        s = [stg("S1", "CHR-A", "TS-URB-CEM", "D001T10:00", role="HIDING"), stg("S2", "CHR-B", "TS-URB-CEM", "D001T10:00", role="HIDING")]
        self.assertTrue(cats(self.hide(self.m(capacity=1), s), "HD-02"))
        self.assertFalse(cats(self.hide(self.m(capacity=2), s), "HD-02"))
        self.assertTrue(cats(self.hide(self.m(capacity=4), [stg("S1", "CHR-A", "TS-URB-CEM", "D001T10:00", role="HIDING", group_size=5)]), "HD-02"))

    def test_overstay_fails_HD03(self):
        s = [stg("S1", "CHR-A", "TS-URB-CEM", "D001T10:00", role="HIDING"), stg("S2", "CHR-A", "TS-URB-CEM", "D001T13:00", role="PRESENT")]
        self.assertTrue(cats(self.hide(self.m(duration_safe=2), s), "HD-03"))
        self.assertFalse(cats(self.hide(self.m(duration_safe=4), s), "HD-03"))
        self.assertFalse(cats(self.hide(model(), s), "HD-03"))

    def test_reuse_of_a_compromised_hideout_fails_HD04_only_if_the_actor_knows(self):
        m = self.m(compromise_events=[{"event": "EV-9", "chapter": 5, "effect": "COMPROMISED"}])
        ledger = {"events": [{"id": "EV-9", "chapter": 5, "knowledge_delta": [{"knower": "CHR-A", "learns": ["EV-9"]}]}]}
        late = [stg("S1", "CHR-A", "TS-URB-CEM", "D009T10:00", chapter=6, role="HIDING")]
        knows = self.hide(m, late, ledger)
        self.assertEqual([(x["category"].split()[0], x["severity"]) for x in knows], [("HD-04", "HIGH")])
        unaware = self.hide(m, [stg("S1", "CHR-B", "TS-URB-CEM", "D009T10:00", chapter=6, role="HIDING")], ledger)
        self.assertEqual([(x["category"].split()[0], x["severity"]) for x in unaware], [("HD-04", "INFO")])
        early = self.hide(m, [stg("S1", "CHR-A", "TS-URB-CEM", "D004T10:00", chapter=4, role="HIDING")], ledger)
        self.assertEqual(early, [])

    def test_seed_fields_must_be_numbers_or_unspecified(self):
        m = self.m(capacity="muitos", duration_safe=-1, discoverability="TALVEZ")
        f = cc.check_hideouts(m)
        self.assertEqual(len(cats(f, "HIDEOUT_FIELD_INVALID")), 2)
        self.assertTrue(cats(f, "INVALID_ENUM"))
        self.assertEqual(cc.check_hideouts(model()), [])

    def test_accessible_hideouts_never_invent_surveillance(self):  # SDD Q5
        r = ch.accessible_hideouts(model(), "TS-CEN-CAP", {"view": "ACTOR", "actor": "CHR-Z"})[0]
        self.assertEqual((r["hideout"], r["reachable"], r["surveillance"]), ("HID-CEM", True, "UNDETERMINED_SURVEILLANCE"))
        self.assertEqual(r["edges"], ["EDG-U-001", "EDG-U-005"])
        self.assertIn("TS-URB-CEM", r["surveillance_to_decide"])

    def test_accessible_hideouts_use_declared_surveillance(self):
        m = model()
        for l in m["locations"]:
            if l["id"] in ("TS-CEN-CAP", "TS-CEN-ORG", "TS-URB-CEM"):
                l["surveillance"] = "NONE"
        self.assertEqual(ch.accessible_hideouts(m, "TS-CEN-CAP", {"view": "ACTOR", "actor": "CHR-Z"})[0]["surveillance"], "NOT_WATCHED_KNOWN")
        next(l for l in m["locations"] if l["id"] == "TS-CEN-ORG")["surveillance"] = "PATROLLED"
        r = ch.accessible_hideouts(m, "TS-CEN-CAP", {"view": "ACTOR", "actor": "CHR-Z"})[0]
        self.assertEqual((r["surveillance"], r["watched_places"]), ("WATCHED", ["TS-CEN-ORG"]))

    def test_accessible_hideouts_report_the_closed_way(self):
        m = model()
        next(e for e in m["edges"] if e["id"] == "EDG-U-005")["state_timeline"] = [{"from_chapter": 0, "state": "RESTRICTED"}]
        blocked = ch.accessible_hideouts(m, "TS-CEN-CAP", {"view": "ACTOR", "actor": "CHR-Z"})[0]
        self.assertFalse(blocked["reachable"])
        opened = ch.accessible_hideouts(m, "TS-CEN-CAP", {"view": "ACTOR", "actor": "CHR-Z", "access_actions": ["EV-1"]})[0]
        self.assertEqual(opened["restricted_edges"], ["EDG-U-005"])


# ---------------------------------------------------------------------------
# perseguição
# ---------------------------------------------------------------------------

class ChaseModel(unittest.TestCase):
    def test_windows_are_ordered_and_start_at_zero(self):
        r = run(chase())
        for who in ("target", "pursuer"):
            for node, (early, late, dist) in r[who]["windows"].items():
                self.assertLessEqual(early, late, (who, node))
        self.assertEqual(r["target"]["windows"]["TS-CEN-CAP"], [0, 0, 0])

    def test_first_400_m_are_at_maximum_effort(self):
        g = cg.Graph(model())
        ctx = cg.make_ctx(mode="RUN", profile="FIT")
        path = g.shortest_path("TS-CEN-ORG", "TS-URB-CEM", ctx)
        early = ch.node_windows(g, path, ctx)[-1][1]
        lmin = g.resolve_lengths(path)[1][0]
        self.assertAlmostEqual(early, lmin / 4.2, places=6)          # < 400 m: tudo a RUN_MAX
        self.assertLess(lmin, 400)

    def test_effort_phase_then_sustained_pace(self):
        g = cg.Graph(model())
        ctx = cg.make_ctx(mode="RUN", profile="FIT")
        path = g.shortest_path("TS-URB-MOI", "TS-CEN-CAP", ctx)
        _, lmin, _ = g.resolve_lengths(path)
        total = sum(lmin)
        self.assertGreater(total, 400)
        early = ch.node_windows(g, path, ctx)[-1][1]
        self.assertAlmostEqual(early, 400 / 4.2 + (total - 400) / 3.2, delta=0.5)

    def test_walking_mode_has_no_effort_phase(self):
        g = cg.Graph(model())
        ctx = cg.make_ctx(mode="WALK", profile="FIT")
        path = g.shortest_path("TS-CEN-ORG", "TS-URB-CEM", ctx)
        early = ch.node_windows(g, path, ctx)[-1][1]
        self.assertAlmostEqual(early, g.resolve_lengths(path)[1][0] / 1.35, places=6)

    def test_secret_route_is_hidden_and_an_escape_from_a_pursuer_who_does_not_know_it(self):  # T26
        r = run(chase(target={"actor": "CHR-K", "start": "TS-CEN-CAP", "route": TUNNEL}))
        self.assertEqual([h["edge"] for h in r["hidden_transitions"]], TUNNEL)
        self.assertEqual([e["edge"] for e in r["escape_points"]], TUNNEL)
        self.assertEqual(r["findings"], [])
        self.assertNotIn("EDG-S-001", json.dumps(r["pursuer"]))       # o perseguidor nunca usa o que não conhece

    def test_same_route_is_no_escape_when_the_pursuer_also_knows_it(self):
        m = model()
        m["baseline"].append({"knower": "CHR-Z", "knows": {"ROUTE": TUNNEL[:1] + ["EDG-S-001", "EDG-S-002", "EDG-P-002"]}})
        r = run(chase(target={"actor": "CHR-K", "start": "TS-CEN-CAP", "route": TUNNEL}), m)
        self.assertEqual(r["escape_points"], [])

    def test_intercept_points_are_where_the_pursuer_can_be_in_time(self):
        r = run(chase(target={"actor": "CHR-K", "start": "TS-CEN-CAP", "end": "TS-URB-CEM", "route": ["EDG-U-001", "EDG-U-005"]}))
        nodes = {p["node"] for p in r["intercept_points"]}
        self.assertIn("TS-URB-CEM", nodes)
        self.assertNotIn("TS-CEN-CAP", nodes)                          # o ponto de partida não conta

    def test_dead_ends_near_the_start_exclude_hideouts_and_exits(self):
        r = run(chase(target={"actor": "CHR-Z", "start": "TS-CEN-CAP", "end": "TS-URB-CEM"}))
        self.assertEqual(r["dead_ends"], ["TS-URB-MOI"])              # Moinho: folha; Cemitério é esconderijo; moldura é saída

    def test_bottlenecks_on_the_target_route(self):
        r = run(chase(target={"actor": "CHR-Z", "start": "TS-CEN-CAP", "end": "TS-FRM-S"}))
        self.assertEqual(r["bottlenecks_on_target_route"], ["TS-CEN-ORG"])
        self.assertTrue(cats(r["findings"], "CH-07"))                  # o perseguidor chega ao gargalo antes: tensão
        self.assertEqual(cats(r["findings"], "CH-07")[0]["severity"], "INFO")


class ChaseRules(unittest.TestCase):
    def find(self, ch_spec, prefix, m=None, ledger=None):
        return cats(run(ch_spec, m, ledger)["findings"], prefix)

    def test_CH01_arrival_before_the_earliest_window(self):
        ev = [{"kind": "ARRIVES", "actor": "CHR-K", "at_node": "TS-URB-CEM", "at_s": 5}]
        self.assertTrue(self.find(chase(declared_events=ev), "CH-01"))
        ok = [{"kind": "ARRIVES", "actor": "CHR-K", "at_node": "TS-URB-CEM", "at_s": 600}]
        self.assertFalse(self.find(chase(declared_events=ok), "CH-01"))

    def test_CH01_actor_appears_at_a_node_off_his_route(self):
        ev = [{"kind": "ARRIVES", "actor": "CHR-K", "at_node": "TS-URB-MOI", "at_s": 900}]
        self.assertTrue(self.find(chase(declared_events=ev), "CH-01"))

    def test_CH01_pursuer_cannot_be_at_the_interception_before_the_earliest_time(self):
        ev = [{"kind": "INTERCEPT", "at_node": "TS-URB-CEM", "at_s": 10}]
        self.assertTrue(self.find(chase(declared_events=ev), "CH-01"))

    def test_CH02_pursuer_route_uses_a_secret_edge_he_does_not_know(self):
        f = self.find(chase(pursuer={"actor": "CHR-Z", "start": "TS-CEN-CAP", "route": TUNNEL}), "CH-02")
        self.assertTrue(f)
        self.assertEqual(f[0]["severity"], "HIGH")

    def test_CH02_is_fine_when_the_pursuer_knows_it(self):
        self.assertFalse(self.find(chase(pursuer={"actor": "CHR-K", "start": "TS-CEN-CAP", "route": TUNNEL}), "CH-02"))

    def test_CH06_target_escapes_through_an_edge_he_does_not_know(self):
        self.assertTrue(self.find(chase(target={"actor": "CHR-Z", "start": "TS-CEN-CAP", "route": TUNNEL}), "CH-06"))

    def test_CH03_gap_closure_is_bounded_by_the_speed_difference(self):
        # FIT persegue FIT: 4,2 (esforço) − 3,2 (sustentado) = 1,0 m/s ⇒ 60 s fecham 60 m
        impossible = [{"kind": "GAP_CLOSED", "from_gap_m": 150, "to_gap_m": 50, "over_s": 60}]
        possible = [{"kind": "GAP_CLOSED", "from_gap_m": 150, "to_gap_m": 100, "over_s": 60}]
        self.assertTrue(self.find(chase(declared_events=impossible), "CH-03"))
        self.assertFalse(self.find(chase(declared_events=possible), "CH-03"))

    def test_CH03_an_injured_target_is_easier_to_catch(self):
        ev = [{"kind": "GAP_CLOSED", "from_gap_m": 150, "to_gap_m": 50, "over_s": 60}]
        hurt = chase(declared_events=ev, target={"actor": "CHR-K", "start": "TS-CEN-CAP", "end": "TS-URB-CEM", "conditions": {"injury": "MAJOR"}})
        self.assertFalse(self.find(hurt, "CH-03"))                    # 4,2 − 3,2/2,2 = 2,7 m/s ⇒ 164 m em 60 s

    def test_CH04_intercept_at_a_node_the_pursuer_cannot_reach_in_time(self):
        ev = [{"kind": "INTERCEPT", "at_node": "TS-URB-CEM"}]
        far = chase(declared_events=ev, target={"actor": "CHR-K", "start": "TS-CEN-CAP", "route": TUNNEL},
                    pursuer={"actor": "CHR-Z", "start": "TS-URB-MOI", "end": "TS-URB-CEM"})
        near = chase(declared_events=ev, target={"actor": "CHR-K", "start": "TS-CEN-CAP", "route": TUNNEL},
                     pursuer={"actor": "CHR-Z", "start": "TS-CEN-ORG", "end": "TS-URB-CEM"})
        self.assertFalse(self.find(near, "CH-04"))
        r = run(far)
        pursuer_earliest = r["pursuer"]["windows"]["TS-URB-CEM"][0]
        target_latest = r["target"]["windows"]["TS-URB-CEM"][1]
        self.assertEqual(bool(self.find(far, "CH-04")), pursuer_earliest > target_latest)     # a regra é exatamente a sobreposição de janelas

    def test_CH04_intercept_off_the_target_route(self):
        ev = [{"kind": "INTERCEPT", "at_node": "TS-URB-MOI"}]
        self.assertTrue(self.find(chase(declared_events=ev), "CH-04"))

    def test_CH04_target_already_passed_the_node(self):
        ev = [{"kind": "INTERCEPT", "at_node": "TS-CEN-ORG"}]
        spec = chase(declared_events=ev, target={"actor": "CHR-Z", "start": "TS-CEN-CAP", "end": "TS-FRM-S"},
                     pursuer={"actor": "CHR-Y", "start": "TS-URB-MOI", "route": ["EDG-U-004", "EDG-U-003", "EDG-U-002"]})
        pursuer_earliest = run(spec)["pursuer"]["windows"]["TS-CEN-ORG"][0]
        target_latest = run(spec)["target"]["windows"]["TS-CEN-ORG"][1]
        self.assertEqual(bool(self.find(spec, "CH-04")), pursuer_earliest > target_latest)

    def test_CH05_reacquiring_sight_where_it_is_impossible(self):
        ev = [{"kind": "SIGHT_REACQUIRED", "pursuer_at": "TS-CEN-ORG", "target_at": "TS-CEN-CAP"}]
        dark = chase(declared_events=ev, lighting="NIGHT_DARK")
        f = self.find(dark, "CH-05")
        self.assertEqual([x["severity"] for x in f], ["MEDIUM"])
        day = self.find(chase(declared_events=ev), "CH-05")
        self.assertEqual([x["severity"] for x in day], ["INFO"])
        declared = [{"kind": "SIGHT_REACQUIRED", "pursuer_at": "TS-CEN-EST", "target_at": "TS-URB-PNT"}]
        self.assertEqual(self.find(chase(declared_events=declared), "CH-05"), [])

    def test_CH08_and_VS01_at_the_start(self):
        bad_gap = chase(initial_gap_m=10, pursuer={"actor": "CHR-Z", "start": "TS-CEN-EST", "end": "TS-URB-CEM"})
        self.assertTrue(self.find(bad_gap, "CH-08"))
        self.assertFalse(self.find(chase(initial_gap_m=800, pursuer={"actor": "CHR-Z", "start": "TS-CEN-EST", "end": "TS-URB-CEM"}), "CH-08"))
        visible = chase(initial_visibility="VISIBLE", lighting="NIGHT_DARK", pursuer={"actor": "CHR-Z", "start": "TS-CEN-EST", "end": "TS-URB-CEM"})
        self.assertTrue(self.find(visible, "VS-01"))
        maybe = chase(initial_visibility="VISIBLE", pursuer={"actor": "CHR-Z", "start": "TS-CEN-EST", "end": "TS-URB-CEM"})
        self.assertTrue(self.find(maybe, "VS-03"))

    def test_closed_edge_on_a_declared_route_fails_AC01(self):
        m = model()
        next(e for e in m["edges"] if e["id"] == "EDG-U-005")["state_timeline"] = [{"from_chapter": 0, "state": "RESTRICTED"}]
        spec = chase(target={"actor": "CHR-Z", "start": "TS-CEN-CAP", "route": ["EDG-U-001", "EDG-U-005"]})
        self.assertTrue(self.find(spec, "AC-01", m))
        spec["target"]["access_actions"] = ["EV-1"]
        self.assertFalse(self.find(spec, "AC-01", m))

    def test_missing_start_is_reported(self):
        self.assertTrue(self.find(chase(target={"actor": "CHR-K", "start": "NOPE"}), "CG-01"))

    def test_broken_route_is_reported(self):
        f = self.find(chase(target={"actor": "CHR-K", "start": "TS-CEN-CAP", "route": ["EDG-U-004"]}), "TR-06")
        self.assertTrue(f)

    def test_knowledge_from_the_ledger_changes_the_verdict(self):  # T12 dentro da perseguição
        spec = chase(pursuer={"actor": "CHR-Z", "start": "TS-CEN-CAP", "route": TUNNEL})
        ledger = {"events": [{"id": "EV-1", "chapter": 2, "knowledge_delta": [{"knower": "CHR-Z", "learns": TUNNEL[:1] + ["EDG-S-001", "EDG-S-002", "EDG-P-002"]}]}]}
        self.assertTrue(self.find({**spec, "chapter": 1}, "CH-02", ledger=ledger))
        self.assertFalse(self.find({**spec, "chapter": 2}, "CH-02", ledger=ledger))


# ---------------------------------------------------------------------------
# cena completa e CLI
# ---------------------------------------------------------------------------

class Scene(unittest.TestCase):
    def test_validate_scene_merges_everything(self):
        doc = {"staging": [stg("S1", "CHR-Z", "TS-CEN-EST", "D001T22:00", sees=["TS-URB-PNT"], conditions={"lighting": "NIGHT_DARK"}),
                           stg("S2", "CHR-Z", "TS-CEN-CAP", "D001T22:01", role="HIDING")],
               "chases": [chase(declared_events=[{"kind": "ARRIVES", "actor": "CHR-K", "at_node": "TS-URB-CEM", "at_s": 1}])]}
        r = ch.validate_scene(model(), doc)
        kinds = {f["category"].split()[0] for f in r["findings"]}
        self.assertTrue({"VS-01", "HD-01", "CH-01", "TR-05"} <= kinds)
        self.assertEqual(len(r["chases"]), 1)

    def test_a_clean_scene_has_no_findings(self):
        doc = {"staging": [stg("S1", "CHR-Z", "TS-CEN-EST", "D001T12:00", sees=["TS-URB-PNT"]),
                           stg("S2", "CHR-Z", "TS-CEN-ORG", "D001T12:03")]}
        self.assertEqual(ch.validate_scene(model(), doc)["findings"], [])


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--canon", str(FIXTURE), *args], capture_output=True, text=True, encoding="utf-8",
                              env={"PYTHONIOENCODING": "utf-8", "PATH": __import__("os").environ.get("PATH", "")})

    def test_visible(self):
        r = json.loads(self.run_cli("--visible", "TS-CEN-ORG", "TS-CEN-CAP", "--lighting", "NIGHT_DARK", "--recognize").stdout)
        self.assertEqual((r["result"], r["recognition"]), ("NOT_VISIBLE", "RECOGNITION_OUT_OF_SCOPE"))

    def test_bottlenecks_and_hideouts(self):
        b = json.loads(self.run_cli("--bottlenecks", "--actor", "CHR-Z").stdout)
        self.assertIn("TS-URB-PNT", b["articulation_points"])
        h = json.loads(self.run_cli("--hideouts", "TS-CEN-CAP", "--actor", "CHR-Z").stdout)
        self.assertEqual(h["hideouts"][0]["surveillance"], "UNDETERMINED_SURVEILLANCE")

    def test_check_staging_runs_chases_and_signals_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "scene.yaml"
            f.write_text(yaml.safe_dump({"chases": [chase(pursuer={"actor": "CHR-Z", "start": "TS-CEN-CAP", "route": TUNNEL})]}), encoding="utf-8")
            r = self.run_cli("--check-staging", str(f))
            self.assertEqual(r.returncode, 1)
            self.assertTrue(any(x["category"].startswith("CH-02") for x in json.loads(r.stdout)["findings"]))


if __name__ == "__main__":
    unittest.main()
