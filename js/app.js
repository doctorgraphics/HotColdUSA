// ============================================================
// app.js - HotCold USA
// ============================================================

const CUSTOM_LOCATIONS_KEY = "hotcold-custom-locations";
const TEMP_UNIT_KEY = "hotcold-temp-unit";
const DISTANCE_UNIT_KEY = "hotcold-distance-unit";
// STALE_HOURS is declared in data.js

const settings = {
  tempUnit: "f",
  distanceUnit: "mi",
};

function el(id) {
  return document.getElementById(id);
}

function getTodayMMDD() {
  const n = new Date();
  return `${String(n.getMonth() + 1).padStart(2, "0")}-${String(n.getDate()).padStart(2, "0")}`;
}

function formatDateShort() {
  return new Date().toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatTime() {
  return new Date().toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short",
  });
}

function getRecord(mmdd) {
  if (CLIMATE_RECORDS[mmdd]) return CLIMATE_RECORDS[mmdd];

  const [m, d] = mmdd.split("-").map(Number);
  const day = (m - 1) * 30 + d;
  let best = null;
  let bestDistance = 999;

  for (const [key, value] of Object.entries(CLIMATE_RECORDS)) {
    const [km, kd] = key.split("-").map(Number);
    const distance = Math.abs((km - 1) * 30 + kd - day);
    if (distance < bestDistance) {
      bestDistance = distance;
      best = value;
    }
  }

  return best;
}

function isStale(iso) {
  return !iso || Date.now() - new Date(iso).getTime() > STALE_HOURS * 3600000;
}

function degToDir(deg) {
  if (deg == null) return "-";
  const dirs = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
  ];
  return dirs[Math.round(deg / 22.5) % 16];
}

function toCelsius(tempF) {
  return ((tempF - 32) * 5) / 9;
}

function displayTemp(tempF) {
  return settings.tempUnit === "c"
    ? Math.round(toCelsius(tempF))
    : Math.round(tempF);
}

function formatTemp(tempF) {
  const suffix = settings.tempUnit === "c" ? "C" : "F";
  return `${displayTemp(tempF)}${String.fromCharCode(176)}${suffix}`;
}

function formatTempDelta(deltaF) {
  const value =
    settings.tempUnit === "c"
      ? Math.round((deltaF * 5) / 9)
      : Math.round(deltaF);
  const suffix = settings.tempUnit === "c" ? "C" : "F";
  return `${value}${String.fromCharCode(176)}${suffix}`;
}

function haversineMiles(a, b) {
  const toRad = (deg) => (deg * Math.PI) / 180;
  const r = 3958.8;
  const dLat = toRad(b.lat - a.lat);
  const dLon = toRad(b.lon - a.lon);
  const lat1 = toRad(a.lat);
  const lat2 = toRad(b.lat);
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
  return 2 * r * Math.asin(Math.sqrt(h));
}

function formatDistanceMiles(distanceMiles) {
  if (distanceMiles == null) return "N/A";
  if (settings.distanceUnit === "km") {
    return `${Math.round(distanceMiles * 1.60934).toLocaleString()} km`;
  }
  return `${Math.round(distanceMiles).toLocaleString()} mi`;
}

function loadUnitSettings() {
  try {
    const savedTemp = localStorage.getItem(TEMP_UNIT_KEY);
    const savedDistance = localStorage.getItem(DISTANCE_UNIT_KEY);
    if (savedTemp === "f" || savedTemp === "c") settings.tempUnit = savedTemp;
    if (savedDistance === "mi" || savedDistance === "km")
      settings.distanceUnit = savedDistance;
  } catch (_) {}
}

function saveUnitSettings() {
  try {
    localStorage.setItem(TEMP_UNIT_KEY, settings.tempUnit);
    localStorage.setItem(DISTANCE_UNIT_KEY, settings.distanceUnit);
  } catch (_) {}
}

function syncUnitControls() {
  el("unit-temp").value = settings.tempUnit;
  el("unit-distance").value = settings.distanceUnit;
}

function normalizeCustomLocation(entry) {
  const city = String(entry.city || "").trim();
  const state = String(entry.state || "").trim();
  const lat = Number(entry.lat);
  const lon = Number(entry.lon);

  if (!city || Number.isNaN(lat) || Number.isNaN(lon)) return null;
  if (lat < -90 || lat > 90 || lon < -180 || lon > 180) return null;

  return {
    id:
      entry.id || `custom_${city}_${state}_${lat}_${lon}`.replace(/\s+/g, "_"),
    city,
    state: state || "Custom",
    lat,
    lon,
    custom: true,
  };
}

