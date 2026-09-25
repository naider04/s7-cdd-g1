"""
OSI Communication Simulator
===========================
Interactive Educational Network Communication & Troubleshooting Simulator
based on the 7-Layer OSI Model.

Author: Antigravity DeepMind Pair Programming
"""

import tkinter as tk
from tkinter import ttk
import sys
import theme
from missions import get_mission_by_id
from gui.mission_select import MissionSelectView
from gui.simulator_view import SimulatorView


class OsiSimulatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Simulador de Comunicación OSI - Laboratorio Educativo Interactivo")
        self.root.geometry("1240x720")
        self.root.minsize(1020, 700)
        self.root.configure(bg=theme.BG_DARK)

        # Configure ttk dark styling
        self._configure_ttk_styles()

        # View container
        self.container = tk.Frame(self.root, bg=theme.BG_DARK)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.current_view: Optional[tk.Widget] = None
        self.active_simulator_view: Optional[SimulatorView] = None

        # Global Keyboard Shortcuts
        self.root.bind("<Return>", self._on_return_key)

        # Show mission selector screen on launch
        self.show_mission_select()

    def _configure_ttk_styles(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Progressbar style
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor=theme.BG_DARK,
            background=theme.COLOR_SUCCESS,
            bordercolor=theme.BORDER,
            lightcolor=theme.COLOR_SUCCESS,
            darkcolor=theme.COLOR_SUCCESS
        )

        # Notebook style
        style.configure(
            "TNotebook",
            background=theme.BG_PANEL,
            bordercolor=theme.BORDER,
            tabmargins=[2, 5, 2, 0]
        )
        style.configure(
            "TNotebook.Tab",
            background=theme.BG_CARD,
            foreground=theme.TEXT_SECONDARY,
            padding=[12, 4],
            font=theme.FONT_SMALL
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", theme.BG_DARK)],
            foreground=[("selected", theme.TEXT_ACCENT)]
        )

        # Combobox style
        style.configure(
            "TCombobox",
            fieldbackground=theme.BG_INPUT,
            background=theme.BG_CARD,
            foreground=theme.TEXT_PRIMARY,
            bordercolor=theme.BORDER,
            arrowcolor=theme.TEXT_ACCENT
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", theme.BG_INPUT)],
            foreground=[("readonly", theme.TEXT_PRIMARY)]
        )

    def show_mission_select(self):
        """Display the mission selection menu."""
        self._clear_view()
        self.active_simulator_view = None
        select_view = MissionSelectView(self.container, on_select_mission=self.launch_mission)
        select_view.pack(fill=tk.BOTH, expand=True)
        self.current_view = select_view

    def launch_mission(self, mission_id: int):
        """Instantiate and display simulator view for the chosen mission."""
        self._clear_view()
        mission = get_mission_by_id(mission_id)
        sim_view = SimulatorView(self.container, mission=mission, on_back=self.show_mission_select)
        sim_view.pack(fill=tk.BOTH, expand=True)
        self.current_view = sim_view
        self.active_simulator_view = sim_view

    def _clear_view(self):
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None

    def _on_return_key(self, event):
        if self.active_simulator_view:
            self.active_simulator_view._on_submit_decision()


def main():
    root = tk.Tk()
    app = OsiSimulatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
