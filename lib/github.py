from github import Github
from github.GithubObject import NotSet

from lib import config

g = Github(config.get("github_token"))

repo = g.get_repo(config.get("github_project"))


def report_issue(title, body):
    issue = repo.create_issue(title, body)
    return issue.number


def update_issue(id, body):
    repo.get_issue(id).edit(body=body)
    return id


def issue_is_closed(id):
    return repo.get_issue(id).closed_by is not NotSet


def issue_closed_by(id):
    return repo.get_issue(id).closed_by


def respond(id, body):
    repo.get_issue(id).create_comment(body)
