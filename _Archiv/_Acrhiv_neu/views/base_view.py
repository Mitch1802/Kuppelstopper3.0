import tkinter as tk

class BaseView:
    def __init__(self, controller):
        self.controller = controller
        # Hauptfenster erzeugen
        self.root = tk.Tk()
        self.root.title(self.controller.settings.get('window_title', 'Kuppelcup'))
        # Hier wird die konkrete UI gebaut
        self._setup_ui()

    def _setup_ui(self):
        """Muss in jeder Subklasse überschrieben werden"""
        raise NotImplementedError("Subclasses must implement _setup_ui()")

    def run(self):
        self.root.mainloop()