"""Book-specific compiler for the forty pre-manuscript chapter briefs.

The authoritative inputs remain the composed runtime canon. This helper exists
to make the repeated brief topology deterministic while leaving literary
judgment (beats, risks, council review) visible in each output.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import yaml


PULSE = {
    range(1, 5): "62→78; suspicion of Astrid and curiosity about Sigrid",
    range(5, 9): "72→86; conditional investment in the pact",
    range(9, 13): "76→92; RB-02 becomes plausible but unsettled",
    range(13, 17): "82→98; desire for flight with moral uncertainty",
    range(17, 19): "105→128; shock followed by grief, never triumph",
    range(19, 24): "118→142; propulsion with one credible exhale in chapter 20",
    range(24, 27): "88→40; betrayal, perceptual silence and ethical alarm",
    range(27, 30): "58→72; boundaries matter more than reunion wish",
    range(30, 35): "70→90; evidentiary suspense and restoration cost",
    range(35, 38): "68→96; hope with active manipulation vigilance",
    range(38, 41): "92→112→74; irreversible choice, grief and earned agency",
}

MOTIFS = {
    1: ["SYM-BLACK-APPLE seed in the crest; public LOW spoiler only"],
    3: ["SYM-BLACK-WATER first material field; archive, never portal"],
    5: ["SIG-THREE-DROPS seeded as count, still INTACT"],
    8: ["promise loop fixed; no sigil state change yet"],
    10: ["black apple recalled as evidence; three marks remain unexplained"],
    11: ["iron crown is literary evidence, not an MVP visual element"],
    14: ["winter branch first bud; three-mark recall"],
    17: ["SIG-THREE-DROPS INTACT→MARKED after EV-08"],
    18: ["MARKED displayed; exact permanent lacunae recorded"],
    20: ["black water transforms; intimacy cannot visually erase risk"],
    25: ["SYM-BLACK-APPLE payoff; SIG MARKED→FRACTURED after EV-11"],
    26: ["FRACTURED displayed through procedural mismatch, not special effects"],
    29: ["SIG FRACTURED→ABSENT after EV-12; body memory is not authorization"],
    32: ["crown surrender and second branch bud remain prose motifs"],
    33: ["apple seed becomes evidentiary payoff"],
    35: ["three permanent lacunae are named; never recovered"],
    39: ["SIG ABSENT→RETURNED_DIFFERENT after EV-17; six new weeks are lost"],
    40: ["black water judgment payoff; changed sigil state appears only post-trigger"],
}

PHYS = {
    "I — A Casa do Gigante": "constrained space, held breath and exact observation; attraction remains observation",
    "II — Os Trabalhos": "effort/recovery cycles shorten; fatigue and evidence accumulate",
    "III — A Fuga": "continuous exertion with plausible injury, exposure and one genuine safe interval",
    "IV — O Homem que a Esqueceu": "alarm, procedural familiarity and desire newly caused remain separate channels",
    "V — Faça-me Lembrar": "staged stress, capacity checks, recovery nights and grief without cure euphoria",
}

BEATS = {
  1: ["Astrid displays the collection notice while keeping its object grammatically vague.", "Liv challenges Elias's assumption; he converts shame into command and excludes her from the decision.", "The apple crest and four old marks make the debt material.", "Elias signs in Liv's place; she is safe but their trust is damaged before he leaves."],
  2: ["Elias follows an inland road that disappears from ordinary navigation.", "At the threshold the Giant separates willingness, adulthood and claimed information into three questions.", "Elias answers yes three times while suppressing what Liv said.", "Four work marks appear; leaving now requires completing the audit he does not yet understand."],
  3: ["Runa inventories Elias and gives house rules without welcome.", "The Giant proves specific Vinter benefits and offers a morally persuasive account of displaced cost.", "Elias finds scraped names where a clean ledger should be.", "He chooses covert investigation, delivering suspicion and rule knowledge to chapter 4."],
  4: ["Sigrid watches Elias test a door and classifies his protective habits as risk.", "She opens the hidden counter-audit room because his investigation threatens her timetable.", "The four tasks are reframed as instruments capable of testing the substitution.", "She offers utility without trust; Elias becomes a possible witness and possible liability."],
  5: ["A reflection lags while Sigrid defines cooperation and exit only.", "Elias presses for motive; she refuses intimacy, biography and obedience as terms.", "They negotiate revocability, scope and separate interests.", "The disappearing ink drop witnesses a limited pact, not romance."],
  6: ["Sigrid demonstrates the house's spatial grammar and her memory notebook.", "A shallow palm laceration from the door mechanism compromises Elias's grip.", "She cleans and closes it with explicit permission; he notices one factual lacuna in her otherwise exact record.", "The hand remains bandaged and grip-limited through the first work."],
  7: ["Dinner offers no fruit but stages the Giant's strongest evidence against Vinter innocence.", "His real attachment to Sigrid appears through custody language, not tenderness coding.", "Elias admits his family benefited and nearly mistakes accurate indictment for legitimate ownership.", "He leaves with the argument unresolved and greater need for independent proof."],
  8: ["Sigrid shows how each work can form an auditable chain rather than a heroic trial.", "She drafts and reads terms limited to exit, name and instruments; Elias can refuse without punishment or added loss.", "Elias accepts before the window witness; the promise grants no body, marriage, exclusivity or obedience.", "The promise opens risk: both now have something the house can weaponize."],
  9: ["The seasonless orchard forces Elias to identify a memory he values without offering it permanently.", "His bandaged palm and denied hunger make handling the trees imprecise.", "He deposits his happiest memory temporarily; its absence produces brief disorientation and emotional blankness.", "The correct apple appears unbitten, and verified return restores facts but leaves fatigue."],
  10: ["Sigrid uses the apple without eating it and opens its chain of custody.", "Three stains recur while the seed shows Solveig and a child entering Vinter care.", "Elias uses counted breath as the recovered memory and new evidence compete for attention.", "They retain instrument one but cannot yet classify the entry as rescue, adoption or delivery."],
  11: ["Sigrid chooses the submerged route because only a reflected mandate can be retrieved.", "The rule pulls her under when she redirects the search; her agency created the risk rather than passive helplessness.", "Elias secures the line with his injured grip and follows her signal, making rescue cooperative and costly.", "They surface with the iron crown, wet, shaking and temporarily deprived of fine motor control."],
  12: ["Sigrid orders wet layers removed, warmth, water and a dexterity check before interpretation.", "Elias prepares coffee clumsily while rewarming; the act is material recovery before intimacy.", "She explains what Mestermø measures but omits that she holds the office.", "Instrument two is secured; hypothermic fatigue and the omission travel into the forest work."],
  13: ["The forest closes paths when either partner repeats a self-protective lie.", "Cold stiffness, Elias's palm pain and Sigrid's tightening jaw degrade their teamwork.", "Sigrid admits prior physical escape chances; Elias hears instrumentalization and withdraws cooperation.", "The branch stays dead and they enter chapter 14 divided with little reserve."],
  14: ["The dead branch responds only when each names a truth that damages a self-model.", "Elias admits choosing suffering; Sigrid admits power helped keep her in the house.", "A near-kiss stops by their joint verbal boundary and the material need to continue—not an external interruption.", "The first bud and their explicit limit permit descent without resolving the tribunal."],
  15: ["Geothermal heat worsens dehydration rather than curing the forest cold.", "Sigrid names three inherited benefits while tremor arrives only after each confrontation.", "The tribunal tests responsibility without confirming religious Hell or inherited guilt as destiny.", "A copper receipt with four marks—one scraped—emerges; both leave depleted, not purified."],
  16: ["They cross-check seed, crown, branch and receipt while pain and sleep debt narrow options.", "Elias uses the title Mestermø to stop an immediate threat.", "The word authenticates Sigrid's office and alerts the house, converting proof into pursuit.", "All four instruments are acquired; recovery is abandoned because the death order follows."],
  17: ["The Giant orders Sigrid to kill Elias under the office logic she helped administer.", "She attempts another route, then chooses a false presence with full knowledge of its price.", "After each drop she tests one target memory: Solveig's voice, felt safety, childhood face; nausea and referentless silence follow.", "She consults the notebook, records facts, orients to date/place/object and only then begins delayed trembling."],
  18: ["Elias witnesses Sigrid complete factual orientation before he discusses escape mechanics.", "The simulacrum supplies voice, heat and shadow but never conversation or personhood.", "Sigrid declares the false death to the reflection and the house accepts a short deadline.", "They enter the drainage with her nausea, tremor and attention failures active; there is no emotional recovery."],
  19: ["Sigrid begins the moving forest sleep-deprived, nauseated and intermittently inattentive.", "Cobradores and contractual paths force a choice between personal records and the seed evidence.", "Elias follows her instructions but stops when her attention drops, preventing competence fantasy.", "She destroys recoverable personal records to preserve the seed and exits with anger, grief and reduced reserve."],
  20: ["Avalanche danger ends only after they reach a stable weather station and verify no immediate pursuit.", "They rewarm, hydrate, eat, treat injuries, orient and sleep enough to recover decision capacity.", "Each initiates and confirms intimacy with an easy stop path; intimacy buys no escape, protection, disclosure or promise.", "Only afterward does Elias learn the three-drop cost; show there was no active lie or strategic withholding for sex, and let his response remain dramatically real."],
  21: ["They leave with insufficient sleep, muscle soreness and lower cold tolerance despite the safe interval.", "At the industrial cableway Sigrid's account of Solveig conflicts with the Giant's repeated version.", "Elias manages the line while Sigrid reads the crown, neither functioning as invulnerable rescuer.", "She admits her memory source may be contaminated; uncertainty, crown and physical depletion enter the mine."],
  22: ["The flooded gallery reactivates Sigrid's water response and Elias's accumulated hand/shoulder pain.", "A reflection shows Astrid delivering the child but does not interpret motive.", "Elias refuses the faster route that would abandon the crown; Sigrid anchors him by date, route and object.", "They emerge cold and exhausted with evidence preserved, no miraculous analgesia."],
  23: ["At the human toll, exposure and fatigue make surrendering Sigrid's name the easiest payment.", "Elias instead gives the Vinter watch and states love without demanding answer or relief.", "Sigrid answers as a present choice while practical passage remains separately negotiated.", "They cross with name and instruments intact, but depleted enough for the next false emergency to exploit judgment."],
  24: ["Before the Vinter boundary they state four taboos and a verification plan.", "One coordinated Astrid deception supplies a time-stamped message, sealed-archive chemical alarm, disabled local line and controlled visible smoke, making outside verification temporarily impossible.", "Elias's Vinter guilt and protector self-model make him enter before securing Sigrid's access; this is his accountable failure under adulterated information, not stupidity.", "Elias knows he left Sigrid at the chapel with the instruments; no Sigrid interiority enters this POV."],
  25: ["Inside, Elias confirms Liv is physically safe but accepts Astrid's claim that food is needed after exposure.", "Astrid uses ordinary hospitality and incomplete causal disclosure; the choice to eat is not informed consent to memory alteration.", "The bite separates ingestion from perceptual change: taste, pause, disorientation, then Sigrid-centered access fails.", "Familiar skills and all non-Sigrid bonds remain; Astrid covers the evidence of violation."],
  26: ["Elias reconstructs escape facts and injuries while finding no person attached to their relational meaning.", "He calls himself alone; the claim fits his accessible self-model but conflicts with material traces.", "He prepares two coffees automatically and cannot explain the second cup; this is procedural rupture, not desire.", "Remain entirely in Elias POV: the empty destination and unclaimed cup imply an absent person; Sigrid's embodied wait begins in chapter 27."],
  27: ["Sigrid enters after a cold, sleepless, underfed vigil at the chapel, regulating by date/place/object and inventorying exits.", "She suppresses the impulse to approach Elias and presents herself as auditor, not lover or guest.", "Once, she tries to choose which fact he 'needs' first; Elias stops the sequence and the later clinical boundary confirms his right to control pace. She accepts the limit.", "The copper receipt grants temporary standing without intimacy; Elias inherits an alarming stranger with evidence."],
  28: ["Elias experiences defensive alarm and procedural familiarity when Sigrid speaks or moves through known work patterns.", "No moral repulsion and no new desire are asserted; he checks exits, facts and witnesses.", "Sigrid keeps distance and offers evidence capable of incriminating her.", "Elias prevents her expulsion because present fairness requires a hearing, not because his body authorizes trust."],
  29: ["An open door, two separated chairs and a revocable time limit create a regulatable conversation.", "Elias reproduces a knot/coffee sequence and asks what it means rather than accepting Sigrid's interpretation.", "She states that procedural memory proves learning only and cannot authorize touch, intimacy or truth.", "They form a narrow evidence pact; old trust becomes formally suspended and the sigil field becomes ABSENT."],
  30: ["Liv brings Sigrid food and archive access without demanding emotional performance after her vigil.", "A graft and childhood drawing connect Astrid to the apple system while Sigrid refuses to test Elias with old preferences.", "Elias's presence triggers approach impulse; she deliberately withdraws and uses Liv's grounding.", "Liv chooses alliance based on present evidence, moving the investigation beyond the couple."],
  31: ["The archive remains physically locked and ethically open only through negotiated access.", "Elias reads evidence of his prior relation while Sigrid stays across the table with door open and pauses revocable.", "His reaction is identity grief and fear of being authored by another self, not possessive competition.", "He chooses distance without expelling her; Astrid's lock becomes the next material opposition."],
  32: ["Sigrid offers the crown for possible destruction, surrendering leverage rather than staging trust theater.", "Elias evaluates present conduct and returns it without invoking bodily familiarity.", "The branch buds because costly truth and refusal of sole custody are enacted, never because the universe blesses attraction.", "Mutual trust enters REBUILDING while the fraud evidence remains incomplete."],
  33: ["Letters, seed and drawing must survive a contested chain-of-custody test rather than merely being read aloud.", "Astrid's altered records challenge provenance; Liv's conservation expertise shifts evidentiary power.", "Elias apologizes for deciding in Liv's place, offers no defense of good intention, asks for no gratitude and accepts anger, silence or refusal; Liv controls her evidence and alliance.", "He accepts historical facts but refuses simulated emotion; the fraud chain becomes provable while restoration stays separate."],
  34: ["The Giant appears through an interested contractual defense, not as an exposition dispenser.", "The copper receipt's scraped fourth mark and crown mandate force a literal answer on invalid substitution; he argues displaced catastrophe made custody necessary.", "Under that instrument-bound challenge he discloses four restoration options and the six-week displacement price.", "Elias receives knowledge but makes no decision; the new self becomes an explicit stake."],
  35: ["Sigrid tries and fails to summon each of her three lost memories, producing nausea and grief without sensory recovery.", "Her notebook supplies facts only; its precision cannot console her.", "She gives Mari magical facts and stop limits, watches Mari offer Elias a private consultation, then leaves; assessment occurs off-page and its content stays confidential unless Elias authorizes disclosure.", "Sigrid does not question Mari or treat clinical silence as a decision; her desire grants no authority."],
  36: ["Mari presents four real options: none; factual reconstruction without magic; partial staged recovery whose exact target and bounded later-memory loss are quantified for each stage; full staged recovery displacing six weeks.", "She states irreversibility, uncertainty, alternatives and the conflicts of Sigrid and the Giant; choosing none cannot cost relationship, protection or testimony.", "Sigrid renounces the old promise before Elias responds; he chooses delay and present acquaintance.", "They leave without a restoration decision and begin the cooling-off interval."],
  37: ["After the established cooling interval, present conduct—not old gestures—supports newly negotiated intimacy.", "A complete scene break follows, including sleep, food, changed room and end of afterglow.", "Mari and Elias meet privately outside Sigrid's POV; Sigrid observes only separation, elapsed time and return, neither asks Mari for content nor treats silence as evidence.", "Elias voluntarily shares only his intention and chosen identity/testimony reasons, without sexual leverage or fear of losing Sigrid; later reconfirmation is still required."],
  38: ["Astrid offers a clandestine shortcut that would restore the old Elias without current safeguards; no ritual or contact begins.", "Sigrid's approach/avoidance tremor makes temptation real; she hands over the protocol, steps out of control and later discloses the attempt without claiming moral credit.", "Liv uncovers the reflection evidence and Astrid confesses from concrete fear and love, not cartoon malice.", "The shortcut is refused; independently witnessed, auditable and capacity-protected restoration becomes the only remaining path."],
  39: ["Day 65 / flight: Mari checks orientation, price, pressure and stop word before/after; Elias confirms, then develops headache/vertigo and receives a full recovery night.", "Day 67 / works: a new independent check and explicit reconfirmation precede consent; nausea, tremor and temporal confusion rise, followed by another full night.", "Day 69 / bond: after a third check Elias reconfirms; old recognition returns as six weeks become recognizably absent, producing acute grief and strong disorientation. Any failure to reconfirm stops the process permanently.", "Sigrid witnesses but never conducts the decision; day 70 is a full recovery night, not a montage bridge."],
  40: ["On day 71 Mari documents residual headache, fatigue, temporal disorientation and incomplete integration before the hearing.", "The four instruments separately invalidate substitution and sole custody; each opt-in custodian speaks for their own acceptance.", "Sigrid takes office only long enough to distribute it and breaks the crown into four accountable fragments.", "Elias testifies 'I was not alone'; leaving together is a present logistical choice, not automatic intimacy. No kiss, sex or totalizing declaration proves cure."],
}

BODY = {
  1: "entry—travel tension and denied hunger; peak—shoulders rise and irony accelerates; regulation—checks the notice twice; exit—leaves underfed and morally activated",
  2: "entry—underfed travel fatigue; peak—threshold vigilance; regulation—counts answers and exits; exit—adrenalized with sleep delayed",
  3: "entry—poor sleep and controlled appetite; peak—argument narrows attention; regulation—material ledger check; exit—suspicion sustains wakefulness",
  4: "entry—Sigrid's light sleep and exit inventory; peak—Elias enters hidden space; regulation—aligns tools and sequences terms; exit—breath still held but plan active",
  5: "entry—mutual vigilance; peak—reflection witnesses terms; regulation—specific revocable language; exit—conditional trust without bodily ease",
  6: "entry—contained fatigue; peak—palm laceration; regulation—consented cleaning/bandage and cold metal; exit—Elias grip-limited, Sigrid jaw tight",
  7: "entry—hand pain and hunger; peak—moral identification with Giant; regulation—fact checking rather than reassurance; exit—sleep and appetite remain impaired",
  8: "entry—low reserve and wary proximity; peak—promise acceptance; regulation—written scope and refusal path; exit—emotional activation without recovery",
  9: "entry—bandaged palm, hunger and poor sleep; peak—temporary happy-memory absence causes disorientation; regulation—Sigrid verifies return and feeds him; exit—memory restored, fatigue and grip limit persist",
  10: "entry—post-disorientation fatigue; peak—Solveig/child evidence; regulation—counted breath and seated orientation; exit—instrument secured, uncertainty and three stains active",
  11: "entry—hand limit and low cold reserve; peak—submersion produces shivering and fine-motor loss; regulation—cooperative line, immediate dry shelter; exit—wet, shaking, crown secured",
  12: "entry—mild hypothermic symptoms; peak—rewarming pain and dexterity failure; regulation—dry layers, warm drink, water, food and rest; exit—motor control improving, deep fatigue persists",
  13: "entry—cold stiffness and sleep debt; peak—closed paths, jaw pain and delayed tremor; regulation—truth statements and paced movement; exit—divided, branch dry, reserves low",
  14: "entry—low reserve and relational rupture; peak—geothermal transition plus vulnerable truth; regulation—verbal boundary, water and sequencing; exit—bud present, dehydration rising",
  15: "entry—dehydration and tremor vulnerability; peak—three confrontations and heat; regulation—paced speech, cooling and salt/water; exit—receipt won, headache/tremor active",
  16: "entry—pain, dehydration and sleep debt; peak—title alerts house; regulation—instrument inventory and rapid plan; exit—adrenaline masks but does not remove deficits",
  17: "entry—accumulated exhaustion under lethal coercion; peak—three exact memory losses with nausea; regulation—notebook, date/place/object; exit—referentless grief and delayed tremor",
  18: "entry—nausea, tremor and attention lapses; peak—death declaration; regulation—Elias checks orientation before route; exit—drainage begins with deficits unchanged",
  19: "entry—sleep deprivation, nausea and reduced attention; peak—forest pursuit and record destruction; regulation—paced stops and Elias following instructions; exit—anger, grief and lower reserve",
  20: "entry—cold exposure and pursuit fatigue; peak—avalanche survival; regulation—secure shelter, dry clothes, warmth, food, water, wound care, orientation and sleep; exit—capacity restored enough for choice, soreness remains",
  21: "entry—insufficient sleep, soreness and low cold tolerance; peak—cableway and memory-source doubt; regulation—shared line work and counted commands; exit—fatigued, uncertainty active",
  22: "entry—water alarm and accumulated limb pain; peak—flooded gallery; regulation—date/route/object grounding and mutual load sharing; exit—cold, exhausted, evidence intact",
  23: "entry—exposure, hunger and fatigue; peak—name demanded at toll; regulation—concrete alternative payment and verbal choice; exit—no analgesic romance, judgment still impaired",
  24: "entry—depleted but mobile; peak—Liv-focused alarm overrides plan; regulation attempt—four taboos/verification plan fails under false data; exit—Elias inside, Sigrid cold at chapel",
  25: "entry—fatigue and domestic relief; peak—nonconsensual identity intervention; regulation unavailable until effect recognized; exit—selective access loss with skills/personality intact",
  26: "entry—disorientation around missing relational meaning; peak—two-cup procedural mismatch; regulation—inventory of retained facts; exit—alarm without desire or total amnesia",
  27: "entry—Sigrid cold, sleepless, underfed and grieving; peak—nonrecognition at gate; regulation—distance, date/place/object and procedural standing; exit—access gained, appetite/sleep debt persist",
  28: "entry—Elias defensive alarm, Sigrid approach/withdraw impulse; peak—familiar procedural cue; regulation—Elias controls distance and evidence order; exit—hearing accepted, no new desire asserted",
  29: "entry—mutual vigilance; peak—body-memory meaning disputed; regulation—open door, two chairs, time limit and revocability; exit—narrow pact, trust suspended",
  30: "entry—Sigrid insomnia/appetite loss; peak—graft evidence plus Elias proximity; regulation—withdrawal, food and Liv grounding; exit—Liv allied, Sigrid still depleted",
  31: "entry—controlled distance and archive fatigue; peak—Elias identity grief; regulation—open door, pauses and right to stop reading; exit—distance chosen without expulsion",
  32: "entry—cautious regulation; peak—crown surrender; regulation—object-based choice, no touch test; exit—trust rebuilding, body not treated as oracle",
  33: "entry—weeks of uneven sleep but improved routine; peak—contested evidence and Liv apology; regulation—chain-of-custody work and accepting response; exit—facts accepted, emotion unperformed",
  34: "entry—stable enough for complex information; peak—six-week price disclosure; regulation—written options and no same-scene choice; exit—uncertainty, no consent yet",
  35: "entry—anticipatory nausea; peak—failed recall of three losses; regulation—notebook facts, Mari's private capacity frame; exit—grief active, protocol control transferred",
  36: "entry—decision pressure; peak—renunciation of old promise; regulation—four options, conflicts, delay and refusal protection; exit—cooling-off begins",
  37: "entry—capacity stable after weeks of present trust; peak—chosen intimacy; regulation—sleep, food, space and later private Mari check; exit—independent intention, not final consent",
  38: "entry—approach/avoidance tremor; peak—real clandestine opportunity; regulation—hands protocol to others and steps away; exit—confession gained, safe route remains",
  39: "entry—capacity assessed anew each session; peaks—vertigo, then nausea/confusion, then acute disorientation/grief; regulation—stop word, before/after checks and full nights; exit—six weeks absent, integration incomplete",
  40: "entry—post-night headache, fatigue, disorientation and grief; peak—hearing/custody division; regulation—Mari record, separate testimony and opt-in roles; exit—logistical togetherness, months of integration ahead",
}


def pulse_for(n: int) -> str:
    return next(text for span, text in PULSE.items() if n in span)


def movement_phys(ch: dict) -> str:
    n = int(ch["number"])
    if 33 <= n <= 37:
        return "slow trust, identity grief, quantified options and cooling-off; restoration-session physiology has not begun"
    return PHYS[ch["movement"]]


def event_block(events: list[dict]) -> str:
    if not events:
        return "No structural ledger event is assigned to this chapter. Do not invent one; advance the next recorded event through scene-level causes."
    chunks = []
    for e in events:
        loops = e.get("loops") or {}
        consent = e.get("consent")
        lines = [
            f"- **{e['id']} / {', '.join(e.get('kind') or [])}:** " + " ".join(e.get("facts") or []),
            f"  - Caused by: {', '.join(e.get('caused_by') or [])}.",
            f"  - Loops: opens {loops.get('opens', [])}; feeds {loops.get('feeds', [])}; resolves {loops.get('resolves', [])}.",
        ]
        if consent:
            lines.append(
                "  - Consent contract: " +
                f"{consent.get('canonical')}; refusal {consent.get('ability_to_refuse')}; " +
                f"boundary {consent.get('boundary_state')}; manipulation {consent.get('manipulation_present')}."
            )
        chunks.append("\n".join(lines))
    return "\n".join(chunks)


def render(ch: dict, events: list[dict], protected: dict[str, dict]) -> str:
    n = int(ch["number"])
    pov = ch["pov"]
    scene = protected.get(ch.get("protected_scene", ""))
    continuity = "\n".join(f"- {x}" for x in ch.get("continuity") or [])
    motif = "\n".join(f"- {x}" for x in MOTIFS.get(n, ["No canonical visual-state transition; motifs may recur only if their meaning changes."]))
    if scene:
        must = "\n".join(f"- MUST PRESERVE: {x}" for x in scene.get("must_preserve") or [])
        reject = "\n".join(f"- REJECT IF: {x}" for x in scene.get("reject_if") or [])
        protected_text = (
            f"**{scene['id']}** — {scene.get('purpose', scene.get('description', 'Preserve exactly as canonized.'))}\n\n"
            f"{must}\n{reject}\n- Auditor: `{scene.get('auditor', 'EXECUTIVE_EDITOR')}`."
        )
    else:
        protected_text = "None assigned. Do not manufacture a substitute protected scene."
    beats = "\n".join(f"{i}. {beat}" for i, beat in enumerate(BEATS[n], 1))
    return f"""# Chapter {n:02d} Brief — {ch['title']}

