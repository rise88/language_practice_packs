# Prompt — update `language_practice_packs` for multi-L2

Copy-paste this into an agent working on https://github.com/rise88/language_practice_packs

---

You are updating **language_practice_packs** so packs declare a **practice language (L2)** for the Vocalis web app (repo `language_practice`).

## Context

The app is no longer French-only for practice content. It loads packs into a language registry keyed by `lang`. UI/gloss locales (`en`/`es`/`ru` in `gloss` maps) stay as they are.

## Required schema changes

1. **Every pack JSON** must include:
   ```json
   "lang": "fr"
   ```
   Use ISO 639-1 (`fr`, `es`, `de`, …). Default existing packs to `"fr"`.

2. **Headword field:** prefer `"l2"` for the practice word/phrase. Keep `"fr"` as a legacy alias on **French** packs (dual-write `l2` + `fr`). Non-French packs should use `"l2"` and may omit `"fr"`. Example:
   ```json
   {
     "id": "es-food-a1-1",
     "l2": "pan",
     "en": "bread",
     "gloss": { "en": "bread", "fr": "pain", "ru": "хлеб" },
     "example": "El pan está fresco.",
     "ipa": "pan",
     "level": "a1"
   }
   ```

3. **`prompts`** (Écrire mode) must be written in the **practice language** of the pack (Spanish prompts for `lang: "es"`), not French. Prefer informal tú register for A1–B2 learner prompts unless the topic requires formal usted.

4. **`catalog.json`**:
   - `"lang"` on each entry (same code as the pack)
   - top-level `"languages": ["fr","es","ru"]` for practice L2s
   - top-level `"locales": ["en","es","ru"]` for gloss tooling

5. Update **`_template.json`**:
   - `pratiquePack: 2` (or 3 if you bump)
   - required `"lang"`
   - seed examples using `l2`
   - description text that does not say “prompts must stay French”

6. Update README / ADD-LANGUAGE docs:
   - Clarify **UI/gloss language** vs **practice language**
   - Point authors at pack `"lang"` + `l2`
   - Catalog URL must be `https://raw.githubusercontent.com/rise88/language_practice_packs/main/catalog.json`

## Migration

- Script or one-shot edit: set `"lang": "fr"` on all existing packs and catalog rows.
- Dual-write `"l2"` from `"fr"` on French seed / phrases / listen items; keep legacy `"fr"`.
- Validate: every pack has non-empty `lang`; every seed item has `l2` or `fr`; catalog has `languages`.

## First non-French content (optional but valuable)

Ship a small Spanish A1 pack set (`lang: "es"`) with seed + glosses + IPA + a few prompts, so the app’s Spanish profile has remote content beyond the bundled starter.

## Out of scope

- Do not build a translation backend
- Do not remove English `gloss` / locale maps
- Do not change pack hosting URLs unless needed

## Done when

- `catalog.json` entries expose `lang` and top-level `languages`
- Template + README document multi-L2
- Existing French packs still install in the app under French and dual-write `l2`
- At least one documented example pack uses `lang` + `l2` for a non-French language
