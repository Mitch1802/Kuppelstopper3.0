import time
from datetime import datetime
from threading import Thread
from customtkinter import *
import events, utils

def start(self, event=None):   
    self.ZeitUebertragen = False
    self.Buzzer1DarfStarten = True
    self.Buzzer2DarfStarten = True
    self.root.BtnStart.configure(state=DISABLED)
    self.root.BtnAllesStop.configure(state=NORMAL)
    self.root.BtnWechsel.configure(state=DISABLED)
    self.root.BtnAnsichtWechseln.configure(state=DISABLED)
    self.root.BtnZeitUebertragen.configure(state=DISABLED)
    self.root.BtnStopReset.configure(state=NORMAL)
    events.change_color_from_button_summary()

    if self.checked_GPIO.get() == True and self.checked_Bahn_1.get() == True:
        self.GPIO_Start_1 = self.root.Start_GPIO_1.get()
        self.GPIO_Stop_1 = self.root.Stop_GPIO_1.get()
        self.BuzzerStartBahn1.when_pressed = self.startBuzzer1

    if self.checked_GPIO.get() == True and self.checked_Bahn_2.get() == True:
        self.GPIO_Start_2 = self.root.Start_GPIO_2.get()
        self.GPIO_Stop_2 = self.root.Stop_GPIO_2.get()
        self.BuzzerStartBahn2.when_pressed = self.startBuzzer2

    if self.checked_Tastatur.get() == True and self.checked_Bahn_1.get() == True:
        self.Taste_Start_1 = self.root.Start_Taste_1.get()
        self.Taste_Stop_1 = self.root.Stop_Taste_1.get()
        self.root.bind(self.Taste_Start_1, self.startBuzzer1)
    
    if self.checked_Tastatur.get() == True and self.checked_Bahn_2.get() == True:
        self.Taste_Start_2 = self.root.Start_Taste_2.get()
        self.Taste_Stop_2 = self.root.Stop_Taste_2.get()
        self.root.bind(self.Taste_Start_2, self.startBuzzer2)
    
    t = Thread(target=self.playSound, args=[self.FileAngriffsbefehl])
    t.start()

def start_buzzer_1(self, event=None):
    if not self.time_is_running_1 and self.Buzzer1DarfStarten == True:
        if self.checked_GPIO.get() == True:
            self.BuzzerStopBahn1.when_pressed = stop_1()
            if event == None:
                utils.write_konsole(self, 'Zeit 1 mit Buzzer gestartet!')
        if self.checked_Tastatur.get() == True:
            self.root.unbind(self.Taste_Start_1)
            self.root.bind(self.Taste_Stop_1, stop_1)
            if event != None:
                utils.write_konsole(self, 'Zeit 1 mit Taste ' + event.char + ' gestartet!')
        self.time_is_running_1 = True
        self.start_time_1 = time.time()
        update_time_1()

def start_buzzer_2(self, event=None):
    if not self.time_is_running_2 and self.Buzzer2DarfStarten == True:
        if self.checked_GPIO.get() == True:
            self.BuzzerStopBahn2.when_pressed = stop_2()
            if event == None:
                utils.write_konsole(self, 'Zeit 2 mit Buzzer gestartet!')
        if self.checked_Tastatur.get() == True:
            self.root.unbind(self.Taste_Start_2)
            self.root.bind(self.Taste_Stop_2, stop_2)
            if event != None:
                utils.write_konsole(self, 'Zeit 2 mit Taste ' + event.char + ' gestartet!')
        self.time_is_running_2 = True
        self.start_time_2 = time.time()
        update_time_2()

def alles_stop(self):
    stop_1('')
    stop_2('')
    utils.write_konsole(self, 'Beide Zeiten mit CTkButton angehalten!')

def stop_1(self, event=None):
    self.time_is_running_1 = False
    self.Buzzer1DarfStarten = False
    t = Thread(target=self.playSound, args=[self.FileStopp])
    t.start()
    if self.checked_Tastatur.get() == True:
        self.root.unbind(self.Taste_Stop_1)
        if event != None and event != '':
            utils.write_konsole(self, 'Zeit 1 mit Taste ' + event.char + ' angehalten!')
    if self.checked_GPIO.get() == True and event == None:
        utils.write_konsole(self, 'Zeit 1 mit Buzzer bzw CTkButton angehalten!')
    if self.time_is_running_1 == False and self.time_is_running_2 == False:
        self.root.BtnAllesStop.configure(state=DISABLED)
        self.root.BtnWechsel.configure(state=NORMAL)
        self.root.BtnAnsichtWechseln.configure(state=NORMAL)
        self.root.BtnZeitUebertragen.configure(state=NORMAL)
        self.root.BtnStopReset .configure(state=NORMAL)
        self.changeColorFromButtonSummary()

