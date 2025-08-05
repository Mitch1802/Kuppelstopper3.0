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

        # Header frame (sticky top)
        self.header_frame = tb.Frame(self)
        self.header_frame.pack(fill=X)
        self._build_header()

        # Canvas for scrollable rows
        self.canvas = tk.Canvas(self, height=scroll_height, highlightthickness=0)
        self.v_scroll = tb.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        # Layout scrollbars and canvas
        self.v_scroll.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)

        # Inner frame within canvas
        self.inner = tb.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor='nw')
        self.inner.bind('<Configure>', self._on_frame_configure)

        # Mouse wheel bindings
        self.canvas.bind('<Enter>', self._bind_mouse)
        self.canvas.bind('<Leave>', self._unbind_mouse)

        # Build initial table rows
        self._build_table()

    def _build_header(self):
        # Clear existing header widgets
        for w in self.header_frame.winfo_children():
            w.destroy()
        # Create header labels
        for j, header in enumerate(self.coldata):
            lbl = tb.Label(
                self.header_frame,
                text=header,
                anchor='center',
                bootstyle='secondary',
                width=int(self.percent_widths[j])
            )
            lbl.grid(row=0, column=j, sticky='ew', padx=2, pady=2)
        # Configure header columns
        for j in range(len(self.coldata)):
            self.header_frame.grid_columnconfigure(j, weight=1)

    def _on_frame_configure(self, event):
        # Update scrollregion to include all inner widgets
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        # Make inner width match canvas width
        canvas_width = event.width
        self.canvas.itemconfigure(self.window_id, width=canvas_width)

    def _bind_mouse(self, event):
        # Windows/Mac
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        # Linux
        self.canvas.bind_all('<Button-4>', lambda e: self.canvas.yview_scroll(-1, 'units'))
        self.canvas.bind_all('<Button-5>', lambda e: self.canvas.yview_scroll(1, 'units'))

    def _unbind_mouse(self, event):
        self.canvas.unbind_all('<MouseWheel>')
        self.canvas.unbind_all('<Button-4>')
        self.canvas.unbind_all('<Button-5>')

    def _on_mousewheel(self, event):
        delta = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(delta, 'units')

    def _destroy_table(self):
        for w in self.inner.winfo_children():
            w.destroy()

    def _build_table(self):
        # Clear existing row widgets
        self._destroy_table()
        # Create rows
        for i, row in enumerate(self.rowdata, start=1):
            cells = list(row) + [''] * (len(self.coldata) - len(row))
            for j, value in enumerate(cells):
                ctype = self.cell_types[j]
                if ctype == 'label':
                    widget = tb.Label(self.inner, text=value, anchor='w')
                elif ctype == 'entry':
                    widget = tb.Entry(self.inner)
                    widget.insert(0, value)
                    self.entry_refs[(i-1, j)] = widget
                elif ctype == 'button':
                    cmd = self.commands[j]
                    widget = tb.Button(
                        self.inner,
                        text=value,
                        command=partial(cmd, row) if cmd else None
                    )
                else:
                    widget = tb.Label(self.inner, text=value)
                widget.grid(row=i, column=j, sticky='ew', padx=2, pady=2)
        # Configure row columns expansion
        for j in range(len(self.coldata)):
            self.inner.grid_columnconfigure(j, weight=1)

    def set_data(self, new_rowdata):
        # Normalize row lengths and rebuild rows
        self.rowdata = [list(r) + [''] * (len(self.coldata) - len(r)) for r in new_rowdata]
        self.entry_refs.clear()
        self._build_table()

    def get_entry_value(self, row, col):
        entry = self.entry_refs.get((row, col))
        if entry:
            return entry.get()
        return None
