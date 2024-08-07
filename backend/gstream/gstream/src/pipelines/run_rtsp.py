import ctypes
import datetime
import logging
import multiprocessing
import xml.etree.ElementTree as ET
import cv2

import gi
import numpy as np

gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from threading import Thread

import gst_utils
from class_models import ModelNN, ModelPoseYOLO
from gi.repository import GLib, Gst, GstRtspServer
from init_conf import CAMERAS, COMMON, DEVICE, FPS, LOGGING_LEVEL, MODELS, POSE_EST
from parprocess import post_data_in_rabbit, work_models, get_data_from_rabbit_for_stream
from utils import change_current_img_between_miltiprocess

logging.basicConfig(format="%(asctime)s|%(levelname)s|%(message)s", level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)


def on_message(bus, message, loop):
    t = message.type
    if str(message.src)[:13] == '<Gst.Pipeline':
        logging.info( " all | on_message | id pipeline: %s \n " % (message.src.get_name()))
    if t == Gst.MessageType.STATE_CHANGED:
        if str(message.src)[:13] == '<Gst.Pipeline':
            old_state, new_state, pending_state = message.parse_state_changed()
            logging.info(
                " %s | on_message | old state: %s \n "
                % (message.src.get_name(), old_state)
            )
            logging.info(
                " %s | on_message | new state: %s \n "
                % (message.src.get_name(), new_state)
            )
            if str(new_state) == '<enum GST_STATE_NULL of type Gst.State>':
                logging.info(
                    " %s | on_message | remake pipeline \n "
                    % (message.src.get_name())
                )
                message.src.set_state(Gst.State.PLAYING)
    if t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        logging.info(
                " %s | on_message | error: %s \n "
                % (message.src.get_name(), err)
            )
        logging.info(
                " %s | on_message | debug: %s \n "
                % (message.src.get_name(), debug)
            )
        message.src.set_state(Gst.State.NULL)
        message.src.set_state(Gst.State.PLAYING)
    return True


def convert_gst_buffer_to_ndarray(buffer: Gst.Buffer, pad) -> np.array:
    success, map_info = buffer.map(Gst.MapFlags.WRITE)
    caps_struct = pad.get_current_caps().get_structure(0)
    height = caps_struct.get_int("height")
    width = caps_struct.get_int("width")
    if not success:
        raise RuntimeError("Could not map buffer data!")
    numpy_frame = np.ndarray(
        shape=(height.value, width.value, 4),
        dtype=np.uint8,
        buffer=map_info.data,
    )
    buffer.unmap(map_info)
    return numpy_frame, height.value, width.value

