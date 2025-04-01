import json

def lade_konfiguration(setup_file):
    with open(setup_file, "r") as f:
        return json.load(f)

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
