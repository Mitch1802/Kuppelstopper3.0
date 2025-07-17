from managers import GruppenManager
from gui.main_view import MainView

def main():
    gruppen_manager = GruppenManager()
    gruppen_manager.lade_gruppen("gruppen.json")
    app = MainView(gruppen_manager)
    app.mainloop()

if __name__ == "__main__":
    main()