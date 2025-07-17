import json

def lade_konfiguration(pfad):
    with open(pfad, 'r') as f:
        return json.load(f)

def speichere_konfiguration(pfad, daten):
    with open(pfad, 'w') as f:
        json.dump(daten, f)