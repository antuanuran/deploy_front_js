import logging
import json
import pika
from telegram import bot, chats_admin_ids
from datetime import datetime as dt
import os
import yaml

LOGGING_LEVEL = logging.INFO
logging.basicConfig(format="%(asctime)s|%(levelname)s|%(message)s", level=LOGGING_LEVEL)
logging.getLogger("videoanalytics").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

BASE_PATH = "/app/common_configs"

with open(os.path.join(BASE_PATH, "texts.yaml"), "r") as file:
    config_texts = yaml.safe_load(file)


def send_photo_to_telegram(body, chats_admin_ids):
    way_of_saving = body["way_of_saving"]
    class_name = body["class_name"]
    confidence = body["confidence"]
    datetime = dt.strptime(str(body["datetime"]), "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        microsecond=0
    )
    cam = body["cam"]
    location_description = body["location_description"]
    description = body.get("description", "-")
    analyzer = body["analyzer"]

    text_telegram = open(f"../templates/texts/{class_name}.html").read().strip()
    text_telegram = text_telegram.format(
        text_for_telegram=config_texts[class_name]["text_for_telegram"],
        camera_name=cam,
        camera_location=location_description,
        model_confidence=confidence,
        dt=datetime,
    )
    logger.info("Try to send notification")

    try:
        with open(way_of_saving, "rb") as photo:
            for chat_id in chats_admin_ids:
                photo.seek(0)
                bot.send_photo(
                    chat_id,
                    photo=photo,
                    caption=text_telegram,
                    parse_mode="html",
                    timeout=3,
                )
                logger.info(f"Send photo to {chat_id}")
    except Exception as e:
        logger.info(f"Failed to send photo to \nError: {e}")


# 0. Connection Parameters - pika
connection_params = pika.ConnectionParameters(
    host="rabbitmq",
    port=5672,
    virtual_host="/",
    credentials=pika.PlainCredentials(username="user", password="password"),
)

# 1. Setting up a connection
connection = pika.BlockingConnection(connection_params)

# 2. Creating a channel for working with RabbitMQ
channel = connection.channel()


# 5. Start callback()
def callback_tg(ch, method, properties, body):
    json_data = body.decode("utf-8")
    data = json.loads(json_data)
    send_photo_to_telegram(data, chats_admin_ids)


# 3. Subscribed to the queue -> switched to callback()
queue_telegram = "telegram_message_queue"
channel.queue_declare(queue=queue_telegram, durable=True)
channel.basic_consume(
    queue=queue_telegram, on_message_callback=callback_tg, auto_ack=True
)

# 4. We started consuming
channel.start_consuming()