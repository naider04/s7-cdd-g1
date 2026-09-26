"""
Motor de encapsulamiento y desencapsulamiento del Modelo OSI.

Implementa la cascada real que recorre el simulador:

    Emisor  (PC-A):  L7 -> L6 -> L5 -> L4 -> L3 -> L2 -> L1
    Receptor (PC-B):  L1 -> L2 -> L3 -> L4 -> L5 -> L6 -> L7

Cada capa construye bytes reales: la capa 6 serializa la carga en base64,
la capa 4 agrega la cabecera TCP, la capa 3 arma el paquete IPv4 con su
checksum, la capa 2 construye el marco Ethernet con preámbulo y FCS/CRC32,
y la capa 1 convierte el marco en bits. El camino inverso verifica el CRC32,
retira cada cabecera y reconstruye el mensaje original.
"""

import base64
import hashlib
import zlib
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

CAPAS: Dict[int, str] = {
    7: "Aplicación",
    6: "Presentación",
    5: "Sesión",
    4: "Transporte",
    3: "Red",
    2: "Enlace de datos",
    1: "Física",
}

CAMPOS_TCP = ("sport", "dport", "seq", "ack", "flags", "win")
CAMPOS_IP = ("version", "ttl", "proto", "src", "dst", "checksum")

PREAMBULO = b"\x55" * 7 + b"\xd5"
ETHERTYPE_IPV4 = b"\x08\x00"
LONGITUD_MAC = 6
LONGITUD_FCS = 4
CABECERA_PREAMBULO = 8


class FcsMismatchError(ValueError):
    """Se lanza cuando el CRC32 del marco no coincide con el calculado."""


@dataclass
class PasoCapa:
    """Un paso de la cascada: qué hace la capa, con qué entra y qué produce."""

    layer_num: int
    layer_name: str
    side: str
    accion: str
    entrada: str
    salida: str
    agregados: List[Tuple[str, str]] = field(default_factory=list)
    eliminados: List[Tuple[str, str]] = field(default_factory=list)
    tecnica: str = ""

    @property
    def etiqueta(self) -> str:
        return f"L{self.layer_num} {self.layer_name}"


@dataclass
class TramaEncapsulada:
    """Resultado de la cascada de envío: los pasos y los bytes de la trama."""

    pasos: List[PasoCapa]
    trama: bytes
    mensaje: str
    mensaje_base64: str
    token_sesion: str
    checksum_ip: str
    fcs_crc32: str
    bits: str
    preambulo: bytes


@dataclass
class RecepcionDecapsulada:
    """Resultado de la cascada de recepción: los pasos y el mensaje recuperado."""

    pasos: List[PasoCapa]
    mensaje: str
    mensaje_base64: str
    token_sesion: str
    checksum_ip: str
    fcs_crc32: str
    fcs_valido: bool
    checksum_ip_valido: bool


@dataclass
class ResultadoTransmision:
    """Informe completo de una transmisión PC-A -> medio -> PC-B."""

    mensaje_original: str
    mensaje_recuperado: str
    pasos_emisor: List[PasoCapa]
    pasos_receptor: List[PasoCapa]
    mensaje_base64: str
    bytes_originales: int
    bytes_base64: int
    bytes_trama: int
    bits_totales: int
    trama: bytes
    bits: str
    fcs_crc32: str
    fcs_valido: bool
    checksum_ip: str
    checksum_ip_valido: bool

    @property
    def integridad_ok(self) -> bool:
        return (
            self.mensaje_original == self.mensaje_recuperado
            and self.fcs_valido
            and self.checksum_ip_valido
        )

    @property
    def expansion_base64(self) -> str:
        if self.bytes_originales == 0:
            return "0.0%"
        delta = (self.bytes_base64 - self.bytes_originales) / self.bytes_originales * 100
        return f"+{delta:.1f}%"


# --- CAPA 6: BASE64 -----------------------------------------------------------

