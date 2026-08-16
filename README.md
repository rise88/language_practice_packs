# language_practice_packs

Public JSON catalog for [Vocalis](https://github.com/rise88/language_practice) (the web app can stay **private**).

Hosting this repo as **public** is free. The app fetches:

`https://raw.githubusercontent.com/rise88/language_practice_packs/main/catalog.json`

## Layout

Packs are grouped by practice language:

| Path | Role |
|------|------|
| `catalog.json` | Index of all packs (still one URL for the app) |
| `fr/*.json` | French L2 packs (`lang: "fr"`) |
| `es/*.json` | Spanish L2 packs (`lang: "es"`) |
| `ru/*.json` | Russian L2 packs (`lang: "ru"`) |
| `_template.json` | Copy into `<lang>/` to add a pack |
| `LAYOUT.md` | Path + catalog URL rules |
| `ADD-LANGUAGE.md` | Gloss locales vs practice language |
| `scripts/` | Validate / migrate / generate helpers |

Each catalog entry points at its language folder, e.g. `"url": "./fr/food-a1.json"`.

Full topic list by CEFR level: see the tables below. Details for folder conventions: [`LAYOUT.md`](LAYOUT.md).

## Practice language (L2)

Each pack and its `catalog.json` entry declare `"lang": "fr"` | `"es"` | `"ru"` | … (ISO code for the language being practiced).

`catalog.json` also lists practice languages in `"languages": ["fr","es","ru"]` and gloss UI languages in `"locales": ["en","es","ru"]`.

| Field | Role |
|-------|------|
| `lang` | Practice language for the whole pack |
| `seed[].l2` | Preferred headword field |
| `seed[].fr` | Legacy headword alias on **French** packs (kept for older app builds) |
| `prompts` | Writing prompts in the pack’s `lang` (not French-by-default) |

Non-French packs should use `l2` for headwords. Do not remove gloss locale maps when adding L2 packs. Validate with `node scripts/validate-packs.mjs`.

## Levels

| Level | French (`lang: fr`) | Spanish (`lang: es`) | Russian (`lang: ru`) |
|-------|--------|--------|--------|
| A1 | Food, Home, Family, School, Weather, Animals, Clothes, Time, In town, Daily routine | Comida, Casa, Familia, Escuela, Clima, Animales, Ropa, Hora, Ciudad, Rutina | Еда, Дом, Семья, Школа, Погода, Животные, Одежда, Время, Город, Распорядок |
| A2 | Travel, Shopping, Health, Restaurant, Hobbies, Work, Directions, Housing, Phone, Celebrations | Viaje, Compras, Salud, Restaurante, Pasatiempos, Trabajo, Direcciones, Vivienda, Teléfono, Celebraciones | Путешествие, Покупки, Здоровье, Ресторан, Хобби, Работа, Направления, Жильё, Телефон, Праздники |
| B1 | Environment, Studies, Relationships, Money, Technology, News, Culture, Opinions, Nature, Admin | Medioambiente, Estudios, Relaciones, Dinero, Tecnología, Noticias, Cultura, Opiniones, Naturaleza, Trámites | Экология, Образование, Отношения, Деньги, Технологии, Новости, Культура, Мнения, Природа, Документы |
| B2 | Workplace, Media and news, Politics and citizenship, Science, Economy, Law and justice, Climate and energy, Psychology, Arts and film, Argumentation | Lugar de trabajo, Medios, Política, Ciencias, Economía, Derecho, Clima y energía, Psicología, Artes, Argumentación | Рабочее место, СМИ, Политика, Науки, Экономика, Право, Климат и энергия, Психология, Искусства, Аргументация |
| C1 | Academic discourse, International relations, Philosophy, Ecological transition, Ethics, Innovation and research, Social issues, Contemporary arts, Language and discourse, Journalism | Académico, Diplomacia, Filosofía, Sostenibilidad, Ética, Innovación, Sociedad, Artes contemporáneas, Lingüística, Periodismo | Академический, Дипломатия, Философия, Устойчивость, Этика, Инновации, Общество, Современное искусство, Лингвистика, Журналистика |
| C2 | Rhetoric, Literary analysis, Geopolitics, Epistemology, Irony and satire, Identity and otherness, Aesthetics, Fundamental rights, Scientific knowledge, Registers and nuances | Retórica, Literario, Geopolítica, Epistemología, Sátira, Identidad, Estética, Derechos, Ciencia, Registros | Риторика, Литературный, Геополитика, Эпистемология, Сатира, Идентичность, Эстетика, Права, Наука, Регистры |

Each level has **10 French + 10 Spanish + 10 Russian** packs with the same section depth (seed, phrases, listen, prompts, grammar, skills).

## Pack fields → Vocalis modes

| Pack field | Feeds |
|------------|--------|
| `lang` | Practice language (L2) for the pack + catalog entry |
| `seed` | Cartes + Prononcer / Mots (required; each card: `l2` preferred or legacy `fr`, legacy `en`, `gloss` `{en,es,ru}`, `example`, `ipa`, `article`; keep `id`s stable) |
| `phrases` | Prononcer / Ombre (3–6 useful sentences in the pack’s `lang`) |
| `listen` | Prononcer / Écoute + Écouter / spot (`word` + `distractors` in the pack’s `lang`) |
| `prompts` | Écrire (3–4 writing prompts **in the pack’s `lang`**) |
| `grammar` | Grammaire (1–2 lessons with `rule`, `table`, `questions`) |
| `skills.<drillId>` | Studio drills for Écouter / Parler / Lire / Sens |
| `sounds` | Prononcer / Sons (optional) |

### Skills drill ids

Include at least: `dictation`, `meaning`, `l2en` (or legacy `fren`), `aloud`. Prefer also `enfr`, `prompt`, `signs`, `pairs`, `gap`, `reorder`, and a `sounds` family (or let the app derive them from seed IPA).

Seed `example` sentences also let the app auto-derive many drills — still ship explicit `phrases`, `listen`, `prompts`, and a light `skills` set.

## Add a pack

1. Copy `_template.json` → `fr/school-a2.json` (or `es/…` / `ru/…`)
2. Set `id`, `level`, `"lang"` (must match the folder), titles, and description
3. Fill `seed` cards with `l2` headwords (French packs may also keep legacy `fr`); natural `example` sentences in the pack’s `lang`; keep card `id`s stable
4. Add `phrases` (3–6), `listen` (2–4), `prompts` (3–4 in the pack’s `lang`), `grammar` (1–2), and `skills` (dictation / meaning / fren / aloud at minimum)
5. Bump `version` whenever content changes
6. Add an entry to `catalog.json` with matching `id`, `version`, `lang`, `cardCount`, and `"url": "./fr/school-a2.json"`; set `updatedAt` to today
7. Run `node scripts/validate-packs.mjs`
8. Commit and push to `main`
9. In Vocalis → **Ajouter → Packs distants → GitHub → Charger**

## Scripts

| Script | Role |
|--------|------|
| `scripts/validate-packs.mjs` | Check `lang`, folder layout, seed headwords, catalog urls |
| `scripts/migrate-gloss.mjs` | Lift v1 flat `en` → `gloss.en` |
| `scripts/enrich-twelve-fixes.py` | Fill grammar gloss/why, expand skills, derive sounds |
| `scripts/generate-spanish-packs.py` | Build Spanish L2 twins from `fr/` into `es/` |
| `scripts/generate-russian-packs.py` | Build Russian L2 twins from `fr/` into `ru/` |
| `scripts/fill-gloss-locales.py` | Fill es/ru gloss maps |

## Privacy split

| Repo | Visibility | Contents |
|------|------------|----------|
| `language_practice` | **Private** | Web app source |
| `language_practice_packs` (this repo) | **Public** | Catalog + pack JSON only |

Only the vocabulary JSON is public — not your app code.
