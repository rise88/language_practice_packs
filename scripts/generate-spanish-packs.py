#!/usr/bin/env python3
"""Generate Spanish L2 packs mirroring every French pack (same topics & depth).

Usage:
  python3 scripts/generate-spanish-packs.py           # all FR packs
  python3 scripts/generate-spanish-packs.py a1 a2     # selected levels
  python3 scripts/generate-spanish-packs.py --dry-run
"""

from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = Path("/tmp/es-pack-translate-cache.json")

# French pack id → Spanish pack id (existing three kept)
FR_TO_ES_ID = {
    "food-a1": "comida-a1",
    "home-a1": "casa-a1",
    "family-a1": "familia-a1",
    "school-a1": "escuela-a1",
    "weather-a1": "clima-a1",
    "animals-a1": "animales-a1",
    "clothes-a1": "ropa-a1",
    "time-a1": "hora-a1",
    "city-a1": "ciudad-a1",
    "daily-a1": "rutina-a1",
    "travel-a2": "viaje-a2",
    "shopping-a2": "compras-a2",
    "health-a2": "salud-a2",
    "restaurant-a2": "restaurante-a2",
    "hobbies-a2": "pasatiempos-a2",
    "work-a2": "trabajo-a2",
    "directions-a2": "direcciones-a2",
    "housing-a2": "vivienda-a2",
    "phone-a2": "telefono-a2",
    "celebrations-a2": "celebraciones-a2",
    "environment-b1": "medioambiente-b1",
    "education-b1": "estudios-b1",
    "relationships-b1": "relaciones-b1",
    "money-b1": "dinero-b1",
    "technology-b1": "tecnologia-b1",
    "news-b1": "noticias-b1",
    "culture-b1": "cultura-b1",
    "opinions-b1": "opiniones-b1",
    "nature-b1": "naturaleza-b1",
    "admin-b1": "tramites-b1",
    "workplace-b2": "lugar-trabajo-b2",
    "media-b2": "medios-b2",
    "politics-b2": "politica-b2",
    "science-b2": "ciencias-b2",
    "economy-b2": "economia-b2",
    "law-b2": "derecho-b2",
    "climate-b2": "clima-energia-b2",
    "psychology-b2": "psicologia-b2",
    "arts-b2": "artes-b2",
    "debate-b2": "argumentacion-b2",
    "academic-c1": "academico-c1",
    "diplomacy-c1": "diplomacia-c1",
    "philosophy-c1": "filosofia-c1",
    "sustainability-c1": "sostenibilidad-c1",
    "ethics-c1": "etica-c1",
    "innovation-c1": "innovacion-c1",
    "society-c1": "sociedad-c1",
    "contemporary-arts-c1": "artes-contemporaneas-c1",
    "linguistics-c1": "linguistica-c1",
    "journalism-c1": "periodismo-c1",
    "rhetoric-c2": "retorica-c2",
    "literary-c2": "literario-c2",
    "geopolitics-c2": "geopolitica-c2",
    "epistemology-c2": "epistemologia-c2",
    "satire-c2": "satira-c2",
    "identity-c2": "identidad-c2",
    "aesthetics-c2": "estetica-c2",
    "rights-c2": "derechos-c2",
    "science-c2": "ciencia-c2",
    "register-c2": "registros-c2",
}

# Override weak FR title.es / description.es for home
TITLE_OVERRIDES = {
    "casa-a1": {
        "fr": "Maison A1 (ES)",
        "en": "Home A1 (ES)",
        "es": "Casa A1",
        "ru": "Дом А1 (ES)",
    },
}

DESC_SUFFIX = {
    "fr": " — pack espagnol.",
    "en": " — Spanish pack.",
    "es": " para estudiar español.",
    "ru": " — испанский пакет.",
}

# Feminine nouns that don't end in -a
FEM_EXCEPTIONS = {
    "leche", "sal", "miel", "luz", "voz", "flor", "noche", "tarde", "mañana",
    "clase", "gente", "ciudad", "salud", "sed", "hambre", "nieve", "lluvia",
    "piel", "mano", "foto", "moto", "radio", "crisis", "tesis", "sintaxis",
    "nación", "estación", "canción", "lección", "opción", "región", "religión",
    "acción", "dirección", "estación", "habitación", "información", "reunión",
    "universidad", "libertad", "verdad", "amistad", "edad", "ciudad", "comunidad",
    "sociedad", "oportunidad", "realidad", "actividad", "identidad", "autoridad",
    "mujer", "madre", "hermana", "hija", "tía", "abuela", "esposa", "novia",
    "carne", "nube", "sangre", "fiebre", "tos", "cárcel", "nave", "nave",
    "calle", "fuente", "puente",  # puente is masc actually
    "cuenta", "fruta", "casa", "mesa", "silla", "cama", "cocina", "puerta",
    "ventana", "escuela", "familia", "ropa", "hora", "semana", "fiesta",
    "pregunta", "respuesta", "tarea", "nota", "bolsa", "tienda", "oficina",
    "empresa", "noticia", "cultura", "naturaleza", "tecnología", "economía",
    "política", "justicia", "ciencia", "filosofía", "ética", "estética",
    "retórica", "ironía", "sátira", "geopolítica", "epistemología",
}
MASC_EXCEPTIONS = {
    "día", "mapa", "problema", "sistema", "tema", "programa", "clima",
    "idioma", "planeta", "drama", "poema", "telegrama", "esquema",
    "pan", "café", "té", "arroz", "pollo", "queso", "jugo", "agua",  # el agua
    "hombre", "padre", "hermano", "hijo", "tío", "abuelo", "esposo", "novio",
    "tren", "avión", "hotel", "parque", "trabajo", "dinero", "gobierno",
    "arte",  # el arte
    "puente", "coche", "viaje", "país", "color", "dolor", "amor", "favor",
    "profesor", "doctor", "motor", "sector", "factor",
}

