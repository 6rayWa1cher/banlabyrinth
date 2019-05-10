import configparser
import os

from appdirs import user_data_dir, user_log_dir

from banlabyrinth import appname, appauthor

CONFIG_DIR = user_data_dir(appname, appauthor)
CONFIG_PATH = user_data_dir(appname, appauthor) + os.sep + "config.ini"


def update_config(config):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)


def create_config():
    config = configparser.ConfigParser()
    config["DEFAULT"]["token"] = "fill_me"
    config["DEFAULT"]["command-prefix"] = "#"
    config.add_section("paths")
    config["paths"]["logs"] = user_log_dir(appname, appauthor) + os.sep
    config["paths"]["database"] = user_data_dir(appname, appauthor) + os.sep + "database.sqlite"
    update_config(config)


def get_token():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if "token" not in config["DEFAULT"] or config["DEFAULT"]["token"] is None or config["DEFAULT"][
        "token"] == "fill_me":
        raise ValueError("Discord token not provided in \"{}\" !".format(os.path.abspath(CONFIG_PATH)))
    return config["DEFAULT"]["token"]


def _get_path(section, option, default, is_dir):
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    path = config.get(section, option, fallback=None)
    prev = path
    if path is None:
        path = default
    if not path.endswith(os.sep) and is_dir:
        path += os.sep
    sub_path = os.path.dirname(path) if not is_dir else path
    os.makedirs(sub_path, exist_ok=True)
    if prev != path:
        if section not in config:
            config.add_section(section)
        config.set(section, option, path)
        update_config(config)
    return path


def get_logs_path():
    return _get_path("paths", "logs",
                     user_log_dir(appname, appauthor),
                     True)


def get_db_path():
    return _get_path("paths", "database",
                     user_data_dir(appname, appauthor) + os.sep + "database.sqlite",
                     False)


def get_command_prefix():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if "command-prefix" not in config["DEFAULT"] or len(config["DEFAULT"]["command-prefix"]) != 1:
        config["DEFAULT"]["command-prefix"] = '#'
        update_config(config)
    return config["DEFAULT"]["command-prefix"]
