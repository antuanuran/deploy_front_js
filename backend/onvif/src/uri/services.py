import sys

sys.path.append("../")

import datetime
import logging
from bs4 import BeautifulSoup

from configs import MEDIA_TYPE, HEADERS, PATH_TAG
from fastapi import Response
import uri.event_service
import time


def create_response(tag_for_det_act, soup_request):
    with open(PATH_TAG[tag_for_det_act]) as file:
        xml_response = file.read()

    match tag_for_det_act:
        case "Renew":
            status_code = 200
            current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            termination_time = (
                datetime.datetime.now() + datetime.timedelta(minutes=1)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            content = xml_response.format(
                current_time=current_time, termination_time=termination_time
            )
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " sevices | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "PullMessages":
            time.sleep(1)
            status_code = 200
            current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            termination_time = (
                datetime.datetime.now() + datetime.timedelta(minutes=1)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            soup_for_temp = BeautifulSoup(xml_response, "xml")
            soup_for_temp.find("wsnt:NotificationMessage").decompose()
            soup_for_temp.find("tev:CurrentTime").string.replace_with(current_time)
            soup_for_temp.find("tev:TerminationTime").string.replace_with(
                termination_time
            )
            if uri.event_service.queue.qsize() != 0:
                while uri.event_service.queue.qsize() != 0:
                    message = uri.event_service.queue.get()                  
                    soup_for_message = BeautifulSoup(xml_response, "xml")
                    soup_for_message = soup_for_message.find("wsnt:NotificationMessage")
                    soup_for_message.find("wsnt:Topic").string.replace_with(
                        message["description"]
                    )
                    soup_for_message.find("tt:Message")["UtcTime"] = message["dt"]
                    soup_for_message.find_all("tt:SimpleItem", {"Name": "camera_name"})[
                        0
                    ]["Value"] = message["camera_name"]
                    soup_for_message.find_all("tt:SimpleItem", {"Name": "class_name"})[
                        0
                    ]["Value"] = message["class_name"]
                    soup_for_message.find_all(
                        "tt:SimpleItem", {"Name": "camera_location"}
                    )[0]["Value"] = message["camera_location"]
                    soup_for_message.find_all(
                        "tt:SimpleItem", {"Name": "model_confidence"}
                    )[0]["Value"] = message["model_confidence"]
                    soup_for_temp.find("tev:PullMessagesResponse").append(
                        soup_for_message
                    )
                content = soup_for_temp.prettify()
            else:
                soup = BeautifulSoup(xml_response, "xml")
                soup.find("wsnt:NotificationMessage").decompose()
                xml_response = soup.prettify()
                content = xml_response.format(
                    current_time=current_time, termination_time=termination_time
                )
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " sevices | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "Unsubscribe":
            uri.event_service.onviv_process.terminate()
            status_code = 200
            content = xml_response
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " sevices | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response
