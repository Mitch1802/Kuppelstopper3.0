# gui.py
from customtkinter import *
from tkinter import messagebox
from widgets import IntSpinbox
from data import DataManager
from logic import LogicHandler


class GUIManager:
    def __init__(self, config):
        self.config = config
        self.data = DataManager(config)
        self.logic = LogicHandler(self.data, config)

        set_appearance_mode("light")
        set_default_color_theme(config.theme_file)

        self.root = CTk()
        self.root.title(config.title)

        self._build_ui()
        self.root.mainloop()

    def _build_ui(self):
        self.tab_view = CTkTabview(self.root, anchor="nw", corner_radius=0)
        self.tab_view.pack(expand=True, fill="both", padx=5, pady=5)

        self.tab_anmeldung = self.tab_view.add("Anmeldung")
        self.tab_zeit = self.tab_view.add("Zeitnehmung")
        self.tab_einstellungen = self.tab_view.add("Einstellungen")

        self._build_tab_anmeldung()
        self._build_tab_zeit()
        self._build_tab_einstellungen()

    def _build_tab_anmeldung(self):
        self.entry_gruppe = CTkEntry(self.tab_anmeldung, placeholder_text="Gruppenname")
        self.entry_gruppe.pack(padx=10, pady=10, fill="x")

        self.list_frame = CTkScrollableFrame(self.tab_anmeldung)
        self.list_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.button_uebernehmen = CTkButton(
            self.tab_anmeldung, text="Gruppen übernehmen", command=self.uebernehme_gruppen
        )
        self.button_uebernehmen.pack(pady=10)

        self.zeichne_gruppenliste()

    def zeichne_gruppenliste(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.data.gruppen:
            CTkLabel(self.list_frame, text="Keine Gruppen angemeldet").pack()
        else:
            for i, gruppe in enumerate(self.data.gruppen):
                CTkLabel(self.list_frame, text=f"{gruppe['gruppenname']} ({'Damen' if gruppe['damenwertung'] else 'Allg.'})").pack(anchor="w", pady=2, padx=5)

    def uebernehme_gruppen(self):
        valid = self.logic.validiere_gruppen()
        if valid:
            self.logic.erzeuge_durchgaenge()
            self.data.speichern()
            self.zeichne_gruppenliste()
            self.tab_view.set("Zeitnehmung")
        else:
            messagebox.showerror("Fehler", "Nicht alle Gruppen haben eine gültige Reihenfolge!")

    def _build_tab_zeit(self):
        self.label_zeit = CTkLabel(self.tab_zeit, text="Zeitnehmung folgt...", font=("Arial", 24))
        self.label_zeit.pack(pady=20)

    def _build_tab_einstellungen(self):
        self.font_label = CTkLabel(self.tab_einstellungen, text="Schriftgröße")
        self.font_label.pack(pady=(20, 5))

        self.font_spinner = IntSpinbox(self.tab_einstellungen)
        self.font_spinner.set(22)
        self.font_spinner.pack(pady=5)
