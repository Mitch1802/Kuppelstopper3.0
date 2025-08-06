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

        # 1) HEADER in Zeile 0, beide Spalten
        self.header_frame = tb.Frame(self)
        self._build_header()
        self.header_frame.grid(row=0, column=0, sticky=EW)

        # 2) CANVAS in Zeile 1, Spalte 0
        self.canvas = tb.Canvas(self, height=scroll_height, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky=NSEW)

        # 3) Scrollbar in Zeile 1, Spalte 1
        self.v_scroll = tb.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.v_scroll.grid(row=1, column=1, sticky=NS)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        # Damit Zeile 1 und Spalte 0 wachsen
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 4) Inneres Frame für die Datenzeilen
        self.inner = tb.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0,0), window=self.inner, anchor=NW)
        self.inner.bind('<Configure>', self._on_inner_configure)

        # Mausrad-Bindings
        self.canvas.bind('<Enter>', lambda e: self.canvas.bind_all('<MouseWheel>', self._on_mousewheel))
        self.canvas.bind('<Leave>', lambda e: self.canvas.unbind_all('<MouseWheel>'))

        # 5) Erster Tabellen-Aufbau
        self._build_table()

    def _build_header(self):
        for w in self.header_frame.winfo_children():
            w.destroy()
        for j, header in enumerate(self.coldata):
            lbl = tb.Label(self.header_frame, text=header, justify=LEFT, bootstyle=PRIMARY)
            lbl.grid(row=0, column=j, sticky=EW, padx=2, pady=2)
        for j, w in enumerate(self.percent_widths):
            self.header_frame.grid_columnconfigure(j, weight=w)

    def _on_inner_configure(self, event):
        # erst das Scrollregion-Update
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

        # verfügbare Breite im Canvas abfragen
        total_width = self.canvas.winfo_width()

        # Summe der Gewichte
        total_weight = sum(self.percent_widths)

        # für jede Spalte pixelgenaues minsize setzen
        x = 0
        for j, w in enumerate(self.percent_widths):
            # Spaltenbreite in Pixel
            col_w = int(total_width * (w / total_weight))
            # Header und inner synchron
            self.header_frame.grid_columnconfigure(j, minsize=col_w, weight=0)
            self.inner.grid_columnconfigure(j, minsize=col_w, weight=0)
            x += col_w

        # Fenster-Breite des inner-Frames an Canvas koppeln
        self.canvas.itemconfigure(self.window_id, width=total_width)

    def _on_mousewheel(self, event):
        delta = int(-1*(event.delta/120))
        self.canvas.yview_scroll(delta, 'units')

    def _destroy_table(self):
        for w in self.inner.winfo_children():
            w.destroy()

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
                    cmd = self.commands[j]
                    widget = tb.Button(self.inner, text=value, command=partial(cmd, row) if cmd else None)
                else:
                    widget = tb.Label(self.inner, text=value)
                    if command:
                         widget.bind("<Button-1>", partial(self._on_label_click, command, row))
                widget.grid(row=i, column=j, sticky=EW, padx=2, pady=2)

        # Spaltengewichte in inner UND header synchronisieren
        for j, w in enumerate(self.percent_widths):
            self.inner.grid_columnconfigure(j, weight=w)
            # self.header_frame.grid_columnconfigure(j, weight=w)
    
    def _on_label_click(self, command, value, event):
        command(value)

    def set_data(self, new_rowdata):
        self.rowdata = [list(r) + ['']*(len(self.coldata)-len(r)) for r in new_rowdata]
        self.entry_refs.clear()
        self._build_table()

    def get_entry_value(self, row, col):
        e = self.entry_refs.get((row, col))
        return e.get() if e else None
