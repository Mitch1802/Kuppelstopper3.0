from tkinter import *
import ttkbootstrap as tb
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *

from gui.auswertung import AuswertungView

class MainView(tb.Window):
    def __init__(self, gruppen_manager):
        super().__init__(themename="litera")
        self.title("Kuppelstopper 3.0")
        # self.geometry("500x300")
        self.minsize(1600, 1000)
        self.gruppen_manager = gruppen_manager
        self.create_widgets()

        # TODO: Ansichtfenster
        # auswertung = AuswertungView(self)
        # auswertung.grab_set()

    def create_widgets(self):
        # Container für die Buttons
        button_frame = tb.Frame(self, style='primary.TFrame')
        button_frame.pack(fill=X, pady=1, side=TOP)

        # Container für die "Tabs"
        self.tab_container = tb.Frame(self)
        self.tab_container.pack(fill=BOTH, expand=YES)

        # Erstelle Tab-Inhalte (Frames)
        self.tabs = {
            "Anmeldung": self.create_anmeldung_tab(),
            "Bewerb": self.create_bewerb_tab(),
            "Einstellungen": self.create_settings_tab()
        }

        # Buttons zur Auswahl der Tabs
        for name in self.tabs:
            btn = tb.Button(button_frame, text=name, command=lambda n=name: self.show_tab(n), compound=LEFT)
            btn.pack(side=LEFT, ipadx=5, ipady=5, padx=(1, 0), pady=1)

        self.show_tab("Anmeldung")  # Standardansicht
    
    def show_tab(self, name):
        # Alle Frames ausblenden
        for frame in self.tabs.values():
            frame.pack_forget()
        # Gewählten Frame anzeigen
        self.tabs[name].pack(fill=BOTH, expand=YES)


    def create_anmeldung_tab(self):
        frame = tb.Frame(self.tab_container)

        label = tb.Label(frame, text="Wettkampfgruppen", font=("Arial", 14))
        label.pack(padx='10', pady=(10,0), anchor=W)

        entry_frame = tb.Frame(frame)
        entry_frame.pack(fill=X, pady=1, side=TOP)

        # lbl = tb.Label(frame, text='WEttkampfgruppe', width=10)
        # lbl.pack(side=LEFT, padx=5)

        ent = tb.Entry(entry_frame)
        ent.pack(side=LEFT, fill='x', padx='10', pady='10', expand=True)
        # ent.bind('<Return>', self.addWettkampfgruppe)

        btn = tb.Button(entry_frame, text='Hinzufügen', compound=LEFT)
        btn.pack(side=LEFT, fill='x', padx='10', pady='10')


        #TODO Liste Gruppen


        btn = tb.Button(frame, text="Auswertung")
        btn.pack(side=TOP, fill='x', padx='10', pady='10')

        return frame
    
    def create_bewerb_tab(self):
        frame = tb.Frame(self.tab_container)

        return frame
    
    def create_settings_tab(self):
        frame = tb.Frame(self.tab_container)

        return frame
