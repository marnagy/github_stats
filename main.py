import sqlite3
import requests
# import flask
from collections import defaultdict
from datetime import datetime, timedelta
import os
from dataclasses import dataclass

from pprint import pprint

BASE_API_URL = "https://api.github.com/repos"

def load_env() -> dict[str, str]:
    return {
        # URLs separated by |
        "repositories": os.getenv("REPOSITORIES"),
        "access_token": os.getenv("ACCESS_TOKEN")
    }

@dataclass(frozen=True, eq=True, kw_only=True)
class OwnerRepoPair:
    owner: str
    repo: str

TYPE_KEY = "type"
DT_KEY = "created_at"

# keys: [repo_name][type]
master_dict = defaultdict(lambda: defaultdict(lambda: list()))

# def main():
env_dict = load_env()
owner_repo_pairs = [
    OwnerRepoPair(owner=repo_url.split('/')[-2], repo=repo_url.split('/')[-1])
    for repo_url in env_dict["repositories"].split('|')
]
pprint(owner_repo_pairs)
# for 
# https://api.github.com/repos/marnagy/gift_lister/events
for pair_obj in owner_repo_pairs:
    resp = requests.get(
        f"{BASE_API_URL}/{pair_obj.owner}/{pair_obj.repo}/events",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Bearer {env_dict['access_token']}"
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

a = 5

    #-H "Accept: application/vnd.github+json" \
#    -H "X-GitHub-Api-Version: 2022-11-28" \
#    -H "Authorization: Bearer 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"

# if __name__ == '__main__':
#     main()