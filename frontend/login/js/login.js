/**
 * login.js  —  Login Form UI Controller
 * =======================================
 * Handles tab switching, validation, loading states,
 * success overlay, error banners, and form submission.
 */
document.addEventListener("DOMContentLoaded", () => {

  const loginForm      = document.getElementById("loginForm");
  const userIdInput    = document.getElementById("userId");
  const passInput      = document.getElementById("password");
  const idField        = document.getElementById("idField");
  const passField      = document.getElementById("passField");
  const submitBtn      = document.getElementById("submitBtn");
  const btnText        = document.getElementById("btnText");
  const btnArrow       = document.getElementById("btnArrow");
  const spinner        = document.getElementById("spinner");
  const eyeIcon        = document.getElementById("eyeIcon");
  const successOverlay = document.getElementById("successOverlay");
  const errorBanner    = document.getElementById("errorBanner");
  const errorBannerMsg = document.getElementById("errorBannerMsg");


  // ── PASSWORD TOGGLE ───────────────────────────────────────
  window.togglePassword = function () {
    if (passInput.type === "password") {
      passInput.type = "text";
      eyeIcon.innerHTML = `<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>`;
    } else {
      passInput.type = "password";
      eyeIcon.innerHTML = `<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>`;
    }
  };

  // ── VALIDATION ────────────────────────────────────────────
  function validateForm() {
    let valid = true;
    if (!userIdInput.value.trim()) { idField.classList.add("error");   valid = false; }
    else                           { idField.classList.remove("error"); }
    if (!passInput.value.trim())   { passField.classList.add("error");  valid = false; }
    else                           { passField.classList.remove("error"); }
    return valid;
  }

  function clearErrors() {
    idField.classList.remove("error");
    passField.classList.remove("error");
    hideErrorBanner();
  }

  userIdInput.addEventListener("input", () => { idField.classList.remove("error");   hideErrorBanner(); });
  passInput.addEventListener("input",   () => { passField.classList.remove("error"); hideErrorBanner(); });

  // ── ERROR BANNER ──────────────────────────────────────────
  function showErrorBanner(message) {
    errorBannerMsg.textContent = message;
    errorBanner.classList.add("show");
    clearTimeout(errorBanner._t);
    errorBanner._t = setTimeout(hideErrorBanner, 6000);
  }
  function hideErrorBanner() { errorBanner.classList.remove("show"); }

  // ── LOADING STATE ─────────────────────────────────────────
  function setLoading(on) {
    if (on) {
      submitBtn.classList.add("loading");
      btnText.textContent    = "Signing in…";
      btnArrow.style.display = "none";
      spinner.style.display  = "block";
      submitBtn.disabled     = true;
    } else {
      submitBtn.classList.remove("loading");
      btnText.textContent    = "Sign in";
      btnArrow.style.display = "";
      spinner.style.display  = "none";
      submitBtn.disabled     = false;
    }
  }

  // ── SUCCESS → redirect to chat.html ──────────────────────
  function showSuccess(rollNumber) {
    const rollDisplay = document.getElementById("successRoll");
    if (rollDisplay) rollDisplay.textContent = rollNumber;
    successOverlay.classList.add("show");
    setTimeout(() => { window.location.href = ENV.REDIRECT_URL; }, 2000);
  }

  successOverlay.addEventListener("click", () => successOverlay.classList.remove("show"));

  // ── FORM SUBMIT ───────────────────────────────────────────
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    const roll     = userIdInput.value.trim();
    const password = passInput.value.trim();

    setLoading(true);
    hideErrorBanner();

    try {
      const result = await AuthService.loginStudent(roll, password);

      if (result.success) {
        showSuccess(result.rollNumber);
      } else {
        setLoading(false);
        showErrorBanner(result.errorMessage || "Sign-in failed. Please check your credentials.");
        idField.classList.add("error");
        passField.classList.add("error");
        passInput.value = "";
      }
    } catch (err) {
      setLoading(false);
      console.error("[login.js] Unexpected error:", err);
      showErrorBanner("An unexpected error occurred. Please try again.");
    }
  });

  // ── CURSOR TRAIL ──────────────────────────────────────────
  const dot = document.createElement("div");
  dot.className = "cursor-dot";
  document.body.appendChild(dot);
  document.addEventListener("mousemove", (e) => {
    dot.style.left    = e.clientX - 3 + "px";
    dot.style.top     = e.clientY - 3 + "px";
    dot.style.opacity = "0.5";
    clearTimeout(dot._t);
    dot._t = setTimeout(() => { dot.style.opacity = "0"; }, 500);
  });

  // ── INIT: Already logged in? Redirect to chat ─────────────
  (async () => {
    try {
      const session = await AuthService.getSession();
      if (session) {
        console.log("[login.js] Active session found, redirecting…");
        window.location.href = ENV.REDIRECT_URL;
      }
    } catch (_) { /* show login form */ }
  })();
});
