"use client";

import { LangProvider } from "@/lib/lang-context";
import ChatApp from "@/components/app/ChatApp";

export default function AppPage() {
  return (
    <LangProvider>
      <ChatApp />
    </LangProvider>
  );
}
