"""
Packet & Frame Inspector widget.
Allows tangible inspection of encapsulated protocol headers, flags, MAC/IP/Port addresses,
and raw hex payload data at each OSI layer.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
import theme
from models import PacketInspectorData


class InspectorWidget(tk.Frame):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg=theme.BG_PANEL, padx=10, pady=8)

        self.current_data = PacketInspectorData()
        self.selected_layer = 4  # Default to Transport Layer

        # Top banner with Layer tabs
        top_bar = tk.Frame(self, bg=theme.BG_PANEL)
        top_bar.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            top_bar,
            text="🔍 Deep Packet Inspector",
            font=theme.FONT_SUBTITLE,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_PANEL
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Layer tab buttons
        self.tab_buttons: Dict[int, tk.Button] = {}
        layers_order = [2, 3, 4, 5, 6, 7, 1]

        for lyr in layers_order:
            meta = theme.OSI_METADATA[lyr]
            btn = tk.Button(
                top_bar,
                text=f"L{lyr} {meta['name']}",
                font=theme.FONT_TINY,
                bg=theme.BG_CARD,
                fg=theme.TEXT_SECONDARY,
                activebackground=meta['color'],
                activeforeground="#ffffff",
                relief=tk.FLAT,
                bd=0,
                padx=6,
                pady=2,
                cursor="hand2",
                command=lambda l=lyr: self.select_layer(l)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.tab_buttons[lyr] = btn

        # Main inspection split pane (Left: Fields Table, Right: Hex Dump & Raw Payload)
        content_pane = tk.Frame(self, bg=theme.BG_PANEL)
        content_pane.pack(fill=tk.BOTH, expand=True)

        # Left Column: Layer Header Details
        self.left_col = tk.Frame(content_pane, bg=theme.BG_CARD, bd=1, relief=tk.SOLID, padx=10, pady=8)
        self.left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        self.lbl_layer_title = tk.Label(self.left_col, text="", font=theme.FONT_BODY_BOLD, fg=theme.TEXT_ACCENT, bg=theme.BG_CARD)
        self.lbl_layer_title.pack(anchor=tk.W, pady=(0, 4))

        self.fields_container = tk.Frame(self.left_col, bg=theme.BG_CARD)
        self.fields_container.pack(fill=tk.BOTH, expand=True)

        # Right Column: Raw Hex Dump & Payload
        self.right_col = tk.Frame(content_pane, bg=theme.BG_CARD, bd=1, relief=tk.SOLID, padx=10, pady=8, width=320)
        self.right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        tk.Label(self.right_col, text="Raw Payload / Hex Dissection", font=theme.FONT_BODY_BOLD, fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD).pack(anchor=tk.W)

        self.hex_text = tk.Text(
            self.right_col,
            font=theme.FONT_MONO,
            bg=theme.BG_DARK,
            fg="#a7f3d0",
            insertbackground="white",
            wrap=tk.NONE,
            height=8,
            width=36,
            bd=0
        )
        self.hex_text.pack(fill=tk.BOTH, expand=True, pady=4)
        self.hex_text.config(state="disabled")

        # Bottom visual encapsulation banner
        self.encap_banner = tk.Label(
            self,
            text="",
            font=theme.FONT_MONO,
            fg=theme.TEXT_ACCENT,
            bg=theme.BG_DARK,
            relief=tk.SUNKEN,
            bd=1,
            padx=8,
            pady=3
        )
        self.encap_banner.pack(fill=tk.X, pady=(6, 0))

        self.select_layer(4)

    def select_layer(self, layer_num: int):
        self.selected_layer = layer_num
        for lyr, btn in self.tab_buttons.items():
            if lyr == layer_num:
                btn.config(bg=theme.OSI_METADATA[lyr]['color'], fg="#ffffff", font=theme.FONT_SMALL)
            else:
                btn.config(bg=theme.BG_CARD, fg=theme.TEXT_MUTED, font=theme.FONT_TINY)
        self.render()

    def update_data(self, data: PacketInspectorData):
        self.current_data = data
        self.render()

    def render(self):
        d = self.current_data
        lyr = self.selected_layer
        meta = theme.OSI_METADATA[lyr]

        self.lbl_layer_title.config(
            text=f"Layer {lyr} — {meta['name']} Protocol Data Unit [{meta['pdu']}]",
            fg=meta['color']
        )

        for w in self.fields_container.winfo_children():
            w.destroy()

        fields = []
        if lyr == 7:  # Application
            fields = [
                ("Protocol:", d.app_protocol),
                ("Data Payload Size:", f"{d.raw_size_bytes} Bytes"),
                ("Format / MIME:", "Text / JSON / Binary Stream"),
                ("Payload Preview:", d.payload_text[:40] + ("..." if len(d.payload_text) > 40 else ""))
            ]
        elif lyr == 6:  # Presentation
            fields = [
                ("Character Encoding:", d.encoding),
                ("Data Compression:", d.compression),
                ("Encryption / Cipher:", d.encryption),
                ("Data Formatting:", "MIME / Abstract Syntax Notation (ASN.1)")
            ]
        elif lyr == 5:  # Session
            fields = [
                ("Session Identifier:", d.session_id),
                ("Connection State:", d.session_state),
                ("Authentication Token:", d.session_token),
                ("Dialog Management:", "Full-Duplex Synchronized")
            ]
        elif lyr == 4:  # Transport
            fields = [
                ("Transport Protocol:", d.transport_protocol),
                ("Source Port:", str(d.src_port)),
                ("Destination Port:", str(d.dst_port)),
                ("Sequence Number:", str(d.seq_num)),
                ("Acknowledgment (ACK):", str(d.ack_num)),
                ("Control Flags:", d.flags),
                ("Window Size:", f"{d.window_size} bytes (Flow Control)")
            ]
        elif lyr == 3:  # Network
            fields = [
                ("IP Version:", d.ip_version),
                ("Source IP Address:", d.ip_src),
                ("Destination IP Address:", d.ip_dst),
                ("Time To Live (TTL):", str(d.ip_ttl)),
                ("Encapsulated Protocol:", d.ip_protocol),
                ("Header Checksum:", d.ip_checksum)
            ]
        elif lyr == 2:  # Data Link
            fields = [
                ("Frame Type:", d.frame_type),
                ("Source MAC Address:", d.frame_src_mac),
                ("Destination MAC Address:", d.frame_dst_mac),
                ("Frame Check Sequence (FCS):", d.frame_fcs),
                ("MTU Payload Size:", "1500 bytes")
            ]
        elif lyr == 1:  # Physical
            fields = [
                ("Physical Transmission:", "Baseband Electrical / Optical Pulses"),
                ("Encoding Scheme:", "Manchester / 4B5B Line Coding"),
                ("Medium:", "Category 6 UTP Copper Cable (1 Gbps)"),
                ("Raw Bits Output:", d.bitstream[:38] + "...")
            ]

        # Populate Fields Grid
        for label, val in fields:
            row = tk.Frame(self.fields_container, bg=theme.BG_CARD)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=label, font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD, width=22, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=val, font=theme.FONT_MONO, fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X)

        # Update Hex Dump
        self.hex_text.config(state="normal")
        self.hex_text.delete("1.0", tk.END)
        self.hex_text.insert(tk.END, d.payload_hex or "(Empty payload)")
        self.hex_text.config(state="disabled")

        # Visual encapsulation hierarchy bar
        encap_text = (
            f"[ Eth Header (Dst: {d.frame_dst_mac[:8]}..) "
            f"[ IP (Dst: {d.ip_dst}) "
            f"[ {d.transport_protocol} (DstPort: {d.dst_port}) "
            f"[ {d.app_protocol} Payload: {d.raw_size_bytes}B ] ] ] "
            f"FCS: {d.frame_fcs[:10]} ]"
        )
        self.encap_banner.config(text=encap_text)
