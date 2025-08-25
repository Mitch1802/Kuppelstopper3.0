import json, random
from models import Durchgang

class DurchgangManager:
    """Verwaltet Durchgänge und Bestzeiten."""
    def __init__(self):
        self.Gruppen = []
        self.Bewerb = []

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
            if dg[3] != '00:00:00' and dg[5] == '00:00:00':
                dg[7] = dg[3]
                dg[8] = int(dg[4])
                dg[9] = self._addiereFehlerZurZeit(dg[3], dg[4])
            elif dg[3] != '00:00:00' and dg[5] != '00:00:00':
                zeit1_inkl_fehler = self._addiereFehlerZurZeit(dg[3], int(dg[4]))
                zeit2_inkl_fehler = self._addiereFehlerZurZeit(dg[5], int(dg[6]))

                zeit1_inkl_fehler_milisekunden = self._berechne_milisekunden(zeit1_inkl_fehler)
                zeit2_inkl_fehler_milisekunden = self._berechne_milisekunden(zeit2_inkl_fehler)

                if zeit1_inkl_fehler_milisekunden < zeit2_inkl_fehler_milisekunden:
                    dg[7] = dg[3]
                    dg[8] = int(dg[4])
                    dg[9] = zeit1_inkl_fehler
                elif zeit1_inkl_fehler_milisekunden >= zeit2_inkl_fehler_milisekunden:
                    dg[7] = dg[5]
                    dg[8] = int(dg[6])
                    dg[9] = zeit2_inkl_fehler
            else:
                dg[7] = '00:00:00'
                dg[8] = 0
                dg[9] = '00:00:00'
    
    def uebernehme_angemeldete_gruppen(self, gruppen):
        """Übernehme alle angemeldeten Gruppen """
        self.Gruppen = gruppen
        self.Bewerb = []

    def lade_grunddurchgang(self, testzeiten: bool):
        """Lade Gruppen für Grunddruchgang"""
        self.Gruppen.sort(key=lambda x: int(x[2]))
        anzahl_gruppen = len(self.Gruppen)
        ko16 = anzahl_gruppen >= 16
        ko8 = anzahl_gruppen >= 8
        ko4 = anzahl_gruppen >= 4

        dg = 1
        count = 0
        for grp in self.Gruppen:
            gruppen_name = grp[0]
            durchgang = Durchgang(dg, self.TypGD, gruppen_name, testzeit=testzeiten)
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

        durchgang = Durchgang(dg, self.TypKF, '', hinweis='KO4_3')
        durchgang = durchgang.to_list()
        self.Bewerb.append(durchgang)

        durchgang = Durchgang(dg, self.TypKF, '', hinweis='KO4_4')
        durchgang = durchgang.to_list()
        self.Bewerb.append(durchgang)
                
        dg += 1

        durchgang = Durchgang(dg, self.TypF, '', hinweis='KO4_1')
        durchgang = durchgang.to_list()
        self.Bewerb.append(durchgang)

        durchgang = Durchgang(dg, self.TypF, '', hinweis='KO4_2')
        durchgang = durchgang.to_list()
        self.Bewerb.append(durchgang)

        # TODO Damenwertung

    def filter_bewerb(self, modus):
        """Filtert alle Duchgänge nach dem aktuellen Modus, zB KO1-16"""
        if modus == self.TypKF or modus == self.TypF:
            daten_gefiltert = [item for item in self.Bewerb if item[1] == self.TypKF or item[1] == self.TypF]
        else:
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
        """Setzt Platzierungen je Modus.
        - Normale Modi: 1..n
        - TypKF (kleines Finale): nur 3 & 4
        - TypF  (Finale): nur 1 & 2
        """
       # Welche Modi sind in diesem Lauf zu berücksichtigen?
        if modus in (self.TypKF, self.TypF):
            involved = (self.TypKF, self.TypF)   # gemeinsam anzeigen
        else:
            involved = (modus,)

        # Platzierungen in den betroffenen Modi zunächst löschen
        for item in self.Bewerb:
            if item[1] in involved:
                item[11] = 0

        # Nur Einträge mit gültiger Bestzeit
        daten = [it for it in self.Bewerb if it[1] in involved and it[9] != '00:00:00']

        if modus in (self.TypKF, self.TypF):
            # Finale und kleines Finale getrennt werten...
            finals = [it for it in daten if it[1] == self.TypF]
            small  = [it for it in daten if it[1] == self.TypKF]

            finals_sorted = sorted(finals, key=self._time_key)  # schnellste zuerst
            small_sorted  = sorted(small,  key=self._time_key)

            # ...aber gemeinsam zurückgeben
            if len(finals_sorted) >= 1: finals_sorted[0][11] = 1
            if len(finals_sorted) >= 2: finals_sorted[1][11] = 2
            if len(small_sorted)  >= 1: small_sorted[0][11]  = 3
            if len(small_sorted)  >= 2: small_sorted[1][11]  = 4

            combined = finals_sorted + small_sorted
            # Für die Rang-Tabelle sortiert nach Platz (1,2,3,4); Fallback: Zeit
            return sorted(
                combined,
                key=lambda it: (0 if it[11] else 99, it[11]) + self._time_key(it)
            )

        # Alle anderen Modi: 1..n
        daten_sortiert = sorted(daten, key=self._time_key)
        for idx, item in enumerate(daten_sortiert, start=1):
            item[11] = idx
        return daten_sortiert
    
    def generiere_zufallsszeit(self, max_minutes: int = 1) -> str:
        """Gibt eine zufällige Zeit im Format 'minute:sekunde:millisekunde' zurück."""
        ms_total = random.randint(0, max_minutes * 60 * 1000 - 1)
        minute = ms_total // 60000
        sekunde = (ms_total % 60000) // 1000
        millisekunde = round((ms_total % 1000) / 10) 
        if millisekunde == 100:
            millisekunde = 99
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
        for row in self.Bewerb:
            if row[0] == int(data[0]) and row[2] == data[1]:
                row[3] = data[2]
                row[4] = data[3]
                row[5] = data[4]
                row[6] = data[5]

    def check_beide_zeiten(self, durchgang):
        zeiten_a = 0
        zeiten_b = 0
        count = 0
        for dg in self.Bewerb:
            if dg[0] == int(durchgang):
                if count == 0:
                    if dg[3] != '00:00:00': zeiten_a += 1
                    if dg[5] != '00:00:00': zeiten_a += 1
                    count += 1
                elif count == 1:
                    if dg[3] != '00:00:00': zeiten_b += 1
                    if dg[5] != '00:00:00': zeiten_b += 1
        
        return [zeiten_a, zeiten_b]

    def zeiten_an_bewerb_uebergeben(self, durchgang, gruppe_a, zeit_a, fehler_a, gruppe_b, zeit_b, fehler_b):
        aktuelle_zeit_a = 0
        aktuelle_zeit_b = 0

        for dg in self.Bewerb:
            if gruppe_a != '':
                if dg[0] == durchgang and dg[2] == gruppe_a:
                    if dg[3] == '00:00:00' and dg[5] == '00:00:00':
                        dg[3] = zeit_a
                        dg[4] = fehler_a
                        aktuelle_zeit_a = 1
                    elif dg[3] != '00:00:00' and dg[5] == '00:00:00':
                        dg[5] = zeit_a
                        dg[6] = fehler_a
                        aktuelle_zeit_a = 2
            else:
                aktuelle_zeit_a = 0
            
            if gruppe_b != '':
                if dg[0] == durchgang and dg[2] == gruppe_b:
                    if dg[3] == '00:00:00' and dg[5] == '00:00:00':
                        dg[3] = zeit_b
                        dg[4] = fehler_b
                        aktuelle_zeit_b = 1
                    elif dg[3] != '00:00:00' and dg[5] == '00:00:00':
                        dg[5] = zeit_b
                        dg[6] = fehler_b
                        aktuelle_zeit_b = 2
            else:
                aktuelle_zeit_b = 0
        if gruppe_a != '' and gruppe_b != '':
            if aktuelle_zeit_a != aktuelle_zeit_b:
                return 0
            else:
                return aktuelle_zeit_a
        else:
            return max(aktuelle_zeit_a, aktuelle_zeit_b)

    def wandle_durchgang_in_modus(self, durchgang):
        for dg in self.Bewerb:
            if dg[0] == durchgang:
                return dg[1]

    def get_max_dgnumber(self):
        length = len(self.Bewerb)
        max = self.Bewerb[length-1]
        max_dg = max[0]
        return max_dg

    def top_gruppen_naechste_runde(self):
        # (Optional) Sicherstellen, dass Platzierungen frisch sind:
        for m in [self.TypGD, self.TypKO16, self.TypKO8, self.TypKO4]:
            self.sort_tbl_rang_daten(m)

        # 1) Alle Ziel-Slots leeren (KO16/KO8/KO4/KF/F)
        for dg in self.Bewerb:
            if dg[1] in (self.TypKO16, self.TypKO8, self.TypKO4, self.TypKF, self.TypF):
                dg[2] = ''  # Gruppe leer

        # 2) Aus allen gefüllten Läufen die Slots wieder befüllen
        for row in self.Bewerb:
            gruppe = row[2]
            bestzeit = row[9]
            platzierung = row[11]
            if bestzeit != '00:00:00' and platzierung:
                prefix = row[1].split('_')[1]  # 'GD', 'KO16', 'KO8', 'KO4'
                ziel_hinweis = f"{prefix}_{platzierung}"
                for ziel in self.Bewerb:
                    if ziel[10] == ziel_hinweis:
                        ziel[2] = gruppe

    def lade_alle_Tabellen_modus(self):
        data = []

        for dg in self.Bewerb:
            if dg[1] not in data:
                data.append(dg[1])
        
        return data

    def zeit_1_und_2_loeschen(self, durchgang):
        for dg in self.Bewerb:
            if dg[0] == int(durchgang):
                dg[3] = '00:00:00'
                dg[4] = 0
                dg[5] = '00:00:00'
                dg[6] = 0

    def zeit_2_loeschen(self, durchgang):
        for dg in self.Bewerb:
            if dg[0] == int(durchgang):
                dg[5] = '00:00:00'
                dg[6] = 0
