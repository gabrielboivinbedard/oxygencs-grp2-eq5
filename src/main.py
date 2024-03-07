import logging
import json
import time
from signalrcore.hub_connection_builder import HubConnectionBuilder
import requests


class App:
    def __init__(self):
        self._hub_connection = None
        self.TICKS = 10

        # To be configured by your team
        self.HOST = "http://159.203.50.162"  # Setup your host here
        self.TOKEN = "a77e02c82ab10e660da7"  # Setup your token here
        self.T_MAX = 60  # Setup your max temperature here
        self.T_MIN = 30  # Setup your min temperature here
        self.DATABASE_URL = "157.230.69.113:5432"  # Setup your database here

    def __del__(self):
        if self._hub_connection is not None:
            self._hub_connection.stop()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )
        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(temperature)
            self.save_event_to_database(timestamp, temperature)
        except IndexError as index_err:
            print(f"IndexError occurred: {index_err}")
        except ValueError as value_err:
            print(f"ValueError occurred: {value_err}")

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.T_MAX):
            self.send_action_to_hvac("TurnOnAc")
        elif float(temperature) <= float(self.T_MIN):
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        try:
            r = requests.get(
                f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{self.TICKS}", timeout=5
            )
            details = json.loads(r.text)
            print(details, flush=True)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request: {e}")

    def save_event_to_database(self, timestamp, temperature):
        """Save sensor data into database."""
        try:
            # TODO: To implement
            pass
        except requests.exceptions.RequestException as e:
            # TODO: To implement
            pass


if __name__ == "__main__":
    app = App()
    app.start()
