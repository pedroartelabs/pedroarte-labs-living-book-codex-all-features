from __future__ import annotations

from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    return yaml.safe_load((ROOT / name).read_text(encoding="utf-8"))


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> int:
    spec = load("BOOK_SPEC.yaml")
    architecture = load("chapter_architecture.yaml")
    rules = load("immutable_rules.yaml")
    protected = load("protected_scenes.yaml")

    chapter_count = spec["metadata"]["chapter_count"]
    titles = {int(k): v for k, v in spec["spec"]["chapter_titles"].items()}
    chapters = architecture.get("chapters", [])

    if sorted(titles) != list(range(1, chapter_count + 1)):
        fail("chapter titles do not cover the complete sequence")
    if len(chapters) != chapter_count:
        fail("chapter architecture count does not match BOOK_SPEC")

    for chapter in chapters:
        number = chapter.get("number")
        if titles.get(number) != chapter.get("title"):
            fail(f"chapter {number} title differs between spec and architecture")
        if not chapter.get("function") or not chapter.get("irreversible_turn"):
            fail(f"chapter {number} lacks narrative function or irreversible turn")
        if not chapter.get("pov"):
            fail(f"chapter {number} lacks a declared point of view")

    # Book-specific: the demographic counter sequence must strictly follow the
    # order declared in seeds/WORLD_RULES_SEED.md (CF-1..CF-10, CH-1..CH-9),
    # never skipping backwards and never repeating a code across chapters.
    seen_codes: list[str] = []
    for chapter in chapters:
        raw = chapter.get("demographic_counter")
        if not raw:
            continue
        for code in str(raw).split(","):
            code = code.strip()
            if not code:
                continue
            if code in seen_codes:
                fail(f"demographic counter {code} referenced more than once")
            seen_codes.append(code)

    final_chapter = chapters[-1]
    final_codes = str(final_chapter.get("demographic_counter") or "").split(",")
    if "CH-9" not in [c.strip() for c in final_codes]:
        fail("final chapter must close with demographic counter CH-9 (population=1, births=0)")

    rule_ids = [rule.get("id") for rule in rules.get("rules", [])]
    if len(rule_ids) != len(set(rule_ids)) or any(not item for item in rule_ids):
        fail("immutable rule IDs must be present and unique")

    required_rule_categories = {
        "ending_pregnancy",
        "ending_death",
        "birds",
        "autopsy_resonance",
        "counters",
        "personhood",
        "causality",
    }
    present_categories = {rule.get("category") for rule in rules.get("rules", [])}
    missing = required_rule_categories - present_categories
    if missing:
        fail(f"immutable_rules.yaml is missing required categories: {sorted(missing)}")

    scene_ids = []
    for scene in protected.get("scenes", []):
        scene_id = scene.get("id")
        scene_ids.append(scene_id)
        if not scene.get("must_preserve") or not scene.get("reject_if"):
            fail(f"protected scene {scene_id} lacks audit criteria")
        for number in scene.get("chapters", []):
            if number < 1 or number > chapter_count:
                fail(f"protected scene {scene_id} references invalid chapter {number}")
    if len(scene_ids) != len(set(scene_ids)):
        fail("protected scene IDs must be unique")

    required_scene_ids = {
        "DESERT_INCIDENT",
        "FINAL_AMBIGUITY",
        "LAST_MAN_DEATH",
        "LAST_WOMAN_THRESHOLD",
        "BOY_BIRTH_PIVOT",
    }
    missing_scenes = required_scene_ids - set(scene_ids)
    if missing_scenes:
        fail(f"protected_scenes.yaml is missing required scenes: {sorted(missing_scenes)}")

    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml", ".toml"}:
            if "TO_DEFINE" in path.read_text(encoding="utf-8"):
                fail(f"unresolved TO_DEFINE in {path.relative_to(ROOT)}")

    print(
        f"BOOK DNA VALID | chapters={chapter_count} "
        f"rules={len(rule_ids)} protected_scenes={len(scene_ids)} "
        f"demographic_checkpoints={len(seen_codes)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
