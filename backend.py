import os
from collections import defaultdict
from datetime import datetime, timedelta
import json
from dataclasses import dataclass

from flask import Flask


ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REPOSITORIES = os.getenv("REPOSITORIES").split('|')
MAX_REPOS = int(os.getenv("MAX_REPOSITORIES_AMOUNT", 5)) 

@dataclass(frozen=True, eq=True, kw_only=True)
class OwnerRepoPair:
    owner: str
    repo: str

app = Flask(__name__)

@app.get("/test")
def test_endpoint():
    return {"server": "running"}

@app.get("/<owner>/<repo>")
def get_stats(owner: str, repo: str):
    return f"{owner} ### {repo}"

# DEV
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)