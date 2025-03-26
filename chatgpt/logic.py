# logic.py
from datetime import datetime
import random


class LogicHandler:
    def __init__(self, data, config):
        self.data = data
        self.config = config

    def validiere_gruppen(self):
        for gruppe in self.data.gruppen:
            if not gruppe['reihenfolge'].isdigit():
                return False
        return True

    def erzeuge_durchgaenge(self):
        self.data.durchgaenge.clear()

        mixed = [g for g in self.data.gruppen if not g['damenwertung']]
        damen = [g for g in self.data.gruppen if g['damenwertung']]

        mixed = sorted(mixed, key=lambda g: int(g['reihenfolge']))
        damen = sorted(damen, key=lambda g: int(g['reihenfolge']))

        for i, gruppe in enumerate(mixed):
            dg = self._create_dg(gruppe, i+1, typ="GD")
            self.data.durchgaenge.append(dg)

        for i, gruppe in enumerate(damen):
            dg = self._create_dg(gruppe, i+1, typ="DW")
            self.data.durchgaenge.append(dg)

    def _create_dg(self, gruppe, nummer, typ="GD"):
        return {
            "wettkampfgruppe": gruppe["gruppenname"],
            "typ": typ,
            "dg": nummer,
            "zeit1": "",
            "zeit2": "",
            "fehler1": 0,
            "fehler2": 0,
            "bestzeit": "",
            "fehlerbest": 0,
            "bestzeitinklfehler": "",
            "platzierung": 0,
            "row": nummer,
            "column": 1,
        }

    def berechne_bestzeiten(self):
        for dg in self.data.durchgaenge:
            z1 = self._addiere_fehler(dg['zeit1'], dg['fehler1'])
            z2 = self._addiere_fehler(dg['zeit2'], dg['fehler2'])
            dg['bestzeitinklfehler'] = min(z1, z2) if z1 and z2 else z1 or z2

    def _addiere_fehler(self, zeit, fehler):
        try:
            dt = datetime.strptime(zeit, '%M:%S:%f')
            sekunden = dt.minute * 60 + dt.second + fehler
            return f"{sekunden // 60:02}:{sekunden % 60:02}:{dt.microsecond // 10000:02}"
        except:
            return ""
