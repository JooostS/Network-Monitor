# ---------- Entry Point ----------
from gui import NetworkMonitorGUI
import customtkinter as ctk

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")
    app = NetworkMonitorGUI()
    ml = getattr(app, "mainloop", None)
    if isinstance(ml, dict):
        try:
            delattr(app, "mainloop")
        except Exception:
            pass
    try:
        app.mainloop()
    except TypeError:
        print("type(app.mainloop):", type(getattr(app, "mainloop", None)))
        ctk.CTk.mainloop(app)