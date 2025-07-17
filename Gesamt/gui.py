from gpiozero import Button as GPIO_Button

from customtkinter import *
from spinbox import *
import events, time_manager, utils


# def init_gui(app):
#     pass

def init_gpio(app, event=None):
    if app.checked_GPIO.get():
        app.BuzzerStartBahn1 = GPIO_Button(app.GPIO_Start_1)
        app.BuzzerStopBahn1 = GPIO_Button(app.GPIO_Stop_1)
        app.BuzzerStartBahn2 = GPIO_Button(app.GPIO_Start_2)
        app.BuzzerStopBahn2 = GPIO_Button(app.GPIO_Stop_2)

def create_tabs(app):
    app.root.TabView = CTkTabview(app.root, anchor='nw', corner_radius=0, fg_color='transparent')
    app.root.TabView.pack(expand=1, side='top', fill='both', padx=5, pady=5)
    app.root.FTab1 = app.root.TabView.add(app.NAME_TAB1)
    app.root.FTab2 = app.root.TabView.add(app.NAME_TAB2)
    app.root.FTab3 = app.root.TabView.add(app.NAME_TAB3)

def create_tab1(app):
    app.root.Entry = CTkEntry(app.root.FTab1, corner_radius=0, placeholder_text='Gruppenname')
    app.root.Entry.pack(side='top', fill='x', padx=10, pady=10)
    app.root.Entry.bind('<Return>', events.add_wettkampfgruppe)

    app.root.LfReihenfolge = CTkScrollableFrame(app.root.FTab1, border_width=0, corner_radius=0, fg_color='transparent')
    app.root.LfReihenfolge.pack(expand=1 ,side='top', fill='both', padx=10, pady=10) 

    if len(app.Wettkampfgruppen) == 0:
        app.root.LNoGroups = CTkLabel(app.root.LfReihenfolge, text='Keine Gruppen angemeldet!', anchor='w')
        app.root.LNoGroups.grid(row=0, column=0, sticky=(W+E+N+S), padx=10, pady=5)
    else:
        zeichne_angemeldete_gruppen(app)

    app.root.BtnUebernehmen = CTkButton(app.root.FTab1, text='Gruppen übernehmen', command=lambda:events.uebernahme_gruppen(app, False), corner_radius=0)
    app.root.BtnUebernehmen.pack(side='bottom', fill='x', padx=10, pady=10)

