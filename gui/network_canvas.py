"""
Animated Network Canvas representing physical topology between Person A and Person B.
Displays Routers, Switches, cables, live packet flights, bitstream pulses, and packet drops.
"""

import tkinter as tk
from typing import Dict, Any, List, Optional, Callable, Tuple
import theme


class NetworkCanvas(tk.Frame):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg=theme.BG_DARK, bd=1, relief=tk.SOLID)

        self.canvas = tk.Canvas(self, bg=theme.BG_DARK, highlightthickness=0, height=180)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Node coordinates dictionary
        self.nodes: Dict[str, Tuple[float, float]] = {}

        # Animation states
        self.animating = False
        self.active_packet_id = None
        self.active_text_id = None

        # Stats
        self.stat_sent = 0
        self.stat_recv = 0
        self.stat_drop = 0

        self.canvas.bind("<Configure>", lambda e: self.redraw())

    def redraw(self):
        """Redraw static network topology elements."""
        self.canvas.delete("static")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if w < 50 or h < 50:
            return

        # Define 4-node or 5-node topology across width
        # Person A (Sender) -> Switch -> Router 1 -> Router 2 -> Person B (Receiver)
        y_center = h / 2

        x_person_a = w * 0.12
        x_switch = w * 0.32
        x_router1 = w * 0.52
        x_router2 = w * 0.70
        x_person_b = w * 0.88

        self.nodes = {
            "Person A": (x_person_a, y_center),
            "Switch": (x_switch, y_center),
            "Router": (x_router1, y_center),
            "Router 2": (x_router2, y_center),
            "Person B": (x_person_b, y_center),
        }

        # Draw physical cables / links
        links = [
            ("Person A", "Switch"),
            ("Switch", "Router"),
            ("Router", "Router 2"),
            ("Router 2", "Person B")
        ]

        for n1, n2 in links:
            x1, y1 = self.nodes[n1]
            x2, y2 = self.nodes[n2]
            # Shadow line
            self.canvas.create_line(x1, y1, x2, y2, fill="#1e293b", width=5, tags="static")
            # Cable line
            self.canvas.create_line(x1, y1, x2, y2, fill="#38bdf8", width=2, dash=(6, 4), tags="static")

        # Draw Nodes
        self._draw_node("Person A", x_person_a, y_center, "👤", "Persona A\n192.168.1.10", theme.OSI_COLORS[5])
        self._draw_node("Switch", x_switch, y_center, "🔀", "Switch\nCapa 2", theme.OSI_COLORS[2])
        self._draw_node("Router", x_router1, y_center, "🌐", "Router 1\nPuerta de enlace", theme.OSI_COLORS[3])
        self._draw_node("Router 2", x_router2, y_center, "🌐", "Router 2\nNúcleo WAN", theme.OSI_COLORS[3])
        self._draw_node("Person B", x_person_b, y_center, "👤", "Persona B\n192.168.1.25", theme.OSI_COLORS[1])

        # Bottom stats bar
        stats_text = f"Tráfico de red: Enviados: {self.stat_sent} | Recibidos: {self.stat_recv} | Perdidos: {self.stat_drop} | Enlace: 1000 Mbps Full-Dúplex"
        self.canvas.create_text(w / 2, h - 14, text=stats_text, fill=theme.TEXT_MUTED, font=theme.FONT_TINY, tags="static")

    def _draw_node(self, name: str, x: float, y: float, icon: str, label: str, color: str):
        # Outer glow circle
        r = 24
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=theme.BG_CARD, outline=color, width=2, tags="static")
        self.canvas.create_text(x, y - 2, text=icon, font=(theme.FONT_FAMILY, 15), tags="static")
        self.canvas.create_text(x, y + r + 16, text=label, font=theme.FONT_TINY, fill=theme.TEXT_SECONDARY, justify=tk.CENTER, tags="static")

    def animate_packet(
        self,
        from_node: str,
        to_node: str,
        packet_type: str,
        label: str,
        is_dropped: bool = False,
        on_complete: Optional[Callable[[], None]] = None,
        duration_ms: int = 700
    ):
        """Smoothly animate packet traveling from from_node to to_node."""
        if from_node not in self.nodes:
            from_node = "Person A"
        if to_node not in self.nodes:
            to_node = "Person B"

        x_start, y_start = self.nodes[from_node]
        x_end, y_end = self.nodes[to_node]

        # Intermediate waypoint if moving end-to-end
        # Path: Person A -> Switch -> Router -> Router 2 -> Person B
        if from_node == "Person A" and to_node == "Person B":
            waypoints = [
                self.nodes["Person A"],
                self.nodes["Switch"],
                self.nodes["Router"],
                self.nodes["Router 2"],
                self.nodes["Person B"]
            ]
        elif from_node == "Person B" and to_node == "Person A":
            waypoints = [
                self.nodes["Person B"],
                self.nodes["Router 2"],
                self.nodes["Router"],
                self.nodes["Switch"],
                self.nodes["Person A"]
            ]
        elif is_dropped and to_node == "Router":
            waypoints = [
                self.nodes["Person A"],
                self.nodes["Switch"],
                self.nodes["Router"]
            ]
        else:
            waypoints = [(x_start, y_start), (x_end, y_end)]

        self.canvas.delete("anim_packet")

        # Create animated packet badge
        color = theme.COLOR_WARNING if "UDP" in label or "Drop" in label else theme.COLOR_SUCCESS
        pkt_rect = self.canvas.create_rectangle(0, 0, 75, 22, fill=color, outline="#ffffff", width=1, tags="anim_packet")
        pkt_text = self.canvas.create_text(0, 0, text=label[:14], fill="#ffffff", font=theme.FONT_MONO_BOLD, tags="anim_packet")

        steps_total = 25
        delay = max(10, duration_ms // steps_total)

        # Calculate polyline points
        all_pts: List[Tuple[float, float]] = []
        for i in range(len(waypoints) - 1):
            p1 = waypoints[i]
            p2 = waypoints[i + 1]
            seg_steps = max(5, steps_total // (len(waypoints) - 1))
            for s in range(seg_steps):
                t = s / seg_steps
                px = p1[0] + (p2[0] - p1[0]) * t
                py = p1[1] + (p2[1] - p1[1]) * t
                all_pts.append((px, py))
        all_pts.append(waypoints[-1])

        def step_anim(idx: int):
            if idx < len(all_pts):
                cx, cy = all_pts[idx]
                w_box = 38
                h_box = 11
                self.canvas.coords(pkt_rect, cx - w_box, cy - h_box, cx + w_box, cy + h_box)
                self.canvas.coords(pkt_text, cx, cy)
                self.after(delay, lambda: step_anim(idx + 1))
            else:
                if is_dropped:
                    self.stat_drop += 1
                    # Show dropped explosion animation at current point
                    last_x, last_y = all_pts[-1]
                    self.canvas.create_text(last_x, last_y - 25, text="💥 PERDIDO (✗)", font=theme.FONT_BODY_BOLD, fill=theme.COLOR_ERROR, tags="anim_packet")
                    self.canvas.itemconfig(pkt_rect, fill=theme.COLOR_ERROR)
                    self.after(400, lambda: self._cleanup_and_callback(on_complete))
                else:
                    self.stat_recv += 1
                    self.after(100, lambda: self._cleanup_and_callback(on_complete))

        step_anim(0)

    def _cleanup_and_callback(self, cb: Optional[Callable[[], None]]):
        self.canvas.delete("anim_packet")
        self.redraw()
        if cb:
            cb()

    def update_stats(self, sent: int, recv: int, drop: int):
        self.stat_sent = sent
        self.stat_recv = recv
        self.stat_drop = drop
        self.redraw()
