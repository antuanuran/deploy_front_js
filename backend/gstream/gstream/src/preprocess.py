import socket
import shutil
import os

from pathlib import Path

from init_conf import CAMERAS, COMMON, MODELS
from class_models import ModelYOLO, ModelPoseYOLO


def ping_server(server: str, port: int, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, port))
    except OSError as error:
        return False
    else:
        s.close()
        return True


def create_hls(camera):
    path_core = Path('/app/gstream/hls_streams')
    os.makedirs(os.path.join(path_core, CAMERAS[camera].name), exist_ok=True)
    shutil.copyfile('/app/templates/hls.html', path_core / CAMERAS[camera].name / 'hls.html')
    shutil.copyfile('/app/templates/video-js.css', path_core / CAMERAS[camera].name / 'video-js.css')
    shutil.copyfile('/app/templates/video.min.js', path_core / CAMERAS[camera].name / 'video.min.js')
    with open (path_core / CAMERAS[camera].name / 'hls.html', 'r') as f:
        data = f.read()
        data = data.replace('test',
                            CAMERAS[camera].name)
        data = data.replace('width="640" height="360"',
                            f""" width="{CAMERAS[camera].hlssink_width}" height="{CAMERAS[camera].hlssink_height}" """)
    with open (path_core / CAMERAS[camera].name / 'hls.html', 'w') as f:
        f.write(data)


def init_models():
    models = {}
    model_skeleton = []
    for camera in COMMON.cameras_in_work:
        for model in CAMERAS[camera].models:
            if model not in models.keys():
                match MODELS[model].type:
                    case "model_yolo":
                        models[model] = ModelYOLO(model)
                    case "model_pose_yolo":
                        if 'skeleton' not in models.keys():
                            models[model] = ModelPoseYOLO(model)
                    case "need_skeleton":
                        models[model] = ModelYOLO(model)
                        if 'skeleton' not in models.keys():
                            models['skeleton'] = ModelPoseYOLO('skeleton')
                        model_skeleton.append(model)
    return models, model_skeleton


def init_destr_camera_on_ports():
    ports_distr_camera = {}
    for camera in COMMON.cameras_in_work:
        if CAMERAS[camera].port not in list(ports_distr_camera.keys()):
            ports_distr_camera[CAMERAS[camera].port] = []
        ports_distr_camera[CAMERAS[camera].port].append(camera)
    return ports_distr_camera
