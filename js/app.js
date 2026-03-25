// ============================================================
// app.js — HotCold USA
//
// Depends on (must be loaded first, in order):
//   data.js      → CITIES, STALE_HOURS
//   records.js   → CLIMATE_RECORDS
//   map.js       → buildMap(), placePins()
//   themes.js    → buildThemeSwitcher(), applyTheme(),
//                  getSavedTheme()
//
// Sections
// ────────
//  1. DOM shorthand
//  2. Date / time helpers
//  3. Data helpers  (getRecord, isStale, degToDir)
//  4. UI interactions  (toggleDiag, scroll, copyShare, updateNav)
//  5. Fetch  (fetchData)
//  6. Process  (process)
//  7. Render  (renderList, renderAll)
//  8. Init
// ============================================================


// ── 1. DOM SHORTHAND ──────────────────────────────────────────

function el(id) {
  return document.getElementById(id);
}


// ── 2. DATE / TIME HELPERS ────────────────────────────────────

function getTodayMMDD() {
  const n = new Date();
  return `${String(n.getMonth() + 1).padStart(2, '0')}-${String(n.getDate()).padStart(2, '0')}`;
}

function formatDateShort() {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'short',
    month:   'short',
    day:     'numeric',
    year:    'numeric',
  });
}

function formatTime() {
  return new Date().toLocaleTimeString('en-US', {
    hour:         'numeric',
    minute:       '2-digit',
    timeZoneName: 'short',
  });
}


// ── 3. DATA HELPERS ───────────────────────────────────────────

// Look up the CLIMATE_RECORDS entry for a given MM-DD string.
// Falls back to the nearest calendar date if an exact match
// is not found (handles leap-day edge cases gracefully).
function getRecord(mmdd) {
  if (CLIMATE_RECORDS[mmdd]) return CLIMATE_RECORDS[mmdd];

  const [m, d] = mmdd.split('-').map(Number);
  const day = (m - 1) * 30 + d;
  let best = null, bd = 999;

  for (const [k, v] of Object.entries(CLIMATE_RECORDS)) {
    const [km, kd] = k.split('-').map(Number);
    const dist = Math.abs(((km - 1) * 30 + kd) - day);
    if (dist < bd) { bd = dist; best = v; }
  }
  return best;
}

// Returns true if the ISO timestamp is missing or older than
// STALE_HOURS (defined in data.js).
function isStale(iso) {
  return !iso || (Date.now() - new Date(iso).getTime()) > STALE_HOURS * 3600000;
}

// Converts a wind bearing in degrees to a compass abbreviation.
function degToDir(deg) {
  if (deg == null) return '—';
  const dirs = ['N','NNE','NE','ENE','E','ESE','SE','SSE',
                'S','SSW','SW','WSW','W','WNW','NW','NNW'];
  return dirs[Math.round(deg / 22.5) % 16];
}


// ── 4. UI INTERACTIONS ────────────────────────────────────────

let diagOpen = false;

// Called by the diagnostics toggle button in index.html.
function toggleDiag() {
  diagOpen = !diagOpen;
  el('diag-body').classList.toggle('open', diagOpen);
  el('diag-toggle').setAttribute('aria-expanded', String(diagOpen));
  el('diag-toggle').querySelector('span').textContent =
    diagOpen ? 'Hide Diagnostics' : 'Show Diagnostics';
}

// Called by the Extremes nav button.
function scrollToTop() {
  el('scroll-body').scrollTo({ top: 0, behavior: 'smooth' });
}

// Called by the Records, Tables, and Map nav buttons.
function scrollToId(id) {
  el(id)?.scrollIntoView({ behavior: 'smooth' });
}

// Called by the Copy button in the daily-report card.
function copyShare() {
  navigator.clipboard.writeText(el('share-text').textContent).then(() => {
    const btn = el('btn-copy');
    btn.textContent = '✓ Copied';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = 'Copy';
      btn.classList.remove('copied');
    }, 2000);
  });
}

// Highlights the correct bottom-nav button as the user scrolls.
// Anchors are section-label divs with id="anchor-*" in index.html.
function updateNav() {
  const btns = document.querySelectorAll('.nav-btn');
  const sy   = el('scroll-body').scrollTop;
  btns.forEach(b => b.classList.remove('active'));

  const aMap = el('anchor-map');
  const aAbs = el('anchor-abstract');
  const aTbl = el('anchor-tables');
  const aRec = el('anchor-records');

  if      (aMap && sy >= aMap.offsetTop - 80) btns[3].classList.add('active');
  else if (aAbs && sy >= aAbs.offsetTop - 80) btns[2].classList.add('active');
  else if (aTbl && sy >= aTbl.offsetTop - 80) btns[2].classList.add('active');
  else if (aRec && sy >= aRec.offsetTop - 80) btns[1].classList.add('active');
  else                                         btns[0].classList.add('active');
}


