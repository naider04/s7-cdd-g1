"""
Mission 3: Make a Video Call
Interactive, decision-driven simulation covering:
- L6 Video Codec Compression (H.264 vs Raw Uncompressed)
- L4 Transport Protocol Trade-offs: UDP (RTP) vs TCP Head-of-Line Blocking
- L5 Session Negotiation (SIP/SDP)
- Real-world consequences: 1450ms video freeze in TCP vs fluid 22ms streaming in UDP
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional
from missions.base_mission import BaseMission
from models import LayerStatus, TroubleshootIssue, RepairOption, StageDecision, PacketInspectorData
from utils.helpers import format_hex_dump
import theme


class MissionVideoCall(BaseMission):
    def __init__(self):
        super().__init__(
            mission_id=3,
            title="Make a Video Call",
            icon="📹",
            subtitle="Establish live audio/video communication with transport latency trade-offs",
            objective="Connect a real-time video call. Select video codecs, negotiate session control, and test whether TCP or UDP best supports interactive conversations.",
            concepts=[
                "Real-Time Transport Protocol (RTP / UDP)",
                "Latency vs Reliability Trade-off",
                "Head-of-Line Blocking in TCP",
                "Video Codec Compression (L6 H.264)",
                "Session Signaling (SIP / SDP at L5)"
            ]
        )
        self.selected_codec = "H.264"
        self.selected_protocol = "UDP"
        self.call_quality = "STANDBY"
        self.latency_ms = 22
        self.jitter_ms = 3

        # UI elements
        self.canvas_video: Optional[tk.Canvas] = None
        self.lbl_quality: Optional[tk.Label] = None
        self.lbl_latency: Optional[tk.Label] = None

    def build_visual_output_ui(self, parent: tk.Widget):
        container = tk.Frame(parent, bg=theme.BG_PANEL, padx=10, pady=8)
        container.pack(fill=tk.BOTH, expand=True)

        top = tk.Frame(container, bg=theme.BG_DARK, padx=10, pady=6, bd=1, relief=tk.SOLID)
        top.pack(fill=tk.X, pady=(0, 6))

        tk.Label(top, text="📹 Live Video Call Session", font=theme.FONT_SUBTITLE, fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK).pack(side=tk.LEFT)

        self.lbl_quality = tk.Label(top, text="Quality: STANDBY", font=theme.FONT_BODY_BOLD, fg=theme.TEXT_MUTED, bg=theme.BG_DARK)
        self.lbl_quality.pack(side=tk.RIGHT, padx=8)

        self.lbl_latency = tk.Label(top, text="Latency: -- ms | Jitter: -- ms", font=theme.FONT_SMALL, fg=theme.TEXT_SECONDARY, bg=theme.BG_DARK)
        self.lbl_latency.pack(side=tk.RIGHT, padx=15)

        # Dual Video Screen Simulation
        video_box = tk.Frame(container, bg=theme.BG_PANEL)
        video_box.pack(fill=tk.BOTH, expand=True)

        self.canvas_video = tk.Canvas(video_box, bg="#1a1d24", highlightthickness=1, highlightbackground=theme.BORDER, height=140)
        self.canvas_video.pack(fill=tk.BOTH, expand=True)
        self.draw_video_call("STANDBY")

    def draw_video_call(self, state: str):
        if not self.canvas_video:
            return
        c = self.canvas_video
        c.delete("all")
        w = c.winfo_width() or 580
        h = c.winfo_height() or 140

        half_w = w / 2

        # Person A (Local Camera)
        c.create_rectangle(10, 10, half_w - 5, h - 10, fill="#222733", outline=theme.OSI_COLORS[5], width=1)
        c.create_text(20, 25, text="👤 Person A (Local Feed - 720p)", font=theme.FONT_SMALL, fill=theme.TEXT_MUTED, anchor=tk.W)
        c.create_oval(half_w/2 - 25, h/2 - 35, half_w/2 + 25, h/2 + 15, fill="#3b82f6", outline="")
        c.create_text(half_w/2, h/2 - 10, text="👤", font=(theme.FONT_FAMILY, 24))
        c.create_text(half_w/2, h - 25, text="Audio: 🎙 ACTIVE (Opus Codec)", font=theme.FONT_TINY, fill=theme.COLOR_SUCCESS)

        # Person B (Remote Stream Received)
        c.create_rectangle(half_w + 5, 10, w - 10, h - 10, fill="#222733", outline=theme.OSI_COLORS[3], width=1)
        c.create_text(half_w + 15, 25, text="👤 Person B (Remote Stream Received)", font=theme.FONT_SMALL, fill=theme.TEXT_MUTED, anchor=tk.W)

        cx = half_w + (w - half_w)/2
        if state == "STANDBY":
            c.create_text(cx, h/2, text="Call not started (Awaiting Decisions)", font=theme.FONT_BODY, fill=theme.TEXT_MUTED)
        elif state == "UDP_GOOD":
            c.create_oval(cx - 25, h/2 - 35, cx + 25, h/2 + 15, fill="#10b981", outline="")
            c.create_text(cx, h/2 - 10, text="👤", font=(theme.FONT_FAMILY, 24))
            c.create_text(cx, h - 25, text="✓ Smooth Real-Time Playback (30 FPS, 22ms)", font=theme.FONT_TINY, fill=theme.COLOR_SUCCESS)
        elif state == "UDP_GLITCH":
            c.create_oval(cx - 25, h/2 - 35, cx + 25, h/2 + 15, fill="#059669", outline="")
            c.create_text(cx, h/2 - 10, text="👤", font=(theme.FONT_FAMILY, 24))
            c.create_rectangle(cx - 20, h/2 - 15, cx + 20, h/2 - 5, fill="#f59e0b", outline="")
            c.create_text(cx, h - 25, text="⚠ Frame #3 Dropped -> Skipped (Call Intact!)", font=theme.FONT_TINY, fill=theme.COLOR_WARNING)
        elif state == "TCP_FROZEN":
            c.create_oval(cx - 25, h/2 - 35, cx + 25, h/2 + 15, fill="#dc2626", outline="")
            c.create_text(cx, h/2 - 10, text="❄️", font=(theme.FONT_FAMILY, 24))
            c.create_text(cx, h/2 + 25, text="STREAM FROZEN (Lag: 1.45s)", font=theme.FONT_SMALL, fill=theme.COLOR_ERROR)
            c.create_text(cx, h - 25, text="✗ Head-of-Line Blocking Waiting for Retransmit", font=theme.FONT_TINY, fill=theme.COLOR_ERROR)

    def load_initial_stage(self):
        self.current_stage_index = 0
        self.stages = [
            # Stage 0: L6 Codec Compression
            StageDecision(
                stage_id="l6_codec",
                layer_num=6,
                title="Presentation Layer — Video Encoding & Compression",
                prompt="Webcam captures raw video at 720p 30fps. How should the Presentation Layer encode the video data before transmission?",
                explanation="Raw 720p uncompressed RGB video requires over 660 Mbps of bandwidth. Video codecs (like H.264) compress video by over 98% to fit standard network connections.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "h264",
                        "title": "H.264 (AVC) Lossy Real-Time Compression (~2 Mbps)",
                        "desc": "Compresses video using inter-frame predictive encoding, allowing smooth internet streaming."
                    },
                    {
                        "id": "raw_rgb",
                        "title": "Raw Uncompressed Bitmaps (RGB24 — 660 Mbps)",
                        "desc": "Sends each pixel value without compression."
                    }
                ],
                default_value="h264",
                button_label="Apply Presentation Codec ▶"
            ),
            # Stage 1: L4 Transport Decision: UDP vs TCP
            StageDecision(
                stage_id="l4_multimedia",
                layer_num=4,
                title="Transport Layer — Low Latency vs Ordered Delivery",
                prompt="For an interactive two-way voice and video conversation, which Transport Layer protocol is best suited?",
                explanation="In human conversations, a delayed audio/video frame is useless. If a packet is lost, is it better to freeze the call to retransmit, or skip it to keep the call live?",
                input_type="CHOICE",
                options=[
                    {
                        "id": "udp",
                        "title": "UDP with RTP (Real-Time Transport Protocol) — Low Latency",
                        "desc": "Delivers packets immediately without retransmission delays. Occasional lost packets are skipped."
                    },
                    {
                        "id": "tcp",
                        "title": "TCP — Guaranteed In-Order Delivery & Retransmission",
                        "desc": "Forces the receiver to freeze playback whenever a packet is dropped until retransmission completes."
                    }
                ],
                default_value="udp",
                button_label="Select Transport Protocol ▶"
            ),
            # Stage 2: L5 Session Signaling
            StageDecision(
                stage_id="l5_session",
                layer_num=5,
                title="Session Layer — Call Signaling & Dialog Control",
                prompt="Which Session Layer signaling protocol should establish the media channel parameters (SDP media offer/answer) between Person A and B?",
                explanation="Session Layer protocols establish, maintain, and terminate interactive sessions. SIP (Session Initiation Protocol) is the telecom standard.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "sip",
                        "title": "SIP / SDP (Session Initiation Protocol — Port 5060)",
                        "desc": "Exchanges audio/video capabilities (codecs, ports) and establishes duplex media channel."
                    },
                    {
                        "id": "ftp_control",
                        "title": "FTP Control (Port 21)",
                        "desc": "File transfer control channel."
                    }
                ],
                default_value="sip",
                button_label="Establish Communication Session ▶"
            ),
            # Stage 3: Live Media Stream & Consequence Test
            StageDecision(
                stage_id="l4_stream_consequence",
                layer_num=4,
                title="Transmission & Packet Drop — Live Call Consequence",
                prompt="Transmitting live multimedia frames across the network. A router drop occurs on Frame #3. Observe consequences:",
                explanation="Observe how the chosen Transport protocol (TCP vs UDP) behaves when router congestion drops a video frame.",
                input_type="ACTION",
                options=[],
                button_label="Transmit Video Frames & Observe Call ▶"
            )
        ]

        self.present_current_stage()

    def submit_user_decision(self, user_value: str, extra_data: Optional[Dict[str, Any]] = None):
        super().submit_user_decision(user_value, extra_data)
        stage = self.stages[self.current_stage_index]

        if stage.stage_id == "l6_codec":
            if user_value == "raw_rgb":
                # Consequence: Bandwidth overflow!
                self.update_layer("sender", 6, LayerStatus.ERROR, "Bandwidth Overflow (660 Mbps > 100 Mbps)", has_error=True)
                self.log("ERROR", "⚠", "Consequence: Raw uncompressed video generates 660 Mbps of data! Uplink capacity is only 100 Mbps. Complete link saturation and crash!", 6)

                def fix_codec():
                    self.selected_codec = "H.264"
                    self.update_layer("sender", 6, LayerStatus.COMPLETE, "H.264 (2 Mbps Stream)")
                    self.log("SUCCESS", "✓", "Repaired: H.264 lossy compression enabled. Stream reduced to manageable 2 Mbps.", 6)
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=6,
                    title="Presentation Layer: Link Capacity Overflow",
                    summary="Uncompressed 720p raw video generates 660 Mbps of traffic, exceeding the network card bandwidth limit.",
                    details=(
                        "Layer 6 (Presentation) is responsible for data compression.\n\n"
                        "Without codec compression (e.g. H.264, VP9, AV1), transmitting 1280x720 pixels at 30 fps requires:\n"
                        "1280 * 720 * 24 bits * 30 fps = ~663 Mbps!\n\n"
                        "Modern codecs use discrete cosine transforms and motion estimation to compress video by 98% down to 2 Mbps without perceptible loss of quality."
                    ),
                    options=[
                        RepairOption(
                            id="use_h264",
                            title="Compress with H.264 Codec (Recommended)",
                            description="Encode frames using H.264 standard for real-time internet streaming.",
                            is_correct=True,
                            feedback="Correct! Bandwidth drops to 2 Mbps, easily accommodated by the link."
                        ),
                        RepairOption(
                            id="keep_raw",
                            title="Buy a 10 Gbps dedicated fiber line",
                            description="Spend thousands of dollars on enterprise fiber.",
                            is_correct=False,
                            feedback="Impractical and unnecessary. Video applications always use video codecs."
                        )
                    ],
                    on_repair_success=fix_codec
                )
                self.trigger_error(issue)
                return

            self.selected_codec = "H.264"
            self.update_layer("sender", 6, LayerStatus.COMPLETE, "H.264 Compressed (2 Mbps)")
            self.log("INFO", "✓", "L6 (Presentation): Encoded video using H.264 AVC (High Profile) & audio using Opus.", 6)
            self.inspector_data.encoding = "H.264 / Opus"
            self.inspector_data.compression = "Lossy DCT Motion Vectors"
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l4_multimedia":
            self.selected_protocol = "UDP" if user_value == "udp" else "TCP"
            if self.selected_protocol == "TCP":
                self.log("WARNING", "⚠", "User chose TCP: Warning! Strict in-order delivery will cause head-of-line blocking if packets drop!", 4)
                self.update_layer("sender", 4, LayerStatus.ACTIVE, "TCP (Retransmission Enabled)")
            else:
                self.log("INFO", "✓", "User chose UDP: Real-Time Transport Protocol (RTP) over UDP. Optimized for interactive conversations.", 4)
                self.update_layer("sender", 4, LayerStatus.ACTIVE, "UDP / RTP (Zero Retransmission Delay)")

            self.inspector_data.transport_protocol = f"{self.selected_protocol} (RTP Port 5004)"
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l5_session":
            if user_value == "ftp_control":
                self.update_layer("sender", 5, LayerStatus.ERROR, "Session Protocol Mismatch (FTP)", has_error=True)
                self.log("ERROR", "⚠", "Consequence: FTP Control cannot initiate or negotiate media codecs for real-time video calls!", 5)

                def fix_session():
                    self.update_layer("sender", 5, LayerStatus.COMPLETE, "SIP/SDP Session Active")
                    self.log("SUCCESS", "✓", "Repaired: SIP INVITE negotiated. Duplex RTP media channel open.", 5)
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=5,
                    title="Session Layer Protocol Incompatibility",
                    summary="FTP is a file-transfer protocol. It does not support real-time audio/video session negotiation.",
                    details=(
                        "In VoIP and video conferencing, Session Initiation Protocol (SIP) is used at Layer 5 to:\n"
                        "• Locate endpoints\n"
                        "• Negotiate media types via SDP (Session Description Protocol)\n"
                        "• Ring and establish call connections\n"
                        "• Tear down calls when hung up."
                    ),
                    options=[
                        RepairOption(
                            id="use_sip",
                            title="Negotiate session with SIP / SDP (Recommended)",
                            description="Use standard VoIP signaling protocol.",
                            is_correct=True,
                            feedback="Correct! SIP INVITE established duplex media session."
                        ),
                        RepairOption(
                            id="skip_session",
                            title="Proceed with no session tracking",
                            description="Stream without negotiating codecs.",
                            is_correct=False,
                            feedback="Incorrect. Receiver won't know which codec or port to listen on."
                        )
                    ],
                    on_repair_success=fix_session
                )
                self.trigger_error(issue)
                return

            self.update_layer("sender", 5, LayerStatus.COMPLETE, "SIP/SDP Session Active")
            self.log("INFO", "✓", "L5 (Session): SIP dialog established. SDP agreed on H.264 @ 720p.", 5)
            self._advance_to_next_stage()

        elif stage.stage_id == "l4_stream_consequence":
            # Animate video stream packets and test consequence!
            self.log("INFO", "→", f"Streaming video packets across network using {self.selected_protocol}...", None)

            def on_stream_done():
                self.packets_sent += 10
                self.packets_received += 9  # 1 packet dropped

                if self.selected_protocol == "TCP":
                    # Severe freeze consequence!
                    self.latency_ms = 1450
                    self.jitter_ms = 320
                    self.call_quality = "POOR (Freeze: 1.45s)"
                    if self.lbl_quality:
                        self.lbl_quality.config(text=f"Quality: {self.call_quality}", fg=theme.COLOR_ERROR)
                    if self.lbl_latency:
                        self.lbl_latency.config(text=f"Latency: {self.latency_ms} ms | Jitter: {self.jitter_ms} ms", fg=theme.COLOR_ERROR)
                    self.draw_video_call("TCP_FROZEN")

                    self.update_layer("receiver", 4, LayerStatus.ERROR, "TCP Stalled (Head-of-Line)", has_error=True)
                    self.log("ERROR", "⚠", "Consequence of TCP Choice: When Frame #3 dropped, TCP halted playback! All newer frames are blocked waiting for retransmission. Call is frozen!", 4)

                    def fix_to_udp():
                        self.selected_protocol = "UDP"
                        self.latency_ms = 22
                        self.jitter_ms = 4
                        self.call_quality = "EXCELLENT (22ms)"
                        if self.lbl_quality:
                            self.lbl_quality.config(text=f"Quality: {self.call_quality}", fg=theme.COLOR_SUCCESS)
                        if self.lbl_latency:
                            self.lbl_latency.config(text=f"Latency: {self.latency_ms} ms | Jitter: {self.jitter_ms} ms", fg=theme.COLOR_SUCCESS)
                        self.draw_video_call("UDP_GOOD")
                        self.log("SUCCESS", "✓", "Switched to UDP (RTP): Lost frames are simply skipped by codec. Real-time latency restored to 22ms!", 4)
                        self.update_layer("receiver", 4, LayerStatus.COMPLETE, "UDP / RTP Real-Time Active")
                        self._finish_video_mission()

                    issue = TroubleshootIssue(
                        layer_num=4,
                        title="Head-of-Line Blocking in Video Call (TCP Failure)",
                        summary="The call froze for 1.45 seconds because TCP halts the stream to wait for lost packet retransmissions.",
                        details=(
                            "This demonstrates why almost all interactive video/voice applications (Zoom, Discord, WebRTC) use UDP.\n\n"
                            "With TCP, if Packet #3 is lost, Packets #4, #5, #6 are buffered and held back from the application until #3 is retransmitted.\n"
                            "In a live conversation, an old frame from 1.5 seconds ago is worthless!\n\n"
                            "With UDP, missing packets are simply dropped, allowing the video codec to interpolate or skip ahead with zero latency penalty."
                        ),
                        options=[
                            RepairOption(
                                id="switch_udp_rtp",
                                title="Switch Transport Protocol to UDP (RTP - Recommended)",
                                description="Eliminate retransmission delays to preserve fluid two-way dialogue.",
                                is_correct=True,
                                feedback="Correct! Latency immediately drops from 1450ms back to 22ms."
                            ),
                            RepairOption(
                                id="wait_tcp_more",
                                title="Wait for TCP retransmit to finish",
                                description="Keep conversation frozen.",
                                is_correct=False,
                                feedback="Incorrect. Waiting for retransmission ruins real-time conversations."
                            )
                        ],
                        on_repair_success=fix_to_udp
                    )
                    self.trigger_error(issue)
                    return

                # UDP success
                self.latency_ms = 24
                self.jitter_ms = 4
                self.call_quality = "EXCELLENT (24ms)"
                if self.lbl_quality:
                    self.lbl_quality.config(text=f"Quality: {self.call_quality}", fg=theme.COLOR_SUCCESS)
                if self.lbl_latency:
                    self.lbl_latency.config(text=f"Latency: {self.latency_ms} ms | Jitter: {self.jitter_ms} ms", fg=theme.COLOR_SUCCESS)
                self.draw_video_call("UDP_GLITCH")
                self.log("INFO", "✓", "UDP Resilience: Frame #3 was dropped by router, but RTP smoothly skipped it. Audio/video remained live at 24ms!", 4)
                self._finish_video_mission()

            if self.cb_network_animate:
                self.cb_network_animate("Person A", "Person B", "PACKET", "RTP Video Frame", False, on_stream_done)
            else:
                on_stream_done()

    def _finish_video_mission(self):
        for lyr in range(1, 8):
            self.update_layer("receiver", lyr, LayerStatus.COMPLETE, "Decapsulated & Streaming")

        self.complete_mission({
            "Session Type": "Real-Time Video Call (WebRTC)",
            "Video Codec (L6)": self.selected_codec,
            "Transport Protocol (L4)": self.selected_protocol,
            "End-to-End Latency": f"{self.latency_ms} ms",
            "Decisions Made": self.decisions_made,
            "Errors Diagnosed & Fixed": self.errors_repaired,
            "Key Lesson": "Interactive multimedia requires UDP because timeliness is more vital than 100% reliability. Head-of-line blocking in TCP makes live conversation impossible."
        })

    def _advance_to_next_stage(self):
        self.current_stage_index += 1
        self.present_current_stage()
