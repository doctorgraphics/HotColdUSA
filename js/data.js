// ============================================================
// data.js — HotCold USA
//
// Station list and fetch configuration.
//
// CITIES        Array of { city, state, lat, lon } objects
//               passed to the Open-Meteo batch API call.
//               Order matters: the API returns results in the
//               same order, so app.js zips by index.
//
// STALE_HOURS   Observations older than this are rejected by
//               process() in app.js.
// ============================================================

const STALE_HOURS = 2;

const CITIES = [
  // ── Sun Belt / South ──────────────────────────────────────
  { city: 'Phoenix',         state: 'AZ', lat:  33.45, lon: -112.07 },
  { city: 'Houston',         state: 'TX', lat:  29.76, lon:  -95.37 },
  { city: 'Miami',           state: 'FL', lat:  25.77, lon:  -80.19 },
  { city: 'Los Angeles',     state: 'CA', lat:  34.05, lon: -118.24 },
  { city: 'Las Vegas',       state: 'NV', lat:  36.17, lon: -115.14 },
  { city: 'Dallas',          state: 'TX', lat:  32.78, lon:  -96.80 },
  { city: 'San Antonio',     state: 'TX', lat:  29.42, lon:  -98.49 },
  { city: 'Jacksonville',    state: 'FL', lat:  30.33, lon:  -81.66 },
  { city: 'El Paso',         state: 'TX', lat:  31.76, lon: -106.49 },
  { city: 'Tucson',          state: 'AZ', lat:  32.22, lon: -110.93 },
  { city: 'Sacramento',      state: 'CA', lat:  38.58, lon: -121.49 },
  { city: 'San Diego',       state: 'CA', lat:  32.72, lon: -117.16 },
  { city: 'Albuquerque',     state: 'NM', lat:  35.08, lon: -106.65 },
  { city: 'Oklahoma City',   state: 'OK', lat:  35.47, lon:  -97.52 },
  { city: 'Memphis',         state: 'TN', lat:  35.15, lon:  -90.05 },
  { city: 'Atlanta',         state: 'GA', lat:  33.75, lon:  -84.39 },
  { city: 'Charlotte',       state: 'NC', lat:  35.23, lon:  -80.84 },
  { city: 'Nashville',       state: 'TN', lat:  36.17, lon:  -86.78 },

  // ── Mountain West ─────────────────────────────────────────
  { city: 'Denver',          state: 'CO', lat:  39.74, lon: -104.98 },
  { city: 'Salt Lake City',  state: 'UT', lat:  40.76, lon: -111.89 },
  { city: 'Billings',        state: 'MT', lat:  45.78, lon: -108.50 },
  { city: 'Boise',           state: 'ID', lat:  43.62, lon: -116.20 },
  { city: 'Cheyenne',        state: 'WY', lat:  41.14, lon: -104.82 },
  { city: 'Helena',          state: 'MT', lat:  46.59, lon: -112.02 },
  { city: 'Reno',            state: 'NV', lat:  39.53, lon: -119.81 },
  { city: 'Rapid City',      state: 'SD', lat:  44.07, lon: -103.22 },
  { city: 'Casper',          state: 'WY', lat:  42.87, lon: -106.31 },
  { city: 'Grand Junction',  state: 'CO', lat:  39.06, lon: -108.55 },
  { city: 'Pueblo',          state: 'CO', lat:  38.25, lon: -104.61 },
  { city: 'Leadville',       state: 'CO', lat:  39.25, lon: -106.29 },
  { city: 'Gunnison',        state: 'CO', lat:  38.55, lon: -106.93 },
  { city: 'Jackson',         state: 'WY', lat:  43.48, lon: -110.76 },

  // ── Pacific Northwest ─────────────────────────────────────
  { city: 'Portland',        state: 'OR', lat:  45.52, lon: -122.67 },
  { city: 'Seattle',         state: 'WA', lat:  47.61, lon: -122.33 },
  { city: 'Redding',         state: 'CA', lat:  40.58, lon: -122.39 },

  // ── Plains / Midwest ──────────────────────────────────────
  { city: 'Minneapolis',     state: 'MN', lat:  44.98, lon:  -93.27 },
  { city: 'Chicago',         state: 'IL', lat:  41.85, lon:  -87.65 },
  { city: 'Detroit',         state: 'MI', lat:  42.33, lon:  -83.05 },
  { city: 'Kansas City',     state: 'MO', lat:  39.10, lon:  -94.58 },
  { city: 'Bismarck',        state: 'ND', lat:  46.81, lon: -100.78 },
  { city: 'Sioux Falls',     state: 'SD', lat:  43.54, lon:  -96.73 },
  { city: 'Fargo',           state: 'ND', lat:  46.88, lon:  -96.79 },
  { city: 'Green Bay',       state: 'WI', lat:  44.52, lon:  -88.02 },
  { city: 'Wichita',         state: 'KS', lat:  37.69, lon:  -97.34 },
  { city: 'Omaha',           state: 'NE', lat:  41.26, lon:  -96.01 },
  { city: 'Des Moines',      state: 'IA', lat:  41.59, lon:  -93.62 },
  { city: 'Madison',         state: 'WI', lat:  43.07, lon:  -89.40 },
  { city: 'Milwaukee',       state: 'WI', lat:  43.04, lon:  -87.91 },
  { city: 'Indianapolis',    state: 'IN', lat:  39.77, lon:  -86.16 },
  { city: 'St. Louis',       state: 'MO', lat:  38.63, lon:  -90.20 },
  { city: 'Duluth',          state: 'MN', lat:  46.78, lon:  -92.10 },
  { city: 'Bemidji',         state: 'MN', lat:  47.47, lon:  -94.88 },
  { city: 'Grand Forks',     state: 'ND', lat:  47.93, lon:  -97.03 },
  { city: 'Minot',           state: 'ND', lat:  48.23, lon: -101.30 },
  { city: 'Scottsbluff',     state: 'NE', lat:  41.87, lon: -103.67 },
  { city: 'North Platte',    state: 'NE', lat:  41.14, lon: -100.76 },
  { city: 'Dodge City',      state: 'KS', lat:  37.75, lon: -100.02 },
  { city: 'Garden City',     state: 'KS', lat:  37.97, lon: -100.87 },

  // ── Northeast ─────────────────────────────────────────────
  { city: 'New York',        state: 'NY', lat:  40.71, lon:  -74.01 },
  { city: 'Boston',          state: 'MA', lat:  42.36, lon:  -71.06 },
  { city: 'Pittsburgh',      state: 'PA', lat:  40.44, lon:  -79.99 },
  { city: 'Buffalo',         state: 'NY', lat:  42.88, lon:  -78.88 },
  { city: 'Cleveland',       state: 'OH', lat:  41.50, lon:  -81.69 },
  { city: 'Columbus',        state: 'OH', lat:  39.96, lon:  -83.00 },
  { city: 'Bangor',          state: 'ME', lat:  44.80, lon:  -68.78 },
  { city: 'Burlington',      state: 'VT', lat:  44.48, lon:  -73.21 },
  { city: 'Providence',      state: 'RI', lat:  41.82, lon:  -71.42 },

  // ── Southeast ─────────────────────────────────────────────
  { city: 'Louisville',      state: 'KY', lat:  38.25, lon:  -85.76 },
  { city: 'New Orleans',     state: 'LA', lat:  29.95, lon:  -90.07 },
  { city: 'Little Rock',     state: 'AR', lat:  34.75, lon:  -92.29 },
  { city: 'Jackson',         state: 'MS', lat:  32.30, lon:  -90.18 },
  { city: 'Montgomery',      state: 'AL', lat:  32.36, lon:  -86.30 },
  { city: 'Tallahassee',     state: 'FL', lat:  30.44, lon:  -84.28 },
  { city: 'Columbia',        state: 'SC', lat:  34.00, lon:  -81.03 },
  { city: 'Raleigh',         state: 'NC', lat:  35.78, lon:  -78.64 },
  { city: 'Richmond',        state: 'VA', lat:  37.54, lon:  -77.43 },

  // ── Desert Southwest extremes ─────────────────────────────
  { city: 'Death Valley',    state: 'CA', lat:  36.46, lon: -116.87 },
  { city: 'Yuma',            state: 'AZ', lat:  32.69, lon: -114.62 },
  { city: 'Needles',         state: 'CA', lat:  34.85, lon: -114.61 },
  { city: 'Blythe',          state: 'CA', lat:  33.61, lon: -114.60 },
  { city: 'Indio',           state: 'CA', lat:  33.72, lon: -116.22 },
  { city: 'Palm Springs',    state: 'CA', lat:  33.83, lon: -116.54 },
  { city: 'Lake Havasu City',state: 'AZ', lat:  34.48, lon: -114.32 },
  { city: 'Bullhead City',   state: 'AZ', lat:  35.15, lon: -114.57 },

  // ── California Central Valley ─────────────────────────────
  { city: 'Fresno',          state: 'CA', lat:  36.74, lon: -119.77 },
  { city: 'Bakersfield',     state: 'CA', lat:  35.37, lon: -119.02 },
  { city: 'Stockton',        state: 'CA', lat:  37.96, lon: -121.29 },
  { city: 'Modesto',         state: 'CA', lat:  37.64, lon: -120.99 },

  // ── Texas extended ────────────────────────────────────────
  { city: 'Lubbock',         state: 'TX', lat:  33.58, lon: -101.85 },
  { city: 'Amarillo',        state: 'TX', lat:  35.22, lon: -101.83 },
  { city: 'Corpus Christi',  state: 'TX', lat:  27.80, lon:  -97.40 },
  { city: 'Brownsville',     state: 'TX', lat:  25.90, lon:  -97.49 },
  { city: 'Laredo',          state: 'TX', lat:  27.50, lon:  -99.50 },

  // ── Cold extremes (lower 48) ──────────────────────────────
  { city: 'Intl Falls',      state: 'MN', lat:  48.60, lon:  -93.41 },

  // ── Alaska ────────────────────────────────────────────────
  { city: 'Anchorage',       state: 'AK', lat:  61.22, lon: -149.90 },
  { city: 'Fairbanks',       state: 'AK', lat:  64.84, lon: -147.72 },
  { city: 'Juneau',          state: 'AK', lat:  58.30, lon: -134.42 },
  { city: 'Barrow',          state: 'AK', lat:  71.29, lon: -156.79 },
  { city: 'Nome',            state: 'AK', lat:  64.50, lon: -165.41 },
  { city: 'Bettles',         state: 'AK', lat:  66.91, lon: -151.52 },
  { city: 'Fort Yukon',      state: 'AK', lat:  66.56, lon: -145.25 },
  { city: 'Prospect Creek',  state: 'AK', lat:  66.83, lon: -150.65 },
  { city: 'McGrath',         state: 'AK', lat:  62.95, lon: -155.61 },

  // ── Hawaii ────────────────────────────────────────────────
  { city: 'Honolulu',        state: 'HI', lat:  21.31, lon: -157.86 },
];
