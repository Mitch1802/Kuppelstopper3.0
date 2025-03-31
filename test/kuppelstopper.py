import os, sys, time, json, re, random
from tkinter import messagebox
from customtkinter import *
from datetime import datetime
from threading import Thread
import pygame
from gpiozero import Button as GPIO_Button
from PIL import Image

# Importiere Funktionen aus den anderen Modulen
from config import lade_konfiguration, export_anmeldung_konfig, export_bewerb_konfig
from gui import init_gui, create_tabs, create_tab1, create_tab2, create_tab3, show_anzeige
from time_manager import update_time_1, update_time_2, addiere_fehler_zur_zeit, bestzeit_platzierung_berechnen, reset_timers
from events import add_wettkampfgruppe, zeichne_angemeldete_gruppen, uebernahme_gruppen, switch_bahn1_state, switch_bahn2_state, bahn_wechsel, werte_uebertragen
from utils import validate_time, validate_number, is_number, write_konsole

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
        self.Status_Anzeige = True  # True = Zeit, False = Auswertung
        self.TYP_GD = '1_GD'
        self.TYP_KO16 = '2_KO16'
        self.TYP_KO8 = '3_KO8'
        self.TYP_KO4 = '4_KO4'
        self.TYP_KF = '5_KLF'
        self.TYP_F = '6_F'
        self.TYP_DW = '7_DW'

        self.NAME_TAB1 = 'Anmeldung'
        self.NAME_TAB2 = 'Übersicht - Zeitnehmung'
        self.NAME_TAB3 = 'Einstellungen'

        # Weitere Variablen initialisieren ...
        self.Durchgänge = []
        self.Wettkampfgruppen = []
        self.DGNumbers = []
        
        # Erstelle das Hauptfenster
        self.__root = CTk()
        self.__root.title(self.Title)
        # Beispiel: Icon laden (Dateipfad muss in der Konfiguration definiert sein)
        self.iconDelete = CTkImage(light_image=Image.open(self.FileIconDelete), dark_image=Image.open(self.FileIconDelete))

        # Weitere Variablen (z. B. für Checkboxen) setzen
        self.checked_Bahn_1 = BooleanVar(value=False)
        self.checked_Bahn_2 = BooleanVar(value=False)
        self.checked_Tastatur = BooleanVar(value=True)
        self.checked_GPIO = BooleanVar(value=False)
        self.checked_Rahmen = BooleanVar(value=False)
        self.checked_Konsole = BooleanVar(value=True)
        
        # GUI-Aufbau (Funktionen aus gui.py)
        init_gui(self)
        create_tabs(self)
        create_tab1(self)
        create_tab2(self)
        create_tab3(self)
        
        # Weitere Initialisierungen (z. B. GPIO, Anzeige)
        self.initGPIO()
        show_anzeige(self)
        
        # Falls bereits Gruppen vorhanden sind, übernehme diese
        if len(self.Durchgänge) > 0:
            uebernahme_gruppen(self, True)
        
    def ladeKonfiguration(self):
        # Lade Konfigurationen über die Funktion aus config.py
        config_data = lade_konfiguration(self.KonfigSetupFile)
        # Setze relevante Attribute, z. B.:
        self.Title = config_data.get('Title', 'Kuppelstopper')
        self.TitleAnzeige = config_data.get('TitleAnzeige', 'Anzeige')
        self.PlaySound = config_data.get('PlaySound', False)
        # ... weitere Attribute setzen (Dateipfade, Tastenbelegungen, Style, etc.)
        # Ebenso: Lade Wettkampfgruppen und Durchgänge aus den entsprechenden Dateien
        if os.path.exists(self.KonfigGruppenFile):
            with open(self.KonfigGruppenFile, "r") as f:
                self.Wettkampfgruppen = json.load(f)
        else:
            self.Wettkampfgruppen = []
        if os.path.exists(self.KonfigBewerbFile):
            with open(self.KonfigBewerbFile, "r") as f:
                data = json.load(f)
                self.Durchgänge = data.get('Bewerb', [])
                self.DGNumbers = data.get('DGNumbers', [])
        else:
            self.Durchgänge = []
            self.DGNumbers = []
        
        # Setze weitere Attribute wie GPIO/PINs, Tasten etc.
        # (Diese Informationen müssen aus deiner Setup-Konfiguration übernommen werden.)
        # Beispiel:
        self.FileIconDelete = config_data['Files'].get('iconDelete')
        self.GPIO_Start_1 = config_data['Buttons'].get('GPIO_Start_1')
        # usw.
    
    def initGPIO(self, event=None):
        if self.checked_GPIO.get():
            self.BuzzerStartBahn1 = GPIO_Button(self.GPIO_Start_1)
            self.BuzzerStopBahn1 = GPIO_Button(self.GPIO_Stop_1)
            self.BuzzerStartBahn2 = GPIO_Button(self.GPIO_Start_2)
            self.BuzzerStopBahn2 = GPIO_Button(self.GPIO_Stop_2)
    
    def run(self):
        self.__root.mainloop()
    
    # Die restlichen Methoden (z. B. Start, Stop, Timer-Updates, Event-Handler) können
    # entweder direkt in dieser Klasse bleiben oder über Funktionen in time_manager.py und events.py abgewickelt werden.
    # Beispiel:
    def start(self, event=None):
        # Setze Statusvariablen
        self.ZeitUebertragen = False
        # Starte Sound (in einem Thread, siehe events.py oder direkt hier)
        t = Thread(target=self.playSound, args=[self.FileAngriffsbefehl])
        t.start()
        # Weitere Logik...
        # Starte Timer (update_time_1 und update_time_2 aus time_manager.py)
        update_time_1(self)
        update_time_2(self)
    
    def playSound(self, file):
        if self.PlaySound:
            write_konsole(self, 'Ein Sound wurde wiedergegeben!')
            sound = pygame.mixer.Sound(file)
            sound.play()

    # ... weitere Methoden, die du ggf. in die Module in events.py, time_manager.py usw. auslagerst.

if __name__ == "__main__":
    app = Kuppelstopper()
    app.run()
