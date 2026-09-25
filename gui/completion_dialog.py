"""
Mission Completion Modal Dialog.
Celebrates mission completion, presents key OSI learning outcomes,
and allows returning to the mission selector.
"""

import tkinter as tk
from typing import Dict, Any, Callable
import theme


class CompletionDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Widget,
        mission_title: str,
        summary_stats: Dict[str, Any],
        on_return_missions: Callable[[], None],
        on_replay: Callable[[], None]
    ):
        super().__init__(parent)
        self.on_return_missions = on_return_missions
        self.on_replay = on_replay

        self.title("Communication Complete!")
        self.geometry("560x500")
        self.resizable(False, False)
        self.configure(bg=theme.BG_DARK)
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        try:
            px = parent.winfo_rootx() + (parent.winfo_width() - 560) // 2
            py = parent.winfo_rooty() + (parent.winfo_height() - 500) // 2
            self.geometry(f"+{max(10, px)}+{max(10, py)}")
        except Exception:
            pass

        # Top Banner
        top = tk.Frame(self, bg="#064e3b", padx=16, pady=14, bd=1, relief=tk.SOLID)
        top.pack(fill=tk.X)

        tk.Label(top, text="🎉 COMMUNICATION COMPLETE!", font=theme.FONT_TITLE, fg=theme.COLOR_SUCCESS, bg="#064e3b").pack(anchor=tk.W)
        tk.Label(top, text=f"Mission: {mission_title}", font=theme.FONT_BODY, fg="#d1fae5", bg="#064e3b").pack(anchor=tk.W, pady=(2, 0))

        # Body
        body = tk.Frame(self, bg=theme.BG_DARK, padx=16, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        # Milestone Checkmarks
        box_checks = tk.Frame(body, bg=theme.BG_PANEL, bd=1, relief=tk.SOLID, padx=12, pady=10)
        box_checks.pack(fill=tk.X, pady=(0, 10))

        checks = [
            "✓ Application Data Encapsulated (L7 → L1)",
            "✓ Physical Bitstream Transmitted across Network",
            "✓ Packets Routed & Switched correctly",
            "✓ Data Link FCS Integrity Verified",
            "✓ Receiver Decapsulated & Reconstructed (L1 → L7)"
        ]
        for c in checks:
            tk.Label(box_checks, text=c, font=theme.FONT_SMALL, fg=theme.COLOR_SUCCESS, bg=theme.BG_PANEL).pack(anchor=tk.W, pady=1)

        # Mission Summary Metrics
        tk.Label(body, text="Transmission Summary & OSI Metrics:", font=theme.FONT_SUBTITLE, fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK).pack(anchor=tk.W, pady=(4, 4))

        stats_box = tk.Frame(body, bg=theme.BG_CARD, bd=1, relief=tk.SOLID, padx=12, pady=10)
        stats_box.pack(fill=tk.BOTH, expand=True)

        for k, v in summary_stats.items():
            row = tk.Frame(stats_box, bg=theme.BG_CARD)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"{k}:", font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD, width=22, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=str(v), font=theme.FONT_BODY_BOLD, fg=theme.TEXT_ACCENT, bg=theme.BG_CARD, wraplength=300, justify=tk.LEFT, anchor=tk.W).pack(side=tk.LEFT)

        # Bottom Buttons
        btn_bar = tk.Frame(self, bg=theme.BG_PANEL, padx=16, pady=12)
        btn_bar.pack(fill=tk.X)

        btn_return = tk.Button(
            btn_bar,
            text="📁 Return to Mission Selection",
            font=theme.FONT_BODY_BOLD,
            bg=theme.OSI_COLORS[5],
            fg="#ffffff",
            activebackground="#2563eb",
            activeforeground="#ffffff",
            padx=14,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2",
            command=self._handle_return
        )
        btn_return.pack(side=tk.RIGHT)

        btn_replay = tk.Button(
            btn_bar,
            text="↺ Replay Mission",
            font=theme.FONT_BODY,
            bg=theme.BG_CARD,
            fg=theme.TEXT_PRIMARY,
            padx=10,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2",
            command=self._handle_replay
        )
        btn_replay.pack(side=tk.RIGHT, padx=10)

    def _handle_return(self):
        self.destroy()
        self.on_return_missions()

    def _handle_replay(self):
        self.destroy()
        self.on_replay()
