
import time, datetime
from gpiozero import Button as GPIO_Button
from threading import Thread

class ZeitManager:
    """Verwaltet Zeitnhemung, start, stopp, bahnwechsel."""
    def __init__(self):
        self.zeit_uebertragen = False
        self.time_is_running_1 = False
        self.start_time_1 = ''
        self.stop_time_1 = ''
        self.id_time_1 = ''
        self.time_is_running_2 = False
        self.start_time_2 = ''
        self.stop_time_2 = ''
        self.id_time_2 = ''

    def start(self):
        if self.checked_GPIO.get() == True and self.checked_Bahn_1.get() == True:
            self.GPIO_Start_1 = self.__root.Start_GPIO_1.get()
            self.GPIO_Stop_1 = self.__root.Stop_GPIO_1.get()
            self.BuzzerStartBahn1.when_pressed = self.startBuzzer1

        if self.checked_GPIO.get() == True and self.checked_Bahn_2.get() == True:
            self.GPIO_Start_2 = self.__root.Start_GPIO_2.get()
            self.GPIO_Stop_2 = self.__root.Stop_GPIO_2.get()
            self.BuzzerStartBahn2.when_pressed = self.startBuzzer2

        if self.checked_Tastatur.get() == True and self.checked_Bahn_1.get() == True:
            self.Taste_Start_1 = self.__root.Start_Taste_1.get()
            self.Taste_Stop_1 = self.__root.Stop_Taste_1.get()
            self.__root.bind(self.Taste_Start_1, self.startBuzzer1)
        
        if self.checked_Tastatur.get() == True and self.checked_Bahn_2.get() == True:
            self.Taste_Start_2 = self.__root.Start_Taste_2.get()
            self.Taste_Stop_2 = self.__root.Stop_Taste_2.get()
            self.__root.bind(self.Taste_Start_2, self.startBuzzer2)
        
        t = Thread(target=self.playSound, args=[self.FileAngriffsbefehl])
        t.start()

    def start_buzzer1(self):
        pass
        # if not self.time_is_running_1:
        #     if self.checked_GPIO.get() == True:
        #         self.BuzzerStopBahn1.when_pressed = self.stop_1
        #         if event == None:
        #             self.writeKonsole('Zeit 1 mit Buzzer gestartet!')
        #     if self.checked_Tastatur.get() == True:
        #         self.__root.unbind(self.Taste_Start_1)
        #         self.__root.bind(self.Taste_Stop_1, self.stop_1)
        #         if event != None:
        #             self.writeKonsole('Zeit 1 mit Taste ' + event.char + ' gestartet!')
        #     self.time_is_running_1 = True
        #     self.start_time_1 = time.time()
        #     self.update_time_1()

    def start_buzzer2(self):
        pass
        # if not self.time_is_running_2:
        #     if self.checked_GPIO.get() == True:
        #         self.BuzzerStopBahn2.when_pressed = self.stop_2
        #         if event == None:
        #             self.writeKonsole('Zeit 2 mit Buzzer gestartet!')
        #     if self.checked_Tastatur.get() == True:
        #         self.__root.unbind(self.Taste_Start_2)
        #         self.__root.bind(self.Taste_Stop_2, self.stop_2)
        #         if event != None:
        #             self.writeKonsole('Zeit 2 mit Taste ' + event.char + ' gestartet!')
        #     self.time_is_running_2 = True
        #     self.start_time_2 = time.time()
        #     self.update_time_2()

    def alles_stop(self):
        pass
        # self.stop_1('')
        # self.stop_2('')
        # self.writeKonsole('Beide Zeiten mit Button angehalten!')

    def stop1(self):
        pass
        # self.time_is_running_1 = False
        # t = Thread(target=self.playSound, args=[self.FileStopp])
        # t.start()
        # if self.checked_Tastatur.get() == True:
        #     self.__root.unbind(self.Taste_Stop_1)
        #     if event != None and event != '':
        #         self.writeKonsole('Zeit 1 mit Taste ' + event.char + ' angehalten!')
        # if self.checked_GPIO.get() == True and event == None:
        #     self.writeKonsole('Zeit 1 mit Buzzer bzw Button angehalten!')
        # if self.time_is_running_1 == False and self.time_is_running_2 == False:
        #     self.__root.BtnAllesStop['state'] = DISABLED
        #     self.__root.BtnWechsel['state'] = NORMAL
        #     self.__root.BtnAnsichtWechseln['state'] = NORMAL
        #     self.__root.BtnZeitUebertragen['state'] = NORMAL
        #     self.__root.BtnStopReset ['state'] = NORMAL


    def stop2(self, event=None):
        pass
        # self.time_is_running_2 = False
        # t = Thread(target=self.playSound, args=[self.FileStopp])
        # t.start()
        # if self.checked_Tastatur.get() == True:
        #     self.__root.unbind(self.Taste_Stop_2)
        #     if event != None and event != '':
        #         self.writeKonsole('Zeit 2 mit Taste ' + event.char + ' angehalten!')
        # if self.checked_GPIO.get() == True and event == None:
        #     self.writeKonsole('Zeit 1 mit Buzzer bzw Button angehalten!')
        # if self.time_is_running_1 == False and self.time_is_running_2 == False:
        #     self.__root.BtnAllesStop['state'] = DISABLED
        #     self.__root.BtnWechsel['state'] = NORMAL
        #     self.__root.BtnAnsichtWechseln['state'] = NORMAL
        #     self.__root.BtnZeitUebertragen['state'] = NORMAL
        #     self.__root.BtnStopReset ['state'] = NORMAL

    def update_time_1(self):
        if self.time_is_running_1:
            elapsed_time = time.time() - self.start_time_1
            dt = datetime.fromtimestamp(elapsed_time).strftime('%M:%S:%f')[:-4]
            self.__root.T1.config(text=dt)
            self.anzeige.Z1.config(text=dt)
            self.__root.T1.after(50, self.update_time_1)
        else:
            self.stop_time_1 = time.time()

    def update_time_2(self):
        if self.time_is_running_2:
            elapsed_time = time.time() - self.start_time_2
            dt = datetime.fromtimestamp(elapsed_time).strftime('%M:%S:%f')[:-4]
            self.__root.T2.config(text=dt)
            self.anzeige.Z2.config(text=dt)
            self.__root.T2.after(50, self.update_time_2)
        else:
            self.stop_time_2 = time.time()

    def stop_reset(self):
        pass
        self.time_is_running_1 = False
        self.time_is_running_2 = False
        self.reset()






