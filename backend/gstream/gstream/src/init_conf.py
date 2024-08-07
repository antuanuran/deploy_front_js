from hydra import compose, initialize
import pika
import logging
import torch

initialize(version_base=None, config_path="../../configs", job_name="app")

CAMERAS = compose(config_name="cameras")
COMMON = compose(config_name="gstream")
MODELS = compose(config_name="models")
POSE_EST = compose(config_name="pose_est")
COLORS = compose(config_name="colors")
TEXTS = compose(config_name="texts")
HOSTNAME = 'rabbitmq'
PORT = 5672
FPS = 2
CONNECTION_PARAMETERS = pika.ConnectionParameters(
    host=HOSTNAME,
    port=PORT,
    virtual_host='/',
    credentials=pika.PlainCredentials(
        username='user',
        password='password'
    )
)

if COMMON.logging_level == "ERROR":
    LOGGING_LEVEL = logging.ERROR
elif COMMON.logging_level == "INFO":
    LOGGING_LEVEL = logging.INFO

if COMMON.device == 'cpu':
    DEVICE = 'cpu'
    DEVICE_FOR_NN = 'cpu'
if COMMON.device == 'cuda':
    DEVICE = 'cuda'
    DEVICE_FOR_NN = torch.cuda.get_device_name(torch.cuda.current_device())
if COMMON.device == 'auto':
    if torch.cuda.is_available():
        DEVICE = 'cuda'
        DEVICE_FOR_NN = torch.cuda.get_device_name(torch.cuda.current_device())
    else:
        DEVICE = 'cpu'
        DEVICE_FOR_NN = 'cpu'