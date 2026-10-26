"use client";

import { useState } from "react";
import { ExternalLink, ShieldAlert, ShieldCheck } from "lucide-react";
import type { Dict } from "@/lib/i18n";
import Flag from "../Flag";

/* eslint-disable @typescript-eslint/no-explicit-any */

type Country = "UZ" | "KR" | "GL";

export function MatchRing({ value, size = 44 }: { value: number; size?: number }) {
  const r = 16;
  const c = 2 * Math.PI * r;
  const color = value >= 80 ? "var(--accent)" : value >= 60 ? "var(--warning)" : "#94a3b8";
  return (
    <div className="relative grid shrink-0 place-items-center" style={{ width: size, height: size }}>
      <svg viewBox="0 0 40 40" className="absolute inset-0 -rotate-90">
        <circle cx="20" cy="20" r={r} fill="none" stroke="var(--line)" strokeWidth="3.5" />
        <circle cx="20" cy="20" r={r} fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round"
          strokeDasharray={c} strokeDashoffset={c * (1 - value / 100)} className="ring-anim" />
      </svg>
      <span className="text-[11px] font-semibold tabular-nums text-ink">{value}%</span>
    </div>
  );
}

export function Jobs({ data, t, onPractice }: { data: any; t: Dict; onPractice: (job: any) => void }) {
  return (
    <div className="space-y-2.5">
      {data.jobs.map((j: any) => {
        const Risk = j.risk_level === "safe" ? ShieldCheck : ShieldAlert;
        const riskColor = j.risk_level === "safe" ? "text-accent-dark" : j.risk_level === "check" ? "text-warning-dark" : "text-red-600";
        return (
          <div key={j.id} className={`rounded-xl border bg-white p-3.5 transition hover:shadow-soft ${j.risk_level === "high" ? "border-red-200 opacity-70" : "border-line"}`}>
            <div className="flex items-start gap-3">
              <MatchRing value={j.match} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-1.5">
                  <p className="truncate text-[14px] font-semibold text-ink">{j.title}</p>
                  <Flag code={(j.country as Country) || "GL"} size={15} />
                  {j.sample && <span className="rounded bg-surface px-1.5 text-[10px] text-muted">{t.app.sample}</span>}
                </div>
                <p className="truncate text-[12.5px] text-muted">
                  {[j.company, j.city, j.salary_text].filter(Boolean).join(" · ")}
                </p>
                <div className="mt-2 flex flex-wrap gap-1.5 text-[11.5px]">
                  {j.have.map((s: string) => (
                    <span key={s} className="rounded-md bg-accent/10 px-1.5 py-0.5 text-accent-dark">✓ {s}</span>
                  ))}
                  {j.missing.map((s: string) => (
                    <span key={s} className="rounded-md bg-warning/10 px-1.5 py-0.5 text-warning-dark">+ {s}</span>
                  ))}
                </div>
              </div>
            </div>
            <div className="mt-3 flex items-center justify-between gap-2 border-t border-line pt-2.5">
              <span className={`inline-flex items-center gap-1 text-[11.5px] font-medium ${riskColor}`} title={j.risk_reasons?.join(", ")}>
                <Risk size={13} /> {t.app.risk[j.risk_level as "safe" | "check" | "high"]} · {j.source}
              </span>
              <div className="flex items-center gap-3">
                {j.url && (
                  <a href={j.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-[12px] text-muted hover:text-ink">
                    {t.app.apply} <ExternalLink size={11} />
                  </a>
                )}
                <button onClick={() => onPractice(j)} className="text-[12px] font-medium text-primary hover:underline">
                  {t.app.practice} →
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function Brief({ data, t }: { data: any; t: Dict }) {
  const label: Record<string, string> = { past: t.demo.briefRows[0][0], now: t.demo.briefRows[1][0], next: t.demo.briefRows[2][0] };
  return (
    <div className="rounded-xl border border-line bg-white p-4">
      <p className="mb-3 text-[13px] font-semibold text-ink">
        {t.demo.brief} <span className="font-normal text-muted">· {data.company}</span>
      </p>
      <dl className="space-y-2.5">
        {data.rows.map((r: any, i: number) => (
          <div key={i} className="grid grid-cols-[64px_1fr] gap-2 text-[13px]">
            <dt className="text-muted">{label[r.key] ?? r.key}</dt>
            <dd className="text-ink">
              {r.text}{" "}
              {r.source?.url && (
                <a href={r.source.url} target="_blank" rel="noreferrer"
                  className="ml-1 inline-flex items-center gap-0.5 rounded bg-surface px-1.5 py-0.5 text-[10.5px] text-muted hover:text-primary">
                  {(r.source.title || t.demo.source).slice(0, 28)} <ExternalLink size={9} />
                </a>
              )}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

export function InterviewQ({ reply, t }: { reply: any; t: Dict }) {
  const d = reply.data;
  return (
    <div className="rounded-xl border border-line bg-white p-4">
      <div className="mb-2 flex items-center justify-between text-[12px] text-muted">
        <span className="tabular-nums">{d.follow_up ? d.follow_up_label : `${d.index + 1} / ${d.total}`}</span>
        <span className="rounded-full bg-surface px-2 py-0.5">{d.category}</span>
      </div>
      <div className="mb-3 flex gap-1">
        {Array.from({ length: d.total }).map((_, i) => (
          <span key={i} className={`h-1 flex-1 rounded-full ${i <= d.index ? "bg-primary" : "bg-surface"}`} />
        ))}
      </div>
      <p className="text-[15px] leading-relaxed text-ink">{reply.text}</p>
      {d.source && (
        <a href={d.source} target="_blank" rel="noreferrer" className="mt-2 inline-flex items-center gap-1 text-[11.5px] text-muted hover:text-primary">
          {t.demo.source} <ExternalLink size={10} />
        </a>
      )}
    </div>
  );
}

function Axes({ scores, t }: { scores: Record<string, number>; t: Dict }) {
  return (
    <div className="space-y-1.5">
      {(Object.keys(t.app.axes) as (keyof Dict["app"]["axes"])[]).map((k) => (
        <div key={k} className="grid grid-cols-[100px_1fr_28px] items-center gap-2 text-[12px]">
          <span className="truncate text-muted">{t.app.axes[k]}</span>
          <div className="h-1.5 overflow-hidden rounded-full bg-surface">
            <div className="bar h-full rounded-full bg-primary" style={{ width: `${((scores[k] || 0) / 5) * 100}%` }} />
          </div>
          <span className="text-right tabular-nums text-ink">{scores[k]}</span>
        </div>
      ))}
    </div>
  );
}

export function Score({ data, t }: { data: any; t: Dict }) {
  return (
    <div className="space-y-2.5 rounded-xl border border-line bg-white p-3.5">
      <div className="flex items-center justify-between">
        <span className="text-[12px] font-medium text-muted">{t.demo.judge}</span>
        <span className="rounded-full bg-primary-soft px-2 py-0.5 text-[12px] font-semibold tabular-nums text-primary">{data.total}/100</span>
      </div>
      <Axes scores={data.scores} t={t} />
      <p className="text-[13px] leading-relaxed text-ink">{data.feedback}</p>
      {data.model_answer && <p className="rounded-lg bg-surface p-2.5 text-[12.5px] text-muted">{data.model_answer}</p>}
    </div>
  );
}

export function Report({ reply, t }: { reply: any; t: Dict }) {
  const d = reply.data;
  return (
    <div className="space-y-3 rounded-xl border border-line bg-white p-4">
      <p className="text-[14px] font-semibold text-ink">{reply.text}</p>
      <div className="flex items-center gap-4">
        <MatchRing value={d.readiness} size={64} />
        <div className="flex-1">
          <p className="mb-1.5 text-[12px] text-muted">{t.app.readiness} · {d.company}</p>
          <Axes scores={d.axes} t={t} />
        </div>
      </div>
    </div>
  );
}

export function Roadmap({ data, t }: { data: any; t: Dict }) {
  const all = data.blocks.flatMap((b: any) => b.tasks);
  const [done, setDone] = useState<boolean[]>(() => all.map(() => false));
  const pct = Math.round((done.filter(Boolean).length / Math.max(all.length, 1)) * 100);
  let n = -1;
  return (
    <div className="rounded-xl border border-line bg-white p-4">
      <div className="mb-1 flex items-center justify-between">
        <p className="text-[13px] font-semibold text-ink">{t.demo.plan}</p>
        <span className="text-[12px] tabular-nums text-muted">{pct}%</span>
      </div>
      <p className="mb-3 text-[12px] text-muted">
        {data.weeks} {t.app.weeks.toLowerCase()} · {data.total_hours} {t.app.hoursTotal}
      </p>
      <div className="mb-4 h-1.5 overflow-hidden rounded-full bg-surface">
        <div className="h-full rounded-full bg-accent transition-all duration-500" style={{ width: `${pct}%` }} />
      </div>
      <div className="space-y-4">
        {data.blocks.map((b: any) => (
          <div key={b.title}>
            <p className="mb-1.5 text-[12px] font-medium text-muted">
              {t.app.weeks} {b.weeks} · {b.title}
            </p>
            <ul className="space-y-0.5">
              {b.tasks.map((task: any) => {
                n += 1;
                const i = n;
                return (
                  <li key={i}>
                    <label className="flex cursor-pointer items-start gap-2.5 rounded-lg px-1.5 py-1.5 text-[13px] hover:bg-surface">
                      <input type="checkbox" checked={done[i]} onChange={() => setDone((d) => d.map((v, j) => (j === i ? !v : v)))}
                        className="mt-0.5 h-4 w-4 accent-[var(--accent)]" />
                      <span className={`flex-1 ${done[i] ? "text-muted line-through" : "text-ink"}`}>
                        {task.text} <span className="text-muted">· {task.hours}h</span>
                        {task.resource?.url && (
                          <a href={task.resource.url} target="_blank" rel="noreferrer" className="ml-1.5 text-[11.5px] text-primary hover:underline">
                            {task.resource.title} ↗
                          </a>
                        )}
                      </span>
                    </label>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
