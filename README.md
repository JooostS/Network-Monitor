# Network Monitor Tool - Enhanced Features

## 🆕 New Features

### 1. Device Nicknames/Labels

Assign friendly names to your devices for easier identification!

**How to use:**
- **Right-click** any device in the table
- Select **"Edit nickname"**
- Enter a friendly name (e.g., "Mom's Laptop", "Living Room TV", "Office Printer")
- Leave blank to remove nickname

**Features:**
- Nicknames appear in the first column of both tables
- Fully searchable in the filter box
- Persistent across sessions (saved in `~/.network-monitor.json`)
- Shown in device details panel
- Included in all exports (JSON & PDF)

**Example:**
```
Instead of: 192.168.1.105
See: "Living Room TV" | 192.168.1.105
```

---

### 2. PDF Report Generation

Generate professional PDF reports with comprehensive network analysis!

**How to use:**
1. Click the **"export"** button
2. Select **"Export PDF report"**
3. Choose save location
4. Wait for generation (status shown in bottom-right)

**PDF Contents:**
- **Summary Statistics**
  - Total devices
  - Online/Offline counts
  - Average ping time
  - Report timestamp

- **Network Activity Chart**
  - Visual graph showing online devices and ping over time
  - Automatically scaled and formatted

- **Complete Device List**
  - All devices with nicknames, IPs, MACs, status, protocols, and ping times
  - Clean table format with alternating row colors

- **Watchlist Section** (if you have pinned devices)
  - Highlighted watchlist devices
  - Quick status overview

**Requirements:**
```bash
pip install reportlab
```

If reportlab is not installed, you'll see an error message with installation instructions.

---

## 📦 Installation

### First Time Setup:
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install manually:
pip install customtkinter matplotlib Pillow reportlab
```

### Running the Application:
```bash
python main.py
```

---

## 🎨 Updated Features

### Enhanced Filter
- Now searches through **nicknames** as well as IPs, MACs, status, etc.
- Type in the filter box: "living" to find "Living Room TV"

### Context Menu (Right-Click)
- **Edit nickname** - Set/change device nickname
- **Copy cell** - Copy single cell value
- **Copy row(s)** - Copy selected row(s)
- **Copy column** - Copy entire column
- **Add/Remove from watchlist** - Pin/unpin devices

### Detail Panel
- Shows nickname at the top
- Full device information including history

### Export Options
- **JSON (visible)** - Export currently filtered devices
- **JSON (all)** - Export all scanned devices
- **PDF report** - Generate comprehensive report with charts

---

## 💡 Usage Tips

### Organizing Devices
1. **Scan your network** - Click "scan" or wait for auto-refresh
2. **Add nicknames** - Right-click devices and assign friendly names
3. **Create watchlist** - Pin important devices (routers, servers, etc.)
4. **Filter easily** - Type nicknames in the filter to find devices quickly

### Generating Reports
- **Before important changes** - Export PDF to document current state
- **Network audits** - Professional reports for documentation
- **Troubleshooting** - Track device availability over time with charts
- **Scheduled reports** - Run scans and export PDFs regularly

### Best Practices
- Use **descriptive nicknames** (include location or owner)
- **Pin critical devices** to watchlist (router, NAS, servers)
- **Export PDFs** before network changes
- Use **filters** to focus on specific device groups

---

## 🔧 Configuration

All settings are saved automatically to: `~/.network-monitor.json`

**Stored data:**
- Theme preference (Dark/Light)
- Auto-refresh toggle
- Last used filter
- Watchlist (pinned IPs)
- **Device nicknames** (new!)
- Sort preferences

---

## 📊 Example Workflow

1. **Initial Setup**
   ```
   Scan network → Find all devices
   ```

2. **Organize**
   ```
   Right-click → Edit nicknames
   Right-click → Add important devices to watchlist
   ```

3. **Monitor**
   ```
   Filter by nickname/status
   Watch real-time status updates
   Check ping performance chart
   ```

4. **Document**
   ```
   Export → PDF report
   Share professional network documentation
   ```

---

## 🐛 Troubleshooting

**"reportlab not installed" error:**
```bash
pip install reportlab
```

**Nicknames not saving:**
- Check write permissions to home directory
- Verify `~/.network-monitor.json` exists

**PDF generation fails:**
- Ensure reportlab is installed
- Check disk space
- Verify write permissions to save location

---

## 🚀 Future Enhancements

Possible next features:
- Device grouping/categories
- Alert notifications
- Historical database (SQLite)
- Port scanning
- Wake-on-LAN support

---

## 📝 Version History

### v2.0 (Current)
- ✨ Device nicknames with persistent storage
- 📄 PDF report generation with charts
- 🔍 Enhanced filtering (includes nicknames)
- 🎨 Improved context menus

### v1.0
- Network scanning (ARP)
- Device ping monitoring
- Dark/Light themes
- Watchlist functionality
- JSON export
- Real-time charts

---

**Enjoy your enhanced Network Monitor Tool!** 🎉
