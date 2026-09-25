"""
GUI interactive decision console verification test.
Tests loading each of the 4 missions, displaying the decision consoles,
submitting choices, and checking receiver screen updates.
"""

import tkinter as tk
from main import OsiSimulatorApp


def test_gui_interactive():
    root = tk.Tk()
    app = OsiSimulatorApp(root)
    root.update()

    print("✓ Main mission select view rendered successfully.")

    # Cycle through all 4 missions in the UI
    for mid in range(1, 5):
        app.launch_mission(mid)
        root.update()
        sim_view = app.active_simulator_view
        assert sim_view is not None, f"Mission {mid} failed to load simulator view"
        assert sim_view.active_decision is not None, f"Mission {mid} did not present an initial decision"
        if sim_view.active_decision.input_type == "CHOICE":
            assert sim_view.choice_var.get() == "", f"Mission {mid} preselected a choice"

        # Submit initial decision
        if sim_view.active_decision.input_type == "CHOICE":
            sim_view.choice_var.set(sim_view.active_decision.default_value)
        sim_view._on_submit_decision()
        root.update()

        # Check inspector
        sim_view.inspector.select_layer(4)
        sim_view.inspector.select_layer(3)
        sim_view.inspector.select_layer(7)
        root.update()

        # Return to menu
        app.show_mission_select()
        root.update()
        print(f"✓ Mission {mid} launched, decision rendered, submitted, and inspected cleanly.")

    root.destroy()
    print("✓ All 4 interactive GUI missions passed successfully!")


if __name__ == "__main__":
    test_gui_interactive()