def prepare_video_stream(pad, info):
        with gst_utils.GST_PAD_PROBE_INFO_BUFFER(info) as buffer:
            id_camera = pad.get_parent_element().get_name()[9:]
            numpy_frame, height, width = convert_gst_buffer_to_ndarray(
                buffer, pad
            )
            logging.info(
                " %s | prepare_video_stream | current pts %s \n "
                % (id_camera, buffer.pts)
            )
            numpy_frame_for_nn = np.copy(numpy_frame)
            numpy_frame_for_nn = numpy_frame_for_nn.astype(np.uint8)
            globals()[f"parameters_p_{id_camera}"].height = height
            globals()[f"parameters_p_{id_camera}"].width = width
            globals()[
                f"numpy_frame_p_{id_camera}"
            ] = numpy_frame_for_nn.ctypes.data_as(
                globals()[f"c_uint_p_{id_camera}"]
            )
            globals()[f"parameters_p_{id_camera}"].pts = buffer.pts
            globals()[f"parameters_p_{id_camera}"].draw_rect_flag += 1
            globals()[f"parameters_p_for_clients_{id_camera}"].height = height
            globals()[f"parameters_p_for_clients_{id_camera}"].width = width
            globals()[f"numpy_frame_p_for clients_{id_camera}"] = globals()[f"numpy_frame_p_{id_camera}"]
            if COMMON.draw_results_detect_full or COMMON.draw_results_detect:
                if f"results_for_gst_{id_camera}" in globals():
                    if len(globals()[f"results_for_gst_{id_camera}"].cls) != 0:
                        numpy_frame = ModelNN.draw_rect_for_gst(
                            numpy_frame,
                            globals()[f"results_for_gst_{id_camera}"],
                            globals()[f"parameters_p_{id_camera}"].draw_rect_flag,
                            height,
                            width
                        )
                    if (
                        COMMON.draw_results_detect_full
                        and len(
                            globals()[f"results_for_gst_{id_camera}"].confsk
                        )
                        != 0
                    ):
                        numpy_frame = ModelPoseYOLO.draw_keypoints_for_gst(
                            numpy_frame,
                            globals()[f"results_for_gst_{id_camera}"],
                        )
                    numpy_frame_for_clients = np.copy(numpy_frame)
                    numpy_frame_for_clients = numpy_frame_for_clients.astype(np.uint8)
                    globals()[
                        f"numpy_frame_p_for clients_{id_camera}"
                    ] = numpy_frame_for_clients.ctypes.data_as(
                        globals()[f"c_uint_p_{id_camera}"]
                        )
            if globals()[f"parameters_p_{id_camera}"].draw_rect_flag > 64:
                globals()[f"parameters_p_{id_camera}"].draw_rect_flag = 0
        return Gst.PadProbeReturn.OK


