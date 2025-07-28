import json, os
from models import Gruppe, Durchgang

class GruppenManager:
    def __init__(self):
        self.gruppen = []

    def lade_gruppen(self, pfad):
        if os.path.exists(pfad):
            with open(pfad, 'r') as f:
                data = json.load(f)
            self.gruppen = [Gruppe(**g) for g in data]
        else:
            self.gruppen = []

    def speichere_gruppen(self, pfad):
        with open(pfad, 'w') as f:
            json.dump([vars(g) for g in self.gruppen], f)

class DurchgangManager:
    def __init__(self):
        self.durchgaenge = []

    def lade_durchgaenge(self, pfad):
        with open(pfad, 'r') as f:
            data = json.load(f)
        self.durchgaenge = [Durchgang(**dg) for dg in data]

    def berechne_bestzeiten(self):
        for dg in self.durchgaenge:
            dg.bestzeit_wert = dg.bestzeit()