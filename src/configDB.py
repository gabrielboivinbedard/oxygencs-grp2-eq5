from configparser import ConfigParser
import psycopg2


class DatabaseConfig:
    def __init__(self, filename="./src/database.ini", section="postgresql"):
        self.filename = filename
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
            with psycopg2.connect(**config) as conn:
                print("Connected to the PostgreSQL server.")
                return conn
        except (psycopg2.DatabaseError, Exception) as error:
            print(error)
            raise ConnectionError(
                "Failed to connect to the PostgreSQL server."
            ) from error
