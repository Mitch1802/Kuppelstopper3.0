import os, json

class ConfigService:
    def __init__(self, base_path):
        self.base = base_path
        self.reg_file = os.path.join(self.base, 'config/anmeldung.json')
        self.bewerb_file = os.path.join(self.base, 'config/bewerb.json')
        self.setup_file = os.path.join(self.base, 'config/setup.json')
        self._load_all()

    def _load_all(self):
        # Gruppen
        if os.path.exists(self.reg_file):
            with open(self.reg_file) as f:
                self.groups = json.load(f)
        else:
            self.groups = []
        # Bewerb (Durchgänge + DGNumbers)
        if os.path.exists(self.bewerb_file):
            with open(self.bewerb_file) as f:
                d = json.load(f)
                self.runs = d['Bewerb']; self.dg_numbers = d['DGNumbers']
        else:
            self.runs = []; self.dg_numbers = []
        # Setup (Style, Buttons, etc)
        with open(self.setup_file) as f:
            self.setup = json.load(f)

    def save_groups(self):
        with open(self.reg_file, 'w') as f:
            json.dump(self.groups, f, indent=2)

    def save_runs(self):
        with open(self.bewerb_file, 'w') as f:
            json.dump({'Bewerb': self.runs, 'DGNumbers': self.dg_numbers}, f, indent=2)