def create_tab2(app):
    app.root.dg = CTkScrollableFrame(app.root.FTab2, border_width=0, fg_color='transparent')

    app.root.zeitnehmung = CTkFrame(app.root.FTab2, border_width=0, fg_color='transparent')
    app.root.BtnAnsichtWechseln = CTkButton(app.root.zeitnehmung, text='Ansicht wechseln', width=120, corner_radius=0, command=events.anzeige_umschalten)
    app.root.BtnAnsichtWechseln.pack(side='left', padx=5, pady=20, ipady=15) 
    app.root.CBDG = CTkComboBox(app.root.zeitnehmung, justify=CENTER, width=100, height=58, corner_radius=0, state='readonly', command=events.lade_zeitnehmungs_daten)
    app.root.CBDG.pack(side='left', padx=5, pady=20)
    app.root.BtnVorherigerDG = CTkButton(app.root.zeitnehmung, text='DG -', width=50, corner_radius=0, command=events.vorheriger_dg)
    app.root.BtnVorherigerDG.pack(side='left', padx=5, pady=20, ipady=15)
    app.root.BtnNaechsterDG = CTkButton(app.root.zeitnehmung, text='DG +', width=50, corner_radius=0, command=events.naechster_dg)
    app.root.BtnNaechsterDG.pack(side='left', padx=5, pady=20, ipady=15)
    app.root.BtnStart = CTkButton(app.root.zeitnehmung, text='Start', width=70, corner_radius=0, command=time_manager.start, state=DISABLED)
    app.root.BtnStart.pack(side='left', padx=5, pady=20, ipady=15)
    app.root.BtnAllesStop = CTkButton(app.root.zeitnehmung, text='Alles Stop', width=90,  corner_radius=0, command=time_manager.alles_stop, state=DISABLED)
    app.root.BtnAllesStop.pack(side='left', padx=5, pady=20, ipady=15)
    app.root.BtnWechsel = CTkButton(app.root.zeitnehmung, text='Bahn Wechsel', width=100, corner_radius=0, command=events.bahn_wechsel, state=DISABLED)
    app.root.BtnWechsel.pack(side='left', padx=5, pady=20, ipady=15)
    app.root.BtnZeitUebertragen = CTkButton(app.root.zeitnehmung, text='Zeit übertragen', width=110, corner_radius=0, command=events.werte_in_ansicht_uebertragen, state=DISABLED)
    app.root.BtnZeitUebertragen.pack(side='left', padx=5, pady=20, ipady=15)

    app.root.LfBahnen = CTkFrame(app.root.FTab2, border_width=1, corner_radius=0, fg_color='transparent')

    app.root.CB1 = CTkCheckBox(app.root.LfBahnen, text='Bahn 1', variable=app.checked_Bahn_1, corner_radius=0, command=events.switch_bahn_1_state)
    app.root.CB1.grid(row=0, column=0, padx=5, pady=(3,0))
    app.root.G1 = CTkLabel(app.root.LfBahnen, text='...', corner_radius=0, font=(app.GlobalFontArt, app.GlobalFontSizeTitle), state=DISABLED)
    app.root.G1 .grid(row=0, column=1, padx=5, pady=(5,0))
    app.root.T1 = CTkLabel(app.root.LfBahnen, text='00:00:00', corner_radius=0, font=(app.GlobalFontArt, app.GlobalFontSizeTitle), state=DISABLED)
    app.root.T1.grid(row=0, column=2, padx=5, pady=(5,0))
    app.root.LblFehler1 = CTkLabel(app.root.LfBahnen, text='Fehler')
    app.root.LblFehler1 .grid(row=0, column=3, padx=5, pady=(5,0))
    app.root.F1 = CTkEntry(app.root.LfBahnen, width=5, corner_radius=0)
    app.root.F1.grid(row=0, column=4, padx=5, pady=(5,0))
    app.root.B1 = CTkButton(app.root.LfBahnen, text='Stop', width=70, corner_radius=0, command=time_manager.stop_1, state=DISABLED)
    app.root.B1.grid(row=0, column=5, padx=(0,5), pady=(5,0))

    app.root.CB2 = CTkCheckBox(app.root.LfBahnen, text='Bahn 2', variable=app.checked_Bahn_2, corner_radius=0, command=events.switch_bahn_2_state)
    app.root.CB2.grid(row=1, column=0, padx=5, pady=(0,3))
    app.root.G2 = CTkLabel(app.root.LfBahnen, text='...', corner_radius=0, font=(app.GlobalFontArt, app.GlobalFontSizeTitle), state=DISABLED)
    app.root.G2 .grid(row=1, column=1, padx=5, pady=(0,5))
    app.root.T2 = CTkLabel(app.root.LfBahnen, text='00:00:00', corner_radius=0, font=(app.GlobalFontArt, app.GlobalFontSizeTitle), state=DISABLED)
    app.root.T2.grid(row=1, column=2, padx=5, pady=(0,5))
    app.root.LblFehler2 = CTkLabel(app.root.LfBahnen, text='Fehler')
    app.root.LblFehler2 .grid(row=1, column=3, padx=5, pady=(0,5))
    app.root.F2 = CTkEntry(app.root.LfBahnen, width=5, corner_radius=0)
    app.root.F2.grid(row=1, column=4, padx=5, pady=(0,5))
    app.root.B2 = CTkButton(app.root.LfBahnen, text='Stop', width=70, corner_radius=0, command=time_manager.stop_2, state=DISABLED)
    app.root.B2.grid(row=1, column=5, padx=(0,5), pady=(0,5))

    app.root.korrektur = CTkFrame(app.root.FTab2, border_width=0, fg_color='transparent')

    app.root.BtnStopReset = CTkButton(app.root.korrektur, text='Stop and Reset', width=110, corner_radius=0, command=time_manager.stop_reset, state=DISABLED)
    app.root.BtnStopReset.pack(side='left', padx=5, pady=20, ipady=15) 
    app.root.BtnLoeZ1 = CTkButton(app.root.korrektur, text='DG Zeit 1+2 löschen', width=120, corner_radius=0, command=time_manager.zeit_1_loeschen)
    app.root.BtnLoeZ1.pack(side='left', padx=5, pady=20, ipady=15) 
    app.root.BtnLoeZ2 = CTkButton(app.root.korrektur, text='DG Zeit 2 löschen', width=120, corner_radius=0, command=time_manager.zeit_2_loeschen)
    app.root.BtnLoeZ2.pack(side='left', padx=5, pady=20, ipady=15) 

