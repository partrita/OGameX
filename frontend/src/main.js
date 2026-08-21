import { translations } from "./i18n.js";

const API_BASE = "/api/v1/game";
const WS_BASE = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws`;

// Current state
let currentLang = localStorage.getItem("ogamex_lang") || "ko";
let activeTab = "overview";

// User session state
let currentUser = JSON.parse(localStorage.getItem("ogamex_user")) || {
  id: 1,
  username: "admin",
  planet_id: 1
};
let currentPlanetId = currentUser.planet_id || 1;

// Initialize App
document.addEventListener("DOMContentLoaded", async () => {
  setupLanguageSwitcher();
  setupNavigation();
  setupAuthHandlers();
  updateUserUI();
  applyLanguage(currentLang);

  await fetchPlanetOverview(currentPlanetId);
  setupFleetCalculator();
  setupGalaxyViewer();
  setupFleetDispatchForm();
  setupWebSocket(currentUser.id);
});

function updateUserUI() {
  const nameEl = document.getElementById("user-display-name");
  const btnLogout = document.getElementById("btn-logout");
  const btnShowAuth = document.getElementById("btn-show-auth");

  if (currentUser && currentUser.username) {
    nameEl.innerHTML = `사령관: <strong>${currentUser.username}</strong>`;
    btnLogout.classList.remove("hidden");
    btnShowAuth.classList.add("hidden");
  } else {
    nameEl.innerHTML = `<span>로그인이 필요합니다</span>`;
    btnLogout.classList.add("hidden");
    btnShowAuth.classList.remove("hidden");
  }
}

function setupAuthHandlers() {
  const modal = document.getElementById("auth-modal");
  const btnShowAuth = document.getElementById("btn-show-auth");
  const btnLogout = document.getElementById("btn-logout");
  const tabBtnLogin = document.getElementById("tab-btn-login");
  const tabBtnRegister = document.getElementById("tab-btn-register");
  const formLogin = document.getElementById("form-login");
  const formRegister = document.getElementById("form-register");

  btnShowAuth.addEventListener("click", () => {
    modal.classList.remove("hidden");
  });

  btnLogout.addEventListener("click", () => {
    localStorage.removeItem("ogamex_user");
    currentUser = null;
    updateUserUI();
    modal.classList.remove("hidden");
  });

  tabBtnLogin.addEventListener("click", () => {
    tabBtnLogin.classList.add("active");
    tabBtnRegister.classList.remove("active");
    formLogin.classList.remove("hidden");
    formRegister.classList.add("hidden");
  });

  tabBtnRegister.addEventListener("click", () => {
    tabBtnRegister.classList.add("active");
    tabBtnLogin.classList.remove("active");
    formRegister.classList.remove("hidden");
    formLogin.classList.add("hidden");
  });

  // Login Submit
  formLogin.addEventListener("submit", async (e) => {
    e.preventDefault();
    const u = document.getElementById("login-username").value.trim();
    const p = document.getElementById("login-password").value;

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: u, password: p })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "로그인 실패");

      currentUser = data;
      currentPlanetId = data.planet_id;
      localStorage.setItem("ogamex_user", JSON.stringify(data));
      updateUserUI();
      modal.classList.add("hidden");
      alert(`🚀 ${data.message} (${data.username} 사령관님 환영합니다!)`);

      await fetchPlanetOverview(currentPlanetId);
      switchTab("overview");
    } catch (err) {
      alert(`로그인 실패: ${err.message}`);
    }
  });

  // Register Submit
  formRegister.addEventListener("submit", async (e) => {
    e.preventDefault();
    const u = document.getElementById("reg-username").value.trim();
    const p = document.getElementById("reg-password").value;
    const pl = document.getElementById("reg-planet-name").value.trim();

    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: u, password: p, planet_name: pl })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "회원가입 실패");

      currentUser = data;
      currentPlanetId = data.planet_id;
      localStorage.setItem("ogamex_user", JSON.stringify(data));
      updateUserUI();
      modal.classList.add("hidden");
      alert(`🪐 ${data.message} 새 모행성이 좌표에 안착되었습니다!`);

      await fetchPlanetOverview(currentPlanetId);
      switchTab("overview");
    } catch (err) {
      alert(`회원가입 실패: ${err.message}`);
    }
  });
}


function setupNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tab = btn.getAttribute("data-tab");
      switchTab(tab);
    });
  });
}

function switchTab(tab) {
  activeTab = tab;
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-tab") === tab);
  });

  document.querySelectorAll(".view-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `tab-${tab}`);
  });

  if (tab === "resources") {
    loadResources();
  } else if (tab === "facilities") {
    loadFacilities();
  } else if (tab === "shipyard") {
    loadShipyard();
  } else if (tab === "fleet") {
    loadFleetDispatch();
  } else if (tab === "galaxy") {
    loadGalaxy(1, 100);
  } else if (tab === "overview") {
    fetchPlanetOverview(currentPlanetId);
  }
}

function setupLanguageSwitcher() {
  const btnKo = document.getElementById("btn-lang-ko");
  const btnEn = document.getElementById("btn-lang-en");

  btnKo.addEventListener("click", () => setLanguage("ko"));
  btnEn.addEventListener("click", () => setLanguage("en"));
}

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("ogamex_lang", lang);
  applyLanguage(lang);

  // Refresh active tab views
  if (activeTab === "resources") loadResources();
  else if (activeTab === "facilities") loadFacilities();
  else if (activeTab === "shipyard") loadShipyard();
  else if (activeTab === "fleet") loadFleetDispatch();
}

function applyLanguage(lang) {
  const dict = translations[lang] || translations.ko;

  document.getElementById("btn-lang-ko").classList.toggle("active", lang === "ko");
  document.getElementById("btn-lang-en").classList.toggle("active", lang === "en");

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.innerText = dict[key];
    }
  });

  const planetNameEl = document.getElementById("current-planet-name");
  if (planetNameEl.dataset.isCustom !== "true") {
    planetNameEl.innerText = dict.planetName;
  }
}

async function fetchPlanetOverview(planetId) {
  try {
    const res = await fetch(`${API_BASE}/planet/${planetId}/overview`);
    if (!res.ok) throw new Error("Failed to fetch planet data");
    const data = await res.json();
    renderPlanet(data);
  } catch (err) {
    console.warn("Backend not running or offline, using fallback state", err);
  }
}

// Live client-side resource interpolation state
let currentResources = { metal: 0, crystal: 0, deuterium: 0, energy: 0 };
let currentProduction = { metal: 0, crystal: 0, deuterium: 0 };
let resourceTickerInterval = null;

function startResourceTicker() {
  if (resourceTickerInterval) clearInterval(resourceTickerInterval);
  resourceTickerInterval = setInterval(() => {
    currentResources.metal += currentProduction.metal / 3600;
    currentResources.crystal += currentProduction.crystal / 3600;
    currentResources.deuterium += currentProduction.deuterium / 3600;

    const mEl = document.getElementById("res-metal");
    const cEl = document.getElementById("res-crystal");
    const dEl = document.getElementById("res-deut");

    if (mEl) mEl.innerText = Math.floor(currentResources.metal).toLocaleString();
    if (cEl) cEl.innerText = Math.floor(currentResources.crystal).toLocaleString();
    if (dEl) dEl.innerText = Math.floor(currentResources.deuterium).toLocaleString();
  }, 1000);
}

function renderPlanet(data) {
  const planetNameEl = document.getElementById("current-planet-name");
  if (data.name && data.name !== "Homeworld") {
    planetNameEl.innerText = data.name;
    planetNameEl.dataset.isCustom = "true";
  } else {
    planetNameEl.innerText = translations[currentLang].planetName;
  }

  document.getElementById("current-planet-coord").innerText = `[${data.coordinates.galaxy}:${data.coordinates.system}:${data.coordinates.position}]`;

  currentResources.metal = data.resources.metal;
  currentResources.crystal = data.resources.crystal;
  currentResources.deuterium = data.resources.deuterium;
  currentResources.energy = data.resources.energy;

  currentProduction.metal = data.resources.metal_production_hourly || 0;
  currentProduction.crystal = data.resources.crystal_production_hourly || 0;
  currentProduction.deuterium = data.resources.deuterium_production_hourly || 0;

  document.getElementById("res-metal").innerText = Math.floor(currentResources.metal).toLocaleString();
  document.getElementById("res-crystal").innerText = Math.floor(currentResources.crystal).toLocaleString();
  document.getElementById("res-deut").innerText = Math.floor(currentResources.deuterium).toLocaleString();
  document.getElementById("res-energy").innerText = (currentResources.energy >= 0 ? "+" : "") + Math.floor(currentResources.energy).toLocaleString();

  document.getElementById("stat-diameter").innerText = `${data.diameter.toLocaleString()} km`;
  document.getElementById("stat-fields").innerText = `${data.fields_used} / ${data.max_fields}`;
  document.getElementById("stat-temp").innerText = `${data.temp_min}°C ~ ${data.temp_max}°C`;

  startResourceTicker();
  renderActiveMissions(data.active_missions || []);
}

function renderActiveMissions(missions) {
  const tbody = document.getElementById("active-missions-body");
  const dict = translations[currentLang];
  if (!tbody) return;

  if (missions.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 16px;">
          ${dict.noActiveMissions || "현재 비행 중인 함대 미션이 없습니다."}
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = "";
  missions.forEach((m) => {
    const tr = document.createElement("tr");
    let missionIcon = "📦";
    let missionName = "수송 (Transport)";
    if (m.mission_type === "attack") { missionIcon = "⚔️"; missionName = "공격 (Attack)"; }
    else if (m.mission_type === "deploy") { missionIcon = "🛡️"; missionName = "배치 (Deploy)"; }
    else if (m.mission_type === "harvest") { missionIcon = "☄️"; missionName = "수거 (Harvest)"; }

    tr.innerHTML = `
      <td style="font-weight: 600;">${missionIcon} ${missionName}</td>
      <td style="font-family: var(--font-mono); color: var(--accent-cyan);">[${m.target_galaxy}:${m.target_system}:${m.target_position}]</td>
      <td><strong>${m.ships_count}</strong> 척</td>
      <td style="font-family: var(--font-mono); color: var(--accent-gold);">${formatSeconds(m.arrival_time_remaining)}</td>
      <td><span class="card-badge" style="background: rgba(16, 185, 129, 0.2); color: var(--accent-green); border-color: rgba(16, 185, 129, 0.4);">🚀 비행 중</span></td>
    `;
    tbody.appendChild(tr);
  });
}


// 1. Resources Tab
async function loadResources() {
  const container = document.getElementById("resources-list");
  const dict = translations[currentLang];
  container.innerHTML = `<div style="color: var(--text-muted);">Loading...</div>`;

  try {
    const res = await fetch(`${API_BASE}/planet/${currentPlanetId}/resources`);
    const data = await res.json();
    container.innerHTML = "";

    data.buildings.forEach((b) => {
      const card = document.createElement("div");
      card.className = "game-card glass-panel";
      card.innerHTML = `
        <div class="card-header">
          <h3 class="card-title">${b.title}</h3>
          <span class="card-badge">${dict.lvl} ${b.level}</span>
        </div>
        <p class="card-desc">${b.description}</p>
        <div class="card-stats">
          <div class="stat-row">
            <span>${dict.prodPerHour}</span>
            <strong style="color: var(--accent-green)">+${Math.floor(b.production_hourly).toLocaleString()}</strong>
          </div>
          <div class="stat-row">
            <span>${dict.upgradeToLvl} ${b.level + 1}</span>
          </div>
          <div class="cost-tags">
            ${b.cost_metal > 0 ? `<span class="cost-tag metal">⛏️ ${b.cost_metal.toLocaleString()}</span>` : ""}
            ${b.cost_crystal > 0 ? `<span class="cost-tag crystal">💎 ${b.cost_crystal.toLocaleString()}</span>` : ""}
            ${b.cost_deuterium > 0 ? `<span class="cost-tag deut">💧 ${b.cost_deuterium.toLocaleString()}</span>` : ""}
          </div>
        </div>
        <button class="btn-card-action" ${!b.can_build ? "disabled" : ""} data-building-id="${b.id}">
          ${b.can_build ? `⚡ ${dict.btnUpgrade}` : dict.btnBuildingUnavailable}
        </button>
      `;

      const btn = card.querySelector("button");
      btn.addEventListener("click", () => upgradeBuilding(b.id));
      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = `<div style="color: #ef4444;">Failed to load resource buildings</div>`;
  }
}

// 2. Facilities Tab
async function loadFacilities() {
  const container = document.getElementById("facilities-list");
  const dict = translations[currentLang];
  container.innerHTML = `<div style="color: var(--text-muted);">Loading...</div>`;

  try {
    const res = await fetch(`${API_BASE}/planet/${currentPlanetId}/facilities`);
    const data = await res.json();
    container.innerHTML = "";

    data.buildings.forEach((b) => {
      const card = document.createElement("div");
      card.className = "game-card glass-panel";
      card.innerHTML = `
        <div class="card-header">
          <h3 class="card-title">${b.title}</h3>
          <span class="card-badge">${dict.lvl} ${b.level}</span>
        </div>
        <p class="card-desc">${b.description}</p>
        <div class="card-stats">
          <div class="stat-row">
            <span>${dict.upgradeToLvl} ${b.level + 1}</span>
          </div>
          <div class="cost-tags">
            ${b.cost_metal > 0 ? `<span class="cost-tag metal">⛏️ ${b.cost_metal.toLocaleString()}</span>` : ""}
            ${b.cost_crystal > 0 ? `<span class="cost-tag crystal">💎 ${b.cost_crystal.toLocaleString()}</span>` : ""}
            ${b.cost_deuterium > 0 ? `<span class="cost-tag deut">💧 ${b.cost_deuterium.toLocaleString()}</span>` : ""}
          </div>
        </div>
        <button class="btn-card-action" ${!b.can_build ? "disabled" : ""} data-building-id="${b.id}">
          ${b.can_build ? `⚡ ${dict.btnUpgrade}` : dict.btnBuildingUnavailable}
        </button>
      `;

      const btn = card.querySelector("button");
      btn.addEventListener("click", () => upgradeBuilding(b.id));
      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = `<div style="color: #ef4444;">Failed to load facilities</div>`;
  }
}

async function upgradeBuilding(buildingId) {
  try {
    const res = await fetch(`${API_BASE}/planet/${currentPlanetId}/buildings/upgrade`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ building_id: buildingId })
    });
    if (!res.ok) throw new Error("Upgrade failed");
    await fetchPlanetOverview(currentPlanetId);
    if (activeTab === "resources") loadResources();
    else if (activeTab === "facilities") loadFacilities();
  } catch (err) {
    alert("건설 자원이 부족하거나 업그레이드에 실패했습니다.");
  }
}

// 3. Shipyard Tab
async function loadShipyard() {
  const container = document.getElementById("shipyard-list");
  const dict = translations[currentLang];
  container.innerHTML = `<div style="color: var(--text-muted);">Loading...</div>`;

  try {
    const res = await fetch(`${API_BASE}/planet/${currentPlanetId}/shipyard`);
    const data = await res.json();
    container.innerHTML = "";

    data.ships.forEach((s) => {
      const card = document.createElement("div");
      card.className = "game-card glass-panel";
      card.innerHTML = `
        <div class="card-header">
          <h3 class="card-title">${s.title}</h3>
          <span class="card-badge">${dict.hangarCount} ${s.count}</span>
        </div>
        <p class="card-desc">${s.description}</p>
        <div class="card-stats">
          <div class="stat-row">
            <span>${dict.shipSpecs}</span>
            <strong>⚔️ ${s.weapon_power} | 🛡️ ${s.shield_power} | 🚀 ${s.base_speed} | 📦 ${s.cargo_capacity}</strong>
          </div>
          <div class="cost-tags">
            ${s.cost_metal > 0 ? `<span class="cost-tag metal">⛏️ ${s.cost_metal.toLocaleString()}</span>` : ""}
            ${s.cost_crystal > 0 ? `<span class="cost-tag crystal">💎 ${s.cost_crystal.toLocaleString()}</span>` : ""}
            ${s.cost_deuterium > 0 ? `<span class="cost-tag deut">💧 ${s.cost_deuterium.toLocaleString()}</span>` : ""}
          </div>
        </div>
        <div class="build-row">
          <input type="number" class="build-input" value="1" min="1" id="ship-build-amt-${s.id}" />
          <button class="btn-card-action" style="flex: 1;" ${!s.can_build ? "disabled" : ""}>
            ${dict.btnBuild}
          </button>
        </div>
      `;

      const btn = card.querySelector(".btn-card-action");
      btn.addEventListener("click", () => {
        const amt = parseInt(card.querySelector(`#ship-build-amt-${s.id}`).value) || 1;
        buildShips(s.id, amt);
      });

      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = `<div style="color: #ef4444;">Failed to load shipyard</div>`;
  }
}

