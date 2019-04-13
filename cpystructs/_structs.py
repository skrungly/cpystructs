import ctypes
from ctypes import (
    c_char, c_char_p, c_double, c_int, c_ssize_t, c_uint,
    c_uint32, c_ulong, c_void_p, POINTER, py_object, Structure
)

# TODO: do we want separate "typedefs" for non-standard
# types in cpython like Py_ssize_t and Py_hash_t? Maybe.

__all__ = [
    "PyAsyncMethods",
    "PyBufferProcs",
    "PyBytesObject",
    "PyFloatObject",
    "PyGetSetDef",
    "PyListObject",
    "PyLongObject",
    "PyMappingMethods",
    "PyMemberDef",
    "PyMethodDef",
    "PyNumberMethods",
    "PyObject",
    "PySequenceMethods",
    "PyTupleObject",
    "PyTypeObject",
    "PyVarObject",
    "Py_buffer",
]


class _PyStruct(Structure):
    """
    A basic subclass of ctypes.Structure which gives a simple
    class method for defining the fields after declaration.
    Also provides basic methods for interacting with objects.
    """

    @classmethod
    def set_fields(cls, **fields):
        cls._fields_ = tuple(fields.items())

    @classmethod
    def from_object(cls, obj):
        return cls.from_address(id(obj))

    @classmethod
    def field_offset(cls, field):
        """
        Find how many bytes are before a field. At least for
        now, this will not check if the given field name is
        in the struct. If a name is passed which isn't in the
        struct, this will fall through to the end and return
        the total size of the struct. For now.
        """

        total = 0
        for name, ctype in cls._fields_:
            if name == field:
                break

            total += ctypes.sizeof(ctype)

        return total

    def field_address(self, field):
        offset = self.field_offset(field)
        addr = ctypes.addressof(self)
        return addr + offset

    @property
    def value(self):
        ptr = c_void_p(ctypes.addressof(self))
        return ctypes.cast(ptr, py_object).value

    def as_type(self, struct_type):
        return struct_type.from_address(
            ctypes.addressof(self)
        )


# we're forward-declaring these structs for two reasons.
# 1 - to avoid postponed references to not-yet-defined structs.
# 2 - to avoid circular imports with the `_funcs.py` script
class PyObject(_PyStruct): ...
class PyVarObject(_PyStruct): ...
class PyTypeObject(_PyStruct): ...
class PyAsyncMethods(_PyStruct): ...
class PyNumberMethods(_PyStruct): ...
class PySequenceMethods(_PyStruct): ...
class PyMappingMethods(_PyStruct): ...
class PyBufferProcs(_PyStruct): ...
class PyMethodDef(_PyStruct): ...
class PyMemberDef(_PyStruct): ...
class Py_buffer(_PyStruct): ...
class PyGetSetDef(_PyStruct): ...
class PyFloatObject(_PyStruct): ...

class PyLongObject(_PyStruct):
    @property
    def ob_digit(self):
        size = self.ob_base.ob_size
        array = c_uint32 * size
        return ctypes.cast(self._ob_digit, array)

class PyListObject(_PyStruct):
    @property
    def ob_item(self):
        size = self.ob_base.ob_size
        ptr = POINTER(POINTER(PyObject) * size)  # PyObject **
        return ctypes.cast(self._ob_item, ptr)

class PyTupleObject(_PyStruct):
    @property
    def ob_item(self):
        size = self.ob_base.ob_size
        array = POINTER(PyObject) * size

        address = self.field_address("_ob_item")
        return array.from_address(address)

class PyBytesObject(_PyStruct):
    @property
    def ob_sval(self):
        size = self.ob_base.ob_size
        array = c_char * (size + 1)

        address = self.field_address("_ob_sval")
        return array.from_address(address)

# all structs have been defined, so now we can import the func types
from ._funcs import *

# if python was configured using the --with-pydebug option
# before being compiled, the PyObject struct will contain two
# additional pointers to other PyObjects, forming a doubly-
# linked list of structs.
WITH_PYDEBUG = object().__sizeof__ == (
    ctypes.sizeof(c_ssize_t) * 4
)

PyObject.set_fields(
    # this could probably be cleaner but oh well.
    _ob_next=POINTER(PyObject) if WITH_PYDEBUG else None,
    _ob_prev=POINTER(PyObject) if WITH_PYDEBUG else None,
    ob_refcount=c_ssize_t,
    ob_type=POINTER(PyTypeObject),
)

PyVarObject.set_fields(
    ob_base=PyObject,
    ob_size=c_ssize_t,
)

