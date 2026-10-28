import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
import { registerSW } from 'virtual:pwa-register';

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Register Service Worker for PWA / offline support via vite-plugin-pwa
const updateSW = registerSW({
  immediate: true,
  onRegistered(r) {
    console.log('SW Registered: ', r);
  },
  onRegisterError(error) {
    console.error('SW registration error', error);
  }
});
