import os
import sys
import json
import time
from typing import Any

class DataManager:
    def __init__(self, config_path: str = "config"):
        self.pfad = os.path.dirname(os.path.abspath(sys.argv[0])).replace('\\', '/')
        self.config_path = f"{self.pfad}/{config_path}"

        self.log_file = f"{self.pfad}/log.txt"
        self.konfig_gruppen_file = f"{self.config_path}/anmeldung.json"
        self.konfig_bewerb_file = f"{self.config_path}/bewerb.json"
        self.konfig_setup_file = f"{self.config_path}/setup.json"
        self.konfig_theme_file = f"{self.config_path}/theme.json"

    def load_json(self, filepath: str) -> Any:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        return None

    def save_json(self, filepath: str, data: Any):
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def log(self, message: str):
        with open(self.log_file, "a", encoding='utf-8') as file:
            file.write(time.strftime('%X') + " " + message + "\n")

    def load_all(self):
        anmeldungen = self.load_json(self.konfig_gruppen_file) or []
        bewerb_data = self.load_json(self.konfig_bewerb_file) or {}
        setup = self.load_json(self.konfig_setup_file) or {}
        theme = self.load_json(self.konfig_theme_file) or {}

        return anmeldungen, bewerb_data.get("Bewerb", []), bewerb_data.get("DGNumbers", []), setup, theme

    def save_anmeldungen(self, gruppen: list):
        self.save_json(self.konfig_gruppen_file, gruppen)

    def save_bewerb(self, durchgaenge: list, dg_numbers: list):
        data = {
            "Bewerb": durchgaenge,
            "DGNumbers": dg_numbers
        }
        self.save_json(self.konfig_bewerb_file, data)
