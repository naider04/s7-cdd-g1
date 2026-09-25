"""
Mission 1: Send a Large File
Interactive, decision-driven simulation covering:
- L7 Data Segmentation vs MTU limit
- L4 Transport Protocol (TCP vs UDP)
- L4 TCP 3-Way Handshake (SYN -> SYN-ACK -> ACK)
- L3 IP Addressing & Routing
- Handling Packet Drops: Retransmission vs UDP File Corruption
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional
from missions.base_mission import BaseMission
from models import LayerStatus, TroubleshootIssue, RepairOption, StageDecision, PacketInspectorData
from utils.helpers import format_hex_dump
import theme


class MissionFileTransfer(BaseMission):
    def __init__(self):
        super().__init__(
            mission_id=1,
            title="Enviar un archivo grande",
            icon="📁",
            subtitle="Entregar un video de 500 MB a Persona B con decisiones de confiabilidad",
            objective="Entregar 'video.mp4' (500 MB) por la red. Elige parámetros del protocolo, realiza el establecimiento de conexión de tres vías y maneja pérdidas reales de paquetes.",
            concepts=[
                "Segmentación frente a límites MTU",
                "Establecimiento de conexión TCP de tres vías (SYN/ACK)",
                "Confiabilidad: TCP vs UDP",
                "Pérdida de paquetes y retransmisión rápida",
                "Integridad de archivo extremo a extremo (MD5/FCS)"
            ]
        )
        self.selected_protocol = "TCP"  # "TCP" or "UDP"
        self.is_segmented = True
        self.chunks_received = [False] * 4
        self.retransmitted_chunk_3 = False
        self.dest_ip = "192.168.1.25"

        # UI elements
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.status_lbl: Optional[tk.Label] = None
        self.chunk_labels: List[tk.Label] = []

    def build_visual_output_ui(self, parent: tk.Widget):
        container = tk.Frame(parent, bg=theme.BG_PANEL, padx=12, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text="📁 Receptor (Persona B) - Monitor de reensamblado",
            font=theme.FONT_SUBTITLE,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_PANEL
        ).pack(anchor=tk.W, pady=(0, 6))

        file_card = tk.Frame(container, bg=theme.BG_CARD, padx=10, pady=8, bd=1, relief=tk.SOLID)
        file_card.pack(fill=tk.X, pady=4)

        self.info_lbl = tk.Label(
            file_card,
            text="Archivo objetivo: video.mp4 | Tamaño: 500 MB | Bloques: 4 (125 MB c/u)",
            font=theme.FONT_BODY,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_CARD
        )
        self.info_lbl.pack(anchor=tk.W)

        # 4 Chunk Blocks
        chunks_box = tk.Frame(container, bg=theme.BG_PANEL)
        chunks_box.pack(fill=tk.X, pady=8)

        self.chunk_labels = []
        for i in range(4):
            c_frame = tk.Frame(chunks_box, bg=theme.BG_CARD, bd=1, relief=tk.GROOVE, padx=10, pady=6)
            c_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

            tk.Label(c_frame, text=f"Bloque #{i+1}", font=theme.FONT_TINY, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack()
            lbl_st = tk.Label(c_frame, text="Esperando...", font=theme.FONT_BODY_BOLD, fg=theme.TEXT_MUTED, bg=theme.BG_CARD)
            lbl_st.pack()
            self.chunk_labels.append(lbl_st)

        # Progress bar
        self.progress_bar = ttk.Progressbar(container, orient=tk.HORIZONTAL, mode='determinate', maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=6)

        self.status_lbl = tk.Label(
            container,
            text="Esperando decisiones del usuario para iniciar la transmisión...",
            font=theme.FONT_BODY_BOLD,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PANEL
        )
        self.status_lbl.pack(anchor=tk.W)

    def load_initial_stage(self):
        """Build the interactive stages."""
        self.chunks_received = [False] * 4
        self.retransmitted_chunk_3 = False
        self.current_stage_index = 0

        self.stages = [
            # Stage 0: L7 Data Packaging
            StageDecision(
                stage_id="l7_packaging",
                layer_num=7,
                title="Capa de Aplicación — Preparación de datos",
                prompt="Persona A tiene un archivo de video de 500 MB. ¿Cómo debe prepararlo la aplicación para transmitirlo?",
                explanation="Los enlaces físicos de red no pueden transmitir un flujo arbitrario de 500 MB en una sola pieza debido a los límites de hardware de la Unidad de Transmisión Máxima (MTU), normalmente 1500 bytes por marco Ethernet.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "segment",
                        "title": "Segmentar en bloques secuenciales discretos (4 bloques de 125 MB)",
                        "desc": "Divide el archivo de 500 MB en bloques numerados y manejables que se ajustan a los límites de MTU de la red."
                    },
                    {
                        "id": "monolithic",
                        "title": "Enviar los 500 MB completos como un único paquete masivo sin segmentar",
                        "desc": "Intenta enviar los 500 MB completos sin dividirlos. (¡Se probarán los límites de la red!)"
                    }
                ],
                default_value="segment",
                button_label="Encapsular capa 7 ▶"
            ),
            # Stage 1: L4 Protocol Decision
            StageDecision(
                stage_id="l4_protocol",
                layer_num=4,
                title="Capa de Transporte — Selección de protocolo",
                prompt="¿Qué protocolo de transporte debe gestionar la entrega de este video de 500 MB?",
                explanation="TCP garantiza una entrega ordenada y completa mediante acuses de recibo, mientras que UDP envía datagramas sin verificar la entrega ni retransmitir pérdidas.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "tcp",
                        "title": "TCP (Protocolo de control de transmisión) — Confiable y orientado a conexión",
                        "desc": "Establece una conexión, numera cada segmento, solicita acuses de recibo y retransmite los paquetes perdidos."
                    },
                    {
                        "id": "udp",
                        "title": "UDP (Protocolo de datagramas de usuario) — Sin conexión y rápido",
                        "desc": "Envía datagramas inmediatamente sin sobrecarga de conexión ni retransmisiones."
                    }
                ],
                default_value="tcp",
                button_label="Configurar protocolo de transporte ▶"
            ),
            # Stage 2: Handshake / Connection
            StageDecision(
                stage_id="l4_handshake",
                layer_num=4,
                title="Capa de Transporte — Establecimiento de conexión",
                prompt="Para establecer una conexión de transporte confiable, Persona A debe iniciar el establecimiento de conexión de tres vías. ¿Qué bandera de control TCP debe enviarse primero?",
                explanation="El establecimiento de conexión TCP sincroniza los números de secuencia entre el emisor y el receptor antes de transmitir cualquier carga útil de datos de usuario.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "syn",
                        "title": "SYN (Sincronizar número de secuencia)",
                        "desc": "Inicia la conexión con el número de secuencia inicial ISN=1000."
                    },
                    {
                        "id": "ack",
                        "title": "ACK (Acuse de recibo)",
                        "desc": "Acusa recibo de los datos recibidos previamente (no válido antes de iniciar la conexión)."
                    },
                    {
                        "id": "fin",
                        "title": "FIN (Finalizar / Terminar)",
                        "desc": "Indica la terminación de la conexión."
                    }
                ],
                default_value="syn",
                button_label="Enviar bandera de control ▶"
            ),
            # Stage 3: L3 Addressing
            StageDecision(
                stage_id="l3_addressing",
                layer_num=3,
                title="Capa de Red — Direccionamiento IP lógico",
                prompt="Especifica la dirección IPv4 de destino de Persona B para el enrutamiento a través de los enrutadores centrales:",
                explanation="Los enrutadores de capa 3 utilizan la IP de destino del encabezado para determinar la interfaz del próximo salto a lo largo de la ruta.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "192.168.1.25",
                        "title": "192.168.1.25 (IP válida de Persona B)",
                        "desc": "Enruta el paquete hacia la interfaz de red de Persona B."
                    },
                    {
                        "id": "192.168.1.99",
                        "title": "192.168.1.99 (Equipo no asignado / incorrecto)",
                        "desc": "El equipo de destino no existe en la red local."
                    }
                ],
                default_value="192.168.1.25",
                button_label="Encapsular paquete IP y transmitir ▶"
            ),
            # Stage 4: Network Transmission & Packet Loss reaction
            StageDecision(
                stage_id="net_loss_response",
                layer_num=4,
                title="Evento de red — Manejo de pérdida en el enrutador",
                prompt="¡El búfer del enrutador central está congestionado! Se descartó el bloque n.º 3. ¿Cómo debe reaccionar Persona A?",
                explanation="En redes confiables, la pérdida de paquetes debe detectarse y resolverse para evitar la corrupción del archivo.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "retransmit",
                        "title": "Retransmitir rápidamente el bloque n.º 3 al recibir un ACK duplicado (TCP)",
                        "desc": "Reenvía el bloque n.º 3 que falta para que Persona B pueda reensamblar el archivo sin pérdida de datos."
                    },
                    {
                        "id": "skip",
                        "title": "Ignorar el bloque que falta y continuar a la siguiente etapa",
                        "desc": "Continúa sin el bloque n.º 3 (simula el comportamiento de UDP o ignora la pérdida de paquetes)."
                    }
                ],
                default_value="retransmit",
                button_label="Aplicar acción de transmisión ▶"
            ),
            # Stage 5: Final Decapsulation & Integrity Check
            StageDecision(
                stage_id="l7_verify",
                layer_num=7,
                title="Desencapsulación del receptor y verificación de integridad",
                prompt="Todos los datos recibidos llegan a Persona B. ¿Cómo debe finalizar el archivo la capa de aplicación de Persona B?",
                explanation="Cuando todas las capas se desencapsulan, la aplicación verifica el hash criptográfico contra el manifiesto original del emisor.",
                input_type="ACTION",
                options=[],
                button_label="Verificar suma de verificación MD5 y guardar video ▶"
            )
        ]

        self.present_current_stage()

    def submit_user_decision(self, user_value: str, extra_data: Optional[Dict[str, Any]] = None):
        super().submit_user_decision(user_value, extra_data)
        stage = self.stages[self.current_stage_index]

        if stage.stage_id == "l7_packaging":
            if user_value == "monolithic":
                # Consequence: MTU violation!
                self.update_layer("sender", 7, LayerStatus.ERROR, "Desbordamiento del búfer MTU (500 MB sin segmentar)", has_error=True)
                self.log("ERROR", "⚠", "Consecuencia: la Unidad de Transmisión Máxima (MTU) de Ethernet es de 1500 bytes. ¡Una carga de 500 MB sin segmentar provoca un desbordamiento inmediato del búfer!", 7)

                def fix_packaging():
                    self.is_segmented = True
                    self.update_layer("sender", 7, LayerStatus.COMPLETE, "Datos segmentados en 4 bloques (125 MB cada uno)")
                    self.log("SUCCESS", "✓", "Reparación: archivo dividido en 4 bloques discretos con etiquetas de secuencia.", 7)
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=7,
                    title="Violación del límite MTU (carga sobredimensionada)",
                    summary="Los dispositivos de red rechazan paquetes que superan el MTU (Unidad de Transmisión Máxima, normalmente 1500 bytes). Un único paquete de 500 MB no se puede transmitir.",
                    details=(
                        "Los límites de transmisión de la capa física exigen dividir los datos en segmentos.\n\n"
                        "Al transmitir conjuntos de datos grandes, las capas de Aplicación y Transporte segmentan los datos en bloques manejables.\n"
                        "Esto permite retransmitir solo los fragmentos perdidos en lugar de reenviar los 500 MB completos."
                    ),
                    options=[
                        RepairOption(
                            id="opt_segment",
                            title="Dividir en bloques discretos (recomendado)",
                            description="Dividir los 500 MB en 4 bloques numerados con seguimiento de secuencia.",
                            is_correct=True,
                            feedback="¡Correcto! La segmentación permite un enrutamiento eficiente y la recuperación de errores."
                        ),
                        RepairOption(
                            id="opt_force",
                            title="Forzar un único paquete de todos modos",
                            description="Intentar forzar un búfer sobredimensionado en el enlace.",
                            is_correct=False,
                            feedback="Incorrecto. Las tarjetas de red y los enrutadores descartarán de inmediato los paquetes que superen el MTU."
                        )
                    ],
                    on_repair_success=fix_packaging
                )
                self.trigger_error(issue)
                return

            self.is_segmented = True
            self.update_layer("sender", 7, LayerStatus.COMPLETE, "Datos segmentados (4 x 125 MB)")
            self.log("INFO", "✓", "L7 (Aplicación): 'video.mp4' dividido en 4 bloques (secuencias n.º 1 a 4).", 7)
            self.inspector_data.app_protocol = "FTP / Flujo multimedia"
            self.inspector_data.payload_text = "[video.mp4: 4 bloques; total: 524 288 000 bytes]"
            self.inspector_data.payload_hex = format_hex_dump(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42")
            self.inspector_data.raw_size_bytes = 524288000
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l4_protocol":
            self.selected_protocol = "TCP" if user_value == "tcp" else "UDP"
            if self.selected_protocol == "UDP":
                self.log("WARNING", "⚠", "El usuario eligió UDP: ¡Advertencia! UDP no garantiza la entrega, no rastrea secuencias ni retransmite paquetes perdidos.", 4)
                self.update_layer("sender", 4, LayerStatus.ACTIVE, "Datagramas UDP (no confiables)")
                self.inspector_data.transport_protocol = "UDP"
                self.inspector_data.flags = "Ninguna (sin conexión)"
                self.inspector_data.seq_num = 0
                self.notify_inspector()
                # Skip handshake stage because UDP is connectionless!
                self.current_stage_index += 1  # jump past handshake
                self._advance_to_next_stage()
            else:
                self.log("INFO", "✓", "El usuario eligió TCP: habilita números de secuencia, acuses de recibo y solicitudes automáticas de repetición (ARQ).", 4)
                self.update_layer("sender", 4, LayerStatus.ACTIVE, "TCP seleccionado (esperando el establecimiento de conexión)")
                self.inspector_data.transport_protocol = "TCP"
                self.notify_inspector()
                self._advance_to_next_stage()

        elif stage.stage_id == "l4_handshake":
            if user_value != "syn":
                self.update_layer("sender", 4, LayerStatus.ERROR, f"Bandera no válida para establecer la conexión TCP ({user_value.upper()})", has_error=True)
                self.log("ERROR", "⚠", f"Consecuencia: no se puede enviar {user_value.upper()} para iniciar la conexión. RFC 793 de TCP exige que el paquete inicial lleve la bandera SYN.", 4)

                def fix_handshake():
                    self.update_layer("sender", 4, LayerStatus.COMPLETE, "Establecimiento de conexión TCP de tres vías completado")
                    self.log("SUCCESS", "✓", "Conexión establecida: SYN enviado -> SYN-ACK recibido -> ACK enviado.", 4)
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=4,
                    title="Error de la máquina de estados de conexión TCP",
                    summary=f"No se puede abrir la conexión TCP con la bandera {user_value.upper()}. El paquete inicial debe llevar la bandera SYN.",
                    details=(
                        "Antes de transmitir datos mediante TCP, ambos extremos deben sincronizar sus números de secuencia.\n\n"
                        "El establecimiento de conexión de tres vías sigue una secuencia estricta:\n"
                        "1. El emisor envía SYN (sincronizar)\n"
                        "2. El receptor responde con SYN-ACK (sincronizar + acusar recibo)\n"
                        "3. El emisor responde con ACK (acusar recibo)\n\n"
                        "Enviar un ACK o FIN sin una conexión previa hará que el receptor descarte el paquete."
                    ),
                    options=[
                        RepairOption(
                            id="send_syn",
                            title="Enviar la bandera SYN para abrir la conexión (recomendado)",
                            description="Enviar un segmento TCP con la bandera SYN activa y el número de secuencia inicial.",
                            is_correct=True,
                            feedback="¡Correcto! El receptor responde con SYN-ACK y se establece la conexión."
                        ),
                        RepairOption(
                            id="skip_handshake",
                            title="Omitir el establecimiento de conexión y enviar los datos",
                            description="Enviar segmentos de datos inmediatamente sin conexión.",
                            is_correct=False,
                            feedback="Incorrecto. El sistema operativo receptor descartará los datos en un socket TCP no establecido."
                        )
                    ],
                    on_repair_success=fix_handshake
                )
                self.trigger_error(issue)
                return

            # Successful handshake animation
            self.log("INFO", "→", "Transmitiendo el paquete TCP SYN a Persona B...", 4)
            def on_syn_reached():
                self.log("INFO", "✓", "Persona B recibió SYN y respondió con SYN-ACK.", 4)
                self.update_layer("sender", 4, LayerStatus.COMPLETE, "Establecimiento de conexión TCP completado (ESTABLECIDA)")
                self.inspector_data.flags = "[SYN, ACK]"
                self.notify_inspector()
                self._advance_to_next_stage()

            if self.cb_network_animate:
                self.cb_network_animate("Person A", "Person B", "PACKET", "TCP SYN", False, on_syn_reached)
            else:
                on_syn_reached()

        elif stage.stage_id == "l3_addressing":
            self.dest_ip = user_value
            if self.dest_ip == "192.168.1.99":
                # Consequence: Host unreachable!
                self.update_layer("sender", 3, LayerStatus.ERROR, "ICMP: equipo inaccesible (192.168.1.99)", has_error=True)
                self.log("ERROR", "⚠", "Consecuencia: la IP de destino 192.168.1.99 no existe en la red. ¡El enrutador central descartó el marco con ICMP Destination Unreachable!", 3)

                def fix_ip():
                    self.dest_ip = "192.168.1.25"
                    self.update_layer("sender", 3, LayerStatus.COMPLETE, "IP de destino establecida en 192.168.1.25")
                    self.log("SUCCESS", "✓", "Reparación: IP de destino actualizada a 192.168.1.25 (Persona B).", 3)
                    self._transmit_initial_chunks()

                issue = TroubleshootIssue(
                    layer_num=3,
                    title="Error de enrutamiento de capa de red: equipo inaccesible",
                    summary="El paquete se dirigió a 192.168.1.99, que no tiene una entrada ARP activa ni un equipo en la red.",
                    details=(
                        "En la capa 3 (Red), el emisor debe dirigir los paquetes a la IP lógica válida del destino previsto.\n"
                        "La dirección IP real de Persona B es 192.168.1.25.\n\n"
                        "Al dirigir un paquete a una IP no asignada (192.168.1.99), falla la resolución ARP y el enrutador descarta la transmisión."
                    ),
                    options=[
                        RepairOption(
                            id="fix_dest_ip",
                            title="Establecer la IP de destino en 192.168.1.25 (Persona B)",
                            description="Usar la dirección IP verificada de Persona B.",
                            is_correct=True,
                            feedback="¡Correcto! El paquete se enruta directamente a Persona B."
                        ),
                        RepairOption(
                            id="ignore_ip",
                            title="Mantener 192.168.1.99",
                            description="Esperar que otro equipo lo reenvíe.",
                            is_correct=False,
                            feedback="Incorrecto. No existe ningún equipo en 192.168.1.99."
                        )
                    ],
                    on_repair_success=fix_ip
                )
                self.trigger_error(issue)
                return

            self.update_layer("sender", 3, LayerStatus.COMPLETE, "Enrutado a 192.168.1.25")
            self.update_layer("sender", 2, LayerStatus.COMPLETE, "Marcos Ethernet (MAC 00:1A:2B:3C:4D:5E)")
            self.update_layer("sender", 1, LayerStatus.COMPLETE, "Flujo de bits generado")
            self.log("INFO", "✓", "L3/L2/L1: encapsulado en paquetes IP y marcos Ethernet. Listo para el tránsito de red.", 3)
            self._transmit_initial_chunks()

        elif stage.stage_id == "net_loss_response":
            if user_value == "skip" or self.selected_protocol == "UDP":
                # Consequence: File corrupted!
                self.chunks_received[3] = True  # chunk 4 arrived, but 3 missing
                self._update_chunk_ui()
                self.update_layer("receiver", 4, LayerStatus.ERROR, "¡Falta el bloque n.º 3! Archivo corrupto", has_error=True)
                self.log("ERROR", "⚠", "Consecuencia: ¡se perdió el bloque n.º 3! El archivo en Persona B solo está completo al 75 % y no se puede abrir.", 4)

                def fix_to_tcp():
                    self.selected_protocol = "TCP"
                    self.retransmitted_chunk_3 = True
                    self.chunks_received[2] = True
                    self.log("SUCCESS", "✓", "Reparación: retransmisión rápida TCP; el receptor envió un ACK duplicado y el emisor retransmitió el bloque n.º 3.", 4)
                    self.update_layer("receiver", 4, LayerStatus.COMPLETE, "Los 4 bloques reensamblados (TCP)")
                    self._update_chunk_ui()
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=4,
                    title="Consecuencia de pérdida de datos (falta el bloque n.º 3)",
                    summary="Persona B no puede abrir 'video.mp4' porque el bloque n.º 3 se descartó y no se retransmitió.",
                    details=(
                        "Esto demuestra la consecuencia fundamental de elegir un protocolo:\n\n"
                        "• En transferencias UDP o sin retransmisión, los bloques perdidos dejan huecos permanentes en el archivo.\n"
                        "• En TCP, los paquetes perdidos activan ACK duplicados y provocan una retransmisión rápida para que el receptor recupere el 100 % de los datos."
                    ),
                    options=[
                        RepairOption(
                            id="repair_retransmit",
                            title="Realizar una retransmisión rápida TCP del bloque n.º 3",
                            description="Retransmitir el bloque n.º 3 que falta para reconstruir el archivo con un 100 % de integridad.",
                            is_correct=True,
                            feedback="¡Correcto! El bloque n.º 3 se retransmite y se acusa recibo."
                        ),
                        RepairOption(
                            id="repair_corrupt",
                            title="Aceptar un archivo corrupto al 75 %",
                            description="Dejar el archivo incompleto.",
                            is_correct=False,
                            feedback="Incorrecto. Las cabeceras del contenedor MP4 y los fotogramas clave están corruptos."
                        )
                    ],
                    on_repair_success=fix_to_tcp
                )
                self.trigger_error(issue)
                return

            # User chose retransmit!
            self.log("INFO", "→", "Retransmisión rápida: Persona A está reenviando el bloque n.º 3 que falta...", 4)
            def on_retrans_reached():
                self.chunks_received[2] = True
                self.chunks_received[3] = True
                self.retransmitted_chunk_3 = True
                self.log("SUCCESS", "✓", "¡El bloque n.º 3 llegó y fue verificado! Los 4 bloques están contabilizados en el búfer del receptor.", 4)
                self._update_chunk_ui()
                self.update_layer("receiver", 4, LayerStatus.COMPLETE, "Los 4 bloques reensamblados (TCP)")
                self._advance_to_next_stage()

            if self.cb_network_animate:
                self.cb_network_animate("Router", "Person B", "PACKET", "Bloque 3 (retransmisión)", False, on_retrans_reached)
            else:
                on_retrans_reached()

        elif stage.stage_id == "l7_verify":
            # Final verification
            for lyr in range(1, 8):
                self.update_layer("receiver", lyr, LayerStatus.COMPLETE, "Desencapsulado y verificado")

            self.log("SUCCESS", "✓", "Persona B: la suma de verificación MD5 (e2fc714c4727ee9395f324dd2e7f331f) coincide al 100 %. ¡'video.mp4' (500 MB) guardado!", 7)
            if self.status_lbl:
                self.status_lbl.config(text="✓ ¡Transferencia de archivos completada y verificada al 100 %! Todas las decisiones fueron correctas.", fg=theme.COLOR_SUCCESS)

            self.complete_mission({
                "Nombre del archivo": "video.mp4",
                "Tamaño total": "500 MB",
                "Protocolo usado": self.selected_protocol,
                "Establecimiento de conexión": "SYN → SYN-ACK → ACK verificado",
                "Paquetes enviados/recibidos": f"{self.packets_sent} enviados / {self.packets_received} recibidos",
                "Decisiones tomadas": self.decisions_made,
                "Errores diagnosticados y corregidos": self.errors_repaired,
                "Lección clave": "Las transferencias de archivos requieren segmentación y transporte confiable (TCP) para garantizar la retransmisión de paquetes perdidos."
            })

    def _transmit_initial_chunks(self):
        """Animate transmission of chunks 1, 2, and dropped chunk 3."""
        self.log("INFO", "→", "Transmitiendo los bloques n.º 1 y 2 por la red...", None)
        def on_c1_2_reached():
            self.chunks_received[0] = True
            self.chunks_received[1] = True
            self.packets_sent += 2
            self.packets_received += 2
            self._update_chunk_ui()

            # Now Chunk 3 drops at Router!
            self.log("WARNING", "⚠", "Búfer del enrutador central congestionado: ¡se descartó el bloque n.º 3 en tránsito!", None)
            self.packets_sent += 1
            self.packets_lost += 1

            def on_c3_dropped():
                self._update_chunk_ui()
                self._advance_to_next_stage()

            if self.cb_network_animate:
                self.cb_network_animate("Person A", "Router", "PACKET", "Bloque n.º 3", True, on_c3_dropped)
            else:
                on_c3_dropped()

        if self.cb_network_animate:
            self.cb_network_animate("Person A", "Person B", "PACKET", "Bloques n.º 1 y 2", False, on_c1_2_reached)
        else:
            on_c1_2_reached()

    def _update_chunk_ui(self):
        if not self.progress_bar or not self.chunk_labels:
            return
        rec_count = sum(1 for c in self.chunks_received if c)
        pct = (rec_count / 4) * 100
        self.progress_bar['value'] = pct

        for i, r in enumerate(self.chunks_received):
            if i < len(self.chunk_labels):
                if r:
                    self.chunk_labels[i].config(text="✓ RECIBIDO", fg=theme.COLOR_SUCCESS)
                elif self.packets_sent > (i + 1) and not r:
                    self.chunk_labels[i].config(text="✗ PERDIDO", fg=theme.COLOR_ERROR)
                else:
                    self.chunk_labels[i].config(text="Esperando...", fg=theme.TEXT_MUTED)

        if self.status_lbl:
            if rec_count == 4:
                self.status_lbl.config(text="✓ ¡Los 4 bloques fueron recibidos! Esperando verificación MD5.", fg=theme.COLOR_SUCCESS)
            elif rec_count > 0:
                self.status_lbl.config(text=f"Recibiendo bloques... {rec_count}/4 ({int(pct)} % completado)", fg=theme.TEXT_ACCENT)

    def _advance_to_next_stage(self):
        self.current_stage_index += 1
        self.present_current_stage()
