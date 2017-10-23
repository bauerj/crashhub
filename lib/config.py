import json
import signal

config = {}


def read_config(*_):
    global config
    with open("config.json", "r") as f:
        config = json.load(f)


def get(key):
    return config[key]

# Reload config when SIGHUP is sent
signal.signal(signal.SIGHUP, read_config)
read_config()