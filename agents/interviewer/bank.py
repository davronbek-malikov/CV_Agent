"""Interview question bank in Uzbek, Russian, Korean and English.

Placeholders: {company}, {role}, {skill}, {headline}.
"""

Q = dict[str, list[str]]

BANK: dict[str, Q] = {
    "intro": {
        "en": ["Please introduce yourself in one minute.", "Walk me through your CV in two minutes."],
        "uz": ["Bir daqiqada o‘zingizni tanishtiring.", "Rezyumengizni ikki daqiqada tushuntirib bering."],
        "ru": ["Представьтесь, пожалуйста, за одну минуту.", "Расскажите о своём резюме за две минуты."],
        "ko": ["1분 자기소개 부탁드립니다.", "2분 동안 이력서를 설명해 주세요."],
    },
    "motivation": {
        "en": ["Why do you want to work at {company}, and why as a {role}?", "Why are you leaving, or starting, now?"],
        "uz": ["Nega aynan {company} da {role} bo‘lib ishlamoqchisiz?", "Nega aynan hozir ish qidiryapsiz?"],
        "ru": ["Почему вы хотите работать в {company} на позиции {role}?", "Почему вы ищете работу именно сейчас?"],
        "ko": ["왜 {company}에서 {role}(으)로 일하고 싶으신가요?", "왜 지금 이직(취업)하려고 하시나요?"],
    },
    "company": {
        "en": ["We recently saw this news: “{headline}”. How could your role help with that?",
               "What do you know about {company}'s main product, and how would you improve it?"],
        "uz": ["Yaqinda shunday yangilik bo‘ldi: “{headline}”. Sizning rolingiz bunda qanday yordam beradi?",
               "{company} ning asosiy mahsuloti haqida nima bilasiz va uni qanday yaxshilagan bo‘lardingiz?"],
        "ru": ["Недавно была новость: «{headline}». Как ваша роль может помочь в этом?",
               "Что вы знаете об основном продукте {company} и как бы вы его улучшили?"],
        "ko": ["최근 이런 뉴스가 있었습니다: “{headline}”. 지원하신 직무로 어떻게 기여할 수 있을까요?",
               "{company}의 주력 제품에 대해 아는 것과, 개선한다면 무엇을 바꾸시겠습니까?"],
    },
    "technical": {
        "en": ["Explain a real project where you used {skill}. What was hard and how did you solve it?",
               "If you joined tomorrow, how would you use {skill} in your first month at {company}?"],
        "uz": ["{skill} ishlatgan real loyihangiz haqida gapiring. Nima qiyin bo‘ldi va qanday hal qildingiz?",
               "Ertaga ishga kirsangiz, {company} da birinchi oyda {skill} ni qanday qo‘llaysiz?"],
        "ru": ["Расскажите о реальном проекте, где вы использовали {skill}. Что было сложно и как вы это решили?",
               "Если бы вы вышли завтра, как бы вы применили {skill} в первый месяц в {company}?"],
        "ko": ["{skill}을(를) 사용한 실제 프로젝트를 설명해 주세요. 어려웠던 점과 해결 방법은 무엇이었나요?",
               "내일 입사한다면 {company}에서 첫 달에 {skill}을(를) 어떻게 활용하시겠습니까?"],
    },
    "behavioral": {
        "en": ["Tell me about a time you disagreed with your team. What did you do?",
               "Describe a mistake you made at work or in a project, and what you learned."],
        "uz": ["Jamoangiz bilan kelisha olmagan vaziyatni aytib bering. Nima qildingiz?",
               "Ishda yoki loyihada qilgan xatoyingiz va undan nima o‘rganganingizni aytib bering."],
        "ru": ["Расскажите о случае, когда вы не согласились с командой. Что вы сделали?",
               "Опишите ошибку, которую вы допустили в работе или проекте, и чему она вас научила."],
        "ko": ["팀과 의견이 달랐던 경험을 말씀해 주세요. 어떻게 하셨나요?",
               "업무나 프로젝트에서 했던 실수와 그로부터 배운 점을 말씀해 주세요."],
    },
    "cv": {
        "en": ["Your CV lists {skill}. How deep is that knowledge, really? Give a concrete example."],
        "uz": ["Rezyumengizda {skill} yozilgan. Bu bilim qanchalik chuqur? Aniq misol keltiring."],
        "ru": ["В резюме указан {skill}. Насколько глубоко вы его знаете? Приведите конкретный пример."],
        "ko": ["이력서에 {skill}이(가) 있는데, 실제로 얼마나 깊이 알고 계신가요? 구체적인 예를 들어 주세요."],
    },
    "stress": {
        "en": ["Honestly, other candidates have more experience. Why should we choose you?",
               "That answer was too general. Try again, in 30 seconds, with one number.",
               "If we reject you today, what will you do tomorrow?"],
        "uz": ["Ochig‘i, boshqa nomzodlarning tajribasi ko‘proq. Nega sizni tanlashimiz kerak?",
               "Bu javob juda umumiy edi. 30 soniyada, bitta raqam bilan qayta urinib ko‘ring.",
               "Bugun sizni rad etsak, ertaga nima qilasiz?"],
        "ru": ["Честно говоря, у других кандидатов больше опыта. Почему мы должны выбрать вас?",
               "Ответ слишком общий. Попробуйте ещё раз за 30 секунд, с одной цифрой.",
               "Если мы вам сегодня откажем, что вы будете делать завтра?"],
        "ko": ["솔직히 다른 지원자들이 경력이 더 많습니다. 왜 당신을 뽑아야 합니까?",
               "답변이 너무 일반적입니다. 30초 안에 숫자 하나를 넣어서 다시 말해 보세요.",
               "오늘 불합격한다면 내일 무엇을 하시겠습니까?"],
    },
    "culture": {
        "en": ["How do you work with a manager who gives very little feedback?"],
        "uz": ["Juda kam fikr bildiradigan rahbar bilan qanday ishlaysiz?"],
        "ru": ["Как вы работаете с руководителем, который почти не даёт обратной связи?"],
        "ko": ["피드백을 거의 주지 않는 상사와는 어떻게 일하시겠습니까?"],
    },
    "background": {
        "en": ["When can you start, and is relocation or a visa needed?"],
        "uz": ["Qachon ishni boshlay olasiz, ko‘chib o‘tish yoki viza kerakmi?"],
        "ru": ["Когда вы можете выйти на работу, нужен ли переезд или виза?"],
        "ko": ["언제부터 근무 가능하신가요? 이주나 비자가 필요하신가요?"],
    },
    "salary": {
        "en": ["What salary do you expect, and how did you decide on that number?",
               "Our budget is 15% lower than your expectation. What would you say?"],
        "uz": ["Qancha maosh kutasiz va bu raqamni qanday aniqladingiz?",
               "Bizning byudjet kutganingizdan 15% kam. Nima deysiz?"],
        "ru": ["Какую зарплату вы ожидаете и как вы пришли к этой цифре?",
               "Наш бюджет на 15% ниже ваших ожиданий. Что скажете?"],
        "ko": ["희망 연봉은 얼마이고, 그 금액은 어떻게 정하셨나요?",
               "저희 예산이 희망 연봉보다 15% 낮습니다. 어떻게 하시겠습니까?"],
    },
    "reverse": {
        "en": ["Do you have any questions for us?"],
        "uz": ["Bizga savollaringiz bormi?"],
        "ru": ["У вас есть вопросы к нам?"],
        "ko": ["저희에게 궁금한 점이 있으신가요?"],
    },
}

