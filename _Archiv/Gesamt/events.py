from tkinter import messagebox
from customtkinter import *
import pygame, random
import utils, gui, config, time_manager

def add_wettkampfgruppe(self, event=None):
    name = self.root.Entry.get()
    if not name:
        messagebox.showerror('Fehlermeldung', 'Bitte einen Namen eingeben!')
        return
    count = sum(1 for i in self.Wettkampfgruppen if i['gruppenname'] == name)
    if count > 0:
        messagebox.showerror('Fehlermeldung', 'Gruppenname bereits vorhanden!')
        return
    if len(self.Wettkampfgruppen) >= 30:
        messagebox.showerror('Fehlermeldung', 'Maximal 30 Gruppen erlaubt!')
        return
    val = {
        'gruppenname': name,
        'reihenfolge': '',
        'damenwertung': False
    }
    self.Wettkampfgruppen.append(val)
    self.root.Entry.delete(0, END)
    gui.zeichne_angemeldete_gruppen(self)
    utils.write_konsole(self, f"{name} wurde hinzugefügt!")

def berechne_bestzeit(self, zeit1, zeit2):
    t1 = zeit1.split(':')
    tf1 = (((int(t1[0]) * 60) + int(t1[1])) * 100) + int(t1[2])
    t2 = zeit2.split(':')
    tf2 = (((int(t2[0]) * 60) + int(t2[1])) * 100) + int(t2[2])
    return 1 if tf1 < tf2 else 2
    
def addiere_fehler_zur_zeit(zeit, fehler):
    t = zeit.split(':')
    t_minute, t_sekunden, t_milisekunden = int(t[0]), int(t[1]), int(t[2])
    t_sekunden += int(fehler)
    if t_sekunden > 59:
        t_sekunden -= 60
        t_minute += 1
    return f"{t_minute:02}:{t_sekunden:02}:{t_milisekunden:02}"

def play_sound(self, file):
    if self.PlaySound:
        utils.write_konsole(self, 'Ein Sound wurde wiedergegeben!')
        sound = pygame.mixer.Sound(file)
        sound.play()

def reihenfolge_speichern(self, event, name):
    reihenfolge = event.widget.get()
    is_number = self.isNumber(reihenfolge)
    
    for i in self.Wettkampfgruppen:
        if i['gruppenname'] == name:
            if is_number == True:
                i['reihenfolge'] = reihenfolge
                utils.writeKonsole(name + ' hat die Reihenfolgenposition von ' + reihenfolge)
            else:
                i['reihenfolge'] = reihenfolge[:-1]
                utils.writeKonsole(name + ' hat die Reihenfolgenposition von ' + reihenfolge[:-1])
    
    gui.zeichne_angemeldete_gruppen()

def eintrag_damenwertung(self, event, name, value):
    for i in self.Wettkampfgruppen:
        if i['gruppenname'] == name:
            if value == True:
                i['damenwertung'] = False
                utils.writeKonsole(name + ' aus der Damenwertung entfernt')
            elif value == False:
                i['damenwertung'] = True
                utils.writeKonsole(name + ' zur Damenwertung hinzugefügt')
    
    gui.zeichne_angemeldete_gruppen(self)

def delete_wettkampfgruppe(self, event, name):
    for i in self.Wettkampfgruppen:
        if i['gruppenname'] == name:
            self.Wettkampfgruppen.remove(i)
    gui.zeichne_angemeldete_gruppen(self)
    utils.writeKonsole(name + ' wurde gelöscht!')

