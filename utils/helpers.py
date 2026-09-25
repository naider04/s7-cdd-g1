"""
Helper utilities for formatting, byte conversions, bitstream generation,
and canvas drawing.
"""

import time
from typing import List, Tuple


def get_timestamp() -> str:
    """Return formatted current time string (HH:MM:SS.mmm)."""
    t = time.time()
    ms = int((t - int(t)) * 1000)
    return time.strftime("%H:%M:%S", time.localtime(t)) + f".{ms:03d}"


def text_to_bits(text: str, max_bytes: int = 16) -> str:
    """Convert a text string to formatted spaced binary octets."""
    try:
        raw_bytes = text.encode("utf-8")[:max_bytes]
    except Exception:
        raw_bytes = text.encode("latin-1", errors="replace")[:max_bytes]

    byte_strs = [f"{b:08b}" for b in raw_bytes]
    if len(text.encode("utf-8", errors="ignore")) > max_bytes:
        return " ".join(byte_strs) + " ..."
    return " ".join(byte_strs) if byte_strs else "00000000"


def format_hex_dump(data_bytes: bytes, max_bytes: int = 48) -> str:
    """Format bytes into a neat Wireshark-like hex dump."""
    if not data_bytes:
        return "0000: (Empty payload)"

    dump_lines: List[str] = []
    chunk_size = 16
    data_slice = data_bytes[:max_bytes]

    for offset in range(0, len(data_slice), chunk_size):
        chunk = data_slice[offset:offset + chunk_size]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        # Pad hex part to align ascii
        hex_part = hex_part.ljust(16 * 3 - 1)
        ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        dump_lines.append(f"{offset:04X}  {hex_part}  |{ascii_part}|")

    if len(data_bytes) > max_bytes:
        dump_lines.append(f"... ({len(data_bytes) - max_bytes} more bytes)")

    return "\n".join(dump_lines)


def format_bytes(num_bytes: int) -> str:
    """Format bytes into human-readable unit (B, KB, MB, GB)."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    elif num_bytes < 1024 * 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{num_bytes / (1024 * 1024 * 1024):.2f} GB"


def draw_rounded_rect(
    canvas, x1: float, y1: float, x2: float, y2: float, radius: int = 8, **kwargs
) -> int:
    """Draw a smooth rounded rectangle on a Tkinter Canvas."""
    points = [
        x1 + radius, y1,
        x1 + radius, y1,
        x2 - radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)
