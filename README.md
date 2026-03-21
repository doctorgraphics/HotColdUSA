# HotCold USA 🌡️

![GitHub repo size](https://img.shields.io/github/repo-size/doctorgraphics/HotColdUSA)
![GitHub last commit](https://img.shields.io/github/last-commit/doctorgraphics/HotColdUSA)
![GitHub license](https://img.shields.io/github/license/doctorgraphics/HotColdUSA)
![GitHub Pages](https://img.shields.io/badge/deploy-GitHub%20Pages-blue)
![Status](https://img.shields.io/badge/status-prototype-orange)

**HotCold USA** is a simple web app that shows the hottest and coldest locations from a tracked set of U.S. cities, along with the national temperature spread across that sample.

The goal is to provide a quick daily snapshot of weather extremes across the country.

🔥 Hottest place in the U.S.  
❄️ Coldest place in the U.S.  
🌡️ Temperature difference across the country  

---

# Demo

Once deployed with GitHub Pages, the site will be available at:

https://doctorgraphics.github.io/HotColdUSA

---

# Features

Current prototype includes:

- 🔥 **Hottest place today**
- ❄️ **Coldest place today**
- 🌡️ **National temperature spread**
- 🗺️ Prototype map display
- 📍 Local comparison
- 📊 3-day history table
- 🏆 Hottest & coldest leaderboards
- 📤 Daily share card

The current version is a static frontend backed by generated JSON files. Weather observations are fetched by Python scripts and then published for the site to consume.

---

# Tech Stack

The project intentionally uses very simple technology so it works easily with GitHub Pages.

- HTML  
- CSS  
- Vanilla JavaScript  
- Python data scripts  
- GitHub Pages for hosting  

No frameworks or build tools are required.

---

# Project Structure

HotColdUSA
│
├── index.html
├── README.md
└── scripts/
    ├── fetch_weather.py
    ├── refresh_stations.py
    └── daily_sync.py

---

# Future Improvements

Planned improvements include:

- Interactive U.S. temperature map
- Real-time hottest and coldest tracking
- Historical temperature spread charts
- Daily notifications
- Shareable social media cards
- Mobile versions for iOS and Android

---

# Data Sources

The current scripts are built around:

- Open-Meteo API for live observations in the tracked city list
- A local `records.json` file for daily climate context

Future versions may also pull weather observations from:

- National Weather Service API
- NOAA weather station observations

These larger sources would make it possible to move beyond the current one-city-per-state sampling approach.

---

# Why This Project Exists

Weather is something people check every day.

HotCold USA focuses on one simple question:

> Where is the hottest place in the United States today?  
> And where is the coldest?

Sometimes the temperature difference across the tracked cities can exceed **150°F**, which makes for an interesting daily statistic.

---

# Current Limitations

- The app currently tracks a curated set of 50 cities, not every reporting station in the United States.
- The "map" is still a visual prototype rather than a precise geospatial rendering.
- Historical records are injected from a local JSON data source during the publish process.

---

# License

MIT License

You are free to use, modify, and distribute this project.
