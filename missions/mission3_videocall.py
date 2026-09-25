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
            title="Hacer una videollamada",
            icon="📹",
            subtitle="Establecer comunicación de audio/video en vivo con decisiones de latencia",
            objective="Conectar una videollamada en tiempo real. Elige códecs, negocia el control de sesión y evalúa si TCP o UDP soporta mejor una conversación interactiva.",
            concepts=[
                "Protocolo de transporte en tiempo real (RTP/UDP)",
                "Compromiso entre latencia y confiabilidad",
                "Bloqueo por orden de llegada en TCP (Head-of-Line)",
                "Compresión de video con códec (L6 H.264)",
                "Señalización de sesión (SIP/SDP en L5)"
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

        tk.Label(top, text="📹 Sesión de videollamada en vivo", font=theme.FONT_SUBTITLE, fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK).pack(side=tk.LEFT)

        self.lbl_quality = tk.Label(top, text="Calidad: EN ESPERA", font=theme.FONT_BODY_BOLD, fg=theme.TEXT_MUTED, bg=theme.BG_DARK)
        self.lbl_quality.pack(side=tk.RIGHT, padx=8)

        self.lbl_latency = tk.Label(top, text="Latencia: -- ms | Variación: -- ms", font=theme.FONT_SMALL, fg=theme.TEXT_SECONDARY, bg=theme.BG_DARK)
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
        c.create_text(20, 25, text="👤 Persona A (video local - 720p)", font=theme.FONT_SMALL, fill=theme.TEXT_MUTED, anchor=tk.W)
        c.create_oval(half_w/2 - 25, h/2 - 35, half_w/2 + 25, h/2 + 15, fill="#3b82f6", outline="")
        c.create_text(half_w/2, h/2 - 10, text="👤", font=(theme.FONT_FAMILY, 24))
        c.create_text(half_w/2, h - 25, text="Audio: 🎙 ACTIVO (códec Opus)", font=theme.FONT_TINY, fill=theme.COLOR_SUCCESS)

        # Person B (Remote Stream Received)
        c.create_rectangle(half_w + 5, 10, w - 10, h - 10, fill="#222733", outline=theme.OSI_COLORS[3], width=1)
        c.create_text(half_w + 15, 25, text="👤 Persona B (flujo remoto recibido)", font=theme.FONT_SMALL, fill=theme.TEXT_MUTED, anchor=tk.W)

        cx = half_w + (w - half_w)/2
        if state == "STANDBY":
            c.create_text(cx, h/2, text="Llamada no iniciada (esperando decisiones)", font=theme.FONT_BODY, fill=theme.TEXT_MUTED)
        elif state == "UDP_GOOD":
            c.create_oval(cx - 25, h/2 - 35, cx + 25, h/2 + 15, fill="#10b981", outline="")
            c.create_text(cx, h/2 - 10, text="👤", font=(theme.FONT_FAMILY, 24))
            c.create_text(cx, h - 25, text="✓ Reproducción fluida en tiempo real (30 FPS, 22 ms)", font=theme.FONT_TINY, fill=theme.COLOR_SUCCESS)
        elif state == "UDP_GLITCH":
            c.create_oval(cx - 25, h/2 - 35, cx + 25, h/2 + 15, fill="#059669", outline="")
            c.create_text(cx, h/2 - 10, text="👤", font=(theme.FONT_FAMILY, 24))
            c.create_rectangle(cx - 20, h/2 - 15, cx + 20, h/2 - 5, fill="#f59e0b", outline="")
            c.create_text(cx, h - 25, text="⚠ Fotograma n.º 3 perdido -> omitido (¡llamada intacta!)", font=theme.FONT_TINY, fill=theme.COLOR_WARNING)
        elif state == "TCP_FROZEN":
            c.create_oval(cx - 25, h/2 - 35, cx + 25, h/2 + 15, fill="#dc2626", outline="")
            c.create_text(cx, h/2 - 10, text="❄️", font=(theme.FONT_FAMILY, 24))
            c.create_text(cx, h/2 + 25, text="TRANSMISIÓN CONGELADA (Retardo: 1,45 s)", font=theme.FONT_SMALL, fill=theme.COLOR_ERROR)
            c.create_text(cx, h - 25, text="✗ Bloqueo por orden de llegada: esperando la retransmisión", font=theme.FONT_TINY, fill=theme.COLOR_ERROR)

    def load_initial_stage(self):
        self.current_stage_index = 0
        self.stages = [
            # Stage 0: L6 Codec Compression
            StageDecision(
                stage_id="l6_codec",
                layer_num=6,
                title="Capa de Presentación — Codificación y compresión de video",
                prompt="La webcam captura video sin comprimir a 720p y 30 fps. ¿Cómo debe codificar la capa de presentación los datos de video antes de transmitirlos?",
                explanation="El video RGB sin comprimir a 720p requiere más de 660 Mbps de ancho de banda. Los códecs de video (como H.264) comprimen el video más de un 98 % para que quepa en conexiones de red estándar.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "h264",
                        "title": "H.264 (AVC) — Compresión con pérdida en tiempo real (~2 Mbps)",
                        "desc": "Comprime el video mediante codificación predictiva entre fotogramas, lo que permite una transmisión fluida por Internet."
                    },
                    {
                        "id": "raw_rgb",
                        "title": "Mapas de bits sin comprimir (RGB24 — 660 Mbps)",
                        "desc": "Envía el valor de cada píxel sin compresión."
                    }
                ],
                default_value="h264",
                button_label="Aplicar códec de presentación ▶"
            ),
            # Stage 1: L4 Transport Decision: UDP vs TCP
            StageDecision(
                stage_id="l4_multimedia",
                layer_num=4,
                title="Capa de Transporte — Baja latencia vs entrega ordenada",
                prompt="Para una conversación interactiva de voz y video bidireccional, ¿qué protocolo de la capa de Transporte resulta más adecuado?",
                explanation="En las conversaciones humanas, un fotograma de audio o video retrasado no tiene utilidad. Si se pierde un paquete, ¿es mejor congelar la llamada para retransmitirlo u omitirlo para mantenerla en vivo?",
                input_type="CHOICE",
                options=[
                    {
                        "id": "udp",
                        "title": "UDP con RTP (Protocolo de transporte en tiempo real) — Baja latencia",
                        "desc": "Entrega los paquetes inmediatamente sin retardos de retransmisión. Los paquetes perdidos ocasionales se omiten."
                    },
                    {
                        "id": "tcp",
                        "title": "TCP — Entrega ordenada garantizada y retransmisión",
                        "desc": "Obliga al receptor a congelar la reproducción cada vez que se pierde un paquete hasta que termina la retransmisión."
                    }
                ],
                default_value="udp",
                button_label="Seleccionar protocolo de transporte ▶"
            ),
            # Stage 2: L5 Session Signaling
            StageDecision(
                stage_id="l5_session",
                layer_num=5,
                title="Capa de Sesión — Señalización de llamada y control de diálogo",
                prompt="¿Qué protocolo de señalización de la capa de Sesión debe establecer los parámetros del canal multimedia (oferta/respuesta de medios SDP) entre Persona A y Persona B?",
                explanation="Los protocolos de la capa de Sesión establecen, mantienen y terminan sesiones interactivas. SIP (Protocolo de Inicio de Sesión) es el estándar de telecomunicaciones.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "sip",
                        "title": "SIP / SDP (Protocolos de Inicio y Descripción de Sesión — puerto 5060)",
                        "desc": "Intercambia las capacidades de audio y video (códecs, puertos) y establece un canal de medios dúplex."
                    },
                    {
                        "id": "ftp_control",
                        "title": "Control FTP (puerto 21)",
                        "desc": "Canal de control para transferencia de archivos."
                    }
                ],
                default_value="sip",
                button_label="Establecer sesión de comunicación ▶"
            ),
            # Stage 3: Live Media Stream & Consequence Test
            StageDecision(
                stage_id="l4_stream_consequence",
                layer_num=4,
                title="Transmisión y pérdida de paquete — Consecuencia durante una llamada en vivo",
                prompt="Se transmiten fotogramas multimedia en vivo por la red. Un enrutador descarta el fotograma n.º 3. Observa las consecuencias:",
                explanation="Observa cómo se comporta el protocolo de Transporte elegido (TCP frente a UDP) cuando la congestión del enrutador descarta un fotograma de video.",
                input_type="ACTION",
                options=[],
                button_label="Transmitir fotogramas de video y observar la llamada ▶"
            )
        ]

        self.present_current_stage()

    def submit_user_decision(self, user_value: str, extra_data: Optional[Dict[str, Any]] = None):
        super().submit_user_decision(user_value, extra_data)
        stage = self.stages[self.current_stage_index]

        if stage.stage_id == "l6_codec":
            if user_value == "raw_rgb":
                # Consequence: Bandwidth overflow!
                self.update_layer("sender", 6, LayerStatus.ERROR, "Desbordamiento del ancho de banda (660 Mbps > 100 Mbps)", has_error=True)
                self.log("ERROR", "⚠", "Consecuencia: ¡el video sin comprimir genera 660 Mbps de datos! La capacidad de subida es de solo 100 Mbps. ¡El enlace queda completamente saturado y se bloquea!", 6)

                def fix_codec():
                    self.selected_codec = "H.264"
                    self.update_layer("sender", 6, LayerStatus.COMPLETE, "H.264 (flujo de 2 Mbps)")
                    self.log("SUCCESS", "✓", "Reparación: se habilitó la compresión con pérdida H.264. El flujo se redujo a unos 2 Mbps.", 6)
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=6,
                    title="Capa de presentación: desbordamiento de la capacidad del enlace",
                    summary="El video 720p sin comprimir genera 660 Mbps de tráfico y supera el límite de ancho de banda de la tarjeta de red.",
                    details=(
                        "La capa 6 (Presentación) es responsable de la compresión de datos.\n\n"
                        "Sin compresión mediante códec (por ejemplo, H.264, VP9 o AV1), transmitir 1280x720 píxeles a 30 fps requiere:\n"
                        "1280 * 720 * 24 bits * 30 fps = ~663 Mbps.\n\n"
                        "Los códecs modernos usan transformadas discretas del coseno y estimación de movimiento para comprimir el video un 98 % hasta 2 Mbps sin una pérdida de calidad perceptible."
                    ),
                    options=[
                        RepairOption(
                            id="use_h264",
                            title="Comprimir con el códec H.264 (recomendado)",
                            description="Codificar los fotogramas con el estándar H.264 para transmisión en tiempo real por Internet.",
                            is_correct=True,
                            feedback="¡Correcto! El ancho de banda baja a 2 Mbps, una capacidad que el enlace puede soportar sin problema."
                        ),
                        RepairOption(
                            id="keep_raw",
                            title="Comprar una línea de fibra dedicada de 10 Gbps",
                            description="Gastar miles de dólares en fibra empresarial.",
                            is_correct=False,
                            feedback="Impracticable e innecesario. Las aplicaciones de video siempre usan códecs de video."
                        )
                    ],
                    on_repair_success=fix_codec
                )
                self.trigger_error(issue)
                return

            self.selected_codec = "H.264"
            self.update_layer("sender", 6, LayerStatus.COMPLETE, "H.264 comprimido (2 Mbps)")
            self.log("INFO", "✓", "L6 (Presentación): video codificado con H.264 AVC (Perfil alto) y audio codificado con Opus.", 6)
            self.inspector_data.encoding = "H.264 / Opus"
            self.inspector_data.compression = "Vectores de movimiento DCT con pérdida"
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l4_multimedia":
            self.selected_protocol = "UDP" if user_value == "udp" else "TCP"
            if self.selected_protocol == "TCP":
                self.log("WARNING", "⚠", "El usuario eligió TCP: ¡advertencia! La entrega estricta en orden provocará un bloqueo por orden de llegada (Head-of-Line) si se pierden paquetes.", 4)
                self.update_layer("sender", 4, LayerStatus.ACTIVE, "TCP (retransmisión habilitada)")
            else:
                self.log("INFO", "✓", "El usuario eligió UDP: Protocolo de transporte en tiempo real (RTP) sobre UDP. Optimizado para conversaciones interactivas.", 4)
                self.update_layer("sender", 4, LayerStatus.ACTIVE, "UDP / RTP (sin retardo de retransmisión)")

            self.inspector_data.transport_protocol = f"{self.selected_protocol} (puerto RTP 5004)"
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l5_session":
            if user_value == "ftp_control":
                self.update_layer("sender", 5, LayerStatus.ERROR, "Protocolo de sesión incompatible (FTP)", has_error=True)
                self.log("ERROR", "⚠", "Consecuencia: ¡el control FTP no puede iniciar ni negociar códecs multimedia para videollamadas en tiempo real!", 5)

                def fix_session():
                    self.update_layer("sender", 5, LayerStatus.COMPLETE, "Sesión SIP/SDP activa")
                    self.log("SUCCESS", "✓", "Reparación: se negoció SIP INVITE. Canal de medios RTP dúplex abierto.", 5)
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=5,
                    title="Incompatibilidad del protocolo de la capa de Sesión",
                    summary="FTP es un protocolo de transferencia de archivos. No admite la negociación de sesiones de audio/video en tiempo real.",
                    details=(
                        "En VoIP y videoconferencia, el Protocolo de Inicio de Sesión (SIP) se utiliza en la capa 5 para:\n"
                        "• Localizar los extremos\n"
                        "• Negociar los tipos de medios mediante SDP (Protocolo de Descripción de Sesión)\n"
                        "• Hacer sonar y establecer las conexiones de llamada\n"
                        "• Finalizar las llamadas cuando se cuelga."
                    ),
                    options=[
                        RepairOption(
                            id="use_sip",
                            title="Negociar la sesión con SIP / SDP (recomendado)",
                            description="Usar el protocolo de señalización VoIP estándar.",
                            is_correct=True,
                            feedback="¡Correcto! SIP INVITE estableció una sesión de medios dúplex."
                        ),
                        RepairOption(
                            id="skip_session",
                            title="Continuar sin seguimiento de sesión",
                            description="Transmitir sin negociar los códecs.",
                            is_correct=False,
                            feedback="Incorrecto. El receptor no sabrá qué códec utilizar ni en qué puerto escuchar."
                        )
                    ],
                    on_repair_success=fix_session
                )
                self.trigger_error(issue)
                return

            self.update_layer("sender", 5, LayerStatus.COMPLETE, "Sesión SIP/SDP activa")
            self.log("INFO", "✓", "L5 (Sesión): diálogo SIP establecido. SDP negoció H.264 a 720p.", 5)
            self._advance_to_next_stage()

        elif stage.stage_id == "l4_stream_consequence":
            # Animate video stream packets and test consequence!
            self.log("INFO", "→", f"Transmitiendo fotogramas de video por la red con {self.selected_protocol}...", None)

            def on_stream_done():
                self.packets_sent += 10
                self.packets_received += 9  # 1 packet dropped

                if self.selected_protocol == "TCP":
                    # Severe freeze consequence!
                    self.latency_ms = 1450
                    self.jitter_ms = 320
                    self.call_quality = "MALA (congelamiento: 1,45 s)"
                    if self.lbl_quality:
                        self.lbl_quality.config(text=f"Calidad: {self.call_quality}", fg=theme.COLOR_ERROR)
                    if self.lbl_latency:
                        self.lbl_latency.config(text=f"Latencia: {self.latency_ms} ms | Variación: {self.jitter_ms} ms", fg=theme.COLOR_ERROR)
                    self.draw_video_call("TCP_FROZEN")

                    self.update_layer("receiver", 4, LayerStatus.ERROR, "TCP detenido (bloqueo por orden de llegada)", has_error=True)
                    self.log("ERROR", "⚠", "Consecuencia de elegir TCP: cuando se descartó el fotograma n.º 3, ¡TCP detuvo la reproducción! Todos los fotogramas más nuevos quedan bloqueados mientras esperan la retransmisión. ¡La llamada está congelada!", 4)

                    def fix_to_udp():
                        self.selected_protocol = "UDP"
                        self.latency_ms = 22
                        self.jitter_ms = 4
                        self.call_quality = "EXCELENTE (22 ms)"
                        if self.lbl_quality:
                            self.lbl_quality.config(text=f"Calidad: {self.call_quality}", fg=theme.COLOR_SUCCESS)
                        if self.lbl_latency:
                            self.lbl_latency.config(text=f"Latencia: {self.latency_ms} ms | Variación: {self.jitter_ms} ms", fg=theme.COLOR_SUCCESS)
                        self.draw_video_call("UDP_GOOD")
                        self.log("SUCCESS", "✓", "Se cambió a UDP (RTP): el códec simplemente omite los fotogramas perdidos. ¡La latencia en tiempo real volvió a ser de 22 ms!", 4)
                        self.update_layer("receiver", 4, LayerStatus.COMPLETE, "UDP / RTP en tiempo real activo")
                        self._finish_video_mission()

                    issue = TroubleshootIssue(
                        layer_num=4,
                        title="Bloqueo por orden de llegada (Head-of-Line) en una videollamada (fallo de TCP)",
                        summary="La llamada se congeló durante 1,45 segundos porque TCP detiene el flujo para esperar las retransmisiones de los paquetes perdidos.",
                        details=(
                            "Esto demuestra por qué casi todas las aplicaciones interactivas de video/voz (Zoom, Discord, WebRTC) usan UDP.\n\n"
                            "Con TCP, si se pierde el paquete n.º 3, los paquetes n.º 4, 5 y 6 se almacenan y se retienen para la aplicación hasta que se retransmita el n.º 3.\n"
                            "En una conversación en vivo, ¡un fotograma antiguo de hace 1,5 segundos no tiene valor!\n\n"
                            "Con UDP, los paquetes que faltan simplemente se descartan, lo que permite que el códec de video interpole o avance sin penalización de latencia."
                        ),
                        options=[
                            RepairOption(
                                id="switch_udp_rtp",
                                title="Cambiar el protocolo de Transporte a UDP (RTP, recomendado)",
                                description="Eliminar los retardos de retransmisión para preservar un diálogo bidireccional fluido.",
                                is_correct=True,
                                feedback="¡Correcto! La latencia baja inmediatamente de 1450 ms a 22 ms."
                            ),
                            RepairOption(
                                id="wait_tcp_more",
                                title="Esperar a que termine la retransmisión TCP",
                                description="Mantener la conversación congelada.",
                                is_correct=False,
                                feedback="Incorrecto. Esperar la retransmisión arruina las conversaciones en tiempo real."
                            )
                        ],
                        on_repair_success=fix_to_udp
                    )
                    self.trigger_error(issue)
                    return

                # UDP success
                self.latency_ms = 24
                self.jitter_ms = 4
                self.call_quality = "EXCELENTE (24 ms)"
                if self.lbl_quality:
                    self.lbl_quality.config(text=f"Calidad: {self.call_quality}", fg=theme.COLOR_SUCCESS)
                if self.lbl_latency:
                    self.lbl_latency.config(text=f"Latencia: {self.latency_ms} ms | Variación: {self.jitter_ms} ms", fg=theme.COLOR_SUCCESS)
                self.draw_video_call("UDP_GLITCH")
                self.log("INFO", "✓", "Resiliencia de UDP: el enrutador descartó el fotograma n.º 3, pero el códec lo omitió y la llamada continuó sin interrupciones. ¡El audio y el video continuaron en vivo a 24 ms!", 4)
                self._finish_video_mission()

            if self.cb_network_animate:
                self.cb_network_animate("Person A", "Person B", "PACKET", "Fotograma de video RTP", False, on_stream_done)
            else:
                on_stream_done()

    def _finish_video_mission(self):
        for lyr in range(1, 8):
            self.update_layer("receiver", lyr, LayerStatus.COMPLETE, "Desencapsulado y transmitiendo")

        self.complete_mission({
            "Tipo de sesión": "Videollamada en tiempo real (WebRTC)",
            "Códec de video (L6)": self.selected_codec,
            "Protocolo de transporte (L4)": self.selected_protocol,
            "Latencia extremo a extremo": f"{self.latency_ms} ms",
            "Decisiones tomadas": self.decisions_made,
            "Errores diagnosticados y corregidos": self.errors_repaired,
            "Lección clave": "El multimedia interactivo requiere UDP porque la inmediatez es más importante que la confiabilidad del 100 %. El bloqueo por orden de llegada (Head-of-Line) en TCP vuelve inviable una conversación en vivo."
        })

    def _advance_to_next_stage(self):
        self.current_stage_index += 1
        self.present_current_stage()
