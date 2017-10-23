from github import Github

from lib import config

g = Github(config.get("github_token"))

repo = g.get_repo(config.get("github_project"))


def report_issue(title, body):
    issue = repo.create_issue(title, body)
    return issue.number


def update_issue(id, title, body):
    repo.get_issue(id).edit(title, body)
    return id
