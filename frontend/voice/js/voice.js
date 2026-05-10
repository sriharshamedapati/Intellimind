/* ============================================================
   voice.js — INTELLMIND Voice Chat
   ============================================================
   Features:
   - Chrome TTS keepalive workaround (prevents 15s auto-pause)
   - Strips markdown before TTS (no reading ** or ### aloud)
   - Renders markdown in message bubbles
   - Auto-listen after bot finishes speaking (hands-free)
   - Status indicator (Idle → Listening → Processing → Speaking)
   - Browser compatibility check at startup
   - Auto-listen retry guard (max 2 consecutive failures)
   ============================================================ */

const VOICE_CHAT_URL = API_BASE + "/chat";
const STUDENT_ROLL = sessionStorage.getItem("im_roll") || "";

if (!STUDENT_ROLL) {
  window.location.replace("../login/index.html");
}

/* ── State ── */
let recognition = null;
let isListening = false;
let isSpeaking = false;
let isProcessing = false;
let autoListenNext = true;
let finalTranscript = "";
let msgCount = 0;
let autoListenFailCount = 0;  // Guard against infinite retry loops
const MAX_AUTO_LISTEN_FAILS = 2;
let voiceHistory = [];

/* ── Chrome TTS Keepalive ── */
// Chrome has a bug where speechSynthesis pauses after ~15 seconds.
// Workaround: call speechSynthesis.resume() periodically while speaking.
let ttsKeepAlive = null;

function startTTSKeepAlive() {
  stopTTSKeepAlive();
  ttsKeepAlive = setInterval(() => {
    if (isSpeaking && speechSynthesis.speaking) {
      speechSynthesis.resume();
    }
  }, 5000); // Resume every 5 seconds
}

function stopTTSKeepAlive() {
  if (ttsKeepAlive) {
    clearInterval(ttsKeepAlive);
    ttsKeepAlive = null;
  }
}

/* ── Browser Compatibility Check ── */
(function checkBrowserSupport() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    const hint = document.getElementById("micHint");
    if (hint) hint.textContent = "Voice not supported in this browser. Use Chrome.";
    const micBtn = document.getElementById("micBtn");
    if (micBtn) {
      micBtn.disabled = true;
      micBtn.title = "Speech recognition requires Chrome or Edge";
    }
    showToast("Voice chat requires Chrome or Edge browser.");
  }

  if (!window.speechSynthesis) {
    showToast("Text-to-speech not available in this browser.");
  }

  // Warmup speechSynthesis (Chrome sometimes needs a trigger to load voices)
  if (window.speechSynthesis) {
    speechSynthesis.getVoices();
  }
})();



/* ── Status Manager ── */
function setStatus(state) {
  const hint = document.getElementById("micHint");
  const micBtn = document.getElementById("micBtn");
  const indicator = document.getElementById("statusIndicator");
  const dot = document.getElementById("statusDot");

  switch (state) {
    case "idle":
      hint.textContent = "Tap to speak";
      indicator.textContent = "Ready";
      dot.className = "status-dot idle";
      micBtn.disabled = false;
      break;
    case "listening":
      hint.textContent = "Listening… tap to stop";
      indicator.textContent = "Listening";
      dot.className = "status-dot listening";
      micBtn.disabled = false;
      setVisualizerState("listening");
      break;
    case "processing":
      hint.textContent = "Thinking…";
      indicator.textContent = "Processing";
      dot.className = "status-dot processing";
      micBtn.disabled = true;
      setVisualizerState("processing");
      break;
    case "speaking":
      hint.textContent = "Speaking… tap mic to interrupt";
      indicator.textContent = "Speaking";
      dot.className = "status-dot speaking";
      micBtn.disabled = false;
      setVisualizerState("speaking");
      break;
  }
}

/* ── Visualizer State Fallback ── */
// The 3D bird module is pending integration, so we use CSS to reflect state on the wrapper
function setVisualizerState(state) {
  const viz = document.querySelector('.viz-wrapper');
  if (!viz) return;

  viz.classList.remove('viz-listening', 'viz-processing', 'viz-speaking');

  if (state !== 'idle') {
    viz.classList.add(`viz-${state}`);
  }

  if (state === 'listening') setWave(true, 'listen');
  else if (state === 'speaking') setWave(true, '');
  else if (state === 'processing') setWave(true, 'processing');
  else setWave(false);
}

/* ── TTS: auto-select best English voice ── */
let selectedVoice = null;

