import json, random
from models import Durchgang

class DurchgangManager:
    """Verwaltet Durchgänge und Bestzeiten."""
    def __init__(self):
        self.Gruppen = []
        self.Bewerb = []
        self.DGNumbers = []

        self.TypGD = '1_GD'
        self.TypKO16 = '2_KO16'
        self.TypKO8 = '3_KO8'
        self.TypKO4 = '4_KO4'
        self.TypKF = '5_KF'
        self.TypF = '6_F'

    def lade_bewerb(self, pfad):
        """Lädt Durchgänge aus einer Datei im Bewerbsformat."""
        with open(pfad, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.Bewerb = [Durchgang(**dg) for dg in data['Bewerb']]

    def berechne_bestzeiten(self):
        """Berechnet für jeden Durchgang die beste Zeit."""
        for dg in self.Bewerb:
            if dg[3] != '' and dg[5] == '':
                dg[7] = dg[3]
                dg[8] = dg[4]
                dg[9] = self._addiereFehlerZurZeit(dg[3], dg[4])
            elif dg[3] != '' and dg[5] != '':
                zeit1_inkl_fehler = self._addiereFehlerZurZeit(dg[3], dg[4])
                zeit2_inkl_fehler = self._addiereFehlerZurZeit(dg[5], dg[6])

                zeit1_inkl_fehler_milisekunden = self._berechne_milisekunden(zeit1_inkl_fehler)
                zeit2_inkl_fehler_milisekunden = self._berechne_milisekunden(zeit2_inkl_fehler)

                if zeit1_inkl_fehler_milisekunden < zeit2_inkl_fehler_milisekunden:
                    dg[7] = dg[3]
                    dg[8] = dg[4]
                    dg[9] = zeit1_inkl_fehler
                elif zeit1_inkl_fehler_milisekunden >= zeit2_inkl_fehler_milisekunden:
                    dg[7] = dg[5]
                    dg[8] = dg[6]
                    dg[9] = zeit2_inkl_fehler
    
    def uebernehme_angemeldete_gruppen(self, gruppen):
        """Übernehme alle angemeldeten Gruppen """
        self.gruppen = gruppen
        self.Bewerb = []
        self.DGNumbers = []

    def lade_grunddurchgang(self, test: bool):
        """Lade Gruppen für Grunddruchgang"""
        self.gruppen.sort(key=lambda x: int(x[2]))
        anzahl_gruppen = len(self.gruppen)
        ko16 = anzahl_gruppen >= 16
        ko8 = anzahl_gruppen >= 8
        ko4 = anzahl_gruppen >= 4

        dg = 1
        count = 0
        for grp in self.gruppen:
            gruppen_name = grp[0]
            durchgang = Durchgang(dg, self.TypGD, gruppen_name, testzeit=test)
            durchgang = durchgang.to_list()
            self.Bewerb.append(durchgang)

            if count == 0: 
                count += 1
            elif count > 0:
                count = 0
                dg += 1
        
        dg += 1

        if ko16:
            count = 0
            hinweis_a = 1
            hinweis_b = 16
            for i in range(16):
                hinweis = ''
                
                if count == 0: 
                    hinweis = 'GD_' + str(hinweis_a)
                    durchgang = Durchgang(dg, self.TypKO16, '', hinweis=hinweis)
                    count += 1
                    hinweis_a += 1
                elif count > 0:
                    hinweis = 'GD_' + str(hinweis_b)
                    durchgang = Durchgang(dg, self.TypKO16, '', hinweis=hinweis)
                    count = 0
                    dg += 1
                    hinweis_b -= 1
                
                durchgang = durchgang.to_list()
                self.Bewerb.append(durchgang)
        
        if ko8:
            count = 0
            hinweis_a = 1
            hinweis_b = 8
            for i in range(8):
                hinweis = ''
                
                if count == 0: 
                    if ko16: hinweis = 'KO16_' + str(hinweis_a)
                    else:  hinweis = 'GD_' + str(hinweis_a)
                    durchgang = Durchgang(dg, self.TypKO8, '', hinweis=hinweis)
                    count += 1
                    hinweis_a += 1
                elif count > 0:
                    if ko16: hinweis = 'KO16_' + str(hinweis_b)
                    else:  hinweis = 'GD_' + str(hinweis_b)
                    durchgang = Durchgang(dg, self.TypKO8, '', hinweis=hinweis)
                    count = 0
                    dg += 1
                    hinweis_b -= 1
                
                durchgang = durchgang.to_list()
                self.Bewerb.append(durchgang)
        
        if ko4:
            count = 0
            hinweis_a = 1
            hinweis_b = 4
            for i in range(4):
                hinweis = ''
                
                if count == 0: 
                    if ko16: hinweis = 'KO16_' + str(hinweis_a)
                    elif ko8: hinweis = 'KO8_' + str(hinweis_a)
                    else: hinweis = 'GD_' + str(hinweis_a)
                    durchgang = Durchgang(dg, self.TypKO4, '', hinweis=hinweis)
                    count += 1
                    hinweis_a += 1
                elif count > 0:
                    if ko16: hinweis = 'KO16_' + str(hinweis_b)
                    elif ko8: hinweis = 'KO8_' + str(hinweis_b)
                    else: hinweis = 'GD_' + str(hinweis_b)
                    durchgang = Durchgang(dg, self.TypKO4, '', hinweis=hinweis)
                    count = 0
                    dg += 1
                    hinweis_b -= 1
                
                durchgang = durchgang.to_list()
                self.Bewerb.append(durchgang)

        durchgang = Durchgang(dg, self.TypKF, '')
        durchgang = durchgang.to_list()
        self.Bewerb.append(durchgang)

        durchgang = Durchgang(dg, self.TypKF, '')
        durchgang = durchgang.to_list()
        self.Bewerb.append(durchgang)
                
        dg += 1

        durchgang = Durchgang(dg, self.TypF, '')
        durchgang = durchgang.to_list()
        self.Bewerb.append(durchgang)

        durchgang = Durchgang(dg, self.TypF, '')
        durchgang = durchgang.to_list()
        self.Bewerb.append(durchgang)

        # TODO Damenwertung

        # TODO Befülle DGNumbers Arary mit Nummern der Durchgänge

        if test:
            self.berechne_bestzeiten()

        data_neu = self.filter_bewerb(self.TypGD)
        return data_neu

    def filter_bewerb(self, modus):
        """Filtert alle Duchgänge nach dem aktuellen Modus, zB KO1-16"""
        daten_gefiltert = [item for item in self.Bewerb if item[1] == modus]
        return daten_gefiltert

    def filter_tbl_bewerb_daten(self, data):
        """Vorbereitung für Bewerb Tabelle"""
        data_return = []
        index_zu_entfernen = {1,7,8,10,11}  
        for dg in data:
            gefiltert = [wert for i, wert in enumerate(dg) if i not in index_zu_entfernen]
            data_return.append(gefiltert)

        return data_return
    
    def filter_tbl_rang_daten(self, data):
        """Vorbereitung für Rang Tabelle"""
        data_return = []
        index_zu_entfernen = {0,1,3,4,5,6,7,8,10}  
        for dg in data:
            gefiltert = [wert for i, wert in enumerate(dg) if i not in index_zu_entfernen]
            platzierung = gefiltert[2]
            gruppe = gefiltert[0]
            zeit = gefiltert[1]
            reihenfolge_neu = [platzierung, gruppe, zeit]
            data_return.append(reihenfolge_neu)
    
        return data_return

    def sort_tbl_rang_daten(self, modus):
        """Sortiert Daten für Platzierung"""
        daten_gefiltert = [item for item in self.Bewerb if item[1] == modus]
        daten_sortiert_nach_zeit = sorted(daten_gefiltert, key=self._time_key)
        platzierung_neu = 1

        for index, item in enumerate(daten_sortiert_nach_zeit):
                platzierung_neu = index + 1
                item[11] = platzierung_neu

        return daten_sortiert_nach_zeit
    
    def generiere_zufallsszeit(self, max_minutes: int = 1) -> str:
        """Gibt eine zufällige Zeit im Format 'minute:sekunde:millisekunde' zurück."""
        ms_total = random.randint(0, max_minutes * 60 * 1000 - 1)
        minute = ms_total // 60000
        sekunde = (ms_total % 60000) // 1000
        millisekunde = ms_total % 1000
        return f"{minute:02}:{sekunde:02}:{millisekunde:02}"
    
    def _addiereFehlerZurZeit(self, zeit, fehler):
        """Addiert die Fehler zur Zeit"""
        t = zeit.split(':')
        t_minute = int(t[0])
        t_sekunden = int(t[1])
        t_milisekunden = int(t[2])
        t_fehler = int(fehler)
        t_sekunden = t_sekunden + t_fehler

        if t_sekunden > 59:
            t_sekunden = t_sekunden - 60
            t_minute = t_minute + 1  

        if t_minute < 10:
            t_minute = '0' + str(t_minute)
        else:
            t_minute = str(t_minute)

        if t_sekunden < 10:
            t_sekunden = '0' + str(t_sekunden)
        else:
            t_sekunden = str(t_sekunden)
        
        if t_milisekunden < 10:
            t_milisekunden = '0' + str(t_milisekunden)
        else:
            t_milisekunden = str(t_milisekunden)

        zeit_neu = t_minute + ':' + t_sekunden + ':' + t_milisekunden
        return zeit_neu
    
    def _berechne_milisekunden(self, zeit):
        """Konvertiert 'minute:sekunde:millisekunde' in Millisekunden"""
        t = zeit.split(':')
        t_minute = int(t[0])
        t_sekunden = int(t[1])
        t_milisekunden = int(t[2])
        tf = (((t_minute * 60) + t_sekunden) * 100) + t_milisekunden

        return tf
    
    def _format_millisekunden(self, ms):
        """Formatiert Millisekunden in 'minute:sekunde:millisekunde'"""
        t_minute = ms // 60000
        t_sekunde = (ms % 60000) // 1000
        t_millisekunde = ms % 1000

        return f"{t_minute}:{t_sekunde:02}:{t_millisekunde:02}"
    
    def _time_key(self, item):
        # Zeitstring aus Index 9 holen
        minute, sekunde, millisekunde = map(int, item[9].split(":"))
        return (minute, sekunde, millisekunde)

    def lade_gruppen_von_durchgang(self, durchgangsnummer):
        gruppe_a = ''
        gruppe_b = ''
        for row in self.Bewerb:
            if row[0] == durchgangsnummer:
                if gruppe_a == '': gruppe_a = row[2]
                else: gruppe_b = row[2]
        
        return [gruppe_a, gruppe_b]

    def change_werte(self, data):
        pass

    def zeiten_an_bewerb_uebergeben(self, durchgang, zeit_a, fehler_a, zeit_b, fehler_b):
        pass

    def wandle_durchgang_in_modus(self, durchgang):
        for dg in self.Bewerb:
            if dg[0] == durchgang:
                return dg[1]

    def get_max_dgnumber(self):
        length = len(self.Bewerb)
        max = self.Bewerb[length-1]
        max_dg = max[0]
        return max_dg