function loadCustomLocations() {
  try {
    const parsed = JSON.parse(
      localStorage.getItem(CUSTOM_LOCATIONS_KEY) || "[]",
    );
    if (!Array.isArray(parsed)) return [];
    return parsed.map(normalizeCustomLocation).filter(Boolean);
  } catch (_) {
    return [];
  }
}

function saveCustomLocations(locations) {
  try {
    localStorage.setItem(CUSTOM_LOCATIONS_KEY, JSON.stringify(locations));
  } catch (_) {}
}

function getCustomLocations() {
  return loadCustomLocations();
}

function getAllLocations() {
  return [...CITIES, ...getCustomLocations()];
}

function setCustomStatus(message, isError = false) {
  const status = el("custom-status");
  status.textContent = message;
  status.classList.toggle("error", isError);
}

function renderCustomLocations() {
  const list = el("custom-list");
  const locations = getCustomLocations();

  if (!locations.length) {
    list.innerHTML = '<li class="custom-empty">No custom locations yet.</li>';
    return;
  }

  list.innerHTML = locations
    .map(
      (location) => `
    <li class="custom-item">
      <div class="custom-item-main">
        <span class="custom-item-name">${location.city}, ${location.state}</span>
        <span class="custom-item-coords">${location.lat.toFixed(2)}, ${location.lon.toFixed(2)}</span>
      </div>
      <button class="custom-remove" type="button" data-location-id="${location.id}">Remove</button>
    </li>
  `,
    )
    .join("");
}

let diagOpen = false;
let refreshToken = 0;
let latestRender = null;

function toggleDiag() {
  diagOpen = !diagOpen;
  el("diag-body").classList.toggle("open", diagOpen);
  el("diag-toggle").setAttribute("aria-expanded", String(diagOpen));
  el("diag-toggle").querySelector("span").textContent = diagOpen
    ? "Hide Diagnostics"
    : "Show Diagnostics";
}

function scrollToTop() {
  el("scroll-body").scrollTo({ top: 0, behavior: "smooth" });
}

function scrollToId(id) {
  el(id)?.scrollIntoView({ behavior: "smooth" });
}

function setCopyButtonState(label, copied = false) {
  const btn = el("btn-copy");
  btn.textContent = label;
  btn.classList.toggle("copied", copied);
}

function resetCopyButton() {
  setTimeout(() => setCopyButtonState("Copy", false), 2000);
}

function fallbackCopyText(text) {
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.setAttribute("readonly", "");
  ta.style.position = "fixed";
  ta.style.top = "-9999px";
  document.body.appendChild(ta);
  ta.select();

  let ok = false;
  try {
    ok = document.execCommand("copy");
  } catch (_) {
    ok = false;
  }

  ta.remove();
  return ok;
}

async function copyShare() {
  const text = el("share-text").textContent;

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    } else if (!fallbackCopyText(text)) {
      throw new Error("Clipboard unavailable");
    }
    setCopyButtonState("Copied", true);
  } catch (_) {
    setCopyButtonState("Copy Failed", false);
  }

  resetCopyButton();
}

function updateNav() {
  const btns = document.querySelectorAll(".nav-btn");
  const sy = el("scroll-body").scrollTop;
  btns.forEach((btn) => btn.classList.remove("active"));

  const aMap = el("anchor-map");
  const aAbs = el("anchor-abstract");
  const aTbl = el("anchor-tables");
  const aRec = el("anchor-records");

  if (aMap && sy >= aMap.offsetTop - 80) btns[3].classList.add("active");
  else if (aAbs && sy >= aAbs.offsetTop - 80) btns[2].classList.add("active");
  else if (aTbl && sy >= aTbl.offsetTop - 80) btns[2].classList.add("active");
  else if (aRec && sy >= aRec.offsetTop - 80) btns[1].classList.add("active");
  else btns[0].classList.add("active");
}

async function fetchData() {
  const t0 = performance.now();
  const locations = getAllLocations();
  const lats = locations.map((c) => c.lat).join(",");
  const lons = locations.map((c) => c.lon).join(",");
  const stations = [];

  try {
    const url = [
      "https://api.open-meteo.com/v1/forecast",
      `?latitude=${lats}`,
      `&longitude=${lons}`,
      "&current=temperature_2m,wind_direction_10m,surface_pressure",
      "&temperature_unit=fahrenheit",
      "&forecast_days=1",
    ].join("");

    const resp = await fetch(url);
    if (resp.ok) {
      const data = await resp.json();
      const results = Array.isArray(data) ? data : [data];

      results.forEach((result, index) => {
        const location = locations[index];
        if (!location) return;

        const temp = result?.current?.temperature_2m;
        if (temp == null) return;

        const pressure = result?.current?.surface_pressure;
        stations.push({
          station_id:
            `OM_${location.id || `${location.city}_${location.state}`}`.replace(
              /\s/g,
              "_",
            ),
          city: location.city,
          state: location.state,
          lat: location.lat,
          lon: location.lon,
          temperature_f: Math.round(temp),
          observation_time_iso: result?.current?.time
            ? new Date(result.current.time + ":00").toISOString()
            : new Date().toISOString(),
          pressure_inhg: pressure ? (pressure * 0.02953).toFixed(2) : null,
          wind_dir:
            result?.current?.wind_direction_10m != null
              ? degToDir(result.current.wind_direction_10m)
              : "-",
        });
      });
    }
  } catch (e) {
    console.warn("fetchData error:", e);
  }

  return {
    stations,
    requests: 1,
    duration: Math.round(performance.now() - t0),
    source: "Open-Meteo / WMO",
  };
}