function pickVoice() {
  const all = speechSynthesis.getVoices();
  if (!all.length) return;
  const PRIORITY = [
    v => v.name === "Google UK English Female",
    v => v.name === "Microsoft Zira - English (United States)",
    v => v.name === "Microsoft Aria Online (Natural) - English (United States)",
    v => v.name === "Google US English" && v.lang === "en-US",
    v => /female/i.test(v.name) && v.lang.startsWith("en"),
    v => /zira|aria|samantha|karen|moira|victoria|fiona|susan|kate|emily|sophie|amy|joanna|salli|kendra|kimberly/i.test(v.name) && v.lang.startsWith("en"),
    v => v.lang === "en-US",
    v => v.lang.startsWith("en"),
  ];
  for (const test of PRIORITY) {
    const match = all.find(test);
    if (match) { selectedVoice = match; return; }
  }
  selectedVoice = all[0];
}
speechSynthesis.onvoiceschanged = pickVoice;
pickVoice();

/* ── Strip Markdown for TTS ── */
function cleanForSpeech(raw) {
  let text = raw;
  // Remove code blocks entirely
  text = text.replace(/```[\s\S]*?```/g, ". See the code in the chat. ");
  // Remove inline code backticks
  text = text.replace(/`([^`]+)`/g, "$1");
  // Remove headers markers
  text = text.replace(/^#{1,6}\s+/gm, "");
  // Remove bold/italic markers
  text = text.replace(/\*\*\*(.+?)\*\*\*/g, "$1");
  text = text.replace(/\*\*(.+?)\*\*/g, "$1");
  text = text.replace(/__(.+?)__/g, "$1");
  text = text.replace(/\*(.+?)\*/g, "$1");
  text = text.replace(/_(.+?)_/g, "$1");
  // Remove list markers
  text = text.replace(/^\s*[-*•]\s+/gm, "");
  text = text.replace(/^\s*\d+\.\s+/gm, "");
  // Remove horizontal rules
  text = text.replace(/^---+$/gm, "");
  // Clean up whitespace
  text = text.replace(/\n{2,}/g, ". ").replace(/\n/g, ". ");
  text = text.replace(/\.\s*\./g, ".").replace(/\s{2,}/g, " ");
  return text.trim();
}

/* ── UI Helpers ── */
function setWave(active, mode) {
  ["waveLeft", "waveRight"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.className = "waveform" + (active ? " active" + (mode ? " " + mode : "") : "");
  });
}

function showConversation() {
  document.getElementById("idleState").style.display = "none";
  document.getElementById("dateSep").style.display = "block";
  document.getElementById("messagesWrap").classList.add("visible");
}

function now() {
  const d = new Date();
  return `${d.getHours()}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function addMessage(role, text) {
  showConversation();
  msgCount++;
  document.getElementById("msgCounter").textContent = `${msgCount} message${msgCount !== 1 ? "s" : ""}`;

  const wrap = document.getElementById("messagesWrap");
  const row = document.createElement("div");
  row.className = `msg-group ${role}`;

  const av = document.createElement("div");
  av.className = `msg-av ${role === "user" ? "user" : "bot"}`;
  av.textContent = role === "user" ? STUDENT_ROLL.slice(0, 2).toUpperCase() : "IM";

  const col = document.createElement("div");
  col.className = "msg-col";

  const sender = document.createElement("div");
  sender.className = "msg-sender";
  sender.textContent = role === "user" ? STUDENT_ROLL : "INTELLMIND";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";

  // Bot messages get rendered markdown, user messages are plain text
  if (role === "bot" || role === "assistant") {
    bubble.innerHTML = renderMarkdown(text);
  } else {
    bubble.textContent = text;
  }

  const time = document.createElement("div");
  time.className = "msg-time";
  time.textContent = now();

  // Entrance animation
  row.style.opacity = "0";
  row.style.transform = "translateY(12px)";

  col.appendChild(sender);
  col.appendChild(bubble);
  col.appendChild(time);
  row.appendChild(av);
  row.appendChild(col);
  wrap.appendChild(row);

  requestAnimationFrame(() => {
    row.style.transition = "opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1), transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)";
    row.style.opacity = "1";
    row.style.transform = "translateY(0)";
  });

  const chatArea = document.getElementById("chatArea");
  setTimeout(() => { chatArea.scrollTop = chatArea.scrollHeight; }, 60);
}

function showTyping(on) {
  document.getElementById("typingRow").classList.toggle("visible", on);
  if (on) {
    const chatArea = document.getElementById("chatArea");
    setTimeout(() => { chatArea.scrollTop = chatArea.scrollHeight; }, 60);
  }
}