def start_connection_to_cam(port, cameras):
    Gst.init(None)
    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(COMMON["level_debug"])
    cmd_run = {}
    cmd_server = {}

    for id_camera in cameras:
        if (
            CAMERAS[id_camera].user_id != "None"
            and CAMERAS[id_camera].user_pw != "None"
        ):
            parameters_user_for_rtspsrc = f"user-id={CAMERAS[id_camera].user_id} user-pw={CAMERAS[id_camera].user_pw}"
        else:
            parameters_user_for_rtspsrc = ""
        if DEVICE == "cuda":
            cmd_run[
                id_camera
            ] = f"""
rtspsrc location={CAMERAS[id_camera].location_rtspsrc} debug=true {parameters_user_for_rtspsrc} latency=0 buffer-mode=4 ! \
rtph264depay ! \
h264parse ! \
nvh264dec ! \
videorate ! \
video/x-raw,framerate=16/1 ! \
videoconvert ! \
video/x-raw,format=BGRA ! \
fakesink name=fakesink_{id_camera}
"""
            cmd_server[id_camera] = f"""
appsrc name=rtsp_{id_camera} max-latency=0 min-latency=-1 ! \
nvh264enc ! \
rtph264pay name=pay0 pt=96 \
appsrc name=meta_{id_camera} ! \
rtponvifmetadatapay name=pay1 pt=127
"""
        if DEVICE == "cpu":
            cmd_run[
                id_camera
            ] = f"""
rtspsrc location={CAMERAS[id_camera].location_rtspsrc} debug=true {parameters_user_for_rtspsrc} latency=0 buffer-mode=4 ! \
rtph264depay ! \
h264parse ! \
avdec_h264 ! \
videorate ! \
video/x-raw,framerate=16/1 ! \
videoconvert ! \
video/x-raw,format=BGRA ! \
fakesink name=fakesink_{id_camera}
"""
            cmd_server[id_camera] = f"""
appsrc name=rtsp_{id_camera} max-latency=0 min-latency=-1 ! \
videoconvert ! \
video/x-raw,format=I420 ! \
x264enc tune=zerolatency pass=17 ! \
rtph264pay name=pay0 pt=96 \
appsrc name=meta_{id_camera} ! \
rtponvifmetadatapay name=pay1 pt=127
"""

    logging.info(" %s \n " % (cmd_run))
    logging.info(" %s \n " % (cmd_server))
    global name_pipeline
    name_pipeline = {}

    for id_camera in cameras:
        globals()[f"parameters_p_{id_camera}"] = gst_utils.GstLastImageParam()
        globals()[f"parameters_p_for_clients_{id_camera}"] = gst_utils.GstLastImageParam()
        globals()[f"c_uint_p_{id_camera}"] = ctypes.POINTER(ctypes.c_uint8)
        globals()[f"parameters_p_{id_camera}"].draw_rect_flag = 0
        globals()[f"pipe_conn_to_cam_{id_camera}"] = Gst.parse_launch(cmd_run[id_camera])
        elem_fakesink = globals()[f"pipe_conn_to_cam_{id_camera}"].get_by_name(f'fakesink_{id_camera}')
        pad_fakesink = elem_fakesink.get_static_pad("sink")
        pad_fakesink.add_probe(
            Gst.PadProbeType.BUFFER, prepare_video_stream
        )
        globals()[f"pipe_conn_to_cam_{id_camera}"].set_state(Gst.State.PLAYING)
        globals()[f"bus_{id_camera}"] = globals()[f"pipe_conn_to_cam_{id_camera}"].get_bus()
        globals()[f"bus_{id_camera}"].add_signal_watch()
        name_pipeline[globals()[f"pipe_conn_to_cam_{id_camera}"].get_name()] = id_camera
        main_loop = GLib.MainLoop()
        globals()[f"bus_{id_camera}"].connect("message", on_message, main_loop)
        thread = Thread(target=main_loop.run)
        thread.start()
    logging.info(" all | start_connection_to_cam | depends of pipeline name and gst.pipeline name: %s \n " % (name_pipeline))


    class ExtendedBin(Gst.Bin):
        def do_handle_message(self, message):
            t = message.type
            if t == Gst.MessageType.STATE_CHANGED:
                if str(message.src)[:17] == '<__gi__.GstAppSrc':
                    old_state, new_state, pending_state = message.parse_state_changed()
                    logging.info(
                        " %s | do_handle_message | old state: %s \n "
                        % (message.src.get_name(), old_state)
                    )
                    logging.info(
                        " %s | do_handle_message | new state: %s \n "
                        % (message.src.get_name(), new_state)
                    )
                    id_client = repr(message.src)
                    id_client = id_client[(id_client.find("GstAppSrc at ") + 13) : -2]
                    if str(new_state) == '<enum GST_STATE_NULL of type Gst.State>':
                        id_camera = message.src.get_name()[5:]
                        if message.src.get_name()[:4] == 'rtsp':
                            clients_to_del_in_rtsp[id_camera].append(id_client)
                            logging.info(
                                " %s | do_handle_message | clients for delete: %s \n "
                                % (id_camera, clients_to_del_in_rtsp[id_camera])
                            )
                        if message.src.get_name()[:4] == 'meta':
                            clients_to_del_in_meta[id_camera].append(id_client)
                            logging.info(
                                " %s | do_handle_message | clients for delete: %s \n "
                                % (id_camera, clients_to_del_in_meta[id_camera])
                            )
            if t == Gst.MessageType.ERROR:
                error, debug = message.parse_error()
                logging.error(
                    " %s | do_handle_message | error: %s \n "
                    % (message.src.get_name(), error.message)
                )
                if debug:
                    logging.info(
                        " %s | do_handle_message | debug info: %s \n "
                    % (message.src.get_name(), debug)
                    )
            Gst.Bin.do_handle_message(self, message)

    class RTSPMediaFactoryCustom(GstRtspServer.RTSPMediaFactory):
        def __init__(self, cmd_server, id_camera):
            GstRtspServer.RTSPMediaFactory.__init__(self)
            self.cmd_server = cmd_server
            self.id_camera = id_camera
            self.fps_rtsp = 16
            self.fps_meta = FPS
            self.number_frames_rtsp = {}
            self.number_frames_meta = {}
            self.duration_rtsp = 1 / self.fps_rtsp * Gst.SECOND
            self.duration_meta = 1 / self.fps_meta * Gst.SECOND

        def on_need_data_meta(self, src, length):
            id_client = repr(src)
            id_client = id_client[(id_client.find("GstAppSrc at ") + 13) : -2]
            while len(clients_to_del_in_meta[self.id_camera]) != 0 and 'clients_to_del_in_meta' in globals():
                id = clients_to_del_in_meta[self.id_camera].pop()
                exist_key = self.number_frames_meta.pop(id, 'nothing')
                if exist_key == 'nothing':
                    logging.error(
                        " %s | on_need_data_meta | error delette client: %s "
                        % (self.id_camera, id)
                        )
                    logging.error(self.number_frames_meta)
            self.number_frames_meta[id_client]["time_request"] = datetime.datetime.now()
            metadata_buf_list = Gst.BufferList.new()

            metadata_buf = Gst.Buffer.new_wrapped(self._get_xml_message())
            metadata_buf.duration = self.duration_meta
            timestamp = self.number_frames_meta[id_client]["number_frame"] * self.duration_meta
            metadata_buf.pts = metadata_buf.dts = int(timestamp)
            metadata_buf.offset = timestamp
            metadata_buf_list.insert(-1, metadata_buf)

            if len(self.number_frames_meta[id_client]["events"]) != 0:
                events_buf = Gst.Buffer.new_wrapped(self._get_xml_events(id_client))
                events_buf.duration = self.duration_meta
                timestamp = self.number_frames_meta[id_client]["number_frame"] * self.duration_meta
                events_buf.pts = events_buf.dts = int(timestamp)
                events_buf.offset = timestamp
                metadata_buf_list.insert(-1, events_buf)

            self.number_frames_meta[id_client]["number_frame"] += 1
            retval = src.emit("push-buffer-list", metadata_buf_list)
            logging.info(
                " %s | on_need_data_meta | id clients with time_request %s \n "
                % (self.id_camera, self.number_frames_meta)
            )
            logging.info(
                " %s | on_need_data_meta | quantity of clients  %s \n "
                % (self.id_camera, len(self.number_frames_meta.keys()))
            )
            logging.info(
                " %s | on_need_data_meta | quantity of events for client with id %s: %s \n "
                % (self.id_camera, id_client, len(self.number_frames_meta[id_client]["events"]))
            )
            if retval != Gst.FlowReturn.OK:
                logging.error(
                    " %s | on_need_data_meta |error pushing metadata buffer: %s "
                    % (self.id_camera, retval)
                )

        def do_create_element(self, url):
            self.server_parse_rtsp = Gst.parse_launch(self.cmd_server)
            extendedBin = ExtendedBin("extendedBin")
            extendedBin.add(self.server_parse_rtsp)
            self.extendedPipeline = Gst.Pipeline.new("extendedPipeline")
            self.extendedPipeline.add(extendedBin)
            return self.extendedPipeline

        def do_configure(self, rtsp_media):
            rtsp_src = rtsp_media.get_element().get_by_name(f"rtsp_{self.id_camera}")
            rtsp_caps = Gst.caps_from_string(
                f"video/x-raw,format=BGRA,width={CAMERAS[self.id_camera].video_width},height={CAMERAS[self.id_camera].video_height},framerate=16/1"
            )
            rtsp_src.set_property("format", Gst.Format.TIME)
            rtsp_src.set_property("block", True)
            rtsp_src.set_property("caps", rtsp_caps)
            rtsp_src.connect("need-data", self.on_need_data_rtsp)
            metadata_src = rtsp_media.get_element().get_by_name(f"meta_{self.id_camera}")
            metadata_caps = Gst.caps_from_string(
                f"application/x-onvif-metadata,framerate={FPS}/1"
            )
            metadata_src.set_property("format", Gst.Format.TIME)
            metadata_src.set_property("block", True)
            metadata_src.set_property("caps", metadata_caps)
            metadata_src.connect("need-data", self.on_need_data_meta)
            self._prepare_list_of_clients(rtsp_src, metadata_src)

        def _prepare_list_of_clients(self, rtsp_src, metadata_src):
            id_client_r = repr(rtsp_src)
            id_client_m = repr(metadata_src)
            id_client_r = id_client_r[(id_client_r.find("GstAppSrc at ") + 13) : -2]
            id_client_m = id_client_m[(id_client_m.find("GstAppSrc at ") + 13) : -2]
            if id_client_r not in self.number_frames_rtsp:
                logging.info(
                    " %s | _prepare_list_of_clients | new client for rtsp stream %s \n "
                    % (self.id_camera, id_client_r)
                    )
                current_time = datetime.datetime.now()
                self.number_frames_rtsp[id_client_r] = {}
                self.number_frames_rtsp[id_client_r]["number_frame"] = 0
                self.number_frames_rtsp[id_client_r]["time_request"] = current_time
                # check exist client for rtsp
                client_to_del = []
                for id in self.number_frames_rtsp:
                    diff_time_sec = int((current_time - self.number_frames_rtsp[id]["time_request"]).total_seconds())
                    if diff_time_sec > COMMON.time_live_client:
                        client_to_del.append(id)
                for id in client_to_del:
                    self.number_frames_rtsp.pop(id, None)
                    logging.info(
                        " %s | _prepare_list_of_clients | delete client for rtsp %s \n "
                        % (self.id_camera, id)
                    )
            if id_client_m not in self.number_frames_meta:
                logging.info(
                    " %s | _prepare_list_of_clients | new client for meta stream %s \n "
                    % (self.id_camera, id_client_m)
                    )
                current_time = datetime.datetime.now()
                self.number_frames_meta[id_client_m] = {}
                self.number_frames_meta[id_client_m]["number_frame"] = 0
                self.number_frames_meta[id_client_m]["time_request"] = current_time
                self.number_frames_meta[id_client_m]["events"] = []
                # check exist client for meta stream
                client_to_del = []
                for id in self.number_frames_meta:
                    diff_time_sec = int((current_time - self.number_frames_meta[id]["time_request"]).total_seconds())
                    if diff_time_sec > COMMON.time_live_client:
                        client_to_del.append(id)
                for id in client_to_del:
                    self.number_frames_meta.pop(id, None)
                    logging.info(
                        " %s | _prepare_list_of_clients | delete client for meta stream %s \n "
                        % (self.id_camera, id)
                    )

        def on_need_data_rtsp(self, src, length):
            id_client = repr(src)
            id_client = id_client[(id_client.find("GstAppSrc at ") + 13) : -2]
            while len(clients_to_del_in_rtsp[self.id_camera]) != 0 and 'clients_to_del_in_rtsp' in globals():
                id = clients_to_del_in_rtsp[self.id_camera].pop()
                exist_key = self.number_frames_rtsp.pop(id, 'nothing')
                if exist_key == 'nothing':
                    logging.error(
                        " %s | on_need_data_rtsp | error delette client: %s "
                        % (self.id_camera, id)
                        )
            self.number_frames_rtsp[id_client]["time_request"] = datetime.datetime.now()
            frame = change_current_img_between_miltiprocess(
                globals()[f"numpy_frame_p_for clients_{self.id_camera}"],
                globals()[f"parameters_p_for_clients_{self.id_camera}"],
                False
            )
            frame = cv2.resize(frame, (CAMERAS[self.id_camera].video_width, CAMERAS[self.id_camera].video_height), \
                interpolation = cv2.INTER_LINEAR)
            data = frame.tobytes()
            rtsp_buf = Gst.Buffer.new_allocate(None, len(data), None)
            rtsp_buf.fill(0, data)
            rtsp_buf.duration = self.duration_rtsp
            timestamp = self.number_frames_rtsp[id_client]["number_frame"] * self.duration_rtsp
            rtsp_buf.pts = rtsp_buf.dts = int(timestamp)
            rtsp_buf.offset = timestamp
            self.number_frames_rtsp[id_client]["number_frame"] += 1
            retval = src.emit("push-buffer", rtsp_buf)
            logging.info(
                " %s | on_need_data_rtsp | id clients with time_request %s \n "
                % (self.id_camera, self.number_frames_rtsp)
            )
            logging.info(
                " %s | on_need_data_rtsp | quantity of clients %s \n "
                % (self.id_camera, len(self.number_frames_rtsp.keys()))
            )
            if retval != Gst.FlowReturn.OK:
                logging.error(
                    " %s | on_need_data_rtsp |error pushing metadata buffer: %s "
                    % (self.id_camera, retval)
                )

        def _get_xml_message(self):
            metadata_stream = ET.Element(
                "tt:MetadataStream",
                attrib={
                    "xmlns:tt": "http://www.onvif.org/ver10/schema",
                    "xmlns:fc": "http://www.onvif.org/ver20/analytics/humanface",
                    "xmlns:bd": "http://www.onvif.org/ver20/analytics/humanbody",
                    "xmlns:acme": "http://www.acme.com/schema",
                },
            )
            if f"results_for_gst_{self.id_camera}" in globals():
                if len(globals()[f"results_for_gst_{self.id_camera}"].cls) != 0:
                    video_analytics = ET.SubElement(metadata_stream, "tt:VideoAnalytics")
                    frame = ET.SubElement(
                        video_analytics,
                        "tt:Frame",
                        {"UtcTime": globals()[f"results_for_gst_{self.id_camera}"].time},
                        )
                    for i in range(
                        len(globals()[f"results_for_gst_{self.id_camera}"].cls)
                        ):
                        object = ET.SubElement(frame, "tt:Object", {"ObjectId": str(i)})
                        appearance = ET.SubElement(object, "tt:Appearance")
                        shape = ET.SubElement(appearance, "tt:Shape")
                        ET.SubElement(
                            shape,
                            "tt:BoundingBox",
                            {
                                "x1": str(
                                    globals()[f"results_for_gst_{self.id_camera}"].x1[i]
                                ),
                                "y1": str(
                                    globals()[f"results_for_gst_{self.id_camera}"].y1[i]
                                ),
                                "x2": str(
                                    globals()[f"results_for_gst_{self.id_camera}"].x2[i]
                                ),
                                "y2": str(
                                    globals()[f"results_for_gst_{self.id_camera}"].y2[i]
                                ),
                            },
                        )
                        class_obj = ET.SubElement(appearance, "tt:Class")
                        type = ET.SubElement(
                            class_obj,
                            "tt:Type",
                            {
                                "Likelihood": f"{float(globals()[f'results_for_gst_{self.id_camera}'].conf[i]*100):.2f}"
                            },
                        )
                        type.text = str(
                            globals()[f"results_for_gst_{self.id_camera}"].cls[i]
                        )
                        if (
                            len(globals()[f"results_for_gst_{self.id_camera}"].confsk)
                            != 0
                        ):
                            for i in range(
                                int(
                                    len(
                                        globals()[
                                            f"results_for_gst_{self.id_camera}"
                                        ].confsk
                                    )
                                    / 17
                                )
                            ):
                                for j in range(17):
                                    if (
                                        float(
                                            globals()[
                                                f"results_for_gst_{self.id_camera}"
                                            ].confsk[17 * i + j]
                                        )
                                        > MODELS[
                                            globals()[
                                                f"results_for_gst_{self.id_camera}"
                                            ].modelsk[i]
                                        ].conf_keypoints
                                    ):
                                        ET.SubElement(
                                            shape,
                                            "tt:BoundingBox",
                                            {
                                                "xsk": str(
                                                    globals()[
                                                        f"results_for_gst_{self.id_camera}"
                                                    ].xsk[17 * i + j]
                                                ),
                                                "ysk": str(
                                                    globals()[
                                                        f"results_for_gst_{self.id_camera}"
                                                    ].ysk[17 * i + j]
                                                ),
                                            },
                                        )
                                        type = ET.SubElement(
                                            class_obj,
                                            "tt:Type",
                                            {
                                                "Likelihood": f"{float(globals()[f'results_for_gst_{self.id_camera}'].confsk[17*i+j]*100):.2f}"
                                            },
                                        )
                                        type.text = list(
                                            POSE_EST.order_keypoints.items()
                                        )[j][0]
            soap_response = ET.tostring(metadata_stream, encoding="utf-8")
            return soap_response

        ## @brief forming result for stream
        #  @param events: result for rtsp as dict
        #  @return None
        def _get_xml_events(self, id_client):
            if len(self.number_frames_meta[id_client]['events']) != 0:
                metadata_stream = ET.Element(
                    "tt:MetadataStream",
                    attrib={
                        "xmlns:SOAP-ENV": "http://www.w3.org/2003/05/soap-envelope",
                        "xmlns:wsa5": "http://www.w3.org/2005/08/addressing",
                        "xmlns:tt": "http://www.onvif.org/ver10/schema",
                        "xmlns:wsnt": "http://docs.oasis-open.org/wsn/b-2",
                        "xmlns:tev": "http://www.onvif.org/ver10/events/wsdl",
                        "xmlns:tns1": "http://www.onvif.org/ver10/topics",
                        "xmlns:tnsvendor": "http://www.vendor.com/2009/event/topics",
                        },
                    )
                event = ET.SubElement(metadata_stream, "tt:Event")
                events_for_xml = []
                while len(self.number_frames_meta[id_client]['events']) != 0:
                    events_for_xml.append(self.number_frames_meta[id_client]['events'].pop())
                if len(events_for_xml) != 0:
                    for event_for_xml in events_for_xml:
                        notification_message = ET.SubElement(event, "wsnt:NotificationMessage")
                        topic = ET.SubElement(notification_message, "wsnt:Topic", {"Dialect": "http://docs.oasis-open.org/wsn/t1/TopicExpression/Simple"})
                        topic.text = event_for_xml["description"]
                        wsnt_message = ET.SubElement(notification_message, "wsnt:Message")
                        tt_message = ET.SubElement(wsnt_message, "tt:Message", {"UtcTime": event_for_xml["datetime"], "PropertyOperation": "Changed"})
                        source = ET.SubElement(tt_message, "tt:Source")
                        simple_item = ET.SubElement(source, "tt:SimpleItem", {"Name": "camera_name", "Value": event_for_xml["cam"]})
                        key = ET.SubElement(tt_message, "tt:Key")
                        data = ET.SubElement(tt_message, "tt:Data")
                        simple_item = ET.SubElement(data, "tt:SimpleItem", {"Name": "class_name", "Value": event_for_xml["class_name"]})
                        simple_item = ET.SubElement(data, "tt:SimpleItem", {"Name": "camera_location", "Value": event_for_xml["location_description"]})
                        simple_item = ET.SubElement(data, "tt:SimpleItem", {"Name": "model_confidence", "Value": str(event_for_xml["confidence"])})
                soap_response = ET.tostring(metadata_stream, encoding="utf-8")
                return soap_response


    class GstreamerRtspServer(GstRtspServer.RTSPServer):
        def __init__(self):
            global factory
            factory = {}
            self.server = GstRtspServer.RTSPServer()
            self.server.props.service = str(port)
            for id_camera in cameras:
                factory[id_camera] = RTSPMediaFactoryCustom(cmd_server[id_camera],
                                                            id_camera)
                factory[id_camera].set_shared(True)
                mount_point = f"/{id_camera}"
                self.server.get_mount_points().add_factory(
                    mount_point, factory[id_camera]
                )
                logging.info(
                    " %s | start_pipeline | server URL : rtsp://%s:%s%s \n "
                    % (id_camera, COMMON.ip_server, port, mount_point)
                )
            self.server.attach(None)

    rtsp_server = GstreamerRtspServer()
    main_loop = GLib.MainLoop()
    thread = Thread(target=main_loop.run)
    thread.start()


    multiprocessing.set_start_method("spawn")
    manager = multiprocessing.Manager()
    message_to_rabbit = multiprocessing.Queue()
    current_img_from_all_cameras = manager.dict(
        {id_camera: 0 for id_camera in COMMON.cameras_in_work}
    )
    pts_current_img_from_all_cameras = manager.dict(
        {id_camera: 0 for id_camera in COMMON.cameras_in_work}
    )
    results_from_all_cameras = manager.dict(
        {id_camera: [] for id_camera in COMMON.cameras_in_work}
    )
    process_post_data_in_rabbit = multiprocessing.Process(
        target=post_data_in_rabbit, args=(message_to_rabbit,)
    )
    process_post_data_in_rabbit.start()
    process_work_models = multiprocessing.Process(
        target=work_models,
        args=(
            current_img_from_all_cameras,
            results_from_all_cameras,
            message_to_rabbit,
            pts_current_img_from_all_cameras,
        ),
    )
    process_work_models.start()
    events_for_stream = manager.dict(
        {id_camera: [] for id_camera in COMMON.cameras_in_work}
    )
    process_get_data_from_rabbit_for_stream = multiprocessing.Process(
        target=get_data_from_rabbit_for_stream,
        args=(events_for_stream,)
        )
    process_get_data_from_rabbit_for_stream.start()

    global clients_to_del_in_rtsp
    global clients_to_del_in_meta

    clients_to_del_in_rtsp = {id_camera: [] for id_camera in COMMON.cameras_in_work}
    clients_to_del_in_meta = {id_camera: [] for id_camera in COMMON.cameras_in_work}

    while True:
        for id_camera in cameras:
            if (
                f"numpy_frame_p_{id_camera}" in globals()
                and f"parameters_p_{id_camera}" in globals()
                and pts_current_img_from_all_cameras[id_camera]
                != globals()[f"parameters_p_{id_camera}"].pts
            ):
                current_img_from_all_cameras[
                    id_camera
                ] = change_current_img_between_miltiprocess(
                    globals()[f"numpy_frame_p_{id_camera}"],
                    globals()[f"parameters_p_{id_camera}"],
                )
                if len(results_from_all_cameras[id_camera]) != 0:
                    logging.info(
                        " %s | start_pipeline_rtsp | get result for Gst \n "
                        % (id_camera)
                    )
                    globals()[
                        f"results_for_gst_{id_camera}"
                    ] = gst_utils.create_ctypes_for_gst(
                        results_from_all_cameras[id_camera]
                    )
                pts_current_img_from_all_cameras[id_camera] = globals()[
                    f"parameters_p_{id_camera}"
                ].pts
                logging.info(
                    " %s | start_pipeline_rtsp | pts of current image %s \n "
                    % (id_camera, pts_current_img_from_all_cameras[id_camera])
                )
                logging.info(
                    " all | start_pipeline_rtsp | quantity of multiprocess: %s \n "
                    % ((len(multiprocessing.active_children())))
                )
            if len(events_for_stream[id_camera]) != 0:
                logging.info(
                    " %s | start_pipeline_rtsp | lenght queue in event stream: %s \n "
                    % (id_camera, len(events_for_stream[id_camera]))
                )
                events_for_clients = []
                while len(events_for_stream[id_camera]) != 0:
                    len_finish = len(events_for_stream[id_camera])
                    events_for_clients.extend(events_for_stream[id_camera][:len_finish])
                    events_for_stream[id_camera] = events_for_stream[id_camera][len_finish:]
                for id_client in factory[id_camera].number_frames_meta.keys():
                    factory[id_camera].number_frames_meta[id_client]['events'].extend(events_for_clients)
