import pika
import datetime
import logging
import numpy as np
import multiprocessing
import pickle
import json
import xml.etree.ElementTree as ET

from init_conf import CAMERAS, MODELS, HOSTNAME, PORT, CONNECTION_PARAMETERS, COMMON
from preprocess import ping_server, init_models
from utils import forming_descriptions_detection, forming_descriptions_keypoints


## @brief get results of detect nn
#  @param current_img current images as dict[str]
#  @param return_results_for_gst result to Gst (shared memory) as dict[str]
#  @param return_result_for_rabbit result to MQrabbit (shared memory) as multiprocessing.Queue
#  @param pts_current_img timestamp of images as dict[str]
#  @return None
def work_models(
        current_img: dict[str],
        return_results_for_gst: dict[str],
        return_result_for_rabbit: multiprocessing.Queue,
        pts_current_img: dict[str],
) -> None:
    models, model_skeleton = init_models()
    get_pts_current_img = {id_camera: 0 for id_camera in COMMON.cameras_in_work}

    while True:
        message_from_all_cameras = {}
        copy_current_img = current_img
        cam_img_matching = {}
        cam_img_matching['img'] = []
        cam_img_matching['cam'] = []
        for id_camera in COMMON.cameras_in_work:
            if isinstance(copy_current_img[id_camera], np.ndarray):
                if get_pts_current_img[id_camera] != pts_current_img[id_camera]:
                    # forming results work of nn
                    cam_img_matching['img'].append(copy_current_img[id_camera])
                    cam_img_matching['cam'].append(id_camera)
                    get_pts_current_img[id_camera] = pts_current_img[id_camera]
                    message = {}
                    message["img"] = copy_current_img[id_camera]
                    message["meta"] = {}
                    message["meta"]["location_description"] = CAMERAS[id_camera].location_description
                    message["meta"]["shape"] = copy_current_img[id_camera].shape
                    message["meta"]["time"] = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).isoformat("T") + "Z"
                    message["meta"]["descriptions"] = {}
                    message["meta"]["descriptions"]["detection"] = []
                    message["meta"]["descriptions"]["keypoints"] = []
                    message_from_all_cameras[id_camera] = message
                    logging.info(" %s | work_models | pts of current image %s \n " % (id_camera, get_pts_current_img[id_camera]))

        if len(message_from_all_cameras.keys()) != 0:
            
            # use skeletom model
            cam_img_matching_process_model = {}
            cam_img_matching_process_model['cam'] = [name_cam for name_cam in cam_img_matching['cam'] if "skeleton" in CAMERAS[name_cam].models or 
                                                        len(list(set(CAMERAS[name_cam].models) & set(model_skeleton))) != 0]
            cam_img_matching_process_model['img'] = [img for number, img in enumerate(cam_img_matching['img']) 
                                                        if cam_img_matching['cam'][number] in cam_img_matching_process_model['cam']]
            if len(cam_img_matching_process_model['cam']) != 0:
                logging.info(" all | work_models | post images in model_pose_yolo skeleton")
                result, batch_images_peoples, relative_coord = models["skeleton"].prepare_images_with_crop_peoples(
                                                                                    cam_img_matching_process_model,
                                                                                    conf=MODELS["skeleton"].conf,
                                                                                    imgsz=MODELS["skeleton"].imgsz
                                                                                    )
                for i in range(len(result)):
                    logging.info(
                        " %s | work_models | model found object: %s" % (cam_img_matching_process_model['cam'][i], result[i].boxes.xyxy.nelement())
                    )
                    if result[i].boxes.xyxy.nelement() != 0:
                        descriptions = forming_descriptions_detection(result[i])
                        message_from_all_cameras[cam_img_matching_process_model['cam'][i]]["meta"]["descriptions"]["detection"].extend(descriptions)
                    if result[i].keypoints.xy.nelement() != 0:
                        descriptions = forming_descriptions_keypoints(result[i])
                        message_from_all_cameras[cam_img_matching_process_model['cam'][i]]["meta"]["descriptions"]["keypoints"].extend(descriptions)

            # use another model
            for model in CAMERAS[id_camera].models:
                match MODELS[model].type:
                    case "model_yolo":
                        cam_img_matching_process_model = {}
                        cam_img_matching_process_model['cam'] = [name_cam for name_cam in cam_img_matching['cam'] if model in CAMERAS[name_cam].models]
                        cam_img_matching_process_model['img'] = [img for number, img in enumerate(cam_img_matching['img']) 
                                                                    if cam_img_matching['cam'][number] in cam_img_matching_process_model['cam']]
                        if len(cam_img_matching_process_model['cam']) != 0:
                            logging.info(" all | work_models | post images in model_yolo %s" % (model))
                            result = models[model].detect(
                                cam_img_matching_process_model['img'], conf=MODELS[model].conf, imgsz=MODELS[model].imgsz
                            )
                            for i in range(len(result)):
                                logging.info(" %s | work_models | model found object: %s" % (cam_img_matching_process_model['cam'][i], result[i].boxes.xyxy.nelement()))
                                if result[i].boxes.xyxy.nelement() != 0:
                                    descriptions = forming_descriptions_detection(result[i])
                                    message_from_all_cameras[cam_img_matching_process_model['cam'][i]]["meta"]["descriptions"]["detection"].extend(descriptions)
                    case "need_skeleton":
                        cam_img_matching_process_model = {}
                        cam_img_matching_process_model['cam'] = [name_cam for name_cam in cam_img_matching['cam'] if model in CAMERAS[name_cam].models]
                        for id_camera in cam_img_matching_process_model['cam']:
                            logging.info(" all | work_models | post images in need_skeleton %s" % (model))
                            if id_camera in batch_images_peoples.keys():
                                if len(batch_images_peoples[id_camera]) != 0:
                                    result = models[model].detect(
                                                                batch_images_peoples[id_camera],
                                                                conf=MODELS[model].conf,
                                                                imgsz=MODELS[model].imgsz,
                                                                )
                                    for i in range(len(result)):
                                        logging.info(
                                            " %s | work_models | model found object: %s"
                                            % (id_camera, result[i].boxes.xyxy.nelement())
                                        )
                                        if result[i].boxes.xyxy.nelement() != 0:
                                            descriptions = forming_descriptions_detection(
                                                result[i],
                                                relative_coord[id_camera][i],
                                            )
                                            message_from_all_cameras[id_camera]["meta"]["descriptions"]["detection"].extend(
                                                descriptions
                                            )
            logging.info(
                " all | work_models | get result work of models"
            )

            # post results in MQrabbit
            logging.info("work_models: result for post in MQrabbit")
            return_result_for_rabbit.put(message_from_all_cameras)

            # post results in Gst
            for id_camera in message_from_all_cameras.keys():
                results_for_gst = {}
                for name_parameter in [
                    "time",
                    "model",
                    "cls",
                    "conf",
                    "x1",
                    "y1",
                    "x2",
                    "y2",
                    "xsk",
                    "ysk",
                    "confsk",
                    "modelsk",
                ]:
                    results_for_gst[name_parameter] = []
                results_for_gst["time"] = message_from_all_cameras[id_camera]["meta"]["time"]
                for i in range(len(message_from_all_cameras[id_camera]["meta"]["descriptions"]["detection"])):
                    results_for_gst["cls"].append(
                        message_from_all_cameras[id_camera]["meta"]["descriptions"]["detection"][i]["cls"]
                    )
                    results_for_gst["conf"].append(
                        message_from_all_cameras[id_camera]["meta"]["descriptions"]["detection"][i]["conf"]
                    )
                    results_for_gst["x1"].append(
                        message_from_all_cameras[id_camera]["meta"]["descriptions"]["detection"][i]["bbox"][0]
                    )
                    results_for_gst["y1"].append(
                        message_from_all_cameras[id_camera]["meta"]["descriptions"]["detection"][i]["bbox"][1]
                    )
                    results_for_gst["x2"].append(
                        message_from_all_cameras[id_camera]["meta"]["descriptions"]["detection"][i]["bbox"][2]
                    )
                    results_for_gst["y2"].append(
                        message_from_all_cameras[id_camera]["meta"]["descriptions"]["detection"][i]["bbox"][3]
                    )
                    results_for_gst["model"].append(
                        message_from_all_cameras[id_camera]["meta"]["descriptions"]["detection"][i]["model"]
                    )
                for i in range(len(message_from_all_cameras[id_camera]["meta"]["descriptions"]["keypoints"])):
                    for j in range(17):
                        results_for_gst["xsk"].append(
                            message_from_all_cameras[id_camera]["meta"]["descriptions"]["keypoints"][i]["description"][
                                j
                            ]["xy"][0]
                        )
                        results_for_gst["ysk"].append(
                            message_from_all_cameras[id_camera]["meta"]["descriptions"]["keypoints"][i]["description"][
                                j
                            ]["xy"][1]
                        )
                        results_for_gst["confsk"].append(
                            message_from_all_cameras[id_camera]["meta"]["descriptions"]["keypoints"][i]["description"][
                                j
                            ]["conf"]
                        )
                        results_for_gst["modelsk"].append("skeleton")
                return_results_for_gst[id_camera] = results_for_gst
            logging.info(" all | work_models | result for gst: %s" % (return_results_for_gst))


