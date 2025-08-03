from managers.gruppen_manager import *
from gui.main_view import MainView
# from gui.auswertung_view import AuswertungView
from config.paths import *

def main():
    gruppen_manager = GruppenManager()
    gruppen_manager.lade_gruppen(ANMELDUNG_JSON)

    app = MainView()
    app.mainloop()

    # TODO: Ansichtfenster
    # auswertung = AuswertungView()
    # auswertung.grab_set()

if __name__ == "__main__":
    main()