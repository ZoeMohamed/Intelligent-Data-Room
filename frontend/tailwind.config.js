/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        surface: "#f5f7ff",
        panel: "#ffffff",
        border: "#d9e1f2",
        muted: "#62708a",
        accent: "#2f5bff",
        accentSoft: "#e6edff",
        emerald: "#34d399"
      },
      fontFamily: {
        display: ['"Outfit"', "sans-serif"],
        body: ['"Manrope"', "sans-serif"]
      },
      boxShadow: {
        soft: "0 20px 50px rgba(34, 61, 140, 0.15)",
        glow: "0 0 0 1px rgba(47, 91, 255, 0.2), 0 12px 24px rgba(47, 91, 255, 0.18)"
      }
    }
  },
  plugins: []
}
