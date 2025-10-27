from gui import NetworkMonitorGUI
import customtkinter as ctk

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")  # or "Light"
    ctk.set_default_color_theme("dark-blue")

    app = NetworkMonitorGUI()

    # --- safety: if an instance attribute named 'mainloop' is shadowing the Tk method, remove or repair it
    ml = getattr(app, "mainloop", None)
    if isinstance(ml, dict):
        try:
            # Remove the shadowing instance attribute, revealing the real class method
            delattr(app, "mainloop")
        except Exception:
            pass

    try:
        # Normal call (works if nothing shadows the method)
        app.mainloop()
    except TypeError:
        # Fallback: call the class method explicitly (cannot be shadowed by an instance attribute)
        print("type(app.mainloop):", type(getattr(app, "mainloop", None)))
        ctk.CTk.mainloop(app)