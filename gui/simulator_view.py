"""
Main Simulator View for the OSI Communication Simulator.
Decision-Driven Interface: Removes passive auto-play and requires active user choices,
configurations, and typed inputs at each OSI layer, displaying immediate network consequences.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable
import theme
from models import LayerStatus, TroubleshootIssue, StageDecision
from missions.base_mission import BaseMission
from gui.osi_stack_widget import OsiStackWidget
from gui.network_canvas import NetworkCanvas
from gui.inspector_widget import InspectorWidget
from gui.event_log_widget import EventLogWidget
from gui.repair_dialog import RepairDialog
from gui.completion_dialog import CompletionDialog


class SimulatorView(tk.Frame):
    def __init__(self, parent: tk.Widget, mission: BaseMission, on_back: Callable[[], None]):
        super().__init__(parent, bg=theme.BG_DARK)
        self.mission = mission
        self.on_back = on_back

        # Active decision state
        self.active_decision: Optional[StageDecision] = None
        self.choice_var = tk.StringVar()
        self.entry_var = tk.StringVar()

        # Build sub-components
        self._build_top_bar()
        self._build_main_stacks_and_network()
        self._build_bottom_panels()

        # Connect callbacks
        self.mission.set_callbacks(
            update_layer=self.handle_layer_update,
            log=self.handle_log,
            network_animate=self.handle_network_animate,
            trigger_troubleshoot=self.handle_troubleshoot,
            mission_complete=self.handle_complete,
            inspector_update=self.handle_inspector_update,
            output_update=self.handle_output_update,
            decision_ready=self.handle_decision_ready
        )

        # Initial inspector update
        self.inspector.update_data(self.mission.inspector_data)

        # Start the interactive mission immediately!
        self.mission.start_mission()

    def _build_top_bar(self):
        top = tk.Frame(self, bg=theme.BG_PANEL, padx=14, pady=6, bd=1, relief=tk.SOLID)
        top.pack(fill=tk.X)

        # Back button
        btn_back = tk.Button(
            top,
            text="← Missions Menu",
            font=theme.FONT_SMALL,
            bg=theme.BG_CARD,
            fg=theme.TEXT_PRIMARY,
            activebackground=theme.BG_CARD_HOVER,
            activeforeground="#ffffff",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._handle_back_click
        )
        btn_back.pack(side=tk.LEFT, padx=(0, 14))

        # Title & Subtitle
        title_box = tk.Frame(top, bg=theme.BG_PANEL)
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box,
            text=f"{self.mission.icon} Mission #{self.mission.mission_id}: {self.mission.title}",
            font=theme.FONT_TITLE,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_PANEL
        ).pack(anchor=tk.W)

        tk.Label(
            title_box,
            text=self.mission.subtitle,
            font=theme.FONT_TINY,
            fg=theme.TEXT_ACCENT,
            bg=theme.BG_PANEL
        ).pack(anchor=tk.W)

        # Right Action & Status
        ctrls = tk.Frame(top, bg=theme.BG_PANEL)
        ctrls.pack(side=tk.RIGHT)

        self.lbl_progress = tk.Label(
            ctrls,
            text="Interactive Decision Mode: Active",
            font=theme.FONT_SMALL,
            fg=theme.COLOR_SUCCESS,
            bg=theme.BG_PANEL
        )
        self.lbl_progress.pack(side=tk.LEFT, padx=(0, 15))

        btn_reset = tk.Button(
            ctrls,
            text="↺ Restart Mission",
            font=theme.FONT_SMALL,
            bg=theme.BG_CARD,
            fg=theme.TEXT_MUTED,
            activebackground=theme.BG_CARD_HOVER,
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.reset_simulation
        )
        btn_reset.pack(side=tk.LEFT)

    def _build_main_stacks_and_network(self):
        middle = tk.Frame(self, bg=theme.BG_DARK, padx=8, pady=4)
        middle.pack(fill=tk.BOTH, expand=True)

        # Left: Person A (Sender) OSI Stack
        self.sender_stack = OsiStackWidget(
            middle,
            title="👤 PERSON A",
            subtitle="SENDER",
            is_sender=True,
            on_layer_select=self.on_layer_selected_by_user,
            on_repair_trigger=self.on_wrench_clicked
        )
        self.sender_stack.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        # Center: Animated Network Topology Canvas
        center_frame = tk.Frame(middle, bg=theme.BG_DARK)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.net_canvas = NetworkCanvas(center_frame)
        self.net_canvas.pack(fill=tk.BOTH, expand=True)

        # Right: Person B (Receiver) OSI Stack
        self.receiver_stack = OsiStackWidget(
            middle,
            title="👤 PERSON B",
            subtitle="RECEIVER",
            is_sender=False,
            on_layer_select=self.on_layer_selected_by_user,
            on_repair_trigger=self.on_wrench_clicked
        )
        self.receiver_stack.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 0))

    def _build_bottom_panels(self):
        bottom = tk.Frame(self, bg=theme.BG_PANEL, bd=1, relief=tk.SOLID, height=310)
        bottom.pack(fill=tk.X, padx=8, pady=(0, 6))
        bottom.pack_propagate(False)

        notebook = ttk.Notebook(bottom)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Interactive Decision Console & Visual Output
        tab_interactive = tk.Frame(notebook, bg=theme.BG_PANEL)
        notebook.add(tab_interactive, text="  🎮 Interactive Decision Console & Live Output  ")

        paned = tk.PanedWindow(tab_interactive, orient=tk.HORIZONTAL, bg=theme.BORDER, bd=0, sashwidth=4)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left: Interactive Decision Console Frame
        self.decision_frame = tk.Frame(paned, bg=theme.BG_CARD, padx=12, pady=10)
        paned.add(self.decision_frame, minsize=420, stretch="always")

        self.decision_action_frame = tk.Frame(self.decision_frame, bg=theme.BG_CARD)
        self.decision_action_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))

        self.decision_body_frame = tk.Frame(self.decision_frame, bg=theme.BG_CARD)
        self.decision_body_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.decision_scrollbar = tk.Scrollbar(
            self.decision_body_frame,
            orient=tk.VERTICAL,
            width=12,
            bd=0,
            highlightthickness=0,
            bg=theme.BG_INPUT,
            troughcolor=theme.BG_PANEL,
            activebackground=theme.TEXT_MUTED
        )
        self.decision_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.decision_canvas = tk.Canvas(
            self.decision_body_frame,
            bg=theme.BG_CARD,
            bd=0,
            highlightthickness=0
        )
        self.decision_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.decision_scrollbar.config(command=self.decision_canvas.yview)

        self.decision_content = tk.Frame(self.decision_canvas, bg=theme.BG_CARD)
        self.decision_scroll_window = self.decision_canvas.create_window(
            (0, 0),
            window=self.decision_content,
            anchor=tk.NW
        )
        self.decision_content.bind("<Configure>", self._sync_decision_scrollregion)
        self.decision_canvas.bind("<Configure>", self._resize_decision_content)

        # Right: Mission Visual Output Frame (Browser, Video, Reassembly, etc.)
        self.output_frame = tk.Frame(paned, bg=theme.BG_PANEL)
        paned.add(self.output_frame, minsize=380, stretch="always")

        self.mission.build_visual_output_ui(self.output_frame)

        # Tab 2: Deep Packet Inspector
        self.inspector = InspectorWidget(notebook)
        notebook.add(self.inspector, text="  🔍 Deep Packet Inspector  ")

        # Tab 3: Chronological Event Log
        self.event_log = EventLogWidget(notebook)
        notebook.add(self.event_log, text="  📋 Event Log  ")

        # Tab 4: OSI Reference Guide
        tab_guide = tk.Frame(notebook, bg=theme.BG_CARD, padx=14, pady=10)
        notebook.add(tab_guide, text="  📖 OSI 7-Layer Reference  ")
        self._build_osi_guide(tab_guide)

    def _sync_decision_scrollregion(self, _event=None):
        self.decision_canvas.configure(scrollregion=self.decision_canvas.bbox("all"))

    def _resize_decision_content(self, event):
        self.decision_canvas.itemconfigure(self.decision_scroll_window, width=event.width)

    def _scroll_decision(self, event):
        if event.num == 4:
            direction = -1
        elif event.num == 5:
            direction = 1
        else:
            direction = -1 if event.delta > 0 else 1
        self.decision_canvas.yview_scroll(direction, "units")
        return "break"

    def _bind_decision_scroll(self, widget):
        widget.bind("<MouseWheel>", self._scroll_decision)
        widget.bind("<Button-4>", self._scroll_decision)
        widget.bind("<Button-5>", self._scroll_decision)
        for child in widget.winfo_children():
            self._bind_decision_scroll(child)

    def _build_osi_guide(self, parent: tk.Widget):
        guide_text = (
            "THE 7 LAYERS OF THE OSI MODEL (DECISION-DRIVEN GUIDE):\n\n"
            "• Layer 7 (Application): Human interface & network services (HTTP/HTTPS, DNS, FTP, Chat).\n"
            "• Layer 6 (Presentation): Character encodings (UTF-8, ASCII), compression (H.264), encryption (TLS/AES). Mismatches cause Mojibake.\n"
            "• Layer 5 (Session): Establishment, authentication, and teardown of communication channels (SIP, Keep-Alive, Tokens).\n"
            "• Layer 4 (Transport): End-to-end transport protocol (TCP reliable/ordered vs UDP low-latency datagrams, Port numbers).\n"
            "• Layer 3 (Network): Logical IP routing and addressing across interconnected subnets (Routers, Gateways, TTL).\n"
            "• Layer 2 (Data Link): Physical MAC addressing, local framing, and CRC32 FCS error detection (Switches, Ethernet).\n"
            "• Layer 1 (Physical): Raw transmission of bitstreams over physical copper, fiber, or radio media."
        )
        lbl = tk.Label(parent, text=guide_text, font=theme.FONT_SMALL, fg=theme.TEXT_SECONDARY, bg=theme.BG_CARD, justify=tk.LEFT)
        lbl.pack(anchor=tk.W)

    # --- DECISION CONSOLE RENDERING ---
    def handle_decision_ready(self, decision: StageDecision):
        """Render the interactive decision challenge in the console."""
        self.active_decision = decision

        # Highlight current active layer card
        meta = theme.OSI_METADATA.get(decision.layer_num, {"name": f"Layer {decision.layer_num}", "color": theme.TEXT_ACCENT})
        self.sender_stack.update_layer_status(decision.layer_num, LayerStatus.ACTIVE, "Awaiting User Decision")

        # Clear existing decision widgets
        for frame in (self.decision_content, self.decision_action_frame):
            for widget in frame.winfo_children():
                widget.destroy()
        self.decision_feedback = None
        self.decision_canvas.yview_moveto(0)

        # Header Badge
        header = tk.Frame(self.decision_content, bg=theme.BG_CARD)
        header.pack(fill=tk.X, pady=(0, 4))

        badge = tk.Label(
            header,
            text=f"LAYER {decision.layer_num} — {meta['name'].upper()}",
            font=theme.FONT_TINY,
            fg="#ffffff",
            bg=meta['color'],
            padx=8,
            pady=2
        )
        badge.pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(
            header,
            text=decision.title,
            font=theme.FONT_SUBTITLE,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_CARD
        ).pack(side=tk.LEFT)

        # Prompt & Educational Explanation
        prompt_lbl = tk.Label(
            self.decision_content,
            text=decision.prompt,
            font=theme.FONT_BODY_BOLD,
            fg=theme.TEXT_ACCENT,
            bg=theme.BG_CARD,
            justify=tk.LEFT,
            wraplength=480
        )
        prompt_lbl.pack(anchor=tk.W, pady=(2, 2))

        expl_lbl = tk.Label(
            self.decision_content,
            text=decision.explanation,
            font=theme.FONT_TINY,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD,
            justify=tk.LEFT,
            wraplength=480
        )
        expl_lbl.pack(anchor=tk.W, pady=(0, 6))

        # Render Input Controls based on input_type
        if decision.input_type == "CHOICE":
            self.choice_var.set("")
            opts_box = tk.Frame(self.decision_content, bg=theme.BG_CARD)
            opts_box.pack(fill=tk.X, pady=2)

            for opt in decision.options:
                opt_frame = tk.Frame(opts_box, bg="#1a2230", bd=1, relief=tk.SOLID, padx=8, pady=4)
                opt_frame.pack(fill=tk.X, pady=3)

                rb = tk.Radiobutton(
                    opt_frame,
                    text=opt['title'],
                    value=opt['id'],
                    variable=self.choice_var,
                    bg="#1a2230",
                    fg=theme.TEXT_PRIMARY,
                    selectcolor=theme.BG_DARK,
                    activebackground="#1a2230",
                    activeforeground=theme.TEXT_ACCENT,
                    font=theme.FONT_BODY_BOLD,
                    command=self._on_choice_selected
                )
                rb.pack(anchor=tk.W)

                if opt.get('desc'):
                    tk.Label(
                        opt_frame,
                        text=opt['desc'],
                        font=theme.FONT_TINY,
                        fg=theme.TEXT_SECONDARY,
                        bg="#1a2230",
                        justify=tk.LEFT,
                        wraplength=450
                    ).pack(anchor=tk.W, padx=(22, 0))

        elif decision.input_type == "TEXT_INPUT":
            input_box = tk.Frame(self.decision_content, bg=theme.BG_CARD)
            input_box.pack(fill=tk.X, pady=4)

            tk.Label(
                input_box,
                text=decision.input_label or "Enter Value:",
                font=theme.FONT_BODY_BOLD,
                fg=theme.TEXT_PRIMARY,
                bg=theme.BG_CARD
            ).pack(side=tk.LEFT, padx=(0, 8))

            self.entry_var.set(decision.default_value)
            entry = tk.Entry(
                input_box,
                textvariable=self.entry_var,
                font=theme.FONT_BODY,
                bg=theme.BG_INPUT,
                fg=theme.TEXT_PRIMARY,
                insertbackground="white",
                width=34
            )
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Action / Submit Button
        self.decision_feedback = tk.Label(
            self.decision_action_frame,
            text="",
            font=theme.FONT_TINY,
            fg=theme.COLOR_WARNING,
            bg=theme.BG_CARD,
            anchor=tk.W
        )
        self.decision_feedback.pack(fill=tk.X, pady=(0, 4))

        btn_submit = tk.Button(
            self.decision_action_frame,
            text=decision.button_label,
            font=theme.FONT_BODY_BOLD,
            bg=theme.OSI_COLORS[4],
            fg="#ffffff",
            activebackground="#0891b2",
            activeforeground="#ffffff",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._on_submit_decision
        )
        btn_submit.pack(fill=tk.X)
        self._bind_decision_scroll(self.decision_content)

    def _on_choice_selected(self):
        if self.decision_feedback:
            self.decision_feedback.config(text="")

    def _on_submit_decision(self):
        """Pass user's decision to mission for execution and consequence evaluation."""
        if not self.active_decision:
            return

        if self.active_decision.input_type == "CHOICE":
            val = self.choice_var.get()
            if not val:
                if self.decision_feedback:
                    self.decision_feedback.config(text="Select an option before continuing.")
                return
        elif self.active_decision.input_type == "TEXT_INPUT":
            val = self.entry_var.get()
        else:
            val = "action"

        self.mission.submit_user_decision(val)

    # --- CALLBACK HANDLERS ---
    def handle_layer_update(self, side: str, layer_num: int, status: LayerStatus, text: str, has_error: bool):
        if side == "sender":
            self.sender_stack.update_layer_status(layer_num, status, text, has_error)
        else:
            self.receiver_stack.update_layer_status(layer_num, status, text, has_error)

    def handle_log(self, level: str, icon: str, message: str, layer_num: Optional[int]):
        self.event_log.log(level, icon, message, layer_num)

    def handle_network_animate(
        self,
        from_node: str,
        to_node: str,
        pkt_type: str,
        label: str,
        is_dropped: bool,
        on_reached: Optional[Callable]
    ):
        self.net_canvas.animate_packet(
            from_node, to_node, pkt_type, label, is_dropped, on_reached,
            duration_ms=650
        )
        self.net_canvas.update_stats(self.mission.packets_sent, self.mission.packets_received, self.mission.packets_lost)

    def handle_troubleshoot(self, issue: TroubleshootIssue):
        # Open interactive repair dialog
        RepairDialog(self, issue, on_repaired=self.on_issue_repaired)

    def on_issue_repaired(self):
        self.mission.resolve_current_error()

    def handle_complete(self, summary_stats: Dict[str, Any]):
        CompletionDialog(
            self,
            mission_title=self.mission.title,
            summary_stats=summary_stats,
            on_return_missions=self.on_back,
            on_replay=self.reset_simulation
        )

    def handle_inspector_update(self):
        self.inspector.update_data(self.mission.inspector_data)

    def handle_output_update(self):
        pass

    def on_layer_selected_by_user(self, layer_num: int):
        self.inspector.select_layer(layer_num)

    def on_wrench_clicked(self, layer_num: int):
        if self.mission.active_issue and self.mission.active_issue.layer_num == layer_num:
            self.handle_troubleshoot(self.mission.active_issue)

    def reset_simulation(self):
        self.sender_stack.reset_all()
        self.receiver_stack.reset_all()
        self.net_canvas.update_stats(0, 0, 0)
        self.event_log.log("INFO", "↺", "Mission reset. Preparing initial decision...", None)
        self.mission.start_mission()

    def _handle_back_click(self):
        self.on_back()