async function buildShips(shipId, amount) {
  try {
    const res = await fetch(`${API_BASE}/planet/${currentPlanetId}/shipyard/build`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ship_id: shipId, amount: amount })
    });
    if (!res.ok) throw new Error("Build failed");
    await fetchPlanetOverview(currentPlanetId);
    loadShipyard();
  } catch (err) {
    alert("자원이 부족하거나 건조에 실패했습니다.");
  }
}

// 4. Fleet Dispatch Tab
async function loadFleetDispatch() {
  const container = document.getElementById("fleet-dispatch-ships");
  container.innerHTML = `<div style="color: var(--text-muted);">Loading fleet...</div>`;

  try {
    const res = await fetch(`${API_BASE}/planet/${currentPlanetId}/shipyard`);
    const data = await res.json();
    container.innerHTML = "";

    data.ships.forEach((s) => {
      const item = document.createElement("div");
      item.className = "ship-input-item";
      item.innerHTML = `
        <span>${s.title} (보유: <strong>${s.count}</strong>)</span>
        <input type="number" id="fleet-ship-${s.id}" value="0" min="0" max="${s.count}" />
      `;
      container.appendChild(item);
    });
  } catch (err) {
    container.innerHTML = `<div style="color: #ef4444;">Failed to load fleet</div>`;
  }
}

