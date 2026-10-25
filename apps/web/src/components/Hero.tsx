"use client";

import { ArrowRight } from "lucide-react";
import { useLang } from "@/lib/lang-context";
import AgentDemo from "./AgentDemo";
import Flag from "./Flag";

export default function Hero() {
  const { t } = useLang();
  return (
    <section id="top" className="relative overflow-hidden">
      <div className="grid-bg pointer-events-none absolute inset-0" aria-hidden />
      <div className="relative mx-auto grid max-w-6xl gap-12 px-4 pb-20 pt-14 sm:px-6 lg:grid-cols-[1fr_440px] lg:gap-14 lg:pt-20">
        <div className="flex flex-col justify-center">
          <span className="mb-6 inline-flex w-fit items-center gap-2 rounded-full border border-line bg-white px-3 py-1 text-[12px] font-medium text-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-accent" />
            {t.hero.badge}
          </span>
          <h1 className="text-[40px] font-semibold leading-[1.05] tracking-tight text-ink sm:text-[56px] lg:text-[64px]">
            {t.hero.title1}
            <br />
            <span className="text-primary">{t.hero.title2}</span>
          </h1>
          <p className="mt-6 max-w-xl text-[17px] leading-relaxed text-muted">{t.hero.sub}</p>
          <div className="mt-6 flex flex-wrap gap-2 text-[13px]">
            {([["UZ", "O‘zbekiston"], ["KR", "대한민국"], ["GL", "Worldwide"]] as const).map(([code, name]) => (
              <span key={code} className="inline-flex items-center gap-2 rounded-full bg-surface px-3 py-1.5 text-ink">
                <Flag code={code} /> {name}
              </span>
            ))}
          </div>
          <div className="mt-9 flex flex-wrap gap-3">
            <a href="#demo" className="btn-primary">
              {t.hero.cta} <ArrowRight size={16} />
            </a>
            <a href="#compare" className="btn-ghost">{t.hero.cta2}</a>
          </div>
          <dl className="mt-12 grid max-w-xl grid-cols-2 gap-x-6 gap-y-5 border-t border-line pt-6 sm:grid-cols-4">
            {t.hero.stats.map(([n, l]) => (
              <div key={l}>
                <dt className="text-[26px] font-semibold tabular-nums tracking-tight text-ink">{n}</dt>
                <dd className="text-[12.5px] leading-snug text-muted">{l}</dd>
              </div>
            ))}
          </dl>
        </div>
        <div id="demo" className="scroll-mt-24">
          <div className="mb-3 flex items-end justify-between">
            <div>
              <h2 className="text-[15px] font-semibold text-ink">{t.demo.title}</h2>
              <p className="text-[12.5px] text-muted">{t.demo.sub}</p>
            </div>
            <span className="shrink-0 rounded-full bg-surface px-2 py-0.5 text-[11px] text-muted">{t.demo.note}</span>
          </div>
          <AgentDemo />
        </div>
      </div>
    </section>
  );
}
