"""Job helpers shared by the pipeline and the matcher: skills, salary, hashing."""

import hashlib
import re

# Canonical skill -> patterns (lowercase). Multilingual aliases where common.
SKILLS: dict[str, list[str]] = {
    "Python": ["python", "파이썬", "питон"],
    "Java": [r"\bjava\b", "자바"],
    "JavaScript": ["javascript", r"\bjs\b", "자바스크립트"],
    "TypeScript": ["typescript", r"\bts\b"],
    "React": ["react", "리액트"],
    "Next.js": ["next.js", "nextjs"],
    "Node.js": ["node.js", "nodejs", r"\bnode\b"],
    "Go": [r"\bgolang\b", r"\bgo\b(?= developer| engineer|,)"],
    "C++": [r"c\+\+"],
    "C#": [r"c#", r"\.net\b"],
    "PHP": [r"\bphp\b", "laravel"],
    "Kotlin": ["kotlin", "코틀린"],
    "Swift": [r"\bswift\b", r"\bios\b"],
    "Flutter": ["flutter", "dart"],
    "SQL": [r"\bsql\b", "postgres", "mysql", "oracle"],
    "NoSQL": ["mongodb", "nosql", "dynamodb"],
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Spring": ["spring"],
    "Docker": ["docker", "도커"],
    "Kubernetes": ["kubernetes", r"\bk8s\b"],
    "AWS": [r"\baws\b", "amazon web services"],
    "GCP": [r"\bgcp\b", "google cloud"],
    "Kafka": ["kafka", "카프카"],
    "Redis": ["redis"],
    "Git": [r"\bgit\b", "github", "gitlab"],
    "Linux": ["linux", "리눅스"],
    "Machine Learning": ["machine learning", r"\bml\b", "머신러닝", "машинн"],
    "Deep Learning": ["deep learning", "딥러닝", "pytorch", "tensorflow"],
    "LLM": [r"\bllm\b", "langchain", r"\brag\b", "generative ai", "genai"],
    "Data Analysis": ["data analy", "데이터 분석", "анализ данных", "pandas"],
    "Excel": ["excel", "엑셀"],
    "Power BI": ["power bi", "tableau"],
    "Statistics": ["statistic", "통계", "статистик"],
    "Figma": ["figma", "피그마"],
    "UX Research": ["ux research", "user research", "usability"],
    "UI Design": ["ui design", "ui/ux", "ux/ui", "product design"],
    "SEO": [r"\bseo\b"],
    "SMM": [r"\bsmm\b", "social media", "instagram", "tiktok"],
    "Content": ["content", "copywrit", "콘텐츠", "контент"],
    "Marketing Analytics": ["google analytics", "marketing analytics", r"\bga4\b"],
    "Sales": ["sales", "영업", "продаж"],
    "English": ["english", "영어", "английск", "ingliz"],
    "Korean": ["korean", "topik", "한국어", "корейск", "koreys"],
    "Russian": ["russian", "러시아어", "русск", "rus tili"],
    "Communication": ["communication", "커뮤니케이션", "коммуникаб"],
}

_COMPILED = {k: [re.compile(p) for p in v] for k, v in SKILLS.items()}


def extract_skills(text: str) -> list[str]:
    low = (text or "").lower()
    return [skill for skill, pats in _COMPILED.items() if any(p.search(low) for p in pats)]


# Role -> core skills, used by the matcher (gap) and the roadmap agent.
ROLE_SKILLS: dict[str, list[str]] = {
    "dev": ["Python", "SQL", "Git", "Docker", "FastAPI", "Linux", "AWS", "Kafka"],
    "frontend": ["JavaScript", "TypeScript", "React", "Next.js", "Git", "Figma"],
    "data": ["Python", "SQL", "Statistics", "Data Analysis", "Machine Learning", "Power BI", "Excel"],
    "ai": ["Python", "Machine Learning", "Deep Learning", "LLM", "Docker", "SQL"],
    "design": ["Figma", "UI Design", "UX Research", "Communication"],
    "marketing": ["SMM", "Content", "SEO", "Marketing Analytics", "English", "Communication"],
}

ROLE_WORDS: dict[str, list[str]] = {
    "dev": ["developer", "engineer", "backend", "dasturchi", "разработчик", "программист", "개발자", "백엔드", "devops"],
    "frontend": ["frontend", "front-end", "프론트", "фронтенд"],
    "data": ["data", "analyst", "analytics", "데이터", "аналитик", "tahlilchi"],
    "ai": [r"\bai\b", r"\bml\b", "machine learning", "인공지능", "llm"],
    "design": ["design", "ux", r"\bui\b", "디자이너", "дизайн", "dizayn"],
    "marketing": ["marketing", "smm", "growth", "마케팅", "маркет", "seo"],
}


def guess_role(text: str) -> str | None:
    low = (text or "").lower()
    order = ["frontend", "ai", "data", "design", "marketing", "dev"]
    for role in order:
        if any(re.search(p, low) for p in ROLE_WORDS[role]):
            return role
    return None


def role_from_skills(skills: list[str]) -> str | None:
    best = max(ROLE_SKILLS, key=lambda r: len(set(ROLE_SKILLS[r]) & set(skills)))
    return best if set(ROLE_SKILLS[best]) & set(skills) else None


_NUM = r"(\d+(?:[.,]\d+)?)\s*(k|m|mln|млн|million|만|천)?"


def _to_number(num: str, unit: str | None) -> float:
    n = float(num.replace(",", "."))
    unit = (unit or "").lower()
    if unit in ("k", "천"):
        n *= 1_000
    elif unit in ("m", "mln", "млн", "million"):
        n *= 1_000_000
    elif unit == "만":
        n *= 10_000
    return n


def parse_salary(text: str) -> dict:
    """'8-12 mln so'm' -> {min: 8e6, max: 12e6, currency: 'UZS'}. Best effort."""
    t = (text or "").lower().replace(" ", " ")
    cur = None
    if re.search(r"so[‘'ʻ`’]?m|сум|uzs", t):
        cur = "UZS"
    elif re.search(r"₩|krw|원|만원", t):
        cur = "KRW"
    elif re.search(r"\$|usd|dollar", t):
        cur = "USD"
    elif re.search(r"€|eur", t):
        cur = "EUR"
    elif re.search(r"₽|руб|rub", t):
        cur = "RUB"
    t2 = re.sub(r"(?<=\d)[ ,](?=\d{3}(?!\d))", "", t)  # 1 500 000 -> 1500000
    found = re.findall(_NUM, t2)
    # "12-18 mln": the unit is written once, on the second number of a range.
    found = [(n, u or (found[i + 1][1] if i + 1 < len(found) else "")) for i, (n, u) in enumerate(found)]
    nums = [_to_number(n, u) for n, u in found]
    nums = [n for n in nums if n >= 100]
    if not nums:
        return {"min": None, "max": None, "currency": cur}
    return {"min": min(nums[:2]), "max": max(nums[:2]), "currency": cur}


def job_hash(title: str, company: str | None, city: str | None) -> str:
    key = "|".join(re.sub(r"\W+", "", (x or "").lower()) for x in (title, company, city))
    return hashlib.sha1(key.encode()).hexdigest()
