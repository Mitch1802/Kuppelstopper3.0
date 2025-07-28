from managers import GruppenManager
from gui.main_view import MainView
import os, sys

def main():
    pfad = os.path.dirname(os.path.abspath(sys.argv[0]))
    pfad = pfad.replace('\\', '/')
    LogFile = pfad + '/log.txt'
    KonfigGruppenFile = pfad + '/config/anmeldung.json'
    KonfigBewerbFile = pfad + '/config/bewerb.json'

    gruppen_manager = GruppenManager()
    gruppen_manager.lade_gruppen(KonfigGruppenFile)
    app = MainView(gruppen_manager)
    app.mainloop()

if __name__ == "__main__":
    main()