/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // ── Persian Green brand palette ───────────────────────────────────
        // CSS channel format keeps Tailwind /opacity modifiers working.
        pg: {
          50: "rgb(248 245 255 / <alpha-value>)", // #F8F5FF  lightest mint
          100: "rgb(239 235 252 / <alpha-value>)", // #EFEBFC  soft mint bg
          200: "rgb(213 200 241 / <alpha-value>)", // #D5C8F1
          300: "rgb(184 162 228 / <alpha-value>)", // #B8A2E4
          400: "rgb(169 138 223 / <alpha-value>)", // #A98ADF
          500: "rgb(118 83 220 / <alpha-value>)", // #7653DC  Persian Green PRIMARY
          600: "rgb(0 143 122 / <alpha-value>)", // #6544C2  darker hover
          700: "rgb(88 64 146 / <alpha-value>)", // #584092  Deep Emerald
          800: "rgb(53 39 79 / <alpha-value>)", // #35274F  Dark Green
          900: "rgb(2 44 34 / <alpha-value>)", // #022C22  deepest
        },
        // ── Gold accent ───────────────────────────────────────────────────
        gold: {
          300: "rgb(231 189 120 / <alpha-value>)", // #E7BD78
          400: "rgb(201 168 106 / <alpha-value>)", // #C9A86A  Champagne Gold
          500: "rgb(178 142 85 / <alpha-value>)", // #B28E55
        },
        // ── Surface ───────────────────────────────────────────────────────
        surface: {
          page: "rgb(245 245 252 / <alpha-value>)", // #F5F5FC  main bg
          ivory: "rgb(255 254 247 / <alpha-value>)", // #FAF9FF  ivory white
          sidebar: "rgb(255 255 255 / <alpha-value>)", // #FFFFFF  sidebar
          card: "rgb(255 255 255 / <alpha-value>)", // #FFFFFF
          mint: "rgb(239 235 252 / <alpha-value>)", // #EFEBFC  soft mint hover/bg
          bg: "rgb(245 245 252 / <alpha-value>)",
          hover: "rgb(239 235 252 / <alpha-value>)",
          teal: "rgb(248 245 255 / <alpha-value>)",
        },
        // ── Ink ───────────────────────────────────────────────────────────
        ink: {
          900: "rgb(37 40 66 / <alpha-value>)", // #252842  primary text
          700: "rgb(40 72 62 / <alpha-value>)", // #514662
          600: "rgb(124 129 151 / <alpha-value>)", // #7C8197  secondary text
          400: "rgb(148 166 158 / <alpha-value>)", // #AAA2B8  placeholder
          border: "rgb(230 224 241 / <alpha-value>)", // #E6E0F1  borders
          primary: "rgb(37 40 66 / <alpha-value>)",
          secondary: "rgb(124 129 151 / <alpha-value>)",
        },
        // ── State ─────────────────────────────────────────────────────────
        success: "rgb(5 150 105 / <alpha-value>)", // #059669
        danger: "rgb(220 38 38 / <alpha-value>)", // #DC2626
        warning: "rgb(217 119 6 / <alpha-value>)", // #D97706
        // Compatibility aliases for existing components, mapped to the new theme.
        brand: {
          blue: "rgb(118 83 220 / <alpha-value>)",
          "blue-dark": "rgb(88 64 146 / <alpha-value>)",
          teal: "rgb(118 83 220 / <alpha-value>)",
          "teal-dark": "rgb(88 64 146 / <alpha-value>)",
        },
        state: {
          success: "rgb(5 150 105 / <alpha-value>)",
          error: "rgb(220 38 38 / <alpha-value>)",
        },
      },
      fontFamily: {
        sans: ["Inter", "'Plus Jakarta Sans'", "system-ui", "sans-serif"],
      },
      borderRadius: {
        "2xl": "16px",
        "3xl": "24px",
        "4xl": "32px",
      },
      animation: {
        "fade-in": "fadeIn 0.2s ease",
        "slide-up": "slideUp 0.3s cubic-bezier(0.16,1,0.3,1)",
        "scale-in": "scaleIn 0.25s cubic-bezier(0.16,1,0.3,1)",
        shimmer: "shimmer 1.8s linear infinite",
        spin: "spin 0.8s linear infinite",
      },
      keyframes: {
        fadeIn: { "0%": { opacity: 0 }, "100%": { opacity: 1 } },
        slideUp: {
          "0%": { opacity: 0, transform: "translateY(12px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        scaleIn: {
          "0%": { opacity: 0, transform: "scale(0.96)" },
          "100%": { opacity: 1, transform: "scale(1)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      boxShadow: {
        xs: "0 1px 2px rgb(0 0 0 / 0.05)",
        sm: "0 1px 3px rgb(0 0 0 / 0.08), 0 1px 2px rgb(0 0 0 / 0.04)",
        md: "0 4px 12px rgb(0 0 0 / 0.08), 0 2px 4px rgb(0 0 0 / 0.04)",
        lg: "0 8px 24px rgb(0 0 0 / 0.10), 0 3px 6px rgb(0 0 0 / 0.04)",
        xl: "0 16px 48px rgb(0 0 0 / 0.12), 0 4px 12px rgb(0 0 0 / 0.06)",
        green: "0 4px 14px rgb(118 83 220 / 0.25)",
        "green-lg": "0 8px 24px rgb(118 83 220 / 0.30)",
        focus: "0 0 0 3px rgb(118 83 220 / 0.20)",
        card: "0 1px 3px rgb(0 0 0 / 0.06), 0 1px 2px rgb(0 0 0 / 0.04)",
        "card-md": "0 4px 12px rgb(0 0 0 / 0.08), 0 2px 4px rgb(0 0 0 / 0.04)",
      },
    },
  },
  plugins: [],
};
