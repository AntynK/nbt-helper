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
from pathlib import Path
from io import BytesIO
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Union
from enum import Enum

from nbt_helper.tags import (
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

StrOrPath = Union[str, Path]


class FileTypes(Enum):
    JE_UNCOMPRESSED = 0
    JE_GZIP_COMPRESSED = 1
    JE_ZLIB_COMPRESSED = 2
    BE_UNCOMPRESSED = 3
    BE_WITH_HEADER = 4


class DataHandler(ABC):
    """This class describes interface of DataHandlers that are used for reading and writing NBT files."""

    @staticmethod
    @abstractmethod
    def read(buffer: BinaryIO, *args, **kwargs) -> TagCompound: ...

    @staticmethod
    @abstractmethod
    def write(data: TagCompound, buffer: BinaryIO, *args, **kwargs) -> None: ...


class Uncompressed(DataHandler):
    @staticmethod
    def read(buffer: BinaryIO, byte_order: ByteOrder) -> TagCompound:
        binary_handler = BinaryHandler(byte_order)
        tag_id = binary_handler.read_byte(buffer)
        if tag_id != TAG_COMPOUND:
            raise ValueError("File data must starts with Compound tag.")
        name = TagString(binary_handler, buffer=buffer).value
        return TagCompound(binary_handler, buffer=buffer, name=name)

    @staticmethod
    def write(data: TagCompound, buffer: BinaryIO) -> None:
        buffer.write(PLAIN_NBT_MAGIC_NUMBER)
        data.write_to_buffer(buffer)


class JE_Uncompressed(DataHandler):
    @staticmethod
    def read(buffer: BinaryIO) -> TagCompound:
        return Uncompressed.read(buffer, ByteOrder.BIG)

    @staticmethod
    def write(data: TagCompound, buffer: BinaryIO) -> None:
        if data.get_byte_order() is ByteOrder.LITTLE:
            data.change_byte_order(ByteOrder.BIG)
        Uncompressed.write(data, buffer)


class BE_Uncompressed(DataHandler):
    @staticmethod
    def read(buffer: BinaryIO) -> TagCompound:
        return Uncompressed.read(buffer, ByteOrder.LITTLE)

    @staticmethod
    def write(data: TagCompound, buffer: BinaryIO) -> None:
        if data.get_byte_order() is ByteOrder.BIG:
            data.change_byte_order(ByteOrder.LITTLE)
        Uncompressed.write(data, buffer)


class JE_ZlibCompressed(DataHandler):
    @staticmethod
    def read(buffer: BinaryIO) -> TagCompound:
        buffer = BytesIO(zlib.decompress(buffer.read()))
        return JE_Uncompressed.read(buffer)

    @staticmethod
    def write(data: TagCompound, buffer: BinaryIO) -> None:
        temp_buffer = BytesIO()
        JE_Uncompressed.write(data, temp_buffer)
        buffer.write(zlib.compress(temp_buffer.getvalue()))


class JE_GzipCompressed(DataHandler):
    @staticmethod
    def read(buffer: BinaryIO) -> TagCompound:
        buffer = BytesIO(gzip.decompress(buffer.read()))
        return JE_Uncompressed.read(buffer)

    @staticmethod
    def write(data: TagCompound, buffer: BinaryIO) -> None:
        temp_buffer = BytesIO()
        JE_Uncompressed.write(data, temp_buffer)
        buffer.write(gzip.compress(temp_buffer.getvalue()))


class BE_WithHeader(DataHandler):
    @staticmethod
    def read(buffer: BinaryIO) -> TagCompound:
        binary_handler = BinaryHandler(ByteOrder.LITTLE)
        magic_number = binary_handler.read_int(buffer)
        if magic_number != BEDROCK_EDITION_MAGIC_NUMBER:
            raise ValueError("Wrong data handler used! Unknown magic number")
        size = binary_handler.read_int(buffer, signed=False)
        buffer = BytesIO(buffer.read(size))
        return BE_Uncompressed.read(buffer)

    @staticmethod
    def write(data: TagCompound, buffer: BinaryIO) -> None:
        binary_handler = BinaryHandler(ByteOrder.LITTLE)
        binary_handler.write_int(buffer, BEDROCK_EDITION_MAGIC_NUMBER)
        temp_buffer = BytesIO()

        BE_Uncompressed.write(data, temp_buffer)

        binary_handler.write_int(buffer, temp_buffer.tell(), signed=False)
        buffer.write(temp_buffer.getvalue())


class NBTFile:
    """This class is used for high-level reading and writing of NBT files.
    The file type is automatically guessed based on the header.
    """

    def __init__(
        self,
        filepath: Optional[StrOrPath] = None,
        buffer: Optional[BinaryIO] = None,
        type: FileTypes = FileTypes.JE_GZIP_COMPRESSED,
    ) -> None:
        super().__init__()
        self._type = type
        self._handler = HANDLERS[self._type]
        self.data = TagCompound(BinaryHandler())

        if filepath:
            with open(filepath, "rb") as file:
                self.load(file)
        elif buffer:
            self.load(buffer)

    def get_file_type(self) -> FileTypes:
        return self._type

    def load(self, buffer: BinaryIO) -> None:
        """Loads data from the buffer

        Raises:
            ValueError: if the file type cannot be guessed.
        """

        if not self.guess(buffer):
            raise ValueError("Unknown file format.")
        self._handler = HANDLERS[self._type]
        self.data = self._handler.read(buffer=buffer)

    def save(
        self,
        filepath: Optional[StrOrPath] = None,
        buffer: Optional[BinaryIO] = None,
        type: Optional[FileTypes] = None,
    ) -> None:
        """Save file data to buffer or file.

        Args:
            filepath (Optional[StrOrPath], optional): if specified, the data is written to the file. Defaults to None.
            buffer (Optional[BinaryIO], optional): if specified, the data is written to the buffer. Defaults to None.
            type (Optional[FileTypes], optional): if specified, changes file type. Defaults to None.
        """

        if type:
            self._type = type
            self._handler = HANDLERS[self._type]
        if buffer:
            self._handler.write(buffer=buffer, data=self.data)
        if filepath:
            with open(filepath, "wb") as file:
                self._handler.write(buffer=file, data=self.data)

    def guess(self, buffer: BinaryIO) -> bool:
        """Guess NBT file type based on header (first 6 bytes). Does not chnage stream position.

        Args:
            buffer (BinaryIO): file buffer

        Returns:
            bool: True if file type was guessed, otherwise False.
        """

        start_pos = buffer.tell()
        magic_number = buffer.read(6)
        buffer.seek(start_pos)

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

    def __repr__(self) -> str:
        return f"NBTFile(type={self.get_file_type()}, handler={self._handler}, data={self.data})"


HANDLERS = {
    FileTypes.JE_UNCOMPRESSED: JE_Uncompressed,
    FileTypes.BE_UNCOMPRESSED: BE_Uncompressed,
    FileTypes.BE_WITH_HEADER: BE_WithHeader,
    FileTypes.JE_GZIP_COMPRESSED: JE_GzipCompressed,
    FileTypes.JE_ZLIB_COMPRESSED: JE_ZlibCompressed,
}
