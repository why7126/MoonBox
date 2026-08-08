export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        mb: {
          background: "var(--mb-background)",
          panel: "var(--mb-panel)",
          border: "var(--mb-border)",
          accent: "var(--mb-accent)",
          text: "var(--mb-text)",
          muted: "var(--mb-muted)",
        },
      },
    },
  },
};