def create_tab3(app):
    app.root.setupEingabe = CTkFrame(app.root.FTab3, border_width=1, corner_radius=0, fg_color='transparent')
    app.root.setupEingabe.pack(side='top', fill='x', padx=10, pady=5)
    app.root.CheckTastatur = CTkCheckBox(app.root.setupEingabe, text='Tastatur', corner_radius=0, variable=app.checked_Tastatur)
    app.root.CheckTastatur.grid(row=0, column=0, padx=10, pady=10)
    app.root.CheckGPIO = CTkCheckBox(app.root.setupEingabe, text='GPIO', variable=app.checked_GPIO, corner_radius=0, command=init_gpio)
    app.root.CheckGPIO.grid(row=0, column=1, pady=10)
    app.root.CheckRahmen = CTkCheckBox(app.root.setupEingabe, text='Rahmen ausblenden', variable=app.checked_Rahmen, corner_radius=0, command=events.update_rahmen_anzeige)
    app.root.CheckRahmen.grid(row=0, column=2, padx=10, pady=10)
    app.root.CheckKonsole = CTkCheckBox(app.root.setupEingabe, text='Konsole', variable=app.checked_Konsole, corner_radius=0)
    app.root.CheckKonsole.grid(row=0, column=3, pady=10)

    app.root.setupTasten = CTkFrame(app.root.FTab3, border_width=1, corner_radius=0, fg_color='transparent')
    app.root.setupTasten.pack(side='top', fill='x', padx=10, pady=5)
    app.root.Start_Taste_1_Label = CTkLabel(app.root.setupTasten, text='Start 1')
    app.root.Start_Taste_1_Label.grid(row=0, column=0, padx=10, pady=10)
    app.root.Start_Taste_1 = CTkEntry(app.root.setupTasten, width=30, corner_radius=0)
    app.root.Start_Taste_1.grid(row=0, column=1, pady=10)
    app.root.Stop_Taste_1_Label = CTkLabel(app.root.setupTasten, text='Stop 1')
    app.root.Stop_Taste_1_Label.grid(row=0, column=2, padx=10, pady=10)
    app.root.Stop_Taste_1 = CTkEntry(app.root.setupTasten, width=30, corner_radius=0)
    app.root.Stop_Taste_1.grid(row=0, column=3, pady=10)
    app.root.Start_Taste_2_Label = CTkLabel(app.root.setupTasten, text='Start 2')
    app.root.Start_Taste_2_Label.grid(row=0, column=4, padx=10, pady=10)
    app.root.Start_Taste_2 = CTkEntry(app.root.setupTasten, width=30, corner_radius=0)
    app.root.Start_Taste_2.grid(row=0, column=5, pady=10)
    app.root.Stop_Taste_2_Label = CTkLabel(app.root.setupTasten, text='Stop 2')
    app.root.Stop_Taste_2_Label.grid(row=0, column=6, padx=10,pady=10)
    app.root.Stop_Taste_2 = CTkEntry(app.root.setupTasten, width=30, corner_radius=0)
    app.root.Stop_Taste_2.grid(row=0, column=7, pady=10)

    app.root.Start_Taste_1.insert(0, app.Taste_Start_1)
    app.root.Stop_Taste_1.insert(0, app.Taste_Stop_1)
    app.root.Start_Taste_2.insert(0, app.Taste_Start_2)
    app.root.Stop_Taste_2.insert(0, app.Taste_Stop_2)

    app.root.setupGPIO = CTkFrame(app.root.FTab3, border_width=1, corner_radius=0, fg_color='transparent')
    app.root.setupGPIO.pack(side='top', fill='x', padx=10, pady=5)
    app.root.Start_GPIO_1_Label = CTkLabel(app.root.setupGPIO, text='Start 1')
    app.root.Start_GPIO_1_Label.grid(row=0, column=0, padx=10, pady=10)
    app.root.Start_GPIO_1 = CTkEntry(app.root.setupGPIO, width=30, corner_radius=0)
    app.root.Start_GPIO_1.grid(row=0, column=1, pady=10)
    app.root.Stop_GPIO_1_Label = CTkLabel(app.root.setupGPIO, text='Stop 1')
    app.root.Stop_GPIO_1_Label.grid(row=0, column=2, padx=10, pady=10)
    app.root.Stop_GPIO_1 = CTkEntry(app.root.setupGPIO, width=30, corner_radius=0)
    app.root.Stop_GPIO_1.grid(row=0, column=3, pady=10)
    app.root.Start_GPIO_2_Label = CTkLabel(app.root.setupGPIO, text='Start 2')
    app.root.Start_GPIO_2_Label.grid(row=0, column=4, padx=10, pady=10)
    app.root.Start_GPIO_2 = CTkEntry(app.root.setupGPIO, width=30, corner_radius=0)
    app.root.Start_GPIO_2.grid(row=0, column=5, pady=10)
    app.root.Stop_GPIO_2_Label = CTkLabel(app.root.setupGPIO, text='Stop 2')
    app.root.Stop_GPIO_2_Label.grid(row=0, column=6, padx=10,pady=10)
    app.root.Stop_GPIO_2 = CTkEntry(app.root.setupGPIO, width=30, corner_radius=0)
    app.root.Stop_GPIO_2.grid(row=0, column=7, pady=10)

    app.root.Start_GPIO_1.insert(0, app.GPIO_Start_1)
    app.root.Stop_GPIO_1.insert(0, app.GPIO_Stop_1)
    app.root.Start_GPIO_2.insert(0, app.GPIO_Start_2)
    app.root.Stop_GPIO_2.insert(0, app.GPIO_Stop_2)

    app.root.setupStyle = CTkFrame(app.root.FTab3, border_width=1, corner_radius=0, fg_color='transparent')
    app.root.setupStyle.pack(side='top', fill='x', padx=10, pady=5)
    app.root.SGZL = CTkLabel(app.root.setupStyle, text='Schriftgröße Zeit')
    app.root.SGZL.grid(row=0, column=0, padx=10, pady=10, sticky=(W))
    app.root.SGZ = IntSpinbox(app.root.setupStyle, command=events.update_fontsize_zeit)
    app.root.SGZ.grid(row=0, column=1, padx=10, pady=10)
    app.root.SGZ.set(app.AnzeigeFontSizeTime)
    app.root.SGGL = CTkLabel(app.root.setupStyle, text='Schriftgröße Gruppe')
    app.root.SGGL.grid(row=0, column=2, padx=10, pady=10, sticky=(W))
    app.root.SGG = IntSpinbox(app.root.setupStyle, command=events.update_fontsize_gruppe)
    app.root.SGG.grid(row=0, column=3, padx=10, pady=10)
    app.root.SGG.set(app.AnzeigeFontSizeGroup)

    app.root.setupAutoAnpassung = CTkFrame(app.root.FTab3, border_width=1, corner_radius=0, fg_color='transparent')
    app.root.setupAutoAnpassung.pack(side='top', fill='x', padx=10, pady=5)
    app.root.LblAnpassungTitel = CTkLabel(app.root.setupAutoAnpassung, text='Aktuelle Fensterhöhe')
    app.root.LblAnpassungTitel.grid(row=0, column=0, padx=10, pady=10, sticky=(W))
    app.root.LblAnpassungWert = CTkLabel(app.root.setupAutoAnpassung, text=app.screen_height)
    app.root.LblAnpassungWert.grid(row=0, column=1, padx=10, pady=10, sticky=(W))
    app.root.LblFaktorZeit = CTkLabel(app.root.setupAutoAnpassung, text='Faktor Zeit')
    app.root.LblFaktorZeit.grid(row=1, column=0, padx=10, pady=2, sticky=(W))
    app.root.SBFaktorZeit = IntSpinbox(app.root.setupAutoAnpassung)
    app.root.SBFaktorZeit.grid(row=1, column=1, padx=10, pady=2)
    app.root.SBFaktorZeit.set(3)
    app.root.LblFaktorGruppen = CTkLabel(app.root.setupAutoAnpassung, text='Faktor Gruppen')
    app.root.LblFaktorGruppen.grid(row=2, column=0, padx=10, pady=2, sticky=(W))
    app.root.SBFaktorGruppen = IntSpinbox(app.root.setupAutoAnpassung)
    app.root.SBFaktorGruppen.grid(row=2, column=1, padx=10, pady=2)
    app.root.SBFaktorGruppen.set(20)
    app.root.LblFaktorInfo = CTkLabel(app.root.setupAutoAnpassung, text='Faktor Info')
    app.root.LblFaktorInfo.grid(row=3, column=0, padx=10, pady=2, sticky=(W))
    app.root.SBFaktorInfo = IntSpinbox(app.root.setupAutoAnpassung)
    app.root.SBFaktorInfo.grid(row=3, column=1, padx=10, pady=2)
    app.root.SBFaktorInfo.set(65)
    app.root.LblFaktorAuswertung = CTkLabel(app.root.setupAutoAnpassung, text='Faktor Auswertung')
    app.root.LblFaktorAuswertung.grid(row=4, column=0, padx=10, pady=2, sticky=(W))
    app.root.SBFaktorAuswertung = IntSpinbox(app.root.setupAutoAnpassung)
    app.root.SBFaktorAuswertung.grid(row=4, column=1, padx=10, pady=2)
    app.root.SBFaktorAuswertung.set(40)
    app.root.BtnChangeStyle = CTkButton(app.root.setupAutoAnpassung, text='Anzeige Autoanpassung', corner_radius=0, command=events.change_fontsize_from_windowsize)
    app.root.BtnChangeStyle.grid(row=5, column=0, padx=10, pady=10, ipadx=10)

    if app.Testmodus == True:
        app.root.setupTest = CTkFrame(app.root.FTab3, border_width=1, corner_radius=0, fg_color='transparent')
        app.root.setupTest.pack(side='bottom', fill='x', padx=10, pady=5)
        app.root.LblAnzahlGruppen = CTkLabel(app.root.setupTest, text='Anzahl Testgruppen')
        app.root.LblAnzahlGruppen.grid(row=0, column=0, padx=10, pady=10)
        app.root.SBAnzahlGruppen = IntSpinbox(app.root.setupTest)
        app.root.SBAnzahlGruppen.grid(row=0, column=1, padx=10, pady=10)
        app.root.LblAnzahlDamenGruppen = CTkLabel(app.root.setupTest, text='Anzahl Testdamengruppen')
        app.root.LblAnzahlDamenGruppen.grid(row=0, column=2, padx=10, pady=10)
        app.root.SBAnzahlDamenGruppen = IntSpinbox(app.root.setupTest)
        app.root.SBAnzahlDamenGruppen.grid(row=0, column=3, padx=10, pady=10)
        app.root.BtnAnzahlGruppen = CTkButton(app.root.setupTest, text='Erstellen', corner_radius=0, command=events.test_gruppen_erstellen)
        app.root.BtnAnzahlGruppen.grid(row=0, column=4, padx=10, pady=10)
       
