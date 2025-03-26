# config.py
import json
import os


class ConfigManager:
    def __init__(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.pfad = base_path.replace('\\', '/')

        self.LogFile = os.path.join(self.pfad, 'log.txt')
        self.KonfigGruppenFile = os.path.join(self.pfad, 'config', 'anmeldung.json')
        self.KonfigBewerbFile = os.path.join(self.pfad, 'config', 'bewerb.json')
        self.KonfigSetupFile = os.path.join(self.pfad, 'config', 'setup.json')
        self.KonfigThemeFile = os.path.join(self.pfad, 'config', 'theme.json')

        self.setup_data = self._load_json(self.KonfigSetupFile)
        self.theme_file = self.KonfigThemeFile

        self.title = self.setup_data['Setup'].get('Title', 'Kuppelstopper')
        self.title_anzeige = self.setup_data['Setup'].get('TitleAnzeige', 'Anzeige')
        self.zeige_alle_zeiten = self.setup_data['Setup'].get('ZeigeAlleZeiten', False)
        self.testmodus = self.setup_data['Setup'].get('Testmodus', False)
        self.play_sound = self.setup_data['Setup'].get('PlaySound', True)

        self.style = self.setup_data['Style']
        self.files = self.setup_data['Files']
        self.buttons = self.setup_data['Buttons']

    def _load_json(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    def save_json(self, path, data):
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    def save_log(self, text):
        with open(self.LogFile, 'a', encoding='utf-8') as f:
            f.write(text + '\n')
