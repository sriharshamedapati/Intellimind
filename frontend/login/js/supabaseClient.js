/**
 * supabaseClient.js  —  Supabase Client Instances
 * =================================================
 * Uses sessionStorage so sessions die when the tab closes
 * — this ensures proper logout behaviour.
 */
(() => {
  if (typeof window.supabase === "undefined") {
    console.error("[supabaseClient] ❌ Supabase CDN not loaded. Check <script> in index.html.");
    return;
  }

  const { createClient } = window.supabase;

  // ── PRIMARY CLIENT (Auth DB) ──────────────────────────────
  window.SupabaseClient = createClient(
    ENV.SUPABASE_URL,
    ENV.SUPABASE_KEY,
    {
      auth: {
        storage: window.sessionStorage,
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true,
      },
    }
  );

  // ── TEAMMATE CLIENT (login logging) ──────────────────────
  window.OtherSupabaseClient = createClient(
    ENV.OTHER_SUPABASE_URL,
    ENV.OTHER_SUPABASE_KEY
  );

  if (ENV.MODE === "development") {
    console.log("[supabaseClient] ✅ Primary  →", ENV.SUPABASE_URL);
    console.log("[supabaseClient] ✅ Teammate →", ENV.OTHER_SUPABASE_URL);
  }
})();