def init_anzeige(app):
    app.anzeige = CTkToplevel()
    app.anzeige.title(app.TitleAnzeige)
    app.anzeige.minsize(700, 400)
    app.anzeige.configure(fg_color=app.AnzeigeBackgroundColor)
    # app.anzeige.iconbitmap(app.FileIcon)

    app.anzeige.frame = CTkFrame(app.anzeige, border_width=0, corner_radius=0, fg_color=app.AnzeigeBackgroundColor)
    app.anzeige.frame.pack(expand=1, side=TOP, fill=BOTH, padx=20, pady=20)

    app.anzeige.G1 = CTkLabel(app.anzeige.frame, text='', anchor='nw', corner_radius=0, text_color=app.AnzeigeGroupColor, fg_color=app.AnzeigeBackgroundColor, font=(app.GlobalFontArt, app.AnzeigeFontSizeGroup))
    app.anzeige.Z1 = CTkLabel(app.anzeige.frame, text='00:00:00', anchor='center', corner_radius=0, text_color=app.AnzeigeTimeColor, fg_color=app.AnzeigeBackgroundColor, font=(app.GlobalFontArt, app.AnzeigeFontSizeTime))
    app.anzeige.Z2 = CTkLabel(app.anzeige.frame, text='00:00:00', anchor='center', corner_radius=0, text_color=app.AnzeigeTimeColor, fg_color=app.AnzeigeBackgroundColor, font=(app.GlobalFontArt, app.AnzeigeFontSizeTime))
    app.anzeige.G2 = CTkLabel(app.anzeige.frame, text='', anchor='ne', corner_radius=0, text_color=app.AnzeigeGroup2Color, fg_color=app.AnzeigeBackgroundColor, font=(app.GlobalFontArt, app.AnzeigeFontSizeGroup))
    
    app.anzeige.ERG = CTkFrame(app.anzeige.frame, border_width=0, corner_radius=0)
    app.anzeige.ERG.pack(expand=1, side=TOP, fill=BOTH)

    app.anzeige.INFO = CTkFrame(app.anzeige.frame, fg_color=app.AnzeigeNextColor, border_width=0, corner_radius=0)
    app.anzeige.INFO.pack(expand=0, side='bottom' , fill='x', pady=20, padx=20)

    events.change_fontsize_from_windowsize(app)

