from datetime import datetime
import os
import logging
from PIL import Image
from lib_loader import check_status

LOGGING_LEVEL = logging.INFO
logging.basicConfig(format="%(asctime)s|%(levelname)s|%(message)s", level=LOGGING_LEVEL)
logging.getLogger("videoanalytics").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


def save_detection(frame, class_name, confidence, datetime_str, cam):
    datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    date = datetime_obj.strftime("%Y-%m-%d")
    dt = datetime_obj.strftime("%Y-%m-%d_%H:%M:%S")
    image_path = f"/app/data/images/{date}/{cam}/{class_name}/{dt}.jpeg"
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    image = Image.fromarray(frame, mode="RGB")
    image.save(image_path, format="JPEG")
    return image_path


TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def _action_was_a_long_time_ago(
    class_name: str,
    time_between_savings: dict,
    param_time: str,
    param_interval: str,
) -> bool:
    logger.info(f"Class {class_name} checks for interval, {param_time=}")
    last_action_time = time_between_savings[class_name].get(param_time)
    if last_action_time is None:
        last_action_time = datetime.now().strftime(TIME_FORMAT)
        time_between_savings[class_name][param_time] = last_action_time
    last_action_time_datetime = datetime.strptime(last_action_time, TIME_FORMAT)
    logger.info(f"Last detection datetime: {last_action_time_datetime}")
    current_time = datetime.now()
    logger.info(f"Current time: {current_time}")
    time_difference = current_time - last_action_time_datetime
    logger.info(f"Time difference: {time_difference}")

    status = check_status(
        time_difference.total_seconds(),
        time_between_savings[class_name][param_interval],
    )
    if status:
        logger.info(f"Action {param_time=} was a long time ago")
        time_between_savings[class_name][param_time] = current_time.strftime(
            TIME_FORMAT
        )
        return True
    else:
        logger.info(f"Action {param_time=} was not a long time ago")
        return False


def save_was_a_long_time_ago(class_name, time_between_savings):
    return _action_was_a_long_time_ago(
        class_name,
        time_between_savings,
        "last_save_time",
        "save_interval",
    )


def telegram_send_was_a_long_time_ago(class_name, time_between_savings):
    return _action_was_a_long_time_ago(
        class_name,
        time_between_savings,
        "last_telegram_send_time",
        "telegram_send_interval",
    )


def onvif_send_was_a_long_time_ago(class_name, time_between_savings):
    return _action_was_a_long_time_ago(
        class_name,
        time_between_savings,
        "last_onvif_send_time",
        "onvif_send_interval",
    )