def uebernahme_gruppen(self, vonKonfig):
    if vonKonfig == False:
        new_Array = True
        count = 0
        for grp in self.Wettkampfgruppen:
            if grp['reihenfolge'] == '':
                count += 1
        if count == 0:
            res = messagebox.askquestion('Reset Auswertung', 'Die Auswertung wird komplett zurückgesetzt!')
            self.Durchgänge = []
            self.DGNumbers = [] 
        else:
            res = 'no'
            messagebox.showinfo('Info', 'Die Reihenfolge muss für jede Gruppe festgelegt werden!')
    else:
        new_Array = False
        res = 'yes'
    
    if res == 'yes':
        wechsel_ansicht_zur_auswertung(self)
        config.export_anmeldung_konfig(self.KonfigGruppenFile, self.Wettkampfgruppen)
        self.checked_Bahn_1.set(False)
        self.checked_Bahn_2.set(False)
        switch_bahn_1_state(self)
        switch_bahn_2_state(self)
        time_manager.reset(self) 
        self.root.BtnStart.configure(state=DISABLED)
        self.root.BtnAllesStop.configure(state=DISABLED)
        self.root.BtnWechsel.configure(state=DISABLED)
        self.root.BtnZeitUebertragen.configure(state=DISABLED)
        self.root.BtnStopReset .configure(state=DISABLED)
        change_color_from_button_summary(self)

        self.root.dg.pack_forget()
        self.root.dg = CTkScrollableFrame(self.root.FTab2, border_width=0, fg_color='transparent')
        self.root.dg.pack(expand=1, side='bottom', fill='both', padx=10, pady=10, ipady=10)
        self.root.zeitnehmung.pack_forget()
        self.root.zeitnehmung.pack(side='left', padx=5)
        self.root.LfBahnen.pack_forget()
        self.root.LfBahnen.pack(side='left', padx=10)
        self.root.korrektur.pack_forget()
        self.root.korrektur.pack(side='left', padx=5)
        mixedWertung = []
        damenWertung = []
        damen_vorhanden = False

        for grp in self.Wettkampfgruppen:
            if grp['reihenfolge'] == '':
                grp['reihenfolge'] = '0'
            if grp['damenwertung'] == True:
                damenWertung.append(grp)
                mixedWertung.append(grp) #TODO: DAMENWERTUNG ZUSÄTZLICH ODER EXTRA
            else:
                mixedWertung.append(grp)

        anzahl_gruppen = 0
        if len(mixedWertung) % 2:
            anzahl_gruppen = len(mixedWertung) + 1
        else: 
            anzahl_gruppen = len(mixedWertung)

        self.AnzahlGrunddurchgänge = anzahl_gruppen

        anzahl_damengruppen = 0
        if len(damenWertung) % 2:
            anzahl_damengruppen = len(damenWertung) + 1
        else: 
            anzahl_damengruppen = len(damenWertung)

        self.AnzahlDamendurchgänge = anzahl_damengruppen

        space = CTkLabel(self.root.dg, text='')
        space.grid(row=0, column=7, rowspan=anzahl_gruppen, sticky=(W+E+N+S), padx=(5,0), ipadx=20)
        space.grid(row=0, column=16, rowspan=anzahl_gruppen, sticky=(W+E+N+S), padx=(5,0), ipadx=20)
            
        if len(damenWertung) > 0:
            damen_vorhanden = True

        gui.zeichne_grundansicht(self, damen_vorhanden, new_Array) 

        self.root.TabView.set(self.NAME_TAB2)
        sorted_MixedWertung = sorted(mixedWertung, key=lambda x : int(x['reihenfolge']), reverse=False)
        sorted_DamenWertung = sorted(damenWertung, key=lambda x : int(x['reihenfolge']), reverse=False)

        for index, item in enumerate(sorted_MixedWertung):
            row = self.AnzeigeGDStartRow + int(index) + 1
            col1 = self.AnzeigeGDStartColumn + 1
            txt = item['reihenfolge'] + ' - ' + item['gruppenname']
            zeichne_neue_werte(self, row, col1, txt, row, col1, self.TYP_GD)

            for x in self.Durchgänge:
                if x['typ'] == self.TYP_GD  and x['row'] == row and x['column'] == col1:
                    x['wettkampfgruppe'] = item['gruppenname']

        for x in self.Durchgänge:
            if x['zeit1'] != '':
                text = str(x['zeit1'])
                if x['fehler1'] > 0:
                    text += ' +' + str(x['fehler1'])
                zeichne_neue_werte(self, x['row'], x['column']+1, text, x['row'], x['column'], x['typ'])
            if x['zeit2'] != '':
                text = str(x['zeit2'])
                if x['fehler2'] > 0:
                    text += ' +' + str(x['fehler2'])
                zeichne_neue_werte(self, x['row'], x['column']+2, text, x['row'], x['column'], x['typ'])
            if x['bestzeit'] != '':
                text = str(x['bestzeit'])
                if x['fehlerbest'] > 0:
                    text += ' +' + str(x['fehlerbest'])
                zeichne_neue_werte(self, x['row'], x['column']+3, text, x['row'], x['column'], x['typ'])

        utils.write_konsole(self, str(len(mixedWertung)) + ' Gruppen wurden übernommen!')

        for index, item in enumerate(sorted_DamenWertung):
            row = self.AnzeigeDWStartRow + int(index) + 1
            col1 = self.AnzeigeDWStartColumn + 1
            txt = item['reihenfolge'] + ' - ' + item['gruppenname']
            zeichne_neue_werte(self, row, col1, txt, row, col1, self.TYP_DW)

            
            for x in self.Durchgänge:
                if x['typ'] == self.TYP_DW and x['row'] == row and x['column'] == col1:
                    x['wettkampfgruppe'] = item['gruppenname']

        utils.write_konsole(self, str(len(damenWertung)) + ' Damengruppen wurden übernommen!')

        change_row_and_column_in_durchgaenge(self)
        bestzeit_platzierung_berechnen(self)
        lade_zeitnehmungs_daten(self)

def naechster_dg(self):
    dg_select = self.root.CBDG.get()
    dg_select = int(dg_select)

    dg_list = []
    for item in self.DGNumbers:
        try:
            dg_list.append(int(item))
        except ValueError:
            pass

    max_dg = max(dg_list)

    if dg_select < max_dg:
        self.root.CBDG.set(str(dg_select+1))
        lade_zeitnehmungs_daten(self)

def vorheriger_dg(self):
    dg_select = self.root.CBDG.get()
    dg_select = int(dg_select)

    if dg_select > 0:
        self.root.CBDG.set(str(dg_select-1))
        lade_zeitnehmungs_daten()

