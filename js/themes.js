// ============================================================
// themes.js - HotCold USA
//
// Responsibilities
// 1. THEME_CATALOG   Metadata for every theme defined in
//                    themes.css - label and the bg colour used
//                    to update the browser's <meta name="theme-color">.
// 2. applyTheme(id)  Sets data-theme on <body>, marks the
//                    active button, updates the meta tag,
//                    and persists the choice to localStorage.
// 3. buildThemeSwitcher()
//                    Injects one <button> per theme into
//                    #theme-btn-group.
// 4. getSavedTheme() Returns the last-chosen theme id from
//                    localStorage, falling back to 'patriot'.
// ============================================================

const THEME_CATALOG = [
  {
    id:    'patriot',
    label: '1890s',
    bg:    '#efe2c8',
  },
  {
    id:    'ranger',
    label: 'Deco',
    bg:    '#0f1110',
  },
  {
    id:    'dispatch',
    label: 'Amber',
    bg:    '#050403',
  },
  {
    id:    'glacier',
    label: 'Blueprint',
    bg:    '#0b1f4d',
  },
  {
    id:    'ember',
    label: 'Desert',
    bg:    '#f0ddc3',
  },
  {
    id:    'harbor',
    label: 'Harbor',
    bg:    '#dfe9ef',
  },
  {
    id:    'canopy',
    label: 'Canopy',
    bg:    '#e7e1cf',
  },
  {
    id:    'motel',
    label: 'Motel',
    bg:    '#f8e7cf',
  },
  {
    id:    'squall',
    label: 'Squall',
    bg:    '#1d2730',
  },
];

const THEME_STORAGE_KEY = 'hotcold-theme';

function getSavedTheme() {
  try {
    const saved = localStorage.getItem(THEME_STORAGE_KEY);
    if (saved && THEME_CATALOG.some(t => t.id === saved)) {
      return saved;
    }
  } catch (_) {
    // localStorage unavailable
  }
  return 'patriot';
}

function applyTheme(id) {
  const theme = THEME_CATALOG.find(t => t.id === id);
  if (!theme) return;

  document.body.dataset.theme = id;

  const metaTag = document.getElementById('theme-color-meta');
  if (metaTag) metaTag.setAttribute('content', theme.bg);

  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.themeId === id);
  });

  try {
    localStorage.setItem(THEME_STORAGE_KEY, id);
  } catch (_) {}
}

function buildThemeSwitcher() {
  const container = document.getElementById('theme-btn-group');
  if (!container) return;

  const currentId = getSavedTheme();

  THEME_CATALOG.forEach(theme => {
    const btn = document.createElement('button');

    btn.className = 'theme-btn';
    btn.dataset.themeId = theme.id;
    btn.setAttribute('aria-label', `Switch to ${theme.label} theme`);
    btn.title = theme.label;
    btn.textContent = theme.label;

    if (theme.id === currentId) btn.classList.add('active');

    btn.addEventListener('click', () => applyTheme(theme.id));

    container.appendChild(btn);
  });
}

