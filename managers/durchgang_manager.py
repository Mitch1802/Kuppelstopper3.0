import json
from models import Durchgang

class DurchgangManager:
    """Verwaltet Durchgänge und Bestzeiten."""
    def __init__(self):
        self.gruppen = []
        self.bewerb = []
        self.dgnumbers = []

    def lade_bewerb(self, pfad):
        """Lädt Durchgänge aus einer Datei im Bewerbsformat."""
        with open(pfad, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.bewerb = [Durchgang(**dg) for dg in data['Bewerb']]

    def berechne_bestzeiten(self):
        """Berechnet für jeden Durchgang die beste Zeit."""
        for dg in self.bewerb:
            dg.bestzeit_wert = dg.bestzeit()
    
    def uebernehme_angemeldete_gruppen(self, gruppen):
        """Übernheme alle angemeldeten Gruppen """
        self.gruppen = gruppen

    def lade_grunddurchgang(self):
        """Lade Gruppen für Grunddruchgang"""
        self.gruppen.sort(key=lambda x: int(x[2]))
        print('Anzahl Gruppen: ', len(self.gruppen))
        anzahl_gruppen = len(self.gruppen)
        ko16 = anzahl_gruppen >= 16
        ko8 = anzahl_gruppen >= 8
        ko4 = anzahl_gruppen >= 4

        dg = 1
        for grp in self.gruppen:
            dg_nr = dg
            if dg % 2: dg += 1

            # TODO Erstelle GD Array

        if ko16:
            for i in range(16):
                # TODO Erstelle KO16 Array
                pass
        
        if ko8:
            for i in range(8):
                # TODO Erstelle KO8 Array
                pass
        
        if ko4:
            for i in range(4):
                # TODO Erstelle KO4 Array
                pass
        
        for i in range(4):
                # TODO Erstelle Finale Array
                pass

        data_neu = self.filter_bewerb("gd")
        return data_neu

    def filter_bewerb(self, modus):
        """Filtert alle Duchgänge nach dem aktuellen Modus, zB KO1-16"""
        test = self.bewerb
        pass





    PL3ECC8PRK