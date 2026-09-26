"""
Pruebas del motor de encapsulamiento OSI (osi_engine).
Verifican la cascada L7 -> L1 -> L7, el uso de base64, el checksum IP,
la deteccion de errores con CRC32 y el panel visual de la cascada.
"""

import math
import tkinter as tk
import unittest

from osi_engine import (
    FcsMismatchError,
    bytes_a_bits,
    calcular_crc32,
    crc32_hex,
    checksum_ip,
    decode_base64,
    desencapsular,
    encapsular,
    encode_base64,
    transmitir,
)
from gui.cascade_panel import CascadePanel

MENSAJE = "Hola PC-B, mensaje con acentos, ñ, á, é y emoji 🌐🔁"


class TestBase64(unittest.TestCase):
    def test_ida_y_vuelta_conserva_el_texto(self):
        for texto in (MENSAJE, "a", "abc", "abcd", "ñandú 🦆", ""):
            with self.subTest(texto=texto):
                self.assertEqual(decode_base64(encode_base64(texto)), texto)

    def test_longitud_multiplo_de_cuatro_y_crecimiento_4_3(self):
        for longitud in range(1, 40):
            with self.subTest(longitud=longitud):
                original = "x" * longitud
                codificado = encode_base64(original)
                self.assertEqual(len(codificado) % 4, 0)
                self.assertEqual(len(codificado), 4 * math.ceil(longitud / 3))
                self.assertEqual(len(codificado), math.ceil(longitud / 3) * 4)

    def test_solo_usa_el_alfabeto_base64(self):
        alfabeto = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
        self.assertTrue(set(encode_base64(MENSAJE)).issubset(alfabeto))


class TestChecksums(unittest.TestCase):
    def test_crc32_es_estable_y_detecta_un_cambio(self):
        datos = b"trama de prueba para el CRC32"
        self.assertEqual(crc32_hex(datos), crc32_hex(datos))
        alterado = bytearray(datos)
        alterado[0] ^= 0x01
        self.assertNotEqual(calcular_crc32(datos), calcular_crc32(bytes(alterado)))
        self.assertRegex(crc32_hex(datos), r"^0x[0-9A-F]{8}$")

    def test_checksum_ip_formato_y_verificacion(self):
        cabecera = b"IP4|version=IPv4|ttl=64|proto=TCP (6)|src=192.168.1.10|dst=93.184.216.34|"
        self.assertRegex(checksum_ip(cabecera), r"^0x[0-9A-F]{4}$")
        self.assertEqual(checksum_ip(cabecera), checksum_ip(cabecera))
        self.assertNotEqual(checksum_ip(cabecera), checksum_ip(cabecera.replace(b"ttl=64", b"ttl=32")))


