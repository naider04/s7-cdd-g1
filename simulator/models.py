from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

LAYERS_TOP_DOWN = [
    "Application",
    "Presentation",
    "Session",
    "Transport",
    "Network",
    "Data Link",
    "Physical",
]


@dataclass(frozen=True)
class LayerDecision:
    layer: str
    question: str
    options: Dict[str, str]
    correct_option: str
    error_message: str
    repair_hint: str


@dataclass(frozen=True)
class Mission:
    mission_id: int
    name: str
    icon: str
    description: str
    payload: str
    decisions: Dict[str, LayerDecision] = field(default_factory=dict)


@dataclass
class SimulationResult:
    mission: Mission
    success: bool
    event_log: List[str]
    layer_objects: Dict[str, Dict[str, str]]
    selected_options: Dict[str, str]
    errors: List[str]


@dataclass
class SimulationState:
    mission: Mission
    selected_options: Dict[str, str] = field(default_factory=dict)
    layer_objects: Dict[str, Dict[str, str]] = field(default_factory=dict)
    event_log: List[str] = field(default_factory=lambda: ["✓ Mission started"])
    errors: List[str] = field(default_factory=list)

    def add_log(self, message: str) -> None:
        self.event_log.append(message)

    def record_layer_object(self, layer: str, obj: Dict[str, str]) -> None:
        self.layer_objects[layer] = obj

    def current_object(self, layer: str) -> Optional[Dict[str, str]]:
        return self.layer_objects.get(layer)
