import tkinter as tk

class CustomListbox(tk.Listbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="lightyellow", font=("Arial", 10))