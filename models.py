import random

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
    
    def to_list(self):
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
    def __init__(self, durchgang, typ, wettkampfgruppe, zeit1='00:00:00', fehler1=0, zeit2='00:00:00', fehler2=0, bestzeit='00:00:00', fehlerbest=0, bestzeitinklfehler='00:00:00', hinweis='', platzierung=0, testzeit=False):

        self.dg = durchgang
        self.typ = typ
        self.wettkampfgruppe = wettkampfgruppe
        if testzeit:   
            self.zeit1 = self._generiere_zufallsszeit()
            self.fehler1 = random.choice(range(0, 21, 5))
            self.zeit2 = self._generiere_zufallsszeit()
            self.fehler2 = random.choice(range(0, 21, 5))
        else:
            self.zeit1 = zeit1
            self.fehler1 = fehler1
            self.zeit2 = zeit2
            self.fehler2 = fehler2
        self.bestzeit = bestzeit
        self.fehlerbest = fehlerbest
        self.bestzeitinklfehler = bestzeitinklfehler
        self.hinweis = hinweis
        self.platzierung = platzierung
    
    def to_list(self):
        return [
            self.dg,
            self.typ,
            self.wettkampfgruppe,
            self.zeit1,
            self.fehler1,
            self.zeit2,
            self.fehler2,
            self.bestzeit,
            self.fehlerbest,
            self.bestzeitinklfehler,
            self.hinweis,
            self.platzierung
        ]

    # def berechne_bestzeit(self):
    #     """
    #     Gibt die schnellere der beiden Zeiten zurück (ohne Fehler).

    #     Returns:
    #         str: schnellere Zeit oder die einzige vorhandene.
    #     """
    #     if self.zeit1 != '' and self.zeit2 != '':
    #         zeit1_inkl_fehler = self._addiereFehlerZurZeit(self.zeit1, self.fehler1)
    #         zeit2_inkl_fehler = self._addiereFehlerZurZeit(self.zeit2, self.fehler2)

    #         zeit1_inkl_fehler_milisekunden = self._berechne_milisekunden(zeit1_inkl_fehler)
    #         zeit2_inkl_fehler_milisekunden = self._berechne_milisekunden(zeit2_inkl_fehler)

    #         if zeit1_inkl_fehler_milisekunden < zeit2_inkl_fehler_milisekunden:
    #             self.bestzeit = self.zeit1
    #             self.fehlerbest = self.fehler1
    #             self.bestzeitinklfehler = self._format_millisekunden(zeit1_inkl_fehler_milisekunden)
    #         elif zeit1_inkl_fehler_milisekunden >= zeit2_inkl_fehler_milisekunden:
    #             self.bestzeit = self.zeit2
    #             self.fehlerbest = self.fehler2
    #             self.bestzeitinklfehler = self._format_millisekunden(zeit2_inkl_fehler_milisekunden)
    
    # def _addiereFehlerZurZeit(self, zeit, fehler):
    #     """Addiert die Fehler zur Zeit"""
    #     t = zeit.split(':')
    #     t_minute = int(t[0])
    #     t_sekunden = int(t[1])
    #     t_milisekunden = int(t[2])
    #     t_fehler = int(fehler)
    #     t_sekunden = t_sekunden + t_fehler

    #     if t_sekunden > 59:
    #         t_sekunden = t_sekunden - 60
    #         t_minute = t_minute + 1  

    #     if t_minute < 10:
    #         t_minute = '0' + str(t_minute)
    #     else:
    #         t_minute = str(t_minute)

    #     if t_sekunden < 10:
    #         t_sekunden = '0' + str(t_sekunden)
    #     else:
    #         t_sekunden = str(t_sekunden)
        
    #     if t_milisekunden < 10:
    #         t_milisekunden = '0' + str(t_milisekunden)
    #     else:
    #         t_milisekunden = str(t_milisekunden)

    #     zeit_neu = t_minute + ':' + t_sekunden + ':' + t_milisekunden
    #     return zeit_neu
    
    # def _berechne_milisekunden(self, zeit):
    #     """Konvertiert 'minute:sekunde:millisekunde' in Millisekunden"""
    #     t = zeit.split(':')
    #     t_minute = int(t[0])
    #     t_sekunden = int(t[1])
    #     t_milisekunden = int(t[2])
    #     tf = (((t_minute * 60) + t_sekunden) * 100) + t_milisekunden

    #     return tf
    
    # def _format_millisekunden(ms: int) -> str:
    #     """Formatiert Millisekunden in 'minute:sekunde:millisekunde'"""
    #     t_minute = ms // 60000
    #     t_sekunde = (ms % 60000) // 1000
    #     t_millisekunde = ms % 1000

    #     return f"{t_minute}:{t_sekunde:02}:{t_millisekunde:02}"
    
    def _generiere_zufallsszeit(self, max_minutes: int = 1) -> str:
        """Gibt eine zufällige Zeit im Format 'minute:sekunde:millisekunde' zurück."""
        ms_total = random.randint(0, max_minutes * 60 * 1000 - 1)
        minute = ms_total // 60000
        sekunde = (ms_total % 60000) // 1000
        millisekunde = round((ms_total % 1000) / 10) 
        if millisekunde == 100:
            millisekunde = 99
        return f"{minute:02}:{sekunde:02}:{millisekunde:02}"
