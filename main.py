from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from datetime import datetime
import time
from random import *
from gpiozero import Button as GPIO_Button


class Hauptfenster():        
    # Hauptfenster
    def __init__(self):
        self.file_angriffbefehel = './Resources/AngriffsbefehlWonie.mp3'
        self.GPIO_Start_1 = 17
        self.GPIO_Stop_1 = 27
        self.GPIO_Start_2 = 19
        self.GPIO_Stop_2 = 26
        self.Taste_Start_1 = 'a'
        self.Taste_Stop_1 = 'q'
        self.Taste_Start_2 = 's'
        self.Taste_Stop_2 = 'w'

        # self.Wettkampfgruppen = []
        self.Wettkampfgruppen = [
            {'gruppenname': 'Gruppe1','reihenfolge': '1'},
            {'gruppenname': 'Gruppe2','reihenfolge': '2'},
            {'gruppenname': 'Gruppe3','reihenfolge': '3'},
            {'gruppenname': 'Gruppe4','reihenfolge': '4'},
            {'gruppenname': 'Gruppe5','reihenfolge': '5'},
            {'gruppenname': 'Gruppe6','reihenfolge': '6'},
            {'gruppenname': 'Gruppe7','reihenfolge': '7'},
            {'gruppenname': 'Gruppe8','reihenfolge': '8'},
            {'gruppenname': 'Gruppe9','reihenfolge': '9'},
            {'gruppenname': 'Gruppe10','reihenfolge': '10'},
            {'gruppenname': 'Gruppe11','reihenfolge': '11'},
            {'gruppenname': 'Gruppe12','reihenfolge': '12'},
            {'gruppenname': 'Gruppe13','reihenfolge': '13'},
            {'gruppenname': 'Gruppe14','reihenfolge': '14'},
            {'gruppenname': 'Gruppe15','reihenfolge': '15'},
            {'gruppenname': 'Gruppe16','reihenfolge': '16'},
            {'gruppenname': 'Gruppe17','reihenfolge': '17'},
            # {'gruppenname': 'Gruppe18','reihenfolge': '18'},
            # {'gruppenname': 'Gruppe19','reihenfolge': '19'},
            # {'gruppenname': 'Gruppe20','reihenfolge': '20'},
            # {'gruppenname': 'Gruppe21','reihenfolge': '21'},
            # {'gruppenname': 'Gruppe22','reihenfolge': '22'},
            # {'gruppenname': 'Gruppe23','reihenfolge': '23'},
            # {'gruppenname': 'Gruppe24','reihenfolge': '24'},
            # {'gruppenname': 'Gruppe25','reihenfolge': '25'},
            # {'gruppenname': 'Gruppe26','reihenfolge': '26'},
            # {'gruppenname': 'Gruppe27','reihenfolge': '27'},
            # {'gruppenname': 'Gruppe28','reihenfolge': '28'},
            # {'gruppenname': 'Gruppe29','reihenfolge': '29'},
            # {'gruppenname': 'Gruppe30','reihenfolge': '30'}
        ]

        self.Durchgänge = []
        self.DGNumbers = []
        self.DurchgangNummer = 1
        self.AnzahlGrunddurchgänge = 0

        self.AnzeigeGDStartRow = 0
        self.AnzeigeGDStartColumn = 0
        self.AnzeigeVFStartRow = 0
        self.AnzeigeVFStartColumn = 8
        self.AnzeigeHFStartRow = 10
        self.AnzeigeHFStartColumn = 8
        self.AnzeigeKFStartRow = 16
        self.AnzeigeKFStartColumn = 8
        self.AnzeigeFStartRow = 20
        self.AnzeigeFStartColumn = 8
        self.AnzeigeDWStartRow = 24
        self.AnzeigeDWStartColumn = 8

        self.time_is_running_1 = False
        self.start_time_1 = ''
        self.stop_time_1 = ''
        self.id_time_1 = ''
        self.time_is_running_2 = False
        self.start_time_2 = ''
        self.stop_time_2 = ''
        self.id_time_2 = ''

        self.__root = Tk()
        self.__root.title('KuppelStopper 3.0')
        self.__root.minsize(1200, 700)

        self.icon = PhotoImage(file='./Resources/Kuppelstopper.png')
        self.__root.iconphoto(False, self.icon)       

        self.iconDelete = PhotoImage(file='./Resources/delete.png')
        
        COLOR_FTab_INACTIVE = '#FFFFFF'
        COLOR_FTab_ACTIVE = '#D3C9C6'
        COLOR_BUTTON_ACTIVE = COLOR_FTab_ACTIVE
        COLOR_BUTTON_HOVER = '#C2BCBA'
        COLOR_BUTTON_DISABLED = '#FFFFFF'

        self.style = Style()
        self.style.theme_use('default')
        self.style.configure('.', background='white')
        self.style.configure('TNotebook', borderwidth=0, background=COLOR_FTab_INACTIVE)
        self.style.configure('TNotebook.FTab', relief=SOLID, borderwidth=0, bordercolor=COLOR_FTab_INACTIVE, darkcolor=COLOR_FTab_INACTIVE, lightcolor=COLOR_FTab_INACTIVE, padding=[10,5], background=COLOR_FTab_INACTIVE)
        self.style.map('TNotebook.FTab', background=[('selected',COLOR_FTab_ACTIVE),('active',COLOR_FTab_ACTIVE)])
        self.style.configure('TButton', relief=SOLID, borderwidth=0, bordercolor=COLOR_BUTTON_ACTIVE, darkcolor=COLOR_BUTTON_ACTIVE, lightcolor=COLOR_BUTTON_ACTIVE, padding=[10,5], background=COLOR_BUTTON_ACTIVE)
        self.style.map('TButton', background=[('active',COLOR_BUTTON_HOVER),('disabled',COLOR_BUTTON_DISABLED)], foreground=[('disabled',COLOR_BUTTON_DISABLED)])

        # Menü
        self.__root.NbFTabControl = Notebook(self.__root, padding='0')
        self.__root.FTab1 = Frame(self.__root.NbFTabControl, padding='5')
        self.__root.FTab2 = Frame(self.__root.NbFTabControl, padding='5')
        self.__root.FTab3 = Frame(self.__root.NbFTabControl, padding='5')
        self.__root.NbFTabControl.add(self.__root.FTab1, text='Anmeldung')
        self.__root.NbFTabControl.add(self.__root.FTab2, text='Übersicht - Zeitnehmung')
        self.__root.NbFTabControl.add(self.__root.FTab3, text='Einstellungen')
        self.__root.NbFTabControl.pack(expand=1, fill='both')
   
        # FTab Anmeldung
        self.config = IntVar()
        self.config.set(1)

        self.__root.anmeldungWettkampfgruppen = LabelFrame(self.__root.FTab1, text='Anmeldung Wettkampfgruppen', borderwidth=1, relief=SOLID)
        self.__root.anmeldungWettkampfgruppen.pack(side='top', fill='x', padx='10', pady='10')
        self.__root.Entry = Entry(self.__root.anmeldungWettkampfgruppen, takefocus = 1)
        self.__root.Entry.pack(side='top', fill='x', padx='10', pady='10')
        self.__root.Entry.bind('<Return>', self.addWettkampfgruppe)

        self.__root.LfReihenfolge = LabelFrame(self.__root.anmeldungWettkampfgruppen, text='Angemeldete Gruppen', borderwidth=1, relief=SOLID)
        self.__root.LfReihenfolge.pack(side='top', fill='x', padx='10', pady='10')

        if len(self.Wettkampfgruppen) == 0:
            self.__root.LNoGroups = Label(self.__root.LfReihenfolge, text='Keine Gruppen angemeldet!', takefocus = 0)
            self.__root.LNoGroups.grid(row=0, column=0, sticky=(W), padx='10', pady='5')
        else:
            self.zeichneAngemeldeteGruppen()

        # self.__root.LfSetupBewerb = LabelFrame(self.__root.FTab1, text='Bewerb Konfiguration', borderwidth=1, relief=SOLID)
        # self.__root.LfSetupBewerb.pack(side='top', fill='x', padx='10', pady='10')
        # self.__root.RbConfig1 = Radiobutton(self.__root.LfSetupBewerb, text='GR:2x AF:1x VF:1x HB:1x KF:1x GF:2x', variable=self.config, value=1, takefocus=0)
        # self.__root.RbConfig1.grid(row=0, column=0, sticky=(W), padx='10', pady='5')
        # self.__root.RbConfig2 = Radiobutton(self.__root.LfSetupBewerb, text='GR:2x VF:2x HB:2x KF:2x GF:2x', variable=self.config, value=2, takefocus=0)
        # self.__root.RbConfig2.grid(row=1, column=0, sticky=(W), padx='10', pady='5')
        # legende = 'GR.....Grunddurchgang\nAF.....Achtelfinale(16)\nVF.....Viertelfinale(8)\nHF.....Halbfinale(4)\nKF.....Kleines Finale(2)\nAF.....Große Finale(2)\n1x.....1 Bahn\n2x.....Beide Bahnen'
        # self.__root.LConfigLegende = Label(self.__root.LfSetupBewerb, text=legende, takefocus = 0)
        # self.__root.LConfigLegende.grid(row=0, column=1, rowspan=2, padx='10', pady='5')

        self.__root.BtnStart = Button(self.__root.FTab1, text='Gruppen übernehmen', width=10, padding=10, command=self.uebernahmeGruppen, takefocus = 0)
        self.__root.BtnStart.pack(side='top', fill='x', padx='10', pady='10')


        # FTab Übersicht - Zeitnehmung
        self.checked_Bahn_1 = BooleanVar()
        self.checked_Bahn_2 = BooleanVar()
        self.checked_Bahn_1.set(False)
        self.checked_Bahn_2.set(False)

        self.__root.dg = LabelFrame(self.__root.FTab2, text='Durchgänge', borderwidth=1, relief=SOLID)
        self.__root.dg.pack(side='top', fill='both', padx='10', pady='10', ipady='10')

        self.__root.zeitnehmung = LabelFrame(self.__root.FTab2, text='Aktueller Durchgang', borderwidth=1, relief=SOLID)
        self.__root.zeitnehmung.pack(side='left', padx='10')

        self.__root.CBDG = Combobox(self.__root.zeitnehmung, textvariable=StringVar(), state='readonly', width=5, takefocus = 0, justify="center",  font=('Helvetica', 14))
        self.__root.CBDG.bind('<<ComboboxSelected>>',self.ladeZeitnehmungsDaten)
        self.__root.CBDG.pack(side='left', padx='10', pady='20', ipady=10)

        self.__root.BtnStart = Button(self.__root.zeitnehmung, text='Start', width=10, padding=10, command=self.start, takefocus = 0, state=DISABLED)
        self.__root.BtnStart.pack(side='left', padx='10', pady='10')
        self.__root.BtnAllesStop = Button(self.__root.zeitnehmung, text='Alles Stop', width=10, padding=10, command=self.allesStop, takefocus = 0, state=DISABLED)
        self.__root.BtnAllesStop.pack(side='left', pady='10')
        self.__root.BtnReset = Button(self.__root.zeitnehmung, text='Reset', width=10, padding=10, command=self.reset, takefocus = 0, state=DISABLED)
        self.__root.BtnReset.pack(side='right', padx='10', pady='10')  
        self.__root.BtnWechsel = Button(self.__root.zeitnehmung, text='Bahn Wechsel', width=15, padding=10, command=self.bahnWechsel, takefocus = 0, state=DISABLED)
        self.__root.BtnWechsel.pack(side='right', padx='10', pady='10')
        self.__root.BtnZeitUebertrag = Button(self.__root.zeitnehmung, text='Zeit übertragen', width=10, padding=10, command=self.reset, takefocus = 0, state=DISABLED)
        self.__root.BtnZeitUebertrag.pack(side='right', padx='10', pady='10') 

        self.__root.LfBahnen = LabelFrame(self.__root.FTab2, text='Zeitnehmung', borderwidth=1, relief=SOLID)
        self.__root.LfBahnen.pack(side='left', padx='10')

        self.__root.LblFehler = Label(self.__root.LfBahnen, text='Fehler', takefocus = 0)
        self.__root.LblFehler .grid(row=0, column=3, padx='10', pady=(5,0))
        
        self.__root.CB1 = Checkbutton(self.__root.LfBahnen, text='Bahn 1', variable=self.checked_Bahn_1, command=self.switchBahn1State, takefocus = 0)
        self.__root.CB1.grid(row=1, column=0, padx='10')
        self.__root.G1 = Label(self.__root.LfBahnen, text='...', font=('Helvetica', 20), takefocus = 0, state=DISABLED)
        self.__root.G1 .grid(row=1, column=1, padx='10')
        self.__root.T1 = Label(self.__root.LfBahnen, text='00:00:00', font=('Helvetica', 20), takefocus = 0, state=DISABLED)
        self.__root.T1.grid(row=1, column=2, padx='10')
        self.__root.F1 = Entry(self.__root.LfBahnen, width=5, takefocus = 0)
        self.__root.F1.grid(row=1, column=3, padx='10')
        self.__root.B1 = Button(self.__root.LfBahnen, text='Stop', width=10, command=self.stop_1, takefocus = 0, state=DISABLED)
        self.__root.B1.grid(row=1, column=4)

        self.__root.CB2 = Checkbutton(self.__root.LfBahnen, text='Bahn 2', variable=self.checked_Bahn_2, command=self.switchBahn2State, takefocus = 0)
        self.__root.CB2.grid(row=2, column=0, padx='10')
        self.__root.G2 = Label(self.__root.LfBahnen, text='...', font=('Helvetica', 20), takefocus = 0, state=DISABLED)
        self.__root.G2 .grid(row=2, column=1, padx='10')
        self.__root.T2 = Label(self.__root.LfBahnen, text='00:00:00', font=('Helvetica', 20), takefocus = 0, state=DISABLED)
        self.__root.T2.grid(row=2, column=2, padx='10')
        self.__root.F2 = Entry(self.__root.LfBahnen, width=5, takefocus = 0)
        self.__root.F2.grid(row=2, column=3, padx='10')
        self.__root.B2 = Button(self.__root.LfBahnen, text='Stop', width=10, command=self.stop_2, takefocus = 0, state=DISABLED)
        self.__root.B2.grid(row=2, column=4)


        # FTab Einstellungen
        self.checked_Tastatur = BooleanVar()
        self.checked_GPIO = BooleanVar()
        self.checked_Rahmen = BooleanVar()
        self.checked_Konsole = BooleanVar()

        self.checked_Tastatur.set(True)
        self.checked_GPIO.set(False)
        self.checked_Rahmen.set(False)
        self.checked_Konsole.set(True)

        self.__root.setupEingabe = LabelFrame(self.__root.FTab3, text='Eingabe', borderwidth=1, relief=SOLID)
        self.__root.setupEingabe.pack(side='top', fill='x', padx='10', pady='5')
        self.__root.CheckTastatur = Checkbutton(self.__root.setupEingabe, text='Tastatur', variable=self.checked_Tastatur, takefocus = 0)
        self.__root.CheckTastatur.grid(row=0, column=0, padx='10')
        self.__root.CheckGPIO = Checkbutton(self.__root.setupEingabe, text='GPIO', variable=self.checked_GPIO, takefocus = 0)
        self.__root.CheckGPIO.grid(row=0, column=1)
        self.__root.CheckRahmen = Checkbutton(self.__root.setupEingabe, text='Rahmen ausblenden', variable=self.checked_Rahmen, takefocus = 0, command=self.updateRahmenAnzeige)
        self.__root.CheckRahmen.grid(row=0, column=2, padx='10')
        self.__root.CheckKonsole = Checkbutton(self.__root.setupEingabe, text='Konsole', variable=self.checked_Konsole, takefocus = 0, command=self.switchKonsoleState)
        self.__root.CheckKonsole.grid(row=0, column=3)

        self.__root.setupTasten = LabelFrame(self.__root.FTab3, text='Tasten', borderwidth=1, relief=SOLID)
        self.__root.setupTasten.pack(side='top', fill='x', padx='10', pady='5')
        self.__root.Start_Taste_1_Label = Label(self.__root.setupTasten, text='Start 1', takefocus = 0)
        self.__root.Start_Taste_1_Label.grid(row=0, column=0, padx='10', pady='10')
        self.__root.Start_Taste_1 = Entry(self.__root.setupTasten, width=3, takefocus = 0)
        self.__root.Start_Taste_1.grid(row=0, column=1, pady='10')
        self.__root.Stop_Taste_1_Label = Label(self.__root.setupTasten, text='Stop 1', takefocus = 0)
        self.__root.Stop_Taste_1_Label.grid(row=0, column=2, padx='10', pady='10')
        self.__root.Stop_Taste_1 = Entry(self.__root.setupTasten, width=3, takefocus = 0)
        self.__root.Stop_Taste_1.grid(row=0, column=3, pady='10')
        self.__root.Start_Taste_2_Label = Label(self.__root.setupTasten, text='Start 2', takefocus = 0)
        self.__root.Start_Taste_2_Label.grid(row=0, column=4, padx='10', pady='10')
        self.__root.Start_Taste_2 = Entry(self.__root.setupTasten, width=3, takefocus = 0)
        self.__root.Start_Taste_2.grid(row=0, column=5, pady='10')
        self.__root.Stop_Taste_2_Label = Label(self.__root.setupTasten, text='Stop 2', takefocus = 0)
        self.__root.Stop_Taste_2_Label.grid(row=0, column=6, padx='10',pady='10')
        self.__root.Stop_Taste_2 = Entry(self.__root.setupTasten, width=3, takefocus = 0)
        self.__root.Stop_Taste_2.grid(row=0, column=7, pady='10')

        self.__root.Start_Taste_1.insert(0, self.Taste_Start_1)
        self.__root.Stop_Taste_1.insert(0, self.Taste_Stop_1)
        self.__root.Start_Taste_2.insert(0, self.Taste_Start_2)
        self.__root.Stop_Taste_2.insert(0, self.Taste_Stop_2)

        self.__root.setupGPIO = LabelFrame(self.__root.FTab3, text='GPIO', borderwidth=1, relief=SOLID)
        self.__root.setupGPIO.pack(side='top', fill='x', padx='10', pady='5')
        self.__root.Start_GPIO_1_Label = Label(self.__root.setupGPIO, text='Start 1', takefocus = 0)
        self.__root.Start_GPIO_1_Label.grid(row=0, column=0, padx='10', pady='10')
        self.__root.Start_GPIO_1 = Entry(self.__root.setupGPIO, width=3, takefocus = 0)
        self.__root.Start_GPIO_1.grid(row=0, column=1, pady='10')
        self.__root.Stop_GPIO_1_Label = Label(self.__root.setupGPIO, text='Stop 1', takefocus = 0)
        self.__root.Stop_GPIO_1_Label.grid(row=0, column=2, padx='10', pady='10')
        self.__root.Stop_GPIO_1 = Entry(self.__root.setupGPIO, width=3, takefocus = 0)
        self.__root.Stop_GPIO_1.grid(row=0, column=3, pady='10')
        self.__root.Start_GPIO_2_Label = Label(self.__root.setupGPIO, text='Start 2', takefocus = 0)
        self.__root.Start_GPIO_2_Label.grid(row=0, column=4, padx='10', pady='10')
        self.__root.Start_GPIO_2 = Entry(self.__root.setupGPIO, width=3, takefocus = 0)
        self.__root.Start_GPIO_2.grid(row=0, column=5, pady='10')
        self.__root.Stop_GPIO_2_Label = Label(self.__root.setupGPIO, text='Stop 2', takefocus = 0)
        self.__root.Stop_GPIO_2_Label.grid(row=0, column=6, padx='10',pady='10')
        self.__root.Stop_GPIO_2 = Entry(self.__root.setupGPIO, width=3, takefocus = 0)
        self.__root.Stop_GPIO_2.grid(row=0, column=7, pady='10')

        self.__root.Start_GPIO_1.insert(0, self.GPIO_Start_1)
        self.__root.Stop_GPIO_1.insert(0, self.GPIO_Stop_1)
        self.__root.Start_GPIO_2.insert(0, self.GPIO_Start_2)
        self.__root.Stop_GPIO_2.insert(0, self.GPIO_Stop_2)

        self.__root.setupStyle = LabelFrame(self.__root.FTab3, text='Style', borderwidth=1, relief=SOLID)
        self.__root.setupStyle.pack(side='top', fill='x', padx='10', pady='5')
        self.__root.SGZL = Label(self.__root.setupStyle, text='Schriftgröße Zeit', takefocus = 0)
        self.__root.SGZL.grid(row=0, column=0, padx='10', pady='10')
        self.__root.SGZ = Spinbox(self.__root.setupStyle, width=3, from_=1, to=500, command=self.updateFontSizeZeit, takefocus = 0)
        self.__root.SGZ.grid(row=0, column=1, padx='10', pady='10')
        self.__root.SGZ.set(50)
        self.__root.SGGL = Label(self.__root.setupStyle, text='Schriftgröße Gruppe', takefocus = 0)
        self.__root.SGGL.grid(row=0, column=2, padx='10', pady='10')
        self.__root.SGG = Spinbox(self.__root.setupStyle, width=3, from_=1, to=500, command=self.updateFontSizeGruppe, takefocus = 0)
        self.__root.SGG.grid(row=0, column=3, padx='10', pady='10')
        self.__root.SGG.set(30)

        self.__root.Konsole = Label(self.__root, takefocus = 0, foreground='#8f8e8c')
        self.__root.Konsole.pack(expand=1, side='top', fill='both')

        self.showAnzeige()

    # Anzeigefenster
    def showAnzeige(self):
        self.anzeige = Toplevel()
        self.anzeige.title('KuppelStopper 3.0 Anzeige')
        self.anzeige.minsize(700, 400)

        self.icon = PhotoImage(file='Resources/Kuppelstopper.png')
        self.anzeige.iconphoto(False, self.icon)

        self.anzeige.frame = Frame(self.anzeige)
        self.anzeige.frame.pack(expand=1, side=TOP, fill=BOTH)

        self.anzeige.G1 = Label(self.anzeige.frame, text='', foreground='#818ef0', background='#6e6c6b', font=('Helvetica', self.__root.SGG.get()), takefocus=0)
        self.anzeige.Z1 = Label(self.anzeige.frame, text='00:00:00', anchor='center', foreground='#ffffff', background='#6e6c6b', font=('Helvetica', self.__root.SGZ.get()), takefocus=0)
        self.anzeige.Z2 = Label(self.anzeige.frame, text='00:00:00', anchor='center', foreground='#ffffff', background='#6e6c6b', font=('Helvetica', self.__root.SGZ.get()), takefocus=0)
        self.anzeige.G2 = Label(self.anzeige.frame, text='', anchor='ne', foreground='#93ff8f', background='#6e6c6b', font=('Helvetica', self.__root.SGG.get()), takefocus=0)
        
        self.anzeige.ERG = Label(self.anzeige.frame, text='Hier finden Sie später\ndie Auswertung!', anchor='center', justify='center', foreground='#ffffff', background='#6e6c6b', font=('Helvetica', self.__root.SGZ.get()), takefocus=0)
        self.anzeige.ERG.pack(expand=1, side=TOP, fill=BOTH)

        self.anzeige.mainloop()

    # Validation Functions
    def validate_only_numbers(self, action, value_if_allowed):
        try:
            if action == '1' and int(value_if_allowed) > 0 and int(value_if_allowed) <= len(self.Wettkampfgruppen): 
                float(value_if_allowed)
                return True
        except ValueError:
            return False
    
    # Functions    
    def updateRahmenAnzeige(self):
        if self.checked_Rahmen.get() == True:
            self.anzeige.wm_overrideredirect(True) 
        else:
            self.anzeige.wm_overrideredirect(False) 

    def updateFontSizeZeit(self, event=None):
        size = self.__root.SGZ.get()
        self.anzeige.Z1.config(font=('Helvetica', size))
        self.anzeige.Z2.config(font=('Helvetica', size))
    
    def updateFontSizeGruppe(self, event=None):
        size = self.__root.SGG.get()
        self.anzeige.G1.config(font=('Helvetica', size))
        self.anzeige.G2.config(font=('Helvetica', size))

    def bahnWechsel(self):
        self.werteInAnsichtUebertragen()

        bahnA = self.__root.G1.cget("text")
        bahnB = self.__root.G2.cget("text")

        bahnAId = self.id_time_1
        bahnBId = self.id_time_2

        self.__root.G1.config(text=bahnB)
        self.id_time_1 = bahnBId
        self.__root.G2.config(text=bahnA)

        self.anzeige.G1.config(text=bahnB)
        self.id_time_2 = bahnAId
        self.anzeige.G2.config(text=bahnA)
        
        self.__root.BtnStart['state'] = NORMAL
        self.__root.BtnReset['state'] = DISABLED

        
        self.checked_Bahn_1.set(False)
        self.checked_Bahn_2.set(False)
        self.switchBahn1State()
        self.switchBahn2State()
        self.checked_Bahn_1.set(True)
        self.checked_Bahn_2.set(True)
        self.switchBahn1State()
        self.switchBahn2State()

        self.writeKonsole('Die Bahnen wurden gewechselt!')
    
    def werteInAnsichtUebertragen(self):
        self.wechselAnsichtZurAuswertung()

        zeit1A = self.__root.T1.cget("text")
        fehler1A = self.__root.F1.get()
        if fehler1A == '':
            fehler1A == '0'
        id1A = self.id_time_1.split('_')
        typ1A = id1A[1]
        row1A = int(id1A[2])
        column1A = int(id1A[3])
        self.zeitUebertragen(typ1A, row1A, column1A, zeit1A, fehler1A)

        zeit2A = self.__root.T2.cget("text")
        fehler2A = self.__root.F2.get()
        if fehler2A == '':
            fehler2A == '0'
        id2A = self.id_time_2.split('_')
        typ2A = id2A[1]
        row2A = int(id2A[2])
        column2A = int(id2A[3])
        self.zeitUebertragen(typ2A, row2A, column2A, zeit2A, fehler2A)

        self.__root.T1.config(text='00:00:00')
        self.__root.T2.config(text='00:00:00')
        self.__root.F1.delete(0, END)
        # self.__root.F1.insert(0, '')
        self.__root.F2.delete(0, END)
        # self.__root.F2.insert(0, '')
        self.anzeige.Z1.config(text='00:00:00')
        self.anzeige.Z2.config(text='00:00:00')

        self.bestzeitPlatzierungBerechnen()

    def zeitUebertragen(self, typ, row, column, zeit, fehler):
        if fehler == '':
            fehler = 0
        elif fehler != '':
            fehler = int(fehler)
        
        for x in self.Durchgänge:
            if x['typ'] == typ and x['row'] == row and x['column'] == column:
                if x['zeit1'] == '':
                    x['zeit1'] = zeit
                    x['fehler1'] = fehler
                    x['bestzeit'] = zeit
                    x['fehlerbest'] = fehler
                    text = str(zeit)
                    if fehler > 0:
                        text += ' +' + str(fehler)
                    self.zeichneNeueWerte(row, column+1, text)
                    self.zeichneNeueWerte(row, column+3, text)
                else:
                    x['zeit2'] = zeit
                    x['fehler2'] = fehler
                    text = str(zeit)
                    if fehler > 0:
                        text += ' +' + str(fehler)
                    self.zeichneNeueWerte(row, column+2, text)
                    
                    time1 = self.addiereFehlerZurZeit(x['zeit1'], x['fehler1']) 
                    time2 = self.addiereFehlerZurZeit(zeit, fehler)

                    if self.berechneBestzeit(time1, time2) == 2:
                        x['bestzeit'] = zeit
                        x['fehlerbest'] = fehler
                        self.zeichneNeueWerte(row, column+3, text)

        self.bestzeitPlatzierungBerechnen()
    
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
        Grunddurchgang = []
        Viertelfinale = []
        Halbfinale = []
        KleinesFinale = []
        Finale = []
        Damenwertung = []

        for dg in self.Durchgänge:
            if dg['bestzeit'] != '':
                bestzeitinklfehler = self.addiereFehlerZurZeit(dg['bestzeit'], dg['fehlerbest'])
            else:
                bestzeitinklfehler = ''

            best_dict = {
                'gruppe': dg['wettkampfgruppe'],
                'bestzeit': dg['bestzeit'],
                'fehlerbest': dg['fehlerbest'],
                'bestzeitinklfehler': bestzeitinklfehler,
                'dg': dg['dg'],
                'row': dg['row'],
                'column': dg['column'],
                'platzierung': 0
            }

            if dg['typ'] == 'gd' and dg['wettkampfgruppe'] != '...':
                Grunddurchgang.append(best_dict)
            elif dg['typ'] == 'vf':
                Viertelfinale.append(best_dict)
            elif dg['typ'] == 'hf':
                Halbfinale.append(best_dict)
            elif dg['typ'] == 'kf':
                KleinesFinale.append(best_dict)
            elif dg['typ'] == 'f':
                Finale.append(best_dict)
            elif dg['typ'] == 'dw':
                Damenwertung.append(best_dict)
        
        Grunddurchgang.sort(key=self.sortTime)
        for index, item in enumerate(Grunddurchgang):
            if item['bestzeitinklfehler'] != '':
                platzierung_neu = index + 1
                item['platzierung'] = platzierung_neu
                self.zeichneNeueWerte(item['row'], item['column'] + 4, platzierung_neu)
            if item['platzierung'] >= 1 and item['platzierung'] <= 8:
                # Gruppe eine Runde weiter schieben
                test = self.Durchgänge
                print()
        
        Viertelfinale.sort(key=self.sortTime)
        for index, item in enumerate(Viertelfinale):
            if item['bestzeitinklfehler'] != '':
                platzierung_neu = index + 1
                item['platzierung'] = platzierung_neu
                self.zeichneNeueWerte(item['row'], item['column'] + 4, platzierung_neu)
            if item['platzierung'] >= 1 and item['platzierung'] <= 4:
                # Gruppe eine Runde weiter schieben
                print()

        Halbfinale.sort(key=self.sortTime)
        for index, item in enumerate(Halbfinale):
            if item['bestzeitinklfehler'] != '':
                platzierung_neu = index + 1
                item['platzierung'] = platzierung_neu
                self.zeichneNeueWerte(item['row'], item['column'] + 4, platzierung_neu)
            if item['platzierung'] >= 1 and item['platzierung'] <= 2:
                # Gruppe eine Runde weiter schieben
                print()
        
        KleinesFinale.sort(key=self.sortTime)
        for index, item in enumerate(KleinesFinale):
            if item['bestzeitinklfehler'] != '':
                platzierung_neu = index + 1
                item['platzierung'] = platzierung_neu
                self.zeichneNeueWerte(item['row'], item['column'] + 4, platzierung_neu)

        Finale.sort(key=self.sortTime)
        for index, item in enumerate(Finale):
            if item['bestzeitinklfehler'] != '':
                platzierung_neu = index + 1
                item['platzierung'] = platzierung_neu
                self.zeichneNeueWerte(item['row'], item['column'] + 4, platzierung_neu)

        Damenwertung.sort(key=self.sortTime)
        for index, item in enumerate(Damenwertung):
            if item['bestzeitinklfehler'] != '':
                platzierung_neu = index + 1
                item['platzierung'] = platzierung_neu
                self.zeichneNeueWerte(item['row'], item['column'] + 4, platzierung_neu)
        
        # Platzierungen ergänzen und in die nächste Stufe eintragen
        print()
    
    def sortTime(self, timeList):
        if timeList['bestzeitinklfehler'] == '':
            return '59', '59', '99'
        else:
            split_up = timeList['bestzeitinklfehler'].split(':')

            return split_up[0], split_up[1], split_up[2]
    
    def zeichneNeueWerte(self, row, column, text):
        for label in self.__root.dg.grid_slaves(row=row, column=column):
            label.config(text=text)

    def allesStop(self):
        self.stop_1('')
        self.stop_2('')
        self.writeKonsole('Beide Zeiten mit Button angehalten!')

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

        val= {
            'gruppenname': name,
            'reihenfolge': ''
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
            self.__root.LNoGroups = Label(self.__root.LfReihenfolge, text='Keine Gruppen angemeldet!', takefocus = 0)
            self.__root.LNoGroups.grid(row=0, column=0, sticky=(W), padx='10', pady='5')

        for index, i in enumerate(self.Wettkampfgruppen):
            row = index + 1
            gruppenname = i['gruppenname']
            reihenfolge = i['reihenfolge']

            w = Label(self.__root.LfReihenfolge, text=gruppenname, takefocus = 0)
            w.grid(row=row, column=0, sticky=(W), padx='10', pady='2')

            e = Entry(self.__root.LfReihenfolge, width=5, takefocus = 0)
            e.grid(row=row, column=1, sticky=(W), padx='10', pady='2')
            e.insert(0, reihenfolge)
            e.bind('<KeyRelease>', lambda event, name=gruppenname: self.reihenfolgeSpeichern(event, name))

            x = Label(self.__root.LfReihenfolge, image=self.iconDelete, takefocus = 0)
            x.grid(row=row, column=2, sticky=(W), padx='10', pady='2')
            x.bind('<Button>', lambda event, name=gruppenname: self.deleteWettkampfgruppe(event, name))

    def deleteWettkampfgruppe(self, event, name):
        for i in self.Wettkampfgruppen:
            if i['gruppenname'] == name:
                self.Wettkampfgruppen.remove(i)
        self.zeichneAngemeldeteGruppen()
        self.writeKonsole(name + ' wurde gelöscht!')

    def reihenfolgeSpeichern(self, event, name):
        reihenfolge = event.widget.get()
        for i in self.Wettkampfgruppen:
            if i['gruppenname'] == name:
                i['reihenfolge'] = reihenfolge
                self.writeKonsole(name + ' hat die Reihenfolgenposition von ' + reihenfolge)

    def uebernahmeGruppen(self):
        self.__root.dg.destroy()
        self.__root.dg = LabelFrame(self.__root.FTab2, text='Durchgänge', borderwidth=1, relief=SOLID)
        self.__root.dg.pack(side='top', fill='both', padx='10', pady='10', ipady='10')
        self.__root.zeitnehmung.pack_forget()
        self.__root.zeitnehmung.pack(side='left', padx='10')
        self.__root.LfBahnen.pack_forget()
        self.__root.LfBahnen.pack(side='left', padx='10')
        self.Durchgänge = []
        self.DGNumbers = []

        # übertrag in Damenwertung fehlt

        anzahl_gruppen = 0
        if len(self.Wettkampfgruppen) % 2:
            anzahl_gruppen = len(self.Wettkampfgruppen) + 1
        else: 
            anzahl_gruppen = len(self.Wettkampfgruppen)

        if anzahl_gruppen < 17:
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

            self.AnzahlGrunddurchgänge = anzahl_gruppen

            max_rows = self.AnzahlGrunddurchgänge
            space = Label(self.__root.dg, text='')
            space.grid(row=0, column=7, rowspan=max_rows, sticky=(W+E+N+S), padx=(5,0), ipadx=20)
            space = Label(self.__root.dg, text='')
            space.grid(row=0, column=16, rowspan=max_rows, sticky=(W+E+N+S), padx=(5,0), ipadx=20)
        else:
            self.AnzahlGrunddurchgänge = anzahl_gruppen
            max_rows = self.AnzahlGrunddurchgänge
            space = Label(self.__root.dg, text='')
            space.grid(row=0, column=7, rowspan=max_rows, sticky=(W+E+N+S), padx=(5,0), ipadx=20)

        self.zeichneGrundansicht()

        self.__root.NbFTabControl.select(self.__root.FTab2)
        sorted_list = sorted(self.Wettkampfgruppen, key=lambda x : int(x['reihenfolge']), reverse=False)
        for i in sorted_list:
            row = self.AnzeigeGDStartRow + int(i['reihenfolge'])
            col1 = self.AnzeigeGDStartColumn + 1
            txt = i['reihenfolge'] + ' - ' + i['gruppenname']
            text = Label(self.__root.dg, text=txt, takefocus = 0)

            if int(i['reihenfolge']) % 2:
                text.grid(row=row, column=col1, sticky=(W), pady=(10,0), ipady='5', ipadx='10')
            else:    
                text.grid(row=row, column=col1, sticky=(W), pady='0', ipady='5', ipadx='10')
            
            for x in self.Durchgänge:
                if x['typ'] == 'gd' and x['row'] == row and x['column'] == col1:
                    x['wettkampfgruppe'] = i['gruppenname']

        self.writeKonsole(str(len(self.Wettkampfgruppen)) + ' Gruppen wurden übernommen!')

    def zeichneGrundansicht(self):
        txt = ''
        time = ''
        rh = ''
        self.DurchgangNummer = 1
        self.zeichneZeitTable('Grunddurchgang (T1/T2/B)', self.AnzeigeGDStartColumn, self.AnzeigeGDStartRow, txt, time, rh, self.AnzahlGrunddurchgänge, True, 'gd', False)
        self.zeichneZeitTable('Viertelfinale (T1/T2/B)', self.AnzeigeVFStartColumn, self.AnzeigeVFStartRow, txt, time, rh, 8, True, 'vf', True)
        self.zeichneZeitTable('Halbfinale (T1/T2/B)', self.AnzeigeHFStartColumn, self.AnzeigeHFStartRow, txt, time, rh, 4, True, 'hf', True)
        self.zeichneZeitTable('Kleines Finale (T1/T2/B)', self.AnzeigeKFStartColumn, self.AnzeigeKFStartRow, txt, time, rh, 2, True, 'kf', True)
        self.zeichneZeitTable('Finale (T1/T2/B)', self.AnzeigeFStartColumn, self.AnzeigeFStartRow, txt, time, rh, 2, True, 'f', True)
        self.zeichneZeitTable('Damenwertung (T1/T2/B)', self.AnzeigeDWStartColumn, self.AnzeigeDWStartRow, txt, time, rh, 4, True, 'dw', False)
        self.DGNumbers.pop()
        self.__root.CBDG.config(values=self.DGNumbers)
        
    def zeichneZeitTable(self, title, startcolumn, startrow, gruppe_txt, time_txt, rh_text, anzahl_gruppen, show_rh, typ, hinweis):
        title = Label(self.__root.dg, text=title, takefocus = 0, anchor="center", font=('Helvetica', 14))
        title.grid(row=startrow, column=startcolumn, columnspan=5, sticky=(W+E+N+S), padx=(5,0))
        col1 = startcolumn + 1
        col2 = startcolumn + 2
        col3 = startcolumn + 3
        col4 = startcolumn + 4
        col5 = startcolumn + 5
        count_vf = 1
        for i in range(anzahl_gruppen):
            if hinweis == True:
                if i['typ'] == 'gd':
                    # Hinweis schreiben
                    print()
            row = startrow + i + 1
            durchgang = Label(self.__root.dg, text=self.DurchgangNummer, takefocus = 0, background='#98CF8B', anchor="center")
            text = Label(self.__root.dg, text=gruppe_txt, takefocus = 0)
            time1 = Label(self.__root.dg, text=time_txt, takefocus = 0, anchor="e")
            time2 = Label(self.__root.dg, text=time_txt, takefocus = 0, anchor="e")
            time3 = Label(self.__root.dg, text=time_txt, takefocus = 0, anchor="e")
            if show_rh == True:
                lrh = Label(self.__root.dg, text=rh_text, takefocus = 0, anchor="center")
            rh = i + 1
            if rh % 2:
                self.konvertiereArray(self.DurchgangNummer, gruppe_txt, typ, row, col1, hinweis)
                durchgang.grid(row=row, column=startcolumn, rowspan=2, sticky=(W+E+N+S), padx=(5,0), pady=(10,0), ipadx='5')
                text.grid(row=row, column=col1, sticky=(W), pady=(10,0), ipady='5', ipadx='10')
                time1.grid(row=row, column=col2, sticky=(W), pady=(10,0), ipady='5', ipadx='10')
                time2.grid(row=row, column=col3, sticky=(W), pady=(10,0), ipady='5', ipadx='10')
                time3.grid(row=row, column=col4, sticky=(W), pady=(10,0), ipady='5', ipadx='10')
                if show_rh == True:
                    lrh.grid(row=row, column=col5, sticky=(W), pady=(10,0), ipady='5', ipadx='10')
                self.DurchgangNummer += 1
            else:
                self.konvertiereArray(self.DurchgangNummer-1, gruppe_txt, typ, row, col1, hinweis)    
                text.grid(row=row, column=col1, sticky=(W), pady='0', ipady='5', ipadx='10') 
                time1.grid(row=row, column=col2, sticky=(W), pady='0', ipady='5', ipadx='10') 
                time2.grid(row=row, column=col3, sticky=(W), pady='0', ipady='5', ipadx='10')
                time3.grid(row=row, column=col4, sticky=(W), pady='0', ipady='5', ipadx='10')
                if show_rh == True:
                    lrh.grid(row=row, column=col5, sticky=(W), pady='0', ipady='5', ipadx='10')
        
    def konvertiereArray(self, dg_nummer, wettkampfgruppe, typ, row, column, hinweis):
        if dg_nummer not in self.DGNumbers:
            self.DGNumbers.append(dg_nummer)
        
        groupdict = {
            'wettkampfgruppe': wettkampfgruppe,
            'zeit1': '',
            'fehler1': '',
            'zeit2': '',
            'fehler2': '',
            'bestzeit': '',
            'fehlerbest': '',
            'typ': typ,                     # Art  (Grunddurchgang, Viertelfinale, ...)
            'dg': dg_nummer,                # Nummer des Durchganges
            'row': row,                     # Reihe von Name
            'column': column,               # Spalte von Name
            'hinweis': hinweis              # Hinweis für Platzierungsposition zb GD_1
        }
        self.Durchgänge.append(groupdict)

    def ladeZeitnehmungsDaten(self, event=None):
        self.wechselAnsichtZurZeit()
        self.checked_Bahn_1.set(False)
        self.checked_Bahn_2.set(False)
        self.switchBahn1State()
        self.switchBahn2State()
        self.__root.G1.config(text='...')
        self.__root.G2.config(text='...')
        self.__root.T1.config(text='00:00:00')
        self.__root.T2.config(text='00:00:00')
        self.__root.F1.delete(0, END)
        # self.__root.F1.insert(0, '')
        self.anzeige.G1.config(text='...')
        self.anzeige.G2.config(text='...')
        self.anzeige.Z1.config(text='00:00:00')
        self.anzeige.Z2.config(text='00:00:00')
        self.__root.F2.delete(0, END)
        # self.__root.F2.insert(0, '')
        count = 1
        dg_select = self.__root.CBDG.get()
        for dg in self.Durchgänge:
            if dg['typ'] == 'gd':
                if dg['dg'] == int(dg_select):
                    if count == 1 and dg['wettkampfgruppe'] != '...' and dg['wettkampfgruppe'] != '':
                        self.checked_Bahn_1.set(True)
                        self.switchBahn1State()
                        self.__root.G1.config(text=dg['wettkampfgruppe'])
                        self.anzeige.G1.config(text=dg['wettkampfgruppe'])
                        self.id_time_1 = 'typ.row.column_' + str(dg['typ']) + '_' + str(dg['row']) + '_' + str(dg['column'])
                    elif count == 2 and dg['wettkampfgruppe'] != '...' and dg['wettkampfgruppe'] != '':
                        self.checked_Bahn_2.set(True)
                        self.switchBahn2State()
                        self.__root.G2.config(text=dg['wettkampfgruppe'])
                        self.anzeige.G2.config(text=dg['wettkampfgruppe'])
                        self.id_time_2 = 'typ.row.column_' + str(dg['typ']) + '_' + str(dg['row']) + '_' + str(dg['column'])
                    count += 1
        
        self.__root.BtnStart['state'] = NORMAL

    def switchBahn1State(self):
        if self.checked_Bahn_1.get() == False:
            self.__root.G1['state'] = DISABLED
            self.__root.T1['state'] = DISABLED
            self.__root.F1['state'] = DISABLED
            self.__root.B1['state'] = DISABLED
            self.anzeige.G1.pack_forget()
            self.anzeige.Z1.pack_forget()
            self.writeKonsole('Bahn 1 wurde deaktiviert!')
        else:
            self.__root.G1['state'] = NORMAL
            self.__root.T1['state'] = NORMAL
            self.__root.F1['state'] = NORMAL
            self.__root.B1['state'] = NORMAL
            self.anzeige.G1.pack(expand=0, side=TOP, fill=X)
            self.anzeige.Z1.pack(expand=1, side=TOP, fill=BOTH)
            self.writeKonsole('Bahn 1 wurde aktiviert!')

    def switchBahn2State(self):
        if self.checked_Bahn_2.get() == False:
            self.__root.G2['state'] = DISABLED
            self.__root.T2['state'] = DISABLED
            self.__root.F2['state'] = DISABLED
            self.__root.B2['state'] = DISABLED
            self.anzeige.G2.pack_forget()
            self.anzeige.Z2.pack_forget()
            self.writeKonsole('Bahn 2 wurde deaktiviert!')
        else:
            self.__root.G2['state'] = NORMAL
            self.__root.T2['state'] = NORMAL
            self.__root.F2['state'] = NORMAL
            self.__root.B2['state'] = NORMAL
            self.anzeige.G2.pack(expand=0, side=BOTTOM, fill=X)
            self.anzeige.Z2.pack(expand=1, side=TOP, fill=BOTH)
            self.writeKonsole('Bahn 2 wurde aktiviert!')

    def startBuzzer1(self, event=None):
        if not self.time_is_running_1:
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
        if not self.time_is_running_2:
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

    def start(self):   
        self.__root.BtnStart['state'] = DISABLED
        self.__root.BtnAllesStop['state'] = NORMAL
        self.__root.BtnWechsel['state'] = DISABLED
        self.__root.BtnReset['state'] = DISABLED

        self.writeKonsole('Der Angriffbefehl wurde erteilt!')
        # os.system('mpg123 ' + self.file_angriffbefehel)
        if self.checked_GPIO.get() == True and self.checked_Bahn_1.get() == True:
            self.GPIO_Start_1 = self.__root.Start_GPIO_1.get()
            self.GPIO_Stop_1 = self.__root.Stop_GPIO_1.get()
            self.BuzzerStartBahn1 = GPIO_Button(self.GPIO_Start_1)
            self.BuzzerStopBahn1 = GPIO_Button(self.GPIO_Stop_1)
            self.BuzzerStartBahn1.when_pressed = self.startBuzzer1

        if self.checked_GPIO.get() == True and self.checked_Bahn_2.get() == True:
            self.GPIO_Start_2 = self.__root.Start_GPIO_2.get()
            self.GPIO_Stop_2 = self.__root.Stop_GPIO_2.get()
            self.BuzzerStartBahn2 = GPIO_Button(self.GPIO_Start_2)
            self.BuzzerStopBahn2 = GPIO_Button(self.GPIO_Stop_2)
            self.BuzzerStartBahn2.when_pressed = self.startBuzzer2

        if self.checked_Tastatur.get() == True and self.checked_Bahn_1.get() == True:
            self.Taste_Start_1 = self.__root.Start_Taste_1.get()
            self.Taste_Stop_1 = self.__root.Stop_Taste_1.get()
            self.__root.bind(self.Taste_Start_1, self.startBuzzer1)
        
        if self.checked_Tastatur.get() == True and self.checked_Bahn_2.get() == True:
            self.Taste_Start_2 = self.__root.Start_Taste_2.get()
            self.Taste_Stop_2 = self.__root.Stop_Taste_2.get()
            self.__root.bind(self.Taste_Start_2, self.startBuzzer2)

    def stop_1(self, event=None):
        self.time_is_running_1 = False
        if self.checked_Tastatur.get() == True:
            self.__root.unbind(self.Taste_Stop_1)
            if event != None and event != '':
                self.writeKonsole('Zeit 1 mit Taste ' + event.char + ' angehalten!')
        if self.checked_GPIO.get() == True and event == None:
            self.writeKonsole('Zeit 1 mit Buzzer bzw Button angehalten!')
        if self.time_is_running_1 == False and self.time_is_running_2 == False:
            self.__root.BtnAllesStop['state'] = DISABLED
            self.__root.BtnWechsel['state'] = NORMAL
            self.__root.BtnReset['state'] = NORMAL

    def stop_2(self, event=None):
        self.time_is_running_2 = False
        if self.checked_Tastatur.get() == True:
            self.__root.unbind(self.Taste_Stop_2)
            if event != None and event != '':
                self.writeKonsole('Zeit 2 mit Taste ' + event.char + ' angehalten!')
        if self.checked_GPIO.get() == True and event == None:
            self.writeKonsole('Zeit 1 mit Buzzer bzw Button angehalten!')
        if self.time_is_running_1 == False and self.time_is_running_2 == False:
            self.__root.BtnAllesStop['state'] = DISABLED
            self.__root.BtnWechsel['state'] = NORMAL
            self.__root.BtnReset['state'] = NORMAL

    def reset(self):
        self.werteInAnsichtUebertragen()
        self.__root.T1.config(text='00:00:00')
        self.__root.T2.config(text='00:00:00')
        self.anzeige.Z1.config(text='00:00:00')
        self.anzeige.Z2.config(text='00:00:00')
        self.__root.BtnStart['state'] = NORMAL
        self.__root.BtnReset['state'] = DISABLED
        self.writeKonsole('Zeit und Button zurückgesetzt!')

    def update_time_1(self):
        if self.time_is_running_1:
            elapsed_time = time.time() - self.start_time_1
            dt = datetime.fromtimestamp(elapsed_time).strftime('%M:%S:%f')[:-4]
            self.__root.T1.config(text=dt)
            self.anzeige.Z1.config(text=dt)
            self.__root.T1.after(50, self.update_time_1)
        else:
            self.stop_time_1 = time.time()

    def update_time_2(self):
        if self.time_is_running_2:
            elapsed_time = time.time() - self.start_time_2
            dt = datetime.fromtimestamp(elapsed_time).strftime('%M:%S:%f')[:-4]
            self.__root.T2.config(text=dt)
            self.anzeige.Z2.config(text=dt)
            self.__root.T2.after(50, self.update_time_2)
        else:
            self.stop_time_2 = time.time()

    def switchKonsoleState(self):
        if (self.checked_Konsole.get() == False):
            self.__root.Konsole.config(text='')
        else:
            self.__root.Konsole.config(text='Konsole: ')

    def writeKonsole(self, text):
        if (self.checked_Konsole.get() == True):
            self.__root.Konsole.config(text='Konsole: ' + text)

    def wechselAnsichtZurZeit(self):
        self.anzeige.ERG.pack_forget()
        self.anzeige.G1.pack(expand=0, side=TOP, fill=X)
        self.anzeige.Z1.pack(expand=1, side=TOP, fill=BOTH)
        self.anzeige.Z2.pack(expand=1, side=TOP, fill=BOTH)
        self.anzeige.G2.pack(expand=0, side=BOTTOM, fill=X)

    def wechselAnsichtZurAuswertung(self):
        self.anzeige.G1.pack_forget()
        self.anzeige.Z1.pack_forget()
        self.anzeige.Z2.pack_forget()
        self.anzeige.G2.pack_forget()
        self.anzeige.ERG.pack(expand=1, side=TOP, fill=BOTH)

Hauptfenster()