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
    """
    Zweites Fenster:
    - oben: Nächste Durchgänge (Queue)
    - unten: umschaltbar -> 'zeit' (aktuelle Gruppe) ODER 'rang' (Rangliste)
    """
    def __init__(self, master, zeit_manager, durchgang_manager, *, themename="litera"):
        super().__init__(master)
        self.title("Auswertung / Anzeige")
        self.geometry("800x600+0+0")

        self.curr_group_bahn1 = None
        self.curr_group_bahn2 = None

        self.zeit_manager = zeit_manager
        self.durchgang_manager = durchgang_manager
        self.modus = "zeit"  # default: 'zeit' oder 'rang'

        # ==== OBERER BEREICH: Nächste Durchgänge ====
        top = tb.Frame(self)
        top.pack(fill=X, padx=12, pady=(12, 6))

        tb.Label(top, text="Nächste Durchgangs‑Gruppen", font=("Arial", 14, "bold")).pack(side=LEFT)

        self.tbl_next = CustomTable(
            self,
            coldata=["DG", "Gruppe"],
            rowdata=[],
            percent_widths=[20, 80],
            cell_types=["label", "label"],
            scroll_height=160,
        )
        self.tbl_next.pack(fill=X, padx=12)

        # ==== UNTERER BEREICH (Stack) ====
        bottom = tb.Frame(self)
        bottom.pack(fill=BOTH, expand=YES, padx=12, pady=12)

        # 1) ZEIT-Ansicht (aktuelle Gruppe groß)
        self.frame_zeit = tb.Frame(bottom)
        self.lbl_curr_title = tb.Label(self.frame_zeit, text="Aktuelle Gruppe", font=("Arial", 14, "bold"))
        self.lbl_curr_title.pack(anchor=W, pady=(0, 8))

        self.lbl_curr_group = tb.Label(self.frame_zeit, text="—", font=("Arial", 40, "bold"))
        self.lbl_curr_group.pack(pady=(0, 16))

        # Anzeige der Zeiten (nur Anzeige; Steuerung bleibt im Hauptfenster)
        row_time = tb.Frame(self.frame_zeit)
        row_time.pack(pady=8)
        self.lbl_t1 = tb.Label(row_time, text="Zeit 1: –", font=("Arial", 24))
        self.lbl_t1.pack(side=LEFT, padx=20)
        self.lbl_f1 = tb.Label(row_time, text="F1: 0", font=("Arial", 24))
        self.lbl_f1.pack(side=LEFT, padx=20)
        self.lbl_t2 = tb.Label(row_time, text="Zeit 2: –", font=("Arial", 24))
        self.lbl_t2.pack(side=LEFT, padx=20)
        self.lbl_f2 = tb.Label(row_time, text="F2: 0", font=("Arial", 24))
        self.lbl_f2.pack(side=LEFT, padx=20)

        tb.Label(self.frame_zeit, text="(Die Zeitsteuerung erfolgt im Hauptfenster.)", font=("Arial", 11, "italic")).pack(pady=(10,0))

        # 2) RANG‑Ansicht
        self.frame_rang = tb.Frame(bottom)
        tb.Label(self.frame_rang, text="Rangliste / Bestzeiten", font=("Arial", 14, "bold")).pack(anchor=W, pady=(0, 8))

        self.tbl_rang = CustomTable(
            self.frame_rang,
            coldata=["Platz", "Gruppe", "Bestzeit inkl. Fehler"],
            rowdata=[],
            percent_widths=[15, 55, 30],
            cell_types=["label", "label", "label"],
            scroll_height=500,
        )
        self.tbl_rang.pack(fill=BOTH, expand=YES)

        # Startansicht
        self._show_mode(self.modus)

        # zyklisches Refresh
        self.after(400, self._auto_refresh)

        # sauber schließen
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ======= Öffentliche API ========
    def set_mode(self, modus: str):
        """Extern aufrufbar: 'zeit' oder 'rang'."""
        modus = (modus or "").lower()
        if modus not in ("zeit", "rang"):
            return
        self.modus = modus
        self._show_mode(modus)

    def show_on_monitor(self, monitor_index=1, *, fullscreen=False, fallback_geometry="+1920+0", margin=40):
        try:
            from screeninfo import get_monitors
            mons = get_monitors()
            if 0 <= monitor_index < len(mons):
                m = mons[monitor_index]
                w = max(600, m.width - margin)
                h = max(400, m.height - margin)
                x = m.x + margin//2
                y = m.y + margin//2
                self.geometry(f"{w}x{h}+{x}+{y}")
                self.update_idletasks()
                if fullscreen:
                    self.after(200, lambda: self.attributes("-fullscreen", True))
                return
        except Exception:
            pass
        self.geometry(fallback_geometry)
        self.update_idletasks()
        if fullscreen:
            self.after(200, lambda: self.attributes("-fullscreen", True))

    def refresh(self):
        """Einmaliges Refresh beider Bereiche."""
        self._refresh_next_groups()
        if self.modus == "rang":
            self._refresh_rangliste()
        else:
            self._refresh_current_group_and_times()

    def update_times(self, zeit1: str = None, f1: int = None, zeit2: str = None, f2: int = None):
        """Optionaler Hook: kann vom MainWindow aufgerufen werden, um Zeiten direkt zu pushen."""
        if zeit1 is not None:
            self.lbl_t1.config(text=f"Zeit 1: {zeit1}")
        if f1 is not None:
            self.lbl_f1.config(text=f"F1: {f1}")
        if zeit2 is not None:
            self.lbl_t2.config(text=f"Zeit 2: {zeit2}")
        if f2 is not None:
            self.lbl_f2.config(text=f"F2: {f2}")

    def set_current_groups(self, bahn1: str | None, bahn2: str | None):
        """Vom MainWindow aufrufen: setzt die aktuell anzuzeigenden Gruppen."""
        self.curr_group_bahn1 = bahn1
        self.curr_group_bahn2 = bahn2
        # Falls du die 'ZEIT'-Ansicht nutzt, hier gleich die Labels updaten:
        if hasattr(self, "lbl_curr_group"):
            if bahn1 and bahn2:
                self.lbl_curr_group.config(text=f"{bahn1}  |  {bahn2}")
            elif bahn1:
                self.lbl_curr_group.config(text=str(bahn1))
            elif bahn2:
                self.lbl_curr_group.config(text=str(bahn2))
            else:
                self.lbl_curr_group.config(text="—")

    # ======= intern ========
    def _on_close(self):
        try:
            if hasattr(self.master, "win_auswertung"):
                self.master.win_auswertung = None
        except Exception:
            pass
        self.destroy()

    def _show_mode(self, modus):
        # Frames umschalten
        self.frame_zeit.pack_forget()
        self.frame_rang.pack_forget()
        if modus == "rang":
            self.frame_rang.pack(fill=BOTH, expand=YES, padx=0, pady=(8,0))
            self._refresh_rangliste()
        else:
            self.frame_zeit.pack(fill=BOTH, expand=YES, padx=0, pady=(8,0))
            self._refresh_current_group_and_times()

    def _auto_refresh(self):
        """Kleiner Poller – hält die Daten aktuell, ohne Buttons zu drücken."""
        self.refresh()
        self.after(1500, self._auto_refresh)

    # ---- Datenaufbereitung ----
    def _find_current_index(self):
        """
        Heuristik: 'aktuell' = erster DG, dessen Bestzeit (Spalte 6) noch '00:00:00' oder leer ist.
        Format pro Zeile erwartet: [DG, Gruppe, Zeit1, F1, Zeit2, F2, Bestzeit inkl. Fehler]
        """
        bewerb = getattr(self.durchgang_manager, "Bewerb", [])
        for idx, row in enumerate(bewerb):
            if len(row) < 7:
                continue
            best = str(row[6]).strip()
            if not best or best == "00:00:00" or _parse_bestzeit_val(best) is None:
                return idx
        return None

    def _refresh_next_groups(self, count: int = 5):
        bewerb = getattr(self.durchgang_manager, "Bewerb", [])
        idx = self._find_current_index()
        start = (idx + 1) if idx is not None else 0
        rows = []
        for r in bewerb[start:start+count]:
            if len(r) >= 2:
                rows.append([r[0], r[1]])
        self.tbl_next.set_data(rows)

    def _refresh_current_group_and_times(self):
        bewerb = getattr(self.durchgang_manager, "Bewerb", [])
        idx = self._find_current_index()
        if idx is None or idx >= len(bewerb):
            self.lbl_curr_group.config(text="—")
            self.update_times("–", 0, "–", 0)
            return
        row = bewerb[idx]
        gruppe = row[1]
        zeit1, f1, zeit2, f2 = row[2], row[3], row[5], row[6] if len(row) > 6 else 0
        # ACHTUNG: In manchen Sets ist Spalte 6 'Bestzeit', nicht F2 -> deshalb F2 sicher aus Spalte 4? Passe ggf. an.
        # Wenn deine Struktur exakt ist: [DG, Gruppe, Zeit1, F1, Zeit2, F2, Best]
        zeit1, f1, zeit2, f2 = row[2], row[3], row[4], row[5]
        self.lbl_curr_group.config(text=str(gruppe))
        self.update_times(zeit1 or "–", f1 or 0, zeit2 or "–", f2 or 0)

    def _refresh_rangliste(self):
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
        self.tbl_rang.set_data(table_rows)
