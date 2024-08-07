import logging
from contextlib import contextmanager
from ctypes import *


@contextmanager
def GST_PAD_PROBE_INFO_BUFFER(info):
    _buffer = info.get_buffer()
    _buffer.mini_object.refcount -= 1
    try:
        yield _buffer
    finally:
        _buffer.mini_object.refcount += 1


class GstLastImageParam(Structure):
    _fields_ = [
                ("height", c_uint16),
                ("width", c_uint16),
                ("pts", c_uint),
                ("draw_rect_flag", c_uint),                
                ]
    

def create_ctypes_for_gst(results):
    lenght = len(results['cls'])
    lenght_sk = len(results['confsk'])


    class GstDetectionParam(Structure):
        _fields_ = [
                    ('time', c_wchar_p),
                    ('model', c_wchar_p * lenght),            
                    ('cls', c_wchar_p * lenght),
                    ('conf', c_float * lenght),
                    ('x1', c_int * lenght),              
                    ('y1', c_int * lenght),                  
                    ('x2', c_int * lenght),
                    ('y2', c_int * lenght),
                    ('xsk', c_int * lenght_sk),
                    ('ysk', c_int * lenght_sk),
                    ('confsk', c_float * lenght_sk),
                    ('modelsk', c_wchar_p * lenght_sk)                                                    
                    ]


    c_types_results = GstDetectionParam(
                                (c_wchar_p)(results['time']),
                                (c_wchar_p * len(results['model']))(*results['model']),     
                                (c_wchar_p * len(results['cls']))(*results['cls']),
                                (c_float * len(results['conf']))(*results['conf']),
                                (c_int * len(results['x1']))(*results['x1']),
                                (c_int * len(results['y1']))(*results['y1']),
                                (c_int * len(results['x2']))(*results['x2']),
                                (c_int * len(results['y2']))(*results['y2']),
                                (c_int * len(results['xsk']))(*results['xsk']),
                                (c_int * len(results['ysk']))(*results['ysk']),
                                (c_float * len(results['confsk']))(*results['confsk']),
                                (c_wchar_p * len(results['modelsk']))(*results['modelsk']),                                                                                      
                                )
    return c_types_results