## @brief post results in MQrabbit
#  @param results_from_work_models result to MQrabbit (shared memory) from nn as multiprocessing.Queue
#  @return None
def post_data_in_rabbit(results_from_work_models: multiprocessing.Queue) -> None:
    while True:
        exist_service = ping_server(HOSTNAME, PORT)
        if exist_service:
            break

    connection = pika.BlockingConnection(CONNECTION_PARAMETERS)
    channel = connection.channel()
    channel.exchange_declare(exchange='meta_data', exchange_type="direct", durable=True)
    channel.queue_declare(queue='meta_data', durable=True)
    channel.queue_bind(exchange='meta_data', queue='meta_data', routing_key='meta_data')
    logging.info(" all | post_data_in_rabbit | start post data in rabbit \n")

    while True:
            batch = []
            while not results_from_work_models.empty():
                logging.info(
                    " all | post_data_in_rabbit | lenght of queue : %s \n"
                    % (results_from_work_models.qsize())
                )
                message_to_rabbit = results_from_work_models.get()
                batch.append(message_to_rabbit)
                if results_from_work_models.qsize() < 5:
                    break
            if batch:
                channel.basic_publish(
                    exchange='meta_data',
                    routing_key='meta_data',
                    body=pickle.dumps({
                                'meta_list_all': batch
                                }
                    ),
                )


## @brief get result from MQrabbit
#  @param events_from_rabbit result from MQrabbit (shared memory) with event as multiprocessing.Queue
#  @return None
def get_data_from_rabbit_for_stream(events_for_stream: dict[list]):
    def callback_events(ch, method, properties, body):
        json_data = body.decode("utf-8")
        data = json.loads(json_data)
        events_for_stream[data["cam"]] += [data]
        logging.info(
            " %s | add_data_to_queue_for_stream | len queue: %s \n "
            % (data["cam"], len(events_for_stream[data["cam"]])))

    while True:
        exist_service = ping_server(HOSTNAME, PORT)
        if exist_service:
            break

    connection = pika.BlockingConnection(CONNECTION_PARAMETERS)
    channel = connection.channel()
    channel.queue_declare(queue='events_data', durable=True, arguments={'x-message-ttl': 600000})
    channel.basic_consume(queue='events_data', on_message_callback=callback_events, auto_ack=True)
    channel.start_consuming()
    logging.info(" all | get_events_from_rabbit | start get events from MQRabbit \n")