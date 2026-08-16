#!/usr/bin/env python3
"""Fill gloss.es / gloss.ru (and related locale maps) for Vocalis packs.

Translates unique strings once (cached), then applies to packs.
Usage:
  python3 scripts/fill-gloss-locales.py           # all packs
  python3 scripts/fill-gloss-locales.py a1 a2     # selected levels
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = Path("/tmp/gloss-translate-cache.json")
LOCALES = ("es", "ru")

cache: dict[str, str] = {}
if CACHE_PATH.exists():
    raw = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    # support both flat and nested shapes
    for k, v in raw.items():
        if isinstance(v, str):
            cache[k] = v
        elif isinstance(v, dict) and "t" in v:
            cache[k] = v["t"]

translators = {
    ("en", "es"): GoogleTranslator(source="en", target="es"),
    ("en", "ru"): GoogleTranslator(source="en", target="ru"),
    ("fr", "en"): GoogleTranslator(source="fr", target="en"),
    ("fr", "es"): GoogleTranslator(source="fr", target="es"),
    ("fr", "ru"): GoogleTranslator(source="fr", target="ru"),
}

_pending_saves = 0


def save_cache() -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def translate(text: str, source: str, target: str) -> str:
    global _pending_saves
    text = text.strip()
    if not text:
        return text
    if source == target:
        return text
    key = f"{source}|{target}|{text}"
    if key in cache and cache[key]:
        return cache[key]

    last_err = None
    for attempt in range(8):
        try:
            out = translators[(source, target)].translate(text)
            if not out:
                raise RuntimeError("empty translation")
            cache[key] = out
            _pending_saves += 1
            if _pending_saves >= 20:
                save_cache()
                _pending_saves = 0
            time.sleep(0.03)
            return out
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"translate failed {source}->{target}: {text[:80]!r}: {last_err}")


def collect_jobs(packs: list[dict]) -> tuple[set[tuple[str, str, str]], dict]:
    """Return set of (source, target, text) jobs and why-templates needing en."""
    jobs: set[tuple[str, str, str]] = set()

    def need(src_lang: str, text: str, targets: tuple[str, ...]) -> None:
        if not isinstance(text, str) or not text.strip():
            return
        for t in targets:
            if t != src_lang:
                jobs.add((src_lang, t, text.strip()))

    for pack in packs:
        for field in ("title", "description"):
            m = pack.get(field) or {}
            en = m.get("en")
            if isinstance(en, str):
                need("en", en, LOCALES)

        for card in pack.get("seed") or []:
            en = (card.get("gloss") or {}).get("en") or card.get("en")
            if isinstance(en, str):
                need("en", en, LOCALES)

        for phrase in pack.get("phrases") or []:
            en = (phrase.get("gloss") or {}).get("en") or phrase.get("en")
            if isinstance(en, str):
                need("en", en, LOCALES)

        for item in pack.get("listen") or []:
            en = (item.get("gloss") or {}).get("en") or item.get("en")
            if isinstance(en, str):
                need("en", en, LOCALES)
            wen = (item.get("wordGloss") or {}).get("en") or item.get("wordEn")
            if isinstance(wen, str):
                need("en", wen, LOCALES)

        for lesson in pack.get("grammar") or []:
            title = lesson.get("title") or {}
            if isinstance(title.get("en"), str):
                need("en", title["en"], LOCALES)
            rule = lesson.get("rule")
            fr = None
            if isinstance(rule, str):
                fr = rule
            elif isinstance(rule, dict):
                fr = rule.get("fr")
            if isinstance(fr, str) and fr.strip():
                need("fr", fr, ("en",) + LOCALES)

            why = lesson.get("why") or {}
            why_en = why.get("en") if isinstance(why, dict) else None
            if not isinstance(why_en, str) or not why_en:
                title_en = title.get("en") if isinstance(title, dict) else None
                if isinstance(title_en, str) and title_en.strip():
                    why_en = f"Useful when you need to apply: {title_en.strip()}."
                else:
                    why_en = "Helps you use this pattern correctly in French."
            need("en", why_en, LOCALES)

        for items in (pack.get("skills") or {}).values():
            if not isinstance(items, list):
                continue
            for item in items:
                en = (item.get("gloss") or {}).get("en") or item.get("en")
                if isinstance(en, str):
                    need("en", en, LOCALES)

    return jobs


def run_jobs(jobs: set[tuple[str, str, str]]) -> None:
    # Prefer shorter strings first (seed lemmas) for faster early progress
    ordered = sorted(jobs, key=lambda j: (len(j[2]), j[0], j[1], j[2]))
    total = len(ordered)
    done = 0
    skipped = 0
    for source, target, text in ordered:
        key = f"{source}|{target}|{text}"
        if key in cache and cache[key]:
            skipped += 1
            done += 1
            continue
        translate(text, source, target)
        done += 1
        if done % 50 == 0 or done == total:
            print(f"  translate {done}/{total} (cached-hit skip {skipped})", flush=True)
    save_cache()


def apply_pack(pack: dict) -> bool:
    changed = False
    pack["pratiquePack"] = 2

    def fill_from_en(m: dict) -> bool:
        nonlocal changed
        c = False
        en = m.get("en")
        if not isinstance(en, str) or not en.strip():
            return False
        for loc in LOCALES:
            if not isinstance(m.get(loc), str) or not m.get(loc):
                m[loc] = translate(en, "en", loc)
                c = True
        return c

    for field in ("title", "description"):
        m = pack.get(field)
        if isinstance(m, dict) and fill_from_en(m):
            changed = True

    def ensure_gloss(obj: dict) -> None:
        nonlocal changed
        g = obj.get("gloss")
        if not isinstance(g, dict):
            g = {}
            obj["gloss"] = g
            changed = True
        en = g.get("en") if isinstance(g.get("en"), str) and g.get("en") else obj.get("en")
        if isinstance(en, str) and en.strip():
            if g.get("en") != en:
                g["en"] = en
                changed = True
            for loc in LOCALES:
                if not isinstance(g.get(loc), str) or not g.get(loc):
                    g[loc] = translate(en, "en", loc)
                    changed = True

    for card in pack.get("seed") or []:
        ensure_gloss(card)
    for phrase in pack.get("phrases") or []:
        ensure_gloss(phrase)
    for item in pack.get("listen") or []:
        ensure_gloss(item)
        wg = item.get("wordGloss")
        if not isinstance(wg, dict):
            wg = {}
            item["wordGloss"] = wg
            changed = True
        wen = wg.get("en") if isinstance(wg.get("en"), str) and wg.get("en") else item.get("wordEn")
        if isinstance(wen, str) and wen.strip():
            if wg.get("en") != wen:
                wg["en"] = wen
                changed = True
            for loc in LOCALES:
                if not isinstance(wg.get(loc), str) or not wg.get(loc):
                    wg[loc] = translate(wen, "en", loc)
                    changed = True

    for lesson in pack.get("grammar") or []:
        title = lesson.get("title")
        if isinstance(title, dict) and fill_from_en(title):
            changed = True

        rule = lesson.get("rule")
        if isinstance(rule, str):
            lesson["rule"] = {"fr": rule}
            rule = lesson["rule"]
            changed = True
        if isinstance(rule, dict):
            fr = rule.get("fr")
            if isinstance(fr, str) and fr.strip():
                if not isinstance(rule.get("en"), str) or not rule.get("en"):
                    rule["en"] = translate(fr, "fr", "en")
                    changed = True
                for loc in LOCALES:
                    if not isinstance(rule.get(loc), str) or not rule.get(loc):
                        rule[loc] = translate(fr, "fr", loc)
                        changed = True

        why = lesson.get("why")
        if not isinstance(why, dict):
            why = {}
            lesson["why"] = why
            changed = True
        if not isinstance(why.get("en"), str) or not why.get("en"):
            title_en = title.get("en") if isinstance(title, dict) else None
            if isinstance(title_en, str) and title_en.strip():
                why["en"] = f"Useful when you need to apply: {title_en.strip()}."
            else:
                why["en"] = "Helps you use this pattern correctly in French."
            changed = True
        for loc in LOCALES:
            if not isinstance(why.get(loc), str) or not why.get(loc):
                why[loc] = translate(why["en"], "en", loc)
                changed = True

    for drill_id, items in (pack.get("skills") or {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            ensure_gloss(item)
            if drill_id == "meaning" and "choices" in item and isinstance(item.get("gloss"), dict):
                del item["choices"]
                changed = True

    return changed


def list_pack_files():
    files = []
    for lang_dir in sorted(p for p in ROOT.iterdir() if p.is_dir() and re.fullmatch(r"[a-z]{2}", p.name)):
        files.extend(sorted(lang_dir.glob("*-*.json")))
    files.extend(sorted(p for p in ROOT.glob("*-*.json") if re.search(r"-[abc][12]\.json$", p.name)))
    # de-dupe while preserving order
    seen = set()
    out = []
    for p in files:
        if p in seen:
            continue
        if not re.search(r"-[abc][12]\.json$", p.name):
            continue
        seen.add(p)
        out.append(p)
    return out


def main() -> None:
    levels = {a.lower() for a in sys.argv[1:]} if len(sys.argv) > 1 else None
    pack_files = list_pack_files()
    if levels:
        pack_files = [p for p in pack_files if any(p.name.endswith(f"-{lv}.json") for lv in levels)]

    packs = []
    for path in pack_files:
        packs.append(json.loads(path.read_text(encoding="utf-8")))

    print(f"collecting jobs for {len(packs)} packs…", flush=True)
    jobs = collect_jobs(packs)
    missing = [j for j in jobs if f"{j[0]}|{j[1]}|{j[2]}" not in cache]
    print(f"unique translation jobs: {len(jobs)} ({len(missing)} uncached)", flush=True)
    run_jobs(jobs)

    catalog_path = ROOT / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog["locales"] = ["en", "es", "ru"]
    catalog["updatedAt"] = "2026-08-15"

    touched = 0
    for path, pack in zip(pack_files, packs):
        # reload from disk? use in-memory pack after translations cached
        before = pack.get("version")
        changed = apply_pack(pack)
        if changed:
            if isinstance(pack.get("version"), int):
                pack["version"] = pack["version"] + 1
            path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            touched += 1
            print(f"filled {path.name} v{before}->{pack['version']}", flush=True)
        # sync catalog entry
        for entry in catalog.get("packs") or []:
            if entry.get("id") == pack.get("id"):
                entry["version"] = pack.get("version")
                entry["title"] = pack.get("title")
                entry["description"] = pack.get("description")
                break

    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    save_cache()
    print(f"done: {touched}/{len(packs)} packs written", flush=True)


if __name__ == "__main__":
    main()
