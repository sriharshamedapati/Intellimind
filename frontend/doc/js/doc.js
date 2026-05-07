/* ============================================================
   doc.js — Document Analyser: Upload → Analysis → Chat & Split
   3 screens controlled by switchView()
   ============================================================ */

// API_BASE is provided by shared/js/config.js (loaded before this script)

// ── State ──────────────────────────────────────────────────────
let selectedFile    = null;
let currentSession  = null;   // { session_id, filename, analysis }
let currentView     = null;   // 'analysis' | 'chat' | 'split'

// ── Helpers ────────────────────────────────────────────────────
function formatSize(b) {
  if (b < 1024)           return b + " B";
  if (b < 1024 * 1024)   return (b / 1024).toFixed(1) + " KB";
  return (b / (1024 * 1024)).toFixed(1) + " MB";
}

function nowTime() {
  const d = new Date();
  return `${d.getHours()}:${String(d.getMinutes()).padStart(2,"0")}`;
}

function md(text) {
  return typeof renderMarkdown === "function"
    ? renderMarkdown(text)
    : text.replace(/\n/g, "<br>");
}

// Toast uses shared/js/toast.js → showToast() loaded before this script

// ── File Handling ──────────────────────────────────────────────
function setFile(file) {
  selectedFile = file;
  document.getElementById("fileName").textContent = file.name;
  document.getElementById("fileSize").textContent = formatSize(file.size);
  document.getElementById("fileStrip").classList.add("visible");
  document.getElementById("analyseBtn").classList.add("active");
  currentSession = null;
}

function clearFile() {
  selectedFile = null;
  document.getElementById("docInput").value = "";
  document.getElementById("fileStrip").classList.remove("visible");
  document.getElementById("analyseBtn").classList.remove("active");
  currentSession = null;
}

document.getElementById("docInput").addEventListener("change", function () {
  if (this.files[0]) setFile(this.files[0]);
});
document.getElementById("removeFile").addEventListener("click", function (e) {
  e.stopPropagation();
  clearFile();
});

// ── Drag & Drop ────────────────────────────────────────────────
const dropZone = document.getElementById("dropZone");
dropZone.addEventListener("dragover",  (e) => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragleave", ()  => { dropZone.classList.remove("drag-over"); });
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file) setFile(file);
});

// ── Loading Overlay ────────────────────────────────────────────
const LOADING_STEPS = [
  { text: "Reading file content…",      pct: 20 },
  { text: "Extracting text…",           pct: 40 },
  { text: "Sending to AI…",             pct: 60 },
  { text: "Generating analysis…",       pct: 80 },
  { text: "Finishing up…",              pct: 95 },
];
let _loadingTimer = null;
let _stepIdx = 0;

function showLoading() {
  const overlay = document.getElementById("loadingOverlay");
  const status  = document.getElementById("loadingStatus");
  const bar     = document.getElementById("loadingBarFill");
  overlay.classList.add("visible");
  _stepIdx = 0;
  _step();

  function _step() {
    if (_stepIdx >= LOADING_STEPS.length) return;
    const s = LOADING_STEPS[_stepIdx++];
    if (status) status.textContent = s.text;
    if (bar)    bar.style.width    = s.pct + "%";
    _loadingTimer = setTimeout(_step, 900);
  }
}

function hideLoading() {
  clearTimeout(_loadingTimer);
  const overlay = document.getElementById("loadingOverlay");
  const bar     = document.getElementById("loadingBarFill");
  if (bar) bar.style.width = "100%";
  setTimeout(() => {
    overlay.classList.remove("visible");
    if (bar) bar.style.width = "0%";
  }, 400);
}