def encode_base64(texto: str) -> str:
    """Codifica un texto UTF-8 a base64, la representación ASCII de la carga binaria."""
    return base64.b64encode(texto.encode("utf-8")).decode("ascii")


def decode_base64(codificado: str) -> str:
    """Decodifica base64 y reconstruye el texto UTF-8 original."""
    return base64.b64decode(codificado.encode("ascii")).decode("utf-8")


# --- UTILIDADES DE BAJO NIVEL ------------------------------------------------

def bytes_a_bits(datos: bytes) -> str:
    """Convierte una secuencia de bytes en su cadena de bits (capa 1)."""
    return "".join(f"{byte:08b}" for byte in datos)


def bits_a_bytes(bits: str) -> bytes:
    """Convierte una cadena de bits en bytes (decodificación de la capa 1)."""
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))


def bytes_a_hex(datos: bytes) -> str:
    """Representación hexadecimal en mayúsculas y separada por espacios."""
    return " ".join(f"{byte:02X}" for byte in datos)


def calcular_crc32(datos: bytes) -> int:
    """CRC32 real (polinomio 0x04C11DB7) del contenido del marco."""
    return zlib.crc32(datos) & 0xFFFFFFFF


def crc32_hex(datos: bytes) -> str:
    """CRC32 en notación hexadecimal de 8 dígitos."""
    return f"0x{calcular_crc32(datos):08X}"


def checksum_ip(cabecera: bytes) -> str:
    """Checksum de Internet IPv4: suma de complementos de 16 bits."""
    if len(cabecera) % 2:
        cabecera += b"\x00"
    total = 0
    for i in range(0, len(cabecera), 2):
        total += (cabecera[i] << 8) + cabecera[i + 1]
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return f"0x{(~total) & 0xFFFF:04X}"


def _mac_a_bytes(mac: str) -> bytes:
    return bytes(int(parte, 16) for parte in mac.split(":"))


def _bytes_a_mac(datos: bytes) -> str:
    return ":".join(f"{byte:02X}" for byte in datos)


def _empaquetar(etiqueta: str, campos: List[Tuple[str, object]]) -> bytes:
    partes = [etiqueta] + [f"{clave}={valor}" for clave, valor in campos]
    return "|".join(partes).encode("utf-8") + b"|"


def _desempaquetar(datos: bytes, cantidad_campos: int) -> Tuple[str, Dict[str, str], bytes]:
    tokens = datos.split(b"|", cantidad_campos + 1)
    etiqueta = tokens[0].decode("utf-8")
    campos: Dict[str, str] = {}
    for token in tokens[1:-1]:
        clave, _, valor = token.decode("utf-8").partition("=")
        campos[clave] = valor
    return etiqueta, campos, tokens[-1]


def _token_sesion(mensaje: str) -> str:
    return "tok_" + hashlib.sha256(mensaje.encode("utf-8")).hexdigest()[:8]


def _vista(texto: str, limite: int = 58) -> str:
    texto = texto.replace("\n", " ")
    if len(texto) <= limite:
        return texto
    return texto[:limite] + f"... (+{len(texto) - limite} car.)"


def _bytes_a_texto(datos: bytes, limite: int = 58) -> str:
    return _vista(datos.decode("utf-8", errors="replace"), limite)


# --- CASCADA DE ENVIO (PC-A) -------------------------------------------------

