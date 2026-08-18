import { defineConfig } from "vitest/config";

// Config separada da de build: os testes nao precisam do pipeline do Tailwind.
export default defineConfig({
  test: {
    environment: "happy-dom",
    include: ["frontend/**/*.test.js"],
    coverage: {
      provider: "v8",
      include: ["frontend/**/*.js"],
      // entries/ e controllers/index.js so ligam (import.meta.glob, Application.start);
      // regra testavel vira modulo em lib/, ver frontend.md.
      exclude: ["frontend/**/*.test.js", "frontend/entries/**", "frontend/controllers/index.js"],
      thresholds: {
        lines: 90,
        statements: 90,
        functions: 90,
        branches: 90,
      },
    },
  },
});
