from tkinter import *
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from gui.custom_table import CustomTable
from gui.edit_popup import EditPopup
from gui.auswertung_window import AuswertungWindow
from models import Gruppe
from managers.gruppen_manager import GruppenManager
from managers.durchgang_manager import DurchgangManager
from managers.zeitnehmung_manager import ZeitManager
from managers.audio_manager import AudioManager
from managers.gpio_manager import GpioManager
from managers.setup_manager import SetupManager
from paths import *


class MainView(tb.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.win_auswertung = None

        self.title("Kuppelstopper 3.0")
        self.minsize(1400, 800)

        # ===== Flags =====
        self.checked_Bahn_1 = BooleanVar(value=False)
        self.checked_Bahn_2 = BooleanVar(value=False)
        self.checked_Tastatur = BooleanVar(value=True)
        self.checked_GPIO = BooleanVar(value=False)
        self.checked_Fullscreen = BooleanVar(value=False)
        self.checked_Konsole = BooleanVar(value=True)
        self.checked_Test = BooleanVar(value=False)
        self.checked_Testzeiten = BooleanVar(value=False)

        # Sound-Pfad NUR aus paths.py
        self.start_sound_path = START_SOUND_PATH
        self.stop_sound_path = STOP_SOUND_PATH

        # Manager
        self.gruppen_manager = GruppenManager()
        self.durchgang_manager = DurchgangManager()
        self.zeit_manager = ZeitManager()
        self.setup_manager = SetupManager()

        # Zeitmanager -> UI live aktualisieren, wenn vorhanden
        if hasattr(self.zeit_manager, "on_tick"):
            self.zeit_manager.on_tick(lambda z1, z2: (
                self.lbl_bahn1_zeit.config(text=z1),
                self.lbl_bahn2_zeit.config(text=z2),
                self._push_times_to_auswertungsfenster(z1, z2)
            ))

        # Audio + GPIO
        self.audio = AudioManager()
        self.gpio_inputs = None
        # Arming-Flags (bewaffnet = wartet auf externen Trigger)
        self._armed_global = False
        self._armed_lane1 = False
        self._armed_lane2 = False

        # Tabellen
        self.coldata_gruppen = ["Gruppenname", "Damen", "Reihenfolge", ""]
        self.coldata_bewerb = ["DG","Gruppe","Zeit1","F1","Zeit2","F2","Bestzeit inkl. Fehler"]
        self.coldata_rang = ["Platzierung", "Gruppe", "Bestzeit inkl. Fehler"]

        self.cell_types_gruppen = ["label", "label", "entry", "button"]
        self.cell_types_bewerb = ["label", "label", "label", "label", "label", "label","label"]
        self.cell_types_rang = ["label", "label", "label"]

        self.commands_gruppen = [None, self.change_damentyp, None, self.del_wettkampfgruppe]
        self.commands_bewerb = [None, self.change_durchgang_gruppe, None, None, None, None, None]
        self.commands_rang = [None, None, None]

        self.percent_widths_gruppen = [75, 10, 10, 10]
        self.percent_widths_bewerb = [5, 20, 20, 5, 20, 5, 20]
        self.percent_widths_rang = [20, 50, 20]

        # UI
        self.setup_ui()

        # Hotkeys & GPIO (werden aus Settings-Feldern gelesen)
        self.after(50, self._bind_hotkeys_from_settings)
        self.after(50, self._setup_gpio_from_settings)

        # Zweitfenster
        if self.checked_Fullscreen.get():
            self.after(300, lambda: self.open_auswertung_window(monitor_index=1, fullscreen=True))
        else:
            self.after(300, lambda: self.open_auswertung_window(monitor_index=1, fullscreen=False))
        
        # Lade Konfiguration
        self.lade_basis_setup()

    # ========= Tabs-Grundgerüst =========
    def setup_ui(self):
        button_frame = tb.Frame(self, bootstyle="primary")
        button_frame.pack(fill=X, side=TOP)

        self.tab_container = tb.Frame(self)
        self.tab_container.pack(fill=BOTH, expand=YES)

        self.tabs = {
            "Anmeldung": self.create_anmeldung_tab(),
            "Bewerb": self.create_bewerb_tab(),
            "Einstellungen": self.create_settings_tab(),  # unverändert in Layout
            "Info": self.create_info_tab()
        }

        self.tab_buttons = {}
        for name in self.tabs:
            btn = tb.Button(button_frame, text=name, command=lambda n=name: self.show_tab(n), compound=LEFT, takefocus=False)
            btn.pack(side=LEFT, ipadx=5, ipady=5)
            self.tab_buttons[name] = btn

        self.show_tab("Anmeldung")

    def show_tab(self, name):
        for frame in self.tabs.values():
            frame.pack_forget()
        self.tabs[name].pack(fill=BOTH, expand=True)
        for n, btn in self.tab_buttons.items():
            btn.configure(bootstyle=(DARK if n == name else PRIMARY))

    # ========= Anmeldung =========
    def create_anmeldung_tab(self):
        frame = tb.Frame(self.tab_container)

        label = tb.Label(frame, text="Wettkampfgruppen", font=("Arial", 20))
        label.pack(padx=10, pady=(10, 0), anchor=W)

        entry_frame = tb.Frame(frame)
        entry_frame.pack(fill=X, pady=1, side=TOP)

        self.ent_anmeldung = tb.Entry(entry_frame)
        self.ent_anmeldung.pack(side=LEFT, fill=X, padx=10, pady=10, expand=True)
        self.ent_anmeldung.bind('<Return>', self.add_wettkampfgruppe)

        btn = tb.Button(entry_frame, text='Hinzufügen', compound=LEFT, command=self.add_wettkampfgruppe, takefocus=0)
        btn.pack(side=LEFT, fill=X, padx=10, pady=10)

        self.tbl_gruppen = CustomTable(frame, self.coldata_gruppen, [], self.percent_widths_gruppen,
                                       cell_types=self.cell_types_gruppen, commands=self.commands_gruppen)

        self.btn_bewerb_starten = tb.Button(frame, text="Bewerb starten", command=self.gruppen_uebernehmen, takefocus=0)
        self.btn_bewerb_starten.pack(side=BOTTOM, fill=X, padx=10, pady=10)

        frame.bind("<Configure>", lambda e, obj=self.tbl_gruppen: self.tbl_build(obj))
        return frame

    def add_wettkampfgruppe(self, event=None):
        name = self.ent_anmeldung.get()
        if name:
            gruppe = Gruppe(name, 'NEIN', 0)
            self.gruppen_manager.gruppe_hinzufuegen(gruppe)
            self.tbl_gruppen_update()
            self.ent_anmeldung.delete(0, END)

    def change_damentyp(self, data):
        self.gruppen_manager.gruppe_aendern(data)
        self.tbl_gruppen_update()

    def del_wettkampfgruppe(self, data):
        self.gruppen_manager.gruppe_loeschen(data)
        self.tbl_gruppen_update()

    def gruppen_uebernehmen(self):
        testzeiten = self.checked_Testzeiten.get()
        self.lbl_dg_number.config(text=1)
        self.gruppen_manager.speichere_anmeldung()
        ang_gruppen = self.gruppen_manager.gruppen_uebernehmen()
        self.durchgang_manager.uebernehme_angemeldete_gruppen(ang_gruppen)
        # TODO Ang. Gruppen speichern in JSON
        anzahl_gruppen = len(ang_gruppen)
        self.update_tabs(anzahl_gruppen)
        self.lade_grunddurchgang(testzeiten)
        self.show_tab('Bewerb')
        self.show_bewerb_subtab('Grunddurchgang')

    # ========= Bewerb / Subtabs / Zeitnehmung =========
    def create_bewerb_tab(self):
        frame = tb.Frame(self.tab_container)
        self.button_frame = tb.Frame(frame, bootstyle="dark")
        self.button_frame.pack(fill=X, side=TOP)

        self.subtab_container = tb.Frame(frame)
        self.subtab_container.pack(fill=BOTH, side=TOP, expand=True)

        # Zeitnehmung-Toolbar (hier fügen wir NUR Start B1/B2 & global Start ein)
        frame_zeitnehmung_frame = self.create_sub_zeitnehmung()
        frame_zeitnehmung_frame.pack(fill=BOTH, side=BOTTOM)

        self.subtabs = {
            "Grunddurchgang": self.create_gd_subtab(),
            "KO 1-16": self.create_ko16_subtab(),
            "KO 1-8": self.create_ko8_subtab(),
            "KO 1-4": self.create_ko4_subtab(),
            "Finale": self.create_finale_subtab()
        }

        self.subtab_buttons = {}
        for name in self.subtabs:
            btn = tb.Button(self.button_frame, text=name, command=lambda n=name: self.show_bewerb_subtab(n),
                            compound=LEFT, takefocus=False, bootstyle="dark")
            self.subtab_buttons[name] = btn
            btn._is_packed = False

        self._show_button("Grunddurchgang")
        self.show_bewerb_subtab("Grunddurchgang")

        return frame

    def create_gd_subtab(self):
        frame = tb.Frame(self.subtab_container)
        frame_left = tb.Frame(frame); frame_left.pack(side=LEFT, fill=BOTH, expand=True)
        self.tbl_gd_bewerb = CustomTable(frame_left, self.coldata_bewerb, [], self.percent_widths_bewerb,
                                         cell_types=self.cell_types_bewerb, commands=self.commands_bewerb)
        frame_left.bind("<Configure>", lambda e, obj=self.tbl_gd_bewerb: self.tbl_build(obj))
        frame_right = tb.Frame(frame); frame_right.pack(side=LEFT, fill=BOTH, expand=True)
        self.tbl_gd_rang = CustomTable(frame_right, self.coldata_rang, [], self.percent_widths_rang,
                                       cell_types=self.cell_types_rang, commands=self.commands_rang)
        frame_right.bind("<Configure>", lambda e, obj=self.tbl_gd_rang: self.tbl_build(obj))
        return frame

    def create_ko16_subtab(self):
        frame = tb.Frame(self.subtab_container)
        frame_left = tb.Frame(frame); frame_left.pack(side=LEFT, fill=BOTH, expand=True)
        self.tbl_ko16_bewerb = CustomTable(frame_left, self.coldata_bewerb, [], self.percent_widths_bewerb,
                                           cell_types=self.cell_types_bewerb, commands=self.commands_bewerb)
        frame_left.bind("<Configure>", lambda e, obj=self.tbl_ko16_bewerb: self.tbl_build(obj))
        frame_right = tb.Frame(frame); frame_right.pack(side=LEFT, fill=BOTH, expand=True)
        self.tbl_ko16_rang = CustomTable(frame_right, self.coldata_rang, [], self.percent_widths_rang,
                                         cell_types=self.cell_types_rang, commands=self.commands_rang)
        frame_right.bind("<Configure>", lambda e, obj=self.tbl_ko16_rang: self.tbl_build(obj))
        return frame

    def create_ko8_subtab(self):
        frame = tb.Frame(self.subtab_container)
        frame_left = tb.Frame(frame); frame_left.pack(side=LEFT, fill=BOTH, expand=True)
        self.tbl_ko8_bewerb = CustomTable(frame_left, self.coldata_bewerb, [], self.percent_widths_bewerb,
                                          cell_types=self.cell_types_bewerb, commands=self.commands_bewerb)
        frame_left.bind("<Configure>", lambda e, obj=self.tbl_ko8_bewerb: self.tbl_build(obj))
        frame_right = tb.Frame(frame); frame_right.pack(side=LEFT, fill=BOTH, expand=True)
        self.tbl_ko8_rang = CustomTable(frame_right, self.coldata_rang, [], self.percent_widths_rang,
                                        cell_types=self.cell_types_rang, commands=self.commands_rang)
        frame_right.bind("<Configure>", lambda e, obj=self.tbl_ko8_rang: self.tbl_build(obj))
        return frame

    def create_ko4_subtab(self):
        frame = tb.Frame(self.subtab_container)
        frame_left = tb.Frame(frame); frame_left.pack(side=LEFT, fill=BOTH, expand=True)
        self.tbl_ko4_bewerb = CustomTable(frame_left, self.coldata_bewerb, [], self.percent_widths_bewerb,
                                          cell_types=self.cell_types_bewerb, commands=self.commands_bewerb)
        frame_left.bind("<Configure>", lambda e, obj=self.tbl_ko4_bewerb: self.tbl_build(obj))
        frame_right = tb.Frame(frame); frame_right.pack(side=LEFT, fill=BOTH, expand=True)
        self.tbl_ko4_rang = CustomTable(frame_right, self.coldata_rang, [], self.percent_widths_rang,
                                        cell_types=self.cell_types_rang, commands=self.commands_rang)
        frame_right.bind("<Configure>", lambda e, obj=self.tbl_ko4_rang: self.tbl_build(obj))
        return frame

    def create_finale_subtab(self):
        frame = tb.Frame(self.subtab_container)
        frame_left = tb.Frame(frame); frame_left.pack(side=LEFT, fill=BOTH, expand=True)
        self.tbl_finale_bewerb = CustomTable(frame_left, self.coldata_bewerb, [], self.percent_widths_bewerb,
                                             cell_types=self.cell_types_bewerb, commands=self.commands_bewerb)
        frame_left.bind("<Configure>", lambda e, obj=self.tbl_finale_bewerb: self.tbl_build(obj))
        frame_right = tb.Frame(frame); frame_right.pack(side=LEFT, fill=BOTH, expand=True)
        self.tbl_finale_rang = CustomTable(frame_right, self.coldata_rang, [], self.percent_widths_rang,
                                           cell_types=self.cell_types_rang, commands=self.commands_rang)
        frame_right.bind("<Configure>", lambda e, obj=self.tbl_finale_rang: self.tbl_build(obj))
        return frame

    def update_tabs(self, counter: int):
        must_show = {"Grunddurchgang"}
        if counter >= 16: must_show.add("KO 1-16")
        if counter >= 8:  must_show.add("KO 1-8")
        if counter >= 4:  must_show.add("KO 1-4")
        if counter >= 2:  must_show.add("Finale")

        order = ["Grunddurchgang", "KO 1-16", "KO 1-8", "KO 1-4", "Finale"]

        for btn in self.subtab_buttons.values():
            if getattr(btn, "_is_packed", False):
                btn.pack_forget()
            btn._is_packed = False

        for name in order:
            if name in must_show:
                self._show_button(name)

        if getattr(self, "_current_subtab_name", "Grunddurchgang") not in must_show:
            self.show_bewerb_subtab("Grunddurchgang")

    def _show_button(self, name: str):
        btn = self.subtab_buttons[name]
        if not getattr(btn, "_is_packed", False):
            btn.pack(fill="x", side="left", ipadx=5, ipady=5, expand=True)
            btn._is_packed = True

    def show_bewerb_subtab(self, name):
        for frame in self.subtabs.values():
            frame.pack_forget()
        self.subtabs[name].pack(fill=BOTH, expand=YES)

        for n, btn in self.subtab_buttons.items():
            if btn._is_packed:
                style = SECONDARY if n == name else DARK
                btn.configure(bootstyle=style)
        self._current_subtab_name = name

    def create_sub_zeitnehmung(self):
        frame = tb.Frame(self.subtab_container)

        frame_zeitnehmung = tb.Frame(frame)
        frame_zeitnehmung.pack(fill=BOTH, side=LEFT)

        btn = tb.Button(frame_zeitnehmung, text='Ansicht', width=10, bootstyle=INFO, takefocus=0, command=self.ansicht_umschalten)
        btn.pack(fill=BOTH, side=LEFT, padx=5, pady=5)

        self.btn_dg_vorheriger = tb.Button(frame_zeitnehmung, text='-', width=5, bootstyle=WARNING, takefocus=0, command=self.dg_vorheriger)
        self.btn_dg_vorheriger.pack(fill=BOTH, side=LEFT, padx=5, pady=5)

        self.lbl_dg_number = tb.Label(frame_zeitnehmung, text="1", font=("Arial", 30))
        self.lbl_dg_number.pack(fill=BOTH, side=LEFT, padx=5, pady=5)

        self.btn_naechster_dg = tb.Button(frame_zeitnehmung, text='+', bootstyle=WARNING, width=5, takefocus=0, command=self.dg_naechster)
        self.btn_naechster_dg.pack(fill=BOTH, side=LEFT, padx=5, pady=5)

        self.btn_start_global = tb.Button(frame_zeitnehmung, text='Start', width=15, takefocus=0, command=self.start_global)
        self.btn_start_global.pack(fill=BOTH, side=LEFT, padx=5, pady=5)

        self.btn_alles_stop = tb.Button(frame_zeitnehmung, text='Alles Stop', width=15, takefocus=0, command=self.alles_stop, state=DISABLED)
        self.btn_alles_stop.pack(fill=BOTH, side=LEFT, padx=5, pady=5)

        self.btn_bahn_wechsel = tb.Button(frame_zeitnehmung, text='Bahn Wechsel', width=15, takefocus=0, command=self.bahnwechsel, state=DISABLED)
        self.btn_bahn_wechsel.pack(fill=BOTH, side=LEFT, padx=5, pady=5)

        self.btn_zeit_uebertragen = tb.Button(frame_zeitnehmung, text='Zeit übertragen', width=15, takefocus=0, command=self.zeit_uebertragen, state=DISABLED)
        self.btn_zeit_uebertragen.pack(fill=BOTH, side=LEFT, padx=5, pady=5)

        frame_bahnen = tb.Frame(frame)
        frame_bahnen.pack(fill=BOTH, side=LEFT, padx=5, pady=5)

        self.lbl_bahn1 = tb.Label(frame_bahnen, text='B 1')
        self.lbl_bahn1.grid(row=0, column=0, padx=10, sticky=W)
        self.lbl_bahn1_gruppe = tb.Label(frame_bahnen, text='...')
        self.lbl_bahn1_gruppe.grid(row=0, column=1, padx=10, sticky=W)
        self.lbl_bahn1_zeit = tb.Label(frame_bahnen, text='00:00:00')
        self.lbl_bahn1_zeit.grid(row=0, column=2, padx=10)
        self.ent_bahn1_fehler = tb.Entry(frame_bahnen, width=5, takefocus=0)
        self.ent_bahn1_fehler.grid(row=0, column=3, padx=10)
        self.btn_bahn1_stop = tb.Button(frame_bahnen, text='Stop B1', width=10, command=self.bahn1_stop, state=DISABLED)
        self.btn_bahn1_stop.grid(row=0, column=4)

        self.lbl_bahn2 = tb.Label(frame_bahnen, text='B 2')
        self.lbl_bahn2.grid(row=1, column=0, padx=10, sticky=W)
        self.lbl_bahn2_gruppe = tb.Label(frame_bahnen, text='...')
        self.lbl_bahn2_gruppe.grid(row=1, column=1, padx=10, sticky=W)
        self.lbl_bahn2_zeit = tb.Label(frame_bahnen, text='00:00:00')
        self.lbl_bahn2_zeit.grid(row=1, column=2, padx=10)
        self.ent_bahn2_fehler = tb.Entry(frame_bahnen, width=5, takefocus=0)
        self.ent_bahn2_fehler.grid(row=1, column=3, padx=10)
        self.btn_bahn2_stop = tb.Button(frame_bahnen, text='Stop B2', width=10, command=self.bahn2_stop, state=DISABLED)
        self.btn_bahn2_stop.grid(row=1, column=4)

        frame_korrektur = tb.Frame(frame)
        frame_korrektur.pack(fill=BOTH, side=LEFT)
        self.btn_stop_reset = tb.Button(frame_korrektur, text='Stop and Reset', width=15, takefocus=0, command=self.stop_und_reset)
        self.btn_stop_reset.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        self.btn_zeit1_loeschen = tb.Button(frame_korrektur, text='Zeit 1+2 löschen', width=15, takefocus=0, command=self.zeit_1_und_2_loeschen)
        self.btn_zeit1_loeschen.pack(fill=BOTH, side=LEFT, padx=5, pady=5)
        self.btn_zeit2_loeschen = tb.Button(frame_korrektur, text='Zeit 2 löschen', width=15, takefocus=0, command=self.zeit_2_loeschen)
        self.btn_zeit2_loeschen.pack(fill=BOTH, side=LEFT, padx=5, pady=5)

        return frame

    # ========= Einstellungen (DEIN Layout, nur Referenzen & Bindings) =========
    def create_settings_tab(self):
        frame = tb.Frame(self.tab_container)
        self.settings_tab = frame

        label = tb.Label(frame, text="Einstellungen", font=("Arial", 20))
        label.pack(padx=10, pady=10, anchor=W)

        label = tb.Label(frame, text="Eingabe", font=("Arial", 15))
        label.pack(padx=10, pady=10, anchor=W)

        sub_frame = tb.Frame(frame)
        sub_frame.pack(fill=X, padx=10, pady=10)

        # deine Checkbuttons
        tb.Checkbutton(sub_frame, text="Tastatur", variable=self.checked_Tastatur, bootstyle="round-toggle").pack(side=LEFT, padx=10, pady=10)
        tb.Checkbutton(sub_frame, text="GPIO", variable=self.checked_GPIO, bootstyle="round-toggle",
                       command=self._setup_gpio_from_settings).pack(side=LEFT, padx=10, pady=10)
        tb.Checkbutton(sub_frame, text="Fullscreen", variable=self.checked_Fullscreen, bootstyle="round-toggle").pack(side=LEFT, padx=10, pady=10)
        tb.Checkbutton(sub_frame, text="Konsole", variable=self.checked_Konsole, bootstyle="round-toggle").pack(side=LEFT, padx=10, pady=10)
        tb.Checkbutton(sub_frame, text="Testgruppen", variable=self.checked_Test, command=self.testframe_anzeigen, bootstyle="round-toggle").pack(side=LEFT, padx=10, pady=10)

        # Tasten
        label = tb.Label(frame, text="Tasten", font=("Arial", 15))
        label.pack(padx=10, pady=(20,10), anchor=W)
        sub_frame = tb.Frame(frame); sub_frame.pack(fill=X, padx=10, pady=10)

        tb.Label(sub_frame, text="Start Bahn 1").pack(side=LEFT, padx=(10,0), pady=10, anchor=W)
        self.ent_key_start1 = tb.Entry(sub_frame, width=5); self.ent_key_start1.pack(side=LEFT, padx=(5,10), pady=10)
        self.ent_key_start1.bind("<FocusOut>", lambda e: self._bind_hotkeys_from_settings())

        tb.Label(sub_frame, text="Stopp Bahn 1").pack(side=LEFT, padx=(10,0), pady=10, anchor=W)
        self.ent_key_stop1 = tb.Entry(sub_frame, width=5); self.ent_key_stop1.pack(side=LEFT, padx=(5,10), pady=10)
        self.ent_key_stop1.bind("<FocusOut>", lambda e: self._bind_hotkeys_from_settings())

        tb.Label(sub_frame, text="Start Bahn 2").pack(side=LEFT, padx=(10,0), pady=10, anchor=W)
        self.ent_key_start2 = tb.Entry(sub_frame, width=5); self.ent_key_start2.pack(side=LEFT, padx=(5,10), pady=10)
        self.ent_key_start2.bind("<FocusOut>", lambda e: self._bind_hotkeys_from_settings())

        tb.Label(sub_frame, text="Stopp Bahn 2").pack(side=LEFT, padx=(10,0), pady=10, anchor=W)
        self.ent_key_stop2 = tb.Entry(sub_frame, width=5); self.ent_key_stop2.pack(side=LEFT, padx=(5,10), pady=10)
        self.ent_key_stop2.bind("<FocusOut>", lambda e: self._bind_hotkeys_from_settings())

        # GPIO
        label = tb.Label(frame, text="GPIO", font=("Arial", 15))
        label.pack(padx=10, pady=(20,10), anchor=W)
        sub_frame = tb.Frame(frame); sub_frame.pack(fill=X, padx=10, pady=10)

        tb.Label(sub_frame, text="Start Bahn 1").pack(side=LEFT, padx=(10,0), pady=10, anchor=W)
        self.ent_gpio_start1 = tb.Entry(sub_frame, width=5); self.ent_gpio_start1.pack(side=LEFT, padx=(5,10), pady=10)
        self.ent_gpio_start1.bind("<FocusOut>", lambda e: self._setup_gpio_from_settings())

        tb.Label(sub_frame, text="Stopp Bahn 1").pack(side=LEFT, padx=(10,0), pady=10, anchor=W)
        self.ent_gpio_stop1 = tb.Entry(sub_frame, width=5); self.ent_gpio_stop1.pack(side=LEFT, padx=(5,10), pady=10)
        self.ent_gpio_stop1.bind("<FocusOut>", lambda e: self._setup_gpio_from_settings())

        tb.Label(sub_frame, text="Start Bahn 2").pack(side=LEFT, padx=(10,0), pady=10, anchor=W)
        self.ent_gpio_start2 = tb.Entry(sub_frame, width=5); self.ent_gpio_start2.pack(side=LEFT, padx=(5,10), pady=10)
        self.ent_gpio_start2.bind("<FocusOut>", lambda e: self._setup_gpio_from_settings())

        tb.Label(sub_frame, text="Stopp Bahn 2").pack(side=LEFT, padx=(10,0), pady=10, anchor=W)
        self.ent_gpio_stop2 = tb.Entry(sub_frame, width=5); self.ent_gpio_stop2.pack(side=LEFT, padx=(5,10), pady=10)
        self.ent_gpio_stop2.bind("<FocusOut>", lambda e: self._setup_gpio_from_settings())

        # Style
        label = tb.Label(frame, text="Style", font=("Arial", 15))
        label.pack(padx=10, pady=(20,10), anchor=W)
        sub_frame = tb.Frame(frame); sub_frame.pack(fill=X, padx=10, pady=10)

        tb.Label(sub_frame, text="Schriftgröße Zeit").pack(side=LEFT, padx=(10,0), pady=10, anchor=W)
        self.ent_font_size_time = tb.Spinbox(sub_frame, from_=0, to=500, width=5, command=self.change_font_size_time, takefocus=0)
        self.ent_font_size_time.pack(side=LEFT, padx=(5,10), pady=10)
        self.ent_font_size_time.set(36)

        tb.Label(sub_frame, text="Schriftgröße Gruppe").pack(side=LEFT, padx=(10,0), pady=10, anchor=W)
        self.ent_font_size_group = tb.Spinbox(sub_frame, from_=0, to=500, width=5, command=self.change_font_size_group, takefocus=0)
        self.ent_font_size_group.pack(side=LEFT, padx=(5,10), pady=10)
        self.ent_font_size_group.set(50)

        tb.Button(sub_frame, text="Schriftgröße Autoanpassung", takefocus=0, command=self.change_font_size_from_window).pack(side=LEFT, padx=10, pady=10)

        # Konfiguration
        label = tb.Label(frame, text="Konfiguration", font=("Arial", 15))
        label.pack(padx=10, pady=(20,10), anchor=W)
        sub_frame = tb.Frame(frame); sub_frame.pack(fill=X, padx=10, pady=10)

        tb.Button(sub_frame, text="Lade Gruppen", takefocus=0, command=self.lade_gruppen).pack(side=LEFT, padx=10, pady=10)
        tb.Button(sub_frame, text="Lade Bewerb", takefocus=0, command=self.lade_bewerb).pack(side=LEFT, padx=10, pady=10)
        tb.Button(sub_frame, text="Lade Einstellungen", takefocus=0, command=self.lade_setup).pack(side=LEFT, padx=10, pady=10)
        tb.Button(sub_frame, text="Export Einstellungen", bootstyle=INFO , takefocus=0, command=self.export_setup).pack(side=LEFT, padx=10, pady=10)

        # Testbereich (dein bestehendes UI)
        self.frame_test = tb.Frame(self.settings_tab)
        label = tb.Label(self.frame_test, text="Test", font=("Arial", 15))
        label.pack(padx=10, pady=(20,10), anchor=W)

        tb.Label(self.frame_test, text="Anzahl Testgruppen").pack(side=LEFT, padx=(10,0), pady=10, anchor=W)
        self.test_gruppen_anzahl = tb.Entry(self.frame_test, width=5) 
        self.test_gruppen_anzahl.pack(side=LEFT, padx=(5,10), pady=10)

        tb.Label(self.frame_test, text="Anzahl Damengruppen").pack(side=LEFT, padx=(10,0), pady=10, anchor=W)
        self.test_damen_anzahl = tb.Entry(self.frame_test, width=5)
        self.test_damen_anzahl.pack(side=LEFT, padx=(5,10), pady=10)

        tb.Checkbutton(self.frame_test, text="Testzeiten", variable=self.checked_Testzeiten, bootstyle="round-toggle").pack(side=LEFT, padx=10, pady=10)
        tb.Button(self.frame_test, text="Erstellen", takefocus=0, command=self.testgruppen_hinzufuegen).pack(side=LEFT, padx=10, pady=10)

        return frame
    
    def change_font_size_group(self, event=None):
        size = self.ent_font_size_group.get() or 0
        self.win_auswertung.change_font_size_group(int(size))
    
    def change_font_size_time(self, event=None):
        size = self.ent_font_size_time.get() or 0
        self.win_auswertung.change_font_size_time(int(size))

    def change_font_size_from_window(self):
        from screeninfo import get_monitors
        mons = get_monitors()
        if 0 <= 1 < len(mons):
            m = mons[1]
        else:
            m = mons[0]

        h = m.height
        
        size_group = h / 14
        size_time =  h / 7

        self.ent_font_size_time.delete(0, END)
        self.ent_font_size_group.delete(0, END)

        self.ent_font_size_time.insert(0, int(size_time))
        self.ent_font_size_group.insert(0, int(size_group))
        self.win_auswertung.change_font_size_from_window(int(size_time), int(size_group))

    def testframe_anzeigen(self):
        if self.checked_Test.get():
            if not hasattr(self, "frame_test") or not self.frame_test.winfo_exists():
                self.frame_test = tb.Frame(self.settings_tab)
            self.frame_test.pack(fill=X, padx=10, pady=10)
        else:
            if hasattr(self, "frame_test") and self.frame_test.winfo_exists():
                self.frame_test.pack_forget()

    def testgruppen_hinzufuegen(self):
        anzahl = self.test_gruppen_anzahl.get()
        damenAnzahl = self.test_damen_anzahl.get()
        self.gruppen_manager.testgruppen_hinzufuegen(self, anzahl, damenAnzahl)
        self.tbl_gruppen_update()
        self.test_gruppen_anzahl.delete(0, END)
        self.test_damen_anzahl.delete(0, END)
        self.show_tab("Anmeldung")

    # ========= Info =========
    def create_info_tab(self):
        frame = tb.Frame(self.tab_container)
        tb.Label(frame, text="Information", font=("Arial", 20)).pack(padx=10, pady=(10,20), anchor=W)
        tb.Label(frame, text="Version: 3.0").pack(padx=10, anchor=W)
        tb.Label(frame, text="Entwickler: Michael Reichenauer, FF Schwadorf").pack(padx=10, anchor=W)
        tb.Label(frame, text="E-Mail: michael.reichenauer@feuerwehr.gv.at").pack(padx=10, anchor=W)
        return frame

    # ========= Tabellen-Hilfen =========
    def tbl_build(self, table_object):
        height = table_object.master.winfo_height()
        if height < 100:
            self.after(100, lambda: self.tbl_build(table_object))
            return
        table_object.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    def tbl_gruppen_update(self):
        daten_neu = self.gruppen_manager.get_gruppen()
        self.tbl_gruppen.set_data(daten_neu)

    # ========= Daten-Logik =========
    def lade_gruppen(self):
        self.gruppen_manager.lade_gruppen(ANMELDUNG_JSON)
        self.tbl_gruppen_update()
        self.show_tab('Anmeldung')

    def lade_bewerb(self):
        anzahl_gruppen = self.durchgang_manager.lade_bewerb(BEWERB_JSON)
        self.update_tabs(anzahl_gruppen)
        self.durchgang_manager.berechne_bestzeiten()
        for modus in self.durchgang_manager.lade_alle_Tabellen_modus():
            self.durchgang_manager.sort_tbl_rang_daten(modus)
        self.durchgang_manager.top_gruppen_naechste_runde()
        self.update_tabelle_von_modus_gesamt()
        self.lade_durchgang_von_dgnumber(1)
        self.show_tab('Bewerb')
        self.show_bewerb_subtab('Grunddurchgang')

    def lade_setup(self):
        self.setup_manager.lade_setup(SETUP_JSON)
        # TODO Setup befüllen

    def lade_basis_setup(self):
        self.ent_gpio_start1.delete(0, END)
        self.ent_gpio_stop1.delete(0, END)
        self.ent_gpio_start2.delete(0, END)
        self.ent_gpio_stop2.delete(0, END)
        
        self.ent_gpio_start1.insert(0, '17')
        self.ent_gpio_stop1.insert(0, '27')
        self.ent_gpio_start2.insert(0, '19')
        self.ent_gpio_stop2.insert(0, '26')
        
        self.ent_key_start1.delete(0, END)
        self.ent_key_stop1.delete(0, END)
        self.ent_key_start2.delete(0, END)
        self.ent_key_stop2.delete(0, END)

        self.ent_key_start1.insert(0, 'a')
        self.ent_key_stop1.insert(0, 'q')
        self.ent_key_start2.insert(0, 's')
        self.ent_key_stop2.insert(0, 'w')

    def export_setup(self):
        data = {}

        data['checked_Tastatur'] = self.checked_Tastatur.get()
        data['checked_GPIO'] = self.checked_GPIO.get()
        data['checked_Fullscreen'] = self.checked_Fullscreen.get()
        data['checked_Konsole'] = self.checked_Konsole.get()
        data['checked_Test'] = self.checked_Test.get()
        data['checked_Testzeiten'] = self.checked_Testzeiten.get()

        data['ent_key_start1'] = self.ent_key_start1.get()
        data['ent_key_stop1'] = self.ent_key_stop1.get()
        data['ent_key_start2'] = self.ent_key_start2.get()
        data['ent_key_stop2'] = self.ent_key_stop2.get()

        data['ent_gpio_start1'] = self.ent_gpio_start1.get()
        data['ent_gpio_stop1'] = self.ent_gpio_stop1.get()
        data['ent_gpio_start2'] = self.ent_gpio_start2.get()
        data['ent_gpio_stop2'] = self.ent_gpio_stop2.get()

        data['ent_font_size_time'] = self.ent_font_size_time.get()
        data['ent_font_size_group'] = self.ent_font_size_group.get()

        self.setup_manager.setup_speichern(SETUP_JSON, data)

    def lade_grunddurchgang(self, testzeiten):
        self.durchgang_manager.lade_grunddurchgang(testzeiten)
        self.durchgang_manager.berechne_bestzeiten()
        for modus in self.durchgang_manager.lade_alle_Tabellen_modus():
            self.durchgang_manager.sort_tbl_rang_daten(modus)
        self.durchgang_manager.top_gruppen_naechste_runde()
        self.update_tabelle_von_modus_gesamt()
        self.lade_durchgang_von_dgnumber(1)

    def change_durchgang_gruppe(self, data):
        """
        Wird von der CustomTable-Kommandospalte aufgerufen (z. B. Klick).
        'data' sollte die Zeilendaten enthalten. Wir öffnen ein Popup,
        lassen Werte bearbeiten und speichern danach alles wie gehabt.
        """
        # Bestmögliche Defaults aus der Zeile ziehen (Passe Keys an deine tatsächlichen Daten an!)
        initial = {
            "Durchgang": data[0],
            "Gruppe": data[1],
            "Zeit1": data[2],
            "F1":    data[3],
            "Zeit2": data[4],
            "F2":    data[5],
        }

        # Welche Felder sollen editierbar sein?
        fields = [
            ("Durchgang", "ro-entry"),
            ("Gruppe", "ro-entry"),
            ("Zeit1",  "entry"),
            ("F1",     "spin", (0, 100)),
            ("Zeit2",  "entry"),
            ("F2",     "spin", (0, 100)),
        ]

        def on_save(d):
            # Neue Daten in die alte Struktur mergen, dann deinen bisherigen Ablauf verwenden
            new_data = list(d.values())

            # Deine bestehende Logik:
            self.durchgang_manager.change_werte(new_data)
            self.durchgang_manager.berechne_bestzeiten()
            self.durchgang_manager.top_gruppen_naechste_runde()
            self.update_tabelle_von_modus_gesamt()

        # Popup öffnen (modal) – schließt sich nach Speichern automatisch
        EditPopup(self, "Durchgang bearbeiten", fields, initial, on_save)

    def ansicht_umschalten(self):
        w = getattr(self, "win_auswertung", None)
        if not (w and w.winfo_exists()):
            return
        new_mode = "rang" if w.modus == "zeit" else "zeit"
        w.set_mode(new_mode)

    def dg_vorheriger(self):
        dg_alt = int(self.lbl_dg_number.cget('text'))
        dg_neu = dg_alt - 1
        self.lbl_dg_number.config(text=dg_neu)
        mod_a = self.durchgang_manager.wandle_durchgang_in_modus(dg_alt)
        mod_b = self.durchgang_manager.wandle_durchgang_in_modus(dg_neu)
        if mod_a != mod_b:
            sub_tab_name = self.wandle_typ_in_ansicht(mod_b)
            self.show_bewerb_subtab(sub_tab_name)
        self.lade_durchgang_von_dgnumber(dg_neu)

    def dg_naechster(self):
        dg_alt = int(self.lbl_dg_number.cget('text'))
        dg_neu = dg_alt + 1
        self.lbl_dg_number.config(text=dg_neu)
        mod_a = self.durchgang_manager.wandle_durchgang_in_modus(dg_alt)
        mod_b = self.durchgang_manager.wandle_durchgang_in_modus(dg_neu)
        if mod_a != mod_b:
            sub_tab_name = self.wandle_typ_in_ansicht(mod_b)
            self.show_bewerb_subtab(sub_tab_name)
        self.lade_durchgang_von_dgnumber(dg_neu)

    def wandle_typ_in_ansicht(self, typ):
        mapping = {
            self.durchgang_manager.TypGD: 'Grunddurchgang',
            self.durchgang_manager.TypKO16: 'KO 1-16',
            self.durchgang_manager.TypKO8: 'KO 1-8',
            self.durchgang_manager.TypKO4: 'KO 1-4',
            self.durchgang_manager.TypKF: 'Finale',
            self.durchgang_manager.TypF: 'Finale'
        }
        return mapping.get(typ)

    def bahnwechsel(self):
        gruppe_a = self.lbl_bahn1_gruppe.cget('text')
        gruppe_b = self.lbl_bahn2_gruppe.cget('text')

        self.lbl_bahn1_gruppe.config(text=gruppe_b)
        self.lbl_bahn2_gruppe.config(text=gruppe_a)

        if gruppe_b != '':
            self.ent_bahn1_fehler['state'] = NORMAL
            self.lbl_bahn1_zeit.config(text='00:00:00')
        else:
            self.lbl_bahn1_zeit.config(text='')
            self.ent_bahn1_fehler['state'] = DISABLED

        if gruppe_a != '':
            self.ent_bahn2_fehler['state'] = NORMAL
            self.lbl_bahn2_zeit.config(text='00:00:00')
        else:
            self.lbl_bahn2_zeit.config(text='')
            self.ent_bahn2_fehler['state'] = DISABLED

    def stop_und_reset(self):
        self.alles_stop()
        self.zeitnehmung_buttons_control(True, False, False, False, False, False, False, True, True)
        self.zeit_reset()
        
    def lade_durchgang_von_dgnumber(self, durchgang):
        dg_min = 1
        dg_max = self.durchgang_manager.get_max_dgnumber()

        self.btn_dg_vorheriger['state'] = DISABLED if durchgang == dg_min else NORMAL
        self.btn_naechster_dg['state'] = DISABLED if durchgang == dg_max else NORMAL

        zeiten_a, zeiten_b = self.durchgang_manager.check_beide_zeiten(durchgang)

        if zeiten_a == 2 or zeiten_b == 2:
            self.lbl_bahn1_gruppe.config(text='')
            self.lbl_bahn1_zeit.config(text='')
            self.ent_bahn1_fehler['state'] = DISABLED
            self.lbl_bahn2_gruppe.config(text='')
            self.lbl_bahn2_zeit.config(text='')
            self.ent_bahn2_fehler['state'] = DISABLED
            self.zeitnehmung_buttons_control(False, False, False, False, False, False, False, True, True)
        else:
            gruppen_start = self.durchgang_manager.lade_gruppen_von_durchgang(durchgang)
            self.lbl_bahn1_zeit.config(text='00:00:00')
            self.ent_bahn1_fehler['state'] = NORMAL
            self.lbl_bahn1_gruppe.config(text=gruppen_start[0])

            if gruppen_start[1] != '':
                self.lbl_bahn2_zeit.config(text='00:00:00')
                self.ent_bahn2_fehler['state'] = NORMAL
                self.lbl_bahn2_gruppe.config(text=gruppen_start[1])
            else:
                self.lbl_bahn2_zeit.config(text='')
                self.ent_bahn2_fehler['state'] = DISABLED
                self.lbl_bahn2_gruppe.config(text='')

            self.zeitnehmung_buttons_control(True, False, False, False, False, False, False, True, True)

        self._push_groups_to_auswertungsfenster()
        self._push_times_to_auswertungsfenster(self.lbl_bahn1_zeit.cget('text'), self.lbl_bahn2_zeit.cget('text'))

        next1, next2 = self._ermittle_naechste_gruppen(durchgang)
        w = getattr(self, "win_auswertung", None)
        if w and w.winfo_exists():
            w.set_next_groups(next1, next2)

    # ========= Start/Stop – mit Sound + externem Trigger =========
    def start_global(self):
        """Sound spielen, dann beide Bahnen 'armen' -> Start via Tastatur/GPIO."""
        self._reset_arming()
        self._armed_global = True
        self._armed_lane1 = True
        self._armed_lane2 = True
        self._prepare_ui_for_start()
        self.audio.play(self.start_sound_path)
        self._setup_gpio_from_settings()  # sicherstellen, dass GPIO aktiv ist

    def start_lane(self, lane: int):
        """Sound spielen, dann nur gewählte Bahn 'armen'."""
        self._reset_arming()
        if lane == 1:
            self._armed_lane1 = True
        elif lane == 2:
            self._armed_lane2 = True
        self._prepare_ui_for_start()
        self.audio.play(self.start_sound_path)
        self._setup_gpio_from_settings()

    def _prepare_ui_for_start(self):
        self.zeitnehmung_buttons_control(False, True, False, False, True, True, True, False, False)
        g1 = (self.lbl_bahn1_gruppe.cget('text') or '').strip()
        g2 = (self.lbl_bahn2_gruppe.cget('text') or '').strip()
        self.lbl_bahn1_zeit.config(text='00:00:00' if g1 else '')
        self.lbl_bahn2_zeit.config(text='00:00:00' if g2 else '')
        self.ent_bahn1_fehler['state'] = NORMAL if g1 else DISABLED
        self.ent_bahn2_fehler['state'] = NORMAL if g2 else DISABLED

    def _reset_arming(self):
        self._armed_global = self._armed_lane1 = self._armed_lane2 = False

    def _external_start(self, lane: int):
        """Von Tastatur/GPIO getriggert. lane=None => globaler Start."""
        if not (self._armed_global or self._armed_lane1 or self._armed_lane2):
            return
        self.audio.stop()
        try:
            if lane is None:
                active1 = (self.lbl_bahn1_gruppe.cget('text') or '').strip() != ''
                active2 = (self.lbl_bahn2_gruppe.cget('text') or '').strip() != ''
                if hasattr(self.zeit_manager, "start"):
                    self.zeit_manager.start(active1, active2)
            else:
                if hasattr(self.zeit_manager, "start_lane"):
                    self.zeit_manager.start_lane(lane)
                else:
                    if hasattr(self.zeit_manager, "start"):
                        self.zeit_manager.start(lane == 1, lane == 2)
        finally:
            if lane is None:
                self._armed_global = self._armed_lane1 = self._armed_lane2 = False
            elif lane == 1:
                self._armed_lane1 = False
            elif lane == 2:
                self._armed_lane2 = False

    def _external_stop_lane(self, lane: int):
        # still ignorieren, wenn schon gestoppt
        if hasattr(self.zeit_manager, "needs_reset") and self.zeit_manager.needs_reset(lane):
            return
        if lane == 1:
            self.bahn1_stop()
        elif lane == 2:
            self.bahn2_stop()

    def alles_stop(self):
        try:
            self.zeit_manager.stop_all()
        except Exception:
            pass
        self.audio.stop()
        self._reset_arming()
        self.audio.play(self.stop_sound_path)
        self.zeitnehmung_buttons_control(False, False, False, True, False, False, False, True, True)
        self._push_times_to_auswertungsfenster(self.lbl_bahn1_zeit.cget('text'), self.lbl_bahn2_zeit.cget('text'))

    def bahn1_stop(self):
        # still ignorieren, wenn schon gestoppt
        try:
            if hasattr(self.zeit_manager, "needs_reset") and self.zeit_manager.needs_reset(1):
                return
            self.zeit_manager.stop_lane(1)
            self.audio.play(self.stop_sound_path)
        except Exception:
            pass
        try:
            self.btn_bahn1_stop['state'] = DISABLED
        except Exception:
            pass
        self._push_times_to_auswertungsfenster(self.lbl_bahn1_zeit.cget('text'), self.lbl_bahn2_zeit.cget('text'))
        self._update_after_lane_stop()  # <--- NEU

    def bahn2_stop(self):
        # still ignorieren, wenn schon gestoppt
        try:
            if hasattr(self.zeit_manager, "needs_reset") and self.zeit_manager.needs_reset(2):
                return
            self.zeit_manager.stop_lane(2)
            self.audio.play(self.stop_sound_path)
        except Exception:
            pass
        try:
            self.btn_bahn2_stop['state'] = DISABLED
        except Exception:
            pass
        self._push_times_to_auswertungsfenster(self.lbl_bahn1_zeit.cget('text'), self.lbl_bahn2_zeit.cget('text'))
        self._update_after_lane_stop()  # <--- NEU

    def zeit_reset(self):
        try:
            self.zeit_manager.reset()
        except Exception:
            pass
        self.audio.stop()
        self._reset_arming()
        self.lbl_bahn1_zeit.config(text='00:00:00')
        self.ent_bahn1_fehler.delete(0, END)
        self.lbl_bahn2_zeit.config(text='00:00:00')
        self.ent_bahn2_fehler.delete(0, END)
        self._push_times_to_auswertungsfenster(self.lbl_bahn1_zeit.cget('text'), self.lbl_bahn2_zeit.cget('text'))

    # ========= Zeiten übertragen & löschen =========
    def zeit_uebertragen(self):
        durchgang = int(self.lbl_dg_number.cget('text'))
        gruppe_a = self.lbl_bahn1_gruppe.cget('text')
        gruppe_b = self.lbl_bahn2_gruppe.cget('text')

        zeit_a = self.lbl_bahn1_zeit.cget('text')
        fehler_a = self.ent_bahn1_fehler.get() or 0
        zeit_b = self.lbl_bahn2_zeit.cget('text')
        fehler_b = self.ent_bahn2_fehler.get() or 0

        count_zeit = self.durchgang_manager.zeiten_an_bewerb_uebergeben(durchgang, gruppe_a, zeit_a, fehler_a, gruppe_b, zeit_b, fehler_b)
        self.durchgang_manager.berechne_bestzeiten()
        for modus in self.durchgang_manager.lade_alle_Tabellen_modus():
            self.durchgang_manager.sort_tbl_rang_daten(modus)
        self.durchgang_manager.top_gruppen_naechste_runde()
        self.update_tabelle_von_modus_gesamt()

        self.zeit_reset()
        self.zeitnehmung_buttons_control(True, False, True, False, False, False, False, True, True)

        if count_zeit == 1:
            self.bahnwechsel()
        elif count_zeit == 2:
            self.dg_naechster()

        self._push_groups_to_auswertungsfenster()
        self._push_times_to_auswertungsfenster(self.lbl_bahn1_zeit.cget('text'), self.lbl_bahn2_zeit.cget('text'))

    def zeit_1_und_2_loeschen(self):
        dg = self.lbl_dg_number.cget('text')
        self.durchgang_manager.zeit_1_und_2_loeschen(dg)
        self.durchgang_manager.berechne_bestzeiten()
        for modus in self.durchgang_manager.lade_alle_Tabellen_modus():
            self.durchgang_manager.sort_tbl_rang_daten(modus)
        self.durchgang_manager.top_gruppen_naechste_runde()
        self.update_tabelle_von_modus_gesamt()
        self.lade_durchgang_von_dgnumber(dg)
        self.zeitnehmung_buttons_control(True, False, False, False, False, False, False, True, True)

    def zeit_2_loeschen(self):
        dg = self.lbl_dg_number.cget('text')
        self.durchgang_manager.zeit_2_loeschen(dg)
        self.durchgang_manager.berechne_bestzeiten()
        for modus in self.durchgang_manager.lade_alle_Tabellen_modus():
            self.durchgang_manager.sort_tbl_rang_daten(modus)
        self.durchgang_manager.top_gruppen_naechste_runde()
        self.update_tabelle_von_modus_gesamt()
        self.lade_durchgang_von_dgnumber(dg)
        self.zeitnehmung_buttons_control(True, False, True, False, False, False, False, True, True)

    def zeitnehmung_buttons_control(self, start_global, alles_stop, bahn_wechsel, zeit_uebertragen,
                                    bahn1_stop, bahn2_stop, stop_reset, zeit1_loeschen, zeit2_loeschen):
        mapping = [
            (start_global, self.btn_start_global),
            (alles_stop, self.btn_alles_stop),
            (bahn_wechsel, self.btn_bahn_wechsel),
            (zeit_uebertragen, self.btn_zeit_uebertragen),
            (bahn1_stop, self.btn_bahn1_stop),
            (bahn2_stop, self.btn_bahn2_stop),
            (stop_reset, self.btn_stop_reset),
            (zeit1_loeschen, self.btn_zeit1_loeschen),
            (zeit2_loeschen, self.btn_zeit2_loeschen)
        ]
        for cond, button in mapping:
            button['state'] = NORMAL if cond else DISABLED

    def update_tabelle_von_modus_gesamt(self):
        self.refresh_auswertung_if_visible()
        all_modus = self.durchgang_manager.lade_alle_Tabellen_modus()
        for modus in all_modus:
            self.update_tabelle_von_modus(modus)
        self.durchgang_manager.export_bewerb(BEWERB_JSON)

    def update_tabelle_von_modus(self, modus):
        daten_bewerb = self.durchgang_manager.filter_bewerb(modus)
        tbl_daten_bewerb = self.durchgang_manager.filter_tbl_bewerb_daten(daten_bewerb)
        daten_rang = self.durchgang_manager.sort_tbl_rang_daten(modus)
        tbl_daten_rang = self.durchgang_manager.filter_tbl_rang_daten(daten_rang)

        if modus == self.durchgang_manager.TypGD:
            self.tbl_gd_bewerb.set_data(tbl_daten_bewerb)
            self.tbl_gd_rang.set_data(tbl_daten_rang)
        elif modus == self.durchgang_manager.TypKO16:
            self.tbl_ko16_bewerb.set_data(tbl_daten_bewerb)
            self.tbl_ko16_rang.set_data(tbl_daten_rang)
        elif modus == self.durchgang_manager.TypKO8:
            self.tbl_ko8_bewerb.set_data(tbl_daten_bewerb)
            self.tbl_ko8_rang.set_data(tbl_daten_rang)
        elif modus == self.durchgang_manager.TypKO4:
            self.tbl_ko4_bewerb.set_data(tbl_daten_bewerb)
            self.tbl_ko4_rang.set_data(tbl_daten_rang)
        elif modus == self.durchgang_manager.TypKF or modus == self.durchgang_manager.TypF:
            self.tbl_finale_bewerb.set_data(tbl_daten_bewerb)
            self.tbl_finale_rang.set_data(tbl_daten_rang)

    # ========= Auswertungsfenster =========
    def open_auswertung_window(self, monitor_index=1, fullscreen=False):
        w = getattr(self, "win_auswertung", None)
        if w and w.winfo_exists():
            w.deiconify()
            w.lift()
            return

        self.win_auswertung = AuswertungWindow(
            self,
            zeit_manager=self.zeit_manager,
            durchgang_manager=self.durchgang_manager,
            themename="litera",
        )
        self.win_auswertung.show_on_monitor(
            monitor_index, fullscreen=fullscreen, fallback_geometry="+1920+0"
        )

        self._push_groups_to_auswertungsfenster()
        self._push_times_to_auswertungsfenster(self.lbl_bahn1_zeit.cget('text'), self.lbl_bahn2_zeit.cget('text'))
        dg = int(self.lbl_dg_number.cget('text')) if self.lbl_dg_number.cget('text').isdigit() else 1
        next1, next2 = self._ermittle_naechste_gruppen(dg)
        self.win_auswertung.set_next_groups(next1, next2)

    def close_auswertung_window(self):
        w = getattr(self, "win_auswertung", None)
        if w and w.winfo_exists():
            w.destroy()
        self.win_auswertung = None

    def toggle_auswertung_window(self):
        w = getattr(self, "win_auswertung", None)
        if w and w.winfo_exists():
            self.close_auswertung_window()
        else:
            self.open_auswertung_window(monitor_index=1, fullscreen=False)

    def refresh_auswertung_if_visible(self):
        w = self.win_auswertung
        if w and w.winfo_exists():
            try:
                w.refresh()
            except Exception:
                pass

    def _push_groups_to_auswertungsfenster(self):
        w = getattr(self, "win_auswertung", None)
        if not (w and w.winfo_exists()):
            return
        try:
            g1 = self.lbl_bahn1_gruppe.cget("text")
        except Exception:
            g1 = None
        try:
            g2 = self.lbl_bahn2_gruppe.cget("text")
        except Exception:
            g2 = None
        g1 = g1 if g1 and g1.strip() and g1.strip() != "—" else None
        g2 = g2 if g2 and g2.strip() and g2.strip() != "—" else None
        w.set_current_groups(g1, g2)

    def _push_times_to_auswertungsfenster(self, zeit1, zeit2):
        w = getattr(self, "win_auswertung", None)
        if w and w.winfo_exists():
            w.update_times(zeit1, zeit2)

    def _update_after_lane_stop(self):
        # Ist die Bahn im aktuellen DG überhaupt aktiv?
        g1_active = bool((self.lbl_bahn1_gruppe.cget('text') or '').strip())
        g2_active = bool((self.lbl_bahn2_gruppe.cget('text') or '').strip())

        # Wurde sie schon gestoppt? (ZeitManager setzt needs_reset(X) nach stop_lane(X))
        needs1 = self.zeit_manager.needs_reset(1) if hasattr(self.zeit_manager, "needs_reset") else False
        needs2 = self.zeit_manager.needs_reset(2) if hasattr(self.zeit_manager, "needs_reset") else False

        # "Alle aktiv gewesenen Bahnen sind gestoppt" -> für inaktive Bahnen nicht warten
        all_active_stopped = (not g1_active or needs1) and (not g2_active or needs2)

        if all_active_stopped:
            self.zeitnehmung_buttons_control(False, False, False, True, False, False, False, True, True)

    def _ermittle_naechste_gruppen(self, aktueller_dg: int):
        try:
            next_tuple = self.durchgang_manager.lade_gruppen_von_durchgang(aktueller_dg + 1)
        except Exception:
            return None, None
        if not next_tuple:
            return None, None
        n1 = next_tuple[0] if len(next_tuple) > 0 and next_tuple[0] else None
        n2 = next_tuple[1] if len(next_tuple) > 1 and next_tuple[1] else None
        return n1, n2

    # ========= Hotkeys/GPIO aus deinen Settings lesen =========
    def _bind_hotkeys_from_settings(self):
        # Erst alles „sauber“ binden – Tk bind_all stapelt, also vorher keine globale Löschung,
        # sondern wir lesen die Keys frisch und binden gezielt (Doppeltbindungen sind idempotent genug).
        def bind_key(keysym, cb):
            keysym = (keysym or "").strip()
            if not keysym:
                return
            self.bind_all(f"<KeyPress-{keysym}>", cb)

        # aus deinen Eingabefeldern
        k_start1 = self.ent_key_start1.get() if hasattr(self, "ent_key_start1") else ""
        k_stop1  = self.ent_key_stop1.get()  if hasattr(self, "ent_key_stop1")  else ""
        k_start2 = self.ent_key_start2.get() if hasattr(self, "ent_key_start2") else ""
        k_stop2  = self.ent_key_stop2.get()  if hasattr(self, "ent_key_stop2")  else ""

        # Start global = beide Bahnen armiert -> externer Start global = KEIN separater Key in deiner GUI,
        # daher nutzen wir denselben Key wie „Start Bahn 1“ optional als globalen Fallback NICHT.
        # -> Globalen Start löst du per Button „Start (global)“ aus.
        # Die Triggers für den wirklichen Start sind:
        bind_key(k_start1, lambda e: (self.checked_Tastatur.get() and self._external_start(1)))
        bind_key(k_start2, lambda e: (self.checked_Tastatur.get() and self._external_start(2)))
        bind_key(k_stop1,  lambda e: (self.checked_Tastatur.get() and self._external_stop_lane(1)))
        bind_key(k_stop2,  lambda e: (self.checked_Tastatur.get() and self._external_stop_lane(2)))

    def _setup_gpio_from_settings(self):
        # Bestehende GPIOs schließen
        if self.gpio_inputs:
            try:
                self.gpio_inputs.close()
            except Exception:
                pass
            self.gpio_inputs = None

        if not self.checked_GPIO.get():
            return

        def to_pin(entry):
            try:
                s = entry.get().strip()
                return int(s) if s else None
            except Exception:
                return None

        pins = {
            "start1": to_pin(self.ent_gpio_start1) if hasattr(self, "ent_gpio_start1") else None,
            "stop1":  to_pin(self.ent_gpio_stop1)  if hasattr(self, "ent_gpio_stop1")  else None,
            "start2": to_pin(self.ent_gpio_start2) if hasattr(self, "ent_gpio_start2") else None,
            "stop2":  to_pin(self.ent_gpio_stop2)  if hasattr(self, "ent_gpio_stop2")  else None,
            # optional: globaler Startpin (nicht in deiner GUI -> None)
            "start_global": None,
        }

        handlers = {
            "start1": lambda: (self._armed_lane1 and self._external_start(1)),
            "stop1":  lambda: self._external_stop_lane(1),
            "start2": lambda: (self._armed_lane2 and self._external_start(2)),
            "stop2":  lambda: self._external_stop_lane(2),
            "start_global": lambda: (self._armed_global and self._external_start(None)),
        }

        self.gpio_inputs = GpioManager(pins, handlers)
