import { Globe } from "lucide-react";

// Inline flags: Windows does not render flag emoji.
export default function Flag({ code, size = 14 }: { code: "UZ" | "KR" | "GL"; size?: number }) {
  const h = Math.round(size * 0.7);
  if (code === "GL") return <Globe size={size} strokeWidth={1.8} className="text-muted" aria-label="Worldwide" />;
  return (
    <svg width={size} height={h} viewBox="0 0 20 14" className="shrink-0 rounded-[2px] ring-1 ring-black/10" aria-label={code === "UZ" ? "Uzbekistan" : "Korea"}>
      {code === "UZ" ? (
        <>
          <rect width="20" height="14" fill="#fff" />
          <rect width="20" height="4.4" fill="#0099B5" />
          <rect y="9.6" width="20" height="4.4" fill="#1EB53A" />
          <rect y="4.4" width="20" height="0.5" fill="#CE1126" />
          <rect y="9.1" width="20" height="0.5" fill="#CE1126" />
        </>
      ) : (
        <>
          <rect width="20" height="14" fill="#fff" />
          <path d="M7 7a3 3 0 0 1 6 0" fill="#CD2E3A" />
          <path d="M7 7a3 3 0 0 0 6 0" fill="#0047A0" />
          <g stroke="#000" strokeWidth="0.6">
            <path d="M2.5 3.2l1.6-1.4M3.1 3.9l1.6-1.4M15.3 1.8l1.6 1.4M15.9 2.5l1.6 1.4M2.5 10.8l1.6 1.4M15.3 12.2l1.6-1.4M15.9 11.5l1.6-1.4" />
          </g>
        </>
      )}
    </svg>
  );
}
