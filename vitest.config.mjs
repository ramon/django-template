import { defineConfig } from "vitest/config";

// Config separada da de build: os testes nao precisam do pipeline do Tailwind.
export default defineConfig({
  test: {
    environment: "happy-dom",
    include: ["frontend/**/*.test.js"],
    coverage: {
      provider: "v8",
      include: ["frontend/**/*.js"],
      exclude: ["frontend/**/*.test.js", "frontend/entries/**"],
    },
  },
});
