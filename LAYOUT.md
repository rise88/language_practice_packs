# Repository layout

Pack JSON is grouped by **practice language (L2)**:

```
catalog.json          # single index consumed by Vocalis
_template.json        # copy to <lang>/<id>.json when authoring
fr/                   # French practice packs
  food-a1.json
  …
es/                   # Spanish practice packs
  comida-a1.json
  …
ru/                   # Russian practice packs
  eda-a1.json
  …
scripts/              # validate / migrate / generate helpers
```

## Rules

1. Pack file path must be `<lang>/<id>.json` where `<lang>` matches the pack’s `"lang"` field.
2. Catalog entry `"url"` must be `./<lang>/<id>.json`.
3. Keep one root `catalog.json` — the app still loads a single GitHub URL.
4. Do not put pack JSON in the repo root (except `_template.json`).

## Add a language folder

1. Create `de/` (example).
2. Add packs under it with `"lang": "de"`.
3. Append `"de"` to `catalog.json` → `languages`.
4. Register each pack with `"url": "./de/<id>.json"`.
5. Run `node scripts/validate-packs.mjs`.
