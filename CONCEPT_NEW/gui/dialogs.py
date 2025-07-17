import tkinter as tk

class EinstellungenDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Einstellungen")
        self.geometry("250x120")
        tk.Label(self, text="Hier Einstellungen ändern").pack(pady=10)
        tk.Button(self, text="Speichern", command=self.destroy).pack(pady=10)