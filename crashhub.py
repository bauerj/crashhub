#!/bin/python3

from lib.routes import app

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
