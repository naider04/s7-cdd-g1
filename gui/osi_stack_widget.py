"""
OSI 7-Layer Stack Widget for Sender and Receiver endpoints.
Displays all 7 layers, their PDU names, status indicators, and interactive wrench repair buttons.
"""

import tkinter as tk
from typing import Dict, Optional, Callable
import theme
from models import LayerStatus


class LayerCard(tk.Frame):
    """Visual card for a single OSI layer in the stack."""
    def __init__(
        self,
        parent: tk.Widget,
        layer_num: int,
        is_sender: bool,
        on_click: Optional[Callable[[int], None]] = None,
        on_wrench_click: Optional[Callable[[int], None]] = None
    ):
        super().__init__(parent, bg=theme.BG_CARD, bd=0, relief=tk.FLAT, padx=6, pady=0)
        self.layer_num = layer_num
        self.is_sender = is_sender
        self.on_click = on_click
        self.on_wrench_click = on_wrench_click
        self.status = LayerStatus.IDLE
        self.has_error = False

        meta = theme.OSI_METADATA[layer_num]
        self.layer_color = meta["color"]

        # Accent color stripe
        self.stripe = tk.Frame(self, bg=self.layer_color, width=4)
        self.stripe.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        # Content container
        content = tk.Frame(self, bg=theme.BG_CARD)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Row 1: Layer Number, Name, and PDU Badge
        row1 = tk.Frame(content, bg=theme.BG_CARD)
        row1.pack(fill=tk.X)

        self.lbl_title = tk.Label(
            row1,
            text=f"L{layer_num} {meta['name']}",
            font=theme.FONT_TINY,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_CARD
        )
        self.lbl_title.pack(side=tk.LEFT)

        self.lbl_pdu = tk.Label(
            row1,
            text=f"[{meta['pdu']}]",
            font=theme.FONT_TINY,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        )
        self.lbl_pdu.pack(side=tk.LEFT, padx=4)

        # Wrench button (hidden by default)
        self.btn_wrench = tk.Button(
            row1,
            text="🔧 REPARAR",
            font=theme.FONT_TINY,
            bg=theme.COLOR_ERROR,
            fg="#ffffff",
            activebackground="#dc2626",
            activeforeground="#ffffff",
            relief=tk.RAISED,
            bd=1,
            cursor="hand2",
            padx=4,
            pady=0,
            command=self._handle_wrench
        )

        # Row 2: Status text
        self.lbl_status = tk.Label(
            content,
            text="Inactivo",
            font=theme.FONT_TINY,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD,
            anchor=tk.W
        )
        self.lbl_status.pack(fill=tk.X)

        # Bind clicks
        self.bind("<Button-1>", lambda e: self._handle_click())
        content.bind("<Button-1>", lambda e: self._handle_click())
        self.lbl_title.bind("<Button-1>", lambda e: self._handle_click())
        self.lbl_status.bind("<Button-1>", lambda e: self._handle_click())

    def _handle_click(self):
        if self.on_click:
            self.on_click(self.layer_num)

    def _handle_wrench(self):
        if self.on_wrench_click:
            self.on_wrench_click(self.layer_num)

    def set_status(self, status: LayerStatus, status_text: str, has_error: bool = False):
        self.status = status
        self.has_error = has_error
        self.lbl_status.config(text=status_text)

        if has_error or status == LayerStatus.ERROR:
            self.config(bg="#3a1c1c", highlightbackground=theme.COLOR_ERROR, highlightthickness=2)
            self.lbl_title.config(bg="#3a1c1c", fg="#fca5a5")
            self.lbl_status.config(bg="#3a1c1c", fg=theme.COLOR_ERROR)
            self.lbl_pdu.config(bg="#3a1c1c")
            self.stripe.config(bg=theme.COLOR_ERROR)
            self.btn_wrench.pack(side=tk.RIGHT, padx=2)
        elif status == LayerStatus.ACTIVE:
            self.config(bg="#1e293b", highlightbackground=self.layer_color, highlightthickness=2)
            self.lbl_title.config(bg="#1e293b", fg=self.layer_color)
            self.lbl_status.config(bg="#1e293b", fg=theme.TEXT_ACCENT)
            self.lbl_pdu.config(bg="#1e293b")
            self.stripe.config(bg=self.layer_color)
            self.btn_wrench.pack_forget()
        elif status == LayerStatus.COMPLETE:
            self.config(bg=theme.BG_CARD, highlightthickness=1, highlightbackground=theme.COLOR_SUCCESS)
            self.lbl_title.config(bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY)
            self.lbl_status.config(bg=theme.BG_CARD, fg=theme.COLOR_SUCCESS)
            self.lbl_pdu.config(bg=theme.BG_CARD)
            self.stripe.config(bg=theme.COLOR_SUCCESS)
            self.btn_wrench.pack_forget()
        else:  # IDLE
            self.config(bg=theme.BG_CARD, highlightthickness=0)
            self.lbl_title.config(bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY)
            self.lbl_status.config(bg=theme.BG_CARD, fg=theme.TEXT_MUTED)
            self.lbl_pdu.config(bg=theme.BG_CARD)
            self.stripe.config(bg=self.layer_color)
            self.btn_wrench.pack_forget()


class OsiStackWidget(tk.Frame):
    """
    Vertical stack displaying the 7 OSI layers for Sender (L7->L1) or Receiver (L1->L7).
    """
    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        subtitle: str,
        is_sender: bool,
        on_layer_select: Optional[Callable[[int], None]] = None,
        on_repair_trigger: Optional[Callable[[int], None]] = None
    ):
        super().__init__(parent, bg=theme.BG_PANEL, bd=1, relief=tk.SOLID, padx=6, pady=0)
        self.title = title
        self.is_sender = is_sender
        self.on_layer_select = on_layer_select
        self.on_repair_trigger = on_repair_trigger

        self.cards: Dict[int, LayerCard] = {}

        # Header
        header = tk.Frame(self, bg=theme.BG_PANEL)
        header.pack(fill=tk.X, pady=0)

        tk.Label(
            header,
            text=title,
            font=theme.FONT_SUBTITLE,
            fg=theme.TEXT_ACCENT if is_sender else theme.COLOR_SUCCESS,
            bg=theme.BG_PANEL
        ).pack(anchor=tk.W)

        direction_text = "ENCAPSULACIÓN: L7 → L1 ↓" if is_sender else "DESENCAPSULACIÓN: L1 → L7 ↑"
        tk.Label(
            header,
            text=f"{subtitle} | {direction_text}",
            font=theme.FONT_TINY,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PANEL
        ).pack(anchor=tk.W)

        # Layer Cards container
        stack_frame = tk.Frame(self, bg=theme.BG_PANEL)
        stack_frame.pack(fill=tk.BOTH, expand=True)

        # Ordering: Sender shows L7 down to L1; Receiver shows L7 down to L1 for side-by-side comparison
        layers_order = [7, 6, 5, 4, 3, 2, 1]

        for lyr in layers_order:
            card = LayerCard(
                stack_frame,
                layer_num=lyr,
                is_sender=is_sender,
                on_click=self.on_layer_select,
                on_wrench_click=self.on_repair_trigger
            )
            card.pack(fill=tk.X, pady=0)
            self.cards[lyr] = card

    def update_layer_status(self, layer_num: int, status: LayerStatus, status_text: str, has_error: bool = False):
        if layer_num in self.cards:
            self.cards[layer_num].set_status(status, status_text, has_error)

    def reset_all(self):
        for card in self.cards.values():
            card.set_status(LayerStatus.IDLE, "Listo", False)