function setupFleetDispatchForm() {
  const form = document.getElementById("fleet-send-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const g = parseInt(document.getElementById("fleet-target-galaxy").value);
    const s = parseInt(document.getElementById("fleet-target-system").value);
    const p = parseInt(document.getElementById("fleet-target-position").value);
    const mission = document.getElementById("fleet-mission-select").value;

    const shipInputs = document.querySelectorAll("[id^='fleet-ship-']");
    const ships = {};
    shipInputs.forEach((input) => {
      const count = parseInt(input.value) || 0;
      if (count > 0) {
        const sid = parseInt(input.id.replace("fleet-ship-", ""));
        ships[sid] = count;
      }
    });

    if (Object.keys(ships).length === 0) {
      alert("발송할 함선을 1척 이상 선택해 주세요.");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/fleet/dispatch/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          origin_planet_id: currentPlanetId,
          target: { galaxy: g, system: s, position: p, planet_type: 1 },
          mission_type: mission,
          ships: ships,
          speed_percent: 1.0
        })
      });

      const result = await res.json();
      if (!res.ok) throw new Error(result.detail || "Dispatch failed");

      alert(`🚀 ${result.message}\n소요 시간: ${formatSeconds(result.flight_time_seconds)}\n연료 소모: ${result.fuel_consumed} Deut`);
      await fetchPlanetOverview(currentPlanetId);
      loadFleetDispatch();
    } catch (err) {
      alert(`함대 발송 실패: ${err.message}`);
    }
  });
}

