import sys

sys.path.append("../")

import datetime
from configs import MEDIA_TYPE, HEADERS, PATH_TAG, COMMON
import logging
from fastapi import Response
import multiprocessing
from parprocess import add_data_to_queue_for_clients


def create_response(tag_for_det_act, soup_request):
    with open(PATH_TAG[tag_for_det_act]) as file:
        xml_response = file.read()

    match tag_for_det_act:
        case "Subscribe":
            status_code = 200
            current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            termination_time = (
                datetime.datetime.now() + datetime.timedelta(minutes=1)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            content = xml_response.format(
                current_time=current_time,
                termination_time=termination_time,
                ip_server=COMMON.ip_server,
                port_for_onvif=COMMON.port_for_onvif
            )
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " event_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "GetEventProperties":
            status_code = 200
            content = xml_response
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " event_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "CreatePullPointSubscription":
            global queue
            global onviv_process

            queue = multiprocessing.Queue()
            subscription_id = 0
            onviv_process = multiprocessing.Process(
                target=add_data_to_queue_for_clients, args=(queue,)
            )
            onviv_process.start()
            logging.info(
                " event_service | create_response | create subscription_id: %s \n "
                % (subscription_id)
            )
            logging.info(
                " event_service | create_response | queue.qsize(): %s \n "
                % (queue.qsize())
            )

            status_code = 200
            current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            termination_time = (
                datetime.datetime.now() + datetime.timedelta(minutes=1)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            content = xml_response.format(
                ip_server=COMMON.ip_server,
                current_time=current_time,
                subscription_id=subscription_id,
                termination_time=termination_time,
                port_for_onvif=COMMON.port_for_onvif
            )
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " event_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response
