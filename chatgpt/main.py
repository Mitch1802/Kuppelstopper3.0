# main.py
import os
import customtkinter as ctk
import logging
from config import ConfigManager
from gui import GUIManager
from data import DataManager


class KuppelstopperApp:
    def __init__(self):
        self.config = ConfigManager()
        self.data = DataManager(self.config)

        self.app = ctk.CTk()
        self.app.title(self.config.title)
        self.app.geometry("1400x800")
        self.app.minsize(1000, 700)

        self.gui = GUIManager(self.app, self.config, self.data)

    def run(self):
        self.app.mainloop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = KuppelstopperApp()
    app.run()