def show_info(app):
    for widgets in app.anzeige.INFO.winfo_children():
        widgets.grid_remove()

    bahnA = ''
    bahnB = ''
    
    dg_select = app.root.CBDG.get()
    if dg_select != '':
        dg_select = int(dg_select)+1
    else:
        dg_select = 1

    app.Durchgänge.sort(key=utils.sort_time_by_row)
    for index, item in enumerate(app.Durchgänge):
        if item['dg'] == dg_select:
            if bahnA == '':
                bahnA = item['wettkampfgruppe']
            elif bahnB == '':
                bahnB = item['wettkampfgruppe']
    app.Durchgänge.sort(key=lambda dg: utils.sort_time(app, dg))


    lbl = CTkLabel(app.anzeige.INFO, text='NÄCHSTER \nDURCHGANG', fg_color=app.AnzeigeNextColor, font=(app.GlobalFontArt, app.AnzeigeFontSizeInfo))
    lbl.grid(row=0, column=0, rowspan=2, sticky=(W+E+N+S), padx=(40,0))

    lblA = CTkLabel(app.anzeige.INFO, text='Bahn A', fg_color=app.AnzeigeNextColor, font=(app.GlobalFontArt, app.AnzeigeFontSizeInfo))
    lblA.grid(row=0, column=1, sticky=(W+E+N+S), padx=(40,0))

    lblB = CTkLabel(app.anzeige.INFO, text='Bahn B', fg_color=app.AnzeigeNextColor, font=(app.GlobalFontArt, app.AnzeigeFontSizeInfo))
    lblB.grid(row=0, column=2, sticky=(W+E+N+S), padx=(40,0))

    text = bahnA
    a = CTkLabel(app.anzeige.INFO, text=text, fg_color=app.AnzeigeNextColor, font=(app.GlobalFontArt, app.AnzeigeFontSizeInfo))
    a.grid(row=1, column=1, sticky=(W+E+N+S), padx=(40,0))

    text = bahnB
    b = CTkLabel(app.anzeige.INFO, text=text, fg_color=app.AnzeigeNextColor, font=(app.GlobalFontArt, app.AnzeigeFontSizeInfo))
    b.grid(row=1, column=2, sticky=(W+E+N+S), padx=(40,0))

