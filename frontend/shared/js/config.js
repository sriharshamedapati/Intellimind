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
) ? "http://127.0.0.1:8000" : "";
// Production: empty string means same-origin (API served from same domain)
// If API is on a different domain, replace "" with the full URL e.g. "https://api.intellimind.io"
