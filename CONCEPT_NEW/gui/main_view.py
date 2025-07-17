import tkinter as tk
from tkinter import ttk

class MainView(tk.Tk):
    def __init__(self, gruppen_manager):
        super().__init__()
        self.title("Kuppelstopper 3.0")
        self.geometry("400x300")
        self.gruppen_manager = gruppen_manager
        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self, text="Wettkampfgruppen", font=("Arial", 14))
        label.pack(pady=10)

        self.listbox = tk.Listbox(self)
        for g in self.gruppen_manager.gruppen:
            self.listbox.insert(tk.END, g.name)
        self.listbox.pack(expand=True, fill=tk.BOTH)

        btn = tk.Button(self, text="Auswertung", command=self.zeige_auswertung)
        btn.pack(pady=10)

    def zeige_auswertung(self):
        from gui.auswertung import AuswertungView
        auswertung = AuswertungView(self)
        auswertung.grab_set()