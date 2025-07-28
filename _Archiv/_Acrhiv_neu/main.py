import argparse, os

from services.database_service import DatabaseService
from services.hardware_service import HardwareService
from services.config_service   import ConfigService
from controllers.admin_controller import AdminController
from controllers.spectator_controller import SpectatorController
from views.admin_view import AdminView
from views.spectator_view import SpectatorView

class Application:
    def __init__(self,
                 mode: str,
                 db_path: str,
                 start_pin: int,
                 end_pin: int,
                 enable_hw: bool):
        # gemeinsame Einstellungen für Fenster-Titel und Tastatur-Keys
        self.settings = {
            'window_title': 'Kuppelcup',
            'start_key': 's',
            'stop_key': 'e'
        }

        # Services initialisieren
        self.config_service = ConfigService(os.path.dirname(db_path))
        self.database_service = DatabaseService(db_path)
        self.hardware_service = HardwareService(start_pin, end_pin, enable_hw)

        # Controller und View je nach Modus
        if mode == 'admin':
            self.controller = AdminController(
                self.config_service,
                self.database_service,
                self.hardware_service,
                self.settings
            )
            self.view = AdminView(self.controller)
        else:
            self.controller = SpectatorController(
                self.config_service,
                self.database_service,
                self.settings
            )
            self.view = SpectatorView(self.controller)

    def run(self):
        self.view.run()


def parse_args():
    parser = argparse.ArgumentParser(description='Kuppelcup Application')
    parser.add_argument(
        '--mode',
        choices=['admin', 'spectator'],
        default='admin',
        help='Modus: "admin" für Verwaltung, "spectator" für Zuschaueranzeige'
    )
    parser.add_argument(
        '--db',
        default='kuppelcup.db',
        help='Pfad zur SQLite-Datenbankdatei'
    )
    parser.add_argument(
        '--start-pin',
        type=int,
        default=17,
        help='GPIO-Pin für Startknopf'
    )
    parser.add_argument(
        '--end-pin',
        type=int,
        default=27,
        help='GPIO-Pin für Endbuzzer'
    )
    parser.add_argument(
        '--enable-hw',
        action='store_true',
        help='GPIO-Hardware aktivieren (sonst nur Tastatursteuerung)'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    app = Application(
        args.mode,
        args.db,
        args.start_pin,
        args.end_pin,
        args.enable_hw
    )
    app.run()