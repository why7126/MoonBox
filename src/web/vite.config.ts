import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const apiProxyTarget = process.env.VITE_API_BASE_URL || "http://localhost:8000";
const buildId = process.env.MOONBOX_BUILD_ID || `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;

export default defineConfig({
  plugins: [react()],
  define: {
    __MOONBOX_BUILD_ID__: JSON.stringify(buildId),
  },
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
