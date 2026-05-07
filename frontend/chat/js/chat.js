/* ============================================================
   chat.js — IntelliMind Chat Logic
   ============================================================
   Features:
   - Smart API calls using API_BASE from config.js
   - Smooth typing indicator
   - Markdown rendering, timestamps, scroll to bottom
   ============================================================ */

const CHAT_URL = API_BASE + "/chat";
const STUDENT_ROLL = sessionStorage.getItem("im_roll") || "";

if (!STUDENT_ROLL) {
  window.location.replace("../login/index.html");
}

let chatStarted = false;
let isWaiting = false;
let selectedImageBase64 = null;
let selectedImageMimeType = null;
let chatHistory = [];

/* ── Image Upload Handling ── */
function handleImageSelect(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (evt) {
    const dataUrl = evt.target.result;
    document.getElementById("imagePreview").src = dataUrl;
    document.getElementById("imagePreviewContainer").style.display = "inline-block";

    // Split "data:image/jpeg;base64,..."
    const parts = dataUrl.split(";base64,");
    selectedImageMimeType = parts[0].split(":")[1];
    selectedImageBase64 = parts[1];
  };
  reader.readAsDataURL(file);
}

function clearImage() {
  selectedImageBase64 = null;
  selectedImageMimeType = null;
  document.getElementById("chatImageUpload").value = "";
  document.getElementById("imagePreview").src = "";
  document.getElementById("imagePreviewContainer").style.display = "none";
}


/* ── Backend Call ── */
async function callBackend(userMsg) {
  const payload = {
    message: userMsg,
    student_roll: STUDENT_ROLL,
    mode: "chat"
  };

  if (selectedImageBase64) {
    payload.image_base64 = selectedImageBase64;
    payload.image_mime_type = selectedImageMimeType;
  }

  const res = await fetch(CHAT_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Backend error ${res.status}`);
  }

  const data = await res.json();
  return data.response;
}

/* ── Message Rendering ── */
function now() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function addMessage(role, rawText, imageSrc = null) {
  const wrap = document.getElementById("messagesWrap");
  const group = document.createElement("div");
  group.className = `msg-group ${role}`;

  const av = document.createElement("div");
  av.className = `msg-av ${role}`;
  av.textContent = role === "bot" ? "IM" : (STUDENT_ROLL.slice(0, 2) || "ME");

  const col = document.createElement("div");
  col.className = "msg-col";

  const sender = document.createElement("div");
  sender.className = "msg-sender";
  sender.textContent = role === "bot" ? "IntelliMind" : (STUDENT_ROLL || "You");

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";

  let bubbleHtml = role === "bot"
    ? renderMarkdown(rawText)
    : "<p>" + esc(rawText).replace(/\n/g, "<br>") + "</p>";

  if (imageSrc) {
    bubbleHtml = `<img src="${imageSrc}" style="max-width:100%; border-radius:8px; margin-bottom:8px; display:block;">` + bubbleHtml;
  }

  bubble.innerHTML = bubbleHtml;

  // Add entrance animation
  group.style.opacity = "0";
  group.style.transform = "translateY(12px)";

  const time = document.createElement("div");
  time.className = "msg-time";
  time.textContent = now();

  col.appendChild(sender);
  col.appendChild(bubble);
  col.appendChild(time);
  group.appendChild(av);
  group.appendChild(col);
  wrap.appendChild(group);

  // Trigger entrance animation
  requestAnimationFrame(() => {
    group.style.transition = "opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1), transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)";
    group.style.opacity = "1";
    group.style.transform = "translateY(0)";
  });

  scrollBottom();
}

function scrollBottom() {
  const ca = document.getElementById("chatArea");
  setTimeout(() => { ca.scrollTop = ca.scrollHeight; }, 60);
}

function showTyping(on) {
  const row = document.getElementById("typingRow");
  row.classList.toggle("visible", on);
  // Update thinking label
  const label = document.getElementById("thinkingLabel");
  if (label) label.textContent = "IntelliMind is thinking...";
  if (on) scrollBottom();
}

function startChat() {
  if (!chatStarted) {
    document.getElementById("welcomeScreen").style.display = "none";
    document.getElementById("dateSep").style.display = "";
    document.getElementById("messagesWrap").classList.add("visible");
    chatStarted = true;
  }
}

/* ── Send Message ── */
async function sendMessage() {
  if (isWaiting) return;
  const input = document.getElementById("chatInput");
  const msg = input.value.trim();
  if (!msg) return;

  const currentImageSrc = document.getElementById("imagePreview").src;
  const hasImage = !!selectedImageBase64;

  startChat();
  addMessage("user", msg, hasImage ? currentImageSrc : null);

  // Save user message to history immediately
  chatHistory.push({ role: "user", content: msg, imageSrc: hasImage ? currentImageSrc : null });
  if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);
  sessionStorage.setItem("im_chat_history", JSON.stringify(chatHistory));

  input.value = "";
  input.style.height = "auto";
  document.getElementById("sendBtn").disabled = true;
  isWaiting = true;
  showTyping(true);
  updateActionBtn();

  // Send button animation
  const sendBtn = document.getElementById("sendBtn");
  sendBtn.classList.add("sent");
  setTimeout(() => sendBtn.classList.remove("sent"), 400);

  // Hide image preview immediately after sending
  document.getElementById("imagePreviewContainer").style.display = "none";

  try {
    const reply = await callBackend(msg);
    showTyping(false);
    addMessage("bot", reply);

    // Save bot reply to history
    chatHistory.push({ role: "assistant", content: reply });
    if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);
    sessionStorage.setItem("im_chat_history", JSON.stringify(chatHistory));
  } catch (err) {
    showTyping(false);
    addMessage("bot", `**Error** — ${err.message}\n\nMake sure the backend is running:\n\`\`\`bash\ncd backend\nuvicorn main:app --reload\n\`\`\``);
  }

  isWaiting = false;
  // Clear image data after request is done
  clearImage();
}

