"""
Theme and styling definitions for the OSI Communication Simulator.
Provides color constants, fonts, and UI styling utilities.
"""

# Color Palette (Modern Dark Slate Theme)
BG_DARK = "#090d16"        # Deep background
BG_PANEL = "#111827"       # Secondary container background
BG_CARD = "#1f2937"        # Card background
BG_CARD_HOVER = "#283548"  # Card hover
BG_INPUT = "#1e293b"       # Input field background
BORDER = "#374151"         # Border color
BORDER_FOCUS = "#38bdf8"   # Focus border

# Text Colors
TEXT_PRIMARY = "#f9fafb"   # Main text
TEXT_MUTED = "#9ca3af"     # Dimmed text
TEXT_SECONDARY = "#d1d5db" # Secondary text
TEXT_ACCENT = "#38bdf8"    # Highlight cyan

# Status Colors
COLOR_SUCCESS = "#10b981"  # Emerald green
COLOR_WARNING = "#f59e0b"  # Amber
COLOR_ERROR = "#ef4444"    # Coral red
COLOR_INFO = "#3b82f6"     # Sky blue

# 7 OSI Layer Colors (Vibrant & Distinct)
OSI_COLORS = {
    7: "#8b5cf6",  # Layer 7 Application (Violet)
    6: "#6366f1",  # Layer 6 Presentation (Indigo)
    5: "#3b82f6",  # Layer 5 Session (Blue)
    4: "#06b6d4",  # Layer 4 Transport (Cyan)
    3: "#10b981",  # Layer 3 Network (Green)
    2: "#f59e0b",  # Layer 2 Data Link (Amber)
    1: "#ef4444",  # Layer 1 Physical (Red)
}

# OSI Layer Metadata
OSI_METADATA = {
    7: {
        "name": "Aplicación",
        "pdu": "Datos",
        "description": "Aplicaciones de red, interfaz de usuario, HTTP, SMTP, DNS y protocolos.",
        "icon": "📱",
        "color": OSI_COLORS[7]
    },
    6: {
        "name": "Presentación",
        "pdu": "Datos",
        "description": "Representación de datos, codificación de caracteres (UTF-8/ASCII), compresión y cifrado.",
        "icon": "🔐",
        "color": OSI_COLORS[6]
    },
    5: {
        "name": "Sesión",
        "pdu": "Datos",
        "description": "Comunicación entre hosts, establecimiento de sesión, gestión de tokens y sincronización.",
        "icon": "🤝",
        "color": OSI_COLORS[5]
    },
    4: {
        "name": "Transporte",
        "pdu": "Segmento / Datagrama",
        "description": "Conexiones extremo a extremo, confiabilidad, control de flujo y segmentación (TCP/UDP, puertos).",
        "icon": "🚚",
        "color": OSI_COLORS[4]
    },
    3: {
        "name": "Red",
        "pdu": "Paquete",
        "description": "Direccionamiento lógico (IP) y determinación de rutas entre redes.",
        "icon": "🌐",
        "color": OSI_COLORS[3]
    },
    2: {
        "name": "Enlace de datos",
        "pdu": "Trama",
        "description": "Direccionamiento físico (MAC), tramas y detección de errores (CRC/FCS).",
        "icon": "🔗",
        "color": OSI_COLORS[2]
    },
    1: {
        "name": "Física",
        "pdu": "Bits",
        "description": "Transmisión de flujo de bits sin estructura por medios físicos (señales, pulsos).",
        "icon": "⚡",
        "color": OSI_COLORS[1]
    },
}

# Fonts
FONT_FAMILY = "DejaVu Sans"
FONT_CODE = "DejaVu Sans Mono"

FONT_APP_TITLE = (FONT_FAMILY, 16, "bold")
FONT_TITLE = (FONT_FAMILY, 14, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 11, "bold")
FONT_HEADING = (FONT_FAMILY, 12, "bold")
FONT_BODY = (FONT_FAMILY, 10)
FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
FONT_SMALL = (FONT_FAMILY, 9)
FONT_TINY = (FONT_FAMILY, 8)
FONT_MONO = (FONT_CODE, 9)
FONT_MONO_BOLD = (FONT_CODE, 9, "bold")
