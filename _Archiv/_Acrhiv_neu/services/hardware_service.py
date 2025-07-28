import sys

class HardwareService:
    def __init__(self, start_pin: int, end_pin: int, enable_hw: bool):
        """
        Verwaltet GPIO-Interaktionen. Wenn enable_hw False oder gpiozero nicht verfügbar,
        wird is_enabled auf False gesetzt und man arbeitet per Tastatur.
        """
        self.start_pin = start_pin
        self.end_pin = end_pin
        self.enable_hw = enable_hw
        self.is_enabled = False  # neu: Standardmäßig deaktiviert

        if enable_hw:
            try:
                from gpiozero import Button, Buzzer
                # Buttons/Buzzer nur anlegen, wenn gpiozero verfügbar ist
                self.start_button = Button(self.start_pin)
                self.end_buzzer = Buzzer(self.end_pin)
                self.is_enabled = True
            except (ImportError, RuntimeError) as e:
                print("GPIO disabled oder nicht verfügbar. Verwende Tastatursteuerung.", file=sys.stderr)
                self.is_enabled = False

    def wait_for_start_button(self):
        """Blockierend auf den Startknopf warten."""
        if not self.is_enabled:
            return
        self.start_button.wait_for_press()

    def wait_for_end_buzzer(self):
        """Blockierend auf den Endbuzzer warten."""
        if not self.is_enabled:
            return
        # Hier je nach Hardware anpassen, z.B. .wait_for_press() oder .wait_for_release()
        self.end_buzzer.wait_for_press()