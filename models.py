"""
Data models and state representations for the OSI Communication Simulator.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Callable


class LayerStatus(Enum):
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


@dataclass
class LayerState:
    layer_num: int
    name: str
    status: LayerStatus = LayerStatus.IDLE
    status_text: str = "Listo"
    has_error: bool = False
    details: Dict[str, Any] = field(default_factory=dict)
    added_header: str = ""
    data_summary: str = ""


@dataclass
class PacketInspectorData:
    """Detailed fields for tangible packet dissection at each OSI layer."""
    # L2 Data Link Frame
    frame_dst_mac: str = "AA:BB:CC:44:55:66"
    frame_src_mac: str = "AA:BB:CC:11:22:33"
    frame_type: str = "0x0800 (IPv4)"
    frame_fcs: str = "0x7F2A9C11 (CRC32 Valid)"

    # L3 Network IP Packet
    ip_version: str = "IPv4"
    ip_ttl: int = 64
    ip_protocol: str = "TCP (6)"
    ip_src: str = "192.168.1.10"
    ip_dst: str = "192.168.1.25"
    ip_checksum: str = "0x4A82 (OK)"

    # L4 Transport Segment
    transport_protocol: str = "TCP"
    src_port: int = 54321
    dst_port: int = 80
    seq_num: int = 1001
    ack_num: int = 0
    flags: str = "[PSH, ACK]"
    window_size: int = 65535

    # L5 Session Information
    session_id: str = "SES-8849-B"
    session_state: str = "ESTABLISHED"
    session_token: str = "tok_7721ab90"

    # L6 Presentation Information
    encoding: str = "UTF-8"
    compression: str = "None (Raw)"
    encryption: str = "None (Plaintext)"

    # L7 Application Payload
    app_protocol: str = "HTTP/1.1"
    payload_text: str = ""
    payload_hex: str = ""
    raw_size_bytes: int = 0

    # L1 Physical Bitstream
    bitstream: str = "01001000 01100101 01101100 01101100 01101111"


@dataclass
class RepairOption:
    id: str
    title: str
    description: str
    is_correct: bool
    feedback: str


@dataclass
class TroubleshootIssue:
    layer_num: int
    title: str
    summary: str
    details: str
    options: List[RepairOption]
    on_repair_success: Optional[Callable[[], None]] = None


@dataclass
class StageDecision:
    """An interactive challenge/decision presented to the user at a specific OSI layer."""
    stage_id: str
    layer_num: int
    title: str
    prompt: str
    explanation: str
    input_type: str = "CHOICE"  # "CHOICE", "TEXT_INPUT", "ACTION"
    options: List[Dict[str, Any]] = field(default_factory=list)
    # Each option is a dict: {"id": str, "title": str, "desc": str}
    default_value: str = ""
    input_label: str = ""
    button_label: str = "Enviar decisión y continuar ▶"


@dataclass
class LogEvent:
    timestamp: str
    level: str  # "INFO", "SUCCESS", "WARNING", "ERROR", "STEP"
    icon: str   # "✓", "⚠", "✗", "→", "ℹ"
    message: str
    layer_num: Optional[int] = None
