# OSI Communication Simulator 🌐⚡

An interactive, **decision-driven** educational simulator of computer network communication and troubleshooting based on the **7-Layer OSI Model**, built with Python & Tkinter.

Instead of passive "auto-play" where students merely observe animations, this simulator requires the user to **actively make networking decisions, configure protocols, and type inputs at each OSI layer**. Every choice produces **real-world network consequences** (MTU drops, connection resets, head-of-line blocking lag, buffer overflows, or Mojibake text corruption).

---

## 🚀 Key Improvements & Features

* **100% Decision-Driven (No Passive Auto-Play)**: The passive "Play" button has been completely eliminated. The user is actively presented with interactive decision consoles, typed parameters, and protocol choices at every layer.
* **Realistic Network Consequences**:
  * Choosing unsegmented data $\to$ **MTU Buffer Overflow** at Layer 7/1.
  * Choosing UDP for file transfers $\to$ **Corrupted, incomplete files** when packets drop.
  * Choosing TCP for real-time video calls $\to$ **Head-of-Line blocking freeze (1450ms lag)**.
  * Entering invalid DNS IPs (`0.0.0.0`) $\to$ **DNS Resolution Failure**.
  * Picking ASCII for multilingual text $\to$ **UnicodeEncodeError / Character strip**.
  * Mismatched receiver decoder (Latin-1 vs UTF-8) $\to$ **Real Mojibake (`Ã¡Hola MarÃa!`) rendered on the receiver's phone screen**.
* **Interactive Troubleshooting & Repair System (🔧)**: When an incorrect choice causes a network problem, a prominent wrench appears on the affected OSI layer. Clicking it opens a diagnostic interface explaining the root cause and providing corrective actions to resume transmission.
* **Dual 7-Layer OSI Stacks**: Visual vertical stacks for both **Person A (Sender)** and **Person B (Receiver)** highlighting active processing, completed headers, and error states.
* **Animated Network Topology**: Real-time canvas illustrating routers, switches, physical cables, moving packet flights, bitstream pulses, and packet drop explosions ($💥$).
* **Deep Packet & Frame Inspector**: Dissects Ethernet II Frames, IPv4 Packets, Transport Segments (Ports, Flags, Seq/Ack), Session tokens, and raw Wireshark-like hex dumps.
* **Chronological Event Log**: Real-time log tracking user decisions, network reactions, timestamps, and severity filters.

---

## 🎯 The 4 Core Missions

1. **📁 Mission 1 — Send a Large File (`mission1_file.py`)**:
   * *Focus*: Layer 4 (Transport) & Layer 7 (Application)
   * *Decisions & Challenges*:
     1. **L7 Packaging**: Choose between segmenting the 500 MB file into discrete MTU chunks vs. sending an unsegmented monolithic stream (causes MTU buffer overflow!).
     2. **L4 Protocol**: Select TCP (reliable, sequence numbers) vs. UDP (unreliable).
     3. **L4 Handshake**: Actively send the `SYN` control flag to initiate the TCP 3-Way Handshake (`SYN` $\to$ `SYN-ACK` $\to$ `ACK`).
     4. **L3 Addressing**: Confirm destination IP `192.168.1.25` vs invalid host `192.168.1.99`.
     5. **Network Packet Loss Response**: When Chunk #3 is dropped at the core router, choose whether to perform TCP Fast Retransmission or ignore it (causing file corruption).
     6. **L7 Integrity**: Verify cryptographic MD5 checksum on receiver.

2. **🌐 Mission 2 — Access a Website (`mission2_web.py`)**:
   * *Focus*: Layer 7 (DNS/HTTP), Layer 6 (TLS), Layer 4 (Ports), and Layer 3 (Routing)
   * *Decisions & Challenges*:
     1. **L7 DNS Resolution**: Select nameserver IP (`8.8.8.8` vs `0.0.0.0`) over UDP port 53 to resolve `www.example.com` to `93.184.216.34`.
     2. **L4/L6 Protocol & Port**: Choose HTTPS (Port 443 with TLS 1.3) vs HTTP (Port 80 plaintext) vs invalid Port 8080 (causes `TCP RST: Connection Refused`).
     3. **L3 Gateway Routing**: Decide whether to forward the off-subnet packet to the Default Gateway Router (`192.168.1.1`) or broadcast locally (causes ARP timeout).
     4. **L7 Browser Rendering**: Parse server's `HTTP/1.1 200 OK` response and inspect rendered HTML page and SSL lock badge.

