/**
 * AERIS Movement Intelligence & Biomechanical Analysis Frontend Engine
 * Handles API calls, authentication tokens, status polling, data binding, and interactions.
 */

const API_BASE = window.location.origin;

// ── Auth Token Helpers ──────────────────────────────────────────────────
function getAuthToken() {
  return localStorage.getItem("aeris_token") || "";
}

function setAuthToken(token, user) {
  localStorage.setItem("aeris_token", token);
  if (user) {
    localStorage.setItem("aeris_user", JSON.stringify(user));
  }
}

function clearAuth() {
  localStorage.removeItem("aeris_token");
  localStorage.removeItem("aeris_user");
}

function getCurrentUser() {
  try {
    const userStr = localStorage.getItem("aeris_user");
    return userStr ? JSON.parse(userStr) : null;
  } catch (e) {
    return null;
  }
}

// ── Toast Notification Engine ───────────────────────────────────────────
function showToast(message, type = "info") {
  let toastContainer = document.getElementById("aeris-toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "aeris-toast-container";
    toastContainer.className = "fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-md w-full px-4 pointer-events-none";
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement("div");
  const bg = type === "error" ? "bg-red-600 text-white" : type === "success" ? "bg-emerald-600 text-white" : "bg-slate-900 text-white";
  const icon = type === "error" ? "error" : type === "success" ? "check_circle" : "info";

  toast.className = `${bg} shadow-xl rounded-xl p-4 flex items-center gap-3 transition-all transform translate-y-2 opacity-0 pointer-events-auto text-sm font-medium`;
  toast.innerHTML = `
    <span class="material-symbols-outlined shrink-0">${icon}</span>
    <span class="flex-1">${message}</span>
    <button onclick="this.parentElement.remove()" class="opacity-70 hover:opacity-100"><span class="material-symbols-outlined text-base">close</span></button>
  `;

  toastContainer.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.remove("translate-y-2", "opacity-0");
  });

  setTimeout(() => {
    if (toast.parentElement) {
      toast.classList.add("translate-y-2", "opacity-0");
      setTimeout(() => toast.remove(), 300);
    }
  }, 4500);
}

