"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Activity, ArrowUp, Loader2, Paperclip, Plus, Sparkles, Terminal } from "lucide-react";
import { useLang } from "@/lib/lang-context";
import { LANGS, type Lang } from "@/lib/i18n";
import { GATEWAY, health, newSession, sendChat, uploadCv, type AgentEvent, type Chip, type Reply } from "@/lib/gateway";
import Logo from "../Logo";
import { Brief, InterviewQ, Jobs, Report, Roadmap, Score } from "./Blocks";

type Item = { id: number; from: "user" | "bot"; text?: string; reply?: Reply };

const AGENT_COLOR: Record<string, string> = {
  orchestrator: "#0f172a", judge: "#10b981", match: "#2563eb", company_research: "#7c3aed", interviewer: "#db2777",
  roadmap: "#ea580c", profile: "#0891b2", gateway: "#64748b",
};

export default function ChatApp() {
  const { t, lang, setLang } = useLang();
  const [state, setState] = useState<"checking" | "offline" | "ready">("checking");
  const [llm, setLlm] = useState("");
  const [sid, setSid] = useState("");
  const [items, setItems] = useState<Item[]>([]);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [input, setInput] = useState("");
  const [waiting, setWaiting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showActivity, setShowActivity] = useState(false);
  const seq = useRef(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const push = (it: Omit<Item, "id">) => setItems((prev) => [...prev, { ...it, id: ++seq.current }]);

  const start = useCallback(async () => {
    setState("checking");
    const h = await health();
    if (!h) return setState("offline");
    setLlm(h.llm);
    const id = await newSession();
    setItems([]);
    setEvents([]);
    setSid(id);
    setState("ready");
  }, []);

  useEffect(() => {
    start();
  }, [start]);

  // One SSE stream per session: replies go to the chat, events to the activity panel.
  useEffect(() => {
    if (!sid) return;
    const es = new EventSource(`${GATEWAY}/api/stream/${sid}`);
    es.onopen = () => {
      setWaiting(true);
      sendChat(sid, null, { type: "start" });
    };
    es.onmessage = (m) => {
      const d = JSON.parse(m.data);
      if (d.type === "reply") {
        const r = d as Reply;
        if (r.lang && LANGS.some((l) => l.code === r.lang)) setLang(r.lang as Lang);
        setWaiting(r.kind === "status");
        push({ from: "bot", reply: r });
      } else {
        setEvents((prev) => [...prev.slice(-80), d as AgentEvent]);
      }
    };
    return () => es.close();
  }, [sid, setLang]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [items, waiting]);

  async function act(chip: Chip) {
    if (chip.action === "lang") setLang(chip.value as Lang);
    push({ from: "user", text: chip.label });
    setWaiting(true);
    await sendChat(sid, null, { type: chip.action || "choose", slot: chip.slot, value: chip.value });
  }

  async function practice(job: { company?: string; title: string }) {
    push({ from: "user", text: `${t.app.practice}: ${job.company || job.title}` });
    setWaiting(true);
    await sendChat(sid, null, { type: "practice", company: job.company || job.title });
  }

  async function send(e?: React.FormEvent) {
    e?.preventDefault();
    const text = input.trim();
    if (!text || !sid) return;
    setInput("");
    push({ from: "user", text });
    setWaiting(true);
    await sendChat(sid, text, null);
  }

  async function onFile(f: File | undefined) {
    if (!f || !sid) return;
    setUploading(true);
    push({ from: "user", text: `📎 ${f.name}` });
    try {
      const res = await uploadCv(sid, f);
      push({ from: "bot", text: `${t.app.uploaded}: ${res.profile.skills.join(", ") || "—"}` });
    } catch (err) {
      push({ from: "bot", text: String((err as Error).message) });
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  const lastQuestionId = [...items].reverse().find((i) => i.reply?.chips?.length)?.id;

  return (
    <div className="flex h-dvh flex-col bg-white">
      <header className="flex h-14 shrink-0 items-center justify-between gap-3 border-b border-line px-4">
        <Link href="/" className="flex items-center gap-2">
          <Logo size={26} />
          <span className="text-[15px] font-semibold tracking-tight text-ink">Portiq</span>
        </Link>
        <div className="flex items-center gap-2">
          {llm && (
            <span className="hidden rounded-full border border-line px-2 py-0.5 font-mono text-[11px] text-muted sm:inline" title="LLM provider">
              LLM: {llm}
            </span>
          )}
          <button onClick={() => setShowActivity((v) => !v)} className="grid h-8 w-8 place-items-center rounded-full border border-line text-muted lg:hidden" aria-label={t.app.activity}>
            <Activity size={15} />
          </button>
          <button onClick={start} className="hidden h-8 items-center gap-1 rounded-full border border-line px-3 text-[12px] text-muted hover:text-ink sm:flex">
            <Plus size={13} /> {t.app.newChat}
          </button>
          <div className="flex rounded-full border border-line p-0.5">
            {LANGS.map((l) => (
              <button key={l.code} onClick={() => setLang(l.code)}
                className={`h-7 min-w-8 rounded-full px-2 text-[12px] font-medium ${lang === l.code ? "bg-ink text-white" : "text-muted hover:text-ink"}`}>
                {l.short}
              </button>
            ))}
          </div>
        </div>
      </header>

      {state === "offline" ? (
        <Offline onRetry={start} />
      ) : (
        <div className="flex min-h-0 flex-1">
          {/* Chat */}
          <main className="flex min-w-0 flex-1 flex-col">
            <div ref={scrollRef} className="flex-1 overflow-y-auto" aria-live="polite">
              <div className="mx-auto max-w-2xl space-y-3 px-4 py-6">
                {state === "checking" && <Loader2 className="mx-auto animate-spin text-muted" />}
                {items.map((it) =>
                  it.from === "user" ? (
                    <div key={it.id} className="flex justify-end fade-up">
                      <div className="max-w-[80%] rounded-2xl rounded-tr-md bg-primary px-3.5 py-2.5 text-[14px] text-white">{it.text}</div>
                    </div>
                  ) : (
                    <BotItem key={it.id} item={it} active={it.id === lastQuestionId} onChip={act} onPractice={practice} />
                  ),
                )}
                {waiting && (
                  <div className="flex items-center gap-2 pl-9 text-[12.5px] text-muted">
                    <span className="flex gap-1">
                      {[0, 1, 2].map((i) => <span key={i} className="dot h-1.5 w-1.5 rounded-full bg-muted" style={{ animationDelay: `${i * 0.15}s` }} />)}
                    </span>
                  </div>
                )}
              </div>
            </div>
            <form onSubmit={send} className="border-t border-line p-3">
              <div className="mx-auto flex max-w-2xl items-center gap-2">
                <input ref={fileRef} type="file" accept=".pdf,.docx,.txt" hidden onChange={(e) => onFile(e.target.files?.[0])} />
                <button type="button" onClick={() => fileRef.current?.click()} disabled={uploading || state !== "ready"}
                  title={t.app.upload} aria-label={t.app.upload}
                  className="grid h-11 w-11 shrink-0 place-items-center rounded-xl border border-line text-muted hover:text-ink disabled:opacity-40">
                  {uploading ? <Loader2 size={17} className="animate-spin" /> : <Paperclip size={17} />}
                </button>
                <input value={input} onChange={(e) => setInput(e.target.value)} placeholder={t.app.placeholder} disabled={state !== "ready"}
                  className="h-11 min-w-0 flex-1 rounded-xl bg-surface px-4 text-[14px] text-ink outline-none ring-primary/30 placeholder:text-muted focus:ring-2" />
                <button type="submit" disabled={!input.trim()} aria-label="Send"
                  className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-primary text-white hover:bg-primary-dark disabled:opacity-30">
                  <ArrowUp size={18} />
                </button>
              </div>
            </form>
          </main>

          {/* Activity */}
          <aside className={`${showActivity ? "fixed inset-x-0 bottom-0 top-14 z-20 flex" : "hidden"} w-full flex-col border-l border-line bg-white lg:static lg:flex lg:w-[340px]`}>
            <div className="flex items-center justify-between border-b border-line px-4 py-3">
              <p className="flex items-center gap-2 text-[13px] font-semibold text-ink">
                <span className="pulse h-1.5 w-1.5 rounded-full bg-accent" /> {t.app.activity}
              </p>
              <span className="font-mono text-[11px] text-muted">{events.length}</span>
            </div>
            <ol className="flex-1 space-y-2 overflow-y-auto p-4">
              {events.length === 0 && <p className="text-[12.5px] text-muted">{t.app.noActivity}</p>}
              {[...events].reverse().map((e, i) => (
                <li key={i} className="fade-up rounded-lg border border-line p-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="flex items-center gap-1.5 font-mono text-[11.5px] font-medium" style={{ color: AGENT_COLOR[e.agent] || "#475569" }}>
                      <span className="h-1.5 w-1.5 rounded-full" style={{ background: AGENT_COLOR[e.agent] || "#94a3b8" }} />
                      {e.agent}
                    </span>
                    {e.verdict ? (
                      <span className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                        e.verdict === "PASS" ? "bg-accent/10 text-accent-dark" : e.verdict === "RETRY" ? "bg-warning/10 text-warning-dark" : "bg-red-50 text-red-600"
                      }`}>{e.verdict}</span>
                    ) : (
                      <span className="text-[10.5px] text-muted">{e.status}</span>
                    )}
                  </div>
                  <p className="mt-1 text-[12px] leading-snug text-ink">{e.text}</p>
                </li>
              ))}
            </ol>
          </aside>
        </div>
      )}
    </div>
  );
}

function BotItem({ item, active, onChip, onPractice }: {
  item: Item; active: boolean; onChip: (c: Chip) => void; onPractice: (j: { company?: string; title: string }) => void;
}) {
  const { t } = useLang();
  const r = item.reply;
  if (!r) return <Bubble>{item.text}</Bubble>;
  if (r.kind === "status") return <p className="pl-9 text-[12.5px] italic text-muted fade-up">{r.text}</p>;

  const body = (() => {
    switch (r.kind) {
      case "jobs":
        return <><p className="mb-2 text-[13px] font-semibold text-ink">{r.text}</p><Jobs data={r.data} t={t} onPractice={onPractice} /></>;
      case "brief":
        return <Brief data={r.data} t={t} />;
      case "interview_q":
        return <InterviewQ reply={r} t={t} />;
      case "score":
        return <Score data={r.data} t={t} />;
      case "report":
        return <Report reply={r} t={t} />;
      case "roadmap":
        return <Roadmap data={r.data} t={t} />;
      default:
        return null;
    }
  })();

  return (
    <div className="space-y-2.5 fade-up">
      {body ? <div className="pl-9">{body}</div> : <Bubble error={r.kind === "error"}>{r.text}</Bubble>}
      {!!r.chips?.length && (
        <div className="flex flex-wrap gap-2 pl-9">
          {r.chips.map((c) => (
            <button key={c.value + c.label} onClick={() => onChip(c)} disabled={!active} className="chip disabled:pointer-events-none disabled:opacity-40">
              {c.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function Bubble({ children, error }: { children: React.ReactNode; error?: boolean }) {
  return (
    <div className="flex items-start gap-2.5 fade-up">
      <div className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full bg-ink text-white">
        <Sparkles size={13} />
      </div>
      <div className={`max-w-[85%] rounded-2xl rounded-tl-md px-3.5 py-2.5 text-[14px] leading-relaxed ${error ? "bg-red-50 text-red-700" : "bg-surface text-ink"}`}>
        {children}
      </div>
    </div>
  );
}

function Offline({ onRetry }: { onRetry: () => void }) {
  const { t } = useLang();
  return (
    <div className="grid flex-1 place-items-center px-4">
      <div className="max-w-md text-center">
        <div className="mx-auto mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-surface text-muted">
          <Terminal size={22} />
        </div>
        <h1 className="text-[18px] font-semibold text-ink">{t.app.offline}</h1>
        <p className="mt-2 text-[14px] leading-relaxed text-muted">{t.app.offlineHint}</p>
        <pre className="mt-4 overflow-x-auto rounded-xl bg-ink p-4 text-left font-mono text-[12.5px] leading-relaxed text-white">
{`git clone https://github.com/davronbek-malikov/CV_Agent
cd CV_Agent && make up
cd apps/web && pnpm dev   # → localhost:3000/app`}
        </pre>
        <div className="mt-5 flex justify-center gap-3">
          <button onClick={onRetry} className="btn-ghost">{t.app.retry}</button>
          <Link href="/#demo" className="btn-primary">{t.nav.demo}</Link>
        </div>
      </div>
    </div>
  );
}
