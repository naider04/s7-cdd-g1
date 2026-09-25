"""
Mission 2: Access a Website
Interactive, decision-driven simulation covering:
- DNS Resolution (Domain to IP mapping over UDP 53)
- Protocol & Port Choice (HTTP Port 80 vs HTTPS Port 443 with TLS vs Port 8080)
- Subnet Routing & Default Gateway determination (192.168.1.1)
- Client-Server Request/Response and HTML rendering in browser
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional
from missions.base_mission import BaseMission
from models import LayerStatus, TroubleshootIssue, RepairOption, StageDecision, PacketInspectorData
from utils.helpers import format_hex_dump
import theme


class MissionWebAccess(BaseMission):
    def __init__(self):
        super().__init__(
            mission_id=2,
            title="Access a Website",
            icon="🌐",
            subtitle="Navigate to a remote web server with routing & protocol decisions",
            objective="Access 'www.example.com'. Resolve its IP via DNS, select HTTP vs HTTPS, configure gateway routing, and inspect the rendered page.",
            concepts=[
                "DNS Resolution (Domain -> IP over UDP 53)",
                "Default Gateway Routing (LAN to WAN)",
                "HTTP vs HTTPS (Port 80 vs 443 / TLS Security)",
                "Client-Server HTTP Request & 200 OK Response",
                "HTML Parsing in Browser Interface"
            ]
        )
        self.target_url = "www.example.com"
        self.resolved_ip = "93.184.216.34"
        self.selected_protocol = "HTTPS"
        self.selected_port = 443
        self.dns_server = "8.8.8.8"
        self.gateway_ip = "192.168.1.1"

        # UI elements
        self.browser_view: Optional[tk.Frame] = None
        self.browser_url_entry: Optional[tk.Entry] = None
        self.browser_status: Optional[tk.Label] = None
        self.ssl_badge: Optional[tk.Label] = None

    def build_visual_output_ui(self, parent: tk.Widget):
        container = tk.Frame(parent, bg=theme.BG_PANEL, padx=10, pady=8)
        container.pack(fill=tk.BOTH, expand=True)

        # Mini Browser Header Bar
        bar = tk.Frame(container, bg=theme.BG_DARK, padx=8, pady=6, bd=1, relief=tk.SOLID)
        bar.pack(fill=tk.X, pady=(0, 6))

        self.ssl_badge = tk.Label(bar, text="🔒 HTTPS", font=theme.FONT_SMALL, fg=theme.COLOR_SUCCESS, bg=theme.BG_DARK, padx=6)
        self.ssl_badge.pack(side=tk.LEFT, padx=(0, 8))

        self.browser_url_entry = tk.Entry(bar, font=theme.FONT_MONO, bg=theme.BG_INPUT, fg=theme.TEXT_PRIMARY, insertbackground="white")
        self.browser_url_entry.insert(0, f"https://{self.target_url}")
        self.browser_url_entry.config(state="readonly")
        self.browser_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.browser_status = tk.Label(bar, text="Offline", font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_DARK)
        self.browser_status.pack(side=tk.RIGHT)

        # Webpage rendering view
        self.browser_view = tk.Frame(container, bg="#ffffff", padx=20, pady=15, bd=1, relief=tk.SUNKEN)
        self.browser_view.pack(fill=tk.BOTH, expand=True)

        self.render_placeholder()

    def render_placeholder(self):
        if not self.browser_view:
            return
        for widget in self.browser_view.winfo_children():
            widget.destroy()
        tk.Label(self.browser_view, text="Awaiting network decisions to request webpage...", font=theme.FONT_BODY, fg="#666666", bg="#ffffff").pack(pady=40)

    def render_webpage(self):
        if not self.browser_view:
            return
        for widget in self.browser_view.winfo_children():
            widget.destroy()

        h1 = tk.Label(self.browser_view, text="Example Domain", font=(theme.FONT_FAMILY, 18, "bold"), fg="#111827", bg="#ffffff")
        h1.pack(anchor=tk.W, pady=(0, 8))

        p1 = tk.Label(
            self.browser_view,
            text="This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.",
            font=theme.FONT_BODY,
            fg="#374151",
            bg="#ffffff",
            justify=tk.LEFT,
            wraplength=550
        )
        p1.pack(anchor=tk.W, pady=(0, 10))

        link = tk.Label(self.browser_view, text="More information... (RFC 2606)", font=(theme.FONT_FAMILY, 10, "underline"), fg="#2563eb", bg="#ffffff")
        link.pack(anchor=tk.W)

    def load_initial_stage(self):
        self.current_stage_index = 0
        self.stages = [
            # Stage 0: DNS Resolver
            StageDecision(
                stage_id="l7_dns",
                layer_num=7,
                title="Application Layer — DNS Name Resolution",
                prompt="Person A wants to navigate to 'www.example.com'. Before creating an IP packet, Layer 7 needs the server's numeric IP address. Which DNS resolver should be queried?",
                explanation="Computers communicate over IP using numeric addresses. DNS (Domain Name System) translates human-readable hostnames into 32-bit IPv4 addresses over UDP port 53.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "8.8.8.8",
                        "title": "8.8.8.8 (Google Public DNS Server — Active)",
                        "desc": "Standard recursive public resolver listening on UDP port 53."
                    },
                    {
                        "id": "0.0.0.0",
                        "title": "0.0.0.0 (Unconfigured / Missing DNS)",
                        "desc": "Non-routable zero address representing an unconfigured DNS entry."
                    },
                    {
                        "id": "127.0.0.1",
                        "title": "127.0.0.1 (Localhost — No DNS Daemon)",
                        "desc": "Queries the local host where no local name server is running."
                    }
                ],
                default_value="8.8.8.8",
                button_label="Send DNS Query (UDP Port 53) ▶"
            ),
            # Stage 1: Protocol & Port Choice
            StageDecision(
                stage_id="l4_l7_proto",
                layer_num=4,
                title="Transport & Application Layers — Protocol & Port",
                prompt="Which web protocol and destination port should be selected for the web connection?",
                explanation="Web servers listen on well-known ports: Port 80 for HTTP (plaintext) and Port 443 for HTTPS (TLS encrypted). Non-standard ports require explicit server listeners.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "https_443",
                        "title": "HTTPS (Port 443 — Encrypted via TLS 1.3)",
                        "desc": "Secures transmission with symmetric encryption, preventing packet eavesdropping."
                    },
                    {
                        "id": "http_80",
                        "title": "HTTP (Port 80 — Plaintext)",
                        "desc": "Unencrypted web transfer. Headers and HTML can be inspected in cleartext."
                    },
                    {
                        "id": "port_8080",
                        "title": "HTTP (Port 8080 — Non-Standard Port)",
                        "desc": "Sends connection request to alternative port 8080."
                    }
                ],
                default_value="https_443",
                button_label="Configure Port & Encapsulate L4 ▶"
            ),
            # Stage 2: Gateway Routing
            StageDecision(
                stage_id="l3_gateway",
                layer_num=3,
                title="Network Layer — Routing & Default Gateway",
                prompt=f"Person A is on subnet 192.168.1.0/24. The resolved web server is {self.resolved_ip} (External WAN). Where should Layer 3 forward the packet?",
                explanation="When destination IPs are outside the local subnet mask, Layer 3 cannot send directly to the destination MAC; it must route through the Default Gateway Router.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "gateway",
                        "title": "Forward to Default Gateway Router (192.168.1.1)",
                        "desc": "Router reads IP destination and routes it across core WAN routers to 93.184.216.34."
                    },
                    {
                        "id": "direct_arp",
                        "title": "Send direct ARP broadcast on local switch for 93.184.216.34",
                        "desc": "Broadcasts locally hoping the external server is attached to the same switch."
                    }
                ],
                default_value="gateway",
                button_label="Encapsulate Layer 3 & Route Packet ▶"
            ),
            # Stage 3: Server Response & Render
            StageDecision(
                stage_id="l7_render",
                layer_num=7,
                title="Application Layer — Browser Rendering",
                prompt="The web server received the GET request and returned 'HTTP/1.1 200 OK' with the HTML document payload. Finalize the transmission:",
                explanation="Person A's browser parses the HTML document structure, evaluates styles, and renders the graphical webpage.",
                input_type="ACTION",
                options=[],
                button_label="Parse HTML & Render Webpage in Browser ▶"
            )
        ]

        self.present_current_stage()

    def submit_user_decision(self, user_value: str, extra_data: Optional[Dict[str, Any]] = None):
        super().submit_user_decision(user_value, extra_data)
        stage = self.stages[self.current_stage_index]

        if stage.stage_id == "l7_dns":
            self.dns_server = user_value
            if self.dns_server != "8.8.8.8":
                self.update_layer("sender", 7, LayerStatus.ERROR, f"DNS Failure ({self.dns_server})", has_error=True)
                self.log("ERROR", "⚠", f"Consequence: Nameserver {self.dns_server} is invalid or unreachable. Host 'www.example.com' cannot be resolved!", 7)

                def fix_dns():
                    self.dns_server = "8.8.8.8"
                    self.update_layer("sender", 7, LayerStatus.COMPLETE, f"Resolved IP: {self.resolved_ip}")
                    self.log("SUCCESS", "✓", f"DNS Query Succeeded: 'www.example.com' -> {self.resolved_ip} (via UDP 53 to 8.8.8.8)", 7)
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=7,
                    title="DNS Name Resolution Failure",
                    summary=f"The operating system could not resolve 'www.example.com' using nameserver {self.dns_server}.",
                    details=(
                        "Without a working DNS server, web browsers cannot determine which IP address to connect to.\n"
                        "0.0.0.0 is an invalid target, and 127.0.0.1 has no active DNS daemon running.\n\n"
                        "To browse the web, configure the system with a valid public resolver like 8.8.8.8 (Google DNS) or 1.1.1.1 (Cloudflare)."
                    ),
                    options=[
                        RepairOption(
                            id="set_8888",
                            title="Configure Primary DNS to 8.8.8.8 (Recommended)",
                            description="Use Google's public recursive DNS resolver.",
                            is_correct=True,
                            feedback="Correct! DNS server returns A-Record 93.184.216.34."
                        ),
                        RepairOption(
                            id="skip_dns",
                            title="Send packet to domain string without IP",
                            description="Send Ethernet frame directly with string name.",
                            is_correct=False,
                            feedback="Incorrect. IP routers cannot route text domain strings; they require a numerical 32-bit IP."
                        )
                    ],
                    on_repair_success=fix_dns
                )
                self.trigger_error(issue)
                return

            self.log("SUCCESS", "✓", f"L7 (DNS): Resolved 'www.example.com' -> {self.resolved_ip} (UDP Port 53 to {self.dns_server})", 7)
            self.update_layer("sender", 7, LayerStatus.COMPLETE, f"Resolved IP: {self.resolved_ip}")
            self.inspector_data.app_protocol = "DNS / UDP 53"
            self.inspector_data.payload_text = f"Query: www.example.com -> Answer: {self.resolved_ip}"
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l4_l7_proto":
            if user_value == "port_8080":
                # Consequence: Connection refused!
                self.update_layer("sender", 4, LayerStatus.ERROR, "TCP RST: Connection Refused (Port 8080)", has_error=True)
                self.log("ERROR", "⚠", "Consequence: Server 93.184.216.34 replied with TCP [RST, ACK]! No web service is listening on Port 8080.", 4)

                def fix_proto():
                    self.selected_protocol = "HTTPS"
                    self.selected_port = 443
                    self.update_layer("sender", 4, LayerStatus.COMPLETE, "TCP Port 443 (HTTPS)")
                    self.log("SUCCESS", "✓", "Repaired to HTTPS (Port 443): Standard encrypted web port accepted by web server.", 4)
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=4,
                    title="Port Unreachable (TCP Connection Refused)",
                    summary="The remote host received the TCP SYN segment on Port 8080, but returned a TCP RST (Reset) because no web server is bound to port 8080.",
                    details=(
                        "In Layer 4 (Transport), destination ports identify specific server software processes.\n\n"
                        "Standard public web servers only bind listeners on:\n"
                        "• Port 80: HTTP (Plaintext)\n"
                        "• Port 443: HTTPS (TLS Secure)\n\n"
                        "Connecting to arbitrary ports like 8080 causes the kernel to immediately reject the connection with TCP RST."
                    ),
                    options=[
                        RepairOption(
                            id="fix_port_443",
                            title="Switch to Standard Port 443 (HTTPS - Recommended)",
                            description="Connect to the web server's secure SSL/TLS listener on port 443.",
                            is_correct=True,
                            feedback="Correct! Server accepts the connection on Port 443."
                        ),
                        RepairOption(
                            id="keep_8080",
                            title="Retry Port 8080 continuously",
                            description="Spam SYN packets to port 8080.",
                            is_correct=False,
                            feedback="Incorrect. The port is closed; repeated attempts will just be rejected."
                        )
                    ],
                    on_repair_success=fix_proto
                )
                self.trigger_error(issue)
                return

            if user_value == "http_80":
                self.selected_protocol = "HTTP"
                self.selected_port = 80
                self.log("WARNING", "⚠", "L6/L4: Plaintext HTTP chosen (Port 80). Warning: Data is unencrypted and readable by network sniffers.", 6)
                self.update_layer("sender", 6, LayerStatus.COMPLETE, "Plaintext (No Encryption)")
                self.update_layer("sender", 4, LayerStatus.COMPLETE, "TCP Port 80 (HTTP)")
                self.inspector_data.encryption = "None (Plaintext)"
            else:
                self.selected_protocol = "HTTPS"
                self.selected_port = 443
                self.log("INFO", "✓", "L6/L4: HTTPS chosen (Port 443). TLS 1.3 encryption negotiated with AES-256-GCM cipher.", 6)
                self.update_layer("sender", 6, LayerStatus.COMPLETE, "TLS 1.3 Encrypted")
                self.update_layer("sender", 4, LayerStatus.COMPLETE, "TCP Port 443 (HTTPS)")
                self.inspector_data.encryption = "TLS 1.3 (AES-256-GCM)"

            self.inspector_data.transport_protocol = "TCP"
            self.inspector_data.dst_port = self.selected_port
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l3_gateway":
            if user_value == "direct_arp":
                # Consequence: ARP timeout!
                self.update_layer("sender", 3, LayerStatus.ERROR, "Subnet Mismatch (ARP Timeout)", has_error=True)
                self.log("ERROR", "⚠", "Consequence: Host 93.184.216.34 is on an external network. Local switch broadcast cannot reach external WAN IP!", 3)

                def fix_gateway():
                    self.gateway_ip = "192.168.1.1"
                    self.update_layer("sender", 3, LayerStatus.COMPLETE, f"Routed to Gateway {self.gateway_ip}")
                    self.log("SUCCESS", "✓", "Repaired: Packet forwarded to Default Gateway Router (192.168.1.1).", 3)
                    self._transmit_web_request()

                issue = TroubleshootIssue(
                    layer_num=3,
                    title="Layer 3 Routing Error: Off-Subnet Delivery without Gateway",
                    summary=f"The client attempted to resolve 93.184.216.34 using a local Layer 2 ARP broadcast instead of routing via the default gateway 192.168.1.1.",
                    details=(
                        "Hosts check if a destination IP matches their local subnet mask (192.168.1.0/24).\n\n"
                        "Because 93.184.216.34 is outside 192.168.1.0/24, the computer MUST encapsulate the IP packet into an Ethernet frame addressed to the MAC of the Default Gateway Router.\n"
                        "Sending an ARP broadcast on the local switch fails because switches do not forward local broadcasts to the Internet."
                    ),
                    options=[
                        RepairOption(
                            id="use_gateway",
                            title="Route through Default Gateway (192.168.1.1 - Recommended)",
                            description="Send frame to local router MAC so it can forward packets onto the Internet WAN.",
                            is_correct=True,
                            feedback="Correct! Gateway receives frame, decrements TTL, and routes packet to WAN."
                        ),
                        RepairOption(
                            id="change_mask",
                            title="Change subnet mask to /0",
                            description="Treat entire world as local subnet.",
                            is_correct=False,
                            feedback="Incorrect. Switches cannot handle worldwide broadcast domains."
                        )
                    ],
                    on_repair_success=fix_gateway
                )
                self.trigger_error(issue)
                return

            self.update_layer("sender", 3, LayerStatus.COMPLETE, f"Routed to Gateway {self.gateway_ip}")
            self.update_layer("sender", 2, LayerStatus.COMPLETE, "Ethernet Frame to Router MAC")
            self.update_layer("sender", 1, LayerStatus.COMPLETE, "Bitstream Transmitted")
            self.log("INFO", "✓", f"L3/L2/L1: Packet forwarded to Gateway {self.gateway_ip} destined for {self.resolved_ip}:{self.selected_port}", 3)
            self._transmit_web_request()

        elif stage.stage_id == "l7_render":
            for lyr in range(1, 8):
                self.update_layer("receiver", lyr, LayerStatus.COMPLETE, "Decapsulated & Processed")

            self.log("SUCCESS", "✓", "Person A: HTTP 200 OK received. HTML parsed and rendered in browser window!", 7)

            # Update browser UI
            if self.browser_url_entry:
                self.browser_url_entry.config(state="normal")
                prefix = "https" if self.selected_protocol == "HTTPS" else "http"
                self.browser_url_entry.delete(0, tk.END)
                self.browser_url_entry.insert(0, f"{prefix}://{self.target_url}")
                self.browser_url_entry.config(state="readonly")

            if self.ssl_badge:
                if self.selected_protocol == "HTTPS":
                    self.ssl_badge.config(text="🔒 HTTPS (TLS 1.3)", fg=theme.COLOR_SUCCESS)
                else:
                    self.ssl_badge.config(text="⚠ HTTP (Not Secure)", fg=theme.COLOR_WARNING)

            if self.browser_status:
                self.browser_status.config(text="200 OK (Loaded)", fg=theme.COLOR_SUCCESS)

            self.render_webpage()

            self.complete_mission({
                "Target Hostname": self.target_url,
                "DNS Server": f"{self.dns_server} (UDP 53)",
                "Resolved IP": self.resolved_ip,
                "Protocol / Port": f"{self.selected_protocol} (Port {self.selected_port})",
                "Routing Path": f"LAN Host -> Gateway {self.gateway_ip} -> Internet -> Server {self.resolved_ip}",
                "Decisions Made": self.decisions_made,
                "Errors Diagnosed & Fixed": self.errors_repaired,
                "Result": "Webpage Rendered Cleanly"
            })

    def _transmit_web_request(self):
        """Transmit HTTP request to server and get response."""
        self.log("INFO", "→", f"Sending {self.selected_protocol} GET request through Gateway across Internet to Web Server...", None)

        def on_server_reached():
            self.packets_sent += 1
            self.log("INFO", "✓", "Web Server (93.184.216.34): Decapsulated request, generated HTTP/1.1 200 OK Response (412 bytes).", 7)
            self.inspector_data.app_protocol = "HTTP/1.1 200 OK"
            self.inspector_data.payload_text = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE html><html><body><h1>Example Domain</h1>...</body></html>"
            self.inspector_data.payload_hex = format_hex_dump(self.inspector_data.payload_text.encode())
            self.notify_inspector()

            # Return response
            def on_resp_reached():
                self.packets_received += 1
                self._advance_to_next_stage()

            if self.cb_network_animate:
                self.cb_network_animate("Person B", "Person A", "PACKET", "HTTP 200 OK", False, on_resp_reached)
            else:
                on_resp_reached()

        if self.cb_network_animate:
            self.cb_network_animate("Person A", "Person B", "PACKET", f"{self.selected_protocol} GET", False, on_server_reached)
        else:
            on_server_reached()

    def _advance_to_next_stage(self):
        self.current_stage_index += 1
        self.present_current_stage()
