/* ============================================================
   roadmap.js — Roadmap Planner Frontend Logic
   ============================================================
   INTEGRATION FIXES (Bhagya → Main Project):
   - Removed hardcoded API_BASE http://localhost:8000
   - Now uses window.INTELLIMIND_API_BASE (set by HTML, same as other pages)
   - Auth reads from sessionStorage im_roll (consistent with chat/doc pages)
   - Duration options: 7, 15, 21, 30 days
   ============================================================ */

// API_BASE is provided by shared/js/config.js (loaded before this script)

// ─── State ────────────────────────────────────────────────────────────────────
let selectedDuration = 7;
let allPlans         = [];
let openPlanId       = null;
let roll             = "";

// ─── DOM Refs ─────────────────────────────────────────────────────────────────
const plansList      = () => document.getElementById("plansList");
const todayBanner    = () => document.getElementById("todayBanner");
const todayTaskEl    = () => document.getElementById("todayTaskText");
const todayMetaEl    = () => document.getElementById("todayMeta");
const todayDayEl     = () => document.getElementById("todayDay");
const todayDoneBtnEl = () => document.getElementById("todayDoneBtn");
const loadingOverlay = () => document.getElementById("loadingOverlay");
const limitDots      = () => [document.getElementById("dot0"), document.getElementById("dot1"), document.getElementById("dot2")];
const limitLabel     = () => document.getElementById("limitLabel");
const limitWarn      = () => document.getElementById("limitWarn");

// ─── Initialise ───────────────────────────────────────────────────────────────
window.addEventListener("load", async () => {
  roll = sessionStorage.getItem("im_roll") || "";
  if (!roll) return;
  await loadPlans();
  await loadActivePlan();
});

// ─── Duration Selector ────────────────────────────────────────────────────────
function selectDuration(days) {
  selectedDuration = days;
  document.querySelectorAll(".dur-btn").forEach(b => {
    b.classList.toggle("selected", parseInt(b.dataset.days) === days);
  });
}
window.selectDuration = selectDuration;

// ─── Generate Plan ────────────────────────────────────────────────────────────
async function generatePlan() {
  if (!roll) return showRoadmapToast("Not logged in", "error");

  const usedCount = allPlans.filter(p => {
    const created = new Date(p.created_at);
    const now = new Date();
    return created.getMonth() === now.getMonth() && created.getFullYear() === now.getFullYear();
  }).length;
  if (usedCount >= 3) return showRoadmapToast("Monthly limit reached (3 plans/month)", "error");

  const btn = document.getElementById("genBtn");
  btn.disabled = true;
  btn.innerHTML = `<div class="gen-spinner"></div> Generating… (up to 2 min)`;
  loadingOverlay().classList.remove("hidden");

  try {
    const controller = new AbortController();
    const timeoutId  = setTimeout(() => controller.abort(), 180000);

    const topicInput = document.getElementById("roadmapTopic");
    const topicText  = topicInput ? topicInput.value.trim() : "";

    const res = await fetch(`${API_BASE}/roadmap/generate`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ student_roll: roll, duration_days: selectedDuration, topic: topicText }),
      signal:  controller.signal,
    });
    if (topicInput) topicInput.value = "";
    clearTimeout(timeoutId);

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Generation failed");
    }

    showRoadmapToast(`✅ Plan created: ${data.title}`, "success");
    await loadPlans();
    await loadActivePlan();

  } catch (e) {
    if (e.name === "AbortError") {
      showRoadmapToast("⏳ Request timed out — AI is busy. Please try again in a moment.", "error");
    } else if (e.message && e.message.includes("progress")) {
      showRoadmapToast("⚠️ " + e.message, "error");
    } else {
      showRoadmapToast(e.message || "Something went wrong.", "error");
    }
  } finally {
    btn.disabled = false;
    btn.innerHTML = `
      <svg viewBox="0 0 24 24"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
      Generate Plan`;
    loadingOverlay().classList.add("hidden");
  }
}
window.generatePlan = generatePlan;

// ─── Load All Plans ───────────────────────────────────────────────────────────
async function loadPlans() {
  try {
    const res  = await fetch(`${API_BASE}/roadmap/plans/${roll}`);
    const data = await res.json();
    allPlans   = data.plans || [];
    renderPlansList(allPlans, data.plans_used_this_month, data.plans_remaining_this_month);
  } catch (e) {
    console.error("[roadmap] loadPlans error:", e);
  }
}

