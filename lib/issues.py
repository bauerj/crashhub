from distutils.version import LooseVersion

from lib.database import Crash, CrashKind
from lib import config
from playhouse.shortcuts import model_to_dict

from lib.util import get_greeting

template = """
Crash Report
============

This crash report was reported through the automatic crash reporting system 🤖

Traceback
--------------

```Python traceback
{stack}
{type}: {exc_string}
```

Reporter
------------

This issue was reported by {user_count} user(s):

| {app_name} Version  | Python Version | Operating System  | Wallet Type  | Locale |
|---|---|---|---|---|
{reporter_table}

Additional Information
------------------------

"""

reporter_row = """| {app_version}  | {python_version} | {os} | {wallet_type} | {locale} |
"""

no_info = "The reporting user(s) did not provide additional information."

template_reopen = """
{greeting} @{user_closed},

I just received another crash report related to this issue. The crash occured on {app_name} {version}.
I'm not sure which versions of {app_name} include the fix but this is the first report from anything
newer than {min_version} since you closed the issue.

Could you please check if this issue really is resolved? Here is the traceback that I just collected:

```Python traceback
{stack}
{type}: {exc_string}
```


~ _With robotic wishes_
"""


def format_issue(kind_id):
    kind = CrashKind.get(id=kind_id)
    crashes = Crash.select().where(Crash.kind_id == kind_id)
    reporter_table = ""
    additional = []
    for c in crashes:
        reporter_table += reporter_row.format(**model_to_dict(c)).replace("\n", " ") + "\n"
        if c.description:
            additional.append(c.description)
    v = {
        "stack": crashes[0].stack,
        "type": kind.type,
        "exc_string": crashes[0].exc_string,
        "reporter_table": reporter_table,
        "user_count": len(crashes),
        "app_name": config.get("app_name")
    }
    report = template.format(**v)
    if additional:
        for a in additional:
            report += "\n> ".join([""] + a.splitlines())
            report += "\n\n---\n\n"
    else:
        report += no_info
    title = kind.type + ": " + crashes[0].exc_string
    if len(title) > 400:
        title = title[:400] + "..."
    return title, report


def format_reopen_comment(kind_id, closed_by):
    kind = CrashKind.get(id=kind_id)
    crashes = Crash.select().where(Crash.kind_id == kind_id)
    if len(crashes) < 2:
        return None
    crashes, new_crash = crashes[:-1], crashes[-1:][0]
    min_version = None
    for c in crashes:
        if not min_version or LooseVersion(min_version) < LooseVersion(c.app_version):
            min_version = c.app_version
    if not LooseVersion(min_version) < LooseVersion(new_crash.app_version):
        return None
    v = {
        "greeting": get_greeting(),
        "user_closed": closed_by.login,
        "app_name": config.get("app_name"),
        "version": new_crash.app_version,
        "min_version": min_version,
        "stack": new_crash.stack,
        "type": kind.type,
        "exc_string": new_crash.exc_string
    }
    return template_reopen.format(**v)