function sendChip(chip) {
  const text = chip.querySelector("strong").textContent;
  setInput(text);
  sendMessage();
}

function setInput(text) {
  const input = document.getElementById("chatInput");
  input.value = text;
  input.focus();
  autoResize(input);
  document.getElementById("sendBtn").disabled = false;
  updateActionBtn();
}

function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
}

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 130) + "px";
  document.getElementById("sendBtn").disabled = el.value.trim().length === 0 || isWaiting;
}

function resetChat() {
  chatStarted = false; chatHistory = []; isWaiting = false;
  sessionStorage.removeItem("im_chat_history");
  document.getElementById("messagesWrap").innerHTML = "";
  document.getElementById("messagesWrap").classList.remove("visible");
  document.getElementById("welcomeScreen").style.display = "";
  document.getElementById("dateSep").style.display = "none";
  document.getElementById("chatInput").value = "";
  document.getElementById("chatInput").style.height = "auto";
  showTyping(false);
  document.getElementById("sendBtn").disabled = true;
  updateActionBtn();
}

function updateActionBtn() {
  const hasText = document.getElementById("chatInput").value.trim().length > 0;
  document.getElementById("sendBtn").style.display = hasText ? "flex" : "none";
  document.getElementById("voiceBtn").style.display = hasText ? "none" : "flex";
}

document.getElementById("chatInput").addEventListener("input", function () {
  document.getElementById("sendBtn").disabled = this.value.trim().length === 0 || isWaiting;
  updateActionBtn();
});

// Init
updateActionBtn();

// Load history from session
(function loadHistory() {
  const saved = sessionStorage.getItem("im_chat_history");
  if (saved) {
    const history = JSON.parse(saved);
    if (history.length > 0) {
      chatHistory = history;
      history.forEach(m => {
        addMessage(m.role === "user" ? "user" : "bot", m.content, m.imageSrc);
      });
      startChat();
    }
  }
})();

// Chat fully initialized