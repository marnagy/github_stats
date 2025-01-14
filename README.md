# GitHub Stats API

The main script for running the REST API is in file `backend.py`.

This script loads events of a GitHub repository and saves them to lower the amount of calls to the API.

### Another possible approach

We could have a cron job that retrieves data periodically and saves them, but this approach is more suitable for more frequently used APIs which I don't think this is. Also there's a limit on the amount of calls to the Github's API.

## .env file

### Required ENV variables

- `ACCESS_TOKEN` - set to GitHub access token
- `REPOSITORIES` - list of repositories to get events about. URLs are separated by `|`

### Optional ENV variables
- `MAX_REPOSITORIES_AMOUNT` - convenience env variable (default: 5)
- `LATENCY_MINUTES` - minimum time that needs to go by so that the REST API actually uses the GitHub's API again (explanation: the API has latency 30s-6h, so I chose the default value 60 min as reasonable compromise)
- `MAX_DAYS` - maximum amount of days to include in the rolling window (default: 7)
- `MAX_WINDOW_SIZE` - maximum size of the rolling window (default: 500)

## How to run (dev version)

### with docker and docker-compose

1. Create folder `data` inside the repository folder
2. Run `docker-compose up`

### locally

1. Create virtual environment (`virtualenv .venc`) and activate it
2. Install modules (`pip3 install -r requirements.txt`)
3. Create `.env` file (more in the section <b>.env file</b>)
4. Run `python3 backend.py`

## How to use

Test endpoint to check if the API is running: `http://[REST API's IP address]:8000/test`

When running `http://[REST API's IP address]:8000/stats` you receive the stats about the repositories in the ENV variable `REPOSITORIES` in <b>seconds</b>.

## Response JSON structure

```json
{
    repo_name1: {
        event_name1: [
            <values from the rolling window in seconds>
        ],
        event_name2: [
            <values from the rolling window in seconds>
        ]
    },
    repo_name2:{
        ...
    }
}

```

------------

## Possible improvements

1. Use database instead of a folder to persist data

This was not implemented since it take a comparatively long time to implement. This would yield faster response time.

2. Use suitable library like `pandas` or `numpy` to compute the rolling window

This was not used since I was not able to find a solution that would use these modules.

3. Use of asynchronous API calling to speed up retrieval of the data

This approach yields faster response time the more repositories you want to monitor.
