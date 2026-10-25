"use client";

import { useLang } from "@/lib/lang-context";
import { LANGS } from "@/lib/i18n";
import Logo from "./Logo";

export default function Header() {
  const { t, lang, setLang } = useLang();
  const links = [
    ["#features", t.nav.features],
    ["#demo", t.nav.demo],
    ["#compare", t.nav.compare],
    ["#tech", t.nav.tech],
  ];
  return (
    <header className="sticky top-0 z-30 border-b border-line/70 bg-white/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        <a href="#top" className="flex items-center gap-2" aria-label="Darvoza home">
          <Logo />
          <span className="text-[17px] font-semibold tracking-tight text-ink">Darvoza</span>
        </a>
        <nav className="hidden items-center gap-7 md:flex">
          {links.map(([href, label]) => (
            <a key={href} href={href} className="text-[14px] text-muted transition hover:text-ink">
              {label}
            </a>
          ))}
        </nav>
        <div className="flex rounded-full border border-line p-0.5" role="group" aria-label="Language">
          {LANGS.map((l) => (
            <button
              key={l.code}
              onClick={() => setLang(l.code)}
              aria-pressed={lang === l.code}
              title={l.label}
              className={`h-7 min-w-8 rounded-full px-2 text-[12px] font-medium transition ${
                lang === l.code ? "bg-ink text-white" : "text-muted hover:text-ink"
              }`}
            >
              {l.short}
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}
