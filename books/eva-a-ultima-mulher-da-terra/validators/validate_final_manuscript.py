from __future__ import annotations

import re
import sys
from pathlib import Path

# This validator runs at GATE_FULL_MANUSCRIPT, after T310_FREEZE_MANUSCRIPT
# has written the frozen manuscript. It is the last mechanical line of
# defense for the two absolute endings rules of this book: no pregnancy
# confirmation, no death confirmation, and the closing counters must read
# exactly population=1 / births=0. Reasoning agents enforce the subtler
# forms of these rules; this script catches the literal vocabulary.

BOOK_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = BOOK_ROOT.parent
MANUSCRIPT = RUNTIME_ROOT / "manuscript" / "final" / "MANUSCRIPT_FINAL_PTBR.md"

# IR005 — forbidden pregnancy vocabulary. Word-boundary, case-insensitive,
# matches common Portuguese inflections without requiring an exhaustive list.
FORBIDDEN_PREGNANCY_TERMS = [
    r"gravidez",
    r"gr[aá]vida",
    r"gesta[cç][aã]o",
    r"gestante",
    r"\bfeto\b",
    r"fetal",
    r"embri[aã]o",
    r"embrion[aá]rio",
    r"\b[uú]tero\b",
    r"contra[cç][aã]o de parto",
    r"trabalho de parto",
    r"atraso menstrual",
    r"movimento fetal",
    r"\bpart[eo]jou\b",
    r"\bparto\b",
]

# IR006 — forbidden explicit death/survival confirmations for the closing
# chapters. These are deliberately narrow (full asserted clauses), not single
# words, so ordinary prose about mortality earlier in the book is untouched.
FORBIDDEN_DEATH_PHRASES = [
    r"eva\s+morreu",
    r"eva\s+estava\s+morta",
    r"o\s+cora[cç][aã]o\s+de\s+eva\s+parou",
    r"[uú]ltima\s+respira[cç][aã]o\s+de\s+eva",
    r"eva\s+sobreviveu",
    r"eva\s+se\s+recuperou",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def extract_final_chapters(text: str) -> str:
    """Best-effort slice covering chapters 41-42 (O Deserto / Pássaros)."""
    markers = ["O Deserto", "Pássaros"]
    positions = [text.find(m) for m in markers if text.find(m) != -1]
    if not positions:
        return text[-20000:]
    start = min(positions)
    return text[start:]


def main() -> int:
    if not MANUSCRIPT.exists():
        fail(f"final manuscript not found at {MANUSCRIPT}")

    text = MANUSCRIPT.read_text(encoding="utf-8")
    ending = extract_final_chapters(text)
    ending_lower = ending.lower()

    for pattern in FORBIDDEN_PREGNANCY_TERMS:
        if re.search(pattern, ending_lower):
            fail(
                "forbidden pregnancy vocabulary (IR005) found in closing "
                f"chapters: pattern '{pattern}' matched"
            )

    for pattern in FORBIDDEN_DEATH_PHRASES:
        if re.search(pattern, ending_lower):
            fail(
                "forbidden death/survival confirmation (IR006) found in "
                f"closing chapters: pattern '{pattern}' matched"
            )

    if "esperando" in text.lower():
        occurrences = [m.start() for m in re.finditer(r"esperando", text.lower())]
        if len(occurrences) > 1:
            fail(
                "the word 'esperando' applied to the birds must appear "
                "exactly once, in the final line of the book (IR008); "
                f"found {len(occurrences)} occurrences"
            )
        last_line = text.strip().splitlines()[-1].lower() if text.strip() else ""
        if "esperando" not in last_line:
            fail("'esperando' must appear in the final line of the manuscript (IR008)")

    if not re.search(r"popula[cç][aã]o humana estimada.*?\b1\b", text, re.IGNORECASE | re.DOTALL):
        fail("final population counter must read exactly 1 (IR010)")
    if not re.search(
        r"nascimentos humanos no [uú]ltimo ano.*?\b0\b", text, re.IGNORECASE | re.DOTALL
    ):
        fail("final births counter must read exactly 0 (IR010)")

    print("FINAL MANUSCRIPT ENDING VALID | pregnancy=clear death=clear counters=1/0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
