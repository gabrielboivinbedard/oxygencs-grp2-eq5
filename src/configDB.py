from configparser import ConfigParser
import os
import psycopg2

def load_config(filename='./src/database.ini', section='postgresql'):

    parser = ConfigParser()
    parser.read(filename)
    print(os.getcwd())
    files = [f for f in os.listdir(os.getcwd()) if os.path.isfile(f)]
    for f in files:
        print(files)
    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config

def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
