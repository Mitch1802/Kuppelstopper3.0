import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.constants import *

class CustomTable:
    def __init__(self, master, coldata, rowdata, percent_widths=None, cell_types=None, commands=None):
        self.master = master
        self.coldata = coldata
        self.rowdata = rowdata
        self.percent_widths = percent_widths or [100 // len(coldata)] * len(coldata)
        self.cell_types = cell_types or ["label"] * len(coldata)  # "label", "entry", "button"
        self.commands = commands or [None] * len(coldata)  # command-Funktionen für Buttons oder Labels
        self.entry_refs = {}  # Speichert Entry-Referenzen

        self._build_table()

    def _build_table(self):
        # ScrolledFrame ohne sichtbare Scrollbars
        self.sf = ScrolledFrame(self.master, autohide=False)
        self.table = self.sf.container  # Richtiges Frame für Inhalt

        # Header-Zeile
        for i, (col, pct) in enumerate(zip(self.coldata, self.percent_widths)):
            lbl = tb.Label(self.table, text=col, anchor=W, font=("Segoe UI", 10, "bold"))
            lbl.grid(row=0, column=i, sticky=EW, padx=(0,15), pady=2)
            self.table.grid_columnconfigure(i, weight=pct)

        # Daten-Zeilen
        for r, row in enumerate(self.rowdata, start=1):
            for c, val in enumerate(row):
                cell_type = self.cell_types[c] if c < len(self.cell_types) else "label"
                command = self.commands[c] if c < len(self.commands) else None

                if cell_type == "entry":
                    entry = tb.Entry(self.table)
                    entry.insert(0, val)
                    entry.grid(row=r, column=c, sticky=EW, padx=(0,15), pady=2)
                    self.entry_refs[(r, c)] = entry
                elif cell_type == "button":
                    btn = tb.Button(self.table, text=val, command=lambda v=val, r=r, c=c: command(v, r, c) if command else None)
                    btn.grid(row=r, column=c, sticky=EW, padx=(0,15), pady=2)
                else:
                    lbl = tb.Label(self.table, text=val, anchor=W)
                    lbl.grid(row=r, column=c, sticky=EW, padx=(0,15), pady=2)
                    if command:
                        lbl.bind("<Button-1>", lambda e, v=val, r=r, c=c: command(v, r, c))

    def get_entry_value(self, row, col):
        entry = self.entry_refs.get((row, col))
        if entry:
            return entry.get()
        return None

    def pack(self, **kwargs):
        self.sf.pack(**kwargs)

    def grid(self, **kwargs):
        self.sf.grid(**kwargs)

    def place(self, **kwargs):
        self.sf.place(**kwargs)

    def destroy(self):
        self.sf.destroy()

    def hide_scrollbars(self):
        self.sf.hide_scrollbars()
    
    def _on_enter(self, event):
        self.sf.hide_scrollbars()