def show_changing_window(app, event, typ, row, column):
    grp_text = ''
    zeit1_text = ''
    fehler1_text = ''
    zeit2_text = ''
    fehler2_text = ''
    for x in app.Durchgänge:
        if x['typ'] == typ and x['row'] == row and x['column'] == column:
            grp_text = x['wettkampfgruppe']
            zeit1_text = x['zeit1']
            fehler1_text = x['fehler1']
            zeit2_text = x['zeit2']
            fehler2_text = x['fehler2']
    
    if zeit1_text != '':
        app.changewindow = CTkToplevel()
        app.changewindow.title('Änderung')

        # app.changewindow.iconphoto(False, app.icon)

        app.changewindow.frame = CTkFrame(app.changewindow)
        app.changewindow.frame.pack(expand=1, side=TOP, fill=BOTH)

        app.changewindow.LZ1 = CTkLabel(app.changewindow.frame, text='Zeit 1')
        app.changewindow.LZ1.grid(row=0, column=1, padx=(0,5), pady=(20,0))

        app.changewindow.LF1 = CTkLabel(app.changewindow.frame, text='Feh. 1')
        app.changewindow.LF1.grid(row=0, column=2, padx=(0,5), pady=(20,0))

        app.changewindow.LZ2 = CTkLabel(app.changewindow.frame, text='Zeit 2')
        app.changewindow.LZ2.grid(row=0, column=3, padx=(0,5), pady=(20,0))

        app.changewindow.LF2 = CTkLabel(app.changewindow.frame, text='Feh. 2')
        app.changewindow.LF2.grid(row=0, column=4, padx=(0,20), pady=(20,0))

        app.changewindow.GRP = CTkLabel(app.changewindow.frame, text=grp_text, anchor='w')
        app.changewindow.GRP.grid(row=1, column=0, sticky=(W), padx=(20,5), pady=(0,20))

        app.changewindow.Z1 = CTkEntry(app.changewindow.frame, width=80)
        app.changewindow.Z1.grid(row=1, column=1, padx=(0,5), pady=(0,20))
        app.changewindow.Z1.insert(0, zeit1_text)
        
        app.changewindow.F1 = CTkEntry(app.changewindow.frame, width=30)
        app.changewindow.F1.grid(row=1, column=2, padx=(0,5), pady=(0,20))
        app.changewindow.F1.insert(0, fehler1_text)

        app.changewindow.Z2 = CTkEntry(app.changewindow.frame, width=80)
        app.changewindow.Z2.grid(row=1, column=3, padx=(0,5), pady=(0,20))
        app.changewindow.Z2.insert(0, zeit2_text)
        
        app.changewindow.F2 = CTkEntry(app.changewindow.frame, width=30)
        app.changewindow.F2.grid(row=1, column=4, padx=(0,20), pady=(0,20))
        app.changewindow.F2.insert(0, fehler2_text)

        app.changeWindowIsAenderungMsg = StringVar()
        app.changewindow.FehlerMsg = CTkLabel(app.changewindow.frame, textvariable=app.changeWindowIsAenderungMsg)
        app.changewindow.FehlerMsg.grid(row=2, column=0, columnspan=5, padx=(0,5), pady=(20,0))

        app.changewindow.BTN = CTkButton(app.changewindow.frame, text='Speichern')
        app.changewindow.BTN.grid(row=3, column=1, columnspan=2, sticky=(W+N+E+S), pady=(0,20))
        app.changewindow.BTN.bind('<Button-1>', lambda event, typ=typ, row=row, column=column:app.closeChangingWindow(event, typ, row, column))

def close_changing_window(app, event, typ, row, column):
    for x in app.Durchgänge:
        if x['typ'] == typ and x['row'] == row and x['column'] == column:
            z1 = app.changewindow.Z1.get()
            f1 = app.changewindow.F1.get()
            z2 = app.changewindow.Z2.get()
            f2 = app.changewindow.F2.get()
            
            msg = ''
            if z1 != '':
                if utils.validate_time(z1) == False:
                    msg += 'Zeit 1 stimmt nicht! \n'
                if utils.validate_number(f1) == False:
                    msg += 'Fehler 1 stimmt nicht! \n'
            if z2 != '':
                if utils.validate_time(z2) == False:
                    msg += 'Zeit 2 stimmt nicht! \n'
                if utils.validate_number(f2) == False:
                    msg += 'Fehler 2 stimmt nicht! \n'

            if msg != '':
                app.changeWindowIsAenderungMsg.set(msg)
                return
            else:
                if z1 != '':
                    f1 = int(f1)
                    x['zeit1'] = z1
                    x['fehler1'] = f1

                    text = str(z1)
                    if f1 > 0:
                        text += ' +' + str(f1)
                    
                    events.zeichne_neue_werte(row, column+1, text, row, column, typ)

                    if z2 == '':
                        x['bestzeit'] = z1
                        x['fehlerbest'] = f1
                        events.zeichne_neue_werte(row, column+3, text, row, column, typ)

                if z1 != '' and z2 != '':
                    f2 = int(f2)
                    x['zeit2'] = z2
                    x['fehler2'] = f2

                    text2 = str(z2)
                    if f2 > 0:
                        text2 += ' +' + str(f2)
                    events.zeichne_neue_werte(row, column+2, text2, row, column, typ)

                    time1 = events.addiere_fehler_zur_zeit(z1, f1) 
                    time2 = events.addiere_fehler_zur_zeit(z2, f2)

                    if events.berechne_bestzeit(time1, time2) == 2:
                        x['bestzeit'] = z2
                        x['fehlerbest'] = f2

                        events.zeichne_neue_werte(row, column+3, text2, row, column, typ)

                app.changewindow.Z1.delete(0, END)
                app.changewindow.F1.delete(0, END)
                app.changewindow.Z2.delete(0, END)
                app.changewindow.F2.delete(0, END)

    app.changewindow.destroy()
    events.bestzeit_platzierung_berechnen()

