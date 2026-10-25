// Sample data for the Phase 1 demo. Companies are fictional.

export type Region = "UZ" | "KR" | "GL";
export type Scope = "uz" | "kr" | "multi" | "all" | "remote";
export type Role = "dev" | "data" | "design" | "marketing";

export type Job = {
  title: string;
  company: string;
  city: string;
  region: Region;
  remote: boolean;
  role: Role;
  salary: string;
  match: number;
  risk: "safe" | "check";
  have: string[];
  miss: string;
  source: string;
};

export const JOBS: Job[] = [
  { title: "Backend Developer", company: "PayLink", city: "Tashkent", region: "UZ", remote: false, role: "dev", salary: "12–18M so‘m", match: 88, risk: "safe", have: ["Python", "FastAPI", "SQL"], miss: "Kafka", source: "hh.uz" },
  { title: "Junior Python Developer", company: "Telegram post", city: "Tashkent", region: "UZ", remote: false, role: "dev", salary: "8–10M so‘m", match: 74, risk: "check", have: ["Python", "Git"], miss: "Docker", source: "Telegram" },
  { title: "Data Analyst", company: "Agro Data Lab", city: "Samarkand", region: "UZ", remote: false, role: "data", salary: "9–13M so‘m", match: 81, risk: "safe", have: ["SQL", "Excel", "Python"], miss: "Power BI", source: "IT Market" },
  { title: "Product Designer", company: "Bazaar Online", city: "Tashkent", region: "UZ", remote: false, role: "design", salary: "10–15M so‘m", match: 79, risk: "safe", have: ["Figma", "UX research"], miss: "Design systems", source: "hh.uz" },
  { title: "SMM Specialist", company: "EduStart", city: "Tashkent", region: "UZ", remote: false, role: "marketing", salary: "7–9M so‘m", match: 76, risk: "safe", have: ["Content", "Instagram"], miss: "Analytics", source: "Telegram" },
  { title: "Backend Engineer (E-7)", company: "Cloudnine Korea", city: "Seoul", region: "KR", remote: false, role: "dev", salary: "4.2–5M ₩", match: 84, risk: "safe", have: ["Python", "Docker", "AWS"], miss: "Korean (TOPIK 4)", source: "Saramin" },
  { title: "ML Engineer", company: "Hanbit AI", city: "Pangyo", region: "KR", remote: false, role: "data", salary: "4.5–6M ₩", match: 80, risk: "safe", have: ["PyTorch", "Python"], miss: "MLOps", source: "Wanted" },
  { title: "UI Designer", company: "Mint Studio", city: "Seoul", region: "KR", remote: false, role: "design", salary: "3.3–4M ₩", match: 72, risk: "safe", have: ["Figma"], miss: "Korean (TOPIK 3)", source: "Work24" },
  { title: "Global Marketing Manager", company: "K-Beauty Co.", city: "Seoul", region: "KR", remote: false, role: "marketing", salary: "3.8–4.5M ₩", match: 78, risk: "safe", have: ["English", "Russian", "SEO"], miss: "Korean (TOPIK 4)", source: "Saramin" },
  { title: "Python Developer", company: "Remotely Inc.", city: "Remote", region: "GL", remote: true, role: "dev", salary: "$2,500–3,500", match: 82, risk: "safe", have: ["Python", "REST", "Git"], miss: "System design", source: "Remotive" },
  { title: "Data Scientist", company: "Northwind Analytics", city: "Remote", region: "GL", remote: true, role: "data", salary: "$3,000–4,200", match: 77, risk: "safe", have: ["Python", "Statistics"], miss: "Spark", source: "Adzuna" },
  { title: "UX Designer", company: "Brightside", city: "Remote", region: "GL", remote: true, role: "design", salary: "$2,200–3,000", match: 75, risk: "safe", have: ["Figma", "Prototyping"], miss: "Usability testing", source: "Jooble" },
  { title: "Growth Marketer", company: "Launchpad", city: "Berlin", region: "GL", remote: false, role: "marketing", salary: "€3,500–4,200", match: 70, risk: "safe", have: ["Ads", "Analytics"], miss: "German (B1)", source: "Adzuna" },
];

