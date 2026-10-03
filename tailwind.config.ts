/** @type {import('tailwindcss').Config} */
export default {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}", "./lib/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          50: "oklch(0.97 0.01 195)",
          100: "oklch(0.94 0.02 195)",
          200: "oklch(0.88 0.03 195)",
          300: "oklch(0.78 0.05 195)",
          400: "oklch(0.62 0.08 195)",
          500: "oklch(0.52 0.1 195)",
          600: "oklch(0.42 0.1 195)",
          700: "oklch(0.32 0.1 195)",
          800: "oklch(0.26 0.08 195)",
          900: "oklch(0.2 0.06 195)",
          950: "oklch(0.15 0.04 195)",
        },
        accent: {
          500: "#F5A623",
          600: "#D4891A",
        },
        neutral: {
          50: "#FAFAFA",
          100: "#F5F5F5",
          200: "#E5E5E5",
          300: "#D4D4D4",
          400: "#A3A3A3",
          500: "#737373",
          600: "#525252",
          700: "#404040",
          800: "#262626",
          900: "#171717",
          950: "#0A0A0A",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        serif: ["Georgia", "Times New Roman", "serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      fontSize: {
        "display-xl": ["4.5rem", { lineHeight: "1.1", letterSpacing: "-0.02em", fontWeight: "700" }],
        "display-lg": ["3.75rem", { lineHeight: "1.1", letterSpacing: "-0.02em", fontWeight: "700" }],
        "display-md": ["3rem", { lineHeight: "1.2", letterSpacing: "-0.01em", fontWeight: "600" }],
        "display-sm": ["2.25rem", { lineHeight: "1.2", letterSpacing: "-0.01em", fontWeight: "600" }],
      },
      borderRadius: {
        xl: "0.75rem",
        "2xl": "1rem",
      },
      boxShadow: {
        card: "0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)",
        elevation: "0 4px 12px 0 rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.04)",
        modal: "0 20px 60px -12px rgb(0 0 0 / 0.15)",
      },
    },
  },
  plugins: [],
};