// ── 5. FETCH ──────────────────────────────────────────────────

// Fetches current conditions for all CITIES (defined in data.js)
// from the Open-Meteo batch API in a single request.
// Returns { stations[], requests, duration, source }.
async function fetchData() {
  const t0   = performance.now();
  const lats = CITIES.map(c => c.lat).join(',');
  const lons = CITIES.map(c => c.lon).join(',');
  let stations = [];

  try {
    const url = [
      'https://api.open-meteo.com/v1/forecast',
      `?latitude=${lats}`,
      `&longitude=${lons}`,
      '&current=temperature_2m,wind_direction_10m,surface_pressure',
      '&temperature_unit=fahrenheit',
      '&forecast_days=1',
    ].join('');

    const resp = await fetch(url);

    if (resp.ok) {
      const data    = await resp.json();
      const results = Array.isArray(data) ? data : [data];

      results.forEach((r, i) => {
        const c    = CITIES[i];
        if (!c) return;

        const temp = r?.current?.temperature_2m;
        if (temp == null) return;

        const pressure = r?.current?.surface_pressure;

        stations.push({
          station_id: `OM_${c.city}_${c.state}`.replace(/\s/g, '_'),
          city:       c.city,
          state:      c.state,
          lat:        c.lat,
          lon:        c.lon,
          temperature_f: Math.round(temp),
          observation_time_iso: r?.current?.time
            ? new Date(r.current.time + ':00').toISOString()
            : new Date().toISOString(),
          pressure_inhg: pressure
            ? (pressure * 0.02953).toFixed(2)
            : null,
          wind_dir: r?.current?.wind_direction_10m != null
            ? degToDir(r.current.wind_direction_10m)
            : '—',
        });
      });
    }
  } catch (e) {
    console.warn('fetchData error:', e);
  }

  return {
    stations,
    requests: 1,
    duration: Math.round(performance.now() - t0),
    source:   'Open-Meteo / WMO',
  };
}


// ── 6. PROCESS ────────────────────────────────────────────────

// Validates and deduplicates raw station observations.
// Returns the sorted list plus convenience references to the
// hottest, coldest, and top-5 extremes at each end.
function process(stations) {
  const seen = new Map();
  let rejected = 0;

  for (const st of stations) {
    const t = st.temperature_f;

    // Reject readings outside the physically plausible range
    if (t == null || isNaN(t) || t < -130 || t > 140) {
      rejected++;
      continue;
    }

    // Reject stale observations
    if (isStale(st.observation_time_iso)) {
      rejected++;
      continue;
    }

    // Keep the most recent reading per station
    const existing = seen.get(st.station_id);
    if (!existing ||
        st.observation_time_iso > (existing.observation_time_iso || '')) {
      seen.set(st.station_id, st);
    }
  }

  const valid  = Array.from(seen.values());
  const sorted = [...valid].sort((a, b) => b.temperature_f - a.temperature_f);

  return {
    valid,
    sorted,
    rejected,
    hottest:  sorted[0]                 || null,
    coldest:  sorted[sorted.length - 1] || null,
    top5hot:  sorted.slice(0, 5),
    top5cold: sorted.slice(-5).reverse(),
  };
}


// ── 7. RENDER ─────────────────────────────────────────────────

// Renders a ranked list of up to 5 stations into a <ul>.
// Fills remaining rows with placeholder dashes if fewer
// than 5 stations are available.
function renderList(id, stations) {
  const list = el(id);
  let html = '';

  for (let i = 0; i < 5; i++) {
    const st = stations[i];
    if (st) {
      html += `<li>
        <span class="rank-num">${i + 1}</span>
        <span class="rank-place">${st.city}, ${st.state}</span>
        <span class="rank-temp">${st.temperature_f}°F</span>
      </li>`;
    } else {
      html += `<li>
        <span class="rank-num">${i + 1}</span>
        <span class="rank-place" style="opacity:0.25">—</span>
        <span class="rank-temp"  style="opacity:0.25">—</span>
      </li>`;
    }
  }

  list.innerHTML = html;
}