3. **📹 Mission 3 — Make a Video Call (`mission3_videocall.py`)**:
   * *Focus*: Layer 6 (Codecs) & Layer 4 (Low-Latency UDP vs TCP Stalls)
   * *Decisions & Challenges*:
     1. **L6 Video Compression**: Select H.264 AVC lossy compression (~2 Mbps) vs Raw uncompressed RGB24 (causes a 660 Mbps link saturation crash!).
     2. **L4 Transport Protocol**: Select UDP/RTP (prioritizing real-time timeliness) vs TCP (guaranteeing ordered delivery).
     3. **L5 Session Signaling**: Select SIP/SDP (Port 5060) to negotiate call capabilities.
     4. **Packet Loss Consequence**: When a frame drops in transit:
        * Under TCP: Head-of-line blocking halts playback! The screen freezes (`❄️ STREAM FROZEN`), audio buffers, and latency spikes to 1450 ms!
        * Under UDP: The dropped frame is skipped, and the call continues fluidly at 22 ms!

4. **💬 Mission 4 — Send a Text Message (`mission4_text.py`)**:
   * *Focus*: Layer 7 (User Input) & Layer 6 (Presentation Character Encodings)
   * *Decisions & Challenges*:
     1. **L7 Text Input**: Type custom multilingual text with accents or emojis (e.g., `¡Hola María! ¿Cómo estás? 🚀`).
     2. **L6 Character Encoding**: Choose between UTF-8 (variable-length Unicode) and 7-bit ASCII (causes immediate `UnicodeEncodeError` on Spanish accents and emojis!).
     3. **L6 Receiver Decoding**: Choose matching UTF-8 vs ISO-8859-1 (Latin-1).
        * If Latin-1 is chosen on UTF-8 bytes: Classic **Mojibake** (`Ã¡Hola MarÃa! Â¿CÃ³mo estÃ¡s?`) appears on Person B's smartphone chat screen!
        * Repairing to UTF-8 cleans the text and awards double checkmarks.

---

## 🛠 Project Structure

```text
osi_simulator/
├── main.py                     # Entry point, Enter key submission & screen navigation
├── theme.py                    # Colors (7 OSI layer color coding, dark theme, typography)
├── models.py                   # Data models (StageDecision, PacketInspectorData, TroubleshootIssue)
├── README.md                   # Full user guide and learning documentation
├── test_simulator.py           # Automated unit tests for all 4 missions & stages
├── test_full_pipeline.py       # Integration tests for decisions, consequences & repairs
├── test_gui.py                 # Automated Tkinter GUI rendering & interaction test
├── utils/
│   ├── __init__.py
│   └── helpers.py              # Hex dump formatter, bitstream converter, time helpers
├── gui/
│   ├── __init__.py
│   ├── mission_select.py       # 4 Mission cards with challenge highlights
│   ├── simulator_view.py       # Decision-Driven Console & Dual OSI Stacks
│   ├── osi_stack_widget.py     # 7-layer visual stack cards with wrench repair triggers
│   ├── network_canvas.py       # Animated network topology with moving packets & drops
│   ├── inspector_widget.py     # Deep packet/frame header & hex payload inspector
│   ├── event_log_widget.py     # Real-time event log with filters & timestamps
│   ├── repair_dialog.py        # Interactive diagnosis & repair modal (🔧)
│   └── completion_dialog.py    # Mission complete celebration & summary modal
└── missions/
    ├── __init__.py             # Mission registry & factory
    ├── base_mission.py         # Decision-driven mission lifecycle & callbacks
    ├── mission1_file.py        # 📁 Mission 1: Send a Large File
    ├── mission2_web.py         # 🌐 Mission 2: Access a Website
    ├── mission3_videocall.py   # 📹 Mission 3: Make a Video Call
    └── mission4_text.py        # 💬 Mission 4: Send a Text Message
```

---

## 💻 How to Run

### Requirements
- Python 3.9+
- Tkinter (standard on Linux/macOS/Windows)

### Launch the Simulator:
```bash
python3 main.py
```

### Run Automated Unit and Integration Tests:
```bash
python3 test_simulator.py
python3 test_full_pipeline.py
python3 test_gui.py
```

---

## 🎮 How to Play

1. **Select a Mission** from the main menu.
2. Read the prompt in the **Interactive Decision Console** at the bottom of the screen.
3. **Make your decision** (select a radio option, type into the input field, or trigger the action).
4. Click **Submit Decision & Proceed ▶** (or press `Enter`).
5. **Watch the consequence** unfold on the Network Topology and Receiver Monitor!
6. If an error occurs, click the **🔧 REPAIR** button on the affected OSI layer to diagnose and fix it.
