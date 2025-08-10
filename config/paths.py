import os

# Basisverzeichnis für Konfigurations- und Datenexporte
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# pfad = os.path.dirname(os.path.abspath(sys.argv[0]))
# pfad = pfad.replace('\\', '/')

# Absolute Pfade zu den JSON-Dateien
ANMELDUNG_JSON = os.path.join(BASE_DIR, "anmeldung.json")
BEWERB_JSON = os.path.join(BASE_DIR, "config/bewerb.json")
SETUP_JSON = os.path.join(BASE_DIR, "config/setup.json")
THEME_JSON = os.path.join(BASE_DIR, "config/theme.json")

ANMELDUNG_JSON = ANMELDUNG_JSON.replace('\\', '/')
BEWERB_JSON = BEWERB_JSON.replace('\\', '/')
SETUP_JSON = SETUP_JSON.replace('\\', '/')
THEME_JSON = THEME_JSON.replace('\\', '/')
