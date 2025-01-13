import os
from collections import defaultdict
from datetime import datetime, timedelta
import json
from dataclasses import dataclass

import requests
from flask import Flask

# ENV vars
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REPOSITORIES = os.getenv("REPOSITORIES").split('|')
MAX_REPOS = int(os.getenv("MAX_REPOSITORIES_AMOUNT", 5)) 

# constants
TYPE_KEY = "type"
DT_KEY = "created_at"
BASE_API_URL = "https://api.github.com/repos"

@dataclass(frozen=True, eq=True, kw_only=True)
class OwnerRepoPair:
    owner: str
    repo: str

app = Flask(__name__)

@app.get("/test")
def test_endpoint():
    return {"server": "running"}

@app.get("/<owner>/<repo>")
def get_stats():
    master_dict = defaultdict(lambda: defaultdict(lambda: list()))
    owner_repo_pairs = [
        OwnerRepoPair(owner=repo_url.split('/')[-2], repo=repo_url.split('/')[-1])
        for repo_url in REPOSITORIES.split('|')
    ]
    print(owner_repo_pairs)
    # for 
    # https://api.github.com/repos/marnagy/gift_lister/events
    for pair_obj in owner_repo_pairs:
        resp = requests.get(
            f"{BASE_API_URL}/{pair_obj.owner}/{pair_obj.repo}/events",
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Authorization": f"Bearer {ACCESS_TOKEN}"
            }
        )
        resp_dict = resp.json()
        for obj in resp_dict:
            master_dict[pair_obj.repo][obj[TYPE_KEY]].append(
                datetime.fromisoformat(obj[DT_KEY])
            )

        for repo in master_dict.keys():
            for event_type in master_dict[repo].keys():
                master_dict[repo][event_type].sort()

# DEV
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)