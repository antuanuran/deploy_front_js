import ultralytics
import cv2
import numpy as np
import ctypes
import logging

from init_conf import MODELS, POSE_EST, COLORS, DEVICE_FOR_NN, COMMON, LOGGING_LEVEL


logging.basicConfig(format="%(asctime)s|%(levelname)s|%(message)s", level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)


class ModelNN():
    def __init__(self, name_model):
      self.name_model = name_model
      self.weight_model = ultralytics.YOLO(MODELS[name_model].path, task=MODELS[self.name_model].task)
      self.colors_detect = self._gen_param_colors()

    def _gen_param_colors(self):
        colors_detect = {}
        for obj, color in MODELS[self.name_model].colors.items():
            colors_detect[obj] = tuple([COLORS[color][2], COLORS[color][1], COLORS[color][0]]) # RGB -> BGR
        return colors_detect

    @staticmethod
    def draw_rect_for_gst(numpy_frame: np.array, results_for_gst: ctypes, draw_rect_flag: int, height: int, width: int) -> np.array:
      fact_need_draw_red_rectangle = False
      for i in range(len(results_for_gst.cls)):
        if results_for_gst.cls[i] in COMMON.class_for_pass_round and not fact_need_draw_red_rectangle:
          fact_need_draw_red_rectangle = True
          numpy_frame = cv2.rectangle(numpy_frame, (0, 0), (width, height), [75, 25, 230], 30)
        if draw_rect_flag < 16 or COMMON.draw_results_detect_full:
          x1 = results_for_gst.x1[i]
          y1 = results_for_gst.y1[i]
          x2 = results_for_gst.x2[i]
          y2 = results_for_gst.y2[i]
          name_color = MODELS[results_for_gst.model[i]].colors[results_for_gst.cls[i]]
          color = tuple([COLORS[name_color][2], COLORS[name_color][1], COLORS[name_color][0]])
          numpy_frame = cv2.rectangle(numpy_frame, (x1, y1), (x2, y2), color, 3)
          if COMMON.draw_results_detect_full:
            text_on_image = f"{results_for_gst.cls[i].upper()}: {float(results_for_gst.conf[i]*100):.2f}%"
            (w, h), _ = cv2.getTextSize(text_on_image, cv2.FONT_HERSHEY_SIMPLEX,
                                        MODELS[results_for_gst.model[i]].high_text, 1)
            numpy_frame = cv2.rectangle(numpy_frame, (x1, y1), (x1 + w, y1 - h - 10), color, -1)
            numpy_frame = cv2.putText(numpy_frame, text_on_image, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX,
                            MODELS[results_for_gst.model[i]].high_text, (255,255,255), 1)
      return numpy_frame

    def detect(self, img: np.ndarray, conf, imgsz) -> np.ndarray:
      result = self.weight_model(
                          img,
                          conf=conf,
                          imgsz=imgsz,
                          verbose=False,
                          classes=MODELS[self.name_model].classes,
                          device=DEVICE_FOR_NN)
      return result


class ModelYOLO(ModelNN):
  pass

class ModelPoseYOLO(ModelNN):
  def prepare_images_with_crop_peoples(self, cam_img_matching: dict[str], conf: float, imgsz: int) -> tuple[np.ndarray, dict, dict]:
    result = self.detect(cam_img_matching['img'], conf=conf, imgsz=imgsz)
    batch_images_peoples = {}
    relative_coord = {}
    x1 = {}
    y1 = {}
    x2 = {}
    y2 = {}
    for i in range(len(result)):
      id_camera = cam_img_matching['cam'][i]
      for coor_people in result[i].boxes.xyxy.cpu():
        x1[id_camera] = int(coor_people.tolist()[0])
        y1[id_camera] = int(coor_people.tolist()[1])
        x2[id_camera] = int(coor_people.tolist()[2])
        y2[id_camera] = int(coor_people.tolist()[3])
        if id_camera not in batch_images_peoples.keys():
          batch_images_peoples[id_camera] = []
          relative_coord[id_camera] = []
        batch_images_peoples[id_camera].append(cam_img_matching['img'][i][y1[id_camera]:y2[id_camera], x1[id_camera]:x2[id_camera]])
        relative_coord[id_camera].append([x1[id_camera], y1[id_camera], x2[id_camera], y2[id_camera]])
    return result, batch_images_peoples, relative_coord

  @staticmethod
  def draw_keypoints_for_gst(numpy_frame: np.array, results_for_gst: ctypes) -> np.array:
    for i in range(int(len(results_for_gst.confsk)/17)):
        for j in range(17):
            if float(results_for_gst.confsk[17*i+j]) > MODELS[results_for_gst.modelsk[i]].conf_keypoints:
                _, class_keypoint = list(POSE_EST.order_keypoints.items())[j][1]
                cv2.circle(
                        numpy_frame,
                        [results_for_gst.xsk[17*i+j], results_for_gst.ysk[17*i+j]],
                        MODELS[results_for_gst.modelsk[i]].size_points,
                        [COLORS[MODELS[results_for_gst.modelsk[i]].colors[class_keypoint]][k] for k in [2, 1, 0]],
                        -1,
                        lineType=cv2.LINE_AA
                        )

        for (first_point_name, second_point_name, class_limb) in POSE_EST.order_limbs:
            first_point_number = POSE_EST.order_keypoints[first_point_name][0]
            second_point_number = POSE_EST.order_keypoints[second_point_name][0]
            if float(results_for_gst.confsk[17*i+first_point_number]) > MODELS[results_for_gst.modelsk[i]].conf_keypoints and \
                        float(results_for_gst.confsk[17*i+second_point_number]) > MODELS[results_for_gst.modelsk[i]].conf_keypoints:
                cv2.line(
                        numpy_frame,
                        [results_for_gst.xsk[17*i+first_point_number], results_for_gst.ysk[17*i+first_point_number]],
                        [results_for_gst.xsk[17*i+second_point_number], results_for_gst.ysk[17*i+second_point_number]],
                        [COLORS[MODELS[results_for_gst.modelsk[i]].colors[class_limb]][k] for k in [2, 1, 0]],
                        thickness=1,
                        lineType=cv2.LINE_AA
                        )
    return numpy_frame
