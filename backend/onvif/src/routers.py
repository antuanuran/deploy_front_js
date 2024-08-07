from fastapi import Request, APIRouter, Response
import logging

import io
from imageio import v3 as iio

import uri.device_service
import uri.media_service
import uri.event_service
import uri.services

from fastapi.responses import FileResponse
from request import parsing_xml
from utils import get_shapshot


router = APIRouter()


@router.post("/onvif/device_service", tags=["device_service"])
async def post_device_service(request: Request):
    xml_bytes = await request.body()
    soup_request, tag_for_det_act = parsing_xml(xml_bytes)

    logging.info(
        " routers | post_device_service | tag_for_det_act: %s \n " % (tag_for_det_act)
    )
    logging.info(
        " routers | post_device_service | headers: %s \n " % (request.headers)
    )
    logging.info(
        " routers | post_device_service | content: %s \n " % (soup_request)
    )

    response = uri.device_service.create_response(tag_for_det_act, soup_request)
    return response


@router.post("/onvif/media_service", tags=["media_service"])
async def post_media_service(request: Request):
    xml_bytes = await request.body()
    soup_request, tag_for_det_act = parsing_xml(xml_bytes)

    logging.info(
        " routers | post_media_service | tag_for_det_act: %s \n " % (tag_for_det_act)
    )
    logging.info(
        " routers | post_media_service | headers: %s \n " % (request.headers)
    )
    logging.info(
        " routers | post_media_service | content: %s \n " % (soup_request)
    )

    response = uri.media_service.create_response(tag_for_det_act, soup_request)
    return response


@router.post("/onvif/event_service", tags=["eventservice"])
async def post_event_service(request: Request):
    xml_bytes = await request.body()
    soup_request, tag_for_det_act = parsing_xml(xml_bytes)

    logging.info(
        " routers | post_event_service | tag_for_det_act: %s \n " % (tag_for_det_act)
    )
    logging.info(
        " routers | post_event_service | headers: %s \n " % (request.headers)
    )
    logging.info(
        " routers | post_event_service | content: %s \n " % (soup_request)
    )

    response = uri.event_service.create_response(tag_for_det_act, soup_request)
    return response


@router.post("/onvif/services", tags=["services"])
async def post_services(request: Request):
    xml_bytes = await request.body()
    soup_request, tag_for_det_act = parsing_xml(xml_bytes)

    logging.info(
        " routers | post_services | tag_for_det_act: %s \n " % (tag_for_det_act)
    )
    logging.info(
        " routers | post_services | headers: %s \n " % (request.headers)
    )
    logging.info(
        " routers | post_services | content: %s \n " % (soup_request)
    )

    response = uri.services.create_response(tag_for_det_act, soup_request)
    return response


@router.get("/snapshot", tags=["snapshot"])
@router.get("/image")
async def get_snapshot_snapshot():
    frame = get_shapshot()
    logging.info(
        " routers | get_snapshot | request snapshot \n "
    )
    with io.BytesIO() as buf:
        iio.imwrite(buf, frame, plugin="pillow", format="JPEG")
        im_bytes = buf.getvalue()
    return Response(im_bytes, media_type='image/jpeg')
