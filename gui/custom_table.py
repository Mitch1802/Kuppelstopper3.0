import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.constants import *
from functools import partial

class CustomTable:
    def __init__(self, master, coldata, rowdata, percent_widths=None, cell_types=None, commands=None):
        self.master = master
        self.coldata = coldata
        self.rowdata = rowdata
        self.percent_widths = percent_widths or [100 // len(coldata)] * len(coldata)
        self.cell_types = cell_types or ["label"] * len(coldata)  # "label", "entry", "button"
        self.commands = commands or [None] * len(coldata)  # command-Funktionen für Buttons oder Labels
        self.entry_refs = {}

        self.sf = None  # ScrolledFrame-Referenz
        self.table = None  # Innenliegendes Container-Frame

        self._build_table()

    def _destroy_scrolled_frame(self):
        if self.sf and self.sf.winfo_exists():
            try:
                self.sf.container.unbind("<Configure>")
                self.sf.unbind("<Enter>")
                self.sf.unbind("<Leave>")
            except Exception as e:
                print("[WARN] Unbind failed:", e)
            self.sf.destroy()
        self.sf = None
        self.table = None

    def _build_table(self):
        self._destroy_scrolled_frame()

        self.master.update_idletasks()

        parent_height = self.master.winfo_height()
        if parent_height < 10:
            parent_height = 600  # Fallback
        dynamic_height = max(200, int(parent_height * 0.5))
        print("[DEBUG] Tabelle wird aufgebaut mit Höhe:", dynamic_height)

        self.sf = ScrolledFrame(self.master, autohide=False, height=dynamic_height)
        self.table = self.sf.container

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
                    btn = tb.Button(self.table, text=val, command=lambda v=row, r=r, c=c: command(v, r, c) if command else None)
                    btn.grid(row=r, column=c, sticky=EW, padx=(0,15), pady=2)
                else:
                    lbl = tb.Label(self.table, text=val, anchor=W)
                    lbl.grid(row=r, column=c, sticky=EW, padx=(0,15), pady=2)
                    if command:
                        lbl.bind("<Button-1>", partial(self._on_label_click, command, row, r, c))

    def _on_label_click(self, command, value, row_idx, col_idx, event):
        command(value, row_idx, col_idx)

    def get_entry_value(self, row, col):
        entry = self.entry_refs.get((row, col))
        if entry:
            return entry.get()
        return None

    def pack(self, **kwargs):
        if self.sf:
            self.sf.pack(**kwargs)

    def grid(self, **kwargs):
        if self.sf:
            self.sf.grid(**kwargs)

    def place(self, **kwargs):
        if self.sf:
            self.sf.place(**kwargs)

    def destroy(self):
        self._destroy_scrolled_frame()

    def set_data(self, new_rowdata):
        """Ersetzt die angezeigten Zeilen durch neue Inhalte."""
        for gruppe in new_rowdata:
            if len(gruppe) < len(self.coldata):
                gruppe.append("X")

        self.rowdata = new_rowdata
        self.entry_refs = {}

        self._build_table()
        self.pack(fill=BOTH, expand=YES, padx=10, pady=10)
