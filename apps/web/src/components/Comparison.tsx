"use client";

import { useState } from "react";
import { Check, ExternalLink, Minus } from "lucide-react";
import { useLang } from "@/lib/lang-context";
import { ROWS, TOOLS, type Category, type Mark } from "@/lib/data";
import { SectionHead } from "./Features";

type Tab = "all" | Category;

export default function Comparison() {
  const { t } = useLang();
  const [tab, setTab] = useState<Tab>("all");
  const [focus, setFocus] = useState<string | null>(null);
  const rows = ROWS.filter((r) => tab === "all" || r.cat === tab);

  const coverage = (marks: Record<string, Mark>) =>
    Math.round((ROWS.reduce((s, r) => s + (marks[r.key] === "y" ? 1 : marks[r.key] === "p" ? 0.5 : 0), 0) / ROWS.length) * 100);

  return (
    <section id="compare" className="scroll-mt-16 border-t border-line">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <SectionHead title={t.compare.title} sub={t.compare.sub} />

        <div className="mt-10 flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap gap-1 rounded-xl bg-surface p-1">
            {(Object.keys(t.compare.tabs) as Tab[]).map((k) => (
              <button
                key={k}
                onClick={() => setTab(k)}
                className={`rounded-lg px-3.5 py-1.5 text-[13px] font-medium transition ${
                  tab === k ? "bg-white text-ink shadow-soft" : "text-muted hover:text-ink"
                }`}
              >
                {t.compare.tabs[k]}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-4 text-[12.5px] text-muted">
            <span className="inline-flex items-center gap-1.5"><MarkIcon m="y" /> {t.compare.yes}</span>
            <span className="inline-flex items-center gap-1.5"><MarkIcon m="p" /> {t.compare.partial}</span>
            <span className="inline-flex items-center gap-1.5"><MarkIcon m="n" /> {t.compare.no}</span>
          </div>
        </div>

        <div className="mt-5 overflow-x-auto rounded-2xl border border-line">
          <table className="w-full min-w-[860px] border-collapse text-left">
            <thead>
              <tr className="border-b border-line">
                <th className="sticky left-0 z-10 w-[230px] bg-white p-4" />
                {TOOLS.map((tool, i) => {
                  const ours = i === 0;
                  const dim = focus && focus !== tool.name && !ours;
                  return (
                    <th
                      key={tool.name}
                      onMouseEnter={() => setFocus(tool.name)}
                      onMouseLeave={() => setFocus(null)}
                      className={`px-2 py-4 text-center align-bottom transition ${ours ? "bg-primary-soft/60" : ""} ${dim ? "opacity-40" : ""}`}
                    >
                      <a
                        href={tool.url}
                        target={ours ? undefined : "_blank"}
                        rel="noreferrer"
                        className={`inline-flex items-center gap-1 text-[13px] font-semibold ${ours ? "text-primary" : "text-ink hover:text-primary"}`}
                      >
                        {tool.name}
                        {!ours && <ExternalLink size={11} className="text-muted" />}
                      </a>
                      <div className="mx-auto mt-2 h-1 w-14 overflow-hidden rounded-full bg-surface">
                        <div
                          className={`bar h-full rounded-full ${ours ? "bg-primary" : "bg-ink/40"}`}
                          style={{ width: `${coverage(tool.marks)}%` }}
                        />
                      </div>
                      <div className="mt-1 text-[11px] font-normal tabular-nums text-muted">
                        {coverage(tool.marks)}% {t.compare.covers}
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.key} className="border-b border-line last:border-0 hover:bg-surface/50">
                  <td className="sticky left-0 z-10 bg-white p-4 text-[13.5px] text-ink">{t.compare.rows[r.key]}</td>
                  {TOOLS.map((tool, i) => {
                    const ours = i === 0;
                    const dim = focus && focus !== tool.name && !ours;
                    return (
                      <td
                        key={tool.name}
                        className={`px-2 py-3 text-center transition ${ours ? "bg-primary-soft/60" : ""} ${dim ? "opacity-30" : ""}`}
                      >
                        <MarkIcon m={tool.marks[r.key]} ours={ours} />
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 space-y-1 text-[12.5px] leading-relaxed text-muted">
          <p>* {t.compare.planned}</p>
          <p>
            {t.compare.sourceNote}{" "}
            <a href="https://www.jobscan.co/blog/ai-job-search-tools/" target="_blank" rel="noreferrer" className="underline hover:text-ink">
              jobscan.co
            </a>
          </p>
        </div>
      </div>
    </section>
  );
}

function MarkIcon({ m, ours }: { m: Mark; ours?: boolean }) {
  if (m === "y")
    return (
      <span className={`inline-grid h-6 w-6 place-items-center rounded-full ${ours ? "bg-primary text-white" : "bg-ink text-white"}`}>
        <Check size={13} strokeWidth={3} />
      </span>
    );
  if (m === "p")
    return (
      <span
        className="inline-block h-[18px] w-[18px] rounded-full border-2 border-ink/60 align-middle"
        style={{ background: "linear-gradient(90deg, rgba(15,23,42,.6) 50%, transparent 50%)" }}
      />
    );
  return (
    <span className="inline-grid h-6 w-6 place-items-center text-line">
      <Minus size={16} strokeWidth={2.5} className="text-[#C9CDD4]" />
    </span>
  );
}