def encapsular(
    mensaje: str,
    protocolo_app: str = "HTTP/1.1",
    recurso: str = "/index.html",
    ip_origen: str = "192.168.1.10",
    ip_destino: str = "93.184.216.34",
    puerto_origen: int = 54321,
    puerto_destino: int = 80,
    mac_origen: str = "AA:BB:CC:11:22:33",
    mac_destino: str = "AA:BB:CC:44:55:66",
    numero_secuencia: int = 1001,
    medio: str = "Cobre UTP (RJ45)",
) -> TramaEncapsulada:
    """Ejecuta la cascada de encapsulamiento L7 -> L1 y devuelve la trama en bits."""
    pasos: List[PasoCapa] = []
    bytes_originales = len(mensaje.encode("utf-8"))

    peticion = f"{protocolo_app} GET {recurso}"
    pasos.append(PasoCapa(
        layer_num=7,
        layer_name=CAPAS[7],
        side="emisor",
        accion="La aplicación genera los datos de usuario",
        entrada=mensaje,
        salida=mensaje,
        agregados=[
            ("Protocolo de aplicación", protocolo_app),
            ("Petición", peticion),
            ("Tamaño de la carga", f"{bytes_originales} bytes"),
        ],
        tecnica="La capa 7 no añade cabeceras: solo produce el mensaje que el usuario quiere enviar.",
    ))

    carga_base64 = encode_base64(mensaje)
    bytes_base64 = len(carga_base64.encode("ascii"))
    pasos.append(PasoCapa(
        layer_num=6,
        layer_name=CAPAS[6],
        side="emisor",
        accion="Codifica a UTF-8 y serializa la carga en base64",
        entrada=mensaje,
        salida=carga_base64,
        agregados=[
            ("Codificación de caracteres", "UTF-8"),
            ("Serialización", "Base64 (alfabeto imprimible)"),
            ("Tamaño original", f"{bytes_originales} bytes"),
            ("Tamaño codificado", f"{bytes_base64} bytes (+{(bytes_base64 - bytes_originales) / max(bytes_originales, 1) * 100:.1f}%)"),
        ],
        tecnica=(
            "Base64 convierte cualquier carga binaria en texto ASCII seguro para transportar. "
            "Es el mecanismo real que usan los adjuntos MIME del correo y los cuerpos JSON de las APIs: "
            "por cada 3 bytes originales se generan 4 caracteres."
        ),
    ))

    token = _token_sesion(mensaje)
    pasos.append(PasoCapa(
        layer_num=5,
        layer_name=CAPAS[5],
        side="emisor",
        accion="Abre el canal lógico y asigna el identificador de sesión",
        entrada=carga_base64,
        salida=carga_base64,
        agregados=[
            ("Id de sesión", token),
            ("Estado", "ESTABLECIDA"),
            ("Keep-alive", "30 s"),
        ],
        tecnica=(
            "La sesión no añade bytes a la carga útil: sus datos viajan en mensajes de control "
            "propios (por ejemplo, la negociación SIP de una llamada). Aquí se registran como metadatos."
        ),
    ))

    campos_tcp = [
        ("sport", puerto_origen),
        ("dport", puerto_destino),
        ("seq", numero_secuencia),
        ("ack", 1),
        ("flags", "PSH,ACK"),
        ("win", 65535),
    ]
    segmento = _empaquetar("TCP", campos_tcp) + carga_base64.encode("ascii")
    pasos.append(PasoCapa(
        layer_num=4,
        layer_name=CAPAS[4],
        side="emisor",
        accion="Agrega la cabecera TCP y segmenta el flujo",
        entrada=carga_base64,
        salida=_bytes_a_texto(segmento),
        agregados=[
            ("Protocolo de transporte", "TCP"),
            ("Puerto origen", str(puerto_origen)),
            ("Puerto destino", str(puerto_destino)),
            ("Número de secuencia", str(numero_secuencia)),
            ("Número de reconocimiento", "1"),
            ("Banderas", "PSH,ACK"),
            ("Ventana de recepción", "65535 bytes"),
            ("Carga útil", f"{bytes_base64} bytes"),
        ],
        tecnica="TCP ofrece entrega fiable, ordenada y con control de flujo entre extremos.",
    ))

    campos_ip = [
        ("version", "IPv4"),
        ("ttl", 64),
        ("proto", "TCP (6)"),
        ("src", ip_origen),
        ("dst", ip_destino),
    ]
    checksum = checksum_ip(_empaquetar("IP4", campos_ip))
    paquete = _empaquetar("IP4", campos_ip + [("checksum", checksum)]) + segmento
    pasos.append(PasoCapa(
        layer_num=3,
        layer_name=CAPAS[3],
        side="emisor",
        accion="Agrega la cabecera IPv4 y direcciona el paquete",
        entrada=_bytes_a_texto(segmento),
        salida=_bytes_a_texto(paquete),
        agregados=[
            ("Versión", "IPv4"),
            ("TTL", "64 saltos"),
            ("Protocolo encapsulado", "TCP (6)"),
            ("IP origen", ip_origen),
            ("IP destino", ip_destino),
            ("Checksum", f"{checksum} (calculado)"),
        ],
        tecnica="La capa 3 direcciona el paquete entre subredes y los enrutadores decide la ruta con el TTL.",
    ))

    cuerpo = _mac_a_bytes(mac_destino) + _mac_a_bytes(mac_origen) + ETHERTYPE_IPV4 + paquete
    fcs = calcular_crc32(cuerpo)
    trama = PREAMBULO + cuerpo + fcs.to_bytes(LONGITUD_FCS, "little")
    pasos.append(PasoCapa(
        layer_num=2,
        layer_name=CAPAS[2],
        side="emisor",
        accion="Construye el marco Ethernet con preámbulo y FCS",
        entrada=_bytes_a_texto(paquete),
        salida=f"{len(trama)} bytes: {bytes_a_hex(trama[:24])}...",
        agregados=[
            ("MAC destino", mac_destino),
            ("MAC origen", mac_origen),
            ("EtherType", "0x0800 (IPv4)"),
            ("Preámbulo + SFD", bytes_a_hex(PREAMBULO)),
            ("FCS / CRC32", f"0x{fcs:08X}"),
            ("Tamaño del marco", f"{len(trama)} bytes"),
        ],
        tecnica="El enlace de datos direcciona dentro de la red local y el FCS/CRC32 detecta errores.",
    ))

    bits = bytes_a_bits(trama)
    pasos.append(PasoCapa(
        layer_num=1,
        layer_name=CAPAS[1],
        side="emisor",
        accion="Convierte el marco en bits y lo transmite por el medio",
        entrada=f"{len(trama)} bytes",
        salida=" ".join(bits[i:i + 8] for i in range(0, 64, 8)) + " ...",
        agregados=[
            ("Medio físico", medio),
            ("Codificación de línea", "Manchester (simplificada)"),
            ("Bits transmitidos", f"{len(bits)} bits"),
            ("Primer byte", f"0x55 (preámbulo) = {bits[:8]}"),
        ],
        tecnica="La fisica solo mueve bits: no interpreta direcciones ni cabeceras.",
    ))

    return TramaEncapsulada(
        pasos=pasos,
        trama=trama,
        mensaje=mensaje,
        mensaje_base64=carga_base64,
        token_sesion=token,
        checksum_ip=checksum,
        fcs_crc32=f"0x{fcs:08X}",
        bits=bits,
        preambulo=PREAMBULO,
    )


