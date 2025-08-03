import json, os
from models import Gruppe
from config.paths import ANMELDUNG_JSON

class GruppenManager:
    """Verwaltet Gruppen: Hinzufügen, Speichern, Laden."""
    def __init__(self):
        self.gruppen = []

    def lade_gruppen(self, pfad=ANMELDUNG_JSON):
        """Lädt Gruppen aus einer JSON-Datei."""
        if os.path.exists(pfad):
            with open(pfad, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.gruppen = [Gruppe(**g) for g in data]
        else:
            self.gruppen = []

    def gruppe_hinzufuegen(self, gruppe: Gruppe):
        """Fügt eine Gruppe zur Liste hinzu."""
        self.gruppen.append(gruppe)

    def gruppe_loeschen(self, gruppe: Gruppe):
        """Löscht eine angemeldetete Gruppe"""
        # self.gruppen.append(gruppe)
        pass

    def speichere_anmeldung(self, pfad=ANMELDUNG_JSON):
        """Speichert die Gruppenliste als JSON."""
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump([vars(g) for g in self.gruppen], f, indent=2, ensure_ascii=False)

    def get_gruppen(self):
        """Gibt die Liste der angemeldeteten Gruppen zurück"""
        return [g.to_dict() for g in self.gruppen]



