FROM python:3.13.1-bookworm AS base

RUN apt update

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY backend.py backend.py
# !: production version should run WSGI server
CMD ["python3", "backend.py"]
