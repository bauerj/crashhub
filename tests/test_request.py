import json

import github
import os
import pytest

os.chdir(os.path.dirname(__file__))


@pytest.fixture
def crashhub_client(tmpdir, mocker):
    mocker.patch("github.Github")
    mocker.patch("lib.config.read_config")

    from lib import config
    config.config["db_name"] = "{}/db.sqlite3".format(tmpdir)

    from crashhub import app
    from lib import database
    app.testing = True
    client = app.test_client()
    with app.app_context():
        database.create_tables()

    return client


request = r"""
{
    "app_version": "b'3.0.3-367-g3838fdb'3.1", 
    "description": "Test", 
    "exc_string": "division by zero", 
    "id": {
      "file": "C:/Users/bauerj/Documents/GitHub/electrum\\gui\\qt\\main_window.py", 
      "name": "show_about", 
      "type": "ZeroDivisionError"
    }, 
    "locale": "de_DE", 
    "os": "Windows-10-10.0.16299-SP0", 
    "stack": "  File \"C:/Users/bauerj/Documents/GitHub/electrum\\gui\\qt\\main_window.py\", line 544, in show_about\n    1/0\n", 
    "wallet_type": "standard"
}
"""


def test_first(crashhub_client):
    response = crashhub_client.post("/crash", data=request)
    assert b"You can track further progress on" in response.data
    github.Github.return_value.get_repo.return_value.create_issue.assert_called_once()
    github.Github.return_value.get_repo.return_value.get_issue.assert_not_called()


def test_updated(crashhub_client):
    for _ in range(2):
        response = crashhub_client.post("/crash", data=request)
    github.Github.return_value.get_repo.return_value.create_issue.assert_called_once()
    github.Github.return_value.get_repo.return_value.get_issue.assert_called_once()


def test_rate_limit(crashhub_client):
    for _ in range(5):
        response = crashhub_client.post("/crash", data=request)
    assert b"You can track further progress on" not in response.data


def test_v2(crashhub_client):
    response = json.loads(crashhub_client.post("/crash.json", data=request).data)
    assert response["status"] == "reported"
