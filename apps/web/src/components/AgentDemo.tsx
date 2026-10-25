"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowUp, Briefcase, Check, Map, MessageSquare, RotateCcw, ShieldAlert, ShieldCheck, Sparkles } from "lucide-react";
import { useLang } from "@/lib/lang-context";
import { LANGS, type Dict, type Lang } from "@/lib/i18n";
import { pickJobs, salaryChips, type Job, type Role, type Scope } from "@/lib/data";
import Flag from "./Flag";

type Mode = "jobs" | "interview" | "roadmap";
type Answer = { id: string; value: string; label: string };
type Chip = { value: string; label: string };
type Step = { id: string; q: (t: Dict) => string; chips: (t: Dict, a: Record<string, string>) => Chip[]; when?: (a: Record<string, string>) => boolean };

const langStep: Step = {
  id: "lang",
  q: (t) => t.demo.qLang,
  chips: () => LANGS.map((l) => ({ value: l.code, label: l.label })),
};

const FLOWS: Record<Mode, Step[]> = {
  jobs: [
    {
      id: "scope",
      q: (t) => t.demo.qScope,
      chips: (t) => (Object.keys(t.demo.scope) as Scope[]).map((k) => ({ value: k, label: t.demo.scope[k] })),
    },
    {
      id: "role",
      q: (t) => t.demo.qRole,
      chips: (t) => (Object.keys(t.demo.roles) as Role[]).map((k) => ({ value: k, label: t.demo.roles[k] })),
    },
    {
      id: "salary",
      q: (t) => t.demo.qSalary,
      chips: (t, a) => [...salaryChips(a.scope as Scope).map((s) => ({ value: s, label: s })), { value: "?", label: t.demo.notSure }],
    },
    {
      id: "visa",
      q: (t) => t.demo.qVisa,
      chips: (t) => ["E-7", "D-10", "F-2"].map((v) => ({ value: v, label: v })).concat({ value: "?", label: t.demo.notSure }),
      when: (a) => a.scope === "kr" || a.scope === "multi",
    },
  ],
  interview: [
    { id: "company", q: (t) => t.demo.qCompany, chips: (t) => t.demo.companies.map((c) => ({ value: c, label: c })) },
    {
      id: "type",
      q: (t) => t.demo.qType,
      chips: (t) => (Object.keys(t.demo.types) as (keyof Dict["demo"]["types"])[]).map((k) => ({ value: k, label: t.demo.types[k] })),
    },
  ],
  roadmap: [
    { id: "target", q: (t) => t.demo.qTarget, chips: (t) => t.demo.targets.map((c) => ({ value: c, label: c })) },
    { id: "days", q: (t) => t.demo.qDays, chips: (t) => t.demo.days.map((c) => ({ value: c, label: c })) },
    { id: "hours", q: (t) => t.demo.qHours, chips: (t) => t.demo.hours.map((c) => ({ value: c, label: c })) },
  ],
};

const MODE_ICON = { jobs: Briefcase, interview: MessageSquare, roadmap: Map };

