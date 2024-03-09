import unittest
import time
from unittest.mock import patch
import sys

# When calling test with -m option it prepend the local path to sys.path
sys.path.append(sys.path[0]+"\\src")
print("HERE 2")
print(sys.path)

from src.main import App


class TestApp(unittest.TestCase):
    def test_take_action_turn_on_ac(self):
        app = App()
        with patch.object(app, "send_action_to_hvac") as mock_send_action_to_hvac:
            app.take_action(70,time.time())
            mock_send_action_to_hvac.assert_called_once_with("TurnOnAc")

    def test_take_action_turn_on_heater(self):
        app = App()
        with patch.object(app, "send_action_to_hvac") as mock_send_action_to_hvac:
            app.take_action(20,time.time())
            mock_send_action_to_hvac.assert_called_once_with("TurnOnHeater")

    def test_take_action_do_nothing(self):
        app = App()
        with patch.object(app, "send_action_to_hvac") as mock_send_action_to_hvac:
            app.take_action(50,time.time())
            mock_send_action_to_hvac.assert_not_called()


if __name__ == "__main__":
    unittest.main()
