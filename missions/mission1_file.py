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
            objective="Entregar 'video.mp4' (500 MB) por la red. Elige parámetros del protocolo, realiza el three-way handshake y maneja pérdidas reales de paquetes.",
            concepts=[
                "Segmentación vs límites MTU",
                "Handshake TCP de 3 vías (SYN/ACK)",
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
                explanation="Physical network links cannot transmit an arbitrary 500 MB stream in one piece due to Maximum Transmission Unit (MTU) hardware limits (typically 1500 bytes per Ethernet frame).",
                input_type="CHOICE",
                options=[
                    {
                        "id": "segment",
                        "title": "Segment into discrete sequential chunks (4 chunks of 125 MB)",
                        "desc": "Divides the 500 MB file into manageable, numbered chunks that fit network MTU limits."
                    },
                    {
                        "id": "monolithic",
                        "title": "Send entire 500 MB as one single massive unsegmented packet",
                        "desc": "Tries to blast the entire 500 MB without splitting. (Will test network limits!)"
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
                explanation="TCP guarantees ordered and complete delivery via acknowledgments, while UDP sends datagrams without verifying delivery or retransmitting losses.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "tcp",
                        "title": "TCP (Transmission Control Protocol) — Reliable & Connection-Oriented",
                        "desc": "Establishes a connection, numbers every segment, requests acknowledgments, and retransmits lost packets."
                    },
                    {
                        "id": "udp",
                        "title": "UDP (User Datagram Protocol) — Connectionless & Fast",
                        "desc": "Sends datagrams immediately without connection overhead or retransmissions."
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
                prompt="To establish a reliable transport connection, Person A must begin the 3-Way Handshake. Which TCP control flag must be sent first?",
                explanation="The TCP handshake synchronizes sequence numbers between sender and receiver before any user data payload is transmitted.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "syn",
                        "title": "SYN (Synchronize Sequence Number)",
                        "desc": "Initiates connection with initial sequence number ISN=1000."
                    },
                    {
                        "id": "ack",
                        "title": "ACK (Acknowledgment)",
                        "desc": "Acknowledges previously received data (invalid before connection is initiated)."
                    },
                    {
                        "id": "fin",
                        "title": "FIN (Finish / Terminate)",
                        "desc": "Signals connection termination."
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
                prompt="Specify Person B's destination IPv4 address for routing across core routers:",
                explanation="Layer 3 routers use the destination IP header to determine the next-hop interface along the path.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "192.168.1.25",
                        "title": "192.168.1.25 (Valid IP of Person B)",
                        "desc": "Routes packet to Person B's network interface."
                    },
                    {
                        "id": "192.168.1.99",
                        "title": "192.168.1.99 (Unassigned / Wrong Host)",
                        "desc": "Destination host does not exist on the local network."
                    }
                ],
                default_value="192.168.1.25",
                button_label="Encapsular paquete IP y transmitir ▶"
            ),
            # Stage 4: Network Transmission & Packet Loss reaction
            StageDecision(
                stage_id="net_loss_response",
                layer_num=4,
                title="Evento de red — Manejo de pérdida en router",
                prompt="Core Router buffer congested! Chunk #3 was DROPPED. How should Person A react?",
                explanation="In reliable networks, packet loss must be detected and resolved to prevent file corruption.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "retransmit",
                        "title": "Fast Retransmit Chunk #3 upon duplicate ACK (TCP)",
                        "desc": "Resend missing Chunk #3 so Person B can reassemble the file without data loss."
                    },
                    {
                        "id": "skip",
                        "title": "Ignore missing chunk and continue to next stage",
                        "desc": "Proceed without Chunk #3 (Simulates UDP behavior or ignoring packet loss)."
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
                prompt="All received data is arriving at Person B. How should Person B's Application Layer finalize the file?",
                explanation="When all layers decapsulate, the application verifies the cryptographic hash against the sender's original manifest.",
                input_type="ACTION",
                options=[],
                button_label="Verificar checksum MD5 y guardar video ▶"
            )
        ]

        self.present_current_stage()

    def submit_user_decision(self, user_value: str, extra_data: Optional[Dict[str, Any]] = None):
        super().submit_user_decision(user_value, extra_data)
        stage = self.stages[self.current_stage_index]

        if stage.stage_id == "l7_packaging":
            if user_value == "monolithic":
                # Consequence: MTU violation!
                self.update_layer("sender", 7, LayerStatus.ERROR, "MTU Buffer Overflow (500 MB unsplit)", has_error=True)
                self.log("ERROR", "⚠", "Consequence: Ethernet Maximum Transmission Unit (MTU) is 1500 bytes. A 500 MB unsplit payload causes immediate buffer overflow!", 7)

                def fix_packaging():
                    self.is_segmented = True
                    self.update_layer("sender", 7, LayerStatus.COMPLETE, "Segmented into 4 chunks (125 MB each)")
                    self.log("SUCCESS", "✓", "Repaired: File partitioned into 4 discrete chunks with sequence tags.", 7)
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=7,
                    title="MTU Limit Violation (Oversized Payload)",
                    summary="Network devices reject packets exceeding the MTU (Maximum Transmission Unit, typically 1500 bytes). A 500 MB single packet cannot be transmitted.",
                    details=(
                        "Physical layer transmission limits require data to be divided into segments.\n\n"
                        "When transmitting large datasets, the Application and Transport layers segment data into manageable chunks.\n"
                        "This allows individual lost fragments to be retransmitted rather than re-sending all 500 MB."
                    ),
                    options=[
                        RepairOption(
                            id="opt_segment",
                            title="Partition into discrete chunks (Recommended)",
                            description="Split 500 MB into 4 numbered chunks with sequence tracking.",
                            is_correct=True,
                            feedback="Correct! Segmentation allows efficient routing and error recovery."
                        ),
                        RepairOption(
                            id="opt_force",
                            title="Force single packet anyway",
                            description="Attempt to force oversized buffer onto link.",
                            is_correct=False,
                            feedback="Incorrect. Network cards and routers will immediately discard packets exceeding MTU."
                        )
                    ],
                    on_repair_success=fix_packaging
                )
                self.trigger_error(issue)
                return

            self.is_segmented = True
            self.update_layer("sender", 7, LayerStatus.COMPLETE, "Data Segmented (4 x 125 MB)")
            self.log("INFO", "✓", "L7 (Application): 'video.mp4' partitioned into 4 chunks (Seq #1-#4).", 7)
            self.inspector_data.app_protocol = "FTP / Media Stream"
            self.inspector_data.payload_text = "[video.mp4: 4 Chunks, Total 524,288,000 bytes]"
            self.inspector_data.payload_hex = format_hex_dump(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42")
            self.inspector_data.raw_size_bytes = 524288000
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l4_protocol":
            self.selected_protocol = "TCP" if user_value == "tcp" else "UDP"
            if self.selected_protocol == "UDP":
                self.log("WARNING", "⚠", "User chose UDP: Warning! UDP does not guarantee delivery, track sequences, or retransmit lost packets.", 4)
                self.update_layer("sender", 4, LayerStatus.ACTIVE, "UDP Datagrams (Unreliable)")
                self.inspector_data.transport_protocol = "UDP"
                self.inspector_data.flags = "None (Connectionless)"
                self.inspector_data.seq_num = 0
                self.notify_inspector()
                # Skip handshake stage because UDP is connectionless!
                self.current_stage_index += 1  # jump past handshake
                self._advance_to_next_stage()
            else:
                self.log("INFO", "✓", "User chose TCP: Enables sequence numbers, acknowledgments, and automatic repeat requests (ARQ).", 4)
                self.update_layer("sender", 4, LayerStatus.ACTIVE, "TCP Selected (Awaiting Handshake)")
                self.inspector_data.transport_protocol = "TCP"
                self.notify_inspector()
                self._advance_to_next_stage()

        elif stage.stage_id == "l4_handshake":
            if user_value != "syn":
                self.update_layer("sender", 4, LayerStatus.ERROR, f"Invalid TCP Handshake Flag ({user_value.upper()})", has_error=True)
                self.log("ERROR", "⚠", f"Consequence: Cannot send {user_value.upper()} to start connection! TCP RFC 793 requires initial packet to carry SYN flag.", 4)

                def fix_handshake():
                    self.update_layer("sender", 4, LayerStatus.COMPLETE, "TCP 3-Way Handshake Established")
                    self.log("SUCCESS", "✓", "Handshake Completed: SYN sent -> SYN/ACK received -> ACK sent. Connection ESTABLISHED.", 4)
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=4,
                    title="TCP Handshake State Machine Error",
                    summary=f"TCP connection cannot be opened with flag {user_value.upper()}. Initial packet must have SYN flag.",
                    details=(
                        "Before transmitting data over TCP, both endpoints must synchronize sequence numbers.\n\n"
                        "The three-way handshake follows a strict sequence:\n"
                        "1. Sender sends SYN (Synchronize)\n"
                        "2. Receiver replies with SYN-ACK (Synchronize + Acknowledge)\n"
                        "3. Sender replies with ACK (Acknowledge)\n\n"
                        "Sending an ACK or FIN without prior connection will cause the receiver to drop the packet."
                    ),
                    options=[
                        RepairOption(
                            id="send_syn",
                            title="Send SYN Flag to open connection (Recommended)",
                            description="Send TCP segment with SYN flag set and initial sequence number.",
                            is_correct=True,
                            feedback="Correct! Receiver responds with SYN-ACK and connection is established."
                        ),
                        RepairOption(
                            id="skip_handshake",
                            title="Skip handshake and blast data",
                            description="Send data segments immediately without connection.",
                            is_correct=False,
                            feedback="Incorrect. The receiving operating system will discard data on an unestablished TCP socket."
                        )
                    ],
                    on_repair_success=fix_handshake
                )
                self.trigger_error(issue)
                return

            # Successful handshake animation
            self.log("INFO", "→", "Transmitting TCP SYN packet to Person B...", 4)
            def on_syn_reached():
                self.log("INFO", "✓", "Person B received SYN, replied with SYN-ACK!", 4)
                self.update_layer("sender", 4, LayerStatus.COMPLETE, "TCP Handshake Complete (ESTABLISHED)")
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
                self.update_layer("sender", 3, LayerStatus.ERROR, "ICMP Host Unreachable (192.168.1.99)", has_error=True)
                self.log("ERROR", "⚠", "Consequence: Destination IP 192.168.1.99 does not exist on network! Core Router dropped frame with ICMP Destination Unreachable.", 3)

                def fix_ip():
                    self.dest_ip = "192.168.1.25"
                    self.update_layer("sender", 3, LayerStatus.COMPLETE, "Destination IP set to 192.168.1.25")
                    self.log("SUCCESS", "✓", "Repaired: Destination IP updated to 192.168.1.25 (Person B).", 3)
                    self._transmit_initial_chunks()

                issue = TroubleshootIssue(
                    layer_num=3,
                    title="Network Layer Routing Error: Host Unreachable",
                    summary="The packet was addressed to 192.168.1.99, which has no active ARP entry or host on the network.",
                    details=(
                        "In Layer 3 (Network), the sender must address packets to the valid logical IP of the intended destination.\n"
                        "Person B's actual IP address is 192.168.1.25.\n\n"
                        "When addressing an unassigned IP (192.168.1.99), ARP resolution fails and router drops the transmission."
                    ),
                    options=[
                        RepairOption(
                            id="fix_dest_ip",
                            title="Set Destination IP to 192.168.1.25 (Person B)",
                            description="Use Person B's verified IP address.",
                            is_correct=True,
                            feedback="Correct! Packet routes directly to Person B."
                        ),
                        RepairOption(
                            id="ignore_ip",
                            title="Keep 192.168.1.99",
                            description="Hope another computer forwards it.",
                            is_correct=False,
                            feedback="Incorrect. No host exists at 192.168.1.99."
                        )
                    ],
                    on_repair_success=fix_ip
                )
                self.trigger_error(issue)
                return

            self.update_layer("sender", 3, LayerStatus.COMPLETE, "Routed to 192.168.1.25")
            self.update_layer("sender", 2, LayerStatus.COMPLETE, "Ethernet Frames (MAC 00:1A:2B:3C:4D:5E)")
            self.update_layer("sender", 1, LayerStatus.COMPLETE, "Bitstream Generated")
            self.log("INFO", "✓", "L3/L2/L1: Encapsulated into IP Packets & Ethernet Frames. Ready for network transit.", 3)
            self._transmit_initial_chunks()

        elif stage.stage_id == "net_loss_response":
            if user_value == "skip" or self.selected_protocol == "UDP":
                # Consequence: File corrupted!
                self.chunks_received[3] = True  # chunk 4 arrived, but 3 missing
                self._update_chunk_ui()
                self.update_layer("receiver", 4, LayerStatus.ERROR, "Missing Chunk #3! File Corrupted", has_error=True)
                self.log("ERROR", "⚠", "Consequence: Chunk #3 was lost! File at Person B is only 75% complete and cannot be opened.", 4)

                def fix_to_tcp():
                    self.selected_protocol = "TCP"
                    self.retransmitted_chunk_3 = True
                    self.chunks_received[2] = True
                    self.log("SUCCESS", "✓", "Repaired to TCP Fast Retransmit: Receiver sent DupACK, Sender retransmitted Chunk #3!", 4)
                    self.update_layer("receiver", 4, LayerStatus.COMPLETE, "All 4 Chunks Reassembled (TCP)")
                    self._update_chunk_ui()
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=4,
                    title="Data Loss Consequence (Missing Chunk #3)",
                    summary="Person B cannot open 'video.mp4' because Chunk #3 was dropped and not retransmitted.",
                    details=(
                        "This demonstrates the fundamental consequence of protocol choice:\n\n"
                        "• In UDP or un-retransmitted transfers, lost chunks leave permanent holes in files.\n"
                        "• In TCP, lost packets trigger Duplicate ACKs, causing Fast Retransmit so the receiver recovers 100% of data."
                    ),
                    options=[
                        RepairOption(
                            id="repair_retransmit",
                            title="Perform TCP Fast Retransmission for Chunk #3",
                            description="Retransmit missing Chunk #3 so the file can be reconstructed with 100% integrity.",
                            is_correct=True,
                            feedback="Correct! Chunk #3 is retransmitted and acknowledged."
                        ),
                        RepairOption(
                            id="repair_corrupt",
                            title="Accept corrupted 75% file",
                            description="Leave file incomplete.",
                            is_correct=False,
                            feedback="Incorrect. MP4 container headers and keyframes are corrupted."
                        )
                    ],
                    on_repair_success=fix_to_tcp
                )
                self.trigger_error(issue)
                return

            # User chose retransmit!
            self.log("INFO", "→", "Fast Retransmit: Person A retransmitting missing Chunk #3...", 4)
            def on_retrans_reached():
                self.chunks_received[2] = True
                self.chunks_received[3] = True
                self.retransmitted_chunk_3 = True
                self.log("SUCCESS", "✓", "Chunk #3 arrived and verified! All 4 chunks accounted for in receiver buffer.", 4)
                self._update_chunk_ui()
                self.update_layer("receiver", 4, LayerStatus.COMPLETE, "All 4 Chunks Reassembled (TCP)")
                self._advance_to_next_stage()

            if self.cb_network_animate:
                self.cb_network_animate("Router", "Person B", "PACKET", "Chunk 3 (Retransmit)", False, on_retrans_reached)
            else:
                on_retrans_reached()

        elif stage.stage_id == "l7_verify":
            # Final verification
            for lyr in range(1, 8):
                self.update_layer("receiver", lyr, LayerStatus.COMPLETE, "Decapsulated & Verified")

            self.log("SUCCESS", "✓", "Person B: MD5 Checksum (e2fc714c4727ee9395f324dd2e7f331f) Matches 100%! 'video.mp4' (500 MB) Saved.", 7)
            if self.status_lbl:
                self.status_lbl.config(text="✓ File Transfer 100% Complete & Verified! All decisions succeeded.", fg=theme.COLOR_SUCCESS)

            self.complete_mission({
                "File Name": "video.mp4",
                "Total Size": "500 MB",
                "Protocol Used": self.selected_protocol,
                "Handshake": "SYN → SYN-ACK → ACK Verified",
                "Packets Sent/Recv": f"{self.packets_sent} sent / {self.packets_received} recv",
                "Decisions Made": self.decisions_made,
                "Errors Diagnosed & Fixed": self.errors_repaired,
                "Key Lesson": "File transfers require segmentation and reliable transport (TCP) to guarantee that dropped packets are retransmitted."
            })

    def _transmit_initial_chunks(self):
        """Animate transmission of chunks 1, 2, and dropped chunk 3."""
        self.log("INFO", "→", "Transmitting Chunk #1 & #2 across network...", None)
        def on_c1_2_reached():
            self.chunks_received[0] = True
            self.chunks_received[1] = True
            self.packets_sent += 2
            self.packets_received += 2
            self._update_chunk_ui()

            # Now Chunk 3 drops at Router!
            self.log("WARNING", "⚠", "Core Router buffer congested: Chunk #3 DROPPED in transit!", None)
            self.packets_sent += 1
            self.packets_lost += 1

            def on_c3_dropped():
                self._update_chunk_ui()
                self._advance_to_next_stage()

            if self.cb_network_animate:
                self.cb_network_animate("Person A", "Router", "PACKET", "Chunk #3", True, on_c3_dropped)
            else:
                on_c3_dropped()

        if self.cb_network_animate:
            self.cb_network_animate("Person A", "Person B", "PACKET", "Chunks #1 & #2", False, on_c1_2_reached)
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
                    self.chunk_labels[i].config(text="✓ RECEIVED", fg=theme.COLOR_SUCCESS)
                elif self.packets_sent > (i + 1) and not r:
                    self.chunk_labels[i].config(text="✗ DROPPED", fg=theme.COLOR_ERROR)
                else:
                    self.chunk_labels[i].config(text="Waiting...", fg=theme.TEXT_MUTED)

        if self.status_lbl:
            if rec_count == 4:
                self.status_lbl.config(text="✓ All 4 Chunks Received! Awaiting MD5 verification.", fg=theme.COLOR_SUCCESS)
            elif rec_count > 0:
                self.status_lbl.config(text=f"Receiving chunks... {rec_count}/4 ({int(pct)}% Complete)", fg=theme.TEXT_ACCENT)

    def _advance_to_next_stage(self):
        self.current_stage_index += 1
        self.present_current_stage()
