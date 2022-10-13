from dataclasses import asdict
import logging

from flask import Flask, request
from github import GithubREST

from query_params import QueryParams, DEFAULT_PAGE, DEFAULT_PER_PAGE


dev_mode = True
app = Flask(__name__)
github = GithubREST()
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s %(message)s",
)


@app.route("/")
def health_check() -> dict:
    return {
        "data": "Hello, welcome to Sleuth backend interview task. Please see instructions in README.md"
    }


@app.route("/health/github")
def github_api_root_example() -> dict:
    return GithubREST().get("/")


@app.route("/github/repos/<path:repository>/pulls", methods=["GET"])
def github_repository_pull_requests(repository: str):
    data = []
    pr_path = f'/repos/{repository}/pulls'
    # collect query params
    page = request.args.get("page", DEFAULT_PAGE)
    per_page = request.args.get("per_page", DEFAULT_PER_PAGE)
    query_params = QueryParams(page=page, per_page=per_page)
    # list repos PRs: https://docs.github.com/en/rest/pulls/pulls#list-pull-requests
    prs = github.get(pr_path, asdict(query_params))
    for pr in prs.get('data'):
        links = pr.get('_links')
        commits_url = links.get('commits')
        commits = github.get(commits_url.get('href'))
        user = pr.get('user')
        head = pr.get('head')
        data.append({
            'title': pr.get('title'),
            'author': user.get('login'),
            'commits': len(commits['data']),
            'head_sha': head.get('sha'),
            'updated': pr.get('updated_at')
        })
    response = {"data": data}
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
