# gui/auswertung_window.py
from tkinter import *
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from gui.custom_table import CustomTable

def _parse_bestzeit_val(val):
    if not val or val == '00:00:00':
        return None
    s = str(val).strip().replace(',', '.')
    try:
        return float(s)
    except ValueError:
        parts = s.split(':')
        try:
            if len(parts) == 2:
                m, ss = parts
                return int(m) * 60 + float(ss)
            if len(parts) == 3:
                h, m, ss = parts
                return int(h) * 3600 + int(m) * 60 + float(ss)
        except Exception:
            return None
    return None

def _fmt_bestzeit(v):
    return "-" if v is None else f"{v:.2f}s"

class AuswertungWindow(tb.Toplevel):
    """Eigenes Fenster für Rangliste / Bestzeiten (zweiter Bildschirm)."""
    def __init__(self, master, zeit_manager, durchgang_manager, *, themename="litera"):
        super().__init__(master)
        # Optik
        self.title("Rangliste")
        self.style = tb.Style(themename=themename)

        # Vollbild-Taste ESC beenden
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        # Inhalt
        header = tb.Label(self, text="Rangliste / Bestzeiten", font=("Arial", 16, "bold"))
        header.pack(pady=10)

        self.coldata = ["Platz", "Gruppe", "Bestzeit inkl. Fehler"]
        self.cell_types = ["label", "label", "label"]
        self.percent_widths = [15, 55, 30]

        self.tbl = CustomTable(
            self,
            coldata=self.coldata,
            rowdata=[],
            percent_widths=self.percent_widths,
            cell_types=self.cell_types,
            scroll_height=800,
        )
        self.tbl.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.btnbar = tb.Frame(self)
        self.btnbar.pack(fill=X, padx=10, pady=(0,10))
        tb.Button(self.btnbar, text="Aktualisieren", command=self.refresh).pack(side=LEFT)
        tb.Button(self.btnbar, text="Vollbild an/aus", command=self.toggle_fullscreen).pack(side=LEFT, padx=6)

        self.zeit_manager = zeit_manager
        self.durchgang_manager = durchgang_manager

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.refresh()

    # ------------ Steuerung / Anzeige -------------
    def toggle_fullscreen(self):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def _on_close(self):
        """Beim Schließen sauber referenz im Master löschen, nicht nur verstecken."""
        try:
            if hasattr(self.master, "win_auswertung"):
                self.master.win_auswertung = None
        except Exception:
            pass
        self.destroy()

    def show_on_monitor(self, monitor_index=1, *, fullscreen=False, fallback_geometry="+1920+0", margin=40):
        """
        Fenster auf gewünschten Monitor schieben.
        - monitor_index: 0 = primär, 1 = zweiter Monitor, ...
        - versucht 'screeninfo' (pip install screeninfo), sonst Fallback-Koordinaten.
        """
        try:
            from screeninfo import get_monitors  # optional
            mons = get_monitors()
            if 0 <= monitor_index < len(mons):
                m = mons[monitor_index]
                # leicht kleiner als die Bildschirmgröße für Fensterränder
                w = max(400, m.width - margin)
                h = max(300, m.height - margin)
                x = m.x + margin//2
                y = m.y + margin//2
                self.geometry(f"{w}x{h}+{x}+{y}")
                self.update_idletasks()
                if fullscreen:
                    self.after(200, lambda: self.attributes("-fullscreen", True))
                return
        except Exception:
            pass
        # Fallback: fixe Koordinaten (z. B. zweiter Monitor rechts bei 1920px Breite)
        self.geometry(fallback_geometry)
        self.update_idletasks()
        if fullscreen:
            self.after(200, lambda: self.attributes("-fullscreen", True))

    def refresh(self):
        """Daten aus DurchgangManager lesen und Rangliste neu rendern."""
        bewerb = getattr(self.durchgang_manager, "Bewerb", [])
        best_by_group = {}

        for row in bewerb:
            if len(row) < 7:
                continue
            gruppe = row[1]
            best_str = row[6]
            best_val = _parse_bestzeit_val(best_str)
            if best_val is None:
                continue
            if gruppe not in best_by_group or best_val < best_by_group[gruppe]:
                best_by_group[gruppe] = best_val

        sortiert = sorted(best_by_group.items(), key=lambda x: x[1])
        table_rows = [[i, grp, _fmt_bestzeit(val)] for i, (grp, val) in enumerate(sortiert, start=1)]
        self.tbl.set_data(table_rows)
