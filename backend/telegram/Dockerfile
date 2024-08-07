FROM python:3.11-slim

RUN mkdir -p /app/data/images

WORKDIR /app

COPY requirements/requirements.txt /app/requirements/requirements.txt

RUN pip install --no-cache-dir -r requirements/requirements.txt

COPY . /app

WORKDIR /app/telegram

CMD ["/bin/sh", "-c", "sleep 15 && python tasks.py"]