export function pickJobs(scope: Scope, role: Role | null): Job[] {
  const inScope = JOBS.filter((j) => {
    if (scope === "uz") return j.region === "UZ";
    if (scope === "kr") return j.region === "KR";
    if (scope === "multi") return j.region === "UZ" || j.region === "KR";
    if (scope === "remote") return j.remote;
    return true;
  });
  const sameRole = inScope.filter((j) => !role || j.role === role);
  const pool = sameRole.length >= 2 ? sameRole : inScope;
  return [...pool].sort((a, b) => b.match - a.match).slice(0, 3);
}

export function salaryChips(scope: Scope): string[] {
  if (scope === "uz") return ["8M so‘m", "12M so‘m", "18M+ so‘m"];
  if (scope === "kr") return ["3M ₩", "4M ₩", "5M+ ₩"];
  return ["$1,500", "$3,000", "$5,000+"];
}

// Feature comparison. y = yes, p = partial, n = not found in public reviews.
export type Mark = "y" | "p" | "n";
export type RowKey =
  | "match" | "why" | "cv" | "mock" | "company" | "stress" | "roadmap"
  | "uz" | "kr" | "tg" | "scam" | "lang" | "judge";
export type Category = "find" | "practice" | "learn" | "local";

export const ROWS: { key: RowKey; cat: Category }[] = [
  { key: "match", cat: "find" },
  { key: "why", cat: "find" },
  { key: "cv", cat: "find" },
  { key: "mock", cat: "practice" },
  { key: "company", cat: "practice" },
  { key: "stress", cat: "practice" },
  { key: "roadmap", cat: "learn" },
  { key: "uz", cat: "local" },
  { key: "kr", cat: "local" },
  { key: "tg", cat: "local" },
  { key: "scam", cat: "find" },
  { key: "lang", cat: "local" },
  { key: "judge", cat: "practice" },
];

export const TOOLS: { name: string; url: string; marks: Record<RowKey, Mark> }[] = [
  {
    name: "Darvoza",
    url: "#demo",
    marks: { match: "y", why: "y", cv: "p", mock: "y", company: "y", stress: "y", roadmap: "y", uz: "y", kr: "y", tg: "y", scam: "y", lang: "y", judge: "y" },
  },
  {
    name: "Jobscan",
    url: "https://www.jobscan.co",
    marks: { match: "y", why: "p", cv: "y", mock: "p", company: "n", stress: "n", roadmap: "n", uz: "n", kr: "n", tg: "n", scam: "n", lang: "n", judge: "n" },
  },
  {
    name: "Teal",
    url: "https://www.tealhq.com",
    marks: { match: "p", why: "n", cv: "y", mock: "n", company: "n", stress: "n", roadmap: "n", uz: "n", kr: "n", tg: "n", scam: "n", lang: "n", judge: "n" },
  },
  {
    name: "Final Round AI",
    url: "https://www.finalroundai.com",
    marks: { match: "n", why: "n", cv: "n", mock: "y", company: "n", stress: "n", roadmap: "n", uz: "n", kr: "n", tg: "n", scam: "n", lang: "n", judge: "n" },
  },
  {
    name: "Big Interview",
    url: "https://www.biginterview.com",
    marks: { match: "n", why: "n", cv: "n", mock: "y", company: "n", stress: "n", roadmap: "n", uz: "n", kr: "n", tg: "n", scam: "n", lang: "n", judge: "n" },
  },
  {
    name: "Saramin",
    url: "https://www.saramin.co.kr",
    marks: { match: "y", why: "n", cv: "n", mock: "y", company: "p", stress: "n", roadmap: "n", uz: "n", kr: "y", tg: "n", scam: "n", lang: "p", judge: "n" },
  },
  {
    name: "Wanted",
    url: "https://www.wanted.co.kr",
    marks: { match: "y", why: "p", cv: "y", mock: "p", company: "n", stress: "n", roadmap: "n", uz: "n", kr: "y", tg: "n", scam: "n", lang: "n", judge: "n" },
  },
  {
    name: "hh.uz",
    url: "https://hh.uz",
    marks: { match: "p", why: "n", cv: "n", mock: "n", company: "n", stress: "n", roadmap: "n", uz: "y", kr: "n", tg: "n", scam: "n", lang: "p", judge: "n" },
  },
];
