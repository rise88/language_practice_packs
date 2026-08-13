# pratique-packs

Public JSON catalog for [Pratique](https://github.com/rise88/language_practice) (the web app can stay **private**).

Hosting this repo as **public** is free. The app fetches:

`https://raw.githubusercontent.com/rise88/pratique-packs/main/catalog.json`

## Files

| File | Role |
|------|------|
| `catalog.json` | Index of available packs |
| `food-a1.json` | Food A1 pack |
| `home-a1.json` | Home A1 pack |
| `family-a1.json` | Family A1 pack |
| `travel-a2.json` | Travel A2 pack |
| `shopping-a2.json` | Shopping A2 pack |
| `health-a2.json` | Health A2 pack |
| `_template.json` | Copy this to add a new pack |

## Levels

| Level | Packs |
|-------|--------|
| A1 | Food, Home, Family |
| A2 | Travel, Shopping, Health |

## Add a pack

1. Copy `_template.json` → `school-a2.json` (example)
2. Edit `id`, titles, and `seed` cards (keep card `id`s stable)
3. Add an entry to `catalog.json` with `"url": "./school-a2.json"`
4. Commit and push to `main`
5. In Pratique → **Ajouter → Packs distants → GitHub → Charger**

## Privacy split

| Repo | Visibility | Contents |
|------|------------|----------|
| `language_practice` | **Private** | Web app source |
| `pratique-packs` (this repo) | **Public** | Catalog + pack JSON only |

Only the vocabulary JSON is public — not your app code.
