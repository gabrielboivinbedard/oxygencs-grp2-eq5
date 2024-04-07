import logging
import json
import signal
import sys
import time
import os
import argparse
from signalrcore.hub_connection_builder import HubConnectionBuilder
import requests
from configDB import DatabaseConfig


class App:

    DEBUG = True

    def __init__(self, host, token):
        signal.signal(signal.SIGINT, self.signal_handler)
        if host is None:
            host = os.getenv("HVAC_HOST", "159.203.50.162")
        if token is None:
            token = os.getenv("TOKEN", "a77e02c82ab10e660da7")
        self.HOST = "http://" + host
        self.TOKEN = token

        if self.DEBUG:
            test_host = os.getenv("HVAC_HOST")
            if test_host is not None:
                print("test_host = " + test_host)
            else:
                print("test_host IS NULL")
            test_token = os.getenv("TOKEN")
            if test_token is not None:
                print("test_token = " + test_token)
            else:
                print("test_token IS NULL")

        print(
            "/*--------------------------------------------*/ Informations /*---------------------------------------------------*/"
        )
        print("Listen to Host :" + self.HOST)
        print("Listen to Token :" + self.TOKEN)
        print(
            "To modify these when running the docker image please define HOST_IP and TOKEN_ROOM environment variables :"
        )
        print(
            "docker run -e HOST_IP={yourHostIP} -e TOKEN_ROOM={yourToken} {imageName}:{tag}"
        )
        print(
            "/*-----------------------------------------------------------------------------------------------------------------*/"
        )

        # Configurations
        self._hub_connection = None
        self.TICKS = 10

        # Temperature configuration
        self.T_MAX = 45
        self.T_MIN = 30

        # Database configurations
        self.DATABASE_URL = "157.230.69.113:5432"
        db_config = DatabaseConfig()
        db_params = db_config.load_config()
        self.conn = db_config.connect(db_params)

    def signal_handler(self, sig, frame):
        print("SIGINT or CTRL-C detected. Exiting gracefully")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        try:
            if self._hub_connection is not None:
                self._hub_connection.stop()
            if self.conn is not None:
                self.conn.close()
                print("Database connection closed.")
        except Exception as e:
            print(f"An error occurred during the database connection closing: {e}")

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
            self.take_action(temperature, timestamp)
            self.save_temperature_to_database(timestamp, temperature)
        except IndexError as index_err:
            print(f"IndexError occurred: {index_err}")
        except ValueError as value_err:
            print(f"ValueError occurred: {value_err}")

    def take_action(self, temperature, timestamp):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.T_MAX):
            self.send_action_to_hvac("TurnOnAc")
            self.save_event_to_database(timestamp, "AC")
        elif float(temperature) <= float(self.T_MIN):
            self.send_action_to_hvac("TurnOnHeater")
            self.save_event_to_database(timestamp, "TurnOnHeater")

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

    def save_temperature_to_database(self, timestamp, temperature):
        """Save sensor data into database."""
        try:
            cur = self.conn.cursor()
            sql = (
                """INSERT INTO temperatures (timestamp, temperature) VALUES (%s, %s)"""
            )
            cur.execute(sql, (timestamp, temperature))
            self.conn.commit()
        except requests.exceptions.RequestException as e:
            print(e)
            print(
                "The database commit failed for values : %s,%s",
                (timestamp, temperature),
            )

    def save_event_to_database(self, timestamp, event):
        """Save sensor data into database."""
        try:
            cur = self.conn.cursor()
            sql = """INSERT INTO events (timestamp, event) VALUES (%s, %s)"""
            cur.execute(sql, (timestamp, event))
            self.conn.commit()
        except requests.exceptions.RequestException as e:
            print(e)
            print("The database commit failed for values : %s,%s", (timestamp, event))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start Oxygen CS.")
    parser.add_argument(
        "--host", type=str, required=False, help="Host IP of the habitation"
    )
    parser.add_argument("--token", type=str, required=False, help="Token of the room")
    args = parser.parse_args()
    app = App(args.host, args.token)
    app.start()