# --- CASCADA DE RECEPCION (PC-B) ---------------------------------------------

def desencapsular(trama: bytes, medio: str = "Cobre UTP (RJ45)") -> RecepcionDecapsulada:
    """Ejecuta la cascada de desencapsulamiento L1 -> L7 sobre los bytes recibidos."""
    pasos: List[PasoCapa] = []

    if len(trama) < CABECERA_PREAMBULO + 2 * LONGITUD_MAC + 2 + LONGITUD_FCS:
        raise ValueError("La trama es demasiado corta para contener un marco Ethernet completo.")

    preambulo = trama[:CABECERA_PREAMBULO]
    mac_destino = _bytes_a_mac(trama[8:14])
    mac_origen = _bytes_a_mac(trama[14:20])
    ethertype = trama[20:22]
    paquete = trama[22:-LONGITUD_FCS]
    fcs_recibido = int.from_bytes(trama[-LONGITUD_FCS:], "little")
    fcs_calculado = calcular_crc32(trama[8:-LONGITUD_FCS])
    fcs_valido = fcs_recibido == fcs_calculado

    pasos.append(PasoCapa(
        layer_num=1,
        layer_name=CAPAS[1],
        side="receptor",
        accion="Detecta los bits y los agrupa en bytes",
        entrada=f"{len(trama) * 8} bits",
        salida=f"{len(trama)} bytes",
        agregados=[
            ("Medio físico", medio),
            ("Sincronización", "Delimitador SFD 0xD5 verificado" if preambulo == PREAMBULO else "SFD no reconocido"),
            ("Bytes recibidos", str(len(trama))),
        ],
        tecnica="En el receptor la capa física decodifica la señal eléctrica y entrega bytes a la capa 2.",
    ))

    if not fcs_valido:
        pasos.append(PasoCapa(
            layer_num=2,
            layer_name=CAPAS[2],
            side="receptor",
            accion="Descarta la trama: el CRC32 no coincide",
            entrada=f"FCS recibido 0x{fcs_recibido:08X}",
            salida="Trama descartada",
            agregados=[("FCS recalculado", f"0x{fcs_calculado:08X}")],
            tecnica="El CRC32 permite detectar cualquier corrupcion del medio antes de entregar datos.",
        ))
        raise FcsMismatchError(
            f"FCS/CRC32 no coincide: recibido 0x{fcs_recibido:08X}, calculado 0x{fcs_calculado:08X}."
        )

    pasos.append(PasoCapa(
        layer_num=2,
        layer_name=CAPAS[2],
        side="receptor",
        accion="Verifica el FCS y retira la encapsulación de enlace",
        entrada=f"FCS 0x{fcs_recibido:08X}",
        salida=f"{len(paquete)} bytes de paquete IPv4",
        agregados=[("FCS / CRC32", f"0x{fcs_calculado:08X} válido")],
        eliminados=[
            ("MAC destino", mac_destino),
            ("MAC origen", mac_origen),
            ("EtherType", bytes_a_hex(ethertype)),
            ("Preámbulo + SFD", bytes_a_hex(preambulo)),
            ("FCS / CRC32", f"0x{fcs_recibido:08X}"),
        ],
        tecnica="Verificado el CRC, la trama se acepta y se entrega el paquete a la capa 3.",
    ))

    _, campos_ip, resto = _desempaquetar(paquete, len(CAMPOS_IP))
    campos_sin_checksum = [(clave, campos_ip[clave]) for clave in CAMPOS_IP if clave != "checksum"]
    checksum_calculado = checksum_ip(_empaquetar("IP4", campos_sin_checksum))
    checksum_recibido = campos_ip.get("checksum", "")
    checksum_valido = checksum_calculado == checksum_recibido
    pasos.append(PasoCapa(
        layer_num=3,
        layer_name=CAPAS[3],
        side="receptor",
        accion="Verifica el checksum IP y retira la cabecera de red",
        entrada=_bytes_a_texto(paquete),
        salida="Segmento TCP",
        agregados=[
            ("IP origen", campos_ip.get("src", "")),
            ("IP destino", campos_ip.get("dst", "")),
            ("Checksum", f"{checksum_recibido} {'válido' if checksum_valido else 'INVÁLIDO'}"),
        ],
        eliminados=[(clave.capitalize(), campos_ip[clave]) for clave in CAMPOS_IP],
        tecnica="Si el checksum no coincidiera, el paquete se descartaría aquí.",
    ))

    _, campos_tcp, carga = _desempaquetar(resto, len(CAMPOS_TCP))
    pasos.append(PasoCapa(
        layer_num=4,
        layer_name=CAPAS[4],
        side="receptor",
        accion="Reensambla el segmento y retira la cabecera TCP",
        entrada="Segmento TCP",
        salida=f"{len(carga)} bytes de carga útil",
        agregados=[
            ("Puerto origen", campos_tcp.get("sport", "")),
            ("Puerto destino", campos_tcp.get("dport", "")),
            ("Secuencia", campos_tcp.get("seq", "")),
            ("Banderas", campos_tcp.get("flags", "")),
        ],
        eliminados=[(clave.upper(), campos_tcp[clave]) for clave in CAMPOS_TCP if clave in campos_tcp],
        tecnica="La capa 4 entrega el flujo de datos ordenado a la capa de sesión.",
    ))

    carga_base64 = carga.decode("ascii")
    token = _token_sesion(decode_base64(carga_base64))
    pasos.append(PasoCapa(
        layer_num=5,
        layer_name=CAPAS[5],
        side="receptor",
        accion="Cierra el canal lógico de la sesión",
        entrada=f"{len(carga)} bytes",
        salida=f"{len(carga)} bytes",
        agregados=[
            ("Id de sesión", token),
            ("Estado", "CERRADA"),
        ],
        tecnica="La sesión libera los recursos del canal y entrega el flujo a la capa de presentación.",
    ))

    mensaje = decode_base64(carga_base64)
    pasos.append(PasoCapa(
        layer_num=6,
        layer_name=CAPAS[6],
        side="receptor",
        accion="Decodifica base64 y reconstruye el texto UTF-8",
        entrada=carga_base64,
        salida=mensaje,
        agregados=[
            ("Codificación", "UTF-8"),
            ("Caracteres decodificados", str(len(mensaje))),
        ],
        eliminados=[("Base64", _vista(carga_base64, 40))],
        tecnica="Al retirar el envoltorio base64 se recupera el contenido binario original de la capa 7.",
    ))

    pasos.append(PasoCapa(
        layer_num=7,
        layer_name=CAPAS[7],
        side="receptor",
        accion="Entrega el mensaje original a la aplicación",
        entrada=mensaje,
        salida=mensaje,
        agregados=[("Integridad", "Coincide con el mensaje enviado" if mensaje else "Vacio")],
        tecnica="Fin del proceso: la persona B lee exactamente lo que la persona A escribió.",
    ))

    return RecepcionDecapsulada(
        pasos=pasos,
        mensaje=mensaje,
        mensaje_base64=carga_base64,
        token_sesion=token,
        checksum_ip=checksum_recibido,
        fcs_crc32=f"0x{fcs_calculado:08X}",
        fcs_valido=fcs_valido,
        checksum_ip_valido=checksum_valido,
    )


