import json

class SetupManager:
    """Verwaltet Durchgänge und Bestzeiten."""
    def __init__(self):
        pass

    def lade_setup(self, pfad):
        """Lädt Einstellungen aus einer Datei"""
        with open(pfad, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def setup_speichern(self, pfad, daten):
        pass
