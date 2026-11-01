import os
from configparser import ConfigParser

BASE_DIR = os.path.dirname(__file__)


def config(filename="database.ini", section="postgresql"):

    config_path = os.path.join(BASE_DIR, filename)
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(config_path)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, config_path))
    return db
