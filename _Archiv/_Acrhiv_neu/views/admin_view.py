# views/admin_view.py

import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Notebook, Frame, LabelFrame, Label, Entry, Checkbutton, Button, Combobox
from views.base_view import BaseView

class AdminView(BaseView):
    def _setup_ui(self):
        # Fenstergröße
        self.root.geometry('1600x1000')

        # Notebook mit Tabs
        self.notebook = Notebook(self.root)
        self.tab_registration = Frame(self.notebook)
        self.tab_runs         = Frame(self.notebook)
        self.tab_settings     = Frame(self.notebook)
        self.notebook.add(self.tab_registration, text='Anmeldung')
        self.notebook.add(self.tab_runs,         text='Übersicht – Zeitnehmung')
        self.notebook.add(self.tab_settings,     text='Einstellungen')
        self.notebook.pack(expand=1, fill='both')

        # Einzelne Tabs aufbauen
        self._setup_registration_tab()
        self._setup_runs_tab()
        self._setup_settings_tab()

    def _setup_registration_tab(self):
        fr = LabelFrame(self.tab_registration, text='Anmeldung Wettkampfgruppen', padding=10)
        fr.pack(side='top', fill='x', padx=10, pady=10)

        # Gruppenname
        Label(fr, text='Gruppenname:').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_group = Entry(fr)
        self.entry_group.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.entry_group.bind('<Return>', lambda e: self._on_add_group())

        # Damengruppe
        self.female_var = tk.BooleanVar()
        Checkbutton(fr, text='Damengruppe', variable=self.female_var)\
            .grid(row=1, column=0, sticky='w', padx=5)

        # Hinzufügen
        Button(fr, text='Gruppe hinzufügen', command=self._on_add_group)\
            .grid(row=1, column=1, sticky='e', padx=5, pady=5)

        # Listbox
        self.listbox_groups = tk.Listbox(fr, height=10)
        self.listbox_groups.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=5, pady=(5,0))
        self.listbox_groups.bind('<<ListboxSelect>>', self._on_group_select)

        # Lösch- und Toggle-Buttons
        btn_frame = Frame(fr)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky='e', pady=5)
        Button(btn_frame, text='Löschen', command=self._on_delete_group).pack(side='right', padx=2)
        Button(btn_frame, text='Toggle Damenwertung', command=self._on_toggle_damen).pack(side='right', padx=2)

        # Lade initial
        self._update_group_list()

    def _setup_runs_tab(self):
        # Steuerung der Durchgänge
        ctrl_fr = LabelFrame(self.tab_runs, text='Durchgang wählen', padding=10)
        ctrl_fr.pack(fill='x', padx=10, pady=10)

        Button(ctrl_fr, text='⟨ Vorheriger', command=self.controller.prev_run)\
            .grid(row=0, column=0, padx=5)
        self.run_var = tk.StringVar()
        self.combo_runs = Combobox(ctrl_fr,
                                   textvariable=self.run_var,
                                   values=self.controller.get_run_numbers(),
                                   state='readonly',
                                   width=5)
        self.combo_runs.grid(row=0, column=1, padx=5)
        self.combo_runs.bind('<<ComboboxSelected>>', lambda e: self.controller.select_run(int(self.run_var.get())))
        Button(ctrl_fr, text='Nächster ⟩', command=self.controller.next_run)\
            .grid(row=0, column=2, padx=5)

        # Aktionen: Start, Stop, Wechsel, Zeit übertragen
        action_fr = Frame(self.tab_runs, padding=10)
        action_fr.pack(fill='x', padx=10, pady=(0,10))

        Label(action_fr, text='Fehler:').grid(row=0, column=0, padx=5)
        self.err_var = tk.StringVar(value='0')
        Entry(action_fr, textvariable=self.err_var, width=3)\
            .grid(row=0, column=1, padx=5)

        Button(action_fr, text='Start',   command=self.controller.start_run)\
            .grid(row=0, column=2, padx=5)
        Button(action_fr, text='Stop',    command=lambda: self.controller.end_run(errors=int(self.err_var.get())))\
            .grid(row=0, column=3, padx=5)
        Button(action_fr, text='Bahn Wechsel',    command=self.controller.switch_lanes)\
            .grid(row=0, column=4, padx=5)
        Button(action_fr, text='Zeit übertragen', command=self.controller.transfer_times)\
            .grid(row=0, column=5, padx=5)

        # Zeitnehmung Frame mit zwei Bahnen
        tm_fr = LabelFrame(self.tab_runs, text='Zeitnehmung', padding=10)
        tm_fr.pack(fill='both', expand=1, padx=10, pady=10)

        # Bahn 1
        self.lane1_var = tk.BooleanVar()
        Checkbutton(tm_fr, text='Bahn 1', variable=self.lane1_var,
                    command=lambda: self._toggle_lane(1))\
            .grid(row=0, column=0, padx=5, pady=5)
        self.group1_lbl = Label(tm_fr, text='...', width=20, anchor='w')
        self.group1_lbl.grid(row=0, column=1, padx=5)
        self.time1_lbl  = Label(tm_fr, text='00:00:00', width=10, anchor='e')
        self.time1_lbl.grid(row=0, column=2, padx=5)
        self.err1_entry = Entry(tm_fr, width=3)
        self.err1_entry.grid(row=0, column=3, padx=5)
        self.stop1_btn  = Button(tm_fr, text='Stop 1',
                                 state='disabled',
                                 command=lambda: self.controller.end_run(errors=int(self.err1_entry.get())))
        self.stop1_btn.grid(row=0, column=4, padx=5)

        # Bahn 2
        self.lane2_var = tk.BooleanVar()
        Checkbutton(tm_fr, text='Bahn 2', variable=self.lane2_var,
                    command=lambda: self._toggle_lane(2))\
            .grid(row=1, column=0, padx=5, pady=5)
        self.group2_lbl = Label(tm_fr, text='...', width=20, anchor='w')
        self.group2_lbl.grid(row=1, column=1, padx=5)
        self.time2_lbl  = Label(tm_fr, text='00:00:00', width=10, anchor='e')
        self.time2_lbl.grid(row=1, column=2, padx=5)
        self.err2_entry = Entry(tm_fr, width=3)
        self.err2_entry.grid(row=1, column=3, padx=5)
        self.stop2_btn  = Button(tm_fr, text='Stop 2',
                                 state='disabled',
                                 command=lambda: self.controller.end_run(errors=int(self.err2_entry.get())))
        self.stop2_btn.grid(row=1, column=4, padx=5)

    def _setup_settings_tab(self):
        fr = LabelFrame(self.tab_settings, text='Einstellungen', padding=10)
        fr.pack(fill='x', padx=10, pady=10)

        # Eingabe-Modus
        self.keyboard_var = tk.BooleanVar(value=True)
        Checkbutton(fr, text='Tastatursteuerung', variable=self.keyboard_var,
                    command=lambda: self.controller.toggle_keyboard(self.keyboard_var.get()))\
            .grid(row=0, column=0, padx=5, pady=5)
        self.gpio_var = tk.BooleanVar(value=self.controller.hardware.is_enabled)
        Checkbutton(fr, text='GPIO-Steuerung', variable=self.gpio_var,
                    command=lambda: self.controller.toggle_gpio(self.gpio_var.get()))\
            .grid(row=0, column=1, padx=5, pady=5)

        # Anzeige-Optionen
        self.frame_var   = tk.BooleanVar(value=False)
        self.console_var = tk.BooleanVar(value=True)
        Checkbutton(fr, text='Rahmen ausblenden', variable=self.frame_var,
                    command=lambda: self.controller.toggle_frame(self.frame_var.get()))\
            .grid(row=1, column=0, padx=5, pady=5)
        Checkbutton(fr, text='Konsole', variable=self.console_var,
                    command=lambda: self.controller.toggle_console(self.console_var.get()))\
            .grid(row=1, column=1, padx=5, pady=5)

        # Tastenbelegung
        key_fr = LabelFrame(self.tab_settings, text='Tastenbelegung', padding=10)
        key_fr.pack(fill='x', padx=10, pady=(0,10))

        Label(key_fr, text='Start Bahn 1').grid(row=0, column=0, padx=5, pady=5)
        self.key_start1 = Entry(key_fr, width=3)
        self.key_start1.insert(0, self.controller.settings.get('start_key', 's'))
        self.key_start1.grid(row=0, column=1, padx=5, pady=5)

        Label(key_fr, text='Stop Bahn 1').grid(row=0, column=2, padx=5, pady=5)
        self.key_stop1 = Entry(key_fr, width=3)
        self.key_stop1.insert(0, self.controller.settings.get('stop_key', 'e'))
        self.key_stop1.grid(row=0, column=3, padx=5, pady=5)

        Label(key_fr, text='Start Bahn 2').grid(row=1, column=0, padx=5, pady=5)
        self.key_start2 = Entry(key_fr, width=3)
        self.key_start2.insert(0, self.controller.settings.get('start2_key', 'x'))
        self.key_start2.grid(row=1, column=1, padx=5, pady=5)

        Label(key_fr, text='Stop Bahn 2').grid(row=1, column=2, padx=5, pady=5)
        self.key_stop2 = Entry(key_fr, width=3)
        self.key_stop2.insert(0, self.controller.settings.get('stop2_key', 'y'))
        self.key_stop2.grid(row=1, column=3, padx=5, pady=5)

        Button(key_fr, text='Speichern', command=self._on_save_keys)\
            .grid(row=2, column=3, sticky='e', padx=5, pady=10)

    # ---- Callbacks Registration ----

    def _on_add_group(self):
        name = self.entry_group.get().strip()
        if not name:
            messagebox.showerror('Fehler', 'Bitte einen Namen eingeben!')
            return
        try:
            self.controller.add_group(name, self.female_var.get())
        except Exception as e:
            messagebox.showerror('Fehler', str(e))
            return
        self.entry_group.delete(0, tk.END)
        self.female_var.set(False)
        self._update_group_list()

    def _update_group_list(self):
        self.listbox_groups.delete(0, tk.END)
        for g in self.controller.groups:
            label = f"{g['gruppenname']} ({'D' if g['damenwertung'] else 'H'})"
            self.listbox_groups.insert(tk.END, label)

    def _on_group_select(self, event):
        sel = self.listbox_groups.curselection()
        if sel:
            self.controller.select_group(sel[0])

    def _on_delete_group(self):
        sel = self.listbox_groups.curselection()
        if not sel:
            return
        name = self.controller.groups[sel[0]]['gruppenname']
        self.controller.delete_group(name)
        self._update_group_list()

    def _on_toggle_damen(self):
        sel = self.listbox_groups.curselection()
        if not sel:
            return
        name = self.controller.groups[sel[0]]['gruppenname']
        self.controller.toggle_damenwertung(name)
        self._update_group_list()

    # ---- Callbacks Runs ----

    def _toggle_lane(self, lane: int):
        if lane == 1:
            on = self.lane1_var.get()
            self.controller.toggle_lane(1, on)
            self.stop1_btn['state'] = 'normal' if on else 'disabled'
        else:
            on = self.lane2_var.get()
            self.controller.toggle_lane(2, on)
            self.stop2_btn['state'] = 'normal' if on else 'disabled'

    # ---- Callbacks Settings ----

    def _on_save_keys(self):
        k1 = self.key_start1.get().strip()
        s1 = self.key_stop1.get().strip()
        k2 = self.key_start2.get().strip()
        s2 = self.key_stop2.get().strip()
        self.controller.update_key_binding(1, 'start', k1)
        self.controller.update_key_binding(1, 'stop', s1)
        self.controller.update_key_binding(2, 'start', k2)
        self.controller.update_key_binding(2, 'stop', s2)
        messagebox.showinfo('Einstellungen', 'Tastenbelegung gespeichert!')
