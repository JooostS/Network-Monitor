🌐 NETWORK MONITOR TOOLKIT 🌐
A Python-based network monitoring dashboard for IT professionals and developers. Track devices, visualize performance, and manage your LAN with a clean, Linux-terminal-inspired UI.

📖 ABOUT THE PROJECT
Network Monitor is a real-time network scanning and visualization tool designed for sysadmins, developers, and IT enthusiasts.
It combines CustomTkinter UI with Matplotlib charts for a modern, responsive interface.

✅ FEATURES

ARP-based device discovery
Threaded ping with latency tracking
Protocol detection (HTTP/DNS/TCP)
Real-time KPI dashboard
Smooth charts with Dark/Light mode
Persistent settings (theme, auto-refresh, filter, watchlist)
Watchlist pinning for critical hosts
Context menu for quick actions (copy cell/row/column, add/remove watchlist)
JSON export (visible or all rows)
Keyboard shortcuts for power users


🚀 QUICK START
Requirements

Python >= 3.8
CustomTkinter
Matplotlib
Pillow

Installation
Shellgit clone https://github.com/<your-username>/network-monitor.gitcd network-monitorpip install -r requirements.txtpython main.pyMeer regels weergeven

🖥️ USAGE
UI Overview

Top Bar: Scan, Auto-refresh toggle, Theme switch, Export button
Filter: Case-insensitive, persistent across refresh
Watchlist: Pinned devices always visible
Main Table: All discovered devices with status badges
Chart: Online devices vs Avg latency (dual-axis)

Keyboard Shortcuts

Ctrl+A → Select all visible rows
Ctrl+F → Focus filter
Esc → Clear filter

Context Menu

Copy cell
Copy row(s)
Copy column
Add/remove from watchlist


📂 EXPORT

Formats: JSON (visible rows or all rows)
Future support: CSV export


⚙️ SETTINGS & PERSISTENCE

Theme
Auto-refresh
Last filter
Watchlist
Sort preferences
Saved automatically to ~/.network-monitor.json.


🛡️ TROUBLESHOOTING

App won't start? Check Python version and install dependencies.
Filter not working? Ensure you're typing in the filter box or press Esc to clear.
Export fails? Verify write permissions in target directory.


🛠️ ROADMAP

CSV export
Per-host latency sparkline
Reverse DNS + MAC vendor lookup
Alerts (sound/webhook) for status changes
Traceroute integration


🤝 CONTRIBUTING
Pull requests welcome! Please:

Fork the repo
Create a feature branch
Submit a PR with clear description


📄 LICENSE
MIT License. Use, modify, and share freely.
