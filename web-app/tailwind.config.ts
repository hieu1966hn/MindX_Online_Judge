import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{ts,tsx}",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e",
        },
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
