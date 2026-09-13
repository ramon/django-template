import path from "node:path";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  // Prefixo vazio: le VITE_PORT e APP_PORT do mesmo .env que o Django e o compose leem
  // (e do ambiente, que tem precedencia). So o que o codigo referencia via
  // import.meta.env chega ao bundle, entao ler tudo aqui nao expoe nada.
  const env = loadEnv(mode, process.cwd(), "");
  // mesma porta que config/settings/parts/vite.py poe na URL do dev server
  const vitePort = Number(env.VITE_PORT || 8001);
  const appPort = Number(env.APP_PORT || 8000);

  return {
    plugins: [tailwindcss()],
    server: {
      host: "0.0.0.0",
      port: vitePort,
      strictPort: true,
      cors: {
        // o runserver anuncia 127.0.0.1 e o README aponta localhost: as duas origens
        origin: [`http://localhost:${appPort}`, `http://127.0.0.1:${appPort}`],
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
  };
});
