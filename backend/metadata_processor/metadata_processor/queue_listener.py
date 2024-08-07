import functools
import os

import pika
import sys
import yaml
import logging
import json
from PIL import Image
import numpy as np
import utils
import datetime
import typing as ty
import cv2
import pickle


LOGGING_LEVEL = logging.INFO
logging.basicConfig(format="%(asctime)s|%(levelname)s|%(message)s", level=LOGGING_LEVEL)
logging.getLogger("videoanalytics").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

BASE_PATH = "/app/common_configs"


with open(os.path.join(BASE_PATH, "common.yaml"), "r") as file:
    config_common = yaml.safe_load(file)

with open(os.path.join(BASE_PATH, "cameras.yaml"), "r") as file:
    config_cameras = yaml.safe_load(file)

with open(os.path.join(BASE_PATH, "colors.yaml"), "r") as file:
    config_colors = yaml.safe_load(file)

with open(os.path.join(BASE_PATH, "models.yaml"), "r") as file:
    config_models = yaml.safe_load(file)

with open(os.path.join(BASE_PATH, "pose_est.yaml"), "r") as file:
    config_pose_est = yaml.safe_load(file)


def _gen_param_colors() -> dict:
    colors_detect = {}
    for camera in config_common["cameras_in_work"]:
        for model_group in config_cameras[camera]["models"]:
            for class_name, color in config_models[model_group]["colors"].items():
                # RGB -> BGR
                colors_detect[class_name] = tuple(
                    [
                        config_colors[color][2],
                        config_colors[color][1],
                        config_colors[color][0],
                    ]
                )
    return colors_detect


colors_store = _gen_param_colors()

# 1. Turned on the flags
telegram_works = config_common.get("telegram_works", False)
onvif_works = config_common.get("onvif_works", False)

logger.info(f"telegram_works: {telegram_works}, onvif_works: {onvif_works}")



# 2. Connection Parameters - pika
connection_params = pika.ConnectionParameters(
    host="rabbitmq",
    port=5672,
    virtual_host="/",
    credentials=pika.PlainCredentials(username="user", password="password"),
)

# 3. Setting up a connection
connection = pika.BlockingConnection(connection_params)

# 4. Creating a channel for working with RabbitMQ
channel = connection.channel()

# 5. We have created telegram, onvif queues
queue_meta_data = "meta_data"
queue_telegram = "telegram_message_queue"
queue_onvif = "onvif_message_queue"
queue_events_data = "events_data"

channel.queue_declare(queue=queue_meta_data, durable=True)
channel.queue_declare(queue=queue_telegram, durable=True)
channel.queue_declare(queue=queue_onvif, durable=True, arguments={"x-message-ttl": 3600000})
channel.queue_declare(queue=queue_events_data, durable=True, arguments={"x-message-ttl": 600000})

# 6. Time_between_savings
with open("../configs/time_between_savings.yaml", "r") as file:
    time_between_savings = yaml.safe_load(file)
    logger.info(f"time_between_savings config: {time_between_savings}")


# 11. Start process_event()
def process_event(
    event: dict, cam, get_image: ty.Callable[[], np.ndarray], data: dict
) -> None:
    class_name = event["cls"]
    if class_name not in time_between_savings:
        return

    if not utils.save_was_a_long_time_ago(
        class_name=class_name, time_between_savings=time_between_savings
    ):
        return

    confidence = event["conf"]
    description = event["text"]
    analyzer = event["model"]
    datetime_str = data["meta"]["time"]
    cam = cam
    location_description = data["meta"]["location_description"]

    way_of_saving = utils.save_detection(
        frame=get_image(),
        class_name=class_name,
        confidence=confidence,
        datetime_str=datetime_str,
        cam=cam,
    )

    payload = {
        "way_of_saving": way_of_saving,
        "class_name": class_name,
        "confidence": confidence,
        "datetime": datetime_str,
        "cam": cam,
        "location_description": location_description,
        "description": description,
        "analyzer": analyzer,
    }

    body = json.dumps(payload).encode("utf-8")
    logger.info("\n----> Created payload \n")

    if telegram_works:
        if not utils.telegram_send_was_a_long_time_ago(
            class_name, time_between_savings
        ):
            return

        channel.basic_publish(
            exchange="",
            routing_key=queue_telegram,
            body=body,
        )
        logger.info("\n\n---->  Created Telegram_message_queue\n")

    if onvif_works:
        if not utils.onvif_send_was_a_long_time_ago(class_name, time_between_savings):
            return

        channel.basic_publish(
            exchange="",
            routing_key=queue_onvif,
            body=body,
        )
        channel.basic_publish(
            exchange="",
            routing_key=queue_events_data,
            body=body,
        )
        logger.info("\n\n----> Created Onvif_message_queue!\n")


