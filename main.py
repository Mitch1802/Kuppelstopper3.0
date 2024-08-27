from tkinter import messagebox
from customtkinter import *
from datetime import datetime
import time, os, sys, json, re, pygame, random
from gpiozero import Button as GPIO_Button
from threading import Thread
from PIL import Image
from typing import Union, Callable

class Kuppelstopper(): 
    pygame.init()
    pfad = os.path.dirname(os.path.abspath(sys.argv[0]))
    pfad = pfad.replace('\\', '/')

    LogFile = pfad + '/log.txt'
    KonfigGruppenFile = pfad + '/config/anmeldung.json'
    KonfigBewerbFile = pfad + '/config/bewerb.json'
    KonfigSetupFile = pfad + '/config/setup.json'
    KonfigThemeFile = pfad + '/config/theme.json'

    set_default_color_theme(KonfigThemeFile)
    set_appearance_mode("light")

    Status_Anzeige = True # True = Zeit, False Auswertung

    TYP_GD = '1_gd'
    TYP_VF = '2_vf'
    TYP_HF = '3_hf'
    TYP_KF = '4_kf'
    TYP_F = '5_f'
    TYP_DW = '6_dw'

    NAME_TAB1 = 'Anmeldung'
    NAME_TAB2 = 'Übersicht - Zeitnehmung'
    NAME_TAB3 = 'Einstellungen'

    DurchgangNummer = 1
    AnzahlGrunddurchgänge = 0

    AnzeigeGDStartRow = 0
    AnzeigeGDStartColumn = 0
    AnzeigeVFStartRow = 0
    AnzeigeVFStartColumn = 8
    AnzeigeHFStartRow = 10
    AnzeigeHFStartColumn = 8
    AnzeigeKFStartRow = 16
    AnzeigeKFStartColumn = 8
    AnzeigeFStartRow = 20
    AnzeigeFStartColumn = 8
    AnzeigeDWStartRow = 24
    AnzeigeDWStartColumn = 8

    ZeitUebertragen = False
    Buzzer1DarfStarten = False
    time_is_running_1 = False
    start_time_1 = ''
    stop_time_1 = ''
    id_time_1 = ''
    Buzzer1DarfStarten = False
    time_is_running_2 = False
    start_time_2 = ''
    stop_time_2 = ''
    id_time_2 = ''

    # Hauptfenster
    def __init__(self):
        self.ladeKonfiguration()

        self.__root = CTk()
        self.__root.title(self.Title)
        # self.__root.minsize(self.__root.winfo_screenwidth()/1.5,self.__root.winfo_screenheight()/1.5)

        # self.__root.iconbitmap(self.FileIcon)   
        self.iconDelete = CTkImage(light_image=Image.open(self.FileIconDelete),dark_image=Image.open(self.FileIconDelete))

        self.screen_height = self.__root.winfo_height()
        self.screen_width = self.__root.winfo_width()

        self.checked_Bahn_1 = BooleanVar()
        self.checked_Bahn_2 = BooleanVar()
        self.checked_Tastatur = BooleanVar()
        self.checked_GPIO = BooleanVar()
        self.checked_Rahmen = BooleanVar()
        self.checked_Konsole = BooleanVar()

        self.checked_Bahn_1.set(False)
        self.checked_Bahn_2.set(False)
        self.checked_Tastatur.set(True)
        self.checked_GPIO.set(False)
        self.checked_Rahmen.set(False)
        self.checked_Konsole.set(True)

        self.initGPIO()
        self.erstelleTabView()
        self.erstelleFTab1()
        self.erstelleFTab2()
        self.erstelleFTab3()        

        self.showAnzeige()

        if len(self.Durchgänge) > 0:
            self.uebernahmeGruppen(True)
        
        self.__root.mainloop()

    def initGPIO(self, event=None):
        if self.checked_GPIO.get() == True:
            self.BuzzerStartBahn1 = GPIO_Button(self.GPIO_Start_1)
            self.BuzzerStopBahn1 = GPIO_Button(self.GPIO_Stop_1)
            self.BuzzerStartBahn2 = GPIO_Button(self.GPIO_Start_2)
            self.BuzzerStopBahn2 = GPIO_Button(self.GPIO_Stop_2)

    def erstelleTabView(self):
        self.__root.TabView = CTkTabview(self.__root, anchor='nw', corner_radius=0, fg_color='transparent')
        self.__root.TabView.pack(expand=1, side='top', fill='both', padx=5, pady=5)
        self.__root.FTab1 = self.__root.TabView.add(self.NAME_TAB1)
        self.__root.FTab2 = self.__root.TabView.add(self.NAME_TAB2)
        self.__root.FTab3 = self.__root.TabView.add(self.NAME_TAB3)
    
    def erstelleFTab1(self):
        self.__root.Entry = CTkEntry(self.__root.FTab1, corner_radius=0, placeholder_text='Gruppenname')
        self.__root.Entry.pack(side='top', fill='x', padx=10, pady=10)
        self.__root.Entry.bind('<Return>', self.addWettkampfgruppe)

        self.__root.LfReihenfolge = CTkScrollableFrame(self.__root.FTab1, border_width=0, corner_radius=0, fg_color='transparent')
        self.__root.LfReihenfolge.pack(expand=1 ,side='top', fill='both', padx=10, pady=10) 

        if len(self.Wettkampfgruppen) == 0:
            self.__root.LNoGroups = CTkLabel(self.__root.LfReihenfolge, text='Keine Gruppen angemeldet!', anchor='w')
            self.__root.LNoGroups.grid(row=0, column=0, sticky=(W+E+N+S), padx=10, pady=5)
        else:
            self.zeichneAngemeldeteGruppen()

        self.__root.BtnUebernehmen = CTkButton(self.__root.FTab1, text='Gruppen übernehmen', command=lambda:self.uebernahmeGruppen(False), corner_radius=0)
        self.__root.BtnUebernehmen.pack(side='bottom', fill='x', padx=10, pady=10)

    def erstelleFTab2(self):
        self.__root.dg = CTkScrollableFrame(self.__root.FTab2, border_width=0, fg_color='transparent')

        self.__root.zeitnehmung = CTkFrame(self.__root.FTab2, border_width=0, fg_color='transparent')
        self.__root.BtnAnsichtWechseln = CTkButton(self.__root.zeitnehmung, text='Ansicht wechseln', width=120, corner_radius=0, command=self.anzeigeUmschalten)
        self.__root.BtnAnsichtWechseln.pack(side='left', padx=5, pady=20, ipady=15) 
        self.__root.CBDG = CTkComboBox(self.__root.zeitnehmung, justify=CENTER, width=100, height=58, corner_radius=0, state='readonly', command=self.ladeZeitnehmungsDaten)
        self.__root.CBDG.pack(side='left', padx=5, pady=20)
        self.__root.BtnVorherigerDG = CTkButton(self.__root.zeitnehmung, text='DG -', width=50, corner_radius=0, command=self.vorherigerDG)
        self.__root.BtnVorherigerDG.pack(side='left', padx=5, pady=20, ipady=15)
        self.__root.BtnNaechsterDG = CTkButton(self.__root.zeitnehmung, text='DG +', width=50, corner_radius=0, command=self.naechsterDG)
        self.__root.BtnNaechsterDG.pack(side='left', padx=5, pady=20, ipady=15)
        self.__root.BtnStart = CTkButton(self.__root.zeitnehmung, text='Start', width=70, corner_radius=0, command=self.start, state=DISABLED)
        self.__root.BtnStart.pack(side='left', padx=5, pady=20, ipady=15)
        self.__root.BtnAllesStop = CTkButton(self.__root.zeitnehmung, text='Alles Stop', width=90,  corner_radius=0, command=self.allesStop, state=DISABLED)
        self.__root.BtnAllesStop.pack(side='left', padx=5, pady=20, ipady=15)
        self.__root.BtnWechsel = CTkButton(self.__root.zeitnehmung, text='Bahn Wechsel', width=100, corner_radius=0, command=self.bahnWechsel, state=DISABLED)
        self.__root.BtnWechsel.pack(side='left', padx=5, pady=20, ipady=15)
        self.__root.BtnZeitUebertragen = CTkButton(self.__root.zeitnehmung, text='Zeit übertragen', width=110, corner_radius=0, command=self.werteInAnsichtUebertragen, state=DISABLED)
        self.__root.BtnZeitUebertragen.pack(side='left', padx=5, pady=20, ipady=15)

        self.__root.LfBahnen = CTkFrame(self.__root.FTab2, border_width=1, corner_radius=0, fg_color='transparent')

        self.__root.CB1 = CTkCheckBox(self.__root.LfBahnen, text='Bahn 1', variable=self.checked_Bahn_1, corner_radius=0, command=self.switchBahn1State)
        self.__root.CB1.grid(row=0, column=0, padx=5, pady=(3,0))
        self.__root.G1 = CTkLabel(self.__root.LfBahnen, text='...', corner_radius=0, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), state=DISABLED)
        self.__root.G1 .grid(row=0, column=1, padx=5, pady=(5,0))
        self.__root.T1 = CTkLabel(self.__root.LfBahnen, text='00:00:00', corner_radius=0, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), state=DISABLED)
        self.__root.T1.grid(row=0, column=2, padx=5, pady=(5,0))
        self.__root.LblFehler1 = CTkLabel(self.__root.LfBahnen, text='Fehler')
        self.__root.LblFehler1 .grid(row=0, column=3, padx=5, pady=(5,0))
        self.__root.F1 = CTkEntry(self.__root.LfBahnen, width=5, corner_radius=0)
        self.__root.F1.grid(row=0, column=4, padx=5, pady=(5,0))
        self.__root.B1 = CTkButton(self.__root.LfBahnen, text='Stop', width=70, corner_radius=0, command=self.stop_1, state=DISABLED)
        self.__root.B1.grid(row=0, column=5, padx=(0,5), pady=(5,0))

        self.__root.CB2 = CTkCheckBox(self.__root.LfBahnen, text='Bahn 2', variable=self.checked_Bahn_2, corner_radius=0, command=self.switchBahn2State)
        self.__root.CB2.grid(row=1, column=0, padx=5, pady=(0,3))
        self.__root.G2 = CTkLabel(self.__root.LfBahnen, text='...', corner_radius=0, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), state=DISABLED)
        self.__root.G2 .grid(row=1, column=1, padx=5, pady=(0,5))
        self.__root.T2 = CTkLabel(self.__root.LfBahnen, text='00:00:00', corner_radius=0, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), state=DISABLED)
        self.__root.T2.grid(row=1, column=2, padx=5, pady=(0,5))
        self.__root.LblFehler2 = CTkLabel(self.__root.LfBahnen, text='Fehler')
        self.__root.LblFehler2 .grid(row=1, column=3, padx=5, pady=(0,5))
        self.__root.F2 = CTkEntry(self.__root.LfBahnen, width=5, corner_radius=0)
        self.__root.F2.grid(row=1, column=4, padx=5, pady=(0,5))
        self.__root.B2 = CTkButton(self.__root.LfBahnen, text='Stop', width=70, corner_radius=0, command=self.stop_2, state=DISABLED)
        self.__root.B2.grid(row=1, column=5, padx=(0,5), pady=(0,5))

        self.__root.korrektur = CTkFrame(self.__root.FTab2, border_width=0, fg_color='transparent')

        self.__root.BtnStopReset = CTkButton(self.__root.korrektur, text='Stop and Reset', width=110, corner_radius=0, command=self.stopreset, state=DISABLED)
        self.__root.BtnStopReset.pack(side='left', padx=5, pady=20, ipady=15) 
        self.__root.BtnLoeZ1 = CTkButton(self.__root.korrektur, text='DG Zeit 1+2 löschen', width=120, corner_radius=0, command=self.zeit1loeschen)
        self.__root.BtnLoeZ1.pack(side='left', padx=5, pady=20, ipady=15) 
        self.__root.BtnLoeZ2 = CTkButton(self.__root.korrektur, text='DG Zeit 2 löschen', width=120, corner_radius=0, command=self.zeit2loeschen)
        self.__root.BtnLoeZ2.pack(side='left', padx=5, pady=20, ipady=15) 

    def erstelleFTab3(self):
        self.__root.setupEingabe = CTkFrame(self.__root.FTab3, border_width=1, corner_radius=0, fg_color='transparent')
        self.__root.setupEingabe.pack(side='top', fill='x', padx=10, pady=5)
        self.__root.CheckTastatur = CTkCheckBox(self.__root.setupEingabe, text='Tastatur', corner_radius=0, variable=self.checked_Tastatur)
        self.__root.CheckTastatur.grid(row=0, column=0, padx=10, pady=10)
        self.__root.CheckGPIO = CTkCheckBox(self.__root.setupEingabe, text='GPIO', variable=self.checked_GPIO, corner_radius=0, command=self.initGPIO)
        self.__root.CheckGPIO.grid(row=0, column=1, pady=10)
        self.__root.CheckRahmen = CTkCheckBox(self.__root.setupEingabe, text='Rahmen ausblenden', variable=self.checked_Rahmen, corner_radius=0, command=self.updateRahmenAnzeige)
        self.__root.CheckRahmen.grid(row=0, column=2, padx=10, pady=10)
        self.__root.CheckKonsole = CTkCheckBox(self.__root.setupEingabe, text='Konsole', variable=self.checked_Konsole, corner_radius=0)
        self.__root.CheckKonsole.grid(row=0, column=3, pady=10)

        self.__root.setupTasten = CTkFrame(self.__root.FTab3, border_width=1, corner_radius=0, fg_color='transparent')
        self.__root.setupTasten.pack(side='top', fill='x', padx=10, pady=5)
        self.__root.Start_Taste_1_Label = CTkLabel(self.__root.setupTasten, text='Start 1')
        self.__root.Start_Taste_1_Label.grid(row=0, column=0, padx=10, pady=10)
        self.__root.Start_Taste_1 = CTkEntry(self.__root.setupTasten, width=30, corner_radius=0)
        self.__root.Start_Taste_1.grid(row=0, column=1, pady=10)
        self.__root.Stop_Taste_1_Label = CTkLabel(self.__root.setupTasten, text='Stop 1')
        self.__root.Stop_Taste_1_Label.grid(row=0, column=2, padx=10, pady=10)
        self.__root.Stop_Taste_1 = CTkEntry(self.__root.setupTasten, width=30, corner_radius=0)
        self.__root.Stop_Taste_1.grid(row=0, column=3, pady=10)
        self.__root.Start_Taste_2_Label = CTkLabel(self.__root.setupTasten, text='Start 2')
        self.__root.Start_Taste_2_Label.grid(row=0, column=4, padx=10, pady=10)
        self.__root.Start_Taste_2 = CTkEntry(self.__root.setupTasten, width=30, corner_radius=0)
        self.__root.Start_Taste_2.grid(row=0, column=5, pady=10)
        self.__root.Stop_Taste_2_Label = CTkLabel(self.__root.setupTasten, text='Stop 2')
        self.__root.Stop_Taste_2_Label.grid(row=0, column=6, padx=10,pady=10)
        self.__root.Stop_Taste_2 = CTkEntry(self.__root.setupTasten, width=30, corner_radius=0)
        self.__root.Stop_Taste_2.grid(row=0, column=7, pady=10)

        self.__root.Start_Taste_1.insert(0, self.Taste_Start_1)
        self.__root.Stop_Taste_1.insert(0, self.Taste_Stop_1)
        self.__root.Start_Taste_2.insert(0, self.Taste_Start_2)
        self.__root.Stop_Taste_2.insert(0, self.Taste_Stop_2)

        self.__root.setupGPIO = CTkFrame(self.__root.FTab3, border_width=1, corner_radius=0, fg_color='transparent')
        self.__root.setupGPIO.pack(side='top', fill='x', padx=10, pady=5)
        self.__root.Start_GPIO_1_Label = CTkLabel(self.__root.setupGPIO, text='Start 1')
        self.__root.Start_GPIO_1_Label.grid(row=0, column=0, padx=10, pady=10)
        self.__root.Start_GPIO_1 = CTkEntry(self.__root.setupGPIO, width=30, corner_radius=0)
        self.__root.Start_GPIO_1.grid(row=0, column=1, pady=10)
        self.__root.Stop_GPIO_1_Label = CTkLabel(self.__root.setupGPIO, text='Stop 1')
        self.__root.Stop_GPIO_1_Label.grid(row=0, column=2, padx=10, pady=10)
        self.__root.Stop_GPIO_1 = CTkEntry(self.__root.setupGPIO, width=30, corner_radius=0)
        self.__root.Stop_GPIO_1.grid(row=0, column=3, pady=10)
        self.__root.Start_GPIO_2_Label = CTkLabel(self.__root.setupGPIO, text='Start 2')
        self.__root.Start_GPIO_2_Label.grid(row=0, column=4, padx=10, pady=10)
        self.__root.Start_GPIO_2 = CTkEntry(self.__root.setupGPIO, width=30, corner_radius=0)
        self.__root.Start_GPIO_2.grid(row=0, column=5, pady=10)
        self.__root.Stop_GPIO_2_Label = CTkLabel(self.__root.setupGPIO, text='Stop 2')
        self.__root.Stop_GPIO_2_Label.grid(row=0, column=6, padx=10,pady=10)
        self.__root.Stop_GPIO_2 = CTkEntry(self.__root.setupGPIO, width=30, corner_radius=0)
        self.__root.Stop_GPIO_2.grid(row=0, column=7, pady=10)

        self.__root.Start_GPIO_1.insert(0, self.GPIO_Start_1)
        self.__root.Stop_GPIO_1.insert(0, self.GPIO_Stop_1)
        self.__root.Start_GPIO_2.insert(0, self.GPIO_Start_2)
        self.__root.Stop_GPIO_2.insert(0, self.GPIO_Stop_2)

        self.__root.setupStyle = CTkFrame(self.__root.FTab3, border_width=1, corner_radius=0, fg_color='transparent')
        self.__root.setupStyle.pack(side='top', fill='x', padx=10, pady=5)
        self.__root.SGZL = CTkLabel(self.__root.setupStyle, text='Schriftgröße Zeit')
        self.__root.SGZL.grid(row=0, column=0, padx=10, pady=10, sticky=(W))
        self.__root.SGZ = IntSpinbox(self.__root.setupStyle, command=self.updateFontSizeZeit)
        self.__root.SGZ.grid(row=0, column=1, padx=10, pady=10)
        self.__root.SGZ.set(self.AnzeigeFontSizeTime)
        self.__root.SGGL = CTkLabel(self.__root.setupStyle, text='Schriftgröße Gruppe')
        self.__root.SGGL.grid(row=0, column=2, padx=10, pady=10, sticky=(W))
        self.__root.SGG = IntSpinbox(self.__root.setupStyle, command=self.updateFontSizeGruppe)
        self.__root.SGG.grid(row=0, column=3, padx=10, pady=10)
        self.__root.SGG.set(self.AnzeigeFontSizeGroup)

        self.__root.setupAutoAnpassung = CTkFrame(self.__root.FTab3, border_width=1, corner_radius=0, fg_color='transparent')
        self.__root.setupAutoAnpassung.pack(side='top', fill='x', padx=10, pady=5)
        self.__root.LblAnpassungTitel = CTkLabel(self.__root.setupAutoAnpassung, text='Aktuelle Fensterhöhe')
        self.__root.LblAnpassungTitel.grid(row=0, column=0, padx=10, pady=10, sticky=(W))
        self.__root.LblAnpassungWert = CTkLabel(self.__root.setupAutoAnpassung, text=self.screen_height)
        self.__root.LblAnpassungWert.grid(row=0, column=1, padx=10, pady=10, sticky=(W))
        self.__root.LblFaktorZeit = CTkLabel(self.__root.setupAutoAnpassung, text='Faktor Zeit')
        self.__root.LblFaktorZeit.grid(row=1, column=0, padx=10, pady=2, sticky=(W))
        self.__root.SBFaktorZeit = IntSpinbox(self.__root.setupAutoAnpassung)
        self.__root.SBFaktorZeit.grid(row=1, column=1, padx=10, pady=2)
        self.__root.SBFaktorZeit.set(3)
        self.__root.LblFaktorGruppen = CTkLabel(self.__root.setupAutoAnpassung, text='Faktor Gruppen')
        self.__root.LblFaktorGruppen.grid(row=2, column=0, padx=10, pady=2, sticky=(W))
        self.__root.SBFaktorGruppen = IntSpinbox(self.__root.setupAutoAnpassung)
        self.__root.SBFaktorGruppen.grid(row=2, column=1, padx=10, pady=2)
        self.__root.SBFaktorGruppen.set(20)
        self.__root.LblFaktorInfo = CTkLabel(self.__root.setupAutoAnpassung, text='Faktor Info')
        self.__root.LblFaktorInfo.grid(row=3, column=0, padx=10, pady=2, sticky=(W))
        self.__root.SBFaktorInfo = IntSpinbox(self.__root.setupAutoAnpassung)
        self.__root.SBFaktorInfo.grid(row=3, column=1, padx=10, pady=2)
        self.__root.SBFaktorInfo.set(65)
        self.__root.LblFaktorAuswertung = CTkLabel(self.__root.setupAutoAnpassung, text='Faktor Auswertung')
        self.__root.LblFaktorAuswertung.grid(row=4, column=0, padx=10, pady=2, sticky=(W))
        self.__root.SBFaktorAuswertung = IntSpinbox(self.__root.setupAutoAnpassung)
        self.__root.SBFaktorAuswertung.grid(row=4, column=1, padx=10, pady=2)
        self.__root.SBFaktorAuswertung.set(40)
        self.__root.BtnChangeStyle = CTkButton(self.__root.setupAutoAnpassung, text='Anzeige Autoanpassung', corner_radius=0, command=self.changeFontSizeFromWindowSize)
        self.__root.BtnChangeStyle.grid(row=5, column=0, padx=10, pady=10, ipadx=10)

        if self.Testmodus == True:
            self.__root.setupTest = CTkFrame(self.__root.FTab3, border_width=1, corner_radius=0, fg_color='transparent')
            self.__root.setupTest.pack(side='bottom', fill='x', padx=10, pady=5)
            self.__root.LblAnzahlGruppen = CTkLabel(self.__root.setupTest, text='Anzahl Testgruppen')
            self.__root.LblAnzahlGruppen.grid(row=0, column=0, padx=10, pady=10)
            self.__root.SBAnzahlGruppen = IntSpinbox(self.__root.setupTest)
            self.__root.SBAnzahlGruppen.grid(row=0, column=1, padx=10, pady=10)
            self.__root.LblAnzahlDamenGruppen = CTkLabel(self.__root.setupTest, text='Anzahl Testdamengruppen')
            self.__root.LblAnzahlDamenGruppen.grid(row=0, column=2, padx=10, pady=10)
            self.__root.SBAnzahlDamenGruppen = IntSpinbox(self.__root.setupTest)
            self.__root.SBAnzahlDamenGruppen.grid(row=0, column=3, padx=10, pady=10)
            self.__root.BtnAnzahlGruppen = CTkButton(self.__root.setupTest, text='Erstellen', corner_radius=0, command=self.testGruppenErstellen)
            self.__root.BtnAnzahlGruppen.grid(row=0, column=4, padx=10, pady=10)
         
    # Anzeigefenster
    def showAnzeige(self):
        self.anzeige = CTkToplevel()
        self.anzeige.title(self.TitleAnzeige)
        self.anzeige.minsize(700, 400)
        self.anzeige.configure(fg_color=self.AnzeigeBackgroundColor)
        # self.anzeige.iconbitmap(self.FileIcon)

        self.anzeige.frame = CTkFrame(self.anzeige, border_width=0, corner_radius=0, fg_color=self.AnzeigeBackgroundColor)
        self.anzeige.frame.pack(expand=1, side=TOP, fill=BOTH, padx=20, pady=20)

        self.anzeige.G1 = CTkLabel(self.anzeige.frame, text='', anchor='nw', corner_radius=0, text_color=self.AnzeigeGroupColor, fg_color=self.AnzeigeBackgroundColor, font=(self.GlobalFontArt, self.AnzeigeFontSizeGroup))
        self.anzeige.Z1 = CTkLabel(self.anzeige.frame, text='00:00:00', anchor='center', corner_radius=0, text_color=self.AnzeigeTimeColor, fg_color=self.AnzeigeBackgroundColor, font=(self.GlobalFontArt, self.AnzeigeFontSizeTime))
        self.anzeige.Z2 = CTkLabel(self.anzeige.frame, text='00:00:00', anchor='center', corner_radius=0, text_color=self.AnzeigeTimeColor, fg_color=self.AnzeigeBackgroundColor, font=(self.GlobalFontArt, self.AnzeigeFontSizeTime))
        self.anzeige.G2 = CTkLabel(self.anzeige.frame, text='', anchor='ne', corner_radius=0, text_color=self.AnzeigeGroup2Color, fg_color=self.AnzeigeBackgroundColor, font=(self.GlobalFontArt, self.AnzeigeFontSizeGroup))
        
        self.anzeige.ERG = CTkFrame(self.anzeige.frame, border_width=0, corner_radius=0)
        self.anzeige.ERG.pack(expand=1, side=TOP, fill=BOTH)

        self.anzeige.INFO = CTkFrame(self.anzeige.frame, fg_color=self.AnzeigeNextColor, border_width=0, corner_radius=0)
        self.anzeige.INFO.pack(expand=0, side='bottom' , fill='x', pady=20, padx=20)

        self.changeFontSizeFromWindowSize()

    def ladeAuswertungDaten(self):
        for widgets in self.anzeige.ERG.winfo_children():
            widgets.grid_remove()

        f_durchgang = 0

        count_gd = 0
        count_vf = 0
        count_hf = 0
        count_kf = 0
        count_f = 0
        count_dw = 0

        for dg in self.Durchgänge:
            if dg['typ'] == self.TYP_GD and dg['platzierung'] > 0:
                count_gd += 1
            if dg['typ'] == self.TYP_VF and dg['bestzeitinklfehler'] != '':
                count_vf += 1
            if dg['typ'] == self.TYP_HF and dg['bestzeitinklfehler'] != '':
                count_hf += 1
            if dg['typ'] == self.TYP_KF and dg['bestzeitinklfehler'] != '':
                count_kf += 1
            if dg['typ'] == self.TYP_F and dg['bestzeitinklfehler'] != '':
                count_f += 1
            if dg['typ'] == self.TYP_DW and dg['platzierung'] > 0:
                count_dw += 1
        
        if count_gd > 0:
            title = CTkLabel(self.anzeige.ERG, text='GRUNDDURCHGANG', fg_color=self.AnzeigeGroupColor, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            title.grid(row=self.AnzeigeGDStartRow, column=self.AnzeigeGDStartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(30,0))
        
        if count_vf > 0:
            title = CTkLabel(self.anzeige.ERG, text='VIERTELFINALE', fg_color=self.AnzeigeGroupColor, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            title.grid(row=self.AnzeigeVFStartRow, column=self.AnzeigeVFStartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(30,0))
        
        if count_hf > 0:
            title = CTkLabel(self.anzeige.ERG, text='HALBFINALE', fg_color=self.AnzeigeGroupColor, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            title.grid(row=self.AnzeigeHFStartRow, column=self.AnzeigeHFStartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(1,0))
        
        if count_kf > 0:
            title = CTkLabel(self.anzeige.ERG, text='KLEINES FINALE', fg_color=self.AnzeigeGroupColor, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            if self.FinaleInEinerSpalte == False:
                title.grid(row=self.AnzeigeKFStartRow, column=self.AnzeigeKFStartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(30,0))
            else:
                title.grid(row=self.AnzeigeKFStartRow, column=self.AnzeigeKFStartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(1,0))
                
        if count_f > 0:
            title = CTkLabel(self.anzeige.ERG, text='FINALE', fg_color=self.AnzeigeGroupColor, anchor='w', font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            title.grid(row=self.AnzeigeFStartRow, column=self.AnzeigeFStartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(1,0))
        
        if count_dw > 0:
            title = CTkLabel(self.anzeige.ERG, text='DAMENWERTUNG', fg_color=self.AnzeigeGroupColor, anchor='w' , font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
            if self.DamenwertungNebenFinale == True:
                title.grid(row=self.AnzeigeDWStartRow, column=self.AnzeigeDWStartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(30,0))
            else:
                title.grid(row=self.AnzeigeDWStartRow, column=self.AnzeigeDWStartColumn, columnspan=5, sticky=(W+E+N+S), padx=20, pady=(1,0))

        for dg in self.Durchgänge:
            if (dg['typ'] == self.TYP_GD or dg['typ'] == self.TYP_DW) and dg['platzierung'] > 0:
                color = '#ffffff'
                if dg['typ'] == self.TYP_GD:
                    row = dg['platzierung']
                    col = 0
                    if dg['platzierung'] <= 8:
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
            
            if (dg['typ'] == self.TYP_VF or dg['typ'] == self.TYP_HF or dg['typ'] == self.TYP_KF or dg['typ'] == self.TYP_F) and dg['bestzeitinklfehler'] != '':
                color = '#ffffff'
                if f_durchgang == 0 or f_durchgang < dg['dg']:
                    f_durchgang = dg['dg']
                    color = self.GlobalDGBackgroundColor
        
                w = CTkLabel(self.anzeige.ERG, text=dg['wettkampfgruppe'], fg_color=color, font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
                w.grid(row=dg['row'], column=dg['column'], sticky=(W+E+N+S), padx=(20,0), ipady='2')
                time = ''
                if self.ZeigeAlleZeiten == True:
                    if dg['zeit1'] != '':
                        time += '   ' + dg['zeit1'] + ' + ' + str(dg['fehler1'])
                    if dg['zeit2'] != '':
                        time += '   ' + dg['zeit2'] + ' + ' + str(dg['fehler2'])
                
                time += '   BZ_' + dg['bestzeit'] + ' + ' + str(dg['fehlerbest'])
                t = CTkLabel(self.anzeige.ERG, text=time, anchor='w', fg_color=color, font=(self.GlobalFontArt, self.AnzeigeFontSizeAuswertung))
                t.grid(row=dg['row'], column=dg['column']+1, sticky=(W+E+N+S), padx=(0,20), ipady='2')
       
        if len(self.Durchgänge) > 0:
            count = 0
            for dg in self.Durchgänge:
                if dg['typ'] == self.TYP_DW:
                    count += 1

            startRowBestzeit = self.AnzeigeDWStartRow + count + 1
            startColumnBestzeit = self.AnzeigeDWStartColumn + 1

            startRowQualZeit = startRowBestzeit + 3
            startColumnQualzeit = startColumnBestzeit
            

            self.Durchgänge.sort(key=self.sortTimeByBesttime)
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
            
            self.Durchgänge.sort(key=self.sortTime)
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

    def showInfo(self):
        for widgets in self.anzeige.INFO.winfo_children():
            widgets.grid_remove()

        bahnA = ''
        bahnB = ''
        
        dg_select = self.__root.CBDG.get()
        if dg_select != '':
            dg_select = int(dg_select)+1
        else:
            dg_select = 1

        self.Durchgänge.sort(key=self.sortTimeByRow)
        for index, item in enumerate(self.Durchgänge):
            if item['dg'] == dg_select:
                if bahnA == '':
                    bahnA = item['wettkampfgruppe']
                elif bahnB == '':
                    bahnB = item['wettkampfgruppe']
        self.Durchgänge.sort(key=self.sortTime)


        lbl = CTkLabel(self.anzeige.INFO, text='NÄCHSTER \nDURCHGANG', fg_color=self.AnzeigeNextColor, font=(self.GlobalFontArt, self.AnzeigeFontSizeInfo))
        lbl.grid(row=0, column=0, rowspan=2, sticky=(W+E+N+S), padx=(40,0))

        lblA = CTkLabel(self.anzeige.INFO, text='Bahn A', fg_color=self.AnzeigeNextColor, font=(self.GlobalFontArt, self.AnzeigeFontSizeInfo))
        lblA.grid(row=0, column=1, sticky=(W+E+N+S), padx=(40,0))

        lblB = CTkLabel(self.anzeige.INFO, text='Bahn B', fg_color=self.AnzeigeNextColor, font=(self.GlobalFontArt, self.AnzeigeFontSizeInfo))
        lblB.grid(row=0, column=2, sticky=(W+E+N+S), padx=(40,0))

        text = bahnA
        a = CTkLabel(self.anzeige.INFO, text=text, fg_color=self.AnzeigeNextColor, font=(self.GlobalFontArt, self.AnzeigeFontSizeInfo))
        a.grid(row=1, column=1, sticky=(W+E+N+S), padx=(40,0))

        text = bahnB
        b = CTkLabel(self.anzeige.INFO, text=text, fg_color=self.AnzeigeNextColor, font=(self.GlobalFontArt, self.AnzeigeFontSizeInfo))
        b.grid(row=1, column=2, sticky=(W+E+N+S), padx=(40,0))

    # Eingabefenster
    def showChangingWindow(self, event, typ, row, column):
        grp_text = ''
        zeit1_text = ''
        fehler1_text = ''
        zeit2_text = ''
        fehler2_text = ''
        for x in self.Durchgänge:
            if x['typ'] == typ and x['row'] == row and x['column'] == column:
                grp_text = x['wettkampfgruppe']
                zeit1_text = x['zeit1']
                fehler1_text = x['fehler1']
                zeit2_text = x['zeit2']
                fehler2_text = x['fehler2']
        
        if zeit1_text != '':
            self.changewindow = CTkToplevel()
            self.changewindow.title('Änderung')

            self.changewindow.iconphoto(False, self.icon)

            self.changewindow.frame = CTkFrame(self.changewindow)
            self.changewindow.frame.pack(expand=1, side=TOP, fill=BOTH)

            self.changewindow.LZ1 = CTkLabel(self.changewindow.frame, text='Zeit 1')
            self.changewindow.LZ1.grid(row=0, column=1, padx=(0,5), pady=(20,0))

            self.changewindow.LF1 = CTkLabel(self.changewindow.frame, text='Feh. 1')
            self.changewindow.LF1.grid(row=0, column=2, padx=(0,5), pady=(20,0))

            self.changewindow.LZ2 = CTkLabel(self.changewindow.frame, text='Zeit 2')
            self.changewindow.LZ2.grid(row=0, column=3, padx=(0,5), pady=(20,0))

            self.changewindow.LF2 = CTkLabel(self.changewindow.frame, text='Feh. 2')
            self.changewindow.LF2.grid(row=0, column=4, padx=(0,20), pady=(20,0))

            self.changewindow.GRP = CTkLabel(self.changewindow.frame, text=grp_text, anchor='w')
            self.changewindow.GRP.grid(row=1, column=0, sticky=(W), padx=(20,5), pady=(0,20))

            self.changewindow.Z1 = CTkEntry(self.changewindow.frame, width=10)
            self.changewindow.Z1.grid(row=1, column=1, padx=(0,5), pady=(0,20))
            self.changewindow.Z1.insert(0, zeit1_text)
            
            self.changewindow.F1 = CTkEntry(self.changewindow.frame, width=5)
            self.changewindow.F1.grid(row=1, column=2, padx=(0,5), pady=(0,20))
            self.changewindow.F1.insert(0, fehler1_text)

            self.changewindow.Z2 = CTkEntry(self.changewindow.frame, width=10)
            self.changewindow.Z2.grid(row=1, column=3, padx=(0,5), pady=(0,20))
            self.changewindow.Z2.insert(0, zeit2_text)
            
            self.changewindow.F2 = CTkEntry(self.changewindow.frame, width=5)
            self.changewindow.F2.grid(row=1, column=4, padx=(0,20), pady=(0,20))
            self.changewindow.F2.insert(0, fehler2_text)

            self.changeWindowIsAenderungMsg = StringVar()
            self.changewindow.FehlerMsg = CTkLabel(self.changewindow.frame, textvariable=self.changeWindowIsAenderungMsg)
            self.changewindow.FehlerMsg.grid(row=2, column=0, columnspan=5, padx=(0,5), pady=(20,0))

            self.changewindow.BTN = CTkButton(self.changewindow.frame, text='Speichern')
            self.changewindow.BTN.grid(row=3, column=1, columnspan=2, sticky=(W+N+E+S), pady=(0,20))
            self.changewindow.BTN.bind('<Button-1>', lambda event, typ=typ, row=row, column=column:self.closeChangingWindow(event, typ, row, column))

    def closeChangingWindow(self, event, typ, row, column):
        for x in self.Durchgänge:
            if x['typ'] == typ and x['row'] == row and x['column'] == column:
                z1 = self.changewindow.Z1.get()
                f1 = self.changewindow.F1.get()
                z2 = self.changewindow.Z2.get()
                f2 = self.changewindow.F2.get()
                
                msg = ''
                if z1 != '':
                    if self.validate_time(z1) == False:
                        msg += 'Zeit 1 stimmt nicht! \n'
                    if self.validate_number(f1) == False:
                        msg += 'Fehler 1 stimmt nicht! \n'
                if z2 != '':
                    if self.validate_time(z2) == False:
                        msg += 'Zeit 2 stimmt nicht! \n'
                    if self.validate_number(f2) == False:
                        msg += 'Fehler 2 stimmt nicht! \n'

                if msg != '':
                    self.changeWindowIsAenderungMsg.set(msg)
                    return
                else:
                    if z1 != '':
                        f1 = int(f1)
                        x['zeit1'] = z1
                        x['fehler1'] = f1

                        text = str(z1)
                        if f1 > 0:
                            text += ' +' + str(f1)
                        
                        self.zeichneNeueWerte(row, column+1, text, row, column, typ)

                        if z2 == '':
                            x['bestzeit'] = z1
                            x['fehlerbest'] = f1
                            self.zeichneNeueWerte(row, column+3, text, row, column, typ)

                    if z1 != '' and z2 != '':
                        f2 = int(f2)
                        x['zeit2'] = z2
                        x['fehler2'] = f2

                        text2 = str(z2)
                        if f2 > 0:
                            text2 += ' +' + str(f2)
                        self.zeichneNeueWerte(row, column+2, text2, row, column, typ)

                        time1 = self.addiereFehlerZurZeit(z1, f1) 
                        time2 = self.addiereFehlerZurZeit(z2, f2)

                        if self.berechneBestzeit(time1, time2) == 2:
                            x['bestzeit'] = z2
                            x['fehlerbest'] = f2

                            self.zeichneNeueWerte(row, column+3, text2, row, column, typ)

                    self.changewindow.Z1.delete(0, END)
                    self.changewindow.F1.delete(0, END)
                    self.changewindow.Z2.delete(0, END)
                    self.changewindow.F2.delete(0, END)

        self.changewindow.destroy()
        self.bestzeitPlatzierungBerechnen()

    # Validierung
    def isNumber(self, text):
        try:
            float(text)
            return True
        except ValueError:
            return False

    def validate_time(self, test_str):
        pattern_str = r'^\d{2}:\d{2}:\d{2}$'

        if re.match(pattern_str, test_str):
            test = test_str.split(':')
            if int(test[0]) > 59:
                return False
            elif int(test[1]) > 59:
                return False
            else:
                return True
        else: 
            return False

    def validate_number(self, test_str):
        test = test_str.isdigit()  
        return test

    # Functions - Allgemein    
    def ladeKonfiguration(self):
        # Lösche alte Log File
        if os.path.exists(self.LogFile):
            os.remove(self.LogFile)

        # Lade Wettkampfgruppen
        if os.path.exists(self.KonfigGruppenFile):
            anmeldungen_file = open(self.KonfigGruppenFile)
            self.Wettkampfgruppen = json.load(anmeldungen_file)
            anmeldungen_file.close()
        else:
            self.Wettkampfgruppen = []

        # Lade Durchgänge
        if os.path.exists(self.KonfigBewerbFile):
            bewerb_file = open(self.KonfigBewerbFile)
            bewerb_data = json.load(bewerb_file)
            bewerb_file.close()
            self.Durchgänge = bewerb_data['Bewerb']
            self.DGNumbers = bewerb_data['DGNumbers']
        else:
            self.Durchgänge = []
            self.DGNumbers = []

        # Lade Konfiguration (Style, CTkButtonbelegung, ...) 
        setup_file = open(self.KonfigSetupFile)
        setup_data = json.load(setup_file)
        setup_file.close()

        files = setup_data['Files']
        self.FileAngriffsbefehl = self.pfad + files['angriffsbefehl']
        self.FileStopp = self.pfad + files['stopp']
        self.FileIcon = self.pfad + files['icon']
        self.FileIconDelete = self.pfad + files['iconDelete']
        
        Buttons = setup_data['Buttons']
        self.GPIO_Start_1 = Buttons['GPIO_Start_1']
        self.GPIO_Stop_1 = Buttons['GPIO_Stop_1']
        self.GPIO_Start_2 = Buttons['GPIO_Start_2']
        self.GPIO_Stop_2 = Buttons['GPIO_Stop_2']
        self.Taste_Start_1 = Buttons['Taste_Start_1']
        self.Taste_Stop_1 = Buttons['Taste_Stop_1']
        self.Taste_Start_2 = Buttons['Taste_Start_2']
        self.Taste_Stop_2 = Buttons['Taste_Stop_2']

        style = setup_data['Style']
        self.GlobalFontArt = style['GlobalFontArt']
        self.GlobalFontSizeText = style['GlobalFontSizeText']
        self.GlobalFontSizeTitle = style['GlobalFontSizeTitle']
        self.GlobalDGBackgroundColor = style['GlobalDGBackgroundColor']

        self.AnzeigeFontSizeGroup = style['AnzeigeFontSizeGroup']
        self.AnzeigeFontSizeTime = style['AnzeigeFontSizeTime']
        self.AnzeigeFontSizeInfo = style['AnzeigeFontSizeInfo']
        self.AnzeigeFontSizeAuswertung = style['AnzeigeFontSizeAuswertung']
        self.AnzeigeBackgroundColor = style['AnzeigeBackgroundColor']
        self.AnzeigeGroupColor = style['AnzeigeGroupColor']
        self.AnzeigeGroup2Color = style['AnzeigeGroup2Color']
        self.AnzeigeTimeColor = style['AnzeigeTimeColor']
        self.AnzeigeNextColor = style['AnzeigeNextColor']

        setup = setup_data['Setup']
        self.Title = setup['Title']
        self.TitleAnzeige = setup['TitleAnzeige']
        self.FinaleInEinerSpalte = setup['FinaleInEinerSpalte']
        self.DamenwertungNebenFinale = setup['DamenwertungNebenFinale']
        self.ZeigeAlleZeiten = setup['ZeigeAlleZeiten']
        self.Testmodus = setup['Testmodus']

        # Spalten und Reihen Konfig nach dem Setup anpassen
        if self.FinaleInEinerSpalte == False:
            self.AnzeigeVFStartRow = 0
            self.AnzeigeVFStartColumn = 8
            self.AnzeigeHFStartRow = 10
            self.AnzeigeHFStartColumn = 8
            self.AnzeigeKFStartRow = 0
            self.AnzeigeKFStartColumn = 17
            self.AnzeigeFStartRow = 4
            self.AnzeigeFStartColumn = 17
            self.AnzeigeDWStartRow = 8
            self.AnzeigeDWStartColumn = 17
        
        if self.DamenwertungNebenFinale == True:
            self.AnzeigeDWStartRow = 0
            self.AnzeigeDWStartColumn = 26

        if self.FinaleInEinerSpalte == False or self.DamenwertungNebenFinale == True:
            self.changeRowAndColumnInDurchgaenge()

    def exportAnmeldungKonfig(self):
        new_list = self.Wettkampfgruppen
        with open(self.KonfigGruppenFile, "w") as outfile:
            json.dump(new_list, outfile)
    
    def exportBewerbKonfig(self):
        new_dict = {
            'Bewerb': self.Durchgänge,
            'DGNumbers': self.DGNumbers
        }
        with open(self.KonfigBewerbFile, "w") as outfile:
            json.dump(new_dict, outfile)

    def changeRowAndColumnInDurchgaenge(self):
        if len(self.Durchgänge) > 0:
            row_kf = self.AnzeigeKFStartRow + 1
            col_kf = self.AnzeigeKFStartColumn + 1
            row_f = self.AnzeigeFStartRow + 1
            col_f = self.AnzeigeFStartColumn + 1
            row_dw = self.AnzeigeDWStartRow + 1
            col_dw = self.AnzeigeDWStartColumn + 1
            self.Durchgänge.sort(key=self.sortTimeByRow)
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
            
            self.Durchgänge.sort(key=self.sortTime)
    
    def sortTime(self, timeList):
        if timeList['typ'] == self.TYP_GD  or timeList['typ'] == self.TYP_DW:
            if timeList['bestzeitinklfehler'] == '':
                return timeList['typ'], '59', '59', '99'
            else:
                split_up = timeList['bestzeitinklfehler'].split(':')
                return timeList['typ'], split_up[0], split_up[1], split_up[2]
        else:
            if timeList['bestzeitinklfehler'] == '':
                return timeList['typ'], timeList['dg'], '59', '59', '99'
            else:
                split_up = timeList['bestzeitinklfehler'].split(':')
                return timeList['typ'], timeList['dg'], split_up[0], split_up[1], split_up[2]
    
    def sortTimeByRow(self, timeList):
        return timeList['typ'], timeList['row']

    def sortTimeByBesttime(self, timeList):
        if timeList['bestzeit'] != '':
            return self.addiereFehlerZurZeit(timeList['bestzeit'],str(timeList['fehlerbest']))
        else:
            return '59:59:99'
    
    def writeKonsole(self, text):
        if (self.checked_Konsole.get() == True):
            f = open(self.LogFile, "a")
            f.write(time.strftime('%X') + ' ' + text + '\n')
            f.close()

    def wechselAnsichtZurZeit(self):
        self.anzeige.ERG.pack_forget()
        self.anzeige.G1.pack(expand=0, side=TOP, fill=X)
        self.anzeige.Z1.pack(expand=1, side=TOP, fill=BOTH)
        self.anzeige.Z2.pack(expand=1, side=TOP, fill=BOTH)
        self.anzeige.G2.pack(expand=0, side=BOTTOM, fill=X)
        self.showInfo()   

    def wechselAnsichtZurAuswertung(self):
        self.anzeige.G1.pack_forget()
        self.anzeige.Z1.pack_forget()
        self.anzeige.Z2.pack_forget()
        self.anzeige.G2.pack_forget()
        self.anzeige.ERG.pack(expand=1, side=TOP, fill=BOTH)
        self.ladeAuswertungDaten()  
        self.showInfo()   

    def playSound(self, file):
        self.writeKonsole('Ein Sound wurde wiedergegeben!')
        sound = pygame.mixer.Sound(file)
        sound.play()

    def testGruppenErstellen(self):
        anzahl = self.__root.SBAnzahlGruppen.get()
        damenAnzahl = self.__root.SBAnzahlDamenGruppen.get()
        
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

        self.zeichneAngemeldeteGruppen()
        self.__root.TabView.set(self.NAME_TAB1)

    def changeColorFromButton(self, button):
        source_fg_color = self.__root.BtnUebernehmen.cget('fg_color')
        disabled_fg_color = 'transparent'
        state = button.cget('state')

        mode = get_appearance_mode()

        if mode == 'Light' and isinstance(source_fg_color, list):
            source_fg_color = source_fg_color[0]
        elif mode == 'Dark' and isinstance(source_fg_color, list):
            source_fg_color = source_fg_color[1]


        if state == 'disabled':
            button.configure(fg_color=disabled_fg_color)
        else:
            button.configure(fg_color=source_fg_color)
    
    def changeColorFromButtonSummary(self):
        self.changeColorFromButton(self.__root.BtnVorherigerDG)
        self.changeColorFromButton(self.__root.BtnNaechsterDG)
        self.changeColorFromButton(self.__root.BtnStart)
        self.changeColorFromButton(self.__root.BtnAllesStop)
        self.changeColorFromButton(self.__root.BtnWechsel)
        self.changeColorFromButton(self.__root.BtnAnsichtWechseln)
        self.changeColorFromButton(self.__root.BtnZeitUebertragen)
        self.changeColorFromButton(self.__root.BtnStopReset)

    # def center_window(window):
    #     window.update_idletasks()
    #     screen_width = window.winfo_screenwidth()
    #     screen_height = window.winfo_screenheight()
    #     x = (screen_width) // 2
    #     y = (screen_height) // 2
    #     window.geometry(f"+{x}+{y}")

    # Functions - Tab Anmeldung
    def addWettkampfgruppe(self, event=None):
        name = self.__root.Entry.get()

        if len(name) == 0:
            messagebox.showerror('Fehlermeldung', 'Bitte einen Namen eingeben!')
            return None
        
        count = 0
        for i in self.Wettkampfgruppen:
            if i['gruppenname'] == name:
                count += 1
        if count > 0:
            messagebox.showerror('Fehlermeldung', 'Gruppenname bereits vorhanden!')
            return None
        
        if len(self.Wettkampfgruppen) >= 30:
            messagebox.showerror('Fehlermeldung', 'Maximal 30 Gruppen erlaubt!')
            return None

        val= {
            'gruppenname': name,
            'reihenfolge': '',
            'damenwertung': False
            }
        self.Wettkampfgruppen.append(val)
        self.__root.Entry.delete(0, END)
        self.__root.Entry.insert(0, '')
        self.zeichneAngemeldeteGruppen()
        self.writeKonsole(name + ' wurde hinzugefügt!')

    def zeichneAngemeldeteGruppen(self):
        for widgets in self.__root.LfReihenfolge.winfo_children():
            widgets.grid_remove()
        
        if len(self.Wettkampfgruppen) == 0:
            self.__root.LNoGroups = CTkLabel(self.__root.LfReihenfolge, text='Keine Gruppen angemeldet!')
            self.__root.LNoGroups.grid(row=0, column=0, sticky=(W), padx=10, pady=5)
        else:
            w = CTkLabel(self.__root.LfReihenfolge, text='Gruppenname')
            w.grid(row=0, column=0, sticky=(W), padx=10, pady='2')

            e = CTkLabel(self.__root.LfReihenfolge, text='Reihenf.')
            e.grid(row=0, column=1, sticky=(W), padx=10, pady='2')

            cb = CTkLabel(self.__root.LfReihenfolge, text='Damen')
            cb.grid(row=0, column=2, sticky=(W), padx=10, pady='2')

            x = CTkLabel(self.__root.LfReihenfolge, text='#')
            x.grid(row=0, column=3, sticky=(W), padx=10, pady='2')

        for index, i in enumerate(self.Wettkampfgruppen):
            row = index + 1
            gruppenname = i['gruppenname']
            reihenfolge = i['reihenfolge']
            damenwertung = 'NEIN'
            if i['damenwertung'] ==True:
                damenwertung = 'JA'

            w = CTkLabel(self.__root.LfReihenfolge, text=gruppenname)
            w.grid(row=row, column=0, sticky=(W), padx=10, pady='2')

            e = CTkEntry(self.__root.LfReihenfolge, width=50, justify = 'center')
            e.grid(row=row, column=1, sticky=(W), padx=10, pady='2')
            e.insert(0, reihenfolge)
            e.bind('<KeyRelease>', lambda event, name=gruppenname: self.reihenfolgeSpeichern(event, name))

            cb = CTkLabel(self.__root.LfReihenfolge, text=damenwertung)
            cb.grid(row=row, column=2, sticky=(W+E+N+S), padx=10, pady='2')            
            cb.bind('<Button-1>', lambda event,  name=gruppenname, value=i['damenwertung']: self.eintragDamenwertung(event, name, value))

            x = CTkLabel(self.__root.LfReihenfolge, text='', image=self.iconDelete)
            x.grid(row=row, column=3, sticky=(W), padx=10, pady='2')
            x.bind('<Button-1>', lambda event, name=gruppenname: self.deleteWettkampfgruppe(event, name))

    def reihenfolgeSpeichern(self, event, name):
        reihenfolge = event.widget.get()
        is_number = self.isNumber(reihenfolge)
        
        for i in self.Wettkampfgruppen:
            if i['gruppenname'] == name:
                if is_number == True:
                    i['reihenfolge'] = reihenfolge
                    self.writeKonsole(name + ' hat die Reihenfolgenposition von ' + reihenfolge)
                else:
                    i['reihenfolge'] = reihenfolge[:-1]
                    self.writeKonsole(name + ' hat die Reihenfolgenposition von ' + reihenfolge[:-1])
        
        self.zeichneAngemeldeteGruppen()

    def eintragDamenwertung(self, event, name, value):
        for i in self.Wettkampfgruppen:
            if i['gruppenname'] == name:
                if value == True:
                    i['damenwertung'] = False
                    self.writeKonsole(name + ' aus der Damenwertung entfernt')
                elif value == False:
                    i['damenwertung'] = True
                    self.writeKonsole(name + ' zur Damenwertung hinzugefügt')
        
        self.zeichneAngemeldeteGruppen()

    def deleteWettkampfgruppe(self, event, name):
        for i in self.Wettkampfgruppen:
            if i['gruppenname'] == name:
                self.Wettkampfgruppen.remove(i)
        self.zeichneAngemeldeteGruppen()
        self.writeKonsole(name + ' wurde gelöscht!')

    def uebernahmeGruppen(self, vonKonfig):
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
            self.wechselAnsichtZurAuswertung()
            self.exportAnmeldungKonfig()
            self.checked_Bahn_1.set(False)
            self.checked_Bahn_2.set(False)
            self.switchBahn1State()
            self.switchBahn2State()
            self.reset() 
            self.__root.BtnStart.configure(state=DISABLED)
            self.__root.BtnAllesStop.configure(state=DISABLED)
            self.__root.BtnWechsel.configure(state=DISABLED)
            self.__root.BtnZeitUebertragen.configure(state=DISABLED)
            self.__root.BtnStopReset .configure(state=DISABLED)
            self.changeColorFromButtonSummary()

            self.__root.dg.pack_forget()
            self.__root.dg = CTkScrollableFrame(self.__root.FTab2, border_width=0, fg_color='transparent')
            self.__root.dg.pack(expand=1, side='bottom', fill='both', padx=10, pady=10, ipady=10)
            self.__root.zeitnehmung.pack_forget()
            self.__root.zeitnehmung.pack(side='left', padx=5)
            self.__root.LfBahnen.pack_forget()
            self.__root.LfBahnen.pack(side='left', padx=10)
            self.__root.korrektur.pack_forget()
            self.__root.korrektur.pack(side='left', padx=5)
            mixedWertung = []
            damenWertung = []
            damen_vorhanden = False

            for grp in self.Wettkampfgruppen:
                if grp['reihenfolge'] == '':
                    grp['reihenfolge'] = '0'
                if grp['damenwertung'] == True:
                    damenWertung.append(grp)
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

            space = CTkLabel(self.__root.dg, text='')
            space.grid(row=0, column=7, rowspan=anzahl_gruppen, sticky=(W+E+N+S), padx=(5,0), ipadx=20)

            if self.FinaleInEinerSpalte == False:
                space = CTkLabel(self.__root.dg, text='')
                space.grid(row=0, column=16, rowspan=anzahl_gruppen, sticky=(W+E+N+S), padx=(5,0), ipadx=20)
            
            if self.DamenwertungNebenFinale == True:
                space = CTkLabel(self.__root.dg, text='')
                space.grid(row=0, column=25, rowspan=anzahl_gruppen, sticky=(W+E+N+S), padx=(5,0), ipadx=20)
                
            if len(damenWertung) > 0:
                damen_vorhanden = True

            self.zeichneGrundansicht(damen_vorhanden, new_Array) 

            self.__root.TabView.set(self.NAME_TAB2)
            sorted_MixedWertung = sorted(mixedWertung, key=lambda x : int(x['reihenfolge']), reverse=False)
            sorted_DamenWertung = sorted(damenWertung, key=lambda x : int(x['reihenfolge']), reverse=False)

            for index, item in enumerate(sorted_MixedWertung):
                row = self.AnzeigeGDStartRow + int(index) + 1
                col1 = self.AnzeigeGDStartColumn + 1
                txt = item['reihenfolge'] + ' - ' + item['gruppenname']
                self.zeichneNeueWerte(row, col1, txt, row, col1, self.TYP_GD)

                for x in self.Durchgänge:
                    if x['typ'] == self.TYP_GD  and x['row'] == row and x['column'] == col1:
                        x['wettkampfgruppe'] = item['gruppenname']

            for x in self.Durchgänge:
                if x['zeit1'] != '':
                    text = str(x['zeit1'])
                    if x['fehler1'] > 0:
                        text += ' +' + str(x['fehler1'])
                    self.zeichneNeueWerte(x['row'], x['column']+1, text, x['row'], x['column'], x['typ'])
                if x['zeit2'] != '':
                    text = str(x['zeit2'])
                    if x['fehler2'] > 0:
                        text += ' +' + str(x['fehler2'])
                    self.zeichneNeueWerte(x['row'], x['column']+2, text, x['row'], x['column'], x['typ'])
                if x['bestzeit'] != '':
                    text = str(x['bestzeit'])
                    if x['fehlerbest'] > 0:
                        text += ' +' + str(x['fehlerbest'])
                    self.zeichneNeueWerte(x['row'], x['column']+3, text, x['row'], x['column'], x['typ'])

            self.writeKonsole(str(len(mixedWertung)) + ' Gruppen wurden übernommen!')

            for index, item in enumerate(sorted_DamenWertung):
                row = self.AnzeigeDWStartRow + int(index) + 1
                col1 = self.AnzeigeDWStartColumn + 1
                txt = item['reihenfolge'] + ' - ' + item['gruppenname']
                self.zeichneNeueWerte(row, col1, txt, row, col1, self.TYP_DW)

                
                for x in self.Durchgänge:
                    if x['typ'] == self.TYP_DW and x['row'] == row and x['column'] == col1:
                        x['wettkampfgruppe'] = item['gruppenname']

            self.writeKonsole(str(len(damenWertung)) + ' Damengruppen wurden übernommen!')

            self.changeRowAndColumnInDurchgaenge()
            self.bestzeitPlatzierungBerechnen()
            self.ladeZeitnehmungsDaten()

    # Functions - Tab Übersicht - Zeitnehmung
    def zeichneGrundansicht(self, damenwertung, new_Array):
        txt = ''
        time = ''
        rh = ''
        self.DurchgangNummer = 1
        self.zeichneZeitTable('Grunddurchgang (Z1/Z2/B)', self.AnzeigeGDStartColumn, self.AnzeigeGDStartRow, txt, time, rh, self.AnzahlGrunddurchgänge, True, self.TYP_GD, new_Array)
        self.zeichneZeitTable('Viertelfinale (Z1/Z2/B)', self.AnzeigeVFStartColumn, self.AnzeigeVFStartRow, txt, time, rh, 8, True, self.TYP_VF, new_Array)
        self.zeichneZeitTable('Halbfinale (Z1/Z2/B)', self.AnzeigeHFStartColumn, self.AnzeigeHFStartRow, txt, time, rh, 4, True, self.TYP_HF, new_Array)
        self.zeichneZeitTable('Kleines Finale (Z1/Z2/B)', self.AnzeigeKFStartColumn, self.AnzeigeKFStartRow, txt, time, rh, 2, True, self.TYP_KF, new_Array)
        self.zeichneZeitTable('Finale (Z1/Z2/B)', self.AnzeigeFStartColumn, self.AnzeigeFStartRow, txt, time, rh, 2, True, self.TYP_F, new_Array)
        if damenwertung == True:
            self.zeichneZeitTable('Damenwertung (Z1/Z2/B)', self.AnzeigeDWStartColumn, self.AnzeigeDWStartRow, txt, time, rh, self.AnzahlDamendurchgänge, True, self.TYP_DW, new_Array)
        self.__root.CBDG.configure(values=self.DGNumbers)
        self.__root.CBDG.set('1')
        
    def zeichneZeitTable(self, title, startcolumn, startrow, gruppe_txt, time_txt, rh_text, anzahl_gruppen, show_rh, typ, new_Array):
        title = CTkLabel(self.__root.dg, text=title, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), anchor='w')
        title.grid(row=startrow, column=startcolumn, columnspan=5, sticky=(W+E+N+S), padx=(5,0))
        col1 = startcolumn + 1
        col2 = startcolumn + 2
        col3 = startcolumn + 3
        col4 = startcolumn + 4
        col5 = startcolumn + 5
        hinweis_text = ''
        for i in range(anzahl_gruppen):
            if typ == self.TYP_VF :
                vf_index = i + 1
                if vf_index == 1: 
                    hinweis_text = 'GD_1'
                elif vf_index == 2: 
                    hinweis_text = 'GD_8' 
                elif vf_index == 3: 
                    hinweis_text = 'GD_2' 
                elif vf_index == 4: 
                    hinweis_text = 'GD_7' 
                elif vf_index == 5: 
                    hinweis_text = 'GD_3' 
                elif vf_index == 6: 
                    hinweis_text = 'GD_6' 
                elif vf_index == 7: 
                    hinweis_text = 'GD_4' 
                elif vf_index == 8: 
                    hinweis_text = 'GD_5' 
            elif typ == self.TYP_HF :
                hf_index = i + 1
                hinweis_text = 'VF_' + str(hf_index)
            elif typ == self.TYP_KF :
                kf_index = i + 1
                hinweis_text = 'KF_' + str(kf_index)
            elif typ == self.TYP_F :
                f_index = i + 1
                hinweis_text = 'F_' + str(f_index)
            else:
                hinweis_text=''
            row = startrow + i + 1
            durchgang = CTkLabel(self.__root.dg, text=self.DurchgangNummer, fg_color=self.GlobalDGBackgroundColor, anchor='center')
            text = CTkLabel(self.__root.dg, text=gruppe_txt)
            time1 = CTkLabel(self.__root.dg, text=time_txt, anchor='e')
            time2 = CTkLabel(self.__root.dg, text=time_txt, anchor='e')
            time3 = CTkLabel(self.__root.dg, text=time_txt, anchor='e')
            if show_rh == True:
                lrh = CTkLabel(self.__root.dg, text=rh_text, anchor='center')
            rh = i + 1
            if rh % 2:
                if new_Array == True:
                    self.konvertiereArray(self.DurchgangNummer, gruppe_txt, typ, row, col1, hinweis_text)
                durchgang.grid(row=row, column=startcolumn, rowspan=2, sticky=(W+E+N+S), padx=(5,0), pady=(1,0), ipadx=5)
                text.grid(row=row, column=col1, sticky=(W), pady=(1,0), ipady='2', ipadx=10)
                time1.grid(row=row, column=col2, sticky=(W), pady=(1,0), ipady='2', ipadx=10)
                time2.grid(row=row, column=col3, sticky=(W), pady=(1,0), ipady='2', ipadx=10)
                time3.grid(row=row, column=col4, sticky=(W), pady=(1,0), ipady='2', ipadx=10)
                if show_rh == True:
                    lrh.grid(row=row, column=col5, sticky=(W), pady=(1,0), ipady='2', ipadx=10)
                self.DurchgangNummer += 1
            else:
                if new_Array == True:
                    self.konvertiereArray(self.DurchgangNummer-1, gruppe_txt, typ, row, col1, hinweis_text)    
                text.grid(row=row, column=col1, sticky=(W), pady='0', ipady='2', ipadx=10) 
                time1.grid(row=row, column=col2, sticky=(W), pady='0', ipady='2', ipadx=10) 
                time2.grid(row=row, column=col3, sticky=(W), pady='0', ipady='2', ipadx=10)
                time3.grid(row=row, column=col4, sticky=(W), pady='0', ipady='2', ipadx=10)
                if show_rh == True:
                    lrh.grid(row=row, column=col5, sticky=(W), pady='0', ipady='2', ipadx=10)
                
    def konvertiereArray(self, dg_nummer, wettkampfgruppe, typ, row, column, hinweis):
        if str(dg_nummer) not in self.DGNumbers:
            self.DGNumbers.append(str(dg_nummer))
        
        groupdict = {
            'wettkampfgruppe': wettkampfgruppe,
            'hinweis': hinweis,             # Hinweis für Platzierungsposition zb GD_1
            'platzierung': 0,
            'zeit1': '',
            'fehler1': 0,
            'zeit2': '',
            'fehler2': 0,
            'bestzeit': '',
            'fehlerbest': 0,
            'bestzeitinklfehler':'',
            'typ': typ,                     # Art  (Grunddurchgang, Viertelfinale, ...)
            'dg': dg_nummer,                # Nummer des Durchganges
            'row': row,                     # Reihe von Name
            'column': column,               # Spalte von Name           
        }
        self.Durchgänge.append(groupdict)

    def anzeigeUmschalten(self):
        if self.Status_Anzeige == False:
            self.Status_Anzeige = True
            self.wechselAnsichtZurZeit()
        else:
            self.Status_Anzeige = False
            self.wechselAnsichtZurAuswertung()

    def bahnWechsel(self):
        self.werteInAnsichtUebertragen()

        bahnA = self.__root.G1.cget('text')
        bahnB = self.__root.G2.cget('text')

        bahnAId = self.id_time_1
        bahnBId = self.id_time_2

        self.__root.G1.configure(text=bahnB)
        self.id_time_1 = bahnBId
        self.__root.G2.configure(text=bahnA)

        self.anzeige.G1.configure(text=bahnB)
        self.id_time_2 = bahnAId
        self.anzeige.G2.configure(text=bahnA)
        
        self.__root.BtnStart.configure(state=NORMAL)
        self.changeColorFromButtonSummary()
        
        self.checked_Bahn_1.set(False)
        self.checked_Bahn_2.set(False)
        self.switchBahn1State()
        self.switchBahn2State()

        if self.__root.G1.cget('text') != '...':
            self.checked_Bahn_1.set(True)
            self.switchBahn1State()
        if self.__root.G2.cget('text') != '...':
            self.checked_Bahn_2.set(True)
            self.switchBahn2State()

        self.writeKonsole('Die Bahnen wurden gewechselt!')
    
    def werteInAnsichtUebertragen(self):
        self.__root.CBDG.focus_set()
        dg_select = self.__root.CBDG.get()

        if self.id_time_1  != '' and self.ZeitUebertragen == False:
            zeit1A = self.__root.T1.cget('text')
            fehler1A = self.__root.F1.get()
            if fehler1A == '':
                fehler1A == '0'
            id1A = self.id_time_1.split('#')
            typ1A = id1A[1]
            row1A = int(id1A[2])
            column1A = int(id1A[3])
            self.zeitUebertragen(typ1A, row1A, column1A, zeit1A, fehler1A, int(dg_select))

        if self.id_time_2  != '' and self.ZeitUebertragen == False:
            zeit2A = self.__root.T2.cget('text')
            fehler2A = self.__root.F2.get()
            if fehler2A == '':
                fehler2A == '0'
            id2A = self.id_time_2.split('#')
            typ2A = id2A[1]
            row2A = int(id2A[2])
            column2A = int(id2A[3])
            self.zeitUebertragen(typ2A, row2A, column2A, zeit2A, fehler2A, int(dg_select))
        
        if self.ZeitUebertragen == False:
            self.ZeitUebertragen = True

        self.__root.T1.configure(text='00:00:00')
        self.__root.T2.configure(text='00:00:00')
        self.__root.F1.delete(0, END)
        self.__root.F2.delete(0, END)
        self.anzeige.Z1.configure(text='00:00:00')
        self.anzeige.Z2.configure(text='00:00:00')

        self.bestzeitPlatzierungBerechnen()

    def zeitUebertragen(self, typ, row, column, zeit, fehler, dg):
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
                    self.zeichneNeueWerte(row, column+1, text, row, column, typ)
                    self.zeichneNeueWerte(row, column+3, text, row, column, typ)
                elif x['zeit2'] == '':
                    x['zeit2'] = zeit
                    x['fehler2'] = fehler
                    text = str(zeit)
                    if fehler > 0:
                        text += ' +' + str(fehler)
                    self.zeichneNeueWerte(row, column+2, text, row, column, typ)
                    
                    time1 = self.addiereFehlerZurZeit(x['zeit1'], x['fehler1']) 
                    time2 = self.addiereFehlerZurZeit(zeit, fehler)

                    if self.berechneBestzeit(time1, time2) == 2:
                        x['bestzeit'] = zeit
                        x['fehlerbest'] = fehler
                        self.zeichneNeueWerte(row, column+3, text, row, column, typ)
    
    def berechneBestzeit(self, zeit1, zeit2):
        t1 = zeit1.split(':')
        t1_minute = int(t1[0])
        t1_sekunden = int(t1[1])
        t1_milisekunden = int(t1[2])
        tf1 = (((t1_minute * 60) + t1_sekunden) * 100) + t1_milisekunden

        t2 = zeit2.split(':')
        t2_minute = int(t2[0])
        t2_sekunden = int(t2[1])
        t2_milisekunden = int(t2[2])
        tf2 = (((t2_minute * 60) + t2_sekunden) * 100) + t2_milisekunden

        if tf1 < tf2:
            return 1
        elif tf1 >= tf2:
            return 2
        
    def addiereFehlerZurZeit(self, zeit, fehler):
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

    def bestzeitPlatzierungBerechnen(self):
        for dg in self.Durchgänge:
            if dg['bestzeit'] != '':
                dg['bestzeitinklfehler'] = self.addiereFehlerZurZeit(dg['bestzeit'], dg['fehlerbest'])
            else:
                dg['bestzeitinklfehler'] = ''

        self.Durchgänge.sort(key=self.sortTime)

        vf_durchgang = 0
        vf_hinweis = ''
        hf_durchgang = 0
        hf_hinweis = ''
        dw_platzierung_neu = 1
        
        for index, item in enumerate(self.Durchgänge):
            if item['typ'] == self.TYP_GD and item['bestzeitinklfehler'] != '':
                platzierung_neu = index + 1
                item['platzierung'] = platzierung_neu
                self.zeichneNeueWerte(item['row'], item['column'] + 4, platzierung_neu, item['row'], item['column'], item['typ'])
        
                if item['platzierung'] >= 1 and item['platzierung'] <= 8:
                    for dg in self.Durchgänge:
                        suchtext = 'GD_' + str(item['platzierung'])
                        if dg['hinweis'] == suchtext:
                            dg['wettkampfgruppe'] = item['wettkampfgruppe']
                            self.zeichneNeueWerte(dg['row'], dg['column'], item['wettkampfgruppe'], dg['row'], dg['column'], dg['typ'])
        
            if item['typ'] == self.TYP_VF and item['bestzeitinklfehler'] != '':
                if vf_durchgang == 0 or vf_durchgang < item['dg']:
                    vf_durchgang = item['dg']
                    if item['hinweis'] == 'GD_1' or item['hinweis'] == 'GD_8':
                        vf_hinweis = 'VF_1'
                    elif item['hinweis'] == 'GD_2' or item['hinweis'] == 'GD_7':
                        vf_hinweis = 'VF_2'
                    elif item['hinweis']  == 'GD_3' or item['hinweis'] == 'GD_6':
                        vf_hinweis = 'VF_3'
                    elif item['hinweis'] == 'GD_4' or item['hinweis'] == 'GD_5':
                        vf_hinweis = 'VF_4'
                    for dg in self.Durchgänge:
                        if dg['hinweis'] == vf_hinweis:
                            dg['wettkampfgruppe'] = item['wettkampfgruppe']
                            self.zeichneNeueWerte(dg['row'], dg['column'], item['wettkampfgruppe'], dg['row'], dg['column'], dg['typ'])
            
            if item['typ'] == self.TYP_HF and item['bestzeitinklfehler'] != '':
                if hf_durchgang == 0 or hf_durchgang < item['dg']:
                    hf_durchgang = item['dg']
                    if item['hinweis'] == 'VF_1' or item['hinweis'] == 'VF_2':
                        hf_hinweis = 'F_1'
                    elif item['hinweis'] == 'VF_3' or item['hinweis'] == 'VF_4':
                        hf_hinweis = 'F_2'
                    for dg in self.Durchgänge:
                        if dg['hinweis'] == hf_hinweis:
                            dg['wettkampfgruppe'] = item['wettkampfgruppe']
                            self.zeichneNeueWerte(dg['row'], dg['column'], item['wettkampfgruppe'], dg['row'], dg['column'], dg['typ'])
                elif hf_durchgang == item['dg']:
                    if item['hinweis'] == 'VF_1' or item['hinweis'] == 'VF_2':
                        hf_hinweis = 'KF_1'
                    elif item['hinweis'] == 'VF_3' or item['hinweis'] == 'VF_4':
                        hf_hinweis = 'KF_2'
                    for dg in self.Durchgänge:
                        if dg['hinweis'] == hf_hinweis:
                            dg['wettkampfgruppe'] = item['wettkampfgruppe']
                            self.zeichneNeueWerte(dg['row'], dg['column'], item['wettkampfgruppe'], dg['row'], dg['column'], dg['typ'])

            if item['typ'] == self.TYP_DW and item['bestzeitinklfehler'] != '':
                item['platzierung'] = dw_platzierung_neu
                self.zeichneNeueWerte(item['row'], item['column'] + 4, dw_platzierung_neu, dg['row'], dg['column'], dg['typ'])  
                dw_platzierung_neu += 1

    def zeichneNeueWerte(self, row, column, text, id_row, id_col, id_typ):
        for label in self.__root.dg.grid_slaves(row=row, column=column):
            label.configure(text=text)
            if row == id_row and column == id_col:
                label.bind('<Button-1>', lambda event, typ=id_typ, row=id_row, column=id_col: self.showChangingWindow(event, typ, row, column))
        
        self.exportBewerbKonfig()

    def ladeZeitnehmungsDaten(self, event=None):
        self.wechselAnsichtZurZeit()
        self.checked_Bahn_1.set(False)
        self.checked_Bahn_2.set(False)
        self.switchBahn1State()
        self.switchBahn2State()
        self.__root.G1.configure(text='...')
        self.__root.G2.configure(text='...')
        self.__root.T1.configure(text='00:00:00')
        self.__root.T2.configure(text='00:00:00')
        self.__root.F1.delete(0, END)
        self.__root.F2.delete(0, END)
        self.id_time_1 = ''
        self.id_time_2 = ''
        check_time = False
        count = 1
        dg_select = self.__root.CBDG.get()
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
            self.__root.BtnVorherigerDG.configure(state=DISABLED)
            self.__root.BtnNaechsterDG.configure(state=NORMAL)

        if dg_select > min_dg and dg_select < max_dg:
            self.__root.BtnVorherigerDG.configure(state=NORMAL)
            self.__root.BtnNaechsterDG.configure(state=NORMAL)
        
        if dg_select == max_dg:
            self.__root.BtnVorherigerDG.configure(state=NORMAL)
            self.__root.BtnNaechsterDG.configure(state=DISABLED)
        
        self.changeColorFromButtonSummary()

        for dg in self.Durchgänge:
            if dg['dg'] == dg_select:
                if count == 1 and dg['wettkampfgruppe'] != '...' and dg['wettkampfgruppe'] != '':
                    self.checked_Bahn_1.set(True)
                    self.switchBahn1State()
                    self.__root.G1.configure(text=dg['wettkampfgruppe'])
                    self.anzeige.G1.configure(text=dg['wettkampfgruppe'])
                    self.id_time_1 = 'typ.row.column#' + str(dg['typ']) + '#' + str(dg['row']) + '#' + str(dg['column'])
                    if dg['zeit1'] != '' and dg['zeit2'] != '':
                        check_time = True
                elif count == 2 and dg['wettkampfgruppe'] != '...' and dg['wettkampfgruppe'] != '':
                    self.checked_Bahn_2.set(True)
                    self.switchBahn2State()
                    self.__root.G2.configure(text=dg['wettkampfgruppe'])
                    self.anzeige.G2.configure(text=dg['wettkampfgruppe'])
                    self.id_time_2 = 'typ.row.column#' + str(dg['typ']) + '#' + str(dg['row']) + '#' + str(dg['column'])
                    if dg['zeit1'] != '' and dg['zeit2'] != '':
                        check_time = True
                count += 1

        self.reset()

        if check_time == True:
            messagebox.showinfo('Info', 'Für diese Gruppen existieren schon zwei Zeiten vorhanden!')

    def switchBahn1State(self):
        if self.checked_Bahn_1.get() == False:
            self.__root.G1.configure(state=DISABLED)
            self.__root.T1.configure(state=DISABLED)
            self.__root.F1.configure(state=DISABLED)
            self.__root.B1.configure(state=DISABLED)
            self.anzeige.G1.pack_forget()
            self.anzeige.Z1.pack_forget()
            self.writeKonsole('Bahn 1 wurde deaktiviert!')
        else:
            self.__root.G1.configure(state=NORMAL)
            self.__root.T1.configure(state=NORMAL)
            self.__root.F1.configure(state=NORMAL)
            self.__root.B1.configure(state=NORMAL)
            self.anzeige.G1.pack(expand=0, side=TOP, fill=X)
            self.anzeige.Z1.pack(expand=1, side=TOP, fill=BOTH)
            self.writeKonsole('Bahn 1 wurde aktiviert!')

    def switchBahn2State(self):
        if self.checked_Bahn_2.get() == False:
            self.__root.G2.configure(state=DISABLED)
            self.__root.T2.configure(state=DISABLED)
            self.__root.F2.configure(state=DISABLED)
            self.__root.B2.configure(state=DISABLED)
            self.anzeige.G2.pack_forget()
            self.anzeige.Z2.pack_forget()
            self.writeKonsole('Bahn 2 wurde deaktiviert!')
        else:
            self.__root.G2.configure(state=NORMAL)
            self.__root.T2.configure(state=NORMAL)
            self.__root.F2.configure(state=NORMAL)
            self.__root.B2.configure(state=NORMAL)
            self.anzeige.G2.pack(expand=0, side=BOTTOM, fill=X)
            self.anzeige.Z2.pack(expand=1, side=TOP, fill=BOTH)
            self.writeKonsole('Bahn 2 wurde aktiviert!')

    def start(self, event=None):   
        self.ZeitUebertragen = False
        self.Buzzer1DarfStarten = True
        self.Buzzer2DarfStarten = True
        self.__root.BtnStart.configure(state=DISABLED)
        self.__root.BtnAllesStop.configure(state=NORMAL)
        self.__root.BtnWechsel.configure(state=DISABLED)
        self.__root.BtnAnsichtWechseln.configure(state=DISABLED)
        self.__root.BtnZeitUebertragen.configure(state=DISABLED)
        self.__root.BtnStopReset.configure(state=NORMAL)
        self.changeColorFromButtonSummary()

        if self.checked_GPIO.get() == True and self.checked_Bahn_1.get() == True:
            self.GPIO_Start_1 = self.__root.Start_GPIO_1.get()
            self.GPIO_Stop_1 = self.__root.Stop_GPIO_1.get()
            self.BuzzerStartBahn1.when_pressed = self.startBuzzer1

        if self.checked_GPIO.get() == True and self.checked_Bahn_2.get() == True:
            self.GPIO_Start_2 = self.__root.Start_GPIO_2.get()
            self.GPIO_Stop_2 = self.__root.Stop_GPIO_2.get()
            self.BuzzerStartBahn2.when_pressed = self.startBuzzer2

        if self.checked_Tastatur.get() == True and self.checked_Bahn_1.get() == True:
            self.Taste_Start_1 = self.__root.Start_Taste_1.get()
            self.Taste_Stop_1 = self.__root.Stop_Taste_1.get()
            self.__root.bind(self.Taste_Start_1, self.startBuzzer1)
        
        if self.checked_Tastatur.get() == True and self.checked_Bahn_2.get() == True:
            self.Taste_Start_2 = self.__root.Start_Taste_2.get()
            self.Taste_Stop_2 = self.__root.Stop_Taste_2.get()
            self.__root.bind(self.Taste_Start_2, self.startBuzzer2)
        
        t = Thread(target=self.playSound, args=[self.FileAngriffsbefehl])
        t.start()

    def startBuzzer1(self, event=None):
        if not self.time_is_running_1 and self.Buzzer1DarfStarten == True:
            if self.checked_GPIO.get() == True:
                self.BuzzerStopBahn1.when_pressed = self.stop_1
                if event == None:
                    self.writeKonsole('Zeit 1 mit Buzzer gestartet!')
            if self.checked_Tastatur.get() == True:
                self.__root.unbind(self.Taste_Start_1)
                self.__root.bind(self.Taste_Stop_1, self.stop_1)
                if event != None:
                    self.writeKonsole('Zeit 1 mit Taste ' + event.char + ' gestartet!')
            self.time_is_running_1 = True
            self.start_time_1 = time.time()
            self.update_time_1()

    def startBuzzer2(self, event=None):
        if not self.time_is_running_2 and self.Buzzer2DarfStarten == True:
            if self.checked_GPIO.get() == True:
                self.BuzzerStopBahn2.when_pressed = self.stop_2
                if event == None:
                    self.writeKonsole('Zeit 2 mit Buzzer gestartet!')
            if self.checked_Tastatur.get() == True:
                self.__root.unbind(self.Taste_Start_2)
                self.__root.bind(self.Taste_Stop_2, self.stop_2)
                if event != None:
                    self.writeKonsole('Zeit 2 mit Taste ' + event.char + ' gestartet!')
            self.time_is_running_2 = True
            self.start_time_2 = time.time()
            self.update_time_2()

    def allesStop(self):
        self.stop_1('')
        self.stop_2('')
        self.writeKonsole('Beide Zeiten mit CTkButton angehalten!')

    def stop_1(self, event=None):
        self.time_is_running_1 = False
        self.Buzzer1DarfStarten = False
        t = Thread(target=self.playSound, args=[self.FileStopp])
        t.start()
        if self.checked_Tastatur.get() == True:
            self.__root.unbind(self.Taste_Stop_1)
            if event != None and event != '':
                self.writeKonsole('Zeit 1 mit Taste ' + event.char + ' angehalten!')
        if self.checked_GPIO.get() == True and event == None:
            self.writeKonsole('Zeit 1 mit Buzzer bzw CTkButton angehalten!')
        if self.time_is_running_1 == False and self.time_is_running_2 == False:
            self.__root.BtnAllesStop.configure(state=DISABLED)
            self.__root.BtnWechsel.configure(state=NORMAL)
            self.__root.BtnAnsichtWechseln.configure(state=NORMAL)
            self.__root.BtnZeitUebertragen.configure(state=NORMAL)
            self.__root.BtnStopReset .configure(state=NORMAL)
            self.changeColorFromButtonSummary()

    def stop_2(self, event=None):
        self.time_is_running_2 = False
        self.Buzzer2DarfStarten = False
        t = Thread(target=self.playSound, args=[self.FileStopp])
        t.start()
        if self.checked_Tastatur.get() == True:
            self.__root.unbind(self.Taste_Stop_2)
            if event != None and event != '':
                self.writeKonsole('Zeit 2 mit Taste ' + event.char + ' angehalten!')
        if self.checked_GPIO.get() == True and event == None:
            self.writeKonsole('Zeit 1 mit Buzzer bzw CTkButton angehalten!')
        if self.time_is_running_1 == False and self.time_is_running_2 == False:
            self.__root.BtnAllesStop.configure(state=DISABLED)
            self.__root.BtnWechsel.configure(state=NORMAL)
            self.__root.BtnAnsichtWechseln.configure(state=NORMAL)
            self.__root.BtnZeitUebertragen.configure(state=NORMAL)
            self.__root.BtnStopReset .configure(state=NORMAL)
            self.changeColorFromButtonSummary()

    def reset(self):
        self.__root.T1.configure(text='00:00:00')
        self.__root.T2.configure(text='00:00:00')
        self.anzeige.Z1.configure(text='00:00:00')
        self.anzeige.Z2.configure(text='00:00:00')
        self.__root.BtnStart.configure(state=NORMAL)
        
        self.changeColorFromButtonSummary()

    def update_time_1(self):
        if self.time_is_running_1:
            elapsed_time = time.time() - self.start_time_1
            dt = datetime.fromtimestamp(elapsed_time).strftime('%M:%S:%f')[:-4]
            self.__root.T1.configure(text=dt)
            self.anzeige.Z1.configure(text=dt)
            self.__root.T1.after(50, self.update_time_1)
        else:
            self.stop_time_1 = time.time()

    def update_time_2(self):
        if self.time_is_running_2:
            elapsed_time = time.time() - self.start_time_2
            dt = datetime.fromtimestamp(elapsed_time).strftime('%M:%S:%f')[:-4]
            self.__root.T2.configure(text=dt)
            self.anzeige.Z2.configure(text=dt)
            self.__root.T2.after(50, self.update_time_2)
        else:
            self.stop_time_2 = time.time()

    def stopreset(self):
        self.time_is_running_1 = False
        self.time_is_running_2 = False
        self.reset()

    def zeit1loeschen(self):
        dg_select = self.__root.CBDG.get()

        for dg in self.Durchgänge:
            if dg['dg'] == int(dg_select):
                dg['zeit1'] = ''
                dg['fehler1'] = 0
                dg['zeit2'] = ''
                dg['fehler2'] = 0
                dg['bestzeit'] = ''
                dg['platzierung'] = 0
                self.zeichneNeueWerte(dg['row'], dg['column']+1, '', dg['row'], dg['column'], dg['typ'])
                self.zeichneNeueWerte(dg['row'], dg['column']+2, '', dg['row'], dg['column'], dg['typ'])
                self.zeichneNeueWerte(dg['row'], dg['column']+3, '', dg['row'], dg['column'], dg['typ'])
                self.zeichneNeueWerte(dg['row'], dg['column']+4, '', dg['row'], dg['column'], dg['typ'])
        
        self.bestzeitPlatzierungBerechnen()

    def zeit2loeschen(self):
        dg_select = self.__root.CBDG.get()

        for dg in self.Durchgänge:
            if dg['dg'] == int(dg_select):
                dg['zeit2'] = ''
                dg['fehler2'] = 0
                self.zeichneNeueWerte(dg['row'], dg['column']+2, '', dg['row'], dg['column'], dg['typ'])
                if dg['zeit1'] != '':
                    dg['bestzeit'] = dg['zeit1']
                    dg['fehlerbest'] = dg['fehler1']
                    text = str(dg['bestzeit'])
                    if dg['fehlerbest'] > 0:
                        text += ' +' + str(dg['fehlerbest'])
                    self.zeichneNeueWerte(dg['row'], dg['column']+3, text, dg['row'], dg['column'], dg['typ'])
                else:
                    dg['bestzeit'] = ''
                    dg['fehlerbest'] = 0
                    dg['platzierung'] = 0
                    self.zeichneNeueWerte(dg['row'], dg['column']+3, '', dg['row'], dg['column'], dg['typ'])
                    self.zeichneNeueWerte(dg['row'], dg['column']+4, '', dg['row'], dg['column'], dg['typ'])
        
        self.bestzeitPlatzierungBerechnen()

    def naechsterDG(self):
        dg_select = self.__root.CBDG.get()
        dg_select = int(dg_select)

        dg_list = []
        for item in self.DGNumbers:
            try:
                dg_list.append(int(item))
            except ValueError:
                pass

        max_dg = max(dg_list)

        if dg_select < max_dg:
            self.__root.CBDG.set(str(dg_select+1))
            self.ladeZeitnehmungsDaten()
    
    def vorherigerDG(self):
        dg_select = self.__root.CBDG.get()
        dg_select = int(dg_select)

        if dg_select > 0:
            self.__root.CBDG.set(str(dg_select-1))
            self.ladeZeitnehmungsDaten()

    # Functions - Tab Einstellungen
    def updateRahmenAnzeige(self):
        if self.checked_Rahmen.get() == True:
            self.anzeige.wm_attributes('-type', 'splash')

    def updateFontSizeZeit(self, event=None):
        size = self.__root.SGZ.get()
        self.anzeige.Z1.configure(font=(self.GlobalFontArt, size))
        self.anzeige.Z2.configure(font=(self.GlobalFontArt, size))
    
    def updateFontSizeGruppe(self, event=None):
        size = self.__root.SGG.get()
        self.anzeige.G1.configure(font=(self.GlobalFontArt, size))
        self.anzeige.G2.configure(font=(self.GlobalFontArt, size))

    def changeFontSizeFromWindowSize(self):
        self.screen_height = self.anzeige.winfo_height()
        self.__root.LblAnpassungWert.configure(text=str(self.screen_height))

        size_new = int(self.screen_height) / int(self.__root.SBFaktorZeit.get())
        self.__root.SGZ.set(size_new)
        self.anzeige.Z1.configure(font=(self.GlobalFontArt, size_new))
        self.anzeige.Z2.configure(font=(self.GlobalFontArt, size_new))
        self.AnzeigeFontSizeTime = size_new

        size_new = int(self.screen_height) / int(self.__root.SBFaktorGruppen.get())
        self.__root.SGG.set(size_new)
        self.anzeige.G1.configure(font=(self.GlobalFontArt, size_new))
        self.anzeige.G2.configure(font=(self.GlobalFontArt, size_new))
        self.AnzeigeFontSizeGroup = size_new

        size_new = int(self.screen_height) / int(self.__root.SBFaktorInfo.get())
        self.AnzeigeFontSizeInfo = size_new
        for widgets in self.anzeige.INFO.winfo_children():
            widgets.configure(font=(self.GlobalFontArt, size_new))
        
        size_new = int(self.screen_height) / int(self.__root.SBFaktorAuswertung.get())
        self.AnzeigeFontSizeAuswertung = size_new
        for widgets in self.anzeige.INFO.winfo_children():
            widgets.configure(font=(self.GlobalFontArt, size_new))

class IntSpinbox(CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: int = 1,
                 command: Callable = None,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = step_size
        self.command = command

        self.configure(fg_color='transparent')  # set frame color

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = CTkButton(self, text="-", width=height-6, height=height-6, corner_radius=0, command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = CTkEntry(self, width=width-(2*height), height=height-6, border_width=0, corner_radius=0, justify=CENTER)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = CTkButton(self, text="+", width=height-6, height=height-6, corner_radius=0, command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # default value
        self.entry.insert(0, "0")

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) - self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def get(self) -> Union[int, None]:
        try:
            return int(self.entry.get())
        except ValueError:
            return None

    def set(self, value: int):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(int(value)))

if __name__ == "__main__":
    Kuppelstopper()