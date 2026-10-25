"use client";

import { Gavel, Network, User, Workflow } from "lucide-react";
import { useLang } from "@/lib/lang-context";
import { SectionHead } from "./Features";

export default function Architecture() {
  const { t } = useLang();
  return (
    <section id="tech" className="scroll-mt-16 border-t border-line">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <SectionHead title={t.tech.title} sub={t.tech.sub} />

        <div className="mt-12 rounded-2xl border border-line p-5 sm:p-8">
          <div className="flex flex-col items-stretch gap-3 lg:flex-row lg:items-center">
            <Node icon={<User size={16} />} label={t.tech.you} />
            <Flow />
            <Node icon={<Workflow size={16} />} label={t.tech.orch} strong />
            <Flow label={t.tech.bus} />
            <div className="grid flex-[2] grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-1">
              {t.tech.agents.map((a, i) => (
                <div
                  key={a}
                  className="flex items-center gap-2 rounded-lg border border-line bg-white px-3 py-2 text-[13px] text-ink"
                >
                  <span className="pulse h-1.5 w-1.5 rounded-full bg-primary" style={{ animationDelay: `${i * 0.3}s` }} />
                  {a}
                </div>
              ))}
            </div>
            <Flow />
            <div className="flex flex-col items-center gap-1.5">
              <Node icon={<Gavel size={16} />} label={t.tech.judge} accent />
              <span className="text-[11.5px] text-muted">↺ {t.tech.retry}</span>
            </div>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          {["Next.js", "FastAPI", "LangGraph", "Apache Kafka", "A2A protocol", "LLM-as-Judge", "Postgres + pgvector", "OpenTelemetry"].map(
            (s) => (
              <span key={s} className="inline-flex items-center gap-1.5 rounded-full border border-line px-3 py-1.5 font-mono text-[12px] text-ink">
                <Network size={12} className="text-muted" /> {s}
              </span>
            ),
          )}
        </div>
      </div>
    </section>
  );
}

function Node({ icon, label, strong, accent }: { icon: React.ReactNode; label: string; strong?: boolean; accent?: boolean }) {
  const cls = strong
    ? "bg-ink text-white border-ink"
    : accent
      ? "bg-accent/10 text-accent-dark border-accent/30"
      : "bg-white text-ink border-line";
  return (
    <div className={`flex flex-1 items-center justify-center gap-2 rounded-xl border px-4 py-3 text-[14px] font-medium ${cls}`}>
      {icon}
      {label}
    </div>
  );
}

function Flow({ label }: { label?: string }) {
  return (
    <div className="flex shrink-0 flex-col items-center justify-center gap-1 lg:w-24">
      {label && <span className="font-mono text-[11px] text-muted">{label}</span>}
      <div className="flow relative h-6 w-px overflow-hidden bg-line lg:h-px lg:w-full" />
    </div>
  );
}