def zeichne_angemeldete_gruppen(app):
    for widgets in app.root.LfReihenfolge.winfo_children():
        widgets.grid_remove()
    
    if len(app.Wettkampfgruppen) == 0:
        app.root.LNoGroups = CTkLabel(app.root.LfReihenfolge, text='Keine Gruppen angemeldet!')
        app.root.LNoGroups.grid(row=0, column=0, sticky=(W), padx=10, pady=5)
    else:
        w = CTkLabel(app.root.LfReihenfolge, text='Gruppenname')
        w.grid(row=0, column=0, sticky=(W), padx=10, pady='2')

        e = CTkLabel(app.root.LfReihenfolge, text='Reihenf.')
        e.grid(row=0, column=1, sticky=(W), padx=10, pady='2')

        cb = CTkLabel(app.root.LfReihenfolge, text='Damen')
        cb.grid(row=0, column=2, sticky=(W), padx=10, pady='2')

        x = CTkLabel(app.root.LfReihenfolge, text='#')
        x.grid(row=0, column=3, sticky=(W), padx=10, pady='2')

    for index, i in enumerate(app.Wettkampfgruppen):
        row = index + 1
        gruppenname = i['gruppenname']
        reihenfolge = i['reihenfolge']
        damenwertung = 'NEIN'
        if i['damenwertung'] ==True:
            damenwertung = 'JA'

        w = CTkLabel(app.root.LfReihenfolge, text=gruppenname)
        w.grid(row=row, column=0, sticky=(W), padx=10, pady='2')

        e = CTkEntry(app.root.LfReihenfolge, width=50, justify = 'center')
        e.grid(row=row, column=1, sticky=(W), padx=10, pady='2')
        e.insert(0, reihenfolge)
        e.bind('<KeyRelease>', lambda event, name=gruppenname: events.reihenfolge_speichern(event, name))

        cb = CTkLabel(app.root.LfReihenfolge, text=damenwertung)
        cb.grid(row=row, column=2, sticky=(W+E+N+S), padx=10, pady='2')            
        cb.bind('<Button-1>', lambda event,  name=gruppenname, value=i['damenwertung']: events.eintrag_damenwertung(event, name, value))

        x = CTkLabel(app.root.LfReihenfolge, text='', image=app.iconDelete)
        x.grid(row=row, column=3, sticky=(W), padx=10, pady='2')
        x.bind('<Button-1>', lambda event, name=gruppenname: events.delete_wettkampfgruppe(event, name))

def zeichne_grundansicht(app, damenwertung, new_Array):
    txt = ''
    time = ''
    rh = ''
    app.DurchgangNummer = 1
    zeichne_zeit_table(app, 'Grunddurchgang (Z1/Z2/B)', app.AnzeigeGDStartColumn, app.AnzeigeGDStartRow, txt, time, rh, app.AnzahlGrunddurchgänge, True, app.TYP_GD, new_Array)
    zeichne_zeit_table(app, 'KO 1-16 (Z1/Z2/B)', app.AnzeigeKO16StartColumn, app.AnzeigeKO16StartRow, txt, time, rh, 16, True, app.TYP_KO16, new_Array)
    zeichne_zeit_table(app, 'KO 1-8 (Z1/Z2/B)', app.AnzeigeKO8StartColumn, app.AnzeigeKO8StartRow, txt, time, rh, 8, True, app.TYP_KO8, new_Array)
    zeichne_zeit_table(app, 'KO 1-4 (Z1/Z2/B)', app.AnzeigeKO4StartColumn, app.AnzeigeKO4StartRow, txt, time, rh, 4, True, app.TYP_KO4, new_Array)
    zeichne_zeit_table(app, 'Kleines Finale (Z1/Z2/B)', app.AnzeigeKFStartColumn, app.AnzeigeKFStartRow, txt, time, rh, 2, True, app.TYP_KF, new_Array)
    zeichne_zeit_table(app, 'Finale (Z1/Z2/B)', app.AnzeigeFStartColumn, app.AnzeigeFStartRow, txt, time, rh, 2, True, app.TYP_F, new_Array)
    if damenwertung == True:
        zeichne_zeit_table(app, 'Damenwertung (Z1/Z2/B)', app.AnzeigeDWStartColumn, app.AnzeigeDWStartRow, txt, time, rh, app.AnzahlDamendurchgänge, True, app.TYP_DW, new_Array)
    app.root.CBDG.configure(values=app.DGNumbers)
    app.root.CBDG.set('1')
    
