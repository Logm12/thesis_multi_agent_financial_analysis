// Trace Dashboard Frontend Core Logic

const API_BASE = "http://localhost:8001/api";
let jwtToken = localStorage.getItem("trace_admin_jwt");
let activeSessionId = null;
let sessionsData = [];
let sseSource = null;

// Initial state check
document.addEventListener("DOMContentLoaded", () => {
  setupApp();
});

function setupApp() {
  if (jwtToken) {
    showAppShell();
    fetchSessions();
  } else {
    showLoginModal();
  }
  registerEventHandlers();
}

function showLoginModal() {
  document.getElementById("login-modal").classList.remove("hidden");
  document.getElementById("app-shell").classList.add("hidden");
}

function showAppShell() {
  document.getElementById("login-modal").classList.add("hidden");
  document.getElementById("app-shell").classList.remove("hidden");
}

// Event Registrations
function registerEventHandlers() {
  // Login submission
  document.getElementById("login-form").addEventListener("submit", handleLogin);

  // Logout button
  document.getElementById("logout-btn").addEventListener("click", handleLogout);

  // Tab selections
  document.getElementById("nav-sessions").addEventListener("click", () => switchTab("sessions"));
  document.getElementById("nav-stats").addEventListener("click", () => switchTab("stats"));
  document.getElementById("nav-logs").addEventListener("click", () => switchTab("logs"));

  // Search input
  document.getElementById("search-sessions").addEventListener("input", filterSessionsList);

  // Refresh stats or sessions
  document.getElementById("refresh-btn").addEventListener("click", () => {
    const currentTab = document.querySelector(".nav-item.active").id;
    if (currentTab === "nav-sessions") {
      fetchSessions();
    } else if (currentTab === "nav-stats") {
      fetchStats();
    }
  });
}

