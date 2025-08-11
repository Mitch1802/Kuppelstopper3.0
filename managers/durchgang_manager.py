import json
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
            # dg.bestzeit_wert = dg.berechne_bestzeit()
            pass
            # TODO Übertrage Bestzeit und Bestezeit inkl. Fehler
    
    def uebernehme_angemeldete_gruppen(self, gruppen):
        """Übernehme alle angemeldeten Gruppen """
        self.gruppen = gruppen
        self.Bewerb = []
        self.DGNumbers = []

    def lade_grunddurchgang(self):
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
            durchgang = Durchgang(dg, self.TypGD, gruppen_name)
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
            data_return.append(gefiltert)

        return data_return

    def sort_tbl_rang_daten(self, data):
        """Sortiert Daten für Platzierung"""
        data.sort(key=lambda x: int(x[11]))
        return data