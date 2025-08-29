import json, os

class SetupManager:
    """Verwaltet Durchgänge und Bestzeiten."""
    def __init__(self):
        pass

    def lade_setup(self, pfad):
        """Lädt Einstellungen aus einer Datei"""
        if os.path.exists(pfad):
            with open(pfad, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        else:
            return []
    
    def setup_speichern(self, pfad, daten):
        with open(pfad, "w") as outfile:
            json.dump(daten, outfile)
