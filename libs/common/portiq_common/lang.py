"""Cheap language detection for uz / ru / ko / en."""

import re

LANGS = ("uz", "ru", "ko", "en")

_UZ_WORDS = {
    "men", "ish", "qidiryapman", "kerak", "salom", "qanday", "ishlash", "toshkent", "uchun",
    "bilan", "emas", "yaxshi", "rahmat", "qayerda", "mumkin", "dasturchi", "maosh", "suhbat",
    "ishga", "kompaniya", "haqida", "qilaman", "bo'lib", "o'zbekiston",
}


def detect_lang(text: str) -> str:
    if not text.strip():
        return "en"
    if re.search(r"[가-힣]", text):
        return "ko"
    cyr = len(re.findall(r"[Ѐ-ӿ]", text))
    if cyr and cyr / max(len(text), 1) > 0.2:
        # Letters only Uzbek Cyrillic has
        return "uz" if re.search(r"[ўқғҳЎҚҒҲ]", text) else "ru"
    if re.search(r"[oOgG][‘'ʻ`’]", text):
        return "uz"
    words = set(re.findall(r"[\w']+", text.lower()))
    if words & _UZ_WORDS:
        return "uz"
    return "en"