// 5. Galaxy Tab
function setupGalaxyViewer() {
  const btnScan = document.getElementById("btn-scan-galaxy");
  btnScan.addEventListener("click", () => {
    const g = parseInt(document.getElementById("galaxy-num").value) || 1;
    const s = parseInt(document.getElementById("system-num").value) || 100;
    loadGalaxy(g, s);
  });
}

async function loadGalaxy(galaxy, system) {
  const tbody = document.getElementById("galaxy-table-body");
  const dict = translations[currentLang];
  tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Scanning System [${galaxy}:${system}]...</td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/galaxy/${galaxy}/${system}`);
    const data = await res.json();
    tbody.innerHTML = "";

    data.slots.forEach((slot) => {
      const tr = document.createElement("tr");
      const hasPlanet = !!slot.planet_name;
      const isPlayer = slot.is_player;

      tr.innerHTML = `
        <td style="font-family: var(--font-mono); font-weight: 600;">${slot.position}</td>
        <td>${hasPlanet ? `🪐 ${slot.planet_name}` : `<span style="color: var(--text-muted);">${dict.emptySlot}</span>`}</td>
        <td class="${isPlayer ? "slot-player" : ""}">${slot.player_name || "-"}</td>
        <td>${slot.alliance_tag ? `[${slot.alliance_tag}]` : "-"}</td>
        <td class="slot-debris">${slot.debris_metal > 0 || slot.debris_crystal > 0 ? `☄️ M: ${slot.debris_metal} / C: ${slot.debris_crystal}` : "-"}</td>
        <td>
          <button class="btn-table-action" data-pos="${slot.position}">${dict.btnSendMission}</button>
        </td>
      `;

      const btn = tr.querySelector(".btn-table-action");
      btn.addEventListener("click", () => {
        switchTab("fleet");
        document.getElementById("fleet-target-galaxy").value = galaxy;
        document.getElementById("fleet-target-system").value = system;
        document.getElementById("fleet-target-position").value = slot.position;
      });

      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="color: #ef4444; text-align: center;">Failed to load galaxy data</td></tr>`;
  }
}