FOLLOW_UP: dict[str, dict[str, str]] = {
    "short": {
        "en": "Can you give one concrete example with a result?",
        "uz": "Natijasi bilan bitta aniq misol keltira olasizmi?",
        "ru": "Можете привести один конкретный пример с результатом?",
        "ko": "결과가 포함된 구체적인 예를 하나 들어 주시겠어요?",
    },
    "number": {
        "en": "How did you measure that? Give me a number.",
        "uz": "Buni qanday o‘lchadingiz? Raqam bilan ayting.",
        "ru": "Как вы это измерили? Назовите цифру.",
        "ko": "그것을 어떻게 측정하셨나요? 숫자로 말씀해 주세요.",
    },
}

ROLE_NAME = {
    "dev": {"en": "developer", "uz": "dasturchi", "ru": "разработчик", "ko": "개발자"},
    "frontend": {"en": "frontend developer", "uz": "frontend dasturchi", "ru": "фронтенд-разработчик", "ko": "프론트엔드 개발자"},
    "data": {"en": "data analyst", "uz": "data tahlilchi", "ru": "аналитик данных", "ko": "데이터 분석가"},
    "ai": {"en": "AI engineer", "uz": "AI muhandis", "ru": "AI-инженер", "ko": "AI 엔지니어"},
    "design": {"en": "designer", "uz": "dizayner", "ru": "дизайнер", "ko": "디자이너"},
    "marketing": {"en": "marketer", "uz": "marketolog", "ru": "маркетолог", "ko": "마케터"},
}

PLANS = {
    "full": ["intro", "motivation", "company", "technical", "behavioral", "cv", "stress", "culture", "background", "salary", "reverse"],
    "tech": ["intro", "technical", "technical", "cv", "company", "behavioral"],
    "stress": ["intro", "stress", "cv", "stress", "behavioral", "stress"],
    "salary": ["intro", "background", "salary", "salary", "reverse"],
}
