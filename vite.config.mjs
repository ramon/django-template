import { defineConfig } from 'vite'
import tailwindcss from "@tailwindcss/vite"
import path from "node:path";

export default defineConfig({
    plugins: [tailwindcss()],
    server: {
        host: '0.0.0.0',
        port: 8001,
        strictPort: true,
        cors: {
            origin: "http://localhost:8000"
        }
    },
    build: {
        manifest: true,
        outDir: 'backend/static/dist',
        assetsDir: 'assets',
        emptyOutDir: true,
        rollupOptions: {
            input: {
                app: path.resolve("frontend/entries/app.js"),
            }
        }
    }
})