def zeichne_zeit_table(app, title, startcolumn, startrow, gruppe_txt, time_txt, rh_text, anzahl_gruppen, show_rh, typ, new_Array):
    title = CTkLabel(app.root.dg, text=title, font=(app.GlobalFontArt, app.GlobalFontSizeTitle), anchor='w')
    title.grid(row=startrow, column=startcolumn, columnspan=5, sticky=(W+E+N+S), padx=(5,0))
    col1 = startcolumn + 1
    col2 = startcolumn + 2
    col3 = startcolumn + 3
    col4 = startcolumn + 4
    col5 = startcolumn + 5
    hinweis_text = ''
    for i in range(anzahl_gruppen):
        if typ == app.TYP_KO16:
            ko16_index = i + 1
            if ko16_index == 1: 
                hinweis_text = 'GD_1'
            elif ko16_index == 2: 
                hinweis_text = 'GD_16'
            elif ko16_index == 3: 
                hinweis_text = 'GD_2'
            elif ko16_index == 4: 
                hinweis_text = 'GD_15'
            elif ko16_index == 5: 
                hinweis_text = 'GD_3'
            elif ko16_index == 6: 
                hinweis_text = 'GD_14'
            elif ko16_index == 7: 
                hinweis_text = 'GD_4'
            elif ko16_index == 8: 
                hinweis_text = 'GD_13'
            elif ko16_index == 9: 
                hinweis_text = 'GD_5'
            elif ko16_index == 10: 
                hinweis_text = 'GD_12'
            elif ko16_index == 11: 
                hinweis_text = 'GD_6'
            elif ko16_index == 12: 
                hinweis_text = 'GD_11'
            elif ko16_index == 13: 
                hinweis_text = 'GD_7'
            elif ko16_index == 14: 
                hinweis_text = 'GD_10'
            elif ko16_index == 15: 
                hinweis_text = 'GD_8'
            elif ko16_index == 16: 
                hinweis_text = 'GD_9'  
        elif typ == app.TYP_KO8:
            ko8_index = i + 1
            if ko8_index == 1: 
                hinweis_text = 'KO16_1'
            elif ko8_index == 2: 
                hinweis_text = 'KO16_8'
            elif ko8_index == 3: 
                hinweis_text = 'KO16_2'
            elif ko8_index == 4: 
                hinweis_text = 'KO16_7'
            elif ko8_index == 5: 
                hinweis_text = 'KO16_3'
            elif ko8_index == 6: 
                hinweis_text = 'KO16_6'
            elif ko8_index == 7: 
                hinweis_text = 'KO16_4'
            elif ko8_index == 8: 
                hinweis_text = 'KO16_5'
        elif typ == app.TYP_KO4 :
            ho4_index = i + 1
            if ho4_index == 1: 
                hinweis_text = 'KO8_1'
            elif ho4_index == 2: 
                hinweis_text = 'KO8_4'
            elif ho4_index == 3: 
                hinweis_text = 'KO8_2'
            elif ho4_index == 4: 
                hinweis_text = 'KO8_3'
        elif typ == app.TYP_KF :
            kf_index = i + 1
            if kf_index == 1: 
                hinweis_text = 'KO4_3'
            elif kf_index == 2: 
                hinweis_text = 'KO4_4'
        elif typ == app.TYP_F :
            f_index = i + 1
            if f_index == 1: 
                hinweis_text = 'KO4_1'
            elif f_index == 2: 
                hinweis_text = 'KO4_2'
        else:
            hinweis_text=''
        row = startrow + i + 1
        durchgang = CTkLabel(app.root.dg, text=app.DurchgangNummer, fg_color=app.GlobalDGBackgroundColor, anchor='center')
        text = CTkLabel(app.root.dg, text=gruppe_txt)
        time1 = CTkLabel(app.root.dg, text=time_txt, anchor='e')
        time2 = CTkLabel(app.root.dg, text=time_txt, anchor='e')
        time3 = CTkLabel(app.root.dg, text=time_txt, anchor='e')
        if show_rh == True:
            lrh = CTkLabel(app.root.dg, text=rh_text, anchor='center')
        rh = i + 1
        if rh % 2:
            if new_Array == True:
                utils.konvertiere_array(app, app.DurchgangNummer, gruppe_txt, typ, row, col1, hinweis_text)
            durchgang.grid(row=row, column=startcolumn, rowspan=2, sticky=(W+E+N+S), padx=(5,0), pady=(1,0), ipadx=5)
            text.grid(row=row, column=col1, sticky=(W), pady=(1,0), ipady='2', ipadx=10)
            time1.grid(row=row, column=col2, sticky=(W), pady=(1,0), ipady='2', ipadx=10)
            time2.grid(row=row, column=col3, sticky=(W), pady=(1,0), ipady='2', ipadx=10)
            time3.grid(row=row, column=col4, sticky=(W), pady=(1,0), ipady='2', ipadx=10)
            if show_rh == True:
                lrh.grid(row=row, column=col5, sticky=(W), pady=(1,0), ipady='2', ipadx=10)
            app.DurchgangNummer += 1
        else:
            if new_Array == True:
                utils.konvertiere_array(app, app.DurchgangNummer-1, gruppe_txt, typ, row, col1, hinweis_text)    
            text.grid(row=row, column=col1, sticky=(W), pady='0', ipady='2', ipadx=10) 
            time1.grid(row=row, column=col2, sticky=(W), pady='0', ipady='2', ipadx=10) 
            time2.grid(row=row, column=col3, sticky=(W), pady='0', ipady='2', ipadx=10)
            time3.grid(row=row, column=col4, sticky=(W), pady='0', ipady='2', ipadx=10)
            if show_rh == True:
                lrh.grid(row=row, column=col5, sticky=(W), pady='0', ipady='2', ipadx=10)
        