"""
Interactive Diagnosis & Repair Modal Dialog.
Opens when a wrench 🔧 is clicked on an error layer. Explains the issue and allows
the user to apply the correct educational fix to resume transmission.
"""

import tkinter as tk
from typing import Optional, Callable
import theme
from models import TroubleshootIssue, RepairOption


class RepairDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, issue: TroubleshootIssue, on_repaired: Callable[[], None]):
        super().__init__(parent)
        self.issue = issue
        self.on_repaired = on_repaired
        self.selected_opt_id = tk.StringVar()

        meta = theme.OSI_METADATA.get(issue.layer_num, {"name": f"Layer {issue.layer_num}", "color": theme.COLOR_ERROR})

        self.title(f"Diagnostic & Repair: Layer {issue.layer_num} ({meta['name']})")
        self.geometry("620x540")
        self.resizable(False, False)
        self.configure(bg=theme.BG_DARK)
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        try:
            px = parent.winfo_rootx() + (parent.winfo_width() - 620) // 2
            py = parent.winfo_rooty() + (parent.winfo_height() - 540) // 2
            self.geometry(f"+{max(10, px)}+{max(10, py)}")
        except Exception:
            pass

        # Top Banner
        banner = tk.Frame(self, bg="#3b1111", padx=16, pady=12, bd=1, relief=tk.SOLID)
        banner.pack(fill=tk.X)

        tk.Label(banner, text=f"🔧 TROUBLESHOOTING: LAYER {issue.layer_num} — {meta['name'].upper()}", font=theme.FONT_TITLE, fg="#fca5a5", bg="#3b1111").pack(anchor=tk.W)
        tk.Label(banner, text=f"Problem: {issue.title}", font=theme.FONT_SUBTITLE, fg="#ffffff", bg="#3b1111").pack(anchor=tk.W, pady=(2, 0))

        # Main Body
        body = tk.Frame(self, bg=theme.BG_DARK, padx=16, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        # Problem description
        desc_box = tk.Frame(body, bg=theme.BG_PANEL, bd=1, relief=tk.SOLID, padx=12, pady=10)
        desc_box.pack(fill=tk.X, pady=(0, 10))

        tk.Label(desc_box, text="Diagnosis Details:", font=theme.FONT_BODY_BOLD, fg=theme.TEXT_ACCENT, bg=theme.BG_PANEL).pack(anchor=tk.W)
        tk.Label(desc_box, text=issue.details, font=theme.FONT_SMALL, fg=theme.TEXT_SECONDARY, bg=theme.BG_PANEL, justify=tk.LEFT, wraplength=560).pack(anchor=tk.W, pady=(4, 0))

        # Options Container
        tk.Label(body, text="Select Corrective Action:", font=theme.FONT_SUBTITLE, fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK).pack(anchor=tk.W, pady=(6, 4))

        self.options_frame = tk.Frame(body, bg=theme.BG_DARK)
        self.options_frame.pack(fill=tk.BOTH, expand=True)

        for i, opt in enumerate(issue.options):
            card = tk.Frame(self.options_frame, bg=theme.BG_CARD, bd=1, relief=tk.RIDGE, padx=10, pady=8)
            card.pack(fill=tk.X, pady=4)

            rb = tk.Radiobutton(
                card,
                text=opt.title,
                value=opt.id,
                variable=self.selected_opt_id,
                bg=theme.BG_CARD,
                fg=theme.TEXT_PRIMARY,
                selectcolor=theme.BG_DARK,
                activebackground=theme.BG_CARD,
                activeforeground=theme.TEXT_ACCENT,
                font=theme.FONT_BODY_BOLD
            )
            rb.pack(anchor=tk.W)

            tk.Label(card, text=opt.description, font=theme.FONT_TINY, fg=theme.TEXT_MUTED, bg=theme.BG_CARD, wraplength=540, justify=tk.LEFT).pack(anchor=tk.W, padx=(24, 0))

        # Feedback banner
        self.feedback_lbl = tk.Label(body, text="", font=theme.FONT_SMALL, fg=theme.COLOR_ERROR, bg=theme.BG_DARK, wraplength=560)
        self.feedback_lbl.pack(fill=tk.X, pady=6)

        # Bottom Button
        btn_frame = tk.Frame(self, bg=theme.BG_PANEL, padx=16, pady=10)
        btn_frame.pack(fill=tk.X)

        btn_apply = tk.Button(
            btn_frame,
            text="Apply Fix & Resume Transmission ▶",
            font=theme.FONT_BODY_BOLD,
            bg=theme.COLOR_SUCCESS,
            fg="#ffffff",
            activebackground="#059669",
            activeforeground="#ffffff",
            padx=14,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.submit_repair
        )
        btn_apply.pack(side=tk.RIGHT)

        btn_cancel = tk.Button(
            btn_frame,
            text="Close / Inspect Later",
            font=theme.FONT_SMALL,
            bg=theme.BG_CARD,
            fg=theme.TEXT_MUTED,
            padx=10,
            pady=6,
            relief=tk.FLAT,
            command=self.destroy
        )
        btn_cancel.pack(side=tk.RIGHT, padx=10)

        # Preselect first option
        if issue.options:
            self.selected_opt_id.set(issue.options[0].id)

    def submit_repair(self):
        choice_id = self.selected_opt_id.get()
        selected_opt: Optional[RepairOption] = None
        for o in self.issue.options:
            if o.id == choice_id:
                selected_opt = o
                break

        if not selected_opt:
            self.feedback_lbl.config(text="Please choose a corrective action.", fg=theme.COLOR_WARNING)
            return

        if selected_opt.is_correct:
            self.feedback_lbl.config(text=f"✓ {selected_opt.feedback}", fg=theme.COLOR_SUCCESS)
            self.update_idletasks()
            self.after(500, self._apply_and_close)
        else:
            self.feedback_lbl.config(text=f"✗ {selected_opt.feedback}", fg=theme.COLOR_ERROR)

    def _apply_and_close(self):
        self.destroy()
        self.on_repaired()
