import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from functools import partial

class CustomTable(tb.Frame):
    def __init__(
        self,
        master,
        coldata,
        rowdata,
        percent_widths=None,
        cell_types=None,
        commands=None,
        scroll_height=300,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.coldata = coldata
        self.rowdata = rowdata
        self.percent_widths = percent_widths or [1] * len(coldata)
        self.cell_types = cell_types or ['label'] * len(coldata)
        self.commands = commands or [None] * len(coldata)
        self.entry_refs = {}

        # 1) HEADER
        self.header_frame = tb.Frame(self)
        self._build_header()
        self.header_frame.grid(row=0, column=0, sticky=EW)

        # 2) CANVAS
        self.canvas = tb.Canvas(self, height=scroll_height, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky=NSEW)

        # 3) Scrollbar
        self.v_scroll = tb.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.v_scroll.grid(row=1, column=1, sticky=NS)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        # Root-Grid expandieren
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 4) Inneres Frame
        self.inner = tb.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor=NW)
        self.inner.bind('<Configure>', self._on_inner_configure)

        # WICHTIG: auch Canvas-Resizes beobachten
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        # Mausrad
        self.canvas.bind('<Enter>', lambda e: self.canvas.bind_all('<MouseWheel>', self._on_mousewheel))
        self.canvas.bind('<Leave>', lambda e: self.canvas.unbind_all('<MouseWheel>'))

        # 5) Erstaufbau
        self._build_table()

    # ------------------ Layout/Hilfen ------------------

    def _build_header(self):
        for w in self.header_frame.winfo_children():
            w.destroy()
        for j, header in enumerate(self.coldata):
            lbl = tb.Label(self.header_frame, text=header, justify=LEFT, bootstyle=PRIMARY)
            lbl.grid(row=0, column=j, sticky=EW, padx=2, pady=2)
            # WICHTIG: keine weight-Verteilung hier; Breiten laufen über minsize
            self.header_frame.grid_columnconfigure(j, weight=0)

    def _sync_column_widths(self):
        """Synchronisiere Header/Daten-Spaltenbreiten proportional zur Canvas-Breite."""
        total_width = max(self.canvas.winfo_width(), 1)
        total_weight = max(sum(self.percent_widths), 1)

        for j, w in enumerate(self.percent_widths):
            col_w = int(total_width * (w / total_weight))
            # Header & Inner: minsize setzen, weight auf 0 lassen
            self.header_frame.grid_columnconfigure(j, minsize=col_w, weight=0)
            self.inner.grid_columnconfigure(j, minsize=col_w, weight=0)

        # Inner-Container an Canvas-Breite koppeln
        self.canvas.itemconfigure(self.window_id, width=total_width)

    def _on_inner_configure(self, event):
        # Scrollregion aktualisieren
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        # Spaltenbreiten synchronisieren
        self._sync_column_widths()

    def _on_canvas_configure(self, event):
        # Bei Canvas-Resize Spaltenbreiten ebenfalls anpassen
        self._sync_column_widths()

    def _on_mousewheel(self, event):
        delta = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(delta, 'units')

    def _destroy_table(self):
        for w in self.inner.winfo_children():
            w.destroy()

    # ------------------ Aufbau/Refresh ------------------

    def _build_table(self):
        self._destroy_table()
        for i, row in enumerate(self.rowdata, start=1):
            cells = list(row) + [''] * (len(self.coldata) - len(row))
            for j, value in enumerate(cells):
                ctype = self.cell_types[j]
                command = self.commands[j]

                if ctype == 'entry':
                    widget = tb.Entry(self.inner)
                    widget.insert(0, value)
                    self.entry_refs[(i-1, j)] = widget

                elif ctype == 'button':
                    widget = tb.Button(
                        self.inner,
                        text=value,
                        command=partial(command, row) if command else None
                    )

                else:  # label (default)
                    widget = tb.Label(self.inner, text=value)
                    if command:
                        widget.bind("<Button-1>", partial(self._on_label_click, command, row))

                widget.grid(row=i, column=j, sticky=EW, padx=2, pady=2)

        # Wichtig: KEINE weight-Verteilung hier setzen (wir nutzen minsize)!
        for j in range(len(self.coldata)):
            self.inner.grid_columnconfigure(j, weight=0)

        # Nach Neuaufbau scrollregion neu, Breiten sync
        self.inner.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self._sync_column_widths()

    def _on_label_click(self, command, value, event):
        command(value)

    def set_data(self, new_rowdata):
        self.rowdata = [list(r) + [''] * (len(self.coldata) - len(r)) for r in new_rowdata]
        self.entry_refs.clear()
        self._build_table()
        # Scrollposition zurück an den Anfang – nützlich nach Updates
        self.canvas.yview_moveto(0)

    def get_entry_value(self, row, col):
        e = self.entry_refs.get((row, col))
        return e.get() if e else None
