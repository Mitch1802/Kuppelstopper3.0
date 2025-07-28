from tkinter import *
import ttkbootstrap as tb
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *

from gui.auswertung_view import AuswertungView

class MainView(tb.Window):
    def __init__(self, gruppen_manager, durchgang_manager):
        super().__init__(themename="litera")
        self.title("Kuppelstopper 3.0")
        # self.geometry("500x300")
        self.minsize(1600, 1000)

        self.gruppen_manager = gruppen_manager
        self.durchgang_manager = durchgang_manager
        self.create_widgets()

    def create_widgets(self):
        # Container für die Buttons
        button_frame = tb.Frame(self, bootstyle="primary")
        button_frame.pack(fill=X, side=TOP)

        # Container für die "Tabs"
        self.tab_container = tb.Frame(self)
        self.tab_container.pack(fill=BOTH, expand=YES)

        # Erstelle Tab-Inhalte (Frames)
        self.tabs = {
            "Anmeldung": self.create_anmeldung_tab(),
            "Bewerb": self.create_bewerb_tab(),
            "Einstellungen": self.create_settings_tab()
        }

        # Tab Buttons speichern
        self.tab_buttons = {}

        for name in self.tabs:
            btn = tb.Button(button_frame, text=name, command=lambda n=name: self.show_tab(n), compound=LEFT, takefocus=False)
            btn.pack(side=LEFT, ipadx=5, ipady=5)
            self.tab_buttons[name] = btn

        self.show_tab("Anmeldung")  # Standardansicht
    
    def show_tab(self, name):
        # Tabs anzeigen
        for frame in self.tabs.values():
            frame.pack_forget()
        self.tabs[name].pack(fill=BOTH, expand=YES)

        # Buttons einfärben
        for n, btn in self.tab_buttons.items():
            style = DARK if n == name else PRIMARY
            btn.configure(bootstyle=style)

    def create_anmeldung_tab(self):
        frame = tb.Frame(self.tab_container)

        label = tb.Label(frame, text="Wettkampfgruppen", font=("Arial", 14))
        label.pack(padx='10', pady=(10,0), anchor=W)

        entry_frame = tb.Frame(frame)
        entry_frame.pack(fill=X, pady=1, side=TOP)

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

        # Container für die Buttons
        button_frame = tb.Frame(frame, bootstyle="dark")
        button_frame.pack(fill=X, side=TOP)

        # Container für die "Sub Tabs"
        self.subtab_container = tb.Frame(frame)
        self.subtab_container.pack(fill=BOTH, expand=YES)

        # Erstelle Tab-Inhalte (Frames)
        self.subtabs = {
            "Grunddurchgang": self.create_gd_subtab(),
            "KO 1-16": self.create_ko16_subtab(),
            "KO 1-8": self.create_ko8_subtab(),
            "KO 1-4": self.create_ko4_subtab(),
            "Finale": self.create_finale_subtab()
        }

        # Tab Buttons speichern
        self.subtab_buttons = {}

        # Buttons zur Auswahl der Tabs
        for name in self.subtabs:
            btn = tb.Button(button_frame, text=name, command=lambda n=name: self.show_bewerb_subtab(n), compound=LEFT, takefocus=False, bootstyle="dark")
            btn.pack(fill=X, side=LEFT, ipadx=5, ipady=5, expand=True)
            self.subtab_buttons[name] = btn

        self.show_bewerb_subtab("Grunddurchgang")  # Standardansicht

        return frame
    
    def create_gd_subtab(self):
        frame = tb.Frame(self.subtab_container)

        label = tb.Label(frame, text="Grunddurchgang", font=("Arial", 14))
        label.pack(padx='10', pady=(10,0), anchor=W)

        return frame
    
    def create_ko16_subtab(self):
        frame = tb.Frame(self.subtab_container)

        label = tb.Label(frame, text="KO 1-16", font=("Arial", 14))
        label.pack(padx='10', pady=(10,0), anchor=W)

        return frame
    
    def create_ko8_subtab(self):
        frame = tb.Frame(self.subtab_container)

        label = tb.Label(frame, text="KO 1-8", font=("Arial", 14))
        label.pack(padx='10', pady=(10,0), anchor=W)

        return frame
    
    def create_ko4_subtab(self):
        frame = tb.Frame(self.subtab_container)

        label = tb.Label(frame, text="KO 1-4", font=("Arial", 14))
        label.pack(padx='10', pady=(10,0), anchor=W)

        return frame
    
    def create_finale_subtab(self):
        frame = tb.Frame(self.subtab_container)

        label = tb.Label(frame, text="Finale", font=("Arial", 14))
        label.pack(padx='10', pady=(10,0), anchor=W)

        return frame
    
    def show_bewerb_subtab(self, name):
        # Tabs anzeigen
        for frame in self.subtabs.values():
            frame.pack_forget()
        self.subtabs[name].pack(fill=BOTH, expand=YES)

        # Buttons einfärben
        for n, btn in self.subtab_buttons.items():
            style = SECONDARY if n == name else DARK
            btn.configure(bootstyle=style)
    
    def create_settings_tab(self):
        frame = tb.Frame(self.tab_container)

        label = tb.Label(frame, text="Einstellungen", font=("Arial", 14))
        label.pack(padx='10', pady=(10,0), anchor=W)

        return frame
