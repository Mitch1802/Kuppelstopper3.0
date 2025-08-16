from tkinter import *
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from gui.custom_table import CustomTable
from models import Gruppe
from managers.gruppen_manager import GruppenManager
from managers.durchgang_manager import DurchgangManager
from managers.zeitnehmung_manager import ZeitManager


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
        self.checked_Test = BooleanVar()

        self.checked_Bahn_1.set(False)
        self.checked_Bahn_2.set(False)
        self.checked_Tastatur.set(True)
        self.checked_GPIO.set(False)
        self.checked_Rahmen.set(False)
        self.checked_Konsole.set(True)
        self.checked_Test.set(False)

        self.gruppen_manager = GruppenManager()
        self.durchgang_manager = DurchgangManager()
        self.zeit_manager = ZeitManager()

        self.coldata_gruppen = ["Gruppenname", "Damen", "Reihenfolge", ""]
        self.coldata_bewerb = ["DG","Gruppe","Zeit1","F1","Zeit2","F2","Bestzeit inkl. Fehler"]
        self.coldata_rang = ["Platzierung", "Gruppe", "Bestzeit inkl. Fehler"]

        self.cell_types_gruppen = ["label", "label", "entry", "button"]
        self.cell_types_bewerb = ["label", "label", "label", "label", "label", "label","label"]
        self.cell_types_rang = ["label", "label", "label"]

        self.commands_gruppen = [None, self.change_damentyp, None, self.del_wettkampfgruppe]
        self.commands_bewerb = [None, self.change_durchgang_gruppe, None, None, None, None, None]
        self.commands_rang = [None, None, None]

        self.percent_widths_gruppen = [75, 10, 10, 10]
        self.percent_widths_bewerb = [5, 20, 20, 5, 20, 5, 20]
        self.percent_widths_rang = [20, 50, 20]

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

        self.btn_bewerb_starten = tb.Button(frame, text="Bewerb starten", command=self.gruppen_uebernehmen, takefocus=0)
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
        test = self.checked_Test.get()
        self.gruppen_manager.speichere_anmeldung()
        ang_gruppen = self.gruppen_manager.gruppen_uebernehmen()
        self.durchgang_manager.uebernehme_angemeldete_gruppen(ang_gruppen)
        self.lade_grunddurchgang(test)
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
        frame_zeitnehmung_frame = self.create_sub_zeitnehmung()
        frame_zeitnehmung_frame.pack(fill=BOTH, side=BOTTOM)

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

        frame_zeitnehmung = tb.Frame(frame)
        frame_zeitnehmung.pack(fill=BOTH, side=LEFT)

        btn = tb.Button(frame_zeitnehmung, text='Ansicht Wechsel', width=20, bootstyle=INFO, takefocus = 0, command=self.ansicht_umschalten) 
        btn.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        self.btn_dg_vorheriger = tb.Button(frame_zeitnehmung, text='<<<', width=10, bootstyle=WARNING, takefocus = 0, command=self.dg_vorheriger) 
        self.btn_dg_vorheriger.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        self.lbl_dg_number = tb.Label(frame_zeitnehmung, text="1", font=("Arial", 30)) 
        self.lbl_dg_number.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        self.btn_naechster_dg = tb.Button(frame_zeitnehmung, text='>>>', bootstyle=WARNING, width=10, takefocus = 0, command=self.dg_naechster) 
        self.btn_naechster_dg.pack(fill=BOTH, side=LEFT, padx=5, pady=5) 
        self.btn_start = tb.Button(frame_zeitnehmung, text='Start', width=15, takefocus = 0, command=self.start, state=DISABLED)
        self.btn_start.pack(fill=BOTH, side=LEFT, padx=5, pady=5) 
        self.btn_alles_stop = tb.Button(frame_zeitnehmung, text='Alles Stop', width=15, takefocus = 0, command=self.alles_stop, state=DISABLED)
        self.btn_alles_stop.pack(fill=BOTH, side=LEFT, padx=5, pady=5) 
        self.btn_bahn_wechsel = tb.Button(frame_zeitnehmung, text='Bahn Wechsel', width=15, takefocus = 0, command=self.bahnwechsel, state=DISABLED)
        self.btn_bahn_wechsel.pack(fill=BOTH, side=LEFT, padx=5, pady=5) 
        self.btn_zeit_uebertragen = tb.Button(frame_zeitnehmung, text='Zeit übertragen', width=15, takefocus = 0, command=self.zeit_uebertragen, state=DISABLED)
        self.btn_zeit_uebertragen.pack(fill=BOTH, side=LEFT, padx=5, pady=5) 

        frame_bahnen = tb.Frame(frame)
        frame_bahnen.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        
        # self.cb_bahn1 = tb.Checkbutton(frame_bahnen, text='Bahn 1', variable=self.checked_Bahn_1, takefocus = 0) #, command=self.switchBahn1State, takefocus = 0)
        # self.cb_bahn1.grid(row=0, column=0, padx=10)
        self.lbl_bahn1_ = tb.Label(frame_bahnen, text='B 1') #, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), takefocus = 0, state=DISABLED)
        self.lbl_bahn1_.grid(row=0, column=0, padx=10, sticky=W)
        self.lbl_bahn1_gruppe = tb.Label(frame_bahnen, text='...') #, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), takefocus = 0, state=DISABLED)
        self.lbl_bahn1_gruppe .grid(row=0, column=1, padx=10, sticky=W)
        self.lbl_bahn1_zeit = tb.Label(frame_bahnen, text='00:00:00') #, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), takefocus = 0, state=DISABLED)
        self.lbl_bahn1_zeit.grid(row=0, column=2, padx=10)
        self.ent_bahn1_fehler = tb.Entry(frame_bahnen, width=5, takefocus = 0)
        self.ent_bahn1_fehler.grid(row=0, column=3, padx=10)
        self.btn_bahn1_stop = tb.Button(frame_bahnen, text='Stop', width=10, command=self.bahn1_stop, state=DISABLED)
        self.btn_bahn1_stop.grid(row=0, column=4)

        # self.cb_bahn2 = tb.Checkbutton(frame_bahnen, text='Bahn 2', variable=self.checked_Bahn_2, takefocus = 0) #, command=self.switchBahn2State, takefocus = 0)
        # self.cb_bahn2.grid(row=1, column=0, padx=10)
        self.lbl_bahn2_ = tb.Label(frame_bahnen, text='B 2') #, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), takefocus = 0, state=DISABLED)
        self.lbl_bahn2_.grid(row=1, column=0, padx=10, sticky=W)
        self.lbl_bahn2_gruppe = tb.Label(frame_bahnen, text='...') #, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), takefocus = 0, state=DISABLED)
        self.lbl_bahn2_gruppe.grid(row=1, column=1, padx=10, sticky=W)
        self.lbl_bahn2_zeit = tb.Label(frame_bahnen, text='00:00:00') #, font=(self.GlobalFontArt, self.GlobalFontSizeTitle), takefocus = 0, state=DISABLED)
        self.lbl_bahn2_zeit.grid(row=1, column=2, padx=10)
        self.ent_bahn2_fehler = tb.Entry(frame_bahnen, width=5, takefocus = 0)
        self.ent_bahn2_fehler.grid(row=1, column=3, padx=10)
        self.btn_bahn2_stop = tb.Button(frame_bahnen, text='Stop', width=10, command=self.bahn2_stop, state=DISABLED)
        self.btn_bahn2_stop.grid(row=1, column=4)

        frame_korrektur = tb.Frame(frame)
        frame_korrektur.pack(fill=BOTH, side=LEFT)

        self.btn_stop_reset = tb.Button(frame_korrektur, text='Stop and Reset', width=15, takefocus = 0, command=self.stop_und_reset) #, state=DISABLED)
        self.btn_stop_reset.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        self.btn_zeit1_loeschen = tb.Button(frame_korrektur, text='Zeit 1+2 löschen', width=15, takefocus = 0, command=self.zeit_1_und_2_loeschen)
        self.btn_zeit1_loeschen.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        self.btn_zeit2_loeschen = tb.Button(frame_korrektur, text='Zeit 2 löschen', width=15, takefocus = 0, command=self.zeit_2_loeschen) 
        self.btn_zeit2_loeschen.pack(fill=BOTH, side=LEFT, padx=5, pady=5)

        return frame
    
    def lade_grunddurchgang(self, test):
        daten_gd = self.durchgang_manager.lade_grunddurchgang(test)
        self.tbl_gd_bewerb_update(daten_gd)

        daten_gd_platzierung = self.durchgang_manager.sort_tbl_rang_daten(self.durchgang_manager.TypGD)
        self.tbl_gd_rang_update(daten_gd_platzierung)

        self.btn_dg_vorheriger['state'] = DISABLED
        gruppen_start = self.durchgang_manager.lade_gruppen_von_durchgang(1)

        self.lbl_bahn1_gruppe.config(text=gruppen_start[0])
        self.lbl_bahn2_gruppe.config(text=gruppen_start[1])

        self.zeitnehmung_buttons_control(True, False, False, False, False, False, False, False, False)

    def change_durchgang_gruppe(self, data):
        self.durchgang_manager.change_werte(data)

    def ansicht_umschalten(self):
        # TODO Ansicht Umschalten
        pass

    def dg_vorheriger(self):
        dg_alt = int(self.lbl_dg_number.cget('text'))
        dg_neu = dg_alt - 1
        self.lbl_dg_number.config(text=dg_neu)

        mod_a = self.durchgang_manager.wandle_durchgang_in_modus(dg_alt)
        mod_b = self.durchgang_manager.wandle_durchgang_in_modus(dg_neu)
        if mod_a != mod_b:
            sub_tab_name = self.wandle_typ_in_ansicht(mod_b)
            self.show_bewerb_subtab(sub_tab_name)

        self.lade_durchgang_von_dgnumber(dg_neu)

    def dg_naechster(self):
        dg_alt = int(self.lbl_dg_number.cget('text'))
        dg_neu = dg_alt + 1
        self.lbl_dg_number.config(text=dg_neu)

        mod_a = self.durchgang_manager.wandle_durchgang_in_modus(dg_alt)
        mod_b = self.durchgang_manager.wandle_durchgang_in_modus(dg_neu)
        if mod_a != mod_b:
            sub_tab_name = self.wandle_typ_in_ansicht(mod_b)
            self.show_bewerb_subtab(sub_tab_name)

        self.lade_durchgang_von_dgnumber(dg_neu)
    
    def wandle_typ_in_ansicht(self, typ):
        mapping = {
            self.durchgang_manager.TypGD: 'Grunddurchgang',
            self.durchgang_manager.TypKO16: 'KO 1-16',
            self.durchgang_manager.TypKO8: 'KO 1-8',
            self.durchgang_manager.TypKO4: 'KO 1-4',
            self.durchgang_manager.TypKF: 'Finale',
            self.durchgang_manager.TypF: 'Finale'

        }  
        return mapping.get(typ)

    def lade_durchgang_von_dgnumber(self, durchgang):
        dg_min = 1
        dg_max = self.durchgang_manager.get_max_dgnumber()

        if durchgang == dg_min: 
            self.btn_dg_vorheriger['state'] = DISABLED
            self.btn_naechster_dg['state'] = NORMAL
        elif durchgang == dg_max: 
            self.btn_dg_vorheriger['state'] = NORMAL
            self.btn_naechster_dg['state'] = DISABLED
        else: 
            self.btn_dg_vorheriger['state'] = NORMAL
            self.btn_naechster_dg['state'] = NORMAL

        gruppen_start = self.durchgang_manager.lade_gruppen_von_durchgang(durchgang)

        self.checked_Bahn_1 = True
        self.lbl_bahn1_zeit.config(text='00:00:00')
        self.ent_bahn1_fehler['state'] = NORMAL
        self.lbl_bahn1_gruppe.config(text=gruppen_start[0])

        if gruppen_start[1] != '': 
            self.checked_Bahn_2 = True
            self.lbl_bahn2_zeit.config(text='00:00:00')
            self.ent_bahn2_fehler['state'] = NORMAL
            self.lbl_bahn2_gruppe.config(text=gruppen_start[1])
        else: 
            self.checked_Bahn_2 = False
            self.lbl_bahn2_zeit.config(text='')
            self.ent_bahn2_fehler['state'] = DISABLED
            self.lbl_bahn2_gruppe.config(text='')

        self.zeitnehmung_buttons_control(True, False, False, False, False, False, False, False, False)

    def start(self):
        # TODO Start Zeitnehmung
        self.zeitnehmung_buttons_control(False, True, False, False, True, True, True, False, False)

    def alles_stop(self):
        # TODO Stop Zeitnehmung
        self.zeitnehmung_buttons_control(False, False, False, True, False, False, False, True, True)

    def bahnwechsel(self):
        # TODO Bahnwechsel
        self.zeitnehmung_buttons_control(True, False, False, False, False, False, False, False, False)

    def zeit_uebertragen(self):
        durchgang = '1' # Wert aus Label
        zeit_a = '00:00:00'
        fehler_a = '0'
        zeit_b = '00:00:00'
        fehler_b = '0'
        modus = self.durchgang_manager.wandle_durchgang_in_modus(durchgang)

        self.durchgang_manager.zeiten_an_bewerb_uebergeben(durchgang, zeit_a, fehler_a, zeit_b, fehler_b)
        self.durchgang_manager.berechne_bestzeiten()

        daten_bewerb = self.durchgang_manager.filter_bewerb(modus)
        daten_rang = self.durchgang_manager.sort_tbl_rang_daten(modus)

        # TODO Tabellen aktueller Modus neu zeichnen und Topgruppen in nächste Runde übertragen
        # TODO Wenn Testzeiten angehakt dann zufallszeiten generieren
        self.zeitnehmung_buttons_control(True, False, False, False, False, False, False, False, False)


    def bahn1_stop(self):
        # TODO Bahn 1 Stop
        pass

    def bahn2_stop(self):
        # TODO Bahn 2 Stop
        pass

    def zeit_reset(self):
        self.lbl_bahn1_zeit.config(text='00:00:00')
        self.lbl_bahn2_zeit.config(text='00:00:00')

    def stop_und_reset(self):
        self.alles_stop()
        self.zeitnehmung_buttons_control(True, False, False, False, False, False, False, False, False)
        self.zeit_reset()

    def zeit_1_und_2_loeschen(self):
        # TODO DG Alle Zeiten löschen
        self.zeitnehmung_buttons_control(True, False, False, False, False, False, False, False, False)

    def zeit_2_loeschen(self):
        # TODO DG Zeit 2 löschen
        self.zeitnehmung_buttons_control(True, False, False, False, False, False, False, False, False)

    def zeitnehmung_buttons_control(self, start, alles_stop, bahn_wechsel, zeit_uebertragen, bahn1_stop, bahn2_stop, stop_reset, zeit1_loeschen, zeit2_loeschen):
        button_mapping = [
            (start, self.btn_start),
            (alles_stop, self.btn_alles_stop),
            (bahn_wechsel, self.btn_bahn_wechsel),
            (zeit_uebertragen, self.btn_zeit_uebertragen),
            (bahn1_stop, self.btn_bahn1_stop),
            (bahn2_stop, self.btn_bahn2_stop),
            (stop_reset, self.btn_stop_reset),
            (zeit1_loeschen, self.btn_zeit1_loeschen),
            (zeit2_loeschen, self.btn_zeit2_loeschen)
        ]

        for condition, button in button_mapping:
            button['state'] = NORMAL if condition else DISABLED

    # Einstellungen Tab
    def create_settings_tab(self):
        frame = tb.Frame(self.tab_container)

        label = tb.Label(frame, text="Einstellungen", font=("Arial", 20))
        label.pack(padx=10, pady=10, anchor=W)

        label = tb.Label(frame, text="Eingabe", font=("Arial", 15))
        label.pack(padx=10, pady=10, anchor=W)

        sub_frame = tb.Frame(frame)
        sub_frame.pack(fill=X, padx=10, pady=10)

        cb = tb.Checkbutton(sub_frame, text="Tastatur", variable=self.checked_Tastatur, bootstyle="round-toggle")
        cb.pack(side=LEFT, padx=10, pady=10)

        cb = tb.Checkbutton(sub_frame, text="GPIO", variable=self.checked_GPIO, bootstyle="round-toggle")
        cb.pack(side=LEFT, padx=10, pady=10)

        cb = tb.Checkbutton(sub_frame, text="Rahmen ausblenden", variable=self.checked_Rahmen, bootstyle="round-toggle")
        cb.pack(side=LEFT, padx=10, pady=10)

        cb = tb.Checkbutton(sub_frame, text="Konsole", variable=self.checked_Konsole, bootstyle="round-toggle")
        cb.pack(side=LEFT, padx=10, pady=10)

        cb = tb.Checkbutton(sub_frame, text="Testgruppen", variable=self.checked_Test, command=self.testframe_anzeigen, bootstyle="round-toggle")
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

        self.frame_test = tb.Frame(frame)

        label = tb.Label(self.frame_test, text="Test", font=("Arial", 15))
        label.pack(padx=10, pady=(20,10), anchor=W)

        label = tb.Label(self.frame_test, text="Anzahl Testgruppen")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        self.test_gruppen_anzahl = tb.Entry(self.frame_test, width=5)
        self.test_gruppen_anzahl.pack(side=LEFT, padx=(5,10), pady=10)

        label = tb.Label(self.frame_test, text="Anzahl Damengruppen")
        label.pack(side=LEFT, padx=(10,0), pady=10, anchor=W)

        self.test_damen_anzahl = tb.Entry(self.frame_test, width=5)
        self.test_damen_anzahl.pack(side=LEFT, padx=(5,10), pady=10)

        # TODO Testzeiten während Bewerb erstellen

        btn = tb.Button(self.frame_test, text="Erstellen", takefocus=0, command=self.testgruppen_hinzufuegen)
        btn.pack(side=LEFT, padx=10, pady=10)

        return frame
    
    def testframe_anzeigen(self):
        if self.checked_Test.get():
            self.frame_test.pack(fill=X, padx=10, pady=10)
        else: 
            self.frame_test.destroy()

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

    def tbl_gd_bewerb_update(self, daten):
        """Filtert Daten und updatet die Tabellendaten"""
        daten_neu = self.durchgang_manager.filter_tbl_bewerb_daten(daten)
        self.tbl_gd_bewerb.set_data(daten_neu)

    def tbl_gd_rang_update(self, daten):
        """Filtert Daten und updatet die Tabellendaten"""
        daten_neu = self.durchgang_manager.filter_tbl_rang_daten(daten)
        self.tbl_gd_rang.set_data(daten_neu)

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
