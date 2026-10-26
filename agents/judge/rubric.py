"""Interview answer rubric (1-5 per axis) that works without an LLM.

Axes: knowledge, structure (STAR), clarity, company fit.
"""

import re
from typing import Any

from portiq_common.jobs import extract_skills

STAR = [
    r"\bwhen\b", r"\bsituation\b", r"\btask\b", r"\bi (did|built|led|made|fixed|decided)\b", r"\bresult", r"\bso\b",
    r"vaziyat", r"vazifa", r"\bqildim\b", r"natija", r"keyin", r"shuning uchun",
    r"ситуац", r"задач", r"я (сделал|сделала|решил|решила|построил)", r"результат", r"поэтому", r"в итоге",
    r"상황", r"과제", r"했습니다", r"결과", r"그래서", r"덕분에",
]
FILLERS = [r"\bum+\b", r"\buh+\b", r"\blike\b", r"\byou know\b", r"\bну\b", r"как бы", r"\bэ+\b",
           r"\banaqa\b", r"\bhaligi\b", r"\bmasalan masalan\b", r"\b음+\b", r"\b어+\b", r"그니까"]

FEEDBACK = {
    "knowledge": {
        "en": "Show more depth: name the tools you used and why you chose them.",
        "uz": "Chuqurroq ko‘rsating: qaysi vositalarni ishlatganingiz va nega tanlaganingizni ayting.",
        "ru": "Покажите глубину: назовите инструменты и почему вы их выбрали.",
        "ko": "더 깊이 보여 주세요: 사용한 도구와 선택한 이유를 말씀하세요.",
    },
    "structure": {
        "en": "Use STAR: Situation → Task → Action → Result, and end with a number.",
        "uz": "STAR tuzilmasidan foydalaning: Vaziyat → Vazifa → Harakat → Natija, oxirida raqam bilan.",
        "ru": "Используйте STAR: Ситуация → Задача → Действие → Результат, в конце — цифра.",
        "ko": "STAR 구조를 쓰세요: 상황 → 과제 → 행동 → 결과, 마지막에 숫자로 마무리하세요.",
    },
    "clarity": {
        "en": "Shorter sentences, fewer filler words. One idea per sentence.",
        "uz": "Qisqaroq gaplar, kamroq ortiqcha so‘zlar. Har gapda bitta fikr.",
        "ru": "Короче предложения, меньше слов-паразитов. Одна мысль — одно предложение.",
        "ko": "문장을 짧게, 군더더기 말은 줄이세요. 한 문장에 한 가지 생각만.",
    },
    "fit": {
        "en": "Connect your answer to this company: its product, news or goals.",
        "uz": "Javobingizni shu kompaniyaga bog‘lang: mahsuloti, yangiliklari yoki maqsadlari.",
        "ru": "Свяжите ответ с этой компанией: её продуктом, новостями или целями.",
        "ko": "답변을 이 회사의 제품, 뉴스, 목표와 연결하세요.",
    },
}

GOOD = {
    "en": "Strong answer. Keep this structure.",
    "uz": "Kuchli javob. Shu tuzilmani saqlang.",
    "ru": "Сильный ответ. Сохраняйте эту структуру.",
    "ko": "훌륭한 답변입니다. 이 구조를 유지하세요.",
}


def _clip(x: float) -> float:
    return round(max(1.0, min(5.0, x)) * 2) / 2


def score_answer(question: str, answer: str, lang: str = "en", company: str = "",
                 brief_terms: list[str] | None = None, category: str = "") -> dict[str, Any]:
    text = answer.strip()
    low = text.lower()
    words = re.findall(r"\w+", low)
    n = len(words)
    sentences = [s for s in re.split(r"[.!?。\n]+", text) if s.strip()]
    has_number = bool(re.search(r"\d", text))

    skills = extract_skills(text)
    q_words = {w for w in re.findall(r"\w{4,}", question.lower())}
    overlap = len(q_words & set(words))
    knowledge = 1.5 + min(2.0, len(skills) * 0.7) + min(1.0, overlap * 0.25) + (0.5 if n > 40 else 0)
    if n < 8:
        knowledge = min(knowledge, 1.5)

    star_hits = sum(1 for p in STAR if re.search(p, low))
    structure = 1.5 + min(2.5, star_hits * 0.6) + (1.0 if has_number else 0)
    if n < 15:
        structure = min(structure, 2.0)

    avg = n / max(len(sentences), 1)
    fillers = sum(len(re.findall(p, low)) for p in FILLERS)
    clarity = 4.5 - (1.0 if avg > 30 else 0) - (0.5 if avg < 4 else 0) - min(2.0, fillers * 0.5) - (1.5 if n < 6 else 0)

    terms = [t.lower() for t in (brief_terms or []) if len(t) > 3]
    fit_hits = (1 if company and company.split()[0].lower() in low else 0) + sum(1 for t in terms if t in low)
    fit = 2.0 + min(2.5, fit_hits * 1.0) + (0.5 if category in ("intro", "stress", "salary", "background") else 0)

    scores = {"knowledge": _clip(knowledge), "structure": _clip(structure), "clarity": _clip(clarity), "fit": _clip(fit)}
    total = round(sum(scores.values()) / 20 * 100)
    weakest = min(scores, key=scores.get)
    lang = lang if lang in GOOD else "en"
    feedback = GOOD[lang] if scores[weakest] >= 4 else FEEDBACK[weakest][lang]
    return {"scores": scores, "total": total, "weakest": weakest, "feedback": feedback,
            "signals": {"words": n, "skills": skills, "star_hits": star_hits, "fillers": fillers, "number": has_number}}
