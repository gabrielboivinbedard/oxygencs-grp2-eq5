import unittest
from unittest.mock import patch
from src.main import App


class TestApp(unittest.TestCase):
    def test_take_action_turn_on_ac(self):
        app = App()
        with patch.object(app, "send_action_to_hvac") as mock_send_action_to_hvac:
            app.take_action(70)
            mock_send_action_to_hvac.assert_called_once_with("TurnOnAc")

    def test_take_action_turn_on_heater(self):
        app = App()
        with patch.object(app, "send_action_to_hvac") as mock_send_action_to_hvac:
            app.take_action(20)
            mock_send_action_to_hvac.assert_called_once_with("TurnOnHeater")

    def test_take_action_do_nothing(self):
        app = App()
        with patch.object(app, "send_action_to_hvac") as mock_send_action_to_hvac:
            app.take_action(50)
            mock_send_action_to_hvac.assert_not_called()


if __name__ == "__main__":
    unittest.main()