// Populates every data-bound element on the page.
// Note: records.js stores the location as `.city`, not `.place`
// (the original code referenced .place — this is the fix).
function renderAll(data, diag) {
  const { hottest, coldest, top5hot, top5cold, valid, rejected } = data;
  const spread = (hottest && coldest)
    ? hottest.temperature_f - coldest.temperature_f
    : null;
  const mmdd   = getTodayMMDD();
  const record = getRecord(mmdd);

  // Header dateline
  el('dateline').innerHTML = `${formatDateShort()}<br>${formatTime()}`;

  // Extreme cards
  if (hottest) {
    el('hot-temp').textContent   = `${hottest.temperature_f}°F`;
    el('hot-place').textContent  = `${hottest.city}, ${hottest.state}`;
    el('hot-detail').textContent = `Bar: ${hottest.pressure_inhg || '—'}"  Wind: ${hottest.wind_dir}`;
  }
  if (coldest) {
    el('cold-temp').textContent   = `${coldest.temperature_f}°F`;
    el('cold-place').textContent  = `${coldest.city}, ${coldest.state}`;
    el('cold-detail').textContent = `Bar: ${coldest.pressure_inhg || '—'}"  Wind: ${coldest.wind_dir}`;
  }

  // Spread banner
  if (spread != null) {
    el('spread-val').textContent  = `${spread}°F`;
    el('spread-desc').innerHTML   = `<em>${hottest.city} → ${coldest.city}</em>`;
  }

  // Map pin labels
  if (hottest) el('legend-hot').textContent  = `${hottest.city}, ${hottest.state} · ${hottest.temperature_f}°F`;
  if (coldest) el('legend-cold').textContent = `${coldest.city}, ${coldest.state} · ${coldest.temperature_f}°F`;
  placePins(hottest, coldest);

  // Records section — field is .city not .place (fix from original)
  if (record) {
    el('rec-high-temp').textContent = `${record.high.temp}°F`;
    el('rec-high-place').innerHTML  =
      `${record.high.city}<br><em style="font-size:9px;opacity:0.6"></em>`;
    el('rec-low-temp').textContent  = `${record.low.temp}°F`;
    el('rec-low-place').innerHTML   =
      `${record.low.city}<br><em style="font-size:9px;opacity:0.6"></em>`;
  }

  // Ranking tables
  renderList('list-hot',  top5hot);
  renderList('list-cold', top5cold);

  // Daily report / share text
  const lines = [
    `🇺🇸 HotCold USA — ${formatDateShort()}`,
    `Updated: ${formatTime()}`,
    ``,
    `🔥 Hottest: ${hottest ? `${hottest.city}, ${hottest.state} — ${hottest.temperature_f}°F` : 'N/A'}`,
    `❄  Coldest: ${coldest ? `${coldest.city}, ${coldest.state} — ${coldest.temperature_f}°F` : 'N/A'}`,
    `↔  Range: ${spread != null ? `${spread}°F` : 'N/A'}`,
    ``,
    record ? `★ Record High (${mmdd}): ${record.high.temp}°F — ${record.high.city}` : '',
    record ? `★ Record Low  (${mmdd}): ${record.low.temp}°F — ${record.low.city}`  : '',
  ].filter(l => l != null).join('\n');
  el('share-text').textContent = lines;

  // Diagnostics panel
  const now = new Date();
  el('d-update').textContent   = now.toLocaleTimeString();
  el('d-snap').textContent     = now.toISOString().replace('T', ' ').substring(0, 19) + 'Z';
  el('d-snapid').textContent   = `REF-${Date.now().toString(36).toUpperCase()}`;
  el('d-total').textContent    = diag.total.toLocaleString();
  el('d-accepted').textContent = valid.length.toLocaleString();
  el('d-rejected').textContent = rejected.toLocaleString();
  el('d-requests').textContent = diag.requests;
  el('d-duration').textContent = `${diag.duration}ms`;
  el('d-source').textContent   = diag.source;
}


// ── 8. INIT ───────────────────────────────────────────────────

async function init() {
  // Theme switcher — runs before data loads so it's immediately usable
  buildThemeSwitcher();
  applyTheme(getSavedTheme());

  // Map skeleton — state paths drawn once, pins added after fetch
  buildMap();

  // Scroll-based nav highlighting
  el('scroll-body').addEventListener('scroll', updateNav, { passive: true });

  // Fetch, process, render
  const t0     = performance.now();
  const result = await fetchData();

  if (!result.stations.length) {
    el('hot-place').textContent  = 'Unable to load data';
    el('cold-place').textContent = 'Check connection and reload';
    return;
  }

  const processed = process(result.stations);

  renderAll(processed, {
    total:    result.stations.length,
    requests: result.requests,
    duration: Math.round(performance.now() - t0),
    source:   result.source,
  });
}

document.addEventListener('DOMContentLoaded', init);