cache: dict[str, str] = {}
if CACHE_PATH.exists():
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))

translators = {
    ("fr", "es"): GoogleTranslator(source="fr", target="es"),
    ("fr", "en"): GoogleTranslator(source="fr", target="en"),
    ("en", "es"): GoogleTranslator(source="en", target="es"),
    ("en", "ru"): GoogleTranslator(source="en", target="ru"),
    ("es", "ru"): GoogleTranslator(source="es", target="ru"),
    ("es", "en"): GoogleTranslator(source="es", target="en"),
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


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def clean_lemma(gloss_es: str, gloss_en: str = "") -> str:
    """Pick a single Spanish headword from gloss.es (may contain alternatives)."""
    raw = (gloss_es or "").strip()
    if not raw:
        raw = tr(gloss_en, "en", "es") if gloss_en else ""
    # take first alternative
    raw = re.split(r"\s*/\s*|\s*;\s*|\s*\(|,", raw)[0].strip()
    # drop leading articles
    raw = re.sub(r"^(el|la|los|las|un|una)\s+", "", raw, flags=re.I)
    # drop trailing punctuation
    raw = raw.strip(" .;:")
    # prefer lowercase for common nouns unless acronym
    if raw.isupper() and len(raw) <= 4:
        return raw
    return raw[:1].lower() + raw[1:] if raw else raw


def guess_article(lemma: str) -> str:
    w = lemma.strip().lower()
    if not w:
        return "el"
    if w in FEM_EXCEPTIONS:
        return "la"
    if w in MASC_EXCEPTIONS:
        return "el"
    # agua/alma etc. → el
    if w in {"agua", "alma", "aula", "águila", "área", "arma"}:
        return "el"
    if w.endswith(("ción", "sión", "dad", "tad", "tud", "umbre", "ie", "a")):
        return "la"
    if w.endswith(("ma", "pa", "ta")) and strip_accents(w).endswith(("ma", "pa", "ta")):
        # many -ma from Greek are masculine
        if strip_accents(w).endswith("ma"):
            return "el"
    return "el"


def spanish_ipa(word: str) -> str:
    """Rough Castilian-oriented IPA for study packs (good enough for TTS hints)."""
    w = word.lower().strip()
    if not w:
        return ""
    # multi-char first
    reps = [
        ("ch", "tʃ"), ("ll", "ʎ"), ("rr", "r"), ("qu", "k"), ("gu", "ɡ"),
        ("gü", "ɡw"), ("ñ", "ɲ"), ("ce", "θe"), ("ci", "θi"), ("za", "θa"),
        ("zo", "θo"), ("zu", "θu"), ("ge", "xe"), ("gi", "xi"), ("j", "x"),
        ("v", "b"), ("y", "ʝ"), ("h", ""), ("á", "ˈa"), ("é", "ˈe"),
        ("í", "ˈi"), ("ó", "ˈo"), ("ú", "ˈu"), ("ü", "w"),
    ]
    out = w
    for a, b in reps:
        out = out.replace(a, b)
    # simple syllable stress if no accent marked: penultimate if ends vowel/n/s else last
    if "ˈ" not in out:
        letters = list(out)
        # naive: mark first vowel of last or penultimate syllable
        vowels = [i for i, c in enumerate(letters) if c in "aeiou"]
        if vowels:
            ends_light = w[-1] in "aeiounsáéíóú"
            idx = vowels[-2] if ends_light and len(vowels) >= 2 else vowels[-1]
            letters[idx] = "ˈ" + letters[idx]
            out = "".join(letters)
    # insert dots between rough syllables (optional light touch)
    out = re.sub(r"([aeiou])([^aeiouˈ\s])([aeiou])", r"\1.\2\3", out)
    return out


def phrase_ipa(sentence: str) -> str:
    words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", sentence)
    return " ".join(spanish_ipa(w) for w in words[:12])


def scramble_words(sentence: str) -> list[str]:
    parts = sentence.strip().split()
    if not parts:
        return []
    # keep final punctuation attached to last token
    return parts


GRAMMAR_BY_LEVEL: dict[str, list[dict]] = {
    "a1": [
        {
            "title": {
                "fr": "Articles définis (el / la)",
                "en": "Definite articles (el / la)",
                "es": "Artículos definidos (el / la)",
                "ru": "Определённые артикли (el / la)",
            },
            "rule": {
                "fr": "el + masculin ; la + féminin.",
                "en": "el + masculine; la + feminine.",
                "es": "el + masculino; la + femenino.",
                "ru": "el + мужской род; la + женский род.",
            },
            "why": {
                "en": "Helps you name nouns correctly.",
                "es": "Ayuda a nombrar sustantivos correctamente.",
                "ru": "Помогает правильно называть существительные.",
            },
            "kind": "article",
        },
        {
            "title": {
                "fr": "Hay + sustantivo",
                "en": "Hay + noun",
                "es": "Hay + sustantivo",
                "ru": "Hay + существительное",
            },
            "rule": {
                "fr": "Hay introduit ce qui existe : Hay un / una + nom.",
                "en": "Hay introduces what exists: Hay un / una + noun.",
                "es": "Hay presenta lo que existe: Hay un / una + sustantivo.",
                "ru": "Hay вводит то, что есть: Hay un / una + существительное.",
            },
            "why": {
                "en": "Useful to say what is there.",
                "es": "Útil para decir lo que hay.",
                "ru": "Полезно, чтобы сказать, что есть.",
            },
            "kind": "hay",
        },
    ],
    "a2": [
        {
            "title": {
                "fr": "Pretérito vs imperfecto",
                "en": "Preterite vs imperfect",
                "es": "Pretérito frente a imperfecto",
                "ru": "Pretérito и imperfecto",
            },
            "rule": {
                "fr": "Le prétérito raconte un fait achevé ; l’imperfecto décrit le cadre ou l’habitude.",
                "en": "Preterite narrates a completed event; imperfect sets the scene or habit.",
                "es": "El pretérito narra un hecho terminado; el imperfecto describe el marco o la costumbre.",
                "ru": "Pretérito — завершённое событие; imperfecto — фон или привычка.",
            },
            "why": {
                "en": "Choosing the right past tense clarifies your story.",
                "es": "Elegir el pasado correcto aclara tu relato.",
                "ru": "Правильный выбор прошедшего делает рассказ яснее.",
            },
            "kind": "past",
        },
        {
            "title": {
                "fr": "Por / para",
                "en": "Por / para",
                "es": "Por / para",
                "ru": "Por / para",
            },
            "rule": {
                "fr": "Para indique le but ou la destination ; por la cause, la durée ou le moyen.",
                "en": "Para marks purpose or destination; por marks cause, duration, or means.",
                "es": "Para indica propósito o destino; por indica causa, duración o medio.",
                "ru": "Para — цель или направление; por — причина, длительность или средство.",
            },
            "why": {
                "en": "Avoids a very common mix-up.",
                "es": "Evita una confusión muy frecuente.",
                "ru": "Помогает избежать частой ошибки.",
            },
            "kind": "porpara",
        },
    ],
    "b1": [
        {
            "title": {
                "fr": "Subjonctif présent après querer que",
                "en": "Present subjunctive after querer que",
                "es": "Subjuntivo presente tras querer que",
                "ru": "Subjuntivo после querer que",
            },
            "rule": {
                "fr": "Après querer / esperar / es importante que, utilisez le subjonctif présent.",
                "en": "After querer / esperar / es importante que, use the present subjunctive.",
                "es": "Tras querer / esperar / es importante que, usa el subjuntivo presente.",
                "ru": "После querer / esperar / es importante que — presente de subjuntivo.",
            },
            "why": {
                "en": "Expresses wishes and necessity about someone else.",
                "es": "Expresa deseos y necesidad sobre otra persona.",
                "ru": "Выражает желание или необходимость в отношении другого.",
            },
            "kind": "subj",
        },
        {
            "title": {
                "fr": "Se impersonal",
                "en": "Impersonal se",
                "es": "Se impersonal",
                "ru": "Безличный se",
            },
            "rule": {
                "fr": "Se + 3e personne exprime une généralité : Se habla español.",
                "en": "Se + 3rd person expresses a general rule: Se habla español.",
                "es": "Se + 3.ª persona expresa una generalidad: Se habla español.",
                "ru": "Se + 3-е лицо выражает общее правило: Se habla español.",
            },
            "why": {
                "en": "Sounds natural in advice and public notices.",
                "es": "Suena natural en consejos y avisos.",
                "ru": "Звучит естественно в советах и объявлениях.",
            },
            "kind": "se",
        },
    ],
    "b2": [
        {
            "title": {
                "fr": "Subjonctif imparfait en hypothèse",
                "en": "Imperfect subjunctive in hypotheses",
                "es": "Imperfecto de subjuntivo en hipótesis",
                "ru": "Imperfecto de subjuntivo в гипотезах",
            },
            "rule": {
                "fr": "Si + imperfecto de subjuntivo, condicional : Si tuviera tiempo, iría.",
                "en": "Si + imperfect subjunctive, conditional: Si tuviera tiempo, iría.",
                "es": "Si + imperfecto de subjuntivo, condicional: Si tuviera tiempo, iría.",
                "ru": "Si + imperfecto de subjuntivo, condicional: Si tuviera tiempo, iría.",
            },
            "why": {
                "en": "Lets you discuss unlikely or polite scenarios.",
                "es": "Permite hablar de escenarios poco reales o corteses.",
                "ru": "Позволяет обсуждать маловероятные или вежливые сценарии.",
            },
            "kind": "hyp",
        },
        {
            "title": {
                "fr": "Aunque + indicatif / subjonctif",
                "en": "Aunque + indicative / subjunctive",
                "es": "Aunque + indicativo / subjuntivo",
                "ru": "Aunque + indicativo / subjuntivo",
            },
            "rule": {
                "fr": "Aunque + indicatif = fait connu ; aunque + subjonctif = concession non assertive.",
                "en": "Aunque + indicative = known fact; + subjunctive = non-assertive concession.",
                "es": "Aunque + indicativo = hecho conocido; + subjuntivo = concesión no asertiva.",
                "ru": "Aunque + indicativo — известный факт; + subjuntivo — уступка без утверждения.",
            },
            "why": {
                "en": "Nuances how strongly you commit to a claim.",
                "es": "Matiza cuánto te comprometes con una afirmación.",
                "ru": "Оттенки того, насколько вы настаиваете на утверждении.",
            },
            "kind": "aunque",
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
                "fr": "Préférez un nom abstrait à une proposition : la revisión del marco, no revisar el marco.",
                "en": "Prefer an abstract noun to a clause: la revisión del marco, not revisar el marco.",
                "es": "Prefiere un sustantivo abstracto a una oración: la revisión del marco, no revisar el marco.",
                "ru": "Предпочитайте абстрактное существительное: la revisión del marco.",
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
                "fr": "Conectores de matización",
                "en": "Hedging connectors",
                "es": "Conectores de matización",
                "ru": "Смягчающие связки",
            },
            "rule": {
                "fr": "No obstante, si bien, en la medida en que permettent de nuancer une thèse.",
                "en": "No obstante, si bien, en la medida en que help you hedge a claim.",
                "es": "No obstante, si bien, en la medida en que permiten matizar una tesis.",
                "ru": "No obstante, si bien, en la medida en que смягчают утверждение.",
            },
            "why": {
                "en": "Signals careful, expert stance.",
                "es": "Señala una postura cuidadosa y experta.",
                "ru": "Показывает осторожную экспертную позицию.",
            },
            "kind": "hedge",
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
                "fr": "Alternez léxico culto y léxico marcado (ironía, eufemismo) según el género discursivo.",
                "en": "Switch between learned and marked lexicon (irony, euphemism) by discourse genre.",
                "es": "Alterna léxico culto y léxico marcado (ironía, eufemismo) según el género discursivo.",
                "ru": "Чередуйте книжную и маркированную лексику в зависимости от жанра.",
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
                "fr": "Concessives complexes",
                "en": "Complex concessives",
                "es": "Concesivas complejas",
                "ru": "Сложные уступительные конструкции",
            },
            "rule": {
                "fr": "Por más que / si bien / aun cuando + subjuntivo intensifican la concesión.",
                "en": "Por más que / si bien / aun cuando + subjunctive intensify concession.",
                "es": "Por más que / si bien / aun cuando + subjuntivo intensifican la concesión.",
                "ru": "Por más que / si bien / aun cuando + subjuntivo усиливают уступку.",
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


def build_grammar(level: str, es_id: str, seeds: list[dict]) -> list[dict]:
    templates = GRAMMAR_BY_LEVEL.get(level, GRAMMAR_BY_LEVEL["a1"])
    nouns = [s for s in seeds if s.get("article")]
    if len(nouns) < 4:
        nouns = seeds
    out = []
    for i, tmpl in enumerate(templates, start=1):
        a = nouns[i % len(nouns)]
        b = nouns[(i + 3) % len(nouns)]
        c = nouns[(i + 5) % len(nouns)]
        art_a, lem_a = a.get("article", "el"), a["l2"]
        art_b, lem_b = b.get("article", "el"), b["l2"]
        kind = tmpl["kind"]
        table = [["Forma", "Uso", "Ejemplo"]]
        questions = []
        if kind == "article":
            table += [
                ["el", "masculino", f"el {lem_a}" if art_a == "el" else f"el {lem_b}"],
                ["la", "femenino", f"la {lem_a}" if art_a == "la" else f"la {lem_b}"],
            ]
            questions = [
                {
                    "id": f"remote-{es_id}-gq-{i}-1",
                    "prompt": f"Completa: ___ {lem_a}.",
                    "answer": art_a,
                    "options": ["el", "la", "los"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-2",
                    "prompt": f"Completa: ___ {lem_b}.",
                    "answer": art_b,
                    "options": ["el", "la", "las"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-3",
                    "prompt": f"¿{art_a.capitalize()} o la? → {lem_a}",
                    "answer": art_a,
                    "options": [art_a, "la" if art_a == "el" else "el", "los"],
                },
            ]
        elif kind == "hay":
            ind = "un" if art_a == "el" else "una"
            table += [
                ["Hay", "existencia", f"Hay {ind} {lem_a}."],
                ["No hay", "negación", f"No hay {lem_b}."],
            ]
            questions = [
                {
                    "id": f"remote-{es_id}-gq-{i}-1",
                    "prompt": f"Completa: ___ {ind} {lem_a}.",
                    "answer": "Hay",
                    "options": ["Hay", "Es", "Está"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-2",
                    "prompt": f"Completa: No ___ {lem_b}.",
                    "answer": "hay",
                    "options": ["hay", "es", "está"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-3",
                    "prompt": f"Elige: Hay ___ {lem_a}.",
                    "answer": ind,
                    "options": [ind, "el", "la"],
                },
            ]
        elif kind == "past":
            table += [
                ["Pretérito", "hecho terminado", f"Ayer vi {art_a} {lem_a}."],
                ["Imperfecto", "costumbre / marco", f"Siempre había {lem_b}."],
            ]
            questions = [
                {
                    "id": f"remote-{es_id}-gq-{i}-1",
                    "prompt": "Ayer ___ al médico. (ir)",
                    "answer": "fui",
                    "options": ["fui", "iba", "iré"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-2",
                    "prompt": "De niño, ___ mucho. (leer)",
                    "answer": "leía",
                    "options": ["leí", "leía", "leeré"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-3",
                    "prompt": f"El año pasado ___ {art_a} {lem_a}. (comprar)",
                    "answer": "compré",
                    "options": ["compré", "compraba", "compro"],
                },
            ]
        elif kind == "porpara":
            table += [
                ["para", "objetivo / destino", f"Esto es para {lem_a}."],
                ["por", "causa / medio", f"Lo hago por {lem_b}."],
            ]
            questions = [
                {
                    "id": f"remote-{es_id}-gq-{i}-1",
                    "prompt": f"Estudio ___ {lem_a}. (objetivo)",
                    "answer": "para",
                    "options": ["para", "por", "con"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-2",
                    "prompt": "Gracias ___ tu ayuda.",
                    "answer": "por",
                    "options": ["por", "para", "de"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-3",
                    "prompt": "Salgo ___ Madrid mañana.",
                    "answer": "para",
                    "options": ["para", "por", "en"],
                },
            ]
        elif kind == "subj":
            table += [
                ["quiero que", "+ subjuntivo", f"Quiero que haya {lem_a}."],
                ["es importante que", "+ subjuntivo", f"Es importante que exista {lem_b}."],
            ]
            questions = [
                {
                    "id": f"remote-{es_id}-gq-{i}-1",
                    "prompt": "Quiero que tú ___ (venir).",
                    "answer": "vengas",
                    "options": ["vengas", "vienes", "vendrás"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-2",
                    "prompt": "Es importante que ___ (haber) consenso.",
                    "answer": "haya",
                    "options": ["haya", "hay", "habrá"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-3",
                    "prompt": "Espero que ___ (ser) posible.",
                    "answer": "sea",
                    "options": ["sea", "es", "será"],
                },
            ]
        elif kind == "se":
            table += [
                ["Se + 3ª", "generalidad", f"Se necesita {lem_a}."],
                ["Se + 3ª", "aviso", f"Se habla de {lem_b}."],
            ]
            questions = [
                {
                    "id": f"remote-{es_id}-gq-{i}-1",
                    "prompt": f"___ habla de {lem_a}.",
                    "answer": "Se",
                    "options": ["Se", "Lo", "Le"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-2",
                    "prompt": f"___ recomienda {lem_b}.",
                    "answer": "Se",
                    "options": ["Se", "Me", "Te"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-3",
                    "prompt": "En España ___ español.",
                    "answer": "se habla",
                    "options": ["se habla", "habla se", "hablan se"],
                },
            ]
        elif kind == "hyp":
            table += [
                ["Si + subj. impf.", "hipótesis", "Si tuviera tiempo, iría."],
                ["condicional", "resultado", f"Compraría {art_a} {lem_a}."],
            ]
            questions = [
                {
                    "id": f"remote-{es_id}-gq-{i}-1",
                    "prompt": "Si ___ tiempo, viajaría. (tener)",
                    "answer": "tuviera",
                    "options": ["tuviera", "tengo", "tendré"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-2",
                    "prompt": "Si pudiera, ___ más. (leer)",
                    "answer": "leería",
                    "options": ["leería", "leo", "leí"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-3",
                    "prompt": f"Si hubiera {lem_b}, sería distinto.",
                    "answer": "hubiera",
                    "options": ["hubiera", "hay", "había"],
                },
            ]
        elif kind == "aunque":
            table += [
                ["aunque + ind.", "hecho conocido", f"Aunque hay {lem_a}, sigo."],
                ["aunque + subj.", "no asertivo", f"Aunque haya {lem_b}, dudo."],
            ]
            questions = [
                {
                    "id": f"remote-{es_id}-gq-{i}-1",
                    "prompt": "Aunque ___ frío, salgo. (hecho)",
                    "answer": "hace",
                    "options": ["hace", "haga", "hará"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-2",
                    "prompt": "Aunque ___ problemas, intentaré. (no seguro)",
                    "answer": "haya",
                    "options": ["haya", "hay", "habrá"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-3",
                    "prompt": f"Aunque exista {lem_a}, no basta.",
                    "answer": "exista",
                    "options": ["exista", "existe", "existirá"],
                },
            ]
        elif kind == "nom":
            table += [
                ["verbo → nombre", "estilo formal", f"la presencia de {lem_a}"],
                ["evitar cláusula", "densidad", f"la ausencia de {lem_b}"],
            ]
            questions = [
                {
                    "id": f"remote-{es_id}-gq-{i}-1",
                    "prompt": "Prefiere: la ___ del marco. (revisar)",
                    "answer": "revisión",
                    "options": ["revisión", "revisar", "revisado"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-2",
                    "prompt": f"La consideración de {lem_a} es central.",
                    "answer": "consideración",
                    "options": ["consideración", "considerar", "considera"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-3",
                    "prompt": "Mejor: el análisis, no ___.",
                    "answer": "analizar",
                    "options": ["analizar", "análisis", "analítico"],
                },
            ]
        elif kind == "hedge":
            table += [
                ["no obstante", "matización", "No obstante, matizo la tesis."],
                ["si bien", "concesión culta", f"Si bien hay {lem_a}, persiste la duda."],
            ]
            questions = [
                {
                    "id": f"remote-{es_id}-gq-{i}-1",
                    "prompt": "___ , la evidencia es parcial.",
                    "answer": "No obstante",
                    "options": ["No obstante", "Porque", "Entonces"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-2",
                    "prompt": "___ el método es sólido, la muestra es corta.",
                    "answer": "Si bien",
                    "options": ["Si bien", "Porque", "Cuando"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-3",
                    "prompt": "En la medida en ___ sea posible.",
                    "answer": "que",
                    "options": ["que", "cual", "quien"],
                },
            ]
        elif kind == "register":
            table += [
                ["culto", "formal", f"contemplar {art_a} {lem_a}"],
                ["marcado", "ironia / eufemismo", f"lo de {lem_b}"],
            ]
            questions = [
                {
                    "id": f"remote-{es_id}-gq-{i}-1",
                    "prompt": "Registro culto: ___ (no 'mirar').",
                    "answer": "contemplar",
                    "options": ["contemplar", "mirar", "ver"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-2",
                    "prompt": "El eufemismo suaviza el ___.",
                    "answer": "tono",
                    "options": ["tono", "sujeto", "verbo"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-3",
                    "prompt": f"Matiz culto para hablar de {lem_a}.",
                    "answer": "discurso",
                    "options": ["discurso", "chisme", "rollo"],
                },
            ]
        else:  # conc
            table += [
                ["por más que", "+ subj.", "Por más que insista, dudo."],
                ["aun cuando", "+ subj.", f"Aun cuando exista {lem_a}, matizo."],
            ]
            questions = [
                {
                    "id": f"remote-{es_id}-gq-{i}-1",
                    "prompt": "Por más que ___, no convence. (insistir)",
                    "answer": "insista",
                    "options": ["insista", "insiste", "insistirá"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-2",
                    "prompt": "Aun cuando ___, matizo. (ser)",
                    "answer": "sea",
                    "options": ["sea", "es", "será"],
                },
                {
                    "id": f"remote-{es_id}-gq-{i}-3",
                    "prompt": "Si bien ___, concedo el punto. (discrepar)",
                    "answer": "discrepo",
                    "options": ["discrepo", "discrepe", "discreparé"],
                },
            ]
        # pad to ~5 questions like FR packs
        while len(questions) < 5:
            n = len(questions) + 1
            questions.append(
                {
                    "id": f"remote-{es_id}-gq-{i}-{n}",
                    "prompt": f"Relaciona con el tema: {lem_a} / {lem_b}. ¿Artículo de «{lem_a}»?",
                    "answer": art_a,
                    "options": [art_a, art_b if art_b != art_a else ("la" if art_a == "el" else "el"), "los"],
                }
            )
        out.append(
            {
                "id": f"remote-{es_id}-grammar-{i}",
                "title": tmpl["title"],
                "rule": tmpl["rule"],
                "why": tmpl["why"],
                "table": table,
                "questions": questions[:5],
            }
        )
    return out


def translate_sentence_fr_es(fr: str) -> str:
    return tr(fr, "fr", "es")


def en_gloss_map(en: str) -> dict:
    en = (en or "").strip()
    es = tr(en, "en", "es") if en else ""
    ru = tr(en, "en", "ru") if en else ""
    return {"en": en, "es": es, "ru": ru}


def build_pack(fr: dict) -> dict:
    fr_id = fr["id"]
    es_id = FR_TO_ES_ID[fr_id]
    level = fr["level"]

    title = {
        "fr": f"{fr['title'].get('fr', fr_id)} (ES)",
        "en": f"{fr['title'].get('en', fr_id)} (ES)",
        "es": fr["title"].get("es", es_id),
        "ru": f"{fr['title'].get('ru', fr_id)} (ES)",
    }
    if es_id in TITLE_OVERRIDES:
        title = TITLE_OVERRIDES[es_id]
    # fix home title.es
    if es_id == "casa-a1":
        title["es"] = "Casa A1"

    description = {}
    for loc in ("fr", "en", "es", "ru"):
        base = fr.get("description", {}).get(loc, "")
        # avoid double suffix if already Spanish-pack wording
        if loc == "es" and base:
            description[loc] = base if "español" in base.lower() else base.rstrip(".") + DESC_SUFFIX[loc]
        else:
            description[loc] = (base.rstrip(".") + DESC_SUFFIX[loc]) if base else DESC_SUFFIX[loc].strip(" —")

    seeds = []
    for i, card in enumerate(fr.get("seed") or [], start=1):
        en = card.get("en") or card.get("gloss", {}).get("en") or ""
        gloss_es = card.get("gloss", {}).get("es") or ""
        lemma = clean_lemma(gloss_es, en)
        if not lemma:
            lemma = translate_sentence_fr_es(card.get("fr") or card.get("l2") or "")
            lemma = clean_lemma(lemma, en)
        gloss = {
            "en": card.get("gloss", {}).get("en") or en,
            "es": lemma if "/" not in (gloss_es or "") else (gloss_es or lemma),
            "ru": card.get("gloss", {}).get("ru") or tr(en, "en", "ru"),
        }
        # keep learner gloss.es as meaning when it was multi-sense; headword is cleaned lemma
        if gloss_es:
            gloss["es"] = gloss_es
        example_fr = card.get("example") or ""
        example = translate_sentence_fr_es(example_fr) if example_fr else f"Ejemplo con {lemma}."
        article = guess_article(lemma)
        # preserve el agua etc.
        if lemma.lower() == "agua":
            article = "el"
        seeds.append(
            {
                "id": f"remote-{es_id}-{i}",
                "l2": lemma,
                "en": en,
                "gloss": gloss,
                "example": example,
                "ipa": spanish_ipa(lemma),
                "article": article,
            }
        )

    phrases = []
    for i, p in enumerate(fr.get("phrases") or [], start=1):
        src = p.get("fr") or p.get("l2") or ""
        l2 = translate_sentence_fr_es(src)
        en = p.get("en") or p.get("gloss", {}).get("en") or tr(l2, "es", "en")
        gloss = p.get("gloss") or {}
        phrases.append(
            {
                "id": f"remote-{es_id}-phrase-{i}",
                "l2": l2,
                "en": en,
                "gloss": {
                    "en": gloss.get("en") or en,
                    "es": gloss.get("es") or l2,
                    "ru": gloss.get("ru") or tr(en, "en", "ru"),
                },
                "ipa": phrase_ipa(l2),
            }
        )

    listen = []
    for i, item in enumerate(fr.get("listen") or [], start=1):
        src = item.get("fr") or item.get("l2") or ""
        l2 = translate_sentence_fr_es(src)
        en = item.get("en") or item.get("gloss", {}).get("en") or tr(l2, "es", "en")
        # map highlighted word via matching seed index when possible
        word_fr = item.get("word") or ""
        word = ""
        for s_fr, s_es in zip(fr.get("seed") or [], seeds):
            if (s_fr.get("fr") or s_fr.get("l2")) == word_fr:
                word = s_es["l2"]
                break
        if not word:
            word = clean_lemma(tr(word_fr, "fr", "es"), item.get("wordEn") or "")
        distractors_fr = item.get("distractors") or []
        distractors = []
        for d in distractors_fr:
            mapped = None
            for s_fr, s_es in zip(fr.get("seed") or [], seeds):
                if (s_fr.get("fr") or s_fr.get("l2")) == d:
                    mapped = s_es["l2"]
                    break
            distractors.append(mapped or clean_lemma(tr(d, "fr", "es")))
        # ensure distractors ≠ word
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
                "id": f"remote-{es_id}-listen-{i}",
                "l2": l2,
                "en": en,
                "gloss": {
                    "en": (item.get("gloss") or {}).get("en") or en,
                    "es": (item.get("gloss") or {}).get("es") or l2,
                    "ru": (item.get("gloss") or {}).get("ru") or tr(en, "en", "ru"),
                },
                "word": word,
                "wordEn": item.get("wordEn") or wg.get("en") or "",
                "wordGloss": {
                    "en": wg.get("en") or item.get("wordEn") or "",
                    "es": wg.get("es") or word,
                    "ru": wg.get("ru") or tr(item.get("wordEn") or word, "en", "ru"),
                },
                "wordIpa": spanish_ipa(word),
                "distractors": distractors,
            }
        )

    prompts = []
    for pr in fr.get("prompts") or []:
        prompts.append(translate_sentence_fr_es(pr))

    grammar = build_grammar(level, es_id, seeds)

    skills_in = fr.get("skills") or {}
    skills: dict = {}

    def map_skill_items(key: str, items: list) -> list:
        out = []
        for i, it in enumerate(items or [], start=1):
            # fren / signs are lemma drills
            if key in ("fren", "signs"):
                src = it.get("fr") or it.get("l2") or ""
                lemma = ""
                for s_fr, s_es in zip(fr.get("seed") or [], seeds):
                    if (s_fr.get("fr") or s_fr.get("l2")) == src:
                        lemma = s_es["l2"]
                        break
                if not lemma:
                    lemma = clean_lemma(tr(src, "fr", "es"), it.get("en") or "")
                entry = {
                    "id": f"remote-{es_id}-{key[:4]}-{i}",
                    "l2": lemma,
                    "en": it.get("en") or "",
                    "gloss": {
                        "en": (it.get("gloss") or {}).get("en") or it.get("en") or "",
                        "es": (it.get("gloss") or {}).get("es") or lemma,
                        "ru": (it.get("gloss") or {}).get("ru") or tr(it.get("en") or lemma, "en", "ru"),
                    },
                }
                if key == "signs" and it.get("hint"):
                    entry["hint"] = tr(it["hint"], "fr", "es") if it["hint"] else it.get("hint")
                    # hints sometimes English
                    if entry["hint"] == it.get("hint") and it.get("hint"):
                        try:
                            entry["hint"] = tr(it["hint"], "en", "es")
                        except Exception:  # noqa: BLE001
                            pass
                out.append(entry)
                continue

            src = it.get("fr") or it.get("l2") or ""
            l2 = translate_sentence_fr_es(src)
            en = it.get("en") or (it.get("gloss") or {}).get("en") or tr(l2, "es", "en")
            entry = {
                "id": f"remote-{es_id}-{key[:4]}-{i}",
                "l2": l2,
                "en": en,
                "gloss": {
                    "en": (it.get("gloss") or {}).get("en") or en,
                    "es": (it.get("gloss") or {}).get("es") or l2,
                    "ru": (it.get("gloss") or {}).get("ru") or tr(en, "en", "ru"),
                },
            }
            if key in ("dictation", "aloud") and (it.get("ipa") is not None or True):
                entry["ipa"] = phrase_ipa(l2)
            if key == "unscramble":
                entry["words"] = scramble_words(l2)
            out.append(entry)
        return out

    for key in ("dictation", "meaning", "fren", "aloud", "unscramble", "signs"):
        if key in skills_in and skills_in[key]:
            skills[key] = map_skill_items(key, skills_in[key])

    # Ensure minimum skill coverage matching FR depth expectations
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
                    "id": f"remote-{es_id}-dict-{len(skills['dictation'])+1}",
                    "l2": ex,
                    "en": s.get("en") or "",
                    "gloss": {"en": s.get("en") or "", "es": ex, "ru": s["gloss"].get("ru", "")},
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
                    "id": f"remote-{es_id}-mean-{len(skills['meaning'])+1}",
                    "l2": ex,
                    "en": s.get("en") or "",
                    "gloss": {"en": s.get("en") or "", "es": ex, "ru": s["gloss"].get("ru", "")},
                }
            )
    if len(skills.get("fren", [])) < 6 and seeds:
        skills["fren"] = [
            {
                "id": f"remote-{es_id}-fren-{i}",
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
                    "id": f"remote-{es_id}-aloud-{len(skills['aloud'])+1}",
                    "l2": ex,
                    "en": s.get("en") or "",
                    "gloss": {"en": s.get("en") or "", "es": ex, "ru": s["gloss"].get("ru", "")},
                    "ipa": phrase_ipa(ex),
                }
            )
    if len(skills.get("unscramble", [])) < 2 and seeds:
        skills["unscramble"] = []
        for i, s in enumerate(seeds[:2], start=1):
            skills["unscramble"].append(
                {
                    "id": f"remote-{es_id}-unsc-{i}",
                    "l2": s["example"],
                    "en": s.get("en") or "",
                    "gloss": {"en": s.get("en") or "", "es": s["example"], "ru": s["gloss"].get("ru", "")},
                    "words": scramble_words(s["example"]),
                }
            )

    # Pad phrases/listen/prompts to FR counts
    while len(phrases) < len(fr.get("phrases") or []) and seeds:
        s = seeds[len(phrases) % len(seeds)]
        phrases.append(
            {
                "id": f"remote-{es_id}-phrase-{len(phrases)+1}",
                "l2": s["example"],
                "en": s.get("en") or "",
                "gloss": {"en": s.get("en") or "", "es": s["example"], "ru": s["gloss"].get("ru", "")},
                "ipa": phrase_ipa(s["example"]),
            }
        )
    while len(listen) < len(fr.get("listen") or []) and len(seeds) >= 4:
        idx = len(listen)
        s = seeds[idx % len(seeds)]
        distractors = [x["l2"] for x in seeds if x["l2"] != s["l2"]][:3]
        listen.append(
            {
                "id": f"remote-{es_id}-listen-{idx+1}",
                "l2": s["example"],
                "en": s.get("en") or "",
                "gloss": {"en": s.get("en") or "", "es": s["example"], "ru": s["gloss"].get("ru", "")},
                "word": s["l2"],
                "wordEn": s.get("en") or "",
                "wordGloss": s["gloss"],
                "wordIpa": s["ipa"],
                "distractors": distractors,
            }
        )
    while len(prompts) < max(4, len(fr.get("prompts") or [])):
        prompts.append(f"Escribe sobre «{seeds[len(prompts) % len(seeds)]['l2']}» en tres frases.")

    pack = {
        "pratiquePack": 2,
        "id": es_id,
        "version": 2 if es_id in {"comida-a1", "familia-a1", "casa-a1"} else 1,
        "level": level,
        "lang": "es",
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
            "lang": "es",
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
        if data["id"] not in FR_TO_ES_ID:
            print(f"skip unmapped {data['id']}")
            continue
        fr_packs.append(data)

    print(f"Generating {len(fr_packs)} Spanish packs…")
    built = []
    for i, fr in enumerate(fr_packs, start=1):
        es_id = FR_TO_ES_ID[fr["id"]]
        print(f"[{i}/{len(fr_packs)}] {fr['id']} → {es_id}")
        pack = build_pack(fr)
        built.append(pack)
        if not dry:
            out = ROOT / f"{es_id}.json"
            out.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            save_cache()
    if not dry:
        update_catalog(built)
        save_cache()
    print(f"Done: {len(built)} packs" + (" (dry-run)" if dry else ""))


if __name__ == "__main__":
    main()
