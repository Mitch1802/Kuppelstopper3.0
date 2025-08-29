import json, os, random
from models import Gruppe
from paths import ANMELDUNG_JSON

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

    def export_gruppen(self, pfad=ANMELDUNG_JSON):
        """Speichert die Gruppenliste als JSON."""
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump([vars(g) for g in self.gruppen], f, indent=2, ensure_ascii=False)

    def gruppe_hinzufuegen(self, gruppe: Gruppe):
        """Fügt eine Gruppe zur Liste hinzu."""
        self.gruppen.append(gruppe)
    
    def testgruppen_hinzufuegen(self, event, anzahl: int, damenAnzahl: int):
        """Fügt eine Gruppe zur Liste hinzu."""

        if not anzahl.isdigit():
            anzahl = 0
        
        if not damenAnzahl.isdigit():
            damenAnzahl = 0

        
        if len(self.gruppen) > 0:
            self.gruppen = []
        reihenfolge = []
        damenReihenfolge = []
        
        for i in range(int(anzahl)):
            rh = random.randint(1,int(anzahl))
            while rh in reihenfolge:
                rh = random.randint(1,int(anzahl))
            reihenfolge.append(rh)

            dwrh = random.randint(1,int(anzahl))
            while dwrh in damenReihenfolge:
                dwrh = random.randint(1,int(anzahl))
            damenReihenfolge.append(dwrh)

            gruppe = Gruppe('Gruppe' + str(i + 1), 'NEIN', str(rh))
            if dwrh <= int(damenAnzahl):
                gruppe = Gruppe('Gruppe' + str(i + 1), 'JA', str(rh))
            self.gruppen.append(gruppe)

    def gruppe_aendern(self, gruppe: Gruppe):
        """Ändert eine angemeldetete Gruppe"""
        for grp in self.gruppen:
            if grp.gruppenname == gruppe[0]:
                if gruppe[1] == 'JA': grp.damenwertung = 'NEIN'
                elif gruppe[1] == 'NEIN': grp.damenwertung = 'JA'

    def gruppe_loeschen(self, gruppe: Gruppe):
        """Löscht eine angemeldetete Gruppe"""
        for grp in self.gruppen:
            if grp.gruppenname == gruppe[0]:
                self.gruppen.remove(grp)

    def get_gruppen(self):
        """Gibt die Liste der angemeldeteten Gruppen zurück für Tabelleneinträge"""
        return [grp.to_list() + ['X'] for grp in self.gruppen]

    def gruppen_uebernehmen(self):
        """Gibt die Liste der angemeldeteten Gruppen zurück"""
        return [grp.to_list() for grp in self.gruppen]
