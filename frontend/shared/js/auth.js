/* ============================================================
   auth.js — Shared Session Guard + Dropdown Init + Sign Out
   ============================================================
   Usage: Include Supabase CDN before this script.
   Auto-initializes on load.
   ============================================================ */

const SUPABASE_URL = "https://esnbwpkgjqoluqcxpnmg.supabase.co";
const SUPABASE_KEY = "sb_publishable_0zaP1XivGLwgBENoVpjqqA_USg5TSQE";
const LOGIN_PAGE   = "../login/index.html";

let sb = null;

try {
  if (typeof window.supabase !== "undefined") {
    const { createClient } = window.supabase;
    sb = createClient(SUPABASE_URL, SUPABASE_KEY, {
      auth: { storage: window.sessionStorage }
    });
  } else {
    console.warn("[auth] Supabase CDN not loaded — auth features unavailable");
  }
} catch (err) {
  console.error("[auth] Failed to create Supabase client:", err);
  sb = null;
}

/* ── Session Guard ── */
async function checkSession() {
  // If we have roll in sessionStorage, consider it a valid session
  // (primary check — works even if Supabase client fails)
  const roll = sessionStorage.getItem("im_roll");
  if (!roll) {
    window.location.replace(LOGIN_PAGE);
    return null;
  }

  // Secondary check: verify with Supabase if client is available
  if (sb) {
    try {
      const { data } = await sb.auth.getSession();
      if (!data?.session) {
        // Supabase session expired but roll exists — clear and redirect
        sessionStorage.removeItem("im_roll");
        sessionStorage.removeItem("im_email");
        sessionStorage.removeItem("im_uid");
        window.location.replace(LOGIN_PAGE);
        return null;
      }
      return data.session;
    } catch (err) {
      console.warn("[auth] Session check failed:", err.message);
      // Supabase session check threw an error — clear and redirect (No exceptions)
      sessionStorage.removeItem("im_roll");
      sessionStorage.removeItem("im_email");
      sessionStorage.removeItem("im_uid");
      window.location.replace(LOGIN_PAGE);
      return null;
    }
  }

  // Supabase not available — trust sessionStorage
  return { user: { id: sessionStorage.getItem("im_uid") || "" } };
}

/* ── Populate User Chip ── */
function populateUser() {
  const roll = sessionStorage.getItem("im_roll") || "";
  if (!roll) return "";
  const avEl   = document.getElementById("userAv");
  const nameEl = document.getElementById("userName");
  if (avEl)   avEl.textContent   = roll.slice(0, 2).toUpperCase();
  if (nameEl) nameEl.textContent = roll;
  // Also update welcome name if it exists
  const welcomeEl = document.getElementById("welcomeName");
  if (welcomeEl) welcomeEl.textContent = roll;
  return roll;
}

/* ── Sign Out ── */
async function doSignOut() {
  if (sb) {
    try {
      await sb.auth.signOut();
    } catch (err) {
      console.warn("[auth] Sign out error:", err.message);
    }
  }
  sessionStorage.removeItem("im_roll");
  sessionStorage.removeItem("im_email");
  sessionStorage.removeItem("im_uid");
  window.location.replace(LOGIN_PAGE);
}

/* ── Token Helper ── */
async function getAuthToken() {
  if (!sb) {
    console.warn("[auth] Supabase client not available for token retrieval");
    return null;
  }
  try {
    const { data, error } = await sb.auth.getSession();
    if (error) {
      console.warn("[auth] getSession error:", error.message);
      return null;
    }
    if (!data?.session?.access_token) {
      console.warn("[auth] No active session found");
      return null;
    }
    return data.session.access_token;
  } catch (err) {
    console.error("[auth] getAuthToken failed:", err);
    return null;
  }
}

/* ── Dropdown Toggle ── */
function initDropdown() {
  const dropdown = document.getElementById("navDropdown");
  const trigger  = document.getElementById("navDropdownTrigger");
  if (!dropdown || !trigger) return;

  trigger.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdown.classList.toggle("open");
  });

  document.addEventListener("click", (e) => {
    if (!dropdown.contains(e.target)) {
      dropdown.classList.remove("open");
    }
  });

  // Close on Escape
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") dropdown.classList.remove("open");
  });
}

/* ── Init ── */
async function initAuth() {
  const session = await checkSession();
  if (!session) return;
  populateUser();
  initDropdown();
}

// Auto-init on load
initAuth();
