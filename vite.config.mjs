import path from "node:path";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [tailwindcss()],
  server: {
    host: "0.0.0.0",
    port: 8001,
    strictPort: true,
    cors: {
      origin: "http://localhost:8000",
    },
  },
  build: {
    manifest: true,
    outDir: "static/dist",
    assetsDir: "assets",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        app: path.resolve("frontend/entries/app.js"),
      },
    },
  },
});
