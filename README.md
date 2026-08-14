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
| `school-a1.json` | School A1 pack |
| `weather-a1.json` | Weather A1 pack |
| `animals-a1.json` | Animals A1 pack |
| `restaurant-a2.json` | Restaurant A2 pack |
| `hobbies-a2.json` | Hobbies A2 pack |
| `_template.json` | Copy this to add a new pack |

## Levels

| Level | Packs |
|-------|--------|
| A1 | Food, Home, Family, School, Weather, Animals |
| A2 | Travel, Shopping, Health, Restaurant, Hobbies |

## Pack fields → Pratique modes

| Pack field | Feeds |
|------------|--------|
| `seed` | Cartes + Prononcer / Mots (required; each card: `fr`, `en`, `example`, `ipa`, `article`; keep `id`s stable) |
| `phrases` | Prononcer / Ombre (3–6 useful sentences) |
| `listen` | Prononcer / Écoute + Écouter / spot (`word` + `distractors`) |
| `prompts` | Écrire (3–4 writing prompts) |
| `grammar` | Grammaire (1–2 lessons with `rule`, `table`, `questions`) |
| `skills.<drillId>` | Studio drills for Écouter / Parler / Lire / Sens |
| `sounds` | Prononcer / Sons (optional) |

### Skills drill ids

Include at least: `dictation`, `meaning`, `fren`, `aloud`. Add `unscramble` or `signs` when they fit the topic.

Seed `example` sentences also let the app auto-derive many drills — still ship explicit `phrases`, `listen`, `prompts`, and a light `skills` set.

## Add a pack

1. Copy `_template.json` → `school-a2.json` (example)
2. Set `id`, `level`, titles, and description
3. Fill `seed` cards (natural French `example` on every card; keep card `id`s stable)
4. Add `phrases` (3–6), `listen` (2–4), `prompts` (3–4), `grammar` (1–2), and `skills` (dictation / meaning / fren / aloud at minimum)
5. Bump `version` whenever content changes
6. Add an entry to `catalog.json` with matching `id`, `version`, `cardCount`, and `"url": "./school-a2.json"`; set `updatedAt` to today
7. Commit and push to `main`
8. In Pratique → **Ajouter → Packs distants → GitHub → Charger**

## Privacy split

| Repo | Visibility | Contents |
|------|------------|----------|
| `language_practice` | **Private** | Web app source |
| `pratique-packs` (this repo) | **Public** | Catalog + pack JSON only |

Only the vocabulary JSON is public — not your app code.
