import os
import sys
import unittest
import time
from unittest.mock import patch

# When calling test with -m option it prepend the local path to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from src.main import App


class TestApp(unittest.TestCase):
    def test_take_action_turn_on_ac(self):
        app = App(None,None)
        with patch.object(app, "send_action_to_hvac") as mock_send_action_to_hvac:
            app.take_action(70, time.time())
            mock_send_action_to_hvac.assert_called_once_with("TurnOnAc")

    def test_take_action_turn_on_heater(self):
        app = App(None,None)
        with patch.object(app, "send_action_to_hvac") as mock_send_action_to_hvac:
            app.take_action(20, time.time())
            mock_send_action_to_hvac.assert_called_once_with("TurnOnHeater")

    def test_take_action_do_nothing(self):
        app = App(None,None)
        with patch.object(app, "send_action_to_hvac") as mock_send_action_to_hvac:
            app.take_action(40, time.time())
            mock_send_action_to_hvac.assert_not_called()


if __name__ == "__main__":
    unittest.main()