// ── Analyse Document ──────────────────────────────────────────
async function analyseDocument() {
  if (!selectedFile) return;

  showLoading();

  const roll = sessionStorage.getItem("im_roll") || "";
  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("student_roll", roll);

  try {
    const res = await fetch(`${API_BASE}/analyze-doc`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Backend error ${res.status}`);
    }

    const data = await res.json();
    hideLoading();

    currentSession = {
      session_id: data.session_id,
      filename:   data.filename,
      analysis:   data.analysis,
    };

    // Populate all three panels
    _populatePanels();

    // Show view switcher in topbar
    document.getElementById("viewSwitcher").classList.add("visible");

    // Show analysis view first
    switchView("analysis");

  } catch (err) {
    hideLoading();
    showToast("Analysis failed: " + err.message);
    console.error("[doc] analyseDocument:", err);
  }
}

function _populatePanels() {
  const s = currentSession;
  if (!s) return;
  const rendered = md(s.analysis);

  // Analysis panel
  document.getElementById("resultFileNameA").textContent = s.filename;
  document.getElementById("resultBodyA").innerHTML       = rendered;

  // Split-left panel
  document.getElementById("splitDocName").textContent   = s.filename;
  document.getElementById("resultBodyS").innerHTML      = rendered;

  // Chat doc name (standalone)
  document.getElementById("chatDocNameC").textContent   = s.filename;
}

// ── Switch Views ───────────────────────────────────────────────
function switchView(view) {
  currentView = view;
  const screens = { analysis:"screenAnalysis", chat:"screenChat", split:"screenSplit" };
  const btns    = { analysis:"vsAnalysis",     chat:"vsChat",     split:"vsSplit"     };

  // Hide upload, show correct screen
  document.getElementById("screenUpload").classList.add("hidden");
  Object.values(screens).forEach(id => document.getElementById(id).classList.add("hidden"));
  document.getElementById(screens[view]).classList.remove("hidden");

  // Toggle button state
  Object.keys(btns).forEach(k => {
    document.getElementById(btns[k]).classList.toggle("active", k === view);
  });
}

function resetToUpload() {
  currentSession = null;
  clearFile();
  currentView = null;

  // Hide all result screens, show upload
  ["screenAnalysis","screenChat","screenSplit"].forEach(id =>
    document.getElementById(id).classList.add("hidden"));
  document.getElementById("screenUpload").classList.remove("hidden");
  document.getElementById("viewSwitcher").classList.remove("visible");

  // Clear chat logs
  _resetChatPanel("C");
  _resetChatPanel("S");
}

// ── Chat helpers ───────────────────────────────────────────────
function _getLog(panel) { return document.getElementById(`chatMessages${panel}`); }

function _resetChatPanel(panel) {
  const log = _getLog(panel);
  if (!log) return;
  log.innerHTML = "";

  // Re-insert welcome
  const welcome = document.createElement("div");
  if (panel === "C") {
    welcome.className = "chat-welcome";
    welcome.innerHTML = `
      <div class="chat-welcome-icon">
        <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      </div>
      <div class="chat-welcome-text">Ask me anything about your document!</div>
      <div class="quick-chips">
        <div class="chip" onclick="prefillChat('Summarise the key points')">Summarise key points</div>
        <div class="chip" onclick="prefillChat('What are the main topics?')">Main topics</div>
        <div class="chip" onclick="prefillChat('Create 5 quiz questions from this document')">Quiz questions</div>
        <div class="chip" onclick="prefillChat('Explain the most important concept')">Key concept</div>
      </div>`;
  } else {
    welcome.className = "chat-welcome chat-welcome--sm";
    welcome.innerHTML = `
      <div class="chat-welcome-text">Ask me anything about this document</div>
      <div class="quick-chips">
        <div class="chip" onclick="prefillChatS('Summarise the key points')">Summarise</div>
        <div class="chip" onclick="prefillChatS('Create 5 quiz questions')">Quiz questions</div>
      </div>`;
  }
  log.appendChild(welcome);
}

function prefillChat(text) {
  const inp = document.getElementById("chatInputC");
  if (inp) { inp.value = text; inp.focus(); }
}
function prefillChatS(text) {
  const inp = document.getElementById("chatInputS");
  if (inp) { inp.value = text; inp.focus(); }
}

function autoResizeC(el) { el.style.height = "auto"; el.style.height = Math.min(el.scrollHeight, 120) + "px"; }
function autoResizeS(el) { el.style.height = "auto"; el.style.height = Math.min(el.scrollHeight, 120) + "px"; }

function handleChatKeyC(e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendDocMessage("C"); } }
function handleChatKeyS(e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendDocMessage("S"); } }

// ── Send Chat Message ─────────────────────────────────────────
async function sendDocMessage(panel) {
  if (!currentSession) { showToast("Analyse a document first."); return; }

  const inputId = `chatInput${panel}`;
  const input   = document.getElementById(inputId);
  if (!input) return;

  const question = input.value.trim();
  if (!question) return;

  input.value = "";
  input.style.height = "auto";

  const roll = sessionStorage.getItem("im_roll") || "";

  _removeWelcome(panel);
  _appendMsg(panel, "user", question);
  const typingId = _appendTyping(panel);

  try {
    const res = await fetch(`${API_BASE}/doc/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id:   currentSession.session_id,
        question:     question,
        student_roll: roll,
      }),
    });

    _removeTyping(panel, typingId);

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      _appendMsg(panel, "error", err.detail || `Error ${res.status}`);
      return;
    }

    const data = await res.json();
    _appendMsg(panel, "bot", data.response);

  } catch (err) {
    _removeTyping(panel, typingId);
    _appendMsg(panel, "error", "Request failed: " + err.message);
    console.error("[doc/chat]", err);
  }
}

function _removeWelcome(panel) {
  const log = _getLog(panel);
  if (!log) return;
  const w = log.querySelector(".chat-welcome");
  if (w) w.remove();
}

function _appendMsg(panel, role, text) {
  const log = _getLog(panel);
  if (!log) return;

  const rollShort = (sessionStorage.getItem("im_roll") || "ME").slice(0, 2).toUpperCase();

  if (role === "error") {
    const el = document.createElement("div");
    el.style.cssText = "color:#dc2626;font-size:0.78rem;padding:0.3rem 0.5rem;";
    el.textContent = "⚠ " + text;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return;
  }

  const isUser = role === "user";
  const row = document.createElement("div");
  row.className = `msg-row ${isUser ? "user" : ""}`;

  const av = document.createElement("div");
  av.className   = `msg-av ${isUser ? "user-av-msg" : "bot"}`;
  av.textContent = isUser ? rollShort : "IM";

  const col = document.createElement("div");
  col.className = "msg-col";

  const sender = document.createElement("div");
  sender.className   = "msg-sender";
  sender.textContent = isUser ? rollShort : "IntelliMind";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.innerHTML = isUser
    ? text.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\n/g,"<br>")
    : md(text);

  const time = document.createElement("div");
  time.className   = "msg-time";
  time.textContent = nowTime();

  col.appendChild(sender);
  col.appendChild(bubble);
  col.appendChild(time);
  row.appendChild(av);
  row.appendChild(col);
  log.appendChild(row);
  log.scrollTop = log.scrollHeight;
}

function _appendTyping(panel) {
  const log = _getLog(panel);
  if (!log) return null;

  const id  = "typing-" + panel + "-" + Date.now();
  const row = document.createElement("div");
  row.className = "typing-row"; row.id = id;
  row.innerHTML = `
    <div class="msg-av bot">IM</div>
    <div class="typing-bubble">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>`;
  log.appendChild(row);
  log.scrollTop = log.scrollHeight;
  return id;
}

function _removeTyping(panel, id) {
  if (!id) return;
  const el = document.getElementById(id);
  if (el) el.remove();
}
