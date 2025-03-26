import sys
import os
import json
import re
import random
import time
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Union, Callable

import pygame
import customtkinter as ctk
from tkinter import messagebox
from gpiozero import Button as GPIO_Button
from PIL import Image

# Logging konfigurieren und altes Logfile löschen
LOG_FILENAME = "log.txt"
if os.path.exists(LOG_FILENAME):
    os.remove(LOG_FILENAME)
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')
logging.info("Programmstart")

# --- Helferfunktionen ---
def validate_time(test_str: str) -> bool:
    """
    Validiert, ob ein String im Format MM:SS:MS vorliegt.
    """
    pattern = r'^\d{2}:\d{2}:\d{2}$'
    if re.match(pattern, test_str):
        minutes, seconds, _ = map(int, test_str.split(':'))
        return minutes <= 59 and seconds <= 59
    return False

def validate_number(test_str: str) -> bool:
    """
    Prüft, ob der String eine ganze Zahl darstellt.
    """
    return test_str.isdigit()

# --- Konfigurationsverwaltung ---
class ConfigurationManager:
    """
    Verwaltet das Laden und Speichern der Konfigurationen.
    """
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.config_dir = self.base_path / "config"
        self.anmeldung_file = self.config_dir / "anmeldung.json"
        self.bewerb_file = self.config_dir / "bewerb.json"
        self.setup_file = self.config_dir / "setup.json"
        self.theme_file = self.base_path / "config" / "theme.json"
        self.wettkampfgruppen = []
        self.durchgaenge = []
        self.dg_numbers = []
        self.setup_data = {}
        self.load_configurations()

    def load_json(self, file_path: Path) -> Union[dict, list]:
        """Lädt JSON-Daten aus der Datei, gibt bei Fehler ein leeres Objekt zurück."""
        try:
            with file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Fehler beim Laden von {file_path}: {e}")
            return {} if file_path.suffix == ".json" else []

    def load_configurations(self):
        """Lädt alle Konfigurationen."""
        self.wettkampfgruppen = self.load_json(self.anmeldung_file) or []
        bewerb = self.load_json(self.bewerb_file)
        self.durchgaenge = bewerb.get("Bewerb", []) if isinstance(bewerb, dict) else []
        self.dg_numbers = bewerb.get("DGNumbers", []) if isinstance(bewerb, dict) else []
        self.setup_data = self.load_json(self.setup_file)
        logging.info("Konfigurationen geladen.")

    def export_anmeldung_config(self):
        """Exportiert die Gruppenkonfiguration."""
        try:
            with self.anmeldung_file.open("w", encoding="utf-8") as f:
                json.dump(self.wettkampfgruppen, f, indent=4, ensure_ascii=False)
            logging.info("Anmeldung-Konfiguration exportiert.")
        except Exception as e:
            logging.error(f"Fehler beim Exportieren der Anmeldung-Konfiguration: {e}")

    def export_bewerb_config(self):
        """Exportiert die Bewerbskonfiguration."""
        data = {"Bewerb": self.durchgaenge, "DGNumbers": self.dg_numbers}
        try:
            with self.bewerb_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logging.info("Bewerb-Konfiguration exportiert.")
        except Exception as e:
            logging.error(f"Fehler beim Exportieren der Bewerb-Konfiguration: {e}")

# --- Timer- und Zeitberechnungslogik ---
class TimerManager:
    """
    Enthält Funktionen zum Starten, Aktualisieren und Vergleichen von Zeiten.
    """
    @staticmethod
    def format_elapsed_time(elapsed: float) -> str:
        dt = datetime.fromtimestamp(elapsed).strftime('%M:%S:%f')[:-4]
        return dt

    @staticmethod
    def add_error_to_time(time_str: str, error: Union[int, str]) -> str:
        """
        Fügt einer Zeit (im Format MM:SS:MS) einen Fehlerwert hinzu.
        """
        try:
            minutes, seconds, ms = map(int, time_str.split(":"))
            seconds += int(error)
            if seconds > 59:
                minutes += seconds // 60
                seconds = seconds % 60
            return f"{minutes:02d}:{seconds:02d}:{ms:02d}"
        except Exception as e:
            logging.error(f"Fehler beim Addieren des Fehlers: {e}")
            return time_str

    @staticmethod
    def compare_times(time1: str, time2: str) -> int:
        """
        Vergleicht zwei Zeiten im Format MM:SS:MS.
        Gibt 1 zurück, wenn time1 schneller ist, sonst 2.
        """
        def to_centiseconds(t: str) -> int:
            m, s, ms = map(int, t.split(":"))
            return ((m * 60) + s) * 100 + ms
        return 1 if to_centiseconds(time1) < to_centiseconds(time2) else 2

