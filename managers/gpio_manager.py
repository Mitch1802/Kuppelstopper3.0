class GpioManager:
    """Optional: GPIO-Buttons für Start/Stop global & je Bahn."""
    def __init__(self, pins, handlers):
        self.enabled = False
        self.buttons = {}
        try:
            from gpiozero import Button
            self.enabled = True
            for key, pin in pins.items():
                if pin is None:
                    self.buttons[key] = None
                    continue
                b = Button(pin, pull_up=True, bounce_time=0.02)
                self.buttons[key] = b
                cb = handlers.get(key)
                if cb:
                    b.when_pressed = cb
        except Exception:
            self.enabled = False
            self.buttons = {}

    def close(self):
        for b in self.buttons.values():
            try:
                if b:
                    b.close()
            except Exception:
                pass
        self.buttons.clear()