"use client";

import { Briefcase, Map, MessageSquare, Plane, ShieldCheck, Target, Video } from "lucide-react";
import { useLang } from "@/lib/lang-context";

const ICONS = [Briefcase, Target, Map, MessageSquare, Plane, ShieldCheck];

export default function Features() {
  const { t } = useLang();
  return (
    <section id="features" className="scroll-mt-16 border-t border-line">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <SectionHead title={t.features.title} sub={t.features.sub} />
        <div className="mt-12 grid gap-px overflow-hidden rounded-2xl border border-line bg-line sm:grid-cols-2 lg:grid-cols-3">
          {t.features.items.map(([title, desc], i) => {
            const Icon = ICONS[i];
            return (
              <div key={title} className="group bg-white p-6 transition hover:bg-surface/60">
                <div className="mb-5 grid h-10 w-10 place-items-center rounded-xl border border-line bg-white text-ink transition group-hover:border-primary/30 group-hover:text-primary">
                  <Icon size={19} strokeWidth={1.7} />
                </div>
                <h3 className="text-[16px] font-semibold text-ink">{title}</h3>
                <p className="mt-1.5 text-[14px] leading-relaxed text-muted">{desc}</p>
              </div>
            );
          })}
        </div>
        <div className="mt-4 flex items-center gap-4 rounded-2xl border border-dashed border-line p-5">
          <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-surface text-muted">
            <Video size={19} strokeWidth={1.7} />
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="text-[15px] font-semibold text-ink">{t.features.live[0]}</h3>
            <p className="text-[13.5px] text-muted">{t.features.live[1]}</p>
          </div>
          <span className="shrink-0 rounded-full bg-surface px-2.5 py-1 text-[11.5px] font-medium text-muted">{t.features.soon}</span>
        </div>
      </div>
    </section>
  );
}

export function SectionHead({ title, sub }: { title: string; sub: string }) {
  return (
    <div className="max-w-2xl">
      <h2 className="text-[30px] font-semibold leading-tight tracking-tight text-ink sm:text-[38px]">{title}</h2>
      <p className="mt-3 text-[16px] leading-relaxed text-muted">{sub}</p>
    </div>
  );
}
