"use client";

import { useLang } from "@/lib/lang-context";
import Logo from "./Logo";

export default function Footer() {
  const { t } = useLang();
  return (
    <footer className="border-t border-line">
      <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-4 px-4 py-10 sm:flex-row sm:items-center sm:px-6">
        <div className="flex items-center gap-2.5">
          <Logo size={24} />
          <span className="text-[14px] font-semibold text-ink">Portiq</span>
          <span className="text-[13px] text-muted">· {t.footer.made}</span>
        </div>
        <a
          href="https://github.com/davronbek-malikov/CV_Agent"
          target="_blank"
          rel="noreferrer"
          className="text-[13px] text-muted transition hover:text-ink"
        >
          {t.footer.repo} ↗
        </a>
      </div>
    </footer>
  );
}