PyTypeObject.set_fields(
    ob_base=PyVarObject,
    tp_name=c_char_p,
    tp_basicsize=c_ssize_t,
    tp_itemsize=c_ssize_t,

    tp_dealloc=destructor,
    tp_print=printfunc,
    tp_getattr=getattrfunc,
    tp_setattr=setattrfunc,
    tp_as_async=POINTER(PyAsyncMethods),
    tp_repr=reprfunc,

    tp_as_number=POINTER(PyNumberMethods),
    tp_as_sequence=POINTER(PySequenceMethods),
    tp_as_mapping=POINTER(PyMappingMethods),

    tp_hash=hashfunc,
    tp_call=ternaryfunc,
    tp_str=reprfunc,
    tp_getattro=getattrofunc,
    tp_setattro=setattrofunc,

    tp_as_buffer=POINTER(PyBufferProcs),
    tp_flags=c_ulong,
    tp_doc=c_char_p,

    tp_traverse=traverseproc,
    tp_clear=inquiry,
    tp_richcompare=richcmpfunc,
    tp_weaklistoffset=c_ssize_t,

    tp_iter=getiterfunc,
    tp_iternext=iternextfunc,

    tp_methods=POINTER(PyMethodDef),
    tp_members=POINTER(PyMemberDef),
    tp_getset=POINTER(PyGetSetDef),
    tp_base=POINTER(PyTypeObject),
    tp_dict=POINTER(PyObject),

    tp_descr_get=descrgetfunc,
    tp_descr_set=descrsetfunc,
    tp_dictoffset=c_ssize_t,
    tp_init=initproc,
    tp_alloc=allocfunc,
    tp_new=newfunc,
    tp_free=freefunc,
    tp_is_gc=inquiry,
    tp_bases=POINTER(PyObject),
    tp_mro=POINTER(PyObject),
    tp_cache=POINTER(PyObject),
    tp_subclasses=POINTER(PyObject),
    tp_weaklist=POINTER(PyObject),

    tp_version_tag=c_uint,
    tp_finalize=destructor,
)

PyAsyncMethods.set_fields(
    am_await=unaryfunc,
    am_aiter=unaryfunc,
    am_anext=unaryfunc,
)

PyNumberMethods.set_fields(
    nb_add=binaryfunc,
    nb_subtract=binaryfunc,
    nb_multiply=binaryfunc,
    nb_remainder=binaryfunc,
    nb_divmod=binaryfunc,
    nb_power=ternaryfunc,
    nb_negative=unaryfunc,
    nb_positive=unaryfunc,
    nb_absolute=unaryfunc,
    nb_bool=inquiry,
    nb_invert=unaryfunc,
    nb_lshift=binaryfunc,
    nb_rshift=binaryfunc,
    nb_and=binaryfunc,
    nb_xor=binaryfunc,
    nb_or=binaryfunc,
    nb_int=unaryfunc,
    nb_reserved=c_void_p,
    nb_float=unaryfunc,

    nb_inplace_add=binaryfunc,
    nb_inplace_subtract=binaryfunc,
    nb_inplace_multiply=binaryfunc,
    nb_inplace_remainder=binaryfunc,
    nb_inplace_power=ternaryfunc,
    nb_inplace_lshift=binaryfunc,
    nb_inplace_rshift=binaryfunc,
    nb_inplace_and=binaryfunc,
    nb_inplace_xor=binaryfunc,
    nb_inplace_or=binaryfunc,

    nb_floor_divide=binaryfunc,
    nb_true_divide=binaryfunc,
    nb_inplace_floor_divide=binaryfunc,
    nb_inplace_true_divide=binaryfunc,

    nb_index=unaryfunc,

    nb_matrix_multiply=binaryfunc,
    nb_inplace_matrix_multiply=binaryfunc,
)

PySequenceMethods.set_fields(
    sq_length=lenfunc,
    sq_concat=binaryfunc,
    sq_repeat=ssizeargfunc,
    sq_item=ssizeargfunc,
    was_sq_slice=c_void_p,
    sq_ass_item=ssizeobjargproc,
    was_sq_ass_slice=c_void_p,
    sq_contains=objobjproc,

    sq_inplace_concat=binaryfunc,
    sq_inplace_repeat=ssizeargfunc,
)

PyMappingMethods.set_fields(
    mp_length=lenfunc,
    mp_subscript=binaryfunc,
    mp_ass_subscript=objobjargproc,
)

PyBufferProcs.set_fields(
    bf_getbuffer=getbufferproc,
    bf_releasebuffer=releasebufferproc,
)

Py_buffer.set_fields(
    buf=c_void_p,
    obj=POINTER(PyObject),
    len=c_ssize_t,
    itemsize=c_ssize_t,

    readonly=c_int,
    ndim=c_int,
    format=c_char_p,
    shape=POINTER(c_ssize_t),
    strides=POINTER(c_ssize_t),
    suboffsets=POINTER(c_ssize_t),
    internal=c_void_p
)

PyGetSetDef.set_fields(
    name=c_char_p,
    get=getter,
    set=setter,
    doc=c_char_p,
    closure=c_void_p,
)

PyLongObject.set_fields(
    ob_base=PyVarObject,
    # `ob_digit` is replaced with `c_uint32[ob_size]` when accessed
    _ob_digit=c_void_p,
)

PyListObject.set_fields(
    ob_base=PyVarObject,
    # `ob_item` is replaced with `PyObject **` when accessed
    _ob_item=c_void_p,
    allocated=c_ssize_t,
)

PyFloatObject.set_fields(
    ob_base=PyObject,
    ob_fval=c_double
)

PyTupleObject.set_fields(
    ob_base=PyVarObject,
    # `ob_item` is replaced with `PyObject*[ob_size]` when accessed
    _ob_item=c_void_p
)

PyBytesObject.set_fields(
    ob_base=PyVarObject,
    ob_shash=c_ssize_t,
    # `ob_sval` is replaced with `char[ob_size]` when accessed
    _ob_sval=c_void_p
)