// ── API Methods ─────────────────────────────────────────────────────────
async function apiRequest(endpoint, method = "GET", body = null) {
  const headers = {};
  const token = getAuthToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let options = { method, headers };

  if (body) {
    if (body instanceof FormData) {
      options.body = body;
    } else {
      headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(body);
    }
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errData.detail || `Request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`[AERIS API Error] ${method} ${endpoint}:`, err);
    throw err;
  }
}

// ── Biomechanical Risk Level Badge Generator ───────────────────────────
function getRiskBadgeHTML(riskLevel, score = null) {
  const level = (riskLevel || "").toUpperCase();
  const scoreText = score !== null ? ` (${score.toFixed(1)}%)` : "";
  if (level === "LOW") {
    return `<span class="badge-low"><span class="material-symbols-outlined text-sm">shield</span> Low Risk${scoreText}</span>`;
  } else if (level === "MODERATE" || level === "MEDIUM") {
    return `<span class="badge-mod"><span class="material-symbols-outlined text-sm">warning</span> Moderate Risk${scoreText}</span>`;
  } else if (level === "HIGH" || level === "CRITICAL") {
    return `<span class="badge-high"><span class="material-symbols-outlined text-sm">error</span> High Risk${scoreText}</span>`;
  } else {
    return `<span class="badge-low"><span class="material-symbols-outlined text-sm">help</span> ${level || 'Normal'}${scoreText}</span>`;
  }
}

// Global user profile display updater across headers & drawer navigation
function updateUserDisplay(user) {
  if (!user) return;
  localStorage.setItem("aeris_user", JSON.stringify(user));
  
  const userNameElems = document.querySelectorAll(".user-display-name");
  const userRoleElems = document.querySelectorAll(".user-display-role");
  const userAvatarElems = document.querySelectorAll(".user-display-avatar");

  const initials = (user.full_name || "Alex Morgan")
    .split(" ")
    .filter(Boolean)
    .map(n => n[0])
    .join("")
    .substring(0, 2)
    .toUpperCase();

  userNameElems.forEach(el => el.textContent = user.full_name || "Alex Morgan");
  userRoleElems.forEach(el => el.textContent = user.role ? user.role.toUpperCase() : "ATHLETE");
  userAvatarElems.forEach(el => el.textContent = initials || "AM");
}
window.updateUserDisplay = updateUserDisplay;

document.addEventListener("DOMContentLoaded", () => {
  // Initialize mobile navigation drawer FIRST so elements exist in DOM
  initMobileDrawer();

  const user = getCurrentUser();
  if (user) {
    updateUserDisplay(user);
  }

  if (getAuthToken()) {
    apiRequest("/api/user/profile", "GET")
      .then(latestUser => {
        updateUserDisplay(latestUser);
      })
      .catch(err => console.log("[AERIS] Profile sync error:", err));
  }

  // Enforce profile navigation when clicking avatar or user display name
  const profileClickTargets = document.querySelectorAll(".user-display-avatar, .user-display-name, .user-display-role");
  profileClickTargets.forEach(el => {
    el.style.cursor = "pointer";
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      window.location.href = "/profile.html";
    });
  });
});

// ── Hamburger Mobile Drawer Engine ─────────────────────────────────────
function initMobileDrawer() {
  let drawerOverlay = document.getElementById("aeris-mobile-drawer");
  if (!drawerOverlay) {
    drawerOverlay = document.createElement("div");
    drawerOverlay.id = "aeris-mobile-drawer";
    drawerOverlay.className = "fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm hidden transition-opacity duration-300 opacity-0";
    
    const currentPath = window.location.pathname;
    const isActive = (path) => currentPath.endsWith(path) || (path === '/dashboard.html' && currentPath === '/');

    drawerOverlay.innerHTML = `
      <div id="aeris-drawer-panel" class="w-[285px] max-w-[85vw] h-full bg-black text-zinc-300 p-6 flex flex-col justify-between shadow-2xl transform -translate-x-full transition-transform duration-300 ease-out border-r border-zinc-900">
        <div>
          <div class="flex justify-between items-center pb-6 border-b border-zinc-900 mb-6">
            <img src="/logo.png" alt="AERIS Logo" class="h-10 w-auto object-contain bg-[#fafbfa] px-3 py-1.5 rounded-xl shadow-md">
            <button id="aeris-drawer-close" class="text-zinc-400 hover:text-white p-1.5 rounded-xl hover:bg-zinc-900 transition-colors cursor-pointer">
              <span class="material-symbols-outlined text-xl">close</span>
            </button>
          </div>
          
          <nav class="space-y-2">
            <a href="/dashboard.html" class="flex items-center gap-3.5 px-4 py-3 rounded-xl font-bold text-sm transition-all ${isActive('dashboard.html') || currentPath === '/' ? 'bg-emerald-600 text-white shadow-md' : 'text-zinc-300 hover:text-white hover:bg-zinc-900'}">
              <span class="material-symbols-outlined text-xl">dashboard</span> Overview
            </a>
            <a href="/reports.html" class="flex items-center gap-3.5 px-4 py-3 rounded-xl font-bold text-sm transition-all ${isActive('reports.html') ? 'bg-emerald-600 text-white shadow-md' : 'text-zinc-300 hover:text-white hover:bg-zinc-900'}">
              <span class="material-symbols-outlined text-xl">assessment</span> Reports & Analysis
            </a>
            <a href="/history.html" class="flex items-center gap-3.5 px-4 py-3 rounded-xl font-bold text-sm transition-all ${isActive('history.html') ? 'bg-emerald-600 text-white shadow-md' : 'text-zinc-300 hover:text-white hover:bg-zinc-900'}">
              <span class="material-symbols-outlined text-xl">monitoring</span> Fatigue & Progress
            </a>
            <a href="/settings.html" class="flex items-center gap-3.5 px-4 py-3 rounded-xl font-bold text-sm transition-all ${isActive('settings.html') || isActive('profile.html') ? 'bg-emerald-600 text-white shadow-md' : 'text-zinc-300 hover:text-white hover:bg-zinc-900'}">
              <span class="material-symbols-outlined text-xl">settings</span> Settings
            </a>
          </nav>
        </div>

        <!-- Bottom Profile & Log Out Option -->
        <div class="pt-4 border-t border-zinc-900 flex items-center justify-between">
          <a href="/profile.html" title="View Athlete Profile" class="flex items-center gap-3 group hover:opacity-90 transition-opacity">
            <div class="w-9 h-9 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center user-display-avatar shadow-md group-hover:scale-105 transition-transform">
              AM
            </div>
            <div class="text-left">
              <div class="text-xs font-bold text-white leading-none user-display-name group-hover:text-emerald-400">Alex Morgan</div>
              <div class="text-[10px] text-emerald-400 font-semibold uppercase tracking-wider user-display-role">Athlete</div>
            </div>
          </a>
          <button id="aeris-logout-btn" title="Log Out" class="p-2 rounded-xl text-zinc-400 hover:text-red-400 hover:bg-zinc-900 transition-colors cursor-pointer flex items-center justify-center">
            <span class="material-symbols-outlined text-xl">logout</span>
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(drawerOverlay);

    const openDrawer = () => {
      const u = getCurrentUser();
      if (u) updateUserDisplay(u);
      drawerOverlay.classList.remove("hidden");
      requestAnimationFrame(() => {
        drawerOverlay.classList.remove("opacity-0");
        document.getElementById("aeris-drawer-panel")?.classList.remove("-translate-x-full");
      });
    };

    const closeDrawer = () => {
      const panel = document.getElementById("aeris-drawer-panel");
      if (panel) panel.classList.add("-translate-x-full");
      drawerOverlay.classList.add("opacity-0");
      setTimeout(() => {
        drawerOverlay.classList.add("hidden");
      }, 300);
    };

    drawerOverlay.addEventListener("click", (e) => {
      if (e.target === drawerOverlay || e.target.closest("#aeris-drawer-close")) {
        closeDrawer();
      }
    });

    // Logout action handler
    const logoutBtn = document.getElementById("aeris-logout-btn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", (e) => {
        e.preventDefault();
        clearAuth();
        showToast("Logged out successfully!", "success");
        setTimeout(() => {
          window.location.href = "/login.html";
        }, 500);
      });
    }

    window.toggleAerisMobileDrawer = openDrawer;
  }

  // Attach click handler to hamburger buttons
  document.querySelectorAll("#aeris-menu-toggle, .aeris-hamburger-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      if (window.toggleAerisMobileDrawer) window.toggleAerisMobileDrawer();
    });
  });
}



