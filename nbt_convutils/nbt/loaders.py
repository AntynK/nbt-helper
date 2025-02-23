import struct
from typing import BinaryIO


class BigEndianLoader:
    @classmethod
    def read_byte(cls, buffer: BinaryIO) -> int:
        return struct.unpack(">b", buffer.read(1))[0]

    @classmethod
    def read_short(cls, buffer: BinaryIO) -> int:
        return struct.unpack(">h", buffer.read(2))[0]

    @classmethod
    def read_int(cls, buffer: BinaryIO) -> int:
        return struct.unpack(">i", buffer.read(4))[0]

    @classmethod
    def read_long(cls, buffer: BinaryIO) -> int:
        return struct.unpack(">q", buffer.read(8))[0]

    @classmethod
    def read_float(cls, buffer: BinaryIO) -> float:
        return struct.unpack(">f", buffer.read(4))[0]

    @classmethod
    def read_double(cls, buffer: BinaryIO) -> float:
        return struct.unpack(">d", buffer.read(8))[0]

    @classmethod
    def read_int_array(cls, buffer: BinaryIO, size: int) -> tuple[int]:
        fmt = struct.Struct(f">{size}i")
        return fmt.unpack(buffer.read(fmt.size))

    @classmethod
    def read_long_array(cls, buffer: BinaryIO, size: int) -> tuple[int]:
        fmt = struct.Struct(f">{size}q")
        return fmt.unpack(buffer.read(fmt.size))


class LittleEndianLoader:
    @classmethod
    def read_byte(cls, buffer: BinaryIO) -> int:
        return struct.unpack("<b", buffer.read(1))[0]

    @classmethod
    def read_short(cls, buffer: BinaryIO) -> int:
        return struct.unpack("<h", buffer.read(2))[0]

    @classmethod
    def read_int(cls, buffer: BinaryIO) -> int:
        return struct.unpack("<i", buffer.read(4))[0]

    @classmethod
    def read_long(cls, buffer: BinaryIO) -> int:
        return struct.unpack("<q", buffer.read(8))[0]

    @classmethod
    def read_float(cls, buffer: BinaryIO) -> float:
        return struct.unpack("<f", buffer.read(4))[0]

    @classmethod
    def read_double(cls, buffer: BinaryIO) -> float:
        return struct.unpack("<d", buffer.read(8))[0]

    @classmethod
    def read_int_array(cls, buffer: BinaryIO, size: int) -> tuple[int]:
        fmt = struct.Struct(f"<{size}i")
        return fmt.unpack(buffer.read(fmt.size))

    @classmethod
    def read_long_array(cls, buffer: BinaryIO, size: int) -> tuple[int]:
        fmt = struct.Struct(f"<{size}q")
        return fmt.unpack(buffer.read(fmt.size))
