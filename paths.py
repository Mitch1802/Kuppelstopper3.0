import os

# Basisverzeichnis für Konfigurations- und Datenexporte
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Absolute Pfade zu den JSON-Dateien
ANMELDUNG_JSON = os.path.join(BASE_DIR, "config/anmeldung.json")
BEWERB_JSON = os.path.join(BASE_DIR, "config/bewerb.json")
SETUP_JSON = os.path.join(BASE_DIR, "config/setup.json")
START_SOUND_PATH = os.path.join(BASE_DIR, "Resources/AngriffsbefehlWonie.mp3")
STOP_SOUND_PATH = os.path.join(BASE_DIR, "Resources/HornHonk.wav")

ANMELDUNG_JSON = ANMELDUNG_JSON.replace('\\', '/')
BEWERB_JSON = BEWERB_JSON.replace('\\', '/')
SETUP_JSON = SETUP_JSON.replace('\\', '/')
START_SOUND_PATH = START_SOUND_PATH.replace('\\', '/')
STOP_SOUND_PATH = STOP_SOUND_PATH.replace('\\', '/')