function process(stations) {
  const seen = new Map();
  let rejected = 0;

  for (const st of stations) {
    const t = st.temperature_f;

    if (t == null || Number.isNaN(t) || t < -130 || t > 140) {
      rejected++;
      continue;
    }

    if (isStale(st.observation_time_iso)) {
      rejected++;
      continue;
    }

    const existing = seen.get(st.station_id);
    if (
      !existing ||
      st.observation_time_iso > (existing.observation_time_iso || "")
    ) {
      seen.set(st.station_id, st);
    }
  }

  const valid = Array.from(seen.values());
  const sorted = [...valid].sort((a, b) => b.temperature_f - a.temperature_f);

  return {
    valid,
    sorted,
    rejected,
    hottest: sorted[0] || null,
    coldest: sorted[sorted.length - 1] || null,
    top5hot: sorted.slice(0, 5),
    top5cold: sorted.slice(-5).reverse(),
  };
}

function renderList(id, stations) {
  const list = el(id);
  let html = "";

  for (let i = 0; i < 5; i++) {
    const st = stations[i];
    if (st) {
      html += `<li><span class="rank-num">${i + 1}</span><span class="rank-place">${st.city}, ${st.state}</span><span class="rank-temp">${formatTemp(st.temperature_f)}</span></li>`;
    } else {
      html += `<li><span class="rank-num">${i + 1}</span><span class="rank-place" style="opacity:0.25">-</span><span class="rank-temp" style="opacity:0.25">-</span></li>`;
    }
  }

  list.innerHTML = html;
}

function renderAll(data, diag) {
  const { hottest, coldest, top5hot, top5cold, valid, rejected } = data;
  const spreadF =
    hottest && coldest ? hottest.temperature_f - coldest.temperature_f : null;
  const distanceMiles =
    hottest && coldest ? haversineMiles(hottest, coldest) : null;
  const mmdd = getTodayMMDD();
  const record = getRecord(mmdd);

  el("dateline").innerHTML = `${formatDateShort()}<br>${formatTime()}`;

  if (hottest) {
    el("hot-temp").textContent = formatTemp(hottest.temperature_f);
    el("hot-place").textContent = `${hottest.city}, ${hottest.state}`;
    el("hot-detail").textContent =
      `Bar: ${hottest.pressure_inhg || "-"}"  Wind: ${hottest.wind_dir}`;
  }

  if (coldest) {
    el("cold-temp").textContent = formatTemp(coldest.temperature_f);
    el("cold-place").textContent = `${coldest.city}, ${coldest.state}`;
    el("cold-detail").textContent =
      `Bar: ${coldest.pressure_inhg || "-"}"  Wind: ${coldest.wind_dir}`;
  }

  if (spreadF != null) {
    el("spread-val").textContent = formatTempDelta(spreadF);
    el("spread-desc").innerHTML =
      `<em>${hottest.city} to ${coldest.city}</em><br>${formatDistanceMiles(distanceMiles)} apart`;
  }

  if (hottest)
    el("legend-hot").textContent = `${hottest.city}, ${hottest.state}`;
  if (coldest)
    el("legend-cold").textContent = `${coldest.city}, ${coldest.state}`;
  placePins(hottest, coldest);

  if (record) {
    el("rec-high-temp").textContent = formatTemp(record.high.temp);
    el("rec-high-place").textContent = record.high.city;

    el("rec-low-temp").textContent = formatTemp(record.low.temp);
    el("rec-low-place").textContent = record.low.city;
  }

  renderList("list-hot", top5hot);
  renderList("list-cold", top5cold);

  const lines = [
    `HotCold USA - ${formatDateShort()}`,
    `Updated: ${formatTime()}`,
    "",
    `Hottest: ${hottest ? `${hottest.city}, ${hottest.state} - ${formatTemp(hottest.temperature_f)}` : "N/A"}`,
    `Coldest: ${coldest ? `${coldest.city}, ${coldest.state} - ${formatTemp(coldest.temperature_f)}` : "N/A"}`,
    `Range: ${spreadF != null ? formatTempDelta(spreadF) : "N/A"}`,
    `Distance: ${formatDistanceMiles(distanceMiles)}`,
    "",
    record
      ? `Record High (${mmdd}): ${formatTemp(record.high.temp)} - ${record.high.city}`
      : "",
    record
      ? `Record Low (${mmdd}): ${formatTemp(record.low.temp)} - ${record.low.city}`
      : "",
  ]
    .filter(Boolean)
    .join("\n");
  el("share-text").textContent = lines;

  const now = new Date();
  el("d-update").textContent = now.toLocaleTimeString();
  el("d-snap").textContent =
    now.toISOString().replace("T", " ").substring(0, 19) + "Z";
  el("d-snapid").textContent = `REF-${Date.now().toString(36).toUpperCase()}`;
  el("d-total").textContent = diag.total.toLocaleString();
  el("d-accepted").textContent = valid.length.toLocaleString();
  el("d-rejected").textContent = rejected.toLocaleString();
  el("d-requests").textContent = diag.requests;
  el("d-duration").textContent = `${diag.duration}ms`;
  el("d-source").textContent = diag.source;

  latestRender = { data, diag };
}

