"""Everything the orchestrator says, in uz / ru / ko / en."""

M: dict[str, dict[str, str]] = {
    "ask_lang": {
        "en": "Hi! I’m Portiq. First, choose your language.",
        "uz": "Salom! Men Portiqman. Avval tilni tanlang.",
        "ru": "Привет! Я Portiq. Сначала выберите язык.",
        "ko": "안녕하세요! Portiq입니다. 먼저 언어를 선택해 주세요.",
    },
    "ask_mode": {
        "en": "What do you need today?",
        "uz": "Bugun sizga nima kerak?",
        "ru": "Что вам нужно сегодня?",
        "ko": "오늘 무엇이 필요하신가요?",
    },
    "ask_scope": {
        "en": "Where do you want to find a job?",
        "uz": "Qayerdan ish qidirmoqchisiz?",
        "ru": "Где вы хотите найти работу?",
        "ko": "어디에서 일자리를 찾으시나요?",
    },
    "ask_role": {
        "en": "What kind of job?",
        "uz": "Qanday ish?",
        "ru": "Какая работа?",
        "ko": "어떤 직무인가요?",
    },
    "ask_salary": {
        "en": "What monthly salary do you want?",
        "uz": "Oyiga qancha maosh xohlaysiz?",
        "ru": "Какую зарплату в месяц вы хотите?",
        "ko": "희망 월급은 얼마인가요?",
    },
    "ask_visa": {
        "en": "Which visa do you have, or plan, for Korea?",
        "uz": "Koreya uchun qaysi vizangiz bor yoki rejalashtiryapsiz?",
        "ru": "Какая у вас виза для Кореи (или какую планируете)?",
        "ko": "한국 비자는 무엇인가요 (또는 계획 중인 비자)?",
    },
    "ask_company": {
        "en": "Which company is the interview for? Type the name.",
        "uz": "Suhbat qaysi kompaniyaga? Nomini yozing.",
        "ru": "Для какой компании интервью? Введите название.",
        "ko": "어느 회사 면접인가요? 회사 이름을 입력하세요.",
    },
    "ask_type": {
        "en": "What kind of interview?",
        "uz": "Qanday suhbat?",
        "ru": "Какое интервью?",
        "ko": "어떤 면접인가요?",
    },
    "ask_target": {
        "en": "What is your target job?",
        "uz": "Maqsadingizdagi ish qaysi?",
        "ru": "Какая работа — ваша цель?",
        "ko": "목표 직무는 무엇인가요?",
    },
    "ask_days": {
        "en": "How much time do you have?",
        "uz": "Qancha vaqtingiz bor?",
        "ru": "Сколько у вас времени?",
        "ko": "기간은 얼마나 있나요?",
    },
    "ask_hours": {
        "en": "How many hours per week can you study?",
        "uz": "Haftasiga necha soat o‘qiy olasiz?",
        "ru": "Сколько часов в неделю вы можете учиться?",
        "ko": "주당 몇 시간 공부할 수 있나요?",
    },
    "working_jobs": {
        "en": "Searching every source for you…",
        "uz": "Barcha manbalardan qidiryapman…",
        "ru": "Ищу по всем источникам…",
        "ko": "모든 출처에서 찾고 있습니다…",
    },
    "working_research": {
        "en": "Researching {company}…",
        "uz": "{company} haqida ma’lumot yig‘yapman…",
        "ru": "Изучаю {company}…",
        "ko": "{company}을(를) 분석하고 있습니다…",
    },
    "working_roadmap": {
        "en": "Building your plan…",
        "uz": "Rejangizni tuzyapman…",
        "ru": "Составляю ваш план…",
        "ko": "계획을 만들고 있습니다…",
    },
    "jobs_title": {
        "en": "Top matches for you",
        "uz": "Siz uchun eng mos ishlar",
        "ru": "Лучшие варианты для вас",
        "ko": "추천 일자리",
    },
    "no_jobs": {
        "en": "No jobs in this scope yet. Try “All countries” or another role.",
        "uz": "Bu hududda hozircha ish yo‘q. “Barcha davlatlar” yoki boshqa yo‘nalishni sinab ko‘ring.",
        "ru": "В этом регионе пока нет вакансий. Попробуйте «Все страны» или другую роль.",
        "ko": "이 범위에는 아직 공고가 없습니다. ‘모든 국가’나 다른 직무를 선택해 보세요.",
    },
    "no_sources": {
        "en": "I found no public sources for this company, so questions will be general.",
        "uz": "Bu kompaniya haqida ochiq manba topilmadi, savollar umumiy bo‘ladi.",
        "ru": "Открытых источников о компании нет, поэтому вопросы будут общими.",
        "ko": "이 회사에 대한 공개 자료가 없어 일반 질문으로 진행합니다.",
    },
    "follow_up": {
        "en": "Follow-up",
        "uz": "Qo‘shimcha savol",
        "ru": "Уточняющий вопрос",
        "ko": "꼬리 질문",
    },
    "report": {
        "en": "Interview finished. Here is your report.",
        "uz": "Suhbat tugadi. Mana hisobotingiz.",
        "ru": "Интервью завершено. Вот ваш отчёт.",
        "ko": "면접이 끝났습니다. 결과 리포트입니다.",
    },
    "failed": {
        "en": "Sorry, something went wrong on our side. Please try again.",
        "uz": "Kechirasiz, bizda xatolik yuz berdi. Qayta urinib ko‘ring.",
        "ru": "Извините, произошла ошибка. Попробуйте ещё раз.",
        "ko": "죄송합니다. 오류가 발생했습니다. 다시 시도해 주세요.",
    },
    "skip": {"en": "Skip", "uz": "O‘tkazish", "ru": "Пропустить", "ko": "건너뛰기"},
    "not_sure": {"en": "Not sure", "uz": "Bilmayman", "ru": "Не знаю", "ko": "잘 모르겠어요"},
    "end": {"en": "End interview", "uz": "Suhbatni tugatish", "ru": "Завершить интервью", "ko": "면접 종료"},
    "again": {"en": "Start again", "uz": "Qaytadan", "ru": "Начать заново", "ko": "다시 시작"},
    "to_roadmap": {
        "en": "Make a roadmap from weak spots",
        "uz": "Zaif joylardan yo‘l xaritasi",
        "ru": "План по слабым местам",
        "ko": "약점으로 로드맵 만들기",
    },
    "cv_saved": {
        "en": "CV read. I found: {skills}.",
        "uz": "Rezyume o‘qildi. Topilgan ko‘nikmalar: {skills}.",
        "ru": "Резюме прочитано. Найдены навыки: {skills}.",
        "ko": "이력서를 읽었습니다. 확인된 역량: {skills}.",
    },
}

