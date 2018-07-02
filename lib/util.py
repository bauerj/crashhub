import datetime
import traceback

from lib import issues, github
from lib.database import CrashKind


def get_greeting():
    now = datetime.datetime.now()
    if now.hour < 12:
        return "Good morning"
    if now.hour < 17:
        return "Good afternoon"
    return "Good evening"


def update_posts(dry_run):
    kinds = CrashKind.select()
    for k in kinds:
        try:
            if not k.github_id:
                continue
            _, body = issues.format_issue(k.id)
            if not dry_run:
                github.update_issue(k.github_id, body)
            if github.issue_is_closed(k.github_id):
                body = issues.format_reopen_comment(k.id, github.issue_closed_by(k.github_id))
                if body:
                    print("Respond", k.github_id, body)
                    if not dry_run:
                        github.respond(k.github_id, body)
        except:
            traceback.print_exc()
