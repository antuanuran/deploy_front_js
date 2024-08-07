import socket
import cv2
import logging

from configs import URI


def ping_server(server: str, port: int, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, port))
    except OSError as error:
        return False
    else:
        s.close()
        return True


def get_shapshot():
    vcap = cv2.VideoCapture(URI['3'])
    _, frame = vcap.read()
    return frame
