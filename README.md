# name: "Network Monitor Toolkit"
description: |
  🌐 NETWORK MONITOR TOOLKIT 🌐
  A Python-based network monitoring dashboard for IT professionals and developers.
  Track devices, visualize performance, and manage your LAN with a clean, Linux-terminal-inspired UI.

about: |
  Network Monitor is a real-time network scanning and visualization tool designed for sysadmins, developers, and IT enthusiasts.
  It combines CustomTkinter UI with Matplotlib charts for a modern, responsive interface.

features:
  - ARP-based device discovery
  - Threaded ping with latency tracking
  - Protocol detection (HTTP/DNS/TCP)
  - Real-time KPI dashboard
  - Smooth charts with Dark/Light mode
  - Persistent settings (theme, auto-refresh, filter, watchlist)
  - Watchlist pinning for critical hosts
  - Context menu for quick actions (copy cell/row/column, add/remove watchlist)
  - JSON export (visible or all rows)
  - Keyboard shortcuts for power users

quick_start:
  requirements:
    - Python >= 3.8
    - CustomTkinter
    - Matplotlib
    - Pillow
  installation: |
    ```bash
    git clone https://github.com/<your-username>/network-monitor.git
    cd network-monitor
    pip install -r requirements.txt
    python main.py
    ```

usage:
  ui_overview: |
    - **Top Bar**: Scan, Auto-refresh toggle, Theme switch, Export button
    - **Filter**: Case-insensitive, persistent across refresh
    - **Watchlist**: Pinned devices always visible
    - **Main Table**: All discovered devices with status badges
    - **Chart**: Online devices vs Avg latency (dual-axis)
  shortcuts:
    - Ctrl+A: Select all visible rows
    - Ctrl+F: Focus filter
    - Esc: Clear filter
  context_menu:
    - Copy cell
    - Copy row(s)
    - Copy column
    - Add/remove from watchlist

export:
  formats:
    - JSON (visible rows or all rows)
  future_support:
    - CSV export
    - Combined watchlist + main export

settings:
  persisted:
    - theme
    - auto_refresh
    - last_filter
    - watchlist
    - sort preferences
  file: "~/.network-monitor.json"

roadmap:
  - CSV export
  - Per-host latency sparkline
  - Reverse DNS + MAC vendor lookup
  - Alerts (sound/webhook) for status changes
  - Traceroute integration

troubleshooting:
  - "App won't start? Check Python version and install dependencies."
  - "Filter not working? Ensure you're typing in the filter box or press Esc to clear."
  - "Export fails? Verify write permissions in target directory."

contributing:
  guidelines: |
    Pull requests welcome! Please:
    - Fork the repo
    - Create a feature branch
    - Submit a PR with clear description

license: "MIT"
badges:
  - python: "Python >= 3.8"
  - license: "MIT"
  - ui: "CustomTkinter"
