from __future__ import annotations

from typing import Callable, Dict, Optional

from .models import LAYERS_TOP_DOWN, Mission, SimulationResult, SimulationState


def _wrap_payload(layer: str, payload: str) -> Dict[str, str]:
    if layer == "Application":
        return {"Type": "Application Data", "Data": payload}
    if layer == "Presentation":
        return {"Type": "Presentation Data", "Transform": "Encoding/Compression/Encryption", "Payload": payload}
    if layer == "Session":
        return {"Type": "Session Data", "State": "ESTABLISHED", "Payload": payload}
    if layer == "Transport":
        return {"Type": "Transport Segment", "Source Port": "50000", "Destination Port": "443", "Payload": payload}
    if layer == "Network":
        return {"Type": "IP Packet", "Source IP": "192.168.1.10", "Destination IP": "192.168.1.25", "Payload": payload}
    if layer == "Data Link":
        return {
            "Type": "Ethernet Frame",
            "Source MAC": "AA:BB:CC:11:22:33",
            "Destination MAC": "AA:BB:CC:44:55:66",
            "FCS": "0x1A2B",
            "Payload": payload,
        }
    return {"Type": "Bits", "Bitstream": "101101001011010010101...", "Payload": payload}


SelectionProvider = Callable[[str, Dict[str, str], str], str]


def simulate_mission(
    mission: Mission,
    selection_provider: Optional[SelectionProvider] = None,
    predefined_selections: Optional[Dict[str, str]] = None,
) -> SimulationResult:
    state = SimulationState(mission=mission)
    payload = mission.payload

    for layer in LAYERS_TOP_DOWN:
        state.add_log(f"→ {layer} layer processing")
        decision = mission.decisions.get(layer)
        if decision:
            if predefined_selections and layer in predefined_selections:
                selected = predefined_selections[layer]
            elif selection_provider:
                selected = selection_provider(layer, decision.options, decision.correct_option)
            else:
                selected = decision.correct_option

            state.selected_options[layer] = selected

            if selected != decision.correct_option:
                error = f"⚠ Layer {layer} problem detected: {decision.error_message}"
                state.errors.append(error)
                state.add_log(error)
                state.add_log(f"✓ {layer} configuration repaired")
                state.selected_options[layer] = decision.correct_option
            else:
                state.add_log(f"✓ {layer} configuration accepted")

        wrapped = _wrap_payload(layer, payload)
        state.record_layer_object(layer, wrapped)
        payload = f"{wrapped['Type']} -> {payload}"
        state.add_log(f"✓ Encapsulation updated at {layer}")

    state.add_log("✓ Physical transmission started")
    state.add_log("✓ Data moved through simulated network path")

    for layer in reversed(LAYERS_TOP_DOWN):
        state.add_log(f"✓ Decapsulation at {layer}")

    state.add_log("✓ Mission completed")

    return SimulationResult(
        mission=mission,
        success=True,
        event_log=state.event_log,
        layer_objects=state.layer_objects,
        selected_options=state.selected_options,
        errors=state.errors,
    )
