"""
Laboratorio de cascada OSI.
Muestra la transmision real calculada por osi_engine: encapsulamiento L7 -> L1
en PC-A, desencapsulamiento L1 -> L7 en PC-B, la cadena base64 de la capa 6,
el checksum IP, el CRC32 de la capa 2 y el flujo de bits de la capa 1.
"""

import tkinter as tk
from typing import List
import theme
from osi_engine import CAPAS, FcsMismatchError, bytes_a_hex, desencapsular, encapsular

MENSAJ_EJEMPLO = "Hola PC-B, mensaje enviado con acentos y emoji"


class CascadePanel(tk.Frame):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg=theme.BG_PANEL)
        self.mensaje_var = tk.StringVar(value=MENSAJ_EJEMPLO)
        self.corrupcion_var = tk.BooleanVar(value=False)

        self._build_controls()
        self._build_output()
        self._mostrar_instrucciones()

    @classmethod
    def abrir(cls, parent: tk.Widget) -> tk.Toplevel:
        """Abre el laboratorio de cascada en una ventana independiente."""
        ventana = tk.Toplevel(parent)
        ventana.title("Laboratorio de cascada OSI - transmitir() / base64 / CRC32")
        ventana.geometry("980x740")
        ventana.minsize(760, 520)
        ventana.configure(bg=theme.BG_DARK)
        panel = cls(ventana)
        panel.pack(fill=tk.BOTH, expand=True)
        return ventana

    def _build_controls(self):
        top = tk.Frame(self, bg=theme.BG_PANEL, padx=12, pady=10)
        top.pack(fill=tk.X)

        tk.Label(
            top,
            text="Mensaje que Persona A envía a Persona B:",
            font=theme.FONT_BODY_BOLD,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_PANEL
        ).pack(side=tk.LEFT)

        entry = tk.Entry(
            top,
            textvariable=self.mensaje_var,
            font=theme.FONT_BODY,
            bg=theme.BG_INPUT,
            fg=theme.TEXT_PRIMARY,
            insertbackground="#ffffff",
            relief=tk.FLAT,
            bd=0
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        entry.bind("<Return>", lambda _e: self.transmitir())

        tk.Checkbutton(
            top,
            text="Alterar 1 bit en el medio",
            variable=self.corrupcion_var,
            bg=theme.BG_PANEL,
            fg=theme.COLOR_WARNING,
            activebackground=theme.BG_PANEL,
            activeforeground=theme.COLOR_WARNING,
            selectcolor=theme.BG_CARD,
            font=theme.FONT_TINY,
            bd=0
        ).pack(side=tk.LEFT, padx=(0, 12))

        tk.Button(
            top,
            text="Transmitir ▶",
            font=theme.FONT_BODY_BOLD,
            bg=theme.OSI_COLORS[4],
            fg="#ffffff",
            activebackground="#0891b2",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=18,
            pady=6,
            cursor="hand2",
            command=self.transmitir
        ).pack(side=tk.RIGHT)

        self.resultado_lbl = tk.Label(
            self,
            text="",
            font=theme.FONT_BODY_BOLD,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PANEL,
            anchor=tk.W,
            padx=12
        )
        self.resultado_lbl.pack(fill=tk.X, pady=(0, 6))

    def _build_output(self):
        paned = tk.PanedWindow(self, orient=tk.VERTICAL, bg=theme.BORDER, bd=0, sashwidth=4)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self.log_text = self._crear_texto(paned, 380, wrap=tk.WORD)
        self.trama_text = self._crear_texto(paned, 150, wrap=tk.NONE, scroll_x=True)

    def _crear_texto(self, parent: tk.Widget, minsize: int, wrap: str, scroll_x: bool = False) -> tk.Text:
        box = tk.Frame(parent, bg=theme.BG_CARD)
        parent.add(box, minsize=minsize, stretch="always")

        texto = tk.Text(
            box,
            bg=theme.BG_CARD,
            fg=theme.TEXT_SECONDARY,
            font=theme.FONT_MONO,
            wrap=wrap,
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=8,
            state=tk.DISABLED
        )

        vsb = tk.Scrollbar(
            box,
            orient=tk.VERTICAL,
            command=texto.yview,
            width=12,
            bd=0,
            highlightthickness=0,
            bg=theme.BG_INPUT,
            troughcolor=theme.BG_PANEL,
            activebackground=theme.TEXT_MUTED
        )
        texto.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if scroll_x:
            hsb = tk.Scrollbar(
                box,
                orient=tk.HORIZONTAL,
                command=texto.xview,
                width=12,
                bd=0,
                highlightthickness=0,
                bg=theme.BG_INPUT,
                troughcolor=theme.BG_PANEL,
                activebackground=theme.TEXT_MUTED
            )
            texto.configure(xscrollcommand=hsb.set)
            hsb.pack(side=tk.BOTTOM, fill=tk.X)

        texto.tag_configure("hdr", font=theme.FONT_MONO_BOLD, foreground=theme.TEXT_ACCENT)
        texto.tag_configure("capa", font=theme.FONT_MONO_BOLD, foreground=theme.TEXT_PRIMARY)
        texto.tag_configure("dato", foreground=theme.TEXT_SECONDARY)
        texto.tag_configure("entra", foreground=theme.TEXT_MUTED)
        texto.tag_configure("alta", foreground=theme.COLOR_SUCCESS)
        texto.tag_configure("baja", foreground=theme.COLOR_WARNING)
        texto.tag_configure("tec", font=(theme.FONT_CODE, 8, "italic"), foreground=theme.TEXT_MUTED)
        texto.tag_configure("ok", font=theme.FONT_MONO_BOLD, foreground=theme.COLOR_SUCCESS)
        texto.tag_configure("error", font=theme.FONT_MONO_BOLD, foreground=theme.COLOR_ERROR)
        return texto

    def _escribir(self, texto: str, tag: str = "dato"):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, texto, tag)
        self.log_text.configure(state=tk.DISABLED)

    def _escribir_trama(self, texto: str, tag: str = "dato"):
        self.trama_text.configure(state=tk.NORMAL)
        self.trama_text.insert(tk.END, texto, tag)
        self.trama_text.configure(state=tk.DISABLED)

    def _limpiar(self):
        for texto in (self.log_text, self.trama_text):
            texto.configure(state=tk.NORMAL)
            texto.delete("1.0", tk.END)
            texto.configure(state=tk.DISABLED)

    def _mostrar_instrucciones(self):
        capas = "  ->  ".join(f"L{num} {CAPAS[num]}" for num in range(7, 0, -1))
        self._escribir("PASO 0 · Punto inicial\n")
        self._escribir("  PC-A tiene el mensaje y PC-B espera. Todavía no hay ningún byte en el medio.\n")
        self._escribir("  El recorrido completo será:\n")
        self._escribir(f"  Envío       : {capas}\n", "alta")
        self._escribir(f"  Recepción  : {'  ->  '.join(f'L{num} {CAPAS[num]}' for num in range(1, 8))}\n", "baja")
        self._escribir("\n  Escribe un mensaje y pulsa «Transmitir ▶».\n")

    def transmitir(self) -> None:
        """Ejecuta osi_engine.transmitir() y vuelca los 14 pasos en pantalla."""
        mensaje = self.mensaje_var.get()
        if not mensaje.strip():
            self.resultado_lbl.config(text="✗ Escribe un mensaje antes de transmitir.", fg=theme.COLOR_ERROR)
            return

        self._limpiar()
        envio = encapsular(mensaje)
        trama = envio.trama

        corrupcion = self.corrupcion_var.get()
        if corrupcion:
            indice = len(trama) // 2
            alterado = bytearray(trama)
            alterado[indice] ^= 0x01
            trama = bytes(alterado)
            self._escribir(
                f"⚡ MEDIO FÍSICO: se alteró 1 bit del byte {indice} "
                f"(0x{trama[indice] ^ 0x01:02X} -> 0x{trama[indice]:02X}) para simular ruido.\n\n",
                "baja"
            )

        self._render_pasos(envio.pasos, "PASOS 1-7 · ENCAPSULAMIENTO EN PC-A (L7 -> L1)", "alta")

        try:
            recepcion = desencapsular(trama)
        except FcsMismatchError as error:
            self._escribir("\nPASOS 8-9 · DESENCAPSULAMIENTO EN PC-B (L1 -> L2)\n", "hdr")
            self._escribir("  L1 Fisica  > agrupa los bits en bytes y entrega el marco a la capa 2\n", "capa")
            self._escribir("  L2 Enlace de datos  > VERIFICA EL CRC32 Y DESCARTA LA TRAMA\n", "error")
            self._escribir(f"      {error}\n", "error")
            self._escribir(
                "      · La corrupción nunca llega a las capas 3 a 7: el FCS protege la red.\n",
                "tec"
            )
            self._mostrar_trama(envio.trama, envio, corrupcion)
            self.resultado_lbl.config(
                text="✗ Trama descartada en la capa 2: el FCS/CRC32 detectó la corrupción del medio.",
                fg=theme.COLOR_ERROR
            )
            return

        self._render_pasos(recepcion.pasos, "PASOS 8-14 · DESENCAPSULAMIENTO EN PC-B (L1 -> L7)", "baja")
        self._mostrar_trama(envio.trama, envio, corrupcion)

        if recepcion.mensaje == mensaje:
            self._escribir("\nRESULTADO\n", "hdr")
            self._escribir("  ✔ Mensaje original recuperado byte a byte en la capa 7 de PC-B.\n", "ok")
            self.resultado_lbl.config(
                text=(
                    f"✔ Mensaje recuperado íntegramente en PC-B · {len(mensaje.encode('utf-8'))} B de carga · "
                    f"base64 {len(envio.mensaje_base64)} B · trama {len(envio.trama)} B / {len(envio.bits)} bits · "
                    f"CRC32 {envio.fcs_crc32} válido · checksum IP {envio.checksum_ip} válido"
                ),
                fg=theme.COLOR_SUCCESS
            )
        else:
            self._escribir("\nRESULTADO\n", "hdr")
            self._escribir("  ✗ El mensaje recibido difiere del original.\n", "error")
            self.resultado_lbl.config(text="✗ El mensaje no coincide con el original.", fg=theme.COLOR_ERROR)

    def _render_pasos(self, pasos: List, titulo: str, tag_alta: str):
        self._escribir(f"\n{titulo}\n", "hdr")
        for paso in pasos:
            self._escribir(f"\n  {paso.etiqueta}  >  {paso.accion}\n", "capa")
            self._escribir(f"      entra : {paso.entrada}\n", "entra")
            self._escribir(f"      sale  : {paso.salida}\n", "dato")
            for clave, valor in paso.agregados:
                self._escribir(f"      + {clave}: {valor}\n", tag_alta)
            for clave, valor in paso.eliminados:
                self._escribir(f"      - {clave}: {valor}\n", "baja")
            if paso.tecnica:
                self._escribir(f"      · {paso.tecnica}\n", "tec")

    def _mostrar_trama(self, trama_original: bytes, envio, corrupcion: bool):
        self.trama_text.configure(state=tk.NORMAL)
        self.trama_text.delete("1.0", tk.END)

        self._escribir_trama("CAPA 6 · Cadena base64 de la carga útil\n", "hdr")
        self._escribir_trama(f"  {envio.mensaje_base64}\n", "dato")
        self._escribir_trama(
            f"  {len(envio.mensaje.encode('utf-8'))} B originales -> "
            f"{len(envio.mensaje_base64)} B en base64\n\n",
            "entra"
        )

        self._escribir_trama("CAPA 2 · Trama Ethernet completa (preámbulo + MAC + IPv4 + FCS)\n", "hdr")
        self._escribir_trama(f"  {bytes_a_hex(trama_original)}\n\n", "dato")

        bits = envio.bits
        self._escribir_trama("CAPA 1 · Flujo de bits (primeros 96 de " + str(len(bits)) + ")\n", "hdr")
        self._escribir_trama("  " + " ".join(bits[i:i + 8] for i in range(0, 96, 8)) + "\n\n", "dato")

        self._escribir_trama("VERIFICACIONES\n", "hdr")
        self._escribir_trama(f"  CRC32 / FCS (capa 2)  : {envio.fcs_crc32}\n", "dato")
        self._escribir_trama(f"  Checksum IP (capa 3)  : {envio.checksum_ip}\n", "dato")
        self._escribir_trama(f"  Token de sesion (L5)  : {envio.token_sesion}\n", "dato")
        if corrupcion:
            self._escribir_trama("  Medio físico          : 1 bit alterado (trama descartada)\n", "error")
        self.trama_text.configure(state=tk.DISABLED)
