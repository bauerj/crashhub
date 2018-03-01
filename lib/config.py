import json
import signal

config = {}


def read_config(*_):
    global config
    with open("config.json", "r") as f:
        config = json.load(f)


def get(key, default=None):
    if key in config:
        return config[key]
    if default:
        return default
    raise MissingValueError(key)


class MissingValueError(BaseException):
    pass

try:
    # Reload config when SIGHUP is sent
    signal.signal(signal.SIGHUP, read_config)
except AttributeError:
    pass  # Windows
read_config()