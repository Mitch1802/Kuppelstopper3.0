from tkinter import *
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from gui.custom_table import CustomTable
from models import Gruppe
from managers.gruppen_manager import GruppenManager
from managers.durchgang_manager import DurchgangManager


class MainView(tb.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("Kuppelstopper 3.0")
        self.minsize(1600, 1000)

        #  TODO Icon App

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

        self.gruppen_manager = GruppenManager()
        self.durchgang_manager = DurchgangManager()

        self.coldata_gruppen = ["Gruppenname", "Damen", "Reihenfolge", ""]
        self.coldata_bewerb = ["DG","Gruppe","Zeit1","Fehler1","Zeit2","Fehler2","Bestzeit inkl. Fehler"]
        self.coldata_rang = ["Platzierung", "Gruppe", "Bestzeit inkl. Fehler"]

        self.cell_types_gruppen = ["label", "label", "entry", "button"]
        self.cell_types_bewerb = ["label", "label", "label", "label", "label", "label","button"]
        self.cell_types_rang = ["label", "label", "label"]

        self.commands_gruppen = [None, self.change_damentyp, None, self.del_wettkampfgruppe]
        self.commands_bewerb = [None, self.change_durchgang_gruppe, None, None, None, None, None]
        self.commands_rang = [None, None, None]

        self.percent_widths_gruppen = [70, 10, 10, 10]
        self.percent_widths_bewerb = [5, 20, 20, 5, 20, 5, 20]
        self.percent_widths_rang = [10, 60, 30]

        self.setup_ui()

    def setup_ui(self):
        # Container für die Buttons
        button_frame = tb.Frame(self, bootstyle="primary")
        button_frame.pack(fill=X, side=TOP)

        # Container für die "Tabs"
        self.tab_container = tb.Frame(self)
        self.tab_container.pack(fill=BOTH, expand=YES)

        # Erstelle Tab-Inhalte (Frames)
        self.tabs = {
            "Anmeldung": self.create_anmeldung_tab(),
            "Bewerb": self.create_bewerb_tab(),
            "Einstellungen": self.create_settings_tab(),
            "Info": self.create_info_tab()
        }

        # Tab Buttons speichern
        self.tab_buttons = {}

        for name in self.tabs:
            btn = tb.Button(button_frame, text=name, command=lambda n=name: self.show_tab(n), compound=LEFT, takefocus=False)
            btn.pack(side=LEFT, ipadx=5, ipady=5)
            self.tab_buttons[name] = btn

        self.show_tab("Anmeldung") # Standardansicht
    
    def show_tab(self, name):
        # Tabs anzeigen
        for frame in self.tabs.values():
            frame.pack_forget()
        self.tabs[name].pack(fill=BOTH, expand=True)

        # Buttons einfärben
        for n, btn in self.tab_buttons.items():
            style = DARK if n == name else PRIMARY
            btn.configure(bootstyle=style)

    # Anmeldung Tab
    def create_anmeldung_tab(self):
        frame = tb.Frame(self.tab_container)

        label = tb.Label(frame, text="Wettkampfgruppen", font=("Arial", 20))
        label.pack(padx=10, pady=(10, 0), anchor=W)

        entry_frame = tb.Frame(frame)
        entry_frame.pack(fill=X, pady=1, side=TOP)

        self.ent_anmeldung = tb.Entry(entry_frame)
        self.ent_anmeldung.pack(side=LEFT, fill=X, padx=10, pady=10, expand=True)
        self.ent_anmeldung.bind('<Return>', self.add_wettkampfgruppe)

        btn = tb.Button(entry_frame, text='Hinzufügen', compound=LEFT, command=self.add_wettkampfgruppe, takefocus=0)
        btn.pack(side=LEFT, fill=X, padx=10, pady=10)

        self.tbl_gruppen = CustomTable(frame, self.coldata_gruppen, [], self.percent_widths_gruppen, cell_types=self.cell_types_gruppen, commands=self.commands_gruppen)

        self.btn_bewerb_starten = tb.Button(frame, text="Bewerb starten", command=self.gruppen_uebernehmen)
        self.btn_bewerb_starten.pack(side=BOTTOM, fill=X, padx=10, pady=10)

        frame.bind("<Configure>", lambda e, obj=self.tbl_gruppen: self.tbl_build(obj))

        return frame
    
    def add_wettkampfgruppe(self, event=None):
        """Liest Eingaben aus und speichert die Gruppe über den Manager."""
        name = self.ent_anmeldung.get()
        if name:
            gruppe = Gruppe(name, 'NEIN', 0)
            self.gruppen_manager.gruppe_hinzufuegen(gruppe)
            self.tbl_gruppen_update()
            self.ent_anmeldung.delete(0, END)

    def change_damentyp(self, data):
        """Ändert den Typ der Wettkampgruppe, ob Damengruppe oder nicht"""
        self.gruppen_manager.gruppe_aendern(data)
        self.tbl_gruppen_update()

    def del_wettkampfgruppe(self, data):
        """Lösch eine angemeldete Wettkampfgruppe"""
        self.gruppen_manager.gruppe_loeschen(data)
        self.tbl_gruppen_update()

    def gruppen_uebernehmen(self):
        """Übernimmt die angemeldeten Gruppen für den Bewerb"""
        self.gruppen_manager.speichere_anmeldung()
        ang_gruppen = self.gruppen_manager.gruppen_uebernehmen()
        self.durchgang_manager.uebernehme_angemeldete_gruppen(ang_gruppen)
        self.lade_grunddurchgang()
        self.show_tab("Bewerb")

    # Bewerb Tab
    def create_bewerb_tab(self):
        frame = tb.Frame(self.tab_container)

        # Container für die Buttons
        button_frame = tb.Frame(frame, bootstyle="dark")
        button_frame.pack(fill=X, side=TOP)

        # Container für die "Sub Tabs"
        self.subtab_container = tb.Frame(frame)
        self.subtab_container.pack(fill=BOTH, side=TOP, expand=True)

        # Container für Zeitnehmung
        self.zeitnehmung_frame = self.create_sub_zeitnehmung()
        self.zeitnehmung_frame.pack(fill=BOTH, side=BOTTOM)

        # Erstelle Tab-Inhalte (Frames)
        self.subtabs = {
            "Grunddurchgang": self.create_gd_subtab(),
            "KO 1-16": self.create_ko16_subtab(),
            "KO 1-8": self.create_ko8_subtab(),
            "KO 1-4": self.create_ko4_subtab(),
            "Finale": self.create_finale_subtab()
        }

        # Tab Buttons speichern
        self.subtab_buttons = {}

        # Buttons zur Auswahl der Tabs
        for name in self.subtabs:
            btn = tb.Button(button_frame, text=name, command=lambda n=name: self.show_bewerb_subtab(n), compound=LEFT, takefocus=False, bootstyle="dark")
            btn.pack(fill=X, side=LEFT, ipadx=5, ipady=5, expand=True)
            self.subtab_buttons[name] = btn

        self.show_bewerb_subtab("Grunddurchgang")  # Standardansicht

        return frame
    
    def create_gd_subtab(self):
        frame = tb.Frame(self.subtab_container)

        frame_left = tb.Frame(frame)
        frame_left.pack(side=LEFT, fill=BOTH, expand=True)

        self.tbl_gd_bewerb = CustomTable(frame_left, self.coldata_bewerb, [], self.percent_widths_bewerb, cell_types=self.cell_types_bewerb, commands=self.commands_bewerb)
        frame_left.bind("<Configure>", lambda e, obj=self.tbl_gd_bewerb: self.tbl_build(obj))

        frame_right = tb.Frame(frame)
        frame_right.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.tbl_gd_rang = CustomTable(frame_right, self.coldata_rang, [], self.percent_widths_rang, cell_types=self.cell_types_rang, commands=self.commands_rang)
        frame_right.bind("<Configure>", lambda e, obj=self.tbl_gd_rang: self.tbl_build(obj))

        return frame
    
    def create_ko16_subtab(self):
        frame = tb.Frame(self.subtab_container)

        frame_left = tb.Frame(frame)
        frame_left.pack(side=LEFT, fill=BOTH, expand=True)

        self.tbl_ko16_bewerb = CustomTable(frame_left, self.coldata_bewerb, [], self.percent_widths_bewerb, cell_types=self.cell_types_bewerb, commands=self.commands_bewerb)
        frame_left.bind("<Configure>", lambda e, obj=self.tbl_ko16_bewerb: self.tbl_build(obj))

        frame_right = tb.Frame(frame)
        frame_right.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.tbl_ko16_rang = CustomTable(frame_right, self.coldata_rang, [], self.percent_widths_rang, cell_types=self.cell_types_rang, commands=self.commands_rang)
        frame_right.bind("<Configure>", lambda e, obj=self.tbl_ko16_rang: self.tbl_build(obj))

        return frame
    
    def create_ko8_subtab(self):
        frame = tb.Frame(self.subtab_container)

        frame_left = tb.Frame(frame)
        frame_left.pack(side=LEFT, fill=BOTH, expand=True)

        self.tbl_ko8_bewerb = CustomTable(frame_left, self.coldata_bewerb, [], self.percent_widths_bewerb, cell_types=self.cell_types_bewerb, commands=self.commands_bewerb)
        frame_left.bind("<Configure>", lambda e, obj=self.tbl_ko8_bewerb: self.tbl_build(obj))

        frame_right = tb.Frame(frame)
        frame_right.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.tbl_ko8_rang = CustomTable(frame_right, self.coldata_rang, [], self.percent_widths_rang, cell_types=self.cell_types_rang, commands=self.commands_rang)
        frame_right.bind("<Configure>", lambda e, obj=self.tbl_ko8_rang: self.tbl_build(obj))

        return frame
    
    def create_ko4_subtab(self):
        frame = tb.Frame(self.subtab_container)

        frame_left = tb.Frame(frame)
        frame_left.pack(side=LEFT, fill=BOTH, expand=True)

        self.tbl_ko4_bewerb = CustomTable(frame_left, self.coldata_bewerb, [], self.percent_widths_bewerb, cell_types=self.cell_types_bewerb, commands=self.commands_bewerb)
        frame_left.bind("<Configure>", lambda e, obj=self.tbl_ko4_bewerb: self.tbl_build(obj))

        frame_right = tb.Frame(frame)
        frame_right.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.tbl_ko4_rang = CustomTable(frame_right, self.coldata_rang, [], self.percent_widths_rang, cell_types=self.cell_types_rang, commands=self.commands_rang)
        frame_right.bind("<Configure>", lambda e, obj=self.tbl_ko4_rang: self.tbl_build(obj))

        return frame
    
    def create_finale_subtab(self):
        frame = tb.Frame(self.subtab_container)

        frame_left = tb.Frame(frame)
        frame_left.pack(side=LEFT, fill=BOTH, expand=True)

        self.tbl_finale_bewerb = CustomTable(frame_left, self.coldata_bewerb, [], self.percent_widths_bewerb, cell_types=self.cell_types_bewerb, commands=self.commands_bewerb)
        frame_left.bind("<Configure>", lambda e, obj=self.tbl_finale_bewerb: self.tbl_build(obj))

        frame_right = tb.Frame(frame)
        frame_right.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.tbl_finale_rang = CustomTable(frame_right, self.coldata_rang, [], self.percent_widths_rang, cell_types=self.cell_types_rang, commands=self.commands_rang)
        frame_right.bind("<Configure>", lambda e, obj=self.tbl_finale_rang: self.tbl_build(obj))

        return frame
    
    def show_bewerb_subtab(self, name):
        # Tabs anzeigen
        for frame in self.subtabs.values():
            frame.pack_forget()
        self.subtabs[name].pack(fill=BOTH, expand=YES)

        # Buttons einfärben
        for n, btn in self.subtab_buttons.items():
            style = SECONDARY if n == name else DARK
            btn.configure(bootstyle=style)

    def create_sub_zeitnehmung(self):
        frame = tb.Frame(self.subtab_container)

        self.zeitnehmung = tb.Frame(frame)
        self.zeitnehmung.pack(fill=BOTH, side=LEFT)

        self.BtnAnsichtWechseln = tb.Button(self.zeitnehmung, text='Ansicht Wechsel', width=20, bootstyle=INFO, takefocus = 0) #, command=self.anzeigeUmschalten, takefocus = 0)
        self.BtnAnsichtWechseln.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        self.BtnVorherigerDG = tb.Button(self.zeitnehmung, text='DG -', width=10, bootstyle=WARNING, takefocus = 0) #, command=self.vorherigerDG, takefocus = 0)
        self.BtnVorherigerDG.pack(fill=BOTH, side=LEFT, padx=5, pady=5)  
        # self.CBDG = tb.Combobox(self.zeitnehmung, width=5, takefocus = 0, textvariable=StringVar(), state=READONLY, justify=CENTER)
        # self.CBDG = Combobox(self.zeitnehmung, textvariable=StringVar(), state='readonly', width=5, takefocus = 0, justify='center')
        # self.CBDG.bind('<<ComboboxSelected>>',self.ladeZeitnehmungsDaten)
        # self.CBDG.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        self.DG = tb.Label(self.zeitnehmung, text="99", font=("Arial", 30)) 
        self.DG.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        self.BtnNaechsterDG = tb.Button(self.zeitnehmung, text='DG +', bootstyle=WARNING, width=10, takefocus = 0) #, command=self.naechsterDG, takefocus = 0)
        self.BtnNaechsterDG.pack(fill=BOTH, side=LEFT, padx=5, pady=5) 
        self.BtnStart = tb.Button(self.zeitnehmung, text='Start', width=15, takefocus = 0) #, command=self.start, takefocus = 0, state=DISABLED)
        self.BtnStart.pack(fill=BOTH, side=LEFT, padx=5, pady=5) 
        self.BtnAllesStop = tb.Button(self.zeitnehmung, text='Alles Stop', width=15, takefocus = 0) #, command=self.allesStop, takefocus = 0, state=DISABLED)
        self.BtnAllesStop.pack(fill=BOTH, side=LEFT, padx=5, pady=5) 
        self.BtnWechsel = tb.Button(self.zeitnehmung, text='Bahn Wechsel', width=15, takefocus = 0) #, command=self.bahnWechsel, takefocus = 0, state=DISABLED)
        self.BtnWechsel.pack(fill=BOTH, side=LEFT, padx=5, pady=5) 
        self.BtnZeitUebertragen = tb.Button(self.zeitnehmung, text='Zeit übertragen', width=15, takefocus = 0) #, command=self.werteInAnsichtUebertragen, takefocus = 0, state=DISABLED)
        self.BtnZeitUebertragen.pack(fill=BOTH, side=LEFT, padx=5, pady=5) 

        self.LfBahnen = tb.Frame(frame)
        self.LfBahnen.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        
        self.CB1 = tb.Checkbutton(self.LfBahnen, text='Bahn 1', variable=self.checked_Bahn_1, takefocus = 0) #, command=self.switchBahn1State, takefocus = 0)
        self.CB1.grid(row=0, column=0, padx=10)
        self.G1 = tb.Label(self.LfBahnen, text='...') #, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), takefocus = 0, state=DISABLED)
        self.G1 .grid(row=0, column=1, padx=10, sticky=W)
        self.T1 = tb.Label(self.LfBahnen, text='00:00:00') #, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), takefocus = 0, state=DISABLED)
        self.T1.grid(row=0, column=2, padx=10)
        self.F1 = tb.Entry(self.LfBahnen, width=5, takefocus = 0)
        self.F1.grid(row=0, column=3, padx=10)
        self.B1 = tb.Button(self.LfBahnen, text='Stop', width=10) #, command=self.stop_1, takefocus = 0, state=DISABLED)
        self.B1.grid(row=0, column=4)

        self.CB2 = tb.Checkbutton(self.LfBahnen, text='Bahn 2', variable=self.checked_Bahn_2, takefocus = 0) #, command=self.switchBahn2State, takefocus = 0)
        self.CB2.grid(row=1, column=0, padx=10)
        self.G2 = tb.Label(self.LfBahnen, text='...') #, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), takefocus = 0, state=DISABLED)
        self.G2 .grid(row=1, column=1, padx=10, sticky=W)
        self.T2 = tb.Label(self.LfBahnen, text='00:00:00') #, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), takefocus = 0, state=DISABLED)
        self.T2.grid(row=1, column=2, padx=10)
        self.F2 = tb.Entry(self.LfBahnen, width=5, takefocus = 0)
        self.F2.grid(row=1, column=3, padx=10)
        self.B2 = tb.Button(self.LfBahnen, text='Stop', width=10) #, command=self.stop_2, takefocus = 0, state=DISABLED)
        self.B2.grid(row=1, column=4)

        self.korrektur = tb.Frame(frame)
        self.korrektur.pack(fill=BOTH, side=LEFT)

        self.BtnStopReset = tb.Button(self.korrektur, text='Stop and Reset', width=15, takefocus = 0) #, command=self.stopreset, takefocus = 0, state=DISABLED)
        self.BtnStopReset.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        self.BtnLoeZ1 = tb.Button(self.korrektur, text='Zeit 1+2 löschen', width=15, takefocus = 0) #, command=self.zeit1loeschen, takefocus = 0)
        self.BtnLoeZ1.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        self.BtnLoeZ2 = tb.Button(self.korrektur, text='Zeit 2 löschen', width=15, takefocus = 0) #, command=self.zeit2loeschen, takefocus = 0)
        self.BtnLoeZ2.pack(fill=BOTH, side=LEFT, padx=5, pady=5)

        return frame
    
    def lade_grunddurchgang(self):
        self.durchgang_manager.lade_grunddurchgang()

    def change_durchgang_gruppe(self):
        pass

    # Einstellungen Tab
    def create_settings_tab(self):
        frame = tb.Frame(self.tab_container)

        label = tb.Label(frame, text="Einstellungen", font=("Arial", 20))
        label.pack(padx=10, pady=10, anchor=W)

        label = tb.Label(frame, text="Eingabe", font=("Arial", 15))
        label.pack(padx=10, pady=10, anchor=W)

        sub_frame = tb.Frame(frame)
        sub_frame.pack(fill=X, padx=10, pady=10)

        cb = tb.Checkbutton(sub_frame, text="Tastatur", bootstyle="round-toggle")
        cb.pack(side=LEFT, padx=10, pady=10)

        cb = tb.Checkbutton(sub_frame, text="GPIO", bootstyle="round-toggle")
        cb.pack(side=LEFT, padx=10, pady=10)

        cb = tb.Checkbutton(sub_frame, text="Rahmen ausblenden", bootstyle="round-toggle")
        cb.pack(side=LEFT, padx=10, pady=10)

        cb = tb.Checkbutton(sub_frame, text="Konsole", bootstyle="round-toggle")
        cb.pack(side=LEFT, padx=10, pady=10)

        cb = tb.Checkbutton(sub_frame, text="Testgruppen", bootstyle="round-toggle")
        cb.pack(side=LEFT, padx=10, pady=10)

        label = tb.Label(frame, text="Tasten", font=("Arial", 15))
        label.pack(padx=10, pady=(20,10), anchor=W)

        sub_frame = tb.Frame(frame)
        sub_frame.pack(fill=X, padx=10, pady=10)

        label = tb.Label(sub_frame, text="Start Bahn 1")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        ent = tb.Entry(sub_frame, width=5)
        ent.pack(side=LEFT, padx=(5,10), pady=10)

        label = tb.Label(sub_frame, text="Stopp Bahn 1")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        ent = tb.Entry(sub_frame, width=5)
        ent.pack(side=LEFT, padx=(5,10), pady=10)

        label = tb.Label(sub_frame, text="Start Bahn 2")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        ent = tb.Entry(sub_frame, width=5)
        ent.pack(side=LEFT, padx=(5,10), pady=10)

        label = tb.Label(sub_frame, text="Stopp Bahn 2")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        ent = tb.Entry(sub_frame, width=5)
        ent.pack(side=LEFT, padx=(5,10), pady=10)

        label = tb.Label(frame, text="GPIO", font=("Arial", 15))
        label.pack(padx=10, pady=(20,10), anchor=W)

        sub_frame = tb.Frame(frame)
        sub_frame.pack(fill=X, padx=10, pady=10)

        label = tb.Label(sub_frame, text="Start Bahn 1")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        ent = tb.Entry(sub_frame, width=5)
        ent.pack(side=LEFT, padx=(5,10), pady=10)

        label = tb.Label(sub_frame, text="Stopp Bahn 1")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        ent = tb.Entry(sub_frame, width=5)
        ent.pack(side=LEFT, padx=(5,10), pady=10)

        label = tb.Label(sub_frame, text="Start Bahn 2")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        ent = tb.Entry(sub_frame, width=5)
        ent.pack(side=LEFT, padx=(5,10), pady=10)

        label = tb.Label(sub_frame, text="Stopp Bahn 2")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        ent = tb.Entry(sub_frame, width=5)
        ent.pack(side=LEFT, padx=(5,10), pady=10)

        label = tb.Label(frame, text="Style", font=("Arial", 15))
        label.pack(padx=10, pady=(20,10), anchor=W)

        sub_frame = tb.Frame(frame)
        sub_frame.pack(fill=X, padx=10, pady=10)

        label = tb.Label(sub_frame, text="Schriftgröße Zeit")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        ent = tb.Entry(sub_frame, width=5)
        ent.pack(side=LEFT, padx=(5,10), pady=10)

        label = tb.Label(sub_frame, text="Schriftgröße Gruppe")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        ent = tb.Entry(sub_frame, width=5)
        ent.pack(side=LEFT, padx=(5,10), pady=10)

        btn = tb.Button(sub_frame, text="Schriftgröße Autoanpassung", takefocus=0)
        btn.pack(side=LEFT, padx=10, pady=10)

        label = tb.Label(frame, text="Test", font=("Arial", 15))
        label.pack(padx=10, pady=(20,10), anchor=W)

        sub_frame = tb.Frame(frame)
        sub_frame.pack(fill=X, padx=10, pady=10)

        label = tb.Label(sub_frame, text="Anzahl Testgruppen")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        self.test_gruppen_anzahl = tb.Entry(sub_frame, width=5)
        self.test_gruppen_anzahl.pack(side=LEFT, padx=(5,10), pady=10)

        label = tb.Label(sub_frame, text="Anzahl Damengruppen")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        self.test_damen_anzahl = tb.Entry(sub_frame, width=5)
        self.test_damen_anzahl.pack(side=LEFT, padx=(5,10), pady=10)

        btn = tb.Button(sub_frame, text="Erstellen", takefocus=0, command=self.testgruppen_hinzufuegen)
        btn.pack(side=LEFT, padx=10, pady=10)

        return frame
    
    def testgruppen_hinzufuegen(self):     
        """Erstellt die angemeldeteten Gruppen aufgrund der Anzahl"""
        anzahl = self.test_gruppen_anzahl.get()
        damenAnzahl = self.test_damen_anzahl.get()
        self.gruppen_manager.testgruppen_hinzufuegen(self, anzahl, damenAnzahl)
        self.tbl_gruppen_update()
        self.test_gruppen_anzahl.delete(0, END)
        self.test_damen_anzahl.delete(0, END)
        self.show_tab("Anmeldung")
    
    # Info Tab
    def create_info_tab(self):
        frame = tb.Frame(self.tab_container)

        label = tb.Label(frame, text="Information", font=("Arial", 20))
        label.pack(padx=10, pady=(10,20), anchor=W)

        label = tb.Label(frame, text="Version: 3.0")
        label.pack(padx=10, pady=0, anchor=W)

        label = tb.Label(frame, text="Entwickler: Michael Reichenauer, FF Schwadorf")
        label.pack(padx=10, pady=0, anchor=W)

        label = tb.Label(frame, text="E-Mail: michael.reichenauer@feuerwehr.gv.at")
        label.pack(padx=10, pady=0, anchor=W)

        return frame

    # Hilfsfunktionen Tables
     
    def tbl_sort(self, bedingung1, bedingung2):
        """Kann die Tabellen grunddaten sortieren nach Bedingung 1  bzw Bedingung 2"""
        pass

    def tbl_build(self, table_object):
        """Erstellt und packt eine Tabelle """
        height = table_object.master.winfo_height()
        if height < 100:
            self.after(100, lambda: self.tbl_build(table_object))
            return

        table_object._build_table()
        table_object.pack(fill=BOTH, expand=YES, padx=10, pady=10)
    
    def tbl_gruppen_update(self):
        """Holt aktuelle Daten und updaten die Tabellendaten"""
        daten_neu = self.gruppen_manager.get_gruppen()
        self.tbl_gruppen.set_data(daten_neu)

    def tbl_gd_bewerb_update(self):
        """Holt aktuelle Daten und updaten die Tabellendaten"""
        # daten_neu = self.durchgang_manager.get_gruppen()
        daten_neu = []
        self.tbl_gruppen.set_data(daten_neu)

    def tbl_gd_rang_update(self):
        pass

    def tbl_ko16_bewerb_update(self):
        pass

    def tbl_ko16_rang_update(self):
        pass

    def tbl_ko8_bewerb_update(self):
        pass

    def tbl_ko8_rang_update(self):
        pass

    def tbl_ko4_bewerb_update(self):
        pass

    def tbl_ko4_rang_update(self):
        pass

    def tbl_finale_bewerb_update(self):
        pass

    def tbl_finale_rang_update(self):
        pass