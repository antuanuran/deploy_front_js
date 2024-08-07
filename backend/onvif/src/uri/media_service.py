import sys

sys.path.append("../")

from configs import MEDIA_TYPE, HEADERS, PATH_TAG, COMMON, CAMERAS, URI
import logging
from fastapi import Response
from bs4 import BeautifulSoup


def create_response(tag_for_det_act, soup_request):
    with open(PATH_TAG[tag_for_det_act]) as file:
        xml_response = file.read()

    match tag_for_det_act:
        case "GetProfiles":
            status_code = 200
            content_head = xml_response[
                : xml_response.find('<trt:Profiles fixed="true" token="{profile}">')
            ]
            content_tail = xml_response[
                xml_response.find("</trt:GetProfilesResponse>") :
            ]
            content_message = xml_response[
                xml_response.find(
                    '<trt:Profiles fixed="true" token="{profile}">'
                ) : xml_response.find("</trt:GetProfilesResponse>")
            ]
            content = content_head
            for video_source in list(COMMON.cameras_in_work):
                for profile in CAMERAS[video_source].profiles:
                    content += content_message.format(
                        profile=profile, video_source=video_source
                    )
            content += content_tail
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " media_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "GetStreamUri":
            profile = soup_request.find("ProfileToken").string
            break_out_flag = False
            for video_source in COMMON.cameras_in_work:
                for camera_profile in CAMERAS[video_source].profiles:
                    if camera_profile == profile:
                        break_out_flag = True
                        break
                if break_out_flag:
                    break
            status_code = 200
            content = xml_response.format(uri=URI[video_source])
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " media_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "GetSnapshotUri":
            status_code = 200
            content = xml_response.format(ip_server=COMMON.ip_server, port_for_onvif=COMMON.port_for_onvif)
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " media_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "GetVideoSources":
            status_code = 200
            soup_for_temp = BeautifulSoup(xml_response, "xml")
            soup_for_temp.find("VideoSources").decompose()
            for video_source in COMMON.cameras_in_work:
                soup_for_message = BeautifulSoup(xml_response, "xml")
                soup_for_message.find("VideoSources")["token"] = video_source
                soup_for_message.find("VideoSources").name = "trt:VideoSources"
                soup_for_message = soup_for_message.find("trt:VideoSources")
                soup_for_temp.find("GetVideoSourcesResponse").append(soup_for_message)
            content = soup_for_temp.prettify().replace("\n", "")
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " media_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "GetVideoSourceConfigurations":
            status_code = 200
            content = xml_response
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " media_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "GetAudioSourceConfigurations":
            status_code = 200
            content = xml_response
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " media_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "GetProfile":
            profile = soup_request.find("ProfileToken").string
            for video_source in COMMON.cameras_in_work:
                if profile in CAMERAS[video_source].profiles:
                    break
            status_code = 200
            content = xml_response.format(profile=profile, video_source=video_source)
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " media_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "GetVideoSourceConfiguration":
            status_code = 200
            content = xml_response
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " media_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "GetMetadataConfigurationOptions":
            status_code = 200
            content = xml_response
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " media_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "GetMetadataConfiguration":
            status_code = 200
            content = xml_response
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " media_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "GetAudioSources":
            status_code = 200
            content = xml_response
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " media_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response

        case "GetVideoEncoderConfigurationOptions":
            status_code = 200
            content = xml_response
            response = Response(
                media_type=MEDIA_TYPE,
                status_code=status_code,
                content=content,
                headers=HEADERS,
            )
            logging.info(
                " media_service | create_response | response: %s \n "
                % (content.replace("\n", "").replace(" ", ""))
            )
            return response
