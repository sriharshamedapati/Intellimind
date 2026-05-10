/**
 * env.js  —  INTELLMIND Frontend Config
 * ========================================
 * Single source of truth for all frontend keys and settings.
 * These are publishable/anon keys — safe for client use.
 */
const ENV = {
  // ── PRIMARY SUPABASE (Your Auth DB) ──────────────────────
  SUPABASE_URL: "https://esnbwpkgjqoluqcxpnmg.supabase.co",
  SUPABASE_KEY: "sb_publishable_0zaP1XivGLwgBENoVpjqqA_USg5TSQE",

  // ── TEAMMATE SUPABASE ─────────────────────────────────────
  OTHER_SUPABASE_URL: "https://vbqppvnnknzseilwromv.supabase.co",
  OTHER_SUPABASE_KEY: "sb_publishable_jOTzIxsaeRXfBgM4xUIj6Q_fOL6aFjM",

  // ── APP CONFIG ────────────────────────────────────────────
  EMAIL_DOMAIN:    "@aec.edu.in",
  REDIRECT_URL:    "../chat/index.html",   // After login → chatbot page
  LOGIN_LOG_TABLE: "login_logs",
  OTHER_LOG_TABLE: "student_logins",

  // ── BACKEND ───────────────────────────────────────────────
  BACKEND_URL: "http://127.0.0.1:8000",

  MODE: "development",
};

Object.freeze(ENV);
