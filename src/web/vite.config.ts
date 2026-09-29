import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const apiProxyTarget = process.env.VITE_API_BASE_URL || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: apiProxyTarget,
        changeOrigin: true,
      },
    },
  },
});
