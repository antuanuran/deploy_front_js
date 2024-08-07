import datetime
from hydra import compose, initialize
import pika

initialize(version_base=None, config_path="../", job_name="app")

MEDIA_TYPE = "application/soap+xml; charset=utf-8"
HEADERS = {
    "Server": "gSOAP/2.8E",
    "Connection": "close",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "X-Content-Type-Options": "nosniff",
    "Strict-Transport-Security": "max-age=63072000; includeSubdomains;",
    "Date": datetime.datetime.utcnow().isoformat("T") + "Z",
}
PATH_TAG = compose(config_name="configs/path_tag").configs
COMMON = compose(config_name="configs_common/gstream").configs_common
CAMERAS = compose(config_name="configs_common/cameras").configs_common

HOSTNAME = "rabbitmq"
PORT = 5672
CONNECTION_PARAMETERS = pika.ConnectionParameters(
    host=HOSTNAME,
    port=PORT,
    virtual_host="/",
    credentials=pika.PlainCredentials(username="user", password="password"),
)

URI = {}
for video_source in list(COMMON.cameras_in_work):
    URI[video_source] = f"rtsp://{COMMON.ip_server}:{CAMERAS[video_source].port}/{video_source}"
