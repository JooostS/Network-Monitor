# 🌐 Network Monitor Toolkit

A Python-based network monitoring dashboard for IT professionals and developers. Track devices, visualize performance, and manage your LAN with a clean, Linux-terminal-inspired UI.

## 📖 About

**Network Monitor** is a real-time network scanning and visualization tool designed for sysadmins, developers, and IT enthusiasts. It combines a modern **CustomTkinter** UI with **Matplotlib** charts for a responsive and intuitive experience.

## ✨ Features

- 🔍 ARP-based device discovery
- 📶 Threaded ping with latency tracking
- 🌐 Protocol detection (HTTP/DNS/TCP)
- 📊 Real-time KPI dashboard
- 🌙 Dark/Light mode support
- ⚙️ Persistent settings (theme, auto-refresh, filter, watchlist)
- 📌 Watchlist pinning for critical hosts
- 🖱️ Context menu for quick actions (copy cell/row/column, add/remove watchlist)
- 📤 JSON export (visible or all rows)
- ⌨️ Keyboard shortcuts for power users

## 🚀 Quick Start

### Requirements

- Python >= 3.8
- `CustomTkinter`
- `Matplotlib`


### Installation
```bash
git clone https://github.com/JooostS/Network-Monitor.git
cd Network-Monitor
pip install -m CustomTkinter Matplotlib 
python main.py
```

# 🖥️ UI Overview

- Top Bar: Scan, Auto-refresh toggle, Theme switch, Export button

- Filter: Case-insensitive, persistent across refresh

- Watchlist: Pinned devices always visible

- Main Table: All discovered devices with status badges

- Chart: Online devices vs Avg latency (dual-axis)

# ⌨️ Shortcuts

Ctrl+A: Select all visible rows

Ctrl+F: Focus filter

Esc: Clear filter

# 🖱️ Context Menu

Copy cell

Copy row(s)

Copy column

Add/remove from watchlist

# 📤 Export

Format: JSON (visible rows or all rows)

- Future: CSV export, combined watchlist + main export

# ⚙️ Settings

Persisted in ~/.network-monitor.json:

Theme

Auto-refresh

Last filter

Watchlist

Sort preferences

# 🛣️ Roadmap

CSV export

Per-host latency sparkline

Reverse DNS + MAC vendor lookup

Alerts (sound/webhook) for status changes

Traceroute integration

# 🧰 Troubleshooting

App won't start? Check Python version and install dependencies.

Filter not working? Ensure you're typing in the filter box or press Esc to clear.

Export fails? Verify write permissions in target directory.


# 🤝 Contributing

Pull requests welcome! Please:

- Fork the repo
- Create a feature branch
- Submit a PR with a clear description

# 📄 License

MIT License. Use, modify, and share freely.

# ✅ Badges 

![Python](https://img.shields.io/badge/Python-%3E%3D3.8-blue)  
![License](https://img.shields.io/badge/License-MIT-green)  
![UI](https://img.shields.io/badge/UI-CustomTkinter-orange)
