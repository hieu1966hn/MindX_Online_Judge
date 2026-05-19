import type { Verdict } from "@/types";

/**
 * VerdictBadge Component
 * 
 * Displays a submission verdict with appropriate color coding:
 * - AC (Accepted): Green
 * - WA (Wrong Answer): Red
 * - TLE (Time Limit Exceeded): Orange
 * - RE (Runtime Error): Purple
 * - CE (Compilation Error): Gray
 * - PD (Pending): Blue
 */

interface VerdictBadgeProps {
  verdict: Verdict;
  className?: string;
}

const VERDICT_CONFIG: Record<Verdict, { label: string; className: string }> = {
  AC: { label: "Accepted", className: "verdict-badge verdict-ac" },
  WA: { label: "Wrong Answer", className: "verdict-badge verdict-wa" },
  TLE: { label: "Time Limit", className: "verdict-badge verdict-tle" },
  RE: { label: "Runtime Error", className: "verdict-badge verdict-re" },
  CE: { label: "Compile Error", className: "verdict-badge verdict-ce" },
  PD: { label: "Pending", className: "verdict-badge verdict-pd" },
};

export default function VerdictBadge({ verdict, className = "" }: VerdictBadgeProps) {
  const config = VERDICT_CONFIG[verdict];

  return (
    <span className={`${config.className} ${className}`}>
      <span className="font-mono font-bold">{verdict}</span>
      <span className="hidden sm:inline">— {config.label}</span>
    </span>
  );
}
