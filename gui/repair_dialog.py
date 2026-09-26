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

        meta = theme.OSI_METADATA.get(issue.layer_num, {"name": f"Capa {issue.layer_num}", "color": theme.COLOR_ERROR})

        self.title(f"Diagnóstico y reparación: Capa {issue.layer_num} ({meta['name']})")
        self.geometry("640x560")
        self.minsize(620, 420)
        self.resizable(True, True)
        self.configure(bg=theme.BG_DARK)
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        try:
            px = parent.winfo_rootx() + (parent.winfo_width() - 640) // 2
            py = parent.winfo_rooty() + (parent.winfo_height() - 560) // 2
            self.geometry(f"+{max(10, px)}+{max(10, py)}")
        except Exception:
            pass

        # Bottom Button
        self.btn_frame = tk.Frame(self, bg=theme.BG_PANEL, padx=16, pady=10)
        self.btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Feedback banner
        self.feedback_lbl = tk.Label(
            self.btn_frame,
            text="",
            font=theme.FONT_SMALL,
            fg=theme.COLOR_ERROR,
            bg=theme.BG_PANEL,
            justify=tk.LEFT,
            anchor=tk.W,
            wraplength=560
        )
        self.feedback_lbl.pack(fill=tk.X, pady=(0, 6))

        btn_row = tk.Frame(self.btn_frame, bg=theme.BG_PANEL)
        btn_row.pack(fill=tk.X)

        self.btn_apply = tk.Button(
            btn_row,
            text="Aplicar corrección y reanudar transmisión ▶",
            font=theme.FONT_BODY_BOLD,
            bg=theme.COLOR_SUCCESS,
            fg="#ffffff",
            activebackground="#059669",
            activeforeground="#ffffff",
            padx=16,
            pady=8,
            bd=0,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.submit_repair
        )
        self.btn_apply.pack(side=tk.RIGHT)

        self.btn_cancel = tk.Button(
            btn_row,
            text="Cerrar / revisar después",
            font=theme.FONT_SMALL,
            bg=theme.BG_CARD,
            fg=theme.TEXT_MUTED,
            activebackground=theme.BG_CARD_HOVER,
            activeforeground=theme.TEXT_PRIMARY,
            padx=14,
            pady=8,
            bd=0,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.destroy
        )
        self.btn_cancel.pack(side=tk.RIGHT, padx=(0, 12))

        # Top Banner
        banner = tk.Frame(self, bg="#3b1111", padx=16, pady=12, bd=1, relief=tk.SOLID)
        banner.pack(fill=tk.X)

        tk.Label(banner, text=f"🔧 DIAGNÓSTICO: CAPA {issue.layer_num} — {meta['name'].upper()}", font=theme.FONT_TITLE, fg="#fca5a5", bg="#3b1111").pack(anchor=tk.W)
        tk.Label(banner, text=f"Problema: {issue.title}", font=theme.FONT_SUBTITLE, fg="#ffffff", bg="#3b1111", justify=tk.LEFT, wraplength=580).pack(anchor=tk.W, pady=(2, 0))

        scroll_area = tk.Frame(self, bg=theme.BG_DARK)
        scroll_area.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(scroll_area, orient=tk.VERTICAL, command=self._on_scrollbar)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.scroll_canvas = tk.Canvas(scroll_area, bg=theme.BG_DARK, highlightthickness=0, bd=0)
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)
        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        body = tk.Frame(self.scroll_canvas, bg=theme.BG_DARK, padx=16, pady=12)
        body_window = self.scroll_canvas.create_window((0, 0), window=body, anchor=tk.NW)

        body.bind(
            "<Configure>",
            lambda _e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        )
        self.scroll_canvas.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.itemconfigure(body_window, width=e.width)
        )

        self.bind("<Button-4>", self._on_mousewheel)
        self.bind("<Button-5>", self._on_mousewheel)
        self.bind("<MouseWheel>", self._on_mousewheel)

        # Main Body
        # Problem description
        desc_box = tk.Frame(body, bg=theme.BG_PANEL, bd=1, relief=tk.SOLID, padx=12, pady=10)
        desc_box.pack(fill=tk.X, pady=(0, 10))

        tk.Label(desc_box, text="Detalles del diagnóstico:", font=theme.FONT_BODY_BOLD, fg=theme.TEXT_ACCENT, bg=theme.BG_PANEL).pack(anchor=tk.W)
        tk.Label(desc_box, text=issue.details, font=theme.FONT_SMALL, fg=theme.TEXT_SECONDARY, bg=theme.BG_PANEL, justify=tk.LEFT, wraplength=540).pack(fill=tk.X, anchor=tk.W, pady=(4, 0))

        # Options Container
        tk.Label(body, text="Selecciona una acción correctiva:", font=theme.FONT_SUBTITLE, fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK).pack(anchor=tk.W, pady=(6, 4))

        self.options_frame = tk.Frame(body, bg=theme.BG_DARK)
        self.options_frame.pack(fill=tk.X)

        for opt in issue.options:
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
                font=theme.FONT_BODY_BOLD,
                justify=tk.LEFT,
                wraplength=480
            )
            rb.pack(fill=tk.X, anchor=tk.W)

            tk.Label(card, text=opt.description, font=theme.FONT_TINY, fg=theme.TEXT_MUTED, bg=theme.BG_CARD, wraplength=500, justify=tk.LEFT).pack(fill=tk.X, anchor=tk.W, padx=(24, 0))

        # Preselect first option
        if issue.options:
            self.selected_opt_id.set(issue.options[0].id)

    def _on_scrollbar(self, *args):
        self.scroll_canvas.yview(*args)

    def _on_mousewheel(self, event):
        if getattr(event, "num", None) == 4:
            delta = -1
        elif getattr(event, "num", None) == 5:
            delta = 1
        else:
            delta = -1 if event.delta > 0 else 1
        self.scroll_canvas.yview_scroll(delta, "units")
        return "break"

    def submit_repair(self):
        choice_id = self.selected_opt_id.get()
        selected_opt: Optional[RepairOption] = None
        for o in self.issue.options:
            if o.id == choice_id:
                selected_opt = o
                break

        if not selected_opt:
            self.feedback_lbl.config(text="Elige una acción correctiva.", fg=theme.COLOR_WARNING)
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
