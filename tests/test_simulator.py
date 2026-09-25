import unittest

from missions import all_missions
from simulator.engine import simulate_mission


class SimulatorTests(unittest.TestCase):
    def test_all_missions_registered(self):
        missions = all_missions()
        self.assertEqual(7, len(missions))
        self.assertEqual([1, 2, 3, 4, 5, 6, 7], [m.mission_id for m in missions])

    def test_wrong_choice_triggers_error_and_repair(self):
        mission = next(m for m in all_missions() if m.mission_id == 7)
        result = simulate_mission(mission, predefined_selections={"Presentation": "ASCII"})

        self.assertTrue(result.success)
        self.assertEqual("UTF-8", result.selected_options["Presentation"])
        self.assertEqual(1, len(result.errors))
        self.assertIn("Encoding mismatch", result.errors[0])

    def test_encapsulation_objects_created_for_all_layers(self):
        mission = next(m for m in all_missions() if m.mission_id == 1)
        result = simulate_mission(mission)

        self.assertEqual(7, len(result.layer_objects))
        self.assertIn("Transport", result.layer_objects)
        self.assertIn("Type", result.layer_objects["Transport"])


if __name__ == "__main__":
    unittest.main()
