"""
Integration test for full decision-driven execution across all 4 core missions.
Verifies decisions, consequences, error repairs, and end-to-end completion.
"""

import unittest
import tkinter as tk
from missions import get_mission_by_id


class TestFullInteractivePipelines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def setup_mission_sync(self, mission):
        mission.cb_network_animate = lambda f, t, pt, l, d, cb: cb() if cb else None
        mission.cb_log = lambda lvl, icon, msg, lyr: None
        mission.cb_update_layer = lambda side, lyr, st, txt, err: None
        mission.cb_trigger_troubleshoot = None
        mission.cb_mission_complete = None
        mission.cb_inspector_update = None
        mission.cb_output_update = None
        mission.cb_decision_ready = None

    def test_mission1_decision_pipeline(self):
        m = get_mission_by_id(1)
        self.setup_mission_sync(m)
        m.start_mission()

        # Step 0: Test Monolithic consequence
        m.submit_user_decision("monolithic")
        self.assertTrue(m.is_paused)
        self.assertEqual(m.active_issue.layer_num, 7)
        # Repair packaging
        m.resolve_current_error()
        self.assertFalse(m.is_paused)

        # Step 1: Protocol choice (TCP)
        m.submit_user_decision("tcp")
        self.assertEqual(m.selected_protocol, "TCP")

        # Step 2: Handshake (SYN)
        m.submit_user_decision("syn")

        # Step 3: Destination IP (192.168.1.25)
        m.submit_user_decision("192.168.1.25")

        # Step 4: Retransmit chunk 3
        m.submit_user_decision("retransmit")

        # Step 5: Final checksum verification
        m.submit_user_decision("action")
        self.assertEqual(m.current_phase, "COMPLETE")

    def test_mission2_decision_pipeline(self):
        m = get_mission_by_id(2)
        self.setup_mission_sync(m)
        m.start_mission()

        # Step 0: Test DNS failure consequence
        m.submit_user_decision("0.0.0.0")
        self.assertTrue(m.is_paused)
        self.assertEqual(m.active_issue.layer_num, 7)
        # Repair DNS
        m.resolve_current_error()
        self.assertEqual(m.dns_server, "8.8.8.8")

        # Step 1: Protocol & Port (HTTPS 443)
        m.submit_user_decision("https_443")
        self.assertEqual(m.selected_port, 443)

        # Step 2: Gateway (192.168.1.1)
        m.submit_user_decision("gateway")

        # Step 3: Render webpage
        m.submit_user_decision("action")
        self.assertEqual(m.current_phase, "COMPLETE")

    def test_mission3_videocall_decision_pipeline(self):
        m = get_mission_by_id(3)
        self.setup_mission_sync(m)
        m.start_mission()

        # Step 0: Codec (H.264)
        m.submit_user_decision("h264")

        # Step 1: Transport (UDP)
        m.submit_user_decision("udp")

        # Step 2: Session (SIP)
        m.submit_user_decision("sip")

        # Step 3: Stream frames
        m.submit_user_decision("action")
        self.assertEqual(m.current_phase, "COMPLETE")

    def test_mission4_text_decision_pipeline(self):
        m = get_mission_by_id(4)
        self.setup_mission_sync(m)
        m.start_mission()

        # Step 0: Type custom message
        m.submit_user_decision("¡Hola Mundo! 🚀")
        self.assertEqual(m.raw_message, "¡Hola Mundo! 🚀")

        # Step 1: Encoding (UTF-8)
        m.submit_user_decision("utf8")

        # Step 2: Receiver decoding (mismatch to test Mojibake consequence!)
        m.submit_user_decision("mismatch_latin1")
        self.assertTrue(m.is_paused)
        self.assertEqual(m.active_issue.layer_num, 6)

        # Repair Mojibake
        m.resolve_current_error()
        self.assertEqual(m.receiver_decoding, "UTF-8")
        self.assertEqual(m.current_phase, "COMPLETE")


if __name__ == "__main__":
    unittest.main()
