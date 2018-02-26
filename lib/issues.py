from lib.database import Crash, CrashKind
from playhouse.shortcuts import model_to_dict

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

| Electrum Version  | Operating System  | Wallet Type  | Locale |
|---|---|---|---|
{reporter_table}

Additional Information
------------------------

"""

reporter_row = """| {app_version}  | {os} | {wallet_type} | {locale} |
"""

no_info = "The reporting user(s) did not provide additional information."


def format_issue(kind_id):
    kind = CrashKind.get(id=kind_id)
    crashes = Crash.select().where(Crash.kind_id == kind_id)
    reporter_table = ""
    additional = []
    for c in crashes:
        reporter_table += reporter_row.format(**model_to_dict(c))
        if c.description:
            additional.append(c.description)
    v = {
        "stack": crashes[0].stack,
        "type": kind.type,
        "exc_string": crashes[0].exc_string,
        "reporter_table": reporter_table,
        "user_count": len(crashes)
    }
    report = template.format(**v)
    if additional:
        for a in additional:
            report += "\n> ".join([""] + a.splitlines())
            report += "\n\n---\n\n"
    else:
        report += no_info
    title = kind.type + ": " + crashes[0].exc_string
    return title, report

