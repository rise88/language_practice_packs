# Adding a learner language (gloss locale)

Pratique pack **v2** (`pratiquePack: 2`) shows card meanings in the learner’s language via `gloss` / `wordGloss` maps. Practice targets (`fr`, `example`, `prompts`, grammar `table` / `questions`) stay **French-only**.

Supported gloss locales in this catalog: **en**, **es**, **ru** (see `catalog.json` → `locales`).

## Field map

| Field | Role |
|-------|------|
| `title` / `description` | Locale maps (`fr` for catalog UI in French + gloss locales) |
| `seed[].en` | Legacy English gloss (kept for older app builds) |
| `seed[].gloss` | `{ en, es, ru }` meanings for Cards / Prononcer Mots |
| `phrases[].gloss` | Same for Ombre phrase meanings |
| `listen[].gloss` | Sentence meaning |
| `listen[].wordEn` | Legacy word gloss |
| `listen[].wordGloss` | `{ en, es, ru }` for the highlighted word |
| `listen[].distractors` | **French** word distractors (not translated) |
| `grammar[].title` / `rule` / `why` | Locale maps (rule keeps `fr`; why is learner-facing) |
| `skills.*.gloss` | Meanings for Studio drills |
| `skills.meaning.choices` | Optional; **omit** when `gloss` exists — the app derives MCQ distractors from other cards’ `gloss[lang]` |
| `prompts` | French writing prompts only |

## Add a new gloss language (e.g. `de`)

1. Extend every `gloss` / `wordGloss` / `title` / `description` / `grammar.title|rule|why` with `"de": "…"`.
2. Append `"de"` to `catalog.json` → `locales`.
3. Bump each changed pack `version` and the matching catalog entry; set `updatedAt`.
4. Do **not** translate `fr`, `example`, `prompts`, or French grammar drill prompts/options.

## Migrate existing v1 packs

```bash
node scripts/migrate-gloss.mjs
```

This sets `pratiquePack: 2`, lifts flat `en` → `gloss.en` (and `wordEn` → `wordGloss.en`), wraps string `grammar.rule` as `{ fr: … }`, and drops `skills.meaning.choices` once `gloss` is present. Legacy `en` / `wordEn` are kept.

## Fill es / ru

After migrate, add `es` and `ru` on every gloss map (and pack `title` / `description`). Prefer matching seed lemmas for `skills.fren` / `listen.wordGloss`. Keep French practice text untouched.

## Try in Pratique

1. Point the app at this catalog branch (or merge to `main`).
2. **Ajouter → Packs distants → Mettre à jour** (reload catalog).
3. Open a pack and switch meaning language to **en / es / ru**.
