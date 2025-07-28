import json, os

def lade_konfiguration(setup_file):
    if not os.path.exists(setup_file) or os.path.getsize(setup_file) == 0:
        with open(setup_file, "w", encoding="utf-8") as f:
            json.dump({}, f)

    with open(setup_file, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("Fehler: Ungültiges JSON-Format.")
            return {}

def export_anmeldung_konfig(config_file, wettkampfgruppen):
    with open(config_file, "w") as f:
        json.dump(wettkampfgruppen, f)

def export_bewerb_konfig(config_file, durchgaenge, dg_numbers):
    data = {
        'Bewerb': durchgaenge,
        'DGNumbers': dg_numbers
    }
    with open(config_file, "w") as f:
        json.dump(data, f)

def init_var(self):
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


