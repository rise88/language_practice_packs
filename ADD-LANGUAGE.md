# Adding a learner language (gloss locale)

Pratique pack **v2** (`pratiquePack: 2`) shows card meanings in the learner’s language via `gloss` / `wordGloss` maps. Practice targets (`l2` / legacy `fr`, `example`, `prompts`, grammar drills) are written in the pack’s **practice language** (`lang`), not French-by-default.

Supported gloss locales in this catalog: **en**, **es**, **ru** (see `catalog.json` → `locales`).

## Practice language (L2)

| Field | Role |
|-------|------|
| `lang` | ISO practice language on the pack **and** its `catalog.json` entry (`fr`, `es`, …). Existing French packs use `"lang": "fr"`. |
| `seed[].l2` | Preferred headword in the practice language |
| `seed[].fr` | Legacy alias for the headword on **French** packs only — keep for older app builds; non-French packs should use `l2` |
| `prompts` | Writing prompts **in the pack’s `lang`** (French for `lang:"fr"`, Spanish for `lang:"es"`, …) |

Do **not** build or rely on a translation backend: ship L2 text in the pack JSON.

## Field map (gloss / UI)

| Field | Role |
|-------|------|
| `title` / `description` | Locale maps (`fr` for catalog UI in French + gloss locales) |
| `seed[].en` | Legacy English gloss (kept for older app builds) |
| `seed[].gloss` | `{ en, es, ru }` meanings for Cards / Prononcer Mots |
| `phrases[].gloss` | Same for Ombre phrase meanings |
| `listen[].gloss` | Sentence meaning |
| `listen[].wordEn` | Legacy word gloss |
| `listen[].wordGloss` | `{ en, es, ru }` for the highlighted word |
| `listen[].distractors` | Distractors in the **practice language** (not translated) |
| `grammar[].title` / `rule` / `why` | Locale maps (rule keeps a practice-language entry; why is learner-facing) |
| `skills.*.gloss` | Meanings for Studio drills |
| `skills.meaning.choices` | Optional; **omit** when `gloss` exists — the app derives MCQ distractors from other cards’ `gloss[lang]` |

Keep gloss locale maps when adding L2 packs — do not remove `en` / `es` / `ru`.

## Add a new gloss language (e.g. `de`)

1. Extend every `gloss` / `wordGloss` / `title` / `description` / `grammar.title|rule|why` with `"de": "…"`.
2. Append `"de"` to `catalog.json` → `locales`.
3. Bump each changed pack `version` and the matching catalog entry; set `updatedAt`.
4. Do **not** machine-translate practice text: keep `l2` / `example` / `prompts` in the pack’s `lang`.

## Add a non-French practice pack (e.g. Spanish)

1. Copy `_template.json`, set `"lang": "es"`.
2. Put headwords in `seed[].l2` (do not use `fr` as the headword field).
3. Write `example`, `phrases`, `listen`, `prompts`, and grammar drills in Spanish.
4. Keep `gloss` / `wordGloss` maps for learner locales.
5. Register in `catalog.json` with the same `"lang": "es"`.

## Migrate existing v1 packs

```bash
node scripts/migrate-gloss.mjs
```

This sets `pratiquePack: 2`, lifts flat `en` → `gloss.en` (and `wordEn` → `wordGloss.en`), wraps string `grammar.rule` as `{ fr: … }`, and drops `skills.meaning.choices` once `gloss` is present. Legacy `en` / `wordEn` are kept.

## Validate

```bash
node scripts/validate-packs.mjs
```

Requires every pack + catalog entry to declare `lang`, and every seed item to have `l2` or `fr`.

## Fill es / ru (gloss)

After migrate, add `es` and `ru` on every gloss map (and pack `title` / `description`). Prefer matching seed lemmas for `skills.fren` / `listen.wordGloss`. Keep practice-language text in the pack’s `lang`.

## Try in Pratique

1. Point the app at this catalog branch (or merge to `main`).
2. **Ajouter → Packs distants → Mettre à jour** (reload catalog).
3. Open a pack and switch meaning language to **en / es / ru**.
