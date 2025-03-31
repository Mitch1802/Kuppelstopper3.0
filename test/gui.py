from customtkinter import *

def init_gui(app):
    # Hier kannst du globale GUI-Einstellungen vornehmen
    # z. B. die Standard-Farbthemen und den Erscheinungsmodus setzen (bereits in kuppelstopper.py gemacht)
    pass

def create_tabs(app):
    app.__root.TabView = CTkTabview(app.__root, anchor='nw', corner_radius=0, fg_color='transparent')
    app.__root.TabView.pack(expand=1, side='top', fill='both', padx=5, pady=5)
    app.__root.FTab1 = app.__root.TabView.add(app.NAME_TAB1)
    app.__root.FTab2 = app.__root.TabView.add(app.NAME_TAB2)
    app.__root.FTab3 = app.__root.TabView.add(app.NAME_TAB3)

def create_tab1(app):
    # Erstelle Widgets für Tab1 (Anmeldung)
    # Beispiel: Eingabefeld, ScrollableFrame, Buttons etc.
    pass

def create_tab2(app):
    # Erstelle Widgets für Tab2 (Übersicht - Zeitnehmung)
    pass

def create_tab3(app):
    # Erstelle Widgets für Tab3 (Einstellungen)
    pass

def show_anzeige(app):
    # Erstelle das Anzeigefenster (Toplevel) und dessen Widgets
    pass
