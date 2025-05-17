__all__ = [
    "FileTypes",
    "DataHandler",
    "JE_Uncompressed",
    "BE_Uncompressed",
    "JE_ZlibCompressed",
    "JE_GzipCompressed",
    "BE_WithHeader",
    "NBTFile",
]

import struct
import zlib
import gzip
from io import BytesIO
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from enum import Enum

from nbt_helper.tags import (
    BaseTag,
    BinaryHandler,
    ByteOrder,
    TagCompound,
    TAG_COMPOUND,
    TagString,
)

BEDROCK_EDITION_MAGIC_NUMBER = 8
GZIP_MAGIC_NUMBER = b"\x1f\x8b\x08"
ZLIB_MAGIC_NUMBER = 120
PLAIN_NBT_MAGIC_NUMBER = b"\n\x00\x00"


class FileTypes(Enum):
    JE_UNCOMPRESSED = 0
    JE_GZIP_COMPRESSED = 1
    JE_ZLIB_COMPRESSED = 2
    BE_UNCOMPRESSED = 3
    BE_WITH_HEADER = 4


class DataHandler(ABC):
    @staticmethod
    @abstractmethod
    def load(buffer: BinaryIO, *args, **kwargs) -> TagCompound: ...

    @staticmethod
    @abstractmethod
    def save(data: TagCompound, buffer: BinaryIO, *args, **kwargs) -> None: ...


class Uncompressed(DataHandler):
    @staticmethod
    def load(buffer: BinaryIO, byte_order: ByteOrder) -> TagCompound:
        binary_handler = BinaryHandler(byte_order)
        tag_id = binary_handler.read_byte(buffer)
        if tag_id != TAG_COMPOUND:
            raise ValueError("File data must starts with Compound tag.")
        name = TagString(binary_handler, buffer=buffer).value
        return TagCompound(binary_handler, buffer=buffer, name=name)

    @staticmethod
    def save(data: BaseTag, buffer: BinaryIO, byte_order: ByteOrder) -> None:
        binary_handler = BinaryHandler(byte_order)
        TagCompound(binary_handler, value=[TagCompound(binary_handler, value=[data])]).write_to_buffer(buffer)


class JE_Uncompressed(DataHandler):
    @staticmethod
    def load(buffer: BinaryIO) -> TagCompound:
        return Uncompressed.load(buffer, ByteOrder.BIG)

    @staticmethod
    def save(data: BaseTag, buffer: BinaryIO) -> None:
        if data.binary_handler.get_byte_order() is ByteOrder.LITTLE:
            data.binary_handler.change_byte_order(ByteOrder.BIG)
        Uncompressed.save(data, buffer, ByteOrder.BIG)


class BE_Uncompressed(DataHandler):
    @staticmethod
    def load(buffer: BinaryIO) -> TagCompound:
        return Uncompressed.load(buffer, ByteOrder.LITTLE)

    @staticmethod
    def save(data: BaseTag, buffer: BinaryIO) -> None:
        if data.binary_handler.get_byte_order() is ByteOrder.BIG:
            data.binary_handler.change_byte_order(ByteOrder.LITTLE)
        Uncompressed.save(data, buffer, ByteOrder.LITTLE)


class JE_ZlibCompressed(DataHandler):
    @staticmethod
    def load(buffer: BinaryIO) -> TagCompound:
        buffer = BytesIO(zlib.decompress(buffer.read()))
        return JE_Uncompressed.load(buffer)

    @staticmethod
    def save(data: BaseTag, buffer: BinaryIO) -> None:
        temp_buffer = BytesIO()
        JE_Uncompressed.save(data, temp_buffer)
        buffer.write(zlib.compress(temp_buffer.getvalue()))


class JE_GzipCompressed(DataHandler):
    @staticmethod
    def load(buffer: BinaryIO) -> TagCompound:
        buffer = BytesIO(gzip.decompress(buffer.read()))
        return JE_Uncompressed.load(buffer)

    @staticmethod
    def save(data: BaseTag, buffer: BinaryIO) -> None:
        temp_buffer = BytesIO()
        JE_Uncompressed.save(data, temp_buffer)
        buffer.write(gzip.compress(temp_buffer.getvalue()))


class BE_WithHeader(DataHandler):
    @staticmethod
    def load(buffer: BinaryIO) -> TagCompound:
        binary_handler = BinaryHandler(ByteOrder.LITTLE)
        magic_number = binary_handler.read_int(buffer)
        if magic_number != BEDROCK_EDITION_MAGIC_NUMBER:
            raise ValueError("Wrong data handler used! Unknown magic number")
        size = binary_handler.read_int(buffer, signed=False)
        buffer = BytesIO(buffer.read(size))
        return BE_Uncompressed.load(buffer)

    @staticmethod
    def save(data: BaseTag, buffer: BinaryIO) -> None:
        binary_handler = BinaryHandler(ByteOrder.LITTLE)
        binary_handler.write_int(buffer, BEDROCK_EDITION_MAGIC_NUMBER)
        temp_buffer = BytesIO()

        BE_Uncompressed.save(data, temp_buffer)

        binary_handler.write_int(buffer, temp_buffer.tell(), signed=False)
        buffer.write(temp_buffer.getvalue())


class NBTFile:
    def __init__(self, type: FileTypes = FileTypes.JE_GZIP_COMPRESSED) -> None:
        super().__init__()
        self._type = type
        self.data = TagCompound(BinaryHandler())

    def load(self, buffer: BinaryIO) -> None:
        self.guess(buffer)
        self._handler = HANDLERS_LIST[self._type]
        self.data = self._handler.load(buffer=buffer)

    def save(self, buffer: BinaryIO, type: Optional[FileTypes] = None) -> None:
        if type is not None:
            self._type = type
            self._handler = HANDLERS_LIST[self._type]

        self._handler.save(buffer=buffer, data=self.data)

    def guess(self, buffer: BinaryIO) -> bool:
        start_pos = buffer.tell()
        magic_number = buffer.read(6)
        buffer.seek(start_pos)

        self._type = FileTypes.JE_GZIP_COMPRESSED

        if magic_number[:3] == GZIP_MAGIC_NUMBER:
            self._type = FileTypes.JE_GZIP_COMPRESSED
            return True
        elif magic_number[:3] == PLAIN_NBT_MAGIC_NUMBER:
            self._type = FileTypes.JE_UNCOMPRESSED
            if struct.unpack(">3h", magic_number)[2] > 255:
                self._type = FileTypes.BE_UNCOMPRESSED
            return True
        elif struct.unpack(">h", magic_number[:2])[0] >> 8 & 255 == ZLIB_MAGIC_NUMBER:
            self._type = FileTypes.JE_ZLIB_COMPRESSED
            return True
        elif struct.unpack("<h", magic_number[:2])[0] == BEDROCK_EDITION_MAGIC_NUMBER:
            self._type = FileTypes.BE_WITH_HEADER
            return True
        return False


HANDLERS_LIST = {
    FileTypes.JE_UNCOMPRESSED: JE_Uncompressed,
    FileTypes.BE_UNCOMPRESSED: BE_Uncompressed,
    FileTypes.BE_WITH_HEADER: BE_WithHeader,
    FileTypes.JE_GZIP_COMPRESSED: JE_GzipCompressed,
    FileTypes.JE_ZLIB_COMPRESSED: JE_ZlibCompressed,
}
