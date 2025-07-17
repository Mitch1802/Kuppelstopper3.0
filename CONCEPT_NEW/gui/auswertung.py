import tkinter as tk

class AuswertungView(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Auswertung")
        self.geometry("300x200")
        label = tk.Label(self, text="Auswertung - Bestzeiten", font=("Arial", 12))
        label.pack(pady=10)
        # Beispielhafte Anzeige, in echt würdest du die Daten aus dem Manager nehmen
        tk.Label(self, text="Gruppe 1: 25.77s").pack()
        tk.Label(self, text="Gruppe 2: 27.22s").pack()