CHIPS: dict[str, dict[str, dict[str, str]]] = {
    "mode": {
        "jobs": {"en": "Find jobs", "uz": "Ish topish", "ru": "Найти работу", "ko": "일자리 찾기"},
        "interview": {"en": "Interview practice", "uz": "Suhbat mashqi", "ru": "Тренировка интервью", "ko": "면접 연습"},
        "roadmap": {"en": "Career roadmap", "uz": "Yo‘l xaritasi", "ru": "План развития", "ko": "커리어 로드맵"},
    },
    "scope": {
        "uz": {"en": "Only Uzbekistan", "uz": "Faqat O‘zbekiston", "ru": "Только Узбекистан", "ko": "우즈베키스탄만"},
        "kr": {"en": "Only Korea", "uz": "Faqat Koreya", "ru": "Только Корея", "ko": "한국만"},
        "multi": {"en": "Uzbekistan + Korea", "uz": "O‘zbekiston + Koreya", "ru": "Узбекистан + Корея", "ko": "우즈베키스탄 + 한국"},
        "all": {"en": "All countries", "uz": "Barcha davlatlar", "ru": "Все страны", "ko": "모든 국가"},
        "remote": {"en": "Remote only", "uz": "Faqat masofaviy", "ru": "Только удалённо", "ko": "원격 근무만"},
    },
    "role": {
        "dev": {"en": "Backend / Developer", "uz": "Backend / Dasturchi", "ru": "Backend / Разработчик", "ko": "백엔드 / 개발자"},
        "frontend": {"en": "Frontend", "uz": "Frontend", "ru": "Фронтенд", "ko": "프론트엔드"},
        "data": {"en": "Data", "uz": "Data", "ru": "Данные", "ko": "데이터"},
        "ai": {"en": "AI / ML", "uz": "AI / ML", "ru": "AI / ML", "ko": "AI / ML"},
        "design": {"en": "Design", "uz": "Dizayn", "ru": "Дизайн", "ko": "디자인"},
        "marketing": {"en": "Marketing", "uz": "Marketing", "ru": "Маркетинг", "ko": "마케팅"},
    },
    "type": {
        "full": {"en": "Full (A to Z)", "uz": "To‘liq (A–Z)", "ru": "Полное (А–Я)", "ko": "전체 (A–Z)"},
        "tech": {"en": "Technical", "uz": "Texnik", "ru": "Техническое", "ko": "기술 면접"},
        "stress": {"en": "Stress test", "uz": "Stress-test", "ru": "Стресс-интервью", "ko": "압박 면접"},
        "salary": {"en": "Salary talk", "uz": "Maosh suhbati", "ru": "О зарплате", "ko": "연봉 협상"},
    },
    "days": {
        "30": {"en": "30 days", "uz": "30 kun", "ru": "30 дней", "ko": "30일"},
        "60": {"en": "60 days", "uz": "60 kun", "ru": "60 дней", "ko": "60일"},
        "90": {"en": "90 days", "uz": "90 kun", "ru": "90 дней", "ko": "90일"},
    },
    "hours": {
        "5": {"en": "5 h / week", "uz": "Haftasiga 5 soat", "ru": "5 ч в неделю", "ko": "주 5시간"},
        "10": {"en": "10 h / week", "uz": "Haftasiga 10 soat", "ru": "10 ч в неделю", "ko": "주 10시간"},
        "20": {"en": "20 h / week", "uz": "Haftasiga 20 soat", "ru": "20 ч в неделю", "ko": "주 20시간"},
    },
}

LANG_CHIPS = [
    {"value": "uz", "label": "O‘zbekcha"},
    {"value": "ru", "label": "Русский"},
    {"value": "ko", "label": "한국어"},
    {"value": "en", "label": "English"},
]

SALARY_CHIPS = {
    "UZS": ["6M so‘m", "10M so‘m", "15M so‘m", "20M+ so‘m"],
    "KRW": ["2.5M ₩", "3.5M ₩", "4.5M ₩", "6M+ ₩"],
    "USD": ["$1,000", "$2,000", "$3,500", "$5,000+"],
}

VISA_CHIPS = ["E-7", "D-10", "E-9", "F-2"]


def msg(key: str, lang: str, **kw: str) -> str:
    d = M[key]
    return d.get(lang, d["en"]).format(**kw)


def chips(group: str, lang: str) -> list[dict[str, str]]:
    return [{"value": k, "label": v.get(lang, v["en"])} for k, v in CHIPS[group].items()]
