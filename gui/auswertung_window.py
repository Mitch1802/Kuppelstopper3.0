# gui/auswertung_window.py
from tkinter import *
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class AuswertungWindow(tb.Toplevel):
    """
    Zweites Fenster für die Zuschaueranzeige:
      - Oben: Label mit den zwei Gruppennamen des nächsten Durchgangs
      - Unten: Zeit-Layout (links oben Gruppe1, Mitte Zeit1, darunter Zeit2, rechts unten Gruppe2)
    Die Inhalte werden vom MainView aktiv 'gepusht', damit alles 1:1 synchron ist.
    """

    def __init__(self, master, zeit_manager, durchgang_manager, *, themename="litera"):
        super().__init__(master)
        self.title("Auswertung / Anzeige")
        self.geometry("1200x900+200+100")

        # Referenzen (falls du später noch etwas brauchst)
        self.zeit_manager = zeit_manager
        self.durchgang_manager = durchgang_manager

        # aktuell gesetzte Werte (nur zur Info/Speicherung)
        self.curr_group_bahn1 = None
        self.curr_group_bahn2 = None
        self.next_group_1 = None
        self.next_group_2 = None
        self.size_group = 36
        self.size_time = 50

        # ========= OBERER BEREICH =========
        top = tb.Frame(self)
        top.pack(fill=X, padx=12, pady=(12, 6))

        tb.Label(top, text="Nächster Durchgang", font=("Arial", 14, "bold")).pack(anchor=W)

        self.lbl_next = tb.Label(top, text="—  vs  —", font=("Arial", 28, "bold"), anchor=CENTER)
        self.lbl_next.pack(fill=X, pady=10)

        separator = tb.Separator(top, orient="horizontal")
        separator.pack(fill=X, pady=10)

        # ========= UNTERER BEREICH (ZEIT-ANSICHT) =========
        bottom = tb.Frame(self)
        bottom.pack(fill=BOTH, expand=YES, padx=12, pady=12)

        self.frame_zeit = tb.Frame(bottom)
        self.frame_zeit.pack(fill=BOTH, expand=YES)

        # Grid-Konfiguration, damit Mitte wirklich mittig bleibt
        # 2 Spalten, 4 Zeilen -> wir nutzen column/row weight für zentrierte Zeiten
        self.frame_zeit.columnconfigure(0, weight=1)
        self.frame_zeit.columnconfigure(1, weight=1)
        self.frame_zeit.rowconfigure(0, weight=1)
        self.frame_zeit.rowconfigure(1, weight=1)
        self.frame_zeit.rowconfigure(2, weight=1)
        self.frame_zeit.rowconfigure(3, weight=1)

        # links oben: Gruppe 1
        self.lbl_b1 = tb.Label(self.frame_zeit, text="—", font=("Arial", self.size_group, "bold"))
        self.lbl_b1.grid(row=0, column=0, sticky="nw", padx=20, pady=20)

        # Mitte: Zeit 1 (Reihe 1, zentriert über beide Spalten)
        self.lbl_t1 = tb.Label(self.frame_zeit, text="Zeit 1: –", font=("Arial", self.size_time))
        self.lbl_t1.grid(row=1, column=0, columnspan=2, sticky="n", pady=(10, 10))

        # darunter Mitte: Zeit 2 (Reihe 2, zentriert über beide Spalten)
        self.lbl_t2 = tb.Label(self.frame_zeit, text="Zeit 2: –", font=("Arial",self.size_time))
        self.lbl_t2.grid(row=2, column=0, columnspan=2, sticky="n", pady=(0, 10))

        # rechts unten: Gruppe 2
        self.lbl_b2 = tb.Label(self.frame_zeit, text="—", font=("Arial", self.size_group, "bold"))
        self.lbl_b2.grid(row=3, column=1, sticky="se", padx=20, pady=20)

        # sauberes Schließen
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ========== Öffentliche API (vom MainView aufrufen) ==========

    def set_current_groups(self, bahn1: str, bahn2: str):
        """Aktuelle Gruppen (Bahn 1 / Bahn 2) setzen."""
        self.curr_group_bahn1 = bahn1
        self.curr_group_bahn2 = bahn2
        self.lbl_b1.config(text=bahn1 or "—")
        self.lbl_b2.config(text=bahn2 or "—")

    def set_next_groups(self, next1: str, next2: str):
        """Nächster Durchgang oben im Label anzeigen (zwei Gruppennamen)."""
        self.next_group_1 = next1
        self.next_group_2 = next2
        self.lbl_next.config(text=f"{next1 or '—'}  vs  {next2 or '—'}")

    def update_times(self, zeit1: str = None, zeit2: str = None):
        """Zeiten 1/2 direkt aus dem MainView übernehmen (push-basiert)."""
        if zeit1 is not None:
            self.lbl_t1.config(text=zeit1)
        if zeit2 is not None:
            self.lbl_t2.config(text=zeit2)

    def show_on_monitor(self, monitor_index=1, *, fullscreen=False, fallback_geometry="+1920+0", margin=200):
        """
        Fenster auf gewünschten Monitor verschieben.
        - monitor_index: 0 = primär, 1 = zweiter Monitor, ...
        - nutzt screeninfo, falls vorhanden; sonst fallback_geometry.
        """
        try:
            from screeninfo import get_monitors
            mons = get_monitors()
            if 0 <= monitor_index < len(mons):
                m = mons[monitor_index]
                w = max(600, m.width - margin)
                h = max(400, m.height - margin)
                x = m.x + margin // 2
                y = m.y + margin // 2
                self.geometry(f"{w}x{h}+{x}+{y}")
                self.update_idletasks()
                if fullscreen:
                    self.after(200, lambda: self.attributes("-fullscreen", True))
                return
        except Exception:
            pass

        # Fallback
        self.geometry(fallback_geometry)
        self.update_idletasks()
        if fullscreen:
            self.after(200, lambda: self.attributes("-fullscreen", True))
    
    def change_font_size_group(self, size):
        self.lbl_b1.config(font=("Arial", size, "bold"))
        self.lbl_b2.config(font=("Arial", size, "bold"))

    def change_font_size_time(self, size):
        self.lbl_t1.config(font=("Arial", size, "bold"))
        self.lbl_t2.config(font=("Arial", size, "bold"))
    
    def change_font_size_from_window(self, time, group):
        self.lbl_b1.config(font=("Arial", group, "bold"))
        self.lbl_t1.config(font=("Arial", time, "bold"))
        self.lbl_t2.config(font=("Arial", time, "bold"))
        self.lbl_b2.config(font=("Arial", group, "bold"))

    # ========== intern ==========

    def _on_close(self):
        try:
            if hasattr(self.master, "win_auswertung"):
                self.master.win_auswertung = None
        except Exception:
            pass
        self.destroy()
