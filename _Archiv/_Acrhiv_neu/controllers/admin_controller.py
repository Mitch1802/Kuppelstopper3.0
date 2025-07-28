import time
from services.config_service import ConfigService
from services.database_service import DatabaseService
from services.hardware_service import HardwareService

class AdminController:
    """
    Steuert die Verwaltungs-Logik:
    - Verwaltung der Wettkampfgruppen (Anmeldung)
    - Auswahl der aktuellen Gruppe für einen Lauf
    - Starten/Beenden eines Laufs (Später)
    """

    def __init__(self,
                 config_service: ConfigService,
                 database_service: DatabaseService,
                 hardware_service: HardwareService,
                 settings: dict):
        # Services und Settings
        self.config   = config_service
        self.database = database_service
        self.hardware = hardware_service
        self.settings = settings

        # Aktuelle Daten aus der Konfiguration
        # Jede Gruppe ist ein dict: {'gruppenname': str, 'reihenfolge': str, 'damenwertung': bool}
        self.groups = self.config.groups

        # Auswahl und Timing
        self.current_group = None
        self.start_time    = None

    def add_group(self, name: str, is_female: bool):
        """
        Neue Gruppe anlegen. Verhindert Duplikate und speichert in der Konfig.
        """
        if any(g['gruppenname'] == name for g in self.groups):
            raise ValueError(f"Gruppe '{name}' existiert bereits.")
        self.groups.append({
            'gruppenname': name,
            'reihenfolge': '',
            'damenwertung': is_female
        })
        self.config.save_groups()

    def delete_group(self, name: str):
        """
        Gelöschte Gruppe aus der Liste entfernen und speichern.
        """
        self.groups = [g for g in self.groups if g['gruppenname'] != name]
        self.config.groups = self.groups
        self.config.save_groups()

    def toggle_damenwertung(self, name: str):
        """
        Damenwertung-Flag einer Gruppe umschalten.
        """
        for g in self.groups:
            if g['gruppenname'] == name:
                g['damenwertung'] = not g['damenwertung']
                break
        self.config.save_groups()

    def select_group(self, index: int):
        """
        Wählt die Gruppe an Position `index` als aktuell aus.
        """
        try:
            self.current_group = self.groups[index]
        except IndexError:
            self.current_group = None

    def start_run(self):
        """
        Startet die Zeitmessung für die aktuell gewählte Gruppe.
        Wenn GPIO aktiv ist, wartet auf den Start-Knopf.
        """
        if not self.current_group:
            print("Keine Gruppe ausgewählt.")
            return
        self.start_time = time.monotonic()
        if self.hardware.is_enabled:
            self.hardware.wait_for_start_button()

    def end_run(self, errors: int = 0):
        """
        Beendet die Zeitmessung, speichert den Versuch in der DB und zeigt die Bestzeit.
        """
        if self.start_time is None:
            print("Kein Lauf gestartet.")
            return
        elapsed = time.monotonic() - self.start_time
        # In der Datenbank wird nach Gruppenname unterschieden
        self.database.add_attempt(self.current_group['gruppenname'], elapsed, errors)
        best = self.database.get_best_attempt(self.current_group['gruppenname'])
        print(f"Bestzeit für {self.current_group['gruppenname']}: {best.penalized_time:.2f}s")
        self.start_time = None