/* ============================================================
   config.js — INTELLMIND API Configuration
   ============================================================
   Single source of truth for the API base URL.
   All pages use API_BASE from this file.
   
   Pattern: localhost/127.0.0.1 → local dev server
            otherwise → window.INTELLMIND_API_BASE or same-origin fallback
            
   To set a custom API base in production, add this to your HTML
   BEFORE loading config.js:
   <script>window.INTELLMIND_API_BASE = "https://api.intellmind.io";</script>
   ============================================================ */

const API_BASE = (
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
) ? "http://127.0.0.1:8000" : (window.INTELLMIND_API_BASE || "");
