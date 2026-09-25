try:
    import tkinter as tk
    from tkinter import ttk
except ModuleNotFoundError:  # pragma: no cover - environment-specific
    tk = None
    ttk = None

from missions import all_missions
from simulator.engine import simulate_mission
from simulator.models import Mission
from simulator.ui import format_result


class OSISimulatorApp:
    def __init__(self, root) -> None:
        if tk is None or ttk is None:  # pragma: no cover - environment-specific
            raise RuntimeError("Tkinter is not available in this Python environment.")
        self.root = root
        self.root.title("OSI Communication Simulator")
        self.root.geometry("1150x700")

        self.missions = all_missions()
        self.completed = set()
        self.selected_mission: Mission | None = None
        self.decision_vars: dict[str, tk.StringVar] = {}
        self.mission_buttons: dict[int, ttk.Button] = {}

        self._build_layout()
        self._refresh_missions()

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        mission_frame = ttk.LabelFrame(self.root, text="Select a mission")
        mission_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        mission_frame.columnconfigure(0, weight=1)
        self.mission_frame = mission_frame

        detail_frame = ttk.Frame(self.root)
        detail_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(3, weight=1)

        self.title_label = ttk.Label(detail_frame, text="Choose a mission", font=("TkDefaultFont", 14, "bold"))
        self.title_label.grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.description_label = ttk.Label(detail_frame, text="", wraplength=700)
        self.description_label.grid(row=1, column=0, sticky="w")

        self.controls_frame = ttk.LabelFrame(detail_frame, text="Layer controls")
        self.controls_frame.grid(row=2, column=0, sticky="ew", pady=10)
        self.controls_frame.columnconfigure(1, weight=1)

        self.run_button = ttk.Button(detail_frame, text="Run mission", command=self._run_selected, state=tk.DISABLED)
        self.run_button.grid(row=2, column=0, sticky="e", pady=(0, 10))

        self.output = tk.Text(detail_frame, wrap="word")
        self.output.grid(row=3, column=0, sticky="nsew")
        self.output.configure(state=tk.DISABLED)

    def _refresh_missions(self) -> None:
        for widget in self.mission_frame.winfo_children():
            widget.destroy()

        for idx, mission in enumerate(self.missions):
            status = "✓" if mission.mission_id in self.completed else " "
            text = f"[{status}] {mission.mission_id}. {mission.icon} {mission.name}"
            button = ttk.Button(self.mission_frame, text=text, command=lambda m=mission: self._select_mission(m))
            button.grid(row=idx, column=0, sticky="ew", padx=6, pady=4)
            self.mission_buttons[mission.mission_id] = button

    def _select_mission(self, mission: Mission) -> None:
        self.selected_mission = mission
        self.title_label.config(text=f"{mission.icon} {mission.name}")
        self.description_label.config(text=f"{mission.description}\nPayload: {mission.payload}")
        self.run_button.config(state=tk.NORMAL)
        self._render_decision_controls()

    def _render_decision_controls(self) -> None:
        for widget in self.controls_frame.winfo_children():
            widget.destroy()

        self.decision_vars.clear()
        if not self.selected_mission:
            return

        if not self.selected_mission.decisions:
            ttk.Label(self.controls_frame, text="This mission has no configurable decisions.").grid(
                row=0, column=0, sticky="w", padx=6, pady=6
            )
            return

        for row, (layer, decision) in enumerate(self.selected_mission.decisions.items()):
            ttk.Label(self.controls_frame, text=f"{layer}:").grid(row=row, column=0, sticky="w", padx=6, pady=4)
            var = tk.StringVar(value=decision.correct_option)
            self.decision_vars[layer] = var
            combo = ttk.Combobox(
                self.controls_frame,
                textvariable=var,
                values=list(decision.options.keys()),
                state="readonly",
            )
            combo.grid(row=row, column=1, sticky="ew", padx=6, pady=4)

    def _run_selected(self) -> None:
        if not self.selected_mission:
            return

        selections = {layer: var.get() for layer, var in self.decision_vars.items()}
        result = simulate_mission(self.selected_mission, predefined_selections=selections)
        self.completed.add(self.selected_mission.mission_id)
        self._refresh_missions()
        self._set_output(format_result(result))

    def _set_output(self, text: str) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)
        self.output.configure(state=tk.DISABLED)


def main() -> None:
    if tk is None:  # pragma: no cover - environment-specific
        raise SystemExit("Tkinter is required to run this app. Install python3-tk.")
    root = tk.Tk()
    app = OSISimulatorApp(root)
    _ = app
    root.mainloop()


if __name__ == "__main__":
    main()
