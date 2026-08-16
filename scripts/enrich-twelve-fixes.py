#!/usr/bin/env python3
"""Enrich packs for the twelve cross-repo inconsistencies.

- grammar lesson why.fr
- grammar question gloss + why (en/es/ru + fr why)
- expand skills: l2en alias, enfr, prompt, signs, pairs, gap, reorder
- derive sounds from seed IPA
- bump pack + catalog versions

Usage:
  python3 scripts/enrich-twelve-fixes.py
  python3 scripts/enrich-twelve-fixes.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parents[1]
WAVE2 = Path("/tmp/wave2-a1")
CACHE_PATH = Path("/tmp/pack-grammar-gloss-cache.json")
LOCALES = ("en", "es", "ru")


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n")


def translate(cache: dict, text: str, source: str, target: str) -> str:
    key = f"{source}->{target}::{text}"
    if key in cache:
        return cache[key]
    if source == target:
        cache[key] = text
        return text
    # Placeholder blanks survive translation better when spaced.
    safe = text.replace("___", " ___ ")
    try:
        out = GoogleTranslator(source=source, target=target).translate(safe) or text
    except Exception:
        time.sleep(1.5)
        try:
            out = GoogleTranslator(source=source, target=target).translate(safe) or text
        except Exception:
            out = text
    out = re.sub(r"\s*___\s*", " ___ ", out).strip()
    out = re.sub(r"\s+", " ", out)
    cache[key] = out
    time.sleep(0.12)
    return out


def headword(card: dict) -> str:
    return (card.get("l2") or card.get("fr") or "").strip()


def derive_skills(pack: dict) -> dict:
    seed = pack.get("seed") or []
    with_ex = [c for c in seed if c.get("example") and headword(c)]
    skills = dict(pack.get("skills") or {})

    def gloss_of(c):
        return c.get("gloss") or ({"en": c["en"]} if c.get("en") else {})

    # l2en alias of fren
    if skills.get("fren") and not skills.get("l2en"):
        skills["l2en"] = skills["fren"]
    if skills.get("l2en") and not skills.get("fren"):
        skills["fren"] = skills["l2en"]

    if not skills.get("enfr") and with_ex:
        pool = [c.get("example") for c in with_ex]
        enfr = []
        for i, c in enumerate(with_ex[:8]):
            ans = c["example"]
            others = [x for x in pool if x != ans][:2]
            enfr.append(
                {
                    "id": f"remote-{pack['id']}-enl2-{i+1}",
                    "fr": ans,
                    "l2": ans,
                    "en": c.get("en") or gloss_of(c).get("en", ""),
                    "gloss": gloss_of(c),
                    "prompt": c.get("en") or gloss_of(c).get("en", ""),
                    "choices": [ans] + others,
                }
            )
        skills["enfr"] = enfr

    if not skills.get("prompt") and seed:
        skills["prompt"] = [
            {
                "id": f"remote-{pack['id']}-prm-{i+1}",
                "en": c.get("en") or gloss_of(c).get("en", ""),
                "gloss": gloss_of(c),
                "answers": [headword(c)]
                + ([f"{c['article']} {headword(c)}"] if c.get("article") else []),
                "target": f"{c['article']} {headword(c)}" if c.get("article") else headword(c),
            }
            for i, c in enumerate(seed[:10])
            if headword(c)
        ]

    if not skills.get("signs") and seed:
        ens = [c.get("en") or gloss_of(c).get("en", "") for c in seed]
        signs = []
        for i, c in enumerate(seed[:12]):
            ans = c.get("en") or gloss_of(c).get("en", "")
            if not ans:
                continue
            others = [x for x in ens if x and x != ans][:2]
            signs.append(
                {
                    "id": f"remote-{pack['id']}-sign-{i+1}",
                    "fr": headword(c),
                    "l2": headword(c),
                    "en": ans,
                    "gloss": gloss_of(c),
                    "choices": [ans] + others,
                }
            )
        if signs:
            skills["signs"] = signs

    if not skills.get("pairs") and len(seed) >= 2:
        pairs = []
        for i in range(0, min(len(seed) - 1, 10), 2):
            a, b = seed[i], seed[i + 1]
            pairs.append(
                {
                    "id": f"remote-{pack['id']}-pair-{i//2+1}",
                    "a": {
                        "fr": headword(a),
                        "l2": headword(a),
                        "en": a.get("en"),
                        "gloss": gloss_of(a),
                    },
                    "b": {
                        "fr": headword(b),
                        "l2": headword(b),
                        "en": b.get("en"),
                        "gloss": gloss_of(b),
                    },
                    "play": "a",
                }
            )
        if pairs:
            skills["pairs"] = pairs

    if not skills.get("gap") and with_ex:
        gaps = []
        for i, c in enumerate(with_ex[:8]):
            word = headword(c)
            sentence = c["example"]
            blanked = sentence.replace(word, "___", 1) if word and word in sentence else re.sub(r"\S+", "___", sentence, count=1)
            gaps.append(
                {
                    "id": f"remote-{pack['id']}-gap-{i+1}",
                    "fr": sentence,
                    "l2": sentence,
                    "speak": sentence,
                    "blank": word,
                    "en": c.get("en") or gloss_of(c).get("en", ""),
                    "gloss": gloss_of(c),
                }
            )
        skills["gap"] = gaps

    if not skills.get("reorder") and with_ex:
        skills["reorder"] = [
            {
                "id": f"remote-{pack['id']}-ord-{i+1}",
                "fr": c["example"],
                "l2": c["example"],
                "en": c.get("en") or gloss_of(c).get("en", ""),
                "gloss": gloss_of(c),
                "words": [w for w in c["example"].split() if w],
            }
            for i, c in enumerate(with_ex[:8])
        ]

    return skills


def derive_sounds(pack: dict) -> list:
    if pack.get("sounds"):
        return pack["sounds"]
    seed = [c for c in (pack.get("seed") or []) if c.get("ipa") and headword(c)]
    if len(seed) < 3:
        return []
    examples = []
    for c in seed[:5]:
        examples.append(
            {
                "fr": headword(c),
                "l2": headword(c),
                "en": c.get("en") or (c.get("gloss") or {}).get("en", ""),
                "gloss": c.get("gloss"),
                "ipa": c["ipa"],
            }
        )
    tip = examples[0]
    return [
        {
            "id": f"remote-{pack['id']}-sounds",
            "label": {
                "fr": "Sons du pack",
                "en": "Pack sounds",
                "es": "Sonidos del pack",
                "ru": "Звуки пакета",
            },
            "ipa": tip["ipa"],
            "tipTitle": {
                "fr": "Prononciation du thème",
                "en": "Topic pronunciation",
                "es": "Pronunciación del tema",
                "ru": "Произношение темы",
            },
            "tipBody": {
                "fr": "Répète les mots du pack en regardant l’IPA.",
                "en": "Repeat the pack words while watching the IPA.",
                "es": "Repite las palabras del pack mirando la IPA.",
                "ru": "Повторяйте слова пакета, глядя на IPA.",
            },
            "examples": examples,
        }
    ]


def why_templates(answer: str) -> dict:
    a = str(answer or "").strip()
    return {
        "fr": f"Réponse : « {a} ».",
        "en": f"Answer: “{a}”.",
        "es": f"Respuesta: « {a} ».",
        "ru": f"Ответ: « {a} ».",
    }


def load_wave2_index() -> dict:
    """Map packId -> questionId -> {gloss, why}."""
    out = {}
    if not WAVE2.exists():
        return out
    for path in WAVE2.glob("*-a1.json"):
        pack = json.loads(path.read_text())
        qmap = {}
        for lesson in pack.get("grammar") or []:
            for q in lesson.get("questions") or []:
                if q.get("id") and (q.get("gloss") or q.get("why")):
                    qmap[q["id"]] = {"gloss": q.get("gloss"), "why": q.get("why")}
        out[pack["id"]] = qmap
    return out


def enrich_pack(pack: dict, cache: dict, wave2: dict) -> bool:
    changed = False
    lang = pack.get("lang") or "fr"
    src = lang if lang in ("fr", "es", "ru", "en") else "auto"

    for lesson in pack.get("grammar") or []:
        title = lesson.get("title") if isinstance(lesson.get("title"), dict) else {}
        why = lesson.get("why") if isinstance(lesson.get("why"), dict) else {}
        if why and not why.get("fr"):
            title_fr = title.get("fr") or title.get("en") or ""
            if title_fr:
                why["fr"] = f"Utile pour appliquer : {title_fr}."
            elif why.get("en"):
                why["fr"] = translate(cache, why["en"], "en", "fr")
            else:
                why["fr"] = "Utile pour cette leçon."
            lesson["why"] = why
            changed = True

        w2 = wave2.get(pack["id"], {})
        for q in lesson.get("questions") or []:
            prompt = str(q.get("prompt") or "")
            hid = w2.get(q.get("id") or "")
            if hid and hid.get("gloss") and not q.get("gloss"):
                q["gloss"] = hid["gloss"]
                changed = True
            if hid and hid.get("why") and not q.get("why"):
                q["why"] = hid["why"]
                changed = True

            gloss = q.get("gloss") if isinstance(q.get("gloss"), dict) else {}
            if prompt and (not gloss or any(not gloss.get(loc) for loc in LOCALES)):
                for loc in LOCALES:
                    if gloss.get(loc):
                        continue
                    if loc == lang:
                        gloss[loc] = prompt
                    else:
                        gloss[loc] = translate(cache, prompt, src, loc)
                q["gloss"] = gloss
                changed = True

            if not q.get("why"):
                q["why"] = why_templates(q.get("answer"))
                changed = True
            else:
                why_q = q["why"] if isinstance(q["why"], dict) else {}
                if not why_q.get("fr"):
                    why_q["fr"] = why_templates(q.get("answer"))["fr"]
                    q["why"] = why_q
                    changed = True

    new_skills = derive_skills(pack)
    if new_skills != (pack.get("skills") or {}):
        pack["skills"] = new_skills
        changed = True

    sounds = derive_sounds(pack)
    if sounds and sounds != (pack.get("sounds") or []):
        pack["sounds"] = sounds
        changed = True

    if changed:
        pack["version"] = int(pack.get("version") or 1) + 1
        pack["pratiquePack"] = max(int(pack.get("pratiquePack") or 2), 2)
    return changed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cache = load_cache()
    wave2 = load_wave2_index()
    catalog = json.loads((ROOT / "catalog.json").read_text())
    catalog_by_id = {e["id"]: e for e in catalog.get("packs") or []}

    pack_files = sorted(
        p for p in ROOT.glob("*.json") if p.name not in ("catalog.json", "_template.json")
    )
    n_changed = 0
    for path in pack_files:
        pack = json.loads(path.read_text())
        before = pack.get("version")
        if enrich_pack(pack, cache, wave2):
            n_changed += 1
            entry = catalog_by_id.get(pack["id"])
            if entry is not None:
                entry["version"] = pack["version"]
            if not args.dry_run:
                path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n")
            print(f"updated {path.name} v{before} -> v{pack['version']}")
        save_cache(cache)

    if not args.dry_run:
        catalog["updatedAt"] = time.strftime("%Y-%m-%d")
        (ROOT / "catalog.json").write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
        )
    print(f"done: {n_changed}/{len(pack_files)} packs changed")


if __name__ == "__main__":
    main()
