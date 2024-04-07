from configparser import ConfigParser
import os
import psycopg2


class DatabaseConfig:
    def __init__(self, filename="database.ini", section="postgresql"):
        # Calcule le chemin absolu du fichier database.ini basé sur l'emplacement de ce fichier (configDB.py)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(base_dir, filename)
        self.section = section

    def load_config(self):
        parser = ConfigParser()
        parser.read(self.filename)
        config = {}
        if parser.has_section(self.section):
            params = parser.items(self.section)
            for param in params:
                config[param[0]] = param[1]
        else:
            raise Exception(
                f"Section [{self.section}] not found in the [{self.filename}] file"
            )
        return config

    def connect(self, config):
        try:
            print("Connecting to PostgreSQL server with config:")
            print(config)
            with psycopg2.connect(**config) as conn:
                print("Connected to the PostgreSQL server.")
                return conn
        except (psycopg2.DatabaseError, Exception) as error:
            print("Failed to connect to the PostgreSQL server.")
            print(error)
            raise ConnectionError(
                "Failed to connect to the PostgreSQL server."
            ) from error
