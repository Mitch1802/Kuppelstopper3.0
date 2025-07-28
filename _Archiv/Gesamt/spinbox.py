from customtkinter import CTkFrame, CTkButton, CTkEntry, CENTER

class IntSpinbox(CTkFrame):
    def __init__(self, *args, width: int = 100, height: int = 32, step_size: int = 1, command=None, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.step_size = step_size
        self.command = command

        self.configure(fg_color='transparent')
        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.subtract_button = CTkButton(self, text="-", width=height-6, height=height-6, corner_radius=0, command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3,0), pady=3)

        self.entry = CTkEntry(self, width=width-(2*height), height=height-6, border_width=0, corner_radius=0, justify=CENTER)
        self.entry.grid(row=0, column=1, padx=3, pady=3, sticky="ew")

        self.add_button = CTkButton(self, text="+", width=height-6, height=height-6, corner_radius=0, command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0,3), pady=3)

        self.entry.insert(0, "0")

    def add_button_callback(self):
        if self.command:
            self.command()
        try:
            value = int(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            pass

    def subtract_button_callback(self):
        if self.command:
            self.command()
        try:
            value = int(self.entry.get()) - self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            pass

    def get(self):
        try:
            return int(self.entry.get())
        except ValueError:
            return None

    def set(self, value: int):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(int(value)))