Task `T{100+n:03d}_BRIEF_CHAPTER` · Owner `SCENE_ARCHITECT` · Status `READY_FOR_COUNCIL_REVIEW`

Sources: chapter architecture; Story, Character, World and Symbol Bibles; Plot Dependency Map; Timeline; Reader Vitals; Emotional Respiration Map; Page Bible; Memory Motif Map; Canon Digest; Causal Ledger; Visual Narrative Canon; immutable rules and protected scenes.

## 1. Function and POV

**POV:** {pov}, limited to what {pov} can perceive and infer now. Do not import the other protagonist's private conclusions.

**Function:** {ch['function']}

**Dramatic question:** {ch['dramatic_question']}

**Irreversible turn:** {ch['irreversible_turn']}

## 2. Scene architecture

{beats}

## 3. Causal contract

{event_block(events)}

Every ledger fact in this chapter must be earned on-page. Facts assigned to later events remain unavailable. Reader beliefs `RB-01` and `RB-02` may be supported or destabilized only on their planned evidence path.

## 4. Physiology, consent and reader pulse

- Movement physiology: {movement_phys(ch)}.
- Executable body ledger: {BODY[n]}.
- Reader pulse: {pulse_for(n)}.
- Recovery is concrete (orientation, water, food, wound care, sleep or accountable conversation) and changes capacity; it never deletes consequence.
- Silence, fear, debt, magic, exhaustion, arousal, old promises and bodily familiarity are not consent.
- When touch occurs, preserve current, specific, reversible agreement and the visible ability to stop.

