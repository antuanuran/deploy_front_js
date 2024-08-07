import pickle
import numpy as np

import pika
import random
from datetime import datetime
import time

# 0. Параметры подключения pika
connection_params = pika.ConnectionParameters(
    host="localhost",
    port=5672,
    virtual_host="/",
    credentials=pika.PlainCredentials(username="user", password="password"),
)

# 1. Установка соединения. Используем библиотеку - pika в роли клиентской библиотеки
connection = pika.BlockingConnection(connection_params)

# 2. Создание канала для работы с RabbitMQ
channel = connection.channel()


# Отправляем сообщение
numb = 4
for i in range(numb):
    count = 1
    list_messages_to_rabbit = []

    for x in range(count):
        print(f" {x} - Время: {datetime.now()}")

        message_json = {
            "7": {
                            "img": (np.random.random((2160, 3840, 3)) * 255*0).astype(np.uint8),
                            "meta": {
                                "time": f"2024-06-25T13:01:32.{random.randint(100000, 999999)}Z",
                                "location_description": "Камера с воспроизведством видео",
                                "descriptions": {
                                    "detection": [
                                                             {'cls': 'person', 'conf': 0.93, 'bbox': [229, 715, 721, 1657], 'text': "tns1:VideoAnalytics/Skeleton/Person", 'model': 'skeleton'},
                                                             {'cls': 'gun', 'conf': 0.91, 'bbox': [1931, 309, 2500, 1644], 'text': "tns1:VideoAnalytics/Guns/Gun", 'model': 'guns'},
                                                             ],
                                    "keypoints": [
                                                            {'id': 0, 'description': [
                                                                                {'cls': 'nose', 'xy': [531, 892], 'conf': 0.99},
                                                                                {'cls': 'left_eye', 'xy': [560, 861], 'conf': 0.95},
                                                                                {'cls': 'right_eye', 'xy': [498, 857], 'conf': 0.98},
                                                                                {'cls': 'left_ear', 'xy': [591, 878], 'conf': 0.56},
                                                                                {'cls': 'right_ear', 'xy': [436, 868], 'conf': 0.91},
                                                                                {'cls': 'left_shoulder', 'xy': [626, 1077], 'conf': 0.97},
                                                                                {'cls': 'right_shoulder', 'xy': [351, 1062], 'conf': 0.99},
                                                                                {'cls': 'left_elbow', 'xy': [677, 1317], 'conf': 0.81},
                                                                                {'cls': 'right_elbow', 'xy': [282, 1304], 'conf': 0.96},
                                                                                {'cls': 'left_brush', 'xy': [676, 1524], 'conf': 0.69},
                                                                                {'cls': 'right_brush', 'xy': [325, 1534], 'conf': 0.9},
                                                                                {'cls': 'left_hip', 'xy': [582, 1575], 'conf': 0.72},
                                                                                {'cls': 'right_hip', 'xy': [392, 1571], 'conf': 0.83},
                                                                                {'cls': 'left_knee', 'xy': [0, 0], 'conf': 0.06},
                                                                                {'cls': 'right_knee', 'xy': [0, 0], 'conf': 0.1},
                                                                                {'cls': 'left_foot', 'xy': [0, 0], 'conf': 0.01},
                                                                                {'cls': 'right_foot', 'xy': [0, 0], 'conf': 0.01}]},
                                                            # {'id': 1, 'description': [
                                                            #                     {'cls': 'nose', 'xy': [2025, 552], 'conf': 0.88},
                                                            #                     {'cls': 'left_eye', 'xy': [2047, 505], 'conf': 0.94},
                                                            #                     {'cls': 'right_eye', 'xy': [0, 0], 'conf': 0.37},
                                                            #                     {'cls': 'left_ear', 'xy': [2168, 465], 'conf': 0.94},
                                                            #                     {'cls': 'right_ear', 'xy': [0, 0], 'conf': 0.07},
                                                            #                     {'cls': 'left_shoulder', 'xy': [2328, 616], 'conf': 0.97},
                                                            #                     {'cls': 'right_shoulder', 'xy': [2206, 690], 'conf': 0.72},
                                                            #                     {'cls': 'left_elbow', 'xy': [2500, 883], 'conf': 0.91},
                                                            #                     {'cls': 'right_elbow', 'xy': [0, 0], 'conf': 0.3},
                                                            #                     {'cls': 'left_brush', 'xy': [2356, 1105], 'conf': 0.8},
                                                            #                     {'cls': 'right_brush', 'xy': [0, 0], 'conf': 0.26},
                                                            #                     {'cls': 'left_hip', 'xy': [2406, 1325], 'conf': 0.79},
                                                            #                     {'cls': 'right_hip', 'xy': [2311, 1346], 'conf': 0.55},
                                                            #                     {'cls': 'left_knee', 'xy': [0, 0], 'conf': 0.09},
                                                            #                     {'cls': 'right_knee', 'xy': [0, 0], 'conf': 0.04},
                                                            #                     {'cls': 'left_foot', 'xy': [0, 0], 'conf': 0.01},
                                                            #                     {'cls': 'right_foot', 'xy': [0, 0], 'conf': 0.01}]},
                                                 ],
                                                },
                                },
                        }
            }

        list_messages_to_rabbit.append(message_json)
    messages_to_rabbit = {"meta_list_all": list_messages_to_rabbit}

    channel.basic_publish(
        exchange="",
        routing_key="meta_data",
        body=pickle.dumps(messages_to_rabbit),
    )
    time.sleep(5)