export default function AgentDemo() {
  const { t, setLang } = useLang();
  const [mode, setMode] = useState<Mode>("jobs");
  const [langPicked, setLangPicked] = useState(false);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [shown, setShown] = useState(0); // activity lines revealed
  const [userAnswer, setUserAnswer] = useState<string | null>(null); // interview answer
  const [judged, setJudged] = useState(0);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const a = useMemo(() => Object.fromEntries(answers.map((x) => [x.id, x.value])), [answers]);

  const steps = useMemo(() => {
    const base = FLOWS[mode].filter((s) => !s.when || s.when(a));
    return langPicked && !answers.some((x) => x.id === "lang") ? base : [langStep, ...base];
  }, [mode, a, langPicked, answers]);

  const current = steps.find((s) => !(s.id in a));
  const finished = !current;

  const activity =
    mode === "jobs" ? t.demo.steps : mode === "interview" ? t.demo.researching : t.demo.planning;

  // Reveal agent activity one line at a time once the questions are done.
  useEffect(() => {
    if (!finished || shown >= activity.length) return;
    const id = setTimeout(() => setShown((n) => n + 1), 550);
    return () => clearTimeout(id);
  }, [finished, shown, activity.length]);

  useEffect(() => {
    if (userAnswer === null || judged >= 2) return;
    const id = setTimeout(() => setJudged((n) => n + 1), 700);
    return () => clearTimeout(id);
  }, [userAnswer, judged]);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [answers, shown, judged, userAnswer, t]);

  function answer(value: string, label: string) {
    if (!current) return;
    if (current.id === "lang") {
      setLang(value as Lang);
      setLangPicked(true);
    }
    setAnswers((prev) => [...prev, { id: current.id, value, label }]);
  }

  function reset(next: Mode, prefill: Answer[] = []) {
    setMode(next);
    setAnswers(prefill);
    setShown(0);
    setUserAnswer(null);
    setJudged(0);
    setInput("");
  }

  function submitText() {
    const text = input.trim();
    if (!text) return;
    setInput("");
    if (current) {
      const fallback: Record<string, string> = { scope: "all", role: "", lang: "en" };
      if (current.id === "lang") return; // language must be picked from the buttons
      answer(current.id in fallback ? fallback[current.id] : text, text);
    } else if (mode === "interview" && shown >= activity.length && userAnswer === null) {
      setUserAnswer(text);
    }
  }

  const jobs = mode === "jobs" ? pickJobs((a.scope as Scope) || "all", (a.role as Role) || null) : [];
  const awaitingInterview = mode === "interview" && finished && shown >= activity.length && userAnswer === null;
  const inputEnabled = (current && current.id !== "lang") || awaitingInterview;

  return (
    <div className="card overflow-hidden">
      {/* Mode switch */}
      <div className="flex items-center gap-1 border-b border-line p-2">
        {(Object.keys(FLOWS) as Mode[]).map((m) => {
          const Icon = MODE_ICON[m];
          const active = m === mode;
          return (
            <button
              key={m}
              onClick={() => reset(m)}
              className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg px-2 py-2 text-[13px] font-medium transition ${
                active ? "bg-ink text-white" : "text-muted hover:bg-surface hover:text-ink"
              }`}
            >
              <Icon size={15} strokeWidth={1.8} />
              <span className="truncate">{t.demo.modes[m]}</span>
            </button>
          );
        })}
      </div>

      {/* Conversation */}
      <div ref={scrollRef} className="h-[460px] space-y-3 overflow-y-auto px-4 py-5 sm:px-5" aria-live="polite">
        {steps.map((s) => {
          const ans = answers.find((x) => x.id === s.id);
          if (!ans && s !== current) return null;
          return (
            <div key={s.id} className="space-y-3">
              <Bot>{s.q(t)}</Bot>
              {ans ? (
                <User>{ans.label}</User>
              ) : (
                <div className="flex flex-wrap gap-2 pl-9 fade-up">
                  {s.chips(t, a).map((c) => (
                    <button key={c.value + c.label} onClick={() => answer(c.value, c.label)} className="chip">
                      {c.label}
                    </button>
                  ))}
                  {s.id !== "lang" && (
                    <button onClick={() => answer("", t.demo.skip)} className="chip chip-ghost">
                      {t.demo.skip}
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {finished && <Activity title={t.demo.working} lines={activity} shown={shown} />}

        {finished && shown >= activity.length && mode === "jobs" && (
          <div className="space-y-2.5 pl-9 fade-up">
            <p className="text-[13px] font-semibold text-ink">{t.demo.results}</p>
            {jobs.map((j) => (
              <JobCard
                key={j.title + j.company}
                job={j}
                t={t}
                onPractice={() =>
                  reset("interview", [{ id: "company", value: j.company, label: `${j.company} · ${j.title}` }])
                }
              />
            ))}
          </div>
        )}

        {finished && shown >= activity.length && mode === "interview" && (
          <div className="space-y-3 pl-9 fade-up">
            <Brief t={t} company={answers.find((x) => x.id === "company")?.label ?? ""} />
            <div className="rounded-xl border border-line bg-white p-4">
              <div className="mb-2 flex items-center justify-between text-[12px] text-muted">
                <span>{t.demo.qNum}</span>
                <span className="rounded-full bg-surface px-2 py-0.5">{t.demo.types[(a.type as keyof Dict["demo"]["types"]) || "full"]}</span>
              </div>
              <p className="text-[15px] leading-relaxed text-ink">
                {t.demo.questions[(a.type as keyof Dict["demo"]["questions"]) || "full"]}
              </p>
              {userAnswer === null && <p className="mt-3 text-[12px] text-muted">{t.demo.answerHint}</p>}
            </div>
          </div>
        )}

        {userAnswer !== null && (
          <>
            <User>{userAnswer}</User>
            {judged < 2 ? (
              <Bot>
                <TypingDots />
              </Bot>
            ) : (
              <Score t={t} onRoadmap={() => reset("roadmap")} />
            )}
          </>
        )}

        {finished && shown >= activity.length && mode === "roadmap" && <Plan t={t} answers={answers} />}

        {finished && shown >= activity.length && (mode !== "interview" || judged >= 2) && (
          <div className="pl-9">
            <button onClick={() => reset(mode)} className="chip chip-ghost inline-flex items-center gap-1.5">
              <RotateCcw size={13} /> {t.demo.restart}
            </button>
          </div>
        )}
      </div>

      {/* Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submitText();
        }}
        className="flex items-center gap-2 border-t border-line p-3"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!inputEnabled}
          placeholder={t.demo.placeholder}
          className="h-11 flex-1 rounded-xl bg-surface px-4 text-[14px] text-ink outline-none ring-primary/30 placeholder:text-muted focus:ring-2 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!inputEnabled || !input.trim()}
          aria-label="Send"
          className="grid h-11 w-11 place-items-center rounded-xl bg-primary text-white transition hover:bg-primary-dark disabled:opacity-30"
        >
          <ArrowUp size={18} />
        </button>
      </form>
    </div>
  );
}

function Bot({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-start gap-2.5 fade-up">
      <div className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full bg-ink text-white">
        <Sparkles size={13} />
      </div>
      <div className="max-w-[85%] rounded-2xl rounded-tl-md bg-surface px-3.5 py-2.5 text-[14px] leading-relaxed text-ink">
        {children}
      </div>
    </div>
  );
}

function User({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex justify-end fade-up">
      <div className="max-w-[80%] rounded-2xl rounded-tr-md bg-primary px-3.5 py-2.5 text-[14px] leading-relaxed text-white">
        {children}
      </div>
    </div>
  );
}

function TypingDots() {
  return (
    <span className="inline-flex gap-1 py-1">
      {[0, 1, 2].map((i) => (
        <span key={i} className="dot h-1.5 w-1.5 rounded-full bg-muted" style={{ animationDelay: `${i * 0.15}s` }} />
      ))}
    </span>
  );
}

function Activity({ title, lines, shown }: { title: string; lines: string[]; shown: number }) {
  const done = shown >= lines.length;
  return (
    <div className="ml-9 rounded-xl border border-line bg-white p-3 fade-up">
      <div className="mb-2 flex items-center gap-2 text-[12px] font-medium text-muted">
        <span className={`h-1.5 w-1.5 rounded-full ${done ? "bg-accent" : "pulse bg-primary"}`} />
        {title}
      </div>
      <ul className="space-y-1.5">
        {lines.slice(0, shown).map((l, i) => {
          const isJudge = i === lines.length - 1;
          return (
            <li key={l} className="flex items-center gap-2 text-[12.5px] text-ink fade-up">
              <Check size={13} className={isJudge ? "text-accent" : "text-primary"} strokeWidth={2.5} />
              <span className="font-mono text-[12px]">{l}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function MatchRing({ value }: { value: number }) {
  const r = 16;
  const c = 2 * Math.PI * r;
  const color = value >= 80 ? "var(--accent)" : "var(--warning)";
  return (
    <div className="relative grid h-11 w-11 shrink-0 place-items-center">
      <svg viewBox="0 0 40 40" className="absolute inset-0 -rotate-90">
        <circle cx="20" cy="20" r={r} fill="none" stroke="var(--line)" strokeWidth="3.5" />
        <circle
          cx="20" cy="20" r={r} fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round"
          strokeDasharray={c} strokeDashoffset={c * (1 - value / 100)} className="ring-anim"
        />
      </svg>
      <span className="text-[11px] font-semibold tabular-nums text-ink">{value}%</span>
    </div>
  );
}

function JobCard({ job, t, onPractice }: { job: Job; t: Dict; onPractice: () => void }) {
  const Risk = job.risk === "safe" ? ShieldCheck : ShieldAlert;
  return (
    <div className="rounded-xl border border-line bg-white p-3.5 transition hover:border-ink/20 hover:shadow-soft">
      <div className="flex items-start gap-3">
        <MatchRing value={job.match} />
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <p className="truncate text-[14px] font-semibold text-ink">{job.title}</p>
            <Flag code={job.region} size={15} />
          </div>
          <p className="truncate text-[12.5px] text-muted">
            {job.company} · {job.city} · {job.salary}
          </p>
          <div className="mt-2 flex flex-wrap items-center gap-1.5 text-[11.5px]">
            <span className="text-muted">{t.demo.why}:</span>
            {job.have.map((s) => (
              <span key={s} className="rounded-md bg-accent/10 px-1.5 py-0.5 text-accent-dark">✓ {s}</span>
            ))}
            <span className="rounded-md bg-warning/10 px-1.5 py-0.5 text-warning-dark">
              {t.demo.missing}: {job.miss}
            </span>
          </div>
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between border-t border-line pt-2.5">
        <span className={`inline-flex items-center gap-1 text-[11.5px] font-medium ${job.risk === "safe" ? "text-accent-dark" : "text-warning-dark"}`}>
          <Risk size={13} /> {job.risk === "safe" ? t.demo.safe : t.demo.check} · {job.source}
        </span>
        <button onClick={onPractice} className="text-[12px] font-medium text-primary hover:underline">
          {t.demo.practice} →
        </button>
      </div>
    </div>
  );
}

function Brief({ t, company }: { t: Dict; company: string }) {
  return (
    <div className="rounded-xl border border-line bg-white p-4">
      <p className="mb-3 text-[13px] font-semibold text-ink">
        {t.demo.brief} <span className="font-normal text-muted">· {company}</span>
      </p>
      <dl className="space-y-2">
        {t.demo.briefRows.map(([k, v]) => (
          <div key={k} className="grid grid-cols-[64px_1fr] gap-2 text-[13px]">
            <dt className="text-muted">{k}</dt>
            <dd className="text-ink">
              {v} <span className="ml-1 rounded bg-surface px-1.5 py-0.5 text-[10.5px] text-muted">{t.demo.source} ↗</span>
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

function Score({ t, onRoadmap }: { t: Dict; onRoadmap: () => void }) {
  const scores = [4, 2.5, 3.5, 3];
  const total = Math.round((scores.reduce((s, x) => s + x, 0) / (scores.length * 5)) * 100);
  return (
    <div className="ml-9 space-y-3 rounded-xl border border-line bg-white p-4 fade-up">
      <div className="flex items-center justify-between">
        <p className="text-[13px] font-semibold text-ink">{t.demo.judge}</p>
        <span className="rounded-full bg-primary-soft px-2.5 py-1 text-[12px] font-semibold tabular-nums text-primary">
          {t.demo.readiness} {total}/100
        </span>
      </div>
      <div className="space-y-2">
        {t.demo.axes.map((ax, i) => (
          <div key={ax} className="grid grid-cols-[110px_1fr_32px] items-center gap-2 text-[12.5px]">
            <span className="truncate text-muted">{ax}</span>
            <div className="h-1.5 overflow-hidden rounded-full bg-surface">
              <div className="bar h-full rounded-full bg-primary" style={{ width: `${(scores[i] / 5) * 100}%` }} />
            </div>
            <span className="text-right tabular-nums text-ink">{scores[i]}</span>
          </div>
        ))}
      </div>
      <p className="text-[13px] leading-relaxed text-ink">{t.demo.feedback}</p>
      <button onClick={onRoadmap} className="text-[12.5px] font-medium text-primary hover:underline">
        {t.demo.toRoadmap} →
      </button>
    </div>
  );
}

function Plan({ t, answers }: { t: Dict; answers: Answer[] }) {
  const label = (id: string) => answers.find((x) => x.id === id)?.label;
  const meta = [label("target"), label("days"), label("hours")].filter(Boolean).join(" · ");
  const [done, setDone] = useState<boolean[]>([true, false, false, false]);
  const pct = Math.round((done.filter(Boolean).length / done.length) * 100);
  return (
    <div className="ml-9 rounded-xl border border-line bg-white p-4 fade-up">
      <div className="mb-1 flex items-center justify-between">
        <p className="text-[13px] font-semibold text-ink">{t.demo.plan}</p>
        <span className="text-[12px] tabular-nums text-muted">{pct}%</span>
      </div>
      {meta && <p className="mb-3 text-[12px] text-muted">{meta}</p>}
      <div className="mb-3 h-1.5 overflow-hidden rounded-full bg-surface">
        <div className="h-full rounded-full bg-accent transition-all duration-500" style={{ width: `${pct}%` }} />
      </div>
      <ul className="space-y-1">
        {t.demo.planRows.map((row, i) => (
          <li key={row}>
            <label className="flex cursor-pointer items-center gap-2.5 rounded-lg px-1.5 py-1.5 text-[13px] hover:bg-surface">
              <input
                type="checkbox"
                checked={done[i]}
                onChange={() => setDone((d) => d.map((v, j) => (j === i ? !v : v)))}
                className="h-4 w-4 accent-[var(--accent)]"
              />
              <span className={done[i] ? "text-muted line-through" : "text-ink"}>{row}</span>
            </label>
          </li>
        ))}
      </ul>
    </div>
  );
}
