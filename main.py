import sqlite3
import requests
# import flask
from collections import defaultdict
from datetime import datetime, timedelta
import os
import json
from functools import reduce
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
load_json = False
if not load_json:
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
                #datetime.fromisoformat(
                    obj[DT_KEY]
                    #)
            )

        for repo in master_dict.keys():
            for event_type in master_dict[repo].keys():
                master_dict[repo][event_type].sort()
else:
    with open("example_resp.json", "r", encoding="utf-8") as input_f:
        master_dict = json.loads("\n".join(input_f.readlines()))
        

# rolling window with size 5
max_min = 2
max_amount = 3


acc = list()
arr = list(map(datetime.fromisoformat, master_dict["yt-dlp"]["WatchEvent"]))

# initial step
left_index = 0
right_index = 0

# initial fill
while len(acc) < max_amount and (len(acc) == 0 or arr[right_index] - acc[0] < timedelta(minutes=max_min)):
    acc.append(arr[right_index])
    right_index += 1

# print(acc)
# print(len(acc))
# print(acc[-1] - acc[0])
# average difference
differences = [ dt2-dt1 for dt1, dt2 in zip(acc, acc[1:])] if len(acc) > 1 else []
result = sum(differences, timedelta(minutes=0))
if len(differences) > 0:
    result = result / len(differences)
print(result)

# step
while right_index < len(arr):
    # do step
    left_index += 1
    del acc[0]
    if len(acc) == 0:
        # repeat initial fill
        while right_index < len(arr) and len(acc) < max_amount and (len(acc) == 0 or arr[right_index] - acc[0] < timedelta(minutes=max_min)):
            acc.append(arr[right_index])
            right_index += 1

    while right_index < len(arr) and len(acc) < max_amount and (len(acc) > 0 and arr[right_index] - acc[0] < timedelta(minutes=max_min)):
        acc.append(arr[right_index])
        right_index += 1

    # average difference
    differences = [ dt2-dt1 for dt1, dt2 in zip(acc, acc[1:])] if len(acc) > 1 else []
    result = sum(differences, timedelta(minutes=0))
    if len(differences) > 0:
        result = result / len(differences)
    print(result)
    
    # print(acc)
    # print(len(acc))
    # if len(acc) > 0:
    #     print(acc[-1] - acc[0])


a = 5

    #-H "Accept: application/vnd.github+json" \
#    -H "X-GitHub-Api-Version: 2022-11-28" \
#    -H "Authorization: Bearer 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"

# if __name__ == '__main__':
#     main()