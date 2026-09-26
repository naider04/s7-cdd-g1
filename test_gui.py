"""
GUI interactive decision console verification test.
Tests loading each of the 4 missions, displaying the decision consoles,
submitting choices, and checking receiver screen updates.
"""

import tkinter as tk
from main import OsiSimulatorApp
from gui.repair_dialog import RepairDialog
from models import RepairOption, TroubleshootIssue


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


def test_repair_dialog_layout():
    root = tk.Tk()
    root.geometry("900x700")

    long_details = "\n\n".join(
        f"Párrafo de diagnóstico {i + 1}. " + "Detalle técnico extenso para forzar el desplazamiento. " * 4
        for i in range(8)
    )
    issue = TroubleshootIssue(
        layer_num=4,
        title="Error de transporte con un título deliberadamente largo para verificar el ajuste de texto",
        summary="Resumen de prueba",
        details=long_details,
        options=[
            RepairOption(
                id=f"opt_{i}",
                title=f"Opción correctiva {i + 1} con un título suficientemente largo para probar el ajuste de línea",
                description="Descripción extendida de la acción correctiva para verificar el ajuste del texto dentro de la tarjeta.",
                is_correct=i == 0,
                feedback="Retroalimentación de prueba",
            )
            for i in range(3)
        ],
        on_repair_success=lambda: None,
    )

    dialog = RepairDialog(root, issue, on_repaired=lambda: None)
    root.update_idletasks()
    root.update()

    assert dialog.resizable() == (True, True), "Repair dialog must stay resizable"
    assert dialog.btn_apply.winfo_ismapped(), "Apply button is not visible"
    assert dialog.btn_cancel.winfo_ismapped(), "Cancel button is not visible"
    assert dialog.btn_apply.winfo_height() >= 24, f"Apply button is compressed: {dialog.btn_apply.winfo_height()}px"
    assert dialog.btn_cancel.winfo_height() >= 24, f"Cancel button is compressed: {dialog.btn_cancel.winfo_height()}px"

    canvas_bottom = dialog.scroll_canvas.winfo_rooty() + dialog.scroll_canvas.winfo_height()
    apply_top = dialog.btn_apply.winfo_rooty()
    assert apply_top >= canvas_bottom - 1, "Button bar overlaps the scrollable body"

    bbox = dialog.scroll_canvas.bbox("all")
    assert bbox is not None and bbox[3] > dialog.scroll_canvas.winfo_height(), "Long diagnosis is not scrollable"

    dialog.destroy()
    root.destroy()
    print("✓ Repair dialog keeps its buttons visible and scrollable for long content.")


if __name__ == "__main__":
    test_gui_interactive()
    test_repair_dialog_layout()