// Login execution
async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById("username-input").value.trim();
  const password = document.getElementById("password-input").value;
  const errorDiv = document.getElementById("login-error");

  try {
    const response = await fetch(`${API_BASE}/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    if (response.ok && data.status === "success") {
      // Auth cookie is HttpOnly, but API also accepts Authorization Bearer
      // Parse token from custom return if cookie scheme fails
      // Look for JWT cookie extraction or retrieve from response headers/meta
      // The current backend login returns AuthResponse with user metadata.
      // Wait, we need to inspect user role. Let's look for tokens in Cookies or custom header.
      // Since response.set_cookie is HttpOnly, we request GET /me to obtain verification.
      
      // Let's perform a test fetch to check if our cookie is valid.
      const meResponse = await fetch(`${API_BASE}/v1/auth/me`);
      if (meResponse.ok) {
        const meData = await meResponse.json();
        if (meData.role === "ADMIN") {
          // Admin logged in successfully!
          jwtToken = "session_cookie_active";
          localStorage.setItem("trace_admin_jwt", jwtToken);
          showAppShell();
          fetchSessions();
          errorDiv.classList.add("hidden");
          return;
        }
      }
      
      // If backend requires JWT passing, we can also extract via mock or default token.
      // In python routes we parsed Bearer Token as fallback.
      // If backend returns cookie on set_cookie, subsequent requests will contain it.
      errorDiv.innerText = "Logged in but you do not have Admin privileges.";
      errorDiv.classList.remove("hidden");
    } else {
      errorDiv.innerText = data.detail || "Incorrect username or password.";
      errorDiv.classList.remove("hidden");
    }
  } catch (err) {
    console.error("Login request error", err);
    errorDiv.innerText = "Backend server unreachable.";
    errorDiv.classList.remove("hidden");
  }
}

function handleLogout() {
  fetch(`${API_BASE}/v1/auth/logout`, { method: "POST" }).finally(() => {
    localStorage.removeItem("trace_admin_jwt");
    jwtToken = null;
    if (sseSource) {
      sseSource.close();
    }
    showLoginModal();
  });
}

function switchTab(tabName) {
  // Navigation elements
  document.querySelectorAll(".nav-item").forEach(btn => btn.classList.remove("active"));
  document.getElementById(`nav-${tabName}`).classList.add("active");

  // Content panels
  document.getElementById("panel-sessions").classList.add("hidden");
  document.getElementById("panel-stats").classList.add("hidden");
  document.getElementById("panel-logs").classList.add("hidden");
  document.getElementById(`panel-${tabName}`).classList.remove("hidden");

  // Page title change
  const titles = {
    sessions: "Trace Audit Sessions",
    stats: "Token & Cost Statistics",
    logs: "Raw Logs Stream"
  };
  document.getElementById("page-title").innerText = titles[tabName];

  if (tabName === "stats") {
    fetchStats();
  } else if (tabName === "logs") {
    setupSSELogStream();
  }
}

// Fetch session lists
async function fetchSessions() {
  try {
    const res = await fetch(`${API_BASE}/traces/sessions`);
    if (res.status === 401 || res.status === 403) {
      handleLogout();
      return;
    }
    const data = await res.json();
    sessionsData = data;
    renderSessionsList(data);
  } catch (err) {
    console.error("Failed to load audit sessions", err);
  }
}

function renderSessionsList(sessions) {
  const container = document.getElementById("sessions-list");
  const countSpan = document.getElementById("session-count");
  container.innerHTML = "";
  countSpan.innerText = sessions.length;

  if (sessions.length === 0) {
    container.innerHTML = `<div class="p-6 text-center text-text-muted text-xs">No sessions tracked yet.</div>`;
    return;
  }

  sessions.forEach(s => {
    const item = document.createElement("div");
    item.className = `p-4 session-item flex flex-col gap-1 border-b border-border-subtle ${activeSessionId === s.thread_id ? 'selected' : ''}`;
    
    // Time formatting
    const timeStr = new Date(s.timestamp).toLocaleTimeString();
    const dateStr = new Date(s.timestamp).toLocaleDateString();

    item.innerHTML = `
      <div class="flex justify-between items-center">
        <span class="text-xs font-mono font-semibold text-text-primary truncate max-w-[150px]">${s.thread_id}</span>
        <span class="text-[10px] text-text-muted font-mono">${timeStr}</span>
      </div>
      <p class="text-xs text-text-secondary truncate mt-1">"${s.message}"</p>
      <div class="flex items-center justify-between mt-2">
        <span class="text-[10px] px-2 py-0.5 rounded ${s.total_cost > 0 ? 'bg-brand-subtle text-brand-light' : 'bg-white/5 text-text-muted'} font-mono">
          $${s.total_cost.toFixed(5)}
        </span>
        <span class="text-[10px] font-mono text-text-muted">${dateStr}</span>
      </div>
    `;

    item.addEventListener("click", () => selectSession(s));
    container.appendChild(item);
  });
}

function filterSessionsList() {
  const q = document.getElementById("search-sessions").value.toLowerCase();
  const filtered = sessionsData.filter(s => 
    s.thread_id.toLowerCase().includes(q) || 
    s.message.toLowerCase().includes(q)
  );
  renderSessionsList(filtered);
}

// Session details mapping
function selectSession(session) {
  activeSessionId = session.thread_id;
  
  // Highlight in sidebar
  document.querySelectorAll(".session-item").forEach(item => {
    const id = item.querySelector("span").innerText;
    if (id === session.thread_id) {
      item.classList.add("selected");
    } else {
      item.classList.remove("selected");
    }
  });

  // Display details panel
  document.getElementById("detail-placeholder").classList.add("hidden");
  document.getElementById("detail-content").classList.remove("hidden");

  // Populate data
  document.getElementById("detail-thread-id").innerText = session.thread_id;
  document.getElementById("detail-timestamp").innerText = new Date(session.timestamp).toLocaleString();
  document.getElementById("detail-message").innerText = `"${session.message}"`;
  document.getElementById("detail-final-answer").innerText = session.final_answer;

  // Render Gantt
  renderGanttChart(session);

  // Render Steps
  renderStepsTimeline(session.steps);

  // Render Token detailed breakdown
  renderTokenUsageDetails(session.token_usage);

  // Chart image
  const imgContainer = document.getElementById("chart-render-container");
  const imgEl = document.getElementById("detail-chart-img");
  if (session.chart_url) {
    imgEl.src = `http://localhost:8001${session.chart_url}?t=${Date.now()}`;
    imgContainer.classList.remove("hidden");
  } else {
    imgContainer.classList.add("hidden");
  }
}

