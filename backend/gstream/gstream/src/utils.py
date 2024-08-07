import numpy as np
import cv2
import multiprocessing
import json

from init_conf import TEXTS, POSE_EST


def forming_descriptions_detection(result, relative_coord = None):
    descriptions = []
    for i in range(len(result.boxes.xyxy)):
        x1, y1, x2, y2 = map(int, result.boxes.xyxy[i].tolist())
        description = {}
        description["cls"] = result.names[int(result.boxes.cls[i])]
        description["conf"] = round(float(result.boxes.conf[i]), 2)
        if relative_coord is None:
            description["bbox"] = [x1, y1, x2, y2]
        else:
            description["bbox"] = [
                            x1+relative_coord[0],
                            y1+relative_coord[1],
                            x2+relative_coord[0],
                            y2+relative_coord[1]
                            ]
        description["text"] = TEXTS[description["cls"]].text
        description["model"] = TEXTS[description["cls"]].model
        descriptions.append(description)
    return descriptions


def forming_descriptions_keypoints(result):
    descriptions = []
    for i in range(len(result.boxes.xyxy)):
        description = {}
        description["id"] = i
        description["description"] = []
        for j in range(17):
            keypoint = {}
            class_keypoint = list(POSE_EST.order_keypoints.keys())[j]
            keypoint["cls"] = class_keypoint
            x, y = map(int, result.keypoints.xy[i][j].cpu().tolist())
            keypoint["xy"] = [x, y]
            keypoint["conf"] = round(float(result.keypoints.conf[i][j]), 2)
            description["description"].append(keypoint)
        descriptions.append(description)
    return descriptions


def change_current_img_between_miltiprocess(numpy_frame_p, parameters_p, convert=True) -> np.array:
        current_img_prepair = np.ctypeslib.as_array(
                                                numpy_frame_p,
                                                shape=(
                                                     parameters_p.height,
                                                     parameters_p.width,
                                                     4
                                                     )
                                                )
        if convert:
            current_img_prepair = cv2.cvtColor(current_img_prepair, cv2.COLOR_BGRA2BGR)
        return current_img_prepair


def control_alive_process(process, function, args: tuple):
    if not process.is_alive():
        process.terminate()
        process = multiprocessing.Process(
                                    target=function,
                                    args=(*args, )
                                    )
        process.start()