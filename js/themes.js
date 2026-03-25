// ============================================================
// themes.js — HotCold USA
//
// Responsibilities
// ────────────────
// 1. THEME_CATALOG   Metadata for every theme defined in
//                    themes.css — label, emoji, and the bg
//                    colour used to update the browser's
//                    <meta name="theme-color"> on mobile.
//
// 2. applyTheme(id)  Sets data-theme on <body>, marks the
//                    active button, updates the meta tag,
//                    and persists the choice to localStorage.
//
// 3. buildThemeSwitcher()
//                    Injects one <button> per theme into
//                    #theme-btn-group. Called once by app.js
//                    inside init() before data loads, so the
//                    switcher is usable immediately.
//
// 4. getSavedTheme() Returns the last-chosen theme id from
//                    localStorage, falling back to 'patriot'.
//
// Depends on: nothing (pure DOM + localStorage).
// Called by:  app.js → init().
// ============================================================


// ── 1. THEME CATALOG ──────────────────────────────────────────
// One entry per theme block in themes.css.
// `bg` must match the --c-bg value in that block exactly —
// it is written to <meta name="theme-color"> so the mobile
// browser chrome matches the app header colour.

const THEME_CATALOG = [
  {
    id:    'patriot',
    label: 'Patriot',
    emoji: '🇺🇸',
    bg:    '#0a1628',
  },
  {
    id:    'ranger',
    label: 'Ranger',
    emoji: '🌲',
    bg:    '#0f1f0f',
  },
  {
    id:    'dispatch',
    label: 'Dispatch',
    emoji: '📡',
    bg:    '#0d0d0d',
  },
  {
    id:    'glacier',
    label: 'Glacier',
    emoji: '🧊',
    bg:    '#070e18',
  },
  {
    id:    'ember',
    label: 'Ember',
    emoji: '🔥',
    bg:    '#110e0b',
  },
];


// ── 2. STORAGE KEY ────────────────────────────────────────────

const THEME_STORAGE_KEY = 'hotcold-theme';


// ── 3. GET SAVED THEME ────────────────────────────────────────
// Returns the stored theme id if it exists in THEME_CATALOG,
// otherwise falls back to 'patriot'.

function getSavedTheme() {
  try {
    const saved = localStorage.getItem(THEME_STORAGE_KEY);
    if (saved && THEME_CATALOG.some(t => t.id === saved)) {
      return saved;
    }
  } catch (_) {
    // localStorage unavailable (private browsing, etc.)
  }
  return 'patriot';
}


// ── 4. APPLY THEME ────────────────────────────────────────────
// Sets data-theme on <body> so themes.css selectors activate,
// updates the mobile browser chrome colour via the meta tag,
// marks the matching button .active, and saves to storage.

function applyTheme(id) {
  const theme = THEME_CATALOG.find(t => t.id === id);
  if (!theme) return;

  // Swap the data-theme attribute — themes.css does the rest
  document.body.dataset.theme = id;

  // Keep the mobile status-bar / browser chrome in sync
  const metaTag = document.getElementById('theme-color-meta');
  if (metaTag) metaTag.setAttribute('content', theme.bg);

  // Update button active states
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.themeId === id);
  });

  // Persist choice
  try {
    localStorage.setItem(THEME_STORAGE_KEY, id);
  } catch (_) {}
}


// ── 5. BUILD THEME SWITCHER ───────────────────────────────────
// Injects buttons into #theme-btn-group (defined in index.html).
// Each button carries data-theme-id so applyTheme can identify
// it, and an aria-label for accessibility.
// Safe to call before or after DOMContentLoaded as long as
// the container element exists when this runs (script is at
// bottom of <body>, so it always does).

function buildThemeSwitcher() {
  const container = document.getElementById('theme-btn-group');
  if (!container) return;

  const currentId = getSavedTheme();

  THEME_CATALOG.forEach(theme => {
    const btn = document.createElement('button');

    btn.className          = 'theme-btn';
    btn.dataset.themeId    = theme.id;
    btn.setAttribute('aria-label', `Switch to ${theme.label} theme`);
    btn.title              = theme.label;
    btn.textContent        = `${theme.emoji} ${theme.label}`;

    if (theme.id === currentId) btn.classList.add('active');

    btn.addEventListener('click', () => applyTheme(theme.id));

    container.appendChild(btn);
  });
}
