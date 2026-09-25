"""
Event Log Widget for tracking chronological simulation events, status changes,
packet transmissions, errors, and repairs.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List
import theme
from models import LogEvent
from utils.helpers import get_timestamp


class EventLogWidget(tk.Frame):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg=theme.BG_PANEL, padx=8, pady=6)

        self.events: List[LogEvent] = []
        self.active_filter = "ALL"

        # Top controls
        top_bar = tk.Frame(self, bg=theme.BG_PANEL)
        top_bar.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            top_bar,
            text="📋 Chronological Event Log",
            font=theme.FONT_SUBTITLE,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_PANEL
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Filter buttons
        self.btn_all = tk.Button(top_bar, text="All", font=theme.FONT_TINY, bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY, bd=0, padx=6, command=lambda: self.set_filter("ALL"))
        self.btn_all.pack(side=tk.LEFT, padx=2)

        self.btn_warn = tk.Button(top_bar, text="⚠ Issues", font=theme.FONT_TINY, bg=theme.BG_CARD, fg=theme.COLOR_WARNING, bd=0, padx=6, command=lambda: self.set_filter("ISSUES"))
        self.btn_warn.pack(side=tk.LEFT, padx=2)

        btn_clear = tk.Button(top_bar, text="Clear", font=theme.FONT_TINY, bg=theme.BG_CARD, fg=theme.TEXT_MUTED, bd=0, padx=6, command=self.clear_log)
        btn_clear.pack(side=tk.RIGHT)

        # Scrollable Text area
        text_frame = tk.Frame(self, bg=theme.BG_CARD, bd=1, relief=tk.SOLID)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(
            text_frame,
            font=theme.FONT_MONO,
            bg=theme.BG_DARK,
            fg=theme.TEXT_PRIMARY,
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD,
            bd=0,
            padx=8,
            pady=6
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_widget.yview)

        # Color Tags configuration
        self.text_widget.tag_config("SUCCESS", foreground=theme.COLOR_SUCCESS)
        self.text_widget.tag_config("WARNING", foreground=theme.COLOR_WARNING)
        self.text_widget.tag_config("ERROR", foreground=theme.COLOR_ERROR)
        self.text_widget.tag_config("STEP", foreground=theme.TEXT_ACCENT)
        self.text_widget.tag_config("INFO", foreground=theme.TEXT_SECONDARY)
        self.text_widget.tag_config("TIME", foreground=theme.TEXT_MUTED)
        self.text_widget.tag_config("LAYER", foreground="#c084fc")

        self.text_widget.config(state="disabled")

    def log(self, level: str, icon: str, message: str, layer_num: Optional[int] = None):
        """Append an event to the log."""
        ts = get_timestamp()
        event = LogEvent(timestamp=ts, level=level, icon=icon, message=message, layer_num=layer_num)
        self.events.append(event)
        self._append_entry(event)

    def _append_entry(self, event: LogEvent):
        if self.active_filter == "ISSUES" and event.level not in ["WARNING", "ERROR"]:
            return

        self.text_widget.config(state="normal")
        self.text_widget.insert(tk.END, f"[{event.timestamp}] ", "TIME")

        if event.layer_num:
            self.text_widget.insert(tk.END, f"[L{event.layer_num}] ", "LAYER")

        self.text_widget.insert(tk.END, f"{event.icon} ", event.level)
        self.text_widget.insert(tk.END, f"{event.message}\n", event.level)
        self.text_widget.see(tk.END)
        self.text_widget.config(state="disabled")

    def set_filter(self, filter_mode: str):
        self.active_filter = filter_mode
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.config(state="disabled")

        for ev in self.events:
            self._append_entry(ev)

    def clear_log(self):
        self.events.clear()
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.config(state="disabled")