# drawing rectangle
def draw_rect(
    img: np.ndarray,
    class_name: str,
    conf: float,
    bbox: tuple[int, int, int, int],
    model: str,
) -> np.ndarray:
    text_on_image = f"{class_name.upper()}: {float(conf * 100):.2f}%"
    color = colors_store[class_name]
    x1, y1, x2, y2 = bbox
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    (w, h), _ = cv2.getTextSize(
        text_on_image, cv2.FONT_HERSHEY_SIMPLEX, config_models[model]["high_text"], 1
    )
    img = cv2.rectangle(img, (x1, y1), (x1 + w, y1 - h - 10), color, -1)

    r, g, b = color
    if r + b + g <= 350:
        img = cv2.putText(img, text_on_image, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, config_models[model]["high_text"], (255, 255, 255), 1)
    else:
        img = cv2.putText(img, text_on_image, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, config_models[model]["high_text"], (0, 0, 0), 1)
    return img


# drawing keypoints
def draw_keypoints(
    img: np.ndarray,
    model_group: str,
    keypoints: list[dict],
) -> np.ndarray:
    for keypoint in keypoints:
        if float(keypoint["conf"]) > config_models[model_group]["conf_keypoints"]:
            _, class_keypoint = config_pose_est["order_keypoints"][keypoint["cls"]]
            cv2.circle(
                img,
                keypoint["xy"],
                config_models[model_group]["size_points"],
                colors_store[class_keypoint],
                -1,
                lineType=cv2.LINE_AA,
            )

    for first_point_name, second_point_name, class_limb in config_pose_est[
        "order_limbs"
    ]:
        first_point_number = int(
            config_pose_est["order_keypoints"][first_point_name][0]
        )
        second_point_number = int(
            config_pose_est["order_keypoints"][second_point_name][0]
        )
        if (
            float(keypoints[first_point_number]["conf"])
            > config_models[model_group]["conf_keypoints"]
            and float(keypoints[second_point_number]["conf"])
            > config_models[model_group]["conf_keypoints"]
        ):
            cv2.line(
                img,
                keypoints[first_point_number]["xy"],
                keypoints[second_point_number]["xy"],
                colors_store[class_limb],
                thickness=1,
                lineType=cv2.LINE_AA,
            )

    return img


# 10. Start process_raw_message() -> switched to process_event()
def process_raw_message(data: dict, cam) -> None:
    @functools.cache
    def prepare_image() -> np.ndarray:
        image = data[cam]["img"]

        for event in data[cam]["meta"]["descriptions"]["detection"]:
            image = draw_rect(
                image, event["cls"], event["conf"], event["bbox"], event["model"]
            )

        for event in data[cam]["meta"]["descriptions"]["keypoints"]:
            image = draw_keypoints(image, "skeleton", event["description"])

        return image[:, :, ::-1]

    for event in data[cam]["meta"]["descriptions"]["detection"]:
        try:
            process_event(event, cam, prepare_image, data[cam])
        except Exception as ex:
            logger.exception(ex)


# 9. Start callback() -> switched to process_raw_message()
def callback(ch, method, properties, body):
    data_all = pickle.loads(body)

    for raw_message in data_all["meta_list_all"]:
        try:
            for key in raw_message:
                process_raw_message(raw_message, key)
        except Exception as ex:
            logger.exception(ex)


# 7. Subscribed to the queue -> switched to callback()
channel.basic_consume(queue=queue_meta_data, on_message_callback=callback, auto_ack=True)

# 8. We started consuming
logger.info("Waiting for messages on configured queues. To exit press CTRL+C")
channel.start_consuming()