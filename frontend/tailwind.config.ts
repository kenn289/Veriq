import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "var(--veriq-ink)",
        paper: "var(--veriq-paper)",
        mint: "var(--veriq-mint)",
        amber: "var(--veriq-amber)",
        clay: "var(--veriq-clay)",
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        serif: ["Source Serif 4", "serif"],
      },
      boxShadow: {
        glow: "0 0 40px rgba(20, 184, 166, 0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
