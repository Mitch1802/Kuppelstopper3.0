class Gruppe:
    """
    Repräsentiert eine Feuerwehrgruppe für den Bewerb.

    Attribute:
        gruppenname (str): Name der Gruppe.
        damenwertung (bool): True, wenn die Gruppe in der Damenwertung startet.
        reihenfolge (int): Startreihenfolge im Bewerb.
    """
    def __init__(self, gruppenname, damenwertung, reihenfolge):
        self.gruppenname = gruppenname
        self.damenwertung = damenwertung
        self.reihenfolge = reihenfolge
    
    def to_dict(self):
        return [
            self.gruppenname,
            self.damenwertung,
            self.reihenfolge
        ]


class Durchgang:
    """
    Repräsentiert einen einzelnen Durchgang einer Wettkampfgruppe.

    Attribute:
        typ (str): Typ des Durchgangs (z.B. 'Bronze', 'Silber').
        row, column (int): Positionierung im Raster oder Plan.
        wettkampfgruppe (str): Gruppenname oder ID.
        zeit1, zeit2 (str): Zwei Zeitversuche (z.B. bei zwei Läufen).
        fehler1, fehler2 (int): Fehlerpunkte für Zeit1 und Zeit2.
        durchgang (int): Durchgangsnummer.
        hinweis (str): Freitextkommentar.
        platzierung (int): Platzierung nach diesem Lauf.
        bestzeit (str): Schnellste Zeit als String.
        fehlerbest (int): Fehler der besten Zeit.
        bestzeitinklfehler (str): Beste Zeit inkl. Fehler.
    """
    def __init__(self, typ, row, column, wettkampfgruppe, zeit1='', fehler1=0, zeit2='', fehler2=0, durchgang=0, hinweis='', platzierung=0):
        self.typ = typ
        self.row = row
        self.column = column
        self.dg = durchgang
        self.wettkampfgruppe = wettkampfgruppe
        self.zeit1 = zeit1
        self.fehler1 = fehler1
        self.zeit2 = zeit2
        self.fehler2 = fehler2
        self.bestzeit = ''
        self.fehlerbest = 0
        self.bestzeitinklfehler = ''
        self.hinweis = hinweis
        self.platzierung = platzierung

    def bestzeit(self):
        """
        Gibt die schnellere der beiden Zeiten zurück (ohne Fehler).

        Returns:
            str: schnellere Zeit oder die einzige vorhandene.
        """
        if self.zeit1 and self.zeit2:
            return min(self.zeit1, self.zeit2)
        return self.zeit1 or self.zeit2
