"""Validador determinístico do bloco `representation` do `CAUSAL_LEDGER.yaml` —
capability `REPRESENTATION_INTEGRITY`.

Ver `docs/sdd/REPRESENTATION_INTEGRITY_SDD_v0.1.md` para o desenho completo.

    LIMITE DE GERAÇÃO != LIMITE DO UNIVERSO FICCIONAL

**Slice 1** (este arquivo) implementa o contrato e as permissões:

- integridade do bloco `representation` (enums, campos obrigatórios,
  `FORBIDDEN` nunca gravável);
- matriz SUBJECT_PERMISSION × SCENE_EXECUTION contra a política da autora
  (`REPRESENTATION_EXCEEDS_POLICY`);
- gate adulto: reuso de INV-06 (`ADULT_SEDUCTION_FAIL`) + `ADULT_KIND_MISSING`
  e `AGE_SOURCE_UNRESOLVED` (AG-01, AG-02);
- hard boundaries HB-01, HB-02 e HB-04 (fail closed, nunca viram gap);
- Authorial Gap: GAP-01, GAP-02, GAP-05 e a política `BLOCK` (Narciso).

Ficam para os próximos slices: snapshot do plano e Canon Sanitization Gate
(Slice 2), artefatos de geração, Dark Content Ledger e aviso ao leitor
(Slice 3), integração no compositor (Slice 4).

Princípios que este script respeita:

- **Nunca lê a prosa por tema.** Só campos estruturais declarados por quem
  planeja. Contexto > keyword.
- **Nenhuma regra depende do nome de um provider.** `generated_by` é
  telemetria e nem é lido aqui.
- **`FORBIDDEN` é projeção, nunca status.** Um hard boundary reprova o plano;
  nunca vira "lacuna para completar depois".
- **Nunca gera nem descreve o conteúdo que ficou de fora.**

Sem dependências novas: biblioteca padrão + PyYAML + `check_causal_ledger`.

Uso:
    python engine/scripts/check_representation.py --runtime runtime/<slug> --policy <politica.yaml>
    python engine/scripts/check_representation.py --ledger <ledger.yaml> --policy <politica.yaml> [--json]
    python engine/scripts/check_representation.py --ledger <f> --event EV-14
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import check_causal_ledger as cl

SEVERITY_ORDER = cl.SEVERITY_ORDER
BLOCKING = {"HIGH", "BLOCKER"}

# --- vocabulário fechado (ver REPRESENTATION_POLICY_TEMPLATE.yaml) ----------

CONTENT_CLASSES = {
    "SEXUAL", "SEXUAL_VIOLENCE", "VIOLENCE", "SELF_HARM", "ABUSE_CONTROL",
    "SUBSTANCE", "TABOO", "PSYCHOLOGICAL_EXTREMITY", "DEATH_GRIEF",
}
# FORBIDDEN não está aqui de propósito: é projeção de hard boundary, nunca
# valor gravável (AD-RI-06).
EXECUTIONS = {"NORMAL", "SENSITIVE", "FADE_TO_BLACK", "REFERENCE_ONLY"}
# Ordem de "presença na página" (14.2). Só para comparar redução; não é escore.
EXECUTION_RANK = {"NORMAL": 3, "SENSITIVE": 3, "FADE_TO_BLACK": 2, "REFERENCE_ONLY": 1}
STATUSES = {"FULLY_REPRESENTED", "CONSTRAINED", "AUTHOR_REVIEW"}
LIMITED_STATUSES = {"CONSTRAINED", "AUTHOR_REVIEW"}
CONSTRAINT_SOURCES = {"NONE", "PROVIDER_LIMIT", "CRAFT_CHOICE", "UNKNOWN"}
STRATEGIES = {
    "CAMERA_SHIFT", "ELLIPSIS", "AFTERMATH", "FRAGMENTED_MEMORY", "LATER_DIALOGUE",
    "CONSEQUENCE", "OBJECT_SYMBOL", "TESTIMONY", "INVESTIGATION", "FADE_TO_BLACK", "OTHER",
}
GAP_DIMENSIONS = {
    "EXPLICITNESS", "GRAPHIC_DETAIL", "PSYCHOLOGICAL_DEPTH", "ON_PAGE_PRESENCE",
    "DURATION", "OTHER",
}
AUTHOR_REVIEW_VALUES = {"RECOMMENDED", "REQUIRED"}
DEPICTION_CEILINGS = ("CAN_EXIST", "CAN_BE_DEPICTED", "CAN_BE_GRAPHICALLY_DEPICTED")
ON_CONSTRAINED_VALUES = {"RECORD_GAP", "BLOCK"}
MIN_INTENSITY, MAX_INTENSITY = 0, 10

DEFAULT_THRESHOLDS = {"gap_threshold": 2, "review_threshold": 4}

# Categorias que classificam o resultado como falha de hard boundary.
HARD_BOUNDARY_CATEGORIES = {
    "HARD_BOUNDARY_MINOR_SEXUALIZATION", "HARD_BOUNDARY_MINOR_ABUSE_DEPICTION",
    "HARD_BOUNDARY_GAP", "ADULT_SEDUCTION_FAIL", "ADULT_KIND_MISSING",
}


# --- utilidades -------------------------------------------------------------

def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _events_with_block(ledger: dict):
    for ev in ledger.get("events") or []:
        block = ev.get("representation")
        if isinstance(block, dict):
            yield ev, block


def _classes(block: dict) -> list:
    value = block.get("content_classes")
    return value if isinstance(value, list) else []


def _ages_of(idx: dict, block: dict, participant: str) -> list:
    """Idades que precisam TODAS ser adultas: a atual (ledger) e, se declarada,
    a idade no momento do evento. Usar as duas impede que `age_at_event` seja
    usado para 'lavar' um personagem cuja idade atual já não é adulta."""
    char = idx["char_index"].get(participant)
    ages = [char.get("age") if char else None]
    at_event = (block.get("age_at_event") or {})
    if participant in at_event:
        ages.append(at_event.get(participant))
    return ages


def _all_adult(ages: list) -> bool:
    return all(_is_int(a) and a >= cl.MIN_ADULT_AGE for a in ages)


def _any_minor_or_unknown(ages: list) -> bool:
    return any((not _is_int(a)) or a < cl.MIN_ADULT_AGE for a in ages)


def _is_erotic(ev: dict, block: dict) -> bool:
    return "SEXUAL" in _classes(block) or bool(set(ev.get("kind") or []) & cl.ADULT_EVENT_KINDS)


def _thresholds(policy: dict | None, overrides: dict | None = None) -> dict:
    out = dict(DEFAULT_THRESHOLDS)
    out.update((policy or {}).get("thresholds") or {})
    out.update(overrides or {})
    return out


# --- política da autora -----------------------------------------------------

def check_policy(policy: dict) -> list[dict]:
    """Integridade da política (o contrato é o template + este validador)."""
    out = []

    def bad(evidence, detail):
        out.append(cl.finding("POLICY_INVALID", "HIGH", "WHOLE_BOOK", evidence, detail,
                               "Corrigir a política conforme REPRESENTATION_POLICY_TEMPLATE.yaml."))

    if policy.get("kind") != "RepresentationPolicy":
        bad("kind", "kind deve ser RepresentationPolicy.")
    for family, cfg in (policy.get("permissions") or {}).items():
        if family not in CONTENT_CLASSES:
            bad(f"permissions.{family}", f"Família desconhecida. Válidas: {sorted(CONTENT_CLASSES)}.")
            continue
        cfg = cfg if isinstance(cfg, dict) else {}
        if cfg.get("depiction_ceiling") not in DEPICTION_CEILINGS:
            bad(f"permissions.{family}.depiction_ceiling", f"Valores: {', '.join(DEPICTION_CEILINGS)}.")
        if "central_theme" in cfg and not isinstance(cfg["central_theme"], bool):
            bad(f"permissions.{family}.central_theme", "central_theme deve ser booleano.")
    for family in policy.get("always_review") or []:
        if family not in CONTENT_CLASSES:
            bad(f"always_review.{family}", "Família desconhecida.")
    mode = policy.get("on_constrained_representation", "RECORD_GAP")
    if mode not in ON_CONSTRAINED_VALUES:
        bad("on_constrained_representation", "Valores: RECORD_GAP, BLOCK.")
    for key, value in (policy.get("thresholds") or {}).items():
        if key not in DEFAULT_THRESHOLDS or not _is_int(value) or value < 1:
            bad(f"thresholds.{key}", "Chaves: gap_threshold, review_threshold; inteiros >= 1.")
    for item in policy.get("additional_hard_boundaries") or []:
        if not (isinstance(item, dict) and item.get("id") and item.get("rule")):
            bad("additional_hard_boundaries", "Cada item precisa de id e rule (a política só acrescenta limites).")
    return out


# --- integridade do bloco `representation` ----------------------------------

def check_structure(ledger: dict) -> list[dict]:
    out = []
    for ev, block in _events_with_block(ledger):
        eid, chapter = ev.get("id"), ev.get("chapter", "WHOLE_BOOK")

        def enum(evidence, detail, action="Corrigir o valor."):
            out.append(cl.finding("INVALID_ENUM", "HIGH", chapter, f"{eid}.{evidence}", detail, action))

        def incomplete(evidence, detail):
            out.append(cl.finding("REPRESENTATION_INCOMPLETE", "HIGH", chapter, f"{eid}.{evidence}", detail,
                                   "Completar o bloco representation conforme o template."))

        classes = block.get("content_classes")
        if not isinstance(classes, list) or not classes:
            incomplete("representation.content_classes", "Pelo menos uma família de conteúdo é obrigatória.")
        else:
            for c in classes:
                if c not in CONTENT_CLASSES:
                    enum("representation.content_classes", f"Família '{c}' desconhecida. Válidas: {sorted(CONTENT_CLASSES)}.")
        themes = block.get("themes")
        if themes is not None and not (isinstance(themes, list) and all(isinstance(t, str) for t in themes)):
            enum("representation.themes", "themes deve ser uma lista de textos (vocabulário aberto da obra).")
        function = block.get("narrative_function")
        if not (isinstance(function, str) and function.strip()):
            incomplete("representation.narrative_function",
                       "A função narrativa é obrigatória: contexto declarado, nunca inferido de palavras.")

        def check_pair(name: str, part):
            if not isinstance(part, dict):
                incomplete(f"representation.{name}", f"{name} é obrigatório e deve ser um mapa.")
                return
            if part.get("execution") not in EXECUTIONS:
                enum(f"representation.{name}.execution",
                     f"execution deve ser {', '.join(sorted(EXECUTIONS))}. FORBIDDEN não é um valor gravável.")
            intensity = part.get("intensity")
            if not (_is_int(intensity) and MIN_INTENSITY <= intensity <= MAX_INTENSITY):
                enum(f"representation.{name}.intensity", "intensity deve ser inteiro de 0 a 10.")
            if not isinstance(part.get("graphic"), bool):
                enum(f"representation.{name}.graphic", "graphic deve ser booleano.")

        check_pair("intended", block.get("intended"))
        realized = block.get("realized")
        if realized is not None:
            check_pair("realized", realized)
            if isinstance(realized, dict):
                if realized.get("constraint_source") not in CONSTRAINT_SOURCES:
                    enum("representation.realized.constraint_source",
                         f"Valores: {', '.join(sorted(CONSTRAINT_SOURCES))}.")
                for s in realized.get("literary_strategy") or []:
                    if s not in STRATEGIES:
                        enum("representation.realized.literary_strategy", f"Estratégia '{s}' desconhecida.")
                rated = realized.get("rated_by") or {}
                if not isinstance(rated, dict) or not all(
                        _is_int(v) and MIN_INTENSITY <= v <= MAX_INTENSITY for v in rated.values()):
                    enum("representation.realized.rated_by", "rated_by: inteiros de 0 a 10.")

        status = block.get("status")
        if realized is not None and status is None:
            incomplete("representation.status", "Representação realizada exige status.")
        if status is not None and status not in STATUSES:
            enum("representation.status",
                 f"status deve ser {', '.join(sorted(STATUSES))}. FORBIDDEN nunca é gravado: é a projeção de "
                 "um hard boundary, e um hard boundary reprova o plano.",
                 "Corrigir o plano; um hard boundary não vira status.")
        if ev.get("status") == "PLANNED" and (realized is not None or status is not None):
            out.append(cl.finding(
                "REALIZED_BEFORE_REALIZATION", "HIGH", chapter, f"{eid}.representation",
                "Evento PLANNED não pode ter representation.realized nem status: só CANON_GUARDIAN "
                "promove o evento, depois que a prosa existe.",
                "Remover realized/status ou promover o evento a REALIZED."))
        gap = block.get("gap")
        if gap is not None:
            if not isinstance(gap, dict):
                enum("representation.gap", "gap deve ser um mapa.")
            else:
                dims = gap.get("dimensions")
                if not isinstance(dims, list) or not dims or any(d not in GAP_DIMENSIONS for d in dims):
                    enum("representation.gap.dimensions", f"dimensions: lista não vazia de {sorted(GAP_DIMENSIONS)}.")
                if not (isinstance(gap.get("description"), str) and gap["description"].strip()):
                    incomplete("representation.gap.description",
                               "O gap descreve a FUNÇÃO narrativa não realizada, em uma frase.")
                if gap.get("author_review") not in AUTHOR_REVIEW_VALUES:
                    enum("representation.gap.author_review", "Valores: RECOMMENDED, REQUIRED.")
        at_event = block.get("age_at_event")
        if at_event is not None and not (isinstance(at_event, dict) and all(_is_int(v) for v in at_event.values())):
            enum("representation.age_at_event", "age_at_event: mapa id -> idade inteira.")
    return out


# --- gate adulto e hard boundaries ------------------------------------------

def hard_boundary_events(ledger: dict, idx: dict) -> dict[str, list[str]]:
    """Eventos que disparam um hard boundary -> lista de ids (HB-01/HB-02).
    Usado também para isentar esses eventos das regras de gap: o que cruza um
    hard boundary não é 'representação limitada' (RI-LAW-07)."""
    triggered: dict[str, list[str]] = {}
    chapters_with_sexual = defaultdict(list)
    for ev, block in _events_with_block(ledger):
        if "SEXUAL" in _classes(block):
            chapters_with_sexual[ev.get("chapter")].append(ev.get("id"))
    for ev, block in _events_with_block(ledger):
        classes = _classes(block)
        participants = sorted(cl._participants_of(ev))
        if _is_erotic(ev, block):
            if any(not _all_adult(_ages_of(idx, block, p)) for p in participants):
                triggered.setdefault(ev.get("id"), []).append("HB-01")
        if "SEXUAL_VIOLENCE" in classes:
            if any(_any_minor_or_unknown(_ages_of(idx, block, p)) for p in participants):
                triggered.setdefault(ev.get("id"), []).append("HB-02")
    return triggered


def check_adult_gate_and_hard_boundaries(ledger: dict, idx: dict) -> list[dict]:
    out = list(cl.check_adult_gate(ledger, idx))          # REUSE: INV-06, BLOCKER, todo perfil
    for ev, block in _events_with_block(ledger):
        eid, chapter = ev.get("id"), ev.get("chapter", "WHOLE_BOOK")
        kinds = set(ev.get("kind") or [])
        if "SEXUAL" in _classes(block) and not (kinds & cl.ADULT_EVENT_KINDS):
            out.append(cl.finding(
                "ADULT_KIND_MISSING", "BLOCKER", chapter, f"{eid}.kind",
                "Evento com classe SEXUAL sem nenhum kind adulto (SEDUCTION, EROTIC_VERBAL, INTIMACY, "
                "SEXUAL): escaparia do gate adulto e do bloco consent (AG-01).",
                "Declarar o kind adulto do evento; isso liga INV-06 e INV-07."))
        if _is_erotic(ev, block):
            for p in sorted(cl._participants_of(ev)):
                char = idx["char_index"].get(p) or {}
                if not (isinstance(char.get("age_source"), str) and char["age_source"].strip()):
                    out.append(cl.finding(
                        "AGE_SOURCE_UNRESOLVED", "HIGH", chapter, f"{eid} participante {p}",
                        "Idade adulta sem age_source: a idade precisa de uma fonte canônica (AG-02).",
                        "Declarar age_source do personagem na bíblia."))
    triggered = hard_boundary_events(ledger, idx)
    sexual_chapters = {ev.get("chapter") for ev, b in _events_with_block(ledger) if "SEXUAL" in _classes(b)}
    for ev, block in _events_with_block(ledger):
        eid, chapter = ev.get("id"), ev.get("chapter", "WHOLE_BOOK")
        hbs = triggered.get(eid, [])
        if "HB-01" in hbs:
            out.append(cl.finding(
                "HARD_BOUNDARY_MINOR_SEXUALIZATION", "BLOCKER", chapter, f"{eid} participantes",
                "HB-01: participante de evento erótico sem idade adulta canônica confirmada "
                "(desconhecida, menor de 18, ou menor no momento do evento). Não é uma limitação de "
                "representação: é um hard boundary do motor, sem override.",
                "Corrigir o plano: remover o participante ou o caráter erótico do evento."))
        if "HB-02" in hbs:
            intended, realized = block.get("intended") or {}, block.get("realized") or {}
            for name, part in (("intended", intended), ("realized", realized)):
                if not part:
                    continue
                if part.get("execution") != "REFERENCE_ONLY" or part.get("graphic") is not False:
                    out.append(cl.finding(
                        "HARD_BOUNDARY_MINOR_ABUSE_DEPICTION", "BLOCKER", chapter, f"{eid}.{name}",
                        "HB-02: abuso envolvendo menor só pode existir como fato canônico não "
                        "sexualizado (REFERENCE_ONLY, graphic: false).",
                        "Reduzir a execução a REFERENCE_ONLY sem detalhe gráfico (testemunho, "
                        "investigação, consequência)."))
            if chapter in sexual_chapters:
                out.append(cl.finding(
                    "HARD_BOUNDARY_MINOR_ABUSE_DEPICTION", "BLOCKER", chapter, f"{eid} capítulo {chapter}",
                    "HB-02: o capítulo contém também um evento SEXUAL; material de abuso de menor nunca "
                    "convive com conteúdo erótico (mesma regra de proximidade da infância de Narciso).",
                    "Separar os eventos em capítulos distintos."))
        if hbs and (block.get("gap") is not None or block.get("status") in LIMITED_STATUSES):
            out.append(cl.finding(
                "HARD_BOUNDARY_GAP", "BLOCKER", chapter, f"{eid}.representation",
                "HB-04: evento em hard boundary com gap ou status limitado. Hard boundary não é "
                "'representação limitada' e nunca é convite a edição posterior.",
                "Remover o gap; corrigir o plano para que o evento não cruze o hard boundary."))
    return out


# --- matriz SUBJECT_PERMISSION x SCENE_EXECUTION ----------------------------

def _ceiling_of(policy: dict, family: str) -> str:
    return ((policy.get("permissions") or {}).get(family) or {}).get("depiction_ceiling", "CAN_EXIST")


def check_matrix(ledger: dict, idx: dict, policy: dict) -> list[dict]:
    out = []
    skip = hard_boundary_events(ledger, idx)
    for ev, block in _events_with_block(ledger):
        if ev.get("id") in skip:
            continue
        for family in _classes(block):
            if family not in CONTENT_CLASSES:
                continue
            level = DEPICTION_CEILINGS.index(_ceiling_of(policy, family)) if _ceiling_of(policy, family) in DEPICTION_CEILINGS else 0
            for name in ("intended", "realized"):
                part = block.get(name)
                if not isinstance(part, dict):
                    continue
                execution, graphic = part.get("execution"), part.get("graphic")
                too_much = (
                    (level == 0 and execution in EXECUTIONS and execution != "REFERENCE_ONLY")
                    or (level < 2 and graphic is True))
                if too_much:
                    out.append(cl.finding(
                        "REPRESENTATION_EXCEEDS_POLICY", "HIGH", ev.get("chapter", "WHOLE_BOOK"),
                        f"{ev.get('id')}.{name} {family} {execution}{' graphic' if graphic else ''}",
                        f"A política da autora limita {family} a {DEPICTION_CEILINGS[level]}. "
                        "Isto é decisão editorial da autora, não segurança: ou o plano cede, ou a "
                        "política muda por decisão humana.",
                        "Ajustar a representação ao teto, ou alterar a política com aprovação humana."))
    return out


# --- Authorial Gap ----------------------------------------------------------

def reduction(block: dict, gap_threshold: int) -> tuple[bool, int]:
    intended, realized = block.get("intended"), block.get("realized")
    if not (isinstance(intended, dict) and isinstance(realized, dict)):
        return False, 0
    if not (_is_int(intended.get("intensity")) and _is_int(realized.get("intensity"))):
        return False, 0
    diff = intended["intensity"] - realized["intensity"]
    exec_drop = (EXECUTION_RANK.get(intended.get("execution"), 0)
                 > EXECUTION_RANK.get(realized.get("execution"), 0))
    graphic_drop = intended.get("graphic") is True and realized.get("graphic") is False
    return (diff >= gap_threshold or exec_drop or graphic_drop), diff


def check_gaps(ledger: dict, idx: dict, policy: dict | None, overrides: dict | None = None) -> list[dict]:
    out = []
    th = _thresholds(policy, overrides)
    always_review = set((policy or {}).get("always_review") or [])
    block_mode = (policy or {}).get("on_constrained_representation", "RECORD_GAP") == "BLOCK"
    skip = hard_boundary_events(ledger, idx)
    for ev, block in _events_with_block(ledger):
        if ev.get("id") in skip or not isinstance(block.get("realized"), dict):
            continue
        eid, chapter = ev.get("id"), ev.get("chapter", "WHOLE_BOOK")
        status, gap = block.get("status"), block.get("gap")
        reduced, diff = reduction(block, th["gap_threshold"])
        limited = status in LIMITED_STATUSES
        if block_mode and (reduced or limited):
            out.append(cl.finding(
                "CAPABILITY_BLOCKER", "HIGH", chapter, f"{eid}.representation",
                "A política desta autora/obra é BLOCK: qualquer redução da representação planejada "
                "bloqueia a wave (não registra lacuna). O cânone não é alterado.",
                "Devolver o evento a PLANNED e revisar a wave, ou decidir por RECORD_GAP com aprovação humana."))
            continue
        if reduced or limited:
            if not limited or not isinstance(gap, dict):
                out.append(cl.finding(
                    "AUTHORIAL_GAP_MISSING", "HIGH", chapter,
                    f"{eid}: intended {block['intended'].get('intensity')} / realized {block['realized'].get('intensity')}, "
                    f"status={status}",
                    "A representação realizada ficou abaixo da planejada (ou o status é limitado), mas falta o "
                    "par status CONSTRAINED/AUTHOR_REVIEW + bloco gap (GAP-01).",
                    "Registrar status e gap com a função narrativa não realizada, ou restaurar a representação."))
                continue
            families = set(_classes(block))
            needs_review = (diff >= th["review_threshold"]
                            or (block.get("realized") or {}).get("constraint_source") == "UNKNOWN"
                            or bool(families & always_review))
            if needs_review and not (status == "AUTHOR_REVIEW" and gap.get("author_review") == "REQUIRED"):
                out.append(cl.finding(
                    "AUTHOR_REVIEW_NOT_ESCALATED", "HIGH", chapter, f"{eid}.representation",
                    "Diferença grande, origem desconhecida ou família sempre-revisada: a cena precisa de "
                    "status AUTHOR_REVIEW e gap.author_review REQUIRED (GAP-05).",
                    "Escalar para AUTHOR_REVIEW/REQUIRED."))
        elif status == "FULLY_REPRESENTED" and gap is not None:
            out.append(cl.finding(
                "GAP_STATUS_INCONSISTENT", "HIGH", chapter, f"{eid}.representation",
                "status FULLY_REPRESENTED com bloco gap e sem redução detectável (GAP-02).",
                "Remover o gap ou corrigir o status."))
    return out


# --- projeções --------------------------------------------------------------

def age_verification(ledger: dict, idx: dict, ev: dict) -> str:
    """Projeção (nunca armazenada): PASS | FAIL | N/A. Idade desconhecida em
    cena erótica é FAIL, nunca N/A."""
    block = ev.get("representation") if isinstance(ev.get("representation"), dict) else {}
    if not _is_erotic(ev, block):
        return "N/A"
    for p in cl._participants_of(ev):
        char = idx["char_index"].get(p) or {}
        if not _all_adult(_ages_of(idx, block, p)):
            return "FAIL"
        if not (isinstance(char.get("age_source"), str) and char["age_source"].strip()):
            return "FAIL"
    return "PASS"


def gap_names(block: dict) -> list[str]:
    """Nome projetado do gap: <família>_<dimensão>_GAP (17.3). Nunca gravado."""
    gap = block.get("gap")
    if not isinstance(gap, dict):
        return []
    return [f"{c}_{d}_GAP" for c in _classes(block) for d in gap.get("dimensions") or []]


def classify(findings: list[dict], ledger: dict) -> str:
    if any(f["category"] in HARD_BOUNDARY_CATEGORIES and f["severity"] in BLOCKING for f in findings):
        return "FAIL_HARD_BOUNDARY"
    if any(f["severity"] in BLOCKING for f in findings):
        return "FAIL_CONTRACT"
    if any(isinstance(b.get("gap"), dict) for _, b in _events_with_block(ledger)):
        return "PASS_WITH_AUTHORIAL_GAPS"
    return "PASS"


def event_report(ledger: dict, idx: dict, event_id: str) -> dict:
    ev = idx["ev_by_id"].get(event_id)
    if ev is None:
        return {"error": f"evento {event_id} não existe"}
    block = ev.get("representation") if isinstance(ev.get("representation"), dict) else None
    return {
        "id": event_id, "chapter": ev.get("chapter"), "participants": sorted(cl._participants_of(ev)),
        "age_verification": age_verification(ledger, idx, ev),
        "representation": block,
        "gap_names": gap_names(block) if block else [],
    }


# --- orquestração -----------------------------------------------------------

def validate(ledger: dict, policy: dict | None = None, mode: str = "plan",
             thresholds: dict | None = None) -> list[dict]:
    idx, dup = cl.build_indices(ledger)
    findings: list[dict] = list(dup)
    if policy is not None:
        findings += check_policy(policy)
    findings += check_structure(ledger)
    findings += check_adult_gate_and_hard_boundaries(ledger, idx)
    if policy is not None:
        findings += check_matrix(ledger, idx, policy)
    findings += check_gaps(ledger, idx, policy, thresholds)
    del mode  # Slice 1: todos os modos aplicam as mesmas regras; Slice 2 diferencia plan de realized.
    return findings


def render_report(findings: list[dict], source: str, result: str) -> str:
    out = ["# Relatório de Representation Integrity\n\n", f"Fonte: `{source}`\n\n",
           f"Resultado: **{result}**\n\n",
           "Gerado por `engine/scripts/check_representation.py` (Slice 1). "
           "Ver docs/sdd/REPRESENTATION_INTEGRITY_SDD_v0.1.md.\n\n"]
    if not findings:
        out.append("Nenhum achado.\n")
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
            out.append(f"  - {f['detail']}\n  - Ação sugerida: {f['recommended_action']}\n")
        out.append("\n")
    return "".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validador do bloco representation (REPRESENTATION_INTEGRITY).")
    ap.add_argument("--runtime", type=Path, help="Raiz do runtime; lê canon/CAUSAL_LEDGER.yaml.")
    ap.add_argument("--ledger", type=Path, help="Caminho direto para um CAUSAL_LEDGER.yaml.")
    ap.add_argument("--policy", type=Path, help="REPRESENTATION_POLICY.vN.yaml da autora.")
    ap.add_argument("--mode", choices=["plan", "realized", "final"], default="plan")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--event", metavar="EVENT_ID", help="Projeção de um evento (age verification, gap).")
    ap.add_argument("--gap-threshold", type=int)
    ap.add_argument("--review-threshold", type=int)
    args = ap.parse_args()

    path = args.ledger or (args.runtime / "canon" / "CAUSAL_LEDGER.yaml" if args.runtime else None)
    if path is None:
        print("informe --ledger ou --runtime", file=sys.stderr)
        return 2
    if not path.is_file():
        print(f"CAUSAL_LEDGER não encontrado: {path}", file=sys.stderr)
        return 2
    policy = None
    if args.policy:
        if not args.policy.is_file():
            print(f"Política não encontrada: {args.policy}", file=sys.stderr)
            return 2
        policy = cl.load_yaml(args.policy)
    ledger = cl.load_yaml(path)

    if args.event:
        idx, _ = cl.build_indices(ledger)
        print(json.dumps(event_report(ledger, idx, args.event), ensure_ascii=False, indent=2))
        return 0

    overrides = {k: v for k, v in (("gap_threshold", args.gap_threshold),
                                    ("review_threshold", args.review_threshold)) if v is not None}
    findings = validate(ledger, policy, args.mode, overrides or None)
    result = classify(findings, ledger)
    if args.json:
        print(json.dumps({"result": result, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        report = render_report(findings, str(path), result)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(report, encoding="utf-8")
            print(f"Relatório: {args.out}")
        else:
            print(report)
    counts: dict[str, int] = defaultdict(int)
    for f in findings:
        counts[f["severity"]] += 1
    print(f"\nRESULT: {result} | TOTAL: {len(findings)} achado(s) "
          f"({', '.join(f'{v} {k}' for k, v in counts.items()) or 'nenhum'})", file=sys.stderr)
    return 1 if any(f["severity"] in BLOCKING for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
