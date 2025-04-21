import os, sys, pygame
from customtkinter import *
from PIL import Image

import config, gui, events

# Klasse für den Hauptcontroller
class Kuppelstopper:
    def __init__(self):
        # Initialisiere pygame und Pfade
        pygame.init()
        self.pfad = os.path.dirname(os.path.abspath(sys.argv[0])).replace('\\', '/')
        self.LogFile = os.path.join(self.pfad, 'log.txt')
        self.KonfigGruppenFile = os.path.join(self.pfad, 'config/anmeldung.json')
        self.KonfigBewerbFile = os.path.join(self.pfad, 'config/bewerb.json')
        self.KonfigSetupFile = os.path.join(self.pfad, 'config/setup.json')
        self.KonfigThemeFile = os.path.join(self.pfad, 'config/theme.json')

        # Konfiguration laden (über Funktion aus config.py)
        self.ladeKonfiguration()

        # Standard-UI-Einstellungen (z.B. Farbthema, Erscheinungsbild)
        set_default_color_theme(self.KonfigThemeFile)
        set_appearance_mode("light")

        # Initialisiere Statusvariablen, Konstanten etc.
        config.init_var(self)

        # Weitere Variablen initialisieren ...
        # self.Durchgänge = []
        # self.Wettkampfgruppen = []
        # self.DGNumbers = []
        self.DurchgangNummer = 1
        self.AnzahlGrunddurchgänge = 0

        self.AnzeigeGDStartRow = 0
        self.AnzeigeGDStartColumn = 0

        self.AnzeigeKO16StartRow = 0
        self.AnzeigeKO16StartColumn = 8
        self.AnzeigeKO8StartRow = 18
        self.AnzeigeKO8StartColumn = 8
        self.AnzeigeKO4StartRow = 30
        self.AnzeigeKO4StartColumn = 8
        
        self.AnzeigeKFStartRow = 0
        self.AnzeigeKFStartColumn = 17
        self.AnzeigeFStartRow = 4
        self.AnzeigeFStartColumn = 17
        self.AnzeigeDWStartRow = 8
        self.AnzeigeDWStartColumn = 17

        self.ZeitUebertragen = False
        self.Buzzer1DarfStarten = False
        self.time_is_running_1 = False
        self.start_time_1 = ''
        self.stop_time_1 = ''
        self.id_time_1 = ''
        self.Buzzer1DarfStarten = False
        self.time_is_running_2 = False
        self.start_time_2 = ''
        self.stop_time_2 = ''
        self.id_time_2 = ''
        
        # Erstelle das Hauptfenster
        self.root = CTk()
        self.root.title(self.Title)

        self.iconDelete = CTkImage(light_image=Image.open(self.FileIconDelete), dark_image=Image.open(self.FileIconDelete))
        self.screen_height = self.root.winfo_height()
        self.screen_width = self.root.winfo_width()

        # Weitere Variablen (z. B. für Checkboxen) setzen
        self.checked_Bahn_1 = BooleanVar(value=False)
        self.checked_Bahn_2 = BooleanVar(value=False)
        self.checked_Tastatur = BooleanVar(value=True)
        self.checked_GPIO = BooleanVar(value=False)
        self.checked_Rahmen = BooleanVar(value=False)
        self.checked_Konsole = BooleanVar(value=True)
        
        # GUI-Aufbau (Funktionen aus gui.py)
        # gui.init_gui(self)
        gui.create_tabs(self)
        gui.create_tab1(self)
        gui.create_tab2(self)
        gui.create_tab3(self)
        gui.init_anzeige(self)
        
        # Falls bereits Gruppen vorhanden sind, übernehme diese
        if len(self.Durchgänge) > 0:
            events.uebernahme_gruppen(self, True)
        
    def ladeKonfiguration(self):
        # Lösche alte Log File
        if os.path.exists(self.LogFile):
            os.remove(self.LogFile)

        # Lade Wettkampfgruppen
        if os.path.exists(self.KonfigGruppenFile):
            self.Wettkampfgruppen = config.lade_konfiguration(self.KonfigGruppenFile)
        else:
            self.Wettkampfgruppen = []

        # Lade Bewerbsdaten
        if os.path.exists(self.KonfigBewerbFile):
            data = config.lade_konfiguration(self.KonfigBewerbFile)
            self.Durchgänge = data.get('Bewerb', [])
            self.DGNumbers = data.get('DGNumbers', [])
        else:
            self.Durchgänge = []
            self.DGNumbers = []
        
        # Setze weitere Attribute wie GPIO/PINs, Tasten etc.
        # (Diese Informationen müssen aus deiner Setup-Konfiguration übernommen werden.)

        config_data = config.lade_konfiguration(self.KonfigSetupFile)
        
        setup = config_data.get('Setup')
        self.Title = setup.get('Title', 'Kuppelstopper')
        self.TitleAnzeige = setup.get('TitleAnzeige', 'Anzeige')
        self.ZeigeAlleZeiten = setup.get('ZeigeAlleZeiten', False)
        self.Testmodus = setup.get('Testmodus', False)
        self.PlaySound = setup.get('PlaySound', False)

        files = config_data.get('Files')
        self.FileAngriffsbefehl = os.path.join(self.pfad, 'Resources', files.get('angriffsbefehl'))
        self.FileStopp = os.path.join(self.pfad, 'Resources', files.get('stopp'))
        self.FileIcon = os.path.join(self.pfad, 'Resources', files.get('icon'))
        self.FileIconDelete = os.path.join(self.pfad, 'Resources', files.get('iconDelete'))

        buttons = config_data.get('Buttons')
        self.GPIO_Start_1 = buttons.get('GPIO_Start_1', 17)
        self.GPIO_Stop_1 = buttons.get('GPIO_Stop_1', 27)
        self.GPIO_Start_2 = buttons.get('GPIO_Start_2', 19)
        self.GPIO_Stop_2 = buttons.get('GPIO_Stop_2', 26)
        self.Taste_Start_1 = buttons.get('Taste_Start_1', 'a')
        self.Taste_Stop_1 = buttons.get('Taste_Stop_1', 'q')
        self.Taste_Start_2 = buttons.get('Taste_Start_2', 's')
        self.Taste_Stop_2 = buttons.get('Taste_Stop_2', 'w')

        style = config_data.get('Style')
        self.GlobalFontArt = style.get('GlobalFontArt', 'Arial')
        self.GlobalFontSizeText = style.get('GlobalFontSizeText', 10)
        self.GlobalFontSizeTitle = style.get('GlobalFontSizeTitle', 15)
        self.GlobalDGBackgroundColor = style.get('GlobalDGBackgroundColor', '#FFFFFF')
        self.AnzeigeFontSizeGroup = style.get('AnzeigeFontSizeGroup', 100)
        self.AnzeigeFontSizeTime = style.get('AnzeigeFontSizeTime', 300)
        self.AnzeigeFontSizeInfo = style.get('AnzeigeFontSizeInfo', 25)
        self.AnzeigeFontSizeAuswertung = style.get('AnzeigeFontSizeAuswertung', 20)
        self.AnzeigeBackgroundColor = style.get('AnzeigeBackgroundColor', '#FFFFFF')
        self.AnzeigeGroupColor = style.get('AnzeigeGroupColor', '#000000')
        self.AnzeigeGroup2Color = style.get('AnzeigeGroup2Color', '#000000')
        self.AnzeigeTimeColor = style.get('AnzeigeTimeColor', '#000000')
        self.AnzeigeNextColor = style.get('AnzeigeNextColor', '#FFFFFF')
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Kuppelstopper()
    app.run()
