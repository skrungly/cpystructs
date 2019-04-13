from ctypes import (
    c_char_p, c_int, c_ssize_t, c_void_p,
    CFUNCTYPE, POINTER, py_object
)

from ._structs import Py_buffer, PyTypeObject

__all__ = [
    "allocfunc",
    "binaryfunc",
    "descrgetfunc",
    "descrsetfunc",
    "destructor",
    "freefunc",
    "getattrfunc",
    "getattrofunc",
    "getbufferproc",
    "getiterfunc",
    "getter",
    "hashfunc",
    "initproc",
    "inquiry",
    "iternextfunc",
    "lenfunc",
    "newfunc",
    "objobjargproc",
    "objobjproc",
    "printfunc",
    "Py_tracefunc",
    "PyFrameEvalFunction",
    "releasebufferproc",
    "reprfunc",
    "richcmpfunc",
    "setattrfunc",
    "setattrofunc",
    "setter",
    "ssizeargfunc",
    "ssizeobjargproc",
    "ssizessizeargfunc",
    "ssizessizeobjargproc",
    "ternaryfunc",
    "traverseproc",
    "unaryfunc",
    "visitproc",
]

# the source for vast majority of these definitions can be found here:
# https://github.com/python/cpython/blob/master/Include/object.h#L145

unaryfunc = CFUNCTYPE(py_object, py_object)
binaryfunc = CFUNCTYPE(py_object, py_object, py_object)
ternaryfunc = CFUNCTYPE(py_object, py_object, py_object, py_object)
inquiry = CFUNCTYPE(c_int, py_object)
lenfunc = CFUNCTYPE(c_ssize_t, py_object)
ssizeargfunc = CFUNCTYPE(py_object, c_ssize_t)
ssizessizeargfunc = CFUNCTYPE(py_object, c_ssize_t, c_ssize_t)
ssizeobjargproc = CFUNCTYPE(c_int, py_object, c_ssize_t, py_object)
ssizessizeobjargproc = CFUNCTYPE(
    c_int, py_object, c_ssize_t, c_ssize_t, py_object
)
objobjargproc = CFUNCTYPE(c_int, py_object, py_object, py_object)
objobjproc = CFUNCTYPE(c_int, py_object, py_object)

visitproc = CFUNCTYPE(c_int, py_object, c_void_p)
traverseproc = CFUNCTYPE(c_int, py_object, visitproc, c_void_p)

freefunc = CFUNCTYPE(None, c_void_p)
destructor = CFUNCTYPE(None, py_object)
getattrfunc = CFUNCTYPE(py_object, py_object, c_char_p)
getattrofunc = CFUNCTYPE(py_object, py_object, py_object)
setattrfunc = CFUNCTYPE(c_int, py_object, c_char_p, py_object)
setattrofunc = CFUNCTYPE(c_int, py_object, py_object, py_object)
reprfunc = CFUNCTYPE(py_object, py_object)
hashfunc = CFUNCTYPE(c_ssize_t, py_object)
richcmpfunc = CFUNCTYPE(py_object, py_object, py_object, c_int)
getiterfunc = CFUNCTYPE(py_object, py_object)
iternextfunc = CFUNCTYPE(py_object, py_object)
descrgetfunc = CFUNCTYPE(py_object, py_object, py_object, py_object)
descrsetfunc = CFUNCTYPE(c_int, py_object, py_object, py_object)
initproc = CFUNCTYPE(c_int, py_object, py_object, py_object)

getbufferproc = CFUNCTYPE(c_int, py_object, POINTER(Py_buffer), c_int)
releasebufferproc = CFUNCTYPE(None, py_object, POINTER(Py_buffer))

newfunc = CFUNCTYPE(py_object, POINTER(PyTypeObject), py_object, py_object)
allocfunc = CFUNCTYPE(py_object, POINTER(PyTypeObject), c_ssize_t)

getter = CFUNCTYPE(py_object, py_object, c_void_p)
setter = CFUNCTYPE(c_int, py_object, py_object, c_void_p)

# TODO: give the c_void_p here an actual type (preferably FILE *)
printfunc = CFUNCTYPE(c_int, py_object, c_void_p, c_int)

# and make this c_void_p a pointer to a frame struct
Py_tracefunc = CFUNCTYPE(c_int, py_object, c_void_p, c_int, py_object)
PyFrameEvalFunction = CFUNCTYPE(py_object, c_void_p, c_int)