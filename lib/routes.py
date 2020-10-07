import datetime
import json
import os

from flask import Flask, request, escape
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


@app.teardown_request
def stop(response):
    db.close()
    return response


@app.route('/crash', methods=['POST'])
def store_crash_legacy():
    response = store_crash(request)
    if response["status"] != "reported":
        return response["text"]
    else:
        return response["text"].replace("GitHub",
                                        """<a href="{}">GitHub</a>""".format(response["location"]))


@app.route('/crash.json', methods=['POST'])
def store_crash_v2():
    return json.dumps(store_crash(request))


@app.route('/crash/<id>')
def show_crash(id):
    crash = Crash.get(Crash.id == id)
    return "<pre>{}</pre>".format(escape(crash.stack))


def store_crash(request):
    if not check_rate_limit(request):
        return {
            "text": "Thanks for reporting this issue!",
            "status": "skip",
            "location": None
        }
    crash = json.loads(request.data)
    # Give Windows paths forward slashes
    crash["id"]["file"] = crash["id"]["file"].replace("\\", "/")
    # We only care about the file name
    crash["id"]["file"] = os.path.split(crash["id"]["file"])[1]
    kind, created = CrashKind.get_or_create(**crash["id"])
    del crash["id"]
    crash["kind_id"] = kind.id
    Crash.create(**crash)
    title, body = issues.format_issue(kind.id)
    if kind.github_id < 0:
        issue = github.report_issue(title, body)
        kind.github_id = issue
        kind.save()
    else:
        github.update_issue(kind.github_id, body)
        if github.issue_is_closed(kind.github_id):
            body = issues.format_reopen_comment(kind.id, github.issue_closed_by(kind.github_id))
            if body:
                github.respond(kind.github_id, body)
    url = "https://github.com/{}/issues/{}".format(config.get("github_project"), kind.github_id)
    return {
        "text": "Thanks for reporting this issue! You can track further progress on GitHub.",
        "status": "reported",
        "location": url
    }


def check_rate_limit(request):
    ip = request.remote_addr
    num_requests = LogEntry.select().where(
        LogEntry.sender_ip == ip).where(
        LogEntry.sent_at > (datetime.datetime.now() - datetime.timedelta(hours=24))
    ).count()
    LogEntry.create(sender_ip=ip)
    return num_requests < 4
