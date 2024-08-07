FROM python:3.11-slim

RUN apt update \
    && apt install -y cron ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/data/images

WORKDIR /app

COPY requirements/requirements.txt /app/requirements/requirements.txt

RUN pip install --no-cache-dir -r requirements/requirements.txt

COPY . /app/
COPY cleaner_cron /etc/cron.d/
RUN chmod +x entrypoint.sh && chmod +x cleaner.sh

WORKDIR /app/metadata_processor

CMD ["bash", "-c", "../entrypoint.sh"]
