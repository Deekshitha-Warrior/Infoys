/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // ── Persian Green brand palette ───────────────────────────────────
        // CSS channel format keeps Tailwind /opacity modifiers working.
        pg: {
          50:  "rgb(240 253 248 / <alpha-value>)",  // #F0FDF8  lightest mint
          100: "rgb(223 247 239 / <alpha-value>)",  // #DFF7EF  soft mint bg
          200: "rgb(167 234 211 / <alpha-value>)",  // #A7EAD3
          300: "rgb(94 211 172 / <alpha-value>)",   // #5ED3AC
          400: "rgb(52 186 152 / <alpha-value>)",   // #34BA98
          500: "rgb(0 166 147 / <alpha-value>)",    // #00A693  Persian Green PRIMARY
          600: "rgb(0 143 122 / <alpha-value>)",    // #008F7A  darker hover
          700: "rgb(6 95 70 / <alpha-value>)",      // #065F46  Deep Emerald
          800: "rgb(6 78 59 / <alpha-value>)",      // #064E3B  Dark Green
          900: "rgb(2 44 34 / <alpha-value>)",      // #022C22  deepest
        },
        // ── Gold accent ───────────────────────────────────────────────────
        gold: {
          300: "rgb(231 189 120 / <alpha-value>)",  // #E7BD78
          400: "rgb(201 168 106 / <alpha-value>)",  // #C9A86A  Champagne Gold
          500: "rgb(178 142 85 / <alpha-value>)",   // #B28E55
        },
        // ── Surface ───────────────────────────────────────────────────────
        surface: {
          page:    "rgb(247 250 248 / <alpha-value>)",  // #F7FAF8  main bg
          ivory:   "rgb(255 254 247 / <alpha-value>)",  // #FFFEF7  ivory white
          sidebar: "rgb(255 255 255 / <alpha-value>)",  // #FFFFFF  sidebar
          card:    "rgb(255 255 255 / <alpha-value>)",  // #FFFFFF
          mint:    "rgb(223 247 239 / <alpha-value>)",  // #DFF7EF  soft mint hover/bg
          bg:      "rgb(247 250 248 / <alpha-value>)",
          hover:   "rgb(223 247 239 / <alpha-value>)",
          teal:    "rgb(240 253 248 / <alpha-value>)",
        },
        // ── Ink ───────────────────────────────────────────────────────────
        ink: {
          900:    "rgb(23 43 37 / <alpha-value>)",   // #172B25  primary text
          700:    "rgb(40 72 62 / <alpha-value>)",   // #28483E
          600:    "rgb(82 100 93 / <alpha-value>)",  // #52645D  secondary text
          400:    "rgb(148 166 158 / <alpha-value>)", // #94A69E  placeholder
          border: "rgb(220 234 227 / <alpha-value>)", // #DCEAE3  borders
          primary: "rgb(23 43 37 / <alpha-value>)",
          secondary: "rgb(82 100 93 / <alpha-value>)",
        },
        // ── State ─────────────────────────────────────────────────────────
        success: "rgb(5 150 105 / <alpha-value>)",   // #059669
        danger:  "rgb(220 38 38 / <alpha-value>)",   // #DC2626
        warning: "rgb(217 119 6 / <alpha-value>)",   // #D97706
        // Compatibility aliases for existing components, mapped to the new theme.
        brand: {
          blue: "rgb(0 166 147 / <alpha-value>)",
          "blue-dark": "rgb(6 95 70 / <alpha-value>)",
          teal: "rgb(0 166 147 / <alpha-value>)",
          "teal-dark": "rgb(6 95 70 / <alpha-value>)",
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
        "fade-in":  "fadeIn 0.2s ease",
        "slide-up": "slideUp 0.3s cubic-bezier(0.16,1,0.3,1)",
        "scale-in": "scaleIn 0.25s cubic-bezier(0.16,1,0.3,1)",
        "shimmer":  "shimmer 1.8s linear infinite",
        "spin":     "spin 0.8s linear infinite",
      },
      keyframes: {
        fadeIn:  { "0%": { opacity: 0 },             "100%": { opacity: 1 } },
        slideUp: { "0%": { opacity: 0, transform: "translateY(12px)" }, "100%": { opacity: 1, transform: "translateY(0)" } },
        scaleIn: { "0%": { opacity: 0, transform: "scale(0.96)" },     "100%": { opacity: 1, transform: "scale(1)" } },
        shimmer: { "0%": { backgroundPosition: "-200% 0" }, "100%": { backgroundPosition: "200% 0" } },
      },
      boxShadow: {
        "xs":       "0 1px 2px rgb(0 0 0 / 0.05)",
        "sm":       "0 1px 3px rgb(0 0 0 / 0.08), 0 1px 2px rgb(0 0 0 / 0.04)",
        "md":       "0 4px 12px rgb(0 0 0 / 0.08), 0 2px 4px rgb(0 0 0 / 0.04)",
        "lg":       "0 8px 24px rgb(0 0 0 / 0.10), 0 3px 6px rgb(0 0 0 / 0.04)",
        "xl":       "0 16px 48px rgb(0 0 0 / 0.12), 0 4px 12px rgb(0 0 0 / 0.06)",
        "green":    "0 4px 14px rgb(0 166 147 / 0.25)",
        "green-lg": "0 8px 24px rgb(0 166 147 / 0.30)",
        "focus":    "0 0 0 3px rgb(0 166 147 / 0.20)",
        "card":     "0 1px 3px rgb(0 0 0 / 0.06), 0 1px 2px rgb(0 0 0 / 0.04)",
        "card-md":  "0 4px 12px rgb(0 0 0 / 0.08), 0 2px 4px rgb(0 0 0 / 0.04)",
      },
    },
  },
  plugins: [],
};