def bestzeit_platzierung_berechnen(self):
    for dg in self.Durchgänge:
        if dg['bestzeit'] != '':
            dg['bestzeitinklfehler'] = addiere_fehler_zur_zeit(dg['bestzeit'], dg['fehlerbest'])
        else:
            dg['bestzeitinklfehler'] = ''

    self.Durchgänge.sort(key=lambda dg: utils.sort_time(self, dg))

    hinweis = ''
    ko16_durchgang = 0
    ko8_durchgang = 0
    ko4_durchgang = 0

    platzierung_KO16_neu = 1

    # vf_durchgang = 0
    # vf_hinweis = ''
    # hf_durchgang = 0
    # hf_hinweis = ''
    dw_platzierung_neu = 1

    #TODO: Bestzeit berechnen
    
    for index, item in enumerate(self.Durchgänge):
        if item['typ'] == self.TYP_GD and item['bestzeitinklfehler'] != '':
            platzierung_GD_neu = index + 1
            item['platzierung'] = platzierung_GD_neu
            zeichne_neue_werte(item['row'], item['column'] + 4, platzierung_GD_neu, item['row'], item['column'], item['typ'])
    
            if item['platzierung'] >= 1 and item['platzierung'] <= 16:
                for dg in self.Durchgänge:
                    suchtext = 'GD_' + str(item['platzierung'])
                    if dg['hinweis'] == suchtext:
                        dg['wettkampfgruppe'] = item['wettkampfgruppe']
                        zeichne_neue_werte(dg['row'], dg['column'], item['wettkampfgruppe'], dg['row'], dg['column'], dg['typ'])
        
        if item['typ'] == self.TYP_KO16 and item['bestzeitinklfehler'] != '':
            item['platzierung'] = platzierung_KO16_neu
            zeichne_neue_werte(item['row'], item['column'] + 4, platzierung_KO16_neu, item['row'], item['column'], item['typ'])
            platzierung_KO16_neu += 1
    
            if item['platzierung'] >= 1 and item['platzierung'] <= 8:
                for dg in self.Durchgänge:
                    suchtext = 'KO16_' + str(item['platzierung'])
                    if dg['hinweis'] == suchtext:
                        dg['wettkampfgruppe'] = item['wettkampfgruppe']
                        zeichne_neue_werte(dg['row'], dg['column'], item['wettkampfgruppe'], dg['row'], dg['column'], dg['typ'])
        
        # if item['typ'] == self.TYP_KO16 and item['bestzeitinklfehler'] != '':
        #     if ko16_durchgang == 0 or ko16_durchgang < item['dg']:
        #         ko16_durchgang = item['dg']
        #         if item['hinweis'] == 'GD_1' or item['hinweis'] == 'GD_16':
        #             hinweis = 'KO8_1'
        #         elif item['hinweis'] == 'GD_2' or item['hinweis'] == 'GD_15':
        #             hinweis = 'KO8_2'
        #         elif item['hinweis']  == 'GD_3' or item['hinweis'] == 'GD_14':
        #             hinweis = 'KO8_3'
        #         elif item['hinweis'] == 'GD_4' or item['hinweis'] == 'GD_13':
        #             hinweis = 'KO8_4'
        #         elif item['hinweis'] == 'GD_5' or item['hinweis'] == 'GD_12':
        #             hinweis = 'KO8_5'
        #         elif item['hinweis']  == 'GD_6' or item['hinweis'] == 'GD_11':
        #             hinweis = 'KO8_6'
        #         elif item['hinweis'] == 'GD_7' or item['hinweis'] == 'GD_10':
        #             hinweis = 'KO8_7'
        #         elif item['hinweis'] == 'GD_8' or item['hinweis'] == 'GD_9':
        #             hinweis = 'KO8_8'
        #         for dg in self.Durchgänge:
        #             if dg['hinweis'] == hinweis:
        #                 dg['wettkampfgruppe'] = item['wettkampfgruppe']
        #                 zeichne_neue_werte(dg['row'], dg['column'], item['wettkampfgruppe'], dg['row'], dg['column'], dg['typ'])

        # if item['typ'] == self.TYP_KO8 and item['bestzeitinklfehler'] != '':
        #     if vf_durchgang == 0 or vf_durchgang < item['dg']:
        #         vf_durchgang = item['dg']
        #         if item['hinweis'] == 'GD_1' or item['hinweis'] == 'GD_8':
        #             vf_hinweis = 'VF_1'
        #         elif item['hinweis'] == 'GD_2' or item['hinweis'] == 'GD_7':
        #             vf_hinweis = 'VF_2'
        #         elif item['hinweis']  == 'GD_3' or item['hinweis'] == 'GD_6':
        #             vf_hinweis = 'VF_3'
        #         elif item['hinweis'] == 'GD_4' or item['hinweis'] == 'GD_5':
        #             vf_hinweis = 'VF_4'
        #         for dg in self.Durchgänge:
        #             if dg['hinweis'] == vf_hinweis:
        #                 dg['wettkampfgruppe'] = item['wettkampfgruppe']
        #                 zeichne_neue_werte(dg['row'], dg['column'], item['wettkampfgruppe'], dg['row'], dg['column'], dg['typ'])
        
        # if item['typ'] == self.TYP_KO4 and item['bestzeitinklfehler'] != '':
        #     if hf_durchgang == 0 or hf_durchgang < item['dg']:
        #         hf_durchgang = item['dg']
        #         if item['hinweis'] == 'VF_1' or item['hinweis'] == 'VF_2':
        #             hf_hinweis = 'F_1'
        #         elif item['hinweis'] == 'VF_3' or item['hinweis'] == 'VF_4':
        #             hf_hinweis = 'F_2'
        #         for dg in self.Durchgänge:
        #             if dg['hinweis'] == hf_hinweis:
        #                 dg['wettkampfgruppe'] = item['wettkampfgruppe']
        #                 zeichne_neue_werte(dg['row'], dg['column'], item['wettkampfgruppe'], dg['row'], dg['column'], dg['typ'])
        #     elif hf_durchgang == item['dg']:
        #         if item['hinweis'] == 'VF_1' or item['hinweis'] == 'VF_2':
        #             hf_hinweis = 'KF_1'
        #         elif item['hinweis'] == 'VF_3' or item['hinweis'] == 'VF_4':
        #             hf_hinweis = 'KF_2'
        #         for dg in self.Durchgänge:
        #             if dg['hinweis'] == hf_hinweis:
        #                 dg['wettkampfgruppe'] = item['wettkampfgruppe']
        #                 zeichne_neue_werte(dg['row'], dg['column'], item['wettkampfgruppe'], dg['row'], dg['column'], dg['typ'])

        if item['typ'] == self.TYP_DW and item['bestzeitinklfehler'] != '':
            item['platzierung'] = dw_platzierung_neu
            zeichne_neue_werte(item['row'], item['column'] + 4, dw_platzierung_neu, dg['row'], dg['column'], dg['typ'])  
            dw_platzierung_neu += 1

