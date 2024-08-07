import gi
from threading import Thread
import logging
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
from init_conf import COMMON, LOGGING_LEVEL, CAMERAS

logging.basicConfig(format="%(asctime)s|%(levelname)s|%(message)s", level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

def start_pipeline_test(id_camera):

    Gst.init(None)
    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(COMMON['level_debug'])

    if CAMERAS[id_camera].user_id != 'None' and CAMERAS[id_camera].user_pw != 'None':
        parameters_user_for_rtspsrc = f'user-id={CAMERAS[id_camera].user_id} user-pw={CAMERAS[id_camera].user_pw}'
    else:
        parameters_user_for_rtspsrc=''

    cmd = f"""
rtspsrc location={CAMERAS[id_camera].location_rtspsrc} \
{parameters_user_for_rtspsrc} ! \
rtph264depay !  \
avdec_h264 !  \
decodebin ! \
videoconvert ! \
autovideosink sync=true
"""

    pipeline_test = Gst.parse_launch(cmd)
    pipeline_test.set_state(Gst.State.PLAYING)
    main_loop = GLib.MainLoop()
    thread = Thread(target=main_loop.run)
    thread.start()
    logging.info(" test | connect_to_rtsp_server | consumer rtsp start \n ")
