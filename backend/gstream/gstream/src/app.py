import multiprocessing
import logging

from pipelines.run_rtsp import start_connection_to_cam
from pipelines.run_hls import start_pipeline_hls
from preprocess import create_hls, init_destr_camera_on_ports
from pipelines.run_test import start_pipeline_test
from init_conf import COMMON, LOGGING_LEVEL


logging.basicConfig(format="%(asctime)s|%(levelname)s|%(message)s", level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    
    if COMMON.type_protocol == "rtsp_rts":
        dict_last_img = {}
        ports_distr_camera = init_destr_camera_on_ports()
        for port in list(ports_distr_camera.keys()):
            start_connection_to_cam(port, ports_distr_camera[port])

    elif COMMON.type_protocol == "hls":
        for id_camera in COMMON.cameras_in_work:
            create_hls(id_camera)
            multiprocessing.Process(target=start_pipeline_hls, args=(id_camera, )).start()

    elif COMMON.type_protocol == "test":
        start_pipeline_test(COMMON.cameras_in_work[0])
