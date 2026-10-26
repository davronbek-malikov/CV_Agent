export const GATEWAY = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8000";

export type Chip = { value: string; label: string; action?: string; slot?: string };

export type Reply = {
  type: "reply";
  kind: "question" | "status" | "text" | "error" | "jobs" | "brief" | "interview_q" | "score" | "report" | "roadmap";
  text?: string;
  slot?: string;
  chips?: Chip[];
  data?: any; // eslint-disable-line @typescript-eslint/no-explicit-any
  lang?: string | null;
  trace_id: string;
  at: string;
};

export type AgentEvent = {
  type: "event";
  agent: string;
  status: "started" | "progress" | "done" | "error" | "verdict";
  text: string;
  verdict?: "PASS" | "RETRY" | "FAIL";
  at: string;
  trace_id: string;
};

export async function health(): Promise<{ status: string; llm: string } | null> {
  try {
    const r = await fetch(`${GATEWAY}/health`, { signal: AbortSignal.timeout(2500) });
    return r.ok ? r.json() : null;
  } catch {
    return null;
  }
}

export async function newSession(): Promise<string> {
  const r = await fetch(`${GATEWAY}/api/session`, { method: "POST" });
  return (await r.json()).session_id;
}

export async function sendChat(sessionId: string, text: string | null, action: Record<string, unknown> | null) {
  await fetch(`${GATEWAY}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, text, action }),
  });
}

export async function uploadCv(sessionId: string, file: File) {
  const fd = new FormData();
  fd.append("session_id", sessionId);
  fd.append("file", file);
  const r = await fetch(`${GATEWAY}/api/cv`, { method: "POST", body: fd });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `Upload failed (${r.status})`);
  return r.json();
}
