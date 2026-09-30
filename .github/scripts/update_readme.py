import json
import os
import subprocess
from datetime import datetime

USERNAME = "hernanrengel"

START = "<!--START_GITHUB_ACTIVITY-->"
END = "<!--END_GITHUB_ACTIVITY-->"


def github_api(endpoint):
    result = subprocess.run(
        [
            "gh",
            "api",
            endpoint,
            "--paginate",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)


def format_date(date_string):
    date = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
    return date.strftime("%b %d, %Y")


def main():
    repos = github_api(
        f"/users/{USERNAME}/repos?sort=updated&direction=desc&per_page=10"
    )

    repos = [
        repo
        for repo in repos
        if not repo["fork"]
        and not repo["archived"]
        and repo["name"] != USERNAME
    ]

    repos = repos[:5]

    lines = [
        "## GitHub Activity",
        "",
        "Recent public projects and repositories:",
        "",
    ]

    for repo in repos:
        name = repo["name"]
        description = repo["description"] or "No description"
        language = repo["language"] or "N/A"
        updated = format_date(repo["updated_at"])
        stars = repo["stargazers_count"]
        url = repo["html_url"]

        lines.extend(
            [
                f"### [{name}]({url})",
                f"{description}",
                "",
                f"`{language}` · ⭐ {stars} · Updated {updated}",
                "",
            ]
        )

    activity = "\n".join(lines)

    with open("README.md", "r", encoding="utf-8") as file:
        readme = file.read()

    start_index = readme.find(START)
    end_index = readme.find(END)

    if start_index == -1 or end_index == -1:
        raise RuntimeError("README markers not found")

    start_index += len(START)

    new_readme = (
        readme[:start_index]
        + "\n\n"
        + activity
        + "\n"
        + readme[end_index:]
    )

    with open("README.md", "w", encoding="utf-8") as file:
        file.write(new_readme)


if __name__ == "__main__":
    main()
