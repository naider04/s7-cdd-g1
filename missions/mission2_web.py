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
            title="Acceder a un sitio web",
            icon="🌐",
            subtitle="Navegar a un servidor web remoto con decisiones de enrutamiento y protocolo",
            objective="Acceder a 'www.example.com'. Resolver su IP con DNS, elegir entre HTTP y HTTPS, configurar el enrutamiento mediante la puerta de enlace e inspeccionar la página renderizada.",
            concepts=[
                "Resolución DNS (dominio -> IP por UDP 53)",
                "Enrutamiento por puerta de enlace predeterminada (de LAN a WAN)",
                "HTTP frente a HTTPS (puerto 80 frente a 443 y seguridad TLS)",
                "Solicitud HTTP cliente-servidor y respuesta 200 OK",
                "Análisis de HTML en la interfaz del navegador"
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

        self.browser_status = tk.Label(bar, text="Sin conexión", font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_DARK)
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
        tk.Label(self.browser_view, text="Esperando decisiones de red para solicitar la página web...", font=theme.FONT_BODY, fg="#666666", bg="#ffffff").pack(pady=40)

    def render_webpage(self):
        if not self.browser_view:
            return
        for widget in self.browser_view.winfo_children():
            widget.destroy()

        h1 = tk.Label(self.browser_view, text="Dominio de ejemplo", font=(theme.FONT_FAMILY, 18, "bold"), fg="#111827", bg="#ffffff")
        h1.pack(anchor=tk.W, pady=(0, 8))

        p1 = tk.Label(
            self.browser_view,
            text="Este dominio está destinado a usarse en ejemplos ilustrativos de documentos. Puedes usar este dominio en publicaciones sin coordinación previa ni solicitud de permiso.",
            font=theme.FONT_BODY,
            fg="#374151",
            bg="#ffffff",
            justify=tk.LEFT,
            wraplength=550
        )
        p1.pack(anchor=tk.W, pady=(0, 10))

        link = tk.Label(self.browser_view, text="Más información... (RFC 2606)", font=(theme.FONT_FAMILY, 10, "underline"), fg="#2563eb", bg="#ffffff")
        link.pack(anchor=tk.W)

    def load_initial_stage(self):
        self.current_stage_index = 0
        self.stages = [
            # Stage 0: DNS Resolver
            StageDecision(
                stage_id="l7_dns",
                layer_num=7,
                title="Capa de Aplicación — Resolución DNS",
                prompt="Persona A quiere navegar a 'www.example.com'. Antes de crear un paquete IP, la capa 7 necesita la dirección IP numérica del servidor. ¿Qué servidor DNS debe consultarse?",
                explanation="Las computadoras se comunican mediante IP usando direcciones numéricas. DNS (Sistema de Nombres de Dominio) traduce los nombres de dominio legibles por personas en direcciones IPv4 de 32 bits mediante el puerto UDP 53.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "8.8.8.8",
                        "title": "8.8.8.8 (servidor DNS público de Google — activo)",
                        "desc": "Resolvedor público recursivo estándar que escucha en el puerto UDP 53."
                    },
                    {
                        "id": "0.0.0.0",
                        "title": "0.0.0.0 (DNS sin configurar / ausente)",
                        "desc": "Dirección cero no enrutable que representa una entrada DNS sin configurar."
                    },
                    {
                        "id": "127.0.0.1",
                        "title": "127.0.0.1 (localhost — sin servicio DNS)",
                        "desc": "Consulta el equipo local, donde no se está ejecutando ningún servidor de nombres local."
                    }
                ],
                default_value="8.8.8.8",
                button_label="Enviar consulta DNS (puerto UDP 53) ▶"
            ),
            # Stage 1: Protocol & Port Choice
            StageDecision(
                stage_id="l4_l7_proto",
                layer_num=4,
                title="Capas de Transporte y Aplicación — Protocolo y puerto",
                prompt="¿Qué protocolo web y puerto de destino deben seleccionarse para la conexión web?",
                explanation="Los servidores web escuchan en puertos conocidos: el puerto 80 para HTTP (texto plano) y el puerto 443 para HTTPS (cifrado con TLS). Los puertos no estándar requieren que el servidor habilite servicios de escucha explícitamente.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "https_443",
                        "title": "HTTPS (puerto 443 — cifrado con TLS 1.3)",
                        "desc": "Protege la transmisión con cifrado simétrico y evita la interceptación de paquetes."
                    },
                    {
                        "id": "http_80",
                        "title": "HTTP (puerto 80 — texto plano)",
                        "desc": "Transferencia web sin cifrar. Las cabeceras y el HTML pueden inspeccionarse en texto claro."
                    },
                    {
                        "id": "port_8080",
                        "title": "HTTP (puerto 8080 — puerto no estándar)",
                        "desc": "Envía la solicitud de conexión al puerto alternativo 8080."
                    }
                ],
                default_value="https_443",
                button_label="Configurar puerto y encapsular L4 ▶"
            ),
            # Stage 2: Gateway Routing
            StageDecision(
                stage_id="l3_gateway",
                layer_num=3,
                title="Capa de Red — Enrutamiento y puerta de enlace predeterminada",
                prompt=f"Persona A está en la subred 192.168.1.0/24. El servidor web resuelto es {self.resolved_ip} (WAN externa). ¿Adónde debe reenviar el paquete la capa 3?",
                explanation="Cuando las IP de destino están fuera de la máscara de subred local, la capa 3 no puede enviarlas directamente a la dirección MAC de destino; debe enrutarlas mediante el enrutador de la puerta de enlace predeterminada.",
                input_type="CHOICE",
                options=[
                    {
                        "id": "gateway",
                        "title": "Reenviar al enrutador de la puerta de enlace predeterminada (192.168.1.1)",
                        "desc": "El enrutador lee la IP de destino y la enruta a través de los enrutadores centrales de la WAN hasta 93.184.216.34."
                    },
                    {
                        "id": "direct_arp",
                        "title": "Enviar una difusión ARP directa en el conmutador local para 93.184.216.34",
                        "desc": "Difunde localmente con la esperanza de que el servidor externo esté conectado al mismo conmutador."
                    }
                ],
                default_value="gateway",
                button_label="Encapsular capa 3 y enrutar paquete ▶"
            ),
            # Stage 3: Server Response & Render
            StageDecision(
                stage_id="l7_render",
                layer_num=7,
                title="Capa de Aplicación — Renderizado del navegador",
                prompt="El servidor web recibió la solicitud GET y devolvió 'HTTP/1.1 200 OK' con la carga del documento HTML. Finaliza la transmisión:",
                explanation="El navegador de Persona A analiza la estructura del documento HTML, evalúa los estilos y renderiza la página web gráfica.",
                input_type="ACTION",
                options=[],
                button_label="Procesar HTML y renderizar página en el navegador ▶"
            )
        ]

        self.present_current_stage()

    def submit_user_decision(self, user_value: str, extra_data: Optional[Dict[str, Any]] = None):
        super().submit_user_decision(user_value, extra_data)
        stage = self.stages[self.current_stage_index]

        if stage.stage_id == "l7_dns":
            self.dns_server = user_value
            if self.dns_server != "8.8.8.8":
                self.update_layer("sender", 7, LayerStatus.ERROR, f"Fallo de DNS ({self.dns_server})", has_error=True)
                self.log("ERROR", "⚠", f"Consecuencia: el servidor de nombres {self.dns_server} no es válido o no está accesible. ¡No se puede resolver el dominio 'www.example.com'!", 7)

                def fix_dns():
                    self.dns_server = "8.8.8.8"
                    self.update_layer("sender", 7, LayerStatus.COMPLETE, f"IP resuelta: {self.resolved_ip}")
                    self.log("SUCCESS", "✓", f"Consulta DNS correcta: 'www.example.com' -> {self.resolved_ip} (mediante UDP 53 hacia 8.8.8.8)", 7)
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=7,
                    title="Fallo de resolución de nombres DNS",
                    summary=f"El sistema operativo no pudo resolver 'www.example.com' usando el servidor de nombres {self.dns_server}.",
                    details=(
                        "Sin un servidor DNS funcional, los navegadores web no pueden determinar a qué dirección IP conectarse.\n"
                        "0.0.0.0 es un destino no válido y 127.0.0.1 no tiene ningún servicio DNS activo en ejecución.\n\n"
                        "Para navegar por la web, configura el sistema con un resolvedor público válido como 8.8.8.8 (Google DNS) o 1.1.1.1 (Cloudflare)."
                    ),
                    options=[
                        RepairOption(
                            id="set_8888",
                            title="Configurar el DNS principal en 8.8.8.8 (recomendado)",
                            description="Usar el resolvedor DNS público recursivo de Google.",
                            is_correct=True,
                            feedback="¡Correcto! El servidor DNS devuelve el registro A 93.184.216.34."
                        ),
                        RepairOption(
                            id="skip_dns",
                            title="Enviar el paquete al nombre de dominio sin IP",
                            description="Enviar directamente un marco Ethernet con el nombre de texto.",
                            is_correct=False,
                            feedback="Incorrecto. Los enrutadores IP no pueden enrutar nombres de dominio de texto; requieren una IP numérica de 32 bits."
                        )
                    ],
                    on_repair_success=fix_dns
                )
                self.trigger_error(issue)
                return

            self.log("SUCCESS", "✓", f"L7 (DNS): 'www.example.com' resuelto -> {self.resolved_ip} (puerto UDP 53 hacia {self.dns_server})", 7)
            self.update_layer("sender", 7, LayerStatus.COMPLETE, f"IP resuelta: {self.resolved_ip}")
            self.inspector_data.app_protocol = "DNS / UDP 53"
            self.inspector_data.payload_text = f"Consulta: www.example.com -> Respuesta: {self.resolved_ip}"
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l4_l7_proto":
            if user_value == "port_8080":
                # Consequence: Connection refused!
                self.update_layer("sender", 4, LayerStatus.ERROR, "TCP RST: conexión rechazada (puerto 8080)", has_error=True)
                self.log("ERROR", "⚠", "Consecuencia: ¡el servidor 93.184.216.34 respondió con TCP [RST, ACK]! No hay ningún servicio web escuchando en el puerto 8080.", 4)

                def fix_proto():
                    self.selected_protocol = "HTTPS"
                    self.selected_port = 443
                    self.update_layer("sender", 4, LayerStatus.COMPLETE, "Puerto TCP 443 (HTTPS)")
                    self.log("SUCCESS", "✓", "Reparación: se cambió a HTTPS (puerto 443); el servidor web aceptó el puerto web cifrado estándar.", 4)
                    self._advance_to_next_stage()

                issue = TroubleshootIssue(
                    layer_num=4,
                    title="Puerto inaccesible (conexión TCP rechazada)",
                    summary="El equipo remoto recibió el segmento TCP SYN en el puerto 8080, pero devolvió un TCP RST (reinicio) porque ningún servidor web está vinculado al puerto 8080.",
                    details=(
                        "En la capa 4 (Transporte), los puertos de destino identifican procesos de software específicos del servidor.\n\n"
                        "Los servidores web públicos estándar solo tienen servicios de escucha vinculados en:\n"
                        "• Puerto 80: HTTP (texto plano)\n"
                        "• Puerto 443: HTTPS (seguro con TLS)\n\n"
                        "Conectarse a puertos arbitrarios como 8080 hace que el núcleo rechace inmediatamente la conexión con TCP RST."
                    ),
                    options=[
                        RepairOption(
                            id="fix_port_443",
                            title="Cambiar al puerto estándar 443 (HTTPS, recomendado)",
                            description="Conectarse al servicio de escucha seguro SSL/TLS del servidor web en el puerto 443.",
                            is_correct=True,
                            feedback="¡Correcto! El servidor acepta la conexión en el puerto 443."
                        ),
                        RepairOption(
                            id="keep_8080",
                            title="Reintentar continuamente en el puerto 8080",
                            description="Enviar repetidamente paquetes SYN al puerto 8080.",
                            is_correct=False,
                            feedback="Incorrecto. El puerto está cerrado; los intentos repetidos solo serán rechazados."
                        )
                    ],
                    on_repair_success=fix_proto
                )
                self.trigger_error(issue)
                return

            if user_value == "http_80":
                self.selected_protocol = "HTTP"
                self.selected_port = 80
                self.log("WARNING", "⚠", "L6/L4: se eligió HTTP en texto plano (puerto 80). Advertencia: los datos no están cifrados y pueden ser leídos por los analizadores de red.", 6)
                self.update_layer("sender", 6, LayerStatus.COMPLETE, "Texto plano (sin cifrado)")
                self.update_layer("sender", 4, LayerStatus.COMPLETE, "Puerto TCP 80 (HTTP)")
                self.inspector_data.encryption = "Ninguno (texto plano)"
            else:
                self.selected_protocol = "HTTPS"
                self.selected_port = 443
                self.log("INFO", "✓", "L6/L4: se eligió HTTPS (puerto 443). Se negoció el cifrado TLS 1.3 con el cifrado AES-256-GCM.", 6)
                self.update_layer("sender", 6, LayerStatus.COMPLETE, "Cifrado con TLS 1.3")
                self.update_layer("sender", 4, LayerStatus.COMPLETE, "Puerto TCP 443 (HTTPS)")
                self.inspector_data.encryption = "TLS 1.3 (AES-256-GCM)"

            self.inspector_data.transport_protocol = "TCP"
            self.inspector_data.dst_port = self.selected_port
            self.notify_inspector()
            self._advance_to_next_stage()

        elif stage.stage_id == "l3_gateway":
            if user_value == "direct_arp":
                # Consequence: ARP timeout!
                self.update_layer("sender", 3, LayerStatus.ERROR, "Discrepancia de subred (tiempo de espera de ARP)", has_error=True)
                self.log("ERROR", "⚠", "Consecuencia: el equipo 93.184.216.34 está en una red externa. ¡La difusión del conmutador local no puede alcanzar la IP externa de la WAN!", 3)

                def fix_gateway():
                    self.gateway_ip = "192.168.1.1"
                    self.update_layer("sender", 3, LayerStatus.COMPLETE, f"Enrutado a la puerta de enlace {self.gateway_ip}")
                    self.log("SUCCESS", "✓", "Reparación: el paquete se reenvió al enrutador de la puerta de enlace predeterminada (192.168.1.1).", 3)
                    self._transmit_web_request()

                issue = TroubleshootIssue(
                    layer_num=3,
                    title="Error de enrutamiento de capa 3: entrega fuera de la subred sin puerta de enlace",
                    summary=f"El cliente intentó resolver 93.184.216.34 mediante una difusión ARP local de capa 2 en lugar de enrutarlo mediante la puerta de enlace predeterminada 192.168.1.1.",
                    details=(
                        "Los equipos comprueban si una IP de destino coincide con su máscara de subred local (192.168.1.0/24).\n\n"
                        "Como 93.184.216.34 está fuera de 192.168.1.0/24, la computadora DEBE encapsular el paquete IP en un marco Ethernet dirigido a la dirección MAC del enrutador de la puerta de enlace predeterminada.\n"
                        "Enviar una difusión ARP en el conmutador local falla porque los conmutadores no reenvían las difusiones locales a Internet."
                    ),
                    options=[
                        RepairOption(
                            id="use_gateway",
                            title="Enrutar mediante la puerta de enlace predeterminada (192.168.1.1, recomendado)",
                            description="Enviar el marco a la dirección MAC del enrutador local para que pueda reenviar los paquetes a la WAN de Internet.",
                            is_correct=True,
                            feedback="¡Correcto! La puerta de enlace recibe el marco, reduce el TTL y enruta el paquete a la WAN."
                        ),
                        RepairOption(
                            id="change_mask",
                            title="Cambiar la máscara de subred a /0",
                            description="Considerar todo el espacio de direcciones como una sola subred local.",
                            is_correct=False,
                            feedback="Incorrecto. Los conmutadores no pueden gestionar dominios de difusión mundiales."
                        )
                    ],
                    on_repair_success=fix_gateway
                )
                self.trigger_error(issue)
                return

            self.update_layer("sender", 3, LayerStatus.COMPLETE, f"Enrutado a la puerta de enlace {self.gateway_ip}")
            self.update_layer("sender", 2, LayerStatus.COMPLETE, "Marco Ethernet a la dirección MAC del enrutador")
            self.update_layer("sender", 1, LayerStatus.COMPLETE, "Flujo de bits transmitido")
            self.log("INFO", "✓", f"L3/L2/L1: el paquete se reenvió a la puerta de enlace {self.gateway_ip} con destino {self.resolved_ip}:{self.selected_port}", 3)
            self._transmit_web_request()

        elif stage.stage_id == "l7_render":
            for lyr in range(1, 8):
                self.update_layer("receiver", lyr, LayerStatus.COMPLETE, "Desencapsulado y procesado")

            self.log("SUCCESS", "✓", "Persona A: se recibió HTTP 200 OK. ¡El HTML se analizó y se renderizó en la ventana del navegador!", 7)

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
                    self.ssl_badge.config(text="⚠ HTTP (no seguro)", fg=theme.COLOR_WARNING)

            if self.browser_status:
                self.browser_status.config(text="200 OK (Página cargada)", fg=theme.COLOR_SUCCESS)

            self.render_webpage()

            self.complete_mission({
                "Equipo objetivo": self.target_url,
                "Servidor DNS": f"{self.dns_server} (UDP 53)",
                "IP resuelta": self.resolved_ip,
                "Protocolo / puerto": f"{self.selected_protocol} (Puerto {self.selected_port})",
                "Ruta de enrutamiento": f"Equipo LAN -> Puerta de enlace {self.gateway_ip} -> Internet -> Servidor {self.resolved_ip}",
                "Decisiones tomadas": self.decisions_made,
                "Errores diagnosticados y corregidos": self.errors_repaired,
                "Resultado": "Página web renderizada correctamente"
            })

    def _transmit_web_request(self):
        """Transmit HTTP request to server and get response."""
        self.log("INFO", "→", f"Enviando la solicitud GET de {self.selected_protocol} a través de la puerta de enlace y de Internet hacia el servidor web...", None)

        def on_server_reached():
            self.packets_sent += 1
            self.log("INFO", "✓", "Servidor web (93.184.216.34): solicitud desencapsulada; generó la respuesta HTTP/1.1 200 OK (412 bytes).", 7)
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
