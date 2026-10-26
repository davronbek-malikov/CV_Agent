"""Gap -> weekly plan that fits the user's hours."""

import math
from typing import Any

from darvoza_common.jobs import ROLE_SKILLS, guess_role

# Free, official-first resources.
RESOURCES: dict[str, tuple[str, str]] = {
    "Python": ("Python tutorial (official)", "https://docs.python.org/3/tutorial/"),
    "SQL": ("SQLBolt interactive lessons", "https://sqlbolt.com/"),
    "Git": ("Learn Git Branching", "https://learngitbranching.js.org/"),
    "Docker": ("Docker: Get started", "https://docs.docker.com/get-started/"),
    "FastAPI": ("FastAPI tutorial", "https://fastapi.tiangolo.com/tutorial/"),
    "Linux": ("Linux Journey", "https://linuxjourney.com/"),
    "AWS": ("AWS Skill Builder", "https://aws.amazon.com/training/digital/"),
    "Kafka": ("Kafka quickstart", "https://kafka.apache.org/quickstart"),
    "Kubernetes": ("Kubernetes basics", "https://kubernetes.io/docs/tutorials/kubernetes-basics/"),
    "JavaScript": ("javascript.info", "https://javascript.info/"),
    "TypeScript": ("TypeScript handbook", "https://www.typescriptlang.org/docs/handbook/intro.html"),
    "React": ("react.dev Learn", "https://react.dev/learn"),
    "Next.js": ("Next.js Learn", "https://nextjs.org/learn"),
    "Statistics": ("Khan Academy statistics", "https://www.khanacademy.org/math/statistics-probability"),
    "Data Analysis": ("Kaggle Learn: pandas", "https://www.kaggle.com/learn/pandas"),
    "Machine Learning": ("Kaggle Learn: intro to ML", "https://www.kaggle.com/learn/intro-to-machine-learning"),
    "Deep Learning": ("fast.ai course", "https://course.fast.ai/"),
    "LLM": ("Hugging Face courses", "https://huggingface.co/learn"),
    "Power BI": ("Microsoft Learn: Power BI", "https://learn.microsoft.com/en-us/training/powerplatform/power-bi"),
    "Figma": ("Figma help center", "https://help.figma.com/"),
    "UI Design": ("Nielsen Norman Group articles", "https://www.nngroup.com/articles/"),
    "UX Research": ("Nielsen Norman Group articles", "https://www.nngroup.com/articles/"),
    "SEO": ("Google SEO starter guide", "https://developers.google.com/search/docs/fundamentals/seo-starter-guide"),
    "Marketing Analytics": ("Google Skillshop", "https://skillshop.withgoogle.com/"),
    "English": ("British Council LearnEnglish", "https://learnenglish.britishcouncil.org/"),
    "Korean": ("TOPIK official site", "https://www.topik.go.kr/"),
    "Redis": ("Redis learn", "https://redis.io/learn"),
}

HOURS = {"Python": 25, "SQL": 15, "Git": 6, "Docker": 10, "Linux": 10, "AWS": 15, "Kafka": 12, "Kubernetes": 15,
         "React": 20, "TypeScript": 12, "Machine Learning": 25, "Deep Learning": 30, "Korean": 40, "English": 30}

