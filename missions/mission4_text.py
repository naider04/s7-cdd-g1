"""
Mission 4: Send a Text Message
Interactive, decision-driven simulation covering:
- L7 User-Typed Input (Multilingual Spanish text, emojis)
- L6 Character Encoding: UTF-8 vs 7-Bit ASCII vs ISO-8859-1 Mojibake
- L6 Encryption vs Encoding distinction (AES-256 Keys)
- Real-time consequences: Mojibake corruption rendered directly on Receiver's phone screen
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional
from missions.base_mission import BaseMission
from models import LayerStatus, TroubleshootIssue, RepairOption, StageDecision, PacketInspectorData
from utils.helpers import text_to_bits, format_hex_dump
import theme


class MissionTextMessage(BaseMission):
    def __init__(self):
        super().__init__(
            mission_id=4,
            title="Send a Text Message",
            icon="💬",
            subtitle="Transmit custom multilingual text with character encoding decisions",
            objective="Type a message with accents or emojis. Choose character encodings and encryption, and observe what happens when endpoints disagree on data representation.",
            concepts=[
                "Presentation Layer (L6) Data Representation",
                "Character Encodings (UTF-8 Multibyte vs 7-Bit ASCII)",
                "Mojibake Encoding Mismatch (Latin-1 vs UTF-8)",
                "Encoding vs Encryption Distinction",
                "End-to-End Chat Reconstruction"
            ]
        )
        self.raw_message = "¡Hola María! ¿Cómo estás? 🚀"
        self.selected_encoding = "UTF-8"
        self.selected_encryption = "PLAIN"
        self.receiver_decoding = "UTF-8"

        # UI elements
        self.chat_bubble_box: Optional[tk.Frame] = None
        self.status_chat_lbl: Optional[tk.Label] = None

    def build_visual_output_ui(self, parent: tk.Widget):
        container = tk.Frame(parent, bg=theme.BG_PANEL, padx=10, pady=8)
        container.pack(fill=tk.BOTH, expand=True)

        top = tk.Frame(container, bg=theme.BG_DARK, padx=10, pady=6, bd=1, relief=tk.SOLID)
        top.pack(fill=tk.X, pady=(0, 6))

        tk.Label(top, text="💬 Person B - Smartphone Messenger", font=theme.FONT_SUBTITLE, fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK).pack(side=tk.LEFT)

        self.status_chat_lbl = tk.Label(top, text="Awaiting Message...", font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_DARK)
        self.status_chat_lbl.pack(side=tk.RIGHT)

        # Messenger Window
        chat_frame = tk.Frame(container, bg="#0d1117", bd=1, relief=tk.RIDGE, padx=15, pady=12)
        chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_bubble_box = tk.Frame(chat_frame, bg="#0d1117")
        self.chat_bubble_box.pack(fill=tk.BOTH, expand=True)

        self.render_chat_placeholder()

    def render_chat_placeholder(self):
        if not self.chat_bubble_box:
            return
        for w in self.chat_bubble_box.winfo_children():
            w.destroy()
        tk.Label(self.chat_bubble_box, text="No messages received yet. Submit decisions to transmit text.", font=theme.FONT_BODY, fg=theme.TEXT_MUTED, bg="#0d1117").pack(pady=40)

    def render_chat_message(self, text: str, is_corrupted: bool = False):
        if not self.chat_bubble_box:
            return
        for w in self.chat_bubble_box.winfo_children():
            w.destroy()

        bubble = tk.Frame(self.chat_bubble_box, bg="#1e293b" if not is_corrupted else "#451a1a", padx=12, pady=10, bd=1, relief=tk.SOLID)
        bubble.pack(anchor=tk.W, pady=10)

        sender_lbl = tk.Label(bubble, text="Person A", font=theme.FONT_BODY_BOLD, fg=theme.TEXT_ACCENT, bg=bubble['bg'])
        sender_lbl.pack(anchor=tk.W)

        msg_lbl = tk.Label(bubble, text=text, font=(theme.FONT_FAMILY, 13), fg=theme.COLOR_ERROR if is_corrupted else theme.TEXT_PRIMARY, bg=bubble['bg'])
        msg_lbl.pack(anchor=tk.W, pady=4)

        meta = tk.Frame(bubble, bg=bubble['bg'])
        meta.pack(fill=tk.X)

        if is_corrupted:
            tk.Label(meta, text="⚠ Mojibake Encoding Failure: Byte mismatch", font=theme.FONT_TINY, fg=theme.COLOR_ERROR, bg=bubble['bg']).pack(side=tk.LEFT)
        else:
            tk.Label(meta, text="✓✓ Delivered & Decoded Cleanly (UTF-8)", font=theme.FONT_TINY, fg=theme.COLOR_SUCCESS, bg=bubble['bg']).pack(side=tk.LEFT)

    def load_initial_stage(self):
        self.current_stage_index = 0
        self.stages = [
            # Stage 0: L7 Custom Message Typing
            StageDecision(
                stage_id="l7_text_input",
                layer_num=7,
                title="Application Layer — Compose Message",
                prompt="Type the text message Person A wants to transmit to Person B (include accents or emojis to test Unicode support):",
                explanation="The user interface in Layer 7 captures human input as abstract character strings.",
                input_type="TEXT_INPUT",
                default_value=self.raw_message,
                input_label="Message text:",
                button_label="Capture Text & Proceed to Layer 6 ▶"
            ),
            # Stage 1: L6 Character Encoding Choice
            StageDecision(
                stage_id="l6_encoding",
                layer_num=6,
                title="Presentation Layer — Character Encoding",
                prompt="How should Layer 6 serialize the text characters into binary bytes?",
                explanation="Encoding maps human characters to binary code points. ASCII is 7-bit (128 English characters), while UTF-8 supports over 149,000 international characters.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "utf8",
                        "title": "UTF-8 (Variable-length Unicode — 1 to 4 bytes per char)",
                        "desc": "Supports all languages, Spanish accents (¡, á, í, ¿), and emojis."
                    },
                    {
                        "id": "ascii",
                        "title": "ASCII (7-Bit Standard — Values 0 to 127)",
                        "desc": "Traditional 7-bit English encoding. Non-ASCII characters cause encoding errors."
                    }
                ],
                default_value="utf8",
                button_label="Apply Encoding Format ▶"
            ),
            # Stage 2: L6 Receiver Decoding Mode
            StageDecision(
                stage_id="l6_receiver_decode",
                layer_num=6,
                title="Presentation Layer — Receiver Interpretation",
                prompt="Which decoding standard should Person B's Presentation Layer use to reconstruct the received bytes?",
                explanation="If the sender and receiver disagree on the representation, raw byte values will be mapped to the wrong glyphs, producing Mojibake.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "match_utf8",
                        "title": "UTF-8 Decoder (Matching Interpretation)",
                        "desc": "Correctly parses multi-byte sequences into the original characters."
                    },
                    {
                        "id": "mismatch_latin1",
                        "title": "ISO-8859-1 Latin-1 Decoder (Encoding Mismatch — Triggers Mojibake!)",
                        "desc": "Interprets each individual byte of a UTF-8 sequence as a separate Latin character, scrambling the text."
                    }
                ],
                default_value="match_utf8",
                button_label="Transmit Across Network & Decode ▶"
            )
        ]

        self.present_current_stage()

    def submit_user_decision(self, user_value: str, extra_data: Optional[Dict[str, Any]] = None):
        super().submit_user_decision(user_value, extra_data)
        stage = self.stages[self.current_stage_index]

        if stage.stage_id == "l7_text_input":
            self.raw_message = user_value.strip() or "¡Hola María! ¿Cómo estás? 🚀"
            self.update_layer("sender", 7, LayerStatus.COMPLETE, f"Captured: '{self.raw_message[:20]}...'")
            self.log("INFO", "✓", f"L7 (Application): Text message input captured: '{self.raw_message}'", 7)
            self.inspector_data.app_protocol = "JSON Instant Message"
            self.inspector_data.payload_text = f'{{"text": "{self.raw_message}"}}'
            self.inspector_data.payload_hex = format_hex_dump(self.inspector_data.payload_text.encode("utf-8", errors="replace"))
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l6_encoding":
            self.selected_encoding = "UTF-8" if user_value == "utf8" else "ASCII"

            if self.selected_encoding == "ASCII":
                # Consequence: ASCII cannot encode accents/emojis!
                try:
                    self.raw_message.encode("ascii")
                except UnicodeEncodeError:
                    self.update_layer("sender", 6, LayerStatus.ERROR, "ASCII UnicodeEncodeError!", has_error=True)
                    self.log("ERROR", "⚠", f"Consequence: ASCII is a 7-bit encoding (0-127). The message '{self.raw_message}' contains non-ASCII characters that cannot be represented in ASCII!", 6)

                    def fix_to_utf8():
                        self.selected_encoding = "UTF-8"
                        self.update_layer("sender", 6, LayerStatus.COMPLETE, "UTF-8 Encoded")
                        self.log("SUCCESS", "✓", "Repaired to UTF-8: Multi-byte Unicode supports all international characters and emojis.", 6)
                        self._advance_to_next_stage()

                    issue = TroubleshootIssue(
                        layer_num=6,
                        title="Presentation Layer: Character Set Incompatibility (ASCII)",
                        summary="The text contains non-ASCII code points (Spanish accents, emojis). ASCII only supports 128 standard English characters.",
                        details=(
                            f"The input string contains characters like '¡', 'á', 'í', '¿' or '🚀'.\n\n"
                            "ASCII uses 7 bits per character (0 to 127). Any character above 127 cannot be serialized into ASCII bytes without data loss or exceptions.\n\n"
                            "UTF-8 is an 8-bit variable-length encoding that dynamically uses 1 to 4 bytes per character, supporting all written human languages and symbols."
                        ),
                        options=[
                            RepairOption(
                                id="fix_utf8",
                                title="Switch Presentation Layer to UTF-8 (Recommended)",
                                description="Encode text using UTF-8 variable-length Unicode.",
                                is_correct=True,
                                feedback="Correct! UTF-8 seamlessly encodes Spanish accents and emojis."
                            ),
                            RepairOption(
                                id="strip_chars",
                                title="Delete all accents and emojis to force ASCII",
                                description="Mutate text to plain English.",
                                is_correct=False,
                                feedback="Incorrect! Network protocols must accommodate user data without stripping meaning."
                            )
                        ],
                        on_repair_success=fix_to_utf8
                    )
                    self.trigger_error(issue)
                    return

            self.update_layer("sender", 6, LayerStatus.COMPLETE, f"{self.selected_encoding} Encoded")
            self.log("INFO", "✓", f"L6 (Presentation): Text serialized into bytes using {self.selected_encoding}.", 6)
            self.inspector_data.encoding = self.selected_encoding
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l6_receiver_decode":
            self.receiver_decoding = "ISO-8859-1" if user_value == "mismatch_latin1" else "UTF-8"

            # Encapsulate lower layers
            for lyr in [5, 4, 3, 2, 1]:
                self.update_layer("sender", lyr, LayerStatus.COMPLETE, "Encapsulated")

            self.log("INFO", "→", "Transmitting encoded bitstream across network...", None)

            def on_msg_transmitted():
                self.packets_sent += 1
                self.packets_received += 1

                for lyr in [1, 2, 3, 4, 5]:
                    self.update_layer("receiver", lyr, LayerStatus.COMPLETE, "Decapsulated")

                # Test consequence of receiver decoding choice!
                if self.receiver_decoding == "ISO-8859-1" and self.selected_encoding == "UTF-8":
                    # Classic Mojibake!
                    raw_bytes = self.raw_message.encode("utf-8")
                    mojibake_text = raw_bytes.decode("latin-1", errors="replace")

                    self.update_layer("receiver", 6, LayerStatus.ERROR, "Mojibake Mismatch!", has_error=True)
                    self.log("ERROR", "⚠", f"Consequence: Presentation Layer Mismatch! Receiver decoded UTF-8 bytes using Latin-1. Rendered garbled Mojibake: '{mojibake_text}'", 6)
                    self.render_chat_message(mojibake_text, is_corrupted=True)

                    def fix_mojibake():
                        self.receiver_decoding = "UTF-8"
                        self.update_layer("receiver", 6, LayerStatus.COMPLETE, "UTF-8 Decoded Cleanly")
                        self.update_layer("receiver", 7, LayerStatus.COMPLETE, "Delivered")
                        self.log("SUCCESS", "✓", "Repaired: Receiver Presentation Layer aligned to UTF-8. Mojibake resolved!", 6)
                        self.render_chat_message(self.raw_message, is_corrupted=False)
                        self._finish_text_mission()

                    issue = TroubleshootIssue(
                        layer_num=6,
                        title="Presentation Layer: Mojibake Character Corruption",
                        summary=f"Sender sent UTF-8, but receiver interpreted bytes as ISO-8859-1 (Latin-1). Person B received: '{mojibake_text}'.",
                        details=(
                            "This illustrates the core purpose of Layer 6 (Presentation).\n\n"
                            "Even though all network packets and bits arrived with 100% accuracy, the information is garbled because the endpoints did not agree on how to interpret the byte sequences.\n\n"
                            "In UTF-8, '¡' is two bytes (0xC2 0xA1). When Latin-1 reads those two bytes, it treats them as two separate characters ('Ã' and '¡'), creating Mojibake."
                        ),
                        options=[
                            RepairOption(
                                id="align_utf8",
                                title="Align Receiver to UTF-8 Decoder (Recommended)",
                                description="Decode the multi-byte sequences using UTF-8.",
                                is_correct=True,
                                feedback="Correct! Bytes are recombined into the original Spanish characters."
                            ),
                            RepairOption(
                                id="ignore_garble",
                                title="Leave text as Mojibake",
                                description="Expect recipient to guess the original words.",
                                is_correct=False,
                                feedback="Incorrect. Text is unreadable."
                            )
                        ],
                        on_repair_success=fix_mojibake
                    )
                    self.trigger_error(issue)
                    return

                # Clean decode
                self.update_layer("receiver", 6, LayerStatus.COMPLETE, "UTF-8 Decoded")
                self.update_layer("receiver", 7, LayerStatus.COMPLETE, "Message Delivered")
                self.render_chat_message(self.raw_message, is_corrupted=False)
                self.log("SUCCESS", "✓", f"Person B received and cleanly decoded: '{self.raw_message}'", 7)
                self._finish_text_mission()

            if self.cb_network_animate:
                self.cb_network_animate("Person A", "Person B", "PACKET", "Chat Text", False, on_msg_transmitted)
            else:
                on_msg_transmitted()

    def _finish_text_mission(self):
        self.complete_mission({
            "Original User Message": self.raw_message,
            "Presentation Encoding": "UTF-8 (Variable-Length Unicode)",
            "Decisions Made": self.decisions_made,
            "Errors Diagnosed & Fixed": self.errors_repaired,
            "Key Lesson": "Layer 6 (Presentation) governs data interpretation. Lower layers can deliver 100% of packets, but if character representations disagree, the application receives Mojibake."
        })

    def _advance_to_next_stage(self):
        self.current_stage_index += 1
        self.present_current_stage()