class TestEncapsular(unittest.TestCase):
    def setUp(self):
        self.envio = encapsular(MENSAJE)

    def test_recorre_las_siete_capas_en_orden(self):
        numeros = [paso.layer_num for paso in self.envio.pasos]
        self.assertEqual(numeros, [7, 6, 5, 4, 3, 2, 1])

    def test_capa_6_agrega_base64_y_capa_5_token(self):
        paso_l6 = self.envio.pasos[1]
        self.assertEqual(paso_l6.salida, self.envio.mensaje_base64)
        self.assertEqual(decode_base64(self.envio.mensaje_base64), MENSAJE)
        self.assertTrue(self.envio.token_sesion.startswith("tok_"))
        self.assertEqual(self.envio.pasos[2].agregados[0][1], self.envio.token_sesion)

    def test_capas_4_3_2_1_agregan_sus_cabeceras(self):
        agregado = {paso.layer_num: dict(paso.agregados) for paso in self.envio.pasos}
        self.assertEqual(agregado[4]["Puerto destino"], "80")
        self.assertEqual(agregado[4]["Protocolo de transporte"], "TCP")
        self.assertEqual(agregado[3]["IP destino"], "93.184.216.34")
        self.assertTrue(agregado[3]["Checksum"].startswith(self.envio.checksum_ip))
        self.assertEqual(agregado[2]["FCS / CRC32"], self.envio.fcs_crc32)
        self.assertEqual(agregado[1]["Bits transmitidos"], f"{len(self.envio.bits)} bits")

    def test_la_trama_contiene_preambulo_ethernet_y_fcs(self):
        self.assertTrue(self.envio.trama.startswith(b"\x55" * 7 + b"\xd5"))
        self.assertEqual(self.envio.trama[8:14], bytes.fromhex("AABBCC445566"))
        self.assertEqual(self.envio.trama[14:20], bytes.fromhex("AABBCC112233"))
        self.assertEqual(self.envio.trama[20:22], b"\x08\x00")
        fcs = int.from_bytes(self.envio.trama[-4:], "little")
        self.assertEqual(fcs, calcular_crc32(self.envio.trama[8:-4]))

    def test_capa_1_convierte_la_trama_entera_en_bits(self):
        self.assertEqual(len(self.envio.bits), len(self.envio.trama) * 8)
        self.assertEqual(bytes_a_bits(self.envio.trama[:1]), "01010101")

    def test_las_cabeceras_tcp_e_ip_viajan_dentro_de_la_trama(self):
        self.assertIn(b"TCP|sport=54321|dport=80|seq=1001|ack=1|flags=PSH,ACK|win=65535|", self.envio.trama)
        self.assertIn(
            b"IP4|version=IPv4|ttl=64|proto=TCP (6)|src=192.168.1.10|dst=93.184.216.34|",
            self.envio.trama
        )
        self.assertIn(self.envio.mensaje_base64.encode("ascii"), self.envio.trama)


class TestDesencapsular(unittest.TestCase):
    def setUp(self):
        self.envio = encapsular(MENSAJE)
        self.recepcion = desencapsular(self.envio.trama)

    def test_recorre_las_siete_capas_en_orden_inverso(self):
        numeros = [paso.layer_num for paso in self.recepcion.pasos]
        self.assertEqual(numeros, [1, 2, 3, 4, 5, 6, 7])

    def test_recupera_el_mensaje_original(self):
        self.assertEqual(self.recepcion.mensaje, MENSAJE)
        self.assertEqual(self.recepcion.mensaje_base64, self.envio.mensaje_base64)
        self.assertTrue(self.recepcion.fcs_valido)
        self.assertTrue(self.recepcion.checksum_ip_valido)

    def test_capa_6_retira_base64_y_capa_2_retira_el_fcs(self):
        eliminados_l2 = dict(self.recepcion.pasos[1].eliminados)
        self.assertIn("FCS / CRC32", eliminados_l2)
        self.assertIn("MAC origen", eliminados_l2)
        eliminados_l6 = dict(self.recepcion.pasos[5].eliminados)
        self.assertIn("Base64", eliminados_l6)
        self.assertEqual(self.recepcion.pasos[6].salida, MENSAJE)

    def test_un_bit_corrupto_es_detectado_por_el_crc32(self):
        alterada = bytearray(self.envio.trama)
        indice = len(alterada) // 2
        alterada[indice] ^= 0x01
        with self.assertRaises(FcsMismatchError) as contexto:
            desencapsular(bytes(alterada))
        self.assertIn("CRC32 no coincide", str(contexto.exception))

    def test_una_trama_demasiado_corta_es_rechazada(self):
        with self.assertRaises(ValueError):
            desencapsular(b"\x55\xd5")

    def test_cambiar_la_ip_deja_el_checksum_invalido(self):
        cuerpo = self.envio.trama[8:-4].replace(b"192.168.1.10", b"192.168.1.99")
        manipulada = self.envio.trama[:8] + cuerpo + calcular_crc32(cuerpo).to_bytes(4, "little")
        recepcion = desencapsular(manipulada)
        self.assertFalse(recepcion.checksum_ip_valido)
        self.assertTrue(recepcion.fcs_valido)