# --- FUNCION PRINCIPAL -------------------------------------------------------

def transmitir(mensaje: str, **opciones) -> ResultadoTransmision:
    """Ejecuta la transmisión completa: encapsula en PC-A y desencapsula en PC-B.

    Es la función central del simulador. Invoca a encapsular() y a
    desencapsular(), compara el mensaje recuperado con el original y devuelve un
    ResultadoTransmision con los 14 pasos (7 de envío y 7 de recepción) y las
    métricas de la trama.
    """
    envio = encapsular(mensaje, **opciones)
    recepcion = desencapsular(envio.trama)

    bytes_originales = len(mensaje.encode("utf-8"))
    return ResultadoTransmision(
        mensaje_original=mensaje,
        mensaje_recuperado=recepcion.mensaje,
        pasos_emisor=envio.pasos,
        pasos_receptor=recepcion.pasos,
        mensaje_base64=envio.mensaje_base64,
        bytes_originales=bytes_originales,
        bytes_base64=len(envio.mensaje_base64.encode("ascii")),
        bytes_trama=len(envio.trama),
        bits_totales=len(envio.bits),
        trama=envio.trama,
        bits=envio.bits,
        fcs_crc32=envio.fcs_crc32,
        fcs_valido=recepcion.fcs_valido,
        checksum_ip=envio.checksum_ip,
        checksum_ip_valido=recepcion.checksum_ip_valido,
    )
