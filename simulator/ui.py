from __future__ import annotations

from typing import Dict

from .engine import simulate_mission
from .models import LAYERS_TOP_DOWN, Mission


def _print_topology() -> None:
    print("\n👤 PERSON A (Sender)                👤 PERSON B (Receiver)")
    print("L7→L6→L5→L4→L3→L2→L1     NETWORK     L1→L2→L3→L4→L5→L6→L7")


def _print_layer_stack(title: str) -> None:
    print(f"\n{title}")
    for layer in LAYERS_TOP_DOWN:
        print(f"- {layer}")


def _print_object(layer: str, obj: Dict[str, str]) -> None:
    print(f"\nCURRENT OBJECT @ {layer}")
    for key, value in obj.items():
        print(f"{key}: {value}")


def _interactive_selector(layer: str, options: Dict[str, str], default: str) -> str:
    print(f"\nLayer: {layer}")
    keys = list(options.keys())
    for idx, key in enumerate(keys, start=1):
        print(f"  {idx}. {key} - {options[key]}")
    raw = input(f"Choose option [default {default}]: ").strip()
    if not raw:
        return default
    if raw.isdigit() and 1 <= int(raw) <= len(keys):
        return keys[int(raw) - 1]
    if raw in options:
        return raw
    print("Invalid choice, using default.")
    return default


def run_mission(mission: Mission) -> None:
    _print_topology()
    _print_layer_stack("\nOSI Layers")
    print(f"\nMission: {mission.icon} {mission.name}")
    print(mission.description)
    print(f"Payload: {mission.payload}")

    result = simulate_mission(mission, selection_provider=_interactive_selector)

    if result.errors:
        print("\nDetected issues and automatic repair guidance:")
        for err in result.errors:
            print(err)

    print("\nPacket/Frame Inspector")
    for layer in LAYERS_TOP_DOWN:
        _print_object(layer, result.layer_objects[layer])

    print("\nEVENT LOG")
    for entry in result.event_log:
        print(entry)

    print("\n✓ COMMUNICATION COMPLETE")
