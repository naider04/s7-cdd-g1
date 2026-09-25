"""
Mission Selection Screen for the OSI Communication Simulator.
Displays cards for all 7 missions with descriptions, concepts, and launch buttons.
"""

import tkinter as tk
from typing import List, Callable
import theme
from missions import get_all_missions, BaseMission


class MissionSelectView(tk.Frame):
    def __init__(self, parent: tk.Widget, on_select_mission: Callable[[int], None]):
        super().__init__(parent, bg=theme.BG_DARK)
        self.on_select_mission = on_select_mission

        # Header Area
        header = tk.Frame(self, bg=theme.BG_PANEL, padx=20, pady=16, bd=1, relief=tk.SOLID)
        header.pack(fill=tk.X)

        title_lbl = tk.Label(
            header,
            text="OSI COMMUNICATION SIMULATOR",
            font=theme.FONT_APP_TITLE,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_PANEL
        )
        title_lbl.pack(anchor=tk.W)

        subtitle_lbl = tk.Label(
            header,
            text="Interactive Educational Simulator of Computer Network Communication & Troubleshooting based on the 7 OSI Layers",
            font=theme.FONT_SMALL,
            fg=theme.TEXT_ACCENT,
            bg=theme.BG_PANEL
        )
        subtitle_lbl.pack(anchor=tk.W, pady=(2, 6))

        info_lbl = tk.Label(
            header,
            text="Choose any of the 4 core missions below. At each OSI layer, you must make real protocol decisions, configure addresses, or type input. Your choices have immediate network consequences!",
            font=theme.FONT_TINY,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PANEL
        )
        info_lbl.pack(anchor=tk.W)

        # Scrollable Canvas container for cards
        container = tk.Frame(self, bg=theme.BG_DARK)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        canvas = tk.Canvas(container, bg=theme.BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=theme.BG_DARK)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_canvas_configure(e):
            canvas.itemconfig(canvas_frame, width=e.width)

        canvas.bind("<Configure>", on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel support
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        # Render Mission Cards
        missions = get_all_missions()
        for m in missions:
            self._create_mission_card(scrollable_frame, m)

        # Footer OSI Layer legend bar
        footer = tk.Frame(self, bg=theme.BG_PANEL, padx=16, pady=8, bd=1, relief=tk.SOLID)
        footer.pack(fill=tk.X)

        tk.Label(footer, text="OSI 7 LAYERS:", font=theme.FONT_TINY, fg=theme.TEXT_MUTED, bg=theme.BG_PANEL).pack(side=tk.LEFT, padx=(0, 8))

        for l in range(7, 0, -1):
            meta = theme.OSI_METADATA[l]
            badge = tk.Label(
                footer,
                text=f"L{l} {meta['name']}",
                font=theme.FONT_TINY,
                fg="#ffffff",
                bg=meta['color'],
                padx=6,
                pady=1
            )
            badge.pack(side=tk.LEFT, padx=3)

    def _create_mission_card(self, parent: tk.Widget, mission: BaseMission):
        card = tk.Frame(parent, bg=theme.BG_CARD, bd=1, relief=tk.SOLID, padx=14, pady=12)
        card.pack(fill=tk.X, pady=6)

        # Left: Icon & Mission ID
        left = tk.Frame(card, bg=theme.BG_CARD, width=60)
        left.pack(side=tk.LEFT, padx=(0, 14))

        tk.Label(left, text=mission.icon, font=(theme.FONT_FAMILY, 24), bg=theme.BG_CARD).pack()
        tk.Label(left, text=f"Mission #{mission.mission_id}", font=theme.FONT_TINY, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack()

        # Middle: Title, Objective, and Concepts
        mid = tk.Frame(card, bg=theme.BG_CARD)
        mid.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(mid, text=mission.title, font=theme.FONT_SUBTITLE, fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD).pack(anchor=tk.W)
        tk.Label(mid, text=mission.subtitle, font=theme.FONT_BODY, fg=theme.TEXT_ACCENT, bg=theme.BG_CARD).pack(anchor=tk.W, pady=(1, 4))
        tk.Label(mid, text=mission.objective, font=theme.FONT_SMALL, fg=theme.TEXT_SECONDARY, bg=theme.BG_CARD, justify=tk.LEFT, wraplength=520).pack(anchor=tk.W, pady=(0, 6))

        # Concepts badges
        c_box = tk.Frame(mid, bg=theme.BG_CARD)
        c_box.pack(anchor=tk.W)

        for concept in mission.concepts[:3]:
            badge = tk.Label(
                c_box,
                text=concept,
                font=theme.FONT_TINY,
                fg=theme.TEXT_SECONDARY,
                bg="#1e293b",
                bd=1,
                relief=tk.FLAT,
                padx=6,
                pady=2
            )
            badge.pack(side=tk.LEFT, padx=(0, 6))

        # Right: Launch Button
        right = tk.Frame(card, bg=theme.BG_CARD)
        right.pack(side=tk.RIGHT, padx=6)

        btn = tk.Button(
            right,
            text="Start Mission ▶",
            font=theme.FONT_BODY_BOLD,
            bg=theme.OSI_COLORS[4],
            fg="#ffffff",
            activebackground="#0891b2",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=lambda mid=mission.mission_id: self.on_select_mission(mid)
        )
        btn.pack()
