/* ============================================================
   security.js — Anti-Inspection Shield
   ============================================================
   Blocks right-click, DevTools shortcuts, and view-source.
   Include this script on every page for client-side protection.
   
   NOTE: This is a deterrent, not absolute security. The real
   protection is that API keys live on the backend, never in
   the browser. This script prevents casual snooping.
   ============================================================ */

(function () {
  "use strict";

  // ── Block right-click context menu ──
  document.addEventListener("contextmenu", function (e) {
    e.preventDefault();
    showSecurityToast("Right-click is disabled on this application.");
    return false;
  });

  // ── Block DevTools keyboard shortcuts ──
  document.addEventListener("keydown", function (e) {
    // F12 — DevTools
    if (e.key === "F12") {
      e.preventDefault();
      showSecurityToast("Developer tools are disabled.");
      return false;
    }

    // Ctrl+Shift+I — Inspect Element
    if (e.ctrlKey && e.shiftKey && e.key === "I") {
      e.preventDefault();
      showSecurityToast("Inspect element is disabled.");
      return false;
    }

    // Ctrl+Shift+J — Console
    if (e.ctrlKey && e.shiftKey && e.key === "J") {
      e.preventDefault();
      showSecurityToast("Console access is disabled.");
      return false;
    }

    // Ctrl+Shift+C — Element picker
    if (e.ctrlKey && e.shiftKey && e.key === "C") {
      e.preventDefault();
      return false;
    }

    // Ctrl+U — View source
    if (e.ctrlKey && e.key === "u") {
      e.preventDefault();
      showSecurityToast("View source is disabled.");
      return false;
    }

    // Ctrl+S — Save page
    if (e.ctrlKey && e.key === "s") {
      e.preventDefault();
      return false;
    }
  });

  // ── Block drag (prevents dragging images/text to reveal source) ──
  document.addEventListener("dragstart", function (e) {
    e.preventDefault();
  });

  // ── Security toast notification ──
  function showSecurityToast(msg) {
    // Remove any existing security toast
    const existing = document.getElementById("securityToast");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.id = "securityToast";
    toast.textContent = "🔒 " + msg;
    Object.assign(toast.style, {
      position: "fixed",
      bottom: "24px",
      left: "50%",
      transform: "translateX(-50%) translateY(20px)",
      background: "rgba(15, 15, 20, 0.95)",
      color: "#f87171",
      padding: "12px 24px",
      borderRadius: "12px",
      fontSize: "0.85rem",
      fontWeight: "500",
      fontFamily: "'Inter', 'Segoe UI', sans-serif",
      zIndex: "99999",
      backdropFilter: "blur(12px)",
      border: "1px solid rgba(248, 113, 113, 0.3)",
      boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
      opacity: "0",
      transition: "opacity 0.3s ease, transform 0.3s ease",
      pointerEvents: "none",
    });

    document.body.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
      toast.style.opacity = "1";
      toast.style.transform = "translateX(-50%) translateY(0)";
    });

    // Animate out after 2s
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(-50%) translateY(20px)";
      setTimeout(() => toast.remove(), 300);
    }, 2000);
  }
})();