function renderPlansList(plans, used, remaining) {
  // Update limit dots
  limitDots().forEach((dot, i) => {
    dot.classList.remove("used", "maxed");
    if (i < used) dot.classList.add(used >= 3 ? "maxed" : "used");
  });
  limitLabel().textContent = `${used}/3 plans created this month`;

  if (used >= 3) {
    limitWarn().classList.remove("hidden");
    document.getElementById("genBtn").disabled = true;
  } else {
    limitWarn().classList.add("hidden");
    document.getElementById("genBtn").disabled = false;
  }

  const container = plansList();
  if (!plans || plans.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        </div>
        <div class="empty-title">No plans yet</div>
        <div class="empty-sub">Generate your first AI study plan to get started!</div>
      </div>`;
    return;
  }

  container.innerHTML = plans.map(plan => {
    const tasks     = plan.plan_tasks || [];
    const completed = tasks.filter(t => t.status === "completed").length;
    const total     = tasks.length;
    const pct       = total ? Math.round((completed / total) * 100) : 0;
    const isActive  = plan.is_active;
    const isOpen    = plan.id === openPlanId;
    const date      = new Date(plan.created_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });

    return `
    <div class="plan-card ${isActive ? "active-plan" : ""} ${isOpen ? "open" : ""}" data-id="${plan.id}">
      <div class="plan-card-header" onclick="togglePlan('${plan.id}')">
        <div class="plan-card-left">
          <div class="plan-title">${plan.title}</div>
          <div class="plan-meta">${plan.duration_days} days · Created ${date}</div>
        </div>
        <div class="plan-card-right">
          ${isActive ? '<span class="badge-active">Active</span>' : ''}
          <div class="plan-progress-ring">
            <svg viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="3"/>
              <circle cx="18" cy="18" r="15.9" fill="none" stroke="var(--green)" stroke-width="3"
                stroke-dasharray="${pct} ${100 - pct}" stroke-dashoffset="25" stroke-linecap="round"/>
            </svg>
            <span class="pct-text">${pct}%</span>
          </div>
          <svg class="chevron-icon" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
      </div>

      ${isOpen ? `
      <div class="plan-detail">
        ${!isActive ? `<button class="btn-activate" onclick="activatePlan('${plan.id}')">Set as Active Plan</button>` : ""}
        <div class="task-list">
          ${tasks.sort((a,b) => a.day_number - b.day_number).map(t => `
            <div class="task-item ${t.status === 'completed' ? 'done' : ''}">
              <div class="task-day">${t.day_number}</div>
              <div class="task-content">
                <div class="task-desc">${t.description}</div>
                ${t.status !== 'completed'
                  ? `<button class="task-done-btn" onclick="markTaskDone('${t.id}')">Mark Done</button>`
                  : `<span class="task-check">✓</span>`}
              </div>
            </div>
          `).join("")}
        </div>
      </div>` : ""}
    </div>`;
  }).join("");
}

// ─── Toggle Plan Open/Close ───────────────────────────────────────────────────
function togglePlan(planId) {
  openPlanId = (openPlanId === planId) ? null : planId;
  const used = allPlans.filter(p => {
    const c = new Date(p.created_at), n = new Date();
    return c.getMonth() === n.getMonth() && c.getFullYear() === n.getFullYear();
  }).length;
  const remaining = Math.max(0, 3 - used);
  renderPlansList(allPlans, used, remaining);
}
window.togglePlan = togglePlan;

// ─── Activate Plan ────────────────────────────────────────────────────────────
async function activatePlan(planId) {
  try {
    const res  = await fetch(`${API_BASE}/roadmap/plans/${planId}/activate`, { method: "PATCH" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Could not activate plan");
    showRoadmapToast("✅ Plan activated!", "success");
    await loadPlans();
    await loadActivePlan();
  } catch (e) {
    showRoadmapToast(e.message, "error");
  }
}
window.activatePlan = activatePlan;

// ─── Mark Task Done ───────────────────────────────────────────────────────────
async function markTaskDone(taskId) {
  try {
    const res  = await fetch(`${API_BASE}/roadmap/tasks/${taskId}/complete`, { method: "PATCH" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Could not mark task done");
    showRoadmapToast("✅ Task completed!", "success");
    await loadPlans();
    await loadActivePlan();
  } catch (e) {
    showRoadmapToast(e.message, "error");
  }
}
window.markTaskDone = markTaskDone;

// ─── Load Active Plan ─────────────────────────────────────────────────────────
async function loadActivePlan() {
  try {
    const res  = await fetch(`${API_BASE}/roadmap/active/${roll}`);
    const data = await res.json();

    if (!data.active_plan || !data.today_task) {
      todayBanner() && todayBanner().classList.add("hidden");
      return;
    }

    const task = data.today_task;
    todayDayEl()    && (todayDayEl().textContent  = `Day ${data.today_day}`);
    todayTaskEl()   && (todayTaskEl().textContent  = task.description);
    todayMetaEl()   && (todayMetaEl().textContent  = task.status === "completed" ? "✅ Completed" : "");
    todayBanner()   && todayBanner().classList.remove("hidden");

    // Today's done button
    const btn = todayDoneBtnEl();
    if (btn) {
      if (task.status === "completed") {
        btn.textContent = "✓ Done";
        btn.disabled    = true;
      } else {
        btn.textContent  = "Mark Done";
        btn.disabled     = false;
        btn.onclick      = () => markTaskDone(task.id);
      }
    }

    // Show completion message if whole plan is done
    if (data.is_complete) {
      todayTaskEl() && (todayTaskEl().textContent = "🎉 All tasks completed! Generate a new plan when you're ready.");
      todayMetaEl() && (todayMetaEl().textContent = "Plan complete");
      if (btn) { btn.textContent = "Complete!"; btn.disabled = true; }
    }

  } catch (e) {
    console.error("[roadmap] loadActivePlan error:", e);
  }
}

// ─── Toast Helper (local — doesn't clash with shared toast.js) ────────────────
function showRoadmapToast(msg, type = "info") {
  if (typeof showToast === "function") {
    showToast(msg);
    return;
  }
  const el = document.createElement("div");
  el.className = `roadmap-toast roadmap-toast--${type}`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}