// Fleet Simulator (Overview)
function setupFleetCalculator() {
  const form = document.getElementById("fleet-sim-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const dict = translations[currentLang];

    const targetGalaxy = parseInt(document.getElementById("target-galaxy").value);
    const targetSystem = parseInt(document.getElementById("target-system").value);
    const targetPosition = parseInt(document.getElementById("target-position").value);

    const ship202 = parseInt(document.getElementById("ship-202").value) || 0;
    const ship204 = parseInt(document.getElementById("ship-204").value) || 0;
    const ship206 = parseInt(document.getElementById("ship-206").value) || 0;

    const ships = {};
    if (ship202 > 0) ships[202] = ship202;
    if (ship204 > 0) ships[204] = ship204;
    if (ship206 > 0) ships[206] = ship206;

    if (Object.keys(ships).length === 0) {
      alert(dict.alertSelectShip);
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/fleet/dispatch/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          origin_planet_id: currentPlanetId,
          target: { galaxy: targetGalaxy, system: targetSystem, position: targetPosition, planet_type: 1 },
          ships: ships,
          speed_percent: 1.0
        })
      });

      if (!res.ok) throw new Error("Calculation failed");
      const result = await res.json();

      const resultBox = document.getElementById("fleet-result");
      resultBox.classList.remove("hidden");
      document.getElementById("res-distance").innerText = `${result.distance.toLocaleString()} km`;
      document.getElementById("res-time").innerText = formatSeconds(result.flight_time_seconds);
      document.getElementById("res-fuel").innerText = `${result.fuel_consumption.toLocaleString()} Deut`;
      document.getElementById("res-cargo").innerText = `${result.cargo_capacity.toLocaleString()} units`;
    } catch (err) {
      console.error(err);
      alert(dict.alertCalcError);
    }
  });
}

function setupWebSocket(userId) {
  const wsStatus = document.getElementById("ws-status");
  try {
    const ws = new WebSocket(`${WS_BASE}/${userId}`);
    ws.onopen = () => {
      wsStatus.innerText = translations[currentLang].liveSync;
    };
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("WebSocket event:", data);
    };
    ws.onclose = () => {
      wsStatus.innerText = translations[currentLang].offline;
    };
  } catch (err) {
    wsStatus.innerText = translations[currentLang].offline;
  }
}

function formatSeconds(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${h > 0 ? h + "h " : ""}${m}m ${s}s`;
}

