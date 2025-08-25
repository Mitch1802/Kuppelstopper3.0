import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class EditPopup(tb.Toplevel):
    """
    Einfaches modales Popup mit Labels + Eingabefeldern.
    fields: Liste von Tupeln (key, typ) oder (key, typ, extra) – typ in {"entry","spin","combo"}
    initial: dict mit Startwerten je key
    on_save: callback(dict) -> None
    """
    def __init__(self, master, title, fields, initial=None, on_save=None, width=380):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.transient(master)         # als Dialog über dem Master
        self.grab_set()                # modal
        self.on_save = on_save or (lambda data: None)
        self.widgets = {}
        self.result = {}

        body = tb.Frame(self, padding=10)
        body.pack(fill="both", expand=True)

        # Felder bauen
        initial = initial or {}
        for r, spec in enumerate(fields):
            if len(spec) == 2:
                key, ftype = spec
                extra = None
            else:
                key, ftype, extra = spec

            tb.Label(body, text=key).grid(row=r, column=0, sticky="w", padx=(0,10), pady=6)

            if ftype == "entry":
                w = tb.Entry(body, width=30)
                w.insert(0, str(initial.get(key, "")))
            elif ftype == "ro-entry":
                w = tb.Entry(body, width=30)
                w.insert(0, str(initial.get(key, "")))
                w.configure(state=DISABLED)
            elif ftype == "spin":
                frm, to = extra if extra else (0, 9999)
                w = tb.Spinbox(body, from_=frm, to=to, width=8)
                w.set(initial.get(key, 0))
            elif ftype == "combo":
                values = extra if extra else []
                w = tb.Combobox(body, values=values, state="readonly", width=27)
                w.set(initial.get(key, values[0] if values else ""))
            else:
                raise ValueError(f"Unbekannter Feldtyp: {ftype}")

            w.grid(row=r, column=1, sticky="ew", pady=6)
            self.widgets[key] = w

        # Buttons
        btnbar = tb.Frame(body)
        btnbar.grid(row=len(fields), column=0, columnspan=2, sticky="e", pady=(12,0))
        tb.Button(btnbar, text="Abbrechen", bootstyle=SECONDARY, command=self._cancel).pack(side="right", padx=(6,0))
        tb.Button(btnbar, text="Speichern", bootstyle=SUCCESS, command=self._save).pack(side="right")

        # Enter/ESC
        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self._cancel())

        # Zentrieren
        self.update_idletasks()
        self.geometry(self._center_geometry(master, width))

        # Fokus
        (next(iter(self.widgets.values()))).focus_set()

    def _center_geometry(self, master, width):
        mh, mw = master.winfo_height(), master.winfo_width()
        mx, my = master.winfo_rootx(), master.winfo_rooty()
        h = self.winfo_height()
        x = mx + (mw - width)//2
        y = my + (mh - h)//3
        return f"{width}x{h}+{max(0,x)}+{max(0,y)}"

    def _collect_values(self):
        data = {}
        for key, w in self.widgets.items():
            if isinstance(w, (tb.Spinbox,)):
                try:
                    data[key] = int(w.get())
                except ValueError:
                    data[key] = w.get()
            else:
                data[key] = w.get()
        return data

    def _save(self):
        self.result = self._collect_values()
        try:
            self.on_save(self.result)
        finally:
            self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()
