# GitHub Stats API

The main script for running the REST API is in file `backend.py`.

## .env file

### Required ENV variables

- `ACCESS_TOKEN` - set to GitHub access token
- `REPOSITORIES` - list of repositories to get events about. URLs are separated by `|`

### Optional ENV variables
- `MAX_REPOSITORIES_AMOUNT` - convenience env variable
- `LATENCY_MINUTES` - minimum time that needs to go by so that the REST API actually uses the GitHub's API
- `MAX_DAYS` - maximum amount of days to include in the rolling window
- `MAX_WINDOW_SIZE` - maximum size of the rolling window

## How to run (dev version)

### with docker and docker-compose

1. Create folder `data` inside the repository folder
2. Run `docker-compose up`

### locally

1. Create virtual environment
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
            <values from the rolling window>
        ],
        event_name2: [
            <values from the rolling window>
        ]
    },
    repo_name2:{
        ...
    }
}

```

------------

## Possible improvements

1. Use database instead of a folder

This was not implemented since it take a comparatively long time to implement.

2. Use suitable library like `pandas` or `numpy` to compute the rolling window

This was not used since I wass not able to find a solution that would use these modules.

3. Use of asynchronous API calling to speed up retrieval of the data

This approach yields faster response time the more repositories you want to monitor.
