import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      // We moved the manifest configuration here. The manual public/manifest.json was removed.
      manifest: {
        name: "Polar Expedition Logistics System",
        short_name: "PolarLogistics",
        start_url: "/",
        display: "standalone",
        background_color: "#0f172a",
        theme_color: "#0f172a",
        // KNOWN GAP: No actual icon image assets exist yet. 
        // These are placeholder paths that must be filled before physical deployment.
        icons: [
          {
            src: "/placeholder-icon-192.png",
            sizes: "192x192",
            type: "image/png",
            purpose: "any maskable"
          },
          {
            src: "/placeholder-icon-512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any maskable"
          }
        ]
      },
      workbox: {
        // Deny navigate fallback for API calls, just in case
        navigateFallbackDenylist: [/^\/api/],
        runtimeCaching: [
          {
            // CRITICAL DESIGN DECISION: Do NOT cache API calls.
            // Serving stale cached API data as if it were live inventory/personnel state
            // would be actively dangerous for a safety-relevant system.
            urlPattern: /^\/api\//,
            handler: 'NetworkOnly'
          }
        ]
      }
    })
  ],

  server: {
    host: "127.0.0.1",
    port: 5173,

    // Proxy all /api requests to the FastAPI backend running on port 8000.
    // This eliminates CORS issues during local development: the browser sees
    // every request going to the same origin (localhost:5173) while Vite
    // proxy: {
    //   "/api": {
    //     target: "http://127.0.0.1:8000",
    //     changeOrigin: true,
    //   },
    // },
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: 4173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    }
  }
});
