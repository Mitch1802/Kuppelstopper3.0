import json
from models import Durchgang

class DurchgangManager:
    """Verwaltet Durchgänge und Bestzeiten."""
    def __init__(self):
        self.gruppen = []
        self.durchgaenge = []

    def lade_durchgaenge(self, pfad):
        """Lädt Durchgänge aus einer Datei im Bewerbsformat."""
        with open(pfad, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.durchgaenge = [Durchgang(**dg) for dg in data['Bewerb']]

    def berechne_bestzeiten(self):
        """Berechnet für jeden Durchgang die beste Zeit."""
        for dg in self.durchgaenge:
            dg.bestzeit_wert = dg.bestzeit()
    
    def uebernehme_angemeldete_gruppen(self, gruppen):
        """Übernheme alle angemeldeten Gruppen """
        self.gruppen = gruppen

    def lade_grunddurchgang(self):
        """Lade Gruppen für Grunddruchgang"""
        pass