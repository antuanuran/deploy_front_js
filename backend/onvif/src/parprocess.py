import logging
import pika
import json
from utils import ping_server
from configs import CONNECTION_PARAMETERS, HOSTNAME, PORT


def add_data_to_queue_for_clients(queue):
    def create_event_to_onvif(body):
        event = {
            "camera_name": body["cam"],
            "camera_location": body["location_description"],
            "class_name": body["class_name"],
            "description": body["description"],
            "dt": body["datetime"],
            "model_confidence": body["confidence"],
        }
        return event

    def callback_onvif(ch, method, properties, body):
        json_data = body.decode("utf-8")
        data = json.loads(json_data)
        event = create_event_to_onvif(data)

        queue.put(event)
        logging.info(
            " parprocess | add_data_to_queue_for_clients | len queue: %s \n "
            % (queue.qsize())
        )

    while True:
        exist_service = ping_server(HOSTNAME, PORT)
        if exist_service:
            break

    connection = pika.BlockingConnection(CONNECTION_PARAMETERS)
    channel = connection.channel()
    queue_onvif = "onvif_message_queue"
    channel.queue_declare(queue=queue_onvif, durable=True, arguments={'x-message-ttl': 3600000})
    channel.basic_consume(
        queue=queue_onvif, on_message_callback=callback_onvif, auto_ack=True
    )
    channel.start_consuming()
    logging.info(
        " __init__ | __init__ | consumer in onvif start \n "
    )
