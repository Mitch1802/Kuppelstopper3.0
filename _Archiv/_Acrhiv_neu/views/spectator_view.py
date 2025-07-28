from views.base_view import BaseView
from controllers.spectator_controller import SpectatorController
from tkinter import ttk

class SpectatorView(BaseView):
    def __init__(self, controller: SpectatorController):
        self.controller = controller
        super().__init__("Kuppelcup Zuschauer")

    def _setup_ui(self):
        self.tree = ttk.Treeview(self.root, columns=("Gruppe","Bahn","Zeit"), show='headings')
        self.tree.heading("Gruppe", text="Gruppe")
        self.tree.heading("Bahn", text="Bahn")
        self.tree.heading("Zeit", text="Bestzeit")
        self.tree.pack(expand=True, fill='both')
        self._refresh()

    def _refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        bests = self.controller.get_best_for_all()
        for (gid,lane), attempt in bests.items():
            self.tree.insert('', 'end', values=(attempt.group.name, lane, f"{attempt.penalized_time:.2f}s"))
        self.root.after(1000, self._refresh)