function resetChat() {
  document.getElementById("messagesWrap").innerHTML = "";
  document.getElementById("messagesWrap").classList.remove("visible");
  document.getElementById("dateSep").style.display = "none";
  document.getElementById("idleState").style.display = "";
  showTyping(false);
  speechSynthesis.cancel();
  stopTTSKeepAlive();
  isSpeaking = false;
  isProcessing = false;
  msgCount = 0;
  autoListenFailCount = 0;
  voiceHistory = [];
  sessionStorage.removeItem("im_voice_history");
  document.getElementById("msgCounter").textContent = "0 messages";
  setStatus("idle");
  setWave(false);
}

/* ── Speech Recognition ── */
let silenceTimer = null;
const SILENCE_TIMEOUT = 3000;

function clearSilenceTimer() {
  if (silenceTimer) { clearTimeout(silenceTimer); silenceTimer = null; }
}

function startSilenceTimer() {
  clearSilenceTimer();
  silenceTimer = setTimeout(() => {
    if (isListening && recognition) {
      console.log("[voice] Silence detected, stopping...");
      recognition.stop();
    }
  }, SILENCE_TIMEOUT);
}

function initRecognition() {
  if (recognition) return recognition; // Reuse existing instance

  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    showToast("Speech recognition not supported. Please use Chrome or Edge.");
    return null;
  }

  const r = new SR();
  r.continuous = true;
  r.interimResults = true;
  r.lang = "en-US";

  r.onstart = () => {
    isListening = true;
    finalTranscript = "";
    autoListenFailCount = 0; // Reset on successful start
    document.getElementById("micBtn").classList.add("listening");
    document.getElementById("liveStrip").classList.add("active");
    document.getElementById("liveText").textContent = "";
    setWave(true, "listen");
    setStatus("listening");
    startSilenceTimer();
  };

  r.onresult = (e) => {
    let interim = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      if (e.results[i].isFinal) finalTranscript += e.results[i][0].transcript + " ";
      else interim += e.results[i][0].transcript;
    }
    document.getElementById("liveText").textContent = (finalTranscript + interim).trim();
    startSilenceTimer();
  };

  r.onend = () => {
    clearSilenceTimer();
    isListening = false;
    document.getElementById("micBtn").classList.remove("listening");
    document.getElementById("liveStrip").classList.remove("active");
    document.getElementById("liveText").textContent = "";
    setWave(false);

    const text = finalTranscript.trim();
    if (text) {
      addMessage("user", text);
      
      // Save user message to history immediately
      voiceHistory.push({ role: "user", text: text });
      if (voiceHistory.length > 20) voiceHistory = voiceHistory.slice(-20);
      sessionStorage.setItem("im_voice_history", JSON.stringify(voiceHistory));

      callBackend(text);
    } else {
      setStatus("idle");
    }
  };

  r.onerror = (e) => {
    clearSilenceTimer();
    isListening = false;
    document.getElementById("micBtn").classList.remove("listening");
    document.getElementById("liveStrip").classList.remove("active");
    setWave(false);
    setStatus("idle");

    // Track auto-listen failures to prevent infinite loops
    autoListenFailCount++;

    if (e.error === "not-allowed" || e.error === "permission-denied") {
      showToast("Microphone access denied. Please allow microphone permission in your browser settings.");
      autoListenNext = false; // Disable auto-listen if mic is blocked
      const btn = document.getElementById("autoListenBtn");
      if (btn) btn.classList.remove("active");
    } else if (e.error === "network") {
      showToast("Network error — speech recognition requires an internet connection.");
    } else if (e.error !== "no-speech" && e.error !== "aborted") {
      showToast(`Mic error: ${e.error}`);
    }
  };

  return r;
}

function toggleMic() {
  if (isSpeaking) {
    stopSpeaking();
    return;
  }
  if (isListening) {
    clearSilenceTimer();
    recognition && recognition.stop();
  } else if (!isProcessing) {
    // Request microphone permission explicitly
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then((stream) => {
          // Permission granted — stop the test stream and start recognition
          stream.getTracks().forEach(t => t.stop());
          if (!recognition) recognition = initRecognition();
          if (recognition) {
            try {
              recognition.start();
            } catch (e) {
              console.warn("[voice] Error starting recognition after mic grant:", e);
            }
          }
        })
        .catch((err) => {
          console.error("[voice] Mic permission error:", err);
          if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
            showToast("Microphone access denied. Please allow mic permission in browser settings.");
          } else if (err.name === "NotFoundError") {
            showToast("No microphone detected. Please connect a mic and try again.");
          } else {
            showToast("Could not access microphone: " + err.message);
          }
        });
    } else {
      // Fallback for browsers without getUserMedia
      recognition = initRecognition();
      if (recognition) {
        try {
          recognition.start();
        } catch (e) {
          console.warn("[voice] Error starting recognition (fallback):", e);
        }
      }
    }
  }
}

