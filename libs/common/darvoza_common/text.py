import re

_SUFFIX = re.compile(r"\b(inc|corp|corporation|co|ltd|llc|llp|plc|group|holdings|gmbh|jsc|ooo|mchj|주식회사)\b\.?|\(주\)", re.I)


def name_tokens(company: str) -> list[str]:
    cleaned = _SUFFIX.sub(" ", company.lower())
    return [t for t in re.findall(r"\w+", cleaned) if len(t) >= 2]


def mentions(company: str, text: str) -> bool:
    """True if every meaningful word of the company name appears in the text."""
    tokens = name_tokens(company)
    low = (text or "").lower()
    return bool(tokens) and all(re.search(rf"(?<!\w){re.escape(t)}", low) for t in tokens)
