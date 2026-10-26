"""CV text -> structured profile, without an LLM."""

import re
from typing import Any

from darvoza_common.jobs import extract_skills, guess_role, role_from_skills

EDU_WORDS = r"(universit|университет|대학교|college|institute|институт|bachelor|master|бакалавр|магистр|학사|석사|PhD|kollej)"
LANG_WORDS = {
    "English": r"english|ingliz|английск|영어|ielts|toefl",
    "Korean": r"korean|koreys|корейск|한국어|topik",
    "Russian": r"russian|rus tili|русск|러시아어",
    "Uzbek": r"uzbek|o[‘'ʻ`’]zbek|узбек|우즈베크",
}


def parse_cv(text: str) -> dict[str, Any]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = None
    for l in lines[:5]:
        if 2 <= len(l.split()) <= 4 and not re.search(r"[@\d:/]", l) and len(l) < 50:
            name = l
            break
    education = [l[:160] for l in lines if re.search(EDU_WORDS, l, re.I)][:4]
    years = [int(y) for y in re.findall(r"(\d{1,2})\+?\s*(?:years?|yil|лет|года|년)", text, re.I)]
    experience_years = max(years) if years else None
    languages = [lang for lang, pat in LANG_WORDS.items() if re.search(pat, text, re.I)]
    topik = re.search(r"topik\s*(?:level\s*)?(\d)", text, re.I)
    skills = extract_skills(text)
    return {
        "name": name,
        "skills": skills,
        "education": education,
        "experience_years": experience_years,
        "languages": languages,
        "korean_level": f"TOPIK {topik.group(1)}" if topik else None,
        "role_guess": guess_role(text) or role_from_skills(skills),
    }
