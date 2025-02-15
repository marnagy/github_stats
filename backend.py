import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import json
from dataclasses import dataclass
import io
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

import requests
from flask import Flask

# ENV vars
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REPOSITORIES = os.getenv("REPOSITORIES").split('|')
MAX_REPOS = int(os.getenv("MAX_REPOSITORIES_AMOUNT", 5)) 
UPDATE_FREQUENCY = int(os.getenv("LATENCY_MINUTES", 60))
assert len(REPOSITORIES) <= MAX_REPOS
MAX_DAYS = int(os.getenv("MAX_DAYS", 7)) 
MAX_WINDOW_SIZE = int(os.getenv("MAX_WINDOW_SIZE", 500)) 

# constants
TYPE_KEY = "type"
DT_KEY = "created_at"
DATA_FOLDER_NAME = "data"
CURRENT_REPOS_FILE_NAME = "current_repos.json"
BASE_API_URL = "https://api.github.com/repos"

@dataclass(frozen=True, eq=True, kw_only=True)
class OwnerRepoPair:
    owner: str
    repo: str

def get_rolling_window_results(arr: list[datetime], max_window_size: int, max_days: int):
    results = list()

    acc: list[timedelta] = list()
    #arr = list(map(datetime.fromisoformat, master_dict["yt-dlp"]["WatchEvent"]))

    # initial step
    left_index = 0
    right_index = 0

    # initial fill
    while right_index < len(arr) and len(acc) < max_window_size and (len(acc) == 0 or arr[right_index] - acc[0] < timedelta(days=max_days)):
        acc.append(arr[right_index])
        right_index += 1

    differences = [ dt2-dt1 for dt1, dt2 in zip(acc, acc[1:])] if len(acc) > 1 else []
    if len(differences) != 0:
        result = sum(differences, timedelta(minutes=0)) / len(differences)
        results.append(result)

    # step
    while right_index < len(arr):
        # do step
        left_index += 1
        del acc[0]
        if len(acc) == 0:
            # repeat initial fill [step between values is bigger than max_days]
            while right_index < len(arr) and len(acc) < max_window_size and (len(acc) == 0 or arr[right_index] - acc[0] < timedelta(days=max_days)):
                acc.append(arr[right_index])
                right_index += 1

        while right_index < len(arr) and len(acc) < max_window_size and (len(acc) > 0 and arr[right_index] - acc[0] < timedelta(days=max_days)):
            acc.append(arr[right_index])
            right_index += 1

        # average difference
        differences = [ dt2-dt1 for dt1, dt2 in zip(acc, acc[1:])] if len(acc) > 1 else []
        if len(differences) != 0:
            result = sum(differences, timedelta(minutes=0)) / len(differences)
            results.append(result)
    return results


if not os.path.exists(DATA_FOLDER_NAME) or not os.path.isdir(DATA_FOLDER_NAME):
    os.mkdir(DATA_FOLDER_NAME)

app = Flask(__name__)

@app.get("/test")
def test_endpoint():
    return {"server": "running"}


@app.get("/stats")
def get_stats():
    master_dict = defaultdict(lambda: defaultdict(lambda: list()))
    results = defaultdict(lambda: defaultdict(lambda: list()))
    owner_repo_pairs = [
        OwnerRepoPair(owner=repo_url.split('/')[-2], repo=repo_url.split('/')[-1])
        for repo_url in REPOSITORIES
    ]
    # logger.info(owner_repo_pairs)
    ## download events from GitHub API
    for pair_obj in owner_repo_pairs:
        try:
            with open(os.path.join(DATA_FOLDER_NAME, f"{pair_obj.owner}-{pair_obj.repo}_last_update.txt"), "w", encoding="utf-8") as f:
                last_update = datetime.fromisoformat(f.readline().strip('\n'))
                if last_update + timedelta(minutes=UPDATE_FREQUENCY) < datetime.now(timezone.utc):
                    raise Exception("Time to update.")
                else:
                    logger.info("Loading from JSON")
                    with open(os.path.join(DATA_FOLDER_NAME, f"{pair_obj.owner}-{pair_obj.repo}_data.json"), "w", encoding="utf-8") as f:
                        master_dict[pair_obj.repo] = json.load(f)
        except:
            logger.info(f"Loading data for {pair_obj.owner}/{pair_obj.repo} from API")
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
            
            with open(os.path.join(DATA_FOLDER_NAME, f"{pair_obj.owner}-{pair_obj.repo}_last_update.txt"), "w", encoding="utf-8") as f:
                print(datetime.now().isoformat(), file=f)
            with open(os.path.join(DATA_FOLDER_NAME, f"{pair_obj.owner}-{pair_obj.repo}_data.json"), "w", encoding="utf-8") as f:
                print(json.dumps(
                    {
                        key: list(map(str, master_dict[pair_obj.repo]))
                        for key in master_dict[pair_obj.repo].keys()
                    }
                ), file=f)

        for repo in master_dict.keys():
            for event_type in master_dict[repo].keys():
                logger.info(f"Solving for {repo} - {event_type}")
                master_dict[repo][event_type].sort()
                ### custom rolling window ###
                window_differences: list[timedelta] = get_rolling_window_results(
                    master_dict[repo][event_type],
                    max_window_size=MAX_WINDOW_SIZE,
                    max_days=MAX_DAYS
                )
                window_differences = [ diff.seconds for diff in window_differences]
                results[repo][event_type] = window_differences

    return dict(results)


# DEV
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)