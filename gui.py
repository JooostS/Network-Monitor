import json
import os
from pathlib import Path
import customtkinter as ctk
from tkinter import ttk, filedialog, Menu, simpledialog
from datetime import datetime
from scanner import scan_network, threaded_ping
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib as mpl

# ---------- Matplotlib perf tweaks ----------
mpl.rcParams.update({
    "path.simplify": True,
    "path.simplify_threshold": 0.3,
    "agg.path.chunksize": 10000,
})

# ---------- Base palette (Dark) ----------
TERMINAL_BG_DARK = "#0b0f10"
TERMINAL_FG_DARK = "#e5e9f0"
GREEN_DARK       = "#00d46a"
RED_DARK         = "#ff5050"
YELLOW_DARK      = "#f0d000"
GREY_DARK        = "#7f8c8d"
ROW_EVEN_DARK    = "#0e1316"
ROW_ODD_DARK     = "#10171b"
HEADER_BG_DARK   = "#11181d"
GRID_STROKE_DARK = "#2a333a"
GRID_ALPHA_DARK  = 0.18

# ---------- Base palette (Light) ----------
TERMINAL_BG_LIGHT = "#ffffff"
TERMINAL_FG_LIGHT = "#1c1f22"
GREEN_LIGHT       = "#13a05a"
RED_LIGHT         = "#d12f2f"
YELLOW_LIGHT      = "#a88300"
GREY_LIGHT        = "#5c6870"
ROW_EVEN_LIGHT    = "#f4f6f8"
ROW_ODD_LIGHT     = "#eef2f5"
HEADER_BG_LIGHT   = "#e8ecf0"
GRID_STROKE_LIGHT = "#cfd6dc"
GRID_ALPHA_LIGHT  = 0.25

# Fonts (monospace feel)
MONO       = ("Cascadia Mono", 11)
MONO_SMALL = ("Cascadia Mono", 10)
MONO_BOLD  = ("Cascadia Mono", 11, "bold")

# Persisted settings file
CONFIG_PATH = Path.home() / ".network-monitor.json"


