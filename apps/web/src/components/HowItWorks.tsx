"use client";

import { useLang } from "@/lib/lang-context";

export default function HowItWorks() {
  const { t } = useLang();
  return (
    <section className="border-t border-line bg-surface/50">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <h2 className="text-[30px] font-semibold tracking-tight text-ink sm:text-[38px]">{t.how.title}</h2>
        <ol className="mt-12 grid gap-8 md:grid-cols-3 md:gap-6">
          {t.how.steps.map(([title, desc], i) => (
            <li key={title} className="relative">
              <div className="mb-4 flex items-center gap-3">
                <span className="grid h-8 w-8 place-items-center rounded-full bg-ink text-[13px] font-semibold text-white tabular-nums">
                  {i + 1}
                </span>
                {i < 2 && <span className="hidden h-px flex-1 bg-line md:block" />}
              </div>
              <h3 className="text-[17px] font-semibold text-ink">{title}</h3>
              <p className="mt-1.5 max-w-sm text-[14.5px] leading-relaxed text-muted">{desc}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