def zeichne_neue_werte(self, row, column, text, id_row, id_col, id_typ):
    for label in self.root.dg.grid_slaves(row=row, column=column):
        label.configure(text=text)
        if row == id_row and column == id_col:
            label.bind('<Button-1>', lambda event, typ=id_typ, row=id_row, column=id_col: gui.show_changing_window(event, typ, row, column))
    
    config.export_bewerb_konfig(self.KonfigBewerbFile, self.Durchgänge, self.DGNumbers)

def wechsel_ansicht_zur_zeit(self):
    self.anzeige.ERG.pack_forget()
    self.anzeige.G1.pack(expand=0, side=TOP, fill=X)
    self.anzeige.Z1.pack(expand=1, side=TOP, fill=BOTH)
    self.anzeige.Z2.pack(expand=1, side=TOP, fill=BOTH)
    self.anzeige.G2.pack(expand=0, side=BOTTOM, fill=X)
    gui.show_info(self)   

def lade_zeitnehmungs_daten(self, event=None):
    wechsel_ansicht_zur_zeit(self)
    self.checked_Bahn_1.set(False)
    self.checked_Bahn_2.set(False)
    switch_bahn_1_state(self)
    switch_bahn_2_state(self)
    self.root.G1.configure(text='...')
    self.root.G2.configure(text='...')
    self.root.T1.configure(text='00:00:00')
    self.root.T2.configure(text='00:00:00')
    self.root.F1.delete(0, END)
    self.root.F2.delete(0, END)
    self.id_time_1 = ''
    self.id_time_2 = ''
    check_time = False
    count = 1
    dg_select = self.root.CBDG.get()
    dg_select = int(dg_select)

    dg_list = []
    for item in self.DGNumbers:
        try:
            dg_list.append(int(item))
        except ValueError:
            pass

    max_dg = max(dg_list)
    min_dg = 1

    if dg_select == min_dg:
        self.root.BtnVorherigerDG.configure(state=DISABLED)
        self.root.BtnNaechsterDG.configure(state=NORMAL)

    if dg_select > min_dg and dg_select < max_dg:
        self.root.BtnVorherigerDG.configure(state=NORMAL)
        self.root.BtnNaechsterDG.configure(state=NORMAL)
    
    if dg_select == max_dg:
        self.root.BtnVorherigerDG.configure(state=NORMAL)
        self.root.BtnNaechsterDG.configure(state=DISABLED)
    
    change_color_from_button_summary(self)

    for dg in self.Durchgänge:
        if dg['dg'] == dg_select:
            if count == 1 and dg['wettkampfgruppe'] != '...' and dg['wettkampfgruppe'] != '':
                self.checked_Bahn_1.set(True)
                switch_bahn_1_state(self)
                self.root.G1.configure(text=dg['wettkampfgruppe'])
                self.anzeige.G1.configure(text=dg['wettkampfgruppe'])
                self.id_time_1 = 'typ.row.column#' + str(dg['typ']) + '#' + str(dg['row']) + '#' + str(dg['column'])
                if dg['zeit1'] != '' and dg['zeit2'] != '':
                    check_time = True
            elif count == 2 and dg['wettkampfgruppe'] != '...' and dg['wettkampfgruppe'] != '':
                self.checked_Bahn_2.set(True)
                switch_bahn_2_state(self)
                self.root.G2.configure(text=dg['wettkampfgruppe'])
                self.anzeige.G2.configure(text=dg['wettkampfgruppe'])
                self.id_time_2 = 'typ.row.column#' + str(dg['typ']) + '#' + str(dg['row']) + '#' + str(dg['column'])
                if dg['zeit1'] != '' and dg['zeit2'] != '':
                    check_time = True
            count += 1

    time_manager.reset(self)

    if check_time == True:
        messagebox.showinfo('Info', 'Für diese Gruppen existieren schon zwei Zeiten vorhanden!')

