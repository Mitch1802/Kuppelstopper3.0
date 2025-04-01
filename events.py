from tkinter import messagebox
from customtkinter import *
import random
from utils import write_konsole

def add_wettkampfgruppe(app, event=None):
    name = app.root.Entry.get()
    if not name:
        messagebox.showerror('Fehlermeldung', 'Bitte einen Namen eingeben!')
        return
    # Prüfe, ob der Gruppenname bereits existiert
    count = sum(1 for i in app.Wettkampfgruppen if i['gruppenname'] == name)
    if count > 0:
        messagebox.showerror('Fehlermeldung', 'Gruppenname bereits vorhanden!')
        return
    if len(app.Wettkampfgruppen) >= 30:
        messagebox.showerror('Fehlermeldung', 'Maximal 30 Gruppen erlaubt!')
        return
    # Füge die neue Gruppe hinzu
    val = {
        'gruppenname': name,
        'reihenfolge': '',
        'damenwertung': False
    }
    app.Wettkampfgruppen.append(val)
    app.root.Entry.delete(0, END)
    zeichne_angemeldete_gruppen(app)
    # Schreibe in die Konsole
    from utils import write_konsole
    write_konsole(app, f"{name} wurde hinzugefügt!")

def zeichne_angemeldete_gruppen(app):
    # Lösche alte Widgets im entsprechenden Frame und zeichne die Gruppen neu
    for widget in app.root.LfReihenfolge.winfo_children():
        widget.grid_remove()
    if not app.Wettkampfgruppen:
        app.root.LNoGroups = CTkLabel(app.root.LfReihenfolge, text='Keine Gruppen angemeldet!')
        app.root.LNoGroups.grid(row=0, column=0, sticky=W, padx=10, pady=5)
    else:
        # Beispiel: Überschriften zeichnen
        lbl = CTkLabel(app.root.LfReihenfolge, text='Gruppenname')
        lbl.grid(row=0, column=0, padx=10, pady=2, sticky=W)
        # Weitere Widgets pro Gruppe...
    # Hier kannst du auch Bindings setzen, um Einträge zu aktualisieren.

def uebernahme_gruppen(app, vonKonfig):
    # Logik, um die angemeldeten Gruppen in die Durchgänge zu übernehmen.
    # Eventuell werden hier auch die Konfigurationen exportiert.
    pass

def switch_bahn1_state(app):
    if not app.checked_Bahn_1.get():
        app.root.G1.configure(state=DISABLED)
        app.root.T1.configure(state=DISABLED)
        app.root.F1.configure(state=DISABLED)
        app.root.B1.configure(state=DISABLED)
        app.anzeige.G1.pack_forget()
        app.anzeige.Z1.pack_forget()
        write_konsole(app, 'Bahn 1 wurde deaktiviert!')
    else:
        app.root.G1.configure(state=NORMAL)
        app.root.T1.configure(state=NORMAL)
        app.root.F1.configure(state=NORMAL)
        app.root.B1.configure(state=NORMAL)
        app.anzeige.G1.pack(expand=0, side=TOP, fill=X)
        app.anzeige.Z1.pack(expand=1, side=TOP, fill=BOTH)
        write_konsole(app, 'Bahn 1 wurde aktiviert!')

def switch_bahn2_state(app):
    if not app.checked_Bahn_2.get():
        app.root.G2.configure(state=DISABLED)
        app.root.T2.configure(state=DISABLED)
        app.root.F2.configure(state=DISABLED)
        app.root.B2.configure(state=DISABLED)
        app.anzeige.G2.pack_forget()
        app.anzeige.Z2.pack_forget()
        write_konsole(app, 'Bahn 2 wurde deaktiviert!')
    else:
        app.root.G2.configure(state=NORMAL)
        app.root.T2.configure(state=NORMAL)
        app.root.F2.configure(state=NORMAL)
        app.root.B2.configure(state=NORMAL)
        app.anzeige.G2.pack(expand=0, side=BOTTOM, fill=X)
        app.anzeige.Z2.pack(expand=1, side=TOP, fill=BOTH)
        write_konsole(app, 'Bahn 2 wurde aktiviert!')

def bahn_wechsel(app):
    # Logik, um die Bahnen zu tauschen, z.B. den Text und zugehörige IDs
    werte_uebertragen(app)
    # Weitere Logik...
    write_konsole(app, 'Die Bahnen wurden gewechselt!')

def werte_uebertragen(app):
    # Übertrage die erfassten Zeiten in die Anzeige (analog zu werteInAnsichtUebertragen in deinem Code)
    pass

def anzeige_umschalten(app):
    pass

def lade_zeitnehmungsdaten(app):
    pass

def vorheriger_dg(app):
    pass

def naechster_dg(app):
    pass

def start(app):
    pass

def alles_stop(app):
    pass

def stop_1(app):
    pass

def stop_2(app):
    pass

def stop_reset(app):
    pass

def zeit_1_loeschen(app):
    pass

def zeit_2_loeschen(app):
    pass

def update_rahmen_anzeige(app):
    pass

def update_font_size_zeit(app):
    pass

def update_font_size_gruppe(app):
    pass

def change_font_size_from_windowsize(app):
    pass

def test_gruppen_erstellen(app):
    pass