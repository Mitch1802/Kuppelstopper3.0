from tkinter import *
from tkinter.ttk import *
from datetime import datetime
import time
import os
from gpiozero import Button as GPIO_Button

class Hauptfenster():
    # Hauptfenster
    def __init__(self):
        self.file_angriffbefehel = './Resources/AngriffsbefehlWonie.mp3'
        self.GPIO_Start_1 = 17
        self.GPIO_Stop_1 = 27
        self.GPIO_Start_2 = 19
        self.GPIO_Stop_2 = 26
        self.Taste_Start_1 = 'a'
        self.Taste_Stop_1 = 'q'
        self.Taste_Start_2 = 's'
        self.Taste_Stop_2 = 'w'

        self.Wettkampfgruppen = []
        self.time_is_running_1 = False
        self.time_is_running_2 = False
        self.start_time_1 = ""
        self.start_time_2 = ""

        self.__root = Tk()
        self.__root.title("KuppelStopper 3.0")
        self.__root.minsize(1000, 700)

        self.icon = PhotoImage(file='./Resources/Kuppelstopper.png')
        self.__root.iconphoto(False, self.icon)
        
        COLOR_TAB_INACTIVE = '#FFFFFF'
        COLOR_TAB_ACTIVE = "#D3C9C6"
        COLOR_BUTTON_ACTIVE = COLOR_TAB_ACTIVE
        COLOR_BUTTON_HOVER = "#C2BCBA"
        COLOR_BUTTON_DISABLED = "#FFFFFF"

        self.style = Style()
        self.style.theme_use("default")
        self.style.configure('.', background='white')
        self.style.configure('TNotebook', borderwidth=0, background=COLOR_TAB_INACTIVE)
        self.style.configure('TNotebook.Tab', relief=SOLID, borderwidth=0, bordercolor=COLOR_TAB_INACTIVE, darkcolor=COLOR_TAB_INACTIVE, lightcolor=COLOR_TAB_INACTIVE, padding=[10,5], background=COLOR_TAB_INACTIVE)
        self.style.map('TNotebook.Tab', background=[("selected",COLOR_TAB_ACTIVE),("active",COLOR_TAB_ACTIVE)])
        self.style.configure('TButton', relief=SOLID, borderwidth=0, bordercolor=COLOR_BUTTON_ACTIVE, darkcolor=COLOR_BUTTON_ACTIVE, lightcolor=COLOR_BUTTON_ACTIVE, padding=[10,5], background=COLOR_BUTTON_ACTIVE)
        self.style.map('TButton', background=[("active",COLOR_BUTTON_HOVER),("disabled",COLOR_BUTTON_DISABLED)], foreground=[("disabled",COLOR_BUTTON_DISABLED)])

        # Menü
        self.__root.tabControl = Notebook(self.__root, padding='0')
        self.__root.tab1 = Frame(self.__root.tabControl, padding='5')
        self.__root.tab2 = Frame(self.__root.tabControl, padding='5')
        self.__root.tab3 = Frame(self.__root.tabControl, padding='5')
        self.__root.tabControl.add(self.__root.tab1, text='Anmeldung')
        self.__root.tabControl.add(self.__root.tab2, text='Übersicht - Zeitnehmung')
        self.__root.tabControl.add(self.__root.tab3, text='Einstellungen')
        self.__root.tabControl.pack(expand=1, fill="both")
   
        # Tab Wettkampfgruppen
        self.config = IntVar()
        self.config.set(1)

        self.__root.Entry = Entry(self.__root.tab1, takefocus = 0)
        self.__root.Entry.pack(side='top', fill='x')
        self.__root.Entry.bind("<Return>", self.addWettkampfgruppe)
        self.var = StringVar(value=self.Wettkampfgruppen)
        self.__root.ListBox = Listbox(self.__root.tab1, listvariable=self.var, activestyle='none', selectmode=SINGLE, takefocus = 0)
        self.__root.ListBox.pack(expand=1, side='top', fill='both')
        self.__root.ListBox.bind("<Delete>", self.deleteWettkampfgruppe)
        self.__root.ListBox.bind('<<ListboxSelect>>', self.itemSelected)

        self.__root.setupBewerb = LabelFrame(self.__root.tab1, text="Bewerb Konfigration", borderwidth=1, relief=SOLID)
        self.__root.setupBewerb.pack(side='top', fill='x', padx='10', pady='10')
        self.__root.config1 = Radiobutton(self.__root.setupBewerb, text="GR:2x AF:1x VF:1x HB:1x KF:1x GF:2x", variable=self.config, value=1, takefocus=0)
        self.__root.config1.grid(row=0, column=0, sticky=(W), padx='10', pady='5')
        self.__root.config2 = Radiobutton(self.__root.setupBewerb, text="GR:2x VF:2x HB:2x KF:2x GF:2x", variable=self.config, value=2, takefocus=0)
        self.__root.config2.grid(row=1, column=0, sticky=(W), padx='10', pady='5')
        legende = "GR.....Grunddurchgang\nAF.....Achtelfinale(16)\nVF.....Viertelfinale(8)\nHF.....Halbfinale(4)\nKF.....Kleines Finale(2)\nAF.....Große Finale(2)\n1x.....1 Bahn\n2x.....Beide Bahnen"
        self.__root.configLegende = Label(self.__root.setupBewerb, text=legende, takefocus = 0)
        self.__root.configLegende.grid(row=0, column=1, rowspan=2, padx='10', pady='5')


        # Tab Zeitnehmung
        self.checked_Bahn_1 = BooleanVar()
        self.checked_Bahn_2 = BooleanVar()
        self.checked_Bahn_1.set(True)
        self.checked_Bahn_2.set(True)

        self.__root.dg = LabelFrame(self.__root.tab2, text="Durchgänge", borderwidth=1, relief=SOLID)
        self.__root.dg.pack(side='top', fill='both', padx='10')

        # Content automatisch erzeugen nach Anmeldungen erzeugen

        self.__root.test = Combobox(self.__root.dg, textvariable=StringVar(), state="readonly", takefocus = 0)
        self.__root.test.grid(row=0, column=0, pady='10', padx='10')

        self.__root.test2 = Combobox(self.__root.dg, textvariable=StringVar(), state="readonly", takefocus = 0)
        self.__root.test2.grid(row=1, column=0)

        self.__root.test3 = Combobox(self.__root.dg, textvariable=StringVar(), state="readonly", takefocus = 0)
        self.__root.test3.grid(row=2, column=0, pady='10')

        self.__root.test4= Combobox(self.__root.dg, textvariable=StringVar(), state="readonly", takefocus = 0)
        self.__root.test4.grid(row=3, column=0)


        self.__root.zeitnehmung = LabelFrame(self.__root.tab2, text="Aktueller Durchgang", borderwidth=1, relief=SOLID)
        self.__root.zeitnehmung.pack(side='left', padx='10')

        self.__root.BtnStart = Button(self.__root.zeitnehmung, text="Start", width=10, padding=10, command=self.start, takefocus = 0)
        self.__root.BtnStart.pack(side='left', padx='10', pady='10')
        self.__root.BtnAllesStop = Button(self.__root.zeitnehmung, text="Alles Stop", width=10, padding=10, command=self.allesStop, takefocus = 0, state=DISABLED)
        self.__root.BtnAllesStop.pack(side='left', pady='10')
        self.__root.BtnReset = Button(self.__root.zeitnehmung, text="Reset", width=10, padding=10, command=self.reset, takefocus = 0, state=DISABLED)
        self.__root.BtnReset.pack(side='right', padx='10', pady='10') 
        self.__root.BtnLoeschen = Button(self.__root.zeitnehmung, text="Löschen", width=10, padding=10, command=self.loeschen, takefocus = 0, state=DISABLED)
        self.__root.BtnLoeschen.pack(side='right', padx='10', pady='10')        
        self.__root.BtnWechsel = Button(self.__root.zeitnehmung, text="Bahn Wechsel", width=15, padding=10, command=self.bahnWechsel, takefocus = 0, state=DISABLED)
        self.__root.BtnWechsel.pack(side='right', padx='10', pady='10')

        self.__root.bahnen = LabelFrame(self.__root.tab2, text="Zeitnehmung", borderwidth=1, relief=SOLID)
        self.__root.bahnen.pack(side='left', padx='10')

        self.__root.CB1 = Checkbutton(self.__root.bahnen, text="Bahn 1", variable=self.checked_Bahn_1, command=self.switchBahn1State, takefocus = 0)
        self.__root.CB1.grid(row=0, column=0, padx='10')
        self.__root.G1 = Combobox(self.__root.bahnen, textvariable=StringVar(), state="readonly", takefocus = 0)
        self.__root.G1.bind('<<ComboboxSelected>>',self.updateGruppe1)
        self.__root.G1.grid(row=0, column=1, padx='10')
        self.__root.T1 = Label(self.__root.bahnen, text="00:00:00", font=("Helvetica", 20), takefocus = 0)
        self.__root.T1.grid(row=0, column=2, padx='10')
        self.__root.B1 = Button(self.__root.bahnen, text="Stop", width=10, command=self.stop_1, takefocus = 0)
        self.__root.B1.grid(row=0, column=3)

        self.__root.CB2 = Checkbutton(self.__root.bahnen, text="Bahn 2", variable=self.checked_Bahn_2, command=self.switchBahn2State, takefocus = 0)
        self.__root.CB2.grid(row=1, column=0, padx='10')
        self.__root.G2 = Combobox(self.__root.bahnen, textvariable=StringVar(), state="readonly", takefocus = 0)
        self.__root.G2.bind('<<ComboboxSelected>>',self.updateGruppe2)
        self.__root.G2.grid(row=1, column=1, padx='10')
        self.__root.T2 = Label(self.__root.bahnen, text="00:00:00", font=("Helvetica", 20), takefocus = 0)
        self.__root.T2.grid(row=1, column=2, padx='10')
        self.__root.B2 = Button(self.__root.bahnen, text="Stop", width=10, command=self.stop_2, takefocus = 0)
        self.__root.B2.grid(row=1, column=3)


        # Tab Einstellungen
        self.checked_Tastatur = BooleanVar()
        self.checked_GPIO = BooleanVar()
        self.checked_Rahmen = BooleanVar()
        self.checked_Konsole = BooleanVar()

        self.checked_Tastatur.set(True)
        self.checked_GPIO.set(False)
        self.checked_Rahmen.set(False)
        self.checked_Konsole.set(False)

        self.__root.setupEingabe = LabelFrame(self.__root.tab3, text="Eingabe", borderwidth=1, relief=SOLID)
        self.__root.setupEingabe.pack(side='top', fill='x', padx='10', pady='5')
        self.__root.CheckTastatur = Checkbutton(self.__root.setupEingabe, text="Tastatur", variable=self.checked_Tastatur, takefocus = 0)
        self.__root.CheckTastatur.grid(row=0, column=0, padx='10')
        self.__root.CheckGPIO = Checkbutton(self.__root.setupEingabe, text="GPIO", variable=self.checked_GPIO, takefocus = 0)
        self.__root.CheckGPIO.grid(row=0, column=1)
        self.__root.CheckRahmen = Checkbutton(self.__root.setupEingabe, text="Rahmen ausblenden", variable=self.checked_Rahmen, takefocus = 0, command=self.updateRahmenAnzeige)
        self.__root.CheckRahmen.grid(row=0, column=2, padx='10')
        self.__root.CheckKonsole = Checkbutton(self.__root.setupEingabe, text="Konsole", variable=self.checked_Konsole, takefocus = 0, command=self.switchKonsoleState)
        self.__root.CheckKonsole.grid(row=0, column=3)

        self.__root.setupTasten = LabelFrame(self.__root.tab3, text="Tasten", borderwidth=1, relief=SOLID)
        self.__root.setupTasten.pack(side='top', fill='x', padx='10', pady='5')
        self.__root.Start_Taste_1_Label = Label(self.__root.setupTasten, text="Start 1", takefocus = 0)
        self.__root.Start_Taste_1_Label.grid(row=0, column=0, padx='10', pady='10')
        self.__root.Start_Taste_1 = Entry(self.__root.setupTasten, width=3, takefocus = 0)
        self.__root.Start_Taste_1.grid(row=0, column=1, pady='10')
        self.__root.Stop_Taste_1_Label = Label(self.__root.setupTasten, text="Stop 1", takefocus = 0)
        self.__root.Stop_Taste_1_Label.grid(row=0, column=2, padx='10', pady='10')
        self.__root.Stop_Taste_1 = Entry(self.__root.setupTasten, width=3, takefocus = 0)
        self.__root.Stop_Taste_1.grid(row=0, column=3, pady='10')
        self.__root.Start_Taste_2_Label = Label(self.__root.setupTasten, text="Start 2", takefocus = 0)
        self.__root.Start_Taste_2_Label.grid(row=0, column=4, padx='10', pady='10')
        self.__root.Start_Taste_2 = Entry(self.__root.setupTasten, width=3, takefocus = 0)
        self.__root.Start_Taste_2.grid(row=0, column=5, pady='10')
        self.__root.Stop_Taste_2_Label = Label(self.__root.setupTasten, text="Stop 2", takefocus = 0)
        self.__root.Stop_Taste_2_Label.grid(row=0, column=6, padx='10',pady='10')
        self.__root.Stop_Taste_2 = Entry(self.__root.setupTasten, width=3, takefocus = 0)
        self.__root.Stop_Taste_2.grid(row=0, column=7, pady='10')

        self.__root.Start_Taste_1.insert(0, self.Taste_Start_1)
        self.__root.Stop_Taste_1.insert(0, self.Taste_Stop_1)
        self.__root.Start_Taste_2.insert(0, self.Taste_Start_2)
        self.__root.Stop_Taste_2.insert(0, self.Taste_Stop_2)

        self.__root.setupGPIO = LabelFrame(self.__root.tab3, text="GPIO", borderwidth=1, relief=SOLID)
        self.__root.setupGPIO.pack(side='top', fill='x', padx='10', pady='5')
        self.__root.Start_GPIO_1_Label = Label(self.__root.setupGPIO, text="Start 1", takefocus = 0)
        self.__root.Start_GPIO_1_Label.grid(row=0, column=0, padx='10', pady='10')
        self.__root.Start_GPIO_1 = Entry(self.__root.setupGPIO, width=3, takefocus = 0)
        self.__root.Start_GPIO_1.grid(row=0, column=1, pady='10')
        self.__root.Stop_GPIO_1_Label = Label(self.__root.setupGPIO, text="Stop 1", takefocus = 0)
        self.__root.Stop_GPIO_1_Label.grid(row=0, column=2, padx='10', pady='10')
        self.__root.Stop_GPIO_1 = Entry(self.__root.setupGPIO, width=3, takefocus = 0)
        self.__root.Stop_GPIO_1.grid(row=0, column=3, pady='10')
        self.__root.Start_GPIO_2_Label = Label(self.__root.setupGPIO, text="Start 2", takefocus = 0)
        self.__root.Start_GPIO_2_Label.grid(row=0, column=4, padx='10', pady='10')
        self.__root.Start_GPIO_2 = Entry(self.__root.setupGPIO, width=3, takefocus = 0)
        self.__root.Start_GPIO_2.grid(row=0, column=5, pady='10')
        self.__root.Stop_GPIO_2_Label = Label(self.__root.setupGPIO, text="Stop 2", takefocus = 0)
        self.__root.Stop_GPIO_2_Label.grid(row=0, column=6, padx='10',pady='10')
        self.__root.Stop_GPIO_2 = Entry(self.__root.setupGPIO, width=3, takefocus = 0)
        self.__root.Stop_GPIO_2.grid(row=0, column=7, pady='10')

        self.__root.Start_GPIO_1.insert(0, self.GPIO_Start_1)
        self.__root.Stop_GPIO_1.insert(0, self.GPIO_Stop_1)
        self.__root.Start_GPIO_2.insert(0, self.GPIO_Start_2)
        self.__root.Stop_GPIO_2.insert(0, self.GPIO_Stop_2)

        self.__root.setupStyle = LabelFrame(self.__root.tab3, text="Style", borderwidth=1, relief=SOLID)
        self.__root.setupStyle.pack(side='top', fill='x', padx='10', pady='5')
        self.__root.SGZL = Label(self.__root.setupStyle, text="Schriftgröße Zeit", takefocus = 0)
        self.__root.SGZL.grid(row=0, column=0, padx='10', pady='10')
        self.__root.SGZ = Spinbox(self.__root.setupStyle, width=3, from_=1, to=500, command=self.updateFontSizeZeit, takefocus = 0)
        self.__root.SGZ.grid(row=0, column=1, padx='10', pady='10')
        self.__root.SGZ.set(50)
        self.__root.SGGL = Label(self.__root.setupStyle, text="Schriftgröße Gruppe", takefocus = 0)
        self.__root.SGGL.grid(row=0, column=2, padx='10', pady='10')
        self.__root.SGG = Spinbox(self.__root.setupStyle, width=3, from_=1, to=500, command=self.updateFontSizeGruppe, takefocus = 0)
        self.__root.SGG.grid(row=0, column=3, padx='10', pady='10')
        self.__root.SGG.set(30)

        self.__root.Konsole = Label(self.__root, takefocus = 0, foreground='#8f8e8c')
        self.__root.Konsole.pack(expand=1, side='top', fill='both')

        self.showAnzeige()

    # Anzeigefenster
    def showAnzeige(self):
        self.anzeige = Toplevel()
        self.anzeige.title("KuppelStopper 3.0 Anzeige")
        self.anzeige.minsize(700, 400)

        self.icon = PhotoImage(file='Resources/Kuppelstopper.png')
        self.anzeige.iconphoto(False, self.icon)

        self.anzeige.frame = Frame(self.anzeige)
        self.anzeige.frame.pack(expand=1, side=TOP, fill=BOTH)

        self.anzeige.G1 = Label(self.anzeige.frame, text="", foreground='#818ef0', background='#6e6c6b', font=("Helvetica", self.__root.SGG.get()), takefocus=0)
        self.anzeige.Z1 = Label(self.anzeige.frame, text="00:00:00", anchor="center", foreground='#ffffff', background='#6e6c6b', font=("Helvetica", self.__root.SGZ.get()), takefocus=0)
        self.anzeige.Z2 = Label(self.anzeige.frame, text="00:00:00", anchor="center", foreground='#ffffff', background='#6e6c6b', font=("Helvetica", self.__root.SGZ.get()), takefocus=0)
        self.anzeige.G2 = Label(self.anzeige.frame, text="", anchor="ne", foreground='#93ff8f', background='#6e6c6b', font=("Helvetica", self.__root.SGG.get()), takefocus=0)
        
        self.anzeige.ERG = Label(self.anzeige.frame, text="Hier finden Sie später\ndie Auswertung!", anchor="center", justify="center", foreground='#ffffff', background='#6e6c6b', font=("Helvetica", self.__root.SGZ.get()), takefocus=0)
        self.anzeige.ERG.pack(expand=1, side=TOP, fill=BOTH)

        self.anzeige.mainloop()

    # Functions     
    def updateRahmenAnzeige(self):
        if self.checked_Rahmen.get() == True:
            self.anzeige.wm_overrideredirect(True) 
        else:
            self.anzeige.wm_overrideredirect(False) 

    def updateGruppe1(self, event=None):
        name = self.__root.G1.get()
        self.anzeige.G1.config(text=name)

    def updateGruppe2(self, event=None):
        name = self.__root.G2.get()
        self.anzeige.G2.config(text=name)

    def updateFontSizeZeit(self, event=None):
        size = self.__root.SGZ.get()
        self.anzeige.Z1.config(font=("Helvetica", size))
        self.anzeige.Z2.config(font=("Helvetica", size))
    
    def updateFontSizeGruppe(self, event=None):
        size = self.__root.SGG.get()
        self.anzeige.G1.config(font=("Helvetica", size))
        self.anzeige.G2.config(font=("Helvetica", size))

    def bahnWechsel(self):
        bahnA = self.__root.G1.get()
        bahnB = self.__root.G2.get()

        self.__root.G1.set(bahnB)
        self.__root.G2.set(bahnA)

        self.anzeige.G1.config(text=bahnB)
        self.anzeige.G2.config(text=bahnA)
        self.writeKonsole("Die Bahnen wurden gewechselt!")

    def allesStop(self):
        self.stop_1("")
        self.stop_2("")
        self.writeKonsole("Beide Zeiten mit Button angehalten!")

    def itemSelected(self, event=None):
        index = self.__root.ListBox.curselection()[0]
        name = self.Wettkampfgruppen[index]
        self.__root.Entry.delete(0, END)
        self.__root.Entry.insert(0, name)

    def addWettkampfgruppe(self, event=None):
        name = self.__root.Entry.get()
        self.Wettkampfgruppen.append(name)
        self.__root.Entry.delete(0, END)
        self.__root.Entry.insert(0, "")
        self.var.set(self.Wettkampfgruppen)
        self.__root.G1.config(values=self.Wettkampfgruppen)
        self.__root.G2.config(values=self.Wettkampfgruppen)
        self.writeKonsole(name + " wurde hinzugefügt!")

    def deleteWettkampfgruppe(self, event=None):
        index = self.__root.ListBox.curselection()[0]
        name = self.Wettkampfgruppen[index]
        self.Wettkampfgruppen.remove(name)
        self.var.set(self.Wettkampfgruppen)
        self.__root.G1.config(values=self.Wettkampfgruppen)
        self.__root.G2.config(values=self.Wettkampfgruppen)
        self.__root.Entry.delete(0, END)
        self.__root.Entry.insert(0, "")
        self.writeKonsole(name + " wurde gelöscht!")

    def switchBahn1State(self):
        if (self.checked_Bahn_1.get() == False):
            self.__root.G1["state"] = DISABLED
            self.__root.T1["state"] = DISABLED
            self.__root.B1["state"] = DISABLED
            self.writeKonsole("Bahn 1 wurde deaktiviert!")
        else:
            self.__root.G1["state"] = "readonly"
            self.__root.T1["state"] = NORMAL
            self.__root.B1["state"] = NORMAL
            self.writeKonsole("Bahn 1 wurde aktiviert!")

    def switchBahn2State(self):
        if (self.checked_Bahn_2.get() == False):
            self.__root.G2["state"] = DISABLED
            self.__root.T2["state"] = DISABLED
            self.__root.B2["state"] = DISABLED
            self.writeKonsole("Bahn 2 wurde deaktiviert!")
        else:
            self.__root.G2["state"] = "readonly"
            self.__root.T2["state"] = NORMAL
            self.__root.B2["state"] = NORMAL
            self.writeKonsole("Bahn 2 wurde aktiviert!")

    def startBuzzer1(self, event=None):
        if not self.time_is_running_1:
            if self.checked_GPIO.get() == True:
                self.BuzzerStopBahn1.when_pressed = self.stop_1
                if event == None:
                    self.writeKonsole("Zeit 1 mit Buzzer gestartet!")
            if self.checked_Tastatur.get() == True:
                self.__root.unbind(self.Taste_Start_1)
                self.__root.bind(self.Taste_Stop_1, self.stop_1)
                if event != None:
                    self.writeKonsole("Zeit 1 mit Taste '" + event.char + "' gestartet!")
            self.time_is_running_1 = True
            self.start_time_1 = time.time()
            self.update_time_1()

    def startBuzzer2(self, event=None):
        if not self.time_is_running_2:
            if self.checked_GPIO.get() == True:
                self.BuzzerStopBahn2.when_pressed = self.stop_2
                if event == None:
                    self.writeKonsole("Zeit 2 mit Buzzer gestartet!")
            if self.checked_Tastatur.get() == True:
                self.__root.unbind(self.Taste_Start_2)
                self.__root.bind(self.Taste_Stop_2, self.stop_2)
                if event != None:
                    self.writeKonsole("Zeit 2 mit Taste '" + event.char + "' gestartet!")
            self.time_is_running_2 = True
            self.start_time_2 = time.time()
            self.update_time_2()

    def start(self):   
        self.__root.BtnStart["state"] = DISABLED
        self.__root.BtnAllesStop["state"] = NORMAL
        self.__root.BtnWechsel["state"] = DISABLED
        self.__root.BtnLoeschen["state"] = DISABLED
        self.__root.BtnReset["state"] = DISABLED

        self.writeKonsole("Der Angriffbefehl wurde erteilt!")
        self.wechselAnsichtZurZeit()
        # os.system("mpg123 " + self.file_angriffbefehel)
        if self.checked_GPIO.get() == True:
            self.GPIO_Start_1 = self.__root.Start_GPIO_1.get()
            self.GPIO_Stop_1 = self.__root.Stop_GPIO_1.get()
            self.GPIO_Start_2 = self.__root.Start_GPIO_2.get()
            self.GPIO_Stop_2 = self.__root.Stop_GPIO_2.get()
            self.BuzzerStartBahn1 = GPIO_Button(self.GPIO_Start_1)
            self.BuzzerStopBahn1 = GPIO_Button(self.GPIO_Stop_1)
            self.BuzzerStartBahn2 = GPIO_Button(self.GPIO_Start_2)
            self.BuzzerStopBahn2 = GPIO_Button(self.GPIO_Stop_2)
            self.BuzzerStartBahn1.when_pressed = self.startBuzzer1
            self.BuzzerStartBahn2.when_pressed = self.startBuzzer2

        if self.checked_Tastatur.get() == True:
            self.Taste_Start_1 = self.__root.Start_Taste_1.get()
            self.Taste_Stop_1 = self.__root.Stop_Taste_1.get()
            self.Taste_Start_2 = self.__root.Start_Taste_2.get()
            self.Taste_Stop_2 = self.__root.Stop_Taste_2.get()

            self.__root.bind(self.Taste_Start_1, self.startBuzzer1)
            self.__root.bind(self.Taste_Start_2, self.startBuzzer2)

    def stop_1(self, event=None):
        self.time_is_running_1 = False
        if self.checked_Tastatur.get() == True:
            self.__root.unbind(self.Taste_Stop_1)
            if event != None and event != '':
                self.writeKonsole("Zeit 1 mit Taste '" + event.char + "' angehalten!")
        if self.checked_GPIO.get() == True and event == None:
            self.writeKonsole("Zeit 1 mit Buzzer bzw Button angehalten!")
        if self.time_is_running_1 == False and self.time_is_running_2 == False:
            self.__root.BtnAllesStop["state"] = DISABLED
            self.__root.BtnWechsel["state"] = NORMAL
            self.__root.BtnLoeschen["state"] = NORMAL
            self.__root.BtnReset["state"] = NORMAL

    def stop_2(self, event=None):
        self.time_is_running_2 = False
        if self.checked_Tastatur.get() == True:
            self.__root.unbind(self.Taste_Stop_2)
            if event != None and event != '':
                self.writeKonsole("Zeit 2 mit Taste '" + event.char + "' angehalten!")
        if self.checked_GPIO.get() == True and event == None:
            self.writeKonsole("Zeit 1 mit Buzzer bzw Button angehalten!")
        if self.time_is_running_1 == False and self.time_is_running_2 == False:
            self.__root.BtnAllesStop["state"] = DISABLED
            self.__root.BtnWechsel["state"] = NORMAL
            self.__root.BtnLoeschen["state"] = NORMAL
            self.__root.BtnReset["state"] = NORMAL

    def reset(self):
        self.__root.T1.config(text="00:00:00")
        self.__root.T2.config(text="00:00:00")
        self.anzeige.Z1.config(text="00:00:00")
        self.anzeige.Z2.config(text="00:00:00")
        self.__root.BtnStart["state"] = NORMAL
        self.__root.BtnReset["state"] = DISABLED
        self.writeKonsole("Zeit und Button zurückgesetzt!")
        self.wechselAnsichtZurAuswertung()
    
    def loeschen(self):
        self.__root.G1.set("")
        self.__root.G2.set("")
        self.anzeige.G1.config(text="")
        self.anzeige.G2.config(text="")
        # self.__root.BtnLoeschen["state"] = DISABLED
        self.writeKonsole("Gruppenauswahl gelöscht!")

    def update_time_1(self):
        if self.time_is_running_1:
            elapsed_time = time.time() - self.start_time_1
            dt = datetime.fromtimestamp(elapsed_time).strftime('%M:%S:%f')[:-4]
            self.__root.T1.config(text=dt)
            self.anzeige.Z1.config(text=dt)
            self.__root.T1.after(50, self.update_time_1)

    def update_time_2(self):
        if self.time_is_running_2:
            elapsed_time = time.time() - self.start_time_2
            dt = datetime.fromtimestamp(elapsed_time).strftime('%M:%S:%f')[:-4]
            self.__root.T2.config(text=dt)
            self.anzeige.Z2.config(text=dt)
            self.__root.T2.after(50, self.update_time_2)

    def switchKonsoleState(self):
        if (self.checked_Konsole.get() == False):
            self.__root.Konsole.config(text="")
        else:
            self.__root.Konsole.config(text="Konsole: ")

    def writeKonsole(self, text):
        if (self.checked_Konsole.get() == True):
            self.__root.Konsole.config(text="Konsole: " + text)

    def wechselAnsichtZurZeit(self):
        self.anzeige.ERG.pack_forget()
        self.anzeige.G1.pack(expand=0, side=TOP, fill=X)
        self.anzeige.Z1.pack(expand=1, side=TOP, fill=BOTH)
        self.anzeige.Z2.pack(expand=1, side=TOP, fill=BOTH)
        self.anzeige.G2.pack(expand=0, side=BOTTOM, fill=X)

    def wechselAnsichtZurAuswertung(self):
        self.anzeige.G1.pack_forget()
        self.anzeige.Z1.pack_forget()
        self.anzeige.Z2.pack_forget()
        self.anzeige.G2.pack_forget()
        self.anzeige.ERG.pack(expand=1, side=TOP, fill=BOTH)

Hauptfenster()