def switch_bahn_1_state(self):
    if self.checked_Bahn_1.get() == False:
        self.root.G1.configure(state=DISABLED)
        self.root.T1.configure(state=DISABLED)
        self.root.F1.configure(state=DISABLED)
        self.root.B1.configure(state=DISABLED)
        self.anzeige.G1.pack_forget()
        self.anzeige.Z1.pack_forget()
        utils.write_konsole(self, 'Bahn 1 wurde deaktiviert!')
    else:
        self.root.G1.configure(state=NORMAL)
        self.root.T1.configure(state=NORMAL)
        self.root.F1.configure(state=NORMAL)
        self.root.B1.configure(state=NORMAL)
        self.anzeige.G1.pack(expand=0, side=TOP, fill=X)
        self.anzeige.Z1.pack(expand=1, side=TOP, fill=BOTH)
        utils.write_konsole(self, 'Bahn 1 wurde aktiviert!')

def switch_bahn_2_state(self):
    if self.checked_Bahn_2.get() == False:
        self.root.G2.configure(state=DISABLED)
        self.root.T2.configure(state=DISABLED)
        self.root.F2.configure(state=DISABLED)
        self.root.B2.configure(state=DISABLED)
        self.anzeige.G2.pack_forget()
        self.anzeige.Z2.pack_forget()
        utils.write_konsole(self, 'Bahn 2 wurde deaktiviert!')
    else:
        self.root.G2.configure(state=NORMAL)
        self.root.T2.configure(state=NORMAL)
        self.root.F2.configure(state=NORMAL)
        self.root.B2.configure(state=NORMAL)
        self.anzeige.G2.pack(expand=0, side=BOTTOM, fill=X)
        self.anzeige.Z2.pack(expand=1, side=TOP, fill=BOTH)
        utils.write_konsole(self, 'Bahn 2 wurde aktiviert!')

def update_rahmen_anzeige(self):
    if self.checked_Rahmen.get() == True:
        self.anzeige.wm_attributes('-type', 'splash')

def update_fontsize_zeit(self, event=None):
    size = self.root.SGZ.get()
    self.anzeige.Z1.configure(font=(self.GlobalFontArt, size))
    self.anzeige.Z2.configure(font=(self.GlobalFontArt, size))

def update_fontsize_gruppe(self, event=None):
    size = self.root.SGG.get()
    self.anzeige.G1.configure(font=(self.GlobalFontArt, size))
    self.anzeige.G2.configure(font=(self.GlobalFontArt, size))

def change_fontsize_from_windowsize(self, event=None):
    self.screen_height = self.anzeige.winfo_height()
    self.root.LblAnpassungWert.configure(text=str(self.screen_height))

    size_new = int(self.screen_height) / int(self.root.SBFaktorZeit.get())
    self.root.SGZ.set(size_new)
    self.anzeige.Z1.configure(font=(self.GlobalFontArt, size_new))
    self.anzeige.Z2.configure(font=(self.GlobalFontArt, size_new))
    self.AnzeigeFontSizeTime = size_new

    size_new = int(self.screen_height) / int(self.root.SBFaktorGruppen.get())
    self.root.SGG.set(size_new)
    self.anzeige.G1.configure(font=(self.GlobalFontArt, size_new))
    self.anzeige.G2.configure(font=(self.GlobalFontArt, size_new))
    self.AnzeigeFontSizeGroup = size_new

    size_new = int(self.screen_height) / int(self.root.SBFaktorInfo.get())
    self.AnzeigeFontSizeInfo = size_new
    for widgets in self.anzeige.INFO.winfo_children():
        widgets.configure(font=(self.GlobalFontArt, size_new))
    
    size_new = int(self.screen_height) / int(self.root.SBFaktorAuswertung.get())
    self.AnzeigeFontSizeAuswertung = size_new
    for widgets in self.anzeige.INFO.winfo_children():
        widgets.configure(font=(self.GlobalFontArt, size_new))

def test_gruppen_erstellen(self):
    # TODO: inkl Zeiten wenn angehakt
    anzahl = self.root.SBAnzahlGruppen.get()
    damenAnzahl = self.root.SBAnzahlDamenGruppen.get()
    
    if len(self.Wettkampfgruppen) > 0:
        self.Wettkampfgruppen = []
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

        val= {
        'gruppenname': 'Gruppe' + str(i + 1),
        'reihenfolge': str(rh),
        'damenwertung': False
        }
        if dwrh <= int(damenAnzahl):
            val['damenwertung'] = True
        self.Wettkampfgruppen.append(val)

    gui.zeichne_angemeldete_gruppen(self)
    self.root.TabView.set(self.NAME_TAB1)

def change_color_from_button(self, button):
    source_fg_color = self.root.BtnUebernehmen.cget('fg_color')
    disabled_fg_color = 'transparent'
    state = button.cget('state')

    mode = set_appearance_mode("light")

    if mode == 'Light' and isinstance(source_fg_color, list):
        source_fg_color = source_fg_color[0]
    elif mode == 'Dark' and isinstance(source_fg_color, list):
        source_fg_color = source_fg_color[1]


    if state == 'disabled':
        button.configure(fg_color=disabled_fg_color)
    else:
        button.configure(fg_color=source_fg_color)

def change_color_from_button_summary(self):
    change_color_from_button(self, self.root.BtnVorherigerDG)
    change_color_from_button(self, self.root.BtnNaechsterDG)
    change_color_from_button(self, self.root.BtnStart)
    change_color_from_button(self, self.root.BtnAllesStop)
    change_color_from_button(self, self.root.BtnWechsel)
    change_color_from_button(self, self.root.BtnAnsichtWechseln)
    change_color_from_button(self, self.root.BtnZeitUebertragen)
    change_color_from_button(self, self.root.BtnStopReset)

