"""
Base Mission class for all OSI Communication Simulator missions.
Provides the interactive decision-driven lifecycle, layer progression hooks,
troubleshooting handling, and inspector data bindings.
"""

import tkinter as tk
from typing import Dict, Any, List, Optional, Callable
from models import LayerStatus, PacketInspectorData, TroubleshootIssue, StageDecision, LogEvent
from utils.helpers import get_timestamp


class BaseMission:
    def __init__(self, mission_id: int, title: str, icon: str, subtitle: str, objective: str, concepts: List[str]):
        self.mission_id = mission_id
        self.title = title
        self.icon = icon
        self.subtitle = subtitle
        self.objective = objective
        self.concepts = concepts

        # Callbacks hooked up by SimulatorView
        self.cb_update_layer: Optional[Callable[[str, int, LayerStatus, str, bool], None]] = None
        self.cb_log: Optional[Callable[[str, str, str, Optional[int]], None]] = None
        self.cb_network_animate: Optional[Callable[[str, str, str, str, bool, Optional[Callable]], None]] = None
        self.cb_trigger_troubleshoot: Optional[Callable[[TroubleshootIssue], None]] = None
        self.cb_mission_complete: Optional[Callable[[Dict[str, Any]], None]] = None
        self.cb_inspector_update: Optional[Callable[[], None]] = None
        self.cb_output_update: Optional[Callable[[], None]] = None
        self.cb_decision_ready: Optional[Callable[[StageDecision], None]] = None

        # Execution state
        self.is_running = False
        self.is_paused = False
        self.current_phase = "DECISION"  # DECISION, ANIMATING, COMPLETE, ERROR
        self.current_layer = 7
        self.current_side = "sender"  # "sender", "network", "receiver"
        self.active_issue: Optional[TroubleshootIssue] = None
        self.current_stage_index = 0
        self.stages: List[StageDecision] = []

        # Current dissected packet data
        self.inspector_data = PacketInspectorData()

        # Stats
        self.packets_sent = 0
        self.packets_received = 0
        self.packets_lost = 0
        self.decisions_made = 0
        self.errors_repaired = 0

    def set_callbacks(
        self,
        update_layer: Callable[[str, int, LayerStatus, str, bool], None],
        log: Callable[[str, str, str, Optional[int]], None],
        network_animate: Callable[[str, str, str, str, bool, Optional[Callable]], None],
        trigger_troubleshoot: Callable[[TroubleshootIssue], None],
        mission_complete: Callable[[Dict[str, Any]], None],
        inspector_update: Callable[[], None],
        output_update: Callable[[], None],
        decision_ready: Callable[[StageDecision], None],
    ):
        self.cb_update_layer = update_layer
        self.cb_log = log
        self.cb_network_animate = network_animate
        self.cb_trigger_troubleshoot = trigger_troubleshoot
        self.cb_mission_complete = mission_complete
        self.cb_inspector_update = inspector_update
        self.cb_output_update = output_update
        self.cb_decision_ready = decision_ready

    def log(self, level: str, icon: str, message: str, layer_num: Optional[int] = None):
        """Append to common event log."""
        if self.cb_log:
            self.cb_log(level, icon, message, layer_num)

    def update_layer(self, side: str, layer_num: int, status: LayerStatus, text: str, has_error: bool = False):
        """Update visual state of a layer card on sender or receiver stack."""
        if self.cb_update_layer:
            self.cb_update_layer(side, layer_num, status, text, has_error)

    def trigger_error(self, issue: TroubleshootIssue):
        """Raise an interactive troubleshooting error."""
        self.active_issue = issue
        self.is_paused = True
        self.current_phase = "ERROR"
        self.update_layer(
            "sender" if self.current_side == "sender" else "receiver",
            issue.layer_num,
            LayerStatus.ERROR,
            f"ERROR: {issue.title}",
            has_error=True
        )
        self.log("ERROR", "⚠", f"Consequence at Layer {issue.layer_num} ({issue.title}): {issue.summary}", issue.layer_num)
        if self.cb_trigger_troubleshoot:
            self.cb_trigger_troubleshoot(issue)

    def resolve_current_error(self):
        """Called when user successfully repairs an issue via the repair dialog."""
        if not self.active_issue:
            return
        layer_num = self.active_issue.layer_num
        self.errors_repaired += 1
        side = "sender" if self.current_side == "sender" else "receiver"
        self.update_layer(side, layer_num, LayerStatus.COMPLETE, "Repaired & Verified", has_error=False)
        self.log("SUCCESS", "✓", f"Layer {layer_num} repaired! Resuming mission...", layer_num)

        callback = self.active_issue.on_repair_success
        self.active_issue = None
        self.is_paused = False
        self.current_phase = "DECISION"

        if callback:
            callback()

    def complete_mission(self, summary_data: Dict[str, Any]):
        """Mark mission as completed and show summary."""
        self.current_phase = "COMPLETE"
        self.is_running = False
        self.log("SUCCESS", "✓", "Communication completed successfully! All layers traversed with user decisions.", None)
        if self.cb_mission_complete:
            self.cb_mission_complete(summary_data)

    def notify_inspector(self):
        """Notify inspector widget that packet data has updated."""
        if self.cb_inspector_update:
            self.cb_inspector_update()

    def notify_output(self):
        """Notify custom visual output panel to refresh."""
        if self.cb_output_update:
            self.cb_output_update()

    def notify_decision(self, decision: StageDecision):
        """Prompt UI to display interactive decision challenge."""
        if self.cb_decision_ready:
            self.cb_decision_ready(decision)

    def start_mission(self):
        """Start mission by presenting the very first interactive challenge."""
        self.reset_state()
        self.is_running = True
        self.is_paused = False
        self.log("INFO", "✓", f"Mission started: {self.title}", None)
        self.load_initial_stage()

    def load_initial_stage(self):
        """Subclasses populate stages and call self.present_current_stage()."""
        pass

    def present_current_stage(self):
        if self.current_stage_index < len(self.stages):
            decision = self.stages[self.current_stage_index]
            self.current_layer = decision.layer_num
            self.notify_decision(decision)
        else:
            self.is_running = False

    def submit_user_decision(self, user_value: str, extra_data: Optional[Dict[str, Any]] = None):
        """Override in subclasses to process user decision and handle consequences."""
        self.decisions_made += 1

    def build_visual_output_ui(self, parent: tk.Widget):
        """Override to build real-time visual output panel (Browser, Chat, Video, etc.)."""
        pass

    def reset_state(self):
        """Reset mission counters and states."""
        self.is_running = False
        self.is_paused = False
        self.current_phase = "DECISION"
        self.current_layer = 7
        self.current_side = "sender"
        self.active_issue = None
        self.current_stage_index = 0
        self.stages = []
        self.packets_sent = 0
        self.packets_received = 0
        self.packets_lost = 0
        self.decisions_made = 0
        self.errors_repaired = 0