function renderGanttChart(session) {
  const chart = document.getElementById("gantt-chart");
  chart.innerHTML = "";

  // Nodes to trace: router -> retriever -> coder -> synthesizer
  const flowNodes = ["router", "retriever", "coder", "synthesizer"];
  
  flowNodes.forEach(nodeName => {
    const record = session.token_usage.find(u => u.node_name === nodeName);
    const hasExecuted = !!record || session.steps.some(s => s.node === nodeName);

    const el = document.createElement("div");
    el.className = "flex flex-col gap-1 py-1";
    
    // Status style mapping
    let fillPct = 0;
    let label = "Skipped / Inactive";
    let colorClass = "bg-white/10";
    
    if (hasExecuted) {
      fillPct = 100;
      label = record ? `${record.model_name} ($${record.cost.toFixed(5)})` : "Executed (Utility)";
      colorClass = "var(--color-brand)";
    }

    el.innerHTML = `
      <div class="flex justify-between items-center text-xs">
        <span class="font-bold text-text-primary capitalize">${nodeName}</span>
        <span class="text-text-muted font-mono text-[10px]">${label}</span>
      </div>
      <div class="gantt-bar-bg mt-1">
        <div class="gantt-bar-fill" style="width: ${fillPct}%; background: ${colorClass}"></div>
      </div>
    `;
    chart.appendChild(el);
  });
}

function renderStepsTimeline(steps) {
  const area = document.getElementById("steps-timeline");
  area.innerHTML = "";

  if (steps.length === 0) {
    area.innerHTML = `<div class="text-text-muted">No thought logs recorded.</div>`;
    return;
  }

  steps.forEach(s => {
    const el = document.createElement("div");
    el.className = "border-l-2 border-brand/40 pl-3 py-1";
    el.innerHTML = `
      <div class="font-semibold text-text-primary text-[10px] uppercase">${s.node}</div>
      <div class="text-text-secondary mt-0.5">${s.output}</div>
    `;
    area.appendChild(el);
  });
}

function renderTokenUsageDetails(tokens) {
  const container = document.getElementById("node-token-details");
  container.innerHTML = "";

  if (tokens.length === 0) {
    container.innerHTML = `<div class="text-text-muted">No token metrics available (free tier / local run).</div>`;
    return;
  }

  tokens.forEach(t => {
    const el = document.createElement("div");
    el.className = "bg-white/5 p-2 rounded flex justify-between items-center gap-2";
    el.innerHTML = `
      <div>
        <div class="font-bold text-text-primary uppercase text-[10px]">${t.node_name}</div>
        <div class="text-[9px] text-text-muted truncate max-w-[180px]">${t.model_name}</div>
      </div>
      <div class="text-right">
        <div class="text-text-primary">${t.prompt_tokens + t.completion_tokens} tks</div>
        <div class="text-[10px] text-brand-light">$${t.cost.toFixed(5)}</div>
      </div>
    `;
    container.appendChild(el);
  });
}

// Fetch stats and render Canvas graphs
async function fetchStats() {
  try {
    const res = await fetch(`${API_BASE}/traces/stats`);
    const data = await res.json();

    document.getElementById("stat-total-cost").innerText = `$${data.total_cost.toFixed(6)}`;
    document.getElementById("stat-total-prompt").innerText = data.total_prompt_tokens.toLocaleString();
    document.getElementById("stat-total-completion").innerText = data.total_completion_tokens.toLocaleString();

    drawNodeChart(data.by_node);
    drawModelChart(data.by_model);
  } catch (err) {
    console.error("Failed to load statistics", err);
  }
}

function drawNodeChart(byNode) {
  const canvas = document.getElementById("node-bar-chart");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const entries = Object.entries(byNode);
  if (entries.length === 0) return;

  const maxVal = Math.max(...entries.map(([_, stats]) => stats.prompt + stats.completion)) || 1;
  const barWidth = 40;
  const spacing = 30;
  let startX = 50;

  // Render axes
  ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(35, 10);
  ctx.lineTo(35, 210);
  ctx.lineTo(380, 210);
  ctx.stroke();

  entries.forEach(([node, stats], i) => {
    const total = stats.prompt + stats.completion;
    const barHeight = (total / maxVal) * 180;
    const x = startX + i * (barWidth + spacing);
    const y = 210 - barHeight;

    // Draw bar gradient
    const grad = ctx.createLinearGradient(x, y, x, 210);
    grad.addColorStop(0, "#8251EE");
    grad.addColorStop(1, "rgba(130, 81, 238, 0.3)");
    ctx.fillStyle = grad;
    ctx.fillRect(x, y, barWidth, barHeight);

    // Text labels
    ctx.fillStyle = "#FFFFFF";
    ctx.font = "9px Outfit";
    ctx.textAlign = "center";
    ctx.fillText(total.toString(), x + barWidth / 2, y - 6);

    ctx.fillStyle = "#A1A1AA";
    ctx.fillText(node, x + barWidth / 2, 224);
  });
}