class NetworkMonitorGUI(ctk.CTk):
    def __init__(self, refresh_interval=5000):
        super().__init__()
        # --- SAFETY GUARD: if something shadowed the Tk mainloop method with a dict, remove it
        if "mainloop" in self.__dict__ and not callable(self.__dict__["mainloop"]):
            del self.__dict__["mainloop"]
        self.title("Network Monitor Tool")
        self.geometry("1200x900")
        try:
            self.iconbitmap("./Network-Monitor/network-monitor-tool.ico")
        except:
            pass
        
        # --- State ---
        self.refresh_interval = refresh_interval
        self.devices = {}
        self.pending = 0

        # Track row IIDs in each table (so we can reattach after detaching on filter)
        self.main_row_ids = set()
        self.watch_row_ids = set()

        # Persistent UI state
        self.settings = {
            "theme": "Dark",
            "auto_refresh": True,
            "last_filter": "",
            "watchlist": [],           # list of IP strings
            "sort_col": "IP",
            "sort_desc": False,
            "nicknames": {}            # NEW: {ip: nickname}
        }
        self._load_settings()

        # Apply theme
        ctk.set_appearance_mode(self.settings.get("theme", "Dark"))
        self._compute_theme_colors()

        # ========= Top Bar =========
        self.topbar = ctk.CTkFrame(self, corner_radius=12)
        self.topbar.pack(fill="x", padx=10, pady=(8, 6))

        self.scan_btn = ctk.CTkButton(self.topbar, text="scan", width=90,
                                      command=self.refresh, font=MONO_SMALL)
        self.scan_btn.pack(side="left", padx=(8, 6), pady=8)

        self.toggle_btn = ctk.CTkButton(self.topbar, text=f"auto: {'ON' if self.settings['auto_refresh'] else 'OFF'}",
                                        width=100, command=self.toggle_auto_refresh, font=MONO_SMALL)
        self.toggle_btn.pack(side="left", padx=6, pady=8)

        self.theme_btn = ctk.CTkButton(self.topbar, text="theme", width=90,
                                       command=self.toggle_mode, font=MONO_SMALL)
        self.theme_btn.pack(side="left", padx=6, pady=8)

        # Export button with JSON/PDF options
        self.export_btn = ctk.CTkButton(self.topbar, text="export", width=90,
                                        command=self._open_export_menu, font=MONO_SMALL)
        self.export_btn.pack(side="left", padx=6, pady=8)

        self.status_line = ctk.CTkLabel(self.topbar, text="ready", font=MONO_SMALL)
        self.status_line.pack(side="right", padx=10, pady=8)

        # ========= KPI Strip =========
        self.kpi = ctk.CTkFrame(self, corner_radius=12)
        self.kpi.pack(fill="x", padx=10, pady=(0, 6))

        self.kpi_total  = ctk.CTkLabel(self.kpi, text="devices: 0", font=MONO_SMALL)
        self.kpi_online = ctk.CTkLabel(self.kpi, text="online: 0",  font=MONO_SMALL)
        self.kpi_avg    = ctk.CTkLabel(self.kpi, text="avg ping: -", font=MONO_SMALL)
        self.kpi_time   = ctk.CTkLabel(self.kpi, text="last: -",     font=MONO_SMALL)

        self.kpi_total.pack(side="left", padx=(10, 12), pady=6)
        self.kpi_online.pack(side="left", padx=12, pady=6)
        self.kpi_avg.pack(side="left", padx=12, pady=6)
        self.kpi_time.pack(side="right", padx=10, pady=6)

        # ========= Filter Row (with Clear) =========
        self.filter_frame = ctk.CTkFrame(self, corner_radius=12)
        self.filter_frame.pack(fill="x", padx=10, pady=(0, 6))

        left = ctk.CTkFrame(self.filter_frame, corner_radius=0, fg_color="transparent")
        left.pack(side="left", expand=True, fill="x", padx=(8,0), pady=8)

        self.filter_var = ctk.StringVar(value=self.settings.get("last_filter", ""))
        self.filter_entry = ctk.CTkEntry(
            left,
            placeholder_text="filter ip / mac / nickname / status / protocol / ping (Esc clears)",
            textvariable=self.filter_var,
            font=MONO_SMALL
        )
        self.filter_entry.pack(side="left", expand=True, fill="x")

        self.clear_btn = ctk.CTkButton(
            self.filter_frame, text="clear", width=70,
            command=self.clear_filter, font=MONO_SMALL
        )
        self.clear_btn.pack(side="right", padx=8, pady=8)

        # Bind filter + global shortcuts
        self.filter_var.trace_add("write", self._on_filter_changed)
        self.bind_all("<Escape>", lambda e: self.clear_filter())
        self.bind_all("<Control-f>", lambda e: (self.filter_entry.focus_set(), "break"))
        self.bind_all("<Control-a>", self._select_all_visible)
        
        # ========= Main Area (All devices) =========
        main_wrap = ctk.CTkFrame(self, corner_radius=12)
        main_wrap.pack(expand=True, fill="both", padx=10, pady=(0, 8))
        ctk.CTkLabel(main_wrap, text="All devices", font=MONO_BOLD).pack(anchor="w", padx=8, pady=(6, 0))

        self.columns = ("Nickname", "IP", "MAC", "Status", "Protocol", "Ping (ms)")
        self.tree = ttk.Treeview(main_wrap, columns=self.columns, show="headings", selectmode="extended")
        self._style_tree()  # apply theme-aware ttk styles

        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_main_by(c))
            if col == "Nickname":
                anchor = "w"
                width = 150
            elif col in ("IP", "MAC"):
                anchor = "w"
                width = 180 if col == "IP" else 250
            else:
                anchor = "center"
                width = 110
            self.tree.column(col, anchor=anchor, width=width, stretch=True)
        self.tree.pack(side="left", expand=True, fill="both", padx=8, pady=(4, 8))

        scrollbar = ttk.Scrollbar(main_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="left", fill="y", pady=(4, 8))

        # Detail panel
        self.detail_panel = ctk.CTkFrame(main_wrap, width=280, corner_radius=12)
        self.detail_panel.pack(side="left", fill="y", padx=(8, 8), pady=(4, 8))
        self.detail_label = ctk.CTkLabel(self.detail_panel, text="select a device",
                                         justify="left", font=MONO_SMALL)
        self.detail_label.pack(padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.show_details)

        # Context menus
        self.tree.bind("<Button-3>", self._open_context_menu_main)

        # ========= Watchlist (Pinned) =========
        watch_wrap = ctk.CTkFrame(self, corner_radius=12)
        watch_wrap.pack(fill="both", padx=10, pady=(0, 6))
        ctk.CTkLabel(watch_wrap, text="Watchlist (pinned)", font=MONO_BOLD).pack(anchor="w", padx=8, pady=(6, 0))

        self.watch_columns = ("Nickname", "IP", "MAC", "Status", "Protocol", "Ping (ms)")
        self.watch_tree = ttk.Treeview(watch_wrap, columns=self.watch_columns, show="headings", selectmode="extended")
        for col in self.watch_columns:
            self.watch_tree.heading(col, text=col, command=lambda c=col: self._sort_tree(self.watch_tree, c))
            if col == "Nickname":
                anchor = "w"
                width = 150
            elif col in ("IP", "MAC"):
                anchor = "w"
                width = 180 if col == "IP" else 250
            else:
                anchor = "center"
                width = 110
            self.watch_tree.column(col, anchor=anchor, width=width, stretch=True)
        self.watch_tree.pack(fill="x", padx=8, pady=(4, 8))
        self.watch_tree.bind("<Button-3>", self._open_context_menu_watch)

        # ========= Chart (smooth updates) =========
        self.figure = Figure(figsize=(8.5, 2.3), dpi=100)
        self.ax  = self.figure.add_subplot(111)
        self.ax2 = self.ax.twinx()

        (self.line_online,)  = self.ax.plot([], [], linewidth=1.6, marker="", antialiased=False)
        (self.line_latency,) = self.ax2.plot([], [], linewidth=1.2, linestyle="-", marker="", antialiased=False)

        self.ax.set_title("online & avg ping", loc="left", fontfamily="monospace", fontsize=10)
        self.ax.set_xlabel("scan #", fontfamily="monospace", fontsize=9)
        self.ax.set_ylabel("online",  fontfamily="monospace", fontsize=9)
        self.ax2.set_ylabel("ms",      fontfamily="monospace", fontsize=9)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill="x", padx=10, pady=(0, 8))

        # Chart state
        self.scan_count = 0
        self.online_history  = []
        self.latency_history = []
        self._chart_window   = 80
        self._chart_needs_draw = False
        self._chart_interval_ms = 120
        self.after(self._chart_interval_ms, self._chart_redraw_tick)

        # Icons for status badges (try tiny PNG circles; fall back to '●')
        self.icon_online = self._make_circle_icon(self._color_green(), 10)
        self.icon_offline = self._make_circle_icon(self._color_red(), 10)

        # Apply theme styling across widgets
        self._apply_theme_to_widgets()
        self._apply_plot_theme()

        # Restore filter from settings (and apply)
        if self.settings.get("last_filter"):
            self.filter_entry.icursor("end")

        # Handle window close → persist settings
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Initial scan
        self.refresh()
        # Auto refresh loop
        self.after(self.refresh_interval, self.auto_refresh_loop)

    # ===================== Theme & Styling =====================
    def _compute_theme_colors(self):
        dark = (ctk.get_appearance_mode() == "Dark")
        if dark:
            self.bg, self.fg = TERMINAL_BG_DARK, TERMINAL_FG_DARK
            self.green, self.red, self.yellow, self.grey = GREEN_DARK, RED_DARK, YELLOW_DARK, GREY_DARK
            self.row_even, self.row_odd = ROW_EVEN_DARK, ROW_ODD_DARK
            self.header_bg = HEADER_BG_DARK
            self.grid_stroke, self.grid_alpha = GRID_STROKE_DARK, GRID_ALPHA_DARK
        else:
            self.bg, self.fg = TERMINAL_BG_LIGHT, TERMINAL_FG_LIGHT
            self.green, self.red, self.yellow, self.grey = GREEN_LIGHT, RED_LIGHT, YELLOW_LIGHT, GREY_LIGHT
            self.row_even, self.row_odd = ROW_EVEN_LIGHT, ROW_ODD_LIGHT
            self.header_bg = HEADER_BG_LIGHT
            self.grid_stroke, self.grid_alpha = GRID_STROKE_LIGHT, GRID_ALPHA_LIGHT

    def _apply_theme_to_widgets(self):
        self.configure(fg_color=self.bg)
        panel_color = self._panel_color()

        for frame in (self.topbar, self.kpi, self.filter_frame, self.detail_panel):
            frame.configure(fg_color=panel_color, border_width=0)
        # Watch + main wrappers inherit parent bg; tables styled via ttk
        self._style_tree()
        self.watch_tree.tag_configure("Online",  foreground=self.green)
        self.watch_tree.tag_configure("Offline", foreground=self.red)
        self.tree.tag_configure("evenrow", background=self.row_even)
        self.tree.tag_configure("oddrow",  background=self.row_odd)
        self.tree.tag_configure("Online",  foreground=self.green)
        self.tree.tag_configure("Offline", foreground=self.red)

        for btn in (self.scan_btn, self.toggle_btn, self.theme_btn, self.export_btn, self.clear_btn):
            btn.configure(text_color=self.fg, hover_color=self._hover_color(), fg_color=self._button_color())
        for lbl in (self.status_line, self.kpi_total, self.kpi_online, self.kpi_avg, self.kpi_time, self.detail_label):
            lbl.configure(text_color=self.fg)
        self.kpi_online.configure(text_color=self.green)
        self.kpi_avg.configure(text_color=self.yellow)
        self.status_line.configure(text_color=self.grey)

        self.filter_entry.configure(
            fg_color=self._entry_color(),
            text_color=self.fg,
            border_width=1,
            border_color=self._entry_border(),
        )

        # Chart colors
        self.line_online.set_color(self.green)
        self.line_latency.set_color(self.yellow)
        self.ax.set_title("online & avg ping", loc="left", color=self.fg, fontfamily="monospace", fontsize=10)
        self.ax.set_xlabel("scan #", color=self.grey, fontfamily="monospace", fontsize=9)
        self.ax.set_ylabel("online", color=self.green,  fontfamily="monospace", fontsize=9)
        self.ax2.set_ylabel("ms",     color=self.yellow, fontfamily="monospace", fontsize=9)

        self._apply_plot_theme()
        self._chart_needs_draw = True

    def _panel_color(self):
        return "#0f151a" if ctk.get_appearance_mode() == "Dark" else "#f4f6f8"
    def _entry_color(self):
        return "#0d1317" if ctk.get_appearance_mode() == "Dark" else "#ffffff"
    def _entry_border(self):
        return "#1e2730" if ctk.get_appearance_mode() == "Dark" else "#cfd6dc"
    def _button_color(self):
        return "#1a2228" if ctk.get_appearance_mode() == "Dark" else "#e6ebf0"
    def _hover_color(self):
        return "#222c34" if ctk.get_appearance_mode() == "Dark" else "#dfe6ec"
    def _color_green(self): return (0, 212, 106)
    def _color_red(self):   return (255, 80, 80)

    def _style_tree(self):
        style = ttk.Style(self)
        try:
            style.theme_use("default")
        except Exception:
            pass
        # Main
        style.configure(
            "Treeview",
            background=self.bg, foreground=self.fg,
            fieldbackground=self.bg, rowheight=24, font=MONO,
            borderwidth=0, relief="flat",
        )
        style.configure(
            "Treeview.Heading",
            background=self.header_bg, foreground=self.fg,
            font=MONO_BOLD, borderwidth=0, relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", "#1f2a31" if ctk.get_appearance_mode() == "Dark" else "#dbe6ef")],
            foreground=[("selected", self.fg)],
        )

    def _apply_plot_theme(self):
        bg = self.bg
        for ax in (self.ax, self.ax2):
            ax.set_facecolor(bg)
            for spine in ax.spines.values():
                spine.set_color(self.grid_stroke)
            ax.tick_params(colors=self.grey, labelsize=8)
        self.figure.set_facecolor(bg)
        self.ax.grid(True, color=self.grid_stroke, alpha=self.grid_alpha, linewidth=0.6)

    def toggle_mode(self):
        current = ctk.get_appearance_mode()
        new_mode = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        self.settings["theme"] = new_mode
        self._compute_theme_colors()
        self._apply_theme_to_widgets()
        self._reapply_filter_keep_view(scroll_to_top=False)

    # ===================== Persistence =====================
    def _load_settings(self):
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings.update({k: v for k, v in data.items() if k in self.settings})
        except Exception:
            pass  # ignore malformed file

    def _save_settings(self):
        # collect state
        self.settings["auto_refresh"] = self.settings.get("auto_refresh", True)
        self.settings["last_filter"] = self.filter_var.get()
        # persist watchlist as sorted unique IPs
        wl = list(dict.fromkeys(self.settings.get("watchlist", [])))
        self.settings["watchlist"] = wl
        # write file
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def _on_close(self):
        self._save_settings()
        self.destroy()

    # ===================== App Logic =====================
    def toggle_auto_refresh(self):
        self.settings["auto_refresh"] = not self.settings["auto_refresh"]
        self.toggle_btn.configure(text=f"auto: {'ON' if self.settings['auto_refresh'] else 'OFF'}")
        self._save_settings()

    def auto_refresh_loop(self):
        if self.settings.get("auto_refresh", True):
            self.refresh()
        self.after(self.refresh_interval, self.auto_refresh_loop)

    def refresh(self):
        self.status_line.configure(text="scanning…")
        self.devices = scan_network()

        # Ensure watchlist IPs are included in the scan set (so they get pinged)
        for ip in self.settings.get("watchlist", []):
            if ip not in self.devices:
                self.devices[ip] = {"mac": "", "status": "Offline", "ping": None, "history": [], "protocol": ""}

        # Save view state
        y_top = self.tree.yview()[0] if self.tree.get_children() else 0.0
        selection = self.tree.selection()

        # Reset tables
        for iid in list(self.main_row_ids):
            try: self.tree.delete(iid)
            except Exception: pass
        self.main_row_ids.clear()

        for iid in list(self.watch_row_ids):
            try: self.watch_tree.delete(iid)
            except Exception: pass
        self.watch_row_ids.clear()

        # Populate WATCHLIST first (always visible, regardless of filter)
        for ip in self.settings.get("watchlist", []):
            info = self.devices.get(ip, {"mac":"", "status":"Scanning…", "ping":"", "protocol":""})
            self._insert_row(self.watch_tree, self.watch_row_ids, ip, info)

        # Populate MAIN table
        for idx, (ip, info) in enumerate(self.devices.items()):
            self._insert_row(self.tree, self.main_row_ids, ip, info, idx)

        # Re-apply filter to MAIN only
        self._reapply_filter_keep_view(scroll_to_top=False)
        # Restore view if filter empty
        if not self.filter_var.get().strip():
            self.tree.yview_moveto(y_top)
        # Restore selection if present
        if selection:
            for iid in selection:
                if iid in self.main_row_ids:
                    self.tree.selection_add(iid)

        self.pending = len(self.devices)
        threaded_ping(self.devices, callback=self._on_ping_result)

    def _insert_row(self, tree, row_set, ip, info, idx=None):
        # Get nickname
        nickname = self.settings.get("nicknames", {}).get(ip, "")
        
        # Build status badge with icon (if available)
        status_text = info.get("status", "Scanning…")
        icon = self.icon_online if status_text == "Online" else self.icon_offline if status_text == "Offline" else None
        values = (nickname, ip, info.get("mac", ""), status_text, info.get("protocol", ""), self._ping_text(info.get("ping")))
        try:
            tree.insert("", "end", iid=str(ip), values=values)
            row_set.add(str(ip))
            # tag colors
            if tree is self.tree:
                if idx is not None:
                    tree.item(str(ip), tags=("evenrow" if idx % 2 == 0 else "oddrow",))
                if status_text in ("Online", "Offline"):
                    tree.item(str(ip), tags=(status_text,))
            else:
                if status_text in ("Online", "Offline"):
                    tree.item(str(ip), tags=(status_text,))
        except Exception:
            pass

    def _ping_text(self, val):
        if val is None or val == "":
            return ""
        try:
            return f"{float(val):.1f}"
        except Exception:
            return str(val)

    def _on_ping_result(self, ip, info):
        self.after(0, lambda: self._update_row(ip, info))

    def _update_row(self, ip, info):
        ip = str(ip)
        nickname = self.settings.get("nicknames", {}).get(ip, "")
        values = (nickname, ip, info.get("mac", ""), info.get("status", "?"),
                  info.get("protocol",""), self._ping_text(info.get("ping")))

        # Update MAIN
        if ip in self.main_row_ids:
            try:
                self.tree.item(ip, values=values, tags=(info.get("status",""),))
            except Exception:
                pass
            # If filter active, re-evaluate only this row
            if self.filter_var.get().strip():
                self._apply_filter_to_iid(ip, self.filter_var.get().lower().strip())

        # Update WATCHLIST (always visible)
        if ip in self.watch_row_ids:
            try:
                self.watch_tree.item(ip, values=values, tags=(info.get("status",""),))
            except Exception:
                pass

        # Update details if selected
        sel = self.tree.selection()
        if sel and sel[0] == ip:
            self.show_details(None)

        # Live KPI & chart
        self._update_kpis_live()
        online_count = sum(1 for d in self.devices.values() if d.get("status") == "Online")
        pings = [d["ping"] for d in self.devices.values() if d.get("ping") is not None]
        avg_ping = (sum(pings) / len(pings)) if pings else 0.0
        self._update_chart_curves(live=(online_count, avg_ping))
        self._chart_needs_draw = True

        # Completion
        self.pending = max(0, self.pending - 1)
        if self.pending == 0:
            self._commit_chart_point()
            self.status_line.configure(text="ready")

    # ===================== Filter (persistent, stable) =====================
    def _on_filter_changed(self, *args):
        # Remember in settings and reapply
        self.settings["last_filter"] = self.filter_var.get()
        self._save_settings()
        self._reapply_filter_keep_view(scroll_to_top=True)

    def clear_filter(self):
        self.filter_var.set("")
        self.filter_entry.focus_set()

    def _reapply_filter_keep_view(self, scroll_to_top=False):
        txt = self.filter_var.get().lower().strip()
        # Reattach all MAIN rows
        for iid in list(self.main_row_ids):
            try: self.tree.reattach(iid, "", "end")
            except Exception:
                self.main_row_ids.discard(iid)
        if not txt:
            if scroll_to_top:
                self.tree.yview_moveto(0.0)
            return
        # Detach non-matches
        for iid in list(self.main_row_ids):
            if not self._matches_filter(iid, txt):
                try: self.tree.detach(iid)
                except Exception: pass
        if scroll_to_top:
            self.tree.yview_moveto(0.0)

    def _matches_filter(self, iid, txt_lower):
        info = self.devices.get(iid, {})
        nickname = self.settings.get("nicknames", {}).get(iid, "")
        values = (
            nickname,
            iid,
            info.get("mac", ""),
            info.get("status", ""),
            info.get("protocol", ""),
            info.get("ping", ""),
        )
        try:
            return any(txt_lower in str(v).lower() for v in values)
        except Exception:
            return False

    def _apply_filter_to_iid(self, iid, txt_lower):
        try:
            if self._matches_filter(iid, txt_lower):
                self.tree.reattach(iid, "", "end")
            else:
                self.tree.detach(iid)
        except Exception:
            pass

    # ---------------- Details & KPIs --------------
    def show_details(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        ip = selected[0]
        info = self.devices.get(ip, {})
        nickname = self.settings.get("nicknames", {}).get(ip, "N/A")
        ping_val = info.get("ping")
        if ping_val is None:
            ping_text = "-"
        else:
            try:
                ping_text = f"{float(ping_val):.1f} ms"
            except Exception:
                ping_text = f"{ping_val} ms"
        history_list = info.get("history", [])
        history_text = ", ".join(history_list[-10:]) if history_list else ""
        text = (
            "nickname: {nick}\n"
            "ip: {ip}\n"
            "mac: {mac}\n"
            "status: {status}\n"
            "protocol: {proto}\n"
            "ping: {ping}\n"
            "history (last 10): {hist}"
        ).format(
            nick=nickname,
            ip=ip,
            mac=info.get("mac", "N/A"),
            status=info.get("status", "N/A"),
            proto=info.get("protocol", ""),
            ping=ping_text,
            hist=history_text,
        )
        self.detail_label.configure(text=text)