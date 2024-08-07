FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY requirements/requirements.txt /app/requirements/requirements.txt

RUN pip install --no-cache-dir -r requirements/requirements.txt

COPY . /app

WORKDIR /app

RUN mkdir -p configs_common

RUN mkdir -p snapshot

CMD ["python3", "src/main.py"]