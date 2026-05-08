/* ============================================================
   config.js — IntelliMind API Configuration
   ============================================================
   Single source of truth for the API base URL.
   All pages use API_BASE from this file.
   
   Pattern: localhost/127.0.0.1 → local dev server
            otherwise → same-origin (relative URLs)
   ============================================================ */

const API_BASE = (
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
) ? "http://127.0.0.1:8000" : "https://intellimind-5e8m.onrender.com";
// Production: API is hosted on Render at https://intellimind-5e8m.onrender.com
