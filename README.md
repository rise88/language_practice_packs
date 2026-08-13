# pratique-packs

Public JSON catalog for [Pratique](https://github.com/rise88/language_practice) (the web app can stay **private**).

Hosting this repo as **public** is free. The app fetches:

`https://raw.githubusercontent.com/rise88/pratique-packs/main/catalog.json`

## Files

| File | Role |
|------|------|
| `catalog.json` | Index of available packs |
| `travel-a2.json` | Sample Travel A2 pack |
| `food-a1.json` | Sample Food A1 pack |
| `_template.json` | Copy this to add a new pack |

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