TEXT = {
    "learn": {"en": "Learn {skill}", "uz": "{skill} ni o‘rganing", "ru": "Изучите {skill}", "ko": "{skill} 학습"},
    "build": {"en": "Build a small project with {skills} and publish it on GitHub",
              "uz": "{skills} bilan kichik loyiha qurib, GitHub’ga joylang",
              "ru": "Сделайте небольшой проект на {skills} и опубликуйте на GitHub",
              "ko": "{skills}(으)로 작은 프로젝트를 만들어 GitHub에 공개"},
    "write": {"en": "Write a 1-page case study for your portfolio", "uz": "Portfolio uchun 1 sahifalik case study yozing",
              "ru": "Напишите кейс на 1 страницу для портфолио", "ko": "포트폴리오용 1페이지 케이스 스터디 작성"},
    "practice": {"en": "Practice 20 interview questions in Darvoza", "uz": "Darvozada 20 ta suhbat savolini mashq qiling",
                 "ru": "Потренируйте 20 вопросов интервью в Darvoza", "ko": "Darvoza에서 면접 질문 20개 연습"},
    "apply": {"en": "Apply to 5 matched jobs", "uz": "Mos 5 ta ishga ariza topshiring",
              "ru": "Откликнитесь на 5 подходящих вакансий", "ko": "추천 공고 5곳에 지원"},
    "block_learn": {"en": "Learn", "uz": "O‘rganish", "ru": "Изучение", "ko": "학습"},
    "block_build": {"en": "Build & prove", "uz": "Qurish va isbotlash", "ru": "Проект и портфолио", "ko": "프로젝트·포트폴리오"},
    "block_ready": {"en": "Get interview-ready", "uz": "Suhbatga tayyorlanish", "ru": "Подготовка к интервью", "ko": "면접 준비"},
}


def t(key: str, lang: str, **kw: Any) -> str:
    d = TEXT[key]
    return d.get(lang, d["en"]).format(**kw)


def role_of(target: str) -> str:
    return target if target in ROLE_SKILLS else (guess_role(target) or "dev")


def build_plan(target: str, days: int, hours_per_week: int, have: list[str], missing: list[str],
               lang: str) -> dict[str, Any]:
    role = role_of(target)
    weeks = max(3, math.ceil(days / 7))
    budget = weeks * hours_per_week
    gap = list(dict.fromkeys(missing + [s for s in ROLE_SKILLS[role] if s not in have]))

    # Reserve ~40% of time for building and interview practice.
    learn_budget = budget * 0.6
    learn: list[dict[str, Any]] = []
    used = 0.0
    for skill in gap:
        h = HOURS.get(skill, 10)
        if used + h > learn_budget:
            h = learn_budget - used
            if h < 3:
                break
        title, url = RESOURCES.get(skill, (None, None))
        learn.append({"text": t("learn", lang, skill=skill), "skill": skill, "hours": round(h),
                      "resource": {"title": title, "url": url} if url else None})
        used += h

    rest = budget - used
    build_h, ready_h = round(rest * 0.6), round(rest * 0.4)
    built_with = ", ".join([x["skill"] for x in learn[:3]] or ROLE_SKILLS[role][:3])
    learn_weeks = max(1, round(weeks * used / budget)) if budget else 1
    build_weeks = max(1, round(weeks * build_h / budget)) if budget else 1
    w1 = min(learn_weeks, weeks - 2)
    w2 = min(max(w1 + 1, w1 + build_weeks), weeks - 1)

    def span(a: int, b: int) -> str:
        return f"{a}" if a == b else f"{a}–{b}"

    blocks = [
        {"weeks": span(1, w1), "title": t("block_learn", lang), "tasks": learn},
        {"weeks": span(w1 + 1, w2), "title": t("block_build", lang), "tasks": [
            {"text": t("build", lang, skills=built_with), "hours": round(build_h * 0.75)},
            {"text": t("write", lang), "hours": build_h - round(build_h * 0.75)},
        ]},
        {"weeks": span(w2 + 1, weeks), "title": t("block_ready", lang), "tasks": [
            {"text": t("practice", lang), "hours": round(ready_h * 0.6)},
            {"text": t("apply", lang), "hours": ready_h - round(ready_h * 0.6)},
        ]},
    ]
    total = sum(task["hours"] for b in blocks for task in b["tasks"])
    return {"target": target, "role": role, "weeks": weeks, "hours_per_week": hours_per_week,
            "budget_hours": budget, "total_hours": total, "gap": gap, "blocks": blocks}
