// An open door: the frame, and a door leaf swung inward.
export default function Logo({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden>
      <rect width="32" height="32" rx="9" fill="var(--ink)" />
      <path d="M10 25V8.5a1.5 1.5 0 0 1 1.5-1.5h9A1.5 1.5 0 0 1 22 8.5V25" stroke="white" strokeWidth="2" strokeLinecap="round" />
      <path d="M10 25l7-2.5V9.2L10 7" fill="var(--primary)" />
      <circle cx="15" cy="16.5" r="1" fill="white" />
      <path d="M7 25h18" stroke="white" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
