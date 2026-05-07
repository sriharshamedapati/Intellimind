/**
 * authService.js  —  Authentication Logic
 * =========================================
 * KEY CONNECTION:
 *   After successful login, stores the roll number in
 *   sessionStorage as "im_roll".
 *
 *   chat.js reads sessionStorage.getItem("im_roll") and
 *   sends it to the FastAPI backend with every message.
 *   The backend uses it to fetch real student data from
 *   Supabase before calling Gemini.
 */
const AuthService = (() => {

  function rollToEmail(roll) {
    return roll.toUpperCase().trim() + ENV.EMAIL_DOMAIN;
  }

  async function logLoginEvent(client, table, rollNumber, label) {
    try {
      const { error } = await client
        .from(table)
        .insert([{ roll_number: rollNumber }]);
      if (error) {
        console.warn(`[authService] ${label} insert failed:`, error.message);
      } else if (ENV.MODE === "development") {
        console.log(`[authService] ✅ Logged to ${label} (${table})`);
      }
    } catch (err) {
      console.warn(`[authService] ${label} threw:`, err.message);
    }
  }

  async function loginStudent(roll, password) {
    const formattedRoll = roll.toUpperCase().trim();
    const email         = rollToEmail(formattedRoll);

    // Step 1: Supabase Auth
    const { data, error } = await window.SupabaseClient.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      console.warn("[authService] Auth failed:", error.message);
      return {
        success:      false,
        errorCode:    error.status ?? "AUTH_ERROR",
        errorMessage: mapAuthError(error),
      };
    }

    // Step 2: Log to primary DB
    await logLoginEvent(window.SupabaseClient, ENV.LOGIN_LOG_TABLE, formattedRoll, "Primary DB");

    // Step 3: Log to teammate DB
    await logLoginEvent(window.OtherSupabaseClient, ENV.OTHER_LOG_TABLE, formattedRoll, "Teammate DB");

    // ⭐ Step 4: Store roll in sessionStorage
    // chat.js reads "im_roll" on the chatbot page — this is the bridge
    sessionStorage.setItem("im_roll",  formattedRoll);
    sessionStorage.setItem("im_email", email);
    sessionStorage.setItem("im_uid",   data?.user?.id ?? "");

    if (ENV.MODE === "development") {
      console.log(`[authService] ✅ Stored in sessionStorage: im_roll = "${formattedRoll}"`);
    }

    return { success: true, rollNumber: formattedRoll };
  }

  function mapAuthError(error) {
    const msg = (error.message || "").toLowerCase();
    if (msg.includes("invalid login") || msg.includes("invalid credentials"))
      return "Incorrect roll number or password. Please try again.";
    if (msg.includes("email not confirmed"))
      return "Your account email is not confirmed. Contact administrator support.";
    if (msg.includes("too many requests") || error.status === 429)
      return "Too many attempts. Please wait a moment and try again.";
    if (msg.includes("network") || msg.includes("fetch"))
      return "Network error. Please check your internet connection.";
    return "Sign-in failed. Please try again or contact support.";
  }

  async function logoutStudent() {
    await window.SupabaseClient.auth.signOut();
    sessionStorage.removeItem("im_roll");
    sessionStorage.removeItem("im_email");
    sessionStorage.removeItem("im_uid");
  }

  async function getSession() {
    const { data } = await window.SupabaseClient.auth.getSession();
    return data?.session ?? null;
  }

  return { loginStudent, logoutStudent, getSession };
})();
