from ctypes import CDLL, c_float, c_bool

lib = CDLL("../ext_lib/status_check.so")

check_status = lib.check_status
check_status.argtypes = [c_float, c_float]
check_status.restype = c_bool