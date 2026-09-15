"""Validador determinístico do `CAUSAL_LEDGER.yaml` — capability
`DARK_ROMANCE_CANON_ARCHITECT`.

Ver `docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md` para o desenho
completo.

**Slice 1** implementou: integridade do ledger (L0), causalidade de
personagem (L1), mutação de relacionamento (L2), payoff de horizonte longo
(L3) e o gate de sedução adulta (L7).

**Slice 2** implementou: crença do leitor e assimetria de informação (L4 —
`INFORMATION_LEAK`, `READER_OMNISCIENCE_LEAK`, `SOFT-03`), ancoragem causal de
revelação (INV-11 — `RETCON_DISGUISED_AS_TWIST`), pré-classificação do
Second-Read Test (L5, só via consulta — nunca vira achado sozinho, para não
virar fórmula de qualidade), consentimento canônico e consent drift (L8 —
`CONSENT_MISSING`, `CONSENT_LAYER_COLLAPSE`, `COERCION_AS_PAYOFF`,
`CONSENT_DRIFT`), e imutabilidade do passado contra um snapshot aprovado
(L10 — `RETCON`).

**Slice 3** (este acréscimo) implementa: amplitude emocional por contraste
(L6 — `CONTINUOUS_ESCALATION`, `PEAK_WITHOUT_CONTRAST`) e memória de
continuação (L9 — `--end-state`), fechando `L0`–`L10`. L6 opera sobre
`chapter_architecture.yaml` (campo `emotional_movement`), **não** sobre o
ledger — é STORY PLANNING, não CANON (ver E.4 do SDD): passe-o como um
segundo arquivo via `--chapter-architecture`, nunca embutido no
`CAUSAL_LEDGER.yaml`.

Princípio de armazenamento (E.2 do SDD): eventos são a única fonte de verdade
temporal. Este script nunca lê nem escreve um "estado atual" — ele projeta a
partir de baseline + deltas toda vez que precisa de um.

Sem dependências novas: biblioteca padrão + PyYAML, como o resto do motor.

Uso:
    python engine/scripts/check_causal_ledger.py --runtime runtime/<slug>
    python engine/scripts/check_causal_ledger.py --ledger caminho/CAUSAL_LEDGER.yaml
    python engine/scripts/check_causal_ledger.py --ledger <f> --mode realized --baseline <snapshot>
    python engine/scripts/check_causal_ledger.py --ledger <f> --why EV-01
    python engine/scripts/check_causal_ledger.py --ledger <f> --relationship CHR-B CHR-A
    python engine/scripts/check_causal_ledger.py --ledger <f> --payoff EV-05
    python engine/scripts/check_causal_ledger.py --ledger <f> --knowledge READER --at-chapter 3
    python engine/scripts/check_causal_ledger.py --ledger <f> --beliefs --at-chapter 6
    python engine/scripts/check_causal_ledger.py --ledger <f> --recontextualized --baseline <snapshot>
    python engine/scripts/check_causal_ledger.py --ledger <f> --chapter-architecture <arch.yaml>
    python engine/scripts/check_causal_ledger.py --ledger <f> --end-state
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "BLOCKER"]

# --- Vocabulário fechado (ver CAUSAL_LEDGER_TEMPLATE.yaml) ------------------

ALLOWED_GT_KINDS = {
    "FORMATIVE_HISTORY", "WOUND", "CORE_BELIEF", "WORLDVIEW",
    "CONSCIOUS_WANT", "UNCONSCIOUS_WANT", "FEAR", "NEED", "CONTRADICTION",
    "DEFENSE", "ATTACHMENT_PATTERN", "BOUNDARY", "TABOO", "SECRET",
    "VULNERABILITY", "TRIGGER", "CONDITION", "MOTIVE",
}
ALLOWED_LOOP_KINDS = {
    "INTIMACY", "EROTIC", "VULNERABILITY", "VERBAL", "POWER", "RELATIONAL",
    "PLOT",
}
ADULT_LOOP_KINDS = {"INTIMACY", "EROTIC"}
ADULT_EVENT_KINDS = {"SEDUCTION", "EROTIC_VERBAL", "INTIMACY", "SEXUAL"}
COERCION_KIND = "COERCION"
# LAW 04 / INV-07: todo evento adulto OU de coerção precisa de bloco `consent`
# completo — coerção também produz estado, e sem isso não seria auditável.
CONSENT_REQUIRED_KINDS = ADULT_EVENT_KINDS | {COERCION_KIND}
EVENT_STATUSES = {"PLANNED", "REALIZED"}
RESOLVE_MODES = {"CLOSED", "TRANSFORMED"}
MIN_ADULT_AGE = 18

CONSENT_CANONICAL_VALUES = {"CONSENSUAL", "DUBIOUS", "COERCIVE", "NON_CONSENSUAL"}
COERCIVE_CONSENT_VALUES = {"COERCIVE", "NON_CONSENSUAL"}
ABILITY_TO_REFUSE_VALUES = {"FULL", "CONSTRAINED", "NONE"}
BOUNDARY_STATE_VALUES = {"RESPECTED", "NEGOTIATED", "PUSHED", "VIOLATED"}
CONFIDENCE_VALUES = {"LOW", "MEDIUM", "HIGH"}
BELIEF_TRUTH_VALUES = {"TRUE", "INCOMPLETE", "FALSE"}

# LAW 05: amplitude por contraste. Ordinal só para comparar "não decrescente"
# — não é escore de intensidade, é ordem de um vocabulário fechado.
INTENSITY_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "PEAK": 4}
CONTRAST_CEILING = "MEDIUM"  # um capítulo LOW ou MEDIUM conta como "vale"

ALLOWED_CHARACTER_KEYS = {
    "id", "major", "age", "age_source", "ground_truth", "self_model",
    "social_persona",
}

CAUSE_ID_RE = re.compile(r"^(GT|EV)-[A-Za-z0-9][A-Za-z0-9_-]*$")

DEFAULT_CONFIG = {
    "min_payoff_feeds": 2,
    "max_monotonic_run": 3,     # usado a partir do Slice 3 (L6)
    "max_loop_silence": 6,      # usado a partir do Slice 3 (SOFT-04)
}


# --- estruturas auxiliares --------------------------------------------------

def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def finding(category: str, severity: str, chapter, evidence: str, detail: str,
            recommended_action: str) -> dict:
    return {
        "category": category,
        "severity": severity,
        "chapter": chapter if chapter is not None else "WHOLE_BOOK",
        "evidence": evidence,
        "detail": detail,
        "recommended_action": recommended_action,
    }


def build_indices(ledger: dict) -> tuple[dict, list[dict]]:
    """Indexa ids e detecta duplicatas. Um id duplicado vira DUPLICATE_ID e
    a segunda ocorrência não substitui a primeira no índice."""
    idx = {
        "char_index": {}, "gt_owner": {}, "gt_by_id": {}, "sm_owner": {},
        "sm_by_id": {}, "sp_owner": {}, "sp_by_id": {}, "ev_by_id": {},
        "lp_by_id": {},
    }
    dup_findings: list[dict] = []

    def add(table: dict, key, value, label: str):
        if not key:
            return
        if key in table:
            dup_findings.append(finding(
                "DUPLICATE_ID", "HIGH", "WHOLE_BOOK", key,
                f"id '{key}' duplicado em {label}.",
                "Tornar os ids únicos no ledger — cada id deve resolver a exatamente um objeto."))
            return
        table[key] = value

    for char in ledger.get("characters") or []:
        add(idx["char_index"], char.get("id"), char, "characters")
        for gt in char.get("ground_truth") or []:
            add(idx["gt_by_id"], gt.get("id"), gt, "ground_truth")
            if gt.get("id") not in idx["gt_owner"]:
                idx["gt_owner"][gt.get("id")] = char.get("id")
        for sm in char.get("self_model") or []:
            add(idx["sm_by_id"], sm.get("id"), sm, "self_model")
            if sm.get("id") not in idx["sm_owner"]:
                idx["sm_owner"][sm.get("id")] = char.get("id")
        for sp in char.get("social_persona") or []:
            add(idx["sp_by_id"], sp.get("id"), sp, "social_persona")
            if sp.get("id") not in idx["sp_owner"]:
                idx["sp_owner"][sp.get("id")] = char.get("id")
    for ev in ledger.get("events") or []:
        add(idx["ev_by_id"], ev.get("id"), ev, "events")
    for lp in ledger.get("loops") or []:
        add(idx["lp_by_id"], lp.get("id"), lp, "loops")
    return idx, dup_findings


def _participants_of(event: dict) -> set:
    out = set(event.get("participants") or [])
    if event.get("actor"):
        out.add(event["actor"])
    return out


# --- L0 — integridade do ledger --------------------------------------------

def check_integrity(ledger: dict) -> list[dict]:
    findings = []
    for required in ("apiVersion", "kind", "metadata", "characters",
                      "relationships", "loops", "events"):
        if required not in ledger:
            findings.append(finding(
                "MISSING_FIELD", "HIGH", "WHOLE_BOOK", required,
                f"Campo obrigatório '{required}' ausente no ledger.",
                "Adicionar o campo — ver engine/templates/CAUSAL_LEDGER_TEMPLATE.yaml."))
    if ledger.get("kind") not in (None, "CausalLedger"):
        findings.append(finding(
            "INVALID_ENUM", "HIGH", "WHOLE_BOOK", f"kind={ledger.get('kind')}",
            "kind deve ser CausalLedger.", "Corrigir o campo kind."))
    for char in ledger.get("characters") or []:
        for gt in char.get("ground_truth") or []:
            if gt.get("kind") not in ALLOWED_GT_KINDS:
                findings.append(finding(
                    "INVALID_ENUM", "HIGH", "WHOLE_BOOK",
                    f"{gt.get('id')}.kind={gt.get('kind')}",
                    "kind de ground_truth fora do vocabulário fechado.",
                    "Usar um dos kinds listados em CAUSAL_LEDGER_TEMPLATE.yaml."))
    for lp in ledger.get("loops") or []:
        if lp.get("kind") not in ALLOWED_LOOP_KINDS:
            findings.append(finding(
                "INVALID_ENUM", "HIGH", "WHOLE_BOOK",
                f"{lp.get('id')}.kind={lp.get('kind')}",
                "kind de loop fora do vocabulário fechado "
                "(INTIMACY/EROTIC/VULNERABILITY/VERBAL/POWER/RELATIONAL/PLOT).",
                "Corrigir o kind do loop."))
    for ev in ledger.get("events") or []:
        chapter = ev.get("chapter", "WHOLE_BOOK")
        if ev.get("status") not in EVENT_STATUSES:
            findings.append(finding(
                "INVALID_ENUM", "HIGH", chapter,
                f"{ev.get('id')}.status={ev.get('status')}",
                "status de evento deve ser PLANNED ou REALIZED.",
                "Corrigir o status do evento."))
        for r in (ev.get("loops") or {}).get("resolves") or []:
            if r.get("mode") not in RESOLVE_MODES:
                findings.append(finding(
                    "INVALID_ENUM", "HIGH", chapter,
                    f"{ev.get('id')} resolves {r.get('loop')} mode={r.get('mode')}",
                    "mode de resolução deve ser CLOSED ou TRANSFORMED.",
                    "Corrigir o mode."))
        consent = ev.get("consent")
        if consent:
            if consent.get("canonical") not in CONSENT_CANONICAL_VALUES:
                findings.append(finding(
                    "INVALID_ENUM", "HIGH", chapter,
                    f"{ev.get('id')}.consent.canonical={consent.get('canonical')}",
                    "consent.canonical deve ser CONSENSUAL, DUBIOUS, COERCIVE ou NON_CONSENSUAL.",
                    "Corrigir o valor canônico de consentimento."))
            if "ability_to_refuse" in consent and consent.get("ability_to_refuse") not in ABILITY_TO_REFUSE_VALUES:
                findings.append(finding(
                    "INVALID_ENUM", "HIGH", chapter,
                    f"{ev.get('id')}.consent.ability_to_refuse={consent.get('ability_to_refuse')}",
                    "ability_to_refuse deve ser FULL, CONSTRAINED ou NONE.",
                    "Corrigir o valor."))
            if "boundary_state" in consent and consent.get("boundary_state") not in BOUNDARY_STATE_VALUES:
                findings.append(finding(
                    "INVALID_ENUM", "HIGH", chapter,
                    f"{ev.get('id')}.consent.boundary_state={consent.get('boundary_state')}",
                    "boundary_state deve ser RESPECTED, NEGOTIATED, PUSHED ou VIOLATED.",
                    "Corrigir o valor."))
    for rb in ledger.get("beliefs") or []:
        if rb.get("confidence") not in CONFIDENCE_VALUES:
            findings.append(finding(
                "INVALID_ENUM", "HIGH", "WHOLE_BOOK",
                f"{rb.get('id')}.confidence={rb.get('confidence')}",
                "confidence deve ser LOW, MEDIUM ou HIGH.", "Corrigir o valor."))
        truth = rb.get("truth")
        if truth is not None and truth not in BELIEF_TRUTH_VALUES:
            if isinstance(truth, bool):
                # Pegadinha comum de YAML 1.1: TRUE/FALSE sem aspas viram
                # booleano, não a string do enum.
                detail = (f"truth={truth!r} — provavelmente `truth: TRUE`/`truth: FALSE` sem "
                          "aspas no YAML, resolvido como booleano em vez da string do enum.")
                action = 'Escrever `truth: "TRUE"` ou `truth: "FALSE"` entre aspas.'
            else:
                detail = "truth deve ser TRUE, INCOMPLETE ou FALSE."
                action = "Corrigir o valor."
            findings.append(finding(
                "INVALID_ENUM", "HIGH", "WHOLE_BOOK", f"{rb.get('id')}.truth={truth!r}",
                detail, action))
    return findings


def check_participant_references(ledger: dict, idx: dict) -> list[dict]:
    findings = []
    for ev in ledger.get("events") or []:
        chapter = ev.get("chapter", "WHOLE_BOOK")
        eid = ev.get("id")
        actor = ev.get("actor")
        if actor and actor not in idx["char_index"]:
            findings.append(finding(
                "UNKNOWN_REFERENCE", "HIGH", chapter, f"{eid}.actor={actor}",
                "personagem inexistente no ledger.",
                "Corrigir o id do personagem ou registrá-lo em characters[]."))
        for p in ev.get("participants") or []:
            if p not in idx["char_index"]:
                findings.append(finding(
                    "UNKNOWN_REFERENCE", "HIGH", chapter,
                    f"{eid}.participants includes {p}",
                    "personagem inexistente no ledger.",
                    "Corrigir o id do personagem ou registrá-lo em characters[]."))
        sa = ev.get("self_attribution")
        if sa:
            owner = idx["sm_owner"].get(sa)
            if owner is None:
                findings.append(finding(
                    "UNKNOWN_REFERENCE", "HIGH", chapter,
                    f"{eid}.self_attribution={sa}",
                    "self_attribution não existe em nenhum characters[].self_model.",
                    "Corrigir o id ou registrar o self_model."))
            elif actor and owner != actor:
                findings.append(finding(
                    "CAUSE_NOT_PARTICIPANT", "HIGH", chapter,
                    f"{eid}.self_attribution={sa} (owner={owner}, actor={actor})",
                    "self_attribution pertence a um personagem diferente do ator.",
                    "Usar um self_model do próprio ator, ou corrigir o ator do evento."))
    for rel in ledger.get("relationships") or []:
        for member in re.split(r"->", rel.get("pair", "")):
            if member and member not in idx["char_index"]:
                findings.append(finding(
                    "UNKNOWN_REFERENCE", "HIGH", "WHOLE_BOOK",
                    f"relationships pair={rel.get('pair')} membro={member}",
                    "personagem inexistente referenciado em relationships.",
                    "Corrigir o id do personagem."))
    for lp in ledger.get("loops") or []:
        for member in re.split(r"<->", lp.get("pair", "")):
            if member and member not in idx["char_index"]:
                findings.append(finding(
                    "UNKNOWN_REFERENCE", "HIGH", "WHOLE_BOOK",
                    f"{lp.get('id')} pair={lp.get('pair')} membro={member}",
                    "personagem inexistente referenciado em loops.",
                    "Corrigir o id do personagem."))
    return findings


# --- L1 — causalidade de personagem ----------------------------------------

def check_character_layers(ledger: dict) -> list[dict]:
    """LAW 01: personagem maior precisa das três camadas independentes."""
    findings = []
    for char in ledger.get("characters") or []:
        if not char.get("major"):
            continue
        cid = char.get("id")
        for layer, label in (("ground_truth", "Ground Truth"),
                              ("self_model", "Self-Model"),
                              ("social_persona", "Social Persona")):
            if not char.get(layer):
                findings.append(finding(
                    "MISSING_CHARACTER_LAYER", "HIGH", "WHOLE_BOOK",
                    f"{cid}.{layer}",
                    f"Personagem maior '{cid}' sem {label} (LAW 01: GT ≠ SM ≠ SP ≠ Reader Model).",
                    f"Adicionar ao menos uma entrada de {layer}."))
    return findings


def check_attraction_attribute(ledger: dict) -> list[dict]:
    """INV-02: atração é propriedade emergente da relação, nunca atributo de
    personagem. Qualquer campo fora do contrato do personagem é suspeito;
    valor numérico é o sintoma direto de `CHARM = 95`."""
    findings = []
    for char in ledger.get("characters") or []:
        cid = char.get("id", "?")
        for key in set(char.keys()) - ALLOWED_CHARACTER_KEYS:
            value = char[key]
            if isinstance(value, bool):
                is_numeric = False
            else:
                is_numeric = isinstance(value, (int, float))
            if is_numeric:
                findings.append(finding(
                    "ATTRACTION_AS_ATTRIBUTE", "HIGH", "WHOLE_BOOK",
                    f"{cid}.{key}={value!r}",
                    "Atributo numérico fora do contrato do personagem — atração/charme/sex "
                    "appeal não são atributo de personagem (LAW 01, INV-02): "
                    "ATTRACTION(A, B, CONTEXT, HISTORY, EMOTIONAL_STATE), nunca CHARM=95.",
                    "Remover o campo; se for atração, expressar como relationship_delta "
                    "direcional com `because` explicando o contexto."))
            else:
                findings.append(finding(
                    "UNKNOWN_FIELD", "LOW", "WHOLE_BOOK", f"{cid}.{key}={value!r}",
                    "Campo fora do contrato do ledger para characters[].",
                    "Remover, ou mover para a bíblia de personagem em prosa."))
    return findings


def check_unused_ground_truth(ledger: dict) -> list[dict]:
    """SOFT-07: GT de personagem maior que nenhum evento cita como causa é
    atributo decorativo, não causa (achado da revisão adversarial do SDD)."""
    cited = set()
    for ev in ledger.get("events") or []:
        for token in ev.get("caused_by") or []:
            if isinstance(token, str) and token.startswith("GT-"):
                cited.add(token)
    findings = []
    for char in ledger.get("characters") or []:
        if not char.get("major"):
            continue
        for gt in char.get("ground_truth") or []:
            gid = gt.get("id")
            if gid and gid not in cited:
                findings.append(finding(
                    "UNUSED_GROUND_TRUTH", "MEDIUM", "WHOLE_BOOK", gid,
                    f"'{gid}' nunca aparece em caused_by de nenhum evento até este ponto — "
                    "risco de ser atributo decorativo em vez de causa viva.",
                    "Citar esta GT como causa de ao menos um evento, ou remover se não for "
                    "estruturalmente relevante."))
    return findings


def resolve_causal_reference(token, idx: dict, event: dict) -> dict | None:
    """Resolve um token de `caused_by`. Retorna um achado se inválido, ou
    None se resolve corretamente. Único ponto de verificação de INV-01."""
    chapter = event.get("chapter", "WHOLE_BOOK")
    eid = event.get("id")
    if not isinstance(token, str) or not CAUSE_ID_RE.match(token):
        return finding(
            "GENRE_LABEL_CAUSALITY", "HIGH", chapter, f"{eid}.caused_by={token!r}",
            "Causa não é um id GT-*/EV-* resolvível — trope, arquétipo, rótulo de gênero "
            "ou alvo de experiência do leitor não são causa (LAW 01).",
            "Substituir por um id de Ground Truth do personagem ou de evento anterior.")
    prefix = token.split("-", 1)[0]
    if prefix == "GT":
        owner = idx["gt_owner"].get(token)
        if owner is None:
            return finding(
                "UNKNOWN_REFERENCE", "HIGH", chapter, f"{eid}.caused_by={token}",
                f"'{token}' não existe em nenhum characters[].ground_truth.",
                "Corrigir o id ou registrar a Ground Truth antes de citá-la.")
        if owner not in _participants_of(event):
            return finding(
                "CAUSE_NOT_PARTICIPANT", "HIGH", chapter, f"{eid}.caused_by={token}",
                f"'{token}' pertence a {owner}, que não participa deste evento.",
                "Citar apenas Ground Truth de quem participa do evento.")
        return None
    cause_event = idx["ev_by_id"].get(token)
    if cause_event is None:
        return finding(
            "UNKNOWN_REFERENCE", "HIGH", chapter, f"{eid}.caused_by={token}",
            f"'{token}' não existe em events[].", "Corrigir o id do evento causador.")
    if cause_event.get("chapter", 0) >= event.get("chapter", 0):
        return finding(
            "CAUSE_NOT_EARLIER", "HIGH", chapter, f"{eid}.caused_by={token}",
            f"'{token}' (cap. {cause_event.get('chapter')}) não é anterior a este evento "
            f"(cap. {event.get('chapter')}).",
            "Causa precisa vir de um capítulo estritamente anterior.")
    return None


def resolve_temporal_reference(token, idx: dict, event: dict) -> dict | None:
    """Resolve um token de `why_now` — exige existência e anterioridade, mas
    não exige posse por participante (uma justificativa de timing pode
    depender de um fato de outro personagem)."""
    chapter = event.get("chapter", "WHOLE_BOOK")
    eid = event.get("id")
    if not isinstance(token, str) or not CAUSE_ID_RE.match(token):
        return finding(
            "GENRE_LABEL_CAUSALITY", "HIGH", chapter, f"{eid}.why_now={token!r}",
            "why_now precisa ser um id GT-*/EV-* resolvível.",
            "Substituir por um id existente.")
    prefix = token.split("-", 1)[0]
    if prefix == "GT":
        if token not in idx["gt_by_id"]:
            return finding(
                "UNKNOWN_REFERENCE", "HIGH", chapter, f"{eid}.why_now={token}",
                f"'{token}' não existe em nenhum characters[].ground_truth.",
                "Corrigir o id.")
        return None
    cause_event = idx["ev_by_id"].get(token)
    if cause_event is None:
        return finding(
            "UNKNOWN_REFERENCE", "HIGH", chapter, f"{eid}.why_now={token}",
            f"'{token}' não existe em events[].", "Corrigir o id do evento.")
    if cause_event.get("chapter", 0) >= event.get("chapter", 0):
        return finding(
            "CAUSE_NOT_EARLIER", "HIGH", chapter, f"{eid}.why_now={token}",
            f"'{token}' (cap. {cause_event.get('chapter')}) não é anterior ao payoff "
            f"(cap. {event.get('chapter')}).",
            "why_now precisa apontar para evidência de capítulo estritamente anterior.")
    return None


def check_causal_references(ledger: dict, idx: dict) -> list[dict]:
    findings = []
    for ev in ledger.get("events") or []:
        for token in ev.get("caused_by") or []:
            result = resolve_causal_reference(token, idx, ev)
            if result:
                findings.append(result)
    return findings


# --- L2 — mutação de relacionamento (LAW 02) --------------------------------

def relationship_projection(ledger: dict) -> tuple[dict, dict, list[dict]]:
    """Dobra `relationship_delta` em ordem de capítulo. Retorna
    (timeline_por_par, estado_final_por_par, achados_STATE_RESET).

    Este é o único lugar do script que conhece "estado atual de relação" — e
    mesmo aqui ele nunca é armazenado, só computado a cada chamada."""
    timeline: dict[str, list[dict]] = defaultdict(list)
    state: dict[str, dict] = {}
    findings: list[dict] = []

    for rel in ledger.get("relationships") or []:
        pair = rel.get("pair")
        state[pair] = dict(rel.get("baseline") or {})

    events = ledger.get("events") or []
    ordered = sorted(enumerate(events), key=lambda pair: (pair[1].get("chapter", 0), pair[0]))
    for _, ev in ordered:
        eid = ev.get("id")
        chapter = ev.get("chapter", "WHOLE_BOOK")
        for delta in ev.get("relationship_delta") or []:
            pair = delta.get("pair")
            dim = delta.get("dimension")
            pair_state = state.setdefault(pair, {})
            expected_from = pair_state.get(dim, "UNKNOWN")
            actual_from = delta.get("from")
            if actual_from != expected_from:
                findings.append(finding(
                    "STATE_RESET", "HIGH", chapter,
                    f"{eid} {pair}.{dim} from={actual_from!r}",
                    f"esperado from={expected_from!r} (estado projetado imediatamente "
                    f"anterior), recebido {actual_from!r} — troca de câmera ou de wave não "
                    "pode resetar estado de relação (INV-04).",
                    "Corrigir `from` para o estado projetado anterior, ou inserir o evento "
                    "que de fato produz essa transição antes deste."))
            pair_state[dim] = delta.get("to")
            timeline[pair].append({
                "chapter": ev.get("chapter"), "event": eid, "dimension": dim,
                "from": actual_from, "to": delta.get("to"),
                "because": delta.get("because"),
            })
    return dict(timeline), state, findings


def check_structural_mutation(ledger: dict) -> list[dict]:
    """LAW 02 (R(t+1) ≠ R(t)) e INV-15 (evento estrutural sem nenhuma
    mutação). Eventos com `loops.resolves` são resíduo de `check_payoffs` —
    lá, a ausência de delta vira POST_PAYOFF_AMNESIA, mais específico."""
    findings = []
    for ev in ledger.get("events") or []:
        if not ev.get("structural"):
            continue
        loops = ev.get("loops") or {}
        if loops.get("resolves"):
            continue
        has_delta = bool(ev.get("relationship_delta"))
        has_loop_effect = bool(loops.get("opens") or loops.get("feeds"))
        has_knowledge_or_belief = bool(ev.get("knowledge_delta") or ev.get("beliefs"))
        if has_delta or has_loop_effect or has_knowledge_or_belief:
            continue
        chapter = ev.get("chapter", "WHOLE_BOOK")
        eid = ev.get("id")
        participants = ev.get("participants") or []
        if len(participants) >= 2:
            findings.append(finding(
                "RELATIONSHIP_AMNESIA", "HIGH", chapter, eid,
                "Evento estrutural com múltiplos participantes não deixa nenhum estado "
                "relacional, de conhecimento ou de loop (LAW 02: toda interação estrutural "
                "precisa produzir R(t+1) ≠ R(t)).",
                "Adicionar ao menos um relationship_delta, efeito de loop ou "
                "knowledge_delta, ou marcar o evento como não estrutural."))
        else:
            findings.append(finding(
                "STRUCTURAL_EVENT_WITHOUT_MUTATION", "HIGH", chapter, eid,
                "Evento estrutural não deixa nenhum estado (INV-15).",
                "Adicionar mutação de estado, ou marcar o evento como não estrutural."))
    return findings


# --- L3 — payoff de horizonte longo (LAW 03) --------------------------------

def check_payoffs(ledger: dict, idx: dict, config: dict) -> list[dict]:
    findings = []
    min_feeds = config.get("min_payoff_feeds", DEFAULT_CONFIG["min_payoff_feeds"])
    events = ledger.get("events") or []

    for ev in events:
        resolves = (ev.get("loops") or {}).get("resolves") or []
        if not resolves:
            continue
        chapter = ev.get("chapter", "WHOLE_BOOK")
        eid = ev.get("id")
        for r in resolves:
            loop_id = r.get("loop")
            mode = r.get("mode")
            into = r.get("into")
            why_now = r.get("why_now") or []
            evidence_prefix = f"{eid} resolves {loop_id}"

            if loop_id not in idx["lp_by_id"]:
                findings.append(finding(
                    "UNKNOWN_REFERENCE", "HIGH", chapter, evidence_prefix,
                    "loop referenciado não existe em loops[].",
                    "Corrigir o id do loop ou registrá-lo antes de resolvê-lo."))
                continue

            opened_before = [
                e for e in events
                if loop_id in ((e.get("loops") or {}).get("opens") or [])
                and e.get("chapter", 0) < ev.get("chapter", 0)
            ]
            if not opened_before:
                findings.append(finding(
                    "LOOP_NOT_OPENED", "HIGH", chapter, evidence_prefix,
                    "Nenhum evento de capítulo anterior abre este loop (LAW 03: payoff "
                    "não pode ser objetivo isolado de cena).",
                    "Adicionar o evento que abre o loop em capítulo anterior, ou corrigir "
                    "o loop referenciado."))

            feeders = [
                e for e in events
                if loop_id in ((e.get("loops") or {}).get("feeds") or [])
                and e.get("chapter", 0) < ev.get("chapter", 0)
            ]
            distinct_chapters = {e.get("chapter") for e in feeders}
            if len(distinct_chapters) < min_feeds:
                findings.append(finding(
                    "HEAT_WITHOUT_HISTORY", "HIGH", chapter, evidence_prefix,
                    f"Apenas {len(distinct_chapters)} capítulo(s) alimentador(es) "
                    f"anterior(es) deste loop; mínimo exigido é {min_feeds} "
                    "(payoff precisa de ancestralidade causal rastreável, não de "
                    "'chegou o capítulo do sexo').",
                    "Plantar mais eventos que alimentem este loop em capítulos "
                    "anteriores distintos, ou manter o payoff como PLANNED."))

            for token in why_now:
                result = resolve_temporal_reference(token, idx, ev)
                if result:
                    findings.append(result)

            if mode == "TRANSFORMED":
                if not into:
                    findings.append(finding(
                        "TRANSFORMED_WITHOUT_SUCCESSOR", "HIGH", chapter, evidence_prefix,
                        "mode TRANSFORMED sem `into` — payoff pode transformar tensão em "
                        "vez de encerrá-la, mas precisa declarar em que ela vira.",
                        "Declarar o loop sucessor em `into`, ou trocar mode para CLOSED."))
                elif into not in ((ev.get("loops") or {}).get("opens") or []):
                    findings.append(finding(
                        "TRANSFORMED_WITHOUT_SUCCESSOR", "HIGH", chapter,
                        f"{evidence_prefix} into {into}",
                        "O loop sucessor declarado em `into` não é aberto por este mesmo "
                        "evento.",
                        "Adicionar `into` a loops.opens deste evento, ou apontar para um "
                        "loop realmente aberto aqui."))

            if not ev.get("relationship_delta"):
                findings.append(finding(
                    "POST_PAYOFF_AMNESIA", "HIGH", chapter, evidence_prefix,
                    "Payoff sem mudança de estado relacional — aftermath é parte do "
                    "payoff (LAW 03) e não pode faltar.",
                    "Adicionar ao menos um relationship_delta a este evento."))
    return findings


# --- L7 — Adult Seduction Gate (hard, independente de perfil) --------------

def check_adult_gate(ledger: dict, idx: dict) -> list[dict]:
    def age_ok(char_id) -> tuple[bool, object]:
        char = idx["char_index"].get(char_id)
        age = char.get("age") if char else None
        ok = isinstance(age, int) and not isinstance(age, bool) and age >= MIN_ADULT_AGE
        return ok, age

    findings = []
    for ev in ledger.get("events") or []:
        kinds = set(ev.get("kind") or [])
        if not (kinds & ADULT_EVENT_KINDS):
            continue
        chapter = ev.get("chapter", "WHOLE_BOOK")
        for participant in _participants_of(ev):
            ok, age = age_ok(participant)
            if not ok:
                findings.append(finding(
                    "ADULT_SEDUCTION_FAIL", "BLOCKER", chapter,
                    f"{ev.get('id')} participante {participant} idade={age!r}",
                    "Evento de sedução/erotismo/intimidade com participante sem idade "
                    "adulta canônica confirmada. Idade desconhecida NÃO equivale a adulto.",
                    "Confirmar idade >= 18 na bíblia de personagem antes de aprovar este "
                    "evento, ou remover o participante da cena."))
    for lp in ledger.get("loops") or []:
        if lp.get("kind") not in ADULT_LOOP_KINDS:
            continue
        members = [m for m in re.split(r"<->", lp.get("pair", "")) if m]
        for member in members:
            ok, age = age_ok(member)
            if not ok:
                findings.append(finding(
                    "ADULT_SEDUCTION_FAIL", "BLOCKER", "WHOLE_BOOK",
                    f"{lp.get('id')} membro {member} idade={age!r}",
                    "Loop de intimidade/erótico com par cuja idade não é adulta "
                    "canônica confirmada.",
                    "Confirmar idade >= 18 de ambos os membros do par antes de declarar "
                    "este loop."))
    return findings


# --- L4 — crença do leitor e assimetria de informação (LAW 04) -------------

def transitive_gt_ancestors(idx: dict, event_id: str, _seen: frozenset | None = None) -> set[str]:
    """Todos os ids de Ground Truth alcançáveis subindo a cadeia `caused_by`
    a partir de um evento. Usado por INV-11 (ancoragem de revelação) e por
    `why_report`."""
    seen = _seen or frozenset()
    if event_id in seen:
        return set()
    seen = seen | {event_id}
    ev = idx["ev_by_id"].get(event_id)
    if ev is None:
        return set()
    out: set[str] = set()
    for token in ev.get("caused_by") or []:
        if not isinstance(token, str):
            continue
        if token.startswith("GT-"):
            out.add(token)
        elif token.startswith("EV-"):
            out |= transitive_gt_ancestors(idx, token, seen)
    return out


def check_belief_revision_ancestry(ledger: dict, idx: dict) -> list[dict]:
    """INV-11: uma revelação só pode recontextualizar uma crença se a GT
    divulgada já estava na ancestralidade causal de ao menos uma das cenas
    que formaram essa crença. Sem isso, é um twist colado depois, não uma
    revelação plantada (RETCON_DISGUISED_AS_TWIST)."""
    findings = []
    beliefs_by_id = {b.get("id"): b for b in ledger.get("beliefs") or []}
    for ev in ledger.get("events") or []:
        revises = (ev.get("beliefs") or {}).get("revises") or []
        chapter = ev.get("chapter", "WHOLE_BOOK")
        for rb_id in revises:
            rb = beliefs_by_id.get(rb_id)
            if rb is None:
                findings.append(finding(
                    "UNKNOWN_REFERENCE", "HIGH", chapter, f"{ev['id']}.beliefs.revises={rb_id}",
                    "crença revisada não existe em beliefs[].",
                    "Corrigir o id ou registrar a crença antes de revisá-la."))
                continue
            disclosed = set(rb.get("disclosed_by_revision") or [])
            if not disclosed:
                continue
            about_events = [a for a in (rb.get("about") or []) if isinstance(a, str) and a.startswith("EV-")]
            anchored = any(disclosed & transitive_gt_ancestors(idx, about_id) for about_id in about_events)
            if not anchored:
                findings.append(finding(
                    "RETCON_DISGUISED_AS_TWIST", "HIGH", chapter, f"{ev['id']} revises {rb_id}",
                    f"Nenhuma das Ground Truth divulgadas ({', '.join(sorted(disclosed))}) está na "
                    f"ancestralidade transitiva das cenas que formaram esta crença "
                    f"({', '.join(about_events) or 'nenhuma cena EV-* declarada'}) — a revelação muda "
                    "o que o leitor acredita ter acontecido sem ter sido plantada como causa (INV-11, "
                    "THE PAST MUST BE ABLE TO CHANGE WITHOUT THE PAST CHANGING).",
                    "Adicionar a GT divulgada a `caused_by` de ao menos uma cena listada em "
                    "`beliefs[].about`, ou revisar uma crença cuja ancoragem já exista."))
    return findings


def check_reader_omniscience(ledger: dict, idx: dict) -> list[dict]:
    """INV-12: o leitor não pode aprender uma Ground Truth antes do evento
    declarado em `reader_access.from_event`, e nunca aprende uma GT marcada
    `NEVER`. Uma GT sem `reader_access` declarado é, por padrão, engine-only
    (mesmo critério do template: 'nunca entregue ao leitor por padrão')."""
    findings = []
    gt_owner_char = {}
    reader_access = {}
    for char in ledger.get("characters") or []:
        for gt in char.get("ground_truth") or []:
            gid = gt.get("id")
            gt_owner_char[gid] = char.get("id")
            reader_access[gid] = gt.get("reader_access")

    events = sorted(ledger.get("events") or [], key=lambda e: (e.get("chapter", 0),))
    for ev in events:
        chapter = ev.get("chapter", "WHOLE_BOOK")
        for kd in ev.get("knowledge_delta") or []:
            if kd.get("knower") != "READER":
                continue
            for gid in kd.get("learns") or []:
                if gid not in reader_access:
                    continue  # não é uma GT (pode ser um EV-* — fato de enredo, sem restrição de reader_access)
                access = reader_access.get(gid)
                if access is None or access == "NEVER":
                    findings.append(finding(
                        "READER_OMNISCIENCE_LEAK", "HIGH", chapter, f"{ev['id']} READER learns {gid}",
                        f"'{gid}' não declara reader_access permissivo (ou declara NEVER) — "
                        "esta Ground Truth não deveria chegar ao leitor por padrão (LAW 04: "
                        "THE ENGINE KNOWS CAUSALITY. THE READER RECEIVES EVIDENCE.).",
                        "Remover este knowledge_delta, ou declarar reader_access explícito "
                        "(OPEN ou {from_event: ...}) na Ground Truth."))
                    continue
                if access == "OPEN":
                    continue
                required_event = access.get("from_event") if isinstance(access, dict) else None
                required_ev = idx["ev_by_id"].get(required_event)
                if required_ev is None:
                    continue
                if ev["id"] != required_event and ev.get("chapter", 0) < required_ev.get("chapter", 0):
                    findings.append(finding(
                        "READER_OMNISCIENCE_LEAK", "HIGH", chapter, f"{ev['id']} READER learns {gid}",
                        f"'{gid}' só deveria chegar ao leitor em '{required_event}' (cap. "
                        f"{required_ev.get('chapter')}), mas foi entregue antes, no capítulo {chapter}.",
                        "Mover este knowledge_delta para o evento de revelação declarado, ou "
                        "corrigir reader_access.from_event."))
    return findings


def check_information_leak(ledger: dict, idx: dict) -> list[dict]:
    """INV-13: um conhecedor não pode agir sobre o que ainda não aprendeu.
    Conhecimento trivial (a própria Ground Truth de quem age; ter estado
    presente num evento anterior) é automático e não exige knowledge_delta
    explícito."""
    findings = []
    # conhecimento explícito acumulado por conhecedor, em ordem de capítulo
    learned_by: dict[str, set[str]] = defaultdict(set)
    events = sorted(enumerate(ledger.get("events") or []), key=lambda pair: (pair[1].get("chapter", 0), pair[0]))

    for _, ev in events:
        actor = ev.get("actor")
        chapter = ev.get("chapter", "WHOLE_BOOK")
        for token in ev.get("acts_on_knowledge") or []:
            known = False
            if isinstance(token, str) and token.startswith("GT-") and idx["gt_owner"].get(token) == actor:
                known = True  # autoconhecimento é automático
            elif isinstance(token, str) and token.startswith("EV-"):
                prior = idx["ev_by_id"].get(token)
                if prior is not None and actor in _participants_of(prior):
                    known = True  # ter estado lá é conhecimento trivial
            if not known and token in learned_by.get(actor, set()):
                known = True
            if not known:
                findings.append(finding(
                    "INFORMATION_LEAK", "HIGH", chapter, f"{ev['id']}.acts_on_knowledge={token}",
                    f"'{actor}' age com base em '{token}' sem ainda tê-lo aprendido — "
                    "assimetria de informação violada (INV-13).",
                    "Adicionar um knowledge_delta anterior que dê a este conhecedor acesso a "
                    "esta informação, ou remover a dependência de acts_on_knowledge."))
        for kd in ev.get("knowledge_delta") or []:
            knower = kd.get("knower")
            for item in kd.get("learns") or []:
                learned_by[knower].add(item)
    return findings


def check_belief_soft(ledger: dict) -> list[dict]:
    """SOFT-03: crença cujo `truth` não é TRUE precisa ser revisada em algum
    momento, ou explicitamente marcada `left_open` — senão fica pendurada sem
    intenção declarada."""
    findings = []
    revised_ids = set()
    for ev in ledger.get("events") or []:
        revised_ids |= set((ev.get("beliefs") or {}).get("revises") or [])
    for rb in ledger.get("beliefs") or []:
        if rb.get("truth") in (None, "TRUE"):
            continue
        if rb.get("id") in revised_ids or rb.get("left_open"):
            continue
        findings.append(finding(
            "UNRESOLVED_BELIEF", "MEDIUM", "WHOLE_BOOK", rb.get("id"),
            f"Crença '{rb.get('id')}' com truth={rb.get('truth')} nunca é revisada nem marcada "
            "left_open (SOFT-03).",
            "Revisar esta crença em algum evento posterior, ou marcar left_open: true se o "
            "livro deixa a ambiguidade deliberadamente aberta."))
    return findings


# --- L8 — consentimento canônico e consent drift (LAW 01/02, invariantes) --

def check_consent_structure(ledger: dict) -> list[dict]:
    """INV-07: evento adulto ou de coerção exige bloco `consent` completo, e
    `perceived` nunca contém a chave `canonical` (a percepção de alguém não
    pode se disfarçar de fato canônico)."""
    findings = []
    for ev in ledger.get("events") or []:
        kinds = set(ev.get("kind") or [])
        if not (kinds & CONSENT_REQUIRED_KINDS):
            continue
        chapter = ev.get("chapter", "WHOLE_BOOK")
        consent = ev.get("consent")
        if not consent:
            findings.append(finding(
                "CONSENT_MISSING", "HIGH", chapter, ev.get("id"),
                "Evento de sedução/erotismo/intimidade/coerção sem bloco `consent` (INV-07) — "
                "consentimento canônico não pode ficar implícito.",
                "Adicionar o bloco `consent` com canonical, manipulation_present, "
                "power_imbalance_present, ability_to_refuse e boundary_state."))
            continue
        if "canonical" in (consent.get("perceived") or {}):
            findings.append(finding(
                "CONSENT_LAYER_COLLAPSE", "HIGH", chapter, f"{ev['id']}.consent.perceived.canonical",
                "`perceived` contém a chave `canonical` — a percepção de um personagem ou do "
                "leitor não pode se sobrepor ao consentimento canônico "
                "(CANONICAL_CONSENT ≠ CHARACTER_A_PERCEPTION ≠ CHARACTER_B_PERCEPTION ≠ "
                "READER_PERCEPTION).",
                "Remover `canonical` de dentro de `perceived`; o valor canônico vive só em "
                "`consent.canonical`."))
    return findings


def check_consent_payoff(ledger: dict, idx: dict) -> list[dict]:
    """INV-09: um evento com consentimento canônico COERCIVE ou
    NON_CONSENSUAL não pode resolver (recompensar) um loop INTIMACY/EROTIC —
    pode alimentar ou abrir loops de consequência (RELATIONAL, POWER,
    VULNERABILITY), nunca funcionar como payoff desejável."""
    findings = []
    for ev in ledger.get("events") or []:
        consent = ev.get("consent") or {}
        if consent.get("canonical") not in COERCIVE_CONSENT_VALUES:
            continue
        for r in (ev.get("loops") or {}).get("resolves") or []:
            loop = idx["lp_by_id"].get(r.get("loop"))
            if loop is not None and loop.get("kind") in ADULT_LOOP_KINDS:
                findings.append(finding(
                    "COERCION_AS_PAYOFF", "HIGH", ev.get("chapter", "WHOLE_BOOK"),
                    f"{ev['id']} resolves {r.get('loop')} (consent.canonical={consent.get('canonical')})",
                    "Evento com consentimento COERCIVE/NON_CONSENSUAL não pode funcionar como "
                    "payoff de um loop de intimidade/erótico — coerção é consequência, nunca "
                    "recompensa (INV-09).",
                    "Reclassificar este evento como consequência (abrindo/alimentando um loop "
                    "RELATIONAL, POWER ou VULNERABILITY), nunca como resolução de um loop "
                    "INTIMACY/EROTIC."))
    return findings


def check_baseline_immutability(ledger: dict, idx: dict, baseline: dict) -> tuple[list[dict], set[str]]:
    """L10 / INV-08 / INV-10: nada que já foi aprovado numa wave anterior
    pode ser reescrito por uma wave posterior. `PAST_FACTS = CONSTANT`;
    `consent` canônico segue a mesma regra (consent drift é uma forma de
    retcon). Retorna (achados, ids de evento cujos `facts`/`caused_by`
    divergiram do snapshot — usado por `second_read_classifications` para
    rebaixar a pré-classificação do Second-Read quando o passado foi
    alterado)."""
    findings: list[dict] = []
    tampered: set[str] = set()

    baseline_events = {e.get("id"): e for e in baseline.get("events") or []}
    for eid, bev in baseline_events.items():
        cur = idx["ev_by_id"].get(eid)
        if cur is None:
            findings.append(finding(
                "RETCON", "HIGH", "WHOLE_BOOK", eid,
                f"Evento '{eid}' existe no snapshot aprovado mas desapareceu do ledger atual.",
                "Um evento REALIZED de wave já aprovada não pode ser removido."))
            tampered.add(eid)
            continue
        chapter = cur.get("chapter", "WHOLE_BOOK")
        if cur.get("facts") != bev.get("facts"):
            findings.append(finding(
                "RETCON", "HIGH", chapter, f"{eid}.facts",
                "`facts` divergem do snapshot da wave já aprovada — PAST_FACTS = CONSTANT (INV-10).",
                "Reverter `facts` ao valor aprovado; uma reinterpretação nunca altera o que "
                "de fato ocorreu."))
            tampered.add(eid)
        if cur.get("caused_by") != bev.get("caused_by"):
            findings.append(finding(
                "RETCON", "HIGH", chapter, f"{eid}.caused_by",
                "`caused_by` diverge do snapshot da wave já aprovada (INV-10).",
                "Reverter a ancestralidade causal ao valor aprovado."))
            tampered.add(eid)
        if bev.get("consent") != cur.get("consent"):
            findings.append(finding(
                "CONSENT_DRIFT", "HIGH", chapter, f"{eid}.consent",
                "Bloco `consent` diverge do snapshot da wave já aprovada (INV-08) — "
                "consentimento não pode ser reescrito para tornar um payoff palatável depois.",
                "Reverter `consent` ao valor aprovado; uma mudança de interpretação nunca "
                "altera o consentimento canônico já registrado."))

    baseline_gt: dict[str, str] = {}
    for char in baseline.get("characters") or []:
        for gt in char.get("ground_truth") or []:
            baseline_gt[gt.get("id")] = gt.get("statement")
    for gid, statement in baseline_gt.items():
        cur_gt = idx["gt_by_id"].get(gid)
        if cur_gt is not None and cur_gt.get("statement") != statement:
            findings.append(finding(
                "RETCON", "HIGH", "WHOLE_BOOK", gid,
                f"Ground Truth '{gid}' divergente do snapshot aprovado.",
                "Ground Truth já citada/divulgada é congelada (INV-10); registrar uma nova "
                "GT em vez de reescrever esta."))
            tampered.add(gid)
    return findings, tampered


# --- L5 — pré-classificação do Second-Read Test (consulta, não achado) -----

def second_read_classifications(ledger: dict, idx: dict,
                                 tampered_event_ids: set[str] | None = None) -> dict:
    """Pré-classificação estrutural de STRONG/PARTIAL/WEAK por crença
    revisada (I.2 do SDD). É evidência, não veredito — o veredito literário
    cabe à auditoria de cena protegida da revelação. Por isso NÃO entra na
    lista de `findings` de `validate()`; é só consultável (--recontextualized)."""
    tampered = tampered_event_ids or set()
    beliefs_by_id = {b.get("id"): b for b in ledger.get("beliefs") or []}
    revisions = [
        (ev, revises) for ev in (ledger.get("events") or [])
        if (revises := (ev.get("beliefs") or {}).get("revises"))
    ]
    results: dict[str, dict] = {}
    for ev, rb_ids in revisions:
        # Duas granularidades deliberadamente distintas: `aggregate_*` mede o
        # alcance da REVELAÇÃO como um todo (quantas cenas, em quantos
        # capítulos, ela recontextualiza — é isso que decide STRONG, porque
        # duas crenças reveladas juntas por um mesmo evento compartilham a
        # força dessa revelação); `own_recontextualized` é específico de CADA
        # crença, para o relatório nunca atribuir a uma crença uma cena que
        # não é dela (RB-01.about=[EV-01] não pode "recontextualizar" EV-03).
        per_belief_recontextualized: dict[str, set[str]] = {}
        aggregate_recontextualized: set[str] = set()
        ancestry_ok_all = True
        facts_ok_all = True
        for rb_id in rb_ids:
            rb = beliefs_by_id.get(rb_id)
            if rb is None:
                per_belief_recontextualized[rb_id] = set()
                continue
            disclosed = set(rb.get("disclosed_by_revision") or [])
            about_events = [a for a in (rb.get("about") or []) if isinstance(a, str) and a.startswith("EV-")]
            own = set()
            for about_id in about_events:
                if about_id in tampered:
                    facts_ok_all = False
                ancestors = transitive_gt_ancestors(idx, about_id)
                if disclosed and (disclosed & ancestors):
                    own.add(about_id)
                    aggregate_recontextualized.add(about_id)
                elif disclosed:
                    ancestry_ok_all = False
            per_belief_recontextualized[rb_id] = own
        distinct_chapters = {
            idx["ev_by_id"][eid]["chapter"] for eid in aggregate_recontextualized if eid in idx["ev_by_id"]
        }
        for rb_id in rb_ids:
            rb = beliefs_by_id.get(rb_id)
            if rb is None:
                continue
            confidence = rb.get("confidence")
            own = per_belief_recontextualized[rb_id]
            if not ancestry_ok_all or not facts_ok_all:
                classification = "WEAK"
            elif len(distinct_chapters) >= 2 and confidence in ("MEDIUM", "HIGH"):
                classification = "STRONG"
            elif own:
                classification = "PARTIAL"
            else:
                classification = "WEAK"
            results[rb_id] = {
                "classification": classification,
                "revealing_event": ev.get("id"),
                "recontextualized_events": sorted(own),
                "distinct_chapters": sorted(distinct_chapters),
                "confidence": confidence,
            }
    return results


def recontextualized_report(ledger: dict, idx: dict,
                             tampered_event_ids: set[str] | None = None) -> list[dict]:
    classifications = second_read_classifications(ledger, idx, tampered_event_ids)
    tampered = tampered_event_ids or set()
    out = []
    for rb_id, result in classifications.items():
        for eid in result["recontextualized_events"]:
            ev = idx["ev_by_id"].get(eid)
            out.append({
                "belief": rb_id,
                "event": eid,
                "chapter": ev.get("chapter") if ev else None,
                "facts_unchanged": "não" if eid in tampered else "sim",
                "classification": result["classification"],
            })
    return out


def knowledge_state(ledger: dict, knower: str, at_chapter: int | None = None) -> list[str]:
    """--knowledge KNOWER [--at-chapter N]: o que este conhecedor (um
    personagem, ou 'READER') já aprendeu, em ordem de aquisição."""
    learned: list[str] = []
    events = sorted(enumerate(ledger.get("events") or []), key=lambda pair: (pair[1].get("chapter", 0), pair[0]))
    for _, ev in events:
        if at_chapter is not None and ev.get("chapter", 0) > at_chapter:
            break
        for kd in ev.get("knowledge_delta") or []:
            if kd.get("knower") == knower:
                for item in kd.get("learns") or []:
                    if item not in learned:
                        learned.append(item)
    return learned


def beliefs_state(ledger: dict, at_chapter: int | None = None, engine_view: bool = False) -> list[dict]:
    """--beliefs [--at-chapter N]: crenças ativas do leitor neste ponto da
    obra. Por padrão (sem --engine-view) omite `truth` e `disclosed_by_revision`
    — a mesma proteção contra vazamento descrita na seção N do SDD."""
    established_at: dict[str, int] = {}
    revised_at: dict[str, int] = {}
    for ev in sorted(ledger.get("events") or [], key=lambda e: e.get("chapter", 0)):
        chapter = ev.get("chapter", 0)
        bl = ev.get("beliefs") or {}
        for rb_id in bl.get("establishes") or []:
            established_at.setdefault(rb_id, chapter)
        for rb_id in bl.get("revises") or []:
            revised_at.setdefault(rb_id, chapter)

    out = []
    for rb in ledger.get("beliefs") or []:
        rb_id = rb.get("id")
        est = established_at.get(rb_id)
        if est is None or (at_chapter is not None and est > at_chapter):
            continue
        rev = revised_at.get(rb_id)
        rev_visible = rev is not None and (at_chapter is None or rev <= at_chapter)
        entry = {
            "id": rb_id,
            "interpretation": rb.get("interpretation"),
            "confidence": rb.get("confidence"),
            "expectation": rb.get("expectation"),
            "established_chapter": est,
            "revised_chapter": rev if rev_visible else None,
            "active": not rev_visible,
        }
        if engine_view:
            entry["truth"] = rb.get("truth")
            entry["disclosed_by_revision"] = rb.get("disclosed_by_revision") or []
        out.append(entry)
    return out


# --- L6 — amplitude emocional por contraste (LAW 05) ------------------------
#
# Opera sobre `book/chapter_architecture.yaml` (campo `emotional_movement`),
# NUNCA sobre o ledger: é STORY PLANNING, não CANON (E.4 do SDD). Um plano de
# capítulo pode mudar livremente sem virar retcon, porque o leitor ainda não
# viu — daí viver num arquivo separado do `CAUSAL_LEDGER.yaml`.

def check_emotional_amplitude(chapters: list[dict], config: dict | None = None) -> list[dict]:
    """LAW 05 (intensidade emerge de contraste, não de escalada contínua):
    SOFT-01 `CONTINUOUS_ESCALATION` e SOFT-02 `PEAK_WITHOUT_CONTRAST`. Ambos
    são soft (MEDIUM) — quem decide se a curva funciona é o EMOTIONAL_EDITOR;
    isto só sinaliza o padrão estrutural."""
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    max_run = cfg.get("max_monotonic_run", DEFAULT_CONFIG["max_monotonic_run"])
    findings: list[dict] = []

    entries = sorted(
        ((c.get("number"), (c.get("emotional_movement") or {}).get("intensity")) for c in chapters),
        key=lambda pair: pair[0] if pair[0] is not None else 0,
    )
    for number, intensity in entries:
        if intensity not in INTENSITY_ORDER:
            findings.append(finding(
                "INVALID_ENUM", "HIGH", number, f"chapter {number}.emotional_movement.intensity={intensity}",
                "intensity deve ser LOW, MEDIUM, HIGH ou PEAK.", "Corrigir o valor."))
    valid = [(n, i) for n, i in entries if i in INTENSITY_ORDER]

    run_start = 0
    for i in range(1, len(valid) + 1):
        broke = i == len(valid) or INTENSITY_ORDER[valid[i][1]] < INTENSITY_ORDER[valid[i - 1][1]]
        if broke:
            run_len = i - run_start
            if run_len > max_run:
                chapters_in_run = [valid[k][0] for k in range(run_start, i)]
                findings.append(finding(
                    "CONTINUOUS_ESCALATION", "MEDIUM", chapters_in_run[-1],
                    f"capítulos {chapters_in_run}",
                    f"{run_len} capítulos consecutivos com intensidade emocional não decrescente "
                    f"(limite: {max_run}) — LAW 05 pede contraste (TRUST→BETRAYAL, SAFETY→DANGER...), "
                    "não escalada contínua de darkness/choque/violência.",
                    "Intercalar um capítulo de intensidade menor (um vale) antes de continuar a escalada, "
                    "ou dividir a wave para que a curva respire."))
            run_start = i

    window = 2
    for pos, (number, intensity) in enumerate(valid):
        if intensity != "PEAK":
            continue
        preceding = valid[max(0, pos - window):pos]
        has_valley = any(INTENSITY_ORDER[i] <= INTENSITY_ORDER[CONTRAST_CEILING] for _, i in preceding)
        if not has_valley:
            findings.append(finding(
                "PEAK_WITHOUT_CONTRAST", "MEDIUM", number, f"chapter {number}",
                f"Capítulo de intensidade PEAK sem um vale (LOW/MEDIUM) nos {window} capítulos "
                "anteriores — um pico perde força sem contraste prévio (LAW 05).",
                "Inserir ou preservar um capítulo de intensidade LOW/MEDIUM pouco antes deste pico."))
    return findings


# --- L9 — memória de continuação --------------------------------------------

def end_state(ledger: dict, idx: dict) -> dict:
    """--end-state: o que o livro precisa lembrar para continuar. Nada aqui é
    recomputado ad hoc em prosa — é a mesma projeção usada no resto do
    script, só que tomada no último capítulo do ledger."""
    loop_ids = {lp.get("id") for lp in ledger.get("loops") or []}
    resolved_ids = set()
    for ev in ledger.get("events") or []:
        for r in (ev.get("loops") or {}).get("resolves") or []:
            resolved_ids.add(r.get("loop"))
    open_loops = [lp for lp in ledger.get("loops") or [] if lp.get("id") in (loop_ids - resolved_ids)]

    established_ids: set[str] = set()
    revised_ids: set[str] = set()
    for ev in ledger.get("events") or []:
        bl = ev.get("beliefs") or {}
        established_ids |= set(bl.get("establishes") or [])
        revised_ids |= set(bl.get("revises") or [])
    open_beliefs = [
        b for b in ledger.get("beliefs") or []
        if b.get("id") in established_ids and b.get("id") not in revised_ids
    ]

    relationship_states = {}
    for rel in ledger.get("relationships") or []:
        pair = rel.get("pair", "")
        if "->" not in pair:
            continue
        from_id, to_id = pair.split("->", 1)
        relationship_states[pair] = relationship_state(ledger, from_id, to_id)

    reader_learned = set(knowledge_state(ledger, "READER"))
    undisclosed_gt = [
        {"id": gt.get("id"), "owner": char.get("id"), "kind": gt.get("kind")}
        for char in ledger.get("characters") or []
        for gt in char.get("ground_truth") or []
        if gt.get("id") not in reader_learned
    ]

    return {
        "open_loops": [
            {"id": lp.get("id"), "kind": lp.get("kind"), "pair": lp.get("pair"), "question": lp.get("question")}
            for lp in open_loops
        ],
        "open_beliefs": [
            {"id": b.get("id"), "interpretation": b.get("interpretation"), "confidence": b.get("confidence")}
            for b in open_beliefs
        ],
        "relationship_states": relationship_states,
        "undisclosed_ground_truth": undisclosed_gt,
    }


# --- orquestração ------------------------------------------------------------

def validate(ledger: dict, mode: str = "plan", config: dict | None = None,
             baseline: dict | None = None, chapter_architecture: list[dict] | None = None) -> list[dict]:
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    idx, dup_findings = build_indices(ledger)

    findings: list[dict] = []
    findings += dup_findings
    findings += check_integrity(ledger)
    findings += check_participant_references(ledger, idx)
    findings += check_character_layers(ledger)
    findings += check_attraction_attribute(ledger)
    findings += check_causal_references(ledger, idx)
    findings += check_structural_mutation(ledger)
    _, _, state_reset_findings = relationship_projection(ledger)
    findings += state_reset_findings
    findings += check_payoffs(ledger, idx, cfg)
    findings += check_adult_gate(ledger, idx)
    findings += check_unused_ground_truth(ledger)
    # Slice 2
    findings += check_belief_revision_ancestry(ledger, idx)
    findings += check_reader_omniscience(ledger, idx)
    findings += check_information_leak(ledger, idx)
    findings += check_belief_soft(ledger)
    findings += check_consent_structure(ledger)
    findings += check_consent_payoff(ledger, idx)
    if baseline is not None:
        baseline_findings, _tampered = check_baseline_immutability(ledger, idx, baseline)
        findings += baseline_findings
    # Slice 3 — L6. Só roda quando o chamador fornece chapter_architecture
    # explicitamente: não está no ledger, então não há custo de import.
    if chapter_architecture is not None:
        findings += check_emotional_amplitude(chapter_architecture, cfg)
    # `mode` diferencia `plan` de `realized`/`final` só pela presença
    # esperada de `baseline` — todas as regras acima se aplicam igualmente a
    # eventos PLANNED e REALIZED.
    del mode
    return findings


# --- consultas de explicabilidade (seção N do SDD) --------------------------

def why_report(ledger: dict, idx: dict, event_id: str) -> dict:
    """Responde 'por que este personagem fez isto?' com a árvore de causa até
    Ground Truth, e se a autoexplicação do personagem diverge da causa real."""
    ev = idx["ev_by_id"].get(event_id)
    if ev is None:
        return {"event": event_id, "found": False}

    sa_id = ev.get("self_attribution")
    sa = idx["sm_by_id"].get(sa_id) if sa_id else None

    ancestors: list[dict] = []

    def walk(token: str, seen: frozenset):
        if token in seen:
            ancestors.append({"type": "CYCLE", "id": token})
            return
        seen = seen | {token}
        if token.startswith("GT-"):
            gt = idx["gt_by_id"].get(token)
            ancestors.append({
                "type": "GT", "id": token, "owner": idx["gt_owner"].get(token),
                "kind": gt.get("kind") if gt else None,
                "statement": gt.get("statement") if gt else None,
            })
        elif token.startswith("EV-"):
            cause_ev = idx["ev_by_id"].get(token)
            ancestors.append({
                "type": "EV", "id": token,
                "chapter": cause_ev.get("chapter") if cause_ev else None,
                "facts": cause_ev.get("facts") if cause_ev else None,
            })
            if cause_ev:
                for nxt in cause_ev.get("caused_by") or []:
                    walk(nxt, seen)
        else:
            ancestors.append({"type": "UNRESOLVED", "id": token})

    for token in ev.get("caused_by") or []:
        walk(token, frozenset())

    return {
        "event": event_id, "found": True, "chapter": ev.get("chapter"),
        "facts": ev.get("facts"), "actor": ev.get("actor"),
        "self_attribution": (
            {"id": sa_id, "statement": sa.get("statement") if sa else None}
            if sa_id else None
        ),
        "diverges_from_cause": bool(sa and sa.get("diverges_from")),
        "ancestors": ancestors,
    }


def relationship_timeline(ledger: dict, from_id: str, to_id: str,
                           at_chapter: int | None = None) -> list[dict]:
    pair = f"{from_id}->{to_id}"
    timeline, _, _ = relationship_projection(ledger)
    entries = timeline.get(pair, [])
    if at_chapter is not None:
        entries = [e for e in entries if e["chapter"] is None or e["chapter"] <= at_chapter]
    return entries


def relationship_state(ledger: dict, from_id: str, to_id: str,
                        at_chapter: int | None = None) -> dict:
    pair = f"{from_id}->{to_id}"
    state = {}
    for rel in ledger.get("relationships") or []:
        if rel.get("pair") == pair:
            state = dict(rel.get("baseline") or {})
            break
    for entry in relationship_timeline(ledger, from_id, to_id, at_chapter):
        state[entry["dimension"]] = entry["to"]
    return state


def payoff_report(ledger: dict, idx: dict, event_id: str) -> dict:
    ev = idx["ev_by_id"].get(event_id)
    if ev is None:
        return {"event": event_id, "found": False}
    resolves = (ev.get("loops") or {}).get("resolves") or []
    out_resolves = []
    events = ledger.get("events") or []
    for r in resolves:
        loop_id = r.get("loop")
        opened_before = [
            e for e in events
            if loop_id in ((e.get("loops") or {}).get("opens") or [])
            and e.get("chapter", 0) < ev.get("chapter", 0)
        ]
        feeders = [
            e for e in events
            if loop_id in ((e.get("loops") or {}).get("feeds") or [])
            and e.get("chapter", 0) < ev.get("chapter", 0)
        ]
        out_resolves.append({
            "loop": loop_id,
            "question": (idx["lp_by_id"].get(loop_id) or {}).get("question"),
            "mode": r.get("mode"),
            "into": r.get("into"),
            "why_now": r.get("why_now") or [],
            "opened_by": [{"event": e["id"], "chapter": e.get("chapter")} for e in opened_before],
            "fed_by": [{"event": e["id"], "chapter": e.get("chapter")} for e in feeders],
        })
    return {
        "event": event_id, "found": True, "chapter": ev.get("chapter"),
        "relationship_delta": ev.get("relationship_delta") or [],
        "resolves": out_resolves,
    }


# --- snapshot determinístico (usado pelo compositor via TOOL_BY_PATTERN) ---

def build_snapshot_document(ledger: dict) -> dict:
    """Recorte imutável do ledger: só o que L10 precisa comparar depois —
    `facts`/`caused_by`/`consent` dos eventos REALIZED e o texto das Ground
    Truth já registradas. Nunca inclui eventos PLANNED (ainda não aprovados,
    livres para mudar) nem estado projetado (que não é armazenado em lugar
    nenhum, por desenho — ver E.2 do SDD)."""
    events = [
        {"id": ev.get("id"), "facts": ev.get("facts"), "caused_by": ev.get("caused_by"),
         "consent": ev.get("consent")}
        for ev in ledger.get("events") or [] if ev.get("status") == "REALIZED"
    ]
    characters = [
        {"id": char.get("id"),
         "ground_truth": [{"id": gt.get("id"), "statement": gt.get("statement")}
                          for gt in char.get("ground_truth") or []]}
        for char in ledger.get("characters") or []
    ]
    realized_chapters = [ev.get("chapter") for ev in ledger.get("events") or [] if ev.get("status") == "REALIZED"]
    return {
        "apiVersion": "pedroarte.livingbooks/v1",
        "kind": "CausalLedgerSnapshot",
        "metadata": {
            "project_id": (ledger.get("metadata") or {}).get("project_id"),
            "through_chapter": max(realized_chapters, default=0),
        },
        "events": events,
        "characters": characters,
    }


def snapshot_auto(ledger_path: Path, ledger: dict) -> Path:
    """--snapshot-auto: escreve o PRÓXIMO snapshot numerado ao lado do
    ledger (`<parent>/snapshots/CAUSAL_LEDGER.WAVE_NN.yaml`). 100% mecânico —
    nenhum julgamento envolvido — por isso é elegível a `tool` no grafo em
    vez de exigir um agente (ver TOOL_BY_PATTERN em engine/scripts/livingbook.py)."""
    snap_dir = ledger_path.parent / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    existing = []
    for p in snap_dir.glob("CAUSAL_LEDGER.WAVE_*.yaml"):
        m = re.search(r"WAVE_(\d+)\.yaml$", p.name)
        if m:
            existing.append(int(m.group(1)))
    next_index = (max(existing) + 1) if existing else 0
    out_path = snap_dir / f"CAUSAL_LEDGER.WAVE_{next_index:02d}.yaml"
    document = build_snapshot_document(ledger)
    out_path.write_text(
        yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")
    return out_path


# --- relatório / CLI ---------------------------------------------------------

def render_report(findings: list[dict], source: str) -> str:
    out = [
        "# Relatório do Causal Ledger\n\n",
        f"Fonte: `{source}`\n\n",
        "Gerado por `engine/scripts/check_causal_ledger.py` (Slices 1-3: L0-L10 completo). "
        "Ver docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md.\n\n",
    ]
    if not findings:
        out.append("Nenhum achado. Ledger consistente para as regras deste slice.\n")
        return "".join(out)
    counts: dict[str, int] = defaultdict(int)
    for f in findings:
        counts[f["severity"]] += 1
    out.append("| Severidade | Achados |\n|---|---:|\n")
    for sev in reversed(SEVERITY_ORDER):
        if counts.get(sev):
            out.append(f"| {sev} | {counts[sev]} |\n")
    out.append("\n")
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        by_cat[f["category"]].append(f)
    for cat, items in by_cat.items():
        out.append(f"## {cat} ({len(items)})\n\n")
        for f in items:
            out.append(f"- **{f['severity']}** (cap. {f['chapter']}) — `{f['evidence']}`\n")
            out.append(f"  - {f['detail']}\n")
            out.append(f"  - Ação sugerida: {f['recommended_action']}\n")
        out.append("\n")
    return "".join(out)


def _load_ledger_path(args) -> Path:
    if args.ledger:
        return args.ledger
    if args.runtime:
        return args.runtime / "canon" / "CAUSAL_LEDGER.yaml"
    raise SystemExit("informe --ledger ou --runtime")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validador determinístico do CAUSAL_LEDGER.yaml (DARK_ROMANCE_CANON_ARCHITECT).")
    parser.add_argument("--runtime", type=Path, help="Raiz do runtime; lê canon/CAUSAL_LEDGER.yaml.")
    parser.add_argument("--ledger", type=Path, help="Caminho direto para um CAUSAL_LEDGER.yaml.")
    parser.add_argument("--mode", choices=["plan", "realized", "final"], default="plan")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--why", metavar="EVENT_ID")
    parser.add_argument("--relationship", nargs=2, metavar=("FROM", "TO"))
    parser.add_argument("--payoff", metavar="EVENT_ID")
    parser.add_argument("--at-chapter", type=int)
    parser.add_argument("--baseline", type=Path,
                         help="Snapshot aprovado (CausalLedgerSnapshot) para checar imutabilidade (L10).")
    parser.add_argument("--knowledge", metavar="KNOWER",
                         help="O que este conhecedor ('READER' ou um id de personagem) já aprendeu.")
    parser.add_argument("--beliefs", action="store_true", help="Crenças ativas do leitor.")
    parser.add_argument("--recontextualized", action="store_true",
                         help="Cenas recontextualizadas por revelações, com pré-classificação do Second-Read Test.")
    parser.add_argument("--engine-view", action="store_true",
                         help="Com --beliefs, inclui `truth` e `disclosed_by_revision` (nunca use isto para gerar prompt de escrita para o leitor).")
    parser.add_argument("--chapter-architecture", type=Path,
                         help="book/chapter_architecture.yaml — ativa L6 (amplitude emocional). "
                              "Nunca embutido no CAUSAL_LEDGER.yaml (é STORY PLANNING, não CANON).")
    parser.add_argument("--end-state", action="store_true",
                         help="Memória de continuação: loops abertos, crenças abertas, estado "
                              "relacional final e Ground Truth nunca divulgada ao leitor (L9).")
    parser.add_argument("--snapshot-auto", action="store_true",
                         help="Escreve o próximo snapshot numerado (canon/snapshots/CAUSAL_LEDGER.WAVE_NN.yaml) "
                              "a partir do estado atual do ledger. 100%% mecânico — usado como `tool` pelo compositor.")
    parser.add_argument("--min-payoff-feeds", type=int,
                         help="Override de BOOK_SPEC.features.causal_ledger.min_payoff_feeds (padrão: 2).")
    parser.add_argument("--max-monotonic-run", type=int,
                         help="Override de .max_monotonic_run (padrão: 3).")
    parser.add_argument("--max-loop-silence", type=int,
                         help="Override de .max_loop_silence (padrão: 6; reservado para uso futuro).")
    args = parser.parse_args()

    path = _load_ledger_path(args)
    if not path.is_file():
        print(f"CAUSAL_LEDGER não encontrado: {path}", file=sys.stderr)
        return 2
    ledger = load_yaml(path)
    idx, _ = build_indices(ledger)

    if args.snapshot_auto:
        out = snapshot_auto(path, ledger)
        print(f"SNAPSHOT OK | {out}")
        return 0

    baseline = load_yaml(args.baseline) if args.baseline else None
    chapter_architecture = None
    if args.chapter_architecture:
        arch = load_yaml(args.chapter_architecture)
        chapter_architecture = arch.get("chapters") or []
    config_overrides = {}
    if args.min_payoff_feeds is not None:
        config_overrides["min_payoff_feeds"] = args.min_payoff_feeds
    if args.max_monotonic_run is not None:
        config_overrides["max_monotonic_run"] = args.max_monotonic_run
    if args.max_loop_silence is not None:
        config_overrides["max_loop_silence"] = args.max_loop_silence

    if args.why:
        print(json.dumps(why_report(ledger, idx, args.why), ensure_ascii=False, indent=2))
        return 0
    if args.relationship:
        entries = relationship_timeline(ledger, args.relationship[0], args.relationship[1],
                                         args.at_chapter)
        print(json.dumps(entries, ensure_ascii=False, indent=2))
        return 0
    if args.payoff:
        print(json.dumps(payoff_report(ledger, idx, args.payoff), ensure_ascii=False, indent=2))
        return 0
    if args.knowledge:
        print(json.dumps(knowledge_state(ledger, args.knowledge, args.at_chapter), ensure_ascii=False, indent=2))
        return 0
    if args.beliefs:
        print(json.dumps(beliefs_state(ledger, args.at_chapter, engine_view=args.engine_view),
                          ensure_ascii=False, indent=2))
        return 0
    if args.recontextualized:
        tampered: set[str] = set()
        if baseline is not None:
            _, tampered = check_baseline_immutability(ledger, idx, baseline)
        print(json.dumps(recontextualized_report(ledger, idx, tampered_event_ids=tampered),
                          ensure_ascii=False, indent=2))
        return 0
    if args.end_state:
        print(json.dumps(end_state(ledger, idx), ensure_ascii=False, indent=2))
        return 0

    findings = validate(ledger, mode=args.mode, baseline=baseline,
                         chapter_architecture=chapter_architecture,
                         config=config_overrides or None)
    if args.json:
        print(json.dumps({"findings": findings}, ensure_ascii=False, indent=2))
    else:
        report = render_report(findings, str(path))
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(report, encoding="utf-8")
            print(f"Relatório: {args.out}")
        else:
            print(report)

    counts: dict[str, int] = defaultdict(int)
    for f in findings:
        counts[f["severity"]] += 1
    print(f"\nTOTAL: {len(findings)} achado(s) "
          f"({', '.join(f'{v} {k}' for k, v in counts.items()) or 'nenhum'})", file=sys.stderr)
    return 1 if any(f["severity"] in ("HIGH", "BLOCKER") for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
