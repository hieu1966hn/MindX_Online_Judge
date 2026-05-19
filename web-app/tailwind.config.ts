import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{ts,tsx}",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Verdict colors for the judge results
        verdict: {
          ac: "#16a34a",   // green-600 — Accepted
          wa: "#dc2626",   // red-600   — Wrong Answer
          tle: "#ea580c",  // orange-600 — Time Limit Exceeded
          re: "#9333ea",   // purple-600 — Runtime Error
          ce: "#4b5563",   // gray-600  — Compile Error
          pd: "#2563eb",   // blue-600  — Pending
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
    },
  },
  plugins: [],
  darkMode: "class",
};

export default config;
