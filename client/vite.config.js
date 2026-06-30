import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/auth": "http://127.0.0.1:8001",
      "/patients": "http://127.0.0.1:8001",
      "/appointments": "http://127.0.0.1:8001",
      "/prescriptions": "http://127.0.0.1:8001",
      "/options": "http://127.0.0.1:8001",
    },
  },
});
