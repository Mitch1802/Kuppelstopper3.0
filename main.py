from managers import *
from gui.main_view import MainView
from gui.auswertung_view import AuswertungView
import os, sys

def main():
    pfad = os.path.dirname(os.path.abspath(sys.argv[0]))
    pfad = pfad.replace('\\', '/')

    KonfigGruppenFile = pfad + '/config/anmeldung.json'
    KonfigBewerbFile = pfad + '/config/bewerb.json'

    gruppen_manager = GruppenManager()
    gruppen_manager.lade_gruppen(KonfigGruppenFile)

    durchgang_manager = DurchgangManager()
    # durchgang_manager.lade_durchgaenge(KonfigBewerbFile)

    app = MainView(gruppen_manager, durchgang_manager)
    app.mainloop()

    # TODO: Ansichtfenster
    # auswertung = AuswertungView()
    # auswertung.grab_set()

if __name__ == "__main__":
    main()