class TestTransmitir(unittest.TestCase):
    def test_transmitir_devuelve_los_catorce_pasos_y_la_integridad(self):
        resultado = transmitir(MENSAJE)
        self.assertEqual(len(resultado.pasos_emisor), 7)
        self.assertEqual(len(resultado.pasos_receptor), 7)
        self.assertEqual(resultado.mensaje_original, MENSAJE)
        self.assertEqual(resultado.mensaje_recuperado, MENSAJE)
        self.assertTrue(resultado.integridad_ok)
        self.assertEqual(resultado.bits_totales, resultado.bytes_trama * 8)
        self.assertEqual(resultado.bits, bytes_a_bits(resultado.trama))

    def test_metricas_de_base64_y_de_trama(self):
        resultado = transmitir(MENSAJE)
        self.assertEqual(resultado.bytes_originales, len(MENSAJE.encode("utf-8")))
        self.assertEqual(resultado.bytes_base64, len(resultado.mensaje_base64))
        self.assertGreater(resultado.bytes_trama, resultado.bytes_base64)
        self.assertTrue(resultado.expansion_base64.startswith("+"))
        self.assertGreater(resultado.bytes_trama, 0)

    def test_admite_direcciones_y_puertos_personalizados(self):
        resultado = transmitir(
            "mensaje corto",
            ip_origen="10.0.0.5",
            ip_destino="8.8.8.8",
            puerto_origen=40000,
            puerto_destino=53,
            mac_origen="AA:00:00:00:00:01",
            mac_destino="AA:00:00:00:00:02",
        )
        self.assertEqual(resultado.mensaje_recuperado, "mensaje corto")
        self.assertTrue(resultado.integridad_ok)

    def test_soporta_varios_mensajes_incluido_el_vacio(self):
        for mensaje in ("", "a", MENSAJE, "x" * 500):
            with self.subTest(mensaje=mensaje[:12]):
                resultado = transmitir(mensaje)
                self.assertEqual(resultado.mensaje_recuperado, mensaje)
                self.assertTrue(resultado.integridad_ok)


class TestPanelCascada(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.geometry("1000x800")
        self.panel = CascadePanel(self.root)
        self.panel.pack(fill=tk.BOTH, expand=True)
        self.root.update()

    def tearDown(self):
        self.root.destroy()

    def test_transmitir_muestra_el_mensaje_recuperado(self):
        self.panel.mensaje_var.set(MENSAJE)
        self.panel.transmitir()
        self.root.update()
        registro = self.panel.log_text.get("1.0", tk.END)
        self.assertIn("ENCAPSULAMIENTO EN PC-A", registro)
        self.assertIn("DESENCAPSULAMIENTO EN PC-B", registro)
        self.assertIn("Mensaje original recuperado byte a byte", registro)
        self.assertIn("recuperado íntegramente", self.panel.resultado_lbl.cget("text"))
        self.assertIn(encode_base64(MENSAJE), self.panel.trama_text.get("1.0", tk.END))

    def test_la_corrupcion_se_reporta_en_la_capa_2(self):
        self.panel.mensaje_var.set(MENSAJE)
        self.panel.corrupcion_var.set(True)
        self.panel.transmitir()
        self.root.update()
        registro = self.panel.log_text.get("1.0", tk.END)
        self.assertIn("VERIFICA EL CRC32 Y DESCARTA LA TRAMA", registro)
        self.assertIn("Trama descartada en la capa 2", self.panel.resultado_lbl.cget("text"))

    def test_un_mensaje_vacio_se_rechaza_en_la_interfaz(self):
        self.panel.mensaje_var.set("   ")
        self.panel.transmitir()
        self.root.update()
        self.assertIn("Escribe un mensaje", self.panel.resultado_lbl.cget("text"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
