"""
Automated unit test for the 4 core interactive missions in the OSI Communication Simulator.
"""

import unittest
import tkinter as tk
from missions import get_all_missions, get_mission_by_id
from main import OsiSimulatorApp


class TestOsiSimulator(unittest.TestCase):
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

    def test_four_missions_exist(self):
        missions = get_all_missions()
        self.assertEqual(len(missions), 4)
        ids = [m.mission_id for m in missions]
        self.assertEqual(ids, [1, 2, 3, 4])

    def test_mission1_file_stages(self):
        m = get_mission_by_id(1)
        m.start_mission()
        self.assertGreaterEqual(len(m.stages), 5)
        # Stage 0 should be packaging
        self.assertEqual(m.stages[0].stage_id, "l7_packaging")
        self.assertEqual(m.stages[1].stage_id, "l4_protocol")

    def test_mission2_web_stages(self):
        m = get_mission_by_id(2)
        m.start_mission()
        self.assertGreaterEqual(len(m.stages), 4)
        self.assertEqual(m.stages[0].stage_id, "l7_dns")

    def test_mission3_videocall_stages(self):
        m = get_mission_by_id(3)
        m.start_mission()
        self.assertGreaterEqual(len(m.stages), 4)
        self.assertEqual(m.stages[0].stage_id, "l6_codec")

    def test_mission4_text_stages(self):
        m = get_mission_by_id(4)
        m.start_mission()
        self.assertGreaterEqual(len(m.stages), 3)
        self.assertEqual(m.stages[0].stage_id, "l7_text_input")

    def test_app_view_switching(self):
        app = OsiSimulatorApp(self.root)
        self.assertIsNotNone(app.current_view)

        # Launch Mission 1
        app.launch_mission(1)
        self.assertIsNotNone(app.active_simulator_view)
        self.assertEqual(app.active_simulator_view.mission.mission_id, 1)

        # Return to menu
        app.show_mission_select()
        self.assertIsNone(app.active_simulator_view)


if __name__ == "__main__":
    unittest.main()
