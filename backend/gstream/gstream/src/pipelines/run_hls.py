import gi
from threading import Thread
import logging
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
from init_conf import CAMERAS, COMMON, LOGGING_LEVEL

logging.basicConfig(format="%(asctime)s|%(levelname)s|%(message)s", level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

def start_pipeline_hls(id_camera):

    Gst.init(None)
    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(COMMON['level_debug'])

    cmd = f"""rtspsrc location={CAMERAS[id_camera].location_rtspsrc} ignore-x-server-reply=True \
latency=2000 debug=false drop-on-latency=false udp-buffer-size=524288 ! \
rtph264depay ! \
avdec_h264 lowres=2 skip-frame=5 ! \
videorate ! \
video/x-raw,framerate={CAMERAS[id_camera].framerate}/1 ! \
videoscale ! \
video/x-raw,width={CAMERAS[id_camera].video_width},height={CAMERAS[id_camera].video_height} ! \
videoconvert ! \
video/x-raw,format=BGR ! \
gstyolo id-camera="{CAMERAS[id_camera].name}" ! \
videoconvert ! \
x264enc tune=zerolatency pass=17 speed-preset=1 bitrate=1000 sliced-threads=true vbv-buf-capacity=600 ! \
mpegtsmux ! \
hlssink target-duration=1 max-files=5 playlist-location=/app/gstream/hls_streams/{CAMERAS[id_camera].name}/playlist.m3u8
location=/app/gstream/hls_streams/{CAMERAS[id_camera].name}/file%05d.ts
"""

    locals()[f"pipeline_{id_camera}"] = Gst.parse_launch(cmd)
    locals()[f"pipeline_{id_camera}"].set_state(Gst.State.PLAYING)
    main_loop = GLib.MainLoop()
    thread = Thread(target=main_loop.run)
    thread.start()
