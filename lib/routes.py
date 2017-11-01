import datetime
import json
import os

from flask import Flask, request
from peewee import OperationalError

from lib import issues, github, config
from lib.database import db, create_tables, CrashKind, Crash, LogEntry

app = Flask(__name__)

db.connect()
create_tables()
db.close()


@app.before_request
def setup():
    try:
        db.connect()
    except OperationalError:
        pass


@app.after_request
def stop(response):
    db.close()
    return response


@app.route('/crash', methods=['POST'])
def store_crash():
    if not check_rate_limit(request):
        return "Thanks for reporting this issue!"
    crash = json.loads(request.data)
    crash["id"]["file"] = os.path.split(crash["id"]["file"])[1]
    kind, created = CrashKind.get_or_create(**crash["id"])
    del crash["id"]
    crash["kind_id"] = kind.id
    Crash.create(**crash)
    title, body = issues.format_issue(kind.id)
    if created:
        issue = github.report_issue(title, body)
        kind.github_id = issue
        kind.save()
    else:
        github.update_issue(kind.github_id, title, body)
    url = "https://github.com/{}/issues/{}".format(config.get("github_project"), kind.github_id)
    return """
    Thanks for reporting this issue! You can track further progress on <a href="{url}">GitHub</a>.
    """.format(url=url)


def check_rate_limit(request):
    ip = request.remote_addr
    num_requests = LogEntry.select().where(
        LogEntry.sender_ip == ip).where(
        LogEntry.sent_at > (datetime.datetime.now() - datetime.timedelta(hours=24))
    ).count()
    LogEntry.create(sender_ip=ip)
    return num_requests < 4