## 5. Motif and visual-state instructions

{motif}

The cover system does not authorize chapter art. `SYM-BLACK-APPLE`, `SIG-THREE-DROPS` and `SYM-BLACK-WATER` can be cited in prose planning only at their anchored meanings. No figure, artifact quotation or new visual fact may be invented.

## 6. Continuity locks

{continuity}

- Current movement: {ch['movement']}.
- Timeline authority: `specs/TIMELINE.md`; do not compress recovery or move instruments without an explicit causal handoff.
- The Giant never lies literally; his ontology stays unresolved. The Hell tribunal stays metaphysically unresolved.
- Sigrid's three sacrificed memories remain permanently unavailable after chapter 17.

## 7. Protected-scene handling

{protected_text}

Protected status fixes ethical and causal function, not ornamental phrasing. If execution weakens refusal, capacity, price or consequence, revise the scene rather than the canon.

## 8. Prohibitions and exit test

- No exposition dump, omniscient diagnosis, destiny language or folklore cosplay.
- No generic dark-romance coercion presented as consent; no competence without fatigue; no magic without the registered price.
- No geography that turns inland Seljord into a maritime fjord.
- Exit only when the irreversible turn is visible, all continuity locks hold, bodily consequence persists, later revelations remain protected and the next chapter inherits a specific changed condition.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runtime", required=True)
    args = ap.parse_args()
    runtime = Path(args.runtime).resolve()
    arch = yaml.safe_load((runtime / "book/chapter_architecture.yaml").read_text(encoding="utf-8"))
    ledger = yaml.safe_load((runtime / "canon/CAUSAL_LEDGER.yaml").read_text(encoding="utf-8"))
    scenes_doc = yaml.safe_load((runtime / "book/protected_scenes.yaml").read_text(encoding="utf-8"))
    raw_scenes = scenes_doc.get("scenes") or scenes_doc.get("protected_scenes") or []
    protected = {s["id"]: s for s in raw_scenes}
    by_chapter: dict[int, list[dict]] = {}
    for event in ledger.get("events") or []:
        by_chapter.setdefault(int(event["chapter"]), []).append(event)
    out = runtime / "briefs/chapters"
    out.mkdir(parents=True, exist_ok=True)
    chapters = arch.get("chapters") or []
    if len(chapters) != 40:
        raise SystemExit(f"Expected 40 chapters, found {len(chapters)}")
    for ch in chapters:
        n = int(ch["number"])
        (out / f"CHAPTER_{n:02d}_BRIEF.md").write_text(
            render(ch, by_chapter.get(n, []), protected), encoding="utf-8"
        )
    print(f"BRIEFS OK | {len(chapters)} chapter briefs | {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
