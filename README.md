# language_practice_packs

Public JSON catalog for [Vocalis](https://github.com/rise88/language_practice) (the web app can stay **private**).

Hosting this repo as **public** is free. The app fetches:

`https://raw.githubusercontent.com/rise88/language_practice_packs/main/catalog.json`

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
| `_template.json` | Copy this to add a new pack (pratiquePack **v2** + `lang` / `l2`) |
| `ADD-LANGUAGE.md` | Gloss locales (en/es/ru) + practice language (`lang`) |
| `scripts/migrate-gloss.mjs` | Lift v1 flat `en` → `gloss.en` |
| `scripts/validate-packs.mjs` | Check every pack has `lang`; every seed has `l2` or `fr` |
| `scripts/enrich-twelve-fixes.py` | Fill grammar gloss/why, expand skills, derive sounds |
| `scripts/generate-spanish-packs.py` | Build Spanish L2 twins from French packs |
| `scripts/generate-russian-packs.py` | Build Russian L2 twins from French packs |
| `comida-a1.json` … `registros-c2.json` | Full Spanish L2 catalog (60 packs, A1–C2) mirroring French topics |
| `eda-a1.json` … `ironiya-c2.json` / `registry-c2.json` | Full Russian L2 catalog (60 packs, A1–C2) mirroring French topics |

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

1. Copy `_template.json` → `school-a2.json` (example)
2. Set `id`, `level`, `"lang"` (practice L2), titles, and description
3. Fill `seed` cards with `l2` headwords (French packs may also keep legacy `fr`); natural `example` sentences in the pack’s `lang`; keep card `id`s stable
4. Add `phrases` (3–6), `listen` (2–4), `prompts` (3–4 in the pack’s `lang`), `grammar` (1–2), and `skills` (dictation / meaning / fren / aloud at minimum)
5. Bump `version` whenever content changes
6. Add an entry to `catalog.json` with matching `id`, `version`, `lang`, `cardCount`, and `"url": "./school-a2.json"`; set `updatedAt` to today
7. Run `node scripts/validate-packs.mjs`
8. Commit and push to `main`
9. In Vocalis → **Ajouter → Packs distants → GitHub → Charger**

## Privacy split

| Repo | Visibility | Contents |
|------|------------|----------|
| `language_practice` | **Private** | Web app source |
| `language_practice_packs` (this repo) | **Public** | Catalog + pack JSON only |

Only the vocabulary JSON is public — not your app code.
