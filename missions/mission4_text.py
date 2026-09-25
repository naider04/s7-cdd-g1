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
            title="Enviar un mensaje de texto",
            icon="💬",
            subtitle="Transmitir texto multilingüe con decisiones de codificación",
            objective="Escribe un mensaje con acentos o emojis. Elige codificación y cifrado, y observa qué pasa cuando los extremos no coinciden en la representación de datos.",
            concepts=[
                "Representación de datos en capa de presentación (L6)",
                "Codificaciones de caracteres (UTF-8 multibyte vs ASCII de 7 bits)",
                "Desajuste de codificación y mojibake (Latin-1 vs UTF-8)",
                "Diferencia entre codificación y cifrado",
                "Reconstrucción de mensajería extremo a extremo"
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

        tk.Label(top, text="💬 Persona B - Mensajería del teléfono", font=theme.FONT_SUBTITLE, fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK).pack(side=tk.LEFT)

        self.status_chat_lbl = tk.Label(top, text="Esperando mensaje...", font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_DARK)
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
        tk.Label(self.chat_bubble_box, text="Aún no se recibieron mensajes. Envía decisiones para transmitir texto.", font=theme.FONT_BODY, fg=theme.TEXT_MUTED, bg="#0d1117").pack(pady=40)

    def render_chat_message(self, text: str, is_corrupted: bool = False):
        if not self.chat_bubble_box:
            return
        for w in self.chat_bubble_box.winfo_children():
            w.destroy()

        bubble = tk.Frame(self.chat_bubble_box, bg="#1e293b" if not is_corrupted else "#451a1a", padx=12, pady=10, bd=1, relief=tk.SOLID)
        bubble.pack(anchor=tk.W, pady=10)

        sender_lbl = tk.Label(bubble, text="Persona A", font=theme.FONT_BODY_BOLD, fg=theme.TEXT_ACCENT, bg=bubble['bg'])
        sender_lbl.pack(anchor=tk.W)

        msg_lbl = tk.Label(bubble, text=text, font=(theme.FONT_FAMILY, 13), fg=theme.COLOR_ERROR if is_corrupted else theme.TEXT_PRIMARY, bg=bubble['bg'])
        msg_lbl.pack(anchor=tk.W, pady=4)

        meta = tk.Frame(bubble, bg=bubble['bg'])
        meta.pack(fill=tk.X)

        if is_corrupted:
            tk.Label(meta, text="⚠ Fallo de codificación mojibake: bytes incompatibles", font=theme.FONT_TINY, fg=theme.COLOR_ERROR, bg=bubble['bg']).pack(side=tk.LEFT)
        else:
            tk.Label(meta, text="✓✓ Entregado y decodificado correctamente (UTF-8)", font=theme.FONT_TINY, fg=theme.COLOR_SUCCESS, bg=bubble['bg']).pack(side=tk.LEFT)

    def load_initial_stage(self):
        self.current_stage_index = 0
        self.stages = [
            # Stage 0: L7 Custom Message Typing
            StageDecision(
                stage_id="l7_text_input",
                layer_num=7,
                title="Capa de Aplicación — Redactar mensaje",
                prompt="Escribe el mensaje de texto que Persona A quiere transmitir a Persona B (incluye acentos o emojis para probar la compatibilidad con Unicode):",
                explanation="La interfaz de usuario de la capa 7 captura la entrada humana como cadenas de caracteres abstractas.",
                input_type="TEXT_INPUT",
                default_value=self.raw_message,
                input_label="Texto del mensaje:",
                button_label="Capturar texto y continuar a la capa 6 ▶"
            ),
            # Stage 1: L6 Character Encoding Choice
            StageDecision(
                stage_id="l6_encoding",
                layer_num=6,
                title="Capa de Presentación — Codificación de caracteres",
                prompt="¿Cómo debe serializar la capa 6 los caracteres de texto en bytes binarios?",
                explanation="La codificación asigna caracteres humanos a puntos de código binarios. ASCII utiliza 7 bits (128 caracteres ingleses), mientras que UTF-8 admite más de 149 000 caracteres internacionales.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "utf8",
                        "title": "UTF-8 (Unicode de longitud variable — de 1 a 4 bytes por carácter)",
                        "desc": "Admite todos los idiomas, acentos españoles (¡, á, í, ¿) y emojis."
                    },
                    {
                        "id": "ascii",
                        "title": "ASCII (estándar de 7 bits — valores de 0 a 127)",
                        "desc": "Codificación tradicional de 7 bits para caracteres básicos. Los caracteres no ASCII producen errores de codificación."
                    }
                ],
                default_value="utf8",
                button_label="Aplicar formato de codificación ▶"
            ),
            # Stage 2: L6 Receiver Decoding Mode
            StageDecision(
                stage_id="l6_receiver_decode",
                layer_num=6,
                title="Capa de Presentación — Interpretación del receptor",
                prompt="¿Qué estándar de decodificación debe usar la capa de Presentación de Persona B para reconstruir los bytes recibidos?",
                explanation="Si el emisor y el receptor no coinciden en la representación, los valores de los bytes se asignarán a glifos incorrectos y se producirá mojibake.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "match_utf8",
                        "title": "Decodificador UTF-8 (interpretación coincidente)",
                        "desc": "Analiza correctamente las secuencias de varios bytes y las convierte en los caracteres originales."
                    },
                    {
                        "id": "mismatch_latin1",
                        "title": "Decodificador ISO-8859-1 Latin-1 (desajuste de codificación: ¡produce mojibake!)",
                        "desc": "Interpreta cada byte individual de una secuencia UTF-8 como un carácter latino distinto y altera el texto."
                    }
                ],
                default_value="match_utf8",
                button_label="Transmitir por la red y decodificar ▶"
            )
        ]

        self.present_current_stage()

    def submit_user_decision(self, user_value: str, extra_data: Optional[Dict[str, Any]] = None):
        super().submit_user_decision(user_value, extra_data)
        stage = self.stages[self.current_stage_index]

        if stage.stage_id == "l7_text_input":
            self.raw_message = user_value.strip() or "¡Hola María! ¿Cómo estás? 🚀"
            self.update_layer("sender", 7, LayerStatus.COMPLETE, f"Capturado: '{self.raw_message[:20]}...'")
            self.log("INFO", "✓", f"L7 (Aplicación): texto del mensaje capturado: '{self.raw_message}'", 7)
            self.inspector_data.app_protocol = "Mensaje instantáneo JSON"
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
                    self.update_layer("sender", 6, LayerStatus.ERROR, "Error de codificación UnicodeEncodeError al usar ASCII", has_error=True)
                    self.log("ERROR", "⚠", f"Consecuencia: ASCII es una codificación de 7 bits (0-127). ¡El mensaje '{self.raw_message}' contiene caracteres no ASCII que no se pueden representar en ASCII!", 6)

                    def fix_to_utf8():
                        self.selected_encoding = "UTF-8"
                        self.update_layer("sender", 6, LayerStatus.COMPLETE, "UTF-8 codificado")
                        self.log("SUCCESS", "✓", "Reparación: se cambió a UTF-8; Unicode de varios bytes admite todos los caracteres internacionales y los emojis.", 6)
                        self._advance_to_next_stage()

                    issue = TroubleshootIssue(
                        layer_num=6,
                        title="Capa de Presentación: conjunto de caracteres incompatible (ASCII)",
                        summary="El texto contiene puntos de código no ASCII (acentos españoles y emojis). ASCII solo define 128 puntos de código, con valores de 0 a 127.",
                        details=(
                            f"La cadena de entrada contiene caracteres como '¡', 'á', 'í', '¿' o '🚀'.\n\n"
                            "ASCII usa 7 bits por carácter (de 0 a 127). Cualquier carácter con un valor superior a 127 no se puede serializar en bytes ASCII sin perder datos ni provocar una excepción.\n\n"
                            "UTF-8 es una codificación de 8 bits y longitud variable que utiliza dinámicamente de 1 a 4 bytes por carácter, y admite todos los idiomas escritos y símbolos humanos."
                        ),
                        options=[
                            RepairOption(
                                id="fix_utf8",
                                title="Cambiar la capa de Presentación a UTF-8 (recomendado)",
                                description="Codificar el texto mediante Unicode UTF-8 de longitud variable.",
                                is_correct=True,
                                feedback="¡Correcto! UTF-8 codifica sin problemas los acentos españoles y los emojis."
                            ),
                            RepairOption(
                                id="strip_chars",
                                title="Eliminar todos los acentos y emojis para forzar ASCII",
                                description="Modificar el texto para eliminar los caracteres no ASCII.",
                                is_correct=False,
                                feedback="¡Incorrecto! Los protocolos de red deben admitir los datos del usuario sin eliminar su significado."
                            )
                        ],
                        on_repair_success=fix_to_utf8
                    )
                    self.trigger_error(issue)
                    return

            self.update_layer("sender", 6, LayerStatus.COMPLETE, f"{self.selected_encoding} codificado")
            self.log("INFO", "✓", f"L6 (Presentación): texto serializado en bytes usando {self.selected_encoding}.", 6)
            self.inspector_data.encoding = self.selected_encoding
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l6_receiver_decode":
            self.receiver_decoding = "ISO-8859-1" if user_value == "mismatch_latin1" else "UTF-8"

            # Encapsulate lower layers
            for lyr in [5, 4, 3, 2, 1]:
                self.update_layer("sender", lyr, LayerStatus.COMPLETE, "Encapsulado")

            self.log("INFO", "→", "Transmitiendo el flujo de bits codificado por la red...", None)

            def on_msg_transmitted():
                self.packets_sent += 1
                self.packets_received += 1

                for lyr in [1, 2, 3, 4, 5]:
                    self.update_layer("receiver", lyr, LayerStatus.COMPLETE, "Desencapsulado")

                # Test consequence of receiver decoding choice!
                if self.receiver_decoding == "ISO-8859-1" and self.selected_encoding == "UTF-8":
                    # Classic Mojibake!
                    raw_bytes = self.raw_message.encode("utf-8")
                    mojibake_text = raw_bytes.decode("latin-1", errors="replace")

                    self.update_layer("receiver", 6, LayerStatus.ERROR, "¡Desajuste de mojibake!", has_error=True)
                    self.log("ERROR", "⚠", f"Consecuencia: ¡desajuste de la capa de Presentación! El receptor decodificó los bytes UTF-8 usando Latin-1. Se mostró mojibake ilegible: '{mojibake_text}'", 6)
                    self.render_chat_message(mojibake_text, is_corrupted=True)

                    def fix_mojibake():
                        self.receiver_decoding = "UTF-8"
                        self.update_layer("receiver", 6, LayerStatus.COMPLETE, "UTF-8 decodificado correctamente")
                        self.update_layer("receiver", 7, LayerStatus.COMPLETE, "Entregado")
                        self.log("SUCCESS", "✓", "Reparación: la capa de Presentación del receptor se alineó con UTF-8. ¡Mojibake resuelto!", 6)
                        self.render_chat_message(self.raw_message, is_corrupted=False)
                        self._finish_text_mission()

                    issue = TroubleshootIssue(
                        layer_num=6,
                        title="Capa de Presentación: corrupción de caracteres por mojibake",
                        summary=f"El emisor envió UTF-8, pero el receptor interpretó los bytes como ISO-8859-1 (Latin-1). Persona B recibió: '{mojibake_text}'.",
                        details=(
                            "Esto ilustra el propósito fundamental de la capa 6 (Presentación).\n\n"
                            "Aunque todos los paquetes y bits de red llegaron con un 100 % de precisión, la información está ilegible porque los extremos no se pusieron de acuerdo sobre cómo interpretar las secuencias de bytes.\n\n"
                            "En UTF-8, '¡' ocupa dos bytes (0xC2 0xA1). Cuando Latin-1 lee esos dos bytes, los trata como dos caracteres distintos ('Ã' y '¡'), lo que produce mojibake."
                        ),
                        options=[
                            RepairOption(
                                id="align_utf8",
                                title="Alinear el receptor con el decodificador UTF-8 (recomendado)",
                                description="Decodificar las secuencias de varios bytes mediante UTF-8.",
                                is_correct=True,
                                feedback="¡Correcto! Los bytes se recombinan para formar los caracteres españoles originales."
                            ),
                            RepairOption(
                                id="ignore_garble",
                                title="Dejar el texto como mojibake",
                                description="Esperar que el destinatario adivine las palabras originales.",
                                is_correct=False,
                                feedback="Incorrecto. El texto es ilegible."
                            )
                        ],
                        on_repair_success=fix_mojibake
                    )
                    self.trigger_error(issue)
                    return

                # Clean decode
                self.update_layer("receiver", 6, LayerStatus.COMPLETE, "UTF-8 decodificado")
                self.update_layer("receiver", 7, LayerStatus.COMPLETE, "Mensaje entregado")
                self.render_chat_message(self.raw_message, is_corrupted=False)
                self.log("SUCCESS", "✓", f"Persona B recibió y decodificó correctamente: '{self.raw_message}'", 7)
                self._finish_text_mission()

            if self.cb_network_animate:
                self.cb_network_animate("Person A", "Person B", "PACKET", "Mensaje de texto", False, on_msg_transmitted)
            else:
                on_msg_transmitted()

    def _finish_text_mission(self):
        self.complete_mission({
            "Mensaje original del usuario": self.raw_message,
            "Codificación de presentación": "UTF-8 (Unicode de longitud variable)",
            "Decisiones tomadas": self.decisions_made,
            "Errores diagnosticados y corregidos": self.errors_repaired,
            "Lección clave": "La capa 6 (Presentación) gobierna la interpretación de datos. Las capas inferiores pueden entregar el 100 % de los paquetes, pero si la representación de caracteres no coincide, la aplicación recibe mojibake."
        })

    def _advance_to_next_stage(self):
        self.current_stage_index += 1
        self.present_current_stage()