/* ── TTS (Text-to-Speech) ── */
function speak(rawText) {
  speechSynthesis.cancel();
  stopTTSKeepAlive();

  const cleanText = cleanForSpeech(rawText);
  const speakText = cleanText.length > 2000 ? cleanText.slice(0, 2000) + ". That's the summary. See the full response in the chat." : cleanText;

  const utt = new SpeechSynthesisUtterance(speakText);
  if (selectedVoice) utt.voice = selectedVoice;
  utt.rate = 1.0;
  utt.pitch = 1.05;

  utt.onstart = () => {
    isSpeaking = true;
    setWave(true, "");
    document.getElementById("stopBtn").disabled = false;
    setStatus("speaking");
    startTTSKeepAlive(); // Prevent Chrome from pausing after 15s
  };

  utt.onend = () => {
    isSpeaking = false;
    setWave(false);
    stopTTSKeepAlive();
    document.getElementById("stopBtn").disabled = true;
    setStatus("idle");

    // Auto-listen for next question (with retry guard)
    if (autoListenNext && autoListenFailCount < MAX_AUTO_LISTEN_FAILS) {
      setTimeout(() => {
        if (!isSpeaking && !isListening && !isProcessing) {
          recognition = initRecognition();
          if (recognition) {
            try {
              recognition.start();
            } catch (e) {
              console.warn("[voice] Auto-listen start failed:", e);
              autoListenFailCount++;
            }
          }
        }
      }, 800);
    } else if (autoListenFailCount >= MAX_AUTO_LISTEN_FAILS) {
      console.log("[voice] Auto-listen disabled after repeated failures");
      showToast("Auto-listen paused. Tap mic to speak.");
      autoListenFailCount = 0; // Reset for next manual trigger
    }
  };

  utt.onerror = (e) => {
    isSpeaking = false;
    setWave(false);
    stopTTSKeepAlive();
    document.getElementById("stopBtn").disabled = true;
    setStatus("idle");
    console.warn("[voice] TTS error:", e.error);
  };

  speechSynthesis.speak(utt);
}

function stopSpeaking() {
  speechSynthesis.cancel();
  stopTTSKeepAlive();
  isSpeaking = false;
  setWave(false);
  document.getElementById("stopBtn").disabled = true;
  setStatus("idle");
}

/* ── Backend Call ── */
async function callBackend(userText) {
  isProcessing = true;
  showTyping(true);
  setStatus("processing");

  try {
    const token = await getAuthToken();
    const res = await fetch(VOICE_CHAT_URL, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        message: userText,
        student_roll: STUDENT_ROLL,
        mode: "voice"
      })
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Backend error ${res.status}`);
    }

    const data = await res.json();
    const reply = data.response;

    showTyping(false);
    isProcessing = false;
    addMessage("bot", reply);

    // Save bot reply to history
    voiceHistory.push({ role: "bot", text: reply });
    if (voiceHistory.length > 20) voiceHistory = voiceHistory.slice(-20);
    sessionStorage.setItem("im_voice_history", JSON.stringify(voiceHistory));

    speak(reply);

  } catch (err) {
    showTyping(false);
    isProcessing = false;
    setStatus("idle");

    // Provide actionable error messages
    if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
      showToast("Cannot reach server. Make sure the backend is running (uvicorn main:app --reload).");
    } else {
      showToast("Error: " + err.message);
    }
  }
}

/* ── Auto-listen toggle ── */
function toggleAutoListen() {
  autoListenNext = !autoListenNext;
  autoListenFailCount = 0; // Reset counter on manual toggle
  const btn = document.getElementById("autoListenBtn");
  btn.classList.toggle("active", autoListenNext);
  btn.title = autoListenNext ? "Auto-listen ON — will start mic after response" : "Auto-listen OFF";
}

// Init auto-listen button state
const autoBtn = document.getElementById("autoListenBtn");
if (autoBtn) autoBtn.classList.toggle("active", autoListenNext);

// Load history from session
(function loadHistory() {
  const saved = sessionStorage.getItem("im_voice_history");
  if (saved) {
    const history = JSON.parse(saved);
    if (history.length > 0) {
      voiceHistory = history;
      history.forEach(m => {
        addMessage(m.role, m.text);
      });
    }
  }
})();

// Voice fully initialized