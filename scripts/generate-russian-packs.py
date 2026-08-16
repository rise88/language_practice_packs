#!/usr/bin/env python3
"""Generate Russian L2 packs mirroring every French pack (same topics & depth).

Usage:
  python3 scripts/generate-russian-packs.py           # all FR packs
  python3 scripts/generate-russian-packs.py a1 a2     # selected levels
  python3 scripts/generate-russian-packs.py --dry-run
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = Path("/tmp/ru-pack-translate-cache.json")

# French pack id → Russian pack id (Latin slugs)
FR_TO_RU_ID = {
    "food-a1": "eda-a1",
    "home-a1": "dom-a1",
    "family-a1": "semya-a1",
    "school-a1": "shkola-a1",
    "weather-a1": "pogoda-a1",
    "animals-a1": "zhivotnye-a1",
    "clothes-a1": "odezhda-a1",
    "time-a1": "vremya-a1",
    "city-a1": "gorod-a1",
    "daily-a1": "rasporyadok-a1",
    "travel-a2": "puteshestvie-a2",
    "shopping-a2": "pokupki-a2",
    "health-a2": "zdorove-a2",
    "restaurant-a2": "restoran-a2",
    "hobbies-a2": "hobbi-a2",
    "work-a2": "rabota-a2",
    "directions-a2": "napravleniya-a2",
    "housing-a2": "zhilye-a2",
    "phone-a2": "telefon-a2",
    "celebrations-a2": "prazdniki-a2",
    "environment-b1": "ekologiya-b1",
    "education-b1": "obrazovanie-b1",
    "relationships-b1": "otnosheniya-b1",
    "money-b1": "dengi-b1",
    "technology-b1": "tehnologii-b1",
    "news-b1": "novosti-b1",
    "culture-b1": "kultura-b1",
    "opinions-b1": "mneniya-b1",
    "nature-b1": "priroda-b1",
    "admin-b1": "dokumenty-b1",
    "workplace-b2": "rabochee-mesto-b2",
    "media-b2": "smi-b2",
    "politics-b2": "politika-b2",
    "science-b2": "nauki-b2",
    "economy-b2": "ekonomika-b2",
    "law-b2": "pravo-b2",
    "climate-b2": "klimat-energiya-b2",
    "psychology-b2": "psihologiya-b2",
    "arts-b2": "iskusstva-b2",
    "debate-b2": "argumentaciya-b2",
    "academic-c1": "akademicheskij-c1",
    "diplomacy-c1": "diplomatiya-c1",
    "philosophy-c1": "filosofiya-c1",
    "sustainability-c1": "ustojchivost-c1",
    "ethics-c1": "etika-c1",
    "innovation-c1": "innovacii-c1",
    "society-c1": "obshchestvo-c1",
    "contemporary-arts-c1": "sovremennoe-iskusstvo-c1",
    "linguistics-c1": "lingvistika-c1",
    "journalism-c1": "zhurnalistika-c1",
    "rhetoric-c2": "ritorika-c2",
    "literary-c2": "literaturnyj-c2",
    "geopolitics-c2": "geopolitika-c2",
    "epistemology-c2": "epistemologiya-c2",
    "satire-c2": "ironiya-c2",
    "identity-c2": "identichnost-c2",
    "aesthetics-c2": "estetika-c2",
    "rights-c2": "prava-c2",
    "science-c2": "nauka-c2",
    "register-c2": "registry-c2",
}

# Preferred Russian titles (overrides weak FR title.ru when needed)
TITLE_OVERRIDES = {
    "eda-a1": {
        "fr": "Nourriture A1 (RU)",
        "en": "Food A1 (RU)",
        "es": "Comida A1 (RU)",
        "ru": "Еда А1",
    },
    "dom-a1": {
        "fr": "Maison A1 (RU)",
        "en": "Home A1 (RU)",
        "es": "Casa A1 (RU)",
        "ru": "Дом А1",
    },
}

DESC_SUFFIX = {
    "fr": " — pack russe.",
    "en": " — Russian pack.",
    "es": " — paquete ruso.",
    "ru": " — русский пакет.",
}

# Noun gender overrides (lemma → м|ж|ср)
GENDER_OVERRIDES = {
    "хлеб": "м",
    "сыр": "м",
    "кофе": "м",
    "суп": "м",
    "сок": "м",
    "рис": "м",
    "чай": "м",
    "сахар": "м",
    "мёд": "м",
    "мёд": "м",
    "человек": "м",
    "папа": "м",
    "дядя": "м",
    "дедушка": "м",
    "мужчина": "м",
    "кофе": "м",
    "путь": "м",
    "день": "м",
    "огонь": "м",
    "словарь": "м",
    "врач": "м",
    "учитель": "м",
    "телефон": "м",
    "компьютер": "м",
    "интернет": "м",
    "аэропорт": "м",
    "вокзал": "м",
    "парк": "м",
    "музей": "м",
    "ресторан": "м",
    "отель": "м",
    "банк": "м",
    "магазин": "м",
    "рынок": "м",
    "город": "м",
    "дом": "м",
    "стол": "м",
    "стул": "м",
    "диван": "м",
    "шкаф": "м",
    "пол": "м",
    "потолок": "м",
    "мир": "м",
    "год": "м",
    "месяц": "м",
    "час": "м",
    "вечер": "м",
    "утро": "ср",
    "яблоко": "ср",
    "молоко": "ср",
    "масло": "ср",
    "мясо": "ср",
    "вино": "ср",
    "пиво": "ср",
    "время": "ср",
    "имя": "ср",
    "окно": "ср",
    "зеркало": "ср",
    "письмо": "ср",
    "море": "ср",
    "солнце": "ср",
    "небо": "ср",
    "дерево": "ср",
    "поле": "ср",
    "кафе": "ср",
    "метро": "ср",
    "радио": "ср",
    "такси": "ср",
    "меню": "ср",
    "пальто": "ср",
    "кино": "ср",
    "фото": "ср",
    "вода": "ж",
    "еда": "ж",
    "еда": "ж",
    "семья": "ж",
    "школа": "ж",
    "погода": "ж",
    "одежда": "ж",
    "работа": "ж",
    "книга": "ж",
    "ручка": "ж",
    "сумка": "ж",
    "машина": "ж",
    "улица": "ж",
    "площадь": "ж",
    "ночь": "ж",
    "дверь": "ж",
    "кровать": "ж",
    "кухня": "ж",
    "ванная": "ж",
    "комната": "ж",
    "квартира": "ж",
    "жизнь": "ж",
    "любовь": "ж",
    "мать": "ж",
    "дочь": "ж",
    "сестра": "ж",
    "жена": "ж",
    "девушка": "ж",
    "женщина": "ж",
    "собака": "ж",
    "кошка": "ж",
    "рыба": "ж",
    "птица": "ж",
    "зима": "ж",
    "весна": "ж",
    "осень": "ж",
    "неделя": "ж",
    "минута": "ж",
    "секунда": "ж",
    "мама": "ж",
    "бабушка": "ж",
    "тётя": "ж",
    "дочь": "ж",
    "мышь": "ж",
    "ложь": "ж",
    "роль": "ж",
    "соль": "ж",
    "боль": "ж",
    "цель": "ж",
    "часть": "ж",
    "новость": "ж",
    "площадь": "ж",
    "тетрадь": "ж",
    "кровать": "ж",
    "дверь": "ж",
    "мать": "ж",
    "дочь": "ж",
}

FEM_ENDINGS = ("а", "я", "ь")  # ь needs override list; many soft-sign nouns are fem
NEUTER_ENDINGS = ("о", "е", "ё", "мя")
# soft-sign feminine common set
FEM_SOFT = {
    "площадь", "тетрадь", "кровать", "дверь", "мать", "дочь", "ночь", "мышь",
    "ложь", "роль", "соль", "боль", "цель", "часть", "новость", "жизнь",
    "любовь", "кровь", "грязь", "пыль", "мебель", "обувь", "тетрадь",
    "модель", "тетрадь", "осень", "зима",  # зима ends with а
}

cache: dict[str, str] = {}
if CACHE_PATH.exists():
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))

translators = {
    ("fr", "ru"): GoogleTranslator(source="fr", target="ru"),
    ("fr", "en"): GoogleTranslator(source="fr", target="en"),
    ("en", "ru"): GoogleTranslator(source="en", target="ru"),
    ("en", "es"): GoogleTranslator(source="en", target="es"),
    ("ru", "en"): GoogleTranslator(source="ru", target="en"),
    ("ru", "es"): GoogleTranslator(source="ru", target="es"),
}
_pending = 0


def save_cache() -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tr(text: str, source: str, target: str) -> str:
    global _pending
    text = (text or "").strip()
    if not text or source == target:
        return text
    key = f"{source}|{target}|{text}"
    if key in cache and cache[key]:
        return cache[key]
    last_err = None
    for attempt in range(8):
        try:
            out = translators[(source, target)].translate(text)
            if not out:
                raise RuntimeError("empty")
            cache[key] = out
            _pending += 1
            if _pending >= 25:
                save_cache()
                _pending = 0
            time.sleep(0.04)
            return out
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"translate {source}->{target} failed: {text[:60]!r}: {last_err}")


def clean_lemma(gloss_ru: str, gloss_en: str = "") -> str:
    """Pick a single Russian headword from gloss.ru (may contain alternatives)."""
    raw = (gloss_ru or "").strip()
    if not raw:
        raw = tr(gloss_en, "en", "ru") if gloss_en else ""
    # take first alternative
    raw = re.split(r"\s*/\s*|\s*;\s*|\s*\(|,", raw)[0].strip()
    # drop leading gender markers / articles-like noise
    raw = re.sub(r"^(м\.|ж\.|ср\.|the|a|an)\s+", "", raw, flags=re.I)
    raw = raw.strip(" .;:•·")
    # strip trailing gender in parentheses leftovers
    raw = re.sub(r"\s*\([^)]*\)\s*$", "", raw).strip()
    if not raw:
        return raw
    # keep Cyrillic lemmas lowercase unless acronym
    if raw.isupper() and len(raw) <= 4:
        return raw
    return raw[:1].lower() + raw[1:] if raw else raw


def guess_gender(lemma: str) -> str:
    """Return м / ж / ср for Russian noun gender (stored in article field)."""
    w = lemma.strip().lower()
    if not w:
        return "м"
    if w in GENDER_OVERRIDES:
        return GENDER_OVERRIDES[w]
    if w in FEM_SOFT:
        return "ж"
    if w.endswith("мя") or w.endswith(("о", "е", "ё")):
        return "ср"
    if w.endswith(("а", "я")):
        # papa/dedushka etc. overridden above
        return "ж"
    if w.endswith("ь"):
        return "ж" if w in FEM_SOFT else "м"
    return "м"


def russian_ipa(word: str) -> str:
    """Rough Russian IPA for study packs (good enough for TTS hints)."""
    w = word.lower().strip()
    if not w:
        return ""
    # multi-char / digraphs first
    reps = [
        ("щ", "ɕː"), ("ш", "ʂ"), ("ч", "tɕ"), ("ж", "ʐ"), ("ц", "ts"),
        ("ю", "ju"), ("я", "ja"), ("ё", "jo"), ("е", "je"),
        ("ы", "ɨ"), ("й", "j"), ("х", "x"), ("ъ", ""), ("ь", "ʲ"),
        ("а", "a"), ("о", "o"), ("у", "u"), ("и", "i"), ("э", "ɛ"),
        ("б", "b"), ("в", "v"), ("г", "ɡ"), ("д", "d"), ("з", "z"),
        ("к", "k"), ("л", "l"), ("м", "m"), ("н", "n"), ("п", "p"),
        ("р", "r"), ("с", "s"), ("т", "t"), ("ф", "f"),
    ]
    out = w
    for a, b in reps:
        out = out.replace(a, b)
    # mark stress on first vowel if unknown (study hint)
    if "ˈ" not in out:
        vowels = [i for i, c in enumerate(out) if c in "aiuɨɛo"]
        if vowels:
            # prefer penultimate-ish for multisyllabic
            idx = vowels[-2] if len(vowels) >= 2 else vowels[-1]
            out = out[:idx] + "ˈ" + out[idx:]
    return out


def phrase_ipa(sentence: str) -> str:
    words = re.findall(r"[A-Za-zА-Яа-яЁё]+", sentence)
    return " ".join(russian_ipa(w) for w in words[:12])


def scramble_words(sentence: str) -> list[str]:
    parts = sentence.strip().split()
    if not parts:
        return []
    return parts


GRAMMAR_BY_LEVEL: dict[str, list[dict]] = {
    "a1": [
        {
            "title": {
                "fr": "Genre des noms (м / ж / ср)",
                "en": "Noun gender (м / ж / ср)",
                "es": "Género de los sustantivos (м / ж / ср)",
                "ru": "Род существительных (м / ж / ср)",
            },
            "rule": {
                "fr": "м — masculin ; ж — féminin ; ср — neutre.",
                "en": "м — masculine; ж — feminine; ср — neuter.",
                "es": "м — masculino; ж — femenino; ср — neutro.",
                "ru": "м — мужской род; ж — женский род; ср — средний род.",
            },
            "why": {
                "en": "Gender affects adjectives and past-tense verbs.",
                "es": "El género afecta a adjetivos y verbos en pasado.",
                "ru": "Род влияет на прилагательные и глаголы в прошедшем времени.",
            },
            "kind": "gender",
        },
        {
            "title": {
                "fr": "Есть + nom",
                "en": "Есть + noun",
                "es": "Есть + sustantivo",
                "ru": "Есть + существительное",
            },
            "rule": {
                "fr": "Есть introduit ce qui existe : Есть + nom.",
                "en": "Есть introduces what exists: Есть + noun.",
                "es": "Есть presenta lo que existe: Есть + sustantivo.",
                "ru": "Есть вводит то, что есть: Есть + существительное.",
            },
            "why": {
                "en": "Useful to say what you have or what is there.",
                "es": "Útil para decir lo que hay o lo que tienes.",
                "ru": "Полезно, чтобы сказать, что есть или что у вас есть.",
            },
            "kind": "yest",
        },
    ],
    "a2": [
        {
            "title": {
                "fr": "Accusatif après я хочу / я вижу",
                "en": "Accusative after я хочу / я вижу",
                "es": "Acusativo tras я хочу / я вижу",
                "ru": "Винительный падеж после я хочу / я вижу",
            },
            "rule": {
                "fr": "Après un verbe transitif, le complément est souvent à l’accusatif.",
                "en": "After a transitive verb, the object is often in the accusative.",
                "es": "Tras un verbo transitivo, el complemento suele ir en acusativo.",
                "ru": "После переходного глагола дополнение часто стоит в винительном падеже.",
            },
            "why": {
                "en": "Lets you say what you want, see, or buy.",
                "es": "Permite decir lo que quieres, ves o compras.",
                "ru": "Позволяет сказать, что вы хотите, видите или покупаете.",
            },
            "kind": "acc",
        },
        {
            "title": {
                "fr": "Passé : -л / -ла / -ло / -ли",
                "en": "Past tense: -л / -ла / -ло / -ли",
                "es": "Pasado: -л / -ла / -ло / -ли",
                "ru": "Прошедшее время: -л / -ла / -ло / -ли",
            },
            "rule": {
                "fr": "Le passé s’accorde en genre et nombre : был, была, было, были.",
                "en": "Past tense agrees in gender and number: был, была, было, были.",
                "es": "El pasado concuerda en género y número: был, была, было, были.",
                "ru": "Прошедшее время согласуется по роду и числу: был, была, было, были.",
            },
            "why": {
                "en": "Past forms must match the subject.",
                "es": "Las formas del pasado deben coincidir con el sujeto.",
                "ru": "Формы прошедшего должны согласоваться с подлежащим.",
            },
            "kind": "past",
        },
    ],
    "b1": [
        {
            "title": {
                "fr": "Génitif après нет / много",
                "en": "Genitive after нет / много",
                "es": "Genitivo tras нет / много",
                "ru": "Родительный падеж после нет / много",
            },
            "rule": {
                "fr": "После нет, мало, много, без — génitif.",
                "en": "After нет, мало, много, без — use genitive.",
                "es": "Tras нет, мало, много, без — genitivo.",
                "ru": "После нет, мало, много, без — родительный падеж.",
            },
            "why": {
                "en": "Essential for negation and quantities.",
                "es": "Esencial para la negación y las cantidades.",
                "ru": "Необходимо для отрицания и количеств.",
            },
            "kind": "gen",
        },
        {
            "title": {
                "fr": "Verbes de mouvement (идти / ехать)",
                "en": "Verbs of motion (идти / ехать)",
                "es": "Verbos de movimiento (идти / ехать)",
                "ru": "Глаголы движения (идти / ехать)",
            },
            "rule": {
                "fr": "Идти — à pied ; ехать — en véhicule (direction précise).",
                "en": "Идти — on foot; ехать — by vehicle (specific direction).",
                "es": "Идти — a pie; ехать — en vehículo (dirección concreta).",
                "ru": "Идти — пешком; ехать — на транспорте (конкретное направление).",
            },
            "why": {
                "en": "Choosing the right motion verb sounds natural.",
                "es": "Elegir el verbo de movimiento correcto suena natural.",
                "ru": "Правильный глагол движения звучит естественно.",
            },
            "kind": "motion",
        },
    ],
    "b2": [
        {
            "title": {
                "fr": "Instrumental (кем / чем)",
                "en": "Instrumental case (кем / чем)",
                "es": "Caso instrumental (кем / чем)",
                "ru": "Творительный падеж (кем / чем)",
            },
            "rule": {
                "fr": "Творительный marque le moyen, l’accompagnement ou le prédicat (стать врачом).",
                "en": "Instrumental marks means, company, or predicate nouns (стать врачом).",
                "es": "El instrumental marca medio, compañía o predicado (стать врачом).",
                "ru": "Творительный обозначает средство, совместность или предикатив (стать врачом).",
            },
            "why": {
                "en": "Needed for professions, tools, and «with».",
                "es": "Necesario para profesiones, herramientas y «con».",
                "ru": "Нужен для профессий, инструментов и значения «с».",
            },
            "kind": "instr",
        },
        {
            "title": {
                "fr": "Aspect perfectif / imperfectif",
                "en": "Perfective / imperfective aspect",
                "es": "Aspecto perfectivo / imperfectivo",
                "ru": "Вид глагола: совершенный / несовершенный",
            },
            "rule": {
                "fr": "Imperfectif = processus / habitude ; perfectif = résultat achevé.",
                "en": "Imperfective = process / habit; perfective = completed result.",
                "es": "Imperfectivo = proceso / hábito; perfectivo = resultado terminado.",
                "ru": "Несовершенный — процесс / привычка; совершенный — завершённый результат.",
            },
            "why": {
                "en": "Aspect is central to natural Russian storytelling.",
                "es": "El aspecto es central en la narración rusa natural.",
                "ru": "Вид — ключ к естественному русскому рассказу.",
            },
            "kind": "aspect",
        },
    ],
    "c1": [
        {
            "title": {
                "fr": "Nominalisation savante",
                "en": "Academic nominalization",
                "es": "Nominalización académica",
                "ru": "Академическая номинализация",
            },
            "rule": {
                "fr": "Préférez un nom abstrait : рассмотрение вопроса, pas рассматривать вопрос.",
                "en": "Prefer an abstract noun: рассмотрение вопроса, not рассматривать вопрос.",
                "es": "Prefiere un sustantivo abstracto: рассмотрение вопроса.",
                "ru": "Предпочитайте абстрактное существительное: рассмотрение вопроса, а не рассматривать вопрос.",
            },
            "why": {
                "en": "Matches formal academic tone.",
                "es": "Encaja con el tono académico formal.",
                "ru": "Соответствует формальному академическому тону.",
            },
            "kind": "nom",
        },
        {
            "title": {
                "fr": "Participes et gerundifs",
                "en": "Participles and verbal adverbs",
                "es": "Participios y gerundios",
                "ru": "Причастия и деепричастия",
            },
            "rule": {
                "fr": "Причастие qualifie un nom ; деепричастие ajoute une action secondaire.",
                "en": "A participle modifies a noun; a verbal adverb adds a secondary action.",
                "es": "El participio modifica un sustantivo; el gerundio añade una acción secundaria.",
                "ru": "Причастие определяет существительное; деепричастие добавляет второстепенное действие.",
            },
            "why": {
                "en": "Dense written Russian relies on these forms.",
                "es": "El ruso escrito denso depende de estas formas.",
                "ru": "Плотный письменный русский опирается на эти формы.",
            },
            "kind": "part",
        },
    ],
    "c2": [
        {
            "title": {
                "fr": "Registres et nuances lexicales",
                "en": "Registers and lexical nuance",
                "es": "Registros y matices léxicos",
                "ru": "Регистры и лексические оттенки",
            },
            "rule": {
                "fr": "Alternez vocabulaire savant et marqué (ironie, euphémisme) selon le genre.",
                "en": "Switch between learned and marked lexicon (irony, euphemism) by genre.",
                "es": "Alterna léxico culto y marcado (ironía, eufemismo) según el género.",
                "ru": "Чередуйте книжную и маркированную лексику (ирония, эвфемизм) в зависимости от жанра.",
            },
            "why": {
                "en": "Control tone at near-native level.",
                "es": "Controla el tono a un nivel casi nativo.",
                "ru": "Контроль тона на почти родном уровне.",
            },
            "kind": "register",
        },
        {
            "title": {
                "fr": "Constructions concessives complexes",
                "en": "Complex concessive constructions",
                "es": "Construcciones concesivas complejas",
                "ru": "Сложные уступительные конструкции",
            },
            "rule": {
                "fr": "Несмотря на / хотя / даже если intensifient la concession.",
                "en": "Несмотря на / хотя / даже если intensify concession.",
                "es": "Несмотря на / хотя / даже если intensifican la concesión.",
                "ru": "Несмотря на / хотя / даже если усиливают уступку.",
            },
            "why": {
                "en": "Useful in critique and rhetoric.",
                "es": "Útil en la crítica y la retórica.",
                "ru": "Полезно в критике и риторике.",
            },
            "kind": "conc",
        },
    ],
}


def build_grammar(level: str, ru_id: str, seeds: list[dict]) -> list[dict]:
    templates = GRAMMAR_BY_LEVEL.get(level, GRAMMAR_BY_LEVEL["a1"])
    nouns = [s for s in seeds if s.get("article")]
    if len(nouns) < 4:
        nouns = seeds
    out = []
    for i, tmpl in enumerate(templates, start=1):
        a = nouns[i % len(nouns)]
        b = nouns[(i + 3) % len(nouns)]
        g_a, lem_a = a.get("article", "м"), a["l2"]
        g_b, lem_b = b.get("article", "м"), b["l2"]
        kind = tmpl["kind"]
        table = [["Форма", "Употребление", "Пример"]]
        questions = []
        if kind == "gender":
            table += [
                ["м", "мужской род", f"{lem_a}" if g_a == "м" else f"{lem_b}"],
                ["ж", "женский род", f"{lem_a}" if g_a == "ж" else f"{lem_b}"],
                ["ср", "средний род", "окно / молоко"],
            ]
            questions = [
                {
                    "id": f"remote-{ru_id}-gq-{i}-1",
                    "prompt": f"Род слова «{lem_a}»?",
                    "answer": g_a,
                    "options": ["м", "ж", "ср"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-2",
                    "prompt": f"Род слова «{lem_b}»?",
                    "answer": g_b,
                    "options": ["м", "ж", "ср"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-3",
                    "prompt": f"Выберите род: {lem_a}",
                    "answer": g_a,
                    "options": [g_a, "ж" if g_a != "ж" else "м", "ср"],
                },
            ]
        elif kind == "yest":
            table += [
                ["Есть", "наличие", f"Есть {lem_a}."],
                ["Нет", "отсутствие (+ род. п.)", f"Нет {lem_b}."],
            ]
            questions = [
                {
                    "id": f"remote-{ru_id}-gq-{i}-1",
                    "prompt": f"Дополните: ___ {lem_a}.",
                    "answer": "Есть",
                    "options": ["Есть", "Это", "Быть"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-2",
                    "prompt": f"Дополните: ___ {lem_b}. (отрицание)",
                    "answer": "Нет",
                    "options": ["Нет", "Есть", "Да"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-3",
                    "prompt": f"У меня ___ {lem_a}.",
                    "answer": "есть",
                    "options": ["есть", "это", "быть"],
                },
            ]
        elif kind == "acc":
            table += [
                ["я вижу + Вин.", "объект", f"Я вижу {lem_a}."],
                ["я хочу + Вин.", "желание", f"Я хочу {lem_b}."],
            ]
            questions = [
                {
                    "id": f"remote-{ru_id}-gq-{i}-1",
                    "prompt": f"Я вижу ___ . ({lem_a})",
                    "answer": lem_a,
                    "options": [lem_a, lem_b, "нет"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-2",
                    "prompt": "После «я хочу» обычно нужен ___ падеж.",
                    "answer": "винительный",
                    "options": ["винительный", "творительный", "предложный"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-3",
                    "prompt": f"Я покупаю ___ .",
                    "answer": lem_b,
                    "options": [lem_b, "нет", "есть"],
                },
            ]
        elif kind == "past":
            table += [
                ["-л", "м. р.", "Он был дома."],
                ["-ла", "ж. р.", "Она была дома."],
                ["-ли", "мн. ч.", "Они были дома."],
            ]
            questions = [
                {
                    "id": f"remote-{ru_id}-gq-{i}-1",
                    "prompt": "Вчера он ___ дома. (быть)",
                    "answer": "был",
                    "options": ["был", "была", "были"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-2",
                    "prompt": "Вчера она ___ дома. (быть)",
                    "answer": "была",
                    "options": ["была", "был", "было"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-3",
                    "prompt": "Вчера они ___ дома. (быть)",
                    "answer": "были",
                    "options": ["были", "был", "была"],
                },
            ]
        elif kind == "gen":
            table += [
                ["нет + Род.", "отрицание", f"Нет {lem_a}."],
                ["много + Род.", "количество", f"Много {lem_b}."],
            ]
            questions = [
                {
                    "id": f"remote-{ru_id}-gq-{i}-1",
                    "prompt": "После «нет» нужен ___ падеж.",
                    "answer": "родительный",
                    "options": ["родительный", "винительный", "дательный"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-2",
                    "prompt": f"У меня нет ___ . (тема: {lem_a})",
                    "answer": lem_a,
                    "options": [lem_a, "есть", "это"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-3",
                    "prompt": "Много / мало / без → ___ падеж.",
                    "answer": "родительный",
                    "options": ["родительный", "творительный", "именительный"],
                },
            ]
        elif kind == "motion":
            table += [
                ["идти", "пешком", "Я иду в магазин."],
                ["ехать", "на транспорте", "Я еду на работу."],
            ]
            questions = [
                {
                    "id": f"remote-{ru_id}-gq-{i}-1",
                    "prompt": "Пешком в парк: я ___ .",
                    "answer": "иду",
                    "options": ["иду", "еду", "летаю"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-2",
                    "prompt": "На автобусе: я ___ .",
                    "answer": "еду",
                    "options": ["еду", "иду", "хожу"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-3",
                    "prompt": "Конкретное направление на машине — глагол ___ .",
                    "answer": "ехать",
                    "options": ["ехать", "идти", "быть"],
                },
            ]
        elif kind == "instr":
            table += [
                ["чем", "средство", f"Пишу ручкой / говорю о {lem_a}."],
                ["кем", "профессия", "Он стал врачом."],
            ]
            questions = [
                {
                    "id": f"remote-{ru_id}-gq-{i}-1",
                    "prompt": "Стать врачом — ___ падеж.",
                    "answer": "творительный",
                    "options": ["творительный", "родительный", "винительный"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-2",
                    "prompt": "Я пишу ___ . (карандаш)",
                    "answer": "карандашом",
                    "options": ["карандашом", "карандаш", "карандаша"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-3",
                    "prompt": f"Тема «{lem_a}» часто требует предложных конструкций.",
                    "answer": "творительный",
                    "options": ["творительный", "именительный", "звательный"],
                },
            ]
        elif kind == "aspect":
            table += [
                ["НСВ", "процесс / привычка", "Я читал книгу час."],
                ["СВ", "результат", "Я прочитал книгу."],
            ]
            questions = [
                {
                    "id": f"remote-{ru_id}-gq-{i}-1",
                    "prompt": "Результат: я ___ книгу. (прочитать)",
                    "answer": "прочитал",
                    "options": ["прочитал", "читал", "буду читать"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-2",
                    "prompt": "Процесс: я долго ___ . (читать)",
                    "answer": "читал",
                    "options": ["читал", "прочитал", "прочту"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-3",
                    "prompt": "Привычка обычно выражается ___ видом.",
                    "answer": "несовершенным",
                    "options": ["несовершенным", "совершенным", "будущим"],
                },
            ]
        elif kind == "nom":
            table += [
                ["глагол → имя", "формальный стиль", f"наличие {lem_a}"],
                ["избегать придаточного", "плотность", f"отсутствие {lem_b}"],
            ]
            questions = [
                {
                    "id": f"remote-{ru_id}-gq-{i}-1",
                    "prompt": "Предпочтительнее: ___ вопроса. (рассмотреть)",
                    "answer": "рассмотрение",
                    "options": ["рассмотрение", "рассмотреть", "рассмотренный"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-2",
                    "prompt": f"Анализ {lem_a} — более академично, чем «анализировать».",
                    "answer": "анализ",
                    "options": ["анализ", "анализировать", "аналитик"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-3",
                    "prompt": "Лучше существительное, а не ___ .",
                    "answer": "глагол",
                    "options": ["глагол", "союз", "междометие"],
                },
            ]
        elif kind == "part":
            table += [
                ["причастие", "определение", "книга, написанная автором"],
                ["деепричастие", "второе действие", "Читая, он делал заметки."],
            ]
            questions = [
                {
                    "id": f"remote-{ru_id}-gq-{i}-1",
                    "prompt": "Форма, определяющая существительное — ___ .",
                    "answer": "причастие",
                    "options": ["причастие", "деепричастие", "наречие"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-2",
                    "prompt": "«Читая» в «Читая, он…» — это ___ .",
                    "answer": "деепричастие",
                    "options": ["деепричастие", "причастие", "инфинитив"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-3",
                    "prompt": "В академическом тексте часто нужны ___ .",
                    "answer": "причастия",
                    "options": ["причастия", "междометия", "обращения"],
                },
            ]
        elif kind == "register":
            table += [
                ["книжный", "формальный", f"рассматривать {lem_a}"],
                ["маркированный", "ирония / эвфемизм", f"то, что связано с {lem_b}"],
            ]
            questions = [
                {
                    "id": f"remote-{ru_id}-gq-{i}-1",
                    "prompt": "Книжный регистр: ___ (не «смотреть»).",
                    "answer": "рассматривать",
                    "options": ["рассматривать", "смотреть", "глядеть"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-2",
                    "prompt": "Эвфемизм смягчает ___ .",
                    "answer": "тон",
                    "options": ["тон", "род", "падеж"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-3",
                    "prompt": f"Оттенок для обсуждения «{lem_a}» в эссе — ___ .",
                    "answer": "дискурс",
                    "options": ["дискурс", "болтовня", "сленг"],
                },
            ]
        else:  # conc
            table += [
                ["несмотря на", "+ Вин.", f"Несмотря на {lem_a}, продолжаю."],
                ["хотя / даже если", "уступка", f"Хотя есть {lem_b}, сомневаюсь."],
            ]
            questions = [
                {
                    "id": f"remote-{ru_id}-gq-{i}-1",
                    "prompt": "Несмотря ___ трудности, иду дальше.",
                    "answer": "на",
                    "options": ["на", "о", "в"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-2",
                    "prompt": "___ холодно, я выхожу. (уступка)",
                    "answer": "Хотя",
                    "options": ["Хотя", "Потому", "Когда"],
                },
                {
                    "id": f"remote-{ru_id}-gq-{i}-3",
                    "prompt": "Даже если будет сложно, я ___ .",
                    "answer": "попробую",
                    "options": ["попробую", "пробовал", "пробую бы"],
                },
            ]
        while len(questions) < 5:
            n = len(questions) + 1
            alt = "ж" if g_a == "м" else "м"
            questions.append(
                {
                    "id": f"remote-{ru_id}-gq-{i}-{n}",
                    "prompt": f"Свяжите с темой: {lem_a} / {lem_b}. Род «{lem_a}»?",
                    "answer": g_a,
                    "options": [g_a, g_b if g_b != g_a else alt, "ср"],
                }
            )
        out.append(
            {
                "id": f"remote-{ru_id}-grammar-{i}",
                "title": tmpl["title"],
                "rule": tmpl["rule"],
                "why": tmpl["why"],
                "table": table,
                "questions": questions[:5],
            }
        )
    return out


def translate_sentence_fr_ru(fr: str) -> str:
    return tr(fr, "fr", "ru")


def build_pack(fr: dict) -> dict:
    fr_id = fr["id"]
    ru_id = FR_TO_RU_ID[fr_id]
    level = fr["level"]

    title = {
        "fr": f"{fr['title'].get('fr', fr_id)} (RU)",
        "en": f"{fr['title'].get('en', fr_id)} (RU)",
        "es": f"{fr['title'].get('es', fr_id)} (RU)",
        "ru": fr["title"].get("ru", ru_id),
    }
    if ru_id in TITLE_OVERRIDES:
        title = TITLE_OVERRIDES[ru_id]

    description = {}
    for loc in ("fr", "en", "es", "ru"):
        base = fr.get("description", {}).get(loc, "")
        if loc == "ru" and base:
            description[loc] = (
                base if "русск" in base.lower() else base.rstrip(".") + DESC_SUFFIX[loc]
            )
        else:
            description[loc] = (base.rstrip(".") + DESC_SUFFIX[loc]) if base else DESC_SUFFIX[loc].strip(" —")

    seeds = []
    for i, card in enumerate(fr.get("seed") or [], start=1):
        en = card.get("en") or card.get("gloss", {}).get("en") or ""
        gloss_ru = card.get("gloss", {}).get("ru") or ""
        lemma = clean_lemma(gloss_ru, en)
        if not lemma:
            lemma = translate_sentence_fr_ru(card.get("fr") or card.get("l2") or "")
            lemma = clean_lemma(lemma, en)
        gloss = {
            "en": card.get("gloss", {}).get("en") or en,
            "es": card.get("gloss", {}).get("es") or tr(en, "en", "es"),
            "ru": gloss_ru if gloss_ru else lemma,
        }
        example_fr = card.get("example") or ""
        example = translate_sentence_fr_ru(example_fr) if example_fr else f"Пример со словом «{lemma}»."
        gender = guess_gender(lemma)
        seeds.append(
            {
                "id": f"remote-{ru_id}-{i}",
                "l2": lemma,
                "en": en,
                "gloss": gloss,
                "example": example,
                "ipa": russian_ipa(lemma),
                "article": gender,
            }
        )

    phrases = []
    for i, p in enumerate(fr.get("phrases") or [], start=1):
        src = p.get("fr") or p.get("l2") or ""
        l2 = translate_sentence_fr_ru(src)
        en = p.get("en") or p.get("gloss", {}).get("en") or tr(l2, "ru", "en")
        gloss = p.get("gloss") or {}
        phrases.append(
            {
                "id": f"remote-{ru_id}-phrase-{i}",
                "l2": l2,
                "en": en,
                "gloss": {
                    "en": gloss.get("en") or en,
                    "es": gloss.get("es") or tr(en, "en", "es"),
                    "ru": gloss.get("ru") or l2,
                },
                "ipa": phrase_ipa(l2),
            }
        )

    listen = []
    for i, item in enumerate(fr.get("listen") or [], start=1):
        src = item.get("fr") or item.get("l2") or ""
        l2 = translate_sentence_fr_ru(src)
        en = item.get("en") or item.get("gloss", {}).get("en") or tr(l2, "ru", "en")
        word_fr = item.get("word") or ""
        word = ""
        for s_fr, s_ru in zip(fr.get("seed") or [], seeds):
            if (s_fr.get("fr") or s_fr.get("l2")) == word_fr:
                word = s_ru["l2"]
                break
        if not word:
            word = clean_lemma(tr(word_fr, "fr", "ru"), item.get("wordEn") or "")
        distractors_fr = item.get("distractors") or []
        distractors = []
        for d in distractors_fr:
            mapped = None
            for s_fr, s_ru in zip(fr.get("seed") or [], seeds):
                if (s_fr.get("fr") or s_fr.get("l2")) == d:
                    mapped = s_ru["l2"]
                    break
            distractors.append(mapped or clean_lemma(tr(d, "fr", "ru")))
        distractors = [x for x in distractors if x and x != word][:3]
        while len(distractors) < 3:
            for s in seeds:
                if s["l2"] != word and s["l2"] not in distractors:
                    distractors.append(s["l2"])
                if len(distractors) >= 3:
                    break
            break
        wg = item.get("wordGloss") or {}
        listen.append(
            {
                "id": f"remote-{ru_id}-listen-{i}",
                "l2": l2,
                "en": en,
                "gloss": {
                    "en": (item.get("gloss") or {}).get("en") or en,
                    "es": (item.get("gloss") or {}).get("es") or tr(en, "en", "es"),
                    "ru": (item.get("gloss") or {}).get("ru") or l2,
                },
                "word": word,
                "wordEn": item.get("wordEn") or wg.get("en") or "",
                "wordGloss": {
                    "en": wg.get("en") or item.get("wordEn") or "",
                    "es": wg.get("es") or tr(item.get("wordEn") or word, "en", "es"),
                    "ru": wg.get("ru") or word,
                },
                "wordIpa": russian_ipa(word),
                "distractors": distractors,
            }
        )

    prompts = []
    for pr in fr.get("prompts") or []:
        prompts.append(translate_sentence_fr_ru(pr))

    grammar = build_grammar(level, ru_id, seeds)

    skills_in = fr.get("skills") or {}
    skills: dict = {}

    def map_skill_items(key: str, items: list) -> list:
        out = []
        for i, it in enumerate(items or [], start=1):
            if key in ("fren", "signs"):
                src = it.get("fr") or it.get("l2") or ""
                lemma = ""
                for s_fr, s_ru in zip(fr.get("seed") or [], seeds):
                    if (s_fr.get("fr") or s_fr.get("l2")) == src:
                        lemma = s_ru["l2"]
                        break
                if not lemma:
                    lemma = clean_lemma(tr(src, "fr", "ru"), it.get("en") or "")
                entry = {
                    "id": f"remote-{ru_id}-{key[:4]}-{i}",
                    "l2": lemma,
                    "en": it.get("en") or "",
                    "gloss": {
                        "en": (it.get("gloss") or {}).get("en") or it.get("en") or "",
                        "es": (it.get("gloss") or {}).get("es") or tr(it.get("en") or lemma, "en", "es"),
                        "ru": (it.get("gloss") or {}).get("ru") or lemma,
                    },
                }
                if key == "signs" and it.get("hint"):
                    entry["hint"] = tr(it["hint"], "fr", "ru") if it["hint"] else it.get("hint")
                    if entry["hint"] == it.get("hint") and it.get("hint"):
                        try:
                            entry["hint"] = tr(it["hint"], "en", "ru")
                        except Exception:  # noqa: BLE001
                            pass
                out.append(entry)
                continue

            src = it.get("fr") or it.get("l2") or ""
            l2 = translate_sentence_fr_ru(src)
            en = it.get("en") or (it.get("gloss") or {}).get("en") or tr(l2, "ru", "en")
            entry = {
                "id": f"remote-{ru_id}-{key[:4]}-{i}",
                "l2": l2,
                "en": en,
                "gloss": {
                    "en": (it.get("gloss") or {}).get("en") or en,
                    "es": (it.get("gloss") or {}).get("es") or tr(en, "en", "es"),
                    "ru": (it.get("gloss") or {}).get("ru") or l2,
                },
            }
            if key in ("dictation", "aloud"):
                entry["ipa"] = phrase_ipa(l2)
            if key == "unscramble":
                entry["words"] = scramble_words(l2)
            out.append(entry)
        return out

    for key in ("dictation", "meaning", "fren", "aloud", "unscramble", "signs"):
        if key in skills_in and skills_in[key]:
            skills[key] = map_skill_items(key, skills_in[key])

    if len(skills.get("dictation", [])) < 3 and seeds:
        skills["dictation"] = skills.get("dictation") or []
        for s in seeds:
            if len(skills["dictation"]) >= 3:
                break
            ex = s["example"]
            if any(x.get("l2") == ex for x in skills["dictation"]):
                continue
            skills["dictation"].append(
                {
                    "id": f"remote-{ru_id}-dict-{len(skills['dictation'])+1}",
                    "l2": ex,
                    "en": s.get("en") or "",
                    "gloss": {"en": s.get("en") or "", "es": s["gloss"].get("es", ""), "ru": ex},
                    "ipa": phrase_ipa(ex),
                }
            )
    if len(skills.get("meaning", [])) < 3 and seeds:
        skills["meaning"] = skills.get("meaning") or []
        for s in seeds[3:]:
            if len(skills["meaning"]) >= 3:
                break
            ex = s["example"]
            skills["meaning"].append(
                {
                    "id": f"remote-{ru_id}-mean-{len(skills['meaning'])+1}",
                    "l2": ex,
                    "en": s.get("en") or "",
                    "gloss": {"en": s.get("en") or "", "es": s["gloss"].get("es", ""), "ru": ex},
                }
            )
    if len(skills.get("fren", [])) < 6 and seeds:
        skills["fren"] = [
            {
                "id": f"remote-{ru_id}-fren-{i}",
                "l2": s["l2"],
                "en": s.get("en") or "",
                "gloss": s["gloss"],
            }
            for i, s in enumerate(seeds[:6], start=1)
        ]
    if len(skills.get("aloud", [])) < 3 and seeds:
        skills["aloud"] = skills.get("aloud") or []
        for s in seeds[6:]:
            if len(skills["aloud"]) >= 3:
                break
            ex = s["example"]
            skills["aloud"].append(
                {
                    "id": f"remote-{ru_id}-aloud-{len(skills['aloud'])+1}",
                    "l2": ex,
                    "en": s.get("en") or "",
                    "gloss": {"en": s.get("en") or "", "es": s["gloss"].get("es", ""), "ru": ex},
                    "ipa": phrase_ipa(ex),
                }
            )
    if len(skills.get("unscramble", [])) < 2 and seeds:
        skills["unscramble"] = []
        for i, s in enumerate(seeds[:2], start=1):
            skills["unscramble"].append(
                {
                    "id": f"remote-{ru_id}-unsc-{i}",
                    "l2": s["example"],
                    "en": s.get("en") or "",
                    "gloss": {"en": s.get("en") or "", "es": s["gloss"].get("es", ""), "ru": s["example"]},
                    "words": scramble_words(s["example"]),
                }
            )

    while len(phrases) < len(fr.get("phrases") or []) and seeds:
        s = seeds[len(phrases) % len(seeds)]
        phrases.append(
            {
                "id": f"remote-{ru_id}-phrase-{len(phrases)+1}",
                "l2": s["example"],
                "en": s.get("en") or "",
                "gloss": {"en": s.get("en") or "", "es": s["gloss"].get("es", ""), "ru": s["example"]},
                "ipa": phrase_ipa(s["example"]),
            }
        )
    while len(listen) < len(fr.get("listen") or []) and len(seeds) >= 4:
        idx = len(listen)
        s = seeds[idx % len(seeds)]
        distractors = [x["l2"] for x in seeds if x["l2"] != s["l2"]][:3]
        listen.append(
            {
                "id": f"remote-{ru_id}-listen-{idx+1}",
                "l2": s["example"],
                "en": s.get("en") or "",
                "gloss": {"en": s.get("en") or "", "es": s["gloss"].get("es", ""), "ru": s["example"]},
                "word": s["l2"],
                "wordEn": s.get("en") or "",
                "wordGloss": s["gloss"],
                "wordIpa": s["ipa"],
                "distractors": distractors,
            }
        )
    while len(prompts) < max(4, len(fr.get("prompts") or [])):
        prompts.append(f"Напишите три предложения на тему «{seeds[len(prompts) % len(seeds)]['l2']}».")

    pack = {
        "pratiquePack": 2,
        "id": ru_id,
        "version": 1,
        "level": level,
        "lang": "ru",
        "title": title,
        "description": description,
        "seed": seeds,
        "phrases": phrases,
        "listen": listen,
        "prompts": prompts,
        "grammar": grammar,
        "skills": skills,
        "sounds": [],
    }
    return pack


def update_catalog(packs: list[dict]) -> None:
    catalog_path = ROOT / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    by_id = {e["id"]: i for i, e in enumerate(catalog["packs"])}
    for pack in packs:
        entry = {
            "id": pack["id"],
            "version": pack["version"],
            "level": pack["level"],
            "lang": "ru",
            "title": pack["title"],
            "description": pack["description"],
            "cardCount": len(pack["seed"]),
            "url": f"./{pack['id']}.json",
        }
        if pack["id"] in by_id:
            catalog["packs"][by_id[pack["id"]]] = entry
        else:
            catalog["packs"].append(entry)
            by_id[pack["id"]] = len(catalog["packs"]) - 1
    catalog["updatedAt"] = "2026-08-16"
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    dry = "--dry-run" in sys.argv
    levels = {a.lower() for a in sys.argv[1:] if not a.startswith("-")}
    fr_files = sorted(
        p for p in ROOT.glob("*.json") if p.name not in {"catalog.json", "_template.json"}
    )
    fr_packs = []
    for path in fr_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("lang") != "fr":
            continue
        if levels and data.get("level") not in levels:
            continue
        if data["id"] not in FR_TO_RU_ID:
            print(f"skip unmapped {data['id']}")
            continue
        fr_packs.append(data)

    print(f"Generating {len(fr_packs)} Russian packs…")
    built = []
    for i, fr in enumerate(fr_packs, start=1):
        ru_id = FR_TO_RU_ID[fr["id"]]
        print(f"[{i}/{len(fr_packs)}] {fr['id']} → {ru_id}", flush=True)
        pack = build_pack(fr)
        built.append(pack)
        if not dry:
            out = ROOT / f"{ru_id}.json"
            out.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            save_cache()
    if not dry:
        update_catalog(built)
        save_cache()
    print(f"Done: {len(built)} packs" + (" (dry-run)" if dry else ""))


if __name__ == "__main__":
    main()
