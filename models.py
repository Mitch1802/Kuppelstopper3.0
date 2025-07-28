class Gruppe:
    def __init__(self, gruppenname, reihenfolge, damenwertung):
        self.gruppenname = gruppenname
        self.reihenfolge = reihenfolge
        self.damenwertung = damenwertung

class Durchgang:
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
        if self.zeit1 and self.zeit2:
            return min(self.zeit1, self.zeit2)
        return self.zeit1 or self.zeit2