def stop_2(self, event=None):
    self.time_is_running_2 = False
    self.Buzzer2DarfStarten = False
    t = Thread(target=self.playSound, args=[self.FileStopp])
    t.start()
    if self.checked_Tastatur.get() == True:
        self.root.unbind(self.Taste_Stop_2)
        if event != None and event != '':
            utils.writeKonsole('Zeit 2 mit Taste ' + event.char + ' angehalten!')
    if self.checked_GPIO.get() == True and event == None:
        utils.write_konsole(self, 'Zeit 1 mit Buzzer bzw CTkButton angehalten!')
    if self.time_is_running_1 == False and self.time_is_running_2 == False:
        self.root.BtnAllesStop.configure(state=DISABLED)
        self.root.BtnWechsel.configure(state=NORMAL)
        self.root.BtnAnsichtWechseln.configure(state=NORMAL)
        self.root.BtnZeitUebertragen.configure(state=NORMAL)
        self.root.BtnStopReset .configure(state=NORMAL)
        events.change_color_from_button_summary(self)

def stop_reset(self):
    self.time_is_running_1 = False
    self.time_is_running_2 = False
    reset()

def reset(self):
    self.root.T1.configure(text='00:00:00')
    self.root.T2.configure(text='00:00:00')
    self.anzeige.Z1.configure(text='00:00:00')
    self.anzeige.Z2.configure(text='00:00:00')
    self.root.BtnStart.configure(state=NORMAL)
    
    events.change_color_from_button_summary(self)

def update_time_1(self):
    if self.time_is_running_1:
        elapsed_time = time.time() - self.start_time_1
        dt = datetime.fromtimestamp(elapsed_time).strftime('%M:%S:%f')[:-4]
        self.root.T1.configure(text=dt)
        self.anzeige.Z1.configure(text=dt)
        self.root.T1.after(50, update_time_1(self))
    else:
        self.stop_time_1 = time.time()

def update_time_2(self):
    if self.time_is_running_2:
        elapsed_time = time.time() - self.start_time_2
        dt = datetime.fromtimestamp(elapsed_time).strftime('%M:%S:%f')[:-4]
        self.root.T2.configure(text=dt)
        self.anzeige.Z2.configure(text=dt)
        self.root.T2.after(50, update_time_2(self))
    else:
        self.stop_time_2 = time.time()

def zeit_1_loeschen(self):
    dg_select = self.__root.CBDG.get()

    for dg in self.Durchgänge:
        if dg['dg'] == int(dg_select):
            dg['zeit1'] = ''
            dg['fehler1'] = 0
            dg['zeit2'] = ''
            dg['fehler2'] = 0
            dg['bestzeit'] = ''
            dg['platzierung'] = 0
            events.zeichne_neue_werte(dg['row'], dg['column']+1, '', dg['row'], dg['column'], dg['typ'])
            events.zeichne_neue_werte(dg['row'], dg['column']+2, '', dg['row'], dg['column'], dg['typ'])
            events.zeichne_neue_werte(dg['row'], dg['column']+3, '', dg['row'], dg['column'], dg['typ'])
            events.zeichne_neue_werte(dg['row'], dg['column']+4, '', dg['row'], dg['column'], dg['typ'])
    
    events.bestzeit_platzierung_berechnen()

def zeit_2_loeschen(self):
    dg_select = self.__root.CBDG.get()

    for dg in self.Durchgänge:
        if dg['dg'] == int(dg_select):
            dg['zeit2'] = ''
            dg['fehler2'] = 0
            events.zeichne_neue_werte(dg['row'], dg['column']+2, '', dg['row'], dg['column'], dg['typ'])
            if dg['zeit1'] != '':
                dg['bestzeit'] = dg['zeit1']
                dg['fehlerbest'] = dg['fehler1']
                text = str(dg['bestzeit'])
                if dg['fehlerbest'] > 0:
                    text += ' +' + str(dg['fehlerbest'])
                events.zeichne_neue_werte(dg['row'], dg['column']+3, text, dg['row'], dg['column'], dg['typ'])
            else:
                dg['bestzeit'] = ''
                dg['fehlerbest'] = 0
                dg['platzierung'] = 0
                events.zeichne_neue_werte(dg['row'], dg['column']+3, '', dg['row'], dg['column'], dg['typ'])
                events.zeichne_neue_werte(dg['row'], dg['column']+4, '', dg['row'], dg['column'], dg['typ'])
    
    events.bestzeit_platzierung_berechnen()

