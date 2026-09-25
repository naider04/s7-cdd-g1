from __future__ import annotations

from .models import LAYERS_TOP_DOWN, SimulationResult


def format_result(result: SimulationResult) -> str:
    lines = []
    lines.append("👤 PERSON A (Sender)                👤 PERSON B (Receiver)")
    lines.append("L7→L6→L5→L4→L3→L2→L1     NETWORK     L1→L2→L3→L4→L5→L6→L7")
    lines.append("")
    lines.append(f"Mission: {result.mission.icon} {result.mission.name}")
    lines.append(result.mission.description)
    lines.append(f"Payload: {result.mission.payload}")
    lines.append("")

    if result.errors:
        lines.append("Detected issues and repairs (🔧):")
        for err in result.errors:
            lines.append(err)
        lines.append("")

    lines.append("Packet/Frame Inspector")
    for layer in LAYERS_TOP_DOWN:
        lines.append("")
        lines.append(f"CURRENT OBJECT @ {layer}")
        for key, value in result.layer_objects[layer].items():
            lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("EVENT LOG")
    lines.extend(result.event_log)
    lines.append("")
    lines.append("✓ COMMUNICATION COMPLETE")
    return "\n".join(lines)