async function refreshData() {
  const token = ++refreshToken;
  const t0 = performance.now();

  setCustomStatus(`Tracking ${getAllLocations().length} total locations.`);

  const result = await fetchData();
  if (token !== refreshToken) return;

  if (!result.stations.length) {
    el("hot-place").textContent = "Unable to load data";
    el("cold-place").textContent = "Check connection and reload";
    return;
  }

  const processed = process(result.stations);
  renderAll(processed, {
    total: result.stations.length,
    requests: result.requests,
    duration: Math.round(performance.now() - t0),
    source: result.source,
  });
}

function rerenderLatest() {
  if (latestRender) renderAll(latestRender.data, latestRender.diag);
}

function handleUnitChange() {
  settings.tempUnit = el("unit-temp").value;
  settings.distanceUnit = el("unit-distance").value;
  saveUnitSettings();
  rerenderLatest();
}

function handleCustomLocationSubmit(event) {
  event.preventDefault();

  const location = normalizeCustomLocation({
    city: el("custom-city").value,
    state: el("custom-state").value,
    lat: el("custom-lat").value,
    lon: el("custom-lon").value,
  });

  if (!location) {
    setCustomStatus("Enter a city plus valid latitude and longitude.", true);
    return;
  }

  const locations = getCustomLocations();
  const duplicate = locations.some(
    (item) =>
      item.city.toLowerCase() === location.city.toLowerCase() &&
      item.state.toLowerCase() === location.state.toLowerCase() &&
      Math.abs(item.lat - location.lat) < 0.001 &&
      Math.abs(item.lon - location.lon) < 0.001,
  );

  if (duplicate) {
    setCustomStatus("That location is already saved.", true);
    return;
  }

  locations.push(location);
  saveCustomLocations(locations);
  renderCustomLocations();
  el("custom-form").reset();
  setCustomStatus(`Added ${location.city}, ${location.state}.`);
  refreshData();
}

function handleCustomListClick(event) {
  const button = event.target.closest("[data-location-id]");
  if (!button) return;

  const id = button.getAttribute("data-location-id");
  const locations = getCustomLocations();
  const next = locations.filter((location) => location.id !== id);
  const removed = locations.find((location) => location.id === id);
  saveCustomLocations(next);
  renderCustomLocations();
  setCustomStatus(
    removed
      ? `Removed ${removed.city}, ${removed.state}.`
      : "Location removed.",
  );
  refreshData();
}

async function init() {
  loadUnitSettings();
  buildThemeSwitcher();
  applyTheme(getSavedTheme());
  buildMap();

  el("custom-form").addEventListener("submit", handleCustomLocationSubmit);
  el("custom-list").addEventListener("click", handleCustomListClick);
  el("unit-temp").addEventListener("change", handleUnitChange);
  el("unit-distance").addEventListener("change", handleUnitChange);
  el("scroll-body").addEventListener("scroll", updateNav, { passive: true });
  el("diag-toggle").addEventListener("click", toggleDiag);
  el("btn-copy").addEventListener("click", copyShare);
  el("nav-top").addEventListener("click", scrollToTop);
  el("nav-records").addEventListener("click", () =>
    scrollToId("anchor-records"),
  );
  el("nav-tables").addEventListener("click", () => scrollToId("anchor-tables"));
  el("nav-map").addEventListener("click", () => scrollToId("anchor-map"));

  syncUnitControls();
  renderCustomLocations();
  await refreshData();
}

document.addEventListener("DOMContentLoaded", init);