def change_row_and_column_in_durchgaenge(self):
    if len(self.Durchgänge) > 0:
        row_kf = self.AnzeigeKFStartRow + 1
        col_kf = self.AnzeigeKFStartColumn + 1
        row_f = self.AnzeigeFStartRow + 1
        col_f = self.AnzeigeFStartColumn + 1
        row_dw = self.AnzeigeDWStartRow + 1
        col_dw = self.AnzeigeDWStartColumn + 1
        self.Durchgänge.sort(key=utils.sort_time_by_row)
        for dg in self.Durchgänge:
            if dg['typ'] == self.TYP_KF:
                dg['row'] = row_kf
                dg['column'] = col_kf
                row_kf += 1
            if dg['typ'] == self.TYP_F:
                dg['row'] = row_f
                dg['column'] = col_f
                row_f += 1
            if dg['typ'] == self.TYP_DW:
                dg['row'] = row_dw
                dg['column'] = col_dw
                row_dw += 1
        
        self.Durchgänge.sort(key=lambda dg: utils.sort_time(self, dg))

def lade_auswertung_daten(self):
    for widgets in self.anzeige.ERG.winfo_children():
        widgets.grid_remove()

    f_durchgang = 0

    count_gd = 0
    count_ko16 = 0
    count_ko8 = 0
    count_ko4 = 0
    count_kf = 0
    count_f = 0
    count_dw = 0

    for dg in self.Durchgänge:
        if dg['typ'] == self.TYP_GD and dg['platzierung'] > 0:
            count_gd += 1
        if dg['typ'] == self.TYP_KO16 and dg['bestzeitinklfehler'] != '':
            count_ko16 += 1
        if dg['typ'] == self.TYP_KO8 and dg['bestzeitinklfehler'] != '':
            count_ko8 += 1
        if dg['typ'] == self.TYP_KO4 and dg['bestzeitinklfehler'] != '':
            count_ko4 += 1
        if dg['typ'] == self.TYP_KF and dg['bestzeitinklfehler'] != '':
            count_kf += 1
        if dg['typ'] == self.TYP_F and dg['bestzeitinklfehler'] != '':
            count_f += 1
        if dg['typ'] == self.TYP_DW and dg['platzierung'] > 0:
            count_dw += 1
    
    if count_gd > 0:
        title = CTkLabel(self.anzeige.ERG, text='GRUNDDURCHGANG', fg_color=self.AnzeigeGroupColor, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
        title.grid(row=self.AnzeigeGDStartRow, column=self.AnzeigeGDStartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(30,0))
    
    if count_ko16 > 0:
        title = CTkLabel(self.anzeige.ERG, text='KO 1-16', fg_color=self.AnzeigeGroupColor, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
        title.grid(row=self.AnzeigeKO16StartRow, column=self.AnzeigeKO16StartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(30,0))

    if count_ko8 > 0:
        title = CTkLabel(self.anzeige.ERG, text='KO 1-8', fg_color=self.AnzeigeGroupColor, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
        title.grid(row=self.AnzeigeKO8StartRow, column=self.AnzeigeKO4StartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(30,0))
    
    if count_ko4 > 0:
        title = CTkLabel(self.anzeige.ERG, text='KO 1-4', fg_color=self.AnzeigeGroupColor, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
        title.grid(row=self.AnzeigeKO4StartRow, column=self.AnzeigeKO4StartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(1,0))
    
    if count_kf > 0:
        title = CTkLabel(self.anzeige.ERG, text='KLEINES FINALE', fg_color=self.AnzeigeGroupColor, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
        title.grid(row=self.AnzeigeKFStartRow, column=self.AnzeigeKFStartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(30,0))

            
    if count_f > 0:
        title = CTkLabel(self.anzeige.ERG, text='FINALE', fg_color=self.AnzeigeGroupColor, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
        title.grid(row=self.AnzeigeFStartRow, column=self.AnzeigeFStartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(1,0))
    
    if count_dw > 0:
        title = CTkLabel(self.anzeige.ERG, text='DAMENWERTUNG', fg_color=self.AnzeigeGroupColor, anchor='w' , font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
        title.grid(row=self.AnzeigeDWStartRow, column=self.AnzeigeDWStartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(30,0))


    for dg in self.Durchgänge:
        if (dg['typ'] == self.TYP_GD or dg['typ'] == self.TYP_DW or dg['typ'] == self.TYP_KO8 or dg['typ'] == self.TYP_KO4 or dg['typ'] == self.TYP_KF or dg['typ'] == self.TYP_F) and dg['platzierung'] > 0:
            color = '#ffffff'
            if dg['typ'] == self.TYP_GD:
                row = dg['platzierung']
                col = 0
                if dg['platzierung'] <= 16:
                    color = self.GlobalDGBackgroundColor
            if dg['typ'] == self.TYP_KO16:
                row = dg['platzierung']
                col = 0
                if dg['platzierung'] <= 8:
                    color = self.GlobalDGBackgroundColor
            if dg['typ'] == self.TYP_KO8:
                row = dg['platzierung']
                col = 0
                if dg['platzierung'] <= 4:
                    color = self.GlobalDGBackgroundColor
            if dg['typ'] == self.TYP_KO4:
                row = dg['platzierung']
                col = 0
                if dg['platzierung'] <= 2:
                    color = self.GlobalDGBackgroundColor
            if dg['typ'] == self.TYP_KF or dg['typ'] == self.TYP_F:
                row = dg['platzierung']
                col = 0
                if dg['platzierung'] <= 1:
                    color = self.GlobalDGBackgroundColor
            if dg['typ'] == self.TYP_DW:
                row = dg['platzierung'] + self.AnzeigeDWStartRow
                col = self.AnzeigeDWStartColumn + 1
                if dg['platzierung'] <= 1:
                    color = self.GlobalDGBackgroundColor

            text = str(dg['platzierung']) + '. ' + dg['wettkampfgruppe']
            w = CTkLabel(self.anzeige.ERG, text=text, anchor='w', fg_color=color, font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            w.grid(row=row, column=col, sticky=(W+E+N+S), padx=(20,0), ipady='2')
            time = ''
            if self.ZeigeAlleZeiten == True:
                if dg['zeit1'] != '':
                    time += '   ' + dg['zeit1'] + ' + ' + str(dg['fehler1'])
                if dg['zeit2'] != '':
                    time += '   ' + dg['zeit2'] + ' + ' + str(dg['fehler2'])
            
            time += '   BZ_' + dg['bestzeit'] + ' + ' + str(dg['fehlerbest'])

            t = CTkLabel(self.anzeige.ERG, text=time, anchor='w', fg_color=color, font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            t.grid(row=row, column=col+1, sticky=(W+E+N+S), padx=(0,20), ipady='2')
        
        # if (dg['typ'] == self.TYP_KO8 or dg['typ'] == self.TYP_KO4 or dg['typ'] == self.TYP_KF or dg['typ'] == self.TYP_F) and dg['bestzeitinklfehler'] != '':
        #     color = '#ffffff'
        #     if f_durchgang == 0 or f_durchgang < dg['dg']:
        #         f_durchgang = dg['dg']
        #         color = self.GlobalDGBackgroundColor
    
        #     w = CTkLabel(self.anzeige.ERG, text=dg['wettkampfgruppe'], fg_color=color, font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
        #     w.grid(row=dg['row'], column=dg['column'], sticky=(W+E+N+S), padx=(20,0), ipady='2')
        #     time = ''
        #     if self.ZeigeAlleZeiten == True:
        #         if dg['zeit1'] != '':
        #             time += '   ' + dg['zeit1'] + ' + ' + str(dg['fehler1'])
        #         if dg['zeit2'] != '':
        #             time += '   ' + dg['zeit2'] + ' + ' + str(dg['fehler2'])
            
        #     time += '   BZ_' + dg['bestzeit'] + ' + ' + str(dg['fehlerbest'])
        #     t = CTkLabel(self.anzeige.ERG, text=time, anchor='w', fg_color=color, font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
        #     t.grid(row=dg['row'], column=dg['column']+1, sticky=(W+E+N+S), padx=(0,20), ipady='2')
    
    if len(self.Durchgänge) > 0:
        count = 0
        for dg in self.Durchgänge:
            if dg['typ'] == self.TYP_DW:
                count += 1

        startRowBestzeit = self.AnzeigeDWStartRow + count + 1
        startColumnBestzeit = self.AnzeigeDWStartColumn + 1

        startRowQualZeit = startRowBestzeit + 3
        startColumnQualzeit = startColumnBestzeit
        

        self.Durchgänge.sort(key=utils.sort_time_by_besttime)
        bestgroup = self.Durchgänge[0]['wettkampfgruppe']
        besttime = self.Durchgänge[0]['bestzeit']
        bestfehler = str(self.Durchgänge[0]['fehlerbest'])
        if besttime != '':
            timetext = '   ' + besttime + ' + ' + bestfehler
            tagessieg_title = CTkLabel(self.anzeige.ERG, text='TAGESBESTZEIT', fg_color=self.AnzeigeGroupColor, anchor='w' , font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            tagessieg_title.grid(row=startRowBestzeit, column=startColumnBestzeit, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(1,0))
            tagessieg_group = CTkLabel(self.anzeige.ERG, text=bestgroup, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            tagessieg_group.grid(row=startRowBestzeit+1, column=startColumnBestzeit, sticky=(W+E+N+S), padx=(20,0), ipady='2')
            tagessieg_time = CTkLabel(self.anzeige.ERG, text=timetext, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            tagessieg_time.grid(row=startRowBestzeit+1, column=startColumnBestzeit+1, sticky=(W+E+N+S), padx=(0,20), ipady='2')
        
        self.Durchgänge.sort(key=lambda dg: utils.sort_time(self, dg))
        bestgroup = self.Durchgänge[7]['wettkampfgruppe']
        besttime = self.Durchgänge[7]['bestzeit']
        bestfehler = str(self.Durchgänge[7]['fehlerbest'])
        if besttime != '':
            timetext = '   ' + besttime + ' + ' + bestfehler
            tagessieg_title = CTkLabel(self.anzeige.ERG, text='QUALIFIKATIONSZEIT', fg_color=self.AnzeigeGroupColor, anchor='w' , font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            tagessieg_title.grid(row=startRowQualZeit, column=startColumnQualzeit, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(1,0))
            tagessieg_group = CTkLabel(self.anzeige.ERG, text=bestgroup, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            tagessieg_group.grid(row=startRowQualZeit+1, column=startColumnQualzeit, sticky=(W+E+N+S), padx=(20,0), ipady='2')
            tagessieg_time = CTkLabel(self.anzeige.ERG, text=timetext, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            tagessieg_time.grid(row=startRowQualZeit+1, column=startColumnQualzeit+1, sticky=(W+E+N+S), padx=(0,20), ipady='2')

def wechsel_ansicht_zur_auswertung(self):
    self.anzeige.G1.pack_forget()
    self.anzeige.Z1.pack_forget()
    self.anzeige.Z2.pack_forget()
    self.anzeige.G2.pack_forget()
    self.anzeige.ERG.pack(expand=1, side=TOP, fill=BOTH)
    lade_auswertung_daten(self)  
    gui.show_info(self)   

def anzeige_umschalten(self):
    if self.Status_Anzeige == False:
        self.Status_Anzeige = True
        wechsel_ansicht_zur_zeit()
    else:
        self.Status_Anzeige = False
        wechsel_ansicht_zur_auswertung(self)

def bahn_wechsel(self):
    werte_in_ansicht_uebertragen()
    # TODO: Nur Bahnwechsel wenn noch mindestens eine Zeit offen ist

    bahnA = self.root.G1.cget('text')
    bahnB = self.root.G2.cget('text')

    bahnAId = self.id_time_1
    bahnBId = self.id_time_2

    self.root.G1.configure(text=bahnB)
    self.id_time_1 = bahnBId
    self.root.G2.configure(text=bahnA)

    self.anzeige.G1.configure(text=bahnB)
    self.id_time_2 = bahnAId
    self.anzeige.G2.configure(text=bahnA)
    
    self.root.BtnStart.configure(state=NORMAL)
    change_color_from_button_summary()
    
    self.checked_Bahn_1.set(False)
    self.checked_Bahn_2.set(False)
    switch_bahn_1_state()
    switch_bahn_2_state()

    if self.root.G1.cget('text') != '...':
        self.checked_Bahn_1.set(True)
        switch_bahn_1_state()
    if self.root.G2.cget('text') != '...':
        self.checked_Bahn_2.set(True)
        switch_bahn_2_state()

    utils.write_konsole(self, 'Die Bahnen wurden gewechselt!')

def werte_in_ansicht_uebertragen(self):
    self.root.CBDG.focus_set()
    dg_select = self.root.CBDG.get()

    if self.id_time_1  != '' and self.ZeitUebertragen == False:
        zeit1A = self.root.T1.cget('text')
        fehler1A = self.root.F1.get()
        if fehler1A == '':
            fehler1A == '0'
        id1A = self.id_time_1.split('#')
        typ1A = id1A[1]
        row1A = int(id1A[2])
        column1A = int(id1A[3])
        zeit_uebertragen(typ1A, row1A, column1A, zeit1A, fehler1A, int(dg_select))

    if self.id_time_2  != '' and self.ZeitUebertragen == False:
        zeit2A = self.root.T2.cget('text')
        fehler2A = self.root.F2.get()
        if fehler2A == '':
            fehler2A == '0'
        id2A = self.id_time_2.split('#')
        typ2A = id2A[1]
        row2A = int(id2A[2])
        column2A = int(id2A[3])
        zeit_uebertragen(typ2A, row2A, column2A, zeit2A, fehler2A, int(dg_select))
    
    if self.ZeitUebertragen == False:
        self.ZeitUebertragen = True

    self.root.T1.configure(text='00:00:00')
    self.root.T2.configure(text='00:00:00')
    self.root.F1.delete(0, END)
    self.root.F2.delete(0, END)
    self.anzeige.Z1.configure(text='00:00:00')
    self.anzeige.Z2.configure(text='00:00:00')

    bestzeit_platzierung_berechnen(self)

def zeit_uebertragen(self, typ, row, column, zeit, fehler, dg):
    if fehler == '':
        fehler = 0
    elif fehler != '':
        fehler = int(fehler)
    
    for x in self.Durchgänge:
        if x['typ'] == typ and x['row'] == row and x['column'] == column and x['dg'] == dg:
            if x['zeit1'] == '':
                x['zeit1'] = zeit
                x['fehler1'] = fehler
                x['bestzeit'] = zeit
                x['fehlerbest'] = fehler
                text = str(zeit)
                if fehler > 0:
                    text += ' +' + str(fehler)
                zeichne_neue_werte(self, row, column+1, text, row, column, typ)
                zeichne_neue_werte(self, row, column+3, text, row, column, typ)
            elif x['zeit2'] == '':
                x['zeit2'] = zeit
                x['fehler2'] = fehler
                text = str(zeit)
                if fehler > 0:
                    text += ' +' + str(fehler)
                zeichne_neue_werte(self, row, column+2, text, row, column, typ)
                
                time1 = addiere_fehler_zur_zeit(x['zeit1'], x['fehler1']) 
                time2 = addiere_fehler_zur_zeit(zeit, fehler)

                if berechne_bestzeit(time1, time2) == 2:
                    x['bestzeit'] = zeit
                    x['fehlerbest'] = fehler
                    zeichne_neue_werte(self, row, column+3, text, row, column, typ)
