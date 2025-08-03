import os

# Basisverzeichnis für Konfigurations- und Datenexporte
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# pfad = os.path.dirname(os.path.abspath(sys.argv[0]))
# pfad = pfad.replace('\\', '/')

# Absolute Pfade zu den JSON-Dateien
ANMELDUNG_JSON = os.path.join(BASE_DIR, "config/anmeldung.json")
BEWERB_JSON = os.path.join(BASE_DIR, "config/bewerb.json")
SETUP_JSON = os.path.join(BASE_DIR, "config/setup.json")
THEME_JSON = os.path.join(BASE_DIR, "config/theme.json")