# --- GUI-Logik und Ereignisbindung ---
class GUIManager:
    """
    Baut die grafische Oberfläche auf, verwaltet Events und steuert die Anzeige.
    """
    def __init__(self, config_manager: ConfigurationManager):
        self.config = config_manager
        # Verwende pathlib und setze den Icon-Pfad
        self.base_path = self.config.base_path
        self.icon_path = self.base_path / self.config.setup_data.get("Files", {}).get("icon", "icon.ico")
        self.icon_delete_path = self.base_path / self.config.setup_data.get("Files", {}).get("iconDelete", "delete.png")
        # Initialisiere customtkinter und setze den Theme
        ctk.set_default_color_theme(str(self.config.theme_file))
        ctk.set_appearance_mode("light")
        self.root = ctk.CTk()
        self.root.title(self.config.setup_data.get("Setup", {}).get("Title", "Kuppelstopper"))
        self._init_state_variables()
        self._init_gpio()
        self._build_ui()
        self._create_display_window()
        self.root.mainloop()

    def _init_state_variables(self):
        """Initialisiert interne Statusvariablen und GUI-Variablen."""
        self.status_display = True  # True: Zeit, False: Auswertung
        self.checked_bahn_1 = ctk.BooleanVar(value=False)
        self.checked_bahn_2 = ctk.BooleanVar(value=False)
        self.checked_keyboard = ctk.BooleanVar(value=True)
        self.checked_gpio = ctk.BooleanVar(value=False)
        self.checked_console = ctk.BooleanVar(value=True)
        # Timervariablen
        self.time_running_1 = False
        self.start_time_1 = 0.0
        self.time_running_2 = False
        self.start_time_2 = 0.0
        self.id_time_1 = ""
        self.id_time_2 = ""
        # Weitere Zustände und Konfigurationen
        self.play_sound_flag = self.config.setup_data.get("Setup", {}).get("PlaySound", False)
        self.global_font = self.config.setup_data.get("Style", {}).get("GlobalFontArt", "Arial")
        self.global_font_size_title = self.config.setup_data.get("Style", {}).get("GlobalFontSizeTitle", 16)
        # Beispielhafte Farbwerte, können aus der Konfiguration geladen werden
        self.display_bg_color = self.config.setup_data.get("Style", {}).get("AnzeigeBackgroundColor", "#222222")

    def _init_gpio(self):
        """Initialisiert GPIO, falls aktiviert."""
        if self.checked_gpio.get():
            try:
                buttons = self.config.setup_data.get("Buttons", {})
                self.buzzer_start_1 = GPIO_Button(int(buttons.get("GPIO_Start_1", 17)))
                self.buzzer_stop_1 = GPIO_Button(int(buttons.get("GPIO_Stop_1", 27)))
                self.buzzer_start_2 = GPIO_Button(int(buttons.get("GPIO_Start_2", 22)))
                self.buzzer_stop_2 = GPIO_Button(int(buttons.get("GPIO_Stop_2", 23)))
                logging.info("GPIO initialisiert.")
            except Exception as e:
                logging.error(f"Fehler bei der GPIO-Initialisierung: {e}")

    def _build_ui(self):
        """Erstellt das Hauptfenster und die Tabs."""
        # Erstelle ein Tabview
        self.tab_view = ctk.CTkTabview(self.root, anchor='nw', corner_radius=0, fg_color='transparent')
        self.tab_view.pack(expand=True, side='top', fill='both', padx=5, pady=5)
        # Tabs: Anmeldung, Übersicht, Einstellungen
        self.tab_anmeldung = self.tab_view.add("Anmeldung")
        self.tab_zeit = self.tab_view.add("Übersicht - Zeitnehmung")
        self.tab_einstellungen = self.tab_view.add("Einstellungen")
        # Baue die einzelnen Tabs
        self._build_anmeldung_tab()
        self._build_zeit_tab()
        self._build_einstellungen_tab()

    def _build_anmeldung_tab(self):
        """Erstellt den Anmeldung-Tab."""
        self.entry_group = ctk.CTkEntry(self.tab_anmeldung, corner_radius=0, placeholder_text='Gruppenname')
        self.entry_group.pack(side='top', fill='x', padx=10, pady=10)
        self.entry_group.bind('<Return>', self.add_wettkampfgruppe)
        # Scrollbares Frame für Gruppenliste
        self.frame_groups = ctk.CTkScrollableFrame(self.tab_anmeldung, border_width=0, corner_radius=0, fg_color='transparent')
        self.frame_groups.pack(expand=True, side='top', fill='both', padx=10, pady=10)
        self._draw_wettkampfgruppen()
        self.btn_import = ctk.CTkButton(self.tab_anmeldung, text='Gruppen übernehmen', command=lambda: self.import_groups(reset_evaluation=True), corner_radius=0)
        self.btn_import.pack(side='bottom', fill='x', padx=10, pady=10)

    def _build_zeit_tab(self):
        """Erstellt den Zeitnehmungs-Tab (Auswahl, Start/Stopp etc.)."""
        # Hier ein minimales Beispiel – die komplette Logik der Zeitnahme (Tabellen etc.) muss noch modularisiert werden
        self.frame_zeit_controls = ctk.CTkFrame(self.tab_zeit, border_width=0, fg_color='transparent')
        self.frame_zeit_controls.pack(side='top', fill='x', padx=5, pady=20)
        self.btn_start = ctk.CTkButton(self.frame_zeit_controls, text='Start', command=self.start_timer, state='disabled', corner_radius=0)
        self.btn_start.pack(side='left', padx=5, pady=20)
        self.btn_stop_all = ctk.CTkButton(self.frame_zeit_controls, text='Alles Stop', command=self.stop_all_timers, state='disabled', corner_radius=0)
        self.btn_stop_all.pack(side='left', padx=5, pady=20)

    def _build_einstellungen_tab(self):
        """Erstellt den Einstellungen-Tab."""
        self.frame_settings = ctk.CTkFrame(self.tab_einstellungen, border_width=1, corner_radius=0, fg_color='transparent')
        self.frame_settings.pack(side='top', fill='x', padx=10, pady=5)
        self.chk_keyboard = ctk.CTkCheckBox(self.frame_settings, text='Tastatur', variable=self.checked_keyboard)
        self.chk_keyboard.grid(row=0, column=0, padx=10, pady=10)
        self.chk_gpio = ctk.CTkCheckBox(self.frame_settings, text='GPIO', variable=self.checked_gpio, command=self._init_gpio)
        self.chk_gpio.grid(row=0, column=1, padx=10, pady=10)
        # Weitere Einstellungen können hier ergänzt werden

    def _create_display_window(self):
        """Erstellt ein separates Anzeigefenster für Zeiten und Gruppen."""
        self.display = ctk.CTkToplevel(self.root)
        self.display.title(self.config.setup_data.get("Setup", {}).get("TitleAnzeige", "Anzeige"))
        self.display.minsize(700, 400)
        self.display.configure(fg_color=self.display_bg_color)
        self.frame_display = ctk.CTkFrame(self.display, border_width=0, corner_radius=0, fg_color=self.display_bg_color)
        self.frame_display.pack(expand=True, side=ctk.TOP, fill=ctk.BOTH, padx=20, pady=20)
        # Beispielhafte Labels für Gruppen- und Zeitanzeige
        self.label_group_left = ctk.CTkLabel(self.frame_display, text='...', anchor='nw',
                                              font=(self.global_font, self.global_font_size_title))
        self.label_time_left = ctk.CTkLabel(self.frame_display, text='00:00:00', anchor='center',
                                             font=(self.global_font, self.global_font_size_title))
        self.label_group_left.pack(expand=False, side=ctk.TOP, fill=ctk.X)
        self.label_time_left.pack(expand=True, side=ctk.TOP, fill=ctk.BOTH)

    # --- Funktionen für Gruppenverwaltung ---
    def add_wettkampfgruppe(self, event=None):
        """Fügt eine neue Wettkampfgruppe hinzu."""
        name = self.entry_group.get().strip()
        if not name:
            messagebox.showerror('Fehlermeldung', 'Bitte einen Namen eingeben!')
            return
        if any(grp.get("gruppenname") == name for grp in self.config.wettkampfgruppen):
            messagebox.showerror('Fehlermeldung', 'Gruppenname bereits vorhanden!')
            return
        if len(self.config.wettkampfgruppen) >= 30:
            messagebox.showerror('Fehlermeldung', 'Maximal 30 Gruppen erlaubt!')
            return
        new_group = {"gruppenname": name, "reihenfolge": "", "damenwertung": False}
        self.config.wettkampfgruppen.append(new_group)
        self.entry_group.delete(0, ctk.END)
        self._draw_wettkampfgruppen()
        logging.info(f"Gruppe '{name}' wurde hinzugefügt.")

    def _draw_wettkampfgruppen(self):
        """Zeichnet die Liste der angemeldeten Gruppen neu."""
        for widget in self.frame_groups.winfo_children():
            widget.destroy()
        if not self.config.wettkampfgruppen:
            label = ctk.CTkLabel(self.frame_groups, text='Keine Gruppen angemeldet!')
            label.pack(padx=10, pady=5)
        else:
            headers = ["Gruppenname", "Reihenf.", "Damen"]
            for i, header in enumerate(headers):
                lbl = ctk.CTkLabel(self.frame_groups, text=header)
                lbl.grid(row=0, column=i, padx=10, pady=2)
            for index, group in enumerate(self.config.wettkampfgruppen, start=1):
                lbl_name = ctk.CTkLabel(self.frame_groups, text=group.get("gruppenname"))
                lbl_name.grid(row=index, column=0, padx=10, pady=2, sticky="w")
                entry_reihenfolge = ctk.CTkEntry(self.frame_groups, width=50, justify='center')
                entry_reihenfolge.grid(row=index, column=1, padx=10, pady=2)
                entry_reihenfolge.insert(0, group.get("reihenfolge", ""))
                entry_reihenfolge.bind('<KeyRelease>', lambda event, name=group.get("gruppenname"): self.save_reihenfolge(event, name))
                lbl_damen = ctk.CTkLabel(self.frame_groups, text='JA' if group.get("damenwertung") else "NEIN")
                lbl_damen.grid(row=index, column=2, padx=10, pady=2)
                lbl_damen.bind('<Button-1>', lambda event, name=group.get("gruppenname"), val=group.get("damenwertung"): self.toggle_damenwertung(event, name, val))

    def save_reihenfolge(self, event, group_name):
        """Speichert die Reihenfolgenposition für eine Gruppe."""
        reihenfolge = event.widget.get()
        if validate_number(reihenfolge):
            for group in self.config.wettkampfgruppen:
                if group.get("gruppenname") == group_name:
                    group["reihenfolge"] = reihenfolge
                    logging.info(f"{group_name} Reihenfolge auf {reihenfolge} gesetzt.")
        else:
            event.widget.delete(len(reihenfolge)-1, ctk.END)

    def toggle_damenwertung(self, event, group_name, current_value):
        """Schaltet die Damenwertung für eine Gruppe um."""
        for group in self.config.wettkampfgruppen:
            if group.get("gruppenname") == group_name:
                group["damenwertung"] = not current_value
                logging.info(f"{group_name} Damenwertung geändert zu {group['damenwertung']}.")
        self._draw_wettkampfgruppen()

    def import_groups(self, reset_evaluation: bool):
        """
        Übernimmt die Gruppen. Falls reset_evaluation True ist, wird auch die Auswertung zurückgesetzt.
        """
        if reset_evaluation:
            self.config.durchgaenge.clear()
            self.config.dg_numbers.clear()
        self.config.export_anmeldung_config()
        # Weitere UI-Updates und Zustandsanpassungen
        logging.info("Gruppen übernommen und Auswertung zurückgesetzt.")

    # --- Timer- und Sound-Funktionen ---
    def start_timer(self):
        """Startet den Timer (Beispiel: für Bahn 1)."""
        self.time_running_1 = True
        self.start_time_1 = time.time()
        self._update_timer_1()
        self.btn_start.configure(state='disabled')
        self.btn_stop_all.configure(state='normal')
        # Sound abspielen
        threading.Thread(target=self.play_sound, args=(self.config.setup_data.get("Files", {}).get("angriffsbefehl"),)).start()
        logging.info("Timer 1 gestartet.")

    def _update_timer_1(self):
        if self.time_running_1:
            elapsed = time.time() - self.start_time_1
            dt = TimerManager.format_elapsed_time(elapsed)
            self.label_time_left.configure(text=dt)
            self.root.after(50, self._update_timer_1)
        else:
            logging.info("Timer 1 gestoppt.")

    def stop_all_timers(self):
        """Stoppt alle laufenden Timer."""
        self.time_running_1 = False
        self.time_running_2 = False
        self.btn_stop_all.configure(state='disabled')
        self.btn_start.configure(state='normal')
        threading.Thread(target=self.play_sound, args=(self.config.setup_data.get("Files", {}).get("stopp"),)).start()
        logging.info("Alle Timer gestoppt.")

    def play_sound(self, file_name: str):
        """
        Spielt einen Sound ab, falls Sound aktiviert ist.
        """
        if self.play_sound_flag and file_name:
            try:
                file_path = self.base_path / self.config.setup_data.get("Files", {}).get(file_name, file_name)
                sound = pygame.mixer.Sound(str(file_path))
                sound.play()
                logging.info(f"Sound {file_name} abgespielt.")
            except Exception as e:
                logging.error(f"Fehler beim Abspielen von Sound {file_name}: {e}")