function drawModelChart(byModel) {
  const canvas = document.getElementById("model-bar-chart");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const entries = Object.entries(byModel);
  if (entries.length === 0) return;

  const maxVal = Math.max(...entries.map(([_, stats]) => stats.cost)) || 0.0001;
  const barWidth = 45;
  const spacing = 35;
  let startX = 60;

  // Render axes
  ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
  ctx.beginPath();
  ctx.moveTo(35, 10);
  ctx.lineTo(35, 210);
  ctx.lineTo(380, 210);
  ctx.stroke();

  entries.forEach(([model, stats], i) => {
    const cost = stats.cost;
    const barHeight = (cost / maxVal) * 180;
    const x = startX + i * (barWidth + spacing);
    const y = 210 - barHeight;

    // Draw bar gradient
    const grad = ctx.createLinearGradient(x, y, x, 210);
    grad.addColorStop(0, "#10B981");
    grad.addColorStop(1, "rgba(16, 185, 129, 0.2)");
    ctx.fillStyle = grad;
    ctx.fillRect(x, y, barWidth, barHeight);

    // Text labels
    ctx.fillStyle = "#FFFFFF";
    ctx.font = "9px Outfit";
    ctx.textAlign = "center";
    ctx.fillText(`$${cost.toFixed(4)}`, x + barWidth / 2, y - 6);

    ctx.fillStyle = "#A1A1AA";
    // Shorten model name if too long
    const modelShort = model.length > 10 ? model.substring(0, 8) + ".." : model;
    ctx.fillText(modelShort, x + barWidth / 2, 224);
  });
}

// SSE Logging Stream setup
function setupSSELogStream() {
  if (sseSource) {
    sseSource.close();
  }

  // Get active session token
  // Cookie auth does not require query param passing, but verification parses cookie.
  // We can pass access_token if cookie is read, currently using placeholder or jwtToken.
  const dummyToken = "auth_cookie"; // Cookies automatically sent by browser
  
  const statusIndicator = document.getElementById("sse-indicator");
  const statusText = document.getElementById("sse-status");
  const area = document.getElementById("sse-logs-area");

  statusIndicator.className = "w-3 h-3 rounded-full bg-status-warning animate-pulse";
  statusText.innerText = "Connecting to log stream...";

  // To pass admin verification, we pass the dummy token query. The backend verify_token parses hs256 JWT
  // But wait, SSE endpoint is authenticated. We need actual jwtToken inside request.
  // In `handleLogin` we set `jwtToken = "session_cookie_active"`.
  // Wait, the backend verify_token requires an actual JWT signature HS256!
  // How does verify_token get token?
  // Let's get the token value directly from browser cookies using document.cookie.
  const cookies = document.cookie.split(";").reduce((acc, c) => {
    const parts = c.split("=");
    acc[parts[0].trim()] = (parts[1] || "").trim();
    return acc;
  }, {});
  
  const rawJwtToken = cookies["access_token"] || "";

  sseSource = new EventSource(`${API_BASE}/traces/logs/stream?token=${rawJwtToken}`);

  sseSource.addEventListener("log_update", (e) => {
    const data = JSON.parse(e.data);
    
    statusIndicator.className = "w-3 h-3 rounded-full bg-status-success animate-pulse";
    statusText.innerText = "Stream connected";

    const timestamp = new Date(data.timestamp).toLocaleTimeString();
    const logItem = document.createElement("div");
    logItem.className = "py-1 border-b border-white/5 animate-in";
    logItem.innerHTML = `
      <span class="text-text-muted">[${timestamp}]</span> 
      <span class="text-brand">Thread ${data.thread_id.substring(0,8)}</span>: 
      <span class="text-text-secondary">${data.message}</span>
      <span class="text-text-muted"> (${data.token_usage ? data.token_usage.length : 0} LLM tasks recorded)</span>
    `;
    area.appendChild(logItem);
    area.scrollTop = area.scrollHeight;
  });

  sseSource.onerror = (err) => {
    console.error("SSE stream error", err);
    statusIndicator.className = "w-3 h-3 rounded-full bg-status-error";
    statusText.innerText = "Stream disconnected (reconnecting...)";
  };
}
