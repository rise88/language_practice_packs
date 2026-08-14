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
| `school-a1.json` | School A1 pack |
| `weather-a1.json` | Weather A1 pack |
| `animals-a1.json` | Animals A1 pack |
| `clothes-a1.json` | Clothes A1 pack |
| `time-a1.json` | Time A1 pack |
| `city-a1.json` | In town A1 pack |
| `daily-a1.json` | Daily routine A1 pack |
| `travel-a2.json` | Travel A2 pack |
| `shopping-a2.json` | Shopping A2 pack |
| `health-a2.json` | Health A2 pack |
| `restaurant-a2.json` | Restaurant A2 pack |
| `hobbies-a2.json` | Hobbies A2 pack |
| `work-a2.json` | Work A2 pack |
| `directions-a2.json` | Directions A2 pack |
| `housing-a2.json` | Housing A2 pack |
| `phone-a2.json` | Phone A2 pack |
| `celebrations-a2.json` | Celebrations A2 pack |
| `environment-b1.json` | Environment B1 pack |
| `education-b1.json` | Studies B1 pack |
| `relationships-b1.json` | Relationships B1 pack |
| `money-b1.json` | Money B1 pack |
| `technology-b1.json` | Technology B1 pack |
| `news-b1.json` | News B1 pack |
| `culture-b1.json` | Culture B1 pack |
| `opinions-b1.json` | Opinions B1 pack |
| `nature-b1.json` | Nature B1 pack |
| `admin-b1.json` | Admin B1 pack |
| `workplace-b2.json` | Workplace B2 pack |
| `media-b2.json` | Media and news B2 pack |
| `politics-b2.json` | Politics and citizenship B2 pack |
| `science-b2.json` | Science B2 pack |
| `economy-b2.json` | Economy B2 pack |
| `law-b2.json` | Law and justice B2 pack |
| `climate-b2.json` | Climate and energy B2 pack |
| `psychology-b2.json` | Psychology B2 pack |
| `arts-b2.json` | Arts and film B2 pack |
| `debate-b2.json` | Argumentation B2 pack |
| `academic-c1.json` | Academic discourse C1 pack |
| `diplomacy-c1.json` | International relations C1 pack |
| `philosophy-c1.json` | Philosophy C1 pack |
| `sustainability-c1.json` | Ecological transition C1 pack |
| `ethics-c1.json` | Ethics C1 pack |
| `innovation-c1.json` | Innovation and research C1 pack |
| `society-c1.json` | Social issues C1 pack |
| `contemporary-arts-c1.json` | Contemporary arts C1 pack |
| `linguistics-c1.json` | Language and discourse C1 pack |
| `journalism-c1.json` | Journalism C1 pack |
| `rhetoric-c2.json` | Rhetoric C2 pack |
| `literary-c2.json` | Literary analysis C2 pack |
| `geopolitics-c2.json` | Geopolitics C2 pack |
| `epistemology-c2.json` | Epistemology C2 pack |
| `satire-c2.json` | Irony and satire C2 pack |
| `identity-c2.json` | Identity and otherness C2 pack |
| `aesthetics-c2.json` | Aesthetics C2 pack |
| `rights-c2.json` | Fundamental rights C2 pack |
| `science-c2.json` | Scientific knowledge C2 pack |
| `register-c2.json` | Registers and nuances C2 pack |
| `_template.json` | Copy this to add a new pack |

## Levels

| Level | Packs |
|-------|--------|
| A1 | Food, Home, Family, School, Weather, Animals, Clothes, Time, In town, Daily routine |
| A2 | Travel, Shopping, Health, Restaurant, Hobbies, Work, Directions, Housing, Phone, Celebrations |
| B1 | Environment, Studies, Relationships, Money, Technology, News, Culture, Opinions, Nature, Admin |
| B2 | Workplace, Media and news, Politics and citizenship, Science, Economy, Law and justice, Climate and energy, Psychology, Arts and film, Argumentation |
| C1 | Academic discourse, International relations, Philosophy, Ecological transition, Ethics, Innovation and research, Social issues, Contemporary arts, Language and discourse, Journalism |
| C2 | Rhetoric, Literary analysis, Geopolitics, Epistemology, Irony and satire, Identity and otherness, Aesthetics, Fundamental rights, Scientific knowledge, Registers and nuances |

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