# --- Benutzerdefinierte IntSpinbox ---
class IntSpinbox(ctk.CTkFrame):
    """
    Ein benutzerdefiniertes Spinbox-Widget für ganze Zahlen.
    """
    def __init__(self, *args, width: int = 100, height: int = 32,
                 step_size: int = 1, command: Callable = None, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.step_size = step_size
        self.command = command
        self.configure(fg_color='transparent')
        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.subtract_button = ctk.CTkButton(self, text="-", width=height-6, height=height-6,
                                             corner_radius=0, command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)
        self.entry = ctk.CTkEntry(self, width=width - (2 * height), height=height-6,
                                  border_width=0, corner_radius=0, justify="center")
        self.entry.grid(row=0, column=1, padx=3, pady=3, sticky="ew")
        self.add_button = ctk.CTkButton(self, text="+", width=height-6, height=height-6,
                                        corner_radius=0, command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)
        self.entry.insert(0, "0")

    def add_button_callback(self):
        if self.command:
            self.command()
        try:
            value = int(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, str(value))
        except ValueError:
            pass

    def subtract_button_callback(self):
        if self.command:
            self.command()
        try:
            value = int(self.entry.get()) - self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, str(value))
        except ValueError:
            pass

    def get(self) -> Union[int, None]:
        try:
            return int(self.entry.get())
        except ValueError:
            return None

    def set(self, value: int):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))

# --- Hauptprogramm ---
def main():
    base_path = Path(sys.argv[0]).parent.resolve()
    config_manager = ConfigurationManager(base_path)
    # Starte das GUI; intern wird das mainloop aufgerufen
    GUIManager(config_manager)

if __name__ == "__main__":
    main()
